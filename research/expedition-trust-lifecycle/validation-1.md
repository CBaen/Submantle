# Validation Report — Trust Lifecycle Expedition
## Date: 2026-03-12
## Validator: Validator 1
## Scope: Teams 1–5 (Status Labels, Sandbox, Review Tiers, Fairness/Recovery, Interaction Metadata)

---

## Divergence-First Protocol — Problems Before Praise

---

## 1. Evidence Challenges

### Team 1 — Status Labels

**Challenge 1.1 — Apple source attribution error.**
Team 1's Section 1.6 cites Google Play's enforcement URL (`support.google.com/googleplay/android-developer/answer/9899234`) twice — once labeled as "Apple App Store enforcement" and once as "Google Play enforcement." These are the same URL. The Apple-specific claims (Resolution Center, "Metadata Rejected" label) cannot be verified from that source. The claims may be accurate, but the sourcing is wrong. Any design decision relying specifically on Apple's label naming needs a correct source.

**Challenge 1.2 — Visa VAMP "3 consecutive months" claim needs verification.**
Team 1 states that VAMP removal requires "3 consecutive months below threshold." The source cited (`ravelin.com/blog/visa-vamp-changes-chargeback-disputes`) is a third-party blog, not Visa's own documentation. The Chargebacks911 source is also a third party. Given the VAMP consolidation was only effective April 2025, this specific exit criterion may be approximated. The claim is plausible but should be labeled as unverified from primary source.

**Challenge 1.3 — W3C Bitstring Status List described as "2025 Recommendation."**
Team 1 calls this a "W3C Recommendation" in Section 1.5. As of March 2026, the W3C Verifiable Credentials Bitstring Status List is a Candidate Recommendation, not a full Recommendation. CLAUDE.md itself specifies "W3C Verifiable Credentials 2.0 + SD-JWT (RFC 9901)" as the attestation format — so citing the Bitstring Status List at all may be forward-looking. The technical claims are accurate in substance, but the maturity characterization is overstated.

**Challenge 1.4 — "25 interactions to exit NEW" threshold is asserted, not derived.**
Team 1 proposes "first 25 interactions" as the threshold for transitioning from NEW to ACTIVE. No source is cited for this number. The Brief asks for defensible design, not arbitrary defaults. Team 2's minimum interaction gate proposal (10 interactions before score publication) directly contradicts Team 1's implied 25-interaction threshold for the same concept. This gap is real and unresolved.

### Team 2 — Sandbox Testing

**Challenge 2.1 — Valorant Level 20 gate claim is unverified.**
Team 2 states Valorant requires "account level 20 before accessing ranked." The cited source (blix.gg, a community site) is not Riot's official documentation. The official Valorant Competitive Mode FAQ is cited but does not appear to contain the Level 20 requirement based on the excerpt provided. This specific gate threshold should not be used as a design justification without verification from Riot's official source.

**Challenge 2.2 — "No competitor offers a developer sandbox" is a negative claim with limited verification.**
Team 2 states in Section 9: "No competitive product was found to offer a developer sandbox for agent behavioral trust testing as of March 2026." This is presented as a competitive opportunity. However, the list reviewed (HUMAN Security, Mnemom, Zenity, Mastercard Verifiable Intent, Google UCP, cheqd) may not be exhaustive. Given the CLAUDE.md describes a 12-18 month competitive window with $450M+ deployed, this claim should be treated as "not found in the products checked" rather than "confirmed does not exist." The competitive opportunity may be real, but the evidence bar is "we didn't find it" not "it doesn't exist."

**Challenge 2.3 — "Separate HMAC secret for sandbox" implementation assumes single-machine key management.**
Team 2 recommends cryptographically separate sandbox and live tokens via a different HMAC secret. This works in a prototype. At production scale (or with any key rotation), having two co-resident secrets creates operational complexity around secret rotation, storage, and potential confusion. The recommendation is sound for V1, but the "this prevents misuse by cryptographic architecture" claim slightly overstates the guarantee — it prevents accidental misuse, not determined misuse by someone with access to both secrets.

### Team 3 — Review Tiers

**Challenge 3.1 — "Critical" severity path bypasses pending state — contradicts a SETTLED DECISION.**
Team 3's severity table includes: "Incident count from single reporter > 10 per agent per 24h → Skip pending → ACCEPTED immediately." The research brief explicitly lists as a SETTLED DECISION: "Incidents enter PENDING state before affecting score — review period required." Skipping pending for any case (even high-volume flooding) contradicts this settled decision. The brief also states "tiered review: automated for clear patterns (10K self-pings), human for ambiguous cases" — automated means automated *review*, not bypassing pending. Team 3 has exceeded its scope by reverting a settled decision.

