# External Researcher Findings: Multi-Protocol Access Strategy
**Date:** 2026-03-12
**Researcher:** External Researcher (Claude Sonnet 4.6)
**Project:** Submantle
**Council Session:** Multi-Protocol Access Strategy

---

## Grounding Summary

Before searching, I read the full codebase:
- `prototype/api.py` — 13 REST endpoints on FastAPI/uvicorn, port 8421. Score query at `GET /api/verify/{agent_name}` (unauthenticated). Agent auth via Bearer tokens (HMAC-SHA256). Incident reporting open (no auth). No business API keys yet.
- `prototype/agent_registry.py` — Beta Reputation formula, HMAC token system, self-ping/dedup pipeline. Core business logic is transport-agnostic (pure Python classes).

The key architectural observation: **the business logic in `AgentRegistry` has zero dependency on the transport layer.** `record_query()`, `compute_trust()`, `record_incident()` are plain method calls. This is the critical enabler for multi-protocol support.

---

## Angle 1: Multi-Protocol Precedents in Neutral Infrastructure

### DNS: The Canonical Precedent

DNS is the oldest and most successful neutral infrastructure. It supports UDP/53 (primary), TCP/53 (large responses, zone transfers), DNS-over-TLS/853 (DoT, encrypted since RFC 7858 in 2016), DNS-over-HTTPS/443 (DoH, RFC 8484 in 2018), and now DNS-over-QUIC (DoQ).

**What DNS teaches Submantle:**

1. **One canonical data layer, many transport adapters.** DNS zone data doesn't know or care whether a query arrived over UDP or HTTPS. The resolver core is identical. The protocol adapters are thin shells. This is the "thin adapter" pattern in its most proven form.

2. **Protocol additions were demand-driven, not anticipatory.** UDP was the original. TCP was added for a specific need (large responses). DoT came with enterprise privacy requirements. DoH came with browser vendor pressure. No protocol was added speculatively. Each filled a specific gap with a specific constituency.

3. **Small teams don't run all transports.** Unbound, Bind9, CoreDNS — production resolvers only enable the transports their deployment needs. The architecture supports all; the operator configures what they expose. This is the right model for a solo founder: build the adapter interface, expose only what you need now, add more as constituencies appear.

4. **DoH3, DoQ, DoT status as of late 2025:** The three encrypted protocols are converging. The right move is "not to pick a winner but to design a multi-transport strategy: DoT as the base, DoH3 and DoQ for latency- and mobility-critical use cases." [Source: CaptainDNS, 2025]

