# Validation Report — Expedition: Trust Lifecycle
## Date: 2026-03-12
## Validator: Validator 2
## Focus: Anti-gaming analysis across all teams — Are countermeasures actually deterministic? Do they introduce hidden complexity for a solo founder? What gaming vectors were missed?

---

## Order of Analysis

1. Evidence Challenges
2. Contradictions
3. Alignment Drift
4. Missing Angles
5. Agreements
6. Surprises

---

## 1. Evidence Challenges

### Team 1 — Status Labels

**Challenge 1: The "3 consecutive months" Visa VAMP exit criterion is cited as a lesson for Submantle, but Submantle is interaction-count-based, not time-based.**

Team 1 proposes PROBATIONARY exit via "minimum N incident-free interactions." This is logically sound. But Team 1 also absorbs the VAMP "3 consecutive months" model as a design lesson and cites it as Pattern 6 ("Removal Requires Sustained Improvement"). The translation to Submantle's interaction-count world is underspecified: what does "consecutive" mean for an agent that runs 1 interaction per month vs. 10,000 per day? The VAMP model relies on calendar months as a fixed denominator. Submantle has no equivalent fixed denominator. The lesson is valid conceptually but the concrete threshold (50 incident-free interactions to exit PROBATIONARY) is pulled from thin air. No analog system was cited to support this specific number.

**Challenge 2: The Apple App Store source URL is duplicated and miscited.**

In the Sources section, the Apple App Store source is listed as `https://support.google.com/googleplay/android-developer/answer/9899234` — a Google Play URL — listed twice under both "App Store Connect status lifecycle" and "Apple App Store enforcement." This is a citation error. The Apple source appears to have been conflated with a Google source. Content drawn from it (the App Review Board structure, the Resolution Center model) may have been attributed to Apple incorrectly.

**Challenge 3: SANDBOX label described as "no maximum duration" — this creates an unaddressed maintenance problem.**

Sandbox agents that are never graduated will accumulate in the registry indefinitely. Team 1 acknowledges no TTL, no cleanup mechanism, no staleness signal. At prototype scale this is harmless, but it contradicts the solo founder simplicity constraint. No analog system was cited where a "test forever" environment is standard.

**Challenge 4: The "reporter concentration" countermeasure threshold (>80% from a single reporter) has no evidence base.**

Team 1 cites this as a deterministic countermeasure for gaming UNDER_REVIEW via coordinated attack. 80% is a number without a cited reference. No analogous threshold from any of the 10 systems studied is given. This is an invented threshold, not a research-derived one.

---

### Team 2 — Sandbox

**Challenge 5: The Valorant Level 20 gate analogy is factually overstated.**

Team 2 states "Players must reach account level 20 before accessing ranked at all — minimum investment required before reputation-affecting play begins." This is cited as a direct analog for Submantle's minimum interaction gate. However, the Valorant level 20 gate is an account age/time gate, not a performance gate — it prevents fresh accounts from jumping directly into ranked, but it does not evaluate play quality. FIDE's minimum 5 rated opponents is a better analog because it requires demonstrated performance against verified opponents. Team 2's own text acknowledges FIDE is stronger ("FIDE's minimum 5 rated opponents"), but then emphasizes Valorant throughout. The analogy is valid but the framing oversells it.

**Challenge 6: The "higher rate limits in sandbox" recommendation has no performance baseline to justify it.**

Team 2 recommends sandbox rate limits be higher than production (citing Stripe). This is reasonable for integration testing. But Stripe's higher sandbox limits exist because sandbox has no fraud risk or financial liability. Submantle's concern is trust pollution, not fraud risk. A higher sandbox rate limit in Submantle means an agent can fire millions of sandbox calls, accumulating sandbox performance data that brands might misinterpret as proof of scale. The justification needs a different framing for Submantle's context.

**Challenge 7: The "counterparty diversity" countermeasure is proposed as V1.5, but it's the primary anti-gaming mechanism for Vector 1 (Controlled Counterparty Farming).**

