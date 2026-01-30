#!/usr/bin/env python3
"""
Smart Socks - Data Collector
ELEC-E7840 Smart Wearables (Aalto University)

Collects data from a single ESP32 reading all 6 sensors.

Hardware: 1x ESP32S3 XIAO, 6 sensors (A0-A5)
Sensors: 2 pressure (heel + ball) + 1 stretch (knee) per leg

Usage:
    # Collect data for an activity
    python collector.py --activity walking --port /dev/cu.usbmodem2101

    # Collect with auto port detection
    python collector.py --activity stairs_up

    # Calibration mode (real-time visualization)
    python collector.py --calibrate --port /dev/cu.usbmodem2101
"""

import argparse
import sys
import time
import csv
import threading
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import Optional, Dict, List

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
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not installed. Visualization unavailable.")

from config import SENSORS, ACTIVITIES, HARDWARE, PATHS


class DataCollector:
    """Collects data from a single ESP32 with all 6 sensors."""

    def __init__(self, port: Optional[str] = None, baudrate: int = 115200):
        self.port = port or self._find_port()
        self.baudrate = baudrate
        self.serial: Optional[serial.Serial] = None
        self.connected = False
        self.data_buffer: deque = deque(maxlen=10000)
        self.is_recording = False
        self.samples_collected = 0
        self.recording_start_time: Optional[float] = None
        self.thread: Optional[threading.Thread] = None
        self.stop_flag = threading.Event()
        self.sensor_names = SENSORS['names']

    def _find_port(self) -> str:
        """Auto-detect serial port."""
        if not SERIAL_AVAILABLE:
            return "/dev/ttyUSB0"

        ports = list(serial.tools.list_ports.comports())

        # Common patterns for XIAO ESP32S3
        patterns = ['/dev/cu.usbmodem2101', '/dev/ttyUSB0', 'COM3']

        for pattern in patterns:
            for port in ports:
                if pattern in port.device:
                    return port.device

        if ports:
            return ports[0].device

        return "/dev/ttyUSB0"

    def connect(self) -> bool:
        """Connect to ESP32 serial port."""
        if not SERIAL_AVAILABLE:
            print("Error: pyserial not available")
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
            print(f"Connected to {self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False

    def disconnect(self):
        """Disconnect from serial port."""
        self.stop_flag.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        if self.serial:
            self.serial.close()
        self.connected = False
        print("Disconnected")

    def start_recording(self):
        """Start recording data."""
        if not self.connected:
            print("Error: not connected")
            return

        self.serial.write(b"START\n")
        self.is_recording = True
        self.recording_start_time = time.time()
        self.samples_collected = 0
        self.data_buffer.clear()
        print("Recording started")

    def stop_recording(self) -> List[Dict]:
        """Stop recording and return collected data."""
        if not self.connected:
            return []

        self.serial.write(b"STOP\n")
        self.is_recording = False

        data = list(self.data_buffer)
        print(f"Recording stopped ({len(data)} samples)")
        return data

    def read_sample(self) -> Optional[Dict]:
        """Read a single sample from serial.

        Expected CSV format: time_ms,L_P_Heel,L_P_Ball,L_S_Knee,R_P_Heel,R_P_Ball,R_S_Knee
        """
        if not self.connected or not self.serial:
            return None

        try:
            line = self.serial.readline().decode('utf-8').strip()
            if not line or line.startswith('#'):
                return None

            parts = line.split(',')
            if len(parts) != 7:  # time_ms + 6 sensors
                return None

            return {
                'time_ms': int(parts[0]),
                'L_P_Heel': int(parts[1]),
                'L_P_Ball': int(parts[2]),
                'L_S_Knee': int(parts[3]),
                'R_P_Heel': int(parts[4]),
                'R_P_Ball': int(parts[5]),
                'R_S_Knee': int(parts[6]),
            }
        except Exception:
            return None

    def collection_loop(self):
        """Background thread for continuous data collection."""
        while not self.stop_flag.is_set():
            sample = self.read_sample()
            if sample:
                self.data_buffer.append(sample)
                if self.is_recording:
                    self.samples_collected += 1
            time.sleep(0.001)

    def start_collection_thread(self):
        """Start background collection thread."""
        self.stop_flag.clear()
        self.thread = threading.Thread(target=self.collection_loop, daemon=True)
        self.thread.start()

    def get_latest_values(self) -> Dict[str, int]:
        """Get most recent sensor values."""
        if self.data_buffer:
            latest = self.data_buffer[-1]
            return {name: latest.get(name, 0) for name in self.sensor_names}
        return {name: 0 for name in self.sensor_names}

    def save_data(self, data: List[Dict], activity: str, subject: str = "unknown"):
        """Save collected data to CSV file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{subject}_{activity}_{timestamp}.csv"
        output_path = Path(PATHS['data_raw']) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not data:
            print("Warning: No data to save")
            return None

        fieldnames = ['time_ms'] + self.sensor_names

        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        print(f"Saved data to: {output_path}")
        print(f"Total samples: {len(data)}")
        return output_path


def run_calibration_visualization(collector: DataCollector):
    """Run real-time calibration visualization."""
    if not MATPLOTLIB_AVAILABLE:
        print("Error: matplotlib required for visualization")
        return

    plt.style.use('dark_background')

    colors = {
        'L_P_Heel': '#81A1C1', 'L_P_Ball': '#88C0D0', 'L_S_Knee': '#A3BE8C',
        'R_P_Heel': '#81A1C1', 'R_P_Ball': '#88C0D0', 'R_S_Knee': '#A3BE8C'
    }

    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    fig.patch.set_facecolor('#2E3440')
    fig.suptitle('Smart Socks - Sensor Calibration', color='#ECEFF4', fontsize=14)

    sensor_names = SENSORS['names']
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
        values = collector.get_latest_values()

        for i, name in enumerate(sensor_names):
            value = values.get(name, 0)
            data_buffers[name].append(value)

            ydata = list(data_buffers[name])
            xdata = list(range(len(ydata)))
            lines[i].set_data(xdata, ydata)

            texts[i].set_text(str(value))

            if value > 3000:
                texts[i].set_color('#A3BE8C')
            elif value > 1000:
                texts[i].set_color('#EBCB8B')
            else:
                texts[i].set_color('#D8DEE9')

        return lines + texts

    ani = animation.FuncAnimation(fig, update, init_func=init, interval=50, blit=True)

    ax_record = fig.add_axes([0.35, 0.02, 0.1, 0.05])
    ax_stop = fig.add_axes([0.55, 0.02, 0.1, 0.05])

    btn_record = plt.Button(ax_record, 'Record', color='#5E81AC', hovercolor='#81A1C1')
    btn_stop = plt.Button(ax_stop, 'Stop', color='#BF616A', hovercolor='#C5727A')

    def on_record(event):
        collector.start_recording()

    def on_stop(event):
        data = collector.stop_recording()
        print(f"Collected {len(data)} samples")

    btn_record.on_clicked(on_record)
    btn_stop.on_clicked(on_stop)

    plt.tight_layout(rect=[0, 0.1, 1, 0.95])
    plt.show()


def main():
    parser = argparse.ArgumentParser(
        description='Smart Socks Data Collector',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Calibrate sensors
  python collector.py --calibrate --port /dev/cu.usbmodem2101

  # Record activity
  python collector.py --activity walking_forward --duration 30

  # List available serial ports
  python collector.py --list-ports
        """
    )

    parser.add_argument('--port', help='Serial port for ESP32')
    parser.add_argument('--baudrate', type=int, default=115200, help='Serial baudrate')

    parser.add_argument('--calibrate', action='store_true', help='Run calibration visualization')
    parser.add_argument('--activity', help='Activity to record')
    parser.add_argument('--subject', default='unknown', help='Subject identifier')
    parser.add_argument('--duration', type=int, help='Recording duration in seconds')

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

    # Calibration mode
    if args.calibrate:
        print("Starting sensor calibration...")
        collector = DataCollector(args.port)

        if not collector.connect():
            print("Failed to connect")
            return

        collector.start_collection_thread()

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
        collector = DataCollector(args.port)

        if not collector.connect():
            print("Failed to connect")
            return

        collector.start_collection_thread()

        try:
            print("Starting in 3 seconds...")
            time.sleep(3)

            collector.start_recording()

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
            data = collector.stop_recording()
            collector.save_data(data, args.activity, args.subject)
            collector.disconnect()
        return

    # No action specified
    parser.print_help()


if __name__ == '__main__':
    main()
