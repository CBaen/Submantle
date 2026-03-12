# Expedition Validation Report: Trust Layer
## Date: 2026-03-10
## Validator: Cross-Validation Agent (Second Pass)

---

## Methodology

All five team findings and the research brief were read in full. Four critical claims were externally verified via live web search. Analysis follows the divergence-first protocol: challenges before agreements.

---

## 1. Evidence Challenges

### Challenge 1: W3C VC 2.0 — CONFIRMED, but with a material caveat

Teams 2, 3, and 5 all state W3C VC 2.0 became a "final W3C Recommendation on May 15, 2025." **This is verified.** The W3C press release and news page confirm the date. Seven specifications were published.

**The caveat no team mentioned:** The W3C announcement states "all but two of the documents have been published as W3C Recommendations — two exceptions are still Candidate Recommendations." No team identified which two remain incomplete. The BBS+ cryptosuite (which Teams 2, 3, and 5 all rely on for selective disclosure — the privacy-preserving "prove your tier without revealing your data" feature) was NOT among the seven finalized Recommendations. BBS cryptosuites are still on the W3C standards track but were not in the May 2025 finalized set. This is a gap that weakens the selective-disclosure claims. Teams should have verified which specifications specifically were finalized before building architectural arguments on top of them.

**Impact on findings:** The W3C VC Data Model itself is solid. The BBS+ selective disclosure layer requires separate verification before Teams 2 and 5's claims about privacy-preserving tier proofs can be trusted.

### Challenge 2: IETF RFC 9711 EAT — CONFIRMED

Teams 2 and 5 state RFC 9711 was published April 2025. **This is verified.** The IETF datatracker and RFC editor both confirm RFC 9711 is a published Internet Standards Track RFC.

No challenge here. The claim is accurate.

### Challenge 3: IETF EAT Agentic Extensions Draft — CONFIRMED AS REAL, but materially mischaracterized

Team 2 states `draft-huang-rats-agentic-eat-cap-attest-00` is published on the IETF datatracker. **This is verified** — the draft exists and its contents match what Team 2 describes.

**The challenge:** Team 2 presents this as a signal of institutional standards momentum: "Submantle could contribute to shaping them." But the draft has an expiration date of December 15, 2025 — meaning it expired without renewal before the date of this expedition (March 2026). An expired individual draft with no adopted working group status is not evidence of institutional momentum; it is evidence that one person submitted a document that has not attracted enough support to be renewed. Team 2 should have checked the expiration date. This does not invalidate the technical content of the draft, but it significantly weakens the "window is open for Submantle to contribute" framing. A draft that expired in December 2025 is not an active IETF process Submantle can join.

**Impact on findings:** The EAT agentic extension concept is real and technically useful. The standards-track opportunity claim is overstated. Submantle cannot "contribute to shaping" a draft that has already expired.

### Challenge 4: HUMAN Security AgenticTrust — CONFIRMED, and the competitive gap claim is WEAKENED

Team 4 says HUMAN Security's AgenticTrust is "the closest in spirit" to Submantle but positions it as purely defensive. The search results show HUMAN's own language: "Trust is not a score, a label, or a rule; trust is a dynamic, ongoing decision." AgenticTrust "decisions evolve in real-time based on what the agent does, not just what it is."

**The challenge:** Team 4's characterization that HUMAN Security is "defensive (detect and block malicious agents)" while Submantle is "constructive (build and reward trustworthy agents)" is a framing choice, not a factual distinction. HUMAN Security's own marketing explicitly claims they are building behavioral, adaptive, dynamic trust — not just blocking. The gap between the two products is real but narrower than Team 4 admits. Specifically: HUMAN Security operates at the web application layer (protecting websites and APIs from AI agent traffic), while Submantle operates at the OS/device layer. That is the real distinction. The "defensive vs. constructive" framing understates HUMAN Security's behavioral sophistication and could lead to underestimating them as a competitor.

**Impact on findings:** The "no one is doing what Submantle does" claim remains directionally correct for the OS-layer, portable, cross-ecosystem behavioral trust score specifically. But HUMAN Security is a more sophisticated near-competitor than Team 4 acknowledges.

### Challenge 5: Zenity funding and characterization — CONFIRMED, minor error

Team 4 says Zenity raised "$38M Series B (October 2024), led by Third Point Ventures and DTCP, with Microsoft M12 as strategic investor. Total funding: $55M+." **This is verified.** The investor list and funding figures are accurate. The date is confirmed as October 2024.

