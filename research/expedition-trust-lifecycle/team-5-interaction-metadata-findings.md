# Team 5 — Interaction Metadata Findings
## Expedition: Trust Lifecycle
## Angle: What Gets Recorded and How It's Presented
## Date: 2026-03-12
## Researcher: Claude Sonnet 4.6

---

## Executive Summary

The research question is: what metadata should Submantle record per interaction, and how should it be presented to technical vs. non-technical audiences? This report draws on credit bureau standards (Experian/Equifax/TransUnion), eBay's bidirectional feedback model, API audit logs (AWS CloudTrail, GitHub, Stripe), and the OWASP security logging standard. The findings converge on a clear minimum viable interaction metadata spec and a well-established dual-interpretation pattern that Submantle should adopt wholesale.

**Key finding**: Every mature trust/audit system records the same five categories — identity, time, action, outcome, context. Denied interactions are always recorded (they are the most informative events). Dual-audience presentation is a solved UX problem: one underlying record, two rendered views. Anti-gaming via metadata manipulation is real and has known deterministic countermeasures.

---

## 1. Credit Bureau Trade Line Fields (Experian/Equifax/TransUnion)

Source: CFPB consumer guidance, myFICO, Equifax public documentation. All sources from 2024-2025.

A credit report trade line — the per-account entry — contains these fields:

**Identity fields:**
- Creditor name and address
- Account number (partial, masked)
- Account type (revolving, installment, mortgage, etc.)
- Account ownership (individual, joint, authorized user)

**Temporal fields:**
- Date opened
- Date of last activity
- Date reported (when bureau last received an update)
- Date of first delinquency (if applicable)

**Financial state fields:**
- Credit limit or original loan amount
- Current balance
- High balance (highest balance ever reported)
- Monthly payment amount
- Amount past due

**Status fields:**
- Payment status (current, 30/60/90/120+ days late)
- Account status (open, closed, transferred, charged off, in collections)
- 24-month payment history grid (each month: paid on time, 30-day late, 60-day, etc.)

**Context fields:**
- Comments (dispute in progress, account included in bankruptcy, settled for less, etc.)
- Special condition codes (e.g., "paying under a partial payment agreement")

**What bureaus show to consumers vs. lenders:**
The underlying data record is identical. The rendering differs:
- Consumer view (annualcreditreport.com): plain English labels, 24-month visual payment grid, status shown as "Current" or "60 days late"
- Lender view (API/batch): METRO 2 format codes — status "11" = current, "71" = 30-day late, "78" = 120+ days. The same payment grid as a numeric array.

**Critical design note for Submantle:** The bureaus separate the data record from its rendering. The METRO 2 status code "71" and "30 days late" are the same fact expressed for two audiences. Submantle should do the same: one canonical interaction record, two rendered interpretations.

---

## 2. eBay Transaction/Feedback Metadata

Sources: eBay Browse API docs (2025), eBay Sell Feedback API docs (2025).

**What eBay records per transaction (feedback entry):**

Core identifiers:
- `feedbackId` — unique per feedback record
- `listingId` — the item being transacted
- `orderLineItemId` — the specific line item (join key linking feedback to the interaction that generated it)
- `userId` — who gave the feedback (privacy-masked for non-logged-in viewers)

Outcome data:
- `commentType` — POSITIVE, NEUTRAL, or NEGATIVE
- `feedbackScore` — integer representing cumulative reputation
- `feedbackPercentage` — positive feedback percentage (aggregate)
- `feedbackState` — status of the feedback entry

Dimensional ratings (per-axis scores, not just a single number):
- `ON_TIME_DELIVERY`
- `ITEM_AS_DESCRIBED`
- `COMMUNICATION`
- `SHIPPING_CHARGES`
- `SHIPPING_TIME`

Content fields:
- `commentText` (500 char max)
- `images` (up to 5)
- `topics` — AI-identified themes (shipping, service, packaging, sentiment) — NOTE: eBay uses ML here; Submantle must not

Temporal:
- `feedbackEnteredDate`
- `feedbackEnteredPeriod`

Response chain:
- `replyComment` — seller's response
- `followupComment` — buyer's follow-up
- `repliedBeforeFollowup` — boolean

**Pending/disputed state:**
eBay has an `awaiting_feedback` state for transactions where feedback has not yet been submitted. The `feedbackState` field carries the entry's lifecycle status. eBay does not provide feedback for cancelled/denied transactions — feedback is only for completed transactions. This is a deliberate design choice: eBay only scores interactions that completed.

