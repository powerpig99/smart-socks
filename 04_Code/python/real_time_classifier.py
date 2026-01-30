#!/usr/bin/env python3
"""
Smart Socks - Real-Time Activity Classifier
ELEC-E7840 Smart Wearables (Aalto University)

Receives live sensor data from ESP32S3 and performs real-time activity
classification using a pre-trained model. Supports both serial and BLE connections.

Usage:
    # Serial mode
    python real_time_classifier.py --model ../05_Analysis/smart_socks_model.joblib --port /dev/ttyUSB0
    
    # BLE mode
    python real_time_classifier.py --model ../05_Analysis/smart_socks_model.joblib --ble --device-name "SmartSocks"
"""

import argparse
import os
import sys
import time
import json
import numpy as np
import serial
import joblib
from collections import deque
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import SENSORS, WINDOWING, HARDWARE

# Backwards compatibility
SENSOR_NAMES = SENSORS['names']
SAMPLING = {'rate_hz': HARDWARE['sample_rate_hz']}
from feature_utils import extract_all_features, features_to_array, get_feature_names

# Window configuration (from config)
WINDOW_SIZE_MS = WINDOWING['window_size_ms']
WINDOW_SAMPLES = WINDOWING['samples_per_window']
STRIDE_SAMPLES = int(WINDOW_SAMPLES * 0.5)  # 50% overlap

# Classification smoothing
SMOOTHING_WINDOW_SIZE = 5  # Number of predictions to average


