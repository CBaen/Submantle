# Build Report: Data & Events — Round 1
**Date:** 2026-03-10
**Builder:** Data & Events (Opus 4.6)
**Status:** COMPLETE — 81/81 tests passing

---

## What Was Built

### Task 1: SQLite Persistence (`prototype/database.py`)

`SubmantleDB` class. Raw sqlite3, no ORM, WAL mode.

**Four tables:**
- `scan_snapshots` — process scan results with nullable `analytics_metadata` column
- `agent_registry` — agent registrations with trust tracking fields
- `events` — append-only event log with privacy mode flag
- `settings` — key-value store for privacy.py and agent_registry.py

**Interface summary for Integration builder (Round 2):**

```
db = SubmantleDB()              # file-backed, default path
db = SubmantleDB(':memory:')    # in-memory (tests only)

# Scans
db.save_scan_snapshot(data, process_count, identified_count)  -> int (row id)
db.get_latest_scan()                                          -> dict | None
db.get_scan_history(limit=100)                                -> list[dict]
db.prune_scan_history(keep_count=1000)                        -> int (deleted)

# Agents
db.register_agent(name, version, author, capabilities, token_hash)  -> int
db.get_agent_by_token_hash(hash)   -> dict | None
db.get_agent_by_id(id)             -> dict | None
db.list_agents()                   -> list[dict]
db.update_agent_last_seen(id)
db.increment_agent_queries(id)
db.increment_agent_incidents(id)
db.deregister_agent(id)            -> bool
db.update_trust_metadata(id, dict)

# Events
db.log_event(event_type, data, privacy_mode_active=False)  -> int
db.get_recent_events(limit=100, event_type=None)            -> list[dict]
db.prune_events(keep_count=10000)                           -> int

# Settings
db.get_setting(key, default=None)   -> Any
db.set_setting(key, value)
db.delete_setting(key)              -> bool
db.all_settings()                   -> dict[str, str]
```

**Key decisions:**

1. **analytics_metadata column is present from day one.** The build brief flagged this as a prerequisite architectural decision — it cannot be retrofitted without a schema migration on every deployed device. The column is nullable, default NULL, and currently unused. A future federated analytics module will populate it with pre-aggregated, privacy-safe statistics. The column comment in the schema explains why it exists.

2. **In-memory vs file-backed connection strategy.** SQLite `:memory:` databases are per-connection — each new connection gets a fresh empty database. The original per-operation connection pattern (open, use, close) would silently discard the schema on every operation in-memory. Fix: in-memory instances hold a single persistent connection for their lifetime. File-backed instances use per-operation connections (WAL handles concurrent access safely). This distinction is documented in the class docstring.

3. **WAL mode.** Enabled at initialization. Returns 'memory' for in-memory DBs (no-op, acceptable). For file-backed DBs, WAL allows the 5-second scan cycle to write concurrently with API read requests without locking.

4. **Token storage.** The schema stores `token_hash` (HMAC-SHA256 hex digest), not the raw token. The raw token is issued to the agent and never persisted. This is enforced by convention — the DB layer accepts whatever string is passed as `token_hash`; it is `agent_registry.py`'s responsibility to pass only the hash.

5. **Row serializers are private module-level functions.** `_row_to_scan_snapshot`, `_row_to_agent`, `_row_to_event` centralize JSON parsing so there's one place to update if the schema changes.

---

### Task 2: Event Bus (`prototype/events.py`)

`EventBus` class. Synchronous pub/sub with SQLite persistence and privacy-mode filtering.

**Interface summary for Integration builder (Round 2):**

```python
from events import EventBus, EventType, Event

bus = EventBus(db=SubmantleDB())   # with persistence
bus = EventBus()                   # without persistence (early startup)

# Subscribe
bus.subscribe(EventType.SCAN_COMPLETE, my_callback)
bus.subscribe("*", wildcard_callback)    # receives all non-suppressed events

# Unsubscribe
bus.unsubscribe(EventType.SCAN_COMPLETE, my_callback)   # returns bool

# Emit
event = bus.emit(EventType.SCAN_COMPLETE, {"process_count": 42}, source="substrate")
# Returns Event or None (None = suppressed by privacy mode)

# Privacy mode
bus.set_privacy_mode(True)    # suppress process events
bus.set_privacy_mode(False)   # restore
bool(bus.privacy_mode)        # current state
```

**Privacy suppression rules:**

