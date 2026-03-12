# External Researcher Challenge: Phase 2
## Date: 2026-03-12
## Role: External Researcher
## Council: Scoring Model V2

---

## Overview

I have reviewed both the Codebase Analyst's findings and the Devil's Advocate's findings in full. This challenge identifies where the three perspectives diverge, where they converge, and what each missed that changes the shape of the design decision. I will be specific about scores, claims, and source evidence.

---

## 1. Reasoning Divergence Points

### Divergence 1: The Float-in-Beta-Formula Problem — The Devil's Advocate Is Correct, But for the Wrong Reason

The Devil's Advocate raises "Risk 2" (medium severity): `formula_weight REAL` on `incident_reports` means `i` in the Beta formula becomes a float sum, breaking the integer-parameter derivation. The Codebase Analyst's proposal (Step 7) treats this as unproblematic — "The formula is 3 lines" — and proposes `effective_incidents = SUM(formula_weight)` without addressing the mathematical underpinning.

**Where the reasoning chains diverge:** The Codebase Analyst is analyzing implementation feasibility (3 lines change, blast radius contained). The Devil's Advocate is analyzing mathematical correctness (integer vs float Beta parameters). Both are right on their own terms.

**What external precedent clarifies:** D&B PAYDEX's formula is a dollar-weighted average — it explicitly sums floating-point values (percentages of dollar amounts by payment class). PAYDEX does not claim to be a Beta distribution. It claims to be a weighted payment index. The moment Submantle's formula moves to `SUM(formula_weight)` for `i`, it should stop calling itself "the mean of Beta(alpha, beta)" in its docstring — because it isn't anymore. It becomes a Beta-inspired weighted ratio.

**This is not catastrophic.** The arithmetic works. The score has a valid 0–1 range. The behavior is sensible (lower weight incidents hurt less). But the Devil's Advocate is correct that the docstring becomes a lie. The fix is a docstring update plus a deliberate decision: "We are using a Beta-inspired formula. The float inputs are intentional. The theoretical derivation no longer strictly applies." FICO 10T added trended data and made exactly this kind of quiet departure from its original theoretical grounding — it still works in practice.

**Score challenge:** The Devil's Advocate rates this "Failure Severity: 5/10 (medium)." I agree with the identification but think 5/10 slightly overstates the operational risk. A miscalibrated-but-consistent score is a design decision, not a system failure. The real severity is the risk of claiming a theoretical property (Beta distribution mean) that no longer holds after adding float inputs. I'd rate this 3/10 severity once the docstring is corrected and the design decision is explicitly documented.

---

### Divergence 2: Reporter Credibility Bootstrapping — The Devil's Advocate Understates the Solution Already in My Findings

The Devil's Advocate identifies "Risk 3" (HIGH): reporter credibility circular dependency, no bootstrapping solution specified. This is listed as a high-priority unresolved risk. The Codebase Analyst lists reporter credibility as a prerequisite chain (steps 7-9 in the dependency chain) but does not propose a mechanism.

**Where the reasoning chains diverge:** Both analysts treat bootstrapping as an open problem. My Phase 1 findings (Section 2.4, PeerTrust) directly resolved this:

- New reporters initialize at Beta(1,1) = 0.5 credibility — the same initialization as new agents
- This means a new reporter's first incident report contributes `base_severity_weight × 0.5` to the formula — half weight, not zero
- As reports are accepted or expire, the reporter's credibility moves toward 1.0 (accurate) or 0.0 (unreliable)
- D&B's alternative solution: don't treat a score as authoritative until reporter_diversity ≥ 2

The Devil's Advocate is correct that "the first N incidents any reporter files effectively shape their credibility for all future incidents." But this is also true of agents being scored — a new agent's first few interactions matter disproportionately until sufficient history accumulates. The Beta formula's design accepts this property. The early-period bootstrapping issue is a feature of the Beta prior (1,1), not a flaw in the design.

