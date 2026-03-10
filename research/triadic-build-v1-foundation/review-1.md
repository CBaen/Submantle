# Review 1 — V1 Foundation Build
**Date:** 2026-03-10
**Reviewer:** Independent (claude-sonnet-4-6)
**Files reviewed:** database.py, events.py, privacy.py, agent_registry.py, substrate.py, api.py, dashboard.html, all 4 test files
**Tests run:** 160/160 passed

---

## 1. Integration Errors

### BUG-1 (MEDIUM-HIGH): EventBus privacy state is never synchronized with PrivacyManager

**Severity:** Medium-High — dormant bug with high future-risk
**File:** `privacy.py`, confirmed missing from `api.py`

The `EventBus` has a `set_privacy_mode()` method specifically designed to suppress process events when PRIVATE mode is active. The `data-events-build.md` report explicitly documented this requirement:

> "Privacy sync. When PrivacyManager toggles state, it should call both `bus.set_privacy_mode(active)` AND emit `EventType.PRIVACY_TOGGLED`."

`PrivacyManager._emit_toggle_event()` only calls `bus.emit('PRIVACY_TOGGLED', ...)`. It never calls `bus.set_privacy_mode()`. Integration Builder C did not add this call either.

**Verified by running:**
```
Bus privacy_mode before toggle: False
Bus privacy_mode after toggle to PRIVATE: False  ← should be True
Bus privacy_mode after toggle back to AWARE: False
```

**Current impact:** Dormant. The only code path that emits PROCESS_STARTED, PROCESS_DIED, or SCAN_COMPLETE is `scan_with_events()`, which is correctly gated by `pm.check_privacy()` before emitting anything. So no process data currently leaks.

**Future risk:** High. The EventBus has a well-designed privacy filter that is completely inactive. Any future code that emits process events directly on the bus (bypassing `scan_with_events`) would not be filtered. The privacy guarantee would silently fail.

**Fix:** In `privacy.py`, `_emit_toggle_event()` should call `self._event_bus.set_privacy_mode(new_state == PrivacyState.PRIVATE)` before or after calling `self._event_bus.emit(...)`. Alternatively, wire it in `api.py`'s toggle endpoint — but putting it in `PrivacyManager` is the correct location since the manager is the authoritative source.

**Why tests missed this:** `test_privacy.py` mocks the event bus as `MagicMock`. None of the 28 privacy tests assert that `bus.set_privacy_mode()` is called during a transition. The test suite verifies `bus.emit` is called but ignores the sync call entirely.

---

### BUG-2 (LOW): `scan_with_events` docstring contains a self-contradiction

**File:** `substrate.py`, lines 205–210

The docstring for `previous_processes` says:

> "Pass None (or []) on first run — every process will look 'new' but no PROCESS_STARTED events will be emitted without a baseline."

Then immediately says:

> "To emit events on the very first scan, pass an empty list explicitly."

These statements contradict each other. The code behavior is:
- `None` → diff is skipped entirely. No lifecycle events. SCAN_COMPLETE still fires.
- `[]` → diff runs. All current processes appear as new. PROCESS_STARTED fires for every running process.

The docstring's first sentence incorrectly claims `None` and `[]` behave the same way. The second sentence contradicts the first. `api.py` uses `None` correctly (no flood on startup). But the docstring will mislead future builders who read it before reading the code.

**Fix:** Rewrite the docstring. Example:
> "Pass None on first run to suppress lifecycle events on startup. Pass [] to treat all current processes as newly started (fires PROCESS_STARTED for every running process on first scan)."

---

### OBSERVATION: Double `verify()` call in DELETE endpoint

**File:** `api.py`, `agents_deregister()`
**Severity:** Performance-only (not a bug)

The DELETE endpoint calls `registry.verify(token)` to get `agent_info` for the ownership check, then calls `registry.deregister(token)` — which internally calls `verify()` again. This is 3 DB reads for one delete operation. For a prototype this is acceptable but worth flagging for when the registry has heavy traffic.

---

## 2. Constraint Violations

None found. All five project constraints are satisfied:
- Lightweight: raw sqlite3, no ORM, no heavy deps
- Signatures not LLMs: process identification unchanged
- Privacy by architecture: on-device, no new external calls
- Always aware, never acting: no action-taking added
- Inner ring first: software process focus maintained

Visual design language preserved. The amber toggle is a deliberate semantic choice (documented and justified in the integration report).

