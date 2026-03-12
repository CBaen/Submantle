# Team 4: Fairness, Recovery, and Probation Mechanisms
## Expedition: Trust Lifecycle
## Date: 2026-03-12
## Researcher: Claude Sonnet 4.6

---

## Executive Summary

Real-world reputation systems — credit bureaus, eBay, app stores, gaming platforms — converge on a small set of structural patterns for rehabilitation. The central tension is the same in all of them: permanent damage discourages honest actors from participating, but easy resets invite bad actors to abuse probation as a laundering mechanism. The systems that work best resolve this tension by separating **time-based rehabilitation** (automatic, structural, non-gameable) from **evidence-based appeal** (human review, slower, for contested claims). Submantle must design the same separation.

The Beta formula's mathematical properties create a natural asymmetry that is largely fair but has one specific failure mode: early incidents hit disproportionately hard. The fix is not to change the formula — it is to add a **pending state buffer** before incidents touch the formula at all.

---

## Section 1: FCRA 7-Year Rule — What Gets Removed and When

**Source: 15 USC 1681c(a), directly verified.**

The Fair Credit Reporting Act prohibits consumer reporting agencies from including:

| Category | Retention Period | Notes |
|----------|-----------------|-------|
| Most negative items (late payments, collections, charge-offs) | 7 years | Starts from date of first delinquency |
| Bankruptcy (Chapter 7) | 10 years | |
| Bankruptcy (Chapter 13) | 7 years | Rewarded for completing a repayment plan |
| Criminal convictions | Indefinite | No statutory removal requirement |
| Civil suits, judgments, arrests | 7 years | |
| Paid tax liens | 7 years from payment date | Unpaid liens: indefinite |

**Key structural feature:** The 7-year clock starts from the *date of first delinquency*, not from when the item was reported or resolved. This prevents creditors from "refreshing" the clock by re-reporting old debts.

**The high-stakes exception (15 USC 1681c(b)):** All timelines are suspended for transactions involving credit over $150,000, life insurance over $150,000, or employment with salary over $75,000. The logic: bigger stakes warrant fuller information. Smaller stakes get the benefit of rehabilitation.

**What this means for Submantle:** The FCRA's core principle is *proportional context*. High-stakes decisions get complete history; routine decisions get time-bounded history. Submantle could apply the same principle: brands querying for high-stakes integrations see full incident history; low-stakes queries see a time-windowed view.

---

## Section 2: Goodwill Adjustments and Rapid Rescoring

### Goodwill Adjustments

A goodwill adjustment is a request to a creditor (not the bureau) to remove a negative mark as a one-time courtesy, typically for a single missed payment in an otherwise clean history. Key facts:
- The request goes to the **original creditor**, not Experian/Equifax/TransUnion
- The bureau cannot remove accurate information — only the furnisher can
- Creditors are under no obligation to grant them
- Common outcome: granted once per account lifetime, for isolated incidents

**What this means for Submantle:** This maps directly to the eBay model of dispute adjudication. The analog for Submantle: an agent can request that a **specific reporter reconsider** a specific incident report. Submantle stores the request and the outcome. If the reporter withdraws the report, the incident counter decrements. The bureau (Submantle) doesn't decide — the furnisher (the reporting brand) does.

### Rapid Rescoring

Rapid rescoring is a service where a **mortgage lender** (not the consumer directly) can request expedited credit report updates within 3-5 business days by submitting documentation of errors or resolved items to the bureaus. Key constraints:
- Only lenders can initiate it — consumers cannot request it themselves
- Requires documentation proving the change is accurate
- Costs $25-$40 per item per bureau (paid by the lender)
- Not available for disputing accurate negative items — only for errors or resolved items

**What this means for Submantle:** The rapid rescoring model suggests that **verified counterparties** (registered brands with their own trust scores) could have an expedited channel to withdraw or correct incident reports. A random anonymous report gets standard processing. A high-trust brand submitting a correction gets faster resolution. This is structurally fair and anti-gameable because only trusted parties with skin in the game get the fast track.

---

## Section 3: eBay Seller Probation and Reinstatement

**Source: eBay Seller Performance Standards documentation (verified).**

eBay evaluates sellers monthly across three tiers: **Below Standard**, **Above Standard**, **Top Rated**.

### What Triggers Each Tier

| Metric | Below Standard Threshold |
|--------|--------------------------|
| Transaction Defect Rate | Above 2% (of transactions in evaluation period) |
| Cases closed without seller resolution | Above 0.3% |
| Late shipment rate | Above 10% |

