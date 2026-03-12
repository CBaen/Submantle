# Research Brief: Trust Lifecycle Design
## Date: 2026-03-12
## Project: Submantle

### Problem Statement
Submantle is the credit bureau for AI agents. We need to design the complete trust lifecycle — from first registration through sandbox testing, live interactions, incident review, probation, and recovery. The core constraint: Submantle NEVER acts, never blocks, never enforces. It labels. Brands and agents make their own decisions based on those labels.

### Expected Outcome
A complete trust lifecycle design covering:
- What status labels entities carry and what they communicate
- How new users can test their agents without score impact (sandbox)
- How incident reports are processed (automated vs human review tiers)
- How entities recover from incidents and probation (fairness mechanisms)
- What metadata accompanies each interaction and how it's presented to both technical and non-technical audiences

The designs must be implementable by a solo founder in Python (prototype stage) and must work with the existing Beta Reputation formula: trust = (queries + 1) / (queries + incidents + 2).

### Current State

**What exists:**
- SQLite database with agent_registry, incident_reports, scan_snapshots tables
- Agent registration with cryptographic token (HMAC-SHA256)
- Trust scoring via `compute_trust()` — pure Beta formula
- `record_query()` incrementing total_queries counter
- `incident_reports` table with plain-text reporter field (NO authentication)
- `trust_metadata TEXT` column exists on agent_registry but is NEVER written to
- Privacy mode, event bus, process awareness all working
- 160 tests passing across 4 test files
- Dashboard at localhost:8421

**What does NOT exist:**
- No interaction logging table (only aggregate counters)
- No interaction IDs or UUIDs
- No reporter authentication (anyone can file with any string)
- No pending state on incidents (immediate formula impact)
- No velocity caps on queries
- No status labels beyond what the trust score implies
- No sandbox/testing mode
- No review workflow
- No MCP server (being built in parallel)

### Project Direction
Trust bureau + MCP server is the V1 wedge. Dashboard follows when customers demand it. The immediate build sequence after this expedition: soft-delete deregistration, interaction logging table, reporter auth + pending state + velocity caps, MCP server (parallel), business API keys + Stripe Payment Links. This expedition's findings will inform the design of items 11-12 on the build priority (sandbox/testing mode, status labels + review workflow).

### Constraints

**NON-CHALLENGEABLE — Settled Decisions (2026-03-12):**

1. **eBay Model for Incident Reporting (SETTLED):** Only registered Submantle members can file incident reports. Must reference a valid interaction ID (proves the parties actually interacted). Both parties get interaction logs. Submantle retains neutral logs for verification. Reports require: auth token + interaction ID + evidence. Submantle analyzes reporter history and agent history to contextualize grievances. System surfaces patterns to help resolve, not just punish. Unintentional issues become actionable feedback, not just score hits.

2. **Labels, Not Enforcement (SETTLED):** Submantle publishes status labels ("New," "Active," "Under Review," "Probationary"). Submantle does NOT enforce these — brands decide whether to interact with under-review agents. A brand denying an under-review agent is itself an interaction that gets logged. That denial/approval generates trust data for BOTH parties. This is consistent with "always aware, never acting" principle.

3. **Pending State on Incidents (SETTLED):** Incidents enter PENDING state before affecting score — review period required. Tiered review: automated for clear patterns (10K self-pings), human for ambiguous cases.

4. **Fairness Principle (SETTLED):** Users should not be permanently damaged by early mistakes. Not everyone builds their own agents. Not everyone is malicious. Sandbox and probation enable recovery.

5. **Interaction Metadata (SETTLED):** Logs include frequency, outcome, technical interpretation, AND layman interpretation. System tracks inflation attempts as a signal (not just blocks them).

**Design Principles (INVIOLABLE):**
- No ML. All review, classification, and pattern detection must be deterministic.
- Submantle never acts. Labels and status are information, not enforcement.
- Solo founder building V1. Complexity is the enemy.
- Credit bureau model. Third-party reports, not self-detection.
- Must work with the Beta Reputation formula: trust = (queries + 1) / (queries + incidents + 2)
- Everything must be auditable and transparent to the entity being scored.
- Privacy by architecture. On-device computation. No telemetry of interaction content.
- Deterministic scoring only — keeps Submantle outside EU AI Act scope permanently.

### Destructive Boundaries
- Do NOT suggest ML-based classification, anomaly detection, or pattern inference
- Do NOT suggest Submantle blocking, gating, or throttling any entity
- Do NOT redesign the Beta Reputation formula itself (research how labels/states interact with it)
- Do NOT suggest blockchain dependencies
- Do NOT suggest mobile-first approaches (desktop/laptop only for V1)
- Do NOT challenge the eBay model, pending state, or labels-not-enforcement decisions — they are SETTLED

