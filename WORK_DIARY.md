# Smart Socks - Work Diary

**ELEC-E7840 Smart Wearables — Aalto University**  
**Team:** Saara, Alex, Jing

---

## Meeting 1: January 21, 2026

**Attendees:** All present (Saara, Alex, Jing)

### Discussion Topics
- How to approach the problem: mapping out different sensor types available, user study, how to use the sensors to create the signals we need
- **Alex:** Sock design, asking physiotherapists, usability, user requirements
- **Saara:** Biosignal creation, knee pads/socks
- **Jing:** Preliminary analysis on the electronics side

### Ideas
- Not only a sports device but also hydration measurement

### Initial Task Assignment
- Fabrication
- Electronics
- Data

---

## Meeting 2: January 29, 2026

**Attendees:** All present (Saara, Alex, Jing)  
**Location:** Y163 - Interaction Zone  
**Time:** 16:00-17:30

### Key Decisions

#### ✅ New Sensor Configuration (Baseline Design)
**Per Leg:**
- **Sock:** 2 pressure sensors (heel + ball of foot)
- **Knee Pad:** 1 stretch sensor (front of knee)
- **Total:** 6 sensors per person (4 pressure + 2 stretch)

**Movement Detection Strategy:**

| Activity | Pressure Pattern | Stretch Pattern |
|----------|------------------|-----------------|
| Walking Forward | Heel → Ball | Knee stretches during swing |
| Walking Backward | Ball → Heel | Knee stretches during swing |
| Stairs Up | Sequential heel → ball | **Stronger** knee stretch (key discriminator) |
| Stairs Down | Ball → heel | Knee stretch on trailing leg |
| Sitting (feet on floor) | Both heels equal | Both knees equal (minimal) |
| Sitting (legs crossed) | Asymmetric pressure | Different stretch magnitudes |
| Sit-to-Stand | Increasing heel pressure | Decreasing knee stretch |
| Standing (upright) | Equal pressure both feet | Minimal/no stretch |
| Standing (leaning) | Asymmetric pressure | Minimal stretch |

### Updated Role Assignments

| Team Member | Responsibility | Tasks |
|-------------|----------------|-------|
| **Saara** | Biosignal Processing | Sensor characterization, signal processing, ML pipeline, references review |
| **Alex** | Design & User Research | Sock/knee pad design, user requirements, physiotherapist consultation |
| **Jing** | Electronics & Firmware | ESP32 programming, circuit design, data acquisition |

### Open Questions
1. How do we structure the knee pad to fit different people?
   - **Idea:** Knitted stretch part in middle + adjustable straps on sides
2. How do we position pressure sensors for various foot sizes?

### References
- [Skating technique detection (3 pressure sensors)](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2025.1554264/full)
- [Healthcare monitoring (5 pressure sensors)](https://pubs-acs-org.ezproxy.utu.fi:2443/doi/full/10.1021/acsnano.8b08329)

### Action Items Before Next Meeting
- [ ] **Saara:** Research sensor characterization methods, define signal processing pipeline
- [ ] **Alex:** Sketch sock and knee pad designs, consult physiotherapist
- [ ] **Jing:** Update ESP32 firmware for 6-sensor config, test circuits
- [ ] **All:** Bring materials to workshop (Wed 04-02)

### Upcoming Meetings

| Date | Time | Location | Purpose |
|------|------|----------|---------|
| Sun 2.2.2026 | 14:45-16:45 | Y163 | Progress review, prototype planning |
| Wed 4.2.2026 | Workshop | - | WiFi data collection tutorial |

---

## Shared Meeting Calendar

### Option 1: Import Calendar File (Recommended)
Download and import the calendar file:
```
00_Planning/meetings/smart_socks_meetings.ics
```

**How to import:**
- **Google Calendar:** Settings → Import & Export → Import → Select .ics file
- **Outlook:** File → Open & Export → Import/Export → Import an iCalendar
- **Apple Calendar:** File → Import → Select .ics file

### Option 2: Manual Calendar Entry
Use these details to create your own calendar event:

### Next Meeting: Sunday, February 2, 2026
```
Title: Smart Socks Team Meeting
Date: 2026-02-02
Time: 14:45 - 16:45
Location: Y163 - Interaction Zone
Attendees: Saara, Alex, Jing
```

### Workshop: Wednesday, February 4, 2026
```
Title: Smart Socks - WiFi Data Collection Workshop
Date: 2026-02-04
Time: TBD (during tutorial slot)
Location: TBD
Attendees: Saara, Alex, Jing
Required: USB-C cable, microcontrollers, breadboard, jumper wires, resistors, sensors
```

---

## Quick Links

- [GitHub Repository](https://github.com/powerpig99/smart-socks)
- [Project Documentation](../../INDEX.md)
- [Design Sketches](../../02_Fabrication/)

---

*Last updated: January 29, 2026*
