# PlatformIO Setup Guide - Smart Socks Project

> **Related:** [[README]] | [[CODE_REVIEW]] | [[calibration_visualizer]]

## Overview

This document describes the complete setup for developing the [[Smart Socks]] project using [[PlatformIO]] in [[VS Code]] with the [[XIAO ESP32S3]] [[microcontroller]].

---

## Hardware Platform

| Component | Specification | Notes |
|-----------|--------------|-------|
| **Board** | [[Seeed Studio]] [[XIAO ESP32S3]] | [[ESP32-S3]] based |
| **Processor** | 240MHz dual-core | |
| **RAM** | 320KB | |
| **Flash** | 8MB | |
| **ADC Resolution** | 12-bit (0-4095) | See [[ADC Configuration]] |
| **USB Port** | USB-C | [[CDC]] mode enabled |

### macOS Port Detection

### Default Port
**Port:** `/dev/cu.usbmodem2101` (macOS example)

### For Other Machines
The XIAO ESP32S3 appears as:
- **macOS:** `/dev/cu.usbmodemXXXX` or `/dev/tty.usbmodemXXXX`
- **Linux:** `/dev/ttyUSB0` or `/dev/ttyACM0`
- **Windows:** `COM3`, `COM4`, etc.

**Find your port:**
```bash
# PlatformIO (recommended)
pio device list

# Or manual:
# macOS: ls /dev/cu.usbmodem*
# Linux: ls /dev/ttyUSB* /dev/ttyACM*
# Windows: Check Device Manager > Ports
```

---

## Project Structure

```
Smart Socks/
├── platformio.ini          # [[PlatformIO]] configuration
├── src/
│   └── main.cpp           # Entry point (symlink to [[Arduino]] sketch)
├── 04_Code/
│   └── arduino/
│       ├── blink_xiao/              # Basic LED test
│       ├── rgb_led_test/            # PWM LED test
│       ├── final_check/             # Diagnostic sketch
│       ├── sensor_test/             # Basic [[ADC]] reading
│       ├── data_collection/         # [[Serial]] data collection
│       ├── data_collection_ble/     # [[BLE]]-enabled data collection
│       └── data_collection_wireless/# [[WiFi]] + BLE + Web dashboard ⭐
└── 03_Data/               # Data logging output
```

**Recommended for calibration:** [[data_collection_wireless]] — provides [[WiFi]] web dashboard, [[BLE]] streaming, and [[Serial]] interface.

---

## PlatformIO Configuration

### `platformio.ini`

```ini
[env:xiao_esp32s3]
platform = espressif32
board = seeed_xiao_esp32s3
framework = arduino
upload_speed = 921600
monitor_speed = 115200
build_flags = 
    -D ARDUINO_USB_MODE=1
    -D ARDUINO_USB_CDC_ON_BOOT=1

[platformio]
src_dir = 04_Code/arduino
default_envs = xiao_esp32s3
```

### Key Configuration Details

| Setting | Value | Purpose |
|---------|-------|---------|
| `platform` | `espressif32` | Espressif ESP32 platform |
| `board` | `seeed_xiao_esp32s3` | Specific board definition |
| `framework` | `arduino` | Arduino framework |
| `upload_speed` | `921600` | Fast upload (9x faster than default) |
| `monitor_speed` | `115200` | Serial monitor baud rate |
| `ARDUINO_USB_MODE=1` | CDC mode | USB Serial for programming |
| `ARDUINO_USB_CDC_ON_BOOT=1` | CDC on boot | Enable Serial at startup |

---

## Pin Mapping

### Analog Sensor Inputs (10 channels)