Team 2 identifies controlled counterparty farming as the most dangerous sandbox gaming vector and then defers the primary countermeasure (counterparty diversity requirements) to a future version. This creates an unprotected window at V1. The text acknowledges the risk but dismisses the countermeasure as adding "complexity." This is inconsistent — if the vector is real, deferring its primary defense needs stronger justification.

---

### Team 3 — Review Tiers

**Challenge 8: The "Critical" severity tier that auto-accepts incidents without human review is a design violation.**

Team 3's severity table includes: "Incident count from single reporter > 10 per agent per 24h → Skip pending → ACCEPTED immediately." This is the most direct violation of Principle 2 from the Research Brief — "Pending State on Incidents (SETTLED): Incidents enter PENDING state before affecting score — review period required." The Brief explicitly states this is settled. Auto-accepting incidents, even for "obvious" cases, means incidents bypass the pending state. Team 3's own anti-gaming analysis for Attack Vector 3 (Reporter Credibility Spoofing) directly contradicts this: a high-volume reporter might be a legitimate incident burst (a genuinely broken agent). Auto-accepting skips exactly the review that protects against false positives.

**Challenge 9: The 0.5 "reduced weight" for DISPUTED incidents after hard maximum is presented without a formula basis.**

Team 3 proposes: "AUTO-ACCEPTED (reduced weight 0.5) or AUTO-EXPIRED" after the 21-day hard maximum. The formula is `trust = (q+1)/(q+i+2)`. There is no mechanism in this formula for fractional incident weight. To implement 0.5 weight, the counter would need to increment by 0.5, or a separate `weighted_incidents` counter is needed. Team 3 acknowledges `formula_weight REAL` as a schema field but does not specify how `compute_trust()` consumes it. Team 4 later proposes a similar reporter credibility weight. Neither team resolves the formula integration. This is a concrete implementation gap that needs resolution before building.

**Challenge 10: "5 per agent per 24-hour window" reporter velocity cap has no supporting evidence.**

Team 3 acknowledges this directly in their Gaps section: "The threshold N is an empirical question. Starting at 5 per agent per 24-hour window is conservative and adjustable." This is honest self-assessment. But the number is presented in the workflow tables as a concrete parameter. At V1 with < 100 agents, this threshold is likely to be hit by legitimate incident bursts from real production failures. A threshold too low will suppress legitimate reports and frustrate users.

---

### Team 4 — Fairness/Recovery

**Challenge 11: The Beta formula recovery tables contain a calculation inconsistency.**

Team 4's recovery table states: "1 incident: needs ~6 queries to reach 0.8. From (0,1): trust = (6+1)/(6+1+2) = 7/9 = 0.78; (7+1)/(7+1+2) = 8/10 = 0.80."

Let me check: `(7+1)/(7+1+2) = 8/10 = 0.80`. That's correct. But the text says "From (0,1)" — meaning 0 queries, 1 incident. After 7 queries: `(7+1)/(7+1+2) = 8/10 = 0.80`. That is the state where total_queries is 7, so the formula is `(total_queries + 1)/(total_queries + incidents + 2) = (7+1)/(7+1+2) = 8/10 = 0.80`. This is correct. However, the general formula given is `q ≥ 4i + 6` (for T=0.8), but the table shows q=6 for i=1: `4(1)+6 = 10`. That doesn't match the table showing q=7. The general formula and the specific example are inconsistent. The general formula overstates the queries needed.

**Challenge 12: The 365-day rolling window recommendation is stated without competitive validation.**

Team 4 recommends 365 days, acknowledging "there is no empirical data yet." The range of comparisons is: FCRA 7 years, eBay 12 months, gaming 90 days. Team 4 selects 12 months (365 days = eBay). But AI agent trust cycles are not established. An agent that behaved badly 11 months ago and is still operating with the same architecture is not the same as a credit account that had a late payment 11 months ago. The recommendation is reasonable but the justification is borrowed from a different domain without examining whether the analogy holds.