**What the Devil's Advocate missed:** The paper Beta-PT (PLOS One 2024), which I cited, explicitly addresses this: "introduces mild penalties for newcomers while damping the influence of overactive reviewers." The newcomer penalty (starting at 0.5 credibility rather than 1.0) is the correct behavior. It means: trust new reporters cautiously, then build trust through track record. This is identical to how Submantle treats new agents. Consistent by design.

**Score challenge:** The Devil's Advocate rates this "HIGH" risk. Based on external evidence, I would lower this to MEDIUM. The bootstrapping solution exists and is well-grounded. The residual risk is that early reporters who aggressively file reports during their low-credibility period may establish bad habits that persist — but this is dampened precisely because those early reports have 0.5× weight applied.

---

### Divergence 3: FICO Version Fragmentation — The Devil's Advocate Treats It as a Failure Mode; External Evidence Treats It as the Correct Pattern

**The Devil's Advocate claim (Risk 4):** "FICO's history shows recalibration rarely happens. Submantle will accumulate a fragmented ecosystem of brands comparing incomparable scores within years of launch."

**My Phase 1 findings (Section 1.1, FICO Version Coexistence):** FICO's 16 simultaneous versions are not presented as a failure. They are presented as the operationally standard pattern. The reason version coexistence exists is specifically to prevent brands from being forced into disruptive threshold recalibration. The Devil's Advocate is reading the same evidence and reaching the opposite conclusion from mine.

**Where the reasoning chains diverge:** The Devil's Advocate frames version fragmentation as brands making incomparable decisions. My research frames version coexistence as brands preserving working business logic while Submantle improves the formula. Both framings are accurate descriptions of the same phenomenon.

**What external evidence settles this:** VantageScore was created precisely because lenders wanted a version-coexisting alternative to FICO. 41.7 billion VantageScore scores were used in 2024 (up 55% YoY) — coexisting with FICO versions — without anyone treating this as a fragmentation crisis. SecurityScorecard does quarterly recalibrations with advance notice, simultaneous rollout, and no version branching — the alternative model. Both work. They serve different needs.

**The real question for Submantle:** Which model fits V1? My recommendation remains FICO version fork, not SecurityScorecard simultaneous recalibration. The reason: Submantle's early brands will be building trust thresholds for the first time. They cannot pre-test against a new formula because they have no existing threshold to compare against. Version forking gives them stability by default. Simultaneous recalibration punishes early adopters who built threshold logic during the V1 period. For V1, there are no existing adopters to protect — but designing for the transition to V2 correctly is the point.

**Score challenge:** The Devil's Advocate scores "Weight versioning creates FICO-style fragmentation" as MEDIUM risk. I disagree with the framing. Version coexistence is not a bug to mitigate — it is the correct protocol to implement. The risk the Devil's Advocate is actually identifying is: "brands will not voluntarily upgrade to V2 when it's better." This is real, but it is a product adoption problem, not a scoring design failure. The answer is not to avoid versioning; it is to make V2 compelling enough that brands want to upgrade.

---

### Divergence 4: SecurityScorecard Simultaneous Recalibration vs. FICO Version Fork — A Gap Neither Agent Addressed

**The Codebase Analyst's Step 5** identifies the `settings` table as the right home for weight versioning but does not specify the recalibration model (simultaneous vs. fork). The Devil's Advocate attacks the versioning concept without distinguishing between the two models.

**What external evidence provides:** SecurityScorecard's quarterly simultaneous recalibration (all entities get new scores at once, advance notice provided, API schema unchanged) is specifically designed for the case where brands care about score accuracy more than score stability. FICO's version fork is designed for the case where brands care about threshold stability more than score accuracy.

For Submantle V1-to-V2 transition, the choice between these models is a product decision that neither internal analyst raised. The council should make this explicit. My recommendation (from Phase 1 findings, Section 3.1): FICO version fork, not SecurityScorecard simultaneous recalibration — because the first brands to build on Submantle scores should not find their thresholds silently recalibrated when V2 ships.

---

### Divergence 5: The Codebase Analyst's Trust in `trust_metadata` — More Optimistic Than Warranted

The Codebase Analyst's Finding 1 calls `trust_metadata` "ready now — use it immediately" and rates this as zero-prerequisite work. The Devil's Advocate does not challenge this.

