/*
 * Smart Socks - Single Leg Data Collection (6-Sensor Config)
 * ELEC-E7840 Smart Wearables (Aalto University)
 *
 * Hardware: ESP32S3 XIAO with 10kΩ voltage dividers
 * Sensors: 3 per leg (2 pressure: heel + ball, 1 stretch: knee)
 *
 * Each leg has its own ESP32. Use LEG_ID to configure left/right.
 * Supports synchronization between two ESP32s via broadcast UDP.
 *
 * Features:
 * - BLE: Real-time sensor monitoring
 * - WiFi: HTTP server for data streaming
 * - UDP Sync: Synchronize with other leg's ESP32
 * - Serial: Debug and command interface
 * - Timestamp: Milliseconds since boot (or synchronized epoch)
 */

#include <WiFi.h>
#include <WebServer.h>
#include <WiFiUdp.h>
#include <ESPmDNS.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <ArduinoJson.h>

// ============== CONFIGURATION ==============

// Leg identifier - set via build flags or manually
// LEFT_LEG  = Left leg ESP32 (IP: 192.168.4.1)
// RIGHT_LEG = Right leg ESP32 (IP: 192.168.4.2)
enum LegID { LEFT_LEG, RIGHT_LEG };

// Use build flag if defined, otherwise default to LEFT
#if defined(LEG_ID_LEFT)
  const LegID LEG_ID = LEFT_LEG;
#elif defined(LEG_ID_RIGHT)
  const LegID LEG_ID = RIGHT_LEG;
#else
  // Manual configuration (change this if not using build flags)
  const LegID LEG_ID = LEFT_LEG;
#endif

// WiFi Configuration
// Choose ONE mode by uncommenting the appropriate section:

// MODE 1: AP Mode (default) - ESP32 creates its own network
// Best for: Quick testing, no existing WiFi available
// #define USE_AP_MODE

// MODE 2: Station Mode - Connect to existing WiFi/lab network
// Best for: Lab use with known network
// MODE 3: Phone Hotspot (RECOMMENDED for demos)
// Best for: Mobile demos, full control over network
#define USE_PHONE_HOTSPOT
// Credentials are in credentials.h (not committed to git)

// Include WiFi credentials from separate file (not committed to git)
// See credentials.h.template for setup instructions
#include "credentials.h"

// Device identification (works in all modes)
// The ESP32 will display its MAC address on startup
// You can identify devices by MAC instead of IP
String deviceMAC;
String deviceHostname;

// AP channel (not sensitive)
const int AP_CHANNEL = 6;

// BLE Configuration
#define BLE_DEVICE_NAME_LEFT  "SmartSocks-Left"
#define BLE_DEVICE_NAME_RIGHT "SmartSocks-Right"
#define BLE_SERVICE_UUID      "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define BLE_CHAR_SENSOR       "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#define BLE_CHAR_COMMAND      "beb5483e-36e1-4688-b7f5-ea07361b26a9"

// Unified pin mapping: Same pins as calibration mode
// Left leg: A0, A1, A2 | Right leg: A3, A4, A5
// This matches calibration_all_sensors.ino pinout
const int SENSOR_PINS_LEFT[] = {A0, A1, A2};
const int SENSOR_PINS_RIGHT[] = {A3, A4, A5};
const int* SENSOR_PINS = (LEG_ID == LEFT_LEG) ? SENSOR_PINS_LEFT : SENSOR_PINS_RIGHT;

const char* SENSOR_NAMES_LEFT[] = {"L_P_Heel", "L_P_Ball", "L_S_Knee"};
const char* SENSOR_NAMES_RIGHT[] = {"R_P_Heel", "R_P_Ball", "R_S_Knee"};
const char** SENSOR_NAMES = (LEG_ID == LEFT_LEG) ? SENSOR_NAMES_LEFT : SENSOR_NAMES_RIGHT;
const int NUM_SENSORS = 3;

