# Team 2 Findings: Structural Composition Patterns
## Date: 2026-03-10
## Researcher: Team Member 2

---

### Preamble: What Was Investigated

This report investigates five structural composition principles from Mae's architecture — the Holon Protocol (10 capabilities), Fractal Self-Similarity, the Stem Cell Principle, Mixin Decomposition, and Autopoietic Closure — and asks: which of these transfer to Submantle, a lightweight process-awareness daemon, and how?

The codebase read was complete: all six Submantle prototype files (substrate.py, database.py, events.py, privacy.py, agent_registry.py, api.py), all five Mae source files (holon_protocol.py, fractal_generator.py, stem_cell.py, mycelial_agent.py, MAES_BIOLOGY.md), and the MAES-MATHEMATICAL-IDENTITY.md document. External research covered mixin composition, holonic architecture, fractal component models, autopoiesis in software, and configuration-over-code patterns, drawing on 2024-2025 sources.

One meta-finding runs through everything: **Mae's structural patterns were designed for an agent (something that acts); Submantle is a ground (something that knows).** This distinction governs every recommendation below. Not every Mae pattern transfers — and naming which ones do not is as important as naming which ones do.

---

### Battle-Tested Approaches

#### 1. Mixin Decomposition for Growing Codebases

**What Mae did:** A 4,225-line god-class (MycelialAgent) was decomposed into a 136-line base plus 10 composable mixins, each with a uniform interface: `_init_{name}()`, `_serialize_{name}()`, `_restore_{name}()`, `get_{name}_statistics()`. The MycelialAgent calls each initializer explicitly in its `__init__`, bypassing Python's MRO for initialization — a deliberate choice that trades MRO elegance for predictable, readable startup order.

**External validation:** This pattern is recognized as a production best practice for large Python codebases. Real Python (2025), Adam Johnson (2025), and The Digital Cat all confirm: mixins should be single-responsibility, should avoid owning `__init__` state, and should be named with a `Mixin` suffix for clarity. The explicit initializer approach (`_init_subsystem()` instead of relying on `super().__init__()`) is specifically recommended when MRO chains become complex or ordering matters — which it will as Submantle grows.

**Source evidence:**
- "Nine times out of ten, you should refrain from putting state into your mixin classes." (Real Python, 2025)
- "Don't include `.__init__()` in your mixin classes unless you have a compelling reason." (Real Python, 2025)
- "Mixins make it so obvious which features an object supports that oftentimes you can read it right off of the class signature." (residentmar.io, 2019, still widely cited)

**Current Submantle state:** Submantle has no mixin pattern today. Its five modules (substrate.py, database.py, events.py, privacy.py, agent_registry.py) are standalone files, not classes that compose. They wire together at the `api.py` level via dependency injection. This is clean for a prototype but creates a ceiling: as features grow, each module will accumulate responsibilities. The database already has four distinct concerns (scan snapshots, agent registry, events, settings).

**Transfer verdict:** High-confidence transfer. When Submantle grows beyond the prototype — especially when adding device awareness, network awareness, and plugin data sources — the mixin pattern is the right tool for keeping modules from becoming the next god-class. The explicit `_init_{name}()` convention is particularly valuable because Submantle has a strict initialization order (DB → EventBus → PrivacyManager → AgentRegistry) that benefits from explicit, readable sequencing.

---

#### 2. The Fractal Component Model — Same Interface, Every Level

**What Mae did:** FractalGenerator organizes Mae's 92 systems into a hierarchy: individual processes → subsystems (triads of 3) → modules → organs → organism. The key architectural property is that the same 10-capability interface (sense, remember, decide, act, learn, heal, know_self, know_up, know_down, know_peers) operates at every level. A single process and the organism as a whole answer the same questions. The resolution changes; the protocol does not.

