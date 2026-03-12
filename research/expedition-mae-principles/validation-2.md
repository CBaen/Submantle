# Expedition Validation Report: Mae/MIDGE Architectural Principles for Submantle
## Date: 2026-03-10
## Validator: Independent Review

---

## Protocol Note

This report follows divergence-first protocol. Evidence challenges, contradictions, and alignment drift come before agreements. Findings that withstand scrutiny are noted at the end, not used to cushion the weak ones.

---

## 1. Evidence Challenges — What Claims Lack Sufficient Evidence

### 1.1 Team 3's IBM Research Citation Is Unverified and Misapplied

Team 3 cites "IBM Research 2021 demonstrated Granger causality on microservice log data" twice — once under the Convergence Quorum section and again under Granger Causality. The source listed is "IBM Research paper on cloud microservices" with no author, title, DOI, or arXiv ID. This is not a verifiable citation. A vague institutional name does not constitute a source. The claim may be true, but the evidence is not there to confirm it.

More critically, the application is potentially misaligned: Granger causality for cloud microservices operates on log streams from services that are already architecturally defined and monitored with structured telemetry. Submantle's SQLite event table stores PROCESS_STARTED, PROCESS_DIED, and SCAN_COMPLETE events — a far sparser, less structured signal. The Granger transfer assumes the process event data has the statistical properties needed for the F-test, which Team 3 partially acknowledges in Gap 3 but does not fully resolve. The citation is used to support a novel claim without adequate grounding.

### 1.2 Team 3's Pearson Correlation Claim Has No Production Validation

The Pearson correlation tracking claim is presented as "battle-tested" because MIDGE uses it. But the evidence given for Submantle's application — "after N process scan cycles, compute cross-domain correlations between process identity events and resource events" — has no prior art at the process-monitoring layer. MIDGE's CorrelationTracker is validated for financial signals that have daily observations and years of history. Process events on a desktop PC are ephemeral and non-stationary. The paper cited for "detect cross-domain anomalies" is MIDGE's own implementation documentation, not external production validation of this approach applied to OS-level process data.

The finding should not be classified as battle-tested for Submantle's context. It is a novel idea with MIDGE inspiration and no independent validation at the process monitoring layer.

### 1.3 Team 2's "Self-sustaining Software Systems (S4)" Citation Is Thin

Team 2 cites arXiv 2401.11370 as validating the autopoietic scan loop concept. The citation is: "The operational closure pattern (a component that verifiably continues producing its own operational state) is cited as a core property of resilient infrastructure." This is paraphrased and unchecked. The conclusion — "a self-sustaining scan loop is the correct architecture" — is reasonable on its face, but if the paper is primarily about microservices or containerized systems, the transfer to a Python daemon may not hold as described.

### 1.4 Team 1's SourcePilot Production Claim Cannot Be Independently Verified

Team 1 cites "SourcePilot Thompson Sampling in production (2025) — acceptance rates went from 65% → 87% across 4 weeks." The source is a blog post at sourcepilot.co. Blog posts are marketing material, not peer-reviewed production evidence. The claim may be accurate, but it is positioned as production validation for Beta trust scoring when it is vendor self-reporting. Team 1 is otherwise rigorous; this particular citation deserves the lower-weight label "claimed production use" rather than "production-validated."

### 1.5 Team 4's Windows Idle Detection Cost Is Flagged But Not Tested

Team 4 identifies Gap 5: "The cost of calling `GetLastInputInfo()` is unknown from research — it may be negligible, or it may require elevated permissions." This gap is correctly acknowledged, but the circadian-aware scheduling proposal is still given a high priority rank (item 2 in the priority stack: "1–2 days"). Proposing a 1–2 day implementation effort for a feature whose key dependency has an unknown cost/permission requirement is premature. The gap acknowledgment should demote this from the priority stack, not just appear as a footnote.

---

## 2. Contradictions — Where Findings Contradict Each Other

### 2.1 Trust Scoring Architecture: Teams 1 and 3 Give Different Implementation Paths

Team 1 recommends a composite trust score built from three signals computed in a single `compute_trust()` pure function: longevity (TEMPORAL), recency (BEHAVIORAL), and Beta reputation (OPERATIONAL). They provide explicit pseudocode.

