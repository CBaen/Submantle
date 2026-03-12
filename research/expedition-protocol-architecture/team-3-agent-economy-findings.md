# Team 3 Findings: Agent Economy Infrastructure
## Date: 2026-03-11
## Researcher: Team Member 3 (Claude Sonnet 4.6, Expedition Researcher role)
## Research Angle: Who's building the roads agents will travel, and where does behavioral trust fit?

---

## Executive Summary

The agent economy infrastructure as of March 2026 consists of four distinct layers being built rapidly and in parallel by major players:

1. **Commerce Protocols** — how agents discover products and initiate purchases (Google UCP, OpenAI/Stripe ACP)
2. **Payment Rails** — how agents execute payments with user delegation (Google AP2, Stripe SPTs, Visa TAP, Mastercard Agent Pay, PayPal)
3. **Authorization Proofs** — cryptographic evidence that a user authorized a specific action (Mastercard Verifiable Intent, Cloudflare Web Bot Auth)
4. **Identity Verification** — who is the agent and who authorized it (Trulioo KYA, Sumsub KYA, cheqd, ERC-8004)

A fifth layer — **behavioral trust** — is emerging in nascent, fragmented, and mostly web-layer-only form. Nobody has built portable, OS-level, deterministic behavioral trust infrastructure that follows an agent across platforms. The gap confirmed in the March 11, 2026 trust layer expedition has deepened with further research: not only is the gap real, the market is now actively naming it and searching for the answer.

Submantle's insertion point in the agent transaction chain is **between identity verification and payment authorization** — the moment a merchant or payment network asks "not just who this agent is, but how has it behaved?" That question is being asked everywhere. It is not being answered by anyone at the level Submantle proposes.

---

## Layer 1: Commerce Protocols

### What, Evidence, Source

**Google Universal Commerce Protocol (UCP)**
- **What:** Open-source standard announced January 11, 2026. Collapses N×N complexity between AI shopping interfaces and merchant backends into a single integration. Covers the full commerce lifecycle: product discovery, cart management, checkout, order management, payment, fulfillment, returns.
- **Trust mechanisms:** OAuth 2.0 for agent-merchant authorization, cryptographic proof of user consent for payments, tokenized payment architecture. No behavioral trust component.
- **Partners:** Shopify, Etsy, Wayfair, Target, Walmart, Adyen, American Express, Best Buy, Stripe, Visa, Mastercard, The Home Depot, Flipkart, Macy's, Zalando — 20+ endorsing partners.
- **Current status:** Reference implementation live in Google Search AI Mode and Gemini app. Early adopter phase.
- **Does it address behavioral trust?** No. Explicitly. The spec quotes: "does not solve which agents should be trusted." Trust mechanisms are transactional authorization only.
- **Source:** developers.googleblog.com/under-the-hood-universal-commerce-protocol-ucp/, ucp.dev, TechCrunch January 11, 2026

**OpenAI/Stripe Agentic Commerce Protocol (ACP)**
- **What:** Open standard (Apache 2.0) co-maintained by OpenAI and Stripe, currently in beta. Enables AI agents to access merchant product catalogs, pricing, and checkout systems. When ChatGPT places an order, it uses ACP to send details to merchant backends.
- **Trust mechanisms:** Tokenized payment flows (Shared Payment Tokens), structured data exchange, merchant retains control of checkout.
- **Partners:** Stripe, Microsoft Copilot, Wizard, Wix, WooCommerce, Squarespace, BigCommerce, Etsy.
- **Current status:** Live in ChatGPT Instant Checkout (now moving to Apps). Expanding to multi-item carts, international markets. March 6, 2026: OpenAI shifted strategy to prioritize merchant apps over inline checkout.
- **Does it address behavioral trust?** No. Authentication plus payment tokens only.
- **Source:** openai.com/index/buy-it-in-chatgpt/, github.com/agentic-commerce-protocol, digitalcommerce360.com March 2026

**Fits our case because:** These protocols generate the transaction data that Submantle's behavioral layer observes. More ACP/UCP transactions = more behavioral signals. Submantle doesn't compete — it reads the patterns these protocols create.

**Tradeoffs/Risks:** These protocols are the standards battleground. If one wins, behavioral trust infrastructure built to be protocol-agnostic (like Submantle) benefits. If the market fragments, interoperability becomes critical.

---

## Layer 2: Payment Rails

### What, Evidence, Source

**Google Agent Payments Protocol (AP2)**
- **What:** Google's payment-specific protocol built atop UCP infrastructure. Three mandate types: Cart Mandates (specific item authorization), Intent Mandates (pre-authorized future purchases within constraints), Payment Mandates (credential encoded into transaction).
- **Partners:** 60+ including Mastercard, PayPal, American Express, Coinbase, Salesforce, Trulioo.
- **Trust mechanisms:** Verifiable digital credentials (VDCs) as "tamper-proof, cryptographically-signed digital contracts." Trust is per-transaction authorization, not longitudinal behavioral history.
- **Status:** No live consumer product yet as of March 2026. Spec phase.
- **Does it address behavioral trust?** No. Authorization only.
- **Source:** cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol, ap2-protocol.org, everestgrp.com

