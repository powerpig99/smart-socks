# Smart Socks - Project Refactor Summary

**Date:** January 30, 2026  
**Scope:** Codebase audit, cleanup, and simplification for Part 1 & 2

---

## Key Findings from Audit

### 1. Sensor Architecture Inconsistency
The project had migrated from a 10-sensor design (5 per sock) to a 6-sensor design (3 per leg: 2 pressure + 1 stretch), but **critical Python files still used old sensor names**:

| Component | Before (Broken) | After (Fixed) |
|-----------|-----------------|---------------|
| `data_preprocessing.py` | Hardcoded 10 old sensor names | Imports from `config.py` |
| `serial_receiver.py` | Hardcoded 10 old sensor names | Imports from `config.py` |
| `train_model.py` | Hardcoded activity list | Imports from `config.py` |
| `real_time_classifier.py` | Old sensor names in step detection | Updated to new names |

### 2. Firmware Complexity
Originally had 3 separate firmware environments (left_leg, right_leg, calibration) with different build flags and source directories. This was unnecessarily complex.

**Insight:** The ESP32 hardware is identical for both legs - only the sensor wiring differs (A0-A2 vs A3-A5). Leg differentiation should happen in **data labeling**, not firmware.

### 3. PlatformIO Build Issues
The `src_filter` option was deprecated, and attempts to use per-environment source directories (`src_dir`, `src`) failed due to PlatformIO version limitations.

**Solution:** Use standard `src/` folder with a single unified firmware.

---

## Changes Made

### Firmware Simplification

**Before:**
```ini
[env:left_leg]
src_dir = 04_Code/arduino/data_collection_leg
build_flags = -D LEG_ID_LEFT=1

[env:right_leg]
src_dir = 04_Code/arduino/data_collection_leg
build_flags = -D LEG_ID_RIGHT=1

[env:calibration]
src_dir = 04_Code/arduino/calibration_all_sensors
```

**After:**
```ini
[env:xiao_esp32s3]
; Single firmware reads all 6 sensors (A0-A5)
; Left leg: connect to A0-A2
; Right leg: connect to A3-A5
; All 6: connect to A0-A5
```

### Critical Bug Fixes

1. **Fixed function declaration order** in `src/main.cpp`
   - Added forward declarations for `handleRoot()` and `handleSensors()`
   - C++ requires functions to be declared before use

2. **Fixed Python sensor name references**
   - `data_preprocessing.py`: Now imports `SENSORS['names']` from `config.py`
   - `serial_receiver.py`: Now imports `SENSORS['names']` from `config.py`
   - `train_model.py`: Now imports `ACTIVITIES['all']` from `config.py`
   - `real_time_classifier.py`: Updated step detection to use `L_P_Heel`, `R_P_Heel`

### Documentation Updates

- **AGENTS.md**: Complete rewrite for 6-sensor architecture
- **CLAUDE.md**: Updated with current commands and architecture
- **v1 design docs**: Added deprecation banners pointing to v2

### Cleanup

- Removed empty directories (`bin/`, `src/` was recreated with firmware)
- Removed legacy PlatformIO environment references
- Audit files now local-only (not pushed to GitHub)

---

## Current Architecture

### Hardware Setup
```
ESP32S3 XIAO (all units run same firmware)
├── A0: L_P_Heel  (or R_P_Heel if using A3-A5)
├── A1: L_P_Ball  (or R_P_Ball if using A3-A5)
├── A2: L_S_Knee  (or R_S_Knee if using A3-A5)
├── A3: R_P_Heel
├── A4: R_P_Ball
├── A5: R_S_Knee
```

**Deployment Options:**
1. **Single leg:** Connect sensors to A0-A2 (firmware reads all 6 but only A0-A2 have data)
2. **Both legs (one ESP32):** Connect all 6 sensors to A0-A5
3. **Both legs (two ESP32s):** Each ESP32 connects 3 sensors to A0-A2

### Data Collection Strategy

**For Part 1 (Sensor Characterization):**
- Use one ESP32 with all 6 sensors connected (A0-A5)
- Python script labels which leg each reading belongs to

**For Part 2 (ML Data Collection):**
- Use two ESP32s, one per leg
- Each ESP32 has 3 sensors on A0-A2
- Python merges streams and labels left/right

### Firmware Features (src/main.cpp)

- Reads all 6 sensors at 50Hz
- WiFi AP mode (SSID: `SmartSocks-Cal`)
- Web dashboard at `http://192.168.4.1`
- Serial CSV output for Python visualizer
- JSON API at `/api/sensors`

---

## Build Instructions

### Using VS Code PlatformIO Plugin
1. Open project folder
2. Click PlatformIO icon in sidebar
3. Select "Build" under `env:xiao_esp32s3`
4. Or run task: `PlatformIO: Build`

### Using Command Line
```bash
# Make sure platformio is in your PATH
export PATH="$PATH:$HOME/.platformio/penv/bin"

# Build
platformio run --environment xiao_esp32s3

# Upload
platformio run --environment xiao_esp32s3 --target upload
```

---

## Files Modified

| File | Change |
|------|--------|
| `platformio.ini` | Single environment, standard src/ folder |
| `src/main.cpp` | New unified firmware with forward declarations |
| `data_preprocessing.py` | Import sensor names from config |
| `serial_receiver.py` | Import sensor names from config |
| `train_model.py` | Import activities from config |
| `real_time_classifier.py` | Fix step detection sensor names |
| `AGENTS.md` | Complete rewrite for 6-sensor design |
| `CLAUDE.md` | Updated architecture and commands |
| `.gitignore` | Added audit files as local-only |

---

## Future Considerations (Part 3 - Edge ML)

When implementing Edge ML with two ESP32s:
1. **Wireless sync:** May need to re-establish dual-leg firmware with sync
2. **Edge Impulse:** Each ESP32 could run inference locally
3. **Communication:** ESP-NOW or BLE between ESP32s for coordination

For now, the single-firmware approach covers Part 1 and Part 2 requirements.

---

## Verification Checklist

- [x] PlatformIO build succeeds (`platformio run --environment xiao_esp32s3`)
- [x] All Python files import from `config.py`
- [x] Documentation reflects 6-sensor architecture
- [x] No hardcoded sensor names in critical pipeline files
- [x] v1 design docs marked as deprecated
- [x] Empty directories removed
- [x] Git commits pushed to remote

---

**Status:** ✅ Ready for Part 1 data collection
