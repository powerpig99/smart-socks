#!/usr/bin/env python3
"""
Smart Socks - Device Discovery Tool
Finds ESP32s on the network by scanning for their API endpoints

Usage:
    python find_smartsocks.py
    python find_smartsocks.py --ip-range 192.168.1
    python find_smartsocks.py --timeout 1.0
"""

import argparse
import socket
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
import json


def get_local_ip_range() -> str:
    """Get local IP address range (e.g., '192.168.1')."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return ".".join(local_ip.split(".")[:3])
    except:
        return "192.168.1"


def check_ip(ip: str, timeout: float = 0.5) -> Optional[Dict]:
    """Check if IP is a Smart Socks device."""
    try:
        url = f"http://{ip}/api/info"
        req = urllib.request.Request(url, method='GET')
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                # Check if this is a Smart Socks device
                hostname = data.get("hostname", "")
                if "smartsocks" in hostname.lower():
                    return data
    except:
        pass
    return None


def scan_network(ip_range: str, timeout: float = 0.5, max_workers: int = 50) -> List[Dict]:
    """Scan network for Smart Socks devices."""
    devices = []
    
    print(f"Scanning {ip_range}.1 - {ip_range}.254...")
    print("(This may take 10-20 seconds)\n")
    
    ips = [f"{ip_range}.{i}" for i in range(1, 255)]
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_ip, ip, timeout): ip for ip in ips}
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                devices.append(result)
                # Print as we find them
                print(f"✓ Found: {result.get('leg', 'unknown').upper()} leg at {result.get('ip', 'unknown')}")
    
    return devices


def print_device_info(devices: List[Dict]):
    """Pretty print device information."""
    if not devices:
        print("\n✗ No Smart Socks devices found.")
        print("\nTroubleshooting:")
        print("  - Are ESP32s powered on?")
        print("  - Are they on the same network?")
        print("  - Try specifying IP range: --ip-range 172.20.10")
        return
    
    print("\n" + "=" * 60)
    print("SMART SOCKS DEVICES FOUND")
    print("=" * 60)
    
    # Sort by leg (left first)
    devices.sort(key=lambda x: x.get('leg', ''))
    
    for dev in devices:
        leg = dev.get('leg', 'unknown').upper()
        mac = dev.get('mac', 'N/A')
        ip = dev.get('ip', 'N/A')
        hostname = dev.get('hostname', 'N/A')
        mode = dev.get('mode', 'unknown')
        ssid = dev.get('ssid', 'N/A')
        pins = dev.get('pins', [])
        
        print(f"\n{leg} LEG:")
        print(f"  MAC Address: {mac}")
        print(f"  IP Address:  {ip}")
        print(f"  Hostname:    {hostname}.local")
        print(f"  URLs:")
        print(f"    http://{ip}")
        print(f"    http://{hostname}.local")
        print(f"  WiFi Mode:   {mode}")
        if ssid != 'N/A':
            print(f"  Network:     {ssid}")
        if pins:
            print(f"  Sensors:     {', '.join(pins)}")
    
    print("\n" + "=" * 60)
    print(f"Total devices: {len(devices)}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Find Smart Socks ESP32 devices on the network',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect IP range and scan
  python find_smartsocks.py
  
  # Scan specific range (e.g., phone hotspot)
  python find_smartsocks.py --ip-range 172.20.10
  
  # Slower but more reliable scan
  python find_smartsocks.py --timeout 1.0 --max-workers 20
        """
    )
    
    parser.add_argument(
        '--ip-range',
        help='IP range to scan (e.g., 192.168.1). Auto-detected if not specified.'
    )
    parser.add_argument(
        '--timeout',
        type=float,
        default=0.5,
        help='Timeout for each connection attempt (default: 0.5s)'
    )
    parser.add_argument(
        '--max-workers',
        type=int,
        default=50,
        help='Number of parallel threads (default: 50)'
    )
    
    args = parser.parse_args()
    
    # Determine IP range
    if args.ip_range:
        ip_range = args.ip_range
    else:
        ip_range = get_local_ip_range()
        print(f"Auto-detected IP range: {ip_range}")
    
    # Scan network
    devices = scan_network(ip_range, args.timeout, args.max_workers)
    
    # Print results
    print_device_info(devices)
    
    # Return exit code
    return 0 if devices else 1


if __name__ == '__main__':
    exit(main())
