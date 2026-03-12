# Devil's Advocate Challenge — Scoring Model Council
## Date: 2026-03-12
## Phase: 2 (Cross-Council Review)
## Authored by: Devil's Advocate

---

## Preface

I have read both the Codebase Analyst findings and the External Researcher findings in full. My challenge below is structured as ordered by the task brief: divergence points first, then score disagreements, evidence gaps, agreements, and surprises. I will be specific. Vague challenges are worthless.

---

## 1. Reasoning Divergence Points

These are the places where I arrive at a different conclusion from one or both of the other agents — and where the divergence in the reasoning chain begins.

---

### Divergence A: The Codebase Analyst's "trust_metadata is a free upgrade" conclusion

**Codebase Analyst claim:** The existing `trust_metadata` JSON column "could hold interaction_breakdown, incident_breakdown, velocity_flags, score_history" and is described as a "recommendation: display-only enrichment, never authoritative formula input."

**Where the reasoning diverges:** The Codebase Analyst is correct that the column exists and is unused. The divergence is in what "display-only enrichment" means in practice. If that metadata is displayed on the trust scorecard — even as supplementary data — it becomes part of the signal that brands use to make decisions. A brand that sees `velocity_flags: [excessive_self_query]` next to a trust score of 0.97 will discount that score. The "authoritative formula input" vs. "display enrichment" distinction is technically meaningful but commercially irrelevant. Once data is visible, it is load-bearing.

**The deeper divergence:** Populating `trust_metadata` with velocity flags requires *detecting* velocity anomalies — which requires logic that is absent from the current system. The Analyst describes this as a "free upgrade." It is not free; it requires implementing the anti-gaming detection layer that currently does not exist. The column is free. The detection logic is not.

---

### Divergence B: External Researcher's conclusion on Signet's "LLM-swap decay rule"

**External Researcher claim:** Signet applies a 25% trust decay on model change, and this identifies a "version/model-swap gap" in Submantle's architecture. The Researcher scores Signet relevance at 10/10.

**Where the reasoning diverges:** The Researcher identifies the gap correctly but the proposed framing is wrong. Signet's 25% decay on model change treats the model as co-constitutive of the agent identity — which contradicts Submantle's design principle that trust belongs to the *registered software entity*, not the model. Applying model-swap decay in Submantle would mean Anthropic's Claude loses trust every time it upgrades — which is precisely backwards from how software product trust should accumulate. The gap the Researcher identified is real (agents can rename to escape bad scores), but the Signet solution would create the wrong incentive: punish legitimate upgrades.

**My divergent conclusion:** The correct fix for the version/model-swap gap is name-locking and canonical identity (did:web anchored to a verified domain), not score decay on model change. The gap is real; the Signet solution applied uncritically would be harmful.

---

### Divergence C: Both agents treat authentication on incident reporting as a "gap to close" rather than a "ship-blocker"

**Codebase Analyst position:** Lists "No reporter authentication at API layer" as the most critical gap in the `incident_reports` table. Scores Failure Probability implicitly at manageable levels given an 8/10 Feasibility score.

**External Researcher position:** Lists "Anonymous incident reports are gameable — credentialed reporters needed" as recommendation #2, after "not all interactions are equal."

**My divergent position:** Both agents frame this as a gap in a list of gaps. I frame it as the *only thing that determines whether trust scores mean anything at all*. This is not a feature gap; it is a foundational broken assumption. The credit bureau model the External Researcher documents at length *requires credentialed data furnishers*. Without them, you do not have a credit bureau; you have a public message board where anyone can post defamatory content about any agent. The divergence is in priority weight, not in identification. Both agents found it. Neither escalated it appropriately.

---

### Divergence D: External Researcher's enforcement conclusion vs. my enforcement analysis

**External Researcher conclusion:** "Submantle should never unregister for bad behavior. Score, expose, let brands decide. Allow dispute of inaccurate data."

**Where the reasoning diverges:** The Researcher reaches this conclusion by analogy to credit bureaus (cannot remove accurate negative info) and certificate authorities (revoke attestations, not entities). Both analogies are partially correct but incomplete. My analysis shows that DNS registrars *do* terminate accounts for phishing, that Visa maintains the MATCH list which is a de facto permanent blacklist, and that CAs revoke certificates within 24 hours for abuse. Every durable neutral infrastructure example the Researcher cites includes a floor of procedurally bounded enforcement that the Researcher then does not include in their conclusion.

**The precise divergence:** The Researcher uses the word "never" in their enforcement conclusion. I conclude "never" is the wrong word. The correct conclusion is "rarely, with procedure, and only for identity fraud or infrastructure abuse" — not "never." This matters because the absolutist "never" position creates a public goods problem: if Submantle cannot respond to an agent registered as "anthropic-claude-official" that is not Anthropic's agent, the system has no defense against identity fraud. The External Researcher's own Signet finding — LLM-swap gap, identity verification — points toward this problem without resolving it.

---

## 2. Score Challenges

### Challenge 1: Codebase Analyst Feasibility — 8/10

**The Analyst's score:** Feasibility 8/10.

