# Smart Socks - Wireless Configuration Guide

**WiFi (AP / Station / Phone Hotspot) and BLE setup for ESP32**

---

## WiFi Mode 1: Station Mode (RECOMMENDED for Lab)

Connect ESP32 to your existing WiFi network (like `aalto` or lab WiFi).

### Setup

1. **Edit `credentials.h`** (in `data_collection_leg/`):

```cpp
#define EXISTING_WIFI_SSID "aalto"
#define EXISTING_WIFI_PASSWORD "password"
```

2. **In `data_collection_leg.ino`**, uncomment:
```cpp
#define USE_EXISTING_WIFI
```

3. **Upload firmware**

4. **Access via browser:**
   - http://smartsocks.local (mDNS)
   - Or check serial output for assigned IP

### Advantages
- Your laptop stays connected to normal WiFi
- Internet access while collecting data

### Requirements
- Must know WiFi credentials
- Network must allow device-to-device communication

---

## WiFi Mode 2: Access Point Mode (Default)

The ESP32 creates its own WiFi network.

### Setup

Leave `USE_EXISTING_WIFI` and `USE_PHONE_HOTSPOT` commented out (default).

### Configuration

| Setting | Value |
|---------|-------|
| Network | `SmartSocks` |
| IP Address | 192.168.4.1 |
| Password | `smartwearables` |

### Usage

1. Connect laptop to `SmartSocks` WiFi
2. Access dashboard: http://192.168.4.1

### Limitations
- Laptop must disconnect from normal WiFi
- No internet access while connected

---

## WiFi Mode 3: Phone Hotspot (Mobile Demos)

Use your phone's hotspot for portable demos anywhere.

### Setup

Edit `credentials.h`:

```cpp
#define HOTSPOT_SSID "YourPhoneName"
#define HOTSPOT_PASSWORD "yourpassword"
```

In `data_collection_leg.ino`:
```cpp
#define USE_PHONE_HOTSPOT
```

### Enable Hotspot

**iPhone:** Settings > Personal Hotspot > Turn On. Enable "Maximize Compatibility" (forces 2.4GHz).

**Android:** Settings > Network & Internet > Hotspot & Tethering > WiFi Hotspot > Turn On.

### Access Methods

- **IP Address:** Check serial output for assigned IP (e.g., http://172.20.10.4)
- **mDNS (recommended):** http://smartsocks.local
  - macOS: works out of the box
  - Windows: install Bonjour
  - Linux: `sudo apt install avahi-daemon`

### Hotspot Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection failed | Check password, ensure hotspot is on |
| Phone locked | Some phones disable hotspot when locked |
| 5GHz only | ESP32 only supports 2.4GHz - enable "Maximize Compatibility" on iPhone |
| IP keeps changing | Use mDNS hostname instead (smartsocks.local) |

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

The ESP32 advertises via Bluetooth Low Energy for parallel or alternative data access.

| Setting | Value |
|---------|-------|
| BLE Name | `SmartSocks` |
| Service UUID | `4fafc201-1fb5-459e-8fcc-c5c9c331914b` |
| Characteristic UUID | `beb5483e-36e1-4688-b7f5-ea07361b26a8` |

### BLE Testing

1. Install a BLE scanner app (nRF Connect for iOS/Android)
2. Scan for `SmartSocks`
3. Connect and enable notifications on the characteristic
4. Data streams as JSON:
   ```json
   {"t":12345,"mac":"AA:BB:CC:DD:EE:FF","s":{"L_P_Heel":1234,"L_P_Ball":567,"L_S_Knee":890,"R_P_Heel":1200,"R_P_Ball":550,"R_S_Knee":870}}
   ```

### BLE Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't see BLE device | Check ESP32 power, check serial output |
| Connection drops | Reduce distance, check for interference |
| No data received | Enable notifications in BLE app |

---

## WiFi Testing Procedure

### Quick Checklist

- [ ] WiFi network visible (AP mode) or ESP32 connected to existing WiFi (Station mode)
- [ ] Web dashboard loads at ESP32's IP
- [ ] `curl http://[IP]/api/sensors` returns JSON with 6 sensor values
- [ ] Serial output at 115200 baud shows CSV data at 50Hz

### Data Streaming Test

```bash
# WiFi HTTP
curl http://192.168.4.1/api/sensors
# Expected: {"t":12345,"mac":"...","s":{"L_P_Heel":1234,"L_P_Ball":567,...}}

# Serial monitor
pio device monitor -e xiao_esp32s3
```

### Performance Expectations

| Metric | Expected |
|--------|----------|
| WiFi Range | ~30m line-of-sight |
| BLE Range | ~10m |
| Data Rate | 50 samples/sec |
| Latency | <20ms |

---

## Upload

```bash
pio run -e xiao_esp32s3 -t upload
```

---

## Python Data Collection

```bash
# Station Mode or Phone Hotspot (all on same network):
python collector.py --calibrate

# Record activity
python collector.py --activity walking_forward --port /dev/cu.usbmodem2101
```

---

## Tips for Mobile Demos

1. Power ESP32 from USB battery pack
2. Use mDNS hostname to avoid IP confusion
3. Label ESP32 with its MAC address
4. Test hotspot connection at demo location beforehand

---

*Last updated: January 2026*