Team 3 recommends implementing Thompson trust scoring by adding a `beta_distributions.json` file modeled on MIDGE's `thompson_distributions.json`, and a `TrustScorer` class. Team 3 also recommends updating trust based on agent capability claims being validated or invalidated — a feedback-dependent model.

These are not compatible designs. Team 1's model works with existing schema fields and needs no new files. Team 3's model needs a new persistence artifact (`beta_distributions.json`), a `TrustScorer` class, and a feedback mechanism that Team 3 itself admits does not exist yet (Gap 1: no outcome feedback loop). Building Team 3's version without the feedback loop yields a one-directional punishment model, which Team 3 calls out as a gap.

Team 1's design is more immediately deployable. Team 3's design is more architecturally complete but builds on infrastructure that does not yet exist. Neither team acknowledges the other's approach. A builder following both documents without synthesis would have to choose, and the contradiction is not surfaced anywhere.

### 2.2 EventBus Stream Layer: Teams 3 and 4 Prioritize Differently

Team 3 calls the EventBus stream layer "Action 1: High impact, low friction" and describes it as "~50 lines of code." Team 4 does not mention the stream layer at all in its priority stack. Team 4's priority stack is focused on self-health and repair patterns. If these are to be reconciled into a single implementation order, the stream layer and the watchdog heartbeat are competing for the same "do next" slot, but they solve different problems and neither team has visibility into the other's priority stack.

### 2.3 Autopoietic Scan Loop: Teams 2 and 4 Define It Differently

Team 2 describes the autopoietic scan loop as: "a background thread running the scan cycle independently of API calls, monitoring its own health, emitting `substrate.loop_alive` events."

Team 4 describes a similar concept under the heading "Three-phase healing for component failures" (item 4 in its priority stack), framed as: "detect (no heartbeat), assess (is the DB locked? is the thread alive?), restore (restart the thread, flush and reconnect DB)."

Both are describing a push-based background scan loop with a watchdog, but they frame it differently, give it different names, and neither cross-references the other. Team 2 treats it as structural architecture (autopoietic closure). Team 4 treats it as a resilience pattern (three-phase healing). These are complementary, not contradictory — but the lack of coordination means a builder could implement them as two separate systems when they should be one.

### 2.4 Priority Sequencing Is Irreconcilable Without a Synthesis Step

Each team provides its own priority stack:

- Team 1: Enforcement mode ladder (advisory → soft gate → hard gate), with no explicit timeline framing
- Team 2: Mixin decomposition, fractal hierarchy naming, configuration over code, selective holon, autopoietic loop
- Team 3: EventBus stream layer, convergence scoring for `query_what_would_break`, Thompson trust scoring
- Team 4: Add Submantle signature (1 hour), idle-adaptive scan rate (1–2 days), watchdog heartbeat (half day), three-phase healing (2–3 days), formalize event payload contracts (ongoing)

There are 15+ distinct action items across four teams with no cross-team ranking. A builder attempting to execute these in parallel would face real architectural dependencies: Team 1's trust score formula requires the database schema to be unchanged; Team 3's stream layer touches the same `events.py` file that Team 4's event payload contracts discussion targets; Team 2's autopoietic loop and Team 4's watchdog heartbeat overlap significantly. This is a structural coordination gap the expedition as a whole has left unresolved.

---

## 3. Alignment Drift — Where Findings Drift From the Research Brief

### 3.1 Team 3's Granger Causality Recommendation Violates the Prototype Constraint

The research brief is explicit: "Don't over-engineer the prototype — it's for proving concepts."

Team 3 dedicates a substantial section to Granger causality analysis, including bidirectional Granger pair detection and weekly offline analysis against the SQLite events table. Team 3 does file this under "Emerging" and notes it requires weeks of data accumulation. But the framing still presents it as a design goal for Submantle — and the Granger section receives as much detail as the simpler, immediately applicable recommendations. The asymmetry in documentation depth implicitly elevates a "later, maybe" idea into the same tier as "do now."

The brief says: "pure inspiration, not integration planning." Granger causality crosses into integration planning territory given the depth it is discussed at.

### 3.2 Team 2's LLM-Enhanced Holonic Architecture Section Contradicts a Destructive Boundary

