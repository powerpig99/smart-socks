# Smart Socks - Reference Materials

**ELEC-E7840 Smart Wearables — Aalto University**

---

## Hardware Documentation

### ESP32-S3 Datasheet
- **File:** `esp32-s3_datasheet.pdf`
- **Source:** Espressif Systems
- **Description:** Official datasheet for ESP32-S3 microcontroller

### ESP32-S3 Tutorial
- **File:** `Tutorial_ESP32S3-part1.pdf`
- **Source:** Aalto University / Course Materials
- **Description:** Development tutorial for ESP32-S3

### Seeed Studio XIAO ESP32S3
- **Title:** XIAO ESP32S3 Getting Started
- **URL:** https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/
- **Publisher:** Seeed Studio
- **Description:** Official getting started guide for XIAO ESP32S3 board including pinout, installation, and examples

---

## Academic Papers - Smart Socks & Gait Analysis

### 1. Gait Analysis Using Smart Socks
**Title:** Gait analysis by using Smart Socks system
- **Authors:** ResearchGate contributors
- **URL:** https://www.researchgate.net/publication/329486130_Gait_analysis_by_using_Smart_Socks_system
- **Summary:** Proposes a method for gait pattern recognition using smart sock systems. Steps are classified based on foot pressure patterns.
- **Relevance:** Directly applicable to our project - similar sensor placement and activity recognition goals

### 2. E-Textile Smart Socks Validation
**Title:** E-Textile smart socks for gait analysis: a preliminary validation study
- **Source:** Journal of Biomechanics (ScienceDirect)
- **URL:** https://www.sciencedirect.com/science/article/abs/pii/S0966636222005471
- **Key Findings:** 
  - Sensoria smart socks validation against OPAL IMU system
  - 3 textile pressure sensors per foot (heel, 1st metatarsal, 5th metatarsal)
  - Good agreement for Gait Cycle Time and Cadence
  - Underestimation of stance phase duration
- **Relevance:** Similar sensor placement to our design; validation methodology useful for our evaluation

### 3. SWEET Sock - E-Textile Wearable System
**Title:** Design and Validation of an E-Textile-Based Wearable System for Gait and Postural Assessment
- **Authors:** Federica Amitrano, Armando Coccia, Carlo Ricciardi, et al.
- **Journal:** Sensors (MDPI), 2020, 20(22), 6691
- **URL:** https://www.mdpi.com/1424-8220/20/22/6691
- **Key Points:**
  - 3 pressure sensors per foot (heel, MTB1, MTB5)
  - Uses EeonTex piezoresistive fabric
  - 18kΩ voltage divider resistors
  - BLE transmission at 66.7 Hz
  - Voltage divider circuit design
  - Comparison with stereophotogrammetry (BTS SMART-DX 700)
- **Relevance:** Very similar to our project - textile pressure sensors, ESP32, BLE, validation with gold standard

---

## Academic Papers - Textile Pressure Sensors

### 4. Textile Stitch-Based Piezoresistive Sensors
**Title:** Design, Development and Characterization of Textile Stitch-Based Piezoresistive Sensors for Wearable Monitoring
- **Journal:** IEEE Sensors Journal
- **URL:** https://ieeexplore.ieee.org/document/9091804/
- **Summary:** Textile-based piezoresistive sensors using conductive threads stitched on fabric
- **Relevance:** Fabrication techniques for textile sensors

### 5. Single-Layer Textile Pressure Sensors
**Title:** Fabrication and Characterization of Single‐Layer Textile‐Based Piezoresistive Pressure Sensors
- **Authors:** N.A. Choudhry et al.
- **Journal:** Advanced Engineering Materials, 2023
- **URL:** https://onlinelibrary.wiley.com/doi/10.1002/adem.202201736
- **Key Points:**
  - Single-layer vs multi-layer sensor comparison
  - Graphene nanoplatelet (GNP) coated threads
  - Machine stitching technique
  - 100 kPa working range
  - Response time <50 ms
  - Durability testing (3280 cycles)
- **Relevance:** Advanced fabrication methods for pressure sensors

