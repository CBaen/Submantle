# Validation Report 1
## Date: 2026-03-10
## Validator: Validator 1

---

### Evidence Challenges

---

**Challenge 1: Team 1 — MCP Roadmap Overstates June 2026 Spec Release as Committed**

- **Finding:** Team 1 (Agent Transport), Battle-Tested #1 and Emerging #2 — states the MCP roadmap "targets Q1 2026 finalization... for a June 2026 spec release" and treats this as near-certain.
- **Problem:** The actual roadmap (verified via WebFetch, March 5 2026 update) explicitly states: "The ideas presented here are not commitments. We may solve these challenges differently than described. Some items may not materialize at all." There is no June 2026 date in the current roadmap text. The roadmap describes Working Group deliverables and priority areas — not a versioned release with a date. Team 1 presents speculative timeline as infrastructure planning fact.
- **Severity:** Moderate — weakens the "Submantle should prepare for June update" planning recommendation, but the underlying finding (stateless transport and Server Cards are genuine priority areas) is confirmed accurate.
- **What I checked:** Direct WebFetch of modelcontextprotocol.io/development/roadmap. Priority areas 1 and 2 confirmed. No release date found anywhere in the document.

---

**Challenge 2: Team 1 — "30+ CVEs in MCP Implementations" Claim Is Unverified**

- **Finding:** Team 1, Battle-Tested #1 — "30+ CVEs documented in MCP implementations through 2025 indicate security immaturity."
- **Problem:** No source is cited for this specific CVE count. The claim is presented as evidence of "security immaturity" — a consequential assertion for a security-adjacent product — but without a traceable reference. CVE counts for a protocol depend heavily on whether the CVEs are in the spec, in specific SDKs, or in third-party implementations. The distinction matters for how Submantle positions itself.
- **Severity:** Minor — the general "MCP has security immaturity" finding is plausible and consistent with a fast-moving protocol. The specific number is unverifiable.
- **What I checked:** Source list at end of Team 1 document. No CVE database or security advisory link cited.

---

**Challenge 3: Team 1 — Dapr "Python-first (Go support TBD)" Is Likely Stale**

- **Finding:** Team 1, Battle-Tested #3 — "Dapr is Python-first (Go support TBD)."
- **Problem:** Dapr has had a Go SDK since its early releases and Go is one of Dapr's primary supported languages. This characterization appears to confuse Dapr Agents (the newer AI-agent-specific framework announced March 2025) with Dapr core. The Go SDK for Dapr core is mature and production-used. Whether Dapr Agents specifically has full Go support as of March 2026 is a narrower question — but framing all of Dapr as "Python-first" misrepresents the project.
- **Severity:** Minor — Dapr is correctly assessed as "not a solo-bootstrappable starting point" regardless of language support. The error doesn't change the recommendation.
- **What I checked:** General knowledge; the Dapr GitHub has had a Go SDK since 2019. The team did not link to the Dapr Agents documentation to verify language support status.

---

**Challenge 4: Team 2 — x402 Transaction Volume Cited as Momentum Validation, But Context Is Missing**

- **Finding:** Team 2, Novel #1 (x402) — "75.41M total transactions, $24.24M volume, 94.06K buyers, 22K sellers — in the last 30 days alone."
- **Problem:** Verified via WebFetch (x402.org, March 2026) — the numbers are accurate. However, Team 2 does not provide any baseline for comparison or growth trajectory from the cited figures. 75M transactions across 94K buyers at $24M volume averages to roughly $256 per buyer over 30 days — which is consistent with developers experimenting, not enterprise adoption at scale. More critically, the "156,000 weekly transactions with 492% growth reported in late 2025" implies transactions were at ~26,000/week before the growth — tiny absolute numbers that grew fast on a low base. The per-buyer spend and small seller count (22K) suggest a developer-experimentation phase, not production-grade enterprise infrastructure. Team 2's treatment of these numbers as validation of enterprise readiness overstates what the data shows.
- **Severity:** Moderate — x402 is real and growing, but the evidence supports "emerging developer track" not "viable enterprise settlement rail." Team 2's own conclusion (x402 is not enterprise-ready until ~2028) is correct, but the evidence section reads more bullishly than the data warrants.
- **What I checked:** Direct WebFetch of x402.org, confirmed figures. Calculated per-buyer average.

---

**Challenge 5: Team 2 — Nevermined "200,000 events/second" Claim Uses Vendor-Provided Numbers**