**My challenge:** This score applies to *enriching the scoring model* — and technically, it is probably correct. The code changes required are bounded and reversible. What the score does not capture is the feasibility of making the enriched scoring model *mean something*. Technical feasibility and semantic feasibility are different dimensions. It is highly feasible to add 5 new schema fields to `incident_reports`. It is not highly feasible to make those fields produce trustworthy data without reporter credentialing, dispute mechanisms, and velocity detection — none of which exist. The 8/10 Feasibility score is correct for the code change. It overstates the feasibility of the *outcome*.

### Challenge 2: Codebase Analyst Reversibility — 6/10

**The Analyst's score:** Reversibility 6/10, with the note that "structural changes require schema migrations and API changes but are bounded."

**My challenge:** I would score this lower — 4/10 — specifically for the incident reporting authentication change. Once you ship authenticated incident reporting to real reporter partners (credentialed organizations), reversing to unauthenticated reporting is not a schema migration; it is a breach of the agreement those partners signed. The migration path is bounded. The relationship path is not. The Analyst's 6/10 treats reversibility as a technical property when it is also a contractual property once real partners are involved.

### Challenge 3: External Researcher Signet Relevance — 10/10

**The Researcher's score:** Signet relevance 10/10.

**My challenge:** 7/10. Signet is the most architecturally analogous competitor, which earns high relevance. But three of Signet's five weighted dimensions are defined by what agents *say about themselves* through an SDK integration — which is self-reported, not independently observed. Submantle's OS-level observation is architecturally superior to Signet's self-reporting model for exactly this reason. Signet is highly relevant as a market comparator but the Researcher's conclusion ("this identifies a version/model-swap gap in Submantle") requires evaluating Signet's design choices critically, not adopting them. 10/10 overstates analytical relevance when two of the key lessons (SDK-reported signals, LLM-swap decay) are lessons in what *not* to copy.

### Challenge 4: External Researcher NIST AI RMF Relevance — 6/10

**The Researcher's score:** NIST AI RMF relevance 6/10, "useful for sales narrative."

**My challenge:** 8/10 for a different reason the Researcher underweights. NIST AI RMF is relevant not because of its technical content but because large enterprise customers — the ones who would pay for Submantle at volume — will use NIST AI RMF compliance as a procurement criterion. Being able to map Submantle's architecture to NIST AI RMF language is not "sales narrative fluff"; it is a procurement gate. The Researcher correctly identifies that NIST is not a scoring protocol, but underweights its commercial relevance as a compliance mapping tool.

---

## 3. Evidence Gaps

### Gap A: Neither agent addresses the cold start problem in depth

My findings document three dimensions of the cold start problem:

1. New agents start at 0.5 ("unknown") — which is indistinguishable from a legitimate agent at exactly average trust
2. A malicious agent can inflate its score *before* deploying maliciously — making the cold start worse for legitimate agents (who arrive fresh) than for bad actors (who prepare)
3. The eBay "feedback farm" pattern (build score on small transactions, then abuse the reputation) is a direct analog

The Codebase Analyst acknowledges that "every new agent starts unknown" in the trust initialization but does not surface the perverse incentive: the cold start problem favors pre-staging by bad actors. The External Researcher discusses eBay/Airbnb cold start solutions but does not connect them to Submantle's specific implementation gap. Neither agent addresses the question of whether "New, unscored" should be a visually distinct state from "Average trust, score=0.5."

### Gap B: Neither agent addresses score decay / temporal trust

A trust score based on historical query count does not decay over time. My findings document two failure modes that the other agents do not cover:

1. **Stale signal:** An agent that was trustworthy for 2 years and then gets compromised retains its high score until third parties file incident reports — which under the credit bureau model requires external parties to notice, attribute, and report. High-reputation compromised agents are more dangerous than unknown agents.
2. **Score permanence asymmetry:** Incidents can accumulate indefinitely. A legitimate agent that had one bad incident 3 years ago cannot clear that incident from its record. Credit bureaus have mandatory data retention limits (7 years for most derogatory items under FCRA). Submantle has no time-based decay or retention policy.

### Gap C: Codebase Analyst does not address the deregister/reregister identity escape in depth

The Analyst notes: "Deregister/reregister gap: Hard DELETE wipes all history. Counters reset to zero." This is listed as a gap but not analyzed as a critical threat. My findings frame this as the agent-scoring equivalent of the synthetic identity fraud pattern — agents build score, then "bust out" by deregistering their tarnished identity and re-registering under a new name. This is not a minor schema gap; it is the primary mechanism by which a sophisticated attacker would neutralize the entire scoring model.

### Gap D: External Researcher does not address the Mastercard Verifiable Intent relationship beyond "complementary"

The Researcher notes Mastercard Verifiable Intent is "complementary, not competitive — 'Was this authorized?' vs. 'has this agent behaved well?'" This is correct but undersells the strategic implication. If Mastercard Verifiable Intent becomes a standard (they have the network to make it one), Submantle needs a clear answer to "how do Verifiable Intent signals feed into Submantle's trust score?" A future integration where authorized+verifiable intents count as higher-quality query signals than anonymous pings is a natural architectural extension. The Researcher identifies the relationship but doesn't map the integration path.

