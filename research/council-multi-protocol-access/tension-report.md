# Tension Report: Multi-Protocol Access Strategy Council
## Date: 2026-03-12
## Author: Tension Analyst (Opus 4.6)
## Subject: The deliberation itself

---

## Prefatory Note

This document does not evaluate Submantle's multi-protocol strategy. It evaluates how three council members reasoned, scored, and decided — and where those activities diverged from each other. The subject is the council, not the protocol question.

The most important tensions in this deliberation are not between agents who disagree. They are between agents who agree on a conclusion but produce contradictory scores to support it — and between an agent whose scores, read carefully, do not support the recommendation they gave.

---

## Section 1: Individual Score-Decision Alignment

### Codebase Analyst (CA)

**Scores:** Feasibility 9, Blast Radius 9, Pattern Consistency 9, Dependency Risk 9, Overall Risk 9, Reversibility 10, Evidence Confidence 10.

**Recommendation:** REST + MCP via fastapi-mcp.

**Alignment assessment:** Perfect — with a structural problem underneath.

Every score CA produced runs 9-10. The recommendation follows logically from near-perfect scores. But this uniformity is itself a signal worth examining. CA grounded every score in specific line numbers and verifiable codebase facts. This is methodologically disciplined and produces high-confidence scores — for the domain CA examined.

The problem is that CA defined "Overall Risk" as "risk to existing code." CA stated this explicitly: "Overall Risk 9 — the core business logic is already decoupled from the transport layer... adding new files, not modifying load-bearing ones." This is a valid and useful answer to a risk question. It is not the only valid risk question. When DA later challenged that the Overall Risk score should be "~5" to capture project-level risk, CA's response was instructive: "Both are correct for their scope."

This is the CA's score-decision tension in compressed form. CA gave Overall Risk a 9 and said it was right. DA proposed a 5 and CA agreed that was also right. Two correct scores to the same labeled dimension. The council assigned a 9 to Overall Risk in the score table. The synthesis labeled it "implementation risk 9, project risk 6, blended." But the table still shows 9. A reader who sees "Overall Risk: 9" and doesn't read the synthesis narrative will import the wrong number.

**Dimension CA weighted most:** Evidence Confidence. Every claim is line-number grounded. CA treated codebase certainty as the foundation of all other scores. This is methodologically coherent but it means CA's scores are only as correct as the assumption that codebase facts dominate risk — which is exactly the assumption DA challenged.

**Dimension CA discounted:** SDK stability. CA's Dependency Risk score (9) was defined as "no upstream dependencies need to change... the SQLite file is the shared state." This is true for the existing codebase. CA explicitly excluded third-party library risk from the Dependency Risk score. The MCP SDK and fastapi-mcp are upstream dependencies for the proposed expansion — and CA didn't score them because they weren't yet in the codebase. This is a gap, not an error, but it means CA's 9 on Dependency Risk is measuring a narrower scope than the label implies.

---

### External Researcher (ER)

**Scores (Approach B):** Relevance 10, Maturity 8, Community Health 9, Integration Effort 9, Overall Risk 8, Reversibility 10, Evidence Confidence 9.

**Recommendation:** REST + MCP via fastapi-mcp.

**Alignment assessment:** Good alignment on direction. One notable score-conclusion gap.

ER gives Overall Risk 8 for Approach B. This is the second-highest risk score in the council (only CA gives a higher score, 9). ER frames this as "Low risk — MCP server is mounted alongside REST, not replacing it." An Overall Risk of 8/10 typically signals very low risk. ER's recommendation follows from this score.

The tension: ER's own narrative introduces concerns that a pure 8/10 doesn't capture. ER writes: "a v0.x library in production carries minor version risk... fastapi-mcp sits on top of the MCP SDK, meaning an MCP SDK v2 breaking change could cascade into fastapi-mcp." ER also acknowledges DA's auth architecture point "landed harder than expected" and revised the sequence to require rate limiting before MCP. These are not trivial concerns. They describe a dependency chain (Submantle → fastapi-mcp → MCP Python SDK v2 breaking changes) and a sequencing prerequisite. Neither of these concerns is reflected in an 8/10 risk score. An 8/10 implies the risk is primarily absorbed — ER's own narrative describes it as present and requiring active management.

