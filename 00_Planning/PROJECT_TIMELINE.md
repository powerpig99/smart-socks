# Smart Socks Project Timeline

**ELEC-E7840 Smart Wearables — Topic 3**  
**Team:** Saara, Alex, Jing

---

## 📅 Project Schedule

| Week | Date Range | Phase | Key Tasks | Deliverables | Owner | Status |
|------|------------|-------|-----------|--------------|-------|--------|
| **1** | Jan 20-26 | Planning & Setup | • Finalize sensor placement design<br>• Order/prepare materials<br>• Set up development environment | Design document, Material list | All | 🟡 In Progress |
| **2** | Jan 27 - Feb 2 | Sensor Fabrication | • Fabricate piezoresistive sensors<br>• Initial sensor testing<br>• Characterization setup | Working sensors (3 per leg) | Alex/Saara | ⚪ Not Started |
| **3** | Feb 3-9 | Sensor Characterization | • Calibration with known weights (0-5kg)<br>• Generate calibration curves<br>• Document sensor specs | Calibration report, Sensitivity data | Saara | ⚪ Not Started |
| **4** | Feb 10-16 | Circuit & Integration | • Build voltage divider circuits<br>• Wire sensors to ESP32S3<br>• Test all 6 channels (3 per ESP32) | Working circuit prototype | Jing | ⚪ Not Started |
| **5** | Feb 17-23 | Prototype Integration | • Integrate into socks<br>• Wearability testing<br>• Iterate design | Wearable prototype v1 | Alex | ⚪ Not Started |
| **6** | Feb 24 - Mar 2 | Data Collection I | • Collect data from 6 training subjects<br>• 11 activities × 3 trials each<br>• Data quality checks<br>• Use dual ESP32 setup | Raw dataset (6 subjects) | All | ⚪ Not Started |
| **7** | Mar 3-9 | **Mid-term Review** | • BLE demo preparation<br>• Present sensor characterization<br>• Show data collection capability | **Mid-term Presentation** | All | 🔴 Critical |
| **8** | Mar 10-16 | ML Pipeline Dev | • Feature extraction<br>• Model training (Random Forest)<br>• Cross-validation | Trained model, Feature set | Saara | ⚪ Not Started |
| **9** | Mar 17-23 | ML Optimization | • Hyperparameter tuning<br>• Cross-subject validation<br>• Confusion matrix analysis | Optimized model (>80% accuracy) | Saara | ⚪ Not Started |
| **10** | Mar 24-30 | Real-time Integration | • Deploy model on PC<br>• Real-time classification<br>• Step counting algorithm | Working real-time demo | Jing | ⚪ Not Started |
| **11** | Mar 31 - Apr 6 | Data Collection II | • Collect from 3 test subjects<br>• Final evaluation dataset<br>• Edge case testing | Test dataset (3 subjects) | All | ⚪ Not Started |
| **12** | Apr 7-13 | User Testing | • WEAR scale questionnaire (5+ users)<br>• SUS usability testing<br>• Comfort evaluation | User study report | Alex | ⚪ Not Started |
| **13** | Apr 14-20 | Analysis & Documentation | • Final accuracy evaluation<br>• Generate confusion matrices<br>• Complete work diary | Analysis report | Saara/Jing | ⚪ Not Started |
| **14** | Apr 21-27 | Final Preparation | • Presentation preparation<br>• Demo rehearsal<br>• Final report writing | Final presentation slides | All | ⚪ Not Started |
| **15** | Apr 28-30 | **Final Review** | • Live demo<br>• Final presentation<br>• Code submission | **Final Deliverables** | All | 🔴 Critical |

---

## 🎯 Key Milestones

### Milestone 1: Sensor Characterization Complete (Week 3)
**Criteria:**
- [ ] All 6 sensors fabricated and tested (4 pressure + 2 stretch)
- [ ] Calibration curves generated (0g, 100g, 200g, 500g, 1kg, 2kg, 5kg)
- [ ] Sensitivity and range documented
- [ ] Sensor variance assessed

