/*
 * Smart Socks - Edge Impulse with LED Feedback
 * ELEC-E7840 Smart Wearables (Aalto University)
 *
 * This sketch shows activity recognition results using RGB LEDs.
 * 
 * Hardware:
 * - XIAO ESP32S3
 * - WS2812B RGB LED strip (5 LEDs recommended)
 * - Connected to GPIO 1 (D1 pin)
 * 
 * LED Feedback Mapping:
 * - LED 1: Activity type (color-coded)
 * - LED 2-4: Confidence level (brightness/bar)
 * - LED 5: Step count indicator (pulses)
 * 
 * Color Scheme:
 * - Green:    Walking
 * - Orange:   Stairs Up
 * - Red:      Stairs Down
 * - Blue:     Sitting
 * - White:    Standing
 * - Purple:   Unknown
 * 
 * Dependencies:
 * - Adafruit NeoPixel library
 */

#include <Adafruit_NeoPixel.h>

// ============== LED CONFIGURATION ==============

#define LED_PIN     1       // D1 on XIAO ESP32S3
#define LED_COUNT   5       // Number of LEDs in strip
#define BRIGHTNESS  50      // 0-255 (lower for battery saving)

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

// Activity colors (R, G, B)
const uint32_t COLOR_WALKING      = strip.Color(0, 255, 0);     // Green
const uint32_t COLOR_STAIRS_UP    = strip.Color(255, 165, 0);   // Orange
const uint32_t COLOR_STAIRS_DOWN  = strip.Color(255, 0, 0);     // Red
const uint32_t COLOR_SITTING      = strip.Color(0, 0, 255);     // Blue
const uint32_t COLOR_STANDING     = strip.Color(255, 255, 255); // White
const uint32_t COLOR_UNKNOWN      = strip.Color(128, 0, 128);   // Purple
const uint32_t COLOR_OFF          = strip.Color(0, 0, 0);       // Off

// Activity names (must match Edge Impulse model labels)
const char* ACTIVITY_NAMES[] = {
  "walking",
  "stairs_up",
  "stairs_down",
  "sitting",
  "standing"
};
const int NUM_ACTIVITIES = 5;

// ============== SENSOR CONFIGURATION ==============

const int NUM_SENSORS = 6;
const int SENSOR_PINS[] = {A0, A1, A2, A3, A4, A5};

// ============== STATE VARIABLES ==============

String currentActivity = "unknown";
float currentConfidence = 0.0;
int stepCount = 0;
unsigned long lastStepTime = 0;

// ============== SETUP ==============

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  
  // Initialize LED strip
  strip.begin();
  strip.setBrightness(BRIGHTNESS);
  strip.show();  // All off
  
  // Initialize sensors
  analogReadResolution(12);
  for (int i = 0; i < NUM_SENSORS; i++) {
    pinMode(SENSOR_PINS[i], INPUT);
  }
  
  // Startup animation
  startupAnimation();
  
  Serial.println("Smart Socks - LED Feedback System");
  Serial.println("==================================");
  Serial.println();
  Serial.println("LED Mapping:");
  Serial.println("  LED 1: Activity (color)");
  Serial.println("  LED 2-4: Confidence (bar)");
  Serial.println("  LED 5: Step count (pulse)");
  Serial.println();
  Serial.println("Activities:");
  Serial.println("  🟢 Green  = Walking");
  Serial.println("  🟠 Orange = Stairs Up");
  Serial.println("  🔴 Red    = Stairs Down");
  Serial.println("  🔵 Blue   = Sitting");
  Serial.println("  ⚪ White  = Standing");
  Serial.println("  🟣 Purple = Unknown");
  Serial.println();
}

// ============== MAIN LOOP ==============

void loop() {
  // Simulate activity detection (replace with actual Edge Impulse inference)
  simulateActivityDetection();
  
  // Update LED display
  updateLEDs();
  
  // Simulate step detection
  detectSteps();
  
  delay(100);  // 10Hz update rate for LEDs
}

// ============== ACTIVITY DETECTION (SIMULATION) ==============

void simulateActivityDetection() {
  // Read sensors (for demo purposes, use simple threshold)
  int l_heel = analogRead(A0);
  int l_ball = analogRead(A1);
  int l_knee = analogRead(A2);
  int r_heel = analogRead(A3);
  int r_ball = analogRead(A4);
  int r_knee = analogRead(A5);
  
  // Simple rule-based detection for demo
  // Replace this with actual Edge Impulse inference
  static int counter = 0;
  counter++;
  
  if (counter < 50) {
    currentActivity = "walking";
    currentConfidence = 0.92;
  } else if (counter < 100) {
    currentActivity = "stairs_up";
    currentConfidence = 0.85;
  } else if (counter < 150) {
    currentActivity = "stairs_down";
    currentConfidence = 0.78;
  } else if (counter < 200) {
    currentActivity = "sitting";
    currentConfidence = 0.96;
  } else {
    counter = 0;
  }
}

// ============== LED DISPLAY FUNCTIONS ==============