---

## 3. Bugs and Logic Errors

### BUG-3 (LOW): `applyPrivacyUI(false)` does not restore the pulse animation state

**File:** `dashboard.html`

When entering PRIVATE mode, `applyPrivacyUI(true)` calls `setAlive(false)` and sets the pulse label to "Private". When exiting PRIVATE mode, `applyPrivacyUI(false)` shows the process sections and resets the checkbox/label — but it does NOT call `setAlive(true)` or reset `pulseDetail`/`pulseTime`.

The result: after toggling back to AWARE, the pulse dot remains in its "offline" appearance until the next `pollStatus()` call fires (up to 5 seconds later). For those 5 seconds the UI shows a privacy-off state but a "stopped" pulse.

The fix is one line: add `setAlive(true)` at the top of the `else` branch in `applyPrivacyUI`. This could also reset `pulseDetail` with a "Resuming…" placeholder while waiting for the first scan.

---

### BUG-4 (LOW): `database.py` `register_agent()` computes `now` unconditionally but it is only used as `last_seen`

**File:** `database.py`, line 241

```python
now = time.time()
if registration_time is None:
    from datetime import datetime, timezone
    registration_time = datetime.now(timezone.utc).isoformat()
```

`now` is always computed (line 241) but is only used as the `last_seen` value in the INSERT. This is not a bug — `now` is used — but the placement suggests the author considered using it for `registration_time` as a fallback, then switched to ISO format. The code is correct, just slightly confusing.

---

## 4. Edge Cases

### EDGE-1: Concurrent `/api/status` calls under multi-worker deployment

**File:** `api.py`, `_get_state()`

`_cache`, `_cache_ts`, and `_previous_processes` are module-level globals with no lock. Two concurrent requests hitting a cache miss would both run `scan_with_events()`, both update `_previous_processes`, and potentially double-emit lifecycle events for the same processes.

This is acceptable for the prototype (single uvicorn worker). It is a latent issue if the server is ever deployed with `--workers > 1`, at which point each worker process has its own module state anyway (separate DBs would be needed too). Document this boundary before production.

### EDGE-2: Server restart while PRIVATE mode active

On restart, `_previous_processes` resets to `None`. The DB correctly persists PRIVATE state, so `PrivacyManager` will initialize as PRIVATE. When the user exits PRIVATE mode after a restart, the first scan will use `None` as baseline → no lifecycle events. This is the correct behavior (noted in the integration report as intentional) but worth documenting as a known startup characteristic.

### EDGE-3: HMAC token remains valid after server secret regeneration (ephemeral fallback)

If the DB is unavailable at startup, `AgentRegistry` generates an ephemeral secret and logs a warning. Any agent tokens issued during that session become invalid on the next restart if the DB comes back online (different secret loaded). Agents would need to re-register. This is documented in the warning log but there is no user-facing error — the agent simply gets a 401 on its first post-restart request. Acceptable for prototype.

---

## 5. Regression Risk

The integration builder's claim of "zero regressions to existing endpoints" holds. All existing endpoints (`/api/status`, `/api/query`, `/api/devices`, `/api/health`) are present and their behavior in AWARE mode is identical to the pre-build code. The `scan_with_events` function is additive — it wraps `scan_processes` without modifying it.

The `json` and `struct` import removals from `api.py` are correct (neither was used after the rewrite).

The `os` import removal from `substrate.py` is correct.

The `delete_agent`/`deregister_agent` mismatch bug caught and fixed by Integration Builder C was real. The fix is correct.

---

## 6. Security

**Acceptable:**
- HMAC-SHA256 for agent tokens using stdlib `hmac` + `hashlib` — correct approach
- Timing-safe comparison via `hmac.compare_digest` — correct
- Token hash (SHA-256 of HMAC) stored in DB, not raw token — correct
- Bearer token ownership verified before deregister — correct
- CORS `allow_origins=["*"]` is intentional for prototype; must be locked down before production

**No injection risk found.** All SQLite queries use parameterized statements (`?` placeholders). No string formatting into SQL.

**No deserialization risk.** `json.loads` is used only on data written by Substrate itself (not from external input).

---

## 7. Test Coverage

**What's covered well:**
- All four new modules have thorough unit tests (160 tests total)
- Privacy suppression rules in EventBus are individually verified
- Thread safety in PrivacyManager is directly tested
- HMAC token lifecycle (create, verify, tamper detection, deregister) is tested
- DB edge cases (constraint violations, prune no-ops, empty results) are covered
- Error isolation (subscriber crashes, DB failures) is tested

