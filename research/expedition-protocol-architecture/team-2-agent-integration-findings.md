# Team 2 Findings: Agent Integration Surface
## Date: 2026-03-11
## Researcher: Team Member 2

---

## Preamble: Why This Matters for Substrate

The question "how do agents connect to things?" has a surprisingly concrete answer as of March 2026: through MCP, or through framework-specific tool/function calling that will eventually converge on MCP. Substrate's MCP server is not a nice-to-have — it is the primary integration surface. Everything in this report is framed around that reality.

---

## Part 1: What Is MCP, Exactly?

### Definition

Model Context Protocol (MCP) is an open, JSON-RPC 2.0 based protocol for connecting AI applications (hosts/clients) to external data sources and capability providers (servers). Launched by Anthropic on November 25, 2024, and now under independent governance with a Specification Enhancement Proposal (SEP) process, working groups, and an official registry.

The best analogy from the official docs: "MCP is the USB-C port for AI applications." One integration, works everywhere.

**Source:** modelcontextprotocol.io/introduction, modelcontextprotocol.io/specification/2025-03-26 (accessed 2026-03-11)

### How It Works Technically

MCP is a three-party architecture:

| Role | What It Is | Example |
|------|-----------|---------|
| **Host** | The AI application; manages lifecycle, security, multiple clients | Claude Desktop, VS Code Copilot |
| **Client** | A connector inside the host; maintains one connection to one server | Created by host per server |
| **Server** | A program exposing capabilities via MCP primitives | Substrate daemon, GitHub server |

**Transport mechanisms (as of spec 2025-03-26):**

1. **stdio** — Client launches server as subprocess; JSON-RPC messages on stdin/stdout, newline-delimited. Zero network overhead. Recommended for local servers. The client controls the server lifecycle entirely.

2. **Streamable HTTP** — Server runs independently; client sends JSON-RPC via HTTP POST to a single endpoint. Server can respond with `application/json` (single response) or `text/event-stream` (SSE stream for multiple messages). Client can also open a GET SSE stream for server-initiated messages. Supports session IDs (`Mcp-Session-Id` header), resumability via `Last-Event-ID`, and backwards compatibility with deprecated HTTP+SSE (2024-11-05 spec).

**Protocol primitives (what servers expose):**
- **Tools** — Executable functions the LLM can invoke (e.g., `substrate/get_status`, `substrate/check_trust`)
- **Resources** — Data the LLM can read (e.g., process list as a resource)
- **Prompts** — Reusable templates

**Protocol primitives (what clients expose to servers):**
- **Sampling** — Server requests an LLM completion from the host
- **Elicitation** — Server requests user input

**Connection lifecycle:**
1. Client sends `initialize` request with `protocolVersion` and client `capabilities`
2. Server responds with `capabilities` (which primitives it supports, whether it supports `listChanged` notifications, etc.)
3. Client sends `notifications/initialized`
4. Active session: client discovers tools via `tools/list`, calls them via `tools/call`, gets responses as content arrays
5. Server can push `notifications/tools/list_changed` when its tool surface changes
6. Session terminates via HTTP DELETE (Streamable HTTP) or stdin close (stdio)

**Source:** modelcontextprotocol.io/specification/2025-03-26/architecture, modelcontextprotocol.io/specification/2025-03-26/basic/transports, modelcontextprotocol.io/docs/concepts/architecture (all accessed 2026-03-11)

### MCP Authentication

For stdio: credentials come from the environment (env vars, config files). No spec-level auth — the client controls the subprocess.

For Streamable HTTP: OAuth 2.1 is the specified mechanism. Flow:
1. Client hits `/.well-known/oauth-authorization-server` for metadata discovery (RFC 8414)
2. Client registers dynamically (RFC 7591) or uses hardcoded client ID
3. Authorization Code flow (user-facing) or Client Credentials flow (machine-to-machine)
4. PKCE required for all public clients
5. Bearer tokens sent as `Authorization: Bearer <token>` on every request

