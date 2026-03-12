# Follow-Up Research: Can a Solo Non-Technical Founder Build a Behavioral Trust Protocol?
## Date: 2026-03-11
## Researcher: Expedition Follow-Up Agent (Opus 4.6)
## Context: Answering the question all five original teams missed

---

## Preface

This report exists because a prior research expedition — five teams and three validators — was explicitly asked whether the proposed MVTL (Minimum Viable Trust Layer) is realistic for a non-technical founder working with AI. Not one team answered it. All three validators flagged the omission.

That is the question this report answers.

The builder is a solo designer/creator. The tool is Claude Code (Opus 4.6) running as an agentic coding partner. The human writes no code. The AI writes all of it. The current result: a working Python prototype, 160 passing tests, SQLite persistence, event bus, privacy mode, and agent identity registration — all functional, all built this way.

The question is whether this model can carry the project forward into authentication middleware, behavioral trust scoring, W3C Verifiable Credentials, incident taxonomy, and eventually infrastructure used by hundreds of thousands of agents.

The honest answer is: **conditionally yes — but the conditions matter enormously, and the risks are not evenly distributed across the roadmap.**

---

## 1. The Current State of AI-Assisted Development for Non-Technical Founders

### The tool landscape is real and capable

As of March 2026, a genuine ecosystem of AI-first development tools exists for non-technical founders. Lovable reached $200M ARR by December 2025 and allows founders to build full-stack applications through natural language alone. Bolt.new, Replit Agent, and v0 by Vercel handle frontend, backend, database, and deployment from descriptions. Claude Code, at the more capable end, handles multi-file codebases, test suites, and agentic workflows.

This is not hype. Bhanu Teja built SiteGPT in a weekend using AI-assisted coding and reached $15,000 monthly recurring revenue as a one-person operation. The 2026 NxCode report documents the "one-person unicorn" pattern as mechanically real, driven by AI agent leverage and context engineering. Anthropic's own Claude Code hackathon selected 500 builders from 13,000 applicants; winners came from outside traditional engineering backgrounds.

Claude Code specifically — which Submantle is using — sits at the most capable tier. It achieved a SWE-bench Verified score of 80.9% with Opus 4.5 in November 2025 and has since been upgraded to Opus 4.6. It can write tests, refactor across files, reason about architectural tradeoffs, and maintain context across sessions when the codebase is structured to support it. Submantle's 160-test foundation was built this way and passes.

**Assessment for Submantle specifically:** The Submantle prototype represents a legitimate accomplishment. The schema is correct, the cryptographic primitives are sound (HMAC-SHA256), the event bus is functional, and the test coverage is real. This is not cosmetic — it is working infrastructure. Claude Code built it, and it is buildable.

### The build model has a name — and it has known failure modes

The practice is called "vibe coding" in the industry — a term coined in early 2025. The distinction that matters is between vibe coding (accepting AI output without review, prompting toward a feeling) and AI-assisted engineering (AI as force multiplier with a human verifying architecture, security, and logic). These are not the same thing. The failure modes belong almost entirely to the former.

The Submantle build, based on its structure and test coverage, sits closer to AI-assisted engineering than pure vibe coding. The CLAUDE.md conventions, the triadic review process, the explicit design principles — these are not vibe coding. They are the scaffolding that separates successful AI-assisted infrastructure from the ones that fail.

---

## 2. Documented Examples: What Non-Technical Founders Have Actually Built

### What works

- **Consumer SaaS and tools**: Non-technical founders have shipped production consumer apps, internal tools, and content platforms. The combination of Lovable/Bolt/Replit + Claude Code handles this reliably.
- **Prototypes with real traction**: Working prototypes in finance, education, and productivity have been built solo. Peter Steinberger's OpenClaw became the fastest-growing open-source project on GitHub in 2025 — reportedly maintained by one developer with AI tooling.
- **Infrastructure with bounded scope**: The Submantle V1 foundation itself. 160 tests, SQLite, HMAC auth, event bus. This is bounded, well-specified infrastructure built cleanly.

### Where the ceiling appears

The documented patterns show a consistent friction point: **things that require a human to understand the code begin to fail when the human does not understand the code.**

A widely-cited 2025 example from Fortune: a founder shared their Cursor-built SaaS, then posted hours later: *"guys, i'm under attack ever since I started sharing how I built my SaaS using Cursor — random things are happening, maxed out usage on API keys, people bypassing the subscription, creating random shit on db."*