### 6. Large-Area Piezoresistive Textile Sensors
**Title:** The Programmable Design of Large-Area Piezoresistive Textile Sensors by Jacquard Processing
- **Authors:** SangUn Kim, TranThuyNga Truong, JunHyuk Jang, Jooyong Kim
- **Journal:** Polymers (MDPI), 2023, 15(1), 78
- **URL:** https://www.mdpi.com/2073-4360/15/1/78
- **Key Points:**
  - Single, double, and quadruple layer structures
  - Jacquard weaving method
  - CNT (carbon nanotube) coating
  - Response time <50 ms
  - 1000+ cycle durability
- **Relevance:** Manufacturing methods for textile sensors

### 7. Resistive Sensors with Smart Textiles
**Title:** Investigation and Testing of Resistive Sensors with Smart Textiles
- **Journal:** ARCN Journals
- **URL:** https://arcnjournals.com/wp-content/uploads/2025/10/2293847487847412.pdf
- **Summary:** Piezoresistive sensor characterization and testing methods
- **Relevance:** Testing protocols for textile sensors

### 8. Wearable Pressure and Strain Sensors (Aalto)
**Title:** Fabrication of Wearable Pressure and Strain Sensors
- **Source:** Aalto University (Aaltodoc)
- **URL:** https://aaltodoc.aalto.fi/bitstreams/3af9fa6c-2435-4592-b9ad-8e3ee61aa547/download
- **Summary:** Introduction, fabrication, and characterization of capacitive pressure sensors
- **Relevance:** Local resource from Aalto University

---

## Academic Papers - Activity Recognition & Machine Learning

### 9. Efficient Human Activity Recognition Using ML
**Title:** Efficient Human Activity Recognition Using Machine Learning Majority Decision Model
- **Authors:** Z. Zhang and B. Li
- **Journal:** Applied Sciences (MDPI), 2025, 15(8), 4075
- **URL:** https://www.mdpi.com/2076-3417/15/8/4075
- **Key Points:**
  - Accelerometer and gyroscope-based recognition
  - Majority voting ensemble of multiple ML algorithms
  - 91.92% average accuracy for 12 activities
  - Time and frequency domain features
  - 5-fold cross-validation by subject
  - Activities: walking, stairs, running, jumping, sitting, standing, lying, elevator
- **Relevance:** Very similar activity set to our project; ensemble methods could improve our accuracy

### 10. Human Activity Recognition using ML Techniques
**Title:** Human Activity Recognition using ML Techniques
- **Source:** IJISRT (International Journal of Innovative Science and Research Technology)
- **URL:** https://www.ijisrt.com/assets/upload/files/IJISRT21AUG260.pdf
- **Summary:** Decision Trees and Random Forest for activity recognition
- **Relevance:** Random Forest validation for our chosen algorithm

### 11. Activity Recognition Survey
**Title:** A Survey on Human Activity Recognition using Wearable Sensors
- **Key Points:**
  - Various sensor placements and their trade-offs
  - Feature extraction methods
  - Classification algorithms comparison
- **Relevance:** Methodology guidance for our ML pipeline

---

## Recommended Reading List by Topic

### For Sensor Design
1. SWEET Sock paper (Amitrano et al., 2020) - Similar sensor placement
2. Single-Layer Textile Sensors (Choudhry et al., 2023) - Advanced fabrication
3. Large-Area Jacquard Sensors (Kim et al., 2023) - Manufacturing methods

### For Activity Recognition
1. Efficient HAR Using ML (Zhang & Li, 2025) - Similar activities, ensemble methods
2. E-Textile Smart Socks Validation - Validation methodology
3. Gait Analysis Using Smart Socks - Pattern recognition approaches

### For Circuit Design
1. SWEET Sock paper - Voltage divider design with 18kΩ resistors
2. Seeed Studio XIAO ESP32S3 guide - Pinout and connections

### For Data Processing
1. Efficient HAR paper - Feature extraction (time & frequency domain)
2. E-Textile Smart Socks - Signal processing algorithms

---

## Citation Format (IEEE)

