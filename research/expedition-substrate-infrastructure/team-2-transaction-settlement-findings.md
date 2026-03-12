# Team 2 Findings: Transaction Settlement & The Submantle Store
## Date: 2026-03-10
## Researcher: Team Member 2

---

### Battle-Tested Approaches

---

**API Marketplace with Fixed Commission (the RapidAPI/Shopify model)**

- **What:** A platform takes a fixed percentage of every transaction between API providers and consumers, acting as the broker, billing intermediary, and discovery layer.
- **Evidence:** RapidAPI (acquired by Nokia, 2024) takes a flat 25% marketplace fee on all payments, serves 4M+ developers and 80K+ APIs, with $44.9M revenue in 2024, up from $24M in 2023. Shopify App Store took 0% on first $1M/year per developer (now lifetime cap effective Jan 1 2025), then 15% above that — with 2.9% payment processing on top. Developers have collectively earned $1.5B+ through the Shopify App Store. Salesforce AppExchange charges 15% revenue share for ISVforce, 25% for OEM Embedded licenses, plus a $2,700 first-year security review fee and $150/year listing fee. AWS Marketplace takes a percentage fee (not publicly disclosed) but positions itself as the billing conduit for ISV revenue.
- **Source:** RapidAPI pricing docs (docs.rapidapi.com/docs/payouts-and-finance, accessed March 2026); Shopify developer changelog (shopify.dev/changelog, accessed March 2026); Salesforce AppExchange ISVforce guide (developer.salesforce.com, accessed March 2026); JuheAPI marketplace comparison article (juheapi.com, accessed March 2026)
- **Fits our case because:** The Submantle Store is structurally identical to these models — Submantle is the discovery and billing layer, identity pack creators are the providers, and agents/users are the consumers. The 15-25% take rate range is validated across multiple marketplaces at scale.
- **Tradeoffs:** 25% is aggressive for developer-first tooling. The most loved developer marketplaces (npm, PyPI, GitHub Actions) are free to publish. A premium of 15-20% on paid packs, with free community packs at 0%, is the established sweet spot. High take rates create ecosystem resentment; low ones require volume.

---

**Usage-Based / Metered API Billing (the Stripe Billing / OpenAI model)**

- **What:** Every API call is metered and aggregated into a billing period invoice; consumers pay for what they use rather than a flat subscription.
- **Evidence:** 67% of SaaS companies now use consumption-based pricing (up from 52% in 2022), per Maxio 2025 pricing trends report. Stripe Billing introduced dedicated token-metering infrastructure for AI workloads in 2025/2026 (currently in private preview waitlist), allowing ingestion of up to 1,000 meter events/second standard and higher throughput via Meter Event Stream. The system aggregates usage and invoices monthly. OpenAI's pricing model ($0.00000175/token for gpt-5.2 input) demonstrates that sub-cent per-unit pricing is live and operational at massive scale. AWS API Gateway charges $3.50 per million REST API calls, proving $0.0000035/call is a viable floor. X revised to usage-based API pricing in October 2025. Algolia, HiveMQ ($0.80/million messages), and Twilio ($0.0075/SMS) all operate at sub-cent per-unit economics.
- **Source:** Maxio 2025 pricing trends report (withorb.com/blog/stripe-pricing, accessed March 2026); Stripe metered billing docs (docs.stripe.com/billing/subscriptions/usage-based, accessed March 2026); Stripe token billing page (docs.stripe.com/billing/token-billing, accessed March 2026); AWS API Gateway pricing (aws.amazon.com/api-gateway/pricing, accessed March 2026)
- **Fits our case because:** Agent transaction microfees ($0.001/query) are exactly this model. Every agent query to Submantle is a meter event. Stripe's infrastructure can aggregate these into monthly invoices — eliminating the per-transaction payment problem entirely.
- **Tradeoffs:** Usage-based billing creates "surprise bills" — a known driver of churn and enterprise procurement friction. The mitigation is credit/budget caps, real-time usage dashboards, and spending alerts. Stripe Radar handles fraud detection at this layer; Submantle would inherit it.

