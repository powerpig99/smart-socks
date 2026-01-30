# Smart Socks - Full Audit: Gaps & Inconsistencies

**Date:** 2026-01-30
**Scope:** All code (Python + Arduino), documentation, and configuration
**Prior audit:** AUDIT_SUMMARY.md (10→6 migration). This audit goes deeper.

---

## Critical Issues

### C1. Sensor Names Still Hardcoded in Core Pipeline Files

**Status:** NOT fixed by prior audit despite claims in AUDIT_SUMMARY.md

**Files affected:**
- `04_Code/python/data_preprocessing.py` (lines 24-26): Hardcodes old 10-sensor names `L_Heel, L_Arch, L_MetaM, L_MetaL, L_Toe, R_Heel, R_Arch, R_MetaM, R_MetaL, R_Toe`
- `04_Code/python/serial_receiver.py` (lines 19-21): Same old 10-sensor names hardcoded

**Impact:** The preprocessing pipeline will fail on data collected with the new 6-sensor firmware. Any CSV with columns `L_P_Heel, L_P_Ball, L_S_Knee, R_P_Heel, R_P_Ball, R_S_Knee` will not be recognized.

**Fix:** Both files must import `SENSORS['names']` from `config.py` instead of hardcoding sensor names.

---

### C2. Cross-Sensor Feature Extraction Broken for 6-Sensor Layout

**File:** `04_Code/python/feature_extraction.py` (lines 125-176)

**Problem:** `extract_cross_sensor_features()` assumes a simple left/right split (`n_sensors // 2`) and then indexes specific anatomical positions (heel=0, arch=1, metatarsals=2-3) that only match the old 5-per-sock layout. With 3 sensors per leg, the index arithmetic is wrong:
- `left_forefoot = np.sum(data[:, 2:n_left])` gets only 1 value (index 2 = L_S_Knee), not forefoot sensors
- Hardcoded references to "Metatarsals at 2-3" don't exist in the 6-sensor design

**Impact:** Cross-sensor features (left/right balance, fore/hindfoot ratio) will be computed incorrectly or raise index errors during training.

**Fix:** Rewrite to use config-based sensor indices: `SENSORS['left_indices']`, `SENSORS['right_indices']`, and sensor type groupings (`pressure_sensors`, `stretch_sensors`).

---

### C3. Feature Extraction Mismatch Between Training and Inference

**Files:**
- Training uses: `04_Code/python/feature_extraction.py`
- Inference uses: `04_Code/python/real_time_classifier.py` → imports from `feature_utils.py`

**Problem:** `feature_utils.py` and `feature_extraction.py` implement the same functions (`extract_statistical_features`, `extract_cross_sensor_features`) with different logic — different zero-crossing-rate formulas, different cross-sensor indexing, different feature ordering.

**Impact:** A model trained with `feature_extraction.py` features will receive differently-computed features at inference time from `feature_utils.py`, producing incorrect predictions silently.

**Fix:** Consolidate into one implementation. Recommended: keep `feature_extraction.py` (config-aware), make `real_time_classifier.py` import from it, and either delete `feature_utils.py` or make it a thin wrapper.

---

### C4. Activity Labels Hardcoded in train_model.py

**File:** `04_Code/python/train_model.py` (lines 20-30)

**Problem:** `ACTIVITIES` list is hardcoded instead of imported from `config.py` (`ACTIVITIES['all']`). If labels change in config, the training script won't see the update.

**Fix:** Replace with `from config import ACTIVITIES` and use `ACTIVITIES['all']`.

---

## High-Priority Issues

### H1. CSV Format Mismatch Between Arduino and Python

**Arduino output** (`data_collection_leg.ino` lines 344-359): Produces CSV with a `leg` column:
```
time_ms,leg,L_P_Heel,L_P_Ball,L_S_Knee
```

**Python expectation** (`data_preprocessing.py`, `CLAUDE.md`): Expects no `leg` column:
```
time_ms,L_Heel,L_Arch,L_MetaM,L_MetaL,L_Toe,R_Heel,R_Arch,R_MetaM,R_MetaL,R_Toe
```

**Impact:** Data collected from the ESP32 will not parse correctly in the Python pipeline. The extra `leg` column will shift all sensor value columns by one.

**Fix:** Either remove the `leg` column from the Arduino CSV output, or update `data_preprocessing.py` to handle it. Also update CLAUDE.md to document the actual format.

---

### H2. Dead Code in ei_led_feedback.ino

**File:** `04_Code/arduino/ei_led_feedback/ei_led_feedback.ino`

**Problem:** `handleSerialCommands()` function (line 258) exists but is never called from `loop()`.

