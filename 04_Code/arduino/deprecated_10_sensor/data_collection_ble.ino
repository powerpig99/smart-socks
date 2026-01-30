/*
 * Smart Socks - Data Collection with BLE Support
 * ELEC-E7840 Smart Wearables (Aalto University)
 *
 * Multi-channel data collection with Bluetooth Low Energy support.
 * Streams 10-channel pressure sensor data at 50+ Hz via BLE.
 *
 * Hardware: ESP32S3 XIAO with 10kΩ voltage dividers
 * Sensors: 5 zones per sock (Heel, Arch, Metatarsal medial/lateral, Toe)
 *
 * BLE Service UUID: 4fafc201-1fb5-459e-8fcc-c5c9c331914b
 * BLE Characteristic UUID: beb5483e-36e1-4688-b7f5-ea07361b26a8
 */

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

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

// BLE Configuration
#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#define DEVICE_NAME         "SmartSocks"

BLEServer *pServer = NULL;
BLECharacteristic *pCharacteristic = NULL;
bool deviceConnected = false;
bool oldDeviceConnected = false;

// Recording state
bool isRecording = false;
String currentActivity = "";
String currentSubject = "";
unsigned long recordingStartTime = 0;
unsigned long sampleCount = 0;

// Output mode
enum OutputMode { SERIAL_ONLY, BLE_ONLY, BOTH };
OutputMode outputMode = BOTH;

// BLE Server Callbacks
class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
      Serial.println("BLE Client Connected");
    };

    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
      Serial.println("BLE Client Disconnected");
    }
};

// BLE Characteristic Callbacks for receiving commands
class MyCallbacks: public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *pCharacteristic) {
      String value = pCharacteristic->getValue().c_str();
      if (value.length() > 0) {
        Serial.print("Received BLE command: ");
        Serial.println(value);
        processCommand(value);
      }
    }
};

// Helper function to send data via BLE with MTU chunking
// Default MTU is 23 bytes (3 bytes overhead + 20 bytes payload)
// We use 20 bytes to be safe across all devices
void sendBLEData(const String& data) {
  if (!deviceConnected || pCharacteristic == NULL) return;
  
  const int CHUNK_SIZE = 20;  // Safe for default BLE MTU
  int length = data.length();
  int offset = 0;
  
  while (offset < length) {
    int chunkLen = min(CHUNK_SIZE, length - offset);
    String chunk = data.substring(offset, offset + chunkLen);
    pCharacteristic->setValue(chunk.c_str());
    pCharacteristic->notify();
    offset += chunkLen;
    
    // Small delay between chunks to prevent overflow
    if (offset < length) {
      delay(5);
    }
  }
}

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    delay(10);
  }

  // Configure ADC
  analogReadResolution(ADC_RESOLUTION);
  analogSetAttenuation(ADC_11db);  // 0-3.3V range for 10kΩ voltage dividers

  // Configure sensor pins
  for (int i = 0; i < NUM_SENSORS; i++) {
    pinMode(SENSOR_PINS[i], INPUT);
  }

  // Initialize BLE
  setupBLE();

  printHelp();
}

void setupBLE() {
  // Create the BLE Device
  BLEDevice::init(DEVICE_NAME);

  // Create the BLE Server
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  // Create the BLE Service
  BLEService *pService = pServer->createService(SERVICE_UUID);

  // Create the BLE Characteristic
  pCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_READ   |
    BLECharacteristic::PROPERTY_WRITE  |
    BLECharacteristic::PROPERTY_NOTIFY |
    BLECharacteristic::PROPERTY_INDICATE
  );

  // Add descriptor for notifications
  pCharacteristic->addDescriptor(new BLE2902());
  pCharacteristic->setCallbacks(new MyCallbacks());

  // Start the service
  pService->start();

  // Start advertising
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);
  pAdvertising->setMaxPreferred(0x12);
  BLEDevice::startAdvertising();

  Serial.println("BLE initialized. Waiting for client connection...");
  Serial.print("Device name: ");
  Serial.println(DEVICE_NAME);
  Serial.print("Service UUID: ");
  Serial.println(SERVICE_UUID);
  Serial.print("Characteristic UUID: ");
  Serial.println(CHARACTERISTIC_UUID);
}

void loop() {
  // Check for serial commands
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    processCommand(command);
  }

  // Handle BLE connection state changes
  if (!deviceConnected && oldDeviceConnected) {
    delay(500);
    pServer->startAdvertising();
    Serial.println("Restarting BLE advertising...");
    oldDeviceConnected = deviceConnected;
  }
  if (deviceConnected && !oldDeviceConnected) {
    oldDeviceConnected = deviceConnected;
  }

  // Data collection
  if (isRecording) {
    static unsigned long lastSampleTime = 0;
    unsigned long currentTime = millis();

    if (currentTime - lastSampleTime >= SAMPLE_INTERVAL_MS) {
      lastSampleTime = currentTime;
      sampleCount++;

      // Build data string
      String dataString = "";
      dataString += String(currentTime - recordingStartTime);

      // Read all sensor values
      int sensorValues[NUM_SENSORS];
      for (int i = 0; i < NUM_SENSORS; i++) {
        sensorValues[i] = analogRead(SENSOR_PINS[i]);
        dataString += "," + String(sensorValues[i]);
      }

      // Output via selected mode
      if (outputMode == SERIAL_ONLY || outputMode == BOTH) {
        Serial.println(dataString);
      }

      if ((outputMode == BLE_ONLY || outputMode == BOTH) && deviceConnected) {
        // Send via BLE with MTU chunking
        sendBLEData(dataString + "\n");
      }
    }
  }
}

