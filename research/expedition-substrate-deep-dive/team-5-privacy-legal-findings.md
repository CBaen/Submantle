# Team 5 Findings: Privacy, Consent & Legal Frameworks
## Date: 2026-03-10
## Researcher: Team Member 5

---

## Framing Note

Substrate is a **passive broker**, not an active surveillance actor. That distinction is legally load-bearing. The research below draws that line hard wherever it exists in law and precedent, because Substrate's entire defensibility rests on it.

---

## Battle-Tested Approaches

### 1. On-Device Processing as the Primary Legal Shield

**What:** Processing all awareness data locally, with no raw data ever transmitted to a server.

**Evidence:** Apple Intelligence's Private Cloud Compute architecture — end-to-end encrypted from device to validated nodes, with cryptographic guarantees that even Apple cannot access the data in transit. Apple uses this framing explicitly in regulatory submissions. The EU Digital Fairness Act public consultation (October 2025) saw Apple argue for on-device processing as a legally privileged approach to privacy.

**Source:** Apple Legal privacy governance pages; Suffolk University Journal of High Technology Law, October 2025 (Listening Closer: Data Privacy and Legal Questions in Apple's Next Generation Devices)

**Fits our case:** Substrate's VISION.md already specifies "local knowledge graph — all on-device, private." This is the right call, and it has now been validated as a legal differentiator, not just a product feature. The legal distinction between "data processed on device" vs. "data transmitted to a server" is increasingly recognized by regulators. GDPR enforcement has been softer on fully on-device systems. The EU AI Act's risk tier framework is more lenient for systems that do not process personal data at scale externally.

**Tradeoffs:** Cross-device sync (Substrate's Capability 5) breaks this shield. The moment data crosses devices over a network, GDPR, ECPA, and ePrivacy Directive protections all reactivate. The sync layer requires its own legal architecture (encrypted at rest, user-controlled keys, no server-side processing).

---

### 2. The Passive/Active Wiretap Distinction (ECPA)

**What:** US federal law (18 U.S.C. § 2511, the Wiretap Act under ECPA) distinguishes between passive monitoring — observing a communication flow without altering it — and active interception. The NIST glossary defines passive wiretapping as "monitoring or recording of data that attempts only to observe a communication flow and gain knowledge of the data it contains, but does not alter or otherwise affect that flow."

**Evidence:** This distinction is formally established in US law. The harder question is the Joffe v. Google precedent (Ninth Circuit, affirmed by Supreme Court non-certiorari): Google's Street View vehicles passively captured unencrypted WiFi traffic from public networks, and the court held this **did** violate the Wiretap Act. The 9th Circuit ruled that the "radio broadcast" exception (which would have made unencrypted WiFi freely capturable) applies only to traditional audio radio, not WiFi. Final $13M settlement approved March 18, 2020.

**Source:** Joffe v. Google, Inc. (9th Cir. 2013); NIST CSRC Glossary; Davis Wright Tremaine privacy blog; EFF analysis (September 2013)

**Fits our case:** If Substrate passively reads WiFi signal metadata (presence/absence of known SSIDs, signal strength for proximity sensing) **without intercepting packet content**, the Joffe precedent does not directly apply — Joffe was about capturing actual payload content from unencrypted packets. SSID names are broadcast identifiers, not content. However: **this is legally untested territory**. The FCC's original position (that unencrypted WiFi was freely capturable) was rejected by the courts. Substrate should not rely on WiFi content sensing at all and should limit WiFi awareness to signal-strength-only proximity detection from the user's own device.

**Tradeoffs:** WiFi sensing limited to the user's own network interface, reading only SSID names (public broadcast identifiers), avoids Joffe exposure. Any deeper packet inspection is categorically off the table under current US law.

---

### 3. EU GDPR + ePrivacy Directive — WiFi MAC Address = Personal Data

**What:** The EU Data Protection Board (EDPB) has definitively ruled that MAC addresses used in WiFi tracking are personal data under GDPR, even in hashed form. The Dutch DPA (2018) required strict conditions for WiFi visitor counting in semi-public spaces.

**Evidence:** EDPB Guidelines 2/2023 on Technical Scope of Article 5(3) ePrivacy Directive — expanded the definition of "terminal equipment" and "information storage" to cover many passive tracking methods. Article 5(3) requires prior consent before storing or accessing information from a user's device.

**Source:** EDPB 2023 Guidelines; TechGDPR blog analysis; Privacy Company EU blog on GDPR WiFi tracking

**Fits our case:** In the EU, Substrate cannot passively read MAC addresses from neighboring devices without consent. The ePrivacy Directive's proposed replacement regulation was **withdrawn by the European Commission on February 11, 2025** — the current Directive remains in force, meaning this requirement is not going away. Substrate's EU deployment must either (a) limit WiFi awareness to the user's own device only, or (b) obtain explicit consent from every detected device owner — which is architecturally impractical. **Practical conclusion: WiFi sensing of third-party devices is legally non-viable in the EU without a radically different architecture.**

**Tradeoffs:** This creates a meaningful US/EU compliance divergence. WiFi proximity sensing of the user's own device is fine in both jurisdictions. Sensing neighboring devices is legally problematic in the EU and legally uncertain in the US.

---

### 4. Two-Party Consent States — Scope and Applicability

**What:** 13 US states require all-party consent for recording: California, Connecticut, Delaware, Florida, Illinois, Maryland, Massachusetts, Michigan, Montana, Nevada, New Hampshire, Pennsylvania, and Washington. These laws apply to "conversations" — the question is whether ambient environmental sensing (WiFi signals, camera presence detection) constitutes a "conversation" under these statutes.

**Evidence:** Current state-by-state survey from Recording Law (2026 Guide) and Justia 50-state survey. The laws were written for audio recording; their application to RF signal sensing is not litigated.

**Source:** Two-Party Consent States (2026 Guide), recordinglaw.com; Justia 50-State Survey

**Fits our case:** Two-party consent laws almost certainly do not apply to Substrate's core capabilities (process awareness, workflow graphing, OS-level monitoring of the user's own machine). They become relevant only if Substrate ever records audio (microphone-based awareness). The framing of "passive environmental sensing" — reading WiFi signal presence, not recording conversations — is outside the scope of wiretap law as traditionally applied. **This is a low risk area for Substrate's defined capabilities, but audio sensing must be explicitly excluded from the product.**

**Tradeoffs:** If Substrate ever adds microphone-based ambient awareness (detecting whether a user is in a meeting, for example), all-party consent law activates in 13 states. Keep audio explicitly out of scope.

---

### 5. Municipal Open Data — Legal Access Framework

**What:** The US OPEN Government Data Act (2018, Title II of the Foundations for Evidence-Based Policymaking Act) requires federal agencies to publish data as open, machine-readable formats. Many cities have extended this principle. Traffic camera feeds are available via public API in Washington DC (opendata.dc.gov), New York (511ny.org), Utah (UDOT), and through commercial aggregators.

**Evidence:** TrafficLand provides live video from 25,000+ cameras across 200+ cities under redistribution agreements with 50+ Departments of Transportation, making it the largest authorized aggregator of live US traffic video. DC Open Data explicitly offers a REST API. The EU Open Data Directive (2019/1024, transposed by July 2021) requires member states to make high-value datasets (including real-time transport data) available via APIs free of charge. The first high-value dataset reporting exercise occurred in 2025.

**Source:** opendata.dc.gov; 511ny.org developer docs; TrafficVision.Live blog; EU Digital Strategy open data pages; EUR-Lex Directive 2019/1024; OPEN Government Data Act, 115th Congress

**Fits our case:** Accessing publicly published municipal traffic camera APIs is legally clean. These are intentionally public data streams. Accessing them via authorized aggregators (TrafficLand model) provides additional legal cover through intermediary licensing agreements. **The key legal principle: public sector data published under open data mandates carries an implicit license for reuse.** Under the US OPEN Government Data Act, government data not under an explicit license is in the worldwide public domain.

**Tradeoffs:** API terms vary by municipality — some require attribution, some restrict commercial use, some restrict real-time redistribution. Substrate needs per-source ToS review before using any camera feed. Real-time data vs. archived data may face different treatment (real-time is typically more permissive in terms of ToS but more sensitive in privacy terms).

---

## Novel Approaches

### 6. Data Trusts as Consent Infrastructure

**What:** A data trust is a legal entity that holds data rights on behalf of a group of people, acting as a fiduciary. Rather than each user individually consenting to each data sharing arrangement, the trust negotiates terms collectively. Individual users grant the trust limited authority to make consent decisions on their behalf within defined parameters.

**Why interesting:** Substrate's boldest feature — awareness extending to neighboring devices (Ring doorbells, traffic cameras, WiFi signals) — creates a multi-stakeholder consent problem that individual OAuth-style permission grants cannot solve. A data trust structure could, in theory, represent an entire neighborhood's consent posture for local infrastructure data.

**Evidence:** The data trust concept has gained traction in academic and policy circles. Smart contract-based consent management — immutable, dynamically updatable, blockchain-anchored — has been proposed in the healthcare federated learning context (PMC, 2025). The concept allows patient-level preferences to propagate automatically through data-sharing networks.

**Source:** SecurePrivacy.ai blog on federated learning consent crisis; PMC article on patient-centric federated learning with smart contracts (2025); MDPI IoT consent reference design model

**Fits our case:** A data trust for "neighborhood infrastructure data" could enable Substrate to access Ring video feeds and municipal sensors with collective rather than individual consent. This is architecturally elegant but legally immature. No jurisdiction has fully codified data trusts with binding consent delegation authority for IoT data. The UK has been most progressive here (Ada Lovelace Institute work on data trusts), but implementation is limited to voluntary pilots.

**Risks:** Legal recognition is jurisdiction-dependent and currently voluntary. Cannot override individual data subject rights under GDPR (right to erasure still applies). Smart contract implementation creates immutability that may conflict with GDPR's Article 17 right to erasure — once data contributes to a model or decision, unwinding that contribution is mathematically complex.

---

### 7. Differential Privacy as a Legal Argument, Not Just a Technical Tool

**What:** Differential privacy adds mathematically calibrated noise to individual data points before aggregation, making it cryptographically infeasible to re-identify any individual from the aggregate output. Apple uses differential privacy in iOS and explicitly argues it creates a legal/regulatory boundary — data processed with differential privacy is not "personal data" in any actionable sense.

**Why interesting:** If Substrate's awareness outputs (the signals it provides to AI agents) are differentially private aggregations rather than raw data, those outputs may fall outside GDPR's definition of personal data entirely. This reframes Substrate's outputs as statistical summaries rather than personal information.

**Evidence:** Apple's differential privacy overview (apple.com/privacy/docs); Apple's active advocacy for differential privacy as a privacy-preserving method in the EU Digital Fairness Act consultation (October 2025); Nature Scientific Reports paper on quantum-resilient privacy-preserving AI (2025).

**Source:** Apple Machine Learning Research; Apple Legal Privacy Governance; Nature Scientific Reports 2025

**Fits our case:** Substrate provides contextual signals to agents ("12 Node processes are running; 2 are yours"), not raw personal data. Framing outputs as differentially private summaries — even where the underlying sensing touches personal data — could create a defensible legal position that Substrate's API outputs are not themselves personal data under GDPR or CCPA.

**Risks:** No regulator has formally accepted differential privacy as a complete personal data exemption. It is an argument, not a settled legal shield. The underlying collection still requires justification even if outputs are anonymized.

---

### 8. The AirTag Unwanted-Tracking Architecture as a Consent Model Template

**What:** Apple's AirTag implements a specific consent architecture for third-party detection: Bluetooth identifiers rotate every 15 minutes (when in range of owner) to prevent passive tracking, but slow to every 24 hours when out of range — deliberately enabling detection of "tags moving with a non-owner." The system is designed so that victims of stalking can detect unwanted tracking even while protecting legitimate owner privacy. Apple, Tile, Samsung, and Google jointly submitted an industry specification to standardize cross-platform unwanted tracking detection.

**Why interesting for Substrate:** This is a real-world implementation of a three-way consent architecture: (1) the owner's privacy is protected from passive scanning; (2) the non-owner's right to know they're being tracked is preserved; (3) law enforcement can request identifying information about the tag owner. This tripartite structure — user consent, third-party detection rights, and legal override — is a template for how Substrate could structure awareness of neighboring smart devices.

**Evidence:** Apple Newsroom (February 2022 AirTag update); Google/Apple joint industry specification submission; Hackster.io on public-key cryptography for stalker detection.

**Source:** Apple Newsroom; Hackster.io; NordVPN AirTag stalking explainer (2025)

**Fits our case:** When Substrate senses a neighboring Ring doorbell or Bluetooth device, it should implement an analogous architecture: (1) the neighboring device owner's data is not retained; (2) the user is informed what Substrate can and cannot sense from neighbors; (3) a detection/disclosure mechanism exists. The AirTag architecture proves this three-way balance is technically achievable.

**Risks:** AirTag's architecture required Apple's control over the Bluetooth stack across hundreds of millions of devices. Substrate does not have that platform control. Replicating this architecture requires cooperation from device manufacturers or working at the OS level — which is exactly where Substrate lives.

---

## Emerging Approaches

### 9. Federated Learning as Privacy Architecture for Cross-Device Awareness

**What:** Substrate's Capability 5 (Cross-Device Sync) could be architecturally redesigned as federated learning: each device maintains its own local awareness model, and only aggregated updates (not raw data) are shared. This means that the user's awareness profile never exists in complete form on any single server.

**Momentum:** Federated learning has moved from research to production deployment in healthcare, finance, and device manufacturers. The Frontiers in Drug Safety and Regulation journal (2025) published a regulatory-approved federated learning framework. GDPR-compliant federated architectures are now actively litigated as defensible, with blockchain audit trails providing Article 5 accountability.

**Source:** Frontiers in Drug Safety and Regulation (2025); SecurePrivacy.ai federated learning consent paper; ACM Computing Surveys on federated learning and privacy-preserving computation

**Fits our case:** Substrate's cross-device sync is its highest privacy-risk capability. Redesigning it as federated — where only model updates, not raw awareness states, cross the network — would make it architecturally analogous to Apple's on-device intelligence while enabling the sync capability. Each device's awareness model improves from the aggregate without raw data ever leaving any device.

**Maturity risk:** GDPR Article 17 (right to erasure) creates a genuine technical problem: once a data point contributes to a federated model update, removing its influence requires reconstructing the training process. This is an active research problem without a production-ready solution as of March 2026.

---

### 10. EU AI Act Classification — Substrate's Risk Tier

**What:** The EU AI Act is fully applicable August 2, 2026. General-purpose AI model obligations have been in effect since August 2, 2025. High-risk AI system obligations for systems embedded in regulated products have an extended deadline to August 2027. The Commission was required to publish classification guidelines by February 2, 2026 — those guidelines are either just published or imminent as of this research date.

**Current classification picture:** High-risk systems include "AI safety components in critical infrastructure" and systems used in safety-critical sectors. Substrate's self-description as a "safety layer" — preventing agents from taking destructive actions — may be read as an AI safety component, which would place it in the high-risk tier. High-risk systems require: conformity assessments, CE marking, quality management systems, human oversight mechanisms, and EU database registration.

**Evidence:** EU AI Act Article 6 classification rules; Legalnodes.com 2026 compliance guide; ComplianceAndRisks.com AI governance guide for 2026; artificialintelligenceact.eu implementation timeline.

**Source:** EU AI Act official text; artificialintelligenceact.eu; legalnodes.com; complianceandrisks.com

**Fits our case:** Substrate should proactively seek a legal opinion on whether it qualifies as a "safety component" under Annex III. If it does, the August 2026 compliance deadline is live now for EU market entry. If it is classified as "limited risk" (a system with transparency obligations but no conformity assessment), the compliance burden is dramatically lower.

**Maturity risk:** The February 2026 Commission classification guidelines are the key document. Until those guidelines are published and interpreted by counsel, Substrate's EU AI Act tier is genuinely uncertain.

---

### 11. Ring Neighbors / Citizen App — Legal Access Status

**What:** Amazon Ring has no public Neighbors API. Third-party access to Ring Neighbors content requires a formal partnership with Ring's developer program, including a Third Party Security Assessment. There is an unofficial npm package (ring-client-api on GitHub) but using it would violate Ring's Terms of Service and potentially constitute unauthorized computer access under the CFAA.

The Citizen app (formerly Vigilante) monitors 911 radio communications and generates location-based alerts. In April 2025, Axon announced integration of Citizen with its Fusus real-time crime-center platform, allowing law enforcement to view live Citizen videos. NYC Mayor's Office officially partnered with Citizen in 2025. **Citizen does not offer a public API for third-party integration.**

Nextdoor offers a "Neighborhoods" API for verified agencies and limited developer partners, but not for general third-party applications.

**Source:** Ring Developer (developer.amazon.com/ring); Ring Community forum on Ring Doorbell APIs; CNN Business/Axon-Citizen integration news (2025); NBC News on Citizen pushing surveillance boundaries

**Fits our case:** Substrate cannot legally access Ring Neighbors, Citizen, or Nextdoor safety data without formal partnership agreements with each platform. These are walled gardens with intentional API restrictions. The viable path is not technical access but rather a consent-mediated delegation: users who choose to share Ring/Citizen/Nextdoor data with Substrate grant that permission explicitly within each platform's authorized integration program. Substrate would need to become an authorized Ring developer partner and a Nextdoor agency partner — that is a business development requirement, not a technical one.

**Maturity risk:** Amazon canceled its Ring-Flock Safety partnership in February 2026 specifically due to privacy concerns and ICE-related controversy. The political and regulatory environment around Ring data sharing is actively hostile. Any Substrate-Ring integration would face significant scrutiny.

---

## Gaps and Unknowns

### Legal Gaps

1. **WiFi signal sensing — no settled US law.** The Joffe/Google decision covers payload content capture from unencrypted networks. SSID-only sensing (no payload) has not been litigated. This is Substrate's largest legal grey zone in the US.

2. **EU AI Act classification — pending February 2026 guidelines.** Substrate's risk tier under the AI Act is uncertain until the Commission publishes its practical classification examples. Legal counsel review is required before EU market entry.

3. **Cross-device sync and GDPR data transfer.** Even user-to-user-device syncing crosses jurisdictional lines. If a US user syncs awareness from their phone (in the US) to their laptop (also in the US but with EU-resident data) the rules are unclear. GDPR's extraterritorial scope (Article 3) applies to any processing of EU residents' data regardless of where processing occurs.

4. **AI agent liability chain.** When Substrate tells an agent "it's safe to delete these processes" and the agent destroys something valuable — the liability chain runs: Substrate developer → agent developer → deploying user. No US court has ruled on middleware liability in an AI agent chain. The EU's revised Product Liability Directive (March 2024) may apply, but it has not been interpreted against context-broker products.

5. **Municipal camera API terms — per-source variability.** Every municipal camera feed has different ToS. No single legal clearance covers all municipalities. Substrate would need a systematic ToS review process before enabling any specific camera feed.

### Architectural Unknowns

6. **Federated learning and GDPR Article 17 erasure.** No production-ready solution exists for right-to-erasure in federated models as of March 2026. If Substrate's cross-device sync uses federated learning, it may be structurally non-compliant with GDPR's erasure rights.

7. **How to handle "incidental capture" of third-party data.** Even with pure on-device processing, Substrate's WiFi sensing will detect devices belonging to people other than the user (neighbors' phones, IoT devices). The legal status of detecting-but-not-retaining third-party device presence is untested.

