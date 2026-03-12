# Expedition Synthesis: Protocol Architecture
## Date: 2026-03-11
## Vetted by: Orchestrator
## Alignment: Checked against Research Brief
## Research: 5 teams (Opus) + 9 validators (Opus)

---

## High Confidence (teams converged, validators confirmed)

### 1. MCP Is the Right Integration Surface for V1
**What:** Build Substrate as an MCP (Model Context Protocol) server. Agents connect to Substrate the same way they connect to any other tool — through a universal plug.

**Evidence:** MCP Go SDK v1.4.0, 4.1k stars, maintained by Google under Anthropic's org. Native support in Claude, ChatGPT, VS Code, Cursor. Official adapters for LangChain (3.4k stars) and Semantic Kernel. One implementation serves the majority of production agents.

**Validator corrections:**
- CrewAI does NOT have native MCP support (LangChain adapter works as fallback)
- MCP Go SDK is maintained by Google, not "Anthropic + Google" as co-maintainers
- OAuth 2.1 for HTTP transport is substantially more complex than "maps to HMAC" — V1 avoids this via stdio transport, but V2 requires real OAuth infrastructure
- TypeScript SDK v1.27.1 was released Feb 2025, not 2026
- A2A repo is at a2aproject/A2A, not google/A2A
- ACP merged with A2A under Linux Foundation — protocol landscape is MCP + A2A, not just MCP

**Confidence: HIGH.** Core recommendation verified. Precision details corrected.

### 2. The Behavioral Trust Gap Is Real — With Sharper Boundaries
**What:** No company offers portable, OS-level, deterministic behavioral trust scoring for AI agents. This is the gap Substrate fills.

**Evidence confirmed by validators:**
- Google UCP "does not solve which agents should be trusted" — confirmed
- Mastercard Verifiable Intent excludes behavioral trust — confirmed
- Stripe's Five Levels trust cliff at Level 3→4 — confirmed (though "trust cliff" is Team 3's editorial label, not Stripe's phrase)
- IETF drafts acknowledge behavioral attestation gap — confirmed, plus a 6th draft found (draft-jiang-seat-dynamic-attestation) that still doesn't fill it
- AAIF has no behavioral trust working group — confirmed
- WEF $236B projection — confirmed (source is Precedence Research via WEF, not WEF original)

**Validator corrections — the gap needs PRECISE framing:**
- **Mnemom** is closer competition than originally assessed. Agent-layer behavioral trust with cryptographic attestation, drift detection, hash-chain-anchored scores. NOT just a web-layer BATMS vendor. Distinction: Mnemom wraps agent clients; Substrate observes OS-level processes.
- **Vouched/KnowThat.ai** ($17M, Feb 2026): Community reputation directory for agents. Same marketing vocabulary, different architecture.
- **t54 Labs** ($5M, Feb 2026): Crypto-rails behavioral risk engine.
- **Gen Agent Trust Hub**: Pre-install safety scanning from Gen Digital (Norton parent).
- **HUMAN Security** now marketing "portable identity" via HTTP Message Signatures — still per-application for scoring, but identity becoming portable. One product decision from narrowing gap.
- **ERC-8004** is a Draft proposal, not live mainnet. "24K agents registered" has no traceable source.
- **ZARQ census URL** returned 404 — unverifiable.

**The precise gap statement:** No company combines all four of: (1) OS-level observation, (2) deterministic scoring, (3) on-device computation, (4) portable W3C VC attestation. Individual pieces exist in isolation. The combination is unoccupied.

**Sleeping giant: Gen Digital (Norton parent, ~500M device install base)** — does pre-install scanning today. One product pivot from OS-level behavioral monitoring at massive scale. Watch closely.

**Confidence: HIGH for the architectural gap. MODERATE for market framing** — competitors occupy adjacent vocabulary even if the architecture differs.

