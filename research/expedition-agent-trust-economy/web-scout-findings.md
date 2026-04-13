# Web Scout Findings — AI Agent Trust Economy
**Researcher:** Web Scout (Live Internet)
**Date:** April 12, 2026
**Research Question:** What specific AI agents are people already using for high-trust transactions, what infrastructure gaps exist, and where would a portable trust score create the most monetary value?

---

## 1. MARKET SIZE — THE NUMBERS

Ranges vary widely by firm; use these as directional, not precise:

- AI agents market 2026: $10.91B–$15B (Grand View, Roots Analysis)
- Agentic AI market 2026–2034: $9.14B → $139.19B at 40.5% CAGR (Fortune Business Insights)
- AI agents market to $52.62B by 2030 (MarketsandMarkets)
- Decentralized identity market alone: projected $7.4B in 2026
- Financial services AI spend in 2026: over $35B total
- WEF projection: AI agents could be worth $236B by 2034 — conditional on trust being solved
- Gartner: 40% of enterprise apps will embed task-specific agents by end of 2026

---

## 2. WHERE AI AGENTS ARE ALREADY OPERATING IN HIGH-TRUST CONTEXTS

### Financial Services
- Banks and fintechs deploying agents for fraud detection, credit underwriting, transaction dispute resolution, compliance monitoring
- Agents processing 50,000 pages of documents in minutes; claimed fraud loss reduction 78%
- 51% of enterprises have AI agents in production as of 2026; 85% have implemented or plan to
- Key platforms: AWS Bedrock Agents, Azure AI Foundry, Google Cloud Vertex AI Agents, Kore.ai (300+ pre-built agents)
- Oracle announced AI agent-driven capabilities for financial crime prevention (April 9, 2026)

### Procurement
- AI agents executing: demand signal aggregation, supplier discovery, RFQ generation, bid comparison, PO approval routing
- Projection: agents will manage 60–70% of end-to-end transactional procurement by 2026–2028
- High-volume use cases already automated: PO creation, three-way matching, spend classification, contract renewal alerts
- Procurement represents only 6% of AI use cases — very early, large upside

### Legal / Contracts
- 52% of in-house legal teams already using or evaluating contract AI
- 78% comfortable delegating first-pass contract review to an agent under attorney supervision
- Active usage nearly quadrupled since 2024
- Tools in production: Spellbook, Harvey, Ironclad, Juro — first-pass NDA review, contract intake, invoice review
- The shift from copilot to fully autonomous agent is underway; legal ops teams deploying networks of specialized agents

### Healthcare
- AI agents verifying patient benefits with claimed 99% accuracy and 10-second average verification time
- Agents determining prior authorization requirements and initiating requests
- HIPAA compliance is the gate: required attribute-based access control, hybrid PHI sanitization, immutable audit trails
- arxiv paper April 2026: "Towards a HIPAA Compliant Agentic AI System in Healthcare" — active research problem, not solved
- NVIDIA Agent Toolkit 2026 positioning in healthcare AI

---

## 3. TRUST INFRASTRUCTURE — WHAT EXISTS TODAY

### Major Commercial Players

**Mastercard Verifiable Intent** (March 5, 2026)
- Co-developed with Google; open-source cryptographic framework
- Creates tamper-resistant proof of consumer authorization for every AI agent transaction
- Aligns with Google's Agent Payments Protocol (AP2) and Universal Commerce Protocol (UCP)
- Uses Selective Disclosure (privacy-preserving); built on FIDO Alliance, EMVCo, IETF, W3C specs
- Partners committed: Fiserv, IBM, Checkout.com, Basis Theory, Getnet
- Focus: payment authorization layer, not general behavioral trust

**Microsoft Entra Agent ID** (Preview, 2026)
- Extends Microsoft Entra to give AI agents verified identities within enterprise IAM
- Supports OAuth 2.0, MCP, A2A protocols
- Four new identity object types; adaptive access policies, real-time risk detection, lifecycle management
- Agent Registry moving from Entra to Agent 365 admin center May 1, 2026
- Focus: enterprise identity management within Microsoft ecosystem — not portable across vendors

