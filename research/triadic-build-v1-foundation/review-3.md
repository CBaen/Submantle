# Independent Review — Build Round: V1 Foundation
**Date:** 2026-03-10
**Reviewer:** Construction Reviewer (independent — did not build this code)
**Focus:** Architecture quality and forward compatibility. MCP readiness, event bus async upgrade path, SQLite schema soundness, constraint compliance, resource weight.

---

## Test Suite Results

160/160 passing. Python 3.14.2. Run time: 0.31s. No errors, no warnings.

---

## 1. Integration Errors

### Finding 1.1 — PrivacyManager does NOT sync the EventBus on toggle [REAL BUG]

This is the most important issue in the build.

The data-events builder (Round 1) correctly documented:
> "Privacy mode is mirrored from PrivacyManager. The bus holds a copy of the privacy state for filtering decisions. `set_privacy_mode()` is called by PrivacyManager when the state changes."

The security-identity builder (Round 1) correctly documented:
> "When `PrivacyManager` toggles state, it should call both `bus.set_privacy_mode(active)` AND emit `EventType.PRIVACY_TOGGLED`."

The integration builder (Round 2) wired PrivacyManager correctly (`PrivacyManager(db=_db, event_bus=_bus)`) but **`PrivacyManager._transition_to()` never calls `self._event_bus.set_privacy_mode()`**.

Looking at `privacy.py` line 156–158:
```python
if changed:
    self._persist_state(new_state)
    self._emit_toggle_event(previous, new_state)
```

`_emit_toggle_event()` fires the PRIVACY_TOGGLED event on the bus, but **the bus's internal `_privacy_mode` flag is never flipped**. The EventBus remains in AWARE mode regardless of the PrivacyManager's state.

**Consequence:** When the user activates privacy mode:
- `_privacy.check_privacy()` correctly returns `True` — scans stop
- The scan cache is invalidated — correct
- BUT `_bus._privacy_mode` stays `False`
- Any component that calls `bus.emit("PROCESS_STARTED", ...)` (e.g., a future background scan thread, or the WebSocket stream) will have those events dispatched and persisted to SQLite, bypassing the EventBus privacy filter entirely

The EventBus privacy filter is architecturally inert until this is fixed. Scan suppression currently only works because `scan_with_events` checks `privacy_manager.check_privacy()` before calling `bus.emit()`. The defense-in-depth the bus provides — its own independent filter — is not activated.

**Fix required in `privacy.py` `_transition_to()`:**
```python
if changed:
    self._persist_state(new_state)
    if self._event_bus is not None:
        self._event_bus.set_privacy_mode(new_state == PrivacyState.PRIVATE)
    self._emit_toggle_event(previous, new_state)
```

### Finding 1.2 — `record_query` calls `verify()` twice per agent request [PERFORMANCE/DESIGN]

`api.py` has no `record_query` call at all in the agent endpoints. That is a separate gap (see section 4.2). But within `agent_registry.py`, `record_query()` internally calls `verify()`, which does:
1. Hash the token (`sha256`)
2. DB lookup by hash
3. HMAC re-derivation
4. Timing-safe comparison

If api.py ever calls `verify()` to authenticate a request and then calls `record_query()` separately, the full verification runs twice for every authenticated agent request. The correct pattern would be to pass the verified agent record into `record_query`, not re-derive it. This is a design smell for the MCP server — every agent query will hit this double-verify cost.

### Finding 1.3 — DELETE endpoint performs verify() then deregister() which performs verify() again [DOUBLE VERIFY]

In `api.py` `agents_deregister()`:
```python
agent_info = _registry.verify(token)   # verify #1
...
success = _registry.deregister(token)  # verify #2 inside deregister()
```

`registry.deregister()` calls `self.verify(token)` internally (line 296 of `agent_registry.py`). This is three DB lookups and three HMAC computations for a single DELETE request. For a prototype it is invisible, but for MCP traffic at scale this pattern compounds into measurable overhead.

---

## 2. Constraint Violations

### Finding 2.1 — Dashboard loads Google Fonts from the network [PRIVACY CONCERN]