A March 2025 incident: a vibe-coded payment gateway approved $2 million in fraudulent transactions. Cyber insurance companies subsequently adjusted policies specifically for AI-generated codebases.

These failures are not failures of AI capability. They are failures of the human oversight gap. The AI wrote functional code. Nobody who understood authentication reviewed it.

---

## 3. The Real Bottlenecks for a Non-Technical Founder

The question is not "can AI write the code?" Claude Code demonstrably can. The question is what breaks when a non-coder is the only human in the loop.

### 3.1 Security review without a reviewer

62% of AI-generated code solutions contain design flaws or known security vulnerabilities (multiple studies, 2025). 40% have security flaws, including SQL injection, hardcoded credentials, and inadequate authentication. AI coding tools themselves had 30+ disclosed vulnerabilities in late 2025, including prompt injection enabling data exfiltration.

The critical failure mode: the non-technical founder cannot tell the difference between code that looks right and code that is right. Claude Code will write secure code when asked to write secure code. But it may not volunteer that a particular design choice is exploitable, especially if the conversation is moving fast. The human reviewer — the one who would catch "this HMAC verification is timing-unsafe" or "this CORS wildcard allows credential exposure" — does not exist in the solo model.

For Submantle specifically: the existing codebase already has a known security gap (CORS wildcard + open registration noted in the gap analysis). It is not exploited yet. But as trust infrastructure is added — authentication middleware, token issuance, trust score exposure — each new component is a new attack surface that cannot be validated by the founder.

**Mitigation that exists:** Submantle uses structured processes (triadic review, validation passes). Claude Code can perform its own security review when explicitly asked. This partially compensates. It does not fully compensate.

### 3.2 Context degradation at scale

AI coding agents lose coherence across sessions. LLMs forget project conventions, repeat known mistakes, and lose task state across context boundaries. Research from a 108,000-line C# project found that single-file context documents do not scale — a 1,000-line prototype can be fully described in one prompt, but a 100,000-line system cannot. "Context rot" is documented: as context length increases, accuracy decreases, even with 200K token windows.

Submantle is currently small. The prototype directory has 9 files. This is fully within Claude Code's coherent operating range. The HANDOFF.md + CLAUDE.md structure is good context engineering — Anthropic's own engineering team has published on this as the critical lever for production AI agent work.

The risk: as the codebase grows from prototype to production-ready trust infrastructure, context management becomes a real engineering discipline. Who maintains the HANDOFF.md? Who decides when to rotate memory? Who notices when Claude Code starts producing code inconsistent with prior architectural decisions? In a technical team, this is a developer's daily work. In the solo model, it is the founder's responsibility — a responsibility that requires enough architectural memory to notice when something is wrong.

### 3.3 Architectural decisions that cannot be undone

GitClear's analysis of 211 million AI-generated lines identified an 8x increase in code blocks with 5+ duplicated lines and a 39.9% decrease in code refactoring. Technical debt accumulates faster with AI-assisted development than human development when there is no human enforcing architectural discipline.

For Submantle: the schema and cryptographic primitives are correct today. The Go rewrite is deferred. Between now and the rewrite, architectural decisions made in Python will shape what the Go rewrite must accommodate. Specifically: the trust attestation credential format, the incident taxonomy, and the API surface. If these are defined incorrectly and then used by external agents, changing them later is a breaking change to a protocol — not a refactor of a private tool.

This is the structural risk for a non-technical solo founder: not "can AI build it" but "who validates that the architecture committed to today is the right architecture for what this becomes?"

### 3.4 Debugging under load

When the product is small, broken behavior is visible. When it scales, broken behavior hides in logs, race conditions, and edge cases. The VentureBeat analysis of production AI coding notes: "code that works for early users often failing when exposed to real-world complexity." The SQLite WAL mode concurrency ceiling under write-heavy trust recording — flagged by the expedition validators — is exactly this class of problem. It will not appear in testing. It will appear when 50 agents are querying simultaneously.

A technical founder can diagnose this. A non-technical founder + Claude Code can also diagnose it — if the session has enough context to know where to look and what constitutes anomalous behavior. The bottleneck is not Claude Code's diagnostic ability. It is whether the founder can articulate "here is what I'm seeing" accurately enough for Claude Code to identify root cause.

---

## 4. The MVTL Components: Realistic Assessment by Component