**Minor factual error:** Team 4 says Zenity has "65 employees (SF + Sydney)." The search results state 65 employees, but describe locations in their Series B announcement differently. This is a trivial discrepancy; the figure is approximately correct.

### Challenge 6: Decagon's $4.5B valuation — SOURCE IS BLOOMBERG, BEHIND PAYWALL

Team 4 cites Decagon's $4.5B valuation at $250M Series D (January 2026), sourced to Bloomberg. Bloomberg articles are paywalled and this validator could not independently verify the figure. The Decagon funding page is cited as a second source. This is a potentially inflated figure in a period of high AI valuations; it should be treated as unverified until a non-paywalled source confirms it.

**Impact on findings:** The market size argument (agents that take real actions are a big market) stands regardless of whether Decagon's valuation is $4.5B or $2B. The specific number is not load-bearing.

### Challenge 7: Team 3's EigenTrust "not recommended" — correct finding, but the reason given is partially wrong

Team 3 correctly concludes EigenTrust is not suitable for Submantle and labels it "Not recommended for V1 or V2." The reasons given include: "Fundamentally designed for distributed P2P, not centralized infrastructure." This is accurate. However, Team 3 also says EigenTrust "does not scale to internet-scale (billions of nodes) using naive power iteration — the matrix becomes intractable." This is technically correct for naive implementation but misleading — EigenTrust's modern variants (including the version used in OpenRank) use distributed power iteration that scales well. The correct reason to reject EigenTrust is that it requires a pre-existing trust graph, which Submantle doesn't have and may never have in the form EigenTrust requires. The scalability claim is a red herring.

