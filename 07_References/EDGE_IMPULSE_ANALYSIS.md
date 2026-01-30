# Smart Socks → Edge Impulse Studio: Deep Dive Analysis

**Feasibility study for converting Smart Socks to a real-time Edge ML project**

Based on:
- XIAO Big Power Small Board - Chapter 4 (TinyML Applications)
- XIAO Reference Design
- Edge Impulse Studio documentation and capabilities
- Hackster.io Edge Impulse projects

---

## Executive Summary

**VERDICT: ✅ HIGHLY FEASIBLE**

Smart Socks is an excellent candidate for Edge Impulse Studio conversion because:
1. **Time-series classification** is a core strength of Edge Impulse
2. **Multiple analog sensors** fit perfectly into the sensor fusion paradigm
3. **XIAO ESP32S3** is officially supported with optimized DSP blocks
4. **Low latency inference** (<10ms) achievable for 6-sensor, 4-class problem

**Estimated Performance:**
- Inference latency: ~5-10ms
- Model size: ~20-50KB
- RAM usage: ~10-20KB
- Accuracy: 90-95% (based on similar motion classification projects)

---

## 1. Edge Impulse Studio Overview

### What is Edge Impulse?
Edge Impulse is the leading **edge machine learning development platform** that enables:
- End-to-end TinyML workflow (data collection → model training → deployment)
- Optimized DSP preprocessing blocks
- Automatic model quantization (Int8)
- One-click Arduino library generation
- Real-time model testing on actual hardware

### Key Features for Smart Socks
| Feature | Smart Socks Application |
|---------|------------------------|
| **Time Series Data** | ✅ Perfect fit - 6 pressure/stretch sensors |
| **Spectral Features Block** | ✅ FFT analysis for periodic motion patterns |
| **Sensor Fusion** | ✅ Combine 6 sensor inputs |
| **Anomaly Detection** | ✅ Optional - detect unusual gait patterns |
| **Live Classification** | ✅ Real-time activity recognition |

---

## 2. Hardware Compatibility Analysis

### XIAO ESP32S3 Specifications
| Spec | Value | Edge Impulse Support |
|------|-------|---------------------|
| MCU | ESP32-S3 @ 240MHz | ✅ Fully supported |
| RAM | 512KB SRAM + 8MB PSRAM | ✅ Excellent for TinyML |
| Flash | 8MB | ✅ Plenty for models |
| ADC | 12-bit, 2 channels | ✅ Analog input supported |
| WiFi/BLE | Built-in | ✅ Data collection via BLE |

### Current Smart Socks Hardware Assessment
```
Current Setup:
├── ESP32S3 XIAO (2x) - ✅ Compatible
├── 6 Analog Sensors (A0-A5)
│   ├── 4x Pressure (piezoresistive)
│   └── 2x Stretch (conductive fabric)
└── Voltage dividers (10kΩ)
```

**Required Changes for Edge Impulse:**
1. **None for hardware** - Current setup is perfect
2. **Add data forwarder** - Stream data to Edge Impulse Studio via BLE/WiFi
3. **Optional: PSRAM usage** - For larger models (if needed)

---

## 3. Proposed Edge Impulse Workflow

### 3.1 Data Collection Phase

**Option A: Edge Impulse Data Forwarder (Recommended)**
```cpp
// Arduino sketch to forward sensor data to Edge Impulse
#include <edge_impulse.h>

void loop() {
    float features[6];
    features[0] = analogRead(A0) / 4095.0f;  // L_P_Heel
    features[1] = analogRead(A1) / 4095.0f;  // L_P_Ball
    features[2] = analogRead(A2) / 4095.0f;  // L_S_Knee
    features[3] = analogRead(A3) / 4095.0f;  // R_P_Heel
    features[4] = analogRead(A4) / 4095.0f;  // R_P_Ball
    features[5] = analogRead(A5) / 4095.0f;  // R_S_Knee
    
    // Send to Edge Impulse Studio via serial/BLE
    ei_printf("%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n",
              features[0], features[1], features[2],
              features[3], features[4], features[5]);
    delay(20);  // 50Hz sampling
}
```

**Option B: CSV Upload**
- Export existing collected data as CSV
- Upload directly to Edge Impulse Studio

### 3.2 Impulse Design (ML Pipeline)