**Source:** [DoH3, DoQ and DoT: everything changing by late 2025 — CaptainDNS](https://www.captaindns.com/en/blog/doh3-doq-dot-2025-latest)

### Certificate Authorities: ACME/CMP/EST/SCEP

CA vendors manage 4 concurrent protocols for certificate issuance. ACME (RFC 8555) handles the vast majority of public TLS automation. EST is replacing SCEP in enterprise/government PKI. CMP handles legacy enterprise control. SCEP persists because device ecosystems move slowly.

**What CA vendors teach Submantle:**

1. **They added protocols only as constituencies demanded them.** ACME emerged because Let's Encrypt needed automation. EST emerged because SCEP was too old for modern PKI. The pattern is always: new constituency → new protocol, not the reverse.

2. **ACME is RESTful at its core.** EST exposes "a small set of REST-like operations." Both are HTTP-based. REST is the lowest common denominator that everything else layers on top of.

3. **The maintenance burden is real but manageable.** Keyfactor, Sectigo, and DigiCert all run multiple protocols. They do it with a shared backend (the CA key management system) and thin protocol adapters per channel. Nobody rebuilds the CA for each new protocol.

**Source:** [Certificate Management Protocols: CMP, ACME, EST and SCEP Compared — Unsung](https://www.unsungltd.com/blog-posts/certificate-management-protocols-cmp-acme-est-and-scep-compared-unsung), [ACME vs EST vs SCEP — SSLInsights](https://sslinsights.com/acme-vs-est-vs-scep-certificate-protocol/)

### Certificate Transparency Logs: The Fully-Open Model

CT logs (RFC 6962, RFC 9162) are the most permissive model: fully open, append-only, Merkle-tree-verified, no API keys required. The RFC itself specifies the API endpoints. Anyone can query them. Abuse is deterred by volume limits enforced at the log operator level.

**What CT logs teach Submantle:**

1. **Full openness works when the data is genuinely public and verifiable.** Trust scores are not the same as CT logs — CT logs contain certificate hashes with no PII. Open scoring access creates gaming incentives that CT logs don't face.

2. **The Merkle tree structure provides tamper-evidence without access control.** An interesting analogy for Submantle's append-only incident records — not the access model, but the data integrity guarantee.

**Source:** [Certificate Transparency — Wikipedia](https://en.wikipedia.org/wiki/Certificate_Transparency), [How CT Works — certificate.transparency.dev](https://certificate.transparency.dev/howctworks/)

### Spamhaus: The DNS-as-Protocol Model

Spamhaus is the best external precedent for Submantle's positioning. Their DNS-based query interface (DNSBLs) requires no HTTP client, no API key, and no SDK — if you know DNS, you can query Spamhaus. This made it ubiquitous in email infrastructure.

**The Spamhaus access model:**
- **Free tier:** DNS-based queries via public mirrors, unlimited for low volume. Attribution via a key appended to the query string (not a traditional API key — it rides the DNS query itself). [Source: Spamhaus Data Access](https://www.spamhaus.com/data-access/free-data-query-service/)
- **Commercial tier:** API access, higher volume, SLA, data feeds.
- **Abuse prevention:** Rate limiting by query attribution. When resolvers can't attribute queries, they start returning error codes instead of blocking outright — a graceful degradation rather than a hard wall.

**What Spamhaus teaches Submantle:**

1. **Protocol choice IS positioning.** DNS-based queries made Spamhaus the path of least resistance for mail administrators. The protocol choice drove adoption, not documentation.

2. **A key-in-query attribution system threads the needle between open and gated.** No API key → anonymous, low volume, no commercial use. Key-in-query → attributed, higher volume, free for non-commercial. Commercial key → SLA, API, data feeds. Submantle's current "anonymous works, token accumulates score" model follows this logic at the behavioral layer.

3. **Free for non-commercial is not the same as free for everyone.** Spamhaus has been very clear that commercial use requires paid access. This is not charity; it's how they fund operations while maximizing adoption.

**Source:** [Spamhaus Free Data Query Service](https://www.spamhaus.com/data-access/free-data-query-service/), [Spamhaus DQS](https://www.spamhaus.com/data-access/real-time-dns-blocklists/)

---

## Angle 2: Agent Ecosystem Protocol Landscape (March 2026)

### MCP Adoption Status

MCP crossed **97 million monthly SDK downloads** (Python + TypeScript combined) as of February 2026. OpenAI adopted in March 2025. Google DeepMind confirmed support. Microsoft, Amazon, Cloudflare are all in. 10,000+ active public MCP servers exist.

This is not a "wait and see" protocol. MCP is the de facto standard for AI agent tool access in 2026. [Source: MCP Wikipedia](https://en.wikipedia.org/wiki/Model_Context_Protocol), [Thoughtworks 2025](https://www.thoughtworks.com/en-us/insights/blog/generative-ai/model-context-protocol-mcp-impact-2025), [MCP 1-Year Anniversary](http://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/)

**Transport evolution:** The MCP roadmap explicitly states they are NOT adding more transports in 2026. Streamable HTTP is consolidating as the production remote transport. stdio remains for local/desktop tools. SSE is being deprecated in favor of Streamable HTTP. [Source: MCP 2026 Roadmap](http://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)

**Framework adoption:**
- Claude Desktop: native MCP (stdio)
- Claude API / Agent SDK: MCP via Streamable HTTP or stdio
- OpenAI Agents SDK: MCP supported [Source: OpenAI Agents Python Docs](https://openai.github.io/openai-agents-python/mcp/)
- LangChain: MCP integration available [Source: MCPs + LangChain guide](https://medium.com/@andres.tellez/mcps-langchain-from-zero-to-hero-ae3149d83c3d)]
- LiteLLM: MCP support [Source: LiteLLM MCP Overview](https://docs.litellm.ai/docs/mcp)
- CrewAI, AutoGen: REST API primarily, MCP adapters emerging

### The CLI Debate (February 2026)

A significant countertrend emerged in early 2026: CLI-based agent access. The OneUptime article (February 3, 2026) argued CLI is the "new MCP" because:
- CLIs already exist for virtually every service
- Zero implementation overhead
- Composable via Unix pipes
- Self-documenting via `--help`

The ScaleKit benchmark showed MCP is **10–32x more expensive than CLI** in token consumption, and CLI at 100% reliability vs. MCP at 72% in their test conditions. [Source: MCP vs CLI Benchmarking — ScaleKit](https://www.scalekit.com/blog/mcp-vs-cli-use), [Why CLI is the New MCP — OneUptime](https://oneuptime.com/blog/post/2026-02-03-cli-is-the-new-mcp/view)

**However, the CLI argument has critical caveats for Submantle:**

The ScaleKit piece ("Should you wrap MCP around your existing API?") draws a clear line: "The moment you cross the boundary from 'I'm automating my own workflow' to 'my product automates workflows for my customers,' every efficiency advantage CLI has becomes an architectural liability."

CLI works when:
- The CLI tool is maintained by the service provider and stays current
- Agents are running in controlled environments with shell access
- Use cases are automation/scripting flavored

CLI fails when:
- The caller is a remote agent making programmatic API calls
- Authentication needs to travel with the request
- Responses need structured parsing by the agent
- The service is called from environments where shell exec is unavailable or sandboxed

**For Submantle specifically:** Submantle's callers are AI agents checking trust scores before granting access. They are NOT developers automating their own workflows. They are remote services making runtime decisions. This is exactly the "product automating workflows for customers" case where CLI breaks down. CLI as a developer tool for Submantle management (registering agents, checking scores during development) is reasonable; CLI as the agent integration path is not.

**Source:** [MCP vs CLI — Microsoft Community Hub](https://techcommunity.microsoft.com/blog/azuredevcommunityblog/mcp-vs-mcp-cli-dynamic-tool-discovery-for-token-efficient-ai-agents/4494272), [PM Guide to Agent Distribution — Aakash G](https://www.news.aakashg.com/p/master-ai-agent-distribution-channel)

### The FastAPI → MCP Bridge: Near-Zero Effort

**fastapi-mcp** (github.com/tadata-org/fastapi_mcp) provides automatic exposure of existing FastAPI endpoints as MCP tools. Key facts:

- **3-line integration:** `mcp = FastApiMCP(app); mcp.mount_http()` — done. All existing endpoints become MCP tools automatically.
- **Auth passthrough:** Existing FastAPI Bearer token dependencies work transparently. An agent's MCP call carries the same auth header as a REST call.
- **Version:** v0.4.0 (July 2025), 11.7k stars, actively maintained, 15 contributors.
- **Deployment options:** Mount on same FastAPI app (one process), or deploy separately for independent scaling.
- **No backend changes required.** The MCP layer calls the existing HTTP endpoints or invokes the same Python functions directly.

This is the critical finding: **adding MCP to Submantle is not a Wave 5 feature that requires rebuilding. It is a 3-line addition to the existing FastAPI app.**

**Source:** [fastapi-mcp GitHub](https://github.com/tadata-org/fastapi_mcp), [Context7 fastapi_mcp docs](https://context7.com/tadata-org/fastapi_mcp/llms.txt), [fastapi-mcp PyPI](https://pypi.org/project/fastapi-mcp/)

---

## Angle 3: Open vs. Gated Access Models for Trust/Reputation Data

### VirusTotal: Tiered API Keys

VirusTotal operates a strict tiered model:
- **Community tier (free):** 500 requests/day, 4 requests/minute, no commercial use, requires registration and API key. Abuse prevention via daily quota + commercial use prohibition.
- **Premium tiers:** No rate limits (contractually managed), commercial use, SLA, enhanced features.
- **October 2025 simplification:** VirusTotal streamlined to fewer, clearer tiers. Contributor tier for engine partners, Duet tier for large organizations. [Source: VirusTotal Blog Oct 2025](https://blog.virustotal.com/2025/10/simpler-access-for-stronger-virustotal.html)

**Key lesson:** VirusTotal requires registration even for free access. This is not frictionless. The reason: attribution. They need to know who is making requests to enforce the commercial use prohibition. They cannot enforce the prohibition without identity.

**Source:** [VirusTotal Public vs Premium API](https://docs.virustotal.com/reference/public-vs-premium-api), [VirusTotal API Overview](https://docs.virustotal.com/docs/api-overview)

### Spamhaus: Query Attribution Over API Keys

As described in Angle 1, Spamhaus threads the needle cleverly: the free tier uses a key that rides the DNS query itself, making attribution lightweight and protocol-native. Commercial users get REST API access.

### Credit Bureaus: Strictly Gated, FCRA Regulated

The real-world credit bureau model (Equifax, Experian, TransUnion) is relevant as architecture precedent, but the regulatory layer is the opposite of Submantle's situation:

- **Access is gated by law (FCRA).** Every API caller must demonstrate a "permissible purpose" (lending, employment screening, property rental). This is not friction — it is a legal requirement. [Source: Equifax Developer Portal](https://developer.equifax.com/products/apiproducts/credit-reports)
- **Setup takes 1-3 days** due to bureau credentialing.
- **No open tier exists.** Even checking your own credit score requires identity verification.

**What this means for Submantle:** Submantle is NOT building a consumer credit bureau. It's building an agent behavioral trust service. There is no FCRA equivalent for AI agents (yet — NIST is working on it). This means Submantle has flexibility the credit bureaus do not. However, the credit bureau model still validates the revenue structure: businesses pay, subjects (agents) register free.

**Source:** [CRS Credit API](https://crscreditapi.com/), [iSoftpull Equifax API](https://www.isoftpull.com/equifax/api)

### Gen Digital Agent Trust Hub: The Emerging Competitor Model

Gen Digital (Norton parent company) launched AARTS (AI Agent Runtime Safety Standard) and the Agent Trust Hub in early 2026. Key characteristics:
- **Open source, vendor-neutral contract** for standardizing security decision-making across agent environments.
- Supports three verdict types: Allow, Deny, Ask.
- Uses "Skill IDs" — deterministic fingerprinting of agent plugins.
- Explicitly invitation-based: "We invite host builders, marketplace operators, enterprise security teams, and fellow security vendors to review, adopt, and challenge."
- **Open source** — available on GitHub. [Source: Gen Digital AI Agent Trust Hub](https://www.gendigital.com/blog/news/company-news/ai-agent-trust-hub-standards)

**Critical distinction from Submantle:** AARTS includes enforcement (Allow/Deny/Ask). Submantle's "always aware, never acting" principle explicitly excludes this. AARTS is an enforcement contract; Submantle is a scoring bureau. These are different positions. However, AARTS's open-source/vendor-neutral positioning validates the strategy of opening the protocol.

### The "Exchange Hub" Question

The research did not find direct precedent for an "exchange hub" model in trust/reputation infrastructure. The closest analogues are:

1. **Payment orchestration platforms** (IXOPAY, Interledger) — neutral layers that connect multiple protocols but pass value through, not just data. These are marketplaces in practice.

2. **Google A2A Agent Cards** — lightweight JSON contracts communicating agent capabilities, compliance tags, and trust scores. These are discovery artifacts, not exchange infrastructure.

3. **x402 protocol** — HTTP-native payment standard for AI agents, blockchain-agnostic. This shows the direction of agent-to-agent economic exchange, but it is payments, not trust.

**Assessment:** An "exchange hub" where different protocols converge and agents/brands interact through shared trust data is architecturally valid — that is exactly what DNS does and what Submantle's transport-agnostic core already enables. However, the word "hub" implies routing and coordination that pushes toward marketplace dynamics. The cleaner framing is "multiple access channels to a single trust ledger." Channels don't route between each other. They all read and write the same store.

**Source:** [Interledger Protocol — Medium](https://medium.com/xpring/interledger-how-to-interconnect-all-blockchains-and-value-networks-74f432e64543), [x402 Protocol — BlockEden](https://blockeden.xyz/blog/2025/10/26/x402-protocol-the-http-native-payment-standard-for-autonomous-ai-commerce/), [Salesforce Agent Interoperability](https://www.salesforce.com/blog/agent-interoperability/)

---

## Approach Scorecards

### Approach A: REST Only (Status Quo)

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Relevance | 5 | Works today; misses the primary agent access pattern of 2026 |
| Maturity | 10 | FastAPI REST is extremely proven |
| Community Health | 10 | FastAPI/Python ecosystem is thriving |
| Integration Effort | 10 | Already built |
| Overall Risk | 9 | Very safe — no change |
| Reversibility | 10 | Trivial |
| Evidence Confidence | 10 | Rock solid |

**Summary:** Safe but leaves Submantle off the path where AI agents are increasingly discovering and using tools (MCP). REST remains essential as the foundation; the question is whether it's sufficient alone.

---

### Approach B: REST + MCP via fastapi-mcp (Thin Adapter)

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Relevance | 10 | Directly addresses agent access with minimal effort |
| Maturity | 8 | fastapi-mcp v0.4.0, 11.7k stars, actively maintained. Not v1.0, but battle-tested |
| Community Health | 9 | High activity, multiple contributors, backed by strong FastAPI ecosystem |
| Integration Effort | 9 | 3 lines of code. Auth passthrough is built-in. No backend changes needed |
| Overall Risk | 8 | Low risk — MCP server is mounted alongside REST, not replacing it |
| Reversibility | 10 | Unmount one line. No impact on REST layer |
| Evidence Confidence | 9 | Multiple confirmed sources including official docs and Context7 |

**Summary:** This is the primary recommendation. fastapi-mcp turns Wave 5 from a multi-week build into a half-day addition. The existing `AgentRegistry.compute_trust()` call becomes an MCP tool automatically. No architectural change required.

---

### Approach C: REST + MCP + CLI (Three Channels)

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Relevance | 6 | CLI relevant for developer tooling, not for runtime agent calls |
| Maturity | 10 | CLI is battle-tested as a pattern |
| Community Health | 8 | CLI tooling healthy; argparse/typer are mature |
| Integration Effort | 6 | Requires building and maintaining a separate CLI binary. Not trivial for solo founder |
| Overall Risk | 7 | Moderate — adds maintenance surface |
| Reversibility | 8 | CLI can be removed; unlikely to create dependencies |
| Evidence Confidence | 8 | CLI-vs-MCP debate is live in 2026; CLI is valid for developer use cases |

**Summary:** A CLI is appropriate specifically for developer workflow (registering test agents, checking scores during integration development, scripting) — not for runtime agent calls. Build it later, after revenue exists. Current priority is agent-facing access, not developer tooling.

---

### Approach D: "Exchange Hub" Architecture

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Relevance | 3 | Conflates Submantle's data access problem with a routing/coordination problem it doesn't have |
| Maturity | 2 | No mature precedents for this exact model in trust/reputation context |
| Community Health | N/A | Not a library; an architectural concept |
| Integration Effort | 2 | Would require significant architectural redesign from the current monolith |
| Overall Risk | 3 | High complexity risk for solo founder; pushes toward marketplace model |
| Reversibility | 3 | Architectural decisions are hard to undo |
| Evidence Confidence | 7 | Evidence is clear that "hub" language creates marketplace incentives |

**Summary:** The "exchange hub" framing is dangerous for Submantle's positioning. Hubs route between parties. Submantle doesn't route — it records and reports. The right framing is "multiple access channels to one trust ledger." This preserves the credit bureau model and "always aware, never acting" principle.

---

### Approach E: Open (No Auth) Score Queries + Gated Business Access

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Relevance | 9 | Matches how DNS, CT logs, and Spamhaus free tier work |
| Maturity | 10 | Spamhaus has run this model for 25 years |
| Community Health | 10 | Industry-standard pattern |
| Integration Effort | 7 | Requires adding API key layer for business tier (Stripe + key issuance) |
| Overall Risk | 7 | Moderate — open scoring creates gaming incentives; requires rate limiting |
| Reversibility | 8 | Can add gating later; removing gating is easy |
| Evidence Confidence | 9 | Multiple confirmed precedents |

**Summary:** Submantle's current open score queries are actually the RIGHT default for adoption. VirusTotal requires registration even for free access; Spamhaus doesn't. For agent trust, low friction wins early adoption. The business tier (brands checking scores at scale) is where auth and billing belong. This matches the current code: anonymous score queries work; agent token accumulates history. Add rate limiting to prevent abuse of open endpoints; add billing keys for businesses wanting SLA.

---

## Synthesis: Priority Ordering and Verdicts

### Protocol Priority Order (from evidence)

1. **REST (already built)** — foundation; no change needed
2. **MCP (add immediately via fastapi-mcp)** — 3 lines of code, reaches every major agent framework that is actually running in 2026. This is not a future wave; it's a weekend addition.
3. **CLI (defer)** — valuable for developer tooling, not for runtime agent calls. Build after first revenue.
4. **Plugins/other** — no evidence of a specific unmet need today. Defer indefinitely until a constituency emerges.

### Open vs. Gated Access Verdict

The Spamhaus/DNS/CT log evidence supports a **graduated model**:
- **Score queries (GET /api/verify/*):** Keep open with rate limiting. Maximum adoption, minimum friction. Matches DNS and CT log precedents.
- **Agent registration and query recording:** Current Bearer token model is correct. No change needed.
- **Business API keys (SLA, high-volume checks, webhook alerts):** Gate with API keys + Stripe. This is Wave 11 in the build priority; the evidence confirms it's the right model.
- **Incident reporting:** Current open-but-validated model is correct for V1. Gating this too early reduces reporter participation and kills the credit bureau flywheel.

### Exchange Hub Verdict

**The "exchange hub" framing should be rejected.** Evidence from every neutral infrastructure precedent (DNS, CAs, CT logs, Spamhaus, Interledger) shows that neutral infrastructure exposes channels, it does not route between participants. The moment Submantle enables agents and brands to "interact through" it, it becomes a marketplace, not infrastructure. This violates the Visa model that is Submantle's core positioning: Visa provides data, merchants and banks interact with each other using that data.

The right articulation: **multiple access channels (REST, MCP, eventually CLI) all reading and writing the same trust ledger.** No cross-channel routing. No participant interaction mediated by Submantle.

---

## Key Findings for Council

1. **fastapi-mcp turns Wave 5 from a build into a mount call.** It is 3 lines of code, auth passthrough is built-in, the existing FastAPI endpoints become MCP tools automatically. This should be re-evaluated as part of Wave 5 scoping. [Source: GitHub tadata-org/fastapi_mcp, v0.4.0]

2. **MCP is the protocol for agent ecosystems in 2026.** 97M monthly downloads, every major LLM provider adopted it, 10,000+ servers. The CLI-vs-MCP debate is real but CLI is for developer workflows, not runtime agent calls. Submantle's callers are runtime agents making programmatic decisions. REST + MCP covers 95%+ of the actual agent ecosystem.

3. **Open score queries is the right default, not a mistake.** CT logs, DNS, and Spamhaus all validate low-friction read access. The business layer (paying customers) is gated, not the open read. Submantle's current unauthenticated `GET /api/verify/{agent_name}` matches the correct model from every precedent.

4. **The "exchange hub" framing is architecturally dangerous.** It implies routing and mediation that turns Submantle from infrastructure into a marketplace. The correct framing is "multiple access channels to one trust ledger."

5. **The thin adapter pattern is the canonical multi-protocol architecture.** DNS does it, CAs do it, Spamhaus does it. One data layer, thin protocol shells. Submantle's transport-agnostic `AgentRegistry` class already implements this correctly. The question is only which shells to mount.

---

## Sources

- [MCP 2026 Roadmap — modelcontextprotocol.io](http://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)
- [Model Context Protocol — Wikipedia](https://en.wikipedia.org/wiki/Model_Context_Protocol)
- [MCP 1-Year Anniversary — modelcontextprotocol.io](http://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/)
- [Thoughtworks: MCP Impact 2025](https://www.thoughtworks.com/en-us/insights/blog/generative-ai/model-context-protocol-mcp-impact-2025)
- [2026: Year for Enterprise-Ready MCP Adoption — CData](https://www.cdata.com/blog/2026-year-enterprise-ready-mcp-adoption)
- [MCP vs CLI Benchmarking — ScaleKit](https://www.scalekit.com/blog/mcp-vs-cli-use)
- [Why CLI is the New MCP for AI Agents — OneUptime (Feb 3, 2026)](https://oneuptime.com/blog/post/2026-02-03-cli-is-the-new-mcp/view)
- [Should You Wrap MCP Around Your Existing API? — ScaleKit](https://www.scalekit.com/blog/wrap-mcp-around-existing-api)
- [fastapi-mcp GitHub — tadata-org](https://github.com/tadata-org/fastapi_mcp)
- [fastapi-mcp PyPI](https://pypi.org/project/fastapi-mcp/)
- [Context7 fastapi_mcp documentation](https://context7.com/tadata-org/fastapi_mcp/llms.txt)
- [MCP vs CLI Dynamic Tool Discovery — Microsoft Community Hub](https://techcommunity.microsoft.com/blog/azuredevcommunityblog/mcp-vs-mcp-cli-dynamic-tool-discovery-for-token-efficient-ai-agents/4494272)
- [OpenAI Agents Python MCP](https://openai.github.io/openai-agents-python/mcp/)
- [VirusTotal Public vs Premium API](https://docs.virustotal.com/reference/public-vs-premium-api)
- [VirusTotal API Overview](https://docs.virustotal.com/docs/api-overview)
- [VirusTotal Simplified Access — Blog Oct 2025](https://blog.virustotal.com/2025/10/simpler-access-for-stronger-virustotal.html)
- [Spamhaus Free Data Query Service](https://www.spamhaus.com/data-access/free-data-query-service/)
- [Spamhaus Real-Time DNS Blocklists (DQS)](https://www.spamhaus.com/data-access/real-time-dns-blocklists/)
- [Equifax Developer Portal — Credit Reports API](https://developer.equifax.com/products/apiproducts/credit-reports)
- [Certificate Transparency — Wikipedia](https://en.wikipedia.org/wiki/Certificate_Transparency)
- [How CT Works — certificate.transparency.dev](https://certificate.transparency.dev/howctworks/)
- [DoH3, DoQ and DoT: everything changing by late 2025 — CaptainDNS](https://www.captaindns.com/en/blog/doh3-doq-dot-2025-latest)
- [Certificate Management Protocols Compared — Unsung](https://www.unsungltd.com/blog-posts/certificate-management-protocols-cmp-acme-est-and-scep-compared-unsung)
- [ACME vs EST vs SCEP — SSLInsights](https://sslinsights.com/acme-vs-est-vs-scep-certificate-protocol/)
- [Gen Digital AI Agent Trust Hub — AARTS](https://www.gendigital.com/blog/news/company-news/ai-agent-trust-hub-standards)
- [Salesforce Agent Interoperability](https://www.salesforce.com/blog/agent-interoperability/)
- [x402 Protocol — BlockEden](https://blockeden.xyz/blog/2025/10/26/x402-protocol-the-http-native-payment-standard-for-autonomous-ai-commerce/)
- [PM Guide to Agent Distribution (MCP/CLI/AGENTS.md) — Aakash G](https://www.news.aakashg.com/p/master-ai-agent-distribution-channel)
- [MCP API Gateway — Gravitee](https://www.gravitee.io/blog/mcp-api-gateway-explained-protocols-caching-and-remote-server-integration)
- [MCP Authorization November 2025 — Aaron Parecki](https://aaronparecki.com/2025/11/25/1/mcp-authorization-spec-update)
