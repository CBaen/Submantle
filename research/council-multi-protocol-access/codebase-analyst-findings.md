# Codebase Analyst Findings: Multi-Protocol Access Strategy
## Date: 2026-03-12
## Project: Submantle
## Role: Codebase Analyst

---

## Summary

The codebase has a natural, already-separated service layer hiding inside `agent_registry.py` and `database.py`. The REST API in `api.py` is a thin adapter over that core — it handles HTTP transport, auth extraction, request parsing, and routing, then delegates immediately to the registry and privacy manager. This means MCP and CLI adapters can be added with near-zero disruption to business logic. However, the current module initialization pattern (singletons in `api.py` global scope) is the one structural choice that would require careful handling for multi-process or multi-entry-point deployments. The "exchange hub" concept is architecturally compatible with the codebase as long as it is defined as "the same data, multiple transports" rather than "a routing layer between agents and brands."

---

## Step 2: File-by-File Analysis

### `prototype/api.py` — The HTTP Transport Adapter

**What it does:** FastAPI application that exposes 13 HTTP endpoints, instantiates all core services (DB, bus, privacy, registry) as module-level singletons, and handles HTTP-specific concerns (headers, status codes, CORS, JSON serialization).

**What depends on it:** The web dashboard (`dashboard.html`), any external HTTP client, and the uvicorn process launcher. Nothing in the codebase imports from `api.py` — it is a leaf node.

**What it depends on:** All four core modules (`database.py`, `events.py`, `privacy.py`, `agent_registry.py`) plus `submantle.py` for process awareness. Also FastAPI, pydantic, psutil, socket, subprocess, pathlib.

**Key patterns it establishes:**

1. **Module initialization order** (`api.py` lines 44–47): `SubmantleDB → EventBus → PrivacyManager → AgentRegistry`. This order is documented as critical and must be preserved by any alternative entry point. A CLI or MCP server that instantiates the same four objects must follow the same sequence.

2. **Thin delegation pattern**: Every endpoint is 5–15 lines. The endpoint validates HTTP-layer concerns (Authorization header format, required body fields), then calls exactly one registry or privacy method. No business logic lives in the route handlers. For example, `verify_agent()` (lines 547–561) is six lines: look up by name, 404 if None, return the result. The trust computation itself lives in `agent_registry.py`.

3. **Token extraction helper** (`_extract_token()`, lines 339–343): The auth pattern is three lines of string manipulation. It is not middleware; it is called inline in routes that need it. This is important: auth is not enforced globally — it is opt-in per route. Score queries (`/api/verify/{agent_name}`) have no auth at all.

4. **Privacy gate placement**: Privacy is checked in route handlers before touching process data, not in middleware. `_get_state()` (line 80) checks privacy mode; `/api/query` checks it at line 389. This gate lives in `api.py`, not in the core modules. A protocol adapter must replicate this gate pattern or extract it.

5. **5-second scan cache**: The `_cache`, `_cache_ts`, `_previous_processes` module-level globals (lines 64–67) are used by `_get_state()`. This cache is specific to the HTTP server process. A second process (MCP server running in a separate process) would not share this cache and would re-scan on its own cadence. That is acceptable — the database is the shared source of truth.

**Endpoint inventory (13 endpoints):**

| Endpoint | Auth | Business Logic Owner |
|---|---|---|
| `GET /api/health` | None | Inline (trivial) |
| `GET /api/status` | None | `_get_state()` → `submantle.py` |
| `GET /api/query` | Optional Bearer (accumulates queries) | `agent_registry.record_query()`, `submantle.query_what_would_break()` |
| `GET /api/devices` | None | Inline (`_discover_devices()`) |
| `POST /api/privacy/toggle` | None | `privacy.toggle()` |
| `GET /api/privacy/status` | None | `privacy.state` |
| `POST /api/agents/register` | None | `agent_registry.register()` |
| `GET /api/agents` | None | `agent_registry.list_agents()` |
| `DELETE /api/agents/{agent_id}` | Required Bearer | `agent_registry.verify()`, `agent_registry.deregister()` |
| `GET /api/verify` | None | `agent_registry.list_agents()`, `agent_registry.compute_trust()` |
| `GET /api/verify/{agent_name}` | None | `agent_registry.compute_trust()` |
| `POST /api/incidents/report` | None | `agent_registry.record_incident()` |
| `GET /` | None | Static file (dashboard.html) |