### 3. RATS RFC 9334 Names the Architecture
**What:** The IETF already has a standard vocabulary for exactly what Substrate is building. RFC 9334 (Remote ATtestation procedureS Architecture) defines: Attester (on-device daemon), Verifier (attestation server), Relying Party (brands/platforms). The "Passport Model" = agent carries credential, presents anywhere.

**Validator verified:** RFC 9334 exists (January 2023, Informational RFC) and maps precisely to Substrate's three-component architecture.

**Nuance:** RFC 9334 is Informational (defines vocabulary/concepts), not a protocol standard (defines wire format). It provides the language and the architecture model, not a drop-in implementation.

**The RATS working group may be a better first standards venue than AAIF.** This was underexplored by all teams.

**Confidence: HIGH.**

### 4. W3C VC 2.0 + SD-JWT Is Correct — And Better Go Libraries Exist
**What:** Trust attestations use W3C Verifiable Credentials 2.0 format with SD-JWT (RFC 9901) selective disclosure. Agents carry portable, cryptographically verifiable credentials.

**Validator corrections on Go libraries:**
- **trustbloc/vc-go v1.3.6** (January 2026, Apache-2.0) — MISSED BY ALL TEAMS. Covers full SD-JWT lifecycle (issuer/holder/verifier) AND W3C VC 2.0 data model. This is the production Go VC stack.
- **pascaldekloe/did v1.1.0** (CC0 license) — Also missed. Implements DID parsing with did:web support. "No v1.0 Go DID library" is wrong.
- **go-sd-jwt v1.4.0** references the draft URL, not RFC 9901 — needs verification that the serialization format matches the final RFC before production use.
- RFC 9901 is a Proposed Standard, not a full Internet Standard as Team 5 claimed.

**Confidence: HIGH** for format choice. **Go library landscape is better than reported.**

### 5. did:web Is Right for Agent Identity
**What:** Agents use did:web (DNS-anchored, no blockchain) for public identity, did:key for ephemeral/anonymous identity.

**No validator challenged this.** The security tradeoffs (DNS dependency, no tamper-evident history) were noted by researchers and acknowledged. did:webvh is the upgrade path when it matures.

**Confidence: HIGH.**

### 6. "Always Aware, Never Acting" Is Validated by DMARC Precedent
**What:** DMARC email authentication works exactly this way — it publishes policy, senders and receivers act on it. DMARC doesn't block email. The "never acting" principle has a proven production precedent at internet scale.

**Confidence: HIGH.**

---

## Corrections (validators caught errors)

### Architecture Model Corrections
1. **CT gossip is dead.** Team 1 cited Certificate Transparency's gossip protocol for trust score propagation. Validator found: the IETF draft (draft-ietf-trans-gossip-05) was filed as "Expired (IESG: Dead)" in 2018-2020. CT v2 (RFC 9162) left gossip out of scope. **Sigstore's Rekor is the real production reference** for distributed verification.

2. **Tailscale analogy is oversimplified.** The conceptual split (on-device computation vs. off-device coordination) is sound. But Team 1 described the control plane as "essentially a signing key" — Tailscale's coordination server also manages security policies, integrates with identity providers, operates relay servers, and provides audit logging. The analogy holds as a concept; it should not justify minimal infrastructure claims.

3. **"Minimum viable infrastructure" is undersold.** "Signing key + HTTPS endpoint + daemon" names the correct logical primitives but glosses over: HSMs for production signing (OWASP requirement), revocation endpoints, credential tracking database, rate limiting, monitoring, key rotation. Sigstore (comparable signing infrastructure) requires three components, 24/7 on-call, and a 99.5% SLO.

### Adoption Model Corrections
4. **"Rough consensus and running code" is from Dave Clark's 1992 IETF speech** (cited in RFC 2031 and RFC 7282), NOT RFC 8170. Two separate IETF concepts conflated under one citation. The philosophy is real; the source attribution is wrong.