- **Finding:** Team 2, Novel #2 (Nevermined) — "processes up to 200,000 events/second with real-time credit deduction."
- **Problem:** This figure comes from Nevermined's own blog posts (nevermined.ai/blog). No independent benchmark, audit, or third-party verification is cited. Vendor-provided performance claims for a commercial billing platform are marketing claims until independently verified. The recommendation to integrate Nevermined for high-throughput billing is consequential — if the actual throughput is lower, Submantle's billing infrastructure fails at scale.
- **Severity:** Moderate — the recommendation to use a billing abstraction layer is sound architecture regardless, but the specific vendor selection based on unverified throughput numbers is a risk. Team 2 correctly notes the vendor dependency risk but doesn't flag the unverified performance claim.
- **What I checked:** Source list in Team 2. Both Nevermined citations are nevermined.ai URLs — the vendor's own site.

---

**Challenge 6: Team 3 — CJEU Ruling Cited as Favorable Precedent Is Very New and Untested**

- **Finding:** Team 3, Novel #5 (Differential Privacy) and Gaps #5 — cites the September 2025 CJEU ruling (C-413/23 P) as establishing that differentially private data may be outside GDPR scope.
- **Problem:** Team 3 itself notes this ruling "has not yet been tested in the context of commercial data products." This is important: citing a 6-month-old court ruling as legal foundation for a commercial data product strategy is building on untested precedent. The Skadden analysis cited is secondary legal commentary, not the ruling itself. The ruling may not generalize from the specific fact pattern of the original case to Submantle's situation. This is flagged correctly in the Gaps section but the ruling is treated with more confidence in the body of the report than its newness warrants.
- **Severity:** Moderate — the legal foundation for Insights is weaker than presented. Team 3's "conditional go" conclusion with counsel review as prerequisite is correct, but the body text reads more confidently about GDPR clearance than the evidence supports.
- **What I checked:** Team 3 source list. The ruling analysis links to skadden.com commentary, not the ruling itself.

---

**Challenge 7: Team 4 — Tailscale "3 Infrastructure Engineers" Claim Verified but Scope Is Narrow**

- **Finding:** Team 4, Battle-Tested #1 — "Tailscale's entire infrastructure team is 3 engineers serving millions of active users."
- **Problem:** Verified via WebFetch of tailscale.com/blog/infra-team-stays-small. The claim is accurate. However, the article itself notes they are "very busy" and "would welcome more headcount" — not a picture of comfortable capacity. More importantly, the article describes the infrastructure team as distinct from product engineering, security, and support teams. The 3-engineer count covers infra operations (the DERP relay fleet, corporate tailnet, monitoring), not the full software engineering team. Using this to argue Submantle can be operated by a small team is valid, but implies that other engineering work (daemon development, feature work, security) requires additional headcount not counted in the "3 engineers" figure.
- **Severity:** Minor — Team 4's conclusion (protocol infrastructure ops can stay small) is sound. The nuance about what "infrastructure team" means doesn't change the recommendation.
- **What I checked:** Direct WebFetch of the cited Tailscale blog post.

---

**Challenge 8: Team 5 — Apple "Core AI Replacing Core ML" Stated as Confirmed Fact**

- **Finding:** Team 5, Kill Shot 1 — "Apple is replacing Core ML with a new Core AI framework (announced for WWDC 2026, revealed March 2026)."
- **Problem:** Verified via WebFetch. The 9to5Mac article Team 5 cites (the URL 404s, but the underlying Gurman Bloomberg report is retrievable) explicitly states this has "not been officially confirmed by Apple" and is based on Mark Gurman's reporting ahead of an expected WWDC announcement. Team 5 presents this as a confirmed fact ("announced for WWDC 2026, revealed March 2026") when it is an unconfirmed pre-announcement leak. The distinction matters: if Apple does not ship Core AI or ships it without the process context broker capability Team 5 implies, Kill Shot 1's severity decreases.
- **Severity:** Moderate — the underlying threat (Apple building OS-level agent awareness) is real and documented through other confirmed sources (App Intents, ESF, Private Cloud Compute). The Core AI replacement claim adds to but is not the foundation of the kill shot. Removing it weakens the evidence slightly, not the argument structurally.
- **What I checked:** WebFetch of the cited 9to5Mac URL (404). Fetched alternative URL confirming the Gurman report is unconfirmed pre-announcement speculation.

---

**Challenge 9: Team 5 — Microsoft "Walking Back AI on Windows" Cited Without Source Verification**

