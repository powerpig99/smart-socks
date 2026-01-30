# Smart Socks - Project Status

**ELEC-E7840 Smart Wearables — Aalto University**  
**Team:** Saara, Alex, Jing  
**Last Updated:** January 29, 2026

---

## Project Recap

### Initial Setup (Completed)

#### 1. PlatformIO + VS Code Setup ✅
- **Platform:** Espressif32 for ESP32S3 XIAO
- **Board:** seeed_xiao_esp32s3
- **Framework:** Arduino
- **Port:** `/dev/cu.usbmodem2101` (macOS)

```ini
; platformio.ini
[env:xiao_esp32s3]
platform = espressif32
board = seeed_xiao_esp32s3
framework = arduino
upload_speed = 921600
monitor_speed = 115200
```

#### 2. Python Environment Setup ✅
- **Environment Manager:** UV (replaces pip+venv)
- **Location:** `~/Projects/Smart-Socks/.venv/`
- **Key Packages:** numpy, pandas, scipy, scikit-learn, matplotlib, pyserial, bleak

```bash
# Setup commands
cd ~/Projects/Smart-Socks
uv venv
source .venv/bin/activate
uv pip install -r 04_Code/python/requirements.txt
```

#### 3. Arduino IDE Setup (Has FAQ)
**Issue:** ESP32 board installation timeout in Arduino IDE Boards Manager  
**Solution:** See [[ARDUINO_ESP32_INSTALLATION_FAQ]] for troubleshooting

**Recommended:** Use **PlatformIO** (primary) or **arduino-cli** (alternative)

---

## Current Hardware Configuration (Jan 29, 2026)

### Sensor Setup (Team Decision)

| Component | Count | Placement | Type |
|-----------|-------|-----------|------|
| **Left Sock** | 2 | Heel + Ball | Pressure |
| **Left Knee** | 1 | Front | Stretch |
| **Right Sock** | 2 | Heel + Ball | Pressure |
| **Right Knee** | 1 | Front | Stretch |
| **Total** | **6** | — | 4 Pressure + 2 Stretch |

### Pinout Configuration

```cpp
// config.py sensor names
"L_P_Heel",  // Left Pressure - Heel (A0/GPIO 1)
"L_P_Ball",  // Left Pressure - Ball (A1/GPIO 2)
"L_S_Knee",  // Left Stretch - Knee (A2/GPIO 3)
"R_P_Heel",  // Right Pressure - Heel (A5/GPIO 6)
"R_P_Ball",  // Right Pressure - Ball (GPIO 7)
"R_S_Knee"   // Right Stretch - Knee (GPIO 8)
```

### Movement Detection Strategy

| Activity | Pressure | Stretch |
|----------|----------|---------|
| Walk Forward | Heel→Ball | Knee stretches |
| Walk Backward | Ball→Heel | Knee stretches |
| Stairs Up | Heel+Ball | **Strong** knee stretch |
| Stairs Down | Ball→Heel | Trailing leg stretches |
| Sit | Equal heels | Equal minimal |
| Stand | Equal heels+balls | Minimal |
| Lean | Asymmetric | Minimal |

---

## Code Status

### Arduino Sketches

| Sketch | Status | Description |
|--------|--------|-------------|
| `sensor_test` | ✅ Working | Basic ADC reading test |
| `data_collection` | ✅ Working | Serial data logging |
| `data_collection_ble` | ✅ Working | BLE wireless streaming |
| `data_collection_wireless` | ✅ Working | WiFi+BLE+Serial unified |
| `data_collection_leg` | ✅ **NEW** | 6-sensor dual ESP32 with sync |
| `calibration_all_sensors` | ✅ **NEW** | All 6 sensors on one ESP32 |

### Python Tools

| Tool | Status | Purpose |
|------|--------|---------|
| `calibration_visualizer.py` | ✅ Ready | Real-time sensor visualization |
| `feature_utils.py` | ✅ Ready | Shared feature extraction |
| `train_model.py` | ✅ Ready | ML pipeline |
| `real_time_classifier.py` | ✅ Ready | Live classification |
| `dual_collector.py` | ✅ **NEW** | Dual ESP32 data collection + merge |

### Key Fixes Applied

1. **ADC Attenuation:** Added `analogSetAttenuation(ADC_11db)` to all sketches
2. **BLE MTU:** Implemented chunking for large data packets
3. **Feature Extraction:** Unified between training and real-time (185 features)
4. **Config Bug:** Fixed `samples_per_window` calculation (2→50)
5. **Missing Imports:** Added `scipy.stats` and `sys` imports

---

## Documentation Status

### Complete
- ✅ PLATFORMIO_SETUP.md
- ✅ SOFTWARE_INSTALLATION.md
- ✅ CODE_REVIEW.md (all critical issues resolved)
- ✅ INDEX.md (Obsidian navigation)
- ✅ DESIGN_ASSETS.md (Nordic design system)
- ✅ WORK_DIARY.md (consolidated meeting notes)
- ✅ sensor_placement_v2.md (new 6-sensor design)

