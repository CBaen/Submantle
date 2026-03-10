# Substrate — Handoff

## What This Is
The ground beneath everything. A persistent awareness layer for computing AND the transport layer for AI agents. Not just process monitoring — the infrastructure that agents travel through, that facilitates agent transactions, that hosts the Substrate Store. This scales to hundreds of millions of devices.

## Current State
- **Phase**: Dashboard prototype live, pre-architecture
- **Git**: github.com/CBaen/SUBSTRATE (main branch, all pushed)
- **Server**: `python -m uvicorn api:app --port 8421` from `prototype/` — dashboard at localhost:8421

## What Exists

### Working Dashboard (prototype/)
- `dashboard.html` — Anthropic-styled awareness dashboard (warm slate palette, clay accent, Inter + JetBrains Mono, light/dark mode)
- `api.py` — FastAPI server: process awareness + ARP-based device discovery + "Ask Substrate" query
- `substrate.py` — Core: process scanning, signature matching, parent-child tree, impact queries
- `signatures.json` — 15 community-curated identity signatures

### Design System
- `ANTHROPIC_DESIGN_BRIEF.md` — Full Anthropic visual language reference (extracted from their CSS bundles)
- `DESIGN_SPEC.md` — Original dashboard design spec

### Research (research/expedition-substrate-deep-dive/)
- 6 teams, 3 validators, vetted synthesis

## Critical Vision (from Guiding Light)
Substrate is NOT just a process monitor or safety checker. It is:
1. **The awareness layer** — knows what's running on every connected device
2. **The transport layer for AI** — agents travel through Substrate
3. **The transaction layer** — facilitates agent-to-agent and agent-to-service transactions
4. **The marketplace** — Substrate Store for identity packs, data plugins, certifications
5. **The nervous system** — piggybacking on existing OS events and network broadcasts (not active scanning)
6. **Eventually: home to its own AI** — trained on awareness data nobody else has

### Anthropic Partnership Vision
Substrate + Claude is the natural pairing. MCP is Anthropic's protocol, Substrate speaks MCP natively. Step 2 of the AI evolution is an official partnership. Guiding Light wants Anthropic.

### Scale Vision
Hundreds of millions of devices. The "Ask Substrate" interface serves infinite use cases — NOT pigeonholed to "what would break." Every query an agent makes, every device that connects, every signature the community contributes grows the network.

## Architecture Insight: Piggybacking
Substrate should be the quietest program on the machine. Instead of active scanning:
- OS event streams (ETW) for process changes
- mDNS listener for device announcements (zero traffic)
- ARP cache reads for passive device knowledge
- Periodic reconciliation scans (once/minute) as sanity check
Events for speed, scans for completeness. Near-zero resource usage.

## Open Decisions
- Open-source license (Apache 2.0 / BSL / AGPL)
- EU AI Act classification (August 2026 deadline)
- Go rewrite timing

## Next Steps
1. Expand "Ask Substrate" beyond process queries — make it truly open-ended
2. Add mDNS + SSDP device discovery (richer than ARP alone)
3. MCP server integration (agents query Substrate natively)
4. Event-driven architecture (piggybacking, not polling)