The research brief's destructive boundaries state: "Do NOT recommend adding LLM-based classification."

Team 2 includes a section titled "LLM-Enhanced Holonic Architecture (Relevant to Future Only)" with this note: "The prohibition is specifically about process identity (signatures handle this). It does not prohibit an LLM-enhanced query interface at the MCP layer."

This is a creative reinterpretation, not a clear constraint violation. But it is worth flagging: the team is carving out an exception for LLM use at the MCP layer while simultaneously deferring it to "not applicable to V1." The brief says no integration planning — yet this section is explicitly planning future LLM integration. The brief's spirit, not just the letter, is bent here.

### 3.3 Team 4's Circadian Scheduling Is a Feature Proposal, Not a Principle Transfer

The research brief asks for principles from Mae/MIDGE that could inform Submantle's DNA — "pure inspiration." Circadian-aware resource scheduling is not a principle from Mae that transfers. Mae's CircadianRhythm module runs on simulation step counts; the team correctly notes it is "not tied to wall-clock time." The actual wall-clock circadian scheduling proposal in Team 4 is an independent product feature idea, not a transfer from Mae.

The finding is useful and well-reasoned on its own terms. But its presence in this expedition is technically off-angle. It answers "here is a feature Submantle should have" rather than "here is a principle Mae taught us that should be in Submantle's DNA."

### 3.4 Team 1's Trust Formula Adds a New Schema Column

Team 1 recommends adding a `last_incident_time` column for the forgetting/decay enhancement (Section 6.2). The research brief's constraint says: "Don't suggest restructuring what's already built — find principles that enhance, not replace."

Adding a new column is not restructuring, but it does require a schema migration on any device that already has the database initialized. The brief cautions against changes that require external infrastructure — schema migrations don't violate this, but the implication that this is "just one new column" understates the operational cost in a production scenario. For a prototype, this is minor. The team correctly labels this as "optional enhancement" rather than required, so this is a marginal issue rather than a clear drift.

---

## 4. Missing Angles — What Research Was Not Done

### 4.1 No Team Examined Submantle's `api.py` Load Patterns

All four teams examined the prototype source code but none analyzed `api.py`'s `_get_state()` function in depth. This function is the critical path for every recommendation: it triggers scanning, manages the 5-second cache, writes to SQLite, and builds the tree. Every team's recommendation about scan loops, caching, and autopoiesis needs to engage with this function as the current implementation. Teams 2 and 4 reference the "pull-based scan triggered by API calls" as a gap, but neither examines what would need to change in `_get_state()` to make it push-based, or what cache invalidation behavior changes when a background thread is running.

### 4.2 No Team Examined the `signatures.json` File as a Constraint

All teams mention the 15 identity signatures as a starting point, but no team examined what those 15 signatures actually cover and whether the signature-matching algorithm in `substrate.py` (scoring: exe_contains=1, cmdline_contains=2, cwd_contains=2) has weaknesses that would affect the convergence scoring and `query_what_would_break` recommendations. Team 3's convergence scoring upgrade would make previously unidentified processes more actionable — but if the signature coverage is thin, "unidentified" is a very large category and the convergence logic would fire more often on weak evidence.

### 4.3 No Team Examined Test Coverage as a Constraint on Changes

All four teams recommend changes to `agent_registry.py`, `events.py`, and `substrate.py`. None examined the 160 tests covering these files to understand which changes would require test updates and which could be added without touching existing tests. The research brief notes "160 tests across 4 test files" — this is a non-trivial test surface that would gate any implementation. The risk that a Trust Score formula or stream layer change breaks existing tests was not evaluated.

### 4.4 No Team Addressed the "record_query Is Called On Every Verify" Pattern

In `agent_registry.py`, `record_query()` calls `verify()` internally, which re-derives the HMAC token on every query. Team 1's trust score formula reads `total_queries`, `incidents`, `registration_time`, and `last_seen` — all in the existing schema. But `record_query()` currently calls `update_agent_last_seen()` AND `increment_agent_queries()` as two separate DB writes per query. As query volume grows, this becomes two writes per authenticated request. No team noted this double-write pattern or evaluated whether the trust scoring additions would add a third read per request, affecting the "lightweight first" constraint at query volume.

### 4.5 No Team Validated Whether the EventBus Is Actually Lightweight at Scale

