# Smart Socks Project

**ELEC-E7840 Smart Wearables — Topic 3**

Team: Saara, Alex, Jing

---

> **🎯 COURSE STRUCTURE: 3 Parts**
> 
> **ELEC-E7840 Smart Wearables** has 3 sequential parts:
> 
> | Part | Focus | Duration | Team |
> |------|-------|----------|------|
> | **Part 1** | Hardware & Sensor Characterization (**NO ML**) | Weeks 1-7 | Saara, Alex, Jing |
> | **Part 2** | Machine Learning & Classification | Weeks 8-15 | Jing only |
> | **Part 3** | Edge ML / TinyML Extension | Personal | Jing only |
> 
> **Current Focus:** Part 1 - Sensor fabrication, circuit design, calibration
> 
> See [[PROJECT_TIMELINE]] for week-by-week schedule.
> 
> ---
> 
> > **⚠️ WORKSHOP PREPARATION (Wed 04-02)**
> > 
> > **Bring to workshop:** USB-C cable, microcontrollers, breadboard, jumper wires, resistors, sensors
> > 
> > **Install before class:**
> > - Python: https://realpython.com/installing-python/ | Video: https://www.youtube.com/watch?v=QhukcScB9W0
> > - IDE: [[Visual Studio Code]] (recommended) or PyCharm
> > - We'll learn WiFi data collection using Arduino IDE/VS Code + Python
> > 
> > See [[PLATFORMIO_SETUP]] for detailed IDE setup instructions.

---

> **Obsidian Links:** [[INDEX]] | [[CODE_REVIEW]] | [[PLATFORMIO_SETUP]] | [[Calibration Visualizer|calibration_visualizer]]
> 
> This project uses [[Obsidian]]-style wiki links for cross-referencing. Open in Obsidian for best experience. Start with [[INDEX]] for navigation.

---

## Folder Structure

```
Smart Socks/
├── 00_Planning/          ← Project plans, meeting notes, timeline
├── 01_Design/            ← Sensor layouts, sock sketches, circuit diagrams
├── 02_Fabrication/       ← Photos of prototypes, build documentation
├── 03_Data/              ← Sensor characterization, collected activity data
├── 04_Code/              ← Arduino sketches, Python scripts
├── 05_Analysis/          ← ML results, plots, confusion matrices
├── 06_Presentation/      ← Slides, final report, user testing materials
├── 07_References/        ← Papers from reading list
├── WORK_DIARY.md         ← Team meeting notes and progress
├── PROJECT_STATUS.md     ← Current project status and recap
└── INDEX.md              ← Documentation navigation hub
```

---

## Quick Links

| Resource | Location | Obsidian Link |
|----------|----------|---------------|
| **Project Status** | **PROJECT_STATUS.md** | [[PROJECT_STATUS]] |
| **Work Diary** | **WORK_DIARY.md** | [[WORK_DIARY]] |
| Course page | MyCourses | — |
| Assignment PDF | 00_Planning/ | — |
| Project Timeline | 00_Planning/PROJECT_TIMELINE.md | [[PROJECT_TIMELINE]] |
| **PlatformIO Setup** | **04_Code/PLATFORMIO_SETUP.md** | [[PLATFORMIO_SETUP]] |
| **Python Setup** | **README_PYTHON_SETUP.md** | [[README_PYTHON_SETUP]] |
| Code Review Report | CODE_REVIEW.md | [[CODE_REVIEW]] |
| BLE Arduino Code | 04_Code/arduino/data_collection_ble/ | — |
| Calibration Visualizer | 04_Code/python/calibration_visualizer.py | [[calibration_visualizer]] |

---

## Working with Claude

Jing has a Claude session tracking this project. To get Claude's help:

1. **Upload the relevant file(s)** to the chat
2. **Give brief context** ("this is our latest sensor data" or "current circuit diagram")
3. **Ask your question**

Claude can help with: code, data analysis, document drafts, troubleshooting, ML pipeline.

See [[PROJECT_STATUS]] for complete project recap and setup history.

---

## Status

| Phase | Status | Notes |
|-------|--------|-------|
| 1. Sensor characterization | ✅ Ready | PlatformIO + Calibration visualizer + Web dashboard |
| 2. Prototype design | 🟡 In Progress | Sensor placement designed |
| 3. Data collection | ✅ Ready | WiFi+BLE+Serial pipeline, calibration tools ready |
| 4. ML & integration | ✅ Ready | Full pipeline, all code review issues fixed |
| 5. Testing & final | ⚪ Not started | Materials prepared |

---

