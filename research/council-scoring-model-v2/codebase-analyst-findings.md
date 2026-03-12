# Codebase Analyst Findings: Weights and Measures — Scoring Model Evolution
## Date: 2026-03-12
## Role: Codebase Analyst
## Council: Scoring Model V2

---

## Analysis Summary

The codebase is currently at a clean, well-understood fork point. The trust scoring machinery is minimal — two counters feeding one formula — but the architecture is deliberately extensible. Every key surface (the formula, the incident intake path, the DB layer, the API response shape) can absorb the weighted scoring model with contained blast radius, provided the right sequencing is followed. The risks are not in the math; they are in the data structures that don't yet exist.

---

## Step 1: What Exists Now — Structure by Structure

### 1a. The Formula (`agent_registry.py` lines 400–402)

```
q = record["total_queries"]
i = record["incidents"]
score = (q + 1) / (q + i + 2)
```

This is the entirety of `compute_trust()`. It reads two integers from a dict, performs arithmetic, and returns a float. The formula is clean, isolated, and has no side effects. It is entirely contained within `AgentRegistry.compute_trust()` — no other file calls this math directly.

**What it cannot do right now:**
- It does not distinguish incident severity. All incidents count as 1.0.
- It does not weight by reporter credibility. Any string reporter is treated equally.
- It does not apply velocity caps. 10,000 identical self-queries all count.
- It does not use formula_weight. The concept doesn't exist in the schema.
- It reads `incidents` from the aggregate counter, not from the `incident_reports` table. A pending/expired distinction does not exist anywhere.

### 1b. The `agent_registry` Table (`database.py` lines 557–571)

Relevant columns:
- `total_queries INTEGER NOT NULL DEFAULT 0` — aggregate counter, no detail
- `incidents INTEGER NOT NULL DEFAULT 0` — aggregate counter, incremented immediately on any report
- `trust_metadata TEXT DEFAULT NULL` — JSON column, never written to in any current code path

The `incidents` counter is a mutable running total. It does not distinguish pending vs accepted incidents. It increments the moment `record_incident()` is called (`database.py` line 313: `UPDATE agent_registry SET incidents = incidents + 1`).

**The `trust_metadata` column is free real estate.** Verified by Grep: `update_trust_metadata()` exists at `database.py` line 338 and is never called from any current code path. The column exists, has a write method, has a read path in `_row_to_agent()` (line 644), and has a test (`test_update_trust_metadata` in `test_database.py` line 239). It is ready to absorb enrichment data immediately.

### 1c. The `incident_reports` Table (`database.py` lines 580–593)

Current columns:
- `id, agent_id, agent_name, reporter, incident_type, description, timestamp`

Missing columns that the prior council identified and `team-3-review-tiers-findings.md` specified:
- `status` — no pending/accepted/expired/disputed/deduplicated state
- `severity` — no classification
- `formula_weight` — no per-incident weight modifier
- `reporter_agent_id` — reporter is a free-text string, not a FK to a registered entity
- `dedup_group_id` — no deduplication key
- `expires_at` — no auto-expiry
- `reviewed_by`, `reviewed_at` — no review audit trail
- `dispute_filed_at` — no dispute timestamp
- `corroboration_count` — no multi-reporter signal

The `reporter` field (line 585) is `TEXT NOT NULL` — any string. There is zero authentication on who files a report. This is the confirmed critical vulnerability from the prior council.

### 1d. The `record_incident()` Method (`agent_registry.py` lines 415–490)

The method signature is:
```python
def record_incident(self, agent_name, reporter, incident_type, description="") -> bool
```

