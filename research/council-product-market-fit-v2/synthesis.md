# Council Synthesis: Who Pays for Agent Trust — and What Exactly Are They Buying?
## Date: 2026-03-12
## Vetted by: Orchestrator
## Alignment: Checked against Research Brief V2
## Challenge round: Refined positions, did NOT introduce new evidence. Phase 3 (Revision) skipped.

---

## Master Score Table

### Codebase Analyst Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Core Trust Mechanism Soundness | 8/10 | Formula correct, persistence works, tokens cryptographically sound |
| Business Integration Readiness | 2/10 | No auth, no billing, no SDK, no rate limiting |
| Bidirectional Trust Readiness | 1/10 | Settled decision exists nowhere in code |
| Directory/Marketplace Readiness | 3/10 | Data spine exists, no query interface |
| Agent Developer Experience | 4/10 | Registration works, but reason to register doesn't exist |
| Security for Commercial Use | 2/10 | Reporter auth absent, CORS wildcard |
| Demo Completeness | 5/10 → **split: 3/10 enterprise, 6/10 developer PoC** (per challenge round) |
| Distance to Paying Customer | 2/10 | MCP server, auth, billing, reporter auth all absent |

### External Researcher Scores — Market Evidence

| Dimension | Score | Notes |
|-----------|-------|-------|
| Market Existence | 9/10 | $240B security spend, $492M AI governance, real mandates live |
| Submantle Ability to Capture | 3/10 | No commercial infrastructure, no anchor, no MCP (from DA challenge) |
| Experian Model Validation | 8/10 | D&B, Sift, SSL cert market all confirm demand-side-pays |
| Bidirectional Trust Precedent | 7/10 | eBay, Uber, Airbnb, D&B DUNS all confirm mechanism works |
| Grassroots PLG Viability | 5/10 | Badge mechanism is real, but requires platform mandate to escape purgatory |
| Forcing Function Proximity | 7/10 | Gen/Vercel live, NIST 18-24 months, insurance emerging |

### Devil's Advocate Risk Scores (Post-Challenge Revision)

| Dimension | Phase 1 | Revised | Notes |
|-----------|---------|---------|-------|
| Agent self-registration motivation | 3/10 | 3/10 | No structural requirement |
| Bidirectional trust bootstrapping | 3/10 | 4/10 | Closer to present need than assumed |
| Grassroots growth mechanism | 4/10 | 4/10 | Purgatory is the base case |
| Directory revenue cannibalization | 2/10 | 4/10 | Per-call programmatic use case confirmed |
| Businesses pay per-query | 5/10 | 5/10 | Still unvalidated |
| Moat vs. build-in-house | 6/10 | 7/10 | Mastercard VI integration vector concrete |
| Single score commercial utility | 5/10 | 5/10 | Needs report context |
| One product, two propositions | 4/10 | 5/10 | CISO buyer unifies both |
| **Overall business confidence** | **4/10** | **4.5/10** | Market evidence stronger than Phase 1 assumed |

---

## High Confidence (agents converged with independent evidence)

These findings survived all three independent analyses AND the challenge round. Treat as resolved.

### 1. Zero customer conversations is the critical risk — and it's getting worse

**Triple convergence.** Devil's Advocate: "the single highest-risk finding — every feature added without a customer conversation is a bet with no data." External Researcher: "sign one brand anchor before opening agent registration." Codebase Analyst: "What the prototype does NOT prove: that businesses will pay, that agents will register, that the flywheel will start."

**Orchestrator assessment:** Two consecutive councils have now converged on this finding. The product scope has expanded (bidirectional trust, directory) while customer validation remains at zero. This is the most important finding in the entire council.

### 2. Reporter authentication is a ship-blocker with legal teeth

**Triple convergence.** Codebase Analyst found the plain-text reporter field — any string goes, no verification. Devil's Advocate escalated: "LAUNCH-BLOCKER with legal teeth" when combined with a public directory. External Researcher confirmed via credit bureau model: "Experian's entire legal framework is built around authenticated, accountable data furnishers."

**Challenge round escalation:** External Researcher: "the reporter field is worse than 'unauthenticated' — it's a plain text string. 'Google' and 'G00GLE' are both valid." This is not a feature gap. It's a liability.

### 3. MCP server is the product, not a feature

**Triple convergence.** Codebase Analyst: "the entire V1 strategy is trust bureau + MCP server. The MCP server does not exist — not even a stub." External Researcher: 10,000+ active MCP servers, 97M monthly SDK downloads — the ecosystem is real. Codebase Analyst challenge: "MCP is how we generate any trust data worth scoring" — without it, agents accumulate meaningless query counts against an awareness API.

**Orchestrator assessment:** The Codebase Analyst's challenge reframe is critical: MCP is not a growth feature, it's the trust data generation surface. Without it, the supply side cannot accumulate meaningful trust signals.

### 4. Bidirectional trust is NOT the V1 lead story

