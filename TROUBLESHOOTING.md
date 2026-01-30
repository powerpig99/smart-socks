# Smart Socks Troubleshooting Guide

**ELEC-E7840 Smart Wearables — Aalto University**

---

## Quick Diagnostics

Run the diagnostic tool first:

```bash
cd 04_Code/python/
python quick_test.py --port /dev/ttyUSB0
```

This checks:
- Serial connection
- Sensor readings
- Data quality
- ML pipeline components

---

## Hardware Issues

### ESP32 Not Detected

**Symptom:** `Error: [Errno 2] could not open port /dev/ttyUSB0`

**Solutions:**
1. Check USB cable (use data cable, not charging-only)
2. Verify port name:
   ```bash
   # Linux/Mac
   ls /dev/ttyUSB* /dev/ttyACM*
   
   # Windows
   Get-PnpDevice -Class Ports
   ```
3. Fix permissions:
   ```bash
   sudo usermod -a -G dialout $USER
   # Log out and back in
   ```
4. Install CH340/CP210x drivers (if needed)

---

### Sensors Not Responding

**Symptom:** Constant values or no change with pressure

**Diagnosis:**
```bash
python quick_test.py --port /dev/ttyUSB0
```

**Solutions:**

| Issue | Check | Fix |
|-------|-------|-----|
| Stuck at ~0 | Wiring | Check GND connection |
| Stuck at ~4095 | Short circuit | Check for solder bridges |
| Noisy/erratic | Loose connection | Re-solder or check breadboard |
| Intermittent | Wire quality | Use shorter, shielded wires |

**Specific Checks:**
1. Verify voltage divider: 10kΩ resistor between signal and GND
2. Check piezoresistive fabric continuity with multimeter
3. Verify ESP32 pin assignments match code

---

### High Dropout Rate

**Symptom:** Missing samples, gaps in timestamp

**Causes & Solutions:**

1. **USB Power Issues**
   - Use powered USB hub
   - Try different USB port
   - Check cable quality

2. **Baud Rate Mismatch**
   - Ensure 115200 baud in both code and connection

3. **Processing Delays**
   - Reduce sample rate temporarily (25 Hz)
   - Check computer isn't overloaded

4. **Long Wires**
   - Keep sensor wires < 30cm
   - Use shielded cable for longer runs

---

## Software Issues

### Import Errors

**Symptom:** `ModuleNotFoundError: No module named 'sklearn'`

**Solution:**
```bash
cd 04_Code/python/
pip install -r requirements.txt
```

**Symptom:** `ModuleNotFoundError: No module named 'config'`

**Solution:**
```bash
# Run from correct directory
cd 04_Code/python/
python your_script.py
```

---

### Arduino IDE ESP32 Installation Timeout

**Symptom:** `Error: 4 DEADLINE_EXCEEDED` when installing ESP32 board package

**Root Cause:** The ESP32 package is ~500MB and downloads slowly from GitHub. Arduino IDE's default timeout is too short.

**Solutions:**

**Option 1: Manual Installation (Foolproof)**
```bash
# 1. Download directly from GitHub releases
# https://github.com/espressif/arduino-esp32/releases/download/3.3.5/esp32-3.3.5.zip

# 2. Extract to Arduino packages folder (macOS example)
mkdir -p ~/Library/Arduino15/packages/esp32/hardware/esp32/3.3.5
unzip ~/Downloads/esp32-3.3.5.zip -d ~/Library/Arduino15/packages/esp32/hardware/esp32/3.3.5

# 3. Fix nested folder structure
mv ~/Library/Arduino15/packages/esp32/hardware/esp32/3.3.5/esp32-3.3.5/* \
   ~/Library/Arduino15/packages/esp32/hardware/esp32/3.3.5/
rmdir ~/Library/Arduino15/packages/esp32/hardware/esp32/3.3.5/esp32-3.3.5

# 4. Restart Arduino IDE
```

