/*
 * Smart Socks - Data Collection Sketch
 * ELEC-E7840 Smart Wearables (Aalto University)
 *
 * Multi-channel data collection for activity recognition.
 * Streams 10-channel pressure sensor data at 50+ Hz.
 *
 * Hardware: ESP32S3 XIAO with 10kΩ voltage dividers
 * Sensors: 5 zones per sock (Heel, Arch, Metatarsal medial/lateral, Toe)
 *
 * Activities to record:
 * - Walking (forward/backward)
 * - Stair climbing (up/down)
 * - Sitting (feet on floor / cross-legged)
 * - Sit-to-stand transitions
 * - Standing (upright / leaning left/right)
 */

// Sensor pin definitions - Left sock
const int L_HEEL = A0;
const int L_ARCH = A1;
const int L_META_MED = A2;
const int L_META_LAT = A3;
const int L_TOE = A4;

// Sensor pin definitions - Right sock
const int R_HEEL = A5;
const int R_ARCH = A6;
const int R_META_MED = A7;
const int R_META_LAT = A8;
const int R_TOE = A9;

// All sensor pins in array
const int SENSOR_PINS[] = {
  L_HEEL, L_ARCH, L_META_MED, L_META_LAT, L_TOE,
  R_HEEL, R_ARCH, R_META_MED, R_META_LAT, R_TOE
};
const int NUM_SENSORS = 10;

// Sampling configuration
const int SAMPLE_RATE_HZ = 50;
const int SAMPLE_INTERVAL_MS = 1000 / SAMPLE_RATE_HZ;

// ADC configuration
const int ADC_RESOLUTION = 12;  // 12-bit ADC (0-4095)

// Recording state
bool isRecording = false;
String currentActivity = "";
String currentSubject = "";
unsigned long recordingStartTime = 0;
unsigned long sampleCount = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    delay(10);
  }

  // Configure ADC
  analogReadResolution(ADC_RESOLUTION);

  // Configure sensor pins
  for (int i = 0; i < NUM_SENSORS; i++) {
    pinMode(SENSOR_PINS[i], INPUT);
  }

  printHelp();
}

void loop() {
  // Check for serial commands
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    processCommand(command);
  }

  // Data collection
  if (isRecording) {
    static unsigned long lastSampleTime = 0;
    unsigned long currentTime = millis();

    if (currentTime - lastSampleTime >= SAMPLE_INTERVAL_MS) {
      lastSampleTime = currentTime;
      sampleCount++;

      // Print timestamp relative to recording start
      Serial.print(currentTime - recordingStartTime);

      // Read and print all sensor values
      for (int i = 0; i < NUM_SENSORS; i++) {
        int value = analogRead(SENSOR_PINS[i]);
        Serial.print(",");
        Serial.print(value);
      }
      Serial.println();
    }
  }
}

void processCommand(String cmd) {
  if (cmd.startsWith("START ")) {
    // Format: START <subject_id> <activity>
    // Example: START S01 walking_forward
    int firstSpace = cmd.indexOf(' ');
    int secondSpace = cmd.indexOf(' ', firstSpace + 1);

    if (secondSpace > firstSpace) {
      currentSubject = cmd.substring(firstSpace + 1, secondSpace);
      currentActivity = cmd.substring(secondSpace + 1);
      startRecording();
    } else {
      Serial.println("ERROR: Invalid format. Use: START <subject_id> <activity>");
    }
  }
  else if (cmd == "STOP") {
    stopRecording();
  }
  else if (cmd == "STATUS") {
    printStatus();
  }
  else if (cmd == "HELP") {
    printHelp();
  }
  else {
    Serial.println("ERROR: Unknown command. Type HELP for available commands.");
  }
}

void startRecording() {
  if (isRecording) {
    Serial.println("WARNING: Already recording. Send STOP first.");
    return;
  }

  isRecording = true;
  recordingStartTime = millis();
  sampleCount = 0;

  Serial.println("# Recording started");
  Serial.print("# Subject: ");
  Serial.println(currentSubject);
  Serial.print("# Activity: ");
  Serial.println(currentActivity);
  Serial.print("# Sample rate: ");
  Serial.print(SAMPLE_RATE_HZ);
  Serial.println(" Hz");
  Serial.println("# Format: time_ms,L_Heel,L_Arch,L_MetaM,L_MetaL,L_Toe,R_Heel,R_Arch,R_MetaM,R_MetaL,R_Toe");
  Serial.println("# DATA_START");
}

void stopRecording() {
  if (!isRecording) {
    Serial.println("WARNING: Not currently recording.");
    return;
  }

  isRecording = false;
  unsigned long duration = millis() - recordingStartTime;

  Serial.println("# DATA_END");
  Serial.print("# Recording stopped. Duration: ");
  Serial.print(duration / 1000.0, 2);
  Serial.print(" seconds, Samples: ");
  Serial.println(sampleCount);
}

void printStatus() {
  Serial.println("=== Smart Socks Data Collection ===");
  Serial.print("Recording: ");
  Serial.println(isRecording ? "YES" : "NO");

  if (isRecording) {
    Serial.print("Subject: ");
    Serial.println(currentSubject);
    Serial.print("Activity: ");
    Serial.println(currentActivity);
    Serial.print("Samples collected: ");
    Serial.println(sampleCount);
    Serial.print("Duration: ");
    Serial.print((millis() - recordingStartTime) / 1000.0, 2);
    Serial.println(" seconds");
  }

  Serial.print("Sample rate: ");
  Serial.print(SAMPLE_RATE_HZ);
  Serial.println(" Hz");
}

void printHelp() {
  Serial.println("=== Smart Socks Data Collection ===");
  Serial.println("Commands:");
  Serial.println("  START <subject_id> <activity> - Start recording");
  Serial.println("  STOP                          - Stop recording");
  Serial.println("  STATUS                        - Show current status");
  Serial.println("  HELP                          - Show this help");
  Serial.println();
  Serial.println("Activities:");
  Serial.println("  walking_forward, walking_backward");
  Serial.println("  stairs_up, stairs_down");
  Serial.println("  sitting_floor, sitting_crossed");
  Serial.println("  sit_to_stand, stand_to_sit");
  Serial.println("  standing_upright, standing_lean_left, standing_lean_right");
  Serial.println();
  Serial.println("Example: START S01 walking_forward");
}
