# Docs & Standards Research — AI Agent Trust, Identity, and Verification
**Researcher role:** Docs & Standards (official sources only)
**Date:** April 12, 2026
**Project:** Submantle

---

## Research Question
What official standards, protocols, and regulations exist or are emerging for AI agent trust, identity, and verification? Where do regulations MANDATE trust verification, creating guaranteed demand?

---

## 1. Agent Protocol Standards

### Model Context Protocol (MCP) — Authorization Layer
- **Source:** https://modelcontextprotocol.io / https://modelcontextprotocol.io/docs/tutorials/security/authorization
- MCP's identity/trust model is built entirely on **OAuth 2.1** — it specifies no behavioral trust layer, only credential-based access control (Bearer tokens, PKCE, authorization code grant).
- The spec (2025-11-25 release) covers Protected Resource Metadata, Authorization Server discovery, Dynamic Client Registration, and token scoping. It does NOT define agent identity beyond OAuth tokens.
- MCP was donated to the **Agentic AI Foundation (AAIF)** under the Linux Foundation in December 2025.
- **Gap for Submantle:** MCP defines HOW an agent authenticates, not WHETHER the agent is behaviorally trustworthy. OAuth says "this token is valid," not "this agent behaves reliably."

### Agent2Agent Protocol (A2A) — Identity Preservation in Multi-Agent
- **Source:** https://a2a-protocol.org/latest/specification/ / https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/
- Announced by Google at Cloud Next April 2025; donated to the Linux Foundation June 2025.
- Technical Steering Committee includes Google, Microsoft, AWS, IBM, Salesforce, SAP.
- A2A uses **Agent Cards** for structured discovery, and **On-Behalf-Of (OBO) pattern** — tokens scoped per task, expiring in minutes, identifying both the user AND the acting agent.
- Supports OAuth 2.0, API Keys, and mTLS. Version 0.3 adds gRPC and signed Agent Cards.
- **Gap for Submantle:** A2A establishes cryptographic agent identity but contains no behavioral history or cross-deployment trust record. Short-lived tokens prevent portable reputation.

### W3C — Verifiable Credentials + DID Standards
- **Sources:**
  - https://www.w3.org/TR/vc-data-model-2.0/
  - https://www.w3.org/TR/did-1.1/
  - https://www.w3.org/groups/cg/agentprotocol/
- W3C Verifiable Credentials v2.0 and DIDs v1.1 are finalized W3C Recommendations.
- The **W3C AI Agent Protocol Community Group** (launched May 2025) is actively building an agent identity model based on open standards, including VC-based trust and cross-origin authentication.
- Cross-origin communication security for agents, including VC-based trust, is explicitly scoped into the CG's work.
- **Relevance:** VCs provide a cryptographic container for carrying claims about an agent. Submantle's behavioral attestation could be expressed as a Verifiable Credential issued to an agent DID.

### OpenID Foundation — OIDC-A and Agentic AI Identity
- **Sources:**
  - https://arxiv.org/abs/2509.25974 (OIDC-A 1.0 proposal)
  - https://openid.net/wp-content/uploads/2025/10/Identity-Management-for-Agentic-AI.pdf
- **OpenID Connect for Agents (OIDC-A) 1.0** (September 2025 proposal): extends OIDC Core 1.0 to define standard claims, endpoints, and protocols for:
  - Agent identity
  - Agent attestation verification
  - Delegation chains
  - Fine-grained authorization based on agent attributes
- OpenID Foundation published whitepaper "Identity Management for Agentic AI" (October 2025), identifying authentication, authorization, and identity management as foundational gaps for autonomous systems.
- OpenID Foundation self-certification program launching February 2026 covers specifications that include agentic use cases.
- **Gap for Submantle:** OIDC-A defines identity and delegation structure but does not define behavioral trust scoring or cross-deployment behavioral evidence.