**Triple convergence.** External Researcher: "Lead with agent scoring. Introduce bidirectional scoring as a feature that grows in importance as the network matures." Codebase Analyst: "1/10 readiness — the settled decision exists nowhere in code." Devil's Advocate: "doubles the cold-start problem."

**Orchestrator assessment:** Bidirectional trust is a genuinely novel feature. It is not V1. It requires both parties to be registered, which requires network density that doesn't exist yet. The decision to build it is sound; the timing should be V2 after the core agent-trust-scoring flywheel proves itself.

### 5. The trust directory is a feature, not a business

**Triple convergence.** External Researcher: "Being a directory is a feature, not a business." Devil's Advocate: "cannibalizes revenue" (revised to 4/10 after acknowledging per-call programmatic queries are different from browsing). Codebase Analyst: "3/10 readiness."

**Challenge round resolution:** Codebase Analyst correctly distinguished browsing (free, human, due diligence) from runtime queries (paid, machine, per-call enforcement). The directory doesn't cannibalize the API — they serve different customers at different points. But the directory requires authenticated reporters before going public (legal exposure).

### 6. The moat is real in multi-agent environments only

**Triple convergence.** Devil's Advocate: "The moat exists for marketplace operators and enterprises with multi-agent environments. It is weak for single-agent companies." External Researcher: "OS-level observation is architecturally beyond what application-layer in-house builds can replicate." Codebase Analyst implicitly confirms through architecture analysis.

**Orchestrator assessment:** The V1 target must be marketplace operators and enterprises with multi-agent environments. Not individual businesses evaluating one agent.

---

## Recommended Approach

Based on the full council deliberation, the recommended path splits into two tracks: **market validation** (no code) and **commercial infrastructure** (code).

### Track 1: Market Validation (BEFORE more code)

**1a. Five customer conversations with businesses operating multi-agent environments.**
- Not to pitch. To listen. What problem do they have right now? How do they solve it? What would they pay for?
- Target: marketplace operators (Zapier AI, AWS Bedrock customers), enterprises with 3+ agents, agent framework companies
- This is the single action that changes business confidence from 4.5/10 to 7/10.
- *Source: Triple convergence. Cannot be delegated to a subagent.*

**1b. Explore Mastercard Verifiable Intent integration.**
- Launched March 5, 2026. Eight enterprise partners (IBM, Worldpay, Fiserv, Adyen). Uses SD-JWT — same standard as Submantle W3C VC attestations.
- A proof-of-concept showing a Submantle trust score inside a Mastercard VI record would be: a concrete demo, enterprise-credible, standards-aligned, and a candidate for the "anchor brand" problem.
- Devil's Advocate named this "the most actionable finding from the combined council."
- *Source: External Researcher finding, escalated by Devil's Advocate in challenge round.*

### Track 2: Commercial Infrastructure (code)

**2a. Reporter authentication — ship-blocker.**
- Create reporter registry or role-based registration
- Require verified reporter identity before accepting incident reports
- Track reporter accuracy over time (false report rate)
- This must be complete before any public demo or brand conversation
- *Source: Triple convergence from BOTH councils (scoring model + PMF).*

**2b. MCP server — the product.**
- This is the trust data generation surface, not just an integration feature
- Go SDK v1.4.0 available; needs: registration tool, trust query tool, incident report tool
- Without it, agents accumulate meaningless awareness-query counts, not behavioral trust signals
- *Source: Triple convergence. Codebase Analyst escalated urgency in challenge round.*

**2c. Business auth + billing infrastructure.**
- API key issuance for business queries
- Metering (count queries per business)
- The revenue mechanism has zero technical infrastructure currently
- *Source: Codebase Analyst: the `/api/verify` endpoint has a comment: "No auth required for V1 — billing comes later."*

### Build Sequence

The correct sequence (from combined council analysis):

1. **Reporter authentication** (ship-blocker — before any demo)
2. **Five customer conversations** (no code needed — validates direction)
3. **MCP server** (the product — enables meaningful trust data)
4. **Business auth + billing** (the revenue mechanism)
5. **Soft-delete deregistration** (prevents reputation laundering)
6. **has_history flag in API** (distinguishes new agents from average)

**What to defer:**
- Bidirectional trust schema → V2 (after network density proves itself)
- Trust directory features → after reporter auth and brand anchor
- W3C VC attestation issuance → accelerate if Mastercard VI partnership materializes

---

## Alternatives

### Alternative A: Build MCP server first, conversations later

**For:** MCP server is the product; without it there's nothing to demonstrate.
**Against:** External Researcher: "building the MCP server before having a brand customer is building supply infrastructure without a demand signal." Devil's Advocate: "every feature added without a customer conversation is a bet with no data."
**Verdict:** The customer conversations are low-cost and produce evidence no code can substitute for. Run conversations IN PARALLEL with MCP server build, not sequentially after.

### Alternative B: Lead with bidirectional trust as differentiator

