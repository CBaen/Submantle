# External Researcher Findings: Weights and Measures — The Scoring Model Evolution
## Date: 2026-03-12
## Council Role: External Researcher
## Assignment: Three research angles on weighted composite scoring

---

## Grounding Statement

This research was conducted against the following constraints (from the Project Fingerprint):
- Beta Reputation formula stays as foundation: `trust = (q+1) / (q+i+2)`
- No ML-based weighting or classification
- Single universal score for V1
- Deterministic only, EU AI Act exempt
- Score consumed by machines and dashboards — full complexity acceptable
- Prior council settled: record interaction types now, weight them in Go rewrite

The three angles below are: (1) FICO/VantageScore/D&B weighted dimension composition, (2) reputation system evolution and score migration patterns, (3) deterministic composite scoring in fintech/insurance/cybersecurity. Each includes scored approaches and source citations verified at access date 2026-03-12.

---

## Angle 1: How FICO, VantageScore, and D&B PAYDEX Compose Weighted Dimensions

### 1.1 FICO Score — Five Weighted Categories, Additive Composition

**What it is:** FICO is the dominant consumer credit score (300–850 range), produced by Fair Isaac Corporation. The score is a weighted sum across five factor categories.

**Exact category weights (universally stable across FICO 8, 9, 10):**
- Payment History: 35%
- Amounts Owed (utilization): 30%
- Length of Credit History: 15%
- New Credit (recent inquiries): 10%
- Credit Mix (account variety): 10%

**Mathematical structure:** The five weights are additive — each factor's sub-score is multiplied by its weight and the results sum to a final numeric score, which is then mapped to the 300–850 range. FICO explicitly states the percentages show relative importance for the *general population*; the actual weighting shifts based on how much data exists per factor for a specific entity.

**Source:** https://www.myfico.com/credit-education/whats-in-your-credit-score (accessed 2026-03-12)

**Thin file treatment — the critical parallel for Submantle:**
FICO's most important behavior for our purposes: when an entity has insufficient history, FICO does not assign a score at all. The entity receives a "no-hit" or "thin file" status, not a score of zero. FICO Score XD is a *separate product* (not a fallback) that uses alternative data (utility bills, telecom payments) to score previously unscorable entities.

FICO's blog explicitly states: "No-hit applicants — the majority who are newly scorable with FICO Score XD — can be a promising segment for lending expansion."

VantageScore 4.0 goes further: a consumer can receive a score with **one month** of credit history, using rent and utility payments as alternative signals.

**Source:** https://www.fico.com/blogs/today-s-no-hit-applicant-may-be-tomorrow-s-profitable-long-term-customer (accessed 2026-03-12); https://vantagescore.com/resources/knowledge-center/homeownership-just-got-easier-for-millions-with-limited-credit-history-thanks-to-vantagescore-4-0-vantagescore-in-forbes (accessed 2026-03-12)

**Thin file direct mapping to Submantle:**
The prior council settled that Beta's 0.5 initialization is mathematically correct but commercially the API should distinguish "no history" from "scored at 0.5." FICO confirms this is the right instinct: credit bureaus do not call 0.5 a score, they call it "no data." Submantle should treat `total_queries == 0` as a distinct "no history" state, with a separate `has_history: false` field in the API response, alongside the computed 0.5. This is not a formula change — it is an API metadata change.

**Weight versioning mechanism:**
FICO does not change weights within a version — FICO 8 still uses the same weights it launched with in 2009. When weights need to change, FICO releases a *new version number* (FICO 9, FICO 10, FICO 10T). Old versions remain fully supported and in active use simultaneously — currently 16 distinct versions are in market. The strategy: "FICO continues to support legacy versions because they remain highly effective and see heavy usage in the marketplace."

There is no retroactive recalculation of past scores under a new version. The new version is a separate product. Lenders choose which version to run. Historical scores computed under FICO 8 remain FICO 8 scores; new scores computed under FICO 10 are FICO 10 scores. The version is always known.

**Source:** https://www.myfico.com/credit-education/credit-scores/fico-score-versions (accessed 2026-03-12); https://www.certifiedcredit.com/fico-score-updates/ (accessed 2026-03-12)

**Direct mapping to Submantle:**
- Each scoring formula is a versioned artifact. When Submantle changes weights in the Go rewrite, that is "version 2." Scores computed under v1 are labeled `score_version: 1`. Brands consuming the API see which version produced the score. This prevents "the threshold we set last year no longer means what it meant" without any system disruption.
- FICO's 16 simultaneous versions confirm that **version coexistence is operationally standard** in production trust infrastructure. Submantle's initial complexity is lower: V1 has one formula, Go rewrite introduces v2. Two versions.

### 1.2 D&B PAYDEX — Dollar-Weighted Average, Non-Human Entity Scoring

**What it is:** PAYDEX is D&B's payment behavior score for *businesses* (not consumers) — scored 1–100. It is the most direct precedent for scoring non-human entities (like AI agents) based on behavioral history.

**Exact formula:** PAYDEX is a dollar-weighted average of payment-class index scores:
1. Sum high-credit dollar amounts by payment class (Anticipates, Discount, Prompt, Slow-15, Slow-30, etc.)
2. Compute each class's percentage share of total dollars
3. Multiply each class's share by its index weight
4. Sum the products

**Payment class index weights:**
- Anticipates (pays before due): 100
- Discount (pays within discount window): 90
- Prompt (pays on time): 80
- Slow-15 (up to 15 days late): 70
- Slow-30 (16–30 days late): 50
- Slow-60: ~30
- Slow-90+: ~10–20
- Unpaid: 0

**Worked example:** 50% of dollars at Discount (90), 25% at Prompt (80), 25% at Slow-30 (50) → PAYDEX = 0.50×90 + 0.25×80 + 0.25×50 = **77**

**Source:** https://www.nav.com/business-credit-scores/dun-bradstreet-paydex/ (accessed 2026-03-12); https://www.dnb.com/en-us/smb/resources/credit-scores/what-is-paydex-score.html (accessed 2026-03-12); https://docs.dnb.com/static/doc-uploads/supplier/en-US/support/FAQs.pdf (accessed 2026-03-12)

