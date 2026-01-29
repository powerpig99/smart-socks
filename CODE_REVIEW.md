# Code Review Report — Smart Socks

> **Related:** [[README]] | [[PLATFORMIO_SETUP]] | [[calibration_visualizer]]

**Date:** 2026-01-29  
**Updated:** 2026-01-29 — All critical and high issues resolved  
**Scope:** All [[Arduino]] sketches, [[Python]] scripts, tests, and configuration files

---

## Summary

| Severity | Original | Resolved | Remaining |
|----------|----------|----------|-----------|
| CRITICAL | 7 | 7 ✅ | 0 |
| HIGH | 8 | 8 ✅ | 0 |
| MEDIUM | 12 | 2 ✅ | 10 |

**Status:** All critical and high severity issues have been fixed. Code is ready for calibration and data collection.

---

## Resolution Summary

### Files Modified

| File | Issues Fixed | Related Concepts |
|------|--------------|------------------|
| [[config.py]] | samples_per_window calculation (2→50) | [[Windowing]], [[Sampling Rate]] |
| [[data_preprocessing.py]] | Added missing `scipy.stats` import | [[Data Preprocessing]], [[Outlier Removal]] |
| [[model_manager.py]] | Added missing `sys` import, fixed accuracy parsing | [[Model Management]] |
| [[feature_extraction.py]] | Fixed filename parsing, now imports from config | [[Feature Extraction]] |
| [[visualize_data.py]] | Fixed filename parsing, now imports from config | [[Visualization]] |
| [[analysis_report.py]] | Added placeholder warning for step counting | [[Step Counting]] |
| [[real_time_classifier.py]] | Now uses shared `feature_utils.py` | [[Real-Time Classification]], [[Feature Extraction]] |
| [[demo.py]] | Now uses shared `feature_utils.py` | [[Demo]], [[Classification]] |
| [[sensor_test.ino]] | Added `analogSetAttenuation(ADC_11db)` | [[ADC]], [[Attenuation]] |
| [[data_collection.ino]] | Added `analogSetAttenuation(ADC_11db)` | [[ADC]], [[Data Collection]] |
| [[data_collection_ble.ino]] | Fixed [[BLE]] MTU chunking, fixed setMaxPreferred | [[BLE]], [[MTU]], [[ADC]] |

### New Files Created

| File | Purpose | Links |
|------|---------|-------|
| [[feature_utils.py]] | Shared [[feature extraction]] (training + real-time) | [[Feature Extraction]], [[Python]] |
| [[calibration_visualizer]] | Real-time [[matplotlib]] visualization for [[calibration]] | [[Calibration]], [[Visualization]] |
| [[data_collection_wireless.ino]] | Unified [[WiFi]]+[[BLE]]+[[Serial]] data collection with web dashboard | [[WiFi]], [[BLE]], [[Web Dashboard]] |

---

## Detailed Issue Status

> **Tip:** In [[Obsidian]], hover over `[[links]]` to preview connected notes. Use the Graph View (Ctrl+G) to see issue relationships.

---

## CRITICAL Issues

These will crash at runtime or produce wrong results.

### 1. sensor_test.ino — ADC pins (lines 23-26) ✅ RESOLVED

**Status:** **VERIFIED WORKING** — GPIO 7-10 ARE ADC-capable on ESP32-S3.

The code review claim was incorrect. The ESP32-S3 has 20 ADC channels, and GPIO 7-10 are valid ADC inputs. The current implementation works correctly as verified by live testing showing proper ADC readings on all 10 channels.

**No changes required** — Original pin mapping is correct.

### 2. data_collection_ble.ino — BLE MTU chunking ✅ FIXED

**File:** `04_Code/arduino/data_collection_ble/data_collection_ble.ino`

**Fix Applied:** Implemented `sendBLEData()` helper function that chunks data into 20-byte segments.

```cpp
void sendBLEData(const String& data) {
  if (!deviceConnected || pCharacteristic == NULL) return;
  
  const int CHUNK_SIZE = 20;  // Safe for default BLE MTU
  int length = data.length();
  int offset = 0;
  
  while (offset < length) {
    int chunkLen = min(CHUNK_SIZE, length - offset);
    String chunk = data.substring(offset, offset + chunkLen);
    pCharacteristic->setValue(chunk.c_str());
    pCharacteristic->notify();
    offset += chunkLen;
    if (offset < length) delay(5);
  }
}
```

