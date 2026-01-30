# Chapter 4: Project Practice Advanced - TinyML Applications

**Source:** XIAO: Big Power, Small Board  
**Author:** Marcelo Rovai  
**URL:** https://mjrovai.github.io/XIAO_Big_Power_Small_Board-ebook/chapter_4.html  

---

## About This Chapter

This chapter introduces Tiny Machine Learning (TinyML) applications using XIAO development boards. It covers the entire TinyML workflow from data collection to deployment.

> **For Smart Socks:** Section 2 (Motion Classification) is most relevant - it demonstrates activity recognition using IMU sensors, which directly applies to our pressure/stretch sensor gait classification.

---

## Sections

| Section | Content | Relevance |
|---------|---------|-----------|
| [[00_Introduction]] | Chapter overview | ⭐ General |
| [[01_TinyML_Concepts]] | TinyML fundamentals | ⭐⭐ Important |
| [[02_Motion_Classification]] | Activity recognition with IMU | ⭐⭐⭐ **Critical for Smart Socks** |
| [[03_Audio_Keyword_Spotting]] | Audio ML on XIAO | ⭐ Extension possible |
| [[04_Image_Classification]] | Computer vision | ⭐⭐ Optional enhancement |
| [[05_Object_Detection]] | Object detection | ⭐ Optional |
| [[06_Final_Project]] | Integration project | ⭐⭐ Useful for complete system |

---

## Key Takeaways for Smart Socks

### From Section 2: Motion Classification
- **Spectral Features Block**: FFT-based feature extraction for time-series
- **Impulse Design**: Input → Processing (DSP) → Learning (NN)
- **Model Architecture**: Dense Neural Networks for classification
- **Deployment**: Arduino library generation from Edge Impulse

### Technical Specifications
- **Window Size**: 2000ms (2 seconds) for activity capture
- **Sampling Rate**: 50-100 Hz
- **FFT Length**: 32-64 points
- **Features per Axis**: 21 (spectral + statistical)

---

## How to Use These Notes

1. **Start with**: [[01_TinyML_Concepts]] for fundamentals
2. **Focus on**: [[02_Motion_Classification]] for implementation details
3. **Reference**: Code snippets and configuration values
4. **Compare**: Adapt IMU-based examples to pressure sensor data

---

## Original Book Information

- **Full Title:** XIAO: Big Power, Small Board - Mastering Arduino and TinyML
- **Author:** Marcelo Rovai
- **GitHub:** https://github.com/Mjrovai/XIAO_Big_Power_Small_Board-ebook
- **License:** Open Access

---

*Converted to Markdown for Obsidian - January 2026*
