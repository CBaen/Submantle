# External Researcher Challenge — Scoring Model Council
## Date: 2026-03-12
## Challenging: Codebase Analyst Findings + Devil's Advocate Findings

---

## Framing

I read both sets of findings after completing my external research independently. The challenge below is structured around where reasoning chains diverge, not just where conclusions differ. Vague disagreement is worthless — I cite exact claims, scores, and lines.

---

## 1. Reasoning Divergence Points

### Divergence A: The Deregister/Reregister Gap — We Reach Different Destinations via Different Routes

**Codebase Analyst** identifies the deregister gap as a problem: "deregister_agent() does a hard DELETE. All history gone. incident_reports rows remain but counters reset." Their proposed fix: `agent_status` column (active/suspended/blacklisted) rather than hard deletion.

**My external research reaches a stronger conclusion via a different path.** The credit bureau model makes this unambiguous: bureaus cannot remove accurate negative information before its legal retention period. The FCRA framework exists precisely because data subjects have incentives to erase negative history. An agent with a history of incidents should not be able to wipe that history by deregistering. The Codebase Analyst's `agent_status` column is the right mechanism, but the reasoning behind it matters — this is not just a data hygiene fix, it is a **structural neutrality requirement**. Submantle that allows history wipes is not a bureau; it is a reputation laundry service.

**Where the reasoning chains diverge:** The Codebase Analyst frames this as a practical implementation gap. My external research frames it as a design principle violation with legal and competitive implications. The destination is the same; the urgency and framing differ. The Codebase Analyst gives this 6/10 on reversibility. I would rate the reversibility of NOT fixing this at 3/10 — once Submantle allows reputation resets, you cannot credibly claim bureau status to enterprise customers who know what credit bureaus actually do.

---

### Divergence B: Reporter Authentication — We Agree It's Critical, but I Have a More Specific Fix

Both the Codebase Analyst and Devil's Advocate correctly identify unauthenticated incident reporting as a critical gap. The Codebase Analyst notes: "No reporter authentication at API layer." The Devil's Advocate calls it "a certainty of abuse."

**My finding adds specificity:** The credit bureau's credentialed-reporter model is not just "require authentication." It has a structural consequence the other two do not name: **reporters must have skin in the game**. eBay's documented experience shows that once reporters bear no cost for false reports, strategic abuse follows. The credit bureau's design inversion — you cannot join unless you are a verified lender — means that false reporting reflects back on the reporter's own credibility.

**The concrete fix** that neither finding surfaces: Submantle should track a **reporter accuracy score** alongside the agent score. If reporter X files 50 incidents and 40 are disputed and unverifiable, reporter X's weight in the formula should decrease. This is the mechanism that makes the system self-correcting rather than just authenticated. Authentication alone stops anonymous abuse; reporter scoring stops credentialed abuse.

**Where the reasoning chains diverge:** The Codebase Analyst treats this as a missing API guard. My external research treats it as a missing system property. The fix for the property is different from the fix for the guard.

---

### Divergence C: The "Neutral Infrastructure Has an Enforcement Floor" Question

The Devil's Advocate states: "Every durable neutral infrastructure maintains minimal enforcement." and proposes: "quarantine don't delete, dispute channel, emergency termination for identity fraud only."

**My external research produces a more precise answer than "minimal enforcement."** I examined four neutral infrastructure types:

1. DNS registrars (ICANN/UDRP): act on third-party evidence with defined process. No proactive detection.
2. Certificate Authorities: revoke their own attestations — not the entity's right to exist. The agent continues to function.
3. Payment networks (Visa/Mastercard): fine acquiring banks, not merchants directly. Two layers removed.
4. Credit bureaus: cannot remove accurate negative data. Dispute process for inaccurate data only.

**The pattern is precise:** Neutral infrastructure does NOT enforce behavior. It can (1) withdraw its own attestations, (2) record evidence provided by third parties, and (3) maintain a dispute process. It never blocks, deactivates, or quarantines the entity itself.

