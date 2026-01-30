# Smart Socks for Physical Activity Recognition

**ELEC-E7840 Smart Wearables** -- Aalto University

**Team:** Saara (ML, sensors, docs), Alex (Prototyping, user testing, design), Jing (Circuit, ESP32, coordination)

Recognizes 5 activity categories (walking, stair climbing, sitting, sit-to-stand, standing) using textile-based pressure and stretch sensors on socks and knee pads. No IMUs -- textile sensors only.

---

## Quick Start

### Python Setup

```bash
cd ./04_Code/python
uv sync                         # Creates .venv and installs all dependencies
source .venv/bin/activate        # Activate environment
# Or run scripts directly: uv run python script.py
```

See [[README_PYTHON_SETUP]] for UV installation and detailed instructions.

### PlatformIO Setup

```bash
# Upload firmware
pio run -e xiao_esp32s3 -t upload

# Serial monitor
pio device monitor -e xiao_esp32s3
```

See [[PLATFORMIO_SETUP]] for VS Code integration and board setup.

---

## Architecture

6-sensor configuration on a single ESP32S3 (pins A0-A5):

```
ESP32S3 XIAO (all 6 sensors):
  A0: L_P_Heel  - Left heel pressure
  A1: L_P_Ball  - Left ball pressure
  A2: L_S_Knee  - Left knee stretch
  A3: R_P_Heel  - Right heel pressure
  A4: R_P_Ball  - Right ball pressure
  A5: R_S_Knee  - Right knee stretch

              ↓ Serial / WiFi / BLE ↓

         Python collector.py (reads 6-column CSV)
                      ↓
    CSV: time_ms,L_P_Heel,L_P_Ball,L_S_Knee,R_P_Heel,R_P_Ball,R_S_Knee
                      ↓
    data_preprocessing.py → feature_extraction.py → train_model.py
                      ↓
              Random Forest (.joblib)
                      ↓
            real_time_classifier.py
```

- **Per leg:** 2 piezoresistive pressure sensors (sock) + 1 stretch sensor (knee pad)
- **Circuit:** Voltage dividers with 10k resistors, 12-bit ADC (0-4095)
- **Sampling:** 50 Hz
- **Communication:** Serial/USB, WiFi (AP/Station/Hotspot), BLE

---

## Folder Structure

```
Smart Socks/
├── 00_Planning/           Project plans, timeline, meeting notes
├── 01_Design/             Sensor placement, circuit diagrams
├── 02_Fabrication/        Prototype photos, build documentation
├── 03_Data/               Raw and processed sensor data
├── 04_Code/
│   ├── arduino/
│   │   ├── data_collection_leg/       Data collection firmware (WiFi+BLE+serial)
│   │   ├── calibration_all_sensors/   All 6 sensors on one ESP32
│   │   ├── ei_data_forwarder/         Edge Impulse data collection
│   │   └── ei_led_feedback/           LED feedback demo
│   ├── python/
│   │   ├── config.py                  Centralized configuration
│   │   ├── calibration_visualizer.py  Real-time sensor visualization
│   │   ├── collector.py                Data collection tool
│   │   ├── data_preprocessing.py      Data cleaning
│   │   ├── feature_extraction.py      ML feature extraction
│   │   ├── train_model.py             Random Forest training
│   │   ├── real_time_classifier.py    Live activity classification
│   │   ├── run_full_pipeline.py       End-to-end ML automation
│   │   └── ...
│   ├── QUICKSTART.md                Quick start for single ESP32
│   └── WIFI_CONFIGURATION.md         WiFi/BLE/Hotspot setup
├── 05_Analysis/           ML results, confusion matrices
├── 06_Presentation/       Poster, slides, user testing materials
├── 07_References/         Papers, datasheets (see REFERENCES.md)
├── PLATFORMIO_SETUP.md    PlatformIO + VS Code setup
├── README_PYTHON_SETUP.md Python/UV environment setup
├── TROUBLESHOOTING.md     Common issues and fixes
├── PROJECT_STATUS.md      Current project status
└── WORK_DIARY.md          Team meeting notes and progress
```

---

## Development Commands

### Build & Upload Firmware

```bash
# Data collection firmware (WiFi + BLE + serial)
pio run -e xiao_esp32s3 -t upload

# Calibration firmware (simple serial-only)
pio run -e calibration -t upload

# Serial monitor (115200 baud)
pio device monitor -e xiao_esp32s3
```

Serial port on macOS: `/dev/cu.usbmodem2101` (find yours with `pio device list`).

### Data Collection

```bash
cd 04_Code/python

# Record activity data
python collector.py --activity walking_forward --port /dev/cu.usbmodem2101

# Calibration visualization
python calibration_visualizer.py --port /dev/cu.usbmodem2101
# Controls: Q=quit, R=reset, S=save CSV, P=pause, C=record GIF
```