```
[1] Espressif Systems, "ESP32-S3 Series Datasheet," Version 1.0, 2021.

[2] Seeed Studio, "XIAO ESP32S3 Getting Started," Wiki Documentation, 
    Available: https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/

[3] F. Amitrano et al., "Design and Validation of an E-Textile-Based Wearable 
    System for Gait and Postural Assessment," Sensors, vol. 20, no. 22, 
    p. 6691, 2020.

[4] Z. Zhang and B. Li, "Efficient Human Activity Recognition Using Machine 
    Learning Majority Decision Model," Appl. Sci., vol. 15, no. 8, p. 4075, 
    2025.

[5] N. A. Choudhry et al., "Fabrication and Characterization of Single-Layer 
    Textile-Based Piezoresistive Pressure Sensors," Adv. Eng. Mater., 2023.
```

---

## How to Access Full Papers

### Downloaded Papers (in `papers/` folder)

| # | Paper | Filename | Status |
|---|-------|----------|--------|
| 7 | Resistive Sensors with Smart Textiles | `07_Resistive_Sensors_Smart_Textiles.pdf` | Downloaded |
| 8 | Fabrication of Wearable Sensors (Aalto) | `08_Wearable_Sensors_Aalto.pdf` | Downloaded |
| 10 | HAR using ML Techniques | `10_HAR_ML_Techniques.pdf` | Downloaded |

### Papers Requiring Manual Download

**Open Access (free, no account needed):**
- Paper 3 (MDPI - SWEET Sock): https://www.mdpi.com/1424-8220/20/22/6691
- Paper 6 (MDPI - Large-Area Sensors): https://www.mdpi.com/2073-4360/15/1/78
- Paper 9 (MDPI - Efficient HAR): https://www.mdpi.com/2076-3417/15/8/4075

**Requires Aalto University access:**
- Paper 2 (ScienceDirect - E-Textile Validation): https://www.sciencedirect.com/science/article/abs/pii/S0966636222005471
- Paper 4 (IEEE - Stitch Sensors): https://ieeexplore.ieee.org/document/9091804/
- Paper 5 (Wiley - Single-Layer Sensors): https://onlinelibrary.wiley.com/doi/10.1002/adem.202201736

**Requires free ResearchGate account:**
- Paper 1 (Gait Analysis Smart Socks): https://www.researchgate.net/publication/329486130

### Aalto Library Access

- **VPN:** Connect to `vpn.aalto.fi` with Cisco AnyConnect, then access publisher sites directly
- **Aalto-Primo:** https://aalto-primo.hosted.exlibrisgroup.com/ — search by title
- **Proxy:** Replace publisher URL domain with `.ezproxy.aalto.fi` suffix

### Naming Convention for Downloads

```
##_Short_Description.pdf
```
Examples: `01_Gait_Analysis_Smart_Socks.pdf`, `03_SWEET_Sock_E-Textile_System.pdf`

---

## Notes for Project

### Key Design Decisions Supported by Literature

| Design Choice | Supported By | Paper |
|--------------|--------------|-------|
| 3-5 sensors per foot | Amitrano et al., 2020; Sensoria validation | [2] |
| Piezoresistive fabric | Choudhry et al., 2023; Kim et al., 2023 | [5, 6] |
| Voltage divider with 10kΩ resistor | Amitrano et al., 2020 (uses 18kΩ) | [2] |
| 50 Hz sampling rate | Literature standard (25-100 Hz) | Multiple |
| Random Forest classifier | Zhang & Li, 2025; HAR surveys | [4] |
| Time + frequency features | Zhang & Li, 2025 | [4] |
| Leave-subject-out validation | Zhang & Li, 2025 | [4] |
| BLE transmission | Amitrano et al., 2020 | [2] |

### Validation Benchmarks
- **Gait Cycle Time:** ±0.01s accuracy achievable
- **Cadence:** <1 step/min error achievable  
- **Stance/Swing:** Challenging, expect ±5-10% error
- **Spatial parameters:** Most difficult, expect higher errors

---

*Last Updated: 2026-01-29*
*Maintained by: Smart Socks Team*
