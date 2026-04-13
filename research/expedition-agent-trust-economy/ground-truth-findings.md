# Ground Truth Findings — Agent Trust Economy Strategy
**Researcher:** Ground Truth (Codebase)
**Date:** 2026-04-12
**Question:** What does Submantle's codebase actually support today for agent registration at scale, what gaps exist, and how ready is it for the "free agents seed the network" strategy?

---

## 1. API Surface — What Actually Exists

**File:** `prototype/api.py` (914 lines), FastAPI, uvicorn, port 8421

### Agent Endpoints (fully implemented)
- `POST /api/agents/register` — registers agent, returns HMAC-SHA256 bearer token. Accepts: `agent_name`, `version`, `author`, `capabilities[]`. No auth required. No rate limit on this endpoint.
- `GET /api/agents` — lists all active agents (token hashes excluded)
- `DELETE /api/agents/{agent_id}` — self-deregister only (token must belong to agent_id)
- `GET /api/verify` — directory of all agents with SubScores. Soft pull default, hard pull at `?pull=hard` (costs 5x rate limit). Requires business context (anonymous=10/hr, free=100/hr, paid=1000/hr).
- `GET /api/verify/{agent_name}` — single agent SubScore lookup, same pull model
- `POST /api/incidents/report` — unauthenticated incident filing (reporter is a string, not a verified identity)

### Business Endpoints (fully implemented)
- `POST /api/business/register` — registers business, returns `sk_live_` prefixed API key (shown once, never recoverable)
- `GET /api/business/tiers` — public tier info
- `POST /api/stripe/webhook` — Stripe payment events, upgrades tier to "paid". Lazy import — server runs without Stripe installed.

### MCP Surface (read-only, 7 endpoints)
Exposed via `fastapi-mcp` at `/mcp`. Read-only by deliberate design decision. The 7 included operations: health, status, query, agents_list, verify_directory, verify_agent, privacy_status. Write operations (register, deregister, incident report) are REST-only.

### Other Endpoints
- `GET /api/query` — process dependency query (what would break if X stopped)
- `GET /api/status`, `GET /api/health` — system state
- `GET /api/devices` — local network ARP scan
- `POST /api/privacy/toggle`, `GET /api/privacy/status` — privacy mode control
- `GET /llms.txt`, `GET /.well-known/agent.json` — machine-readable discovery files
- `GET /`, `GET /trust`, `GET /landing` — HTML dashboard pages

---

## 2. Trust Layer — What the Formula Actually Is

**File:** `prototype/agent_registry.py`, `compute_trust()` method (lines 372-433)

**Formula:** `score = (q + 1) / (q + i + 2)`
- q = `total_queries` (incremented by `record_query()` on authenticated calls to `/api/query`)
- i = accepted incident count from `incident_reports` table WHERE `status = 'accepted'`
- New agents start at `(0+1)/(0+0+2) = 0.5` (unknown, not bad)

**Trust score fields returned:**
`agent_name`, `trust_score`, `total_queries`, `incidents`, `accepted_incidents`, `registration_time`, `last_seen`, `version`, `author`, `score_version` ("v1.0"), `has_history`, `reporter_diversity`, `is_active`

**Soft pull** returns only: `agent_name`, `trust_score`, `is_active`, `has_history`, `score_version`

**Incident pipeline (3 stages, implemented):**
1. Self-ping check: reporter == agent_name → auto-REJECTED (stored but not counted)
2. Dedup: same reporter + agent + type within 24h → DUPLICATE
3. Otherwise: auto-ACCEPTED (V1 design — no human review gate implemented yet)

**Incident types:** Freeform string. No enumerated taxonomy in code. Severity: "critical" or "standard" only. No velocity caps or query diversity rules are implemented in code (described in VISION.md as planned, not present in codebase).

**Anti-gaming measures actually implemented:**
- Self-ping rejection (yes)
- 24h dedup per reporter/agent/type (yes)
- Deregistered names permanently blocked from reuse (yes)
- Velocity caps: NOT implemented
- Query diversity rules: NOT implemented
- Rate limiting on registration endpoint: NOT implemented

---

## 3. Schema — Full Table Inventory

**File:** `prototype/database.py` (lines 765-880)