**Impact on findings:** The conclusion (don't use EigenTrust for V1-V2) is correct. The supporting argument is partially inaccurate.

### Challenge 8: Team 1's eBay reputation inflation — evidence is anecdotal

Team 1 states that eBay feedback became meaningless because "98%+ of feedback became positive." This is a widely repeated claim but Team 1 cites only "eBay Help" and general claims, not a specific academic study or data source. Team 1 explicitly acknowledges this gap in their own "Gaps and Unknowns" section. The lesson drawn (behavioral trust beats opinion trust) is strongly supported by other cases (Amazon, Steam) even if the eBay specifics lack hard citation. This is a self-aware gap, not a hidden one.

**Impact on findings:** Low. The pattern holds across enough cases that the eBay anecdote is not load-bearing.

---

## 2. Contradictions Between Teams

### Contradiction 1: When to implement trust decay

Team 3 says: "Do not decay yet. Implement decay in V2 after observing real query and incident distributions."

Team 5 says: The decay mechanism is "part of Gap 3" (the compute_trust() function), which is listed as part of the Minimum Viable Trust Layer buildable "in a single focused session."

These are incompatible. Team 3 argues correctly that implementing decay before having baseline data produces an arbitrarily parameterized model. Team 5 implies decay is part of V1 work. **Team 3 is correct.** Decay requires a tunable parameter (half-life) that cannot be responsibly chosen without empirical data. Team 5's framing that decay is part of the TEMPORAL signal in compute_trust() conflates two things: using last_seen as a freshness indicator (reasonable in V1) with full exponential decay applied to historical queries (not reasonable in V1 without data).

**Resolution:** The TEMPORAL signal (penalizing agents not seen recently via last_seen delta) is appropriate for V1. Full decay applied to accumulated alpha/beta history is a V2 decision. Teams should have distinguished these.

### Contradiction 2: Cold start initialization

Team 3 recommends initializing new agents at `total_queries=1, incidents=1` (Beta prior = 0.5, "unknown").

Team 5 does not specify initialization values and implies the current schema state (0,0 = undefined) is acceptable because "the enforcement mode ladder is in Advisory phase."

Team 3 is more rigorous here. A 0/0 initialization produces undefined behavior in the formula. The 0.5 prior is the correct Bayesian starting point. This is a trivial implementation detail but Teams should have agreed.

### Contradiction 3: EAT agentic draft status

Team 2 presents the draft as an active opportunity: "Submantle could contribute to shaping them."
Team 5 also cites the draft as evidence of a "first-mover opportunity at the standards level."

Neither team checked the expiration date (December 15, 2025 — expired before this expedition). The contradiction is not between teams but between both teams and reality. This is the most consequential factual error in the expedition: the standards opportunity framing is based on a document that has already lapsed.

---

## 3. Alignment Drift from Research Brief

### Drift 1: The research brief explicitly says "Do NOT suggest blockchain/crypto as the trust mechanism." Team 3 mentions ZK proofs as a V3 capability, which uses cryptographic techniques associated with blockchain contexts (zk-SNARKs, originally developed for Ethereum). This is not a violation — ZK proofs are a mathematical tool, not blockchain infrastructure — but Team 3 should have been more explicit that ZKP and blockchain are not the same thing. The brief's intent is to avoid Ethereum-style distributed ledgers, not to prohibit cryptographic proofs. No drift violation here, but the framing requires care when presenting to Guiding Light.

### Drift 2: The brief asks for "who's tried to build internet-scale trust before and what happened to them" as Outcome 1. Team 1 delivers this well. Teams 2-5 occasionally drift into recommending actions (Team 2: "Join W3C AI Agent Protocol Community Group," "Publish an IETF Individual Draft") that go beyond the brief's research scope. The brief says "research should identify what's needed, not prescribe premature implementation." The standards body engagement roadmap in Teams 2 and 5 is prescriptive rather than informational. Minor drift, but noted.

### Drift 3: Team 4's marketplace analysis is strong on the Visa/Starbucks/Progressive Snapshot analogies and maps well to the brief's Outcome 3 (how brands and marketplaces plug into trust infrastructure). No material drift. The competitive analysis specifically addresses the brief's "what's missing" question.

### Drift 4: Team 5 is explicitly a gap analysis — Outcome 4 and 5. It delivers both well. The critical path analysis (6 steps to MVTL) is the clearest, most actionable output in the entire expedition. It is within scope and appropriate.

---

## 4. Missing Angles

### Missing Angle 1: BBS+ cryptosuite finalization status

Every team that mentions selective disclosure relies on BBS+ as the implementation. No team verified whether BBS cryptosuites were included in the May 2025 W3C finalization or are still Candidate Recommendations. This is not a theoretical gap — it determines whether the privacy-preserving attestation model is buildable today with a stable standard or requires waiting for a specification that is not yet finalized.

### Missing Angle 2: HUMAN Security's actual behavioral model vs. Submantle's

Team 4 dismisses HUMAN Security as purely defensive without examining their behavioral trust methodology in depth. Given HUMAN Security's own language about "dynamic, ongoing decisions based on what the agent does," a deeper comparison — what signals they use, what their scoring model looks like, whether they have a portable trust credential — would have either validated or undermined the "gap is unoccupied" thesis more convincingly.

### Missing Angle 3: Mastercard + Google "new trust layer" for agentic commerce

Team 4 explicitly flags this in their own gaps section: "search results reference this specifically ('Mastercard and Google's new trust layer could reshape how AI buys for you') but details were not surfaced." This was identified as potentially a direct competitor or integration partner and then not researched. This is the single highest-priority unresolved research question from this expedition. If Mastercard and Google are building a portable behavioral trust layer for agentic commerce, the "no one is doing what Submantle does" thesis requires significant qualification.

### Missing Angle 4: OpenID Federation 1.0 finalization status

Team 5 mentions OpenID Federation 1.0 "entered its final review period December 2025–February 2026." As of March 2026, that review period has ended. The team did not verify whether OpenID Federation 1.0 has been published as a final specification or is still in review. This matters for Gap 8 (cross-instance trust federation).

### Missing Angle 5: The incident taxonomy — explicitly unresolved

Both Teams 3 and 5 flag the incident definition as the most critical unresolved design decision, and both leave it unresolved. The research brief does not explicitly ask for this, but the teams correctly identify it as blocking. Neither team proposed a draft taxonomy for Guiding Light to react to. Given that it's identified as the single highest-leverage design decision, failing to offer even a starter list of candidate incident types is a missed opportunity.

### Missing Angle 6: cheqd as a direct reference implementation

Team 5 cites cheqd multiple times as having already built MCP servers for VC issuance for AI agents. No team examined cheqd's implementation in depth — what their VC schema looks like, how they handle revocation, what their agent identity model is. If cheqd has already built most of what Gap 4 requires, Submantle may be able to adopt or extend their work rather than designing from scratch. This is a potentially large time savings that was not investigated.

---

## 5. Agreements (High-Confidence Zone)

The following claims were reached independently by multiple teams and have external evidence support:

**1. W3C VC 2.0 is the correct portable trust credential format.** Teams 2, 3, and 5 independently converged on this. External verification confirms the standard is finalized. Confidence: HIGH.

**2. RFC 9711 EAT is a real, published standard.** Teams 2 and 5 both cite it. Externally verified. Confidence: HIGH.

**3. The behavioral trust gap is real and structurally unoccupied at the OS/device layer.** Team 4's competitive sweep of 20+ companies, Team 2's protocol landscape table, and the research brief's own framing all converge. HUMAN Security's existence weakens but does not close this claim. Confidence: HIGH with caveat (the Mastercard/Google item is uninvestigated).

**4. Beta Reputation System (alpha/(alpha+beta)) is the right V1 algorithm.** Validated by the mae-principles expedition, confirmed by Team 3's literature review, cited by Teams 1, 4, and 5. Confidence: HIGH.

**5. Auth middleware is the single most blocking gap.** Teams 3 and 5 agree. The mae-principles expedition's validators agree. The logic is sound: without record_query() wired to the endpoint, no trust data accumulates and the formula always returns undefined. Confidence: HIGH.

**6. MCP is the right integration surface.** All five teams agree. Team 4 documents adoption at 97M+ monthly SDK downloads. The Linux Foundation governance makes it permanent infrastructure. Confidence: HIGH.

**7. Cold start is handled correctly by open access design.** Teams 1, 3, and 5 agree. The credit bureau and eBay precedents support this. Confidence: HIGH.

**8. Privacy-first on-device architecture is a genuine differentiator, not a constraint.** Teams 1 and 3 both make this case independently. The credit bureau comparison (behavioral trust that survived being hated because of network effects) and the Microsoft Recall backlash both support the on-device model's value. Confidence: HIGH.

---

## 6. Surprises

**Surprise 1: The agentic EAT draft expired.** The standards-track narrative assumes this draft is active. It is not, as of the expedition date. This reframes the IETF opportunity from "join an active process" to "revive or submit anew." That is a different — harder — path than Teams 2 and 5 describe.

**Surprise 2: HUMAN Security's behavioral framing is more sophisticated than Team 4 acknowledges.** The "trust is a dynamic, ongoing decision based on what the agent does" language from HUMAN Security's own product page is nearly identical to Submantle's design philosophy. The key distinction is layer (web application vs. OS) and portability (HUMAN's is per-website, not portable), but the behavioral model overlap is significant enough to warrant a deeper competitive analysis than Team 4 provided.

