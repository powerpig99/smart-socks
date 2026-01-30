# Smart Socks - Edge Impulse Quick Start Guide

**Step-by-step guide to convert Smart Socks to Edge ML**

---

## Prerequisites

### Hardware
- 2x XIAO ESP32S3 (left & right legs)
- 6x sensors (4 pressure + 2 stretch)
- USB-C cables
- Smartphone (for data collection via BLE)

### Software
- [Edge Impulse Studio](https://studio.edgeimpulse.com) account (free)
- Arduino IDE or PlatformIO
- Python 3.x (for data collection)

---

## Phase 1: Setup (15 minutes)

### Step 1: Create Edge Impulse Project

1. Go to [studio.edgeimpulse.com](https://studio.edgeimpulse.com)
2. Click "Create new project"
3. Name: `Smart-Socks-Activity-Detection`
4. Select "Classification" as project type

### Step 2: Install Edge Impulse CLI (optional)

```bash
# macOS/Linux
npm install -g edge-impulse-cli

# Or use web uploader (no install needed)
```

### Step 3: Connect Device

**Option A: Serial Data Forwarder (Recommended for initial testing)**

Upload this sketch to your ESP32:

```cpp
// SmartSocks_EI_DataForwarder.ino
#define EI_CLASSIFIER_SENSORFREQ_HZ 50

void setup() {
    Serial.begin(115200);
    analogReadResolution(12);
    
    Serial.println("Edge Impulse Data Forwarder");
    Serial.println("Format: L_P_Heel,L_P_Ball,L_S_Knee,R_P_Heel,R_P_Ball,R_S_Knee,label");
}

void loop() {
    // Read all 6 sensors
    float l_heel = analogRead(A0) / 4095.0f;
    float l_ball = analogRead(A1) / 4095.0f;
    float l_knee = analogRead(A2) / 4095.0f;
    float r_heel = analogRead(A3) / 4095.0f;
    float r_ball = analogRead(A4) / 4095.0f;
    float r_knee = analogRead(A5) / 4095.0f;
    
    // Send to Edge Impulse
    Serial.print(l_heel, 4); Serial.print(",");
    Serial.print(l_ball, 4); Serial.print(",");
    Serial.print(l_knee, 4); Serial.print(",");
    Serial.print(r_heel, 4); Serial.print(",");
    Serial.print(r_ball, 4); Serial.print(",");
    Serial.print(r_knee, 4); Serial.print(",");
    Serial.println("walking");  // Change label during collection
    
    delay(20);  // 50Hz
}
```

**Option B: BLE Data Collection (Better for mobile)**

Use the Edge Impulse mobile app:
1. Install "Edge Impulse" app on phone
2. Pair with ESP32 via BLE
3. Collect data wirelessly

---

## Phase 2: Data Collection (1-2 hours)

### Step 4: Define Data Sources

In Edge Impulse Studio:
1. Go to **Data acquisition**
2. Click **Record new data**
3. Select **Accelerometer** (we'll repurpose for analog sensors)
4. Set:
   - Sample length: 10000 ms (10 seconds)
   - Sample frequency: 50 Hz
   - Axis: 6 (one per sensor)

### Step 5: Record Training Data

Record 10-20 samples per activity:

| Activity | Samples | Duration Each |
|----------|---------|---------------|
| Walking | 15 | 10 seconds |
| Stairs Up | 15 | 10 seconds |
| Stairs Down | 15 | 10 seconds |
| Sitting | 10 | 10 seconds |
| Standing | 10 | 10 seconds |

**Tips:**
- Perform activity naturally
- Include transitions (start/stop)
- Vary speed/intensity
- Record in different shoes if possible

### Step 6: Label Data

1. Click on each sample
2. Draw bounding boxes around activity segments
3. Label: `walking`, `stairs_up`, `stairs_down`, `sitting`, `standing`
4. Split: 80% training, 20% testing (auto-split)

---

## Phase 3: Impulse Design (30 minutes)

### Step 7: Create Impulse

Go to **Impulse design** → **Create impulse**

```
┌─────────────────────────────────────────┐
│  Input Block: Time series data          │
│  • Window size: 2000 ms (2 seconds)     │
│  • Window increase: 200 ms              │
│  • Frequency: 50 Hz                     │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  Processing Block: Spectral Features    │
│  • FFT length: 32                       │
│  • Scale: 0.1                           │
│  • Axis: 6 (all sensors)                │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  Learning Block: Classification         │
│  • Neural Network (default)             │
│  • Or: K-means anomaly detection        │
└─────────────────────────────────────────┘
```

### Step 8: Configure Spectral Features

Click **Spectral features** → **Generate features**

Parameters:
- **FFT length**: 32
- **Scale axes**: 0.1 (normalize)
- **Filter**: Low-pass at 25Hz

**Expected output**: ~126 features (21 per sensor × 6 sensors)

### Step 9: Configure Neural Network

Click **NN Classifier** → **Start training**

**Architecture (Expert Mode):**
```python
# Copy this into Expert Mode
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout

model = Sequential([
    Dense(60, activation='relu', input_shape=(input_length,)),
    Dropout(0.3),
    Dense(30, activation='relu'),
    Dropout(0.2),
    Dense(15, activation='relu'),
    Dense(classes, activation='softmax')
])

model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Train
model.fit(train_dataset, epochs=30, validation_data=validation_dataset)
```

**Training settings:**
- Epochs: 30-50
- Learning rate: 0.0005
- Batch size: 32
- Data augmentation: Enabled

---

## Phase 4: Model Testing (15 minutes)

### Step 10: Model Validation

1. Go to **Model testing**
2. Click **Classify all**
3. Check confusion matrix
4. Target: >90% accuracy

### Step 11: Live Classification

1. Connect ESP32 via serial
2. Go to **Live classification**
3. Click **Start sampling**
4. Walk around and see real-time predictions!

---

## Phase 5: Deployment (20 minutes)

### Step 12: Build Arduino Library

1. Go to **Deployment**
2. Select **Arduino library**
3. Choose **Quantized (Int8)**
4. Click **Build**
5. Download `.zip` file

### Step 13: Deploy to ESP32

**In Arduino IDE:**
1. Sketch → Include Library → Add .ZIP Library
2. Select downloaded file
3. Open example: File → Examples → Smart_Socks_inferencing → static_buffer

**Modify the example:**
```cpp
#include <Smart_Socks_inferencing.h>

void setup() {
    Serial.begin(115200);
    analogReadResolution(12);
    
    Serial.println("Smart Socks - Edge ML");
    
    if (EI_CLASSIFIER_RAW_SAMPLES_PER_FRAME != 6) {
        Serial.println("Error: Model expects 6 sensors!");
        return;
    }
}

void loop() {
    // Allocate buffer
    float buffer[EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE];
    
    // Collect 2 seconds of data
    for (size_t i = 0; i < EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE; 
         i += EI_CLASSIFIER_RAW_SAMPLES_PER_FRAME) {
        
        buffer[i + 0] = analogRead(A0) / 4095.0f;
        buffer[i + 1] = analogRead(A1) / 4095.0f;
        buffer[i + 2] = analogRead(A2) / 4095.0f;
        buffer[i + 3] = analogRead(A3) / 4095.0f;
        buffer[i + 4] = analogRead(A4) / 4095.0f;
        buffer[i + 5] = analogRead(A5) / 4095.0f;
        
        delay(20);  // 50Hz
    }
    
    // Run inference
    signal_t signal;
    numpy::signal_from_buffer(buffer, EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE, &signal);
    
    ei_impulse_result_t result;
    EI_IMPULSE_ERROR err = run_classifier(&signal, &result, false);
    
    if (err == EI_IMPULSE_OK) {
        // Print results
        Serial.print("Predicted: ");
        Serial.print(result.classification[0].label);
        Serial.print(" (");
        Serial.print(result.classification[0].value * 100);
        Serial.println("%)");
        
        // LED feedback (optional)
        if (result.classification[0].value > 0.8) {
            digitalWrite(LED_BUILTIN, HIGH);
        } else {
            digitalWrite(LED_BUILTIN, LOW);
        }
    }
}
```

### Step 14: Test Standalone

1. Upload code to ESP32
2. Disconnect USB
3. Power with battery
4. Walk and observe predictions!

---

## Troubleshooting

### Issue: Low accuracy
**Solutions:**
- Collect more training data
- Check sensor calibration
- Verify window size matches activity duration
- Try different FFT lengths

### Issue: High latency
**Solutions:**
- Reduce FFT length (32 → 16)
- Reduce hidden layer size
- Enable EON Compiler (TFLite Micro)

### Issue: Out of memory
**Solutions:**
- Reduce model size (fewer neurons)
- Disable debug output
- Use quantized model (Int8)

---

## Next Steps

### Improvements
1. **Add anomaly detection** for unknown activities
2. **Implement continuous learning** (update model on-device)
3. **Add step counting** using peak detection
4. **Create mobile app** for visualization

### Research Questions
1. How does accuracy compare to scikit-learn Random Forest?
2. What's the power consumption during inference?
3. Can we do cross-subject generalization?

---

## Resources

- [Edge Impulse Docs](https://docs.edgeimpulse.com)
- [XIAO ESP32S3 Guide](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/)
- [TinyML Book](https://www.oreilly.com/library/view/tinyml/9781492052036/)

---

**Time to first working model: ~2-3 hours**

Good luck! 🚀
