# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Smart Socks for Physical Activity Recognition - an academic project for ELEC-E7840 Smart Wearables (Aalto University). The goal is to recognize 5 activity categories (walking, stair climbing, sitting, sit-to-stand, standing) using textile-based pressure sensors integrated into socks.

**Constraint:** Textile-based sensors only (pressure, bend, strain). No IMUs permitted.

## Technology Stack

- **Embedded firmware:** Arduino/C for ESP32S3 XIAO microcontroller
- **Data processing & ML:** Python with scikit-learn (Random Forest classifier)
- **Sensors:** Piezoresistive fabric sensors (5 zones per sock, 10 total channels)
- **Communication:** Serial/BLE from ESP32 to PC

## Hardware Architecture

```
Piezoresistive fabric sensors (5 per sock)
    → Voltage divider circuit (10kΩ resistors)
    → ESP32S3 ADC (50+ Hz sampling)
    → Serial/BLE
    → Python receiver (PC)
    → ML classification
```

**Sensor zones per sock:** Heel, Arch, Metatarsal medial, Metatarsal lateral, Toe

## Directory Structure

```
00_Planning/       - Project plans, meeting notes
01_Design/         - Sensor layouts, circuit diagrams
02_Fabrication/    - Prototype photos, build docs
03_Data/           - Sensor characterization, activity data (see README.md for naming)
04_Code/
  ├── arduino/
  │   ├── sensor_test/       - Basic ADC reading for characterization
  │   └── data_collection/   - Multi-channel recording with serial commands
  └── python/
      ├── requirements.txt
      ├── serial_receiver.py          - Save serial data to CSV
      └── sensor_characterization.py  - Calibration curve analysis
05_Analysis/       - ML results, plots, confusion matrices
06_Presentation/   - Slides, final report
07_References/     - Research papers
```

## Development Commands

**Arduino (ESP32S3):**
```bash
# Compile and upload via Arduino IDE or arduino-cli
arduino-cli compile --fqbn esp32:esp32:XIAO_ESP32S3 04_Code/arduino/sensor_test/
arduino-cli upload -p /dev/ttyUSB0 --fqbn esp32:esp32:XIAO_ESP32S3 04_Code/arduino/sensor_test/
```

**Python:**
```bash
pip install -r 04_Code/python/requirements.txt
python 04_Code/python/serial_receiver.py --port /dev/ttyUSB0
python 04_Code/python/sensor_characterization.py --data 03_Data/calibration/
```

**Arduino Serial Commands (data_collection sketch):**
```
START S01 walking_forward   # Start recording for subject S01
STOP                        # Stop recording
STATUS                      # Check current status
HELP                        # Show available commands
```

**Activity Labels:** `walking_forward`, `walking_backward`, `stairs_up`, `stairs_down`, `sitting_floor`, `sitting_crossed`, `sit_to_stand`, `stand_to_sit`, `standing_upright`, `standing_lean_left`, `standing_lean_right`

## Key Technical Details

- **ADC sampling:** 50+ Hz across all 10 sensor channels
- **Sensor characterization:** Test with known weights (100g-5kg), record ADC values, plot pressure vs. ADC curves
- **Feature extraction:** Time-domain statistics, pressure ratios, temporal patterns
- **Step counting:** Peak detection algorithm running in parallel with classification
- **Data split:** 6 subjects for training, 3 for testing (leave-subject-out validation)

## Activity Recognition Requirements

| Activity | Sub-tasks |
|----------|-----------|
| Walking | Forward/backward detection + step counting |
| Stair climbing | Up/down detection + step counting |
| Sitting | Feet on floor vs. cross-legged |
| Sit-to-stand | Detection + timing (seconds) |
| Standing | Upright vs. leaning left/right |
