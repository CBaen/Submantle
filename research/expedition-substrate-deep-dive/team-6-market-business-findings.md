# Team 6 Findings: Market, Customers & Business Model
## Date: 2026-03-10
## Researcher: Team Member 6

---

### Battle-Tested Approaches

- **Infrastructure middleware SaaS (per seat + usage tiers)**
  - Evidence: Datadog $3.43B revenue in 2025 (27.7% YoY growth), 4,310 enterprise customers at $100k+ ARR, 603 at $1M+ ARR. Started as a dev-friendly agent → grew upmarket. Pro at ~$15/host/month, Enterprise at ~$23/host/month. Enterprise deals routinely $50k–$1M+/year.
  - Source: Datadog Q4 2025 10-K SEC filing, Macrotrends, AlphaStreet
  - Fits our case: Substrate IS infrastructure middleware. Datadog proves the path from developer adoption → enterprise expansion. Process/environment monitoring is Datadog's founding use case — Substrate is its evolutionary successor for AI agents.
  - Tradeoffs: Datadog's usage-based billing creates "surprise bills." Substrate should consider predictable pricing to avoid the same reputation problem.

- **Security-layer per-seat SaaS (freemium → business → enterprise)**
  - Evidence: 1Password runs free tier → Teams Starter $19.95/month flat → Business $7.99/user/month → Enterprise (custom). Revenue path: cross-platform middleware position locks in users who integrate across all apps, driving high switching costs.
  - Source: 1Password.com pricing, Cybernews 2026 review, CloudEagle
  - Fits our case: Substrate, like 1Password, is a cross-platform ambient layer. The integration moat (once agents use the Substrate API, switching costs are high) mirrors the browser-extension integration moat 1Password built.
  - Tradeoffs: Per-seat pricing favors individual/SMB; doesn't capture per-agent value at enterprise scale where one user might run 50 agents.

- **Freemium infrastructure networking (free personal → per-user business → enterprise custom)**
  - Evidence: Tailscale: free personal (3 users, 100 devices), Starter $6/user/month, Premium $18/user/month, Enterprise custom. Explicitly designed for "personal value, self-serve team value, enterprise top-down value" — three distinct buyer archetypes.
  - Source: Tailscale.com pricing, Tailscale blog "How our free plan stays free," G2 2026
  - Fits our case: Tailscale's three-tier buyer model maps cleanly to Substrate's own three segments: power user, developer/team, enterprise. Their principle of not making users the product aligns with Substrate's privacy-first positioning.
  - Tradeoffs: Tailscale is still mostly developer-adopted; enterprise direct sales is a harder motion.

- **Identity middleware (per-user per-month, usage-based for developer tier)**
  - Evidence: Okta Workforce: $6/user/month starter → $17/user/month essentials → Enterprise custom. Auth0: free → $240/month flat for SMB → enterprise custom. Auth0 went from developer-first authentication SDK to the identity layer baked into millions of apps. Okta acquired them for $6.5B.
  - Source: Okta.com pricing, GetMonetizely 2024, FusionAuth "IDP tax" analysis
  - Fits our case: Substrate's Agent API is precisely analogous to Auth0's authentication API — a mandatory query before an agent acts, just as auth is a mandatory check before a user accesses a resource. The acquisition path (Auth0 → Okta, ~$6.5B) validates the middleware acquisition thesis.
  - Tradeoffs: Auth0/Okta monetize at the application layer (per end user). Substrate needs a per-agent or per-query model, which has no exact precedent.

- **Developer-first PLG → enterprise top-down**
  - Evidence: Datadog self-service drives 25%+ of new customers; 2,000-person sales team handles enterprise expansion. Stripe, Twilio, Snyk all followed identical pattern: frictionless developer adoption → bottom-up enterprise land → top-down expansion. Snyk: $343M ARR in 2025 at $25/developer/month (Team) to custom (Enterprise), started as a free CLI tool.
  - Source: Datadog Q4 2025 call, Sacra Snyk $300M ARR analysis, Snyk.io pricing, Decibel VC MuleSoft case study
  - Fits our case: AI agent developers (the builders at LangChain, CrewAI, AutoGen shops) are Substrate's Stripe moment. They integrate the API early when it's free. Their employers then need the enterprise tier.
  - Tradeoffs: PLG requires a compelling free tier that delivers real value without destroying commercial upside. Timing the PLG → enterprise upgrade gate is the hardest strategic decision.

