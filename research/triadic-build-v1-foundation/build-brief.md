# Build Brief: Substrate V1 Foundation
## Date: 2026-03-10
## Project: Substrate
## Source: Fresh-eyes audit + expedition synthesis + Guiding Light product direction

### Goal
Build the invisible groundwork for Substrate V1: privacy mode, SQLite persistence, an internal event bus, and agent identity registration. These four components are the foundation that the MCP server, ambient awareness stream, and polished dashboard will build on in subsequent rounds.

### Existing Code (all in prototype/)
- `substrate.py` (238 lines) — process scanning, signature matching, process tree, impact queries
- `api.py` (327 lines) — FastAPI server with REST endpoints, ARP device discovery
- `dashboard.html` (734 lines) — single-file Anthropic-styled frontend
- `signatures.json` (129 lines) — 15 community-curated identity signatures

### Team Size: 3 builders + 3 reviewers

**Builders:**

| Builder | Domain | Files Owned | Round |
|---------|--------|-------------|-------|
| Data & Events | prototype/database.py (new), prototype/events.py (new) | Round 1 |
| Security & Identity | prototype/privacy.py (new), prototype/agent_registry.py (new) | Round 1 |
| Integration | prototype/substrate.py, prototype/api.py, prototype/dashboard.html, .gitignore | Round 2 |

**Reviewers:** 3 independent reviewers (Phase 2, after all building completes)

### Round Structure
- **Round 1** (parallel): Data & Events + Security & Identity build new modules simultaneously. No dependencies between them.
- **Round 2** (sequential): Integration builder wires Round 1 modules into existing codebase. Depends on Round 1 interfaces.

### Build Tasks

#### Round 1 — Builder A: Data & Events

**Task 1: SQLite Persistence (prototype/database.py)**
- Replace JSON state file with SQLite using Python's built-in sqlite3
- Tables:
  - `scan_snapshots` — timestamped process scan results (id, timestamp, data JSON, process_count, identified_count)
  - `agent_registry` — registered agents (id, agent_name, version, author, capabilities JSON, token_hash, registration_time, last_seen, total_queries, incidents, trust_metadata JSON)
  - `events` — event log (id, timestamp, event_type, data JSON, privacy_mode_active BOOLEAN)
  - `settings` — key-value settings store (key TEXT PRIMARY KEY, value TEXT, updated_at)
- CRITICAL: Include nullable `analytics_metadata JSON` column on scan_snapshots for future federated analytics accommodation. This is a prerequisite architectural decision — can't retrofit later.
- Database file: prototype/substrate.db (must be gitignored)
- Provide clean Python interface: SubstrateDB class with methods for each operation
- No ORM — raw sqlite3, keep it lightweight
- WAL mode for concurrent read access

**Task 2: Event Bus (prototype/events.py)**
- Internal pub/sub system for state changes
- Event types: PROCESS_STARTED, PROCESS_DIED, SCAN_COMPLETE, PRIVACY_TOGGLED, AGENT_REGISTERED, AGENT_DEREGISTERED, RESOURCE_WARNING
- EventBus class with: subscribe(event_type, callback), unsubscribe(event_type, callback), emit(event_type, data)
- Events are also logged to SQLite events table
- Privacy mode suppresses all process-related events (only PRIVACY_TOGGLED still fires)
- Synchronous for now — design interface so asyncio upgrade is straightforward later
- Each event has: timestamp, event_type, data dict, source (which component emitted it)

#### Round 1 — Builder B: Security & Identity

**Task 3: Privacy Mode (prototype/privacy.py)**
- PrivacyManager class managing AWARE and PRIVATE states
- AWARE: normal operation
- PRIVATE: stops scanning, drops in-memory state, writes nothing to SQLite scan tables, suppresses process events
- Privacy mode still allows: health checks, agent registry queries, "Substrate is running" signals, PRIVACY_TOGGLED events
- State persisted via SQLite settings table (call database.py interface)
- Thread-safe state access (threading.Lock)
- check_privacy() method that other components call before doing sensitive work

**Task 4: Agent Identity & Registration (prototype/agent_registry.py)**
- AgentRegistry class managing agent lifecycle
- Registration requires: agent_name, version, author/publisher, capabilities list
- Substrate issues HMAC-SHA256 token using a server secret (generated on first run, stored in settings)
- Token structure: HMAC(secret, agent_name + registration_timestamp)
- Verification: agent presents token, Substrate validates via HMAC check
- Trust fields tracked: registration_time, last_seen, total_queries, incidents (schema only — scoring algorithm is future work)
- Methods: register(name, version, author, capabilities) -> token, verify(token) -> agent_info or None, list_agents(), deregister(token), record_query(token)
- Agent registry operates in both AWARE and PRIVATE modes (identity is not sensitive — activity is)
- Persists to SQLite agent_registry table

#### Round 2 — Builder C: Integration

**Task 5: Wire substrate.py to use event bus**
- Import and initialize EventBus
- Emit PROCESS_STARTED/PROCESS_DIED events when scan detects changes (compare with previous scan)
- Emit SCAN_COMPLETE after each scan
- Check privacy mode before scanning — return empty/cached results when PRIVATE
- Remove JSON state file writing (replaced by SQLite)

**Task 6: Wire api.py to use all new modules**
- Import database, events, privacy, agent_registry modules
- Initialize all modules on startup
- Check privacy mode in /api/status and /api/query endpoints — return limited response when PRIVATE
- Add endpoints: POST /api/privacy/toggle, GET /api/privacy/status
- Add endpoints: POST /api/agents/register, GET /api/agents, DELETE /api/agents/{agent_id}
- Use SQLite for state persistence instead of in-memory cache
- Keep the existing 5-second scan cache but back it with SQLite

**Task 7: Dashboard privacy toggle**
- Add a prominent privacy mode toggle to dashboard.html
- Big, visible, top of the page near the brand dot
- When PRIVATE: dashboard shows "Privacy Mode — Substrate is not watching" with reduced UI
- When toggling: immediate visual feedback, then API call
- Honest about what it does — tooltip or label explaining "Stops all monitoring. No data collected."

**Task 8: Housekeeping**
- Add substrate.db to .gitignore
- Remove substrate_state.json references from substrate.py

### Project Constraints (from CLAUDE.md)
1. Lightweight first — invisible resource usage
2. Community knowledge over AI inference — signatures, not LLMs
3. Privacy by architecture — on-device, no telemetry
4. Always aware, never acting — provides knowledge, doesn't act
5. Inner ring first — software awareness is the focus

### Destructive Boundaries
- Do NOT modify signatures.json
- Do NOT add any external network calls or telemetry
- Do NOT add LLM-based classification
- Do NOT change the dashboard's visual design language (Anthropic warm slate palette, clay accent)

### Verification Plan
- `cd prototype && python -c "from database import SubstrateDB; db = SubstrateDB(':memory:'); print('DB OK')"` — SQLite module loads
- `cd prototype && python -c "from events import EventBus; bus = EventBus(); print('Events OK')"` — Event bus loads
- `cd prototype && python -c "from privacy import PrivacyManager; print('Privacy OK')"` — Privacy module loads
- `cd prototype && python -c "from agent_registry import AgentRegistry; print('Registry OK')"` — Agent registry loads
- `cd prototype && python -m uvicorn api:app --port 8421` — Server starts without errors
- Dashboard loads at localhost:8421 with privacy toggle visible
- POST to /api/privacy/toggle returns new state
- POST to /api/agents/register with valid payload returns token