The MVTL identified by the expedition is: auth middleware + incident taxonomy + trust scoring + W3C VC integration. Here is an honest assessment of each.

### 4.1 Auth Middleware

**Verdict: Fully buildable in the solo model.**

This is precisely what Claude Code does well. The gap is identified clearly (the `/api/query` endpoint needs a FastAPI dependency that extracts a Bearer token, calls `_registry.verify()`, and calls `_registry.record_query()`). The pattern is standard. Claude Code can implement this correctly, including edge cases like timing-safe comparison, anonymous fallback behavior, and error responses. The 160 existing tests provide a regression harness.

Risk: low. This is a bounded, well-specified implementation task against established FastAPI patterns.

### 4.2 Incident Taxonomy

**Verdict: Buildable — but the taxonomy itself must be designed by the founder, not discovered by Claude Code.**

The previous expedition was correct: the incident definition is a product decision, not a technical one. What counts as a behavioral incident is a judgment call about trust semantics. Does a query that returns an error count? Does deregistering and re-registering within 60 seconds count? Does querying for critical process information without declaring the relevant capability count?

Claude Code can implement any taxonomy the founder specifies. What it cannot do is decide what the taxonomy should be. This is actually the right constraint — the founder's domain knowledge and product vision are exactly what should drive this. The bottleneck is not technical capability; it is getting the founder to articulate concrete rules.

Risk: medium — not because of AI limitations, but because the founder may defer this decision indefinitely, leaving the beta formula's denominator always zero (as it currently is).

### 4.3 Trust Scoring (Beta Reputation System)

**Verdict: Fully buildable in the solo model.**

The formula is `trust = alpha / (alpha + beta)` where alpha = total_queries and beta = incidents. This is a pure function. The previous expedition validated it extensively (Team 3, Team 5, historical precedents). Once the incident taxonomy is defined and auth middleware wires query counting, the compute_trust() function is a single Python function with no new dependencies.

The validation disagreement (pure Beta vs. three-signal composite) is resolved by the evidence: pure Beta is correct for V1. The three-signal formula introduces unvalidated parameters before baseline data exists. This is a clear call — use pure Beta, defer composite until real data justifies it.

Risk: low once incident taxonomy is decided.

### 4.4 W3C Verifiable Credentials Integration

**Verdict: Technically feasible but architecturally consequential — this is the highest-risk component for the solo model.**

W3C VC 2.0 became a final W3C Recommendation in May 2025. The JavaScript library (digitalbazaar/vc) exists. cheqd has already released MCP servers specifically for DID/VC operations, meaning there is a working precedent for MCP-integrated VC infrastructure.

However: VC implementation involves JSON-LD, cryptographic key management, credential schemas, selective disclosure with BBS+ cryptosuites, and revocation mechanism design. The expedition identified VC revocation as a blocking unknown — no team answered it. W3C StatusList2021 and Bitstring Status List v1.0 exist but have scalability and privacy tradeoffs that were not researched.

Claude Code can implement a W3C VC issuance endpoint. The question is whether the design decisions made in that implementation are correct decisions. The credential schema, the claim structure, the revocation approach, the key rotation strategy — these decisions will be public-facing once agents carry attestations. They are not easy to change.

The honest assessment: Claude Code can build a functional VC issuer. Whether it builds a production-grade, standards-compliant, revocation-safe VC issuer without a human expert reviewing the cryptographic design is uncertain. The cheqd shortcut (extending their MCP server rather than building from scratch) deserves serious consideration and was not explored by the original expedition.

Risk: high for the cryptographic and revocation components. Medium if cheqd integration is used as the implementation path.

---

## 5. The Solo Founder Model at Scale

### The optimistic case (2026 consensus)

The "one-person unicorn" narrative is not pure marketing. The NxCode 2026 report, Fast Company, and Wedbush Research all document genuine structural change: AI agents handling tasks that previously required teams. Context engineering (structuring information so AI agents have everything they need, when they need it) is the key skill — and it is a skill a non-technical founder can develop.

For infrastructure specifically: managed cloud services (Cloudflare Workers, Vercel, Railway, Fly.io) handle scaling, deployment, and DevOps automatically. The Submantle architecture's "lightweight first" constraint fits naturally here — if Submantle remains a daemon process rather than a cloud service, the scaling complexity is deferred.

### The honest case