`dashboard.html` lines 9–10:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?..." rel="stylesheet">
```

The build brief states: "Do NOT add any external network calls or telemetry."

Loading Google Fonts is an external network call that leaks the user's IP and browser fingerprint to Google. The pre-existing code before this build round already had this, and the integration builder correctly did not change the design language — but the constraint was re-stated in the brief and a reviewer must flag it. It was not introduced in this build round.

Severity: Low for a prototype running on localhost. Non-negotiable before any production deployment or user distribution.

### Finding 2.2 — All constraints otherwise respected

- No LLM classification: confirmed
- No external network calls introduced by this build round: confirmed
- Signatures.json untouched: confirmed
- Design language preserved: confirmed
- Lightweight (no ORMs, no heavy dependencies): confirmed

---

## 3. Bugs and Logic Errors

### Finding 3.1 — `scan_with_events` docstring contradicts the implementation [MISLEADING DOCUMENTATION]

The docstring says:
> "Pass None (or []) on first run — every process will look 'new' but no PROCESS_STARTED events will be emitted without a baseline (events require knowing what changed). To emit events on the very first scan, pass an empty list explicitly."

This is internally contradictory. `None` and `[]` are documented as equivalent ("Pass None (or [])") but then distinguished ("To emit events on the very first scan, pass an empty list explicitly"). The code correctly distinguishes them — `if previous_processes is not None` at line 225 is the gate. But the docstring says "Pass None (or [])" which implies they are equivalent. A future integrator reading this will be confused.

The correct behavior is:
- `None` = no diff, no lifecycle events (first call, no baseline yet)
- `[]` = diff against empty set (every current process emits PROCESS_STARTED)

The docstring must be corrected. This is not a code bug but will produce incorrect integration behavior if read by the MCP server builder.

### Finding 3.2 — Agent re-registration with same name is silently allowed [SECURITY GAP]

`register()` in `agent_registry.py` has no uniqueness check on `agent_name`. Two separate callers can both register `"claude-mcp-client"` and receive two different valid tokens. Both tokens verify successfully. The trust score and incident tracking then split across two records.

The UNIQUE constraint on `token_hash` means two registrations with identical timestamp+name are impossible (same HMAC = same hash = integrity violation). But in practice timestamps always differ, so two agents with the same name register without error.

This matters for the MCP server design: if an agent re-registers after losing its token, the old record accumulates while the new one starts fresh. There is no way to discover "I already have an old registration."

This may be intentional for the prototype, but it should be a documented decision. The build brief is silent on this.

### Finding 3.3 — `_CACHE_TTL = 5.0` but `pollStatus` interval is also 5 seconds [RACE CONDITION]

`api.py` cache TTL is 5 seconds. The dashboard polls every 5 seconds. If the poll and the cache expiry are in phase, the cache will sometimes still be warm when the poll arrives, and the user will see data that is effectively up to 10 seconds old. This is expected for a prototype but should be documented — or the cache TTL should be slightly less than the poll interval (e.g., 4.5s) to ensure each poll gets fresh data.

### Finding 3.4 — No API endpoint tests [TEST COVERAGE GAP]

There are 160 tests for the four isolated modules but zero tests for `api.py`. The integration points — initialization order, privacy mode responses, agent endpoint behavior, DELETE ownership check — are untested at the HTTP level. The integration builder noted this implicitly by only providing "verification commands" rather than an automated test suite.

Missing test coverage includes:
- `GET /api/status` in PRIVATE mode returns the stub shape
- `GET /api/query` in PRIVATE mode returns 403
- `POST /api/privacy/toggle` invalidates the cache
- `DELETE /api/agents/{id}` rejects wrong-owner tokens
- `POST /api/agents/register` with missing fields returns 422

If the MCP server is built assuming these endpoints behave correctly, and they don't, there is no automated net to catch the failure.

---

## 4. Edge Cases

### Finding 4.1 — Privacy toggle during an in-flight scan [THEORETICAL RACE]

`_get_state()` in `api.py` is not atomic. Sequence:
1. `_privacy.check_privacy()` returns False (AWARE)
2. Thread yields (Python GIL allows this between bytecodes)
3. User posts `/api/privacy/toggle` → state becomes PRIVATE
4. `scan_with_events()` runs, scans processes, emits PROCESS_STARTED events

The scan runs after the privacy toggle. `scan_with_events` has its own internal `privacy_manager.check_privacy()` gate at the top, so it will re-check. But between that check and the `bus.emit()` calls there is still a window. In a single-process asyncio server (FastAPI/uvicorn default), the GIL doesn't apply the same way and concurrent requests can interleave. This is a theoretical issue at the prototype scale but becomes real when the MCP server adds concurrent agent queries.

The correct architecture for this is `asyncio.Lock` on `_get_state()`, but this is a known async-upgrade concern documented by the builders.

### Finding 4.2 — `record_query` is never called from api.py [MISSING WIRE]

The agent registry's `record_query()` method tracks last_seen and total_queries. This is the foundation of the future trust scoring system. There is no call to `_registry.record_query(token)` anywhere in `api.py`. The query counter and last_seen timestamp will never increment through normal API usage.

This means the trust tracking infrastructure built in Round 1 is correctly wired to the DB but disconnected at the API layer. When the MCP server queries Substrate, no usage data accumulates. The trust scoring algorithm (future work) will have no data to work with.

### Finding 4.3 — `deregister` endpoint returns 404 if deregister() returns False AFTER verify() succeeded [IMPOSSIBLE STATE]

In `agents_deregister()`:
```python
success = _registry.deregister(token)
if not success:
    raise HTTPException(status_code=404, detail="Agent not found")