---

## Synthesis

### The Legal Architecture Substrate Must Build

Substrate's defensibility rests on four structural commitments:

**1. On-device by default, cross-device by explicit user choice.**
On-device processing is the strongest legal shield available across all jurisdictions. The moment data crosses the device boundary, GDPR, ECPA, ePrivacy, and state wiretap laws all activate. Cross-device sync must be architecturally isolated as an opt-in module with its own consent flow, its own encryption model, and its own legal disclosure.

**2. No payload sensing, ever.**
The Joffe v. Google precedent draws a hard line: capturing actual content from wireless networks violates the Wiretap Act even when networks are unencrypted. Substrate must categorically exclude any functionality that reads packet content from any wireless signal. WiFi awareness must be limited to: (a) the user's own network interfaces; (b) SSID presence/absence (public broadcast identifiers); (c) signal strength for proximity inference. Nothing more.

**3. Neighbor/third-party device awareness requires explicit, granular consent.**
Any capability that senses devices not owned by the user — Ring doorbells, neighbors' WiFi, Bluetooth beacons — must be gated behind an explicit, specific consent flow. The AirTag architecture provides the right model: the sensing is disclosed, the user controls it, third parties have a detection/disclosure right. Substrate must implement this tripartite consent architecture for any cross-device/cross-owner sensing.