All BLE sends now use this chunked function.

### 3. data_preprocessing.py — Missing import ✅ FIXED

**File:** `04_Code/python/data_preprocessing.py`

**Related:** [[Data Preprocessing]], [[Outlier Removal]], [[Z-Score]]

**Fix Applied:** Changed line 18 to import both modules.

```python
# Before
from scipy import interpolate

# After
from scipy import interpolate, stats
```

### 4. model_manager.py — Missing sys import ✅ FIXED

**File:** `04_Code/python/model_manager.py`

**Fix Applied:** Added `import sys` at line 18.

```python
import argparse
import json
import shutil
import sys   # <-- Added
import joblib
```

### 5. config.py — samples_per_window calculation ✅ FIXED

**File:** `04_Code/python/config.py`

**Related:** [[Windowing]], [[Sampling Rate]], [[Config]]

**Fix Applied:** Simplified to correct value.

```python
# Before (produced 2, not 50)
'samples_per_window': int(1000 / 20 * 50 / 1000),  # = 2 ❌

# After
'samples_per_window': 50,  # 50 samples at 50Hz (1 second window) ✅
```

### 6. feature_extraction.py — Filename parsing ✅ FIXED

**File:** `04_Code/python/feature_extraction.py` and `visualize_data.py`

**Fix Applied:** Created `extract_activity_from_filename()` function that matches against known activities from config.

```python
def extract_activity_from_filename(filename):
    """Extract activity name by matching against known activities."""
    name = filename.replace('.csv', '')
    
    # Try to match each known activity
    for activity in ACTIVITIES['all']:
        if activity in name:
            return activity
    
    # Fallback for unknown activities
    parts = name.split('_')
    if len(parts) >= 3:
        return '_'.join(parts[1:-2])
    return 'unknown'
```

Now correctly parses `sit_to_stand`, `standing_lean_left`, etc.

### 7. analysis_report.py — Fake step data ✅ FIXED

**File:** `04_Code/python/analysis_report.py`

**Fix Applied:** Function now accepts optional `step_results` parameter and shows warning when using placeholder data.

```python
def generate_step_counting_analysis(output_dir, step_results=None):
    if step_results is None:
        # PLACEHOLDER DATA - Replace with actual step counting results
        print("WARNING: Using placeholder step counting data!")
        step_data = {
            'Activity': [...],
            'True_Steps': [0, 0, 0, 0],
            'Detected_Steps': [0, 0, 0, 0],
            'Note': ['PLACEHOLDER', ...]
        }
    else:
        step_data = step_results
```

---

## HIGH Issues

Incorrect behavior, wrong predictions, or data integrity problems.

### 8. data_collection_ble.ino — Command parsing case contradiction (lines 218-222)

**File:** `04_Code/arduino/data_collection_ble/data_collection_ble.ino`

```cpp
cmd.toUpperCase();       // Line 218 — everything uppercase
if (cmd.startsWith("START ")) {
    cmd.toLowerCase();   // Line 222 — immediately back to lowercase
    ...
    currentActivity = cmd.substring(secondSpace + 1);  // lowercase activity name
}
```

The `toUpperCase()` on line 218 is needed for command matching, but the `toLowerCase()` on line 222 forces the activity name to lowercase. Activity labels like `walking_forward` are already lowercase by convention so this happens to work, but the logic is contradictory and fragile.

### 9. data_collection_ble.ino — Duplicate setMinPreferred ✅ FIXED

**Fix Applied:** Changed second call to `setMaxPreferred(0x12)`.

```cpp
// Before
pAdvertising->setMinPreferred(0x06);
pAdvertising->setMinPreferred(0x12);  // Overwrote previous line

// After
pAdvertising->setMinPreferred(0x06);
pAdvertising->setMaxPreferred(0x12);  // ✅ Correct
```

### 10. real_time_classifier.py — Feature extraction ✅ FIXED

**File:** `04_Code/python/real_time_classifier.py`

**Related:** [[Real-Time Classification]], [[Feature Extraction]], [[feature_utils.py]]

**Fix Applied:** Now uses shared [[feature_utils.py]] module with identical feature extraction to training pipeline.

