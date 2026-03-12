# Submantle — Handoff

## What This Is
The credit bureau for AI agents. Agents register, earn trust scores through interactions, and businesses pay to check those scores. Neutral infrastructure — Submantle never acts, never enforces. It labels. Brands decide their own thresholds.

## Current State
- **Phase**: STRATEGIC PIVOT — Trust bureau + MCP server is the V1 wedge. Dashboard follows when customers demand it.
- **Git**: github.com/CBaen/SUBMANTLE (main branch)
- **Server**: `python -m uvicorn api:app --port 8421` from `prototype/` — dashboard at localhost:8421
- **Tests**: 160 passing across 4 test files (trust layer code from prior session still uncommitted — 187 tests with those changes)
- **Research**: 5 expeditions + 6 follow-ups + 3 research councils in progress. Files in `research/`.

## What Just Happened (2026-03-12)

### RESEARCH COUNCIL V2: Product-Market Fit — COMPLETE (ALL 5 PHASES)
Full deliberation: 3 agents (Codebase Analyst, External Researcher, Devil's Advocate) + challenge round + orchestrator synthesis + Tension Analyst meta-analysis.

**All files in `research/council-product-market-fit-v2/`:**
- `research-brief.md` — Approved brief with settled decisions marked non-challengeable
- `codebase-analyst-findings.md` + `codebase-analyst-challenge.md`
- `external-researcher-findings.md` + `external-researcher-challenge.md`
- `devils-advocate-findings.md` + `devils-advocate-challenge.md`
- `synthesis.md` — Full synthesis with master score table, 6 high-confidence findings
- `tension-report.md` — Meta-analysis of council's own deliberation
- `plan-deepen-notes.md` — 5-agent research on implementation details

**Council Key Findings (triple convergence):**
1. Zero customer conversations is the #1 risk — two consecutive councils agree
2. Reporter authentication is a legal ship-blocker (plain-text reporter field)
3. MCP server is the product, not a feature — without it, trust data is meaningless
4. Bidirectional trust should wait for V2 (network needs density first)
5. Trust directory is a feature, not a business
6. Moat is real only in multi-agent environments
7. Business confidence: 4.5/10. Market existence: 9/10. Capture ability: 3/10.

**Most Actionable External Finding:** Mastercard Verifiable Intent (launched March 5, 2026). SD-JWT standard. 8 enterprise partners. Explicitly excludes behavioral trust — Submantle fills the exact gap.

### MAJOR DESIGN DECISIONS MADE (2026-03-12) — ALL SETTLED

**1. Incident Reporting: eBay Model (Settled)**
- Only registered Submantle members can file incident reports
- Must reference a valid interaction ID (proves the parties actually interacted)
- Both parties get interaction logs. Submantle retains neutral logs for verification.
- Reports require: auth token + interaction ID + evidence
- Submantle analyzes reporter history and agent history to contextualize grievances
- System surfaces patterns ("consistent issue on your side") to help resolve, not just punish
- Unintentional issues become actionable feedback, not just score hits
- Decision log entry: 2026-03-12

**2. Trust System Lifecycle Design (Settled)**
- Incidents enter PENDING state before affecting score — review period required
- Tiered review: automated for clear patterns (10K self-pings), human for ambiguous cases
- Probationary periods for agents with valid incidents
- Sandbox/testing mode for new users — simulate interactions without score impact
- Users get warnings about abuse and how reviews work
- System tracks inflation attempts as a signal (not just blocks them)
- Interaction logs include: frequency, outcome, technical interpretation, AND layman interpretation
- Fairness principle: users should not be permanently damaged by early mistakes
- Decision log entry: 2026-03-12

**3. Labels, Not Enforcement (Settled)**
- Submantle publishes status labels ("New," "Active," "Under Review," "Probationary")
- Submantle does NOT enforce these — brands decide whether to interact with under-review agents
- A brand denying an under-review agent is itself an interaction that gets logged
- That denial/approval generates trust data for BOTH parties
- This is consistent with "always aware, never acting" principle

### PLAN-DEEPEN FINDINGS — "Reporter Auth" Is 5 Things

The council said "build reporter auth" as one task. Research found it's actually 5 dependent steps:
1. **Soft-delete** for deregistration (prevents record erasure by bad actors)
2. **Interaction logging table** with UUIDs (prerequisite — no interaction log exists today)
3. **Reporter auth** via bearer token + valid interaction ID
4. **Pending state** on incidents (buffer before formula impact)
5. **Velocity caps** on queries (prevents self-inflation)

MCP server can be built IN PARALLEL — it's a thin Python wrapper over existing modules. Stdio transport, no OAuth for V1.

Billing can be nearly zero code — Stripe Payment Links for first ~10 customers.

### PENDING: Trust Lifecycle Expedition — NOT YET DISPATCHED

GL approved a 5-team expedition on Trust Lifecycle Design. Context ran out before dispatch. **The next instance MUST run this expedition.**

**Topic:** `expedition-trust-lifecycle`
**Teams:** 5 (Status Labels, Sandbox/Testing, Review Tiers, Fairness/Recovery, Interaction Metadata)

**CRITICAL: The full approved expedition brief is in the conversation that produced this handoff. The next instance should:**
1. Read `research/council-product-market-fit-v2/plan-deepen-notes.md` for implementation context
2. Read `submantle-decisions.md` (search for 2026-03-12 entries) for ALL settled decisions
3. Read VISION.md for the current product vision (updated 2026-03-12 with bidirectional trust, Experian model)
4. Write the expedition research brief to `research/expedition-trust-lifecycle/research-brief.md`
5. Dispatch 5 Opus teams using `/expedition` skill
6. Include settled decisions as NON-CHALLENGEABLE constraints in the brief

**WARNING: Prior research agents got opinionated over stale VISION.md data. The VISION.md was updated 2026-03-12 to reflect the strategic pivot. Ensure all agents read the CURRENT VISION.md, not cached content.**

## What Just Happened (2026-03-11)

### STRATEGIC PIVOT SESSION — Most Consequential Session to Date
GL and Opus 4.6 conducted full product audit + 10-agent competitive expedition.

**Key Decisions Made:**
- Trust bureau + MCP server is the V1 wedge
- Scores change ONLY through interaction, never through time
- Businesses pay to check scores. Agents register free. (Experian model)
- Awareness layer and trust layer are inside/outside views of one product
- Don't split into multiple companies. Be the ONE standard.

**New Competitors Found:**
- **Signet** — Closest trust competitor. Composite 0-1000 score. No OS-level observation, no revenue model.
- **Gen Digital Agent Trust Hub** — Vercel partnership, 500M devices. Pre-install scanning only.
- **Microsoft Agent 365** — GA May 1, 2026, $15/user/mo. Microsoft-scoped, not neutral.

**Visa/Mastercard Opportunity:** Submantle trust score as a field inside Mastercard Verifiable Intent records. Same SD-JWT standard. Neither payment network can build neutral behavioral trust.

## Uncommitted Changes

**From prior session (2026-03-11):** Trust layer code — 4 modified files + 1 new test file. 187 tests passing with these changes. Still uncommitted.

**From this session (2026-03-12):** VISION.md updates (bidirectional trust, Experian model, go-to-market). All research council V2 files. Plan-deepen notes. This HANDOFF.md.

**Next instance should commit all changes.**

## Build Priority — Revised (Post-Council, Post-Plan-Deepen)

| # | Task | Status | Why |
|---|------|--------|-----|
| 1 | Privacy mode | DONE | |
| 2 | SQLite persistence | DONE | |
| 3 | Event bus | DONE | |
| 4 | Agent identity | DONE | |
| 5 | Trust layer wiring | DONE (uncommitted) | record_query(), compute_trust(), anti-gaming stubs |
| 6 | Soft-delete deregistration | NEXT | Prerequisite for reporter auth — prevents record erasure |
| 7 | Interaction logging table | NEXT | Foundation for everything — three-sided logs with UUIDs |
| 8 | Reporter auth + pending state + velocity caps | NEXT | The eBay model — only members report, must reference real interactions |
| 9 | MCP server (Python, stdio) | NEXT (parallel with 6-8) | Thin wrapper over existing modules. The product. |
| 10 | Business API keys + Stripe Payment Links | NEXT | Minimal billing — scales to ~10 customers with near-zero code |
| 11 | Sandbox/testing mode | AFTER EXPEDITION | Design pending trust lifecycle expedition |
| 12 | Status labels + review workflow | AFTER EXPEDITION | Design pending trust lifecycle expedition |
| 13 | Dashboard depth | DEFERRED | Follows when customers demand it |
| 14 | Go production rewrite | FUTURE | |
| 15 | W3C VC attestation issuance | FUTURE (accelerate if Mastercard VI materializes) | |

## Key Research Pointers

| Research | Location | Key Finding |
|----------|----------|-------------|
| Council V2: Product-Market Fit | `research/council-product-market-fit-v2/` | Business confidence 4.5/10. Zero customer conversations is critical risk. |
| Plan-Deepen Notes | `research/council-product-market-fit-v2/plan-deepen-notes.md` | Reporter auth is 5 subtasks. MCP is simpler than expected. |
| Tension Report | `research/council-product-market-fit-v2/tension-report.md` | MCP urgency vs sequencing tension. Anchor brand has no mechanism. |
| Council V1: Scoring Model | `research/council-scoring-model/` | Formula sound. Single score correct for V1. |
| Protocol Architecture | `research/expedition-protocol-architecture/` | MCP, RATS RFC 9334, Go libraries confirmed |
| Trust Layer | `research/expedition-trust-layer/` | Beta formula, VC format, anti-gaming |

## Open Questions

1. **How to acquire an anchor brand without supply?** Council's biggest unresolved question.
2. **Should Mastercard VI integration be pursued now?** Most actionable external finding but requires W3C VC layer.
3. **Trust lifecycle labels, sandbox, review tiers** — pending expedition results.
4. **SDK version:** CLAUDE.md says "MCP Go SDK v1.4.0" but context7 found v0.4.0-v1.2. Verify before Go build.
