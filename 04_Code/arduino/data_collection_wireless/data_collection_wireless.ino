/*
 * Smart Socks - Wireless Data Collection
 * ELEC-E7840 Smart Wearables (Aalto University)
 *
 * Multi-mode data collection with BLE + WiFi support.
 * Supports real-time calibration via BLE and data streaming via WiFi.
 *
 * Hardware: ESP32S3 XIAO with 10kΩ voltage dividers
 * Sensors: 5 zones per sock (Heel, Arch, Metatarsal medial/lateral, Toe)
 *
 * Features:
 * - BLE: Real-time sensor monitoring and calibration
 * - WiFi: HTTP server for data streaming and OTA updates
 * - Serial: Debug and command interface
 */

#include <WiFi.h>
#include <WebServer.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <ArduinoJson.h>

// ============== CONFIGURATION ==============

// WiFi Configuration (AP Mode)
const char* WIFI_SSID = "SmartSocks";
const char* WIFI_PASSWORD = "smartwearables";
const int WIFI_CHANNEL = 6;

// BLE Configuration
#define BLE_DEVICE_NAME     "SmartSocks-BLE"
#define BLE_SERVICE_UUID    "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define BLE_CHAR_SENSOR     "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#define BLE_CHAR_COMMAND    "beb5483e-36e1-4688-b7f5-ea07361b26a9"

// Sensor pins (Left sock: A0-A4, Right sock: A5 + GPIO 7-10)
const int SENSOR_PINS[] = {A0, A1, A2, A3, A4, A5, 7, 8, 9, 10};
const char* SENSOR_NAMES[] = {
  "L_Heel", "L_Arch", "L_MetaM", "L_MetaL", "L_Toe",
  "R_Heel", "R_Arch", "R_MetaM", "R_MetaL", "R_Toe"
};
const int NUM_SENSORS = 10;

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

// Data buffer for HTTP streaming
String dataBuffer = "";
const int BUFFER_SIZE = 50;  // Number of samples to buffer
int bufferCount = 0;

// Calibration mode
bool calibrationMode = false;

// ============== BLE CALLBACKS ==============

class BLEServerCallbacks: public BLEServerCallbacks {
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
  
  // BLE MTU is typically 20 bytes, chunk data
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
  
  JsonObject sensors = doc.createNestedObject("s");
  for (int i = 0; i < NUM_SENSORS; i++) {
    sensors[SENSOR_NAMES[i]] = analogRead(SENSOR_PINS[i]);
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

// ============== HTTP HANDLERS ==============

void handleRoot() {
  String html = R"(
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Smart Socks · Calibration</title>
  <style>
    /* Nordic Design System */
    :root {
      --nord0: #2E3440;
      --nord1: #3B4252;
      --nord2: #434C5E;
      --nord3: #4C566A;
      --nord4: #D8DEE9;
      --nord5: #E5E9F0;
      --nord6: #ECEFF4;
      --nord7: #8FBCBB;
      --nord8: #88C0D0;
      --nord9: #81A1C1;
      --nord10: #5E81AC;
      --nord11: #BF616A;
      --nord12: #D08770;
      --nord13: #EBCB8B;
      --nord14: #A3BE8C;
      --nord15: #B48EAD;
    }
    
    * { box-sizing: border-box; }
    
    body { 
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      margin: 0;
      padding: 30px;
      background: var(--nord0);
      color: var(--nord6);
      line-height: 1.6;
    }
    
    /* Header */
    .header {
      text-align: center;
      margin-bottom: 30px;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--nord3);
    }
    
    h1 { 
      color: var(--nord6);
      font-weight: 300;
      font-size: 28px;
      letter-spacing: 4px;
      margin: 0;
    }
    
    .subtitle {
      color: var(--nord8);
      font-size: 12px;
      letter-spacing: 2px;
      margin-top: 5px;
    }
    
    /* Status Panel */
    #status { 
      margin: 20px 0; 
      padding: 15px 20px; 
      background: var(--nord1); 
      border-radius: 8px;
      border-left: 4px solid var(--nord8);
      font-family: monospace;
      font-size: 13px;
    }
    
    .recording { 
      color: var(--nord11); 
      font-weight: bold; 
    }
    
    /* Sensor Grid */
    .sensor-grid { 
      display: grid; 
      grid-template-columns: repeat(5, 1fr); 
      gap: 12px; 
      margin: 25px 0; 
    }
    
    .sensor-box { 
      background: var(--nord1); 
      padding: 18px 12px; 
      border-radius: 8px; 
      text-align: center;
      border: 1px solid var(--nord2);
      transition: border-color 0.3s;
    }
    
    .sensor-box:hover {
      border-color: var(--nord8);
    }
    
    .sensor-name { 
      font-size: 11px; 
      color: var(--nord4);
      text-transform: uppercase;
      letter-spacing: 1px;
      font-weight: 500;
    }
    
    .sensor-value { 
      font-size: 26px; 
      font-weight: 300;
      color: var(--nord8); 
      margin: 12px 0;
      font-family: 'SF Mono', Monaco, monospace;
    }
    
