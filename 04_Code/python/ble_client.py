#!/usr/bin/env python3
"""
Smart Socks - BLE Client
ELEC-E7840 Smart Wearables (Aalto University)

Bluetooth Low Energy client for connecting to ESP32S3.
Receives sensor data wirelessly for real-time classification.

Usage:
    python ble_client.py --scan
    python ble_client.py --device "SmartSocks" --model ../05_Analysis/smart_socks_model.joblib
"""

import argparse
import asyncio
import sys
import time
import json
import numpy as np
from datetime import datetime
from collections import deque
from typing import Optional, Callable, Dict, Any

# Try to import bleak, provide helpful error if not installed
try:
    from bleak import BleakClient, BleakScanner
    from bleak.backends.characteristic import BleakGATTCharacteristic
    BLE_AVAILABLE = True
except ImportError:
    BLE_AVAILABLE = False
    print("Warning: BLE support requires 'bleak' package.")
    print("Install with: pip install bleak")

from config import HARDWARE, SENSORS, REALTIME, WINDOWING
from logging_utils import get_logger, setup_logging

logger = get_logger(__name__)


# BLE UUIDs (must match Arduino sketch)
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"

# Sensor configuration
SENSOR_NAMES = SENSORS['names']
WINDOW_SAMPLES = int(WINDOWING['window_size_ms'] / 1000 * HARDWARE['sample_rate_hz'])