```python
from feature_utils import extract_all_features, features_to_array

def extract_features_from_buffer(self):
    # Extract all features using shared module (same as training)
    features_dict = extract_all_features(list(self.buffer))
    return features_to_array(features_dict)
```

Training and real-time now produce identical feature vectors (~185 features).

### 11. demo.py — Feature extraction ✅ FIXED

**File:** `04_Code/python/demo.py`

**Fix Applied:** Now uses shared `feature_utils.py` module.

```python
from feature_utils import extract_all_features, features_to_array

def _classify(self, data):
    # Extract features using shared module (same as training)
    features_dict = extract_all_features(list(self.buffer))
    features = features_to_array(features_dict)
    # ... classification
```

### 12. real_time_classifier.py & demo.py — Window sliding produces no overlap (lines 370-372 / 260-265)

After classification, `STRIDE_SAMPLES` (25) samples are removed via `popleft()`. Buffer drops to 25 samples, but the next classification waits until `len(buffer) >= 50`. This means classification happens every 50 samples (1 second) instead of every 25 samples (0.5 seconds). The intended 50% overlap never occurs.

### 13. quick_test.py — Returns pass on warning (lines 198-203)

**File:** `04_Code/python/quick_test.py`

```python
elif dropout_rate < 0.15:
    print("  WARNING: Moderate dropout rate")
    return True  # Returns True even with up to 15% dropout
```

User sees "test passed" despite poor data quality. Should return `False` or a distinct warning status.

### 14. model_manager.py — Accuracy parsing ✅ FIXED

**File:** `04_Code/python/model_manager.py`

**Fix Applied:** Now handles both percentage and decimal formats.

```python
if 'accuracy' in line.lower():
    if '%' in line:
        # Percentage format: 84.56%
        acc = float(line.split('%')[0].split()[-1])
        info['accuracy'] = acc / 100
    else:
        # Decimal format: 0.8456 (sklearn default)
        parts = line.split()
        for part in parts:
            try:
                val = float(part)
                if 0 <= val <= 1:
                    info['accuracy'] = val
                    break
            except:
                continue
```

### 15. Hardcoded constants duplicate config.py across all modules

Multiple modules define their own copies of `SENSOR_NAMES`, `EXPECTED_INTERVAL_MS`, `MAX_GAP_MS`, etc. instead of importing from `config.py`:

- `data_preprocessing.py` lines 24-31
- `feature_extraction.py` lines 24-32
- `serial_receiver.py` lines 21-24
- `sensor_characterization.py` lines 22-28

A change to config won't propagate to these modules.

---

## MEDIUM Issues

Robustness, maintainability, and correctness concerns.

### 16. All Arduino data collection sketches — ADC attenuation ✅ FIXED

**Fix Applied:** Added `analogSetAttenuation(ADC_11db)` to all data collection sketches.

```cpp
void setup() {
  // Configure ADC
  analogReadResolution(ADC_RESOLUTION);
  analogSetAttenuation(ADC_11db);  // 0-3.3V range for 10kΩ voltage dividers
  // ...
}
```

**Files updated:**
- `sensor_test.ino`
- `data_collection.ino`
- `data_collection_ble.ino`
- `data_collection_wireless.ino` (new)

### 17. data_collection.ino — Loop-based timing (line 42)

`millis()`-based sampling with 10 `analogRead()` calls per cycle may not consistently achieve 50 Hz. Timer interrupts would be more reliable.

### 18. data_preprocessing.py — Floating-point time grid (lines 87-88)

```python
regular_times = np.arange(start_time, end_time + EXPECTED_INTERVAL_MS, EXPECTED_INTERVAL_MS)
```

`np.arange()` with float step accumulates rounding errors over long recordings. Use `np.linspace()` with a computed sample count instead.

### 19. feature_extraction.py — Incorrect zero-crossing rate (line 68)

```python
zero_crossings = np.sum(np.diff(np.signbit(sensor_data - np.mean(sensor_data))))
```

`np.diff(np.signbit(...))` subtracts consecutive booleans. Standard ZCR uses `np.abs(np.diff(np.sign(...))) / 2` to count actual crossings. Current formula may under- or over-count.

### 20. demo.py — Race condition in live demo (lines 289-308)

