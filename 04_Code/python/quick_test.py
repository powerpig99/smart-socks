#!/usr/bin/env python3
"""
Smart Socks - Quick Test Script
ELEC-E7840 Smart Wearables (Aalto University)

Quick sanity checks for the Smart Socks system:
- Verify sensor connections
- Test data streaming
- Check classification pipeline

Usage:
    python quick_test.py --port /dev/ttyUSB0
"""

import argparse
import sys
import time
import numpy as np
import serial


from config import SENSORS, HARDWARE

SENSOR_NAMES = SENSORS['names']
NUM_SENSORS = SENSORS['total_count']


def test_serial_connection(port, baudrate=115200, timeout=5):
    """Test serial connection to ESP32."""
    print(f"\n[TEST 1] Serial Connection")
    print(f"  Port: {port}, Baudrate: {baudrate}")
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Wait for Arduino reset
        
        # Clear buffer
        ser.reset_input_buffer()
        
        # Send status command
        ser.write(b"STATUS\n")
        time.sleep(0.5)
        
        # Read response
        response = b""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if ser.in_waiting:
                response += ser.read(ser.in_waiting)
                if b"Smart Socks" in response:
                    break
            time.sleep(0.1)
        
        ser.close()
        
        if b"Smart Socks" in response:
            print("  ✅ PASSED: Device responding")
            return True
        else:
            print("  ❌ FAILED: No valid response from device")
            return False
            
    except serial.SerialException as e:
        print(f"  ❌ FAILED: {e}")
        return False


def test_sensor_reading(port, baudrate=115200, duration=5):
    """Test sensor readings from ESP32."""
    print(f"\n[TEST 2] Sensor Reading")
    print(f"  Collecting data for {duration} seconds...")
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)
        ser.reset_input_buffer()
        
        # Start recording
        ser.write(b"START TEST sensor_test\n")
        time.sleep(0.5)
        
        readings = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8').strip()
                if line and not line.startswith('#') and ',' in line:
                    parts = line.split(',')
                    if len(parts) >= NUM_SENSORS + 1:
                        try:
                            values = [int(p) for p in parts[1:NUM_SENSORS+1]]
                            readings.append(values)
                        except ValueError:
                            pass
        
        # Stop recording
        ser.write(b"STOP\n")
        ser.close()
        
        if len(readings) < 10:
            print(f"  ❌ FAILED: Only {len(readings)} readings collected")
            return False
        
        readings = np.array(readings)
        
        print(f"  Collected {len(readings)} samples")
        print(f"  Sample rate: {len(readings)/duration:.1f} Hz")
        
        # Check each sensor
        all_ok = True
        for i, sensor in enumerate(SENSOR_NAMES):
            values = readings[:, i]
            mean_val = np.mean(values)
            std_val = np.std(values)
            unique_vals = len(np.unique(values))
            
            status = "✅"
            issue = ""
            
            # Check for stuck sensor (constant value)
            if unique_vals < 5:
                status = "⚠️"
                issue = " (possible disconnect)"
                all_ok = False
            # Check for unrealistic values
            elif mean_val < 10 and std_val < 5:
                status = "⚠️"
                issue = " (very low signal)"
            elif mean_val > 4000:
                status = "⚠️"
                issue = " (near saturation)"
            
            print(f"  {status} {sensor}: mean={mean_val:.0f}, std={std_val:.1f}, unique={unique_vals}{issue}")
        
        if all_ok:
            print("  ✅ PASSED: All sensors responding")
        else:
            print("  ⚠️ WARNING: Some sensors may have issues")
        
        return True
        
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False


def test_data_quality(port, baudrate=115200, duration=10):
    """Test data quality and consistency."""
    print(f"\n[TEST 3] Data Quality")
    print(f"  Collecting data for {duration} seconds...")
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)
        ser.reset_input_buffer()
        
        ser.write(b"START TEST quality_test\n")
        time.sleep(0.5)
        
        timestamps = []
        readings = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8').strip()
                if line and not line.startswith('#') and ',' in line:
                    parts = line.split(',')
                    if len(parts) >= SENSORS['total_count'] + 1:
                        try:
                            timestamp = int(parts[0])
                            values = [int(p) for p in parts[1:SENSORS['total_count'] + 1]]
                            timestamps.append(timestamp)
                            readings.append(values)
                        except ValueError:
                            pass
        
        ser.write(b"STOP\n")
        ser.close()
        
        if len(timestamps) < 10:
            print(f"  ❌ FAILED: Insufficient data")
            return False
        
        # Check timestamp consistency
        time_diffs = np.diff(timestamps)
        expected_interval = 20  # 50 Hz = 20ms
        
        dropout_count = np.sum(time_diffs > expected_interval * 2)
        dropout_rate = dropout_count / len(time_diffs)
        
        print(f"  Total samples: {len(timestamps)}")
        print(f"  Timestamp range: {timestamps[0]} - {timestamps[-1]} ms")
        print(f"  Average interval: {np.mean(time_diffs):.1f} ms")
        print(f"  Dropouts: {dropout_count} ({dropout_rate:.2%})")
        
        if dropout_rate < 0.05:
            print("  ✅ PASSED: Data quality good")
            return True
        elif dropout_rate < 0.15:
            print("  ⚠️ WARNING: Moderate dropout rate")
            return True
        else:
            print("  ❌ FAILED: High dropout rate")
            return False
        
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False