### IETF OAuth Drafts for AI Agents
- **Sources:**
  - https://datatracker.ietf.org/doc/html/draft-oauth-ai-agents-on-behalf-of-user-01
  - https://www.ietf.org/archive/id/draft-patwhite-aauth-00.html
  - https://datatracker.ietf.org/doc/draft-song-oauth-ai-agent-authorization/
- Three active IETF Internet-Drafts (2025) targeting AI agent authorization:
  1. **On-Behalf-Of User Authorization** — requested_actor and actor_token parameters for agents acting for users
  2. **AAuth (Agentic Authorization)** — OAuth 2.1 extension for agents with long-lived identities and scoped natural-language descriptions
  3. **Authorization on Target** — target_id field for per-target agent authorization
- None of these drafts are finalized RFCs. All address credentials, not behavioral evidence.

### SPIFFE/SPIRE — Workload Identity Attestation
- **Source:** https://spiffe.io/docs/latest/spire-about/spire-concepts/
- SPIFFE defines workload identity for software systems; SPIRE is the production implementation.
- Performs two-phase attestation: node attestation (is this the right machine?) and workload attestation (is this the right process?).
- Issues short-lived SVIDs (SPIFFE Verifiable Identity Documents) — cryptographic workload identity.
- Used in cloud-native infrastructure; increasingly applied to AI agent deployments.
- **Gap:** SPIFFE proves "this is process X on node Y," not "this agent behaves reliably across deployments."

### Agentic AI Foundation (AAIF)
- **Source:** https://aaif.io / https://www.techzine.eu/news/applications/139057/agentic-ai-foundation-the-home-of-mcp-grows-to-146-members/
- Launched December 2025 by Anthropic, OpenAI, Block; now 146 members including American Express, JPMorgan Chase, Red Hat, Cisco, ServiceNow, UiPath.
- Stewards MCP, Goose (Block), AGENTS.md (OpenAI) under Linux Foundation governance.
- Mission: open standards for agent interoperability, avoiding fragmentation.
- **No behavioral trust standard exists under AAIF yet.** The gap is documented in the consortium's roadmap discussions.

---

## 2. Regulatory Requirements

### EU AI Act — Transparency Obligations
- **Sources:**
  - https://artificialintelligenceact.eu/article/50/
  - https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50
- **Article 50** (not 52) governs transparency obligations for AI systems interacting with people.
- Applies since August 2024 (high-risk provisions phased in through 2026).
- Requirements: disclose AI identity to users, disclose deepfake generation, disclose emotion recognition.
- Applies to deployers of AI systems — which includes organizations deploying AI agents in customer-facing contexts.
- Does NOT mandate behavioral verification between agents in multi-agent pipelines — a regulatory gap.

### NIST AI Risk Management Framework
- **Sources:**
  - https://www.nist.gov/itl/ai-risk-management-framework
  - https://www.nist.gov/programs-projects/concept-note-ai-rmf-profile-trustworthy-ai-critical-infrastructure
  - https://nvlpubs.nist.gov/nistpubs/ir/2025/NIST.IR.8596.iprd.pdf
- **February 2026:** NIST released the AI Agent Standards Initiative — officially declaring AI governance has entered the "agent era." Strategic extension of AI RMF 1.0 and Generative AI Profile (AI 600-1).
- **April 7, 2026:** NIST released concept note for AI RMF Profile on Trustworthy AI in Critical Infrastructure — guides critical infrastructure operators on risk management for AI agents.
- RMF characteristics emphasized for agents: reliability, safety, security, explainability, privacy, fairness, transparency, accountability, robustness.
- NIST IR 8596 (initial public draft 2025): Cybersecurity Framework Profile — directly addresses AI agent security.
- **Mandate signal:** Critical infrastructure sectors (energy, finance, healthcare, transport) will be directed to apply the AI Agent Standards Initiative to their agent deployments.

