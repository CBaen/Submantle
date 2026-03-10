# Team 3 Findings: Behavioral Trust Science — The Math of Reputation That Can't Be Gamed
## Date: 2026-03-10
## Researcher: Team Member 3

---

## Preamble: What the Codebase Already Has

Before presenting external findings, the existing schema deserves precise mapping:

| Schema Field | Trust Signal | Role |
|---|---|---|
| `registration_time` | TEMPORAL — origin anchor | When did this agent first appear? |
| `last_seen` | TEMPORAL — recency | Is the agent still active? |
| `total_queries` | BEHAVIORAL — activity volume | How much has it done? |
| `incidents` | OPERATIONAL — failure rate | How often does it break trust? |
| `trust_metadata` (JSON, empty) | Reserved | Ready to hold multi-dimensional scores |
| `capabilities` (JSON array) | Context anchor | What domains does this agent operate in? |

The Beta Reputation System formula `trust = alpha / (alpha + beta)` where `alpha = total_queries` and `beta = incidents` is already the right choice for the single-score case. The research below either confirms this, extends it for multi-dimensional use, or addresses the surrounding infrastructure the formula alone cannot handle.

---

## 1. Reputation Algorithms Beyond Beta

### Battle-Tested Approaches

**Beta Reputation System (Jøsang 2002)**
- **What:** Models trust as a Beta probability distribution over binary outcomes (success/failure). Score = alpha / (alpha + beta).
- **Evidence:** Used in production in MANETs, P2P systems, IoT trust frameworks, and the MIDGE system studied in the Mae expedition. Validated in the mae-principles synthesis as the right algorithm for Substrate.
- **Source:** Jøsang & Ismail (2002). Confirmed current: ScienceDirect, Springer (accessed March 2026). DOI: 10.1007/978-3-540-74810-6_8
- **Fits our case because:** Maps exactly to `total_queries` (alpha) and `incidents` (beta). O(1) computation. No dependencies. Already confirmed by previous expedition.
- **Tradeoffs:** Single-dimensional. Does not distinguish trust by capability domain without extension. Does not weight recency without a decay mechanism layered on top.

**PeerTrust (Xiong & Liu, 2004)**
- **What:** Multi-factor trust formula incorporating transaction satisfaction, feedback credibility, transaction context weight, and community context factor.
- **Evidence:** Extensively studied in the P2P and e-commerce literature. A 2024 multi-agent manufacturing study compared PeerTrust, EigenTrust, PageRank, PowerTrust, and Time-decay — PeerTrust achieved the strongest alignment between price and quality while resisting monopolistic dominance. A hybrid Beta-PT combining PeerTrust and Bayesian-beta outperformed all single algorithms.
- **Source:** Arxiv 2511.19930, "Designing Reputation Systems for Manufacturing Data Trading Markets," November 2025 (accessed March 2026). Original algorithm: IEEE TKDE 2004.
- **Fits our case because:** PeerTrust's transaction context factor is the seed of context-dependent trust (see Section 3). Substrate's `capabilities` array is a natural context axis.
- **Tradeoffs:** More complex than Beta. Requires feedback credibility weights — Substrate currently has no mechanism for weighting the source of an incident report.