**Challenge 3.2 — "Reduced weight" incidents (0.5 formula weight) are not compatible with the Beta formula as specified.**
Team 3's severity table introduces fractional incident weights (0.5 for new reporters). The Brief specifies the Beta formula as `trust = (queries + 1) / (queries + incidents + 2)` where `incidents` is a count. Fractional incident weights require either (a) modifying the formula or (b) maintaining a separate weighted-sum counter. The Brief's constraint says "Do NOT redesign the Beta Reputation formula itself." Team 3 did not address whether fractional weights constitute a formula modification. This needs resolution before implementation.

**Challenge 3.3 — eBay seller protection URL is non-production.**
Team 3's source for the reporter velocity cap claim uses `ebaysc.stage.liveplatform.com` — this is a staging/preview URL, not production eBay documentation. Evidence drawn from staging environments can be incomplete, outdated, or inaccurate. The claim itself (eBay proactively restricts high-volume case filers) is credible and appears in other context, but the citation should be flagged.

**Challenge 3.4 — 21-day hard limit with "auto-accepts at 0.5 weight" has the same fractional weight problem as 3.2.**
If disputed incidents auto-accept at "0.5 formula weight," this has the same formula compatibility issue noted above. Additionally, auto-accepting an incident of unknown validity after a timeout is a meaningful policy choice with real consequences for agent trust scores. It is presented as a technical default without surfacing the fairness tension: a legitimate agent who did not dispute in time (through neglect, not guilt) gets half-penalized regardless.

### Team 4 — Fairness / Recovery

**Challenge 4.1 — Rolling window recommendation modifies formula inputs in a way the Brief prohibits.**
Team 4's Recommendation 3 proposes filtering incidents older than 365 days out of the `compute_trust()` formula. The Brief states "Do NOT redesign the Beta Reputation formula itself (research how labels/states interact with it)." A rolling window changes what goes *into* the formula — it changes the effective denominator over time. This is a modification to the formula's input semantics, which is functionally equivalent to redesigning it. Team 4 acknowledges the Brief's constraint but then recommends it anyway without addressing the contradiction.

**Challenge 4.2 — Recovery math table has arithmetic inconsistency.**
Team 4's recovery table states: "1 incident, queries needed to reach 0.8 — ~6 queries." Check: `(7+1)/(7+1+2) = 8/10 = 0.80`. This is correct. But the "~6 queries" label in column 1 says "~6 queries" while the note says 7-8 queries. Minor but should be corrected: 7 queries are needed, not ~6.

**Challenge 4.3 — 365-day window recommendation is unsubstantiated for AI agents.**
Team 4 acknowledges this: "The right duration for AI agents is unknown — there is no empirical data yet." This is an honest admission, but the value is still presented as a firm recommendation rather than a hypothesis requiring validation. Given the competitive window is 12-18 months, an agent that was bad 13 months ago may be indistinguishable from a new bad actor today. The 365-day default deserves more explicit "placeholder — revisit" framing.

**Challenge 4.4 — "Reporter minimum trust: only agents with trust > 0.6 can file reports at full weight" conflicts with a SETTLED DECISION.**
The Brief settles: "Only registered Submantle members can file incident reports." It does not settle a minimum trust threshold for filing. However, Team 4's Recommendation 4 introduces `trust >= 0.7 AND registration_age >= 30 days` for full-weight incidents. This is not flagged as a new unsettled decision — it is presented as a recommendation. Given the Brief says Submantle "analyzes reporter history and agent history to contextualize grievances," this is likely in-scope, but the specific threshold (0.7) is asserted without derivation.

### Team 5 — Interaction Metadata

**Challenge 5.1 — Outcome confirmation window requires bidirectional interaction infrastructure that doesn't exist.**
Team 5 proposes in Section 8 that "both parties must confirm the outcome" for outcome to move from PENDING to confirmed. This is a meaningful new infrastructure requirement — a mutual confirmation protocol. The Brief's current state shows no MCP server yet, no bidirectional interaction logging, no registered brand counterparties. For V1 (solo founder, Python prototype), implementing mutual outcome confirmation is substantial scope. This is not flagged as complexity or deferred — it is presented as a baseline anti-gaming measure.

