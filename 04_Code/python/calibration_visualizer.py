#!/usr/bin/env python3
"""
Smart Socks - Real-Time Calibration Visualizer
ELEC-E7840 Smart Wearables (Aalto University)

Nordic Design Edition: Minimalist, professional real-time visualization.
Clean aesthetics with muted colors and functional elegance.

Usage:
    python calibration_visualizer.py --port /dev/cu.usbmodem2101
    python calibration_visualizer.py --port /dev/cu.usbmodem2101 --save-calibration
    
Controls:
    'q' - Quit
    'r' - Reset min/max tracking
    's' - Save current readings to calibration file
    'p' - Pause/Resume display
"""

import argparse
import sys
import time
import serial
import numpy as np
from collections import deque
from datetime import datetime

# Nordic Design System
try:
    from nordic_style import (
        apply_nordic_style, create_sensor_card, create_header, 
        create_status_bar, SENSOR_COLORS, COLORS
    )
    NORDIC_STYLE = True
except ImportError:
    NORDIC_STYLE = False
    print("Note: nordic_style.py not found. Using default style.")

# Matplotlib
try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib.gridspec import GridSpec
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("ERROR: matplotlib required. Install with: pip install matplotlib")
    sys.exit(1)

from config import SENSORS, HARDWARE

# Backwards compatibility with old config structure
SENSOR_NAMES = SENSORS['names']
SAMPLING = {'rate_hz': HARDWARE['sample_rate_hz']}

# Sensor configuration for dual leg setup
LEFT_SENSORS = SENSORS['left_leg']  # ['L_P_Heel', 'L_P_Ball', 'L_S_Knee']
RIGHT_SENSORS = SENSORS['right_leg']  # ['R_P_Heel', 'R_P_Ball', 'R_S_Knee']
NUM_LEFT = len(LEFT_SENSORS)
NUM_RIGHT = len(RIGHT_SENSORS)


