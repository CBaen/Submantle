# Council Synthesis: What Changes an Agent's Trust Score?
## Date: 2026-03-12
## Vetted by: Orchestrator
## Alignment: Checked against Research Brief
## Challenge round: Did NOT introduce new evidence. Phase 3 (Revision) skipped.

---

## Master Score Table

### Codebase Analyst Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Feasibility (of enriching scoring) | 8/10 | Formula, DB, and registry cleanly separated |
| Blast Radius (10=minimal) | 7/10 | One test breaks on formula change. Schema migration needed for new columns. |
| Pattern Consistency | 8/10 | Additive changes fit existing pattern |
| Reversibility | 6/10 | Formula changes affect all historical scores |
| Dependency Risk (10=none) | 9/10 | Pure stdlib Python + sqlite3 |

### External Researcher Scores — Reputation System Precedents

| System | Relevance | Maturity | Community Health | Integration Effort | Evidence Quality |
|--------|-----------|----------|------------------|--------------------|------------------|
| Credit Bureaus (FICO) | 9/10 | 10/10 | 9/10 | 8/10 | 9/10 |
| eBay / Amazon | 7/10 | 9/10 | 8/10 | 7/10 | 8/10 |
| Uber / Lyft / Airbnb | 6/10 | 8/10 | 7/10 | 6/10 | 7/10 |
| App Stores | 5/10 | 9/10 | 7/10 | 4/10 | 6/10 |

### External Researcher Scores — Frameworks & Competitors

| System | Relevance | Maturity | Community Health | Integration Effort | Evidence Quality |
|--------|-----------|----------|------------------|--------------------|------------------|
| IETF RATS RFC 9334 | 9/10 | 9/10 | 8/10 | 7/10 | 10/10 |
| NIST AI RMF | 6/10 | 9/10 | 8/10 | 3/10 | 8/10 |
| Mastercard Verifiable Intent | 8/10 | 6/10 | 8/10 | 6/10 | 8/10 |
| Signet | 10/10 | 6/10 | 6/10 | N/A | 7/10 |
| ZKP Reputation | 7/10 | 6/10 | 7/10 | 3/10 | 7/10 |

### Devil's Advocate Risk Scores

| Dimension | Score (10=safe) | Notes |
|-----------|-----------------|-------|
| Failure Probability | 3 | Unauthenticated reporting = certainty of abuse |
| Failure Severity | 4 | Core signal can be zeroed by anonymous spam |
| Assumption Fragility | 3 | Two load-bearing assumptions unverified |
| Rollback Difficulty | 6 | Formula easy; structural changes bounded but not trivial |
| Hidden Complexity | 5 | Sociotechnical machinery not simple |

### Challenge Round Score Adjustments

| Original Score | Challenger | Proposed Adjustment | Orchestrator Ruling |
|----------------|------------|---------------------|---------------------|
| eBay Relevance 7/10 (ER) | Codebase Analyst → 5/10 | **Adjust to 6/10.** Two-sided problem doesn't exist in Submantle, but behavioral-outcomes-over-explicit-ratings lesson is transferable. |
| Signet Relevance 10/10 (ER) | Devil's Advocate → 7/10 | **Adjust to 8/10.** Closest direct competitor, but two key lessons (SDK self-reporting, LLM-decay) are lessons in what NOT to copy. |
| NIST Relevance 6/10 (ER) | Devil's Advocate → 8/10 | **Adjust to 7/10.** Enterprise procurement gatekeeping is real but NIST doesn't inform the scoring model directly. |
| Feasibility 8/10 (CA) | Devil's Advocate: overstates semantic feasibility | **Keep 8/10 for code feasibility; note semantic feasibility is lower (~5/10).** Two distinct dimensions. |
| Reversibility 6/10 (CA) | External Researcher: different changes have different profiles | **Keep 6/10 as blended average; note range is 0/10 to 9/10 depending on specific change.** |
| Cold start "commercially useless" (DA) | Codebase Analyst: system working correctly | **Split the finding.** Mathematically correct (0.5 is sound). Commercially, the API should distinguish "no history" from "scored at 0.5." |