**EigenTrust (Kamvar, Schlosser, Garcia-Molina — Stanford, 2003)**
- **What:** Computes global trust scores via power iteration over a peer-trust matrix, producing a single eigenvector of reputation values.
- **Evidence:** Foundational P2P reputation algorithm. HonestPeer and EERP enhancements published through 2023. Used in OpenRank (open-source trust graph infrastructure). Fast convergence: < 10 iterations for 1,000 nodes.
- **Source:** Stanford NLP (nlp.stanford.edu/pubs/eigentrust.pdf), OpenRank documentation (docs.openrank.com, accessed March 2026).
- **Fits our case because:** Trust propagation across agent-to-agent relationships could be a V2+ capability — when Agent A vouches for Agent B, EigenTrust can propagate that endorsement.
- **Tradeoffs:** Requires a network graph of trust relationships to exist. Not applicable to isolated agents (Substrate's current model). Relies on a set of pre-trusted seed nodes — centralization risk. Does not scale to internet-scale (billions of nodes) using naive power iteration — the matrix becomes intractable. Fundamentally designed for distributed P2P, not centralized infrastructure. **Not recommended for V1 or V2 Substrate.** V3+ if agent networks emerge.

**PageRank-Style Trust Propagation**
- **What:** Treats trust relationships as a directed graph and applies random-walk probability to compute global authority scores.
- **Evidence:** Same 2024/2025 manufacturing study found PageRank exhibited the smallest slope — provider dominance decoupled price from quality. PageRank-style systems allow dominant agents to accumulate disproportionate trust without behavioral justification.
- **Source:** Arxiv 2511.19930 (accessed March 2026).
- **Fits our case because:** It doesn't. Substrate's design is behavioral, not positional. An agent with many connections should not automatically outrank one with fewer connections but better behavior.
- **Tradeoffs:** Gameable by structural position rather than behavioral quality. Not recommended.

### Novel Approaches

**Subjective Logic (Jøsang — same author as Beta)**
- **What:** Extends Beta distributions to a full algebra for reasoning under uncertainty, with operators for trust discounting (chaining) and consensus fusion (combining independent opinions).
- **Why it's interesting:** The discounting operator enables "I trust Agent A, and Agent A trusts Agent B — how much should I trust Agent B?" This is the mathematical foundation of transitive trust.
- **Evidence:** A 2024 publication (Springer, "Trust Level Evaluation Engine for Dynamic Trust Assessment with Reference to Subjective Logic") confirms active research. InterTrust (a cloud trust system) demonstrated low execution time and high scalability using subjective logic.
- **Source:** Springer link.springer.com/chapter/10.1007/978-3-031-76714-2_3 (2024, accessed March 2026). Earlier cloud implementation: Journal of Supercomputing 2018.
- **Fits our case because:** When Substrate builds agent-to-agent delegation chains (Agent A delegates to Agent B which delegates to Agent C), subjective logic's discounting operator computes the end-to-end trust precisely. The Beta distribution is a special case of subjective logic — Substrate can start with Beta and upgrade to full subjective logic without breaking backward compatibility.
- **Risks:** Algebraic overhead compared to simple Beta. The consensus fusion operator is only needed when multiple independent attestations exist — Substrate currently has one attestation source (itself). Premature to implement now.

**Synthesis: Best Algorithm Path for Substrate**

| Phase | Algorithm | Reason |
|---|---|---|
| V1 | Beta Reputation System | Already in schema. O(1). No new infrastructure. |
| V2 | Beta per capability domain | Extend `trust_metadata` JSON with per-capability alpha/beta pairs. |
| V3 | Hybrid Beta-PT | Add transaction context weights when MCP integration creates multi-domain query data. |
| V4+ | Subjective Logic discounting | When agent delegation chains exist and transitive trust needs computing. |

---

## 2. Trust Decay Models

### Battle-Tested Approaches

**Exponential Decay with Half-Life Parameter**
- **What:** Weight each historical interaction by e^(-λt) where t is the time elapsed since the interaction and λ is the decay constant. The half-life H = ln(2)/λ defines "how long until an interaction's weight halves."
- **Evidence:** Analysis of the exponential decay principle in probabilistic trust models (ScienceDirect, originally published in Theoretical Computer Science). A half-life decaying model for recommender systems demonstrated improved accuracy. FICO Score 10T uses a 24-month behavioral window with recency weighting, showing the industry consensus around recency-biased scoring.
- **Source:** ScienceDirect (pii/S0304397509004034, accessed March 2026). FICO Score 10T methodology: myFICO.com (accessed March 2026).
- **Fits our case because:** A sliding window or hard cutoff (e.g., ignore incidents older than 90 days) loses all history abruptly. Exponential decay preserves the full history while naturally emphasizing recent behavior. A single parameter (half-life) is tunable without algorithm replacement.
- **Tradeoffs:** Must choose the half-life. Wrong choice means either: scores are too sticky (old bad behavior dominates unfairly) or too volatile (recent blip erases earned trust). No universal optimal value — must be tuned empirically.

**Sliding Window with Recency Bands**
- **What:** Divide history into time bands (e.g., last 30 days, 31–90 days, 91–365 days) and apply different weights to each band.
- **Evidence:** FICO uses a qualitative version of this — recent payment history has higher weight than older history. Research on concept drift in reputation assessment (AAMAS 2018) found sliding windows effective for gradual behavioral change but poor at sudden change.
- **Source:** FICO algorithmic methodology documentation (fico.com, accessed March 2026). AAMAS 2018 proceedings (ifaamas.org, accessed March 2026).
- **Fits our case because:** Simpler to implement than exponential decay, more auditable ("this incident was in the 30-day high-weight band"), and maps naturally to human intuition about recency.
- **Tradeoffs:** Cliff effects at band boundaries — an incident on day 30 versus day 31 produces a sudden score jump. Choosing band sizes requires domain expertise Substrate doesn't yet have.

### Key Findings on Decay Parameters

Research from multiple sources converged on these findings:
1. The optimal forgetting rate varies by context. There is no universal value. Substrate should treat the half-life as a tunable constant, not a hardcoded number.
2. Forgetting factors handle gradual behavioral change well but poorly handle sudden changes (an agent that was good then goes rogue). A step-function component (detecting sudden incident spikes) complements exponential decay.
3. The FICO 7-year window is a legal artifact (Fair Credit Reporting Act), not a mathematical optimum. Agent behavior in a software ecosystem evolves on a timescale of weeks to months — a 12-month effective window (with exponential decay) is a reasonable starting hypothesis.

**Recommended Implementation for Substrate V1:**
Do not decay yet. The Beta Reputation System's `alpha / (alpha + beta)` formula is already insensitive to time because it accumulates counts — a recent incident is treated identically to an old one. This is a known limitation, not a bug to fix in V1 when the database has zero baseline data. Implement decay in V2 after observing real query and incident distributions.

**Recommended V2 decay design:**
- Apply an exponential time-weight to each incident and each query: effective_alpha = sum(e^(-λ * age_of_query)), effective_beta = sum(e^(-λ * age_of_incident))
- Start with half-life = 30 days. Tune after 90 days of real data.
- This requires storing timestamps per query and per incident, not just cumulative counts. The schema migration from `total_queries INTEGER` to a time-series format is the key architectural commitment.

---

## 3. Context-Dependent Trust

### Battle-Tested Approaches

**Capability-Scoped Trust Scores (Multi-Dimensional Beta)**
- **What:** Maintain separate alpha/beta pairs per capability domain. Trust(file_operations) is independent of Trust(network_access).
- **Evidence:** PeerTrust's transaction context factor formalizes this. The mae-principles expedition synthesis listed "per-capability Beta distributions" as a valid V2 extension, correctly deferred from V1. A 2025 inter-agent trust model study (arxiv 2511.03434) confirmed that capability-scoped trust is necessary for safe agent delegation in production multi-agent systems.
- **Source:** Arxiv 2511.03434 "Inter-Agent Trust Models: A Comparative Study," November 2025 (accessed March 2026). Mae-principles synthesis (confirmed).
- **Fits our case because:** Substrate's `capabilities` JSON array is already the natural partition axis. An agent registering `["file_read", "process_query"]` should build trust independently in each domain. A file-reading agent that never makes network calls has zero evidence of network trustworthiness — treating them as trusted for network access because they're trusted for file reads is the classic capability confusion attack.
- **Tradeoffs:** Requires separate incident tracking per capability. The `increment_agent_incidents()` method must accept a capability parameter. Schema migration required.

**Trust Composition Across Domains**
- **What:** When an action spans multiple capabilities, compose the per-capability scores (typically: take the minimum, weighted harmonic mean, or product).
- **Evidence:** The "weakest link" principle (minimum composition) is standard in security. NIST SP 800-207 (Zero Trust Architecture) explicitly uses least-privilege and capability-scoped access tokens, not aggregate trust scores.
- **Source:** NIST SP 800-207 (Zero Trust Architecture). Confirmed applicable by "Action Restrictions and Permissions: Controlling What Your AI Agent Can Do," mbrenndoerfer.com (2025, accessed March 2026).
- **Fits our case because:** A query spanning both file_read and network_access should require trust in BOTH domains. Minimum composition is the conservative correct choice.
- **Tradeoffs:** Minimum composition penalizes specialists (high in one domain, low in another) even when the action only uses the high domain. The capability-specific gate should only apply to the capabilities actually exercised by a given query.

**WebAssembly-Inspired Capability Tokens**
- **What:** Issue explicit unforgeable capability tokens per resource type. An agent receives a `file_read_cap` token and a `process_query_cap` token. Each token carries its own trust context.
- **Evidence:** WebAssembly's capability-based security model is described as "mathematically verifiable sandboxing" in production AI agent security documentation (northflank.com, 2026, accessed March 2026). ARIA (Agent Relationship-based Identity and Authorization) formalizes delegation relationships as cryptographically verifiable graph edges.
- **Source:** Northflank, "How to sandbox AI agents in 2026" (accessed March 2026). Arxiv 2510.21236, "Securing AI Agent Execution" (2025, accessed March 2026).
- **Fits our case because:** Substrate already issues HMAC tokens per agent. Extending to per-capability tokens is a natural evolution. A capability token could encode the current trust score for that capability domain, enabling Substrate to pass trust context to downstream systems.
- **Risks:** More tokens to manage, more token validation overhead. V2+ consideration after capability-scoped trust scores are proven.

---

## 4. Sybil Resistance

### The Fundamental Constraint

Substrate's open access design ("agents don't have to identify themselves") creates a genuine Sybil problem: nothing prevents an attacker from registering 1,000 anonymous agents and having them query each other to build fake trust. This constraint is not a mistake — it is Guiding Light's explicit design choice. The research below identifies what's achievable within it.

### Key Finding: The Trilemma

Research across multiple sources confirmed a hard trilemma: **Open Access + Privacy + Strong Sybil Resistance cannot all be simultaneously achieved.** You must sacrifice one. Substrate has chosen to sacrifice Strong Sybil Resistance in favor of Open Access + Privacy. The question is how to minimize the damage from that sacrifice.

### Battle-Tested Approaches

**Velocity Limits and Rate Throttling**
- **What:** Limit the rate at which any single agent (or IP/device/fingerprint cluster) can accumulate trust signals. Cap queries-per-hour, queries-per-day, maximum trust gain per time window.
- **Evidence:** Standard in fraud detection. iGaming platforms detect "accounts with identical behavioral profiles" and "immediate bonus use with no signs of regular gameplay" — both are velocity anomalies. SEON and similar platforms detect Sybil networks via device fingerprinting and behavioral clustering.
- **Source:** SEON iGaming fraud prevention guide (seon.io, accessed March 2026). AU10TIX "Top Fraud Trends 2025-2026" (au10tix.com, accessed March 2026).
- **Fits our case because:** Substrate is on-device and knows the device context. An agent that makes 10,000 queries in one hour is not behaving like a legitimate autonomous agent — it's either a loop or a gaming attempt. Velocity caps are lightweight, require no identity, and respect privacy.
- **Tradeoffs:** Legitimate high-frequency agents (monitoring daemons, automation pipelines) may legitimately query at high rates. Caps must be set based on observed legitimate behavior, not theoretical maximums.

**Social Graph Sybil Resistance (SybilGuard / SybilLimit)**
- **What:** Use the connectivity structure of the trust graph — malicious nodes can create many identities but few genuine trust relationships — to identify Sybil clusters.
- **Evidence:** SybilLimit reduces accepted Sybil nodes by ~200x versus SybilGuard in million-node systems. The key insight: real trust relationships require real interaction, which is expensive to fake at scale.
- **Source:** SybilLimit, IEEE/ACM Transactions on Networking 2010. Wikipedia Sybil attack (accessed March 2026).
- **Fits our case because:** Only applicable when Substrate has a trust graph (agents vouching for other agents). Not applicable to V1 where trust is individually computed. V3+ if agent endorsements are built.
- **Tradeoffs:** Requires trust relationships to exist. Cannot be implemented until trust graph features are built. Also, the social network connectivity assumptions (fast-mixing) may not hold for synthetic agent networks.

**Cost Imposition (Graduated Registration)**
- **What:** Make registration progressively more expensive (computationally or reputationally) as agents request higher trust tiers. Anonymous tier: free but no trust benefits. Registered tier: requires some cost (developer identity claim, signed manifest, etc.). Trusted tier: earned only through sustained behavior.
- **Evidence:** Graduated access is the standard pattern for open APIs that need quality control without mandatory identity. The principle that "trust is earned not claimed" — already Substrate's design — implements this implicitly.
- **Source:** General API security literature. Confirmed applicable by "Secured AI Agent Systems" (IBM Think, 2025, accessed March 2026).
- **Fits our case because:** This is already Substrate's architecture: Anonymous → Registered → Trusted. The point is that the Trusted tier must require sustained behavioral evidence that is expensive to manufacture — specifically, consistent behavior over a long time window. Time is the anti-Sybil resource that can't be faked or bought.
- **Tradeoffs:** Attackers can be patient. A sufficiently motivated attacker will wait the time window. But the cost-benefit ratio for gaming a trust score at one node on one device is extremely low — this is an attack against centralized systems with network-wide trust transfer, not Substrate's local model.

### Key Finding: Substrate's Architecture is Inherently Sybil-Resistant by Locality

A crucial insight emerges from the project's constraints: **Substrate computes trust locally, on-device, from locally-observed behavior.** This is fundamentally different from the Sybil threat model in distributed P2P systems, where fake identities are injected into the network to influence global scores.

In Substrate's model, an attacker would have to fake behavior on the same device that Substrate runs on. That requires control of the device itself, which is a different attack class (local compromise) with different mitigations (OS security, not trust algorithm design). Sybil attacks in the network sense are largely irrelevant to V1–V2 Substrate. Design resources spent on Sybil resistance are better spent on the cold start problem and decay models.

---

## 5. Cold Start Problem

### Battle-Tested Approaches

**Provisional Trust with Graduated Access Gates**
- **What:** New agents start in a neutral state with limited access. Trust builds through observed behavior. Access expands only as behavioral signals accumulate.
- **Evidence:** This is the standard pattern. Academic research on bootstrapping mechanisms for collaborative systems confirms that graduated access is the correct approach for the cold start problem in trust systems. Substrate's own design already encodes this: Anonymous → Registered → Trusted.
- **Source:** "Building a reputation-based bootstrapping mechanism for newcomers in collaborative alert systems," ScienceDirect (pii/S0022000013001219, 2014, still the canonical reference as of March 2026). Cold start survey, Springer 2025.
- **Fits our case because:** Substrate's enforcement mode ladder (Advisory → Soft Gate → Hard Gate) is the operational implementation of graduated access. No cold-start agent is blocked; they are simply not elevated.
- **Tradeoffs:** New legitimate agents have a degraded experience until they accumulate history. This is the inherent cost of behavioral trust — it requires history. The mitigation is making the initial experience tolerable, not eliminating the requirement.

**Developer Reputation Transfer (Author-Level Bootstrap)**
- **What:** An agent from an author with an established reputation gets a higher starting score than an agent from an unknown author.
- **Evidence:** App stores use this implicitly (trusted developer programs, verified publishers). The mae-principles synthesis proposed "developer trust" as a future concept. The `author` field in Substrate's schema is already captured.
- **Source:** App store trust literature. Mae-principles synthesis (confirmed).
- **Fits our case because:** `author` is already a field in `agent_registry`. A bootstrap multiplier based on `author` reputation could give well-known agents (e.g., an agent from Anthropic, from Cursor, from a known open-source project) a head start.
- **Tradeoffs:** Requires a secondary trust system for authors — who decides which authors are trusted? This recreates the cold start problem one level up unless author reputation is also behaviorally derived. Viable when Substrate has a community certification program (Substrate Store). Not viable in V1.

**Certification-Based Starting Scores**
- **What:** Agents that pass a certification process (code review, behavioral test suite, security audit) start at a higher trust tier.
- **Evidence:** App Store review processes, AWS certification programs, OpenRank's "pre-trusted seeds" in EigenTrust. Professional certifications create trust baseline before behavioral history.
- **Source:** General certification literature. EigenTrust pre-trusted peer model (Stanford, accessed March 2026).
- **Fits our case because:** The planned Substrate Store includes certifications. A "Substrate Certified" badge could translate to a starting trust boost. This is a market mechanism that bootstraps trust before behavioral data exists.
- **Tradeoffs:** Requires Substrate to run a certification program. Not available until V3+. Also, certification attests to code quality at a point in time, not ongoing behavioral quality — an agent can be certified and then go rogue.

**Decay Floor (Minimum Viable Trust)**
- **What:** New agents start with a small nonzero alpha value (e.g., alpha=1, beta=0), representing one unit of provisional trust rather than complete uncertainty.
- **Evidence:** Beta(1,1) is the Bayes prior for a fair coin — equal probability of success or failure. Starting at Beta(1,0) gives initial score = 1/(1+0) = 1.0, which is too high. Starting at Beta(1,1) gives 0.5 — provisional "benefit of the doubt." This is the standard Bayesian approach to cold start.
- **Source:** Jøsang Beta Reputation System paper (2002). Confirmed by multiple trust system implementations.
- **Fits our case because:** The current schema initializes `total_queries=0, incidents=0`, which makes `alpha/(alpha+beta) = 0/0` — undefined. The simplest cold start fix is initializing to `total_queries=1, incidents=0` (score = 1.0, "new and clean") or `total_queries=1, incidents=1` (score = 0.5, "unknown"). The initial values are a design choice that encodes the system's prior belief about new agents.
- **Tradeoffs:** The "new and clean" prior (1,0) = 1.0 is gameable: a new agent can make one query, get a perfect score, and exploit it before accumulating incidents. The "unknown" prior (1,1) = 0.5 is more conservative and correct. The enforcement mode ladder (Advisory phase first) makes this moot for V1 — no decisions are made on the score yet.

### Recommended Cold Start Implementation

For V1: Initialize `total_queries=1, incidents=1` (score=0.5, "unknown"). The enforcement mode ladder is in Advisory phase, so no gates block new agents regardless. The 0.5 initialization correctly signals "no data" rather than "perfect."

For V2: Add a `bootstrap_source` field to `trust_metadata` to record how initial trust was established (cold_start, developer_certified, author_reputation_transfer). This preserves auditability of why an agent started at its initial score.

---

## 6. Privacy-Preserving Trust

### The Design Constraint

Substrate's privacy principle: behavioral data stays on-device. Trust attestations can travel. This means the trust SCORE can leave the device; the BEHAVIORAL LOG that produced it cannot. This is not a problem to solve — it is an architectural advantage and the key differentiator from surveillance-based trust systems.

### Battle-Tested Approaches

**Signed Score Export (Simple Attestation)**
- **What:** Substrate signs an agent's trust score with its device private key. The resulting signed attestation is portable: "Device X attests that Agent Y has trust score Z at time T."
- **Evidence:** This is the foundational model for W3C Verifiable Credentials (VCs). The 2025 State of Verifiable Credential Report confirms VC adoption is accelerating with the W3C VC 2.0 standard finalized. AI is being integrated into VC verification systems to detect anomalies and prevent fraud.
- **Source:** W3C Verifiable Credentials Data Model (w3.org). Dock.io "Verifiable Credentials: The Ultimate Guide 2025" (accessed March 2026). GS1 VC technical landscape reference (ref.gs1.org, 2025, accessed March 2026).
- **Fits our case because:** Substrate already has HMAC signing infrastructure. A signed score attestation is a natural extension: `{agent_id, trust_score, computed_at, expires_at, substrate_device_signature}`. No behavioral data leaves the device. Downstream systems verify the signature and trust the score.
- **Tradeoffs:** Trust is anchored to the device. If the device is compromised or the user is malicious, the attestation is false. There is no external verification of the behavioral data that produced the score. This is a single-source-of-truth model — appropriate for V1, may need multi-device corroboration in V2.

**Zero-Knowledge Proofs for Tier Claims**
- **What:** Instead of publishing the exact score, the agent proves membership in a trust tier ("my score is above threshold T") without revealing the exact value or the behavioral data.
- **Evidence:** ZK proofs have moved from academic curiosity to production deployment. The EU Digital Identity wallet uses ZKPs for selective disclosure. The ZK KYC market grew at 40.5% CAGR as of 2025. The EU's eIDAS 2.0 framework incorporates ZK selective disclosure for identity wallets.
- **Source:** EU Digital Identity Wallet architecture (eu-digital-identity-wallet.github.io, accessed March 2026). Policy Review, "Impact of zero-knowledge proofs on data minimisation compliance" (policyreview.info, accessed March 2026). Wiley, "Promise of ZKPs for Blockchain Privacy" (2025, accessed March 2026).
- **Fits our case because:** An agent could prove "I am in the Trusted tier" to a marketplace without revealing its exact score or the queries that built it. This is the privacy-maximizing attestation model.
- **Tradeoffs:** ZKP libraries add significant complexity and compute overhead. zk-SNARKs require trusted setup ceremonies. zk-STARKs are setup-free but have larger proof sizes. For V1–V2 Substrate (Python prototype, on-device compute), the overhead is unjustifiable. The simple signed score export is sufficient and the ZKP model can be layered on later when the Go production system is built.

**Homomorphic Aggregation**
- **What:** Aggregate trust signals across multiple devices without any device revealing its raw data. Each device contributes encrypted behavioral evidence; the aggregator computes the composite score without decrypting.
- **Evidence:** Active research area in federated learning (2025 surveys across ScienceDirect, Springer, ACM). Biscotti system demonstrated proof-of-federation with reputation-based node selection using homomorphic encryption. Practical limitations: CKKS scheme enables arithmetic on encrypted data but with ~1,000x performance overhead versus plaintext.
- **Source:** Protiviti white paper on homomorphic encryption in federated learning (March 2025, accessed March 2026). ACM Computing Surveys, "When Federated Learning Meets Privacy-Preserving Computation" (2024, accessed March 2026).
- **Fits our case because:** When Substrate's cross-device sync mesh is built, agents operating across multiple devices could aggregate trust evidence from all devices without any device exposing its behavioral log. This is the eventual vision.
- **Tradeoffs:** ~1,000x compute overhead makes this infeasible for V1–V3 on-device computation. A prerequisite is building the cross-device sync infrastructure first. V4+ consideration.

### Privacy-Trust Architecture Decision

For V1–V2: Signed score attestation only. Simple, fast, already within the HMAC infrastructure.
For V3 (Go rewrite, production): ZKP-based tier proofs using a zk-SNARK library (Circom/SnarkJS or gnark in Go).
For V4+ (multi-device mesh): Homomorphic aggregation when the sync infrastructure justifies it.

---

## 7. Anti-Gaming

### Why Behavioral Trust is Harder to Game Than Opinion-Based Reviews

The research yielded a clear structural reason: **faking behavior is more expensive than faking opinion.**

- Amazon and Google reviews require only writing text. The cost is near zero. Coordinated review farms operate at industrial scale (Trustpilot removed 4.5M fake reviews in 2024; 90% were detected automatically).
- Behavioral trust requires producing actual behavior over actual time. To fake a high `total_queries` score, an attacker must generate real API requests — which consume real resources, take real time, and leave real traces (IP addresses, timing patterns, query content).

The friction multiplier is time + resource expenditure. A system that requires 90 days of consistent behavior before elevating to a higher trust tier forces the attacker to maintain the fake identity for 90 real days at real cost.

### Battle-Tested Approaches

**Behavioral Anomaly Detection (Velocity + Pattern)**
- **What:** Flag statistical anomalies in query patterns: query bursts far above median rate, perfect regularity (suggesting scripted bots), queries that never produce incidents despite high volume (suggesting a sandbox environment), etc.
- **Evidence:** iGaming fraud detection platforms (SEON, CrossClassify, Threatmark) use behavioral anomaly detection as the primary defense against Sybil-style multi-accounting. They detect "accounts with identical behavioral profiles" — behavior that is too consistent, too fast, or too perfectly timed.
- **Source:** SEON iGaming fraud prevention (seon.io, 2025, accessed March 2026). CrossClassify AI-powered fraud detection (crossclassify.com, accessed March 2026). AU10TIX Top Fraud Trends 2025-2026 (accessed March 2026).
- **Fits our case because:** Substrate observes query rates, query timing, and query content. A bot gaming the trust system will exhibit different patterns than a human-operated AI assistant. Velocity limits and anomaly flags are the correct first line of anti-gaming defense.
- **Tradeoffs:** Requires baseline behavioral data before anomalies can be detected. Month 1 of operation has no baseline. Anomaly detection is a V2 feature, not V1.

**What Credit Bureaus Do: Behavioral Signals That Are Hard to Fake**
FICO's anti-gaming methodology offers important lessons:
1. **Temporal commitment:** Payment history over years cannot be manufactured quickly. Time is the primary anti-gaming mechanism.
2. **Diverse signal types:** FICO uses payment history, credit utilization, account age, credit mix, and new credit inquiries. Gaming one signal (e.g., opening new accounts to show "credit mix") degrades another signal (account age decreases). Multi-signal systems are harder to optimize for gaming than single-signal systems.
3. **Trended data:** FICO Score 10T uses 24-month behavioral trajectories. An agent whose behavior is trending worse over time is scored worse even if the absolute current value looks acceptable. A gamer who builds up trust then depletes it is caught by the trend.

**Source:** FICO algorithmic credit scoring white paper (fico.com, accessed March 2026). FICO Score 10T methodology (myfico.com, accessed March 2026).

**Gameable Signals: What to Watch For**

| Signal | Why It's Gameable | Mitigation |
|---|---|---|
| `total_queries` alone | Attacker can run a query loop at no cost | Velocity cap + anomaly detection |
| `incidents / total_queries` ratio | Attacker avoids all behaviors that trigger incidents | Define incidents that are triggered by realistic failure modes, not just explicit errors |
| Certification/registration | Attacker can register many agents cheaply | Registration cost (e.g., developer GitHub account link) creates friction |
| Starting score (cold start) | New agent starts at 0.5 = tolerable default | Enforcement mode ladder ensures gates only apply after baseline data accumulates |

**The Key Anti-Gaming Insight for Substrate:**
The definition of "incident" is the most critical anti-gaming design decision in the entire trust system. If incidents are only triggered by explicit, obvious failures (e.g., a malformed API call), a sophisticated attacker will simply avoid those calls. Incidents must be defined to include behavioral anomalies that are costly to consistently avoid:
- Query volume that exceeds normal agent behavior patterns
- Queries during device privacy mode (active circumvention attempt)
- Declared capabilities that are never exercised (possible deception)
- Query patterns inconsistent with declared capability set

This definition of incident is not yet present in the codebase. It is the highest-value trust system design decision that isn't currently addressed.

---

## Gaps and Unknowns

1. **Incident definition is completely absent.** The schema has an `incidents` column. Nothing in the codebase defines what triggers an incident. This is the most critical gap — the entire Beta Reputation System is hollow without it. (Confirmed by mae-principles synthesis, item 5.)

2. **No time-series query data exists.** Implementing temporal decay requires knowing when each query happened. The current schema only stores `total_queries` as a running count. Decay requires a migration to time-stamped event data. This is the key architectural commitment for V2 trust.

3. **Optimal half-life for agent trust is empirically unknown.** Research confirmed there is no universal optimal value. Substrate will need 60–90 days of real behavioral data to fit a decay parameter. Any value chosen now is a hypothesis.

4. **Multi-device trust corroboration is unresearched for this expedition.** When an agent operates across Substrate on multiple devices, do the trust scores from all devices agree? What if one device is compromised? This question is deferred to the cross-device sync expedition.

5. **The boundary between Advisory and Soft Gate thresholds is unknown.** What trust score constitutes "warn the caller"? What constitutes "block"? These are policy decisions that require real data, not algorithms. The enforcement mode ladder correctly defers this decision — but the question is when to escalate from Advisory to Soft Gate.

6. **Behavioral anomaly baselines don't exist yet.** Anti-gaming via anomaly detection requires knowing what normal looks like. Normal only becomes visible after weeks of legitimate operation. There is no shortcut.

7. **ZKP proof system selection for Go production.** When Substrate is rewritten in Go, two ZKP libraries are viable: gnark (by ConsenSys, MIT license, actively maintained) and arkworks (Rust, but Rust-Go FFI is possible). Neither was evaluated in depth here. This is a V3 decision.

---

## Synthesis

### The Strongest Overall Approach

The behavioral trust science for Substrate is already 70% correct by design. The Beta Reputation System mapped to the existing schema is the right algorithm. The enforcement mode ladder from the mae-principles expedition is the right operational framework. What's missing is:

1. **The incident definition** — without it, the beta term is always zero and the formula is always 1.0 (perfect trust). This is not a complex engineering problem; it's a design decision that must be made explicitly.

2. **The temporal layer** — V1 can be timeless (accumulate counts), but V2 needs timestamps per query and per incident so decay can be applied. The schema migration from count columns to event records is the key architectural commitment.

3. **The capability dimension** — `trust_metadata` JSON is already reserved in the schema for multi-dimensional scores. Filling it with per-capability alpha/beta pairs is the natural V2 extension.

### What Combination of Approaches Works Best

| Concern | Recommended Approach | When |
|---|---|---|
| Single trust score | Beta Reputation System (existing) | V1 |
| Cold start | Initialize to (1,1) = 0.5 prior | V1 |
| Sybil resistance | Locality model + velocity caps | V1 |
| Trust decay | Exponential decay, 30-day half-life hypothesis | V2 |
| Context-dependence | Per-capability alpha/beta in trust_metadata | V2 |
| Anti-gaming | Incident definition breadth + velocity anomaly flags | V1 (definition), V2 (anomaly) |
| Privacy attestation | Signed score export via HMAC | V2 |
| ZKP tier proofs | zk-SNARKs (gnark in Go) | V3 |
| Homomorphic aggregation | Only with multi-device sync mesh | V4+ |
| EigenTrust / PageRank | Not recommended — Substrate's model is behavioral, not positional | Never for core scoring |
| Transitive trust (Subjective Logic) | Only if agent delegation chains are built | V3+ |

### What the Orchestrator Needs to Know

**The incident definition is the only truly blocking design decision for trust scoring.** Everything else — decay, multi-dimensionality, ZKP, anti-gaming — is layered on top of a functioning incident signal. A well-chosen incident definition produces a meaningful beta term, which produces a meaningful trust score, which makes the entire system operational. A poorly chosen or absent incident definition means the Beta Reputation System outputs 1.0 for every agent regardless of behavior.

**Substrate's local-only trust model is a Sybil-resistance gift that should be celebrated, not apologized for.** The reason Sybil attacks devastate distributed reputation systems (P2P, social networks, blockchain) is that fake identities can influence the global score. Substrate's scores are local, computed from locally-observed behavior. There is nothing for a remote Sybil attack to influence. The only Sybil threat is local (controlled by the device owner), which is outside the trust system's threat model entirely.

**Time is the ultimate anti-gaming mechanism, and it's free.** The enforcement mode ladder naturally implements this: an agent cannot game its way through three months of advisory-mode observation followed by a month of soft-gate warning. Each phase requires sustained behavioral consistency over real elapsed time. This is more robust than any algorithmic anti-gaming mechanism.

**The schema is well-positioned.** The `trust_metadata` JSON column, the `capabilities` array, the `registration_time` and `last_seen` fields, and the `total_queries` + `incidents` counters form a complete foundation. No new schema is needed for V1. V2 requires adding per-query timestamps (new table or extending the events table) and per-capability incident tracking.
