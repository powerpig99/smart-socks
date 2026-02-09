// =============================================================================
// read_serial.ino — Single Analog Sensor Reader for Seeed XIAO ESP32-S3
// =============================================================================
// Purpose: Reads one analog sensor on pin A5 and prints the raw ADC value
//          plus the converted voltage to the Serial Monitor.
// Usage:   Upload to XIAO ESP32-S3, open Serial Monitor at 115200 baud.
//          Output refreshes every 100 ms (~10 readings/second).
// Hardware: Any resistive sensor (pressure, stretch, FSR, potentiometer, etc.)
//           connected between A5 and GND/VCC with appropriate voltage divider.
// =============================================================================

// --- Pin Configuration -------------------------------------------------------
// A5 is one of the 6 analog-capable GPIO pins on the XIAO ESP32-S3.
// Other available analog pins: A0, A1, A2, A3, A4.
const int sensorPin = A0;

// =============================================================================
// setup() — Runs once when the board powers on or resets
// =============================================================================
void setup()
{
  // Start serial communication at 115200 baud.
  // This must match the baud rate set in the Serial Monitor / PlatformIO monitor.
  // 115200 is the standard rate used across the Smart Socks project.
  Serial.begin(115200);

  // Configure A5 as a digital input pin.
  // Note: For analogRead() on ESP32, pinMode(INPUT) is technically optional —
  // the ADC peripheral overrides the pin mode automatically. Included here
  // for clarity and good practice.
  pinMode(sensorPin, INPUT);

  // Wait 1 second for the USB-serial connection to establish.
  // Without this delay, the first few Serial.print() calls may be lost
  // because the host PC hasn't opened the serial port yet.
  delay(1000);

  // Confirm the sketch is running — helpful for debugging connection issues.
  Serial.println("Starting sensor readings on A5...");
}

// =============================================================================
// loop() — Runs repeatedly after setup() completes
// =============================================================================
void loop()
{
  // ---- Step 1: Read the raw ADC value ----
  // analogRead() samples the voltage on A5 using the ESP32-S3's built-in ADC.
  // The ADC has 12-bit resolution by default, producing values 0–4095:
  //   0    = 0.0 V (GND)
  //   4095 = 3.3 V (full scale, equal to the board's logic level)
  // The conversion takes ~10 microseconds, which is negligible at 10 Hz.
  int sensorValue = analogRead(sensorPin);

  // ---- Step 2: Convert raw ADC count to voltage ----
  // Formula: voltage = (raw / max_raw) * reference_voltage
  //   - max_raw = 4095 (2^12 - 1, the highest 12-bit value)
  //   - reference_voltage = 3.3 V (XIAO ESP32-S3 operates at 3.3 V logic)
  // Example: raw 2048 => 2048/4095 * 3.3 = ~1.65 V (midpoint)
  // Note: ESP32 ADC is non-linear near 0 V and 3.3 V; for precision work,
  // consider using the ESP-IDF calibration API (esp_adc_cal).
  float voltage = sensorValue * (3.3 / 4095.0);

  // ---- Step 3: Print results to Serial Monitor ----
  // Output format: "Raw Reading: 2048	 Voltage: 1.65 V"
  // The tab character (\t) aligns columns for easier reading.
  // To plot this data, use Arduino Serial Plotter or pipe to a Python script.
  Serial.print("Raw Reading: ");
  Serial.print(sensorValue);
  Serial.print("\t Voltage: ");
  Serial.print(voltage);
  Serial.println(" V");

  // ---- Step 4: Pace the readings ----
  // 100 ms delay = ~10 readings per second (10 Hz).
  // This is slow enough to read in the Serial Monitor but fast enough
  // to observe sensor changes in real time.
  // For the full Smart Socks data collection pipeline, 20 ms (50 Hz) is used
  // — see data_collection_leg.ino for the production sampling rate.
  delay(100);
}