**Critical design note for Submantle:** eBay's `orderLineItemId` is the interaction join key — the authoritative record that a transaction happened. Submantle's equivalent is the `interaction_id`. The reporter can only file feedback against an interaction ID that Submantle itself generated. This is the anti-fabrication mechanism: Submantle owns the proof of interaction.

---

## 3. API Audit Log Metadata (AWS CloudTrail, GitHub, Stripe)

### AWS CloudTrail
Source: AWS CloudTrail Event Reference documentation (current).

Every CloudTrail event — success or denial — contains:

**Identity:** `userIdentity` (type, principalId, ARN, accountId, accessKeyId, userName, sessionContext with MFA status)

**Time:** `eventTime` (ISO 8601)

**Action:** `eventName` (API method called), `eventSource` (which service), `eventCategory` (Management/Data/NetworkActivity)

**Network context:** `sourceIPAddress`, `userAgent`, `awsRegion`, `tlsDetails` (version, cipher suite)

**Request:** `requestParameters` (what was passed in)

**Response/Outcome:** `responseElements` (what came back; null on denied calls), `errorCode` (e.g., `VpceAccessDenied`), `errorMessage` (human-readable reason)

**Tracking:** `requestID` (unique per call), `eventID` (unique per CloudTrail record), `readOnly` (boolean)

**Resources affected:** `resources` array (ARN, type, accountId)

**For denied calls specifically:** Same fields as successful calls, with `responseElements: null` and `errorCode`/`errorMessage` populated. CloudTrail Insights specifically tracks unusual `AccessDeniedException` error rates as a behavioral signal.

### GitHub Audit Log
Source: GitHub organization audit log documentation (2025).

Fields per event: `action`, `actor`, `user`, `org`, `repo`, `created_at` (epoch ms), `actor_location.country_code`, plus event-type-specific data fields.

### Stripe Charge Object
Source: Stripe API docs (2025).

Key fields: `id`, `amount`, `currency`, `created`, `paid`, `captured`, `outcome` (risk_level, risk_score 0-100, network_status, seller_message, type), `failure_code`, `failure_message`, `fraud_details`, `billing_details`, `payment_method_details`, `metadata` (custom key-value).

For PaymentIntent failures: `last_payment_error` containing `code` (machine-readable), `decline_code` (issuer reason), `message` (human-readable), `network_decline_code`, `advice_code`, `payment_method` details.

**Critical design note for Submantle:** Stripe's `outcome` object is the clearest model for the dual-interpretation pattern. It contains both `risk_score: 73` (technical) and `seller_message: "Stripe blocked this charge as too risky"` (layman). One field for machines, one field for humans, both in the same record. Submantle should adopt this exact pattern.

---

## 4. Dual-Audience Presentation: The UX Pattern

Sources: Stripe Radar documentation, AWS CloudTrail Insights, OWASP Logging Cheat Sheet.

Every mature system that presents trust/risk data to mixed audiences uses the same pattern:

**Layer 1 — Raw record (internal, machine-readable):**
Canonical data with codes and IDs. Example: `errorCode: "VpceAccessDenied"`, `risk_score: 73`, payment status `"71"` (METRO 2).

**Layer 2 — Technical rendering:**
Codes expanded with context. Example: CloudTrail shows `AccessDeniedException` in the error column alongside the full request parameters. Stripe Dashboard shows `outcome.type: "blocked"` with `outcome.reason: "highest_risk_level"`.

**Layer 3 — Layman rendering:**
Same underlying fact in plain language. Stripe's `seller_message` field: "Stripe blocked this charge as too risky." Credit report: "60 days late" instead of status code "78". eBay feedback: "Positive" instead of type enum.

**Stripe Radar's review queue** is the clearest V1 model:
- List view: quick scan with risk level, name, method, amount, date — no jargon
- Detail view: full metadata with risk insights, customizable context fields
- Both views render from the same underlying charge/outcome record

**Pattern for Submantle:**
Every interaction record stores one `technical_interpretation` string and one `layman_interpretation` string, generated deterministically at write time (not at query time — this ensures consistency and avoids computation on read). Both are populated from the same structured outcome data.

Example:
```
technical_interpretation: "HTTP 504 Gateway Timeout after 30s on POST /api/payment/confirm — 3 occurrences in 5-minute window"
layman_interpretation: "This agent's payment confirmation timed out — it took too long to respond, three times in a row"
```

---

## 5. The Denial Scenario: Does a Denied Interaction Affect Scores?

**The scenario:** An under-review agent tries to interact with a brand. The brand's system denies access because the agent's trust score is below threshold. That denial is itself an event. How should it be recorded? Does it affect either party's score?

