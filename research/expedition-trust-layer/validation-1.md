# Validation Report: Expedition Trust Layer
## Date: 2026-03-10
## Validator: Independent Review Agent

---

## Preface

This report follows the divergence-first protocol. Problems are documented before agreements. Every challenge is specific. Every alignment check references the Research Brief.

---

## 1. Evidence Challenges

### 1.1 Team 1 — Equifax 2017: The "147 million Americans" figure

Team 1 states "Equifax 2017: 147 million Americans' data." The commonly reported figure is 147 million, which has appeared in FTC and CFPB communications. However, Equifax's own post-breach disclosures put the number at approximately 143–148 million, with the "147.9 million" figure emerging only after multiple revisions. Team 1 cites this without a direct source — the only Equifax citation is attributed to CFPB general documentation, not the breach report itself. The number is likely correct but the sourcing is loose for a claim used to make an argument about privacy failure at scale.

### 1.2 Team 1 — DigiNotar: "200+ fraudulent certificates covering over 20 domains"

Team 1 says "more than 200 certificates" and "over 20 domains." The Mozilla Security Blog source cited is real and well-regarded. However, the Mozilla blog post from September 2011 is cited as accessed 2026-03-10, which is plausible for archival access — but the specific claim about 200+ certificates across 20+ domains conflates two different figures from different stages of the investigation. The initial scope was narrower; the 200+ figure emerged after deeper forensic analysis. This is a minor precision issue, not a fabrication, but the sourcing collapses a multi-stage disclosure into a single claim.

### 1.3 Team 1 — eBay Feedback Inflation: No Timeline or Measurement

Team 1 explicitly acknowledges in its Gaps section that it found "general claims but not a specific timeline or measurement of when the positive feedback rate became meaningless." The claim "98%+ of feedback became positive, destroying the signal value" appears in the synthesis without a direct citation. The eBay Help source cited covers current feedback policy, not historical signal degradation. This is a pattern assertion, not an evidenced one. The conclusion drawn from it — that Substrate's Beta formula solves this problem — may be correct, but it rests on an unverified premise about eBay's actual inflation trajectory.

### 1.4 Team 2 — MCP "97M+ monthly SDK downloads as of December 2025"

Team 2 cites this figure with three sources: the MCP Specification page, a Stack Overflow Blog post from January 2026, and the MCP Anniversary Blog from November 2025. The November 2025 blog announced the 97M figure. The figure is plausible and widely cited. However, Team 4 independently cites the same figure from a different source (The New Stack). This cross-citation is reassuring but does not confirm the figure is accurate — it confirms the figure was published and then repeated. No independent verification (e.g., npm download counters or PyPI stats) was performed by either team to validate the number. The figure should be treated as vendor-reported, not independently verified.

### 1.5 Team 2 — OIDC-A: Single-Author Proposal Presented as Protocol Direction

Team 2 presents OIDC-A as a "Novel Approach" with the caveat that it is "not yet a formal standards track document." However, the framing — "if OIDC-A becomes a standard, Substrate's trust tier becomes a native field in the agent's identity token" — implies a reasonable probability of adoption. The source is a single blog post from April 2025 by one author (Subramanya N.) with no affiliation to any standards body. There is no evidence this has been submitted to IETF or W3C, no implementation guide, no known implementations, and no endorsement from any organization beyond the author. The adoption probability is very low. The claim that Substrate should not build against it "exclusively" understates the problem: Substrate should not build against it at all until it reaches a formal proposal stage.

### 1.6 Team 3 — "ZK KYC market grew at 40.5% CAGR as of 2025"

The ZKP tier proof section cites "ZK KYC market grew at 40.5% CAGR as of 2025" from a Policy Review source. This is a market research figure for a specific niche (KYC applications of ZKP) cited to support the broader claim that ZKPs have reached production deployment. Market size figures from research firms are frequently derived from small base numbers, have wide confidence intervals, and are often paid-for projections rather than empirical measurements. The figure does not directly support the claim that ZKP computation is lightweight enough for Substrate's "lightweight first" constraint — which is actually the critical question. The CAGR figure is interesting but not evidence of the thing that matters.

