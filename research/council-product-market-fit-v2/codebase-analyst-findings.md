# Codebase Analyst Findings: What Can the Prototype Actually Deliver?
## Research Council: Product-Market Fit V2
## Date: 2026-03-12
## Analyst: Codebase Analyst (Sonnet 4.6)

---

## Scope

This analysis answers five questions about the working prototype today:

1. What can a business actually DO with the current API?
2. How ready is the codebase for bidirectional trust?
3. How ready is the codebase for a trust directory/marketplace?
4. What is demo readiness for each customer type?
5. What is the gap between "working prototype" and "something a customer would pay for"?

All findings are based on reading `prototype/api.py`, `prototype/agent_registry.py`, `prototype/database.py`, `prototype/events.py`, the test suite, VISION.md, HANDOFF.md, and the scoring model council synthesis.

---

## 1. What Can a Business Actually DO With the Current API?

### Complete Endpoint Inventory

The prototype exposes 11 REST endpoints. Here is what each one actually does and what a business would receive:

**`GET /api/verify`** — Public directory of all registered agents with trust scores.
- No authentication required
- No billing or rate limiting
- Returns: `{"agents": [...], "total": N}` where each agent record contains: `agent_name`, `trust_score` (float 0–1), `total_queries`, `incidents`, `registration_time`, `last_seen`, `version`, `author`
- What's missing from the response: `capabilities`, `has_history` flag, `entity_type` (agent vs business), any category or domain metadata

**`GET /api/verify/{agent_name}`** — Single agent trust score lookup.
- No authentication required
- Returns the same 8-field dict as above for one named agent
- Returns 404 if name not found
- Comment in api.py explicitly notes: "No auth required for V1 — billing comes later"
- What a business gets: a single float between 0 and 1, plus raw counts and registration metadata. That is the entire product today.

**`POST /api/incidents/report`** — Report a problem with an agent.
- No authentication required for reporters — anyone can report anyone
- Requires: `agent_name`, `reporter` (free-text string, not verified), `incident_type` (free-text string, not normalized), optional `description`
- Returns: `{"reported": true, "agent_name": "..."}`
- Critical gap: the `reporter` field is a plain text string. There is no token, no registration, no verification. A business can claim to be "Google" or "OpenAI" without any proof.

**`GET /api/agents`** — List all registered agents without trust scores.
- Returns name, version, author, capabilities, registration_time, last_seen — but NOT trust_score
- A business trying to browse agents for due diligence would get the directory without the trust data; they'd need to call `/api/verify` separately

**`GET /api/query?process=X`** — Ask "what would break if I stopped process X?"
- This is the awareness layer product, not the trust product
- Optionally accepts `Authorization: Bearer <token>` — if present, records a query against that agent's trust counter
- This is the only endpoint where authenticated agents accumulate trust score through interaction

**`POST /api/agents/register`** — Register a new agent, get a bearer token.
- Free, unauthenticated, no rate limiting
- Returns a bearer token the agent must store
- This is the supply-side onboarding

**`GET /api/status`, `GET /api/devices`, `POST /api/privacy/toggle`, `GET /api/privacy/status`, `DELETE /api/agents/{id}`** — Dashboard and management endpoints. Not business-facing.

### What the Integration Experience Actually Looks Like

If a business developer opened the Submantle API docs today and tried to integrate:

**Step 1:** Call `GET /api/verify/{agent_name}` with the name of an agent they want to evaluate.

**Step 2:** Receive a JSON response with a `trust_score` between 0 and 1. If the agent has zero history, they get `trust_score: 0.5` with `total_queries: 0` and `incidents: 0`.

**Step 3:** Decide what to do based on that score.

There is no authentication, no API key, no billing, no rate limiting, no SDK, no documentation beyond the code itself, no webhook for score changes, no batch lookup, and no filtering by capability or category.

The integration is genuinely simple — one HTTP GET, one JSON response. But "simple" is doing a lot of work here. The simplicity exists because nothing sophisticated has been built yet.

---

## 2. Bidirectional Trust Readiness

### What "Bidirectional" Requires Architecturally

For both parties in an interaction to be scored, the system needs:
- Both parties must be registered entities with IDs
- Each interaction must record which two entities were involved
- `record_query()` must accept a counterparty identifier
- Both counterparty IDs must be stored in the interaction record
- `compute_trust()` must be able to compute a score for businesses/APIs, not just agents

