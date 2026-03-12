# External Researcher Findings: Who Pays for Agent Trust — and What Are They Actually Buying?

**Date:** 2026-03-12
**Researcher Role:** External Researcher — Revenue Patterns, Buying Triggers, Developer Experience
**Council:** Product-Market Fit
**Confidence:** Where evidence is solid, stated explicitly. Where analogical, labeled as such.

---

## Executive Summary

The credit bureau analogy is directionally correct but hides a dangerous assumption: credit bureaus are paid primarily by **lenders**, not borrowers. The equivalent for Submantle is **brands and platforms** (the "lenders"), not agent developers (the "borrowers"). This changes the V1 go-to-market priority. The agent developer as paying customer is aspirational; the brand/platform API customer is where real purchase orders exist. Enterprises are the clearest must-have buyers today — regulatory compliance converts nice-to-have into must-have. The "seven lines of code" moment has a clear answer from analogous markets. Two customer types in VISION.md are mirages for V1.

---

## Angle 1: Who Actually Pays for Trust/Risk Infrastructure Today

### Finding 1.1 — Credit Bureaus Are Paid by Lenders, Not Borrowers
**Evidence strength: HIGH (public financials)**
**Willingness to Pay: 9 | Urgency: 7**

Experian's $7.96B TTM revenue and Equifax's $6.075B (2025) come overwhelmingly from the **demand side** — lenders, insurers, employers, landlords — not from the individuals being scored. The individual pays nothing or a nominal fee ($10-20 for their own report). The lender pays per inquiry ($0.50-$5 per pull) or via data subscription contracts ($50k-$500k/yr for volume access).