| Zone | Variable Name | Pin | GPIO | Notes |
|------|--------------|-----|------|-------|
| **Left Sock** |
| Heel | `L_HEEL` | A0 | GPIO 1 | Standard analog |
| Arch | `L_ARCH` | A1 | GPIO 2 | Standard analog |
| Metatarsal Medial | `L_META_MED` | A2 | GPIO 3 | Standard analog |
| Metatarsal Lateral | `L_META_LAT` | A3 | GPIO 4 | Standard analog |
| Toe | `L_TOE` | A4 | GPIO 5 | Standard analog |
| **Right Sock** |
| Heel | `R_HEEL` | A5 | GPIO 6 | Standard analog |
| Arch | `R_ARCH` | GPIO 7 | GPIO 7 | D8/SDA pin |
| Metatarsal Medial | `R_META_MED` | GPIO 8 | GPIO 8 | D9/SCL pin |
| Metatarsal Lateral | `R_META_LAT` | GPIO 9 | GPIO 9 | D10/MOSI pin |
| Toe | `R_TOE` | GPIO 10 | GPIO 10 | Alternate function |

**Important:** XIAO ESP32S3 only has A0-A5 defined. For channels 6-9, use GPIO numbers directly (7-10).

### LED Pin

| Component | Pin | Notes |
|-----------|-----|-------|
| Built-in RGB LED | GPIO 21 | WS2812B - requires PWM or NeoPixel library |

**Note:** Simple `digitalWrite(21, HIGH)` will NOT work. Use `ledcAttach()` + `ledcWrite()` for basic PWM, or Adafruit NeoPixel library for full RGB control.

---

## Critical Code Changes

### 1. Arduino.h Include (PlatformIO Requirement)

**Problem:** [[PlatformIO]] compiles `.cpp` files directly without [[Arduino IDE]] preprocessing.

**Solution:** Add `#include <Arduino.h>` at the top of all `.cpp` files:

```cpp
#include <Arduino.h>  // Required for PlatformIO

// Sensor pin definitions...
```

> **Note:** See [[CODE_REVIEW]] Issue #3 for related import fixes in Python.

### 2. Pin Definitions for XIAO ESP32S3

**Original (Arduino Uno style - FAILED):**
```cpp
const int R_ARCH = A6;      // ERROR: 'A6' not defined
const int R_META_MED = A7;  // ERROR: 'A7' not defined
```

**Fixed (Using GPIO numbers):**
```cpp
const int R_ARCH = 7;       // GPIO 7 (D8/SDA)
const int R_META_MED = 8;   // GPIO 8 (D9/SCL)
const int R_META_LAT = 9;   // GPIO 9 (D10/MOSI)
const int R_TOE = 10;       // GPIO 10
```

---

## Build and Upload Instructions

### VS Code + PlatformIO Extension

1. **Open Project:** File → Open Folder → `Smart Socks/`

2. **Build:** Click checkmark icon (✓) in bottom toolbar or:
   ```
   PlatformIO: Build
   ```

3. **Upload:** Click arrow icon (→) in bottom toolbar or:
   ```
   PlatformIO: Upload
   ```

4. **Serial Monitor:** Click terminal icon in bottom toolbar or:
   ```
   PlatformIO: Serial Monitor
   ```

### Command Line (Alternative)

```bash
# Build
~/.platformio/penv/bin/pio run -e xiao_esp32s3

# Upload
~/.platformio/penv/bin/pio run -e xiao_esp32s3 --target upload

# Serial Monitor
~/.platformio/penv/bin/pio device monitor -e xiao_esp32s3
```

---

## Sensor Test Output Format

### Serial Output (115200 baud)

```
Smart Socks Sensor Test
=======================
Place known weights on sensors for characterization.
Format: timestamp,L_Heel,L_Arch,L_MetaM,L_MetaL,L_Toe,R_Heel,R_Arch,R_MetaM,R_MetaL,R_Toe

time_ms,L_Heel,L_Arch,L_MetaM,L_MetaL,L_Toe,R_Heel,R_Arch,R_MetaM,R_MetaL,R_Toe
181556,712,694,672,831,734,720,820,855,829,143
181576,703,699,678,839,745,729,821,855,839,137
...
```