```
┌─────────────────────────────────────────────────────────┐
│                    IMPULSE DESIGN                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐  │
│  │  Input Block │───▶│ Process Block│───▶│Learning  │  │
│  │  (Raw Data)  │    │ (DSP/FFT)    │    │Block     │  │
│  └──────────────┘    └──────────────┘    └──────────┘  │
│        │                    │                  │       │
│        ▼                    ▼                  ▼       │
│  • 6 sensor channels    • Spectral         • Neural    │
│  • 50Hz sampling        • Analysis         • Network   │
│  • 2-second windows     • (FFT)            • Classifier│
│  • 100 samples/win      • 16-64 features   • 4 classes │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Recommended Configuration:**
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Window Size | 2000ms (2s) | Captures full gait cycle |
| Window Increase | 80ms | 50% overlap for smooth transitions |
| Sampling Rate | 50Hz | Current configuration |
| FFT Length | 32-64 points | Balance accuracy vs. latency |
| Features/Axis | 21 (spectral + statistical) | From PDF Chapter 4 |

### 3.3 Processing Block: Spectral Features

From XIAO Big Power Small Board - Chapter 4:

> "The Spectral Analysis block performs DSP, extracting features such as FFT or Wavelets. For continuous time signals, use FFT with length 32-64."

**Feature Extraction Output:**
```
Per Sensor (6 total):
├── Time Domain (3 features)
│   ├── RMS: 1
│   ├── Skewness: 1
│   └── Kurtosis: 1
│
└── Frequency Domain (18 features)
    ├── Spectral Power: 16 (FFT/2)
    ├── Spectral Skewness: 1
    └── Spectral Kurtosis: 1

Total: 21 features × 6 sensors = 126 input features
```

### 3.4 Learning Block: Neural Network

**Recommended Architecture (from PDF):**
```
Input Layer:        126 neurons (6 sensors × 21 features)
    │
    ▼
Hidden Layer 1:     40 neurons (ReLU activation)
    │
    ▼
Hidden Layer 2:     20 neurons (ReLU activation)
    │
    ▼
Output Layer:       4-11 neurons (Softmax)
                    [walking, stairs_up, stairs_down, sitting, standing, ...]
```

**Alternative: Sensor Fusion Architecture**
```
                    ┌─────────────────────────────────────┐
                    │        SENSOR FUSION MODEL          │
                    └─────────────────────────────────────┘
    
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  Left Leg    │  │  Right Leg   │  │   Combined   │
    │  (3 sensors) │  │  (3 sensors) │  │   (6 total)  │
    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
           │                 │                 │
           ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ Conv1D/      │  │ Conv1D/      │  │ Dense        │
    │ Dense Branch │  │ Dense Branch │  │ Layers       │
    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
           │                 │                 │
           └────────┬────────┘                 │
                    │                          │
                    ▼                          ▼
            ┌───────────────────────────────────────┐
            │      Concatenate + Dense Layers       │
            │         → Final Classification        │
            └───────────────────────────────────────┘
```

---

## 4. Activity Classes & Model Complexity

### Current Activities (from config.py)
```python
ACTIVITIES = [
    'walking_forward',
    'walking_backward', 
    'stairs_up',
    'stairs_down',
    'sitting_floor',
    'sitting_crossed',
    'sit_to_stand',
    'stand_to_sit',
    'standing_upright',
    'standing_lean_left',
    'standing_lean_right'
]
```

**Recommendation:** Start with 4-6 core classes
| Priority | Activity | Distinguishability |
|----------|----------|-------------------|
| 1 | Walking | ✅ Very distinct (heel-ball pattern) |
| 2 | Stairs Up | ✅ High knee stretch signature |
| 3 | Stairs Down | ✅ Controlled heel landing |
| 4 | Sitting | ✅ Low pressure, static |
| 5 | Standing | ✅ Equal pressure, static |
| 6 | Transitions | ⚠️ Harder, add later |

---

## 5. Deployment Options

### Option A: Arduino Library (Recommended)
Edge Impulse generates a complete Arduino library:

```cpp
#include <Smart_Socks_inferencing.h>