### Nordic Design Assets
- ✅ Logo (assets/logo.svg)
- ✅ Activity Icons (assets/activity_icons.svg)
- ✅ Slide Template (06_Presentation/templates/nordic_slides.html)
- ✅ Research Poster (06_Presentation/poster.html)

---

## Known Inconsistencies Checklist

### ✅ Fixed
- [x] Working diary consolidated (single WORK_DIARY.md)
- [x] Sensor count updated (10→6)
- [x] Sensor names updated in config.py
- [x] Pin mapping simplified (A0-A2 per ESP32)
- [x] ADC attenuation in all sketches
- [x] Port references (using `/dev/cu.usbmodem2101` as default)
- [x] Circuit diagram V2 created (dual ESP32)
- [x] Sensor placement V2 created (6-sensor config)
- [x] Bill of materials updated (4 pressure + 2 stretch + spares)

### 🆕 New Design (Feb 2026)
- **Hardware:** Dual ESP32S3 XIAO (one per leg)
- **Sensors:** 6 total (4 pressure + 2 stretch)
- **Docs:** [[sensor_placement_v2]] | [[circuit_diagram_v2]]

### ✅ New Features (Feb 2026)
- [x] Arduino `data_collection_leg.ino` - 6-sensor, sync support
- [x] Arduino `calibration_all_sensors.ino` - All 6 sensors on one ESP32
- [x] Synchronization: Independent / Master-Slave / Trigger modes
- [x] Python `dual_collector.py` - Merge + visualize dual streams
- [x] Unified pin mapping: A0-A2=left, A3-A5=right
- [x] WiFi: AP mode, Station mode, AND Phone Hotspot support
- [x] mDNS hostnames: smartsocks-left.local / smartsocks-right.local
- [x] MAC address identification for device discovery
- [x] Python `find_smartsocks.py` - Auto-discovery by MAC
- [x] BLE with device-specific names
- [x] Documentation: README for dual ESP32 setup
- [x] **Edge Impulse Analysis: TinyML feasibility study completed**
- [x] **Edge Impulse Quick Start guide for real-time edge ML**
- [x] **LED Display Research: RGB, OLED, 7-segment options documented**
- [x] **Reference Library: 8 papers organized with README**
- [x] **Arduino IDE FAQ: ESP32 installation troubleshooting guide**
- [x] **XIAO Chapter 4: Converted to linked Markdown for Obsidian**

### Course Structure: 3 Parts

| Part | Focus | Duration | Team |
|------|-------|----------|------|
| **Part 1** | Hardware & Sensor Characterization (**NO ML**) | Weeks 1-7 | Saara, Alex, Jing |
| **Part 2** | Machine Learning & Classification | Weeks 8-15 | Jing only |
| **Part 3** | Edge ML / TinyML Extension | Personal | Jing only |

### Part 1 Focus (All Team - NO ML)
**Priority: Hardware, Calibration, Data Collection**
- [ ] Fabricate 6 sensors (4 pressure + 2 stretch)
- [ ] Build voltage divider circuits
- [ ] Calibrate sensors with known weights
- [ ] Test BLE/WiFi data transmission
- [ ] Collect initial dataset
- [ ] **Mid-term deliverable:** Working prototype with sensor characterization

### Part 2 Focus (Jing Only - WITH ML)
**Priority: ML Pipeline & Real-time Classification**
- [ ] Collect training data from 6+ subjects
- [ ] Train Random Forest model (>85% accuracy)
- [ ] Real-time classification via Python
- [ ] User study with 5+ participants
- [ ] **Final deliverable:** Working ML system

### Part 3 Extension (Jing Only - Edge ML)
**Priority: TinyML on ESP32 (Optional)**
- [ ] Create Edge Impulse Studio project
- [ ] Deploy quantized model to ESP32
- [ ] Standalone operation without PC
- **Status:** Documented for future work

---

## Next Steps

### Immediate (Before Workshop Wed 04-02)
1. **Software Install**
   - Python: https://realpython.com/installing-python/
   - Video: https://www.youtube.com/watch?v=QhukcScB9W0
   - VS Code: https://code.visualstudio.com/

2. **Bring to Workshop**
   - USB-C cable
   - Microcontrollers (ESP32S3 XIAO)
   - Breadboard, jumper wires, resistors
   - Sensors

### Upcoming Meetings
- **Sun 2.2.2026, 14:45-16:45, Y163:** Progress review
- **Wed 4.2.2026:** WiFi data collection workshop

**Calendar Import:** `00_Planning/meetings/smart_socks_meetings.ics`

---

## Quick Commands Reference

```bash
# Build and upload firmware
cd ~/Projects/Smart-Socks
pio run --target upload --environment xiao_esp32s3

# Serial monitor
pio device monitor -e xiao_esp32s3

# Calibration visualizer
source .venv/bin/activate
python 04_Code/python/calibration_visualizer.py --port /dev/cu.usbmodem2101

# List available ports
pio device list
```

---

## Resources

- **GitHub:** https://github.com/powerpig99/smart-socks
- **Obsidian Vault:** Open `Smart-Socks` folder in Obsidian
- **PlatformIO Docs:** https://docs.platformio.org/
- **XIAO ESP32S3 Wiki:** https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/

---

*Document created for project continuity and team onboarding*