| Table | Purpose | Key columns |
|---|---|---|
| `scan_snapshots` | Process scan history | timestamp, data (JSON), process_count, identified_count, analytics_metadata (nullable, reserved) |
| `agent_registry` | Agent identity + trust data | agent_name (UNIQUE), version, author, capabilities (JSON), token_hash (UNIQUE), registration_time, last_seen, total_queries, incidents, trust_metadata (JSON nullable), deregistered_at |
| `incident_reports` | Third-party incident filings | agent_id FK, agent_name, reporter, incident_type, description, timestamp, status (pending/accepted/rejected/duplicate), severity (critical/standard), reviewed_at, duplicate_of |
| `events` | Immutable event log | event_type, data (JSON), privacy_mode_active |
| `settings` | Key-value config | key, value (HMAC secret stored here) |
| `business_api_keys` | Business credentials | key_hash (UNIQUE), business_name, email, tier (free/paid), rate_limit, stripe_customer_id, is_active |
| `business_api_usage` | Hourly rate limit counters | key_hash, window_start (hour-aligned), request_count |

**DB engine:** SQLite (WAL mode). File at `prototype/submantle.db`. No Postgres, no Redis, no distributed store.

---

## 4. Authentication and Identity

**Agent tokens:** HMAC-SHA256 over `"{agent_name}:{iso_timestamp}"` using a 32-byte random server secret. Secret generated on first run, stored in `settings` table. Only the SHA-256 hash of the token is stored — raw token shown once at registration. Token verification re-derives and uses `hmac.compare_digest` (timing-safe).

**Business keys:** `sk_live_` prefix + 64 hex chars (32 random bytes). SHA-256 hash stored. Verified by hashing the presented key and looking up.

**What auth protects:**
- `DELETE /api/agents/{id}` — requires valid bearer token matching that agent_id
- `GET /api/query` — token optional; if present, `record_query()` increments trust counter
- `GET /api/verify*` — requires business context (anonymous IP rate-limited, or API key)

**What auth does NOT protect:**
- `POST /api/agents/register` — completely open, no auth, no rate limit
- `POST /api/incidents/report` — open, reporter is just a string field. No token required, no verification that reporter has any relationship with the agent.

---

## 5. Distribution Readiness

**Packaging:**
- No `setup.py`, no `pyproject.toml`, no pip package
- `prototype/requirements.txt` exists: fastapi, uvicorn, psutil, pydantic, fastapi-mcp, stripe (optional), pytest, httpx
- No Docker, no docker-compose, no Railway config in the repository
- No SDK or client library of any kind
- No npm package

**For an external agent to register today:**
```
POST http://{host}:8421/api/agents/register
Content-Type: application/json
{"agent_name": "my-agent", "version": "1.0.0", "author": "me", "capabilities": []}
```
One HTTP call. No prerequisites. Returns a bearer token. That is the entire external surface for agent onboarding.

**Discovery files present:**
- `/.well-known/agent.json` — Google A2A format agent card (localhost URL hardcoded — not production-ready)
- `/llms.txt` — llmstxt.org format, complete and accurate

**Claude Code / Agent SDK integration:** No files, no skill packaging, no `--agent` flag integration, no plugin format present in the repository. Zero Claude-Code-specific integration exists.

---

## 6. Scale Gap Analysis

### For 1,000 agents to register:
- The registration endpoint is fully open with no rate limiting — technically nothing prevents it
- SQLite WAL handles concurrent reads fine; writes serialize through SQLite locking
- The HMAC secret is a single server-side value in `settings` table — if the server restarts with a different DB, all tokens are invalidated
- **Critical gap:** No rate limiting on `POST /api/agents/register`. A single actor could register 1,000 agents in seconds with no friction.
- **Critical gap:** Agent name uniqueness is enforced, and deregistered names are permanently blocked. Namespace squatting is trivially possible.

### For 10,000 agents to register:
- SQLite becomes a bottleneck. Per-operation connections (WAL) help but are not a distributed system.
- The in-memory rate limiter cache (`rate_limiter.py`) is process-local — multiple uvicorn workers would have divergent state.
- The `business_api_usage` table for rate limiting would need pruning automation (method exists but nothing calls it).
- No horizontal scaling mechanism exists.

### What's missing for production deployment:
1. No Dockerfile or deployment config
2. `agent.json` has `localhost:8421` hardcoded — needs production URL
3. No production database (Postgres, etc.)
4. No multi-worker rate limiter synchronization
5. No registration rate limiting or Sybil prevention
6. No email verification for business registration
7. No health monitoring or alerting
8. No HTTPS configuration