---

**Prepaid Credit System (the Clay.ai / OpenAI Credits model)**

- **What:** Users pre-purchase a block of credits that deplete with usage; no real-time payment per query, no surprise invoices, natural fraud prevention.
- **Evidence:** Clay.ai uses a credit abstraction system where different AI actions consume variable credit quantities from a purchased bucket. OpenAI offers prepaid credits for API usage. Moesif's technical documentation confirms Stripe supports prepaid credit-based billing as a first-class use case. The Nevermined AI agent billing platform specifically identifies "Flex Credits" (prepaid consumption units) as the preferred enterprise billing approach, providing "predictable spend" and "real-time burn rate visibility."
- **Source:** Chargebee 2026 AI agent pricing playbook (chargebee.com/blog/pricing-ai-agents-playbook/, accessed March 2026); Nevermined billing patterns (nevermined.ai/blog/ai-agent-billing-patterns, accessed March 2026); Moesif Stripe credit billing guide (moesif.com, accessed March 2026)
- **Fits our case because:** Prepaid credits solve Submantle's three hardest billing problems simultaneously: (1) eliminates per-microtransaction payment processor overhead; (2) prevents unpaid usage — credits must exist before queries run; (3) natural fraud ceiling — a compromised API key can only burn existing credits, not create unlimited debt. This is how Submantle should implement agent transaction billing.
- **Tradeoffs:** Prepaid creates friction at acquisition (users must pay before they get value). Mitigation: a free-tier credit allowance at signup. Enterprise finance teams actually prefer prepaid because it allows budget control.

---

**Outcome-Based Pricing (the Intercom Fin model)**

- **What:** Charging per resolved outcome rather than per resource consumed — aligning price directly to demonstrated value delivered.
- **Evidence:** Intercom Fin AI charges $0.99 per fully resolved customer support ticket. It now handles 80%+ of support volume, resolves 1M customer issues per week, and grew from $1M to $100M+ ARR on this model. Fin carries a $1M performance guarantee if resolution targets aren't met. The model aligns pricing with users' success, allowing self-validation of value. The Chargebee 2026 report identifies outcome-based as one of the three dominant AI agent pricing patterns, with hybrid (fixed floor + usage tail) as the most adopted.
- **Source:** Intercom Fin pricing page (intercom.com/pricing, accessed March 2026); GTM newsletter "How Intercom Built a $100M AI Agent with Outcome Pricing" (thegtmnewsletter.substack.com, accessed March 2026); Sequence blog "How Intercom cracked outcome-based pricing" (sequencehq.com, accessed March 2026)
- **Fits our case because:** "Submantle Safe" certification is inherently outcome-based — value is "this agent is verified to not destroy data." A per-certification fee tied to certification renewal (annual, like SOC 2) follows this pattern. For the broker API, outcome-based pricing would be: per-prevented-incident rather than per-query — but that's unquantifiable in real-time. Per-query remains the right model for the broker; outcome-based fits certification.
- **Tradeoffs:** Outcome pricing requires clear, measurable, and agreed-upon outcome definitions. "Resolved ticket" is unambiguous. "Agent safety check passed" is ambiguous — the agent could still cause harm. Outcome pricing is not applicable to the broker API layer.

---

**SOC 2 / Security Certification as a Revenue Vehicle**

