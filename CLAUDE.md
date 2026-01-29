# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Smart Socks for Physical Activity Recognition — ELEC-E7840 Smart Wearables (Aalto University). Recognizes 5 activity categories (walking, stair climbing, sitting, sit-to-stand, standing) using textile-based pressure sensors in socks. **No IMUs permitted** — textile sensors only.

**Team:** Saara (ML, sensors, docs), Alex (Prototyping, user testing, design), Jing (Circuit, ESP32, coordination)

## Architecture

```
Piezoresistive fabric sensors (5 per sock, 10 total)
    → Voltage divider (10kΩ resistors)
    → ESP32S3 XIAO ADC (50 Hz, 12-bit)
    → Serial or BLE
    → Python receiver (PC)
    → ML classification (Random Forest)
```

**Sensor zones per sock:** Heel, Arch, Metatarsal medial, Metatarsal lateral, Toe

**Data flow:** Raw CSV → `data_preprocessing.py` → `feature_extraction.py` (200+ features, 1s windows, 50% overlap) → `train_model.py` (Random Forest, leave-subject-out validation) → `.joblib` model → `real_time_classifier.py`

**Centralized config:** All hardware constants, sensor mappings, ML parameters, feature toggles, and path conventions live in `04_Code/python/config.py`. Modify config values there rather than in individual scripts.

## Development Commands

### Python Setup & Tests

```bash
pip install -r 04_Code/python/requirements.txt

# Run tests
cd 04_Code/python && python -m pytest tests/ -v

# Run a single test
cd 04_Code/python && python -m pytest tests/test_data_validation.py -v

# Linting and formatting
cd 04_Code/python && black . && flake8 . && mypy .
```

### Arduino / PlatformIO

PlatformIO with VS Code is the recommended dev environment (see `04_Code/PLATFORMIO_SETUP.md`). Config is in `platformio.ini` at repo root.

```bash
# Alternative: arduino-cli
arduino-cli compile --fqbn esp32:esp32:XIAO_ESP32S3 04_Code/arduino/sensor_test/
arduino-cli upload -p /dev/cu.usbmodem2101 --fqbn esp32:esp32:XIAO_ESP32S3 04_Code/arduino/sensor_test/
```

**Note:** Serial port is `/dev/cu.usbmodem2101` on macOS (not `/dev/ttyUSB0`).

### ML Pipeline

```bash
# Full pipeline (recommended)
python 04_Code/python/run_full_pipeline.py --raw-data ../../03_Data/raw/ --output ../../05_Analysis/

# Step-by-step: preprocess → extract features → train → report
python 04_Code/python/data_preprocessing.py --input ../../03_Data/raw/ --output ../../03_Data/processed/
python 04_Code/python/feature_extraction.py --input ../../03_Data/processed/ --output ../../03_Data/features/
python 04_Code/python/train_model.py --features ../../03_Data/features/features_all.csv --output ../../05_Analysis/
python 04_Code/python/train_model.py --features ../../03_Data/features/features_all.csv --output ../../05_Analysis/ --cross-subject
python 04_Code/python/analysis_report.py --results-dir ../../05_Analysis/ --output ../../06_Presentation/report/
```

### Real-Time Demo

```bash
python 04_Code/python/real_time_classifier.py --model ../../05_Analysis/smart_socks_model.joblib --port /dev/cu.usbmodem2101
python 04_Code/python/real_time_classifier.py --model ../../05_Analysis/smart_socks_model.joblib --ble
```

## Arduino Serial Protocol

115200 baud. Commands: `START <subject_id> <activity>`, `STOP`, `STATUS`, `HELP`. BLE version adds: `MODE SERIAL|BLE|BOTH`.

## Key Conventions

- **Activity labels:** `walking_forward`, `walking_backward`, `stairs_up`, `stairs_down`, `sitting_floor`, `sitting_crossed`, `sit_to_stand`, `stand_to_sit`, `standing_upright`, `standing_lean_left`, `standing_lean_right`
- **Data naming:** `<subject_id>_<activity>_<timestamp>.csv` (e.g., `S01_walking_forward_20260115_143022.csv`)
- **Subject split:** S01-S06 training, S07-S09 testing (cross-subject validation is critical)
- **CSV columns:** `time_ms,L_Heel,L_Arch,L_MetaM,L_MetaL,L_Toe,R_Heel,R_Arch,R_MetaM,R_MetaL,R_Toe`
- **BLE UUIDs:** Service `4fafc201-1fb5-459e-8fcc-c5c9c331914b`, Characteristic `beb5483e-36e1-4688-b7f5-ea07361b26a8`, Device name `SmartSocks`
- **Arduino LED:** XIAO ESP32S3 uses GPIO 21 (`#define LED_BUILTIN 21`)
- **Git:** Local only, no remote. `.gitignore` excludes CSV data, Python cache, IDE settings.
- **Python path:** Tests use `sys.path.insert` to add parent dir; run pytest from `04_Code/python/`.

## Target Accuracy

>85% average, >80% per activity on held-out test subjects. Key discriminating features: total pressure per foot, fore/hindfoot ratio, left/right balance, temporal gait patterns.
