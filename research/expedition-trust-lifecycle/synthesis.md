# Expedition Synthesis: Trust Lifecycle Design
## Date: 2026-03-12
## Vetted by: Orchestrator
## Alignment: Checked against Research Brief
## Teams: 5 researchers + 3 validators

---

## Vetting Process

All 5 team findings were cross-validated by 3 independent validators with different lenses:
- **Validator 1**: General evidence quality, contradictions, alignment drift
- **Validator 2**: Anti-gaming analysis, deterministic enforcement, solo founder feasibility
- **Validator 3**: Implementation feasibility, math verification, scope aggregation

Each recommendation below has been checked against:
1. **Alignment** with the Research Brief's expected outcome
2. **Constraints** (no ML, no enforcement, deterministic only, solo founder)
3. **Evidence quality** (cited sources, verified claims)
4. **Cross-team consensus** (convergence = high confidence)
5. **Implementation risk** (codebase blast radius, test breakage)

---

## High Confidence (teams converged with independent evidence)

These findings were reached independently by 3+ teams and confirmed by all 3 validators. They are the foundation of the design.

### 1. Pending State Before Formula Impact — HIGHEST PRIORITY

**Convergence:** Teams 1, 3, 4, 5 + all 3 validators
**Evidence:** FCRA dispute model (item hidden from score during investigation), eBay's review period, content moderation queue patterns
**The math:** A single incident against a new agent (0 queries) drops trust from 0.5 to 0.333 — immediately, permanently, with no review. This is the most dangerous gap in the current codebase.

**Vetted design:** Incidents enter PENDING state. Only ACCEPTED incidents affect the formula. The aggregate `incidents` counter on `agent_registry` stops being the formula input — `compute_trust()` reads accepted incidents from `incident_reports` instead.

**Anti-gaming:** Bounded pending duration (14 days standard, 21 days max with dispute extension) prevents indefinite limbo.

### 2. Five Entity Status Labels

**Convergence:** Teams 1, 4 + Validators 1, 3
**Evidence:** Credit bureau status codes (11/71-84/93/97), ICANN EPP codes (clientHold/serverHold), Stripe Connect (Restricted/In Review/Enabled), Visa VAMP tiers, Apple App Store lifecycle

**Vetted labels:**

| Label | Meaning | Applied By | Transition Trigger |
|-------|---------|------------|-------------------|
| **NEW** | Recently registered, thin history | System (automatic) | Registration |
| **ACTIVE** | Sufficient interaction history, no unresolved incidents | System (automatic) | 10+ interactions, no pending incidents |
| **UNDER_REVIEW** | Has accepted incident(s) being investigated | System (automatic) | First accepted incident |
| **PROBATIONARY** | Has resolved incident(s), rebuilding trust | System (automatic) | Incident resolved, score below threshold |
| **SUSPENDED** | **CONTESTED — see Disagreements** | — | — |

**Sixth meta-state: SANDBOX** — isolated test environment (see Battle-Tested Approaches).

**Metadata per label** (from Team 1, confirmed by Validator 1):
- `status_applied_at` — when the label was assigned
- `status_applied_by` — who/what triggered it (system rule, human review, or specific incident)
- `status_reason` — machine-readable reason code
- `previous_status` — audit trail

### 3. Interaction IDs as Anti-Fabrication Anchor

**Convergence:** Teams 3, 4, 5 + all 3 validators
**Evidence:** eBay's `orderLineItemId` (incident reports must reference a real transaction), AWS CloudTrail event IDs, GitHub audit log correlation IDs

**Vetted design:** Every interaction generates a Submantle-issued UUID. Incident reports must reference a valid interaction ID. This proves the reporter and agent actually interacted. Server-generated, not client-supplied.

**Validator 2 flag (important):** The interaction_id generation mechanism must be coordinated with the MCP server being built in parallel. The MCP server needs to know how to request or embed interaction IDs. This is a concrete dependency requiring a design decision before either workstream can finalize.

