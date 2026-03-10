# Expedition Synthesis: Behavioral Trust Layer
## Date: 2026-03-10
## Vetted by: Orchestrator
## Alignment: Checked against Research Brief

---

## High Confidence (teams converged, validators confirmed)

### 1. The Behavioral Trust Gap Is Real and Structurally Unoccupied

The strongest finding of the expedition. Teams 1, 2, 4, and 5 all independently confirmed — through historical precedent, protocol architecture, competitive analysis, and gap analysis respectively — that no existing protocol, product, or standard provides portable behavioral trust scoring for software agents.

- Team 2's protocol stack: MCP (communication), A2A (agent-to-agent), OAuth (auth), SPIFFE (identity). Behavioral trust = "NOTHING."
- Team 4's competitive sweep of 20+ companies: every player builds agents, frameworks, auth, security monitoring, or communication protocols. None builds the trust layer underneath.
- All 3 validators confirmed this finding as the expedition's strongest.

**Caveat (from validators):** The Mastercard/Google "new trust layer" partnership (January 2026) was identified by Team 4 as potentially relevant but NOT investigated. Until this is researched, the "unoccupied" claim carries an asterisk. Also, HUMAN Security's AgenticTrust is more behaviorally sophisticated than Team 4 acknowledged — the real distinction is layer (web application vs. OS/device) and portability (per-website vs. universal), not "defensive vs. constructive."

**Confidence: HIGH with one open question (Mastercard/Google).**

### 2. W3C Verifiable Credentials 2.0 Is the Right Portable Trust Format

Three independent teams (2, 3, 5) converged on W3C VC 2.0 as the format for Substrate Trust Attestations. The standard was finalized as a W3C Recommendation on May 15, 2025. All three validators confirmed this convergence as the expedition's highest-confidence technical finding.

**Caveat (from Validator 2):** BBS+ cryptosuites for selective disclosure (the "prove your tier without revealing your data" feature) were NOT among the seven specifications finalized in May 2025. Two specifications remained as Candidate Recommendations. Whether BBS+ is one of them is unverified. The privacy-preserving tier proof architecture depends on BBS+ being stable. This is a "verify before building" item, not a blocker for the overall VC direction.

**Confidence: HIGH for VC 2.0 as format. MEDIUM for BBS+ selective disclosure specifically.**

### 3. Beta Reputation System Is the Right V1 Algorithm

Teams 3 and 5 validated independently, aligned with the mae-principles expedition. The formula: trust = total_queries / (total_queries + incidents). Confirmed by Josang 2002, IoT/MANET/P2P production systems, and three independent research passes.

**Critical resolution (Team 3 vs. Team 5):** Team 5 proposed a three-signal composite formula (TEMPORAL + BEHAVIORAL + OPERATIONAL). All three validators flagged this as over-engineering the prototype. Team 3's pure Beta formula is the correct V1 choice. The three-signal approach belongs in V2 after baseline behavioral data exists.

**Cold start initialization:** Team 3's recommendation of (1,1) = 0.5 "unknown" Bayesian prior is correct. A 0/0 initialization produces undefined behavior in the formula.

**Confidence: HIGH for pure Beta. Team 5's composite FILTERED for V1.**

### 4. Auth Middleware + record_query() Are the Most Blocking Gaps

Teams 3 and 5, plus the mae-principles expedition validators, all identified the same two missing pieces: record_query() is never called, and /api/query has no auth middleware. Without these, no trust data accumulates and the formula always returns undefined. Three independent research passes reaching the same conclusion about the same missing code.

**Confidence: HIGH.**

### 5. Open Access Design Correctly Handles Agent-Level Cold Start

Teams 1, 3, and 5 independently confirmed through different research angles (credit bureau history, Bayesian statistics, gap analysis) that Substrate's "register to earn benefits, not to participate" design is the correct cold start answer.

**Caveat (from Validator 3):** Agent-level cold start is handled. Platform-level cold start (Substrate itself has no registered agents, no brand partners, no demonstrated trust economy) is a separate chicken-and-egg problem requiring market development strategy, not a formula adjustment. No team addressed this.

**Confidence: HIGH for agent cold start. UNADDRESSED for platform cold start.**

### 6. Sybil Resistance by Locality Is a Genuine Architectural Advantage