### 1.7 Team 4 — Decagon "$4.5B valuation (January 2026)"

Team 4 cites Bloomberg and Decagon's own Series D announcement. The Bloomberg article URL is cited but cannot be independently verified within this validation without live access. The Decagon source is self-reported. Valuations from private funding rounds are frequently paper valuations that do not reflect market price. This does not invalidate the argument Team 4 makes (that the market for action-taking agents is enormous), but the specific $4.5B figure cited as market evidence is not independently verified.

### 1.8 Team 4 — "Starbucks drives 60% of U.S. revenue from loyalty members"

Team 4 cites GrowthHQ for this figure. The Starbucks loyalty revenue claim is commonly cited in marketing analysis. However, the 60% figure historically referred to Starbucks Rewards transactions as a proportion of total U.S. transactions — not revenue. These are meaningfully different metrics, and the distinction matters when Team 4 uses this figure to argue for behavior-based loyalty economics. High transaction frequency from loyalty members does not automatically translate to 60% of revenue if those members transact at lower average ticket prices. The figure should be treated as approximate, not precise evidence.

### 1.9 Team 5 — "SQLite 100K TPS over a billion rows" Applies to Write-Heavy Trust Recording

Team 5 cites the andersmurphy.com December 2025 benchmark as evidence that SQLite is not the bottleneck. However, Team 5 immediately qualifies this: "Substrate's trust recording is write-heavy under concurrent agent load" and "the 100K TPS benchmark requires read-heavy configuration — write-heavy trust recording under concurrent load hits earlier limits." This is honest self-correction, but it means the headline claim (SQLite is sufficient) relies on a benchmark that the same team acknowledges does not apply to Substrate's specific workload. The SQLite WAL mode concurrency limit for write-heavy workloads is not tested or cited. This matters for the Go rewrite timing recommendation.

---

## 2. Contradictions Between Teams

### 2.1 Trust Decay Timing: Team 3 Recommends Deferral; Team 5 Implies It's Part of Phase 1

Team 3 explicitly states: "Do not decay yet. The Beta Reputation System's formula is already insensitive to time... Implement decay in V2 after observing real query and incident distributions." Team 5's critical path (Part 3) includes decay as part of the `compute_trust()` function in Phase 1, describing the TEMPORAL signal as `(now - registration_time) / 86400` contributing to the score. This is not exponential decay — it is a recency component — but Team 5 treats this as satisfying the "use it or lose it" principle while Team 3 specifically says not to implement time weighting before V2. The two reports use different definitions of "decay." This needs to be resolved: does the V1 `compute_trust()` function include any temporal component, or not?

**Stronger evidence:** Team 3's argument is stronger. Implementing a temporal signal before baseline data exists means choosing weights blindly. The TEMPORAL signal in Team 5's formula weights days-since-registration, which means newer agents score lower on one dimension regardless of behavior — penalizing new legitimate agents with no data justification. Team 3's deferral is the more rigorous recommendation.

### 2.2 Team 5's Three-Signal Formula Contradicts Previous Expedition Findings

Team 5 proposes a three-signal trust formula: TEMPORAL (days since registration), BEHAVIORAL (queries per day), and OPERATIONAL (Beta ratio). The Research Brief states the Beta Reputation formula is "already identified" and refers specifically to `trust = alpha/(alpha+beta)`. Team 3, Team 5's peer on this expedition, explicitly recommends Beta only for V1 and defers multi-dimensional scoring to V2+. Team 5's Phase 1 MVTL introduces two new signal dimensions without the same level of scientific validation it provides for the Beta formula itself. The sources for the combined three-signal approach (maprinciples synthesis) are internal references, not external validation. This is Team 5 extending beyond the validated formula under the guise of "Phase 1."

