/*
 * Smart Socks - Data Collection (6-Sensor, Single ESP32)
 * ELEC-E7840 Smart Wearables (Aalto University)
 *
 * Hardware: ESP32S3 XIAO with 10kΩ voltage dividers
 * Sensors: 6 total (2 pressure + 1 stretch per leg, all on one ESP32)
 *   A0: L_P_Heel, A1: L_P_Ball, A2: L_S_Knee
 *   A3: R_P_Heel, A4: R_P_Ball, A5: R_S_Knee
 *
 * Features:
 * - BLE: Real-time sensor monitoring
 * - WiFi: HTTP server for data streaming
 * - Serial: Debug and command interface
 * - Timestamp: Milliseconds since boot
 */

#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <ArduinoJson.h>

// ============== CONFIGURATION ==============

// WiFi Configuration
// Choose ONE mode by uncommenting the appropriate section:

// WiFi: Auto-connect to saved networks, fallback to AP mode
// Edit credentials.h to add/remove networks (file is gitignored)
// On boot: scan → match saved networks → connect to strongest → fallback to AP
#include "credentials.h"

// Device identification (works in all modes)
// The ESP32 will display its MAC address on startup
// You can identify devices by MAC instead of IP
String deviceMAC;
String deviceHostname = "smartsocks";

// AP channel (not sensitive)
const int AP_CHANNEL = 6;

// BLE Configuration
#define BLE_DEVICE_NAME   "SmartSocks"
#define BLE_SERVICE_UUID  "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define BLE_CHAR_SENSOR   "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#define BLE_CHAR_COMMAND  "beb5483e-36e1-4688-b7f5-ea07361b26a9"

// 6-sensor pin mapping (same as calibration_all_sensors.ino)
const int SENSOR_PINS[] = {A0, A1, A2, A3, A4, A5};
const char* SENSOR_NAMES[] = {
  "L_P_Heel", "L_P_Ball", "L_S_Knee",
  "R_P_Heel", "R_P_Ball", "R_S_Knee"
};
const int NUM_SENSORS = 6;

// Sampling configuration
const int SAMPLE_RATE_HZ = 50;
const int SAMPLE_INTERVAL_MS = 1000 / SAMPLE_RATE_HZ;
const int ADC_RESOLUTION = 12;

// ============== GLOBAL STATE ==============

// Web server
WebServer server(80);

// BLE
BLEServer *bleServer = NULL;
BLECharacteristic *bleSensorChar = NULL;
BLECharacteristic *bleCommandChar = NULL;
bool bleDeviceConnected = false;

// Recording state
bool isRecording = false;
String currentActivity = "";
String currentSubject = "";
unsigned long recordingStartTime = 0;
unsigned long sampleCount = 0;

// Data buffer for HTTP download
String dataBuffer = "";
const int MAX_BUFFER_LINES = 1000;
int bufferLineCount = 0;


// Forward declarations
void processCommand(String cmd);

// ============== BLE CALLBACKS ==============

class SmartSocksServerCallbacks: public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) {
    bleDeviceConnected = true;
    Serial.println("BLE: Client connected");
  }
  void onDisconnect(BLEServer* pServer) {
    bleDeviceConnected = false;
    Serial.println("BLE: Client disconnected");
    BLEDevice::startAdvertising();
  }
};

class BLECommandCallbacks: public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristic) {
    String value = pCharacteristic->getValue().c_str();
    if (value.length() > 0) {
      Serial.print("BLE Command: ");
      Serial.println(value);
      processCommand(value);
    }
  }
};

// ============== HELPER FUNCTIONS ==============

void sendBLEChunked(const String& data) {
  if (!bleDeviceConnected || bleSensorChar == NULL) return;

  const int CHUNK_SIZE = 20;
  int len = data.length();
  int offset = 0;

  while (offset < len) {
    int chunkLen = min(CHUNK_SIZE, len - offset);
    String chunk = data.substring(offset, offset + chunkLen);
    bleSensorChar->setValue(chunk.c_str());
    bleSensorChar->notify();
    offset += chunkLen;
    if (offset < len) delay(5);
  }
}

String readSensorsJSON() {
  StaticJsonDocument<512> doc;
  doc["t"] = millis();
  doc["mac"] = deviceMAC;

  JsonObject sensors = doc.createNestedObject("s");
  for (int i = 0; i < NUM_SENSORS; i++) {
    sensors[SENSOR_NAMES[i]] = analogRead(SENSOR_PINS[i]);
  }

  String output;
  serializeJson(doc, output);
  return output;
}

