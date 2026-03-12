# Validation Report — Expedition: Trust Lifecycle Design
## Date: 2026-03-12
## Validator: Validator 3
## Focus: Solo founder implementation feasibility — is the combined scope manageable?

---

## 1. Evidence Challenges

### Team 1: One source attribution error, one citation mismatch

**Google Play link cited as Apple source (minor but notable):**
Team 1's sources list for Apple App Store enforcement links to `support.google.com/googleplay/android-developer/answer/9899234` — a Google Play URL — appearing twice, once labeled as Apple and once as Google. The Apple section of the findings does not derive factually incorrect claims from this, but the citation is wrong. The substantive Apple App Store content appears accurate from independent knowledge; the sourcing is sloppy.

**Visa VAMP transition date is correct, but the framing may mislead:**
Team 1 describes the "Advisory" tier as "April-September 2025" and then "Enrolled/Standard" as the ongoing state. The ravelin.com source cited confirms the VAMP consolidation happened April 2025. However, the Advisory period was a transition window — the current (2026) state is that all merchants are on VAMP Standard/Excessive tiers. Describing Advisory as a current label creates a false impression of a still-operative tier. As a design pattern it remains valid; as a current-state reference it needs the caveat that the Advisory tier was transitional.

### Team 2: Valorant Level 20 claim requires verification

Team 2 states "Players must reach account level 20 before accessing ranked at all." The cited Valorant Competitive FAQ is legitimate but the specific Level 20 requirement was changed in 2024 — Riot reduced it to account level 10 (Episode 8 Act 1, January 2024) and later to 5 in some markets. The structural principle is sound (minimum investment gate before score-affecting play) but the specific number used as support is outdated. This does not break the design recommendation, only the cited evidence.

### Team 3: eBay stage URL raises reliability concern

Team 3 cites `https://ebaysc.stage.liveplatform.com/seller-protection/fair-case-resolution` for the reporter velocity cap claim. The `.stage.` subdomain is a staging/pre-production environment, not the production eBay documentation. The URL pattern suggests internal or pre-release content. The claim that eBay "proactively identifies and restricts buyers filing unusually high numbers of cases" is consistent with eBay's published policy approach and not in dispute substantively, but the evidential basis is a staging server, not a production documentation page. Flag as unverifiable.

### Team 4: Beta formula recovery table contains math errors

Team 4 presents recovery tables as follows:

- "1 incident, ~6 queries to reach 0.8" — they show `(7+1)/(7+1+2) = 8/10 = 0.80`. Correct.
- "2 incidents, ~14 queries" — they show `(14+1)/(14+2+2) = 15/18 = 0.83`. The threshold is 0.8, and 0.83 > 0.8, so this is technically satisfied but the claimed "~14 queries" doesn't target the threshold precisely. At q=11: `(12)/(11+2+2) = 12/15 = 0.80`. The answer is 11 queries, not 14. The table is conservative but imprecise.
- The "general formula" `q ≥ 4i + 6` for T=0.8: Solving `(q+1)/(q+i+2) ≥ 0.8` gives `q+1 ≥ 0.8q + 0.8i + 1.6`, so `0.2q ≥ 0.8i + 0.6`, so `q ≥ 4i + 3`. The correct formula is `q ≥ 4i + 3`, not `4i + 6`. The error makes recovery appear harder than it is. For 10 incidents: the table says 78 queries needed; the correct answer is ~43 queries.

This error is in the wrong direction — it overstates how hard recovery is, which is a fairness concern in the other direction. Not a critical blocker but it means any recovery thresholds built on this math will be calibrated wrong.

### Team 5: Formula in CLAUDE.md differs from Research Brief formula

Team 5 (and Teams 3 and 4) use the formula from the Research Brief: `trust = (q+1)/(q+i+2)`. However, CLAUDE.md states the formula as `trust = total_queries / (total_queries + incidents)` — no Bayesian prior at all. These are different formulas producing different scores, especially at low query counts:
- Brief formula at q=0, i=0: `1/2 = 0.5`
- CLAUDE.md formula at q=0, i=0: `0/0 = undefined` (division by zero)

