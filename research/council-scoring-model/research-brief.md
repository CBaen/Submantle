# Research Council Brief: What Changes an Agent's Trust Score?
## Date: 2026-03-12
## Project: Submantle

### The Question
We have a working Beta Reputation formula but "queries" and "incidents" are placeholders. What interactions actually count? What data is exchanged? How do counterparties grade agents? Should Submantle ever unregister a harmful agent, or does that destroy neutrality?

### Expected Outcome
A clear scoring model that: (1) defines what interactions change a score, (2) specifies what data flows where while preserving privacy, (3) resolves the two-way grading problem (interaction outcome vs. counterparty rating), (4) takes a position on the enforcement boundary, (5) addresses anti-gaming.

### Current State
- Trust bureau prototype with 187 passing tests across 5 test files
- Beta formula: trust = (queries + 1) / (queries + incidents + 2), init 0.5
- record_query() wired — every authenticated API call increments total_queries
- record_incident() wired — third parties report incidents, increments counter
- Verification endpoint: GET /api/verify/{agent_name} returns trust score
- Incident reporting: POST /api/incidents/report (credit bureau intake)
- Agent name uniqueness enforced
- No interaction type differentiation — all queries count equally
- No counterparty rating system
- No anti-gaming rules beyond DB unique constraints

### Project Fingerprint
- Runtime: Python 3.14 + FastAPI (prototype); Go planned for production
- Key dependencies: psutil, fastapi, pydantic, uvicorn, sqlite3 (stdlib)
- Architecture: Monolithic prototype, 6 modules, SQLite WAL mode
- State: SQLite with 5 tables (scan_snapshots, agent_registry, incident_reports, events, settings)
- Database columns ready: total_queries, incidents, trust_metadata (JSON, unused)
- Known constraints: No ML (EU AI Act), no enforcement (neutral infrastructure), no blockchain, privacy by architecture, deterministic scoring only, credit bureau model
- Active boundaries: "Always aware, never acting" — Submantle never blocks, gates, or throttles

### Constraints
- No ML. Scoring must be pure deterministic math. EU AI Act compliance.
- No enforcement unless council finds compelling reason to reconsider.
- Privacy by architecture. On-device computation. No telemetry of interaction content.
- Credit bureau model. Records third-party reports, doesn't detect incidents.
- Solo founder building V1. Complexity is the enemy.
- Competitors: Signet (closest), Gen Digital, Microsoft Agent 365, Keycard, HUMAN Security

### Destructive Boundaries
- DO NOT suggest ML-based scoring or anomaly detection
- DO NOT suggest blockchain dependencies
- DO NOT suggest Submantle becoming an enforcement layer (without extremely strong justification)
- DO NOT suggest sending interaction content off-device

### Codebase Files for Analysis
- prototype/agent_registry.py — compute_trust(), record_query(), record_incident()
- prototype/database.py — schema, incident_reports table, trust_metadata column
- prototype/api.py — endpoints including /api/verify and /api/incidents/report
- prototype/events.py — EventType enum including INCIDENT_REPORTED

### External Research Angles
1. How do credit bureaus (Experian, Equifax, TransUnion), eBay, Uber, and Airbnb handle reputation scoring? What data flows, what's private, how is gaming prevented?
2. What do DNS registrars, certificate authorities, and payment networks (Visa, Mastercard) do when abuse is reported? Where is the enforcement boundary for neutral infrastructure?
3. What emerging agent trust/reputation frameworks exist as of March 2026? (IETF RATS, NIST AI RMF, Google UCP, Mastercard Verifiable Intent)