For Substrate's use case (agents calling in), **Client Credentials** is the right OAuth grant type. No human in the loop. The agent authenticates as itself, not on behalf of a user.

**Source:** modelcontextprotocol.io/specification/2025-03-26/basic/authorization (accessed 2026-03-11)

### MCP Adoption (March 2026)

**Quantitative evidence:**
- MCP Python SDK: version 1.26.0 released January 24, 2026. GitHub: 22,100 stars, 821 commits. Active.
- MCP TypeScript SDK: Similar scale.
- Third-party server directory mcp.so: **18,419 MCP servers** collected as of March 2026
- Official GitHub repo (modelcontextprotocol/servers) hosts reference servers and links to the official MCP Registry for community server publishing
- Official SDKs: TypeScript, Python, C#, Go (Tier 1 — full feature parity, maintained by core team); Java, Rust (Tier 2); Swift, Ruby, PHP, Kotlin (Tier 3/TBD)

**Qualitative evidence:**
- Claude Desktop: MCP support built-in
- VS Code Copilot: MCP support built-in
- Cursor: MCP support built-in
- OpenAI Agents Python SDK: Native MCP support across all four transport types (stdio, SSE, Streamable HTTP, hosted)
- LangChain/LangGraph: Official `langchain-mcp-adapters` package (v0.2.1, released December 9, 2025)
- Google Vertex AI Agent Engine: MCP listed as supported protocol
- AutoGen/AG2: MCP-compatible (via tool wrapping)
- LlamaIndex: ToolSpec model compatible with MCP tool definitions

**Source:** pypi.org/project/mcp, github.com/modelcontextprotocol/python-sdk, mcp.so, modelcontextprotocol.io/clients, pypi.org/project/langchain-mcp-adapters (all accessed 2026-03-11)

### How Agents Discover and Connect to MCP Servers

There is **no universal discovery registry** — this is the honest answer. Discovery currently works through three mechanisms:

1. **Manual configuration** — Users or developers specify server URLs/commands in their host app's config (e.g., Claude Desktop's `claude_desktop_config.json`, VS Code settings). Most common today.

2. **The MCP Registry** — Official registry at the MCP website. Developers publish servers; users browse and install. Growing, not yet the primary discovery path.

3. **mcp.so and Smithery** — Third-party directories with thousands of servers. Community-curated.

4. **Embedded in frameworks** — OpenAI Agents SDK has `MCPServerManager` that handles connecting to multiple servers and exposing them to agents. LangChain adapters wrap servers into tools automatically.

**For Substrate specifically:** The daemon runs locally (stdio transport) or as a service (Streamable HTTP). Agents discover it by:
- User installing Substrate and it registering itself in their agent host's config
- Developer explicitly pointing their agent at Substrate's endpoint
- Future: Substrate could register itself in the official MCP Registry so developers can find it

---

## Part 2: All Major Agent Frameworks — How They Connect

### 2.1 OpenAI Agents Python SDK

**Connection model:** Five tool types:
1. `HostedMCPTool` — Pushes execution to OpenAI's servers (Responses API). Zero-latency for OpenAI-hosted servers.
2. `MCPServerStreamableHttp` — Manages connection to a remote Streamable HTTP MCP server
3. `MCPServerSse` — Deprecated HTTP+SSE transport (backwards compatibility)
4. `MCPServerStdio` — Launches local subprocess, communicates via stdio
5. `MCPServerManager` — Coordinates multiple servers, exposes their tools to agents

Agents receive tools from SDK via auto-introspection: `@function_tool` decorator or `inspect` module parses Python function signatures → JSON schema. Tools are passed to the model as JSON schema definitions.

**Authentication:** API key in environment for OpenAI's own API. For third-party MCP servers: OAuth (HTTP) or env vars (stdio).

**Substrate integration path:** Substrate runs as an `MCPServerStdio` (local daemon) or `MCPServerStreamableHttp` (network service). Agent registers capabilities on connect. Zero rewrites needed.

**Source:** openai.github.io/openai-agents-python/mcp, openai.github.io/openai-agents-python/tools (accessed 2026-03-11)

