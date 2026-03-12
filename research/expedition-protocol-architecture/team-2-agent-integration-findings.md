# Team 2 Findings: Agent Integration Surface
## Date: 2026-03-11
## Researcher: Team Member 2

---

## Executive Summary

MCP (Model Context Protocol) is the dominant, production-ready integration surface for AI agents as of March 2026. Anthropic-originated but community-governed, with an official Go SDK (v1.4.0, jointly maintained by Anthropic and Google), making it a natural fit for Submantle's production language. The integration path is clear: Submantle as an MCP server, exposing trust queries and ambient awareness as Tools and Resources. Every major agent framework (LangChain, CrewAI, AutoGen, Semantic Kernel) either natively connects to MCP servers or has an adapter. A single MCP server implementation reaches the majority of production agents without requiring framework-specific connectors.

---

## 1. What is MCP? Origin, Architecture, Adoption

### What It Is

Model Context Protocol is an open standard for connecting AI applications to external systems. Created by Anthropic in late 2024, now community-governed under the MCP organization on GitHub. The official analogy from the docs: "USB-C for AI applications" -- a standardized connection point that works with anything.

Source: modelcontextprotocol.io/introduction, verified 2026-03-11

### Architecture

MCP follows a client-server model with three participants:
- MCP Host: The AI application (Claude Desktop, Cursor, VS Code, an agent framework)
- MCP Client: Component inside the host managing one connection to one server
- MCP Server: A program that exposes capabilities (tools, resources, prompts)

The data layer uses JSON-RPC 2.0 for all messages. Two transport mechanisms:

1. stdio: Server runs as subprocess; client communicates via stdin/stdout. Zero network overhead. One client per server. Best for local servers.
2. Streamable HTTP: Server is an independent process. HTTP POST for client-to-server. Optional SSE for streaming server-to-client. Supports multiple concurrent clients. Required for remote/network deployment.

Source: modelcontextprotocol.io/docs/concepts/architecture, verified 2026-03-11

### Three Core Primitives (Server-Exposed)

| Primitive | Description | Submantle Example |
|-----------|-------------|-------------------|
| Tools | Executable functions the LLM invokes | submantle_get_trust(agent_id) |
| Resources | Data sources providing context | submantle://ambient-stream |
| Prompts | Reusable interaction templates | "Analyze this agent behavioral history" |

Tools are model-controlled (LLM decides when to call them). Resources are application-driven (host decides when to include them as context). Resources support subscriptions -- clients subscribe to a URI and receive push notifications when data changes. This is the ambient stream model Submantle needs.

Source: MCP spec 2025-11-25, verified 2026-03-11

### Tool Discovery and Invocation (Exact Protocol)

Discovery request from client:

    {"jsonrpc":"2.0","id":1,"method":"tools/list"}

Discovery response from server:

    {"result":{"tools":[{"name":"submantle_get_trust","description":"...","inputSchema":{"type":"object","properties":{"agent_id":{"type":"string"}},"required":["agent_id"]}}]}}

