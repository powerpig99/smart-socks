# Smart Socks - Dual ESP32 Quick Start Guide

**Quick reference for the 6-sensor dual ESP32 configuration**

---

## Hardware Setup (5 minutes)

### Unified Pin Mapping (Same Pins, Different Modes)

We use **consistent pin assignments** across all modes:
- **A0-A2** = Left leg sensors
- **A3-A5** = Right leg sensors

| Sensor | Calibration | Left Leg (Prod) | Right Leg (Prod) |
|--------|-------------|-----------------|------------------|
| L_P_Heel | **A0** | A0 | — |
| L_P_Ball | **A1** | A1 | — |
| L_S_Knee | **A2** | A2 | — |
| R_P_Heel | **A3** | — | **A3** |
| R_P_Ball | **A4** | — | **A4** |
| R_S_Knee | **A5** | — | **A5** |

### Wiring

**Mode A: Calibration (1 ESP32, all 6 sensors)**
Use `calibration_all_sensors.ino` for this mode.
```
A0: L_P_Heel    A3: R_P_Heel
A1: L_P_Ball    A4: R_P_Ball  
A2: L_S_Knee    A5: R_S_Knee
```
Upload: `pio run -e calibration -t upload`

**Mode B: Production (2 ESP32s)**
```
Left ESP32:        Right ESP32:
A0: L_P_Heel       A3: R_P_Heel
A1: L_P_Ball       A4: R_P_Ball
A2: L_S_Knee       A5: R_S_Knee
(A3-A5 unused)     (A0-A2 unused)
```
Upload: `pio run -e left_leg -t upload` and `pio run -e right_leg -t upload`

### 2. Connect to Computer

| Leg | USB Port | Expected Device |
|-----|----------|-----------------|
| Left | USB-C | `/dev/cu.usbmodem2101` (macOS) |
| Right | USB-C | `/dev/cu.usbmodem2102` (macOS) |

**Find your ports:**
```bash
pio device list
# or
ls /dev/cu.usbmodem*
```

---

## Firmware Upload (3 minutes)

### Option A: PlatformIO (Recommended)

```bash
# Install PlatformIO if needed
pip install platformio

# Find your ports
pio device list

# Upload - Left Leg (A0-A2)
pio run --environment left_leg --target upload --upload-port /dev/cu.usbmodem2101

# Upload - Right Leg (A3-A5)
pio run --environment right_leg --target upload --upload-port /dev/cu.usbmodem2102

# Upload - Calibration mode (all 6 sensors on one ESP32)
pio run --environment calibration --target upload
```

### Option B: Arduino IDE

1. Install ESP32 board support:
   - File → Preferences → Additional Board Manager URLs
   - Add: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Tools → Board → Boards Manager → Search "esp32" → Install

2. Select board: **XIAO_ESP32S3**

3. Select port: `/dev/cu.usbmodem2101` (or your port)

4. Configure the leg in code:
   ```cpp
   // For left leg:
   const LegID LEG_ID = LEFT_LEG;
   
   // For right leg:
   // const LegID LEG_ID = RIGHT_LEG;
   ```

5. Click Upload

6. Repeat for the other leg (change `LEG_ID`)

---

## Data Collection

### Step 1: Start Calibration (Visual Check)

```bash
# Run calibration UI
python 04_Code/python/calibration_visualizer.py --port /dev/cu.usbmodem2101

# Or use web dashboard: http://192.168.4.1
```

You should see 6 sensor plots updating in real-time. Walk in place to verify all sensors respond.

### Step 2: Record Activity

```bash
# Record 30 seconds of walking
python 04_Code/python/dual_collector.py --activity walking \
  --left-port /dev/cu.usbmodem2101 \
  --right-port /dev/cu.usbmodem2102 \
  --subject test_user \
  --duration 30
```

Data saves to: `03_Data/collection/walking_test_user_YYYYMMDD_HHMMSS_dual.csv`

---

## Troubleshooting

| Problem | Check |
|---------|-------|
| "Failed to connect" | Correct port? `pio device list` |
| No sensor response | Wiring: 10kΩ resistors to GND? |
| Upload fails | Correct environment selected? |
| Wrong sensor values | Check pin mapping - left=A0-A2, right=A3-A5 |
| Values stuck at 0 | ADC pins connected? |
| Can't access web dashboard | WiFi mode configured correctly? Check serial output for IP |
| WiFi connection fails | SSID/password correct? 2.4GHz network? (ESP32 doesn't support 5GHz) |
| Same IP conflict | Different IPs configured for left/right? |

---

## File Reference

| File | Purpose |
|------|---------|
| `calibration_all_sensors.ino` | All 6 sensors on one ESP32 (A0-A5) |
| `data_collection_leg.ino` | Single leg (left=A0-A2, right=A3-A5) |
| `dual_collector.py` | Python collection tool |
| `platformio.ini` | Build config (calibration/left_leg/right_leg) |
| `PIN_MAPPING.md` | Detailed pin documentation |

---

## Command Cheat Sheet

```bash
# List ports
pio device list

# Upload firmware
pio run -e left_leg -t upload --upload-port /dev/cu.usbmodem2101
pio run -e right_leg -t upload --upload-port /dev/cu.usbmodem2102

# Calibrate with Python
python calibration_visualizer.py --port /dev/cu.usbmodem2101

# Record activity
python dual_collector.py --activity walking --duration 30

# Find devices on network (auto-discovery)
python find_smartsocks.py

# Test WiFi connection
python test_wifi_connection.py --ip 192.168.4.1
```

---

## WiFi Configuration

Choose your WiFi mode (see [[WIFI_CONFIGURATION]] and [[PHONE_HOTSPOT_GUIDE]] for details):

### Mode A: Phone Hotspot (Recommended for Demos) ⭐
Edit `data_collection_leg.ino`:
```cpp
#define USE_PHONE_HOTSPOT
const char* HOTSPOT_SSID = "YourPhoneName";      // Your phone's hotspot
const char* HOTSPOT_PASSWORD = "yourpassword";   // Hotspot password
```
Access via:
- http://smartsocks-left.local (mDNS)
- http://smartsocks-right.local (mDNS)
- Or scan for IPs: `python find_smartsocks.py`

### Mode B: Connect to Existing WiFi (Lab Use)
Edit `data_collection_leg.ino`:
```cpp
#define USE_EXISTING_WIFI
const char* EXISTING_WIFI_SSID = "aalto";
const char* EXISTING_WIFI_PASSWORD = "password";
```

### Mode C: ESP32 Creates WiFi Network (Standalone)
No changes needed. Connect laptop to:
- Network: `SmartSocks`
- Password: `smartwearables`
- Left leg: http://192.168.4.1
- Right leg: http://192.168.4.2

## WiFi & Bluetooth Testing

See [[WIFI_BLE_TESTING]] for detailed testing procedures.

Quick test:
1. Power on both ESP32s
2. Open browser to your configured IPs (or 192.168.4.1/.2 for AP mode)
3. Use nRF Connect app to scan for `SmartSocks-Left` and `SmartSocks-Right` BLE devices
4. Verify data streaming at 50Hz

---

*Updated: February 2026 · Unified Pin Mapping Edition*
