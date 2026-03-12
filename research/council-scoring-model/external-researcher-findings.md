# External Researcher Findings: Scoring Model Council
## Date: 2026-03-12
## Researcher Role: External (ecosystem, industry, precedent)

---

## Framing Note

The core question is: what actually changes a trust score, and where is the enforcement boundary for neutral infrastructure? I researched four angles. Findings are direct and opinionated where the evidence is clear.

---

## Angle 1: Reputation System Precedents

### Credit Bureaus (Experian, Equifax, TransUnion / FICO)

**How they work:**
- Bureaus are pure data aggregators. They receive reports from creditors (banks, card issuers, auto lenders, debt collectors) and store them. They do not observe transactions themselves.
- Data received: payment history, amounts owed, account age, credit mix, new inquiries. **No transaction content.** Only outcomes — paid, missed, late by N days, defaulted.
- Bureaus do NOT share data with each other. Scores differ across bureaus because reporters choose which bureaus to report to.
- FICO scoring is a **pure formula applied to bureau data** — FICO is a separate company that licenses the algorithm. The bureaus store facts; FICO computes scores.
- Key anti-gaming structural feature: **reporters must be credentialed members**. You cannot self-report a clean payment history. Only verified lenders can submit data.

**What maps to Submantle:**
- The separation of "data store" (bureau) from "score formula" (FICO) is already Submantle's architecture. Good.
- The "credentialed reporter" model is directly applicable: incident reporters should be registered entities, not anonymous. This raises the cost of false reports.
- Bureaus record **outcome metadata only** — not the content of the loan conversation, not spending patterns. Maps to Submantle recording query counts and incident type, never interaction content.
- FICO uses five weighted categories (payment history 35%, amounts owed 30%, length of history 15%, credit mix 10%, new credit 10%). This suggests **differentiated query types** may matter more than raw counts — a "high-stakes" query that completes cleanly should weight more than a trivial ping.

**Scores:**
- Relevance: 9/10 — closest structural analog
- Maturity: 10/10 — 50+ years of production
- Community Health: 9/10 — heavily regulated, well-documented
- Integration Effort: 8/10 — concept integration only, no code dependency
- Evidence Quality: 9/10 — public documentation, academic literature

---

### eBay / Amazon Seller Ratings

**How they work:**
- eBay uses Detailed Seller Ratings (DSR): four dimensions rated 1–5 stars after each transaction: item description accuracy, communication quality, shipping time, shipping charges. Overall score is feedback percentage (positive / total).
- The two-sided grading problem is real and documented: **strategic feedback manipulation** is endemic. Sellers retaliate against negative buyers; buyers withhold feedback to extract refunds. eBay's response was to make negative feedback from sellers to buyers nearly impossible — **asymmetric enforcement**.
- eBay's gaming response evolved from pure crowd ratings to **transaction-outcome signals** (disputes opened, return rates, "item not as described" claims) that buyers can't easily fake. These behavioral signals now outweigh stated ratings.
- Amazon moved toward **implicit behavioral signals** (return rate, contact rate, late shipment rate) rather than explicit ratings after discovering explicit ratings were easily gamed.

**What maps to Submantle:**
- The lesson: **explicit ratings decay in value; behavioral outcomes are harder to fake**. For Submantle, this means incident reports from credentialed reporters (behavioral outcomes) are more valuable than self-declared capability claims.
- The asymmetry insight: when Submantle receives an incident report, the reporter should have **skin in the game** — a false report should carry a cost (e.g., Submantle could track reporter accuracy over time).
- eBay's four DSR dimensions suggest that a single "incidents" counter is a simplification worth revisiting — different incident types have different severity.

**Scores:**
- Relevance: 7/10 — two-sided problem is real but Submantle is one-sided (no agent rating brands)
- Maturity: 9/10 — 20+ years of evolved anti-gaming
- Community Health: 8/10
- Integration Effort: 7/10 — concept integration
- Evidence Quality: 8/10 — academic literature solid (Tadelis et al.)

---

### Uber / Lyft / Airbnb

