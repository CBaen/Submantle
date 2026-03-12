# Team 1 Findings: Mathematical Foundations & Trust Architecture
## Date: 2026-03-10
## Researcher: Team Member 1

---

## Preamble: What Was Examined

Internal: Mae's full mathematical identity document, ConnectionRegistry (198+ connections, 0 bare dyads), TriadEnforcer (16 processes, 62 validators, majority voting), Submantle's agent_registry.py (HMAC-SHA256, 5 trust fields), database.py (schema: registration_time, last_seen, total_queries, incidents, trust_metadata), events.py (7 event types, privacy gate). MIDGE's ThompsonSampler (Beta(α,β) per signal, regime-aware decay, persistence, history log).

External: Jøsang Beta Reputation System (2002, production-validated), CS-PBFT dynamic trust scoring (Springer 2025), TC-PBFT availability/authenticity/response metrics (2024), Beta reputation in human-robot collaboration at fine-grained timescales (arxiv 2024), SourcePilot Thompson Sampling in production (2025), Peirce irreducibility theorem, Simmel triadic closure, Lamport Byzantine Generals mathematics.

---

## Part 1: The Six Mathematical Proofs — Which Transfer to an Awareness Layer?

Mae's identity document claims six independent fields prove the triadic minimum. This section evaluates each for genuine transferability to Submantle (an awareness layer, not a multi-agent system).

### 1.1 Laman Rigidity (1970) — Graph Structure
- **What it proves:** A triangle is the minimal rigid 2D graph. For n points you need 2n-3 edges for rigidity; a triangle has exactly 3 edges for 3 points.
- **Domain:** Structural rigidity of mechanical linkages.
- **Transferability to Submantle:** WEAK. Submantle's connections are not mechanical linkages and do not deform. The rigidity metaphor applies only poetically. Mae's own meta-review admits this: "No rigidity analysis in codebase." For Submantle, this proof is background color, not design mandate.

### 1.2 Peirce Irreducibility (proven Burch 1991) — Relational Logic
- **What it proves:** Triadic relations cannot be decomposed into dyads. Any higher-arity relation CAN be built from triads. Three is the logical atom of relational complexity.
- **Domain:** Formal semiotics and relational algebra.
- **Transferability to Submantle:** MODERATE-HIGH. This is genuinely useful for Submantle's trust model design. The claim: you cannot verify A's behavior toward B using only A and B — you need C (a witness, a log entry, a second data point). This is not metaphor; it is a claim about what information structures can represent. Peirce says any verification protocol reducible to A↔B is informationally incomplete. Adding C (even a passive one like an audit log entry) creates a genuinely different, irreducible structure.
- **Honest caveat:** Peirce's theorem is about the formal logic of relations, not about security or trust specifically. The inference "therefore you need a witness node" is an architectural interpretation, not a mathematical proof. It is a strong analogy, not a theorem. It remains a useful design heuristic.
- **Source:** Burch (1991) Peirce's Reduction Thesis; Wikipedia Peirce's Semiotic Framework (accessed 2026-03-10)

### 1.3 Byzantine Consensus (Lamport/Shostak/Pease 1982) — Fault Tolerance
- **What it proves:** For f Byzantine (arbitrarily malicious) nodes, you need 3f+1 total nodes to reach consensus. With 2 honest + 1 liar, truth wins. With 1 honest + 1 liar, truth is indistinguishable from lie.
- **Domain:** Distributed consensus among adversarial nodes.
- **Transferability to Submantle:** HIGH — with an important translation. Submantle is not a distributed consensus system. It is a single-node awareness layer. However, the TRUST SCORING application is directly relevant:
  - When an agent makes a query, Submantle has exactly two inputs: the agent's claim and Submantle's own observation of system state. That is a dyad — one honest, potentially one "lying" (misconfigured agent). Byzantine math says: **two inputs cannot distinguish truth from lie when one may be wrong.**
  - Introducing a third input — e.g., comparing current process data against historical baseline, or cross-referencing agent-declared capabilities against observed query behavior — creates the 3-party structure that makes verification possible.
  - This is genuine transfer: the math motivates why Submantle's trust model should never rely on agent-provided claims alone.