### How comparable systems handle this:

**AWS CloudTrail:** Records the denial with full metadata (same fields as a success, plus `errorCode`/`errorMessage`). The denial does NOT affect IAM user reputation scores — CloudTrail logs for audit, not scoring. However, CloudTrail Insights flags unusual denial rates as behavioral signals.

**eBay:** Does NOT generate feedback for denied/cancelled transactions. Feedback is only for completed transactions. This is the right model for outcome scoring — you can only score what was actually attempted and resolved.

**Credit bureaus:** A lender declining to extend credit does NOT appear on the borrower's credit report. What appears is the "hard inquiry" — the lender checked the score. Multiple hard inquiries in a short window are themselves a scoring signal (signals credit-seeking behavior).

**Stripe:** Records declined payment intents with full metadata including `last_payment_error`. A declined charge does not retroactively lower a customer's risk score — the score was why it was declined, not the result of the decline. However, the decline is recorded for audit and pattern analysis.

### Synthesis for Submantle:

**The brand's denial should NOT affect the agent's trust score.** The agent was denied access because of its existing score — using the denial to further lower the score is circular and unfair (the credit bureau equivalent of "we denied your loan, which we're now recording as a default").

**The brand's denial SHOULD be recorded as an interaction record** with `outcome: DENIED_BY_COUNTERPARTY`. Reasons:
1. It provides behavioral context — an agent accumulating many denials across brands is a signal worth surfacing (like a credit hard-inquiry concentration)
2. It provides an audit trail for the brand (compliance)
3. It enables Submantle to surface the pattern: "This agent has been denied access by 7 brands in 30 days" — useful information without being punitive

**The brand's denial SHOULD be recorded against the brand too.** Bidirectional trust: a brand that denies a high-trust agent (false positive) or accepts a low-trust agent (false negative) is producing observable data about its own threshold quality over time.

