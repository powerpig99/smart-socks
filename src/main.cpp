/*
 * Smart Socks - Calibration Mode (All 6 Sensors on One ESP32)
 * ELEC-E7840 Smart Wearables (Aalto University)
 *
 * Use this sketch for calibration only - connect all 6 sensors to one ESP32:
 *   A0: L_P_Heel    A3: R_P_Heel
 *   A1: L_P_Ball    A4: R_P_Ball  
 *   A2: L_S_Knee    A5: R_S_Knee
 *
 * For production data collection, use data_collection_leg.ino on two ESP32s.
 */

#include <WiFi.h>
#include <WebServer.h>

// ============== CONFIGURATION ==============

// Unified pin mapping: A0=Heel, A1=Ball, A2=Knee on EVERY ESP32
// Calibration mode: 6 sensors on A0-A5 (one ESP32)
// Production mode: 3 sensors on A0-A2 (two ESP32s, one per leg)
const int SENSOR_PINS[] = {A0, A1, A2, A3, A4, A5};
const char* SENSOR_NAMES[] = {
  "L_P_Heel",   // A0 - Left Heel Pressure
  "L_P_Ball",   // A1 - Left Ball Pressure
  "L_S_Knee",   // A2 - Left Knee Stretch
  "R_P_Heel",   // A3 - Right Heel Pressure (A0 on right ESP32)
  "R_P_Ball",   // A4 - Right Ball Pressure (A1 on right ESP32)
  "R_S_Knee"    // A5 - Right Knee Stretch (A2 on right ESP32)
};
const int NUM_SENSORS = 6;

// WiFi Configuration
const char* WIFI_SSID = "SmartSocks-Cal";
const char* WIFI_PASSWORD = "calibrate";

// Sampling
const int SAMPLE_RATE_HZ = 50;
const int SAMPLE_INTERVAL_MS = 1000 / SAMPLE_RATE_HZ;
const int ADC_RESOLUTION = 12;

// ============== GLOBALS ==============

WebServer server(80);

// ============== FUNCTION DECLARATIONS ==============

void handleRoot();
void handleSensors();

// ============== SETUP ==============

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  
  Serial.println("\n========================================");
  Serial.println("Smart Socks - CALIBRATION MODE");
  Serial.println("All 6 sensors on single ESP32");
  Serial.println("========================================\n");
  
  // Configure ADC
  analogReadResolution(ADC_RESOLUTION);
  analogSetAttenuation(ADC_11db);
  
  // Configure pins
  for (int i = 0; i < NUM_SENSORS; i++) {
    pinMode(SENSOR_PINS[i], INPUT);
  }
  
  Serial.println("Sensor mapping:");
  Serial.println("  A0 (GPIO 1) -> L_P_Heel  (Left Heel Pressure)");
  Serial.println("  A1 (GPIO 2) -> L_P_Ball  (Left Ball Pressure)");
  Serial.println("  A2 (GPIO 3) -> L_S_Knee  (Left Knee Stretch)");
  Serial.println("  A3 (GPIO 4) -> R_P_Heel  (Right Heel Pressure)");
  Serial.println("  A4 (GPIO 5) -> R_P_Ball  (Right Ball Pressure)");
  Serial.println("  A5 (GPIO 6) -> R_S_Knee  (Right Knee Stretch)");
  Serial.println();
  
  // Start WiFi
  WiFi.softAP(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("WiFi AP: ");
  Serial.println(WIFI_SSID);
  Serial.print("IP: ");
  Serial.println(WiFi.softAPIP());
  
  // Setup web server
  server.on("/", HTTP_GET, handleRoot);
  server.on("/api/sensors", HTTP_GET, handleSensors);
  server.begin();
  
  Serial.println("\nWeb dashboard: http://192.168.4.1");
  Serial.println("Python: python calibration_visualizer.py --port <serial_port>");
  Serial.println("\n========================================\n");
}

// ============== WEB HANDLERS ==============

void handleRoot() {
  String html = R"(
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Smart Socks · Calibration</title>
  <style>
    :root { --bg: #2E3440; --card: #3B4252; --text: #ECEFF4; --accent: #88C0D0; }
    body { font-family: system-ui; margin: 0; padding: 30px; background: var(--bg); color: var(--text); }
    h1 { font-weight: 300; letter-spacing: 3px; text-align: center; }
    .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; max-width: 800px; margin: 30px auto; }
    .sensor { background: var(--card); padding: 20px; border-radius: 8px; text-align: center; }
    .name { font-size: 12px; text-transform: uppercase; color: #81A1C1; }
    .value { font-size: 36px; font-weight: 300; color: var(--accent); margin: 10px 0; }
    .pin { font-size: 11px; color: #4C566A; }
    .bar { height: 6px; background: #2E3440; border-radius: 3px; margin-top: 10px; }
    .fill { height: 100%; background: linear-gradient(90deg, #88C0D0, #81A1C1); border-radius: 3px; transition: width 0.2s; }
  </style>
</head>
<body>
  <h1>SMART SOCKS · CALIBRATION</h1>
  <p style="text-align:center;color:#81A1C1">All 6 sensors on single ESP32</p>
  <div class="grid" id="sensors"></div>
  <script>
    const sensors = [
      {name: 'L_P_Heel', pin: 'A0'}, {name: 'L_P_Ball', pin: 'A1'}, {name: 'L_S_Knee', pin: 'A2'},
      {name: 'R_P_Heel', pin: 'A3'}, {name: 'R_P_Ball', pin: 'A4'}, {name: 'R_S_Knee', pin: 'A5'}
    ];
    const grid = document.getElementById('sensors');
    sensors.forEach((s, i) => {
      grid.innerHTML += `<div class="sensor">
        <div class="name">${s.name}</div>
        <div class="value" id="val-${i}">-</div>
        <div class="pin">Pin ${s.pin}</div>
        <div class="bar"><div class="fill" id="bar-${i}" style="width:0%"></div></div>
      </div>`;
    });
    setInterval(() => {
      fetch('/api/sensors').then(r => r.json()).then(data => {
        sensors.forEach((s, i) => {
          const v = data[s.name];
          document.getElementById(`val-${i}`).textContent = v;
          document.getElementById(`bar-${i}`).style.width = (v / 40.95) + '%';
        });
      });
    }, 100);
  </script>
</body>
</html>
)";
  server.send(200, "text/html", html);
}

void handleSensors() {
  String json = "{";
  for (int i = 0; i < NUM_SENSORS; i++) {
    if (i > 0) json += ",";
    json += "\"" + String(SENSOR_NAMES[i]) + "\":" + String(analogRead(SENSOR_PINS[i]));
  }
  json += "}";
  server.send(200, "application/json", json);
}

// ============== LOOP ==============

void loop() {
  server.handleClient();
  
  static unsigned long lastPrint = 0;
  unsigned long now = millis();
  
  if (now - lastPrint >= SAMPLE_INTERVAL_MS) {
    lastPrint = now;
    
    // Output CSV for Python visualizer
    Serial.print(now);
    for (int i = 0; i < NUM_SENSORS; i++) {
      Serial.print(",");
      Serial.print(analogRead(SENSOR_PINS[i]));
    }
    Serial.println();
  }
}