**How they work:**
- Uber uses simultaneous reveal (both parties rate at the same time, neither sees the other's rating until both submit). This was specifically designed to prevent retaliation-driven rating inflation.
- Airbnb uses a 14-day window before reviews are published, and reviews only appear if both sides submit — preventing strategic non-submission.
- Both platforms moved away from raw star averages toward **relative peer comparison** — you're ranked against similar drivers/hosts, not against an absolute scale.
- Gaming response: Uber deactivates below 4.6 (out of 5). This creates **artificial floor enforcement by the platform** — which is explicitly NOT what Submantle should do.

**What maps to Submantle:**
- Simultaneous reveal doesn't apply (Submantle is one-sided: brands rate agents, not vice versa).
- The time-window + mutual reveal pattern suggests: **incident reports should have a confirmation window** before they affect the score — preventing drive-by malicious reports.
- The relative comparison insight is interesting but contradicts Submantle's deterministic constraint. Skip.
- Key negative lesson: platform deactivation (Uber's 4.6 floor) is exactly what Submantle must NOT do. Submantle exposes the score; brands set their own floors.

**Scores:**
- Relevance: 6/10 — consumer marketplace, different threat model
- Maturity: 8/10
- Community Health: 7/10
- Integration Effort: 6/10
- Evidence Quality: 7/10

---

### App Stores (Google Play, Apple)

**How they work:**
- Developer reputation is binary at the infrastructure level: you're in or you're out. No gradient trust score.
- App stores use **pre-publication review** (Apple) or **post-publication behavioral monitoring** (Google Play Protect). Google's approach is closer to Submantle's model: observe runtime behavior, flag anomalies.
- Developer accounts can be terminated; apps can be removed. The MATCH-equivalent is the developer account ban.

**What maps to Submantle:**
- The binary in/out model is what Submantle should NOT replicate — a gradient score is the whole point.
- Google Play's runtime behavioral monitoring (scanning installed apps for malicious behavior) is structurally analogous to Submantle's OS-level observation, but Submantle doesn't detect incidents — it records third-party reports of them.

**Scores:**
- Relevance: 5/10 — binary enforcement model doesn't translate
- Maturity: 9/10
- Community Health: 7/10
- Integration Effort: 4/10
- Evidence Quality: 6/10

---

## Angle 2: The Enforcement Boundary for Neutral Infrastructure

### DNS Registrars / ICANN

**The model:**
- ICANN's Uniform Domain-Name Dispute-Resolution Policy (UDRP) requires **evidence of abuse before any action**. Registrars must not cancel, suspend, or transfer a domain without agreement, court action, or arbitration — with narrow emergency exceptions for documented DNS abuse (malware, phishing).
- ICANN's guidance explicitly states: registrars take "appropriate mitigation action that is reasonably necessary to stop, or otherwise disrupt, the Registered Name from being used for DNS Abuse" — only when evidence is provided.
- The neutral infrastructure principle holds: registrars are common carriers. They act on **external evidence from third parties**, not on their own detection.
- Key: even in clear abuse cases, the process includes a **defined appeal path**.

**Enforcement boundary finding:** Registrars act on third-party evidence with a defined process. They do NOT proactively detect abuse. This is the credit bureau / Submantle model — Submantle records third-party reports; it does not detect incidents.

---

### Certificate Authorities (SSL Revocation)

**The model:**
- CAs can revoke certificates when domain validation fails, when private keys are compromised, or when a subscriber violates the CA/Browser Forum baseline requirements.
- DigiCert revoked 83,000+ certificates in July 2024 for a domain validation procedural error — **mass revocation on technical grounds, not behavioral grounds**.
- Revocation is a **trust infrastructure action, not an enforcement action** — the CA is withdrawing its attestation that it validated the identity, not judging the entity's behavior.
- Important nuance: "takedown-by-revocation" is a risk — revocation can be weaponized as an enforcement mechanism that bypasses due process. This is a structural warning for Submantle.

**Enforcement boundary finding:** CAs revoke their own attestations (withdrawing what they vouched for), not the entity's right to exist. Submantle's analog: Submantle could theoretically issue a "verified" attestation and withdraw it, without blocking the agent from operating. Score drops; attestation lapses. The agent continues to function.

---

### Payment Networks (Visa / Mastercard)

**The model — precise thresholds (publicly documented):**
- Mastercard ECM (Excessive Chargeback Merchant): triggered at 1.5% chargeback ratio OR 100–299 chargebacks/month. Fines begin.
- Mastercard HECM (High Excessive Chargeback Merchant): 3% ratio OR 300+ chargebacks/month. Account termination risk.
- Terminated merchants are added to the **MATCH list** (Member Alert to Control High-Risk Merchants) — a permanent industry blacklist maintained by Mastercard, accessible to all member banks.
- Visa's VAMP (Visa Acquirer Monitoring Program) has similar thresholds with a progressive fine structure before termination.
- **Critical structural point:** Visa and Mastercard do not terminate merchants directly. They fine and pressure the **acquiring bank**, which terminates the merchant relationship. The network is two layers removed from the merchant.

**What maps to Submantle:**
- The MATCH list is the closest analog to a "suspended" agent status — not deletion, but a permanent record that other parties can query. Submantle's incident report table is already this.
- The "two layers removed" model is exactly right for Submantle: Submantle records the score, brands decide what to do with it. Submantle never directly terminates anything.
- Visa/Mastercard's threshold-based monitoring program (watch list → fines → termination) suggests Submantle could offer **threshold alerts to brands** (e.g., "this agent's score dropped below 0.3") without Submantle itself enforcing anything.

**Enforcement boundary finding:** Payment networks are NOT neutral in practice — they fine and terminate. But their architecture is: (1) objective thresholds, (2) progressive escalation, (3) enforcement delegated to the bank layer. Submantle should stay at the "objective threshold + score" layer and leave enforcement to the brand layer.

---

### Credit Bureaus — Can They Remove Someone?

**The model:**
- Bureaus CANNOT remove accurate negative information before its legal retention period (7 years for most negative items; 10 years for bankruptcy).
- They CAN remove inaccurate information through a dispute process. The Fair Credit Reporting Act (FCRA) requires bureaus to investigate disputes within 30 days and remove data that cannot be verified by the original reporter.
- The "right to be forgotten" (EU GDPR) applies differently — in the EU, inaccurate or outdated data must be deleted. In the US, accurate data stays.

**What maps to Submantle:**
- Submantle should NOT allow agents to delete accurate incident reports. The bureau model holds.
- Submantle SHOULD allow dispute of inaccurate reports — with the burden of verification on the original reporter. If the reporter cannot verify, the incident is removed.
- This is a direct answer to the enforcement boundary question: **Submantle removes inaccurate data on dispute; it never removes accurate negative history**.

---

## Angle 3: Agent Trust Frameworks (March 2026)

### IETF RATS RFC 9334 — Passport Model

**What it is:**
- RFC 9334 defines a remote attestation architecture with three roles: Attester (the device/agent claiming properties), Verifier (evaluates evidence against appraisal policy), Relying Party (uses the attestation result to make decisions).
- The Passport Model: Attester produces Evidence → Verifier evaluates → issues Attestation Result → Attester presents to Relying Party. The Relying Party never sees the raw Evidence, only the Verifier's signed result.
- This maps **exactly** to Submantle: daemon (Attester) → Submantle attestation server (Verifier) → brand API consumer (Relying Party).

**What maps to Submantle:**
- The Passport Model is the correct architectural frame for Submantle's W3C VC attestation path (future work).
- The key insight: the Relying Party gets a signed result from the Verifier, not raw behavioral data. This preserves privacy — brands see the score, not the interaction history.
- RFC 9334 defines "Evidence" types that are relevant: claims about software version, runtime behavior, configuration state. These correspond to what Submantle records (capabilities declared, queries made, incidents reported).

**Scores:**
- Relevance: 9/10 — direct architectural match
- Maturity: 9/10 — published RFC, IETF standard
- Community Health: 8/10 — active RATS working group
- Integration Effort: 7/10 — Go library support exists (noted in CLAUDE.md)
- Evidence Quality: 10/10 — IETF standard

---

### NIST AI RMF 1.0

**What it is:**
- Four functions: GOVERN (policy, accountability), MAP (context, risk identification), MEASURE (analysis, assessment), MANAGE (response, monitoring).
- Voluntary, non-sector-specific framework. Not a scoring standard — it's an organizational process framework.
- 2026 status: NIST expanding with generative AI profiles and playbooks. No agent-specific scoring standard yet published.

**What maps to Submantle:**
- NIST RMF is useful for Submantle's **sales narrative** with enterprise customers, not for the scoring model itself.
- The MEASURE function's emphasis on "analysis of AI risks" without prescribing the method is an opening: Submantle's Beta Reputation formula could be positioned as a MEASURE-compliant deterministic risk assessment tool.
- Critically: NIST RMF does NOT prescribe how to score agents. It describes what organizations should do. Submantle fills the "how" gap.

**Scores:**
- Relevance: 6/10 — framework for organizations, not a scoring protocol
- Maturity: 9/10
- Community Health: 8/10
- Integration Effort: 3/10 — conceptual positioning only
- Evidence Quality: 8/10

---

### Mastercard Verifiable Intent (March 5, 2026)

**What it is:**
- Open-source cryptographic framework (co-developed with Google, supported by Fiserv). Published at verifiableintent.dev.
- Creates a **tamper-resistant proof of consumer authorization** for AI agent transactions: links consumer identity + specific instructions + transaction outcome into a single signed record.
- Uses **Selective Disclosure**: each party sees only the minimum necessary information. The merchant sees "authorization confirmed" without seeing the user's full instruction set.
- Architecture: cryptographic audit trail that all parties can consult if a dispute arises. Dispute resolution without full data exposure.

**What maps to Submantle:**
- Selective Disclosure is directly relevant to Submantle's privacy architecture. When a brand queries an agent's trust score, it should receive the score + confidence interval, not the full incident report list. The incident details stay in Submantle's private audit trail.
- The "tamper-resistant audit trail" concept maps to Submantle's append-only incident_reports table. The table IS the audit trail.
- Verifiable Intent is about authorizing agent actions on behalf of users. Submantle is about scoring agents based on past behavior. They are complementary: Verifiable Intent answers "was this action authorized?", Submantle answers "has this agent behaved well historically?"
- **Important gap these solve together:** A brand could require both: a Verifiable Intent proof (this specific action was authorized) AND a Submantle score above 0.7 (this agent has a clean behavioral history). Two different trust questions.

**Scores:**
- Relevance: 8/10 — architectural complement, not competitor
- Maturity: 6/10 — released March 2026, early adoption
- Community Health: 8/10 — Mastercard + Google + Fiserv backing
- Integration Effort: 6/10 — open standard, Go-compatible
- Evidence Quality: 8/10 — primary source available at verifiableintent.dev

---

### Signet (agentsignet.com)

**What it is:**
- Composite trust score 0–1000 from five weighted dimensions: Reliability 30%, Quality 25%, Financial 20%, Security 15%, Stability 10%.
- Persistent cross-platform "Signet ID" (SID-0x + 16 hex chars). Identity verification via callback challenge-response (URL ownership proof).
- Score responds to model swaps: LLM change triggers 25% decay toward the operator's baseline score. Score rebuilds as the new config is proven.
- API response under 50ms. Currently free, no paid tiers.
- "Verified" badge at identity level 1+; "Clear" recommendation at score 700+.

**What Submantle should know about Signet:**
- Signet's five dimensions vs. Submantle's single Beta formula: Signet has more dimensions but each is subjectively assessed. Submantle's Beta formula is simpler but fully deterministic. These are different bets.
- Signet's "Financial" dimension (20%) is interesting — it suggests interaction value/stakes affect trust, not just incident count. High-stakes successful transactions should count more than trivial pings. This is a gap in Submantle's current `total_queries` (all queries equal).
- Signet's LLM-swap decay rule is a sophisticated anti-gaming measure: you can't reset your score by switching models. Submantle should consider: what happens when an agent updates its version? Currently nothing — the score is per `agent_name`, not per version. This is a gap.
- Signet is enforcement-light but not neutral — the "Clear" recommendation is a form of soft gatekeeping. Submantle is more neutral (no recommendation, just score).
- **Key differentiator**: Signet appears to rely on self-reported or API-observable data. Submantle's OS-level observation is structurally deeper and harder to game.

**Scores:**
- Relevance: 10/10 — direct competitor, closest product
- Maturity: 6/10 — appears early-stage in 2026
- Community Health: 6/10 — limited public information
- Integration Effort: N/A — competitor analysis
- Evidence Quality: 7/10 — public website, some inferred

---

### Google UCP (Universal Control Plane)

Not separately researched in this pass — the CLAUDE.md notes state Google's UCP "explicitly states it does not solve which agents should be trusted." This is confirmed by the competitive landscape analysis: UCP is an orchestration layer, not a trust scoring layer. Gap remains open for Submantle.

---

## Angle 4: Privacy-Preserving Scoring

### What Metadata Is Sufficient for Trust Scoring?

**Finding from credit bureau model:**
Credit bureaus score on **outcome metadata only**:
- Did the payment happen? (binary)
- When? (timestamp)
- How much? (amount)
- Who was the counterparty? (creditor identifier)

They do NOT score on: what was purchased, what was said in the loan application, why the payment was missed.

**Mapping to Submantle's interaction model:**
Sufficient metadata for trust scoring (privacy-safe):
- Query count (already tracked: `total_queries`)
- Query timestamp (already tracked: `last_seen`)
- Query category / capability invoked (NOT currently tracked — gap)
- Incident type (already tracked: `incident_type`)
- Incident reporter identity (already tracked: `reporter`)
- Incident timestamp (already tracked: `timestamp`)

**NOT needed and must NOT be tracked:**
- Content of queries
- Content of agent responses
- Data accessed during a query
- User identity behind a query

---

### Zero-Knowledge Approaches to Reputation

**What exists (March 2026):**
- ZK-based reputation systems are an active research area (ACM Computing Surveys survey published, PRepChain for supply chains published Feb 2026).
- ZKP systems can prove "my score is above threshold X" without revealing the actual score. This is relevant for Submantle's attestation layer (future W3C VC work).
- Current ZKP approaches require either ML components or blockchain substrates — both are excluded by Submantle's constraints.
- Non-interactive ZKPs (NIZKs) with Fiat-Shamir heuristic produce deterministic proofs — compatible with Submantle's "no ML" constraint in principle.

**Practical finding for Submantle now:**
ZKP is future-state (Go production rewrite + W3C VC attestation layer). For the Python prototype, the privacy model is simpler and already correct:
- Interaction content never enters the system
- The Beta score is computed on-device
- The API exposes the score, not the underlying data
- Brands query `/api/verify/{agent_name}` — they get the score, not the incident list

The current architecture IS privacy-preserving by construction. ZKP adds an additional "prove threshold without revealing score" capability — useful when brands want to check "is this agent's score above 0.7?" without Submantle exposing the raw number. Not needed for V1.

**Scores:**
- Relevance: 7/10 — important for V2 attestation layer
- Maturity: 6/10 — production ZKP exists but complex
- Community Health: 7/10
- Integration Effort: 3/10 — high implementation complexity for V1
- Evidence Quality: 7/10 — academic primary sources available

---

## Synthesis: Key Recommendations for the Council

These are findings, not decisions. The council synthesizes.

### 1. What counts as a "query"?
The credit bureau model and Signet's financial dimension both suggest **not all interactions are equal**. A query that invokes a high-stakes capability (e.g., `device_list`, `process_query`) should be distinguished from a health-check ping. The current `total_queries` counter treats them identically. Consider: the `capabilities` field already exists on the agent record — this is the hook for weighted query types.

### 2. The incident reporting pipeline needs reporter credentialing
eBay's gaming problem and the credit bureau's credentialed-reporter model both point the same direction: **anonymous incident reports are gameable**. Reporters should be registered entities with their own accountability record. A false report from a credentialed reporter should reflect back on the reporter.

### 3. The enforcement boundary answer is clear
DNS registrars, CAs, payment networks, and credit bureaus all converge on the same model:
- Collect third-party reports (Submantle already does this)
- Apply objective thresholds/formulas to compute a signal (Beta formula, done)
- Expose the signal; let downstream parties enforce (brands set their own thresholds)
- Do NOT detect or block directly
- DO allow dispute of inaccurate data (not yet built)

**Submantle should never unregister an agent for bad behavior.** Deregistration is an enforcement action. Only the agent itself (via valid token) should be able to deregister. An agent with a score of 0.05 still exists in Submantle — it just has an extremely low score that brands can act on. This preserves neutrality. If Submantle deletes bad actors, it becomes the judge, not the bureau.

### 4. The version/model-swap gap
Signet's LLM-swap decay rule highlights a real problem: an agent could accumulate a bad score, rename itself (new `agent_name`), and start fresh. Submantle's current model has no answer to this. The `author` field is the partial answer — same author, different name. The council should address this.

### 5. Mastercard Verifiable Intent is complementary, not competitive
Verifiable Intent answers "was this specific action authorized by the user?" Submantle answers "does this agent have a history of good behavior?" Enterprise customers will eventually want both. Submantle's score + Verifiable Intent's authorization proof = the complete trust picture for agentic commerce.

### 6. The dispute mechanism is missing and legally necessary
Credit bureau law (FCRA in the US, GDPR in the EU) requires a dispute process. Even as a neutral infrastructure provider, Submantle will face demands to correct inaccurate incident reports. The architecture supports it (incident_reports table, reporter field), but there is no dispute endpoint. This is a gap that grows more important as Submantle scales.

---

## Source Citations

- [FICO Score Versions — myFICO](https://www.myfico.com/credit-education/credit-scores/fico-score-versions)
- [Equifax vs TransUnion vs Experian 2026](https://www.unitedcreditservices.com/blog/equifax-vs-transunion-vs-experian/)
- [eBay Seller Ratings System 2026 — eDesk](https://www.edesk.com/blog/ebay-star-ratings/)
- [Reputation and Feedback Systems in Online Platform Markets — Tadelis (Annual Review)](https://faculty.haas.berkeley.edu/stadelis/Annual_Review_Tadelis.pdf)
- [Mastercard Chargeback Threshold — Chargebacks911](https://chargebacks911.com/mastercard-chargeback-threshold/)
- [Visa/Mastercard Risk Program Thresholds — Moneris](https://www.moneris.com/-/media/Files/Downloadable_Guides/Visa-and-Mastercard-Fraud-and-Chargeback-Program-Thresholds.ashx)
- [ICANN Uniform Domain-Name Dispute-Resolution Policy](https://www.icann.org/resources/pages/help/dndr/udrp-en)
- [Notice and Takedown in the DNS — WLU Law Review](https://scholarlycommons.law.wlu.edu/cgi/viewcontent.cgi?article=4565&context=wlulr)
- [RFC 9334 — IETF RATS Architecture](https://datatracker.ietf.org/doc/html/rfc9334)
- [NIST AI Risk Management Framework 1.0](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10)
- [Mastercard Verifiable Intent — PYMNTS](https://www.pymnts.com/mastercard/2026/mastercard-unveils-open-standard-to-verify-ai-agent-transactions/)
- [How Verifiable Intent Builds Trust in Agentic AI Commerce — Mastercard](https://www.mastercard.com/global/en/news-and-trends/stories/2026/verifiable-intent.html)
- [Mastercard and Google Launch Verifiable Intent — The Paypers](https://thepaypers.com/payments/news/mastercard-introduces-verifiable-intent-co-developed-with-google)
- [Signet — Identity and Trust for the Agent Economy](https://agentsignet.com/)
- [Privacy-Preserving Reputation Systems — ACM Computing Surveys](https://dl.acm.org/doi/10.1145/3490236)
- [Zero-Knowledge Proofs for Privacy-Preserving Context Validation — Security Boulevard](https://securityboulevard.com/2026/03/zero-knowledge-proofs-for-privacy-preserving-context-validation/)