**What's missing:**

1. **No test verifies `bus.set_privacy_mode()` is called when `PrivacyManager` transitions.** This is the direct cause of BUG-1 going undetected. Add a test to `test_privacy.py`:
   ```
   def test_bus_privacy_mode_synced_on_transition():
       bus = MagicMock()
       pm = PrivacyManager(event_bus=bus)
       pm.set_private()
       bus.set_privacy_mode.assert_called_once_with(True)
   ```

2. **No integration tests across module boundaries.** The test suite tests each module in isolation with mocks. There are no tests that run `PrivacyManager` + `EventBus` + `SubstrateDB` together through the actual API layer. An end-to-end test (even a minimal one hitting the FastAPI app with `httpx` or `TestClient`) would have caught BUG-1 immediately.

3. **No test for `scan_with_events` in `substrate.py`.** The function is entirely untested. Its privacy gate, PID diffing logic, and event emissions are not covered.

4. **No test for `api.py` endpoints.** The integration builder added 5 new endpoints and significant privacy logic but no endpoint tests exist. The verification commands in the build report are manual shell commands, not automated tests.

---

## 8. What Works

The build is substantially correct and the foundation is solid.

- **Database layer:** Clean, well-designed, correct connection management for both in-memory and file-backed modes. WAL mode properly configured. All methods use parameterized queries. The `analytics_metadata` architectural placeholder is well-executed.

- **Event bus:** Privacy suppression rules are correct for all 7 event types. Subscriber error isolation, iterator-copy-on-dispatch, and wildcard subscriptions all work correctly. The `EventType.__str__` override for Python 3.11+ compatibility is the right fix.

- **PrivacyManager:** Thread safety is correctly implemented (lock scope is minimal, no deadlock risk). Fail-open default on DB unavailability is appropriate. Idempotent transitions are well-designed.

- **AgentRegistry:** HMAC architecture is sound. The `registration_time` ownership is correctly implemented — the registry controls the canonical timestamp, the DB stores what it's given. The SHA-256(token) storage pattern is correct.

- **Integration (api.py):** Module initialization order is correct. Cache invalidation on privacy toggle is correct. Ownership check on DELETE is correctly implemented. All 5 new endpoints are correctly designed.

- **Dashboard:** Privacy toggle placement, optimistic UI, double-click prevention, and server-state confirmation on toggle are all correctly implemented. `pollStatus()` guard against privacy stub response is correctly placed.

- **Housekeeping:** `.gitignore` entries are correct. JSON state file references removed from `substrate.py`.

---

## Summary

| # | Severity | Issue | File |
|---|----------|-------|------|
| BUG-1 | Medium-High | `EventBus.set_privacy_mode()` never called — bus privacy filter permanently inactive | `privacy.py` |
| BUG-2 | Low | `scan_with_events` docstring self-contradicts `None` vs `[]` semantics | `substrate.py` |
| BUG-3 | Low | `applyPrivacyUI(false)` leaves pulse dot in offline state for up to 5 seconds | `dashboard.html` |
| BUG-4 | Low | `register_agent()` minor readability issue with unused-looking `now` placement | `database.py` |
| EDGE-1 | Prototype OK | No lock on module-level globals in `_get_state()` | `api.py` |
| EDGE-2 | Acceptable | `_previous_processes` resets to `None` on restart | `api.py` |
| EDGE-3 | Acceptable | Ephemeral HMAC secret invalidates tokens on restart | `agent_registry.py` |
| GAP-1 | Test Gap | No test verifies `bus.set_privacy_mode()` is called on privacy transition | `test_privacy.py` |
| GAP-2 | Test Gap | No integration tests across module boundaries | (missing) |
| GAP-3 | Test Gap | `scan_with_events` has zero test coverage | (missing) |
| GAP-4 | Test Gap | API endpoints have zero automated test coverage | (missing) |

**BUG-1 must be fixed before proceeding.** It is a latent privacy violation waiting for a future code path to expose it. The fix is a one-line addition to `PrivacyManager._emit_toggle_event()`. Test GAP-1 must be added at the same time to prevent regression.

BUG-2 through BUG-4 can be fixed in the same pass. Test GAPs 2-4 are appropriate for a follow-on testing round.