**Option 2: Use Older Version (Smaller Download)**
- Version 2.0.17 = ~200MB (vs 3.3.5 = ~500MB)
- Install via Board Manager → Select version 2.0.17 from dropdown

**Option 3: Arduino CLI**
```bash
arduino-cli config set network.timeout 600
arduino-cli core update-index
arduino-cli core install esp32:esp32@3.3.5
```

**Package Paths by Platform:**
| Platform | Path |
|----------|------|
| macOS | `~/Library/Arduino15/packages/esp32/hardware/esp32/3.3.5/` |
| Windows | `%LOCALAPPDATA%\Arduino15\packages\esp32\hardware\esp32\3.3.5\` |
| Linux | `~/.arduino15/packages/esp32/hardware/esp32/3.3.5/` |

See [[ARDUINO_ESP32_INSTALLATION_FAQ]] for complete troubleshooting guide.

---

### Feature Extraction Fails

**Symptom:** `KeyError: 'L_P_Heel'` or missing columns

**Solutions:**
1. Verify CSV has all required columns:
   ```python
   import pandas as pd
   df = pd.read_csv('your_file.csv')
   print(df.columns)
   ```
2. Check data was recorded properly
3. Run validation:
   ```python
   from data_validation import validate_sensor_data
   report = validate_sensor_data(df)
   print(report.summary())
   ```

---

### Model Training Low Accuracy

**Symptom:** Accuracy <70% on validation set

**Diagnostic Steps:**

1. **Check Data Quality**
   ```bash
   python data_preprocessing.py --input ../../03_Data/raw/ --output ../../03_Data/processed/ --report quality.csv
   ```

2. **Verify Cross-Subject Split**
   ```bash
   python train_model.py --features features.csv --output results/ --cross-subject
   ```

3. **Check for Overfitting**
   - Training accuracy >> Validation accuracy
   - Solution: Add more training subjects, reduce model complexity

4. **Inspect Feature Importance**
   - Check `05_Analysis/feature_importance.csv`
   - Ensure pressure ratio features are high-ranked

**Common Causes:**
- [ ] Sensor calibration not done
- [ ] Training/test subjects mixed
- [ ] Insufficient training data (<5 subjects)
- [ ] Stuck sensors in training data

---

### Real-Time Classifier Issues

**Symptom:** Predictions don't match actual activity

**Solutions:**

1. **Check Model Loading**
   ```python
   import joblib
   model = joblib.load('smart_socks_model.joblib')
   print(model.classes_)  # Verify activity labels
   ```

2. **Verify Feature Alignment**
   - Ensure real-time features match training features
   - Check `feature_names` in model metadata

3. **Latency Issues**
   - Expected: <100ms per prediction
   - If slower: Reduce window size or check CPU usage

---

## BLE Connection Issues

### Device Not Found

**Symptom:** Cannot find "SmartSocks" in BLE scan

**Solutions:**
1. Ensure BLE sketch is uploaded (not serial version)
2. Check ESP32 is powered and within range
3. Reset ESP32 (press reset button)
4. Verify UUIDs match:
   - Service: `4fafc201-1fb5-459e-8fcc-c5c9c331914b`
   - Characteristic: `beb5483e-36e1-4688-b7f5-ea07361b26a8`

---

### BLE Disconnects Frequently

**Solutions:**
1. Reduce data rate (change to 25 Hz)
2. Increase BLE connection interval
3. Check power supply (use battery instead of USB if possible)
4. Reduce obstacles between devices

---

## Data Quality Issues

### Stuck Sensors

**Diagnosis:**
```
Warning: L_P_Heel has only 2 unique values
```

**Causes:**
1. Sensor disconnected
2. Sensor saturated (constant max value)
3. Wiring issue

**Fix:**
- Check wiring
- Test sensor resistance with multimeter
- Re-fabricate if sensor is damaged

---

### Timestamps Not Monotonic

**Diagnosis:**
```
ERROR: Timestamps not monotonically increasing
```

**Causes:**
1. ESP32 timer overflow
2. Serial buffer overflow
3. Computer processing delays

**Fix:**
- Restart ESP32
- Check serial buffer size
- Reduce sampling rate

---

### High Dropout Rate

**Diagnosis:**
```
Warning: Dropout rate 35% (threshold: 20%)
```

**Impact:**
- Reduced model accuracy
- Inconsistent window sizes

**Fix:**
- Check USB connection
- Reduce sample rate
- Close other applications
- Use direct USB connection (not through hub)

---

## ML Pipeline Issues

### Feature Extraction Too Slow

**Solutions:**
1. Process files in parallel:
   ```python
   from multiprocessing import Pool
   with Pool(4) as p:
       p.map(process_file, file_list)
   ```

2. Reduce feature set in `config.py`

3. Downsample data before feature extraction

---

### Out of Memory

**Symptom:** `MemoryError` during training

**Solutions:**
1. Process in chunks:
   ```python
   # Read CSV in chunks
   for chunk in pd.read_csv('large_file.csv', chunksize=10000):
       process(chunk)
   ```

2. Reduce number of estimators in Random Forest

3. Use feature selection to reduce dimensionality

---

### Model File Not Found

**Symptom:** `FileNotFoundError: smart_socks_model.joblib`

**Solution:**
```bash
# Train model first
python train_model.py --features ../../03_Data/features/features_all.csv --output ../../05_Analysis/

