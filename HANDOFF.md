# Submantle — Handoff

## What This Is
The credit bureau for AI agents. Agents register, earn trust scores through interactions, and businesses pay to check those scores. Neutral infrastructure — Submantle never acts, never enforces. Brands decide their own thresholds.

## Current State
- **Phase**: STRATEGIC PIVOT — Trust bureau + MCP server is the V1 wedge. Dashboard follows when customers demand it.
- **Git**: github.com/CBaen/SUBMANTLE (main branch)
- **Server**: `python -m uvicorn api:app --port 8421` from `prototype/` — dashboard at localhost:8421
- **Tests**: 160 passing across 4 test files
- **Research**: 4 expeditions complete (deep-dive, infrastructure, trust-layer, protocol-architecture) + 6 targeted follow-ups

## What Just Happened (2026-03-11)

### STRATEGIC PIVOT SESSION — Most Consequential Session to Date (LATEST)
GL and Opus 4.6 conducted full product audit + 10-agent competitive expedition.

**Key Decisions Made:**
- **Trust bureau + MCP server is the V1 wedge.** Dashboard follows when customers demand it. Every successful infra platform (Stripe, Twilio, AWS) started with one sharp thing.
- **Scores change ONLY through interaction, never through time.** Last interaction date is visible metadata. No expiry, no degradation.
- **Interactions automatically generate trust data.** No manual reporting needed for core loop.
- **Businesses pay to check scores. Agents register free.** Experian model. Supply side (agents) is free. Demand side (brands) pays.
- **Submantle runs a verification service.** Brands query it directly. No complex credential-carrying for V1.
- **Awareness layer and trust layer are inside/outside views of one product.** Not two products. Inside = your machine. Outside = your agents in the world. Data flows one direction: trust scores INTO local display. Local data NEVER flows out.
- **Don't split into multiple companies.** Be the ONE standard. Let the ecosystem build on top.

**New Competitors Found:**
- **Signet** (agentsignet.com) — Closest trust competitor. Composite 0-1000 score, portable identity. BUT: no OS-level observation, scores based on reported data not behavioral evidence. Registry without bank statements.
- **Gen Digital Agent Trust Hub** — Launched Feb 2026, Vercel partnership, 500M devices. Pre-install scanning only, not runtime behavioral scoring. Sleeping giant confirmed awake but facing the wrong direction.
- **Microsoft Agent 365** — GA May 1, 2026, $15/user/mo. Full lifecycle management but Microsoft-scoped, not neutral.
- **Galileo Agent Control** — Open-sourced March 11, 2026. Policy-as-code control plane. Enforcement, not scoring.

**Visa/Mastercard Opportunity (Billion-Dollar Path):**
- Visa TAP (open-source) + Mastercard Verifiable Intent (open-sourced March 5) both handle transaction authorization but explicitly do NOT handle behavioral trust history.
- A Submantle trust score could be a field inside Mastercard's Verifiable Intent record (supports Selective Disclosure).
- Neither payment network can build neutral behavioral trust without favoring their own network.
- This is the moonshot: become the behavioral trust layer for agent commerce infrastructure.

**Acceleration Stack Identified:**
- OpenSaaS (Wasp) for SaaS skeleton, Supabase for DB + realtime, Tremor for dashboard components, Clerk for auth, Zuplo for API gateway with billing. Saves weeks of boilerplate.

### Protocol Architecture Expedition — Complete
5 research teams (Opus) + 9 validators (Opus). All files in `research/expedition-protocol-architecture/`.

**Key Findings (validated):**
- MCP confirmed as V1 integration surface (Go SDK v1.4.0, maintained by Google under Anthropic org)
- RATS RFC 9334 "Passport Model" maps precisely to Submantle's architecture — IETF standard vocabulary
- Behavioral trust gap confirmed with sharper boundaries: no one combines OS-level observation + deterministic scoring + on-device computation + portable VC attestation
- trustbloc/vc-go v1.3.6 — stable Go VC + SD-JWT stack (missed by researchers, caught by validators)
- Incident taxonomy RESOLVED: credit bureau model — Submantle records reports from third parties, doesn't detect incidents itself
- Android OS sandboxing blocks process awareness — desktop/laptop first, mobile later
- Solo non-technical founder protocol precedent: NONE documented. Product first, protocol later.
- Gen Digital (Norton, 500M devices) identified as sleeping giant — one pivot from competing
- IETF RATS working group is better first standards venue than AAIF

**Investor pitch validated:** "We're building the credit bureau for AI agents — every agent earns a trust score through behavior, carries it everywhere, and brands decide their own thresholds."

### Trust Layer Expedition — Complete
5 research teams (Opus) + 3 validators (Opus) + 6 targeted follow-ups. All files in `research/expedition-trust-layer/`.