**Auth architecture observation**: There are effectively two doors, exactly as the brief states. Door 1 (agent operations) uses HMAC bearer tokens. Door 2 (score queries) has no auth today. The business API keys for billing would add a third tier, but there is no existing hook point for it — a future middleware or per-route API key check would need to be added.

---

### `prototype/agent_registry.py` — The Actual Service Layer

**What it does:** Manages agent lifecycle (register, verify, deregister), computes trust scores (Beta Reputation formula), records queries and incidents, and enforces business rules (name uniqueness, self-ping rejection, deduplication).

**What depends on it:** `api.py` imports `AgentRegistry` directly. Tests import it directly. Nothing else.

**What it depends on:** `database.py` (via injected `_db` parameter) and `events.py` (via injected `_event_bus` parameter). No FastAPI, no HTTP, no pydantic. It is protocol-agnostic today.

**This is the natural service layer.** The public methods of `AgentRegistry` — `register()`, `verify()`, `compute_trust()`, `record_query()`, `record_incident()`, `list_agents()`, `deregister()`, `review_incident()` — are the complete API surface that any protocol adapter needs. A MCP server would call these methods directly. A CLI would call these methods directly. No translation layer is needed because there is no HTTP coupling in this class.

**Dependency injection pattern**: Both `db` and `event_bus` are injected at construction time (lines 72–83). This means `AgentRegistry` can be instantiated in a test with no external dependencies (both default to None, triggering safe no-op paths). This pattern ports trivially to any entry point: the MCP server instantiates `SubmantleDB`, `EventBus`, `PrivacyManager`, and `AgentRegistry` in the same order as `api.py` does.

**Trust formula location**: The Beta Reputation formula lives at lines 372–433. It reads `total_queries` from the agent record and calls `self._db.get_accepted_incident_count()` for incident data. This is entirely within `agent_registry.py`. No protocol adapter touches the formula or its data sources. The formula is safe from protocol layer changes.

---

### `prototype/database.py` — The Shared State Store

**What it does:** SQLite persistence layer with five logical sections: scan snapshots, agent registry, incident reports, events, and settings. All state that must survive a restart lives here.

**What depends on it:** `api.py` (indirectly through the objects it constructs), `agent_registry.py`, `events.py`, `privacy.py`, all test files.

**What it depends on:** Only Python stdlib (`json`, `sqlite3`, `time`, `contextlib`, `pathlib`). Zero external dependencies.

**Key architectural property for multi-protocol**: The database file path defaults to `prototype/submantle.db` (line 32). Any process on the same machine that instantiates `SubmantleDB()` with the same path will connect to the same database. SQLite WAL mode (line 118) allows concurrent reads and serializes writes. This means a MCP server process and the REST API server process can both read and write the same database safely, without any shared-memory coordination. This is the "shared state" that makes multi-protocol access coherent.

**Schema coverage**: The `agent_registry` table holds all trust data (lines 644–665). The `incident_reports` table holds all incident records (lines 668–681). These are the two tables that matter for cross-protocol consistency. The `events` table is append-only and used for internal pub/sub logging — not a concern for protocol adapters.

**Migration pattern** (lines 121–136): Schema migrations are handled inline in `_initialize()` via try/except `ALTER TABLE`. This is a known prototype pattern. For production Go rewrite, this will need proper versioned migrations. For the prototype, it is safe — adding columns with defaults is non-destructive.

---

### `prototype/events.py` — Internal Pub/Sub

**What it does:** Synchronous in-memory pub/sub event bus with SQLite persistence. Routes events to subscribers and logs them to the `events` table.

**What depends on it:** `api.py` constructs `EventBus`, `agent_registry.py` emits events through it, `privacy.py` manages its privacy filter. Tests import it directly.

**What it depends on:** Only Python stdlib. No external dependencies.

**Multi-protocol relevance**: The event bus is an in-process pub/sub system. If MCP and REST API run as separate processes (which they likely would — uvicorn for REST, `python mcp_server.py` for MCP), each process would have its own `EventBus` instance. Events would not propagate across the process boundary. This is acceptable for V1 — events are for internal coordination (privacy filter sync, audit log). Cross-process event propagation would require a message queue or shared SQLite polling, which is out of scope.

