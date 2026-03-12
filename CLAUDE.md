# Substrate — Project Rules

## What This Is
The ground beneath everything. A persistent awareness layer for computing.
Read VISION.md for the full picture. Read HANDOFF.md for current state.

## Conventions
- **Prototype code**: Python, in `prototype/`
- **Production code** (future): Go, will live in `cmd/` and `internal/`
- **Research**: `research/expedition-{topic}/`
- **Identity signatures**: `prototype/signatures.json` — community-curated, lightweight pattern matching

## Design Principles
1. **Lightweight first.** Substrate must be invisible in resource usage. No heavy models.
2. **Community knowledge over AI inference.** Signatures, not LLMs, identify processes.
3. **Privacy by architecture.** On-device processing. E2E encrypted sync. No telemetry.
4. **Always aware, never acting.** Substrate provides knowledge and trust scores. It never blocks, gates, or throttles agents. Brands and platforms enforce their own thresholds using Substrate's data. This applies to BOTH the awareness layer AND the trust layer.
5. **Inner ring first.** Software awareness before hardware before environment.
6. **Deterministic scoring only.** Trust formulas must be pure math (Beta Reputation), not ML. This keeps Substrate outside EU AI Act scope permanently. No ML-based anomaly detection, no pattern inference.

## What NOT to Do
- Don't add LLM-based process classification — signatures handle this
- Don't send process data off-device
- Don't add features that make Substrate an agent (it's the ground, not the organism)
- Don't over-engineer the prototype — it's for proving concepts
- Don't add ML-based trust scoring or anomaly detection — deterministic formulas keep us outside EU AI Act scope
- Don't build enforcement into Substrate — no blocking, no gating, no throttling. Substrate exposes scores; third parties decide what to do with them

## Document Parity

| Document | Location | Tracks |
|----------|----------|--------|
| VISION.md | Project root | Product vision, business model, architecture, competitive landscape |
| HANDOFF.md | Project root | Current state, what's next, open decisions |
| CLAUDE.md | Project root | Rules, conventions, design principles |
| substrate-queue.md | Project root | Active tasks only. Git preserves completed. |
| substrate-index.md | Project root | Pointers to research and reference material |
| substrate-decisions.md | Project root | Append-only decision log. Use decision-search.py, never read full file. |
| signatures.json | prototype/ | 15 identity signatures |

## Self-Improvement Loop

After ANY correction from the user, append a lesson to `lessons-learned.md` in this project root. Format: `### Title` / `- **Pattern**:` what went wrong / `- **Rule**:` what to do instead / `- **Why**:` why the old way fails. Universal lessons go to `C:\Users\baenb\.claude\lessons-learned.md` instead.