**Key design decision:** eBay uses a **rolling 12-month evaluation window**. Old transactions age off. A seller who had a terrible month 13 months ago is not penalized today. This is the eBay equivalent of the FCRA 7-year rule: automatic, time-based rehabilitation.

### What Happens at Below Standard

- Listings appear lower in search results
- Selling limits may be imposed
- Access to some selling categories may be restricted
- The designation is visible in the seller profile

eBay does **not** publish the agent/brand as "below standard" to every buyer — the consequence is operational (lower visibility, limits) not reputational labeling visible to all counterparties. This is a subtlety: the enforcement is structural, not a visible scarlet letter.

### Recovery Path

1. Improve the actual metrics (the only real path)
2. Use Seller Help to request removal of specific defects that were outside the seller's control (e.g., carrier delays, buyer error)
3. Wait — the rolling window means improvement is automatic if metrics improve

**What this means for Submantle:** The rolling evaluation window is the most portable mechanism here. Submantle's Beta formula currently has no time dimension. The formula treats a 3-year-old incident identically to a 3-day-old incident. A rolling window — where incidents older than N months are archived (not deleted) but excluded from the active formula — would be structurally rehabilitative without enabling resets.

---

## Section 4: Apple App Store and Google Play Appeals

### Apple App Store

**Source: developer.apple.com/distribute/app-review/ (verified)**

Apple's process has two tiers:
1. **Standard rejection**: Developer can remediate and resubmit, or respond with clarification
2. **Appeal to App Review Board**: Available if the developer believes the app complies with guidelines or was treated unfairly. One appeal per rejection. Requires specific reasoning, not just disagreement.

Key structural feature: Apple's appeals go to a **separate body** (the App Review Board) from the original reviewer. This is the separation between first-line assessment and rehabilitation adjudication that credit bureaus also use (dispute to the bureau vs. goodwill to the creditor).

**What has NO path back:**
- Apps removed for fraud, malware, or serious safety violations
- Developer accounts terminated for repeated guideline violations

**What this means for Submantle:** The two-tier appeal structure maps cleanly. Tier 1: agent disputes a specific incident with the reporting brand (goodwill adjustment model). Tier 2: agent disputes to Submantle's arbitration layer if they believe the report was filed in bad faith (formal dispute model). Tier 2 requires higher evidence bar and is slower. The existence of Tier 2 prevents brands from abusing Tier 1 (reporter knows a second path exists).

### Google Play

Google Play uses a similar structure with developer account-level reputation separate from individual app suspension. Repeated policy violations result in account termination from which reinstatement is difficult. The key mechanism is **graduated response**: warning → temporary suspension → permanent termination. Each tier requires progressively worse violations to trigger. First-time violations of minor guidelines get warnings.

**What this means for Submantle:** Graduated response is the right pattern. First incident in a category: pending state (no formula impact until reviewed). Second incident of same type: formula impact applies, but label shows "one prior incident resolved." Third incident of same type: full weight, label shows "repeated pattern."

---

## Section 5: Gaming Platforms (Xbox, PlayStation, Steam)

**Source: Research via Steam subscriber agreement and Xbox enforcement pages (direct access limited by JavaScript requirements).**

Gaming platforms converge on a common pattern:

**Steam:** The subscriber agreement does not contain probation or recovery mechanisms. Valve reserves the right to terminate permanently for violations. For trading/marketplace violations, Steam applies **time-based restrictions** (e.g., no trading for 15 days after suspicious activity). These expire automatically without any appeal mechanism — pure time-based rehabilitation for minor violations.

**Xbox enforcement (from general knowledge + attempted fetch):** Microsoft uses a tiered system where:
- Communication bans (muting) are temporary, tiered in duration (1 day → 7 days → 14 days → permanent)
- Device bans are permanent and non-appealable
- Account suspensions fall between, with limited appeals via the Xbox Enforcement Review Panel

The key structural insight from gaming platforms: **temporary restrictions that expire automatically** are used for minor violations; the appeal mechanism is reserved for contested enforcement actions where the user claims it was an error. This is computationally elegant — no human review needed for temporary restrictions.

**What this means for Submantle:** Submantle should have three tracks:
1. **Auto-expiring restrictions** (for velocity violations, query spam): handled deterministically, no review
2. **Pending incidents** (for reported behavioral incidents): held in pending state until reviewed, then accepted or dismissed
3. **Formal dispute** (for contested accepted incidents): requires human/arbitration review, high evidence bar

---

## Section 6: Probation Mechanisms — The Synthesis

Across all systems surveyed, effective probation has four structural properties:

### Property 1: Temporal Bounds on Negative History