**External precedent that complicates this:** Every production reputation system (eBay, Airbnb, SecurityScorecard) treats metadata as a display layer, not a formula input. The Codebase Analyst correctly observes this architecture (two-track: formula score + metadata). But the framing "use it immediately" implies we can start writing velocity data, query type breakdowns, and reporter concentration flags to `trust_metadata` now without those signals being validated.

**The risk:** Submantle is in a period with zero real-world data on what interaction patterns look like. Any signal we write to `trust_metadata` today will train brands to build logic on unvalidated data. FICO does not include a new category in its published weights until it has validated the signal against millions of real credit files.

**My position:** Writing signals to `trust_metadata` is low-risk precisely because it is display-only and does not affect the formula. The Codebase Analyst is right that there is no technical risk. But we should be explicit that signals in `trust_metadata` are "data under observation, not validated scoring dimensions." Brands should know the data is there but unvalidated. A `metadata_maturity: experimental | validated` field per dimension would be the right pattern here — a distinction that neither analyst raised.

---

## 2. Score Challenges

### Challenge A: Devil's Advocate "Failure Probability: 4/10"

The Devil's Advocate rates overall failure probability at 4/10 (fairly likely to fail). My basis for disagreement: the two highest-probability failure mechanisms — (1) two sources of truth for incident count, and (2) reporter credibility circular dependency — both have specified solutions in the external research. If those solutions are adopted, the failure probability drops materially.

**The two sources of truth problem** is only a problem if `compute_trust()` is not refactored to read from `incident_reports WHERE status='accepted'`. The Codebase Analyst's dependency chain (Step 8, specifically step 3) sequences this correctly: pending state on `incident_reports` must exist before the formula changes. This is a sequencing discipline problem, not a design flaw.

**My revised assessment:** Failure probability is 2-3/10 if the implementation follows the Codebase Analyst's sequencing. It is 5-6/10 if implementation shortcuts the sequencing and leaves both code paths alive simultaneously. The score should be contingent on sequencing discipline, not fixed.

### Challenge B: Codebase Analyst "Evidence Confidence: 9/10"

The Codebase Analyst rates evidence confidence at 9/10, noting "all claims reference specific file lines, verified by direct file reads and Grep." This confidence level is fully justified for the technical claims. I do not challenge this score.

However, the Codebase Analyst's scores are exclusively about implementation feasibility — blast radius, pattern consistency, dependency risk. The 9/10 evidence confidence does not transfer to the design quality of the proposed weighted dimensions themselves. The council should not interpret "implementation is feasible with high confidence" as "the dimension design is well-validated."

### Challenge C: Devil's Advocate "Assumption Fragility: 3/10" (Low = Fragile)

The Devil's Advocate marks 5 of 8 assumptions as unverified. My research directly addresses three of them:

1. **"`formula_weight` (float) can be substituted into a formula originally derived for integer Beta distribution parameters"** — Marked UNVERIFIED. External evidence: D&B PAYDEX (float-weighted averages in a scoring formula not derived for integer parameters) has worked for decades. This is PARTIALLY VERIFIED once we accept the docstring must be updated.

2. **"Reporter credibility can be computed without circular bootstrapping problems"** — Marked UNVERIFIED. External evidence: PeerTrust Cr(v) mechanism + Beta initialization at (1,1) provides the solution. This is VERIFIED with the half-weight newcomer treatment.