ER's Evidence Confidence score (9) is the other notable tension. ER gives 9/10 confidence to Approach B's evidence. DA challenged this to 7/10, arguing that 9/10 is evidence that fastapi-mcp works — not that it handles Submantle's custom HMAC auth scheme, not that it will track SDK v2 changes on a compatible timeline. ER's response did not contest this challenge directly. The score remained 9 in the table. The synthesis's risk section lists "HMAC auth passthrough unverified" as an open risk. These two facts — Evidence Confidence 9 in the score table, HMAC passthrough unverified in the risks section — sit in unresolved tension.

**Dimension ER weighted most:** Relevance and ecosystem adoption. The 97M monthly downloads finding anchors ER's entire recommendation. ER treats adoption as the primary signal that MCP is the correct protocol choice. This is reasonable — protocol choices are network effects problems and adoption data is the right evidence. But it means ER's scores weight ecosystem momentum heavily relative to implementation risk, which explains the gap with DA.

**Dimension ER discounted:** SDK stability. ER presented the MCP spec's transport evolution as settled ("Streamable HTTP consolidating as production remote transport"), but did not check the Python SDK repository state. This is the gap DA identified in the Challenge Round. ER acknowledged it. The 9/10 Evidence Confidence score doesn't fully reflect this gap.

---

### Devil's Advocate (DA)

**Scores:** Failure Probability 3, Failure Severity 3, Assumption Fragility 2, Hidden Complexity 2, Overall Risk 2, Reversibility 5, Evidence Confidence 7.

**Recommendation:** Implicit — DA does not formally recommend an approach. DA raises objections and asks three questions: which vulnerabilities are patched before multi-protocol ships? What is the auth story for MCP? How does stdio coexist with the always-running daemon?

**Alignment assessment:** This is where the most interesting score-decision tension lives.

DA's scores are the most internally consistent of the three agents. Low scores on failure modes, low overall risk, moderate reversibility, reasonable evidence confidence. By DA's own scoring, the proposal carries meaningful risk but not prohibitive risk — "proceed with caution" is the logical read.

But DA's narrative is the most hostile to proceeding. The strongest objections — MCP SDK v2 breaking changes are imminent and certain, open multi-protocol before auth trains the market toward free, incident reporting via MCP is a prompt injection attack surface, three protocols is three products for a solo founder — read as arguments for significant delay or fundamental restructuring.

The scoring and the narrative are not contradictory, but they are calibrated differently. Failure Probability 3/10 means "high probability of failure" in DA's scale (where low scores indicate high risk). Failure Severity 3/10 means "high severity if it fails." This is a strong risk signal. But DA also consistently says these risks are manageable through sequencing and scoping. The risk scores say "this can fail badly." The narrative says "here's how to not fail badly."

**The scale inversion problem:** DA's scoring scale inverts convention. All other agents score high numbers as high quality / low risk (CA's 9/10 Feasibility means "very feasible"). DA's role-specific dimensions score high numbers as low risk *of failure* — but Overall Risk 2/10 means "very high risk" in conventional framing. This inversion is partially documented (DA labels scores as "Failure Probability 3" where 3/10 means high failure probability) but produces visual confusion in comparison tables where CA's 9 and DA's 2 appear side-by-side on "Overall Risk."

The score extraction table shows Overall Risk: CA 9, ER 8, DA 2. A naive reader sees "DA 2/10" and thinks DA considers this very low risk. The opposite is true. The spread analysis correctly notes this, but the table itself creates a misleading impression that persists in any document that quotes the table without context.