It immediately calls `self._db.increment_agent_incidents(agent_id)` (line 464) in the same operation as `save_incident_report()` (line 465). There is no pending state, no deduplication check, no severity classification, no velocity cap. One call = one counter increment = score impact is immediate and permanent until the row is hard-deleted (which isn't possible via the current API).

### 1e. The `compute_trust()` Return Shape (`agent_registry.py` lines 404–413)

Current response dict:
```python
{
    "agent_name": ..., "trust_score": ..., "total_queries": ..., "incidents": ...,
    "registration_time": ..., "last_seen": ..., "version": ..., "author": ...
}
```

Missing from the response:
- `has_history` flag (the "thin file" commercial signal — settled by prior council)
- `score_breakdown` — no per-dimension visibility
- `weight_version` — no indication of which weight set was used
- `pending_incidents` — count of incidents not yet affecting formula
- `accepted_incidents` — count that actually contributed to current score

The test `test_compute_trust_returns_metadata` at `test_trust_layer.py` line 131 explicitly asserts the response has exactly these 8 keys:
```python
required_keys = {"agent_name", "trust_score", "total_queries", "incidents",
                 "registration_time", "last_seen", "version", "author"}
```
This test **will fail** if `compute_trust()` adds new keys unless the assertion is updated to use `assertIn` or an expanded set.

### 1f. The API Layer (`api.py`)

Two trust-facing endpoints:
- `GET /api/verify` (line 529) — directory of all agents with scores
- `GET /api/verify/{agent_name}` (line 546) — single agent score check
- `POST /api/incidents/report` (line 566) — incident intake, no auth required

The incident endpoint (`IncidentReportRequest` model at line 332) accepts `agent_name, reporter, incident_type, description` — no bearer token, no interaction ID, no authentication. Any HTTP caller can file an incident against any registered agent.

The `_extract_token()` helper at line 339 is already written and reusable for adding auth to the incident endpoint.

---

## Step 2: What Exists That Can Support Weighted Scoring

### Existing support:
1. **`trust_metadata` JSON column** — never written, but the full plumbing exists: schema column, write method (`update_trust_metadata`), read in row serializer, one passing test. Can absorb dimension data, velocity cap counters, interaction type breakdowns immediately.
2. **`incident_reports` table with per-incident detail** — `incident_type`, `reporter`, `timestamp` already stored. SQL `GROUP BY incident_type` and `GROUP BY reporter` can detect concentration immediately. No new schema needed for basic pattern data.
3. **`compute_trust()` is a single isolated function** — the formula modification surface is exactly one function in one file. No other module does trust math.
4. **`_row_to_agent()` serializer** — adding fields to the trust response requires touching this serializer and the `compute_trust()` return dict, nowhere else for the DB-to-API path.
5. **`settings` table** — key-value store already exists. Weight versioning (store current weight set identifier) fits naturally here.
6. **Event bus** — `INCIDENT_REPORTED` event already fires on every incident. Subscribers can trigger async processing (deduplication, velocity cap checks) without touching the hot path.

### Does not yet exist:
1. **No `interaction_logs` table** — confirmed by Grep and `plan-deepen-notes.md` Section 1. Interaction UUIDs that incident reports reference do not exist anywhere.
2. **No `reporter_registry` table or reporter auth** — the prior council settled this as Tier 1 / ship-blocker. Nothing is built.
3. **No `agent_status` column** — deregister is a hard `DELETE` at `database.py` line 323. Soft-delete is not implemented.
4. **No velocity cap logic anywhere** — no query-per-hour throttle, no reporter-per-agent-per-day limit, no self-query pattern detection.
5. **No weight configuration** — no table, no settings key, no version identifier for the scoring formula.

---

## Step 3: Blast Radius Analysis — Implementing Weighted Scoring

### Change 1: Add `formula_weight` and `status` to `incident_reports`

**Files changed:** `database.py` (schema string + `save_incident_report()` signature + `_row_to_incident_report()` serializer), `agent_registry.py` (`record_incident()` method), `api.py` (`IncidentReportRequest` model, incident endpoint)

**Tests broken:**
- `test_trust_layer.py::TestDatabaseIncidentReports::test_save_and_retrieve_incident_report` — checks specific field list, will pass if new fields have defaults
- `test_trust_layer.py::TestRecordIncident::test_record_incident_increments_counter` — this test will **break conceptually** when status=pending incidents no longer immediately increment the counter
- `test_trust_layer.py::TestRecordIncident::test_record_incident_lowers_trust_score` — same: if new incidents go to `pending` state, this test's assumption (filing an incident immediately lowers the score) becomes false

**Blast radius score: 7/10** — contained to 3 files, but 2-3 tests will need logic updates (not just signature changes).

### Change 2: Modify `compute_trust()` to read `accepted` incidents from `incident_reports` instead of the aggregate counter

**Files changed:** `agent_registry.py` (`compute_trust()`), `database.py` (new query method needed: `get_accepted_incident_count(agent_id)`), potentially `api.py` (if response shape changes)

**Tests broken:**
- `test_trust_layer.py::TestComputeTrust::test_compute_trust_formula_correctness` — this test at line 86 specifically verifies `(10+1)/(10+2+2) = 0.7857`. If the formula now reads from `incident_reports WHERE status='accepted'` instead of the aggregate counter, the test setup must also transition incidents to `accepted` state or the test score will be wrong (incidents would read as 0 if they're still in `pending` by default).
- `test_trust_layer.py::TestComputeTrust::test_compute_trust_after_incidents_decreases` — same dependency
- `test_trust_layer.py::TestRecordIncident::test_record_incident_lowers_trust_score` — same

**Blast radius score: 6/10** — 3 directly failing tests, plus a DB layer addition. The formula change itself is 3 lines. The infrastructure around it (the new query, the status transition mechanism) is larger.

### Change 3: Add `formula_weight` to the formula (weighted incident sum)

**Current formula location:** `agent_registry.py` lines 400–402, exactly 3 lines.

**New formula logic:**
```
effective_incidents = SUM(formula_weight) WHERE status='accepted'
score = (q + 1) / (q + effective_incidents + 2)
```

**Files changed:** `agent_registry.py` (`compute_trust()` + new DB query), `database.py` (new method `get_weighted_incident_sum(agent_id)`), `api.py` (response shape update)

**Tests broken:**
- `test_trust_layer.py::TestComputeTrust::test_compute_trust_formula_correctness` — the test at line 97 computes `11/14`. With formula weights, 2 incidents at weight 1.0 still = 2. No change IF test incidents are accepted at weight 1.0. But if default incidents go to `pending`, the effective_incidents would be 0 and score would be `11/12`. **This test will fail unless test setup explicitly accepts the incidents.**
- All 3 formula-dependent tests in `TestComputeTrust` are affected.

**Blast radius score: 6/10** — same 3 tests, but the formula change is slightly larger.

### Change 4: Add dimension breakdown to `compute_trust()` response

**Files changed:** `agent_registry.py` (`compute_trust()` return dict), `api.py` (downstream consumers get richer data — no breakage, additive)

**Tests broken:**
- `test_trust_layer.py::TestComputeTrust::test_compute_trust_returns_metadata` at line 131 — this test asserts **exactly** the 8-key set. Adding any key to the response breaks `self.assertEqual(required_keys, set(result.keys()))`. This test must be updated to use `assertIsSubset` or expand `required_keys`.

**Blast radius score: 8/10** — one test is the precise breakage surface. It's a low-effort fix once located.

### Change 5: Add weight versioning via `settings` table

**Files changed:** `database.py` (no schema change needed — `settings` table exists), `agent_registry.py` (load weight version at init or compute time), `api.py` (include `weight_version` in response)

**Tests broken:** None expected. The `settings` table already has tests. This is purely additive.

**Blast radius score: 9/10** — minimal. The settings infrastructure is already tested and working.

### Change 6: Add `agent_status` column (soft-delete)

**Files changed:** `database.py` (schema: new column on `agent_registry`; `deregister_agent()` becomes an UPDATE not a DELETE; new `list_agents()` must filter WHERE status='active'), `agent_registry.py` (`deregister()` method, `list_agents()` logic), `api.py` (no change needed)

**Tests broken:**
- `test_agent_registry.py::TestDeregister::test_deregister_removes_from_db` at line 396 — asserts `db.list_agents() == []` after deregister. With soft-delete, the agent record remains; it just has `status='deregistered'`. This test breaks by design.
- `test_agent_registry.py::TestDeregister::test_double_deregister_second_returns_false` — depends on the agent being gone.
- `test_trust_layer.py::TestAgentNameUniqueness::test_deregister_then_reregister_same_name` — this test registers, deregisters, then re-registers same name. With soft-delete, the unique index on `agent_name` would block re-registration unless the uniqueness constraint is scoped to `WHERE status='active'`. This is a more involved change (partial index or application-level logic).
- `test_database.py::TestAgentRegistry::test_deregister_agent` — asserts `get_agent_by_id(agent_id) is None` after deregister. With soft-delete, the agent still exists.
- `test_database.py::TestAgentRegistry::test_deregister_nonexistent_returns_false` — likely still passes.

**Blast radius score: 5/10** — 4 tests break, and the "re-register same name after deregister" feature is a legitimate question about desired semantics with soft-delete. This is the highest-impact single schema change.

### Change 7: Add `reporter_agent_id` FK to `incident_reports`

**Files changed:** `database.py` (schema: new FK column; `save_incident_report()` signature), `agent_registry.py` (`record_incident()` — must now validate that reporter is a registered agent), `api.py` (`IncidentReportRequest` model needs reporter token, endpoint needs auth)

**Tests broken:**
- `test_trust_layer.py::TestRecordIncident::test_record_incident_saves_report` — checks specific fields, will need `reporter_agent_id` added to assertions
- All tests that call `record_incident()` with a plain string reporter will need to be updated if reporter becomes required to be a registered agent. **This is the largest single test surface change** — 8 tests in `TestRecordIncident` all use `reporter="brand-x"` style strings.
- `test_agent_registry.py` tests that call `record_incident` indirectly are not present (the MockDB doesn't implement incident reporting), so no breakage there.

**Blast radius score: 5/10** — the test surface is wide (8 tests) but the changes are mechanical. The larger concern is the schema migration for existing `incident_reports` rows which have no `reporter_agent_id`.

---

## Step 4: Pattern Inventory

### How trust is currently computed: ONE place, ONE function

Grep confirms `compute_trust` appears in exactly 3 files: `agent_registry.py` (definition), `api.py` (two call sites at lines 540 and 555), and `test_trust_layer.py` (test setup). No other file imports or calls trust computation logic.

**Implication for weighted scoring:** Adding dimensions to the formula touches exactly these 3 locations. No other module is affected.

### How incidents are currently recorded: TWO operations, NO pending state

The call chain is: `api.py:record_incident()` → `agent_registry.py:record_incident()` → `db.increment_agent_incidents()` + `db.save_incident_report()`. Two atomic SQLite operations, no transaction wrapper, no status gate. The formula reads `record["incidents"]` which is the aggregate counter, not a `COUNT(*)` from `incident_reports`.

**Implication for weighted scoring:** Moving to `status='accepted'` incidents requires decoupling these two operations. The counter is no longer the source of truth; the `incident_reports` table becomes the source of truth and `compute_trust()` must query it.

### How `trust_metadata` is currently used: it isn't

`update_trust_metadata()` is called from exactly zero places in the production code (confirmed by Grep). The column exists in schema, has a write path, has a read path, has one test. It has been waiting for content since it was created.

**Implication for weighted scoring:** This is the ready-made home for: velocity cap counters, query diversity tracking, interaction type breakdowns, dimension scores, reporter concentration flags. No new column needed. The pattern for writing to it is: read current dict, merge new data, write back. The atomic update race noted in `plan-deepen-notes.md` Section 4 is a real concern — the pattern should be: `UPDATE ... SET trust_metadata = ?` where the new value is computed in Python from the current value, inside a single `_conn()` context.

### How the API exposes trust: raw formula output

The two `/api/verify` endpoints return `compute_trust()` output unchanged. There is no transformation layer between the formula result and the HTTP response. Any change to `compute_trust()`'s return dict is immediately reflected in the API response — no adapter needed, but also no protection layer if the response shape needs to be different from the internal format.

**Implication for weighted scoring:** A `score_breakdown` structure, `weight_version`, `has_history` flag, and `pending_incidents` count can all be added to `compute_trust()`'s return dict and will appear in the API response automatically. The only constraint is the test at `test_trust_layer.py` line 131 that asserts exact key equality.

### How the settings table is used: two consumers

Grep confirms `settings` table is used by: `privacy.py` (privacy mode state), `agent_registry.py` (HMAC secret). Both use simple string get/set. The pattern is established and clean.

**Implication for weighted scoring:** Storing `scoring_weight_version = "v1"` (or a JSON blob of the full weight set) in settings follows the existing pattern exactly. No new infrastructure needed.

---

## Step 5: Dimension Data — What's Available Now vs What Needs Building

| Dimension | Available Now? | Source | What's Needed |
|-----------|---------------|--------|---------------|
| Raw incident count | Yes | `agent_registry.incidents` | Already in formula |
| Incident severity | No | `incident_reports.severity` (doesn't exist) | New column on `incident_reports` |
| Formula weight per incident | No | `incident_reports.formula_weight` (doesn't exist) | New column + logic to set it |
| Pending vs accepted status | No | `incident_reports.status` (doesn't exist) | New column + state machine |
| Reporter credibility | No | Reporter is a free-text string | Need reporter registry + reporter trust scores |
| Query volume | Yes | `agent_registry.total_queries` | Already in formula |
| Query velocity | No | No per-time-window data exists | Velocity cap logic + `trust_metadata` storage |
| Query diversity | No | All queries increment same counter | Per-query-type breakdown needed |
| Interaction type | No | No `interaction_logs` table exists | New table (prerequisite for reporter auth) |
| Agent age | Yes | `agent_registry.registration_time` | Available now, not used in formula |
| Corroboration count | No | `incident_reports.corroboration_count` (doesn't exist) | New column + dedup logic |
| Author cross-agent signal | Partial | `agent_registry.author` exists | SQL query needed, no new schema |

---

## Step 6: Schema Changes Required for Multi-Dimensional Scoring

### Minimum schema additions for V1 weighted scoring:

**On `agent_registry`:**
```sql
agent_status TEXT NOT NULL DEFAULT 'active'  -- active | deregistered | suspended
```

**On `incident_reports`:**
```sql
status           TEXT NOT NULL DEFAULT 'pending'  -- pending | accepted | expired | disputed | deduplicated | suspicious
severity         TEXT NOT NULL DEFAULT 'standard' -- critical | standard | reduced | suspicious
formula_weight   REAL NOT NULL DEFAULT 1.0        -- 1.0 | 0.5 | 0.0
reporter_agent_id INTEGER                          -- FK to agent_registry, NULL for migration compat
dedup_group_id   TEXT                              -- sha256 dedup key, NULL if not in a group
expires_at       REAL NOT NULL DEFAULT 0           -- Unix ts; 0 = no expiry (for migrated rows)
dispute_filed_at REAL                              -- NULL if not disputed
corroboration_count INTEGER NOT NULL DEFAULT 0
reviewed_by      TEXT
reviewed_at      REAL
```

**New table `interaction_logs`** (prerequisite for reporter auth, not strictly required for weighted scoring formula, but required for the eBay model to work):
```sql
CREATE TABLE IF NOT EXISTS interaction_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    interaction_id  TEXT    NOT NULL,            -- UUID v4, shared between perspective rows
    perspective     TEXT    NOT NULL,            -- 'agent' | 'counterparty' | 'submantle'
    party_a_id      INTEGER NOT NULL,            -- agent_registry FK (the querying agent)
    party_b_id      TEXT    NOT NULL,            -- free text for prototype (unregistered counterparties)
    interaction_type TEXT   NOT NULL,            -- 'query' | 'process_check' | etc.
    timestamp       REAL    NOT NULL,
    metadata        TEXT    DEFAULT NULL         -- JSON
);
```

**Weight version in `settings`** (no schema change):
```
key: 'scoring_weight_version'
value: 'v1.0'
```

### What does NOT require schema changes:
- `trust_metadata` on `agent_registry` — free slot, ready now
- `settings` table for weight versioning — exists and works
- Agent age signal in formula — `registration_time` already stored
- Author cross-agent lookup — SQL join on existing data

---

## Step 7: `compute_trust()` Evolution Path

The function currently reads 2 fields. The evolved version would:

1. **Read from `incident_reports` directly** instead of the aggregate counter — `SELECT SUM(formula_weight) FROM incident_reports WHERE agent_id=? AND status='accepted'`
2. **Accept optional dimension overrides** for future weighted inputs
3. **Return a richer dict** including `score_breakdown`, `has_history`, `weight_version`, `pending_incidents`
4. **Read weight configuration** from settings or a hard-coded weight map (V1: hard-coded constants, versioned via settings key)

The aggregate `incidents` counter on `agent_registry` becomes a **cache** or **derived signal** — it can remain for backward compatibility but should no longer be the authoritative input to the formula. This avoids a migration problem: old rows with non-zero `incidents` counters remain readable while the formula transitions to reading the `incident_reports` table.

**Transition approach (no data loss):**
- Keep `incidents` counter on `agent_registry` for now
- Add `status='accepted'` filter logic to `compute_trust()`
- When `incident_reports` table has status data, use it; when it doesn't (rows created before the schema migration), treat all rows as `accepted` (backward-compatible)
- This means the formula reads: `SELECT COALESCE(SUM(formula_weight), 0) FROM incident_reports WHERE agent_id=? AND (status='accepted' OR status IS NULL)`

---

## Step 8: Test Coverage Assessment

**Current test count:** 187 tests across 5 test files (verified by running `pytest --collect-only`).

**Trust-scoring-specific tests by file:**
- `test_trust_layer.py` — 26 tests covering: `compute_trust()` (8 tests), `record_incident()` (8 tests), agent name uniqueness (3 tests), `incident_reports` DB operations (5 tests), event bus behavior (1 test), privacy mode compatibility (1 test)
- `test_agent_registry.py` — `TestRecordQuery` (5 tests covering `record_query()` counter increments), `TestDeregister` (6 tests covering hard-delete behavior that will break with soft-delete)
- `test_database.py` — `TestAgentRegistry::test_increment_incidents` (1 test), `test_update_trust_metadata` (1 test)

**Tests that will break with proposed changes:**

| Test | File | Break Cause | Severity |
|------|------|-------------|----------|
| `test_compute_trust_returns_metadata` | `test_trust_layer.py:131` | Exact 8-key dict assertion — any new key breaks it | Low effort fix |
| `test_compute_trust_formula_correctness` | `test_trust_layer.py:85` | Formula reads accepted incidents, not aggregate counter | Medium — requires test setup to accept incidents |
| `test_compute_trust_after_incidents_decreases` | `test_trust_layer.py:72` | Same as above — filing incident won't lower score if pending | Medium |
| `test_record_incident_increments_counter` | `test_trust_layer.py:154` | Counter no longer increments immediately in pending model | Medium |
| `test_record_incident_lowers_trust_score` | `test_trust_layer.py:166` | Pending incident has no formula impact | Medium |
| `test_deregister_removes_from_db` | `test_agent_registry.py:396` | Soft-delete leaves record in DB | Low effort fix |
| `test_double_deregister_second_returns_false` | `test_agent_registry.py:425` | Deregistered agent still exists | Medium |
| `test_deregister_then_reregister_same_name` | `test_trust_layer.py:281` | Unique index blocks re-registration of soft-deleted name | Higher — semantic question |
| `test_deregister_agent` | `test_database.py:224` | `get_agent_by_id` returns record not None | Low effort fix |
| All 8 `TestRecordIncident` tests | `test_trust_layer.py:150-254` | If reporter becomes authenticated, string reporter breaks | Medium batch update |

**Tests that will NOT break:**
- All `TestComputeTrust` lookup tests (by name, by id, unknown agent) — no formula dependency
- All `TestAgentRegistryInit` tests — secret management unchanged
- All `TestTokenHelpers` tests — HMAC machinery unchanged
- All `TestRegister` and `TestVerify` tests — registration path unchanged
- All `TestListAgents` tests — list operation unchanged
- All `TestRecordQuery` tests — counter increment path unchanged
- All `TestEvents` and `TestPrivacyMode` tests — unrelated subsystem
- All `TestDatabaseIncidentReports` field-retrieval tests — additive schema changes don't remove existing fields

**Net assessment:** Approximately 10 of 187 tests will need updating for the full weighted scoring model. None of the breaks are complex to fix — they are semantic adjustments to test setup (accept incidents before asserting score impact) or field-count assertions.

---

## Scores

### Role-Specific Dimensions

| Dimension | Score | Justification |
|-----------|-------|---------------|
| **Feasibility** | 8/10 | The formula, DB, and registry are cleanly separated. Multi-dimensional inputs are an additive change to `compute_trust()` and the schema. The machinery to store enrichment data (`trust_metadata`) already exists and is unused. The primary feasibility constraint is the sequencing dependency: pending state must exist before the formula can safely change. |
| **Blast Radius** | 7/10 | 3 production files change (`database.py`, `agent_registry.py`, `api.py`). 10 of 187 tests break. All breaks are in the trust/incident subsystem — no cross-cutting changes. The awareness layer (scanning, processes, devices) is completely unaffected. |
| **Pattern Consistency** | 8/10 | Additive JSON to `trust_metadata` follows the exact pattern of `analytics_metadata` on `scan_snapshots`. New `incident_reports` columns follow the existing `CREATE TABLE IF NOT EXISTS` pattern. The `settings` table for weight versioning follows the existing privacy mode / HMAC secret pattern. Formula reads from a query instead of a field — consistent with how `compute_trust()` already calls `get_agent_by_name()`. |
| **Dependency Risk** | 7/10 | The formula change depends on pending state being implemented first (otherwise the formula reads zero accepted incidents). Reporter auth depends on the interaction log table being built first. Soft-delete depends on the partial-index uniqueness solution being designed. These dependencies are sequential but not circular. Pure stdlib Python + sqlite3 means no external library risk. |

### Shared Dimensions

| Dimension | Score | Justification |
|-----------|-------|---------------|
| **Overall Risk** | 7/10 | The formula is the trust product's core value proposition. Changing its inputs while maintaining its math is lower risk than replacing the formula. The 10 breaking tests are all in the domain being changed — no surprises in unrelated subsystems. The primary risk is the data migration: `incident_reports` rows created before the status/formula_weight columns will need backward-compatible handling. |
| **Reversibility** | 6/10 | New schema columns with defaults are easy to add and can be ignored by old code. But once `compute_trust()` reads from `incident_reports WHERE status='accepted'` instead of the aggregate counter, reverting requires restoring the counter-based path AND ensuring the counter matches reality. The soft-delete change is harder to reverse (hard-deleted rows can't be restored). Range is 3/10 (soft-delete) to 9/10 (adding trust_metadata enrichment only). |
| **Evidence Confidence** | 9/10 | All claims reference specific file lines, verified by direct file reads and Grep. Test counts verified by running `pytest --collect-only`. The "trust_metadata is never written" claim was confirmed by Grep across all .py files. The "incidents counter increments immediately" claim was verified at `agent_registry.py` line 464 and `database.py` line 313. No speculation. |

**Overall Internal Confidence:** 8/10 — The codebase can absorb a weighted scoring model cleanly. The architecture supports it. The test surface is contained. The sequencing dependencies (pending state first, then reporter auth, then formula weighting) are clear and implementable in order. The one structural risk is the soft-delete/re-registration name conflict, which is a semantic design decision that needs to be made before implementation begins.

---

## Critical Findings for Council

### Finding 1: `trust_metadata` is ready now — use it immediately

The `update_trust_metadata()` method exists, works, and is called from zero places. Every interaction that passes through the system without populating this column is wasted signal. Before any formula change, start writing velocity data, query type breakdowns, and reporter concentration flags to `trust_metadata`. This unblocks dimension weighting without requiring any formula change.

**File:** `database.py` line 338, `agent_registry.py` line ~363 (after `compute_trust()`)

### Finding 2: The formula's true blast radius is 3 tests, not the formula itself

The formula is 3 lines. The blast radius of changing what it reads (counters → accepted incidents) is 5 tests in `test_trust_layer.py`. These tests are mechanical to update — they need to include an "accept this incident" step before asserting score impact. This is not a technical blocker; it is a test maintenance task.

### Finding 3: The `incidents` counter is a liability in disguise

The aggregate `incidents` counter on `agent_registry` was built to make `compute_trust()` fast (one integer field read). But it makes the pending state model impossible to implement without decoupling the counter from the formula. The transition path is: keep the counter as a cache/audit field, have `compute_trust()` read from `incident_reports` directly. Two writes happen on incident acceptance: counter increments AND formula reads the table. Eventually the counter becomes redundant and can be dropped.

### Finding 4: Soft-delete has a naming collision problem

`test_trust_layer.py` line 281 tests "deregister then re-register same name." With soft-delete, the deregistered record still occupies the unique name slot. SQLite does not support partial unique indexes natively. The solution options are: (a) application-level uniqueness check (`WHERE status='active'`), removing the DB-level unique index, (b) append a suffix to the deregistered name (e.g., `recycled-bot__deregistered_1709000000`), (c) prohibit re-registration with a deregistered name (credit bureau model: you can't un-create the record). The prior council's recommendation — "re-registration with same name inherits history" — requires option (a). This is a design decision that changes existing behavior and breaks a current test by intent.

### Finding 5: The `weight_version` belongs in the API response from day one

Adding `weight_version` to `compute_trust()` output requires changing exactly one test (the exact-key assertion). But NOT having it means brands will receive scores with no provenance when weights change. The settings table can store the version. The cost of adding this now is 5 minutes. The cost of retrofitting it after brands start consuming scores is an API contract change.

---

## Appendix: Dependency Chain for Weighted Scoring (by build prerequisite)

```
1. trust_metadata enrichment (no prerequisites, do now)
   ↓
2. Soft-delete for agent_registry (prerequisite for history preservation)
   ↓
3. Pending state on incident_reports + expires_at (prerequisite for formula change)
   ↓
4. compute_trust() reads accepted incidents (requires #3)
   ↓
5. formula_weight per incident (requires #3)
   ↓
6. severity classification for incidents (requires #3)
   ↓
7. interaction_logs table with UUIDs (prerequisite for reporter auth)
   ↓
8. reporter_agent_id FK on incident_reports + auth on POST /api/incidents/report (requires #2 + #7)
   ↓
9. Reporter credibility as scoring dimension (requires #8)
   ↓
10. Weight versioning in settings + weight_version in API response (can be done at any point after #4)
```

Steps 1-6 deliver weighted scoring without reporter credibility. Steps 7-9 add the reporter credibility dimension. Step 10 is pure infrastructure for transparency.
