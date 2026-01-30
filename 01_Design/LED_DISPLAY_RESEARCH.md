# Smart Socks - LED Display Output Research

**Research on visual feedback options for XIAO ESP32S3**

---

## Executive Summary

For displaying activity recognition results on Smart Socks, we have three main options:

| Option | Complexity | Cost | Power | Readability | Recommendation |
|--------|-----------|------|-------|-------------|----------------|
| **RGB LEDs (WS2812B)** | Low | $2-3 | ~20mA | Good (color) | ⭐ **Best for wearables** |
| **OLED Display (SSD1306)** | Medium | $5-8 | ~15mA | Excellent | Good for debugging |
| **7-Segment LED** | Low | $1-2 | ~40mA | Moderate | Simple numeric output |

**Primary Recommendation:** RGB LEDs (NeoPixel/WS2812B)
- Low power, simple wiring, color-coded feedback
- Can show activity type + confidence level

---

## Option 1: RGB LEDs (WS2812B/NeoPixel) ⭐ RECOMMENDED

### Overview
Addressable RGB LEDs that can display any color. Perfect for wearable feedback.

### Hardware

**Components:**
- WS2812B LED strip or individual LEDs
- 3 wires: VCC, GND, Data
- Current limiting resistor (optional)

**Wiring for XIAO ESP32S3:**
```
WS2812B LED Strip
═════════════════
VCC  → 3.3V (or 5V if using level shifter)
GND  → GND
DIN  → D1 (GPIO 1) - Any digital pin
```

**Power Considerations:**
- Each LED: ~20mA at full brightness
- 5 LEDs: ~100mA (manageable for USB/battery)
- Use lower brightness for battery operation

### Software

**Library:** Adafruit NeoPixel
```cpp
#include <Adafruit_NeoPixel.h>

#define LED_PIN    1
#define LED_COUNT  5

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  strip.begin();
  strip.setBrightness(50);  // 0-255, lower for battery saving
  strip.show();
}

void showActivity(const char* activity, float confidence) {
  // Map activity to color
  if (strcmp(activity, "walking") == 0) {
    strip.fill(strip.Color(0, 255, 0));  // Green
  } else if (strcmp(activity, "stairs_up") == 0) {
    strip.fill(strip.Color(255, 165, 0));  // Orange
  } else if (strcmp(activity, "stairs_down") == 0) {
    strip.fill(strip.Color(255, 0, 0));  // Red
  } else if (strcmp(activity, "sitting") == 0) {
    strip.fill(strip.Color(0, 0, 255));  // Blue
  } else {
    strip.fill(strip.Color(128, 0, 128));  // Purple (unknown)
  }
  
  // Adjust brightness based on confidence
  uint8_t brightness = (uint8_t)(confidence * 255);
  strip.setBrightness(brightness);
  strip.show();
}
```

### Color Coding Scheme

| Activity | Color | RGB Value |
|----------|-------|-----------|
| Walking | 🟢 Green | (0, 255, 0) |
| Stairs Up | 🟠 Orange | (255, 165, 0) |
| Stairs Down | 🔴 Red | (255, 0, 0) |
| Sitting | 🔵 Blue | (0, 0, 255) |
| Standing | ⚪ White | (255, 255, 255) |
| Unknown | 🟣 Purple | (128, 0, 128) |

### Advanced: Multi-LED Feedback

Use multiple LEDs to show additional information:
```
LED 1: Activity type (color)
LED 2: Confidence level (brightness/pulse)
LED 3-5: Step count indicator (progress bar)
```

---

## Option 2: OLED Display (SSD1306)

### Overview
Small 0.96" or 1.3" display showing text and graphics. Good for detailed feedback.

### Hardware

**Components:**
- SSD1306 128x64 OLED (I2C)
- 4 wires: VCC, GND, SCL, SDA

**Wiring for XIAO ESP32S3:**
```
SSD1306 OLED
════════════
VCC  → 3.3V
GND  → GND
SCL  → D5 (GPIO 7) - Default SCL
SDA  → D4 (GPIO 6) - Default SDA
```

**I2C Address:** Usually 0x3C or 0x3D

### Software

**Library:** Adafruit SSD1306
```cpp
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define SCREEN_ADDRESS 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

void setup() {
  display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS);
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
}

void showActivity(const char* activity, float confidence, int step_count) {
  display.clearDisplay();
  
  display.setCursor(0, 0);
  display.setTextSize(2);
  display.println(activity);
  
  display.setTextSize(1);
  display.print("Confidence: ");
  display.print((int)(confidence * 100));
  display.println("%");
  
  display.print("Steps: ");
  display.println(step_count);
  
  // Draw confidence bar
  display.drawRect(0, 56, 128, 8, SSD1306_WHITE);
  display.fillRect(0, 56, (int)(128 * confidence), 8, SSD1306_WHITE);
  
  display.display();
}
```

