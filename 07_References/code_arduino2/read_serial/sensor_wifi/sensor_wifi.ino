// =============================================================================
// sensor_wifi.ino — Single-Sensor WiFi Streaming to TCP Server
// =============================================================================
// This sketch reads one analog sensor (e.g., a pressure or stretch sensor)
// and streams the readings over WiFi to a Python TCP server running on a
// computer. The ESP32 acts as a WiFi station (client), connecting to an
// existing network (e.g., a phone hotspot), then opens a persistent TCP
// connection to push comma-separated sensor values at ~10 Hz.
//
// Data flow:
//   Analog sensor → ESP32 ADC → WiFi TCP → Python server (collector)
//
// Pair this with a Python TCP server script that listens on the same port
// (e.g., socket server on port 5000) to receive and log the data.
// =============================================================================

#include <WiFi.h> // ESP32 WiFi library (included with ESP32 Arduino core)

// -----------------------------------------------------------------------------
// WiFi credentials — the network the ESP32 will join as a station (client).
// In this example, it connects to a phone hotspot named "zyyyyy".
// Replace these with your own SSID and password.
// -----------------------------------------------------------------------------
const char *ssid = "Jing_iPhoneAir";
const char *password = "powerpig";

// -----------------------------------------------------------------------------
// TCP server details — the IP and port of the computer running the Python
// receiver script. The IP must be the computer's address on the SAME network
// as the ESP32 (i.e., the hotspot's subnet). Find it with `ifconfig` (macOS)
// or `ipconfig` (Windows) after connecting your computer to the same hotspot.
// The port must match what the Python server is listening on.
// -----------------------------------------------------------------------------
const char *serverIP = "172.20.10.5";
const int serverPort = 5000;

// -----------------------------------------------------------------------------
// Sensor configuration
// - sensorPin1: The analog input pin connected to the sensor.
//   A5 maps to GPIO 4 on XIAO ESP32S3 (see board pinout).
// - sensorValue1: Variable to hold the latest ADC reading (0–4095 for 12-bit).
// -----------------------------------------------------------------------------
int sensorPin1 = A0;
int sensorValue1 = 0;

// Unused: a digital button input for testing, kept commented out as reference.
// const int buttonPin = 2;

// -----------------------------------------------------------------------------
// WiFiClient — the TCP socket object used to maintain a persistent connection
// to the Python server. Data is sent using client.print().
// -----------------------------------------------------------------------------
WiFiClient client;

// =============================================================================
// setup() — Runs once at power-on or reset.
// Responsibilities:
//   1. Initialize serial monitor for debug output (115200 baud).
//   2. Connect to the WiFi network (blocking until connected).
//   3. Open a TCP connection to the Python server (blocking until connected).
// =============================================================================

void ensureWiFiConnected() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi disconnected → reconnecting...");
        WiFi.disconnect(true);
        delay(100);
        WiFi.mode(WIFI_STA);
        WiFi.begin(ssid, password);

        int attempts = 0;
        while (WiFi.status() != WL_CONNECTED && attempts < 30) {
            delay(500);
            Serial.print(".");
            attempts++;
        }
        if (WiFi.status() == WL_CONNECTED) {
            Serial.println("\nWiFi reconnected. IP: " + WiFi.localIP().toString());
        } else {
            Serial.println("\nWiFi failed after 15s");
        }
    }
}

