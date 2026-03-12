# Team 3 Findings: Review Tiers and Incident Processing
## Date: 2026-03-12
## Researcher: Team Member 3

---

## Current State Assessment (Before External Research)

The codebase has a critical gap: `record_incident()` in `agent_registry.py` immediately calls `increment_agent_incidents()` on the same transaction. There is no pending state, no deduplication, no review tier. A single bad actor can register 100 fake agents, generate interaction IDs, file 100 reports against a target, and that target's trust score collapses to 0.0097 before any human can respond. The `incident_reports` table has no `status` column, no `reviewed_by` column, no `dedup_group_id` column, no `severity` column.

The research brief has already settled: pending state is required, eBay model is the framework, deterministic rules only. This research provides the evidence base for exactly *how* to implement those settled decisions.

---

## Battle-Tested Approaches

### 1. eBay's Three-Tier Resolution Model

**What:** eBay processes disputes through a tiered system: automated disposition for rule-clear cases, Seller Help human review for ambiguous removal requests, and formal escalation to eBay Customer Service as a last resort.

**Evidence:** eBay processes over 60 million disputes annually. The feedback removal policy (updated September 2024) explicitly distinguishes: "eBay uses automation to proactively remove feedback that goes against its policy, but for cases that are not clear-cut, we carry out a manual review." Removal decisions are made within 24 hours when approved. The September 2025 seller update introduced automatic positive feedback for eligible orders, showing continued investment in the automated tier.

**Source:** https://www.valueaddedresource.net/ebay-new-feedback-removal-policy/ (accessed 2026-03-12); https://www.valueaddedresource.net/ebay-us-august-2025-seller-update/ (accessed 2026-03-12)