String getDeviceInfoJSON() {
  StaticJsonDocument<512> doc;
  doc["mac"] = deviceMAC;
  doc["hostname"] = deviceHostname;

  if (WiFi.getMode() == WIFI_STA || WiFi.getMode() == WIFI_AP_STA) {
    doc["mode"] = "station";
    doc["ssid"] = WiFi.SSID();
    doc["ip"] = WiFi.localIP().toString();
  } else {
    doc["mode"] = "ap";
    doc["ssid"] = AP_SSID;
    doc["ip"] = WiFi.softAPIP().toString();
  }

  JsonArray pins = doc.createNestedArray("pins");
  for (int i = 0; i < NUM_SENSORS; i++) {
    pins.add(SENSOR_NAMES[i]);
  }

  String output;
  serializeJson(doc, output);
  return output;
}

String readSensorsCSV() {
  String line = String(millis() - recordingStartTime);
  for (int i = 0; i < NUM_SENSORS; i++) {
    line += "," + String(analogRead(SENSOR_PINS[i]));
  }
  return line;
}

void startRecording() {
  isRecording = true;
  recordingStartTime = millis();
  sampleCount = 0;
  bufferLineCount = 0;
  dataBuffer = "time_ms";
  for (int i = 0; i < NUM_SENSORS; i++) {
    dataBuffer += "," + String(SENSOR_NAMES[i]);
  }
  dataBuffer += "\n";
  Serial.println("Recording started");
}

void stopRecording() {
  isRecording = false;
  Serial.println("Recording stopped");
}

// ============== HTTP HANDLERS ==============

void handleRoot() {
  String html = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Smart Socks</title>
  <style>
    :root {
      --nord0: #2E3440; --nord1: #3B4252; --nord2: #434C5E;
      --nord3: #4C566A; --nord4: #D8DEE9; --nord5: #E5E9F0;
      --nord6: #ECEFF4; --nord7: #8FBCBB; --nord8: #88C0D0;
      --nord9: #81A1C1; --nord10: #5E81AC; --nord11: #BF616A;
      --nord12: #D08770; --nord13: #EBCB8B; --nord14: #A3BE8C;
      --nord15: #B48EAD;
    }
    * { box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      margin: 0; padding: 30px;
      background: var(--nord0); color: var(--nord6);
      line-height: 1.6;
    }
    .header { text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid var(--nord3); }
    h1 { color: var(--nord6); font-weight: 300; font-size: 28px; letter-spacing: 4px; margin: 0; }
    .subtitle { color: var(--nord8); font-size: 12px; letter-spacing: 2px; margin-top: 5px; }

    #status {
      margin: 20px 0; padding: 15px 20px;
      background: var(--nord1); border-radius: 8px;
      border-left: 4px solid var(--nord8);
      font-family: monospace; font-size: 13px;
    }
    .recording { color: var(--nord11); font-weight: bold; }

    .sensor-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 25px 0; }
    .sensor-box {
      background: var(--nord1); padding: 25px 15px;
      border-radius: 8px; text-align: center; border: 1px solid var(--nord2);
      transition: border-color 0.3s;
    }
    .sensor-box:hover { border-color: var(--nord8); }
    .sensor-name { font-size: 12px; color: var(--nord4); text-transform: uppercase; letter-spacing: 1px; font-weight: 500; }
    .sensor-value { font-size: 32px; font-weight: 300; color: var(--nord8); margin: 15px 0; font-family: 'SF Mono', Monaco, monospace; }
    .sensor-bar { height: 8px; background: var(--nord0); border-radius: 4px; overflow: hidden; margin-top: 10px; }
    .sensor-bar-fill { height: 100%; background: linear-gradient(90deg, var(--nord8), var(--nord9)); transition: width 0.15s ease; border-radius: 4px; }

    .row-label { grid-column: 1 / -1; font-size: 11px; color: var(--nord3); text-transform: uppercase; letter-spacing: 2px; padding: 5px 0 0 5px; }

    .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 25px 0; }
    .stat-box { background: var(--nord1); padding: 20px; border-radius: 8px; text-align: center; border: 1px solid var(--nord2); }
    .stat-value { font-size: 28px; font-weight: 300; color: var(--nord8); font-family: 'SF Mono', Monaco, monospace; }
    .stat-label { font-size: 11px; color: var(--nord4); text-transform: uppercase; letter-spacing: 1px; margin-top: 5px; }

    .controls { margin: 30px 0; display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; }
    button {
      padding: 14px 28px; border: none; border-radius: 6px; cursor: pointer;
      font-size: 13px; font-weight: 500; letter-spacing: 0.5px;
      transition: all 0.2s; text-transform: uppercase;
    }
    button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
    button:active { transform: translateY(0); }
    .btn-primary { background: var(--nord10); color: var(--nord6); }
    .btn-primary:hover { background: var(--nord9); }
    .btn-danger { background: var(--nord11); color: var(--nord6); }
    .btn-danger:hover { background: #C5727A; }
    .btn-secondary { background: var(--nord2); color: var(--nord6); border: 1px solid var(--nord3); }
    .btn-secondary:hover { background: var(--nord3); }

    .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--nord3); text-align: center; color: var(--nord3); font-size: 11px; letter-spacing: 1px; }
  </style>
