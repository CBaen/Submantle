# Tension Report: Scoring Model Council
## Date: 2026-03-12
## Authored by: Tension Analyst (Claude Opus 4.6)

---

## What This Report Does

The synthesis already synthesized. My job is not to re-synthesize it. My job is to find the places where agents said one thing with their scores and did something different with their conclusions — and where agents agreed with each other loudly while disagreeing quietly, and where the council as a whole converged on answers that their own evidence doesn't fully support.

The tension between scores and decisions is where the real insight lives. That is what this report contains.

---

## Part 1: Individual Score-Decision Alignment

### Codebase Analyst

**Scorecard summary:**
- Feasibility: 8/10
- Blast Radius (10=minimal): 7/10
- Pattern Consistency: 8/10
- Reversibility: 6/10
- Dependency Risk (10=none): 9/10

**The tension:** The Codebase Analyst scored feasibility at 8/10 and produced a genuinely optimistic picture of the codebase — clean separation, minimal blast radius, a free upgrade sitting unused in `trust_metadata`. Their conclusions match their scores almost perfectly. There is no meaningful tension between what they scored and what they recommended.

**But the tension exists at the edges of their frame.** The Codebase Analyst's mandate was to assess the blast radius of enriching the scoring model. They did this well. The tension is that this frame made them constitutionally unable to see the system's most dangerous failure mode: the deregister hard DELETE. They found it, eventually, but only in Section 6, after five sections of technical analysis. An analyst doing blast-radius assessment naturally looks at what breaks when you add things. The hard DELETE is a problem with what happens when you remove things. It lives outside the blast-radius frame. The Codebase Analyst found it anyway — credit to them — but the framing explains why it appeared at the bottom of the list rather than the top.

**Score the Codebase Analyst ignored:** Their Reversibility score of 6/10 implies meaningful risk of irreversibility. But their recommendations do not reflect urgency about irreversibility. They propose the `agent_status` column as a fix — in "Priority Challenges for the Council" item #1 — but do not flag it as a "before any other work begins" blocker. A 6/10 on reversibility, once you understand that the specific irreversibility here is the permanent deletion of historical agent records that can never be recovered, should drive more urgency than their framing conveys.

**The most revealing tension:** The Codebase Analyst noted that `update_trust_metadata()` exists and nothing calls it — and then described using `trust_metadata` as a "free upgrade." The Devil's Advocate correctly identified that the column is free but the detection logic to populate it meaningfully is not. The Codebase Analyst's score of 8/10 on Pattern Consistency applies to the column. It does not apply to the anti-gaming logic that would need to be written to make the column useful. The analyst scored the storage layer but described the full enrichment stack as if it were approximately free.

---

### External Researcher

**The FICO relevance score (9/10) versus the eBay relevance score (7/10) produces a hidden structural recommendation.**

The External Researcher gave credit bureaus/FICO a 9/10 relevance score and eBay/Amazon a 7/10 relevance score. Both are high scores. But FICO and eBay actually point in opposite directions on a critical design question: what is a "reporter"?

- FICO's model: reporters (lenders) are credentialed institutions who are legally liable for what they report. The bureau passively receives.
- eBay's model: reporters (buyers) can only rate after a completed transaction. The platform links the rating to the event.

The External Researcher's synthesis collapsed these into a single recommendation: "require reporter credentialing." But the two systems actually answer different questions. eBay's answer is about **linkage** (a report must be tied to a real transaction). FICO's answer is about **identity verification** (a reporter must be a known entity). Submantle needs both — but the External Researcher's synthesis produced only the FICO half.

The reason this matters: the External Researcher in the challenge round proposed that Submantle should track "reporter accuracy score" — if a reporter files 50 incidents and 40 are disputed, their weight decreases. That recommendation is eBay-style (behavioral feedback on the reporter). But this was proposed in the challenge round, not in the Phase 1 findings. The Phase 1 FICO-dominant frame produced "credentialed reporters," and only the challenge round's confrontation with the Codebase Analyst's findings produced the richer "reporter accuracy scoring" insight.

