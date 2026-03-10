# Build Report: Integration — Round 2
**Date:** 2026-03-10
**Builder:** Integration (Opus 4.6 / claude-sonnet-4-6)
**Tasks:** 5 (scan_with_events), 6 (api.py), 7 (dashboard privacy toggle), 8 (housekeeping)
**Status:** COMPLETE — 160/160 tests passing

---

## What Was Built

### Task 5: `scan_with_events` in `prototype/substrate.py`

New function added. Existing functions untouched — zero regressions.

**What it does:**
- Privacy gate first: `if privacy_manager.check_privacy(): return []`
- Calls existing `scan_processes(signatures)`
- Diffs against `previous_processes` using PID sets to find new/dead processes
- Emits `PROCESS_STARTED` for each new PID, `PROCESS_DIED` for each dead PID
- Emits `SCAN_COMPLETE` with `{process_count, identified_count}` summary
- Returns the current process list for the caller to pass as `previous_processes` on the next call

**Key decisions:**

1. **`previous_processes=None` vs `[]` semantics.** When `None`, no diff is computed and no lifecycle events are emitted — useful when the caller doesn't have a prior baseline. When `[]`, diffs are computed and every currently-running process looks "new". The API uses `None` implicitly on first call, which avoids a flood of PROCESS_STARTED events on server startup. This was not specified in the brief but is the correct behaviour.

2. **PID-based diffing.** Processes are identified by PID for the diff. PIDs can be recycled by the OS, but at the 5-second scan interval the probability of a PID collision (process died AND same PID assigned to a new process within the window) is negligibly low for a prototype. The brief did not ask for process fingerprinting.

3. **Returns empty list in PRIVATE mode.** The caller (`_get_state` in api.py) is responsible for deciding whether to baseline `_previous_processes` when coming out of PRIVATE mode. Currently it does not — on the first scan after PRIVATE mode ends, `_previous_processes` is still the last pre-private list, so diffs will correctly detect what changed during the private window. This is intentional: the system "wakes up" knowing what changed.

4. **Removed unused `os` import from substrate.py.** The `os` module was imported but never used. Also removed JSON state file writing from `main()`.

---

### Task 6: `prototype/api.py` — Full module wiring

Complete rewrite of api.py. All existing endpoints preserved with identical behaviour when in AWARE mode.

**Module initialization order (critical):**
```python
_db      = SubstrateDB()
_bus     = EventBus(db=_db)
_privacy = PrivacyManager(db=_db, event_bus=_bus)
_registry = AgentRegistry(db=_db, event_bus=_bus)
```
This order matches the dependency graph: DB must exist before bus (for persistence), privacy and registry both need both.

**Privacy integration in existing endpoints:**

- `GET /api/status` — when `_privacy.check_privacy()` is True, returns `{"privacy_mode": True, "status": "<message>"}` instead of process data
- `GET /api/query` — returns HTTP 403 with `{"error": "...", "privacy_mode": True}` when PRIVATE

**New endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/privacy/toggle` | POST | Toggle AWARE/PRIVATE. Invalidates scan cache. Returns `{previous_state, new_state, changed, is_private}` |
| `/api/privacy/status` | GET | Returns `{state, is_private}` |
| `/api/agents/register` | POST | Accepts `{agent_name, version, author, capabilities}`, returns `{token, agent_name}` |
| `/api/agents` | GET | Returns `{agents: [...]}` — token_hash excluded |
| `/api/agents/{agent_id}` | DELETE | Requires `Authorization: Bearer <token>`. Verifies token belongs to the agent_id being deleted. |

**Cache invalidation on privacy toggle:** When the user toggles privacy mode, `_cache` and `_cache_ts` are reset. This ensures the next `/api/status` call reflects the mode change immediately, rather than serving a 5-second-stale process snapshot in AWARE→PRIVATE transitions (which would be confusing — the user just asked for no monitoring, but old data appears briefly).

**SQLite-backed state:** After each scan, `_db.save_scan_snapshot(data={"report": report}, ...)` is called. On server restart, `_db.get_latest_scan()` could be used to serve a "last known state" without waiting for the first scan cycle to complete. This is a natural extension; the wiring is there.

**CORS updated:** `allow_methods` now includes `"POST"` and `"DELETE"` in addition to `"GET"`.

**DELETE /api/agents/{agent_id} — ownership check:** The endpoint extracts the token from `Authorization: Bearer`, verifies it, confirms the verified agent's `id` matches the URL `agent_id`, then calls `registry.deregister(token)`. This prevents one agent from deleting another agent's registration.

**Key decisions:**

1. **`_previous_processes` module-level global.** The scan diff needs to persist across API calls but not across server restarts. A module-level variable is the correct scope — it lives as long as the server process, which is exactly what we want.

2. **Non-fatal DB write in `_get_state`.** The `save_scan_snapshot` call is wrapped in a try/except that silently continues. The system must never stop serving `/api/status` because a DB write failed. The event bus already logs SCAN_COMPLETE; the snapshot is a redundant persistence.

3. **Pydantic model for register request.** `AgentRegisterRequest` uses Pydantic, which FastAPI validates automatically. Malformed requests (missing fields, wrong types) get a 422 from FastAPI before the endpoint code runs.

4. **`struct` and `json` imports removed.** Neither was used in the new version — `json` was only used by the old in-memory cache serialization, and `struct` was never used.

---

### Task 7: Dashboard privacy toggle

Added to `prototype/dashboard.html`. The existing visual design language (warm slate palette, clay accent #d97757, Inter + JetBrains Mono) is fully preserved.

**What was added:**

1. **CSS:** `.privacy-toggle-wrap`, `.privacy-switch`, `.privacy-track`, `.privacy-label` — a native-feeling toggle switch. Active (PRIVATE) state uses amber (`#eab308`) rather than clay, because amber reads as "warning/caution" which is the correct emotional register for privacy mode. Using clay would be ambiguous — it's the brand colour, not a warning colour.