3. **"Adding more weighted dimensions produces a more meaningful score"** — Marked PARTIALLY VERIFIED. My research provides both supporting evidence (SecurityScorecard's breach-correlation: F-rated companies are 13.8× more likely to breach) and complicating evidence (eBay 2008 rating inflation). The correct nuance: more dimensions improve signal if they are observational (SecurityScorecard finds security issues), but cause gaming and inflation if they are directly controllable by the rated party (eBay sellers learning to optimize sub-ratings). Submantle's dimensions split across these categories: incident severity (not agent-controlled) vs. interaction diversity (agent-controlled). The gaming risk applies to the latter, not the former.

**Revised assessment:** Assumption fragility is 4-5/10 (not as fragile as the Devil's Advocate asserts), with the caveat that the agent-controlled dimensions (query diversity, interaction type) require the anti-gaming rules the Devil's Advocate correctly flags.

---

## 3. Evidence Gaps

### Gap 1: Neither Agent Addressed Score Time Decay — But External Evidence Flags It as Load-Bearing

My Phase 1 findings identified D&B PAYDEX's rolling window behavior as a design choice Submantle has implicitly rejected (Beta is cumulative, not rolling). The Devil's Advocate does not address this at all. The Codebase Analyst does not address this at all.

**What external evidence establishes:** D&B's rolling window and Airbnb's recency weighting (2025 Summer Release down-weighted historical ratings in favor of last 90 days) are production responses to a specific failure mode: high-reputation entities can behave badly for a long time before their score reflects the change. SecurityScorecard addresses this differently — quarterly recalibrations that re-score all entities on current findings, not historical ones.

**For Submantle, this is the "compromised agent" scenario.** An agent that earned 0.92 trust through 5,000 clean interactions and then gets exfiltrated (or transferred to a malicious actor) will take many interactions to score down from 0.92 to a dangerous threshold. Under Beta with `q=5000, i=0` baseline, even 50 additional incidents would only move the score to `5001/5053 = 0.989` (already wrong). Wait — that math is wrong in the naive direction. Let me correct: if a previously-trusted agent had `q=5000, i=0` giving `5001/5002 = 0.9998`, then 50 new incidents brings it to `5001/5052 = 0.990`. Still very high. This is the score-inertia problem for high-history agents.

This is a known failure mode in all cumulative scoring systems. The council has not specified a mitigation. My recommendation: this is a V2 problem, but the data collection to diagnose it (timestamped incidents, timestamped queries) must be built in V1. The `expires_at` field on incident reports partially addresses this — but only for incidents, not for the query accumulation.

### Gap 2: Neither Agent Addressed the Qualys Multiplicative-Additive Hybrid in Relation to Severity × Credibility Composition

My Phase 1 findings (Section 3.4) identified the Qualys TruRisk formula as a precedent for multiplicative composition at the top level (asset criticality multiplies everything) with additive composition across severity tiers. This directly answers how severity and reporter credibility should compose when both apply to the same incident.

The Devil's Advocate (Section 2b) asks: "A 0.5-severity incident from a 0.7-credibility reporter: does it contribute 0.35 to `i`? 0.5? 0.7? This is unspecified." This is a real gap in the proposal.

**External evidence answer:** Qualys's multiplicative-additive pattern says: `effective_weight = severity_weight × reporter_credibility`. A 0.5-severity incident from a 0.7-credibility reporter contributes 0.35 to `i`. This is the same pattern Qualys uses (vulnerability severity × asset criticality). The multiplication is intentional — both factors must be strong for the incident to carry full weight. Neither analyst connected this precedent to the question.

### Gap 3: The Devil's Advocate Missed the SecurityScorecard ML-at-Classification, Determinism-at-Scoring Distinction

The Devil's Advocate raises "Risk 5" (MEDIUM): reporter credibility weighting where weights are derived from behavioral history may cross from "rules defined by natural persons" into "system that derives patterns from data" for EU AI Act purposes.

**What external evidence provides:** SecurityScorecard explicitly uses ML to identify and classify findings (what is a security issue), but the scoring formula is pure deterministic arithmetic applied to those classified findings. This is documented in their ML white paper (cited in my findings). The Commission's "rules defined by natural persons" boundary applies to the scoring formula layer, not the data classification layer.

For Submantle: the severity classification rules ("data_exfiltration = critical, rate_limit_violation = standard") are rules written by natural persons. The reporter credibility computation (`Beta(accepted+1, expired+1)`) is arithmetic applied to observable counts. Neither uses ML or learns from data. Both are deterministic at the scoring layer.

The Devil's Advocate's EU AI Act concern is legitimate as a general caution but overstated for Submantle's specific design. The risk rating of MEDIUM may be too high. The EU AI Act concern would be valid if reporter credibility were computed via a trained model or parameter-fitting against historical data — which is explicitly not what PeerTrust Cr(v) does.

### Gap 4: Both Agents Under-Addressed the D&B Two-Reporter Minimum and Its API Implication

My Phase 1 findings proposed a `reporter_diversity` field in the API response as a direct analog to D&B's two-reporter minimum. Neither analyst addressed this. The Codebase Analyst's response shape section (Step 1e) lists missing fields but does not include `reporter_diversity`. The Devil's Advocate does not address it.

**This is commercially significant.** A brand receiving a trust score of 0.87 based on a single reporter's absence-of-incidents (no one has reported anything, so the score defaults high) is making a different decision than a brand seeing 0.87 based on reports from 12 distinct reporters. D&B treats these as categorically different data quality levels — the single-reporter case does not even produce a score. Submantle should surface this as metadata. It costs one SQL COUNT(DISTINCT reporter_agent_id) in `compute_trust()`.

---

## 4. Agreements — High-Confidence Convergence

Where all three independent analyses converged, the council should treat these as settled:

### Agreement 1: Two Sources of Truth for Incident Count Is the #1 Implementation Risk

The Devil's Advocate (Risk 1, HIGH), the Codebase Analyst (Finding 3, "incidents counter is a liability in disguise"), and my external research all identify the mutable `incidents` counter in `agent_registry` as the primary risk vector. If the formula continues to read this counter while the proposal adds `formula_weight` to `incident_reports`, the weighted scoring system is built on a bypassed foundation. Triple convergence: this must be resolved before weighted scoring ships.

### Agreement 2: Pending State Must Precede the Formula Change

The Codebase Analyst's dependency chain (step 3 → step 4) and the Devil's Advocate's migration trap description both agree that the formula cannot safely change until `incident_reports` has a `status` column with `pending`/`accepted` states. My external research supports this with the eBay DSR precedent: the dimension infrastructure must exist before the formula can reference it. Triple convergence.

### Agreement 3: Record Interaction Types Now, Weight Later — Still Correct

All three analyses independently affirm the prior council's settled decision. The Codebase Analyst notes it requires `interaction_logs` infrastructure. The Devil's Advocate implicitly accepts it (their counter-evidence is against adding formula complexity now, not against recording data). My research confirms it with VantageScore 4.0's precedent. Triple convergence: this remains the right call.

### Agreement 4: `trust_metadata` Is the Right Home for Enrichment Signals

The Codebase Analyst (Finding 1), the Devil's Advocate (does not challenge this), and my research (Airbnb's two-track architecture) all converge on `trust_metadata` as the display-only enrichment layer that does not affect the formula. The infrastructure is already built. Writing to it is additive. Triple convergence.

### Agreement 5: Corroboration Should Be Visible, Not Multiplied Into the Formula

The Devil's Advocate explicitly endorses (Step 6, item 2) the design where multiple reporters on one incident = 1 score hit but `corroboration_count` visible to brands. My research agrees (eBay's design: feedback count is the score, DSRs are separate signals). The Codebase Analyst's schema proposal includes `corroboration_count` as a column. Triple convergence.

