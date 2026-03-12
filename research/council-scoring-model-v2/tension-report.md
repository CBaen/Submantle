# Tension Report: Scoring Model V2 — Weights and Measures
## Date: 2026-03-12
## Author: Tension Analyst (Opus 4.6)
## Subject: The deliberation itself — Council agents: Codebase Analyst (CA), External Researcher (ER), Devil's Advocate (DA)

---

## Prefatory Note

This report does not evaluate the scoring model design. It evaluates the council's own reasoning — the gap between what agents scored and what they decided, where agreement was real versus performed, and what the tensions in those numbers reveal about what each agent actually valued. Every claim below references specific scores and specific decisions. Interpretations are marked as such.

---

## Section 1: Individual Score-Decision Alignment

### 1.1 Codebase Analyst — Scores Support Conclusions, But a Hidden Weighting Is Revealed

The CA's scores across role-specific dimensions:
- Feasibility: 8/10
- Blast Radius: 7/10
- Pattern Consistency: 8/10
- Dependency Risk: 7/10
- Overall Risk: 7/10
- Reversibility: 6/10
- Evidence Confidence: 9/10

The CA recommends proceeding with the weighted scoring model. These scores, taken together, read as a recommendation to proceed — no dimension is below 6/10, and the 9/10 Evidence Confidence anchors the overall posture. This is score-decision alignment.

**But the CA's recommendation is actually more conservative than these scores imply.** The CA's "key divergences where I hold my ground" in the challenge round includes: "Reporter credibility in the V1 formula is not feasible — 8 prerequisite steps." The Feasibility score of 8/10 is for *the whole proposal's architecture*, but the CA's actual recommendation only endorses Steps 1-6 of the 10-step dependency chain — explicitly pushing reporter credibility to V2.

**The observable weighting:** The CA's Dependency Risk (7/10) was the dimension doing the most work in their recommendation. Despite 8/10 Feasibility, the CA's primary contribution to the council was the dependency chain that sequenced when different components become feasible. The Feasibility score describes structural readiness; the Dependency Risk score reflects that readiness is conditional. The CA's recommendation is shaped more by the 7/10 Dependency Risk than the 8/10 Feasibility — but Dependency Risk is scored higher (better), not lower, which makes its influence on the CA's conservatism invisible from the score alone.

**Interpretation:** The CA's scores do not reveal the "build Steps 1-6 first, evaluate later" recommendation that is the CA's actual value-add. A reader looking only at the 8/10 Feasibility score would expect a more aggressive "ship it" recommendation than the CA actually gives. The conservatism is embedded in the structure of the dependency chain, not in any individual score.

**One genuine score-decision tension:** The CA scores Reversibility at 6/10 — noting "reverting requires restoring the counter-based path AND ensuring the counter matches reality" and "range is 3/10 (soft-delete) to 9/10 (adding trust_metadata enrichment only)." A Reversibility range spanning 3/10 to 9/10 collapses into a single 6/10 average, which obscures that the CA is simultaneously endorsing one highly reversible change (trust_metadata enrichment) and one barely reversible change (soft-delete). The council's final recommendation to proceed includes both — the 6/10 average score performs a quiet risk-averaging that makes the irreversible soft-delete change look more acceptable than it would appear at its own 3/10 raw rating.

---

### 1.2 External Researcher — Two Self-Reversals Reveal What the ER Actually Weighted

The ER scored approaches differently from the other two agents, producing per-approach risk ratings rather than per-dimension scores. For shared dimensions, the ER noted scores "vary by approach." This makes direct comparison harder, but the ER's challenge round self-reversals are more analytically useful than their Phase 1 scores.

**Self-Reversal 1:** The ER placed reporter credibility weighting in "V1 ship requirement (Layer 2)" in Phase 1. After reading the CA's dependency chain showing 8 prerequisites, the ER explicitly revised this to "V2 / Go rewrite."

What the reversal reveals: the ER's Phase 1 position was grounded in external analogs (PeerTrust, D&B) without checking whether Submantle's codebase had the infrastructure to support the pattern. The ER explicitly acknowledges this in the challenge round: "The Codebase Analyst's error is reasoning from analogy without checking what infrastructure would need to exist." The ER had made exactly this error in Phase 1. The reversal is not a minor adjustment — it changes the ER's V1 scope recommendation fundamentally. **The ER's Phase 1 evidence confidence was implicitly ~8/10 (high-quality external citations, multiple precedents per claim) but their recommendation was built on external analogy without internal verification.** The gap between evidence quality and recommendation validity is the ER's primary weakness as a council member.