### Financial Services — SEC, FCA
- **SEC:**
  - Source: https://www.sec.gov/newsroom/speeches-statements/daly-020326-artificial-intelligence-future-investment-management
  - SEC launched AI Task Force August 2025; Valerie Szczepanik designated Chief AI Officer.
  - 2025 examination priorities expanded AI oversight — firms must demonstrate adequate policies and procedures for AI monitoring and supervision.
  - Proposed predictive data analytics rule withdrawn June 12, 2025 (regulatory rollback under current administration).
  - December 2025: Investor Advisory Committee recommended mandatory AI disclosure guidance.
  - **Status:** Active oversight but no specific agent identity mandate yet. Firms deploying autonomous trading agents face supervisory risk under existing market manipulation rules.

- **FCA (UK):**
  - Source: https://www.fca.org.uk/firms/ai-financial-services
  - FCA explicitly uses principles-based approach — no AI-specific rules. Consumer Duty (active) requires empirical proof of good outcomes.
  - AI Live Testing cohort 2 launching April 2026.
  - **PS25/22 "targeted support" framework (April 2026):** First regulatory framework creating compliant pathway for automated financial guidance — AI restricted to segment assignment, mandatory disclosures.
  - House of Commons Treasury Committee recommended FCA publish comprehensive AI guidance by end of 2026.
  - **Mandate signal:** Consumer Duty creates de facto audit trail requirement for AI agent decisions affecting consumers.

### Healthcare — HIPAA
- **Source:** https://www.kiteworks.com/hipaa-compliance/ai-agents-hipaa-phi-access/
- 2025 Security Rule amendments directly address AI agent deployments:
  - Mandatory encryption for all PHI data paths an AI agent touches (no longer "addressable")
  - Risk assessments must explicitly address AI agents (omitting them renders assessment non-compliant)
  - Operation-level audit logs required — "which agent accessed which PHI, what did it do, who authorized"
- 73% of healthcare AI implementations reportedly fail HIPAA Technical Safeguards requirements.
- **Hard mandate:** BAA required for any AI vendor processing PHI. Audit trail of agent actions is a legal requirement, not optional.

### ISO 42001 — AI Management System
- **Source:** https://www.iso.org/standard/42001
- Published December 2023; certification market active through 2025-2026.
- Requires governance structures, risk management strategies, compliance protocols for AI systems.
- Third-party conformity assessment required for certification.
- Does not specify behavioral trust scores or inter-agent verification, but requires documented accountability for AI system behavior.
- **Mandate signal:** Becoming table-stakes for enterprise AI vendor procurement — analogous to ISO 27001 for information security.

---

## 3. Market Sizing (Official Sources)

### McKinsey — Agentic AI Governance 2026
- Source: https://www.mckinsey.com/capabilities/risk-and-resilience/our-insights/trust-in-the-age-of-agents
- "With agentic AI, you can't govern what you can't see. If you don't inventory it and identity bind it, you're not scaling agents; you're scaling unknown risk."
- Average Responsible AI maturity score: 2.3/5 (up from 2.0 in 2025). Only one-third of organizations report maturity level 3+ in agentic AI governance.
- Organizations now face systems "doing the wrong thing" — unintended actions, tool misuse, operating beyond guardrails.
- AI agents market: ~$12-15B in 2025 → $80-100B by 2030.

### McKinsey — State of AI Trust 2026
- Source: https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/tech-forward/state-of-ai-trust-in-2026-shifting-to-the-agentic-era
- Trust maturity gap is documented at scale: most organizations lack agentic governance capability.

---

## 4. Existing Behavioral Certification (Market Precedent)

### ACF Standards — Agent Certification Framework
- Source: https://acfstandards.org/
- Independent behavioral certification platform for AI agents (not model-level, agent-as-deployed).
- 30 behavioral tests across 4 suites: Commitment Boundary, Consistency, Hallucination Detection, Adversarial Resistance.
- Public certificate registry with scores and tier — verifiable third-party attestation.
- Targets procurement workflows: "prerequisite before AI vendor conversations begin."
- **Direct market signal:** A for-profit behavioral certification market is already forming. ACF is the earliest known entrant.