### 2.2 LangChain / LangGraph

**Connection model:** Tool-first. Agents receive a list of `BaseTool` subclasses. The `langchain-mcp-adapters` package (v0.2.1) converts MCP servers into LangChain tools automatically. Transport options: stdio, HTTP, SSE, Streamable HTTP. Custom headers supported for auth/tracing.

LangGraph wraps tool invocations in a graph of nodes — tools are the edges. An agent node decides which tool to call; a tool node executes it.

**Authentication:** API keys via environment. HTTP MCP servers: custom headers or OAuth.

**Substrate integration path:** Substrate MCP server → `langchain-mcp-adapters` converts it to LangChain tools → available to any LangGraph agent. No Substrate-specific LangChain plugin needed.

**Source:** pypi.org/project/langchain-mcp-adapters (accessed 2026-03-11)

### 2.3 CrewAI

**Connection model:** Tool-centric. Agents are initialized with a list of `BaseTool` instances. Pre-built integrations include ComposioTool (which itself wraps hundreds of APIs) and LlamaIndexTool. Custom tools via `@tool` decorator or subclassing `BaseTool`.

**MCP support:** No native MCP support documented as of March 2026. Integration path: wrap a Substrate REST API call as a CrewAI tool. Less elegant than MCP-native, but works.

**Authentication:** Per-tool (API keys in tool constructor). No unified auth model.

**Substrate integration path:** Short-term: REST API wrapper tool. Medium-term: CrewAI will likely add MCP support as ecosystem pressure grows.

**Source:** docs.crewai.com/concepts/tools (accessed 2026-03-11)

### 2.4 AutoGen / AG2 (Microsoft)

**Connection model:** Tool registration via decorator or explicit registration on agent objects. Agents are instantiated with capability declarations; tools become part of their available action set. Python function introspection for schema generation, same pattern as OpenAI.

**MCP support:** Not found as native feature in documentation accessed. Integration via tool wrapping.

**Authentication:** Per-tool or environment-based.

**Substrate integration path:** REST API wrapper or, if AG2 adds MCP, native MCP connection.

**Source:** microsoft.github.io/autogen (accessed 2026-03-11, various pages)

### 2.5 Anthropic Tool Use (Claude direct API)

**Connection model:** Tools defined as JSON schema in the `tools` parameter of the Messages API. Claude returns `tool_use` content blocks when it wants to invoke a tool. Client executes the tool and returns a `tool_result` message. Loop continues until Claude produces a final text response.

This is NOT MCP — it's a lower-level primitive. MCP sits on top of this: an MCP client translates between the MCP tool definitions and Claude's tool use format.

**Key difference from MCP:** Stateless per API call. You pass the full tool list every call. MCP adds stateful sessions, capability negotiation, streaming notifications, and server-side lifecycle management.

**Authentication:** `x-api-key` header (Anthropic API key). No auth to external tools — that's the developer's responsibility.

**Source:** platform.claude.com/docs/en/docs/build-with-claude/tool-use/overview (accessed 2026-03-11)

### 2.6 LlamaIndex

**Connection model:** `FunctionTool` wraps any Python function. `QueryEngineTool` wraps a retrieval engine. `ToolSpec` bundles multiple tools for a single service (e.g., GmailToolSpec). Tools are passed to agent via list. `OnDemandLoaderTool` handles APIs that return large data volumes by indexing then querying.

**MCP support:** Compatible with MCP tool definitions; LlamaIndex tools share the same JSON schema pattern. No native MCP client documented.

**Authentication:** Per-tool via constructor parameters or environment.

**Substrate integration path:** FunctionTool wrapping Substrate REST endpoints, or via LangChain adapters if using a LangChain/LlamaIndex hybrid.

**Source:** developers.llamaindex.ai (accessed 2026-03-11)

### 2.7 Google Vertex AI Agent Engine

**Connection model:** Managed platform supporting LangChain, LangGraph, AG2, LlamaIndex as frameworks. Provides sessions, memory bank, code execution sandbox, observability (OpenTelemetry), and an example store.