The Research Brief version with the Beta prior `(q+1)/(q+i+2)` is the correct one (matches standard Beta Reputation initialization at 0.5) and is what the codebase actually uses based on prior expedition synthesis. The CLAUDE.md formula appears to be a simplified display version or a stale entry. But no team flagged this inconsistency. Teams should have caught it and called it out. It matters because a solo founder implementing from CLAUDE.md rather than the Brief would get a broken formula.

---

## 2. Contradictions Between Teams

### Teams 1 and 4 propose incompatible status labels for probation

Team 1's label table (Section 3) defines "SUSPENDED" as a label Submantle applies, with an explicit entry for `suspended`. Team 4 (Section 10) explicitly states: "Suspension is not a Submantle action — Submantle never acts. If a brand decides not to serve a probationary agent, that is the brand's enforcement."

This is a real contradiction. Team 1 has Submantle actively applying a "Suspended" label as a status state. Team 4 says Submantle never acts, so suspension must be the brand's call.

The Research Brief itself settles this obliquely: "Submantle publishes status labels... Submantle does NOT enforce these." A "Suspended" label is still a label — it communicates, it doesn't enforce. Team 1's position is defensible: Submantle can label an agent "suspended" (a data statement) while brands decide whether to honor it. Team 4's statement is an overcorrection — it conflates "labeling" with "acting."

However, this disagreement needs explicit resolution before implementation. If Submantle can apply a Suspended label unilaterally, that is a meaningful departure from pure neutral infrastructure. The MATCH list analogy (Team 1) supports this: Mastercard doesn't block merchants, but being on the MATCH list has real consequences. The credit bureau flags a charge-off, it doesn't cause the charge-off. Team 1's position is more consistent with analogues.

**Verdict:** Team 1's position is better supported. But the contradiction must be resolved explicitly in the decision log before building.

### Teams 3 and 4 propose different incident status schemas

Team 3's five incident states: `SUSPICIOUS | PENDING | DISPUTED | ACCEPTED | EXPIRED | DEDUPLICATED`

Team 4's four incident states: `pending | accepted | disputed | withdrawn`

Team 3 adds `SUSPICIOUS` (pre-pending) and `DEDUPLICATED` and `EXPIRED`. Team 4 uses `withdrawn` where Team 3 uses `EXPIRED`. These are not just naming differences — Team 3's `SUSPICIOUS` state is a meaningful pre-filter that Team 4 doesn't include. Team 4's `withdrawn` (brand retracts a report) doesn't appear in Team 3's schema.

Neither schema is complete. A merged schema needs all six concepts: `suspicious`, `pending`, `disputed`, `accepted`, `expired`, `withdrawn` (reporter-initiated retraction, distinct from expiry). This needs reconciliation before implementation.

### Teams 2 and 1 describe sandbox differently at the schema level

Team 1 proposes sandbox columns on `agent_registry` itself (`sandbox_mode`, `sandbox_queries`, `sandbox_incidents`). Team 2 proposes a separate `sandbox_interactions` table with cryptographically separate HMAC secrets. These are architecturally different approaches: Team 1 embeds sandbox state in the production registry; Team 2 separates them structurally.

Team 2's approach is correct — it matches the Stripe model (separate environments, not flags). Team 1's approach embeds sandbox into the production registry, which creates exactly the coupling Team 2's research shows is the failure mode. Stripe explicitly built separate sandbox environments *because* test mode flags on the same database caused problems.

**Verdict:** Team 2's architecture should take precedence over Team 1's schema proposals for sandbox.

---

## 3. Alignment Drift

### The interaction_logs table creates a dependency chain that isn't reflected in the build priority