## Technical Reference

### Hardware Setup (Updated Jan 29, 2026)
- **MCU:** ESP32S3 XIAO (Seeed Studio)
- **Sensors per leg:**
  - **Sock:** 2 piezoresistive pressure sensors (heel + ball of foot)
  - **Knee pad:** 1 stretch sensor (front of knee)
- **Total:** 6 sensors (4 pressure + 2 stretch)
- **Circuit:** Voltage dividers with 10kΩ resistors
- **Sampling:** 50 Hz, 12-bit ADC (0-4095)
- **Port:** `/dev/cu.usbmodem2101` (default). Use `pio device list` to find yours

### Development Environment

**PlatformIO + VS Code** (Recommended)

Full setup guide: [[PLATFORMIO_SETUP]] or [04_Code/PLATFORMIO_SETUP.md](04_Code/PLATFORMIO_SETUP.md)

Quick commands in VS Code:
| Action | Button | Shortcut |
|--------|--------|----------|
| Build | ✓ (checkmark) | PlatformIO: Build |
| Upload | → (arrow) | PlatformIO: Upload |
| Serial Monitor | 🖥️ (terminal) | PlatformIO: Serial Monitor |

**Arduino CLI** (Alternative)
```bash
# Compile and upload sensor test
arduino-cli compile --fqbn esp32:esp32:XIAO_ESP32S3 04_Code/arduino/sensor_test/
arduino-cli upload -p /dev/cu.usbmodem2101 --fqbn esp32:esp32:XIAO_ESP32S3 04_Code/arduino/sensor_test/
# Replace /dev/cu.usbmodem2101 with your port (find with: pio device list)
```

### Code Structure
```
04_Code/
├── arduino/
│   ├── data_collection_leg/         # 6-sensor dual ESP32 (recommended)
│   ├── calibration_all_sensors/     # All 6 sensors on one ESP32 for calibration
│   ├── ei_data_forwarder/           # Edge Impulse data collection (Part 2)
│   ├── ei_led_feedback/             # LED feedback demo (Part 2)
│   └── deprecated_10_sensor/        # OLD 10-sensor sketches (deprecated)
└── python/
    ├── requirements.txt
    ├── config.py                    # Centralized configuration (6 sensors)
    ├── feature_utils.py             # Shared feature extraction
    ├── calibration_visualizer.py    # Real-time calibration visualization ⭐
    ├── dual_collector.py            # Collect from 2 ESP32s simultaneously
    ├── serial_receiver.py           # Save serial data to CSV
    ├── sensor_characterization.py   # Calibration curve analysis
    ├── data_preprocessing.py        # Data cleaning and normalization
    ├── feature_extraction.py        # Extract ML features from raw data
    ├── train_model.py               # Train Random Forest classifier
    ├── real_time_classifier.py      # Real-time activity classification
    ├── analysis_report.py           # Generate evaluation reports
    ├── visualize_data.py            # Data visualization tools
    ├── quick_test.py                # Hardware/software sanity checks
    └── run_full_pipeline.py         # Complete ML pipeline automation
```

**Recommended for calibration:** `calibration_visualizer.py` with `data_collection_wireless.ino`

---

## 🧠 Edge Impulse / TinyML (Part 2 Extension)

> **⚠️ NOTE:** Edge Impulse / TinyML is **Part 3** (extension) for Jing only.
> Saara and Alex are only taking Part 1 (no ML), so Part 2 and Part 3 are NOT required for them.

Based on analysis of XIAO Big Power Small Board Chapter 4, Smart Socks is an ideal candidate for Edge Impulse Studio conversion.

### Why Edge Impulse? (Future Work)
| Feature | Benefit |
|---------|---------|
| **Real-time inference** | 5-10ms latency on ESP32 |
| **Standalone operation** | No PC needed for classification |
| **Sensor fusion** | Optimized for multiple analog inputs |
| **One-click deploy** | Arduino library auto-generation |
| **Tiny model size** | ~20KB quantized models |

### Documentation (For Reference)
- [[EDGE_IMPULSE_ANALYSIS]] - Feasibility study
- [[EDGE_IMPULSE_QUICKSTART]] - Deployment guide

### Expected Performance
- **Inference latency:** 5-10ms
- **Model size:** 15-30KB
- **Accuracy:** 90-95% (4-6 activity classes)

### Installation

```bash
# Install Python dependencies
cd 04_Code/python/
pip install -r requirements.txt

# Run quick test to verify setup
python quick_test.py --port /dev/cu.usbmodem2101
# Replace with your port (find with: pio device list)
```

