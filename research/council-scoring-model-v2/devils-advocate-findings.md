# Devil's Advocate Findings: Weights and Measures — The Scoring Model Evolution
## Date: 2026-03-12
## Role: Devil's Advocate
## Council: Research Council — Scoring Model V2

---

## Orientation

The proposal asks: given that the Beta formula's inputs are the problem (settled), what weighted dimensions should feed into those inputs, how should they compose, and how should that system evolve over time?

My job is not to help design this. My job is to find every assumption that hasn't been tested, every way this could fail, and every risk that is being underestimated. If the design survives, it's ready. If it doesn't, I've saved the project from building something that breaks at first contact with reality.

The prior council already addressed unauthenticated reporting (now solved by eBay model), deregister as hard-delete, and the cold-start 0.5 problem. I will not re-litigate those. What follows are risks the prior council did not fully surface, applied to the specific new complexity this V2 council is being asked to add.

---

## Step 1: What Is Being Proposed

The proposal adds multiple weighted input dimensions to the Beta formula. Specifically:

1. **Incident severity weighting** — different incident types count differently (data exfiltration > timeout)
2. **Reporter credibility weighting** — reports from trusted reporters count more than reports from unknown ones
3. **Interaction volume/diversity** — high-volume agents with diverse queries are treated differently
4. **Corroboration weighting** — multiple reporters on one incident = 1 score hit but higher confidence signal
5. **Agent history depth** — a 10,000-query agent with 1 incident is treated differently from a 10-query agent with 1 incident
6. **Versioned weight evolution** — weights will change over time with documented rationale

The proposal also inherits from the prior council's Team 3 findings: five incident states, dedup via fingerprint rules, formula_weight column (1.0/0.5/0.0), and corroboration_count on incident rows.

---

## Step 2: Codebase Observations

### 2a. The `incidents` counter is mutable and live-wired

`agent_registry.increment_agent_incidents()` increments `incidents` on `agent_registry` directly, immediately, in the same call path as `record_incident()`. The Team 3 proposal correctly identifies that the formula should read from `incident_reports WHERE status = 'accepted'` rather than this counter — but the current code has `compute_trust()` reading `record["incidents"]` from the registry row.

**This is a migration trap.** The proposal assumes the formula will be refactored to count accepted incidents from the reports table. But that requires changing `compute_trust()` to do a JOIN or subquery on every trust calculation, and changing the counter semantics from "eager increment" to "derived count." The current test suite has 160 passing tests. Any of those tests that mock `incidents` directly will silently continue testing the old code path if the counter isn't removed from the registry table. The risk: both code paths co-exist for months, the counter gets incremented on every incident (including pending ones), and compute_trust reads the counter, not the table. The weighting logic lives in the table. The formula ignores the table.

**Neither the existing code nor the Team 3 schema patch removes the `incidents` column from `agent_registry`.** The proposal creates two sources of truth for the incident count.

### 2b. `formula_weight` is a per-incident column — but the formula is a ratio

Team 3 proposes `formula_weight REAL NOT NULL DEFAULT 1.0` on `incident_reports`. The intent: reduced-severity incidents count as 0.5. But the Beta formula is `(q+1) / (q+i+2)` where `i` is an integer count. The proposal implicitly requires `i` to become a sum of floats, not a count of integers.

This is a silent type change. `incidents` in `agent_registry` is `INTEGER NOT NULL DEFAULT 0`. The sum of formula_weights across accepted incidents will be a float. If the formula reads `incidents` from the registry (integer), the weighting is ignored entirely. If it reads the sum of `formula_weight` from the reports table (float), the formula changes in character — it is no longer operating on counts of events but on a weighted sum of severities. The Beta distribution has specific mathematical properties tied to integer alpha/beta parameters. Making beta a float changes those properties and breaks the documented "mean of Beta(alpha, beta) distribution" derivation in `compute_trust()`'s docstring.

**The proposal conflates two different things**: weighting incident impact (what Team 3 means by `formula_weight`) and weighting the reporter's credibility. These interact multiplicatively if both are applied: `effective_weight = severity_weight × reporter_credibility_weight`. Nobody has specified what happens when both apply simultaneously. A 0.5-severity incident from a 0.7-credibility reporter: does it contribute `0.35` to `i`? `0.5`? `0.7`? This is unspecified.

