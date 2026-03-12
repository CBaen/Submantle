# Team 1 Findings: Agent Transport & Routing Architecture
## Date: 2026-03-10
## Researcher: Team Member 1

---

## Research Question
How does Submantle become the layer that AI agents literally travel through? What does "transport layer for AI" mean technically — and is there a real analogy to MQTT, Twilio, and Stripe becoming infrastructure?

---

### Battle-Tested Approaches

---

**1. MCP as the Universal Agent Integration Surface — Now with Stateless Transport Evolution**

- **What:** Model Context Protocol (JSON-RPC 2.0 over Streamable HTTP or stdio) is the dominant standard for connecting agents to tools and data. As of March 2026, it has 97M+ monthly SDK downloads, 16,000+ MCP servers created in 2025 alone, and is adopted by Anthropic, OpenAI, Google, Microsoft, and the Linux Foundation (via the Agentic AI Foundation, Dec 2025). Spec version 2025-11-25 is current.
- **Evidence:** Anthropic donated MCP to the Linux Foundation's Agentic AI Foundation in December 2025. OpenAI officially adopted MCP in March 2025. MCP Dev Summit North America 2026 (April 2-3, NYC) has 95+ sessions from maintainers and production deployers. Source: [Linux Foundation AAIF announcement](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation), [MCP Dev Summit 2026](https://events.linuxfoundation.org/2026/02/24/agentic-ai-foundation-unveils-mcp-dev-summit-north-america-2026-schedule/), [MCP Wikipedia](https://en.wikipedia.org/wiki/Model_Context_Protocol). Date accessed: March 2026.
- **Fits our case because:** Submantle-as-MCP-server is the lowest-friction path to being queryable by every agent framework. But the more consequential insight is the transport evolution: the MCP roadmap (updated March 5, 2026) explicitly prioritizes stateless Streamable HTTP, `/.well-known/mcp.json` Server Cards for capability discovery, and well-defined gateway/proxy behavior as priority areas. This means the protocol is actively building toward being proxy-able — which is exactly what Submantle needs to intercept traffic at scale.
- **Tradeoffs:** MCP does not enforce pre-action checks — agents voluntarily query Submantle. The protocol is evolving fast (June 2026 spec release expected), meaning Submantle must track spec changes. 30+ CVEs documented in MCP implementations through 2025 indicate security immaturity.
- **Source:** [MCP Roadmap (March 5, 2026)](https://modelcontextprotocol.io/development/roadmap), [MCP Transport Future post (Dec 2025)](http://blog.modelcontextprotocol.io/posts/2025-12-19-mcp-transport-future/)

---

**2. The MCP Proxy/Gateway Pattern — Interception Is Now an Established Market**

- **What:** MCP proxy products — agentgateway (Linux Foundation, Solo.io, built in Rust), Lasso MCP Gateway (open source, April 2025), Gravitee Agent Gateway, Microsoft MCP Gateway (Kubernetes reverse proxy), Kong Context Mesh (Feb 2026) — sit between agent clients and MCP servers, intercepting ALL tool calls at the protocol level. The pattern is now a market category, not a concept.
- **Evidence:** agentgateway was accepted into the Linux Foundation in August 2025. Contributing companies include Solo.io, Microsoft, Apple, Alibaba, Adobe, AWS, Cisco, Salesforce. Lasso MCP Gateway is open source on GitHub. Microsoft published mcp-gateway for Kubernetes (session-aware stateful routing). Runlayer raised $11M seed from Khosla Ventures (Nov 2025), signed 8 unicorn customers in 4 months. Kong launched Context Mesh on Feb 10, 2026. Sources: [Linux Foundation agentgateway](https://www.linuxfoundation.org/press/linux-foundation-welcomes-agentgateway-project-to-accelerate-ai-agent-adoption-while-maintaining-security-observability-and-governance), [Runlayer TechCrunch](https://techcrunch.com/2025/11/17/mcp-ai-agent-security-startup-runlayer-launches-with-8-unicorns-11m-from-khoslas-keith-rabois-and-felicis/), [Kong Context Mesh](https://konghq.com/company/press-room/press-release/kong-launches-context-mesh-to-connect-enterprise-data-to-ai-agents). Date accessed: March 2026.
- **Fits our case because:** This validates that "Submantle as MCP proxy" is technically sound and commercially real. The gap: every existing proxy does security enforcement, access control, and logging — but none enriches the context with OS-level process awareness. Runlayer sees "what tool was called." Submantle would add "and here's what the machine is actually doing right now, and here's what you'd break." That is the differentiator — not the proxy itself, but the knowledge graph it consults.
- **Tradeoffs:** Only catches MCP-compliant agents. Agents using direct subprocess calls, raw OS APIs, or non-MCP tool invocations bypass this layer entirely. Proxy adds latency to every call. Requires deployment as MCP router — an ops challenge at the individual device level.

---

**3. Dapr Agents — The Event-Driven Message Bus Model for Agent-to-Agent at Scale**

- **What:** Dapr (Distributed Application Runtime, CNCF project) announced Dapr Agents in March 2025. It uses pub/sub messaging as the backbone for multi-agent coordination, supporting thousands of agents on a single core with transparent horizontal scaling. Agents communicate through Dapr's event broker; coordination models include LLM-based decision-making, random selection, and round-robin.
- **Evidence:** [Dapr Agents announcement (CNCF, March 2025)](https://www.cncf.io/blog/2025/03/12/announcing-dapr-ai-agents/), [InfoQ coverage](https://www.infoq.com/news/2025/03/dapr-agents/), [Dapr docs](https://docs.dapr.io/developing-ai/dapr-agents/). Date accessed: March 2026.
- **Fits our case because:** Dapr's pub/sub model demonstrates how a message bus becomes the routing backbone for millions of agents. It also demonstrates the value of "state management" baked into the infrastructure layer — analogous to Submantle's knowledge graph. Submantle could publish awareness events (process state changes, device joins, anomaly detection) to a Dapr-compatible pub/sub channel, and agents subscribe.
- **Tradeoffs:** Dapr is Python-first (Go support TBD). Adding a Dapr dependency adds significant complexity for a single-device prototype. This is an enterprise pattern, not a solo-bootstrappable starting point.

---

**4. Solace Agent Mesh — The Event-Driven Agent Fabric Pattern**

- **What:** Solace Agent Mesh (SAM), released GA in December 2025, is an event-driven agentic AI framework built on Solace Event Broker. It routes messages between agents dynamically using intelligent orchestration, supports A2A protocol for inter-agent delegation, and provides enterprise-grade security and horizontal scaling.
- **Evidence:** [Solace Agent Mesh Enterprise GA (Dec 2025)](https://www.prnewswire.com/news-releases/solace-signals-the-future-of-real-time-agentic-ai-with-introduction-of-solace-agent-mesh-enterprise-302628418.html), [Solace docs](https://docs.solace.com/Agentic-AI/agent-mesh.htm), [IntellyX analysis](https://intellyx.com/2025/07/23/solace-agent-mesh-for-agentic-ai-orchestration/). Date accessed: March 2026.
- **Fits our case because:** The "event mesh as neural network" metaphor exactly matches the Submantle vision: "decoupling senders from receivers, messages flow naturally between agents, gateways, and external systems." Submantle's awareness events (battery low, process anomaly, unsaved work detected) fit naturally into this pub/sub topology as event producers. Agents subscribe to the context streams they care about.
- **Tradeoffs:** Solace is enterprise infrastructure. Not bootstrappable for a solo creator. Demonstrates the pattern; doesn't provide the path.

---

**5. MQTT's Playbook — The Canonical Case for Internal Tool to Open Standard to Infrastructure**

- **What:** MQTT was created in 1999 by Andy Stanford-Clark (IBM) and Arlen Nipper for monitoring oil pipelines via satellite. IBM used it internally for 11 years. In 2010, IBM released it as royalty-free. In 2011, IBM simultaneously submitted it to OASIS and launched Eclipse Paho (open-source reference implementation). OASIS published MQTT 3.1.1 in 2014. By 2017, MQTT overtook HTTP as the leading IoT protocol.
- **Evidence:** [IBM MQTT blog](https://developer.ibm.com/blogs/open-source-ibm-mqtt-the-messaging-protocol-for-iot/), [OASIS announcement](https://www.oasis-open.org/2014/11/13/foundational-iot-messaging-protocol-mqtt-becomes-international-oasis-standard/), [History of MQTT (HiveMQ)](https://www.hivemq.com/blog/the-history-of-mqtt-part-1-the-origin/), [MQTT Wikipedia](https://en.wikipedia.org/wiki/MQTT). Date accessed: March 2026.
- **Fits our case because:** The MQTT playbook is: (1) solve a real problem internally, (2) open-source the reference implementation, (3) donate to a neutral standards body, (4) ecosystem grows because no one owns it. MCP followed this exact playbook — Anthropic built it internally, open-sourced it, donated to Linux Foundation/AAIF. Submantle should follow the same pattern: solve process-aware context brokering, open-source the daemon, contribute Submantle's broker protocol to AAIF or IETF. The protocol layer becomes free; the commercial layer is the store, the cloud sync, the enterprise deployment.
- **Tradeoffs:** MQTT took 15+ years from invention to dominance. MCP moved faster because it was born into an ecosystem hungry for standards. Submantle is entering at a moment when standards are being written — but that also means the window to shape them is finite.

---

### Novel Approaches

---

**1. The "Submantle as Context Enrichment Proxy" — The Missing Differentiation in the Existing Market**

- **What:** Every existing MCP gateway does policy enforcement (what is this agent allowed to do?) and logging (what did it do?). None does context enrichment (here's what the machine is actually doing, and what this action would break). The architectural pattern is: Submantle sits in the proxy layer but enriches every intercepted call with its knowledge graph before allowing or flagging it.
- **Why it's interesting:** This is not a new architectural pattern (it's how WAFs work — intercept, analyze, enrich, decide) but it's genuinely novel at the MCP protocol level. Existing gateways treat tool calls as abstract JSON. Submantle would translate them into "kill all node processes on a machine where 8 node processes are part of a 2-hour Stable Diffusion pipeline." The context is the product.
- **Evidence:** Gartner's January 2026 report "How to Enable Agentic AI via API-based Integration" identified "context mesh" — real-time context delivery to agents — as the critical missing layer. Kong launched Context Mesh (Feb 10, 2026) to address this from the API/enterprise data side. But Kong's context comes from enterprise APIs. Submantle's context comes from the OS. That's a different layer — and currently unoccupied. Source: [Kong Context Mesh blog](https://konghq.com/blog/enterprise/gartners-context-mesh), [Kong press release](https://konghq.com/company/press-room/press-release/kong-launches-context-mesh-to-connect-enterprise-data-to-ai-agents). Date accessed: March 2026.
- **Fits our case because:** Submantle's three-tier architecture (MCP server → MCP proxy → OS-level guardian) is not just an integration path — it's a progression toward being the enrichment layer that sits below Kong, Runlayer, and agentgateway. Those products need context from somewhere. Submantle provides OS-level context that none of them can see.
- **Risks:** Submantle's process-awareness knowledge graph must actually be built and populated before the enrichment layer has anything meaningful to contribute. The knowledge graph is the prerequisite for everything else. Without it, Submantle is just another proxy.

---

**2. The Agent Discovery Gap — "DNS for Agents" Is Actively Being Built, Submantle Could Be a Node**

- **What:** A2A's Agent Cards establish a standard for agent self-description at `/.well-known/agent-card.json`. But dynamic discovery — finding the right agent for a task without knowing its address — remains unsolved. Solo.io documented the three missing components: Agent Registry, Agent Naming Service (ANS), and Agent Gateway. IETF published draft-pioli-agent-discovery-01 (ARDP). Microsoft launched Entra Agent Registry. Kong launched MCP Registry (Feb 2026).
- **Why it's interesting:** Submantle is already a "thing" that every agent would want to find. If Submantle registers in agent discovery infrastructure (ARDP, Entra, Kong's registry) as a "context provider for this device/mesh," it becomes a discoverable node in the agent graph. Any agent that queries "what context sources are available for this machine?" gets Submantle. This is passive growth — Submantle doesn't need to push; agents pull.
- **Evidence:** [Solo.io agent discovery blog](https://www.solo.io/blog/agent-discovery-naming-and-resolution---the-missing-pieces-to-a2a), [IETF ARDP draft](https://www.ietf.org/ietf-ftp/internet-drafts/draft-pioli-agent-discovery-01.html), [Kong MCP Registry](https://www.prnewswire.com/news-releases/kong-introduces-mcp-registry-in-kong-konnect-to-power-ai-connectivity-for-agent-discovery-and-governance-302676451.html), [Microsoft Entra Agent Registry](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/publish-agents-to-registry). Date accessed: March 2026.
- **Fits our case because:** Submantle publishes a `/.well-known/substrate-card.json` describing its capabilities (process awareness, device mesh, anomaly detection). Discovery registries index this. Agents searching for "OS context" find Submantle automatically. This is how a service becomes infrastructure — not by pushing into every stack, but by being findable and standard-compliant.
- **Risks:** Discovery infrastructure is fragmented across ARDP, Entra, Kong, and others. No clear winner yet. Registering in all of them is feasible but requires tracking a moving target.

---

**3. Agent Network Protocol (ANP) — The Decentralized Internet-Scale Agent Routing Vision**

- **What:** ANP is an open-source protocol (inspired by W3C DID, DNS, and P2P) that positions itself as "the HTTP of the agentic web." Three-layer architecture: identity (DID-based), meta-protocol (capability negotiation), and application (JSON-LD agent descriptions). Agents have their own digital identities and can be discovered across the public internet without central registries.
- **Why it's interesting:** If ANP achieves internet-scale adoption, Submantle doesn't need to integrate with any specific platform. It registers as an ANP node, and every ANP-capable agent can discover and query it. This is the most infrastructure-like path — Submantle becomes like a web server: discoverable to anyone, by standard protocol.
- **Evidence:** [ANP GitHub](https://github.com/agent-network-protocol/AgentNetworkProtocol), [ANP homepage](https://agentnetworkprotocol.com/en/), [Agentic AI protocols comparison](https://k21academy.com/agentic-ai/agentic-ai-protocols-comparison/). Date accessed: March 2026.
- **Fits our case because:** ANP's DID-based identity model aligns with the "agent passport" pattern. If Submantle devices have DID identities, agents can find them without any central registry. This matters at the hundreds-of-millions-of-devices scale.
- **Risks:** ANP is the least adopted of the major protocols (MCP >> A2A >> ACP > ANP by current adoption). The DID-based approach has high implementation complexity. This is a long-horizon bet, not a near-term integration path.

---

### Emerging Approaches

---

**1. The Agent Mesh / Agentic AI Mesh — A New Infrastructure Layer Being Named and Claimed**

- **What:** "Agent mesh" is an emerging architectural pattern (named by Solo.io, ema.ai, Gartner, and others) describing a runtime layer that handles agent discovery, secure communication, semantic routing, observability, and policy enforcement across heterogeneous agent systems. The mesh sits above API gateways and event buses as an "intelligent overlay." By 2027, over 50% of enterprise AI agents are predicted to rely on standardized frameworks like MCP or A2A for cross-system interoperability.
- **Momentum:** Solo.io published the agent mesh concept and launched agentgateway (Linux Foundation, August 2025). McKinsey/QuantumBlack deployed it at enterprise scale. The MCP developer community created over 16,000 MCP servers in 2025 alone. Gartner's 40% enterprise agent penetration prediction (August 2025) is forcing infrastructure vendors to respond. Sources: [Solo.io agent mesh blog](https://www.solo.io/blog/agent-mesh-for-enterprise-agents), [agentgateway.dev](https://agentgateway.dev/), [Gartner prediction](https://www.gartner.com/en/newsroom/press-releases/2025-08-26-gartner-predicts-40-percent-of-enterprise-apps-will-feature-task-specific-ai-agents-by-2026-up-from-less-than-5-percent-in-2025). Date accessed: March 2026.
- **Fits our case because:** "Agent mesh" is exactly what Submantle-at-scale would be called. Submantle's process awareness and knowledge graph would function as the data plane of a device-centric agent mesh. The pattern is being established now; Submantle can name itself as an agent mesh node rather than inventing new vocabulary. This lowers the explanation burden with enterprise buyers.
- **Maturity risk:** The agent mesh pattern is being defined by infrastructure vendors who have existing businesses (Solo.io, Kong, Solace). Submantle's differentiation must be that it provides OS-level context that cloud-first vendors cannot — not that it does everything the mesh does.

---

**2. MCP Stateless Transport + Server Cards — The Infrastructure-Grade Evolution Arriving June 2026**

- **What:** The MCP roadmap (updated March 5, 2026) targets Q1 2026 finalization of Spec Enhancement Proposals for a June 2026 spec release that makes Streamable HTTP stateless across server instances, defines proper session semantics, and introduces `/.well-known/mcp.json` Server Cards for pre-connection capability discovery. Routing metadata will be exposed via HTTP headers (not buried in JSON payloads), enabling standard load balancers and proxies to route without payload parsing.
- **Momentum:** This is priority area #1 in the current MCP roadmap with a named Transports Working Group. The June 2026 release is the target. Source: [MCP Roadmap March 5, 2026](https://modelcontextprotocol.io/development/roadmap), [MCP Transport Future (Dec 2025)](http://blog.modelcontextprotocol.io/posts/2025-12-19-mcp-transport-future/). Date accessed: March 2026.
- **Fits our case because:** Stateless MCP transport means Submantle can deploy as a horizontal MCP proxy at scale without sticky session routing hacks. Server Cards enable auto-discovery of Submantle's capabilities before any connection is established. Routing metadata in HTTP headers means Submantle can route without deep packet inspection. These are the protocol-level features that make Submantle-as-infrastructure operationally feasible.
- **Maturity risk:** This is a roadmap item, not a shipped spec. June 2026 is 3 months away and subject to slippage. Submantle should prototype against the current spec and prepare for the June update.

---

**3. MCP Agent Communication Extension (Tasks Primitive, SEP-1686) — The Async Agent-to-Agent Layer**

- **What:** SEP-1686 added a Tasks primitive to MCP, enabling a "call now / fetch later" pattern for long-running agent work. The MCP roadmap's Agent Communication priority area is focused on hardening Tasks with retry semantics and expiry policies for production deployments. The roadmap explicitly envisions MCP servers acting as agents that communicate with other MCP servers (a "Travel Agent" server negotiating with a "Booking Agent" server).
- **Momentum:** Listed as priority area #2 in MCP roadmap (March 2026). Named Agents Working Group. Production deployments are already surfacing gaps. Source: [MCP Roadmap](https://modelcontextprotocol.io/development/roadmap). Date accessed: March 2026.
- **Fits our case because:** The Tasks primitive is the first step toward "agents travel through MCP." When Submantle is an MCP server that receives a task ("I'm about to kill all Node processes — what would I break?"), it can respond asynchronously with full process graph context. The Agents WG's work on retry and expiry directly affects Submantle's reliability as a context broker.
- **Maturity risk:** Retry and expiry semantics are not yet defined. Production deployments will experience failures before the spec hardens. Submantle should implement graceful degradation — never block an agent, only enrich or warn.

---

**4. NATS — The Sub-Millisecond Pub/Sub Backbone That Could Underpin Submantle's Awareness Mesh**

- **What:** NATS is a lightweight, high-performance pub/sub messaging system. In 2026 benchmarks, it achieves 15M+ operations/second with sub-100µs latency. It is emerging as the preferred message broker for AI agent systems due to lower overhead than Kafka and simpler operational model.
- **Momentum:** Appearing in 2026 AI infrastructure comparisons as the recommendation for "lightweight, quantum-safe, and protocol-flexible environments, especially in AI agent systems." Source: [Message Brokers for AI 2026](https://dasroot.net/posts/2026/03/message-brokers-ai-kafka-nats-rabbitmq/). Date accessed: March 2026.
- **Fits our case because:** Submantle's awareness mesh (cross-device state sharing, event-driven updates from OS event streams) needs a pub/sub backbone. NATS is a realistic candidate for the inter-Submantle communication layer — lightweight enough to run on embedded devices, fast enough for real-time awareness updates. Submantle instances on different devices could publish events to a NATS topic; agents subscribe.
- **Maturity risk:** Adds a dependency. For the prototype, NATS is overkill — gRPC or SQLite replication suffices. For the production mesh at hundreds of millions of devices, NATS or a similar system is necessary but architecturally foreign to the current prototype.

---

### Gaps and Unknowns

---

**1. "Agents travel through Submantle" vs "Agents query Submantle" is a different architectural commitment.**

The current vision ("Ask Submantle") positions Submantle as a service agents call. "Agents travel through Submantle" means Submantle is in the critical path of every agent action — a proxy. These are very different failure mode profiles. A query service can be unavailable and agents degrade gracefully. A proxy that is unavailable breaks every agent workflow. The research found no existing product that has navigated this transition from advisory layer to mandatory transport without enterprise mandates forcing it. How does Submantle move from optional to required without platform authority?

**2. The "context enrichment" differentiation is unproven at real scale.**

The research confirms that no existing proxy enriches with OS process context. But it did not find evidence that enterprises actually want OS-level context in their agent proxy layer. Runlayer, Kong, and agentgateway are all selling security enforcement and observability — not process enrichment. The question is whether "what would this action break at the OS level" is a buying criterion or a nice-to-have. This needs primary research with agent framework developers and enterprise buyers.

**3. Agent-to-agent routing at millions-of-agents scale has no proven architecture yet.**

A2A, ACP, ANP, and ARDP all address agent discovery and communication. None of them has been deployed at hundreds-of-millions-of-agents scale as of March 2026. Gartner's 40% enterprise agent penetration by 2026 is from a standing start — the scaling problems have not been hit yet. The architecture Submantle would need to handle this (distributed hash tables? federated registries? hierarchical mesh?) is still theoretical.

**4. The five protocol landscape (MCP, A2A, ACP, ANP, AP2) creates a fragmentation risk.**

A Stream blog from January 2026 confirmed five competing protocols with no clear dominant winner for agent-to-agent communication. MCP dominates agent-to-tool. A2A is gaining enterprise adoption for agent-to-agent. ACP (IBM BeeAI) offers a simpler REST alternative. ANP targets internet-scale decentralization. Submantle would need to support all of them to be universal infrastructure, or bet on one and risk missing a significant portion of the ecosystem.

**5. The bootstrap question: how does an individual-device proxy become a multi-device mesh without centralized infrastructure?**

Every "agent mesh" product found in the research (Solace, Dapr, agentgateway) assumes centralized infrastructure — a cloud relay, a Kubernetes cluster, a broker. Submantle's privacy-by-architecture commitment (on-device, E2E encrypted sync) and bootstrappability constraint (no VC to begin) create tension with the hub-and-spoke topologies that make mesh routing work. The research found no product that runs a true peer-to-peer agent mesh at scale without some central coordination point. Tailscale is the closest (P2P wireguard with DERP relay fallback) but it's a networking layer, not an agent routing layer.

**6. Submantle's position relative to existing gateways is complementary, not competitive — but this needs explicit positioning.**

agentgateway, Kong Context Mesh, and Runlayer are potential partners (Submantle provides the OS context layer they query) or potential competitors (they could add OS context gathering to their products). The research did not find evidence of OS-level process awareness in any of these products, but it is a logical addition. The window to establish Submantle as the canonical OS context source is open but not permanently open.

---

### Synthesis

**What "agents travel through Submantle" actually means architecturally:**

The phrase conflates two different things. Separating them is essential:

1. **Agents query Submantle for context** — Submantle is a service. Agents call it before acting. This is the current vision. Already implementable via MCP server. Low friction. Not "transport."

2. **Agent traffic routes through Submantle** — Submantle is a proxy. Every MCP call passes through Submantle before reaching its destination. Submantle sees intent, enriches with context, allows or flags. This is "transport." It requires Submantle to be in the critical path of every agent action on the device. Operationally feasible at the device level (configure Submantle as the local MCP proxy). Hard to enforce without platform authority.

Only the second interpretation makes Submantle "the layer agents travel through." And the research confirms: this is a real architectural pattern (MCP proxy / agent gateway) with real products already doing it (agentgateway, Runlayer, Lasso). The gap is that none of them knows what's actually running on the machine. Submantle does.

**The strongest analogy is not MQTT, Twilio, or Stripe — it's Nginx.**

Nginx started as a web server, became a reverse proxy, became load balancer infrastructure, became the default entry point for virtually every web application. It did this by: (1) being genuinely better than the alternative at one thing, (2) being open source, (3) adding features that made it the natural extension point for the problems operators already had. Submantle's path is analogous: start as the authoritative process awareness source (the thing Submantle is uniquely positioned to do), deploy as an MCP server, evolve into the proxy that enriches all MCP traffic with its context, become the entry point that everything passes through because it's where the context lives.

**The MQTT/Twilio/Stripe pattern does apply — but to the commercial layer, not the protocol layer.**

MQTT became infrastructure when IBM open-sourced it and donated it to OASIS. Twilio became infrastructure when it abstracted telecom complexity into an API that developers could use without understanding carrier networks. Stripe became infrastructure when it handled compliance (PCI-DSS, fraud, identity verification) so that no one building a payment flow had to. The pattern is: take a domain that is complex, fragmented, and legally/technically risky — and make it simple for developers. For AI agents in 2026, that domain is "what is actually happening on the device I'm about to act on?" Submantle simplifies that.

**Recommended transport architecture — three concrete layers:**

**Layer 0 — Submantle as MCP Server (ship now, prototype already provides this via FastAPI):**
Expose process awareness, device state, anomaly detection as MCP tools. Any MCP-compatible agent can query. Publish `/.well-known/mcp.json` Server Card for auto-discovery. Implement A2A agent card for agent-to-agent protocols. Implement ARDP registration for discovery infrastructure. This is not transport — it's presence. But presence is the prerequisite.

**Layer 1 — Submantle as Local MCP Proxy (V2, post Go-rewrite):**
Submantle runs as the local MCP gateway. Agent framework configurations point to `localhost:SUBSTRATE_PORT` as their MCP router. Submantle intercepts, enriches with process context, forwards to destination servers. Implements the MCP gateway/proxy patterns being standardized in the June 2026 spec. This is "agents travel through Submantle" — on a single device. Operationally: configure once, invisible thereafter. This is how Nginx became default entry point: it was the thing you put in your config once.

**Layer 2 — Submantle Awareness Mesh as Event Bus (V3, multi-device):**
Submantle instances on different devices form an awareness mesh. OS events (ETW, mDNS, eBPF) are published as a shared event stream. Other Submantles and agents subscribe to relevant streams. Message transport: NATS or similar for low-latency pub/sub. E2E encrypted, peer-to-peer where possible (Tailscale model), with relay fallback. This is where "hundreds of millions of devices" becomes meaningful — not as a monolith but as a federated mesh of local substrates.

**The go/no-go answer for this angle: GO — with caveats.**

The transport architecture is real, buildable incrementally, and unoccupied at the specific layer Submantle targets. The MCP proxy pattern is validated by $11M+ in funding for products that do it without process context. The agent mesh pattern is being named and claimed by major vendors — Submantle can name itself as a node in that mesh. The protocol landscape (MCP as the dominant standard, A2A growing, June 2026 spec hardening the proxy/gateway patterns) is moving in Submantle's favor.

The caveats: (1) The knowledge graph must be built before the enrichment layer matters. (2) "Agents travel through Submantle" requires Submantle to be in the critical path — a hard requirement that only comes through developer adoption and eventual platform-level configuration. (3) The bootstrap from single-device to mesh is the hardest architectural problem and remains unsolved by anyone at scale with privacy constraints. (4) The window to shape the standards (AAIF, IETF, ARDP) is open now — a working Submantle reference implementation could influence what gets standardized.

---

### Sources (all accessed March 2026)

- [MCP Official Roadmap (March 5, 2026)](https://modelcontextprotocol.io/development/roadmap)
- [MCP Transport Future Blog Post (Dec 2025)](http://blog.modelcontextprotocol.io/posts/2025-12-19-mcp-transport-future/)
- [MCP Wikipedia](https://en.wikipedia.org/wiki/Model_Context_Protocol)
- [Linux Foundation AAIF Announcement](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation)
- [MCP Dev Summit North America 2026](https://events.linuxfoundation.org/2026/02/24/agentic-ai-foundation-unveils-mcp-dev-summit-north-america-2026-schedule/)
- [agentgateway.dev](https://agentgateway.dev/)
- [agentgateway GitHub (Linux Foundation)](https://github.com/agentgateway/agentgateway)
- [Linux Foundation welcomes agentgateway](https://www.linuxfoundation.org/press/linux-foundation-welcomes-agentgateway-project-to-accelerate-ai-agent-adoption-while-maintaining-security-observability-and-governance)
- [Solo.io Agent Mesh blog](https://www.solo.io/blog/agent-mesh-for-enterprise-agents)
- [Solo.io Agent Discovery: Missing Pieces for A2A](https://www.solo.io/blog/agent-discovery-naming-and-resolution---the-missing-pieces-to-a2a)
- [Runlayer TechCrunch (Nov 2025)](https://techcrunch.com/2025/11/17/mcp-ai-agent-security-startup-runlayer-launches-with-8-unicorns-11m-from-khoslas-keith-rabois-and-felicis/)
- [Microsoft MCP Gateway (GitHub)](https://github.com/microsoft/mcp-gateway)
- [Kong Context Mesh press release (Feb 2026)](https://konghq.com/company/press-room/press-release/kong-launches-context-mesh-to-connect-enterprise-data-to-ai-agents)
- [Kong Context Mesh blog — Gartner angle](https://konghq.com/blog/enterprise/gartners-context-mesh)
- [Gartner 40% enterprise agent prediction (Aug 2025)](https://www.gartner.com/en/newsroom/press-releases/2025-08-26-gartner-predicts-40-percent-of-enterprise-apps-will-feature-task-specific-ai-agents-by-2026-up-from-less-than-5-percent-in-2025)
- [Gravitee MCP Proxy blog](https://www.gravitee.io/blog/mcp-proxy-unified-governance-for-agents-tools)
- [Top AI Agent Protocols 2026 (Stream)](https://getstream.io/blog/ai-agent-protocols/)
- [A2A IBM overview](https://www.ibm.com/think/topics/agent2agent-protocol)
- [A2A Protocol](https://a2aprotocol.ai/)
- [MQTT Wikipedia](https://en.wikipedia.org/wiki/MQTT)
- [IBM MQTT blog](https://developer.ibm.com/blogs/open-source-ibm-mqtt-the-messaging-protocol-for-iot/)
- [OASIS MQTT standard announcement](https://www.oasis-open.org/2014/11/13/foundational-iot-messaging-protocol-mqtt-becomes-international-oasis-standard/)
- [HiveMQ MQTT History Part 1](https://www.hivemq.com/blog/the-history-of-mqtt-part-1-the-origin/)
- [HiveMQ MQTT History Part 2](https://www.hivemq.com/blog/the-history-of-mqtt-part-2-mqtt-3-standardization/)
- [Dapr Agents CNCF announcement (March 2025)](https://www.cncf.io/blog/2025/03/12/announcing-dapr-ai-agents/)
- [Solace Agent Mesh Enterprise GA](https://www.prnewswire.com/news-releases/solace-signals-the-future-of-real-time-agentic-ai-with-introduction-of-solace-agent-mesh-enterprise-302628418.html)
- [Stripe as infrastructure (TNGlobal, March 2026)](https://technode.global/2026/03/09/stripe/)
- [MCP is TCP/IP of AI agents (DEV Community)](https://dev.to/nicolas_fainstein/why-mcp-is-the-tcpip-of-ai-agents-4ie4)
- [ANP GitHub](https://github.com/agent-network-protocol/AgentNetworkProtocol)
- [IETF ARDP agent discovery draft](https://www.ietf.org/ietf-ftp/internet-drafts/draft-pioli-agent-discovery-01.html)
- [Kong MCP Registry (Feb 2026)](https://www.prnewswire.com/news-releases/kong-introduces-mcp-registry-in-kong-konnect-to-power-ai-connectivity-for-agent-discovery-and-governance-302676451.html)
- [Microsoft Entra Agent Registry](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/publish-agents-to-registry)
- [Message Brokers for AI 2026 (dasroot.net)](https://dasroot.net/posts/2026/03/message-brokers-ai-kafka-nats-rabbitmq/)
- [The Agent Mesh DEV article](https://dev.to/webmethodman/the-agent-mesh-building-the-integration-layer-for-the-ai-renaissance-5io)