---

### Novel Approaches

- **Per-agent subscription (agent-count billing, not per-user)**
  - Why interesting: As enterprises run hundreds or thousands of AI agents, per-user pricing collapses (one IT admin "uses" 500 agents). Billing per managed agent — similar to per-host in Datadog — captures actual value delivered. At $5/agent/month, 100 agents = $500/month; 1,000 agents = $5,000/month.
  - Evidence: No product currently bills this way for safety middleware. Anthropic's Frontier enterprise platform mentions "per agent" orchestration but no published pricing. Agentic AI governance market at $7.28B in 2025 → $38.94B by 2030 (39.85% CAGR).
  - Source: Mordor Intelligence Agentic AI Governance report, Anthropic Frontier platform announcement
  - Fits our case: Substrate's core value — brokering agent actions — scales directly with number of agents. This aligns price to value perfectly.
  - Risks: Enterprises resist variable costs that grow with AI adoption. Could create perverse incentive to avoid deploying agents. Mitigated by tiered caps.

- **AI liability insurance premium reduction (compliance-as-a-feature)**
  - Why interesting: AIUC (AI Underwriting Company) raised $15M seed in July 2025 explicitly to build AI agent insurance infrastructure. 2026 state AI liability laws are expanding. Enterprises paying cyber insurance premiums for AI incidents would pay more for Substrate if it demonstrably reduces their risk profile.
  - Evidence: Major insurers are building "near miss" databases for AI incidents. WTW (Willis Towers Watson) 2025 report: insurers offering discounts for documented AI governance frameworks. AIUC's AIUC-1 framework specifically targets AI agent certification.
  - Source: Fortune (AIUC seed round July 2025), WTW "Insuring the AI Age" Dec 2025, Wiley Law 2026 state AI bills, Insurance Business Mag cyber insurance AI era
  - Fits our case: Substrate's audit log of agent queries is a compliance artifact. A "Substrate Verified" certification could command premium pricing AND be the evidence insurers require for discounts. Indirect revenue through reduced insurance costs is a strong enterprise purchasing argument.
  - Risks: Insurance industry moves slowly. Certification requires third-party validation infrastructure that doesn't yet exist. Medium-term play, not launch strategy.

- **Agent framework SDK integration (baked-in, not bolted-on)**
  - Why interesting: LangChain (Apache 2.0), CrewAI (MIT), LlamaIndex, AutoGen are the pipes every AI agent runs through. If Substrate ships an official LangChain integration that makes the broker API a one-line addition to any agent, adoption could follow MCP's growth trajectory — MCP went from 100k → 8M server downloads in 5 months after framework adoption.
  - Evidence: MCP achieved universal adoption (OpenAI, Google, Microsoft, 97M SDK downloads/month, 5,800+ servers) by becoming the standard embedded in developer tools. LangSmith, CrewAI Enterprise, AutoGen Azure all built commercial layers on open-source cores.
  - Source: Wikipedia MCP article, Pento "A Year of MCP" review, CData "2026: Year of Enterprise MCP Adoption," various framework comparison articles
  - Fits our case: Substrate's Agent API is complementary to MCP, not competitive. MCP handles what data the agent sees; Substrate handles what the agent is allowed to do with it. A co-positioning strategy ("MCP tells agents what's available, Substrate tells agents what's safe") is compelling.
  - Risks: Framework fragmentation could require maintaining multiple integrations. Open-source contribution builds awareness but requires a clear commercial gate.

---

### Emerging Approaches

- **Cloudflare's "pay-to-act" middleware model**
  - What: Cloudflare launched Pay Per Crawl in July 2025 — AI bots must pay to access content, with Cloudflare as the broker. More broadly, Cloudflare is positioning itself as the middleware layer for agentic commerce: agents run on Workers, route through AI Gateway, get rate-limited, cached, and observed. Revenue follows the action, not the identity.
  - Momentum: Cloudflare Q4 2025 beat revenue and EPS forecasts. Workers platform and AI Gateway are its fastest-growing segments. Source: CNBC Q4 2025 earnings, Alpha-Sense analysis, Medium PM Breakdown piece.
  - Fits our case: Substrate could charge per broker query — $0.001 per agent check at millions of queries/day = meaningful revenue. Like Cloudflare, the value is in the act of brokering, not just presence.
  - Maturity risk: Per-query pricing at micro-scale requires significant volume and frictionless integration before it's viable. Not a launch model.