---

## 4. Agreements — High-Confidence Findings

Where independent analysis converged, the findings are high-confidence. All three agents independently reached the following conclusions:

**Agreement 1: Unauthenticated incident reporting is the most critical vulnerability.**
All three analyses — my assessment (live attack vector, CRITICAL severity), Codebase Analyst (most critical missing field: reporter_verified BOOLEAN), External Researcher (recommendation #2: credentialed reporters needed) — independently prioritize this as the top structural gap. This is not debatable. It is confirmed.

**Agreement 2: One score is correct for V1.**
My findings verify this via Klout failure case. External Researcher verifies via eBay/Airbnb/FICO historical precedent. Codebase Analyst implicitly confirms by documenting that enrichment goes into trust_metadata (display) rather than the formula (authoritative). Three independent paths to the same conclusion: one score, complexity after product-market fit.

**Agreement 3: The Beta formula math is sound; the inputs are the problem.**
My findings: "sound instrument pointed at imprecise target." External Researcher: sufficient metadata identified (query count, timestamp, category, incident type). Codebase Analyst: formula is a one-function implementation. All three agree the formula is not the bottleneck. The bottleneck is input quality, specifically incident report credibility.

**Agreement 4: A dispute mechanism is required.**
My findings: "agents can contest incident reports" as part of the enforcement middle ground. External Researcher: "Dispute mechanism missing and legally necessary." Codebase Analyst: no dispute mechanism currently exists. Three-way convergence that this is not optional for a production system.

**Agreement 5: The enforcement question requires a nuanced answer, not a binary.**
My findings argue for a procedurally bounded enforcement floor. External Researcher argues for "score, expose, let brands decide, allow dispute." Codebase Analyst implies soft enforcement via agent_status column rather than hard delete. The convergence is that "never enforce" and "enforce freely" are both wrong; the middle path is structured dispute and minimum-necessary response.

---

## 5. Surprises — What Changed My Thinking

**Surprise 1: The trust_metadata column already exists.**

I did not know this before reading the Codebase Analyst's findings. This materially changes the enrichment timeline. Velocity flags and interaction breakdowns can be stored *today* with zero schema migration — only detection logic is missing. This shifts my priority estimate: the missing piece is the detection logic, not the storage layer. I would revise my Phase 1 assessment to distinguish "schema ready" from "logic ready" more explicitly.

**Surprise 2: The Codebase Analyst's blast radius analysis is more optimistic than I expected — and probably correct.**

I expected the scoring model enrichment to have higher blast radius given the interconnected nature of trust computation. The Analyst's finding that only one test breaks (two-line fix) on weighted scoring, and that trust_metadata is already in the schema, suggests the actual code changes are more contained than I modeled. I maintain my position that the *sociotechnical* blast radius (getting reporter credentialing right, establishing dispute mechanisms) is high. But the *code* blast radius appears to be genuinely low. This is a useful distinction.

**Surprise 3: The External Researcher found that ZKP is "future-state" and current architecture is "already privacy-preserving by construction."**

This validates the current approach more strongly than I expected. I had assumed the privacy/scoring tension I identified (you need to know *what* the agent did to score meaningfully, which requires content the privacy model doesn't capture) would require explicit architectural resolution. The Researcher's finding that the current architecture is privacy-preserving by construction is correct — but it does not resolve the tension I identified. It means Submantle has chosen the privacy-preserving side of that tradeoff by default, which is the right call, but should be acknowledged explicitly as a tradeoff rather than assumed to be a free win.

**Surprise 4: Mastercard Verifiable Intent is already in market.**

The External Researcher's finding that Mastercard Verifiable Intent is "in market" and complementary — rather than competitive or future-state — changes the competitive urgency calculation. If Mastercard is already asking "was this authorized?", the market is ready to hear "was this trustworthy over time?" The timing is better than I assumed from my Phase 1 research alone.

---

## Summary Judgment

The three agents' findings are more convergent than divergent. The critical divergences are:

1. **Priority weight on unauthenticated incident reporting:** I maintain this is a ship-blocker, not a gap in a list. The other agents found it; neither escalated it to the right level.
2. **The enforcement "never" vs. "rarely with procedure" distinction:** The External Researcher's absolutist "never unregister" conclusion is not supported by the infrastructure precedents they themselves cite.
3. **Cold start and score decay are underweighted by both agents:** These are not edge cases; they are the primary mechanism by which sophisticated attackers will neutralize the system over time.
4. **Signet's LLM-swap decay rule should not be adopted uncritically:** It contradicts Submantle's identity model and would punish legitimate software upgrades.

The high-confidence findings (reporter credentialing, single score, dispute mechanism, Beta formula soundness) should be treated as resolved by this council. The divergences above are the live questions requiring a Tension Analyst to synthesize.

---

*Filed by: Devil's Advocate, Research Council*
*Phase 2 Challenge — Date: 2026-03-12*
