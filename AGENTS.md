# AGENTS.md - Smart Socks Project

This file provides guidance to AI coding agents working with the Smart Socks codebase.

## Project Overview

**Smart Socks for Physical Activity Recognition** - An academic project for ELEC-E7840 Smart Wearables course at Aalto University.

The goal is to recognize 5 activity categories using textile-based pressure sensors integrated into socks:
- Walking (forward/backward) with step counting
- Stair climbing (up/down) with step counting
- Sitting (feet on floor / cross-legged)
- Sit-to-stand transitions (with timing)
- Standing (upright / leaning left/right)

**Key Constraint:** Textile-based sensors only (pressure, bend, strain). No IMUs permitted.

**Team:** Saara (ML, sensors, documentation), Alex (Prototyping, user testing, design), Jing (Circuit, ESP32, coordination)

---

## Technology Stack

### Hardware
- **MCU:** ESP32S3 XIAO (Seeed Studio)
- **Sensors:** 10 piezoresistive fabric sensors (EeonTex piezoresistive fabric)
- **Zones per sock:** Heel, Arch, Metatarsal medial, Metatarsal lateral, Toe
- **Circuit:** Voltage dividers with 10kΩ reference resistors
- **ADC:** 12-bit resolution (0-4095 range)
- **Sampling Rate:** 50 Hz

### Software
- **Embedded Firmware:** Arduino/C++ for ESP32S3
- **Data Processing & ML:** Python 3 with scikit-learn (Random Forest classifier)
- **Communication:** Serial (USB) / BLE from ESP32 to PC
- **Data Format:** CSV files with timestamp and 10 sensor channels

### Python Dependencies
See `04_Code/python/requirements.txt`:
- `numpy>=1.21.0` - Numerical operations
- `pandas>=1.3.0` - Data handling
- `scikit-learn>=1.0.0` - Machine learning
- `matplotlib>=3.4.0` - Plotting
- `seaborn>=0.11.0` - Visualization
- `pyserial>=3.5` - Serial communication
- `scipy>=1.7.0` - Signal processing

---

## Project Structure

```
Smart Socks/
├── 00_Planning/          # Project plans, meeting notes, assignment PDF
├── 01_Design/            # Sensor layouts, sock sketches, circuit diagrams
├── 02_Fabrication/       # Photos of prototypes, build documentation
├── 03_Data/              # Sensor characterization, collected activity data
│   ├── calibration/      # Known weight tests (0g, 100g, 200g, etc.)
│   ├── raw/              # Raw recordings by subject (S01/, S02/, etc.)
│   ├── processed/        # Preprocessed/segmented data
│   └── features/         # Extracted features for ML
├── 04_Code/
│   ├── arduino/
│   │   ├── sensor_test/       # Basic ADC reading for characterization
│   │   │   └── sensor_test.ino
│   │   └── data_collection/   # Multi-channel recording with serial commands
│   │       └── data_collection.ino
│   └── python/
│       ├── requirements.txt
│       ├── serial_receiver.py         # Save serial data to CSV
│       └── sensor_characterization.py # Calibration curve analysis
├── 05_Analysis/          # ML results, plots, confusion matrices
├── 06_Presentation/      # Slides, final report
├── 07_References/        # Research papers from reading list
├── Work_Diary.docx       # Required deliverable - project documentation
├── README.md             # Human-readable project overview
├── CLAUDE.md             # Original Claude-specific guidance
└── AGENTS.md             # This file
```

---

## Build and Development Commands

### Python Environment Setup

```bash
# Install dependencies
cd 04_Code/python
pip install -r requirements.txt
```

### Running Python Scripts

```bash
# Serial data receiver - records data from ESP32 to CSV
cd 04_Code/python
python serial_receiver.py --port /dev/ttyUSB0 --output ../../03_Data/

# Sensor characterization - analyzes calibration data
cd 04_Code/python
python sensor_characterization.py --data ../../03_Data/calibration/
```

### Arduino (ESP32S3)

```bash
# Compile and upload via arduino-cli
arduino-cli compile --fqbn esp32:esp32:XIAO_ESP32S3 04_Code/arduino/sensor_test/
arduino-cli upload -p /dev/ttyUSB0 --fqbn esp32:esp32:XIAO_ESP32S3 04_Code/arduino/sensor_test/

# Or use Arduino IDE with XIAO_ESP32S3 board selected
```

---

## Arduino Serial Protocol

The `data_collection.ino` sketch accepts these commands via serial (115200 baud):

```
START <subject_id> <activity>   # Start recording
STOP                            # Stop recording
STATUS                          # Check current status
HELP                            # Show available commands
```

**Example:**
```
START S01 walking_forward
```

**Output format:**
```
time_ms,L_Heel,L_Arch,L_MetaM,L_MetaL,L_Toe,R_Heel,R_Arch,R_MetaM,R_MetaL,R_Toe
0,1234,1567,1890,1456,1678,1345,1789,1567,1345,1890
20,1245,1578,1901,1467,1689,1356,1800,1578,1356,1901
...
```

---

## Data Naming Conventions

### Raw Activity Data Files

Format: `<subject_id>_<activity>_<timestamp>.csv`

**Examples:**
- `S01_walking_forward_20260115_143022.csv`
- `S02_stairs_up_20260115_144530.csv`
- `S03_sitting_crossed_20260115_150000.csv`