Team 3 proposes adding a bounded in-memory deque stream layer to the EventBus (~50 lines). The existing EventBus dispatches synchronously, swallows subscriber exceptions, and persists every event to SQLite before dispatching. At 5-second scan intervals with PROCESS_STARTED/PROCESS_DIED diffing, the event volume depends entirely on process churn. On a developer machine that compiles code, runs npm scripts, and spawns subprocesses, this could be hundreds of events per minute. No team estimated the event volume per hour in a real development environment or evaluated whether the synchronous SQLite write-per-event pattern is adequate at that rate.

---

## 5. Agreements — Where Independent Teams Converged

### 5.1 Strong Convergence: Trust Scoring Algorithm and Schema Alignment

Teams 1 and 3 independently arrived at Beta distribution-based trust scoring, both tracing it through MIDGE's ThompsonSampler. Both independently observed that Submantle's existing schema (`total_queries`, `incidents`, `registration_time`, `last_seen`) already captures the inputs needed. Neither team knew the other's approach when writing. This convergence is meaningful — it is the same mathematical insight arrived at from different entry points (Mae's mathematical laws via Team 1, MIDGE's implementation via Team 3). The underlying model is sound.

### 5.2 Strong Convergence: Enforcement Mode Ladder

Team 1 (Section 5.2) and Team 4 (implicitly in the three-phase healing discussion) both independently identified the value of a staged rollout: advisory logging before enforcement. This maps to Mae's own ConnectionRegistry behavior (PERMISSIVE → ADVISORY → BLOCKING). The principle is independently validated by the circuit breaker pattern in distributed systems literature (Team 4's external sources) and by Mae's endurance testing results. Do not enforce before you have baseline data. This is the most actionable and safest principle in the expedition.

### 5.3 Moderate Convergence: Background Scan Loop Needed

Teams 2, 3, and 4 all independently identified that Submantle's pull-based scan (triggered by API calls) is architecturally insufficient for a daemon that should be "always aware." Team 2 frames it as autopoietic closure. Team 3 frames it as a prerequisite for the ambient stream MCP server. Team 4 frames it as a watchdog heartbeat requirement. All three are pointing at the same gap: the scan loop must become push-based and self-sustaining. The convergence on this is genuine, even though the three teams frame the solution differently.

### 5.4 Moderate Convergence: Event Payload Contracts Are Fragile

Team 3 (Gap 6 in Mae's lessons) and Team 4 (Gap 6: Key mismatch pattern from Mae's HANDOFF.md) both flag that informal event payload contracts (plain dicts with no enforcement) are a maintenance liability. Mae's `node_id` vs `{"nodes": [...]}` mismatch silently failed for weeks. Submantle's EventBus passes plain dicts as `data` in every `emit()` call — the shape of each event type is documented only in docstrings and in the calling code, not in any enforced contract. Both teams flag this. It will become a real problem as event types multiply.

### 5.5 Moderate Convergence: Submantle Must Know Itself

Teams 2, 4, and (implicitly) 1 all independently arrive at the same principle: Submantle should include itself in its own awareness. Team 4 calls it autopoietic closure (Submantle appears in its own process scan as a critical process). Team 2 calls it `know_self` from the holon protocol (Submantle knows its own version, configuration, and health). Team 1 calls it the balance feedback pathway (agents get trust score signals). The meta-principle is the same: a system that monitors everything but knows nothing about itself is incomplete. The specific mechanisms differ but the insight converges.

---

## 6. Surprises — What Changed This Validator's Thinking

### 6.1 The Code Reveals a Critical Gap All Teams Understated: `increment_agent_incidents()` Is Never Called

All four teams build recommendations on top of the `incidents` field in the agent registry schema. Team 1 explicitly flags this as Gap 1: "The `incidents` field exists in Submantle's schema, but there is no code that calls `increment_agent_incidents()`." Team 3 does not flag this gap at all — it proceeds as if the incident counter is functional. Team 4 does not address it.

Reading the actual code confirms Team 1's observation: `database.py` has `increment_agent_incidents()` implemented (line 309), and `agent_registry.py` has `record_query()` that increments `total_queries`, but there is no call path anywhere in the codebase from any observable behavior to `increment_agent_incidents()`. An agent can make malformed queries, trigger rate limits, or behave anomalously, and `incidents` stays zero forever.

