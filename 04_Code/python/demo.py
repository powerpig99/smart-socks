#!/usr/bin/env python3
"""
Smart Socks - Interactive Demo
ELEC-E7840 Smart Wearables (Aalto University)

Interactive demonstration of the Smart Socks system.
Supports both live data and recorded data playback.

Usage:
    # Live demo with hardware
    python demo.py --port /dev/ttyUSB0 --model ../../05_Analysis/smart_socks_model.joblib
    
    # Playback recorded data
    python demo.py --playback ../../03_Data/raw/S01_walking_forward_*.csv --model ../../05_Analysis/smart_socks_model.joblib
    
    # Visualize only
    python demo.py --playback ../../03_Data/raw/S01_walking_forward_*.csv --visualize-only
"""

import argparse
import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path
from collections import deque
from datetime import datetime

# Try to import matplotlib for visualization
try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib.patches import Circle, Rectangle
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from config import SENSORS, HARDWARE, REALTIME, WINDOWING

# Backwards compatibility
SENSOR_NAMES = SENSORS['names']
from logging_utils import setup_logging, get_logger
from data_validation import validate_sensor_data
from feature_utils import extract_all_features, features_to_array

setup_logging()
logger = get_logger(__name__)


class LivePlotter:
    """Real-time matplotlib visualization."""
    
    def __init__(self, n_sensors=6, history_length=200):
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib required for visualization")
        
        self.n_sensors = n_sensors
        self.history_length = history_length
        
        # Data buffers
        self.timestamps = deque(maxlen=history_length)
        self.data = {sensor: deque(maxlen=history_length) for sensor in SENSORS['names']}
        
        # Setup figure
        ncols = 2
        nrows = (n_sensors + ncols - 1) // ncols
        self.fig, self.axes = plt.subplots(nrows, ncols, figsize=(12, nrows * 2.8))
        self.axes = self.axes.flatten()
        
        # Setup subplots
        self.lines = {}
        colors = plt.cm.tab10(np.linspace(0, 1, n_sensors))
        
        for idx, (ax, sensor) in enumerate(zip(self.axes, SENSORS['names'])):
            self.lines[sensor], = ax.plot([], [], color=colors[idx], linewidth=1)
            ax.set_ylim(0, HARDWARE['adc_max_value'])
            ax.set_ylabel('ADC Value')
            ax.set_title(sensor)
            ax.grid(True, alpha=0.3)
            
            if idx >= n_sensors - 2:  # Bottom row
                ax.set_xlabel('Sample')
        
        self.fig.suptitle('Smart Socks - Real-Time Sensor Data', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        # Status text
        self.status_text = self.fig.text(0.5, 0.02, 'Waiting for data...', 
                                         ha='center', fontsize=10,
                                         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
    def update(self, frame):
        """Update plot for animation."""
        if len(self.timestamps) == 0:
            return list(self.lines.values())
        
        x = np.arange(len(self.timestamps))
        
        for sensor in SENSORS['names']:
            if len(self.data[sensor]) > 0:
                self.lines[sensor].set_data(x, list(self.data[sensor]))
                self.axes[SENSORS['names'].index(sensor)].set_xlim(0, len(x))
        
        return list(self.lines.values())
    
    def add_data(self, timestamp, sensor_values):
        """Add new data point."""
        self.timestamps.append(timestamp)
        for sensor, value in sensor_values.items():
            self.data[sensor].append(value)
    
    def update_status(self, text):
        """Update status text."""
        self.status_text.set_text(text)
    
    def show(self):
        """Show the plot."""
        self.ani = animation.FuncAnimation(
            self.fig, self.update, interval=50, blit=False, cache_frame_data=False
        )
        plt.show()


class TextModeDemo:
    """Text-only demo mode (no matplotlib)."""
    
    def __init__(self):
        self.last_update = time.time()
        self.sample_count = 0
        
    def update(self, timestamp, sensor_values, activity="Unknown", confidence=0, steps=0):
        """Update text display."""
        self.sample_count += 1
        
        # Update every 0.5 seconds
        if time.time() - self.last_update < 0.5:
            return
        
        self.last_update = time.time()
        
        # Clear screen (ANSI escape code)
        print('\033[2J\033[H', end='')
        
        # Header
        print("="*70)
        print(" SMART SOCKS - REAL-TIME DEMO ".center(70, "="))
        print("="*70)
        print(f"Time: {datetime.now().strftime('%H:%M:%S')} | Samples: {self.sample_count}")
        print("-"*70)
        
        # Activity status
        print(f"\n  Activity: {activity:20s} | Confidence: {confidence:.2f}")
        print(f"  Steps: {steps}")
        
        # Sensor values
        print("\n  Sensor Readings:")
        print("  " + "-"*66)
        
        for i in range(0, len(SENSORS['names']), 2):
            left_sensor = SENSORS['names'][i]
            right_sensor = SENSORS['names'][i+1] if i+1 < len(SENSORS['names']) else None
            
            left_val = sensor_values.get(left_sensor, 0)
            left_bar = "█" * int(left_val / 200)
            
            if right_sensor:
                right_val = sensor_values.get(right_sensor, 0)
                right_bar = "█" * int(right_val / 200)
                print(f"  {left_sensor:10s}: {left_val:4d} {left_bar:20s} | "
                      f"{right_sensor:10s}: {right_val:4d} {right_bar:20s}")
            else:
                print(f"  {left_sensor:10s}: {left_val:4d} {left_bar:20s}")
        
        print("\n  " + "-"*66)
        print("  Press Ctrl+C to stop")
        print("="*70)


class SmartSocksDemo:
    """Main demo class."""
    
    def __init__(self, model_path=None, port=None, playback_file=None, visualize=True):
        self.model_path = model_path
        self.port = port
        self.playback_file = playback_file
        self.visualize = visualize and MATPLOTLIB_AVAILABLE
        
        # Load model if provided
        self.model = None
        self.scaler = None
        if model_path:
            self._load_model()
        
        # Setup visualization
        self.plotter = None
        self.text_demo = None
        
        if self.visualize:
            try:
                self.plotter = LivePlotter()
            except Exception as e:
                logger.warning(f"Could not create plotter: {e}")
                self.visualize = False
        
        if not self.visualize:
            self.text_demo = TextModeDemo()
        
        # Classification state
        self.buffer = deque(maxlen=WINDOWING['samples_per_window'])
        self.current_activity = "Unknown"
        self.confidence = 0.0
        self.step_count = 0
        
    def _load_model(self):
        """Load ML model."""
        try:
            import joblib
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.model_path.replace('.joblib', '_scaler.joblib'))
            logger.info(f"Loaded model from {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None
    
    def _classify(self, data):
        """Classify current buffer using shared feature extraction."""
        if self.model is None or len(self.buffer) < WINDOWING['samples_per_window'] * 0.8:
            return "Unknown", 0.0
        
        # Extract features using shared module (same as training)
        try:
            features_dict = extract_all_features(list(self.buffer))
            features = features_to_array(features_dict)
            
            features_scaled = self.scaler.transform(features)
            prediction = self.model.predict(features_scaled)[0]
            probs = self.model.predict_proba(features_scaled)[0]
            confidence = np.max(probs)
            return prediction, confidence
        except Exception as e:
            logger.debug(f"Classification error: {e}")
            return "Unknown", 0.0
    
    def _count_steps(self, sensor_values):
        """Simple step counting."""
        heel_pressure = sensor_values.get('L_P_Heel', 0) + sensor_values.get('R_P_Heel', 0)
        
        if heel_pressure > 2000:
            current_time = time.time()
            if not hasattr(self, '_last_step'):
                self._last_step = 0
            
            if current_time - self._last_step > 0.3:
                self.step_count += 1
                self._last_step = current_time
    
    def _process_sample(self, timestamp, sensor_values):
        """Process a single sample."""
        # Add to buffer
        self.buffer.append(sensor_values)
        
        # Count steps
        self._count_steps(sensor_values)
        
        # Classify
        if len(self.buffer) >= WINDOWING['samples_per_window']:
            self.current_activity, self.confidence = self._classify(self.buffer)
            
            # Slide window
            for _ in range(int(WINDOWING['samples_per_window'] * 0.5)):
                if self.buffer:
                    self.buffer.popleft()
        
        # Update display
        if self.plotter:
            self.plotter.add_data(timestamp, sensor_values)
            status = f"Activity: {self.current_activity} | Confidence: {self.confidence:.2f} | Steps: {self.step_count}"
            self.plotter.update_status(status)
        elif self.text_demo:
            self.text_demo.update(timestamp, sensor_values, 
                                self.current_activity, self.confidence, self.step_count)
    
    def run_live(self):
        """Run live demo with hardware."""
        import serial
        
        logger.info(f"Connecting to {self.port}...")
        
        try:
            ser = serial.Serial(self.port, HARDWARE['serial_baudrate'], timeout=1)
            time.sleep(HARDWARE['serial_reset_delay'])
            
            logger.info("Connected! Starting demo...")
            
            if self.plotter:
                # Run in thread with matplotlib
                import threading
                
                def read_serial():
                    while True:
                        try:
                            line = ser.readline().decode('utf-8').strip()
                            if line and not line.startswith('#') and ',' in line:
                                parts = line.split(',')
                                if len(parts) >= SENSORS['total_count'] + 1:
                                    timestamp = int(parts[0])
                                    values = {SENSORS['names'][i]: int(parts[i+1]) 
                                             for i in range(SENSORS['total_count'])}
                                    self._process_sample(timestamp, values)
                        except (UnicodeDecodeError, ValueError):
                            pass
                
                thread = threading.Thread(target=read_serial, daemon=True)
                thread.start()
                self.plotter.show()
                
            else:
                # Text mode
                try:
                    while True:
                        line = ser.readline().decode('utf-8').strip()
                        if line and not line.startswith('#') and ',' in line:
                            parts = line.split(',')
                            if len(parts) >= SENSORS['total_count'] + 1:
                                timestamp = int(parts[0])
                                values = {SENSORS['names'][i]: int(parts[i+1]) 
                                         for i in range(SENSORS['total_count'])}
                                self._process_sample(timestamp, values)
                except KeyboardInterrupt:
                    pass
            
            ser.close()
            
        except serial.SerialException as e:
            logger.error(f"Serial error: {e}")
            return 1
        
        return 0
    
    def run_playback(self):
        """Run demo with recorded data."""
        logger.info(f"Loading playback file: {self.playback_file}")
        
        try:
            df = pd.read_csv(self.playback_file)
        except Exception as e:
            logger.error(f"Failed to load file: {e}")
            return 1
        
        # Validate data
        report = validate_sensor_data(df)
        if not report.is_valid:
            logger.warning(f"Data quality issues: {report.issues}")
        
        logger.info(f"Playing back {len(df)} samples...")
        
        if self.plotter:
            import threading
            
            def playback():
                for _, row in df.iterrows():
                    timestamp = row['time_ms'] if 'time_ms' in row else 0
                    values = {sensor: row[sensor] for sensor in SENSORS['names']}
                    self._process_sample(timestamp, values)
                    time.sleep(1 / HARDWARE['sample_rate_hz'])
            
            thread = threading.Thread(target=playback, daemon=True)
            thread.start()
            self.plotter.show()
            
        else:
            # Text mode
            try:
                for _, row in df.iterrows():
                    timestamp = row['time_ms'] if 'time_ms' in row else 0
                    values = {sensor: row[sensor] for sensor in SENSORS['names']}
                    self._process_sample(timestamp, values)
                    time.sleep(1 / HARDWARE['sample_rate_hz'])
            except KeyboardInterrupt:
                pass
        
        return 0
    
    def run(self):
        """Run demo."""
        if self.playback_file:
            return self.run_playback()
        elif self.port:
            return self.run_live()
        else:
            logger.error("Specify either --port for live demo or --playback for file")
            return 1


def main():
    parser = argparse.ArgumentParser(description='Smart Socks Interactive Demo')
    parser.add_argument('--port', '-p', help='Serial port for live demo')
    parser.add_argument('--playback', help='CSV file for playback demo')
    parser.add_argument('--model', '-m', help='Trained model for classification')
    parser.add_argument('--no-visualization', action='store_true', 
                       help='Use text mode only')
    
    args = parser.parse_args()
    
    if not args.port and not args.playback:
        parser.print_help()
        print("\nError: Specify either --port or --playback")
        return 1
    
    demo = SmartSocksDemo(
        model_path=args.model,
        port=args.port,
        playback_file=args.playback,
        visualize=not args.no_visualization
    )
    
    return demo.run()


if __name__ == '__main__':
    sys.exit(main())