**MCP stream note**: `privacy.py` line 212 already anticipates the MCP connection: "the bus stays in AWARE mode and process events leak through to subscribers (including the future MCP stream)." This shows the architecture was written with MCP in mind, but the event bus itself doesn't provide streaming — it only calls synchronous callbacks. An MCP server wanting to stream events would need to poll or subscribe and buffer.

**Privacy enforcement**: The bus enforces privacy mode filtering (lines 251–252). When `_privacy_mode=True`, process events (`PROCESS_STARTED`, `PROCESS_DIED`, `SCAN_COMPLETE`) are dropped before reaching any subscriber. Agent and trust events pass through. This filter must be active in any process that touches privacy-sensitive data.

---

### `prototype/privacy.py` — Privacy Gate

**What it does:** Manages the AWARE/PRIVATE state machine, persists state to SQLite settings, emits `PRIVACY_TOGGLED` events, and provides `check_privacy()` as the gate for all sensitive operations.

**What depends on it:** `api.py` constructs `PrivacyManager` and calls `check_privacy()` before process scans and queries.

**What it depends on:** `database.py` and `events.py` (both injected). Threading lock for state safety.

**Multi-protocol relevance**: Privacy state is persisted to the `settings` table with key `privacy_mode`. Because state lives in SQLite, all processes reading from the same database file will see the correct privacy state. However, each process maintains its own `PrivacyManager` instance — toggling privacy via REST API does not update the `EventBus` in the MCP server process. The MCP server would need to poll `PrivacyManager.check_privacy()` on each operation (which re-reads from `_state`, an in-memory mirror). To keep the in-memory state current across processes, each process's `PrivacyManager` would need to re-read the DB setting before gating — or the toggle endpoint would need to signal the MCP process (not currently implemented).

**Practical implication**: For V1, a simple solution is for every MCP tool handler to call `privacy_manager.check_privacy()` which reads the in-memory state. On startup, the MCP server loads state from DB. If REST API toggles privacy, the MCP server's in-memory state goes stale until it restarts. This is an acceptable V1 limitation — privacy mode is rarely toggled, and the MCP server can offer its own toggle command.

---

### `prototype/submantle.py` — Process Awareness Layer

**What it does:** Scans running processes using psutil, matches them against signatures, builds process trees, generates awareness reports, and answers "what would break" queries.

**What depends on it:** `api.py` imports five functions from it. Nothing else.

**What it depends on:** psutil, json, time, pathlib, collections. The signatures file at `prototype/signatures.json`.

**Multi-protocol relevance**: The awareness layer (process scanning) is relevant only for the process-query use case. The trust bureau operations (register, verify, compute_trust, report_incident) do not touch this module at all. An MCP server focused on trust score queries would not need to import `submantle.py` at all. A CLI doing process awareness queries would need it.

---

## Step 3: Blast Radius Mapping

### Protocol Adapter 1: MCP Server (Wave 5)

**Files that need to change:** Zero existing files need to change. A new `prototype/mcp_server.py` file would:
- Import and instantiate `SubmantleDB`, `EventBus`, `PrivacyManager`, `AgentRegistry` (same initialization sequence as `api.py` lines 44–47)
- Expose MCP tools by calling `AgentRegistry` methods directly
- Handle its own stdio transport layer

**Files that would NOT change:** `database.py`, `agent_registry.py`, `events.py`, `privacy.py`, `submantle.py`. None of the core business logic modules need modification.

**Tests that could break:** None — existing tests test the core modules directly, not through `api.py`. New MCP tests would be additive.

**Conventions that need updating:** `api.py` module initialization comment (line 7–12) should become a shared reference, or duplicated in `mcp_server.py` with a note pointing back. The critical initialization order needs to be documented as a shared invariant, not an `api.py`-specific concern.

**Blast radius: Minimal.** One new file. Zero changes to existing files.

---

### Protocol Adapter 2: CLI Tool

**Files that need to change:** Zero existing files need to change. A new `prototype/cli.py` (or a top-level `cmd/submantle.py`) would follow the same instantiation pattern and call `AgentRegistry` methods.