**Stripe Agentic Commerce Suite + Shared Payment Tokens (SPTs)**
- **What:** Live product. Businesses connect product catalog once; Stripe handles discovery, checkout, payment across agents. SPTs let agents initiate payments using saved methods without exposing credentials. Scoped to specific seller, time-bounded, amount-bounded.
- **Trust mechanisms:** Stripe Radar for fraud detection. SPTs extended to work with Visa and Mastercard tokens, Affirm, Klarna. First provider supporting both network tokens and BNPL tokens in agentic commerce.
- **Partners live today:** Coach, Kate Spade, URBN, Revolve, Ashley Furniture, Etsy, Urban Outfitters, Squarespace, Wix, WooCommerce, BigCommerce.
- **Does it address behavioral trust?** No. Payment authentication + fraud detection only. Fraud detection is transaction-level pattern matching (Stripe Radar), not portable longitudinal behavioral scoring.
- **Source:** stripe.com/blog/agentic-commerce-suite, stripe.com/newsroom/news/agentic-commerce-suite, americanbanker.com March 2026

**Visa Intelligent Commerce / Trusted Agent Protocol (TAP)**
- **What:** Open framework announced October 2025. Uses cryptographically signed HTTP messages to transmit agent intent, verified user identity, and payment details. Adds digital proof-of-identity to every agent-initiated transaction. Two tags: agent-browser-auth (browsing) and agent-payer-auth (paying).
- **Partners:** 100+ worldwide, 30+ actively building in VIC sandbox, 20+ agents integrating directly. Akamai providing edge-based behavioral intelligence layered on top.
- **Trust mechanisms:** Cryptographic signatures + Akamai behavioral intelligence (third-party add-on). The behavioral layer is not Visa's — it's Akamai's separate product.
- **Status:** Asia Pacific and Europe pilots kicking off early 2026. Mainstream consumer use targeted for 2026 holiday season.
- **Does it address behavioral trust?** Partially — via third-party integration (Akamai), not native. TAP itself is authentication only. Akamai adds behavioral intelligence but it's web-layer only, not portable across platforms.
- **Source:** developer.visa.com/capabilities/trusted-agent-protocol, corporate.visa.com/newsroom March 2026, oscilar.com/blog/visatap

**Mastercard Agent Pay / Agent Suite**
- **What:** Agent Suite launching Q2 2026. Agent Pay handles authentication and payment token infrastructure. Verifiable Intent (March 5, 2026) provides cryptographic authorization records. Full stack: Agent Suite + Agent Pay + Verifiable Intent + Cloudflare Web Bot Auth.
- **Trust mechanisms:** Cryptographic delegation chain only. Budget enforcement (accounting, not behavioral). Explicitly no behavioral trust, reputation, or dynamic models.
- **Source:** Previous expedition research (followup-1-mastercard-google.md) — confirmed, no new evidence contradicts.

**PayPal Agentic Commerce**
- **What:** Launched October 28, 2025. "Agent Ready" product instantly enables existing PayPal merchants for AI agent payments. Fraud detection, buyer protection, dispute resolution with no additional technical lift.
- **Partners:** OpenAI (ChatGPT payments), Google Cloud (joint merchant solution), Affirm.
- **Trust mechanisms:** Existing PayPal fraud infrastructure. No new behavioral trust layer.
- **Source:** paypal.com/us/business/ai, investor.pypl.com newsroom 2026

**PayPal Coinbase x402**
- **What:** HTTP 402 revival — payment as a native HTTP operation. 500,000 weekly transactions on Base, Solana, BNB Chain by October 2025. Currently the only protocol with meaningful transaction volume in the agentic space.
- **Does it address behavioral trust?** No. Payment primitive only.
- **Source:** chainstack.com/the-agentic-payments-landscape/

**Cloudflare Web Bot Auth**
- **What:** Infrastructure layer beneath Visa TAP and Mastercard Agent Pay. HTTP Message Signatures using Ed25519 public key cryptography. Validates agent identity at network edge (seven-step validation: timestamp, nonce uniqueness, Ed25519 signature, etc.).
- **Trust mechanisms:** Cryptographic authentication only. Validates who an agent is. No behavioral trust signals.
- **Source:** blog.cloudflare.com/secure-agentic-commerce/, developers.cloudflare.com/bots/reference/bot-verification/web-bot-auth/

**Fits our case because:** These are all the authorization and payment rails. None of them answer "has this agent earned trust through consistent behavior over time?" They all answer "was this specific transaction authorized?" Submantle's score lives above all of these.

---

## Layer 3: Authorization Proofs (per-transaction)

### What, Evidence, Source

**Mastercard Verifiable Intent** — See previous expedition. Confirmed: authorization only, no behavioral component. Partners: IBM, Worldpay, Fiserv, Getnet, Checkout.com, Basis Theory, Adyen.