### Current State: Agents-Only, Unidirectional

The `agent_registry` table has one schema for all registrants: `agent_name`, `version`, `author`, `capabilities`. There is no `entity_type` field distinguishing agents from businesses from APIs.

`record_query()` in `agent_registry.py` (lines 339–361) takes only a `token` — it increments the querying entity's `total_queries` counter. There is no second-party parameter. There is no way to record "Agent A queried Business B's API."

The `incident_reports` table records `reporter` as a free-text string — not a foreign key to a registered entity. This means businesses cannot currently receive trust scores from incidents reported against them.

The `/api/query` endpoint in `api.py` (lines 380–408) is the only interaction point that triggers `record_query()`. It is an awareness query ("what processes are running") — not a trust interaction between two parties. When an agent calls `/api/query`, they accumulate queries against themselves, but the "other party" (Submantle itself) has no score and is not tracked.

### What Would Need to Change

To implement bidirectional trust, four changes are required:

**Schema change:** Add `entity_type` column to `agent_registry` (values: `agent`, `business`, `api`). Low blast radius — additive column, no migration required for existing rows if nullable or defaulted.

**Schema change:** Add `counterparty_id` column to the interaction log — but there is no interaction log table yet. Currently interactions are recorded only as an aggregate counter (`total_queries INTEGER`). Individual interaction records with two-party data don't exist in the schema. This is a new table.

**API change:** `record_query()` needs a second parameter — the counterparty's entity ID. Every call site in `api.py` must pass this. Currently there is one call site (line 402).

**New endpoints:** Businesses need a registration path (currently `POST /api/agents/register` could be reused with an `entity_type` field), and a query path that records both-party interactions.

**Assessment:** Bidirectional trust is architecturally compatible with the current codebase but is not implemented. The data model is agent-centric. A targeted build session (adding entity_type, an interaction_log table, and wiring two-party recording) could implement the foundation without breaking existing tests.

---

## 3. Trust Directory/Marketplace Readiness

### What "Trust Directory" Requires

A trust directory/marketplace needs:
- Filterable registry: find agents by category, capability, trust threshold
- Leaderboard: ranked lists by trust score
- Search: "find me a trusted agent that does X"
- Entity profiles: enough metadata for meaningful discovery

### Current State: Primitive Registry, No Discovery

`GET /api/agents` returns all registered agents with their metadata. `GET /api/verify` returns all agents with their trust scores. Both return flat lists — no filtering, no sorting, no pagination.

The `capabilities` field exists and is stored as a JSON array in the database. The `/api/agents/register` endpoint accepts `capabilities: list[str]`. However, no endpoint currently filters or searches by capability. The `GET /api/agents` endpoint returns all agents ordered by registration time only (per `database.py` line 289: `ORDER BY registration_time ASC`).

The `GET /api/verify` endpoint calls `_registry.list_agents()` then `_registry.compute_trust()` in a Python loop — N+1 query pattern. At scale this would be slow, but for a demo with handful of agents it functions.

**What exists that supports a directory:**
- `capabilities` field — data is there, query interface is not
- `author` field — could support filtering by publisher
- `registration_time` — could support "newest" sort
- `trust_score` computed in the verify endpoint — could support threshold filtering

**What does not exist:**
- Category/domain field (payments, coding, research, etc.)
- Description field (free text about what the agent does)
- Filtering parameters on any endpoint
- Sort parameters
- Pagination
- Search endpoint
- Leaderboard endpoint
- Any concept of "entity type" to separate agent leaderboards from business leaderboards

**Assessment:** The data spine for a directory is present (capabilities, author, trust score), but the query interface is entirely absent. A minimal discovery layer (filter by capability, sort by trust_score, paginate) would require new query parameters on existing endpoints and no schema changes. A richer marketplace (description, category, search) requires schema additions.

---

## 4. Demo Readiness by Customer Type

### Scenario A: A Brand Walks In Wanting to Query Trust Scores

**Experience today:**

1. They ask "can I check an agent's trust score before letting it access my API?"
2. You show them `GET /api/verify/{agent_name}` — they get a JSON response with a trust_score float.
3. They ask "what do these numbers mean?" You explain Beta Reputation — 0.5 is unknown, higher is better.
4. They ask "who are these agents?" The registry is likely empty or has test agents you created.
5. They ask "what if I want to report an agent that misbehaved?" You show them `POST /api/incidents/report`.
6. They ask "how do I know the reporter is legitimate?" You have no answer — the reporter field is a free-text string.
7. They ask "how much does this cost?" No billing exists.
8. They ask "is there an SDK?" No.
9. They ask "what's your SLA? uptime? support?" No.

