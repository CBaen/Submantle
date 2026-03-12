# Council Synthesis: Scoring Model V2 — Weights and Measures
## Date: 2026-03-12
## Vetted by: Orchestrator
## Alignment: Checked against Research Brief + GL rulings (2026-03-12)
## Council members: Codebase Analyst, External Researcher, Devil's Advocate
## Phases completed: Phase 1 (independent research), Phase 2 (challenge round)
## Phase 3 skipped: Challenges refined positions without introducing fundamental new research questions. Convergence was strong enough to synthesize.

---

## GL Rulings Incorporated

Three contested decisions from the Trust Lifecycle Expedition were ruled on by GL during this session:

1. **"Suspended" label renamed** — GL ruled the word implies enforcement power Submantle doesn't have. Replace with a neutral informational label. Agents can self-identify issues voluntarily; interaction logs prove honesty.
2. **Dispute timeout: auto-withdraw** — confirmed. Matches FCRA model. Unsubstantiated claims drop.
3. **Minimum interaction threshold needs math** — GL ruled this cannot be an arbitrary number. Must determine what interaction types count, the mathematical basis for the threshold, and account for the fact that even refusal-of-exchange is an interaction.

---

## Master Score Table

### Role-Specific Scores (Phase 1 → Post-Challenge)

| Dimension | Codebase Analyst | External Researcher | Devil's Advocate | Spread |
|-----------|-----------------|---------------------|------------------|--------|
| **Feasibility** | 8/10 | N/A (external focus) | N/A | — |
| **Blast Radius** | 7/10 | N/A | N/A | — |
| **Pattern Consistency** | 8/10 | N/A | N/A | — |
| **Dependency Risk** | 7/10 | N/A | N/A | — |
| **Failure Probability** | N/A | N/A | 4/10 (higher=worse) | — |
| **Failure Severity** | N/A | N/A | 5/10 (medium) | — |
| **Assumption Fragility** | N/A | N/A | 3/10 (low=fragile) | — |
| **Hidden Complexity** | N/A | N/A | 4/10 | — |
| **Overall Risk** | 7/10 | varies by approach | 4/10 | 3 |
| **Reversibility** | 6/10 | N/A | 6/10 | 0 |
| **Evidence Confidence** | 9/10 | N/A | 7/10 | 2 |

### Post-Challenge Score Adjustments

| Score | Original | Challenge Revision | Who Revised | Why |
|-------|----------|--------------------|-------------|-----|
| DA Failure Probability | 4/10 (whole proposal) | Split: severity weighting 8/10 likely to succeed; reporter credibility 2/10 near-certain to fail as specified | CA challenge | Proposal contains two components with very different risk profiles |
| DA EU AI Act risk | MEDIUM | LOW-MEDIUM | DA self-revision | SecurityScorecard precedent: deterministic scoring with behavioral inputs operates under EU regulatory scrutiny successfully |
| ER Reporter credibility | V1 ship requirement | V2 / Go rewrite | ER self-revision | Codebase dependency chain shows 8 prerequisites; bootstrapping unresolved |
| ER Severity approach | Formula weight (1.0/0.7/0.3) | Processing path / routing | ER partial reversal | DA's argument: routing avoids float-in-Beta entirely |
| CA Two-sources-of-truth | Not explicitly scored | MEDIUM (test suite catches it) | CA challenge | Integration tests fail immediately if counter and table diverge |
| DA Bootstrapping severity | HIGH | MEDIUM (D&B diversity threshold is alternative) | DA self-revision | D&B two-reporter minimum delegates threshold to brands, sidestepping formula bootstrapping |

---

## High Confidence Findings (Triple Convergence)

These findings emerged from independent analysis by all three agents and survived the challenge round. The council treats these as settled.

### 1. Pending State Must Precede Any Formula Change

The formula cannot safely read from `incident_reports WHERE status='accepted'` until the status column and state machine exist. Without it, the formula reads zero accepted incidents and returns perfect scores. CA's dependency chain, DA's migration trap warning, and ER's eBay DSR precedent all converge.

**Implementation:** Step 3 in CA's dependency chain. Non-negotiable prerequisite.

### 2. The Aggregate `incidents` Counter Must Stop Being the Formula Input

The mutable counter on `agent_registry` was built for speed but makes pending state impossible. All three agents independently identified this. The transition: `compute_trust()` reads `SUM(formula_weight) FROM incident_reports WHERE status='accepted'`. The counter becomes a deprecated cache, then is removed.