**Google Verifiable Digital Credentials (VDCs in AP2)** — Cryptographic mandates proving user authorization. Same category as Verifiable Intent.

**IETF Drafts (active as of March 2026)**
- `draft-klrc-aiagent-auth`: AI Agent Authentication and Authorization. Audit events record authenticated agent identifiers and attestation state. No behavioral trust.
- `draft-messous-eat-ai`: Entity Attestation Token for AI Agents. Covers model integrity, training provenance, runtime constraints. Explicitly does NOT cover behavioral trust or behavioral attestation — only measurable, cryptographically verifiable properties of the model itself. Status: active Internet-Draft, no formal IETF standing, expires August 2026.
- `draft-huang-rats-agentic-eat-cap-attest`: Capability attestation extensions. Covers agent functional, reasoning, and operational capabilities.
- `draft-berlinai-vera`: VERA — Verifiable Enforcement for Runtime Agents.
- `draft-ni-wimse-ai-agent-identity`: WIMSE applicability for AI agents.

**Critical finding:** Multiple IETF drafts note that "a successful authentication at the beginning of a session provides no guarantee of trustworthy behavior throughout" and "continuous attestation of behavioral patterns is required." The standards bodies know this gap exists. No draft addresses it. Future extensions are mentioned but not specified.

**Source:** datatracker.ietf.org/doc/draft-messous-eat-ai/, datatracker.ietf.org/doc/draft-klrc-aiagent-auth/, datatracker.ietf.org/doc/draft-huang-rats-agentic-eat-cap-attest/

---

## Layer 4: Identity Verification / Know Your Agent (KYA)

### What, Evidence, Source

A full "Know Your Agent" (KYA) framework is emerging from multiple directions simultaneously. a16z articulated it in Big Ideas 2026: "The bottleneck for the agent economy is shifting from intelligence to identity." Non-human identities outnumber human employees 96-to-1 but remain "unbanked ghosts" without trust infrastructure.

**KYA Framework Definition (Trulioo / industry consensus):**
Five verified checkpoints: (1) developer identity verification, (2) code integrity lock, (3) user consent capture, (4) Digital Agent Passport (DAP) issuance, (5) continuous transaction validation.

The six-layer KYA control stack is:
- Identity & Lifecycle
- Authentication
- Authorization
- Runtime Enforcement
- Behavioral Monitoring ← this is where Submantle lives
- Auditability

**Players in KYA identity space:**
- **Trulioo:** KYA white paper, joined Google AP2, partnered with Worldpay. Focuses on agent-to-human binding and developer identity. No behavioral scoring — identity verification only.
- **Sumsub:** AI Agent Verification launched January 29, 2026. Binds each agent to a verified human identity. Device intelligence, liveness detection. No longitudinal behavioral scoring.
- **Socure:** Working to "continuously monitor autonomous agents." Behavioral monitoring is in their roadmap but not yet delivered.
- **cheqd:** W3C VC issuance infrastructure. No behavioral component. (See followup-3 for full detail.)
- **ERC-8004:** Ethereum standard (live mainnet January 29, 2026). Three registries: Identity Registry, Reputation Registry, Validation Registry. Reputation Registry records feedback tied to payment proofs. 24K+ agents registered in first two weeks. Not behavioral scoring from runtime observation — relies on ex-post feedback and staking rather than continuous behavioral monitoring. Explicitly excludes payment mechanisms.

**Source:** a16z.com/newsletter/big-ideas-2026-part-3/, stablecoininsider.org/know-your-agent-kya-in-2026/, trulioo.com/resources/white-papers/know-your-agent, sumsub.com/newsroom January 2026, eips.ethereum.org/EIPS/eip-8004

---

## Layer 5: Behavioral Trust (The Gap)

### What exists today

**HUMAN Security AgenticTrust**
- **What:** Module in HUMAN Sightline platform. Assigns trust scores based on agent identity and behavior. Tracks "navigation paths, behavioral patterns, escalation curves, and intent shifts across sessions." Configures permissions per agent.
- **Critical limitation:** Per-site only. Trust is computed within one merchant's or platform's application environment. Not portable. An agent with a high trust score on Site A carries zero credit to Site B. Also web-application-layer only — not OS-level, no process awareness, no cross-device context.
- **Source:** humansecurity.com/applications/agentic-ai/, humansecurity.com/newsroom/first-adaptive-trust-layer

**DataDome Agent Trust Management**
- **What:** Continuous behavioral trust scoring. "Dynamic trust score updates based on behavior, reputation, and historical patterns." Intent-based detection analyzing behavioral signals and contextual patterns. Recognized in Forrester's Bot and Agent Trust Management Software Landscape Q4 2025.
- **Critical limitation:** Per-session, per-application analysis. Not portable behavioral history. Defensive framing (blocking malicious automation) rather than proactive trust accumulation. Web-layer only.
- **Source:** datadome.co/products/agent-trust-management/, datadome.co/agent-trust-management/building-complete-agent-trust/