**Microsoft Agent Governance Toolkit** (April 2, 2026 — open source)
- Cryptographic identity using DIDs with Ed25519
- Inter-Agent Trust Protocol (IATP) for secure agent-to-agent communication
- Dynamic trust scoring: 0–1000 scale, five behavioral tiers

**Zenity**
- Enterprise AI agent security and governance platform
- Coverage: SaaS + cloud + endpoint environments
- Featured prominently at RSA 2026 as a category leader
- Focus: runtime security, policy enforcement, threat detection — not portable trust credentials

**HUMAN Security / AgenticTrust**
- 2026 State of AI Traffic report: AI-driven traffic up 187% Jan–Dec 2025; automation growth outpacing humans
- Key insight: only 0.5% separates benign automation rate from malicious automation rate
- Platform shifts from "bot or not?" to "is this interaction trustworthy?" regardless of human or AI origin
- Focus: web traffic layer, not financial or procurement trust

**Ping Identity** (March 24, 2026)
- "Runtime Identity Standard for Autonomous AI" — generally available
- Three components: Agent IAM Core, Agent Gateway, Agent Detection
- Establishes agent identity, enforces delegated authority at runtime, detects agentic activity

**A2Apex**
- First searchable directory of verified A2A-protocol agents
- Trust score: 0–100 with tiered badges (Gold, Silver, Bronze)
- Schema compliance checking + real JSON-RPC endpoint testing
- Focus: A2A protocol compliance verification only

### Emerging / Early-Stage Trust Infrastructure

**MolTrust** (Switzerland)
- Trust infrastructure for the AI agent economy: identity verification, reputation scoring, verifiable credentials
- Agents carry portable W3C verifiable credentials signed with Ed25519
- Reputation built from agent-to-agent ratings with anti-gaming protection
- Native Bitcoin Lightning integration (micropayments for trust services)
- Aligned with Singapore IMDA MGF for Agentic AI (2026)
- Has an MCP server on GitHub (early-stage, active development)

**Prova (Provatrust)**
- Hardware-backed attestation delivered as an API
- Proof of what ran, where data came from, how credentials were handled — without operating own TEE fleet
- Targets regulated industries needing hardware-level security and cryptographic auditability

**Klaimee** (YC, 2026)
- Certifies and insures autonomous AI agents
- Risk evaluation across 5 categories; certification badge; financial guarantee
- New entrant, very early stage

**AIUC — Artificial Intelligence Underwriting Company** (emerged July 2025, $15M seed)
- Investors: Nat Friedman/NFDG, Emergence, Terrain; angels include Anthropic co-founder Ben Mann
- AIUC-1 framework: pulls together NIST AI RMF, EU AI Act, MITRE ATLAS — agent-specific safeguards
- Three-pillar: standards + independent audits (5,000+ adversarial simulations) + liability insurance
- ElevenLabs: first company live with AIUC-1-backed policy (February 2026, covers AI voice agents)
- Other certified: Intercom, Ada, Alpharun, UiPath
- This is the closest existing model to "trust certification that unlocks higher-stakes deployment"

**Tumeryk AI Trust Score Report 2026**
- Published AI Trust Score framework; commercial product unclear but report is public

### Standards and Protocols

**IETF draft-sharif-agent-payment-trust-00** (R. Sharif, CyberSecAI Ltd, March 25, 2026)
- Proposes: five-dimension trust scoring model, per-agent ECDSA P-256 cryptographic identity, challenge-response verification, spend limit tiers derived from trust scores, anomaly detection for financial behavior, public trust query API
- "Agent Passport": cryptographic delegation certificate as pre-signed human authorization
- Status: Internet-Draft only — not a standard yet

