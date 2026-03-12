# Team 3 Findings: Submantle Insights — The Usage Intelligence Play
## Date: 2026-03-10
## Researcher: Team Member 3

---

## Framing Note

"Google knows what people search for. Submantle knows what people actually use." This framing is commercially compelling — but it needs to be surgically examined. There is a real market for aggregated usage intelligence. There are also real legal landmines and a specific tension with Submantle's own privacy-first brand. This report lays out the landscape with evidence and does not hedge on the hard questions.

---

## Battle-Tested Approaches

### 1. Subscription-Based Aggregated Intelligence (Similarweb / Comscore / Nielsen Model)

- **What:** Sell access to aggregated intelligence reports and API feeds under recurring subscription contracts, never selling raw data or revealing individual-level behavior.
- **Evidence:** Similarweb (SMWB) generated $282.6M in full-year 2025 revenue (+13% YoY), with 6,128 customers and 454 accounts at $100K+ ARR representing 63% of total ARR. Multi-year subscriptions now constitute 60% of ARR (up from 49%). The company describes itself explicitly as "at its core a data business" and operates a Data-as-a-Service (DaaS) arm in addition to SaaS tooling. Comscore generated $360-370M in 2025 revenue from measurement subscriptions, with 20% YoY growth in cross-platform solutions. NIQ (NielsenIQ) reported Annualized Intelligence Subscription revenue of $2,877.1M in 2025, growing 6.6% YoY, serving 23,000 clients including 80% of Fortune 100 companies.
- **Source:** Similarweb Q4 2025 earnings (BusinessWire, February 2026); Comscore Q3 2025 results (Comscore IR, October 2025); NIQ FY2025 results (BusinessWire, February 2026)
- **Fits our case because:** Submantle's awareness data — "what processes run together on devices at scale" — maps directly to the intelligence these companies sell about "what websites and apps people use." The subscription model is proven. The DaaS tier (raw API data feeds) unlocks enterprise analytics teams. The analogy is strong: Similarweb knows what websites get traffic; Submantle knows what software actually runs.
- **Tradeoffs:** Similarweb had a 2025 net loss of $32.9M despite $282.6M revenue — data collection, cleaning, and enrichment infrastructure is expensive to maintain. At Submantle's scale-up phase, the margin profile of a data business is worse than SaaS until sufficient data volume makes the collection infrastructure nearly fixed-cost.

---

### 2. Technology Intelligence / Technographics (BuiltWith / SimilarTech Model)

- **What:** Provide intelligence about what software/technology companies and users run, primarily for B2B sales, marketing, and competitive intelligence use cases.
- **Evidence:** The technographics market grew from ~$367M (2020) to $1.17B (2025) at a 26.1% CAGR — growing 2-3x faster than the broader software market. BuiltWith tracks 85,000+ technologies across 673 million websites at prices from $295-$995/month. SimilarTech (a Similarweb company) tracks 5,000+ technologies and prices from $200-$490/month. "Over 80% of businesses now incorporate technographics into their decision-making." Companies using this data report 50% higher likelihood of exceeding revenue goals, 28% higher conversion rates, and 27% shorter sales cycles.
- **Source:** TechnologyChecker.io industry statistics report (2025); SimilarTech pricing via Research.com (2026); BuiltWith pricing via BuiltWith.com
- **Fits our case because:** This is the closest structural analog to "Submantle Insights." What BuiltWith does for websites — "this company runs Shopify + Klaviyo + Gorgias" — Submantle could do for desktop software at a far deeper level of accuracy. Desktop software co-occurrence data ("45% of ComfyUI users also run Blender") does not exist commercially today. Submantle would own this category.
- **Tradeoffs:** BuiltWith's data is scraped from public sources (HTML, DNS, CDN headers). Submantle's data comes from on-device monitoring with user consent — meaningfully more accurate, but also more legally complex to aggregate and sell. The buyers for technographic data are primarily B2B sales teams, not individual users. This limits the initial monetization path to enterprise intelligence contracts, not mass-market subscriptions.

---

### 3. Panel-Based Measurement with Explicit Consent (Nielsen / Comscore Model)