**Where I diverge from the Devil's Advocate:** The DA's "quarantine don't delete" and "emergency termination for identity fraud only" are enforcement actions — they affect the agent's ability to operate, not just Submantle's attestation. A CA that revokes a certificate is not blocking the website from running; the website just loses the CA's endorsement. If Submantle quarantines an agent, it is acting as a regulator, not a bureau. The correct answer is: Submantle withdraws its "Verified" badge / stops issuing attestations for a flagged agent. The agent continues to exist in the registry with a low score. Brands decide what to do with that.

**Concretely:** The only legitimate Submantle-initiated action is withdrawing its own attestations and updating the score. Not quarantine. Not suspension. Not termination.

---

### Divergence D: The Version/Model-Swap Gap — My Finding Is More Specific

The Codebase Analyst does not address version continuity at all. The Devil's Advocate does not address it. My external research surfaces this via Signet's LLM-swap decay rule: Signet applies a 25% score decay when an agent changes its model, then lets the score rebuild.

**Submantle currently has no answer to this.** The score is keyed to `agent_name`. An agent that accumulates a 0.1 score can rename itself — new name, fresh 0.5 start. The `author` field provides partial protection (same author, different name), but it is not enforced.

**My proposed mechanism is different from Signet's:** Signet decays the score on model swap (same agent, worse score temporarily). Submantle's approach should be via the `author` field — when an agent registers, Submantle checks whether the author has other registered agents and surfaces that relationship to brands. This does not prevent re-registration, but it makes the relationship queryable. Brands can decide: "author X has three agents, two of which have low scores — I'll apply a discount to this new one."

This is additive intelligence (new endpoint, no formula change) that preserves neutrality without enforcement.

---

## 2. Score Challenges

### Challenge: Codebase Analyst's Reversibility Score of 6/10

The Codebase Analyst rates Reversibility at 6/10 with the note "Formula changes affect all historical scores."

**I challenge this as underestimated for certain changes, overestimated for others.**

- For adding weighted interaction types to the formula: 4/10 reversibility, not 6/10. Once you differentiate query types, all historical queries lose their type context. You cannot retroactively categorize them. Old queries remain equal-weight forever. This is a one-way door.
- For the `agent_status` column: 8/10 reversibility. A soft status column is easier to roll back than a formula change.
- For fixing the deregister behavior: 9/10 reversibility going forward, but 0/10 retroactively. You cannot restore deleted history.

The Codebase Analyst's single Reversibility score obscures that different changes have radically different reversibility profiles. The council should not treat these as equivalent.

---

### Challenge: Devil's Advocate Failure Probability Score of 3/10

The DA rates Failure Probability at 3 (low, indicating high probability of failure) with the justification "Unauthenticated reporting is certainty of abuse."

**The score of 3/10 is correct but the reasoning needs precision.** Unauthenticated reporting is not just "certainty of abuse" — it is **specifically certainty of structured competitive abuse once Submantle has any market traction.** The threat model is not random vandals; it is sophisticated actors (competitors, disgruntled customers, malicious agents) who will discover that filing false incident reports is free.

The DA's score is right. My challenge is about the mechanism of failure: it scales with Submantle's success, not its current state. At zero users, reporter auth is irrelevant. At 10 enterprise customers, it becomes a liability. At 100, it becomes an existential vulnerability. This is a delayed fuse, not an immediate crisis — which makes it more dangerous because it won't feel urgent until it's too late to fix structurally.

---

### Challenge: Codebase Analyst's "Pattern Consistency" Score of 8/10

The Codebase Analyst rates Pattern Consistency at 8/10: "Additive changes fit existing pattern."

**This misses that some proposed changes are NOT additive.** Adding weighted query types changes the formula semantics. The existing pattern is: every query counts once. A weighted query model is not that pattern — it is a different model. If `compute_trust()` now weights a "device_list" query at 3x a health-check ping, that is a new semantic layer on top of an existing function. The pattern changes.