---

## High Confidence (agents converged with independent evidence)

These findings survived all three independent analyses AND the challenge round without being overturned. Treat as resolved.

### 1. Unauthenticated incident reporting is the most critical vulnerability

**Triple convergence.** Codebase Analyst found it in the schema. External Researcher found it via credit bureau credentialed-furnisher model. Devil's Advocate stress-tested it as CRITICAL severity. Challenge round escalated it further: Devil's Advocate argues it's a ship-blocker, not merely a gap. External Researcher adds that authentication alone is insufficient — reporter accuracy scoring is also needed.

**Orchestrator assessment:** This is the single highest-priority finding. The entire credit bureau model requires credentialed reporters. Without them, Submantle is a public defamation endpoint.

### 2. Single universal score is correct for V1

**Triple convergence.** Devil's Advocate verified via Klout failure case ($40M raised, shut down due to score complexity). External Researcher verified via eBay/FICO/Airbnb precedent (all started with one number). Codebase Analyst confirmed enrichment data goes to trust_metadata (display) not formula (authoritative). No challenge disputed this.

### 3. The Beta formula math is sound; the inputs are the problem

**Triple convergence.** Devil's Advocate: "sound instrument pointed at imprecise target." External Researcher: sufficient metadata identified. Codebase Analyst: formula is clean, one-function implementation. The formula is not the bottleneck. Input quality (specifically incident report credibility and interaction type differentiation) is.

### 4. A dispute mechanism is required

**Triple convergence.** Devil's Advocate: agents must be able to contest reports. External Researcher: FCRA and GDPR require dispute handling. Codebase Analyst: no dispute mechanism exists; `status` field missing from incident_reports. External Researcher's challenge adds legal urgency: build before first enterprise customer.

### 5. Deregister must become soft-delete

**Triple convergence.** Codebase Analyst found the hard DELETE at database.py line 323. External Researcher framed it as a design principle violation (bureau that allows history wipes is a "reputation laundry service"). Devil's Advocate framed it as the primary sophisticated attack vector (synthetic identity fraud pattern). No challenge disputed the fix: `agent_status` column (active/suspended/deregistered).

### 6. trust_metadata is the right home for enrichment data

**Double convergence + challenge refinement.** Codebase Analyst identified the unused column and write method. External Researcher changed their recommendation after reading this (from "new table" to "use existing column"). Devil's Advocate correctly noted: the column is free, the detection logic to populate it is not. Orchestrator concurs with distinction.

---

## Recommended Approach

Based on the full council deliberation, the recommended scoring model changes fall into three tiers:

### Tier 1: Ship-Blockers (before any public demo or customer)

**1a. Authenticate incident reporters.**
- Create a `reporter_registry` table (or reuse agent_registry with a `role` field)
- Require reporter registration with verified identity before accepting incident reports
- POST /api/incidents/report requires a valid reporter token
- Track reporter accuracy over time (false report rate) — per External Researcher's challenge
- *Source: All three agents converged. Devil's Advocate escalated to ship-blocker status.*

**1b. Add velocity caps on query counting.**
- Maximum N queries per hour counting toward trust score per agent
- Repeated identical queries within a window count once
- Store velocity data in trust_metadata
- *Source: Devil's Advocate (CRITICAL), Codebase Analyst (no current defense), External Researcher (credit bureau parallel).*

**1c. Convert deregister to soft-delete.**
- Add `agent_status` column: active / deregistered / suspended
- Deregister sets status rather than deleting the row
- All history preserved; score computation skips deregistered agents
- Re-registration with same name by same author inherits history
- *Source: Triple convergence. Codebase Analyst proposed the fix; External Researcher provided the rationale; Devil's Advocate identified the attack pattern.*

### Tier 2: Before First Enterprise Customer