- **What:** Independent third-party certification of a product's security posture, sold as a compliance artifact that unlocks enterprise sales.
- **Evidence:** SOC 2 Type 2 certification costs $30,000–$150,000 to obtain (2026 data). 83% of enterprise buyers now require SOC 2 from SaaS vendors before signing; this rises to 91% for companies with 5,000+ employees (Vanta 2025 survey). 67% of certified startups report directly enabling deals they would have lost. Median deal enabled: $120,000. Year-two total cost drops 30-50% once the foundation exists. UL Solutions launched formal AI safety certification services under UL 3115 standard in November 2025, covering robustness, reliability, transparency, accountability, privacy, fairness, safety, security, and freedom from bias. CSA and Northeastern University launched the TAISE (Trusted AI Safety Expert) Certificate Program in 2025 at $795/bundle, targeting 100,000 professionals by 2026. Salesforce AppExchange requires a $2,700 security review for paid apps.
- **Source:** Sprinto SOC 2 cost breakdown (sprinto.com/blog/soc-2-compliance-cost/, accessed March 2026); Vanta 2025 enterprise buyer survey via StrongDM (strongdm.com/blog/how-much-does-soc-2-cost, accessed March 2026); UL Solutions press release (businesswire.com/news/home/20251102590835, accessed March 2026); CSA TAISE certification announcement (cloudsecurityalliance.org, accessed March 2026)
- **Fits our case because:** "Submantle Safe" certification is a direct revenue engine AND an enterprise sales accelerator. If agent developers can display a "Submantle Safe" badge to their enterprise customers, Submantle certification becomes the SOC 2 of AI agents — a purchasing requirement, not a nice-to-have. The certification fee ($2,500–$5,000/year per agent framework) is justified by the deal-enabling value.
- **Tradeoffs:** Certification requires building and maintaining evaluation infrastructure, legal review of claims, and liability management. This is a medium-term play — Submantle must achieve credibility as an awareness platform before "Submantle Safe" means anything to enterprise buyers. UL Solutions' entry validates the market exists; it also validates a potential competitor or partner.

---

### Novel Approaches

---

**x402 / HTTP 402 Native Agent-to-Agent Payments**

- **What:** Reviving the dormant HTTP 402 "Payment Required" status code as a payment rail where any server can demand micropayment before serving a response, and any agent can pay instantly via stablecoin.
- **Why it's interesting:** Eliminates accounts, API keys, subscriptions, and billing cycles entirely. Every Submantle query could require HTTP 402 payment in stablecoin (USDC). No Stripe, no invoices, no credit cards. The agent pays $0.001 in USDC at query time, Submantle's wallet receives it instantly. Settlement in 200ms on Base network. Protocol charges zero protocol fees — only nominal blockchain network fees (currently fractions of a cent on Base).
- **Evidence:** x402 protocol established by Coinbase Developer Platform and Cloudflare in September 2025. As of March 2026 tracking: 75.41M total transactions processed, $24.24M transaction volume, 94.06K buyers, 22K sellers — in the last 30 days alone. Growth trajectory: 156,000 weekly transactions with 492% growth reported in late 2025. Google's Agent Payments Protocol (AP2), launched September 2025 and backed by Salesforce, Mastercard, Visa, and 60+ partner organizations, integrated x402 as its stablecoin settlement rail. Nevermined platform reports 10,000% transaction surge in October 2025, approximately 500,000 transactions in a single week, using the x402 rail.
- **Source:** x402.org (accessed March 2026); Coinbase Developer Platform blog (coinbase.com/developer-platform/discover/launches/google_x402, accessed March 2026); Nevermined AI agent payment statistics (nevermined.ai/blog/ai-agent-payment-statistics, accessed March 2026); Orium agentic payments explainer (orium.com/blog/agentic-payments-acp-ap2-x402, accessed March 2026)
- **Fits our case because:** Submantle's microfee model ($0.001/query) is structurally incompatible with traditional card-based payment processors (Stripe's standard 2.9% + $0.30 would consume the entire fee on any single transaction). The x402 protocol solves this natively. If an enterprise agent makes 10M queries/month to Submantle at $0.001/query = $10,000/month — the x402 settlement infrastructure handles this autonomously without human intervention or monthly invoices.
- **Risks:** Cryptocurrency/stablecoin integration creates enterprise adoption friction. Many enterprise IT and procurement departments cannot or will not approve crypto payment flows in 2026. Regulatory uncertainty in some jurisdictions. Submantle would need to offer both tracks: x402 for crypto-comfortable developers and credit prepay + Stripe for enterprises. A pure x402 play is too early for enterprise go-to-market.

---

**Nevermined-Style Agent Payment Infrastructure (Specialized Layer)**

