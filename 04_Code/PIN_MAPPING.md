# Smart Socks - Pin Mapping

**Single ESP32S3 XIAO reads all 6 sensors on pins A0-A5**

---

## Pin Assignment Table

| Pin | Sensor | Type | Location |
|-----|--------|------|----------|
| **A0** | L_P_Heel | Pressure | Left heel |
| **A1** | L_P_Ball | Pressure | Left ball of foot |
| **A2** | L_S_Knee | Stretch | Left knee |
| **A3** | R_P_Heel | Pressure | Right heel |
| **A4** | R_P_Ball | Pressure | Right ball of foot |
| **A5** | R_S_Knee | Stretch | Right knee |

---

## Wiring Diagram

```
ESP32S3 XIAO
═════════════
3.3V ──┬──┬──┬──┬──┬──┬── All sensor VCC
       │  │  │  │  │  │
A0  ───┴──┘  │  │  │  │  L_P_Heel (Heel Pressure)
A1  ────────┴──┘  │  │  │  L_P_Ball (Ball Pressure)
A2  ─────────────┴──┘  │  │  L_S_Knee (Knee Stretch)
A3  ──────────────────┴──┘  │  R_P_Heel (Heel Pressure)
A4  ───────────────────────┴──┘  R_P_Ball (Ball Pressure)
A5  ────────────────────────────┘  R_S_Knee (Knee Stretch)

GND ──┬──┬──┬──┬──┬──┬── All sensor GND
     10kΩ pull-down on each pin
```

---

## Firmware Selection

| Mode | Sketch | Upload Command |
|------|--------|----------------|
| **Data Collection** | `data_collection_leg.ino` | `pio run -e xiao_esp32s3 -t upload` |
| **Calibration** | `calibration_all_sensors.ino` | `pio run -e calibration -t upload` |

Both firmwares use the same pin mapping (A0-A5).

---

## Benefits

1. **Simple wiring** — one ESP32, six pins, always the same
2. **Consistent mental model** — A0-A2 = Left, A3-A5 = Right
3. **Calibration values transfer** directly to data collection
4. **Shared pin layout** between calibration and data collection firmwares

---

## Quick Reference Card

```
┌─────────────────────────────────────┐
│      SMART SOCKS PIN MAP            │
├─────────────────────────────────────┤
│  A0 = L_P_Heel    A3 = R_P_Heel    │
│  A1 = L_P_Ball    A4 = R_P_Ball    │
│  A2 = L_S_Knee    A5 = R_S_Knee    │
├─────────────────────────────────────┤
│  1 ESP32, pins A0-A5, always       │
└─────────────────────────────────────┘
```

---

*Last updated: January 2026*