**Self-Reversal 2:** The ER endorsed severity as a formula weight (1.0/0.7/0.3) in Phase 1 ("Approach D: Severity-Weighted Incident Accumulation"). After reading the DA's challenge, the ER "partially reversed" this position, adopting severity-as-routing for V1. The ER's own words: "Before reading this, my Phase 1 findings fully embraced severity as a formula_weight modifier. After reading the Devil's Advocate's challenge, I find the processing-path-only argument stronger than I would have predicted."

**What the self-reversals reveal together:** The ER's Phase 1 recommendations were built around what external systems have done. The ER's Phase 2 revisions were driven by what Submantle's codebase can currently support. This suggests the ER weighted external analogy heavily in Phase 1 and implementation feasibility heavily in Phase 2 — but both should have been weighted simultaneously. The ER's most valuable Phase 1 contribution was the external evidence; the ER's least reliable Phase 1 contribution was the V1 scope judgment.

**Interpretation:** The ER's two self-reversals are high-quality signals, not failures. The fact that the ER revised rather than defended reveals genuine responsiveness to disconfirming evidence. But the reversals also expose that the ER's initial recommendations overshot — the ER recommended complexity that the CA's infrastructure audit disproved. The ER's scoring on individual approaches (e.g., Approach D rated as "low effort") was not grounded in blast radius analysis. The CA's challenge correctly identified this: "low effort" for the formula line is different from "low effort" for the full state machine prerequisite.

---

### 1.3 Devil's Advocate — The Score Structure Is Inverted; The Most Valuable Work Is in What the DA Could Not Disprove

The DA's scores:
- Failure Probability: 4/10 (higher = worse; so this means "likely to fail")
- Failure Severity: 5/10 (medium)
- Assumption Fragility: 3/10 (low = fragile; so this means "assumptions are fragile")
- Hidden Complexity: 4/10
- Overall Risk: 4/10 (using the same scale — i.e., high risk)
- Reversibility: 6/10
- Evidence Confidence: 7/10

These scores, on a "higher is worse" scale for most dimensions, represent a strongly negative assessment of the proposal. The DA rates the proposal as likely to fail, as having fragile assumptions, as hiding significant complexity. And yet the DA's "What I Could Not Disprove" section is a pivotal positive contribution to the council — it validates four major design choices that survived adversarial scrutiny.

**This is the most significant individual score-decision tension in the entire council.** The DA's scores read as "this proposal has serious problems." But the DA's "Could Not Disprove" findings amount to: "the core architecture is sound, the five-state incident workflow is well-grounded, and recording interaction types without weighting is correct." The DA's recommendation is not "reject this proposal" — it is "build Steps 1-6, defer reporter credibility to V2, address the risks I've identified."

**What explains the gap?** The DA was scoring "the proposal as stated" — including reporter credibility weighting as a V1 feature, severity as formula weight, and all the unresolved bootstrapping problems. When those components are removed (which the challenge round produced), the DA's own risk assessment drops substantially. The post-challenge score revision confirms this: the DA split Failure Probability from 4/10 (whole proposal) into "severity weighting 8/10 likely to succeed; reporter credibility 2/10 near-certain to fail as specified." This is not a small adjustment — it is the DA acknowledging that the proposal contained two fundamentally different risk profiles, and the original 4/10 was averaging them.

**Interpretation:** The DA's Phase 1 scores reflect what the proposal included, not what the council ultimately decided to do. The DA's adversarial function did exactly what it was designed to do: by scoring the full proposal harshly, the DA forced the council to separate the low-risk components (severity routing, trust_metadata enrichment) from the high-risk ones (reporter credibility formula integration). The 4/10 overall risk score produced the right outcome — not by being accurate about the final design, but by being accurate about the risks embedded in the original proposal, which the council then stripped out.