**Thin file / minimum data requirement:**
PAYDEX requires **at least two trade references (reporters)** — two suppliers who have done business with the entity must report payment history before a PAYDEX score is generated at all. With zero or one trade reference, the entity has no PAYDEX score. D&B uses up to 874 trade experiences for a fully mature score.

**Direct mapping to Submantle:**
The "two reporters minimum" rule maps precisely: Submantle should require at least two distinct registered reporters to have interacted with an agent before the score is presented as meaningful (though Beta's 0.5 initialization remains as the baseline). The `has_history` flag could also incorporate a `reporter_diversity: N` count — brands see "this score is based on reports from 2 distinct sources" vs "12 sources," which parallels PAYDEX's transparency.

The dollar-weighting of PAYDEX is highly relevant: **D&B weights transactions by dollar value because a $1M payment tells you more than a $1 payment.** For Submantle, the parallel is **interaction type severity** — a data exfiltration incident carries more weight than a rate-limit violation. The current formula treats all incidents as equal (like a PAYDEX that treats a $1 late payment the same as a $1M late payment). The fix is not to change the Beta formula for V1, but to confirm the design decision to weight incident types in the Go rewrite.

**Key distinction:** PAYDEX is a rolling average — it reflects current payment behavior. High weight for recent transactions. No permanent scoring of old behavior. Submantle's Beta formula is cumulative, not rolling — this is a design choice worth documenting, not a flaw.

### 1.3 VantageScore 4.0 — Weight Evolution Without Breaking Scores

**What it is:** VantageScore 4.0 uses a different category structure from FICO with different weights:
- Payment History: ~40% (vs FICO's 35%)
- Credit Utilization: ~20% (vs FICO's 30%)
- Age and Type of Credit: ~21%
- New Credit: ~5%
- Balances: ~6%
- Available Credit: ~2–3%
- Trended behavior: incorporated as modifier

**Source:** https://fhmtg.com/2025/08/14/what-are-the-differences-between-vantagescore-vs-fico-credit-scoring-models/ (accessed 2026-03-12)

**The migration coexistence pattern:** As of November 2025, Fannie Mae updated its disclosures to include both Classic FICO and VantageScore 4.0 fields simultaneously. Lenders choose which model to submit. Neither replaces the other. 41.7 billion VantageScore scores were used in 2024, up 55% from 26.9 billion in 2023 — demonstrating that a new scoring model can gain massive adoption without requiring migration of existing scores.

**Source:** https://capitalmarkets.fanniemae.com/mortgage-backed-securities/single-family-mbs/november-2025-disclosure-enhancements-vantagescore (accessed 2026-03-12)

**Critical versioning insight:**
VantageScore 4.0's biggest innovation for thin files: **minimum credit history reduced to one month** (vs FICO's typical 6-month minimum). This was done by adding alternative data signals, not by changing the fundamental math. The formula evolved to accept more inputs while the score range (300–850) stayed constant. Existing scores were not recalculated; new scores simply incorporated more data.

**Direct mapping to Submantle:**
This is the "record interaction types now, weight them later" pattern confirmed by a real-world system at scale. VantageScore 4.0 added trended data as a modifier, not as a formula replacement. The Beta formula stays; the inputs become richer over time.

---

## Angle 1 Score Table

| System | Relevance | Maturity | Community Health | Integration Effort | Overall Risk | Reversibility | Evidence Confidence |
|--------|-----------|----------|------------------|--------------------|--------------|---------------|---------------------|
| FICO Weighted Categories | 9/10 | 10/10 | 9/10 | 8/10 | 9/10 | 8/10 | 9/10 |
| FICO Version Coexistence Model | 10/10 | 10/10 | 10/10 | 9/10 | 10/10 | 9/10 | 9/10 |
| D&B PAYDEX Non-Human Entity Scoring | 9/10 | 9/10 | 8/10 | 8/10 | 9/10 | 7/10 | 9/10 |
| D&B Two-Reporter Minimum | 9/10 | 9/10 | 8/10 | 9/10 | 10/10 | 9/10 | 9/10 |
| VantageScore Thin File Expansion | 8/10 | 8/10 | 9/10 | 7/10 | 8/10 | 8/10 | 8/10 |

**Overall Angle 1 Confidence: 9/10** — Three well-documented production systems with decades of evidence. Sources are authoritative (FICO, D&B, FHFA, Fannie Mae). All findings verified against multiple sources.

---

## Angle 2: Reputation System Evolution — Weight Versioning and Score Migration

### 2.1 eBay DSR: The Additive Dimension Migration Pattern (2007–2008)

**What happened:** eBay introduced Detailed Seller Ratings (DSRs) in May 2007, adding four sub-dimensions (item description accuracy, communication, shipping speed, shipping charges) rated 1–5 stars alongside the existing positive/negative feedback count. In 2008, eBay went further: sellers could no longer receive negative feedback from buyers (unilateral feedback restriction).

**The migration pattern — preserve plus augment:**
- The existing positive/negative feedback *count* (the legacy "score") was **preserved unchanged**. Sellers kept every point they had earned.
- DSRs were *additive* — a new parallel track, not a replacement. The feedback count remained the primary score; DSRs were displayed as separate averages alongside it.
- No retroactive recalculation. Old feedback left before DSRs existed simply did not have DSR data attached. The score was not penalized for "missing" DSR data on old transactions.
- The new dimension (DSRs) only accumulated from the launch date forward.

**The practical result:** Established sellers with 10,000 positive feedbacks kept all 10,000. New DSR dimensions started at zero and built over time. The two tracks coexisted.

**What broke:** eBay's 2008 unilateral feedback change (sellers cannot leave negative feedback for buyers) generated massive seller backlash. The *content policy* change, not the *scoring model* change, created the controversy. This is a clean data point: formula changes are survivable; enforcement and policy changes are the dangerous ones.

**Source:** https://algopix.com/glossary/ebay-dsr (accessed 2026-03-12); https://www.auctionnudge.com/guides/the-lowdown-on-ebays-seller-rating-system/ (accessed 2026-03-12); academic table: https://www.researchgate.net/figure/Recent-changes-in-the-eBays-feedback-system_tbl2_220300488 (accessed 2026-03-12)

**DSR composition — the hidden insight:**
DSRs are not composited into the feedback score. They sit alongside it as separate numbers. eBay uses DSRs to determine *eligibility for programs* (Top Rated Seller status) but not to change the feedback count. This is the exact architecture the prior council settled on: `trust_metadata` carries enrichment data, the Beta formula remains the authoritative score. eBay validated this architecture in production for 18 years.

**Current state (2026):** eBay's September 2025 Seller Update introduced automatic positive feedback for eligible orders — further automating the positive-signal accumulation, which maps to Submantle's `record_query()` model (interactions auto-accumulate as positive signal unless contested).

**Source:** https://www.valueaddedresource.net/ebay-us-august-2025-seller-update/ (accessed 2026-03-12)

### 2.2 Airbnb: Weight Shift Without Score Replacement

**What happened:** Airbnb's algorithm has undergone multiple evolutions from simple star rating (1–5) to a multi-dimensional system rating six specific categories:
- Cleanliness
- Accuracy
- Check-in
- Communication
- Location
- Value

**Current composition (2025 observed behavior):**
- Individual category scores (cleanliness, accuracy, check-in) are weighted **twice as heavily** as the overall rating in search ranking algorithms.
- The displayed "overall star rating" visible to guests is a simple average of the single overall rating guests give.
- The category sub-ratings affect *ranking and badge eligibility*, not the displayed score.

**Source:** https://triadvacationrentals.com/blog/airbnb-algorithm-and-how-to-rank-higher (accessed 2026-03-12); https://www.rentalscaleup.com/airbnb-highlight-system-top-1-percent-guest-favorite-2025/ (accessed 2026-03-12)

**The migration pattern:**
- Guest Favorites (2024/2025 change) replaced the Superhost badge. Old Superhost histories were not erased — hosts either retained the badge or lost it based on the new criteria, applied going forward.
- The 2025 Summer Release shifted algorithm weight toward *recent* performance, but historical ratings were not deleted — they were simply down-weighted in ranking. A host with 500 historical 5-star reviews did not lose those reviews; they just mattered less in search ranking than the last 90 days.
- Airbnb publicly announced these changes and gave hosts 30–90 days advance notice. Existing scores remained visible throughout.

**Source:** https://awning.com/post/airbnb-system-updates (accessed 2026-03-12)

**Direct mapping to Submantle:**
Airbnb's pattern: the *displayed score* and the *ranking/eligibility algorithm* can diverge. Submantle's Beta score is the displayed score (like Airbnb's star rating). The trust_metadata enrichment (interaction diversity, reporter credibility count, account age) is the ranking/eligibility signal (like Airbnb's sub-dimensions). Brands that want to use sub-dimensions can; brands that just want the number get the number. This pattern has 10+ years of Airbnb production evidence behind it.

### 2.3 Uber: The Rolling Window Migration Pattern

**What happened:** Uber's driver rating is a rolling average of the most recent 500 trips (not all-time). When Uber adds sub-rating dimensions (e.g., "excellent conversation," "expert navigation"), these are:
- Displayed as separate counts, not composited into the 1–5 score
- The 1–5 score remains the raw average of rider ratings
- New metrics build from their introduction date forward — no retroactive data

**Key migration insight:** Uber's "fresh start" for new metrics means that when a new sub-dimension is added, all drivers start at zero for that dimension simultaneously. There is no disadvantage for established drivers versus new drivers on the new dimension — the playing field resets for new signals. This is the cleanest migration pattern for additive signals.

**Normalization mechanism:** Uber uses city-level averages to anchor deactivation thresholds (a 4.6 minimum may be different in San Francisco vs Nairobi due to cultural rating differences). This is a *threshold adjustment* at the consumer side, not a formula change. The score formula is unchanged; what changes is what brands/Uber does with the score. This is exactly Submantle's model: Submantle provides the score, brands set their own thresholds.

**Source:** https://www.uber.com/ca/en/drive/basics/how-ratings-work/ (accessed 2026-03-12); https://news.stanford.edu/stories/2025/08/uber-ride-sharing-quality-control-ratings-incentive-system-research (accessed 2026-03-12); https://www.uber.com/blog/umetric/ (accessed 2026-03-12)

### 2.4 PeerTrust: Academic Weighted Reputation with Credibility Factors

**What it is:** PeerTrust (Xiong & Liu, IEEE TKDE 2004, widely cited in P2P trust literature) is the canonical academic framework for weighted trust computation that accounts for reporter credibility. The formula is:

`T(u) = Σ[S(u,i) × Cr(v) × TF(u,i)] × CF(u) / Σ|I(u)|`

Where:
- **S(u,i)**: Normalized satisfaction score from transaction i (0–1)
- **Cr(v)**: Credibility factor of the feedback source (the reporter) — this is the key innovation
- **TF(u,i)**: Transaction context factor (adaptive weight based on transaction characteristics)
- **CF(u)**: Community context factor (adaptive modifier)
- **I(u)**: Total interaction count

**Source:** https://www.comp.nus.edu.sg/~cs6203/guidelines/topic7/peer-trust.pdf (accessed 2026-03-12)

**The reporter credibility mechanism — direct Submantle parallel:**
PeerTrust uses two methods to compute `Cr(v)`:
1. **TVM (Trust Value Model):** The reporter's own trust score is their credibility weight. A reporter with trust 0.9 has their report weighted at 0.9; a reporter with trust 0.3 has their report weighted at 0.3. Recursive, self-reinforcing.
2. **PSM (Personalized Similarity Model):** Reporter credibility is computed from historical agreement with consensus. A reporter whose past reports aligned with eventual outcomes scores higher. A reporter with 80% false-report history gets near-zero weight.

**Recent extension (2024–2025):** Beta-PT, a published extension of PeerTrust, explicitly incorporates Beta distribution priors (Bayesian-Beta) and "introduces mild penalties for newcomers while damping the influence of overactive reviewers." This is the closest academic analog to Submantle's current formula.

**Source:** https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0336039 (accessed 2026-03-12); https://arxiv.org/html/2511.19930 (accessed 2026-03-12)

**Direct mapping to Submantle:**
The PeerTrust `Cr(v)` mechanism is the precise design answer to the question: "how should reporter credibility weight incident reports?" The deterministic implementation:
- Each reporter has their own Beta score (total_accepted_reports, total_expired_reports)
- When a reporter's report is accepted: increment total_accepted for that reporter
- When a reporter's report expires or is rejected: increment total_expired for that reporter
- Reporter credibility = Beta(accepted+1, expired+1) = same formula Submantle uses for agents
- An incident's formula weight = `base_weight × reporter_credibility_score`

This is fully deterministic, no ML, self-bootstrapping, and produces a transparent audit trail.

### 2.5 The Migration Pattern Synthesis

Across eBay, Airbnb, Uber, and PeerTrust, one consistent migration pattern emerges:

**The Three-Layer Architecture:**
1. **Legacy score (preserved):** The existing score formula is never changed retroactively. Existing scores retain their meaning and value.
2. **Additive metadata (accumulated from launch):** New dimensions start accumulating from the moment they are introduced. Old entities don't have historical data for the new dimension; that's acceptable.
3. **Threshold/eligibility layer (brand-controlled):** Brands decide how to use the score and metadata. They can apply sub-dimension gates independently of the main score.

**The Score Version Tag:**
No production system found leaves scores version-unlabeled. FICO has numbered versions. SecurityScorecard has version 3.0. D&B has PAYDEX (distinct from their other scores). Every time weights change, the version identifier changes. The score without its version is incomplete data.

---

## Angle 2 Score Table

| System | Relevance | Maturity | Community Health | Integration Effort | Overall Risk | Reversibility | Evidence Confidence |
|--------|-----------|----------|------------------|--------------------|--------------|---------------|---------------------|
| eBay DSR Migration Pattern | 8/10 | 9/10 | 8/10 | 9/10 | 9/10 | 9/10 | 8/10 |
| Airbnb Two-Track Architecture | 8/10 | 8/10 | 7/10 | 9/10 | 8/10 | 9/10 | 7/10 |
| Uber Rolling Window + Threshold Split | 7/10 | 9/10 | 8/10 | 8/10 | 8/10 | 8/10 | 7/10 |
| PeerTrust Reporter Credibility (Cr(v)) | 9/10 | 7/10 | 7/10 | 7/10 | 8/10 | 7/10 | 8/10 |
| Beta-PT Academic Extension | 8/10 | 5/10 | 6/10 | 6/10 | 7/10 | 7/10 | 7/10 |

**Overall Angle 2 Confidence: 8/10** — Well-documented production systems (eBay, Airbnb, Uber) provide strong migration pattern evidence. Academic PeerTrust is peer-reviewed and directly applicable. Beta-PT is newer (2024–2025) and less proven in production.

---

## Angle 3: Deterministic Composite Scoring in Fintech, Insurance, and Cybersecurity

### 3.1 SecurityScorecard Scoring 3.0 — The Recalibration Model

**What it is:** SecurityScorecard rates organizations on a 0–100 scale across 10 risk factor categories. Scoring 3.0 (launched April 2024) is the most recently evolved version of a mature cybersecurity trust score.

**Composition structure:**
- 200+ weighted issue types are defined
- Each issue type has a weight based on "relative breach risk" calibrated against 15,000+ documented breaches
- Issue type weights are the **only weights that impact the total score** — factor categories no longer have their own weights in 3.0 (this was a change from prior versions)
- The 10 factor categories now serve as organizational groupings with 0–100 sub-scores, but they don't directly compose into the total score — the issue type weights do
- Issue type weights "do not change and are the same for all companies" — this is the deterministic guarantee

**The formula structure (from their documentation):** The overall score is computed by aggregating weighted issue type findings across all assets. The composition is additive within each severity tier, with tiered multipliers applied for severity levels.

**Source:** https://securityscorecard.com/blog/securityscorecard-10-risk-factors-explained/ (accessed 2026-03-12); search results from query "SecurityScorecard methodology 2025 2026" (accessed 2026-03-12)

**The recalibration model — key evidence for Submantle:**
SecurityScorecard performs **quarterly scoring recalibrations**:
- October 21, 2025 recalibration: decreased impact of 8 issue types, increased impact of 2 issue types
- February 18, 2026 recalibration: decreased impact of 3 issue types, increased impact of 3 issue types; no new issue types added

**What happens to existing scores:** When a recalibration runs, scores change immediately for all entities based on new weights applied to current findings. There is no "FICO version coexistence" — all entities move to the new weights simultaneously. However, SecurityScorecard provides:
- Advance notice (weeks before recalibration)
- Preview score under new weights
- The recalibration is not retroactive to past scores stored in customer reports
- API backward compatibility is maintained at the endpoint level; the score fields return the same schema, just updated values

**Source:** https://support.securityscorecard.com/hc/en-us/articles/40187012005275-Scoring-Recalibration-October-21-2025 (accessed 2026-03-12); https://support.securityscorecard.com/hc/en-us/articles/44219572850587-Upcoming-scoring-recalibration-February-18-2026 (accessed 2026-03-12)

**The machine learning boundary:**
SecurityScorecard uses ML to *identify and classify findings* (what is a security issue), but once issue types are established, their weights are deterministic and fixed. The score computation is pure math. This is a useful distinction: ML at the data collection layer (what counts as an incident) is separate from the scoring formula layer (how incidents weight against each other). Submantle has made the cleaner choice — no ML at either layer — but SecurityScorecard confirms that deterministic weights at the scoring layer are production-proven.

**Source:** https://securityscorecard.com/wp-content/uploads/2024/01/Applying-Machine-Learning-to-Optimize-the-Correlation-of-SecurityScorecard-Scores-with-Breach-Likelihood.pdf (accessed 2026-03-12)

**The breach-correlation calibration:**
SecurityScorecard's weights are calibrated against real breach outcomes: "Drawing insights from a vast dataset of over 15,000 breaches, our data scientists identified key issue types with significant predictive capabilities." A company scoring F (≤60) is 13.8× more likely to experience a breach than one scoring A (90–100). This is the gold standard for weight calibration: weights are derived from observed outcomes, not arbitrary assignments. Submantle's equivalent: weights on incident types should eventually be calibrated against observed downstream harm rates (brands reporting which incident types actually caused problems). This requires data collection now to enable calibration later.

**Direct mapping to Submantle:**
SecurityScorecard's quarterly recalibration model is the **simultaneous recalibration** approach — all entities get new scores when weights change. FICO's versioned model is the **version fork** approach — new formula is a new product, old scores preserved. For Submantle's V1-to-Go-rewrite transition, either approach works. The recommendation: use FICO's version fork approach (label scores with `score_version: 1` vs `score_version: 2`), not SecurityScorecard's simultaneous recalibration, because Submantle's brands will build business logic around thresholds that should not silently shift.

### 3.2 ISO FSRS — The Divergence Factor in Additive Models

**What it is:** ISO's Fire Suppression Rating Schedule (FSRS) scores communities for fire protection risk. It produces a Public Protection Classification (PPC) used directly in insurance pricing. It is a classic fully deterministic, no-ML composite score.

**Exact weighted composition:**
- Fire Department: **50 points**
- Water Supply: **40 points**
- Emergency Communications: **10 points**
- Community Risk Reduction (bonus): up to **5.5 points**
- Total possible: **105.5 points** (mapped to PPC 1–10 rating)

**The divergence factor — critical insight:**
When the fire department score and water supply score differ significantly, the FSRS applies a **downward divergence adjustment** to the total. A community with an excellent fire department but inadequate water supply scores lower than the additive sum of the two components would suggest. The weakest link limits the strongest link.

**Source:** https://www.isomitigation.com/ppc/fsrs/ (accessed 2026-03-12); https://www.federato.ai/library/post/how-iso-fire-protection-ratings-drive-optimal-insurance-pricing (accessed 2026-03-12)

**Direct mapping to Submantle:**
The divergence factor is a powerful concept for Submantle's weighted scoring model. Consider: an agent with 10,000 queries and 0 incidents scores nearly 1.0 under the Beta formula. But if all 10,000 queries are to one single brand (no diversity) and registered 1 day ago — the agent looks good on the primary metric but weak on secondary signals. A divergence-style adjustment would say: if interaction_diversity < threshold, the raw Beta score is discounted.

This is implementable as: `adjusted_score = raw_beta_score × diversity_multiplier`, where `diversity_multiplier` is 1.0 for diverse interactions and degrades toward 0.5 for single-reporter concentration. This stays deterministic, transparent, and fully explainable.

### 3.3 Moody's Weighted Scorecard — The Additive-to-Narrative Pattern

**What it is:** Moody's rates financial institutions using a scorecard where sub-factor scores are multiplied by weights and summed to produce an aggregate numeric score.

**Structure:** "The numeric score for each sub-factor is multiplied by the weight for that sub-factor, with the results then summed to produce an aggregate numeric score." This is additive composition.

- Business Profile factors: 35% of total
- Financial Profile factors: 65% of total
- Within each, sub-factors have their own weights that sum to 100% within the parent

**Key principle:** "The weights represent an approximation of their importance across the sector, but the actual importance of a particular factor may vary substantially based on an individual company's circumstances." — This is why Moody's analysts can override the scorecard-indicated outcome based on qualitative assessment. The scorecard is an input, not a final answer.

**Source:** https://ratings.moodys.com/api/rmc-documents/418351 (accessed 2026-03-12); search result summary from Moody's methodology PDF (accessed 2026-03-12)

**Direct mapping to Submantle:**
Moody's model confirms: an additive weighted scorecard works at institutional scale for non-consumer entity scoring. The "analyst override" concept is the enterprise analog to Submantle's human review queue — the deterministic score is the default, human judgment can modify it in edge cases. The weights are transparent, documented, and sector-calibrated.

### 3.4 Qualys TruRisk — Multiplicative-Additive Hybrid

**What it is:** Qualys TruRisk composes vulnerability risk into an Asset Risk Score (ARS) using a hybrid multiplicative-additive formula.

**Structure:**
`ARS = ACS × [wc × Avg(QDS_critical) × f(critical_count) + wh × Avg(QDS_high) × f(high_count) + ...] × I(External)`

Where:
- **ACS:** Asset Criticality Score (a multiplier for how important the asset is)
- **wc, wh, wm, wl:** Severity-tier weights (fine-tuned constants)
- **f(count):** Exponential scaling function — more vulnerabilities of the same severity increase risk non-linearly
- **I(External):** Binary flag — externally-exposed assets score higher

**Key insight:** The formula is **multiplicative at the top level** (asset criticality multiplies everything) and **additive across severity tiers**. Individual issue weights compose additively; severity context multiplies the result. This hybrid pattern produces non-linear behavior without ML.

**Source:** https://blog.qualys.com/qualys-insights/2022/10/10/in-depth-look-into-data-driven-science-behind-qualys-trurisk (accessed 2026-03-12); https://docs.qualys.com/en/vmdr/latest/mergedProjects/prioritize_your_vulnerabilities/threat/calculating_asset_risk_score.htm (accessed 2026-03-12)

**Direct mapping to Submantle:**
The multiplicative asset criticality concept maps to Submantle's reporter credibility concept: a reporter with a high trust score should multiply the weight of their incident reports, not just add to them. The formula becomes:

`effective_incidents = Σ(incident_severity_weight × reporter_credibility_score)`

Rather than simply counting incidents, Submantle counts credibility-weighted, severity-adjusted incidents. This is fully deterministic, fully explainable, and directly analogous to a production system that processes millions of assets.

The exponential scaling function `f(count)` for multiple vulnerabilities at the same severity is also notable — Submantle may eventually want to apply non-linear scaling to the incident count when an agent has many incidents of the same type, as this signals a systematic behavior pattern rather than isolated incidents.

---

## Angle 3 Score Table

| System | Relevance | Maturity | Community Health | Integration Effort | Overall Risk | Reversibility | Evidence Confidence |
|--------|-----------|----------|------------------|--------------------|--------------|---------------|---------------------|
| SecurityScorecard Scoring 3.0 | 9/10 | 8/10 | 8/10 | 8/10 | 8/10 | 7/10 | 9/10 |
| SecurityScorecard Recalibration Model | 9/10 | 8/10 | 8/10 | 8/10 | 8/10 | 6/10 | 9/10 |
| ISO FSRS Divergence Factor | 8/10 | 10/10 | 7/10 | 8/10 | 9/10 | 8/10 | 9/10 |
| Moody's Additive Weighted Scorecard | 7/10 | 10/10 | 8/10 | 7/10 | 9/10 | 7/10 | 8/10 |
| Qualys TruRisk Multiplicative-Additive | 8/10 | 7/10 | 7/10 | 6/10 | 7/10 | 6/10 | 8/10 |

**Overall Angle 3 Confidence: 9/10** — SecurityScorecard is directly analogous (trust scores for technical entities, quarterly recalibration, deterministic weights). ISO FSRS is decades-proven. Qualys TruRisk is current (2024–2025) documentation with specific formulas. Sources verified.

---

## Battle-Tested Approaches

These approaches have production evidence and survive Submantle's constraints (no ML, deterministic, single score for V1):

### A. Score Version Tagging (FICO Model)
**Pattern:** When formula weights change, issue a new version number. Old scores remain valid under their original version. New scores are computed under the new version. Both coexist.
**Evidence:** 16 FICO versions simultaneously in market. FICO 8 (2009) still dominant in 2026.
**Submantle application:** Every score returned by the API includes `score_version: 1`. When the Go rewrite introduces weighted dimensions, that becomes `score_version: 2`. Brands that built logic on v1 scores are not broken. This requires one additional field in the API response.
**Effort:** Minimal — one integer column in agent_registry, one field in compute_trust() return dict.

### B. Reporter Credibility as Multiplicative Weight (PeerTrust Cr(v))
**Pattern:** Each reporter has their own Beta score (accepted reports / total reports). Their credibility score multiplies the weight of each incident they file.
**Evidence:** PeerTrust (IEEE TKDE 2004, thousands of citations); Beta-PT (2024–2025 extension).
**Submantle application:** `effective_incident_weight = base_severity_weight × reporter_credibility` where reporter_credibility = Beta(accepted+1, expired+1). The formula `incidents` counter becomes a sum of weighted incident values rather than a count of incidents. Fully deterministic, fully explainable.
**Effort:** Medium — requires reporter_registry with accepted/expired counters, changes to how `incidents` is accumulated in the formula.
**Constraint check:** Does NOT require ML. Fully deterministic. EU AI Act safe.

### C. Two-Track Architecture (eBay DSR / Airbnb)
**Pattern:** Primary score (Beta formula) is the authoritative number. Sub-dimensions (interaction type diversity, reporter credibility count, account age, corroboration count) are stored in trust_metadata and returned alongside the score. Brands can use sub-dimensions as eligibility gates without touching the formula.
**Evidence:** eBay 18 years in production. Airbnb 10+ years. Both show that sub-dimensions add value for sophisticated consumers without complicating the primary number.
**Submantle application:** This is exactly the trust_metadata architecture the prior council settled. External evidence fully validates it.
**Effort:** Already designed (trust_metadata column exists). Implementation effort is data population.

### D. Severity-Weighted Incident Accumulation (D&B PAYDEX / ISO FSRS)
**Pattern:** Not all events count equally. D&B weights late payments by dollar amount. ISO weights fire department vs water supply by their relative importance. The formula counts weighted severity units, not raw event counts.
**Evidence:** D&B PAYDEX (decades old, industry standard). ISO FSRS (50+ year history).
**Submantle application:** `incidents_weighted = Σ(formula_weight per incident)` where formula_weight is 1.0 for data_exfiltration, 0.7 for unauthorized_access, 0.3 for rate_limit_violation. The `incidents` value in Beta becomes the sum of these weights rather than a count. Compatible with the review tier design (Team 3 already defined `formula_weight REAL NOT NULL DEFAULT 1.0` as a column on incident_reports).
**Effort:** Low — Team 3's schema already includes formula_weight. The only change is to make the Beta formula sum formula_weight values rather than count rows.
**Constraint check:** Fully deterministic. Weights are a published enumeration, not ML inference.

### E. Divergence Factor for Gaming Detection (ISO FSRS)
**Pattern:** When two key dimensions diverge significantly from each other, the total score is discounted. Prevents gaming a single dimension while leaving others weak.
**Evidence:** ISO FSRS divergence factor is a standard actuarial technique.
**Submantle application:** If interaction_diversity < threshold (e.g., 90% of queries from one brand), apply a diversity multiplier that reduces the raw Beta score. Formula: `adjusted_score = raw_beta × min(1.0, diversity_score)` where diversity_score = 1 - concentration_ratio. Fully deterministic, transparent in the API response.
**Effort:** Medium — requires tracking interaction_diversity in trust_metadata, one additional multiplier in compute_trust().

---

## Novel Approaches

These approaches have less direct precedent but are well-grounded in research:

### F. Interaction Type Weighting as Formula Modifier (Not Replacement)
**Pattern:** Record interaction types now (settled decision). When Go rewrite arrives, weight them as multipliers on the query count. High-quality interactions (multi-step, cross-domain, enterprise API calls) count more than simple queries.
**Evidence:** D&B PAYDEX's dollar-weighting precedent. VantageScore 4.0's trended behavior modifier.
**Risk:** The weights are initially arbitrary — no real-data calibration is possible until interaction type data accumulates. Must ship the recording infrastructure now to enable calibration later.

### G. Minimum Reporter Diversity Threshold (D&B Two-Reporter Minimum)
**Pattern:** Before presenting a score as meaningful, require at least N distinct reporters to have filed reports (incidents or interactions). Prevents single-source manipulation.
**Evidence:** D&B requires minimum 2 trade references for PAYDEX to exist at all.
**Submantle application:** API response includes `reporter_diversity: N` — the count of distinct registered reporters who have interacted with this agent. Brands can apply their own minimum (e.g., require reporter_diversity ≥ 3 before accepting the score as meaningful). Submantle does not enforce this threshold — brands do. Consistent with "always aware, never acting."

---

## Emerging Approaches

### H. Formula Weight Calibration Against Outcome Data
**Pattern:** SecurityScorecard calibrates issue type weights against 15,000 documented breach outcomes. Qualys calibrates vulnerability weights against EPSS (Exploit Prediction Scoring System) and CISA KEV (Known Exploited Vulnerabilities). Both produce weights that are empirically derived from observed harm.
**Relevance:** Submantle's eventual weight calibration (when incident type severity weights are introduced) should be grounded in real outcome data from the agent ecosystem, not arbitrary designer intuition.
**Constraint check:** The calibration process may use ML or statistics — but the *resulting weights*, once fixed as constants, are deterministic at scoring time. This is the same boundary SecurityScorecard draws.

---

## Gaps and Unknowns

1. **The bootstrapping problem for reporter credibility:** PeerTrust's Cr(v) mechanism requires reporters to have existing credibility scores before their reports are weighted. New reporters start with Beta(1,1) = 0.5 credibility — the same as new agents. This means the first incidents from new reporters get half-weight, which may be too cautious for legitimate early reporters. The D&B model (minimum 2 reporters before a score is valid) provides a different solution: don't present the score as authoritative until minimum reporter diversity is met. The right approach is unclear and requires empirical data.

2. **Severity weight calibration without outcome data:** Submantle has no real-world data on which incident types actually cause downstream harm. Assigning data_exfiltration = 1.0 and rate_limit_violation = 0.3 is principled but not empirically calibrated. The weights must be versioned (see Approach A) precisely because they will need to change as real outcome data accumulates.

3. **PAYDEX recency weighting vs. Beta cumulative accumulation:** D&B PAYDEX is a rolling average that down-weights old behavior. Beta is cumulative — old behavior never leaves. The prior council's Devil's Advocate identified stale scores on compromised high-reputation agents as a medium-risk gap. External evidence from D&B confirms the risk is real: an agent that behaved well for 2 years and then went rogue will have a high score that doesn't decay. The solution (rolling window, time decay, or recency multiplier) is not settled. This research confirms it needs design attention, but V1 is not the right time — real data is needed to calibrate any decay function.

4. **Score version coexistence in a single-tenant SQLite:** When the Go rewrite introduces score_version 2, old scores in the SQLite database were computed under version 1. The API needs to clearly label which version produced which score. A `score_version` column on agent_registry (or on score audit logs) is necessary infrastructure to enable future version coexistence. Building it now costs one column; not building it creates a migration problem later.

5. **The "good actor gaming a new dimension" problem:** Every time Submantle adds a new trust signal (interaction type diversity, reporter count, account age), sophisticated agents will optimize for it. This is not a reason to avoid adding signals — FICO, D&B, and SecurityScorecard all face this — but it means each new signal needs an anti-gaming rule documented at the time it is added.

---

## Synthesis

The external evidence converges on a composite scoring design with four layers:

### Layer 1: The Beta Formula (unchanged, V1)
`trust = (q+1) / (q+i+2)`
where `q` = velocity-capped query count, `i` = sum of accepted incident formula_weights

The only changes from the current implementation:
- `q` is velocity-capped (anti-gaming, already settled)
- `i` is the SUM of formula_weights on ACCEPTED incidents (not a count) — enables severity weighting without formula replacement
- Score returned with `score_version: 1` field

### Layer 2: Input Quality Guards (V1 ship requirement)
- Velocity caps on q accumulation (self-query inflation defense)
- formula_weight per accepted incident (severity taxonomy, Team 3 schema already designed this)
- reporter_credibility used for formula_weight modifier = base_severity_weight × Cr(reporter) — this is the PeerTrust Cr(v) mechanism applied to incident weight

### Layer 3: trust_metadata Enrichment (V1 data collection, display only)
- interaction_diversity: ratio of distinct brands to total queries
- reporter_diversity: count of distinct registered reporters who have filed reports
- has_history: true/false (FICO thin file parallel)
- score_version: 1
- These fields are returned in the API alongside the score but do not affect the formula

### Layer 4: Divergence Multiplier (Go rewrite, not V1)
`adjusted_score = raw_beta × min(1.0, diversity_score)`
where diversity_score = 1 - (max_single_brand_query_share)

This layer is the ISO FSRS divergence factor applied to gaming defense. It requires real data on normal interaction diversity patterns before calibration. Do not build for V1.

### The Score Versioning Protocol
Every compute_trust() response includes `score_version: 1`. When the Go rewrite changes any weight, formula, or multiplier, that becomes `score_version: 2`. Scores under different versions are not directly comparable (same as FICO 8 vs FICO 10). The API documents each version's formula in a publicly accessible endpoint. This is the FICO coexistence model applied to Submantle's scale.

### The Migration Pattern (When the Time Comes)
Based on eBay DSR, Airbnb, and Uber evidence:
1. New dimensions accumulate from introduction date — no retroactive data
2. Old scores retain their version label and remain valid under that version
3. Advance notice (minimum 30 days) to brands before formula changes take effect
4. Preview scores under the new formula available before the cutover date
5. Both versions return in API responses during transition period

This is the Three-Layer Architecture confirmed by three independent production systems at scale.

---

## Sources

All sources accessed 2026-03-12 unless otherwise noted.

- [myFICO — What's In Your Credit Score](https://www.myfico.com/credit-education/whats-in-your-credit-score)
- [myFICO — FICO Score Versions](https://www.myfico.com/credit-education/credit-scores/fico-score-versions)
- [FICO Blog — No-Hit Applicants (thin file)](https://www.fico.com/blogs/today-s-no-hit-applicant-may-be-tomorrow-s-profitable-long-term-customer)
- [FICO Fall 2025 Credit Insights Report](https://www.fico.com/en/latest-thinking/market-research/fico-score-credit-insights-fall-2025-edition)
- [Certified Credit — FICO Score Updates](https://www.certifiedcredit.com/fico-score-updates/)
- [D&B — What is a PAYDEX Score](https://www.dnb.com/en-us/smb/resources/credit-scores/what-is-paydex-score.html)
- [NAV — D&B PAYDEX Score Methodology](https://www.nav.com/business-credit-scores/dun-bradstreet-paydex/)
- [LendingTree — PAYDEX Score](https://www.lendingtree.com/business/paydex-score/)
- [D&B FAQs PDF (Trade Algorithm)](https://docs.dnb.com/static/doc-uploads/supplier/en-US/support/FAQs.pdf)
- [VantageScore — Homeownership and Thin Files](https://vantagescore.com/resources/knowledge-center/homeownership-just-got-easier-for-millions-with-limited-credit-history-thanks-to-vantagescore-4-0-vantagescore-in-forbes)
- [First Heritage Mortgage — VantageScore 4.0 vs FICO 10](https://fhmtg.com/2025/08/14/what-are-the-differences-between-vantagescore-vs-fico-credit-scoring-models/)
- [Fannie Mae — November 2025 VantageScore Disclosure Enhancements](https://capitalmarkets.fanniemae.com/mortgage-backed-securities/single-family-mbs/november-2025-disclosure-enhancements-vantagescore)
- [Algopix — eBay DSR Definition](https://algopix.com/glossary/ebay-dsr)
- [Auction Nudge — eBay Seller Rating System](https://www.auctionnudge.com/guides/the-lowdown-on-ebays-seller-rating-system/)
- [eBay September 2025 Seller Update](https://www.valueaddedresource.net/ebay-us-august-2025-seller-update/)
- [eBay New Feedback Removal Policy](https://www.valueaddedresource.net/ebay-new-feedback-removal-policy/)
- [3Dsellers — eBay Feedback Stars](https://www.3dsellers.com/blog/understanding-ebay-feedback-stars-ebay-feedback-score)
- [AirDNA — Airbnb Ratings Guide](https://www.airdna.co/blog/hosts-guide-to-airbnb-ratings)
- [Awning — Airbnb 2025 System Updates](https://awning.com/post/airbnb-system-updates)
- [RentalScaleUp — Airbnb Highlight System 2025](https://www.rentalscaleup.com/airbnb-highlight-system-top-1-percent-guest-favorite-2025/)
- [Triad Vacation Rentals — Airbnb Algorithm 2025](https://triadvacationrentals.com/blog/airbnb-algorithm-and-how-to-rank-higher)
- [Uber — How Ratings Work](https://www.uber.com/ca/en/drive/basics/how-ratings-work/)
- [Uber Newsroom — A Peek Into Your Rating](https://www.uber.com/newsroom/rider-ratings-breakdown/)
- [Uber Blog — Metric Standardization (uMetric)](https://www.uber.com/blog/umetric/)
- [Stanford Report — Uber Ratings Research August 2025](https://news.stanford.edu/stories/2025/08/uber-ride-sharing-quality-control-ratings-incentive-system-research)
- [PeerTrust Formula (NUS)](https://www.comp.nus.edu.sg/~cs6203/guidelines/topic7/peer-trust.pdf)
- [PeerTrust — ResearchGate](https://www.researchgate.net/publication/3297318_PeerTrust_Supporting_Reputation-Based_Trust_for_Peer-to-Peer_Electronic_Communities)
- [Beta-PT — PLOS One 2024 (BR-PBFT)](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0336039)
- [SecurityScorecard — 10 Risk Factors Explained](https://securityscorecard.com/blog/securityscorecard-10-risk-factors-explained/)
- [SecurityScorecard — Scoring Recalibration October 2025](https://support.securityscorecard.com/hc/en-us/articles/40187012005275-Scoring-Recalibration-October-21-2025)
- [SecurityScorecard — Scoring Recalibration February 2026](https://support.securityscorecard.com/hc/en-us/articles/44219572850587-Upcoming-scoring-recalibration-February-18-2026)
- [SecurityScorecard — Prepare for Scoring 3.0](https://support.securityscorecard.com/hc/en-us/articles/16235105523739-Prepare-for-Scoring-3-0)
- [SecurityScorecard — ML and Scoring Correlation](https://securityscorecard.com/wp-content/uploads/2024/01/Applying-Machine-Learning-to-Optimize-the-Correlation-of-SecurityScorecard-Scores-with-Relative-Likelihood-of-Breach.pdf)
- [ISO FSRS Overview — Verisk](https://www.isomitigation.com/ppc/fsrs/)
- [ISO Fire Protection Ratings and Insurance — Federato](https://www.federato.ai/library/post/how-iso-fire-protection-ratings-drive-optimal-insurance-pricing)
- [Moody's Financial Institutions Rating Methodology (April 2024)](https://ratings.moodys.com/api/rmc-documents/418351)
- [Qualys TruRisk — Data-Driven Science Blog](https://blog.qualys.com/qualys-insights/2022/10/10/in-depth-look-into-data-driven-science-behind-qualys-trurisk)
- [Qualys — Calculating Asset Risk Score](https://docs.qualys.com/en/vmdr/latest/mergedProjects/prioritize_your_vulnerabilities/threat/calculating_asset_risk_score.htm)
- [Qualys VMDR Advantage Blog 2025](https://blog.qualys.com/product-tech/2025/02/24/from-vulnerability-scanning-to-risk-management-the-complete-vmdr-advantage)
