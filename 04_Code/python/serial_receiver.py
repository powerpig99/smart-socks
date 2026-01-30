#!/usr/bin/env python3
"""
Smart Socks - Serial Data Receiver
ELEC-E7840 Smart Wearables (Aalto University)

Receives sensor data from ESP32S3 via serial and saves to CSV files.
Supports the data_collection.ino protocol.

Usage:
    python serial_receiver.py --port /dev/ttyUSB0 --output ../03_Data/
"""

import argparse
import os
import sys
import serial
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import SENSORS

# Sensor channel names from config
SENSOR_NAMES = SENSORS['names']


class SerialReceiver:
    def __init__(self, port, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.is_recording = False
        self.output_file = None
        self.subject_id = None
        self.activity = None

    def connect(self):
        """Connect to the ESP32 via serial."""
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset
            print(f"Connected to {self.port} at {self.baudrate} baud")
            return True
        except serial.SerialException as e:
            print(f"Error connecting to {self.port}: {e}")
            return False

    def disconnect(self):
        """Disconnect from serial port."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            print("Disconnected from serial port")

    def send_command(self, command):
        """Send a command to the ESP32."""
        if self.serial and self.serial.is_open:
            self.serial.write((command + '\n').encode())
            print(f"Sent: {command}")

    def start_recording(self, subject_id, activity, output_dir):
        """Start a recording session."""
        self.subject_id = subject_id
        self.activity = activity

        # Create output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{subject_id}_{activity}_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)

        # Open output file
        self.output_file = open(filepath, 'w')
        self.is_recording = True

        # Send start command to ESP32
        self.send_command(f"START {subject_id} {activity}")
        print(f"Recording to: {filepath}")

    def stop_recording(self):
        """Stop the current recording session."""
        self.send_command("STOP")
        self.is_recording = False

        if self.output_file:
            self.output_file.close()
            self.output_file = None
            print("Recording stopped and file saved")

    def run(self, output_dir):
        """Main loop for receiving and saving data."""
        os.makedirs(output_dir, exist_ok=True)

        print("\n=== Smart Socks Serial Receiver ===")
        print("Commands:")
        print("  start <subject_id> <activity> - Start recording")
        print("  stop                          - Stop recording")
        print("  status                        - Request status from device")
        print("  quit                          - Exit program")
        print()

        while True:
            # Read from serial
            if self.serial and self.serial.in_waiting:
                try:
                    line = self.serial.readline().decode('utf-8').strip()
                    if line:
                        print(f"[RX] {line}")

                        # Save data if recording
                        if self.is_recording and self.output_file:
                            # Skip metadata lines (starting with #)
                            if not line.startswith('#'):
                                self.output_file.write(line + '\n')
                                self.output_file.flush()

                except UnicodeDecodeError:
                    pass

            # Check for user input (non-blocking would be better)
            try:
                user_input = input()
                if user_input:
                    self.process_user_command(user_input, output_dir)
            except EOFError:
                break


    def process_user_command(self, command, output_dir):
        """Process user commands from terminal."""
        parts = command.strip().lower().split()

        if not parts:
            return

        if parts[0] == 'start' and len(parts) >= 3:
            subject_id = parts[1].upper()
            activity = parts[2]
            self.start_recording(subject_id, activity, output_dir)

        elif parts[0] == 'stop':
            self.stop_recording()

        elif parts[0] == 'status':
            self.send_command("STATUS")

        elif parts[0] == 'quit':
            if self.is_recording:
                self.stop_recording()
            raise KeyboardInterrupt

        else:
            print("Unknown command. Use: start/stop/status/quit")


def main():
    parser = argparse.ArgumentParser(
        description='Smart Socks Serial Data Receiver'
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
        '--output', '-o',
        default='../../03_Data/',
        help='Output directory for CSV files'
    )

    args = parser.parse_args()

    receiver = SerialReceiver(args.port, args.baudrate)

    if not receiver.connect():
        return 1

    try:
        receiver.run(args.output)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        receiver.disconnect()

    return 0


if __name__ == '__main__':
    exit(main())