**External validation:** The Fractal Component Model (France Telecom / INRIA, introduced 2001) is an independently validated precedent for exactly this pattern. Its defining characteristic is that "architecture is expressed homogeneously at arbitrary levels of abstraction." The fractal model is production-proven: Julia (Java), Plasma (C++), ProActive (distributed grid computing) all use it. Key production principle: components must support recursivity (nesting) and reflexivity (introspection about their own structure). The 2024 article "Software is fractal" (Javier Holguera, 2024) independently confirms that when problems repeat at every scale, the same mental model — and the same API — should apply at every scale.

**Where Mae's fractal breaks:** MAES-MATHEMATICAL-IDENTITY.md is honest: the fractal structure breaks at the leaves (opaque Python objects with no internal triadic structure) and at the organism level (5 organs, not 3). Mae's hierarchy is "triadic where possible." This is the right honesty to carry forward — a target structure, not an immutable constraint.

**Transfer to Submantle:** Submantle has three natural scales that map directly to Mae's fractal levels:

| Mae Level | Submantle Equivalent | What It Knows |
|-----------|---------------------|---------------|
| Process (leaf) | Individual data collector | One metric stream (e.g., process scan, sensor reading) |
| Subsystem | Awareness domain | Process awareness, device awareness, network awareness |
| Organ | Ring | Inner ring (software), Middle ring (hardware), Outer ring (environment) |
| Organism | Submantle | The ground beneath everything |

This mapping is not forced — it already exists in Submantle's design vision. The fractal pattern would make it explicit and give every level the same query interface. An agent asking "what's running?" would address the same interface whether it wants inner-ring process data or outer-ring weather/public data.

**Transfer verdict:** High-confidence structural inspiration. The fractal grouping concept (naming the hierarchy levels explicitly) is directly applicable. The "same interface at every level" is achievable for Submantle's query API. However: do not implement a full FractalGenerator in the prototype. The fractal registry is organizational metadata — it costs little to add but clarifies the architecture enormously.

---

#### 3. Configuration Over Code for Data Sources (Stem Cell Principle)

**What Mae did:** AgentGenome defines a catalog of 22 configurable parameters across 10 mixins. Every agent starts as STEM (undifferentiated). Specialization happens by applying an epigenome — a role profile that activates a subset of genes. Nine role profiles (EXPLORER, LEARNER, COMMUNICATOR, HEALER, etc.) exist as pure configuration dictionaries. The `redifferentiate()` function swaps one role profile for another at runtime without changing code. An EXPLORER can become a LEARNER by updating its epigenome.

**External validation:** The "configuration over code" principle is well-established in plugin architectures. The StemCellFactory (biotech automation, Frontiers 2020) independently arrived at the same architecture: agent-based software where adding a new device requires only changing software agent configuration, not rewriting code. Cloud Foundry BOSH uses "stemcells" — base OS images that take on role identity through configuration at deploy time. The Holonic Learning framework (arXiv 2024) uses the same structural principle: a universal holon that specializes via configuration to become a leaf node, aggregator, or coordinator.

**Current Submantle state:** Submantle's signatures.json already embodies a version of this principle — a community-curated catalog where each signature is a configuration record (exe_contains, cmdline_contains, importance, category, description) rather than code. A process scanner that matches "node" is not a different class from one that matches "chrome" — it's the same scanner with different signature data.

**The full Stem Cell transfer for Submantle:** Submantle will eventually need multiple types of awareness collectors: process scanners, hardware sensors, network scanners, location providers, calendar/context providers. Today, each would likely become its own module (hardware_scanner.py, network_scanner.py, etc.). The Stem Cell principle says: build one `AwarenessCollector` base with a uniform interface, and let each data source be a configuration record that tells the collector what to ask for and how to interpret results.

Example genome for an AwarenessCollector:
- `source_type`: "process" | "hardware" | "network" | "sensor" | "public_api"
- `scan_interval_seconds`: int (default 5)
- `privacy_sensitive`: bool (whether to suppress in PRIVATE mode)
- `output_schema`: the expected shape of collected data
- `signature_set`: which signature file to use for identity matching