TechCrunch's February 2025 analysis of the one-person unicorn model states directly: "constraints often appear over time, as usage grows, security, infrastructure reliability, and system resilience begin to get more complicated and demanding." Companies assembling products through AI tooling "struggle under sustained load" and code "often failing when exposed to real-world complexity."

For protocol-layer infrastructure used by hundreds of thousands of agents: the solo model has not been demonstrated at this scale. The examples that work are SaaS products and tools — not protocols. HTTPS, TCP/IP, OAuth 2.0 — the protocols that run the internet — were not built by solo non-technical founders. They were built by engineers who could participate in standards bodies, review each other's cryptographic designs, and defend technical decisions under expert scrutiny.

**The critical distinction for Submantle:** There is a difference between Submantle as a product (a daemon on your device that gives you awareness) and Submantle as a protocol (a trust standard that agents and brands build against). The product can likely be built and maintained in the solo model for a long time. The protocol requires credibility with technical audiences — standards bodies, enterprise security teams, cryptographers — that the solo model alone cannot provide.

### What actually happens at scale in open-source infrastructure

The Open Source Security Foundation's 2025 statement is clear: open infrastructure is not free. Successful open-source infrastructure projects that outgrow their founding team share a pattern: the founding leader sets vision, product direction, and culture, while a community of technical contributors handles security reviews, cryptographic audits, and standards participation.

The founding maintainer does not need to write the code. But the project needs technical contributors who do. The governance models that work — do-ocracy, steering committees, contributor ladders — are all documented. The Linux Foundation guide explicitly notes: "a maintainer doesn't necessarily have to be someone who writes code — it could be someone who's done a lot of work evangelizing the project."

**Implication for Submantle:** The solo model is not a permanent ceiling — it is the appropriate model for the prototype and early product phase. The ceiling appears when Submantle needs external technical contributors: security reviewers, cryptographers, standards participants. The founder's job at that stage is not to learn cryptography — it is to build a community of contributors who can do what Claude Code cannot: vouch for the protocol's security with human credibility.

---

## 6. Known Failure Modes of the Vibe Coding / AI-First Model

These are documented, not theoretical:

**Security by omission.** AI generates functional code that lacks essential security safeguards because no one in the loop knew they were required. Called "insecure by dumbness" in industry literature. Common vulnerabilities: hardcoded credentials, missing input sanitization, naive auth logic, race conditions in concurrent access.

**Technical debt cascade.** GitClear documents an 8x increase in duplicated code blocks and 39.9% decrease in refactoring in AI-assisted codebases. Predictive analysis expects a technical debt crisis in 2026-2027. For infrastructure, debt in the API surface becomes a compatibility burden.

**Context rot.** AI agents lose coherence as codebases grow. Claude Code's context window is large but not unlimited. Conventions established early get forgotten. Architectural decisions made in one session are silently violated in another. The HANDOFF.md structure helps, but only if it is maintained.

**The invisible ceiling.** Non-engineers "hit walls when even minor changes cause cascading failures." When this happens to a solo non-technical founder, there is no fallback. Either Claude Code diagnoses the failure correctly, or the project stalls. No amount of prompting resolves a cascading failure that requires understanding the execution model.

**Regulatory invisibility.** AI assistants are unaware of regulatory constraints. The EU AI Act is live. The expedition identified this as a gap. A behavioral trust system that scores agents and gates their access could fall under EU AI Act high-risk AI system provisions. Building without legal review is not a technical failure — it is a structural gap of the solo model, where no legal adviser is in the loop.

**Misplaced confidence.** The biggest failure mode is not catastrophic breakdown — it is building something that appears to work, reaching external deployment, and then discovering a flaw that cannot be patched in production. Security vulnerabilities in trust infrastructure are not cosmetic. An exploitable trust scoring endpoint that allows an agent to inflate its own score retroactively would undermine the entire value proposition.

---

## 7. Open-Source Infrastructure with Non-Technical Leads: What Makes It Work

Successful open-source projects with non-technical founding leadership share these patterns:

**Product-led vision, community-executed implementation.** The founder provides coherent product direction, design philosophy, and community culture. Technical contributors execute implementation. This is the division of labor that scales.

**Early technical anchor relationships.** Before community forms, successful projects typically have one or two trusted technical advisers — not employees, but collaborators who review critical design decisions and can flag problems the founder cannot see. These relationships form before the project needs them, not after a security incident.