**Fix:** Add `handleSerialCommands();` to `loop()`.

---

### H3. Hardcoded WiFi Credentials

**File:** `04_Code/arduino/data_collection_leg/data_collection_leg.ino` (lines 47-63)

```cpp
const char* HOTSPOT_SSID = "SmartSocks-Hotspot";
const char* HOTSPOT_PASSWORD = "smartsocks123";
```

**Fix:** Move to a `credentials.h` file that is `.gitignore`d, or use build flags.

---

### H4. BLE Implementation Incomplete

**Files:**
- `04_Code/python/ble_client.py`: Partial async implementation, incomplete data parsing
- `04_Code/python/real_time_classifier.py` (line 155-166): BLE mode prints "not fully implemented"

**Fix:** Either complete the BLE implementation or clearly mark it as Part 2/3 scope and remove the `--ble` CLI flag from `real_time_classifier.py`.

---

### H5. Test Coverage Insufficient

**Current tests:** Only `tests/test_data_validation.py` exists.

**Missing tests for:**
- `data_preprocessing.py` — no tests at all
- `feature_extraction.py` — no tests at all
- `train_model.py` — no tests at all
- `real_time_classifier.py` — no tests at all

**Additionally:** Test fixtures in `conftest.py` use OLD sensor names (`L_Heel`, `R_Heel`) instead of new names from config.

**Fix:** Add unit tests for preprocessing, feature extraction, and training. Update `conftest.py` fixtures to use `SENSORS['names']` from config.

---

## Moderate Issues

### M1. CLAUDE.md Still Describes 10-Sensor Architecture

**File:** `CLAUDE.md`

**Specific problems:**
- Line 5: "Piezoresistive fabric sensors (5 per sock, 10 total)" — should be 6 total (3 per leg)
- Line 11: "Sensor zones per sock: Heel, Arch, Metatarsal medial, Metatarsal lateral, Toe" — outdated
- Line 78: CSV columns list `L_Heel,L_Arch,L_MetaM,L_MetaL,L_Toe,R_Heel,R_Arch,R_MetaM,R_MetaL,R_Toe` — should be `L_P_Heel,L_P_Ball,L_S_Knee,R_P_Heel,R_P_Ball,R_S_Knee`

**Fix:** Update all architecture descriptions and CSV column definitions to match the 6-sensor design.

---

### M2. Legacy v1 Design Documents Not Clearly Marked

**Files still describing 10-sensor design without deprecation headers:**
- `01_Design/circuit_diagram.md` — full 10-sensor circuit design
- `01_Design/sensor_placement.md` — 5-zones-per-foot layout
- `AGENTS.md` (lines 9-26) — "10 piezoresistive fabric sensors"

v2 documents exist (`circuit_diagram_v2.md`, `sensor_placement_v2.md`) but the v1 files lack a clear "DEPRECATED" banner.

**Fix:** Add a deprecation notice at the top of each v1 document pointing to the v2 version.

---

### M3. Path Conventions Inconsistent

Different files use different approaches:
- `config.py` (lines 281-288): Defines `PATHS` dict with relative paths like `../../03_Data/raw/`
- `serial_receiver.py` (line 144): Hardcodes `../../03_Data/`
- `real_time_classifier.py`: No path constants, uses argparse defaults only

Running scripts from different working directories will break relative paths.

**Fix:** Standardize all path references through `config.py`'s `PATHS` dict.

---

### M4. Serial Port Platform Mismatch

- `config.py` (lines 50-62): Port hardcoded to `/dev/cu.usbmodem2101` (macOS)
- `real_time_classifier.py` (line 426): Default `/dev/ttyUSB0` (Linux)
- `TROUBLESHOOTING.md` (line 13): References `/dev/ttyUSB0`

**Fix:** Use platform detection or make port a required argument. Update docs to list both macOS and Linux port names.

---

### M5. No Model-Config Version Tracking

When config changes (sensor count, feature parameters), saved `.joblib` models become incompatible with the new pipeline, but there's no mechanism to detect this.

**Fix:** Add a `CONFIG_VERSION` string to `config.py`, embed it in saved models, and check it at load time in `real_time_classifier.py`.

---

### M6. platformio.ini References Deprecated Code

**File:** `platformio.ini` (line 96)

The `xiao_esp32s3` environment references `04_Code/arduino/data_collection_wireless/` which is in the deprecated folder.

**Fix:** Remove or update the legacy environment.

---

### M7. Undocumented Serial Commands

**File:** `04_Code/arduino/data_collection_leg/data_collection_leg.ino`

