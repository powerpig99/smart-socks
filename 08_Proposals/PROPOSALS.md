# Smart Socks - Proposed Improvements

**Status:** Design Phase — Not Yet Implemented  
**Created:** January 31, 2026  
**Purpose:** Explore enhancements without modifying existing codebase

---

## Table of Contents

1. [Feature Importance Analysis for Edge ML](#1-feature-importance-analysis)
2. [Unknown Class Detection / Anomaly Rejection](#2-unknown-class-detection)
3. [Web Dashboard Build-Time Embedding](#3-web-dashboard-embedding)
4. [Cross-Sensor Validation](#4-cross-sensor-validation)
5. [CI/CD for Firmware](#5-cicd-for-firmware)
6. [Automated Data Validation Pipeline](#6-automated-data-validation)

---

## 1. Feature Importance Analysis

### Current State
- ~100 features extracted per window
- No analysis of which features actually contribute to classification
- Edge deployment will carry unnecessary computational overhead

### Proposal
Implement feature importance analysis to identify the minimal viable feature set for edge deployment.

### Implementation Approach

```python
# proposals/feature_importance.py
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def analyze_feature_importance(model, feature_names, top_n=20):
    """
    Analyze and visualize feature importance from trained Random Forest.
    
    Returns:
        - Sorted list of (feature_name, importance_score)
        - Cumulative importance curve
        - Recommendation for minimal feature set
    """
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    # Calculate cumulative importance
    cumulative = np.cumsum(importances[indices])
    
    # Find feature count for 95% cumulative importance
    n_95 = np.argmax(cumulative >= 0.95) + 1
    
    results = {
        'top_features': [(feature_names[i], importances[i]) 
                        for i in indices[:top_n]],
        'n_for_95_percent': n_95,
        'features_95': [feature_names[i] for i in indices[:n_95]],
        'cumulative_curve': cumulative
    }
    
    return results

def generate_edge_feature_config(importance_results, output_path):
    """
    Generate a reduced feature configuration for edge deployment.
    
    This creates a new config file with only the essential features,
    reducing memory and computation requirements on ESP32.
    """
    essential_features = importance_results['features_95']
    
    config = {
        'edge_features': essential_features,
        'feature_count_reduction': {
            'original': len(importance_results['cumulative_curve']),
            'edge': len(essential_features),
            'reduction_percent': (1 - len(essential_features) / 
                                 len(importance_results['cumulative_curve'])) * 100
        },
        'expected_accuracy_retention': '95%+ of full model'
    }
    
    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    return config
```

### Expected Outcome
- Reduce from ~100 features to ~15-25 essential features
- 60-75% reduction in computation time for edge inference
- Minimal accuracy loss (< 2%)
- Smaller model size for TinyML deployment

### Files to Create
- `08_Proposals/feature_importance/feature_importance.py`
- `08_Proposals/feature_importance/edge_config_template.json`
- `08_Proposals/feature_importance/README.md`

---

## 2. Unknown Class Detection

### Current State
- Config has 'unknown' class defined but no implementation
- Model forced to classify everything as one of target activities
- Critical failure mode: jumping classified as "walking"

### Proposal
Implement two-tier rejection system: confidence thresholding + novelty detection.

### Implementation Approach

#### Option A: Confidence Threshold (Simple)
```python
# proposals/unknown_class/confidence_threshold.py

class RejectingClassifier:
    """
    Wrapper that adds rejection capability to any sklearn classifier.
    """
    def __init__(self, base_model, threshold=0.6):
        self.base_model = base_model
        self.threshold = threshold
        self.classes_ = list(base_model.classes_) + ['unknown']
    
    def predict(self, X):
        probs = self.base_model.predict_proba(X)
        max_probs = np.max(probs, axis=1)
        predictions = self.base_model.predict(X)
        
        # Reject low-confidence predictions
        rejected = max_probs < self.threshold
        result = predictions.copy()
        result[rejected] = 'unknown'
        
        return result
    
    def predict_proba(self, X):
        """Returns probability including unknown class."""
        base_probs = self.base_model.predict_proba(X)
        max_probs = np.max(base_probs, axis=1)
        
        # Add unknown class probability
        unknown_prob = np.maximum(0, self.threshold - max_probs)
        adjusted_probs = base_probs * (1 - unknown_prob[:, np.newaxis])
        
        return np.column_stack([adjusted_probs, unknown_prob])
```

#### Option B: Novelty Detection (Robust)
```python
# proposals/unknown_class/novelty_detection.py
from sklearn.svm import OneClassSVM
from sklearn.ensemble import IsolationForest

class NoveltyAwareClassifier:
    """
    Two-stage classification: novelty detection → classification.
    """
    def __init__(self, classifier, novelty_detector):
        self.classifier = classifier
        self.novelty_detector = novelty_detector
    
    def fit(self, X_target, y_target):
        """
        Fit on target activities only.
        Novelty detector learns "normal" data distribution.
        """
        self.classifier.fit(X_target, y_target)
        self.novelty_detector.fit(X_target)
    
    def predict(self, X):
        # Stage 1: Check if sample is "known" or "novel"
        is_known = self.novelty_detector.predict(X) == 1
        
        # Stage 2: Classify known samples
        predictions = np.full(len(X), 'unknown', dtype=object)
        if np.any(is_known):
            predictions[is_known] = self.classifier.predict(X[is_known])
        
        return predictions

# Usage:
# Train on target activities only (no jumping/running data needed)
novelty_detector = IsolationForest(contamination=0.1, random_state=42)
model = NoveltyAwareClassifier(rf_classifier, novelty_detector)
model.fit(X_train, y_train)  # Only walking, stairs, sitting, etc.

# At inference:
prediction = model.predict(X_test)  # Returns 'unknown' for jumping
```

### Data Collection Requirements

```python
# proposals/unknown_class/unknown_activities_protocol.md

## Required "Unknown" Activity Data

Collect 30-60 seconds each:

1. **Jumping**
   - Both legs simultaneously
   - Single leg alternating
   - Small hops vs. high jumps

2. **Running in Place**
   - High cadence
   - Various intensities

3. **Random Leg Movement**
   - Sitting with restless leg syndrome style
   - Standing with shuffling
   - Lying down with leg movement

4. **Stretching**
   - Hamstring stretches
   - Quad stretches
   - Calf raises (slow)

5. **Non-target Activities**
   - Cycling motion (if applicable)
   - Swimming kicks (if tested)
   - Any other leg movements not in target list

## Collection Protocol

```bash
# Example data collection commands
cd 04_Code/python

# Unknown activities
python collector.py --activity jumping --subject S01 --duration 60
python collector.py --activity running_in_place --subject S01 --duration 60
python collector.py --activity random_movement --subject S01 --duration 60
```
```

### Expected Outcome
- Model correctly rejects non-target activities
- No embarrassing misclassifications during demo
- Higher perceived intelligence ("it knows what it doesn't know")

---

## 3. Web Dashboard Build-Time Embedding

### Current State
- 400+ lines of HTML/CSS/JS embedded as C++ raw string literal
- No syntax highlighting, hard to edit, easy to break
- Any change requires recompiling entire firmware

### Proposal
Store web assets as separate files, embed at build time using PlatformIO's build hooks.

### Implementation Approach

```python
# proposals/web_dashboard/embed_web_assets.py
"""
PlatformIO pre-build script to embed web assets.
Add to platformio.ini: extra_scripts = pre:embed_web_assets.py
"""

import os
import gzip
import hashlib

def generate_cpp_header(web_dir, output_file):
    """
    Convert web assets to C++ header with compressed content.
    
    Benefits:
    - Separate files for editing (with syntax highlighting)
    - Gzip compression reduces flash usage
    - Automatic rebuilding when web files change
    """
    assets = {}
    
    for filename in os.listdir(web_dir):
        filepath = os.path.join(web_dir, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'rb') as f:
                content = f.read()
            
            # Compress
            compressed = gzip.compress(content)
            
            # Generate variable name
            var_name = filename.replace('.', '_').replace('-', '_')
            
            assets[var_name] = {
                'original_size': len(content),
                'compressed_size': len(compressed),
                'data': compressed,
                'mime_type': get_mime_type(filename)
            }
    
    # Generate C++ header
    with open(output_file, 'w') as f:
        f.write('// Auto-generated by embed_web_assets.py\n')
        f.write('// Do not edit manually\n\n')
        f.write('#pragma once\n\n')
        f.write('#include <Arduino.h>\n\n')
        
        for var_name, info in assets.items():
            f.write(f'// {var_name}: {info["original_size"]} bytes '
                   f'→ {info["compressed_size"]} bytes (gzipped)\n')
            f.write(f'const uint8_t {var_name}_gz[] PROGMEM = {{\n')
            
            # Write hex values
            for i, byte in enumerate(info['data']):
                if i % 16 == 0:
                    f.write('  ')
                f.write(f'0x{byte:02x}, ')
                if i % 16 == 15:
                    f.write('\n')
            
            f.write('\n};\n\n')
            f.write(f'const size_t {var_name}_gz_len = {info["compressed_size"]};\n\n')
    
    print(f"Generated {output_file}")
    print(f"Total assets: {len(assets)}")
    print(f"Flash savings: {sum(a['original_size'] - a['compressed_size'] for a in assets.values())} bytes")

def get_mime_type(filename):
    """Get MIME type for file extension."""
    mime_types = {
        '.html': 'text/html',
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.json': 'application/json',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.svg': 'image/svg+xml'
    }
    ext = os.path.splitext(filename)[1].lower()
    return mime_types.get(ext, 'application/octet-stream')

if __name__ == '__main__':
    generate_cpp_header('src/web/', 'src/web_assets.h')
```

### Directory Structure

```
src/
├── main.ino              # Clean firmware, includes web_assets.h
├── web/                  # Editable web assets
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── favicon.svg
└── web_assets.h          # Auto-generated, don't edit
```

### PlatformIO Integration

```ini
# platformio.ini additions
extra_scripts = pre:embed_web_assets.py

[env:xiao_esp32s3]
platform = espressif32
board = seeed_xiao_esp32s3
framework = arduino
lib_deps = 
    me-no-dev/AsyncTCP @ ^1.1.1
    me-no-dev/ESP Async WebServer @ ^1.2.3
```

### ESP32 Serving Code

```cpp
// proposals/web_dashboard/serve_compressed.cpp

#include <ESPAsyncWebServer.h>
#include <web_assets.h>  // Auto-generated
#include <zlib.h>        // For decompression

AsyncWebServer server(80);

void setupWebServer() {
    // Main page - serve decompressed index.html
    server.on("/", HTTP_GET, [](AsyncWebServerRequest *request) {
        AsyncWebServerResponse *response = request->beginResponse(
            200, "text/html", index_html_gz, index_html_gz_len
        );
        response->addHeader("Content-Encoding", "gzip");
        request->send(response);
    });
    
    // CSS
    server.on("/style.css", HTTP_GET, [](AsyncWebServerRequest *request) {
        AsyncWebServerResponse *response = request->beginResponse(
            200, "text/css", style_css_gz, style_css_gz_len
        );
        response->addHeader("Content-Encoding", "gzip");
        request->send(response);
    });
    
    // JavaScript
    server.on("/app.js", HTTP_GET, [](AsyncWebServerRequest *request) {
        AsyncWebServerResponse *response = request->beginResponse(
            200, "application/javascript", app_js_gz, app_js_gz_len
        );
        response->addHeader("Content-Encoding", "gzip");
        request->send(response);
    });
    
    server.begin();
}
```

### Expected Outcome
- Edit web files with full IDE support (syntax highlighting, linting)
- Automatic recompilation when web files change
- Smaller binary (gzip compression typically 60-70% savings)
- Cleaner firmware code (no 400-line string literals)

---

## 4. Cross-Sensor Validation

### Current State
- Data validation checks individual sensors (stuck, saturated, disconnected)
- No validation of sensor-to-sensor relationships
- Physically impossible combinations not detected

### Proposal
Add cross-sensor consistency checks based on physical constraints.

### Implementation Approach

```python
# proposals/cross_sensor_validation/physical_constraints.py

class PhysicalConstraintValidator:
    """
    Validates sensor data against physical constraints.
    Detects sensor failures by checking for impossible combinations.
    """
    
    CONSTRAINTS = {
        # During walking: if heel has pressure, ball should eventually have pressure
        'walking_heel_ball_sequence': {
            'description': 'Heel strike must be followed by ball contact',
            'check': lambda heel, ball: not (heel > 1000 and max(ball[-10:]) < 100),
            'window': 10  # samples
        },
        
        # Standing: both feet should have roughly equal pressure
        'standing_symmetry': {
            'description': 'Standing should have similar pressure on both feet',
            'check': lambda left, right: 0.5 < left/right < 2.0 if right > 500 else True,
            'threshold': 500
        },
        
        # Knee stretch limits
        'knee_stretch_range': {
            'description': 'Knee stretch sensor should vary with knee angle',
            'check': lambda stretch: 500 < stretch < 3500,
            'valid_range': (500, 3500)
        },
        
        # Cross-leg consistency
        'leg_sync_during_walking': {
            'description': 'During walking, legs should alternate (anti-phase)',
            'check': lambda left, right: np.corrcoef(left, right)[0,1] < 0.3,
            'activity': 'walking'
        }
    }
    
    def validate_window(self, window_df, expected_activity=None):
        """
        Validate a window of sensor data against physical constraints.
        
        Returns:
            ValidationReport with violations detected
        """
        violations = []
        
        # Check heel-ball sequence for walking activities
        if expected_activity in ['walking_forward', 'walking_backward']:
            for leg in ['L', 'R']:
                heel = window_df[f'{leg}_P_Heel'].values
                ball = window_df[f'{leg}_P_Ball'].values
                
                # Look for heel strike without subsequent ball contact
                heel_strikes = np.where(heel > 1000)[0]
                for strike in heel_strikes:
                    if strike + 10 < len(ball):
                        if max(ball[strike:strike+10]) < 100:
                            violations.append({
                                'constraint': 'walking_heel_ball_sequence',
                                'sensor': f'{leg}_P_Ball',
                                'frame': strike,
                                'severity': 'warning',
                                'message': f'{leg} heel strike without ball contact - possible sensor failure'
                            })
        
        # Check standing symmetry
        if expected_activity in ['standing_upright', 'standing_lean_left', 'standing_lean_right']:
            left_total = window_df['L_P_Heel'].mean() + window_df['L_P_Ball'].mean()
            right_total = window_df['R_P_Heel'].mean() + window_df['R_P_Ball'].mean()
            
            if right_total > 500 and not (0.3 < left_total/right_total < 3.0):
                violations.append({
                    'constraint': 'standing_symmetry',
                    'severity': 'error',
                    'message': f'Asymmetric standing: L={left_total:.0f}, R={right_total:.0f}'
                })
        
        return ValidationReport(violations)


@dataclass
class ValidationReport:
    violations: List[Dict]
    
    def is_valid(self):
        return not any(v['severity'] == 'error' for v in self.violations)
    
    def has_warnings(self):
        return any(v['severity'] == 'warning' for v in self.violations)
```

### Integration with Data Collection

```python
# In collector.py, add to data validation:

validator = PhysicalConstraintValidator()

# After collecting a window
report = validator.validate_window(window_df, expected_activity=args.activity)

if not report.is_valid():
    print("⚠️  Physical constraint violations detected:")
    for v in report.violations:
        print(f"  - {v['message']}")
    
    # Option: Auto-reject recording
    if any(v['severity'] == 'error' for v in report.violations):
        print("❌ Recording rejected due to critical violations")
        return
```

### Expected Outcome
- Catch sensor failures during data collection (not after)
- Higher quality training data
- Automatic flagging of "impossible" movements
- Prevents training on corrupted data

---

## 5. CI/CD for Firmware

### Current State
- Manual build and upload process
- No automated testing of firmware changes
- Easy to break build without noticing

### Proposal
GitHub Actions workflow for automated build, test, and release.

### Implementation Approach

```yaml
# proposals/cicd/.github/workflows/firmware.yml

name: Firmware CI

on:
  push:
    paths:
      - 'src/**'
      - '04_Code/arduino/**'
      - 'platformio.ini'
  pull_request:
    paths:
      - 'src/**'
      - '04_Code/arduino/**'

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install PlatformIO
      run: |
        pip install platformio
        pio upgrade
    
    - name: Build firmware (data collection)
      run: |
        cp 04_Code/arduino/data_collection_leg/data_collection_leg.ino src/main.ino
        pio run -e xiao_esp32s3
    
    - name: Build firmware (calibration)
      run: |
        cp 04_Code/arduino/calibration_all_sensors/calibration_all_sensors.ino src/main.ino
        pio run -e calibration
    
    - name: Check code formatting
      run: |
        pip install clang-format
        find src -name "*.ino" -o -name "*.cpp" -o -name "*.h" | \
          xargs clang-format --dry-run --Werror
    
    - name: Upload firmware artifacts
      uses: actions/upload-artifact@v3
      with:
        name: firmware-binaries
        path: |
          .pio/build/xiao_esp32s3/firmware.bin
          .pio/build/xiao_esp32s3/firmware.elf

  size-analysis:
    needs: build
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Download artifacts
      uses: actions/download-artifact@v3
      with:
        name: firmware-binaries
    
    - name: Analyze binary size
      run: |
        echo "## Firmware Size Analysis" >> $GITHUB_STEP_SUMMARY
        echo "| File | Size |" >> $GITHUB_STEP_SUMMARY
        echo "|------|------|" >> $GITHUB_STEP_SUMMARY
        ls -lh *.bin | awk '{print "| " $9 " | " $5 " |"}' >> $GITHUB_STEP_SUMMARY
        
        # Check for size warnings
        SIZE=$(stat -c%s firmware.bin)
        if [ $SIZE -gt 1310720 ]; then  # 1.25MB warning threshold
          echo "⚠️ **Warning:** Firmware size > 1.25MB" >> $GITHUB_STEP_SUMMARY
        fi
```

### Local Pre-Commit Hooks

```bash
# proposals/cicd/.pre-commit-config.yaml

repos:
  - repo: local
    hooks:
      - id: clang-format
        name: Format C++ code
        entry: clang-format -i
        language: system
        files: \.(ino|cpp|h)$
      
      - id: platformio-build
        name: Build firmware
        entry: bash -c 'pio run -e xiao_esp32s3'
        language: system
        files: \.(ino|cpp|h|ini)$
        pass_filenames: false
      
      - id: python-black
        name: Format Python code
        entry: black
        language: system
        files: \.py$
      
      - id: python-flake8
        name: Lint Python code
        entry: flake8
        language: system
        files: \.py$
```

### Expected Outcome
- Every commit automatically tested for build success
- Code formatting enforced consistently
- Binary size tracked over time
- No "works on my machine" issues
- Catch breaking changes before they reach main branch

---

## 6. Automated Data Validation Pipeline

### Current State
- Data validation exists but must be run manually
- No automated rejection of bad recordings
- Quality issues discovered late in pipeline

### Proposal
Integrate validation into data collection workflow with automatic rejection and retry.

### Implementation Approach

```python
# proposals/auto_validation/auto_validator.py

class AutomatedDataValidator:
    """
    Real-time data validation during collection.
    Rejects bad recordings immediately, not after the fact.
    """
    
    def __init__(self):
        self.checks = [
            ('dropout_rate', self.check_dropout, 0.20),
            ('stuck_sensors', self.check_stuck_sensors, 0),
            ('saturated_sensors', self.check_saturation, 0),
            ('temporal_consistency', self.check_temporal_jumps, 3),
            ('physical_constraints', self.check_physical_constraints, None)
        ]
    
    def validate_live(self, buffer, activity_type):
        """
        Validate data during collection (every N samples).
        
        Returns:
            (is_valid, issues_list)
        """
        issues = []
        
        for check_name, check_func, threshold in self.checks:
            result = check_func(buffer, threshold)
            if result:
                issues.append({
                    'check': check_name,
                    'details': result,
                    'severity': 'error' if check_name in ['stuck_sensors', 'saturated_sensors'] else 'warning'
                })
        
        # Physical constraint check
        if activity_type:
            constraint_issues = self.check_physical_constraints(buffer, activity_type)
            if constraint_issues:
                issues.extend(constraint_issues)
        
        is_valid = not any(i['severity'] == 'error' for i in issues)
        return is_valid, issues
    
    def check_temporal_jumps(self, buffer, max_jump=3):
        """
        Check for impossible jumps (electrical noise).
        
        Args:
            max_jump: Maximum allowable ADC change per sample (4095 / 50Hz * max_velocity)
        """
        jumps_detected = []
        
        for sensor in SENSORS['names']:
            values = [b[sensor] for b in buffer]
            diffs = np.diff(values)
            
            # Find jumps larger than threshold
            large_jumps = np.where(np.abs(diffs) > 1000)[0]  # 1000 ADC units in 20ms
            
            if len(large_jumps) > 0:
                jumps_detected.append({
                    'sensor': sensor,
                    'count': len(large_jumps),
                    'max_jump': int(np.max(np.abs(diffs)))
                })
        
        return jumps_detected if jumps_detected else None
    
    def post_collection_validation(self, filepath, activity_type):
        """
        Full validation after collection completes.
        
        Returns:
            ValidationResult with pass/fail and detailed report
        """
        df = pd.read_csv(filepath)
        
        # Run all checks
        report = validate_sensor_data(df, filepath)
        
        # Check duration
        duration_sec = (df['time_ms'].iloc[-1] - df['time_ms'].iloc[0]) / 1000
        if duration_sec < 10:
            report.issues.append(f"Recording too short: {duration_sec:.1f}s (min 10s)")
            report.is_valid = False
        
        # Check sample count
        expected_samples = duration_sec * 50  # 50Hz
        actual_samples = len(df)
        if actual_samples < expected_samples * 0.8:
            report.issues.append(f"Missing samples: {actual_samples}/{int(expected_samples)} expected")
            report.is_valid = False
        
        return report


# Integration with collector.py

def collect_with_validation(args):
    """
    Enhanced collector with real-time validation.
    """
    validator = AutomatedDataValidator()
    buffer = deque(maxlen=250)  # 5 seconds at 50Hz
    
    collector = DataCollector(port=args.port)
    if not collector.connect():
        return False
    
    print(f"Collecting {args.activity}...")
    print("Validating in real-time (Ctrl+C to cancel)\n")
    
    issues_in_window = []
    
    try:
        while True:
            sample = collector.read_sample()
            if sample:
                buffer.append(sample)
                
                # Validate every 5 seconds (250 samples)
                if len(buffer) == 250:
                    is_valid, issues = validator.validate_live(buffer, args.activity)
                    
                    if not is_valid:
                        print("\n❌ Critical issues detected:")
                        for issue in issues:
                            print(f"  - {issue['check']}: {issue['details']}")
                        print("\n⚠️  Recording may be invalid. Continue? (y/n)")
                        response = input().lower()
                        if response != 'y':
                            return False
                    
                    elif issues:
                        # Warnings only
                        if len(issues_in_window) < 3:  # Limit warnings
                            print(f"⚠️  Warnings: {[i['check'] for i in issues]}")
                            issues_in_window.append(issues)
    
    except KeyboardInterrupt:
        print("\n\nStopping collection...")
    
    # Post-collection validation
    filepath = collector.save_recording(args.subject, args.activity)
    report = validator.post_collection_validation(filepath, args.activity)
    
    print("\n" + report.summary())
    
    if not report.is_valid:
        print("\n❌ Recording FAILED validation")
        print("Delete file? (y/n): ", end='')
        if input().lower() == 'y':
            os.remove(filepath)
            print(f"Deleted {filepath}")
        return False
    
    print("\n✅ Recording PASSED validation")
    return True
```

### Expected Outcome
- Catch data quality issues during collection, not after
- Reduce bad data entering training set
- Real-time feedback to collector about sensor issues
- Automatic cleanup of failed recordings
- Higher quality training data with less manual review

---

## Summary

| Proposal | Effort | Impact | Priority |
|----------|--------|--------|----------|
| Feature Importance | Low | High (edge ML) | High |
| Unknown Class Detection | Medium | Critical (teacher requirement) | Critical |
| Web Dashboard Embedding | Low | Medium (dev experience) | Low |
| Cross-Sensor Validation | Medium | High (data quality) | Medium |
| CI/CD for Firmware | Low | Medium (reliability) | Low |
| Automated Validation | Medium | High (data quality) | High |

**Recommended Implementation Order:**
1. Unknown Class Detection (required for course)
2. Feature Importance Analysis (benefits Part 3)
3. Automated Validation (improves data quality immediately)
4. Cross-Sensor Validation (catches edge cases)
5. Web Dashboard Embedding (nice to have)
6. CI/CD (team scaling)

---

*Generated by Huyo (Digital Twin) for Smart Socks Project*  
*January 31, 2026*