- **Evidence:** Lamport (1982) proven result; Springer 2025 CS-PBFT shows this principle extended to dynamic scoring with behavioral metrics (availability, authenticity, response delay). TC-PBFT (2024) operationalizes this as: trust_score = w1 * availability + w2 * authenticity + w3 * response_delay_penalty.
- **Source:** Lamport/Shostak/Pease (1982) ACM; link.springer.com CS-PBFT (2025)

### 1.4 Simmel Witnessing / Triadic Closure (1908, network science) — Social Trust
- **What it proves:** A triangle is the smallest cycle — minimum structure for mutual witness. "I know that you know that I know." The atom of social consciousness. Triadic closure: if A-B and A-C exist, B-C tends to form, creating reputation cost for bad behavior.
- **Domain:** Social network theory, sociology.
- **Transferability to Submantle:** MODERATE. Simmel's insight maps to Submantle's trust model as follows: an agent with verified identity (HMAC token) and a history of consistent behavior has a "triadic closure" with Submantle's own observation log — meaning Submantle can form a reputation estimate without any third party, using time as the third node. Agent's claim (A), Submantle's observation (B), and historical pattern (C, accumulated over time) form the minimum verification structure.
- **Empirical evidence:** Granovetter (1973) showed triadic closure creates reputation costs — violators lose standing across the network, not just with one party. This maps cleanly to Submantle's incident counter: an agent that triggers incidents loses trust score in ways that affect all future interactions, not just the one that triggered the incident.
- **Source:** Wikipedia Triadic closure (accessed 2026-03-10); Granovetter (1973)

### 1.5 Hegel Synthesis — Dialectical Emergence
- **What it proves:** Thesis + antithesis + synthesis. Two things oppose; only with a third does something new arise.
- **Domain:** Philosophy of history and logic.
- **Transferability to Submantle:** WEAK for trust architecture. This is inspiring but not prescriptive. Mae's own meta-review notes this is "cited as proof, no dialectical process in codebase." For Submantle, this is background philosophy. Skip as design input.

### 1.6 IIT / Tononi Consciousness — Integrated Information
- **What it proves:** Feedforward (dyadic) networks have zero Phi (integrated information). Only recurrent (triadic/looped) networks generate consciousness.
- **Domain:** Neuroscience / consciousness theory.
- **Transferability to Submantle:** WEAK for trust architecture, but INTERESTING for event bus design. Submantle is explicitly not trying to be conscious. However, the IIT observation that recurrent (looped) information structures have qualitatively different properties than feedforward ones is architecturally relevant: an event bus that only flows one direction (A emits, B receives, no feedback) is structurally weaker than one where observations feed back into behavior. Submantle's event bus is currently feedforward — agents receive no signal about their own trust standing. Adding a feedback loop (agents get a trust score signal they can respond to) would create a recurrent structure. This is design inspiration, not mandate.
- **Source:** Tononi et al. IIT 4.0 (2023) PLOS Computational Biology

---

## Part 2: Law 1 (No Bare Dyads) — Application to Submantle

### 2.1 What Mae Does
Mae's ConnectionRegistry assigns at least two witnesses to every system-to-system connection. In ADVISORY mode, bare dyads are logged. In BLOCKING mode, they are rejected. The auto-assignment heuristic uses SomaticMap topology (shared neighbors first, nervous system fallback). 198+ connections, 0 bare dyads.

The three pathways:
- **Primary:** A → B (direct signal)
- **Verification:** A → C → B (witness checks primary)
- **Balance:** B → C → A (feedback loop)

### 2.2 What Submantle Currently Has
Submantle has a **binary trust model**: a token is either valid (HMAC verifies) or it is not. There is no third element. An agent's claim about itself (name, version, capabilities) is accepted at registration. Submantle's only verification is the HMAC math. This is a bare dyad: agent claims ↔ Submantle accepts.