**A secondary tension:** The DA scored Evidence Confidence at 7/10, lower than the CA's 9/10. The DA's evidence was strong (FICO fragmentation well-documented, eBay inflation in academic literature, EU AI Act gap grounded in regulatory text). The 7/10 vs. 9/10 difference appears to reflect the DA's more conservative posture about using regulatory risk claims (the EU AI Act concern was "grounded in a gap," not in a ruling), while the CA's 9/10 was grounded in line-verified code. These are genuinely different evidence types — the lower DA score is probably appropriate — but the spread is worth noting because the DA's EU AI Act concern is a qualitatively different kind of evidence from the CA's "line 338 confirmed by Grep."

---

## Section 2: Cross-Agent Score Comparison — Shared Dimensions

Three dimensions were scored by both the CA and DA (the ER used per-approach scoring). These are the primary quantitative comparison points.

### 2.1 Overall Risk

| Agent | Score | Scale Convention |
|-------|-------|-----------------|
| Codebase Analyst | 7/10 | Higher = lower risk (favorable) |
| Devil's Advocate | 4/10 | Appears to use: lower = higher risk (same as CA convention, but the DA's justification reads as "this is risky") |
| External Researcher | Varies by approach | Not directly comparable |

**Spread: 3 points.** This meets the threshold for "genuine disagreement."

The CA's 7/10 Overall Risk means: "manageable risk, the architecture supports it, the test surface is contained." The DA's 4/10 Overall Risk (if using the same scale convention) means: "high risk, the mechanisms are underspecified in dangerous ways." These are not close positions.

**What explains the gap?** The CA scored overall risk on the technical implementation — blast radius, test coverage, formula isolation. The DA scored overall risk on the design specification — unresolved bootstrapping, two sources of truth, float-in-integer formula, EU AI Act. Both agents were scoring "the proposal" but they were scoring different dimensions of "risk" without explicitly declaring their scope. The CA's 7/10 is about "can we build this safely?" The DA's 4/10 is about "will the thing we build do what we intend?"

**Post-challenge synthesis resolution:** The synthesis splits this difference at 7/10 in the Master Score Table, with a note that "DA's counter about API data integrity and soft-delete naming collision are valid deductions." The synthesis chose the CA's framing (technical feasibility) as the primary lens for "Overall Risk" — but this is itself a choice about what counts as risk, not a resolution of the genuine disagreement. The DA's concerns were addressed by removing the risky components from V1 scope, not by scoring them lower. **The 7/10 in the synthesis represents the proposal after it was modified by the DA's critique, not the same proposal the DA scored at 4/10.**

### 2.2 Reversibility

| Agent | Score |
|-------|-------|
| Codebase Analyst | 6/10 |
| Devil's Advocate | 6/10 |
| Spread | 0 |

**Exact agreement at 6/10.** This appears to be genuine convergence — but the justifications reveal different reasoning.

The CA's 6/10: "New schema columns with defaults are easy to add... but once compute_trust() reads from incident_reports WHERE status='accepted' instead of the aggregate counter, reverting requires restoring the counter-based path AND ensuring the counter matches reality. Range is 3/10 (soft-delete) to 9/10 (adding trust_metadata enrichment only)."

The DA's 6/10: "Recording interaction types without weighting is fully reversible. Adding formula_weight to incident_reports is a schema change that can be added without breaking existing scores. The hard-to-reverse element is embedding reporter credibility weighting into the formula: once reporters have credibility scores, changing the weighting formula retroactively reweights all historical incidents."

Both agents score 6/10, but the CA's "hard-to-reverse" case is the formula counter transition, and the DA's "hard-to-reverse" case is reporter credibility in the formula. These are different technical components. **The 6/10 agreement is coincidental — they agree on the number but are evaluating different parts of the proposal as the source of irreversibility.** This produces the correct summary (overall reversibility is moderate) for different reasons, which means the 6/10 agreement does not constitute high-confidence convergence on reversibility. It constitutes low-confidence agreement on a number.

**Interpretation:** Because the DA's hardest-to-reverse element (reporter credibility in formula) was removed from V1 scope during the challenge round, the post-challenge reversibility for the actual V1 design is likely higher than 6/10. The CA's hardest-to-reverse element (soft-delete) remains. The synthesis does not produce an updated Reversibility score for the V1-scoped design, which is an omission.

### 2.3 Evidence Confidence