void loop() {
    // Read sensors
    float features[6];
    features[0] = analogRead(A0) / 4095.0f;
    // ... etc
    
    // Run inference
    ei_impulse_result_t result;
    EI_IMPULSE_ERROR err = run_classifier(features, &result, false);
    
    if (err == EI_IMPULSE_OK) {
        // Get predicted class
        const char* activity = result.classification[0].label;
        float confidence = result.classification[0].value;
        
        Serial.printf("Activity: %s (%.2f%%)\n", activity, confidence * 100);
    }
}
```

**Pros:**
- ✅ Standalone operation (no PC needed)
- ✅ Optimized C++ code
- ✅ Quantized Int8 model (~20KB)
- ✅ Latency: 5-10ms

### Option B: EON Compiler (TFLite Micro)
- Even more optimized than standard Arduino library
- Tighter memory constraints
- Best for production

### Option C: WebAssembly (for testing)
- Test model in browser before deployment

---

## 6. Performance Estimates

### Model Characteristics
| Metric | Estimate | Notes |
|--------|----------|-------|
| Model Size | 15-30KB | Quantized Int8 |
| RAM Usage | 10-20KB | Working memory |
| Inference Time | 5-15ms | At 240MHz |
| Power Consumption | ~50mA | Active inference |
| Battery Life | 8-10 hours | With 500mAh LiPo |

### Accuracy Expectations
| Scenario | Expected Accuracy |
|----------|------------------|
| Same user, same device | 95-98% |
| Same user, different day | 90-95% |
| Different user | 80-85% (needs personalization) |

---

## 7. Implementation Roadmap

### Phase 1: Data Collection (Week 1)
1. Set up Edge Impulse Studio project
2. Deploy data forwarder to ESP32
3. Collect 10-20 minutes per activity class
4. Split: 80% training, 20% testing

### Phase 2: Model Training (Week 1-2)
1. Configure impulse (Spectral Features + NN)
2. Train initial model
3. Iterate on features/model architecture
4. Target: >90% accuracy on validation set

### Phase 3: Deployment & Testing (Week 2)
1. Generate Arduino library
2. Deploy to ESP32
3. Real-world testing
4. Fine-tune thresholds

### Phase 4: Optimization (Week 3)
1. EON Compiler optimization
2. Power consumption optimization
3. Add anomaly detection (optional)

---

## 8. Comparison: Edge Impulse vs. Current Approach

| Aspect | Current (Python/Scikit) | Edge Impulse (TinyML) |
|--------|------------------------|----------------------|
| **Latency** | 50-100ms (PC) | 5-10ms (on-device) |
| **Power** | Requires laptop | ~50mA standalone |
| **Portability** | Needs PC + cables | Fully wearable |
| **Real-time** | Near real-time | True real-time |
| **Cost** | PC required | $10 ESP32 only |
| **Privacy** | Data to PC | Data stays on device |
| **Training** | Easy (scikit-learn) | Studio-based (visual) |
| **Accuracy** | 90-95% | 90-95% (comparable) |

---

## 9. Challenges & Mitigations

### Challenge 1: Limited Training Data
**Problem:** Small dataset may overfit
**Solution:** 
- Use data augmentation in Edge Impulse
- Transfer learning from public motion datasets
- Collect more data incrementally

### Challenge 2: User Variability
**Problem:** Different gait patterns
**Solution:**
- Continuous learning (update model on-device)
- User-specific calibration
- Enroll multiple users in training

### Challenge 3: Battery Life
**Problem:** WiFi + inference drains battery
**Solution:**
- Use BLE for data collection only
- Deep sleep between inferences
- Optimize model size

### Challenge 4: Real-world Noise
**Problem:** Sensor drift, temperature effects
**Solution:**
- Auto-calibration on startup
- Use differential features (ratios)
- Anomaly detection for outliers

---

## 10. Recommended Next Steps

### Immediate Actions
1. ✅ **Create Edge Impulse account** (free)
2. ✅ **Install data forwarder** on one ESP32
3. ✅ **Collect initial dataset** (2-3 activities)
4. ✅ **Train proof-of-concept model**

### For Demo/Demonstration
1. Deploy standalone Arduino library
2. Add LED feedback (activity indicator)
3. Add buzzer for step counting
4. Create mobile app (optional)

### For Research/Publication
1. Compare Edge Impulse vs. scikit-learn accuracy
2. Measure actual power consumption
3. Test cross-subject generalization
4. Publish TinyML workflow

---

## 11. Useful Resources

### Edge Impulse Documentation
- [XIAO ESP32S3 Sense Official Guide](https://docs.edgeimpulse.com/hardware/boards/seeed-xiao-esp32s3-sense)
- [Sensor Fusion Tutorial](https://www.edgeimpulse.com/blog/sensor-fusion-with-machine-learning-on-edge-impulse/)
- [Spectral Features Block](https://docs.edgeimpulse.com/docs/edge-impulse-studio/processing-blocks/spectral-features)

### Reference Projects
- [Motion Classification (XIAO nRF52840)](https://docs.edgeimpulse.com/experts/hackster-io-contest-2021/predictive-maintenance-pallets-transport)
- [Keyword Spotting (XIAO ESP32S3)](https://wiki.seeedstudio.com/xiao_esp32s3_keyword_spotting/)

### Community
- Edge Impulse Forum: https://forum.edgeimpulse.com/
- Seeed Studio Discord: https://discord.gg/seeed

---

## Conclusion

**Smart Socks + Edge Impulse Studio = Perfect Match**

The combination of:
- ✅ Well-defined time-series classification problem
- ✅ Optimized XIAO ESP32S3 hardware
- ✅ Mature Edge Impulse tooling
- ✅ Clear path to standalone deployment

...makes this an ideal TinyML project for research, education, and practical deployment.

**Estimated Time to Working Demo:** 1-2 weeks

---

*Analysis completed: February 2026*
*Based on XIAO Big Power Small Board Chapter 4 and Edge Impulse documentation*