**Resolution needed:** Either the V1 formula is `total_queries / (total_queries + incidents)` (Team 3's recommendation, consistent with the Brief), or it is the three-signal composite (Team 5's proposal, lacking external validation). These produce different scores. A design decision must be made, not assumed.

### 2.3 Cold Start Initial Values: Team 3 Says (1,1); Team 5's Formula Produces a Different Starting Score

Team 3 recommends initializing new agents to `total_queries=1, incidents=1` (Beta score = 0.5). Team 5's Phase 1 critical path says "trust score in API responses" will come from the three-signal formula using `registration_time`, `last_seen`, and `total_queries/incidents`. At registration time with Team 5's formula, a new agent with 0 queries and 0 incidents gets: TEMPORAL = some small value (just registered), BEHAVIORAL = 0/1 = 0, OPERATIONAL = 0/0 = undefined. Team 5 does not specify initial values for the schema, meaning the cold start problem survives into Team 5's own MVTL unless Team 3's initialization is adopted. Neither team explicitly resolves the interaction between Team 3's (1,1) initialization and Team 5's formula.

### 2.4 Go Rewrite Timing: Teams Imply Different Thresholds

Team 5 states the rewrite becomes necessary "before the first external adoption" — specifically when the trust schema and API surface need to be committed. Team 2 implies the Go rewrite is needed before W3C VC issuance with BBS+ cryptosuites, citing immature Python libraries. Team 3 treats Go as a V3 consideration for ZKP libraries. These three teams give three different trigger conditions that could place the Go rewrite anywhere from immediately (before first external user) to after V2 features are proven. No synthesis between these positions appears in any of the five reports.

---

## 3. Alignment Drift

### 3.1 Team 2 Drift: Standards Body Participation Strategy Is Out of Scope

The Research Brief's expected outcome for Team 2 is: "What protocols, standards, and infrastructure a behavioral trust protocol needs" and "What would a 'Substrate Trust Attestation' look like as a portable credential?"

Team 2 spends significant space on a four-step standards participation strategy ("Join W3C AI Agent Protocol Community Group," "Publish an IETF Individual Draft," "Get MCP Registry trust integration," "IETF Working Group participation"). This is strategic roadmapping, not protocol architecture research. The Brief says "Do NOT modify any existing code — this is pure research" and the expected outcome does not include "advise how Substrate should position in standards politics." The strategy is interesting but it is not what was asked for. The actual protocol architecture question — what does a Substrate Trust Attestation credential look like technically — is answered well, but it is partially displaced by strategic recommendations that belong in a roadmap, not a research finding.

### 3.2 Team 4 Drift: Competitive Analysis Depth Exceeds the Brief's Scope

The Research Brief for Team 4 is: "How do trust-gated marketplaces create unstoppable flywheels? Study credit card networks, app stores, loyalty ecosystems, professional certifications. How do Fortune 500 brands plug into trust infrastructure?" Team 4 delivers an extensive competitive landscape analysis (20+ companies) that goes far beyond the Brief's scope. The competitive analysis is valuable but it answers a question that was not asked — "who are the competitors?" — rather than the question that was asked — "how do the mechanics of trust-gated marketplaces work?"

The brief's expected outcome is: "How brands and marketplaces plug into trust infrastructure (the network effect engine)." The marketplace mechanics are covered well (Visa, Starbucks, Progressive Snapshot). But the competitive analysis displaces the deeper question: what are the *mechanics* of how a Fortune 500 brand would actually plug into Substrate? What does the API call look like? What's the data contract? What is the brand's motivation stated in procurement terms, not market analysis terms? These questions are not answered.

### 3.3 Team 3 Drift: Anti-Gaming Section Recommends LLM-Adjacent Pattern Detection Without Acknowledging Constraint

