# Research Brief: Mae/MIDGE Architectural Principles for Submantle
## Date: 2026-03-10
## Project: Submantle

### Problem Statement
Submantle's V1 foundation is built (privacy mode, SQLite, event bus, agent identity — 160 tests). Before building further (dashboard depth, MCP server), Guiding Light wants to know what foundational principles from mae-core and MIDGE could set Submantle up for long-term success. These are sister projects — mae-core is a biologically-inspired multi-agent organism with 8 mathematical laws, and MIDGE is its market-specialized fork. Both contain deep architectural thinking that may transfer.

### Expected Outcome
A comprehensive map of every transferable principle from Mae/MIDGE to Submantle. Not integration planning — pure inspiration. "What did we learn building Mae that we should carry into Submantle's DNA before the foundation hardens?"

### Current State

**Submantle (what exists):**
- `prototype/privacy.py` — PrivacyManager, AWARE/PRIVATE states, thread-safe
- `prototype/database.py` — SubmantleDB, SQLite persistence, WAL mode, 4 tables
- `prototype/events.py` — EventBus, 7 event types, privacy filtering, wildcard subscriptions
- `prototype/agent_registry.py` — AgentRegistry, HMAC-SHA256 tokens, trust schema
- `prototype/substrate.py` — Process scanning, signature matching, impact queries
- `prototype/api.py` — FastAPI, 10 endpoints
- `prototype/dashboard.html` — Anthropic-styled frontend with privacy toggle
- 160 tests across 4 test files

**Mae-core (source of principles):**
- 92 systems, 2583 tests, 107 holons, 328 connections
- 8 mathematical laws governing every change
- 32-layer bootstrap, 14 mixins on MycelialAgent
- MycelialSubmantle module: topology, nutrient flow, signal propagation
- Holon Protocol: 10 capabilities at every scale
- Fractal self-similarity, stem cell principle, autopoietic closure

**MIDGE (source of principles):**
- 149 systems (92 core + 57 market), 4536 tests
- 34 data sources, convergence engine, Thompson Bayesian learning
- Pattern archaeology, hypothesis engine, multi-timeframe analysis
- DrawdownMonitor circuit breaker, SelfMonitor anomaly detection

### Project Direction
Submantle is an ambient awareness layer for computing — "the ground beneath everything." Next steps: dashboard depth (nested data, clickable detail views), then MCP server (ambient stream + deep queries for agents). Production rewrite in Go is future. The prototype is Python for proving concepts.

### Constraints
- **Lightweight first** — Submantle must be invisible in resource usage
- **Community knowledge over AI inference** — signatures, not LLMs
- **Privacy by architecture** — on-device, no telemetry
- **Always aware, never acting** — provides knowledge, doesn't act
- **Don't over-engineer the prototype** — it's for proving concepts
- **No integration planning** — treat Mae/MIDGE purely as inspiration, not as future integration targets

### Destructive Boundaries
- Do NOT recommend importing Mae's complexity wholesale
- Do NOT suggest adding LLM-based classification
- Do NOT propose changes that would make Submantle an agent
- Do NOT recommend anything that requires external infrastructure (Redis, Qdrant, etc.)
- Do NOT suggest restructuring what's already built — find principles that enhance, not replace

### Research Angles

**Angle 1: Mathematical Foundations & Trust Architecture**
Investigate which of Mae's 8 mathematical laws apply to an awareness layer. Focus on Law 1 (No Bare Dyads / triadic witnessing), Law 7 (Rule of 3/5 validation consensus), and how they could inform Submantle's agent trust scoring and verification architecture. Also examine Mae's ConnectionRegistry pattern and TriadEnforcer.

**Angle 2: Structural Composition Patterns**
Investigate how Mae's Holon Protocol (10 capabilities: sense, remember, decide, act, learn, heal, know_self, know_up, know_down, know_peers), fractal self-similarity (Law 4), and stem cell principle (Law 5: one class, specialization via config) could inform how Submantle's modules compose and scale. Look at the mixin decomposition pattern and how it keeps the codebase clean.

**Angle 3: Signal Intelligence & Convergence**
Investigate what MIDGE's convergence engine (fires when 3+ independent domains agree), Thompson Bayesian learning (signal reliability tracking), and EventBus channel architecture teach about Submantle's event system, "what would break?" queries, and ambient awareness stream design.

**Angle 4: Resilience & The Submantle Metaphor**
Mae literally has a MycelialSubmantle module — topology management, nutrient flow, signal propagation, health monitoring, starvation detection, region isolation. Investigate what Submantle (the product) can learn from MycelialSubmantle (the module), plus Mae's auto-healing patterns, endurance hardening, and the way it serves as "the soil everything grows in."

### Team Size: 4
Each angle covers a distinct architectural domain. The codebases are large (mae-core: 92 systems, MIDGE: 149 systems) and deeply interconnected. 4 teams ensures thorough coverage without overlap.

### Failed Approaches
None specific to this research. However, the fresh-eyes audit from earlier in this session noted that previous Submantle research was "AI researching for AI validators audited by AI" — teams should ground findings in concrete, transferable patterns, not abstract theory.
