# Smart Socks - Phone Hotspot Guide

**Using your phone's hotspot for mobile demos**

---

## Why Phone Hotspot?

- ✅ Full control over network settings
- ✅ Works anywhere (lab, field, home)
- ✅ Easy to troubleshoot
- ✅ No IT department needed
- ✅ mDNS hostnames work reliably

---

## Quick Setup

### Step 1: Configure ESP32

Edit `data_collection_leg.ino` (lines 45-60):

```cpp
// Choose phone hotspot mode:
#define USE_PHONE_HOTSPOT

// Set your phone's hotspot credentials:
const char* HOTSPOT_SSID = "YourPhoneName";      // e.g., "iPhone-Jing"
const char* HOTSPOT_PASSWORD = "yourpassword";   // Your hotspot password
```

### Step 2: Enable Phone Hotspot

**iPhone:**
1. Settings → Personal Hotspot → Turn On
2. Note the WiFi Password
3. (Optional) Set hotspot name in Settings → General → About → Name

**Android:**
1. Settings → Network & Internet → Hotspot & Tethering
2. WiFi Hotspot → Turn On
3. Note/Set the Network Name and Password

### Step 3: Upload Firmware

```bash
# Left leg
pio run -e left_leg -t upload --upload-port /dev/cu.usbmodem2101

# Right leg
pio run -e right_leg -t upload --upload-port /dev/cu.usbmodem2102
```

### Step 4: Check Serial Output

Open serial monitor to see connection status:

```
========================================
Smart Socks - Left Leg Data Collection
========================================

Device Information:
  Leg: Left
  MAC Address: A4:CF:12:34:56:78
  Hostname: smartsocks-left

Connecting to phone hotspot: iPhone-Jing
......
✓ Hotspot Connected!
  IP Address: 172.20.10.4
  mDNS: http://smartsocks-left.local
```

---

## Access Methods

### Method 1: IP Address (Direct)

Check serial output for IP, then:
- Left leg: http://172.20.10.4 (example)
- Right leg: http://172.20.10.5 (example)

### Method 2: mDNS Hostname (Recommended)

Use hostname instead of remembering IPs:
- Left leg: http://smartsocks-left.local
- Right leg: http://smartsocks-right.local

> **Note:** mDNS requires Bonjour/Avahi on your laptop:
> - **macOS:** Built-in (works out of box)
> - **Windows:** Install iTunes or Bonjour Print Services
> - **Linux:** `sudo apt install avahi-daemon`

### Method 3: MAC Address (Most Reliable)

Each ESP32 has a unique MAC address printed on startup:

```
MAC Address: A4:CF:12:34:56:78
```

You can identify devices by MAC even if IPs change.

**Get MAC via API:**
```bash
curl http://172.20.10.4/api/info
# {"leg":"left","mac":"A4:CF:12:34:56:78","hostname":"smartsocks-left",...}
```

---

## Python Data Collection with Phone Hotspot

### Option 1: Auto-discovery by MAC

Create a discovery script that finds ESP32s by MAC:

```python
# find_smartsocks.py
import subprocess
import json
import requests
from concurrent.futures import ThreadPoolExecutor

def scan_network():
    """Scan local network for Smart Socks devices."""
    # Get your IP range (e.g., 172.20.10.x)
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    
    base = ".".join(local_ip.split(".")[:3])
    
    devices = []
    
    def check_ip(ip):
        try:
            response = requests.get(f"http://{ip}/api/info", timeout=0.5)
            if response.status_code == 200:
                data = response.json()
                if "smartsocks" in data.get("hostname", ""):
                    return data
        except:
            pass
        return None
    
    # Scan common IP range
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(check_ip, f"{base}.{i}") for i in range(1, 255)]
        for future in futures:
            result = future.result()
            if result:
                devices.append(result)
    
    return devices

# Usage
if __name__ == "__main__":
    print("Scanning for Smart Socks devices...")
    devices = scan_network()
    for dev in devices:
        print(f"{dev['leg'].upper()} LEG:")
        print(f"  MAC: {dev['mac']}")
        print(f"  IP: {dev['ip']}")
        print(f"  Hostname: {dev['hostname']}")
        print(f"  URL: http://{dev['ip']}")
```

### Option 2: Use mDNS Discovery

```bash
# macOS/Linux - discover via mDNS
dns-sd -B _http._tcp

# Look for smartsocks-left and smartsocks-right
```

---

## Troubleshooting

### "Hotspot connection failed!"

| Cause | Solution |
|-------|----------|
| Wrong password | Check hotspot password on phone |
| Hotspot not enabled | Turn on Personal Hotspot |
| Phone locked | Some phones disable hotspot when locked |
| 5GHz only | ESP32 only supports 2.4GHz - enable "Maximize Compatibility" on iPhone |

### Can't access via mDNS (.local)

| Platform | Solution |
|----------|----------|
| macOS | Should work - try `ping smartsocks-left.local` |
| Windows | Install Bonjour: https://support.apple.com/kb/DL999 |
| Linux | `sudo apt install avahi-daemon` |

### IP keeps changing

Phone hotspots often use DHCP. Solutions:
1. **Use mDNS hostnames** (smartsocks-left.local) - auto-updates
2. **Check serial output** on startup for current IP
3. **Use MAC address** to identify which device is which

---

## Example: Complete Phone Hotspot Workflow

```bash
# 1. Enable hotspot on phone
# 2. Configure and upload firmware to both ESP32s
# 3. Connect laptop to same hotspot

# 4. Find devices
python find_smartsocks.py
# Found:
# LEFT LEG:
#   MAC: A4:CF:12:34:56:78
#   IP: 172.20.10.4
#   URL: http://172.20.10.4
# RIGHT LEG:
#   MAC: A4:CF:12:87:65:43
#   IP: 172.20.10.5
#   URL: http://172.20.10.5

# 5. Open dashboards
open http://172.20.10.4    # Left leg
open http://172.20.10.5    # Right leg

# 6. Or use mDNS
open http://smartsocks-left.local
open http://smartsocks-right.local

# 7. Collect data
python dual_collector.py --calibrate
```

---

## Tips for Mobile Demos

1. **Power both ESP32s** from USB battery packs
2. **Use mDNS hostnames** to avoid IP confusion
3. **Write down MAC addresses** on stickers for each ESP32
4. **Test beforehand** - verify hotspot connection at demo location
5. **Bring USB cables** for debugging if needed

---

*Last updated: February 2026*