---

## 5. Disconfirmation Search — Arguments Against Portable Behavioral Trust

### What official sources say against portable trust scores:

1. **Behavioral intent vs. actual behavior gap** (ACM FAccT 2025 — https://dl.acm.org/doi/10.1145/3715275.3732025): Measuring behavioral intent has documented limitations vs. measuring actual behavior; external variables prevent prediction.

2. **Asymmetric trust dynamics** (PMC research): AI trust loss occurs faster than trust building; a single failure can erase a score's value rapidly.

3. **Context-dependence of behavior**: MCP, A2A, and OIDC-A all assume per-deployment identity. A behavioral score from Deployment A may not transfer to Deployment B with different system prompts, tools, and data.

4. **Regulatory preference for process over scores**: EU AI Act, HIPAA, FCA Consumer Duty all mandate audit trails and process documentation — not portable scores. Regulators prefer inspectable evidence chains over summary numbers.

5. **No regulatory mandate for portable behavioral scores exists.** Current mandates are for: audit logs (HIPAA), disclosure (EU AI Act), risk documentation (NIST/ISO 42001), supervisory procedures (SEC/FCA). The scores themselves are not mandated — only the underlying evidence they would aggregate.

---

## 6. Key Findings Summary

### What exists (official standards):
- **Credential-based identity:** MCP (OAuth 2.1), A2A (OBO + Agent Cards), SPIFFE (workload attestation), OIDC-A (agent identity claims), multiple IETF drafts — all address WHO the agent is, not HOW it behaves.
- **Behavioral certification (emerging):** W3C AI Agent Protocol CG (VC-based trust), ACF Standards (deployed agent testing), NIST AI Agent Standards Initiative (February 2026).
- **Regulatory audit requirements:** HIPAA (operation-level logs, mandatory), EU AI Act (disclosure, mandatory), ISO 42001 (governance documentation, certifiable), NIST AI RMF (critical infrastructure guidance).

### The documented gap:
All current official standards address identity (who is this agent?) and access (what is this agent allowed to do?). None define a portable, cross-deployment behavioral trust record. The AAIF, W3C CG, and NIST Agent Standards Initiative all have this gap in scope but no published specification fills it.

### Where regulations CREATE demand:
| Regulation | Mandate | Agent Trust Demand Created |
|---|---|---|
| HIPAA 2025 Security Rule | Operation-level agent audit logs | Verified behavioral audit trail per agent |
| EU AI Act Article 50 | Disclose AI identity to users | Agent identity attestation layer |
| FCA Consumer Duty | Prove agent decisions led to good outcomes | Behavioral evidence records |
| NIST AI Agent Standards Initiative | Critical infrastructure AI risk management | Verifiable agent risk profile |
| ISO 42001 | Third-party AI governance certification | Documented agent behavior standards |
| SEC examination priorities | Supervisory procedures for AI | Agent behavioral audit capability |

### Redundancy risk (disconfirmation):
- MCP + A2A + OIDC-A together cover credential identity and session authorization comprehensively. If behavioral trust is folded into OIDC-A agent attestation claims as the spec matures, that could reduce Submantle's differentiation on the identity side.
- The ACF Standards offering (behavioral certification) is a direct competitive precedent — market is not unoccupied.

---

## Sources

- [MCP Authorization Tutorial](https://modelcontextprotocol.io/docs/tutorials/security/authorization)
- [MCP OAuth Client Registration Blog](https://blog.modelcontextprotocol.io/posts/client_registration/)
- [A2A Protocol Specification](https://a2a-protocol.org/latest/specification/)
- [Google A2A Announcement](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)
- [A2A Protocol Upgrade Blog](https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade)
- [W3C Verifiable Credentials v2.0](https://www.w3.org/TR/vc-data-model-2.0/)
- [W3C DID v1.1](https://www.w3.org/TR/did-1.1/)
- [W3C AI Agent Protocol Community Group](https://www.w3.org/community/agentprotocol/)
- [OIDC-A 1.0 Proposal (arXiv)](https://arxiv.org/abs/2509.25974)
- [OpenID Foundation Identity Management for Agentic AI Whitepaper](https://openid.net/wp-content/uploads/2025/10/Identity-Management-for-Agentic-AI.pdf)
- [IETF OAuth On-Behalf-Of AI Agents Draft](https://datatracker.ietf.org/doc/html/draft-oauth-ai-agents-on-behalf-of-user-01)
- [IETF AAuth Draft](https://www.ietf.org/archive/id/draft-patwhite-aauth-00.html)
- [IETF OAuth AI Agent Authorization Draft](https://datatracker.ietf.org/doc/draft-song-oauth-ai-agent-authorization/)
- [SPIFFE SPIRE Concepts](https://spiffe.io/docs/latest/spire-about/spire-concepts/)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [NIST AI RMF Critical Infrastructure Concept Note](https://www.nist.gov/programs-projects/concept-note-ai-rmf-profile-trustworthy-ai-critical-infrastructure)
- [NIST IR 8596 Cybersecurity Framework Profile (PDF)](https://nvlpubs.nist.gov/nistpubs/ir/2025/NIST.IR.8596.iprd.pdf)
- [EU AI Act Article 50 (Transparency)](https://artificialintelligenceact.eu/article/50/)
- [EU AI Act Transparency Guidelines](https://digital-strategy.ec.europa.eu/en/faqs/guidelines-and-code-practice-transparent-ai-systems)
- [FCA AI Approach](https://www.fca.org.uk/firms/innovation/ai-approach)
- [FCA AI in Financial Services](https://www.fca.org.uk/firms/ai-financial-services)
- [UK Financial Services Regulators AI 2026](https://www.insideglobaltech.com/2026/04/09/uk-financial-services-regulators-approach-to-artificial-intelligence-in-2026/)
- [SEC AI Future of Investment Management](https://www.sec.gov/newsroom/speeches-statements/daly-020326-artificial-intelligence-future-investment-management)
- [Microsoft Entra Agent ID](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/what-is-agent-id)
- [Microsoft Entra Agent ID Overview](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/agent-identities)
- [HIPAA AI Agents PHI Access](https://www.kiteworks.com/hipaa-compliance/ai-agents-hipaa-phi-access/)
- [HIPAA Agentic AI Healthcare arXiv](https://arxiv.org/html/2504.17669v1)
- [ISO 42001 AI Management System](https://www.iso.org/standard/42001)
- [McKinsey Trust in the Age of Agents](https://www.mckinsey.com/capabilities/risk-and-resilience/our-insights/trust-in-the-age-of-agents)
- [McKinsey State of AI Trust 2026](https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/tech-forward/state-of-ai-trust-in-2026-shifting-to-the-agentic-ea)
- [McKinsey Securing the Agentic Enterprise](https://www.mckinsey.com/capabilities/risk-and-resilience/our-insights/securing-the-agentic-enterprise-opportunities-for-cybersecurity-providers)
- [ACF Standards — Behavioral Certification](https://acfstandards.org/)
- [AAIF 146 Members](https://www.techzine.eu/news/applications/139057/agentic-ai-foundation-the-home-of-mcp-grows-to-146-members/)
- [AAIF Press Release 97 New Members](https://aaif.io/press/agentic-ai-foundation-welcomes-97-new-members-as-demand-for-open-collaborative-agent-standardization-increases/)
- [ACM FAccT AI Trust Questionnaire 2025](https://dl.acm.org/doi/10.1145/3715275.3732025)
