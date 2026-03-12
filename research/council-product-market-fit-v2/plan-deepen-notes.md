# Plan Deepen — Research Notes
## Date: 2026-03-12
## Subject: V1 Build Sequence (Reporter Auth → MCP Server → Business Auth/Billing)
## Source: 5 parallel research agents against current codebase + external docs

---

## Section 1: Interaction Logging Architecture

### Edge Cases
- **No interaction log exists.** Currently interactions are tracked only as aggregate counters (`total_queries INTEGER`). Building the three-sided log requires a new table, new write paths, and a decision about schema design.
- **Storage growth at scale:** 1,000 agents × 100 interactions/day × 3 perspective rows × 300 bytes = ~90 MB/day. SQLite degrades past ~1 GB for frequent writes. Need a pruning strategy from day one (pattern already exists: `prune_scan_history()` and `prune_events()`).
- **WAL mode write contention:** Not a problem at prototype scale. One writer at a time, millisecond blocking. The existing per-operation connection pattern is correct under WAL.

### Existing Patterns
- Schema defined in `_SCHEMA` string in database.py — idempotent `CREATE TABLE IF NOT EXISTS`
- Each table gets `save_*()`, `get_*()`, `list_*()`, `prune_*()` companion methods
- Tests use `:memory:` SQLite — new `TestInteractionLogs` class slots in cleanly
- `trust_metadata TEXT` column on agent_registry exists but is **never written to** — free storage slot for pattern data

### Risks
- The `pass` in scan snapshot writes (api.py line 111) silently swallows DB errors. Must NOT be copied for interaction logs — these are the core product.
- `total_queries` counter vs `COUNT(*)` on interaction log: both can coexist during transition. Counter stays for cheap trust formula; log provides detail.
- `FOREIGN KEY` on incident_reports has no `ON DELETE CASCADE`. Deregistration orphans records. Credit bureau model argues for preservation (soft-delete).

### Recommendation
**Two rows per interaction with shared UUID** is the recommended schema pattern. `interaction_id` is the join key; `perspective` column (`'agent'` / `'counterparty'` / `'submantle'`) is the filter key. `party_b_id` should be TEXT (not FK) for the prototype to support unregistered counterparties, with a migration note.

---

## Section 2: Reporter Authentication via Interaction IDs

### Edge Cases
- **No interactions table exists.** The plan assumes interaction IDs exist to reference. They don't. This is a prerequisite dependency — interaction logging must be built BEFORE interaction-ID-based reporting.
- **Interaction IDs are cheap to manufacture.** Free registration + free queries = cheap interaction IDs. The gate is necessary but not sufficient alone. Needs velocity caps + reporter reputation + registration age minimums.
- **One incident per interaction ID** — or can an interaction generate multiple reports? Recommend: unique constraint on `(interaction_id, reporter_agent_id)`.
- **Hard DELETE on deregister** means a bad-actor reporter can erase their record after filing reports. Soft-delete must come before or alongside reporter auth.

### Existing Patterns
- `verify(token)` infrastructure is fully built and working. Adding bearer token verification to the incident endpoint is a small additive change — pattern already in `DELETE /api/agents/{agent_id}`.
- `_extract_token()` helper at api.py line 339 is generic and reusable.

### Risks
- **Schema migration on incident_reports needed:** Adding `reporter_agent_id INTEGER NOT NULL` as FK. Existing rows have no reporter agent ID — migration strategy required.
- **Coordinated attack:** Register 100 fake agents, interact with target, file 100 reports. Mitigation: reporter reputation scoring (track false report rate), minimum reporter age, minimum reporter trust score to file reports that affect the formula at full weight.

### Recommendation
Build in this order: (1) interaction logging table with UUIDs, (2) soft-delete for deregistration, (3) reporter auth requiring bearer token + valid interaction ID, (4) velocity caps on report filing. The eBay model is correct — Submantle must be the authoritative source of "did this interaction happen," not either party.

---

## Section 3: MCP Server Design

### Edge Cases
- **SDK version discrepancy:** CLAUDE.md cites "MCP Go SDK v1.4.0" but context7 shows v0.4.0–v1.2 documented. Verify before build.
- **Two viable SDKs:** Official `modelcontextprotocol/go-sdk` (Anthropic-maintained, built-in `RequireBearerToken` middleware) vs community `mark3labs/mcp-go` (higher adoption, better docs). Open decision for Go production build.
- **HTTP transport requires full OAuth 2.1** — substantial infrastructure, NOT for V1. Stdio transport requires zero OAuth.
- **Two audiences through one server:** Agents (register, record interactions) and brands (query trust scores). Different auth profiles, different rate limits. Must not design for agents only.

### Existing Patterns
- All business logic already exists as importable Python modules. MCP server is a thin wrapper, not a rewrite.
- 7 tools identified: `register_agent`, `get_trust_score`, `list_agents`, `record_interaction`, `report_incident`, `query_process_awareness`, `get_my_score`.

### Risks
- **TypeScript SDK v2 pre-alpha** — protocol-level changes will propagate to Go SDK. Track before committing Go build.
- **Tool descriptions are LLM-facing copy** — they determine when agents invoke the tools. Must be written as product copy, not API docs.
- **"Not found" vs "not registered"** — `get_trust_score("unknown")` must distinguish "no record exists" from "registered with zero history." Different meanings for brands.

