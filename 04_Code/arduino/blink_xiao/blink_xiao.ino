#include <Adafruit_NeoPixel.h>

  #define LED_PIN 21
  #define NUM_LEDS 1

  Adafruit_NeoPixel led(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

  void setup() {
    led.begin();
    led.show();  // Initialize off
  }

  void loop() {
    led.setPixelColor(0, led.Color(255, 0, 0));  // Red
    led.show();
    delay(500);

    led.setPixelColor(0, led.Color(0, 255, 0));  // Green
    led.show();
    delay(500);

    led.setPixelColor(0, led.Color(0, 0, 255));  // Blue
    led.show();
    delay(500);

    led.setPixelColor(0, led.Color(0, 0, 0));    // Off
    led.show();
    delay(500);
  }