**Explicit governance from the start.** ClearlyDefined, Apache-governed projects, and Linux Foundation projects all document roles and contribution pathways early. This creates a ladder for contributors to invest in. Open-source infrastructure abandoned without governance tends to be forked or replaced.

**Credible standards participation.** For protocols specifically, credibility in standards bodies requires technical contributors who can submit Internet-Drafts, respond to expert review, and defend design decisions against cryptographers. The IETF's open participation model (anyone can contribute, no formal membership) lowers the bar to entry — but participation still requires drafting technically credible documents. Claude Code can draft an Internet-Draft. Whether it would survive expert review without a human champion is a different question.

---

## 8. Realistic Timeline for the MVTL

The expedition's proposed MVTL: auth middleware + incident taxonomy + trust scoring + W3C VC integration.

### Within one focused session (4-8 hours of active work):
- Auth middleware wiring
- Pure Beta trust score computation function
- Trust score returned in API responses
- Tests for all of the above

**This is realistic.** It is bounded, well-specified, and within Claude Code's demonstrated capability range for this codebase.

### Requiring a design decision before building:
- Incident taxonomy (product decision, then 1 session to implement and test)

**This is realistic but blocked on founder decision.** Claude Code cannot make this call. The founder must define: what counts as an incident? Once defined, implementation is fast.

### Requiring careful design review before committing:
- W3C VC integration

**This should not be rushed.** The credential schema, revocation approach, and key management design will be public-facing. The cheqd MCP server shortcut should be evaluated first — it may provide most of what is needed without building VC issuance from scratch. If building from scratch, the design should be reviewed against the W3C VC Implementation Guidelines before implementation begins.

### Realistic total timeline for MVTL:
- Session 1: Auth middleware + Beta trust scoring (one session, fully achievable)
- Between sessions: Founder defines incident taxonomy
- Session 2: Incident taxonomy implementation + wiring + tests
- Session 3: VC design research (evaluate cheqd integration path vs. custom build) + design decision
- Sessions 4-5: VC integration, revocation mechanism, tests

This is 5 focused sessions, not one. The original expedition's implied "one session" framing was unrealistic — specifically because incident taxonomy requires a founder decision, and VC integration requires architectural design review before touching code.

---

## 9. The Questions That Can and Cannot Be Answered by Claude Code

### Claude Code can answer:
- Is this code correct?
- Is this implementation secure given these constraints?
- Does this test coverage reach the edge cases?
- What does this standard say and how should I implement it?
- What is the right data model for this feature?

### Claude Code cannot answer:
- Is this the right architecture for what this will become in three years?
- Is this implementation's cryptographic design auditable by external security researchers?
- Will this credential format earn trust from enterprise security teams?
- What regulatory exposure does this create?
- Is the incident taxonomy we chose aligned with how real trust works in the agent ecosystem?

The boundary is clear: Claude Code is an expert implementer with broad knowledge. It is not a security auditor, a legal adviser, a cryptographer, or a product strategist who understands the ecosystem's actual norms. Those roles do not disappear because the founder is non-technical — they are deferred, which means their absence becomes a risk.

---

## 10. Honest Summary

**The solo non-technical founder + Claude Code model has already proven itself at the Submantle prototype stage.** The current foundation is sound. The methods (structured handoffs, explicit design principles, triadic review, test coverage) are the right practices. This is not vibe coding — it is disciplined AI-assisted engineering.

**The MVTL's first three components (auth middleware, incident taxonomy, pure Beta scoring) are fully achievable in this model.** They are bounded, well-specified, and within the demonstrated capability range. Building them is a matter of sessions, not a leap of faith.

**W3C VC integration is the risk boundary.** It is technically achievable but architecturally consequential. The cryptographic design decisions made here will be hard to change in production. This component specifically benefits from external technical review before implementation — a collaborator, an adviser, or at minimum explicit external validation of the design before any code is written.

**Scale requires community, not just a better AI model.** A one-person + AI model can carry Submantle through its product phase: working daemon, trust scoring, agent identity, dashboard, MCP server. The protocol phase — where external agents rely on Submantle's trust attestations, where brands build against the API, where the credential format needs to survive expert scrutiny — requires technical contributors the founder must recruit, not build. The founder's job at that stage is vision, culture, and community-building. Claude Code's job is implementation. A community of technical contributors handles the credibility gap.