**Critical addition from DA challenge:** The API response must also change. If the API returns `incidents: 5` (from the counter, including pending) but the score reflects only 3 accepted incidents, brands see inconsistent data. The `incidents` field in the API response must reflect `accepted_incidents`, not the raw counter.

### 3. Reporter Credibility Weighting Is V2 (Go Rewrite)

All three agents converged after the challenge round:
- CA: 8 prerequisite steps before infrastructure exists
- ER: Reversed own position — dependency chain evidence places it in V2
- DA: Bootstrapping circular dependency unresolved; EU AI Act risk if behavioral weights enter formula

The D&B two-reporter diversity minimum (surface `reporter_diversity` count in API metadata, let brands set their own threshold) sidesteps the bootstrapping problem entirely for V1.

### 4. Two-Track Architecture: Beta Score + trust_metadata Enrichment

The primary Beta formula produces the score. `trust_metadata` holds everything else: velocity data, query type breakdowns, reporter concentration flags, corroboration counts, pending incident counts. Brands see both. The formula stays clean; the metadata gets rich.

Validated by: eBay (DSRs alongside feedback count), Airbnb (sub-ratings alongside star rating), Uber (sub-dimensions alongside 1-5 score). Production-proven at scale.

**Caveat from ER challenge:** Signals in `trust_metadata` are "data under observation, not validated scoring dimensions." Brands should understand the data is there but unvalidated until real-world patterns emerge.

**Caveat from DA challenge:** Anti-gaming counters (velocity caps) must NOT go in trust_metadata JSON. The read-modify-write pattern has a race condition under concurrent writes. Velocity caps need atomic increment operations — separate columns or separate table, not JSON fields.

### 5. Record Interaction Types Now, Weight Later

Reaffirms prior council's settled decision. New evidence:
- VantageScore 4.0 added trended data as a modifier, not replacement (ER)
- Recording without weighting means nothing to migrate when weights change (DA)
- Codebase has no interaction logs yet — the infrastructure gap is the real work (CA)

### 6. Score Version Tagging Ships in V1

Every score returned by the API includes `score_version: "v1.0"`. Cost: 5 minutes. The settings table already supports it. Not having it creates an API contract problem when weights inevitably change.

FICO version fork model (not SecurityScorecard simultaneous recalibration) — brands build thresholds against a labeled version and choose when to upgrade. For V1, there's only one version, but the field must exist from day one.

### 7. Corroboration Is Metadata, Not Formula Multiplier

Multiple reporters on one incident = 1 score hit. `corroboration_count` is visible to brands in `trust_metadata`. The formula does not multiply it. One incident, regardless of how many reporters confirm it, is one incident. Brands can use corroboration count to assess confidence.

### 8. `has_history` Flag Ships in V1

Distinguishes "unknown agent" (no interaction history) from "low-scoring agent" (history exists, score is bad). FICO and D&B both make this thin-file / no-file distinction. One boolean in the API response. One test assertion to update.

### 9. `reporter_diversity` Ships in V1 API Metadata

Count of distinct registered reporters who have interacted with or filed reports about an agent. D&B's two-reporter minimum is the precedent. A brand seeing trust=0.87 from 1 reporter makes a different decision than trust=0.87 from 12 reporters. Costs one `COUNT(DISTINCT reporter_agent_id)` query.

---

## Recommended Approach: V1 Scoring Model

### The Formula Stays Simple for V1

```
q = total_queries (velocity-capped)
i = COUNT(*) FROM incident_reports WHERE agent_id=? AND status='accepted'
trust = (q + 1) / (q + i + 2)
```

**Key V1 decision: incidents are COUNTED, not weighted.** Severity determines the processing path (which review tier handles the incident, how fast it expires), not the formula impact. This preserves the Beta formula's integer-parameter theoretical grounding. Float formula_weight is deferred to V2 when outcome data can calibrate the weights.

This means for V1:
- A critical incident and a standard incident both count as 1 in the formula
- But a critical incident goes to immediate human review (Tier 1) and gets processed faster
- A standard incident has a 14-day expiry window
- Severity affects HOW an incident is handled, not HOW MUCH it hurts the score

### The API Response Gets Rich

```python
{
    "agent_name": ...,
    "trust_score": 0.847,
    "score_version": "v1.0",
    "has_history": True,
    "total_queries": 500,
    "accepted_incidents": 3,        # replaces raw counter
    "pending_incidents": 1,         # transparency
    "reporter_diversity": 4,        # distinct reporters
    "registration_time": ...,
    "last_seen": ...,
    "version": ...,
    "author": ...,
    "trust_metadata": {             # enrichment layer
        "query_types": {"verify": 300, "process_check": 200},
        "incident_types": {"timeout": 2, "rate_limit": 1},
        "corroboration_max": 3,     # highest corroboration on any incident
        "agent_age_days": 45
    }
}
```

