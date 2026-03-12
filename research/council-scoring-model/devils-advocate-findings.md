# Devil's Advocate Findings — Scoring Model Stress Test
## Date: 2026-03-12
## Analyst Role: Devil's Advocate (Research Council)
## Project: Submantle

---

## Preface

I read the full research brief, agent_registry.py (compute_trust, record_query, record_incident), database.py (schema), and the api.py incident reporting endpoint. My job is to find every way this fails. Here is my honest assessment.

---

## 1. Assumption Audit

### "All interactions should count equally toward trust"
**Status: UNVERIFIED — and likely wrong in practice.**

The current formula counts every `record_query()` identically. A health-check ping and a "read all user files" operation both increment `total_queries` by 1. This means an agent could run 10,000 low-stakes status pings and build a 0.99 trust score before ever performing a sensitive operation. The score would be numerically high but informationally empty about what actually matters to businesses.

The assumption hasn't been tested against a real customer. No paying business has told you "yes, total query count is the signal I want." This is a founding assumption with zero empirical support.

**Severity:** High. The entire trust signal could be noise.

---

### "Third-party incident reports are trustworthy"
**Status: CONTRADICTED by the current implementation.**

`POST /api/incidents/report` requires zero authentication. The `reporter` field is a free-text string — anyone can claim to be anyone. A competitor can file an incident against `rival-agent` with `reporter: "Amazon"` and there is no mechanism to verify Amazon actually filed it. The credit bureau analogy breaks immediately here: Equifax only accepts reports from credentialed, contracted data furnishers. Banks cannot anonymously submit missed payments. Submantle currently accepts anonymous incident reports from the open internet.

**This is the single most exploitable vulnerability in the current system.** It is not a future concern. It is live today.

---

### "The Beta formula is sufficient for V1"
**Status: VERIFIED as mathematically sound, UNVERIFIED as business-sufficient.**

Beta(α=q+1, β=i+1) with a uniform prior is a legitimate, well-understood Bayesian estimator. The math is correct. The problem is not the formula — it is what the formula is computing. If queries means "API calls made" rather than "meaningful trustworthy interactions verified by a counterparty," the formula is computing something that looks like trust but isn't. The formula is a sound instrument pointed at an imprecise target. For a V1 proof of concept, it is sufficient. For a paid product, the question is whether customers trust the inputs, not the formula.

---

### "Privacy can be preserved while scoring interactions meaningfully"
**Status: UNVERIFIED — there is a fundamental tension here.**

On-device computation preserves privacy of interaction content. But meaningful scoring requires knowing WHAT the agent did, not just THAT it made a query. To differentiate between "browsed a webpage" and "accessed a financial account," you need either (a) the content of the interaction — which violates privacy by architecture — or (b) the agent to self-report its action type — which the agent can lie about. There is no architecture currently proposed that solves this tension. The current workaround is counting queries without content, which preserves privacy but produces shallow scores.

---

### "A single universal trust score is better than category-specific scores"
**Status: VERIFIED as correct for V1.**

Every successful reputation system started with one number. eBay started with +1/-1. Uber started with 1-5 stars overall. Credit bureaus started with a single FICO score. Complexity was added only after product-market fit. Launching with multiple category scores would require (a) defining categories that map to real business needs without ML, (b) collecting enough data per category to make each score meaningful, and (c) explaining a vector of numbers to customers who want a single answer to "should I trust this agent." The complexity cost for a solo founder is prohibitive at this stage. One score is correct.

**The risk runs the other way:** a single score that proves meaningless to the first real customer is worse than no score. The single score needs to mean something specific — and right now it doesn't clearly.

---

### "Neutral infrastructure should never enforce (never unregister agents)"
**Status: UNVERIFIED as an absolute position — and dangerous if held rigidly.**

The analogy to Visa breaks down at an important boundary. Visa does have enforcement: they can terminate merchant accounts for fraud. DNS registrars revoke domains used for phishing. Certificate Authorities revoke certificates for malicious actors. IANA does not let anyone register arbitrary IP blocks for botnet C2. Every "neutral infrastructure" example that has survived at scale has a floor of abuse-response enforcement, even if the day-to-day operation is neutral.

The question is not "never enforce vs. always enforce" but "what is the minimum enforcement necessary to maintain infrastructure integrity." Refusing to ever unregister an agent whose entire purpose is to file false incident reports against competitors is a position that will eventually produce a PR crisis. The current stance — no enforcement whatsoever — is legally and reputationally fragile, not just philosophically pure.

---

### "Businesses will pay for trust scores"
**Status: UNVERIFIED — the most important unverified assumption.**

No business has paid yet. No business has been asked specifically "would you pay $X/month for this score." The competitive intelligence is compelling but it is not customer discovery. The argument that trust infrastructure is valuable because competitors are raising money is true but indirect. Businesses pay for scores when:
1. The score predicts something they care about (reduced fraud, reduced liability, regulatory compliance)
2. The score is different from what they could compute themselves
3. The cost of using the score is less than the cost of not using it