**Protocol support:** Both MCP and A2A are explicitly listed as supported protocols. This is significant — Google's production agent platform supports both protocols.

**Authentication:** Google Cloud IAM. External APIs: service accounts, secrets manager.

**Substrate integration path:** Substrate deployed as an MCP server; Vertex agents connect via Streamable HTTP transport with GCP service account auth.

**Source:** docs.cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview (accessed 2026-03-11)

### 2.8 Amazon Bedrock Agents

**Connection model:** API-centric. Agents are configured with action groups (sets of API operations defined via OpenAPI schema). External services are invoked via Lambda functions or direct HTTPS. Agents automatically invoke the right API based on user intent.

**Protocol support:** No explicit MCP support documented. OpenAPI schema is the integration language. Lambda handles authentication via IAM roles.

**Authentication:** IAM roles, Secrets Manager for third-party API keys.

**Substrate integration path:** Define Substrate's REST API as a Bedrock action group using OpenAPI spec. Lambda proxy handles auth. More friction than MCP but achievable.

**Source:** aws.amazon.com/bedrock/agents (accessed 2026-03-11)

### 2.9 Microsoft Semantic Kernel

**Connection model:** Plugin-based. Plugins expose functions to the kernel; the kernel routes LLM tool calls to plugin functions. Native plugin types, HTTP connector plugins, OpenAPI plugins. Semantic Kernel is the foundation under Copilot and other Microsoft AI products.

**MCP support:** MCP connector package exists (found reference in documentation structure). Given Microsoft's deep AI investment and MCP's broad adoption, Semantic Kernel almost certainly has MCP support.

**Authentication:** Per-plugin. HTTP plugins use configurable auth headers.

**Substrate integration path:** Substrate as an MCP plugin, or HTTP plugin wrapping REST API.

**Source:** microsoft.github.io/semantic-kernel (accessed 2026-03-11)

---

## Part 3: OpenAI Function Calling vs. MCP

These are complementary, not competing:

| Dimension | OpenAI Function Calling | MCP |
|-----------|------------------------|-----|
| **What it is** | API-level primitive: tools defined per-request | Protocol: persistent server exposing tools, resources, prompts |
| **State** | Stateless per API call | Stateful sessions with lifecycle management |
| **Discovery** | Developer hardcodes tool list in every call | Client queries server's `tools/list` dynamically |
| **Transport** | Always HTTPS to OpenAI's API | stdio or Streamable HTTP |
| **Schema** | JSON Schema in API payload | JSON Schema in MCP primitives |
| **Scope** | One LLM call, one tool list | Multiple clients, multiple sessions, push notifications |
| **Auth to external services** | Developer's responsibility | OAuth specified at transport level |

OpenAI function calling IS how Claude, GPT-4o, and other models understand tool use at the LLM level. MCP is the ecosystem protocol that sits above it, providing server management, capability negotiation, and multi-client support. Every MCP client translates MCP tool definitions into the underlying model's function calling format.

**Source:** platform.claude.com/docs/en/docs/build-with-claude/tool-use/overview, openai.github.io/openai-agents-python (accessed 2026-03-11)

---

## Part 4: A2A (Agent-to-Agent) Protocol

### What It Is

A2A is an open protocol for agent-to-agent communication and task delegation. **MCP connects agents to tools and data. A2A connects agents to other agents.** These are complementary layers.

### Who Proposed It

Google launched A2A on **April 9, 2025**, with 50+ technology partners: Atlassian, Box, Cohere, Intuit, LangChain, MongoDB, PayPal, Salesforce, SAP, ServiceNow, and major consulting firms. Now under the **Linux Foundation** (as of v0.3.0, July 30, 2025).

### Technical Specification

**Transport:** JSON-RPC 2.0 over HTTP(S), with optional gRPC and HTTP/REST bindings.

**Interaction modalities:**
- Synchronous request/response
- Streaming via Server-Sent Events
- Asynchronous push notifications

