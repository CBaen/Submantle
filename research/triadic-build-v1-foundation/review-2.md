# Security Review — Submantle V1 Foundation
**Date:** 2026-03-10
**Reviewer:** Independent (claude-sonnet-4-6)
**Scope:** Privacy mode integrity, token forgery resistance, SQL injection, API input validation, data exposure, XSS, dashboard leakage
**Test suite:** 160/160 passing

---

## Summary Verdict

The security posture of this build is **good for a prototype, with three issues that need resolution before any production use and two advisory findings**. The cryptographic design is sound, SQL injection is structurally impossible, and the privacy gate is real. The issues found are: an unauthenticated registration endpoint that is a spam/abuse vector, a CORS wildcard that will become a problem the moment the token system matters, and a subtle double-verify race in the DELETE endpoint.

---

## 1. Integration Errors

### FINDING 1 — EventBus privacy state is not synchronized at startup

**Severity: Low / Correctness gap**

`PrivacyManager` loads persisted state from the DB at init time (`_load_persisted_state`). `EventBus` defaults to `_privacy_mode = False` at init time regardless. The integration in `api.py` initializes `_privacy = PrivacyManager(db=_db, event_bus=_bus)` — but this only calls `set_privacy_mode` on the bus when a *transition* happens. If the server was shut down in PRIVATE mode and restarted, `PrivacyManager` will correctly wake up in PRIVATE mode (it reads the DB), but `EventBus._privacy_mode` will be `False` until the first toggle.

**Impact:** In the window between server startup and the first toggle, if something calls `bus.emit(EventType.PROCESS_STARTED, ...)` before `PrivacyManager.check_privacy()` has been checked by the caller, the event bus will dispatch and log it. In practice `_get_state()` gates on `_privacy.check_privacy()` before calling `scan_with_events`, so the bus's own filtering is a defense-in-depth layer, not the primary gate. The primary gate (`check_privacy()`) is always correct. But the defense-in-depth layer is wrong for the first scan cycle after restart in PRIVATE mode.

**Fix:** In `PrivacyManager.__init__`, after `self._state = self._load_persisted_state()`, call `self._event_bus.set_privacy_mode(self.is_private())` if `self._event_bus is not None`.

---

### FINDING 2 — DELETE /api/agents/{agent_id} double-verifies, creating a TOCTOU window

**Severity: Low / Correctness gap**

The DELETE endpoint calls `_registry.verify(token)` to get `agent_info`, then passes `token` to `_registry.deregister(token)`. `deregister()` internally calls `verify(token)` again before deleting. Between the first verify and the second verify, a concurrent DELETE on the same agent (from another request) could deregister the agent first. The second verify would then return `None`, and `deregister()` would return `False`, causing the endpoint to return 404 to the original caller even though the intent (removing the agent) was already accomplished by the concurrent request.

This is a benign TOCTOU — both requests have valid tokens, both are authorized. The outcome is cosmetically wrong (one caller gets a 404 for their own valid token) but not a security hole.

**Fix:** The cleaner design is to have the endpoint call `registry.deregister(token)` directly and let that method handle the auth check internally. The ownership check `agent_info["id"] != agent_id` (to validate the URL matches the token owner) is the only thing the endpoint needs to do before delegating to `deregister`. Extract just the ownership guard from the verify result, then call `deregister` once.

---

## 2. Constraint Violations

None. All project constraints from CLAUDE.md are respected:
- No LLM classification added
- No external network calls beyond the pre-existing ARP/ping device discovery
- signatures.json untouched
- Dashboard visual language preserved

---

## 3. Bugs and Logic Errors

### FINDING 3 — `toggle()` has a non-atomic read-then-act pattern

**Severity: Low / Thread-safety nuance**

```python
def toggle(self) -> dict:
    with self._lock:
        current = self._state   # read under lock
    # lock released here
    if current == PrivacyState.AWARE:
        return self._transition_to(PrivacyState.PRIVATE)  # acquires lock again
    else:
        return self._transition_to(PrivacyState.AWARE)
```

Between releasing the lock after reading `current` and acquiring it again in `_transition_to`, another thread could call `toggle()`. Both threads see the same `current`, both call `_transition_to` to the same new state, and `_transition_to` correctly handles this — it sets the state and checks `changed = previous != new_state`. Because `_transition_to` uses the lock for its own write, the second write will be a no-op that correctly returns `changed=False`.

The result: two rapid concurrent toggles could both resolve to the same target state (both go PRIVATE to AWARE, neither goes AWARE to PRIVATE to AWARE). This is not a security failure but is a behavioral surprise. The idempotency guard means no extra events fire, and the state settles correctly.

**Fix for a true atomic toggle:** Hold the lock for both the read and the write. Since `_transition_to` acquires the lock, inline the transition logic into `toggle()` under a single lock acquisition. For prototype use, this is not urgent.

---

### FINDING 4 — `record_query` calls `verify()` on every query, doubling DB lookups

**Severity: Performance / Not a security bug**