**NIST AI Agent Standards Initiative** (February 2026)
- Launched by CAISI at NIST
- Focus areas: agent authentication, identity infrastructure, human-agent and multi-agent interactions
- Concept paper: "Accelerating the Adoption of Software and AI Agent Identity and Authorization"
- Standards under consideration: MCP, OAuth 2.0/2.1, OpenID Connect, SPIFFE/SPIRE, SCIM, NGAC

**Know Your Agent (KYA)** — emerging framework, multiple proponents
- Components: verifiable identity + authority binding + runtime controls + tamper-evident audit
- Framed as "KYC for bots" — directly addresses agentic commerce trust
- EU AI Act (August 2, 2026 deadline) effectively mandates KYA-style approaches for high-risk AI systems
- AgentFacts.org publishing KYA standard; adoption nascent

**ERC-8004** (deployed Ethereum mainnet January 29, 2026)
- Co-authored: MetaMask, Ethereum Foundation, Google, Coinbase engineers
- Three singleton registries with unique agentId + agentURI pointing to JSON metadata
- Created August 2025; on-chain agent identity for blockchain-native contexts

**W3C Verifiable Credentials + DIDs for agents**
- arxiv paper Nov 2025: "AI Agents with Decentralized Identifiers and Verifiable Credentials"
- Core problem: agents can't build differentiated trust at the onset of agent-to-agent dialogue
- Solution: DID anchored to ledger + third-party issued VCs in signed tamper-evident format
- Indicio's Proven AI for KYC: banks using VCs to authenticate customers during AI-assisted onboarding

**A2A Protocol** (Google, April 2025; now Linux Foundation)
- Open protocol for multi-agent interoperability across vendors
- HTTPS + role-based access control + zero-trust governance
- 28% of executives list lack of trust in AI agents as a top-three challenge (PwC)

**Cloud Security Alliance — Agentic Trust Framework** (February 2, 2026)
- Zero Trust governance model adapted for AI agents
- Continuous evaluation of identity and behavior

---

## 4. INFRASTRUCTURE GAPS — WHERE THE FLOOR IS MISSING

### The Pilot-to-Production Gap
- March 2026 survey: 78% of enterprises have AI agent pilots; under 15% reach production
- Five failure modes (89% of scaling failures): integration complexity, output inconsistency at volume, absent monitoring tooling, unclear organizational ownership, insufficient domain training data
- Only 11% of use cases made it to full production in 2025 (McKinsey)
- 99% of companies plan to put agents into production; only 11% have done so (financial services specific)

### Security and Authorization Gaps
- 82% of executives confident their policies protect against unauthorized agent actions
- Only 14.4% of organizations send agents to production with full security or IT approval
- 50% of deployed AI agents operate in complete isolation — can't share context or coordinate
- Gartner: 1 in 4 enterprise breaches could be tied to AI agent exploitation by 2028

### Trust Infrastructure Gaps (the core finding)
- No portable trust score that travels with an agent across platforms, vendors, or deployment contexts
- Current solutions are either: (a) siloed within one vendor ecosystem (Entra), (b) payment-layer only (Mastercard), (c) compliance/audit only with no runtime portability (AIUC-1), or (d) behavior detection only (HUMAN Security)
- IETF draft and MolTrust are the closest to "portable behavioral trust" — both very early
- The gap between "agent identity" (authentication) and "agent trustworthiness" (behavioral reputation) is not bridged by any production system
- 53% of leaders spend as long checking AI as using it — the "trust tax" is already being paid, informally, expensively

### Regulatory Gap Creating Demand
- EU AI Act August 2, 2026: high-risk AI agent requirements take full effect; penalties 7% global revenue or €35M
- Required: automatic logging of all agent actions (6-month minimum retention), human oversight mechanisms, agent registry with unique IDs and capability records
- HIPAA proposed updates: encryption now mandatory (not addressable) for all PHI data paths AI agents touch
- Financial services: Basel III, Fair Lending Act, SEC AI risk guidelines — all requiring model documentation
- Compliance demand is regulatory mandate, not optional market development

