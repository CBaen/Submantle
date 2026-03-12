# Submantle — Project Rules

## What This Is

**The credit bureau for AI agents.** Every agent earns a trust score through observed behavior, carries it everywhere as a portable credential, and brands decide their own thresholds.

Submantle is two things in one:
1. **Awareness layer** — knows what's running on your devices, what it means, what would break
2. **Behavioral trust infrastructure** — scores agents based on what they actually do, not what they claim

Think of it like the ground beneath everything. Submantle isn't an agent, isn't a tool, isn't a security product. It's the earth that agents and tools grow from. It provides knowledge and trust scores. It never acts.

**Read VISION.md** for the full product vision, business model, and competitive landscape.
**Read HANDOFF.md** for current state and what was last built.

## Why This Matters — The Competitive Clock

As of March 2026, **$450M+ in funding** has been poured into adjacent agent trust products. None of them occupy Submantle's specific position, but they're converging toward it:

- **HUMAN Security** ($300M+, 469 employees) — behavioral trust at the web layer. Per-app, per-session. Trust doesn't travel.
- **Zenity** ($55M, Microsoft M12) — enterprise agent governance. Scores don't leave the building.
- **Keycard** ($38M, a16z) — agent identity/IAM. No behavioral scoring yet, but could add it.
- **Gen Digital/Norton** (~500M devices) — pre-install scanning. One pivot from runtime behavioral scoring.
- **Mnemom** (self-funded, shipping) — LLM API reasoning analysis. Can only see what agents say to the LLM, not what they do. Requires agent cooperation.
- **Microsoft Entra Agent ID** (in preview) — agent risk levels, enforcement-first. Not neutral.

**The gap no one fills:** No company combines (1) OS-level observation, (2) deterministic scoring, (3) on-device computation, (4) portable W3C VC attestations. Google's own UCP spec explicitly states it "does not solve which agents should be trusted."

**The window is 12-18 months.** The IETF has an informational draft on behavioral evidence but no protocol. NIST launched an agent standards initiative. The field is organizing. Ship production code and get one real customer loop before someone with $50M fills this exact gap.

## The Edge — Why Submantle Wins

Submantle's defensible position is **structural neutrality**:

- Microsoft can't be neutral (favors Azure/Windows agents)
- Anthropic can't be neutral (favors Claude agents)
- Gen Digital is a security company, not infrastructure
- HUMAN is per-application — trust resets at every site boundary
- Mnemom requires agents to opt in and route through their gateway

**Submantle is the only product positioned as neutral infrastructure** — open protocol, on-device computation, no enforcement. Platform vendors cannot build this without destroying their own business incentives. This is why Visa works: banks couldn't trust each other's payment systems, so they needed a neutral intermediary.

**Additional structural advantages:**
- **OS-level observation without cooperation** — sees everything running, doesn't ask permission
- **Deterministic scoring (Beta formula) outside EU AI Act** — competitors using ML are potentially inside regulatory scope
- **On-device computation** — privacy by architecture, Sybil resistance by locality
- **Portable W3C VC attestations** — trust travels with the agent, not locked to one platform

## Design Principles — Inviolable

1. **Lightweight first.** Submantle must be invisible in resource usage. No heavy models.
2. **Community knowledge over AI inference.** Signatures, not LLMs, identify processes.
3. **Privacy by architecture.** On-device processing. E2E encrypted sync. No telemetry.
4. **Always aware, never acting.** Submantle provides knowledge and trust scores. It NEVER blocks, gates, or throttles agents. Brands and platforms enforce their own thresholds using Submantle's data. This applies to BOTH the awareness layer AND the trust layer. This is the Visa model — Visa doesn't decide whether you can buy something, the merchant does.
5. **Inner ring first.** Software awareness before hardware before environment.
6. **Deterministic scoring only.** Trust formulas must be pure math (Beta Reputation), not ML. This keeps Submantle outside EU AI Act scope permanently. No ML-based anomaly detection, no pattern inference. Adding ML would be an existential regulatory mistake.
7. **Credit bureau model.** Submantle records incident reports from third parties. It does NOT detect incidents itself. Banks report missed payments to the bureau; the bureau stores them. Same model.

## Trust Layer Architecture

- **Formula**: `trust = (total_queries + 1) / (total_queries + incidents + 2)` — Beta Reputation with Laplace smoothing. Initialize at (0,0) = 0.5 ("unknown"). The +1/+2 prevents division by zero and provides a Bayesian prior.
- **Attestation format**: W3C Verifiable Credentials 2.0 + SD-JWT (RFC 9901). NOT BBS+ (still Candidate, no Go support).
- **Agent identity**: `did:web` (DNS-anchored, no blockchain) for public identity, `did:key` for ephemeral.
- **Tiers**: Anonymous (open access) -> Registered ("Submantle Verified") -> Trusted (high score, best rates).
- **Anti-gaming**: Deterministic rules only — velocity caps, query diversity requirements, registration age visibility. No ML.
- **Standards alignment**: IETF RATS RFC 9334 "Passport Model" maps precisely to Submantle's architecture (Attester = daemon, Verifier = attestation server, Relying Party = brands).
- **Go libraries for production**: trustbloc/vc-go v1.3.6 (VC + SD-JWT), pascaldekloe/did v1.1.0 (DID parsing), MCP Go SDK v1.4.0.

