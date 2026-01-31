# Smart Socks - Project Status

**ELEC-E7840 Smart Wearables -- Aalto University**
**Team:** Saara, Alex, Jing
**Last Updated:** January 30, 2026

---

## Current State (Jan 30, 2026)

### Hardware
- **Single ESP32S3 XIAO** reading all 6 sensors on pins A0-A5
- 1 pressure sensor currently connected (A0: L_P_Heel), remaining 5 sensors pending fabrication
- No external antenna -- using onboard PCB antenna

### Communication -- All Verified

| Mode | Status | Notes |
|------|--------|-------|
| Serial/USB | Working | 50Hz streaming, 115200 baud, `/dev/cu.usbmodem2101` |
| WiFi AP | Working | SSID: SmartSocks, IP: `192.168.4.1` |
| WiFi Hotspot | Working | iPhone (Maximize Compatibility), IP: `172.20.10.3` |
| WiFi Home | Working | TP-Link_F528, IP: `192.168.8.167` |
| BLE | Working | Discoverable from iPhone (nRF Connect), weak signal (shared PCB antenna), not visible from macOS CoreBluetooth |
| Web Dashboard | Working | Accessible at device IP over WiFi, shows all 6 sensors in 2x3 grid |

### Firmware Workflow
Source lives in `src/main.ino` (PlatformIO default). Swap firmware by copying:
- **Data collection:** `cp 04_Code/arduino/data_collection_leg/data_collection_leg.ino src/main.ino`
- **Calibration:** `cp 04_Code/arduino/calibration_all_sensors/calibration_all_sensors.ino src/main.ino`
- **Build & upload:** `pio run -t upload`

WiFi mode: set `#define` at top of `src/main.ino`:
- `USE_PHONE_HOTSPOT` (default) -- connect to phone hotspot
- `USE_EXISTING_WIFI` -- connect to home/lab WiFi
- Neither -- AP mode (ESP32 creates its own network)
- Credentials in `src/credentials.h` (gitignored)

### Software

| Tool | Status | Description |
|------|--------|-------------|
| `data_collection_leg.ino` | Working | Main firmware: WiFi + BLE + serial + web dashboard |
| `calibration_all_sensors.ino` | Working | Simple calibration: always streams all 6 sensors |
| `calibration_visualizer.py` | Working | Real-time plots, serial commands (Enter=START/STOP, I=STATUS), GIF recording |
| `collector.py` | Ready | Single-port CSV data collection |
| `config.py` | Ready | Centralized configuration |
| `data_preprocessing.py` | Ready | Data cleaning pipeline |
| `feature_extraction.py` | Ready | ML feature extraction (1s windows, 50% overlap) |
| `train_model.py` | Ready | Random Forest training with cross-subject validation |
| `real_time_classifier.py` | Ready | Live activity classification (serial or BLE) |
| `run_full_pipeline.py` | Ready | End-to-end ML automation |

---

## Mid-Term Review (Week 7)

### Requirements (from teacher)
- Working sensors integrated into socks and knee pads
- Real-time data collection from all 6 sensors simultaneously
- Sensor characterization (sensitivity, sensing range)
- Explain sensor layout choice
- NO machine learning required for mid-term
- Demo: live OR pre-recorded video showing sensor readings varying in real-time

### Checklist

#### Hardware (Priority 1)
- [ ] Fabricate 4 pressure sensors (heel + ball for both socks)
- [ ] Fabricate 2 stretch sensors (knee pads)
- [ ] Integrate sensors into socks and knee pads
- [ ] Build voltage divider circuits (10k resistors)
- [ ] Wire all 6 sensors to ESP32
- [x] Test single sensor working with firmware

#### Sensor Characterization (Priority 2)
- [ ] Calibrate pressure sensors with known weights
- [ ] Test stretch sensor range (knee bend angles)
- [ ] Document sensitivity and sensing range

#### Demo (Priority 3)
- [x] Firmware tested and working (serial + WiFi + BLE)
- [x] Web dashboard showing all 6 sensors
- [x] Calibration visualizer with real-time plots
- [ ] Record demo video or prepare live demo with all sensors

---

## Final Review (Week 15)

- [x] ML pipeline (feature extraction, training, evaluation)
- [x] Real-time classification software
- [x] Cross-subject validation framework
- [x] User testing materials (WEAR, SUS questionnaires)
- [x] Analysis report generator
- [ ] Trained model with >85% accuracy (need data)
- [ ] User study results (5+ participants)
- [ ] 'Unknown' class for non-target activities

---

## Course Structure

| Part | Focus | Duration | Team |
|------|-------|----------|------|
| Part 1 | Hardware & Sensor Characterization (NO ML) | Weeks 1-7 | Saara, Alex, Jing |
| Part 2 | Machine Learning & Classification | Weeks 8-15 | Jing only |
| Part 3 | Edge ML / TinyML Extension (optional) | Personal | Jing only |

---

## Next Steps

1. **Fabricate remaining sensors** -- 4 pressure + 2 stretch
2. **Connect all 6 sensors** and verify with calibration visualizer
3. **Sensor characterization** -- calibration curves with known weights
4. **Collect activity data** from test subjects (S01-S06 training, S07-S09 testing)
5. **Run ML pipeline** -- preprocessing, feature extraction, training
6. **Optional:** BLE ESP32-to-ESP32 for dual-leg wireless communication

---

## Quick Commands

```bash
# Build & upload firmware
pio run -t upload

# Serial monitor
pio device monitor

# Calibration visualizer
cd 04_Code/python
uv run python calibration_visualizer.py --port /dev/cu.usbmodem2101

# Data collection
uv run python collector.py --activity walking_forward --port /dev/cu.usbmodem2101

# Full ML pipeline
uv run python run_full_pipeline.py --raw-data ../../03_Data/raw/ --output ../../05_Analysis/
```

---

*Last updated: 2026-01-30*