### Liability Gap
- When agents fail, existing insurance policies contain exclusions that don't map cleanly to probabilistic AI outputs
- Traditional CGL and E&O coverage not designed for autonomous agents
- AIUC and Klaimee are the only companies explicitly bridging this gap — both pre-scale
- "The trillion-dollar liability question nobody can answer" (WebPRONews headline, 2026)

---

## 5. WHERE A PORTABLE TRUST SCORE CREATES MONETARY VALUE

### Highest-Value Deployment Contexts

**Financial Transactions (immediate, largest)**
- AI agents are already executing trades, managing spend, initiating payments
- Mastercard Verifiable Intent addresses authorization proof but not behavioral reputation
- IETF draft explicitly calls out the gap: need spend limit tiers derived from trust scores
- Value mechanism: higher trust score = higher spend limits = more autonomous transaction volume
- The "Agent Passport" concept (IETF draft) is the clearest articulation of the need

**Procurement / B2B Purchasing**
- 60–70% of transactional procurement projected to be autonomous by 2028
- Suppliers need to trust inbound agents before accepting autonomous POs
- No current standard for "this agent has a clean purchase history"
- Value mechanism: trust score unlocks autonomous PO approval thresholds; lowers supplier friction cost

**Healthcare Data Access**
- PHI access is gated — every access event must be attributable, auditable, minimized
- HIPAA requires audit trails but has no interoperable standard for agent behavioral reputation
- An agent with a trust credential could get faster/broader PHI access; one without is blocked or requires human in loop
- Value mechanism: trust score replaces manual human oversight requirements for lower-risk access patterns

**Legal Contract Execution**
- Agents acting as "electronic agents" under UETA — legally binding but accountability unclear
- 78% of legal teams comfortable delegating first-pass review under attorney supervision; the "under supervision" requirement disappears with verified trust
- Value mechanism: verified trust credential reduces supervision overhead, enabling fully autonomous contract workflows

**Enterprise SaaS / Multi-Agent Orchestration**
- 50% of agents operate in isolation — can't coordinate
- Trust score enables inter-agent authority delegation without human intermediation
- Value mechanism: reduces the "human checkpoint tax" in multi-agent pipelines

### Who Would Pay

- **Enterprises deploying agents** — to unlock higher spend limits, reduce compliance burden, avoid EU AI Act penalties
- **Platforms hosting agents** — to offer differentiated "certified" vs "uncertified" agent tiers (AIUC model)
- **Insurers underwriting agent liability** — trust score = actuarial input for pricing (AIUC is already doing this)
- **Regulated industries** — healthcare, financial services, legal — where the alternative is manual human oversight at labor cost

---

## 6. DISCONFIRMATION — REASONS TO BE SKEPTICAL

- Only 6% of companies fully trust AI agents to run core business processes (HBR survey, late 2025)
- 77% of consumers remain concerned about AI agents acting on their behalf
- 73% of organizations admit a gap between what they want to do with agentic AI and what they can deploy
- 43% restrict agents to limited or routine operational tasks only
- Only 20% say their technology infrastructure is fully ready for agentic AI
- Gartner: over 40% of agentic AI projects will be canceled by end of 2027 without value and risk controls
- Trust scores face a fundamental measurement problem: behavior in controlled audit conditions may not predict behavior in production edge cases
- 28% of US organizations have zero confidence in the data quality feeding their LLMs/agents — trust scoring is only as good as the underlying agent reliability
- The IETF draft is one author's proposal — not a ratified standard
- All current trust infrastructure players are early-stage, fragmented, or siloed within a single ecosystem

---

## 7. KEY PLAYERS SUMMARY TABLE