2. **CSS:** `.privacy-overlay` — a card-sized block shown in place of the process sections when PRIVATE. Shows a lock emoji, "Substrate is not watching", and a description.

3. **HTML topbar:** The toggle sits between `.scan-age` and `.theme-toggle` in the topbar, clearly visible without crowding the brand identity.

4. **JavaScript:**
   - `loadPrivacyStatus()` — called on page load, syncs UI to server state before first `pollStatus()` call
   - `applyPrivacyUI(isPrivate)` — single function that drives all visual state changes: checkbox, label, overlay, process/query section visibility, stat strip opacity, query input disabled state, pulse animation
   - `privacyCheckbox` change handler — optimistic UI update (immediate visual feedback), then POST to `/api/privacy/toggle`, revert on error
   - `pollStatus()` updated — if `/api/status` returns `privacy_mode: true`, calls `applyPrivacyUI(true)` instead of rendering process data

**Key decisions:**

1. **Amber, not clay.** Privacy mode is a warning state. Amber is semantically "caution/stop" in most design systems. Clay is the Substrate brand accent — using it for privacy mode would blur the distinction between "alive and watching" and "stopped watching."

2. **Optimistic UI.** The toggle responds instantly to the click rather than waiting for the server round-trip. This is standard UX for toggle switches. If the server rejects the toggle, the UI reverts.

3. **`privacyToggling` flag.** Prevents double-click from sending two toggle requests, which would leave the server in the opposite state from the user's intent.

4. **`pollStatus()` guards against privacy_mode response.** Without this guard, `renderStatus(data)` would crash trying to access `data.total_processes` on a privacy stub response.

---

### Task 8: Housekeeping

- `.gitignore` already contains `prototype/substrate.db`, `prototype/substrate.db-wal`, `prototype/substrate.db-shm`, and `prototype/substrate_state.json` — Builder A handled this in Round 1. Confirmed present. No change needed.
- Removed JSON state file writing from `substrate.py main()` — replaced with a comment explaining the new persistence path.
- Removed unused `os` import from `substrate.py`.
- No references to `substrate_state.json` existed in `api.py`.

---

### Bug Fixed (not in task scope, but correctness requires it)

**`agent_registry.py` called `self._db.delete_agent()` but `database.py` exposes `deregister_agent()`.**

The test mock used `delete_agent` (matching the broken call), so Round 1 tests passed despite the mismatch. At runtime against the real `SubstrateDB`, `deregister()` would always fail with `AttributeError`. Fixed by:
1. Changing `agent_registry.py` to call `self._db.deregister_agent(agent_id)`
2. Renaming `MockDB.delete_agent` to `MockDB.deregister_agent` in `tests/test_agent_registry.py`

This is the correct fix — the real DB interface is the source of truth. Mocks must match the real interface.

---

## Files Modified

| File | Action | Key changes |
|------|--------|-------------|
| `prototype/substrate.py` | MODIFIED | Added `scan_with_events()`, removed JSON state write from `main()`, removed unused `os` import |
| `prototype/api.py` | REWRITTEN | Wired all 4 modules, added 5 new endpoints, privacy integration in existing endpoints, SQLite-backed scan persistence, CORS POST/DELETE |
| `prototype/dashboard.html` | MODIFIED | Privacy toggle in topbar, privacy overlay, full JS privacy state management, pollStatus guard |
| `prototype/agent_registry.py` | BUG FIX | `delete_agent` → `deregister_agent` (call matches real DB interface) |
| `prototype/tests/test_agent_registry.py` | BUG FIX | `MockDB.delete_agent` → `MockDB.deregister_agent` (mock matches real interface) |
| `.gitignore` | VERIFIED | Already correct — no changes made |

---

## Test Results

```
160 passed in 0.36s
```

All 160 tests pass. No regressions. The 4 failures that appeared on first run were caused by the `delete_agent` / `deregister_agent` mismatch — fixed and verified.

---

## Verification Commands (all passing)

```
cd prototype && python -c "from substrate import scan_with_events; print('OK')"
# → substrate OK

cd prototype && python -c "from api import app; print('API OK')"
# → API OK

cd prototype && python -m pytest tests/ -v
# → 160 passed in 0.36s
```

---

## Notes for Reviewers

1. **Interface mismatch between agent_registry.py and database.py** was a pre-existing bug from Round 1 that only manifested at runtime (the mock shielded it from tests). Fix is clean and correct — see Bug Fixed section above.

2. **Privacy mode UX intentionally uses amber, not clay.** Clay is the brand accent. Amber reads as warning. The toggle state colour matters for the product trust story.

3. **Scan cache invalidation on privacy toggle** is important for UX correctness. Without it, there's a 5-second window after toggling PRIVATE where stale process data could still appear.

4. **`_previous_processes` baseline on PRIVATE exit** is intentional. When the user comes out of PRIVATE mode, the first diff is against the pre-private process list, which means the system correctly reports what changed during the private window. An alternative design would be to baseline to `None` on PRIVATE entry (causing no events on the first post-private scan), but that loses the "what changed while I wasn't watching" signal.

5. **DELETE endpoint ownership check** uses a two-step verify: `registry.verify(token)` to get the agent record, then `agent_info["id"] != agent_id` to confirm the token belongs to the requested agent. This is intentional — `registry.deregister(token)` deregisters by token, not by ID. The URL `agent_id` is only used for the ownership guard.
