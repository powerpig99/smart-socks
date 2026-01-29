/*
 * Smart Socks - XIAO ESP32S3 Diagnostic Tool
 * ELEC-E7840 Smart Wearables (Aalto University)
 *
 * Comprehensive diagnostic to test LED pins, Serial, and ADC
 */

const int LED_PINS[] = {21, 2, 13, 15, 14, 25};
const int NUM_LED_PINS = 6;
int currentLed = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n=== XIAO ESP32S3 DIAGNOSTIC ===\n");
  Serial.print("Chip: "); Serial.println(ESP.getChipModel());
  
  // Init all LED pins
  for (int i = 0; i < NUM_LED_PINS; i++) {
    pinMode(LED_PINS[i], OUTPUT);
    digitalWrite(LED_PINS[i], LOW);
  }
  
  Serial.println("\nTesting LED pins: 21, 2, 13, 15, 14, 25");
  Serial.println("Type 't' to test all pins");
  Serial.println("Type '+' to cycle through pins");
  Serial.println("Current pin should blink automatically\n");
  
  // Quick test flash
  flashAll();
}

void loop() {
  // Auto-blink current pin
  static unsigned long lastToggle = 0;
  static bool state = false;
  
  if (millis() - lastToggle > 500) {
    lastToggle = millis();
    state = !state;
    digitalWrite(LED_PINS[currentLed], state ? HIGH : LOW);
    Serial.print("Pin "); Serial.print(LED_PINS[currentLed]);
    Serial.println(state ? " HIGH" : " LOW");
  }
  
  // Handle commands
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 't') testAllPins();
    else if (c == '+') {
      digitalWrite(LED_PINS[currentLed], LOW);
      currentLed = (currentLed + 1) % NUM_LED_PINS;
      Serial.print("Switched to pin "); Serial.println(LED_PINS[currentLed]);
    }
    else if (c == 'i') {
      Serial.print("Pin "); Serial.print(LED_PINS[currentLed]);
      Serial.println(" - Is the LED blinking?");
    }
  }
}

void testAllPins() {
  Serial.println("\n--- Testing all pins ---");
  for (int i = 0; i < NUM_LED_PINS; i++) {
    int pin = LED_PINS[i];
    Serial.print("Pin "); Serial.print(pin); Serial.print(" ... ");
    
    // Flash 3 times
    for (int j = 0; j < 3; j++) {
      digitalWrite(pin, HIGH); delay(150);
      digitalWrite(pin, LOW); delay(150);
    }
    Serial.println("check if LED blinked!");
    delay(500);
  }
  Serial.println("\nWhich pin worked?");
}

void flashAll() {
  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < NUM_LED_PINS; j++) digitalWrite(LED_PINS[j], HIGH);
    delay(100);
    for (int j = 0; j < NUM_LED_PINS; j++) digitalWrite(LED_PINS[j], LOW);
    delay(100);
  }
}