## What "An Agent" Is

An agent is the **registered software entity**. Not the model. Not the context window. Not the user. You give a credit score to the company, not the employee, not the phone call, not the customer. Trust survives model changes, accumulates across sessions, and belongs to the builder. See VISION.md for edge cases (forks, multi-model, version upgrades).

## What NOT to Do

- Don't add LLM-based process classification — signatures handle this
- Don't send process data off-device
- Don't add features that make Submantle an agent (it's the ground, not the organism)
- Don't over-engineer the prototype — it's for proving concepts
- Don't add ML-based trust scoring or anomaly detection — this would enter EU AI Act scope and destroy a core competitive advantage
- Don't build enforcement into Submantle — no blocking, no gating, no throttling. Submantle exposes scores; third parties decide what to do with them
- Don't add blockchain dependencies — deterministic, chain-agnostic
- Don't build for mobile first — Android sandboxing blocks process awareness. Desktop/laptop only for V1.
- Don't skip the credit bureau model — Submantle records third-party reports, it does NOT detect incidents

## Build Priority — V1 Path to Proof

The goal is ONE working customer loop: an agent carries a Submantle score, a brand uses it. Everything below serves that goal. Build sequence derived from Scoring Model Council V2 (2026-03-12).

| # | Task | Status | Why It Matters |
|---|------|--------|---------------|
| 1 | Privacy mode | DONE | #1 trust feature |
| 2 | SQLite persistence | DONE | Data survives restarts |
| 3 | Event bus | DONE | Internal pub/sub for all modules |
| 4 | Agent identity | DONE | Cryptographic registration |
| 5 | Trust layer wiring | DONE | record_query(), compute_trust(), anti-gaming stubs |
| 6 | Wave 1: trust_metadata + score_version + has_history | DONE | score_version, has_history, reporter_diversity in API |
| 7 | Wave 2: Soft-delete deregistration | DONE | Permanent names, token invalidation, is_active field |
| 8 | Wave 3: Pending state + severity classification + dedup | NEXT | Prerequisite for formula change |
| 9 | Wave 4: Formula reads accepted incidents + API update | NEXT | Decouples from counter. Core scoring evolution. |
| 10 | Wave 5: MCP server (Python, stdio) | NEXT (parallel) | The product — agents query Submantle |
| 11 | Business API keys + Stripe Payment Links | NEXT | First revenue — near-zero code |
| 12 | Go production rewrite | FUTURE | Reporter credibility, severity weights, recency |
| 13 | W3C VC attestation issuance | FUTURE | Portable trust credentials |

## Conventions

- **Prototype code**: Python, in `prototype/`
- **Production code** (future): Go, in `cmd/` and `internal/`
- **Research**: `research/expedition-{topic}/`
- **Identity signatures**: `prototype/signatures.json` — community-curated, lightweight pattern matching
- **Tests**: `prototype/tests/` — 200 passing across 4 test files. Don't break them.
- **Server**: `python -m uvicorn api:app --port 8421` from `prototype/` — dashboard at localhost:8421

## Document Parity

| Document | Location | Tracks |
|----------|----------|--------|
| VISION.md | Project root | Product vision, business model, architecture, competitive landscape |
| HANDOFF.md | Project root | Current state, what's next, open decisions |
| CLAUDE.md | Project root | Rules, conventions, design principles, competitive context, build priorities |
| submantle-queue.md | Project root | Active tasks only. Git preserves completed. |
| submantle-index.md | Project root | Pointers to research and reference material |
| submantle-decisions.md | Project root | Append-only decision log. Use decision-search.py, never read full file. |
| signatures.json | prototype/ | 15 identity signatures |

## Self-Improvement Loop

After ANY correction from Guiding Light, append a lesson to `lessons-learned.md` in this project root. Format: `### Title` / `- **Pattern**:` what went wrong / `- **Rule**:` what to do instead / `- **Why**:` why the old way fails. Universal lessons go to `C:\Users\baenb\.claude\lessons-learned.md` instead.

## Key Research (for deep context)

4 expeditions + 6 follow-ups completed. Pointers in `submantle-index.md`. Key syntheses:
- `research/expedition-protocol-architecture/synthesis.md` — MCP, RATS RFC 9334, competitive gaps, Go libraries
- `research/expedition-trust-layer/synthesis.md` — Beta formula, VC format, regulatory, anti-gaming
- `research/expedition-submantle-infrastructure/synthesis.md` — Go vs Rust, SQLite, daemon design
- `research/expedition-submantle-deep-dive/synthesis.md` — What Submantle is, competitive landscape, MCP strategy