---

### Team 5 — Interaction Metadata

**Challenge 13: The bidirectional trust metadata for brands is mentioned but not specified.**

Team 5 states "The brand's denial SHOULD be recorded against the brand too. Bidirectional trust: a brand that denies a high-trust agent (false positive) or accepts a low-trust agent (false negative) is producing observable data about its own threshold quality over time." This is correct and aligns with the Brief's bidirectional model. But the schema spec in Section 6 does not include any brand-side tracking fields. The spec only covers the agent's perspective. The brand-side interaction record is unspecified. If it's just the same `interaction_logs` table with `counterparty_id` pointing to the brand, that should be stated explicitly. The gap between the narrative and the schema is not closed.

**Challenge 14: "Outcome confirmation window — both parties must confirm" adds synchronous handshake overhead that is not compatible with the solo founder constraint.**

Team 5 proposes: "For bidirectional trust, both parties must confirm the outcome. If only one party reports, the outcome is PENDING until confirmed or a timeout window passes." This sounds clean, but it means every interaction requires two API calls to be resolved — one from each party. For a solo prototype with MCP server integration, this doubles the surface area and introduces a class of timeout management complexity not present in any other recommendation. No analog system requires bilateral confirmation for routine interactions — only for disputed outcomes (eBay's mutual confirmation is for disputes, not every transaction). This proposal should be scoped to incident confirmation only, not all interactions.

---

## 2. Contradictions

### Contradiction A: SUSPENDED label in Team 1 vs. "Submantle never acts" principle.

Team 1's SUSPENDED label section states: "Triggers on: (a) New serious incident while PROBATIONARY; (b) Pattern of incidents across multiple reporters meeting severity threshold; (c) Confirmed identity fraud." These triggers are all fine — they're label applications.

But Team 1's implementation notes then say: "Automated review for clear patterns (velocity spikes, single-reporter floods) can run as a background task." Combined with Team 3's Critical tier that auto-accepts incidents, there is a pathway: Critical incident → auto-ACCEPTED → score drops → triggers SUSPENDED. Submantle has applied a suspension-equivalent outcome through a chain of automated actions, even though each individual step is "just a label." The chain-of-automation problem is not acknowledged by any team.

### Contradiction B: Team 4 says disputes "do not change the formula" but Team 3 says disputed incidents auto-accept at reduced weight.

Team 4 (Section 9, Attack 5): "Disputes don't remove incidents from the formula — they add a label ('Disputed'). The brand's withdrawal is what removes the incident."

Team 3 (Synthesis, workflow): "AUTO-ACCEPTED (reduced weight 0.5) or AUTO-EXPIRED" after 21-day hard maximum.

These are different models for what happens when a dispute doesn't resolve. Team 4's model: disputed incidents stay in formula at full weight; withdrawal is required to remove. Team 3's model: after 21 days, auto-accepts at 0.5 weight OR auto-expires. These cannot both be true. One team models disputes as label-only; the other models them as affecting the timing and weight of formula impact.

**Stronger evidence:** The Research Brief's settled constraints require pending state before formula impact and a fairness principle that protects innocent actors. Team 3's auto-accept at reduced weight is more conservative for bad actors (they can't dispute their way out of formula impact forever). Team 4's model is more protective of innocent actors (a disputed incident can be withdrawn at full credit). Neither is demonstrably superior — but the designs must be reconciled before building.

### Contradiction C: Team 1 says incidents enter UNDER_REVIEW when "accepted incident count crosses threshold." Team 3's workflow has no threshold — a single pending incident can trigger UNDER_REVIEW.

Team 1: "UNDER_REVIEW triggers on: Accepted incident count crosses threshold (e.g., first accepted incident with a verified interaction ID)."

Team 3: The first accepted incident DOES trigger UNDER_REVIEW by implication (severity Standard = PENDING → 72h agent response window → UNDER_REVIEW if disputed). But Team 3's Critical tier also triggers ACCEPTED immediately — and it's unclear whether ACCEPTED-from-Critical-tier immediately triggers the UNDER_REVIEW label.

This is a sequencing inconsistency. The two teams designed compatible workflows independently but did not align on the exact trigger chain.

### Contradiction D: Team 3 proposes weighted incidents (formula_weight 0.5) but no team addresses how compute_trust() consumes fractional weights.

Team 3 introduces `formula_weight REAL`. Team 4 recommends reporter credibility weighting with weight = 0.5 for low-trust reporters. These are compatible proposals but both leave the implementation gap: the current `compute_trust()` uses `incidents INTEGER`. Fractional incident weights require either (a) a `weighted_incidents REAL` counter or (b) a per-computation aggregation query. No team specifies which approach.

---

## 3. Alignment Drift

### Drift 1: Team 3's Critical severity tier violates a settled constraint (most critical finding).

The Research Brief states: "Pending State on Incidents (SETTLED): Incidents enter PENDING state before affecting score — review period required." This is listed under NON-CHALLENGEABLE SETTLED DECISIONS.

Team 3's Critical severity tier skips pending entirely for two cases: (1) reporter filing > 10 incidents per agent per 24 hours, (2) self-ping evidence. The rationale — "it's obvious" — does not override a settled constraint. The correct handling for obvious cases is: (a) auto-ACCEPT after an extremely short pending window (e.g., 1 hour instead of 72 hours), or (b) add a flag that brands can see ("automated review completed, no human review needed") while still technically passing through PENDING state. The label architecture (Team 1) actually supports this: UNDER_REVIEW with automated resolution is still UNDER_REVIEW, just resolved quickly.

**Recommendation for synthesis team:** Replace "skip pending → ACCEPTED immediately" with "PENDING (auto-review: 1 hour) → ACCEPTED." Preserves the settled constraint without meaningfully delaying obvious outcomes.

### Drift 2: Team 5's bilateral outcome confirmation adds enforcement-adjacent complexity.

The Brief constraint: "Submantle never acts." Requiring both parties to confirm an interaction outcome before it's considered COMPLETED is a lightweight form of enforcement — Submantle is holding the interaction in PENDING until both parties cooperate. A brand that refuses to confirm is effectively blocking the agent's query count from accumulating. This is indirect enforcement through protocol design. The Brief is explicit that brands should make their own decisions using Submantle's labels — Submantle should not create mechanisms where brands can suppress agent score accumulation by refusing to confirm interactions. The confirmation model should apply only to disputed outcomes, not all outcomes.

### Drift 3: Team 4's rolling window recommendation requires compute_trust() to change its query pattern — this is underspecified against the existing codebase.

The Brief states findings "must work with the existing Beta Reputation formula: trust = (queries + 1) / (queries + incidents + 2)." Team 4 recommends filtering incidents older than 365 days from the formula. This requires `compute_trust()` to query `incident_reports WHERE timestamp > (now - 365 days)` rather than using the aggregate `incidents` counter on `agent_registry`. This is a fundamental change to how the formula is fed — from a counter lookup to a filtered aggregation — with performance implications at scale and requiring the `incidents` counter on `agent_registry` to be deprecated or maintained in parallel. This architectural impact is not flagged.

### Drift 4: None of the teams fully closes the "brand denial as interaction data" loop described in the Brief.

The Brief's settled constraint: "A brand denying an under-review agent is itself an interaction that gets logged. That denial/approval generates trust data for BOTH parties." Team 5 addresses this in Section 5 (Denial Scenario) and correctly concludes that denials should not affect the agent's Beta formula but should be recorded. However, none of the teams address how brand threshold quality data (false positive/false negative rates) feeds back into Submantle's system or what happens with this data. Team 5 mentions it; no team designs it. The Brief says it "generates trust data for BOTH parties" — the brand-side trust accumulation is entirely undesigned.

---

## 4. Missing Angles

### Missing: What happens when a registered brand deregisters or goes dark?

If a brand has filed multiple incident reports and then deregisters (or simply stops responding), what happens to their pending reports? Team 3's design has a 14-day auto-expiry for unsubstantiated reports — this is the right mechanism. But it's not explicitly connected to the brand deregistration scenario. The FCRA equivalent (furnisher doesn't respond → item deleted) is the right model. This should be stated explicitly.

### Missing: Sandbox graduation creates a new agent at 0.5 — but the sandbox history should be visible for context even if not formula-affecting.

No team addresses whether a graduated agent's sandbox history is visible to brands after graduation. If sandbox history disappears at graduation, a brand has no signal that the agent was tested. If it remains visible (as "test results"), it provides the integration quality signal Team 2 describes. The graduation pathway from Team 1 and Team 2 leaves this unresolved.

### Missing: The interaction_id is described as "Submantle-generated" but no team specifies the generation mechanism or its interaction with the MCP server being built in parallel.

The MCP server is being built in parallel with this trust lifecycle work. Interaction IDs must be issued before an interaction occurs — the MCP server needs to know how to request or embed an interaction ID. No team addresses how interaction IDs are issued pre-interaction vs. recorded post-interaction. This is a concrete dependency between the trust lifecycle design and the MCP server that needs resolution before either can be finalized.

### Missing: Reporter reputation formula is acknowledged as needed but never designed.

Three teams (1, 3, 4) mention that reporters should have their own trust scores. Team 4 recommends "binary rule: trust_score >= 0.7 AND registration_age >= 30 days for full weight." But what is the reporter's trust score computed from? Is it their own agent trust score (as a participant in the ecosystem)? Is it a separate reporter-quality metric (false report rate)? The Brief mentions "Submantle analyzes reporter history and agent history to contextualize grievances" as a settled constraint. No team designs the reporter reputation mechanism with a concrete formula.

### Missing: The anti-gaming analysis does not address the "sophisticated patient attacker."

All teams address burst attacks and obvious gaming vectors. None address the patient attacker who slowly builds a legitimate-appearing reporter history over 6 months, then uses it to file credible-looking false reports against a competitor. The FCRA handles this via furnisher liability (legal exposure for false reporting). Submantle has no legal liability hook. The reporter's "false report rate" countermeasure (Team 1, Team 3) is the only defense, but it only activates after a pattern of dismissed reports has accumulated. A patient attacker ensures their false reports are not dismissed — they are genuinely crafted to be ambiguous, directing them to human review where they consume founder time. This vector is not addressed by any team.

---

## 5. Agreements (High-Confidence Zone)

The following findings were reached independently by multiple teams and can be treated as high-confidence:

**A1: Pending state before formula impact is both necessary and universal.**
Teams 1, 3, 4, and 5 all independently arrived at this conclusion, supported by different analog systems (credit bureaus, eBay, gaming platforms, content moderation). The Brief settled this, and research across all domains confirms it.

**A2: Interaction IDs must be Submantle-generated.**
Teams 3, 4, and 5 all independently identify this as the primary anti-fabrication mechanism. The eBay `orderLineItemId` model cited by Teams 3 and 5 is the same source reaching the same conclusion.

**A3: Dual-audience presentation (technical + layman interpretation) in the same record is the industry norm.**
Teams 1 and 5 reach this independently. Team 1 via Stripe's API response pattern; Team 5 via Stripe's `seller_message` / `outcome.risk_score` duality. These are the same Stripe pattern identified from two angles. The finding is reliable.

**A4: Denied interactions must be recorded but must not affect the Beta formula.**
Teams 1 and 5 reach this independently. Team 5 via credit bureau hard inquiry model; Team 1 via the principle that labels are information not enforcement. The Brief's settled constraint supports this.

**A5: Recovery is built into the Beta formula's math — the pending state is the primary protection, not formula modification.**
Teams 3, 4, and 5 independently compute or acknowledge that the Beta formula is already rehabilitative at scale. The early-incident vulnerability (q < 20) is the primary mathematical concern, and pending state addresses it. No team proposed changing the formula.

**A6: Solo founder constraint requires automation to handle the majority of cases; human review must be reserved for genuinely ambiguous situations.**
Teams 2, 3, and 4 all design around this independently. The 80/20 split (deterministic automation for clear cases, human queue for edge cases) is consistent across all three.

**A7: The interaction_logs table is the necessary new addition; the existing formula, incident table, and event bus stay unchanged.**
Teams 1, 3, 4, and 5 all implicitly agree on this architectural boundary. None propose redesigning existing tables.

---

## 6. Surprises

**S1: Team 3's deduplication rules are more sophisticated than any analog system surveyed.**

PagerDuty uses sender-defined dedup keys. Sentry uses fingerprint rules. Team 3 proposes server-side computed dedup keys with three tiers (exact match, burst match, cross-reporter corroboration). This is more sophisticated than anything in the reference systems. It may be the right design, but it introduces a novel mechanism without an analog. The corroboration flag (5 reporters → 1 incident with a "corroborated" label) is genuinely interesting and not present in any surveyed system.

**S2: The Beta formula is actually more forgiving than expected at moderate scale.**

Team 4's recovery math shows that with 100 queries and 5 incidents, the trust score is still 0.944. This means that at modest interaction volumes, the formula is extraordinarily forgiving — far more so than a FICO score or eBay defect rate. This is a selling point for Submantle (it rewards genuine activity without permanent punishment) but it also means self-ping inflation is more dangerous than intuition suggests: an agent with 10,000 fake queries and 10 real incidents scores 10001/10013 = 0.9988. The formula needs velocity caps to be meaningful.

**S3: No competitive product has a developer sandbox for behavioral trust.**

Team 2 identifies this as first-mover opportunity. Given that Stripe's sandbox is a primary competitive advantage in payment infrastructure (it lowered developer onboarding friction dramatically), this is a meaningful gap. The finding changes the priority assessment — sandbox may be more strategically important than its position in the build queue suggests.

**S4: The "trajectory signal" proposed by Team 4 is underrepresented in analog systems but is the most actionable metric for brands.**

Team 4 notes that a brand's decision should be informed by whether a probationary agent's score is improving, stable, or declining. No analog system exposes this. eBay shows current status, not trend. Credit bureaus show payment history (which implies trend) but don't compute it. The trajectory signal is a Submantle-native innovation with no direct precedent — and it requires only storing periodic score snapshots, which is low-complexity. This deserves prioritization.

---

## Summary Assessment

**By team:**

| Team | Quality | Critical Issues |
|------|---------|----------------|
| Team 1 — Status Labels | High — thorough analog research, practical schema | Citation error (Apple/Google conflation); 80% threshold invented; SANDBOX TTL problem unaddressed |
| Team 2 — Sandbox | High — Valorant + Stripe architecture is the right model | Counterparty diversity defense deferred despite being primary attack vector; bilateral confirmation introduces enforcement adjacency |
| Team 3 — Review Tiers | Highest technical depth | Critical tier violates settled pending-state constraint; fractional formula weight unresolved; complexity risks solo founder overload |
| Team 4 — Fairness/Recovery | Strong on formula math | Rolling window changes compute_trust() architecture without flagging it; patient attacker not addressed; formula inconsistency in recovery table |
| Team 5 — Interaction Metadata | Strong on schema design | Brand-side tracking unspecified; bilateral confirmation adds enforcement-adjacent complexity |

**The single most important issue for synthesis:** Team 3's Critical severity tier that skips pending state must be reconciled with the settled constraint. Recommend replacing "skip pending → auto-accept" with "pending (1-hour auto-review) → accept." All other issues are resolvable without changing the core architecture.

**The single most important missing piece:** The interaction_id generation mechanism and its relationship to the parallel MCP server build. This dependency needs a decision before either workstream can finalize its design.