**Dimension DA weighted most:** Strategic and adversarial scenarios. DA treated the security blast radius analysis and the "billing training" concern as more important than implementation risk. This weighting is explicit — DA distinguishes "security blast radius" from "code blast radius" and argues CA's analysis only covers the latter. Whether this weighting is appropriate depends on what question the council was actually trying to answer, which is a values dispute, not a factual one.

**Dimension DA discounted:** Implementation ease. DA did not know about fastapi-mcp before the Challenge Round. This is not a criticism — DA's job is to find failure modes, and fastapi-mcp genuinely addresses several of them. But DA's initial scores on Hidden Complexity and Failure Probability were set without knowledge of the library that reduces implementation to three lines. DA acknowledges this in the Challenge Round: "fastapi-mcp is a genuine mitigation." The scores were not formally revised. The official score table still shows the pre-fastapi-mcp Hidden Complexity and Failure Probability assessments.

---

## Section 2: Cross-Agent Score Comparison (Shared Dimensions)

### Overall Risk

| Agent | Score | What They Measured |
|-------|-------|-------------------|
| Codebase Analyst | 9/10 | Risk to existing code from adding MCP adapter |
| External Researcher | 8/10 | Risk from fastapi-mcp dependency and ecosystem maturity |
| Devil's Advocate | 2/10 | Strategic risk to project: SDK instability, billing timing, attack surface multiplication, solo founder maintenance burden |
| Spread | **7** | Not measuring the same thing |

A spread of 7 across a shared dimension is the council's loudest signal. The synthesis correctly identifies the cause: "two different risk questions producing two different scores." This is the right diagnosis. But it raises a structural question the synthesis doesn't answer: if three agents are measuring different things on a shared dimension, what is the shared dimension for?

The score extraction says "Overall Risk spread of 7 — CA sees implementation risk, DA sees project risk." But this framing suggests the spread is explained. It is not resolved. The synthesis produces a "blended" position ("implementation risk ~9, project risk ~6") but does not produce a single Overall Risk score that captures both. The synthesis score table shows CA=9, ER=8, DA=2, Avg=6.3. The average of scores measuring different things is not a meaningful number — it does not represent the actual project risk or the actual implementation risk. It is an artifact of combining incommensurable measurements.

**What the spread actually reveals:** The three agents had different mental models of what question they were scoring. CA's model: "will this break the codebase?" ER's model: "will this approach work in the ecosystem?" DA's model: "will this strategic decision succeed or fail?" These are all valid questions. None of them is what "Overall Risk" typically means without qualification. The council should have aligned on a single definition before scoring, or produced three separate risk scores. It produced one labeled dimension, three different questions, and a spread that looks like disagreement but is partly a labeling problem.

---

### Reversibility

| Agent | Score | What They Measured |
|-------|-------|-------------------|
| Codebase Analyst | 10/10 | Before publication: delete the file, no impact |
| External Researcher | 10/10 | Implementation: remove 3 lines and one import |
| Devil's Advocate | 5/10 | After publication: breaking change for external integrators |
| Challenge proposals | CA: 10 → proposed 8-10 by ER+CA; DA: 5 → proposed 8+ by ER+CA | Both parties acknowledged timeframe-dependence |
| Spread | **5** | Measuring different timeframes |

The reversibility spread is a timeframe dispute, not a factual disagreement. CA and ER score the present moment: "right now, nothing is published, the file can be deleted." DA scores a future moment: "after agents integrate against the MCP endpoint, removing it breaks their pipelines."

Both positions are correct. Reversibility is a moving target — a decision that is 10/10 reversible today can be 5/10 reversible after publication. The synthesis adopts 9/10 "for the current prototype stage, with a note that this drops to ~7 once the MCP endpoint is documented and consumed." This is a reasonable resolution, but it requires the reader to understand that "Reversibility 9/10" means "reversible today, less so tomorrow" — which is not what a score of 9 normally communicates.

