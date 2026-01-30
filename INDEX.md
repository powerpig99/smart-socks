# Smart Socks Project — Obsidian Index

**ELEC-E7840 Smart Wearables — Topic 3**  
Team: Saara, Alex, Jing

---

> **🎯 COURSE STRUCTURE: 3 Parts**
> 
> **ELEC-E7840 Smart Wearables**
> 
> | Part | Focus | Team |
> |------|-------|------|
> | **Part 1** | Hardware & Sensor Characterization (**NO ML**) | Saara, Alex, Jing |
> | **Part 2** | Machine Learning & Classification | Jing only |
> | **Part 3** | Edge ML / TinyML Extension | Jing only |
> 
> **Current Focus:** Part 1 - Sensor fabrication, circuit design, calibration
> 
> **Hardware:** 6-sensor design (2 ESP32, 3 sensors each)
> 
> ---

> **Welcome to the Smart Socks Obsidian Vault!**
> 
> This index provides quick navigation to all project documents and concepts.
> Use `[[double-brackets]]` to explore linked notes, or open the **Graph View** (Ctrl+G) to see connections.

---

## 📁 Main Documents

| Document | Description | Link |
|----------|-------------|------|
| **Project Overview** | Main README with quick links | [[README]] |
| **Project Status** | Current status, recap, setup history | [[PROJECT_STATUS]] |
| **Work Diary** | Team meeting notes and decisions | [[WORK_DIARY]] |
| **PlatformIO Setup** | Hardware setup, build instructions (PlatformIO - Recommended) | [[PLATFORMIO_SETUP]] |
| **Arduino IDE FAQ** | ESP32 installation troubleshooting | [[ARDUINO_ESP32_INSTALLATION_FAQ]] |
| **Python Setup** | UV environment setup guide | [[README_PYTHON_SETUP]] |
| **Code Review** | Bug fixes and issue tracking | [[CODE_REVIEW]] |
| **Design Assets** | Nordic design system, logos, icons | [[DESIGN_ASSETS]] |

---

## 🔧 Hardware

### Design Documents (Updated Feb 2026)
| Document | Description |
|----------|-------------|
| [[sensor_placement_v2]] | 6-sensor placement guide (heel, ball, knee) |
| [[circuit_diagram_v2]] | Dual ESP32 system architecture + BOM |
| [[PIN_MAPPING]] | Unified pin mapping (A0-A2=left, A3-A5=right) |
| [[WIFI_CONFIGURATION]] | WiFi modes: AP vs Station vs Phone Hotspot |
| [[PHONE_HOTSPOT_GUIDE]] | Using phone hotspot for mobile demos |
| [[WIFI_BLE_TESTING]] | WiFi & Bluetooth testing procedures |
| [[EDGE_IMPULSE_ANALYSIS]] | **TinyML feasibility study & deep dive** |
| [[EDGE_IMPULSE_QUICKSTART]] | **Step-by-step Edge ML deployment** |
| [[LED_DISPLAY_RESEARCH]] | **LED feedback options (RGB, OLED, 7-segment)** |
| [[XIAO_Chapter_4/00_INDEX]] | **XIAO Book Ch.4 - TinyML (linked Markdown)** |

### Microcontroller
- [[ESP32-S3]] — Dual-core 240MHz processor
- [[XIAO ESP32S3]] — Seeed Studio development board
- [[ADC]] — 12-bit analog-to-digital converter
- [[GPIO]] — Pin mappings and configuration
- [[Dual ESP32]] — Two controllers (one per leg)

### Sensors
- [[Piezoresistive Sensors]] — Fabric pressure sensors
- [[Voltage Divider]] — 10kΩ reference circuit
- [[Sensor Zones]] — Heel, Arch, Metatarsal, Toe

### Connectivity
- [[USB-C]] — Programming and serial
- [[WiFi]] — Wireless access point mode
- [[BLE]] — Bluetooth Low Energy streaming
- [[Serial]] — UART communication

---

## 💻 Software

### Development Environment
- [[PlatformIO]] — IDE and build system
- [[VS Code]] — Editor with PlatformIO extension
- [[Arduino]] — Framework for ESP32
- [[Python]] — Data processing and ML

### Arduino Sketches
| Sketch | Purpose | Link |
|--------|---------|------|
| sensor_test | Basic ADC reading | `04_Code/arduino/sensor_test/` |
| data_collection | Serial data logging | `04_Code/arduino/data_collection/` |
| data_collection_ble | BLE streaming | `04_Code/arduino/data_collection_ble/` |
| data_collection_wireless | WiFi+BLE+Web | [[data_collection_wireless]] |
| **data_collection_leg** | **6-sensor dual ESP32** | [[data_collection_leg]] |
| **calibration_all_sensors** | **All 6 sensors on one ESP32** | `04_Code/arduino/calibration_all_sensors/` |

### Python Tools
| Tool | Purpose | Link |
|------|---------|------|
| calibration_visualizer | Real-time calibration UI | [[calibration_visualizer]] |
| feature_utils | Shared feature extraction | [[feature_utils.py]] |
| train_model | ML training pipeline | `04_Code/python/train_model.py` |
| real_time_classifier | Live classification | [[real_time_classifier.py]] |
| **dual_collector** | **Dual ESP32 collection** | [[dual_collector.py]] |
| **GIF Recording Fix** | **Technical deep-dive on calibration visualizer recording** | [[GIF_RECORDING_FIX]] |