// Sampling configuration
const int SAMPLE_RATE_HZ = 50;
const int SAMPLE_INTERVAL_MS = 1000 / SAMPLE_RATE_HZ;
const int ADC_RESOLUTION = 12;

// Synchronization
const int SYNC_PORT = 4210;
const unsigned long SYNC_INTERVAL_MS = 1000;  // Broadcast sync every 1s
const unsigned long SYNC_TIMEOUT_MS = 3000;   // Consider other leg offline after 3s

// ============== GLOBAL STATE ==============

// Web server
WebServer server(80);

// UDP for synchronization
WiFiUDP udp;
bool otherLegConnected = false;
IPAddress otherLegIP;
unsigned long lastSyncReceived = 0;
unsigned long timeOffset = 0;  // Offset to synchronize time with other leg

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

// Calibration mode
bool calibrationMode = false;

// Sync mode
enum SyncMode { SYNC_NONE, SYNC_MASTER, SYNC_SLAVE };
SyncMode syncMode = SYNC_NONE;

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

// ============== SYNCHRONIZATION ==============

void initSync() {
  udp.begin(SYNC_PORT);
  Serial.print("UDP Sync started on port ");
  Serial.println(SYNC_PORT);
  
  // Set other leg IP
  otherLegIP = (LEG_ID == LEFT_LEG) ? IPAddress(192, 168, 4, 2) : IPAddress(192, 168, 4, 1);
}

void broadcastSync() {
  if (syncMode != SYNC_MASTER) return;
  
  StaticJsonDocument<256> doc;
  doc["type"] = "sync";
  doc["leg"] = (LEG_ID == LEFT_LEG) ? "left" : "right";
  doc["time"] = millis();
  doc["recording"] = isRecording;
  
  String msg;
  serializeJson(doc, msg);
  
  udp.beginPacket(otherLegIP, SYNC_PORT);
  udp.print(msg);
  udp.endPacket();
}

void checkSyncMessages() {
  int packetSize = udp.parsePacket();
  if (packetSize) {
    char buffer[255];
    int len = udp.read(buffer, 255);
    if (len > 0) {
      buffer[len] = '\0';
      
      StaticJsonDocument<256> doc;
      DeserializationError error = deserializeJson(doc, buffer);
      
      if (!error) {
        const char* type = doc["type"];
        if (strcmp(type, "sync") == 0) {
          lastSyncReceived = millis();
          otherLegConnected = true;
          
          // If we're in slave mode, sync our recording state
          if (syncMode == SYNC_SLAVE && doc["recording"] != isRecording) {
            isRecording = doc["recording"];
            if (isRecording) {
              recordingStartTime = millis();
              sampleCount = 0;
              Serial.println("Sync: Recording started by master");
            } else {
              Serial.println("Sync: Recording stopped by master");
            }
          }
        }
        else if (strcmp(type, "trigger") == 0) {
          // Trigger signal - start recording simultaneously
          unsigned long triggerTime = doc["trigger_time"];
          unsigned long delayMs = triggerTime > millis() ? triggerTime - millis() : 0;
          
          Serial.print("Sync: Trigger received, starting in ");
          Serial.print(delayMs);
          Serial.println("ms");
          
          delay(delayMs);
          if (!isRecording) {
            startRecording();
          }
        }
      }
    }
  }
  
  // Check for timeout
  if (otherLegConnected && (millis() - lastSyncReceived > SYNC_TIMEOUT_MS)) {
    otherLegConnected = false;
    Serial.println("Sync: Other leg disconnected");
  }
}

void sendTrigger(unsigned long delayMs) {
  StaticJsonDocument<256> doc;
  doc["type"] = "trigger";
  doc["leg"] = (LEG_ID == LEFT_LEG) ? "left" : "right";
  doc["trigger_time"] = millis() + delayMs;
  
  String msg;
  serializeJson(doc, msg);
  
  // Send multiple times to ensure delivery
  for (int i = 0; i < 3; i++) {
    udp.beginPacket(otherLegIP, SYNC_PORT);
    udp.print(msg);
    udp.endPacket();
    delay(10);
  }
}

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