**Verdict:** You can show the concept. You cannot close a paying customer. The core mechanism (query a name, get a score) is demonstrable. Everything around it that converts a demonstration into a commercial relationship is absent.

**What's missing for a paying customer:**
- API keys / authentication for business queries
- Billing and metering
- SLA or uptime guarantee
- At least a handful of real registered agents with real history
- Reporter authentication (blocks enterprise sales on security review)
- SDK or integration documentation

### Scenario B: An Agent Developer Wants to Register and Start Building Trust

**Experience today:**

1. They call `POST /api/agents/register` with `agent_name`, `version`, `author`, `capabilities`.
2. They receive a bearer token.
3. They include that token in `Authorization: Bearer <token>` headers on `GET /api/query` calls.
4. Each authenticated call increments their `total_queries` counter.
5. They can check their own score at `GET /api/verify/{their_agent_name}` — they see it rising from 0.5.
6. They ask "is there a way to build trust through interactions with other agents or businesses, not just awareness queries?" There is not. The only trust-accumulating action is querying the awareness endpoint.
7. They ask "can businesses see me in a directory?" They can see a name and score — no description, no category, no search.
8. They ask "what do I do with this token? Is there an MCP server I can point my agent to?" There is no MCP server.
9. They ask "what if someone falsely reports an incident against me?" No dispute mechanism.

**Verdict:** The registration loop works end-to-end. An agent developer can register and watch their score increment. But the REASON to register — gaining access to opportunities, being discoverable, carrying trust credentials to other platforms — does not yet exist. The value of having a score is currently theoretical.

**What's missing for an agent developer to care:**
- MCP server (the "seven lines of code" integration moment)
- Meaningful interactions beyond awareness queries (agent-to-business, agent-to-agent)
- Discoverability — a brand that actually uses Submantle scores to make decisions
- Portable credentials (W3C VC attestation is future work)
- Any incentive signal visible to the developer (no brands, no thresholds, no rewards for high scores)

---

## 5. Gap Between "Working Prototype" and "Something a Customer Would Pay For"

This is the brutal honest accounting. The prototype has a working core. What it lacks is everything that surrounds the core in a commercial product.

### What Actually Works Today (genuinely functional)

- Agent registration with cryptographic tokens (HMAC-SHA256, timing-safe verification)
- Trust score computation (Beta Reputation formula, mathematically correct)
- Incident reporting (records against named agents, decrements score)
- Score persistence across restarts (SQLite WAL)
- Public trust directory (all agents + scores, no auth required)
- Agent name uniqueness enforcement
- Privacy mode (kills process data collection, preserves trust layer)
- 160 tests covering all core logic paths

### What Is Structurally Absent (not partially built — simply not there)

| Gap | Business Impact | Effort to Fix |
|-----|-----------------|---------------|
| No authentication for business queries | Cannot charge for queries | Medium — API key system, billing integration |
| No reporter authentication | Any competitor can spam false incidents against any agent | Medium — reporter registry, tokens for reporters |
| No MCP server | The stated V1 wedge doesn't exist | Medium — Go SDK v1.4.0 available, but this is new code |
| No bidirectional scoring | The settled decision isn't reflected in the code | Medium — schema + API changes |
| No has_history flag in API responses | Cold-start agents look identical to average agents | Small — display-layer change only |
| Hard delete still in place | Reputation laundering attack is live | Small — add `agent_status` column, change DELETE to soft-delete |
| Free-text incident_type | No normalized taxonomy for severity weighting | Small — enum validation layer |
| No filtering/search on directory | Trust directory is not navigable | Medium — query parameters, no schema change |
| No agent description or category field | Directory is undiscoverable | Small schema change, bigger UX work |
| No billing | Zero revenue possible | Large — payment processor, metering, tiers |
| No SDK | Integration friction is high | Large — documentation + client library |
| No real agents in the registry | Demo has no content | Requires: dogfood agents built and running |
| CORS wildcard | Security hole for V1 | Small — lock to localhost or specific origins |
| No API endpoint tests | API behavior untested against HTTP layer | Medium — FastAPI TestClient tests |

### The Three Most Consequential Gaps