### Data Format

| Column | Description | Range |
|--------|-------------|-------|
| `time_ms` | Timestamp since boot (milliseconds) | 0 - 2^32 |
| `L_Heel` | Left heel sensor ADC value | 0 - 4095 |
| `L_Arch` | Left arch sensor ADC value | 0 - 4095 |
| `L_MetaM` | Left metatarsal medial ADC value | 0 - 4095 |
| `L_MetaL` | Left metatarsal lateral ADC value | 0 - 4095 |
| `L_Toe` | Left toe sensor ADC value | 0 - 4095 |
| `R_Heel` | Right heel sensor ADC value | 0 - 4095 |
| `R_Arch` | Right arch sensor ADC value | 0 - 4095 |
| `R_MetaM` | Right metatarsal medial ADC value | 0 - 4095 |
| `R_MetaL` | Right metatarsal lateral ADC value | 0 - 4095 |
| `R_Toe` | Right toe sensor ADC value | 0 - 4095 |

### ADC Value Interpretation

| Condition | Expected Value | Notes |
|-----------|----------------|-------|
| No sensor connected | ~700-850 | Floating input noise |
| No pressure (max resistance) | ~4000-4095 | 10kΩ pullup, sensor open |
| Maximum pressure | ~0-500 | Sensor resistance << 10kΩ |

---

## Troubleshooting

### Build Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `'A6' was not declared` | XIAO only has A0-A5 | Use GPIO numbers (7-10) |
| `'Serial' was not declared` | Missing Arduino.h | Add `#include <Arduino.h>` |
| `'millis' was not declared` | Missing Arduino.h | Add `#include <Arduino.h>` |

### Upload Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Port not found` | Board not connected | Check USB cable (must be data cable) |
| `Failed to connect` | Wrong port | Default is `/dev/cu.usbmodem2101`. Use `pio device list` to find yours |
| `Permission denied` | Port permissions | No sudo needed on macOS |

### Runtime Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| LED doesn't blink | RGB LED on GPIO 21 | Use PWM (`ledcWrite`) or NeoPixel |
| No serial output | Wrong baud rate | Use 115200 baud |
| Garbled output | USB CDC not enabled | Check `ARDUINO_USB_CDC_ON_BOOT=1` |

---

## Memory Usage

Last build statistics:

```
RAM:   [=         ]   5.7% (used 18812 bytes from 327680 bytes)
Flash: [=         ]   7.8% (used 261857 bytes from 3342336 bytes)
```

**Plenty of headroom** for additional features (WiFi, data logging, ML inference, etc.)

---

## Development Workflow

### 1. Initial Setup (One-time)

```bash
# Install PlatformIO VS Code extension
# Open Smart Socks folder in VS Code
# PlatformIO will auto-install platform and toolchains
```

### 2. Daily Development Cycle

```
1. Edit code in 04_Code/arduino/sensor_test/
2. Click Build (✓) to compile
3. Click Upload (→) to flash
4. Click Serial Monitor to view data
5. Press Ctrl+C to stop monitor
```

### 3. Data Logging

Copy serial monitor output to file:
```bash
# In VS Code terminal
cat > ../03_Data/sensor_reading_$(date +%Y%m%d_%H%M%S).csv
# Then start monitor and copy data
```

---

## Wireless Data Collection (Recommended)

The [[data_collection_wireless]] sketch provides **three connection methods** simultaneously:

### Features
- **WiFi AP Mode**: Web dashboard at `192.168.4.1`
- **BLE Streaming**: JSON sensor data via Bluetooth
- **Serial Interface**: CSV data and command interface

### Upload Wireless Sketch

```bash
# Copy wireless sketch to src/main.cpp
cp 04_Code/arduino/data_collection_wireless/data_collection_wireless.ino src/main.cpp

# Build and upload
pio run --target upload
```

### Connection Options

