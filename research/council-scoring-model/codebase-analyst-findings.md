# Codebase Analyst Findings: Scoring Model
## Research Council — Submantle
## Date: 2026-03-12
## Analyst: Codebase Analyst (Claude Sonnet 4.6)

---

## 1. What Exists Now — Complete Map

### Data Flow: Interaction → Score

```
Agent API call
  → api.py: _extract_token() reads Authorization header
  → api.py: _registry.record_query(token) [only if token present]
    → agent_registry.py: verify(token) — token hash lookup + HMAC re-derivation
    → database.py: increment_agent_queries(agent_id) — total_queries += 1
    → database.py: update_agent_last_seen(agent_id)

Third-party incident report
  → api.py POST /api/incidents/report (IncidentReportRequest)
    → agent_registry.py: record_incident(agent_name, reporter, incident_type, description)
      → database.py: increment_agent_incidents(agent_id) — incidents += 1
      → database.py: save_incident_report(agent_id, agent_name, reporter, incident_type, description)
      → event_bus.emit("INCIDENT_REPORTED")

Score computation (read-only, called on demand)
  → api.py GET /api/verify/{agent_name}
    → agent_registry.py: compute_trust(agent_name)
      → database.py: get_agent_by_name(agent_name)
      → formula: (total_queries + 1) / (total_queries + incidents + 2)
      → returns dict: agent_name, trust_score, total_queries, incidents,
                      registration_time, last_seen, version, author
```

### Functions Involved in Trust Scoring

| Location | Function | Role |
|----------|----------|------|
| `agent_registry.py` | `compute_trust(agent_name, agent_id)` | Applies Beta formula, returns score dict |
| `agent_registry.py` | `record_query(token)` | Verifies token, increments total_queries |
| `agent_registry.py` | `record_incident(agent_name, reporter, incident_type, description)` | Validates, increments incidents, saves report, emits event |
| `database.py` | `increment_agent_queries(agent_id)` | SQL: total_queries += 1 + updates last_seen |
| `database.py` | `increment_agent_incidents(agent_id)` | SQL: incidents += 1 |
| `database.py` | `save_incident_report(...)` | Inserts row in incident_reports |
| `database.py` | `get_incident_reports(agent_id, limit)` | Read: returns reports newest-first |
| `database.py` | `update_trust_metadata(agent_id, trust_metadata)` | Write to JSON blob — called by nothing currently |

### Table Columns Involved

**agent_registry table:**
- `total_queries` INTEGER DEFAULT 0 — positive signal for Beta formula
- `incidents` INTEGER DEFAULT 0 — negative signal for Beta formula
- `trust_metadata` TEXT DEFAULT NULL — JSON blob, unused
- `last_seen` REAL — touched on every query, returned in score dict
- `registration_time` TEXT — returned in score dict, also anchors HMAC token

**incident_reports table:**
- `id`, `agent_id` (FK), `agent_name`, `reporter`, `incident_type`, `description`, `timestamp`

### API Endpoints Touching Trust

| Endpoint | Method | Trust Role |
|----------|--------|-----------|
| `GET /api/query` | Read + optional write | Calls record_query() if Bearer token present |
| `GET /api/verify/{agent_name}` | Read | Returns compute_trust() result |
| `GET /api/verify` | Read | Returns compute_trust() for all agents |
| `POST /api/incidents/report` | Write | Calls record_incident() |

---

## 2. Blast Radius of Enriching the Scoring Model

### If We Add Interaction Types (e.g., "query" vs. "deep scan request" vs. "write operation")

**What changes:**
- `record_query()` in agent_registry.py needs an `interaction_type` parameter
- `increment_agent_queries()` in database.py would need to store the type somewhere (trust_metadata JSON is the natural home)
- The formula in `compute_trust()` would need to weight by type
- The `IncidentReportRequest` Pydantic model in api.py is unaffected
- The `/api/query` endpoint would need to pass interaction type context

**What breaks:**
- `test_trust_layer.py` has 8 tests in `TestComputeTrust` and 8 in `TestRecordIncident` that assume flat query counting. Adding weights without changing the formula leaves tests green; changing the formula breaks `test_compute_trust_formula_correctness` (hardcoded 11/14 assertion at line 98).
- Any agent that has accumulated a score under the old formula gets a different score under new weights retroactively. There is no migration path for historical data because interaction type was never recorded.

**Verdict:** Adding interaction types without historical data is a forward-only change. Old queries remain equal-weight forever unless you store type on each event.

### If We Add Counterparty Ratings (agents rate each other or rate businesses)

**What changes:**
- New table needed (no existing schema supports this)
- A new DB method, a new registry method, a new API endpoint
- The formula in compute_trust() would need a third Beta parameter or a composite score

**What breaks:**
- Nothing in existing tests would break — this is purely additive
- The formula change IS a blast: compute_trust() is called in 8 test cases with exact score assertions

**Verdict:** Schema is additive; formula change has targeted blast. Manageable.

### If We Add Weighted Scoring (some incident types count more)

