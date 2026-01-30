# Deprecated 10-Sensor Arduino Sketches

**⚠️ WARNING: These sketches are DEPRECATED and use the OLD 10-sensor design.**

## Current Design: 6 Sensors (3 per leg)

The project has been updated to use **6 sensors total** (2 pressure per sock + 1 stretch per knee) across **2 ESP32S3 XIAO** boards (one per leg).

## Use These Instead

| Purpose | Use This Sketch |
|---------|-----------------|
| Data Collection | `data_collection_leg/data_collection_leg.ino` |
| Calibration | `calibration_all_sensors/calibration_all_sensors.ino` |

## Key Differences

| Feature | Old (Deprecated) | Current |
|---------|------------------|---------|
| Sensors | 10 (5 per foot) | 6 (3 per leg) |
| ESP32 Boards | 1 | 2 (one per leg) |
| Sensor Types | Pressure only | Pressure + Stretch |
| Pin Mapping | A0-A4 + A5 + GPIO | A0-A2 per ESP32 |

## Migration Notes

If you need the 10-sensor version for reference:
- These sketches read 10 pressure sensors on ONE ESP32
- Left sock: A0-A4
- Right sock: A5 + GPIO 7-10

The current 6-sensor design uses:
- Left ESP32: A0-A2 (L_P_Heel, L_P_Ball, L_S_Knee)
- Right ESP32: A0-A2 (R_P_Heel, R_P_Ball, R_S_Knee)

---
*Last Updated: 2026-01-30*