```

`deregister()` returns False if `verify(token)` returns None. But we already verified the token two lines up — if the token was valid then, it must still be valid now (within the same request). The only way `deregister()` returns False at this point is if:
a) The DB deleted the agent between the two verify calls (race condition)
b) `deregister()` has a bug

This 404 path is unreachable in practice, but it's also misleading — returning 404 for a token that was just successfully verified is confusing. This is a minor logic smell.

### Finding 4.4 — `_load_persisted_state` in PrivacyManager can raise on invalid stored value [UNCAUGHT EXCEPTION]

```python
raw = self._db.get_setting(_SETTING_KEY)
if raw is not None:
    return PrivacyState(raw)
```

If the settings table somehow contains a corrupted `privacy_mode` value (e.g., `"UNKNOWN"` or `"1"`), `PrivacyState(raw)` raises `ValueError`. This is inside the outer `try/except Exception`, so it falls through to return `PrivacyState.AWARE` — which is the safe fallback. The behavior is correct but not obviously intentional. A comment would clarify this is an expected error path.

---

## 5. Regression Risk

### Finding 5.1 — Existing endpoints are structurally preserved, no regressions detected

The original `/api/status`, `/api/query`, `/api/devices`, and `/` endpoints all exist with backward-compatible response shapes when in AWARE mode. The new `privacy_mode: False` field added to the status response is an additive change that existing consumers should handle gracefully.

### Finding 5.2 — `main()` in substrate.py still works standalone

The `main()` function in `substrate.py` does not use `scan_with_events()` — it calls `scan_processes()` directly. This is correct and intentional (CLI use case needs no event bus). No regression.

---

## 6. Security

### Finding 6.1 — CORS is wide open [ACCEPTABLE FOR PROTOTYPE, MUST CLOSE BEFORE PRODUCTION]

```python
allow_origins=["*"]
```

Any website can POST to `/api/privacy/toggle` and flip privacy mode, or POST to `/api/agents/register` and get a valid agent token. This is a standard localhost development default but must be locked to `["http://localhost:8421"]` before any non-localhost deployment. The MCP server will also need careful CORS thinking.

### Finding 6.2 — Agent token returned in plain JSON, no transport encryption [PROTOTYPE ACCEPTABLE]

`POST /api/agents/register` returns the bearer token in JSON. On localhost this is fine. When Substrate gains a network-accessible interface (MCP server, mesh sync), this endpoint must be TLS-only. Documenting this now protects the MCP builder from assuming the token channel is secure.

### Finding 6.3 — Token security design is sound

HMAC-SHA256 construction, timing-safe comparison via `hmac.compare_digest`, SHA-256 hash storage (not the raw token), and separator to prevent concatenation collisions — all correct. No issues.

### Finding 6.4 — Privacy mode cannot be remotely disabled by an agent [CORRECT BEHAVIOR]

The `/api/privacy/toggle` endpoint has no authentication requirement. Anyone with network access to the API can toggle privacy off. This is currently acceptable because Substrate is localhost-only. The MCP server build round must decide: should agents be able to disable privacy mode? Almost certainly not. Document this decision before the MCP endpoints are designed.

---

## 7. Test Coverage

### Gaps

1. **No api.py tests** — see Finding 3.4. The entire HTTP integration layer is untested. This is the highest priority test gap.

2. **No scan_with_events tests** — `substrate.py`'s new function has no test coverage. The `None` vs `[]` semantics (Finding 3.1), the PROCESS_STARTED/DIED diff logic, and the PRIVATE mode early return are all untested.

3. **No integration tests that cross module boundaries with real objects** — all tests mock their dependencies. There is no test that wires `SubstrateDB + EventBus + PrivacyManager + AgentRegistry` together and verifies the whole chain. Finding 1.1 (bus privacy mode not synced) would be caught by an integration test.

4. **MockDB in `test_agent_registry.py` does not call `get_agent_by_id`** — this method is used in the real DB but the mock doesn't implement it. The mock is not a faithful contract proxy.

5. **Thread safety tests for `AgentRegistry` are absent** — `PrivacyManager` has three thread safety tests. `AgentRegistry` has none, despite having a non-trivial secret loading path that could theoretically have a TOCTOU issue on first run with two concurrent callers.

### Strengths

- Database tests are exhaustive and well-structured. All edge cases (nulls, constraint violations, empty results, prune no-ops) are covered.
- EventBus privacy suppression matrix is completely tested — every event type in both modes.
- PrivacyManager thread safety tests exist and are meaningful (concurrent toggles, read-while-write).
- 0.31s test run time is excellent — no I/O overhead, fully in-memory.

---

## 8. MCP Integration Readiness

### Ready
- `EventBus` wildcard subscriptions are a natural hook for MCP event streaming. An MCP subscription handler can `bus.subscribe("*", mcp_stream_callback)` and receive all events.
- The `source` field on `Event` enables routing to the right MCP resource.
- `AgentRegistry` is exactly the right primitive for MCP agent authentication — register once, verify on each tool call.
- The SQLite schema (particularly `events` and `agent_registry`) is the right persistence layer for MCP audit trails.

### Gaps
- Finding 1.1 (bus privacy mode not synced) means the MCP stream would leak process events in PRIVATE mode if it subscribes to the bus directly. **This must be fixed before the MCP server is built.**
- Finding 4.2 (record_query never called) means the MCP server will need to add this call itself, or it will be added twice when someone notices.
- The async upgrade is well-documented (one comment block in EventBus explains exactly what to change) but not yet done. The MCP server using asyncio will need to make this upgrade.

### WebSocket Streaming Readiness
The synchronous EventBus is ready to be wrapped in a simple asyncio queue pattern:
```python
async def event_stream(request: Request):
    queue = asyncio.Queue()
    bus.subscribe("*", lambda e: queue.put_nowait(e.to_dict()))
    async for event in queue_to_generator(queue):
        yield event
