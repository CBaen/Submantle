# Submantle — Handoff

## What This Is
The credit bureau for AI agents. Agents register, earn trust scores through interactions, and businesses pay to check those scores. Neutral infrastructure — Submantle never acts, never enforces. It labels. Brands decide their own thresholds.

## Current State
- **Phase**: BUILDING — Wave 1 complete, Wave 2 next. Implementation sequence executing.
- **Git**: github.com/CBaen/SUBMANTLE (main branch, in sync with origin)
- **Server**: `python -m uvicorn api:app --port 8421` from `prototype/` — dashboard at localhost:8421
- **Tests**: 193 passing across 4 test files
- **Research**: ALL COMPLETE. 5 expeditions + 6 follow-ups + 3 research councils. Files in `research/`. DO NOT re-research settled topics — read this file and build.

## FOR NEW INSTANCES — READ THIS FIRST
1. Research phase is DONE. Do not start new expeditions or councils unless GL explicitly requests one.
2. All design decisions are settled (see below). Do not re-litigate.
3. The 5-wave implementation sequence is ready to execute. Start at Wave 1.
4. GL is the bottleneck. Do not ask GL technical questions — research internally first.
5. Push to remote is needed (~42 commits ahead of origin/main).

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

### EXPEDITION: Trust Lifecycle Design — IN PROGRESS (Phase 2 Complete)

5-team expedition on Trust Lifecycle Design. All research and cross-validation done. Synthesis pending.

**Topic:** `expedition-trust-lifecycle`
**All files in `research/expedition-trust-lifecycle/`:**
- `research-brief.md` — Approved brief with settled decisions as NON-CHALLENGEABLE
- `team-1-status-labels-findings.md` — 9 analog systems, 5 lifecycle labels, anti-gaming per label
- `team-2-sandbox-testing-findings.md` — Stripe sandbox architecture, Valorant unrated mode
- `team-3-review-tiers-findings.md` — 5 incident states, severity classification, dedup rules
- `team-4-fairness-recovery-findings.md` — FCRA 7-year rule, Beta formula early-incident vulnerability
- `team-5-interaction-metadata-findings.md` — 5 metadata categories, denied interactions, dual interpretation
- `validation-1.md` — Team 3 breaks settled rule (skip pending), fractional weights unimplemented, 3 contradictions
- `validation-2.md` — Patient attacker vector unaddressed, fractional weight blocker, interaction_id MCP dependency
- `validation-3.md` — Solo-founder feasibility (20 artifacts = 8-12 weeks), math errors in Team 4, formula discrepancy

**Key Validator Findings:**
1. **Fractional weights blocker**: Teams proposed 0.5 formula_weight but Beta formula expects integers — no one solved this
2. **Reporter credibility bootstrapping**: First brands have no accuracy history — chicken-and-egg problem
3. **EU AI Act fragility**: Behavioral-data-derived weights may not qualify for "rules defined solely by natural persons" exemption
4. **Patient attacker vector**: Slow, sophisticated attacker building legitimate history — no deterministic defense exists
5. **Formula discrepancy**: CLAUDE.md shows `total_queries / (total_queries + incidents)` but codebase uses `(total_queries + 1) / (total_queries + incidents + 2)`
6. **Team 4 math errors**: Recovery formula should be `q ≥ 4i + 3` not `4i + 6`. 10 incidents needs ~43 queries for 0.8, not 78.

**Phase 3 (Synthesis): COMPLETE** — `synthesis.md` written 2026-03-12. Vetted all findings against 3 validators. 7 high-confidence convergences, 3 contested decisions escalated to GL, 5 items filtered out, 6 risks documented. Phased implementation sequence provided.

**NEXT STEP: GL rules on 3 contested decisions (see section below), then implementation begins.**

### RESEARCH COUNCIL V2: Scoring Model (Weights & Measures) — NEAR COMPLETE (Phase 5 in progress)

