# Validation Report: Behavioral Trust Gap (CLUSTER B)
## Date: 2026-03-11
## Validator Focus: Is the gap real and unoccupied?

**Note:** Assigned filename was validation-2.md, which already contains a different validator's work
(focus: Tailscale feasibility / Team 5 Go libraries / Team 3 economy completeness). Written here
to avoid overwriting that work. Orchestrator should reconcile file numbering.

---

## Evidence Challenges

### B1 — "No company offers portable, OS-level, deterministic behavioral trust for agents"

This claim holds on the OS-level and deterministic dimensions but overstates the portability gap.
Three companies missed by Team 3 are making credible portability claims as of March 2026:

**Vouched / KnowThat.ai** (Agent Checkpoint launched February 2026, $17M Series A):
Community-driven reputation directory where MCP servers report on agent behavior across platforms.
Explicitly markets "portable, verifiable histories" and reusable agent credentials across
organizations. Not OS-level, not deterministic (community-sourced feedback). But portability is a
stated design goal and is live — this is not a gap anymore in the vocabulary sense.

**t54 Labs** ($5M seed, February 2026, backed by Ripple and Franklin Templeton):
Real-time behavioral risk engine ("Trustline") using behavioral patterns, device context, code
audits, and mandates. Targets agent-initiated financial transactions. Claims cross-chain portability
across XRPL, Solana, Base, and Virtuals. Not OS-level, not privacy-preserving on-device, and
crypto-financial-rails only.

**Gen Agent Trust Hub** (February 4, 2026, NASDAQ: GEN — parent of Norton/NortonLifeLock):
Pre-install safety scanning for AI agent skills. Risk classification (Safe / Low / High / Critical).
Partnership with Vercel for skills.sh marketplace. This is defensive and pre-install only — no
behavioral history accumulation, no portable trust scores. Not a real competitor for Submantle's
use case today, but Gen has consumer device distribution that could enable OS-level behavioral
monitoring if they chose to extend the product.

**Previously identified but understated — HUMAN Security AgenticTrust:**
The team accurately described HUMAN as per-site behavioral scoring. That stands. However, HUMAN has
since open-sourced the "HUMAN Verified AI Agent," which uses HTTP Message Signatures and public-key
cryptography to authenticate agents and explicitly markets "stronger and more portable identity for
AI agents." HUMAN's trust scoring is still per-application, but their identity layer is now
portable. Portable identity is the prerequisite for portable trust. HUMAN is one product decision
away from closing that gap.

**Verdict:** The claim should be tightened from "no company" to "no company offers portable
behavioral trust derived from OS-level, deterministic, on-device observation." The broader
portability claim is no longer strictly accurate — it is accurate at the architecture level but
not at the market-positioning level. Vouched in particular occupies the same vocabulary.

---

### B4 — "Stripe articulated Five Levels of Agentic Commerce; trust cliff is at Level 3→4"

The Five Levels framework is confirmed at stripe.com/blog/three-agentic-commerce-trends-nrf-2026
and independently corroborated at johndschultz.com, businessengineer.ai, and in NRF 2026 coverage.
The framework is real.

The "trust cliff" label is Team 3's editorial framing, not Stripe's verbatim language. Stripe
describes the Level 3→4 transition as "the jump from 'help me decide faster' to 'decide for me' —
not an incremental shift." Team 3's "trust cliff" reframing is accurate in spirit.

One notable finding: a DEV Community post titled "Building Trust Infrastructure for the Agentic
Economy: A Response to Stripe's Five Levels" (attributed to an author associated with Mnemom)
explicitly builds on this framing to make the case for behavioral trust infrastructure. Third
parties in the behavioral trust space are already using Stripe's Five Levels as their canonical
hook. This strengthens the claim's real-world resonance and confirms the framing is landing with
the intended audience.

**Verdict:** Underlying facts verified. "Trust cliff" is an interpretation, not a direct quote.
Flag this in any public-facing materials that cite Stripe.

---

### B5 — "WEF projects AI agents market at $236B by 2034"

Confirmed: weforum.org/stories/2026/01/ai-agents-trust/ exists and makes this claim. The $236B
figure originates from Precedence Research (press release July 2025, globenewswire.com), which WEF
cites. This is a market research firm's projection, not original WEF analysis — standard practice
for WEF stories, but worth noting the confidence tier.

One precision risk: Precedence Research separately projects "Agentic AI" at $199B by 2034. The
$236B figure is for the "AI agents" category. How these categories are delineated is not
transparent. The directional magnitude (market in the hundreds of billions by 2034) is supported
by multiple independent projections. The exact $236B figure carries market-research-quality
confidence, not academic precision.

**Verdict:** Verified. Cite with confidence tier: "market research projections." Do not present
as a WEF original analysis figure.

---

### B6 — "Multiple IETF drafts note behavioral attestation is required but none specify how"