Team 3's anti-gaming section discusses "behavioral anomaly detection" including identifying "queries that never produce incidents despite high volume (suggesting a sandbox environment)" and "query patterns inconsistent with declared capability set." These anomaly patterns require either rule-based inference from behavioral signals or statistical modeling. Team 3 frames them as "velocity caps and anomaly flags." However, the Brief's constraints include "Community knowledge over AI inference. Signatures, not LLMs." The anomaly detection patterns Team 3 describes are inference from behavioral signals — not identical to LLMs, but the same category of problem. The Brief says Substrate should use community knowledge (signatures, pattern databases) not inferred scoring. Whether behavioral anomaly detection crosses this line is not addressed by Team 3. This is a constraint the team should have explicitly engaged with.

### 3.4 Team 5: Three-Signal Formula Violates "No Over-Engineering the Prototype"

The Brief constraint: "No over-engineering the prototype — it's for proving concepts." Team 5's Phase 1 MVTL introduces a three-signal weighted composite formula for V1 trust scoring. The Beta Reputation System (`total_queries / (total_queries + incidents)`) is a single formula that the Brief identifies as already validated. Team 5 adds TEMPORAL and BEHAVIORAL dimensions with weights, creating a more complex system with three unvalidated parameters. This is over-engineering the prototype when the validated formula already exists and the Brief explicitly prohibits over-engineering. The three-signal formula belongs in V2 after baseline data, not in the MVTL.

---

## 4. Missing Angles

### 4.1 No Team Addressed the "Always Aware, Never Acting" Constraint for the Trust Layer Itself

The Brief's design principle: "Always aware, never acting. Substrate provides knowledge, agents and apps act on it." The trust layer, as described by multiple teams, includes mechanisms that approach action: Gap 2 (incident wiring) would require Substrate to detect anomalous behavior and increment a counter that affects what agents can do. The trust tier system gates access and rates. The verification protocol enforces trust-tier-based discounts. These are not passive observations — they are outputs that affect behavior. No team addressed whether the trust layer itself violates the "never acting" principle, and if so, whether that is an intentional evolution of the design or a constraint that needs to be reframed. This is the most conceptually important question the expedition did not ask.

### 4.2 No Team Researched Whether W3C VC Revocation Mechanisms Are Lightweight Enough

Multiple teams converge on W3C Verifiable Credentials with BBS+ selective disclosure as the portable trust credential format. Team 2 explicitly flags "credential freshness vs. privacy" as an unanswered question: "if Substrate issues a trust VC and the agent's behavior deteriorates, how is the credential revoked without creating a global revocation list that leaks which agents have been penalized?" Team 5 mentions revocation as a requirement but does not answer it either. W3C StatusList2021 and Bitstring Status List v1.0 are mentioned by Team 2 as existing options "with scalability and privacy tradeoffs." No team researched what those tradeoffs actually are, whether they are compatible with Substrate's privacy constraints, or whether an alternative revocation model exists. Given that the entire trust credential model depends on timely revocation when trust scores drop, this is a blocking unknown that all five teams passed by.

### 4.3 No Team Asked What Happens When the User Intentionally Games Their Own Trust Score

The Sybil resistance analysis (Team 3) focuses on external attackers gaming the system. The credit bureau comparison (Team 1) focuses on why behavioral trust is harder to fake than opinion trust. But neither addresses the scenario where the legitimate device owner deliberately runs high-frequency benign queries from their own agents to inflate their own trust scores. This is not a Sybil attack (no fake identities) and it does not violate any architectural constraint (the device owner has full access). Yet it could produce high-trust scores for agents that have never operated in any real behavioral context. The "locality is inherently Sybil-resistant" finding in Team 3 explicitly identifies this as the device owner's domain — and then stops, treating it as outside scope. But the trust economy (brand discounts, premium access) would be directly vulnerable to this. No team proposed a mitigation.

### 4.4 The Incident Definition Is Identified as Absent but No Team Proposed One