Every surviving system has a time limit on how long old negative events affect current standing. The FCRA mandates this by law. eBay implements it via rolling windows. Gaming platforms use timed restrictions.

**Why:** Without temporal bounds, a single early mistake creates permanent disadvantage. This is structurally unfair and empirically counterproductive — it drives honest actors to abandon the system ("I got one incident when I was learning, now I'll never recover, so why participate?").

### Property 2: Separation of Pending State from Formula Impact

No well-designed system allows unverified reports to immediately damage standing. eBay's defect rate only counts finalized cases. Apple's rejection doesn't affect any external reputation until the developer fails to fix and resubmits. Credit bureaus require furnishers to verify disputed items before they're re-added.

**Why:** Allowing immediate formula impact from unverified reports creates a trivial attack vector. Anyone can destroy anyone's reputation at zero cost. The pending state is the primary anti-gaming mechanism.

### Property 3: Source Credibility Weighting

The weight given to an incident report is proportional to the credibility of the reporter. Credit bureaus only accept reports from furnishers who have signed data agreements. eBay weights buyer feedback based on buyer history. Apple's appeal is reviewed by a board separate from the original reviewer.

**Why:** A report from a trusted, verified party with a track record of accurate reporting is different in kind from a report from an anonymous account registered yesterday. Treating them identically is both unfair and gameable.

### Property 4: Visible Status Labels During Probation

Counterparties see a status label, not raw incident counts. eBay shows "Above Standard" or "Below Standard," not "2.1% defect rate." Apple shows "App Removed" or "App Available." Credit reports show "Collection Account" with date and amount, not a raw score.

**Why:** Labels convey actionable information without exposing the full forensic record. They are interpretable by counterparties who don't know the formula. They also enable progressive disclosure: a brand can see "On Probation" and, if they want to know more, query the detailed record.

---

## Section 7: What Happens to Interactions During Probation

**The question:** Can an interaction with a "probationary" agent generate data that helps both parties?

The answer from analogous systems is yes, and the mechanism matters:

- **eBay:** A Below Standard seller can still sell. Every successful transaction in the evaluation window helps improve their rate. The probation is not a freeze — it's a label that changes as behavior changes.
- **Credit bureaus:** An account in collections still reports on-time payments on other accounts. The negative item doesn't freeze all credit activity.
- **Uber:** A driver with a low rating is warned but can continue driving. Every highly-rated trip improves the rolling average.

**For Submantle:** During probation, agents should continue to accumulate queries toward their trust score. The probation label appears alongside the score, but the formula continues to run. This means:
1. An honest agent on probation due to a mistaken report can continue demonstrating good behavior
2. The score trajectory (improving, stable, declining) is visible to brands
3. A brand can make a sophisticated decision: "Agent is on probation but score has improved 15% in 30 days — the incident may have been a one-time issue"

This is more informative than freezing the score during probation, which hides behavioral evidence.

---

## Section 8: Beta Formula Math — Recovery Analysis

**Formula:** `trust = (q + 1) / (q + i + 2)` where q = total_queries, i = incidents

**Initialization:** New agent with no history: `(0+1)/(0+0+2) = 0.5` — "unknown"

### Recovery Tables

**How many queries to recover to 0.8 after N incidents, starting from zero history:**

| Incidents | Queries needed to reach 0.8 | Notes |
|-----------|---------------------------|-------|
| 1 | ~6 queries | From (0,1): trust = (6+1)/(6+1+2) = 7/9 = 0.78; (7+1)/(7+1+2) = 8/10 = 0.80 |
| 2 | ~14 queries | From (0,2): trust = (14+1)/(14+2+2) = 15/18 = 0.83 |
| 3 | ~22 queries | From (0,3): trust = (22+1)/(22+3+2) = 23/27 = 0.85 |
| 5 | ~38 queries | From (0,5): trust = (38+1)/(38+5+2) = 39/45 = 0.87 |
| 10 | ~78 queries | Formula: need q where (q+1)/(q+i+2) ≥ 0.8; solves to q ≥ 4i + 2 |

**General formula for reaching trust threshold T after i incidents:**
`q ≥ (T × (i + 2) - 1) / (1 - T)`

For T = 0.8: `q ≥ 4i + 6` (approximately)
For T = 0.9: `q ≥ 9i + 16` (approximately)

### The Early Incident Problem

The most acute fairness issue is not many incidents — it is **early incidents**. Consider:

- Agent with 1000 queries and 1 incident: `(1000+1)/(1000+1+2) = 1001/1003 = 0.998`
- Agent with 10 queries and 1 incident: `(10+1)/(10+1+2) = 11/13 = 0.846`
- Agent with 0 queries and 1 incident: `(0+1)/(0+1+2) = 1/3 = 0.333`

