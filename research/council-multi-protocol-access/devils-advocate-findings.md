# Devil's Advocate Findings: Multi-Protocol Access Strategy
**Council Role:** Devil's Advocate
**Date:** 2026-03-12
**Project:** Submantle
**Analyst:** Claude Sonnet 4.6

---

## Step 1: What's Being Proposed

The proposal is to expand Submantle's access surface from its current single REST API (13 endpoints, FastAPI, port 8421) to multiple protocols: REST API (exists), MCP server (Wave 5, Python stdio), CLI tool (proposed), and "plugins" (undefined). The framing is that "neutral infrastructure shouldn't favor one protocol."

The "exchange hub" vision extends this further: different protocol consumers (agents via MCP, businesses via REST, developers via CLI) all interact with shared trust data regardless of how they connect.

My job is to find every way this fails.

---

## Step 2: Codebase Observations

Reading the three files reveals several embedded vulnerabilities that the multi-protocol proposal makes worse:

**Observation 1: The current auth model is fundamentally split.** `/api/verify/{agent_name}` has NO authentication. Anyone can query any agent's trust score for free. `/api/query` has optional auth — anonymous queries work but don't accumulate trust. The incident reporting endpoint (`/api/incidents/report`) also has NO authentication on the reporter field. Any string is accepted as a reporter identity.

**Observation 2: The incident pipeline is a free-fire zone.** `record_incident()` rejects self-pings (reporter == agent_name) and 24h duplicates. That's it. A bad actor who controls two agent names (or any non-matching string as reporter) can file unlimited accepted incidents against any registered agent. This is already a problem in single-protocol REST. Multi-protocol compounds it: the same unauthenticated reporter string now arrives via three separate code paths (REST, MCP tool call, CLI command), each of which must implement identical validation — and each is a new surface for that validation to fail or be bypassed.

**Observation 3: The HMAC token mechanism doesn't survive multi-protocol.** Tokens are long hex strings designed for HTTP Authorization headers. A CLI user would need to pass this as a flag (`--token abc123...`) or environment variable. This is a UX disaster and invites token leakage via shell history. MCP's stdio transport doesn't have headers — the token would need to be passed in the JSON-RPC `params` payload, which is a completely different credential surface than HTTP Bearer. Three protocols means three credential-passing conventions.

**Observation 4: SQLite with per-operation connections.** The database comment explicitly states "For multi-threaded production use, always use a file-backed database" and the in-memory connection is "safe for single-threaded test use." Multi-protocol means multiple concurrent access paths — REST requests, a running MCP subprocess, and a CLI invocation could all hit SQLite simultaneously. WAL mode handles readers; concurrent writers still serialize. This is probably fine at prototype scale, but the architecture has never been stress-tested for concurrent multi-process access.

**Observation 5: CORS is wide open.** `allow_origins=["*"]` — this is fine for a local dashboard but becomes an attack surface if the server ever binds to anything other than localhost. Multi-protocol discussions often lead to "let's expose this publicly." The CORS configuration would need to be revisited for each protocol's security model.

---

## Step 3: Research-Based Failure Modes

### 3A. MCP Protocol Instability