**2a. Normalize incident taxonomy.**
- Replace free-text `incident_type` with an enum of recognized types
- Add `severity` weight per type (e.g., data_exfiltration > rate_limit_violation > api_misuse)
- Severity weights DO NOT change the Beta formula yet — stored in trust_metadata for V1
- *Source: Codebase Analyst (normalized_incident_type missing), External Researcher (FICO weighted categories).*

**2b. Build dispute mechanism.**
- Add `status` column to incident_reports: pending / accepted / disputed / resolved
- Dispute endpoint: agent contests a report; reporter must verify within 30 days or incident is removed from score calculation
- FCRA-modeled: burden of proof on the reporter, not the agent
- *Source: Triple convergence. External Researcher provided legal framework; Devil's Advocate provided dispute-as-enforcement rationale.*

**2c. Distinguish "no history" from "scored at 0.5" in API response.**
- API response includes `has_history: false` for agents with zero interactions
- Brands can differentiate "genuinely unknown" from "average score"
- Does NOT change the formula — display-layer change only
- *Source: Devil's Advocate identified the cold start problem. External Researcher proposed the specific fix (credit bureau "thin file" handling). Codebase Analyst argued 0.5 is the system working correctly — orchestrator agrees mathematically but sides with the API distinction commercially.*

### Tier 3: Design Decisions for Go Production Rewrite

**3a. Record interaction types now; weight them later.**
- Add `interaction_type` parameter to record_query()
- Store breakdown in trust_metadata
- Do NOT change the Beta formula to weight by type yet
- Calibrate weights only when real data exists to inform them
- *Source: External Researcher proposed weighted queries. Codebase Analyst's blast radius analysis showed no migration path for old data. External Researcher changed their recommendation in the challenge round: "collect data now, weight in Go rewrite." Devil's Advocate validated: complexity kills early reputation systems.*

**3b. Author-based cross-agent visibility.**
- When an agent registers, check if the author has other registered agents
- Surface the relationship in the API response (not the formula)
- Brands can discount a new agent from an author with low-scoring agents
- Does NOT apply Signet's decay rule (which punishes legitimate upgrades)
- *Source: External Researcher identified the version/model-swap gap via Signet. Devil's Advocate correctly challenged Signet's decay rule as incompatible with Submantle's identity model. External Researcher proposed the author-field fix.*

**3c. Score decay / temporal trust (design decision, not V1 build).**
- Open question: should high trust scores decay if an agent stops interacting?
- Credit bureaus retain data for 7 years. But stale scores on compromised agents are dangerous.
- Council does NOT have consensus on this — Devil's Advocate argues decay is needed; neither other agent addressed it. Flag for future research.
- *Source: Devil's Advocate Phase 1 findings. Not disputed but not resolved.*

---

## Alternatives

### Alternative A: Weighted formula now (instead of collecting types and weighting later)

**For:** External Researcher's Phase 1 recommendation. FICO uses five weighted categories. Richer signal.
**Against:** Codebase Analyst's blast radius analysis (no migration path for old data). Devil's Advocate's Klout precedent (complexity kills early systems). External Researcher reversed this recommendation in the challenge round.
**Verdict:** Rejected for V1. Record types, weight later.

### Alternative B: Signet-style LLM-swap decay rule

**For:** Addresses the version/model-swap gap. Signet is shipping it.
**Against:** Devil's Advocate challenge: contradicts Submantle's identity model ("trust belongs to the entity, not the model"). Punishes legitimate upgrades. External Researcher's alternative (author-based visibility) preserves neutrality.
**Verdict:** Rejected. Use author-based cross-agent visibility instead.

### Alternative C: "Quarantine" enforcement mechanism (Devil's Advocate Phase 1)