Full deliberation: 3 agents (Codebase Analyst, External Researcher, Devil's Advocate) + challenge round + orchestrator synthesis. Tension Analyst dispatched.

**All files in `research/council-scoring-model-v2/`:**
- `research-brief.md` — Approved brief: what interactions change a score, data exchange, two-way grading, enforcement boundary
- `codebase-analyst-findings.md` + `codebase-analyst-challenge.md`
- `external-researcher-findings.md` + `external-researcher-challenge.md`
- `devils-advocate-findings.md` + `devils-advocate-challenge.md`
- `synthesis.md` — Full synthesis with master score table, 9 high-confidence findings, 5-wave implementation sequence
- `tension-report.md` — Pending (Tension Analyst dispatched)

**Council Key Findings (triple convergence):**
1. Reporter credibility is V2 (Go rewrite) — 8 prerequisites missing, bootstrapping unsolved
2. Severity determines processing path, NOT formula weight for V1 — avoids float-in-Beta entirely
3. Pending state must precede any formula change — non-negotiable prerequisite
4. Two-track architecture: Beta score + trust_metadata enrichment — production-validated pattern
5. Incidents COUNTED (integers), not weighted (floats) for V1 — preserves Beta distribution math
6. Score versioning (FICO version fork model) ships in V1
7. Corroboration is metadata, not formula multiplier
8. `has_history` flag and `reporter_diversity` count ship in V1 API
9. Deregistered agent names are permanent records (credit bureau model)

**V1 Implementation: 5-Wave Build Sequence**
- Wave 1: trust_metadata enrichment + score_version + has_history (no dependencies)
- Wave 2: Soft-delete (history preservation)
- Wave 3: Pending state + status column + severity classification + dedup
- Wave 4: Formula reads accepted incidents from table (not counter) + API response update
- Wave 5: MCP server (parallel with Waves 3-4)

### CONTESTED DECISIONS — RESOLVED (GL rulings 2026-03-12)

1. **"Suspended" label → renamed.** GL ruled the word implies enforcement power Submantle doesn't have. Replace with neutral informational label. Agents can voluntarily self-identify issues; interaction logs prove honesty. Exact label TBD (candidates: "Flagged," "Under Review" already exists).

2. **Dispute timeout: auto-withdraw.** Confirmed. Matches FCRA model — unsubstantiated claims drop. Benefit of the doubt to the agent.

3. **Minimum interaction threshold: needs math, not arbitrary number.** GL ruled: must determine what types of interactions count, mathematical basis for the number, and that refusal-of-exchange counts as an interaction. Scoring Model Council produced Beta credible interval framework (see synthesis) but the specific number requires validation against commercial context. V1 approach: surface `has_history`, `total_queries`, `reporter_diversity` — let brands set their own floors.

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

## Build Priority — Revised (Post-Scoring-Model-Council)

**V1 Goal:** ONE working customer loop — agent carries score, brand uses it.

| # | Task | Status | Why |
|---|------|--------|-----|
| 1 | Privacy mode | DONE | |
| 2 | SQLite persistence | DONE | |
| 3 | Event bus | DONE | |
| 4 | Agent identity | DONE | |
| 5 | Trust layer wiring | DONE | record_query(), compute_trust(), anti-gaming stubs |
| 6 | Wave 1: trust_metadata + score_version + has_history | DONE | score_version "v1.0", has_history bool, reporter_diversity count. |
| 7 | Wave 2: Soft-delete deregistration | DONE | Permanent names, token invalidation, is_active field. 200 tests. |
| 8 | Wave 3: Pending state + severity classification + dedup | NEXT | Non-negotiable prerequisite for formula change. |
| 9 | Wave 4: Formula reads accepted incidents + API update | NEXT | Decouples from counter. accepted_incidents, reporter_diversity in API. |
| 10 | Wave 5: MCP server (Python, stdio) | NEXT (parallel with 8-9) | Thin wrapper over existing modules. The product. |
| 11 | Business API keys + Stripe Payment Links | NEXT | Minimal billing — scales to ~10 customers with near-zero code |
| 12 | Interaction logging table + reporter auth | V1.1 | eBay model — only members report, must reference interactions |
| 13 | Sandbox/testing mode | V1.1 | Design from Trust Lifecycle Expedition |
| 14 | Status labels + review workflow | V1.1 | Design from Trust Lifecycle Expedition |
| 15 | Dashboard depth | DEFERRED | Follows when customers demand it |
| 16 | Go production rewrite | FUTURE | Reporter credibility, severity-as-formula-weight, recency weighting |
| 17 | W3C VC attestation issuance | FUTURE (accelerate if Mastercard VI materializes) | |

## Key Research Pointers

| Research | Location | Key Finding |
|----------|----------|-------------|
| Council V2: Product-Market Fit | `research/council-product-market-fit-v2/` | Business confidence 4.5/10. Zero customer conversations is critical risk. |
| Council V2: Scoring Model | `research/council-scoring-model-v2/` | Phase 4 complete, Phase 5 pending. Severity = routing not formula weight. Incidents counted not weighted for V1. 5-wave build sequence. |
| Expedition: Trust Lifecycle | `research/expedition-trust-lifecycle/` | Phase 2 complete. 5 labels, sandbox design, review tiers, recovery math, interaction metadata. |
| Plan-Deepen Notes | `research/council-product-market-fit-v2/plan-deepen-notes.md` | Reporter auth is 5 subtasks. MCP is simpler than expected. |
| Tension Report | `research/council-product-market-fit-v2/tension-report.md` | MCP urgency vs sequencing tension. Anchor brand has no mechanism. |
| Council V1: Scoring Model | `research/council-scoring-model/` | Formula sound. Single score correct for V1. |
| Protocol Architecture | `research/expedition-protocol-architecture/` | MCP, RATS RFC 9334, Go libraries confirmed |
| Trust Layer | `research/expedition-trust-layer/` | Beta formula, VC format, anti-gaming |

## Open Questions

1. **How to acquire an anchor brand without supply?** Council's biggest unresolved question.
2. **Should Mastercard VI integration be pursued now?** Most actionable external finding but requires W3C VC layer.
3. **Neutral label for severe status** — GL rejected "Suspended." Candidates: "Flagged," possibly merge with "Under Review." Needs design.
4. **Self-identification mechanism** — GL raised: agents/users can voluntarily self-identify issues. How does this surface in API? Affects formula differently?
5. **Minimum interaction threshold math** — Beta credible interval framework provided but needs validation against commercial context.
6. **Score inertia for compromised high-history agents** — 5000-query agent barely affected by 50 incidents. V2 recency-weighting needed.
7. **SDK version:** CLAUDE.md says "MCP Go SDK v1.4.0" but context7 found v0.4.0-v1.2. Verify before Go build.

## Resolved Questions (this session)

- **Fractional weights blocker** — RESOLVED: V1 counts incidents (integers), doesn't weight them. formula_weight column exists in schema at 1.0 default for V2 readiness.
- **Reporter credibility bootstrapping** — RESOLVED for V1: deferred to V2. D&B reporter_diversity in API metadata lets brands set their own threshold.
- **3 contested decisions** — ALL RULED by GL. See "Contested Decisions — RESOLVED" section above.
