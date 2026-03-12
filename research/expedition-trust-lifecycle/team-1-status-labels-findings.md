# Team 1 Research Findings: Status Labels and What They Communicate
## Date: 2026-03-12
## Expedition: Trust Lifecycle Design
## Angle: Status Labels and What They Communicate

---

## Executive Summary

Eight analog systems were researched to understand how neutral infrastructure labels entities without acting on those labels. The pattern that emerges is consistent across credit bureaus, payment networks, app stores, domain registries, and certificate authorities:

**The labeling authority provides transparent, auditable status information with accompanying metadata. The entity making decisions (the lender, acquirer, merchant, buyer) interprets and enforces. The infrastructure never acts unilaterally.**

For Submantle V1, a five-label system is sufficient and implementable: **New**, **Active**, **Under Review**, **Probationary**, and **Suspended**. A sixth meta-state — **Sandbox** — isolates test interactions from production scoring. The labels are additive to the trust score, not replacements for it.

---

## Research Method

Internal codebase reviewed:
- `prototype/database.py` — existing schema: `agent_registry`, `incident_reports`, `events`, `settings`
- `prototype/agent_registry.py` — existing trust model: `compute_trust()`, `record_incident()`, `record_query()`
- `research/council-product-market-fit-v2/plan-deepen-notes.md` — dependency chain analysis, existing gaps

External systems researched:
1. **Credit bureaus** (Experian, TransUnion, Equifax) — account status codes and dispute labels
2. **Mastercard MATCH list** — terminated entity file with reason codes
3. **Visa VAMP** (formerly VDMP/VFMP) — merchant monitoring program tiers
4. **Domain registries** (ICANN EPP status codes) — clientHold, serverHold, pendingDelete
5. **X.509 / PKI** (OCSP/CRL) — revoked, suspended, expired certificate labels
6. **Apple App Store Connect** — full submission and account status lifecycle
7. **eBay seller performance** — Below Standard / Above Standard / Top Rated with fairness mechanisms
8. **Stripe Connect** — Restricted / Restricted Soon / In Review / Rejected / Enabled
9. **W3C Bitstring Status List** — revocation, suspension, message labels for Verifiable Credentials
10. **Amazon Account Health Rating** — 0-1000 score with color-coded status tiers

---

## Section 1: How Analog Systems Do It

### 1.1 Credit Bureaus (Experian, TransUnion, Equifax)

Credit bureaus use numeric status codes (not human-readable labels) to communicate account state. The codes that matter for Submantle's design:

**Key status codes:**
- Code 11: Current account (equivalent to "Active")
- Codes 71-84: Delinquency ladder (30/60/90/120/150/180+ days overdue) — granular progression
- Code 93: Seriously past due, assigned to collections (equivalent to "Probationary")
- Code 97: Loss reported by credit grantor (equivalent to "Suspended")
- During dispute: "Account Information Disputed by Consumer" flag — equivalent to "Under Review"

**Critical design insight — the FCRA dispute label:**
When a consumer files a dispute, the account is flagged "under investigation." During this period, the disputed entry is **hidden from the FICO score** — it cannot hurt or help the score while review is pending. This is the credit bureau model for "pending state on incidents." The entity is not penalized while the investigation runs.

After investigation, the notation "account information disputed by consumer meets FCRA requirements" remains on the report permanently as an audit trail — even if the dispute is resolved. **The investigation history is visible to lenders.**

**What metadata lenders see:**
- The numeric status code
- The date the code was assigned
- Whether the account is currently disputed
- The furnisher (reporter) identity
- Original creditor, account open date, last activity date
- The complete payment history timeline

**Submantle lesson:** Status labels should be accompanied by the date applied, who triggered the transition, and the investigation history. The audit trail is part of the infrastructure's value.

---

### 1.2 Mastercard MATCH List (Terminated Merchant File)

The MATCH list is the purest example of the credit bureau model for severe status labels. Mastercard maintains a database of terminated merchants — acquiring banks are required to report terminations, and other banks query the database when evaluating merchant applications.

**How it works (neutral infrastructure model):**
- Mastercard does NOT block terminated merchants from getting a new merchant account
- Mastercard requires banks to ADD merchants to the list (reporting obligation)
- Banks independently query the list and decide whether to approve applications
- Mastercard provides data; banks make decisions

**Status: placed on MATCH list** — triggered by one of 14 reason codes:
1. Account Data Compromise
2. Common Point of Purchase
3. Laundering
4. Excessive Chargebacks (most common trigger)
5. Excessive Fraud
6. (Unused)
7. Fraud Conviction
8. Questionable Merchant Audit Program (Mastercard designation)
9. Bankruptcy/Liquidation/Insolvency
10. Violation of Standards
11. Merchant Collusion
12. PCI-DSS Noncompliance (removable upon compliance)
13. Illegal Transactions
14. Identity Theft