**Fits our case because:** The automated/human split maps directly to Submantle's needs. eBay's automated tier handles rule-clear violations (matching Submantle's self-ping detection, burst flood detection). eBay's human tier handles ambiguous cases (matching Submantle's "genuine incident or coordinated attack?" decisions). eBay also explicitly tracks buyer filing rate and proactively restricts buyers "filing unusually high numbers of cases" — this is the reporter velocity cap Submantle needs.

**Tradeoffs:** eBay has a full CS team for human review. Submantle is a solo founder. eBay's 24-hour decision window assumes staff availability. The solo founder path must make "human review" async and bounded — 72 hours maximum, with auto-resolution fallback.

---

### 2. FCRA Credit Bureau Dispute Process — The 30/45-Day Model

**What:** When a consumer disputes a credit report item, the bureau has 30 days to investigate (extendable to 45 days if new information arrives). The bureau forwards the dispute to the data furnisher within 5 business days. If the furnisher doesn't respond within the 30-day window, the disputed information *must be deleted* — the bureau cannot simply leave it standing.

**Evidence:** 15 U.S.C. § 1681i codifies this process. Experian's published documentation confirms: "If you submit additional information on your dispute during the standard 30-day investigation window, the credit bureau may take an additional 15 days, or a total of 45 days." The FTC's furnisher guidance states: "if you don't investigate and respond to the notification of the dispute within the specified times, the CRA must delete the disputed information from its files."

**Source:** https://www.law.cornell.edu/uscode/text/15/1681i (accessed 2026-03-12); https://www.experian.com/blogs/ask-experian/how-long-does-it-take-to-complete-the-dispute-process/ (accessed 2026-03-12)

**Fits our case because:** This is the exact model Submantle should follow. The credit bureau (Submantle) receives a dispute (incident report). The data furnisher (the reporter) submitted the claim. The subject (the agent) is the one being scored. The FCRA rule that "if the furnisher doesn't respond, delete the item" translates directly to: if the reporter doesn't substantiate within N days, the pending incident auto-expires without affecting the formula. The clock-stopping rule (new information extends the window by 15 days) provides a clean mechanism for disputed incidents.

**Tradeoffs:** FCRA covers humans, not software agents — the legal obligation doesn't apply to Submantle. But the *process design* is directly applicable. The 30-day window was designed for a bureaucracy. Submantle should compress this: 72 hours for automated resolution, 14 days for disputed cases.

---

### 3. PagerDuty Deduplication — The dedup_key Pattern

**What:** PagerDuty groups multiple alerts into a single incident using a deterministic `dedup_key`. While an incident is unresolved, any subsequent alerts with a matching `dedup_key` deduplicate into the original alert rather than creating new incidents. The key is operator-defined, not ML-inferred.

**Evidence:** PagerDuty's official documentation: "When an incident remains unresolved, any subsequent alerts sharing a matching dedup_key automatically consolidate into the original alert." The system is fully deterministic — no ML required. The dedup_key can be any string the sender chooses (typically incident type + affected entity).

**Source:** https://support.pagerduty.com/main/docs/alerts (accessed 2026-03-12)

**Fits our case because:** The dedup_key pattern maps cleanly to Submantle's duplicate incident problem. "Same bug reported 100 times" = same incident type + same agent + same reporter within a time window → same dedup_key → one pending incident, not 100. The score impact is capped at 1 per deduplicated group, not 100.

**Tradeoffs:** PagerDuty's dedup_key is sender-defined, meaning the sender can game it (set a unique key to force 100 separate incidents). Submantle must compute the dedup_key server-side using deterministic rules the reporter cannot override.

---

### 4. Sentry Fingerprint Rules — Deterministic Grouping Without ML

**What:** Sentry groups error events using deterministic fingerprint rules: `matcher:expression -> fingerprint`. Events matching the same rule get the same fingerprint and are grouped into one issue. Teams configure rules per-project; rules evaluate sequentially; first match wins. No ML required for the deterministic tier.

**Evidence:** Sentry documentation: "Rules are evaluated sequentially, and the first match applies." Matchers include error type, error value, log level, stack trace path, function name, module, and custom tags. A rule like `error.type:ConnectionTimeout -> database-timeout` groups all ConnectionTimeout errors into one issue regardless of volume.

**Source:** https://docs.sentry.io/concepts/data-management/event-grouping/fingerprint-rules/ (accessed 2026-03-12)

**Fits our case because:** The fingerprint rule pattern is exactly what Submantle needs for incident deduplication. Submantle's deterministic grouping rules would be expressed as: `incident_type:self_ping + reporter:X + agent:Y → dedup_group = "self-ping-{reporter}-{agent}-{date}"`. All matching incidents collapse into one group. Score impact = 1, not N.

**Tradeoffs:** Sentry now uses ML (Seer) on top of its deterministic fingerprints for semantic grouping. Submantle must not follow this path — fingerprint rules without the ML layer are the appropriate target. The deterministic rules cover ~80% of deduplication cases; the remaining 20% (novel abuse patterns) go to human review.

---

### 5. Amazon's Layered Appeal System — Three Escalation Tiers

**What:** Amazon uses automated enforcement (algorithm flags, auto-suspends) as Tier 1, standard appeal with human review (5-10 minute review window) as Tier 2, and escalated appeal with senior review as Tier 3. In 2025, Amazon added "Seller Challenge" — 3 formal challenge slots per 180 days for AHA program members, triggering re-evaluation by a separate team.

**Evidence:** Multiple sources document 5-10 minute Tier 2 review windows, with Tier 3 escalations triggering legal team review. The September 2025 Seller Challenge launch confirms the three-tier model is industry standard. The pre-arbitration letter triggering legal review is Tier 4 — not relevant for Submantle's prototype.

**Source:** https://amazonsellerslawyer.com/amazon-review-manipulation-suspension-appeal-strategies-2026 (accessed 2026-03-12); https://www.mrjeffamz.com/blog/amazon-seller-challenge-feature-explained-whats-changing-in-listing-enforcement-and-appeals (accessed 2026-03-12)

**Fits our case because:** Three tiers (auto, standard human, escalated human) is the proven pattern. For Submantle at solo founder scale, this compresses to: auto-processing (Tier 1, always available), founder async review (Tier 2, 72-hour SLA), and a hard "cannot be verified → auto-expire" rule that replaces Tier 3 for now.

**Tradeoffs:** Amazon has dedicated enforcement teams. Submantle's "human review" is a solo founder checking a review queue. The 5-10 minute review window Amazon uses is impossible for a solo founder at scale. Submantle must make Tier 2 human review rare by making Tier 1 automation handle the clear cases.

---

## Novel Approaches

### 6. eBay's Reporter Velocity Cap as First-Class Defense

**What:** eBay doesn't just review individual disputes — it proactively monitors buyer claim-filing rates and restricts buyers filing "unusually high numbers of cases." The restriction is the countermeasure, not the review.

**Evidence:** eBay's seller protection documentation explicitly states eBay "proactively identifies and restricts buyers filing unusually high numbers of cases."

**Source:** https://ebaysc.stage.liveplatform.com/seller-protection/fair-case-resolution (accessed 2026-03-12)

**Fits our case because:** Submantle should implement the same pattern. A reporter filing more than N incidents per 24 hours against the same agent enters a flagged state — subsequent reports from that reporter are queued as `suspicious` rather than `pending`. They don't affect the formula at all until a human reviews them. This is orthogonal to the formula itself — it's a pre-formula filter.

**Tradeoffs:** The threshold N is an empirical question. Too low and legitimate incident floods (a genuinely broken agent) get suppressed. Too high and coordinated attacks get through. Starting at 5 per agent per 24-hour window is conservative and adjustable.

---

### 7. Airbnb's Bilateral Evidence Requirement — Both Sides Mandatory

**What:** Airbnb's Resolution Center requires both parties to present evidence (photos, messages, receipts) before escalation to Airbnb review. The 60-day window for filing and the 3-day response window before escalation are hard deadlines.

**Evidence:** Airbnb's official help documentation: "If an agreement isn't reached, the host or guest can submit a request in the Resolution Center within 60 days of the reservation ending. If your request isn't resolved by guests within 3 days, you should 'Escalate to Airbnb'." Evidence presentation is required.

**Source:** https://www.airbnb.com/help/article/1423 (accessed 2026-03-12)

**Fits our case because:** The "3 days before escalation" model maps to Submantle's design. When an incident is filed, the reported agent gets 72 hours to respond (submit context, evidence, dispute the claim). If the agent doesn't respond in 72 hours, the case proceeds to next tier. If the reporter doesn't substantiate within 14 days, the incident auto-expires. The bilateral obligation prevents one-sided abuse.

**Tradeoffs:** Airbnb has AI-generated fraud already (verified 2026: a $9,000 damage claim with AI-generated "evidence" images). Submantle's interaction ID requirement (only registered members who interacted can file) already handles much of this, but the evidence review problem remains for human tier.

---

## Emerging Approaches

### 8. Severity Classification via Deterministic Thresholds (Content Moderation Pattern)

**What:** Content moderation platforms (2025) define severity levels S0–S3 with deterministic thresholds rather than ML inference. S0 = imminent/mass harm = auto-block. S1 = widespread abuse = rate limits. S2 = contextual = human review. S3 = edge case = lowest priority.

**Evidence:** Industry research from 2025 documents structured severity frameworks: "Severity levels (S0–S3) are defined with corresponding actions, where S0 represents imminent harm or mass exploitation requiring immediate takedown and law-enforcement referral, while S1 covers widespread policy abuse requiring rate limits and feature flags."

**Source:** https://deepcleer.com/m/blog/content-moderation-best-practices-challenges-2025--122 (accessed 2026-03-12)

**Fits our case because:** The S0-S3 pattern maps cleanly to Submantle incident severity. The key insight is that severity determines *processing tier*, not just human priority. High-severity incidents (self-ping flood) auto-process without human review. Low-severity incidents (single disputed transaction) get human review. This is exactly what deterministic-only requires.

**Tradeoffs:** Content moderation S0 means content removal — an enforcement action. Submantle's equivalent is not removal but "incident immediately enters formula as accepted, no pending period." For the solo founder phase, only the most extreme cases should skip pending.

---

## Gaps and Unknowns

1. **What is the right auto-expire window for unsubstantiated incidents?** The FCRA uses 30 days (bureaucratic pace). eBay uses 90 days for feedback removal requests. Airbnb uses 60 days for filing and 3 days for response. For Submantle's prototype, 14 days for reporter substantiation and 72 hours for agent response are defensible defaults, but these are not validated by customer data yet.

2. **How should weight be applied to partial deduplication?** PagerDuty deduplicates identical events completely. Sentry groups by fingerprint. Neither addresses "same incident type, same agent, different reporters, different interaction IDs." The research does not yield a clear industry precedent for multi-reporter deduplication of the same underlying incident. The FCRA model (one investigation per disputed item, regardless of how many consumers dispute it) is the closest analogy.

3. **What happens when a reporter's interaction ID is valid but the interaction was adversarial?** A reporter can manufacture a valid interaction (register, make one real query, then file a false incident) to bypass the interaction ID gate. eBay's equivalent problem is solved by reputation-weighted filing (Top Rated Sellers get more benefit of the doubt). Submantle's reporter trust score is the right countermeasure but isn't built yet.

4. **What constitutes "resolved" for a disputed incident?** When the reporter substantiates and the agent doesn't dispute — clear. When both parties dispute — who decides? The FCRA model says the furnisher (reporter) has the burden of verification; if they can't verify, delete. For Submantle: if reporter cannot substantiate within 14 days, incident expires. If agent disputes with counter-evidence, human review required. "Resolved" should mean: formula impact finalized (either accepted or expired), with full audit trail preserved.

5. **Reporter reputation scoring mechanics:** The research confirms weighting reports by reporter reputation is standard (eBay, academic Beta reputation literature) but provides no specific formula for how reporter trust interacts with incident weight. This is an open design decision.

---

## Anti-Gaming Analysis

### Attack Vector 1: Incident Flood (Reporter Coordinated Attack)
**Attack:** Register 50 agents, interact with target, file 50 incidents from 50 reporters. Target score collapses before pending state review completes.

**Deterministic countermeasures:**
- Reporter velocity cap: max 5 pending incidents per reporter per 24-hour window (new reports beyond threshold enter `suspicious` state, don't count toward formula)
- Cross-reporter dedup group: if 10+ pending incidents share `incident_type + agent_id + time_window_24h`, they collapse into one dedup group (one formula impact, not 10)
- Registration age gate: reporters with < 30 days registration age get a reduced-weight flag on their reports (brands see the flag; formula impact delayed until human review)

**Evidence base:** eBay's proactive restriction of high-volume case filers; Amazon's automated enforcement monitoring

### Attack Vector 2: Self-Ping Inflation
**Attack:** Agent calls `/api/query` 10,000 times with identical parameters. Trust score approaches 1.0 regardless of incidents.

**Deterministic countermeasures:**
- Query diversity cap: if 90%+ of an agent's last 1,000 queries share identical parameters, queries beyond 100 in that cluster don't accumulate trust
- Velocity cap: max 60 trust-accumulating queries per hour (queries beyond cap are logged but don't increment `total_queries`)
- These rules are already in CLAUDE.md — this research confirms they're needed and provides the threshold logic

**Evidence base:** Section 4 of plan-deepen-notes.md; VISION.md anti-gaming section

### Attack Vector 3: Reporter Credibility Spoofing
**Attack:** Register with legitimate history (30+ days, high trust score), file false reports to destroy a competitor.

**Deterministic countermeasures:**
- False report rate tracking: if a reporter's historically filed incidents have > 50% `expired` outcomes (not accepted), their future reports carry a flag visible to human reviewers
- One-incident-per-interaction-ID constraint: a reporter cannot file two pending incidents against the same agent for the same interaction ID (unique constraint on `interaction_id + reporter_agent_id`)
- Cooldown period: 24 hours between filing incidents against the same agent from the same reporter

**Evidence base:** FCRA furnisher accountability model; eBay seller protection documentation

### Attack Vector 4: Pending State Exploitation
**Attack:** File an incident knowing it goes pending — use the "Under Review" label on the target to discourage brands from interacting, without the incident ever affecting the score.

**Deterministic countermeasures:**
- Pending duration is public but bounded: labels showing "Under Review since [date]" with a "resolves by [date]" field prevent indefinite status manipulation
- Brands see both the pending count AND the accepted incident count — a pile of pending incidents that never get accepted is itself a signal of potential false reporting
- After 3 pending incidents from the same reporter against the same agent, subsequent reports from that reporter-agent pair require human review before even entering pending state

**Evidence base:** FCRA model (disputed items are visible but labeled "under investigation"); eBay's approach of removing feedback for completed cases

### Attack Vector 5: Self-Dispute Loop
**Attack:** Agent files dispute against their own pending incidents to keep them in limbo indefinitely, blocking the formula impact.

**Deterministic countermeasures:**
- Hard maximum pending duration: 14 days. After 14 days, the system must either accept or expire the incident — it cannot remain pending indefinitely regardless of dispute state
- Disputes do not reset the 14-day clock; they extend it by at most 7 additional days (maximum 21 days total)
- After the maximum window, if substantiation is missing, incident expires; if dispute is unresolved, incident auto-accepts at reduced weight (0.5 formula weight vs 1.0 for fully accepted)

**Evidence base:** FCRA's 45-day maximum window with extension rules; Airbnb's hard filing deadlines

---

## Synthesis: The Minimum Viable Review Workflow

Based on research across eBay, FCRA, PagerDuty, Sentry, Amazon, Airbnb, and content moderation platforms, here is the complete incident processing design for Submantle — implementable by a solo founder, using only deterministic rules, requiring minimal human time.

### The Five Incident States

```
SUSPICIOUS → (human clears) → PENDING
             (human confirms) → REJECTED

PENDING → (auto: clear-cut violation) → ACCEPTED
        → (auto: dedup group) → DEDUPLICATED (grouped under primary)
        → (auto: 14 days no substantiation) → EXPIRED
        → (agent disputes, within 14 days) → DISPUTED
        → (reporter substantiates) → ACCEPTED

DISPUTED → (human review within 72h of dispute) → ACCEPTED or EXPIRED
         → (21-day hard limit) → AUTO-ACCEPTED (reduced weight 0.5) or AUTO-EXPIRED

ACCEPTED → affects formula immediately (incident counter incremented)
         → status visible to brands indefinitely (audit trail)
         → agent can request re-review after 30 days if new evidence emerges

EXPIRED → does NOT affect formula
        → stored in audit log
        → if reporter files same incident_type against same agent again within 30 days: auto-SUSPICIOUS
```

### Severity Classification (Deterministic Rules Only)

| Severity | Rule | Processing Path | Formula Impact |
|----------|------|-----------------|----------------|
| **Critical** | Incident count from single reporter > 10 per agent per 24h | Skip pending → ACCEPTED immediately, reporter flagged | Full (1.0 weight) |
| **Critical** | Incident type = `self_ping_detected` + evidence = interaction log showing 10,000+ identical queries | Auto-ACCEPTED, no human review needed | Full (1.0 weight) |
| **Standard** | Single incident, reporter trust > 0.5, interaction ID verified | PENDING → 72h agent response window → human review if disputed | Full (1.0 weight) if accepted |
| **Reduced** | Reporter registration age < 30 days | PENDING → requires human review before ACCEPTED | Reduced (0.5 weight) if accepted |
| **Suspicious** | Reporter velocity > 5 incidents per agent per 24h | SUSPICIOUS → human review before entering PENDING | Zero until cleared |

### Deduplication Rules (Deterministic, Server-Side)

The `dedup_key` is computed server-side and cannot be influenced by the reporter. Rules, in priority order:

1. **Exact match:** `sha256(incident_type + agent_id + reporter_agent_id + date)` — same reporter filing same incident type against same agent on same day = single dedup group
2. **Burst match:** `incident_type + agent_id + floor(timestamp / 3600)` — any incidents of same type against same agent within the same 1-hour window = dedup group (one formula impact)
3. **Cross-reporter match:** If 5+ reporters file same `incident_type` against same agent within 48 hours, collapse into one dedup group — score impact = 1 incident, not 5 (marks the incident as "corroborated" which brands can see, but formula impact stays 1)

The "corroborated" flag from rule 3 is important: a single incident with 5 reporters corroborating it is more credible than 5 separate incidents. It should be visible to brands without multiplying the formula impact.

### Pending Duration Standards

| Case Type | Agent Response Window | Reporter Substantiation Deadline | Hard Expiry |
|-----------|-----------------------|----------------------------------|-------------|
| Standard | 72 hours | 14 days from filing | 14 days |
| Disputed | 72 hours | 14 days from filing | 21 days (7-day extension) |
| Critical (self-ping, flood) | N/A — auto-processed | N/A | N/A — immediate |

Justification: The FCRA uses 30/45 days for bureaucratic processes with legal liability. eBay uses 24h for clear-cut cases. Airbnb uses 72h for response windows. For a trust infrastructure system (not legal obligation), 72h for response and 14 days for resolution is aggressive but appropriate — prolonged pending harms both parties.

### What "Resolved" Means

An incident is "resolved" when it reaches ACCEPTED or EXPIRED state. Resolution is final when:
- Formula impact is determined (accepted → counter incremented; expired → no impact)
- Audit record is permanently written
- Both parties are notified of outcome
- No further state transitions are possible EXCEPT: ACCEPTED incidents can be re-reviewed after 30 days if new evidence emerges (this prevents permanent damage from early processing errors)

### The Solo Founder Review Queue

The solo founder's human review burden is minimized by design. Human review is only triggered by:
1. DISPUTED incidents (agent files dispute → founder reviews within 72 hours)
2. SUSPICIOUS reports (reporter velocity exceeded → founder reviews before PENDING)
3. Edge cases: first incident from a new reporter against a well-established agent (trust score > 0.8, 90+ days, 500+ queries) — high-stakes case, worth human eyes

Everything else is processed automatically. At prototype scale (< 100 agents, < 10 brands), the human review queue should be near-empty. The review queue is the exception path, not the default path.

### Schema Changes Required

These are the columns that need to be added to `incident_reports` to support this design:

```sql
-- New columns on incident_reports
status TEXT NOT NULL DEFAULT 'pending'      -- pending | suspicious | accepted | expired | disputed | deduplicated
dedup_group_id TEXT                         -- sha256-based key; NULL if not in a group
severity TEXT NOT NULL DEFAULT 'standard'  -- critical | standard | reduced | suspicious
formula_weight REAL NOT NULL DEFAULT 1.0   -- 1.0 | 0.5 | 0.0
reviewed_by TEXT                           -- founder token or 'system'; NULL if not yet reviewed
reviewed_at REAL                           -- Unix timestamp; NULL if pending
expires_at REAL NOT NULL                   -- Unix timestamp: when this incident auto-expires if not substantiated
dispute_filed_at REAL                      -- NULL if not disputed
corroboration_count INTEGER DEFAULT 0      -- count of other reporters who filed same incident (dedup group size)
```

These columns allow the formula to stay clean: only count `incidents WHERE status = 'accepted'` toward the trust formula. The aggregate counter `incidents INTEGER` on `agent_registry` becomes a derived view, not a mutable counter (or: only increment it when status transitions to `accepted`).

### How This Interacts with the Beta Formula

Current formula: `trust = (total_queries + 1) / (total_queries + incidents + 2)`

With the review tier design:
- `incidents` in the formula = count of ACCEPTED incidents only (not pending, not expired)
- Formula-weight modifier for reduced-weight incidents: `incidents` counts them as 0.5 instead of 1.0
- `total_queries` still requires velocity cap (separate change, but essential companion)

The formula itself doesn't change. The inputs to it become trustworthy.

---

## Sources

- [eBay New Feedback Removal Policy](https://www.valueaddedresource.net/ebay-new-feedback-removal-policy/)
- [eBay August 2025 Seller Update](https://www.valueaddedresource.net/ebay-us-august-2025-seller-update/)
- [eBay Seller Protection / Fair Case Resolution](https://ebaysc.stage.liveplatform.com/seller-protection/fair-case-resolution)
- [eBay Money Back Guarantee Policy](https://www.ebay.com/help/policies/ebay-money-back-guarantee-policy/ebay-money-back-guarantee-policy?id=4210)
- [FCRA 15 U.S.C. § 1681i — Procedure in Case of Disputed Accuracy](https://www.law.cornell.edu/uscode/text/15/1681i)
- [Experian: How Long Does the Dispute Process Take?](https://www.experian.com/blogs/ask-experian/how-long-does-it-take-to-complete-the-dispute-process/)
- [PagerDuty: Alerts Documentation](https://support.pagerduty.com/main/docs/alerts)
- [Sentry: Fingerprint Rules](https://docs.sentry.io/concepts/data-management/event-grouping/fingerprint-rules/)
- [Amazon Seller Challenge Feature Explained](https://www.mrjeffamz.com/blog/amazon-seller-challenge-feature-explained-whats-changing-in-listing-enforcement-and-appeals)
- [Amazon Appeal Best Practices 2025](https://amazonsellerslawyer.com/amazon-review-manipulation-suspension-appeal-strategies-2026)
- [Airbnb Resolution Center — After Your Stay](https://www.airbnb.com/help/article/1423)
- [Content Moderation Best Practices 2025](https://deepcleer.com/m/blog/content-moderation-best-practices-challenges-2025--122)
- [YouTube Content Moderation — NeoWork](https://www.neowork.com/insights/how-does-youtube-moderate-content)
- [YouTube: 12M Channel Terminations 2025](https://www.creatorhandbook.net/youtube-addresses-ai-moderation-concerns-after-reporting-12-million-channel-terminations-in-2025/)