### Course Structure: 3 Parts

| Part | Weeks | Focus | Team |
|------|-------|-------|------|
| **Part 1** | 1-7 | Hardware & Sensor Characterization (**NO ML**) | Saara, Alex, Jing |
| **Part 2** | 8-15 | Machine Learning & Classification | Jing only |
| **Part 3** | Personal | Edge ML / TinyML Extension | Jing only |

**Part 1 Ends:** Week 7 (Mid-term Review)  
**Part 2 Ends:** Week 15 (Final Review)

### Milestone 2: Working Prototype (Week 5)
**Criteria:**
- [ ] All sensors integrated into socks
- [ ] ESP32S3 successfully reads all 10 channels
- [ ] Data transmits reliably via serial
- [ ] Prototype is wearable and comfortable

### Milestone 3: Mid-term Review (Week 7)
**Grading Criteria (10 points max):**
| Criteria | Target | Points |
|----------|--------|--------|
| Garment design | Can recognize required activities | 3 |
| Sensor fabrication & characterization | Sensing range & sensitivity measured | 4 |
| Data collection | Multi-sensor + BLE real-time transmission | 3 |

**Deliverables:**
- [ ] Live BLE demo with real-time data transmission
- [ ] Sensor characterization results
- [ ] Working prototype demonstration

### Milestone 4: Trained Model (Week 9) — Part 2 Only
**⚠️ Jing Only — Part 2 (ML)**

**Criteria:**
- [ ] >80% average accuracy on validation set
- [ ] Cross-subject validation performed
- [ ] Feature importance analyzed
- [ ] Confusion matrix generated

### Milestone 5: Real-time Demo Ready (Week 10) — Part 2 Only
**⚠️ Jing Only — Part 2 (ML)**

**Criteria:**
- [ ] Model deployed on PC
- [ ] Real-time classification <100ms latency
- [ ] Step counting working
- [ ] BLE connection stable

### Milestone 6: Final Review (Week 15)
**Grading Criteria (66 points max):**
| Criteria | Weight | Target |
|----------|--------|--------|
| Recognition accuracy | 10 pts | >85% average, >80% per activity |
| Final sensor design | 2 pts | Technically sound, well explained |
| Wearability & Usability | 5 pts | Easy to use, user tested (5+) |
| Live Demo | 5 pts | High performance, robust |
| Work diary | 2 pts | Documented iterative process |
| Individual essay | 2 pts | Reflection on learning |

---

## 👥 Task Distribution

### Saara
- **Primary:** Machine Learning, Data Analysis, Documentation
- **Tasks:**
  - Feature extraction design
  - Random Forest model training
  - Cross-subject validation
  - Confusion matrix analysis
  - Work diary documentation

### Alex
- **Primary:** Prototyping, User Testing, Design
- **Tasks:**
  - Sensor fabrication
  - Sock integration
  - Wearability testing
  - User study coordination
  - WEAR/SUS questionnaires

### Jing
- **Primary:** Circuit Design, Embedded Systems, Coordination
- **Tasks:**
  - ESP32S3 programming
  - Circuit design & wiring
  - BLE implementation
  - Real-time classification deployment
  - Project coordination

---

## ⚠️ Risk Management

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Sensor durability issues | Medium | High | Fabricate spare sensors; use protective layers |
| BLE connectivity problems | Medium | Medium | Fallback to serial; test early and often |
| Low classification accuracy | Medium | High | Iterate feature engineering; try different models |
| Cross-subject performance drop | High | High | Collect diverse training data; normalization |
| Subject recruitment delays | Low | Medium | Start recruitment early; flexible scheduling |
| Hardware failures | Low | High | Have backup components; regular testing |

---

## 📝 Weekly Meeting Schedule

- **Day:** Tuesdays
- **Time:** 14:00-15:00
- **Location:** TBD (or virtual)
- **Agenda:**
  1. Progress update (5 min each)
  2. Blockers discussion
  3. Next week planning
  4. Task assignments

---

*Last updated: 2026-01-29*