**Discovery mechanism — Agent Cards:**
Each agent publishes an "Agent Card" (JSON) at a known endpoint describing:
- Identity (name, provider, version)
- Capabilities (what it can do)
- Security schemes (API key, OAuth 2.0, mutual TLS)
- Skills and supported operations
- Available protocol interfaces

Clients fetch the public card unauthenticated; extended cards (more details) require auth. Cards can be digitally signed.

**Authentication:**
- Client-to-server: credentials declared in Agent Card (API key, OAuth 2.0, mTLS)
- In-task authorization: agents can request additional credentials mid-task via `AUTH_REQUIRED` state

**Message format:**
```
Message:
  role: "user" | "agent"
  parts: [Part]  // text, file reference, structured data
  contextId: optional  // groups related messages across interactions
  taskId: optional  // references existing tasks
  metadata: {}  // extensible key-value pairs
```

**Status:** Version 0.3.0 released July 30, 2025. 22,400 GitHub stars. SDKs in Python, Go, JavaScript, Java, .NET. DeepLearning.AI course available. Production-ready.

**Source:** developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability, github.com/google/A2A, a2a-protocol.org/latest/specification (accessed 2026-03-11)

### A2A vs. MCP for Substrate

| | MCP | A2A |
|--|-----|-----|
| **Primary use** | Agent ↔ Tool/Service | Agent ↔ Agent |
| **Substrate role** | Substrate is the server; agents are clients | Substrate could be a peer agent |
| **Fits Substrate's model** | Perfectly — Substrate exposes awareness tools | Partially — relevant for multi-agent orchestration scenarios |

**Verdict:** Substrate should implement MCP first. A2A is relevant if Substrate ever needs to be discoverable as an autonomous agent in multi-agent systems (e.g., orchestrators delegating awareness queries to a Substrate agent). Not a V1 requirement.

---

## Part 5: How Agents Authenticate Today

Across all frameworks, authentication falls into these patterns:

| Method | Use Case | Who Uses It |
|--------|----------|-------------|
| **Environment variables** | API keys, secrets | Universal — all frameworks |
| **OAuth 2.1 / Bearer tokens** | User-delegated auth, MCP HTTP transport | MCP spec (required), OpenAI (optional) |
| **API key headers** | Direct service auth | Every REST integration |
| **IAM roles** | Cloud-native services | AWS Bedrock, GCP Vertex |
| **mTLS** | Enterprise / high-security | A2A enterprise flows |
| **HMAC tokens** | Service-to-service | Substrate's current model |

**Substrate's current model** (HMAC-SHA256 bearer tokens) maps cleanly to MCP's bearer token mechanism. Agents POST to register, get a token, include `Authorization: Bearer <token>` on every call. This is the right model.

**One gap:** Substrate does not currently implement OAuth 2.1. For the MCP HTTP transport spec compliance, this will eventually be needed. Short-term: bearer tokens are sufficient. Long-term: OAuth Client Credentials flow enables automatic agent registration without human involvement.

---

## Part 6: What a Substrate SDK Would Look Like

### The Minimum Integration Surface

Based on what every framework actually needs:

**Layer 1: REST API (already exists, partially)**
- `POST /api/agents/register` → returns token (exists)
- `GET /api/status` → awareness report (exists)
- `GET /api/query?process=X` → what-would-break query (exists)
- `GET /api/devices` → connected devices (exists)
- `GET /api/trust/{agent_id}` → trust score (not yet built)
- `POST /api/trust/report_incident` → report incident (not yet built)
- `GET /api/trust/credential` → issue W3C VC (not yet built)

**Layer 2: MCP Server (the integration multiplier)**

One MCP server exposes all REST functionality as MCP tools. Every framework with MCP support gets Substrate for free. This is the highest-leverage single build.

Tools to expose:
```
substrate_status()              → current awareness report
substrate_query(process: str)   → what-would-break analysis
substrate_devices()             → connected device list
substrate_get_trust(agent_id)   → trust score lookup
substrate_register()            → register calling agent (returns token)
```

Resources to expose:
```
substrate://processes           → live process list
substrate://devices             → connected devices
substrate://events              → recent event stream
```