---

## 5. Surprises — What Changed My Thinking

### Surprise 1: The Devil's Advocate's Severity-as-Processing-Path Claim Is More Convincing Than I Expected

The Devil's Advocate's Step 6, item 5: "Severity classification as a processing-path determinant, not a formula weight" — severity determines which tier processes an incident, not the formula impact. The argument: severity affecting processing path = deterministic rules; severity affecting formula input weight = the float-in-integer-formula problem.

Before reading this, my Phase 1 findings fully embraced severity as a `formula_weight` modifier (Approach D: "incidents_weighted = Σ(formula_weight per incident)"). After reading the Devil's Advocate's challenge, I find the processing-path-only argument stronger than I would have predicted.

**My revised position:** Severity as a routing mechanism (critical incidents go to Tier 1 human review immediately, standard incidents expire in 14 days) is cleaner than severity as a formula weight. The formula weight approach introduces the float-in-Beta problem and requires calibrating weights without outcome data. The routing approach uses severity as a workflow signal without changing the formula's mathematical properties.

However, the two approaches are not mutually exclusive in the long run. For V1, severity as routing is the right call. For V2 (Go rewrite), severity as `formula_weight` can be added once outcome data validates the calibration. This is a partial reversal of my Phase 1 recommendation that the council should note.

### Surprise 2: The Codebase Analyst's Soft-Delete Naming Collision Is More Consequential Than Either Expected

