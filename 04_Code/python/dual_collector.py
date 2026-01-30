#!/usr/bin/env python3
"""
Smart Socks - Dual Leg Data Collector
ELEC-E7840 Smart Wearables (Aalto University)

Collects and merges data from two ESP32s (one per leg) for synchronized
data collection with the 6-sensor configuration.

Hardware: 2x ESP32S3 XIAO, 6 sensors total (3 per leg)
Sensors: 2 pressure (heel + ball) + 1 stretch (knee) per leg

Usage:
    # Collect from both legs simultaneously
    python dual_collector.py --left-port /dev/cu.usbmodem2101 --right-port /dev/cu.usbmodem2102 --activity walking

    # Collect with auto port detection
    python dual_collector.py --activity stairs_up

    # Merge existing CSV files
    python dual_collector.py --merge --left left_data.csv --right right_data.csv --output merged.csv

    # Calibration mode (real-time visualization)
    python dual_collector.py --calibrate --left-port /dev/cu.usbmodem2101 --right-port /dev/cu.usbmodem2102
"""

import argparse
import sys
import time
import json
import csv
import threading
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import Optional, Dict, List, Tuple
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("Warning: pyserial not installed. Serial collection unavailable.")

try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib.patches import Rectangle
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not installed. Visualization unavailable.")

from config import SENSORS, ACTIVITIES, HARDWARE, PATHS