All five teams assume an `interaction_logs` table exists or will be built as part of this work. The Research Brief identifies this as something that "does NOT exist." Every team's proposal chains through it:
- Reporter authentication requires interaction IDs
- Incident deduplication requires interaction IDs
- Anti-gaming velocity caps require interaction log data
- The Beta formula's `total_queries` needs to be fed by interaction logs, not raw endpoint hits
- Sandbox validation requires interaction log separation

The Research Brief's stated build sequence: "soft-delete deregistration, interaction logging table, reporter auth + pending state + velocity caps." The teams correctly identify this dependency but none of them size the interaction_logs table work explicitly as a prerequisite deliverable. They treat it as obvious context. For a solo founder, "obvious" dependencies are where scope balloons.

The interaction_logs table is not a minor add. It requires: new table, UUID generation, write path for every API call, velocity flag computation at write time, diversity flag computation at write time, outcome confirmation workflow, privacy boundary enforcement. This is a complete feature, not a schema migration. No team scoped it this way.

### Team 4's rolling window recommendation contradicts the "deterministic, no ML" principle in one edge case

Team 4 recommends: "Incidents older than 365 days are archived but excluded from the active formula." This is deterministic and consistent with the principle. However, Team 4 also recommends: "Label as 'improving,' 'stable,' or 'declining' based on slope."

Slope calculation over a rolling window using sampled data points is deterministic math. But the team does not specify: what sample rate? What smoothing? What constitutes "improving" vs "stable" — is it any positive slope, or a statistically significant one? An unspecified slope calculation could introduce ML-adjacent inference if implemented loosely. The principle says "deterministic scoring only." Slope labels need an explicit threshold specification: "improving = score at day 30 is more than X points higher than score at day 0." Without that, it is opaque to users and potentially gameable (agents could time interactions to maximize the slope label even if absolute score is low).

### Teams do not address the formula discrepancy in CLAUDE.md

As noted above, CLAUDE.md has the formula as `trust = total_queries / (total_queries + incidents)`, which is division by zero at initialization. No team flagged this. The Research Brief, which correctly uses `(q+1)/(q+i+2)`, is the source all teams used. But the solo founder reading CLAUDE.md without the Brief would get a different formula. This is an alignment gap with existing documentation that should be corrected as part of implementing this work.

---

## 4. Missing Angles

### No team assessed the mutual confirmation requirement's implementation cost

The Research Brief's settled eBay model requires both parties to have interaction logs. Team 5 mentions "outcome confirmation window (both parties or timeout)" as a bullet point in the anti-gaming section. No team worked through what bilateral confirmation means in practice for a solo founder:

- How does the brand confirm an interaction happened? They need an API endpoint.
- What happens when only one party reports? The current codebase has zero bilateral confirmation infrastructure.
- The MCP server is being built in parallel — who generates interaction IDs if agents are calling Submantle via MCP? The MCP server would need to generate IDs, but teams treat ID generation as a solved problem.

This is a significant implementation gap. The eBay model is settled, but none of the five teams scoped the bilateral confirmation infrastructure needed to make it work. A solo founder cannot implement the interaction ID requirement without first building: (1) an endpoint for brands to confirm interactions, (2) interaction ID generation at the MCP layer, and (3) the timeout/auto-confirm logic. This is 3-4 features before reporter auth even becomes functional.

### No team assessed what "human review" means operationally for one person at scale

Team 3 acknowledges this most directly ("The solo founder's human review burden is minimized by design") but does not quantify it. At what agent/brand scale does the "minimized" human queue become unmanageable? If 100 agents each generate 5 disputed incidents per month, that is 500 human review tasks per month — unsustainable for one person. None of the teams defined a maximum sustainable review load, or what happens when the founder cannot clear the queue in 72 hours.

The answer may be: at V1 prototype scale, the queue is near-empty and this doesn't matter yet. But that should be stated explicitly, not assumed.

### No team addressed what happens to existing test data in the database