5. **Git's "solo founder" phase was ~2 weeks.** Torvalds had 50 contributors and handed maintenance to Junio Hamano within three months, before Git 1.0. Not a meaningful precedent for solo protocol development.

6. **No documented case of a solo NON-TECHNICAL founder creating a successful internet protocol standard.** The Git/BitTorrent examples are both deeply technical founders with decades of systems experience. Survivorship bias was not examined.

### Data Quality Corrections
7. **97M monthly MCP SDK downloads** — carried from prior research, not re-verified in this expedition.
8. **ERC-8004 "24K agents in two weeks"** — no traceable source. ERC-8004 is a Draft, not live mainnet.
9. **ZARQ census URL** — returned 404. Unverifiable.

---

## New Risks (validators surfaced)

### 1. Android OS Sandboxing Blocks Process Awareness
The "any device can run a node" vision has an unexamined mobile constraint. Android's sandboxing model prevents one app from observing another's processes. Substrate's process awareness — the core value proposition — cannot work on stock Android without system-level access. This limits the "inner ring first" strategy to desktop/laptop initially.

### 2. On-Device Daemon Integrity Problem
What stops a malicious on-device daemon from lying about its trust score? If trust computation happens on-device, the device owner controls the computation. Neither Team 1 nor Team 5 resolved this. This is the central integrity assumption of the entire attestation architecture.

### 3. EU AI Act — Indirect Liability Path
EU AI Act August 2026 compliance deadline is 5 months away. Deterministic Beta formula likely keeps Substrate outside scope. BUT: if enterprise customers use Substrate scores to make decisions affecting human employees (hiring, access, performance), indirect liability may apply. Needs legal review before enterprise sales.

### 4. NIST AI Agent Standards Initiative (February 2026)
Missed by all 5 teams. If NIST defines a behavioral trust standard, Substrate needs to align or explain why not. Monitor actively.

### 5. Protocol Fragmentation
ACP merged with A2A under Linux Foundation in August 2025. The integration surface is MCP + A2A, not MCP alone. "MCP alone reaches most agents" may become less true as A2A grows.

### 6. Technical Co-Author Recruitment Is Harder Than Implied
Domain authority people with IETF/W3C credibility don't casually attach their name to unproven solo-founder projects. The plan to "recruit a technical co-author" has no mechanics — it's a hope, not a plan. The Anthropic relationship may be the only realistic path to a co-signer.

---

## The #1 Blocking Decision: Incident Taxonomy

Every team treated this as resolved background. No team investigated it. Every validator flagged the gap.

**What it is:** "What counts as an incident?" is the single most important design decision for the entire trust system. The Beta formula (trust = queries / queries + incidents) is meaningless without a definition of what an incident IS.

**Why it blocks everything:** Without incident taxonomy, there is no trust scoring. Without trust scoring, there are no attestations. Without attestations, there is no protocol. The incident taxonomy is the keystone that unlocks the entire architecture.

**What the validators said:**
- Validator 1: "The incident taxonomy is a dependency for everything downstream"
- Validator 3: "The incident taxonomy is not just a product design problem — it's a protocol credibility blocker"
- Validator 5: "Without a defined incident taxonomy, the protocol cannot be implemented by third parties"

**This requires Guiding Light's product input.** It is iterative (will evolve), but the V1 definition must exist before trust scoring has meaning.

---

## Synthesized Recommendation

### What to Build (Product First, Protocol Later)

**Phase 1 — Local MCP Server (Python, builds on existing prototype)**
Wrap existing FastAPI routes as MCP Tools. Expose: agent registration, trust queries, process awareness, ambient stream (as MCP Resource). This validates the integration surface before committing to Go.

**Phase 2 — Trust Layer Wiring**
Wire record_query(), define V1 incident taxonomy, compute_trust(), issue BehavioralAttestation VCs. Use trustbloc/vc-go when moving to Go. This is where the product becomes real.