    .sensor-bar { 
      height: 6px; 
      background: var(--nord0); 
      border-radius: 3px; 
      overflow: hidden;
      margin-top: 8px;
    }
    
    .sensor-bar-fill { 
      height: 100%; 
      background: linear-gradient(90deg, var(--nord8), var(--nord9));
      transition: width 0.15s ease;
      border-radius: 3px;
    }
    
    /* Stats Grid */
    .stats { 
      display: grid; 
      grid-template-columns: repeat(3, 1fr); 
      gap: 15px; 
      margin: 25px 0; 
    }
    
    .stat-box { 
      background: var(--nord1); 
      padding: 20px; 
      border-radius: 8px; 
      text-align: center;
      border: 1px solid var(--nord2);
    }
    
    .stat-value { 
      font-size: 28px; 
      font-weight: 300;
      color: var(--nord8); 
      font-family: 'SF Mono', Monaco, monospace;
    }
    
    .stat-label { 
      font-size: 11px; 
      color: var(--nord4);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-top: 5px;
    }
    
    /* Controls */
    .controls { 
      margin: 30px 0;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      justify-content: center;
    }
    
    button { 
      padding: 12px 24px; 
      border: none; 
      border-radius: 6px; 
      cursor: pointer; 
      font-size: 13px;
      font-weight: 500;
      letter-spacing: 0.5px;
      transition: all 0.2s;
      text-transform: uppercase;
    }
    
    button:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    button:active {
      transform: translateY(0);
    }
    
    .btn-primary { 
      background: var(--nord10); 
      color: var(--nord6); 
    }
    
    .btn-primary:hover {
      background: var(--nord9);
    }
    
    .btn-danger { 
      background: var(--nord11); 
      color: var(--nord6); 
    }
    
    .btn-danger:hover {
      background: #C5727A;
    }
    
    .btn-secondary { 
      background: var(--nord2); 
      color: var(--nord6); 
      border: 1px solid var(--nord3);
    }
    
    .btn-secondary:hover {
      background: var(--nord3);
    }
    
    /* Footer */
    .footer {
      margin-top: 40px;
      padding-top: 20px;
      border-top: 1px solid var(--nord3);
      text-align: center;
      color: var(--nord3);
      font-size: 11px;
      letter-spacing: 1px;
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>SMART SOCKS</h1>
    <div class="subtitle">Real-Time Sensor Calibration · ELEC-E7840</div>
  </div>
  
  <div id="status">
    <strong>Status:</strong> <span id="conn-status">Connecting...</span>
    <span id="recording-status" class="recording" style="display:none;"> ● RECORDING</span>
  </div>
  
  <div class="sensor-grid" id="sensors">
)";

  for (int i = 0; i < NUM_SENSORS; i++) {
    html += "    <div class='sensor-box'>";
    html += "      <div class='sensor-name'>" + String(SENSOR_NAMES[i]) + "</div>";
    html += "      <div class='sensor-value' id='val-" + String(i) + "'>-</div>";
    html += "      <div class='sensor-bar'><div class='sensor-bar-fill' id='bar-" + String(i) + "' style='width:0%'></div></div>";
    html += "    </div>";
  }

  html += R"(
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
    let ws;
    let minValues = new Array(10).fill(4095);
    let maxValues = new Array(10).fill(0);
    let sampleCount = 0;
    let lastSampleTime = 0;
    
    function connect() {
      ws = new WebSocket('ws://' + window.location.host + '/ws');
      ws.onopen = () => {
        document.getElementById('conn-status').textContent = 'Connected (WebSocket)';
        document.getElementById('conn-status').style.color = '#4fbdba';
      };
      ws.onmessage = (e) => {
        const data = JSON.parse(e.data);
        updateDisplay(data);
      };
      ws.onclose = () => {
        document.getElementById('conn-status').textContent = 'Disconnected - Retrying...';
        document.getElementById('conn-status').style.color = '#e94560';
        setTimeout(connect, 2000);
      };
    }
    
    function updateDisplay(data) {
      const sensors = data.s;
      for (let i = 0; i < 10; i++) {
        const val = sensors[['L_Heel','L_Arch','L_MetaM','L_MetaL','L_Toe','R_Heel','R_Arch','R_MetaM','R_MetaL','R_Toe'][i]];
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
      minValues.fill(4095);
      maxValues.fill(0);
    }
    
    setInterval(() => {
      document.getElementById('uptime').textContent = Math.floor(performance.now()/1000) + 's';
    }, 1000);
    
    connect();
  </script>
</body>
</html>
)";

  server.send(200, "text/html", html);
}

void handleAPIStart() {
  isRecording = true;
  recordingStartTime = millis();
  sampleCount = 0;
  dataBuffer = "time_ms,L_Heel,L_Arch,L_MetaM,L_MetaL,L_Toe,R_Heel,R_Arch,R_MetaM,R_MetaL,R_Toe\n";
  server.send(200, "application/json", "{\"status\":\"recording\"}");
  Serial.println("HTTP: Recording started");
}

