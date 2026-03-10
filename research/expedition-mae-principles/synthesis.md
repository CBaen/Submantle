# Expedition Synthesis: Mae/MIDGE Architectural Principles for Substrate
## Date: 2026-03-10
## Vetted by: Orchestrator
## Alignment: Checked against Research Brief

---

## High Confidence (teams converged, validators confirmed)

### 1. The Enforcement Mode Ladder
**Source:** Teams 1, 3, 4 converged independently. All 3 validators confirmed as highest-confidence finding.

Never gate on trust before you have baseline data. Three phases:
- **Phase 1 (Advisory):** Compute trust scores, return them in API responses, log everything. Don't block anything.
- **Phase 2 (Soft Gate):** Warn when trust score falls below threshold. Still don't block.
- **Phase 3 (Hard Gate):** Reject queries from agents below minimum trust threshold.

Derived from Mae's ConnectionRegistry (PERMISSIVE → ADVISORY → BLOCKING) and validated by Mae's endurance testing: blocking without baseline data causes false rejections.

### 2. Three Independent Trust Signals, Not One
**Source:** Teams 1, 2, 3 converged. Validators confirmed the math.

Trust scoring must use multiple independent signals (Mae's Law 7: Rule of 3/5). The three signals map to Substrate's existing schema:
- **TEMPORAL (Longevity):** registration_time, last_seen
- **BEHAVIORAL (Activity):** total_queries / time elapsed
- **OPERATIONAL (Incidents):** incidents / total_queries (Beta Reputation System)

The Beta Reputation System (Jøsang 2002) is the right algorithm. It maps directly to `total_queries` (alpha) and `incidents` (beta). MIDGE validates this in production via ThompsonSampler. Formula is O(1) arithmetic, pure Python, no dependencies.

### 3. Substrate Must Know Itself
**Source:** Teams 2 and 4 converged. All validators confirmed.

Substrate does not appear in its own awareness report. Add a Substrate identity signature to `signatures.json` (importance: "critical"). This closes the autopoietic loop — the awareness layer knows it exists. ~15 minutes of work.

### 4. Event Payload Contracts Are Fragile
**Source:** Teams 1 and 4 converged. Validators confirmed with Mae evidence.

Mae's endurance run revealed silent failures from key mismatches in event payloads (`node_id` vs `{"nodes": [...]}`). Substrate's events are plain dicts with no schema enforcement. As event types multiply, this will cause the same class of silent bug. Formalizing expected payload shapes per EventType — even just in docstrings — prevents this.

---

## Battle-Tested (proven patterns, filtered for alignment)

### 5. Beta Reputation System for Trust Scoring
**Source:** Team 1, validated by all 3 validators.

The formula uses only existing schema fields. No new infrastructure. Validators caught two critical blockers:
- `record_query()` is never called from `api.py` — `total_queries` stays at 0
- `increment_agent_incidents()` is never called anywhere — `incidents` stays at 0
- **Validator 3 discovered:** No authentication middleware exists on query endpoints — agents aren't required to identify themselves

**Implementation order (from validators, not researchers):**
1. Add auth middleware to `/api/query` and `/api/status`
2. Wire `record_query()` in that middleware
3. Define what constitutes an "incident"
4. Wire `increment_agent_incidents()` into the incident detection code path
5. Add `compute_trust()` as a pure function over existing schema fields
6. Return trust_score in API responses (Phase 1 Advisory)

### 6. Watchdog Heartbeat for Scanner Thread
**Source:** Team 4, confirmed by all validators as zero-risk, high-value.

If the scanner hangs, nothing currently detects it. A simple heartbeat timestamp checked on the next API call catches "alive but stuck" zombie scenarios. The healer-skips-self pattern (from Mae's endurance run) is a concrete safety rule: any health monitor must not attempt to heal itself from within itself.

### 7. Mae's Endurance Failure Checklist
**Source:** Team 4, Validator 1 called this "the most immediately actionable output."

Six categories of failure invisible to unit tests, surfaced only after 25,000 simulation steps:
1. Trust floor decay (providers decayed below rejection threshold)
2. Missing EventBus channel registration (30K+ warning floods)
3. Self-healing loop (healer triggered its own threshold)
4. Key mismatch in message contracts (handler silently failed for weeks)
5. Zero replenishment (all nodes starved after ~350 steps)
6. Cooldown absence (re-healed same system every scan)

**For Substrate:** Run the daemon for 72 hours and watch what drifts. Unit tests won't find these.

---

## Novel (theoretical backing, filtered for feasibility)

### 8. Convergence Principle for "What Would Break?"
**Source:** Team 3, partially confirmed by validators.

The principle: a single data point is an observation; convergence across independent domains is knowledge. Currently `query_what_would_break()` checks identity importance and child processes. Adding runtime behavioral signals (uptime, memory velocity) would strengthen the answer.

**Validators caught:** This is more architecturally disruptive than presented. The function is currently pure (takes inputs, returns output). Adding behavioral signals requires either changing its signature or giving it DB access. Defer until after the background scan loop exists.

### 9. Selective Holon Protocol (4 of 10 Capabilities)
**Source:** Team 2, validators noted it's simpler than the framing suggests.

Four capabilities survive the "always aware, never acting" filter: **sense**, **remember**, **heal**, **know_self/know_down**. Each module should answer: "Can you scan?" / "What's your history?" / "Are you healthy?" / "What are your components?"

Validators correctly noted this is essentially "add a `get_health()` method to each module" — a standard health interface pattern. The Holon Protocol framing adds context but the implementation is a simple ABC.

### 10. Configuration Over Code for Future Collectors
**Source:** Team 2, aligned with existing `signatures.json` pattern.

Substrate's signatures.json already embodies the Stem Cell Principle (Law 5): same scanner, different configuration. When adding hardware sensors, network scanners, etc., use the same pattern — one `AwarenessCollector` base, specialization via configuration profiles, not bespoke classes.

---

## Filtered Out (removed and why)

| Finding | Team | Why Filtered |
|---------|------|-------------|
| Granger causality analysis | Team 3 | Requires months of data, statsmodels dependency, calibration for sub-second intervals. Correct to defer to V2+. |
| Physarum optimizer for process relationships | Team 4 | V2+ concept. Adds state and computation for theoretical benefit. |
| Circadian-aware scan scheduling | Team 4 | Useful feature idea but NOT a Mae principle transfer. Unvalidated Windows API dependency. Feature spec, not architecture. |
| Full mixin decomposition now | Team 2 | Team correctly deferred to "before Go rewrite." Python mixins don't transfer to Go interfaces. |
| LLM-enhanced holonic routing | Team 2 | Violates spirit of "no LLM classification" constraint. Correctly deferred by team. |
| EventBus stream layer as top priority | Team 3 | Validator 3 caught: SQLite with WAL mode and indexes serves the same purpose at prototype scale. Valid at production scale, not justified now. |
| Per-capability Beta distributions (JSON file) | Team 3 | Conflicts with Team 1's schema-based approach. Team 1's is more immediately deployable. Team 3's is a V2 extension. |
| Fractal hierarchy registry | Team 2 | The category structure already exists implicitly in signatures.json. "Formalize what's there" is correct; "create from scratch" overstates the gap. |

---

## Disagreements

### Trust Scoring Architecture: Teams 1 vs 3
- **Team 1:** Pure function over existing schema fields. No new files.
- **Team 3:** Separate `beta_distributions.json` + `TrustScorer` class + feedback loop.
- **Resolution:** Team 1's approach first (uses what exists, zero new infrastructure). Team 3's per-capability tracking is a valid V2 extension when Substrate needs to trust individual agent capabilities differently.

### EventBus Priority: Team 3 vs Validators
- **Team 3:** Stream layer is "Action 1: highest priority."
- **Validators 2 and 3:** SQLite already serves recent event queries at prototype scale. Not justified as top priority.
- **Resolution:** Defer stream layer until MCP server build, when real latency requirements can be measured.

### Background Scan Loop Scope: Team 2 vs Team 4
- **Team 2:** Rich autopoietic loop with `substrate.loop_alive` events and Fibonacci cadences.
- **Team 4:** Simple watchdog heartbeat timestamp.
- **Resolution:** Team 4's simpler framing for prototype. Team 2's event pattern can be the payload format.

---

## Risks

1. **The authentication gap is the real blocker.** No team identified that query endpoints don't require agent tokens. All trust scoring work is hollow until auth middleware exists.
2. **Thread safety for background scan.** Moving to a push-based scan requires making `_cache`, `_cache_ts`, and `_previous_processes` thread-safe. Neither recommending team named this prerequisite.
3. **Compound scope.** 15+ recommendations across 4 teams aggregate to a medium-sized sprint. "Lightweight per-recommendation" compounds. Prioritize ruthlessly.
4. **Python → Go transition.** Several Python-specific patterns (mixins, ABCs) won't survive the Go rewrite. Focus on principles that are language-agnostic.

---

## Synthesized Implementation Order

Based on all research, all validation, and dependency analysis:

**Immediate (before next build round):**
1. Add Substrate identity signature to `signatures.json` (~15 min)
2. Formalize event payload shapes in EventType docstrings (ongoing discipline)

**Next build round (with dashboard depth):**
3. Add auth middleware to query endpoints + wire `record_query()`
4. Define incident types for Substrate agents
5. Wire `increment_agent_incidents()` into incident detection
6. Add `compute_trust()` pure function (Team 1's formula)
7. Return trust_score in `/api/agents` responses (Phase 1 Advisory)
8. Add scanner watchdog heartbeat

**After MCP server:**
9. Evaluate stream layer need based on real MCP latency
10. Convergence scoring for `query_what_would_break` (requires background scan loop first)
11. Per-capability Beta distributions (Team 3's extension)

**V2+ / Go rewrite:**
12. Health interface on all modules (language-agnostic version of Holon Protocol subset)
13. Configuration-based collector pattern
14. Granger causality (when months of event data exist)
15. Circadian-aware scheduling (validated Windows API cost first)