### 2c. Reporter credibility introduces a circular dependency with no bootstrapping solution specified

The proposal says: "a reporter's own trust score and accuracy history should weight their reports." This creates a circular dependency: to have a trust score, reporters need interaction history. To build interaction history, reporters need to file reports. New reporters — including the first brands to adopt Submantle — have no trust score. Their incident reports would be weighted near zero.

The proposal inherits the eBay model (settled), which says: only registered members report. But eBay's seller/buyer trust is built through transactions, not through incident-filing. The mechanism by which a reporter builds "accuracy history" for weighting purposes is never specified. Is it: % of their past incidents that were accepted? % that were not disputed? Some combination? The Team 3 document notes this as an open gap ("Reporter reputation scoring mechanics: the research confirms weighting reports by reporter reputation is standard but provides no specific formula"). This council is being asked to specify what data feeds each dimension — and the reporter credibility dimension has no specified data source yet.

**The circular dependency is worse than it appears.** If reporter credibility weights incident impact, and reporter credibility is built from accuracy history, then the first N incidents any reporter files effectively shape their credibility for all future incidents — but those first N incidents were filed with no credibility weighting applied (since credibility was unestablished). The system cannot retroactively reweight those early incidents when the reporter's credibility is established later. This means: early reporters who file aggressively can establish a credibility baseline that their early reporting influenced.

---

## Step 3: Failure Modes Researched

### 3a. The FICO versioning problem is worse than it looks

FICO has released versions 2, 4, 5, 8, 9, and now 10/10T. The version migration is not a technical problem — it's a market adoption problem. Lenders are still using FICO 2, 4, and 5 as primary scoring models for specific loan products (mortgage Fannie/Freddie requirements specifically). FICO does not force migration. Each lender decides if and when to upgrade. The result: the same consumer has different scores under different versions, and neither FICO nor the lender tells the consumer which version is being used for any given decision.

**Applied to Submantle:** The proposal describes a versioned weight system where "weights WILL evolve over time — versioned, documented, transparent." This sounds clean. FICO shows what it looks like in practice: adopters lock to the version that was current when they integrated, because weight changes require them to recalibrate their own thresholds (a brand that requires trust > 0.8 under V1 weights may need to recalibrate to trust > 0.75 under V2 weights, because V2 weights made all scores shift). The brand's engineering team has to re-test. The brand's risk team has to re-approve. **The proposal assumes brands will adopt weight updates. FICO shows they often won't.** This means Submantle will have live agents being scored under different formula versions simultaneously, with brands making different decisions based on incomparable scores.

**This is not theoretical.** VantageScore was created specifically because Experian, TransUnion, and Equifax wanted a unified model FICO customers could compare across bureaus. FICO's version fragmentation is one of its most-cited criticism in fintech. Submantle is explicitly proposing to repeat this fragmentation by design.

### 3b. Reputation inflation is a documented failure mode of all weighting adjustments

Every reputation system that has modified its weighting to "make scores more meaningful" has produced inflation. eBay's 2008 change from two-sided to one-sided feedback (sellers cannot leave negative feedback for buyers) was designed to make ratings more honest — instead it made positive feedback near-universal. Uber's driver ratings inflated from an average of 4.6 to near 5.0 over time as riders learned that 4 stars causes punishment. Airbnb's rating inflation is documented in academic literature.

The mechanism is consistent: **changing weights changes what actors optimize for**. If a brand learns that "interaction diversity" is now weighted in the trust score, agents will diversify query types mechanically to optimize diversity without genuine behavioral diversity. If "agent history depth" (total_queries) is weighted, agents will pad query counts. The proposal adds multiple dimensions that are individually observable by agents — and therefore individually gameable.

**The prior council noted this risk ("deterministic formulas are easier to reverse-engineer") but treated it as an acknowledged tradeoff.** I'm escalating it: adding more weighted dimensions does not just add more gaming surfaces — it adds *combinatorial* gaming surfaces. An agent optimizing a single-dimension system can choose one strategy. An agent optimizing a multi-dimensional system can explore which combination of gaming behaviors maximizes score most efficiently. This is not speculative; it is the documented pattern from every multi-dimensional reputation system.