**Phase 3 — Go Production Server**
Rewrite MCP server in Go using Go SDK v1.4.0. Split-plane architecture: thin attestation server (signs VCs) + on-device daemon (observes, computes). Use trustbloc/vc-go for VC stack, pascaldekloe/did for DID parsing.

**Phase 4 — Protocol Publication**
RATS RFC 9334 provides the vocabulary. Publish a BehavioralAttestation specification. Target IETF RATS working group first (more accessible than AAIF for a solo founder). "Rough consensus and running code" — the running code must exist first.

### What NOT to Build Yet
- A2A bridge (A2A is v0.3.0, pre-1.0 — premature)
- TRQP trust registry interface (V2 scope)
- OID4VP presentation exchange (V2 scope)
- BBS+ selective disclosure (wait for Go library maturity)
- Mobile version (Android sandboxing blocks core functionality)

---

## Disagreements

### Thin Notary vs. Live Registry
Team 1 recommended a "thin notary" (signs and forgets). Team 5 recommended a "live TRQP registry" (queryable trust database). These are architecturally incompatible. The synthesized recommendation: start with a live registry (brands need to query scores in real-time) and add offline-verifiable VCs (the passport model) as a complementary channel. Both, not either/or.

### AAIF vs. IETF RATS as Standards Venue
Team 4 recommended AAIF. Validators challenged: AAIF is corporate-weighted, individual access is unclear, and there's no behavioral trust working group. IETF RATS working group already has the vocabulary (RFC 9334) and accepts individual contributors. **IETF RATS first, AAIF second** is the more realistic path.

---

## Filtered Out

1. **Blockchain-anchored approaches** (ERC-8004, Mnemom on-chain): Filtered per destructive boundary — no blockchain dependency.
2. **LLM-based trust analysis** (Mnemom AIP): Filtered per constraint — deterministic scoring only.
3. **CT gossip protocol reference**: Filtered — the protocol was never standardized (Dead at IETF).
4. **Team 3's transaction chain diagram**: Subtly frames Substrate as an active gatekeeper. Filtered for alignment with "always aware, never acting."

---

## Watch List

| Entity | Why | Risk Level |
|--------|-----|------------|
| Gen Digital (Norton) | ~500M device install base, pre-install scanning today | HIGH — one pivot from OS-level behavioral trust |
| HUMAN Security | Adding portable agent identity, per-app behavioral scoring | MEDIUM — one product decision from narrowing gap |
| Mnemom | Agent-layer behavioral trust with crypto attestation | MEDIUM — closest architecture, different layer |
| Vouched/KnowThat.ai | $17M Feb 2026, same marketing vocabulary | LOW — different architecture, same narrative |
| NIST AI Agent Standards | February 2026 initiative, could define behavioral trust | MEDIUM — regulatory influence |
| Anthropic AAIF role | Could include or exclude behavioral trust | HIGH — primary relationship and potential co-signer |

---

## Confidence Summary

| Finding | Confidence | Basis |
|---------|------------|-------|
| MCP as V1 integration surface | HIGH | 4 teams + 2 validators, corrections are precision not direction |
| Behavioral trust gap (architectural) | HIGH | All teams + all validators confirm no one combines all 4 differentiators |
| Behavioral trust gap (market narrative) | MODERATE | Adjacent competitors occupy same vocabulary, need precise framing |
| W3C VC 2.0 + SD-JWT format | HIGH | Standards finalized, better Go libraries found than initially reported |
| RATS RFC 9334 architecture mapping | HIGH | Directly verified by validator |
| Solo non-technical founder can ship a protocol | LOW | No documented precedent. Technical co-author is a requirement, not optional |
| AAIF as standards venue | MODERATE | Accessible for members, unclear for individuals |
| IETF RATS as standards venue | MODERATE-HIGH | Already has vocabulary, accepts individuals, but needs running code first |
| Android mobile viability | LOW | OS sandboxing is a hard constraint |
| Incident taxonomy as #1 blocker | HIGH | Flagged by every validator, untouched by every researcher |