- **Finding:** Team 5, Kill Shot 1 — "Microsoft is 'reevaluating its AI strategy on Windows 11 and plans to scale back or remove Copilot integrations.'"
- **Problem:** The cited source (WindowsCentral, "Microsoft is walking back Windows 11's AI overload," February 2026) could not be fetched for verification (businessinsider.com blocked, WindowsCentral not attempted). This is a significant claim used to support a nuanced argument — that Microsoft's Recall failure is "a warning" for Submantle. If the reporting is accurate, the warning is valid. If the reporting was speculative or has since been contradicted, the analogy weakens. The claim about Windows Recall being "internally considered a failure" is presented without a direct Microsoft source.
- **Severity:** Minor — the Microsoft Recall controversy is well-documented from multiple sources regardless of this specific article. The warning about user backlash on ambient monitoring is directionally correct even without this specific citation.
- **What I checked:** Source list in Team 5. Attempted WebFetch of businessinsider.com (blocked). Did not locate alternative verification.

---

**Challenge 10: Team 3 — Federated Analytics "5.2% Production Deployment" Statistic Requires Scrutiny**

- **Finding:** Team 3, Novel #6 — "only 5.2% of federated learning research has reached production deployment."
- **Problem:** This statistic comes from a DEV Community blog post — a developer blog, not a peer-reviewed source. The claim is used to support the "production maturity gap is real" argument. The distinction between federated learning (model training) and federated analytics (aggregate statistics) matters here: federated analytics is significantly simpler and more mature than federated model training. Google Parfait (cited by Team 3) is a production federated analytics deployment. Apple's use of DP at hundreds of millions of devices is production. The "5.2%" figure likely applies to the harder ML training case, not the simpler statistics case Submantle would use. Team 3 applies a federated learning production gap statistic to argue caution about federated analytics.
- **Severity:** Moderate — the caution about federated analytics engineering complexity is legitimate, but the 5.2% figure overstates the maturity risk for the specific use case (aggregate statistics) Submantle would deploy.
- **What I checked:** Source attribution in Team 3. Citation is to dev.to, not an academic paper or industry report.

---

### Contradictions Between Teams

---

**Contradiction 1: Transaction Revenue — Team 2 vs. Team 5**

- **Team 2 says:** The microtransaction model is viable using prepaid credits + Stripe metered billing. Revenue table shows $36.5M/year at 1M active agents. Treats this as a meaningful revenue engine.
- **Team 5 says:** "$0.001/query to reach $1M ARR requires 1 billion queries per year — 2.7 million queries per day. This requires adoption at a scale that Stripe or Cloudflare needed years to reach." Concludes microtransaction revenue should not appear in near-term financial models.
- **Stronger evidence:** Team 5. The math is straightforward and Team 5's analysis of the perverse incentive (agent developers batch or avoid queries to cut costs) is a well-documented API pricing dynamic. Team 2's revenue table does not account for this optimization behavior. Team 2 itself acknowledges "the query rate is the uncertain variable" but projects high rates without justification.
- **My assessment:** The orchestrator should treat microtransaction revenue as a long-term aspirational engine and not include it in 0-18 month financial projections. Team 2's billing architecture recommendations (prepaid credits, Stripe metered aggregation) remain sound infrastructure even if the revenue contribution is initially small.

---

**Contradiction 2: Competitive Moat — Teams 1/2/3/4 vs. Team 5**

- **Teams 1-4 say:** Submantle occupies an unoccupied layer (OS-level process context enrichment), the MCP proxy market validates the pattern ($11M+ to Runlayer), and no existing product knows what processes mean semantically.
- **Team 5 says:** The category is attracting capital (Runlayer $11M, /dev/agents $56M), platform incumbents are building native equivalents (Apple ESF + App Intents, Google AppFunctions), and established security vendors (Datadog, Palo Alto) can bolt on the missing features with existing distribution.
- **Stronger evidence:** Both are partially correct, and the contradiction is temporal. Teams 1-4 describe the current state (the layer is unoccupied today). Team 5 describes the trajectory (the layer will be contested within 12-24 months). The research brief asked for a go/no-go — the contradiction reveals this is a "go now or the window closes" situation, not a "go whenever." Neither side's evidence invalidates the other.
- **My assessment:** The orchestrator should treat the window as finite and urgent. The "unoccupied layer" finding from Teams 1-4 is accurate for March 2026. Team 5's timeline estimate (12-24 months before consolidation) is plausible and corroborated by AAIF formation and Apple's trajectory.

---