| Agent | Score |
|-------|-------|
| Codebase Analyst | 9/10 |
| Devil's Advocate | 7/10 |
| Spread | 2 |

**Spread of 2 — normal variation, but the justification gap is wider than the number suggests.**

CA's 9/10: "All claims reference specific file lines, verified by direct file reads and Grep. Test counts verified by running pytest --collect-only. The 'trust_metadata is never written' claim was confirmed by Grep across all .py files. No speculation."

DA's 7/10: "FICO versioning fragmentation is well-documented fact. Reputation inflation in multi-dimensional systems is supported by academic literature and documented eBay/Uber behavior. The EU AI Act legal risk is speculative but grounded in the gap between the Commission's guidance scope and the proposed system's actual mechanism."

Both are accurately self-assessing. The CA's evidence is the highest-confidence category in research: direct code inspection with line-number verification. The DA's evidence is a mix of documented historical fact (FICO, eBay inflation) and reasoned inference from regulatory gap (EU AI Act). The 7/10 reflects that mixture honestly.

**A meta-observation:** The CA's 9/10 evidence confidence is irrelevant to whether the proposal design is correct. The ER's challenge round explicitly noted this: "The Codebase Analyst's scores are exclusively about implementation feasibility... The council should not interpret 'implementation is feasible with high confidence' as 'the dimension design is well-validated.'" The 9/10 evidence confidence for "whether the code can be changed" does not transfer to "whether the change is the right change." The synthesis's evidence quality summary correctly identifies this by giving the CA "highest internal evidence quality" and the ER "highest external evidence quality" — two different validity claims.

---

## Section 3: Score-Decision Tension Map

### 3.1 Severity as Formula Weight — High Scores, Rejected Anyway

The ER's Phase 1 scored Approach D (Severity-Weighted Incident Accumulation) as the recommended primary approach, citing D&B PAYDEX precedent, SecurityScorecard issue-type weighting, and the existing `formula_weight` column in Team 3's schema. The ER described this as "low effort" and gave it an implicit high score on feasibility and external validation.

The council ultimately rejected severity as formula weight for V1.

**What overrode the ER's favorable assessment?** Two sources:
1. The DA's mathematical challenge: float `i` changes the Beta distribution's theoretical properties. The DA scores this as Failure Severity 5/10 (medium).
2. The ER's own reversal: "Severity as a routing mechanism... is cleaner than severity as a formula weight. The formula weight approach introduces the float-in-Beta problem and requires calibrating weights without outcome data."

**The invisible criterion that isn't captured in scoring dimensions:** The decision hinged on theoretical integrity — whether the formula could still claim to be "the mean of Beta(alpha, beta)" after float inputs were introduced. No scoring dimension explicitly captures "theoretical integrity of the formula's documented derivation." The DA's concern was labeled as Failure Severity 5/10, which is medium — not a catastrophically high score. But the council treated it as decisive.

**Interpretation:** The rejection of severity-as-formula-weight reveals that theoretical integrity was weighted heavily by the council — more heavily than the scoring dimensions make visible. The DA's "float breaks Beta derivation" concern received a 5/10 severity score, which in isolation would not clearly dominate a set of favorable scores from the ER. What made it decisive was the combination of: (a) no outcome data to calibrate the weights anyway, and (b) the routing approach achieves the same priority-processing benefit without touching the formula. The second reason is a cost-benefit argument, not a risk argument. The council correctly noted it, but it does not appear in any scoring dimension.

### 3.2 Reporter Credibility — Recommended in Phase 1, Rejected for V1

The ER recommended reporter credibility weighting as a V1 ship requirement in Phase 1. The ER cited PeerTrust Cr(v), D&B precedent, and rated reporter credibility positively across multiple approach dimensions.

The council rejected reporter credibility for V1. After the challenge round, all three agents converged on V2/Go rewrite.

**The divergent scores that produced consensus rejection:**
- CA: Not explicitly scored, but flagged as "near-certain to fail as specified" with 8 prerequisite steps
- DA: Bootstrapping risk rated HIGH (Phase 1), then revised to MEDIUM after D&B diversity alternative surfaced
- ER: Self-reversed from "V1 ship requirement" to "V2"