The challenge round proposed revisions were never adopted. DA proposed ER's Reversibility score should be 8 (ER implicitly agreed with this framing in the challenge). CA and ER proposed DA's Reversibility should be 8-10 (DA acknowledged this only partially, maintaining that deployment reversibility is the relevant scope). The score table still shows the original Phase 1 scores. This is the correct protocol — scores are produced in Phase 1 and challenged but not changed. But the gap between what the challenge round established (timeframe-dependence is real, the scores should be understood in that context) and what the score table shows (10, 10, 5) is wider than the synthesis narrative acknowledges.

---

### Evidence Confidence

| Agent | Score | What They Measured |
|-------|-------|-------------------|
| Codebase Analyst | 10/10 | Confidence in codebase claims (every line number cited) |
| External Researcher | 9/10 | Confidence in ecosystem claims (sources cited, fastapi-mcp verified) |
| Devil's Advocate | 7/10 | Confidence in failure mode evidence (SDK GitHub, Wiz Research, Willison) |
| Spread | **3** | Measuring confidence in different evidence bodies |

This is the cleanest shared dimension. The scores are similar in magnitude (7-10), and the spread of 3 is consistent with genuine variation in evidence quality across different domains. CA's 10 is defensible — specific line numbers are highly verifiable. ER's 9 is also defensible — external sources are cited and credible. DA's 7 reflects that failure mode evidence is inherently more speculative (you're documenting scenarios that haven't occurred).

But there is a subtle tension: each agent's Evidence Confidence score is confidence in their own evidence, not confidence in the overall picture. When three agents each have high confidence in their own evidence, and their evidence points in different directions, the aggregate confidence in the conclusion is lower than any individual score. This effect is real in this council: CA is highly confident the codebase is ready. ER is highly confident MCP is the right protocol. DA is fairly confident about the failure scenarios. Together, these produce a picture with genuine uncertainty — but no single Evidence Confidence score captures that. The synthesis's Avg of 8.7 for Evidence Confidence suggests the council is collectively 87% confident. Whether that's the right number depends on how the evidence bodies combine, which was never explicitly evaluated.

---

## Section 3: Score-Decision Tension Map

### The Core Tension: What Got Recommended vs. What the Scores Support

The council's recommendation is: **REST + MCP via fastapi-mcp, with read-only MCP scope and rate limiting prerequisites.**

DA's scores say: Failure Probability 3/10, Failure Severity 3/10, Overall Risk 2/10. In DA's scale, these mean "high probability of failure, high severity if it fails, high overall project risk." Yet DA's challenge round begins: "The fastapi-mcp discovery is the most useful finding in either report" and concludes that fastapi-mcp "changed my recommendation on implementation path." DA does not formally recommend against proceeding.

This is not a contradiction — DA's role is to surface risks, not to veto decisions. But it creates an interpretive gap: does DA's score of 2/10 on Overall Risk mean "I think this should not be done"? Or does it mean "here are the risk factors you should manage"? The challenge round suggests the latter, but the Phase 1 findings read as the former.

If DA's Phase 1 scores are read as "high-risk, do not proceed without addressing X," and the recommendation addresses X (read-only scope, rate limiting prerequisite, billing keys in close sequence), then the recommendation is responsive to the scores. If DA's scores are read as capturing baseline risk that the sequencing precautions only partially offset, then the council may have underweighted them in the final recommendation.

The synthesis does not adjudicate this. It presents DA's risks as "real but manageable through sequencing" — which is the optimistic reading of DA's score-narrative pattern. The pessimistic reading — that DA's low scores mean the risks remain high even after sequencing — is not examined.

---

### The fastapi-mcp Discovery and the Obsoleted Analysis

The largest single score-decision tension in this council is not between agents but within the deliberation's own timeline. DA's Phase 1 scores were set without knowledge of fastapi-mcp. This is correct procedure — Phase 1 happens before the Challenge Round. But the effect is that DA's role-specific scores (Failure Probability 3, Hidden Complexity 2) reflect implementation complexity that does not exist in the fastapi-mcp implementation path.

