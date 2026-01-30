# Smart Socks - WiFi & Bluetooth Testing Guide

**Testing wireless connectivity for dual ESP32 configuration**

---

## Configuration Overview

### WiFi Modes

**Mode 1: Station Mode (Existing WiFi)** ⭐ RECOMMENDED
- ESP32s connect to your lab WiFi (e.g., "aalto")
- Configured via `USE_EXISTING_WIFI` flag
- Requires 2 static IPs on your network

**Mode 2: Access Point Mode (Default)**
- ESP32s create their own WiFi network
- Same SSID for both: `SmartSocks`
- Different static IPs: 192.168.4.1 and 192.168.4.2

See [[WIFI_CONFIGURATION]] for setup details.

### WiFi Access Points (AP Mode)

| ESP32 | SSID | IP Address | Password |
|-------|------|------------|----------|
| Left Leg | `SmartSocks` | 192.168.4.1 | `smartwearables` |
| Right Leg | `SmartSocks` | 192.168.4.2 | `smartwearables` |
| Calibration | `SmartSocks-Cal` | 192.168.4.1 | `calibrate` |

> **Note:** Both production ESP32s use the same SSID but different IPs. Connect once to access both.

### BLE Device Names

| ESP32 | BLE Name | Service UUID |
|-------|----------|--------------|
| Left Leg | `SmartSocks-Left` | `4fafc201-1fb5-459e-8fcc-c5c9c331914b` |
| Right Leg | `SmartSocks-Right` | `4fafc201-1fb5-459e-8fcc-c5c9c331914b` |

---

## Test Procedure

### Step 1: WiFi AP Test

**1.1 Upload firmware to both ESP32s**
```bash
# Terminal 1 - Left Leg
pio run -e left_leg -t upload

# Terminal 2 - Right Leg
pio run -e right_leg -t upload
```

**1.2 Connect both ESP32s to USB power**

**1.3 Check WiFi networks**
```bash
# macOS
/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s | grep SmartSocks

# Or use WiFi menu - look for "SmartSocks" network
```

**AP Mode:** You should see one `SmartSocks` network.
**Station Mode:** No new network - ESP32s join your existing WiFi.

**1.4 Connect to Left Leg**

*AP Mode:*
1. Connect laptop to WiFi: `SmartSocks`
2. Open browser: http://192.168.4.1

*Station Mode:*
1. Ensure laptop is on same WiFi as ESP32s
2. Open browser: http://[LEFT_IP_STR] (e.g., http://192.168.1.101)

You should see the web dashboard with 3 sensors (L_P_Heel, L_P_Ball, L_S_Knee)

**1.5 Connect to Right Leg**

*AP Mode:* (Same network, different IP)
1. Already connected to `SmartSocks`
2. Open browser: http://192.168.4.2

*Station Mode:*
1. Open browser: http://[RIGHT_IP_STR] (e.g., http://192.168.1.102)

You should see the web dashboard with 3 sensors (R_P_Heel, R_P_Ball, R_S_Knee)

> **Alternative:** Use laptop + phone - connect laptop to left, phone to right.

---

### Step 2: BLE Test

**2.1 Install BLE scanner app**
- iOS: "nRF Connect" or "LightBlue"
- Android: "nRF Connect"
- macOS: Built-in Bluetooth menu (hold Option + click Bluetooth icon)

**2.2 Scan for BLE devices**
With both ESP32s powered on:

```bash
# macOS command line
blueutil --inquiry 10 | grep SmartSocks
```

Or use the app - you should see:
- `SmartSocks-Left`
- `SmartSocks-Right`

**2.3 Connect to BLE device**
Using nRF Connect app:
1. Scan for devices
2. Tap on `SmartSocks-Left`
3. Look for service UUID: `4fafc201-1fb5-459e-8fcc-c5c9c331914b`
4. Enable notifications on characteristic: `beb5483e-36e1-4688-b7f5-ea07361b26a8`
5. You should see JSON data streaming:
   ```json
   {"t":12345,"leg":"left","sync":false,"s":{"L_P_Heel":1234,"L_P_Ball":567,"L_S_Knee":890}}
   ```

---

