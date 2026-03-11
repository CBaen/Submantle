# Followup Research: Mastercard/Google Trust Layer
**Expedition:** Trust Layer Deep Dive
**Date:** 2026-03-11
**Researcher:** Field Research Team (Followup-1)
**Assignment:** Investigate the Mastercard/Google "trust layer" flagged by Team 4 as highest-priority unresolved question

---

## Executive Summary

The Mastercard/Google "trust layer" is a real, named product: **Verifiable Intent**, announced March 5, 2026. It is co-developed by Mastercard and Google, open-sourced, and backed by eight industry partners.

**The critical finding for Substrate:** Verifiable Intent is purely transactional authorization infrastructure. It does not provide behavioral trust scoring, agent reputation, or longitudinal monitoring. The specification explicitly excludes these. Three independent validators were correct: this is not Substrate's space. It is the plumbing beneath where Substrate would operate.

---

## What Verifiable Intent Is

Verifiable Intent is a cryptographic framework that creates a tamper-resistant record linking three elements into a single, privacy-preserving token:

1. **Consumer identity** — who authorized the agent
2. **Consumer instructions** — what the agent was authorized to do (with explicit constraints: amount bounds, merchant allowlists, budget caps, recurrence terms)
3. **Transaction outcome** — what the agent actually did

It uses SD-JWT (Selective Disclosure JSON Web Token) architecture — a delegation chain binding the credential issuer, the user, and the agent through cryptographic key confirmation claims. Only the minimum necessary information is shared with each party (Selective Disclosure).

The specification is built on established standards from FIDO Alliance, EMVCo, IETF, and W3C. It is available at verifiableintent.dev and on GitHub.

**What this solves:** When an AI agent executes a purchase hours or days after receiving instructions, proving the consumer actually authorized that specific action becomes legally and technically difficult. Verifiable Intent provides cryptographic proof of that authorization — creating an audit trail for dispute resolution.

---

## Seven Questions Answered

### 1. What exactly IS it? What does it do?

Verifiable Intent is a cryptographic authorization trail for AI agent transactions. It proves, after the fact, that a specific transaction was within the scope of what a user actually authorized. Think of it as a cryptographically signed receipt that travels with every AI agent transaction, linking the original human instruction to the final purchase.

It operates in two modes:
- **Immediate mode**: User confirms in real-time
- **Autonomous mode**: Agent acts within pre-set constraints, with the agent's public key bound to the credential

**Source:** verifiableintent.dev specification, Mastercard announcement (March 5, 2026)

---

### 2. Does it provide behavioral trust scoring for AI agents?

**No. Explicitly and completely.**

From the specification: the scope is cryptographic constraints and delegation chains. There is no reputation scoring, no behavioral profiling, no dynamic trust adjustment mechanism.

The spec does note that payment networks will "maintain cumulative state" for enforcing budget caps across multiple transactions — but this is accounting state (has this agent spent more than $X this month?), not behavioral trust (has this agent been making good decisions?).

Verifiable Intent answers: "Was this authorized?"
It does not answer: "Should this agent be trusted?"

**Source:** verifiableintent.dev/spec/ (explicit scope boundaries section)

---

### 3. Is it portable across ecosystems or locked to Google/Mastercard?

**Designed to be portable, but practically weighted toward the Google/Mastercard stack.**

The specification is explicitly "protocol agnostic — capable of working across agentic protocols, devices, wallets, platforms, and other payment networks." The spec references alignment with:
- Google's Agent Payments Protocol (AP2)
- Google's Universal Commerce Protocol (UCP)
- OpenAI's Agentic Commerce Protocol (ACP)
- Google's Agent2Agent Protocol (A2A)

The open-source release (GitHub + verifiableintent.dev) invites broad contribution. However, real-world deployment in "the coming months" is via integration with **Mastercard Agent Pay's intent APIs specifically** — which means early adoption is Mastercard-network-first.

Portability is the stated goal. Lock-in is the practical near-term reality.

**Source:** ppc.land summary; verifiableintent.dev homepage; PYMNTS coverage

---

### 4. Does it compete with Substrate's vision of universal behavioral trust?

**No. It occupies a different layer entirely.**

Verifiable Intent answers: "Did this agent do what it was authorized to do in this transaction?"

Substrate's thesis answers: "What is the behavioral profile of this agent across all its actions, over time, across all contexts?"

These are complementary layers, not competing solutions. Verifiable Intent is the transactional authorization layer. Substrate (as behavioral trust infrastructure) would sit above it — reading the patterns that Verifiable Intent's audit trail creates, but synthesizing them into reputation, reliability scores, and behavioral signatures.