Teams 3 and 5 both explicitly call out the missing incident definition as the most critical design gap. Team 3 says: "The incident definition is the only truly blocking design decision for trust scoring." Team 5 says: "The incident taxonomy is entirely undefined... This requires Guiding Light's input — it's a product decision, not a technical one." But the Brief assigned Team 3 specifically to research "how you score trust from observed behavior at internet scale." The incident definition is not purely a product decision — it is informed by how other systems have defined behavioral signals (credit bureau payment events, Google Play Integrity runtime checks, iGaming fraud velocity signals). Team 3 provides good background on anti-gaming but stops short of proposing even a draft incident taxonomy based on what it learned. The research was done; the synthesis was not.

### 4.5 No Team Researched the EU AI Act Implications for Behavioral Trust Infrastructure

The MEMORY.md notes an EU AI Act legal review with August 2026 as a deadline. A behavioral trust system that scores AI agents and uses those scores to gate access, set rates, and issue credentials could fall under EU AI Act provisions regarding high-risk AI systems or prohibited practices (depending on how trust scores affect access to services). No team touched this angle. Team 1 correctly notes that "regulatory framework will come" and uses FCRA as the analogy, but FCRA is US-specific. The EU AI Act is already in force. This is not a deferred risk — it is a live compliance question for a system designed to operate at internet scale. Given the August 2026 deadline in the project's own records, this gap is consequential.

---

## 5. Agreements — High-Confidence Findings

The following findings emerged independently from multiple teams and are the most trustworthy outputs of this expedition.

### 5.1 W3C Verifiable Credentials 2.0 is the Right Trust Attestation Format

Teams 2, 3, and 5 independently converged on W3C VC 2.0 with BBS+ selective disclosure as the correct format for portable Substrate trust attestations. Team 2 reached this from protocol architecture analysis. Team 3 reached this from privacy-preserving trust science. Team 5 reached this from gap analysis of existing code against standards. Three independent angles, same conclusion, all citing the same finalized W3C standard (May 2025 Recommendation). This is the highest-confidence technical finding in the expedition.

### 5.2 The Behavioral Trust Gap Is Real and Unoccupied

Teams 2 and 4 both independently confirmed, through different research angles, that no existing protocol or product fills the behavioral trust layer. Team 2's protocol stack table shows behavioral trust as "NOTHING" beneath all existing agent protocols. Team 4's competitive table shows every company either builds agents, governs them in silos, or handles security/auth — none builds portable behavioral reputation. This convergence across protocol research and competitive research is strong validation of the core product thesis.

### 5.3 Beta Reputation System is the Correct V1 Algorithm

Teams 3, 5, and (implicitly) Team 1 all confirm the Beta Reputation System as the right choice for V1 scoring. This aligns with the Brief's identification of the formula and the mae-principles expedition findings cited by multiple teams. The evidence base (Jøsang 2002, IoT/MANET/P2P production use, previous expedition validation) is the most thoroughly sourced finding in the expedition.

### 5.4 Open Access as Cold Start Solution is Validated by Historical Precedent

Team 1's analysis of credit bureaus, eBay, and SSL/TLS independently validates the Brief's existing design decision: "open access is the design." The finding that every trust system that scaled had a compelling cold-start answer — and that Substrate's inversion (register to earn benefits, not to participate) is the correct answer — is confirmed by three distinct historical case studies. This is not a new recommendation; it is validation of an existing design decision.

### 5.5 Auth Middleware and record_query() Wiring Are Blocking Gaps

Teams 3 and 5 independently identify the same two missing wires (`record_query()` never called, no auth middleware on `/api/query`) as the most critical implementation gaps. Team 3 flags the incident definition. Team 5 surfaces both and identifies the missing wiring explicitly. The mae-principles expedition validators (cited by Team 5) made the same finding. Three independent research passes reaching the same conclusion about the same two lines of missing code is high-confidence validation.

---