**Practical consideration**: The CLI would likely target read-only operations (look up a score, list agents, check status) and write operations (register an agent, report an incident). The same `AgentRegistry` public API covers all of this. The only CLI-specific concern is output formatting (human-readable vs. JSON), which is purely in the CLI layer.

**Blast radius: Minimal.** One new file.

---

### Protocol Adapter 3: Business API Keys (Wave 11)

**Files that need to change:** `api.py` needs a new authentication layer for business clients hitting score-query endpoints. The current `_extract_token()` helper handles agent bearer tokens. Business API keys would require a different credential type — either a separate lookup table or a distinguishable token prefix.

**What would need to be added:**
- A new `business_api_keys` table in `database.py` (or a new `settings` entry for a simple single-key proof of concept)
- A new `_verify_business_key()` function in `api.py` (analogous to `_extract_token()`)
- Applied to `/api/verify` and `/api/verify/{agent_name}` endpoints

**No changes needed to:** `agent_registry.py`, `events.py`, `privacy.py`, `submantle.py`, any tests.

**Blast radius: Targeted.** `database.py` (new table) + `api.py` (new auth check on 2 routes). The trust formula and core business logic are untouched.

---

### The "Exchange Hub" Concept

**What it would mean architecturally**: A routing layer where agents connect to Submantle (via any protocol) and brands query it (via any protocol), with Submantle as the mediating exchange.

**What it would require**: A stateful session layer, routing logic between participants, possibly message brokering. Submantle would become a participant in the interaction, not just a lookup service.

**Blast radius against current architecture: Significant, and violates "always aware, never acting."** The current architecture is a pure lookup service — agents register, third parties report, businesses query. There is no session concept, no routing, no mediation. Adding exchange hub semantics would require introducing:
- Session management (no mechanism exists)
- Participant-to-participant routing (not a pattern anywhere in the codebase)
- Submantle taking action based on queries (currently prohibited by design principle 4)

The "exchange hub" vision is safe only if interpreted as "the same data is accessible via multiple protocols." The underlying `AgentRegistry` already supports this — any protocol that can call `compute_trust()` can serve as an access point to the trust data. The data is shared (SQLite file); the transports are independent.

---

## Step 4: Pattern Inventory

### Pattern 1: Dependency Injection for Service Objects
All core service objects (`SubmantleDB`, `EventBus`, `PrivacyManager`, `AgentRegistry`) accept their dependencies as constructor parameters. This is applied consistently in `agent_registry.py` (lines 72–83), `events.py` (line 133), and `privacy.py` (lines 52–68). Any new protocol adapter must follow this pattern: instantiate DB, inject into bus, inject both into privacy manager, inject both into registry.

### Pattern 2: Privacy Gate Before Sensitive Operations
Process data is privacy-gated at the point of use, not globally. Routes that return process data call `_privacy.check_privacy()` before accessing `_get_state()`. The pattern is: `if _privacy.check_privacy(): return 403`. Protocol adapters must replicate this gate — it cannot be assumed to be handled elsewhere.

### Pattern 3: Bearer Token Auth as Optional Enhancement
Token auth is not globally enforced. `/api/query` accepts optional auth (token presence records the query for trust accumulation, absence still works). Only destructive operations (`DELETE /api/agents/{id}`) require auth. This asymmetric auth pattern — open reads, gated writes, optional-but-beneficial tokens — should be preserved across protocols.

### Pattern 4: Business Logic Does Not Know About Transport
`agent_registry.py` has zero HTTP imports. It raises Python exceptions (`ValueError`, `RuntimeError`) not HTTP exceptions. The `api.py` layer catches these and maps them to HTTP status codes. An MCP adapter would map the same exceptions to MCP error responses. A CLI adapter would map them to exit codes and stderr messages.

### Pattern 5: Initialization Order Is a First-Class Concern
The comment in `api.py` lines 6–12 treats the initialization order as a critical invariant. This is not just documentation — if `AgentRegistry` is instantiated before `SubmantleDB`, the HMAC secret lookup fails. Any new entry point must preserve this order. This pattern is currently documented only in `api.py`. For a multi-entry-point architecture, it should live in a shared initialization module or at minimum be documented in each entry point that replicates it.