This means: **every trust scoring recommendation from all four teams is building on an input that has no current means of being populated.** The Beta distribution model, the composite trust formula, the Thompson scoring — all require a non-trivial definition of "what counts as an incident" and code that detects and records it before any trust scoring is meaningful. This is the most consequential finding the actual code reveals, and only Team 1 surfaced it clearly. The other three teams proceeded as if the missing piece were merely an algorithm, when the missing piece is actually the detection and recording of incidents in the first place.

### 6.2 The Convergence Scoring Upgrade Is More Architecturally Disruptive Than Presented

Team 3's Action 2 (upgrade `query_what_would_break` to convergence scoring) is presented as "High impact, medium work." Reading the actual `substrate.py` code reveals that `query_what_would_break()` is a pure function that takes `(target_name, processes, tree)` as inputs. To add runtime behavioral signals (Domain 3: abnormal CPU/memory), the function would need access to scan history (currently only available through the DB layer, not passed to this function) or previous scan deltas (available in `_previous_processes` in `api.py` as a module-level global, not accessible inside `substrate.py`).

Adding convergence scoring requires either: (a) passing additional arguments to `query_what_would_break()`, changing its signature and all call sites including tests, or (b) making it stateful by giving it access to the DB, which contradicts its design as a pure function. Team 3 presents this as a localized improvement; it is actually an interface change with wider implications.

### 6.3 Team 4's Highest-Priority Item Is Not in Any Other Team's Plan

Team 4's top-priority recommendation is: "Add a Submantle identity signature to `signatures.json` for the Submantle daemon process." This is 1 hour of work, closes the autopoietic loop, and makes Submantle self-aware in its own reports. No other team mentions this. It does not appear in Team 1's trust architecture, Team 2's structural patterns, or Team 3's signal intelligence — even though all three teams discuss self-awareness as a principle.

This is genuinely the simplest, most targeted action item in the entire expedition. A single JSON entry. The fact that three other teams discussing the same principle missed the obvious concrete implementation is a coordination gap. It would be easy to lose in a 15-item cross-team priority queue.

---

## Overall Verdict

### What Holds Up Well

The expedition produced three findings that are well-evidenced, code-grounded, and immediately actionable without architectural disruption:

1. **The enforcement mode ladder for trust scoring** (Team 1, corroborated by Team 3). Advisory before blocking. No new infrastructure. No schema changes required beyond adding a `compute_trust()` call.

2. **Add Submantle's own identity signature to `signatures.json`** (Team 4). One JSON entry. Closes the autopoietic loop without touching any code.

3. **The EventBus stream layer for the MCP ambient stream** (Team 3). Bounded in-memory deque. Genuinely low-friction and addresses a real gap that will be hit when the MCP server is built.

### What Requires Caution Before Building

1. **Any trust scoring implementation** — Teams 1 and 3 both require incident detection to be implemented first. No incident detection = no meaningful trust score, only a proxy formula that reads zero incidents for every agent. Define and build incident detection before building the scoring formula.

2. **Convergence scoring for `query_what_would_break`** (Team 3, Action 2) — requires either a signature change on a function tested by the test suite, or giving the function DB access, changing its purity. This is more disruptive than presented.

3. **Teams 1 and 3's trust scoring approaches need to be reconciled into one design** — they are not compatible as written. Choose one before implementing.

### What Should Be Deferred or Discarded for the Prototype

- Granger causality analysis (Team 3) — data requirements, stationarity assumptions, and engineering complexity do not fit the prototype stage
- Circadian-aware scheduling (Team 4) — useful, but not a Mae principle transfer, and has an unvalidated Windows permission dependency
- Full LLM-enhanced holonic routing (Team 2) — explicitly deferred by the team itself; needs no further discussion now
- Physarum optimizer for process relationship weights (Team 4) — correctly labeled V2+

### Critical Action Before Any Build

**Define what an "incident" is for Submantle agents, and wire `increment_agent_incidents()` into the code path where incidents occur.** Until this is done, every trust scoring recommendation across all four teams is building on an empty input. This is the single most important gap in the entire expedition, and it was adequately surfaced only by Team 1.