I would rate Pattern Consistency at 6/10 for the weighted-queries change specifically, with 8/10 only for purely additive changes (new columns, new endpoints that don't touch the formula).

---

## 3. Evidence Gaps

### Gap A: The Dispute Mechanism — Neither Analyst Names the Legal Dimension

Both analysts identify the missing dispute mechanism as a gap. Neither names the legal dimension.

The Fair Credit Reporting Act (US) and GDPR Article 17 (EU) both require that inaccurate data be correctable. Submantle is not yet subject to these laws, but the moment it processes data about entities that operate in the EU or US at any scale, the dispute mechanism is not a nice-to-have — it is a compliance requirement. The fact that Submantle stores incident reports about named agents makes it a data processor. GDPR applies to processors even when they are not in the EU if the data subjects (agents) are operating on behalf of EU users.

**My finding:** Submantle should build the dispute endpoint before it has its first enterprise customer, not after. Once a customer relies on Submantle's incident data for real access decisions, the liability of having no dispute process crystallizes.

---

### Gap B: The Mastercard Verifiable Intent Architectural Complement

Neither the Codebase Analyst nor the Devil's Advocate addresses Mastercard Verifiable Intent (released March 5, 2026). This is an external development both would miss by design — it is not in the codebase.

**The relevance:** Enterprise customers evaluating agent trust will encounter both Verifiable Intent and Submantle. These are not competitors — they answer different questions (was this action authorized vs. does this agent have a good history?). But Submantle's sales team will be asked "how do you compare to Verifiable Intent?" The correct answer is "we're complementary," and Submantle should be able to demonstrate that.

**The architectural implication:** Verifiable Intent uses Selective Disclosure — brands see confirmation without seeing the underlying instruction. Submantle should adopt the same principle: `/api/verify/{agent_name}` returns score + confidence interval, not the incident list. Brands get the signal without the underlying data. The current implementation already does this (compute_trust() returns the score, not the raw incident data). That alignment should be documented as intentional, not accidental.

---

### Gap C: The Cold Start Problem — My Research Has a More Specific Answer

The Devil's Advocate flags cold start (0.5 = "commercially useless") as a gap. Neither analyst names the fix.

**My external research surfaces the specific mechanism:** Credit bureaus do not start new accounts at 0. They start at "no history" — which is a distinct state from a bad score. Lenders treat "no history" differently from "bad history." A first-time borrower gets a different offer than someone with defaults.

**The Submantle fix:** The API response for an unregistered or newly-registered agent should return `status: "no_history"` (or equivalent), not `trust_score: 0.5`. The 0.5 Beta prior is a correct mathematical initialization — internally. But the API consumer should know whether they're seeing "genuinely unknown" vs. "score with evidence." The difference matters for access decisions.

This is a two-line API change and a documentation update. It is not a formula change. The DA identified the symptom; this is the fix.

---

### Gap D: Signet as a Direct Competitor

The Codebase Analyst does not analyze Signet at all — they cannot, as it is not in the codebase. The Devil's Advocate does not mention Signet.

**Signet (agentsignet.com) is the closest direct competitor and is already live.** Key facts:
- Composite trust score 0–1000 from five dimensions (Reliability 30%, Quality 25%, Financial 20%, Security 15%, Stability 10%)
- Persistent cross-platform SID. Currently free.
- LLM-swap decay rule: 25% score decay on model change, then rebuilds

**Strategic implications the other analysts cannot see:** Signet's five dimensions require subjective assessment. Submantle's Beta formula is fully deterministic. These are different bets. Signet will face the same EU AI Act questions Submantle is designed to avoid — subjective multi-dimensional scoring may qualify as consequential automated decision-making under Article 22. Submantle's deterministic formula is specifically designed to stay outside that scope. This is a competitive advantage neither analyst documents because neither has the competitive intelligence.

---

## 4. Agreements — High-Confidence Convergences

These are the findings that survive all three independent analyses. Treat them as the highest-confidence signals.

**1. Unauthenticated incident reporting is the most urgent structural gap.**
All three analysts reached this independently. I arrived via credit bureau precedent + eBay gaming history. The Codebase Analyst found it in the code. The Devil's Advocate stress-tested the assumption. Triple convergence. Fix this before shipping to any real customer.

**2. The deregister behavior is wrong as designed.**
I arrived via credit bureau legal requirements. The Codebase Analyst found the hard DELETE in database.py. Double convergence on mechanism; triple convergence on the problem. The Codebase Analyst's `agent_status` column is the correct fix.

**3. A single universal score is correct for V1.**
The Devil's Advocate verified this directly. My eBay and Signet research confirms: Klout's complexity killed it; Signet's five dimensions are a liability; one number is the right starting point. Every durable reputation system launched with one signal. Triple implied convergence.

**4. Score computation should be read-only and on-demand.**
The Codebase Analyst documents this is how it works now. My external research confirms this matches the FICO architecture (FICO computes on demand from stored bureau data — the score is not stored). The current architecture is correct. Do not change it.

**5. The `trust_metadata` JSON column is the right place for enrichment data.**
The Codebase Analyst identifies this as unused but well-positioned. My research confirms this maps to credit bureau "metadata" that informs scoring without changing the authoritative counter. Use it for display-only enrichment (velocity flags, interaction breakdown) — never as authoritative formula input. This distinction is important: the formula inputs must remain auditable; display-only data can be richer.

---

## 5. Surprises — What Changed My Thinking

### Surprise A: The Blast Radius of Formula Changes Is More Severe Than I Anticipated

My external research focused on what SHOULD be in the scoring model (interaction differentiation, reporter credentialing, etc.). Reading the Codebase Analyst's blast radius analysis changed my weighting.

Their finding: "Old queries remain equal-weight forever (no migration path)" for interaction-type weighting is correct and consequential. I was prepared to recommend weighted queries as an improvement. After reading this, I downgrade that recommendation to "design decision for Go production rewrite, not prototype change." The prototype should add the `interaction_type` field to the API and database but NOT change the formula — collect the data now, weight it later when you can migrate cleanly.

**This is a change in my concrete recommendation.** Before reading the Codebase Analyst: add weighted queries. After: add the `interaction_type` column as a data collection hook, leave the formula unchanged.

---

### Surprise B: The `trust_metadata` Column Is a Better Investment Than I Thought

I had not identified the `trust_metadata` JSON blob as an unused column. The Codebase Analyst's observation that this column exists, a write method exists, and nothing uses it is a significant finding.

This column can absorb interaction_breakdown, velocity_flags, and reporter_accuracy data without a schema migration. If I had written recommendations before seeing this, I would have proposed a new table. The existing column is better — no migration, no schema change, backwards compatible.

**This changes my recommendations on implementation sequence.** Use `trust_metadata` as the home for enrichment data in V1. Reserve new table creation for the Go rewrite.

---

### Surprise C: The Devil's Advocate's "Customer Discovery Must Precede Dashboard Work" Is Correct and Underweighted

The DA's Priority Finding #5 is: "Customer discovery must precede dashboard work." This is listed last among five priorities but is actually the most strategically critical finding in any of the three analyses.

None of Submantle's scoring model improvements matter if the fundamental business assumption — that brands will pay for trust scores — is unverified. The DA gives this medium weighting. I would give it maximum weighting.

**My external research context:** The Signet competitor is already live and free. The window is 12–18 months per CLAUDE.md. A scoring model that is architecturally correct but built for an unverified customer is a scoring model built in a vacuum. The council should surface this to Guiding Light: all the technical work is bounded by whether anyone will buy it.

This does not mean stop building — it means the next customer conversation is a higher priority than the next scoring model feature.

---

## Summary: Ranked Challenges for Council Synthesis

1. The enforcement boundary question needs a sharper answer than "minimal enforcement." Neutral infrastructure withdraws its own attestations; it does not quarantine agents. The Devil's Advocate's "quarantine" recommendation crosses the line.
2. Reporter authentication requires reporter scoring, not just registration. Authentication alone is insufficient.
3. The deregister behavior must change before any customer is onboarded. This is a design principle violation, not just a practical gap.
4. Add `interaction_type` as a data collection hook now; do NOT weight it in the formula until the Go rewrite allows a clean migration.
5. The dispute mechanism has a legal dimension neither analyst names. Build it before the first enterprise customer.
6. "No history" and "0.5 score" must be distinguishable in the API response. This is a two-line change with disproportionate business value.
7. Customer discovery is the highest-priority finding no one wants to rank first. It should be.

---

*External Researcher — Research Council, Scoring Model*
*2026-03-12*