class BLESmartSocksClient:
    """
    BLE client for Smart Socks data collection and real-time classification.
    """
    
    def __init__(
        self,
        device_name: str = "SmartSocks",
        service_uuid: str = SERVICE_UUID,
        char_uuid: str = CHARACTERISTIC_UUID,
        data_callback: Optional[Callable] = None
    ):
        self.device_name = device_name
        self.service_uuid = service_uuid
        self.char_uuid = char_uuid
        self.data_callback = data_callback
        
        self.client: Optional[BleakClient] = None
        self.device_address: Optional[str] = None
        self.connected = False
        
        # Data buffer for sliding window
        self.buffer = deque(maxlen=WINDOW_SAMPLES)
        
        # Statistics
        self.packets_received = 0
        self.start_time = None
        self.last_data_time = None
        
        # Recording
        self.recording = False
        self.record_file = None
        
    async def scan(self, timeout: float = 10.0) -> list:
        """
        Scan for BLE devices.
        
        Args:
            timeout: Scan duration in seconds
            
        Returns:
            List of discovered devices
        """
        logger.info(f"Scanning for BLE devices for {timeout}s...")
        
        devices = await BleakScanner.discover(timeout=timeout)
        
        # Filter for devices with our service or name
        smart_socks_devices = []
        for device in devices:
            if device.name and self.device_name.lower() in device.name.lower():
                smart_socks_devices.append(device)
                logger.info(f"Found Smart Socks: {device.name} ({device.address})")
            elif device.name:
                logger.debug(f"Found other device: {device.name} ({device.address})")
        
        return smart_socks_devices
    
    async def connect(self, address: Optional[str] = None) -> bool:
        """
        Connect to the Smart Socks device.
        
        Args:
            address: Device address (if None, will scan first)
            
        Returns:
            True if connected successfully
        """
        if not BLE_AVAILABLE:
            logger.error("BLE not available. Install bleak package.")
            return False
        
        # Find device address if not provided
        if address is None:
            devices = await self.scan()
            if not devices:
                logger.error(f"No devices found with name '{self.device_name}'")
                return False
            address = devices[0].address
        
        self.device_address = address
        logger.info(f"Connecting to {address}...")
        
        try:
            self.client = BleakClient(address)
            await self.client.connect()
            
            if self.client.is_connected:
                self.connected = True
                logger.info(f"Connected to {address}")
                
                # Discover services
                services = await self.client.get_services()
                logger.debug(f"Discovered {len(services.services)} services")
                
                return True
            else:
                logger.error("Connection failed")
                return False
                
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from device."""
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            self.connected = False
            logger.info("Disconnected")
    
    def _parse_data(self, data: bytes) -> Optional[Dict[str, Any]]:
        """
        Parse incoming BLE data packet.
        
        Expected format: "timestamp,sensor1,sensor2,...,sensor10\n"
        
        Args:
            data: Raw bytes from BLE
            
        Returns:
            Dictionary with parsed data or None if invalid
        """
        try:
            # Decode bytes to string
            line = data.decode('utf-8').strip()
            
            # Skip metadata lines
            if line.startswith('#') or not line:
                return None
            
            # Parse CSV
            parts = line.split(',')
            if len(parts) < SENSORS['total_count'] + 1:  # timestamp + sensors
                return None
            
            result = {
                'timestamp': int(parts[0]),
                'sensors': {}
            }
            
            for i, sensor in enumerate(SENSOR_NAMES):
                result['sensors'][sensor] = int(parts[i + 1])
            
            return result
            
        except (UnicodeDecodeError, ValueError) as e:
            logger.debug(f"Parse error: {e}")
            return None
    
    def _notification_handler(self, sender: BleakGATTCharacteristic, data: bytearray):
        """
        Handle incoming BLE notifications.
        
        Args:
            sender: Characteristic that sent the notification
            data: Raw data bytes
        """
        self.packets_received += 1
        self.last_data_time = time.time()
        
        # Parse data
        parsed = self._parse_data(bytes(data))
        if parsed is None:
            return
        
        # Add to buffer
        self.buffer.append(parsed['sensors'])
        
        # Save to file if recording
        if self.recording and self.record_file:
            line = f"{parsed['timestamp']},{','.join(str(parsed['sensors'][s]) for s in SENSOR_NAMES)}\n"
            self.record_file.write(line)
            self.record_file.flush()
        
        # Call user callback
        if self.data_callback:
            self.data_callback(parsed)
    
    async def start_data_collection(self, output_file: Optional[str] = None):
        """
        Start receiving data from the device.
        
        Args:
            output_file: Optional file to save data to
        """
        if not self.connected:
            logger.error("Not connected to device")
            return
        
        # Open output file if specified
        if output_file:
            self.record_file = open(output_file, 'w')
            # Write header
            header = "time_ms," + ",".join(SENSOR_NAMES) + "\n"
            self.record_file.write(header)
            self.recording = True
            logger.info(f"Recording to {output_file}")
        
        # Enable notifications
        await self.client.start_notify(self.char_uuid, self._notification_handler)
        logger.info("Data collection started")
        
        self.start_time = time.time()
        self.packets_received = 0
    
    async def stop_data_collection(self):
        """Stop receiving data."""
        if self.client and self.client.is_connected:
            await self.client.stop_notify(self.char_uuid)
        
        if self.record_file:
            self.record_file.close()
            self.record_file = None
            self.recording = False
        
        # Print statistics
        if self.start_time:
            duration = time.time() - self.start_time
            rate = self.packets_received / duration if duration > 0 else 0
            logger.info(f"Collection stopped. Received {self.packets_received} packets "
                       f"in {duration:.1f}s ({rate:.1f} Hz)")
    
    async def send_command(self, command: str):
        """
        Send command to the device.
        
        Args:
            command: Command string (e.g., "START S01 walking_forward")
        """
        if not self.connected:
            logger.error("Not connected")
            return
        
        try:
            data = command.encode('utf-8')
            await self.client.write_gatt_char(self.char_uuid, data)
            logger.info(f"Sent command: {command}")
        except Exception as e:
            logger.error(f"Failed to send command: {e}")
    
    def get_buffer_data(self) -> np.ndarray:
        """
        Get current buffer as numpy array.
        
        Returns:
            Array of shape (n_samples, n_sensors)
        """
        if len(self.buffer) == 0:
            return np.array([])
        
        data = []
        for sample in self.buffer:
            row = [sample[sensor] for sensor in SENSOR_NAMES]
            data.append(row)
        
        return np.array(data)


class BLEClassifier(BLESmartSocksClient):
    """
    Extended BLE client with real-time classification.
    """
    
    def __init__(self, model_path: str, **kwargs):
        super().__init__(**kwargs)
        
        # Load ML model
        self._load_model(model_path)
        
        # Classification state
        self.current_activity = "Unknown"
        self.confidence = 0.0
        self.step_count = 0
        self.prediction_history = deque(maxlen=REALTIME['smoothing_window'])
        
    def _load_model(self, model_path: str):
        """Load trained model."""
        import joblib
        
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(model_path.replace('.joblib', '_scaler.joblib'))
        metadata = joblib.load(model_path.replace('.joblib', '_metadata.joblib'))
        
        self.feature_names = metadata['feature_names']
        self.classes = metadata['classes']
        
        logger.info(f"Loaded model with classes: {self.classes}")
    
    def _extract_features(self, data: np.ndarray) -> np.ndarray:
        """
        Extract features from window of data.
        
        Args:
            data: Array of shape (n_samples, n_sensors)
            
        Returns:
            Feature vector
        """
        features = []
        
        # Statistical features per sensor
        for i, sensor in enumerate(SENSOR_NAMES):
            sensor_data = data[:, i]
            features.append(np.mean(sensor_data))
            features.append(np.std(sensor_data))
            features.append(np.min(sensor_data))
            features.append(np.max(sensor_data))
            features.append(np.percentile(sensor_data, 25))
            features.append(np.percentile(sensor_data, 75))
            features.append(np.sqrt(np.mean(sensor_data**2)))  # RMS
        
        # Cross-sensor features
        SENSOR_NAMES = SENSORS['names']
        left_indices = [SENSOR_NAMES.index(s) for s in SENSORS['left_leg']]
        right_indices = [SENSOR_NAMES.index(s) for s in SENSORS['right_leg']]
        left_total = np.sum(data[:, left_indices], axis=1)
        right_total = np.sum(data[:, right_indices], axis=1)
        features.append(np.mean(left_total))
        features.append(np.mean(right_total))
        features.append(np.mean(left_total) / (np.mean(right_total) + 1e-6))
        
        return np.array(features).reshape(1, -1)
    
    def _classify(self) -> tuple:
        """
        Classify current buffer contents.
        
        Returns:
            (activity, confidence)
        """
        if len(self.buffer) < WINDOW_SAMPLES * 0.8:
            return "Unknown", 0.0
        
        data = self.get_buffer_data()
        features = self._extract_features(data)
        
        # Scale and predict
        features_scaled = self.scaler.transform(features)
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]
        confidence = np.max(probabilities)
        
        # Smooth predictions
        self.prediction_history.append((prediction, confidence))
        
        if len(self.prediction_history) >= 3:
            # Vote weighted by confidence
            votes = {}
            for pred, conf in self.prediction_history:
                votes[pred] = votes.get(pred, 0) + conf
            prediction = max(votes, key=votes.get)
        
        return prediction, confidence
    
    def _count_steps(self, sensor_data: Dict[str, int]):
        """
        Simple step counting based on heel pressure.
        
        Args:
            sensor_data: Dictionary of sensor values
        """
        # Simple threshold-based step detection
        left_heel = sensor_data.get('L_P_Heel', 0)
        right_heel = sensor_data.get('R_P_Heel', 0)
        total_pressure = left_heel + right_heel
        
        threshold = REALTIME['step_counting']['threshold']
        min_interval = REALTIME['step_counting']['min_step_interval_ms'] / 1000
        
        if total_pressure > threshold:
            current_time = time.time()
            if not hasattr(self, '_last_step_time'):
                self._last_step_time = 0
            
            if current_time - self._last_step_time > min_interval:
                self.step_count += 1
                self._last_step_time = current_time
    
    def _on_data(self, parsed_data: Dict):
        """
        Callback for new data - perform classification.
        
        Args:
            parsed_data: Parsed sensor data
        """
        # Count steps
        self._count_steps(parsed_data['sensors'])
        
        # Classify when buffer is full
        if len(self.buffer) >= WINDOW_SAMPLES:
            self.current_activity, self.confidence = self._classify()
            
            # Print status
            status = f"\r[{datetime.now().strftime('%H:%M:%S')}] "
            status += f"Activity: {self.current_activity:<20} "
            status += f"Confidence: {self.confidence:.2f}  "
            status += f"Steps: {self.step_count}"
            print(status, end='', flush=True)
            
            # Slide window
            for _ in range(int(WINDOW_SAMPLES * 0.5)):
                if self.buffer:
                    self.buffer.popleft()


async def main():
    parser = argparse.ArgumentParser(description='Smart Socks BLE Client')
    parser.add_argument('--scan', action='store_true', help='Scan for devices')
    parser.add_argument('--device', default='SmartSocks', help='Device name')
    parser.add_argument('--address', help='Device MAC address')
    parser.add_argument('--model', help='Path to trained model for classification')
    parser.add_argument('--output', '-o', help='Output CSV file')
    parser.add_argument('--duration', '-d', type=int, help='Duration in seconds')
    parser.add_argument('--command', '-c', help='Send command to device')
    
    args = parser.parse_args()
    
    if not BLE_AVAILABLE:
        print("Error: bleak package not installed.")
        print("Install with: pip install bleak")
        return 1
    
    setup_logging()
    
    # Scan mode
    if args.scan:
        client = BLESmartSocksClient(device_name=args.device)
        devices = await client.scan()
        
        print(f"\n{'='*60}")
        print("SCAN RESULTS")
        print('='*60)
        if devices:
            for i, device in enumerate(devices):
                print(f"{i+1}. {device.name} - {device.address}")
        else:
            print("No Smart Socks devices found.")
            print("Make sure the device is powered on and advertising.")
        return 0
    
    # Create client (classifier or data collection)
    if args.model:
        client = BLEClassifier(
            model_path=args.model,
            device_name=args.device
        )
        print(f"Loaded model from {args.model}")
    else:
        client = BLESmartSocksClient(device_name=args.device)
    
    # Connect
    if not await client.connect(args.address):
        return 1
    
    # Send command if specified
    if args.command:
        await client.send_command(args.command)
        await asyncio.sleep(1)
    
    # Start data collection
    await client.start_data_collection(args.output)
    
    try:
        # Run for specified duration or indefinitely
        if args.duration:
            await asyncio.sleep(args.duration)
        else:
            print("\nPress Ctrl+C to stop...")
            while True:
                await asyncio.sleep(1)
                
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        await client.stop_data_collection()
        await client.disconnect()
        
        if args.model:
            print(f"\n\nFinal Activity: {client.current_activity}")
            print(f"Total Steps: {client.step_count}")
    
    return 0


if __name__ == '__main__':
    result = asyncio.run(main())
    sys.exit(result)