class RealTimeClassifier:
    """
    Real-time activity classifier for Smart Socks.
    """
    
    def __init__(self, model_path, connection_type='serial', **connection_params):
        """
        Initialize the classifier.
        
        Args:
            model_path: Path to saved model joblib file
            connection_type: 'serial' or 'ble'
            **connection_params: Connection-specific parameters
        """
        self.connection_type = connection_type
        self.connection_params = connection_params
        
        # Load model, scaler, and metadata
        self._load_model(model_path)
        
        # Data buffer for sliding window
        self.buffer = deque(maxlen=WINDOW_SAMPLES)
        
        # Prediction history for smoothing
        self.prediction_history = deque(maxlen=SMOOTHING_WINDOW_SIZE)
        
        # Statistics
        self.total_predictions = 0
        self.correct_predictions = 0  # If ground truth available
        self.latency_ms = []
        
        # Connection object
        self.connection = None
        
        # Current activity (for step counting)
        self.current_activity = None
        self.step_count = 0
        self.last_step_time = 0
        
    def _load_model(self, model_path):
        """Load the trained model and preprocessing objects."""
        base_path = model_path.replace('.joblib', '')
        
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(f"{base_path}_scaler.joblib")
        metadata = joblib.load(f"{base_path}_metadata.joblib")
        
        self.feature_names = metadata['feature_names']
        self.classes = metadata['classes']
        
        print(f"Loaded model from {model_path}")
        print(f"Model classes: {self.classes}")
        
    def connect(self):
        """Establish connection to ESP32."""
        if self.connection_type == 'serial':
            return self._connect_serial()
        elif self.connection_type == 'ble':
            return self._connect_ble()
        else:
            raise ValueError(f"Unknown connection type: {self.connection_type}")
    
    def _connect_serial(self):
        """Connect via serial port."""
        port = self.connection_params.get('port', '/dev/ttyUSB0')
        baudrate = self.connection_params.get('baudrate', 115200)
        
        try:
            self.connection = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)  # Wait for Arduino reset
            print(f"Connected to {port} at {baudrate} baud")
            return True
        except serial.SerialException as e:
            print(f"Error connecting to {port}: {e}")
            return False
    
    def _connect_ble(self):
        """Connect via Bluetooth Low Energy."""
        try:
            from bleak import BleakClient
            self.ble_available = True
        except ImportError:
            print("Error: BLE support requires 'bleak' package.")
            print("Install with: pip install bleak")
            return False
        
        # BLE implementation would go here
        # This is a placeholder for the actual BLE connection code
        print("BLE connection not fully implemented yet.")
        print("Falling back to serial mode.")
        self.connection_type = 'serial'
        return self._connect_serial()
    
    def disconnect(self):
        """Close connection."""
        if self.connection and hasattr(self.connection, 'is_open'):
            if self.connection.is_open:
                self.connection.close()
                print("Disconnected")
    
    def read_sensor_data(self):
        """
        Read a line of sensor data from the connection.
        
        Returns:
            dict with sensor values or None if no valid data
        """
        if not self.connection:
            return None
        
        try:
            if self.connection_type == 'serial':
                line = self.connection.readline().decode('utf-8').strip()
                if line and not line.startswith('#') and ',' in line:
                    parts = line.split(',')
                    if len(parts) >= SENSORS['total_count'] + 1:  # timestamp + sensors
                        values = {
                            'timestamp': int(parts[0]),
                        }
                        for i, sensor in enumerate(SENSOR_NAMES):
                            values[sensor] = int(parts[i + 1])
                        return values
        except (UnicodeDecodeError, ValueError) as e:
            pass
        
        return None
    
    def extract_features_from_buffer(self):
        """
        Extract features from the current buffer using shared feature extraction.
        
        Returns:
            numpy array of features matching training format
        """
        if len(self.buffer) < WINDOW_SAMPLES * 0.8:
            return None
        
        # Extract all features using shared module (same as training)
        features_dict = extract_all_features(list(self.buffer))
        
        # Convert to array with consistent ordering
        return features_to_array(features_dict)
    
    def classify(self, features):
        """
        Classify features and return prediction with confidence.
        
        Args:
            features: numpy array of features
        
        Returns:
            (predicted_class, confidence, all_probabilities)
        """
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Get prediction and probabilities
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]
        confidence = np.max(probabilities)
        
        return prediction, confidence, probabilities
    
    def smooth_prediction(self, prediction, confidence):
        """
        Apply temporal smoothing to predictions.
        
        Args:
            prediction: Current prediction
            confidence: Prediction confidence
        
        Returns:
            Smoothed prediction
        """
        self.prediction_history.append((prediction, confidence))
        
        if len(self.prediction_history) < 3:
            return prediction
        
        # Count votes weighted by confidence
        votes = {}
        for pred, conf in self.prediction_history:
            votes[pred] = votes.get(pred, 0) + conf
        
        # Return most voted class
        return max(votes, key=votes.get)
    
    def detect_steps(self, sensor_data, activity):
        """
        Simple step detection algorithm.
        
        Args:
            sensor_data: dict of sensor values
            activity: current activity classification
        
        Returns:
            True if step detected, False otherwise
        """
        if 'walking' not in activity and 'stairs' not in activity:
            return False
        
        # Use heel pressure for step detection (updated sensor names)
        left_heel = sensor_data.get('L_P_Heel', 0)
        right_heel = sensor_data.get('R_P_Heel', 0)
        total_pressure = left_heel + right_heel
        
        # Simple threshold-based step detection
        current_time = time.time() * 1000
        if total_pressure > 2000:  # Threshold
            if current_time - self.last_step_time > 300:  # Minimum 300ms between steps
                self.step_count += 1
                self.last_step_time = current_time
                return True
        
        return False
    
    def print_status(self, sensor_data, prediction, confidence, smoothed_pred):
        """Print current status."""
        # Clear line and print status
        status = f"\r[{datetime.now().strftime('%H:%M:%S')}] "
        status += f"Activity: {smoothed_pred:<20} "
        status += f"Confidence: {confidence:.2f}  "
        status += f"Steps: {self.step_count}"
        
        print(status, end='', flush=True)
    
    def run(self, duration_seconds=None, verbose=True):
        """
        Main classification loop.
        
        Args:
            duration_seconds: Run for specified duration (None = infinite)
            verbose: Print status updates
        """
        print("\n" + "="*60)
        print("Real-Time Activity Classification Started")
        print("="*60)
        print("Press Ctrl+C to stop\n")
        
        start_time = time.time()
        sample_count = 0
        classification_count = 0
        
        try:
            while True:
                # Check duration
                if duration_seconds and (time.time() - start_time) >= duration_seconds:
                    break
                
                # Read sensor data
                sensor_data = self.read_sensor_data()
                if sensor_data is None:
                    continue
                
                sample_count += 1
                self.buffer.append(sensor_data)
                
                # Classify when buffer is full
                if len(self.buffer) >= WINDOW_SAMPLES:
                    classify_start = time.time()
                    
                    # Extract features and classify
                    features = self.extract_features_from_buffer()
                    if features is not None:
                        prediction, confidence, probs = self.classify(features)
                        smoothed_pred = self.smooth_prediction(prediction, confidence)
                        
                        # Update step count
                        self.detect_steps(sensor_data, smoothed_pred)
                        
                        # Update current activity
                        if smoothed_pred != self.current_activity:
                            self.current_activity = smoothed_pred
                        
                        # Track latency
                        latency = (time.time() - classify_start) * 1000
                        self.latency_ms.append(latency)
                        
                        classification_count += 1
                        self.total_predictions += 1
                        
                        # Print status
                        if verbose and classification_count % 10 == 0:
                            self.print_status(sensor_data, prediction, confidence, smoothed_pred)
                    
                    # Slide window (keep half for next classification)
                    for _ in range(STRIDE_SAMPLES):
                        if self.buffer:
                            self.buffer.popleft()
        
        except KeyboardInterrupt:
            print("\n\nStopping...")
        
        # Print summary
        self._print_summary(sample_count, classification_count)
    
    def _print_summary(self, sample_count, classification_count):
        """Print session summary."""
        print("\n" + "="*60)
        print("Session Summary")
        print("="*60)
        print(f"Total samples received: {sample_count}")
        print(f"Classifications performed: {classification_count}")
        
        if self.latency_ms:
            print(f"\nLatency Statistics:")
            print(f"  Mean: {np.mean(self.latency_ms):.2f} ms")
            print(f"  Std:  {np.std(self.latency_ms):.2f} ms")
            print(f"  Max:  {np.max(self.latency_ms):.2f} ms")
        
        print(f"\nFinal Activity: {self.current_activity}")
        print(f"Total Steps Counted: {self.step_count}")