**Evidence:** The MCP Python SDK GitHub shows "main — v2 development (breaking changes)" with v1.x in maintenance mode. The spec has 158 open issues including schema inconsistencies between prose docs and JSON schema (issues #2313, #1906). The SDK releases multiple times per week with known architectural redesigns coming ("lifespan redesign needed" — issue #2113; SSE transport deprecation — issue #2278).

**Failure mode:** A solo founder builds a stdio MCP server against the current Python SDK. The v2 SDK ships with the transport layer redesigned. The stdio transport the Wave 5 plan depends on has known issues: server processes survive parent termination when stdin EOF should trigger shutdown (issue #2231), HTTP transport swallows non-2xx status codes causing hangs (issue #2110). The founder now maintains a server against an unstable spec, debugging issues that are upstream SDK bugs, while simultaneously building Waves 1-4, business API keys, and Stripe integration.

### 3B. Multi-Protocol Attack Surface Multiplication

**Evidence:** Wiz Research found MCP-specific vulnerabilities including DNS rebinding attacks on SSE transport, OAuth implementation flaws in spec-required flows, and tool name conflicts enabling masquerade. Simon Willison's analysis documents tool poisoning, rug pulls, and confused deputy attacks. OWASP API Security 2023 identifies "Improper Inventory Management" as a top risk — "APIs tend to expose more endpoints than traditional web applications."

**Failure mode specific to Submantle:** Submantle's MCP server exposes trust scoring as a *tool* that agents can call. An agent requesting its own score, an agent filing an incident via MCP tool call, and a business checking scores via REST are now three attack surfaces instead of one. The incident filing tool called via MCP has all the existing authentication problems of the REST endpoint, plus MCP-specific ones: the caller identity comes from the LLM's tool call, not a verified HTTP token. A prompt injection attack against an agent using Submantle's MCP server could cause that agent to file false incidents against competitors.

### 3C. The "Neutral Protocol" Argument is Self-Defeating

**The claim:** Supporting all protocols = neutrality.

**The reality:** Protocol choice is not about favoritism — it's about use case fit. REST is for synchronous request/response from businesses. MCP is for agents running inside LLM contexts. CLI is for developers and automation. These are different users with different needs. Supporting all three doesn't make Submantle neutral; it makes Submantle diffuse.

More critically: MCP stdio is a *subprocess* model. The MCP client launches Submantle as a child process. This means Submantle, which is designed to be always-running background infrastructure, must also function as a disposable subprocess that starts, handles queries, and terminates. These are architecturally opposed requirements. A daemon that gets spawned and killed per MCP session cannot maintain its 5-second scan cache, its privacy state, or its in-memory state across sessions. Unless the MCP server is a thin wrapper that talks to the running REST API — in which case you've added a protocol layer that just duplicates the REST API.

### 3D. The "Exchange Hub" Concept Violates "Always Aware, Never Acting"

**The claim:** Different protocols converge on shared trust data regardless of how they connect.

**The problem:** "Exchange hub" implies Submantle brokers interactions between parties. An agent queries Submantle via MCP. A business checks scores via REST. Submantle sits in the middle, receiving inputs from multiple directions and responding to each.

This is fine for read queries. But incident reporting via MCP is different. When an agent calls a `report_incident` MCP tool, Submantle is now receiving adversarial inputs from inside the AI execution environment — exactly the injection-vulnerable surface that security researchers flagged. The "always aware, never acting" principle is about Submantle not enforcing. But facilitating interactions between agents (one agent filing reports via MCP that affect another agent's score) is a form of acting as a mediator. The Visa analogy breaks here: Visa doesn't let merchants report other merchants' fraud through the same payment rails.

### 3E. Open/Unauthenticated Access Destroys the Revenue Model

**Evidence from codebase:** `/api/verify/{agent_name}` — no auth, returns full trust score. The comment says "No auth required for V1 — billing comes later." The Experian model charges businesses to check scores.

**Failure mode:** If score queries are free via REST today, and also free via MCP tomorrow, and also free via CLI the day after — you have trained every potential customer that this data is free. Adding authentication later requires asking existing integrations to change. The "billing comes later" assumption is correct for a prototype, but the multi-protocol expansion actively makes the path to billing harder: now you need auth on REST, MCP, AND CLI, with different credential flows for each.

The deeper problem: open unauthenticated access to the verify endpoint is a precondition for self-serve customers to test without friction, but it also means the entire trust database is queryable without paying. A competitor could scrape all agent scores, build their own database, and undercut Submantle's business before the first API key is sold.

### 3F. CLI Traction Is Real But For Wrong Use Cases

**Evidence:** CLI tools like `curl`, `jq`, `gh`, and `stripe` CLI have genuine developer adoption. However, these serve developer-facing products where the developer IS the user. Submantle's actual customers are businesses checking agent scores programmatically — not developers running one-off queries at a terminal.

A CLI tool for Submantle would primarily be used for:
1. Development/testing (a use case already served by the REST API)
2. Scripts and automation (a use case already served by the REST API)

There is no use case for Submantle's CLI that isn't already served by `curl`. The maintenance burden of a CLI tool includes: argument parsing, help text, error messages, shell completion, cross-platform packaging, version management, and its own authentication credential storage. For a solo founder, this is months of work for zero new customer value.

### 3G. Concurrent Security Vulnerabilities Are Harder to Audit

**Evidence from codebase:** The current architecture has known security gaps that haven't been fixed: (1) Unauthenticated incident reporting, (2) Reporter identity is an unverified string, (3) No rate limiting on any endpoint. These are present in the single-protocol REST API today.

**Failure mode:** Adding MCP and CLI before fixing these means:
- The same vulnerability exists in three code paths
- Security audits must cover three surfaces instead of one
- A fix to the REST API doesn't automatically fix the MCP tool or CLI command
- Security regression testing must run against all three protocols

A vulnerability in the MCP server is particularly damaging for Submantle's positioning. Submantle is trust infrastructure. A security incident in the trust infrastructure product is existential, not inconvenient.

---

## Step 4: Assumption Audit

| Assumption | Status | Risk If Wrong |
|---|---|---|
| MCP is gaining adoption that makes it worth building against | Partially verified — major IDEs have integrated it, but the spec has 158 open issues and v2 is breaking | Building against v1 SDK when v2 is imminent wastes work |
| stdio transport is the right MCP transport for Submantle | Unverified — MCP spec says "clients SHOULD support stdio whenever possible" but Streamable HTTP is the new primary | Submantle builds stdio server; the ecosystem moves to HTTP |
| A CLI tool serves a real unmet need | Unverified — no customer evidence cited | CLI tool provides no value, becomes pure maintenance burden |
| "Neutral" means "supports every protocol" | Not verified — this is a design opinion, not a competitive requirement | Building unnecessary protocols introduces complexity that contradicts the design principle |
| Multi-protocol doesn't complicate the auth/billing transition | Unverified — no plan exists for adding auth to MCP or CLI | When billing is added, auth must be retrofitted to 3 protocols, not 1 |
| The MCP server can safely mediate incident reports from AI contexts | Actively contradicted — security research shows MCP tool calls are injection-vulnerable | MCP-routed incident reports are forgeable via prompt injection |
| SQLite WAL mode is safe for concurrent multi-process access | Partially verified — WAL handles readers, but concurrent writer processes require external locking | Two processes write simultaneously; WAL serializes but doesn't prevent data races at the application layer |
| "Exchange hub" is consistent with "always aware, never acting" | Not verified — the two framings have a logical tension | Exchange hub implies mediation, which is a form of acting |
| Building MCP now is higher priority than billing/auth | Unverified — the build priority table lists MCP as "NEXT" alongside business API keys | MCP with no billing produces no revenue; billing with no MCP produces revenue |

---

## Step 5: Counter-Evidence

**Against "support every protocol for neutrality":**

The IETF RATS RFC 9334 "Passport Model" that Submantle's architecture maps to does NOT define protocol neutrality as a requirement. The Attester, Verifier, and Relying Party roles are about trust chain architecture, not access method. Being neutral means not favoring one agent builder over another — it has nothing to do with which HTTP transport a business uses to query scores.

**Against MCP as the right protocol for trust queries:**

MCP is designed for agents that need tools during LLM inference. Trust score queries are not inference-time tool calls — they are business decision queries that happen before or after an agent interaction. A brand checking whether to allow an agent to access their platform does this BEFORE the agent is running in an LLM context, not during. REST is the correct protocol for that use case. MCP would only make sense if Submantle were used inside an LLM's tool loop — which is possible, but is a different product position than the credit bureau model.

**Against "exchange hub" positioning:**

Experian is not an exchange hub. Experian has exactly two surfaces: (1) entities being scored submit their own data and corrections, and (2) businesses pay to query scores. There is no protocol where entities interact WITH each other through Experian. The "exchange hub" framing introduces a third category — agents and businesses interacting through Submantle — that Experian does not support and Visa specifically outsources to merchants. This is scope creep disguised as vision.

**Against building CLI before production Go rewrite:**

The project's own CLAUDE.md build priority lists "Go production rewrite" as item #12, after MCP server and Stripe. A Python CLI tool built on top of a Python prototype is a dead-end investment: when the production rewrite happens in Go, the CLI must be rebuilt entirely. The Go rewrite is the natural point to build a CLI if one is needed.

---

## Step 6: Risk Scores

### Devil's Advocate Dimensions

| Dimension | Score | Justification |
|---|---|---|
| **Failure Probability** | 3/10 | Multi-protocol for a solo founder at prototype stage has a high probability of failing to ship complete, or shipping with exploitable security gaps in one or more protocols. The MCP SDK v2 breaking changes are imminent and certain. |
| **Failure Severity** | 3/10 | A security incident in trust infrastructure is existential. Multi-protocol means more attack surface before existing single-protocol vulnerabilities are patched. Failure isn't "we wasted two weeks" — it's "a bad actor poisoned trust scores via a vulnerable MCP tool and the product lost all credibility." |
| **Assumption Fragility** | 2/10 | The central assumptions (MCP is the right protocol, CLI serves a real need, "neutral" means multi-protocol) are all unverified design opinions, not validated customer requirements. The billing compatibility assumption is the most dangerous: open free access on all protocols makes monetization harder, not easier. |
| **Hidden Complexity** | 2/10 | The visible work is "add an MCP server." The hidden work is: auth on all three protocols, rate limiting on all three, incident validation on all three, regression testing on all three, SDK maintenance tracking, CLI packaging and distribution, and handling the architectural contradiction between stdio subprocess model and always-running daemon. |

### Shared Dimensions

| Dimension | Score | Justification |
|---|---|---|
| **Overall Risk** | 2/10 | The combination of solo founder constraints + unstable upstream spec + existing unpatched vulnerabilities + billing model conflict makes this a high-risk move. The project can't afford to ship broken trust infrastructure. |
| **Reversibility** | 5/10 | Individual protocols can be deprecated, but published APIs create external dependencies. If the MCP server ships and agents start using it, removing it breaks those integrations. REST versioning, MCP versioning, and CLI versioning are three separate migration problems. |
| **Evidence Confidence** | 7/10 | MCP SDK instability is documented from GitHub issues and release notes. Security vulnerabilities are from Wiz Research and Simon Willison (verifiable sources). The solo founder maintenance burden argument is structural and doesn't require external evidence. The revenue model conflict is deducible from the existing codebase (no auth on verify endpoint). |

---

## Summary of Strongest Objections

**1. MCP Wave 5 is being built against an SDK on the verge of a breaking v2 release.** The transport layer is being redesigned. This is not FUD — it's in the release notes. Building now means rebuilding later.

**2. The architectural contradiction is unresolved.** Submantle is a daemon (always-running, stateful, caches). MCP stdio makes it a subprocess (started on demand, stateless per session). These are structurally incompatible without a thin wrapper that just proxies to the REST API — at which point MCP adds no new capability, only maintenance burden.

**3. Open multi-protocol access before auth makes billing harder, not easier.** Every protocol that ships unauthenticated trains users that this data is free. Adding auth later is a breaking change across N protocols instead of 1.

**4. Incident reporting via MCP is a prompt injection attack surface.** Agents filing reports on other agents through an MCP tool call is the exact vulnerability class that security researchers have documented as exploitable. This is not hypothetical — it maps directly to known attack patterns.

**5. "Exchange hub" is scope creep from the credit bureau model.** Experian doesn't let creditors interact with each other through Experian. The neutral infrastructure position is strongest when Submantle has exactly two surfaces: agents registering themselves, and businesses querying scores. Every additional protocol and interaction model weakens that clarity.

**6. For a solo founder, three protocols is three products.** Each protocol needs its own: auth flow, error handling, rate limiting, regression tests, documentation, and security audit. The maintenance multiplication factor is not 3x — security vulnerabilities compound across surfaces, so the attack surface is larger than the sum of parts.

---

*If the proposal can answer: (1) Which existing single-protocol vulnerabilities are patched before multi-protocol ships? (2) What is the auth story for MCP and CLI specifically? (3) How does MCP stdio coexist with the always-running daemon model? — then it has addressed my strongest objections.*
