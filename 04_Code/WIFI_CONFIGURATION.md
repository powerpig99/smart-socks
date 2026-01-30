# Smart Socks - WiFi Configuration Guide

**Two modes: Access Point (AP) vs Station (existing WiFi)**

---

## Mode 1: Station Mode (RECOMMENDED for Lab)

Connect ESP32s to your existing WiFi network (like `aalto` or lab WiFi).

### Setup

1. **Edit `data_collection_leg.ino`** (lines 35-48):

```cpp
// Uncomment to use existing WiFi:
#define USE_EXISTING_WIFI

// Set your lab WiFi credentials:
const char* EXISTING_WIFI_SSID = "aalto";           // Your WiFi name
const char* EXISTING_WIFI_PASSWORD = "password";    // Your WiFi password

// Static IPs - ask IT for 2 available IPs on your network:
const char* LEFT_IP_STR = "192.168.1.101";   // Left leg ESP32
const char* RIGHT_IP_STR = "192.168.1.102";  // Right leg ESP32
```

2. **Upload to both ESP32s**

3. **Access via browser:**
   - Left leg: http://192.168.1.101
   - Right leg: http://192.168.1.102

### Advantages
- ✅ Your laptop stays connected to normal WiFi
- ✅ Can access both ESP32s simultaneously
- ✅ Internet access while collecting data
- ✅ No network switching needed

### Requirements
- Need 2 available static IPs on your network
- Must know WiFi credentials
- Network must allow device-to-device communication

---

## Mode 2: Access Point Mode (Default)

Each ESP32 creates its own WiFi network.

### Setup

Leave `USE_EXISTING_WIFI` commented out (default):

```cpp
// Comment out or remove this line for AP mode:
// #define USE_EXISTING_WIFI
```

### Configuration

| ESP32 | Network Name | IP Address | Password |
|-------|--------------|------------|----------|
| Left | `SmartSocks` | 192.168.4.1 | `smartwearables` |
| Right | `SmartSocks` | 192.168.4.2 | `smartwearables` |

### Usage

1. Connect laptop to `SmartSocks` WiFi
2. Access left leg: http://192.168.4.1
3. Access right leg: http://192.168.4.2

### Advantages
- ✅ Works anywhere, no existing WiFi needed
- ✅ No IT configuration required
- ✅ Deterministic IPs (always 192.168.4.1 and .2)

### Limitations
- ❌ Laptop must disconnect from normal WiFi
- ❌ No internet access while connected
- ❌ Can be confusing if both ESP32s use same SSID

---

## Quick Start: Lab Setup (Station Mode)

### Step 1: Find Available IPs

Ask your network administrator for 2 available static IPs, or check yourself:

```bash
# Scan network to find available IPs
nmap -sn 192.168.1.0/24 | grep "Nmap scan"
```

### Step 2: Configure Credentials

```cpp
#define USE_EXISTING_WIFI
const char* EXISTING_WIFI_SSID = "aalto";
const char* EXISTING_WIFI_PASSWORD = "your_wifi_password";
const char* LEFT_IP_STR = "192.168.1.101";
const char* RIGHT_IP_STR = "192.168.1.102";
```

### Step 3: Upload

```bash
# Left leg
pio run -e left_leg -t upload

# Right leg
pio run -e right_leg -t upload
```

### Step 4: Test

```bash
# From your laptop (connected to same WiFi):
ping 192.168.1.101
curl http://192.168.1.101/api/sensors

curl http://192.168.1.102/api/sensors
```

---

## Hybrid Mode (Fallback)

If you enable `USE_EXISTING_WIFI` but the ESP32 fails to connect, it automatically falls back to AP mode. You'll see this in serial output:

```
Connecting to WiFi: aalto
.....
WiFi connection failed, falling back to AP mode
AP Mode IP: 192.168.4.1
```

---

## Troubleshooting

### Station Mode Issues

| Problem | Solution |
|---------|----------|
| "WiFi connection failed" | Check SSID/password, check if WiFi is 2.4GHz (ESP32 doesn't support 5GHz) |
| Can't access IP | Check if IP is already in use, try different IPs |
| Intermittent connection | Check WiFi signal strength, move ESP32 closer to router |

### AP Mode Issues

| Problem | Solution |
|---------|----------|
| Can't see "SmartSocks" | ESP32 not powered, check USB connection |
| Wrong IP (not 192.168.4.x) | Another device may have conflicting IP, try resetting ESP32 |

---

## Upload Methods

### Option 1: PlatformIO (Recommended)

```bash
# Setup
pip install platformio

# Upload left leg
pio run -e left_leg -t upload --upload-port /dev/cu.usbmodem2101

# Upload right leg
pio run -e right_leg -t upload --upload-port /dev/cu.usbmodem2102
```

### Option 2: Arduino IDE

1. Install ESP32 board support:
   - Boards Manager → Add URL: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Install "esp32" by Espressif Systems

2. Select board: **XIAO_ESP32S3**

3. Select port: `/dev/cu.usbmodem2101` (or your port)

4. Configure `LEG_ID` in code:
   ```cpp
   const LegID LEG_ID = LEFT_LEG;  // For left leg
   // const LegID LEG_ID = RIGHT_LEG;  // For right leg
   ```

5. Click Upload

6. Repeat for right leg (change `LEG_ID` to `RIGHT_LEG`)

---

## Python Data Collection

Regardless of WiFi mode, use the same Python commands:

```bash
# If using Station Mode (existing WiFi):
python dual_collector.py --calibrate
# Then connect to http://192.168.1.101 and http://192.168.1.102

# If using AP Mode:
# 1. Connect laptop to "SmartSocks" WiFi
# 2. Run:
python dual_collector.py --calibrate --left-port auto --right-port auto
```

---

*Last updated: February 2026*