**Challenge 5.2 — Shannon entropy for diversity detection is presented as "deterministic" but requires a configurable threshold.**
Team 5 proposes using Shannon entropy of the endpoint histogram to detect rotation gaming, with "threshold is a fixed constant." Shannon entropy is deterministic computation, but the threshold that separates "diverse" from "gaming" is not — it requires empirical calibration. Without data on what legitimate agent endpoint distributions look like, the threshold is an unvalidated assumption. This is not a fatal flaw, but framing it as "deterministic" elides the threshold selection problem.

**Challenge 5.3 — `COMPLETED_WITH_INCIDENT` as a formula input creates a timing dependency.**
Team 5 specifies that only `COMPLETED_WITH_INCIDENT` increments `incidents`. But under the pending state design (Teams 1, 3, 4), an incident is only ACCEPTED after review. If the interaction record is created at transaction time but the formula impact only happens after incident acceptance, there is a state synchronization question: does the `outcome` field on an interaction log update when the incident review resolves? This cross-table dependency is not addressed in any team's findings.

---

## 2. Contradictions Between Teams

### Contradiction A — Minimum interaction threshold: 10 vs. 25

**Team 1** (Section 3) proposes 25 interactions before NEW → ACTIVE transition.
**Team 2** (Section 7) proposes 10 interactions before trust score is surfaced to brands.
**Team 4** (Recommendation 2) proposes 10 queries before incidents can affect the formula.

These three thresholds serve different purposes but overlap in concept. No team references the others' thresholds. The practical effect: under Team 1's proposal, an agent is NEW for 25 interactions. Under Team 2's proposal, scores are surfaced at 10. Under Team 4's proposal, incidents don't apply until 10. These can be made coherent, but they are currently three independent assertions with three different numbers for conceptually similar gates.

**Which has stronger evidence:** Team 2's reference to Valorant's level gate and FIDE's 5-rated-opponent minimum provides rationale for a low bar (10) to unlock score surfacing. Team 4's mathematical analysis shows that below 10 queries, single incidents have severe disproportionate impact — supporting 10 as the incident-immunity threshold. Team 1's 25 for NEW → ACTIVE is the least evidenced and should be scrutinized.

### Contradiction B — What happens to "Suspended" agents: Team 1 vs. Team 4

**Team 1** defines SUSPENDED as a formal label that Submantle applies, with reason codes, 90-day reinstatement path, and explicit suspension-to-PROBATIONARY transitions.
**Team 4** (Section 10, status table) includes a note: "*Suspension is not a Submantle action — Submantle never acts. If a brand decides not to serve a probationary agent, that is the brand's enforcement."

These are contradictory. Team 1 designs a SUSPENDED state that Submantle applies. Team 4 says Submantle never applies suspension. The Brief's INVIOLABLE principle is "Submantle never acts. Labels and status are information, not enforcement." This cuts to the core of SUSPENDED: if Submantle applies a SUSPENDED label, is that acting? Team 1 argues labels are information. Team 4 argues Submantle doesn't apply them at all.

**Which has stronger evidence:** The Brief itself lists "Under Review" and "Probationary" as labels Submantle publishes — implying Submantle does apply labels. Team 1's reading is more consistent with the Brief's settled decisions. Team 4's footnote appears to be the outlier and should be corrected. However, the question of whether applying SUSPENDED crosses the "acting" line is a real design tension that deserves explicit resolution.

### Contradiction C — Incident auto-acceptance timing

**Team 3** proposes that disputes auto-accept at "reduced weight 0.5" after 21 days if unresolved.
**Team 4** (Recommendation 6) proposes that a brand's withdrawal removes the incident counter, with no mention of auto-acceptance.
**Team 4** also says (Section — What This Research Does NOT Resolve): "If the reporter doesn't respond to a dispute within N days, the incident is auto-withdrawn."

Team 3: unresolved disputes auto-accept.
Team 4: reporter non-response leads to auto-withdrawal.

These are opposite outcomes for the same scenario (reporter files, agent disputes, reporter goes silent). The FCRA model (Team 3 references it) says if the furnisher doesn't respond, the item must be deleted — supporting auto-withdrawal, not auto-acceptance. Team 4's reading of the FCRA is more accurate. Team 3's auto-acceptance of unresolved disputes contradicts both the FCRA analogy and Team 4's findings.

---

## 3. Alignment Drift

