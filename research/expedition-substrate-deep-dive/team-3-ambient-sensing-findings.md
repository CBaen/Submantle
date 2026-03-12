# Team 3 Findings: Ambient Sensing & Spatial Awareness Technology
## Date: 2026-03-10
## Researcher: Team Member 3

---

## Summary

The outer ring of Submantle's awareness model — WiFi sensing, on-device CV, audio classification, sensor fusion, and public data APIs — is more mature and more accessible than most engineers assume. Multiple technologies have crossed from research into commercial products in the last 12 months. The key finding: **a viable outer-ring implementation can be built today, on consumer hardware, without OS vendor cooperation, without surveillance architecture, and without proprietary hardware**. The harder problem is not the sensing itself — it is the consent architecture and the data broker that aggregates it all meaningfully.

---

## 1. WiFi Sensing / RF Sensing

### Battle-Tested Approaches

- **Origin Wireless TruPresence**
  - **What**: Software-only presence and motion detection using CSI (Channel State Information) from existing WiFi signals. Detects human presence, filters pets, provides motion zoning.
  - **Evidence**: Commercial partnerships with Verizon Fios routers (shipping now), Verisure (security), and Airties. Operates entirely on the edge; cloud communication only on event triggers.
  - **Source**: [Origin Wireless TruPresence](https://www.originwirelessai.com/trupresence-2/); [MIT Technology Review](https://www.technologyreview.com/2024/02/27/1088154/wifi-sensing-tracking-movements/)
  - **Fits our case**: Yes — software-only means no hardware procurement. Edge processing means privacy-preserving by design.
  - **Tradeoffs**: Requires integration with the router's firmware or SDK. Not a user-installable app. Partnership model, not a public API.

- **Cognitive Systems WiFi Motion**
  - **What**: AI/ML-based WiFi sensing layer licensed to ISPs and hardware OEMs (Plume, ASUS, etc.). Distributed to 100+ ISPs via Plume's HomePass platform.
  - **Evidence**: Confirmed integration with Plume HomePass across 100+ ISPs globally. Amazon Alexa, Google, and Apple Alexa smart home apps integration announced.
  - **Source**: [Cognitive Systems WiFi Motion](https://www.cognitivesystems.com/wifi-motion/); [WiFi NOW Global](https://wifinowglobal.com/news-and-blog/cognitive-systems-wi-fi-based-rf-cognition-could-expand-to-a-host-of-use-cases/)
  - **Fits our case**: Potentially via ISP partnership or Plume API access, but not a self-service developer API.
  - **Tradeoffs**: B2B licensing model. No documented public API for third-party developers.

### Novel Approaches

- **ESP32-based CSI sensing (Pulse-Fi / open research)**
  - **What**: Using $5–10 ESP32 chips to capture WiFi CSI signals and detect breathing rate and heart rate. Runs entirely on-device (under 600KB RAM). Accepted at IEEE DCOSS-IoT 2025.
  - **Why interesting**: Enables DIY ambient sensing for ~$10/room with no router modification. Could be a first-party Submantle sensor node.
  - **Evidence**: Pulse-Fi achieves 0.08 BPM mean absolute error on single-antenna amplitude; runs on ESP32 in real-time. [UCSC i-NRG Lab](https://inrg.engineering.ucsc.edu/2025/05/30/pulse-fi-a-low-cost-system-for-accurate-heart-rate-monitoring-using-wi-fi-channel-state-information/)
  - **Source**: [Pulse-Fi IEEE DCOSS-IoT 2025](https://inrg.engineering.ucsc.edu/2025/05/30/pulse-fi-a-low-cost-system-for-accurate-heart-rate-monitoring-using-wi-fi-channel-state-information/); [WiFi CSI Human Pose GitHub](https://github.com/euaziel/WiFi-CSI-Human-Pose-Detection)
  - **Fits our case**: High fit — cheap, local, privacy-preserving, no vendor cooperation needed.
  - **Risks**: Requires dedicated hardware node. Not passive on existing routers without firmware access.

- **ESPectre (WiFi CSI + Home Assistant)**
  - **What**: Open-source motion detection using WiFi spectral analysis (CSI) with native Home Assistant integration via ESPHome. Neural network motion detection, on-device, no calibration required.
  - **Evidence**: Active GitHub project; [ESPectre GitHub](https://github.com/francescopace/espectre)
  - **Fits our case**: Direct path to integration with Home Assistant's REST API as an ambient sensor source.
  - **Risks**: DIY/hobbyist maturity. Not production-hardened.

### Emerging Approaches

- **IEEE 802.11bf Standard (ratified September 2025)**
  - **What**: Official WiFi sensing standard published September 26, 2025. Defines bistatic/multistatic sensing in 2.4, 5, and 6 GHz bands. Enables presence detection, environment monitoring, and remote wellness monitoring as standardized WiFi features.
  - **Momentum**: 802.11bf passed IEEE ballot with 98% approval. North American WiFi sensing CPE installations projected to reach 112 million by 2030 (51.6% CAGR from 2024). Qualcomm, Intel, Huawei contributing.
  - **Source**: [IEEE SA 802.11bf-2025](https://standards.ieee.org/ieee/802.11bf/11574/); [ABI Research](https://www.abiresearch.com/press/north-american-wifi-sensing-cpe-installations-to-surge-to-112-million-by-2030); [NIST](https://www.nist.gov/publications/ieee-80211bf-enabling-widespread-adoption-wi-fi-sensing)
  - **Fits our case**: Future-proofs the architecture. As 802.11bf routers ship (2026+), Submantle's WiFi sensing module can switch from CSI hacks to standardized APIs.
  - **Maturity risk**: No consumer routers with certified 802.11bf sensing available as of March 2026. Standard is fresh.

---

## 2. On-Device Computer Vision

### Battle-Tested Approaches

- **YOLO26 (released January 2026) — Ultralytics**
  - **What**: Latest YOLO generation. NMS-free, end-to-end, optimized for edge and low-power devices. Exportable to TFLite/LiteRT for deployment on Raspberry Pi, mobile, and embedded hardware.
  - **Evidence**: Released January 14, 2026. Faster CPU inference vs prior generations, improved small-object accuracy. [YOLO26 Docs](https://docs.ultralytics.com/models/yolo26/); [Roboflow](https://blog.roboflow.com/yolo26/)
  - **Source**: [Ultralytics YOLO Docs](https://docs.ultralytics.com/); [arXiv YOLO Overview](https://arxiv.org/html/2510.09653v2)
  - **Fits our case**: Strong fit for local presence detection without cloud dependency. Runs on consumer hardware (Raspberry Pi 4+, any x86 machine).
  - **Tradeoffs**: Requires a camera. Privacy-sensitive — on-device inference helps but users must opt in.

- **Apple Vision Framework (visionOS/iOS/macOS)**
  - **What**: Apple's on-device CV framework. Supports person detection, body/hand pose tracking, trajectory analysis, scene understanding. All processing on-device — no cloud. Updated at WWDC25 with smaller, faster hand pose model.
  - **Evidence**: Available across iOS, iPadOS, macOS, tvOS, visionOS. [Apple Vision Docs](https://developer.apple.com/documentation/vision); [WWDC25 Vision Session](https://developer.apple.com/videos/play/wwdc2025/272/)
  - **Fits our case**: Excellent for macOS/iOS Submantle clients. Privacy-preserving by Apple's architecture. Can detect person presence without sending data anywhere.
  - **Tradeoffs**: Apple-only. Cannot be used on Windows or Android.

- **MOLO: MobileNet + YOLO Hybrid**
  - **What**: Hybrid architecture combining MobileNetV2 (resource-constrained) and YOLOv8-s (high accuracy). Targets embedded devices. INT8 quantization support.
  - **Evidence**: [Springer Nature Link](https://link.springer.com/article/10.1007/s44163-025-00398-3)
  - **Fits our case**: Good middle path when YOLO26 is too heavy for a given device.
  - **Tradeoffs**: More complex deployment than single-model approaches.

### Novel Approaches

- **MS-YOLO: Infrared + MobileNetV4 for edge deployment**
  - **What**: Infrared object detection for edge using MobileNetV4 backbone + SlideLoss. Designed for low-light/no-light environments.
  - **Why interesting**: Enables passive presence detection without visible-light cameras — lower privacy concern.
  - **Evidence**: [arXiv 2509.21696](https://arxiv.org/abs/2509.21696)
  - **Fits our case**: Thermal/IR presence detection is less invasive than RGB cameras. Emerging hardware market.
  - **Risks**: IR sensors add hardware cost. Less mature ecosystem.

### Emerging Approaches

- **On-device LLM + sensor fusion for intent inference**
  - **What**: Pairing lightweight LLMs (Llama 3.1 8B, Qwen2.5-VL-7B) with sensor inputs for context-aware agents. RAG-based sensor prompts feeding real-time state to the model.
  - **Momentum**: "2026 will be the year of Hybrid AI" with local LLMs handling simple context, cloud for heavy reasoning. [Edge AI Vision Alliance](https://www.edge-ai-vision.com/2026/01/on-device-llms-in-2026-what-changed-what-matters-whats-next/); [SiliconFlow Guide](https://www.siliconflow.com/articles/en/best-llms-for-edge-ai-devices-2025)
  - **Fits our case**: This is exactly Submantle's Agent API layer — sensor data → local context model → broker decision. On-device LLMs mean Submantle doesn't need cloud for the interpretation layer.
  - **Maturity risk**: 7–8B models still need 8–16GB RAM. Viable on developer machines, not on minimal edge nodes yet.

---

## 3. Audio Classification / Ambient Sound

### Battle-Tested Approaches

- **TensorFlow Lite + YAMNet (Google)**
  - **What**: YAMNet classifies 521 audio event classes (speech, alarms, doorbells, typing, music, silence, etc.) from raw audio waveforms. Runs on-device via TFLite. Pre-trained model available with TFLite metadata for direct mobile integration.
  - **Evidence**: [TFLite Audio Classification](https://www.tensorflow.org/lite/examples/audio_classification/overview); [TFLite Task Library](https://www.tensorflow.org/lite/inference_with_metadata/task_library/audio_classifier). Google Codelab for Android audio classification: [developers.google.com](https://developers.google.com/codelabs/tflite-audio-classification-basic-android)
  - **Fits our case**: Cross-platform (Android, iOS, Windows, Linux, Raspberry Pi). Pre-trained on 521 classes covers nearly all ambient events Submantle would care about. Real-time inference on consumer hardware.
  - **Tradeoffs**: 521 classes is broad — custom fine-tuning needed for domain-specific events (specific alarm types, specific voices). TFLite Model Maker enables transfer learning with minimal training data.

- **Apple Sound Analysis Framework (macOS/iOS)**
  - **What**: Apple's on-device audio classification using Core ML. Classify ambient sounds in real-time. Fully on-device, privacy-preserving by architecture.
  - **Evidence**: Available as part of the Apple ML stack alongside Core ML. WWDC sessions confirm continued investment.
  - **Fits our case**: Excellent for macOS Submantle client. Classifies environmental sounds without any network calls.
  - **Tradeoffs**: Apple-only. Cannot be the cross-platform solution.

### Novel Approaches

- **Custom TFLite Model Maker for domain-specific events**
  - **What**: Transfer learning on top of YAMNet for detecting specific events relevant to the user's environment (specific device sounds, their doorbell model, their smoke detector brand).
  - **Evidence**: [Google AI Edge Model Maker](https://ai.google.dev/edge/litert/libraries/modify/audio_classification)
  - **Fits our case**: Submantle's learning engine (Core Capability 3: User Intent Model) could build personalized audio classifiers over time. The user trains their model without data leaving the device.
  - **Risks**: Requires a training pipeline in Submantle. Adds complexity.

---

## 4. Sensor Fusion

### Battle-Tested Approaches

- **Extended Kalman Filter (EKF) fusion of WiFi/IMU/LiDAR**
  - **What**: Filter-based fusion for indoor localization. Proven in autonomous vehicles and robotics. Achieving sub-5ms latency on KITTI dataset; 99.3% fusion accuracy on nuScenes.
  - **Evidence**: [arXiv EKF WiFi/LiDAR/IMU](https://arxiv.org/pdf/2509.23118); [Uplatz multi-sensor fusion analysis](https://uplatz.com/blog/real-time-multi-sensor-fusion-architectures-for-autonomous-perception-a-comprehensive-analysis-of-lidar-camera-radar-and-imu-integration/)
  - **Fits our case**: Submantle's middle-ring (hardware sensors) + outer-ring (WiFi, audio) fusion needs this class of algorithm to produce unified spatial awareness.
  - **Tradeoffs**: EKF assumes Gaussian noise. Deep learning fusion (below) handles non-linearity better but requires training.

- **Multimodal audio/video/RFID fusion for activity recognition**
  - **What**: Fusing audio, video, and RFID substantially improves classification accuracy for activity recognition over any single modality.
  - **Evidence**: [Springer multimodal survey](https://link.springer.com/chapter/10.1007/978-3-642-14883-5_39); [PMC multimodal healthcare](https://pmc.ncbi.nlm.nih.gov/articles/PMC9375645/)
  - **Fits our case**: Submantle's outer ring can fuse WiFi motion data + audio events + camera presence into a single "is the user working/sleeping/away/in a call" signal.
  - **Tradeoffs**: More modalities = more processing overhead. Submantle needs to be lightweight by design.

- **Home Assistant as existing sensor fusion hub**
  - **What**: Home Assistant aggregates Matter, Zigbee, Z-Wave, WiFi, Bluetooth, and hundreds of third-party integrations into a unified REST API. Millions of active installations. ESPHome adds custom sensor nodes (WiFi CSI, environmental, mmWave presence).
  - **Evidence**: [Home Assistant REST API](https://developers.home-assistant.io/docs/api/rest/); [ESPHome integration](https://www.home-assistant.io/integrations/esphome/)
  - **Fits our case**: **This is the most pragmatic path for Submantle's outer ring.** Rather than building a sensor fusion layer from scratch, Submantle can treat a local Home Assistant instance as an already-fused environmental data source via its REST API. Optional integration, not required.
  - **Tradeoffs**: Requires user to have Home Assistant installed. Not zero-setup. Adds a dependency.

### Emerging Approaches

- **Deep learning sensor fusion (CNN/RNN-based)**
  - **What**: Replacing filter-based fusion with learned representations. Better handles nonlinear sensor relationships and missing modalities.
  - **Momentum**: Active research direction; increasingly practical on NPU-equipped consumer hardware.
  - **Source**: [Springer sensor fusion DL overview](https://link.springer.com/article/10.1007/978-3-642-14883-5_39); [Emergent Mind survey](https://www.emergentmind.com/topics/sensor-fusion-framework)
  - **Fits our case**: Future direction for Submantle's learning engine. Not needed in v1.
  - **Maturity risk**: Training data collection for the user's specific environment remains unsolved.

---

## 5. Public Data APIs

### Battle-Tested: Traffic

- **GTFS Realtime (transit)**
  - **What**: Open standard. Real-time trip updates, service alerts, vehicle positions from transit agencies worldwide. Mobility Database catalogs 6000+ feeds in 99+ countries.
  - **Source**: [GTFS.org](https://gtfs.org/); [Mobility Database](https://transitfeeds.com/); [Google GTFS Realtime](https://developers.google.com/transit/gtfs-realtime)
  - **Fits our case**: Free, open, standardized. Submantle can pull "user's commute route is disrupted" as outer-ring context.
  - **Tradeoffs**: Transit only. Not road traffic.

- **511 SF Bay / regional 511 systems**
  - **What**: Real-time road closures, detours, traffic events for participating jurisdictions. Free API.
  - **Source**: [511.org Open Data](https://511.org/open-data)
  - **Fits our case**: U.S.-regional. Not global.

- **Google Maps Directions/Traffic API**
  - **What**: Real-time traffic conditions, travel time estimates. Pay-as-you-go pricing. Waze data is NOT directly accessible via API (Google doesn't expose it). Waze Transport SDK is restricted to transportation companies via partnership.
  - **Source**: [Google Maps Pricing](https://mapsplatform.google.com/pricing/); [Waze for Developers](https://developers.google.com/waze)
  - **Fits our case**: Reliable but paid. Appropriate for premium Submantle tier.
  - **Tradeoffs**: Cost. Privacy implication of sending location to Google to get traffic.

### Battle-Tested: Environmental

- **OpenAQ**
  - **What**: Open-source air quality platform. Aggregates hundreds of global sources. Free tier: 300 calls per 5-minute window.
  - **Source**: [OpenAQ](https://openaq.org/)
  - **Fits our case**: "Air quality in user's neighborhood is poor — consider closing windows" is valid outer-ring context.

- **AirNow API (US EPA)**
  - **What**: Official U.S. air quality data. Free. Real-time AQI.
  - **Source**: [AirNow](https://www.airnow.gov/)

- **Open-Meteo Air Quality API**
  - **What**: Free, open-source weather and air quality API. No API key required for basic use.
  - **Source**: [Open-Meteo](https://open-meteo.com/en/docs/air-quality-api)

- **Meersens Noise API**
  - **What**: Average noise levels by location. Comparison to WHO standards. Health recommendations.
  - **Source**: [Meersens](https://meersens.com/api/?lang=en)

### Battle-Tested: Municipal Open Data

- **Data.gov / Socrata**
  - **What**: Catalogs raw government data APIs (U.S.). Socrata Open Data API is the standard for city/state open data portals.
  - **Source**: [Data.gov](https://data.gov/developers/apis/); [Socrata](https://dev.socrata.com/)
  - **Fits our case**: Submantle can query 311 incident reports, permit activity, infrastructure closures.

### Gaps: Safety Data

- **Ring Neighbors API**: Not publicly available. Ring does not expose Neighbors data to third-party developers. Amazon Sidewalk opened developer access in 2023 but is restricted to low-bandwidth IoT (not video feeds). No path to Neighbors data without Amazon partnership.
  - **Source**: [Amazon Sidewalk Developer](https://techcrunch.com/2023/03/28/amazon-opens-its-low-bandwidth-long-range-sidewalk-network-to-developers/)

- **Citizen App**: No public API. The "citizen-api" GitHub project is an unofficial/reverse-engineered effort, not a supported integration. Terms of service prohibit it.
  - **Source**: [Citizen API GitHub (unofficial)](https://github.com/MichaelEvtushenko/citizen-api)

- **Emergency/Safety data**: The most accessible path is FEMA's public feeds, NOAA weather alerts (free, standardized), and city-specific open data portals — not consumer safety apps.

---

## 6. Bluetooth/BLE Mesh & Matter Protocol

### Battle-Tested Approaches

- **Matter 1.5 (current as of March 2026)**
  - **What**: Published November 20, 2025. Matter is an application-layer standard (not a radio protocol) that works over WiFi, Thread, and Ethernet. Supported by Apple Home, Google Home, Amazon Alexa, Samsung SmartThings.
  - **Sensor types exposed**: Occupancy (PIR, radar, vision, ambient), temperature, humidity, pressure, illuminance, air quality (PM2.5, VOC, CO2), door/window contact, water leak, smoke, CO. Matter 1.4 added customizable sensitivity + event-based reporting for occupancy sensing. Matter 1.5 added cameras and soil moisture.
  - **Evidence**: [CSA Matter 1.4 announcement](https://csa-iot.org/newsroom/matter-1-4-enables-more-capable-smart-homes/); [Matter 1.5 status review](https://matter-smarthome.de/en/development/the-matter-standard-in-2026-a-status-review/); [Matter Wikipedia](https://en.wikipedia.org/wiki/Matter_(standard))
  - **Fits our case**: Matter SDK is open-source (github.com/project-chip/connectedhomeip). Submantle can implement a Matter controller to read all sensor data from any Matter device on the local network — without OS vendor cooperation.
  - **Tradeoffs**: Matter controller role requires a Thread Border Router for Thread devices. WiFi-based Matter devices work without it. Matter 1.4/1.5 adds radar and vision presence sensing which directly maps to Submantle's outer ring.

- **Thread Mesh**
  - **What**: IPv6 mesh protocol for battery-powered sensors. Self-healing, low-power. As of January 1, 2026, Thread 1.3 devices are no longer accepted (Thread 1.4 required).
  - **Source**: [Matter & Thread Explained 2026](https://datawiresolutions.com/blog/matter-thread-explained-2026)
  - **Fits our case**: Thread sensors (occupancy, temperature, air quality) are directly readable by a Matter controller Submantle implements.

- **mmWave Radar Presence Sensors (consumer, 2025–2026)**
  - **What**: 60GHz mmWave sensors (Aqara FP300, SwitchBot Presence Sensor) detect presence including stillness, breathing, heartbeat. Consumer prices: ~$30–70. Matter/Zigbee/WiFi connectivity. Home Assistant integration available.
  - **Evidence**: [Seeed Studio mmWave Guide 2026](https://www.seeedstudio.com/blog/2025/02/25/best-presence-sensors-for-home-assistant/); [SmartHomeScene Best Presence Sensors 2026](https://smarthomescene.com/blog/best-and-worst-presence-sensors-for-home-assistant/). Infineon XENSIV 60GHz: [Infineon](https://www.infineon.com/products/sensor/radar-sensors/radar-sensors-for-iot/60ghz-radar)
  - **Fits our case**: Off-the-shelf hardware that integrates with Home Assistant AND Matter. Submantle reads them via Matter SDK or HA API.
  - **Tradeoffs**: Requires user to purchase hardware. But ~$30/room and no subscription.

---

## 7. Hardware APIs by Platform

### Windows

- **Sensor API (Win32 / `Windows.Devices.Sensors`)**
  - Accelerometer, inclinometer, compass, gyrometer, light sensor, altimeter — accessible via Win32 ISensorManager COM interface or WinRT `Windows.Devices.Sensors` namespace.
  - **Practical reality for desktop**: Most Windows desktops (non-laptop) have NO physical sensors. Laptops have accelerometers and ambient light sensors. The meaningful sensors on Windows are: webcam (MediaCapture API), microphone (WASAPI / MediaCapture), Bluetooth (Windows.Devices.Bluetooth), and WiFi (Windows.Devices.WiFi + Wlan API).
  - **Source**: [Microsoft Sensor API](https://learn.microsoft.com/en-us/windows/win32/sensorsapi/portal); [Windows.Devices.Sensors](https://learn.microsoft.com/en-us/uwp/api/windows.devices.sensors)

- **Webcam**: `Windows.Media.Capture.MediaCapture`. Requires `webcam` capability declaration. Full programmatic access.
- **Microphone**: WASAPI (low-level) or `Windows.Media.Capture`. Requires `microphone` capability.
- **Bluetooth/BLE**: `Windows.Devices.Bluetooth` — scan, advertise, connect, GATT. No elevated permissions required for scanning.
- **UWB on Windows**: Not exposed through public APIs. UWB chipsets in some laptops are not accessible to applications. **UWB on Windows is a gap.**
- **WiFi CSI**: Not accessible through Windows WiFi APIs. Requires dedicated hardware (ESP32) or special router firmware.

### macOS

- **Camera/Microphone**: AVFoundation. Privacy-gated (user permission dialog). Full programmatic access once granted.
- **UWB (NearbyInteraction)**: iOS/watchOS only. **macOS does NOT have a public UWB API.** Macs with UWB (M2+ have T2/UWB) expose it only to Apple's internal Handoff/AirDrop — no public API for third-party apps.
- **Bluetooth/BLE**: CoreBluetooth — full access including scanning, GATT.
- **Accelerometer/IMU**: MacBooks have accelerometers (SMS — Sudden Motion Sensor) but this is not a public API. No public IMU access on macOS.
- **Source**: [Apple Nearby Interaction](https://developer.apple.com/documentation/nearbyinteraction); [Apple Vision Framework](https://developer.apple.com/documentation/vision)

### iOS

- **Camera**: AVFoundation. Permission required. Full local inference via Core ML / Vision framework.
- **Microphone**: AVFoundation + SoundAnalysis framework. Permission required.
- **UWB**: `NearbyInteraction` framework. Requires compatible iPhone (iPhone 11+) and certified UWB accessory. App must be in foreground for ranging.
- **Accelerometer/Gyro/Magnetometer**: CoreMotion. Available without permission (accelerometer/gyro), magnetometer requires no special permission.
- **WiFi**: No CSI access. App cannot scan WiFi networks freely (entitlement required and heavily restricted in iOS 18+).
- **Source**: [Android UWB AOSP](https://source.android.com/docs/core/ota/modular-system/uwb)

### Android

- **Camera**: CameraX / Camera2. Permission required. Full local inference.
- **Microphone**: AudioRecord API. Permission required.
- **UWB**: `androidx.core.uwb` (Android 13+). Requires foreground app or service. Background ranging restricted. Based on FiRa specification. UWB module is modular system component.
- **Full sensor suite**: Accelerometer, gyroscope, magnetometer, barometer, proximity, ambient light, step detector — all via `SensorManager`. No special permission for most.
- **WiFi**: Limited CSI access (Android 10+ has some RSSI/scanning APIs but not full CSI).
- **Source**: [Android UWB Developer Docs](https://developer.android.com/develop/connectivity/uwb); [UWB-enabled device list](https://en.wikipedia.org/wiki/List_of_UWB-enabled_mobile_devices)

---

## Gaps and Unknowns

1. **WiFi CSI on standard consumer routers without firmware modification**: No public API exists for extracting raw CSI from consumer WiFi chipsets via standard OS APIs. This requires either (a) a dedicated ESP32/ESP8266 sensing node, (b) router firmware support (Origin/Cognitive Systems router partner), or (c) waiting for 802.11bf routers.

2. **Ring Neighbors / Citizen safety feeds**: No API access. The creator's vision of "neighbor's Ring camera" data is architecturally possible as a consent-gated pull (user connects their own Ring account) but not as passive ambient sensing of public safety events.

3. **UWB as spatial awareness on Windows/macOS**: Neither platform exposes UWB to third-party apps. iOS/Android have APIs but require foreground app. This limits UWB's utility for an always-running Submantle daemon.

4. **Matter controller complexity**: Running a full Matter controller (to read all local Matter sensors) requires implementing the Matter SDK, which is non-trivial. Home Assistant already does this — the pragmatic path is HA integration.

5. **Consent architecture for external data** (Ring consent, traffic consent, public data opt-in): No established standard exists. This is a design problem Submantle must solve — the technology is available but the consent layer has to be built from scratch.

6. **Multi-person vs. single presence disambiguation in WiFi sensing**: Current consumer solutions detect presence/motion but do not reliably distinguish between 1 person and 3 people in a room at low cost.

---

## Synthesis

### What is real and accessible today (March 2026)

| Technology | Status | Path for Submantle |
|---|---|---|
| WiFi presence sensing | Commercial (partner model) | ESP32 DIY nodes OR HA integration with CSI sensors |
| mmWave presence sensors | Consumer products, $30–70 | Matter SDK or HA REST API |
| On-device CV (YOLO26, Apple Vision) | Production-ready | Local inference, user-opt-in camera |
| On-device audio (YAMNet/TFLite) | Production-ready | 521 classes, real-time on any device |
| Matter sensor ecosystem | Mature (v1.5) | Open SDK, no vendor cooperation needed |
| Air/environment open APIs | Free and stable | OpenAQ, AirNow, Open-Meteo |
| Transit real-time data | Free and global | GTFS Realtime + Mobility Database |
| Home Assistant as fusion hub | 3M+ installs, REST API | Optional integration for power users |
| 802.11bf standard | Published Sept 2025, no hardware yet | Architect for it now, ship when hardware ships |

### Key architectural recommendation

**The outer ring should be modular and consent-first.** Each sensing capability (WiFi, camera, audio, Matter, public APIs) should be an independently enabled module. The user explicitly enables each module. No sensing happens by default.

**The pragmatic first implementation** of the outer ring is not WiFi CSI or camera vision — it is:
1. **Matter device integration** (free SDK, works with existing consumer hardware, no OS vendor cooperation)
2. **Public environmental APIs** (air quality, weather, transit — free, no hardware needed)
3. **On-device audio classification via YAMNet** (runs on any device, detects 521 event types, consent-gated microphone access)

This delivers meaningful outer-ring awareness with zero new hardware requirements for the baseline user. Advanced sensing (WiFi CSI, camera CV) is additive for users who opt in.

**The Home Assistant bridge** is the fastest path to reading WiFi sensing, mmWave presence, and dozens of other sensor types without Submantle needing to implement every protocol. HA is the de facto sensor fusion middleware that already exists in the market. Submantle integrates with it rather than competing with it.

**The privacy architecture is the hard part.** The technology is solved. Consent-gated modules, on-device inference, and explicit external data authorization (Ring account connection, traffic API opt-in) are not technically novel but must be the design foundation, not an afterthought. Academic work on interactive consent for context-aware systems (Springer 2026: doi:10.1007/s10207-026-01228-y) and federated edge intelligence frameworks confirms this is an active and solvable design space.

---

## Sources Referenced

- [Origin Wireless TruPresence](https://www.originwirelessai.com/trupresence-2/)
- [MIT Technology Review: WiFi sensing becomes usable tech](https://www.technologyreview.com/2024/02/27/1088154/wifi-sensing-tracking-movements/)
- [ABI Research: 112M WiFi sensing installations by 2030](https://www.abiresearch.com/press/north-american-wifi-sensing-cpe-installations-to-surge-to-112-million-by-2030)
- [Cognitive Systems WiFi Motion](https://www.cognitivesystems.com/wifi-motion/)
- [IEEE SA 802.11bf-2025](https://standards.ieee.org/ieee/802.11bf/11574/)
- [NIST: 802.11bf enabling widespread adoption](https://www.nist.gov/publications/ieee-80211bf-enabling-widespread-adoption-wi-fi-sensing)
- [Pulse-Fi: ESP32 heart rate via WiFi CSI](https://inrg.engineering.ucsc.edu/2025/05/30/pulse-fi-a-low-cost-system-for-accurate-heart-rate-monitoring-using-wi-fi-channel-state-information/)
- [ESPectre: WiFi CSI motion + Home Assistant](https://github.com/francescopace/espectre)
- [Ultralytics YOLO26 Docs](https://docs.ultralytics.com/models/yolo26/)
- [YOLO26 Roboflow](https://blog.roboflow.com/yolo26/)
- [arXiv YOLO Evolution overview](https://arxiv.org/html/2510.09653v2)
- [MOLO: MobileNet + YOLO hybrid](https://link.springer.com/article/10.1007/s44163-025-00398-3)
- [MS-YOLO infrared edge detection](https://arxiv.org/abs/2509.21696)
- [Apple Vision Framework](https://developer.apple.com/documentation/vision)
- [WWDC25 Vision Framework session](https://developer.apple.com/videos/play/wwdc2025/272/)
- [TFLite Audio Classification](https://www.tensorflow.org/lite/examples/audio_classification/overview)
- [Google AI Edge Model Maker audio](https://ai.google.dev/edge/litert/libraries/modify/audio_classification)
- [Home Assistant REST API](https://developers.home-assistant.io/docs/api/rest/)
- [ESPHome integration](https://www.home-assistant.io/integrations/esphome/)
- [CSA Matter 1.4 announcement](https://csa-iot.org/newsroom/matter-1-4-enables-more-capable-smart-homes/)
- [Matter Wikipedia](https://en.wikipedia.org/wiki/Matter_(standard))
- [Matter & Thread Explained 2026](https://datawiresolutions.com/blog/matter-thread-explained-2026)
- [Seeed Studio mmWave Presence Sensors 2026](https://www.seeedstudio.com/blog/2025/02/25/best-presence-sensors-for-home-assistant/)
- [SmartHomeScene Best Presence Sensors](https://smarthomescene.com/blog/best-and-worst-presence-sensors-for-home-assistant/)
- [Infineon XENSIV 60GHz radar](https://www.infineon.com/products/sensor/radar-sensors/radar-sensors-for-iot/60ghz-radar)
- [OpenAQ](https://openaq.org/)
- [AirNow](https://www.airnow.gov/)
- [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api)
- [Meersens Noise API](https://meersens.com/api/?lang=en)
- [GTFS.org](https://gtfs.org/)
- [Mobility Database](https://transitfeeds.com/)
- [511 Open Data](https://511.org/open-data)
- [Google Waze for Developers](https://developers.google.com/waze)
- [Amazon Sidewalk developer access (TechCrunch)](https://techcrunch.com/2023/03/28/amazon-opens-its-low-bandwidth-long-range-sidewalk-network-to-developers/)
- [Android UWB Developer Docs](https://developer.android.com/develop/connectivity/uwb)
- [Apple Nearby Interaction](https://developer.apple.com/documentation/nearbyinteraction)
- [Microsoft Sensor API](https://learn.microsoft.com/en-us/windows/win32/sensorsapi/portal)
- [Windows.Devices.Sensors namespace](https://learn.microsoft.com/en-us/uwp/api/windows.devices.sensors)
- [On-Device LLMs in 2026 (SiliconFlow)](https://www.siliconflow.com/articles/en/best-llms-for-edge-ai-devices-2025)
- [EKF WiFi/LiDAR/IMU fusion arXiv](https://arxiv.org/pdf/2509.23118)
- [Springer privacy consent context-aware systems 2026](https://link.springer.com/article/10.1007/s10207-026-01228-y)