| Player | Type | Focus | Stage | Notable |
|--------|------|--------|-------|---------|
| Mastercard + Google | Corp | Payment authorization trust | Production | Open standard, March 2026 |
| Microsoft Entra Agent ID | Corp | Enterprise identity management | Preview | Ecosystem-locked |
| Microsoft Agent Governance Toolkit | Corp/OSS | Runtime security + trust scoring | April 2026 launch | 0–1000 score, five tiers |
| Zenity | Startup | Enterprise agent security/governance | Commercial | RSA 2026 prominent |
| HUMAN Security | Corp | Behavioral traffic trust | Commercial | 1 quadrillion interactions analyzed |
| Ping Identity | Corp | Runtime identity standard | GA March 2026 | Three-component stack |
| AIUC | Startup | Standards + audit + insurance | $15M seed, July 2025 | Closest to trust-unlocks-liability model |
| Klaimee | Startup | Certification + insurance | YC, 2026 | Very early |
| MolTrust | Startup | Portable trust credentials | Early/active dev | Bitcoin Lightning + W3C VCs |
| Prova | Startup | Hardware-backed attestation API | Commercial | Regulated industries focus |
| A2Apex | Product | A2A protocol compliance scoring | Live | 0–100 score, badge tiers |
| NIST CAISI | Gov | Standards development | Active | Industry input phase |
| Cloud Security Alliance | Org | Agentic Trust Framework | Published Feb 2026 | Zero Trust adapted |

---

## 8. SOURCES

All findings sourced from live web searches conducted April 12, 2026.

