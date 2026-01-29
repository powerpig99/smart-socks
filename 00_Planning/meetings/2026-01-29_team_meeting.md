# Team Meeting Notes - January 29, 2026

**Date:** January 29, 2026  
**Time:** 16:00-17:30  
**Location:** Y163 - Interaction Zone  
**Attendees:** Saara, Alex, Jing (all present)

---

## Agenda
1. Review initial sensor concepts
2. Finalize sensor configuration
3. Assign roles and tasks
4. Plan next meetings

---

## Key Decisions

### ✅ Sensor Configuration (Approved Design)

**New Baseline Design:**
- **Per Leg:** 2 pressure sensors + 1 stretch sensor
- **Per Person:** 4 pressure sensors + 2 stretch sensors = **6 total**

| Location | Sensor Type | Placement |
|----------|-------------|-----------|
| Sock | Pressure | Under heel |
| Sock | Pressure | Under ball of foot |
| Knee Pad | Stretch | Front of knee |

**Rationale:**
- Simpler than 5-sensor design while maintaining discrimination capability
- Stretch sensor adds valuable information for stairs vs walking detection
- More practical for fabrication and user comfort
- Cost-effective

### Movement Detection Strategy

**Walking Forward:**
- Heel pressure → Ball pressure
- Knee stretches during swing

**Walking Backward:**
- Ball pressure → Heel pressure
- Knee stretches during swing

**Stairs Up:**
- Sequential heel → ball pressure
- **Stronger** knee stretch (key discriminator from flat walking)

**Stairs Down:**
- Ball → heel pressure
- Knee stretch on trailing leg

**Sitting:**
- Both heels: equal pressure
- Crossed legs: asymmetric pressure/stretch

**Sit-to-Stand:**
- Increasing heel pressure
- Decreasing knee stretch

**Standing:**
- Upright: equal pressure, minimal stretch
- Leaning: asymmetric pressure

---

## Role Assignments

| Team Member | Primary Responsibility | Tasks |
|-------------|------------------------|-------|
| **Saara** | Biosignal Processing | Sensor characterization, signal processing, ML pipeline |
| **Alex** | Design & User Research | Sock/knee pad design, user requirements, physiotherapist consultation |
| **Jing** | Electronics & Firmware | ESP32 programming, circuit design, data acquisition |

---

## Action Items

### Before Next Meeting (Sun 2.2.2026)

**Saara:**
- [ ] Research sensor characterization methods
- [ ] Define signal processing pipeline
- [ ] Review references provided

**Alex:**
- [ ] Sketch sock and knee pad designs
- [ ] Consult with physiotherapist if possible
- [ ] Research user requirements for wearable comfort

**Jing:**
- [ ] Update ESP32 firmware for 6-sensor configuration
- [ ] Test pressure sensor circuits
- [ ] Research stretch sensor interfacing

**All:**
- [ ] Bring materials to workshop (Wed 04-02)

---

## Next Meetings

| Date | Time | Location | Purpose |
|------|------|----------|---------|
| Sun 2.2.2026 | 14:45-16:45 | Y163 | Progress review, prototype planning |
| Wed 4.2.2026 | Workshop | TBD | WiFi data collection tutorial |

---

## References Shared

1. **Skating Technique (3 pressure sensors):**
   https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2025.1554264/full

2. **Healthcare Monitoring (5 pressure sensors):**
   https://pubs-acs-org.ezproxy.utu.fi:2443/doi/full/10.1021/acsnano.8b08329

---

## Attachments

- [Saara's sketch: Initial design concept](../../02_Fabrication/IMG_6071.jpeg)
- [Meeting room booking confirmation](../../Smart%20Wearables%20Project%20Work/2026-01-29%2018.54.13.jpg)

---

*Meeting recorded by: Jing*  
*Last updated: 2026-01-29*