String getLegName() {
  return (LEG_ID == LEFT_LEG) ? "Left" : "Right";
}

String getLegIDStr() {
  return (LEG_ID == LEFT_LEG) ? "L" : "R";
}

String readSensorsJSON() {
  StaticJsonDocument<512> doc;
  doc["t"] = millis();
  doc["leg"] = (LEG_ID == LEFT_LEG) ? "left" : "right";
  doc["sync"] = otherLegConnected;
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
  doc["leg"] = (LEG_ID == LEFT_LEG) ? "left" : "right";
  doc["mac"] = deviceMAC;
  doc["hostname"] = deviceHostname;
  
#if defined(USE_PHONE_HOTSPOT)
  doc["mode"] = "hotspot";
  doc["ssid"] = HOTSPOT_SSID;
#elif defined(USE_EXISTING_WIFI)
  doc["mode"] = "station";
  doc["ssid"] = EXISTING_WIFI_SSID;
#else
  doc["mode"] = "ap";
  doc["ssid"] = AP_SSID;
#endif
  
  if (WiFi.getMode() == WIFI_STA || WiFi.getMode() == WIFI_AP_STA) {
    doc["ip"] = WiFi.localIP().toString();
  } else {
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
  line += "," + getLegIDStr();
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
  dataBuffer = "time_ms,leg," + String(SENSOR_NAMES[0]) + "," + 
               String(SENSOR_NAMES[1]) + "," + String(SENSOR_NAMES[2]) + "\n";
  Serial.println("Recording started");
}

void stopRecording() {
  isRecording = false;
  Serial.println("Recording stopped");
}

// ============== HTTP HANDLERS ==============

void handleRoot() {
  String legName = getLegName();
  String html = R"(
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Smart Socks · )" + legName + R"( Leg</title>
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
    .leg-badge { display: inline-block; background: var(--nord10); padding: 4px 12px; border-radius: 4px; margin-top: 10px; }
    
    #status { 
      margin: 20px 0; padding: 15px 20px; 
      background: var(--nord1); border-radius: 8px;
      border-left: 4px solid var(--nord8);
      font-family: monospace; font-size: 13px;
    }
    .recording { color: var(--nord11); font-weight: bold; }
    .sync-connected { color: var(--nord14); }
    .sync-disconnected { color: var(--nord11); }
    
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
    
    .sync-controls { background: var(--nord1); padding: 20px; border-radius: 8px; margin: 20px 0; }
    .sync-controls h3 { margin-top: 0; color: var(--nord8); font-weight: 400; }
    .sync-mode { display: flex; gap: 10px; margin: 10px 0; }
    .sync-mode label { display: flex; align-items: center; gap: 5px; color: var(--nord4); cursor: pointer; }
    
    .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--nord3); text-align: center; color: var(--nord3); font-size: 11px; letter-spacing: 1px; }
  </style>