This is a case of **divergent scores producing consensus rejection through different reasoning chains**. The CA rejected reporter credibility because the infrastructure doesn't exist (implementation-feasibility argument). The DA rejected it because bootstrapping is unresolved (design-correctness argument). The ER reversed because the codebase dependency chain made V1 infeasible (a combination of both).

**What makes this tension interesting:** The DA's final risk rating for bootstrapping dropped from HIGH to MEDIUM after the challenge round. MEDIUM risk, in isolation, does not typically produce outright rejection. The DA even acknowledged: "This partially resolves the bootstrapping problem I raised in Phase 1." But reporter credibility was still rejected. The resolution came not from resolving the risks but from finding that the D&B `reporter_diversity` approach sidesteps them entirely — surface the count, let brands decide. This is a classic move: reject the risky solution by finding an alternative that achieves the practical goal with lower risk, rather than lowering the risk assessment of the original solution.

**The synthesis framing of this rejection** reads: "All three agents converged after the challenge round." This is technically true but obscures that the convergence was not symmetric — the CA never endorsed reporter credibility for V1, the DA opposed it from the start, and the ER reversed a Phase 1 recommendation. "Convergence" here describes the endpoint, not the path. The path was: two agents opposed it, one reversed under the weight of their peers' evidence.

### 3.3 Two-Sources-of-Truth — CA MEDIUM, DA HIGH, Synthesized as "MEDIUM with Mandatory Fix"

The DA labeled the two-sources-of-truth incident count problem as HIGH risk in Phase 1. The CA challenged this and labeled it MEDIUM, arguing the test suite catches divergence immediately.

The synthesis rates it as "MEDIUM, with a mandatory fix" — closer to the CA's position.

**The score gap: CA MEDIUM vs DA HIGH.** The DA's argument: even if the test suite catches divergence, the API response will show `incidents: 5` (counter-based, including pending) while the score reflects 3 accepted incidents. This API inconsistency is a data integrity problem that will confuse brand integrations. The CA's argument: the COALESCE approach handles the formula; the counter becomes a cache.

**What the synthesis resolved:** The synthesis sided with the CA's risk rating (MEDIUM) but incorporated the DA's concern by adding: "The API response must also change. If the API returns incidents: 5 (from the counter, including pending) but the score reflects only 3 accepted incidents, brands see inconsistent data." The synthesis accepted the DA's mechanism while rejecting the DA's severity rating.

**Interpretation:** The CA's 7/10 Dependency Risk score (from Phase 1) understated this specific risk because the CA's concern was sequencing (pending state before formula change), not API surface consistency. The DA surfaced a genuinely new concern — the API response field name `incidents` would mislead brands even after the formula transition. This was not a risk the CA's dependency chain addressed. The synthesis incorporated it not by raising the risk rating but by adding a mandatory fix. This is a third category of tension resolution: accept the mechanism of the concern while rejecting its severity, and address it through implementation specification rather than risk escalation.

### 3.4 Score Inertia — Evidence Identifies It, No Score Dimension Captures It, Synthesis Rates It MEDIUM

The ER's challenge round introduced score inertia: an agent with q=5000, i=0 that gets compromised would barely show score impact from 50 new incidents (score: 0.999 → 0.990). The ER calculated this explicitly. Neither the CA nor the DA scored this risk in Phase 1.

The synthesis rates it MEDIUM and defers mitigation to V2.

**The tension:** This is a failure mode that all three agents acknowledged as real, that the council explicitly did not design around, and that the synthesis accepted as a known limitation. No Phase 1 scoring dimension captured it. The DA's Phase 1 Failure Severity of 5/10 was for the float-in-formula problem, not score inertia. The council produced a design decision (defer to V2) without a supporting score — the score inertia risk is assessed as MEDIUM by fiat, not by independent dimension scoring.

**What this reveals:** The scoring framework used by this council was not designed to capture emergent risks discovered during the challenge round. The three shared dimensions (Overall Risk, Reversibility, Evidence Confidence) were scored in Phase 1. Score inertia was not identified until Phase 2. The synthesis had to rate it without a scoring foundation — MEDIUM is the synthesis orchestrator's judgment, not an aggregated agent assessment. This is not a failure of the scoring framework; it is a structural limitation of phase-based scoring.

---

## Section 4: Observable Weighting Analysis