All collectors share the same lifecycle: `collect()` → `identify()` → `emit()`. No new classes for new data sources. Only new configuration profiles.

**Transfer verdict:** High-confidence, directly applicable. Submantle's signatures.json is already the genome. The next step is ensuring all future data collectors use the same base interface rather than bespoke classes.

---

### Novel Approaches

#### 4. Selective Holon Protocol — 4 of 10 Capabilities for an Awareness Layer

**The full protocol:** Mae's HolonMixin implements 10 capabilities at every level: sense, remember, decide, act, learn, heal, know_self, know_up, know_down, know_peers.

**The critical constraint:** Submantle is "always aware, never acting." It provides knowledge; agents and apps act on it. This eliminates certain capabilities from the protocol entirely and transforms others. The question is: which of the 10 capabilities make sense for a *ground*, not an *agent*?

**Analysis of all 10:**

| Capability | Mae's Purpose | Submantle's Equivalent | Transfer? |
|-----------|--------------|----------------------|-----------|
| **sense** | Perceive local state + neighbors | Scan processes, hardware, network — this IS Submantle's core function | Yes — this is what Submantle does |
| **remember** | Store/retrieve experiences | SQLite persistence of scan history, event log | Yes — already implemented |
| **decide** | Three-tier routing (reflex/habit/deliberation) | Submantle does not decide. Decisions belong to agents and apps. | No — violates "never acting" |
| **act** | Execute in domain | Submantle does not act. Same reason. | No — violates "never acting" |
| **learn** | Update from outcomes | Learning from what agents query (e.g., which signatures are most useful) could inform signature prioritization | Partial — relevant for Submantle Insights, not V1 |
| **heal** | Detect/recover from failures | Self-health monitoring: is the scan loop running? Is the DB accessible? | Yes — Submantle must know when it's degraded |
| **know_self** | Maintain self-model | Submantle knowing its own version, configuration, active privacy mode, scan frequency | Yes — this is the /api/health and /api/status pattern |
| **know_up** | Aware of parent context | Submantle-as-infrastructure knowing about the device it runs on (OS version, hardware class) | Partial — useful for future multi-device awareness |
| **know_down** | Aware of child components | Submantle knowing its own sub-modules: scanner, event bus, agent registry, privacy manager | Yes — critical for health monitoring and startup validation |
| **know_peers** | Aware of siblings | Submantle instances on other devices in the awareness mesh | Yes — relevant for future mesh, not V1 |

**The 4-capability subset that maps cleanly to V1:**

1. **sense** — scan processes, hardware, network (core function)
2. **remember** — persist to SQLite with history (already built)
3. **heal** — detect degradation, report it, attempt recovery
4. **know_self / know_down** — (treat as one) Submantle knows its own components, their health, and its current configuration

This is not a diminishment of the holon protocol. It is the holon protocol applied correctly to an awareness layer's nature. Mae's MAES-MATHEMATICAL-IDENTITY.md is explicit: "The resolution changes. The pattern does not." For an awareness layer, `decide` and `act` have zero resolution. `sense`, `remember`, `heal`, and `know_self` have full resolution.

**Novel application:** A lightweight `SubmantleHolon` dataclass — not a full Mae HolonProxy — could encode these four capabilities as a health interface that every Submantle module implements. The AwarenessPulse equivalent for Submantle would periodically call `get_health()` on each module and publish a `substrate.health_pulse` event. Any agent or dashboard subscribes to this and knows Submantle's self-assessment without making individual API calls.

**External validation:** The Holonic Learning framework (arXiv 2024) demonstrates the same selective implementation: holon nodes implement only the capabilities relevant to their role (leaf nodes implement less than coordinator nodes). Full 10-capability implementation is for agents; subsets are appropriate for infrastructure components.