**Duration and removal:**
- Standard listing: 5 years from entry date
- Removal before 5 years: (a) original bank reports "added in error," (b) reason code 12 upon demonstrated PCI compliance
- After 5 years: automatic removal

**What data is shared:**
- Business name, owner name, address
- Date added
- Reason code
- Which bank added them
- The specific violation details

**Submantle lesson:** Severe status labels need reason codes, not just a label. "Suspended" without a reason code is opaque. "Suspended (reason: excessive_incidents)" is informative. Removal pathways must be explicit and time-bounded where possible.

---

### 1.3 Visa VAMP (Acquirer Monitoring Program)

Visa's VAMP (which consolidated VDMP and VFMP as of April 2025) is the definitive model for tiered risk communication without enforcement.

**How it works:**
- Visa calculates a VAMP Ratio (disputes + fraud combined) monthly for each merchant
- Banks are notified of where their merchants fall
- Visa does NOT block merchants — acquiring banks are responsible for remediation
- Banks develop remediation plans; merchants work with their banks

**Status tiers:**
- **No enrollment**: Below threshold — normal state
- **Advisory** (April-September 2025): Above threshold, notified, no penalties
- **Enrolled/Standard**: Above 2.2% VAMP ratio — remediation plan required within 15 days, additional $10/dispute fee
- **Excessive**: Further above threshold — higher penalties, bank liability shared

**Early warning tier (legacy, still instructive):**
The legacy VDMP had an explicit "Early Warning" tier at 0.65% dispute ratio. This is pure signal, no penalty — "you are trending toward a threshold." This is an extremely useful label for Submantle: a warning status before the entity reaches a formal enforcement threshold.

**Removal criteria:** Below enrollment threshold for **3 consecutive months** before exit. This prevents gaming by staying just under the line for one month.

**What metadata is communicated:**
- The ratio that triggered enrollment
- The threshold the entity exceeded
- The month of enrollment
- The acquiring bank receives the full calculation methodology
- Reason counts (enumeration attacks, dispute types)

**Submantle lesson:** (1) Use a warning tier before a formal "Under Review" label. (2) Require sustained behavior improvement before removing a negative label — "3 consecutive months below threshold" is a proven model. (3) The calculating entity (Visa/Submantle) communicates the data; the acting entity (bank/brand) makes the decision.

---

### 1.4 ICANN EPP Domain Status Codes

The EPP (Extensible Provisioning Protocol) system is the clearest example of a two-tier labeling architecture: registrar-applied codes vs. registry-applied codes.

**Two authorities, distinct scopes:**
- **Client codes** (registrar-applied): clientHold, clientTransferProhibited, clientUpdateProhibited, clientDeleteProhibited, clientRenewProhibited
- **Server codes** (registry-applied): serverHold, serverTransferProhibited, serverUpdateProhibited, serverDeleteProhibited, serverRenewProhibited

**The key labels:**
- `ok` — normal operating state (equivalent to "Active")
- `addPeriod` — just registered, 5-day grace period before deletion (equivalent to "New")
- `clientHold` — registrar-applied hold (non-payment most common trigger). Domain removed from DNS but can still be updated, transferred. Action by registrar.
- `serverHold` — registry-applied hold. Financial, legal, or operational reason. Higher authority, harder to remove.
- `pendingDelete` — terminal state, 5-day countdown, cannot be restored
- `redemptionPeriod` — 30-day recovery window after expiration, before pendingDelete

**What these teach Submantle:**
1. The `addPeriod` model is precisely what Submantle needs for "New" — a grace window where the entity is live but has special status.
2. `clientHold` vs `serverHold` maps to "reporter-applied" vs "Submantle-applied" status. Reporter requests Under Review; Submantle can apply Suspended independently.
3. `redemptionPeriod` before terminal deletion is a model for the recovery pathway — a structured window to fix the problem before permanent action.
4. EPP codes communicate the **authority level** of the status (who applied it). Submantle labels should carry this: "under_review (reporter: BrandX, incident_id: 4729)" vs "probationary (submantle: pattern detected)."

**Removal mechanisms:**
- Client codes: registrant contacts registrar → registrar removes
- Server codes: requires coordination between registrar AND registry
- Removal authority always matches application authority

---

### 1.5 X.509 Certificate Status (OCSP/CRL)

PKI certificate status is infrastructure communication at its most basic: a bit (or a few bits) that means "valid," "revoked," or "unknown."

**The three OCSP states:**
- `good` — valid, no revocation
- `revoked` — permanently invalid. Subdivided by reason:
  - `keyCompromise` — private key exposed
  - `cACompromise` — issuing authority compromised
  - `affiliationChanged` — certificate holder identity changed
  - `superseded` — replaced by new certificate
  - `cessationOfOperation` — entity stopped operating
  - `certificateHold` — **temporary, reversible hold**
  - `privilegeWithdrawn` — authorization revoked
  - `aACompromise` — attribute authority compromised