void handleAPIStop() {
  isRecording = false;
  server.send(200, "application/json", "{\"status\":\"stopped\",\"samples\":" + String(sampleCount) + "}");
  Serial.println("HTTP: Recording stopped");
}

void handleAPIDownload() {
  server.sendHeader("Content-Disposition", "attachment; filename=\"smart_socks_data.csv\"");
  server.send(200, "text/csv", dataBuffer);
}

void handleSensorData() {
  server.send(200, "application/json", readSensorsJSON());
}

void handleNotFound() {
  server.send(404, "application/json", "{\"error\":\"Not found\"}");
}

// ============== COMMAND PROCESSING ==============

void processCommand(String cmd) {
  cmd.trim();
  cmd.toUpperCase();
  
  if (cmd == "START") {
    isRecording = true;
    recordingStartTime = millis();
    sampleCount = 0;
    Serial.println("Recording started");
  }
  else if (cmd == "STOP") {
    isRecording = false;
    Serial.println("Recording stopped");
  }
  else if (cmd == "CAL ON") {
    calibrationMode = true;
    Serial.println("Calibration mode ON");
  }
  else if (cmd == "CAL OFF") {
    calibrationMode = false;
    Serial.println("Calibration mode OFF");
  }
  else if (cmd == "STATUS") {
    printStatus();
  }
  else if (cmd == "HELP") {
    printHelp();
  }
}

void printStatus() {
  Serial.println("\n=== Status ===");
  Serial.print("WiFi AP: ");
  Serial.println(WiFi.softAPIP());
  Serial.print("BLE Connected: ");
  Serial.println(bleDeviceConnected ? "Yes" : "No");
  Serial.print("Recording: ");
  Serial.println(isRecording ? "Yes" : "No");
  Serial.print("Calibration: ");
  Serial.println(calibrationMode ? "Yes" : "No");
  Serial.print("Samples: ");
  Serial.println(sampleCount);
  Serial.println();
}

void printHelp() {
  Serial.println("\n=== Commands ===");
  Serial.println("START      - Start recording");
  Serial.println("STOP       - Stop recording");
  Serial.println("CAL ON     - Enable calibration mode");
  Serial.println("CAL OFF    - Disable calibration mode");
  Serial.println("STATUS     - Show status");
  Serial.println("HELP       - Show this help");
  Serial.println("\nWeb Interface: http://192.168.4.1");
  Serial.println();
}

// ============== SETUP & LOOP ==============

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  
  Serial.println("\n========================================");
  Serial.println("Smart Socks - Wireless Data Collection");
  Serial.println("========================================\n");
  
  // Configure ADC
  analogReadResolution(ADC_RESOLUTION);
  analogSetAttenuation(ADC_11db);
  
  // Configure sensor pins
  for (int i = 0; i < NUM_SENSORS; i++) {
    pinMode(SENSOR_PINS[i], INPUT);
  }
  
  // Start WiFi AP
  WiFi.softAP(WIFI_SSID, WIFI_PASSWORD, WIFI_CHANNEL);
  IPAddress IP = WiFi.softAPIP();
  Serial.print("WiFi AP Started: ");
  Serial.println(WIFI_SSID);
  Serial.print("IP Address: ");
  Serial.println(IP);
  
  // Setup HTTP server
  server.on("/", HTTP_GET, handleRoot);
  server.on("/api/sensors", HTTP_GET, handleSensorData);
  server.on("/api/start", HTTP_POST, handleAPIStart);
  server.on("/api/stop", HTTP_POST, handleAPIStop);
  server.on("/api/download", HTTP_GET, handleAPIDownload);
  server.onNotFound(handleNotFound);
  server.begin();
  Serial.println("HTTP Server started on port 80");
  
  // Initialize BLE
  BLEDevice::init(BLE_DEVICE_NAME);
  bleServer = BLEDevice::createServer();
  bleServer->setCallbacks(new BLEServerCallbacks());
  
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
  
  // Sensor sampling at 50 Hz
  static unsigned long lastSampleTime = 0;
  unsigned long currentTime = millis();
  
  if (currentTime - lastSampleTime >= SAMPLE_INTERVAL_MS) {
    lastSampleTime = currentTime;
    
    // Read sensors
    String csvLine = readSensorsCSV();
    String jsonData = readSensorsJSON();
    
    // Send to Serial
    if (calibrationMode || isRecording) {
      Serial.println(csvLine);
    }
    
    // Send to BLE (chunked)
    if (bleDeviceConnected) {
      sendBLEChunked(jsonData + "\n");
    }
    
    // Buffer for HTTP download
    if (isRecording) {
      dataBuffer += csvLine + "\n";
      sampleCount++;
      
      // Prevent buffer overflow
      if (dataBuffer.length() > 50000) {
        // Keep only last 1000 lines
        int pos = dataBuffer.lastIndexOf('\n', dataBuffer.length() - 100);
        if (pos > 0) {
          dataBuffer = dataBuffer.substring(pos + 1);
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