**Gap 1: No MCP Server.** The entire V1 strategy is "trust bureau + MCP server." The trust bureau exists in prototype form. The MCP server does not exist at all — not even a stub. This is the stated wedge. Without it, the only way agents interact with Submantle is a direct REST call, which requires custom integration work from every agent developer. The MCP server is the "plug in three lines and your agent has trust" moment. It is the most important missing piece for the agent-side growth flywheel.

**Gap 2: No Authenticated Business Queries.** The `/api/verify` endpoint has a comment in the source code that reads: "No auth required for V1 — billing comes later." This is honest, but it means the business model has zero technical infrastructure behind it. A business cannot be charged for queries they make unauthenticated. The Experian model requires the demand side to pay. Currently the demand side has no registration, no API key, no metering, no invoicing. The entire revenue mechanism is future work.

**Gap 3: Bidirectional Trust Is a Design Decision Reflected Nowhere in Code.** The brief says bidirectional trust is settled. The code has never heard of it. The `agent_registry` table has no `entity_type` column. There is no interaction log with two parties. Businesses cannot register through a separate business-oriented path. A business's trust score cannot be computed because there is no counterparty data. The scoring model council that preceded this research reviewed a codebase that only knew about agents. All the scoring model findings assume a world that requires new schema.

---

## Scoring the Proposal

The "proposal" being assessed is whether the current codebase can support the product-market fit vision described in the brief.

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Core Trust Mechanism Soundness | 8/10 | Formula is correct, persistence works, tokens are cryptographically sound — the engine runs |
| Business Integration Readiness | 2/10 | No auth, no billing, no SDK, no rate limiting — the commercial layer is entirely absent |
| Bidirectional Trust Readiness | 1/10 | The settled decision exists nowhere in code; schema and API are agent-only and unidirectional |
| Directory/Marketplace Readiness | 3/10 | Data spine exists (capabilities, author, score) but no query interface, no category, no search |
| Agent Developer Experience | 4/10 | Registration works end-to-end, but the reason to register (discoverability, credential portability, market access) doesn't exist yet |
| Security for Commercial Use | 2/10 | Reporter authentication is absent (critical), CORS wildcard open, no reporter verification — ship-blockers per prior council |
| Demo Completeness | 5/10 | The concept is demonstrable and the math is live, but the demo has no content (empty registry) and collapses under business questions |
| Distance to Paying Customer | 2/10 | The honest answer: the working prototype is a proof-of-concept engine. Transforming it into something a customer pays for requires the MCP server, business auth/billing, reporter authentication, bidirectional schema, and real agents in the registry — none of which exist |

---

## What the Prototype Actually Proves

The prototype proves three things that matter for a product conversation:

1. **The math works.** Beta Reputation formula is implemented, tested, and produces intuitive results. A new agent scores 0.5. Queries push it up. Incidents push it down. The formula is simple enough to explain to any business in 30 seconds.

2. **The data model is coherent.** Registration, identity, incident recording, and score computation are cleanly separated across three files. The schema is extensible — adding `entity_type`, an interaction log, and counterparty IDs would extend rather than replace what exists.

3. **The privacy architecture is sound.** The AWARE/PRIVATE toggle is real, persisted, and tested. The trust layer operates independently of the awareness layer. A business could use just the trust API without the process awareness layer — the modules are genuinely decoupled.

What the prototype does NOT prove: that businesses will pay, that agents will register, that the flywheel will start, or that anyone outside of this codebase has ever touched it. Those remain zero-validated assumptions.

---

## Dependency Map for the V1 Wedge

The stated V1 wedge is "trust bureau + MCP server." Here is what each piece of that wedge requires that doesn't yet exist:

**Trust bureau (usable by businesses):**
- Business registration path (entity_type field or separate table)
- API key issuance for business queries
- Billing/metering (external dependency: Stripe or equivalent)
- Reporter authentication (reporter_registry table or role field on agent_registry)
- has_history flag in API response (display-layer, no schema change)
- Soft-delete for deregister (agent_status column)

**MCP server (how agents connect):**
- Entire new component — zero code exists
- Go SDK v1.4.0 is available and maintained
- Needs: registration tool, trust query tool, incident report tool
- Event bus integration for real-time updates

**For the flywheel to start:**
- At least one real agent registered and interacting
- At least one business making real trust queries
- Something visible to show: a leaderboard, a real score, a real integration

The prototype is the foundation. The wedge requires building on top of that foundation, not inside it. The foundation is solid enough to build on.