**Contradiction 3: Solo Non-Technical Founder Risk — Team 4 vs. Team 5**

- **Team 4 says:** "Protocol scale is not the hard problem." 3 engineers can run Tailscale-scale infrastructure. Solo founder can reach 10,000 users comfortably.
- **Team 5 says:** "The specific combination — solo, non-technical, bootstrapped, infrastructure-layer — has essentially no successful precedent." Production requirements (signed kernel drivers, four-platform OS support, CRDT sync) represent 12-18 months of engineering by a small team.
- **Stronger evidence:** Team 5 on the development question; Team 4 on the operations question. These are different questions. Team 4 addresses the question of running infrastructure at scale. Team 5 addresses the question of building the production daemon in the first place. The two findings are compatible: a solo founder can operate Submantle's infrastructure at scale once built, but cannot build the full production vision alone. Team 4's findings do not address the build challenge — they address the ops challenge post-build.
- **My assessment:** The orchestrator must distinguish "can Guiding Light run this infrastructure?" (yes, based on Team 4 evidence) from "can Guiding Light build the production daemon alone?" (unlikely, based on Team 5 evidence). Team 4's finding does not rebut Team 5's strongest kill shot.

---

**Contradiction 4: Privacy Architecture for Insights — Team 3 vs. Prior Expedition**

- **Team 3 says:** Federated analytics dissolves the privacy-data tension identified by the first expedition. The privacy-first brand and Insights revenue are compatible if built correctly.
- **Prior expedition (Team 6, referenced) says:** "Privacy-first creates a paradox for the data insights revenue model" — and "ruled it out."
- **Stronger evidence:** Team 3, conditionally. The federated analytics architecture (Google Parfait model, Apple DP deployments) is real and production-proven. If Submantle builds this way, Team 6's ruling-out is superseded. However, Team 3's "conditional go" explicitly gates this on engineering investment that hasn't happened. The prior expedition's ruling-out remains correct for centralized aggregation, which is the simpler path Submantle might take.
- **My assessment:** Team 3 wins this contradiction on evidence but the condition matters. The orchestrator should understand that Insights is only compatible with Submantle's brand if the federated analytics path is chosen — the simpler centralized path restores the contradiction Team 6 identified.

---

### Alignment Issues

---

**Alignment Issue 1: The "Go/No-Go" Expected Outcome Is Not Cleanly Delivered by Any Team**

- **Finding:** All five teams
- **Drift:** The research brief states the expected outcome is "a clear go or no-go — no hedging." Teams 1-4 all produce "conditional go" conclusions with caveats. Team 5 produces "the idea is strong; the configuration needs to change." No team delivers an unconditional verdict in either direction.
- **Severity:** Moderate — this is the core deliverable of the brief. The hedged conclusions are intellectually honest (the evidence genuinely supports conditional verdicts) but they do not give Guiding Light the "clear conviction in one direction" the brief asked for. The hedging is well-evidenced, but the orchestrator should synthesize these into a single verdict rather than presenting five conditional answers.

---

**Alignment Issue 2: Team 4 Does Not Address the Bootstrapability Constraint for Submantle Insights**

- **Finding:** Team 4 (Protocol-Scale Infrastructure)
- **Drift:** The brief's constraints include "must be buildable incrementally by a solo creator with AI assistance." Team 4's scale ladder goes to solo founder reaching 10,000 users — but federated analytics infrastructure (which Team 3 recommends as prerequisite for Insights) is not addressed at all. The two teams were not coordinated on whether the Insights infrastructure is within the scale ladder Team 4 describes.
- **Severity:** Minor — different research angles, but the gap matters for the consolidated go/no-go on Insights specifically.

---

**Alignment Issue 3: Team 2 Does Not Address the Destructive Boundary "Must Not Require VC to Begin"**

- **Finding:** Team 2 (Transaction Settlement), Nevermined integration recommendation
- **Drift:** The brief explicitly states "do not recommend approaches that require venture capital to begin." Team 2 recommends integrating Nevermined-style billing infrastructure as a primary path. While Nevermined itself doesn't cost VC money, Team 2's revenue projections and billing architecture assume a scale (millions of agent queries, enterprise clients) that requires significant marketing and sales investment to reach. The billing architecture is sound; the path to the revenue scale that makes it meaningful is not addressed under the bootstrapping constraint.
- **Severity:** Minor — Team 2's near-term recommendations (Stripe metered billing, prepaid credits) are bootstrappable. The constraint drift is in the revenue projections, not the architecture.