**Layer 3: Framework-Specific Wrappers (community-driven)**
- `substrate-langchain` — thin wrapper calling MCP server
- `substrate-crewai` — tool definitions for CrewAI
- These should be community-contributed, not first-party

**Layer 4: A2A Agent Card (future)**
- Publish Substrate as an A2A-discoverable agent for multi-agent orchestration scenarios

### What the Developer Experience Looks Like

For an agent developer using any MCP-capable framework:

**Zero-code integration (via MCP):**
```json
// Add to claude_desktop_config.json or equivalent
{
  "mcpServers": {
    "substrate": {
      "command": "substrate-mcp",
      "args": ["--port", "8421"]
    }
  }
}
```

Done. The agent now has `substrate_status`, `substrate_query`, etc. as callable tools.

**Minimal code (via REST API):**
```python
import requests
# Register
token = requests.post("http://localhost:8421/api/agents/register",
    json={"agent_name": "my-agent", "version": "1.0", "author": "Acme", "capabilities": []}).json()["token"]
# Query
status = requests.get("http://localhost:8421/api/status",
    headers={"Authorization": f"Bearer {token}"}).json()
```

Two calls. No SDK needed.

---

## Battle-Tested Approaches

### MCP as Primary Integration Surface

- **What:** Implement Substrate as an MCP server (stdio + Streamable HTTP transports). Expose all awareness and trust capabilities as MCP tools and resources.
- **Evidence:** 18,419 servers on mcp.so, 22,100 stars on Python SDK, supported by Claude Desktop, VS Code, Cursor, OpenAI Agents SDK, LangChain, Google Vertex AI. The ecosystem is real and growing.
- **Source:** mcp.so, github.com/modelcontextprotocol/python-sdk, openai.github.io/openai-agents-python/mcp (accessed 2026-03-11)
- **Fits our case because:** Any agent using any MCP-capable client gets Substrate for free. One implementation, universal reach.
- **Tradeoffs:** MCP is still evolving (spec 2025-03-26, OAuth only recently fully specified). Some framework quirks exist. Not every framework is MCP-native yet (CrewAI, Bedrock require wrappers).

### REST API as Fallback Integration

- **What:** Keep the existing FastAPI REST API as the universal fallback. Every framework can wrap HTTP calls as tools.
- **Evidence:** Bedrock uses OpenAPI schemas; CrewAI uses custom tool wrappers; both reduce to HTTPS calls with JSON payloads.
- **Source:** aws.amazon.com/bedrock/agents, docs.crewai.com/concepts/tools (accessed 2026-03-11)
- **Fits our case because:** Zero framework dependency. Works with anything that can make HTTP calls.
- **Tradeoffs:** No push notifications, no capability negotiation, more boilerplate for integrators.

### Bearer Token Auth (Current Approach)

- **What:** Substrate issues HMAC-SHA256 bearer tokens at registration; agents include them as `Authorization: Bearer` headers.
- **Evidence:** This is exactly what MCP's Streamable HTTP transport requires for bearer token auth. The existing implementation is already spec-compliant for non-OAuth bearer auth.
- **Source:** modelcontextprotocol.io/specification/2025-03-26/basic/authorization (accessed 2026-03-11)
- **Fits our case because:** Already implemented. Agents can self-register without human involvement.
- **Tradeoffs:** Not full OAuth 2.1 compliance. For the MCP spec's stricter auth requirements in enterprise deployments, OAuth Client Credentials will eventually be needed.

---

## Novel Approaches

### Agent Card (A2A) for Substrate Discovery

- **What:** Publish Substrate as an A2A-discoverable agent with an Agent Card at a well-known URL. Enables orchestration frameworks to discover and delegate to Substrate as a peer agent.
- **Why it's interesting:** A2A has 22,400 GitHub stars, Linux Foundation governance, 50+ partners, v0.3.0 SDKs. It's becoming the standard for multi-agent coordination. Substrate-as-agent in multi-agent orchestration is a future product motion.
- **Evidence:** Google Vertex AI Agent Engine supports both MCP and A2A. The ecosystem is converging on both protocols as complementary layers.
- **Source:** a2a-protocol.org, github.com/google/A2A, docs.cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview (accessed 2026-03-11)
- **Fits our case because:** Enables Substrate to be discovered and invoked by orchestration systems without developer configuration.
- **Risks:** A2A adoption is still lower than MCP. Building A2A support before MCP would be premature.