#### Option 1: WiFi Web Dashboard (Recommended for Calibration)

1. **Connect to [[WiFi]] AP** on your laptop/phone:
   - SSID: `SmartSocks`
   - Password: `smartwearables`

2. **Open browser**: http://192.168.4.1

3. **Features**:
   - Real-time bar graphs for all 10 [[sensors]]
   - Min/max tracking
   - Start/Stop recording
   - Download [[CSV]] data
   - Sample rate display

#### Option 2: Python [[calibration_visualizer]]

```bash
cd 04_Code/python
python calibration_visualizer.py --port /dev/cu.usbmodem2101
# Replace with your port. See Port Detection section above
```

See [[calibration_visualizer]] for detailed documentation.

**Controls:**
| Key | Action |
|-----|--------|
| `Q` | Quit |
| `R` | Reset min/max tracking |
| `S` | Save calibration [[CSV]] |
| `P` | Pause/Resume |

**Features:**
- Live time series plots (5s history)
- Current values bar chart
- Min/max statistics panel
- Color-coded pressure levels

#### Option 3: [[BLE]] Connection

Use any [[BLE]] terminal app to connect to `SmartSocks-BLE`:

| Command | Description |
|---------|-------------|
| `START` | Start recording |
| `STOP` | Stop recording |
| `CAL ON` | Enable [[calibration]] mode |
| `STATUS` | Show system status |

> **Note:** See [[CODE_REVIEW]] Issue #2 for [[BLE]] MTU chunking implementation.

### WiFi + BLE Configuration

| Parameter | Value |
|-----------|-------|
| WiFi SSID | `SmartSocks` |
| WiFi Password | `smartwearables` |
| Web Interface | http://192.168.4.1 |
| BLE Device Name | `SmartSocks-BLE` |
| BLE Service UUID | `4fafc201-1fb5-459e-8fcc-c5c9c331914b` |
| BLE Characteristic | `beb5483e-36e1-4688-b7f5-ea07361b26a8` |

---

## Calibration Workflow

### Step 1: Upload Wireless Sketch
```bash
pio run --target upload
```

### Step 2: Connect via WiFi or Python Visualizer
```bash
# Option A: Web dashboard (open browser to 192.168.4.1)
# Option B: Python visualizer
python calibration_visualizer.py --port /dev/cu.usbmodem2101
# Replace with your port. See Port Detection section above
```

### Step 3: Verify Sensor Response
1. Place known weights on each sensor zone
2. Observe ADC value changes (0-4095)
3. Check that min/max ranges are reasonable
4. Verify all 10 channels respond

### Step 4: Save Calibration Data
- Press `S` in Python visualizer
- Or use web dashboard to record and download

### Step 5: Collect Calibration Curves
Apply incremental weights and record ADC values for each sensor:
- 0g (no load)
- 100g
- 200g
- 500g
- 1000g

---

## References

- [XIAO ESP32S3 Wiki](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/)
- [PlatformIO ESP32 Platform](https://docs.platformio.org/en/latest/platforms/espressif32.html)
- [ESP32-S3 ADC Documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/adc.html)

---

## Summary

✅ **PlatformIO + VS Code** configured for XIAO ESP32S3  
✅ **10-channel ADC** sensor reading at 50Hz  
✅ **Pin mapping** established for all 10 sensor zones  
✅ **Serial output** formatted for data logging  
✅ **Build/upload** workflow verified and working  

**Status:** Ready for sensor characterization and calibration experiments.


---

## Navigation

| ← Previous | ↑ Up | Next → |
|------------|------|--------|
| [[CODE_REVIEW]] | [[INDEX]] | [[README]] |

**Related Topics:**
- [[calibration_visualizer]] — Python calibration visualization
- [[data_collection_wireless]] — WiFi+BLE+Serial firmware
- [[ESP32-S3]] — Hardware documentation
- [[ADC]] — Analog-to-digital converter setup