### 4. Sandbox: Cryptographic Separation, Not Flags

**Convergence:** Teams 1, 2 + Validators 1, 2, 3
**Evidence:** Stripe's sandbox architecture (separate API keys, separate environments), Valorant's unrated mode (separate MMR tracking)

**Vetted design (Team 2's architecture wins over Team 1 — Validator 3 confirms):**
- Separate HMAC secret for sandbox tokens
- Sandbox interactions stored separately (not just flagged in production tables)
- Sandbox metrics visible to brands as "test results" — clearly labeled, never affecting trust score
- No maximum sandbox duration (Validator 2 flags: stale sandbox agents accumulate; acceptable at prototype scale)

**Anti-gaming:** Sandbox tokens cannot authenticate against production endpoints (cryptographic enforcement, not just labeling).

### 5. Denied Interactions: Record But Don't Score

**Convergence:** Teams 1, 5 + Validators 1, 2
**Evidence:** Credit bureau hard inquiry model (inquiry is recorded but doesn't count as a default), AWS CloudTrail (denied API calls are logged), Stripe (declined charges appear in logs but don't affect merchant standing)

**Vetted design:** When a brand denies an under-review agent, the denial is logged as an interaction with outcome `DENIED`. It does NOT increment `total_queries` or `incidents`. It IS visible in the interaction log. Brands can see denial patterns (an agent denied by 50 brands is a signal; an agent denied by 1 brand with unusual thresholds is noise).

### 6. Dual Interpretation at Write Time

**Convergence:** Teams 1, 5 + Validators 1, 2
**Evidence:** Stripe's `seller_message` + `outcome.risk_score` duality, credit bureau METRO 2 codes (code "71" for machines, "30 days late" for humans), OWASP logging standards

**Vetted design:** Every interaction record carries two interpretation fields:
- `technical_interpretation`: "HTTP 504 Gateway Timeout after 30s on /api/payment/confirm"
- `layman_interpretation`: "This agent's payment confirmation timed out — it took too long to respond"

Generated at write time, not read time. Prevents inconsistency if generation logic changes later.

### 7. Reporter Velocity Caps

**Convergence:** Teams 1, 3, 4 + Validators 1, 2
**Evidence:** eBay proactively restricts high-volume case filers, Amazon monitors filing rates

**Vetted design:** Max N incidents per reporter per agent per 24-hour window. Reports beyond threshold enter SUSPICIOUS state (pre-PENDING, requires human clearance).

**Threshold:** Teams disagree on specific numbers (Team 1: 3 per 7 days; Team 3: 5 per 24 hours). Validator 2 notes that at V1 scale (< 100 agents), any threshold is conservative. **Recommendation: Start at 5 per agent per 24-hour window. Adjustable constant, not hardcoded in formula.**

---

## Battle-Tested Approaches

### Incident Review Workflow (Team 3, vetted against FCRA/eBay/Amazon models)

**Five incident states** — reconciled from Teams 3 and 4 (which proposed different schemas):

```
SUSPICIOUS → (human clears) → PENDING → (auto/human review) → ACCEPTED or EXPIRED
                                      → (agent disputes) → DISPUTED → ACCEPTED or WITHDRAWN
```

| State | Who Triggers | Formula Impact | Duration |
|-------|-------------|----------------|----------|
| SUSPICIOUS | System (velocity cap exceeded) | None | Until human clears |
| PENDING | System (incident filed) | None | 14 days max |
| DISPUTED | Agent (disputes pending incident) | None | 21 days max (7-day extension) |
| ACCEPTED | System or human review | Yes — increments effective incidents | Permanent (with audit trail) |
| EXPIRED | System (14-day timeout, no substantiation) | None | Permanent (audit only) |
| WITHDRAWN | Reporter retracts | None — removes any prior impact | Permanent (audit only) |

**Key correction from validators:** Team 3's original design had a "Critical" severity path that bypassed PENDING entirely. **All 3 validators flagged this as violating the settled pending-state constraint.** Corrected design: even clear-cut cases (10,000 self-pings) pass through PENDING with an automated 1-hour review window, then auto-transition to ACCEPTED. No incident bypasses PENDING.

### Deduplication Rules (Team 3, confirmed by Validators 1, 2)

Server-side computed, reporter cannot influence:

1. **Exact match:** `sha256(incident_type + agent_id + reporter_agent_id + date)` — same reporter, same type, same day = 1 incident
2. **Burst match:** Same type + same agent within 1-hour window = 1 dedup group
3. **Cross-reporter corroboration:** 5+ reporters filing same type against same agent within 48 hours = 1 incident with `corroborated` flag

Score impact = 1 per dedup group, not N. The `corroborated` flag is visible to brands as a credibility signal without multiplying formula impact.

**Evidence:** PagerDuty dedup_key (but server-side, not sender-defined), Sentry fingerprint rules (deterministic, no ML layer)

### FCRA-Style Dispute Resolution (Team 4, confirmed by Validator 1)

When an agent disputes a pending incident:
1. Reporter has 14 days to substantiate with evidence
2. If reporter doesn't respond → incident auto-withdraws (**FCRA model: non-response = deletion**)
3. If reporter substantiates → human review (solo founder, 72-hour target)
4. Hard maximum: 21 days. After that, unresolved disputes auto-expire.

**Key correction:** Team 3 proposed auto-ACCEPT at reduced weight for unresolved disputes. Team 4 proposed auto-WITHDRAW. **Validator 1 confirmed Team 4's reading of the FCRA is more accurate: non-response from the furnisher = deletion, not acceptance.** This is more protective of innocent agents. **CONTESTED — see Disagreements for the full picture.**

---

## Novel Approaches

### Trajectory Signal (Team 4 — unique, no analog found)

No existing reputation system exposes whether a score is improving, stable, or declining. Team 4 proposes periodic score snapshots that let brands see the direction of change, not just the current number.

**Implementation:** Store score + timestamp at regular intervals (daily or per-N-interactions). Compute slope. Label as "improving," "stable," or "declining" based on configurable thresholds.

**Validator 3 flag:** The slope calculation needs explicit threshold specification to remain deterministic. "Improving = score at day 30 is ≥ 0.05 higher than score at day 0" — not ML-adjacent inference.

**Verdict:** Sound concept. Defer to post-V1 (requires interaction history to be meaningful). Low implementation cost when the time comes.

### Corroboration as Credibility Signal, Not Formula Multiplier (Team 3)

Multiple reporters on the same incident = 1 score hit but the `corroborated` flag is visible. This is different from multiplying the formula impact (which would be a gaming vector).

**Validator 1 confirmed:** Corroboration is credibility information, not frequency information. The formula should not multiply it; the dashboard should surface it.

**Verdict:** Adopt for V1. The dedup rule (cross-reporter match → 1 incident with corroborated flag) handles this naturally.

---

## Emerging Approaches

### Severity as Processing-Path Determinant (Team 3, refined by Devil's Advocate from council)

Severity determines *which review tier processes an incident*, not the formula weight. This keeps severity classification purely in the processing domain and avoids the fractional-weight problem.

| Severity | Trigger (Deterministic Rule) | Processing Path |
|----------|------------------------------|-----------------|
| Critical | Self-ping (10,000+ identical queries) or flood (>10 incidents/24h from single reporter) | PENDING → auto-review (1 hour) → ACCEPTED |
| Standard | Normal incident, verified interaction ID, reporter trust > 0.5 | PENDING → 72h agent response → human review if disputed |
| Reduced | Reporter registration < 30 days | PENDING → requires human review before ACCEPTED |
| Suspicious | Reporter velocity cap exceeded | SUSPICIOUS → human review before PENDING |

**Key insight (DA from council V2):** Severity affecting the processing path = deterministic rules. Severity affecting formula input weight = the float-in-integer-formula problem. The processing-path model avoids the fractional weight issue entirely.

**Verdict:** Adopt for V1. The severity classification is a routing decision, not a scoring decision.

---

## Synthesized Recommendation

### What to build (in dependency order):

**Phase 1 — Blocking prerequisites (build before anything else):**
1. Soft-delete on `deregister_agent` (prevents Sybil resets via re-registration)
2. `status` column on `incident_reports`: `pending | accepted | expired | withdrawn | disputed | suspicious`
3. Stop calling `increment_agent_incidents()` immediately — only increment when status transitions to `accepted`
4. Auto-expire pending incidents after 14 days (background check, not a new system)
5. Fix `expires_at` column to be nullable or have a default (`DEFAULT 0.0`) — Validator 3 caught that `NOT NULL` with no default breaks SQLite `ALTER TABLE ADD COLUMN`

**Phase 2 — Interaction log foundation:**
6. `interaction_logs` table with minimum fields: `interaction_id` (UUID), `agent_id`, `counterparty_id`, `interaction_type`, `outcome`, `initiated_at`, `technical_interpretation`, `layman_interpretation`
7. `interaction_id` FK on `incident_reports`
8. Interaction ID generation at API/MCP layer

**Phase 3 — Anti-gaming minimum:**
9. Velocity cap on query trust accumulation (configurable constant)
10. Reporter velocity cap (5 per agent per 24h)
11. Reporter minimum registration age check at incident filing (30 days)
12. Dedup key computation (server-side, sha256-based)

**Phase 4 — Labels and sandbox (after interaction logs exist):**
13. `agent_status` column on `agent_registry`: `new | active | under_review | probationary` (+ suspended if GL approves)
14. `compute_status_label()` method — deterministic, reads from interaction/incident data
15. Sandbox: separate HMAC secret, separate storage, graduate endpoint

**Defer to post-V1:**
- Rolling window (until history data exists)
- Score trajectory snapshots (until dashboard is demanded)
- Reporter credibility weighting (bootstrapping problem unresolved)
- Bilateral outcome confirmation (V2 complexity)
- Brand-side label system (acknowledged gap, not V1)

### Estimated test impact (from Validator 3 + council codebase analyst):
~10 of 187 tests will need updating. All breaks are in the trust/incident subsystem — no cross-cutting changes. The awareness layer (scanning, processes, devices) is completely unaffected.

---

## Disagreements

### 1. SUSPENDED Label — NEEDS GL RULING

**Team 1:** Submantle applies a SUSPENDED label as the most severe status. Triggers: new serious incident while probationary, pattern of incidents across multiple reporters, confirmed identity fraud. This is consistent with Mastercard MATCH (labeling, not enforcement) and credit bureau charge-off codes.

**Team 4:** "Suspension is not a Submantle action — Submantle never acts." If a brand refuses a probationary agent, that's the brand's enforcement, not Submantle's.

**Validator 1 analysis:** Team 1's reading is more consistent with the Brief (which lists labels Submantle publishes). A SUSPENDED label is information ("this entity has critical unresolved incidents"), not enforcement. Brands decide whether to honor it. The MATCH list analogy supports this — Mastercard doesn't block merchants, but being listed has real consequences.

**Validator 3 analysis:** Team 1's position is better-supported by analogues, but the contradiction must be resolved explicitly before building.

**Orchestrator assessment:** Applying SUSPENDED as a label is consistent with "always aware, never acting" — it's the same mechanism as UNDER_REVIEW or PROBATIONARY, just higher severity. But this is a philosophical question about where labeling ends and acting begins. **Escalating to GL.**

### 2. Dispute Timeout — Auto-Accept vs. Auto-Withdraw — NEEDS GL RULING

**Team 3:** After 21-day hard maximum, unresolved disputes auto-accept at reduced weight (0.5). Rationale: the agent couldn't prove innocence, so the incident stands (weakened).

**Team 4:** If the reporter doesn't respond to a dispute, the incident auto-withdraws. FCRA model: non-response from the furnisher = delete the item. Rationale: benefit of the doubt goes to the scored entity.

**Validator 1:** "The FCRA model says if the furnisher (reporter) doesn't respond, the item must be deleted — supporting auto-withdrawal. Team 4's reading of the FCRA is more accurate."

**Orchestrator assessment:** The FCRA precedent is strong. Auto-withdrawal is more protective of innocent agents and more consistent with the fairness principle. Auto-acceptance penalizes agents for their reporter's inaction. **Leaning auto-withdraw, but escalating to GL since this affects the fundamental fairness posture.**

### 3. Minimum Interaction Threshold — 10 vs. 25 — NEEDS GL RULING

**Team 1:** 25 interactions before NEW → ACTIVE transition.
**Team 2:** 10 interactions before trust score is surfaced to brands.
**Team 4:** 10 queries before incidents can affect the formula.

**Validator 1:** "Team 2's reference to competitive gaming minimum gates and Team 4's mathematical analysis both support 10. Team 1's 25 is the least evidenced."

**Orchestrator assessment:** 10 has stronger evidence (Team 4's math shows single incidents are disproportionate below 10 queries; Team 2 cites competitive gaming placement minimums). 25 is more conservative but slower onboarding. **Recommend 10, but escalating since this affects user experience directly.**

---

## Filtered Out

### 1. Team 3's "Critical Severity → Skip Pending" (REMOVED — violates settled constraint)

All 3 validators flagged this. The Research Brief explicitly settles: "Incidents enter PENDING state before affecting score — review period required." Even obvious cases (10,000 self-pings) must pass through PENDING — but with an automated 1-hour review window instead of the standard 72 hours. The principle is preserved; the processing is fast.

### 2. Team 4's Rolling 365-Day Window (DEFERRED — modifies formula inputs, out of V1 scope)

Validators 1 and 2 flagged this as functionally modifying the formula's behavior by changing what inputs it receives. The Brief says "Do NOT redesign the Beta Reputation formula itself." Additionally, there is no empirical data on appropriate window duration for AI agents (Validator 3: "The right duration for AI agents is unknown"). Deferred until interaction history exists to calibrate against.

### 3. Team 5's Bilateral Outcome Confirmation for All Interactions (DEFERRED — V2 complexity)

All 3 validators flagged this as enforcement-adjacent (a brand refusing to confirm suppresses the agent's query accumulation) and disproportionate for V1 (doubles API surface area). eBay's mutual confirmation applies to disputes, not every transaction. Scoped to incident confirmation only for V1.

### 4. Fractional Formula Weights (0.5) (DEFERRED — unresolved implementation)

Teams 3 and 4 both proposed fractional incident weights. Validators 1 and 2 independently identified the same blocker: the Beta formula expects integer counts. Making `incidents` a float sum changes the mathematical properties of the Beta distribution. The council scoring model V2 (running in parallel) is specifically addressing this — do not implement before that council concludes.

### 5. Reporter Credibility Weighting (DEFERRED — bootstrapping unsolved)

The first brands to adopt Submantle have no accuracy history. Their reports would be weighted near zero. The circular dependency (credibility requires history, history requires reports, reports require credibility) has no specified bootstrapping solution. The council scoring model V2 is investigating this.

---

## Risks

### 1. Patient Attacker Vector — No Deterministic Defense (Validator 2, HIGH)

A sophisticated attacker builds legitimate reporter history over 6 months, then files credible-looking false reports against a competitor. The reports are crafted to be ambiguous, directing them to human review where they consume the solo founder's time. Reporter velocity caps don't catch slow, deliberate filing. False report rate tracking only activates after a pattern of dismissed reports — but the patient attacker ensures their false reports are not dismissed.

**Mitigation:** This is an inherent limitation of any reputation system without legal liability. The FCRA handles it through furnisher liability (legal exposure for false reporting). Submantle's V1 mitigation: the interaction_id requirement (must have actually interacted) raises the cost of fabrication, and the pending state buffer prevents immediate score impact. Acknowledged as an unsolved problem at the deterministic level.

### 2. Combined Scope Is 8-12 Weeks for Solo Founder (Validator 3, MEDIUM)

The five teams together propose 20+ new code artifacts. Validator 3 mapped the full scope: new tables, new columns, new methods, new endpoints, migration handling. The phased implementation sequence in the Synthesized Recommendation reduces this to a manageable sequence, but the total work is substantial. The build priority should follow the dependency chain strictly — no parallel tracks that create integration risk.

### 3. Interaction_logs Table Is Larger Than Teams Acknowledge (Validator 3, MEDIUM)

Every team assumes an `interaction_logs` table but none scoped it as a feature. It requires: new table, UUID generation, write path for every API call, velocity computation at write time, privacy boundary enforcement, coordination with MCP server. This is a complete feature, not a schema migration.

### 4. EU AI Act Fragility Under Future Weighting (DA from council V2, LOW for V1)

The current design (deterministic severity classification, deterministic dedup rules) stays safely outside EU AI Act scope. The risk emerges if future versions add behavioral-data-derived weights (reporter credibility computed from historical patterns). For V1, this is not a concern — all classification is rules-defined-by-natural-persons.

### 5. Formula Discrepancy (Validator 3, RESOLVED)

CLAUDE.md showed the wrong formula variant (`total_queries / (total_queries + incidents)` — division by zero at init). **FIXED this session** — corrected to `(total_queries + 1) / (total_queries + incidents + 2)` across CLAUDE.md, VISION.md, and submantle-index.md.

### 6. Team 4 Recovery Math Errors (Validator 3, NOTED)

The general recovery formula should be `q ≥ 4i + 3` (not `4i + 6`). 10 incidents needs ~43 queries to reach 0.8, not 78. Any probation exit thresholds built from Team 4's table must use the corrected math.

---

## Evidence Quality Summary

| Team | Quality | Critical Issues | Validator Consensus |
|------|---------|----------------|-------------------|
| Team 1 — Status Labels | Strong | Minor source mis-attribution (Apple/Google URL); 25-threshold unevidenced | Good research, schema needs reconciliation with Team 2 on sandbox |
| Team 2 — Sandbox | Strong | Valorant Level 20 claim outdated; counterparty diversity deferred | Architecture (separate HMAC) confirmed as correct by all validators |
| Team 3 — Review Tiers | Highest technical depth | Critical severity violates settled constraint; fractional weights unresolved; staging URL source | Core workflow design is sound after correcting the pending-bypass |
| Team 4 — Fairness/Recovery | Strong on formula math | Recovery math errors (corrected above); rolling window out of scope | FCRA analysis is the strongest external precedent in this expedition |
| Team 5 — Interaction Metadata | Strong schema design | Brand-side tracking unspecified; bilateral confirmation scoped down | Dual-interpretation pattern confirmed as industry standard |

---

## Open Gaps (for future research)

1. **Brand-side label system** — agents have labels, brands don't. If brands carry trust scores, do they also have status labels?
2. **Sandbox graduation visibility** — does a graduated agent's sandbox history remain visible to brands?
3. **Reporter reputation formula** — three teams mention it, none design it. Deferred to council scoring model V2.
4. **Submantle-originated error appeals** — if Submantle's automated dedup misgroups incidents, how does an agent challenge a Submantle-generated label?
5. **Human review queue capacity** — at what agent/brand scale does the queue become unmanageable for a solo founder?
