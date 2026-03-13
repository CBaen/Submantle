# Devil's Advocate Challenge: Multi-Protocol Access Strategy
**Council Role:** Devil's Advocate — Phase 2 Review
**Date:** 2026-03-12
**Reviewing:** Codebase Analyst Findings + External Researcher Findings

---

## Prefatory Note on Method

A good challenge is not contrarianism. Where the other agents are right, I say so — convergence is evidence. Where they are wrong or incomplete, I cite exactly what's wrong. This document leads with divergence because that's where synthesis earns its value.

---

## 1. Reasoning Divergence Points

These are the specific steps where my chain of reasoning departs from theirs.

---

### Divergence A: The Codebase Analyst's "Zero Changes to Existing Code" Claim

**Their claim:** "MCP Server: ONE new file, ZERO changes to existing code. '100-150 line file'"

**Where my reasoning diverges:** This is true only for a read-only MCP server. The divergence happens at Step 2 of my analysis: the Codebase Analyst found that `AgentRegistry` is protocol-agnostic (true), but did not trace what happens when `report_incident()` is called via MCP tool call versus REST.

The existing `record_incident()` function requires `reporter` to be a non-empty string and non-self-reporter. Nothing else. When called via MCP tool call, the `reporter` field is populated by whatever the LLM put in the tool call parameters — not a verified business identity. This is not "zero changes" territory; it's "the existing vulnerability is now reachable via a new path." The MCP server file is new. The attack surface is not.

**Concretely:** An agent running inside Claude Desktop calls the `report_incident` MCP tool with `reporter="CompetitorB"` and `agent_name="CompetitorA"`. This call succeeds with the current codebase. The new file did not introduce the bug, but it made the bug reachable without an HTTP client. The Codebase Analyst's blast radius analysis is accurate for happy-path code; it misses the security blast radius.

---

### Divergence B: The External Researcher's fastapi-mcp Score

**Their claim:** Approach B (REST + MCP via fastapi-mcp) scores Overall Risk 8/10, Reversibility 10/10.

**Where my reasoning diverges:** The External Researcher's fastapi-mcp discovery is the most useful finding in either report, and I agree it changes the implementation calculus significantly. But the score inflation happens at the reversibility step.