</head>
<body>
  <div class="header">
    <h1>SMART SOCKS</h1>
    <div class="subtitle">Real-Time Sensor Calibration · ELEC-E7840</div>
    <div class="leg-badge">)" + legName + R"( Leg</div>
  </div>
  
  <div id="status">
    <strong>Status:</strong> <span id="conn-status">Connecting...</span>
    <span id="sync-status"></span>
    <span id="recording-status" class="recording" style="display:none;"> ● RECORDING</span>
    <div id="device-info" style="margin-top:10px;font-size:11px;color:var(--nord3);"></div>
  </div>
  
  <div class="sensor-grid" id="sensors">
    <div class='sensor-box'>
      <div class='sensor-name'>)" + String(SENSOR_NAMES[0]) + R"(</div>
      <div class='sensor-value' id='val-0'>-</div>
      <div class='sensor-bar'><div class='sensor-bar-fill' id='bar-0' style='width:0%'></div></div>
    </div>
    <div class='sensor-box'>
      <div class='sensor-name'>)" + String(SENSOR_NAMES[1]) + R"(</div>
      <div class='sensor-value' id='val-1'>-</div>
      <div class='sensor-bar'><div class='sensor-bar-fill' id='bar-1' style='width:0%'></div></div>
    </div>
    <div class='sensor-box'>
      <div class='sensor-name'>)" + String(SENSOR_NAMES[2]) + R"(</div>
      <div class='sensor-value' id='val-2'>-</div>
      <div class='sensor-bar'><div class='sensor-bar-fill' id='bar-2' style='width:0%'></div></div>
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
  
  <div class="sync-controls">
    <h3>Synchronization</h3>
    <div class="sync-mode">
      <label><input type="radio" name="sync" value="none" checked onchange="setSyncMode('none')"> Independent</label>
      <label><input type="radio" name="sync" value="master" onchange="setSyncMode('master')"> Master</label>
      <label><input type="radio" name="sync" value="slave" onchange="setSyncMode('slave')"> Slave</label>
    </div>
    <p style="font-size:12px;color:var(--nord4);">Use <strong>Master</strong> on one leg, <strong>Slave</strong> on the other for synchronized recording.</p>
  </div>
  
  <div class="controls">
    <button class="btn-primary" onclick="startRecording()">Start Recording</button>
    <button class="btn-danger" onclick="stopRecording()">Stop Recording</button>
    <button class="btn-secondary" onclick="downloadData()">Download CSV</button>
    <button class="btn-secondary" onclick="resetMinMax()">Reset Min/Max</button>
  </div>
  
  <script>
    let ws;
    let minValues = [4095, 4095, 4095];
    let maxValues = [0, 0, 0];
    let sampleCount = 0;
    let lastSampleTime = 0;
    let sensorNames = [')" + String(SENSOR_NAMES[0]) + R"(', ')" + String(SENSOR_NAMES[1]) + R"(', ')" + String(SENSOR_NAMES[2]) + R"('];
    
    function connect() {
      fetch('/api/sensors').then(r => r.json()).then(data => {
        document.getElementById('conn-status').textContent = 'Connected (HTTP)';
        document.getElementById('conn-status').style.color = '#4fbdba';
        updateSyncStatus(data.sync);
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
    
    function updateSyncStatus(sync) {
      const el = document.getElementById('sync-status');
      if (sync) {
        el.innerHTML = ' <span class="sync-connected">● Other Leg Connected</span>';
      } else {
        el.innerHTML = ' <span class="sync-disconnected">○ Other Leg Offline</span>';
      }
    }
    
    function updateDisplay() {
      fetch('/api/sensors').then(r => r.json()).then(data => {
        const sensors = data.s;
        for (let i = 0; i < 3; i++) {
          const val = sensors[sensorNames[i]];
          document.getElementById('val-' + i).textContent = val;
          document.getElementById('bar-' + i).style.width = (val / 40.95) + '%';
          minValues[i] = Math.min(minValues[i], val);
          maxValues[i] = Math.max(maxValues[i], val);
        }
        updateSyncStatus(data.sync);
        
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
    
    function setSyncMode(mode) {
      fetch('/api/sync/' + mode, {method: 'POST'});
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
      minValues = [4095, 4095, 4095];
      maxValues = [0, 0, 0];
    }
    
    setInterval(() => {
      document.getElementById('uptime').textContent = Math.floor(performance.now()/1000) + 's';
    }, 1000);
    
    setInterval(updateDisplay, 100);
    connect();
  </script>
</body>
</html>
)";

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
  String legID = getLegIDStr();
  String filename = "smart_socks_" + legID + "_" + String(millis()) + ".csv";
  server.sendHeader("Content-Disposition", "attachment; filename=\"" + filename + "\"");
  server.send(200, "text/csv", dataBuffer);
}

void handleSensorData() {
  server.send(200, "application/json", readSensorsJSON());
}

void handleDeviceInfo() {
  server.send(200, "application/json", getDeviceInfoJSON());
}

void handleSyncMode() {
  String mode = server.pathArg(0);
  if (mode == "master") {
    syncMode = SYNC_MASTER;
    Serial.println("Sync mode: MASTER");
  } else if (mode == "slave") {
    syncMode = SYNC_SLAVE;
    Serial.println("Sync mode: SLAVE");
  } else {
    syncMode = SYNC_NONE;
    Serial.println("Sync mode: NONE");
  }
  server.send(200, "application/json", "{\"sync_mode\":\"" + mode + "\"}");
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
  else if (cmd == "TRIGGER") {
    // Trigger both legs to start simultaneously
    sendTrigger(100);  // 100ms delay for network latency
    delay(100);
    startRecording();
    Serial.println("Triggered synchronized start");
  }
  else if (cmd == "MASTER") {
    syncMode = SYNC_MASTER;
    Serial.println("Sync mode: MASTER");
  }
  else if (cmd == "SLAVE") {
    syncMode = SYNC_SLAVE;
    Serial.println("Sync mode: SLAVE");
  }
  else if (cmd == "SYNC OFF") {
    syncMode = SYNC_NONE;
    Serial.println("Sync mode: NONE");
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
  else if (cmd == "HELP" || cmd == "?") {
    printHelp();
  }
}

void printStatus() {
  Serial.println("\n=== " + getLegName() + " Leg Status ===");
  Serial.print("WiFi AP: ");
  Serial.println(WiFi.softAPIP());
  Serial.print("BLE Connected: ");
  Serial.println(bleDeviceConnected ? "Yes" : "No");
  Serial.print("Other Leg: ");
  Serial.println(otherLegConnected ? "Connected" : "Offline");
  Serial.print("Sync Mode: ");
  Serial.println(syncMode == SYNC_MASTER ? "Master" : (syncMode == SYNC_SLAVE ? "Slave" : "None"));
  Serial.print("Recording: ");
  Serial.println(isRecording ? "Yes" : "No");
  Serial.print("Samples: ");
  Serial.println(sampleCount);
  Serial.println();
}

void printHelp() {
  Serial.println("\n=== " + getLegName() + " Leg Commands ===");
  Serial.println("START / S      - Start recording");
  Serial.println("STOP / X       - Stop recording");
  Serial.println("TRIGGER        - Trigger synchronized start");
  Serial.println("MASTER         - Set as sync master");
  Serial.println("SLAVE          - Set as sync slave");
  Serial.println("SYNC OFF       - Disable sync");
  Serial.println("CAL ON/OFF     - Calibration mode");
  Serial.println("STATUS         - Show status");
  Serial.println("HELP / ?       - Show this help");
  Serial.println("\nWeb: http://" + String(WiFi.softAPIP()[0]) + "." + 
                String(WiFi.softAPIP()[1]) + "." + 
                String(WiFi.softAPIP()[2]) + "." + 
                String(WiFi.softAPIP()[3]));
  Serial.println();
}

// ============== SETUP & LOOP ==============

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  
  Serial.println("\n========================================");
  Serial.println("Smart Socks - " + getLegName() + " Leg Data Collection");
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
  deviceHostname = (LEG_ID == LEFT_LEG) ? "smartsocks-left" : "smartsocks-right";
  
  Serial.println("Device Information:");
  Serial.print("  Leg: ");
  Serial.println(getLegName());
  Serial.print("  MAC Address: ");
  Serial.println(deviceMAC);
  Serial.print("  Hostname: ");
  Serial.println(deviceHostname);
  Serial.println();
  
  // Setup WiFi based on selected mode
#if defined(USE_PHONE_HOTSPOT)
  // Mode 3: Phone Hotspot (RECOMMENDED for demos)
  WiFi.mode(WIFI_STA);
  WiFi.setHostname(deviceHostname.c_str());
  WiFi.begin(HOTSPOT_SSID, HOTSPOT_PASSWORD);
  
  Serial.print("Connecting to phone hotspot: ");
  Serial.println(HOTSPOT_SSID);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ Hotspot Connected!");
    Serial.print("  IP Address: ");
    Serial.println(WiFi.localIP());
    
    // Start mDNS responder
    if (MDNS.begin(deviceHostname.c_str())) {
      Serial.print("  mDNS: http://");
      Serial.print(deviceHostname);
      Serial.println(".local");
      MDNS.addService("http", "tcp", 80);
    }
  } else {
    Serial.println("\n✗ Hotspot connection failed!");
    Serial.println("  Check SSID/password and restart");
  }
  
#elif defined(USE_EXISTING_WIFI)
  // Mode 2: Connect to existing WiFi (lab network)
  WiFi.mode(WIFI_STA);
  WiFi.setHostname(deviceHostname.c_str());
  WiFi.begin(EXISTING_WIFI_SSID, EXISTING_WIFI_PASSWORD);
  
  Serial.print("Connecting to WiFi: ");
  Serial.println(EXISTING_WIFI_SSID);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ WiFi Connected!");
    Serial.print("  IP Address: ");
    Serial.println(WiFi.localIP());
    
    // Start mDNS responder
    if (MDNS.begin(deviceHostname.c_str())) {
      Serial.print("  mDNS: http://");
      Serial.print(deviceHostname);
      Serial.println(".local");
      MDNS.addService("http", "tcp", 80);
    }
  } else {
    Serial.println("\n✗ WiFi connection failed, falling back to AP mode");
    goto fallback_to_ap;
  }
  
#else
  // Mode 1: AP Mode (default) or fallback
  fallback_to_ap:
  WiFi.mode(WIFI_AP);
  WiFi.softAP(AP_SSID, AP_PASSWORD, AP_CHANNEL);
  
  IPAddress localIP(192, 168, 4, (LEG_ID == LEFT_LEG) ? 1 : 2);
  IPAddress gateway(192, 168, 4, 1);
  IPAddress subnet(255, 255, 255, 0);
  WiFi.softAPConfig(localIP, gateway, subnet);
  
  Serial.println("✓ AP Mode Started");
  Serial.print("  SSID: ");
  Serial.println(AP_SSID);
  Serial.print("  IP Address: ");
  Serial.println(WiFi.softAPIP());
#endif
  
  // Setup HTTP server
  server.on("/", HTTP_GET, handleRoot);
  server.on("/api/sensors", HTTP_GET, handleSensorData);
  server.on("/api/info", HTTP_GET, handleDeviceInfo);
  server.on("/api/start", HTTP_POST, handleAPIStart);
  server.on("/api/stop", HTTP_POST, handleAPIStop);
  server.on("/api/download", HTTP_GET, handleAPIDownload);
  server.on("/api/sync/" + String(".*"), HTTP_POST, handleSyncMode);
  server.onNotFound(handleNotFound);
  server.begin();
  Serial.println("HTTP Server started on port 80");
  
  // Initialize UDP sync
  initSync();
  
  // Initialize BLE
  const char* bleName = (LEG_ID == LEFT_LEG) ? BLE_DEVICE_NAME_LEFT : BLE_DEVICE_NAME_RIGHT;
  BLEDevice::init(bleName);
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
  Serial.println(bleName);
  Serial.println("\n========================================");
  
  printHelp();
}

void loop() {
  // Handle HTTP clients
  server.handleClient();
  
  // Handle mDNS
  MDNS.update();
  
  // Check for sync messages
  checkSyncMessages();
  
  // Check for serial commands
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    processCommand(cmd);
  }
  
  unsigned long currentTime = millis();
  
  // Broadcast sync if master
  static unsigned long lastSyncBroadcast = 0;
  if (syncMode == SYNC_MASTER && (currentTime - lastSyncBroadcast >= SYNC_INTERVAL_MS)) {
    lastSyncBroadcast = currentTime;
    broadcastSync();
  }
  
  // Sensor sampling at 50 Hz
  static unsigned long lastSampleTime = 0;
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