class LegDataCollector:
    """Collects data from a single ESP32 (one leg)."""
    
    def __init__(self, port: str, leg_id: str, baudrate: int = 115200):
        """
        Initialize leg data collector.
        
        Args:
            port: Serial port for ESP32
            leg_id: 'L' for left, 'R' for right
            baudrate: Serial baudrate (default 115200)
        """
        self.port = port
        self.leg_id = leg_id
        self.baudrate = baudrate
        self.serial: Optional[serial.Serial] = None
        self.connected = False
        self.data_buffer = deque(maxlen=1000)
        self.is_recording = False
        self.samples_collected = 0
        self.recording_start_time: Optional[float] = None
        self.thread: Optional[threading.Thread] = None
        self.stop_flag = threading.Event()
        
        # Sensor names for this leg
        if leg_id == 'L':
            self.sensor_names = ["L_P_Heel", "L_P_Ball", "L_S_Knee"]
        else:
            self.sensor_names = ["R_P_Heel", "R_P_Ball", "R_S_Knee"]
    
    def connect(self) -> bool:
        """Connect to ESP32 serial port."""
        if not SERIAL_AVAILABLE:
            print(f"Error: pyserial not available for {self.leg_id} leg")
            return False
        
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1,
                write_timeout=1
            )
            time.sleep(2)  # Wait for ESP32 to reset
            self.connected = True
            print(f"✓ Connected to {self.leg_id} leg on {self.port}")
            return True
        except Exception as e:
            print(f"✗ Failed to connect {self.leg_id} leg: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from serial port."""
        self.stop_flag.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        if self.serial:
            self.serial.close()
        self.connected = False
        print(f"Disconnected {self.leg_id} leg")
    
    def start_recording(self):
        """Start recording data."""
        if not self.connected:
            print(f"Error: {self.leg_id} leg not connected")
            return
        
        # Send START command
        self.serial.write(b"START\n")
        self.is_recording = True
        self.recording_start_time = time.time()
        self.samples_collected = 0
        print(f"Started recording {self.leg_id} leg")
    
    def stop_recording(self) -> List[Dict]:
        """Stop recording and return collected data."""
        if not self.connected:
            return []
        
        self.serial.write(b"STOP\n")
        self.is_recording = False
        
        # Return copy of data buffer
        data = list(self.data_buffer)
        print(f"Stopped recording {self.leg_id} leg ({len(data)} samples)")
        return data
    
    def read_sample(self) -> Optional[Dict]:
        """Read a single sample from serial."""
        if not self.connected or not self.serial:
            return None
        
        try:
            line = self.serial.readline().decode('utf-8').strip()
            if not line or line.startswith('#'):
                return None
            
            # Parse CSV: time_ms,leg,sensor1,sensor2,sensor3
            parts = line.split(',')
            if len(parts) != 5:
                return None
            
            return {
                'time_ms': int(parts[0]),
                'leg': parts[1],
                'sensors': {
                    self.sensor_names[0]: int(parts[2]),
                    self.sensor_names[1]: int(parts[3]),
                    self.sensor_names[2]: int(parts[4])
                }
            }
        except Exception as e:
            return None
    
    def collection_loop(self):
        """Background thread for continuous data collection."""
        while not self.stop_flag.is_set():
            sample = self.read_sample()
            if sample:
                self.data_buffer.append(sample)
                if self.is_recording:
                    self.samples_collected += 1
            time.sleep(0.001)  # Small delay to prevent CPU spinning
    
    def start_collection_thread(self):
        """Start background collection thread."""
        self.stop_flag.clear()
        self.thread = threading.Thread(target=self.collection_loop, daemon=True)
        self.thread.start()
    
    def get_latest_values(self) -> Dict[str, int]:
        """Get most recent sensor values."""
        if self.data_buffer:
            return self.data_buffer[-1]['sensors']
        return {name: 0 for name in self.sensor_names}


class DualDataCollector:
    """Manages data collection from both legs simultaneously."""
    
    def __init__(self, left_port: Optional[str] = None, right_port: Optional[str] = None):
        self.left = LegDataCollector(left_port or self._find_port("left"), 'L')
        self.right = LegDataCollector(right_port or self._find_port("right"), 'R')
        self.merged_data: List[Dict] = []
        self.is_recording = False
    
    def _find_port(self, leg: str) -> str:
        """Auto-detect serial port for given leg."""
        if not SERIAL_AVAILABLE:
            return "/dev/ttyUSB0"
        
        ports = list(serial.tools.list_ports.comports())
        
        # Common patterns for XIAO ESP32S3
        patterns = {
            'left': ['/dev/cu.usbmodem2101', '/dev/ttyUSB0', 'COM3'],
            'right': ['/dev/cu.usbmodem2102', '/dev/ttyUSB1', 'COM4']
        }
        
        for pattern in patterns.get(leg, []):
            for port in ports:
                if pattern in port.device:
                    return port.device
        
        # Return first available port as fallback
        if ports:
            return ports[0].device
        
        return "/dev/ttyUSB0"
    
    def connect(self) -> bool:
        """Connect to both legs."""
        left_ok = self.left.connect()
        right_ok = self.right.connect()
        
        if left_ok and right_ok:
            self.left.start_collection_thread()
            self.right.start_collection_thread()
            return True
        
        # Cleanup if either failed
        if left_ok:
            self.left.disconnect()
        if right_ok:
            self.right.disconnect()
        return False
    
    def disconnect(self):
        """Disconnect from both legs."""
        self.left.disconnect()
        self.right.disconnect()
    
    def start_synchronized_recording(self, delay_ms: int = 100):
        """Start synchronized recording on both legs."""
        # Send TRIGGER to both
        if self.left.connected:
            self.left.serial.write(b"TRIGGER\n")
        if self.right.connected:
            self.right.serial.write(b"TRIGGER\n")
        
        time.sleep(delay_ms / 1000.0)
        
        self.left.start_recording()
        self.right.start_recording()
        self.is_recording = True
        self.recording_start_time = time.time()
        print(f"Started synchronized recording with {delay_ms}ms delay")
    
    def stop_recording(self) -> Tuple[List[Dict], List[Dict]]:
        """Stop recording and return data from both legs."""
        left_data = self.left.stop_recording()
        right_data = self.right.stop_recording()
        self.is_recording = False
        return left_data, right_data
    
    def merge_data(self, left_data: List[Dict], right_data: List[Dict]) -> List[Dict]:
        """Merge left and right leg data by timestamp."""
        # Create time-indexed dictionaries
        left_by_time = {d['time_ms']: d for d in left_data}
        right_by_time = {d['time_ms']: d for d in right_data}
        
        # Get all timestamps
        all_times = sorted(set(left_by_time.keys()) | set(right_by_time.keys()))
        
        merged = []
        for t in all_times:
            row = {'time_ms': t}
            
            # Add left leg data
            if t in left_by_time:
                row.update(left_by_time[t]['sensors'])
            else:
                # Interpolate or use zeros
                row.update({name: 0 for name in self.left.sensor_names})
            
            # Add right leg data
            if t in right_by_time:
                row.update(right_by_time[t]['sensors'])
            else:
                row.update({name: 0 for name in self.right.sensor_names})
            
            merged.append(row)
        
        return merged
    
    def save_merged_data(self, data: List[Dict], activity: str, subject: str = "unknown"):
        """Save merged data to CSV file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{activity}_{subject}_{timestamp}_dual.csv"
        output_path = Path(PATHS['data_raw']) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not data:
            print("Warning: No data to save")
            return
        
        # Get fieldnames from first row
        fieldnames = list(data[0].keys())
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"Saved merged data to: {output_path}")
        print(f"Total samples: {len(data)}")
        return output_path


def run_calibration_visualization(collector: DualDataCollector):
    """Run real-time calibration visualization."""
    if not MATPLOTLIB_AVAILABLE:
        print("Error: matplotlib required for visualization")
        return
    
    plt.style.use('dark_background')
    
    # Nordic color palette
    colors = {
        'L_P_Heel': '#81A1C1', 'L_P_Ball': '#88C0D0', 'L_S_Knee': '#A3BE8C',
        'R_P_Heel': '#81A1C1', 'R_P_Ball': '#88C0D0', 'R_S_Knee': '#A3BE8C'
    }
    
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    fig.patch.set_facecolor('#2E3440')
    fig.suptitle('Smart Socks - Dual Leg Calibration', color='#ECEFF4', fontsize=14)
    
    # Configure axes
    sensor_names = ["L_P_Heel", "L_P_Ball", "L_S_Knee", "R_P_Heel", "R_P_Ball", "R_S_Knee"]
    positions = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
    
    lines = []
    texts = []
    data_buffers = {name: deque(maxlen=100) for name in sensor_names}
    
    for name, (row, col) in zip(sensor_names, positions):
        ax = axes[row, col]
        ax.set_facecolor('#3B4252')
        ax.set_title(name, color='#ECEFF4', fontsize=10)
        ax.set_ylim(0, 4095)
        ax.set_xlim(0, 100)
        ax.tick_params(colors='#D8DEE9')
        ax.grid(True, alpha=0.2)
        
        line, = ax.plot([], [], color=colors[name], linewidth=1.5)
        lines.append(line)
        
        text = ax.text(0.98, 0.95, '0', transform=ax.transAxes,
                      ha='right', va='top', color='#ECEFF4',
                      fontsize=12, fontweight='bold')
        texts.append(text)
    
    def init():
        for line in lines:
            line.set_data([], [])
        return lines + texts
    
    def update(frame):
        # Get latest values from both legs
        left_values = collector.left.get_latest_values()
        right_values = collector.right.get_latest_values()
        
        all_values = {**left_values, **right_values}
        
        for i, name in enumerate(sensor_names):
            value = all_values.get(name, 0)
            data_buffers[name].append(value)
            
            # Update line
            ydata = list(data_buffers[name])
            xdata = list(range(len(ydata)))
            lines[i].set_data(xdata, ydata)
            
            # Update text
            texts[i].set_text(str(value))
            
            # Color code based on value
            if value > 3000:
                texts[i].set_color('#A3BE8C')  # Green for high
            elif value > 1000:
                texts[i].set_color('#EBCB8B')  # Yellow for medium
            else:
                texts[i].set_color('#D8DEE9')  # Default
        
        return lines + texts
    
    ani = animation.FuncAnimation(fig, update, init_func=init, interval=50, blit=True)
    
    # Add control buttons
    ax_record = fig.add_axes([0.35, 0.02, 0.1, 0.05])
    ax_stop = fig.add_axes([0.55, 0.02, 0.1, 0.05])
    
    btn_record = plt.Button(ax_record, 'Record', color='#5E81AC', hovercolor='#81A1C1')
    btn_stop = plt.Button(ax_stop, 'Stop', color='#BF616A', hovercolor='#C5727A')
    
    def on_record(event):
        collector.start_synchronized_recording()
    
    def on_stop(event):
        left_data, right_data = collector.stop_recording()
        merged = collector.merge_data(left_data, right_data)
        print(f"Collected {len(merged)} merged samples")
    
    btn_record.on_clicked(on_record)
    btn_stop.on_clicked(on_stop)
    
    plt.tight_layout(rect=[0, 0.1, 1, 0.95])
    plt.show()


def merge_csv_files(left_path: str, right_path: str, output_path: str):
    """Merge two existing CSV files."""
    left_data = []
    right_data = []
    
    # Read left leg data
    with open(left_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            left_data.append({
                'time_ms': int(row['time_ms']),
                'leg': row['leg'],
                'sensors': {
                    'L_P_Heel': int(row.get('L_P_Heel', 0)),
                    'L_P_Ball': int(row.get('L_P_Ball', 0)),
                    'L_S_Knee': int(row.get('L_S_Knee', 0))
                }
            })
    
    # Read right leg data
    with open(right_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            right_data.append({
                'time_ms': int(row['time_ms']),
                'leg': row['leg'],
                'sensors': {
                    'R_P_Heel': int(row.get('R_P_Heel', 0)),
                    'R_P_Ball': int(row.get('R_P_Ball', 0)),
                    'R_S_Knee': int(row.get('R_S_Knee', 0))
                }
            })
    
    # Create collector instance for merging
    collector = DualDataCollector()
    merged = collector.merge_data(left_data, right_data)
    
    # Save merged data
    with open(output_path, 'w', newline='') as f:
        fieldnames = ['time_ms'] + SENSORS['names']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(merged)
    
    print(f"Merged {len(left_data)} + {len(right_data)} = {len(merged)} samples")
    print(f"Saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Smart Socks Dual Leg Data Collector',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Calibrate both legs
  python dual_collector.py --calibrate --left-port /dev/cu.usbmodem2101 --right-port /dev/cu.usbmodem2102
  
  # Record activity
  python dual_collector.py --activity walking --duration 30
  
  # Merge existing files
  python dual_collector.py --merge --left left.csv --right right.csv --output merged.csv
        """
    )
    
    parser.add_argument('--left-port', help='Serial port for left leg ESP32')
    parser.add_argument('--right-port', help='Serial port for right leg ESP32')
    parser.add_argument('--baudrate', type=int, default=115200, help='Serial baudrate')
    
    parser.add_argument('--calibrate', action='store_true', help='Run calibration visualization')
    parser.add_argument('--activity', choices=list(ACTIVITIES['names'].keys()), 
                       help='Activity to record')
    parser.add_argument('--subject', default='unknown', help='Subject identifier')
    parser.add_argument('--duration', type=int, help='Recording duration in seconds')
    
    parser.add_argument('--merge', action='store_true', help='Merge existing CSV files')
    parser.add_argument('--left', help='Left leg CSV file (for merge)')
    parser.add_argument('--right', help='Right leg CSV file (for merge)')
    parser.add_argument('--output', help='Output file (for merge)')
    
    parser.add_argument('--list-ports', action='store_true', help='List available serial ports')
    
    args = parser.parse_args()
    
    # List ports
    if args.list_ports:
        if SERIAL_AVAILABLE:
            print("Available serial ports:")
            for port in serial.tools.list_ports.comports():
                print(f"  {port.device}: {port.description}")
        else:
            print("pyserial not installed")
        return
    
    # Merge mode
    if args.merge:
        if not args.left or not args.right:
            print("Error: --left and --right required for merge")
            return
        output = args.output or "merged_data.csv"
        merge_csv_files(args.left, args.right, output)
        return
    
    # Calibration mode
    if args.calibrate:
        print("Starting dual leg calibration...")
        collector = DualDataCollector(args.left_port, args.right_port)
        
        if not collector.connect():
            print("Failed to connect to both legs")
            return
        
        try:
            run_calibration_visualization(collector)
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            collector.disconnect()
        return
    
    # Recording mode
    if args.activity:
        print(f"Recording activity: {args.activity}")
        collector = DualDataCollector(args.left_port, args.right_port)
        
        if not collector.connect():
            print("Failed to connect to both legs")
            return
        
        try:
            print("Starting in 3 seconds...")
            time.sleep(3)
            
            collector.start_synchronized_recording()
            
            if args.duration:
                print(f"Recording for {args.duration} seconds...")
                time.sleep(args.duration)
            else:
                print("Recording... Press Ctrl+C to stop")
                while True:
                    time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            left_data, right_data = collector.stop_recording()
            merged = collector.merge_data(left_data, right_data)
            collector.save_merged_data(merged, args.activity, args.subject)
            collector.disconnect()
        return
    
    # No action specified
    parser.print_help()


if __name__ == '__main__':
    main()
