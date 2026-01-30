# Smart Socks - Audit Verification & Final Recommendation

**Date:** January 30, 2026  
**Auditor:** AI Code Review  
**Status:** ⚠️ CRITICAL - Project has significant inconsistencies

---

## Executive Summary

The project is in a **partially migrated state** between the old 10-sensor design and the new 6-sensor design. While the hardware (Arduino) code has been updated for the 6-sensor configuration, **critical Python pipeline files still use the old 10-sensor names**, making the ML pipeline non-functional with current hardware.

### Migration Status Overview

| Component | 10-Sensor (Old) | 6-Sensor (New) | Status |
|-----------|-----------------|----------------|--------|
| Arduino `data_collection_leg.ino` | ❌ | ✅ | Updated |
| Arduino `calibration_all_sensors.ino` | ❌ | ✅ | Updated |
| `config.py` | ❌ | ✅ | Updated |
| `feature_extraction.py` | ❌ | ✅ | Updated |
| `data_preprocessing.py` | ✅ | ❌ | **DEPRECATED - needs update** |
| `serial_receiver.py` | ✅ | ❌ | **DEPRECATED - needs update** |
| `train_model.py` activities | Hardcoded | ❌ | **Needs update** |
| `feature_utils.py` cross-sensor | Old logic | ❌ | **Needs update** |
| `real_time_classifier.py` | Partial | Partial | **Step detection broken** |
| CLAUDE.md | ✅ | ❌ | Outdated |
| AGENTS.md | ✅ | ❌ | Outdated |
| v1 Design docs | No banner | - | Missing deprecation |

---

## Verified Issues (Confirmed by Code Review)

### 🔴 CRITICAL (Blocks Data Pipeline)

#### C1. `data_preprocessing.py` - Hardcoded 10-Sensor Names
**File:** `04_Code/python/data_preprocessing.py` (lines 24-27)
```python
SENSOR_NAMES = [
    "L_Heel", "L_Arch", "L_MetaM", "L_MetaL", "L_Toe",
    "R_Heel", "R_Arch", "R_MetaM", "R_MetaL", "R_Toe"
]
```
**Expected (from config.py):**
```python
["L_P_Heel", "L_P_Ball", "L_S_Knee", "R_P_Heel", "R_P_Ball", "R_S_Knee"]
```
**Impact:** Preprocessing will fail on all new data files.

#### C2. `serial_receiver.py` - Hardcoded 10-Sensor Names
**File:** `04_Code/python/serial_receiver.py` (lines 21-24)
Same issue as C1 - cannot receive data from current firmware.

#### C3. `train_model.py` - Hardcoded Activities
**File:** `04_Code/python/train_model.py` (lines 28-35)
Activities list is hardcoded instead of imported from `config.py`.

#### C4. `real_time_classifier.py` - Old Sensor Names in Step Detection
**File:** `04_Code/python/real_time_classifier.py` (lines 248-250)
```python
left_heel = sensor_data.get('L_Heel', 0)  # Should be 'L_P_Heel'
right_heel = sensor_data.get('R_Heel', 0)  # Should be 'R_P_Heel'
```

---

### 🟡 HIGH (Functional Impact)

#### H1. CSV Format Mismatch
**Arduino output** (`data_collection_leg.ino` line 346):
```
time_ms,leg,L_P_Heel,L_P_Ball,L_S_Knee
```

**Python expectation** (`data_preprocessing.py`):
```
time_ms,L_Heel,L_Arch,L_MetaM,L_MetaL,L_Toe,R_Heel,R_Arch,R_MetaM,R_MetaL,R_Toe
```

**Impact:** The extra `leg` column will shift all columns; Python expects merged data.

#### H2. `ei_led_feedback.ino` - Dead Code
**File:** `04_Code/arduino/ei_led_feedback/ei_led_feedback.ino`
`handleSerialCommands()` function exists but is never called from `loop()`.

#### H3. `feature_utils.py` vs `feature_extraction.py` Divergence
- `feature_utils.py` uses hardcoded index arithmetic for 10-sensor layout
- `feature_extraction.py` correctly uses config-based sensor groupings
- Training vs inference will use different feature computations