void processCommand(String cmd) {
  cmd.toUpperCase();
  
  if (cmd.startsWith("START ")) {
    // Format: START <subject_id> <activity>
    cmd.toLowerCase();
    int firstSpace = cmd.indexOf(' ');
    int secondSpace = cmd.indexOf(' ', firstSpace + 1);

    if (secondSpace > firstSpace) {
      currentSubject = cmd.substring(firstSpace + 1, secondSpace);
      currentSubject.toUpperCase();
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
  else if (cmd == "MODE SERIAL") {
    setOutputMode(SERIAL_ONLY);
  }
  else if (cmd == "MODE BLE") {
    setOutputMode(BLE_ONLY);
  }
  else if (cmd == "MODE BOTH") {
    setOutputMode(BOTH);
  }
  else if (cmd == "HELP") {
    printHelp();
  }
  else {
    Serial.println("ERROR: Unknown command. Type HELP for available commands.");
  }
}

void setOutputMode(OutputMode mode) {
  outputMode = mode;
  Serial.print("Output mode set to: ");
  switch(mode) {
    case SERIAL_ONLY:
      Serial.println("SERIAL ONLY");
      break;
    case BLE_ONLY:
      Serial.println("BLE ONLY");
      break;
    case BOTH:
      Serial.println("BOTH (Serial + BLE)");
      break;
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

  String header = "# Recording started\n";
  header += "# Subject: " + currentSubject + "\n";
  header += "# Activity: " + currentActivity + "\n";
  header += "# Sample rate: " + String(SAMPLE_RATE_HZ) + " Hz\n";
  header += "# Format: time_ms,L_Heel,L_Arch,L_MetaM,L_MetaL,L_Toe,R_Heel,R_Arch,R_MetaM,R_MetaL,R_Toe\n";
  header += "# DATA_START";

  Serial.println(header);

  // Send header via BLE if connected
  if (deviceConnected) {
    sendBLEData(header + "\n");
  }
}

void stopRecording() {
  if (!isRecording) {
    Serial.println("WARNING: Not currently recording.");
    return;
  }

  isRecording = false;
  unsigned long duration = millis() - recordingStartTime;

  String footer = "# DATA_END\n";
  footer += "# Recording stopped. Duration: " + String(duration / 1000.0, 2) + " seconds, Samples: " + String(sampleCount);

  Serial.println(footer);

  // Send footer via BLE if connected
  if (deviceConnected) {
    sendBLEData(footer + "\n");
  }
}

void printStatus() {
  String status = "=== Smart Socks Status ===\n";
  status += "Recording: " + String(isRecording ? "YES" : "NO") + "\n";
  status += "Output Mode: ";
  switch(outputMode) {
    case SERIAL_ONLY: status += "SERIAL\n"; break;
    case BLE_ONLY: status += "BLE\n"; break;
    case BOTH: status += "BOTH\n"; break;
  }
  status += "BLE Connected: " + String(deviceConnected ? "YES" : "NO") + "\n";

  if (isRecording) {
    status += "Subject: " + currentSubject + "\n";
    status += "Activity: " + currentActivity + "\n";
    status += "Samples: " + String(sampleCount) + "\n";
    status += "Duration: " + String((millis() - recordingStartTime) / 1000.0, 2) + " seconds\n";
  }

  status += "Sample rate: " + String(SAMPLE_RATE_HZ) + " Hz";

  Serial.println(status);

  // Send status via BLE if connected
  if (deviceConnected) {
    sendBLEData(status + "\n");
  }
}

void printHelp() {
  String help = "=== Smart Socks Data Collection (BLE Enabled) ===\n";
  help += "Commands:\n";
  help += "  START <subject_id> <activity> - Start recording\n";
  help += "  STOP                          - Stop recording\n";
  help += "  STATUS                        - Show current status\n";
  help += "  MODE SERIAL                   - Output to serial only\n";
  help += "  MODE BLE                      - Output via BLE only\n";
  help += "  MODE BOTH                     - Output to both (default)\n";
  help += "  HELP                          - Show this help\n";
  help += "\nBLE Configuration:\n";
  help += "  Device Name: " + String(DEVICE_NAME) + "\n";
  help += "  Service UUID: " + String(SERVICE_UUID) + "\n";
  help += "\nActivities:\n";
  help += "  walking_forward, walking_backward\n";
  help += "  stairs_up, stairs_down\n";
  help += "  sitting_floor, sitting_crossed\n";
  help += "  sit_to_stand, stand_to_sit\n";
  help += "  standing_upright, standing_lean_left, standing_lean_right\n";
  help += "\nExample: START S01 walking_forward";

  Serial.println(help);
}