The schema has the RIGHT FIELDS already — `total_queries`, `incidents`, `trust_metadata` — but the algorithm filling those fields has not been written. The comment in agent_registry.py says "Trust scoring schema is captured but algorithm is deferred (future work)."

### 2.3 The Triadic Witnessing Pattern for Submantle

**What a "witness" means for an awareness layer (not a multi-agent system):**

In Mae, witnesses are other systems. In Submantle, the natural third element is **time + observation**. The pattern translates as:

| Mae's Pattern | Submantle Translation |
|--------------|----------------------|
| A → B (agent claims identity) | Agent presents HMAC token |
| A → C → B (witness verifies) | Submantle cross-references token against observed query behavior |
| B → C → A (balance/feedback) | Trust score signals agent standing back into future gating decisions |

The witness C in Submantle is not a separate process — it is the **behavioral history** accumulated in the database. This is faithful to Peirce's insight (you need three terms, but C can be a record, not an agent) and to Simmel's network theory (reputation cost comes from accumulated observations over time).

### 2.4 Concrete Design Principle Derived

**"No bare token verification."** The pattern says: Submantle should never accept or reject a query based solely on HMAC validity. A valid token with zero history should be treated differently from a valid token with 1,000 queries and 0 incidents. The witness (C) is the behavioral record.

This is a lightweight principle: it requires only what the schema already has (total_queries, incidents), plus a scoring formula. It adds zero infrastructure.

**Boundary condition (not over-engineering):** Submantle must NOT implement full ConnectionRegistry-style witnessing for agent-to-agent connections, because Submantle is not a multi-agent organism. The principle applies to: agent identity verification. It does not apply to: Submantle's internal module connections (which are not inter-system in the Mae sense).

---

## Part 3: Law 7 (Rule of 3/5 Validation) — Application to Submantle

### 3.1 What Mae Does
TriadEnforcer registers processes with 3 validators (standard) or 5 (critical). Validators must be odd-count (to prevent deadlock) and must represent at least 2 different ValidatorTypes (complementary, not copies). Majority vote determines approval.

ValidatorTypes in Mae: STRUCTURAL, BEHAVIORAL, OPERATIONAL, PREDICTIVE, CONSENSUS, CAUSAL, TEMPORAL, RESOURCE, FORMAL.

### 3.2 What Submantle Could Use

The Rule of 3/5 principle for Submantle is not about validating Mae-style processes. It is about **trust signal composition**: Submantle's trust score should never be built from a single metric.

The parallel:
- **Mae:** 3 validators (different approaches) before a process is approved
- **Submantle:** 3 trust dimensions (different evidence types) before a trust score is reliable

The three dimensions that map to Submantle's existing schema:

| Dimension | What It Measures | Schema Field | ValidatorType Analog |
|-----------|-----------------|-------------|---------------------|
| Longevity | How established is this agent | registration_time, last_seen | TEMPORAL |
| Activity consistency | Does query rate match declared use | total_queries / time elapsed | BEHAVIORAL |
| Incident rate | How often does this agent trigger problems | incidents / total_queries | OPERATIONAL |

These three are already there. The formula just hasn't been written. A simple weighted combination gives a trust score in [0, 1] that is structurally triadic — three independent signals, not three copies of the same signal.

**Why odd count matters for Submantle:** When two signals agree and one dissents, the score resolves to the majority. This prevents a single anomalous metric from dominating. An agent with high queries but also many incidents is not "trusted" (two of three signals weak). An agent with high queries, zero incidents, and long history is trusted (three signals align). This is Byzantine math applied to scoring, not consensus — but the informational logic is the same.

### 3.3 Critical for Submantle: No TriadEnforcer Needed

Mae's TriadEnforcer is a full system: process registration, validator registration, majority vote machinery, compliance checking, violation events. That complexity is appropriate for a 92-system organism.

