# Sensor Manufacturing Research for Smart Socks

**ELEC-E7840 Smart Wearables — Aalto University**
**Research Date:** January 31, 2026
**Compiled by:** Huyo (Digital Twin)

> **Related:** [[video_tutorials]] | [[REFERENCES]] | [[sensor_placement_v2]] | [[circuit_diagram_v2]] | [[PROPOSALS]]
>
> *GitHub:* [Video Tutorials](video_tutorials.md) · [References](REFERENCES.md) · [Sensor Placement](../01_Design/sensor_placement_v2.md) · [Circuit Diagram](../01_Design/circuit_diagram_v2.md) · [Proposals](../08_Proposals/PROPOSALS.md)

---

## Executive Summary

This document provides a comprehensive review of textile-based sensor manufacturing techniques suitable for the Smart Socks project, covering:
- **Foot pressure sensors** (piezoresistive, capacitive, triboelectric)
- **Knee stretch sensors** (conductive fabric, stitched strain gauges)

Key finding: Piezoresistive sensors using conductive fabrics (Eeonyx, Velostat/Linqstat) offer the best balance of simplicity, cost, and performance for academic projects.

---

## Part 1: Foot Pressure Sensors

### 1.1 Sensor Types Comparison

| Type | Mechanism | Pros | Cons | Suitability |
|------|-----------|------|------|-------------|
| **Piezoresistive** | Resistance change under pressure | Simple, low cost, good dynamic range | Hysteresis, drift over time | **Best for socks** |
| **Capacitive** | Capacitance change between electrodes | High sensitivity, low power | Complex electronics, humidity sensitive | Good but complex |
| **Triboelectric** | Voltage from friction/contact | Self-powered, high sensitivity | Unstable output, signal processing needed | Research stage |
| **Piezoelectric** | Voltage from mechanical stress | Fast response, good for dynamic | Poor static performance, expensive | Not recommended |

### 1.2 Piezoresistive Sensor Construction

#### Option A: Easy-to-Build Anti-Static Sheet Method

**Reference:** *Easy-to-Build Textile Pressure Sensor* (PMC5948620)

**Materials:**
- Anti-static sheet (conductive layer)
- Conductive woven fabric (electrode)
- Standard household tools (iron, scissors)

**Construction:**
1. Layer structure: Fabric electrode → Anti-static sheet → Fabric electrode
2. Apply pressure → anti-static sheet compresses → resistance drops
3. Create 1-70 kPa linear response range
4. Recovery time: ~1 second for 8 kPa release

**Advantages:**
- ✅ No sewing machine required
- ✅ Uses household tools only
- ✅ Suitable for educational/didactic applications
- ✅ Low variability between sensors

