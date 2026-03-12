# Codebase Analyst Challenge: Scoring Model Council
## Date: 2026-03-12
## Challenging: External Researcher Findings + Devil's Advocate Findings

---

## Framing Note

My findings come from the actual code: `agent_registry.py`, `database.py`, `api.py`, and the test suite. Where the other agents reasoned from analogy and assumption, I can cite line numbers and schema definitions. That changes the confidence level on several of their conclusions and the urgency ordering of their recommendations.

---

## 1. Reasoning Divergence Points

### Divergence A: The "reporter authentication" problem — we agree on the conclusion but disagree on the severity

Both agents identify unauthenticated incident reporting as the top vulnerability. I agree. But the Devil's Advocate frames it as "CRITICAL" in isolation without noticing that the codebase already has a partial structural hook for solving it.

The `reporter` field in `incident_reports` is already there. The `agent_id` foreign key constraint is already enforced. The missing piece is a `reporter_id` FK pointing to a verified business registry — not a new table, not a new concept. The schema is one column and one new table away from the credit bureau model's credentialed furnisher requirement.

**The divergence:** The Devil's Advocate says unauthenticated reporting is a structural flaw requiring architectural rethink. The codebase evidence says it's a gap in a schema that was already designed with attribution in mind. These lead to different remediation scopes.

### Divergence B: The deregister/score-reset problem — the Devil's Advocate missed it entirely

The External Researcher does not address the deregister path at all. The Devil's Advocate lists "Sybil Attacks" as MEDIUM severity and "self-querying" as CRITICAL, but neither agent identified what the codebase reveals: `deregister_agent()` at line 323 of `database.py` does a hard DELETE, which means a low-scoring agent can wipe its entire history and re-register with a fresh 0.5.

This is the most structurally damaging gaming vector, and neither agent found it. The credit bureau model's entire value proposition is that negative history persists. A hard DELETE breaks this at the database layer, not at the API layer. Rate limits and reporter authentication don't protect against it.

**The divergence:** The other agents focus on input gaming (inflation via query spam, incident spam). The codebase reveals an output gaming path (score reset via deregistration) that bypasses every input-side control.

### Divergence C: Weighted interaction types — the External Researcher overstates the complexity

The External Researcher cites FICO's five weighted categories and suggests Submantle should adopt differentiated query types, noting the `capabilities` field as a natural hook. The Devil's Advocate correctly identifies that complexity kills early reputation systems (Klout, Facebook Trustworthiness Score) and recommends one score for V1.

The codebase provides a third angle neither agent had: `trust_metadata` is a JSON column that already exists on every agent row, has a write method (`update_trust_metadata()` at database.py line 338), and is currently unused. The codebase has already pre-built the storage layer for interaction breakdowns without changing the formula. This means the correct path is not "add weights now" or "defer weights forever" — it's "record interaction types in trust_metadata today, add weights to the formula only when you have real data to calibrate them."

**The divergence:** The External Researcher says "add weights" and the Devil's Advocate says "stay simple." The codebase says there is a third option: record without scoring, enabling calibrated weights later without a retroactive data problem.

### Divergence D: The enforcement boundary — the Visa analogy is more precise than either agent claims

The External Researcher calls the payment network model "NOT neutral in practice" because Visa fines and terminates. The Devil's Advocate says "neutral infrastructure should never enforce" is "dangerous if held rigidly" and recommends a minimal abuse-response floor.

The codebase is more specific: `deregister()` in `agent_registry.py` at line 304 only accepts a token that matches the calling agent. There is no admin deregistration endpoint. No admin authentication exists anywhere in the codebase. The architecture is currently MORE neutral than Visa — Submantle has literally zero enforcement capability, not even the MATCH-list equivalent.

The External Researcher's enforcement boundary analysis (CA revocation model) maps precisely: Submantle could maintain a "revoked agents" list without blocking anyone. Revoking an attestation is not the same as terminating an account. The codebase has no equivalent of either. Building a MATCH-list analog (a `revoked_agents` table, a status flag on `agent_registry`) is architecturally trivial. Building actual enforcement (blocking `record_query()` for low-score agents) would violate Design Principle 4. These are very different things and both agents conflated them.

---

## 2. Score Challenges

### External Researcher: eBay/Amazon Seller Ratings — Relevance 7/10

