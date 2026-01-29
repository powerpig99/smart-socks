# Smart Socks Project Review
## Gap Analysis & Improvement Recommendations

**Date:** 2026-01-29  
**Project:** ELEC-E7840 Smart Wearables — Topic 3

---

## Executive Summary

The project has a solid foundation with complete ML pipeline implementation. However, several gaps have been identified that could impact robustness, maintainability, and grading outcomes. This review categorizes issues by severity and provides actionable recommendations.

**Overall Assessment:** 🟡 Good foundation with room for improvement

| Category | Status |
|----------|--------|
| Core ML Pipeline | ✅ Strong |
| Embedded Systems | 🟡 Adequate |
| Testing & QA | 🔴 Needs Work |
| Documentation | 🟡 Adequate |
| Configuration Mgmt | 🔴 Missing |
| Error Handling | 🟡 Basic |

---

## 🔴 Critical Issues (Must Fix)

### 1. Empty Design & Fabrication Folders

**Issue:** `01_Design/`, `02_Fabrication/`, and `07_References/` are empty.

**Impact:** 
- Missing sensor placement diagrams for report
- No circuit schematics for deliverables
- No build documentation for reproducibility

**Recommendations:**
- [ ] Create sensor placement diagram showing 5 zones per sock
- [ ] Draw circuit schematic (ESP32S3 + voltage dividers)
- [ ] Document wiring harness design
- [ ] Add step-by-step fabrication guide with photos
- [ ] Create BOM (Bill of Materials)

**Priority:** HIGH — Required for final presentation

---

### 2. No Configuration Management

**Issue:** Hardcoded values scattered across Python files.

**Examples:**
```python
# In feature_extraction.py (and 6 other files)
SENSOR_NAMES = [...]  # Duplicated 8 times
WINDOW_SIZE_MS = 1000  # Duplicated 5 times
SAMPLE_RATE_HZ = 50  # Duplicated 6 times
```

**Impact:**
- Difficult to change parameters consistently
- High risk of inconsistencies
- Tedious to modify for different setups

**Recommendations:**
- [ ] Create `config.py` with all constants
- [ ] Use YAML/JSON for runtime configuration
- [ ] Document all tunable parameters

**Implementation:**
```python
# config.py
SENSOR_CONFIG = {
    'names': ["L_Heel", "L_Arch", ...],
    'count': 10,
    'sample_rate_hz': 50,
    'adc_resolution': 12,
}

WINDOW_CONFIG = {
    'size_ms': 1000,
    'stride_ms': 500,
    'min_samples_ratio': 0.8,
}
```

---

### 3. Missing Unit & Integration Tests

**Issue:** No automated testing for any Python scripts.

**Impact:**
- Bugs may go unnoticed until demo day
- Refactoring is risky
- No regression protection

**Recommendations:**
- [ ] Create `tests/` directory with pytest
- [ ] Unit tests for feature extraction
- [ ] Integration tests for full pipeline
- [ ] Mock data generator for testing

**Test Coverage Needed:**
```
tests/
├── __init__.py
├── conftest.py
├── test_feature_extraction.py
├── test_train_model.py
├── test_data_preprocessing.py
├── fixtures/
│   ├── sample_sensor_data.csv
│   └── expected_features.csv
└── integration/
    └── test_full_pipeline.py
```

---

## 🟡 Important Improvements (Should Fix)

### 4. Error Handling Gaps

**Issue:** Several scripts lack robust error handling.

**Examples Found:**

```python
# feature_extraction.py line 246
df = pd.read_csv(filepath)  # No try/except

# real_time_classifier.py
def extract_features_from_buffer(self):
    # Returns None silently on error
```

**Recommendations:**
- [ ] Add try/except blocks for file I/O
- [ ] Validate data format before processing
- [ ] Provide meaningful error messages
- [ ] Add graceful degradation

**Example Fix:**
```python
def load_data(filepath):
    try:
        df = pd.read_csv(filepath)
        validate_columns(df)  # Check required columns exist
        validate_data_quality(df)  # Check for NaN, infinities
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        raise
    except pd.errors.EmptyDataError:
        logger.error(f"Empty file: {filepath}")
        raise
    except ValidationError as e:
        logger.error(f"Data validation failed: {e}")
        raise
```

---

### 5. Logging Inconsistency

**Issue:** Mix of `print()` statements, no structured logging.

**Impact:**
- Hard to debug issues
- No log files for post-analysis
- Inconsistent output format

**Recommendations:**
- [ ] Use Python `logging` module throughout
- [ ] Add verbose/quiet modes
- [ ] Write logs to file for debugging
- [ ] Add timestamps and log levels