**The tension:** The External Researcher's highest-relevance score (9/10, credit bureaus) anchored their Phase 1 thinking in a direction that missed the eBay-derived insight they themselves scored at 7/10. The scores were internally consistent; the implications weren't fully extracted.

---

**The Signet relevance score (10/10, later adjusted to 8/10) versus the actual Signet analysis.**

The External Researcher gave Signet a 10/10 relevance score and then described Signet's LLM-swap decay rule as a lesson to learn from. The Devil's Advocate correctly challenged this: Signet's decay rule contradicts Submantle's design principle that trust belongs to the entity, not the model.

The relevant tension: a 10/10 relevance score says "this is as relevant as it gets." But the council ultimately rejected the Signet-derived decay rule and adopted the author-field visibility approach instead. The score said "maximum relevance"; the decision said "do not copy this specific thing." These are compatible — high relevance and "don't copy this" coexist — but the External Researcher did not make that distinction. They treated high relevance as directional. It should have been analytical: Signet is maximally relevant *for understanding what not to do* is a coherent position. It is not the same as "Signet is maximally relevant as a model to follow."

---

**The NIST AI RMF relevance score (6/10) versus the Devil's Advocate's challenge (8/10).**

The External Researcher scored NIST at 6/10 with the note "useful for sales narrative." The Devil's Advocate challenged this upward to 8/10, arguing that NIST is a procurement gate for enterprise customers.

The Orchestrator split the difference at 7/10. But neither the original score nor the challenge fully articulated the actual tension here: the External Researcher's characterization of NIST as "sales narrative fluff" reveals an implicit assumption that the scoring model's job is to produce technically correct signals. The Devil's Advocate's challenge reveals an implicit assumption that the scoring model's job is to produce signals that enterprise customers will buy.

These are different jobs. The 6/10 versus 8/10 score disagreement is a proxy for a deeper disagreement about what Submantle is building: infrastructure that is technically correct, or a product that enterprise customers recognize as familiar.

---

### Devil's Advocate

**The Risk Scorecard versus the recommendations.**

The Devil's Advocate's Risk Scorecard:
- Failure Probability: 3/10 (low score = high probability of failure)
- Failure Severity: 4/10
- Assumption Fragility: 3/10
- Rollback Difficulty: 6/10
- Hidden Complexity: 5/10

These scores paint a genuinely alarming picture. The Failure Probability of 3/10 means the Devil's Advocate believes failure is more likely than not. Assumption Fragility of 3/10 means the load-bearing assumptions are more likely wrong than right.

Yet the Devil's Advocate's recommendations are entirely constructive: fix the reporter auth, add velocity caps, handle cold start, document the enforcement floor. These are reasonable engineering fixes. They are not "stop what you're doing and re-examine the entire premise."

**The tension is acute:** A Failure Probability of 3/10 and Assumption Fragility of 3/10 should produce recommendations that say "do not build further until the assumptions are verified." Instead they produce a prioritized list of things to build. The Devil's Advocate correctly identified that "businesses will pay for trust scores" is the most important unverified assumption — and then filed it as Priority Finding #5, behind three technical fixes.

The scores and the recommendations are not aligned. The scores say "this is probably going to fail." The recommendations say "here's what to fix." The council needed to resolve this tension directly: either the Failure Probability score is too pessimistic, or the recommendation to prioritize technical fixes over customer discovery is wrong. The synthesis flagged customer discovery as important ("the most strategically important finding in the entire council") but deferred it as "outside the scoring model scope." That deferral is exactly the move the scores were supposed to prevent.

---

**The "Neutral infrastructure should never enforce" assumption verdict: UNVERIFIED, rated "dangerous if held rigidly" — but the recommendation softens the finding.**

The Devil's Advocate's Phase 1 verdict was that the absolutist "never enforce" position is "legally and reputationally fragile." They proposed a middle ground: quarantine, dispute channel, emergency termination for identity fraud.

