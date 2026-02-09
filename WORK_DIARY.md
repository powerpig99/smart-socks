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

## Meeting 3: February 5, 2026

**Attendees:** All present (Saara, Alex, Jing)

### Key Decisions
- Use **3 layers** of pressure-sensing material with **3 sensors per foot** + **1 stretch sensor per knee**
- External antenna attached to XIAO ESP32S3 — improved WiFi/BLE signal

### Task Assignments
- **Saara:** Wove two fabric samples, will make more
- **Alex:** Will fabricate the pressure sensors (has sewing machine at home)
- **Jing:** Continue software development and sensor testing

---

## Meeting 4 + Work Session: February 9, 2026

**Attendees:** All present (Saara, Alex, Jing)

### Sensor Testing Results
- Sewed **3 sensors onto one sock** — tested and working
- Tested **4 new 3-layer pressure sensors** — all work
- Tested **2 knee stretch sensors** — all work
- **Finding:** 3 layers is still not enough sensitivity → decided to make **smaller 4-layer sensors**

### Midterm Demo Decision
- **Live presentation** for midterm (first one), Friday Feb 14 at 12:15
- Final prep meeting: Wednesday Feb 11 at 16:00

### WiFi Observations
- With external antenna, firmware now connects reliably to the open Aalto network (was previously a signal strength issue)
- **Problem:** Cannot access web interface on the free public network (likely network restrictions)
- Firmware tends to connect to the open network even when hotspot is nearby and on
- **Decision:** Limit to hotspot only for the midterm demonstration

### Firmware & Documentation Work (Jing)
- WiFi reliability overhaul: non-blocking boot, tiered reconnect, AP mode removed
- Serial blocking fixes: removed `while (!Serial)`, guarded output with `if (Serial)`
- Serial always streams when USB host listens (no START needed)
- Documentation sync: README, PROJECT_STATUS, WIFI_CONFIGURATION, CLAUDE.md, AGENTS.md, QUICKSTART, TROUBLESHOOTING

### Next Steps
- [x] Update calibration firmware to use hotspot only (not open networks)
- [ ] Fabricate smaller 4-layer pressure sensors
- [ ] Finish integrating sensors into both socks and knee pads
- [ ] Prepare for midterm demo — check all requirements
- [ ] Meet Wednesday Feb 11 at 16:00 for final prep

---

## Quick Links

- [GitHub Repository](https://github.com/powerpig99/smart-socks)
- [[README|Project Documentation]]
- [Design Sketches](../../02_Fabrication/)

---

*Last updated: February 9, 2026*