**Key Findings (validated):**
- The behavioral trust gap is real and unoccupied. No protocol, product, or standard fills it. Confirmed by 5 teams, 3 validators, 6 follow-ups.
- Mastercard's "Verifiable Intent" (March 5, 2026) explicitly excludes behavioral trust from its spec. Complementary, not competitive.
- W3C VC 2.0 + SD-JWT (not BBS+) for V1 trust attestations. BBS+ is still a Candidate Recommendation — use SD-JWT (RFC 9901, finalized November 2025).
- Pure Beta formula for V1: trust = total_queries / (total_queries + incidents). Initialize at (1,1) = 0.5.
- EU AI Act: Submantle likely outside scope entirely (deterministic arithmetic, not ML).
- cheqd has MCP toolkit for VC issuance but NO behavioral trust. Complementary infrastructure, not a competitor.
- Three active IETF drafts exist (Huawei, AWS/Zscaler/Ping) for agent identity — NONE cover behavioral trust. Gap uncontested at standards level.
- Solo founder + AI model works for product phase. Protocol phase needs technical contributors.
- Realistic MVTL timeline: 5 focused sessions, not 1.

**Design Decision Resolved:**
"Always aware, never acting" applies to the ENTIRE system including the trust layer. Submantle exposes trust scores. Third parties (brands, platforms) enforce their own thresholds. Submantle never blocks, never gates, never throttles. This makes Submantle infrastructure (like Visa), not a gatekeeper. More financial opportunities, not fewer — every consumer of trust data needs their own enforcement layer built on top.

### V1 Foundation — Previously Built (2026-03-10)
3 builders (Opus) + 3 reviewers (Opus). All files in `research/triadic-build-v1-foundation/`.

**Built:**
- **Privacy Mode** (`privacy.py`) — Real off switch. AWARE/PRIVATE toggle, thread-safe, persisted across restarts.
- **SQLite Persistence** (`database.py`) — Four tables: scan_snapshots, agent_registry, events, settings. WAL mode.
- **Event Bus** (`events.py`) — Internal pub/sub. 7 event types. Privacy filtering at bus level.
- **Agent Identity** (`agent_registry.py`) — HMAC-SHA256 tokens, cryptographic registration, trust tracking schema.
- **Integration** — All modules wired into api.py and submantle.py. 5 new API endpoints. Dashboard privacy toggle.

**Open issues from V1 build (noted for next round):**
- Open agent registration (no rate limit/passphrase) — fix before WiFi deployment
- CORS wildcard — lock to localhost before V1
- No API endpoint tests
- record_query() not wired in api.py — trust data doesn't accumulate yet
- No uniqueness constraint on agent names — decide before trust scoring

## What Exists

### Foundation Modules (prototype/)
- `database.py` — SubmantleDB class, SQLite persistence, WAL mode
- `events.py` — EventBus class, 7 event types, privacy filtering
- `privacy.py` — PrivacyManager class, AWARE/PRIVATE states
- `agent_registry.py` — AgentRegistry class, HMAC-SHA256 tokens
- `tests/` — 160 tests across 4 test files

### Existing (prototype/)
- `dashboard.html` — Anthropic-styled dashboard with privacy toggle
- `api.py` — FastAPI server, 10 endpoints (5 original + 5 new)
- `submantle.py` — Core scanning + scan_with_events()
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
- `research/expedition-protocol-architecture/` — Fourth expedition (5 teams + 9 validators)
- `research/expedition-submantle-infrastructure/` — Second expedition
- `research/expedition-submantle-deep-dive/` — First expedition
- `research/future-expeditions.md` — Agent reviews, privacy UX, payment processor

## What to Build Next (REVISED 2026-03-11 — Strategic Pivot)

### Priority 1: Trust Layer Wiring (the wedge product)
1. Wire record_query() — every API call from registered agent generates trust data automatically
2. Agent name uniqueness enforcement
3. compute_trust() — Beta formula on real data, trust score in API responses
4. Auth middleware on /api/query (token-based)
5. Verification endpoint — businesses query agent trust scores (this is where revenue starts)
6. Interaction metadata schema — success, timing, patterns (not content — privacy-first)

### Priority 2: MCP Server (how agents connect)
- Agent registration via MCP protocol (every connecting agent is automatically a registrant)
- Trust score query tools (agents and brands check scores)
- Wire into event bus
- This is the "seven lines of code" moment — one integration, one outcome

### Priority 3: Dogfood Agents (prove the loop)
- Build simple test agents that register, interact with public APIs, accumulate real scores
- Analyze interaction data, refine scoring
- First entries in the trust registry — seed data

### Priority 4: Dashboard (second product, built when customers ask)
- Clickable device rows, process categories, nested detail views
- Agent trust score display (awareness layer CONSUMES trust data, doesn't produce it)
- Mobile-responsive, lock CORS, registration passphrase

## Architecture
- **Prototype**: Python (FastAPI, psutil, SQLite, stdlib crypto)
- **Production** (future): Go daemon, gRPC API, SQLite knowledge graph
- **Integration**: MCP server (agents query via Model Context Protocol)
- **Trust**: Pure Beta formula (deterministic), W3C VC 2.0 + SD-JWT for attestations
- **Privacy**: On-device processing, real off switch, no telemetry

## Open Decisions
- Open-source license (Apache 2.0 / BSL / AGPL)
- Agent name uniqueness constraint (before trust scoring)
- Success metrics for the 90-day experiment
- On-device daemon integrity (what stops lying about scores? — unsolved)
- Product name — RESOLVED: Submantle (submantle.com purchased, full rebrand complete 2026-03-11)