### Subject IDs
- Training subjects: S01-S06
- Testing subjects: S07-S09

### Activity Labels

| Category | Sub-activity | Label |
|----------|--------------|-------|
| Walking | Forward | `walking_forward` |
| Walking | Backward | `walking_backward` |
| Stair climbing | Up | `stairs_up` |
| Stair climbing | Down | `stairs_down` |
| Sitting | Feet on floor | `sitting_floor` |
| Sitting | Cross-legged | `sitting_crossed` |
| Sit-to-stand | Transition | `sit_to_stand` |
| Stand-to-sit | Transition | `stand_to_sit` |
| Standing | Upright | `standing_upright` |
| Standing | Lean left | `standing_lean_left` |
| Standing | Lean right | `standing_lean_right` |

### CSV Column Headers

```
time_ms,L_Heel,L_Arch,L_MetaM,L_MetaL,L_Toe,R_Heel,R_Arch,R_MetaM,R_MetaL,R_Toe
```

---

## Code Style Guidelines

### Arduino (C++)
- Use `camelCase` for variables and functions
- Use `UPPER_CASE` for constants and macros
- Prefix left sock sensors with `L_`, right sock with `R_`
- Document pin mappings at the top of each sketch
- Include course attribution in file headers

**Example:**
```cpp
// Sensor pin definitions - Left sock
const int L_HEEL = A0;
const int L_ARCH = A1;

// Sampling configuration
const int SAMPLE_RATE_HZ = 50;
const int SAMPLE_INTERVAL_MS = 1000 / SAMPLE_RATE_HZ;
```

### Python
- Follow PEP 8 style guide
- Use `snake_case` for variables and functions
- Use `UPPER_CASE` for module-level constants
- Include docstrings for all modules and functions
- Use type hints where appropriate

**Example:**
```python
# Sensor channel names (must match Arduino sketch)
SENSOR_NAMES = [
    "L_Heel", "L_Arch", "L_MetaM", "L_MetaL", "L_Toe",
    "R_Heel", "R_Arch", "R_MetaM", "R_MetaL", "R_Toe"
]

def connect(self) -> bool:
    """Connect to the ESP32 via serial."""
    pass
```

---

## Testing Instructions

### Sensor Characterization
1. Upload `sensor_test.ino` to ESP32
2. Place known weights (100g-5kg) on each sensor zone
3. Record data to `03_Data/calibration/<weight>g.csv`
4. Run `sensor_characterization.py` to generate calibration curves

### Data Collection
1. Upload `data_collection.ino` to ESP32
2. Run `serial_receiver.py` on PC
3. Use commands: `start S01 walking_forward`, then `stop`
4. Verify CSV output in `03_Data/`

### Quality Checks
Before using data for training:
- [ ] Verify all 10 sensor channels have valid readings
- [ ] Check for dropped samples (timestamp gaps > 25ms)
- [ ] Confirm activity labels match actual recorded activity
- [ ] Remove corrupted or incomplete recordings

---

## Data Collection Protocol

1. **Calibration data:** Record 30+ seconds at each reference weight
2. **Activity recordings:** Minimum 30 seconds per activity per subject
3. **Rest periods:** 5 seconds of still standing between activities
4. **Multiple trials:** At least 3 trials per activity per subject

---

## Key Technical Details

### Hardware Architecture
```
Piezoresistive fabric sensors (5 per sock)
    → Voltage divider circuit (10kΩ resistors)
    → ESP32S3 ADC (50+ Hz sampling, 12-bit)
    → Serial/BLE
    → Python receiver (PC)
    → ML classification
```

### Sensor Zones
- **L_Heel / R_Heel:** Heel pressure
- **L_Arch / R_Arch:** Arch pressure
- **L_MetaM / R_MetaM:** Metatarsal medial (big toe side)
- **L_MetaL / R_MetaL:** Metatarsal lateral (little toe side)
- **L_Toe / R_Toe:** Toe pressure

### Feature Extraction (Planned)
- Time-domain statistics (mean, std, min, max)
- Pressure ratios between zones
- Temporal patterns (gait cycle detection)
- Step counting via peak detection

### ML Pipeline (Planned)
- **Algorithm:** Random Forest classifier
- **Validation:** Leave-subject-out (6 train, 3 test)
- **Metrics:** Accuracy, F1-score, confusion matrix

---

## Git Conventions

- **Repository:** Local only (no remote configured)
- **Data files:** Excluded via `.gitignore` (`*.csv`, `*.pkl`, `*.npy`)
- **Python cache:** Excluded (`__pycache__/`, `*.pyc`)
- **IDE files:** Excluded (`.vscode/`, `.idea/`)
- **macOS files:** Excluded (`.DS_Store`)

---

## External References

- **Course:** ELEC-E7840 Smart Wearables, Aalto University
- **MCU:** Seeed Studio XIAO ESP32S3
- **Sensors:** EeonTex Piezoresistive Fabric
- **Assignment PDF:** `00_Planning/Smart Wearables Assignment- Spring2026-draft.pdf`

---

## Notes for AI Agents

1. **No IMU data:** This project is constrained to textile sensors only
2. **Academic context:** Code quality and documentation are important for grading
3. **Team collaboration:** Changes may affect hardware prototyping - communicate clearly
4. **Data privacy:** Human subject data - keep local, no cloud uploads
5. **Hardware dependencies:** Some code cannot be fully tested without the ESP32/sensor hardware