I would score this 5/10. The two-sided grading problem (sellers retaliate against buyers) is structurally absent in Submantle. Brands report on agents; agents do not report on brands. The asymmetry insight is real, but it applies to a problem Submantle doesn't have. The External Researcher acknowledges this ("Submantle is one-sided") but still gives 7. The relevant lesson — behavioral outcomes over explicit ratings — is already covered at 9/10 by the credit bureau analog. The marginal contribution of the eBay section is low.

### External Researcher: App Stores — Relevance 5/10

I agree with 5/10. The binary in/out model is the right disqualifier.

### External Researcher: Signet — Relevance 10/10

I would score this 8/10 on relevance and flag it as a competitive threat more explicitly than the External Researcher does. Signet's 0–1000 composite score from five weighted dimensions (Reliability 30%, Quality 25%, Financial 20%, Security 15%, Stability 10%) with API response under 50ms and a persistent cross-platform ID is the closest competitive feature match to what Submantle's trust layer would be. The LLM-swap decay rule (25% decay on model change) is directly relevant to CLAUDE.md's "what counts as the same agent across version upgrades" open question. This deserves more weight than "10/10 relevance, currently free" — the maturity score of 6/10 undersells it as a signal that the space is being built now.

### Devil's Advocate: Score Inflation via Self-Querying — CRITICAL

I agree this is critical. But the Devil's Advocate stops at diagnosis. The codebase reveals the exact fix is two lines: a `rate_limit` entry or a per-agent `queries_last_hour` counter in `trust_metadata`. Neither exists. The Devil's Advocate correctly identifies it but doesn't distinguish between "easy to fix, not yet fixed" and "hard to fix." This is easy to fix. The urgency is high; the remediation scope is not.

### Devil's Advocate: Cold Start as "commercially useless" — OVERSTATED

The 0.5 initialization is mathematically sound (Beta(1,1)). The Devil's Advocate calls it "commercially useless" and implies it's a problem requiring a solution. The codebase shows that 0.5 is not a problem — it's an explicit design choice that the `verify()` endpoint returns. Brands can set their own thresholds. If a brand's threshold is 0.7 for high-stakes operations, an unknown agent doesn't qualify. That is the system working correctly, not a product gap. The "problem" is a customer discovery problem: do brands want a "this agent is unknown" signal? That's worth researching, but it doesn't require changing the formula.

---

## 3. Evidence Gaps — What They Missed

### Gap 1: The deregister/hard-delete vulnerability (neither agent found this)

`database.py` line 323: `deregister_agent()` deletes the agent_registry row entirely. `incident_reports` rows survive (FK without CASCADE), but they're orphaned — no future score query can find them. A low-scoring agent deletes and re-registers: score resets to 0.5, all accumulated query history gone, all incidents gone from the score calculation (though the incident_reports rows technically remain, pointing to a now-nonexistent agent_id).

This is the credit bureau model's most fundamental failure mode in the current code, and both agents missed it because they were reasoning from analogy rather than reading the schema.

**Fix required:** `agent_status` column on `agent_registry` (active/suspended/deregistered), soft-delete instead of hard-delete, preserved history linkable to new registrations via `author` field match.

### Gap 2: The trust_metadata free upgrade (neither agent leveraged this)

The External Researcher recommends adding interaction type weighting. The Devil's Advocate says keep it simple. Neither agent knew that `trust_metadata TEXT DEFAULT NULL` already exists on every agent row with a fully implemented write method. This changes the recommendation from "add a new column" (schema migration, blast radius) to "write to an existing column" (no migration, zero blast radius).

### Gap 3: The normalized_incident_type problem (neither agent raised it)

The `incident_type` field in `incident_reports` is free text. "policy_violation" and "PolicyViolation" and "Policy Violation" are three different values in any GROUP BY query. The External Researcher discusses incident taxonomy in the context of severity weighting but misses this underlying data quality problem. A severity system built on top of a free-text incident_type field is not queryable without string normalization.

### Gap 4: The test blast radius is precise (neither agent could have known this)

The Devil's Advocate correctly identifies that formula changes are reversible ("Rollback Difficulty: 6"). The codebase evidence is more specific: the only test that breaks on formula change is `test_compute_trust_formula_correctness` at `test_trust_layer.py` line 98, which asserts `(1+10)/(1+10+3+2) == 11/16` (approximately). One assertion, one file, two-line fix. The Devil's Advocate's "Rollback Difficulty: 6" is probably too cautious given this precision.

