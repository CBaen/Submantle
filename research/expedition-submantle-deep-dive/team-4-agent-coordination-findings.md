# Team 4 Findings: AI Agent Coordination & Integration Protocols
## Date: 2026-03-10
## Researcher: Team Member 4

---

### Battle-Tested Approaches

---

**1. Model Context Protocol (MCP) as the Native Integration Surface for Submantle**

- **What**: MCP is the dominant protocol (as of March 2026) for connecting AI agents to external tools and data. JSON-RPC 2.0 over stdio or HTTP+SSE. Spec version 2025-11-25 is current. 97M+ monthly SDK downloads. Adopted by Anthropic, OpenAI, Google, Microsoft, LangChain. Now governed by the Linux Foundation (Agentic AI Foundation, Dec 2025).
- **Evidence**: 5,800+ MCP servers in public registries. OpenAI officially adopted it in March 2025. MCP server downloads grew from ~100K (Nov 2024) to 8M+ (Apr 2025). Source: [MCP Wikipedia](https://en.wikipedia.org/wiki/Model_Context_Protocol), [Year of MCP](https://www.pento.ai/blog/a-year-of-mcp-2025-review), [2026 Enterprise Adoption](https://www.cdata.com/blog/2026-year-enterprise-ready-mcp-adoption)
- **Fits our case**: Submantle can expose itself as an MCP server. Every agent framework that supports MCP (Claude, GPT-4o, Gemini, LangChain, CrewAI, AutoGen) can query Submantle through a standard interface without agent rewrites. This is the lowest-friction path to universal integration.
- **Tradeoffs**: MCP by itself does NOT enforce pre-action checks. The spec says hosts SHOULD obtain consent before invoking tools, but nothing in the protocol enforces it. An agent can ignore Submantle if not required by its framework or system prompt. MCP is also synchronous by default — the 2025-11-25 spec adds async support but it's newer. Security: 30+ CVEs documented in MCP implementations as of 2025 — the ecosystem is maturing but not hardened.

---

**2. MCP Elicitation as the Native Pause-and-Ask Mechanism**

- **What**: MCP's Elicitation feature (introduced June 2025 spec) allows an MCP server to pause agent execution and request structured input from the user via the client. The server sends an `elicitation/create` request; the client presents a dialog; the user responds with accept/decline/cancel. Three-action response model.
- **Evidence**: Detailed in [MCP 2025-06-18 spec](https://modelcontextprotocol.io/specification/2025-06-18/client/elicitation), covered by [Glama](https://glama.ai/blog/2025-09-03-elicitation-in-mcp-bridging-the-human-ai-gap), [The New Stack](https://thenewstack.io/how-elicitation-in-mcp-brings-human-in-the-loop-to-ai-tools/), [Cisco](https://blogs.cisco.com/developer/whats-new-in-mcp-elicitation-structured-content-and-oauth-enhancements)
- **Fits our case**: Submantle-as-MCP-server can expose a `check_before_action` tool. When an agent calls it, Submantle responds with process context. If the context reveals risk (8 Node processes belong to active image generation), Submantle uses Elicitation to pause and ask the user: "Agent wants to kill all Node processes. 8 belong to your Stable Diffusion pipeline (running 2h). Proceed?" This gives Submantle a standards-compliant human-in-the-loop mechanism without custom code.
- **Tradeoffs**: Elicitation schemas are limited to flat objects with primitive properties only — no nested data structures. Elicitation is NOT a blocking mechanism for tool calls the agent has already decided to make; it's a server-initiated information request. The agent must voluntarily call Submantle first.

---

**3. Framework-Level Before-Tool Hooks (LangChain `wrap_tool_call`, OpenAI `needs_approval`)**

- **What**: Most major agent frameworks have a hook point where tool calls can be intercepted before execution.
  - **LangChain**: `AgentMiddleware` with `wrap_tool_call` hook. Developers wrap execution to control the before/after. `HumanInTheLoopMiddleware` intercepts in `after_model` to trigger user approval. `before_tool`/`after_tool` hooks were requested (GitHub issue #33441) but closed as "not planned" — current path is `wrap_tool_call`.
  - **OpenAI Agents SDK**: `needs_approval` parameter on tools. When set to `true`, execution pauses. `result.interruptions` contains pending approvals. Call `state.approve(interruption)` or `state.reject(interruption)` to resume. Works with streaming.
  - **CrewAI**: LLM Call Hooks (`before_llm_call`, `after_llm_call`) with full context. No native tool execution hook — only LLM-level hooks. External via APort `before_tool_call` hook.
  - **AutoGen**: Event-driven messaging via Core layer. No documented built-in pre-action hook for tool calls.
- **Evidence**: [LangChain middleware docs](https://docs.langchain.com/oss/python/langchain/middleware/custom), [LangChain GitHub issue #33441](https://github.com/langchain-ai/langchain/issues/33441), [OpenAI Agents SDK human-in-the-loop](https://openai.github.io/openai-agents-js/guides/human-in-the-loop/), [CrewAI LLM hooks](https://docs.crewai.com/en/learn/llm-hooks)
- **Fits our case**: For frameworks with native hooks (LangChain, OpenAI Agents SDK), Submantle can provide a plugin/middleware that intercepts tool calls and queries the Submantle daemon before allowing execution. This is the "middleware/plugin" integration path that requires minimal agent rewriting — just registering Submantle as middleware at framework initialization.
- **Tradeoffs**: Each framework requires a separate plugin. CrewAI and AutoGen have weaker native hooks — need external libraries or workarounds. This approach requires framework-specific code, violating the "must work with ANY framework" constraint unless we layer it above MCP (where the hook is at the protocol level, not the framework level).

---

**4. MCP Proxy/Gateway as the Universal Interception Layer**

- **What**: MCP proxy products (Gravitee, Lasso, MCPWall, MintMCP) sit between agent clients and MCP servers, intercepting ALL tool calls at the protocol level. They understand JSON-RPC MCP messages, can enforce ACLs per tool and per user/agent, rate-limit, block, and log every call.
- **Evidence**: [Gravitee MCP Proxy](https://www.gravitee.io/blog/mcp-proxy-unified-governance-for-agents-tools), [MCP Manager gateways](https://mcpmanager.ai/blog/mcp-gateway/), [Integrate.io comparison](https://www.integrate.io/blog/best-mcp-gateways-and-ai-agent-security-tools/), [MCPWall via Glama](https://glama.ai/mcp/servers/@behrensd/mcpwall)
- **Fits our case**: If Submantle positions itself as an MCP proxy (or embeds proxy capabilities), it becomes the mandatory routing layer for ALL MCP traffic. Every tool call passes through Submantle before reaching its destination server. Submantle sees every intent, can enrich the call with context ("you're about to call `kill_process` — here's what's running"), and can block or flag based on its knowledge graph. This is a viable universal integration path — an agent using any MCP-compatible framework can be caught.
- **Tradeoffs**: Only works for MCP-compliant agents. Agents using raw subprocess calls, direct OS APIs, or non-MCP tool invocations bypass this entirely. The proxy adds latency to every tool call (not just destructive ones). Requires Submantle to be configured as the MCP router in the environment — a deployment/ops challenge.

---

**5. OS-Level Enforcement: eBPF (Linux) / macOS ESF / Windows ETW + Kernel Callbacks**

- **What**: OS-provided mechanisms that can intercept system calls before (or during) execution.
  - **Linux eBPF + Tetragon**: Tetragon (Cilium) uses eBPF to enforce policies at the kernel level. When a policy violation is detected, the process does NOT return from the syscall — it is terminated via SIGKILL. `<1% CPU overhead`. AWS EKS now uses Cilium/eBPF as its default CNI. Can intercept `kill()`, `execve()`, file access, network connections. Falco monitors but cannot block; Tetragon CAN block.
  - **macOS Endpoint Security Framework (ESF)**: Apple's kernel-based security API (macOS 10.15+). Real-time event subscription with AUTH (blocking) and NOTIFY (observing) event types. AUTH events can be allowed or denied before execution. Covers process creation, file operations, network events. Used by all major macOS AV/EDR products.
  - **Windows**: `PsSetCreateProcessNotifyRoutineEx` kernel callback can set `CreateInfo->CreationStatus = STATUS_ACCESS_DENIED` to block process creation. ETW provides real-time event streams. Windows Job Objects can constrain what a process can do (kill permissions, etc.). No direct kernel callback for `TerminateProcess` interception — EDRs use inline API hooking in user-mode or kernel-mode DKOM.
- **Evidence**: [Tetragon enforcement docs](https://tetragon.io/docs/getting-started/enforcement/), [Tetragon vs Falco](https://medium.com/@mughal.asim/falco-vs-tetragon-a-runtime-security-showdown-for-kubernetes-a0e9fb9f30a0), [macOS ESF WithSecure](https://www2.withsecure.com/en/expertise/resources/macos-endpoint-security-framework), [Windows PsSetCreateProcessNotifyRoutineEx](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreateprocessnotifyroutineex), [ETW red team notes](https://www.ired.team/miscellaneous-reversing-forensics/windows-kernel-internals/etw-event-tracing-for-windows-101)
- **Fits our case**: The OS-level layer is the true guarantee layer. If Submantle integrates with eBPF (Linux), ESF (macOS), or a kernel driver (Windows), it can intercept a `kill()` syscall from an AI agent BEFORE it executes — regardless of framework, MCP, or any application-layer protocol. This is how every EDR/antivirus product works. Submantle can hook into this layer to be the authoritative "block or allow" decision point.
- **Tradeoffs**: Requires kernel-level components (signed kernel driver on Windows, entitlements + notarization on macOS, CAP_BPF on Linux). Significantly higher engineering complexity and certification requirements. Bugs at this layer cause system instability (BSODs, kernel panics). eBPF's current enforcement model terminates the process — it cannot pause-and-query Submantle then allow/deny. The AUTH event model on macOS ESF CAN do pause-query-allow/deny. On Windows, kernel callbacks can deny process creation but cannot do async external queries (must respond synchronously, quickly).

---

### Novel Approaches

---

**1. APort / Open Agent Passport: Cryptographic Permission Manifests as Pre-Action Contract**

- **What**: APort (aport.io) implements W3C DID-based "agent passports" — cryptographically signed documents declaring an agent's permitted capabilities and blocked operations. A `before_tool_call` hook checks every tool call against the passport. Default policies block 50+ patterns: shell commands, data export, messaging, MCP tools, session management. Setup: one npm command. Passport revocation propagates globally in ≤30 seconds with ≤200ms validation latency.
- **Why interesting**: This is the closest existing thing to a universal pre-action authorization layer for AI agents. The Open Agent Passport spec is published. Framework support: OpenClaw, Cursor, LangChain, CrewAI, any framework with a before-tool hook. Prompt injection cannot override it — the hook is at the platform level, not the LLM context.
- **Evidence**: [APort GitHub](https://github.com/aporthq/aport-agent-guardrails), [DEV.to article](https://dev.to/uu/i-built-the-pre-action-authorization-layer-that-would-have-stopped-clinejection-5dji), [aport.io](https://aport.io/), [OpenID Identity for Agentic AI](https://openid.net/wp-content/uploads/2025/10/Identity-Management-for-Agentic-AI.pdf)
- **Fits our case**: Submantle could integrate with the Open Agent Passport standard. An agent carrying a passport that says "allowed: process.query, not allowed: process.kill" would be checked by Submantle's hook before any kill action. Submantle provides the context ("here's what you'd break"), the passport provides the permission boundary. Together they cover both "know what you're doing" and "are you allowed to do it."
- **Risks**: APort is early-stage. The Open Agent Passport spec is v1.0 and not an official standard yet. If APort doesn't become the standard, this dependency becomes dead weight. But the pattern (DID-based agent identity + declared capabilities) is being considered by OpenID and IETF — the concept is on track to be standardized regardless of APort.

---

**2. A2A Protocol Task Lifecycle as a Native Pause Point for Submantle**

- **What**: Google's Agent2Agent protocol (A2A, now Linux Foundation, v0.3 as of late 2025) defines a task lifecycle with an `input-required` state. A remote agent can transition a task to `input-required`, pausing execution, and wait for a client to send new input to resume. Tasks have unique IDs and context IDs. Push notifications via HTTP POST to registered endpoints on state changes.
- **Why interesting**: The `input-required` state is a standards-compliant mechanism for an agent to say "I need external confirmation before proceeding." Submantle could be an A2A "remote agent" that any orchestrating agent hands off to for pre-flight validation. The orchestrator sends: "Task: kill all Node processes." Submantle responds: `input-required` + context payload. The orchestrator surfaces this to the user or uses the context to decide.
- **Evidence**: [A2A spec](https://a2a-protocol.org/latest/specification/), [A2A IBM overview](https://www.ibm.com/think/topics/agent2agent-protocol), [Google A2A upgrade blog](https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade), 50+ partners including Atlassian, Salesforce, SAP.
- **Fits our case**: Submantle implementing A2A means any A2A-compatible agent (and the ecosystem is growing) can delegate pre-action checks to Submantle as a remote agent, using standard protocols without custom integrations.
- **Risks**: A2A adoption is strong but still agent-to-agent, not agent-to-OS. An A2A-based Submantle only catches agents that choose to call it. Doesn't address the blindspot: an agent that doesn't use A2A.

---

**3. AGNTCY Infrastructure Layer — Discovery, Identity, Observability**

- **What**: AGNTCY (Linux Foundation, launched July 2025) provides infrastructure for multi-agent collaboration: discovery, identity, secure messaging, observability. It complements MCP (tool connection) and A2A (agent communication) with the coordination layer.
- **Why interesting**: AGNTCY provides agent identity and observability primitives that Submantle needs. If every agent in a system has an AGNTCY identity, Submantle can attribute actions to specific agents, build trust scores over time, and refuse service to agents with poor track records.
- **Evidence**: [Agentic AI Foundation guide](https://intuitionlabs.ai/pdfs/agentic-ai-foundation-guide-to-open-standards-for-ai-agents.pdf)
- **Fits our case**: Submantle-as-broker could register in AGNTCY as a required waypoint for destructive actions. Agents discover it, get context, proceed safely.
- **Risks**: AGNTCY is very new (July 2025). Adoption trajectory unclear.

---

### Emerging Approaches

---

**1. IETF Agentic AI Standards Working Group — No Standards Yet, Huge Signal**

- **What**: IETF hosted a side meeting at IETF 124 (~250 participants) to discuss agentic AI standardization. A strawman charter exists. Focus areas: agent discovery, context/information sharing, credential management, multimodal capabilities, human oversight. A formal working group charter is still being developed. No RFCs yet — this is exploration phase.
- **Momentum**: 250 attendees at the side meeting, active mailing list, community of framework builders signaling they want interop standards. The void that Submantle wants to fill (pre-action broker) is exactly the category IETF participants are saying needs standardization.
- **Source**: [IETF blog on agentic AI standards](https://www.ietf.org/blog/agentic-ai-standards/)
- **Fits our case**: Submantle is early enough to influence what IETF standardizes. If Submantle ships a working implementation of pre-action context brokering, it becomes a reference implementation that IETF can standardize around.
- **Maturity risk**: High. No working group chartered yet. Could take 2-4 years for RFC. Industry standards (MCP, A2A) are moving faster than IETF.

---

**2. MCP-Derived Sandbox Permission Model — Not Production Yet**

- **What**: The sandboxing article (2026 analysis) describes an emerging pattern: MCP server manifests (which list tool capabilities) could drive sandbox permissions. An agent authorized only for `web_search` gets outbound HTTPS on 443; one with `filesystem_read` gets zero network access. No production sandbox implements this yet.
- **Momentum**: The concept is described as a "future capability" in 2026 analysis. MCP tool schemas include rich capability metadata that sandbox runtimes could consume.
- **Source**: [AI Agent Sandboxing Guide 2026](https://manveerc.substack.com/p/ai-agent-sandboxing-guide)
- **Fits our case**: If this pattern emerges, Submantle could serve as the policy engine that translates agent context + current system state into sandbox rules. "Agent is running a code gen task; here are the 3 processes it started; limit its `kill` authority to those PIDs only."
- **Maturity risk**: High. No implementation exists. Conceptual stage.

---

**3. NIST AI Agent Standards Initiative**

- **What**: NIST has flagged emerging agent interoperability protocols (including MCP) as candidates for integrating security and identity controls. As of early 2026, MCP compliance is appearing in federal RFPs.
- **Momentum**: Government procurement is a forcing function. If NIST formalizes standards, enterprise buyers will require compliance — which means Submantle's broker pattern could become a compliance requirement.
- **Source**: [NIST AI agent standards analysis](https://www.joneswalker.com/en/insights/blogs/ai-law-blog/nists-ai-agent-standards-initiative-why-autonomous-ai-just-became-washingtons.html)
- **Fits our case**: Submantle's value proposition aligns with what NIST is framing: security-first agent interactions, audit trails, controlled access to system resources.
- **Maturity risk**: Medium-high. Government timelines are slow. But the directional signal is very strong for enterprise markets.

---

### Gaps and Unknowns

---

**1. No existing solution owns the "environmental context before action" problem.**
Every product found addresses either: (a) permission enforcement ("is this agent allowed to do X?") or (b) audit logging ("what did this agent do?"). None addresses: (c) contextual enrichment before action ("here's what you'd break if you do X"). Submantle's core proposition — process-aware context delivery — has no direct competitor as of March 2026.

**2. The enforcement gap is real and architectural.**
Current approaches either block blindly (Tetragon kills the process) or ask contextlessly (human-in-the-loop shows the raw tool call). No layer combines: "intercept the action + enrich with context + present meaningful question." This requires Submantle's knowledge graph to exist before the interception can be meaningful.

**3. eBPF cannot currently pause-query-allow/deny.**
eBPF enforcement via Tetragon terminates the process — it cannot asynchronously query Submantle, wait for a response, and then allow or deny the syscall. macOS ESF AUTH events CAN do this (they're synchronous allow/deny decisions). Windows kernel callbacks are also synchronous but can deny. This means the "pause and ask Submantle" pattern works natively on macOS ESF; it requires more complex proxy/hook approaches on Linux and Windows.

**4. The "must work without agent rewriting" constraint creates a hierarchy.**
From most to least invasive:
- OS kernel layer (eBPF/ESF/Windows callbacks): catches everything, requires kernel components
- MCP proxy layer: catches all MCP traffic, requires proxy deployment
- Framework middleware layer: catches framework-managed tools, requires per-framework plugins
- Agent-voluntary: agent calls Submantle before acting, requires agent design choice

Submantle needs a strategy for each layer. Pure voluntary compliance (agents call Submantle because they're supposed to) is insufficient for safety-critical use.

**5. Framework hook coverage is incomplete.**
CrewAI has no native tool-execution hook (only LLM-level hooks). AutoGen has no documented pre-action hook. LangChain declined to add `before_tool` hooks (GitHub #33441 closed "not planned"). OpenAI Agents SDK has `needs_approval` but only for declared tools. If Submantle relies solely on framework hooks, agents on these frameworks may have no intercept point.

**6. Agent identity is unsolved at scale.**
APort's Open Agent Passport is promising but pre-standard. IETF SCIM extensions for agents are in draft. Without stable agent identity, Submantle cannot build reliable trust models — it doesn't know which agent is making the request or whether that agent's context claim is trustworthy.

**7. Multi-agent orchestration is the hard case.**
When Agent A spawns Agent B which spawns Agent C, and C takes a destructive action, accountability is diffuse. Current A2A and MCP standards don't propagate intent context through the delegation chain. Submantle would need to track the full provenance chain to give meaningful context: "Agent C (spawned by B, spawned by A, which was started by Claude Code, which was initiated by the user at 2:34pm) is about to kill this process."

---

### Synthesis

**Submantle's position in the existing landscape is genuinely novel.** The infrastructure stack it needs exists — MCP for the API surface, eBPF/ESF for the OS layer, framework hooks for the application layer — but nobody has assembled them with process-aware contextual enrichment as the core value.

**The recommended integration architecture has three tiers:**

**Tier 1 — Submantle as MCP Server (ship first)**
Expose Submantle's process awareness as an MCP server with tools: `query_process_context(action, target)`, `check_action_safety(proposed_action)`. Any MCP-compatible agent (Claude, GPT-4o, Gemini, LangChain, CrewAI) can query it. This requires zero agent rewriting — just registering the Submantle MCP server in the agent's MCP config. Use MCP Elicitation for human-in-the-loop pause when Submantle detects high-risk actions. This layer catches agents that voluntarily comply.

**Tier 2 — Submantle as MCP Proxy (enterprise deployment)**
Deploy Submantle as an MCP gateway/proxy layer that all agent traffic routes through. Every `tools/call` to any MCP server passes through Submantle first. Submantle enriches the call with context and can block or flag based on its knowledge graph. ACL policies per agent identity (using Open Agent Passport or equivalent). This layer catches all MCP agents without their cooperation.

**Tier 3 — Submantle as OS-Level Guardian (safety guarantee)**
On macOS: ESF AUTH event subscription for process, file, and network operations. On Linux: eBPF via Tetragon-style enforcement. On Windows: kernel callbacks + ETW + user-mode API hooks. This layer is the true safety guarantee — it catches agents regardless of framework, protocol, or cooperation level. This requires signed kernel components and is the hardest to ship, but it's what makes Submantle actually reliable when stakes are high.

**The key architectural insight:** Tiers 1 and 2 are the product's commercial surface (easy to integrate, high value). Tier 3 is the product's safety guarantee (hard to build, but what makes it trustworthy for enterprise). Submantle can ship and gain adoption at Tier 1 while building Tier 3.

**The immediate competitive window:** No competitor owns the process-aware context layer. MCP proxies do enforcement without context. APort does identity-based permissions without context. eBPF tools do OS-level enforcement without context. Submantle's differentiator — the knowledge graph that knows what processes ARE, not just that they exist — must be protected as the core moat. The integration protocols (MCP, A2A, framework hooks) are means to an end; the knowledge graph is the product.

**The protocol landscape is moving fast and in Submantle's favor:** MCP is the de-facto standard. A2A is gaining enterprise adoption. IETF is actively exploring pre-action safety standards. Enterprise buyers are starting to require agent governance. Submantle is arriving at exactly the right moment.