</head>
<body>
  <div class="header">
    <h1>SMART SOCKS</h1>
    <div class="subtitle">Real-Time Sensor Dashboard · ELEC-E7840</div>
  </div>

  <div id="status">
    <strong>Status:</strong> <span id="conn-status">Connecting...</span>
    <span id="recording-status" class="recording" style="display:none;"> ● RECORDING</span>
    <div id="device-info" style="margin-top:10px;font-size:11px;color:var(--nord3);"></div>
  </div>

  <div class="sensor-grid" id="sensors">
    <div class="row-label">Left Leg</div>
    <div class='sensor-box'>
      <div class='sensor-name'>)rawliteral" + String(SENSOR_NAMES[0]) + R"rawliteral(</div>
      <div class='sensor-value' id='val-0'>-</div>
      <div class='sensor-bar'><div class='sensor-bar-fill' id='bar-0' style='width:0%'></div></div>
    </div>
    <div class='sensor-box'>
      <div class='sensor-name'>)rawliteral" + String(SENSOR_NAMES[1]) + R"rawliteral(</div>
      <div class='sensor-value' id='val-1'>-</div>
      <div class='sensor-bar'><div class='sensor-bar-fill' id='bar-1' style='width:0%'></div></div>
    </div>
    <div class='sensor-box'>
      <div class='sensor-name'>)rawliteral" + String(SENSOR_NAMES[2]) + R"rawliteral(</div>
      <div class='sensor-value' id='val-2'>-</div>
      <div class='sensor-bar'><div class='sensor-bar-fill' id='bar-2' style='width:0%'></div></div>
    </div>
    <div class="row-label">Right Leg</div>
    <div class='sensor-box'>
      <div class='sensor-name'>)rawliteral" + String(SENSOR_NAMES[3]) + R"rawliteral(</div>
      <div class='sensor-value' id='val-3'>-</div>
      <div class='sensor-bar'><div class='sensor-bar-fill' id='bar-3' style='width:0%'></div></div>
    </div>
    <div class='sensor-box'>
      <div class='sensor-name'>)rawliteral" + String(SENSOR_NAMES[4]) + R"rawliteral(</div>
      <div class='sensor-value' id='val-4'>-</div>
      <div class='sensor-bar'><div class='sensor-bar-fill' id='bar-4' style='width:0%'></div></div>
    </div>
    <div class='sensor-box'>
      <div class='sensor-name'>)rawliteral" + String(SENSOR_NAMES[5]) + R"rawliteral(</div>
      <div class='sensor-value' id='val-5'>-</div>
      <div class='sensor-bar'><div class='sensor-bar-fill' id='bar-5' style='width:0%'></div></div>
    </div>
  </div>

  <div class="stats">
    <div class="stat-box">
      <div class="stat-value" id="sample-rate">-</div>
      <div class="stat-label">Samples/sec</div>
    </div>
    <div class="stat-box">
      <div class="stat-value" id="sample-count">0</div>
      <div class="stat-label">Total Samples</div>
    </div>
    <div class="stat-box">
      <div class="stat-value" id="uptime">0s</div>
      <div class="stat-label">Uptime</div>
    </div>
  </div>

  <div class="controls">
    <button class="btn-primary" onclick="startRecording()">Start Recording</button>
    <button class="btn-danger" onclick="stopRecording()">Stop Recording</button>
    <button class="btn-secondary" onclick="downloadData()">Download CSV</button>
    <button class="btn-secondary" onclick="resetMinMax()">Reset Min/Max</button>
  </div>

  <script>
    let sampleCount = 0;
    let lastSampleTime = 0;
    let minValues = [4095, 4095, 4095, 4095, 4095, 4095];
    let maxValues = [0, 0, 0, 0, 0, 0];
    let sensorNames = [')rawliteral" + String(SENSOR_NAMES[0]) + R"rawliteral(', ')rawliteral" + String(SENSOR_NAMES[1]) + R"rawliteral(', ')rawliteral" + String(SENSOR_NAMES[2]) + R"rawliteral(', ')rawliteral" + String(SENSOR_NAMES[3]) + R"rawliteral(', ')rawliteral" + String(SENSOR_NAMES[4]) + R"rawliteral(', ')rawliteral" + String(SENSOR_NAMES[5]) + R"rawliteral('];

    function connect() {
      fetch('/api/sensors').then(r => r.json()).then(data => {
        document.getElementById('conn-status').textContent = 'Connected (HTTP)';
        document.getElementById('conn-status').style.color = '#4fbdba';
      }).catch(() => {
        document.getElementById('conn-status').textContent = 'Disconnected';
        document.getElementById('conn-status').style.color = '#e94560';
      });

      // Fetch device info
      fetch('/api/info').then(r => r.json()).then(data => {
        const infoEl = document.getElementById('device-info');
        infoEl.innerHTML = `MAC: ${data.mac} | IP: ${data.ip} | Mode: ${data.mode}`;
      }).catch(() => {});
    }

    function updateDisplay() {
      fetch('/api/sensors').then(r => r.json()).then(data => {
        const sensors = data.s;
        for (let i = 0; i < 6; i++) {
          const val = sensors[sensorNames[i]];
          document.getElementById('val-' + i).textContent = val;
          document.getElementById('bar-' + i).style.width = (val / 40.95) + '%';
          minValues[i] = Math.min(minValues[i], val);
          maxValues[i] = Math.max(maxValues[i], val);
        }

        sampleCount++;
        document.getElementById('sample-count').textContent = sampleCount;

        const now = Date.now();
        if (lastSampleTime) {
          const rate = 1000 / (now - lastSampleTime);
          document.getElementById('sample-rate').textContent = rate.toFixed(1);
        }
        lastSampleTime = now;
      });
    }

    function startRecording() {
      fetch('/api/start', {method: 'POST'});
      document.getElementById('recording-status').style.display = 'inline';
    }

    function stopRecording() {
      fetch('/api/stop', {method: 'POST'});
      document.getElementById('recording-status').style.display = 'none';
    }

    function downloadData() {
      window.location = '/api/download';
    }

    function resetMinMax() {
      minValues = [4095, 4095, 4095, 4095, 4095, 4095];
      maxValues = [0, 0, 0, 0, 0, 0];
    }

    setInterval(() => {
      document.getElementById('uptime').textContent = Math.floor(performance.now()/1000) + 's';
    }, 1000);

    setInterval(updateDisplay, 100);
    connect();
  </script>
</body>
</html>
)rawliteral";

  server.send(200, "text/html", html);
}

