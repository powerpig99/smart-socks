/*
 * Smart Socks - Sensor Test Sketch
 * ELEC-E7840 Smart Wearables (Aalto University)
 *
 * Basic ESP32S3 ADC reading for sensor characterization.
 * Tests individual piezoresistive fabric sensors through voltage dividers.
 *
 * Hardware: ESP32S3 XIAO with 10kΩ voltage dividers
 * Sensors: 5 zones per sock (Heel, Arch, Metatarsal medial/lateral, Toe)
 */

#include <Arduino.h>

// Sensor pin definitions - Left sock (A0-A4 = GPIO 1-5)
const int L_HEEL = A0;      // GPIO 1
const int L_ARCH = A1;      // GPIO 2
const int L_META_MED = A2;  // GPIO 3
const int L_META_LAT = A3;  // GPIO 4
const int L_TOE = A4;       // GPIO 5

// Sensor pin definitions - Right sock (A5 = GPIO 6, GPIO 7-10 for remainder)
const int R_HEEL = A5;      // GPIO 6
const int R_ARCH = 7;       // GPIO 7 (D8/SDA pin)
const int R_META_MED = 8;   // GPIO 8 (D9/SCL pin)
const int R_META_LAT = 9;   // GPIO 9 (D10/MOSI pin)
const int R_TOE = 10;       // GPIO 10

// All sensor pins in array for easy iteration
const int SENSOR_PINS[] = {
  L_HEEL, L_ARCH, L_META_MED, L_META_LAT, L_TOE,
  R_HEEL, R_ARCH, R_META_MED, R_META_LAT, R_TOE
};
const int NUM_SENSORS = 10;

// Sensor names for debug output
const char* SENSOR_NAMES[] = {
  "L_Heel", "L_Arch", "L_MetaM", "L_MetaL", "L_Toe",
  "R_Heel", "R_Arch", "R_MetaM", "R_MetaL", "R_Toe"
};

// Sampling configuration
const int SAMPLE_RATE_HZ = 50;
const int SAMPLE_INTERVAL_MS = 1000 / SAMPLE_RATE_HZ;

// ADC configuration
const int ADC_RESOLUTION = 12;  // 12-bit ADC (0-4095)

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    delay(10);  // Wait for serial connection
  }

  // Configure ADC
  analogReadResolution(ADC_RESOLUTION);
  analogSetAttenuation(ADC_11db);  // 0-3.3V range for 10kΩ voltage dividers

  // Configure sensor pins as inputs
  for (int i = 0; i < NUM_SENSORS; i++) {
    pinMode(SENSOR_PINS[i], INPUT);
  }

  Serial.println("Smart Socks Sensor Test");
  Serial.println("=======================");
  Serial.println("Place known weights on sensors for characterization.");
  Serial.println("Format: timestamp,L_Heel,L_Arch,L_MetaM,L_MetaL,L_Toe,R_Heel,R_Arch,R_MetaM,R_MetaL,R_Toe");
  Serial.println();

  // Print header
  Serial.print("time_ms");
  for (int i = 0; i < NUM_SENSORS; i++) {
    Serial.print(",");
    Serial.print(SENSOR_NAMES[i]);
  }
  Serial.println();
}

void loop() {
  static unsigned long lastSampleTime = 0;
  unsigned long currentTime = millis();

  if (currentTime - lastSampleTime >= SAMPLE_INTERVAL_MS) {
    lastSampleTime = currentTime;

    // Print timestamp
    Serial.print(currentTime);

    // Read and print all sensor values
    for (int i = 0; i < NUM_SENSORS; i++) {
      int value = analogRead(SENSOR_PINS[i]);
      Serial.print(",");
      Serial.print(value);
    }
    Serial.println();
  }
}