**4. Public data sources require documented ToS review, not just technical access.**
Municipal camera feeds, public transit APIs, and open government datasets are legally accessible but require per-source review. Substrate needs a data source registry — a list of approved sources, each with ToS review status, attribution requirements, and jurisdictional notes. The TrafficLand aggregator model (licensed redistribution agreements with 50+ DOTs) is the right commercial shortcut for traffic camera data in the US.

### The EU AI Act Risk — Act Now

Substrate describes itself as a "safety layer" that prevents destructive AI actions. That language may trigger high-risk classification under the EU AI Act's "AI safety components" category, with August 2026 as the compliance deadline. Given that Substrate was founded on March 10, 2026 — exactly 5 months before that deadline — EU legal counsel review of the Act's classification rules should happen in the first 90 days of the company's existence. Missing the August 2026 deadline would bar EU market entry.

### The Strongest Privacy Position Available

Substrate does not need to be defensively private — it can be offensively private. Apple's trajectory proves that privacy architecture marketed as a feature creates regulatory goodwill, user trust, and competitive differentiation simultaneously. Substrate should:

- Publish its privacy architecture publicly and in plain language
- Apply differential privacy to all awareness outputs exposed to AI agents
- Build consent flows that are granular, revocable, and auditable
- Position on-device-by-default as a product promise, not just a compliance checkbox
- Seek early engagement with the FTC (US), ICO (UK), and a lead GDPR supervisory authority (EU) to establish a cooperative regulatory relationship before any enforcement action becomes possible

