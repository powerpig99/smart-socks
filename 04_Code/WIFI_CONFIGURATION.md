# Smart Socks - Wireless Configuration Guide

**WiFi and BLE setup for ESP32S3 XIAO**

---

## WiFi Configuration

The firmware uses a `SAVED_NETWORKS[]` array in `src/credentials.h` (gitignored). On boot, it scans for available networks and connects to the strongest saved match.

### Setup

1. **Edit `src/credentials.h`** — add your networks:

```cpp
const WiFiNetwork SAVED_NETWORKS[] = {
    {"YourPhone-Hotspot", "your_password"}, // Phone hotspot
    // {"HomeWiFi", "home_password"},        // Home WiFi
    // {"aalto open", NULL},                 // Open networks — may block web interface
};

const bool ALLOW_OPEN_NETWORKS = false;  // Don't auto-connect to unknown open networks
```

2. **Upload firmware:** `pio run -t upload`

3. **Access web dashboard** at the IP shown in serial output, or via mDNS: http://smartsocks.local

### Boot Behavior

1. Scans for WiFi networks
2. Connects to the strongest saved match (up to 3 attempts on boot)
3. If not found, proceeds without WiFi — serial and sensors work regardless
4. Retries every 15s in the background:
   - First 3 retries: quick `WiFi.reconnect()` (instant, no scan freeze)
   - After that: full network scan (brief 2-5s pause)
5. Reconnects automatically when hotspot becomes available

### Important Notes

- **No AP mode** — firmware only connects to saved networks
- **Works on battery** — no USB host required; serial output is silently skipped
- **Aalto open WiFi** blocks device-to-device HTTP — unusable for web dashboard
- **iPhone hotspot:** Enable "Maximize Compatibility" (forces 2.4GHz, which ESP32 requires)

### Phone Hotspot Tips

| Problem | Solution |
|---------|----------|
| Connection failed | Check password, ensure hotspot is active |
| Phone locked | Some phones disable hotspot when locked |
| 5GHz only | ESP32 only supports 2.4GHz — enable "Maximize Compatibility" on iPhone |
| IP keeps changing | Use mDNS hostname (smartsocks.local) |

---

## BLE Configuration

The ESP32 advertises via Bluetooth Low Energy concurrently with WiFi.

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

### BLE Notes

- External antenna improves signal significantly on XIAO ESP32S3
- BLE is initialized before WiFi to avoid shared-antenna conflicts
- BLE advertising pauses during WiFi scans, resumes automatically

---

## Serial Streaming

- Sensor data streams at 50Hz over serial whenever a USB host is listening
- No START command needed — data flows automatically when the serial port is opened
- START/STOP only controls the CSV download buffer on the web dashboard
- On battery (no USB), serial output is silently skipped — no blocking

---

## Testing Checklist

- [ ] ESP32 connects to hotspot (check serial output or web dashboard)
- [ ] Web dashboard loads at device IP or smartsocks.local
- [ ] `curl http://[IP]/api/sensors` returns JSON with 6 sensor values
- [ ] Serial output shows CSV data at 50Hz when port is opened
- [ ] WiFi reconnects after hotspot is toggled off/on

---

## Tips for Mobile Demos

1. Power ESP32 from USB battery pack — works without USB host
2. Turn on phone hotspot before powering ESP32 (or wait for background retry)
3. Use mDNS hostname (smartsocks.local) to avoid IP confusion
4. Test hotspot connection at demo location beforehand

---

*Last updated: February 2026*
