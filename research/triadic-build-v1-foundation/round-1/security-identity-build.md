# Security & Identity Build Report — Round 1
**Date:** 2026-03-10
**Builder:** Security & Identity (Opus 4.6)
**Tasks:** Task 3 (privacy.py) + Task 4 (agent_registry.py)
**Status:** Complete — 79/79 tests passing

---

## What Was Built

### prototype/privacy.py — PrivacyManager

A thread-safe, persistence-backed state machine with two states: `AWARE` and `PRIVATE`.

**The guarantee:** When in PRIVATE mode, `check_privacy()` returns `True`. Every component that touches process data calls this gate before doing sensitive work. The off switch is a real in-memory state change protected by `threading.Lock`, not a config file that could be cached or ignored.

**Key design decisions:**

1. **Lock scope is minimal.** The state write happens under the lock. Persistence (DB write) and event emission happen outside it. This means there's a brief window where state has changed but the DB hasn't caught up — that's acceptable because the safe direction is to refuse scanning if uncertain, and in-memory state is what the gate checks.

2. **Fail open on DB unavailability.** If the DB isn't available at startup, default is AWARE. Privacy mode is an operator-initiated action — if the operator hasn't toggled it, AWARE is correct. Failing closed (forcing PRIVATE on DB error) would break normal startup.

3. **PRIVACY_TOGGLED fires in both modes.** The dashboard needs to know when state changes. This is explicitly allowed by the brief.

4. **Idempotent transitions.** `set_private()` when already PRIVATE returns `changed=False` and emits no event. This prevents duplicate events from retry logic.

5. **`check_privacy()` convention.** Returns `True` means "skip this work" — matches how Python gatekeeping code reads naturally: `if privacy_manager.check_privacy(): return`.

**Interface for other components:**
```python
pm = PrivacyManager(db=db, event_bus=bus)

# Gate for sensitive operations
if pm.check_privacy():
    return  # PRIVATE mode — skip

# Toggle
result = pm.toggle()   # {"previous_state": "AWARE", "new_state": "PRIVATE", "changed": True}

# Direct set
pm.set_private()
pm.set_aware()

# State inspection
pm.state          # PrivacyState.AWARE or PrivacyState.PRIVATE
pm.is_private()   # bool
pm.is_aware()     # bool
```

---

### prototype/agent_registry.py — AgentRegistry

Full agent lifecycle with HMAC-SHA256 tokens. No external crypto libraries — `hmac` + `hashlib` from stdlib only.

**Token architecture:**

- Server secret: 32 random bytes, generated on first run, stored as hex in the settings table. Survives restarts. If DB unavailable, ephemeral secret is used (logged as a warning).
- Token derivation: `HMAC-SHA256(secret, "agent_name:registration_time")` as hex
- The colon separator in the message prevents name/timestamp ambiguity (e.g. `"foo"` + `"bar:ts"` would collide with `"foobar"` + `":ts"` without it)
- Storage: only the SHA-256 hash of the token is stored, never the raw token. A compromised DB yields nothing usable.
- Verification: look up by token hash, re-derive expected HMAC from stored data, compare with `hmac.compare_digest` (timing-safe).

**Interface note for Builder A (database.py):**

`register_agent()` must accept a `registration_time` parameter. Without it, the DB would generate its own timestamp that differs from the one used in token derivation, causing all HMAC verifications to fail.

Expected signature:
```python
def register_agent(self, agent_name, version, author, capabilities, token_hash,
                   registration_time: str) -> int:
```

This is a non-optional interface requirement. The brief's interface spec omitted this parameter but it is architecturally necessary. Builder A should be notified.

**Key design decisions:**

1. **Registry owns the timestamp.** The registry generates `registration_time` and passes it to the DB. The DB stores what it's given. This is the only way HMAC re-derivation can work at verify time.

2. **Token hash, not token, stored in DB.** Agent tokens are bearer credentials. Storing them in plain or hashed-but-reversible form would let a DB breach impersonate any agent. SHA-256(token) is not reversible.

3. **Deregister requires a valid token.** Prevents unauthenticated deletion. An agent can only deregister itself (or a system component with the token can deregister it).

4. **Registry is privacy-mode-agnostic.** No `check_privacy()` call inside the registry. Identity is not sensitive. The caller (api.py in Round 2) decides whether to surface registry operations based on privacy state.

5. **DB errors on stats updates (record_query) are non-fatal.** Query counting and last_seen updates are observational, not critical. Failing to increment a counter should never crash an agent request.

**Public interface:**
```python
registry = AgentRegistry(db=db, event_bus=bus)

# Register
token = registry.register("my-agent", "1.0.0", "Alice", ["process_query"])

# Verify (returns agent dict or None)
agent_info = registry.verify(token)

# List all agents (token_hash excluded from output)
agents = registry.list_agents()

# Deregister (requires valid token)
success = registry.deregister(token)

# Record a query (updates last_seen + total_queries)
registry.record_query(token)
```

---

## Tests

### prototype/tests/test_privacy.py
28 tests across 6 test classes:
- `TestPrivacyManagerInit` — defaults, loading from DB, DB failure handling
- `TestPrivacyManagerStatePredicates` — is_private, is_aware, check_privacy
- `TestPrivacyManagerTransitions` — set_private, set_aware, toggle, idempotency
- `TestPrivacyManagerPersistence` — DB writes, no-DB operation, DB write failure
- `TestPrivacyManagerEvents` — PRIVACY_TOGGLED emission, idempotent suppression, bus failure
- `TestPrivacyManagerThreadSafety` — concurrent reads, concurrent toggles, read-while-write

### prototype/tests/test_agent_registry.py
51 tests across 8 test classes:
- `TestAgentRegistryInit` — secret creation, persistence, loading existing, DB failure
- `TestTokenHelpers` — SHA-256 hashing, HMAC derivation, separator collision prevention
- `TestRegister` — success path, DB storage, hash-not-token, input validation, events, DB failure
- `TestVerify` — valid/invalid tokens, empty, no-DB, post-deregister, tamper detection, DB error
- `TestListAgents` — empty, multiple agents, token_hash exclusion, no-DB, DB error
- `TestDeregister` — success, removal, invalid token, empty token, event emission, double-deregister
- `TestRecordQuery` — increment, last_seen update, invalid token, DB error non-fatal
- `TestAgentRegistryPrivacyModeCompatibility` — registry works independently of privacy state

**All 79 tests pass.**

---

## Interface Dependencies for Builder A

Builder A (database.py) must implement `register_agent` with an additional `registration_time` parameter beyond what the build brief specified. All other interfaces match the brief exactly.

| Method | Change | Reason |
|--------|--------|--------|
| `register_agent(...)` | Add `registration_time: str` parameter | HMAC token re-derivation at verify time requires the same timestamp used during registration. If the DB generates its own, HMAC verification always fails. |

---

## Verification Commands

```
cd prototype && python -c "from privacy import PrivacyManager; print('Privacy OK')"
cd prototype && python -c "from agent_registry import AgentRegistry; print('Registry OK')"
cd prototype && python -m pytest tests/test_privacy.py tests/test_agent_registry.py -v
```

All three pass.

---

## Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `prototype/privacy.py` | ~190 | PrivacyManager — thread-safe AWARE/PRIVATE state machine |
| `prototype/agent_registry.py` | ~255 | AgentRegistry — HMAC token lifecycle |
| `prototype/tests/__init__.py` | 1 | Makes tests/ a package |
| `prototype/tests/test_privacy.py` | ~270 | 28 tests for PrivacyManager |
| `prototype/tests/test_agent_registry.py` | ~480 | 51 tests for AgentRegistry |
