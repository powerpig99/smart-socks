# Individual Essay — ELEC-E7840 Smart Wearables

**Jing Liang** | Smart Socks for Physical Activity Recognition (Topic 3) | Spring 2026

---

## What I Learned

In the Smart Socks project, I handled most of the software and electronics: designing circuits, programming the ESP32-S3 firmware, building Python data collection and visualization tools, and implementing the communication stack (serial, WiFi, and BLE). This experience taught me that wearable system development is fundamentally different from pure software work — the hardware imposes constraints that remain invisible during desk testing and only reveal themselves when you test in the actual operating environment.

## Challenge 1: ESP32-S3 Native USB Behavior

The most frustrating technical challenge was making the firmware work reliably across different conditions. The ESP32-S3 XIAO uses native USB rather than a separate UART bridge chip, which introduces behaviors that are poorly documented and difficult to diagnose.

During development, everything worked fine on my laptop. But on battery power, the device froze at boot. The root cause was `while (!Serial) delay(10);` — a common Arduino pattern that waits for the serial port to be ready. On native USB, this condition is never satisfied without a connected computer, so the device blocked forever. The fix was trivial, but finding it required understanding the hardware-level difference between a UART bridge and the ESP32-S3's built-in USB CDC.

A second issue appeared when the device was connected to USB but no terminal was open: `Serial.println()` at 50 Hz fills the transmit buffer in seconds, and once full, every write blocks the entire main loop — sensors stop, WiFi drops, everything halts. The solution was guarding all serial output with `if (Serial)` to skip writes when no host is listening.

These bugs taught me to always test embedded devices in every deployment scenario (battery-only, USB with terminal open, USB without terminal), not just the convenient one at the workbench.

## Challenge 2: WiFi That Blocks Everything

WiFi connectivity went through several iterations. The initial reconnection logic used `WiFi.scanNetworks()`, which blocks the processor for 2–5 seconds. At Aalto, with dozens of visible access points, the scan would find many networks but none matching our saved hotspot, causing repeated multi-second freezes in the sensor data stream.

The fix was a tiered reconnection strategy: try `WiFi.reconnect()` first (nearly instant, reconnects to the last known AP), and only fall back to a full scan after repeated failures. More importantly, I adopted the principle that WiFi must never block core functionality — sensor sampling and serial streaming continue regardless of WiFi state. This single architectural decision prevented a whole class of reliability problems.

I also discovered that Aalto's open WiFi blocks device-to-device HTTP, making it unusable for our web dashboard demo. We switched to a phone hotspot, which turned out to be more reliable and portable.

## Challenge 3: Iterative Sensor Design

Our sensor configuration evolved substantially through the project. We explored different numbers and placements of sensors before arriving at the final design: 3 pressure sensors per foot (heel, inner ball, outer ball) and 1 stretch sensor per knee, totaling 8 sensors across two ESP32 boards (one per leg).

The three-point pressure layout on the foot captures weight distribution more completely than two sensors could — the medial and lateral metatarsal separation helps distinguish activities like leaning or turning, where weight shifts sideways. The knee stretch sensor detects flexion angle, which is critical for separating stair climbing from flat walking. Each iteration taught us something about what information the system would actually need to distinguish our target activities.

Building supporting tools was equally important. The real-time calibration visualizer I wrote — with live plots, GIF recording, and serial command integration — gave the whole team immediate visual feedback on whether sensors were responding correctly. This made integration sessions far more productive than interpreting raw numbers on a terminal.

## Challenge 4: Team Dynamics

With three team members having different skills and availability, I ended up taking on the bulk of the electronics and software work while my teammates focused on sensor fabrication, garment design, and documentation. The main challenge was that hardware and firmware development are tightly coupled — I needed working sensors to test firmware, but sensor fabrication had its own timeline. I addressed this by using early prototype sensors I had made during a class session to develop and debug the firmware, then validating with the final textile sensors once they were ready. This decoupled the two workflows and avoided a situation where hardware and software problems would surface simultaneously.

I also explored the machine learning side briefly, setting up the preprocessing and feature extraction pipeline. Even without training a model yet, this early exploration shaped practical decisions — choosing the right sampling rate, CSV format, and labeling conventions from the start so that data collected now would be directly usable for classification later.

## Reflection

The most valuable lesson from this project is that wearable systems fail at boundaries: between hardware and software, between bench testing and real-world use, between teammates working on different subsystems. Technical skills like ESP32 programming, protocol implementation, and Python tooling are important, but the deeper insight is about process — always test in the real deployment environment, simplify the design wherever possible, and build tools that make the system's behavior visible to everyone. These principles will stay with me well beyond this course.