---

### 🟠 MODERATE (Documentation/Quality)

#### M1. CLAUDE.md - Outdated Architecture
- Line 14: "5 per sock, 10 total" → Should be "3 per leg, 6 total"
- Line 22: Old sensor zone names
- Line 87: Old CSV column format

#### M2. AGENTS.md - Outdated Architecture
- Line 26: "10 piezoresistive fabric sensors" → Should be 6
- Line 27: Old sensor zones
- Lines 135, 177, 212: Old sensor names in examples

#### M3. v1 Design Docs Not Marked as Deprecated
- `01_Design/circuit_diagram.md` - No deprecation banner
- `01_Design/sensor_placement.md` - No deprecation banner
- v2 versions exist but aren't clearly the current standard

#### M4. platformio.ini Legacy Environment
Line 96 references `data_collection_wireless/` which is in deprecated folder.

#### M5. Empty Directories
- `bin/` - Empty, vestigial
- `src/` - Contains only broken symlink

---

## Final Recommendation

### Option A: Full Migration (Recommended)

Update all remaining Python files to use 6-sensor config. **This is the cleanest approach** but requires 2-3 hours of work.

**Steps:**
1. Update `data_preprocessing.py` to import from config
2. Update `serial_receiver.py` to import from config  
3. Update `train_model.py` to import activities from config
4. Fix `real_time_classifier.py` step detection sensor names
5. Update `feature_utils.py` to match `feature_extraction.py`
6. Update CLAUDE.md and AGENTS.md
7. Add deprecation banners to v1 docs
8. Remove empty directories

### Option B: Minimal Fix (Fastest)

Only fix the critical blockers to get a working pipeline.

**Steps:**
1. Fix `data_preprocessing.py` sensor names
2. Fix `serial_receiver.py` sensor names
3. Handle `leg` column in CSV parsing
4. Fix step detection sensor names
5. Leave documentation as-is for now

### Recommended Choice: Option B Now, Option A Later

Given the project timeline (Part 1 ends Week 7), **Option B** provides immediate functionality. Document the remaining issues for Part 2 (ML phase).

---

## Immediate Action Required

The following must be fixed before any data collection:

1. ✅ **Fix `data_preprocessing.py`** - Import SENSOR_NAMES from config
2. ✅ **Fix `serial_receiver.py`** - Import SENSOR_NAMES from config  
3. ✅ **Fix CSV parsing** - Handle `leg` column or remove from Arduino
4. ✅ **Fix `real_time_classifier.py`** - Update step detection sensor names

---

## Cleanup Actions (Deprecated Content)

### Files/Directories to Remove or Archive

| Item | Action | Reason |
|------|--------|--------|
| `bin/` | Remove | Empty, unused |
| `src/` | Remove | Broken symlink only |
| `platformio.ini` lines 86-97 | Remove | References deprecated code |
| `01_Design/circuit_diagram.md` | Add banner | Direct to v2 version |
| `01_Design/sensor_placement.md` | Add banner | Direct to v2 version |
| `04_Code/arduino/deprecated_10_sensor/` | Keep | Already properly organized |

### Files to Update with Deprecation Notices

1. `01_Design/circuit_diagram.md` - Add banner pointing to v2
2. `01_Design/sensor_placement.md` - Add banner pointing to v2
3. `AGENTS.md` - Update architecture section
4. `CLAUDE.md` - Update architecture section

---

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Critical Issues | 4 | Must fix before data collection |
| High Priority | 3 | Fix before ML pipeline |
| Moderate Issues | 5 | Can defer to Part 2 |
| Minor Issues | 5 | Cleanup when convenient |
| Deprecated Files | 2 docs + 2 dirs | Clean up now |

**Bottom Line:** The hardware code is ready, but the Python pipeline needs 4 critical fixes before data collection can proceed. The documentation reflects the old design and needs updating to prevent confusion.

---

*Generated for Smart Socks Project - ELEC-E7840 Smart Wearables*