DA acknowledged this explicitly: "fastapi-mcp is a genuine mitigation." The synthesis acknowledged it. But the score table shows the Phase 1 scores. The tension is this: the council's official score record shows DA assessing failure probability as high — but DA's post-fastapi-mcp position is that implementation failure probability is lower. There is no mechanism in the council's Phase 1 score architecture to capture a score update that was clearly warranted by Challenge Round evidence.

If DA had known about fastapi-mcp in Phase 1, DA's Hidden Complexity score would likely have been 4-5 rather than 2 (fastapi-mcp eliminates the auth-across-three-protocols problem, the subprocess/daemon conflict, the new-file build effort). The council's score table would look meaningfully different. The recommendation would be identical, but it would rest on a more accurate risk foundation.

---

### The Unresolved: report_incident via MCP

DA raised this in Phase 1, in the Challenge Round, and in the summary of unresolved items. No other agent produced a definitive answer. ER proposed "selective MCP endpoint exposure" as the resolution — expose read-only via MCP, keep writes REST-only. The synthesis adopts this: "Expose only read endpoints via MCP initially."

But the tension was never closed. DA's summary of unresolved items listed: "report_incident via MCP, billing timing, Wave 5 vs Wave 11 priority." The synthesis addresses billing timing ("ship business API keys in close sequence with MCP") and Wave priority ("rate limiting → fastapi-mcp mount → HMAC validation → business API keys → expand MCP scope"). It addresses report_incident via MCP by deferring it.

Deferral is not resolution. The synthesis says "MCP starts read-only; write operations added only after reporter identity verification." Reporter identity verification is not in the current build queue. It is not scoped. It is not in the build priority table that the synthesis references. The tension DA identified — that incident reporting via MCP creates a prompt injection attack surface — is managed by not doing it yet. What "reporter identity verification" means architecturally, and when it arrives, is left open.

---

### The Wave 5 vs. Wave 11 Priority Conflict

The build priority table lists MCP server as Wave 5 and Business API keys as Wave 11. The synthesis recommendation says to ship them "in close sequence." DA noted in the Challenge Round: "neither agent challenged this priority ordering or argued the other direction" — and treated this as a notable silence.

The silence was not resolved in synthesis. The build priority table in CLAUDE.md still shows Wave 5 and Wave 11. The synthesis recommendation section says "ship business API keys in close sequence with MCP (weeks, not months apart)" — but does not change the wave numbering or explain how six waves separate in a build table translates to "weeks apart" in execution.

This is the council's largest unresolved practical tension. If a builder reads the CLAUDE.md build table, they see MCP at Wave 5 and business API keys at Wave 11 — six steps apart, with soft-delete deregistration, pending state, severity classification, dedup, and formula changes in between. If a builder reads the synthesis recommendation, they see "ship in close sequence." These are different instructions. The synthesis did not reconcile them with the canonical source document.

---

## Section 4: Observable Weighting Analysis

### What Each Agent Actually Weighted

**Codebase Analyst weighted:** Architectural purity and codebase readiness. CA's scores track the extent to which the proposed change is additive vs. disruptive to existing code. Every high score has a corresponding architectural explanation (protocol-agnostic service layer, dependency injection pattern, SQLite WAL mode). Every CA score that could be lower (e.g., Dependency Risk 9 vs. 10) is explained by a single identified risk (initialization order invariant). CA's recommendation follows directly from finding that the architectural prerequisites are already met.

**External Researcher weighted:** Ecosystem adoption and protocol fit. ER's scores track how well the evidence supports the protocol choice. The highest-confidence finding (MCP: 97M monthly downloads, de facto standard) drives the highest score (Relevance 10). The second-most-important finding (fastapi-mcp: 3-line integration, auth passthrough) drives the Integration Effort score (9). ER's recommendation follows from finding that the ecosystem is ready and the implementation is easy.