- **What:** A purpose-built agent billing layer (separate from Stripe or x402) that handles real-time metering at 200,000 events/second, credit deduction, agent identity via DIDs, cryptographic usage signing, and A2A payment routing — with Stripe as the fiat on-ramp.
- **Why it's interesting:** Nevermined (and similar platforms emerging in 2026) demonstrates that traditional billing infrastructure cannot handle agentic billing natively. Stripe requires "weeks of custom development" for AI use cases; Nevermined enables integration in under 20 minutes. Valory reduced agent deployment from 6 weeks to 6 hours using purpose-built billing infrastructure.
- **Evidence:** Nevermined supports MCP, Google A2A, x402, and any HTTP-based protocol. Their platform processes up to 200,000 events/second with real-time credit deduction, cryptographic signing of every usage record (append-only for audit compliance), ASC 606 and IFRS 15 workflow support, and DIDs for agent identity. They explicitly solve the "critical gaps" of legacy systems: agent-to-agent transactions, protocol support (A2A, MCP), cryptographic identity, and high-volume event ingestion.
- **Source:** Nevermined payment systems guide (nevermined.ai/blog/ai-agent-payment-systems, accessed March 2026); Nevermined billing patterns (nevermined.ai/blog/ai-agent-billing-patterns, accessed March 2026)
- **Fits our case because:** Submantle should not build billing infrastructure from scratch. Integrating a Nevermined-style billing layer gives Submantle metering at 200K events/second, cryptographic audit logs, A2A payment support, and a fiat+crypto dual track — in weeks, not months. This is the infrastructure layer beneath the Submantle Store, not a competitor.
- **Risks:** Dependency on a third-party billing vendor. If Nevermined fails or changes terms, Submantle is exposed. Mitigate by abstracting the billing layer behind a Submantle-owned interface, making the vendor swappable. Also note: Stripe is actively building similar infrastructure (token billing in private preview) — in 12-18 months Stripe may close this gap.

---

**Per-Agent Subscription Billing (Not Per-User)**

- **What:** Billing enterprises by number of AI agents registered with Submantle, not by number of human users — capturing the actual value delivered.
- **Why it's interesting:** At $5/agent/month, an enterprise with 100 agents = $500/month; 1,000 agents = $5,000/month. This aligns price precisely to the Submantle value proposition: brokering safety for each agent. Team 6 (prior expedition) identified this as a novel approach with no current direct precedent.
- **Evidence:** Gartner projects 40% of enterprise applications will have embedded agents by end of 2026, up from <5% in 2025. Enterprise AI agent count is growing faster than seat count. Anthropic's Frontier enterprise platform mentions "per agent" orchestration but has no published pricing as of March 2026. The AI governance market is $7.28B (2025) → projected $38.94B (2030) at 39.85% CAGR (Mordor Intelligence). Datadog's per-host billing ($15-23/host/month) is the closest working analog — each host is an "agent" in infrastructure monitoring.
- **Source:** Gartner 2026 agent projection (cited in Team 6 findings, expedition 1); Mordor Intelligence Agentic AI Governance report (cited in Team 6); Chargebee 2026 AI agent pricing playbook (accessed March 2026)
- **Fits our case because:** Submantle's value scales with agent count, not user count. One security engineer "supervising" 500 agents creates no subscription friction under per-agent billing. This is the billing model that captures exponential value as enterprises deploy more agents.
- **Risks:** Enterprises resist variable costs that grow with AI adoption — could create perverse incentive to avoid deploying more agents or to route around Submantle. Mitigation: tiered caps (e.g., first 10 agents included in Team tier, then $5/agent/month above that). This is a medium-term model, not a day-one model.

---

### Emerging Approaches

---

**Stripe's Agentic Commerce Protocol (ACP) + AI Billing Infrastructure**