## 6. Surprises

### 6.1 Team 3's "Sybil Resistance by Locality" Argument Is Genuinely Novel and Strong

The finding that Substrate's local trust computation makes distributed Sybil attacks structurally irrelevant — because there is no global score to influence from outside the device — is a clean argument not seen in the prior expedition research. It re-frames what looked like a weakness (single-device scope) as a security property. This is the kind of architectural insight that should be explicitly documented as a design principle, not buried in a research synthesis section. It reframes the "Substrate is just local" limitation as "Substrate is inherently Sybil-resistant by design."

### 6.2 Progressive Snapshot (Usage-Based Insurance) Is a Better Product Analogy Than the Credit Bureau

Team 4 surfaces Progressive Snapshot as a behavioral-trust-to-economic-benefit analogy that is cleaner than the credit bureau model Team 1 develops at length. The UBI model (observe driving behavior → score safety → adjust insurance rate → create economic incentive for safer behavior) is exactly Substrate's loop for agents. It is more visible to consumers, better understood as a product mechanic, and more easily explained. That Team 4 found this while doing marketplace research rather than historical precedents research means it was almost missed. It should have appeared in Team 1's case studies — UBI is arguably the closest living analog to what Substrate proposes.

### 6.3 cheqd Has Already Built an MCP Server for VC Issuance

Team 5 identifies that cheqd has released MCP servers specifically enabling agents to read/write DIDs and issue Verifiable Credentials. This means Substrate is not building into a vacuum — there is a working precedent for MCP-integrated VC infrastructure in 2025. This was not in any prior expedition and has direct implications for the technical approach: Substrate could potentially extend or integrate with cheqd's MCP server rather than building VC issuance from scratch. No team explored this option. It deserves attention before committing to a full custom VC issuance implementation.

### 6.4 The "Never Acting" Principle May Need Deliberate Reframing for the Trust Layer

As noted in Missing Angles (4.1), the trust layer's incident counter, tier gates, and verification protocol all introduce outputs that influence agent behavior. This was not an explicit finding in any team's report — it emerged from reading all five reports together. The "always aware, never acting" principle was designed for Substrate's awareness layer (process scanning, event observation). Applying it rigidly to the trust layer would prevent trust tiers from having any effect. This tension is never surfaced by any team. Whether the principle needs to be scoped (applies to the awareness layer, not the trust enforcement layer) is a design decision that has not been made explicitly. This is the most consequential unresolved tension in the entire expedition.

---

## Summary Judgment

**What to trust with high confidence:**
- W3C VC 2.0 + BBS+ as the trust attestation format (three independent teams, finalized standard)
- The behavioral trust gap is real and unoccupied (two independent research angles)
- Beta Reputation System for V1 (three independent confirmations)
- Auth middleware + record_query() wiring are the most blocking implementation gaps (three independent confirmations)
- Open access as cold start solution is validated by historical precedent (four historical case studies)

**What needs further work before acting:**
- V1 trust formula: resolve the Team 3 vs. Team 5 disagreement (pure Beta vs. three-signal composite) before writing any code
- VC revocation mechanism: no team answered this; it is a blocking unknown for the attestation format
- Incident taxonomy: the research was done to inform a draft; no draft was produced; this needs synthesis before the MVTL can be built
- EU AI Act implications: not researched; requires dedicated attention before any external deployment

**What to set aside:**
- OIDC-A: single-author blog post, no standards traction, do not build against it
- Team 2's standards participation strategy: useful as context, not a research finding
- Team 4's competitive landscape: exceeds Brief scope; useful separately, not part of the marketplace mechanics answer
- Three-signal V1 formula (Team 5): over-engineers the prototype, not validated

**The most important unresolved question the expedition did not ask:**
Does the trust layer violate the "always aware, never acting" design principle? This must be explicitly answered before the trust layer is built, because the answer determines whether Substrate is extending its architecture or contradicting its own foundation.