The External Researcher challenged this in Phase 2, arguing that "quarantine" is enforcement and the correct model is withdrawing attestations. The Orchestrator adopted a synthesis: Submantle can withdraw its "Verified" badge; it does not quarantine.

**The tension:** The Devil's Advocate's Phase 1 finding was that the "never enforce" position is specifically dangerous because of the identity fraud case — someone registers "anthropic-claude-official." The Orchestrator's resolution (withdraw attestations) does not resolve the identity fraud case. An agent named "anthropic-claude-official" continues to exist in the registry with its score. Submantle can decline to issue a "Verified" badge to it. But the agent is still there, still named "anthropic-claude-official," still queryable. The External Researcher's CA revocation analogy breaks down here: when a CA revokes a certificate, the revocation is visible to the entire browser ecosystem immediately. When Submantle withdraws a "Verified" badge from a fake Anthropic agent, that badge was never issued in the first place.

The synthesis resolved the enforcement debate by adopting the External Researcher's framing. But the Devil's Advocate's specific case — pre-existing identity fraud, not behavioral scoring — was not fully answered by either model. The tension remains unresolved.

---

## Part 2: Cross-Agent Score Comparison

### eBay Relevance: 7/10 vs. 5/10

External Researcher: 7/10. Codebase Analyst challenge: 5/10. Orchestrator adjustment: 6/10.

**The gap (2 points) is meaningful and reveals a genuine interpretive difference.** The Codebase Analyst argued that the two-sided grading problem (sellers retaliating against buyers) doesn't apply to Submantle because brands rate agents but agents don't rate brands. The External Researcher acknowledged this ("Submantle is one-sided") but retained 7/10 because the behavioral-outcomes lesson (implicit signals over explicit ratings) is transferable.

What neither agent said explicitly: the most valuable eBay finding is not about two-sided grading at all. It is about the evolution of anti-gaming mechanisms — from explicit ratings toward implicit behavioral signals. eBay's lesson is that any scoring system built on explicit reports will be gamed, and the fix is to make the signal harder to manufacture. The External Researcher derived this correctly but buried it. The Codebase Analyst challenged the relevance score rather than the derivation.

The 6/10 compromise preserves the insight without fully explaining why both scores were partially right.

---

### Signet Relevance: 10/10 vs. 7/10 vs. 8/10 (final)

External Researcher: 10/10. Devil's Advocate challenge: 7/10. Orchestrator adjustment: 8/10.

**This is the largest score disagreement in the entire council on any single dimension (3-point spread). It deserves more examination than it received.**