- **What:** Stripe and OpenAI co-developed an Agentic Commerce Protocol enabling programmatic commerce flows between buyers, AI agents, and businesses — and Stripe is simultaneously building AI-specific metered billing infrastructure (token billing, markup automation, real-time cost tracking).
- **Momentum:** Stripe confirmed ACP integration with ChatGPT for purchasing from Etsy, Shopify merchants (1M+ sellers), with direct expansion planned. Stripe's token billing allows companies to apply a markup percentage above raw model costs, automatically track per-customer token consumption, and invoice monthly. Stripe's Meter Event endpoint handles 1,000 calls/second (standard) with a high-throughput stream for higher volume. Stripe's AI billing product is in private preview waitlist as of March 2026.
- **Source:** Stripe ACP announcement (stripe.com/blog/developing-an-open-standard-for-agentic-commerce, accessed March 2026); Stripe token billing docs (docs.stripe.com/billing/token-billing, accessed March 2026); PYMNTS Stripe AI billing article (pymnts.com, accessed March 2026)
- **Fits our case because:** Stripe is becoming the default billing infrastructure for AI-native companies. Submantle's commercial billing (subscriptions, pro/team/enterprise tiers, credit purchases) runs on Stripe today and should continue to. Stripe's metered billing handles aggregation; Submantle sends meter events per broker query; Stripe invoices monthly. The ACP is less relevant — it handles buyer-to-merchant flows, not agent-to-service microtransactions.
- **Maturity risk:** Stripe's token billing is still in private preview. The feature set may shift before GA release. For launch, Submantle should use Stripe's existing metered billing (which is GA) and migrate to token billing when it becomes available.

---

**The Palo Alto Networks / Cortex XSOAR Content Pack Model**

- **What:** A security platform's built-in marketplace for community-contributed and vendor-contributed integration packs — free and paid tiers, with the platform verifying all content before publishing.
- **Momentum:** Cortex XSOAR launched its Marketplace in 2020 with content packs from Code42, Google Chronicle, Recorded Future, Wipro, and others. Premium content is purchased with "Marketplace points" (a credit abstraction). The platform positions verification ("the only SOAR platform that verifies all free and paid third-party content") as the trust signal.
- **Source:** Palo Alto Networks XSOAR Marketplace announcement (paloaltonetworks.com/blog/2020/08/cortex-xsoar-marketplace/, accessed March 2026); Cortex XSOAR marketplace (xsoar.pan.dev/marketplace, accessed March 2026)
- **Fits our case because:** The Submantle Store's identity packs are structurally identical to XSOAR content packs: community-contributed definitions, platform-verified before publishing, free community tier, premium vendor-created packs. The "Marketplace points" credit abstraction maps to Submantle credits. The trust signal ("Submantle verified") is the same mechanism as XSOAR's verification badge.
- **Maturity risk:** XSOAR's marketplace primarily serves security operations teams, not developer consumers. The adoption model for identity packs (much smaller and more specific than security playbooks) has less precedent. The open-source analog (antivirus definition contributions) is the better mental model for community-sourced identity signatures.

---

**Zero-Protocol-Fee Stablecoin Settlement for Developer Ecosystems**

- **What:** As x402 / AP2 matures, zero-fee agent-to-agent payment rails become infrastructure-grade — enabling a Submantle billing model with no transaction overhead on microfees.
- **Momentum:** x402 processed 75.41M transactions in the past 30 days (March 2026). AP2 backed by Google, Mastercard, Visa, Salesforce. Stripe is building its own blockchain ("Tempo") for cross-border stablecoin payments with sub-second finality. Stablecoin B2B payment volume doubled to ~$400B in 2025 (60% B2B). The Nevermined platform and x402 ecosystem are adding enterprise-grade features (SOC 2 Type II, multi-currency, audit logs) throughout 2025-2026.
- **Source:** x402.org live statistics (accessed March 2026); PYMNTS Stripe blockchain article (pymnts.com/blockchain/2026, accessed March 2026); This Week in Fintech Stripe AI infrastructure (accessed March 2026)
- **Fits our case because:** The x402 model eliminates the fundamental economic problem of microtransactions: traditional processors cannot profitably process $0.001 transactions. With x402, Submantle charges $0.001 in USDC per query, the agent pays instantly, and Submantle's wallet accumulates. At 10M queries/day: $10,000/day, $3.65M/year — with zero payment processing overhead.
- **Maturity risk:** Enterprise procurement in 2026 still struggles with crypto payment approvals. The 2027-2028 window is when this becomes mainstream enterprise infrastructure. For now, Submantle should offer x402 as an experimental developer track while running fiat credit billing as the primary enterprise path.