`api.py` does not currently call `record_query` anywhere. When it is wired in (future), every authenticated agent request will call `verify()` once for auth, then `record_query()` calls `verify()` again internally. Two DB lookups per request where one would suffice.

This is not a security issue but is worth noting: if `record_query` is ever wired into a hot path, refactor it to accept `agent_id` directly instead of re-deriving it from the token.

---

## 4. Edge Cases

### FINDING 5 — Agent name collision is silently unconstrained at the registry layer

**Severity: Advisory**

`agent_registry.py` does not check for duplicate `agent_name` before inserting. The DB schema has no UNIQUE constraint on `agent_name`, only on `token_hash`. Two agents with the same name can be registered and will receive different tokens. The `list_agents()` output and the future trust-scoring system will see two agents with identical names.

This may be intentional (the same agent version could legitimately run on multiple devices with the same name). But if `agent_name` is expected to be a unique identifier across the registry, the constraint belongs in the schema. Currently it is not enforced at any layer.

No exploit exists here — it is a semantic ambiguity, not a security gap. Worth deciding now before the trust-scoring algorithm is designed around it.

---

### FINDING 6 — `/api/agents/register` is completely unauthenticated

**Severity: Medium — should be addressed before any non-local deployment**

Any caller with network access can POST to `/api/agents/register` and receive a valid token. There is no rate limiting, no admin approval, no allowlist. For a localhost prototype serving a single user this is acceptable. But the moment Submantle is deployed on a network-accessible interface (which the "phone sees laptop via WiFi" V1 goal requires), any device on the LAN — or any malicious process on the host — can register arbitrary agents and receive valid HMAC tokens.

The tokens themselves are cryptographically sound. The weakness is that the issuance gate is open to anyone who can reach the port.

**Recommended mitigation for V1:** Require a one-time registration passphrase (stored in DB settings, set on first run, displayed to the user in the dashboard) that must be included in the registration body. This is a low-friction change that closes the open registration door without adding complexity.

**Not blocking for current prototype phase,** but must be resolved before the WiFi discovery feature ships.

---

## 5. Regression Risk

The integration builder chose to rewrite `api.py` rather than modify it surgically. The rewrite preserves all existing endpoint signatures and behavior in AWARE mode, verified by test coverage. No regressions observed. The risk here is that the new api.py has zero direct tests — all test coverage is at the module level (database, events, privacy, registry). A test for the API layer would catch endpoint-level integration failures.

---

## 6. Security

### FINDING 7 — CORS wildcard (`allow_origins=["*"]`) combined with credential-bearing token header

**Severity: Medium — advisory for current prototype, real risk when deployed**

`api.py` sets `allow_origins=["*"]`. The DELETE endpoint requires `Authorization: Bearer <token>` in the header. On `allow_origins=["*"]`, the CORS spec does not allow `credentials: include` in browser requests, so this combination cannot be used to steal tokens via CSRF from a browser that holds them in cookies. However: the dashboard currently stores no tokens (it has no agent registration UI), and tokens are returned in response bodies only at registration time.

The real risk: if a future feature allows the dashboard to act on behalf of a registered agent (e.g., storing the token in localStorage and passing it in headers), then any page the user visits can read and exfiltrate data from Submantle since all origins are allowed. A token stored in localStorage is not protected by same-origin policy against fetch() calls from other origins.

For the current prototype (no tokens in browser storage, API is localhost-only), this is low risk. It must be restricted before V1.

**Fix:** Restrict `allow_origins` to `["http://localhost:8421"]` or an explicit allowlist. Do not use `["*"]` in production.

---

### Is privacy mode truly blind?

**Yes, with the startup-sync caveat noted in Finding 1.**

Three independent gates must fail simultaneously for process data to escape in PRIVATE mode:

1. `_privacy.check_privacy()` in `_get_state()` — this is the authoritative gate, using the lock-protected in-memory state. It cannot be bypassed by a DB failure, stale cache, or concurrent request.
2. `scan_with_events()` re-checks `privacy_manager.check_privacy()` before touching psutil.
3. `EventBus._privacy_mode` — a defense-in-depth filter. Wrong at startup (Finding 1), correct otherwise.

The gate at layer 1 is real. In-memory state changes atomically under a lock. No code path reaches `scan_processes()` without passing this gate. Privacy mode persists to DB as a best-effort backup — if the DB write fails, the state is correct in memory and will survive for the current process lifetime (but not a restart). This is documented and acceptable.

**Privacy mode does NOT stop** the `/api/devices` endpoint, which scans the local network. Network topology is arguably sensitive data. The build brief does not mention this and it may be intentional, but it is worth flagging: enabling privacy mode stops process data collection but the LAN device list remains live.

---

### Can agent tokens be forged?

**No, given the secret is uncompromised.**