| Event | AWARE mode | PRIVATE mode |
|-------|-----------|-------------|
| PROCESS_STARTED | dispatched + logged | dropped (returns None) |
| PROCESS_DIED | dispatched + logged | dropped (returns None) |
| SCAN_COMPLETE | dispatched + logged | dropped (returns None) |
| PRIVACY_TOGGLED | dispatched + logged | dispatched + logged |
| AGENT_REGISTERED | dispatched + logged | dispatched + logged |
| AGENT_DEREGISTERED | dispatched + logged | dispatched + logged |
| RESOURCE_WARNING | dispatched + logged | dispatched + logged |

**Key decisions:**

1. **EventType.__str__ override.** Python 3.11+ changed `str(StrEnum)` to return `"ClassName.MEMBER"` instead of the value. Overriding `__str__` ensures `str(EventType.SCAN_COMPLETE)` returns `"SCAN_COMPLETE"` consistently across all Python versions, which is required for SQLite storage and JSON serialization.

2. **DB write before dispatch.** Events are persisted to SQLite before being delivered to in-memory subscribers. If the DB write fails, dispatch still proceeds — the event log is best-effort. The system must never stop functioning because a logging operation failed.

3. **Subscriber error isolation.** A crashing subscriber cannot propagate its exception to the emitter or prevent subsequent subscribers from receiving the event. Errors are silently swallowed per-callback. This is intentional: the system must be robust against buggy subscribers. Future work: route these to a structured error channel.

4. **Dispatch iterates a copy of the subscriber list.** `list(self._subscribers.get(key, []))` is used so that a subscriber that calls `unsubscribe()` during dispatch doesn't corrupt the iterator.

5. **Wildcard subscriptions.** `bus.subscribe("*", cb)` receives every event that passes privacy filtering. Useful for logging, debugging, and the future awareness stream. Wildcard delivery happens after type-specific delivery in a separate dispatch pass.

6. **Asyncio upgrade path.** The interface is designed so that making the bus async requires one change: `emit()` becomes `async def emit()` and `_dispatch()` becomes `async def _dispatch()` with `await cb(event)`. Subscribers should be written to expect this — keep callbacks fast, no blocking I/O.

7. **Privacy mode is mirrored from PrivacyManager.** The bus holds a copy of the privacy state for filtering decisions. It is not the authoritative source — `PrivacyManager.check_privacy()` (built by Security & Identity builder) is. `set_privacy_mode()` is called by PrivacyManager when the state changes.

---

## Files Created/Modified

| File | Action | Lines |
|------|--------|-------|
| `prototype/database.py` | CREATED | ~340 |
| `prototype/events.py` | CREATED | ~230 |
| `prototype/tests/__init__.py` | CREATED | 1 |
| `prototype/tests/test_database.py` | CREATED | ~250 |
| `prototype/tests/test_events.py` | CREATED | ~290 |
| `.gitignore` | MODIFIED | +3 lines |

---

## Test Results

```
81 passed in 0.17s
```

Coverage:
- `SubmantleDB`: all public methods covered, including edge cases (empty results, constraint violations, prune no-ops, timestamp updates)
- `EventBus`: subscribe/unsubscribe mechanics, all EventType privacy rules, SQLite integration, error isolation, wildcard subscriptions, data immutability

---

## Issues Found and Fixed During Build

1. **SQLite :memory: per-connection isolation.** The original per-operation `_conn()` design opened a new `:memory:` connection each call, discarding the schema. Fixed by holding a persistent connection for in-memory instances. File-backed instances unchanged.

2. **Python 3.14 str(Enum) behavior.** `str(EventType.SCAN_COMPLETE)` returns `"EventType.SCAN_COMPLETE"` in Python 3.11+, not `"SCAN_COMPLETE"`. Added `__str__` override to the enum. This is a non-obvious Python version trap — documented in both the code and this report.

---

## Notes for Integration Builder (Round 2)

- **Initialization order matters.** `SubmantleDB` must be created before `EventBus` if you want persistence. It's safe to create `EventBus(db=None)` early and call `bus._db = db` later if needed.
- **Privacy sync.** When `PrivacyManager` toggles state, it should call both `bus.set_privacy_mode(active)` AND emit `EventType.PRIVACY_TOGGLED`. The bus will allow PRIVACY_TOGGLED through regardless of mode.
- **Scan persistence.** After each `scan_processes()` call, pass the result to `db.save_scan_snapshot(data, process_count, identified_count)`. The `data` field is flexible — include whatever the API needs to reconstruct the last known state on restart.
- **Pruning.** Call `db.prune_scan_history()` and `db.prune_events()` periodically (e.g., once per hour). Default keep counts are 1000 snapshots and 10000 events — generous for a prototype, adjustable.
- **settings keys used by other modules:**
  - `privacy.py` will use key `"privacy_mode"` (value: `"true"` / `"false"`)
  - `agent_registry.py` will use key `"agent_registry_secret"` (HMAC secret)