Implements commands not in CLAUDE.md: `TRIGGER`, `MASTER`, `SLAVE`, `SYNC OFF`, `CAL ON`, `CAL OFF`.

**Fix:** Document these in CLAUDE.md under the serial protocol section.

---

### M8. config.py Validation Gaps

**File:** `04_Code/python/config.py` (lines 342-364)

`validate_config()` doesn't check:
- Whether `SENSORS['names']` length matches `total_count`
- Whether sensor names in sub-lists exist in the main names list
- Whether left/right index arrays are within bounds

**Fix:** Add these validation checks.

---

## Minor Issues

### L1. Inconsistent Logging

Most pipeline files use `print()` for output. Only `data_validation.py` uses Python's `logging` module. `logging_utils.py` exists but isn't used by the core pipeline.

**Fix:** Migrate core pipeline files to use `logging_utils.py`.

---

### L2. Missing Type Hints

Most functions across `feature_extraction.py`, `data_preprocessing.py`, `feature_utils.py` lack type annotations.

**Fix:** Add return types and parameter annotations to public functions.

---

### L3. Magic Numbers Not in Config

- `real_time_classifier.py` line 309: `SMOOTHING_WINDOW_SIZE = 5`
- `real_time_classifier.py` line 344: `2000` threshold for step detection
- `data_preprocessing.py` line 24: Various detection parameters

**Fix:** Move to `config.py` under appropriate sections.

---

### L4. SVG Diagrams May Be Outdated

Files in `01_Design/diagrams/`:
- `sensor_placement.svg` — may show 5-zone layout
- `system_architecture.svg` — may show single-ESP32 architecture
- `voltage_divider.svg` — likely still correct

**Fix:** Verify each SVG matches the current 6-sensor, dual-ESP32 design. Update or create v2 SVGs if needed.

---

### L5. Empty Directories

- `05_Analysis/` — empty (output placeholder)
- `bin/` — empty
- `src/` — empty

`bin/` and `src/` appear vestigial. If unused, remove them.

---

## Implementation Priority

| # | Issue | Severity | Effort | Blocks |
|---|-------|----------|--------|--------|
| C1 | Sensor names hardcoded in preprocessing | Critical | Low | Data pipeline |
| C2 | Cross-sensor features broken | Critical | Medium | ML training |
| C3 | Training/inference feature mismatch | Critical | Medium | Real-time classification |
| C4 | Activities hardcoded in train_model | Critical | Low | Config consistency |
| H1 | CSV format mismatch Arduino↔Python | High | Low | Data collection |
| H5 | Test coverage insufficient | High | High | Quality assurance |
| M1 | CLAUDE.md outdated architecture | Moderate | Low | Developer onboarding |
| M5 | No model-config versioning | Moderate | Medium | Model compatibility |
| H3 | Hardcoded WiFi credentials | High | Low | Security |
| H2 | Dead code in ei_led_feedback | High | Low | LED feedback feature |
| M2 | v1 docs missing deprecation notices | Moderate | Low | Documentation clarity |
| M3 | Path conventions inconsistent | Moderate | Low | Script portability |
| M4 | Serial port platform mismatch | Moderate | Low | Cross-platform |
| M6 | platformio.ini legacy reference | Moderate | Low | Build config |
| M7 | Undocumented serial commands | Moderate | Low | Protocol docs |
| M8 | Config validation gaps | Moderate | Low | Config safety |
| H4 | BLE implementation incomplete | High | High | BLE feature |
| L1-L5 | Minor issues | Low | Various | Code quality |

---

## Suggested Implementation Order

**Phase 1 — Fix data pipeline (C1, C4, H1):**
Update `data_preprocessing.py` and `serial_receiver.py` to import from config. Update `train_model.py` to import activities from config. Decide on CSV format and align Arduino output with Python expectations.

**Phase 2 — Fix feature pipeline (C2, C3):**
Rewrite `extract_cross_sensor_features()` for 6-sensor layout. Consolidate `feature_utils.py` and `feature_extraction.py` into one implementation. Update `real_time_classifier.py` imports.

**Phase 3 — Documentation sync (M1, M2, M7):**
Update CLAUDE.md architecture section. Add deprecation banners to v1 design docs. Document extended serial commands.

**Phase 4 — Testing and hardening (H5, M5, M8):**
Add unit tests for preprocessing and feature extraction. Add config versioning to saved models. Improve config validation.

**Phase 5 — Cleanup (H2, H3, M3, M4, M6, L1-L5):**
Fix dead code, credentials, paths, ports, logging, type hints, magic numbers, empty dirs.

**Phase 6 — BLE (H4):**
Complete or defer BLE implementation based on project timeline.