### Step 3: Data Streaming Test

**3.1 WiFi HTTP Streaming**
```bash
# Get current sensor values
curl http://192.168.4.1/api/sensors

# Expected response:
# {"L_P_Heel":1234,"L_P_Ball":567,"L_S_Knee":890}
```

**3.2 Serial Monitor Check**
```bash
# Left leg
pio device monitor --port /dev/cu.usbmodem2101

# You should see CSV output:
# 0,L,1234,567,890
# 20,L,1235,568,891
```

**3.3 BLE Data Rate Test**
Using nRF Connect, check the data rate:
- Expected: ~50 messages/second (50Hz sampling)
- Each message: ~50-80 bytes JSON

---

### Step 4: Dual Connection Test (Advanced)

**4.1 Connect to both simultaneously**

*Station Mode (Existing WiFi) - RECOMMENDED:*
All devices on same network, access both ESP32s:

| Device | Connection | URL |
|--------|------------|-----|
| Laptop | WiFi → Lab Network | http://192.168.1.101 and http://192.168.1.102 |
| Phone | WiFi → Lab Network | Same URLs |
| Tablet | BLE → SmartSocks-Left | nRF Connect app |

*AP Mode:*
Laptop connects to `SmartSocks`, accesses both via different IPs:

| Device | Connection | URL |
|--------|------------|-----|
| Laptop | WiFi → SmartSocks | http://192.168.4.1 and http://192.168.4.2 |
| Phone | BLE → SmartSocks-Left | nRF Connect app |
| Phone | BLE → SmartSocks-Right | nRF Connect app |

**4.2 Python dual collector test**
```bash
python 04_Code/python/dual_collector.py --calibrate \
  --left-port /dev/cu.usbmodem2101 \
  --right-port /dev/cu.usbmodem2102
```

---

## Troubleshooting

### WiFi Issues

| Problem | Solution |
|---------|----------|
| Can't see "SmartSocks" network | ESP32 not powered? Check USB connection |
| Wrong IP address | Clear DHCP lease: `sudo ipconfig set en0 DHCP` |
| Page won't load | Try http://192.168.4.1 or http://192.168.4.2 |
| Can't see network | AP Mode: ESP32 powered? Station Mode: Check serial for connection status |
| WiFi keeps disconnecting | Check power supply - USB might not provide enough current for WiFi + BLE |

### BLE Issues

| Problem | Solution |
|---------|----------|
| Can't see BLE devices | ESP32 not advertising? Check serial output |
| Connection drops | Reduce distance, check for interference |
| No data received | Enable notifications in BLE app |
| Garbled data | BLE MTU issue - should be handled by chunking |

### Serial Issues

| Problem | Solution |
|---------|----------|
| No serial output | Wrong port? Check `pio device list` |
| Garbage characters | Wrong baud rate - should be 115200 |
| ESP32 keeps resetting | Check USB cable (needs data lines, not just power) |

---

## Quick Test Checklist

### WiFi Tests
- [ ] (AP Mode) `SmartSocks` WiFi network visible OR (Station Mode) ESP32s connected to existing WiFi
- [ ] Left leg web dashboard loads (http://[LEFT_IP])
- [ ] Right leg web dashboard loads (http://[RIGHT_IP])
- [ ] Both dashboards update in real-time

### BLE Tests
- [ ] `SmartSocks-Left` visible in BLE scanner
- [ ] `SmartSocks-Right` visible in BLE scanner
- [ ] BLE connection succeeds on Left
- [ ] BLE connection succeeds on Right
- [ ] Data streaming at ~50Hz
- [ ] JSON format correct

### Serial Tests
- [ ] CSV output on serial at 50Hz
- [ ] Correct sensor values
- [ ] No dropped packets

---

## Performance Expectations

| Metric | Expected | Notes |
|--------|----------|-------|
| WiFi Range | ~30m line-of-sight | Reduced with obstacles |
| BLE Range | ~10m | Class 2 Bluetooth |
| Data Rate | 50 samples/sec | Configurable in firmware |
| Latency | <20ms | WiFi + processing |
| Concurrent Clients | 4-8 | WiFi AP limit |

---

*Last updated: February 2026*