**What changes:**
- `compute_trust()` formula must change
- `increment_agent_incidents()` needs severity stored somewhere
- incident_reports needs a `severity` or `weight` column (schema migration)

**What breaks:**
- `test_compute_trust_formula_correctness` (line 85): hardcoded exact formula assertion breaks immediately
- All existing incident_reports rows lack severity — retroactive weighting is undefined

**Verdict:** The formula test is the only direct blast. Two-line fix. Schema migration for incident_reports is the bigger concern on a live DB.

---

## 3. The trust_metadata JSON Column

**Current state:** Column exists in schema (line 570 in database.py), `update_trust_metadata()` method exists (line 338), `_row_to_agent()` deserializes it (line 644). Nothing writes to it. Nothing reads it in the scoring path.

**What it could hold without changing the formula:**
```json
{
  "interaction_breakdown": {"query": 45, "deep_scan": 12, "write": 3},
  "incident_breakdown": {"policy_violation": 2, "unauthorized_access": 1},
  "reporter_ids": ["brand-acme", "brand-xyz"],
  "velocity_flags": {"queries_last_hour": 120, "flagged": true},
  "registration_age_days": 14,
  "score_history": [{"timestamp": 1741000000, "score": 0.72}, ...]
}
```

**Implications of using it:**
1. **No schema migration required** — column already exists on every device
2. **Read/write path must be added to compute_trust() and record_query()** — currently neither touches it
3. **Atomic update risk**: `increment_agent_queries()` and `update_trust_metadata()` are two separate SQL statements. Under concurrent load (WAL mode handles reads, but writes serialize), a race condition could make the JSON stale relative to the counters. This must be either a single transaction or the JSON must be treated as a cache, recomputed from authoritative counters.
4. **JSON is not queryable in SQLite without json_extract()** — if anti-gaming rules need to COUNT reporters or check velocity, raw SQL against trust_metadata is awkward. Separate columns or a separate table are cleaner for anything that needs filtering.
5. **Size risk**: score_history would grow unboundedly. Needs a max-entries cap.

**Recommendation for the council:** Use trust_metadata for display-only enrichment (breakdown, history cache). Never use it as the authoritative input to the formula — counters stay authoritative.

---

## 4. The incident_reports Table — Credit Bureau Model Adequacy

**Current schema:**
```sql
id, agent_id (FK), agent_name, reporter, incident_type, description, timestamp
```

**What's present:**
- Attribution (reporter field) — credit bureau model requires this. Present. ✓
- Incident taxonomy (incident_type free text) — present but uncontrolled. ✓/✗
- Audit trail (timestamp) — present. ✓
- Description (free text) — present. ✓

**What's missing for a real credit bureau model:**

| Missing Field | Why It Matters | Credit Bureau Analog |
|---------------|----------------|---------------------|
| `reporter_verified` BOOLEAN | Anyone can POST an incident. Is the reporter a registered business? | Bureaus only accept reports from credentialed furnishers (banks, lenders) |
| `severity` or `weight` INTEGER | All incidents equal today. A failed captcha ≠ data exfiltration. | Different derogatory marks have different FICO score impact |
| `evidence_hash` TEXT | No link between the claim and any supporting data. | Bureaus require documentation |
| `status` (pending/accepted/disputed/resolved) | No dispute or resolution workflow. | FCRA requires dispute handling |
| `source_ip` or `source_agent_id` | Can't detect one reporter spamming incidents. | Furnisher audit logs |
| `incident_id` (external, reporter-assigned) | No way for reporter to reference their own records. | Tradeline ID |
| `normalized_incident_type` | incident_type is free text — "policy_violation" and "PolicyViolation" are two different types in queries. | Bureaus have a fixed taxonomy of account status codes |

**Most critical gap:** There is no reporter authentication at the API layer. `POST /api/incidents/report` accepts any string as the `reporter` field. A bad actor could spam incidents against a competitor by calling the endpoint anonymously.

---

## 5. Anti-Gaming — Current State and Gaps

**What exists today:**
- `UNIQUE INDEX idx_agent_registry_name` — prevents two registrations with the same name
- `UNIQUE` on `token_hash` — prevents token collision
- `FOREIGN KEY (agent_id) REFERENCES agent_registry(id)` — orphan incident reports impossible

**What is completely absent:**

### The Friendly Business Attack
An agent registers. The agent's owner also registers a business reporter. The business POSTs to `/api/incidents/report` about *competitor* agents to lower their scores, or — more cleverly — the agent queries Submantle from many IP addresses to inflate its own `total_queries`.

**Specific vectors:**

| Attack | Current Defense | Gap |
|--------|-----------------|-----|
| Self-spam: Agent calls `/api/query` in a loop | None | No rate limit, no velocity cap on queries per hour |
| Sybil queries: Same agent under different IPs | None | query count is per-agent, not per-IP or per-session |
| Reporter spam: One business reports many incidents against competitors | None | POST /api/incidents/report has no auth, no rate limit |
| Fake reporter: Registering "AcmeBank" as reporter when you're not Acme | None | reporter is free text |
| Fresh deregister/reregister: Reset score by deleting and re-registering | Partially mitigated: score resets to 0.5 (clean slate, not higher) | Score reset IS a form of gaming for agents with low scores |
| Query diversity gaming: Same query endpoint called 1000 times | None | All calls to /api/query count equally |