The current codebase has 160 passing tests and live SQLite data. Every team proposes schema migrations (adding columns to `agent_registry` and `incident_reports`). No team addressed SQLite's lack of column type alteration and the specific migration strategy needed. SQLite `ALTER TABLE ADD COLUMN` works for adding nullable columns but there are constraints (columns with `NOT NULL DEFAULT` values require care). The teams propose several `NOT NULL DEFAULT` additions:

- Team 1: `status TEXT NOT NULL DEFAULT 'new'`
- Team 1: `sandbox_mode INTEGER NOT NULL DEFAULT 0`
- Team 3: `status TEXT NOT NULL DEFAULT 'pending'` on incident_reports
- Team 3: `severity TEXT NOT NULL DEFAULT 'standard'`
- Team 3: `formula_weight REAL NOT NULL DEFAULT 1.0`
- Team 3: `expires_at REAL NOT NULL` — this one is **problematic**: `NOT NULL` with no default on existing rows would fail on SQLite `ALTER TABLE ADD COLUMN`

`expires_at REAL NOT NULL` with no default value cannot be added via `ALTER TABLE ADD COLUMN` in SQLite — existing rows would have NULL in a NOT NULL column. This will break the migration. Either a default value is needed (`DEFAULT 0.0` or `DEFAULT (unixepoch() + 1209600)`) or the column must be nullable. No team caught this.

---

## 5. Agreements — High-Confidence Zone

All five teams independently converged on these points. High confidence:

1. **Pending state is mandatory and urgent.** The codebase's current immediate-formula-impact is the single most dangerous gap. Team 3's math makes the attack concrete: filing one incident against a new agent drops them to 0.333. All five teams agree this is the first fix.

2. **Only ACCEPTED incidents affect the Beta formula.** Universal agreement. The formula inputs change, not the formula.

3. **Interaction IDs are the anti-fabrication backbone.** All teams treat Submantle-generated interaction IDs as the prerequisite for reporter authentication. Consistent with the settled eBay model.

4. **Sandbox must be cryptographically separated, not flagged.** Teams 1 and 2 differ on schema approach but Team 2's case for HMAC secret separation is stronger and unchallenged by any team.

5. **Denial by counterparty must not affect the denied agent's formula score.** Teams 4 and 5 both confirm this. The credit bureau analogy is exact: a hard inquiry is not a default.

6. **Dual-interpretation fields (technical + layman) should be generated at write time.** Team 5 specifies this correctly and Teams 1 and 4 implicitly rely on it. Generating at write time is the right call — read-time generation creates consistency risks.

---

## 6. Surprises

### The combined scope is larger than any single team acknowledges

This is the core finding of this validation, stated plainly:

The five teams together propose the following new code artifacts:
- `interaction_logs` table with ~15 columns (Team 5)
- `sandbox_interactions` table (Team 2) OR sandbox columns on agent_registry (Team 1, contradicted)
- 6 new columns on `agent_registry` (Team 1)
- 9 new columns on `incident_reports` (Team 3)
- Soft-delete on `deregister_agent` (Team 4, referenced)
- `compute_status_label()` method (Team 1)
- `review_incident()` method replacing immediate `increment_agent_incidents()` calls (Team 1)
- `graduate_from_sandbox()` endpoint (Team 1)
- Sandbox token generation (separate HMAC secret) (Team 2)
- Sandbox profile API endpoint (Team 2)
- Velocity cap logic on `record_query()` (Teams 1, 3, 4)
- Query diversity flag computation (Teams 1, 5)
- Deduplication key computation (Team 3)
- Automated severity classification at incident write time (Team 3)
- `expires_at` timer and auto-expiry background job (Team 3)
- Reporter velocity cap check (Teams 1, 3)
- Rolling 365-day window filter in `compute_trust()` (Team 4)
- Reporter credibility weight at incident write time (Team 4)
- Score trajectory snapshot storage (Team 4)
- Dual-interpretation string generation at write time (Team 5)
- Bilateral outcome confirmation endpoint (Team 5, partially)
- Schema migrations on existing tables with live test data