None of these three conditions have been verified through customer conversations. This is fine for a prototype — it is not fine for the "build priority" table to treat "Demo / landing page" as step 8 when it should be step 2.

---

### "The credit bureau model works for AI agents"
**Status: UNVERIFIED — and the analogy has a critical flaw.**

Credit bureaus work because:
1. **Data furnishers are credentialed and contractually liable for accuracy** — banks are legally bound by the FCRA to report accurately or face penalties
2. **The subject of the report has legal rights** — consumers can dispute inaccurate records
3. **The bureau is legally regulated** — FCRA, GDPR, etc.

In Submantle's current implementation: reporters are anonymous, agents have no dispute mechanism, and Submantle operates in no regulatory framework (yet). The surface analogy — "third parties report, we store" — is correct. The supporting mechanisms that make the model trustworthy in credit are entirely absent. This is not a reason to abandon the model. It is a reason to understand that the model requires those mechanisms to work at scale, and to plan for them.

---

## 2. Gaming Vectors

### Score Inflation — Self-Querying
**Severity: CRITICAL. Effort: Trivial.**

An agent can call `GET /api/processes` (or any authenticated endpoint) in an infinite loop, incrementing its own `total_queries` counter. At 10,000 automated queries, trust score approaches 1.0. The API has no rate limiting, no velocity cap, no query diversity requirement. The code in `record_query()` calls `verify()` then `increment_agent_queries()` — there is no check on whether the query serves any purpose beyond inflating the score.

Fix path: velocity caps (max N queries per hour counting toward trust), query diversity requirements (repeated identical queries count once), or interaction verification (a counterparty must confirm the interaction happened).

---

### Score Inflation — Friendly Business Collusion
**Severity: HIGH. Effort: Low.**

A business registers as a "reporter" and submits zero incidents for its own agents, while filing incidents against competitors. Meanwhile, it also creates a secondary account that queries its own agents repeatedly. No authentication required on incident reports means collusion rings are trivially easy to construct. eBay had this problem in 2000 with "feedback rings" — sellers mutually trading positive feedback.

eBay's solution: removed the ability for buyers to receive negative feedback from sellers, created asymmetric reporting. The lesson is that symmetric, unauthenticated reporting is always gamed.

---

### Score Deflation — False Incident Reports Against Competitors
**Severity: CRITICAL. Effort: Trivial. Current protection: None.**

`POST /api/incidents/report` requires: `agent_name`, `reporter`, `incident_type`, `description`. All free text. No authentication. No rate limiting. I can file 1,000 incident reports against `claude-assistant` from `reporter: "Amazon"` right now, from a script, in under 60 seconds. Trust score goes from 0.5 to near 0.0.

This is not a theoretical risk. It is a live, working attack vector in the current prototype. Any competitor, troll, or script kiddie can destroy any agent's reputation with zero friction.

**This must be fixed before any public demo.** Showing the system to a potential customer while this endpoint is unauthenticated is a demonstration of how to destroy the product, not how to use it.

---

### Sybil Attacks — Multiple Agent Registrations
**Severity: MEDIUM. Effort: Low.**

Agent names must be unique, but there is no constraint on who can register agents. A bad actor registers `claude-assistant-v1`, `claude-assistant-v2`, `claude-assistant-official` — none of which are the real Claude assistant. They build up scores on these spoofed names, then use the confusion to mislead businesses doing `GET /api/verify/claude-assistant`. There is no agent identity verification at registration — only name uniqueness. The real Anthropic cannot protect its agent's name in the current system.

---

### Incident Report Spam — No Auth on POST /api/incidents/report
**Severity: CRITICAL. Already documented above.**

Confirmed by code review: the endpoint has no `Authorization` header check, no rate limiting, no CAPTCHA, no API key. The `reporter` field is unverified text. This is the most urgent vulnerability in the codebase.

---

### How Credit Bureaus Prevent This
Credit bureaus (Experian, Equifax, TransUnion) require data furnishers to:
1. Sign a data furnisher agreement with legal liability clauses
2. Use authenticated, credentialed data submission channels (not open HTTP endpoints)
3. Follow FCRA dispute resolution procedures
4. Face regulatory penalties for willful inaccuracies

