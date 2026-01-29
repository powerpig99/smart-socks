# Smart Socks - Sensor Placement Guide V2

**ELEC-E7840 Smart Wearables — Aalto University**

> **Updated Design (Jan 29, 2026):** 2 pressure sensors + 1 stretch sensor per leg
> 
> **Related:** [[circuit_diagram]] | [[PLATFORMIO_SETUP]] | [[README]]

---

## New Sensor Configuration

Based on team meeting (Jan 29, 2026) with Saara, Alex, and Jing:

### Per Leg Setup:
| Location | Sensor Type | Placement | Purpose |
|----------|-------------|-----------|---------|
| **Sock - Heel** | Pressure | Under heel | Initial contact, weight bearing |
| **Sock - Ball** | Pressure | Under ball of foot | Push-off, propulsion |
| **Knee Pad** | Stretch | Front of knee | Knee flexion/extension |

### Total System:
- **4 Pressure Sensors:** 2 per sock (heel + ball)
- **2 Stretch Sensors:** 1 per knee pad
- **Total:** 6 sensors per person

---

## Movement Detection Strategy

### Walking Forward
- **Heel:** Peak pressure at initial contact
- **Ball:** Peak pressure at push-off
- **Knee:** Front stretches during swing phase

### Walking Backward
- **Ball:** Peak pressure at initial contact
- **Heel:** Peak pressure at push-off
- **Knee:** Front stretches during swing phase

### Stairs Up
- **Heel → Ball:** Sequential pressure (can be simultaneous)
- **Knee:** Stronger front stretch on stepping foot (distinguishes from flat walking)

### Stairs Down
- **Ball → Heel:** Sequential pressure
- **Knee:** Front stretch on leg that stays behind

### Sitting (Feet on floor)
- **Both Heels:** Equal pressure
- **Both Knees:** Equal stretch (minimal)

### Sitting (Legs crossed)
- **One Heel:** Pressure only under supporting foot
- **Both Knees:** Different stretch magnitudes

### Sit-to-Stand
- **Both Heels:** Pressure increases
- **Both Knees:** Stretch decreases as legs straighten

### Standing (Upright)
- **Heels + Balls:** Equal pressure both feet
- **Knees:** Minimal or no stretch

### Standing (Leaning)
- **One side:** More pressure
- **Knees:** Minimal stretch

---

## Sensor Fabrication Notes

### Pressure Sensors (Per sock: 2 needed)
- **Material:** Piezoresistive fabric (Eeonyx TL-210)
- **Size:** 2cm × 2cm squares
- **Method:** Heat-pressed for consistency
- **Placement:** Sewn/adhered to sock at marked positions

### Stretch Sensors (Per knee pad: 1 needed)
- **Material:** Conductive thread/knit fabric
- **Method:** Knitted stretch sensor
- **Placement:** Front of knee pad, across knee joint
- **Structure:** Knitted stretch part in middle, adjustable straps on sides

### Knee Pad Design Challenge
**Problem:** Different leg diameters affect results

**Solution:** 
- Knitted stretch part in center (sensor area)
- Elastic fabric with adjustable straps on sides
- "Starting position" can be standardized with straps
- Minimizes impact of different leg sizes

---

## Placement Procedure

### Step 1: Mark Foot
1. Stand on paper, trace foot outline
2. Mark:
   - **Heel:** Center of heel
   - **Ball:** Center of ball of foot (metatarsal heads)

### Step 2: Prepare Sock
1. Turn sock inside out
2. Transfer marks to sock
3. Reinforce area with fabric backing if needed

### Step 3: Attach Pressure Sensors
1. Position sensor at marked location
2. Sew or adhere in place
3. Route conductive thread along sock (avoid pressure points)
4. Test conductivity

### Step 4: Prepare Knee Pad
1. Measure knee circumference
2. Cut fabric: knitted center (sensor) + elastic sides
3. Sew stretch sensor into front center
4. Add adjustable straps

### Step 5: Connect Wiring
- Route all wires to central hub (ESP32 location)
- Secure with fabric tape
- Leave slack for movement

---

## References

1. **Skating Technique Detection (3 pressure sensors):**
   https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2025.1554264/full
   - 2 at ball, 1 at heel

2. **Healthcare & Sport Monitoring (5 pressure sensors):**
   https://pubs-acs-org.ezproxy.utu.fi:2443/doi/full/10.1021/acsnano.8b08329
   - Ball, heel, big toe, sides

---

## Meeting Notes (Jan 29, 2026)

**Attendees:** Saara, Alex, Jing

**Key Decisions:**
- ✅ Adopt 2 pressure + 1 stretch sensor per leg design
- ✅ Focus on heel and ball pressure (skip arch, metatarsals lateral, toe for now)
- ✅ Add knee pads with stretch sensors for better activity discrimination
- ✅ Next meeting: Sun 2.2.2026 14:45-16:45 (Y163)

**Action Items:**
- Saara: Biosignal processing, sensor characterization methodology
- Alex: Sock/knee pad design, user requirements, physiotherapist consultation
- Jing: Electronics, preliminary analysis, ESP32 firmware

---

## Navigation

| ← Previous | ↑ Up | Next → |
|------------|------|--------|
| [[circuit_diagram]] | [[INDEX]] | — |

---

*Last updated: 2026-01-29 · Design Version 2.0*