### Recommendation
**V1: Python MCP server** (`prototype/mcp_server.py`) importing existing modules directly. Stdio transport. Bearer token from environment variable. No OAuth. Add `interaction_id` to the incident report schema NOW in the Python prototype — cheap to add, expensive to retrofit. Go production MCP server is a separate binary sharing `internal/` packages.

---

## Section 4: Grievance Contextualization / Pattern Detection

### Edge Cases
- **100 incidents from one bug = score destroyed.** A new agent with 0 queries and 100 reports scores 0.0097. No deduplication, no burst detection, no pending state.
- **Self-query inflation is CRITICAL.** Agent calls `/api/query` 10,000 times → score approaches 1.0 regardless of incidents. No velocity caps exist. No query diversity requirements exist.
- **`trust_metadata` column exists but is NEVER populated.** Every query that happens without updating this column is evidence thrown away.

### Existing Patterns
- `compute_trust()` is pure math on two counters. Clean, correct, extensible.
- `incident_reports` table has per-incident detail (type, reporter, timestamp) — enough for basic pattern detection via SQL GROUP BY.
- `prune_*()` methods are the established pattern for growth control.

### Deterministic Pattern Detection Available (No ML)
- Frequency analysis by incident type (GROUP BY)
- Rolling time windows (incidents last 30 days vs prior 30 days)
- Reporter concentration (if 90% of incidents from one reporter, flag it)
- Burst detection (incidents_today / daily_average > 10 = burst)
- Standard deviation outlier detection (agent at mean + 3σ)

### Risks
- **Pending state is essential.** Incidents should NOT immediately affect the formula. Add `status` column (`pending / accepted / disputed / resolved`). Only `accepted` incidents increment the counter. This alone buffers floods.
- **Atomic update race condition:** `increment_agent_queries()` and `update_trust_metadata()` are separate SQL statements. Must be a single transaction or treat JSON as a recomputed cache.

### Recommendation
Start with three deterministic safeguards: (1) pending state on incidents (buffer before formula impact), (2) velocity caps on queries (max N/hour counting toward trust), (3) reporter concentration flag (single-source reports weighted less). All pure rules. No ML. The `trust_metadata` JSON blob is the right home for pattern data before the Go rewrite.

---

## Section 5: Business Auth + Billing

### Edge Cases
- **Businesses are two things simultaneously:** A registered party with a trust score (bidirectional trust) AND a paying query customer. One account, two roles. The token model needs to handle both.
- **Free browsing vs paid API already architecturally present:** `/api/verify` (directory, all agents) vs `/api/verify/{agent_name}` (specific lookup). The pay wall belongs on the specific-agent endpoint.
- **Zuplo already flagged in HANDOFF.md** as acceleration stack option — managed API gateway that handles auth, rate limiting, metering, and developer portal. $250/month paid tier. Build-vs-buy decision.

### Existing Patterns
- HMAC-SHA256 token pattern is reusable for business keys. Same crypto, different header (`X-API-Key` vs `Authorization: Bearer`).
- `_extract_token()` helper is generic.

### Risks
- **Stripe Billing Meters are asynchronous** — can't use Stripe for real-time rate limiting. Need own counter in SQLite for enforcement; Stripe handles money.
- **The revenue model is unvalidated.** The council rated "businesses pay per-query" at 5/10 confidence. Building full billing infrastructure before a single customer conversation is the exact pattern the council warned against.

### Recommendation
**Solo founder path: start with Stripe Payment Links (prepaid credits).** No subscription code, no webhook complexity. "1,000 trust queries — $10" as a payment link. Manually issue API key + SQLite quota. Scales to ~10 customers with zero billing code. Switch to Billing Meters when real customers demand it. This is the minimum path to "I can charge someone" without engineering billing infrastructure.

---

## Critical Dependencies Discovered

The research reveals a dependency chain the council's build sequence didn't make explicit:

```
1. Soft-delete for deregistration (prerequisite for reporter auth — can't let bad actors erase records)
2. Interaction logging table with UUIDs (prerequisite for interaction-ID-based reporting)
3. Reporter auth via bearer token + interaction ID (depends on #1 and #2)
4. Pending state on incidents (prevents formula manipulation before verification)
5. Velocity caps on queries (prevents self-query inflation)
6. MCP server (wraps all of the above for agent integration)
7. Business API keys + minimal billing (Stripe Payment Links, not full billing infra)
```

Items 1-5 are prerequisites that the council sequenced as one item ("reporter authentication"). They are actually five distinct changes with dependencies between them.

---

## Contradictions with Plan Assumptions

| Assumption | Reality | Impact |
|-----------|---------|--------|
| "Reporter auth" is one task | It's 5 dependent subtasks (soft-delete → interaction log → auth → pending state → velocity caps) | Effort is 3-5x what "reporter auth" implies |
| Interaction IDs exist | No interactions table exists at all | Must build interaction logging first |
| MCP server is item #3 | Could be built in parallel with items 1-5 since it wraps existing modules | Sequencing may be too serial |
| Full billing infrastructure needed | Stripe Payment Links + manual API keys scale to ~10 customers with zero code | Can defer billing engineering significantly |
| `trust_metadata` is future work | Column exists, is never written — every query without it is wasted evidence | Should start populating immediately |
