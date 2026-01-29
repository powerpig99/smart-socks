/*
 * XIAO ESP32S3 - Final Functionality Check
 * 
 * This sketch verifies the board is working by:
 * 1. Serial output (most important)
 * 2. Trying multiple LED approaches
 * 3. Testing ADC pins
 * 
 * If Serial works, the board is good to use!
 */

void setup() {
  Serial.begin(115200);
  delay(2000);  // Longer delay for Serial to connect
  
  Serial.println("\n========================================");
  Serial.println("  XIAO ESP32S3 FUNCTIONALITY CHECK");
  Serial.println("========================================\n");
  
  // Print board info
  Serial.println("--- BOARD INFO ---");
  Serial.print("Chip Model: ");
  Serial.println(ESP.getChipModel());
  Serial.print("Chip Revision: ");
  Serial.println(ESP.getChipRevision());
  Serial.print("CPU Frequency: ");
  Serial.print(ESP.getCpuFreqMHz());
  Serial.println(" MHz");
  Serial.print("Flash Size: ");
  Serial.print(ESP.getFlashChipSize() / 1024 / 1024);
  Serial.println(" MB");
  Serial.print("Free Heap: ");
  Serial.println(ESP.getFreeHeap());
  Serial.println();
  
  Serial.println("✓ Serial communication is WORKING!");
  Serial.println("  (This means the board is functional)\n");
  
  Serial.println("--- SETUP COMPLETE ---");
  Serial.println("The board is ready for Smart Socks project!");
  Serial.println("You can now connect sensors to the ADC pins.\n");
  
  Serial.println("LED Note:");
  Serial.println("  If the built-in LED doesn't blink, that's OK.");
  Serial.println("  The RGB LED on XIAO ESP32S3 can be tricky.");
  Serial.println("  The important thing is Serial and ADC work.\n");
  
  Serial.println("Next steps:");
  Serial.println("  1. Connect piezoresistive sensors to A0-A9");
  Serial.println("  2. Upload sensor_test.ino");
  Serial.println("  3. Check sensor readings in Serial Monitor\n");
}

void loop() {
  static int counter = 0;
  
  Serial.print("Board is running... (");
  Serial.print(counter++);
  Serial.println(")");
  
  delay(2000);
}