### Substrate as an MCP Registry Entry

- **What:** Publish the Substrate MCP server in the official MCP Registry so developers can discover and install it the same way they discover other MCP servers.
- **Why it's interesting:** The registry is the emerging standard discovery mechanism. Being listed there means developer discovery without Substrate-specific marketing.
- **Evidence:** Official MCP Registry exists and is referenced in the Anthropic documentation. mcp.so lists 18,419 servers.
- **Source:** modelcontextprotocol.io/llms.txt, mcp.so (accessed 2026-03-11)
- **Fits our case because:** Passive distribution. Developers searching for "process awareness" or "agent trust" find Substrate.
- **Risks:** Registry is still maturing; discoverability depends on search quality and community size.

### Resource-Based Ambient Stream

- **What:** Expose Substrate's event bus as an MCP Resource with change notifications. Agents subscribe to `substrate://events` and receive real-time push notifications when process state changes, privacy mode toggles, etc.
- **Why it's interesting:** MCP supports `listChanged` notifications and resource subscriptions. This enables the "ambient stream" design (agents feel the ground without asking) using the MCP protocol natively.
- **Evidence:** MCP spec 2025-03-26 includes resource subscriptions and server-initiated notifications. The capability negotiation system makes this opt-in.
- **Source:** modelcontextprotocol.io/specification/2025-03-26/architecture (accessed 2026-03-11)
- **Fits our case because:** Exactly the "ambient stream vs deep queries" architectural distinction in Substrate's VISION.md. Agents subscribe once, get pushed awareness changes automatically.
- **Risks:** Requires Streamable HTTP transport (not stdio) for server-initiated messages. Adds complexity. Worth building after basic tool exposure works.

---

## Emerging Approaches

### MCP OAuth Dynamic Client Registration for Agent Self-Registration

- **What:** Implement OAuth 2.1 Dynamic Client Registration (RFC 7591) on the Substrate MCP server. Agents that connect automatically self-register without developer configuration.
- **Momentum:** MCP spec requires this for fully compliant HTTP transport servers. Anthropic's own recommendation in the spec is to implement it to "remove friction for users."
- **Source:** modelcontextprotocol.io/specification/2025-03-26/basic/authorization (accessed 2026-03-11)
- **Fits our case because:** Every agent that connects to Substrate's MCP server can automatically become a registered agent with a trust history. Zero-friction trust accumulation.
- **Maturity risk:** OAuth 2.1 is still a draft (draft-ietf-oauth-v2-1-12 as of spec reference). The spec is stable enough for implementation but formally still IETF draft status.

### Substrate-Verified Badge via MCP Tool

- **What:** Expose a `substrate_get_credential()` MCP tool that issues W3C VC trust credentials on-demand. Any agent connected via MCP can request its portable trust credential.
- **Momentum:** Trust credential issuance is a planned Substrate revenue stream (Trust Attestation Fees). MCP makes the credential issuance flow native to the connection model.
- **Source:** Substrate VISION.md, modelcontextprotocol.io/specification/2025-03-26 (accessed 2026-03-11)
- **Fits our case because:** Closes the loop: agent connects via MCP → accumulates trust history → requests W3C VC via MCP tool → carries credential to other platforms. The entire trust economy runs through MCP.
- **Maturity risk:** Depends on trust layer being built (MVTL — 5 sessions away). W3C VC 2.0 + SD-JWT format is solid (no maturity risk there).

---

## Gaps and Unknowns

1. **No universal discovery standard.** There is no authoritative, searchable registry that all agents check before connecting to services. MCP Registry and mcp.so are growing, but discovery is still largely manual configuration. **Impact for Substrate:** Distribution requires presence in multiple registries plus direct developer outreach. Cannot rely on passive discovery alone in 2026.