- **What:** Recruit a panel of consenting users who agree to detailed monitoring; aggregate their behavior into statistically representative intelligence; sell the aggregate to media buyers, product companies, and advertisers.
- **Evidence:** Nielsen's Big Data + Panel product now covers 45 million households and 75 million devices (as of January 2025 MRC accreditation). Nielsen maintains approximately 90% market share in TV audience measurement. Comscore's panel model is built on "affirmative consent from panelists" — panel members are recruited, disclosed the full scope of monitoring, and compensated or incentivized. NIQ's consumer panel covers 250,000+ households across 25 countries.
- **Source:** Nielsen Big Data + Panel (SportsmediaWatch, December 2025); Comscore privacy framework (comscore.com); NIQ Homescan panel description (NIQ.com)
- **Fits our case because:** Submantle's opt-in architecture is structurally compatible with a panel model. Users who install Submantle and consent to aggregate contribution are precisely the panel structure Nielsen and Comscore use. The key difference is that Submantle's panel would know what *software* users run, not what *TV* they watch — a genuinely novel data signal with no current market equivalent.
- **Tradeoffs:** Panel-based measurement requires active panel recruitment and management. Nielsen's infrastructure cost for maintaining a 75M device panel is substantial. For Submantle, the panel is "free" if organic installs opt in — but panel size matters: statistical representativeness requires hundreds of thousands of devices minimum before the data is credible to enterprise buyers.

---

### 4. Alternative Data for Investment Decisions

- **What:** Sell behavioral/usage data to hedge funds and asset managers who use it to gain trading edge — the "alternative data" industry.
- **Evidence:** The global alternative data market was valued at $14-$18B in 2025, growing at 50%+ CAGR with projections of $135B by 2030. Over 70% of hedge funds now use alternative data, up from 30% a decade ago. Hedge funds allocate an average of $1.6M/year toward alternative data. Credit card transaction data commands the largest share at 18.3% of the market. The broader alternative data ecosystem encompasses satellite imagery, geolocation tracking, web traffic, social media sentiment, and IoT sensor data — but software usage at desktop level is **not yet a named category**.
- **Source:** Integrity Research alternative data industry analysis (accessed March 2026); Precedence Research alternative data market report (2025); ExtractAlpha alternative data sources for hedge funds (July 2025); HedgeCo "Influence of AI, Alternative Data, and ESG on Hedge Fund Strategy in 2025"
- **Fits our case because:** Software usage patterns are a genuine leading indicator of enterprise technology adoption, which is investable information. "What software is replacing what other software" measured across millions of devices is the kind of signal that doesn't exist in any current financial data product. A hedge fund that could see rising ComfyUI + GPU cluster usage months before Nvidia's next earnings call would pay for that signal.
- **Tradeoffs:** The alternative data buyer relationship is relationship-intensive and often requires exclusivity negotiations. The data must be clean, structured, and delivered via API or data feed — significant engineering. Privacy compliance in this context is paramount: the SEC has active guidance on alternative data that prohibits material non-public information. Submantle must ensure its aggregated signals are truly aggregate (no individual-company identification) and not MNPI.

---

## Novel Approaches

### 5. Differential Privacy as the Legal and Technical Foundation

- **What:** Apply differential privacy (DP) to all aggregate signal generation, making individual re-identification mathematically infeasible, while retaining statistically valid population-level insights.
- **Why it's interesting:** Differential privacy has been deployed at production scale by Apple (hundreds of millions of iOS/macOS devices, since 2016), Google (RAPPOR in Chrome, Gboard via Federated Analytics, Maps busyness data), the US Census Bureau (2020 Census), and Mozilla Firefox (DPrio). It is not theoretical — it is the state-of-the-art privacy tool used by the world's largest data collection operations. Under the September 2025 CJEU ruling (C-413/23 P), pseudonymized data is not personal data for the *recipient* if the recipient cannot realistically re-identify individuals. Differentially private outputs are the strongest possible version of this — re-identification is not just contractually or technically difficult, it is mathematically proven infeasible.
- **Evidence:** Apple deploys DP at hundreds of millions of users for emoji, health type, and Safari domain collection. Epsilon values used in practice (Apple: epsilon=4 for Safari domain data, with daily privacy budget limiting records per use case). US Census Bureau adopted DP for 2020 Census after discovering 2010 data could reconstruct 300M individuals from public tables. CJEU September 2025 ruling establishes that data truly not re-identifiable is outside GDPR scope for the recipient. NIST SP 800-226 provides federal guidance on evaluating DP guarantees (published 2023, remains current).
- **Source:** Apple Machine Learning Research, "Learning with Privacy at Scale" (machinelearning.apple.com); Apple Differential Privacy Overview PDF (cdn.arstechnica.net, 2025); Privacy Guides, "What is Differential Privacy?" (September 2025); CJEU case C-413/23 P analysis (Skadden, November 2025); NIST SP 800-226
- **Fits our case because:** Submantle Insights outputs (e.g., "45% of ComfyUI users run Blender") are naturally differentially private statistics — they are population-level claims, not individual-level claims. If Submantle generates these statistics using a DP mechanism (adding calibrated noise to individual device contributions before aggregation), the outputs are both legally robust and genuinely privacy-preserving. This resolves the core tension between "privacy-first brand" and "monetizing aggregate data."
- **Risks:** Differential privacy introduces noise that reduces statistical precision. For small population segments (e.g., "users of a very niche software in a specific country"), the noise may render the statistic meaningless. The privacy-utility tradeoff is real: high epsilon = more utility, less privacy; low epsilon = less utility, more privacy. Apple uses epsilon=4 for Safari domains — an epsilon level that privacy researchers have critiqued as providing weaker-than-ideal protection (Access Now, "Differential Privacy Part 3," 2019 — still relevant). Submantle must decide where on the epsilon spectrum to operate and be prepared to defend that choice to regulators.

