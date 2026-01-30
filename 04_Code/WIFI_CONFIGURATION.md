# Smart Socks - Wireless Configuration Guide

**WiFi (AP / Station / Phone Hotspot) and BLE setup for dual ESP32**

---

## WiFi Mode 1: Station Mode (RECOMMENDED for Lab)

Connect ESP32s to your existing WiFi network (like `aalto` or lab WiFi).

### Setup

1. **Edit `data_collection_leg.ino`** (lines 35-48):

```cpp
// Uncomment to use existing WiFi:
#define USE_EXISTING_WIFI

// Set your lab WiFi credentials:
const char* EXISTING_WIFI_SSID = "aalto";           // Your WiFi name
const char* EXISTING_WIFI_PASSWORD = "password";    // Your WiFi password

// Static IPs - ask IT for 2 available IPs on your network:
const char* LEFT_IP_STR = "192.168.1.101";   // Left leg ESP32
const char* RIGHT_IP_STR = "192.168.1.102";  // Right leg ESP32
```

2. **Upload to both ESP32s**

3. **Access via browser:**
   - Left leg: http://192.168.1.101
   - Right leg: http://192.168.1.102

### Advantages
- Your laptop stays connected to normal WiFi
- Can access both ESP32s simultaneously
- Internet access while collecting data

### Requirements
- Need 2 available static IPs on your network
- Must know WiFi credentials
- Network must allow device-to-device communication

---

## WiFi Mode 2: Access Point Mode (Default)

Each ESP32 creates its own WiFi network.

### Setup

Leave `USE_EXISTING_WIFI` commented out (default):

```cpp
// Comment out or remove this line for AP mode:
// #define USE_EXISTING_WIFI
```

### Configuration

| ESP32 | Network Name | IP Address | Password |
|-------|--------------|------------|----------|
| Left | `SmartSocks` | 192.168.4.1 | `smartwearables` |
| Right | `SmartSocks` | 192.168.4.2 | `smartwearables` |

### Usage

1. Connect laptop to `SmartSocks` WiFi
2. Access left leg: http://192.168.4.1
3. Access right leg: http://192.168.4.2

### Limitations
- Laptop must disconnect from normal WiFi
- No internet access while connected

---

## WiFi Mode 3: Phone Hotspot (Mobile Demos)

Use your phone's hotspot for portable demos anywhere.

### Setup

Edit `data_collection_leg.ino`:

```cpp
#define USE_PHONE_HOTSPOT

const char* HOTSPOT_SSID = "YourPhoneName";      // e.g., "iPhone-Jing"
const char* HOTSPOT_PASSWORD = "yourpassword";
```

### Enable Hotspot

**iPhone:** Settings > Personal Hotspot > Turn On. Enable "Maximize Compatibility" (forces 2.4GHz).

**Android:** Settings > Network & Internet > Hotspot & Tethering > WiFi Hotspot > Turn On.

### Access Methods

- **IP Address:** Check serial output for assigned IP (e.g., http://172.20.10.4)
- **mDNS (recommended):** http://smartsocks-left.local / http://smartsocks-right.local
  - macOS: works out of the box
  - Windows: install Bonjour
  - Linux: `sudo apt install avahi-daemon`

### Hotspot Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection failed | Check password, ensure hotspot is on |
| Phone locked | Some phones disable hotspot when locked |
| 5GHz only | ESP32 only supports 2.4GHz - enable "Maximize Compatibility" on iPhone |
| IP keeps changing | Use mDNS hostnames instead (smartsocks-left.local) |

---

## Hybrid Mode (Fallback)

If `USE_EXISTING_WIFI` is enabled but the ESP32 fails to connect, it automatically falls back to AP mode:

```
Connecting to WiFi: aalto
.....
WiFi connection failed, falling back to AP mode
AP Mode IP: 192.168.4.1
```

---

## BLE Configuration

Both ESP32s also advertise via Bluetooth Low Energy for parallel or alternative data access.

| ESP32 | BLE Name | Service UUID |
|-------|----------|--------------|
| Left Leg | `SmartSocks-Left` | `4fafc201-1fb5-459e-8fcc-c5c9c331914b` |
| Right Leg | `SmartSocks-Right` | `4fafc201-1fb5-459e-8fcc-c5c9c331914b` |

**Characteristic UUID:** `beb5483e-36e1-4688-b7f5-ea07361b26a8`

### BLE Testing

1. Install a BLE scanner app (nRF Connect for iOS/Android)
2. Scan for `SmartSocks-Left` / `SmartSocks-Right`
3. Connect and enable notifications on the characteristic
4. Data streams as JSON:
   ```json
   {"t":12345,"leg":"left","sync":false,"s":{"L_P_Heel":1234,"L_P_Ball":567,"L_S_Knee":890}}
   ```

### BLE Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't see BLE devices | Check ESP32 power, check serial output |
| Connection drops | Reduce distance, check for interference |
| No data received | Enable notifications in BLE app |

---

## WiFi Testing Procedure

### Quick Checklist

- [ ] WiFi network visible (AP mode) or ESP32s connected to existing WiFi (Station mode)
- [ ] Left leg web dashboard loads
- [ ] Right leg web dashboard loads
- [ ] `curl http://[IP]/api/sensors` returns JSON with 3 sensor values
- [ ] Serial output at 115200 baud shows CSV data at 50Hz

### Data Streaming Test

```bash
# WiFi HTTP
curl http://192.168.4.1/api/sensors
# Expected: {"L_P_Heel":1234,"L_P_Ball":567,"L_S_Knee":890}

# Serial monitor
pio device monitor --port /dev/cu.usbmodem2101
```

### Performance Expectations

| Metric | Expected |
|--------|----------|
| WiFi Range | ~30m line-of-sight |
| BLE Range | ~10m |
| Data Rate | 50 samples/sec |
| Latency | <20ms |

---

## Upload Methods

### PlatformIO (Recommended)

```bash
pio run -e left_leg -t upload --upload-port /dev/cu.usbmodem2101
pio run -e right_leg -t upload --upload-port /dev/cu.usbmodem2102
```

### Arduino IDE

1. Install ESP32 board support (Boards Manager URL: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`)
2. Select board: **XIAO_ESP32S3**
3. Select port: `/dev/cu.usbmodem2101`
4. Set `LEG_ID` in code, then upload

---

## Python Data Collection

```bash
# Station Mode or Phone Hotspot (all on same network):
python dual_collector.py --calibrate

# AP Mode:
# 1. Connect laptop to "SmartSocks" WiFi
python dual_collector.py --calibrate --left-port auto --right-port auto
```

---

## Tips for Mobile Demos

1. Power both ESP32s from USB battery packs
2. Use mDNS hostnames to avoid IP confusion
3. Label each ESP32 with its MAC address
4. Test hotspot connection at demo location beforehand

---

*Last updated: January 2026*