---

## 4. Agreements — High-Confidence Convergence

### Agreement 1: Reporter authentication is the highest-priority structural fix

All three agents independently identified this as the most critical vulnerability. The codebase analyst (schema), the External Researcher (credit bureau credentialed furnisher model), and the Devil's Advocate (unauthenticated incident reports = CRITICAL) all arrived here independently. This is not a close call.

### Agreement 2: One score for V1

The External Researcher recommends one score. The Devil's Advocate recommends one score. The codebase analyst notes that the formula is clean and well-tested. Convergence is complete. The Klout/Facebook failure cases cited by the Devil's Advocate are strong evidence.

### Agreement 3: Enforcement boundary is "expose scores, let downstream enforce"

All three agents agree Submantle should not block agents. The disagreement is only about whether a minimal abuse-response floor (MATCH-list equivalent) is compatible with neutrality. On the primary principle — no blocking, no gating in the scoring path — there is full convergence.

### Agreement 4: The dispute mechanism is missing and matters

The External Researcher flags it: credit bureaus require dispute handling (FCRA). The Devil's Advocate implies it in the "quarantine don't delete" recommendation. The codebase analyst's missing-field table includes `status (pending/accepted/disputed/resolved)`. Three independent paths to the same gap.

---

## 5. Surprises — What Changed My Thinking

### Surprise 1: Signet's LLM-swap decay rule is directly relevant to an open design question

I did not expect the External Researcher to surface a competitor implementing a specific rule for the "model change" scenario. Signet decays the score 25% toward operator baseline on model swap. This is a concrete, shipping answer to a question CLAUDE.md lists as unresolved ("Trust survives model changes"). The question for the council is whether Submantle's `author` field plus `version` field gives enough information to detect a meaningful model change — and whether decay (not reset, decay) is the right response. I had no prior position on this; now I lean toward decay-not-reset as architecturally sounder than either "ignore model changes" or "reset to 0.5."

### Surprise 2: The Devil's Advocate's "Businesses will pay for trust scores" as the most important unverified assumption

I had not rated customer discovery validation as a blocking concern for the scoring model work itself. The Devil's Advocate argues that dashboard depth should not outrank customer discovery — and that no architecture decision is well-grounded until at least one business has expressed willingness to pay. This is uncomfortable but I cannot refute it from the codebase. The infrastructure is sound. The question of what signal businesses actually want is genuinely unverified. This does not change what the scoring model should look like technically, but it should change sequencing: customer discovery conversations should run in parallel with scoring model development, not after it.

### Surprise 3: The MATCH list analog I raised in my findings maps exactly to the CA revocation model the External Researcher raised

I raised the Visa MATCH list as an enforcement-compatible neutrality model in my findings independently. The External Researcher arrived at the CA revocation model (withdrawing attestation without blocking existence) from a different angle. These are structurally equivalent: both are "record a negative status, let downstream enforce." This convergence via different analogies increases my confidence that a `revoked_agents` table or an `agent_status` flag is the right design — not hard enforcement, not nothing.

---

## Priority Challenges for the Council to Resolve

In order of structural impact, based on codebase evidence:

1. **Hard-delete vs. soft-delete on deregistration** — This is the single decision with the most irreversible consequences. Once agents accumulate history under hard-delete semantics, migrating to soft-delete preserves nothing. A schema decision made now has no blast radius; the same decision made after a year of production data is a migration problem.

2. **Reporter authentication architecture** — Specifically: does a "registered business" reporter require a separate registry (new table, new registration flow, new auth) or can it reuse the existing agent auth mechanism (a business IS an agent, just a different type)? The answer shapes V2 scope significantly.

3. **trust_metadata write policy** — If the council agrees to use trust_metadata for interaction breakdowns today (zero migration, free upgrade), someone needs to own the write path in `record_query()`. This is the lowest-cost decision on this list and should be resolved first.

4. **Decay vs. reset on identity change** — The Signet precedent suggests decay-not-reset. The CLAUDE.md open question needs a closed answer before building W3C VC attestation issuance (build priority #10), because attestations that travel with the agent need to encode how score changes on version/model upgrade.
