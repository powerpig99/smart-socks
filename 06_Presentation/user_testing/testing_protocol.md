# Smart Socks User Testing Protocol

**ELEC-E7840 Smart Wearables — Aalto University**

---

## Overview

This document describes the standardized protocol for testing the Smart Socks wearable device. The protocol ensures consistent evaluation across all participants and covers both wearability assessment and system usability testing.

**Estimated Duration:** 30-45 minutes per participant  
**Minimum Participants Required:** 5 (for final evaluation)  
**Equipment Needed:**
- Smart Socks prototype
- ESP32S3 with charged battery
- Laptop/tablet for real-time display
- Stopwatch
- Questionnaires (printed or digital)
- Stairs access (for stair climbing activity)
- Chair (for sitting/stand-to-sit activities)

---

## Pre-Test Setup (5 minutes)

### 1. Equipment Check
- [ ] ESP32S3 powered on and connected
- [ ] BLE connection established with display device
- [ ] Real-time classification display visible
- [ ] All 6 sensors responding to pressure
- [ ] Step counter reset to zero

### 2. Participant Briefing
Read the following to the participant:

> "Thank you for participating in our user study. We are testing a Smart Socks device that uses pressure sensors to recognize activities like walking, climbing stairs, sitting, and standing. The system also counts your steps.
> 
> During this test, you will perform a series of activities while wearing the socks. We'll ask you to complete some questionnaires about your experience. There are no right or wrong answers - we want your honest feedback to help us improve the device.
> 
> Please let us know if you experience any discomfort at any point, and you can stop the test at any time."

### 3. Baseline Measurement
- Record participant's shoe size: ___________
- Check sock fit: [ ] Good [ ] Tight [ ] Loose
- Note any initial comfort issues: ___________

---

## Part 1: Wearability Assessment (15 minutes)

### Activity Sequence

Participants perform the following activities in order:

#### 1. Walking Test (5 minutes)
- **Forward walking:** Walk 20 meters forward at normal pace
- **Backward walking:** Walk 10 meters backward
- **Observer notes:**
  - [ ] Any gait changes?
  - [ ] Discomfort reported?
  - [ ] Socks staying in place?

#### 2. Stair Climbing (5 minutes)
- **Stairs up:** Climb 2 flights of stairs
- **Stairs down:** Descend 2 flights of stairs
- **Observer notes:**
  - [ ] Any hesitation or caution?
  - [ ] Grip/slip issues?
  - [ ] Comfort on steps?

#### 3. Sitting Test (3 minutes)
- **Sitting feet on floor:** Sit for 1 minute with feet flat
- **Sitting cross-legged:** Sit for 1 minute cross-legged
- **Observer notes:**
  - [ ] Pressure point discomfort?
  - [ ] Ease of position change?

#### 4. Standing Test (2 minutes)
- **Standing upright:** Stand still for 30 seconds
- **Leaning left:** Lean left for 15 seconds
- **Leaning right:** Lean right for 15 seconds
- **Observer notes:**
  - [ ] Balance affected?
  - [ ] Discomfort during leaning?

---

## Part 2: System Usability Test (10 minutes)

### Real-Time Feedback Session

Show the participant the real-time classification display and explain:

> "This screen shows what activity the system thinks you're doing. The activity name and confidence level are displayed, along with a step counter."

#### Test Sequence:

1. **Activity Recognition Test (5 minutes)**
   - Have participant perform each activity for 30 seconds
   - Observer records system accuracy:

| Activity | Attempts | Correct Detections | Accuracy |
|----------|----------|-------------------|----------|
| Walking forward | | / | % |
| Walking backward | | / | % |
| Stairs up | | / | % |
| Stairs down | | / | % |
| Sitting (feet on floor) | | / | % |
| Sitting (cross-legged) | | / | % |
| Standing upright | | / | % |
| Standing lean left | | / | % |
| Standing lean right | | / | % |

2. **Step Counting Test (5 minutes)**
   - Have participant walk 50 steps at normal pace
   - Record actual vs. detected steps:
     - Actual steps: ___________
     - Detected steps: ___________
     - Error: ___________%
   
   - Have participant climb 20 steps:
     - Actual steps: ___________
     - Detected steps: ___________
     - Error: ___________%

---

## Part 3: Questionnaires (10 minutes)

Administer in the following order:

1. **WEAR Scale Questionnaire** (5 minutes)
   - 28 questions about wearability and social acceptability
   - Include open-ended feedback section

2. **SUS Questionnaire** (3 minutes)
   - 10 standard SUS questions
   - 5 system-specific questions

3. **Demographics** (2 minutes)
   - Age, gender, occupation
   - Prior experience with wearables

---

## Post-Test (5 minutes)

### Participant Debrief
Ask the participant:

1. "On a scale of 1-10, how would you rate the overall experience?" ___________
2. "Would you use this device daily?" [ ] Yes [ ] Maybe [ ] No
3. "What is the maximum you would pay for such a device?" €___________

### Observer Notes
Record any additional observations:

_______________________________________________

_______________________________________________

_______________________________________________

### Issues Encountered
- [ ] Technical issues (describe): ___________
- [ ] Comfort issues (describe): ___________
- [ ] Safety concerns (describe): ___________

---

## Data Recording

### Spreadsheet Template

Create a spreadsheet with the following columns:

| Field | Description |
|-------|-------------|
| Participant_ID | Anonymous identifier (P01, P02, etc.) |
| Date | Test date |
| Age | Participant age |
| Gender | Participant gender |
| Shoe_Size | Participant shoe size |
| WEAR_Score | Calculated WEAR score |
| WEAR_Comfort | Comfort subscale score |
| WEAR_Social | Social acceptability subscale score |
| SUS_Score | Calculated SUS score |
| SUS_Grade | Letter grade |
| Recognition_Accuracy | Overall activity recognition % |
| Step_Count_Error | Average step counting error % |
| Would_Use_Daily | Yes/Maybe/No |
| Max_Price | Maximum willing to pay |
| Comments | Additional feedback |

---

## Safety Guidelines

### Emergency Procedures
- Participant can stop at any time
- Have first aid kit available
- Ensure stairs have handrails
- Clear walking path of obstacles

### Risk Mitigation
- Test socks beforehand for any electrical issues
- Ensure wires are properly insulated
- Keep battery pack away from water
- Monitor for any skin irritation

---

## Analysis Plan

### Quantitative Analysis
1. Calculate mean WEAR scores across all participants
2. Calculate mean SUS score and grade distribution
3. Analyze recognition accuracy by activity type
4. Calculate step counting error statistics
5. Compare results across demographics

### Qualitative Analysis
1. Code open-ended responses for themes
2. Identify common complaints/suggestions
3. Extract quotes for presentation

### Reporting
Create summary including:
- Participant demographics
- WEAR scale results (mean ± std)
- SUS results (mean ± std, grade distribution)
- Activity recognition accuracy by type
- Step counting accuracy
- Key qualitative feedback themes

---

## References

1. Kelly, N., & Gilbert, S. (2016). The WEAR Scale: Developing a Measure of the Social Acceptability of a Wearable Device. *CHI EA '16*.

2. Brooke, J. (1996). SUS: A 'Quick and Dirty' Usability Scale. *Usability Evaluation in Industry*.

3. Bangor, A., Kortum, P., & Miller, J. (2008). An Empirical Evaluation of the System Usability Scale. *Intl. Journal of Human-Computer Interaction*.

---

*Protocol Version: 1.0*  
*Last Updated: 2026-01-29*
