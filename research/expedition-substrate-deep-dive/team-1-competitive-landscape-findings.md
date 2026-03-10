# Team 1 Findings: Competitive Landscape & Prior Art
## Date: 2026-03-10
## Researcher: Team Member 1

---

## Executive Summary

The competitive landscape for Substrate is fragmented across five distinct categories — none of which have been unified into the broker layer Substrate proposes. The closest approach launched *yesterday* (Sage, March 9 2026), and it only covers three action types (bash, file write, URL fetch) with no OS process awareness. The gap Substrate targets — semantic understanding of what's running before an agent acts — is demonstrably unbuilt and recently validated as urgent by Sage's launch and the MCP security crisis of 2025.

---

## Battle-Tested Approaches

### 1. Passive Screen Recording + AI Search (Screenpipe, Microsoft Recall, Limitless/Rewind)

- **What:** Continuously record screen and audio, index with AI for searchable personal memory
- **Evidence:** Screenpipe raised $2.8M in July 2025 and has active GitHub usage across Windows, macOS, Linux. Microsoft Recall shipped to Copilot+ PCs in 2025 after multiple privacy delays. Limitless was acquired by Meta in December 2025 for integration into their wearables platform. Rewind rebranded/upgraded to Limitless 2.0 with ~14GB/month storage.
- **Source:** https://screenpi.pe/ (accessed March 2026); https://techcrunch.com/2025/12/05/meta-acquires-ai-device-startup-limitless/ (December 2025); https://www.windowslatest.com/2026/02/20/microsoft-says-2026-is-the-moment-for-ai-pcs-touts-windows-11-recall-copilot-and-the-highest-standard-of-security/ (February 2026)
- **Fits our case because:** These tools prove the market wants ambient awareness of computing context. They solve the "what did I do?" question for humans.
- **Tradeoffs:** All are passive observers — they cannot broker agent actions. Screenpipe has no concept of process semantics or workflow graphs. Recall cannot tell an agent "that Node process has been running for 2 hours and has unsaved work." None have an agent API. They record what happened; Substrate would govern what happens next.

### 2. AI Agent Guardrails Frameworks (Superagent, OpenGuardrails)

- **What:** Application-layer policy enforcement — evaluate agent actions (tool calls, API calls, prompts) against defined rules before execution
- **Evidence:** Superagent is open-source on GitHub with active development as of December 2025. OpenGuardrails launched November 2025. Both have documented GitHub stars and enterprise use cases.
- **Source:** https://www.helpnetsecurity.com/2025/12/29/superagent-framework-guardrails-agentic-ai/ (December 2025); https://www.helpnetsecurity.com/2025/11/06/openguardrails-open-source-make-ai-safer/ (November 2025)
- **Fits our case because:** Proves the market need — developers want guardrails around agents before destructive actions.
- **Tradeoffs:** Operate entirely at the application layer. No OS process awareness. Cannot answer "what processes are running and what do they mean?" They enforce rules defined by developers, not real-time awareness of the OS state. A policy can say "don't run rm -rf" but cannot say "these 8 Node processes belong to an image generation pipeline."

### 3. Authorization Platforms for Agent Permissions (WorkOS FGA, Cerbos, OpenFGA, OPA)

- **What:** Enterprise-grade authorization — control what data and APIs agents can access, with sub-50ms decision latency
- **Evidence:** WorkOS, Cerbos, and OPA are production-deployed at scale across large enterprises. OPA is a CNCF standard. These platforms handle billions of authorization decisions.
- **Source:** https://workos.com/blog/best-authorization-platforms-ai-agent-permissions-2026 (2026)
- **Fits our case because:** Proves the market will pay for agent permission brokering. The infrastructure pattern (query before act) is exactly what Substrate's Agent API needs.
- **Tradeoffs:** These are resource/data authorization tools — they manage *who can access what data*, not *what is currently happening on the OS*. They have zero awareness of running processes, workflow graphs, or user intent. The decision context is "does agent X have permission to read database Y" — not "should this agent kill these processes right now given what the user is doing."