- **Agentic observability as a platform (Zenity, Fiddler AI positioning)**
  - What: Zenity and Fiddler AI have emerged in 2025 as dedicated "AI agent security posture management" tools. Zenity monitors agent behavior at runtime, flags prompt injection, data leaks, over-permissioned actions. Fiddler offers an "AI Control Plane" with observability and guardrails. Both are enterprise-only, custom pricing.
  - Momentum: Zenity is in Forrester's AI Governance Solutions Landscape Q2 2025. Fiddler recently repositioned from ML monitoring to agentic observability. Source: Obsidian Security "2025 AI Agent Security Landscape," Zenity.io, Fiddler.ai.
  - Fits our case: These are the closest existing competitors to Substrate's vision — but they sit at the application layer (monitoring agent behavior AFTER the fact) not the OS layer (providing context BEFORE the agent acts). Substrate's positioning as pre-action context vs. post-action monitoring is a meaningful differentiator.
  - Maturity risk: If Zenity or Fiddler pivots to pre-action brokering, they could compete directly. First-mover at the OS layer matters.

- **Open-source core + commercial enterprise (GitLab/Grafana model)**
  - What: Grafana OSS is free; Grafana Cloud starts at free and scales to enterprise. GitLab has Community and Enterprise editions. Both monetize the operational layer around an open core: compliance, SSO, audit logs, support, hosted infrastructure.
  - Momentum: Multiple analyst pieces in 2025 confirm open-source + PLG as the dominant GTM for infrastructure developer tools. PLG drives 25-40% of new customer acquisition for companies that execute it well. Source: ProductMarketingAlliance, Decibel VC MuleSoft analysis, Qodo blog.
  - Fits our case: Substrate's daemon/local engine could be fully open source. Enterprise tier adds: compliance audit exports, centralized policy management, cross-device cloud sync, priority support, and the forthcoming AI liability certification. Privacy-first positioning is reinforced, not undermined, by open-sourcing the local component.
  - Maturity risk: Open source creates forks. The commercial gate must be something organizations genuinely need (compliance, support, cloud), not an artificial feature lock.

---

### Gaps and Unknowns

1. **No direct comp exists.** The "pre-action OS-layer context broker for AI agents" is a genuinely empty category in March 2026. Zenity/Fiddler monitor post-hoc; Apple Intelligence/Recall are passive; MCP provides tools context, not safety context. This means pricing must be discovered, not copied.

2. **Agent count at enterprise is unknowable yet.** Gartner: 40% of enterprise apps will have embedded agents by end of 2026, up from <5% in 2025. But how many agents per enterprise? At what concurrency? This determines whether per-agent or per-seat pricing wins.

3. **Developer willingness to add a mandatory pre-action query is unproven.** Auth0 succeeded because auth was already a regulatory/security requirement. Substrate needs to become similarly necessary — either through regulation, insurance requirements, or a high-profile incident that makes "we didn't use Substrate" a liability. The AIUC partnership angle could accelerate this.

4. **OS vendor threat is real but slow.** Apple Intelligence and Microsoft Recall are both inching toward Substrate's territory from the platform side. Microsoft's Copilot + Recall could evolve into a broker layer. Timeline: 2-4 years before they're competitive. Substrate needs to be the standard before they get there.

5. **Privacy-first creates a paradox for the data insights revenue model.** Anonymized aggregate data about what agents are doing across millions of installs would be extraordinarily valuable. But Substrate's core trust proposition is "we don't sell your data." This model cannot be pursued without destroying the brand. Ruled out.

6. **First segment to target is unclear.** Individual developers have low friction but low revenue. Enterprises have high revenue but slow sales cycles. Agent framework companies (LangChain, CrewAI) have high leverage but are gate-keeper risks. Research does not yield a definitive answer — this requires a founder decision.