void handleAPIStart() {
  startRecording();
  server.send(200, "application/json", "{\"status\":\"recording\"}");
}

void handleAPIStop() {
  stopRecording();
  server.send(200, "application/json", "{\"status\":\"stopped\",\"samples\":" + String(sampleCount) + "}");
}

void handleAPIDownload() {
  String filename = "smart_socks_" + String(millis()) + ".csv";
  server.sendHeader("Content-Disposition", "attachment; filename=\"" + filename + "\"");
  server.send(200, "text/csv", dataBuffer);
}

void handleSensorData() {
  server.send(200, "application/json", readSensorsJSON());
}

void handleDeviceInfo() {
  server.send(200, "application/json", getDeviceInfoJSON());
}

void handleNotFound() {
  server.send(404, "application/json", "{\"error\":\"Not found\"}");
}

// ============== COMMAND PROCESSING ==============

void processCommand(String cmd) {
  cmd.trim();
  cmd.toUpperCase();

  if (cmd == "START" || cmd == "S") {
    startRecording();
  }
  else if (cmd == "STOP" || cmd == "X") {
    stopRecording();
  }
  else if (cmd == "STATUS") {
    printStatus();
  }
  else if (cmd == "HELP" || cmd == "?") {
    printHelp();
  }
}

void printStatus() {
  Serial.println("\n=== Smart Socks Status ===");
  Serial.print("WiFi: ");
  if (WiFi.getMode() == WIFI_STA || WiFi.getMode() == WIFI_AP_STA) {
    Serial.println(WiFi.localIP());
  } else {
    Serial.println(WiFi.softAPIP());
  }
  Serial.print("BLE Connected: ");
  Serial.println(bleDeviceConnected ? "Yes" : "No");
  Serial.print("Recording: ");
  Serial.println(isRecording ? "Yes" : "No");
  Serial.print("Samples: ");
  Serial.println(sampleCount);
  Serial.println();
}