```
The `to_dict()` method on Event is correctly implemented. The wildcard subscription handles all event types. The privacy filter on the bus (once Finding 1.1 is fixed) means privacy mode is automatically respected by the stream.

---

## 9. SQLite Schema Soundness

The schema is well-designed for Substrate's long-term needs:

- `analytics_metadata` column on `scan_snapshots` is correctly present from day one, nullable, with detailed comments explaining why it cannot be retrofitted. This is sound forward architecture.
- WAL mode is correct for the concurrent read/write access pattern.
- `token_hash UNIQUE` on `agent_registry` provides the right constraint.
- Indexes on `timestamp` and `event_type, timestamp` are exactly right for the query patterns used.
- No migrations are needed in the foreseeable future — the schema has room for the trust scoring algorithm (fields already exist), federated analytics (column already exists), and event streaming (events table is already append-only with the right structure).

One concern: there is no `db.close()` call anywhere in `api.py`. The in-memory connection is only relevant for tests, but the file-backed DB uses per-operation connections (so no persistent connection to close). Still, a `lifespan` handler in FastAPI for graceful shutdown would be cleaner and is required when the DB pattern changes.

---

## 10. What Works

The foundation is solid. Here is what is genuinely well-built:

1. **The four-module architecture is clean.** Each module has a single responsibility, clear interfaces, and documented dependencies.
2. **Initialization order is correct and documented.** The comment in `api.py` lines 7–11 is exactly the right thing to have there.
3. **Privacy mode is a real off switch.** The `threading.Lock` in PrivacyManager, the bus filter, and the scan gate are all independently consistent. The flaw (Finding 1.1) is a missing wire, not a design flaw.
4. **Token security architecture is correct.** Not storing raw tokens, using HMAC re-derivation for verification, and timing-safe comparison are all right decisions made from first principles.
5. **The EventBus privacy suppression table is complete and correct.** Every event type is explicitly classified. The `_PROCESS_EVENTS` frozenset is the right primitive.
6. **`analytics_metadata` is present from day one.** This is the one architectural decision the build brief called "cannot be retrofitted" — it was done correctly.
7. **The async upgrade is designed-in, not an afterthought.** The comments in `events.py` tell the next builder exactly what to change and why.
8. **Test isolation is excellent.** In-memory DB, mock dependencies, no file I/O — the 160 tests run in 0.31 seconds and leave no artifacts.

---

## Summary of Issues by Priority

| Priority | Finding | Action |
|----------|---------|--------|
| P0 — Fix before MCP build | 1.1 — Bus privacy mode not synced by PrivacyManager | Fix `_transition_to()` to call `bus.set_privacy_mode()` |
| P1 — Fix before release | 4.2 — `record_query` never called from api.py | Add call in agent endpoints |
| P1 — Fix before release | 3.4 — No api.py tests | Add TestClient-based HTTP tests |
| P2 — Fix before MCP build | 3.1 — `scan_with_events` docstring contradicts implementation | Correct the docstring |
| P2 — Document as decision | 3.2 — Duplicate agent names allowed silently | Add a decision log entry |
| P3 — Known, monitor | 1.2/1.3 — Double verify() on record_query and deregister | Acceptable for prototype; redesign before MCP scale |
| P3 — Known, monitor | 2.1 — Google Fonts external call | Not introduced by this build; must close before user distribution |
| P3 — Note for MCP builder | 6.4 — Privacy toggle has no auth | Document the intended policy before designing MCP endpoints |