---

### Synthesis

**The single most important finding:** Substrate is entering a $7.28B governance market growing at 40% CAGR with no direct competitor at its layer. Every analog (Datadog, 1Password, Auth0, Cloudflare, Tailscale) became a category-defining company by owning the middleware position first and monetizing it second. All of them started with developers, not enterprises.

**Who pays, and how much:**

| Segment | Mechanism | Price Signal | Confidence |
|---|---|---|---|
| Individual developers / power users | Free tier → Pro subscription | $10–20/month | High — matches AI tool market |
| Developer teams (5-50 people) | Per-seat or per-agent flat | $8–15/user/month | High — matches 1Password/Tailscale |
| Enterprises (500+ employees) | Per-agent + compliance features | $50–200k/year custom | Medium — no direct comp |
| Agent framework integrations (LangChain etc.) | Free SDK + revenue share or OEM licensing | TBD | Low — novel territory |
| Insurance reduction / compliance certification | Indirect value, premium pricing | $25–50k/year add-on | Speculative but real |

**Recommended go-to-market sequence:**

1. **Open-source the daemon.** Privacy-first open core builds trust and removes the enterprise security objection ("we can audit it"). This is how Grafana, Tailscale's OSS components, and HashiCorp Vault established credibility.

2. **Target AI agent framework developers first.** LangChain has 97M+ monthly SDK downloads as proxy for MCP — similar integration leverage. A Substrate integration in LangChain's agent loop means every developer who builds an agent gets Substrate exposure for free. This is the Stripe webhook moment.

3. **Free tier: local only, single device, individual use.** No sign-up required. Delivers core value (process awareness, workflow graph, agent API locally). Converts developers into advocates.

4. **Pro tier ($15/month):** Cross-device sync, persistent user intent model, expanded agent API rate limits, audit log export. Targets prosumers and individual developers who rely on Substrate daily.

5. **Team tier ($12/user/month, min 5):** Centralized policy management, shared agent allowlists, team audit logs. Targets developer teams adopting agents at work.

6. **Enterprise tier (custom, $50k–$500k/year):** Full compliance export (EU AI Act, NIST AI RMF, SOC 2 ready), SSO, deployment governance, priority support, AI liability certification (when available). Targets IT and security buyers at large orgs.

7. **Developer/API tier (usage-based):** For agent framework companies and platform integrators who embed Substrate. $0.001–$0.01 per broker query at volume. Minimum $500/month. Targets companies building agents-as-a-product.

**Competitive moat assessment:**

The moat compounds through four mechanisms, in order of defensibility:
1. **Integration lock-in** (highest): Once 50 agents in an enterprise query Substrate, ripping it out requires updating every agent — identical to how removing Auth0 or 1Password is a multi-quarter project.
2. **Intent model data** (high): Substrate's on-device learned model of user workflow patterns is unique to each user. Competitors can copy the broker API; they can't copy years of learned context.
3. **Network effects** (medium): As more agent frameworks ship Substrate integrations by default, every new agent developer gets Substrate without choosing it. The standard creates the moat.
4. **First-mover category definition** (medium): "Substrate-verified" becoming shorthand for "safe agent" in the way "Stripe-powered" means trusted payments. Brand moat requires execution speed.

**TAM numbers (cross-referenced):**
- Agentic AI Governance market: $7.28B (2025) → $38.94B (2030), 39.85% CAGR — Mordor Intelligence
- AI Agents overall market: $7.84B (2025) → $52.62B (2030), 46.3% CAGR — GM Insights
- 57% of companies have AI agents in production (G2 August 2025 survey)
- Gartner: 40% of enterprise apps will have task-specific agents by end of 2026
- 50% of executives plan to spend $10–50M on agentic security in the coming year
- Developer tools market context: Snyk at $343M ARR ($25/dev/month), Datadog at $3.43B annual revenue

**Bottom line:** Substrate's business case is strong — the market is real, the timing is right (agents are deploying faster than governance can keep up), and the category is empty. The founding risk is not "is there a market" but "can we reach developers fast enough to own the standard before OS vendors or the Zenity/Fiddler tier pivots into our layer." Speed to open-source release and framework integration is the singular strategic priority.
