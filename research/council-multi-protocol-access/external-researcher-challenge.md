# External Researcher Challenge: Multi-Protocol Access Strategy
**Date:** 2026-03-12
**Role:** External Researcher
**Challenging:** Codebase Analyst Findings + Devil's Advocate Findings

---

## 1. Reasoning Divergence Points

### Divergence A: Codebase Analyst on MCP Implementation Effort (Their Feasibility: 9)

The Codebase Analyst concludes that MCP = "one new file, zero changes to existing code" and frames it as a Wave 5 feature requiring its own build track. Their reasoning: the service layer is clean, so the adapter is easy to write from scratch.

**Where the chain diverges:** The Analyst is reasoning from the codebase outward, without knowing that `fastapi-mcp` (github.com/tadata-org/fastapi_mcp) exists. If you know that library, the implementation is not "one new file" — it is **three lines added to the existing `api.py`**, with no new file required at all. The auth passthrough is built-in; existing FastAPI Bearer token dependencies propagate automatically into the MCP layer.

This is not a small difference. The Analyst's framing ("Wave 5 feature") implies a future build that is weeks away. The library evidence makes it a weekend addition that could happen in Wave 6 or earlier. The Feasibility score of 9 is actually too conservative — it should be 10 because the hard part (auth, routing, transport) is already solved by the library.

**Implication:** The Analyst's build priority table and blast-radius analysis are correct in direction but wrong in magnitude for MCP specifically. This changes the sequencing recommendation.

---

### Divergence B: Devil's Advocate on MCP Daemon/Subprocess Contradiction (Their Failure Probability: 3)

The Devil's Advocate raises "daemon vs subprocess" as an unresolved architectural contradiction. Their framing: MCP stdio is a subprocess model, Submantle is a daemon, and these are "architecturally opposed."

**Where the chain diverges:** The Devil's Advocate is reasoning about a specific deployment topology (stdio-only MCP), not the full MCP transport picture. My research found that the MCP 2026 roadmap explicitly states **Streamable HTTP is consolidating as the production remote transport**. The "subprocess" problem only applies to stdio. For remote agents connecting to Submantle, the transport is Streamable HTTP, not stdio. This means the daemon/subprocess contradiction is real only for local tool usage (Claude Desktop) — not for the agent-to-Submantle integration that is actually the product use case.

Furthermore, `fastapi-mcp` mounts the MCP interface directly onto the existing FastAPI HTTP process. There is no separate subprocess at all. The entire "daemon vs subprocess" objection evaporates when the implementation is HTTP-based rather than stdio-based.

The Devil's Advocate scored this as a real failure mode. It is not — it is a misdiagnosis of the architecture based on stdio-centric MCP thinking.

---

### Divergence C: Devil's Advocate on Open Access Killing Revenue (Their Failure Probability for "3E: Open Access Destroys Revenue")

The Devil's Advocate argues: "Free multi-protocol access trains users that data is free. Auth later = breaking change across N protocols."

**Where the chain diverges:** This conflates "free" with "no business model." My research shows three major neutral infrastructure services that have successfully maintained open score access alongside commercial tiers: Spamhaus (25 years), Certificate Transparency logs (10+ years), and DNS (40+ years). The pattern is consistent: open read access drives adoption; gated business access (SLA, volume, webhooks) drives revenue. These are separate value propositions for separate constituencies.

The "breaking change" framing is specifically wrong. Adding auth to the score query endpoint after it is open would be a breaking change. But Submantle's revenue model does NOT require gating score queries. It requires gating **business API keys for SLA-backed, high-volume, webhook-enabled business access**. These are new endpoints/features, not a lock added to existing open endpoints. There is no breaking change in that sequence.

The open score query (`GET /api/verify/{agent_name}`) can and should remain open forever — that is what drives adoption, which feeds the score database, which makes business access valuable. The Devil's Advocate is arguing against the architecture of its own closest analogues.

---

### Divergence D: Devil's Advocate on "Three Protocols = Three Products" (Their Hidden Complexity: 2)

The Devil's Advocate flags the solo founder maintenance burden as a genuine risk. I partially agree, but the framing is wrong.

**Where the chain diverges:** For REST + MCP via fastapi-mcp, there is no meaningful maintenance multiplier. The library handles the MCP protocol layer. A bug in the scoring logic is fixed once in `agent_registry.py` and is automatically fixed in both REST and MCP layers. The "same vulnerability in three code paths" objection (Finding 3G) applies if MCP is built as a separate service. It does not apply if MCP is a thin mount on the same FastAPI app — which is exactly what fastapi-mcp does.

