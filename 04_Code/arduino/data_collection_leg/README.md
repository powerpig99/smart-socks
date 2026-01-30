# Smart Socks - Data Collection Firmware

## Overview

This sketch runs on a **single ESP32S3 XIAO** reading all 6 sensors (A0-A5):

| Pin | Sensor | Type | Location |
|-----|--------|------|----------|
| A0 | L_P_Heel | Pressure | Left heel |
| A1 | L_P_Ball | Pressure | Left ball of foot |
| A2 | L_S_Knee | Stretch | Left knee |
| A3 | R_P_Heel | Pressure | Right heel |
| A4 | R_P_Ball | Pressure | Right ball of foot |
| A5 | R_S_Knee | Stretch | Right knee |

## Features

- **WiFi:** HTTP server with web dashboard (AP, Station, or Phone Hotspot mode)
- **BLE:** Real-time sensor streaming as JSON
- **Serial:** CSV data output and command interface
- **Recording:** Buffer data for HTTP download

## Upload Firmware

### PlatformIO (Recommended)

```bash
pio run -e xiao_esp32s3 -t upload
```

### Arduino IDE

1. Select board: **XIAO_ESP32S3**
2. Select port: `/dev/cu.usbmodem2101`
3. Upload

## Serial Commands

Connect via serial monitor (115200 baud):

```
START / S      - Start recording
STOP / X       - Stop recording
CAL ON/OFF     - Calibration mode
STATUS         - Show status
HELP / ?       - Show help
```

## Python Data Collection

Use `collector.py` for data collection:

```bash
# List available ports
python collector.py --list-ports

# Calibrate sensors
python collector.py --calibrate --port /dev/cu.usbmodem2101

# Record activity
python collector.py --activity walking_forward \
  --port /dev/cu.usbmodem2101 \
  --subject S01 \
  --duration 30
```

## Data Format

### CSV Output
```
time_ms,L_P_Heel,L_P_Ball,L_S_Knee,R_P_Heel,R_P_Ball,R_S_Knee
0,1234,567,890,1200,550,870
20,1250,580,895,1220,560,875
...
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Wrong sensor values | Check wiring - Left: A0-A2, Right: A3-A5 |
| Can't connect | Use `pio device list` to find correct port |
| No WiFi | Check credentials.h and selected WiFi mode |

## Wiring Reference

**Pin Mapping:** A0-A2 = Left leg, A3-A5 = Right leg

```
ESP32S3 XIAO
A0 (GPIO 1) ──┬── L_P_Heel (Heel Pressure)
              └── 10kΩ ── GND

A1 (GPIO 2) ──┬── L_P_Ball (Ball Pressure)
              └── 10kΩ ── GND

A2 (GPIO 3) ──┬── L_S_Knee (Knee Stretch)
              └── 10kΩ ── GND

A3 (GPIO 4) ──┬── R_P_Heel (Heel Pressure)
              └── 10kΩ ── GND

A4 (GPIO 5) ──┬── R_P_Ball (Ball Pressure)
              └── 10kΩ ── GND

A5 (GPIO 6) ──┬── R_S_Knee (Knee Stretch)
              └── 10kΩ ── GND
```

## See Also

- [[sensor_placement_v2]] - Sensor placement guide
- [[circuit_diagram_v2]] - Wiring and BOM
- [[collector.py]] - Python collection tool