void printHelp() {
  Serial.println("\n=== Smart Socks Commands ===");
  Serial.println("START / S      - Start recording");
  Serial.println("STOP / X       - Stop recording");
  Serial.println("STATUS         - Show status");
  Serial.println("HELP / ?       - Show this help");

  Serial.print("\nWeb: http://");
  if (WiFi.getMode() == WIFI_STA || WiFi.getMode() == WIFI_AP_STA) {
    Serial.println(WiFi.localIP());
  } else {
    Serial.println(WiFi.softAPIP());
  }
  Serial.println();
}

// ============== SETUP & LOOP ==============

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);

  Serial.println("\n========================================");
  Serial.println("Smart Socks - Data Collection (6 Sensors)");
  Serial.println("========================================\n");

  // Configure ADC
  analogReadResolution(ADC_RESOLUTION);
  analogSetAttenuation(ADC_11db);

  // Configure sensor pins
  for (int i = 0; i < NUM_SENSORS; i++) {
    pinMode(SENSOR_PINS[i], INPUT);
  }

  // Get MAC address for device identification
  deviceMAC = WiFi.macAddress();

  Serial.println("Device Information:");
  Serial.print("  MAC Address: ");
  Serial.println(deviceMAC);
  Serial.print("  Hostname: ");
  Serial.println(deviceHostname);
  Serial.print("  Sensors: ");
  Serial.println(NUM_SENSORS);
  Serial.println();

  // Initialize BLE BEFORE WiFi (shared antenna, BLE needs to init first)
  BLEDevice::init(BLE_DEVICE_NAME);
  bleServer = BLEDevice::createServer();
  bleServer->setCallbacks(new SmartSocksServerCallbacks());

  BLEService *pService = bleServer->createService(BLE_SERVICE_UUID);

  bleSensorChar = pService->createCharacteristic(
    BLE_CHAR_SENSOR,
    BLECharacteristic::PROPERTY_READ |
    BLECharacteristic::PROPERTY_NOTIFY
  );
  bleSensorChar->addDescriptor(new BLE2902());

  bleCommandChar = pService->createCharacteristic(
    BLE_CHAR_COMMAND,
    BLECharacteristic::PROPERTY_WRITE
  );
  bleCommandChar->setCallbacks(new BLECommandCallbacks());
  bleCommandChar->addDescriptor(new BLE2902());

  pService->start();

  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(BLE_SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);
  pAdvertising->setMaxPreferred(0x12);
  BLEDevice::startAdvertising();

  Serial.println("BLE Advertising started");
  Serial.print("BLE Device Name: ");
  Serial.println(BLE_DEVICE_NAME);

  // Auto-connect WiFi: scan → match saved networks → connect strongest → fallback AP
  WiFi.mode(WIFI_STA);
  WiFi.setHostname(deviceHostname.c_str());

  Serial.println("Scanning for WiFi networks...");
  int numNetworks = WiFi.scanNetworks();
  Serial.print("  Found ");
  Serial.print(numNetworks);
  Serial.println(" networks");

  // Find best matching saved network (strongest RSSI)
  int bestIndex = -1;
  int bestRSSI = -999;
  String bestSSID = "";
  const char* bestPassword = NULL;
  bool bestIsOpen = false;

  for (int i = 0; i < numNetworks; i++) {
    String scannedSSID = WiFi.SSID(i);
    int rssi = WiFi.RSSI(i);
    bool isOpen = (WiFi.encryptionType(i) == WIFI_AUTH_OPEN);

    // Check against saved networks
    for (int j = 0; j < NUM_SAVED_NETWORKS; j++) {
      if (scannedSSID == SAVED_NETWORKS[j].ssid && rssi > bestRSSI) {
        bestIndex = i;
        bestRSSI = rssi;
        bestSSID = scannedSSID;
        bestPassword = SAVED_NETWORKS[j].password;
        bestIsOpen = false;
        break;
      }
    }

    // Track strongest open network as fallback
    if (ALLOW_OPEN_NETWORKS && isOpen && bestIndex == -1 && rssi > bestRSSI) {
      bestIndex = i;
      bestRSSI = rssi;
      bestSSID = scannedSSID;
      bestPassword = NULL;
      bestIsOpen = true;
    }
  }

  WiFi.scanDelete();  // Free scan memory

  bool wifiConnected = false;

  if (bestIndex >= 0) {
    Serial.print("Connecting to: ");
    Serial.print(bestSSID);
    Serial.print(" (RSSI: ");
    Serial.print(bestRSSI);
    Serial.print(")");
    if (bestIsOpen) Serial.print(" [open]");
    Serial.println();

    if (bestPassword && strlen(bestPassword) > 0) {
      WiFi.begin(bestSSID.c_str(), bestPassword);
    } else {
      WiFi.begin(bestSSID.c_str());
    }

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
      delay(500);
      Serial.print(".");
      attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
      wifiConnected = true;
      Serial.println();
      Serial.print("  WiFi Connected! IP: ");
      Serial.println(WiFi.localIP());

      if (MDNS.begin(deviceHostname.c_str())) {
        Serial.print("  mDNS: http://");
        Serial.print(deviceHostname);
        Serial.println(".local");
        MDNS.addService("http", "tcp", 80);
      }
    } else {
      Serial.println("\n  Connection failed");
    }
  } else {
    Serial.println("  No saved networks found");
  }

  // Fallback to AP mode
  if (!wifiConnected) {
    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_PASSWORD, AP_CHANNEL);
    IPAddress localIP(192, 168, 4, 1);
    IPAddress gateway(192, 168, 4, 1);
    IPAddress subnet(255, 255, 255, 0);
    WiFi.softAPConfig(localIP, gateway, subnet);
    Serial.print("  AP Mode: ");
    Serial.print(AP_SSID);
    Serial.print(" @ ");
    Serial.println(WiFi.softAPIP());
  }

  // Setup HTTP server
  server.on("/", HTTP_GET, handleRoot);
  server.on("/api/sensors", HTTP_GET, handleSensorData);
  server.on("/api/info", HTTP_GET, handleDeviceInfo);
  server.on("/api/start", HTTP_POST, handleAPIStart);
  server.on("/api/stop", HTTP_POST, handleAPIStop);
  server.on("/api/download", HTTP_GET, handleAPIDownload);
  server.onNotFound(handleNotFound);
  server.begin();
  Serial.println("HTTP Server started on port 80");

  Serial.println("\n========================================");

  printHelp();
}

