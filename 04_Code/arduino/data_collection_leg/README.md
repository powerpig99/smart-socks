# Smart Socks - Dual ESP32 Data Collection

## Overview

This sketch supports the **6-sensor dual ESP32 configuration** (Jan 29, 2026 team decision):

| Component | Left Leg | Right Leg |
|-----------|----------|-----------|
| **ESP32** | ESP32S3 XIAO #1 | ESP32S3 XIAO #2 |
| **Pressure** | Heel (A0), Ball (A1) | Heel (A3), Ball (A4) |
| **Stretch** | Knee (A2) | Knee (A5) |
| **WiFi IP** | 192.168.4.1 | 192.168.4.2 |
| **Port** | `/dev/cu.usbmodem2101` | `/dev/cu.usbmodem2102` |

## Setup Instructions

### 1. Configure Each ESP32

For **Left Leg ESP32**, ensure this line is set:
```cpp
const LegID LEG_ID = LEFT_LEG;  // In data_collection_leg.ino, line 29
```

For **Right Leg ESP32**, change to:
```cpp
const LegID LEG_ID = RIGHT_LEG;  // In data_collection_leg.ino, line 29
```

### 2. Upload Firmware (PlatformIO)

```bash
# Upload to Left Leg ESP32
# 1. Connect left ESP32 via USB
pio run --environment left_leg --target upload

# Upload to Right Leg ESP32  
# 1. Connect right ESP32 via USB
pio run --environment right_leg --target upload
```

Or via VS Code PlatformIO extension:
1. Click on **Project Tasks** → **left_leg** → **Upload** (for left leg)
2. Click on **Project Tasks** → **right_leg** → **Upload** (for right leg)

### 2b. Upload Firmware (Arduino IDE)

```cpp
// For Left Leg - uncomment this line:
const LegID LEG_ID = LEFT_LEG;

// For Right Leg - uncomment this line instead:
// const LegID LEG_ID = RIGHT_LEG;
```

Then upload to each ESP32 separately.

### 3. Connect Both Legs

```bash
# Connect both ESP32s to USB ports
# They will create separate WiFi APs or connect to laptop via serial
```

## Usage

### Web Dashboard

Each leg runs its own web dashboard:
- **Left Leg:** http://192.168.4.1
- **Right Leg:** http://192.168.4.2

### Serial Commands

Connect via serial monitor (115200 baud):

```
START / S       - Start recording
STOP / X        - Stop recording
TRIGGER         - Synchronized start (both legs)
MASTER          - Set as sync master
SLAVE           - Set as sync slave
SYNC OFF        - Disable synchronization
CAL ON/OFF      - Calibration mode
STATUS          - Show status
HELP / ?        - Show help
```

### Synchronization Modes

#### Independent Mode (Default)
Each leg records independently. No synchronization between legs.

#### Master-Slave Mode
1. On one leg: Send `MASTER` command
2. On other leg: Send `SLAVE` command
3. On master: Send `START` - both legs start simultaneously

#### Trigger Mode
Send `TRIGGER` command to both legs for synchronized start with 100ms delay.

## Python Data Collection

Use `dual_collector.py` for synchronized data collection:

```bash
# List available ports
python dual_collector.py --list-ports

# Calibrate both legs
python dual_collector.py --calibrate \
  --left-port /dev/cu.usbmodem2101 \
  --right-port /dev/cu.usbmodem2102

# Record activity
python dual_collector.py --activity walking \
  --left-port /dev/cu.usbmodem2101 \
  --right-port /dev/cu.usbmodem2102 \
  --subject test_user \
  --duration 30

# Merge existing CSV files
python dual_collector.py --merge \
  --left left_leg_data.csv \
  --right right_leg_data.csv \
  --output merged_data.csv
```

## Data Format

### CSV Output (Per Leg)
```
time_ms,leg,L_P_Heel,L_P_Ball,L_S_Knee
0,L,1234,567,890
20,L,1250,580,895
...
```

### Merged CSV (Dual Collector)
```
time_ms,L_P_Heel,L_P_Ball,L_S_Knee,R_P_Heel,R_P_Ball,R_S_Knee
0,1234,567,890,1200,550,870
20,1250,580,895,1220,560,875
...
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Both legs same IP | Check `LEG_ID` setting - must be different |
| Sync not working | Verify both on same WiFi channel, check firewall |
| Wrong sensor values | Check wiring - Left: A0-A2, Right: A3-A5 |
| Can't connect | Use `pio device list` to find correct ports |

## Wiring Reference

**Unified Pin Mapping:** A0-A2 = Left leg, A3-A5 = Right leg

### Left Leg ESP32
```
A0 (GPIO 1) ──┬── L_P_Heel (Heel Pressure)
              └── 10kΩ ── GND

A1 (GPIO 2) ──┬── L_P_Ball (Ball Pressure)
              └── 10kΩ ── GND

A2 (GPIO 3) ──┬── L_S_Knee (Knee Stretch)
              └── 10kΩ ── GND

A3-A5: Unused (available for future expansion)
```

### Right Leg ESP32
```
A3 (GPIO 4) ──┬── R_P_Heel (Heel Pressure)
              └── 10kΩ ── GND

A4 (GPIO 5) ──┬── R_P_Ball (Ball Pressure)
              └── 10kΩ ── GND

A5 (GPIO 6) ──┬── R_S_Knee (Knee Stretch)
              └── 10kΩ ── GND

A0-A2: Unused (available for future expansion)
```

### Calibration Mode (1 ESP32)
Connect all 6 sensors to a single ESP32 using A0-A5 as shown above.

## See Also

- [[sensor_placement_v2]] - Sensor placement guide
- [[circuit_diagram_v2]] - Wiring and BOM
- [[dual_collector.py]] - Python collection tool
