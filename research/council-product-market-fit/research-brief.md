# Research Council Brief: Who Pays for Agent Trust — and What Exactly Are They Buying?
## Date: 2026-03-12
## Project: Submantle

### The Question
The scoring model council (completed earlier today) confirmed the trust formula is sound but rated confidence that the built product will mean something to businesses at ~5/10. The Devil's Advocate identified "businesses will pay for trust scores" as the most important unverified assumption. Guiding Light agrees — and sharpens the question: WHO are our customers, WHAT additional use cases exist, and what is THE THING that makes this worth more than it costs to every customer type?

This is not "will someone eventually pay for trust infrastructure?" (the market signals say yes — $450M+ in adjacent funding). This is: **what specific thing do we build, for whom, that is so simple and valuable they can't say no?**

### Expected Outcome
A clear answer to:
1. **Who specifically pays?** Not abstract categories — real segments with real buying triggers. What job are they hiring Submantle for?
2. **What use cases exist beyond what's documented?** VISION.md lists 5 customer types. Are there more? Are some of those 5 actually the same customer? Which ones are real for V1 vs. aspirational?
3. **What is THE THING?** The irreducible value proposition that works for agents, businesses, AND users. Stripe's thing is "seven lines of code to accept payments." What's Submantle's equivalent?
4. **What makes it worth more than it costs?** The cost side: API fees, integration time, trust in a new provider. The value side: fraud reduction, compliance, competitive advantage, peace of mind. Where does the value clearly exceed the cost?
5. **What doesn't work?** Which customer types or use cases are mirages? Which sound good in a pitch deck but won't survive contact with a real buyer?

### Current State
- 5 customer types defined in VISION.md: Agent Developers, Brands/Platforms, Device Owners, Enterprises, Data Buyers
- 8 revenue streams theorized (Pro Subscriptions → Insights licensing)
- Go-to-market sequence: open-source daemon → agent framework developers → free tier → enterprise
- Strategic pivot (2026-03-11): Trust bureau + MCP server is V1 wedge
- Competitive landscape: $450M+ in adjacent funding, no one fills the exact gap
- Scoring model council completed: formula sound, reporter authentication critical, single score correct for V1
- Zero customer conversations have occurred. Zero revenue. Zero LOIs.
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

### Existing Use Cases from VISION.md (for council to validate or challenge)
1. **Agent developers** pay for registration, trust credentials, API volume. "Higher trust = better rates everywhere."
2. **Brands/Platforms** pay for trust score API access. "Show me all agents above trust 0.8."
3. **Device owners** pay for multi-device awareness mesh. "Your devices know what's going on."
4. **Enterprises** pay for managed trust policies, compliance, agent governance. "$50k-$500k/yr."
5. **Data buyers** pay for anonymized aggregate intelligence. "Nobody else has this data."

### Use Cases GL Has Highlighted
- Agent that deleted a production database (Replit/SaaStr incident, July 2025) — awareness prevents this
- First confirmed AI agent attack by state-sponsored actors (March 2026) — trust scores flag compromised agents
- NIST AI RMF compliance requirement — enterprises need audit trails of agent behavior
- Mastercard Verifiable Intent complement — "was this authorized?" + "has this agent behaved well?" = complete trust picture
- Visa/Mastercard moonshot — become the behavioral trust field inside agent commerce infrastructure

### Constraints
- No ML. Deterministic scoring only.
- No enforcement. Submantle exposes scores; third parties enforce.
- Privacy by architecture. On-device computation.
- Solo founder building V1. Complexity is the enemy.
- The product must be simpler, more lightweight, easier to pitch, and provide more value than it costs. THAT'S WHAT PEOPLE PAY FOR.
- Zero customers exist today. This research must be grounded in real market evidence, not just logical arguments.

### Destructive Boundaries
- DO NOT suggest ML-based features
- DO NOT suggest enforcement mechanisms
- DO NOT suggest complex multi-score systems for V1
- DO NOT present theoretical demand as validated demand
- DO NOT conflate "someone could pay for this" with "someone will pay for this"
- DO NOT assume all 5 VISION.md customer types are real. Challenge them.

### External Research Angles
1. **Who actually pays for trust/reputation/risk infrastructure today?** Not who could — who does. What are real purchase orders for? What's the buying trigger? Interview the invoices, not the pitch decks. Look at Experian business model, Dun & Bradstreet, SSL certificate market, API security gateway market (Salt Security, 42Crunch), fraud prevention (Sift, Forter, Riskified).
2. **What is the agent economy actually buying right now (March 2026)?** Not what they'll buy in 2028. What are agent developers, agent framework companies, and enterprises spending money on TODAY for agent safety/trust/governance? What's shipping, what's selling, what's getting budget?
3. **What use cases create "must-have" vs. "nice-to-have" demand?** Regulatory compliance is must-have. "Peace of mind" is nice-to-have. Where does agent trust scoring land for each customer type? What would make it must-have?
4. **What's the "seven lines of code" moment for Submantle?** Stripe's genius was making payment integration trivially easy. What's the equivalent for trust? What does the simplest possible integration look like that delivers immediate value?

### Codebase Files for Analysis
- prototype/api.py — current API surface, what's actually usable today
- prototype/agent_registry.py — registration flow, trust computation
- VISION.md — full product vision with all 5 customer types
- HANDOFF.md — current state, strategic pivot decisions
- CLAUDE.md — competitive landscape, design principles
- research/council-scoring-model/synthesis.md — scoring model council findings
- research/council-scoring-model/tension-report.md — unresolved tensions including the ~5/10 confidence gap