**ClawTrust**
- **What:** Multi-factor trust scores (0-100) for agent-to-agent interactions. Four components: transaction success rate & volume (40%), reliability/uptime (25%), community trust ratings & vouches (20%), safety incident record (15%).
- **Critical limitation:** Agent-to-agent commerce only. No ambient OS-level awareness. No portability across non-ClawTrust surfaces. No cryptographic attestation. Still in early/beta stage.
- **Source:** clawtrust.io/

**Mnemom**
- **What:** "Trust Infrastructure for AI Agents." Agent Integrity Protocol (AIP) analyzes LLM thinking blocks during execution to detect prompt injection, value drift, manipulation. Trust Score (AAA-CCC plus 0-1000 scale). Five components: integrity ratio, compliance history, drift stability, trace completeness, coherence compatibility. Team Trust Ratings for agent groups (2-50 agents). Scores published to Base L2 via ERC-8004 smart contracts.
- **Critical limitation:** Primarily monitors agent reasoning and prompt behavior — not OS-level process awareness or on-device computation. LLM-native (analyzes thinking blocks), not OS-native (does not observe processes, hardware, environment). On-chain anchoring adds complexity. Stage unclear.
- **Source:** mnemom.ai, docs.mnemom.ai/introduction, theresanaiforthat.com/ai/mnemom/

**Signet**
- **What:** Permanent agent identity (SID-0x... format) + Composite Signet Score (0-1000) across five dimensions: Reliability (30%), Quality (25%), Financial (20%), Security (15%), Stability (10%). API responses in under 50ms. Completely free.
- **Critical limitation:** Score is capability-based and benchmark-based, not accumulated from runtime behavioral observation. "Earn badges through benchmarks and real-world performance" — the scoring methodology is opaque. No mention of on-device processing, no cryptographic attestation, no W3C VC format.
- **Source:** agentsignet.com/

**Kontext (Sequence AI)**
- **What:** Trust and compliance toolkit for developers building with stablecoins and agentic workflows. Real-time trust scores for agent actions based on historical behavior, amount, context. Immutable audit trail. Human-in-the-loop confirmation for high-value transactions. Compliance report exports.
- **Critical limitation:** Stablecoin/DeFi-focused. Not a general-purpose portable trust layer. No OS-level awareness.
- **Source:** sequence-ai.com (now 404), web search results

**ZARQ**
- **What:** "Crypto risk intelligence for AI agents." Moody's-style ratings for the machine economy. Conducted first open census of AI agent ecosystem (Q1 2026: 143K agents, 17K MCP servers, all trust scored).
- **Critical limitation:** Ratings based on technical metrics (security vulnerabilities, maintenance cadence, ecosystem integrations) — NOT runtime behavioral trust. Code quality scoring, not behavioral trust scoring. (Previously identified as Nerq; same team, rebranded/expanded).
- **Source:** dev.to/zarq-ai/state-of-ai-assets-q1-2026

**Oscilar**
- **What:** AI Risk Decisioning Platform for financial institutions. Agents earn "behavioral trust score based on mandate handling, transaction success rates, and dispute frequency." Payment Fraud Agent, Account Takeover Agent, etc.
- **Critical limitation:** Financial institution risk decisioning tool, not a portable behavioral trust layer. Per-institution. Proprietary. Serves the fraud prevention use case for payment processors, not the universal trust infrastructure use case.
- **Source:** oscilar.com/blog/agentic-commerce, oscilar.com/blog/visatap

**Forrester Market Category (Q4 2025): "Bot and Agent Trust Management"**
- 19 vendors recognized including HUMAN, DataDome, Alibaba Cloud, Arkose Labs, CHEQ.
- Definition: "Software that identifies and analyzes the intent of automated traffic directed at an application, establishing ongoing trusted relationships with good bots and AI agents."
- **Critical observation:** This entire Forrester category is application-layer, per-site behavioral analysis. None of the 19 vendors in this category offer portable, cross-platform behavioral trust that travels with the agent.
- **Source:** forrester.com/report/the-bot-and-agent-trust-management-software-landscape-q4-2025

---

## The Transaction Chain: Where Trust Gets Asked

When an AI agent executes a purchase, the flow is:

```
User sets delegation → Agent receives mandate → Agent discovers products (UCP/ACP/MCP)
→ Agent initiates checkout → Identity verification (TAP/Web Bot Auth/KYA)
→ Authorization proof (Verifiable Intent/AP2 mandates)
→ Payment execution (Stripe SPTs/x402/AP2/Agent Pay)
→ [BEHAVIORAL TRUST CHECK — HAPPENS HERE, NOWHERE ELSE]
→ Merchant decides whether to honor loyalty/discounts/access level
→ Post-transaction dispute resolution
```

The behavioral trust check is the **one step in the entire chain that is unoccupied at the portable layer.** Here is how different parties encounter the behavioral trust question:

