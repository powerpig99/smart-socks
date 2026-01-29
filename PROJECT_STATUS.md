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

#### 3. Arduino IDE Issues (Resolved)
**Problem:** ESP32 board installation timeout in Arduino IDE Boards Manager  
**Solution:** Use **PlatformIO** or **arduino-cli** instead

```bash
# Arduino CLI (working alternative)
arduino-cli config init
arduino-cli config add board_manager.additional_urls \
  "https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json"
arduino-cli core update-index
arduino-cli core install esp32:esp32

# Upload to XIAO ESP32S3
arduino-cli upload -p /dev/cu.usbmodem2101 \
  --fqbn esp32:esp32:XIAO_ESP32S3 <sketch>
```

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

### Python Tools

| Tool | Status | Purpose |
|------|--------|---------|
| `calibration_visualizer.py` | ✅ Ready | Real-time sensor visualization |
| `feature_utils.py` | ✅ Ready | Shared feature extraction |
| `train_model.py` | ✅ Ready | ML pipeline |
| `real_time_classifier.py` | ✅ Ready | Live classification |

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
- [x] Pin mapping for GPIO 7-10 (not A6-A9)
- [x] ADC attenuation in all sketches
- [x] Port references (using `/dev/cu.usbmodem2101` as default)

### ⚠️ To Verify
- [ ] Arduino sketches updated for 6-sensor config (not 10)
- [ ] Circuit diagrams reflect new sensor placement
- [ ] Bill of materials updated (4 pressure + 2 stretch sensors)

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