### Pros/Cons

**Pros:**
- Detailed text output
- Can show multiple metrics
- Good for debugging

**Cons:**
- More power consumption
- Fragile for wearables
- Requires more code

---

## Option 3: 7-Segment LED Display

### Overview
Simple numeric display. Good for showing step count or activity ID.

### Hardware
- TM1637 4-digit display
- I2C-like interface (2 wires)

**Wiring:**
```
TM1637
══════
VCC  → 3.3V
GND  → GND
CLK  → D2 (any digital pin)
DIO  → D3 (any digital pin)
```

### Software
```cpp
#include <TM1637Display.h>

#define CLK 2
#define DIO 3

TM1637Display display(CLK, DIO);

void setup() {
  display.setBrightness(7);  // 0-7
}

void showStepCount(int steps) {
  display.showNumberDec(steps, false);
}

void showActivityId(int activity_id) {
  // A1, A2, A3, A4 for different activities
  display.showNumberHexEx(0xA100 + activity_id, 0, false);
}
```

---

## Option 4: Simple LEDs (Individual)

### Overview
Basic single-color LEDs. Most simple option.

### Hardware
- 5x LEDs (different colors)
- 5x 220Ω resistors

**Wiring:**
```
LEDs
════
LED1 (Green)  → D1 + 220Ω → GND (Walking)
LED2 (Yellow) → D2 + 220Ω → GND (Stairs Up)
LED3 (Red)    → D3 + 220Ω → GND (Stairs Down)
LED4 (Blue)   → D4 + 220Ω → GND (Sitting)
LED5 (White)  → D5 + 220Ω → GND (Standing)
```

### Software
```cpp
const int LED_PINS[] = {1, 2, 3, 4, 5};
const int NUM_LEDS = 5;

void setup() {
  for (int i = 0; i < NUM_LEDS; i++) {
    pinMode(LED_PINS[i], OUTPUT);
  }
}

void showActivity(int activity_id) {
  // Turn off all LEDs
  for (int i = 0; i < NUM_LEDS; i++) {
    digitalWrite(LED_PINS[i], LOW);
  }
  
  // Turn on corresponding LED
  if (activity_id >= 0 && activity_id < NUM_LEDS) {
    digitalWrite(LED_PINS[activity_id], HIGH);
  }
}
```

---

## Recommendation Matrix

| Use Case | Recommended | Reason |
|----------|-------------|--------|
| **Wearable demo** | RGB LEDs | Low power, simple, color intuitive |
| **Development/debug** | OLED | Detailed feedback, easy to read |
| **Step counting** | 7-Segment | Clear numeric display |
| **Budget/simple** | Individual LEDs | Cheapest, easiest to implement |

---

## Implementation Plan

### Phase 1: RGB LEDs (Recommended)
1. Order WS2812B strip (5-10 LEDs)
2. Connect to GPIO 1 on XIAO
3. Implement color mapping in firmware
4. Test with different activities

### Phase 2: Optional OLED
1. Add SSD1306 for detailed feedback
2. Mount on ankle/wrist for visibility
3. Show activity + confidence + step count

### Phase 3: Power Optimization
1. Reduce LED brightness to 30-50%
2. Turn off display after 5s of inactivity
3. Use deep sleep between updates

---

## Shopping List

### RGB LED Option (Recommended)
| Item | Qty | Est. Cost | Link |
|------|-----|-----------|------|
| WS2812B LED Strip (5 LEDs) | 1 | $2-3 | Amazon/AliExpress |
| JST connectors | 2 | $1 | - |
| Wire (26 AWG) | 1m | $0.5 | - |

### OLED Option
| Item | Qty | Est. Cost | Link |
|------|-----|-----------|------|
| SSD1306 0.96" OLED | 1 | $5-8 | Amazon/Adafruit |
| Headers | 1 set | $1 | - |

### Simple LED Option
| Item | Qty | Est. Cost |
|------|-----|-----------|
| 5mm LEDs (5 colors) | 5 | $1 |
| 220Ω resistors | 5 | $0.5 |

---

## References

- Adafruit NeoPixel Guide: https://learn.adafruit.com/adafruit-neopixel-uberguide
- SSD1306 Arduino Library: https://github.com/adafruit/Adafruit_SSD1306
- TM1637 Display: https://github.com/avishorp/TM1637
- XIAO ESP32S3 Pinout: https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/

---

*Research completed: February 2026*