### The Dependency Chain (V1 Scope: Steps 1-6)

From CA's dependency chain, validated by all three agents:

```
1. trust_metadata enrichment (no prerequisites)
   ↓
2. Soft-delete for agent_registry (history preservation)
   ↓
3. Pending state on incident_reports + expires_at + status column
   ↓
4. compute_trust() reads accepted incidents from incident_reports table
   ↓
5. Severity classification for incidents (processing path, not formula weight)
   ↓
6. Score version tag + has_history + reporter_diversity + accepted_incidents in API response
```

Steps 7-9 (interaction_logs table, reporter auth, reporter credibility) are V2 / Go rewrite territory. Step 10 (weight versioning infrastructure) can ship alongside Steps 4-6 since it's pure additive.

---

## Severity as Processing Path — The V1 Model

This is the most consequential design decision this council produced. The DA argued for it in Phase 1; the ER reversed to it in the challenge round; the CA provided the codebase evidence that supports it.

**V1 severity classification (deterministic rules, no ML):**

| Severity | Example | Processing Path | Formula Impact | Review Tier |
|----------|---------|----------------|----------------|-------------|
| Critical | data_exfiltration, unauthorized_access | Immediate human review queue | 1 (full count) | Tier 1 |
| Standard | timeout, rate_limit_violation, api_misuse | 14-day expiry window | 1 (full count) | Tier 2 (auto) |
| Reduced | minor_version_mismatch, formatting_error | 30-day expiry, auto-expire likely | 1 (full count) | Tier 3 (auto) |
| Suspicious | potential_self_ping, velocity_anomaly | Flagged for pattern analysis | 0 (no formula impact until accepted) | Tier 2 |

**V2 evolution:** Once outcome data validates calibration, severity can move from processing-path-only to formula weight. `formula_weight` column ships in V1 schema (defaulting to 1.0 for all accepted incidents) so the infrastructure is ready. The column exists; the formula doesn't read it yet.

---

## The Minimum Interaction Threshold — Open Gap

GL ruled this cannot be an arbitrary number. The council did not produce the math. Here's the framework:

For Beta(q+1, i+2) with zero incidents, the score's reliability depends on q:

| Interactions (q) | Score | 95% Credible Interval Width | Interpretation |
|-------------------|-------|----------------------------|----------------|
| 0 | 0.500 | ~0.95 | Completely unknown |
| 5 | 0.778 | ~0.55 | Very unreliable |
| 10 | 0.846 | ~0.38 | Moderately unreliable |
| 25 | 0.929 | ~0.20 | Becoming meaningful |
| 50 | 0.962 | ~0.12 | Fairly reliable |
| 100 | 0.980 | ~0.07 | Reliable |

**The threshold depends on what brands need.** If a brand requires >90% confidence that the true trust exceeds 0.7, the math dictates a minimum. This is a computable answer per brand threshold, not a universal number.

**Recommended V1 approach:** Don't enforce a threshold. Instead, surface `has_history: true/false` (any interactions at all), `total_queries` (raw count), and let brands set their own floors. A brand can implement "require total_queries >= 25 before trusting this score" on their side. This is the D&B model — the bureau publishes the data; the lender decides what's sufficient.

GL's point that "even refusal-of-exchange is an interaction" maps cleanly: any authenticated API call that touches an agent's record (query, verify, denied-access-logged) increments `total_queries`. The interaction type is recorded in `trust_metadata`. Brands can filter by type if they want.

**Research gap:** The statistical analysis above should be validated by a follow-up expedition when real interaction data exists. The Beta formula's credible interval narrows predictably, but the right threshold depends on commercial context (financial services need tighter intervals than social platforms).

---

## Deregistered Agent Names — Credit Bureau Model

The CA raised this as the "highest-consequence unresolved design question." The ER's D&B evidence clinches it:

**Deregistered agent names are permanent records. Re-registration with the same name under a different key creates a new entity.**

D&B's D-U-N-S numbers are permanent and never reused. Equifax doesn't delete credit files when accounts close. Submantle is a credit bureau. The name slot stays occupied. This prevents bad actors from deregistering compromised agents and re-registering with a clean slate.

The test `test_deregister_then_reregister_same_name` should be updated: re-registration with a deregistered name fails (or creates a new entity with a different internal ID and the name visibly modified, e.g., `my-agent (v2)`).

**This modifies the prior council's recommendation** ("re-registration inherits history"). The new position: history is permanent and belongs to the original entity. A new registration with the same name is treated as a successor entity with its own fresh history, clearly distinguished.