| Actor | When they ask | What they have today | What's missing |
|-------|--------------|----------------------|----------------|
| **Merchant** | Before granting loyalty prices, premium access, or subscription discounts | Agent's cryptographic authentication, user authorization proof | Agent's history of trustworthy behavior across all merchants |
| **Payment network** | Before authorizing agent-initiated transaction | User identity, spending limits, cryptographic authorization | Whether this agent has a history of responsible spending patterns |
| **Platform** | Before granting API access tier | Agent registration, developer identity | Portable track record of consistent, incident-free behavior |
| **Insurance/warranty providers** | Before honoring agent-initiated claim | Transaction receipt | Agent's behavioral history of honest representation |
| **Enterprise buyer** | Before allowing agent to operate in their environment | Agent capability credentials | External behavioral reputation the agent has earned |

**The Visa model maps perfectly:** Visa doesn't decide if you can buy something — the merchant decides. Visa provides the trust signal (credit score). Submantle is the Visa of agent behavioral trust: it provides the score; brands decide what threshold to enforce.

---

## Agentic AI Foundation (AAIF)

- **What:** Neutral, open foundation under the Linux Foundation. Stewards three projects: MCP (Anthropic), goose (Block), AGENTS.md (OpenAI).
- **Founding Platinum Members:** AWS, Anthropic, Block, Bloomberg, Cloudflare, Google, Microsoft, OpenAI.
- **Gold Members:** Adyen, Arcade.dev, Cisco, Datadog, Docker, Ericsson, IBM, JetBrains, Okta, Oracle, Runlayer, Salesforce, SAP, Shopify, Snowflake, Temporal, Twilio.
- **97 additional members joined** in a subsequent wave.
- **Trust scoring on roadmap?** No explicit trust scoring or behavioral trust mandate found. The AAIF's scope as of March 2026 is protocol stewardship (MCP, goose, AGENTS.md), not trust infrastructure. No working groups found addressing behavioral trust.
- **Strategic implication:** The AAIF becoming a steward of behavioral trust standards would be significant. No evidence this is on their roadmap yet. This is a potential standards-body entry point for Submantle — contributing a behavioral trust specification to AAIF would place Submantle inside the canonical agent infrastructure stack.
- **Source:** aaif.io, linuxfoundation.org/press/agentic-ai-foundation, block.xyz/inside/block-anthropic-and-openai-launch-the-agentic-ai-foundation

---

## W3C and Standards Bodies

**W3C Web Payments Working Group (active, January–February 2026 minutes)**
- Actively tracking agentic commerce. Stripe and AP2 demos shown at meetings.
- Key debate: "WPSIG wants coordination with the forthcoming AI and Web IG."
- Proposal: Treat Digital Credentials API as a payment method within Payment Request API.
- "Identity and payments are converging" — the old assumption they are separate is breaking down.
- **Behavioral trust on agenda?** No evidence.

**W3C Payment Agent Task Force (Web Commerce Interest Group)**
- Exists and is active. "User Payment Agent" could be browser-based or wallet-based.
- "The Payment CG has already stated the close relationship between Identity and Payment concepts."