### Authentication/identity gaps:
- Incident reporting requires no auth — anyone can report any agent for anything
- The VISION.md describes reporter authentication ("only registered members can file reports, must reference valid interaction ID") — this is NOT implemented. The current code accepts any string as reporter.
- W3C Verifiable Credential issuance: described in VISION.md as planned, not implemented. `submantle-decisions.md` defers this pending co-founder with cryptography expertise.

### Sybil prevention:
- **Nothing** prevents a single actor from registering thousands of fake agents. Registration is open, no CAPTCHA, no email verification, no proof of work, no IP rate limiting on the registration endpoint.
- VISION.md describes Sybil defense as "local-only trust computation" (architectural) rather than registration gates. The argument is that fake agents only affect your own device. This holds for a local-first model but breaks for a shared hosted service.

---

## 7. Existing Research Coverage

The `research/` directory contains approximately 100+ files across these expeditions:
- `expedition-submantle-deep-dive` — competitive landscape, cross-platform, ambient sensing, market/business
- `expedition-trust-layer` — historical precedents, protocol architecture, behavioral trust science, competitor analysis
- `expedition-protocol-architecture` — agent transport, agent integration, agent economy, adoption playbook, decentralized identity
- `expedition-submantle-infrastructure` — agent transport, transaction settlement, usage intelligence, protocol scale
- `expedition-mae-principles` — math/trust, structural composition, signal convergence, resilience substrate
- `expedition-trust-lifecycle` — sandbox/testing, review tiers, interaction metadata
- Multiple research councils: scoring model (x2), product-market-fit (x2)
- `triadic-build-v1-foundation` — build briefs, security/identity build, reviews

No expedition has directly addressed "free agents seed the network" strategy or agent registration at scale.

---

## 8. What the VISION.md and Decisions Say vs. What's In Code

| Vision/Decision | In Code? |
|---|---|
| Beta formula (q+1)/(q+i+2) | Yes — exact match |
| Soft/hard pull model | Yes |
| Business tiers (anon/free/paid 10/100/1000) | Yes |
| Stripe tier upgrade via webhook | Yes (lazy import) |
| MCP read-only surface | Yes |
| W3C VC / SD-JWT attestation | No — deferred |
| Reporter must be authenticated/have interaction ID | No — reporter is free-form string |
| Velocity caps (anti-gaming) | No |
| Query diversity rules (anti-gaming) | No |
| Sandbox/testing mode | No |
| Probation periods | No |
| Dispute timeout / auto-withdraw | No |
| Bidirectional trust (businesses scored too) | No — only agents have SubScores |
| Agent-to-agent trust scoring | No |

---

## 9. Summary Assessment for "Free Agents Seed the Network" Strategy

**What works today:**
- One HTTP call registers an agent. Genuinely frictionless.
- Token returned immediately, usable immediately.
- MCP surface means any MCP-compatible agent can query trust scores without writing code.
- llms.txt and agent.json discovery files are present (agent.json needs production URL).
- The trust formula is implemented and functional.

**What is broken for this strategy:**
- Registration has zero Sybil prevention. "Free agents" also means "free fake agents" — a competitor or bad actor could flood the namespace.
- Incident reporting is completely unauthenticated. The VISION claims "only registered members can file reports" — the code does not enforce this.
- No SDK, no Claude Code plugin, no automated registration path. An agent developer must write the HTTP call themselves.
- `agent.json` has `localhost:8421` hardcoded — discovery only works locally.
- SQLite is not a scale database. 10,000 agents is technically feasible; 10,000 concurrent queries is not.
- The HMAC secret in `settings` table means a DB migration or server move invalidates all agent tokens.

**The one structural risk to the strategy:**
Namespace squatting is permanently consequential. Names that are registered and deregistered are BLOCKED FOREVER (`ValueError: Agent name '...' was previously registered and deregistered. Names are permanent records and cannot be reused.`). With open registration and no rate limiting, a bad actor could poison the namespace for well-known agent names (e.g., "claude-code", "cursor", "copilot") before legitimate registrations occur.

---

*Source files verified:*
- `/prototype/api.py`
- `/prototype/agent_registry.py`
- `/prototype/business_registry.py`
- `/prototype/database.py`
- `/prototype/rate_limiter.py`
- `/prototype/requirements.txt`
- `/prototype/.well-known/agent.json`
- `/prototype/llms.txt`
- `/VISION.md`
- `/BUILD-NEXT.md`
- `/submantle-decisions.md`