---

### Gaps and Unknowns

**1. The Microtransaction Problem is Real — and the Solutions are Bifurcated.**
Traditional card processors cannot handle $0.001/query billing without batching. Stripe's standard 2.9% + $0.30 would cost $0.30 per transaction — 300x the transaction value. The two working solutions are: (A) aggregate usage into monthly invoices via Stripe metered billing (removes per-transaction fees), or (B) use x402/stablecoin rails (zero protocol fees). Submantle needs both tracks. The math for monthly aggregation: an agent making 100K queries/month at $0.001 = $100 invoiced via Stripe. That's viable. The math for x402: $0.001 per query settled instantly in USDC. That's also viable. What is NOT viable: processing $0.001 as an individual card transaction.

**2. Identity Pack Economics Are Unproven at the Right Scale.**
The Submantle identity signature format (15 signatures currently, kilobytes each) maps to community-curated content packs in other platforms. The pricing question: what does someone pay for a "professional identity pack" covering, say, all 200+ Adobe Creative Cloud processes? $4.99 one-time? $0.99/month? The antivirus analogy suggests free-plus-optional-donations for community packs (like Wikipedia) and paid premium packs for enterprise software stacks. No research surface found a direct analog product at this specificity. This requires a pricing discovery experiment.

**3. The Submantle Store Network Effects Are Dependent on Organic Signature Contribution.**
The Cortex XSOAR marketplace launched with content from established security vendors — not grassroots contributions. The WordPress plugin ecosystem's community health is real but it took years. The key question: what incentivizes a developer to contribute an identity signature to Submantle for free? The answer from antivirus: recognition (contributor credit), reputation in the community, and the free tier benefit of getting to use the full signature library. Explicit contributor rewards (revenue share on premium packs derived from community packs) would accelerate this but require careful design.

**4. "Submantle Safe" Certification Infrastructure Doesn't Exist Yet.**
UL Solutions (UL 3115 standard), CSA/Northeastern (TAISE), and others are building AI safety certification programs in 2025-2026. None of them are specifically certifying that an AI agent is "safe to operate in the presence of Submantle." The Submantle Safe certification would be narrower: "this agent correctly uses the Submantle broker API and respects its signals." Building this requires: (A) a written certification standard, (B) an evaluation methodology, (C) a legal framework for the badge, (D) liability protection for false positives. This is a 12-18 month build, not a launch-day feature.

**5. Fraud Prevention at Microtransaction Scale is Solved Infrastructure.**
This is NOT a gap — it's a solved problem. The mechanisms are: (A) prepaid credits eliminate post-pay debt fraud entirely; (B) API key rate limits cap per-key spend regardless of billing model; (C) Stripe Radar applies ML fraud detection automatically; (D) x402's stablecoin model requires real payment before service, eliminating credit fraud by definition. Twilio's fraud prevention model (rate limits by phone number, ML fraud scoring, automatic disabling of suspicious accounts) is directly applicable to Submantle's API key model. The research did not surface any novel fraud vectors specific to agent query billing that aren't already handled by these mechanisms.

**6. Revenue Projections at Scale Are Speculative but Calculable.**

| Scale | Queries/Day | Monthly Revenue (@$0.001) | Annual Revenue |
|---|---|---|---|
| 10K active agents (early) | 1M | $30,000 | $365,000 |
| 100K active agents | 10M | $300,000 | $3.65M |
| 1M active agents | 100M | $3,000,000 | $36.5M |
| 10M active agents | 1B | $30,000,000 | $365M |

These numbers assume $0.001/query average. At $0.01/query (which is defensible given the value provided), multiply by 10x. The query rate is the uncertain variable — an agent might make 1 Submantle query per task, or 10. Research did not surface data on realistic query-per-agent-session ratios.