**The biggest realistic risk is not code quality.** It is the invisible gap between code that passes tests and code that survives adversarial real-world use, regulatory review, and expert cryptographic analysis. These are not problems Claude Code solves. They are problems that require humans who understand the domain — whether employees, advisers, or open-source contributors — to be in the loop before external deployment.

**The path forward is clear:** Build the MVTL's first components now. Treat W3C VC as a design-first problem, not a code-first problem. Recruit a technical collaborator for the trust attestation and revocation design before committing it. Be explicit that the solo model is appropriate for the current phase and plan for its evolution before reaching the protocol phase.

Submantle's vision — infrastructure at internet scale — is genuinely achievable. The solo model is not the constraint that prevents it. The solo model is the correct approach for this phase of the build.

---

## Sources

- [Lovable $200M ARR: Best AI Coding Tools 2026 — SimilarLabs](https://similarlabs.com/blog/best-ai-coding-tools-2026)
- [The One-Person Unicorn: Solo Founder Guide 2026 — NxCode](https://www.nxcode.io/resources/news/one-person-unicorn-context-engineering-solo-founder-guide-2026)
- [Vibe Coding — Wikipedia](https://en.wikipedia.org/wiki/Vibe_coding)
- [Vibe coding is not the same as AI-Assisted engineering — Addy Osmani, Medium](https://medium.com/@addyosmani/vibe-coding-is-not-the-same-as-ai-assisted-engineering-3f81088d5b98)
- [Vibe Coding Security Risks — FontsArena](https://fontsarena.com/blog/vibe-coding-security-risks-what-happens-when-you-ship-ai-generated-code-without-looking-inside/)
- [AI coding tools security exploit 2025 — Fortune](https://fortune.com/2025/12/15/ai-coding-tools-security-exploit-software/)
- [AI writes code like a junior dev — Help Net Security](https://www.helpnetsecurity.com/2025/10/27/ai-code-security-risks-report/)
- [AI Vibe Coding: 45% of AI-Generated Code is a Security Risk — BayTech Consulting](https://www.baytechconsulting.com/blog/ai-vibe-coding-security-risk-2025)
- [AI Technical Debt: How Vibe Coding Increases TCO — BayTech Consulting](https://www.baytechconsulting.com/blog/ai-technical-debt-how-vibe-coding-increases-tco-and-how-to-fix-it)
- [Codified Context: Infrastructure for AI Agents in a Complex Codebase — arXiv 2602.20478](https://arxiv.org/abs/2602.20478)
- [Why AI coding agents aren't production-ready — VentureBeat](https://venturebeat.com/ai/why-ai-coding-agents-arent-production-ready-brittle-context-windows-broken)
- [Effective context engineering for AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [W3C Verifiable Credentials 2.0 — W3C Press Release](https://www.w3.org/press-releases/2025/verifiable-credentials-2-0/)
- [MCP Authorization — Cerbos](https://www.cerbos.dev/blog/mcp-authorization)
- [MCP's Next Phase: November 2025 Specification — Medium](https://medium.com/@dave-patten/mcps-next-phase-inside-the-november-2025-specification-49f298502b03)
- [AI agents could birth the first one-person unicorn — TechCrunch](https://techcrunch.com/2025/02/01/ai-agents-could-birth-the-first-one-person-unicorn-but-at-what-societal-cost/)
- [SaaS Scale Trap: Validation Gaps Doom Non-Technical Founders in 2026 — WebProNews](https://www.webpronews.com/saas-scale-trap-how-validation-gaps-doom-non-technical-founders-in-2026/)
- [Open Infrastructure is Not Free — OpenSSF](https://openssf.org/blog/2025/09/23/open-infrastructure-is-not-free-a-joint-statement-on-sustainable-stewardship/)
- [Leadership and Governance — Open Source Guides](https://opensource.guide/leadership-and-governance/)
- [Claude Code Review 2026 — AI Tool Analysis](https://aitoolanalysis.com/claude-code/)
- [Agentic Trust Framework: Zero Trust for AI Agents — CSA](https://cloudsecurityalliance.org/blog/2026/02/02/the-agentic-trust-framework-zero-trust-governance-for-ai-agents)
- [Trust Score-Based Access Control Model — MDPI](https://www.mdpi.com/2076-3417/15/17/9551)
- [IETF Working Group Guidelines — RFC 1603](https://www.rfc-editor.org/rfc/rfc1603.html)
