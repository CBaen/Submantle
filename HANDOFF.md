# Substrate — Handoff

## What This Is
The ground beneath everything. A persistent awareness layer AND behavioral trust infrastructure for computing. Your devices know what's going on, and the agents on them earn their place.

## Current State
- **Phase**: V1 Foundation built, trust layer expedition complete, dashboard depth next
- **Git**: github.com/CBaen/SUBSTRATE (main branch, uncommitted research files)
- **Server**: `python -m uvicorn api:app --port 8421` from `prototype/` — dashboard at localhost:8421
- **Tests**: 160 passing across 4 test files
- **Research**: 3 expeditions complete (deep-dive, infrastructure, trust-layer) + 6 targeted follow-ups

## What Just Happened (2026-03-11)

### Trust Layer Expedition — Complete
5 research teams (Opus) + 3 validators (Opus) + 6 targeted follow-ups. All files in `research/expedition-trust-layer/`.

**Key Findings (validated):**
- The behavioral trust gap is real and unoccupied. No protocol, product, or standard fills it. Confirmed by 5 teams, 3 validators, 6 follow-ups.
- Mastercard's "Verifiable Intent" (March 5, 2026) explicitly excludes behavioral trust from its spec. Complementary, not competitive.
- W3C VC 2.0 + SD-JWT (not BBS+) for V1 trust attestations. BBS+ is still a Candidate Recommendation — use SD-JWT (RFC 9901, finalized November 2025).
- Pure Beta formula for V1: trust = total_queries / (total_queries + incidents). Initialize at (1,1) = 0.5.
- EU AI Act: Substrate likely outside scope entirely (deterministic arithmetic, not ML).
- cheqd has MCP toolkit for VC issuance but NO behavioral trust. Complementary infrastructure, not a competitor.
- Three active IETF drafts exist (Huawei, AWS/Zscaler/Ping) for agent identity — NONE cover behavioral trust. Gap uncontested at standards level.
- Solo founder + AI model works for product phase. Protocol phase needs technical contributors.
- Realistic MVTL timeline: 5 focused sessions, not 1.

**Design Decision Resolved:**
"Always aware, never acting" applies to the ENTIRE system including the trust layer. Substrate exposes trust scores. Third parties (brands, platforms) enforce their own thresholds. Substrate never blocks, never gates, never throttles. This makes Substrate infrastructure (like Visa), not a gatekeeper. More financial opportunities, not fewer — every consumer of trust data needs their own enforcement layer built on top.

### V1 Foundation — Previously Built (2026-03-10)
3 builders (Opus) + 3 reviewers (Opus). All files in `research/triadic-build-v1-foundation/`.

**Built:**
- **Privacy Mode** (`privacy.py`) — Real off switch. AWARE/PRIVATE toggle, thread-safe, persisted across restarts.
- **SQLite Persistence** (`database.py`) — Four tables: scan_snapshots, agent_registry, events, settings. WAL mode.
- **Event Bus** (`events.py`) — Internal pub/sub. 7 event types. Privacy filtering at bus level.
- **Agent Identity** (`agent_registry.py`) — HMAC-SHA256 tokens, cryptographic registration, trust tracking schema.
- **Integration** — All modules wired into api.py and substrate.py. 5 new API endpoints. Dashboard privacy toggle.

**Open issues from V1 build (noted for next round):**
- Open agent registration (no rate limit/passphrase) — fix before WiFi deployment
- CORS wildcard — lock to localhost before V1
- No API endpoint tests
- record_query() not wired in api.py — trust data doesn't accumulate yet
- No uniqueness constraint on agent names — decide before trust scoring

## What Exists

### Foundation Modules (prototype/)
- `database.py` — SubstrateDB class, SQLite persistence, WAL mode
- `events.py` — EventBus class, 7 event types, privacy filtering
- `privacy.py` — PrivacyManager class, AWARE/PRIVATE states
- `agent_registry.py` — AgentRegistry class, HMAC-SHA256 tokens
- `tests/` — 160 tests across 4 test files

### Existing (prototype/)
- `dashboard.html` — Anthropic-styled dashboard with privacy toggle
- `api.py` — FastAPI server, 10 endpoints (5 original + 5 new)
- `substrate.py` — Core scanning + scan_with_events()
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
- `research/expedition-trust-layer/` — Trust layer expedition (17 files: 5 teams, 3 validators, 1 synthesis, 6 follow-ups, 1 brief)
- `research/triadic-build-v1-foundation/` — V1 build (brief, 3 builder reports, 3 reviewer reports)
- `research/expedition-substrate-infrastructure/` — Second expedition
- `research/expedition-substrate-deep-dive/` — First expedition
- `research/future-expeditions.md` — Agent reviews, privacy UX, payment processor

## What to Build Next

### Priority 1: Dashboard Depth (Guiding Light's direct request)
- Clickable device rows that expand to show everything Substrate knows
- Process categories with nested detail views
- "Ask Substrate" results with full dependency chains
- Every field that shows a count should be expandable

### Priority 2: Trust Layer Wiring (MVTL — 5 sessions)
1. Auth middleware on /api/query (token-based, wired to agent registry)
2. Incident taxonomy definition (Guiding Light's product decision)
3. record_query() wired to endpoints (every interaction becomes trust data)
4. Agent name uniqueness enforcement
5. compute_trust() using pure Beta formula, trust score in API responses

### Priority 3: MCP Server
- Ambient awareness stream (agents subscribe, receive events without asking)
- Deep query tools (agents ask specific questions on demand)
- Agent registration via MCP protocol
- Wire into the event bus (wildcard subscription → MCP stream)

### Priority 4: Dashboard Polish
- Mobile-responsive (phone visits laptop-ip:8421 over WiFi)
- Lock CORS to localhost
- Agent registration passphrase

## Architecture
- **Prototype**: Python (FastAPI, psutil, SQLite, stdlib crypto)
- **Production** (future): Go daemon, gRPC API, SQLite knowledge graph
- **Integration**: MCP server (agents query via Model Context Protocol)
- **Trust**: Pure Beta formula (deterministic), W3C VC 2.0 + SD-JWT for attestations
- **Privacy**: On-device processing, real off switch, no telemetry

## Open Decisions
- Open-source license (Apache 2.0 / BSL / AGPL)
- Incident taxonomy (what specific agent behaviors constitute an incident — product decision)
- Agent name uniqueness constraint (before trust scoring)
- Success metrics for the 90-day experiment