### ML Pipeline

```bash
cd 04_Code/python

# Full pipeline (recommended)
python run_full_pipeline.py --raw-data ../../03_Data/raw/ --output ../../05_Analysis/

# Step-by-step
python data_preprocessing.py --input ../../03_Data/raw/ --output ../../03_Data/processed/
python feature_extraction.py --input ../../03_Data/processed/ --output ../../03_Data/features/
python train_model.py --features ../../03_Data/features/features_all.csv --output ../../05_Analysis/
python analysis_report.py --results-dir ../../05_Analysis/ --output ../../06_Presentation/report/
```

### Real-Time Demo

```bash
cd 04_Code/python

# Serial mode
python real_time_classifier.py --model ../../05_Analysis/smart_socks_model.joblib --port /dev/cu.usbmodem2101

# BLE mode
python real_time_classifier.py --model ../../05_Analysis/smart_socks_model.joblib --ble
```

### Tests & Linting

```bash
cd 04_Code/python
python -m pytest tests/ -v
uv run black . && uv run flake8 . && uv run mypy .
```

---

## Data Format & Conventions

**CSV columns (merged):** `time_ms,L_P_Heel,L_P_Ball,L_S_Knee,R_P_Heel,R_P_Ball,R_S_Knee`

**File naming:** `<subject_id>_<activity>_<timestamp>.csv` (e.g., `S01_walking_forward_20260115_143022.csv`)

**Activity labels:** `walking_forward`, `walking_backward`, `stairs_up`, `stairs_down`, `sitting_floor`, `sitting_crossed`, `sit_to_stand`, `stand_to_sit`, `standing_upright`, `standing_lean_left`, `standing_lean_right`

**Subject split:** S01-S06 training, S07-S09 testing (cross-subject validation)

**Serial protocol (115200 baud):**
```
START / S      # Start recording
STOP / X       # Stop recording
CAL ON/OFF     # Calibration mode
STATUS         # Check status
HELP / ?       # Show commands
```

**BLE:** Service `4fafc201-...914b`, Characteristic `beb5483e-...26a8`. Device: `SmartSocks`.

**Target accuracy:** >85% average, >80% per activity on held-out test subjects.

---

## Change Log

### Jan 30, 2026: Single-ESP32 Firmware Unification

- **Unified firmware:** Single `data_collection_leg.ino` reads all 6 sensors (A0-A5) on one ESP32
- Removed dual-ESP32 sync system (UDP, TRIGGER/MASTER/SLAVE commands)
- Removed LEG_ID build flag system and conditional compilation
- Replaced `dual_collector.py` with `collector.py` (single-port data collection)
- Simplified `platformio.ini` to 2 environments (`xiao_esp32s3`, `calibration`)
- Web dashboard shows all 6 sensors in 2×3 grid
- Updated all documentation for single-ESP32 architecture
- Added `QUICKSTART.md`, removed `DUAL_ESP32_QUICKSTART.md`

### Jan 29-30, 2026: Sensor Migration + Audit

- **Migrated from 10-sensor to 6-sensor design** (2 pressure + 1 stretch per leg)
- Fixed 25 audit issues across Python, Arduino, docs, and build system (see [[AUDIT_GAPS_AND_FIXES]])
- Consolidated documentation: removed redundant files, merged wireless guides into [[WIFI_CONFIGURATION]]
- Removed deprecated v1 10-sensor code and designs
- Restored Obsidian wiki-links throughout documentation
- Updated SVG diagrams to match 6-sensor configuration
- All sensor names standardized: `L_P_Heel`, `L_P_Ball`, `L_S_Knee`, `R_P_Heel`, `R_P_Ball`, `R_S_Knee`
- Single ESP32 reads all 6 sensors (A0-A5)
- GIF recording in calibration_visualizer.py fully implemented

---

## Deliverables Checklist

### Mid-term Review (Week 7)
- [x] Sensor fabrication code
- [x] Data collection software
- [x] BLE transmission capability
- [ ] Calibration curves (need sensor data)
- [ ] Live demo (need hardware)

### Final Review (Week 15)
- [x] ML pipeline (feature extraction, training, evaluation)
- [x] Real-time classification
- [x] Cross-subject validation framework
- [x] User testing materials (WEAR, SUS questionnaires)
- [x] Analysis report generator
- [ ] Trained model with >85% accuracy (need data)
- [ ] User study results (5+ participants)

---

## Contacts

- **Saara** -- ML, sensors, documentation
- **Alex** -- Prototyping, user testing, design
- **Jing** -- Circuit, ESP32, coordination

---

*Last updated: 2026-01-30*