**DB-level constraints that could help but don't exist:**
- No `reporter_id` foreign key linking reporters to verified accounts
- No `rate_limit` table or last_report_time per reporter
- No max_incidents_per_reporter_per_day logic
- No UNIQUE constraint preventing same reporter/agent_name/incident_type combination within a time window

**The deregister/reregister gap** is worth highlighting separately: `deregister_agent()` does a hard DELETE (line 323 database.py). All history — queries, incidents — is gone. A low-scoring agent can wipe its record. The incident_reports rows remain (FK constraint doesn't CASCADE DELETE), but `total_queries` and `incidents` on the new registration start at zero. This breaks the credit bureau model's core premise that history persists.

---

## 6. The Enforcement Question — Codebase Perspective

### What deregister() Does Today
`AgentRegistry.deregister(token)` in agent_registry.py (line 304):
1. Verifies the token belongs to the calling agent
2. Calls `database.py: deregister_agent(agent_id)` — hard DELETE from agent_registry
3. Emits `AGENT_DEREGISTERED` event

**Critical constraint:** Only the agent itself can deregister — the token must match. There is no admin-initiated deregistration endpoint. No one can remove an agent from outside.

### What Breaks if Submantle Needed to Force-Remove an Agent

Nothing in the current codebase would break architecturally — the DB operation is a simple DELETE. But the following gaps would need to be filled:

1. **No admin authentication** — there is no admin token, admin role, or privileged endpoint. Any force-remove endpoint would need to be built from scratch and secured carefully.
2. **No blacklist mechanism** — after deletion, the same agent could immediately re-register under the same name (the UNIQUE index would allow it since the row is gone). A blacklist table would be needed to prevent this.
3. **No historical record of forced removal** — the incident_reports rows survive the DELETE (FK without CASCADE), but the agent record itself is gone. Future score queries would return 404. The incident history becomes orphaned — reportable to nobody.
4. **Event bus** — AGENT_DEREGISTERED would fire, but no subscriber currently acts on it. A blacklist subscriber would need to be added.

### Is deregister() Sufficient or Does It Need to Be More Aggressive?

For voluntary self-removal: sufficient.

For the enforcement scenario (removing a harmful agent without their cooperation): insufficient. It requires:
- An `agent_status` column (active / suspended / blacklisted) rather than hard deletion
- A privileged deactivation endpoint that sets status rather than deleting
- The verify() path checking status before returning agent info
- A blacklist of agent names that cannot re-register

**But this is an enforcement mechanism**, which violates Design Principle 4: "Always aware, never acting." The council must decide whether a "suspend" capability counts as enforcement or as record-keeping. The codebase makes no architectural decision here — it simply has no such feature.

**One distinction worth raising for the council:** Visa does have a mechanism to revoke a merchant's processing capability. They don't "act" on individual transactions, but they do maintain a MATCH list (Member Alert to Control High-Risk Merchants). That's not transaction enforcement — it's list maintenance. Submantle maintaining a "revoked agents" list could be analogous — publishing that an agent has been formally revoked, while leaving actual blocking to the brand/platform.

---

## Scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| **Feasibility** (of enriching scoring) | 8/10 | Formula, DB, and registry are cleanly separated. Changes are localized. |
| **Blast Radius** (10 = minimal) | 7/10 | Formula change breaks one exact-assertion test. Schema migration for new columns needed on live DB. trust_metadata is already there. |
| **Pattern Consistency** | 8/10 | Additive changes (new incident fields, trust_metadata use) fit the existing pattern well. |
| **Reversibility** | 6/10 | Formula changes affect all historical scores immediately — no snapshot of what scores "used to be." score_history in trust_metadata could address this. |
| **Dependency Risk** (10 = none) | 9/10 | No external dependencies. All trust code is stdlib Python + sqlite3. Changes are fully self-contained. |

---

## Summary for Council

**The infrastructure is solid and deliberately minimal.** The Beta formula, DB counters, and incident intake are clean and well-separated. The test suite covers the core formula correctly.

**The three gaps that matter most for a real scoring model:**

1. **Reporter authentication is absent.** Anyone can report anything. This is the single biggest gaming surface and the biggest deviation from the actual credit bureau model (which requires credentialed furnishers).

2. **Deregister wipes history.** Hard DELETE means a low-scoring agent can reset to 0.5. The credit bureau model requires permanent records. This is a fundamental schema decision: soft-delete with status field, or keep the hard-delete and accept that re-registration is a legitimate fresh start.

3. **All queries count equally.** This is by design for now, but as the product matures, the council needs to decide whether a "read the process list" query and a "deep scan of what would break" query should have different trust signal weight. trust_metadata can hold this breakdown without changing the formula.

**The trust_metadata column is a free upgrade.** It exists, has a write method, and needs zero migration. Storing interaction breakdown, score history, and velocity flags there gives the product richer data for V2 without touching the core formula today.