---

### 6. Federated Analytics (No Raw Data Ever Leaves the Device)

- **What:** Rather than collecting data to a central server and then aggregating, the aggregation happens on-device with only the summary statistics (not raw records) transmitted. Google calls this "Federated Analytics" and has deployed it in production via Google Parfait.
- **Why it's interesting:** In federated analytics, each device answers a query locally (e.g., "do you run ComfyUI and Blender together?") and transmits only a privacy-preserving answer, not the underlying data. The server aggregates the answers across millions of devices. Google's Confidential Federated Analytics uses Trusted Execution Environments (TEEs) to further guarantee that the server operator cannot access individual responses. This is architecturally more private than traditional DP (where raw data reaches the server before noise is added) because raw data never leaves the device at all.
- **Evidence:** Google implemented Confidential Federated Analytics in production for Gboard (Android keyboard), with source code released as Google Parfait. Apple hosted the PPML 2025 workshop presenting "Local Pan-Privacy for Federated Analytics." The federated learning/analytics market is reaching $0.1B in 2025, projected at $1.6B by 2035 at 27% CAGR. However, only 5.2% of federated learning research has reached production deployment — the gap between research and production is real.
- **Source:** Google Research Blog, "Discovering new words with confidential federated analytics" (research.google); Apple Machine Learning Research, PPML 2025 workshop (machinelearning.apple.com); DEV Community, "Federated Learning in 2025: What You Need to Know" (dev.to)
- **Fits our case because:** Submantle already processes everything on-device. Extending this with federated analytics means Submantle's Insights product could be provably privacy-preserving by architecture — not just by policy. "We never collect raw data" is a stronger privacy claim than "we anonymize data before analysis." This is the strongest possible answer to GDPR scrutiny and user trust concerns. It also resolves Team 6's concern: "Privacy-first creates a paradox for the data insights revenue model" — federated analytics dissolves this paradox.
- **Risks:** Federated analytics is significantly more complex to engineer than centralized aggregation with post-hoc anonymization. The query infrastructure (what questions do you ask devices, how often, how do you validate results) requires substantial investment. The production maturity gap is real: 5.2% of FL research reaches production. GDPR Article 17 (right to erasure) creates a genuine unresolved technical problem if any form of model learning is involved — once a device contributes to a federated model update, removing that contribution requires retraining. This is less acute for pure federated statistics (not model training) — the query-and-aggregate pattern is more erasure-compatible than federated model training.

---

### 7. The "Submantle Insights API" — Selling to Product Companies, Not Advertisers