### 4.1 What Each Agent's Recommendation Reveals About What They Weighted

**Codebase Analyst:** The CA's recommendation is conservative relative to their scores. Despite 8/10 Feasibility, the CA's primary output is a 10-step dependency chain that sequences implementation. This reveals that the CA weighted sequencing discipline over raw feasibility. The observable evidence: the CA explicitly pushes back on the ER's "low effort" assessment of Approach D, noting that the state machine prerequisites are "medium effort" and must exist before the formula change is safe to deploy. The CA's highest-weighted dimension was not captured in any of their scores — it was implementation sequencing, which appears only in the Appendix dependency chain.

**External Researcher:** The ER's Phase 1 recommendation was more aggressive than the other two agents'. Despite acknowledging the bootstrapping problem as an "open gap," the ER still placed reporter credibility in V1. This reveals that the ER weighted external analogy proof-of-concept (PeerTrust works in the literature) over internal infrastructure readiness. After the challenge round, the ER's self-reversals show that internal infrastructure evidence was weighted at zero in Phase 1 and heavily after seeing the CA's codebase analysis. The ER's most important dimension — implementation readiness — was not scored in Phase 1 because it is the CA's domain.

**Devil's Advocate:** The DA's recommendation is striking: despite scores that read as a strongly negative assessment (4/10 overall risk, 3/10 assumption fragility, 4/10 failure probability), the DA never recommended rejecting the proposal outright. The DA's "What I Could Not Disprove" section validated the two-track architecture, the five-state incident workflow, and the record-now/weight-later approach. This reveals that the DA weighted structural soundness over component-level risk. The observable evidence: the DA called the Codebase Analyst's dependency chain "the most structurally valuable finding in this council" and explicitly credited it for turning a binary debate into "build Steps 1-6 first, evaluate when real reporters exist." The DA's adversarial scores applied to the full proposal, but the DA's recommendation was to strip the risky components — which is a constructive posture, not a pure adversarial one.

### 4.2 Dimensions Scored But Apparently Not Weighted in Final Recommendation

**DA's Failure Severity (5/10 for float-in-formula):** This score describes the float-in-Beta problem as "medium-high severity: not catastrophic but silently incorrect." The synthesis resolved this risk not by accepting it (which a 5/10 might imply) but by designing it away entirely — severity-as-routing preserves integer parameters. The 5/10 score did not appear to influence the decision; instead, the existence of a score-free solution made the score irrelevant.

**DA's Assumption Fragility (3/10):** The DA rated 5 of 8 assumptions as unverified. The synthesis's treatment of this is indirect — the Post-Challenge Score Adjustments table shows the ER revised DA's assessment of three assumptions to "partially verified" or "verified." But the assumption fragility score itself (3/10) does not appear in the synthesis's risk summary or implementation sequence. The assumptions were addressed not by raising confidence in them but by removing the assumptions that mattered (reporter credibility from V1 scope). The score was bypassed by scope change.

**CA's Blast Radius (7/10):** This score describes how many files and tests change. It appears in the synthesis only in the implementation plan, not in the risk section. The CA's specific finding — 10 of 187 tests will break — is treated as a implementation planning detail, not a risk signal. A 7/10 Blast Radius (relatively high) does not appear to have influenced the council's recommendation at all. This is appropriate: high blast radius in tests is not a reason to change the design decision; it is a reason to plan the implementation carefully. But it is worth noting that this scored dimension had essentially no influence on the council's direction.

---

## Section 5: Confidence Calibration

### 5.1 Cases Where Agents Were More Confident Than Evidence Warranted

**ER Phase 1 confidence on V1 scope for reporter credibility:** The ER cited PeerTrust, D&B, and Beta-PT as evidence for a bootstrapping solution. The confidence level was high enough to include reporter credibility in "V1 ship requirement (Layer 2)." But the evidence was about the existence of the mechanism in the literature, not about whether Submantle had the infrastructure to implement it. The ER was highly confident that the mechanism was correct; the ER was wrong that this made it V1-feasible. The evidence quality was high on the wrong question.