The Codebase Analyst's Finding 4 identifies the naming collision problem: with soft-delete, deregistered agents still occupy the unique name slot. The test `test_deregister_then_reregister_same_name` breaks. The Codebase Analyst presents three options and notes "the prior council's recommendation requires option (a)."

**What neither analyst surfaced:** In the credit bureau model, you do not un-create a file. Equifax does not delete a credit file when someone's credit history is inactive. The file persists, potentially forever. If Submantle truly is a credit bureau for agents, the correct behavior is: deregistered agents keep their file, and re-registration with the same name under a different key is treated as a new entity (separate file). The naming conflict is a feature, not a bug — it prevents bad actors from deregistering a compromised agent and re-registering it with a clean slate. My Phase 1 research on D&B's business entity model confirms this: D&B's D-U-N-S numbers are permanent and never reused.

This reframing suggests option (c) from the Codebase Analyst's list ("prohibit re-registration with a deregistered name") may be more aligned with the credit bureau model than the prior council's recommendation ("re-registration inherits history"). This is a design decision that needs explicit council attention.

### Surprise 3: My Own Synthesis May Have Over-Proposed for V1

My Phase 1 synthesis proposed four layers: Beta formula with float inputs, input quality guards (velocity caps + reporter credibility), `trust_metadata` enrichment, and a divergence multiplier for V2. Reading the Devil's Advocate's challenge, I notice my Layer 2 ("reporter credibility used for formula_weight modifier") is what the Devil's Advocate identifies as unready for V1 — not because the mechanism is wrong, but because reporter credibility requires interaction history infrastructure that doesn't exist yet.

The Codebase Analyst's dependency chain confirms this: reporter credibility (step 9) depends on reporter_agent_id FK (step 8), which depends on interaction_logs table (step 7), which is currently nonexistent. My Phase 1 synthesis placed reporter credibility in "V1 ship requirement" (Layer 2). The internal evidence suggests it belongs in "V2 / Go rewrite" (Layer 4) alongside the divergence multiplier.

**Corrected synthesis for V1:** The formula change should be limited to: (1) velocity-capped query counts, (2) `status='accepted'` filtering on incidents. Reporter credibility weighting and the divergence multiplier both belong in V2. This is more conservative than my Phase 1 recommendation — and I believe it is more correct after seeing the codebase dependency chain.

---

## Summary: What the Council Should Decide

The three agents' combined analysis points to these open decisions requiring council resolution:

**Decision 1 (HIGH priority):** Is reporter credibility in V1 or V2? My Phase 1 placed it in V1. The dependency chain evidence places it in V2. The council must settle this explicitly.

**Decision 2 (HIGH priority):** Is severity a routing mechanism (processing path) or a formula weight in V1? The Devil's Advocate argues for routing only. My Phase 1 argued for formula weight. After reading the internal evidence, I partially reverse my position — routing is safer for V1.

**Decision 3 (MEDIUM priority):** Is the score version model a FICO version fork or a SecurityScorecard simultaneous recalibration? This must be specified before the Go rewrite begins.

**Decision 4 (MEDIUM priority):** Should deregistered agent names be prohibited from re-registration (credit bureau model: permanent file) or allowed with inherited history? The credit bureau model suggests prohibition — but this conflicts with what the prior council settled. This conflict needs explicit resolution.

**Decision 5 (LOW priority, but V1-ship-blocking):** Does the API response include `reporter_diversity: N` (distinct registered reporters who have interacted with this agent)? This is a one-query addition that significantly changes how brands interpret scores. It should be built now, not retrofitted.