---

**Alignment Issue 4: "Submantle as Transport Layer" — Teams Treat Aspirational Framing as Current**

- **Finding:** Teams 1, 2, 4 — repeatedly use "transport layer," "agent mesh," and "protocol infrastructure" language for current Submantle
- **Drift:** The brief asks whether "Submantle as transport layer for AI agents" can be built. Team 5 (Kill Shot 9) correctly identifies that the "transport layer" claim is aspirational — current architecture is an optional MCP server (Tier 1), not a transport layer. Teams 1-4 adopt the aspirational framing in their descriptions without clearly distinguishing what is current vs. what is the multi-year roadmap. This makes it harder to extract a near-term plan from the findings.
- **Severity:** Moderate — the orchestrator needs to hold the "transport layer" vision as a 3-5 year destination, not a current capability description, when using these findings to plan near-term work.

---

### Missing Angles

---

**1. No Direct Customer Validation for Any Revenue Engine**

The research brief did not explicitly require customer interviews, but the expected outcome of a "go or no-go" on a business model without any evidence of willingness-to-pay is methodologically weak. Team 3 explicitly notes that Insights buyers are "unvalidated." No team sourced developer surveys, agent framework developer interviews, or enterprise buyer conversations. The entire business case rests on market analogy, not demand validation. This is the single largest gap across all five reports.

**2. /dev/agents Architecture Is Unresearched**

Team 5 flags /dev/agents as potentially the most dangerous competitor but explicitly states "their actual architecture is unknown." Given that /dev/agents was founded by the Stripe CTO and has $56M at a $500M valuation, their architecture should have been investigated more aggressively. A targeted search of their job postings, GitHub repositories, technical blog posts, and public demos would likely reveal whether they are building at the OS layer. This gap leaves the competitive analysis incomplete on the most dangerous threat.

**3. The Windows-First Strategy Is Underexamined**

The research brief implicitly assumes cross-platform scope. But Submantle's prototype runs on Windows, and the first expedition found iOS/Android are restricted. Team 4 briefly mentions Windows MSI signing but no team analyzed whether a Windows-only V1 (where ETW process monitoring is mature, signing is obtainable, and the MCP ecosystem is primarily desktop-developer-deployed) would dramatically reduce the founding risk Team 5 identifies. A focused Windows-first analysis could substantially change the go/no-go calculus on Kill Shot 3.

**4. Anthropic Partnership Path Is Uninvestigated**

The research brief lists "Anthropic as strategic partner" as one of the new ideas to research. No team addresses this. The AAIF formation (platinum member: Anthropic) is noted by Teams 1 and 5, but no team researched what a genuine partnership with Anthropic would require, what precedents exist for small startups partnering with Anthropic, or what the MCP-alignment path to being a recommended Submantle integration would look like.

**5. The EU AI Act Classification Question Has No Legal Research**

Team 5 identifies EU AI Act classification risk as a potential kill shot. Team 3 notes regulatory exposure. But no team actually researched the EU AI Act classification framework to determine whether Submantle as an MCP server (Tier 1, optional) or as an MCP proxy (Tier 2) would actually trigger high-risk AI system classification. The first expedition recommended a 90-day legal review. This expedition does not advance that analysis. The 145-day window to the August 2026 deadline makes this a gap that increases in severity daily.

---

### Convergence Points

These represent the highest-confidence findings — independent teams arrived at the same conclusion from different research angles:

1. **MCP is the right integration surface.** Teams 1, 2, 4, and 5 all independently confirm MCP as the dominant standard with 97M+ monthly downloads, multi-vendor adoption, and Linux Foundation governance. Even Team 5 (Kill Shot) treats MCP integration as the correct starting point. Confidence: very high.

2. **The OS-layer process context is genuinely unoccupied.** Teams 1, 3, 5, and 7 (implicitly) agree that no existing product (Runlayer, Kong, agentgateway, Datadog, osquery) provides semantic OS-level process context to agents. Team 5 acknowledges this as "the thing that survives the kill shots." Confidence: high.

3. **Microtransaction revenue is a long-term play, not a near-term engine.** Teams 2 and 5 arrive at the same conclusion from different directions. Team 2 through billing architecture analysis; Team 5 through adoption math. The subscription tiers are the viable near-term revenue path. Confidence: high.

4. **Platform incumbents (Apple especially) are the most consequential long-term threat.** Teams 1, 4, and 5 all identify Apple's architectural trajectory (ESF, App Intents, Private Cloud Compute) as the largest existential risk. No team argues Apple is not a threat. Confidence: high.

