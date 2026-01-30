# Teacher Feedback - January 30, 2026

**Course:** ELEC-E7840 Smart Wearables, Aalto University  
**Feedback Session:** January 30, 2026  
**Relevance:** Topic 3 - Smart Socks with Knee Pads

---

## Critical Requirements (Must Address)

### 1. 'Unknown' Class is REQUIRED

**Feedback:** It's crucial to ensure your socks do not misinterpret 'unknown' activities as one of the intended target activities. The AI should indicate 'unknown' rather than providing an incorrect result.

**Implications for Our Project:**
- Activities NOT in our list (jumping, running, random movements) should NOT be misclassified as walking, stairs, sitting, etc.
- During final review, prototypes will be tested with random gestures to verify they don't misclassify them

**Action Items:**
- [x] Add 'unknown' class to `config.py` ACTIVITIES
- [ ] Collect data for 'unknown' activities (jumping, running, random leg movements)
- [ ] Train model to recognize and reject non-target activities
- [ ] Test extensively with random movements during validation

**Data Collection for Unknown Class:**
- Jumping (both legs, single leg)
- Running in place
- Random leg shaking while sitting
- Stretching exercises
- Lying down with leg movement
- Any other non-target movement

---

## Validation Strategy

### Mid-Term Review Requirements

**What We Need to Show:**
1. ✅ Working sensors integrated into socks and knee pads
2. ✅ Real-time data collection from all 6 sensors simultaneously
3. ✅ Sensor characterization (sensitivity, sensing range, calibration)
4. ✅ Explanation of sensor layout choice

**What We DON'T Need for Mid-Term:**
- Machine learning implementation
- Activity classification working

**Demo Format:**
- Live demo OR pre-recorded video showing sensor readings varying in real-time
- Must clearly show how sensor values change with different activities

---

## Hardware Recommendations

### 1. Knee Pads with Bending Sensors

**Feedback:** Knee pads with bending sensors are good options for detecting knee bending.

**Our Status:** ✅ **Already implemented**
- L_S_Knee (Left Stretch - Knee)
- R_S_Knee (Right Stretch - Knee)

**Teacher Confirmation:** This validates our sensor layout choice.

---

### 2. USB vs Battery Power

**Feedback:**
- USB cables allowed for gloves and calculators
- For socks and knee pads: **recommended to use batteries** for improved wearability
- Can switch from USB to batteries after mid-term review
- Teacher can provide batteries if needed

**Our Plan:**
- Phase 1 (Now - Mid-term): Use USB for development and demo
- Phase 2 (After mid-term): Switch to battery power
- Contact teacher for battery provision

---

## Sensor Layout Considerations

### Sensor Count Strategy

**Feedback:** Generally advisable to begin with a larger number of sensors and later eliminate those that are irrelevant or less important.

**Our Approach:**
- Started with 10 sensors (5 per sock)
- Reduced to 6 sensors (3 per leg: 2 pressure + 1 stretch)
- This is appropriate - we validated that 6 sensors can distinguish our target activities
- Need to ensure our 6 sensors can differentiate ALL target activities AND unknown activities

### Multiplexer Consideration

**Feedback:** If you have a substantial number of sensors, you may need multiplexers due to limited ESP32 pins.

**Our Status:** ✅ **Not needed**
- Using 6 sensors across 2 ESP32s
- Each ESP32 reads only 3 sensors (A0, A1, A2)
- No multiplexers required

---

## Testing Strategy

### 1. Test with 'Unknown' Activities

**Feedback:** When testing prototypes, ensure you also evaluate them with 'other' or 'unknown' gestures/activities.

**Test Plan:**
1. **Target Activity Testing:** Verify correct classification of all 11 target activities
2. **Unknown Activity Testing:** Verify these are NOT misclassified:
   - Jumping (various styles)
   - Running
   - Random leg movements
   - Stretching
   - Lying down with leg movement

### 2. Misclassification Prevention

**Example from Feedback:** Letter B and 4 can be easily misclassified if you cannot differentiate finger abduction and adduction.

**Our Analog:**
- Walking vs Running: Need to distinguish cadence/speed
- Stairs Up vs Jumping: Need to distinguish knee bend pattern
- Sitting vs Lying: Need to distinguish leg angle

**Mitigation:**
- Knee stretch sensors help distinguish jumping from stairs
- Pressure pattern analysis distinguishes running from walking

---

## Immediate Action Items

### For Mid-Term Review (Week 7)

**Priority 1 - Hardware:**
- [ ] Complete sensor fabrication
- [ ] Integrate sensors into socks and knee pads
- [ ] Test all 6 sensors working simultaneously
- [ ] Calibrate sensors with known weights

**Priority 2 - Data Collection:**
- [ ] Collect sample data for each target activity
- [ ] Collect "unknown" activity samples (jumping, running)
- [ ] Demonstrate real-time visualization working

**Priority 3 - Documentation:**
- [ ] Document sensor layout rationale
- [ ] Document sensor characterization results
- [ ] Prepare demo video or live demo script

### Post Mid-Term (Part 2 - ML Phase)

- [ ] Switch to battery power
- [ ] Implement full ML pipeline
- [ ] Train model with 'unknown' class
- [ ] Validate with extensive testing including unknown activities

---

## Key Dates & Milestones

| Date | Milestone | Status |
|------|-----------|--------|
| Week 5-6 | Sensor fabrication complete | In Progress |
| Week 7 | Mid-term review | Demo + sensor characterization |
| Week 8-15 | ML training and classification | Jing only |

---

## Summary

The teacher feedback validates several of our design choices:
1. ✅ Knee pads with stretch sensors are appropriate
2. ✅ Our sensor count (6) is reasonable
3. ⚠️ We MUST implement 'unknown' class handling
4. ⚠️ We should switch to batteries post mid-term
5. ⚠️ Mid-term demo needs real-time sensor visualization

**Critical Gap Identified:** We need to collect data for and train an 'unknown' class to handle non-target activities like jumping and running.

---

*Document created for Smart Socks Project - ELEC-E7840 Smart Wearables*
