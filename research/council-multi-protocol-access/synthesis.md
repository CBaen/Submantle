# Council Synthesis: Multi-Protocol Access Strategy
## Date: 2026-03-12
## Vetted by: Orchestrator
## Alignment: Checked against Research Brief

---

## Shared Dimensions (cross-agent comparison)

| Shared Dimension | Codebase Analyst | External Researcher | Devil's Advocate | Avg | Spread |
|-----------------|-----------------|---------------------|------------------|-----|--------|
| Overall Risk | 9/10 | 8/10 | 2/10 | 6.3 | **7** |
| Reversibility | 10/10 | 10/10 | 5/10 | 8.3 | **5** |
| Evidence Confidence | 10/10 | 9/10 | 7/10 | 8.7 | **3** |

**Interpreting the spread:** The 7-point Overall Risk spread is the council's most significant divergence. It is NOT a disagreement about the same thing — it is two different risk questions producing two different scores. The Codebase Analyst measures "risk to existing code" (very low — MCP is additive). The Devil's Advocate measures "risk to the project" (higher — SDK instability, billing timing, attack surface). Both are correct for their scope. The synthesis must address both.

---

## Role-Specific Scores (per-agent depth — NOT cross-compared)

### Codebase Analyst: Implementation Readiness
| Dimension | Score |
|-----------|-------|
| Feasibility | 9/10 |
| Blast Radius | 9/10 |
| Pattern Consistency | 9/10 |
| Dependency Risk | 9/10 |

**Summary:** The codebase is structurally ready for multi-protocol today. AgentRegistry is protocol-agnostic. MCP = one new file or 3-line fastapi-mcp mount, zero changes to core modules. High confidence, line-number grounded.

### External Researcher: Ecosystem Positioning
| Dimension | Score (Approach B: REST+MCP) |
|-----------|------|
| Relevance | 10/10 |
| Maturity | 8/10 |
| Community Health | 9/10 |
| Integration Effort | 9/10 |

**Summary:** MCP is the de facto agent protocol of 2026 (97M monthly downloads). fastapi-mcp provides 3-line integration with auth passthrough. Spamhaus graduated access model is the strongest external precedent. CLI deferred. Exchange hub rejected.

### Devil's Advocate: Failure Analysis
| Dimension | Score |
|-----------|-------|
| Failure Probability | 3/10 |
| Failure Severity | 3/10 |
| Assumption Fragility | 2/10 |
| Hidden Complexity | 2/10 |

**Summary:** MCP SDK v2 breaking changes are imminent. Incident reporting via MCP is a prompt injection surface. Open multi-protocol before billing trains market toward free. For a solo founder, three protocols = three products. Real risks, especially strategic ones.

---

## High Confidence (agents converged with independent evidence)

These findings had 3/3 independent agreement via different evidence chains:

1. **AgentRegistry is already protocol-agnostic.** CA verified from imports (zero HTTP dependencies at `agent_registry.py` lines 37-46). ER confirmed from architectural pattern. DA implicitly confirmed by not flagging it as a risk. Multi-protocol is additive code, not a refactor.

2. **"Exchange hub" framing must be rejected.** CA: no session layer, routing layer, or mediation exists — blast radius to build it is a rewrite. ER: no precedent in trust/reputation infrastructure; "hub" implies marketplace. DA: violates "always aware, never acting" — Submantle in agent execution paths = acting as mediator. **Replacement framing: "multiple access channels to one trust ledger."**

3. **CLI should be deferred.** CA: CLI calls the same AgentRegistry methods, zero differentiation. ER: CLI is developer tooling, not runtime agent calls. DA: no CLI use case not served by `curl`. Defer until Go production rewrite, where it's a natural byproduct.

4. **Business API keys must remain on the near-term roadmap.** CA: the missing "third door" in the auth model. ER: Spamhaus graduated model requires a commercial tier. DA: open multi-protocol without billing trains market toward free. Convergence on timing urgency, not just need.

5. **Agent tokens and business API keys must be architecturally separate.** CA and DA independently reached this from codebase analysis. Two credential types serving two constituencies (agents recording activity vs. businesses purchasing lookups). Do not unify them.

---

## Recommended Approach

**REST + MCP via fastapi-mcp, with read-only MCP scope and rate limiting prerequisites.**

This recommendation synthesizes the strongest elements from all three analyses:

### From the Codebase Analyst:
- The implementation path is additive (zero changes to core modules)
- The initialization order invariant must be preserved or documented
- Privacy state cross-process issues are eliminated by the fastapi-mcp in-process approach

### From the External Researcher:
- fastapi-mcp provides 3-line integration with auth passthrough — transforms Wave 5 from a multi-week build to a focused addition
- Streamable HTTP transport resolves the daemon/subprocess contradiction the DA raised
- Spamhaus graduated model is the right access precedent: open reads, gated business tier

### From the Devil's Advocate:
- Expose only read endpoints via MCP initially (score queries, agent lookup) — keep write endpoints (incident reporting, registration) REST-only until reporter identity can be verified
- Add rate limiting to open endpoints before publishing MCP — prevents abuse multiplication
- Ship business API keys in close sequence with MCP, not Wave 11

### Concrete Implementation Sequence:

1. **Add rate limiting to open REST endpoints** (verify, agents list) — prerequisite, not optional
2. **Mount fastapi-mcp on api.py** — selective endpoint exposure, read-only scope (verify, health, status)
3. **Validate HMAC auth passthrough** — confirm fastapi-mcp correctly propagates Bearer tokens for authenticated MCP calls
4. **Ship business API keys** — Stripe Payment Links for commercial score access, separate from agent tokens
5. **Expand MCP scope** — add authenticated write operations only after reporter identity validation exists

### What This Does NOT Include:
- CLI tool (deferred to Go rewrite)
- Plugins (no constituency, defer indefinitely)
- Exchange hub routing (rejected)
- Incident reporting via MCP (deferred until reporter identity verification)
- stdio MCP transport (HTTP via fastapi-mcp instead)

---

## Alternatives

### Alternative A: Build standalone MCP server (`mcp_server.py`)

The Codebase Analyst's original analysis supports this — one new file, AgentRegistry instantiated directly. Viable if fastapi-mcp proves incompatible with Submantle's HMAC auth scheme.

**Tradeoff:** More code (100-150 lines vs. 3 lines), but full control. Introduces process-boundary issues (privacy state staleness, separate EventBus). Recommended as fallback only.

### Alternative B: Defer MCP entirely, build billing first

The Devil's Advocate's strongest argument — billing before distribution. Ship business API keys and Stripe integration first, then add MCP when there's revenue to protect.

**Tradeoff:** Eliminates SDK stability risk and billing timing concern. But delays agent-facing distribution — the primary product use case. The 12-18 month competitive window argues against waiting. Recommended only if fastapi-mcp integration fails or SDK v2 ships before MCP is ready.

### Alternative C: Full MCP including write operations from Day 1

The most aggressive approach. All endpoints exposed via MCP, including incident reporting and registration.

**Tradeoff:** Maximum agent capability, but creates the prompt injection surface the Devil's Advocate identified. An agent running in an LLM context could be manipulated into filing false incidents. Not recommended without reporter identity verification.

---

## Disagreements

### Overall Risk: Implementation vs. Project
CA scores 9/10 (implementation risk is minimal). DA scores 2/10 (project risk is significant). **Resolution:** Both are correct for their scope. The implementation is safe. The strategic risks (SDK stability, billing timing, attack surface) are real but manageable through the sequencing recommended above. The synthesis adopts a blended position: implementation risk ~9, project risk ~6, yielding an overall assessment of "proceed with sequencing precautions."

### Reversibility: Pre-publication vs. Post-publication
CA and ER score 10/10. DA scores 5/10. **Resolution:** Reversibility is timeframe-dependent. Before publication: ~10 (delete a file or remove 3 lines). After external agents integrate: ~7 (removal is a breaking change for integrators). The synthesis adopts 9/10 for the current prototype stage, with a note that this drops to ~7 once the MCP endpoint is documented and consumed.

### MCP SDK Stability
ER presents MCP ecosystem as mature (97M downloads). DA presents MCP SDK as unstable (v2 breaking changes). **Resolution:** The ecosystem is mature; the Python SDK is churning. fastapi-mcp abstracts the SDK, reducing direct exposure. The risk is a dependency chain (Submantle → fastapi-mcp → MCP SDK). Manageable for a prototype; worth tracking for production Go rewrite (which would use the Go MCP SDK v1.4.0, which is more stable).

---

## Filtered Out

1. **"Neutral means supporting every protocol" argument** — The External Researcher found that neutrality in infrastructure precedents (DNS, RATS RFC 9334) means not favoring one agent builder over another, not supporting every transport. Protocol choice is about use case fit, not fairness. Filtered because it was the weakest argument for multi-protocol.

2. **CORS concerns** — The DA flagged `allow_origins=["*"]` as a risk. This is true but not specific to multi-protocol — it's a general hardening task. Filtered as out of scope for this council.

3. **SQLite concurrent writer concerns** — The DA flagged concurrent multi-process writes. WAL mode serializes these safely. The CA confirmed this. The fastapi-mcp in-process approach eliminates the concern entirely. Filtered as resolved.

---

## Risks

1. **fastapi-mcp v0.x stability.** The library is v0.4.0 with 11.7k stars. It is not v1.0. If it breaks or is abandoned, fallback to standalone `mcp_server.py` (Alternative A). Mitigation: pin version, monitor releases.

2. **MCP SDK v2 breaking changes cascade.** If MCP Python SDK v2 ships with breaking transport changes, fastapi-mcp must update, then Submantle must update. This is a dependency chain. Mitigation: fastapi-mcp abstracts the SDK; the Go production rewrite will use the more stable Go MCP SDK.

3. **Billing timing.** Open MCP score queries before business API keys are live creates a window where the market treats trust data as free. Mitigation: ship business API keys in close sequence with MCP (weeks, not months apart).

4. **Prompt injection via MCP write operations.** If incident reporting is exposed via MCP, an LLM-manipulated agent could file false incidents. Mitigation: MCP starts read-only; write operations added only after reporter identity verification.

5. **HMAC auth passthrough unverified.** fastapi-mcp documentation shows OAuth/Bearer auth passthrough, but Submantle uses a custom HMAC scheme. The passthrough needs validation before shipping. Mitigation: test during implementation; fall back to Alternative A if incompatible.
