# Research Council Brief: Weights and Measures — The Scoring Model Evolution
## Date: 2026-03-12
## Project: Submantle

### The Question
The Beta Reputation formula (trust = (q+1)/(q+i+2)) treats every interaction as equal and every incident as equal. But they're not. A data exfiltration incident is not a timeout. A report from a brand with 5,000 interactions carries more weight than one from a brand registered yesterday. An agent with 10,000 successful interactions and 1 incident is different from one with 10 interactions and 1 incident. What dimensions should Submantle track, how should they be weighted, and how should those weights compose into a score that brands can use for real decisions — while remaining fully deterministic, fully explainable, and outside EU AI Act scope?

### Context: What the Prior Council Settled (NON-CHALLENGEABLE)
The first scoring council (2026-03-12, `research/council-scoring-model/`) established:
1. **Single universal score is correct for V1** (triple convergence, Klout failure case)
2. **The Beta formula math is sound; the inputs are the problem** (triple convergence)
3. **Record interaction types now, weight them later** (consensus after challenge round)
4. **trust_metadata is the right home for enrichment data** (double convergence)
5. **Unauthenticated reporting is the critical vulnerability** (triple convergence) — NOW SOLVED by eBay model (settled 2026-03-12)
6. **Deregister must become soft-delete** (triple convergence)

### What Changed Since the Prior Council
- **eBay model for incident reporting** (settled): Only registered members report, must reference interaction IDs, three-sided logs
- **Interaction logging with UUIDs** (settled design): Two rows per interaction with shared UUID, perspective column
- **Review tiers** (from expedition Team 3): Five incident states (suspicious → pending → accepted/expired/disputed), severity classification, deduplication via fingerprint rules, corroboration counts
- **Reporter credibility** (emerged): A reporter's own trust score and accuracy history should weight their reports
- **Corroboration concept** (new): Multiple reporters on same incident = 1 score hit but higher confidence signal
- **GL's insight**: The audience for this score is machines and dashboards, not humans reading a number. Full complexity is acceptable if it's deterministic and explainable. Weights WILL evolve over time — versioned, documented, transparent.

### Expected Outcome
A scoring model design that:
1. Identifies the minimum set of weighted dimensions that produce a meaningful score
2. Defines how those dimensions compose (additive? multiplicative? layered?)
3. Specifies what data feeds each dimension
4. Remains 100% deterministic (pure math, no ML)
5. Is fully explainable — any brand can see exactly why a score is what it is
6. Accounts for: incident type severity, reporter credibility, interaction volume/diversity, agent history depth, corroboration strength
7. Can evolve (versioned weight updates) without breaking existing scores

### Project Fingerprint
- Runtime: Python 3.x (prototype), Go (future production)
- Database: SQLite with WAL mode, JSON columns for structured data
- Current formula: `trust = (total_queries + 1) / (total_queries + incidents + 2)` — Beta Reputation
- Current schema: agent_registry (total_queries, incidents, trust_metadata), incident_reports (agent_id, reporter, incident_type, description, timestamp)
- Planned additions: interaction_logs table with UUIDs, status/severity/dedup on incident_reports, reporter_agent_id FK
- Constraints: No ML, no blockchain, deterministic only, EU AI Act exempt, credit bureau model
- Design principles: Always aware never acting, privacy by architecture, labels not enforcement

### Constraints
- The Beta formula stays as the foundation/skeleton — this council designs what feeds into it and how
- No ML-based scoring, anomaly detection, or pattern inference
- Single universal score for V1 — NOT category-specific scores (settled by prior council)
- Must work for a solo founder building V1 in Python
- Weights must be versioned and transparent — any entity can see why their score is what it is
- The score is consumed by machines (AI agents) and displayed on dashboards — full complexity is acceptable

### Destructive Boundaries
- Do NOT propose replacing the Beta formula with something incompatible
- Do NOT propose ML-based weighting or classification
- Do NOT propose category-specific scores for V1
- Do NOT re-litigate settled decisions from the prior council

### Codebase Files for Analysis
- `C:\Users\baenb\projects\submantle\VISION.md` — Current product vision
- `C:\Users\baenb\projects\submantle\CLAUDE.md` — Design principles and constraints
- `C:\Users\baenb\projects\submantle\prototype\database.py` — Current schema
- `C:\Users\baenb\projects\submantle\prototype\agent_registry.py` — Current trust computation (compute_trust method)
- `C:\Users\baenb\projects\submantle\research\council-scoring-model\synthesis.md` — Prior council findings
- `C:\Users\baenb\projects\submantle\research\expedition-trust-lifecycle\team-3-review-tiers-findings.md` — Review tier design with severity, dedup, corroboration
- `C:\Users\baenb\projects\submantle\research\council-product-market-fit-v2\plan-deepen-notes.md` — Implementation research

### External Research Angles
1. How do FICO, VantageScore, and D&B PAYDEX actually compose weighted dimensions? What are the category breakdowns and how are weights calibrated?
2. How do reputation systems that evolved from simple to complex (eBay, Uber, Airbnb) handle weight versioning and score migration?
3. What deterministic composite scoring models exist in fintech, insurance, or cybersecurity that could inform Submantle's approach?