---

## Alternatives Considered

### A. Severity as Formula Weight (Rejected for V1)

ER's original proposal: `i = SUM(formula_weight)` where critical=1.0, standard=0.7, reduced=0.3. Produces a more nuanced score. Rejected because:
- Float `i` breaks Beta distribution's theoretical grounding (DA)
- No outcome data to calibrate weights (ER self-revision)
- Severity as routing achieves the priority-processing benefit without formula complexity (DA)

**V2 path:** When outcome data exists, severity weighting can be added with explicit `score_version` bump. The `formula_weight` column ships in V1 schema to avoid later migration.

### B. SecurityScorecard Simultaneous Recalibration (Rejected)

All entities get new scores simultaneously when weights change. Rejected because:
- Punishes early adopters who built threshold logic (ER)
- Requires all brands to recalibrate at once (DA)
- FICO version fork is the standard pattern for threshold-sensitive consumers (ER)

### C. Reporter Credibility in V1 (Rejected)

PeerTrust Cr(v) mechanism: `effective_weight = severity × reporter_credibility`. Rejected because:
- 8 infrastructure prerequisites don't exist (CA)
- Bootstrapping circular dependency unresolved (DA)
- EU AI Act risk increases with behavioral-history-derived weights (DA, revised to LOW-MEDIUM)
- D&B `reporter_diversity` sidesteps the problem for V1 (DA self-revision)

---

## Filtered Out

| Item | Source | Why Filtered |
|------|--------|-------------|
| Rolling window / time decay | ER Gap 1 | Out of V1 scope. Data collection (timestamps on queries and incidents) ships now. Analysis deferred to V2. |
| `metadata_maturity: experimental/validated` per dimension | ER challenge | Over-engineering for V1. All metadata is implicitly experimental at launch. |
| Qualys multiplicative-additive hybrid for severity×credibility | ER Gap 2 | Relevant only when both severity weighting AND reporter credibility are active. Neither is in V1 formula. Filed for V2 reference. |
| Bilateral outcome confirmation | Prior expedition | V2. Network needs density first. |
| Divergence multiplier | ER Phase 1 Layer 4 | V2. Concept requires validated baseline scores to detect divergence. |

---

## Disagreements Resolved During Synthesis

### 1. Feasibility: CA 8/10 vs DA-implied 6/10

**Resolution: 7/10.** CA's structural analysis is accurate — the formula, DB, and registry are cleanly separated. DA's counter about API data integrity and soft-delete naming collision are valid deductions. The average reflects both: technically feasible with known semantic questions that must be resolved before implementation begins.

### 2. Two-Sources-of-Truth Severity: CA MEDIUM vs DA HIGH

**Resolution: MEDIUM, with a mandatory fix.** CA is correct that the test suite catches divergence immediately (integration tests, not unit tests). DA is correct that the API response must be updated to show `accepted_incidents` instead of the raw counter. The risk is MEDIUM because it's catchable, but the fix is mandatory — ship the API response change alongside the formula change, not after.

### 3. Float-in-Beta: Theoretical vs Practical

**Resolution: Avoided entirely for V1.** By choosing severity-as-routing over severity-as-formula-weight, the Beta formula keeps integer parameters in V1. The docstring remains accurate. The `formula_weight` column exists in schema (defaulting to 1.0) for V2 readiness, but the formula reads `COUNT(*)` not `SUM(formula_weight)`.

---

## Risks

### 1. Score Inertia for High-History Agents (MEDIUM)
ER identified: an agent with q=5000, i=0 that gets compromised barely shows score impact from new incidents. 50 incidents: score goes from 0.999 to 0.990. This is a known failure mode of all cumulative scoring systems. No V1 fix — but timestamped incidents and queries enable V2 recency analysis.