The Devil's Advocate scores Hidden Complexity at 2/10 (suggesting very low hidden complexity) but scores Overall Risk at 2/10 (low risk). These are actually consistent — my objection is to the reasoning, not the score. The DA appears to believe complexity is manageable, which is correct for the right implementation (fastapi-mcp) but for the wrong reasons (they don't appear to know about fastapi-mcp).

---

## 2. Score Challenges

### Codebase Analyst — Shared Dimensions

**Overall Risk: 9 (CA) vs. my implicit 8 for REST+MCP combined**

The CA's 9 for "Core logic decoupled from transport" is defensible for the existing codebase. My slight discount to 8 comes from the SDK dependency risk the CA did not evaluate: fastapi-mcp is v0.4.0, not v1.0. The library is actively maintained with 11.7k stars, but a v0.x library in production carries minor version risk. This is not a serious risk, but it is not a 9 either.

**Reversibility: 10 (CA) — I agree**

The CA's 10 for "delete mcp_server.py" is directionally correct. With fastapi-mcp it would be "remove 3 lines and one import." No downstream coupling. Full agreement.

**Evidence Confidence: 10 (CA) — I agree with a caveat**

The CA's 10 is earned for codebase claims — every line number is cited and verifiable. My caveat: the CA's confidence is bounded to what the codebase shows and does not incorporate external ecosystem evidence. The CA correctly notes the service layer is clean; they correctly identify the blast radius. But they do not evaluate fastapi-mcp, the MCP adoption data (97M downloads), or the SDK stability question. Their confidence in their own evidence is warranted; the scope of their evidence is narrow.

---

### Devil's Advocate — Shared Dimensions

**Overall Risk: 2/10 (DA)**

I read this as "low risk overall," which I agree with for REST+MCP via fastapi-mcp. The DA arrives at the right destination via partially wrong reasoning (stdio contradiction, maintenance multiplier). The score is correct; the path has errors.

**Reversibility: 5/10 (DA)**

The DA scores reversibility lower than the CA (5 vs. 10). I think the truth is closer to the CA's position. The DA's reasoning would be correct if MCP were built as a standalone service with its own auth stack, database connections, and deployment config. With fastapi-mcp mounting on the existing app, reversibility is near-10. The DA is scoring a harder implementation scenario than the one the evidence supports.

**Evidence Confidence: 7/10 (DA)**

Appropriate. The DA's codebase observations are correct (open endpoints, HMAC limitations, CORS). The research-based failure modes are mostly valid as theoretical vectors, but some (like the daemon/subprocess claim) are based on incomplete MCP transport knowledge. 7 is right.

---

## 3. Evidence Gaps

### Gap A: Neither Agent Evaluated fastapi-mcp

The single most consequential gap in both analyses is the absence of `fastapi-mcp`. The Codebase Analyst built a detailed blast-radius analysis for an MCP server as a new standalone file. The Devil's Advocate raised the subprocess/daemon contradiction as a real objection. Both of these analyses are invalidated or significantly modified by the existence of a library that:

- Mounts MCP directly on the existing FastAPI process (no subprocess, no new file)
- Passes auth through automatically
- Has 11.7k stars, v0.4.0, actively maintained
- Requires 3 lines of code

Neither agent's findings address this. This is the most important piece of evidence for the council's actual decision.

---

### Gap B: Devil's Advocate Did Not Distinguish MCP Transport Modes

The DA's Observation 3 ("HMAC token mechanism doesn't survive multi-protocol — MCP stdio = no headers") and the daemon/subprocess objection both assume stdio as the MCP transport. The MCP 2026 roadmap distinguishes:

- **stdio:** Local tool process (Claude Desktop, local agents). Headers not applicable; auth is different.
- **Streamable HTTP:** Remote agents connecting over network. Standard HTTP headers, Bearer tokens work exactly as they do in REST.

For Submantle's actual use case (remote agents checking trust scores), the transport is Streamable HTTP, not stdio. The DA's auth objection does not apply to the primary use case. The DA should have differentiated between these two modes and scoped the risk appropriately.

---

### Gap C: Codebase Analyst Did Not Evaluate SDK Stability Risk

The CA gives Dependency Risk a 9 but does not evaluate third-party library risk at all — only "upstream dependencies" meaning the existing Python codebase. fastapi-mcp is v0.4.x. The DA raised MCP Python SDK v2 breaking changes as a concern (Finding 3A). Neither agent connected these: fastapi-mcp sits on top of the MCP SDK, meaning an MCP SDK v2 breaking change could cascade into fastapi-mcp. This is a dependency chain the CA's analysis did not trace.