**Devil's Advocate weighted:** Adversarial scenarios and strategic risk. DA's scores track the probability and severity of failure scenarios. The strongest finding (MCP SDK v2 breaking changes imminent) drives the lowest scores. DA gives higher Evidence Confidence (7) than Assumption Fragility (2), signaling that the failure scenarios are well-evidenced but the assumptions underlying the proposal are fragile. DA's implied recommendation follows from finding that the risks are real and the assumptions are not yet validated.

### What the Weighting Reveals About Values

All three agents agreed on the recommendation. This agreement emerged from completely different weighting frameworks. CA valued architectural readiness. ER valued ecosystem alignment. DA valued risk management. The convergence on "REST + MCP via fastapi-mcp with sequencing precautions" means this recommendation satisfies all three frameworks simultaneously — or means the framing of the recommendation absorbed the concerns from each agent's framework without forcing explicit tradeoffs.

The synthesis recommendation contains elements that would score differently in each framework:
- "Rate limiting first" — DA's contribution. CA would not have derived this from codebase analysis alone.
- "3-line fastapi-mcp mount" — ER's contribution. CA derived a more complex implementation.
- "Read-only scope initially" — DA's contribution. ER proposed it. CA confirmed it.
- "Business API keys in close sequence" — all three agents contributed, but only DA identified it as sequencing-critical.

The synthesis looks like consensus because it incorporated all of these elements. But there was no explicit vote or resolution on which framework should dominate when the frameworks diverged. The synthesis aggregated; it did not arbitrate.

---

## Section 5: Confidence Calibration

### Where Stated Confidence Was Well-Calibrated

CA's Evidence Confidence 10/10 for codebase claims is appropriate. Every claim has a line number. A reader could verify each claim directly. The confidence is bounded to what was measured (the existing codebase), and CA is explicit about those bounds.

DA's Evidence Confidence 7/10 is appropriate. DA cites Wiz Research, Simon Willison, and SDK GitHub issue numbers. These are verifiable. DA's acknowledgment that "the solo founder maintenance burden argument is structural and doesn't require external evidence" correctly flags inference-based claims as less certain than documented-source claims.

### Where Stated Confidence Was Overcalibrated

ER's Evidence Confidence 9/10 for Approach B is the council's most clearly overcalibrated score. ER's confidence is justified for two claims: fastapi-mcp exists and MCP is widely adopted. ER's confidence is not justified, by ER's own account, for: whether fastapi-mcp correctly handles Submantle's custom HMAC auth scheme, whether the 3-line integration works for selective endpoint exposure, and whether fastapi-mcp will track MCP SDK v2 changes on a compatible timeline. These are not peripheral concerns — they are the load-bearing assumptions of the recommendation. The synthesis lists all three as open risks. If the evidence to support the recommendation includes unverified assumptions about the central mechanism (HMAC auth passthrough), a 9/10 confidence score misrepresents the council's actual epistemic position.

### The Confidence Asymmetry

