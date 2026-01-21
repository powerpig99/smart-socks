# Smart Socks Project

**ELEC-E7840 Smart Wearables — Topic 3**

Team: Saara, Alex, Jing

---

## Folder Structure

```
Smart Socks/
├── 00_Planning/          ← Project plans, meeting notes
├── 01_Design/            ← Sensor layouts, sock sketches, circuit diagrams
├── 02_Fabrication/       ← Photos of prototypes, build documentation
├── 03_Data/              ← Sensor characterization, collected activity data
├── 04_Code/              ← Arduino sketches, Python scripts
├── 05_Analysis/          ← ML results, plots, confusion matrices
├── 06_Presentation/      ← Slides, final report
├── 07_References/        ← Papers from reading list
└── Work_Diary.docx       ← Required deliverable - document as we go
```

---

## Quick Links

| Resource | Location |
|----------|----------|
| Course page | MyCourses |
| Assignment PDF | 00_Planning/ |
| Current plan | 00_Planning/Smart_Socks_Plan.pdf |

---

## Working with Claude

Jing has a Claude session tracking this project. To get Claude's help:

1. **Upload the relevant file(s)** to the chat
2. **Give brief context** ("this is our latest sensor data" or "current circuit diagram")
3. **Ask your question**

Claude can help with: code, data analysis, document drafts, troubleshooting, ML pipeline.

---

## Status

| Phase | Status | Notes |
|-------|--------|-------|
| 1. Sensor characterization | Not started | |
| 2. Prototype design | Not started | |
| 3. Data collection | Not started | |
| 4. ML & integration | Not started | |
| 5. Testing & final | Not started | |

---

## Technical Reference

### Hardware Setup
- **MCU:** ESP32S3 XIAO
- **Sensors:** 10 piezoresistive fabric sensors (5 per sock)
- **Zones:** Heel, Arch, Metatarsal medial, Metatarsal lateral, Toe
- **Circuit:** Voltage dividers with 10kΩ resistors
- **Sampling:** 50 Hz, 12-bit ADC (0-4095)

### Code Structure
```
04_Code/
├── arduino/
│   ├── sensor_test/       # Basic ADC reading for characterization
│   └── data_collection/   # Multi-channel recording with serial commands
└── python/
    ├── requirements.txt
    ├── serial_receiver.py          # Save serial data to CSV
    └── sensor_characterization.py  # Calibration curve analysis
```

### Commands
```bash
# Install Python dependencies
pip install -r 04_Code/python/requirements.txt

# Run serial receiver
python 04_Code/python/serial_receiver.py --port /dev/ttyUSB0

# Arduino serial commands
START S01 walking_forward   # Start recording
STOP                        # Stop recording
STATUS                      # Check status
```

### Data Naming Convention
Format: `<subject_id>_<activity>_<timestamp>.csv`

Activities: `walking_forward`, `walking_backward`, `stairs_up`, `stairs_down`, `sitting_floor`, `sitting_crossed`, `sit_to_stand`, `stand_to_sit`, `standing_upright`, `standing_lean_left`, `standing_lean_right`

### Git
- Local only (no remote)
- `.gitignore` excludes `.csv` data files, Python cache, IDE settings

---

## Contacts

- **Saara** — ML, sensors, documentation
- **Alex** — Prototyping, user testing, design
- **Jing** — Circuit, ESP32, coordination

---

*Last updated: [date]*
