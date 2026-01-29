/*
 * XIAO ESP32S3 RGB LED Test - PWM Method
 * 
 * The XIAO ESP32S3 has an RGB LED controlled by PWM on GPIO 21
 * This sketch uses PWM to fade the LED in and out
 */

#define LED_PIN 21

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n=== XIAO ESP32S3 LED PWM Test ===");
  Serial.println("LED should fade in and out");
  
  // Setup PWM on pin 21
  // For ESP32-S3, we use ledc functions
  ledcAttach(LED_PIN, 5000, 8);  // Pin, frequency (5kHz), resolution (8-bit)
}

void loop() {
  // Fade in (0 to 255)
  Serial.println("Fading IN...");
  for (int i = 0; i <= 255; i++) {
    ledcWrite(LED_PIN, i);
    delay(10);
  }
  
  // Hold at full brightness
  delay(500);
  
  // Fade out (255 to 0)
  Serial.println("Fading OUT...");
  for (int i = 255; i >= 0; i--) {
    ledcWrite(LED_PIN, i);
    delay(10);
  }
  
  // Hold off
  delay(500);
}
