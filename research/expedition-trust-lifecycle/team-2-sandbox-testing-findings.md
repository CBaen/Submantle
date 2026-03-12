# Team 2 Findings — Sandbox and Testing Environments in Trust Systems

**Date:** 2026-03-12
**Research Angle:** Sandbox and Testing Environments in Trust Systems
**Model:** Claude Sonnet 4.6

---

## Executive Summary

Six external reference classes were examined: eBay's developer sandbox, payment processors (Stripe, PayPal), competitive gaming placement systems (FIDE chess, League of Legends, Valorant), marketplace cold-start onboarding (Uber, Airbnb), credit bureau entry pathways (secured cards, credit builder loans, authorized user piggybacking), and emerging AI agent sandbox infrastructure. Together they converge on a coherent pattern for Submantle.

The central finding: **the most durable sandbox designs share one architectural property — the sandbox and production environments are cryptographically and structurally separate, with no pathway for sandbox performance to automatically transfer into the live score.** The value of a sandbox is precisely that it cannot be farmed for live reputation. Anything that weakens that wall also weakens the sandbox's anti-gaming value.

Sandbox performance CAN be made visible to brands as a distinct, labeled signal — but it must be labeled as "test results," never incorporated into the Beta formula. This is the right architecture for Submantle.

---

## Section 1: Do Real Platforms Offer Practice Modes? (eBay, Uber, Airbnb)

### eBay — Developer Sandbox, No Consumer Practice Mode

eBay operates a full sandbox environment exclusively for developers building against its API. Key properties:
- Sandbox users are virtual accounts completely separate from production users.
- All money exchanged is test money. All listings are test listings.
- Reputation scores in sandbox are independent of production. No crossover.
- Call rate limits are actually *higher* in sandbox than production, allowing faster iteration.
- Unsupported features list exists — some production behaviors do not replicate in sandbox.

**Critical finding:** eBay provides no "practice mode" for regular new sellers on the live platform. There is no sandbox for end users. New sellers simply begin selling with their real reputation at stake. The developer sandbox is infrastructure for API integrators, not a consumer onboarding tool.

**What this means for Submantle:** eBay chose not to offer a consumer sandbox because eBay's model requires real transactions to build real reputation. Submantle's situation differs — agents need to *test their integration* before going live, which maps exactly to eBay's developer sandbox model, not a consumer model. Submantle's sandbox is for agent developers, not end users.