**For:** Every durable neutral infrastructure has an abuse-response floor.
**Against:** External Researcher's challenge: "quarantine" is enforcement, not attestation management. CAs revoke certificates; they don't quarantine websites. The correct model is withdrawing Submantle's own attestation/badge, not suspending the agent.
**Verdict:** Modified. Submantle can withdraw its "Verified" attestation. It should not quarantine/suspend agents. Score speaks for itself. Brands enforce.

---

## Disagreements

### The enforcement boundary — "never" vs. "rarely with procedure"

**External Researcher position:** "Submantle should never unregister for bad behavior."
**Devil's Advocate position:** "Never is the wrong word. Rarely, with procedure, for identity fraud only."
**Codebase Analyst position:** "Building a MATCH-list analog is architecturally trivial. Building actual enforcement violates Design Principle 4."

**Orchestrator assessment:** The council converges on "Submantle does not block, gate, or throttle." The disagreement is specifically about identity fraud (someone registers "anthropic-claude-official" impersonating Anthropic). The External Researcher's "withdraw attestation" model handles this: Submantle can decline to issue a "Verified" badge, or withdraw one already issued, without deregistering the agent. The agent continues to exist with its (low) score. This is the CA revocation model applied correctly.

**Resolution:** The "never enforce" principle holds for behavioral scoring. For identity fraud, Submantle may withdraw its own attestations. It does not deregister, suspend, or quarantine.

### Customer discovery timing

**Devil's Advocate position:** Customer discovery should outrank dashboard work and scoring model features.
**External Researcher position (challenge):** Customer discovery is "the highest-priority finding no one wants to rank first."

**Orchestrator assessment:** This is outside the scoring model scope but is the most strategically important finding in the entire council. Surfacing to Guiding Light as a meta-finding. The scoring model work should continue, but customer conversations should run in parallel — not after.

---

## Filtered Out

### Zero-knowledge proofs for threshold proving
External Researcher documented ZKP for reputation. Filtered: future-state (Go rewrite + W3C VC layer), high implementation complexity, current architecture already privacy-preserving. Not needed for V1.

### Relative peer comparison (Uber model)
External Researcher noted Uber/Airbnb moved toward relative comparison. Filtered: contradicts Submantle's deterministic constraint. Skip.

### ML-based anomaly detection for anti-gaming
Not proposed by any agent (correctly). Filtered: violates EU AI Act constraint.

### Category-specific scores for V1
Filtered by triple convergence: single score is correct. Complexity kills early reputation systems.

---

## Risks

### From Devil's Advocate, validated against other agents

| Risk | Severity | Validation |
|------|----------|------------|
| Unauthenticated reporting enables competitive sabotage | CRITICAL | Triple convergence. Live attack vector. |
| Self-query inflation produces meaningless scores | CRITICAL | Triple convergence. No defense exists. |
| Hard-delete enables reputation laundering | HIGH | Triple convergence. Breaks bureau model. |
| Cold start favors pre-staging bad actors over legitimate agents | MEDIUM | Devil's Advocate only. Valid but solvable with "no_history" flag. |
| Stale scores on compromised high-reputation agents | MEDIUM | Devil's Advocate only. Not resolved. Design decision for future. |
| "Businesses will pay" is unverified | HIGH | Devil's Advocate + External Researcher. Outside scoring scope but strategically critical. |
| Deterministic formulas are easier to reverse-engineer and game | MEDIUM | Devil's Advocate. Acknowledged tradeoff. EU AI Act compliance justifies the choice. |
| Normalized incident types are missing (free-text field) | MEDIUM | Codebase Analyst. Data quality issue. |

---

## Council Process Notes

- **Phase 1:** 3 agents dispatched in parallel (Codebase Analyst, External Researcher, Devil's Advocate). All completed independently.
- **Phase 2:** Challenge round completed. All 3 agents read each other's findings and wrote structured challenges.
- **Phase 3:** Skipped. Challenges refined positions and identified analytical divergences but did not introduce fundamentally new evidence requiring additional research.
- **Phase 4:** This synthesis.
- **Phase 5:** Tension Analysis (next).
