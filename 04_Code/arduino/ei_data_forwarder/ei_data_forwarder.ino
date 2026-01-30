/*
 * Smart Socks - Edge Impulse Data Forwarder
 * ELEC-E7840 Smart Wearables (Aalto University)
 *
 * This sketch sends sensor data to Edge Impulse Studio for model training.
 * 
 * Wiring (Calibration Mode - all 6 sensors on one ESP32):
 *   A0: L_P_Heel (Left Heel Pressure)
 *   A1: L_P_Ball (Left Ball Pressure)  
 *   A2: L_S_Knee (Left Knee Stretch)
 *   A3: R_P_Heel (Right Heel Pressure)
 *   A4: R_P_Ball (Right Ball Pressure)
 *   A5: R_S_Knee (Right Knee Stretch)
 *
 * Instructions:
 * 1. Upload this sketch to ESP32
 * 2. Open Serial Monitor (115200 baud)
 * 3. Connect to Edge Impulse Studio via data forwarder
 * 4. Record samples for each activity
 * 5. Train model and deploy!
 */

#include <Arduino.h>

// ============== CONFIGURATION ==============

// Sampling configuration
const int SAMPLE_RATE_HZ = 50;
const int SAMPLE_INTERVAL_MS = 1000 / SAMPLE_RATE_HZ;
const int ADC_RESOLUTION = 12;

// Sensor pins (all 6 sensors for calibration mode)
const int NUM_SENSORS = 6;
const int SENSOR_PINS[] = {A0, A1, A2, A3, A4, A5};
const char* SENSOR_NAMES[] = {
  "L_Heel", "L_Ball", "L_Knee",
  "R_Heel", "R_Ball", "R_Knee"
};

// Data format for Edge Impulse
// CSV format: timestamp,L_Heel,L_Ball,L_Knee,R_Heel,R_Ball,R_Knee

// ============== SETUP ==============

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  
  // Configure ADC
  analogReadResolution(ADC_RESOLUTION);
  analogSetAttenuation(ADC_11db);
  
  // Configure sensor pins
  for (int i = 0; i < NUM_SENSORS; i++) {
    pinMode(SENSOR_PINS[i], INPUT);
  }
  
  // Print header
  Serial.println("============================================");
  Serial.println("Smart Socks - Edge Impulse Data Forwarder");
  Serial.println("============================================");
  Serial.println();
  Serial.println("Sensor Configuration:");
  for (int i = 0; i < NUM_SENSORS; i++) {
    Serial.print("  ");
    Serial.print(SENSOR_NAMES[i]);
    Serial.print(" -> A");
    Serial.println(SENSOR_PINS[i]);
  }
  Serial.println();
  Serial.println("CSV Format: timestamp,L_Heel,L_Ball,L_Knee,R_Heel,R_Ball,R_Knee");
  Serial.println();
  Serial.println("Instructions:");
  Serial.println("1. Connect to Edge Impulse Studio data forwarder");
  Serial.println("2. Set frequency to 50Hz");
  Serial.println("3. Set axes to 6");
  Serial.println("4. Start recording samples");
  Serial.println();
  Serial.println("Starting data stream in 3 seconds...");
  Serial.println();
  
  delay(3000);
}

// ============== LOOP ==============

void loop() {
  static unsigned long lastSample = 0;
  unsigned long now = millis();
  
  if (now - lastSample >= SAMPLE_INTERVAL_MS) {
    lastSample = now;
    
    // Read all sensors
    int values[NUM_SENSORS];
    for (int i = 0; i < NUM_SENSORS; i++) {
      values[i] = analogRead(SENSOR_PINS[i]);
    }
    
    // Send CSV format
    Serial.print(now);
    for (int i = 0; i < NUM_SENSORS; i++) {
      Serial.print(",");
      Serial.print(values[i]);
    }
    Serial.println();
  }
}

/*
 * Edge Impulse Studio Connection Instructions:
 * 
 * Method 1: Serial Data Forwarder
 * 1. Install Edge Impulse CLI:
 *    npm install -g edge-impulse-cli
 * 
 * 2. Run data forwarder:
 *    edge-impulse-data-forwarder --frequency 50 --axes L_Heel,L_Ball,L_Knee,R_Heel,R_Ball,R_Knee
 * 
 * 3. Follow prompts to connect to your project
 * 
 * Method 2: Web Uploader (no CLI needed)
 * 1. Go to studio.edgeimpulse.com
 * 2. Data Acquisition -> Upload
 * 3. Record data via Serial Monitor, save to CSV, upload
 * 
 * Data Collection Tips:
 * - Record 10-20 samples per activity
 * - Each sample: 10-30 seconds
 * - Activities: walking, stairs_up, stairs_down, sitting, standing
 * - Vary speed and intensity
 * - Include natural movements
 */