**Source:** eBay Developers Program documentation — [Sandbox overview](https://developer.ebay.com/api-docs/static/gs_understand-the-sandbox-and.html), [Sandbox benefits](https://developer.ebay.com/api-docs/static/gs_sandbox-benefits.html)

### Uber and Airbnb — No Sandbox; Protected First Period Instead

Neither Uber nor Airbnb offer a sandbox or practice mode for new drivers/hosts. Instead they use a different strategy: all interactions are live from day one, but the first period is *implicitly protected* through the rating system's statistical mechanics.

Uber's approach:
- New drivers are exposed to live ratings immediately.
- Rating deactivation thresholds are enforced (below ~4.5 stars = warnings, below ~4.0 = deactivation risk).
- But early ratings carry high variance and are acknowledged as less statistically reliable. A single bad rating matters less when you have 5 trips than when you have 500.

Airbnb's approach:
- No protected trial period. New hosts go live immediately.
- Trust is built through verification (government ID, property proof), not through a sandbox.
- The beta reputation dynamic naturally applies: early interactions have high uncertainty and low sample size.

**What this means for Submantle:** The "protected first period" concept in marketplaces is typically handled implicitly by Beta statistics (high variance at low sample size), not by an explicit sandbox. Submantle already has this built in — Beta(1,1) = 0.5 (unknown) naturally represents high uncertainty. A formal sandbox adds something different: a place to *test integration mechanics* before any score-affecting interactions occur.

**Source:** [Stanford research on Uber quality control](https://news.stanford.edu/stories/2025/08/uber-ride-sharing-quality-control-ratings-incentive-system-research), [First Round Review on marketplace trust](https://review.firstround.com/how-modern-marketplaces-like-uber-airbnb-build-trust-to-hit-liquidity/)

---

## Section 2: Competitive Gaming — Placement Matches and Calibration

### FIDE Chess — Provisional Phase (K=40 for First 30 Games)

FIDE's rating system has an explicit calibration phase:
- K-factor (how much a single game affects your rating) starts at 40 for the first 30 games.
- After 30 games, K drops to 20 (if under 2400) — smaller swings, more stable rating.
- To receive a FIDE rating at all, an unrated player must face 5 rated opponents and achieve a minimum performance rating of 1400.
- Entry requirement acts as an anti-noise filter: you can't get a rating from playing against unrated opponents.

**Key insight:** FIDE's provisional phase is NOT a sandbox. Games are real, results are published, and rating movements are real. The calibration is achieved through *higher volatility*, not through isolation. You play live games; your rating just moves faster while it finds its true level.

**Source:** [FIDE Rating Regulations, effective March 2024](https://handbook.fide.com/chapter/B022024)

### League of Legends — Placement Matches + Hidden MMR

League of Legends has two parallel systems:
- **Visible rank** (Iron/Bronze/Silver/... Challenger) — the public-facing tier.
- **Hidden MMR** (matchmaking rating) — the real number used for matchmaking and LP gain/loss calculations.

Placement mechanics:
- New season: play 5 placement matches to unlock your visible rank.
- K-factor starts high during placements — large rank swings are expected.
- Hidden MMR carries over season to season (soft reset, not full reset).
- Placement results determine *where* you start your climb, not your ceiling.

**Critical finding:** Riot announced for 2026 that it is introducing TrueSkill 2 to replace the current MMR system, and will add a "climb indicator" when visible rank lags behind actual MMR. This is a transparency improvement, not a sandbox.

**What this means for Submantle:** The two-layer system (hidden score + visible rank) is directly analogous to Submantle's architecture: internal Beta score (like MMR) + what brands see (the visible trust score). Brands could, in theory, see a "confidence interval" indicator when an agent's score is based on very few interactions — analogous to the provisional/placement phase indicator.

**Source:** [Riot Games LoL Ranked 2026 changes](https://esportsinsider.com/2025/12/riot-games-league-of-legends-ranked-2026-changes), [LoL placements support article](https://support-leagueoflegends.riotgames.com/hc/en-us/articles/4405783687443-Placements-Promotions-Series-Demotions-and-Decay)

### Valorant — Unrated Mode as True Sandbox

Valorant has a meaningful sandbox design:
- **Unrated mode** (casual play) uses a completely separate matchmaking system from ranked mode.
- Unrated games do NOT affect ranked MMR or RR (rank rating).
- Only competitive mode matches impact the ranked score.
- Players must reach account level 20 before accessing ranked at all — minimum investment required before reputation-affecting play begins.

**Quote from Riot's official FAQ:** "Only competitive matches impact your MMR and RR. Customs and unrated are safe for practice without risking your standing."

**This is the closest existing model to what Submantle wants to build.** Valorant's unrated mode is structurally identical to a Submantle sandbox:
- Real gameplay happens (not mock/fake).
- Results are visible and meaningful within their own context.
- No pathway for unrated performance to inflate ranked score.
- The two systems are structurally separated, not just labeled differently.

The Level 20 gate before ranked access is also directly applicable: a minimum number of interactions before score-affecting behavior begins.

**Source:** [Valorant Competitive Mode FAQ](https://support-valorant.riotgames.com/hc/en-us/articles/360047937633-VALORANT-Competitive-Mode-FAQ), [blix.gg Valorant ranking explained 2025](https://blix.gg/blog/news/valorant/valorant-ranking-system-explained-2025-edition/)

---

## Section 3: Credit Bureau Entry Pathways

### Secured Cards — Collateralized Entry

A secured credit card requires a cash deposit equal to the credit limit. The deposit is held as collateral; if the cardholder defaults, the issuer takes the deposit.
- Payment history IS reported to credit bureaus — this is live score-affecting behavior.
- The collateral reduces risk, enabling entry by people without credit history.
- This is NOT a sandbox — it's a risk-reduced live environment. Every payment counts.

**What this means for Submantle:** The secured card model is the *probation tier* analog, not the sandbox analog. An agent with limited history could be required to operate under more restrictive conditions (brands might set lower query caps or require more verification), but their interactions still count toward their real score. Different from a sandbox.

### Credit Builder Loans — Sequenced Entry

Credit builder loans (offered by Self, credit unions) work like this:
- Borrower takes out a small loan ($300-$1,000).
- Funds are held in a locked savings account, not disbursed.
- Borrower makes monthly payments for 12-24 months.
- Each on-time payment is reported to all three major bureaus.
- At the end, the savings account is released to the borrower.

The loan is designed purely to generate a payment history. The borrower never gets the money until the end. They're paying to prove reliability.

**Source:** [Federal Reserve overview of credit building products, December 2024](https://www.federalreserve.gov/econres/notes/feds-notes/an-overview-of-credit-building-products-20241206.html), [Experian credit builder loan explainer](https://www.experian.com/blogs/ask-experian/what-is-a-credit-builder-loan/)

**What this means for Submantle:** The credit builder loan is the closest credit bureau analog to a "probation with training wheels" concept. An agent developer could engage in a structured series of interactions under controlled conditions specifically to accumulate score. But — critically — these are LIVE interactions. They count. There is no sandbox in the credit bureau world because the bureau's value depends on every data point being real.

### Authorized User Piggybacking — The Gaming Attack

The authorized user pathway allows someone with no credit history to be added to an established account, gaining that account's history on their credit file. This is legitimate in its designed form (adding a family member to your card).

**The gaming version (commercial piggybacking):**
- Companies sell "tradeline rentals" — they add strangers as authorized users on high-credit accounts.
- The stranger's credit score improves while they never actually used the card.
- The FTC identified this as fraud in 2022. Lenders treat it as a red flag.
- FICO scoring models were updated to detect and downweight patterns consistent with commercial piggybacking.

**Anti-gaming response from credit bureaus:**
- Some issuers stopped reporting authorized users to bureaus entirely.
- FICO 8+ applies reduced weight to authorized user accounts that pattern-match commercial services.
- Mortgage lenders now screen explicitly for piggybacking patterns.

**Direct implication for Submantle's sandbox design:** The authorized user model maps precisely to the sandbox gaming attack Submantle must prevent. An agent developer could run a "perfect" sandbox session using a controlled environment — one where the counterparty is also their own agent, always responding perfectly. If sandbox results had ANY weight in the live score, this is the attack vector. The mitigation is the same: structural separation with no pathway from sandbox to live score, and detection of suspicious patterns (all interactions between same two parties, no diversity).

**Source:** [Experian piggybacking explainer](https://www.experian.com/blogs/ask-experian/what-is-piggybacking-credit/), [FTC fraud case reference via ScamBusters](https://scambusters.org/piggyback.html), [EzeCreditServices complete guide 2026](https://ezecreditservices.com/how-does-authorized-user-piggybacking-work/)

---

## Section 4: Payment Processor Sandboxes — The Best-Executed Model

### Stripe Sandboxes

Stripe's sandbox architecture is the gold standard for "test mode that cannot contaminate production."

Key properties:
- API objects in one mode are not accessible from the other. A test product cannot participate in a live payment. This is enforced at the object level, not just the account level.
- Sandboxes are isolated environments within the same account. Up to 5 sandboxes per account.
- Sandbox data cannot be copied to production (only settings can transfer, not transaction data or object records).
- Rate limits: sandbox has HIGHER call limits than production to allow rapid iteration. This is intentional — developers should be able to test freely without throttling.
- AI-generated test scenarios are now available in sandbox to simulate real-world payment patterns.
- User access control: sandbox access requires explicit role assignment (Sandbox User, Admin, Developer, Sandbox Admin). Not automatic.

**The structural isolation principle:** Stripe's sandbox is not a "test flag" on the same database. It is a physically separate environment with separate API keys, separate data stores, and explicit role access. The separation is architectural, not labeling.

**Source:** [Stripe Sandboxes documentation](https://docs.stripe.com/sandboxes), [Stripe dev blog on avoiding test mode tangles](https://stripe.dev/blog/avoiding-test-mode-tangles-with-stripe-sandboxes)

### PayPal Sandbox

PayPal's sandbox mirrors Stripe's approach:
- Self-contained virtual environment simulating live PayPal.
- Separate accounts, separate endpoints, separate credentials.
- No crossover between sandbox transactions and live account data.
- Designed for developers to test API integrations before going live.

**Source:** [PayPal sandbox testing guide](https://developer.paypal.com/tools/sandbox/)

### Xbox Live Reputation Sandbox

Microsoft's Xbox Live reputation system provides one more data point — a reputation sandbox for partners building against the Xbox platform:
- Partners can make reputation calls in sandbox environments.
- Sandbox calls allow artificially setting base reputation scores and zeroing out weightings for positive feedback.
- This creates test users with specific reputation configurations for testing purposes.
- RETAIL sandbox is explicitly excluded — you cannot test reputation manipulation against the live retail environment.

**Source:** Microsoft Game Development Kit documentation — reputation overview

---

## Section 5: What Anti-Gaming Mechanisms Already Exist in These Systems

Compiled from all reference classes:

| System | Attack | Countermeasure | Type |
|--------|--------|----------------|------|
| Credit bureaus | Commercial piggybacking | FICO model updates, lender screening, issuer stops reporting AUs | Statistical detection + policy |
| Credit bureaus | Fabricated payment history | Bureau only records what creditors report; creditors face legal liability for false reports | Structural (liability) |
| Valorant | Smurf accounts (high-skill player creates new account) | MMR calibrates based on in-game performance metrics, not just win/loss | Behavioral signal |
| Valorant | Duo queue manipulation | Penalty for duo queue partner having much lower/higher MMR | Mathematical constraint |
| FIDE chess | Playing weak opponents to farm rating points | Rating Performance minimum (1400) and rated opponent requirement before initial rating | Gatekeeping |
| Stripe | Fake test transactions contaminating production | Structural API key separation — impossible by architecture | Architectural isolation |
| eBay | Test account behavior affecting real reputation | Completely separate user populations — sandbox users have no production identity | Structural isolation |

---

## Section 6: Sandbox Gaming Vectors Specific to Submantle

Given the research above, these are the specific ways Submantle's sandbox could be gamed:

### Vector 1: Controlled Counterparty Farming

**How:** Agent developer registers two agents. Agent A is the one they want to look good. Agent B is a cooperative counterparty. In sandbox, A and B exchange thousands of interactions — all successful, no incidents. Developer then shows sandbox metrics as "proof of reliability."

**Why it's dangerous:** If sandbox results carry ANY weight toward live score (even through visibility/inference by brands), this is a real attack. Even if sandbox results are labeled as "test results," brands under time pressure may use them as a proxy.

**Countermeasure:** Sandbox records must include counterparty identity. A diversity requirement: sandbox records with fewer than N distinct counterparties should be flagged or discounted. The principle is the same as FIDE's requirement to face rated opponents — you must prove performance against independent parties.

### Vector 2: Perfect Sandbox → Bad Live Behavior

**How:** Developer builds a perfect sandbox record. Brands see the sandbox metrics before taking the agent on as a partner. Once live, agent behaves badly.

**Why it's dangerous:** This is the "résumé fraud" attack. The sandbox record has no predictive validity if it's fully controlled by the agent developer.

**Countermeasure:** Brands should understand that sandbox results measure *integration correctness*, not behavioral reliability. The labeling must make this explicit. "Sandbox: 1,200 test interactions, zero errors" means the agent's integration works. It says nothing about whether the agent will behave well against real counterparties under real conditions. Documentation and UI labeling must communicate this distinction clearly. This is not a technical problem — it is a communication design problem.

### Vector 3: Sandbox Pollution of Production Data

**How:** An agent developer accidentally (or intentionally) sends live traffic through the sandbox endpoint. Sandbox data accumulates at scale. If sandbox data can be blended into live score calculations (through any pathway), the live score is contaminated.

**Countermeasure:** Structural isolation (Stripe model). Sandbox tokens and live tokens must be cryptographically distinct. No API call to a sandbox endpoint should ever affect the live registry. This is an architecture decision, not a policy decision.

### Vector 4: Minimum Threshold Gaming

**How:** If Submantle introduces a "minimum interactions before score is shown" threshold (analogous to Valorant's Level 20 gate), an agent developer runs exactly N interactions to unlock score visibility, with all N being controlled interactions.

**Countermeasure:** The threshold is not a quality filter, it is a statistical confidence filter. The Beta formula already handles this: (N+1)/(N+2) with zero incidents at N=20 = 21/22 ≈ 0.95. But brands should see the sample size, not just the score. "Trust 0.95, based on 20 interactions" is qualitatively different from "Trust 0.95, based on 2,000 interactions." Registration age and sample size visibility (already planned in VISION.md) is the defense.

---

## Section 7: Architecture Recommendation for Submantle Sandbox

Synthesizing all reference classes, this is the design that fits Submantle's constraints:

### The Two-Layer Model (Valorant + Stripe Combined)

**Layer 1: Sandbox Registry (separate from live registry)**

A sandbox registration generates a sandbox token, stored in a separate table (or separate DB entirely). Sandbox tokens cannot authenticate against live endpoints. Live tokens cannot authenticate against sandbox endpoints. This is enforced at the cryptographic level — separate HMAC secrets for sandbox and live environments.

This is the Stripe model: not a flag, a separate environment with separate keys.

**Layer 2: Sandbox interaction log (never touches Beta formula)**

Sandbox interactions are logged in a sandbox-specific interaction table. These records accumulate performance metrics: response success rate, error types, latency patterns, protocol compliance. None of these records touch `total_queries` or `incidents` in the live `agent_registry` table.

This is the Valorant model: unrated matches are real, they have their own matchmaking, they are just structurally disconnected from ranked.

### What Brands Can See

Sandbox metrics can be made available to brands as a distinct, clearly labeled API response:

```
GET /api/trust/{agent_name}/sandbox-profile

{
  "agent_name": "my-assistant",
  "sandbox_interactions": 450,
  "sandbox_error_rate": 0.002,
  "sandbox_counterparty_diversity": 12,  // distinct counterparties
  "sandbox_last_active": "2026-03-10T...",
  "label": "TEST_RESULTS_ONLY",
  "warning": "Sandbox performance measures integration correctness, not behavioral reliability."
}
```

This is NOT part of the trust score response. It is a separate endpoint, with a separate label, designed to answer the question "does this agent's integration work?" — not "should I trust this agent?"

**Analogy:** A job candidate's portfolio (what they built in a controlled setting) versus their references (what real employers say about real work). Both are visible to a hiring manager. Neither is conflated with the other.

### Minimum Live Interaction Gate

Before an agent's live trust score is surfaced to brands, require a minimum number of live interactions (proposed: 10). This mirrors Valorant's Level 20 gate and FIDE's minimum 5 rated opponents.

- Below the threshold: brands see "Score: Pending (N/10 qualifying interactions)"
- The 0.5 prior still applies mathematically — the score exists, it just isn't surfaced until it is statistically meaningful
- This prevents "perfect score, 3 interactions" from appearing credible

This is already consistent with Submantle's existing pending state design for incidents. Apply the same principle to minimum interaction counts before score publication.

### What the Sandbox Produces That Has Real Value

The sandbox's legitimate value is:

1. **Integration testing** — verifies that the agent can correctly call Submantle's API, handle token auth, parse responses, submit incident reports in the right format.

2. **Performance benchmarking** — measures latency, error rates, and protocol compliance under load. This is the "test results" a brand might want to see before onboarding an agent.

3. **Onboarding friction reduction** — new agent developers can make mistakes (wrong format, missing fields, auth errors) without those errors counting against them. They learn the protocol safely.

4. **Debugging** — sandbox logs can be more verbose and detailed than production logs without privacy risk, since no real users or real counterparties are involved.

None of these benefits require sandbox results to affect the live score.

---

## Section 8: Labeling Sandbox Interactions

The research across all systems converges on one principle: **labeling is not enough if the underlying data is not structurally separated.**

Stripe learned this with test mode — developers kept mixing test and live API keys because both lived in the same dashboard. They built Sandboxes (separate environments with separate role access) specifically because labeling failed.

For Submantle, the recommendation is:

| Interaction Type | Token Type | Stored In | Affects Beta Formula | Visible to Brands |
|-----------------|------------|-----------|---------------------|-------------------|
| Live | Live token (HMAC with live secret) | `agent_registry.total_queries` | YES | YES — trust score |
| Sandbox | Sandbox token (HMAC with sandbox secret) | `sandbox_interactions` table | NO | YES — labeled "test results" |

The HMAC secret separation means it is cryptographically impossible to present a sandbox token as a live token. There is no "mode flag" to flip, no endpoint parameter to manipulate. The keys are different.

This satisfies the constraint: sandbox interactions are clearly distinct from live interactions, not by policy, but by cryptographic architecture.

---

## Section 9: What Existing Competitive Products Do

No competitive product (HUMAN Security, Mnemom, Zenity, Mastercard Verifiable Intent, Google UCP, cheqd) was found to offer a developer sandbox for agent behavioral trust testing as of March 2026.

- Mnemom wraps agent clients and requires cooperation — their "test mode" would be entirely under the agent developer's control, providing no independent signal.
- cheqd offers credential management but no behavioral scoring sandbox.
- Google UCP explicitly states it "does not solve which agents should be trusted."
- HUMAN Security is per-application; no developer sandbox for trust scoring.

**This means Submantle has an opportunity to be the first behavioral trust system with a well-designed developer sandbox.** A sandbox that works like Stripe's (structurally isolated, with higher rate limits, verbose logging, and no production data contamination) would differentiate Submantle as the developer-friendly trust infrastructure. "Test your integration safely before your score is at stake" is a compelling developer value proposition that no competitor currently offers.

---

## Section 10: Implementation Complexity Assessment (Solo Founder Lens)

Given that Submantle is a solo founder building V1, this section assesses what is feasible in which order.

**Minimal viable sandbox (low complexity, high value):**
- Add a `sandbox_mode: bool` field to the registration call.
- Sandbox registrations get tokens derived from a separate HMAC secret (single line change to `_make_token` in `agent_registry.py`).
- Sandbox queries write to a new `sandbox_interactions` table (new schema, new `increment_sandbox_query()` method in `database.py`).
- Sandbox queries never touch `total_queries` or `incidents`.
- Sandbox profile endpoint returns counts from `sandbox_interactions`.

Estimated scope: 1 new DB table, 2 new DB methods, 1 new API endpoint, 1 modified registration flow. Well within prototype scope.

**What to defer:**
- Counterparty diversity requirements (adds complexity, defensible to defer to V1.5)
- Sandbox rate limit configuration separate from live (nice to have, not blocking)
- AI-generated test scenarios (Stripe's newest feature — not relevant for V1)

**Recommended sequence relative to existing build priority:**

The current build priority (from CLAUDE.md) puts Dashboard depth at #5 and Trust layer wiring at #6. Sandbox infrastructure is a dependency of trust layer wiring — without a sandbox, agent developers have no safe place to test their trust interactions before real scores are at stake. Recommendation: build the minimal viable sandbox (described above) as part of #6, not as a separate item.

---

## Key Findings Summary

1. **No consumer-facing "practice mode" exists in any reference marketplace.** eBay, Uber, Airbnb all go live immediately. The developer sandbox (eBay) and statistical early-period uncertainty (Uber, Airbnb) serve different purposes.

2. **The Valorant model is the best direct analog for Submantle's sandbox.** Separate queues, separate scores, real gameplay, clearly labeled, no pathway from one to the other.

3. **The Stripe model is the best direct analog for the technical architecture.** Separate secrets, separate environments, no data copy from sandbox to production, higher limits in sandbox, explicit role access.

4. **Credit bureau history confirms the anti-gaming principle.** Authorized user piggybacking is the credit analog to sandbox farming. The defense is structural (FICO model updates detecting the pattern, issuer policy changes) not just labeling.

5. **FIDE's provisional phase and Valorant's Level 20 gate confirm minimum interaction gates.** A score based on 5 interactions should be surfaced differently than a score based on 5,000.

6. **Sandbox results can be visible to brands as "test results" but must never be incorporated into the Beta formula.** The API design must make this separation explicit and unambiguous in the response schema.

7. **The primary sandbox gaming vectors are counterparty farming and credential confusion.** Both are solved by the same architecture: cryptographic separation of sandbox and live tokens, plus counterparty diversity visibility in the sandbox profile.

8. **No competitor currently offers a developer sandbox for agent behavioral trust testing.** First-mover opportunity for Submantle.

---

## Sources

- [eBay: Understanding Sandbox and Production environments](https://developer.ebay.com/api-docs/static/gs_understand-the-sandbox-and.html)
- [eBay: Sandbox benefits](https://developer.ebay.com/api-docs/static/gs_sandbox-benefits.html)
- [Stripe: Sandboxes documentation](https://docs.stripe.com/sandboxes)
- [Stripe: Avoiding test mode tangles with Sandboxes (dev blog)](https://stripe.dev/blog/avoiding-test-mode-tangles-with-stripe-sandboxes)
- [PayPal: Sandbox testing guide](https://developer.paypal.com/tools/sandbox/)
- [FIDE Rating Regulations, effective March 2024](https://handbook.fide.com/chapter/B022024)
- [Riot Games: LoL Ranked 2026 changes (Esports Insider)](https://esportsinsider.com/2025/12/riot-games-league-of-legends-ranked-2026-changes)
- [Riot Games: LoL Placements, Promotions, Demotions support article](https://support-leagueoflegends.riotgames.com/hc/en-us/articles/4405783687443-Placements-Promotions-Series-Demotions-and-Decay)
- [Valorant: Competitive Mode FAQ (official)](https://support-valorant.riotgames.com/hc/en-us/articles/360047937633-VALORANT-Competitive-Mode-FAQ)
- [blix.gg: Valorant ranking system explained 2025](https://blix.gg/blog/news/valorant/valorant-ranking-system-explained-2025-edition/)
- [Federal Reserve: Overview of credit-building products, December 2024](https://www.federalreserve.gov/econres/notes/feds-notes/an-overview-of-credit-building-products-20241206.html)
- [Experian: Credit builder loan explainer](https://www.experian.com/blogs/ask-experian/what-is-a-credit-builder-loan/)
- [Experian: Credit piggybacking explainer](https://www.experian.com/blogs/ask-experian/what-is-piggybacking-credit/)
- [EzeCreditServices: Authorized user piggybacking complete guide 2026](https://ezecreditservices.com/how-does-authorized-user-piggybacking-work/)
- [Stanford: How Uber steers drivers toward better performance, 2025](https://news.stanford.edu/stories/2025/08/uber-ride-sharing-quality-control-ratings-incentive-system-research)
- [First Round Review: How marketplaces like Uber and Airbnb build trust](https://review.firstround.com/how-modern-marketplaces-like-uber-airbnb-build-trust-to-hit-liquidity/)
- [Northflank: How to sandbox AI agents in 2026](https://northflank.com/blog/how-to-sandbox-ai-agents)
- [Jentic: The Agentic Sandbox](https://jentic.com/blog/the-agentic-sandbox)
- [Help Net Security: Engineering trust for autonomous AI agents, March 2026](https://www.helpnetsecurity.com/2026/03/05/securing-autonomous-ai-agents/)
