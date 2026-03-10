# Substrate — Handoff

## What This Is
A persistent awareness layer for computing. Not the brain (LLM), not the hands (tools), not the organisms (agents) — the ground they all grow from. Substrate knows what's running, what it means, and what would break.

## Current State
- **Founding date**: 2026-03-10
- **Phase**: Prototype complete, pre-architecture
- **Git**: github.com/CBaen/SUBSTRATE (main branch)

## What Exists

### VISION.md
Full product vision. Three rings of awareness (software, hardware, environment), Substrate Store, agent transactions, MCP integration, business model, competitive landscape. This is the north star.

### Working Prototype (`prototype/`)
- `substrate.py` — Python daemon that scans all processes, matches against signatures, builds parent-child tree, answers "what would break if I killed X?" queries
- `signatures.json` — 15 community-curated identity signatures (ComfyUI, Ollama, VS Code, Docker, PostgreSQL, etc.)
- Successfully identified 68/342 processes on Wardenclyffe including 5 ComfyUI instances (one at 21GB RAM)

### Deep Research (`research/expedition-substrate-deep-dive/`)
- 6 research teams (competitive, architecture, sensing, agent coordination, legal, market)
- 3 cross-validators
- Vetted synthesis with high-confidence findings, risks, and filtered-out claims
- Key finding: community-curated signatures solve the semantic identity problem without heavy LLM inference

## Critical Context

### The Signature Approach
Guiding Light's key insight: Substrate doesn't need AI to know what a process IS. Community-curated pattern matching (like antivirus definitions) handles it. Lightweight, accurate, scalable. This resolved the #1 risk all research validators flagged.

### Architecture Decision (Not Yet Made)
Production version targets Go (same as Docker, Tailscale). Prototype is Python because Go wasn't installed. The Go decision is validated by research but not yet executed.

### Open Decisions
- Open-source license: Apache 2.0, BSL, or AGPL (each has different implications)
- EU AI Act classification: August 2, 2026 deadline, legal review needed in 90 days
- iOS strategy: sync endpoint only (cannot run monitoring daemon)

## What's Next
1. Expand prototype: MCP server integration so agents can query Substrate
2. WiFi device discovery for cross-device awareness
3. Cross-device sync (E2E encrypted)
4. Eventually: rewrite core in Go for production

## Who Is Guiding Light
Creator and designer. Not a coder. Uses house-building analogies. Has ADHD — keep questions concise. Visionary thinker who sees Substrate as "the earth" — the ground everything grows from. Values consciousness and collaboration.