### 3c. The "deterministic = EU AI Act exempt" claim is load-bearing and fragile at composite weighting

CLAUDE.md states: "EU Commission guidance (April 2025) explicitly excludes 'systems based on rules defined solely by natural persons to execute operations automatically.' Submantle likely falls outside the Act entirely."

This exemption rests on the scoring being pure arithmetic — "deterministic formulas." The current formula (`(q+1)/(q+i+2)`) is unambiguously arithmetic. But the V2 proposal introduces:

- **Severity classification**: an incident is assigned to a severity tier via deterministic rules ("if incident_type = data_exfiltration, severity = critical"). This is rule-based classification.
- **Reporter credibility weighting**: a reporter's past accuracy rate weights their reports. This requires computing a ratio (accepted_incidents / total_incidents_filed), then applying it as a multiplier. This is a computed attribute derived from aggregate behavioral history.
- **Corroboration weighting**: multiple reports on the same incident increase confidence signal. This requires counting a group and applying a modifier.

Individually, each is arithmetic. In combination, they produce a **composite multi-factor model where input weights are derived from observed behavioral patterns**. The EU AI Act's definitional boundary between "rules defined by natural persons" and "systems that derive patterns from data" is not as clean as the exemption claim assumes. I could not find a legal ruling or Commission guidance that specifically addresses composite multi-factor scoring where intermediate weights are computed from behavioral history rather than hardcoded by a human.