2. **MCP auth is only fully specified for HTTP transport.** stdio servers have no protocol-level auth — they rely on OS process isolation and environment variables. **Impact for Substrate:** The local daemon running via stdio has no token validation mechanism in the MCP layer. Substrate's own bearer token registry (already built) fills this gap correctly.

3. **CrewAI and Bedrock have no native MCP support.** Two significant platforms require REST API wrapper approach. **Impact for Substrate:** Need to maintain REST API as first-class interface, not just a backend for MCP.

4. **A2A adoption trajectory relative to MCP is unclear.** A2A has strong backing (Google, Linux Foundation, 50+ partners) but MCP has more client adoption today (18K+ servers, more framework integrations documented). **Impact for Substrate:** Implement MCP first, design the architecture so A2A can be layered on later.

5. **MCP capability negotiation doesn't include trust signals.** When a client connects to an MCP server, there is no protocol mechanism to declare "this client has trust score X." The trust layer is an application concern, not a protocol concern. **Impact for Substrate:** Trust score lookup via `substrate_get_trust()` tool is the right model — query Substrate, don't embed trust in protocol headers.

6. **No tested "Substrate SDK" pattern to copy.** Nothing quite like Substrate (local awareness daemon + trust scoring + MCP server) exists to benchmark against. The closest things are Runlayer (MCP security gateway, $11M, no OS context) and HUMAN Security AgenticTrust (web-layer only). This is genuinely novel territory.

---

## Synthesis

### The Integration Surface Hierarchy (What to Build First)

```
Priority 1: MCP Server (stdio + Streamable HTTP)
  → Reaches: Claude Desktop, VS Code, Cursor, OpenAI Agents SDK, LangGraph, Vertex AI
  → Tools: status, query, devices, register, get_trust (future)
  → Resources: substrate://events (ambient stream, future)
  → Auth: bearer token now, OAuth Client Credentials later

Priority 2: REST API (maintain and expand)
  → Reaches: CrewAI, Bedrock, any HTTP client
  → Already built; add trust endpoints as trust layer is wired

Priority 3: MCP Registry listing
  → Passive discovery; list when MCP server is stable

Priority 4: A2A Agent Card
  → When multi-agent orchestration becomes relevant
  → Probably post-MVTL

Priority 5: Framework-specific SDKs
  → Community-driven; don't build these first-party
```

### What the Minimum Integration Surface Actually Is

The question was: "one function call? An MCP server? A REST API? All of the above?"

**Answer: MCP server is the answer. REST API is the fallback. Not all of the above simultaneously — prioritize MCP.**

Here's why: Every framework that matters either (a) already supports MCP natively or (b) can wrap MCP tools as their own tool type via adapters that already exist. Building the MCP server covers 80%+ of the addressable framework surface. The REST API covers the remaining 20% (Bedrock, CrewAI) without requiring separate maintenance of a "Substrate SDK."

The single highest-leverage thing Substrate can build for agent integration is: **an MCP server that exposes all awareness and trust primitives as tools and resources, reachable via both stdio (local) and Streamable HTTP (network).**

### Compatibility Verdict: Substrate's Existing Code

The current `AgentRegistry` and bearer token model are well-designed for the agent integration surface:
- HMAC-SHA256 bearer tokens map directly to MCP's `Authorization: Bearer` mechanism
- The registration endpoint (`POST /api/agents/register`) is exactly the agent self-registration pattern that MCP's OAuth dynamic client registration formalizes
- The `record_query()` method is the right hook for trust accumulation triggered by MCP tool calls

The main gaps vs. production-ready MCP server:
- No MCP protocol layer on top of the FastAPI server (biggest gap — needs an MCP server wrapper)
- No OAuth 2.1 (nice to have for HTTP transport; not blocking)
- No resource subscriptions / push notifications (needed for ambient stream, not V1)
- Trust endpoints don't exist yet (depends on MVTL work)

The existing code is a solid foundation. The MCP server is the next layer to build on top of it.
