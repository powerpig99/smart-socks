# Smart Socks - Sensor Placement V2

**ELEC-E7840 Smart Wearables — Aalto University**

> **Updated Design (Feb 2026):** 6 sensors total, dual ESP32 configuration
> 
> **Related:** [[circuit_diagram_v2]] | [[calibration_guide]] | [[PROJECT_STATUS]]

---

## Design Philosophy

### Why 6 Sensors?

After team discussion (Jan 29, 2026), we simplified from 10 sensors to **6 sensors** (3 per leg):

| Leg | Pressure | Stretch | Total |
|-----|----------|---------|-------|
| Left | 2 (heel + ball) | 1 (knee) | 3 |
| Right | 2 (heel + ball) | 1 (knee) | 3 |
| **Total** | **4** | **2** | **6** |

### Benefits

1. **Reduced Complexity:** Fewer wires, easier calibration
2. **Faster Prototyping:** Less sensor placement to iterate
3. **Easier Debugging:** 6 data streams vs 10
4. **Adequate Information:** Still captures gait cycle + knee movement
5. **Cost Reduction:** ~40% fewer sensors to purchase

---

## Sensor Layout - Left Leg

### Foot: Pressure Sensors

```
        ┌─────────────────┐
        │                 │
        │    TOES         │
        │                 │
        │                 │
        │    [BALL]  ◉    │  ← Pressure Sensor #2 (Ball)
        │                 │     Location: 1st metatarsal head
        │                 │     ADC: A1
        └─────────────────┘
                  │
                  │
        ┌─────────────────┐
        │                 │
        │    [HEEL]  ◉    │  ← Pressure Sensor #1 (Heel)
        │                 │     Location: Center of heel
        │                 │     ADC: A0
        └─────────────────┘
```

**Why these locations?**
- **Heel:** First/last contact during walking
- **Ball:** Push-off phase, toe clearance during swing

### Knee: Stretch Sensor

```
    ┌───────────────────┐
    │                   │
    │     ◉ STRETCH     │  ← Stretch Sensor (Knee)
    │    ╱   ╲          │     Location: Front of knee (patella)
    │   ╱     ╲         │     ADC: A2
    │  ╱   ●    ╲       │     Orientation: Horizontal across knee
    │ ╱  (knee)  ╲      │
    │╱             ╲    │
    └───────────────────┘
```

**Why knee stretch?**
- Detects knee flexion/extension angle
- Critical for stairs vs flat walking discrimination
- Measures swing phase knee clearance

---

## Sensor Layout - Right Leg (Mirror)

Identical physical placement to left leg, but different pins in production:

**Calibration Mode (1 ESP32):**
- **A3:** Heel pressure
- **A4:** Ball pressure  
- **A5:** Knee stretch

**Production Mode (separate ESP32):**
- **A3:** Heel pressure (maps to A0 if using per-leg firmware)
- **A4:** Ball pressure (maps to A1 if using per-leg firmware)
- **A5:** Knee stretch (maps to A2 if using per-leg firmware)

> **Unified Pin Mapping:** A0-A2 = Left, A3-A5 = Right across all modes

---

## Naming Convention

```python
# config.py sensor names
SENSORS = {
    'names': [
        "L_P_Heel", "L_P_Ball", "L_S_Knee",   # Left leg
        "R_P_Heel", "R_P_Ball", "R_S_Knee",   # Right leg
    ]
}

# Format: {L/R}_{P/S}_{Location}
# L = Left, R = Right
# P = Pressure, S = Stretch
```

---

## Activity Detection Strategy

### Gait Cycle Detection

**Ground Contact Phases:**
- **Heel Strike:** L_P_Heel/R_P_Heel peaks
- **Mid-Stance:** Both pressure sensors active
- **Toe-Off:** L_P_Ball/R_P_Ball peaks, then release

**Swing Phase:**
- **Knee Flexion:** L_S_Knee/R_S_Knee stretches during swing
- **Knee Extension:** Returns to resting before heel strike

### Activity Signatures

| Activity | Pressure Pattern | Stretch Pattern |
|----------|------------------|-----------------|
| **Walking** | Alternating L/R heel→ball | Moderate knee flexion |
| **Stairs Up** | Higher ball pressure | Increased knee flexion |
| **Stairs Down** | Controlled heel landing | Extended knee stretch |
| **Sitting** | Low/constant pressure | Knee at ~90° |
| **Standing** | Steady weight distribution | Minimal stretch |

---

## Fabrication Steps

### Materials Needed
- Athletic socks (4 pairs - with spares)
- Knee pads or fabric knee sleeves (4)
- Conductive fabric for pressure sensors
- Conductive thread for stretch sensors
- Velcro straps for securing sensors

### Step 1: Pressure Sensors in Socks

1. **Mark locations** on sock:
   - Heel: Center of heel cup
   - Ball: Under big toe joint

2. **Sew sensor patches:**
   ```
   Cut conductive fabric: 2cm × 2cm squares
   
   Attach to sock with conductive thread:
   ┌─────────┐
   │  ◉      │  ← Center point (measurement)
   │ /│\     │
   │/ │ \    │  ← Sew radial spokes
   │  │  \   │
   └─────────┘
   ```

3. **Route wires** up to ankle/lower calf

### Step 2: Stretch Sensor at Knee

1. **Prepare knee sleeve:**
   - Sew conductive fabric strips (10cm × 2cm)
   - One at top, one at bottom of knee cap

2. **Create variable resistor:**
   ```
   Top strip ─────┬──── Wire to A2
                  │
                  └──── Conductive thread crossing knee
                        (acts as variable resistor based on stretch)
   Bottom strip ──┬──── Wire to GND
                  │
                  └──── Same thread
   ```

3. **Add reference resistor:**
   - 10kΩ pull-down resistor creates voltage divider
   - Output to ESP32 A2 pin

### Step 3: Wire Management

- Use **elastic straps** to route wires along leg
- Keep **ESP32 on thigh or waist belt** for stability
- Use **connector clips** for easy removal/washing

---

## Calibration Procedure

### 1. Baseline Reading
```
Sensor sitting flat, no weight:
  Record ADC value (typically 0-100)
```

### 2. Max Load
```
Standing with full weight:
  Record ADC value (typically 3000-4000)
```

### 3. Map to 0-1 Range
```python
def calibrate(value, min_val, max_val):
    return (value - min_val) / (max_val - min_val)
```

### 4. Store Calibration
- Save per-sensor calibration to `03_Data/calibration/`
- Run calibration tool: `python calibration_viz.py`

---

## Testing Checklist

- [ ] All 6 sensors respond to movement
- [ ] Heel sensors detect ground contact
- [ ] Ball sensors detect push-off
- [ ] Knee sensors detect flexion
- [ ] Left/right synchronization verified
- [ ] No crosstalk between sensors
- [ ] Wiring secure during walking

---

## Troubleshooting

| Problem | Possible Cause | Solution |
|---------|---------------|----------|
| No pressure reading | Sensor not in contact | Adjust sock tightness |
| No stretch reading | Thread disconnected | Re-sew connection |
| Erratic values | Loose wire | Check all solder joints |
| One leg not working | Wrong port | Check `/dev/cu.usbmodem*` |
| Drift over time | Temperature/humidity | Re-calibrate |

---

## Navigation

| ← Previous | ↑ Up | Next → |
|------------|------|--------|
| [[circuit_diagram_v2]] | [[INDEX]] | [[calibration_guide]] |

---

*Last updated: February 2026 · 6-Sensor Configuration*