**Implementation:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('smart_socks.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
```

---

### 6. Data Validation Missing

**Issue:** No validation that sensor data is within expected ranges.

**Checks Needed:**
- [ ] ADC values in valid range (0-4095 for 12-bit)
- [ ] Timestamps are monotonically increasing
- [ ] No duplicate timestamps
- [ ] Sensor values not stuck (constant)

**Implementation:**
```python
def validate_sensor_data(df):
    """Validate sensor data meets quality standards."""
    issues = []
    
    # Check ADC range
    for col in SENSOR_NAMES:
        if (df[col] < 0).any() or (df[col] > 4095).any():
            issues.append(f"{col}: values out of ADC range")
    
    # Check timestamp monotonicity
    if not df['time_ms'].is_monotonic_increasing:
        issues.append("Timestamps not monotonically increasing")
    
    # Check for stuck sensors
    for col in SENSOR_NAMES:
        if df[col].nunique() < 5:
            issues.append(f"{col}: possible stuck sensor")
    
    return issues
```

---

### 7. Real-Time Classifier Limitations

**Issue:** `real_time_classifier.py` has several gaps.

**Problems:**
1. Feature extraction duplicates code from `feature_extraction.py`
2. No feature name alignment check with training
3. Step counting algorithm is very basic
4. No recording capability for live data

**Recommendations:**
- [ ] Refactor to use shared feature extraction
- [ ] Add feature compatibility check
- [ ] Improve step counting with adaptive threshold
- [ ] Add option to save live predictions to CSV

---

### 8. No Model Versioning

**Issue:** Trained models overwrite previous versions.

**Impact:**
- Cannot compare model iterations
- Risk of losing best model
- No reproducibility

**Recommendations:**
- [ ] Add timestamp to model filenames
- [ ] Save model metadata (training date, accuracy, params)
- [ ] Keep top-N best models
- [ ] Add model comparison script

**Implementation:**
```python
from datetime import datetime

model_name = f"model_{datetime.now():%Y%m%d_%H%M%S}_acc{accuracy:.3f}"
```

---

### 9. Missing Data Augmentation

**Issue:** No strategy for handling limited training data.

**For Activity Recognition:**
- [ ] Add time-shift augmentation
- [ ] Add small noise to sensor values
- [ ] Random window cropping

**Implementation:**
```python
def augment_data(X, y, noise_level=0.01):
    """Add Gaussian noise to training data."""
    X_aug = X + np.random.normal(0, noise_level, X.shape)
    return np.vstack([X, X_aug]), np.concatenate([y, y])
```

---

### 10. BLE Implementation Incomplete

**Issue:** BLE Python client is a placeholder.

**Current State:**
```python
def _connect_ble(self):
    # BLE implementation would go here
    print("BLE connection not fully implemented yet.")
```

**Recommendations:**
- [ ] Complete bleak-based BLE client
- [ ] Handle connection drops gracefully
- [ ] Add BLE data buffering
- [ ] Test with actual ESP32 BLE

---

## 🟢 Nice-to-Have Improvements

### 11. Performance Optimization

**Current Bottlenecks:**
- Feature extraction loads entire file into memory
- No parallel processing for multiple files
- Visualization loads all data at once

**Recommendations:**
- [ ] Add chunked processing for large files
- [ ] Use multiprocessing for batch feature extraction
- [ ] Add progress bars for long operations (partially done)

---

### 12. Visualization Enhancements

**Missing Features:**
- [ ] Interactive plots (Plotly/Bokeh)
- [ ] Real-time visualization dashboard
- [ ] Feature importance interactive explorer
- [ ] Model decision visualization

---

### 13. Documentation Additions

**Gaps:**
- [ ] API documentation for Python modules
- [ ] Troubleshooting guide
- [ ] FAQ for common issues
- [ ] Video tutorial links

---

## 📋 Implementation Priority Matrix

| Issue | Effort | Impact | Priority | Deadline |
|-------|--------|--------|----------|----------|
| Empty design folders | Medium | High | 🔴 P0 | Week 4 |
| Configuration management | Low | High | 🔴 P0 | Week 5 |
| Unit tests | High | High | 🔴 P0 | Week 6 |
| Error handling | Medium | Medium | 🟡 P1 | Week 6 |
| Logging | Low | Medium | 🟡 P1 | Week 5 |
| Data validation | Medium | Medium | 🟡 P1 | Week 5 |
| Model versioning | Low | Low | 🟢 P2 | Week 8 |
| BLE completion | Medium | Medium | 🟡 P1 | Week 7 |
| Data augmentation | Medium | Medium | 🟢 P2 | Week 9 |

---

## 🎯 Quick Wins (Do This Week)

1. **Create config.py** (2 hours)
   - Centralize all constants
   - Reduces maintenance burden

2. **Add basic validation** (3 hours)
   - ADC range checks
   - Stuck sensor detection
   - Prevents bad data from entering pipeline

3. **Setup logging** (2 hours)
   - Replace print statements
   - Add file output
   - Helps with debugging

4. **Fill design folders** (4 hours)
   - Draw circuit schematic
   - Create sensor placement diagram
   - Required for presentation

---

## 🔍 Code Quality Issues

### Duplicated Constants
```bash
# Found in multiple files:
SENSOR_NAMES  # 8 occurrences
WINDOW_SIZE_MS  # 5 occurrences
SAMPLE_RATE_HZ  # 6 occurrences
```

### Import Organization
Some files have unused imports:
- `train_model.py`: imports `pickle` but uses `joblib`
- `real_time_classifier.py`: imports `json` but doesn't use it

### Function Length
Some functions are quite long (>50 lines):
- `extract_statistical_features()`: 47 lines
- `processCommand()` in Arduino: 43 lines

---

## 📊 Testing Checklist

Before mid-term review:
- [ ] All sensors read correctly (quick_test.py passes)
- [ ] BLE connection stable for >5 minutes
- [ ] Data collection saves complete CSV files
- [ ] Feature extraction runs without errors
- [ ] Model trains on sample data
- [ ] Real-time classifier shows predictions

Before final review:
- [ ] Model accuracy >85% on test subjects
- [ ] Step counting error <10%
- [ ] All 11 activities classified correctly
- [ ] User study completed (5+ participants)
- [ ] All deliverables in correct folders

---

## 📝 Recommendations Summary

### Immediate Actions (This Week)
1. Create `04_Code/python/config.py` with all constants
2. Add data validation to preprocessing
3. Fill `01_Design/` with schematics
4. Fix real-time classifier feature alignment

### Short-term (Next 2 Weeks)
1. Implement basic unit tests
2. Add structured logging
3. Complete BLE implementation
4. Create model versioning

### Long-term (Before Final)
1. Add data augmentation
2. Performance optimization
3. Interactive visualizations
4. Comprehensive documentation

---

*Review conducted by: Claude Code*  
*Next review recommended: After mid-term*