fastapi-mcp mounts an MCP server as an HTTP endpoint (`/mcp`). The auth passthrough is built-in. This addresses my Observation 3 (HMAC tokens don't survive multi-protocol) by inheriting FastAPI's existing auth middleware — a real mitigation, not a workaround.

However, Reversibility 10/10 requires that published integrations can be removed without external cost. If fastapi-mcp is a 3-line mount, it's also a 3-line unmount. But the reversibility clock starts when the first external agent integrates with the MCP endpoint, not when the code ships. The External Researcher implicitly scores the implementation reversibility (high), not the deployment reversibility (lower). Once Submantle publishes an MCP endpoint and an agent builder documents their integration against it, removing it is a breaking change. My score for Reversibility on Approach B is 8/10, not 10/10.

---

### Divergence C: The External Researcher's CLI Framing

**Their claim:** "CLI appropriate for developer workflow only, not runtime agent calls"

**Where I agree up to a point:** This conclusion is correct. The divergence is in the conclusion's implication. The External Researcher frames CLI as "deferred" — appropriate, but not now. My analysis reaches a harder conclusion: there is no Submantle use case that CLI serves better than `curl`. Developer workflow IS already served by `curl`, `httpie`, or any HTTP client. A CLI tool is a developer experience investment, not a capability investment. For a solo founder on a 12-18 month competitive clock, "deferred" is effectively "never" — and that's the right answer.

The External Researcher's CLI scorecard gives it Reversibility 8/10. But you cannot reverse the decision to defer CLI — that's not a reversibility question. The question should be: once built, how reversible is it? Answer: low. Published CLI tools have users. Deprecating a CLI breaks shell scripts and CI pipelines. The 8/10 score is measuring the wrong thing.

---

### Divergence D: MCP Transport Stability — External Researcher Understates the Risk

**Their claim:** "Streamable HTTP consolidating as production remote transport; stdio for local/desktop" — presented as settled fact.

**My evidence from Phase 1:** The MCP Python SDK has "main — v2 development (breaking changes)" active. SSE transport is being deprecated (issue #2278). The stdio transport has known bug: server processes survive parent termination (issue #2231). These are not edge cases — they are open issues in the active v2 development branch.

**The divergence:** The External Researcher presents the protocol landscape as stable enough to build against. My reading of the SDK repository says v1.x is in maintenance and v2 has architectural redesigns in flight. fastapi-mcp's 3-line integration is built on top of the Python SDK. If the SDK's transport layer is redesigned in v2, fastapi-mcp must update to match, and Submantle's integration must update to match fastapi-mcp. This is a dependency chain, not a single update. The External Researcher's Evidence Confidence score of 9/10 for Approach B assumes the fastapi-mcp library tracks SDK changes reliably. That assumption is unverified.

---

### Divergence E: Where "Exchange Hub" Danger Actually Lives

**Both agents:** Correctly identify exchange hub as problematic.

**The divergence is in the mechanism.** The Codebase Analyst says it "violates 'always aware, never acting.'" The External Researcher says the "framing should be rejected." Both are right about the conclusion but imprecise about the mechanism.

The deeper problem is this: "exchange hub" is dangerous because it implies Submantle becomes the bottleneck through which agent-to-agent interactions flow. The IETF RATS RFC 9334 Passport Model that Submantle maps to has a specific property: the Relying Party (brand) queries the Verifier (Submantle) independently. There is no MCP channel through which Agent A can affect Agent B's score in real time. Once Submantle adds an MCP server with `report_incident` as a callable tool, it has inserted itself into the agent execution loop. The "always aware, never acting" principle isn't about blocking — it's about not being in the execution path. An MCP tool that agents call during inference IS in the execution path.

My specific objection the Codebase Analyst missed: the blast radius for an MCP server with `report_incident` as a tool is not "one new file." It's "Submantle is now inside agent execution contexts," which is an architectural position change, not a file count.

---

## 2. Score Challenges

### Challenge to Codebase Analyst: Overall Risk 9/10 for REST + MCP

The Codebase Analyst gives Overall Risk 9/10 (high confidence, low risk) to the overall multi-protocol proposal. This score is based on "blast radius to existing code" — and on that dimension, the 9 is accurate.

But the shared dimension Overall Risk is supposed to capture the full risk envelope, not just implementation risk. Three risks the Codebase Analyst's score does not capture:

1. **Deployment risk:** New attack surfaces for existing unpatched vulnerabilities
2. **Strategic risk:** Open multi-protocol access before billing makes monetization harder
3. **Maintenance risk:** A solo founder maintaining three protocol surfaces while also building Waves 1-4

If Overall Risk means "risk to existing code," 9/10 is justified. If it means "risk to the project," the score is closer to 5/10. The Codebase Analyst should define which they mean, because synthesis council members will otherwise weight these scores against each other incorrectly.

---

### Challenge to External Researcher: Evidence Confidence 9/10 for Approach B

The External Researcher gives Evidence Confidence 9/10 to Approach B (REST + MCP via fastapi-mcp). The justification is that fastapi-mcp exists, has 11.7k stars, and has working auth passthrough.

This is evidence that fastapi-mcp works. It is not evidence that:
- fastapi-mcp will track the MCP SDK v2 breaking changes on a timeline compatible with Submantle's build schedule
- Auth passthrough works correctly for Submantle's specific HMAC token scheme (not OAuth, not API key — a custom HMAC scheme that is agent-scoped, not business-scoped)
- The 3-line integration handles the daemon/subprocess architectural conflict I identified in Phase 1

My Evidence Confidence for Approach B is 7/10. The 2-point deduction is for unverified assumptions about SDK compatibility and HMAC auth passthrough behavior.

---

### Challenge to Codebase Analyst: Reversibility 10/10

The Codebase Analyst gives Reversibility 10/10 with the note that "you can just delete the MCP server file." This is implementation reversibility, not deployment reversibility. Once the MCP endpoint is published and integrated by external agents, removing it is not free. I score Reversibility at 8/10 for the same reason I challenge the External Researcher's 10/10 on this dimension.

---

## 3. Evidence Gaps

### Gap A: Neither Agent Addressed the Daemon/Subprocess Architectural Conflict

My Phase 1 analysis identified this conflict: Submantle is designed as an always-running daemon (5-second scan cache, persistent privacy state, in-memory state across sessions). MCP stdio makes it a subprocess (started on demand, killed after use). These are structurally opposed.

The fastapi-mcp discovery partially resolves this (HTTP transport doesn't require subprocess model), but neither agent explicitly addressed it. The Codebase Analyst's "zero changes to existing code" claim implicitly assumes the MCP server would be a thin HTTP wrapper over the existing REST API — which is exactly the fastapi-mcp pattern. That assumption should be stated explicitly, because it determines whether the daemon/subprocess conflict applies.

---

### Gap B: Neither Agent Addressed the Billing Path in Multi-Protocol Context

My Phase 1 analysis identified that open unauthenticated access on all protocols trains customers that data is free, making the billing transition harder. Neither agent's findings address this. The Codebase Analyst notes "Auth Token Is Agent-Scoped, Not Business-Scoped" as a finding but doesn't connect it to the billing path problem. The External Researcher recommends "Open score queries + gated business access (Spamhaus model)" but doesn't address what happens to existing MCP integrations when the gating is added.

This is a gap, not a disagreement — neither agent found evidence against my concern. Absence of evidence is not evidence of absence.

---

### Gap C: External Researcher Did Not Check MCP SDK Repository State

The External Researcher's finding that "Streamable HTTP consolidating as production remote transport" is accurate for the spec. But the MCP Python SDK GitHub was not checked. The SDK is what Submantle (or fastapi-mcp) would actually run against. My finding that v2 development has breaking changes in flight is from the SDK repository, not the spec. These are different stability signals.

---

### Gap D: Neither Agent Addressed Reporter Identity in MCP Context

Both agents noted that `AgentRegistry` is protocol-agnostic. Neither traced what happens when `report_incident()` is called via MCP — specifically, that the reporter identity comes from LLM-generated tool call parameters, not a verified HTTP token. This is the prompt injection attack surface I documented in Phase 1. If the MCP server exposes only read operations (verify, query), this gap doesn't apply. But the build priority table has the MCP server as the access path for the product — agents query Submantle — and that implies write operations (query accumulation) are also exposed.

---

## 4. Surprises — What Changed My Thinking

### Surprise 1: fastapi-mcp is a genuine mitigation

My Phase 1 most serious objection was: "HMAC tokens don't survive multi-protocol — three protocols means three credential-passing conventions." The External Researcher's discovery of fastapi-mcp directly addresses this. The library inherits FastAPI's existing auth middleware, meaning the HTTP-based HMAC scheme would work unchanged for MCP over HTTP.

This is a real update. I was modeling MCP as stdio-only, which requires passing credentials in JSON-RPC params. If fastapi-mcp mounts MCP over HTTP, the credential problem is largely solved. My Failure Mode 3A (HMAC token survival) needs to be qualified: it applies to stdio transport, not HTTP transport via fastapi-mcp.

**Updated position:** MCP via fastapi-mcp over HTTP is meaningfully safer than MCP via Python SDK stdio. The External Researcher's 3-line finding changed my recommendation on implementation path, even if it doesn't change my core objections about attack surface and billing timing.

---

### Surprise 2: The Codebase Analyst confirmed my Observation 6 about auth architecture

I observed that auth tokens are agent-scoped, not business-scoped, and that this creates a problem for business API keys. The Codebase Analyst independently found "Auth architecture: keep agent tokens and business keys separate" as a key finding. This is convergence — two separate analyses of the same codebase reaching the same architectural constraint. This should be treated as high-confidence.

---

### Surprise 3: Neither agent challenged the Wave 5 priority ordering

The build priority table in CLAUDE.md has "Wave 5: MCP server (Python, stdio)" and "Business API keys + Stripe Payment Links" both listed as NEXT. My Phase 1 analysis argued that MCP with no billing produces no revenue, while billing with no MCP produces revenue. Neither agent challenged this priority ordering or argued the other direction. This is a notable silence. Either both agents implicitly agree with the ordering (build MCP and billing in parallel), or neither examined the priority conflict. The council synthesis should address this explicitly.

---

## 5. Agreements — High-Confidence Convergence

These are findings where Devil's Advocate Phase 1 analysis and both agents' independent work converge. Treat these as high-confidence.

### Agreement 1: "Exchange hub" framing must be rejected

All three analyses independently concluded that "exchange hub" is the wrong framing. The Codebase Analyst says it violates "always aware, never acting." The External Researcher says "framing should be rejected — use 'multiple access channels to one trust ledger' instead." My analysis says it implies mediation and moves Submantle into agent execution paths. Three independent paths to the same conclusion: strong evidence this is correct.

**Council recommendation:** The "exchange hub" framing is out. "Multiple access channels to one trust ledger" is the replacement.

---

### Agreement 2: CLI should be deferred

Both the External Researcher (CLI appropriate for developer workflow only, not runtime agent calls) and my Phase 1 analysis (no use case not already served by curl) recommend against building CLI now. The Codebase Analyst also implicitly excludes CLI from the high-score tier.

**Council recommendation:** CLI is deferred until the Go production rewrite, where it could be built as a byproduct of the Go client library.

---

### Agreement 3: AgentRegistry is already protocol-agnostic

The Codebase Analyst verified this from the code; my Phase 1 analysis assumed it from the architecture. Independent confirmation: `AgentRegistry` does not know about HTTP, JSON, or any transport. Protocol adapters are genuinely additive.

---

### Agreement 4: MCP adoption is real and worth building against

Despite my objections about SDK instability and timing, I did not argue against MCP adoption in general — I argued against the specific Wave 5 implementation plan (Python SDK, stdio). The External Researcher's evidence (97M monthly downloads, every major LLM provider adopted) confirms MCP is a real distribution channel. My objection is timing and implementation path, not the target.

---

### Agreement 5: Auth architecture requires agent tokens and business keys to be separate

Both the Codebase Analyst and my Phase 1 analysis independently reached this conclusion from the same codebase observation. This is the highest-confidence finding in the council: two independent readings of the same code, same conclusion.

---

## Summary: What the Council Should Synthesize

The strongest objections that remain unresolved after reading both agents' findings:

1. **MCP SDK v2 breaking changes are imminent.** fastapi-mcp partially mitigates the auth problem but does not resolve the SDK dependency chain risk. Evidence Confidence for Approach B should reflect this.

2. **Report_incident via MCP is a prompt injection attack surface.** Neither agent addressed this. It is not resolved by fastapi-mcp. If the MCP server exposes write operations, this is unpatched.

3. **Billing timing conflict remains unaddressed.** Multi-protocol open access before gating trains customers that data is free. Spamhaus model is the right target; the path from "currently open" to "Spamhaus model" through multi-protocol expansion is unclear.

4. **The daemon/subprocess conflict is partially resolved by fastapi-mcp** (HTTP transport doesn't require subprocess model), but should be explicitly stated in the synthesis, not left implicit.

The findings that fastapi-mcp makes MCP genuinely easier to add (External Researcher) and that the existing code is already protocol-agnostic (Codebase Analyst) are real updates. The question is whether the remaining risks (SDK stability, injection surface, billing path) are acceptable at current project stage.

---

*This challenge is complete. Phase 2 review written. All score challenges cite specific claims and scores from the reviewed findings. The synthesis phase can now reconcile.*