A useful framing: Verifiable Intent is the receipt printer. Substrate is the analyst who reads ten thousand receipts and builds a trust model of each agent.

**Source:** Multiple sources confirm VI's scope is per-transaction only; no source shows any behavioral scoring component.

---

### 5. What companies/partners are involved?

**Core developers:** Mastercard, Google

**Eight endorsing partners:**
- IBM
- Worldpay
- Fiserv (already integrating into merchant platform)
- Getnet
- Checkout.com
- Basis Theory
- Adyen

**Infrastructure layer:** Cloudflare (provides Web Bot Auth — HTTP Message Signatures — as the underlying agent authentication layer that Agent Pay and Visa's Trusted Agent Protocol both use)

**Adjacent protocols:** OpenAI (Agentic Commerce Protocol), Google A2A, Google AP2, Google UCP — Verifiable Intent is designed to work with all of these.

**Source:** Mastercard press release; Cloudflare blog post; PYMNTS coverage

---

### 6. What is its current status?

**Specification phase as of March 5, 2026. Not yet live in production.**

Specific status:
- Open-source specification published at verifiableintent.dev and GitHub
- Reference implementation available
- API specifications and developer tools for Mastercard Agent Pay integration: "expected to follow"
- Full integration into Mastercard Agent Pay's intent APIs: "in the coming months" (post March 5, 2026)
- Live pilot: Australia demonstrated "first authenticated agentic transactions using Agent Pay" — but this appears to be Agent Pay (the parent product), not Verifiable Intent specifically

Mastercard's broader Agent Suite (which Verifiable Intent will plug into) is scheduled for availability in Q2 2026.

**Source:** PYMNTS; aiagentsdirectory.com; Mastercard Australia press release

---

### 7. Does it have any behavioral/reputation component?

**No behavioral or reputation component exists. None is planned in the specification.**

The specification explicitly defers the following to future versions or external systems:
- Credential revocation (deferred to future version)
- Agent attestation schemes (optional extensions only)
- Behavioral monitoring
- Reputation systems
- Dynamic trust models

The only ongoing state tracking is budget enforcement — counting dollars spent against a cap. This is accounting, not behavioral trust.

**Source:** verifiableintent.dev/spec/ explicit scope boundaries

---

## The Competitive Landscape: Who IS Doing Behavioral Trust?

Given the gap Verifiable Intent leaves, I searched for other players in the behavioral trust space. Three emerged:

### ClawTrust (clawtrust.io)
A reputation system purpose-built for agent-to-agent interactions. Uses behavioral scoring: transaction success rates (40%), reliability/uptime (25%), community vouches from other agents (20%), safety incident record (15%). Scores 0–100. Sub-100ms trust checks. This is the closest existing analog to Substrate's behavioral trust layer — but it is commerce-transaction-only, agent-to-agent only, and has no ambient awareness component. No cryptographic verification. No cross-device or cross-context awareness.

### Nerq (dev.to/zarq-ai)
Scores 143,642+ AI assets across six registries (GitHub, npm, PyPI, HuggingFace, Docker Hub, MCP). Pure technical metrics: security vulnerabilities, maintenance cadence, popularity, documentation quality, ecosystem integrations. No behavioral scoring. No runtime awareness. It is a code quality scoring system, not a behavioral trust system.

### A2Apex (a2apex.io)
Compliance certification for Google's A2A Protocol. Tests protocol compliance, not behavior. Assigns Gold/Silver/Bronze badges. No runtime behavioral analysis.

**None of these provide what Substrate proposes:** ambient, cross-context, cross-device behavioral awareness that accumulates into persistent trust profiles for agents operating in the real world.

---

## Strategic Implications for Substrate

### The space is real and unoccupied

Every source confirmed the same gap: the existing trust infrastructure (Verifiable Intent, Agent Pay, Visa Trusted Agent Protocol, Cloudflare Web Bot Auth) handles authentication and authorization at the transaction level. None of it tracks whether an agent's decision-making is trustworthy over time.

The WEF published "Trust is the new currency in the AI agent economy" (July 2025). The question is widely recognized. The answer does not yet exist at the behavioral layer.

### Verifiable Intent is infrastructure Substrate could read

Verifiable Intent will create a growing corpus of cryptographically verified agent action records. This is raw material — behavioral signals that Substrate's pattern-matching layer could synthesize into trust profiles. Rather than competing, Substrate could explicitly position itself as the behavioral intelligence layer built on top of Verifiable Intent's transactional audit trail.

### The Mastercard stack does not close the behavioral trust gap

Mastercard's full stack as of March 2026:
- **Agent Suite** (Q2 2026): Build/deploy/advise on agent deployments
- **Agent Pay**: Authentication and payment token infrastructure
- **Verifiable Intent**: Cryptographic authorization records
- **Cloudflare Web Bot Auth**: Agent identity signing at network layer

None of these layers, individually or combined, provide behavioral trust scoring. Mastercard explicitly said they will "continue working with industry bodies to define complementary standards for conversational AI in commerce" — signaling they know gaps remain.

### Timing is favorable for Substrate

Verifiable Intent was just announced (March 5, 2026). It is not yet integrated into Agent Pay. The behavioral trust layer does not exist. The industry is now building the authorization plumbing that will generate the data a behavioral trust layer needs. Substrate's timing — building the behavioral layer while the transactional layer is being established — is architecturally correct.

---

## What Team 4's Validators Got Right

All three validators who flagged this as the highest-priority unknown were correct to be concerned, but for the right reason in the wrong direction. The concern was: "does this close the behavioral trust gap and threaten Substrate's thesis?"

The answer is no — and the evidence is clear and explicit in the specification itself. What the validators correctly sensed was the significance of this development: a major industry coalition building trust infrastructure for agentic commerce is a strong signal that the market is real and moving fast. But they are building the floor, not Substrate's layer.

The correct updated framing: Mastercard/Google are building the authorization layer. **This is a tailwind, not a headwind.** The more transactions flow through Verifiable Intent, the more behavioral data becomes available for a layer like Substrate to analyze.

---

## Evidence Quality Assessment

| Claim | Sources | Confidence |
|-------|---------|------------|
| Verifiable Intent announced March 5, 2026 | Mastercard, PYMNTS, Fintech Singapore, multiple | High |
| Co-developed with Google | All sources consistent | High |
| Authorization only, no behavioral scoring | Spec explicit; multiple sources confirm | High |
| Open source at verifiableintent.dev/GitHub | Mastercard, multiple | High |
| 8 endorsing partners | Multiple sources consistent | High |
| Spec phase, not yet live in production | Multiple sources consistent | High |
| Q2 2026 Agent Suite availability | digitalcommerce360, PYMNTS | High |
| No existing behavioral trust equivalent | Survey of landscape, 3 alternatives examined | Medium-High |
| ClawTrust as closest behavioral analog | clawtrust.io direct | Medium (single source, novel company) |

---

## Sources

- Mastercard Verifiable Intent announcement: https://www.mastercard.com/us/en/news-and-trends/stories/2026/verifiable-intent.html
- Verifiable Intent specification: https://verifiableintent.dev / https://verifiableintent.dev/spec/
- ppc.land summary article: https://ppc.land/mastercard-and-googles-new-trust-layer-could-reshape-how-ai-buys-for-you/
- PYMNTS coverage: https://www.pymnts.com/mastercard/2026/mastercard-unveils-open-standard-to-verify-ai-agent-transactions/
- The Paypers: https://thepaypers.com/payments/news/mastercard-introduces-verifiable-intent-co-developed-with-google
- AgenticPlug.ai explainer: https://agenticplug.ai/blog/mastercard-verifiable-intent-for-agentic-commerce
- AI Agents Directory: https://aiagentsdirectory.com/blog/mastercard-introduces-verifiable-intent-standard-for-ai-agent-transactions
- Mastercard Agent Suite press release: https://www.mastercard.com/global/en/news-and-trends/press/2026/january/mastercard-launches-agent-suite-to-ready-enterprises-for-a-new-e.html
- Cloudflare secure agentic commerce: https://blog.cloudflare.com/secure-agentic-commerce/
- DEV Community Agent Action Receipt: https://dev.to/andrew_glaz_12f84661fd541/mastercard-just-validated-the-standard-we-built-verifiable-agent-actions-with-aar-5b1g
- Nerq trust scoring Q1 2026: https://dev.to/zarq-ai/state-of-ai-assets-q1-2026-143k-agents-17k-mcp-servers-all-trust-scored-2dc2
- ClawTrust: https://clawtrust.io/
- A2Apex: https://a2apex.io/
- WEF trust article: https://www.weforum.org/stories/2025/07/ai-agent-economy-trust/
- FinTech Magazine: https://fintechmagazine.com/news/mastercard-and-google-how-is-agentic-commerce-advancing