**Surprise 3: cheqd appears to have already shipped VC issuance for AI agents via MCP.** Multiple sources in Teams 3 and 5 confirm this. No team investigated what cheqd actually built. If cheqd's implementation is production-quality and compatible with Submantle's model, Gap 4 may have a reference implementation available rather than requiring original design.

**Surprise 4: Team 4's Google UCP analysis is stronger and more current than expected.** The January 2026 UCP launch with Shopify, Walmart, Target, Mastercard, and Visa is well-documented and the analysis that UCP handles commerce authorization while explicitly NOT handling behavioral trust scoring is a sharp observation. However, it creates the unresolved Mastercard/Google trust layer question (Missing Angle 3) that Team 4 identified but did not pursue.

---

## Overall Assessment

**Reliability tier by team:**

| Team | Finding Quality | Key Weakness |
|------|----------------|--------------|
| Team 1 (Historical) | HIGH | eBay inflation data is anecdotal but self-acknowledged |
| Team 2 (Protocol) | MEDIUM-HIGH | EAT draft expiration unchecked; OIDC-A sourced to a single author's blog |
| Team 3 (Trust Science) | HIGH | EigenTrust scalability argument slightly wrong; decay/V1 contradiction with Team 5 |
| Team 4 (Marketplace) | MEDIUM-HIGH | HUMAN Security underestimated; Mastercard/Google item uninvestigated; Decagon valuation unverifiable |
| Team 5 (Gap Analysis) | HIGH | Best-structured output; minor decay contradiction with Team 3 |

**Highest-confidence conclusions from the expedition:**
- Beta Reputation System is the right algorithm
- Auth middleware is the single most blocking gap
- W3C VC 2.0 is the right portable credential format (with BBS+ finalization status still to verify)
- The behavioral trust gap is real at the OS/device layer

**Requires follow-up before acting on:**
- Whether BBS cryptosuites are in the finalized W3C Recommendation set
- Mastercard + Google agentic trust layer — is this a direct competitor?
- What cheqd has already built for AI agent VC issuance via MCP
- Whether the EAT agentic draft can be revived or whether a new submission is needed

---

*Validated: 2026-03-10. External verification performed on W3C VC 2.0, RFC 9711, draft-huang-rats-agentic-eat-cap-attest-00, HUMAN Security AgenticTrust, and Zenity Series B funding.*