### Drift 3.1 — Team 3's "Critical" severity skipping pending state violates a settled decision.
Already noted in Evidence Challenges 3.1. The Brief says "Incidents enter PENDING state before affecting score — review period required." Team 3's Critical severity path (flood detection) skips this. This is not a gap — it is a direct conflict with a non-challengeable settled decision. The automated tier should automatically accept incidents into PENDING, then auto-transition from PENDING → ACCEPTED (without human review), not skip PENDING entirely.

### Drift 3.2 — Team 4's rolling window recommendation is out of scope.
The Brief says "Do NOT redesign the Beta Reputation formula itself." A rolling window changes what inputs the formula receives over time. Team 4 frames this as a fairness mechanism, which it is — but it also modifies the formula's effective behavior. This belongs in "open decisions for future design" rather than V1 recommendations.

### Drift 3.3 — Team 5's bidirectional outcome confirmation is a V2 feature presented as V1.
The Brief states: "Complexity is the enemy. Solo founder building V1." Bidirectional outcome confirmation requires registered counterparties on both sides, a confirmation window protocol, and handling of timeouts and disputes about the outcome itself. The MCP server is not yet built. This is a sound design principle but premature as a V1 requirement.

---

## 4. Missing Angles

### Gap 4.1 — No team addressed the interaction between sandbox and status labels.
Can a sandbox agent have a status label? What happens if a sandbox agent is graduated to production — does it start as NEW or ACTIVE? Team 1 designed the sandbox as a separate meta-state. Team 2 designed the sandbox architecture. They do not connect. The graduation path from SANDBOX → NEW vs. SANDBOX → ACTIVE is unspecified.

### Gap 4.2 — No team addressed bidirectional trust label asymmetry.
The Brief cites VISION.md's updated "bidirectional trust, Experian model." Team 5 mentions that brand denials generate trust data "for both parties" and that brands carry their own scores. But no team designed what the brand-side label system looks like. The agent-side label system (NEW/ACTIVE/PROBATIONARY etc.) is well-specified. The brand-side label system is absent. If brands carry trust scores, do they also have status labels? What triggers a brand entering UNDER_REVIEW?

### Gap 4.3 — No team connected the reporter trust score to the incident pipeline concretely.
Teams 3 and 4 both mention "reporter trust score" as a countermeasure. But the reporter trust score is not a separate entity — reporters are themselves registered agents with their own Beta scores. No team explicitly confirmed that the existing `compute_trust()` function, applied to the reporter's agent record, is the reporter credibility signal. This is likely the intent, but it is never stated explicitly across any of the five findings.

### Gap 4.4 — No team addressed what happens when Submantle itself makes an error.
If Submantle's automated deduplication misgroups incidents, or if a self-ping detection rule fires incorrectly, how does an agent challenge a Submantle-generated label (as opposed to a reporter-generated one)? The ICANN analogy (server hold vs. client hold) suggests Submantle-applied labels need a separate challenge path from reporter-triggered ones. Team 1 gestures at this with `status_applied_by`, but no team designed the appeal workflow for Submantle-originated actions.

### Gap 4.5 — No team addressed the transition cost to the existing codebase tests.
The Brief notes 160 passing tests. Teams 1, 3, 4, and 5 all propose schema migrations. No team assessed whether any proposed migration would break existing tests. The Brief explicitly says "Don't break them." This is an implementation risk that belongs in the findings.

---

## 5. Agreements — High-Confidence Convergence

The following conclusions appear across three or more teams independently, making them high-confidence:

**Agreement A — Pending state is the single most critical anti-gaming mechanism.**
Teams 1, 3, 4, and 5 all identify this independently. The mathematical case (Team 4: a single incident before any queries drops score to 0.333) is the clearest evidence. This is the most urgent implementation gap in the codebase.

**Agreement B — Labels are information, not enforcement. Brands decide.**
Teams 1, 2, 4, and 5 all confirm this independently across multiple reference systems. The Visa/Mastercard/credit bureau model is unanimous. Submantle's "labels only" principle is validated by every reference class examined.

**Agreement C — Structural separation (not just labeling) is required for sandbox isolation.**
Teams 1 and 2 converge: separate tokens, separate storage, separate secrets. Team 2 provides the Stripe evidence. Team 1 proposes the sandbox meta-state. The principle that labeling alone fails is supported by Stripe's own evolution (test mode → sandboxes).

**Agreement D — Status labels must carry authority provenance.**
Team 1 (EPP client vs. server codes), Team 3 (reviewed_by field), and Team 4 (brand vs. Submantle withdrawal) all independently arrive at the need to know who applied a status. The `status_applied_by` field in Team 1's schema is the right mechanism.