---

## 📊 Data Pipeline

### Collection
- [[Sampling Rate]] — 50 Hz configuration
- [[Windowing]] — 1-second windows, 50% overlap
- [[CSV]] — Data format
- [[JSON]] — BLE data format

### Processing
- [[Data Preprocessing]] — Cleaning, normalization
- [[Feature Extraction]] — Statistical and frequency features
- [[Outlier Removal]] — Z-score based filtering

### Machine Learning
- [[Random Forest]] — Classification algorithm
- [[Cross-Subject Validation]] — Generalization testing
- [[Classification]] — Activity recognition
- [[Step Counting]] — Gait analysis

---

## 🎯 Calibration

### Tools
- [[calibration_visualizer]] — Python matplotlib UI
- [[Web Dashboard]] — Browser-based at 192.168.4.1
- [[Min/Max Tracking]] — Dynamic range detection

### Process
1. Upload [[data_collection_wireless]] firmware to **both** ESP32s
2. Connect to [[WiFi]] or run [[calibration_visualizer]] (two instances for two legs)
3. Apply known weights to each sensor zone:
   - Heel pressure (standing)
   - Ball pressure (toe push)
   - Knee stretch (knee flexion)
4. Record [[ADC]] response values
5. Save calibration to `03_Data/calibration/`

### Calibration Commands
```bash
# Terminal 1 - Left leg
python 04_Code/python/calibration_visualizer.py --port /dev/cu.usbmodem2101

# Terminal 2 - Right leg (different port)
python 04_Code/python/calibration_visualizer.py --port /dev/cu.usbmodem2102
```

---

## 🐛 Issues & Fixes

### Critical (All Fixed ✅)
- [[Issue 1]] — ADC pins (verified working)
- [[Issue 2]] — BLE MTU chunking
- [[Issue 3]] — Missing scipy.stats import
- [[Issue 4]] — Missing sys import
- [[Issue 5]] — samples_per_window calculation
- [[Issue 6]] — Filename parsing
- [[Issue 7]] — Fake step counting data

### High (All Fixed ✅)
- [[Issue 8]] — Command parsing
- [[Issue 9]] — setMaxPreferred fix
- [[Issue 10]] — Feature extraction mismatch
- [[Issue 11]] — demo.py features
- [[Issue 12]] — Window sliding
- [[Issue 13]] — quick_test warnings
- [[Issue 14]] — Accuracy parsing
- [[GIF_RECORDING_FIX]] — Calibration visualizer GIF recording (6 bugs fixed)

See [[CODE_REVIEW]] and [[AUDIT_GAPS_AND_FIXES]] for full details.

---

## 🚀 Quick Start

> **New to the project?** See [[DUAL_ESP32_QUICKSTART]] for the 6-sensor setup.
> 
> **Want Edge ML?** See [[EDGE_IMPULSE_QUICKSTART]] for TinyML deployment!

### 1. Hardware Setup
```bash
# Connect BOTH XIAO ESP32S3s via USB-C (one per leg)
# Default ports: /dev/cu.usbmodem2101 (Left), /dev/cu.usbmodem2102 (Right)
# Use `pio device list` to find your ports
```

### 2. Build & Upload
```bash
# In VS Code with PlatformIO:
# 1. Click Build (✓)
# 2. Click Upload (→)
```

### 3. Setup Python Environment
```bash
cd ~/Projects/Smart-Socks  # Adjust path as needed

# Create UV environment at project root
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r 04_Code/python/requirements.txt
```
See [[README_PYTHON_SETUP]] for details.

### 4. Calibration
```bash
# Option A: Python visualizer
python 04_Code/python/calibration_visualizer.py --port /dev/cu.usbmodem2101
# Use `pio device list` to find your port

# Option B: Web dashboard
# Connect to WiFi 'SmartSocks', open http://192.168.4.1
```

### 5. Data Collection
```bash
# Start recording via web dashboard or serial commands
# Download CSV when done
```

---

## 📁 Folder Structure

```
Smart Socks/
├── [[00_Planning]]/      # Plans, timelines, meeting notes
├── [[01_Design]]/        # Sensor layouts, sketches
├── [[02_Fabrication]]/   # Build photos, prototypes
├── [[03_Data]]/          # Calibration, collected data
├── [[04_Code]]/          # Arduino, Python
│   ├── [[arduino]]/
│   └── [[python]]/
├── [[05_Analysis]]/      # ML results, plots
├── [[06_Presentation]]/  # Slides, reports
└── [[07_References]]/    # Papers, reading list
```

---

## 🔗 External Links

- [XIAO ESP32S3 Wiki](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/)
- [PlatformIO Docs](https://docs.platformio.org/)
- [ESP32-S3 ADC Docs](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/adc.html)
- [Aalto MyCourses](https://mycourses.aalto.fi)

---

## 📝 Tags

#SmartSocks #ELEC-E7840 #Wearables #ESP32 #PlatformIO #Python #ML #Calibration #BLE #WiFi

---

*Last updated: 2026-02-01*  
*Open in [[Obsidian]] for best experience*