**Circuit** (see [[circuit_diagram_v2]] for our project's implementation):
```
+3.3V ──┬── Conductive Fabric (Top)
        │
       [Anti-Static Sheet]
        │
        ├── ADC Input (A0-A5 on ESP32)
        │
       [10kΩ Resistor]
        │
       GND
```

#### Option B: Velostat/Linqstat Method

**Materials:**
- Velostat/Linqstat (pressure-sensitive conductive film)
- Conductive fabric (copper/nickel plated)
- Neoprene or foam (optional, for cushioning)

**Construction:**
1. Cut Velostat to desired sensor size (2-3 cm diameter for heel/ball)
2. Place between two conductive fabric layers
3. Stitch or bond edges (leave room for compression)
4. Connect wires to conductive fabric electrodes

**Characteristics:**
- Resistance range: ~10kΩ (unpressed) to ~1kΩ (pressed)
- Response: Monotonic but non-linear
- Hysteresis: Moderate (acceptable for activity recognition)

#### Option C: Jacquard Woven Sensors (Advanced)

**Reference:** *Programmable Design of Large-Area Piezoresistive Textile Sensors* (PMC9824245)

**Method:**
- Single-wall carbon nanotubes (SWCNT) coating on polyester fabric
- Jacquard weaving creates programmable electrode patterns
- Three sensor types: single-layer, double-layer, quadruple-layer

**Performance:**
- Thickness: <0.52 mm
- Response time: <50 ms
- Hysteresis increases with layer count
- Full 20×20 cm sensitive area possible

**Manufacturing:**
- Requires access to Jacquard loom
- CNT coating process needs lab equipment
- Suitable for thesis-level projects

### 1.3 Key Manufacturing Parameters

| Parameter | Recommended Value | Notes |
|-----------|------------------|-------|
| Sensor diameter | 2-3 cm | Matches foot pressure points |
| Electrode spacing | 1-2 mm | Affects sensitivity |
| Material thickness | 0.5-1 mm | Balance comfort and sensitivity |
| Voltage divider resistor | 10 kΩ | Matches Velostat range (~1-10kΩ); Amitrano et al. (2020) used 18kΩ for EeonTex's higher range |
| ADC resolution | 12-bit (ESP32 default) | 0-4095 range |

### 1.4 Commercial Sources

| Material | Supplier | Product | Cost |
|----------|----------|---------|------|
| Velostat/Linqstat | Adafruit | 12"x12" sheet | ~$10 |
| Conductive Fabric | LessEMF | Stretch Conductive Fabric | ~$15/ft |
| EeonTex | Eeonyx Corp. | Stretchable conductive fabric | Contact for pricing |
| Conductive Thread | SparkFun | 2-ply 117/17 silver | ~$20/50ft |

---

## Part 2: Knee Stretch Sensors

### 2.1 Sensor Types for Knee Flexion

| Type | Mechanism | Range | Best For |
|------|-----------|-------|----------|
| **Conductive Fabric** | Resistance change with stretch | 0-30% strain | Knee angle (0-90°) |
| **Stitched Sensor** | Thread geometry changes resistance | 0-50% strain | Large movements |
| **Inductive Coil** | Inductance changes with stretch | 0-20% strain | High precision |
| **Optical Fiber** | Light intensity modulation | 0-10% strain | Medical grade |

### 2.2 Conductive Fabric Stretch Sensors

#### Option A: EeonTex Fabric (Eeonyx)

**Reference:** *Fabric-Based Textile Stretch Sensor* (MDPI Sensors 2020)

**Material:**
- Nylon/Spandex fabric coated with doped polypyrrole
- Bidirectionally stretchy
- Conductive coating changes resistance when stretched

**Characteristics:**
- **Working range:** 0-15% stretch (best accuracy)
- **Resistance range:** Varies by formulation (10kΩ to 100kΩ unstretched)
- **Non-linear:** Resistance **decreases** with stretch (e.g., EeonTex LTT-SLPA: 20kΩ/sq resting → ~10kΩ stretched)
- **Hysteresis:** Moderate (~5-10%)

**Usage Notes:**
- ⚠️ Ambiguous zone: 0-5% stretch (resistance not unique)
- ✅ Use in pre-strained state for better accuracy
- ✅ Suitable for knee flexion (15-30° typically produces 5-10% fabric stretch)

**Stretch Direction Note:**
- **Course direction** (horizontal): Better repeatability, recommended for longevity
- **Wale direction** (vertical): Larger resistance change range but fabric stretches out over time
- Source: Eeonyx LTT-SLPA Technical Data Sheet

**Manufacturing:**
1. Cut EeonTex strip (3-5 cm wide, 10-15 cm long)
2. Sew conductive thread to ends for electrical connection
3. Mount on knee pad with elastic to maintain tension
4. Calibrate: 0° (straight) → 90° (bent) mapping

#### Option B: Silver-Plated Yarn Knit Sensors

**Reference:** *Analysis of Textile Knit Stretch Sensors* (PMC6720445)

**Materials:**
- Silver-plated nylon yarn (2-ply, 110-150 Ω/m)
- Knit structure: Single jersey performs best
- Base fabric: Spandex or elastic knit

**Manufacturing Methods:**

**Hand-Knitting (Simple):**
1. Knit conductive yarn into strip (10-15 rows)
2. Integrate into knee pad elastic band
3. Connect silver thread to copper wire at ends

**Machine Knitting (Better consistency):**
1. Use flat-bed knitting machine
2. Program jersey stitch pattern
3. Include conductive yarn every 3-4 rows
4. Bind off and integrate into garment

**Performance:**
- Better linearity than EeonTex
- More hysteresis than EeonTex
- Good for 0-40% strain range
- Signal noise: Low to moderate

#### Option C: Stitched Stretch Sensors

**Reference:** *Stitched Stretch Sensor Patent* (US9322121B2)

**Concept:**
- Conductive thread stitched in specific geometry
- Stretch changes stitch geometry → resistance changes
- Programmable by stitch pattern

**Stitch Patterns:**

| Pattern | Sensitivity | Range | Use Case |
|---------|-------------|-------|----------|
| Zigzag | High | 0-20% | Small movements |
| Loop | Medium | 0-40% | Medium movements |
| Coil | Low | 0-60% | Large movements |

**Manufacturing:**
1. Mark sensor area on knee pad
2. Set sewing machine: zigzag stitch, conductive thread
3. Sew 5-10 parallel lines (2-3 cm apart)
4. Connect lines in series for higher resistance change
5. Test resistance range with multimeter

### 2.3 Knee Sensor Placement

> See [[sensor_placement_v2]] for our chosen placement.

**Recommended Position:**
- **Location:** Front of knee (patella area)
- **Orientation:** Vertical, along knee flexion axis
- **Pre-strain:** 10-15% stretch at 0° (straight leg)
- **Active range:** 10-25% stretch during 0-90° flexion

**Alternative Positions:**
- Above knee: Less strain, more comfort
- Side of knee: Different strain pattern
- Behind knee: Compression instead of stretch (different sensor type)

### 2.4 Circuit Design

**Voltage Divider (Same as Pressure Sensors):**
```
+3.3V ──┬── Stretch Sensor (L_S_Knee/R_S_Knee)
        │
        ├── ADC Input (A2/A5 on ESP32)
        │
       [10kΩ Resistor]
        │
       GND
```

**Expected Readings:**
- Straight leg: ~1500 ADC (higher resistance, sensor at pre-strain only)
- Bent knee: ~2500 ADC (lower resistance, sensor further stretched by knee flexion)
- Note: Knee bending stretches front-of-knee fabric more. V_ADC = 3.3V × 10kΩ / (R_sensor + 10kΩ), so lower R → higher ADC. Values depend on pre-strain amount and specific sensor.

---

## Part 3: Integration Considerations

### 3.1 Wiring Strategy

**Recommendation:** Use conductive thread for comfort

**Technique:**
1. Sew conductive thread traces into sock/knee pad
2. Use insulating fabric layer to prevent short circuits
3. Connect to ESP32 at sock cuff (easiest access)
4. Consider snap connectors for removable electronics

### 3.2 Durability

| Issue | Solution |
|-------|----------|
| Sensor drift | Calibrate before each use |
| Hysteresis | Accept as limitation; use threshold-based detection |
| Fatigue (EeonTex) | Replace sensors after ~1000 cycles |
| Moisture | Use water-resistant coating or encapsulation |
| Washing | Remove electronics; hand wash sensors only |

### 3.3 Cost Estimate (Per Sock + Knee Pad Set)

| Component | Cost (EUR) | Source |
|-----------|-----------|--------|
| Velostat sheet (shared) | 5 | Adafruit/LessEMF |
| Conductive fabric (30×30 cm) | 10 | LessEMF |
| EeonTex fabric (20×10 cm) | 8 | Eeonyx |
| Conductive thread (10m) | 15 | SparkFun |
| Neoprene/foam | 3 | Local fabric store |
| Regular fabric (sock) | 5 | Local store |
| **Total per set** | **~46 EUR** | |
| **Total for 2 legs** | **~92 EUR** | |

---

## Part 4: Step-by-Step Manufacturing Guide

> See [[video_tutorials]] for visual walkthroughs of these techniques.

### 4.1 Pressure Sensor (Heel/Ball of Foot)

**Materials:**
- Velostat sheet (10×10 cm)
- Conductive fabric (10×10 cm, 2 pieces)
- Conductive thread
- Neoprene or felt (optional, for cushioning)

**Steps:**
1. Cut Velostat: 2.5 cm diameter circles (4 pieces for 2 heels + 2 balls)
2. Cut conductive fabric: 3 cm diameter circles (8 pieces)
3. Layer: Fabric → Velostat → Fabric (sandwich)
4. Sew edges with regular thread (leave 2mm gap for compression)
5. Sew conductive thread from each fabric layer to cuff
6. Test with multimeter: Unpressed >10kΩ, pressed <2kΩ
7. Integrate into sock at heel and ball positions

### 4.2 Stretch Sensor (Knee)

**Materials:**
- EeonTex fabric (15×5 cm strip)
- Conductive thread
- Elastic band (for mounting)
- Knee pad base

**Steps:**
1. Cut EeonTex: 10 cm × 3 cm strip
2. Sew conductive thread to each end (10 cm tails)
3. Attach to knee pad with elastic:
   - Top: Fixed to knee pad
   - Bottom: Elastic allows stretch
4. Pre-strain: Attach so 0° knee has ~15% fabric stretch
5. Test: Straight leg → bent knee should change resistance 2-3×
6. Calibrate with known angles (0°, 30°, 60°, 90°)

---

## Part 5: References

> Full citation list in [[REFERENCES]].

### Key Papers

1. **Easy-to-Build Textile Pressure Sensor** (2018)
   - PMC ID: PMC5948620
   - URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC5948620/
   - Key finding: Anti-static sheets + conductive fabric, household tools only

2. **Programmable Design of Large-Area Piezoresistive Textile Sensors** (2023)
   - PMC ID: PMC9824245
   - URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC9824245/
   - Key finding: Jacquard processing with CNT coating, <50ms response

3. **Fabric-Based Textile Stretch Sensor for Optimized Measurement** (2020)
   - DOI: 10.3390/s20247323
   - URL: https://www.mdpi.com/1424-8220/20/24/7323
   - Key finding: EeonTex 0-15% optimal range, pre-strain required

4. **Analysis of Textile Knit Stretch Sensors** (2019)
   - PMC ID: PMC6720445
   - URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC6720445/
   - Key finding: Silver-plated yarn single jersey best for knee tracking

5. **Stitched Stretch Sensor Patent** (2016)
   - US Patent: US9322121B2
   - URL: https://patents.google.com/patent/US9322121B2/
   - Key finding: Programmable resistance via stitch geometry

### Commercial Resources

- **Adafruit:** Velostat, conductive thread (learn.adafruit.com)
- **LessEMF:** Wide range of conductive fabrics (lessemf.com)
- **Eeonyx Corp:** EeonTex stretchable fabrics (eeonyx.com)
- **Kobakant:** DIY e-textile tutorials (kobakant.at/DIY)
- **SparkFun:** Conductive thread, sensors (sparkfun.com)

### Course Context

This research supports:
- **Part 1:** Sensor fabrication and characterization (Weeks 1-7)
- **Mid-term demo:** Real-time sensor visualization
- **Part 2:** ML pipeline with reliable sensor data (Weeks 8-15)
- **Part 3:** Edge ML with optimized sensors (optional extension)

---

## Summary Recommendations

### For Your Smart Socks Project:

**Pressure Sensors (Heel/Ball):**
- ✅ Use **Velostat/Linqstat** with conductive fabric
- ✅ 10kΩ voltage divider, 12-bit ADC
- ✅ Sew into sock at pressure points
- ✅ Expected range: 10kΩ (unpressed) → 1kΩ (pressed)

**Stretch Sensors (Knee):**
- ✅ Use **EeonTex** fabric or **silver-plated yarn knit**
- ✅ Mount with 15% pre-strain at 0° knee angle
- ✅ Same voltage divider circuit
- ✅ Calibrate: ADC values → knee angles

**Critical Success Factors:**
1. Pre-strain the stretch sensors
2. Test all sensors before final integration
3. Document calibration curves for each sensor
4. Plan for sensor replacement (fatigue over time)

---

> **Navigation:** [[video_tutorials]] | [[REFERENCES]] | [[sensor_placement_v2]] | [[circuit_diagram_v2]] | [[PROPOSALS]]
>
> *GitHub:* [Video Tutorials](video_tutorials.md) · [References](REFERENCES.md) · [Sensor Placement](../01_Design/sensor_placement_v2.md) · [Circuit Diagram](../01_Design/circuit_diagram_v2.md) · [Proposals](../08_Proposals/PROPOSALS.md)

*Document compiled for ELEC-E7840 Smart Wearables*
*Aalto University, January 2026*
