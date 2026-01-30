#!/usr/bin/env python3
"""
Smart Socks - WiFi Connection Test
Tests HTTP connection to ESP32 web servers

Usage:
    python test_wifi_connection.py --ip 192.168.4.1
    python test_wifi_connection.py --ip 192.168.4.2 --interval 0.5
"""

import argparse
import requests
import time
import sys
from datetime import datetime


def test_connection(ip, timeout=5):
    """Test HTTP connection to ESP32."""
    try:
        url = f"http://{ip}/api/sensors"
        response = requests.get(url, timeout=timeout)
        
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, f"HTTP {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Connection refused"
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)


def main():
    parser = argparse.ArgumentParser(description='Test Smart Socks WiFi Connection')
    parser.add_argument('--ip', default='192.168.4.1', help='ESP32 IP address')
    parser.add_argument('--interval', type=float, default=1.0, help='Poll interval in seconds')
    parser.add_argument('--count', type=int, help='Number of polls (default: infinite)')
    args = parser.parse_args()
    
    print("=" * 60)
    print("Smart Socks - WiFi Connection Test")
    print("=" * 60)
    print(f"Target: http://{args.ip}/api/sensors")
    print(f"Interval: {args.interval}s")
    print("=" * 60)
    print()
    
    success_count = 0
    fail_count = 0
    start_time = time.time()
    
    try:
        iteration = 0
        while args.count is None or iteration < args.count:
            iteration += 1
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            
            success, data = test_connection(args.ip)
            
            if success:
                success_count += 1
                # Format sensor values
                values = ", ".join([f"{k}={v}" for k, v in data.items()])
                print(f"[{timestamp}] ✓ {values}")
            else:
                fail_count += 1
                print(f"[{timestamp}] ✗ {data}")
            
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    
    # Summary
    elapsed = time.time() - start_time
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total attempts: {success_count + fail_count}")
    print(f"Successful: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Success rate: {100*success_count/(success_count+fail_count):.1f}%")
    print(f"Duration: {elapsed:.1f}s")
    print(f"Average rate: {(success_count+fail_count)/elapsed:.1f} polls/sec")
    print("=" * 60)


if __name__ == '__main__':
    main()