---

### Synthesis

**The strongest overall finding: Submantle's transaction model is viable at scale, but requires a carefully layered billing architecture, not a single mechanism.**

The fundamental problem — traditional payment processors can't handle $0.001 transactions economically — has two currently-proven solutions: (1) aggregate via monthly metered billing (Stripe, viable today), and (2) stablecoin settlement via x402 (viable for crypto-comfortable developers today, enterprise-viable by 2028). Both should be implemented.

**The Submantle Store is the right model. Here's what it should look like at scale:**

**Layer 1: Community Identity Packs (Free Tier)**
- All community-contributed identity signatures are free to all users
- Contributors get attribution and optional tips/donations
- The free library grows through network effects — more users = more signatures = better Submantle
- Modeled after: antivirus definition databases, npm, WordPress plugin repository (0% take rate)

**Layer 2: Premium Identity Packs (Paid, Submantle takes 15-20%)**
- Vendor-certified packs (e.g., "Official Adobe Creative Cloud Pack" with 200+ signatures)
- Enterprise software stacks (e.g., "SAP Enterprise Pack")
- Specialized verticals (medical devices, financial software, industrial control systems)
- Pricing: $4.99–$29.99/month per pack or one-time purchase
- Modeled after: Cortex XSOAR Marketplace, Minecraft Marketplace (content packs), App Store small software
- Take rate precedents: RapidAPI 25%, Shopify 15% above $1M, Salesforce 15-25%

**Layer 3: Agent Transaction Microfees (Usage-Based)**
- $0.001–$0.01 per broker query (validate against query value — "what would break" queries are high-value)
- Billing mechanism: Prepaid credit system (buy credits, burn per query) for enterprise; x402 stablecoin for developer-native
- Infrastructure: Stripe Billing (metered aggregation) + Nevermined-style event ingestion for high-throughput
- Fraud prevention: Rate limits per API key + credit caps + Stripe Radar
- Free tier: 1,000 queries/month included (enough for individual developers to evaluate)

**Layer 4: Submantle Safe Certification (Annual Fee)**
- $2,500–$5,000/year per agent framework or product
- Requires evaluation against a published Submantle compatibility standard
- Unlocks "Submantle Safe" badge for marketing use
- Revenue driver AND trust signal for enterprise buyers
- Launch timeline: 12-18 months post-platform adoption (certification is meaningless before the community exists)

**The take rate question across marketplaces:**

| Marketplace | Take Rate | Context |
|---|---|---|
| Apple App Store | 15-30% | Consumer platform, forced billing |
| Google Play Store | 15-20% (reduced 2025) | Consumer platform |
| Shopify App Store | 15% (above $1M lifetime) | Developer tools |
| Salesforce AppExchange | 15-25% | Enterprise platform |
| RapidAPI | 25% | API marketplace |
| AWS Marketplace | Undisclosed (est. 20-30%) | Enterprise cloud |
| VSCode Marketplace | 0% (no native paid support) | Developer tools, Microsoft loss leader |
| WordPress.org | 0% | Open source repository |

