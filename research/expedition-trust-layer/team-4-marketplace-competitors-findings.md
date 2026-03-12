# Team 4 Findings: Marketplace, Network Effects & Competitive Landscape
## Date: 2026-03-10
## Researcher: Team Member 4

---

## PART A: Competitive Analysis

### Protocols Layer

---

#### Anthropic MCP (Model Context Protocol)

**What they actually sell/do:**
An open standard (not a product) for connecting AI systems to external data sources and tools. Defines a client-server protocol where AI apps are "hosts," data/service providers are "servers," and a protocol layer standardizes communication. Submantle already plans to expose an MCP server, making this an integration target, not a competitor.

**How big:**
- Launched November 2024
- 97M+ monthly SDK downloads across Python and TypeScript (as of mid-2025)
- Adopted by OpenAI (March 2025), Google DeepMind (April 2025), and virtually every major AI framework
- Thousands of pre-built MCP servers as of early 2026
- Anthropic donated MCP to the Linux Foundation's new Agentic AI Foundation (alongside goose by Block and AGENTS.md by OpenAI) — governance now industry-wide
- Source: [Anthropic announcement](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation), [The New Stack](https://thenewstack.io/why-the-model-context-protocol-won/), [Pento Year Review](https://www.pento.ai/blog/a-year-of-mcp-2025-review) — accessed March 2026

**Relationship to Submantle:** Pure ally. MCP defines how agents call tools. Submantle builds the MCP server that gives agents awareness. MCP is the pipe; Submantle is the water. Every agent using MCP is a potential Submantle query.

**Behavioral trust features:** None. MCP has no concept of agent trust, reputation, or behavioral history. This is the exact gap Submantle fills.

**What Submantle should adopt:** MCP is the right integration surface — this decision is already validated by industry adoption. The donation to Linux Foundation means MCP will be permanent infrastructure, not abandoned.

---

#### Linux Foundation A2A / IBM ACP (now merged)

**What they actually sell/do:**
Two protocols that merged in mid-2025. A2A (Agent-to-Agent, from Google) defines how agents discover and communicate with each other. ACP (Agent Communication Protocol, from IBM's BeeAI) defined REST-based agent messaging. Post-merger, A2A is the unified standard under Linux Foundation for agent-to-agent communication — where MCP is agent-to-tool, A2A is agent-to-agent.

**How big:**
- Google donated A2A to Linux Foundation (late 2025)
- IBM donated ACP to Linux Foundation (August 2025), then the two merged
- "Quickly becoming the de facto standard for how agents should talk to one another" — but MCP has larger ecosystem as of early 2026
- Source: [Linux Foundation announcement](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents), [LFAI blog](https://lfaidata.foundation/communityblog/2025/08/29/acp-joins-forces-with-a2a-under-the-linux-foundations-lf-ai-data/), [The Register](https://www.theregister.com/2026/01/30/agnetic_ai_protocols_mcp_utcp_a2a_etc/) — accessed March 2026

**Relationship to Submantle:** Complementary at a different level. A2A handles agent-to-agent messaging. Submantle handles the awareness layer that gives agents context. An agent discovering another agent via A2A still needs Submantle to understand what that agent is doing, its trust history, and what it's accessing.

**Behavioral trust features:** None. A2A establishes communication channels, not trust hierarchies. A2A defines that agents can talk; it says nothing about whether they should be trusted.

**What Submantle should adopt:** Monitor A2A for the "agent discovery" use case — agents registering on the A2A network could be enriched with Submantle trust scores.

---

#### Agent Network Protocol (ANP)

**What they actually sell/do:**
An open-source protocol using W3C DID (Decentralized Identifiers) to give agents cryptographic identities. Three-layer architecture: Identity + Encrypted Communication (W3C DID-based), Meta-Protocol, Application Protocol. Aims to become "the HTTP of the Agentic Web." Uses the `did:wba` method for decentralized authentication without central authority.

**How big:**
- GitHub project, arxiv white paper (August 2025), IETF draft in progress
- Early stage — "W3C DID infrastructure is not yet mature" (per their own white paper)
- No known commercial deployment, no funding disclosed
- Source: [ANP GitHub](https://github.com/agent-network-protocol/AgentNetworkProtocol), [ANP arxiv paper](https://arxiv.org/html/2508.00007v1), [protocol comparison survey](https://arxiv.org/html/2505.02279v1) — accessed March 2026

**Relationship to Submantle:** More ally than threat — ANP solves agent identity, Submantle solves agent trust. ANP answers "who is this agent?" cryptographically; Submantle answers "should I trust this agent?" behaviorally. They are adjacent layers. Submantle could accept ANP-verified identities as input to its trust scoring.

**Behavioral trust features:** None. ANP is purely identity/authentication. No behavioral history, no trust scoring, no reputation decay.

**Maturity risk:** W3C DID is newly ratified; infrastructure is immature. ANP is still early-adopter territory with no production deployments confirmed. Not an immediate competitive threat.

---

### Infrastructure / Middleware

---

#### Composio

**What they actually sell/do:**
An integration and authentication layer for AI agents. Manages OAuth flows, stores/refreshes API keys, and provides 500+ pre-built tool integrations. The key mechanism: agents never see the actual API key — Composio holds credentials and makes calls on the agent's behalf (Brokered Credentials pattern). Positioned as "the only unified API platform purpose-built for AI agents."

**How big:**
- Series A: $25M raised July 2025, led by Lightspeed at $120M valuation
- Total funding: ~$29M
- $2M ARR as of June 2025 (per Latka data)
- Source: [SiliconANGLE](https://siliconangle.com/2025/07/22/composio-raises-25m-funding-ease-ai-agent-development/), [Latka](https://getlatka.com/companies/composio.dev), [Crunchbase](https://www.crunchbase.com/organization/composio-b822) — accessed March 2026

**Relationship to Submantle:** Complementary, not competitive. Composio handles auth/credentials (what the agent is allowed to DO). Submantle handles awareness and trust (what the agent IS and has DONE). A high-trust Submantle score could eventually unlock reduced Composio credential friction — they're adjacent, not overlapping.

**Behavioral trust features:** None. Composio manages auth tokens, not behavioral history. No reputation scoring, no trust tiers, no behavioral decay.

**What to learn:** Composio's "brokered credentials" model is analogous to Submantle's trust brokerage. Just as Composio holds credentials so agents don't need to, Submantle holds behavioral history so apps don't need to build their own. Same pattern, different domain.

---

#### LangChain / LangGraph / Langflow

**What they actually sell/do:**
LangChain is the dominant agent framework for building LLM-powered applications. LangGraph is their stateful agent orchestration layer (directed graphs of agent steps). LangSmith is their observability/monitoring product. Langflow is a competing low-code visual flow builder. These are tools for BUILDING agents, not governing them.

**How big:**
- LangChain is the most widely adopted agent framework — no specific revenue disclosed but industry-standard adoption
- 89% of agent developers use some form of agent observability (LangSmith category), per their own State of Agent Engineering survey
- Langflow: lacks RBAC and built-in observability, exposes workflows over REST and MCP
- Source: [LangChain State of Agent Engineering](https://www.langchain.com/state-of-agent-engineering), [Analytics Vidhya comparison](https://www.analyticsvidhya.com/blog/2026/01/langchain-vs-langgraph-vs-langsmith-vs-langflow/) — accessed March 2026

**Relationship to Submantle:** Major integration opportunity, not competition. LangChain/LangGraph agents are exactly the kind of agents that need Submantle awareness. Once Submantle has an MCP server, LangChain agents can query it directly. LangSmith handles observability within a single agent's lifecycle; Submantle handles cross-agent, cross-session behavioral trust across the whole ecosystem.

**Behavioral trust features:** LangSmith provides execution traces and monitoring, but this is debug-oriented, not trust-scoring. No reputation system, no cross-session behavioral history, no trust portability.

**What to learn:** LangSmith's adoption proves developers want visibility into agent behavior. Submantle's trust layer is what happens AFTER that visibility is aggregated over time into reputational signal.

---

#### Terminal / Sandbox Execution Environments

**What they actually sell/do:**
"Terminal Use" as named by Gemini does not appear to be a specific company. The category is AI agent sandboxing: isolated execution environments for agents that run code. Key players identified:
- **E2B**: Firecracker microVMs, 150ms cold start, 24-hour session limit
- **Daytona**: $31M raised (including $24M Series A, February 2026), sub-90ms cold starts, $1M ARR in under 3 months
- **Northflank**: Processes 2M+ isolated workloads monthly
- Source: [Northflank sandbox guide](https://northflank.com/blog/best-code-execution-sandbox-for-ai-agents), [Daytona customer story](https://www.daytona.io/customers/laude), [sandbox comparison](https://lifo.sh/blog/ai-sandbox-comparison-2026) — accessed March 2026

**Relationship to Submantle:** Different layer entirely. Sandboxes isolate agent execution. Submantle tracks what agents DO, not where they run. Submantle's awareness of what's running could integrate with sandbox execution — e.g., knowing which sandboxed agent is running which task.

**Behavioral trust features:** None. Isolation is about containment, not reputation.

---

#### SentinelOne / Zenity (the actual "shadow agent monitoring" companies)

**What they actually sell/do:**
The name "Sential/Sentrial" from the original brief likely refers to SentinelOne's AI security work and/or Zenity. These are the real shadow-agent monitoring players:

**Zenity:**
- Full inventory and attribution of AI agents: who created them, what tools they use, what systems they access
- Three pillars: Observe (behavioral baselines, anomaly detection), Govern (posture management), Defend (real-time threat detection/response)
- Specifically monitors shadow AI (unsanctioned agents), prompt injection, data leaks, over-permissioned actions
- $38M Series B (October 2024), led by Third Point Ventures and DTCP, with Microsoft M12 as strategic investor
- Total funding: $55M+
- Named Gartner Cool Vendor 2025 in Agentic AI TRiSM, Fortune Cyber 60 2025
- Source: [Zenity platform](https://zenity.io/platform), [BankInfoSecurity](https://www.bankinfosecurity.com/zenity-gets-38m-series-b-for-agentic-ai-security-expansion-a-26696) — accessed March 2026

**SentinelOne:**
- Acquired Prompt Security (shadow AI tool), integrates via MCP gateway
- AI Red Teaming based on OWASP Top 10 for LLMs
- Source: [SentinelOne blog](https://www.sentinelone.com/blog/how-sentinelone-secures-the-ai-tools-that-act-like-users/), [TechCrunch VC analysis](https://techcrunch.com/2026/01/19/rogue-agents-and-shadow-ai-why-vcs-are-betting-big-on-ai-security/) — accessed March 2026

**Relationship to Submantle:** Zenity is the closest competitor identified in this research. Zenity does behavioral monitoring of agents inside enterprises. Submantle does behavioral awareness of agents at the device/OS level.

Key distinction: Zenity is enterprise security — it's sold to IT teams to govern agents they've deployed. Submantle is device infrastructure — it operates below the application layer and tracks what's actually happening on the machine. Zenity looks down from the security layer. Submantle looks up from the OS layer.

**Does Zenity have universal behavioral trust?** No. Zenity detects threats and anomalies within an enterprise deployment. It does not build portable, cross-ecosystem behavioral trust scores. It doesn't offer trust portability. It doesn't create an economy around trust reputation. It's a security product, not a trust infrastructure.

**What to learn:** Zenity's $55M in funding at Gartner Cool Vendor status validates that enterprise buyers will pay for agent behavioral monitoring. Submantle's design is more ambitious — not just monitoring, but a trust protocol layer — but Zenity demonstrates the market exists.

---

### Enterprise Agentic Meshes

---

#### Microsoft Copilot Studio

**What they actually sell/do:**
Low-code platform for building autonomous agents within the Microsoft 365 ecosystem (SharePoint, Teams, Dynamics, Azure). As of March 2026, Microsoft launched "Agent 365" — a unified view of agents across M365 Copilot and Copilot Studio for IT governance. Announced "Frontier Suite" on March 9, 2026 with emphasis on intelligence + trust.

**How big:**
- 1.6 million Microsoft Security customers
- Microsoft is the dominant enterprise software provider globally
- Source: [Microsoft 365 Blog March 2026](https://www.microsoft.com/en-us/microsoft-365/blog/2026/03/09/powering-frontier-transformation-with-copilot-and-agents/), [Microsoft Security Blog](https://www.microsoft.com/en-us/security/blog/2026/03/09/secure-agentic-ai-for-your-frontier-transformation/) — accessed March 2026

**Relationship to Submantle:** Operating at a different level — but with overlap risk. Copilot Studio builds agents FOR enterprises. Submantle provides awareness UNDER all agents. Microsoft is explicitly moving toward open standards (MCP support, open agent SDK). If Submantle builds the OS-level trust layer, Microsoft enterprise agents become Submantle's customers, not competitors.

**Behavioral trust features:** Microsoft Agent 365 provides governance dashboards and policy enforcement, but this is within the Microsoft ecosystem only. No portable trust scores, no cross-ecosystem reputation.

**Risk:** Microsoft has resources to build Submantle-like features into Windows if they see the opportunity. However, their trust is enterprise-scoped (tied to Azure AD / Entra), not universal.

---

#### Salesforce Agentforce

**What they actually sell/do:**
Enterprise agent platform for customer service, sales, and marketing workflows. Uses "Einstein Trust Layer" — a proprietary AI governance framework baked into Salesforce's data cloud. Agents operate within Salesforce CRM data, follow defined "Agent Operating Procedures," and have strict action guardrails.

**How big:**
- Salesforce is a $200B+ market cap company
- CEO Marc Benioff claimed 93% agent accuracy (contested)
- Source: [VentureBeat Salesforce research](https://venturebeat.com/security/salesforce-research-across-the-c-suite-trust-is-the-key-to-scaling-agentic), [Trailhead trust module](https://trailhead.salesforce.com/content/learn/modules/trusted-agentic-ai/discover-how-salesforce-builds-trusted-agentic-ai) — accessed March 2026

**Relationship to Submantle:** Different level. Agentforce agents work within Salesforce data. Submantle works at the OS/device layer. Salesforce's Einstein Trust Layer is proprietary, scoped to their ecosystem, and not portable. A Salesforce agent interacting with a user's device still has no Submantle-level awareness of what's happening outside Salesforce.

**Behavioral trust features:** Yes — but siloed. Einstein Trust Layer includes quality data checks, behavioral guardrails, approval workflows, and performance monitoring. However, it is 100% proprietary to Salesforce and not portable across ecosystems.

**What to learn:** Salesforce validated that enterprises will pay for trust-bounded agents. Their framework proves the commercial case for "trust as a product feature." Submantle's advantage is portability — Einstein Trust Layer only covers Salesforce agents; Submantle covers all agents.

---

#### Netcracker

**What they actually sell/do:**
NEC subsidiary building agentic AI solutions specifically for telecom operators. 60+ pre-built agents for telecom workflows (billing, network ops, customer journeys). Won Juniper Research Platinum Award for AI Innovation in Telco, 2026. Results claimed: service designs 7x faster, 70% less time to resolve billing issues, 2.5x faster time to market.

**How big:**
- NEC subsidiary — enterprise telecom vendor
- Source: [Netcracker press releases](https://www.netcracker.com/news/press-releases/juniper-research-presents-netcracker-with-distinguished-2026-platinum-award-for-ai-innovation-in-telco.html) — accessed March 2026

**Relationship to Submantle:** Niche vertical player. Netcracker is telecom-specific. Irrelevant as a direct competitor. Interesting as a future partnership/integration target — telecoms that deploy Netcracker's agents would benefit from Submantle's OS-level awareness.

**Behavioral trust features:** Netcracker mentions an "AI Trust & Control layer" in its platform description, but this appears to be internal to their telecom agent orchestration. Not a universal trust layer.

---

### Agentic Web Startups

---

#### Relevance AI

**What they actually sell/do:**
No-code platform for building "AI workforces" — teams of specialized agents that collaborate like employees. Product called "Workforce" for multi-agent coordination. Also "Invent" for creating agents via natural language. Targets non-technical professionals.

**How big:**
- Series B: $24M (May 2025), led by Bessemer Venture Partners
- Total funding: $37M
- 40,000 agents created on platform in January 2025 alone
- 80 employees (SF + Sydney)
- Customers: Qualified, Activision, Safety Culture
- Source: [TechCrunch Series B](https://techcrunch.com/2025/05/06/relevance-ai-raises-24m-series-b-to-help-anyone-build-teams-of-ai-agents/), [Relevance AI blog](https://relevanceai.com/blog/the-ai-workforce-revolution-24m-series-b-to-accelerate-our-mission) — accessed March 2026

**Relationship to Submantle:** Agent builder, not trust infrastructure. Relevance AI creates agents; those agents need Submantle to understand their environment.

**Behavioral trust features:** None identified. Platform tracks what agents do within workflows, but no cross-ecosystem trust reputation.

---

#### Lindy AI

**What they actually sell/do:**
No-code agent platform for work automation. Core loop: Agent Builder (workflows via natural language) + Computer Use (browser automation) + 5,000+ integrations. Monitor via dashboard showing actions taken, decisions made, and human escalations. Human-in-the-loop for edge cases. Credit-based pricing ($49.99/mo Pro, $299.99/mo Business).

**How big:**
- No disclosed funding found
- G2 reviews indicate growing adoption among non-technical users
- Source: [Lindy reviews](https://www.g2.com/products/lindy-lindy/reviews), [Lindy AI review analysis](https://ucstrategies.com/news/lindy-ai-review-2026-pricing-features-and-real-productivity-gains/) — accessed March 2026

**Relationship to Submantle:** Agent platform. Lindy's dashboard shows what agents did — Submantle shows what's happening at the OS level where those agents operate. Complementary, not competing. Lindy is the agent; Submantle is the ground.

**Behavioral trust features:** Lindy has basic monitoring (actions taken, escalations) but this is internal to its platform. No portable trust, no reputation scoring.

---

#### Decagon & Sierra

**What they actually sell/do:**
Both build enterprise AI agents for customer experience (customer support, sales, service). Decagon uses "Agent Operating Procedures" (AOPs) to define agent behavior. Sierra gives teams tools to define goals, guardrails, and integrations. Both enable agents to take real actions (refunds, account updates, order changes).

**How big:**
- Decagon: $4.5B valuation (January 2026), $250M Series D, total funding $481M. Source: [Bloomberg](https://www.bloomberg.com/news/articles/2026-01-28/ai-customer-support-startup-decagon-valued-at-4-5-billion), [Decagon Series D](https://decagon.ai/resources/series-d-announcement) — accessed March 2026
- Sierra: Well-funded enterprise AI agent company, exact round data not surfaced in this search

**Relationship to Submantle:** These are the applications that need Submantle infrastructure. Decagon/Sierra agents running on user devices benefit from Submantle awareness. More importantly: a Medium analysis (February 2026) noted that "Decagon and Sierra CAN build trustworthy agents — the gap isn't technical, it's priority." Their AOPs and guardrails encode workflow logic but not behavioral trust. They are exactly the kind of platform that would query a universal Submantle trust layer rather than build their own.

**Behavioral trust features:** Internal guardrails only. Decagon's Trust Center and Sierra's guardrail framework constrain agent behavior but don't create portable trust scores or cross-ecosystem reputation. A user's trust history with Decagon agents is invisible to Sierra agents and vice versa.

**What to learn:** Decagon's $4.5B valuation proves the market for agents that take real actions is enormous. The trust gap identified in the Medium analysis — trust is a priority gap, not a capability gap — is precisely where Submantle sits. Nobody is building the portable trust layer these platforms need.

---

### Critical Question: Does Any Company Do What Submantle Proposes?

**Answer: No. Not one.**

Here is what exists and the gap it leaves:

| Company | What it does | What it leaves for Submantle |
|---------|-------------|------------------------------|
| Zenity | Enterprise agent security monitoring | No portable trust, no cross-ecosystem reputation, enterprise-only |
| HUMAN Security (AgenticTrust) | Behavioral bot/agent detection for websites | Defensive (detect malicious), not constructive (build reputation); no trust economy |
| Runlayer | MCP security gateway, threat detection | Protocol-level security, not behavioral reputation |
| Salesforce Einstein Trust | In-ecosystem agent governance | 100% siloed to Salesforce, not portable |
| Microsoft Agent 365 | Enterprise agent governance dashboard | Tied to Azure AD/Entra, not portable across ecosystems |
| SentinelOne | Shadow AI detection, red teaming | Threat-focused, no constructive trust building |
| Google UCP | Commerce protocol for agentic shopping | Handles transactions, not behavioral reputation |

**The gap that no one is filling:**
A universal, portable, behavioral trust score that:
1. Accumulates from observed behavior (not self-reported or policy-constrained)
2. Is portable across platforms, agents, and ecosystems
3. Creates economic incentives (discounts, access, rates) tied to reputation
4. Operates at the OS/device layer, below all applications
5. Enables a marketplace of trust-gated benefits

HUMAN Security's AgenticTrust is the closest in spirit — behavioral, real-time, adaptive — but it is positioned as a defensive security product (detect and block malicious agents) not as constructive trust infrastructure (build and reward trustworthy agents). They are fighting the same war from opposite angles.

---

## PART B: Marketplace & Network Effects

### 1. Credit Card Networks — The Foundational Analogy

**How Visa solved the chicken-and-egg problem:**
Bank of America created BankAmericard in 1958 and, critically, began *licensing the network* to other regional banks in 1966 rather than trying to be the only issuer. This single decision solved the chicken-and-egg problem: regional banks brought their existing customer relationships (cardholders), BofA provided the processing infrastructure (merchant acceptance). Within 11 years, the network had reached critical mass. By 1969, MasterCharge (now Mastercard) had emerged as a competing consortium, proving the same model could scale from alliance rather than single-company dominance.

**The flywheel mechanics:**
- More banks → more cardholders → more merchant incentive to accept → more card usage → more fee revenue → more banks want to join
- The network effects are two-sided: consumer utility rises with merchant acceptance, merchant utility rises with cardholder density
- Once the network reaches critical mass, switching costs become prohibitive — "building a global brand and acceptance network would cost $2-5 billion; no company has entered since Discover in 1985"

**The revenue model:**
- Interchange fees: ~1.5-2.5% per transaction paid by merchant's bank to cardholder's bank
- Network fees: small % paid to Visa/Mastercard for network access
- Visa itself earns ~0.1% on total transaction volume — at $13T+ volume, this is ~$13B/year
- Visa does NOT take credit risk. It is a pure network intermediary.

**Submantle mapping:**
Visa is the closest structural analogy to what Submantle wants to build. Visa does not make the purchases — it is the trusted intermediary that makes purchases possible. The key insight: **Visa's moat is not its technology — it's the fact that both merchants AND consumers depend on it simultaneously.** Submantle must create equivalent bilateral dependency: agents need trust scores to unlock features, platforms need trust data to serve their users better.

**Source:** [Dividendmonk network effects analysis](https://www.dividendmonk.com/visa-mastercard-unbeatable-business-model/), [Federal Reserve History](https://www.federalreservehistory.org/essays/electronic-point-of-sale-payments), [Cascade Visa strategy study](https://www.cascade.app/studies/visa-strategy-study) — accessed March 2026

---

### 2. App Stores — Trust-Gated Distribution

**The trust model:**
Apple App Store uses manual review (24-72 hours) creating a quality/safety guarantee that developers pay 30% for. Google Play uses automated review with faster approval but lower trust guarantee. Both create a certification system: "in the App Store" means Apple approved it.

**Revenue mechanics:**
- Standard: 30% cut of in-app purchases and subscriptions
- After year 1 of subscription: 15%
- Small Business Program (under $1M revenue): 15% across the board
- Google: 15% on first $1M, then 30% above that
- App Store generates $100B+ annual gross app revenue

**Why developers accept the 30% tax:**
The distribution. Being in the App Store gives access to hundreds of millions of paying customers who trust the store's curation. The tax pays for trust. Developers who build outside the store reach fewer customers — the trust premium is worth more than the fee.

**Submantle mapping:**
The "Submantle Safe" certification described in VISION.md is structurally identical to App Store certification. Developers pay/invest in certification because certified access unlocks a trusted distribution channel. The Submantle Store is an App Store for agent capabilities, not apps.

**Critical difference:** App Store certification is one-time and binary (approved/rejected). Submantle certification is behavioral and continuous (trust accumulates, decays, varies by context). This is strictly more valuable — and more defensible.

**Source:** [Business of Apps revenue data](https://www.businessofapps.com/data/app-revenues/), [Pravaah comparison](https://www.pravaahconsulting.com/post/apple-app-store-vs-google-play-store) — accessed March 2026

---

### 3. Loyalty Ecosystems — Trust-as-Currency

**Airline loyalty program mechanics:**
Frequent flyer programs are built on three psychological levers:
1. **Progress addiction:** "Just 8,000 points away from Platinum" — apps and emails constantly remind members of proximity to the next tier
2. **Status identity:** Losing Platinum status is described as "feeling like a breakup" — the tier becomes part of identity
3. **Irrational behavior engine:** Rational consumers take the cheapest flight. Loyal flyers take connections and pay more to protect their tier. The FFP's job is to manufacture irrationality.

**The paradox:**
Airline loyalty programs "have never been more profitable, yet members have never been less loyal" — 95% of airline loyalty reviews on Trustpilot rated one star between 2019-2025. Airlines keep devaluing points; members keep complaining and keep flying the same airline. The status lock-in outlasts the satisfaction.

**What actually works:**
The tiers that drive behavior change are ones where the delta between tiers is EXPERIENTIAL (lounge access, upgrades) not just accumulation (more points). You don't obsess over points — you obsess over the *identity* of the tier.

**Starbucks as the superior model:**
Starbucks Rewards drives 60% of U.S. revenue from loyalty members. Key stats:
- 44% customer retention rate vs. 25% industry average
- Loyalty members are 5.6x more likely to visit daily
- 100M+ weekly transactions processed with real-time behavioral analytics
- March 10, 2026: Starbucks just relaunched three-tier system (Green, Gold, Reserve)
- The star currency works because redemption is FAST (you earn and use quickly, keeping engagement high vs. airline points which take years to accumulate)

**Submantle mapping:**
Submantle's trust tiers (Anonymous → Registered → Trusted) should create EXPERIENTIAL deltas, not just rate deltas. "Registered agents get faster responses" is less sticky than "Registered agents get access to premium awareness data streams" — the identity matters. Starbucks proves that behavioral data (purchase history, daypart, churn signals) used to personalize rewards creates addiction loops. Submantle has richer behavioral data than Starbucks ever will.

**Source:** [Medium loyalty economics analysis](https://medium.com/travel-marketing-insights/the-economics-and-psychology-of-airline-loyalty-programs-eddc5caa844d), [Startup Spells FFP analysis](https://startupspells.com/p/frequent-flyer-programs-airline-loyalty-economics), [GrowthHQ Starbucks 2026 analysis](https://www.growthhq.io/our-thinking/starbucks-digital-loyalty-2026-how-starbucks-rewards-drives-60-revenue-inspires-global-brands-and-sets-the-benchmark-for-mobile-first-custom), [CNBC Starbucks tier relaunch](https://www.cnbc.com/2026/01/29/starbucks-to-reintroduce-loyalty-program-tiers.html) — accessed March 2026

---

### 4. Professional Certifications — Trust Through Demonstrated Capability

**How certifications create economic value:**
AWS, Azure, and Google Cloud certifications create a 27-40% salary premium for certified professionals ($148K-$163K for AWS Solutions Architect Professional). The cloud certification market is driven by employer demand: companies deploying cloud infrastructure need to verify their staff can do it safely.

The key economics: AWS doesn't primarily earn from cert revenue — they earn from increased cloud adoption by certified customers. Certification is a marketing and ecosystem-building mechanism that happens to also be a revenue line.

**Revenue model:**
- AWS exam fees: $150-300 per attempt
- Recertification required every 3 years (recurring revenue)
- AWS likely earns hundreds of millions from certifications, but the real payoff is cloud spend from certified customers

**Submantle mapping:**
"Submantle Safe" certification follows the same model. The cert fee is secondary. The primary value is:
1. Certified developers build agents that work correctly with Submantle (reduces ecosystem fragmentation)
2. Certified agents get access to premium trust tiers (creates developer incentive)
3. Enterprises require Submantle certification for agent deployments (creates pull from the demand side)

AWS certifications work because cloud adoption creates urgency. Agent safety adoption will create urgency in the same way — eventually, enterprises will require proof that agent developers understand Submantle's trust model.

**Source:** [CertWizard certification guide](https://certwizard.com/blog/aws-vs-azure-vs-google-cloud-certifications), [KodeKloud AWS cert value](https://kodekloud.com/blog/top-aws-certifications-in-2026-which-are-worth-your-investment/) — accessed March 2026

---

### 5. The Submantle Store Vision — What "Setting Up a Store" Actually Looks Like

**What the research reveals about Fortune 500 brand motivation:**

The Google Universal Commerce Protocol (launched January 2026 with Shopify, Walmart, Target, Wayfair, Etsy, Mastercard, Visa, American Express, and 15+ others) reveals what Fortune 500 brands actually want from trust infrastructure: **verified intent at point of transaction.** UCP uses cryptographic proof of user consent for each authorization. What brands want is to know that the agent acting on behalf of a user actually has that user's permission, and that the user has a verified behavioral history.

Submantle's trust score answers the question UCP can't: not just "did the user consent to this purchase?" but "has this agent's behavior over time demonstrated it should be trusted to act on this user's behalf?"

**The minimum viable Submantle marketplace:**
Drawing from marketplace research on seeding strategies and the Visa/Starbucks models, the minimum viable marketplace for Submantle needs three things:

1. **Seeded supply before launch:** At least 20-30 agent integrations with verified Submantle trust scores before opening to brands. "Seed your marketplace with high-quality supply before you launch to customers" — without this, the store is empty and early visitors don't return.

2. **One addiction anchor:** One brand offering a genuinely meaningful trust-gated benefit. Not "$5 off" — something experiential. Example: a developer tools company offering instant priority support to Submantle-verified agents (no queue, direct to expert). This creates FOMO for developers who are not verified.

3. **The bilateral dependency:** Agents register with Submantle to build trust history. Brands access Submantle to offer trust-gated benefits. The value flows in both directions simultaneously — exactly like Visa needed both cardholders AND merchants.

**What creates addiction:**
Progressive Snapshot (behavioral telematics) proves the model works outside financial services. Drivers who enroll in Snapshot save an average of $322/year for safe behavior — 2/10 get rate increases for unsafe behavior. The psychological mechanism: real economic stakes tied to observable behavior create behavior change. Submantle's equivalent: agents that behave well earn trust that unlocks real economic benefits (lower API transaction fees, premium data access, brand discounts). Agents that behave badly see trust decay and lose access.

The Progressive Snapshot model (discount for verified safe behavior) directly maps to Submantle: verified safe agents get cheaper access. This creates incentive for agent developers to build well-behaved agents, not just functional ones.

**Source:** [UCP Google Developers Blog](https://developers.googleblog.com/under-the-hood-universal-commerce-protocol-ucp/), [Progressive Snapshot review](https://www.autoinsurance.com/companies/progressive/snapshot/), [Sharetribe MVP marketplace guide](https://www.sharetribe.com/academy/how-to-build-a-minimum-viable-platform/), [NfX network effects construction guide](https://www.sciencedirect.com/science/article/pii/S2666954422000242) — accessed March 2026

---

### 6. Trust-Based Discounts — Existing Models

**Progressive Snapshot (most direct analog):**
- Behavior observed: hard braking, acceleration patterns, night driving, phone use, miles driven
- Outcome: average $322 savings per year for safe drivers; rate increases for unsafe drivers
- The model: behavior observation → trust score → real economic outcome
- 2/10 drivers get rate increases — the consequence of unsafe behavior makes the discount meaningful (you can't just enroll and coast)
- Source: [Progressive Snapshot review 2026](https://www.autoinsurance.com/companies/progressive/snapshot/) — accessed March 2026

**UBI (Usage-Based Insurance) as behavioral trust economy:**
State Farm's Drive Safe & Save, Allstate's Drivewise, Progressive Snapshot — the entire UBI market is built on "we trust you more when we can see your behavior." The insurance industry arrived at exactly the same architecture Submantle is proposing: observation → scoring → economic benefit. Key difference: insurance UBI tracks driving behavior. Submantle tracks agent behavior. The mechanism is identical.

**The loyalty-trust bridge:**
Modern loyalty programs are converging on behavioral trust. Open Loyalty's 2026 benchmark reports that "beyond-purchase behaviors" (reviews, referrals, app engagement, community participation) now unlock multiplier rewards. The shift from "buy more, earn more" to "behave well, earn more" is exactly Submantle's trust model applied to consumer loyalty.

---

## Gaps and Unknowns

- **Zenity's exact behavioral scoring methodology** is not publicly disclosed. Whether they use Beta Reputation or proprietary algorithms is unknown. Closer research needed before Submantle finalizes its own scoring to avoid/leverage their approach.
- **HUMAN Security's AgenticTrust funding** was not found. The product launched July 2025; current scale is unknown. If well-funded, they are the closest competitor to Submantle's trust layer concept (from the defensive/security side).
- **Google UCP + Mastercard "new trust layer" partnership** — search results reference this specifically ("Mastercard and Google's new trust layer could reshape how AI buys for you") but details were not surfaced. This bears direct investigation — if Mastercard and Google are building an agentic transaction trust layer, this is either a direct competitor or a potential integration partner for Submantle.
- **ANP's real traction:** ANP has a white paper and GitHub repo but no confirmed production deployments. The threat level is unclear. If ANP gets adopted as the standard for agent identity (the `did:wba` method), Submantle should plan to accept ANP-verified identities as inputs to its trust model.
- **The revenue model for the Submantle Store at early scale** — the research shows that marketplace MVPs need seeded supply, but the specific pricing model (what does a Fortune 500 brand actually pay to access Submantle trust-segmented demand?) needs validation against real enterprise procurement data.
- **Whether Salesforce or Microsoft will build a portable trust layer** — both have the resources and incentive. Currently they are building trust layers that are ecosystem-siloed. The risk is not that they build Submantle — it's that they achieve enough enterprise lock-in that their siloed trust layers become "good enough" for most buyers.

---

## Synthesis

### The Strongest Finding: The Gap Is Real and Unoccupied

After reviewing 20+ companies, the answer to the critical question is clear: **No one is building behavioral trust as a universal infrastructure layer.** Every company in the space is either:

1. Building agents (Decagon, Sierra, Relevance AI, Lindy)
2. Building agent frameworks (LangChain, Langflow)
3. Building agent auth/credentials (Composio)
4. Building agent security/monitoring within enterprises (Zenity, SentinelOne)
5. Building agent communication protocols (MCP, A2A, ANP)
6. Building commerce protocols for agent transactions (Google UCP)

None of them are building the layer that sits underneath all of these and tracks behavioral trust over time, makes that trust portable, and creates an economy of trust-gated benefits.

The closest parallel to what Submantle proposes — HUMAN Security's AgenticTrust — positions itself as a defensive security product (detect and stop malicious agents). Submantle's vision is constructive (build and reward trustworthy agents). These are the same problem from opposite directions. HUMAN Security answers "is this agent malicious?" Submantle answers "how much should this agent be trusted?"

### The Strongest Network Effect Model for Submantle

The Visa model is the right structural template:
- Visa doesn't take credit risk; it's a network intermediary
- Submantle shouldn't store behavioral data centrally; it's a trust protocol
- Visa's moat is bilateral dependency; Submantle must create the same
- Visa solved chicken-and-egg by licensing the network to banks; Submantle should seed the network by building trust scores for the most widely-deployed agents first (LangChain agents, Claude agents, GPT agents) before launching the marketplace

**The addiction loop:**
Starbucks proves the model: behavioral data → personalized benefits → habit formation → dependency. Submantle's version: observable agent behavior → accumulating trust score → unlocking real economic benefits → agent developers prioritize good behavior → more good behavior → deeper trust data → richer benefits → more developers want in.

The critical insight from the airline loyalty research: **the addiction is not to the points, it's to the identity of the tier.** Submantle must make "Submantle Verified" a badge developers want. Not because the discount is huge — but because the badge means something. "My agent is Submantle Verified" should feel like "my app is in the App Store" or "I'm United Platinum."

### What Combination Works Best

**Phase 1 (Minimum Viable Trust Layer):**
- MCP server gives agents access to Submantle awareness (already planned)
- Beta Reputation scoring (already designed)
- Basic tier system with one meaningful experiential delta (Anonymous → Registered → Trusted)
- Seed with top 30 agent signatures to demonstrate the trust model is real

**Phase 2 (Minimum Viable Marketplace):**
- Sign 3-5 developer tools brands to offer trust-gated benefits (priority support, free compute credits, premium docs access)
- Make the trust-gated benefit genuinely meaningful — not a discount, an unlock
- Open the Submantle Store for identity pack contributions (community seeding)

**Phase 3 (Bilateral Dependency Lock):**
- Agent developers depend on Submantle scores to access brand benefits
- Brands depend on Submantle to reach trust-segmented agent developers
- This is the Visa flywheel. Once both sides depend on Submantle simultaneously, the network effect compounds and switching cost becomes prohibitive.

### What the Orchestrator Needs to Know

The competitive landscape confirms that **2026 is exactly the right moment.** The protocol wars (MCP vs A2A vs ANP) are resolving — MCP has effectively won as the dominant standard, and Submantle should bet on MCP. Enterprise security players (Zenity, SentinelOne) are staking out the "threat detection" side of agent trust. Nobody has staked out the "constructive reputation" side.

The most dangerous scenario for Submantle is not a competitor building the same thing. It's Google, Microsoft, or Salesforce deciding to build a portable trust layer as a competitive weapon — using their existing enterprise distribution to make their siloed trust model "standard." Submantle's defense against this is speed and openness: become the community standard for behavioral agent trust before these players move.

The Google Universal Commerce Protocol launch (January 2026) is a signal, not a threat. UCP handles commerce transactions. It explicitly does NOT handle behavioral trust scoring (per the DataDome analysis — "protocols regulate HOW agents interact, not WHICH agents should be trusted"). UCP is infrastructure that NEEDS Submantle's trust layer sitting underneath it.

The market is proving, right now, that trust is the central unsolved problem in agentic AI. The window to define the standard is open. It will not stay open.