My assessment: this is real but manageable. fastapi-mcp is actively maintained and will likely track SDK changes. The risk is a lag window between SDK update and library update. Not a showstopper, but worth acknowledging in the risk ledger.

---

### Gap D: Neither Agent Addressed the Incident Reporting via MCP Surface

The DA mentioned "MCP incident reporting = prompt injection surface" (Strongest Objection 4). The CA's blast-radius analysis focused on the score query endpoints, not the incident pipeline. My research found that incident reporting in the current code has minimal validation (self-ping rejection + 24h dedup), which the DA correctly identified.

But the right response to this is not "don't add MCP" — it is "don't expose incident reporting endpoints via MCP." The fastapi-mcp library allows selective endpoint exposure. You can mount the MCP interface on score queries only (the read path) and keep the incident reporting and registration endpoints REST-only. Neither agent proposed this surgical scoping.

---

## 4. Surprises — What Changed My Thinking

**The Devil's Advocate's auth architecture point landed harder than expected.**

I had framed the open score query as straightforwardly correct, backed by Spamhaus/DNS/CT log precedents. The DA's point about open multi-protocol before auth is structurally sound if you read it differently: the risk is not "open queries are wrong" but "open queries across multiple protocols before rate limiting is in place means a new attack surface appears with each new protocol."

My Phase 1 recommendation was: add MCP immediately. But the DA's point implies the correct sequence is: add rate limiting to open endpoints first, then add MCP. This is a sequencing note, not a reversal. The DA's 3E failure mode is a valid pre-condition check, not a reason to avoid multi-protocol.

**The Codebase Analyst's auth architecture observation is more important than it appeared.**

The CA notes: "Auth Token Is Agent-Scoped, Not Business-Scoped" and "Business API keys are the gating mechanism that matters." This aligns exactly with my Spamhaus/VirusTotal research finding that two different auth mechanisms serve two different constituencies. The CA reached the same conclusion from codebase structure alone. This is the convergence point that matters most for the council.

---

## 5. Agreements — High-Confidence Convergence Points

All three analyses arrived at these independently. These are the council's strongest signals:

**Agreement 1: The service layer is already protocol-agnostic.**
CA (from code), me (from architectural pattern), DA (implicitly, by not flagging it as a risk). `AgentRegistry` does not know what called it. Multi-protocol is addition, not refactoring.

**Agreement 2: The "exchange hub" framing should be rejected.**
CA (calls it significant blast radius, violates design principles), me (hub implies routing, turns Submantle into marketplace), DA (scope creep). Three independent analyses, same verdict.

**Agreement 3: Business API keys are the right revenue gate.**
CA (identifies it as the gating mechanism), me (Spamhaus/VirusTotal evidence for separate business tier), DA (implies auth is needed before revenue). The disagreement is only about when and how — not whether.

**Agreement 4: MCP is the right protocol for agent access.**
CA (architecturally feasible, additive), me (97M downloads, every major framework), DA (does not recommend against MCP, only raises implementation considerations). No agent recommends staying REST-only.

**Agreement 5: CLI is low priority.**
CA (does not recommend it as part of MCP wave), me (developer tooling only, not runtime agent calls), DA (no CLI use case not served by curl). Independent convergence.

---

## Summary of Strongest Challenges

1. **fastapi-mcp invalidates the "Wave 5 build" framing.** The Codebase Analyst's implementation path and the Devil's Advocate's subprocess objection both assume a custom MCP server. The library makes MCP a 3-line mount. This is the most impactful divergence.

2. **The daemon/subprocess contradiction is a stdio-specific concern.** The Devil's Advocate's architectural objection does not apply to the production remote transport (Streamable HTTP). The objection is valid only for local Claude Desktop integration, not for the agent-to-Submantle use case.

3. **Open access is not the revenue risk — missing rate limiting is.** The DA's "open access destroys revenue" argument is wrong about the mechanism. The risk is gaming and abuse via unlimited open calls, not that users learn data is "free." Rate limiting on open endpoints + gating only the business tier is the correct architecture, supported by 25 years of Spamhaus precedent.

4. **Selective MCP endpoint exposure resolves the incident reporting attack surface.** Neither agent proposed exposing read-only endpoints via MCP while keeping write endpoints REST-only. This eliminates the prompt injection concern while preserving the adoption benefit.
