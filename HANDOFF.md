# Substrate — Handoff

## What This Is
The ground beneath everything. A persistent awareness layer for computing. Your devices finally understand what you're doing and protect you from losing it.

## Current State
- **Phase**: Dashboard prototype live, deep research complete, ready to BUILD V1
- **Git**: github.com/CBaen/SUBSTRATE (main branch)
- **Server**: `python -m uvicorn api:app --port 8421` from `prototype/` — dashboard at localhost:8421

## What Just Happened (2026-03-10)

### Deep Research Expedition Completed
Full expedition: 5 research teams (Opus), 3 validators (Opus), 1 independent auditor (Opus). All files in `research/expedition-substrate-infrastructure/`.

**Verdict: GO on a 90-day experiment.** Ship a working MCP server before June 2026 WWDC. Define success metrics before building. The idea is sound, the timing is urgent, the differentiation is real. The founding configuration (solo non-technical) is the constraint — ship V1, prove value, then seek co-founder or capital.

Key files:
- `research/expedition-substrate-infrastructure/synthesis.md` — Vetted synthesis with 9 audit-recommended revisions applied
- `research/expedition-substrate-infrastructure/synthesis-audit.md` — Independent audit of the synthesis
- `research/future-expeditions.md` — Three future expedition ideas captured (agent reviews, privacy mode UX, agent payment processor)

### Critical Findings
1. MCP is the right integration surface (97M+ monthly SDK downloads)
2. OS-layer semantic process context is genuinely unoccupied — no competitor has it
3. Subscriptions are near-term revenue, not microtransactions
4. Open-source daemon, closed coordination server (Tailscale model)
5. Solo non-technical founder ceiling is the strongest constraint — mitigated by scoping V1
6. Runlayer (competitor) has AAIF governance seat — ship before standards are written
7. Microsoft Recall failure = active market opening for privacy-first on Windows

### Guiding Light's Product Direction (post-expedition)
The product is NOT about agent infrastructure or payment processing first. It's about **the feeling**: your devices know what's going on in your life. The business model grows from that root.

Key insights from Guiding Light:
- **Privacy mode** is the trust feature, not a compromise. Must be front and center. "For porn!" — the honest reason people need an off switch, and that honesty IS the brand.
- **Privacy mode should still feel good** — live view without memory, device connections stay active
- **Agent reviews** — "the new Google Reviews but for agent infrastructure." Agents rate services based on measured experience. Novel, nobody doing it. (Captured in future-expeditions.md)
- **The Orwellian concern is real** — Substrate's answer: YOU watch YOUR stuff. Open source. Privacy mode prominent. Origin story builds trust.
- **Substrate as payment processor** for agent transactions, designed for ease of use. Credit economy, not traditional payment processing.

### Prerequisite Decision (before Go daemon)
The federated analytics data layer must be DESIGNED into the daemon's data structures from day one. Not built, but designed for. This preserves the Insights revenue option. Binary decision — can't retrofit later.

## What Exists

### Working Dashboard (prototype/)
- `dashboard.html` — Anthropic-styled awareness dashboard (warm slate palette, clay accent, Inter + JetBrains Mono, light/dark mode, has viewport meta for mobile)
- `api.py` — FastAPI server: process awareness + ARP device discovery + "Ask Substrate" query
- `substrate.py` — Core: process scanning, signature matching, parent-child tree, impact queries
- `signatures.json` — 15 community-curated identity signatures

### Design System
- `ANTHROPIC_DESIGN_BRIEF.md` — Full Anthropic visual language reference
- `DESIGN_SPEC.md` — Original dashboard design spec

### Research
- `research/expedition-substrate-deep-dive/` — First expedition (process awareness daemon validation)
- `research/expedition-substrate-infrastructure/` — Second expedition (infrastructure/business validation)
- `research/future-expeditions.md` — Captured future research ideas

## What to Build Next (V1 — The 90-Day Experiment)

### Priority Order
1. **Privacy mode toggle** — the trust feature. One button, front and center. Stops scanning, drops in-memory state, no data written. The off switch being real IS the product.
2. **Mobile-responsive dashboard** — so Guiding Light can see laptop awareness from their Android phone via WiFi (visit laptop-ip:8421)
3. **MCP server endpoints** — so AI agents can query Substrate natively (the expedition's #1 convergence point)
4. **mDNS + SSDP device discovery** — richer than ARP alone
5. **Event-driven architecture** — piggybacking on OS events, not polling

### Guiding Light's Devices
- **Laptop**: Windows 11 (primary awareness device, deep process monitoring via ETW)
- **Phone**: Android (companion device, UsageStats API for app awareness)
- **Connection**: Same WiFi network, phone accesses laptop's Substrate via browser initially

### Success Metrics (MUST define before shipping)
- What user adoption justifies continuing?
- What willingness-to-pay signal is sufficient?
- What evidence justifies seeking co-founder or capital?

## Architecture
- **Prototype**: Python (FastAPI, psutil, SQLite for state)
- **Production** (future): Go daemon, gRPC API, SQLite knowledge graph
- **Integration**: MCP server (agents query via Model Context Protocol)
- **Privacy**: On-device processing, E2E encrypted sync, privacy mode toggle

## Open Decisions
- Open-source license (Apache 2.0 / BSL / AGPL)
- EU AI Act classification (August 2026 deadline, 145 days — legal review needed)
- Go rewrite timing (after V1 proves value)
- Federated analytics data layer design (prerequisite decision before Go)
- Community signature incentive structure (what motivates contribution?)
