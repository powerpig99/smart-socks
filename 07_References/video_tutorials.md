# Video Tutorials for Smart Sock Sensor Manufacturing

**ELEC-E7840 Smart Wearables — Aalto University**
**Compiled:** January 31, 2026

> **Related:** [[sensor_manufacturing_research]] | [[REFERENCES]] | [[sensor_placement_v2]] | [[circuit_diagram_v2]]
>
> *GitHub:* [Sensor Manufacturing Research](sensor_manufacturing_research.md) · [References](REFERENCES.md) · [Sensor Placement](../01_Design/sensor_placement_v2.md) · [Circuit Diagram](../01_Design/circuit_diagram_v2.md)

---

## Part 1: Pressure Sensors (Heel & Ball of Foot)

> See [[sensor_manufacturing_research]] Section 1.2 for construction specs and material characteristics.

### Velostat/Linqstat Pressure Sensors

#### Beginner-Friendly Tutorials

**1. eTextiles: How to Make a Pressure Sensor (YouTube)**
- **URL:** https://www.youtube.com/watch?v=Qnoso-uHNfs
- **Fallbacks:** [Instructables version](https://www.instructables.com/eTextiles-How-to-Make-a-Pressure-Sensor/) · [Author's site](https://lbruning.com/etextilelounge/how-to-make-a-pressure-sensor/)
- **Channel:** Lynne Bruning
- **Published:** November 8, 2011
- **Level:** Beginner
- **Content:** Basic pressure sensor using conductive fabric, Velostat, and regular fabric. Good starting point for understanding the sandwich construction.
- **Relevance:** ⭐⭐⭐⭐⭐ Essential basics
- ⚠️ *YouTube link may be unavailable; use fallback links above*

**2. How to Setup Pressure Sensitive Fabric with Velostat and Conductive Fabric (YouTube)**
- **URL:** https://www.youtube.com/watch?v=8SQOBF0_80Y
- **Published:** September 24, 2016
- **Level:** Beginner
- **Content:** Start-to-finish beginners example using conductive fabric and Velostat. Part 1 of 2.
- **Relevance:** ⭐⭐⭐⭐⭐ Complete walkthrough

**3. Pressure Fabric Part 2: Hooking up to Arduino (YouTube)**
- **URL:** https://www.youtube.com/watch?v=aXS2b1hIyGA
- **Published:** October 9, 2016
- **Level:** Beginner-Intermediate
- **Content:** Continuation showing Arduino integration and code.
- **Relevance:** ⭐⭐⭐⭐⭐ Critical for ESP32 integration

**4. Creating Pressure Sensors with Velostat and Conductive Thread (YouTube)**
- **URL:** https://www.youtube.com/watch?v=lPxr8RTkFOQ
- **Published:** November 20, 2014
- **Level:** Beginner
- **Content:** Using conductive thread instead of fabric for electrodes. Alternative construction method.
- **Relevance:** ⭐⭐⭐⭐ Good for learning conductive thread technique

**5. Arduino DIY Bend Flex Pressure Sensor Velostat (YouTube)**
- **URL:** https://www.youtube.com/watch?v=zUN2ZYdYAUo
- **Published:** February 18, 2018
- **Level:** Beginner
- **Content:** Building bend, flex, and pressure sensors using Velostat. Includes material sourcing information.
- **Relevance:** ⭐⭐⭐⭐ Shows multiple sensor types

### Intermediate/Advanced Tutorials

**6. Velostat Homemade Pressure Sensor Mat (Instructables)**
- **URL:** https://www.instructables.com/Velostat-Homemade-Pressure-Sensor-Mat/
- **Published:** September 20, 2017
- **Level:** Intermediate
- **Content:** Creating a pressure sensor matrix using Velostat. Good for understanding multi-sensor arrays.
- **Relevance:** ⭐⭐⭐⭐ If you want to expand beyond 2 pressure points

**7. DIY Pressure Sensor - The Bela Knowledge Base (Written Tutorial)**
- **URL:** https://learn.bela.io/tutorials/pure-data/sensors/diy-pressure-sensor/
- **Level:** Intermediate
- **Content:** Comprehensive guide on Velostat, pressure-sensitive conductive material. Good explanation of theory.
- **Relevance:** ⭐⭐⭐⭐⭐ Best theoretical explanation

**8. Kobakant: Pressure Matrix Code + Circuit (Written)**
- **URL:** https://www.kobakant.at/DIY/?p=7943
- **Level:** Advanced
- **Content:** How pressure matrices work, wiring to Arduino, and matrix parsing code.
- **Relevance:** ⭐⭐⭐⭐ For advanced sensor matrix design

---

## Part 2: Stretch Sensors (Knee Flexion)

> See [[sensor_manufacturing_research]] Section 2.2 for EeonTex characteristics and stretch direction notes.

### EeonTex/Eeonyx Fabric Sensors

**1. Fabric Stretch Sensor (Eeontex) (YouTube)**
- **URL:** https://www.youtube.com/watch?v=oDBm0aezEvg
- **Published:** October 25, 2018
- **Level:** Beginner
- **Content:** Demonstration of Eeonyx fabric as stretch sensor. Shows resistance change with stretch.
- **Relevance:** ⭐⭐⭐⭐⭐ Directly applicable to knee sensors

**2. EeonTex Conductive Fabrics from SparkFun (YouTube)**
- **URL:** https://www.youtube.com/watch?v=2-YMxyYiYm8
- **Published:** February 10, 2017
- **Level:** Beginner
- **Content:** Overview of EeonTex stretchable and pressure-sensing fabrics. Product showcase with applications.
- **Relevance:** ⭐⭐⭐⭐⭐ Shows both sensor types you'll use

**3. Eeonyx Stretch Test (YouTube)**
- **URL:** https://www.youtube.com/watch?v=VLBq6jOihlw
- **Published:** February 25, 2009
- **Level:** Beginner
- **Content:** Early video testing various Eeonyx stretchy conductive fabrics. Shows resistance measurement.
- **Relevance:** ⭐⭐⭐⭐ Historical but useful material comparison

**4. Fabric Stretch Sensor (YouTube)**
- **URL:** https://www.youtube.com/watch?v=W8MSCUVPfbk
- **Channel:** Kitronyx
- **Published:** May 27, 2018
- **Level:** Beginner
- **Content:** Demonstration of copper-coated nylon conductive fabric as stretch sensor.
- **Relevance:** ⭐⭐⭐⭐ Alternative material option

### Fabric Bend Sensors (Alternative to Stretch)

**5. Fabric Bend Sensor (Instructables)**
- **URL:** https://www.instructables.com/Fabric-bend-sensor/
- **Published:** November 9, 2017
- **Level:** Intermediate
- **Content:** Creating a fabric bend sensor using EeonTex instead of Velostat. Useful for knee flexion.
- **Relevance:** ⭐⭐⭐⭐⭐ Best tutorial for knee bend application

**6. Human Breadboard: Stretch Sensor (Written)**
- **URL:** http://thesoftcircuiteer.net/stretch-sensor-human-breadboard/
- **Level:** Intermediate
- **Content:** Using Eeontex with conductive thread and voltage divider circuit.
- **Relevance:** ⭐⭐⭐⭐⭐ Exact circuit you'll use

---

## Part 3: General E-Textile Skills

### Conductive Thread & Fabric Basics

**1. How to Work With Conductive Fabric (Instructables)**
- **URL:** https://www.instructables.com/How-to-Work-With-Conductive-Fabric/
- **Published:** October 10, 2017
- **Level:** Beginner
- **Content:** Complete guide to working with conductive fabric. Design and material choices.
- **Relevance:** ⭐⭐⭐⭐⭐ Foundation skills

**2. E-Textiles Tutorials - SparkFun Learn**
- **URL:** https://learn.sparkfun.com/tutorials/tags/e-textiles
- **Level:** Beginner to Advanced
- **Content:** Collection of tutorials on e-textiles including conductive thread, sensors, and projects.
- **Relevance:** ⭐⭐⭐⭐⭐ Comprehensive learning resource

**3. Making E-Textile Interfaces with Trill Craft (Video)**
- **URL:** https://blog.bela.io/e-textiles-with-trill-craft/
- **Level:** Intermediate
- **Content:** Building robust electrical connections between PCBs and e-textile circuits using conductive thread.
- **Relevance:** ⭐⭐⭐⭐ Connection techniques

**4. 4 Crafty Ways to Make DIY Sewable Electronic Sensors (SparkFun)**
- **URL:** https://blog.sparkfuneducation.com/5-crafty-ways-to-make-diy-sewable-electronic-sensors
- **Level:** Beginner
- **Content:** Various sensor construction techniques using conductive materials.
- **Relevance:** ⭐⭐⭐⭐⭐ Multiple sensor ideas

---

## Part 4: Advanced Resources

### Kobakant DIY Wearable Technology

**Main Site:** https://www.kobakant.at/DIY/

Kobakant is the definitive resource for DIY wearable technology. Their tutorials cover:
- Fabric sensors (pressure, stretch, bend)
- Conductive materials
- Circuit design
- Wearable integration

**Key Pages for Your Project:**
- Fabric Stretch Sensors: https://www.kobakant.at/DIY/?p=210
- Pressure Sensors: https://www.kobakant.at/DIY/?p=7943
- Eeonyx Experiments: https://www.kobakant.at/DIY/?p=5689

### Instructables Projects

**Search terms:** "e-textile sensor", "velostat pressure", "conductive fabric wearable"

Popular projects:
- Velostat pressure mats
- Smart gloves
- Wearable controllers

---

## Recommended Learning Path

### Week 1: Basics
1. Watch: "eTextiles: How to Make a Pressure Sensor" (15 min)
2. Watch: "How to Setup Pressure Sensitive Fabric" Part 1 & 2 (30 min total)
3. Read: "How to Work With Conductive Fabric" Instructable

### Week 2: Stretch Sensors
1. Watch: "Fabric Stretch Sensor (Eeontex)" (10 min)
2. Watch: "EeonTex Conductive Fabrics from SparkFun" (8 min)
3. Build: Follow "Fabric Bend Sensor" Instructable

### Week 3: Integration
1. Explore Kobakant DIY site for specific techniques
2. Plan your sensor placement based on knee bend videos
3. Practice sewing conductive thread connections

---

## Key Techniques to Master

### From Videos
1. **Sandwich construction** — Fabric/Velostat/Fabric layers
2. **Conductive thread sewing** — Making electrical connections
3. **Voltage divider circuit** — Same for both sensor types (see [[circuit_diagram_v2]] for our implementation)
4. **Stretch sensor mounting** — Pre-strain for knee application

### Best Practices
- Always test resistance with multimeter before Arduino connection
- Use insulating fabric between sensor layers
- Keep conductive thread lengths short (<30cm) to reduce noise
- Document calibration values for each sensor

---

## Supplier Videos

### Adafruit
- Eeonyx Stretchy Variable Resistance Sensor: https://www.adafruit.com/product/3669
- Video overview of product features

### SparkFun
- EeonTex product videos and tutorials
- Conductive thread usage guides

---

## Summary Checklist

Before starting fabrication, watch:
- [ ] Basic pressure sensor construction (1 video)
- [ ] Arduino hookup for pressure sensor (1 video)
- [ ] Stretch/bend sensor demonstration (1 video)
- [ ] Conductive thread technique (written tutorial)

This will give you:
- ✅ Understanding of materials
- ✅ Circuit knowledge
- ✅ Construction techniques
- ✅ Integration approach

---

> **Navigation:** [[sensor_manufacturing_research]] | [[REFERENCES]] | [[sensor_placement_v2]] | [[circuit_diagram_v2]]
>
> *GitHub:* [Sensor Manufacturing Research](sensor_manufacturing_research.md) · [References](REFERENCES.md) · [Sensor Placement](../01_Design/sensor_placement_v2.md) · [Circuit Diagram](../01_Design/circuit_diagram_v2.md)

*Document compiled for ELEC-E7840 Smart Wearables*
*Aalto University, January 2026*