void setup()
{
    Serial.begin(115200); // Match baud rate with Serial Monitor / PlatformIO

    // Optional: block until Serial Monitor is open. Useful for debugging but
    // prevents the sketch from running without a connected computer, so it's
    // commented out for standalone operation.
    // while (!Serial);

    // --- Step 1: Connect to WiFi network ---
    WiFi.mode(WIFI_STA);           // Explicitly set station mode
    WiFi.setAutoReconnect(true);   // Auto-rejoin if WiFi drops
    WiFi.disconnect(true);         // Clear stale state from NVS flash
    delay(500);                    // Let radio initialize before begin()

    // Scan first to warm up radio (matches working main firmware pattern)
    Serial.println("Scanning for WiFi networks...");
    int numNetworks = WiFi.scanNetworks();
    bool found = false;
    for (int i = 0; i < numNetworks; i++) {
        Serial.print("  ["); Serial.print(i); Serial.print("] ");
        Serial.print(WiFi.SSID(i));
        Serial.print(" RSSI:"); Serial.println(WiFi.RSSI(i));
        if (WiFi.SSID(i) == ssid) found = true;
    }
    WiFi.scanDelete();

    if (!found) {
        Serial.print("SSID \""); Serial.print(ssid);
        Serial.println("\" not found in scan — restarting...");
        delay(2000);
        ESP.restart();
    }

    Serial.print("Connecting to WiFi...");
    WiFi.begin(ssid, password);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 40)
    {
        Serial.print(".");
        delay(500);
        attempts++;
    }

    if (WiFi.status() != WL_CONNECTED)
    {
        Serial.println("\nWiFi failed after 20s — restarting...");
        ESP.restart();
    }

    // WiFi connected — print the assigned IP address for debugging.
    // This IP is assigned by the hotspot's DHCP server.
    Serial.println("");
    Serial.println("Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP()); // e.g., 172.20.10.x

    // --- Step 2: Connect to the TCP server ---
    // client.connect() attempts a TCP handshake with the Python server.
    // If the server isn't running yet, this loop retries every 1 second.
    // NOTE: This blocks forever if the server is unreachable — in production
    // you'd add a retry limit or timeout.
    Serial.print("Connecting to server...");
    while (!client.connect(serverIP, serverPort))
    {
        Serial.print("."); // Visual heartbeat during connection attempts
        delay(1000);
    }
    Serial.println("Connected to server!");
}

// =============================================================================
// loop() — Runs repeatedly after setup() completes.
// Responsibilities:
//   1. Check if the TCP connection is still alive.
//   2. If connected: read the sensor, format the value, send it over TCP.
//   3. If disconnected: attempt to reconnect.
//
// Timing: delay(100) → ~10 readings per second (10 Hz).
// Each reading is sent as "<value>," (comma-terminated) so the Python server
// can split incoming data on commas to parse individual readings.
// =============================================================================
void loop()
{
    ensureWiFiConnected();
    
    if (client.connected())
    {
        // --- Read sensor ---
        // analogRead() returns a 12-bit value (0–4095) proportional to the
        // voltage on the pin (0–3.3V on ESP32). Higher values = more pressure
        // or stretch depending on the sensor type.
        sensorValue1 = analogRead(sensorPin1);

        // Unused: digital button read for testing purposes.
        // int test_value = digitalRead(buttonPin);

        // --- Format data ---
        // Convert the integer ADC value to a String and append a comma as a
        // delimiter. The Python server accumulates the TCP stream and splits
        // on commas to extract individual readings.
        // Example output: "2048," or "3500,"
        String data = String(sensorValue1) + ",";

        // --- Send over TCP ---
        // client.print() writes the string to the TCP socket. Unlike
        // client.println(), it does NOT append a newline — the comma serves
        // as the delimiter instead.
        client.print(data);

        // --- Debug output ---
        // Echo the sent data to Serial Monitor so you can verify readings
        // without needing to check the Python server side.
        Serial.print("Sent: ");
        Serial.println(data);

        // --- Pacing ---
        // 100 ms delay → ~10 Hz sample rate. Increase delay for slower rates,
        // decrease for faster (but watch for WiFi buffer saturation).
        delay(100);
    }
    else
    {
        // --- Reconnection logic ---
        // If the TCP connection drops (server closed, network glitch, etc.),
        // close the old socket cleanly with client.stop(), wait 2 seconds,
        // then attempt to reconnect. This runs in a loop since loop() is
        // called repeatedly — it will keep retrying every ~2 seconds.
        // NOTE: Does not re-check WiFi status. If WiFi itself dropped,
        // client.connect() will fail until WiFi reconnects (which ESP32
        // handles automatically by default with WiFi.setAutoReconnect(true)).
        Serial.println("Disconnected, reconnecting...");
        client.stop();                        // Release the old socket resources
        delay(2000);                          // Wait before retrying (avoid rapid-fire attempts)
        
        if (client.connect(serverIP, serverPort)) {
            Serial.println("TCP reconnected!");
        } else {
            Serial.println("TCP connect failed");
            delay(2000);
        }        

//        client.connect(serverIP, serverPort); // Try to reconnect
    }
}