**DA Phase 1 confidence on HIGH risk for two-sources-of-truth:** The DA labeled this HIGH risk with clear reasoning. The CA challenged it and argued MEDIUM (test suite catches it immediately). The DA's Phase 2 response did not fully concede this point — the DA held that the API response inconsistency remains a data integrity problem. But the synthesis rated it MEDIUM. The DA was more confident in the severity than the evidence (specifically, the strength of the test-suite safety net) warranted. This is the DA's function — adversarial analysts are expected to flag risks conservatively. But the DA did not explicitly acknowledge this calibration limitation.

### 5.2 Cases Where Agents Were Less Confident Than Evidence Warranted

**CA's Reversibility score (6/10, range 3/10 to 9/10):** The CA provided a range of 3/10 to 9/10, then reported 6/10 as the summary. This is statistically reasonable (midpoint of range) but it understates the CA's own evidence. The CA's codebase evidence shows that trust_metadata enrichment (no schema changes) is clearly 9/10 reversible, and soft-delete (breaks 4 tests, SQLite uniqueness problem, semantic change to credit bureau model) is closer to 3/10. A score that averages these is less confident about both extremes than the evidence supports. The CA could have scored trust_metadata enrichment separately from soft-delete and provided cleaner guidance to the council. By averaging into 6/10, the CA's evidence confidence (9/10) did not translate into scoring precision.

**DA's "What I Could Not Disprove" section:** The DA identified five design elements they could not disprove, including the five-state incident workflow and server-side deduplication. These are strong positive signals — adversarial review that found no failure mode is higher-confidence support than affirmative review. But the DA did not translate these findings into score adjustments. The "What I Could Not Disprove" findings support higher scores on Assumption Fragility (fewer unverified assumptions) and lower Failure Probability (the things that survived scrutiny are likely sound), but those scores were not adjusted. The DA's adversarial validation produced strong evidence that was not incorporated into the scoring.

### 5.3 The Most Significant Calibration Gap in the Council

**The ER's Phase 1 evidence confidence (implicit ~8/10 based on quality of citations) vs. the reliability of their V1 scope recommendations:** The ER produced the strongest external evidence of any council member — specific systems, dates, documented behavior patterns. But two of the ER's primary recommendations were reversed in the challenge round (reporter credibility to V2, severity from formula weight to routing). The quality of the evidence was high; the translation from evidence to recommendation was poor.

This is a specific calibration failure: the ER was highly confident in the external analogs (appropriate confidence) but also highly confident that those analogs justified V1 recommendations (overcalibrated confidence in the inference from evidence to recommendation). Evidence about what D&B does is not evidence about what Submantle can do in V1. The ER conflated these, and the self-reversals are the record of that conflation being corrected.

---

## Section 6: Specific Tensions the Synthesis Left Unresolved

### 6.1 The API Response `incidents` Field Name Conflict

The DA raised a specific mechanism: after the formula transition, the API response will contain `incidents: N` (from the counter, including pending) while the score reflects only accepted incidents. The synthesis addresses this by replacing `incidents` with `accepted_incidents` and `pending_incidents` in the API response spec.

**The unresolved tension:** The synthesis Master Score Table shows "CA Two-sources-of-truth: MEDIUM (test suite catches it)" in the Post-Challenge Score Adjustments. But the DA's challenge round analysis argued that even after the formula transition, if the counter and the table diverge, every brand integration reading both `incidents` and `trust_score` will see inconsistent data. The test suite catches developer-side divergence, not API consumer confusion.

**What remains unresolved:** Is the two-sources-of-truth a MEDIUM risk (CA's framing, mitigated by tests) or a data integrity problem (DA's framing, requiring API response redesign)? The synthesis incorporated the DA's fix (API response change) while accepting the CA's risk rating (MEDIUM). This is synthesis success on the practical level but leaves the risk evaluation unresolved — the synthesis adopted the DA's remedy without upgrading the DA's risk assessment.

### 6.2 Severity Classification as Processing Path — Two Different Justifications That Are Not Equivalent