### Research Angles

**Team 1: Status Labels and What They Communicate**
What labels/statuses should a registered entity carry? "New," "Active," "Under Review," "Probationary," "Suspended" — what do these look like in credit bureaus, app stores, DNS registrars, and certificate authorities? How do labels get applied and removed? What information accompanies each label so brands can make informed decisions? Key constraint: Submantle publishes the label but doesn't enforce it. Research how neutral infrastructure platforms communicate risk without acting on it.

**Team 2: Sandbox and Testing Environments in Trust Systems**
Do any reputation/trust platforms offer a "practice mode"? How do competitive gaming systems handle placement matches? How do credit bureaus handle "authorized user" or "secured card" pathways that let people build credit safely? Submantle wants a sandbox where users can test their agents — simulate interactions, see speed, find errors — without affecting their real score. How should sandbox interactions be labeled so they're clearly distinct from live interactions? Can sandbox performance metrics be visible to brands as "test results" without being "trust score"?

**Team 3: Review Tiers and Incident Processing**
When an incident report is filed, how should it be processed? Research: automated vs human review tiers in content moderation (YouTube, Airbnb, eBay), dispute resolution timelines, what triggers escalation from auto to human. For Submantle specifically: self-ping detection (10,000 identical queries = automated handling), duplicate incident deduplication (same bug reported 100 times = one incident), severity classification (deterministic rules, NO ML). What does the review workflow look like? How long should pending last? What constitutes "resolved"?

**Team 4: Fairness, Recovery, and Probation Mechanisms**
How do credit bureaus handle rehabilitation? FCRA 7-year rule, goodwill adjustments, rapid rescoring. How does eBay handle seller probation? How do app stores handle app suspension and reinstatement? Submantle's fairness principle: users shouldn't be permanently damaged by early mistakes. What probation mechanisms exist that (a) protect the ecosystem from bad actors while (b) giving honest actors a path back? How do status labels change during probation? Can an interaction with an "under review" or "probationary" agent generate data that helps both parties?

**Team 5: Interaction Metadata — What Gets Recorded and How It's Presented**
What metadata do credit reports, eBay transaction histories, and API audit logs actually contain? Submantle needs both a technical interpretation ("HTTP 504 Gateway Timeout after 30s on /api/payment/confirm") and a layman interpretation ("This agent's payment confirmation timed out — it took too long to respond"). How do existing platforms present interaction history to technical and non-technical audiences? What about the specific scenario: an under-review agent tries to interact with a brand, the brand denies access — that denial is itself an interaction. Does it affect scores? How is it recorded?

### Team Size: 5
Five distinct research angles covering status communication, sandbox design, review workflow, fairness/recovery, and interaction metadata. Each angle is independent and requires different domain expertise (credit bureaus, gaming systems, content moderation, legal frameworks, UX/data presentation).

### Codebase Files for Analysis
All teams should read these files for codebase context:
- `C:\Users\baenb\projects\submantle\VISION.md` — CURRENT product vision (updated 2026-03-12 with bidirectional trust, Experian model). READ THIS FIRST.
- `C:\Users\baenb\projects\submantle\CLAUDE.md` — Project rules and design principles
- `C:\Users\baenb\projects\submantle\prototype\database.py` — Current schema and persistence patterns
- `C:\Users\baenb\projects\submantle\prototype\api.py` — Current API endpoints and trust scoring
- `C:\Users\baenb\projects\submantle\prototype\agent_registry.py` — Agent registration and token management
- `C:\Users\baenb\projects\submantle\research\council-product-market-fit-v2\plan-deepen-notes.md` — Implementation research on reporter auth, interaction logging, MCP server

### Failed Approaches
- Prior research agents got opinionated over stale VISION.md data. The VISION.md was updated 2026-03-12 to reflect the strategic pivot. Ensure all research reflects the CURRENT state.
- ML-based approaches have been repeatedly proposed and rejected. The constraint is absolute: deterministic only.
- Enforcement-based approaches (blocking, gating, throttling by Submantle) violate the core design principle. Submantle labels; it never acts.

### Anti-Gaming Analysis Required
Each team must include anti-gaming analysis for whatever mechanism they propose. If you design a sandbox, how can it be gamed? If you design a review tier, how can it be abused? If you design a recovery mechanism, how can bad actors exploit it? Deterministic countermeasures only.