# Or run full pipeline
python run_full_pipeline.py --raw-data ../../03_Data/raw/ --output ../../05_Analysis/
```

---

## User Study Issues

### WEAR/SUS Forms Incomplete

**Prevention:**
- Use digital forms (Google Forms)
- Have researcher check completeness before participant leaves
- Provide clear instructions

### Participant Discomfort

**Response:**
1. Stop test immediately
2. Remove device
3. Assess for injury
4. Document incident
5. Redesign if needed

---

## Getting Help

### Debug Information to Collect

When reporting an issue, include:

1. **System Info**
   ```python
   import platform, sys
   print(f"Python: {sys.version}")
   print(f"Platform: {platform.platform()}")
   ```

2. **Error Messages**
   - Full traceback
   - Log file (`smart_socks.log`)

3. **Data Sample**
   - First 10 rows of problematic CSV
   - Output of `quick_test.py`

4. **Hardware Setup**
   - ESP32 board version
   - Sensor configuration
   - Wiring diagram/photo

---

## FAQ

### Q: Can I use a different microcontroller?
**A:** Yes, but you'll need to modify the Arduino code for your board's ADC and pin layout.

### Q: What if I don't have all 6 sensors working?
**A:** The code can work with fewer sensors, but accuracy may decrease. Update `SENSORS['names']` in `config.py`.

### Q: Can I increase the sampling rate?
**A:** Yes, but be careful of dropout issues. Test thoroughly at higher rates.

### Q: How do I add a new activity?
**A:** 
1. Add to `ACTIVITIES['all']` in `config.py`
2. Collect training data
3. Retrain model

### Q: What if my accuracy is stuck at ~50%?
**A:** This suggests random guessing. Check:
- Labels are correct in training data
- Features have discriminative power
- No data leakage between train/test

---

## Emergency Procedures

### If Hardware Smokes or Gets Hot
1. Disconnect power immediately
2. Check for short circuits
3. Inspect for damaged components
4. Do not reconnect until issue identified

### If Participant Reports Pain
1. Stop test immediately
2. Remove device
3. Assess injury
4. Seek medical attention if needed
5. Document incident thoroughly

---

## Resources

- **Course Page:** MyCourses
- **ESP32 Documentation:** https://docs.espressif.com/
- **Scikit-learn Help:** https://scikit-learn.org/stable/
- **Project Issues:** Check with team members

---

*Last updated: 2026-01-29*