Confirmed and partially strengthened. Five IETF drafts were identified by Team 3. Validation
surfaced a sixth draft Team 3 missed: draft-jiang-seat-dynamic-attestation ("Dynamic Attestation
for AI Agent Communication"). This draft addresses long-lived session attestation where "agent
runtime posture can change frequently." It is closer to the behavioral problem than the other five.

However, draft-jiang covers runtime posture changes for platform TCB and agent manifest (models,
tools, policies) — not longitudinal behavioral scoring or portable behavioral history. The posture
being attested is configuration state, not behavior over time. The gap stands.

The standards landscape is slightly more active than Team 3's five-draft list suggests, but the
behavioral attestation gap remains unaddressed in all of them.

**Verdict:** Verified. Add draft-jiang-seat-dynamic-attestation to the IETF inventory. The gap
claim remains accurate.

---

### B2 — "Google UCP does not solve agent trust"

Confirmed via multiple independent 2026 sources. DataDome's March 2026 Security Boulevard post
explicitly states: UCP and ACP "don't address which agents should be trusted." This is now an
industry consensus statement cited by market commentators, not just a reading of the UCP spec. The
claim has been externally validated by Submantle's most directly comparable competitor.

**Verdict:** Verified and stronger than originally claimed. The quote in question is corroborated
industry-wide.

---

### B3 — "Mastercard Verifiable Intent explicitly excludes behavioral trust — authorization only"

Confirmed. Mastercard's own March 2026 description of Verifiable Intent is: a cryptographic
delegation chain linking consumer identity, specific instructions, and transaction outcome into a
tamper-resistant record. Partners listed (IBM, Worldpay, Fiserv, Checkout.com, Basis Theory, Adyen,
Getnet) include no behavioral trust vendor. No behavioral scoring, reputation, or dynamic trust
model is mentioned anywhere in Mastercard's materials.

**Verdict:** Verified.

---

### B7 — "AAIF has no working group addressing behavioral trust"

Confirmed. Direct search of aaif.io returns AAIF's working group scope as: protocol stewardship
(MCP, goose, AGENTS.md), governance, regulatory alignment, security, and observability. No
behavioral trust working group found. The security and observability working groups are adjacent
but not equivalent.

**Verdict:** Verified. Note for strategy: AAIF's observability working group is the most proximate
entry point if Submantle wanted to contribute a spec.

---

### B8 — "ERC-8004 is feedback-based, not behavioral observation"

Confirmed. The ERC-8004 Reputation Registry is built on a `giveFeedback(...)` interface — post-hoc
structured feedback submitted by clients or peer agents after interactions. Per the EIP text and
multiple secondary sources (Allium, CoinDesk, Whales Market), this is explicitly retrospective
feedback, not runtime behavioral observation.

One nuance the team did not flag: the ERC-8004 spec allows off-chain scoring, meaning a third
party could theoretically build runtime behavioral observation and write results back to the registry
using the identity layer as the anchor. This is not being done today. But ERC-8004 is not
architecturally incompatible with behavioral observation — it just does not implement it.

**Verdict:** Verified for current state. Flag the theoretical extension as a future risk: if
someone builds runtime behavioral scoring on top of ERC-8004's identity layer and writes to the
registry, that directly competes with Submantle's attestation layer.

Separate factual note not in this cluster but relevant: Validation-2.md (the pre-existing report)
found that ERC-8004 is still in Draft status as an EIP. Team 3 described it as "live mainnet
January 29, 2026" — this appears to conflate a specific contract deployment with EIP finalization.
The EIP itself is not a finalized Ethereum standard. This does not affect the B8 behavioral
observation claim but is a factual error the expedition synthesis should correct.

---

## New Competitors Found

### 1. Vouched / KnowThat.ai — Closest conceptual overlap
- Funding: $17M Series A (September 2025)
- Product: Agent Checkpoint (February 2026). Community reputation directory at knowthat.ai.
  MCP servers report agent behavior. Proposes MCP-I (MCP-Identity) extension for portable
  cryptographic agent credentials.
- Explicitly positions as "portable behavioral histories" for agents.
- Critical limitations: Community feedback model (reputation-by-testimony, not
  reputation-by-measurement). No on-device computation. No deterministic formula. No EU AI Act
  safety advantage. No process-level OS awareness. The portability is user-reported, not observed.
- Threat level: Medium. Vouched will attract funding and market attention in the same vocabulary
  space as Submantle. The conceptual overlap is high; the architectural overlap is low.

### 2. t54 Labs — Crypto-rails behavioral risk engine
- Funding: $5M seed (February 2026). Investors: Ripple, Franklin Templeton, Anagram, PL Capital.
- Product: Trustline real-time risk engine. Evaluates behavioral patterns, device context, code
  audits, mandates for agent-initiated financial transactions.
- Runs across XRPL, Solana, Base, Virtuals.
- Critical limitations: Financial-rails only. Blockchain-native (on-chain = inherently public,
  no on-device privacy). No OS-level process awareness. No deterministic formula cited.
  Crypto-native audience limits general market reach.
- Threat level: Low for Submantle's general-purpose use case. Medium for the crypto/DeFi segment.

### 3. Gen Agent Trust Hub — Consumer device company with device distribution
- Parent: Gen Digital (NASDAQ: GEN), owner of Norton, Avast, LifeLock.
- Product: Pre-install safety scanning for AI agent skills. Risk classification. Partnership with
  Vercel for skills.sh marketplace.
- Critical limitations: Defensive and pre-install only. No behavioral history accumulation.
  No portable trust scores. No B2B trust score API.
- Threat level: Low today. Elevated watch if Gen adds post-install behavioral monitoring. Gen has
  consumer device distribution (Norton's ~500M device install base) that would give them OS-level
  access at scale if they chose to use it. This is the sleeping giant scenario.

---

## Verified Claims

**B2** — Google UCP does not solve agent trust. Confirmed by UCP spec and independently by
DataDome, Security Boulevard, and multiple March 2026 industry commentators.

**B3** — Mastercard Verifiable Intent is authorization-only. Confirmed by Mastercard's own
materials. No behavioral trust component anywhere in the product or partner stack.

**B5** — WEF $236B market projection exists and cites a real underlying source (Precedence
Research July 2025). Confidence tier: market research projection, not academic analysis.

**B6** — IETF drafts acknowledge behavioral attestation need without specifying a solution.
Confirmed across five cited drafts plus one additional (draft-jiang-seat-dynamic-attestation)
not in Team 3's inventory.

**B7** — AAIF has no behavioral trust working group. Confirmed via aaif.io search.

**B8** — ERC-8004 Reputation Registry is feedback-based, not runtime behavioral observation.
Confirmed via EIP text and multiple secondary analyses.

**B4** — Stripe Five Levels framework is real and widely cited. The "trust cliff" label is Team
3's interpretation, not Stripe's verbatim phrase. The interpretation is accurate.

---

## Missing Angles

**1. Socure behavioral monitoring status not resolved.**
Team 3 flagged Socure as having behavioral monitoring on their roadmap. Validation search found
Socure's October 2025 RiskOS AI Suite launch but no evidence of a shipped agent behavioral scoring
product. Socure ($94M+ raised) has enterprise identity distribution and the stated intent to
monitor autonomous agents. This requires a targeted follow-up search in 60 days.

**2. Microsoft Multimodal Agent Score not examined.**
A Microsoft Dynamics blog post "Multimodal Agent Score: A New Standard for Evaluating AI Agents"
(February 4, 2026) surfaced in validation searches but was not investigated. If Microsoft is
building an agent evaluation/scoring standard, that is a significant competitive signal that could
reshape the standards landscape.

**3. YC W26 and S25 batches not systematically scanned.**
Validation search found general YC batch data and several agent observability/evaluation startups
(Lucidic AI, Respan, Salus, Cascade) but no behavioral-trust-specific company. A direct scan of
the YC W26 batch was not completed. This remains an open risk.

**4. IETF draft-jiang-seat-dynamic-attestation not in Team 3's inventory.**
This draft covers runtime posture attestation for long-lived agent sessions. It is closer to the
behavioral gap than the other five IETF drafts. It does not fill the gap, but it narrows the
characterization from "nobody is working on anything like this" to "one draft attempts runtime
posture, not behavioral history." The gap claim remains accurate; the nuance should be added.

**5. The ERC-8004 EIP status discrepancy was not Team 3's focus.**
Team 3's B8 claim concerns behavioral observation vs. feedback. The separate factual issue — that
ERC-8004 is still a Draft EIP, not a finalized standard — is raised by Validator 2 in the existing
validation-2.md. Both validations should be read together on ERC-8004.

---

## Overall Assessment

The behavioral trust gap is real. The strongest version of B1 — that no company offers portable
behavioral trust derived from OS-level, deterministic, on-device observation — holds under direct
search pressure. Three companies missed by Team 3 (Vouched, t54 Labs, Gen) have entered the
vocabulary space of "portable agent trust" since the Q4 2025 research that produced the Forrester
BATMS category. None of them threaten the architectural distinctiveness of Submantle's core
proposition: all three lack OS-level process awareness, all three lack deterministic non-ML scoring,
and all three lack on-device privacy-preserving computation. The closest conceptual competitor is
Vouched/KnowThat.ai, whose community reputation model overlaps with Submantle's portability thesis
at the marketing level while differing fundamentally at the architecture level — reputation-by-
testimony versus reputation-by-measurement. The IETF and AAIF findings confirm that no standards
body has filled or is currently filling this gap. Market signals from WEF, Stripe, and a16z are
independently verified. The primary risk is not that the gap is occupied — it is not. The primary
risk is that Vouched, Gen, or an undetected YC company captures the "portable agent trust"
narrative in market perception before Submantle ships the architecturally superior version. Speed
of narrative matters here as much as architectural correctness.