### Serial Commands (Data Collection Mode)

Once connected via serial monitor (115200 baud):
```
START S01 walking_forward   # Start recording
STOP                        # Stop recording
STATUS                      # Check status
MODE SERIAL                 # Output to serial only
MODE BLE                    # Output via BLE only
MODE BOTH                   # Output to both (default)
HELP                        # Show available commands
```

### Sensor Test Output

Raw ADC values from 6 sensors (CSV format):
```
time_ms,L_P_Heel,L_P_Ball,L_S_Knee,R_P_Heel,R_P_Ball,R_S_Knee
181556,712,694,1203,720,820,1156
181576,703,699,1198,729,821,1160
```

### Data Collection Workflow

```bash
# 1. Collect raw data
python serial_receiver.py --port /dev/cu.usbmodem2101 --output ../../03_Data/raw/

# 2. Preprocess data
python data_preprocessing.py --input ../../03_Data/raw/ --output ../../03_Data/processed/

# 3. Extract features
python feature_extraction.py --input ../../03_Data/processed/ --output ../../03_Data/features/

# 4. Train model (with cross-subject validation)
python train_model.py --features ../../03_Data/features/features_all.csv --output ../../05_Analysis/
python train_model.py --features ../../03_Data/features/features_all.csv --output ../../05_Analysis/ --cross-subject

# 5. Generate report
python analysis_report.py --results-dir ../../05_Analysis/ --output ../../06_Presentation/report/

# Or run full pipeline at once:
python run_full_pipeline.py --raw-data ../../03_Data/raw/ --output ../../05_Analysis/
```

### Real-Time Classification Demo

```bash
# Serial mode
python real_time_classifier.py --model ../../05_Analysis/smart_socks_model.joblib --port /dev/cu.usbmodem2101

# BLE mode (requires bleak package)
python real_time_classifier.py --model ../../05_Analysis/smart_socks_model.joblib --ble
```

### Real-Time Calibration Visualizer

```bash
# Connect ESP32 and visualize all 6 sensors in real-time
python calibration_visualizer.py --port /dev/cu.usbmodem2101
# Replace with your port (find with: pio device list)

# Controls:
#   Q - Quit
#   R - Reset min/max tracking
#   S - Save calibration data to CSV
#   P - Pause/Resume
```

### Wireless Data Collection (Web Dashboard)

```bash
# 1. Upload data_collection_wireless.ino to ESP32
# 2. Connect to WiFi 'SmartSocks' / 'smartwearables'
# 3. Open browser: http://192.168.4.1
# 4. View real-time sensor dashboard, record data, download CSV
```

### Data Visualization

```bash
# Plot time series
python visualize_data.py --file ../../03_Data/raw/S01_walking_forward_*.csv --plot-type timeseries

# Generate all plots
python visualize_data.py --file ../../03_Data/raw/S01_walking_forward_*.csv --plot-type all --output ./plots/

# Compare activities
python visualize_data.py --dir ../../03_Data/raw/ --compare --output ./plots/
```

### Data Naming Convention
Format: `<subject_id>_<activity>_<timestamp>.csv`

Activities: `walking_forward`, `walking_backward`, `stairs_up`, `stairs_down`, `sitting_floor`, `sitting_crossed`, `sit_to_stand`, `stand_to_sit`, `standing_upright`, `standing_lean_left`, `standing_lean_right`

### BLE Configuration
- **Device Name:** SmartSocks
- **Service UUID:** 4fafc201-1fb5-459e-8fcc-c5c9c331914b
- **Characteristic UUID:** beb5483e-36e1-4688-b7f5-ea07361b26a8

### Git
- Local only (no remote)
- `.gitignore` excludes `.csv` data files, Python cache, IDE settings

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

- **Saara** — ML, sensors, documentation
- **Alex** — Prototyping, user testing, design
- **Jing** — Circuit, ESP32, coordination

---

---

## Knowledge Graph

Key concepts in this project:
- [[Hardware]]: [[ESP32-S3]], [[XIAO]], [[ADC]], [[Piezoresistive Sensors]], [[Voltage Divider]]
- [[Software]]: [[PlatformIO]], [[Arduino]], [[Python]], [[BLE]], [[WiFi]], [[Serial]]
- [[ML Pipeline]]: [[Feature Extraction]], [[Random Forest]], [[Classification]], [[Calibration]]
- [[Data]]: [[Sensor Characterization]], [[Windowing]], [[CSV]], [[JSON]]

---

*Last updated: 2026-01-29 — All code review issues fixed, calibration tools ready*