**Recommended outcome states for an interaction record:**
- `COMPLETED` — both parties transacted, no incident
- `COMPLETED_WITH_INCIDENT` — transaction completed but a report was filed
- `DENIED_BY_COUNTERPARTY` — brand rejected the agent (brand's threshold, not agent's behavior)
- `DENIED_BY_AGENT` — agent rejected the brand (agent's threshold)
- `TIMEOUT` — interaction attempted, no response
- `ERROR` — technical failure (HTTP 5xx, connection refused)
- `PENDING` — interaction initiated, outcome not yet resolved

Only `COMPLETED_WITH_INCIDENT` should affect the Beta Reputation formula. The others are context data.

---

## 6. Minimum Viable Interaction Metadata Spec for Submantle V1

Drawing on all sources above, the minimum viable interaction record for Submantle V1 contains:

### Core Identity Fields
```
interaction_id       TEXT NOT NULL UNIQUE    -- UUID, Submantle-generated, authoritative proof of interaction
agent_id             INTEGER NOT NULL        -- FK to agent_registry
counterparty_id      TEXT NOT NULL           -- agent_id if registered, or "unregistered:{name}" for unregistered
counterparty_type    TEXT NOT NULL           -- 'agent' | 'brand' | 'service' | 'unregistered'
```

### Temporal Fields
```
initiated_at         REAL NOT NULL           -- Unix epoch float, when interaction started
resolved_at          REAL                    -- NULL until outcome known
duration_ms          INTEGER                 -- resolved_at - initiated_at in milliseconds
```

### Action Fields
```
interaction_type     TEXT NOT NULL           -- 'query' | 'report_incident' | 'verify_score' | 'request_access' | ...
endpoint             TEXT                    -- what was called (e.g., 'get_trust_score', 'mcp:tools/call')
```

### Outcome Fields
```
outcome              TEXT NOT NULL           -- 'COMPLETED' | 'COMPLETED_WITH_INCIDENT' | 'DENIED_BY_COUNTERPARTY' |
                                            --   'DENIED_BY_AGENT' | 'TIMEOUT' | 'ERROR' | 'PENDING'
http_status          INTEGER                 -- HTTP status code if applicable (200, 403, 504, etc.)
error_code           TEXT                    -- machine-readable error code (e.g., 'ACCESS_DENIED', 'TIMEOUT_30S')
```

### Interpretation Fields (dual-audience — generated at write time)
```
technical_interpretation  TEXT NOT NULL      -- e.g., "HTTP 504 after 30s on POST /api/payment/confirm"
layman_interpretation     TEXT NOT NULL      -- e.g., "Payment confirmation timed out — took too long to respond"
```

### Anti-Gaming Fields
```
velocity_flag        INTEGER NOT NULL DEFAULT 0   -- 1 if this interaction was capped (counted for audit, not trust formula)
diversity_flag       INTEGER NOT NULL DEFAULT 0   -- 1 if interaction was flagged as non-diverse (same endpoint as 90%+ prior)
```

### Privacy Fields
```
privacy_mode_active  INTEGER NOT NULL DEFAULT 0   -- snapshot of privacy state at record time
```

### Trust Formula Integration
Only interactions where `outcome = 'COMPLETED'` increment `total_queries`. Only interactions where `outcome = 'COMPLETED_WITH_INCIDENT'` increment `incidents`. All other outcomes are contextual records only.

---

## 7. Privacy: Metadata Without Content

Sources: OWASP Logging Cheat Sheet, RATS RFC 9334, Submantle design principles.

**What Submantle sees:** interaction metadata — who, what type of call, when, how long, what happened. NOT the content of the interaction (what data was passed, what was returned).

**This is already the industry norm:**
- CloudTrail logs `requestParameters` at the parameter-name level but not the data values in many cases. For sensitive services, parameters are omitted.
- GitHub audit logs record `action`, `actor`, `target` — not the content of commits or pull requests.
- eBay feedback records `commentType` (POSITIVE/NEUTRAL/NEGATIVE) and structured ratings — the free-text comment is optional and user-controlled.
- OWASP explicitly prohibits logging "authentication passwords," "access tokens," or "session identification values."

**What metadata alone is sufficient for trust scoring:**
- Interaction frequency (volume signal)
- Outcome distribution (COMPLETED vs ERROR vs TIMEOUT rates)
- Endpoint diversity (breadth of use signal)
- Counterparty diversity (breadth of relationships signal)
- Duration patterns (timeout frequency)
- Incident rate (reported problems)

This is enough for the Beta Reputation formula and for the anti-gaming rules. No content needed.

**Privacy boundary rule for Submantle:** The `data` field in the events table (already exists) should never contain interaction content. The `technical_interpretation` and `layman_interpretation` fields describe what type of interaction happened and its outcome — never what was in the request or response payload.

---

## 8. Anti-Gaming Analysis: How Interaction Metadata Can Be Manipulated

### Attack vectors against interaction metadata:

**1. Fabricated interaction IDs (reporter fraud)**
An agent claims interaction ID `xyz-123` happened and files an incident against it. Defense: Submantle generates all interaction IDs. A reporter can only reference an ID that Submantle issued. This is the eBay model — eBay owns the `orderLineItemId`; you can't leave feedback for a transaction that eBay has no record of.

**2. Self-query inflation via interaction logging**
Agent creates 10,000 interaction records with itself as both parties. Defense: `counterparty_id = agent_id` interactions don't count toward trust. Velocity cap: max N `COMPLETED` interactions per hour count toward the formula.

**3. Outcome manipulation**
Agent reports all its own interactions as `COMPLETED` and reports counterparty interactions as `ERROR` or `TIMEOUT`. Defense: For bidirectional trust, both parties must confirm the outcome. If only one party reports, the outcome is `PENDING` until confirmed or a timeout window passes. This is the eBay mutual confirmation model.

**4. Diversity gaming**
Agent cycles through a rotation of 10 endpoints to pass the 90% diversity threshold, then repeats the cycle. Defense: Diversity is measured against a rolling time window. The `diversity_flag` can use entropy calculation over endpoint distribution — low-entropy distributions (even if not 90% identical) get flagged. Deterministic: Shannon entropy of endpoint histogram, threshold is a fixed constant.

**5. Denial accumulation against competitors**
Brand A repeatedly "denies" Brand B's agent to accumulate negative context signals against it. Defense: `DENIED_BY_COUNTERPARTY` outcome does NOT affect the Beta formula. It is contextual data only. Mass denials from a single brand are a signal about the brand's behavior, not the agent's.

**6. Metadata poisoning via reporter field**
Bad actor registers many fake brands, each filing denial records. Defense: Reporter minimum age (registration_time must be X days old to file records that appear in context signals). Reporter trust score minimum (low-trust brands' denials are weighted lower in context display, though they're still stored).

**7. Interaction ID harvesting**
Agent observes interaction IDs from legitimate transactions and attempts to reuse them for fabricated reports. Defense: Unique constraint on `(interaction_id, reporter_agent_id)` — one report per interaction per reporter. The interaction ID is generated with cryptographic entropy (UUID v4), making enumeration attacks infeasible.

### Deterministic countermeasures sufficient for V1:
1. Submantle-generated interaction IDs (prevents fabrication)
2. `velocity_flag` on interactions exceeding hourly cap (prevents inflation)
3. `diversity_flag` on low-entropy endpoint distributions (prevents rotation gaming)
4. Outcome confirmation window (both parties or timeout — prevents unilateral outcome setting)
5. Reporter minimum age check (prevents throwaway reporter accounts)
6. `DENIED_BY_COUNTERPARTY` excluded from formula (prevents competitive denial campaigns)

---

## 9. Connecting to Existing Codebase

Current state (from codebase review):
- `agent_registry` table tracks `total_queries` and `incidents` as aggregate counters — no per-interaction detail
- `incident_reports` table has: `agent_id`, `agent_name`, `reporter`, `incident_type`, `description`, `timestamp`
- No `interaction_id` field exists anywhere
- `trust_metadata` column exists on `agent_registry` but is never written — available for pattern caching
- `events` table exists but records system events, not agent-to-agent interactions

**What must be added:**
1. `interaction_logs` table (new) — the per-interaction record with all fields from Section 6
2. `interaction_id` field on `incident_reports` (schema migration) — joins an incident to its interaction
3. `technical_interpretation` and `layman_interpretation` generated by a helper function at write time
4. `velocity_flag` and `diversity_flag` set by the write path, not computed at query time

**The `trust_metadata` column is the right home for aggregate pattern data** derived from interaction logs — velocity window counts, diversity entropy score, denial concentration stats. This avoids expensive per-query aggregations. Recompute and cache on each new interaction record write.

**The existing `compute_trust()` formula remains unchanged.** Only `COMPLETED` interactions increment `total_queries`. Only `COMPLETED_WITH_INCIDENT` interactions increment `incidents`. The formula stays pure Beta Reputation math. The interaction log provides the raw data; the counters provide the formula inputs.

---

## 10. Key Sources

| Source | Type | Recency | Used For |
|--------|------|---------|---------|
| eBay Sell Feedback API docs | Official API docs | 2025 | Feedback fields, pending states, interaction join key pattern |
| eBay Browse API docs | Official API docs | 2025 | Seller reputation fields, aggregated scores |
| AWS CloudTrail Event Reference | Official docs | Current | Full event record schema, denied call handling |
| Stripe Charge Object API | Official docs | 2025 | Dual-interpretation pattern, failure metadata |
| Stripe PaymentIntent API | Official docs | 2025 | Denial recording, `last_payment_error` structure |
| Stripe Radar Risk docs | Official docs | 2025 | Technical vs. layman presentation, `seller_message` pattern |
| GitHub Audit Log docs | Official docs | 2025 | Audit log field structure |
| OWASP Logging Cheat Sheet | Security standard | Current | Required fields for denied requests, privacy boundaries |
| RATS RFC 9334 | IETF standard | 2023 | Evidence structure, Passport Model |
| myFICO credit education | Consumer reference | 2024-2025 | Trade line field categories |
| CFPB credit resources | Regulatory reference | 2024 | Consumer vs. lender presentation differences |

---

## Conclusions

1. **The minimum viable interaction record is well-established.** Five categories (identity, time, action, outcome, context) appear in every mature system. Submantle should follow this structure without deviation.

2. **Dual-interpretation is a solved pattern.** Store both `technical_interpretation` and `layman_interpretation` in the record at write time. Stripe's `seller_message` is the direct model. Generate these deterministically from structured outcome fields — no ML, no inference.

3. **Denied interactions must be recorded but must not affect the trust formula.** This is how credit bureaus (hard inquiries ≠ defaults), CloudTrail (AccessDeniedException ≠ reputation hit), and payment networks (declined payment ≠ customer score change) all handle it. Denial is context, not outcome.

4. **The interaction_id is the anti-fabrication mechanism.** Submantle generates it. Reporters can only reference IDs Submantle issued. This is the eBay `orderLineItemId` model applied to trust.

5. **Anti-gaming is deterministic and sufficient.** Velocity caps, diversity entropy, reporter age minimums, and outcome confirmation windows cover the realistic attack surface without ML. EU AI Act exemption is preserved.

6. **Privacy is structural.** Log who, what type, when, how long, what outcome — never what was in the request or response. This is already industry norm and matches Submantle's on-device, no-telemetry principle.

7. **The existing codebase needs one new table.** `interaction_logs` with the spec from Section 6. Everything else — the trust formula, the incident table, the event bus — stays as-is. The counters remain; the log adds the detail layer beneath them.