For Submantle, the Rule of 3/5 principle is a **scoring formula design constraint**, not an enforcement system. The principle says: compose trust from at least 3 independent signals. It does NOT say: build a voting system. Submantle should implement this as a pure function: `compute_trust(registration_time, last_seen, total_queries, incidents) -> float`.

---

## Part 4: The Beta Reputation System — The Right Trust Algorithm for Submantle

### 4.1 What It Is
The Beta Reputation System (Jøsang & Ismail, 2002) is a published, production-validated framework for computing trust scores using Beta distributions. It is mathematically equivalent to Thompson Sampling (which MIDGE uses) but framed for reputation rather than exploration.

**Core formula:**
- Each agent has Alpha (α) = count of positive interactions, Beta (β) = count of negative interactions
- Trust expectation: `E(trust) = α / (α + β)`
- Initial state: α=1, β=1 (uninformative prior — equal uncertainty)
- Update: success → α += 1; failure → β += 1

**Evidence of production use:**
- MIDGE's ThompsonSampler implements this exact mechanism for signal reliability, with regime-aware decay (0.90-0.99 multipliers by context)
- SourcePilot (2025) implemented Beta Thompson Sampling for AI model selection; acceptance rates went from 65% → 87% across 4 weeks
- Human-robot collaboration research (arxiv 2024) shows Beta reputation at fine-grained timescales: "failures impact trust more than successes" — suggesting asymmetric weights matter
- Multiple PBFT-variant papers (2023-2025) use this exact pattern for blockchain consensus node scoring

**Source:** Jøsang & Ismail (2002) Beta Reputation System; arxiv.org 2411.01866 (2024); sourcepilot.co (2025)

### 4.2 Why This Maps Directly to Submantle's Schema

Submantle's current schema already stores the raw inputs:

| Beta Reputation Field | Submantle Schema Field | Notes |
|----------------------|----------------------|-------|
| Alpha (successes) | total_queries | Proxy: each query that completes without incident |
| Beta (failures) | incidents | Direct: each recorded incident |
| Registration age | registration_time | Used for longevity weighting |
| Recency | last_seen | Used for decay factor |

This is not a coincidence — Submantle's schema was designed with future trust scoring in mind (the comment in the code says "Trust scoring schema is captured but algorithm is deferred"). The Beta Reputation System IS that algorithm.

### 4.3 The MIDGE Improvement: Regime-Aware Forgetting

MIDGE adds one critical enhancement to Thompson/Beta: **forgetting rate varies by context** (volatile=0.90, stable=0.97). The mechanism: periodically decay α and β toward the prior by multiplying both by the decay factor, floored at 2.0 to preserve directional memory.

For Submantle, "regime" maps to **query pattern**:
- An agent that queries rarely (low total_queries) should have faster forgetting — its history is thin, old data is less reliable
- An agent that queries constantly should have slower forgetting — accumulated evidence is strong

This translates to a **query-volume-aware decay rate** rather than MIDGE's market-regime-aware rate. Mechanically identical, contextually appropriate.

The floor of 2.0 (not 1.0) is a key engineering insight from MIDGE: flooring at 1.0 collapses everything to an uninformative Beta(1,1) prior after enough time. Flooring at 2.0 preserves a gentle directional memory — a historically trustworthy agent stays "more trustworthy" even after a period of inactivity.

### 4.4 The Asymmetric Weight Insight

The human-robot collaboration paper (arxiv 2024) found empirically that "failures impact trust more than successes." For a 1:1 symmetric update (each incident hurts as much as each query helps), an agent needs N clean queries to recover from 1 incident. The asymmetry argument says incidents should hurt MORE than successes help.

This maps to the security intuition: one security incident from an agent is more informative than 100 successful queries. The Beta distribution supports this by using weighted updates: incident → β += 2 (or some weight > 1) while clean query → α += 1.

This is an optional calibration to apply after proving the base model works.

---

## Part 5: ConnectionRegistry Pattern — What Transfers

### 5.1 What Mae's ConnectionRegistry Actually Does (vs. What It Claims)

