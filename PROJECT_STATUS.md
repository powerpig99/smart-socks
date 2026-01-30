# Smart Socks - Project Status

**ELEC-E7840 Smart Wearables — Aalto University**  
**Team:** Saara, Alex, Jing  
**Last Updated:** January 30, 2026

---

## ⚠️ Critical Issues (Fix Before Data Collection)

See [`AUDIT_GAPS_AND_FIXES.md`](AUDIT_GAPS_AND_FIXES.md) for detailed tracking.

| Issue | File | Problem | Fix |
|-------|------|---------|-----|
| C3 | `demo.py` | `range(10)` crashes with 6 sensors | Change to `range(SENSORS['total_count'])` |
| C4 | `quick_test.py` | Rejects 6-sensor data (expects 10) | Change `>= 11` to `>= SENSORS['total_count'] + 1` |
| C5 | `dual_collector.py` | Imports non-existent `CONFIG` | Remove `CONFIG` from import |
| C1-C2 | `feature_utils.py` | Wrong index math for cross-sensor features | Rewrite to use config-based groupings |
| H1 | `demo.py`, `ble_client.py` | Old sensor names (`L_Heel` vs `L_P_Heel`) | Update to `SENSORS['names']` from config |

**Phase 1 (Crash Fixes):** 3 lines → fixes C3, C4, C5  
**Phase 2 (Features):** Consolidate `feature_utils.py` with `feature_extraction.py`  
**Phase 3 (Names):** Update old sensor name references

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
"R_P_Heel",  // Right Pressure - Heel (A0/GPIO 1 - on 2nd ESP32)
"R_P_Ball",  // Right Pressure - Ball (A1/GPIO 2 - on 2nd ESP32)
"R_S_Knee"   // Right Stretch - Knee (A2/GPIO 3 - on 2nd ESP32)
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
| `feature_extraction.py` | ✅ Ready | Config-aware feature extraction |
| `train_model.py` | ✅ Ready | ML pipeline |
| `real_time_classifier.py` | ⚠️ Needs Fix | Uses `feature_utils.py` (wrong features) |
| `dual_collector.py` | ❌ **BROKEN** | Import error (C5) |
| `demo.py` | ❌ **BROKEN** | `range(10)` crash (C3) |
| `quick_test.py` | ❌ **BROKEN** | Rejects 6-sensor data (C4) |

### Key Fixes Applied

1. **ADC Attenuation:** Added `analogSetAttenuation(ADC_11db)` to all sketches
2. **BLE MTU:** Implemented chunking for large data packets
3. **Feature Extraction:** Config-aware with correct sensor groupings
4. **Config Bug:** Fixed `samples_per_window` calculation (2→50)
5. **Missing Imports:** Added `scipy.stats` and `sys` imports

---

## Documentation Status

### Complete
- ✅ PLATFORMIO_SETUP.md
- ✅ SOFTWARE_INSTALLATION.md
- ✅ CODE_REVIEW.md
- ✅ INDEX.md (Obsidian navigation)
- ✅ DESIGN_ASSETS.md (Nordic design system)
- ✅ WORK_DIARY.md (consolidated meeting notes)
- ✅ sensor_placement_v2.md (new 6-sensor design)
- ✅ circuit_diagram_v2.md (dual ESP32)
- ✅ AUDIT_GAPS_AND_FIXES.md (issue tracking)

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
- [x] `data_preprocessing.py` imports from config
- [x] `serial_receiver.py` imports from config
- [x] `train_model.py` imports activities from config

### 🆕 New Design (Feb 2026)
- **Hardware:** Dual ESP32S3 XIAO (one per leg)
- **Sensors:** 6 total (4 pressure + 2 stretch)
- **Docs:** [[sensor_placement_v2]] | [[circuit_diagram_v2]]

### 🐛 Critical Bugs to Fix
- [ ] `demo.py` — `range(10)` crash (C3)
- [ ] `quick_test.py` — rejects 6-sensor data (C4)
- [ ] `dual_collector.py` — `CONFIG` import error (C5)
- [ ] `feature_utils.py` — wrong index math (C1-C2)
- [ ] `demo.py`, `ble_client.py` — old sensor names (H1)

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
1. **Fix Critical Bugs** (C3, C4, C5 — 3 lines total)
   - `demo.py`: Change `range(10)` to `range(SENSORS['total_count'])`
   - `quick_test.py`: Change `>= 11` to `>= SENSORS['total_count'] + 1`
   - `dual_collector.py`: Remove `CONFIG` from import

2. **Software Install**
   - Python: https://realpython.com/installing-python/
   - Video: https://www.youtube.com/watch?v=QhukcScB9W0
   - VS Code: https://code.visualstudio.com/

3. **Bring to Workshop**
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