**A single incident before ANY legitimate queries drops the score to 0.333 — below the "unknown" baseline of 0.5.** This is the mathematical case for pending state. An incident filed against a brand-new agent before they've had any chance to demonstrate behavior is maximally damaging and maximally gameable (attack a new agent before they build history).

The pending state buffer is not just a fairness mechanism — it is mathematically necessary to prevent incident reports from being used as new-agent suppression attacks.

### Is the Math Fair at Scale?

At scale (100+ queries), the formula is highly forgiving. An agent with 100 queries and 5 incidents scores `101/107 = 0.944`. Recovery is proportional to effort. This is fair.

The formula becomes unfair only in two specific regimes:
1. **Early stage** (q < 20): single incidents have outsized impact
2. **Time-invariant history**: a 3-year-old incident counts identically to yesterday's incident

Both are solvable without changing the formula:
1. Pending state buffers early incidents until q reaches a minimum threshold (e.g., 10 verified queries)
2. Rolling window or incident age decay weights recent incidents more heavily

---

## Section 9: Anti-Gaming Analysis — How Recovery Mechanisms Can Be Abused

### Attack 1: Probation as a Reset Button

**Method:** Register agent → accumulate incidents intentionally → deregister → re-register under new name with fresh 0.5 score.

**Current vulnerability:** Hard DELETE on deregistration means the incident history is gone. Re-registration starts clean.

**Countermeasure (deterministic):** Soft-delete on deregistration. Registration age is always visible to brands ("Registered: 3 days ago"). Brands applying minimum age requirements catch this. The council notes document already identifies soft-delete as a prerequisite.

### Attack 2: Query Flooding to Overwhelm Incidents

**Method:** After accumulating incidents, flood the query endpoint with self-directed queries to push score toward 1.0. Formula is `(q+1)/(q+i+2)` — enough queries overwhelm any fixed number of incidents.

**Current vulnerability:** No velocity caps exist on queries counting toward trust.

**Countermeasure (deterministic):** Velocity caps. Queries above N per hour don't count toward the formula. Query diversity requirements (identical queries don't accumulate trust). Both are in VISION.md anti-gaming rules but not yet implemented.

### Attack 3: Using Probation Window to Shop for Permissive Brands

**Method:** During probation, query brands with low trust thresholds. Use those interactions to accumulate query count. Avoid high-threshold brands until score recovers.

**Assessment:** This is actually correct behavior. An agent with a damaged score should access lower-stakes services while rebuilding. This is exactly how the credit system works — you get a secured credit card after bankruptcy, not a mortgage. This is NOT an attack; it is the intended use of the system.

### Attack 4: Reporter Bombing New Agents

**Method:** Register multiple fake agents as "brands." File incident reports against a new competitor agent before they build query history.

**Current vulnerability:** The 0.333 score after a single early incident (shown above) makes this devastating.

**Countermeasures (deterministic):**
1. Pending state before formula impact (most important)
2. Reporter minimum age: only agents registered for N+ days can file reports that affect the formula
3. Reporter minimum trust: only agents with trust > 0.6 can file reports at full weight
4. Reporter concentration: if 80%+ of an agent's incidents come from one reporter, they're automatically flagged for review

### Attack 5: Dispute Flooding (Gaming the Appeals Process)

**Method:** File disputes on all accepted incidents to delay formula impact indefinitely.

**Countermeasure:** Disputes don't remove incidents from the formula — they add a label ("Disputed"). The brand's withdrawal is what removes the incident. Filing a dispute that is ultimately rejected adds a negative signal to the disputer's own trust metadata (frivolous dispute pattern). Rate-limit disputes to N per rolling period.

---

## Section 10: Status Labels During Probation — What Counterparties Should See

Based on the survey of real-world systems, a graduated label set with progressive disclosure is the right pattern:

| Status | Formula Impact | What Counterparties See | Available Detail |
|--------|---------------|------------------------|-----------------|
| Active | Normal | Trust score + query/incident counts | Full incident list |
| Incident Pending | None yet | "Incident under review" label | Count of pending incidents |
| On Probation | Normal (incidents accepted) | "On Probation" + score + trajectory | Incident detail + resolution status |
| Disputed | Normal (incidents accepted) | "Dispute Filed" label | Incident + dispute status |
| Suspended* | N/A | "Account Inactive" | None |

*Suspension is not a Submantle action — Submantle never acts. If a brand decides not to serve a probationary agent, that is the brand's enforcement. Submantle's label is informational.