**Transfer verdict:** Novel but well-grounded. The selective holon protocol (4 capabilities) is the correct adaptation for a non-agent awareness layer. The key insight is that `sense`, `remember`, `heal`, and `know_self` form a coherent subset — an awareness layer that perceives, remembers what it perceived, knows when it's degraded, and can report on its own state.

---

#### 5. Autopoietic Closure as a Self-Health Loop (Bounded)

**What Mae implements:** Components produce the processes that produce the components. Maintenance loops are operational (heal, repair, resource allocation). The system sustains itself.

**The honest Mae assessment (from MAES-MATHEMATICAL-IDENTITY.md):** "The architecture is built for autopoiesis; full closure requires systems that can produce new systems, not just maintain existing ones." Mae has maintenance loops (operational) but not full production loops (systems creating other systems). The meta-review score: this is a design target more than a full implementation.

**The narrow transfer that is genuinely useful for Submantle:** Submantle already has a partial autopoietic loop:
- The scan loop (`_get_state()` in api.py) runs on every API call with a 5-second TTL
- It calls `scan_with_events()`, which produces process data
- Process data is persisted to SQLite
- The EventBus emits events that (in future) agents subscribe to
- Agents query back through the API, closing a loop: Submantle-data → agent-query → Submantle-response

The gap: the scan loop is pull-based (triggered by API calls), not push-based (running independently). A background thread or periodic task that scans continuously would make the loop genuinely self-sustaining rather than dependent on external polling.

**What autopoiesis concretely means for Submantle V1:** A `SubmantleLoop` class that:
1. Runs an independent background scan cycle (no API poll required to keep it alive)
2. Monitors its own health (is the scan running? Is the DB writable?)
3. Emits `substrate.loop_alive` events at Fibonacci-cadenced intervals (e.g., every 5 seconds)
4. Attempts self-recovery if the scan loop stalls (restart the scanner thread)

This is not philosophical — it is the difference between a daemon that knows it's alive and one that only appears alive when poked.

**External validation:** The arXiv paper "Self-sustaining Software Systems (S4)" (2024) identifies the same gap in most monitoring tools: they monitor external systems but do not monitor themselves with the same rigor. The operational closure pattern (a component that verifiably continues producing its own operational state) is cited as a core property of resilient infrastructure.

**Transfer verdict:** Novel but bounded. Full autopoiesis (Submantle spawning new Submantle instances) is out of scope and out of character. The bounded version — a self-sustaining scan loop that monitors itself — is directly applicable and practically important for a daemon that must be "always aware."

---

### Emerging Approaches

#### 6. LLM-Enhanced Holonic Architecture (Relevant to Future Only)

**What exists:** A 2025 arXiv paper ("LLM-Enhanced Holonic Architecture for Self-Adaptive System of Systems") proposes adding LLM reasoning layers to holonic architectures. Supervisor holons use LLMs to interpret natural language queries and route them to appropriate sub-holons.

**Why this is flagged:** It directly addresses the use case Submantle will face — agents asking natural language questions about system state ("What would break if Chrome crashed?"). The holonic routing pattern (question → ring → domain → collector) maps well to Submantle's three-ring architecture.

**The constraint:** Submantle's design explicitly prohibits LLM-based classification ("Don't add LLM-based process classification"). This prohibition is specifically about process identity (signatures handle this). It does not prohibit an LLM-enhanced query interface at the MCP layer. A future MCP server could accept natural language queries, decompose them through the holonic hierarchy, and return structured awareness data — without any LLM touching the process classification pipeline.

**Transfer verdict:** Not applicable to V1. File for consideration at MCP server stage. The "query decomposition via hierarchy" concept (not the LLM part) is relevant immediately.

---

#### 7. Holonic Distributed Learning for Multi-Device Mesh

**What exists:** Holonic Learning (arXiv 2024) proposes a self-similar hierarchy for federated machine learning. Each holon in the hierarchy can aggregate, forward, or compute, depending on its position. The privacy property is interesting: holons at higher levels only see aggregated outputs from children, never raw data.