Mae's own meta-review (score 5/10) distinguishes:
- **Declarative (registered):** 198+ connections with named witnesses — real
- **Operational (executes):** Verification pathways (A→C→B) now run via WitnessNotifier — recently added but still "advisory" by default
- **BLOCKING mode:** Unregistered connections are rejected — available but not default

The most valuable implementation insight from ConnectionRegistry is not the witnesses — it is the **enforcement mode ladder**:
1. PERMISSIVE (bootstrap): no checks, everything passes
2. ADVISORY (default): log violations, allow everything
3. BLOCKING: reject violations

This three-stage rollout strategy is how you safely introduce trust enforcement without breaking existing functionality. Start with advisory logging to learn what would have been blocked. Then tighten.

### 5.2 What Submantle Should Borrow

**The enforcement mode ladder.** Submantle's current trust model is effectively PERMISSIVE — a valid HMAC token is accepted unconditionally. The path to a trust-based system:

1. **Advisory phase:** Compute trust scores but log them, don't gate. Build empirical baseline of agent behavior.
2. **Soft gate phase:** Log when trust score falls below threshold, issue warnings in API responses.
3. **Hard gate phase:** Reject queries from agents below minimum trust threshold (or return degraded data).

This is the ConnectionRegistry pattern applied to the agent registry. It costs nothing to add phase 1 now — it is just a computed field in `list_agents()` and `verify()` responses.

### 5.3 The Channel Index Pattern

ConnectionRegistry maintains a `_channel_index: dict[channel -> conn_id]` as a fallback when source/target names don't match publisher names. For Submantle's EventBus, the parallel would be maintaining an index of which agent_ids have subscribed to which event types. Currently the EventBus has no such index — it only tracks callbacks, not the agents associated with those callbacks. This would be relevant only when agents can subscribe via the API (future MCP server work), not now.

---

## Part 6: Trust Architecture Design — The Integrated Recommendation

Combining everything above, here is what Submantle's trust architecture should look like. This is a pure principles synthesis — no new infrastructure required.

### 6.1 The Trust Score Formula

```
# All values from existing schema fields
days_since_registration = (now - registration_time) / 86400
days_since_last_seen = (now - last_seen) / 86400
query_rate = total_queries / max(days_since_registration, 1)

# Longevity signal [0-1]: agents older than 30 days get full score
longevity = min(days_since_registration / 30.0, 1.0)

# Activity signal [0-1]: recency check — not seen in 7 days starts declining
recency = max(0.0, 1.0 - (days_since_last_seen / 7.0))

# Beta reputation [0-1]: positive interactions vs incidents
alpha = total_queries + 1   # +1 = uninformative prior
beta  = incidents + 1       # +1 = uninformative prior
beta_trust = alpha / (alpha + beta)

# Composite: 3 independent signals (Law 7: Rule of 3, odd signals, complementary types)
# Weights can be tuned; default is equal
trust_score = (longevity + recency + beta_trust) / 3.0
```

This formula:
- Uses only schema fields that already exist (no new DB columns needed)
- Is a pure Python function (no dependencies)
- Embodies Law 7 (three independent signals: TEMPORAL, BEHAVIORAL, OPERATIONAL)
- Implements the Beta Reputation System for the operational signal
- Is computable in O(1) per agent

### 6.2 Forgetting / Decay (Optional Enhancement)

Following MIDGE's pattern, add a periodic decay to the incident counter (not a new field — just part of the formula):

```
# Decay incidents toward the prior based on time since last incident
# If no incidents in 90 days, incidents_effective approaches 0
incident_recency_factor = exp(-0.5 * days_since_last_incident / 30.0)
effective_incidents = incidents * incident_recency_factor
```

This requires adding `last_incident_time` to the schema — a single new column. It prevents old incidents from permanently damaging trust for agents that have since behaved well.

### 6.3 Where to Gate