**The trajectory signal is underrated.** Showing not just the current score but the 30-day trend ("improving," "stable," "declining") gives brands significantly more decision-making power than a static score. An agent on probation with an improving trajectory is materially different from one with a declining trajectory. This requires storing score snapshots over time, which the `trust_metadata` JSON column already provides a home for.

---

## Section 11: Design Recommendations for Submantle

These are ordered by implementation priority. All are deterministic. None require ML.

### Recommendation 1: Pending State Before Formula Impact (CRITICAL)

Add `status` column to `incident_reports` table with values: `pending | accepted | disputed | withdrawn`.

Only `accepted` incidents increment the `incidents` counter. `pending` incidents appear in the label ("1 incident under review") but do not touch the formula.

Auto-accept after N days with no response from the reporting brand (prevents brands from leaving incidents in limbo forever to suppress competition). Suggested window: 14 days.

**Why critical:** Without pending state, a competitor or bad actor can file a report against a brand-new agent and immediately drop them to 0.333. This is the most urgent anti-gaming gap in the current codebase.

### Recommendation 2: Minimum Query Threshold Before Incidents Apply

Do not allow incidents to affect the formula until the agent has at least M legitimate queries (suggested: M = 10). Before that threshold, incidents go to `pending` regardless. This protects agents in the "vulnerability window" identified in the Beta math analysis.

Implementation: modify `compute_trust()` — if `total_queries < 10`, treat `incidents` as 0 in the formula and add "Early stage — incident review pending" to the trust response.

### Recommendation 3: Rolling Evaluation Window (Time-Based Rehabilitation)

Incidents older than 365 days are archived but excluded from the active formula. They remain visible in the full incident history for brands that want to see complete records.

Implementation: Add `timestamp` filtering to the trust computation. `compute_trust()` queries only incidents from the last 365 days for the formula. Brands can optionally query `compute_trust(include_archived=True)` for the full picture.

**This is the eBay rolling window model.** It is the single most impactful fairness mechanism because it is automatic, non-gameable, and applies symmetrically to all agents.

### Recommendation 4: Reporter Credibility Weighting

Incident weight in the formula is proportional to reporter credibility. In V1, a binary rule:
- Reporters with `trust_score >= 0.7` AND `registration_age >= 30 days`: incident weight = 1.0
- All other reporters: incident weight = 0.5 (still recorded, still labeled, but half formula impact)

Implementation: Compute reporter's own trust score at time of incident filing. Store weight in incident record. Modify `increment_agent_incidents()` to accept a weight parameter.

### Recommendation 5: Score Trajectory Snapshot

Store a daily trust score snapshot in `trust_metadata`. Expose 30-day trajectory in `compute_trust()` response. Label as "improving," "stable," or "declining" based on slope.

Implementation: Trust metadata JSON already exists. Add a `score_history: [{date, score}]` array. Prune to last 90 days.

### Recommendation 6: Dispute Mechanism

Agents can file a dispute against a specific accepted incident, triggering a review request to the reporting brand. The dispute adds a label but does not change the formula. If the brand withdraws, the incident counter decrements. Rate limit: 3 active disputes per agent at any time.

---

## What This Research Does NOT Resolve

1. **Who adjudicates disputes if the reporter doesn't respond?** Credit bureaus require reporters to verify within 30 days or the item is removed. Submantle needs the same rule: if a reporter doesn't respond to a dispute within N days, the incident is auto-withdrawn. But this requires human judgment calls for edge cases. Document the rule, flag for future policy design.

2. **How to handle forks and renamed agents.** A bad actor who soft-deletes an agent and re-registers under a new name still shows "registered yesterday." Brands see this. But there's no cross-agent history linkage. This is a long-term problem (requires author-level reputation, not just agent-level).

3. **Whether the 365-day rolling window is the right duration.** The FCRA uses 7 years for major defaults, 10 for bankruptcy. eBay uses 12 months. Gaming platforms use 90 days. The right duration for AI agents is unknown — there is no empirical data yet. The recommendation of 365 days is a reasonable starting point that can be adjusted as data accumulates.

---

## Key Sources

- 15 USC 1681c: Fair Credit Reporting Act, directly accessed via law.cornell.edu
- eBay Seller Performance Standards: ebay.com/help/selling/seller-levels-performance-standards
- Apple App Store Review process: developer.apple.com/distribute/app-review/
- Steam Subscriber Agreement: store.steampowered.com/subscriber_agreement/
- plan-deepen-notes.md (codebase): Section 4 — Grievance Contextualization / Pattern Detection
- database.py and agent_registry.py (codebase): current schema and trust formula implementation