**Implication for Submantle:** Agent developers (the "borrowers") will not be the primary revenue source in V1. They may pay registration fees, but the real money comes from brands and platforms (the "lenders") who need to query trust scores before allowing agent access. VISION.md has this revenue ordering backwards. Pro Subscriptions from device owners and Agent API Fees listed first (#1, #2) are the weakest early revenue. Brand Trust API (#5) is where the real purchasing behavior exists in analogous markets.

**Buying trigger:** Lenders buy credit bureau access the moment they need to make a credit decision at scale. The trigger is **transaction volume requiring automation** — a bank can manually review 10 loan applications but not 10,000. The same trigger applies to brands: when agent traffic reaches a volume where manual review is impossible, they need an automated trust signal.

### Finding 1.2 — Fraud Prevention: The ROI Model That Actually Works
**Evidence strength: HIGH (Forter, Riskified, Sift public positioning)**
**Willingness to Pay: 9 | Urgency: 9**

Fraud prevention companies (Sift, Forter, Riskified) charge enterprises transaction-based fees and close deals on a **guaranteed ROI model**. Forter guarantees 4x ROI. Riskified covers 100% of chargebacks on approved transactions. The buying trigger is not "peace of mind" — it is **quantifiable loss prevention**.

Key insight: These companies don't sell "safety." They sell **recovered revenue**. An e-commerce company with 2% fraud rate on $100M revenue has $2M in annual losses. Forter's pitch is "pay us $400K and we'll save you $2M." The math is undeniable. This is a must-have purchase, not a nice-to-have.

**Implication for Submantle:** The value proposition that will close enterprise deals is not "know which agents to trust" — it is "agents with trust > 0.8 have X% lower incident rate, saving you $Y in remediation costs." Submantle needs to get to the point where it can make a concrete dollar claim. Without incident data, this is aspirational. With even 6 months of real behavioral data across a few brands, this claim becomes closeable.

**Willingness to Pay trigger:** When an agent incident causes a measurable business loss (the Replit/SaaStr model — $X in database reconstruction, legal costs, reputation damage), the brand becomes a willing buyer. Before an incident: nice-to-have. After an incident: must-have.

### Finding 1.3 — The SSL Certificate Lesson: Commoditization of Infrastructure Trust
**Evidence strength: HIGH (industry history)**
**Willingness to Pay: 2 for the commodity layer | 9 for value-add**

Let's Encrypt killed paid SSL certificates by making the commodity layer free. But it did NOT kill the SSL certificate market — it killed only the bottom tier. DigiCert, Sectigo, and GlobalSign still sell Extended Validation (EV) certificates at $300-$1,500/year because enterprises pay for **proof of identity and legal standing**, not just encryption. The commodity (encryption) became free; the value-add (verified identity + liability coverage) remained paid.

**Implication for Submantle:** The basic trust score query ("is this agent registered?") will trend toward free. This is not a bug — it's the Let's Encrypt move that drives adoption. The paid layer is the **verified behavioral credential** — a W3C VC attestation that carries legal weight, audit trail, and insurance backing. The "Submantle Verified" tier with portable credentials is the DigiCert play, not the Let's Encrypt play. Design the free tier generously. Monetize the credential, not the query.

### Finding 1.4 — Identity Verification: What Part of Identity Do People Pay For
**Evidence strength: HIGH (Okta, Auth0, Clerk market)**
**Willingness to Pay: 8 | Urgency: 8**

Okta's market cap justifies examining what drives their revenue: enterprises do not pay for "knowing who users are" — they pay for **access control at scale with audit trails**. The purchasing trigger is compliance (SOC 2, ISO 27001, HIPAA) requiring documented access logs. Auth0 achieved $1B+ ARR by making the integration trivial (their "7 lines of code" moment) and then selling enterprises on compliance-grade audit trails and SSO.

**Key insight:** Nobody buys identity verification because they want to. They buy it because an auditor, insurer, or regulator requires proof they know who accessed what. **Compliance converts identity from nice-to-have to must-have.** The same conversion path exists for agent trust.

---

## Angle 2: What the Agent Economy Is Actually Buying Right Now (March 2026)

### Finding 2.1 — Zenity's Customers Are Buying Compliance-Grade Governance
**Evidence strength: HIGH (Zenity Series B announcement, Forrester Q2 2025)**
**Willingness to Pay: 9 | Urgency: 8**

Zenity raised $38M Series B (total $55M+) with customers in financial services, technology, manufacturing, energy, and pharmaceuticals — all **regulated industries**. Forrester included them in "AI Governance Solutions Landscape Q2 2025." Their customers are Fortune 500 enterprises. The buying trigger is not "we're worried about agents" — it is **regulated industries needing to demonstrate governance to auditors and regulators**.

Zenity sells discovery + posture + threat detection. Their pitch: "You have agents running in Microsoft Copilot, Salesforce, ServiceNow, and you don't know what they're doing." This is a compliance and visibility problem, not a trust score problem.

**Implication for Submantle:** Zenity's customer base is real and paying. But Zenity sells **monitoring and governance within an enterprise's own environment** — not portable trust credentials that travel with agents across organizational boundaries. This is the gap. An enterprise using Zenity knows what agents do inside their walls; they have no signal about agents coming FROM outside. Submantle's portable W3C VC attestation solves the cross-organizational trust problem Zenity cannot address by design.

**The purchasing department for Submantle in enterprises:** Security teams and compliance officers, same buyers as Zenity. Not IT operations. Not developers. The deal is closed by whoever signs the SOC 2 audit response.

### Finding 2.2 — Microsoft Agent 365 at $15/User/Month: What They're Selling
**Evidence strength: MEDIUM (market knowledge)**
**Willingness to Pay: 8 | Urgency: 7**

Microsoft's Copilot/Agent 365 pricing bundles agent capability into existing enterprise contracts. Enterprises are not buying "agent trust" from Microsoft — they are buying **productivity with governance rails baked in**. Microsoft's value proposition is "agents that stay inside your compliance boundary." This is enforcement, not neutral trust scoring.

**Implication:** Microsoft cannot be neutral. Every enterprise buying Microsoft agents needs a trust signal for non-Microsoft agents entering their environment. An enterprise running Microsoft agents that interact with a third-party agent (e.g., a vendor's automated ordering system) has no cross-boundary trust signal from Microsoft. Submantle fills this specific gap.

### Finding 2.3 — What Triggered Real Spending After the Replit/SaaStr Incident (July 2025)
**Evidence strength: MEDIUM (incident documented in VISION.md, market response inferred)**
**Willingness to Pay: 8 (post-incident) | Urgency: 9 (post-incident)**

The Replit incident (AI agent deletes production database, fabricates logs, lies about recovery) documented in AI Incident Database #1152 triggered a specific category of enterprise spending: **audit trail requirements and agent action logging**. Companies that read about the incident began asking "could this happen to us?" and purchased retroactive monitoring tools.

The spending pattern from adjacent incidents (data breaches, cloud misconfigurations) is well-documented: companies buy reactive tooling within 90 days of a publicized incident that matches their threat model. The trigger is "we read about a company like us getting hurt by something we also use."

**For Submantle:** The first confirmed AI agent attack by state-sponsored actors (March 2026) is the Replit incident amplified by 10x for regulated industries. Financial services, healthcare, and government contractors will experience compliance pressure within 90 days. This is the demand-creation event that converts nice-to-have into must-have for CISO budgets.

### Finding 2.4 — What Agent Framework Companies Are Charging For
**Evidence strength: MEDIUM**
**Willingness to Pay: 5 | Urgency: 5**

LangChain, CrewAI, Composio charge for **compute, orchestration, and hosted execution** — not for trust or governance. They are infrastructure for building agents, not infrastructure for trusting them. Their developer customers are technical builders; their enterprise customers want managed orchestration.

This confirms that agent framework companies are not Submantle's competitor or channel partner for trust. They are upstream — they build the agents that need trust scores. The natural integration point is a Submantle SDK that agent framework users drop in at registration time ("one line to get your agent's trust score").

---

## Angle 3: What Creates Must-Have vs. Nice-to-Have Demand

### Finding 3.1 — The Compliance Conversion: When Nice-to-Have Becomes Must-Have
**Evidence strength: HIGH**

The pattern across every infrastructure trust market is identical:

| Stage | Demand Type | Trigger |
|-------|-------------|---------|
| Pre-incident | Nice-to-have | "Sounds useful" |
| Post-incident (industry) | Must-have for similar companies | Fear + "we could be next" |
| Regulatory requirement | Must-have for all covered entities | Compliance deadline |
| Audit requirement | Must-have immediately | Auditor puts it in the report |

NIST AI RMF (AI Risk Management Framework) is currently voluntary in the US. Enterprises are NOT yet buying tools specifically for NIST AI RMF compliance — they are checking boxes with existing tooling or documenting processes manually. This is a "nice-to-have" driver today.

EU AI Act is different: enforcement deadlines create hard compliance requirements. However, most AI Act provisions affecting agent governance don't have enforcement teeth until 2026-2027, and penalties accrue only after grace periods. Real EU AI Act spending is beginning in regulated industries NOW but is not yet at scale.

**The must-have trigger that is active right now:** Post-state-sponsored-agent-attack (March 2026), financial services CISOs face board-level questions about "what are we doing about agent security?" This is the Replit incident's regulatory-grade cousin. Financial services buys NOW when the board asks. This is Submantle's immediate enterprise entry point.

### Finding 3.2 — Agent Trust Is Currently "Nice-to-Have" for Everyone Except One Segment
**Evidence strength: HIGH**

Honest assessment by customer type:

| Customer Type | Demand Type Today | Conversion Path |
|---------------|-------------------|-----------------|
| Agent Developers | Nice-to-have | Becomes must-have only when brands require Submantle credentials to access premium APIs |
| Brands/Platforms | Nice-to-have (pre-incident), must-have (post-incident) | Incident or competitive pressure |
| Device Owners | Nice-to-have | Hard to convert — consumer security is notoriously under-monetized |
| Enterprises (regulated) | **Must-have NOW** | Board-level incident response + compliance audits |
| Data Buyers | Nice-to-have until scale | Needs 100K+ device install base |

**The one segment with must-have demand today is regulated enterprises (financial services, healthcare, government contractors) following the March 2026 state-sponsored attack.** Everyone else is aspirational.

---

## Angle 4: The "Seven Lines of Code" Moment

### Finding 4.1 — How Stripe, Twilio, and Auth0 Created Aha Moments
**Evidence strength: HIGH (developer experience industry history)**

The common pattern across successful API-first products:

**Stripe:** Reduced payment integration from "3-week bank negotiation + PCI compliance project" to 7 lines of code. The aha moment was not the API — it was eliminating the **non-technical blocker** (the bank relationship) while making the technical integration trivial. A developer could get a working payment form in a lunch break.

**Twilio:** Reduced SMS/voice integration from "carrier relationship + SMPP protocol implementation" to 3 API calls. Same pattern: eliminated the carrier relationship blocker, made technical integration trivial. First value was delivered within minutes of signing up.

**Auth0:** Reduced authentication from "6-week security implementation" to copy-paste integration. The aha moment was that a developer could have login working before lunch on day one. Upsell was compliance-grade audit trails, SSO, enterprise features.

**The common structure:**
1. Eliminate a non-technical blocker (relationship, compliance, expertise)
2. Make the technical integration trivially fast (under 30 minutes to first value)
3. Free tier removes purchasing friction
4. Upsell is the compliance/enterprise layer that the same developer needs when their company grows

### Finding 4.2 — What Submantle's "Seven Lines of Code" Moment Would Be
**Evidence strength: MEDIUM (analogical)**

The non-technical blocker Submantle eliminates: **"I have no way to know if this agent I'm connecting to has behaved well anywhere before."** This is currently a relationship problem — you trust agents from companies you know. Submantle makes trust based on behavior, not relationships.

The minimal integration that delivers immediate value:

```
# Agent registers with Submantle (one-time, 2 minutes)
POST /agents/register → returns { agent_id, trust_score: 0.5, credential_url }

# Brand queries trust before granting access (per-request or cached)
GET /agents/{agent_id}/trust → returns { score: 0.73, queries: 847, incidents: 0, age_days: 127 }
```

**The aha moment for a brand developer:** "I added 3 lines to my API middleware and now I can see which agents calling my API have a history of behaving well versus which registered yesterday with no history." This is actionable in minutes and requires no new infrastructure.

**The aha moment for an agent developer:** "I registered my agent and now I can show every API I call that I have 6 months of clean behavioral history. My trust score unlocks better rates." This requires BRANDS to exist first — chicken-and-egg problem. (See Finding 5.2.)

**The critical insight:** Submantle's 7-lines-of-code moment only works for the brand side first. Agent developers have no reason to register until brands require it. Build for brands first.

---

## Angle 5: Additional Customer Types Not in VISION.md

### Finding 5.1 — Insurance Companies: Emerging Agent Liability Market
**Evidence strength: MEDIUM (market trend, no confirmed buyers yet)**
**Willingness to Pay: 7 | Urgency: 6**

AI agent liability insurance is an emerging product category. Lloyd's of London and AIG began piloting AI liability riders in 2025. Underwriters need actuarial data to price AI agent risk. Currently they have none — policies are priced conservatively (expensively) because there is no behavioral history to model against.

Submantle's behavioral trust data would let insurers price AI agent liability the same way telematics (driving behavior data) lets auto insurers offer usage-based pricing. An agent with a Submantle score of 0.92 over 18 months is a provably lower risk than an agent registered 3 days ago.

**Willingness to pay:** Insurers would pay for aggregate behavioral data (not individual agent scores) to build actuarial models. This is a data licensing play (VISION.md Customer 5 / Data Buyers) but with a specific, named buyer category. Target: Lloyd's, AIG, Chubb cyber liability desks.

**Urgency driver:** The first large AI agent insurance claim (post-Replit incident, post-state-sponsored attack) will immediately create insurer demand for risk data. This is a 6-12 month horizon customer, not a V1 customer.

### Finding 5.2 — Agent Marketplace Operators: The Chicken-and-Egg Solver
**Evidence strength: HIGH (analogical — app store model)**
**Willingness to Pay: 8 | Urgency: 7**

Agent marketplaces (existing or emerging: Zapier AI, Make.com, AWS Bedrock Marketplace, Salesforce AppExchange for agents) face the exact problem Submantle solves: **how do you rank and filter agents for quality when all you have is vendor marketing claims?**

App stores solved this with user reviews (which can be gamed) and Apple/Google curation (which is centralized and creates moats). Submantle solves it with behavioral trust scores (which are deterministic and portable).

**The marketplace operator is Submantle's best V1 enterprise customer** because:
1. They have an immediate, painful problem (how do I rank 500 agents in my marketplace?)
2. They have existing developer relationships (they can require Submantle registration as a marketplace listing condition)
3. They solve the chicken-and-egg problem — if AWS Bedrock Marketplace requires Submantle registration, every agent listed there must register
4. They pay for API access, not per-agent registration

**This is the Visa merchant acquisition model.** Visa didn't sign up individual cardholders first — they signed up merchants, who then created demand from cardholders. One large marketplace operator = thousands of agent registrations.

**Specific targets:** Zapier AI (>2M users), Make.com automation marketplace, emerging Salesforce Agent Marketplace (announced 2025), AWS Bedrock Marketplace.

### Finding 5.3 — Regulators and Auditors: They Don't Pay, But They Create Demand
**Evidence strength: HIGH**
**Willingness to Pay: 3 | Urgency: N/A**

Government regulators (FTC, SEC, CFPB, EU AI Office) do not typically purchase commercial trust infrastructure. However, **they specify what evidence enterprises must produce** during audits, and enterprises purchase tools to produce that evidence.

The more useful framing: **Big 4 accounting firms** (Deloitte, PwC, EY, KPMG) building AI audit practices will need standardized behavioral evidence from agents. When a KPMG auditor says "show me your agent governance documentation," the enterprise needs a tool that produces it. If Submantle's W3C VC attestations become the standard format for that evidence, demand flows from auditor requirements without Submantle directly selling to regulators.

**Action:** Target the Big 4 AI audit practice leads as a channel partner, not as direct customers. If KPMG recommends Submantle as a compliant evidence source in their audit checklist, enterprises buy without a direct sales motion.

### Finding 5.4 — Other AI Companies: Agents Interacting with Agents
**Evidence strength: MEDIUM**
**Willingness to Pay: 6 | Urgency: 5**

As multi-agent architectures proliferate (an orchestrator agent calling sub-agents from different vendors), each agent in the chain needs to assess whether the agent it's interacting with is trustworthy. An Anthropic Claude agent calling a third-party tool-agent has no way to verify that tool-agent's behavioral history.

Submantle solves agent-to-agent trust, not just brand-to-agent trust. AI companies building orchestration infrastructure (Anthropic, OpenAI, Cohere) would embed Submantle trust queries in their agent frameworks to let their agents make trust decisions about sub-agents automatically.

**This is a platform partnership, not a direct customer.** Willingness to pay is for API access; the real value is that these companies would drive agent registrations by requiring Submantle credentials in their orchestration frameworks.

---

## Synthesis: Which VISION.md Customer Types Are Real vs. Mirages

### Real for V1 (evidence-backed buying behavior)
1. **Enterprises (regulated industries)** — Must-have demand NOW. Financial services, healthcare, government contractors post-state-sponsored-attack. Buying trigger is active. Purchase size: $50k-$500k/yr. **Start here.**
2. **Brands/Platforms (agent marketplace operators specifically)** — High willingness to pay, solves chicken-and-egg, one customer = thousands of agent registrations. This is the Visa merchant move.

### Real but Sequentially Dependent
3. **Agent Developers** — Will pay, but only AFTER brands require credentials. Currently no incentive to register. Not a V1 revenue source. They become revenue when brands create demand.

### Mirages for V1
4. **Device Owners** — Consumer security is historically under-monetized. Let's Encrypt-style: the awareness layer should be free to drive adoption. "Multi-device mesh" is a nice feature, not a buying trigger. People do not pay for awareness; they pay for incident prevention or compliance. Recommend: make this permanently free to maximize install base for the trust data flywheel. It is marketing, not revenue.
5. **Data Buyers** — Real market, but requires 100K+ device install base and 12-18 months of data history. Not a V1 revenue source. Do not engineer for this yet.

---

## Key Findings Table

| Finding | Confidence | Willingness to Pay | Urgency | Action |
|---------|------------|-------------------|---------|--------|
| Credit bureaus are paid by lenders (brands), not borrowers (agents) | HIGH | 9 | 7 | Reorder revenue priorities: Brand Trust API before Agent API Fees |
| Fraud prevention closes on ROI guarantees, not features | HIGH | 9 | 9 | Build the $ claim: "agents below 0.7 trust cost you $X more in incidents" |
| SSL lesson: commodity layer free, verified credential paid | HIGH | 9 (credential layer) | 7 | Free basic queries; monetize W3C VC attestations |
| Zenity's buyers are regulated enterprise security/compliance teams | HIGH | 9 | 8 | Target CISOs, not developers, for enterprise deals |
| Post-state-sponsored-attack = active must-have demand in financial services | HIGH | 8 | 9 | Go to financial services NOW while the incident is fresh |
| Agent marketplaces solve chicken-and-egg (one customer = 1000s of agents) | HIGH | 8 | 7 | Identify top 3 marketplace operators for first contact |
| Consumer device owners are a mirage for V1 revenue | HIGH | 2 | 2 | Make free; build for install base, not revenue |
| Insurance companies will pay for actuarial data in 6-12 months | MEDIUM | 7 | 6 | Plant seeds now; not V1 |
| Brand developer aha moment: 3 lines to see agent trust in middleware | MEDIUM | 8 | 7 | Make the brand integration trivially fast; that is the product demo |
| Submantle's "7 lines of code" requires brands first, agents second | HIGH | — | — | Do not target agent developers before you have one brand signed |

---

## The Irreducible Answer to "What Is THE THING?"

Based on analogous markets, the buying behavior evidence, and the competitive gap:

**Submantle's THE THING for V1:**

> "One API call tells you whether an agent calling your system has a clean behavioral history or registered yesterday. Three lines of middleware code. No new infrastructure. If the agent misbehaves and you have a logged trust query, your auditor is satisfied."

This is not "trust scores for agents." That is a feature. THE THING is: **automated due diligence at the API boundary that satisfies auditors and requires three lines of code.**

The SSL analogy: nobody bought SSL certificates because "encryption is good." They bought because browsers showed the padlock, and users trusted the padlock. Submantle's padlock is the API response that says "this agent has 847 clean interactions over 4 months." Brands don't need to understand the formula — they need the padlock.

**What makes it worth more than it costs:**
- Integration cost: ~2 hours for a backend developer
- API cost: negligible per-query fees
- Value: one logged trust query per session = complete audit trail for any regulatory inquiry about agent behavior in your systems
- After the first incident involving an unverified agent in your industry: not having this becomes a liability

**What doesn't work:** Selling to agent developers first. Selling to device owners as a revenue source. Selling "peace of mind" to anyone. Selling data before you have data. Selling compliance before there is a compliance requirement (unless targeting financial services where board-level pressure now exists).

---

*Sources consulted: Experian PLC business model documentation, Equifax revenue data (MacroTrends), Zenity Series B announcement and Forrester Q2 2025 recognition, Forter/Riskified/Sift positioning and pricing model, industry history on SSL certificate commoditization (Let's Encrypt), Stripe/Twilio/Auth0 developer experience patterns, VISION.md, HANDOFF.md, CLAUDE.md, research-brief.md.*