- `unknown` — no information available (equivalent to Submantle's "New" with no history)

**The certificateHold concept is directly applicable to Submantle:**
`certificateHold` is the only reversible revocation reason in X.509. A certificate on hold cannot be used but can be reinstated. This is the PKI equivalent of "Probationary" — not permanently revoked, but suspended pending resolution.

**W3C Bitstring Status List (2025 Recommendation):**
The W3C has formalized status labels for Verifiable Credentials:
- `revocation` — permanent, irreversible
- `suspension` — temporary, reversible
- `refresh` — new version available, current still valid
- `message` — arbitrary status codes (extensible)

The `statusSize` field allows multiple bits per credential entry, enabling up to 256 distinct status values per credential. This is directly relevant if Submantle ever needs fine-grained status values in VCs.

**Privacy architecture (directly applicable):**
The Bitstring Status List uses random index assignment (not sequential) to prevent correlation. If all revoked credentials cluster at low indices, an attacker can infer group behavior from list size. Random assignment prevents this. **Submantle should randomize status log indices/IDs to prevent correlation attacks.**

---

### 1.6 Apple App Store Connect

Apple's app submission lifecycle has the most granular label set of any system reviewed:

**Submission-level statuses:**
- `Waiting for Review` — queued, not yet examined
- `In Review` — active examination underway
- `Metadata Rejected` — binary acceptable, description/screenshots violate guidelines
- `Rejected` — full rejection with specific feedback in Resolution Center
- `Developer Rejected` — developer self-withdrew from review
- `Approved` — review passed, awaiting release
- `Ready for Sale` — live

**Account/app-level statuses:**
- `Active` — app available for download
- `Removed from Sale` — not available (can be re-listed)
- `Developer Removed from Sale` — developer-initiated removal
- `Suspended` — account-level action, no apps available

**Key design insights:**
1. "Metadata Rejected" is a precise surgical label — the binary is fine, a specific non-code element violated guidelines. This teaches Submantle that labels should be as specific as possible about what triggered them.
2. The Resolution Center is the communication channel — disputes and rejections happen there, with structured back-and-forth. Not email. Not general support. A dedicated resolution channel.
3. Suspension is account-level, not app-level. When an account is suspended, everything on it goes with it. This matches Submantle's model: an agent's status is entity-level.
4. "Limited Visibility" (discoverability reduced but not removed) is a label that doesn't exist explicitly in other systems but is relevant — degraded access without full suspension.

**What metadata is communicated:**
- To developer: specific violation reason, relevant guideline section, Resolution Center message thread
- To buyers/users: nothing (except for Suspension, where listings disappear)
- To Apple internally: full submission history, previous violations, account-level pattern

**Anti-gaming:** Apple considers "account information (for example, past history of policy violations)" when reviewing content. History is persistent and informs future review stringency. This is the ratchet effect — a clean record gets benefit of the doubt; a dirty record gets heightened scrutiny.

---

### 1.7 eBay Seller Performance Levels

eBay's seller performance system is the clearest analog to Submantle's bidirectional trust because it scores both sides of a transaction (sellers and buyers) and applies different visibility rules to different audiences.

**Status levels:**
- `Top Rated` — exceeds standards, publicly visible badge ("Top Rated Plus")
- `Above Standard` — meets minimum requirements, invisible to buyers
- `Below Standard` — fails minimum requirements, invisible to buyers but affects seller

**What triggers Below Standard:**
- Transaction defect rate > 2% OR
- Cases closed without seller resolution > 0.3% (or 2 cases)

**Review cycle:** Monthly evaluation. Next evaluation date shown to seller.

**What buyers see:** Only the Top Rated Plus badge. Below Standard is hidden.
**What sellers see:** Detailed dashboard with peer benchmarking.

**Consequences of Below Standard (without blocking):**
- Additional 5% final value fee
- Reduced search ranking (algorithmic, not announced)
- Blocked from Promoted Listings
**eBay never blocks a Below Standard seller from selling. The market adjusts.**

**Fairness mechanism (critical for Submantle):**
When a seller first falls Below Standard, they get a **3-month grace period**: no additional restrictions are applied, giving time to recover. If still Below Standard but showing improvement after 3 months, the grace period extends month-by-month as long as improvement continues. This is exactly the "Probationary" model Submantle needs — a structured recovery window with measurable progress.

**Gaming prevention:** Peer benchmarking. Sellers are compared to others with similar profiles, not absolute thresholds. This makes gaming harder — you can't manufacture defect rates to look "below average in a low-defect category" without actually being below average. Submantle could use a registration cohort model (similar agents registered within the same time window) for relative scoring context.

---

### 1.8 Stripe Connect Account Statuses

Stripe Connect provides the most technically precise labeling model, with machine-readable status fields at the capability level rather than just account level.

**Account-level labels:**
- `Enabled` — all capabilities active, charges_enabled and payouts_enabled both true
- `Restricted Soon` — requirements approaching deadline, warning state
- `Restricted` — at least one capability inactive, requirements past due
- `In Review` — Stripe actively verifying submitted information or watchlist check
- `Rejected` — declined by Stripe or platform (irreversible)

**Capability-level states (within an account):**
- `active` — capability available
- `inactive` — capability suspended
- `pending` — capability under evaluation

**What the API returns:**
```json
{
  "charges_enabled": true,
  "payouts_enabled": false,
  "requirements": {
    "disabled_reason": "requirements.past_due",
    "currently_due": ["business_profile.url"],
    "past_due": ["individual.verification.document"],
    "eventually_due": []
  },
  "capabilities": {
    "card_payments": "active",
    "transfers": "inactive"
  }
}
```

**Critically relevant: The "Restricted Soon" state.** Stripe provides a pre-warning before a capability actually becomes inactive. This is not a penalty — it's a signal. Submantle should have an equivalent: a label that says "you are trending toward a negative status" without applying that status yet.

**Visibility tiers:**
- Platform operators see: full requirements, risk signals, all metadata
- Connected account holders (Standard/Express): their own status, what they need to submit
- End users/buyers: nothing — status is entirely invisible to end users

**Submantle lesson:** Machine-readable status fields separate from human-readable labels. The API returns `status: "under_review"` AND `reason: "incident_pattern_detected"` AND `triggered_at: timestamp` AND `triggered_by: "reporter:BrandX"`. Both technical and layman interpretations coexist in the same payload.

---

### 1.9 Amazon Account Health Rating

Amazon's AHR is the most quantified label system, combining a numeric score with color-coded status labels.

**Score bands:**
- 200-1000: **Healthy** (green) — no deactivation risk
- 100-199: **At Risk** (yellow) — at risk of deactivation, prominently warned
- 0-99: **Unhealthy** (red) — eligible for deactivation or already deactivated

**What triggers each:**
AHR is a weighted composite of policy violations across three categories:
1. Customer service performance (Order Defect Rate, Cancellation Rate, Late Shipment Rate)
2. Product policy compliance (authenticity, safety, IP)
3. Listing policy compliance (prohibited items, accurate descriptions)

**What buyers see:** When a seller is deactivated (suspended), all listings vanish from search. The suspension itself is not labeled for buyers — the absence of listings is the signal.

**Appeal process:**
Amazon requires a "Plan of Action" (root cause + corrective actions + preventive measures). Review team evaluates the POA and supporting documents. Typical response time: 24-72 hours. No cap on resubmissions, but generic appeals are consistently rejected.

**Anti-gaming:** Amazon evaluates account history when reviewing appeals. A seller with multiple prior violations faces higher scrutiny. Clean history gets benefit of the doubt.

---

## Section 2: Cross-System Patterns

These patterns appear across 6+ of the 9 systems studied:

### Pattern 1: Labels Are Information, Not Enforcement
Every neutral infrastructure system studied communicates status without acting on it unilaterally:
- Visa communicates the VAMP ratio; the acquiring bank enforces remediation
- Mastercard maintains the MATCH list; other banks decide whether to approve applications
- Domain registries publish EPP status codes; DNS resolvers and TLDs implement them
- Stripe reports Restricted status; the platform decides what to do with restricted accounts

**For Submantle:** The label is the product. Brands consume the label and decide their own policy.

### Pattern 2: Pending/Buffer States Before Score Impact
Every mature system has a buffer between event and consequence:
- Credit bureaus: "under investigation" hides disputed items from the score during review
- Visa VAMP: 6-month advisory period before penalties (April-September 2025)
- Domain registries: `redemptionPeriod` (30 days) before `pendingDelete`
- eBay: 3-month grace period before Below Standard triggers additional restrictions

**For Submantle:** Incidents enter PENDING state. Only ACCEPTED incidents contribute to the Beta formula. This is not just a fairness feature — it is the universal design pattern for trustworthy infrastructure.

### Pattern 3: Graduated Progression, Not Binary
Systems that work well have multiple states between "fine" and "blocked":
- Visa: No enrollment → Early Warning → Standard → Excessive
- Stripe: Enabled → Restricted Soon → Restricted → Rejected
- eBay: Top Rated → Above Standard → Below Standard
- ICANN: ok → addPeriod → clientHold/serverHold → redemptionPeriod → pendingDelete
- Amazon: Healthy (200-1000) → At Risk (100-199) → Unhealthy (0-99)

**For Submantle:** The five-label sequence should have an explicit warning label before "Under Review." "Trending" or a numerical signal in the score itself can serve this function.

### Pattern 4: Authority-Labeled Status
The most transparent systems tag the status with its authority:
- EPP: `clientHold` (registrar-applied) vs `serverHold` (registry-applied)
- Stripe: `requirements` object distinguishes what the platform set vs. what Stripe set
- Credit bureaus: furnisher identity accompanies every status code

**For Submantle:** The label should carry who applied it — `reporter:BrandX` vs `submantle:pattern` vs `system:registration_age`.

### Pattern 5: Asymmetric Visibility
Status is shown differently to different audiences:
- eBay: Below Standard is invisible to buyers, visible to sellers with full detail
- Stripe: End users see nothing; platform operators see full capability matrix
- App Store: Rejection visible to developers with specific feedback; invisible to users
- Credit bureaus: Disputed status shown to lenders; detailed dispute process visible to consumer

**For Submantle:** Status labels are primarily for brands (demand side). Agents (supply side) see their own full status and the reason. Unrelated third parties see nothing beyond the trust score and public label tier.

### Pattern 6: Removal Requires Sustained Improvement
Systems that prevent gaming require duration, not just one good measurement:
- Visa VAMP: 3 consecutive months below threshold to exit
- eBay: Monthly evaluation; grace period extends with demonstrated improvement
- Mastercard MATCH: 5 years, or proven error/compliance
- ICANN: `redemptionPeriod` is fixed at 30 days, cannot be shortened

**For Submantle:** Probationary status should require a minimum number of incident-free interactions (not just a time period, since score is interaction-based, not time-based).

### Pattern 7: Labels Don't Replace Scores — They Augment Them
Every system pairs labels with quantitative metrics:
- Amazon: color label AND 0-1000 numeric score
- Visa: "Enrolled" label AND specific VAMP ratio percentage
- eBay: "Below Standard" label AND specific defect rate and peer percentile
- Credit bureaus: status code AND payment history timeline

**For Submantle:** Status labels are metadata on top of the Beta trust score. A brand queries and gets: `{trust_score: 0.73, status: "active", queries: 847, incidents: 0, registration_age_days: 234}`.

---

## Section 3: Proposed Submantle Label System

### V1 Label Set (Minimum Viable)

Six labels total. Five lifecycle states plus one meta-state.

---

**Label: NEW**

| Field | Value |
|-------|-------|
| Human label | "New" |
| Machine key | `new` |
| Analogy | Credit bureau `addPeriod`, Visa "no history" |
| Triggers on | Agent registration (automatic) |
| Score at entry | 0.5 (Beta prior: 1 query, 0 incidents) |
| Visible to brands | Yes, prominently. "Registered X days ago, no interaction history" |
| Visible to agent | Yes |
| What triggers exit | Automatic: first 25 interactions completed (configurable threshold) |
| Transitions to | ACTIVE (automatically) |
| Purpose | Signals new entity without history. Brands apply extra caution. "Perfect score, registered yesterday" is a red flag brands can spot. |

---

**Label: ACTIVE**

| Field | Value |
|-------|-------|
| Human label | "Active" |
| Machine key | `active` |
| Analogy | eBay "Above Standard," Stripe "Enabled," credit bureau code 11 |
| Triggers on | Automatic transition from NEW after 25 interactions |
| Score at entry | Variable — whatever they've earned |
| Visible to brands | Yes: trust score, query count, incident count, registration age |
| Visible to agent | Yes |
| What triggers exit | Incident report enters PENDING state (no status change yet); if ACCEPTED, may trigger UNDER_REVIEW |
| Transitions to | UNDER_REVIEW (if accepted incidents cross threshold), or can regress to NEW if deregistered and re-registered |
| Purpose | Normal operating state. The majority of agents should be here. |

---

**Label: UNDER_REVIEW**

| Field | Value |
|-------|-------|
| Human label | "Under Review" |
| Machine key | `under_review` |
| Analogy | Credit bureau "account disputed by consumer," Stripe "In Review," Apple "In Review" |
| Triggers on | Accepted incident count crosses threshold (e.g., first accepted incident with a verified interaction ID); OR Submantle detects deterministic pattern (velocity spike, reporter concentration) |
| Score during | Pending incidents DO NOT affect score while review is open. Score frozen at pre-incident value. |
| Visible to brands | Yes: "This agent has an open review. Pending incidents have not yet affected the trust score." |
| Visible to agent | Yes: reason for review, incident IDs, which reporter filed, expected timeline |
| What triggers exit | Review completes: (a) incident upheld → transitions to PROBATIONARY; (b) incident dismissed → returns to ACTIVE, score unaffected; (c) incident partially upheld → score adjusts, returns to ACTIVE with lower score |
| Duration | Target: automated review ≤ 48 hours; human review ≤ 7 days |
| Who applies | Reporter filing triggers UNDER_REVIEW; Submantle's automated pattern detection can also apply it |
| Transitions to | ACTIVE (dismissed/resolved favorably), PROBATIONARY (upheld) |
| Purpose | Investigation buffer. Prevents score destruction from single burst of incidents. Communicates active review to brands. |

---

**Label: PROBATIONARY**

| Field | Value |
|-------|-------|
| Human label | "Probationary" |
| Machine key | `probationary` |
| Analogy | eBay Below Standard grace period, Visa VAMP Standard enrollment, ICANN redemptionPeriod |
| Triggers on | Review completes and incident(s) are upheld; now affects score |
| Score during | Affected by accepted incidents. Score may be low. |
| Visible to brands | Yes: "This agent has accepted incidents on record. Current trust score: X. Entered probationary status on: [date]." |
| Visible to agent | Yes: incident count, what was upheld, minimum interaction requirement to exit |
| What triggers exit | Minimum N incident-free interactions (e.g., 50) completed since probationary entry. Deterministic — no subjective review. |
| Transitions to | ACTIVE (minimum interactions completed without new incidents), SUSPENDED (new serious incident while probationary) |
| Purpose | Recovery with accountability. Entity is not permanently damaged. Shows brands that the entity is in recovery mode. |

---

**Label: SUSPENDED**

| Field | Value |
|-------|-------|
| Human label | "Suspended" |
| Machine key | `suspended` |
| Analogy | Mastercard MATCH list, Apple Suspended, domain serverHold |
| Triggers on | (a) New serious incident while PROBATIONARY; (b) Pattern of incidents across multiple reporters meeting severity threshold; (c) Confirmed identity fraud |
| Score during | Score computable but flagged. Trust score is near-zero by definition (many incidents, low queries) |
| Visible to brands | Yes: "This agent is suspended. [Reason code]. Suspended on: [date]." |
| Visible to agent | Yes: reason code, incident IDs, appeal pathway |
| What triggers exit | (a) Successful appeal (must reference and dispute specific incident IDs); (b) Time-limited automatic reinstatement after 90 days for non-fraud suspensions; (c) Confirmed false-report pattern — Submantle rescinds suspension |
| Duration | Non-fraud: 90 days minimum before appeal/reinstatement. Fraud-confirmed: indefinite (5-year model from MATCH). |
| Reason codes (V1) | `excessive_incidents`, `pattern_detected`, `reporter_fraud_confirmed`, `identity_violation` |
| Transitions to | PROBATIONARY (after successful appeal or time-out), or permanent suspension for identity fraud |
| Purpose | Severe status for clear bad actors. Still communicates, never enforces. |

---

**Meta-State: SANDBOX**

| Field | Value |
|-------|-------|
| Human label | "Sandbox" |
| Machine key | `sandbox` |
| Analogy | Stripe test mode, Twilio SendGrid IP warmup, AWS SP-API sandbox |
| How activated | Agent registration includes `mode: sandbox` flag OR a separate sandbox token is issued alongside the production token |
| Score isolation | Sandbox interactions are NEVER counted toward the production trust score. Separate counter: `sandbox_queries`, `sandbox_incidents`. |
| Visible to brands | No. Brands querying a production score never see sandbox activity. |
| Visible to agent | Yes: full sandbox dashboard showing how score would look if sandbox activity counted |
| What triggers exit | Agent explicitly calls `graduate_from_sandbox()` endpoint, which freezes sandbox history and activates production token |
| Duration | No maximum duration — stays in sandbox until developer deliberately graduates |
| Purpose | Developer testing without polluting the production trust score. Enables builders to test incident reporting, verify score formula, and simulate edge cases. |

---

### Label Metadata Payload (for API responses)

Every entity query returns this structure alongside the trust score:

```json
{
  "agent_name": "ShoppingBot",
  "trust_score": 0.73,
  "trust_label": "active",
  "label_applied_at": "2026-02-14T09:00:00Z",
  "label_applied_by": "system:registration_threshold",
  "label_reason_code": null,
  "registration_age_days": 27,
  "total_queries": 847,
  "total_incidents": 0,
  "pending_incidents": 0,
  "open_reviews": 0,
  "sandbox_mode": false,
  "layman_summary": "This agent has been active for 27 days with 847 interactions and no confirmed incidents.",
  "technical_summary": "Beta trust score computed from 847 queries and 0 accepted incidents. Score initialized at 0.5, current: 0.73.",
  "registration_cohort": "2026-Q1",
  "query_velocity_flag": false,
  "diversity_flag": false
}
```

The `layman_summary` and `technical_summary` fields directly implement the "technical interpretation AND layman interpretation" requirement from the settled decisions.

---

## Section 4: Anti-Gaming Analysis

For each label, how can it be gamed, and what deterministic countermeasures exist?

### Gaming the NEW Label

**Attack:** Maintain "New" status permanently by registering fresh entities and abandoning them after score damage. Fresh start = 0.5 always.

**Countermeasure:** Registration age is visible to brands regardless of label. "New" is not a clean slate that hides history — it's a descriptor for entities WITH no history. A brand can set: "no agents registered less than 30 days ago." The label itself is the countermeasure.

**Second attack:** Batch-register many agents, use them as throwaways (make one interaction, get the free 0.5 score, discard).

**Countermeasure:** Throwaway agents don't accumulate real trust scores. They stay at 0.5. Brands requiring scores > 0.6 automatically filter them. No additional countermeasure needed — the formula handles this.

---

### Gaming the ACTIVE Label

**Attack:** Self-query inflation. Make 10,000 identical queries to push score toward 1.0.

**Countermeasures (deterministic, no ML):**
1. **Velocity cap:** Max N queries per hour counting toward trust (configurable, e.g., 100/hour). Excess queries are counted for billing but NOT for trust.
2. **Diversity requirement:** If >90% of queries are identical type, the repetitive portion does not accumulate trust. Query diversity floor.
3. Both countermeasures are transparent rules published in documentation. Not ML, not inference.

**Attack:** Coordinate with a friendly business to file false positive interactions, both sides inflating each other's scores.

**Countermeasure:** Interaction IDs are Submantle-issued. Both parties cannot manufacture interaction IDs that Submantle didn't generate. Submantle is the authoritative source of "did this interaction happen."

---

### Gaming the UNDER_REVIEW Label

**Attack:** File malicious reports against a competitor to put them in "Under Review," disrupting their business.

**Countermeasures:**
1. Filing an incident report requires: (a) a valid bearer token (registered member only), (b) a valid interaction ID (must have actually interacted with the target), (c) evidence.
2. **Reporter reputation:** Reporters who file incidents that are consistently dismissed accumulate a "false report rate." High false report rate = reports weighted less in triggering UNDER_REVIEW.
3. **Reporter concentration flag:** If >80% of pending incidents against an entity come from a single reporter, the review process flags this as potential coordinated attack.
4. **Velocity cap on report filing:** A reporter cannot file more than N reports per entity per time window (e.g., 3 per 7 days).

**Attack:** Flood Submantle with reports to keep many entities in UNDER_REVIEW permanently.

**Countermeasure:** Filing reports is rate-limited per reporter. Additionally, reporters who file many incidents that are dismissed face suspension of reporting privileges.

---

### Gaming the PROBATIONARY Label

**Attack:** Do the minimum interactions to exit probation, then immediately resume bad behavior.

**Countermeasure:** The minimum interaction count to exit probation is a floor, not a ceiling. Scoring is continuous. If an entity exits probation at a low trust score (say 0.3) and immediately accumulates more incidents, they re-enter UNDER_REVIEW quickly. The formula punishes this automatically — a low-trust entity with more incidents barely changes score numerically, but triggers review thresholds faster because their baseline is already low.

**Attack:** Create a second agent identity to avoid probation, operating from a clean 0.5 score.

**Countermeasure:** This is the Sybil attack. Submantle's locality model helps: on a given device, the same behavioral patterns re-emerge. Brands can also require minimum registration age and minimum interaction history — a fresh identity with 0.5 score gets treated as New (cautiously) regardless of how it was obtained.

---

### Gaming the SUSPENDED Label

**Attack:** Disputed false: claim suspension is unjust without referencing specific incident IDs.

**Countermeasure:** Appeals must reference specific incident IDs. "I didn't do anything wrong" is not an appeal. The agent must show: incident ID X is false because [evidence]. Structured appeal process prevents vague complaints.

**Attack:** Accept suspension, wait 90 days, start fresh with same Probationary history.

**Countermeasure:** Suspension history is permanent in the audit trail. Even after reinstatement, brands can query: "has this agent ever been suspended?" The answer and reason code are always visible. Reinstatement means PROBATIONARY, not ACTIVE — they don't get a clean slate.

---

### Gaming the SANDBOX Label

**Attack:** Developer builds a perfectly behaved sandbox agent, then "graduates" it into production to inherit a clean score.

**Reality check:** Sandbox interactions never count toward production score. Graduation means the production token starts fresh at 0.5. There is nothing to inherit. The sandbox label prevents gaming by design — there is no production score to game.

**Attack:** Use sandbox mode permanently to avoid accumulating incidents.

**Countermeasure:** Brands can (and should) reject sandbox-mode agents entirely. `sandbox_mode: true` means no real history. If a brand requires a production trust score, they simply require `sandbox_mode: false`. Sandbox is for development; brands are not required to accept sandbox entities.

---

## Section 5: V1 Implementation Notes

### What Exists in the Codebase Today

The current schema (`database.py`) has:
- `agent_registry` table with `total_queries`, `incidents`, `trust_metadata` (NULL)
- `incident_reports` table (no `status` column — incidents immediately affect the formula today)
- No `status` column on `agent_registry`
- No interaction log table
- No sandbox mode

### Minimum Schema Changes for Label System

**Add to `agent_registry`:**
```sql
status          TEXT    NOT NULL DEFAULT 'new',        -- new|active|under_review|probationary|suspended
status_reason   TEXT    DEFAULT NULL,                   -- reason code for non-active statuses
status_since    REAL    DEFAULT NULL,                   -- Unix timestamp when current status was applied
status_applied_by TEXT  DEFAULT NULL,                   -- 'system:registration' | 'reporter:NAME' | 'submantle:pattern'
sandbox_mode    INTEGER NOT NULL DEFAULT 0,             -- BOOLEAN: 0=production, 1=sandbox
sandbox_queries INTEGER NOT NULL DEFAULT 0,             -- sandbox interaction count
sandbox_incidents INTEGER NOT NULL DEFAULT 0            -- sandbox incident count
```

**Add to `incident_reports`:**
```sql
status          TEXT    NOT NULL DEFAULT 'pending',     -- pending|accepted|dismissed|disputed
interaction_id  TEXT    DEFAULT NULL,                   -- required for V2+, optional for V1
review_completed_at REAL DEFAULT NULL
```

**New method on `AgentRegistry`:**
`compute_status_label()` — pure function, takes agent record, returns current label with full metadata payload.

### Graduated Migration Path

The current `record_incident()` immediately calls `increment_agent_incidents()`, which immediately affects the formula. To implement pending state:

1. Stop calling `increment_agent_incidents()` in `record_incident()`
2. Add `review_incident(incident_id, outcome)` method — only calls `increment_agent_incidents()` when outcome = 'accepted'
3. Automated review for clear patterns (velocity spikes, single-reporter floods) can run as a background task
4. Human review queue populated when automated review is inconclusive

This change is additive — it does not break existing tests. The `increment_agent_incidents()` method still exists; it's just called at a different point in the workflow.

---

## Section 6: What Neutral Infrastructure Communicates Without Enforcing

The key insight from all systems studied: **neutral infrastructure builds trust with both sides by being reliably honest about what it knows, without making decisions that belong to someone else.**

Visa tells a bank: "This merchant has a 3.1% dispute rate." It does not tell the merchant whether to keep banking them. The bank decides. This is why both merchants and banks trust Visa — it doesn't favor either party.

Mastercard tells a bank: "This merchant was added to MATCH for Excessive Chargebacks on 2024-03-01." It does not tell the new bank whether to approve the merchant. The new bank decides. This is why both merchants (who can appeal errors) and banks (who get reliable data) participate in the system.

For Submantle:
- Submantle tells a brand: "This agent has trust score 0.45, is in PROBATIONARY status (entered 2026-02-20), has 3 accepted incidents, and 0 pending incidents."
- The brand decides whether to serve the agent, at what access level, and under what conditions.
- Submantle says nothing about what the brand should do. It provides honest, complete data.

**The label is the product. The decision is the brand's.**

---

## Sources Consulted

- ICANN EPP Status Codes: https://www.icann.org/resources/pages/epp-status-codes-2014-06-16-en
- Credit Bureau Status Codes (CUBase/CUNA): https://help.cubase.org/cubase/crtburstatuscodes.htm
- FCRA Dispute Process: https://www.consumerfinance.gov/ask-cfpb/how-do-i-dispute-an-error-on-my-credit-report-en-314/
- Mastercard MATCH List analysis: https://chargebacks911.com/match-list/
- Visa VAMP/VDMP/VFMP monitoring programs: https://www.chargebackgurus.com/blog/visa-dispute-and-fraud-monitoring-programs-vdmp-vfmp
- Visa VAMP 2025 changes: https://www.ravelin.com/blog/visa-vamp-changes-chargeback-disputes
- App Store Connect status lifecycle: https://aso.dev/app-store-connect/application-statuses/
- Apple App Store enforcement: https://support.google.com/googleplay/android-developer/answer/9899234
- Google Play enforcement: https://support.google.com/googleplay/android-developer/answer/9899234
- eBay seller performance standards: https://www.ebay.com/help/selling/seller-levels-performance-standards/seller-levels-performance-standards?id=4080
- eBay Below Standard guide: https://www.zikanalytics.com/blog/how-to-fix-below-standard-on-ebay/
- Stripe Connect status documentation: https://docs.stripe.com/connect/dashboard/review-actionable-accounts
- Amazon Account Health Rating: https://sellerengine.com/amazon-account-health-rating-guide-sellerengine/
- W3C Bitstring Status List v1.1: https://w3c.github.io/vc-bitstring-status-list/
- NIST SP 800-63-4 Digital Identity: https://pages.nist.gov/800-63-4/sp800-63.html
- Goodhart's Law and gaming metrics: https://medium.com/@claus.nisslmueller/goodharts-law-and-the-death-of-honest-metrics-e08cc756f93a
- X.509 OCSP/CRL: https://datatracker.ietf.org/doc/html/rfc6960
- SendGrid IP warmup (sandbox/warmup model): https://www.twilio.com/docs/sendgrid/concepts/reputation/warm-up-ip-addresses