### 4. Process Mining / Task Mining Tools (Skan, UltimateSuite/ServiceNow, ClearWork)

- **What:** Capture OS-level user activity (clicks, application switches, keystrokes, screen captures) to build workflow maps for enterprise process improvement
- **Evidence:** Task mining is a $2B market in 2025, projected to reach $10B by 2033 at 25% CAGR. UltimateSuite was acquired by ServiceNow in 2024. Skan has active enterprise customers.
- **Source:** https://www.skan.ai/top-10-process-mining-tools-for-the-2025-enterprise (2025)
- **Fits our case because:** These tools prove it is technically feasible to build workflow graphs from OS activity observation. They do the hard part (observing what's happening) but for enterprise process analytics, not real-time agent brokering.
- **Tradeoffs:** Built for retrospective business analysis, not real-time agent protection. They map workflows for process improvement, not to give agents contextual warnings. No agent API. No real-time query capability. No semantic process identity (they track application windows, not what a process *means*).

---

## Novel Approaches

### 5. Sage — Agent Detection & Response (Gen Digital / Avast, March 9 2026)

- **What:** Open-source security layer that installs as a plugin into AI coding agents (Claude Code, Cursor/VS Code) and intercepts three action types — bash commands, file writes, URL fetches — running them through heuristic threat detection before execution
- **Why it's interesting:** This is the most direct prior art found — published *yesterday* (March 9 2026). It explicitly names itself "Agent Detection & Response (ADR)", mirroring endpoint security terminology. It runs as a plugin that hooks into the agent's tool invocation layer. It's built by Gen Digital (Avast/Norton parent).
- **Evidence:** Active open-source project at github.com/avast/sage, covered by Help Net Security. Gen Threat Labs found over 18,000 exposed agent instances online, with 15% of observed skills containing malicious instructions.
- **Source:** https://www.helpnetsecurity.com/2026/03/09/open-source-tool-sage-security-layer-ai-agents/ (March 9, 2026)
- **Fits our case because:** Sage validates Substrate's core thesis — there is a real and urgent market for intercepting agent actions before they cause harm. The ADR framing is exactly the category Substrate's Agent API would create.
- **Risks / Gaps vs. Substrate:** Sage has zero OS process awareness. It cannot answer "what processes are running and what do they mean." It checks URLs and bash commands against threat heuristics — it has no concept of user workflow context, no workflow graph, no intent model, no cross-device sync. It's threat detection (is this malicious?) not context brokering (is this safe given what the user is doing right now?). Sage would not have prevented the Node process incident in VISION.md — killing active Node processes isn't a security threat, it's a contextual mistake.

### 6. Runlayer — MCP Security Gateway ($11M Seed, Khosla, November 2025)

- **What:** MCP-layer security startup providing gateway + threat detection + permissions + observability for AI agents operating over the Model Context Protocol
- **Why it's interesting:** Well-funded ($11M, Khosla Ventures), rapid customer adoption (8 unicorns/public companies in 4 months including Gusto, Instacart, Opendoor). Validates enterprise willingness to pay for agent brokering at the protocol layer.
- **Evidence:** TechCrunch coverage, November 2025 launch with confirmed enterprise customer list
- **Source:** https://techcrunch.com/2025/11/17/mcp-ai-agent-security-startup-runlayer-launches-with-8-unicorns-11m-from-khoslas-keith-rabois-and-felicis/ (November 2025)
- **Fits our case because:** Direct proof that enterprises will pay for agent permission brokering — this is Substrate's enterprise revenue thesis confirmed.
- **Risks / Gaps vs. Substrate:** Runlayer operates at the MCP protocol layer — it governs *API access* (what data sources and tools agents can connect to), not *OS context*. No process awareness. No workflow graph. No user intent. It's "can this agent access this database" not "should this agent kill these processes given what the user is doing." Also: Runlayer is enterprise/cloud-focused; Substrate targets the local machine and personal computing context.

### 7. AIOS — LLM Agent Operating System (Rutgers/AGI Research, COLM 2025)

- **What:** An OS kernel abstraction layer for LLM agents — manages scheduling, memory, storage, and access control for multiple agents running concurrently in the same environment
- **Why it's interesting:** The only academic project that frames itself as an "OS for agents" rather than guardrails around agents. Achieves 2.1x faster agent execution through intelligent scheduling. Published at COLM 2025. Active open-source project on GitHub.
- **Evidence:** Peer-reviewed at COLM 2025, open source, documented performance benchmarks, GitHub star count
- **Source:** https://arxiv.org/abs/2403.16971 (COLM 2025); https://www.labellerr.com/blog/aios-explained/ (2025)
- **Fits our case because:** Proves the architectural concept of an OS-like layer managing agent resources is sound and buildable. The privilege-based access control mechanism (hashmap of agent IDs to privilege groups) is a direct analogue to Substrate's broker.
- **Risks / Gaps vs. Substrate:** AIOS manages agents running *inside AIOS*, not system-wide OS processes. It coordinates agents with each other but has no awareness of what the user's non-AIOS processes are doing. An AIOS agent has no knowledge of an image generation pipeline running outside the AIOS environment. It's an agent execution environment, not a context layer visible to all agents regardless of their framework.

---

## Emerging Approaches

### 8. /dev/agents — OS for AI Agents ($56M Seed, Index Ventures + CapitalG, November 2024)

- **What:** Founded by Android/Google veterans (David Singleton, Hugo Barra, Ficus Kirkpatrick, Nicholas Jitkoff), building "a cloud-based operating system for trusted AI agents to work with users across all of their devices"
- **Momentum:** $56M seed at $500M post-money valuation. Backed by Andrej Karpathy, Alexandr Wang, Andy Rubin. $36M estimated 2025 revenue with 15-person team. Capital G (Alphabet) lead suggests Google strategic interest.
- **Source:** https://sdsa.ai/ (accessed March 2026); https://www.indexventures.com/perspectives/the-operating-system-for-ai-agents-our-investment-in-devagents/ (2024/2025)
- **Fits our case because:** Largest funded bet on the "OS layer for agents" thesis. Cross-device focus matches Substrate's cross-device sync capability. Android/Google DNA suggests deep OS-level ambition.
- **Maturity risk:** Product details are not public. The public framing is UX-centric ("new UI patterns") rather than process-safety-centric. The vision may be about agent app distribution, not OS process context brokering. Critically: /dev/agents appears cloud-first, which means agents query a cloud OS rather than having a local daemon with deep OS-level visibility. This creates a fundamental difference from Substrate's local-first, process-level awareness model.

### 9. Microsoft Windows Agentic OS (October 2025 Ignite, March 2026)

- **What:** Microsoft's integration of Copilot into Windows as a system-level agent layer — "Voice, Vision, Actions" capabilities added to Windows 11, with Agent Workspaces (isolated mini-sessions for agents), an MCP registry built into Windows, and Defender-based runtime protection for Copilot Studio agents
- **Momentum:** Shipped in October 2025 Windows 11 update. Enterprise controls via Intune/Entra planned for 2026. Microsoft's security blog specifically addressed agentic AI security on March 9 2026 (same day as Sage launch).
- **Source:** https://techcommunity.microsoft.com/blog/windows-itpro-blog/evolving-windows-new-copilot-and-ai-experiences-at-ignite-2025/ (November 2025); Microsoft Security Blog March 9 2026
- **Fits our case because:** Microsoft is building OS-level agent infrastructure — validates the architectural thesis that this belongs at the OS layer.
- **Maturity risk:** Windows-only, deeply tied to Copilot ecosystem. The "Agent Workspace" is isolated from the user's actual session — it's a sandboxed agent environment, not an awareness layer for the full OS context. Copilot Vision "sees" the screen but it's a per-task visual layer, not a persistent semantic process graph. No cross-device awareness of process state. Defender-based runtime protection is security-focused (threat detection), not context-aware (workflow awareness). Most critically: it requires Microsoft cooperation, Copilot+ hardware, and Windows — violating Substrate's OS-agnostic constraint.

### 10. Viven.ai — Personal Digital Twin ($35M Seed, Khosla, October 2025)

- **What:** AI digital twins for workplace knowledge — ingests emails, meetings, Slack, Google Docs to create a knowledge graph of what each person is working on, enabling "querying an absent colleague"
- **Momentum:** $35M seed round, deployed at Genpact and other enterprises, covered by TechCrunch and Josh Bersin
- **Source:** https://techcrunch.com/2025/10/15/eightfold-co-founders-raise-35m-for-viven-an-ai-digital-twin-startup-for-querying-unavailable-coworkers/ (October 2025)
- **Fits our case because:** Proves the market will pay for a knowledge graph of a person's work context. The pairwise context privacy framework is exactly the kind of consent model Substrate needs. The cross-application awareness (email + Slack + docs = work context) maps to Substrate's workflow graph.
- **Maturity risk:** Enterprise-focused (Microsoft Graph, Google Workspace). No OS process awareness. No agent brokering. No real-time query capability for destructive action prevention. It answers "what is this person working on?" not "what should this agent not destroy right now?"

---

## Gaps and Unknowns

### Questions This Research Did Not Answer

1. **Does any product do semantic process identity?** No product was found that understands a process as *what it is* (image generation pipeline) rather than just *what it is called* (node.exe). This is Substrate's most novel capability claim and no counterevidence was found.

2. **Does /dev/agents have local daemon architecture?** /dev/agents' public communications are intentionally vague about implementation. The cloud-first framing suggests a different architectural model than Substrate, but this is unconfirmed.

3. **What is Apple's roadmap for agent brokering?** Apple Intelligence has a semantic index and App Intents framework. Apple has not announced any agent broker or permission API. The gap is well-documented but Apple's private roadmap is unknown.

4. **Is there an open standard emerging for pre-action agent context queries?** MCP covers tool access, but no standard was found for "query running OS context before destructive action." This appears to be a standards gap, not just a product gap.

5. **What is the legal exposure for cross-device sensing?** Research found that EU GDPR remains the governing framework and US privacy law is fragmented. Environmental sensing is an active area of EU legal development (Tandfonline 2025). The specific exposure for a local-only daemon with user consent is unclear but likely manageable with proper consent architecture.

### Thin or Contradictory Evidence

- **Runlayer's technical architecture:** TechCrunch coverage is funding-announcement-only. The actual interception mechanism is undisclosed. It may be closer to Substrate than the MCP framing suggests, or it may be entirely different.
- **Agent observability tools (Arize, Maxim, AgentOps):** These track agent behavior for debugging/evaluation but do not intercept or broker. The line between "observability" and "active brokering" is blurry — some observability tools may be evolving toward real-time intervention.
- **/dev/agents revenue claim:** $36M 2025 revenue from a 15-person team with an undisclosed product is difficult to verify and may reflect pre-revenue contract value rather than actual ARR.

---

## Synthesis

### The Gap Is Real and Confirmed

After mapping approximately 15 products and projects across all relevant categories, **no existing product does what Substrate's Agent API proposes**: a cross-platform, OS-level daemon that maintains a semantic model of running processes and their relationships, and exposes an API that any agent can query before taking destructive actions. This is not a minor feature gap — it is a categorical absence.

The closest product (Sage) launched yesterday, operates at the agent plugin layer rather than the OS layer, covers only three action types, has no semantic process understanding, and is security-focused (threat detection) rather than context-aware (workflow preservation). Sage's existence validates the category without filling the gap.

### The Market Is Being Validated From Multiple Directions

- **Enterprise side:** Runlayer ($11M), Viven ($35M), Arize ($70M Series C) all confirm enterprises will pay for agent context management
- **Consumer side:** Screenpipe ($2.8M), Limitless (acquired by Meta), Microsoft Recall (shipping to Copilot+ PCs) all confirm demand for passive ambient awareness
- **Platform side:** /dev/agents ($56M seed), Microsoft Windows agentic OS, AIOS (COLM 2025) all confirm the "OS layer for agents" architectural thesis is taken seriously by well-funded teams

### Substrate's Unique Position

Every existing product fails on at least one of these three dimensions that Substrate proposes to combine:

| Capability | Passive Recorders | Guardrail Frameworks | Auth Platforms | Agent OS (AIOS, /dev/agents) | Sage |
|---|---|---|---|---|---|
| OS process awareness | Screen only | No | No | Agent processes only | No |
| Semantic process identity | No | No | No | No | No |
| Workflow graph (process relationships) | No | No | No | No | No |
| Real-time agent broker API | No | Application-layer only | API-access only | Internal to framework | Plugin-layer only |
| Cross-platform (Win/Mac/Linux) | Screenpipe only | Yes | Yes | Yes | Partial |
| User intent model (learned patterns) | No | No | No | No | No |
| Cross-device sync | No | No | No | Partially (cloud) | No |

### The Strongest Strategic Insight for the Orchestrator

**The window is narrow.** Sage launched March 9 2026. Microsoft shipped agentic Windows in October 2025. /dev/agents has $56M and Android veterans. The category is activating. However, none of these players are building from the OS process layer up with semantic process understanding as the core primitive. They are all building from the agent/protocol layer down. Substrate builds from the OS layer up — and that architectural inversion is the unfilled gap.

**The MCP security crisis creates urgency.** Over 13,000 MCP servers launched in 2025 with documented tenant isolation failures affecting unicorns (Asana, May 2025). The enterprise market is actively seeking a broker layer — Runlayer's 8 unicorn customers in 4 months is direct evidence. Substrate should position against this wave.

**The "inner ring first" constraint is validated by the market.** Every well-funded entrant is starting from software-only context (screen recording, API access, agent orchestration). No one is attempting to build the middle ring (hardware sensors) or outer ring (environmental data) first. The constraint in the Research Brief maps directly to where the market currently is, which means Substrate can be competitive with its inner ring alone.

---

## Sources

- https://www.helpnetsecurity.com/2026/03/09/open-source-tool-sage-security-layer-ai-agents/
- https://techcrunch.com/2025/11/17/mcp-ai-agent-security-startup-runlayer-launches-with-8-unicorns-11m-from-khoslas-keith-rabois-and-felicis/
- https://www.indexventures.com/perspectives/the-operating-system-for-ai-agents-our-investment-in-devagents/
- https://sdsa.ai/
- https://arxiv.org/abs/2403.16971
- https://www.labellerr.com/blog/aios-explained/
- https://screenpi.pe/
- https://techcrunch.com/2025/12/05/meta-acquires-ai-device-startup-limitless/
- https://www.windowslatest.com/2026/02/20/microsoft-says-2026-is-the-moment-for-ai-pcs-touts-windows-11-recall-copilot-and-the-highest-standard-of-security/
- https://techcrunch.com/2025/10/15/eightfold-co-founders-raise-35m-for-viven-an-ai-digital-twin-startup-for-querying-unavailable-coworkers/
- https://workos.com/blog/best-authorization-platforms-ai-agent-permissions-2026
- https://www.helpnetsecurity.com/2025/12/29/superagent-framework-guardrails-agentic-ai/
- https://www.esentire.com/blog/model-context-protocol-security-critical-vulnerabilities-every-ciso-should-address-in-2025
- https://newsletter.victordibia.com/p/agent-middleware-adding-control-and
- https://www.skan.ai/top-10-process-mining-tools-for-the-2025-enterprise
- https://techcommunity.microsoft.com/blog/windows-itpro-blog/evolving-windows-new-copilot-and-ai-experiences-at-ignite-2025/
- https://www.obsidiansecurity.com/blog/ai-agent-market-landscape
- https://deepmind.google/models/project-astra/