Invocation request from client:

    {"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"submantle_get_trust","arguments":{"agent_id":"email-bot-by-acme"}}}

Invocation response from server (with outputSchema):

    {"result":{"content":[{"type":"text","text":"trust_score: 0.87, tier: trusted"}],"structuredContent":{"trust_score":0.87,"tier":"trusted","total_queries":1243,"incidents":0}}}

Tools carry: name (unique identifier), description (what the LLM reads to decide when to use it), inputSchema (JSON Schema for parameters), optional outputSchema (JSON Schema for structured results with guaranteed validation).

### Adoption as of March 2026

- TypeScript SDK: 11.8k GitHub stars, v1.27.1 (Feb 24, 2026), 158 contributors, 1,400 commits
- Python SDK: v1.26.0 (Jan 24, 2026), Tier 1 (full spec compliance), Beta status
- Go SDK: v1.4.0 (Feb 2026), 4.1k stars, 373 forks, 995 dependent projects, jointly maintained by Anthropic and Google. This is Submantle's production SDK.
- Also available: C#, Java, Rust, Swift, Ruby, PHP, Kotlin
- MCP clients: Claude Desktop, ChatGPT, VS Code Copilot, Cursor, Windsurf, Zed, Replit, and dozens more

Source: GitHub repos and modelcontextprotocol.io/docs/sdk, verified 2026-03-11

---

## 2. Tool Use Across AI Providers: The Common Pattern

### Anthropic Claude Tool Use

Tools defined with: name, description, input_schema (JSON Schema). When Claude decides a tool is needed, it returns a tool_use content block. The host executes and returns a tool_result block. Claude continues reasoning with the result.

Anthropic supports strict: true on tool definitions for guaranteed schema conformance via Structured Outputs. This matters for Submantle: strict mode eliminates malformed trust queries reaching the server.

Source: docs.anthropic.com tool use docs, verified 2026-03-11

### OpenAI Function Calling

Nearly identical pattern: tools defined with name, description, parameters (JSON Schema). Model returns a function call with arguments. Host executes and returns results.

Critical constraint documented by OpenAI: no more than 10-20 tools per LLM call -- model accuracy degrades beyond that. Submantle's MCP tool surface should stay under 10 for MVP.

Source: Semantic Kernel docs referencing OpenAI function calling guide, verified 2026-03-11

### The Universal Pattern

Every major LLM provider (Anthropic, OpenAI, Google, Mistral, Cohere) uses the same tool-calling loop:
1. Host provides list of tools with JSON Schema descriptions
2. Model selects tool and provides arguments
3. Host executes and returns result
4. Model continues

MCP is the standardization layer above this. MCP defines how tools are discovered from external servers (via tools/list) and how calls are routed (via tools/call). Individual AI providers still have their own native APIs, but MCP abstracts the discovery layer so the same Submantle MCP server works with all of them without provider-specific code.

---

## 3. Agent Frameworks: Integration Models

### LangChain / LangGraph

Official MCP adapter (langchain-mcp-adapters, 3.4k GitHub stars as of March 2026). Wraps MCP tools into LangChain-compatible tools via MultiServerMCPClient. An agent connects to multiple MCP servers simultaneously, loads all tools via load_mcp_tools(), and binds them to any LLM via bind_tools().

What this means for Submantle: A LangChain/LangGraph agent can connect to a Submantle MCP server with roughly 10 lines of configuration code. No Submantle-specific integration work needed from the agent developer.

Source: github.com/langchain-ai/langchain-mcp-adapters, 3.4k stars, verified 2026-03-11

### CrewAI

CrewAI supports MCP via their toolkit. Agents are assigned tools at instantiation. Custom tools are built by subclassing BaseTool or using the @tool decorator. The framework also integrates LangChain Tools directly, so the LangChain MCP adapter path applies here too.

Source: docs.crewai.com/concepts/tools, verified 2026-03-11

### Microsoft Semantic Kernel

Semantic Kernel explicitly supports three plugin import methods: native code, OpenAPI specification, and MCP Server. The docs state directly: "You can create a MCP Server from your Kernel instance, which allows other applications to consume your plugins as a service." Submantle as an MCP server would be natively importable as a Semantic Kernel plugin with no custom code.

Source: learn.microsoft.com/en-us/semantic-kernel/concepts/plugins/, verified 2026-03-11

### Framework Integration Summary

| Framework | MCP Support | Path to Submantle |
|-----------|-------------|-------------------|
| LangChain/LangGraph | Official adapter (3.4k stars) | Drop-in via langchain-mcp-adapters |
| CrewAI | MCP toolkit | Via adapter or direct MCP client |
| Semantic Kernel | Native MCP server import | Native, documented feature |
| AutoGen | Via MCP adapter pattern | Tool framework integration |
| Claude (direct) | Native MCP host | First-class integration |
| ChatGPT | MCP support | Native integration |
| VS Code / Cursor / Windsurf | Native MCP hosts | Configuration-based |

The network effect is real: an MCP server is not 7 different integrations. It is one protocol that all of these clients speak. Build once, reach all.

---

## 4. The MCP Authorization Model (Critical for Submantle)

### STDIO Transport (Local)

For local MCP servers (same machine, subprocess), the spec says: do not use the OAuth spec; retrieve credentials from the environment. In practice: the host passes a bearer token as an environment variable. The server reads it at startup.

### Streamable HTTP Transport (Remote/Network)

MCP has a full OAuth 2.1 authorization specification for HTTP-based servers:
- Servers act as OAuth 2.1 resource servers
- Clients use bearer tokens in Authorization: Bearer token headers on every request, even within a session
- Servers expose WWW-Authenticate with resource metadata URL to guide clients through auth discovery
- Three registration mechanisms: pre-registration (hardcoded client_id), Client ID Metadata Documents (HTTPS URL as client_id), Dynamic Client Registration (RFC7591)
- PKCE required (S256 challenge method) for all authorization code flows
- Session management via MCP-Session-Id header

For Submantle specifically: An agent that has registered with Submantle and received a bearer token includes that token in every MCP HTTP request. The Submantle MCP server validates the token using the existing AgentRegistry.verify() logic and knows exactly which registered agent is asking. This maps perfectly to the existing architecture -- no new auth model is needed.

Source: modelcontextprotocol.io/specification/2025-11-25/basic/authorization, verified 2026-03-11

### The Simplest Auth Path for Submantle MVP

For V1 (local, single machine):
1. Agent calls Submantle REST API (POST /api/agents/register) to register and get token
2. Token stored as environment variable
3. MCP server (stdio transport) reads token from env at startup
4. All subsequent MCP calls are pre-authorized

For V2 (network, multi-tenant):
1. Submantle MCP server responds to unauthenticated requests with HTTP 401 + WWW-Authenticate header
2. MCP clients follow the OAuth 2.1 discovery flow automatically
3. Submantle acts as its own authorization server or delegates to one
4. Full bearer token flow per the spec

---

## 5. The A2A Protocol

### What It Is

Agent2Agent (A2A) is an open protocol enabling communication and interoperability between opaque agentic applications. Created by Google, contributed to the Linux Foundation. Repository metrics: 22.4k GitHub stars, 144 contributors, 2.3k forks, v0.3.0 (July 30, 2025). Active development.

Uses JSON-RPC 2.0 over HTTP(S). Agents publish Agent Cards describing their capabilities. Other agents discover these cards and initiate tasks.

Source: a2aprotocol.ai, github.com/google/A2A, verified 2026-03-11

### A2A vs. MCP: Explicitly Complementary

The official A2A documentation makes the distinction explicit:
- MCP: Tool integration. Connects LLMs to data sources, APIs, tools. Hierarchical (host calls server).
- A2A: Agent collaboration. Enables agents as peers -- neither knows the other's internals. Lateral (agent negotiates with agent).

Recommended pattern from A2A docs: "Use MCP for tools, A2A for agents."

### A2A Backers (50+ partners)

LangChain, Salesforce, SAP, ServiceNow, PayPal, Workday, MongoDB, Intuit, Atlassian, Box, Cohere, UKG. Enterprise-heavy -- aimed at business workflow automation where one agent delegates to another.

### Relevance to Submantle

A2A matters for Submantle's future, not V1. When agents collaborate peer-to-peer via A2A, they need to verify each other's trustworthiness before delegating work. An agent presenting its Submantle trust attestation (W3C VC + SD-JWT) to an A2A peer is the natural integration pattern. Submantle provides the credential; A2A defines how agents exchange it.

Short term: build for MCP. Long term: trust attestations flow through A2A interactions.

---

## 6. What a Submantle SDK Would Look Like

### Step A: Register with Submantle

Today (REST API):
  POST /api/agents/register with agent_name, version, author, capabilities
  Response: token (HMAC-SHA256 bearer credential), agent_name

Future (MCP tool):
  tools/call submantle_register with {agent_name, version, author, capabilities}
  Response structuredContent: {token, agent_name, tier: "registered"}

### Step B: Query Another Agent's Trust Score

Via MCP Tool call:
  tools/call submantle_get_trust with {agent_id: "email-bot-by-acme"}
  Response structuredContent: {trust_score: 0.87, total_queries: 1243, incidents: 0, tier: "trusted", registered_days_ago: 142}

The outputSchema on the tool definition guarantees this structure -- no parsing required, LLMs can reliably consume it.

### Step C: Present Its Own Trust Attestation

Via MCP Tool call:
  tools/call submantle_get_attestation with {agent_token: "bearer-token", format: "sd-jwt"}
  Response: W3C VC 2.0 + SD-JWT credential the agent presents to brands and platforms as proof of trust tier. Portable, verifiable, carries the agent's behavioral history.

### What No-SDK Integration Looks Like

Because MCP is JSON-RPC 2.0 over HTTP, the minimum for any agent to talk to Submantle:
1. HTTP POST to /mcp endpoint
2. JSON-RPC initialize call (capability handshake, one round trip)
3. JSON-RPC tools/call with tool name and arguments

No Submantle SDK required. Any language with an HTTP library works. The official SDKs (Go, Python, TypeScript) just make it ergonomic.

---

## Battle-Tested Approaches

### MCP as Primary Integration Surface

What: Build Submantle as an MCP server. Expose trust queries and awareness data as Tools and Resources.

Evidence: Official Go SDK at v1.4.0, 4.1k stars, 995 dependent projects, co-maintained by Anthropic and Google. TypeScript SDK has 11.8k stars. Every major agent framework either natively supports MCP or has an official adapter.

Source: github.com/modelcontextprotocol/go-sdk, github.com/modelcontextprotocol/typescript-sdk, modelcontextprotocol.io/docs/sdk, verified 2026-03-11

Fits our case because: MCP is explicitly designed for agents querying external systems for context and action. Submantle IS the context provider. The architectural match is not incidental. One MCP server serves Claude, ChatGPT, LangChain, CrewAI, Semantic Kernel, VS Code Copilot simultaneously with no per-client integration work.

Tradeoffs/Risks:
- MCP spec is evolving. The old HTTP+SSE transport was deprecated in favor of Streamable HTTP. Breaking changes have happened between protocol versions. Pin to a specific protocol version in Submantle's implementation.
- OAuth 2.1 auth for HTTP transport adds implementation complexity, but the spec is thorough and maps to Submantle's existing token model.
- For local (same-machine) deployment, stdio transport limits to one client at a time. Acceptable for V1; Streamable HTTP resolves this for V2.

### Ambient Stream via MCP Resources and Subscriptions

What: Expose real-time process awareness data as a subscribable MCP Resource. Agents subscribe once; Submantle pushes updates via notifications/resources/updated.

Evidence: MCP Resources support subscription natively (via resources/subscribe and notifications/resources/updated notifications). Documented in the 2025-11-25 spec and implemented in all Tier 1 SDKs.

Source: modelcontextprotocol.io/specification/2025-11-25/server/resources, verified 2026-03-11

Fits our case because: This is Submantle's ambient stream concept mapped directly to an existing MCP primitive. Agents feel the ground by subscribing to the resource rather than polling. No custom protocol needed.

Tradeoffs/Risks:
- Resource subscriptions are stateful -- server must track which clients are subscribed and push updates. More complex than stateless tool calls.
- Streamable HTTP transport required for push notifications to remote clients (stdio is inherently request-response, cannot push unsolicited messages).

---

## Novel Approaches

### MCP + A2A Trust Bridge

What: Submantle issues W3C VC trust attestations (already designed) that agents present during A2A peer negotiations. Submantle MCP server is the credential issuer; A2A is the credential presentation channel.

Evidence: A2A v0.3.0 supports authentication and authorization as first-class features. W3C VC 2.0 + SD-JWT is designed for portable presentation. The two are architecturally complementary -- each solves a different layer.

Source: github.com/google/A2A (22.4k stars, Linux Foundation), a2aprotocol.ai, verified 2026-03-11

Fits our case because: Closes the loop on the portable trust promise. An agent earns trust through Submantle MCP interactions, carries the VC attestation, presents it to A2A peers who verify with Submantle.

Tradeoffs/Risks: A2A is at v0.3.0, pre-1.0. Credential presentation format may shift before 1.0. This is future work, not V1 scope.

### MCP Tools with Structured Output Schemas

What: Define outputSchema on all Submantle trust tools, enabling strict schema validation and direct LLM consumption of structured trust data without text parsing or hallucination risk.

Evidence: MCP spec 2025-11-25 explicitly defines outputSchema as a JSON Schema field on Tool definitions. When provided, servers must return structured results conforming to the schema. Anthropic strict mode for tool use guarantees schema conformance.

Source: modelcontextprotocol.io/specification/2025-11-25/server/tools/, verified 2026-03-11

Fits our case because: Trust scores are structured data (numeric score, tier, query count, incident count, registration age). An LLM consuming trust data with a guaranteed schema makes reliable decisions without parsing failures or type errors.

Tradeoffs/Risks: Output schema must be kept in sync with trust data model changes. Adds schema definition overhead to each tool.

---

## Emerging Approaches

### MCP Tasks (Experimental) for Async Attestation Issuance

What: MCP's experimental Tasks primitive provides durable execution wrappers for long-running operations. W3C VC signing (attestation issuance) could use this pattern for async credentialing.

Evidence: Tasks listed as Experimental in MCP spec 2025-11-25. "Durable execution wrappers that enable deferred result retrieval and status tracking for MCP requests."

Source: modelcontextprotocol.io/docs/concepts/architecture, verified 2026-03-11

Tradeoffs/Risks: Marked experimental -- API may change before stabilization. Not required for MVP trust queries, which are synchronous operations.

### MCP Elicitation for Human-Confirmed Incident Recording

What: MCP's Elicitation primitive allows servers to request additional information from users. When an incident is flagged, Submantle could elicit confirmation from the agent's human operator before recording it in the trust ledger.

Fits our case because: Incident taxonomy (the number one unresolved design decision from prior trust layer research) needs human judgment. Elicitation creates a structured, MCP-native channel for that.

Tradeoffs/Risks: Client must support Elicitation (not all MCP clients do as of March 2026). High friction for autonomous agents running without human-in-the-loop.

---

## Gaps and Unknowns

1. MCP Auth Bootstrapping for Stdio Mode
   For local deployments (stdio transport), the spec says retrieve credentials from the environment. Submantle needs a pre-auth step: agent registers via REST API (POST /api/agents/register), stores the token, and passes it as an env var before starting the MCP subprocess. No standard convention for this exists in the MCP spec -- implementer discretion.

2. Tool Count vs. LLM Accuracy Tradeoff
   OpenAI recommends 10-20 tools max per LLM call, with accuracy degrading beyond that. If Submantle exposes many tools (trust, process, devices, attestation, etc.), agents using OpenAI models may see degraded tool selection. Mitigation: keep MCP tool count under 10 for MVP by grouping related capabilities or using Resources for passive data that does not require active invocation.

3. CrewAI Native MCP Status
   CrewAI official docs did not clearly document direct MCP server support in the portion accessible to this research. The LangChain adapter path works (CrewAI integrates LangChain Tools natively), but CrewAI's own first-party MCP integration story is unclear. Low risk -- the adapter path is confirmed functional.

4. A2A Credential Presentation Format
   A2A v0.3.0's authentication model vis-a-vis W3C VC presentation is not fully documented in publicly accessible form. Compatibility with W3C VC 2.0 + SD-JWT needs verification before the trust bridge pattern is designed in detail. Future-work verification, not blocking for MCP.

5. Python Prototype to Go MCP Server Migration
   The existing prototype is Python (FastAPI). The Go MCP SDK (v1.4.0) is the correct production target. AgentRegistry.verify() and the trust formula must be faithfully re-implemented in Go. Go's concurrency model differs from Python's async. Account for this in the production timeline.

---

## Synthesis

### The Single Integration That Reaches the Most Agents

Build Submantle as an MCP server using the official Go SDK (v1.4.0).

This is not a close call. MCP has:
- Official Go SDK with production metrics (4.1k stars, 995 dependent projects, co-maintained by Anthropic + Google)
- Native support in Claude, ChatGPT, VS Code Copilot, Cursor, Windsurf (the tools developers use to build and run agents)
- Official adapters for LangChain and Semantic Kernel (the frameworks that build production agent pipelines)
- A complete authorization spec (OAuth 2.1) that maps directly to Submantle's existing HMAC bearer token model
- Ambient stream support via the Resources + Subscriptions primitive

A LangChain agent, a Claude Desktop user, a CrewAI crew, and a Semantic Kernel enterprise system can all connect to the same Submantle MCP server with zero Submantle-specific client code. Widest reach, least effort, single implementation.

### What the Submantle MCP Server Exposes

Tools (active queries, model-controlled -- LLM decides when to call):
- submantle_register: register this agent with Submantle, receive HMAC bearer token
- submantle_get_trust: query trust score for any registered agent by agent_id
- submantle_get_attestation: get W3C VC trust credential for this agent (portable proof of tier)
- submantle_query_process: what is this process and what does it mean for the system?
- submantle_what_would_break: given a proposed action, what is the blast radius?

Resources (passive context, application-driven -- host decides when to include):
- submantle://ambient-stream: real-time process awareness, subscribable for push updates
- submantle://device-list: connected devices and their current state
- submantle://process-snapshot: current process awareness snapshot (non-subscribable, polling-safe)

For anonymous agents (no registration): Awareness tools work; trust-specific tools return tier: "anonymous", trust_score: null.
For registered agents: Bearer token in every request; trust accumulates via record_query() per the existing AgentRegistry design.

### The Authorization Mapping

Submantle's existing bearer token model maps directly to MCP HTTP transport auth:
- Agent registers via submantle_register MCP tool, receives HMAC-SHA256 token
- Agent stores token; includes it as Authorization: Bearer token on every subsequent MCP HTTP request
- Submantle MCP server validates via AgentRegistry.verify() (existing code, unchanged)
- record_query() called on every valid authenticated request; trust score accumulates
- Trust score updates reflected immediately in subsequent submantle_get_trust calls

This is the existing auth model surfaced through MCP's standard HTTP transport layer. No new auth design required.

### Build Order Recommendation

Phase 1 (Immediate): Wrap existing FastAPI REST routes as MCP Tools via Python MCP SDK (FastMCP, mcp package v1.2.0+). Enables MCP clients to reach Submantle within one session -- no Go migration required. Prototype validates the MCP integration surface before committing to the Go rewrite.

Phase 2 (Trust Layer Wiring): As trust layer wires (record_query, compute_trust, issue_attestation), expose as new MCP tools: submantle_get_trust, submantle_get_attestation.

Phase 3 (Resources and Subscriptions): Implement ambient stream as a subscribable MCP Resource. Requires Streamable HTTP transport with SSE for server-push notifications.

Phase 4 (Go Production Server): Rewrite MCP server in Go using official Go SDK (v1.4.0). Python prototype served its purpose -- retire it.

Phase 5 (A2A Bridge): Once trust attestations are issuing, design A2A credential presentation pattern. Submantle attestations become the trust signal that A2A agents present to each other during peer delegation.

### Why A2A Does Not Compete with MCP for Submantle's Integration Surface

MCP is for tool use -- agent queries a system. A2A is for peer delegation -- agent delegates to another agent. Submantle is a system that agents query, not an agent itself. Therefore MCP is the correct protocol for Submantle's integration surface. A2A becomes relevant when agents use Submantle-issued credentials in their peer negotiations -- Submantle provides the credential, A2A is the channel where it gets presented. Complementary, not competitive.

---

## Key Sources (All Verified 2026-03-11)

| Claim | Source |
|-------|--------|
| MCP architecture (host/client/server, primitives, lifecycle) | modelcontextprotocol.io/docs/concepts/architecture |
| MCP tool spec (JSON-RPC format, inputSchema, outputSchema) | modelcontextprotocol.io/specification/2025-11-25/server/tools/ |
| MCP transport spec (stdio, Streamable HTTP, session management) | modelcontextprotocol.io/specification/2025-11-25/basic/transports |
| MCP authorization spec (OAuth 2.1, PKCE, bearer tokens) | modelcontextprotocol.io/specification/2025-11-25/basic/authorization |
| MCP resources and subscriptions | modelcontextprotocol.io/specification/2025-11-25/server/resources |
| Go SDK (v1.4.0, 4.1k stars, 995 dependents, Anthropic+Google) | github.com/modelcontextprotocol/go-sdk |
| TypeScript SDK (11.8k stars, v1.27.1, Feb 2026) | github.com/modelcontextprotocol/typescript-sdk |
| Python SDK (v1.26.0, Jan 2026, Tier 1) | pypi.org/project/mcp/ |
| SDK tier classifications (TypeScript, Python, C#, Go = Tier 1) | modelcontextprotocol.io/docs/sdk |
| LangChain MCP adapter (3.4k stars) | github.com/langchain-ai/langchain-mcp-adapters |
| Semantic Kernel native MCP server import | learn.microsoft.com/semantic-kernel/concepts/plugins/ |
| CrewAI tool integration model | docs.crewai.com/concepts/tools |
| A2A protocol (22.4k stars, v0.3.0, Linux Foundation) | github.com/google/A2A, a2aprotocol.ai |
| Anthropic Claude tool use (strict mode, schema conformance) | docs.anthropic.com tool use docs |
| OpenAI 10-20 tool limit recommendation | Semantic Kernel docs referencing OpenAI function calling guide |