CA's confidence is high and bounded (codebase only). ER's confidence is high and moderately bounded (ecosystem + library, with acknowledged gaps). DA's confidence is moderate and explicitly scoped (failure scenarios, SDK state, not ecosystem adoption data). The council's aggregate confidence is high — but the areas of genuine uncertainty (HMAC auth passthrough, fastapi-mcp's SDK tracking behavior, reporter identity verification architecture) sit precisely in the space where ER's high confidence is most overcalibrated.

This asymmetry matters because the recommendation rests most heavily on ER's finding (fastapi-mcp is the implementation path). That finding carries the highest uncertainty about its load-bearing assumptions. The council decided confidently on the basis of evidence that has the largest unverified component.

---

## Section 6: What the Council Did Not Notice

### The Scale Inversion Was Never Acknowledged

DA uses an inverted scale for role-specific dimensions. "Failure Probability 3/10" means *high* failure probability (low score = bad). This is internally consistent with DA's role — as Devil's Advocate, lower scores mean the adversarial case is stronger. But the shared dimensions (Overall Risk, Reversibility, Evidence Confidence) are presumably on the same scale as CA and ER's shared dimensions, where higher = better.

DA scores Overall Risk 2/10. CA scores Overall Risk 9/10. In the comparison table, these look like a 7-point disagreement on a common scale. In reality, DA's 2 on Overall Risk means "high risk" while CA's 9 means "low risk" — the scale is consistent, the score values are consistent, but the visual representation in a table where they appear side-by-side creates a misleading picture. A reader unfamiliar with the role-specific conventions might interpret the table as "CA sees very low risk, DA sees moderate risk" rather than the correct "CA sees very low implementation risk, DA sees high project risk."

The synthesis addresses this in narrative but not in the table. The table persists as the most compact summary of the council's output, and it is the format most likely to be referenced without the surrounding context.

### The Definition Problem Was Present Throughout

"Overall Risk" was never defined. Each agent scored it according to their role's natural interpretation of risk. The synthesis correctly identifies this as two different questions producing two different scores. But it identifies this after the fact, in the resolution section. A pre-scoring definition would have either forced the agents to score the same thing (producing genuine comparability) or prompted explicit acknowledgment that three separate risk questions were being tracked.

This is not unique to this council — shared dimensions in multi-agent research are inherently ambiguous without explicit definitions. But the 7-point spread is partly an artifact of the ambiguity, not purely a signal of genuine disagreement. The insight ("CA sees implementation risk, DA sees project risk") is valuable and correct. It would have been more valuable if the council had designed for it.

### The Challenge Round Produced Score Updates That Were Never Applied

DA acknowledged fastapi-mcp "changed my recommendation on implementation path." CA acknowledged the MCP SDK instability "is more serious than I expected." ER acknowledged DA's auth architecture point "landed harder than expected" and revised the implementation sequence to require rate limiting first. These are meaningful epistemic updates.

The score table shows Phase 1 scores throughout. The challenge round's effect on scores was preserved only as proposed revisions that "were not adopted." The record shows what the council learned but not how that learning affected the confidence of its output. A reader who uses the Phase 1 scores as the canonical record will import pre-learning estimates as the council's considered position.

---

## Summary: The Five Tensions That Matter

**1. Overall Risk is two questions wearing one label.** CA's 9 measures implementation risk. DA's 2 measures project risk. The synthesis blends them into a narrative but not a single score. Any downstream use of "Overall Risk" from this council needs to specify which question it's answering.

**2. DA's scores were set before fastapi-mcp, but the recommendation assumes fastapi-mcp.** The load-bearing implementation decision (use fastapi-mcp, not a standalone server) was discovered in Phase 2. DA's Phase 1 scores do not reflect it. The recommendation rests on an implementation path that the council's official score record did not fully evaluate.

**3. ER's Evidence Confidence 9/10 is overcalibrated for the load-bearing assumption.** The recommendation depends on HMAC auth passthrough working with fastapi-mcp. This is unverified. A 9/10 confidence score on evidence that does not verify the central mechanism misrepresents the council's epistemic state.

**4. "Billing in close sequence" is not reconciled with Wave 5 / Wave 11 in the build table.** The synthesis recommendation and the canonical build priority table give different instructions. A builder will read one or the other, not both. Which one governs?

**5. Reporter identity verification is deferred without being scoped.** DA's strongest surviving objection (incident reporting via MCP = prompt injection surface) is managed by not doing it yet. The condition for doing it ("after reporter identity verification exists") is not in the build queue. The tension is suspended, not resolved.

---

*The value of a tension report is not to second-guess the recommendation. The recommendation may be exactly right. The value is to make the reasoning's joints visible — so that when assumptions are later tested against reality, the council's actual epistemic state is legible, not just its conclusions.*