### 2. Combinatorial Gaming Surfaces (MEDIUM)
DA identified: multi-dimensional visibility (agents can see what's weighted) creates optimization surfaces. Mitigated for V1 by: (a) severity doesn't affect formula, (b) reporter credibility not in formula, (c) velocity caps, (d) interaction types recorded but not weighted. The formula input is just `count of accepted incidents` — one dimension, hard to game without colluding reporters.

### 3. Counter/Table Migration (LOW-MEDIUM)
The transition from eager-increment counter to accepted-incident-count query. Mitigated by: CA's COALESCE approach + mandatory API response update + integration tests that catch divergence immediately. Must be a single atomic deployment, not phased.

### 4. Soft-Delete Naming Collision (LOW-MEDIUM)
SQLite doesn't support partial unique indexes. Application-level uniqueness check introduces a (theoretical) race condition. At V1 prototype scale with single-threaded SQLite, this is not a practical concern. For Go rewrite, PostgreSQL partial indexes solve this cleanly.

### 5. Dispute Resolution Schema Gap (LOW)
DA identified: the `disputed` state needs two exit states (upheld / dismissed). Without them, disputes accumulate with no resolution mechanism. Requires `dispute_outcome TEXT` column (`upheld`/`dismissed`) and `dispute_resolved_at REAL`. Low risk because implementation naturally surfaces this.

### 6. trust_metadata Race Condition for Anti-Gaming Counters (LOW)
DA challenge: velocity cap counters in JSON trust_metadata can be lost under concurrent writes. Mitigated by: separate atomic-increment columns for velocity counters (not JSON fields). Display-only metadata in JSON is safe.

---

## Evidence Quality Summary

| Agent | Phase 1 Evidence | Challenge Round Evidence | Overall |
|-------|-----------------|------------------------|---------|
| Codebase Analyst | 9/10 — specific file lines, Grep-verified, test counts confirmed | Strong — identified 4 evidence gaps in other agents' work | Highest internal evidence quality |
| External Researcher | 8/10 — cited systems with dates, multiple precedents per claim | Self-revised on 2 key positions after seeing codebase evidence | Highest external evidence quality; intellectual honesty in reversals |
| Devil's Advocate | 7/10 — FICO fragmentation well-documented, EU AI Act claim grounded in regulatory gap | Revised EU AI Act risk downward, endorsed D&B alternative | Most valuable adversarial contribution: severity-as-routing insight |

---

## Implementation Sequence — V1 Scoring Model Build

Derived from CA's dependency chain, filtered through all three agents' challenge round findings and GL's rulings:

### Wave 1 (No dependencies)
- [ ] Start writing to `trust_metadata`: velocity data, query type breakdowns
- [ ] Add `score_version: "v1.0"` to `compute_trust()` response
- [ ] Add `has_history` boolean to `compute_trust()` response
- [ ] Update `test_compute_trust_returns_metadata` key assertion

### Wave 2 (Soft-delete)
- [ ] Add `agent_status` column to `agent_registry` (active/deregistered)
- [ ] Change `deregister_agent()` from DELETE to UPDATE
- [ ] Implement credit bureau model: deregistered names are permanent records
- [ ] Update 4 affected tests

### Wave 3 (Pending state — prerequisite for formula change)
- [ ] Add `status`, `severity`, `formula_weight`, `expires_at`, `dispute_filed_at`, `dispute_outcome`, `dispute_resolved_at`, `corroboration_count`, `dedup_group_id`, `reviewed_by`, `reviewed_at` to `incident_reports`
- [ ] Implement five-state machine: suspicious → pending → accepted/expired/disputed
- [ ] Severity classification rules (deterministic, processing-path only)
- [ ] Deduplication via server-side sha256 fingerprinting

### Wave 4 (Formula change — requires Wave 3)
- [ ] `compute_trust()` reads `COUNT(*) FROM incident_reports WHERE status='accepted'` instead of aggregate counter
- [ ] Deprecate `incidents` counter on `agent_registry` (keep for backward compat, stop using in formula)
- [ ] API response: `accepted_incidents` and `pending_incidents` replace raw `incidents`
- [ ] Add `reporter_diversity` to API response
- [ ] Update 5 affected formula tests

### Wave 5 (Parallel with Waves 3-4 — MCP server)
- [ ] MCP server wraps existing modules (thin Python, stdio transport)
- [ ] Trust score query via MCP
- [ ] Incident reporting via MCP

---

## Open Gaps for Future Research

1. **Minimum interaction threshold math** — GL requires research-backed statistical basis. Framework provided above (Beta credible intervals). Needs validation against commercial context.
2. **Score inertia mitigation** — High-history compromised agents barely show score impact. Needs recency-weighting or sliding-window analysis for V2.
3. **Interaction type taxonomy** — What types exist, how they're classified, whether refusal-of-exchange generates its own type. Needed before interaction_logs table is built (Wave 2 of V2).
4. **Neutral label for "Suspended" status** — GL rejected "Suspended." Need a term that communicates "this agent has unresolved critical incidents" without implying enforcement. Candidates: "Flagged," "Under Review," "Unresolved Incidents." (Note: "Under Review" already exists as a label from the Trust Lifecycle Expedition.)
5. **Self-identification mechanism** — GL raised: agents/users can voluntarily self-identify issues. Design needed for how this surfaces in the API and whether self-reported issues affect the formula differently.