- **What:** Position aggregate software usage intelligence as a product intelligence product sold directly to software companies who want to understand their competitive ecosystem, not as advertising data sold to media buyers.
- **Why it's interesting:** The most valuable Submantle Insights outputs — "45% of ComfyUI users also run Blender" — are most valuable to the companies building those products (Stability AI, Blender Foundation, hardware manufacturers), not to advertisers. Product managers, competitive intelligence teams, and product marketing teams at software companies would pay for "what does our user's installed software ecosystem look like?" This creates a cleaner, more defensible monetization path that avoids the advertising data stigma and the regulatory complexity of behavioral advertising.
- **Evidence:** Technographic data companies (BuiltWith, SimilarTech) already prove this demand exists — but their data covers only *websites*, not desktop software. The technographics market grew to $1.17B in 2025. B2B information services reached $103M in 2025 (growing to $271.5M by 2034) with "over 70% of large enterprises relying on third-party B2B information platforms for risk assessment, compliance monitoring, and competitive intelligence." Sales intelligence market at $4.42B in 2025, growing to $8.19B by 2030. Hardware manufacturers (NVIDIA, Intel, AMD) would specifically value "what software uses GPU together with what other software" to inform hardware bundle strategy and driver optimization priorities.
- **Source:** TechnologyChecker.io industry statistics (2025); Market Reports World B2B Information Services Market (2025); Mordor Intelligence Sales Intelligence Market (2025)
- **Fits our case because:** This is the cleanest product-market fit for Submantle Insights. The buyer (a software company's product team) has a direct, identifiable budget (competitive intelligence, market research, product analytics). The use case is defensible (not advertising). The data asset (desktop software co-occurrence at scale) is genuinely unique — nothing like it exists. Hardware manufacturers in particular (NVIDIA, Qualcomm, Intel) would pay significant sums for "what software stacks actually run on GPU-equipped machines" because this directly informs chip design, driver support, and marketing bundle decisions.
- **Risks:** The sales cycle for enterprise intelligence contracts is long (90-180 days). The buyer is a product manager or competitive intelligence lead — not a data buyer with an existing alternative data budget. Submantle would need to educate buyers on what this data is and why they want it. First contract will be hard. Tenth will be easy.

---

## Emerging Approaches

### 8. AI Training Data Licensing

- **What:** License aggregated, privacy-preserved awareness data to AI companies who need diverse training signal about real-world software usage patterns.
- **Momentum:** Similarweb disclosed that "Gen AI and LLM training related revenues accounted for nearly 8% of Q2 2025 revenues and are one of the fastest growing revenue streams." The company's CEO stated: "Similarweb's unmatched view of the evolving digital world is a prime foundation for training and maintaining LLMs." Publicis Group purchased Lotame in June 2025, integrating 4 billion unique IDs into Epsilon's environment — consolidation driven partly by AI training data demand.
- **Source:** Similarweb Q4 2025 earnings release (BusinessWire, February 2026); Similarweb Q2 2025 earnings (BusinessWire, August 2025); Publicis/Lotame acquisition coverage (2025)
- **Fits our case because:** Submantle's awareness data — what software runs, in what context, with what process relationships — is exactly the kind of grounded, real-world behavioral signal that AI companies need for training agents to understand computing environments. An AI model trained on Submantle's awareness data would have a fundamentally better mental model of "what software ecosystems look like" than one trained on web text alone. This could be a meaningful secondary revenue stream with minimal additional engineering if the DP/federated analytics infrastructure is already in place.
- **Maturity risk:** AI training data licensing is a nascent market with unclear pricing precedents. The data must be properly licensed, anonymized, and documented in terms of provenance — AI companies are increasingly under scrutiny for training data sourcing. Submantle would need clear user consent language that covers "contributing anonymized signals for AI training purposes" — a separate consent bucket from "contributing to aggregate intelligence reports."

---

### 9. The "Privacy Report as a Product" Subscription

- **What:** Sell individuals a premium "Submantle Insights: Your Privacy Report" — showing them what their software ecosystem reveals about them and how it compares to the aggregate.
- **Momentum:** Privacy-first analytics platforms (Plausible, Fathom, PostHog) have successfully monetized on the basis of giving users visibility rather than extracting data from them. Plausible has reached $2M+ ARR with a $9/month starting price. PostHog targets $100M ARR from its full-stack product analytics suite. The privacy-as-feature premium is real: the market for no-tracker, consent-first analytics tools is growing.
- **Source:** Userbird "Google Analytics Alternatives by Revenue" (2025); Legal-Forge "Privacy-First Analytics Alternatives 2026" (2026)
- **Fits our case because:** Submantle's free tier already gives users personal awareness. A premium "Insights" subscription — "here's what your software stack says about you, here's how it compares to people like you, here's what's unusual about your setup" — creates a compelling upsell without requiring any data to leave the device. The aggregate comparison ("you're in the top 5% of complex software stacks") is generated via federated analytics. This is a D2C monetization path for Submantle Insights that doesn't require B2B sales.
- **Maturity risk:** This product requires significant UI/UX investment to make software usage data interesting to non-technical users. The market is largely untested. "Your software profile" is interesting to power users and developers; it may not be interesting to mass-market users.

---

## Gaps and Unknowns

### 1. The Re-identification Risk Is Real and Growing — "Truly Safe" Anonymization May Be Impossible

This is the most important gap. Recent research establishes that "99.98% of Americans would be correctly re-identified in any dataset using 15 demographic attributes." A dataset "properly anonymized in 2015 might become re-identifiable in 2025 as new public datasets emerge, computational methods improve, and auxiliary information becomes available." The EDPB's April 2025 report clarifies that LLMs rarely achieve anonymization standards.

**The practical consequence for Submantle Insights:** If Submantle publishes aggregate reports like "45% of ComfyUI users also run Blender in Seattle," and that report is combined with other data sources (IP ranges, user forums, social media), re-identification of specific individuals or small communities becomes feasible. The smaller the cohort, the higher the risk. Differential privacy with well-chosen epsilon values is the technical mitigation — but it introduces noise that may make small-cohort statistics unreliable or meaningless.

**Evidence:** ScienceDaily re-identification study coverage (July 2019, foundational); Nature Scientific Reports methodology for re-identification risk assessment (2025); EDPB April 2025 report on LLM anonymization; Access Now, "Differential Privacy Part 3" (2019)

**What would validate this:** Submantle would need a formal re-identification risk assessment for any proposed reporting format before launch, using the methodology from Nature Scientific Reports (2025). Until that assessment exists, the safety of any specific report format is unknown.

---

### 2. The Specific Buyers for "Desktop Software Co-Occurrence Data" Are Unvalidated

The hypothesis — "product companies, investors, and hardware manufacturers would buy this" — has strong structural logic but **no validated customer interviews or stated willingness-to-pay**. The technographic data market ($1.17B) proves demand for technology intelligence, but that market is almost entirely about *website* technology stacks, used by B2B sales teams for lead generation.

Desktop software co-occurrence is a different product for a different buyer. It needs customer development before revenue projections can be built. Questions that need answering through actual conversations with target buyers:
- Would a product company (e.g., Adobe, Autodesk) pay for "what other software our users run simultaneously"?
- Would a hedge fund pay for "software adoption curves across the install base"?
- At what price point and reporting cadence?

---

### 3. The Consent Architecture for Data Contribution Is Undefined

For Submantle Insights to work, users must consent to their device contributing to aggregate intelligence. The consent language, opt-in vs. opt-out structure, and what users are told about how their data contributes to commercial products is undesigned. This matters because:
- GDPR requires explicit, specific, informed consent for data processing. "Agree to terms of service" is not sufficient.
- CCPA requires the ability to opt out of "selling" personal information — even aggregated, the California AG has argued that contributing to a panel constitutes a "sale."
- The 2026 CCPA regulations introduce new risk assessment requirements and data broker registration rules.

Until a consent architecture is designed and reviewed by counsel, the Insights product cannot legally launch in the EU or California.

---

### 4. The "Privacy-First Brand vs. Data Business" Tension Is Real, Not Theoretical

Team 6 identified this: "Privacy-first creates a paradox for the data insights revenue model." They concluded it was "ruled out." This research disagrees — but only conditionally. The tension is real if the data business is structured as "we collect your data and sell it." The tension dissolves if:
- The product uses federated analytics (data never leaves the device)
- Contributions are opt-in, not opt-out
- Users have a clear, revocable consent mechanism
- The outputs are differentially private statistics, not behavioral profiles

The framing matters enormously for user trust. "Submantle uses your device's anonymous contribution to generate aggregate industry reports" is very different from "Submantle sells your data." The federated analytics architecture is the mechanism that makes the former true and the latter false.

**This gap requires a design decision:** Does Submantle build federated analytics infrastructure (significant engineering, cleaner privacy story) or centralized aggregation with DP post-processing (simpler engineering, weaker but still defensible privacy story)?

---

### 5. Regulatory Landscape for Aggregated Data Is Actively Shifting

The September 2025 CJEU ruling (C-413/23 P) is favorable: pseudonymized/differentially private data may not be "personal data" for the recipient if they cannot re-identify individuals. But:
- This ruling was issued in September 2025 — it is new precedent and has not yet been tested in the context of commercial data products
- The 2026 CCPA regulations (effective January 1, 2026) introduce new data broker registration requirements — Submantle Insights may trigger data broker status in California
- New state AI liability laws are expanding across the US in 2026
- The EU AI Act's August 2026 deadline is live — classification review is urgent

**What's unknown:** Whether Submantle Insights triggers California data broker registration. Whether the CJEU ruling applies when the pseudonymization is done by the data controller (Submantle) rather than a third-party processor. Whether the EU AI Act affects data-product outputs, not just model operations.

---

## Synthesis

### What the Landscape Tells Us

Submantle Insights is a genuinely novel product in a proven market category. The adjacent markets validate demand:
- Technographics: $1.17B market, 26.1% CAGR, strong B2B demand
- Alternative data: $14-18B market, 50%+ CAGR, hedge funds paying $1.6M/year average
- Aggregated intelligence subscriptions: Similarweb at $282M ARR, NIQ at $2.9B ARR

The specific data asset — desktop software co-occurrence, process-level awareness at scale — does not exist in any current commercial product. Submantle would own this category. "45% of ComfyUI users also run Blender" is not available anywhere. That is a genuine moat.

### The Strongest Approach: Federated Analytics + Opt-In Panel + B2B Intelligence Subscription

The cleanest path through the legal and brand complexity:

1. **Architecture:** Federated analytics (Google Parfait model) — queries run on-device, only differentially private aggregate answers are transmitted. Raw data never leaves the device. This is not "collecting data"; it is "answering questions."

2. **Consent:** Explicit opt-in for panel participation, separate from Submantle's core functionality. Users who opt in become "Submantle Insights contributors" — clearly disclosed, easily revocable. Model language: "Help us generate industry reports about software usage patterns. Your device answers aggregate questions. Your individual data never leaves your device."

3. **Product:** "Submantle Insights" reports sold as B2B subscriptions to:
   - Software product companies (competitive intelligence: "what do our users' software ecosystems look like?")
   - Hardware manufacturers (GPU driver priority, hardware bundle strategy: "what software stacks run on NVIDIA RTX 4090s?")
   - Financial intelligence firms / hedge funds (software adoption curves as alternative data: "ComfyUI install rate growth Q1 2026 vs Q4 2025")
   - AI companies (training data licensing for world-model calibration)

4. **Pricing:** Technographic data benchmarks suggest $295-$995/month for self-serve; enterprise custom (likely $25K-$200K/year for bespoke intelligence API access). This is consistent with Similarweb's $100K+ ARR account tier.

### What the Orchestrator Needs to Know

**The go/no-go on Submantle Insights is "conditional go" with one critical prerequisite:** The product must be built on federated analytics architecture, not centralized data collection. Without that architectural decision made upfront:
- The privacy-first brand is compromised
- The GDPR legal position is weaker
- The regulatory exposure in California is higher
- The user trust story is messier

The federated analytics architecture is significantly more complex to build than centralized aggregation. It requires a deliberate engineering investment. But it is the only version of this product that is consistent with Submantle's "privacy by architecture" principle and that resolves the tension Team 6 identified.

**The market is real. The data asset is novel. The legal path exists. The engineering investment is the gate.**

**The single most important question Guiding Light must answer:** Is Submantle willing to invest in federated analytics infrastructure to build Insights the right way — or should Insights be deferred until the core daemon business has resources for it? Launching Insights with centralized aggregation + post-hoc DP is faster, but it puts Submantle in the same category as every other data company. Launching with federated analytics makes it genuinely different — and genuinely defensible.

---

## Sources
- [Similarweb Q4 FY2025 Results — StockTitan](https://www.stocktitan.net/news/SMWB/similarweb-announces-fourth-quarter-and-fiscal-2025-2xb2nmaex19p.html) (February 2026)
- [Similarweb FY2025 Results — BusinessWire](https://www.businesswire.com/news/home/20260217787459/en/Similarweb-Announces-Fourth-Quarter-and-Fiscal-2025-Results) (February 2026)
- [NIQ FY2025 Results — BusinessWire](https://www.businesswire.com/news/home/20260227890281/en/NIQ-Announces-Strong-Fourth-Quarter-and-Full-Year-2025-Results) (February 2026)
- [Comscore Q3 2025 Results — Comscore IR](https://www.comscore.com/Insights/Press-Releases/2025/10/Comscore-Reports-Third-Quarter-2025-Results) (October 2025)
- [Nielsen Big Data + Panel — Sports Media Watch](https://www.sportsmediawatch.com/2025/12/nielsen-big-data-plus-panel-tv-measurement/) (December 2025)
- [Palantir Q4 2025 Earnings — Palantir IR](https://investors.palantir.com/news-details/2026/Palantir-Reports-Q4-2025-U-S--Comm-Revenue-Growth-of-137-YY-and-Revenue-Growth-of-70-YY-Issues-FY-2026-Revenue-Guidance-of-61-YY-and-U-S--Comm-Revenue-Guidance-of-115-YY-Crushing-Consensus-Expectations/) (February 2026)
- [Alternative Data Market Size — Precedence Research](https://www.precedenceresearch.com/alternative-data-market) (2025)
- [Alternative Data Industry Growth — Integrity Research](https://www.integrity-research.com/the-explosive-growth-of-the-alternative-data-industry-trends-drivers-and-revenue-forecasts-through-2028/) (accessed March 2026)
- [Hedge Funds and Alternative Data — HedgeCo](https://www.hedgeco.net/news/10/2025/the-influence-of-ai-alternative-data-and-esg-on-hedge-fund-strategy-in-2025/) (October 2025)
- [Alternative Data Sources for Hedge Funds — ExtractAlpha](https://extractalpha.com/2025/07/07/5-best-alternative-data-sources-for-hedge-funds/) (July 2025)
- [Technology Lookup Software Industry Statistics — TechnologyChecker.io](https://technologychecker.io/blog/technology-lookup-software-industry-statistics-insights) (2025)
- [Apple Differential Privacy Overview — Apple ML Research](https://machinelearning.apple.com/research/learning-with-privacy-at-scale) (accessed March 2026)
- [Apple Differential Privacy PDF — Ars Technica CDN](https://cdn.arstechnica.net/wp-content/uploads/2025/05/Differential_Privacy_Overview.pdf) (2025)
- [What is Differential Privacy? — Privacy Guides](https://www.privacyguides.org/articles/2025/09/30/differential-privacy/) (September 2025)
- [Google Confidential Federated Analytics — Google Research](https://research.google/blog/discovering-new-words-with-confidential-federated-analytics/)
- [Apple PPML 2025 Workshop — Apple ML Research](https://machinelearning.apple.com/updates/ppml-2025) (2025)
- [Federated Learning in 2025 — DEV Community](https://dev.to/lofcz/federated-learning-in-2025-what-you-need-to-know-3k2j) (2025)
- [CJEU Landmark Ruling on Pseudonymized Data — Skadden](https://www.skadden.com/insights/publications/2025/11/in-a-landmark-decision-eu-court-clarifies) (November 2025)
- [GDPR vs CCPA Compliance 2026 — Usercentrics](https://usercentrics.com/knowledge-hub/gdpr-vs-ccpa-compliance/) (2026)
- [CCPA Requirements 2026 — SecurePrivacy](https://secureprivacy.ai/blog/ccpa-requirements-2026-complete-compliance-guide) (2026)
- [Re-identification Risk Methodology — Nature Scientific Reports](https://www.nature.com/articles/s41598-025-04907-3) (2025)
- [BuiltWith Alternatives — Revealera](https://revealera.com/blog/7-builtwith-alternatives-2025) (2025)
- [Privacy-First Analytics Revenue — Userbird](https://userbird.com/blog/google-analytics-alternatives-ordered-by-usage-revenue) (2025)
- [Comscore Privacy Framework — Comscore](https://www.comscore.com/Insights/Blog/Respecting-Privacy-in-Online-Measurement-Comscores-Vision)
- [Data Broker Market — Mordor Intelligence](https://www.mordorintelligence.com/industry-reports/data-broker-market) (2025)
- [Mixpanel vs Amplitude 2025 — GetMonetizely](https://www.getmonetizely.com/articles/mixpanel-vs-amplitude-vs-google-analytics-which-product-analytics-tool-offers-best-value-for-saas-in-2025) (2025)
- [Nielsen 2025 Annual Marketing Report — Nielsen](https://www.nielsen.com/news-center/2025/nielsen-releases-its-2025-annual-marketing-report-looking-at-the-power-of-data-driven-marketing/) (2025)
- [B2B Information Services Market — Market Reports World](https://www.marketreportsworld.com/market-reports/b2b-information-services-market-14723674) (2025)
