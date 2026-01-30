# Smart Socks - Documentation Index

**ELEC-E7840 Smart Wearables - Aalto University**

This index helps you find the right documentation for each task.

---

## Getting Started

| Task | Document |
|------|----------|
| First time setup | [README.md](README.md) |
| Install PlatformIO & VS Code | [SOFTWARE_INSTALLATION.md](SOFTWARE_INSTALLATION.md) |
| Fix Arduino IDE issues | [ARDUINO_ESP32_INSTALLATION_FAQ.md](ARDUINO_ESP32_INSTALLATION_FAQ.md) |
| Build/upload firmware | [PLATFORMIO_SETUP.md](PLATFORMIO_SETUP.md) |
| Python environment | [README_PYTHON_SETUP.md](README_PYTHON_SETUP.md) |

---

## Hardware & Design

| Topic | Document |
|-------|----------|
| Circuit design (current) | [01_Design/circuit_diagram_v2.md](01_Design/circuit_diagram_v2.md) |
| Circuit design (old - deprecated) | [01_Design/circuit_diagram.md](01_Design/circuit_diagram.md) |
| Sensor placement (current) | [01_Design/sensor_placement_v2.md](01_Design/sensor_placement_v2.md) |
| Sensor placement (old - deprecated) | [01_Design/sensor_placement.md](01_Design/sensor_placement.md) |
| LED display options | [01_Design/LED_DISPLAY_RESEARCH.md](01_Design/LED_DISPLAY_RESEARCH.md) |
| Design system/assets | [DESIGN_ASSETS.md](DESIGN_ASSETS.md) |

---

## Firmware & Software

| Task | Document |
|------|----------|
| PlatformIO commands | [PLATFORMIO_SETUP.md](PLATFORMIO_SETUP.md) |
| Python code reference | [04_Code/python/](04_Code/python/) |
| Arduino sketches reference | [04_Code/arduino/](04_Code/arduino/) |
| Firmware architecture | [CLAUDE.md](CLAUDE.md) |

---

## Data Collection & ML Pipeline

| Task | Document |
|------|----------|
| Data collection workflow | [AGENTS.md](AGENTS.md) → Data Collection Protocol section |
| Activity labels | [AGENTS.md](AGENTS.md) → Activity Labels section |
| Feature extraction | [04_Code/python/feature_extraction.py](04_Code/python/feature_extraction.py) |
| Training model | [04_Code/python/train_model.py](04_Code/python/train_model.py) |
| Real-time classification | [04_Code/python/real_time_classifier.py](04_Code/python/real_time_classifier.py) |

---

## Project Status & Planning

| Topic | Document |
|-------|----------|
| Current project status | [PROJECT_STATUS.md](PROJECT_STATUS.md) |
| Meeting notes & diary | [WORK_DIARY.md](WORK_DIARY.md) |
| Project index (Obsidian) | [INDEX.md](INDEX.md) |

---

## Troubleshooting

| Issue | Document |
|-------|----------|
| Build/upload errors | [PLATFORMIO_SETUP.md](PLATFORMIO_SETUP.md) → Troubleshooting |
| ESP32 not detected | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |
| Serial port issues | [PLATFORMIO_SETUP.md](PLATFORMIO_SETUP.md) → Troubleshooting |
| Arduino IDE problems | [ARDUINO_ESP32_INSTALLATION_FAQ.md](ARDUINO_ESP32_INSTALLATION_FAQ.md) |

---

## For AI Assistants

| Purpose | Document |
|---------|----------|
| Coding guidelines | [AGENTS.md](AGENTS.md) |
| Claude-specific guidance | [CLAUDE.md](CLAUDE.md) |
| Project structure | [AGENTS.md](AGENTS.md) → Project Structure |

---

## Recent Changes (January 30, 2026)

### Major Refactor
See [PROJECT_REFACTOR_SUMMARY.md](PROJECT_REFACTOR_SUMMARY.md) for details on:
- Simplified firmware (single environment)
- Fixed Python hardcoding issues
- Updated documentation

### Key Files Changed
- `platformio.ini` - Single environment for all ESP32s
- `src/main.cpp` - Unified firmware
- `AGENTS.md` - Complete rewrite for 6-sensor design
- `CLAUDE.md` - Updated architecture

---

## Quick Reference

### Build Firmware
```bash
# After adding PlatformIO to PATH (see PLATFORMIO_SETUP.md)
platformio run --environment xiao_esp32s3

# Or use VS Code PlatformIO plugin
```

### Data Collection
```bash
# Activate Python environment
source .venv/bin/activate

# Calibrate sensors
python 04_Code/python/calibration_visualizer.py --port /dev/cu.usbmodem2101

# Collect data (single ESP32 with all 6 sensors)
python 04_Code/python/serial_receiver.py --port /dev/cu.usbmodem2101

# Collect data (two ESP32s - one per leg)
python 04_Code/python/dual_collector.py --left /dev/cu.usbmodem2101 --right /dev/cu.usbmodem2102
```

### ML Pipeline
```bash
# Full pipeline
python 04_Code/python/run_full_pipeline.py --raw-data ../../03_Data/raw/ --output ../../05_Analysis/

# Or step by step
python 04_Code/python/data_preprocessing.py --input ../../03_Data/raw/ --output ../../03_Data/processed/
python 04_Code/python/feature_extraction.py --input ../../03_Data/processed/ --output ../../03_Data/features/
python 04_Code/python/train_model.py --features ../../03_Data/features/features_all.csv --output ../../05_Analysis/
```

---

## Course Structure

| Part | Focus | Duration | Team |
|------|-------|----------|------|
| **Part 1** | Hardware & Sensor Characterization (**NO ML**) | Weeks 1-7 | Saara, Alex, Jing |
| **Part 2** | Machine Learning & Classification | Weeks 8-15 | Jing only |
| **Part 3** | Edge ML / TinyML Extension | Personal | Jing only |

---

**Last Updated:** January 30, 2026