This is not one sprint of work for a solo founder. By a conservative estimate: the full combined proposal is 8-12 weeks of engineering work for one person working full-time. The Research Brief says "Complexity is the enemy." The teams produced individually reasonable proposals that collectively form an overwhelming implementation load.

### Most teams buried V1 prioritization rather than leading with it

Team 2 is the exception — it has an explicit "Minimal viable sandbox" section estimating scope. Teams 1, 3, 4, and 5 mention V1 in passing but do not distinguish "build this now" from "think about this eventually." A solo founder reading all five reports without this validation would face a 20-item schema and logic checklist with no forced prioritization.

### Team 4's suggestion that disputes "add a label but do not change the formula" is inconsistent with Team 3's AUTO-ACCEPTED at reduced weight rule

Team 4: "Filing a dispute that is ultimately rejected adds a negative signal to the disputer's own trust metadata." Team 3: "After the maximum window, if substantiation is missing, incident expires; if dispute is unresolved, incident auto-accepts at reduced weight (0.5 formula weight)." Team 4 says disputes don't change the formula; Team 3 says disputes that aren't resolved auto-accept at 0.5 weight. These are in direct conflict on what happens at the 21-day hard limit. This needs explicit resolution.

---

## Summary: Recommended Implementation Sequence

Based on this validation, the teams' work is high-quality research with good sourcing. The primary failure is scope aggregation — no single team could see the full pile. For a solo founder, the correct reading of these five reports produces the following prioritized sequence:

**Phase 1 (blocking — build before anything else):**
1. Soft-delete on `deregister_agent` (one-line change, prevents Sybil resets)
2. `status` column on `incident_reports` with `pending | accepted | expired | withdrawn` (4 states, not 6 — defer `suspicious` and `deduplicated`)
3. Stop calling `increment_agent_incidents()` immediately — only call it when status transitions to `accepted`
4. Auto-expire pending incidents after 14 days (a cron-equivalent background check, not a new system)
5. Fix `expires_at` column to be nullable or have a default before writing the migration

**Phase 2 (interaction log foundation):**
6. `interaction_logs` table with minimum fields: `interaction_id`, `agent_id`, `counterparty_id`, `interaction_type`, `outcome`, `initiated_at`
7. `interaction_id` on incident_reports (migration)
8. Interaction ID generation at query endpoint

**Phase 3 (anti-gaming minimum):**
9. Velocity cap on query trust accumulation (configurable constant, not dynamic)
10. Reporter minimum age check at incident filing

**Defer to later:**
- Sandbox (until MCP server is built and real developers need it)
- Rolling window (until there is enough history data for it to matter)
- Score trajectory snapshots (until dashboard is demanded by customers)
- Deduplication key system (until incident volume makes it necessary)
- Reporter credibility weighting (requires reporter trust scores to exist first)
- Dual-interpretation strings (implement when interaction_logs table exists)
- Human review queue tooling (implement when first real disputed incident arrives)

---

## Critical Defects to Fix Before Implementation

1. **Team 3's `expires_at REAL NOT NULL` column will break SQLite migration.** Needs a default value or must be nullable.

2. **CLAUDE.md formula is wrong or stale** — `trust = total_queries / (total_queries + incidents)` is division by zero at initialization. Must be corrected to `(q+1)/(q+i+2)` to match the Research Brief and actual implementation intent.

3. **Team 4's recovery math is wrong.** The general formula `q ≥ 4i + 3` (not `4i + 6`) and 10 incidents requires ~43 queries to reach 0.8, not 78. Any probation exit thresholds built from Team 4's table will be miscalibrated by nearly 2x.

4. **Suspended label vs. "Submantle never acts" contradiction** between Teams 1 and 4 must be resolved in the decision log before any status label code is written.

5. **Incident status schema is unreconciled** — Teams 3 and 4 propose different state machines. One canonical schema must be chosen before any implementation begins.