Team 3's novel finding: Substrate's local-only trust computation makes distributed Sybil attacks structurally irrelevant because there is no global score to influence from outside the device. Validator 1 called this "genuinely novel and strong." Validator 3 confirmed it should be documented as a design principle.

**Caveat (from Validator 3):** Team 3 simultaneously claims Sybil resistance is "solved by locality" AND that it's a "known sacrifice in the trilemma." These are incompatible. The resolution: distributed Sybil attacks are neutralized by locality. Local self-gaming (device owner inflating own scores) is a separate vulnerability that no team mitigated. This matters for the trust economy.

**Confidence: HIGH for distributed Sybil resistance. UNADDRESSED for local self-gaming.**

---

## Battle-Tested Approaches (proven patterns with production evidence)

### 7. Credit Bureau Model Is Substrate's Closest Ancestor

Team 1 mapped credit bureau architecture to Substrate's design and found deep structural parallels: behavioral observation, score computation from observed actions, tiered access based on score, portability of score across providers. The credit bureau model survived being hated (Equifax breach, score opaqueness) because of bilateral dependency: lenders need scores, borrowers need credit. Substrate's flywheel works the same way: brands need trust signals, agents need trust credentials.

**Key lesson:** Every trust system that reached internet scale shares one property — the trust mechanism was invisible to the end user and mandatory for participants. Certificate Transparency is the architectural ancestor for trust logging.

### 8. Progressive Snapshot Is the Best Product Analogy

Team 4 surfaced this and Validator 1 elevated it above the credit bureau comparison. Progressive Snapshot: observe driving behavior -> score safety -> adjust insurance rate -> create economic incentive for safer driving. Average savings: $322/year for safe drivers. This is exactly Substrate's loop: observe agent behavior -> score trust -> adjust transaction rates -> create economic incentive for trustworthy behavior. It's more visible to consumers, better understood as a product mechanic, and more easily explained than credit bureaus.

### 9. The Visa Model for Trust Intermediation

Team 4's strongest marketplace finding: Substrate as trust intermediary, not risk-taker. Visa doesn't hold money or make loans. It provides the trust infrastructure that connects merchants and cardholders. Bilateral dependency flywheel: merchants need verified customers, customers need accepted cards. Neither can leave without losing access to the other side.

---

## Novel Approaches (unconventional ideas with theoretical backing)

### 10. Google's Universal Commerce Protocol NEEDS Substrate

Team 4 found that Google's UCP (January 2026, backed by Walmart/Target/Shopify/Mastercard/Visa) explicitly does NOT solve behavioral trust. "Protocols regulate how agents interact, not which agents should be trusted." UCP handles commerce authorization. Substrate handles the trust scoring that makes authorization decisions meaningful. This is a natural integration point, not a competitive threat.

### 11. Standards Window Is Open — But Requires New Submission

Team 2 identified IETF RFC 9711 (Entity Attestation Token) as the right base for behavioral trust attestations. However, Validator 2 caught a critical factual error: the agentic EAT extension draft (draft-huang-rats-agentic-eat-cap-attest-00) EXPIRED December 15, 2025. Teams 2 and 5 presented this as an active standards opportunity. It is not. The opportunity is real but requires submitting a NEW individual draft to IETF, not joining an existing process. Different — harder — path than described.

### 12. cheqd as Reference Implementation (Not Just Validation)

Team 5 cited cheqd as having already built MCP servers for VC issuance to AI agents. Validator 1 elevated this: cheqd has a working implementation of MCP-integrated VC infrastructure. Substrate could potentially extend or integrate with cheqd's work rather than building VC issuance from scratch. No team investigated what cheqd actually built. This deserves attention before committing to a full custom implementation.

**Also flagged as potential competitor (Validator 3):** If cheqd pivots from VC issuance infrastructure into behavioral trust scoring, they'd be the closest direct competitor.

---

## Emerging Approaches (gaining traction, not yet proven at scale)

### 13. Zero-Knowledge Proofs for Privacy-Preserving Trust Verification (V3+)

Teams 2 and 3 identified ZKPs as the future mechanism for agents to prove trust tier without revealing behavioral data. Deferred to V3 due to computational overhead concerns. However, Validator 1 flagged that the deferral is based on intuition, not measurement — no team benchmarked actual ZKP computation cost on consumer hardware. The deferral is likely correct but not evidence-based.

