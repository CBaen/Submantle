# Substrate — Handoff

## What This Is
The ground beneath everything. A persistent awareness layer for computing. Your devices finally understand what you're doing and protect you from losing it.

## Current State
- **Phase**: V1 Foundation built, dashboard depth next
- **Git**: github.com/CBaen/SUBSTRATE (main branch, 28 commits ahead of origin)
- **Server**: `python -m uvicorn api:app --port 8421` from `prototype/` — dashboard at localhost:8421
- **Tests**: 160 passing across 4 test files

## What Just Happened (2026-03-10)

### V1 Foundation — Triadic Build Complete
3 builders (Opus) + 3 reviewers (Opus). All files in `research/triadic-build-v1-foundation/`.

**Built:**
- **Privacy Mode** (`privacy.py`) — Real off switch. AWARE/PRIVATE toggle, thread-safe, persisted across restarts. Dashboard has prominent amber toggle in topbar.
- **SQLite Persistence** (`database.py`) — Four tables: scan_snapshots (with analytics_metadata column for future federated analytics), agent_registry, events, settings. WAL mode. No ORM.
- **Event Bus** (`events.py`) — Internal pub/sub. 7 event types. Privacy filtering at bus level. Wildcard subscriptions. Ready for MCP ambient stream.
- **Agent Identity** (`agent_registry.py`) — HMAC-SHA256 tokens, cryptographic registration, trust tracking schema. Only token hash stored. Timing-safe verification.
- **Integration** — All modules wired into api.py and substrate.py. 5 new API endpoints. Dashboard privacy toggle.

**Reviewer Findings (fixed):**
- P0: EventBus privacy filter was dead code — PrivacyManager never synced it. Fixed.
- P0: EventBus not synced on restart in PRIVATE mode. Fixed.
- Integration bug: delete_agent vs deregister_agent naming mismatch. Fixed by Integration builder.

**Reviewer Findings (noted for next round):**
- Open agent registration (no rate limit/passphrase) — fix before WiFi deployment
- CORS wildcard — lock to localhost before V1
- No API endpoint tests
- record_query() not wired in api.py — trust data doesn't accumulate yet
- No uniqueness constraint on agent names — decide before trust scoring

### Guiding Light's Product Feedback
- Dashboard fields are flat — **no nested data, no clickable depth**. Devices shows count but nothing about what's on the network. Process categories show names but no detail. "None of these fields have nested data. That's necessary."
- This is the priority for the next build round.

### Fresh-Eyes Audit (this session's instance)
New instance read all research from both expeditions and delivered an independent perspective:
- Research has been talking to itself (AI researching for AI validators audited by AI). Zero customer validation exists.
- Solo non-technical founder constraint is underweighted despite being the #1 finding across all teams.
- The "feeling" insight (your devices know what's going on) is the real product discovery.
- MCP server should be the value proof — let agents be the first users.
- Android companion is a trap for V1 — get Windows right first.
- Origin story ("Claude Code deleted my work") is the marketing.
- The name "Substrate" is perfect.

## What Exists

### Foundation Modules (NEW — prototype/)
- `database.py` — SubstrateDB class, SQLite persistence, WAL mode
- `events.py` — EventBus class, 7 event types, privacy filtering
- `privacy.py` — PrivacyManager class, AWARE/PRIVATE states
- `agent_registry.py` — AgentRegistry class, HMAC-SHA256 tokens
- `tests/` — 160 tests across 4 test files

### Existing (prototype/)
- `dashboard.html` — Anthropic-styled dashboard with privacy toggle
- `api.py` — FastAPI server, 10 endpoints (5 original + 5 new)
- `substrate.py` — Core scanning + new scan_with_events()
- `signatures.json` — 15 community-curated identity signatures

### API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/health | GET | Health check |
| /api/status | GET | Process awareness (privacy-gated) |
| /api/query | GET | "What would break?" queries (privacy-gated) |
| /api/devices | GET | Network device discovery |
| /api/privacy/toggle | POST | Toggle AWARE/PRIVATE |
| /api/privacy/status | GET | Current privacy state |
| /api/agents/register | POST | Register agent, get token |
| /api/agents | GET | List registered agents |
| /api/agents/{id} | DELETE | Deregister (requires Bearer token) |

### Research & Build Docs
- `research/triadic-build-v1-foundation/` — Build brief, 3 builder reports, 3 reviewer reports
- `research/expedition-substrate-infrastructure/` — Second expedition
- `research/expedition-substrate-deep-dive/` — First expedition
- `research/future-expeditions.md` — Agent reviews, privacy UX, payment processor

## What to Build Next

### Priority 1: Dashboard Depth (Guiding Light's direct request)
- Clickable device rows that expand to show everything Substrate knows
- Process categories with nested detail views
- "Ask Substrate" results with full dependency chains
- Every field that shows a count should be expandable

### Priority 2: MCP Server
- Ambient awareness stream (agents subscribe, receive events without asking)
- Deep query tools (agents ask specific questions on demand)
- Agent registration via MCP protocol
- Wire into the event bus (wildcard subscription → MCP stream)

### Priority 3: Dashboard Polish
- Mobile-responsive (phone visits laptop-ip:8421 over WiFi)
- Record_query() wired for trust tracking
- Lock CORS to localhost
- Agent registration passphrase

## Architecture
- **Prototype**: Python (FastAPI, psutil, SQLite, stdlib crypto)
- **Production** (future): Go daemon, gRPC API, SQLite knowledge graph
- **Integration**: MCP server (agents query via Model Context Protocol)
- **Privacy**: On-device processing, real off switch, no telemetry

## Open Decisions
- Open-source license (Apache 2.0 / BSL / AGPL)
- EU AI Act classification (August 2026 deadline)
- Agent name uniqueness constraint (before trust scoring)
- Success metrics for the 90-day experiment
