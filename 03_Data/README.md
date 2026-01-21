# Data Organization Guidelines

This directory contains all sensor data for the Smart Socks project.

## Directory Structure

```
03_Data/
├── calibration/          # Sensor characterization data
│   ├── 0g.csv
│   ├── 100g.csv
│   ├── 200g.csv
│   └── ...
├── raw/                  # Raw activity recordings
│   ├── S01/             # Subject 01
│   ├── S02/             # Subject 02
│   └── ...
├── processed/           # Preprocessed/segmented data
└── features/            # Extracted features for ML
```

## File Naming Convention

### Raw Activity Data

Format: `<subject_id>_<activity>_<timestamp>.csv`

Examples:
- `S01_walking_forward_20260115_143022.csv`
- `S02_stairs_up_20260115_144530.csv`
- `S03_sitting_crossed_20260115_150000.csv`

### Subject IDs

- Training subjects: S01-S06
- Testing subjects: S07-S09

### Activity Labels

| Activity Category | Sub-activity | Label |
|------------------|--------------|-------|
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

## CSV File Format

### Sensor Data Columns

| Column | Description | Unit |
|--------|-------------|------|
| `time_ms` | Timestamp from recording start | milliseconds |
| `L_Heel` | Left heel sensor | ADC (0-4095) |
| `L_Arch` | Left arch sensor | ADC (0-4095) |
| `L_MetaM` | Left metatarsal medial | ADC (0-4095) |
| `L_MetaL` | Left metatarsal lateral | ADC (0-4095) |
| `L_Toe` | Left toe sensor | ADC (0-4095) |
| `R_Heel` | Right heel sensor | ADC (0-4095) |
| `R_Arch` | Right arch sensor | ADC (0-4095) |
| `R_MetaM` | Right metatarsal medial | ADC (0-4095) |
| `R_MetaL` | Right metatarsal lateral | ADC (0-4095) |
| `R_Toe` | Right toe sensor | ADC (0-4095) |

### Sample Rate

- Target: 50 Hz (20ms between samples)
- Actual rate may vary slightly; always use timestamps for analysis

## Data Collection Protocol

1. **Calibration data**: Record 30+ seconds at each reference weight
2. **Activity recordings**: Minimum 30 seconds per activity per subject
3. **Rest periods**: 5 seconds of still standing between activities
4. **Multiple trials**: At least 3 trials per activity per subject

## Quality Checks

Before using data for training:

- [ ] Verify all 10 sensor channels have valid readings
- [ ] Check for dropped samples (timestamp gaps > 25ms)
- [ ] Confirm activity labels match actual recorded activity
- [ ] Remove corrupted or incomplete recordings