The External Researcher scored Signet at 10/10 because it is the closest direct competitor. "Relevance" is doing two jobs here that should be separated:
1. Relevance as competitive intelligence (how closely does Signet map to what Submantle is building?)
2. Relevance as design input (how much should Submantle learn from Signet's design choices?)

For job #1, 10/10 is defensible. Signet and Submantle are building structurally similar products.
For job #2, the Devil's Advocate's 7/10 is more defensible — two of Signet's key design choices (SDK self-reporting, LLM-swap decay) are counter-examples for Submantle.

The Orchestrator split the difference at 8/10 without resolving which job "relevance" was scoring. The score adjustment feels like a social compromise rather than a conceptual resolution. If relevance means "how much should this inform our design," the correct score is closer to 7/10. If relevance means "how closely does this match our product category," the correct score is 10/10. The 8/10 satisfies neither interpretation.

---

### NIST AI RMF Relevance: 6/10 vs. 8/10 vs. 7/10 (final)

External Researcher: 6/10. Devil's Advocate challenge: 8/10. Orchestrator adjustment: 7/10.

**Same pattern: the Orchestrator split the difference without resolving the underlying disagreement.**

The External Researcher's 6/10 reflects: "NIST doesn't tell us how to build the scoring model."
The Devil's Advocate's 8/10 reflects: "NIST is how enterprise customers will ask about the scoring model."

These are compatible positions that produce different scores because they're measuring different things. The council needed to decide what "relevance" means for a source that provides no technical content but significant commercial framing. It did not make that decision. The 7/10 is a numerical average, not a conceptual synthesis.

---

### Feasibility: Code feasibility 8/10, semantic feasibility ~5/10 (Orchestrator ruling)

This is the most important score resolution in the entire council. The Orchestrator correctly ruled that feasibility has two distinct dimensions with different scores. But this ruling appears only in the Master Score Table footnote and is not carried forward into the recommendations.

If semantic feasibility — can we make the scoring model produce signals that actually mean something to businesses — is ~5/10, then every Tier 1 recommendation is implicitly rated ~5/10 on the dimension that determines whether the work has any value.

The recommendations are presented with confidence. The underlying semantic feasibility score is not. The tension between "we can build this" (8/10) and "this will mean something when built" (~5/10) is exactly the kind of tension that produces technically impressive systems no one buys.

---

## Part 3: Score-Decision Tension Map

### Proposal: Authenticated incident reporters (Tier 1, highest priority)

All three agents scored the current state of unauthenticated reporting as CRITICAL (Failure Probability 3/10, Failure Severity 4/10). The recommendation is to build reporter authentication before any public demo.

**Tension:** The recommendation is calibrated to the scores. But the discussion of HOW to implement authentication reveals a deeper unresolved question. The Codebase Analyst asks: does a "registered business" reporter require a separate registry, or can it reuse agent auth with a `role` field? The External Researcher says reporters need "skin in the game" — not just registration, but accuracy tracking. The synthesis adopted both suggestions but did not resolve which comes first, how reporter accuracy is computed, or what the relationship between a reporter's accuracy score and their reports' weight in the formula actually is.

The recommendation says "Track reporter accuracy over time." This is a second Beta-style reputation system running in parallel with the agent reputation system. The scores say this is the most critical fix. The decision does not fully specify what "reporter accuracy tracking" means as an implementation. The council converged on the destination but not the architecture.

---

### Proposal: Trust score has two valid initializations — Beta prior 0.5 (correct) and "no history" flag (commercially needed)

**Tension map:**

The Codebase Analyst scored the cold start as "system working correctly." The Devil's Advocate scored it as "commercially useless." The External Researcher proposed a specific fix ("no_history" API flag). The Orchestrator split the finding: "Mathematically correct. Commercially, the API should distinguish 'no history' from 'scored at 0.5.'"

This is the only place in the entire council where the synthesis explicitly acknowledges that two things that are both true can still be in tension. But the resolution — add a display flag — minimizes the tension rather than engaging with it.

**What the DA's score actually implies:** If 0.5 for an unknown agent is "commercially useless," then the architecture has a cold start problem that is worse than a display flag resolves. The DA's argument (malicious agents can pre-stage before deploying; legitimate agents arrive fresh) is not addressed by a "no_history" flag. A brand seeing "has_history: false" on a brand-new agent and "trust_score: 0.97" on an agent that pinged the API 10,000 times does not have better information for their access decision. They have clearer labeling of a system that still disadvantages legitimate late-entrants.

The score (3/10 on Assumption Fragility) implies the cold start problem is deeper than a labeling fix. The decision treats it as a labeling fix.

---

### Proposal: Score decay for compromised high-trust agents (Tier 3, "flag for future research")

**Tension map:**

The Devil's Advocate raised score decay in Phase 1. Neither other agent addressed it. The Orchestrator noted: "Council does NOT have consensus — flag for future research."

**The tension:** The DA's argument is structural, not stylistic. A Beta Reputation formula that accumulates trust indefinitely produces a dangerous asymmetry: an agent compromised after years of clean operation retains its high score until external reporters notice and file incidents. Under the credit bureau model (Submantle records third-party reports; it does NOT detect incidents), this lag is built into the architecture. The question "how long does a compromised agent keep its high score?" is a product liability question, not just a design choice.

The council declined to answer this question because no agent disputed the DA but no agent provided a concrete resolution mechanism. The synthesis flagged it honestly. But "flag for future research" is not an answer to a structural security property of the system. The council's silence on this point means the delivered scoring model has an unresolved failure mode in which the most dangerous agents are the ones most trusted — precisely because they have good historical records.

---

## Part 4: Observable Weighting Analysis

### Codebase Analyst

**Which dimensions appear to have driven their recommendations:**
- Pattern Consistency (8/10) — every recommendation they make is framed as "this fits the existing pattern"
- Dependency Risk (9/10) — they repeatedly note that changes are "purely self-contained"

**Which dimensions were scored but appear not to have influenced decisions:**
- Reversibility (6/10) — scored moderately concerning but does not produce a "do this first or you lose the ability" recommendation
- Blast Radius (7/10) — scored 7/10 but described throughout as "manageable," which makes the score feel disconnected from the prose

The Codebase Analyst weighted pattern-consistency and dependency-safety above reversibility in practice, which produces a recommendation set that is safe, low-disruption, and incrementalist. The 6/10 Reversibility score should have produced at least one recommendation framed as "if you don't do this now, you cannot do it later." The deregister fix is that recommendation. It appears as item #1 in Priority Challenges but is not framed with that irreversibility urgency.

---

### External Researcher

**Which dimensions appear to have driven their recommendations:**
- Relevance scores for credit bureaus (9/10) and IETF RATS (9/10) dominated the framing
- High evidence quality scores (9/10, 10/10) for the standards-based sources produced high confidence in standards-derived recommendations

**Which dimensions were scored but don't appear to have influenced the decisions:**
- Uber/Airbnb scored 6/10 relevance — and the only lesson derived (simultaneous reveal) was explicitly discarded as inapplicable
- App Stores scored 5/10 relevance — listed but not used at all

This is actually correct behavior: low-relevance sources should not drive recommendations. But it reveals that the External Researcher's scoring was functioning as a filter. Sources scoring below 7/10 relevance did not contribute to conclusions. This means the 7/10 eBay score was borderline — just above the threshold where findings get incorporated. If the Codebase Analyst's challenge had moved eBay to 5/10, the transaction-linkage insight from eBay (ratings must tie to real events, not just to reporter identity) would likely have been dropped entirely. A two-point score difference would have eliminated a structurally important finding.

---

### Devil's Advocate

**Which dimensions drove recommendations:**
- Failure Probability (3/10) and Assumption Fragility (3/10) drove the urgency ordering
- These scores produced the "customer discovery before dashboard" finding

**The critical observable weighting tension:**
Customer discovery outranked as Priority Finding #5 even though it connects to the two lowest scores (Failure Probability and Assumption Fragility). The DA's observable weighting placed technical fixes (reporter auth, velocity caps, cold start) above the finding that connects to their most alarming scores.

Why? The most plausible explanation: the technical fixes are within scope (the council was asked about the scoring model). Customer discovery is outside scope (the council was not asked whether anyone will buy the scoring model). The DA correctly identified that scope boundary and respected it. But this means the scores (3/10 on failure probability) were generated by out-of-scope concerns that the DA could not translate into in-scope recommendations with appropriate urgency.

The synthesis resolved this correctly by flagging customer discovery as meta-finding. But the tension between scores (alarming) and technical recommendations (constructive and bounded) was never explicitly named as a scope artifact.

---

## Part 5: Confidence Calibration

### The External Researcher: High stated confidence, high evidence quality — well calibrated

The External Researcher cited primary sources for nearly every claim. Their evidence quality scores were consistently high (8-10/10) and their confidence in the derived recommendations appears proportionate. The challenge round revealed one miscalibration: the Signet 10/10 relevance score was stated with high confidence but later adjusted when the DA correctly identified that the LLM-decay lesson was counterproductive. That adjustment was appropriate. Overall, the External Researcher's confidence tracked their evidence quality more closely than either other agent.

---

### The Codebase Analyst: Confidence calibrated to the code, miscalibrated to sociotechnical outcomes

The Codebase Analyst's confidence is explicitly technical and well-supported by code citations. But their characterization of `trust_metadata` as a "free upgrade" represents confidence that exceeds the evidence. The evidence shows the column exists and a write method exists. The confidence implies the enrichment data will be meaningful once populated. The gap between "column exists" (evidence) and "enrichment data will be meaningful" (implication) is exactly the semantic feasibility gap the Orchestrator identified at ~5/10.

This is a systematic pattern in the Codebase Analyst's report: their confidence is calibrated to code completeness, not to whether the code, once extended, will produce meaningful signals. The two are correlated but not identical.

---

### The Devil's Advocate: Confidence lower than evidence quality on technical claims, higher than evidence quality on strategic claims

The DA rated Failure Probability at 3/10 (effectively saying failure is likely). But their evidence for the gaming attacks is the code itself — and the code demonstrates that the attacks work. For the technical failure modes, the evidence quality is high and the confidence is appropriately alarming.

For the strategic failure mode ("businesses will pay" is unverified), the DA's evidence is the absence of customer conversations — not evidence that businesses won't pay. A Failure Probability of 3/10 based on an absence of evidence is more confident than the evidence supports. The correct characterization is "unknown probability" — which is uncomfortable but accurate. Rating it 3/10 implies an estimate below 50%, which requires positive evidence of likely failure that the DA does not have.

The DA's most important finding (customer discovery) rests on the weakest epistemic foundation: the absence of data. Their most alarmist score (3/10 Failure Probability) is calibrated correctly for the technical attacks (we have positive evidence these work) and miscalibrated for the business model question (we have no data either way).

---

## Part 6: Findings the Scores Should Have Produced But Didn't

### Finding 1: The "reporter accuracy tracking" recommendation creates a second reputation system that was not scoped, scored, or designed.

The External Researcher proposed in the challenge round that Submantle should track reporter accuracy — if a reporter files 50 incidents and 40 are disputed, their weight decreases. The synthesis adopted this recommendation (Tier 1, 1a: "Track reporter accuracy over time").

This is a second Beta-style reputation system. Reporters accumulate a score based on how many of their incident reports are verified versus disputed. This score affects how much weight their reports carry in the agent formula.

No agent scored the feasibility of building this. No agent specified the formula. No agent analyzed the blast radius of having a nested reputation system in which a reporter's score affects an agent's score. The synthesis presents this as a component of the Tier 1 "ship-blocker" fix.

The council produced a recommendation for a system it didn't research. The scores nowhere reflect that Tier 1 includes an unanalyzed sub-system.

---

### Finding 2: The triple convergence on "unauthenticated incident reporting is the top priority" produced false precision.

All three agents independently identified unauthenticated incident reporting as the most critical vulnerability. The synthesis correctly called this "high confidence." But the three agents identified three different problems:

- Codebase Analyst: a missing `reporter_verified` BOOLEAN column
- External Researcher: missing credentialed furnisher architecture (contractual liability, not just a token)
- Devil's Advocate: a live attack vector that can zero out any agent's score in 60 seconds

These are different problems at different layers. The Codebase Analyst's fix (add a column and a token check) does not produce the External Researcher's credentialed furnisher model. The External Researcher's fix (require reporter registration with terms-of-service acceptance) does not solve the DA's attack vector unless registration is enforced in real-time before any report is accepted.

The convergence on "reporter authentication is critical" masked the divergence on "what authentication actually means." The synthesis adopted all three framings simultaneously without specifying which implementation satisfies all three. The recommendation is: "Require reporter registration with verified identity before accepting incident reports." But "verified identity" is undefined. A token is not verified identity. A terms-of-service checkbox is not verified identity. Legal accountability is verified identity. The recommendation is more confident than the council's deliberation supports.

---

### Finding 3: The enforcement boundary debate was resolved by terminology, not principle.

The External Researcher argued: "Never unregister for bad behavior."
The Devil's Advocate argued: "Never is the wrong word; rarely with procedure for identity fraud."
The Orchestrator resolved: "Submantle withdraws attestations; it does not deregister, suspend, or quarantine."

This is a terminological resolution. The underlying question — "if someone registers 'anthropic-claude-official' to impersonate Anthropic, what does Submantle do?" — was not answered. "Withdraw attestation" is only applicable if Submantle previously issued a "Verified" attestation to the impersonator — which it would not do for an unverified agent. Declining to issue an attestation is not an action; it is a default.

The impersonation case requires Submantle to do something active, not merely decline to do something. Every agent model the council examined — CAs, DNS registrars, Visa — has a mechanism for responding to active impersonation. The council concluded Submantle should not have such a mechanism. This may be the right conclusion. But the reasoning that produced it (CA revocation analogy) does not apply to the specific case the Devil's Advocate raised.

The enforcement debate was resolved by excluding the hardest case.

---

### Finding 4: The synthesis deferred "score decay / temporal trust" without acknowledging its connection to the credit bureau model's own design.

Credit bureaus retain negative items for 7 years, then remove them. This is a form of temporal decay — not mathematical decay of the score, but mandatory expiration of negative evidence. The External Researcher's highest-relevance source (credit bureaus, 9/10) has a built-in time-based mechanism that the council's recommended scoring model does not include.

The Devil's Advocate raised score decay. No other agent addressed it. The synthesis flagged it as "unresolved — design decision for future."

But the question is not just a design decision — it is a gap between the recommended model and the model's highest-relevance analogue. A credit bureau that retained negative information permanently would violate FCRA. The council's recommended scoring model retains incident reports permanently with no decay or expiration mechanism. This is not an oversight in the scoring model; it may be the right call for V1. But the tension between "credit bureaus are our model" (9/10 relevance) and "our model lacks the credit bureau's mandatory expiration mechanism" was never named.

---

## Summary: The Five Core Tensions

These are the tensions the council produced but did not resolve. They are not failures of the council. They are the live questions that remain after the deliberation.

**Tension 1: Technical feasibility (8/10) versus semantic feasibility (~5/10)**
The codebase can be enriched. It is uncertain whether the enriched model will produce signals businesses will pay for. Every Tier 1 recommendation sits on top of this unresolved gap. The Orchestrator named it correctly. No one gave it a home.

**Tension 2: "Reporter accuracy tracking" is a Tier 1 recommendation for an undesigned second reputation system**
The council recommended building a reporter accuracy score without scoping, scoring, or designing it. The risk scores that drove Tier 1 urgency apply to the reporter authentication layer. They may not apply to the reporter scoring sub-system, which is a different problem at a different layer.

**Tension 3: "Never enforce" is resolved by terminology**
Withdrawing attestations, declining to issue badges, and maintaining a low score are the council's substitutes for enforcement. These substitutes work against behavioral misconduct. They do not work against active impersonation. The DA's hardest case was excluded from the resolution.

**Tension 4: Triple convergence on "unauthenticated reporting" masked three different implementations**
The council agreed on the problem but produced three different implied solutions. The synthesis adopted all three without specifying which implementation satisfies all three requirements. "Verified identity" is undefined.

**Tension 5: The highest-confidence strategic finding (customer discovery) was filed outside scope**
The Devil's Advocate's two lowest scores (Failure Probability 3/10, Assumption Fragility 3/10) were driven by the unverified business model assumption. The council deferred this as "outside scoring model scope." The synthesis called it "the most strategically important finding in the entire council" and then treated it as advisory. The scores say it should block or at minimum run parallel to the technical work. The framing says it is important but separable. The framing is easier to act on. That may be why it won.

---

*Filed by: Tension Analyst, Research Council*
*Phase 5 — Date: 2026-03-12*