def main():
    parser = argparse.ArgumentParser(
        description='Smart Socks Real-Time Classifier'
    )
    parser.add_argument(
        '--model', '-m',
        required=True,
        help='Path to trained model joblib file'
    )
    parser.add_argument(
        '--port', '-p',
        default='/dev/ttyUSB0',
        help='Serial port (default: /dev/ttyUSB0)'
    )
    parser.add_argument(
        '--baudrate', '-b',
        type=int,
        default=115200,
        help='Baud rate (default: 115200)'
    )
    parser.add_argument(
        '--ble',
        action='store_true',
        help='Use Bluetooth Low Energy instead of serial'
    )
    parser.add_argument(
        '--device-name',
        default='SmartSocks',
        help='BLE device name (default: SmartSocks)'
    )
    parser.add_argument(
        '--duration', '-d',
        type=int,
        default=None,
        help='Duration to run in seconds (default: infinite)'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Reduce output verbosity'
    )

    args = parser.parse_args()

    # Determine connection type
    connection_type = 'ble' if args.ble else 'serial'
    
    # Create classifier
    classifier = RealTimeClassifier(
        model_path=args.model,
        connection_type=connection_type,
        port=args.port,
        baudrate=args.baudrate,
        device_name=args.device_name
    )
    
    # Connect
    if not classifier.connect():
        return 1
    
    try:
        # Run classification
        classifier.run(
            duration_seconds=args.duration,
            verbose=not args.quiet
        )
    finally:
        classifier.disconnect()
    
    return 0


if __name__ == '__main__':
    exit(main())