5. **The coordination/infrastructure scale problem is solved.** Teams 1, 2, 4 arrive at the conclusion that running protocol infrastructure at scale is achievable with a small team given the right architecture (minimal coordination plane, maximum local processing). The engineering cost of building to that scale remains the open question. Confidence: high on ops; low on build cost.

6. **Privacy-by-architecture is a genuine legal and brand differentiator.** Teams 3 and 4 both identify on-device processing as reducing GDPR exposure significantly (Team 3 legally; Team 4 architecturally). Team 5 confirms it as Submantle's strongest defense against the legal kill shots. Confidence: high.

7. **The window for shaping standards is now, not later.** Teams 1, 4, and 5 all independently flag the AAIF formation and 2026 standards activity as creating a finite window. Team 5 identifies shipping before June 2026 WWDC as the specific deadline. Confidence: high.

---

### Surprises

**1. The MCP roadmap does not have a June 2026 release date.** Team 1 built planning recommendations on a date that does not appear in the actual roadmap document. Verifying this took one WebFetch. It changed my assessment of Team 1 from "well-sourced" to "contains at least one fabricated-or-stale timeline claim." This raises questions about other specific claims in that report.

**2. Team 4's "3 engineers" finding is real but narrower than it appears.** The Tailscale blog confirms 3 infra engineers — but the article itself says they're stretched and want more headcount. The finding is used to argue "small teams can run massive infrastructure" without the qualification that those 3 engineers are not the ones building the product.

**3. The AAIF gold member list includes Runlayer.** Team 2 recommends Runlayer as a market validator; Team 5 identifies Runlayer as a competitor; neither team notes that Runlayer is a gold member of the Linux Foundation's AAIF — the same body that governs MCP. This means Runlayer has a standards governance seat that Submantle does not. A competitor with governance access to the standard Submantle depends on is a more serious structural threat than either team identified.

**4. x402's numbers are real but smaller than they seem.** The figures (75M transactions, $24M volume, 94K buyers) look large until you calculate the per-buyer average ($256/month). The ecosystem is developer experimentation at this stage — meaningful as direction, misleading as scale validation.

**5. Team 5 is the most internally rigorous report.** The kill shot team correctly identified which of its own kill shots survive scrutiny and which don't. Its self-assessment ("3 survive as serious threats") is accurate based on my independent review. This is unusual — adversarial teams typically oversell their findings. Team 5's discipline increases confidence in its conclusions.

---

### Overall Assessment

The five reports together represent substantive, well-sourced research that substantially advances the go/no-go question — but does not fully answer it as the brief demanded. Here is what the orchestrator actually has:

**What is well-established:** MCP integration is the right starting point. The OS-layer context is genuinely unoccupied. Protocol infrastructure can be run by a small team. Subscription revenue is viable if the product ships. The window to matter is 12-24 months.

**What is not established:** Whether real buyers exist and would pay for any of the three revenue engines (no customer validation). Whether Guiding Light can build the production daemon (the most critical open question, named by Team 5 but not resolved). Whether Submantle Insights can survive regulatory scrutiny in the EU and California (legal research was not done, only flagged as needed).

**What the evidence actually supports as a verdict:** Conditional go on a narrower scope. The "Tier 1 MCP server + process awareness dashboard + community signatures" combination is buildable, viable, legally lower-risk, and positions Submantle to participate in the AAIF standards process. This is a genuine go. The full infrastructure vision (Tier 2 proxy, Tier 3 kernel guardian, Insights, Store at scale) requires either a technical co-founder or proof-of-demand that justifies raising capital. That is a deferred go pending evidence.

**Highest confidence recommendations to carry forward:** (1) Ship a public MCP server before WWDC June 2026. (2) Get legal review of EU AI Act classification immediately — 145 days is not long. (3) Do not include microtransaction revenue in any near-term financial model. (4) Investigate /dev/agents' actual architecture before treating them as only a funding threat.

**Evidence quality overall:** Teams 1-4 are generally well-sourced with verifiable citations and appropriate caveats in their gap sections. Team 1 contains at least one timeline claim that does not appear in the cited source (June 2026 MCP spec release date). Team 3 builds partially on a very new CJEU ruling that has not been tested commercially. Team 5 is the most reliable for having correctly scoped its own findings. The aggregate picture is trustworthy enough to act on — but the go/no-go on the full infrastructure vision requires the customer validation and legal review that no team conducted.