**Recommendation for Submantle:** 0% on community identity packs (maximize ecosystem growth), 15% on premium commercial packs (competitive with Shopify/Salesforce), no take rate on agent transaction fees (Submantle IS the fee — the query fee IS the revenue, not a commission on someone else's revenue).

**What the orchestrator needs to know:**

The most consequential architectural decision in this research angle is the billing mechanism for agent transaction microfees. The choice is:

1. **Monthly metered aggregation via Stripe** (viable today, enterprise-friendly, requires minimum commit to be worthwhile — suggest $10/month minimum)
2. **Prepaid credits** (fraud-proof, enterprise procurement-friendly, best for usage predictability)
3. **x402 stablecoin** (zero overhead, developer-native, not enterprise-ready until ~2028)

The **right answer is (2) prepaid credits as the primary model, with Stripe Billing for monthly invoicing of large enterprises, and x402 as an experimental developer track.** This is what Clay.ai, OpenAI, and the emerging Nevermined-style platforms are converging on.

The second most consequential finding: **identity packs are a sound product concept, but need pricing discovery experiments.** There is no direct precedent for "community-curated process identity signatures as a marketplace product." The closest analogs (antivirus definitions, XSOAR content packs) are not directly comparable. The free/premium split is the right model; the price point requires testing with early users.

The third finding: **"Submantle Safe" certification is a real revenue engine in 18-24 months** — but only after the platform has adoption. Without adoption, the badge is worthless. Prioritize platform growth first; certification is the monetization layer that arrives after credibility.

---

*Sources accessed March 10, 2026:*
- [RapidAPI Payouts and Finance docs](https://docs.rapidapi.com/docs/payouts-and-finance)
- [RapidAPI marketplace pricing comparison (JuheAPI)](https://www.juheapi.com/blog/api-marketplace-pricing-comparison-rapidapi-vs-openrouter-vs-wisdom-gate)
- [Shopify App Store revenue share](https://shopify.dev/docs/apps/launch/distribution/revenue-share)
- [Salesforce AppExchange revenue share docs](https://developer.salesforce.com/docs/atlas.en-us.packagingGuide.meta/packagingGuide/appexchange_checkout_rev_share.htm)
- [Stripe pricing](https://stripe.com/pricing)
- [Stripe usage-based billing docs](https://docs.stripe.com/billing/subscriptions/usage-based)
- [Stripe token billing docs](https://docs.stripe.com/billing/token-billing)
- [Stripe ACP blog](https://stripe.com/blog/developing-an-open-standard-for-agentic-commerce)
- [x402 protocol](https://www.x402.org/)
- [Coinbase/Google x402 launch](https://www.coinbase.com/developer-platform/discover/launches/google_x402)
- [Nevermined AI agent payment systems](https://nevermined.ai/blog/ai-agent-payment-systems)
- [Nevermined billing patterns](https://nevermined.ai/blog/ai-agent-billing-patterns)
- [Chargebee 2026 AI agent pricing playbook](https://www.chargebee.com/blog/pricing-ai-agents-playbook/)
- [Intercom Fin pricing](https://www.intercom.com/pricing)
- [GTM newsletter Intercom $100M AI Agent](https://thegtmnewsletter.substack.com/p/gtm-178-intercom-ai-agent-outcome-based-pricing-archana-agrawal)
- [Moesif prepaid credit billing](https://www.moesif.com/blog/technical/api-development/Pre-paid-Credit-Based-Billing-With-Stripe/)
- [SOC 2 certification cost 2026 (Sprinto)](https://sprinto.com/blog/soc-2-compliance-cost/)
- [SOC 2 enterprise buyer data (StrongDM)](https://www.strongdm.com/blog/how-much-does-soc-2-cost)
- [UL Solutions AI certification launch](https://www.businesswire.com/news/home/20251102590835/en/UL-Solutions-Launches-Landmark-Artificial-Intelligence-Safety-Certification-Services)
- [CSA TAISE certification](https://cloudsecurityalliance.org/blog/2025/10/22/introducing-taise-the-trusted-ai-safety-expert-certificate)
- [Cortex XSOAR Marketplace](https://www.paloaltonetworks.com/blog/2020/08/cortex-xsoar-marketplace/)
- [Orium agentic payments explainer (ACP, AP2, x402)](https://orium.com/blog/agentic-payments-acp-ap2-x402)
- [Cloudflare AI Gateway pricing](https://developers.cloudflare.com/ai-gateway/reference/pricing/)
- [Maxio consumption billing guide](https://www.maxio.com/blog/consumption-based-billing)
- [Nordic APIs monetization models](https://nordicapis.com/9-types-of-api-monetization-models/)
- [AWS API Gateway pricing](https://aws.amazon.com/api-gateway/pricing/)
- [Twilio fraud prevention](https://www.twilio.com/docs/verify/preventing-toll-fraud)
- [Stripe Radar fraud detection](https://stripe.com/radar)