**Why this is relevant:** Submantle's future multi-device mesh (phone + laptop + tablet) is exactly a holonic hierarchy. Each device is a leaf holon. A "personal mesh" holon aggregates across devices. Guiding Light's device-specific awareness stays on-device; cross-device aggregated insight lives at the mesh level.

**Transfer verdict:** Not applicable to V1. File for the multi-device architecture design. The privacy hierarchy (raw data at leaves, aggregates at higher levels) is directly compatible with Submantle's privacy-by-architecture principle.

---

### Gaps and Unknowns

**1. The composability ceiling for Submantle's current architecture.**
Submantle's current design is five independent modules wired in `api.py`. This is clean for a prototype. What is not known: at what point does the injection pattern in `api.py` become unmanageable? When Submantle adds hardware scanning, network scanning, and mobile companion sync, `api.py` will likely become the new god-class unless a compositional pattern is introduced earlier. The mixin pattern addresses this, but the transition point is unclear.

**2. Whether "know_down" (module health monitoring) needs a formal registry.**
Mae's HolonRegistry is substantial infrastructure (the full `holon_protocol.py` is 717 lines). Submantle's equivalent would be far lighter — likely a simple dict of `{module_name: health_check_callable}`. But the right scope for this registry is unknown without knowing how many modules Submantle will eventually have. The prototype has 5; the production system could have 20+.

**3. The scan loop architecture decision.**
The current scan loop is pull-based (5-second TTL on API calls). A push-based background thread is the correct autopoietic architecture, but it introduces concurrency complexity: thread safety for the process cache, coordination with the privacy manager, and clean shutdown behavior. Mae's AwarenessPulse (which runs on a step-count cadence, not wall-clock time) avoids this by running inside a simulation step loop. Submantle doesn't have a simulation loop — it runs as a daemon. The correct threading model for a production Go rewrite is clear (goroutines + channels); the right Python prototype approach is less certain.

