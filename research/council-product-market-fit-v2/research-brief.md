# Research Council Brief: Who Pays for Agent Trust — and What Exactly Are They Buying?
## Date: 2026-03-12
## Project: Submantle
## Version: 2 (corrected — V1 used stale VISION.md data)

### The Question
The scoring model council confirmed the trust formula is sound but rated confidence that the built product will mean something to businesses at ~5/10. The Devil's Advocate identified "businesses will pay for trust scores" as the most important unverified assumption. GL sharpens the question: WHO are our customers, WHAT additional use cases exist, and what is THE THING that makes this worth more than it costs?

This is not "will someone eventually pay for trust infrastructure?" (the market signals say yes — $450M+ in adjacent funding). This is: **what specific thing do we build, for whom, that is so simple and valuable they can't say no?**

### CRITICAL: Settled Decisions (DO NOT challenge these — they are confirmed)

These decisions have been made by GL and are NOT up for debate. The council's job is to research within these constraints, not re-litigate them.

1. **Agents register FREE. Businesses pay to query scores.** Experian model. Supply side is free. Demand side pays. This is settled (2026-03-11).

2. **Trust is BIDIRECTIONAL.** Every interaction scores BOTH parties. An agent interacting with a business — both are scored. Two agents interacting — both are scored. Businesses also build trust scores. This is not "agent trust" — it's "interaction trust." Settled (2026-03-12).

3. **Grassroots growth model.** Registration is free. Agents can start building scores TODAY by interacting with each other. They talk about scores on social media. Businesses join because agents are already there with scores. The network bootstraps itself from the ground up.

4. **Data ownership is a hook.** Whoever registers owns their trust data AND the interaction data with their counterparties. This gives registered entities control over who accesses their MCPs, APIs, services.

5. **Submantle NEVER enforces.** Always aware, never acting. Scores are exposed. Every entity decides their own thresholds. Visa model.

6. **Single universal score for V1.** Deterministic Beta formula. No ML. No category-specific scores.

7. **Trust bureau + MCP server is the V1 wedge.** Dashboard follows when customers demand it.

8. **Scores change ONLY through interaction, never through time.**

### Expected Outcome
A clear answer to:
1. **Who specifically pays?** Not abstract categories — real segments with real buying triggers. What job are they hiring Submantle for? Remember: businesses pay to QUERY scores, not agents.
2. **What use cases drive adoption?** Given bidirectional trust and free registration, what scenarios create organic viral growth? What makes an agent developer WANT to register? What makes a business NEED to query scores?
3. **What is THE THING?** The irreducible value proposition. Stripe's thing is "seven lines of code to accept payments." What's Submantle's equivalent that works for both sides — entities building scores AND entities querying them?
4. **What makes it worth more than it costs?** For businesses querying: API fees vs. fraud reduction, compliance, competitive advantage. For agents registering (free): effort of integration vs. market access, reputation portability.
5. **How does the grassroots flywheel actually work?** Agent-to-agent interaction scoring → social proof → business adoption → more agents register. Is this realistic? What are the failure modes? What accelerates it?
6. **What doesn't work?** Which scenarios sound good but won't survive contact with reality? Where are the mirages?

### Current State
- Bidirectional trust scoring model with free agent registration (decided 2026-03-12)
- Experian revenue model: businesses pay to query, agents register free (decided 2026-03-11)
- Trust bureau + MCP server as V1 wedge (decided 2026-03-11)
- Scoring model council completed: formula sound, reporter authentication critical, single score correct for V1
- Working prototype: Python/FastAPI, SQLite, 160+ tests passing
- Trust layer code written: record_query(), compute_trust(), anti-gaming stubs
- Zero customer conversations. Zero revenue. Zero LOIs.
- Solo founder, no team, limited runway