The synthesis states that severity as routing was adopted because: (a) float `i` breaks the Beta distribution's theoretical grounding (DA's argument), and (b) no outcome data to calibrate weights yet (ER's partial reversal argument).

**These are different arguments with different implications.** The DA's argument is permanent: float inputs corrupt the theoretical grounding regardless of data availability. The ER's argument is temporary: severity as formula weight is deferred until calibration data exists. The V2 section of the synthesis states: "When outcome data validates calibration, severity can move from processing-path-only to formula weight. The formula_weight column ships in V1 schema (defaulting to 1.0) for V2 readiness."

**The unresolved tension:** If the DA's argument is correct (float inputs corrupt the theoretical derivation), then the `formula_weight` column shipping in V1 schema for "V2 readiness" is preparing for a change that the DA argues should never happen — or at minimum, requires a deliberate decision to stop calling the formula "the mean of Beta(alpha, beta)." The synthesis does not resolve whether V2 severity weighting would require abandoning the Beta distribution label. It defers the decision by saying "deferred to V2," but the DA's argument applies to V2 as much as V1.

The synthesis implicitly adopted the ER's "temporary" framing (defer until calibration data exists) while the DA's argument is structural (changing the formula's mathematical grounding cannot be undone by having more data). These two framings produce the same V1 decision but incompatible V2 expectations.

### 6.3 Soft-Delete Naming Collision — Credit Bureau Model vs Prior Council Recommendation

The synthesis states: "Deregistered agent names are permanent records. Re-registration with the same name under a different key creates a new entity." This is framed as following from D&B's permanent D-U-N-S numbers. The synthesis also states: "This modifies the prior council's recommendation ('re-registration inherits history')."

**The tension:** The prior council's recommendation was non-challengeable (listed in the brief's "Context: What the Prior Council Settled"). The synthesis modified it. The brief states the prior council settled "Deregister must become soft-delete" — it did not specify whether re-registration with the same name was allowed or what happens when it is attempted. The synthesis is reading the prior council settlement as only settling "soft-delete" and interpreting what credit bureau semantics imply about re-registration.

**What the synthesis does not resolve:** The brief's non-challengeable list includes "Deregister must become soft-delete" but does not include "re-registration inherits history" as settled. The External Researcher's Phase 2 finding ("credit bureau model: permanent file... conflict with what the prior council settled") suggests the ER read the prior council as settling re-registration inheritance. The CA's Finding 4 presents three options without declaring a winner, suggesting the CA did not read the prior council as having settled this.

**Whether this constitutes overstepping the brief's constraints** is a question the Tension Analyst observes but does not answer. The synthesis resolved it as a design decision; whether that decision is within scope is for Guiding Light to evaluate.

---

## Summary: The Highest-Signal Tensions

**Tension 1 (Strongest signal):** The ER scored reporter credibility favorably in Phase 1 but reversed to V2 in Phase 2. The reversal is not a sign of weakness — it reveals that the council's Phase 2 process did exactly what it was designed to do: expose over-extension from external evidence to internal scope. The ER's reversal is the council's most important moment of self-correction.

**Tension 2:** The DA scored the full proposal at 4/10 Overall Risk but never recommended rejection. This reveals that adversarial review in this council was not a veto mechanism — it was a scope-narrowing mechanism. The DA's high risk scores on reporter credibility and float-in-formula did not produce "don't build this." They produced "don't build the risky parts first." This is the correct adversarial function, but it means the DA's Phase 1 scores describe a proposal that the council never actually built — the scores and the final recommendation apply to different objects.

**Tension 3:** The CA and DA scored Reversibility identically at 6/10 but for different components. This coincidental agreement obscures that the CA's low-reversibility concern (counter/table transition) was partially mitigated in the synthesis, while the DA's low-reversibility concern (reporter credibility in formula) was removed from scope entirely. The post-challenge reversibility of the V1 design is likely higher than 6/10, but no agent rescored it.

**Tension 4:** The severity-as-routing decision resolved a genuine disagreement (DA for routing vs ER for formula weight) using two incompatible justifications that were treated as equivalent. The DA's argument is structural (float inputs are wrong). The ER's argument is empirical (no calibration data yet). These are both right for V1, but they produce different expectations for V2. The synthesis leaves this unresolved under the "deferred to V2" framing.

**Tension 5:** The DA's "What I Could Not Disprove" findings supported the overall architecture with high adversarial confidence — but these positive findings did not register as score adjustments. The DA's adversarial endorsements may be the most reliable confidence signals in the council, because they survived intentional attack. They should carry higher weight than any affirmative score from the other two agents on the same components. The council's scoring framework does not currently capture "survived adversarial review" as a confidence multiplier.
