# Smart Socks - Unified Pin Mapping

**Same pin definitions for calibration and production modes**

---

## Concept

Use **consistent pin assignments** across all modes:
- **A0-A2** = Left leg sensors (always)
- **A3-A5** = Right leg sensors (always)

This means:
- Calibration: One ESP32 with all 6 sensors (A0-A5)
- Production: Two ESP32s, each using half the pins

---

## Pin Assignment Table

| Sensor | Calibration | Left Leg (Prod) | Right Leg (Prod) |
|--------|-------------|-----------------|------------------|
| **L_P_Heel** | A0 | **A0** | — |
| **L_P_Ball** | A1 | **A1** | — |
| **L_S_Knee** | A2 | **A2** | — |
| **R_P_Heel** | A3 | — | **A3** |
| **R_P_Ball** | A4 | — | **A4** |
| **R_S_Knee** | A5 | — | **A5** |

---

## Wiring Diagrams

### Calibration Mode (1 ESP32)
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

### Production Mode (2 ESP32s)

**Left Leg ESP32:**
```
3.3V ──┬──┬──┬──
       │  │  │
A0  ───┴──┘  │     L_P_Heel
A1  ────────┴──┘   L_P_Ball
A2  ─────────────┘ L_S_Knee
A3-A5: UNUSED
GND ──┴──┴──┴──
```

**Right Leg ESP32:**
```
3.3V ──┬──┬──┬──
       │  │  │
A0  ───┘  │  │     UNUSED (or future expansion)
A1  ──────┘  │     UNUSED
A2  ─────────┘     UNUSED
A3  ───┴──┘        R_P_Heel
A4  ────────┴──┘   R_P_Ball
A5  ─────────────┘ R_S_Knee
GND ──┴──┴──┴──
```

---

## Firmware Selection

| Mode | Sketch | Upload Command |
|------|--------|----------------|
| **Calibration** | `calibration_all_sensors.ino` | `pio run -e calibration -t upload` |
| **Left Leg** | `data_collection_leg.ino` | `pio run -e left_leg -t upload` |
| **Right Leg** | `data_collection_leg.ino` | `pio run -e right_leg -t upload` |

The `LEG_ID` compile flag automatically selects the correct pin subset.

---

## Benefits

1. **No rewiring** between calibration and production
2. **Consistent mental model** - A0-A2 = Left, A3-A5 = Right
3. **Simpler documentation** - one pin table for everything
4. **Calibration values transfer** directly to production
5. **Future expansion** - A0-A2 available on right leg, A3-A5 on left

---

## Physical Wiring Reference

### For Calibration (One ESP32)
Connect all 6 sensors to a single ESP32:
- Left sock sensors → A0, A1, A2
- Right sock sensors → A3, A4, A5

### For Production (Two ESP32s)

**Left Leg ESP32:**
- Only wire sensors to A0, A1, A2
- Leave A3, A4, A5 unconnected (or tape them off)

**Right Leg ESP32:**
- Wire sensors to A3, A4, A5
- A0, A1, A2 remain unconnected
- This matches the calibration wiring for the right side

---

## Quick Reference Card

```
┌─────────────────────────────────────┐
│      SMART SOCKS PIN MAP            │
├─────────────────────────────────────┤
│  A0 = L_P_Heel    A3 = R_P_Heel     │
│  A1 = L_P_Ball    A4 = R_P_Ball     │
│  A2 = L_S_Knee    A5 = R_S_Knee     │
├─────────────────────────────────────┤
│  Calibration: A0-A5 (one ESP32)     │
│  Left Leg:    A0-A2                 │
│  Right Leg:   A3-A5                 │
└─────────────────────────────────────┘
```

---

*Last updated: February 2026*