- [Trust Scoring and Identity Verification for Autonomous AI Agent Payment Transactions — IETF Draft](https://datatracker.ietf.org/doc/html/draft-sharif-agent-payment-trust-00)
- [Mastercard Verifiable Intent](https://www.mastercard.com/global/en/news-and-trends/stories/2026/verifiable-intent.html)
- [Google Agent Payments Protocol (AP2) announcement](https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol)
- [Microsoft Zero Trust for AI](https://www.microsoft.com/en-us/security/blog/2026/03/19/new-tools-and-guidance-announcing-zero-trust-for-ai/)
- [Microsoft Agent Governance Toolkit](https://opensource.microsoft.com/blog/2026/04/02/introducing-the-agent-governance-toolkit-open-source-runtime-security-for-ai-agents/)
- [Microsoft Entra Agent ID](https://learn.microsoft.com/en-us/entra/agent-id/)
- [Ping Identity Runtime Identity Standard](https://press.pingidentity.com/2026-03-24-Ping-Identity-Defines-the-Runtime-Identity-Standard-for-Autonomous-AI)
- [NIST AI Agent Standards Initiative](https://www.nist.gov/news-events/news/2026/02/announcing-ai-agent-standards-initiative-interoperable-and-secure)
- [NIST NCCoE Concept Paper on Agent Identity](https://www.nccoe.nist.gov/sites/default/files/2026-02/accelerating-the-adoption-of-software-and-ai-agent-identity-and-authorization-concept-paper.pdf)
- [Zenity AI Agent Security at RSA 2026](https://zenity.io/blog/events/rsa-2026-ai-agent-security-market)
- [HUMAN Security 2026 State of AI Traffic Report](https://www.humansecurity.com/learn/resources/2026-state-of-ai-traffic-cyberthreat-benchmarks/)
- [MolTrust Trust Infrastructure](https://moltrust.ch/)
- [Prova Attestation as a Service](https://www.provatrust.com/)
- [AIUC — AI Agent Standard and Insurance](https://aiuc.com/)
- [AIUC $15M seed — Fortune](https://fortune.com/2025/07/23/ai-agent-insurance-startup-aiuc-stealth-15-million-seed-nat-friedman/)
- [ElevenLabs first AIUC-1 policy](https://elevenlabs.io/blog/aiuc-announcement)
- [Klaimee YC](https://www.ycombinator.com/companies/klaimee)
- [Cloud Security Alliance Agentic Trust Framework](https://cloudsecurityalliance.org/blog/2026/02/02/the-agentic-trust-framework-zero-trust-governance-for-ai-agents)
- [A2Apex — A2A Agent Trust Scoring](https://a2apex.io/)
- [A2A Protocol — Linux Foundation](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents)
- [Know Your Agent (KYA) — AgentFacts](https://agentfacts.org/kya)
- [KYA in 2026 — Stable Coin Insider](https://stablecoininsider.org/know-your-agent-kya-in-2026/)
- [KYA — PYMNTS](https://www.pymnts.com/artificial-intelligence-2/2026/the-kya-moment-why-knowing-your-agent-is-becoming-table-stakes/)
- [AI Agents with DIDs and Verifiable Credentials — arxiv](https://arxiv.org/abs/2511.02841)
- [Why Verifiable Credentials Will Power AI in 2026 — Indicio](https://indicio.tech/blog/why-verifiable-credentials-will-power-ai-in-2026/)
- [EU AI Act — What AI Agents Must Prove by August 2](https://centurian.ai/blog/eu-ai-act-compliance-2026)
- [EU AI Act Agentic AI Governance Challenges](https://www.artificialintelligence-news.com/news/agentic-ais-governance-challenges-under-the-eu-ai-act-in-2026/)
- [AI Agent Scaling Gap — Pilot to Production](https://www.digitalapplied.com/blog/ai-agent-scaling-gap-march-2026-pilot-to-production)
- [Agentic AI Infrastructure Gap](https://www.distributedthoughts.org/2026-02-05-agentic-ai-infrastructure-gap/)
- [Digital Trust Index 2026 — Thales](https://cpl.thalesgroup.com/about-thalesgroup/newsroom/digital-trust-index-2026-ai-skepticism-identity-access-friction)
- [State of AI Trust 2026 — McKinsey](https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/tech-forward/state-of-ai-trust-in-2026-shifting-to-the-age-of-agents)
- [WEF: AI Agents Could Be Worth $236B](https://www.weforum.org/stories/2026/01/ai-agents-trust/)
- [Agentic AI in Financial Services 2026 — Neurons Lab](https://neurons-lab.com/article/agentic-ai-in-financial-services-2026/)
- [AI Agent Trends in Financial Services 2026 — Google Cloud](https://cloud.google.com/resources/content/ai-agent-trends-financial-services-2026)
- [Towards a HIPAA Compliant Agentic AI System in Healthcare — arxiv](https://arxiv.org/abs/2504.17669)
- [AIUC-1 First AI Agent Security Standard](https://dev.to/custodiaadmin/aiuc-1-is-the-first-ai-agent-security-standard-heres-what-compliance-evidence-looks-like-5enl)
- [Oracle Financial Crime and Compliance AI Agents](https://www.oracle.com/news/announcement/oracle-brings-new-ai-capabilities-and-agents-to-its-financial-crime-and-compliance-portfolio-2026-04-09/)
- [Contract Law in the Age of Agentic AI — Proskauer](https://www.proskauer.com/blog/contract-law-in-the-age-of-agentic-ai-whos-really-clicking-accept)
- [When AI Agents Break Things Who Pays — WebProNews](https://www.webpronews.com/when-ai-agents-break-things-who-pays-the-trillion-dollar-liability-question-nobody-can-answer/)
- [AI Agent Economy Market Size — Agentic AI — Fortune Business Insights](https://www.fortunebusinessinsights.com/agentic-ai-market-114233)
- [MCP Rise and Monetization 2026 — Medium](https://medium.com/mcp-server/the-rise-of-mcp-protocol-adoption-in-2026-and-emerging-monetization-models-cb03438e985c)
- [Agent Skills — Anthropic next standard bid — The New Stack](https://thenewstack.io/agent-skills-anthropics-next-bid-to-define-ai-standards/)
- [AI Agent Liability Insurance — State AI Bills 2026](https://www.wiley.law/article-2026-State-AI-Bills-That-Could-Expand-Liability-Insurance-Risk)