**The specific risk:** adding reporter credibility weighting (a weight derived from the reporter's own behavioral history, not hardcoded by a human) may cross from "rules defined by natural persons" into "system that derives operational parameters from data." This is not a certainty — it is an unresolved legal question that the proposal has not surfaced.

### 3d. Composing dimensions multiplicatively creates score non-linearity that is hard to explain

The proposal says the score must be "fully explainable — any brand can see exactly why a score is what it is." This is possible when the formula is `(q+1)/(q+i+2)`. It becomes substantially harder when `i` is the sum of `formula_weight × reporter_credibility_weight` across accepted incidents, and `q` is velocity-capped total_queries, and the result sits next to a `has_history: false` flag, and the brand also sees corroboration_count and a pending incident pile.

The academic literature on credit scoring consistently shows that consumers (and now software systems consuming scores) cannot meaningfully decompose composite weighted scores even when the formula is disclosed. FICO publishes its five categories and their weights — 35% payment history, 30% amounts owed, etc. — yet the research shows most consumers cannot predict how a specific action (paying off a card) will affect their score. This is because the categories interact non-linearly: amounts owed affects payment history utilization which affects the amounts-owed calculation.

**Submantle's proposed composition will have the same property.** A brand receiving trust = 0.74 with 3 accepted incidents (1 critical severity + 2 standard severity from 70%-credibility reporters) cannot easily verify this from first principles. The "fully explainable" goal is achievable only if the formula is simple enough to verify by hand.

---

## Step 4: Assumption Audit

| Assumption | Status | Evidence |
|------------|--------|----------|
| Brands will adopt weight updates when Submantle versions the formula | **UNVERIFIED** | FICO shows lenders frequently do not migrate. Versioning creates fragmentation, not improvement. |
| Reporter credibility weighting is correctly categorized as "deterministic" for EU AI Act purposes | **UNVERIFIED** | Commission guidance does not address composite systems where intermediate weights are derived from behavioral history. |
| The `incidents` counter in `agent_registry` will be replaced by a derived count from `incident_reports` | **UNVERIFIED** | No migration path specified. Two sources of truth are the most likely implementation outcome. |
| `formula_weight` (float) can be substituted into a formula originally derived for integer Beta distribution parameters | **UNVERIFIED** | The Beta distribution's mathematical properties change when parameters are floats. The docstring's derivation claim becomes incorrect. |
| Reporter credibility can be computed without circular bootstrapping problems | **UNVERIFIED** | No formula specified for bootstrapping new reporters. First N reports from any reporter are filed with unestablished credibility — retroactive reweighting is not proposed. |
| Adding more weighted dimensions produces a more meaningful score | **PARTIALLY VERIFIED** | True in theory. Contradicted in practice by eBay (2008 change), Uber (inflation), Airbnb (inflation). Combination of observable dimensions produces combinatorial gaming surfaces. |
| The composite multi-dimensional score remains "fully explainable" | **UNVERIFIED** | FICO's published weights are insufficient for consumers to predict score behavior. Multi-factor composites are systematically harder to explain than single-formula scores. |
| Severity classification rules will remain stable once defined | **UNVERIFIED** | No process specified for updating severity thresholds without triggering a formula version change. |

---

## Step 5: Counter-Evidence

### Against weighted composite scoring for V1

The prior council (synthesis.md) cited Klout as a failure case for score complexity and explicitly filtered "category-specific scores for V1" as too complex. The decision to "record types now, weight later" was reached after the External Researcher reversed their own recommendation in the challenge round. The rationale was: "complexity kills early reputation systems."

The V2 proposal is now asking for severity weighting, reporter credibility weighting, interaction diversity weighting, and corroboration weighting — simultaneously — in what it calls V1. This is not "simple weighted inputs." This is the category-specific scoring that was rejected, reframed as "input enrichment." The practical effect on formula complexity is the same.

### Against reporter credibility weighting specifically

The ScienceDirect paper on "endorsement-based trust bootstrapping for newcomer cloud services" (referenced in external search results) identifies the bootstrapping problem in reporter credibility systems as a fundamental structural challenge. Their proposed solution requires either a pre-trusted seed set (centralized authority) or a prolonged cold-start period (commercially useless). Neither fits Submantle's model.

Bayesian trust models with reporter credibility weighting do achieve higher transaction success rates — but only in mature systems with established history. In early-stage systems with sparse interaction graphs, reporter credibility weighting suppresses signal from exactly the parties who are most likely to have valid early incident reports: new brands with no established history.

### Against formula_weight as a float modifier

The original Beta Reputation System paper (Josang, 2002) uses integer alpha/beta parameters by design. The mean of Beta(α, β) = α/(α+β) works cleanly with integer counts. Converting beta (the incidents parameter) to a float sum of formula_weights preserves the arithmetic but destroys the theoretical grounding. You no longer have "observed incidents" and "prior belief" as interpretable parameters — you have a weighted sum with a Beta distribution label. This is not necessarily wrong mathematically, but it requires re-deriving the confidence interval interpretation. The current docstring's claim ("This is the mean of Beta(alpha=queries+1, beta=incidents+1)") becomes incorrect.

---

## Step 6: What I Could Not Disprove

The following elements of the proposal appear sound to me and I could not find evidence against them:

1. **Recording interaction types now without weighting them** — the consensus position from the prior council's challenge round is supported by all major evidence. FICO's versioning problem actually strengthens this: if weights are not embedded in the formula yet, there is nothing to migrate. Recording data without committing to weights is the correct approach for V1.

2. **Corroboration as a confidence signal, not a formula multiplier** — the Team 3 design (1 score hit regardless of corroboration count, but corroboration_count visible to brands) is correct. Multiple reporters on the same incident is credibility information, not frequency information. The formula should not multiply it; the dashboard should surface it.

3. **Dedup logic being server-side and reporter-non-influenceable** — Team 3's observation that PagerDuty's sender-defined dedup_key is gameable, and Submantle must compute dedup_key server-side, is correct. I could not find a counterargument.

4. **The five-state incident workflow (suspicious → pending → accepted/expired/disputed)** — the state machine design is well-grounded in eBay, FCRA, and Amazon precedent. The 14-day expiry for unsubstantiated incidents is defensible. The 72-hour agent response window is aggressive but appropriate for a non-legal-obligation system.

5. **Severity classification as a processing-path determinant, not a formula weight** — Team 3's content-moderation mapping (severity determines which tier processes an incident, not the formula impact) is sounder than embedding severity as a `formula_weight` modifier. Severity affecting processing path = deterministic rules. Severity affecting formula input weight = the float-in-integer-formula problem.

---

## Score Table

### Role-Specific Dimensions

| Dimension | Score | Justification |
|-----------|-------|---------------|
| **Failure Probability** | 4 | The two-sources-of-truth migration trap and the reporter credibility circular dependency are likely to produce implementation errors. The overall direction is sound, but the specific composition details have enough unresolved precision to produce a broken build. |
| **Failure Severity** | 5 | If formula_weight floats are used with the integer-derived Beta formula, scores are wrong but consistently wrong — brands would be making decisions on a miscalibrated signal without knowing it. This is medium-high severity: not catastrophic but silently incorrect. |
| **Assumption Fragility** | 3 | Five of eight audited assumptions are unverified. The EU AI Act exemption claim is load-bearing and fragile under the proposed complexity additions. The reporter credibility bootstrapping problem is unresolved. |
| **Hidden Complexity** | 4 | The migration from eager-increment `incidents` counter to derived count from `incident_reports` is non-trivial. The circular dependency in reporter credibility requires a bootstrapping protocol. Weight versioning requires an adoption protocol that doesn't exist. The proposal surfaces the end-state design but not the path to get there. |

### Shared Dimensions

| Dimension | Score | Justification |
|-----------|-------|---------------|
| **Overall Risk** | 4 | The direction is correct. The specific mechanisms for composing weighted dimensions are underspecified in ways likely to produce a subtly broken implementation — particularly the float formula_weight in an integer Beta formula, and the two-sources-of-truth incident count. |
| **Reversibility** | 6 | Recording interaction types without weighting is fully reversible. Adding formula_weight to incident_reports is a schema change that can be added without breaking existing scores. The hard-to-reverse element is embedding reporter credibility weighting into the formula: once reporters have credibility scores, changing the weighting formula retroactively reweights all historical incidents. |
| **Evidence Confidence** | 7 | FICO versioning fragmentation is well-documented fact. Reputation inflation in multi-dimensional systems is supported by academic literature and documented eBay/Uber behavior. The EU AI Act legal risk is speculative but grounded in the gap between the Commission's guidance scope and the proposed system's actual mechanism. |

---

## Summary of Highest-Priority Risks

**Risk 1 — Two sources of truth for incident count (HIGH)**
The proposal does not specify removing `incidents` from `agent_registry`. Until it does, `compute_trust()` reading the registry counter and the new formula reading the `incident_reports` table will co-exist. The registry counter is incremented eagerly; the table-based count reflects only accepted incidents. This produces systematically lower trust scores than intended, with no visible error.

**Risk 2 — Float formula_weight breaks the Beta distribution derivation (MEDIUM)**
`formula_weight REAL` on `incident_reports` means `i` in `(q+1)/(q+i+2)` becomes a float sum. This is not a catastrophic failure — the arithmetic still works — but the theoretical grounding (mean of Beta distribution with integer parameters) is incorrect. The docstring becomes a lie. More importantly, applying reporter credibility as a second multiplier (`effective_weight = severity × credibility`) compounds this: the formula is now a weighted sum of weighted sums pretending to be a Beta reputation system.

**Risk 3 — Reporter credibility circular dependency has no specified bootstrapping solution (HIGH)**
New reporters file their first N incidents with no credibility weight. Those incidents either count with full weight (defeating the credibility system) or count with zero weight (making reporting commercially useless for new brands). The proposal does not resolve this. The eBay model (settled) only solved unauthenticated reporting — it did not solve how credibility bootstraps.

**Risk 4 — Weight versioning creates FICO-style fragmentation (MEDIUM)**
Brands will lock to the formula version current at their integration time. Weight updates require brands to recalibrate thresholds. FICO's history shows this recalibration rarely happens. Submantle will accumulate a fragmented ecosystem of brands comparing incomparable scores within years of launch. The "versioned, documented, transparent" framing makes this sound like a feature; it is a documented failure mode in every credit scoring system that attempted it.

**Risk 5 — EU AI Act exemption claim is fragile under composite behavioral weighting (MEDIUM)**
Reporter credibility weighting (where the weight is derived from the reporter's behavioral history, not hardcoded) is the specific mechanism most likely to attract regulatory scrutiny. The Commission's "rules defined solely by natural persons" language targets systems where parameters are hardcoded — not systems where operational parameters (the credibility weight) are computed from observed data. This is an unresolved legal question, not a settled one.