### Pattern 6: Auth Token Is Agent-Scoped, Not Business-Scoped
The HMAC token system identifies agents, not businesses. A business querying `/api/verify/{agent_name}` today is anonymous. The future business API key system will be a new, separate credential type. These two auth systems must not be conflated — agent tokens (for agents reporting their own queries) and business keys (for businesses purchasing score lookups) serve different roles and should remain distinct.

---

## Step 5: Scores

### Role-Specific Dimensions

| Dimension | Score | Justification |
|-----------|-------|---------------|
| **Feasibility** | 9 | The service layer (AgentRegistry) is already protocol-agnostic. Adding MCP or CLI requires one new file each with no changes to core modules, verified by tracing all 13 endpoint implementations. |
| **Blast Radius** | 9 | MCP and CLI adapters are additive — zero changes to `database.py`, `agent_registry.py`, `events.py`, `privacy.py`. Business API keys touch only `api.py` + a new DB table. Score: 9 (minimal) for MCP/CLI, 7 for business keys. Using 9 as the MCP case since that is Wave 5. |
| **Pattern Consistency** | 9 | The dependency injection pattern, privacy gate pattern, and thin-adapter pattern in `api.py` give a clear template. A new MCP entry point that replicates the four-line initialization sequence and delegates to `AgentRegistry` is perfectly consistent with existing conventions. |
| **Dependency Risk** | 9 | No upstream dependencies need to change. No downstream consumers are affected. The SQLite file is the shared state — WAL mode already handles concurrent access. The one risk is the single-file cache in `api.py` which is process-local, but that is not shared state and does not create cross-process inconsistency. |

### Shared Dimensions

| Dimension | Score | Justification |
|-----------|-------|---------------|
| **Overall Risk** | 9 | The core business logic is already decoupled from the transport layer. Multi-protocol access is adding new files, not modifying load-bearing ones. The main risk is the initialization order invariant being missed in a new entry point, but this is documented and easily caught in testing. |
| **Reversibility** | 10 | New protocol adapters are additive. If MCP proves unusable, delete `mcp_server.py`. Nothing else changes. No schema migrations. No changes to existing files. |
| **Evidence Confidence** | 10 | All claims are grounded in specific line numbers across the five files. The dependency chain was verified: `api.py` imports are at lines 26–37, `agent_registry.py` imports are at lines 37–46 (no HTTP imports), `database.py` has no external dependencies at all. No speculative claims are made. |

**Overall Internal Confidence: 9/10** — The codebase is structurally ready for multi-protocol access today. The natural service layer exists and is protocol-agnostic. The one complexity worth managing is the privacy state cross-process propagation issue, which is V1-acceptable but documented here for awareness.

---

## Key Findings for the Council

1. **The service layer exists and is clean.** `AgentRegistry` in `agent_registry.py` is already a protocol-agnostic service object. Any new protocol adapter calls the same eight methods. This was built correctly from the start.

2. **MCP server = one new file, zero changes to existing code.** The initialization pattern in `api.py` lines 44–47 is the complete recipe. A `mcp_server.py` that follows it and wraps `AgentRegistry` methods as MCP tools is a 100–150 line file.

3. **The "exchange hub" is safe only as "same data, multiple transports."** The current architecture has no routing, no session management, and no mediation. The data (SQLite) is the hub. The protocols are independent readers of that data. Any "exchange hub" framing that implies Submantle routing messages between agents and brands would require a fundamental architectural change and would violate "always aware, never acting."

4. **Business API keys are the gating mechanism that matters.** The trust score endpoint (`/api/verify/{agent_name}`) is currently open. All three protocols (REST, MCP, CLI) would need to enforce the same access model once monetization begins. The most natural home for this enforcement is at the transport layer (a check in each protocol adapter), not in `AgentRegistry` — because the registry doesn't know what kind of caller it is serving.

5. **Privacy state cross-process propagation is a V1 gap.** If REST API and MCP server run as separate processes, toggling privacy via REST does not immediately update the MCP server's in-memory state. Each process loads state from DB on startup. This is acceptable for V1 given that privacy mode changes are infrequent, but should be documented as a known limitation.

6. **Auth architecture for multiple protocols: keep two doors separate.** Agent bearer tokens (HMAC, for agents recording their own activity) and business API keys (future, for businesses paying to query scores) are structurally different. They should not be unified into a single auth mechanism. Each protocol adapter should support both independently.