**4. Fractal depth for Submantle's three-ring architecture.**
The Inner Ring (software) → Middle Ring (hardware) → Outer Ring (environment) maps to a depth-3 fractal hierarchy. Whether this needs an explicit `SubmantleFractalRegistry` (like Mae's `FractalGenerator`) or can stay as an implicit naming convention is unknown. The explicit registry adds introspective capability (any agent can ask "what rings does Submantle know about?") but adds overhead the prototype may not need yet.

**5. External literature on "awareness layers" as a recognized pattern.**
The search did not find prior art specifically named "awareness layer" as an architectural pattern in the monitoring/observability space. Existing systems (Prometheus, collectd, Sensu Go) are monitoring tools, not awareness layers — they measure and alert; they do not identify meaning or relationships. Submantle's identity-aware, relationship-modeling approach appears genuinely novel. This is a gap in validation, not a gap in the design.

---

### Synthesis

Mae's structural composition patterns are the output of a system that was *designed to act*. Submantle is designed to *know*. This is the governing constraint. The patterns that transfer are the ones concerned with how a system is organized and maintains itself, not the ones concerned with how a system decides and acts.

**Four high-confidence transfers:**

**Transfer 1: Mixin Decomposition** — apply when Submantle grows beyond 5 modules. The pattern: one `SubmantleBase` class, plus mixins for ProcessAwareness, DeviceAwareness, NetworkAwareness, AgentRegistry, Privacy. Each mixin: `_init_{name}()`, `_serialize_{name}()`, `get_{name}_health()`. This prevents the next god-class before it forms. Not needed in the prototype today; needed before the Go rewrite begins.

**Transfer 2: Fractal Hierarchy Naming** — name the three rings explicitly in code (not just in vision documents). A lightweight `AwarenessHierarchy` registry that maps domain names to their ring level costs almost nothing but gives agents and the dashboard a queryable map of what Submantle knows. The FractalGenerator concept without the machinery.

**Transfer 3: Configuration Over Code for Collectors** — extend the signatures.json pattern to all future data collectors. One `AwarenessCollector` base class; specialization via configuration profiles. New data sources (hardware sensors, network scanners) become new configuration files, not new Python modules with bespoke logic.

**Transfer 4: Selective Holon Protocol (4 capabilities)** — `sense`, `remember`, `heal`, `know_self/know_down`. Each Submantle module should answer: "Can you scan?" (sense), "What do you know from history?" (remember), "Are you healthy?" (heal), "What are your components?" (know_down). This is a lightweight health interface, not the full 10-capability Mae protocol. It can be implemented as a simple `HealthReportable` ABC (abstract base class) with four methods.

**One bounded novel transfer:**

**Transfer 5: Autopoietic Scan Loop** — a background thread running the scan cycle independently of API calls. The loop monitors its own health, emits `substrate.loop_alive` events, and attempts recovery if it stalls. This makes Submantle genuinely daemon-like: always aware, not just aware when asked.

**What does NOT transfer:**

- `decide`, `act`, `learn` from the Holon Protocol — these are agent capabilities. Submantle is the ground, not the organism.
- The full 10-capability HolonMixin, HolonProxy, HolonRegistry machinery — Mae's implementation is 717 lines and serves a 92-system organism. Submantle needs a 30-line health interface.
- The full FractalGenerator and FractalReport infrastructure — Submantle needs hierarchy naming, not hierarchy wiring.
- StemCellRegistry and redifferentiation — Submantle's "collectors" don't need to switch roles at runtime. Configuration profiles are fixed per collector type.
- Fibonacci cadences for behavioral timing — these govern Mae's agent step behavior. Submantle's timing is wall-clock (5-second scan TTL). Keep it simple.

**The DNA principle to carry forward:**

Mae's most durable lesson is not any specific pattern — it is the discipline of naming the levels. Every module in Mae knows whether it is a process, a subsystem, a module, an organ, or the organism. Every agent knows its capabilities and advertises them uniformly. Every connection is registered and witnessed.

Submantle should adopt this discipline: name the rings, name the capabilities each module provides, and register them in a queryable structure early — before the system is large enough to make this hard. The time to establish the organizational skeleton is when the skeleton is light. Mae learned this the hard way: the holon protocol was retrofitted onto 92 systems. Submantle can grow into it from the start.

---

### Research Sources (External)

- Real Python: "What Are Mixin Classes in Python?" — https://realpython.com/python-mixin/ (2025)
- Adam Johnson: "Python type hints: mixin classes" — https://adamj.eu/tech/2025/05/01/python-type-hints-mixin-classes/ (2025)
- Fractal Component Model (Wikipedia): https://en.wikipedia.org/wiki/Fractal_component_model
- Fractal Component-Based Software Engineering (ResearchGate, France Telecom / INRIA, 2001): https://www.researchgate.net/publication/220842163_Fractal_Component-Based_Software_Engineering
- Holonic Learning: A Flexible Agent-based Distributed Machine Learning Framework (arXiv 2024): https://arxiv.org/abs/2401.10839
- LLM-Enhanced Holonic Architecture for Self-Adaptive System of Systems (arXiv 2025): https://arxiv.org/html/2501.07992v1
- Self-sustaining Software Systems (S4) (arXiv 2024): https://arxiv.org/abs/2401.11370
- Holon Programming Model: A Software-Defined Approach for System of Systems (arXiv / ICSOFT 2024): https://arxiv.org/html/2410.17784
- Software is Fractal (Javier Holguera, 2024): https://javierholguera.com/2024/04/17/software-is-fractal/
- Holonomic Systems: What Arthur Koestler Can Teach Us About Software Architecture (DEV Community): https://dev.to/felipeness/holonomic-systems-what-arthur-koestler-can-teach-us-about-software-architecture-29hf
- Holons, Boundaries, and Context Graphs: From Koestler to SHACL: https://ontologist.substack.com/p/holons-boundaries-and-context-graphs
