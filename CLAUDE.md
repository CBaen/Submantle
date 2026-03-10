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
4. **Always aware, never acting.** Substrate provides knowledge. Agents and apps act on it.
5. **Inner ring first.** Software awareness before hardware before environment.

## What NOT to Do
- Don't add LLM-based process classification — signatures handle this
- Don't send process data off-device
- Don't add features that make Substrate an agent (it's the ground, not the organism)
- Don't over-engineer the prototype — it's for proving concepts

## Document Parity

| Document | Location | Tracks |
|----------|----------|--------|
| VISION.md | Project root | Product vision, business model, architecture |
| HANDOFF.md | Project root | Current state, what's next |
| CLAUDE.md | Project root | Rules and conventions |
| signatures.json | prototype/ | 15 identity signatures |