**How eBay prevents feedback gaming:**
1. Mutual feedback suppression (you can't see what the other party wrote until both submit)
2. Asymmetric rules (sellers can't leave negative feedback for buyers)
3. Transaction linkage (feedback only valid for completed transactions)
4. Velocity limits (X feedbacks per period per relationship)

Submantle has none of these controls. The model name is borrowed but none of the protective mechanisms are implemented.

---

## 3. The Enforcement Trap

Guiding Light asked: "Do we have the ability to unregister agents from the network immediately to stop them causing harm?"

**The honest answer is: yes, technically — deregister() exists. The policy question is whether you should ever use it proactively.**

### What Neutral Infrastructure Actually Chose:

**DNS:** ICANN and registrars DO revoke domains. The Uniform Domain-Name Dispute-Resolution Policy (UDRP) allows forced transfers for trademark violations. Registrars terminate accounts for SPAM and phishing. DNS is "neutral infrastructure" that absolutely enforces at the margin.

**Certificate Authorities:** CAs revoke certificates for key compromise, mis-issuance, and abuse. The CA/Browser Forum requires revocation within 24 hours for certain violations. This is active enforcement by neutral infrastructure.

**Visa/Mastercard:** Both terminate merchant accounts. Both maintain MATCH (Member Alert to Control High-Risk Merchants) lists that effectively blacklist merchants across the network. Visa is neutral infrastructure with an enforcement floor.

**The pattern:** Every durable neutral infrastructure maintains a minimal enforcement capability that is:
- Triggered by third-party reports (not proactive surveillance)
- Procedurally bounded (not arbitrary)
- Transparent (the terminated party knows why)
- Appeal-able (there is a dispute mechanism)

### The Middle Ground

Submantle does not need to be an enforcement gatekeeper to handle existential abuse cases. The model is:
1. **Score, never gate** — trust score updates remain the primary mechanism
2. **Quarantine, don't delete** — flag an agent as "under review" rather than unregistering; the score speaks for itself
3. **Maintain a dispute channel** — agents can contest incident reports
4. **Reserve emergency termination** for provable identity fraud only (e.g., someone registered "claude-anthropic" impersonating Anthropic's actual agent)

The risk of the current absolutist "never enforce" position is that it guarantees Submantle will eventually be weaponized in a way that makes headlines. The risk of adding enforcement is regulatory capture and loss of neutrality. The middle ground is procedurally bounded, abuse-only, last-resort action — which is what every surviving neutral infrastructure actually does.

---

## 4. The "What Metrics Matter" Trap

### Does Adding Category-Specific Scores Create Unsustainable Complexity?

**Yes. Emphatically yes.**

Each category score requires:
- A definition of what actions belong to it
- Sufficient volume of that interaction type to produce a meaningful score
- Explanation to customers ("your data access score is 0.7 but your communication score is 0.9 — what does this mean for me?")
- Separate anti-gaming rules per category
- A display layer that doesn't confuse

For a solo founder, this is not a roadmap item. It is a moat-builder for the competition to fill while you're building six dashboards.

### Did Any Reputation System Start With Multiple Score Types?

No successful one. FICO started as one number. eBay started as +1/-1. Airbnb started as "star rating." Uber started as one rating out of 5. All complexity came after market validation.

The one failure mode that proves the opposite: **Klout** launched with a complex multi-dimensional influence score (topics, network type, engagement rate). Users couldn't explain what their score meant. Businesses couldn't map it to purchase intent. Klout raised $40M and shut down in 2018. The complexity was the product's primary failure mode.

**The risk of too simple:** Customers say "this doesn't tell me what I need to know" and churn. This is recoverable — you add dimensions after you understand what's missing.

**The risk of too complex:** Customers can't explain what they're buying. This is not recoverable without a product rebuild.

One score is the right call for V1. The question to resolve now is whether the current "total queries + incidents" formula produces a score that is simple AND meaningful.

---

## 5. Counter-Evidence

### Failed Reputation Systems

**Klout (2008-2018):** Complex multi-dimensional social influence score. Raised $40M, had 200M users at peak, shut down. Failure modes: scores were gameable (automated Twitter activity), businesses couldn't map scores to outcomes, score complexity created user anxiety without business value. Directly analogous to the risk of over-engineering Submantle's scoring.

**Facebook's "Trustworthiness Score" (2018):** Internal score assigned to users to weight news reporting credibility. Never public. Killed within a year after leaks caused PR crisis. Lesson: trust scores on entities become politically untenable when the scoring criteria are opaque, even when deterministic.

**Google's PageRank (as public metric):** Originally published as a 0-10 toolbar score. SEOs reverse-engineered it and gamed it systematically. Google deprecated the public PageRank display in 2016. Lesson: publishing a score that can be gamed creates an adversarial optimization dynamic that degrades the signal over time.

### Cold Start Problems in Trust Systems

The Beta formula initializes at 0.5 ("unknown"). This is mathematically sound but practically problematic:

- **Every new agent starts at "unknown."** Businesses asking "should I trust this agent?" for a brand-new deployment get a shrug. This is the moment trust infrastructure needs to be most useful.
- **Trust accumulates through API calls, not business outcomes.** An agent that calls Submantle 100 times has a trust score of 0.97 — but a business doesn't know if those 100 calls represented $100M in safely processed transactions or 100 health-checks from localhost.
- **The cold start is worse for legitimate agents than malicious ones.** A malicious agent can inflate its score before deploying. A legitimate agent that goes to a business fresh has 0.5. This is backwards.

eBay solved cold start with "new seller" badges and transaction minimums before full selling privileges. Airbnb solved it with manual verification, Facebook login linkage, and "Superhost" designation for early adopters. Credit bureaus solve it with "thin file" handling — a separate category that triggers manual underwriting.

Submantle has no cold start handling. 0.5 for unknown is mathematically defensible but commercially useless.

### Cases Where Credit Bureau Models Were Gamed at Scale

**Synthetic Identity Fraud (US, $6B/year):** Fraudsters build credit files over 2-3 years using combinations of real SSNs with fake names. They make small, consistent payments to establish legitimacy, then "bust out" — taking maximum credit and disappearing. The credit bureau model was gamed by playing the long game on legitimate-looking inputs. Direct analog for Submantle: an agent builds 50,000 query-count over 6 months, establishes a 0.99 trust score, then deploys maliciously.

**eBay Feedback Farms (2000-2008):** Sellers in Eastern Europe built up feedback scores through small transactions, then used high-reputation accounts to run large scams. eBay's fix was a combination of transaction linkage and new seller limits — neither of which exists in Submantle's model.

### Arguments Against Deterministic-Only Scoring

**The gaming argument:** Deterministic formulas are easier to reverse-engineer and optimize against than ML models, precisely because they're transparent. If the formula is published, bad actors can calculate exactly how many queries they need to offset an incident. With ML, the adversary faces a black box. Determinism buys regulatory clarity but pays for it in gaming surface area.

**The stale signal argument:** A trust score based on historical interaction count doesn't decay. An agent that was trustworthy for 2 years and then gets compromised retains its high score until incident reports accumulate — which, under the credit bureau model, requires third parties to notice, attribute, report, and wait for the score to move. A compromised high-reputation agent is more dangerous than a new unknown one.

**The context collapse argument:** One score collapses context that matters. An agent with a 0.8 trust score for data retrieval and 0.2 for financial transactions is represented as 0.5 — identical to an unknown new agent. A business making a high-stakes financial decision gets noise.

*(Note: These are devil's advocate arguments, not recommendations to add ML. The regulatory constraint is real and the no-ML rule is correct. But the tradeoffs should be acknowledged explicitly, not assumed away.)*

---

## Risk Scorecard

| Dimension | Score (1-10, 10=safe/minimal risk) | Notes |
|-----------|-------------------------------------|-------|
| **Failure Probability** | 3 | Unauthenticated incident reporting is a certainty of abuse, not a probability. Current implementation cannot survive a public demo without being trivially destroyed. |
| **Failure Severity** | 4 | Core trust signal can be zeroed for any agent by anonymous report spam. First customer demo could be weaponized live. Recovery requires re-architecting the reporting model. |
| **Assumption Fragility** | 3 | The two load-bearing assumptions — "businesses will pay" and "incident reports are trustworthy" — are both unverified. Neither has customer evidence. The former is a hypothesis; the latter is contradicted by the code. |
| **Rollback Difficulty** | 6 | Formula change is easy (one function). Structural changes — authentication on incident reporting, cold start handling, dispute mechanisms — require schema migrations and API changes but are bounded. Not catastrophic to reverse. |
| **Hidden Complexity** | 5 | The formula is simple. The sociotechnical machinery required to make the formula produce meaningful signals is not. Gaming prevention, reporter credentialing, cold start handling, and dispute resolution are each a product in themselves. These aren't in scope yet but they are load-bearing. |

---

## Priority Findings

Ranked by urgency — what must be addressed before any public demo:

1. **Unauthenticated incident reporting is a live attack vector.** `POST /api/incidents/report` must require authentication before any public exposure. Minimum: require a registered agent token. Better: require a separate "reporter credential" with terms of service acceptance.

2. **Score inflation via self-querying has no protection.** Velocity caps must exist before trust scores are shown to customers or the signal is meaningless on day one.

3. **Cold start handling is missing.** 0.5 for unknown agents doesn't answer the business question. "New, unscored" needs to be a visible state distinct from "average trust."

4. **The Visa analogy overstates neutrality.** Every surviving neutral infrastructure has a procedurally bounded abuse-response mechanism. Documenting a clear, minimal enforcement policy now is less costly than reverse-engineering one after a PR incident.

5. **Customer discovery must precede dashboard work.** "Businesses will pay for trust scores" is the founding assumption of the entire business model and it remains unverified. Dashboard depth (current priority #5) should not outrank one customer conversation that confirms or invalidates the premise.

---

*Filed by: Devil's Advocate, Research Council*
*Date: 2026-03-12*