The companies that get in front of regulators and demonstrate genuine privacy-first architecture receive dramatically more favorable treatment than those that encounter regulators reactively.

---

*Sources consulted:*
- [ECPA — EPIC](https://epic.org/ecpa/)
- [Joffe v. Google — EPIC documents](https://epic.org/documents/ben-joffe-v-google/)
- [Joffe v. Google — Wikipedia](https://en.wikipedia.org/wiki/Joffe_v._Google,_Inc.)
- [Google Street View Settlement — Davis Wright Tremaine](https://www.dwt.com/blogs/privacy--security-law-blog/2019/08/google-street-view-lawsuit-settled)
- [EFF analysis of Joffe v. Google](https://www.eff.org/deeplinks/2013/09/what-google-street-view-decision-means-researchers-and-cops)
- [EDPB ePrivacy Directive tracking guidance](https://www.edpb.europa.eu/news/news/2023/edpb-provides-clarity-on-tracking-techniques-covered-eprivacy-directive_en)
- [ePrivacy Directive EU Digital Omnibus 2025](https://www.kennedyslaw.com/en/thought-leadership/article/2026/the-2025-european-commission-eu-digital-omnibus-package-the-e-privacy-directive/)
- [GDPR and IoT — legalitgroup.com](https://legalitgroup.com/en/gdpr-and-internet-of-things-iot/)
- [WiFi Tracking and GDPR — TechGDPR](https://techgdpr.com/blog/wifi-tracking-retail-analytics-gdpr/)
- [EU AI Act official page](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)
- [EU AI Act 2026 compliance guide — Legalnodes](https://www.legalnodes.com/article/eu-ai-act-2026-updates-compliance-requirements-and-business-risks)
- [EU AI Act implementation timeline — artificialintelligenceact.eu](https://artificialintelligenceact.eu/implementation-timeline/)
- [EU Open Data Directive — EUR-Lex](https://eur-lex.europa.eu/EN/legal-content/summary/open-data-and-the-reuse-of-public-sector-information.html)
- [EU Data Act — Skadden](https://www.skadden.com/insights/publications/2025/06/eu-data-act)
- [OPEN Government Data Act — Congress.gov](https://www.congress.gov/crs-product/IF12299)
- [DC Open Data traffic cameras](https://opendata.dc.gov/datasets/DCGIS::traffic-camera/api)
- [TrafficVision.Live on embedding traffic cameras](https://trafficvision.live/blog/embedding-traffic-cameras-city-hoa-websites)
- [Ring Terms of Service](https://ring.com/terms)
- [Ring community forum — API discussions](https://community.ring.com/t/ring-doorbell-apis/159495)
- [Ring-Flock partnership cancellation — CNN](https://www.cnn.com/2026/02/13/tech/amazon-ring-flock-partnership-ice)
- [Citizen app — Wikipedia](https://en.wikipedia.org/wiki/Citizen_(app))
- [NYC Mayor Office Citizen app partnership 2025](https://www.nyc.gov/mayors-office/news/2025/07/-mayor-adams-expands-public-safety-communications-with--nyc-publ)
- [Citizen app surveillance concerns — NBC News](https://www.nbcnews.com/tech/tech-news/citizen-public-safety-app-pushing-surveillance-boundaries-rcna1058)
- [Apple on-device intelligence privacy — Apple Legal](https://www.apple.com/legal/privacy/data/en/intelligence-engine/)
- [Apple differential privacy overview](https://www.apple.com/privacy/docs/Differential_Privacy_Overview.pdf)
- [Apple Intelligence privacy — Suffolk University JHTL 2025](https://sites.suffolk.edu/jhtl/2025/10/16/listening-closer-data-privacy-and-legal-questions-in-apples-next-generation-devices/)
- [AirTag unwanted tracking update — Apple Newsroom](https://www.apple.com/newsroom/2022/02/an-update-on-airtag-and-unwanted-tracking/)
- [AirTag detection — Help Net Security 2025](https://www.helpnetsecurity.com/2025/02/11/apple-airtags-tracking-detect-disable/)
- [Agentic AI liability — Squire Patton Boggs](https://www.squirepattonboggs.com/insights/publications/the-agentic-ai-revolution-managing-legal-risks/)
- [AI agent liability framework — hungyichen.com](https://www.hungyichen.com/en/insights/ai-agent-liability-framework)
- [Federated learning consent crisis — SecurePrivacy.ai](https://secureprivacy.ai/blog/consent-orchestration-federated-learning)
- [Patient-centric federated learning smart contracts — PMC 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12046574/)
- [Two-party consent states 2026 — recordinglaw.com](https://recordinglaw.com/party-two-party-consent-states/)
- [Life360 lawsuit guide 2026 — lawrift.com](https://lawrift.com/life360-lawsuit/)
- [App Tracking Transparency — Apple Developer](https://developer.apple.com/documentation/apptrackingtransparency)