Following ConnectionRegistry's enforcement mode pattern:
- **Phase 1 (now):** Add `trust_score` as a computed field returned by `/agents` endpoint and `list_agents()`. No gating. Build observation baseline.
- **Phase 2 (after MCP server):** When agents query via MCP, include trust score in response metadata. Log low-trust queries.
- **Phase 3 (future):** Gate high-impact queries (process detail, kill signals, etc.) on minimum trust threshold.

---

## Part 7: What Does NOT Transfer — Honest Assessment

The most important finding of this research is what to leave behind.

### 7.1 ConnectionRegistry-Style Witness Assignment: Do Not Port
Mae assigns named system-to-system witnesses across 92 interconnected systems. Submantle has 5 modules with simple sequential dependencies. The overhead of assigning witnesses to Submantle's internal connections would add complexity for zero safety gain. Submantle is not adversarial to itself. The principle transfers (behavioral evidence as witness); the mechanism does not.

### 7.2 TriadEnforcer Voting Machinery: Do Not Port
Mae's TriadEnforcer runs majority votes with 3-5 validators per process. This is appropriate when 16 distinct processes each need independent oversight. Submantle has one trust-sensitive process: agent query authorization. One well-designed scoring function replaces the entire machinery. The principle (complement independent signals) transfers; the mechanism does not.

### 7.3 Fractal Hierarchy at Mae's Scale: Not Applicable
Mae's fractal dimension, organ/module/subsystem nesting, and 4-layer depth make sense for a 92-system organism. Submantle is 5 modules. Fractal self-similarity at Submantle's current scale is a solved problem: there is no scale to fractal across. This is a principle for when Submantle has 50+ systems, not now.

### 7.4 BLOCKING Mode by Default: Not Safe Without Baseline
Mae's ConnectionRegistry uses ADVISORY as default, not BLOCKING. Submantle should follow this — do not gate on trust score before you have baseline data. The enforcement mode ladder exists precisely to avoid blocking legitimate agents during calibration.

### 7.5 IIT Consciousness Properties: Domain-Specific
Mae tracks Phi (integrated information), Markov blankets, and 8 consciousness properties. Submantle is not attempting to model consciousness and is not an agent. These properties do not transfer to an awareness layer. They are fascinating and clearly correct for Mae's design goals, but they add no value to Submantle's trust model.

---

## Part 8: Gaps and Unknowns

1. **Incident definition:** The `incidents` field exists in Submantle's schema, but there is no code that calls `increment_agent_incidents()`. The trust scoring formula is only as good as the incident detection it builds on. What counts as an incident? Rate limit violations? Invalid query parameters? Privacy mode bypass attempts? This needs to be defined before trust scoring can be meaningful.

2. **Cold start problem:** A new agent has zero queries and zero incidents — trust score of ~0.5 (Beta prior). Is that too low? Too high? MIDGE's ThompsonSampler solves cold start by seeding from known reliability scores. Submantle has no analogous seed data. The uninformative prior is safe but conservative.

3. **Multi-device trust:** Submantle's vision is hundreds of millions of devices. If an agent is registered on device A with a strong trust score, how does that transfer to device B? The current architecture is per-device. The trust_metadata JSON column is available for storing cross-device trust signals if sync is added. This is flagged as future architecture.

4. **Asymmetric weighting validation:** The finding that "failures impact trust more than successes" is from human-robot collaboration (continuous physical tasks). Whether this asymmetry holds for software query agents is unknown. Suggested approach: implement 1:1 symmetric Beta first, measure, then adjust weights based on observed incident distributions.

5. **Byzantine threat model:** The Byzantine math (3f+1) formally applies when f nodes can be arbitrarily malicious. Submantle's threat model is probably softer: misconfigured agents, not adversarial ones. This means the 3-validator minimum is a useful heuristic, not a formal requirement. Submantle does not need 3f+1 anything — it needs trust scoring that detects misconfiguration, not active attacks.

---

## Synthesis

### Which Laws Genuinely Apply to Submantle