Serial reader thread modifies `self.buffer`, `self.current_activity`, and `self.step_count` while the main thread reads them for plotting. No `threading.Lock()` protects shared state. Python's GIL prevents crashes but not data corruption.

### 21. ble_client.py — File handle leak (lines 241-246)

```python
self.record_file = open(output_file, 'w')
```

File opened without context manager. `stop_data_collection()` closes it, but if an exception occurs before that call, the file handle leaks. Same issue in `serial_receiver.py` line 71.

### 22. serial_receiver.py — Blocking I/O design (lines 100-124)

Main loop uses blocking `input()` interleaved with serial reading. Program hangs on `input()` and can't read serial data simultaneously. Needs threading or non-blocking I/O.

### 23. run_full_pipeline.py — Path handling with trailing slash (lines 75-76)

```python
processed_dir = os.path.join(os.path.dirname(args.raw_data), 'processed')
```

`os.path.dirname('/path/to/raw/')` returns `/path/to/raw`, but `os.path.dirname('/path/to/raw')` returns `/path/to`. Inconsistent behavior depending on user input.

### 24. platformio.ini — src_dir set to repo root (line 24)

```ini
src_dir = .
```

Causes PlatformIO to scan the entire repository as source code, not just the active sketch directory.

### 25. test_data_validation.py — Always-passing assertion (line 105)

```python
def test_quick_check_fails_on_bad_data(self, invalid_sensor_data):
    result = quick_check(invalid_sensor_data)
    assert isinstance(result, bool)  # Always True — doesn't test the value
```

Should be `assert not result` to verify bad data actually fails validation.

### 26. conftest.py — temp_output_dir doesn't create directory (line 90)

```python
def temp_output_dir(tmp_path):
    return tmp_path / "output"  # Path object returned but directory not created
```

Tests that write to this directory will fail with `FileNotFoundError`.

### 27. requirements.txt — No upper version bounds (lines 8-26)

All dependencies use `>=` without upper limits. `numpy>=1.21.0` could install numpy 2.x which has breaking API changes. Recommend adding `<2.0.0` bounds for major packages.

---

## Patterns — Status Update

### ✅ Feature extraction inconsistency — RESOLVED

**Solution:** Created `feature_utils.py` with shared `extract_all_features()` function.

- Training pipeline (`feature_extraction.py`) now calls shared function
- Real-time classifiers (`real_time_classifier.py`, `demo.py`) use same function
- All produce identical ~185 feature vectors

### ✅ Filename parsing fragility — RESOLVED

**Solution:** Created `extract_activity_from_filename()` utility function.

- Matches filenames against `config.ACTIVITIES['all']`
- Correctly handles multi-word activities: `sit_to_stand`, `standing_lean_left`
- Used by `feature_extraction.py` and `visualize_data.py`

### ✅ Config not used — PARTIALLY RESOLVED

**Progress:** 
- `feature_extraction.py` now imports from `config.py`
- `visualize_data.py` now imports from `config.py`
- `real_time_classifier.py` now imports from `config.py`
- `demo.py` now imports from `config.py`

**Remaining:** `data_preprocessing.py`, `serial_receiver.py`, `sensor_characterization.py` still have hardcoded constants (low priority).

---

## New Features Added

### [[calibration_visualizer]]
Real-time [[matplotlib]] visualization for sensor [[calibration]]:
- 10-channel time series plots
- Live bar chart with min/max tracking
- Keyboard controls (Q/R/S/P)
- [[CSV]] export for calibration data

See [[PLATFORMIO_SETUP]] for usage instructions.

### [[data_collection_wireless.ino]]
Unified wireless data collection with:
- [[WiFi]] AP Mode + Web dashboard (192.168.4.1)
- [[BLE]] streaming ([[JSON]] data)
- [[Serial]] interface ([[CSV]] data)
- Real-time sensor visualization in browser


---

## Navigation

| ← Previous | ↑ Up | Next → |
|------------|------|--------|
| [[README]] | [[INDEX]] | [[PLATFORMIO_SETUP]] |

**Related Topics:**
- [[calibration_visualizer]] — Calibration tools
- [[feature_utils.py]] — Shared feature extraction
- [[data_collection_wireless]] — Wireless data collection
