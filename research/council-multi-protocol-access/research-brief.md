# Research Council Brief: Multi-Protocol Access Strategy
## Date: 2026-03-12
## Project: Submantle

### The Question
Should Submantle support multiple access protocols (REST API, MCP, CLI, plugins) and how should access be gated? Does the "exchange hub" vision — where different protocols converge and agents/brands interact through shared trust data regardless of how they connect — fit Submantle's positioning, or does it push toward a marketplace model that conflicts with "always aware, never acting"?

### Why Now
GL's insight that neutral infrastructure shouldn't favor one protocol. A TikTok about CLI tools vs. MCP reinforced that the agent ecosystem is fragmenting across access methods. Wave 5 (MCP server) is next on the build priority — this is the moment to decide whether MCP alone is sufficient or if the strategy should be broader.

### Expected Outcome
A clear priority ordering for which protocols to build and when. A position on open vs. gated access with precedent analysis. A verdict on whether "exchange hub" strengthens or endangers the credit bureau positioning. Implementation recommendations that a solo founder can actually execute.

### Current State
- REST API exists: 13 endpoints on FastAPI (port 8421), including `/api/verify/{agent_name}` (trust score lookup), `/api/agents/register` (agent registration), `/api/incidents/report` (incident intake)
- No auth on score queries — anyone can hit `/api/verify/{agent_name}`
- Agent registration returns a bearer token used for authenticated operations (deregister, record_query)
- MCP server planned (Wave 5) — Python, stdio transport, no OAuth for V1
- No CLI tool exists
- No business API keys or billing
- Revenue model: businesses pay to check scores, agents register free (Experian model)

### Project Fingerprint
- Runtime: Python 3.14.2, FastAPI, uvicorn
- Key dependencies: FastAPI, psutil, pydantic, sqlite3 (stdlib)
- Architecture: Monolithic prototype — single FastAPI server, SQLite persistence, event bus, agent registry
- State management: SQLite (WAL mode) + in-memory EventBus
- Database: SQLite with agent_registry and incident_reports tables
- Core modules: database.py, agent_registry.py, events.py, privacy.py, api.py, submantle.py
- Known constraints: No ML, no enforcement, credit bureau model, solo founder, deterministic only, privacy by architecture
- Prior failed approaches: None for this specific question
- Active boundaries: Design principles are inviolable. Waves 1-4 architecture is settled. "Always aware, never acting" is non-negotiable.

### Constraints
- Solo founder building V1. Complexity is the enemy.
- "Always aware, never acting" — Submantle provides data, never enforces or mediates.
- Credit bureau model — Experian doesn't help you get a loan, it just tells the bank your score.
- Privacy by architecture — on-device computation where possible.
- Deterministic scoring only — no ML.
- Revenue model: businesses pay to check scores, agents register free.
- Must not violate neutrality — no protocol favoritism.

### Destructive Boundaries
- Do NOT modify the trust scoring formula or its data flow (Waves 1-4 are settled)
- Do NOT add enforcement mechanisms (blocking, gating, throttling)
- Do NOT add ML-based anything
- Do NOT propose blockchain dependencies
- Do NOT propose changes that would make Submantle an agent or marketplace

### Codebase Files for Analysis
- `prototype/api.py` — Full REST API surface (13 endpoints, FastAPI setup, auth patterns)
- `prototype/agent_registry.py` — Core business logic (register, verify, compute_trust, record_incident, record_query)
- `prototype/database.py` — SQLite persistence layer (tables, queries, schema)
- `prototype/events.py` — Event bus (pub/sub, privacy mode filtering)
- `prototype/submantle.py` — Process awareness layer (signatures, scanning)

### External Research Angles
1. **Multi-protocol precedents in neutral infrastructure**: How do DNS (UDP/TCP/DoH/DoT), certificate authorities (ACME/CMP/EST), credit bureaus (Metro 2/API/batch), and domain reputation services handle multiple access methods? Is there a canonical "thin adapter" pattern?
2. **Agent ecosystem protocol landscape (March 2026)**: What do Claude, GPT, LangChain, CrewAI, AutoGen, and other frameworks actually support? MCP adoption rate vs. REST vs. CLI. Where is the momentum?
3. **Open vs. gated access models**: VirusTotal (tiered API keys), Spamhaus (free for low volume), certificate transparency logs (fully open), credit bureaus (strictly gated). What model fits a trust bureau for AI agents?