class CalibrationVisualizer:
    """Real-time calibration visualization with Nordic design."""
    
    def __init__(self, port, baudrate=115200, history_seconds=5):
        self.port = port
        self.baudrate = baudrate
        self.history_seconds = history_seconds
        self.history_samples = int(history_seconds * SAMPLING['rate_hz'])
        
        # Data buffers
        self.timestamps = deque(maxlen=self.history_samples)
        self.sensor_data = {name: deque(maxlen=self.history_samples) for name in SENSOR_NAMES}
        
        # Calibration tracking
        self.min_values = {name: 4095 for name in SENSOR_NAMES}
        self.max_values = {name: 0 for name in SENSOR_NAMES}
        self.current_values = {name: 0 for name in SENSOR_NAMES}
        
        # State
        self.serial_conn = None
        self.running = True
        self.paused = False
        self.save_calibration = False
        self.sample_count = 0
        
        # Setup plot
        self._setup_plot()
        
    def _setup_plot(self):
        """Initialize matplotlib figure with Nordic design."""
        if NORDIC_STYLE:
            apply_nordic_style()
        else:
            plt.style.use('dark_background')
        
        # Create figure with Nordic proportions
        self.fig = plt.figure(figsize=(18, 10), facecolor=COLORS.get('nord0', '#2E3440'))
        self.fig.canvas.manager.set_window_title('Smart Socks · Calibration')
        
        # Nordic Grid Layout
        # [Header]      [Header]      [Header]
        # [Left Foot]   [Right Foot]  [Stats]
        # [Time Series] [Time Series] [Time Series]
        # [Status Bar]
        
        gs = GridSpec(4, 3, figure=self.fig, 
                      hspace=0.3, wspace=0.25,
                      height_ratios=[0.8, 2, 1.5, 0.3])
        
        # Header spanning all columns
        self.header_ax = self.fig.add_subplot(gs[0, :])
        if NORDIC_STYLE:
            create_header(self.header_ax, 
                         "SMART SOCKS", 
                         "Real-Time Sensor Calibration · ELEC-E7840")
        else:
            self.header_ax.text(0.5, 0.5, 'Smart Socks - Calibration', 
                              ha='center', va='center', fontsize=16)
            self.header_ax.axis('off')
        
        # Left Leg Sensors (3 cards in 1 column)
        self.left_cards = []
        left_gs = gs[1, 0].subgridspec(NUM_LEFT, 1, hspace=0.1)
        for i in range(NUM_LEFT):
            ax = self.fig.add_subplot(left_gs[i, 0])
            sensor_name = LEFT_SENSORS[i]
            color_idx = SENSOR_NAMES.index(sensor_name)
            self.left_cards.append((ax, sensor_name, SENSOR_COLORS[color_idx]))
        
        # Right Leg Sensors (3 cards in 1 column)
        self.right_cards = []
        right_gs = gs[1, 1].subgridspec(NUM_RIGHT, 1, hspace=0.1)
        for i in range(NUM_RIGHT):
            ax = self.fig.add_subplot(right_gs[i, 0])
            sensor_name = RIGHT_SENSORS[i]
            color_idx = SENSOR_NAMES.index(sensor_name)
            self.right_cards.append((ax, sensor_name, SENSOR_COLORS[color_idx]))
        
        # Statistics Panel
        self.stats_ax = self.fig.add_subplot(gs[1, 2])
        self.stats_ax.set_facecolor(COLORS.get('nord1', '#3B4252'))
        self.stats_text = self.stats_ax.text(0.1, 0.95, '', 
                                            transform=self.stats_ax.transAxes,
                                            fontsize=9, verticalalignment='top',
                                            fontfamily='monospace',
                                            color=COLORS.get('nord4', '#D8DEE9'))
        self.stats_ax.axis('off')
        
        # Time Series Plot (bottom row)
        self.ts_ax = self.fig.add_subplot(gs[2, :2])
        self.ts_ax.set_facecolor(COLORS.get('nord1', '#3B4252'))
        self.ts_lines = {}
        for i, name in enumerate(SENSOR_NAMES):
            line, = self.ts_ax.plot([], [], color=SENSOR_COLORS[i], 
                                   linewidth=1.5, label=name, alpha=0.8)
            self.ts_lines[name] = line
        
        self.ts_ax.set_xlim(0, self.history_seconds)
        self.ts_ax.set_ylim(0, 4095)
        self.ts_ax.set_xlabel('Time (s)', color=COLORS.get('nord4', '#D8DEE9'))
        self.ts_ax.set_ylabel('ADC Value', color=COLORS.get('nord4', '#D8DEE9'))
        self.ts_ax.legend(loc='upper right', framealpha=0.9, 
                         facecolor=COLORS.get('nord2', '#434C5E'),
                         edgecolor=COLORS.get('nord3', '#4C566A'))
        
        # Mini heatmap
        self.heatmap_ax = self.fig.add_subplot(gs[2, 2])
        self.heatmap_ax.set_facecolor(COLORS.get('nord1', '#3B4252'))
        num_sensors = len(SENSOR_NAMES)
        self.heatmap_bars = self.heatmap_ax.barh(range(num_sensors), [0]*num_sensors, 
                                                  color=SENSOR_COLORS[:num_sensors],
                                                  edgecolor=COLORS.get('nord3', '#4C566A'),
                                                  linewidth=0.5)
        self.heatmap_ax.set_xlim(0, 4095)
        self.heatmap_ax.set_yticks(range(num_sensors))
        self.heatmap_ax.set_yticklabels([n.replace('_', '\n') for n in SENSOR_NAMES],
                                       fontsize=7)
        self.heatmap_ax.set_xlabel('Current Value', fontsize=8,
                                  color=COLORS.get('nord4', '#D8DEE9'))
        self.heatmap_ax.invert_yaxis()
        
        # Status Bar
        self.status_ax = self.fig.add_subplot(gs[3, :])
        self.status_text = "Initializing..."
        
        # Footer with controls
        controls_text = "[Q]uit  [R]eset  [S]ave  [P]ause"
        self.fig.text(0.5, 0.01, controls_text,
                     ha='center', fontsize=9,
                     color=COLORS.get('nord4', '#D8DEE9'),
                     fontfamily='monospace',
                     bbox=dict(boxstyle='round', facecolor=COLORS.get('nord2', '#434C5E'),
                              edgecolor=COLORS.get('nord3', '#4C566A'), pad=0.5))
        
        # Connect keyboard events
        self.fig.canvas.mpl_connect('key_press_event', self._on_key)
        
    def _on_key(self, event):
        """Handle keyboard events."""
        key = event.key.lower()
        if key == 'q':
            self.running = False
        elif key == 'r':
            self._reset_minmax()
        elif key == 's':
            self.save_calibration = True
        elif key == 'p':
            self.paused = not self.paused
            
    def _reset_minmax(self):
        """Reset min/max tracking."""
        self.min_values = {name: 4095 for name in SENSOR_NAMES}
        self.max_values = {name: 0 for name in SENSOR_NAMES}
        print("\n[RESET] Min/max tracking reset")
        
    def connect(self):
        """Connect to serial port."""
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"Connected to {self.port} at {self.baudrate} baud")
            time.sleep(2)  # Wait for Arduino reset
            
            # Flush any startup messages
            while self.serial_conn.in_waiting:
                self.serial_conn.readline()
                
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from serial port."""
        if self.serial_conn:
            self.serial_conn.close()
            print("Disconnected")
            
    def _parse_line(self, line):
        """Parse a CSV line of sensor data.
        
        Supports multiple formats:
        - Calibration mode (6 sensors): timestamp,val1,val2,val3,val4,val5,val6
        - Single leg mode: timestamp,leg,val1,val2,val3
        - Legacy 10-sensor: timestamp,val1,...,val10
        """
        try:
            line = line.decode('utf-8').strip()
            if not line or line.startswith('Smart') or line.startswith('==='):
                return None
            if 'time_ms' in line or 'L_Heel' in line or 'L_P_Heel' in line:
                return None  # Header line
                
            parts = line.split(',')
            num_sensors = len(SENSOR_NAMES)  # 6 sensors
            
            if len(parts) < 2:
                return None
                
            timestamp = int(parts[0])
            
            # Format 1: Calibration mode - timestamp + 6 values (A0-A5)
            # Example: 12345,100,200,300,400,500,600
            if len(parts) == num_sensors + 1:  # 7 parts = timestamp + 6 sensors
                values = [int(v) for v in parts[1:]]
                return timestamp, dict(zip(SENSOR_NAMES, values))
            
            # Format 2: Single leg format - timestamp,leg,3values
            # Example: 12345,L,100,200,300
            elif len(parts) == 5 and parts[1] in ['L', 'R']:
                values = [int(v) for v in parts[2:5]]
                leg = parts[1]
                if leg == 'L':
                    sensor_dict = dict(zip(LEFT_SENSORS, values))
                    for s in RIGHT_SENSORS:
                        sensor_dict[s] = 0
                else:  # 'R'
                    sensor_dict = dict(zip(RIGHT_SENSORS, values))
                    for s in LEFT_SENSORS:
                        sensor_dict[s] = 0
                return timestamp, sensor_dict
            
            # Format 3: Legacy 10-sensor format (for backwards compatibility)
            # Example: 12345,100,200,300,400,500,600,700,800,900,1000
            elif len(parts) == 11:
                # Only use first 6 values, map to new sensor names
                values = [int(v) for v in parts[1:7]]
                return timestamp, dict(zip(SENSOR_NAMES, values))
                
        except Exception as e:
            pass
        return None
        
    def _read_data(self):
        """Read data from serial port."""
        if not self.serial_conn or not self.serial_conn.in_waiting:
            return None
            
        try:
            line = self.serial_conn.readline()
            return self._parse_line(line)
        except:
            return None
            
    def _update_data(self):
        """Read and process new data."""
        # Read all available lines
        for _ in range(10):  # Process up to 10 lines per update
            data = self._read_data()
            if data is None:
                break
                
            timestamp, values = data
            
            if not self.paused:
                # Update buffers
                self.timestamps.append(timestamp)
                for name, value in values.items():
                    self.sensor_data[name].append(value)
                    self.current_values[name] = value
                    
                    # Update min/max
                    self.min_values[name] = min(self.min_values[name], value)
                    self.max_values[name] = max(self.max_values[name], value)
                    
                self.sample_count += 1
                    
        # Check if we should save calibration
        if self.save_calibration:
            self._save_calibration()
            self.save_calibration = False
            
    def _save_calibration(self):
        """Save current calibration values to file."""
        filename = f"calibration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = f"../../03_Data/calibration/{filename}"
        
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            f.write("Sensor,Current,Min,Max,Range\n")
            for name in SENSOR_NAMES:
                curr = self.current_values[name]
                min_v = self.min_values[name]
                max_v = self.max_values[name]
                range_v = max_v - min_v if max_v > min_v else 0
                f.write(f"{name},{curr},{min_v},{max_v},{range_v}\n")
                
        print(f"\n[SAVED] Calibration saved to {filepath}")
        
    def _update_plot(self, frame):
        """Update the matplotlib plot (called by animation)."""
        self._update_data()
        
        # Update sensor cards (left foot)
        for ax, name, color in self.left_cards:
            if NORDIC_STYLE:
                ax.clear()
                create_sensor_card(ax, name, 
                                 self.current_values[name],
                                 self.min_values[name],
                                 self.max_values[name],
                                 color)
            else:
                ax.clear()
                ax.text(0.5, 0.5, f"{name}\n{self.current_values[name]}",
                       ha='center', va='center')
                ax.axis('off')
                    
        # Update sensor cards (right foot)
        for ax, name, color in self.right_cards:
            if NORDIC_STYLE:
                ax.clear()
                create_sensor_card(ax, name,
                                 self.current_values[name],
                                 self.min_values[name],
                                 self.max_values[name],
                                 color)
            else:
                ax.clear()
                ax.text(0.5, 0.5, f"{name}\n{self.current_values[name]}",
                       ha='center', va='center')
                ax.axis('off')
        
        # Update statistics
        stats_lines = []
        stats_lines.append("SENSOR          CURR   MIN    MAX    RANGE")
        stats_lines.append("─" * 45)
        for name in SENSOR_NAMES:
            curr = self.current_values[name]
            min_v = self.min_values[name]
            max_v = self.max_values[name]
            range_v = max_v - min_v if max_v > min_v else 0
            stats_lines.append(f"{name:<14} {curr:>5} {min_v:>5} {max_v:>5} {range_v:>5}")
        
        stats_lines.append("")
        status = "PAUSED" if self.paused else "ACTIVE"
        stats_lines.append(f"Status: {status}  |  Samples: {self.sample_count}")
        
        self.stats_text.set_text('\n'.join(stats_lines))
        
        # Update time series
        if len(self.timestamps) > 1:
            times = np.array(self.timestamps) / 1000.0
            times = times - times[0]
            
            for name in SENSOR_NAMES:
                if len(self.sensor_data[name]) > 0:
                    self.ts_lines[name].set_data(times, list(self.sensor_data[name]))
            
            self.ts_ax.set_xlim(max(0, times[-1] - self.history_seconds),
                               max(self.history_seconds, times[-1]))
                    
        # Update heatmap
        for i, (bar, name) in enumerate(zip(self.heatmap_bars, SENSOR_NAMES)):
            bar.set_width(self.current_values[name])
        
        # Update status bar
        if NORDIC_STYLE:
            self.status_ax.clear()
            status = f"PORT: {self.port}  |  SAMPLES: {self.sample_count}  |  {'PAUSED' if self.paused else 'RUNNING'}"
            create_status_bar(self.status_ax, status, is_recording=not self.paused)
        
        return []
        
    def run(self):
        """Main run loop."""
        if not self.connect():
            return
            
        print("\n" + "="*60)
        print("Smart Socks · Nordic Edition")
        print("="*60)
        print(f"Port: {self.port}")
        print(f"Sensors: {len(SENSOR_NAMES)}")
        print(f"History: {self.history_seconds}s")
        print("\nControls: Q=Quit  R=Reset  S=Save  P=Pause")
        print("="*60 + "\n")
        
        # Start animation
        self.ani = animation.FuncAnimation(
            self.fig, 
            self._update_plot,
            interval=50,  # 50ms update rate (20 FPS)
            blit=False,
            cache_frame_data=False
        )
        
        try:
            plt.show()
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            self.disconnect()
            

def main():
    parser = argparse.ArgumentParser(
        description='Smart Socks Calibration Visualizer · Nordic Edition',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Nordic Design Principles:
  · Clean, functional aesthetics
  · Muted, harmonious colors
  · Clear information hierarchy
  
Examples:
    python calibration_visualizer.py --port /dev/cu.usbmodem2101
    python calibration_visualizer.py --port COM3 --history 10
        """
    )
    
    parser.add_argument('--port', '-p', required=True,
                        help='Serial port (e.g., /dev/cu.usbmodem2101, COM3)')
    parser.add_argument('--baud', '-b', type=int, default=115200,
                        help='Baud rate (default: 115200)')
    parser.add_argument('--history', type=int, default=5,
                        help='History window in seconds (default: 5)')
    
    args = parser.parse_args()
    
    visualizer = CalibrationVisualizer(
        port=args.port,
        baudrate=args.baud,
        history_seconds=args.history
    )
    
    visualizer.run()


if __name__ == '__main__':
    main()