void loop() {
  // Handle HTTP clients
  server.handleClient();

  // Check for serial commands
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    processCommand(cmd);
  }

  unsigned long currentTime = millis();

  // Sensor sampling at 50 Hz
  static unsigned long lastSampleTime = 0;
  if (currentTime - lastSampleTime >= SAMPLE_INTERVAL_MS) {
    lastSampleTime = currentTime;

    // Read sensors
    String csvLine = readSensorsCSV();
    String jsonData = readSensorsJSON();

    // Send to Serial
    if (isRecording) {
      Serial.println(csvLine);
    }

    // Send to BLE (chunked)
    if (bleDeviceConnected) {
      sendBLEChunked(jsonData + "\n");
    }

    // Buffer for HTTP download
    if (isRecording) {
      dataBuffer += csvLine + "\n";
      bufferLineCount++;
      sampleCount++;

      // Prevent buffer overflow
      if (bufferLineCount > MAX_BUFFER_LINES) {
        // Keep header and last 500 lines
        int headerEnd = dataBuffer.indexOf('\n') + 1;
        int cutoffPos = dataBuffer.lastIndexOf('\n', dataBuffer.length() - 100);
        if (cutoffPos > headerEnd) {
          dataBuffer = dataBuffer.substring(0, headerEnd) + dataBuffer.substring(cutoffPos + 1);
          bufferLineCount = 500;
        }
      }
    }
  }

  // Reconnect BLE if disconnected
  if (!bleDeviceConnected) {
    static unsigned long lastAdvTime = 0;
    if (currentTime - lastAdvTime > 2000) {
      lastAdvTime = currentTime;
      BLEDevice::startAdvertising();
    }
  }
}