**Agreement E — Interaction ID is the anti-fabrication anchor.**
Teams 3, 4, and 5 all independently converge on the interaction_id as the proof-of-interaction mechanism. eBay's `orderLineItemId` is cited in multiple findings. This is the correct architecture.

**Agreement F — Dual technical/layman interpretation should be generated at write time.**
Teams 1 and 5 converge on this. Team 1 proposes it in the API payload. Team 5 provides the Stripe `seller_message` as the canonical model and specifies write-time generation. Both agree on the mechanism.

**Agreement G — Reporter velocity caps are necessary.**
Teams 1, 3, and 4 all independently propose caps on how many incident reports a single reporter can file against a single agent within a time window. The specific thresholds differ (Team 1: 3 per 7 days; Team 3: 5 per 24 hours) but the mechanism is consistent.

---

## 6. Surprises

**Surprise 6.1 — The Beta formula is MORE forgiving than expected at scale.**
Team 4's math shows that an agent with 100 queries and 5 incidents scores 0.944. This is surprisingly high. The formula's harshness at low query counts is well-documented, but its generosity at scale is equally notable. This has an implication: brands setting trust thresholds at 0.7 or 0.8 may inadvertently exclude only early-stage agents, not genuinely bad actors at scale. The anti-gaming velocity caps are therefore essential — without them, bad actors at scale can maintain high scores indefinitely by volume.

**Surprise 6.2 — No credit bureau offers a sandbox, and this is deliberate.**
Team 2 notes: "There is no sandbox in the credit bureau world because the bureau's value depends on every data point being real." This is a structural insight that the research brief did not fully anticipate. If Submantle's competitive position is as neutral credit bureau infrastructure, there is a philosophical tension in offering a sandbox — it means some of Submantle's data ecosystem is explicitly non-real. The teams resolve this correctly (sandbox is for developer integration testing, not behavioral scoring), but the tension is worth noting as a future positioning question.

**Surprise 6.3 — FCRA auto-withdrawal on non-response is the correct resolution for disputed incidents (contradicting Team 3's auto-acceptance default).**
Team 4's analysis of the FCRA more accurately captures the principle: if the furnisher (reporter) doesn't respond, the item must be deleted. Team 3's proposal to auto-accept unresolved disputes after 21 days inverts this principle. The surprise is that the more legally grounded reading (Team 4) is the less punitive one — and it is the right default.

---

## Summary Scorecard

| Team | Evidence Quality | Alignment with Brief | Internal Consistency | Critical Issues |
|------|-----------------|---------------------|---------------------|----------------|
| Team 1 | Strong (minor sourcing errors) | Good | Good | Source mis-attribution (Apple/Google URL); 25-interaction threshold ungrounded |
| Team 2 | Strong | Good | Good | Valorant Level 20 unverified; "no competitor" is under-evidenced |
| Team 3 | Strong | **Partial violation** | Moderate | Critical severity bypasses pending (violates settled decision); fractional weights need formula resolution |
| Team 4 | Strong | **Partial violation** | Good | Rolling window recommendation contradicts "don't redesign formula" constraint |
| Team 5 | Strong | Good (scope creep on bidirectional confirmation) | Good | Mutual outcome confirmation is V2 complexity framed as V1 baseline |

---

## Recommended Actions Before Implementation

1. **Resolve immediately (blocks implementation):** Clarify whether Team 3's "Critical severity → skip pending" path is permissible under the settled pending state decision. It is not, as written. The correct reading: automated review still lands in PENDING → auto-ACCEPTED, not PENDING-bypassed.

2. **Resolve immediately (formula integrity):** Team 3 and 4's fractional incident weights (0.5) need explicit formula treatment. Either (a) maintain a separate weighted-incidents counter alongside the integer counter, or (b) define this as out of scope for V1. Do not implement without settling this.

3. **Resolve before V1 schema migration:** Align the three minimum-interaction thresholds (Team 1: 25, Team 2: 10, Team 4: 10) into a single consistent number with a single justification. Recommend: 10, per Teams 2 and 4's mathematical and precedent-based evidence.

4. **Defer to V1.5:** Team 5's mutual outcome confirmation, Team 4's rolling window, and Team 4's score trajectory snapshots. All are sound design but add complexity a solo founder should not carry in V1.

5. **Design gap to fill:** Brand-side label system (Gap 4.2). Not needed for V1 but should be acknowledged as an open design decision before MCP server launch, since brands will be interacting through MCP.
