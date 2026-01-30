# Smart Socks - Reference Materials

**Research papers, datasheets, and technical documentation**

---

## Quick Reference

| Document | Topic | Relevance |
|----------|-------|-----------|
| [XIAO_Big_Power_Small_Board_v20240307.pdf](#xiaobook) | **TinyML Guide** | ⭐⭐⭐ Primary reference - Chapter 4 covers Edge Impulse |
| [2025_Nature_Efficient_HAR_TinyML.pdf](#nature2025) | HAR on Edge | ⭐⭐⭐ Latest research on efficient HAR using TinyML |
| [2022_arXiv_EdgeImpulse_MLOps_Platform.pdf](#edgeimpulse) | Edge Impulse | ⭐⭐⭐ Official platform documentation |
| [2024_arXiv_Wearable_Multimodal_Edge.pdf](#multimodal) | Wearable Edge | ⭐⭐⭐ Multi-modal wearable edge computing |
| [XIAO-Reference-Design.pdf](#refdesign) | Hardware Design | ⭐⭐ Hardware reference for XIAO |

---

## Core References

### <a name="xiaobook"></a>XIAO Big Power Small Board (2024)
**File:** `XIAO_Big_Power_Small_Board_v20240307.pdf` (67 MB)

**Key Chapters:**
- **Chapter 4: Project Practice Advanced - TinyML Applications**
  - TinyML workflow: data collection → preprocessing → model training → deployment
  - Motion classification using XIAO nRF52840 Sense (6-axis IMU)
  - Spectral Features Block explanation (FFT + statistical features)
  - Neural network architecture for time-series classification
  - Edge Impulse Studio step-by-step tutorial

**Why it's important:** This is our primary reference for converting Smart Socks to Edge Impulse. The motion classification example closely matches our gait recognition use case.

**Relevant Pages:** 168-220 (Chapter 4)

---

### <a name="nature2025"></a>Efficient HAR on Edge Devices (Nature 2025)
**File:** `2025_Nature_Efficient_HAR_TinyML.pdf` (3.0 MB)

**Citation:**
```
Nature Scientific Reports (2025)
"Efficient human activity recognition on edge devices using TinyML"
```

**Key Findings:**
- Lightweight deep learning models for HAR using TinyML
- Deployment on resource-constrained devices
- Performance benchmarks and optimization techniques
- Comparison of model architectures (CNN, LSTM, TCN)

**Why it's important:** Latest peer-reviewed research on our exact topic - activity recognition on edge devices.

---

### <a name="edgeimpulse"></a>Edge Impulse MLOps Platform (arXiv 2022)
**File:** `2022_arXiv_EdgeImpulse_MLOps_Platform.pdf` (907 KB)

**Citation:**
```
arXiv:2212.03332 (2022)
"Edge Impulse: An MLOps Platform for Tiny Machine Learning"
```

**Key Content:**
- End-to-end TinyML workflow
- Data forwarder architecture
- Model optimization (quantization, pruning)
- Deployment options (Arduino, C++ library)

**Why it's important:** Official paper describing the platform we plan to use.

---

### <a name="multimodal"></a>Wearable Multi-Modal Edge System (arXiv 2024)
**File:** `2024_arXiv_Wearable_Multimodal_Edge.pdf` (1.1 MB)

**Citation:**
```
arXiv:2409.06341 (2024)
"A Wearable Multi-Modal Edge-Computing System for Real-Time Human Activity Recognition"
```

**Key Content:**
- Multi-modal sensor fusion (accelerometer + pressure)
- Real-time inference on wearable devices
- Edge computing architecture
- Low-power design considerations

**Why it's important:** Similar hardware setup to Smart Socks (multiple sensor types on wearable).

---

## Supporting References

### TinyML Foundations

| File | Year | Topic |
|------|------|-------|
| `2021_arXiv_TinyML_Ubiquitous_Edge_AI.pdf` | 2021 | TinyML for ubiquitous edge AI |
| `2023_arXiv_TinyML_Introduction.pdf` | 2023 | Introduction to TinyML |
| `2024_arXiv_OnDevice_Transfer_Learning.pdf` | 2024 | On-device transfer learning |

### Hardware Documentation

| File | Topic |
|------|-------|
| `2021_Espressif_ESP32S3_Datasheet.pdf` | Official ESP32-S3 datasheet |
| `2023_SeeedStudio_ESP32S3_Tutorial_Part1.pdf` | XIAO ESP32S3 getting started |
| `XIAO-Reference-Design.pdf` | Hardware reference design |

---

## Research Themes

### 1. Activity Recognition on Edge
**Papers:**
- Nature 2025: Efficient HAR on Edge Devices
- arXiv 2024: Wearable Multi-Modal Edge System

**Key Insights:**
- CNN-LSTM hybrid architectures perform best for time-series
- Quantization to Int8 reduces model size by 4x with minimal accuracy loss
- Sliding window approach (2s windows, 50% overlap) standard for HAR

### 2. TinyML Deployment
**Papers:**
- XIAO Book Chapter 4
- Edge Impulse MLOps Platform (arXiv 2022)

**Key Insights:**
- Spectral Features Block (FFT) optimal for repetitive motion
- Dense Neural Networks (2-3 layers) sufficient for 4-6 class problems
- Model sizes: 15-30KB achievable for HAR tasks

### 3. Multi-Modal Sensor Fusion
**Papers:**
- arXiv 2024: Multi-Modal Edge System

**Key Insights:**
- Combining pressure + IMU improves accuracy by 10-15%
- Sensor fusion at feature level (before classification) most effective
- Normalization critical for different sensor scales

---

## How to Use These References

### For Implementation
1. Start with **XIAO Book Chapter 4** ([[XIAO_Chapter_4/00_INDEX]]) for workflow understanding
2. Use **Edge Impulse paper** for platform-specific details
3. Reference **Nature 2025** for model architecture decisions
4. See **LED_DISPLAY_RESEARCH.md** for output/feedback options

### For Paper Writing
1. Cite **XIAO Book** as primary methodology reference
2. Use **Nature 2025** and **arXiv 2024** for related work
3. Reference **Edge Impulse paper** for MLOps justification

### For Optimization
1. **On-Device Transfer Learning** paper for continuous learning
2. **Multi-Modal Edge** paper for sensor fusion techniques
3. **Efficient HAR** paper for quantization strategies

### For Hardware Design
1. **XIAO-Reference-Design.pdf** for hardware best practices
2. **ESP32S3 Datasheet** for electrical specifications
3. **LED Display Research** for output device selection

---

## Chapter 4 - Markdown Version

**Location:** `XIAO_Chapter_4/` folder  
**Format:** Linked Markdown files for Obsidian

| File | Content |
|------|---------|
| [[XIAO_Chapter_4/00_INDEX]] | Chapter overview and navigation |
| [[XIAO_Chapter_4/00_Introduction]] | Chapter introduction |
| [[XIAO_Chapter_4/01_TinyML_Concepts]] | TinyML fundamentals |
| [[XIAO_Chapter_4/02_Motion_Classification]] | **Activity recognition (most relevant)** |
| [[XIAO_Chapter_4/03_Audio_Keyword_Spotting]] | Audio ML |
| [[XIAO_Chapter_4/04_Image_Classification]] | Computer vision |
| [[XIAO_Chapter_4/05_Object_Detection]] | Object detection |
| [[XIAO_Chapter_4/06_Final_Project]] | Integration project |

**Source:** Converted from https://mjrovai.github.io/XIAO_Big_Power_Small_Board-ebook/chapter_4.html

---

## Download Links

Papers downloaded from:
- arXiv: https://arxiv.org/
- Nature Scientific Reports: https://www.nature.com/srep/
- Seeed Studio Wiki: https://wiki.seeedstudio.com/
- Espressif: https://www.espressif.com/

---

## Notes

- All PDFs are open access or included with permission
- File naming convention: `YYYY_Source_ShortTitle.pdf`
- Last updated: February 2026

---

*For questions about these references, see the project documentation or ask the team.*