**For:** Genuinely novel. No competitor has it.
**Against:** Triple convergence against it for V1. Requires both sides registered (doubles cold-start). 1/10 code readiness. Adds complexity to pitch.
**Verdict:** Keep as V2 feature. Mention in conversations to gauge interest, but don't build or lead with it.

### Alternative C: Build public trust directory as acquisition channel

**For:** External Researcher: "every agent displaying its Submantle score is an acquisition channel." Badge mechanism is real.
**Against:** Devil's Advocate: legal exposure when combined with unauthenticated reporters. Cannibalization risk for due-diligence use case.
**Verdict:** Directory after reporter authentication is complete. Badge mechanism is valuable. Public rankings are dangerous without authenticated reporters.

---

## Disagreements

### The anchor brand chicken-and-egg

**External Researcher:** "Sign one brand anchor before opening agent registration."
**Devil's Advocate:** "How? Brands won't commit to an empty trust bureau. The anchor brand problem is itself unsolved."
**Codebase Analyst:** "If you sign a brand before building auth + billing + reporter verification, you create a contractual obligation to deliver a system that doesn't exist."

**Orchestrator assessment:** The Devil's Advocate is right that the mechanism for acquiring an anchor brand without supply is unaddressed. The answer may be: (a) seed the registry with dogfood agents (Submantle's own), (b) pursue a platform partnership rather than a direct brand customer (Mastercard VI, Gen/Vercel-style), or (c) use the prototype demo to validate willingness to pay without requiring a production contract. This remains the council's largest open question.

### Whether awareness and trust belong under one brand

**Devil's Advocate:** Two different customer segments, two different buying motions.
**External Researcher:** The CISO buyer wants both — "which agents are running AND can I trust them?"
**Codebase Analyst:** Modules are genuinely decoupled. The trust API works without the awareness layer.

**Orchestrator assessment:** For enterprise CISOs, both belong together. For individual device owners, they're separate value propositions. This is a go-to-market question, not an architecture question. The Codebase Analyst confirmed the architecture supports both approaches. Lead with trust bureau for V1; add awareness as a secondary capability.

---

## Filtered Out

### "Agent-to-agent interaction scoring will be the primary growth mechanism"
Filtered by triple convergence: agent-to-agent trust building requires high-frequency interactions between continuously-running, registered agents. Most current agents are session-based and low-frequency. Incident reporting from brands provides score signal before interaction volume is meaningful. Not the V1 growth engine.

### "NIST compliance creates immediate demand"
Filtered: NIST agent standards arrive mid-2026 to 2027. The compliance demand is real but on an 18-24 month horizon. Current demand is operational ("what are my agents doing?"), not compliance-driven.

### "Data buyers as a customer type"
Filtered: Not V1. Requires 100K+ device scale. Focus on the one customer that pays first.

---

## Risks

### From Devil's Advocate, validated against other agents

| Risk | Severity | Validation |
|------|----------|------------|
| Zero customer conversations while product scope expands | CRITICAL | Triple convergence, two consecutive councils |
| Reporter authentication gap enables competitive sabotage AND legal liability | CRITICAL | Triple convergence, worse than previously assessed (plain-text field) |
| MCP server doesn't exist — stated V1 wedge is half-absent | HIGH | Triple convergence |
| Anchor brand chicken-and-egg unsolved | HIGH | Devil's Advocate challenge, unresolved |
| Grassroots growth stalls in "developer tool purgatory" | MEDIUM | Devil's Advocate, partially mitigated by badge mechanism |
| Bidirectional trust doubles cold-start if launched too early | MEDIUM | Triple convergence on deferring to V2 |
| Single score without report context insufficient for CISOs | MEDIUM | Devil's Advocate, validated by External Researcher |
| Solo founder cannot sustain simultaneous build + developer campaign | MEDIUM | Devil's Advocate, uncontested |

---

## The Most Actionable Finding

The Mastercard Verifiable Intent launch (March 5, 2026) is the most actionable external development. It was surfaced by the External Researcher and escalated by the Devil's Advocate as "the most actionable finding from the combined council." Key facts:

- Launched 7 days before this council
- 8 enterprise partners already (IBM, Worldpay, Fiserv, Adyen)
- Uses SD-JWT — exactly Submantle's planned attestation format
- Explicitly excludes behavioral trust history — Submantle fills the exact gap
- A Submantle trust score as a field inside a Mastercard VI record would solve: the "anchor brand" problem (enterprise partnership with distribution), the demo problem (concrete, standards-aligned, enterprise-credible), and the "why pay?" question for financial transaction platforms

This is not a V1 feature. It is a V1 relationship to pursue.

---

## Council Process Notes

- **Phase 1:** 3 agents dispatched in parallel (Codebase Analyst, External Researcher, Devil's Advocate). All completed independently.
- **Phase 2:** Challenge round completed. All 3 agents read each other's findings and wrote structured challenges. Multiple scores revised.
- **Phase 3:** Skipped. Challenges refined positions and produced useful corrections but did not introduce fundamentally new evidence.
- **Phase 4:** This synthesis.
- **Phase 5:** Tension Analysis (next).