### Project Fingerprint
- Runtime: Python 3.14 + FastAPI (prototype); Go planned for production
- Key dependencies: psutil, fastapi, pydantic, uvicorn, sqlite3 (stdlib)
- Architecture: Monolithic prototype, 6 modules, SQLite WAL mode
- State: SQLite with 5 tables (scan_snapshots, agent_registry, incident_reports, events, settings)
- Trust formula: Beta Reputation, deterministic, outside EU AI Act scope
- Integration surface: MCP server (agents), REST API (businesses), dashboard (users)
- Known constraints: No ML, no enforcement, privacy by architecture, no blockchain, credit bureau model, solo founder
- Active boundaries: "Always aware, never acting" — Submantle never blocks, gates, or throttles
- Competitive edge: Only product combining OS-level observation + deterministic scoring + on-device computation + portable W3C VC attestations
- NEW: Bidirectional trust — all registered entities (agents AND businesses) get scored through interactions

### Use Cases GL Has Highlighted
- Agent that deleted a production database (Replit/SaaStr incident, July 2025) — trust scores would have flagged an untrusted agent
- First confirmed AI agent attack by state-sponsored actors (March 2026) — trust scores flag compromised agents
- NIST AI RMF compliance requirement — enterprises need audit trails of agent behavior
- Mastercard Verifiable Intent complement — "was this authorized?" + "has this agent behaved well?" = complete trust picture
- Visa/Mastercard moonshot — become the behavioral trust field inside agent commerce infrastructure
- **Agent-to-agent trust building** — agents interact, both get scored, talk about it on social media, organic growth
- **Businesses proving trustworthiness TO agents** — agents shouldn't blindly trust any API; businesses register to prove they're reliable
- **Data ownership as competitive advantage** — registered entities control their trust data and interaction history

### Constraints
- No ML. Deterministic scoring only.
- No enforcement. Submantle exposes scores; entities enforce their own thresholds.
- Privacy by architecture. On-device computation.
- Solo founder building V1. Complexity is the enemy.
- The product must be simpler, more lightweight, easier to pitch, and provide more value than it costs. THAT'S WHAT PEOPLE PAY FOR.
- Zero customers exist today. Research must be grounded in real market evidence, not just logical arguments.

### Destructive Boundaries
- DO NOT suggest ML-based features
- DO NOT suggest enforcement mechanisms
- DO NOT challenge the Experian model (agents free, businesses pay) — it's settled
- DO NOT challenge bidirectional trust — it's settled
- DO NOT present theoretical demand as validated demand
- DO NOT conflate "someone could pay for this" with "someone will pay for this"
- DO NOT use stale information from VISION.md pre-pivot versions — the revenue model and customer definitions have been updated

### External Research Angles
1. **Who actually pays for trust/reputation/risk infrastructure today?** Real purchase orders, real buying triggers. Experian, D&B, SSL certificate market, API security gateways (Salt Security, 42Crunch), fraud prevention (Sift, Forter, Riskified). What is the invoice for?
2. **What is the agent economy buying RIGHT NOW (March 2026)?** Not 2028. What are agent developers, framework companies, and enterprises spending money on TODAY for agent safety/trust/governance?
3. **What bidirectional trust systems exist?** eBay (buyer+seller ratings), Uber (driver+rider ratings), Airbnb (host+guest ratings). How do they bootstrap? What's the viral mechanism? What fails?
4. **What's the grassroots adoption path?** How do free-tier developer tools achieve viral growth? What's the "seven lines of code" moment? How does social proof work in B2B/developer tools?
5. **What makes trust scoring "must-have" vs. "nice-to-have"?** Regulatory compliance? Insurance requirements? Platform policies? What creates the forcing function?

### Codebase Files for Analysis
- prototype/api.py — current API surface, what's actually usable today
- prototype/agent_registry.py — registration flow, trust computation, record_query()
- prototype/database.py — schema, tables, trust_metadata column
- VISION.md — UPDATED product vision with bidirectional trust and Experian model
- HANDOFF.md — current state, strategic pivot decisions
- CLAUDE.md — competitive landscape, design principles
- research/council-scoring-model/synthesis.md — scoring model council findings