The HMAC-SHA256 construction is correct. Token message is `"agent_name:timestamp"` — the colon separator prevents the specific prefix-extension attack described in the docs. Verification uses `hmac.compare_digest`, which is timing-safe. The raw token is never stored — only its SHA-256 hash. A DB breach yields token hashes that cannot be reversed to recover the original tokens (SHA-256 is preimage-resistant). The server secret is 32 bytes from `secrets.token_bytes(32)` — 256 bits of entropy, appropriate for HMAC.

**One residual concern:** The server secret is stored as a hex string in the SQLite `settings` table. A local attacker who can read `substrate.db` can extract the secret and forge tokens for any agent name and timestamp they wish. This is an accepted tradeoff for an on-device prototype — the attacker with DB read access already has full local access. For a multi-user or networked deployment, the secret storage location should be reconsidered (e.g., OS keystore).

---

### Are there SQL injection vectors?

**No.** Every SQL statement uses parameterized queries (sqlite3's `?` placeholder). There is not a single instance of string interpolation in SQL construction in `database.py`. This is fully correct.

---

### XSS in dashboard.html?

**No. The dashboard is XSS-clean.**

All DOM construction uses the `el()` helper, which creates elements with `document.createElement` and sets content via `element.textContent`. The `textContent` setter never interprets HTML. The `process.cmdline` string passed to query results goes through `textNode(str)` which calls `document.createTextNode()` — also safe. There is no `innerHTML`, no `document.write`, and no `eval` anywhere in the file.

---

### Data leakage in dashboard JavaScript?

None observed. The dashboard does not store tokens, does not log to console (no `console.log` calls), and does not make any cross-origin requests. The only external requests are to `fonts.googleapis.com` (for Inter and JetBrains Mono). For a strictly air-gapped deployment, those font loads are a minor privacy consideration, but this is standard practice and explicitly allowed by the build brief's visual language constraint.

---

## 7. Test Coverage

**160 tests, all passing. Coverage is strong at the module level but absent at the API layer.**

Strong:
- Privacy mode state machine fully covered including thread-safety and persistence failure modes
- HMAC construction, collision prevention, tamper detection all covered
- Event bus privacy suppression rules exhaustively covered per event type
- DB operations including edge cases (empty results, constraint violations, pruning no-ops)

Gaps:
- `api.py` has no tests. The five new endpoints are untested at the HTTP layer. The privacy integration in `/api/status` and `/api/query` is untested via HTTP. An incorrect endpoint response (wrong status code, wrong field name) would not be caught.
- `substrate.py` `scan_with_events` has no tests. The PID diffing logic and event emission are untested. The privacy gate in `scan_with_events` is untested.
- Dashboard JavaScript has no tests. The `applyPrivacyUI` state machine, the `privacyToggling` lock, and the `pollStatus` guard are untested. These are not security issues but are behavioral code with no coverage.

---

## 8. What Works

The fundamentals are solid:

- **Privacy gate is real.** In-memory lock-protected state, checked before any psutil call. Cannot be bypassed by cache staleness or DB failure.
- **HMAC cryptography is correct.** stdlib only, proper construction, timing-safe comparison, hash-not-token storage.
- **SQL injection is structurally impossible.** 100% parameterized queries, no string interpolation.
- **XSS is structurally impossible.** 100% textContent/createTextNode, no innerHTML.
- **EventBus privacy suppression is correctly implemented** for all seven event types.
- **Token hash storage is correct.** SHA-256 of the token is stored; a DB breach cannot yield usable tokens.
- **Privacy mode cache invalidation is correct.** The cache is flushed on toggle, preventing stale process data from appearing immediately after switching to PRIVATE mode.
- **The dashboard privacy UI is well-designed.** Optimistic update, revert on failure, `privacyToggling` lock preventing double-submit, and `pollStatus` guard preventing crash on privacy-mode API response.
- **Initialization order is correct.** DB to EventBus to PrivacyManager to AgentRegistry matches the dependency graph.
- **The interface mismatch bug (`delete_agent` vs `deregister_agent`) was caught and fixed in Round 2.** The fix is correct — the mock was updated to match the real interface, not the other way around.

---

## Issues Summary

| # | Finding | Severity | Blocking? |
|---|---------|----------|-----------|
| 1 | EventBus privacy state not synced at startup when restarting in PRIVATE mode | Low | No |
| 2 | DELETE endpoint double-verify creates benign TOCTOU | Low | No |
| 3 | `toggle()` non-atomic read-then-act (concurrent toggle behavioral surprise) | Low | No |
| 4 | `record_query` double-verifies (future performance concern) | Advisory | No |
| 5 | No agent_name uniqueness constraint | Advisory | No |
| 6 | `/api/agents/register` unauthenticated — open to LAN abuse when WiFi feature ships | Medium | Before WiFi deployment |
| 7 | CORS `allow_origins=["*"]` — risk escalates when tokens enter browser storage | Medium | Before V1 network deployment |

None of the findings are blocking for the current prototype phase. Findings 6 and 7 must be resolved before the phone-sees-laptop WiFi feature ships. Finding 1 should be fixed in the next build pass — it is a one-line change.