def test_pressure_response(port, baudrate=115200):
    """Test if sensors respond to pressure changes."""
    print(f"\n[TEST 4] Pressure Response")
    print("  INSTRUCTION: Apply pressure to different sensors while testing...")
    print("  Test running for 10 seconds...")
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)
        ser.reset_input_buffer()
        
        ser.write(b"START TEST pressure_test\n")
        time.sleep(0.5)
        
        # Collect baseline
        baseline_readings = []
        start_time = time.time()
        while time.time() - start_time < 3:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8').strip()
                if line and ',' in line and not line.startswith('#'):
                    parts = line.split(',')
                    if len(parts) >= SENSORS['total_count'] + 1:
                        try:
                            values = [int(p) for p in parts[1:11]]
                            baseline_readings.append(values)
                        except ValueError:
                            pass
        
        # Collect during pressure (user should be pressing)
        pressure_readings = []
        print("  Apply pressure now! (7 seconds remaining)")
        start_time = time.time()
        while time.time() - start_time < 7:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8').strip()
                if line and ',' in line and not line.startswith('#'):
                    parts = line.split(',')
                    if len(parts) >= SENSORS['total_count'] + 1:
                        try:
                            values = [int(p) for p in parts[1:11]]
                            pressure_readings.append(values)
                        except ValueError:
                            pass
        
        ser.write(b"STOP\n")
        ser.close()
        
        if len(baseline_readings) < 5 or len(pressure_readings) < 5:
            print("  ❌ FAILED: Insufficient data")
            return False
        
        baseline = np.array(baseline_readings)
        pressure = np.array(pressure_readings)
        
        print("\n  Pressure Response Analysis:")
        responding_sensors = 0
        
        for i, sensor in enumerate(SENSOR_NAMES):
            baseline_mean = np.mean(baseline[:, i])
            pressure_mean = np.mean(pressure[:, i])
            change = pressure_mean - baseline_mean
            change_pct = (change / (baseline_mean + 1)) * 100
            
            if abs(change) > 100:  # Significant change
                responding_sensors += 1
                print(f"  ✅ {sensor}: {change:+.0f} ({change_pct:+.1f}%)")
            else:
                print(f"  ⚪ {sensor}: {change:+.0f} (no significant change)")
        
        if responding_sensors >= NUM_SENSORS // 2:
            print(f"\n  ✅ PASSED: {responding_sensors}/{NUM_SENSORS} sensors responding")
            return True
        elif responding_sensors >= 2:
            print(f"\n  ⚠️ WARNING: Only {responding_sensors}/{NUM_SENSORS} sensors responding")
            return True
        else:
            print(f"\n  ❌ FAILED: Only {responding_sensors}/{NUM_SENSORS} sensors responding")
            return False
        
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False


def test_ml_pipeline():
    """Test if ML pipeline components are available."""
    print(f"\n[TEST 5] ML Pipeline Components")
    
    tests = [
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("scikit-learn", "sklearn"),
        ("matplotlib", "matplotlib"),
        ("scipy", "scipy"),
        ("joblib", "joblib"),
    ]
    
    all_ok = True
    for name, module in tests:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - NOT INSTALLED")
            all_ok = False
    
    # Check for pipeline scripts
    import os
    scripts = [
        "feature_extraction.py",
        "train_model.py",
        "real_time_classifier.py",
        "data_preprocessing.py"
    ]
    
    print("\n  Pipeline Scripts:")
    for script in scripts:
        if os.path.exists(script):
            print(f"  ✅ {script}")
        else:
            print(f"  ❌ {script} - NOT FOUND")
            all_ok = False
    
    if all_ok:
        print("\n  ✅ PASSED: All ML components available")
        return True
    else:
        print("\n  ⚠️ WARNING: Some components missing")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Smart Socks Quick Test'
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
        '--skip-hardware',
        action='store_true',
        help='Skip hardware tests (software only)'
    )

    args = parser.parse_args()

    print("="*60)
    print("SMART SOCKS - QUICK TEST")
    print("="*60)
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Software tests (always run)
    results.append(("ML Pipeline", test_ml_pipeline()))
    
    # Hardware tests
    if not args.skip_hardware:
        results.append(("Serial Connection", test_serial_connection(args.port, args.baudrate)))
        results.append(("Sensor Reading", test_sensor_reading(args.port, args.baudrate)))
        results.append(("Data Quality", test_data_quality(args.port, args.baudrate)))
        results.append(("Pressure Response", test_pressure_response(args.port, args.baudrate)))
    else:
        print("\n[NOTE] Hardware tests skipped (--skip-hardware)")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
        return 0
    elif passed >= total * 0.7:
        print("\n⚠️ MOST TESTS PASSED - Check warnings above")
        return 0
    else:
        print("\n❌ MULTIPLE TESTS FAILED - Please check setup")
        return 1


if __name__ == '__main__':
    exit(main())
