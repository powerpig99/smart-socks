# Smart Socks - Quick Start Guide

**Quick reference for the 6-sensor single ESP32 configuration**

---

## Hardware Setup

### Pin Mapping

One ESP32S3 XIAO reads all 6 sensors:

| Pin | Sensor | Type | Location |
|-----|--------|------|----------|
| **A0** | L_P_Heel | Pressure | Left heel |
| **A1** | L_P_Ball | Pressure | Left ball of foot |
| **A2** | L_S_Knee | Stretch | Left knee |
| **A3** | R_P_Heel | Pressure | Right heel |
| **A4** | R_P_Ball | Pressure | Right ball of foot |
| **A5** | R_S_Knee | Stretch | Right knee |

### Wiring

```
ESP32S3 XIAO
═════════════
3.3V ──┬──┬──┬──┬──┬──┬── All sensor VCC
       │  │  │  │  │  │
A0  ───┘  │  │  │  │  │  L_P_Heel
A1  ──────┘  │  │  │  │  L_P_Ball
A2  ─────────┘  │  │  │  L_S_Knee
A3  ────────────┘  │  │  R_P_Heel
A4  ─────────────────┘  │  R_P_Ball
A5  ────────────────────┘  R_S_Knee

GND ──┬──┬──┬──┬──┬──┬── All sensor GND
     10kΩ pull-down on each pin
```

### Connect to Computer

| Item | Value |
|------|-------|
| USB Port | USB-C |
| Serial Device | `/dev/cu.usbmodem2101` (macOS) |

**Find your port:**
```bash
pio device list
# or
ls /dev/cu.usbmodem*
```

---

## Firmware Upload

### PlatformIO (Recommended)

```bash
# Upload data collection firmware (WiFi + BLE + serial)
pio run -e xiao_esp32s3 -t upload

# Upload calibration firmware (simple serial-only)
pio run -e calibration -t upload

# Serial monitor
pio device monitor -e xiao_esp32s3
```

### Arduino IDE

1. Install ESP32 board support:
   - File > Preferences > Additional Board Manager URLs
   - Add: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Tools > Board > Boards Manager > Search "esp32" > Install

2. Select board: **XIAO_ESP32S3**

3. Select port: `/dev/cu.usbmodem2101` (or your port)

4. Upload

---

## Data Collection

### Step 1: Start Calibration (Visual Check)

```bash
# Run calibration UI
python 04_Code/python/calibration_visualizer.py --port /dev/cu.usbmodem2101

# Or use web dashboard (if WiFi configured)
```

You should see 6 sensor plots updating in real-time. Walk in place to verify all sensors respond.

### Step 2: Record Activity

```bash
# Record 30 seconds of walking
python 04_Code/python/collector.py --activity walking_forward \
  --port /dev/cu.usbmodem2101 \
  --subject S01 \
  --duration 30
```

Data saves to: `03_Data/raw/S01_walking_forward_YYYYMMDD_HHMMSS.csv`

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

---

## File Reference

| File | Purpose |
|------|---------|
| `calibration_all_sensors.ino` | Simple serial-only 6-sensor firmware |
| `data_collection_leg.ino` | Full-featured firmware (WiFi + BLE + serial) |
| `collector.py` | Python data collection tool |
| `platformio.ini` | Build config (xiao_esp32s3 / calibration) |
| `PIN_MAPPING.md` | Detailed pin documentation |

---

## Command Cheat Sheet

```bash
# List ports
pio device list

# Upload firmware
pio run -e xiao_esp32s3 -t upload

# Calibrate with Python
python calibration_visualizer.py --port /dev/cu.usbmodem2101

# Record activity
python collector.py --activity walking_forward --duration 30

# Serial monitor
pio device monitor -e xiao_esp32s3
```

---

## WiFi Configuration

Choose your WiFi mode (see [[WIFI_CONFIGURATION]] for details):

### Mode A: Phone Hotspot (Recommended for Demos)
Edit `credentials.h`:
```cpp
#define HOTSPOT_SSID "YourPhoneName"
#define HOTSPOT_PASSWORD "yourpassword"
```
Access via:
- http://smartsocks.local (mDNS)
- Or check serial output for assigned IP

### Mode B: Connect to Existing WiFi (Lab Use)
Edit `credentials.h`:
```cpp
#define EXISTING_WIFI_SSID "aalto"
#define EXISTING_WIFI_PASSWORD "password"
```

### Mode C: ESP32 Creates WiFi Network (Standalone)
No changes needed. Connect laptop to:
- Network: `SmartSocks`
- Password: `smartwearables`
- Dashboard: http://192.168.4.1

## BLE Testing

1. Install a BLE scanner app (nRF Connect for iOS/Android)
2. Scan for `SmartSocks` BLE device
3. Connect and enable notifications on the characteristic
4. Data streams as JSON

---

*Updated: January 2026 · Single ESP32 Edition*