---

## Synthesized Recommendation

Based on vetting all findings against the Research Brief, validator challenges, and project constraints, here is what Substrate should build and in what order:

### The Minimum Viable Trust Layer (MVTL)

Team 5's critical path, corrected by validator feedback:

1. **Auth middleware on /api/query** — Token-based, wired to agent registry
2. **Incident taxonomy definition** — Product decision: what specific agent behaviors constitute an incident (this is iterative, not one-shot)
3. **record_query() wired to endpoints** — Every agent interaction becomes trust data
4. **Agent name uniqueness enforcement** — Prevents trivial identity confusion
5. **compute_trust() using pure Beta formula** — trust = total_queries / (total_queries + incidents), initialized at (1,1) = 0.5
6. **Trust score exposed in API responses** — Agents see their own score; querying agents see scores of registered agents

Steps 1-5 require zero new dependencies. Step 6 is a schema/API change.

**What was filtered from Team 5's MVTL:**
- Three-signal composite formula (over-engineers prototype; V2 after baseline data)
- Temporal decay component (no basis for choosing parameters without real data)
- "One session" effort estimate (aspirational, not benchmarked; incident taxonomy alone is iterative)

### The Trust Attestation Layer (Post-MVTL)

- W3C VC 2.0 format for Substrate Trust Attestations
- Verify BBS+ cryptosuite finalization status before committing to selective disclosure
- Investigate cheqd's MCP VC implementation before building from scratch
- VC revocation mechanism must be designed (no team solved this; it's blocking for attestations)

### The Standards Path (Background, Not Blocking)

- IETF RFC 9711 EAT is the right base
- Agentic extension draft expired — requires new submission if Substrate wants to define the standard
- W3C AI Agent Protocol Community Group exists for engagement
- MCP's Linux Foundation governance makes it permanent infrastructure

---

## Disagreements

### 1. V1 Formula: Pure Beta vs. Three-Signal Composite
**Team 3:** Pure Beta only. Defer multi-dimensional scoring to V2.
**Team 5:** Three-signal composite (temporal + behavioral + operational).
**All 3 validators:** Team 5's composite over-engineers the prototype.
**Resolution:** Pure Beta for V1. Team 5's approach is deferred to V2 with data to inform weights.

### 2. Trust Decay Timing
**Team 3:** Do not implement decay. Wait for real data distributions.
**Team 5:** Include temporal signal (days since registration) in V1.
**Validators 1 and 2:** Team 3 is correct. Implementing temporal weighting before baseline data exists means choosing weights blindly.
**Resolution:** No decay in V1. Use last_seen as a freshness indicator only (not a score component).

### 3. Go Rewrite Timing
**Team 5:** Before first external adoption.
**Team 2:** Before W3C VC issuance with BBS+ (Python crypto libraries immature).
**Team 3:** V3 consideration for ZKP libraries.
**Validator 3:** Team 5 contradicts itself — says "before external adoption" but also "not needed for MCP integration or brand partnerships" which ARE external adoption.
**Resolution:** No single trigger. Monitor concurrent agent load, crypto library needs, and API surface commitments independently.

---

## Foundational Tension: "Always Aware, Never Acting"

This is the most consequential unresolved question from the expedition. All three validators independently flagged it. No team addressed it.

**The problem:** Substrate's design principle is "always aware, never acting — provides knowledge, doesn't act." The trust layer, as designed by the teams, includes mechanisms that ARE actions: blocking agents (Hard Gate), changing transaction rates based on score, throttling queries (velocity caps), gating access to features. These are not awareness. They are interventions.

**Why it matters:** Either the principle is modified for the trust layer context, or the enforcement mechanisms must be redesigned so Substrate only EXPOSES the trust signal and third parties decide whether to act on it.

**The two possible resolutions:**
1. **Scope the principle:** "Always aware, never acting" applies to the awareness layer (process scanning, event observation). The trust layer is a different context where Substrate provides scored signals AND third parties enforce them. Substrate doesn't block agents — brands and platforms set their own thresholds using Substrate's scores.
2. **Redesign enforcement:** Substrate only provides trust scores. Rate changes, access gating, and blocking are all implemented by the consumers of trust data (brands, platforms, other agents), never by Substrate itself.

**This must be resolved before the trust layer is built.** The answer determines whether Substrate is extending its architecture or contradicting its foundation.

---

## Filtered Out (what I removed and why)

| Finding | Source | Why Filtered |
|---------|--------|--------------|
| OIDC-A as protocol direction | Team 2 | Single-author blog post, no standards traction, no implementations. Validator 1 confirmed: do not build against it. |
| Standards participation strategy (4-step roadmap) | Team 2 | Strategic roadmapping, not research findings. Useful context but exceeds Brief scope. |
| Three-signal V1 formula | Team 5 | Over-engineers the prototype. All 3 validators flagged. Pure Beta is validated. |
| IETF EAT draft as "active opportunity" | Teams 2, 5 | Draft expired December 15, 2025. Caught by Validator 2. The opportunity exists but requires a NEW submission. |
| EigenTrust scalability rejection rationale | Team 3 | Conclusion correct (don't use EigenTrust) but the scalability argument is wrong per Validator 2. Correct reason: requires pre-existing trust graph Substrate doesn't have. |
| "One session" effort estimate for MVTL | Team 5 | Aspirational. Incident taxonomy alone is iterative design work requiring multiple cycles. Validator 3 confirmed. |
| eBay inflation as hard evidence | Team 1 | Self-acknowledged by Team 1 as anecdotal. The pattern holds across other cases (Amazon, Steam) so the lesson is valid even without eBay specifics. |
| Starbucks "60% of revenue" from loyalty | Team 4 | Validator 1 flagged: figure refers to transactions, not revenue. Approximate, not precise evidence. The loyalty mechanics lesson is valid regardless of exact percentage. |

---

## Risks

### 1. The Incident Definition Is the True Blocker
Every team identified it. No team proposed a draft taxonomy. Validator 3: "The incident definition determines what the Beta formula measures. If defined too narrowly, every error-free agent gets perfect trust. If too broadly, legitimate high-frequency agents are penalized." This requires iterative calibration against real behavioral data that doesn't exist yet. It is not a one-shot design decision.

### 2. VC Revocation Is Unsolved
If Substrate issues a trust VC and the agent's behavior deteriorates, how is the credential revoked without creating a global revocation list that reveals which agents have been penalized? Team 2 flagged this. No team answered it. W3C StatusList2021 and Bitstring Status List exist but their privacy tradeoffs were not evaluated. This is blocking for the attestation layer.

### 3. Platform Cold Start Is Not Addressed
Agent-level cold start is solved (open access + Beta prior). Platform cold start (who builds the first 30 integrations, who are the first brand partners, what makes agents register before there's a trust economy to benefit from) requires market development strategy. No team addressed this despite Validator 3 flagging the solo founder constraint.

### 4. Regulatory Risk Is Unresearched
EU AI Act (August 2026 deadline per project memory). FCRA-style implications for behavioral scoring. GDPR for behavioral data even when on-device. No team researched these. Team 1 correctly notes regulation is "when, not if." The timeline is live, not theoretical.

### 5. Local Self-Gaming Is Unmitigated
A device owner can run high-frequency benign queries from their own agents to inflate trust scores. This is not a Sybil attack (legitimate identity, single device) and doesn't violate any architectural constraint. But it undermines the trust economy. No team proposed a mitigation.

### 6. HUMAN Security Is a More Sophisticated Near-Competitor Than Acknowledged
Their own language: "Trust is not a score, a label, or a rule; trust is a dynamic, ongoing decision based on what the agent does." The real gap between them and Substrate is layer (web application vs. OS) and portability (per-website vs. universal), not sophistication. A product pivot from HUMAN Security could close the gap.

---

## Open Questions Requiring Follow-Up

1. **Mastercard/Google "new trust layer" partnership** — Is this a direct competitor? Highest-priority open question.
2. **BBS+ cryptosuite finalization** — Is it in the W3C Recommendation set or still Candidate?
3. **cheqd's actual implementation** — What did they build? Can Substrate extend it?
4. **IETF EAT agentic draft revival** — Can the expired draft be revived, or does Substrate need to submit new?
5. **EU AI Act implications** — Does behavioral trust scoring trigger high-risk AI classification?
6. **Solo founder feasibility** — No team addressed the Brief's explicit question about this.

---

*Synthesis completed: 2026-03-10. Vetted against Research Brief, 5 team findings, and 3 independent validator reports.*