void updateLEDs() {
  // LED 1: Activity color
  uint32_t activityColor = getActivityColor(currentActivity);
  strip.setPixelColor(0, activityColor);
  
  // LED 2-4: Confidence bar (0-3 LEDs lit based on confidence)
  int confidenceLEDs = (int)(currentConfidence * 3);  // 0-3
  for (int i = 0; i < 3; i++) {
    if (i < confidenceLEDs) {
      strip.setPixelColor(i + 1, dimColor(activityColor, 128));
    } else {
      strip.setPixelColor(i + 1, COLOR_OFF);
    }
  }
  
  // LED 5: Step count pulse
  if (stepCount > 0 && (millis() - lastStepTime) < 500) {
    // Pulse white for step
    int brightness = 255 - ((millis() - lastStepTime) / 2);
    strip.setPixelColor(4, strip.Color(brightness, brightness, brightness));
  } else {
    strip.setPixelColor(4, COLOR_OFF);
  }
  
  strip.show();
}

uint32_t getActivityColor(const String& activity) {
  if (activity == "walking") return COLOR_WALKING;
  if (activity == "stairs_up") return COLOR_STAIRS_UP;
  if (activity == "stairs_down") return COLOR_STAIRS_DOWN;
  if (activity == "sitting") return COLOR_SITTING;
  if (activity == "standing") return COLOR_STANDING;
  return COLOR_UNKNOWN;
}

uint32_t dimColor(uint32_t color, uint8_t brightness) {
  uint8_t r = (uint8_t)(color >> 16);
  uint8_t g = (uint8_t)(color >> 8);
  uint8_t b = (uint8_t)color;
  
  r = (r * brightness) / 255;
  g = (g * brightness) / 255;
  b = (b * brightness) / 255;
  
  return strip.Color(r, g, b);
}

// ============== STEP DETECTION ==============

void detectSteps() {
  // Simple step detection based on heel pressure threshold
  static int lastHeelValue = 0;
  int heelValue = analogRead(A0);  // Left heel
  
  // Detect peak (simplified)
  if (heelValue > 3000 && lastHeelValue < 3000) {
    stepCount++;
    lastStepTime = millis();
    
    // Serial feedback
    Serial.print("Step detected! Total: ");
    Serial.println(stepCount);
  }
  
  lastHeelValue = heelValue;
}

// ============== UTILITY FUNCTIONS ==============

void startupAnimation() {
  // Rainbow fade on startup
  for (int j = 0; j < 256; j++) {
    for (int i = 0; i < LED_COUNT; i++) {
      strip.setPixelColor(i, wheel((i * 256 / LED_COUNT + j) & 255));
    }
    strip.show();
    delay(20);
  }
  
  // Clear
  strip.clear();
  strip.show();
}

uint32_t wheel(byte wheelPos) {
  wheelPos = 255 - wheelPos;
  if (wheelPos < 85) {
    return strip.Color(255 - wheelPos * 3, 0, wheelPos * 3);
  }
  if (wheelPos < 170) {
    wheelPos -= 85;
    return strip.Color(0, wheelPos * 3, 255 - wheelPos * 3);
  }
  wheelPos -= 170;
  return strip.Color(wheelPos * 3, 255 - wheelPos * 3, 0);
}

// ============== SERIAL COMMANDS ==============

void handleSerialCommands() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    
    if (cmd == "test") {
      // Test all colors
      testColors();
    } else if (cmd == "brightness") {
      // Cycle brightness
      static int b = 50;
      b = (b + 50) % 256;
      strip.setBrightness(b);
      Serial.print("Brightness: ");
      Serial.println(b);
    } else if (cmd == "reset") {
      stepCount = 0;
      Serial.println("Step count reset");
    }
  }
}

void testColors() {
  uint32_t colors[] = {
    COLOR_WALKING, COLOR_STAIRS_UP, COLOR_STAIRS_DOWN,
    COLOR_SITTING, COLOR_STANDING, COLOR_UNKNOWN
  };
  const char* names[] = {
    "Walking", "Stairs Up", "Stairs Down",
    "Sitting", "Standing", "Unknown"
  };
  
  for (int i = 0; i < 6; i++) {
    strip.fill(colors[i]);
    strip.show();
    Serial.print("Testing: ");
    Serial.println(names[i]);
    delay(1000);
  }
  
  strip.clear();
  strip.show();
}

/*
 * Integration with Edge Impulse:
 * 
 * To use this with actual Edge Impulse inference:
 * 
 * 1. Include the Edge Impulse library:
 *    #include <Smart_Socks_inferencing.h>
 * 
 * 2. Replace simulateActivityDetection() with:
 *    void runInference() {
 *      // Read sensors into buffer
 *      float buffer[EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE];
 *      // ... fill buffer ...
 *      
 *      // Run inference
 *      signal_t signal;
 *      numpy::signal_from_buffer(buffer, EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE, &signal);
 *      ei_impulse_result_t result = {0};
 *      EI_IMPULSE_ERROR err = run_classifier(&signal, &result, false);
 *      
 *      if (err == EI_IMPULSE_OK) {
 *        // Get top prediction
 *        currentActivity = result.classification[0].label;
 *        currentConfidence = result.classification[0].value;
 *      }
 *    }
 * 
 * 3. Call runInference() in loop() instead of simulateActivityDetection()
 */