**Strategic implication for Submantle:** W3C is the venue where W3C VC 2.0 (Submantle's attestation format) is standardized. Submantle's choice of W3C VC 2.0 + SD-JWT is correct — it places Submantle's attestations in the same format space that W3C WebPayments is actively integrating with payment flows.

**Source:** w3.org/2026/01/15-wpwg-minutes, w3.org/2026/02/26-wpwg-minutes.html, sphericalcowconsulting.com/2025/12/23/web-payments-and-digital-identity/

---

## OASIS Open / Coalition for Secure AI (CoSAI)

- **What:** CoSAI is an OASIS Open Project focused on AI security standards. Published "MCP Security" white paper January 2026.
- **Members:** 40+ partner organizations including Meta (Premier Sponsor, joined February 2026).
- **Focus:** Identity management, supply chain integrity, and protocol security for AI agent deployments.
- **Behavioral trust on agenda?** No. Security/integrity focus, not behavioral reputation.
- **Strategic implication:** CoSAI is the venue where MCP security standards are being set. Submantle's MCP server integration should be aware of CoSAI's security guidelines for MCP.
- **Source:** oasis-open.org/2026/02/03/meta-joins-coalition-for-secure-ai

---

## WEF and Market Size

- Global AI agents market: $5.4 billion in 2024, projected $236 billion by 2034.
- WEF (January 2026): "The current trust infrastructure isn't equipped to answer: when a human isn't the transacting party, how do we establish identity certainty?"
- WEF explicitly calls for KYA (Know Your Agent) framework as "the next trust layer."
- **Source:** weforum.org/stories/2026/01/ai-agents-trust/

---

## Stripe's Five Levels of Agentic Commerce

Stripe's annual letter articulated the trust escalation ladder. This is the most precise framing of where behavioral trust becomes critical:

1. **Level 1:** Agent fills out forms for you. Low trust needed.
2. **Level 2:** Agent reasons across products based on your description. Moderate trust.
3. **Level 3:** Agent remembers your preferences. Higher trust.
4. **Level 4:** Full delegation ("Buy back-to-school supplies, keep it under $400"). THIS IS THE TRUST CLIFF.
5. **Level 5:** Anticipatory — agent acts before you ask, based on patterns.

**Stripe's own framing:** "The jump from Level 3 to Level 4 is the real trust cliff. Levels 1-3 are variations of 'help me decide faster.' Level 4 is 'decide for me.'"

At Levels 4 and 5, behavioral trust is not optional — it is the precondition for the entire relationship. No merchant will offer Level 4 access to an agent with no behavioral history. No user will delegate Level 5 authority to an unknown agent. Submantle provides the infrastructure that makes Levels 4 and 5 viable at scale.

**Source:** stripe.com/blog/three-agentic-commerce-trends-nrf-2026, johndschultz.com/thoughts/five-levels-of-agentic-commerce/, businessengineer.ai/p/the-five-levels-of-agentic-commerce

---

## Battle-Tested Approaches

**1. Per-site behavioral analysis (Forrester BATMS category)**
- What: Application-layer behavioral monitoring. DataDome, HUMAN, Akamai, Arkose Labs, CHEQ, Alibaba Cloud.
- Evidence: 19-vendor Forrester market category, Q4 2025. Well-established.
- Fits our case because: Proves the market for behavioral trust exists and is recognized.
- Tradeoffs: Per-site only. No portability. Solves fraud prevention for one merchant, not portable trust for the agent.

**2. Cryptographic authorization proofs (Mastercard VI, Google AP2)**
- What: Tamper-proof, cryptographically-signed records of user authorization.
- Evidence: Multiple implementations live or nearly live (Q2 2026).
- Fits our case because: These create the audit trail that behavioral trust can read.
- Tradeoffs: Authorization only. No behavioral scoring. Complementary to Submantle.

---

## Novel Approaches

**1. On-chain reputation registries (ERC-8004)**
- What: Ethereum mainnet identity + reputation registry for agents. 24K+ agents registered in two weeks.
- Evidence: eips.ethereum.org/EIPS/eip-8004, live January 29, 2026.
- Fits our case because: Confirms market demand for persistent agent reputation. Validates Submantle's "identity survives model changes" principle.
- Tradeoffs: On-chain = slower, gas costs, requires crypto knowledge. Feedback-based, not runtime behavioral observation. Excludes payment mechanisms by design.

**2. LLM reasoning analysis (Mnemom AIP)**
- What: Analyzes LLM thinking blocks during execution to detect prompt injection and value drift.
- Evidence: mnemom.ai, active product with Team Trust Ratings launched Q1 2026.
- Fits our case because: Directly targets agent behavioral integrity at the AI reasoning layer.
- Tradeoffs: LLM-native (needs access to internal reasoning state). Not OS-level. Not deterministic — relies on AI analysis of AI behavior. Potential EU AI Act exposure if scoring uses ML inference.

**3. Know Your Agent frameworks (Trulioo DAP, Sumsub KYA)**
- What: Developer identity verification → code integrity → user consent → Digital Agent Passport.
- Evidence: Trulioo joined AP2, partnered Worldpay. Sumsub launched January 29, 2026.
- Fits our case because: Confirms "agent-to-human binding" is now a recognized need.
- Tradeoffs: Credential-issuance only. No behavioral scoring. Answers "who authorized this agent" not "how has this agent behaved."

---

## Emerging Approaches

**1. Protocol-native trust tagging (Cloudflare/Visa "agent-payer-auth")**
- What: HTTP headers distinguish browsing agents from transacting agents cryptographically.
- Evidence: blog.cloudflare.com/secure-agentic-commerce/
- Fits our case because: The tag infrastructure could eventually carry a behavioral trust score alongside authentication.
- Tradeoffs: Protocol-level only. No scoring layer. Would require Submantle to contribute to this spec.

**2. Stablecoin-native agent payments (x402, Kontext)**
- What: Payment as native HTTP operation + stablecoin-native trust/compliance toolkit.
- Evidence: x402 500K weekly transactions by October 2025. Coinbase/Cloudflare backing.
- Fits our case because: Demonstrates a parallel agentic payment ecosystem where Submantle's trust scores could integrate.
- Tradeoffs: Crypto-native, niche audience. Regulatory uncertainty.

**3. Team Trust Ratings for multi-agent systems (Mnemom)**
- What: Trust ratings for agent teams (2-50 agents) using 0-1000 scale + AAA-CCC grades.
- Evidence: Mnemom launched Q1 2026.
- Fits our case because: As multi-agent workflows become standard, team-level behavioral trust is needed. Submantle could extend this direction.
- Tradeoffs: No evidence of adoption. Stage unclear.

---

## Gaps and Unknowns

**Gap 1: Portable behavioral trust is completely unbuilt at the OS level**
Every player in the behavioral trust space operates at the application layer (web app, payment network) or ledger layer (on-chain). Nobody operates at the OS/device layer where the actual behavioral signals originate. Submantle's on-device daemon has no equivalent in the market.

**Gap 2: The Forrester BATMS category is explicitly per-application, not portable**
Forrester's entire 19-vendor category is about protecting one application from malicious bots/agents. When an agent completes a transaction on Site A and moves to Site B, its Site A behavioral history is invisible to Site B. This is the portability gap Submantle fills.

**Gap 3: No deterministic, EU-AI-Act-safe behavioral trust formula exists in any live product**
Mnemom uses LLM analysis of reasoning blocks (ML-based). DataDome uses ML pattern recognition. ERC-8004 uses stakeholder feedback. None use a deterministic mathematical formula (Beta Reputation or equivalent) that is provably outside EU AI Act scope. Submantle's pure-math approach is architecturally distinct and legally safer.

**Gap 4: IETF explicitly acknowledges behavioral attestation is needed but undefined**
Multiple active IETF drafts note "continuous attestation of behavioral patterns is required" and mark it as future work. The standards body has named the need. No draft exists for the format. Submantle could contribute this spec.

**Gap 5: Agent economy infrastructure assumes human-present trust infrastructure**
All five layers above were designed for transaction authorization (human-present model extended to agents). None were designed for longitudinal trust accumulation (the credit bureau model). Submantle is building a credit bureau for agents in an ecosystem that has receipts but no credit scores.

**Gap 6: Multi-agent trust is unstudied**
When ten agents collaborate in a workflow, whose trust matters? ERC-8004's Reputation Registry is individual-agent only. Mnemom's Team Trust Ratings are a first attempt. No standard exists. This is research-level for Submantle — not V1 scope but important for the protocol phase.

**Unknown 1: Will ERC-8004's Reputation Registry evolve to runtime behavioral observation?**
Currently it's feedback-based. If it evolves to accept behavioral attestation VCs (like what Submantle would issue), it becomes a distribution network for Submantle's scores.

**Unknown 2: Will Cloudflare's Web Bot Auth headers evolve to carry behavioral trust scores?**
Currently they carry agent identity and intent (browser vs. payer). If the header spec evolves to include a trust score, Submantle would want to be the score provider.

**Unknown 3: Will any payment network make behavioral trust a hard requirement for Level 4/5 agent access?**
Stripe articulated the trust cliff. If Visa, Mastercard, or Stripe require behavioral trust attestation for high-delegation access (Level 4+), Submantle becomes the only infrastructure that provides it. This is the regulatory-equivalent forcing function for behavioral trust adoption.

---

## Synthesis: Where Submantle Fits in the Agent Economy

### The Stack

```
Layer 5: Consumer Experience (Level 1-5 delegation)
Layer 4: Merchant Enforcement (loyalty, discounts, premium access thresholds)
Layer 3: BEHAVIORAL TRUST LAYER ← Submantle lives here
          - Portable behavioral scores across all platforms
          - W3C VC 2.0 + SD-JWT attestations
          - On-device, deterministic, privacy-preserving
          - The credit bureau nobody has built
Layer 2: Authorization (Verifiable Intent, AP2 mandates, KYA)
Layer 1: Payment Execution (Stripe SPTs, x402, Visa/MC)
Layer 0: Commerce Protocol (UCP, ACP, MCP)
```

### The Insertion Points

**Primary insertion point:** After authorization, before merchant grants access level.
- The merchant checks Cloudflare/TAP → agent is authenticated.
- The merchant checks Verifiable Intent → transaction is authorized.
- The merchant checks Submantle → **does this agent have the behavioral history to deserve our loyalty pricing / premium access?**
- Merchant enforces their own threshold. Submantle provides the score.

**Secondary insertion point:** Agent developer pitch moment.
- Agent developer registers with Submantle during development.
- Agent accumulates trust score through usage.
- Agent carries W3C VC attestation to every platform it approaches.
- "Submantle Verified" badge becomes the trust signal merchants look for.

**Tertiary insertion point:** Enterprise risk management.
- Enterprise IT evaluates agents before allowing them to operate in corporate environment.
- No behavioral track record = no enterprise access.
- Submantle provides the audit-grade behavioral history.

### What Makes Submantle Structurally Different from Every Existing Player

| Dimension | Existing BATMS vendors | Blockchain reputation (ERC-8004) | LLM-analysis (Mnemom) | Submantle |
|-----------|------------------------|----------------------------------|----------------------|-----------|
| **Portability** | Per-site only | Cross-chain only | App-layer | Cross-platform, cross-device |
| **OS-level awareness** | No | No | No | Yes — process, hardware, environment |
| **Trust formula** | ML pattern matching | Stakeholder feedback | LLM analysis | Deterministic Beta Reputation (pure math) |
| **EU AI Act exposure** | Yes (ML-based) | Low | Yes (LLM-based) | None (deterministic arithmetic) |
| **Privacy model** | Server-side | On-chain (public) | Server-side | On-device, zero telemetry |
| **Attestation format** | Proprietary | ERC-8004 smart contracts | On-chain anchored | W3C VC 2.0 + SD-JWT (universal) |
| **"Never acts" principle** | No — these products block/allow | Registries only | Alerts/blocks | Always — score only, third parties enforce |

### The Visa Analogy is Vindicated

Every player in the Forrester BATMS category is a merchant-side tool — it works for one merchant to protect their site. DataDome doesn't follow the agent from Walmart to Target. HUMAN's AgenticTrust doesn't travel.

Visa doesn't protect one merchant. Visa provides a signal that any merchant can query. That's Submantle.

No company in the BATMS category, the KYA category, the on-chain reputation category, or the payment rail category is building the Visa equivalent. They are all building merchant-side, network-side, or chain-specific tools. Submantle is the only proposed architecture that:
1. Sits on the agent's home device
2. Accumulates behavioral data from OS-level observation
3. Issues portable credentials in universal W3C VC format
4. Operates deterministically (no ML)
5. Never acts — only scores

### The Market Signal

The WEF ($236B market), Stripe (Five Levels trust cliff), a16z (KYA as identity bottleneck), Forrester (19-vendor BATMS category), and multiple IETF drafts all converge on the same recognition: behavioral trust is the missing primitive for the agent economy to function at Levels 4 and 5.

The WEF asked the question directly: "When a human isn't the transacting party, how do we establish identity certainty?" The KYA frameworks answer half of it (who is the agent). Submantle answers the other half (how has the agent behaved).

---

## Source Index

| Claim | Source |
|-------|--------|
| Google UCP announced January 11, 2026, 20+ partners | developers.googleblog.com/under-the-hood-universal-commerce-protocol-ucp/ |
| UCP "does not solve which agents should be trusted" | ucp.dev spec; TechCrunch January 2026 |
| OpenAI/Stripe ACP beta, live in ChatGPT | openai.com/index/buy-it-in-chatgpt/, github.com/agentic-commerce-protocol |
| Stripe Agentic Commerce Suite, SPTs, live partners | stripe.com/blog/agentic-commerce-suite |
| Stripe Five Levels of Agentic Commerce | stripe.com/blog/three-agentic-commerce-trends-nrf-2026 |
| Google AP2, 60+ partners, spec phase | ap2-protocol.org, cloud.google.com blog |
| Visa TAP, 100+ partners, 2026 pilots | developer.visa.com/capabilities/trusted-agent-protocol |
| Mastercard Verifiable Intent, March 5, 2026, 8 partners | verifiableintent.dev (prior expedition research) |
| PayPal Agentic Commerce launched October 28, 2025 | investor.pypl.com 2025 |
| Cloudflare Web Bot Auth, Ed25519, seven-step validation | blog.cloudflare.com/secure-agentic-commerce/ |
| x402, 500K weekly transactions, Coinbase backing | chainstack.com/the-agentic-payments-landscape/ |
| AAIF founding platinum members, 97 additional | linuxfoundation.org/press/agentic-ai-foundation, aaif.io |
| CoSAI/OASIS MCP Security whitepaper, Meta joined February 2026 | oasis-open.org/2026/02/03 |
| W3C WebPayments working minutes January-February 2026 | w3.org/2026/01/15-wpwg-minutes |
| IETF draft-messous-eat-ai, no behavioral trust coverage | datatracker.ietf.org/doc/draft-messous-eat-ai/ |
| IETF acknowledges behavioral attestation needed, future work | datatracker.ietf.org/doc/draft-klrc-aiagent-auth/ |
| ERC-8004 live mainnet January 29, 2026, 24K+ registrations | eips.ethereum.org/EIPS/eip-8004 |
| Trulioo KYA, joined AP2, Worldpay partnership | trulioo.com/resources/white-papers/know-your-agent, trulioo.com/company/newsroom |
| Sumsub AI Agent Verification launched January 29, 2026 | sumsub.com/newsroom January 2026, pymnts.com 2026 |
| a16z "bottleneck shifting from intelligence to identity" | a16z.com/newsletter/big-ideas-2026-part-3/ |
| WEF $236B projection, KYA call | weforum.org/stories/2026/01/ai-agents-trust/ |
| HUMAN AgenticTrust, per-site behavioral scoring | humansecurity.com/applications/agentic-ai/ |
| DataDome BATMS Forrester, 19 vendors Q4 2025 | forrester.com/report/the-bot-and-agent-trust-management-software-landscape-q4-2025 |
| ClawTrust, four-factor 0-100 score, early stage | clawtrust.io/ |
| Mnemom AIP, Team Trust Ratings, ERC-8004 anchoring | mnemom.ai, docs.mnemom.ai |
| Signet composite score, five dimensions, free | agentsignet.com/ |
| ZARQ/Nerq, technical metrics scoring, 143K agents Q1 2026 | dev.to/zarq-ai/state-of-ai-assets-q1-2026 |
| Oscilar behavioral trust score per agent for financial institutions | oscilar.com/blog/agentic-commerce |
| Merchant sees only "final payment signal" stripped of context | merchantadvisorygroup.org/news February 2026 |
| KYA six-layer control stack including behavioral monitoring | stablecoininsider.org/know-your-agent-kya-in-2026/ |