| Mae's Law | Transferability | How It Applies | Mechanism |
|-----------|---------------|----------------|-----------|
| Law 1: No Bare Dyads | HIGH | Don't authorize on token alone; witness with behavioral history | Beta trust score as C in the triad |
| Law 2: K3 Triadic Generator | LOW | Background inspiration only | N/A for Submantle's current scale |
| Law 3: Holon Protocol | COVERED BY TEAM 2 | Not in scope here | - |
| Law 4: Fractal Self-Similarity | LOW | Applicable only when Submantle reaches 50+ systems | N/A now |
| Law 5: Stem Cell | COVERED BY TEAM 2 | Not in scope here | - |
| Law 6: Autopoietic Closure | MEDIUM | Trust score feeds back into agent behavior (recurrent loop) | Phase 3 gating |
| Law 7: Rule of 3/5 | HIGH | Three independent trust signals, complementary types | Longevity + Recency + Beta |
| Law 8: Eight Consciousness Props | VERY LOW | Submantle is not attempting consciousness | N/A |

### What Mae Learned That Submantle Should Carry Into Its DNA

1. **The enforcement mode ladder.** Start ADVISORY, go BLOCKING later. Never skip phases. This is the most operationally important lesson from ConnectionRegistry.

2. **The Beta Reputation System is the right trust algorithm.** It is mathematically sound (Jøsang 2002, production-validated for 20+ years), computationally trivial (pure arithmetic), and directly maps to Submantle's existing schema. MIDGE validates this — it is the same mechanism in production.

3. **Three independent signals, not one.** Law 7 says: a trust score built on a single metric is fragile. Use TEMPORAL (longevity), BEHAVIORAL (recency), and OPERATIONAL (incident rate) as three orthogonal trust dimensions. This is cheap to implement and architecturally sound.

4. **Agents need a feedback signal to be fair.** An agent whose trust is declining should know about it — at least at query time (trust score in API response metadata). This is the balance pathway (B→C→A) from Law 1. It requires no new infrastructure, just including trust_score in API responses.

5. **Incidents are the most information-dense signal.** Byzantine math, Beta distribution theory, and the HRC empirical research all agree: failures are more informative than successes. Define incidents carefully and weight them accordingly.

6. **Define before you build.** Mae's meta-review found the gap between declarative (registered) and operational (executes). Submantle should define what counts as an incident BEFORE building the trust scoring system, or it will build a formula that inputs zero into the most important variable.

---

## Sources Referenced

- Jøsang & Ismail (2002) "The Beta Reputation System" — people.cs.vt.edu
- Lamport, Shostak, Pease (1982) "The Byzantine Generals Problem" — ACM / lamport.azurewebsites.net
- Tononi et al. (2023) "IIT 4.0" — PLOS Computational Biology
- Burch (1991) "Peirce's Reduction Thesis" — cited in Mae's mathematical identity document
- Simmel (1908) "Soziologie" — via Wikipedia Triadic Closure (accessed 2026-03-10)
- Granovetter (1973) "The Strength of Weak Ties" — via Triadic Closure overview
- CS-PBFT (2025) "Comprehensive Scoring-Based PBFT" — link.springer.com/article/10.1007/s11227-025-07342-3
- TC-PBFT dynamic trust metrics — MDPI and Springer Nature (2024)
- SourcePilot Thompson Sampling production results (2025) — sourcepilot.co/blog/2025/11/22
- Beta Reputation in Human-Robot Collaboration (2024) — arxiv.org/html/2411.01866
- Mae mathematical identity (MAES-MATHEMATICAL-IDENTITY.md) — internal, C:\Users\baenb\projects\mae-core\data
- ConnectionRegistry implementation — internal, C:\Users\baenb\projects\mae-core\mae_core\backbone\connection_registry.py
- TriadEnforcer implementation — internal, C:\Users\baenb\projects\mae-core\mae_core\backbone\triad_enforcer.py
- ThompsonSampler implementation — internal, C:\Users\baenb\projects\MIDGE\mae_core\market\intelligence\thompson_sampler.py
- Submantle agent_registry, database, events — internal, C:\Users\baenb\projects\Submantle\prototype\
