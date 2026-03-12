# Team 5 — Decentralized Identity & Trust Infrastructure
## Expedition: Protocol Architecture
## Date: 2026-03-11
## Researcher: Team 5 Sub-Agent

---

## Executive Summary

The decentralized identity ecosystem has reached a genuine inflection point in 2025-2026. W3C VC 2.0 is finalized, OpenID4VP is final, SD-JWT is RFC 9901, and the EU is legally mandating implementation by December 2026. The technology is no longer theoretical. However, the Go library landscape is fragmented and pre-v1.0 for most DID tooling, and BBS+ selective disclosure remains unfinished. For Submantle specifically: did:web is the right DID method for AI agent identity (no blockchain, DNS-anchored, verifiable), the Submantle deployment can itself function as a specialized trust registry (distinct from TRQP-style governance registries), and the behavioral trust layer Submantle is building has no standards-track competition anywhere in the ecosystem.

---

## Part 1: DID Methods — Production Readiness Assessment

### Battle-Tested: did:key

**What:** A DID method where the entire DID document is derived cryptographically from a single public key. No external resolution required — the identifier IS the key.

**Evidence:** W3C CCG Draft v0.9. Used in virtually every SSI demo environment, academic paper, and test suite. It is the "localhost" of DID methods.

**Fits Submantle because:** Perfect for ephemeral agent identities — an agent that hasn't registered with Submantle can still have a cryptographically verifiable identity with zero infrastructure. Zero-dependency agent bootstrapping.

**Tradeoffs/Risks:**
- No update capability — key rotation requires a new DID entirely
- No revocation by design
- Not proposed for the W3C DID Methods WG's formal standardization track (the WG wants one ephemeral method; did:key is a leading candidate but not yet confirmed)
- Source: https://w3c-ccg.github.io/did-key-spec/

**Go library support:** `github.com/tbd54566975/web5-go` (v0.24.0, Apache-2.0, August 2024 — pre-v1.0), `github.com/nuts-foundation/go-did` (v0.18.0, GPL-3.0, February 2026 — pre-v1.0). No production-stable (v1.0+) Go implementation. Multiple pre-v1.0 libraries exist with varying maturity.

---

### Battle-Tested (in web context): did:web

**What:** DID documents hosted at well-known HTTPS paths on existing web infrastructure. A DID like `did:web:submantle.example.com:agents:claude-001` resolves by fetching `https://submantle.example.com/agents/claude-001/did.json`.

**Evidence:** Used in production by enterprises, governments, and AI agent frameworks. The Cisco New Identity Framework for AI Agents (2025) recommends did:web as the foundational identity method for agents. The W3C DID Methods WG is drafting a standard for one web-based DID method — did:web is the primary candidate alongside did:webvh.

**Adoption signal:** did:web has the broadest real-world adoption of any DID method that does not require a blockchain, because it reuses DNS + HTTPS infrastructure that already exists.

**Source:** https://w3c-ccg.github.io/did-method-web/ ; Cisco Community identity framework post (2025)

**Fits Submantle because:**
- No blockchain dependency — aligns exactly with Submantle's constraint
- On-device DID hosting is possible: Submantle daemon could serve `/.well-known/did.json` locally
- Agent developers can publish their agent's DID at their own domain
- Verifiers can resolve agent DIDs without Submantle infrastructure

**Tradeoffs/Risks (critical for Submantle):**
- **DNS dependency = centralization risk.** If the hosting domain is compromised, expired, or seized, the DID is unresolvable or spoofable. This is did:web's fundamental security flaw. A company's agent identity is only as strong as their DNS registration.
- **No tamper-evident history.** You cannot verify that a did:web document has not been secretly changed between resolutions. An attacker who controls DNS can silently rotate keys.
- **Hosting burden.** Someone must serve the HTTPS endpoint indefinitely.
- **Mitigation in progress:** did:webvh (formerly did:tdw — "Trust DID Web") is being developed specifically to address did:web's history problem by adding a verifiable log of DID document changes. It is in the W3C DID Methods WG charter as one of nine candidate methods. However, it is a draft, not a finalized spec, and has no production Go library.

**Go library support:** `github.com/tbd54566975/web5-go/dids/didweb` (v0.24.0, Apache-2.0, August 2024 — pre-v1.0). `github.com/decentralgabe/ssi-sdk/did/web` (active fork of TBD's ssi-sdk). Neither is v1.0.

---

### Hype, Not Production: did:ion

**What:** Microsoft's Identity Overlay Network. A Sidetree-protocol DID method running on top of Bitcoin blockchain. Batches DID operations into Bitcoin transactions.

**Current status:** The GitHub repository (`decentralized-identity/ion`) shows the last formal release was v1.0.4 in June 2022 — now 3.5 years old. 72 open issues, 7 open PRs. Active issues but slow release cadence. Microsoft has not made major public commitments to ION in 2025-2026. The primary development (Sidetree protocol) lives in a separate repository.

**Evidence:** No evidence of new enterprise deployments or significant ecosystem traction in 2025. Microsoft's own decentralized identity work has largely pivoted toward the Entra Verified ID product (which uses did:web for issuer identity and vc-jwt format).

**Source:** https://github.com/decentralized-identity/ion (last release June 2022)

**Not fit for Submantle because:**
- Requires Bitcoin blockchain — direct violation of Submantle's no-blockchain-dependency constraint
- No production Go library exists
- Adoption has stalled; Microsoft has not evangelized ION in 2025 the way they did in 2021-2022
- High operational complexity (Bitcoin node required)

---

### Niche, Not General-Purpose: did:ethr

**What:** DID method using Ethereum smart contracts. Identity anchored in the Ethereum blockchain.

**Current status:** Used in some DeFi and Web3 identity contexts. Not seeing significant adoption in enterprise or government contexts.

**Not fit for Submantle because:** Blockchain dependency, Ethereum gas costs, no Go library, incompatible with on-device-first architecture.

---

### Tactical/Offline Use: did:peer

**What:** DIDs exchanged directly between two parties without a verifiable data registry. Designed for pairwise relationships — you share your did:peer with a specific counterpart.

**Evidence:** Widely used in DIDComm-based messaging (Hyperledger Aries, Credo-ts). W3C DID Methods WG is considering standardizing it.

**Fits Submantle because:** Useful for private agent-to-agent interactions where neither party wants to publish their identity to a registry. An agent could use did:peer when querying Submantle privately, then use did:web for its public identity.

**Tradeoffs/Risks:** No global resolvability — did:peer DIDs only work between the parties that exchanged them. Not useful for public identity claims.

**Go library support:** Included in TBD's web5-go and nuts-foundation go-did, both pre-v1.0.

---

### Summary DID Method Table

| Method | Production Status | Blockchain Required | Go Library | Fits Submantle |
|--------|-------------------|---------------------|------------|----------------|
| did:key | Production in demos, draft spec | No | Pre-v1.0 multiple | Yes (ephemeral) |
| did:web | Production in enterprises/gov | No | Pre-v1.0 | Yes (primary) |
| did:webvh | Draft, fixing did:web flaws | No | None found | Yes (future) |
| did:peer | Production in DIDComm | No | Pre-v1.0 | Yes (pairwise) |
| did:ion | Stalled post-2022 | Bitcoin | None | No |
| did:ethr | Niche Web3 | Ethereum | None | No |

**W3C DID Methods WG is standardizing:** Nine candidate methods including did:key, did:web, did:webvh, did:webs, did:peer, did:plc, did:webplus, did:scid, and a cryptographic event log specification. Charter is in draft; no start date yet.

---

## Part 2: W3C VC 2.0 Ecosystem Maturity

### Status: Final Standard, Production Ecosystem Building

W3C Verifiable Credentials Data Model v2.0 achieved W3C Recommendation status on May 15, 2025. Seven related specifications were finalized simultaneously (see followup-2-bbs-plus-status.md for the complete list).

**What is finalized:**
- VC Data Model v2.0 (core format)
- Data Integrity ECDSA and EdDSA cryptosuites
- Securing VCs using JOSE and COSE (enables SD-JWT VC format)
- Bitstring Status List v1.0 (revocation)

**What is NOT finalized (still Candidate Recommendation):**
- BBS Cryptosuites v1.0 (selective disclosure with unlinkability)
- VC JSON Schema Specification

**Real-world deployment trajectory:** The EU Digital Identity Wallet mandate (legally required implementation by December 2026) is driving rapid adoption of W3C VC 2.0 across European member states. The California DMV mDL is deployed using OID4VP. Self-certification for OpenID4VC implementations launched February 2026.

**Source:** W3C press release May 15, 2025; OpenID Foundation self-certification announcement

**Go VC libraries:**
- `github.com/nuts-foundation/go-did` (v0.18.0, GPL-3.0, 33 importers, pre-v1.0) — supports VC parsing and JSON-LD + JWT proof formats
- `github.com/hyperledger/aries-framework-go` — comprehensive but heavyweight; includes sdjwt package
- Multiple pre-v1.0 implementations with varying maturity

**Assessment for Submantle:** W3C VC 2.0 is the correct format for Submantle Trust Attestations. The standard is final. The tooling ecosystem is production-ready for ECDSA/EdDSA-signed JWT VCs. This decision is confirmed and not controversial.

---

## Part 3: SD-JWT Ecosystem

### Status: RFC 9901 — Full Internet Standard, Production Go Library Exists

SD-JWT was published as RFC 9901 on November 19, 2025 — an Internet Standards Track RFC. This is the highest IETF standards designation. Co-authored by Fett (Authlete), Yasuda (SPRIND), and Campbell (Ping Identity) — strong institutional backing.

**How it works:** The issuer marks specific claims as selectively disclosable by replacing their values with hash digests. The holder presents only the claims needed, along with the pre-images (disclosures) for those claims. Verifiers check disclosed claims against the signed digests.

**Production deployment reality:** The EU Digital Identity Wallet, OID4VCI (Final September 2025), and OID4VP (Final July 2025) all explicitly support SD-JWT VC format. SD-JWT is the dominant selective disclosure mechanism in production as of early 2026. Not BBS+.

**Source:** https://datatracker.ietf.org/doc/rfc9901/ ; followup-2-bbs-plus-status.md (internally researched)

**Go library status:**
- `github.com/MichaelFraser99/go-sd-jwt` — v1.4.0, MIT, published August 30, 2025. **Reached major version v1 — considered stable.** Implements the SD-JWT specification. Note: documentation references the draft URL, but v1.4.0 on the stable semver track suggests it tracks the finalized RFC. Go 1.21+ required. This is the primary Go SD-JWT library.
- `github.com/hyperledger/aries-framework-go/component/models/sdjwt` — Also available, part of the heavyweight Aries framework.
- `github.com/extrimian/ssi-sdk/sd-jwt` — Additional option.

**Assessment for Submantle:** SD-JWT is the correct selective disclosure mechanism for V1 Trust Attestations. RFC 9901 is final. A stable v1.0 Go library exists. This is a confirmed decision, consistent with followup-2-bbs-plus-status.md. The note that go-sd-jwt's docs reference the draft URL is worth watching — verify in the library source that the RFC 9901 serialization format is implemented correctly before production use.

**Privacy caveat (already flagged):** SD-JWT does not provide unlinkability. Two presentations of the same credential can be correlated by verifiers. This is acceptable for V1 (agent trust tier verification by brand partners) but becomes a concern at scale. BBS+ remains the V2+ target for unlinkability when Go support matures.

---

## Part 4: Ceramic Network — Status Update

### Status: Pivoted Away From Decentralized Identity

**Critical finding:** In February 2025, 3Box Labs (Ceramic's creator) merged with Textile. In conjunction, Ceramic pivoted away from decentralized identity and composable data toward AI agent intelligence infrastructure — described as "an open intelligence network where AI agents can autonomously buy and sell intelligence from each other."

**ComposeDB is being deprecated.** The team is shipping `ceramic-one` as a standalone implementation. The identity/VC use case that made Ceramic relevant to this research has been de-emphasized.

**Source:** https://blog.ceramic.network/ceramic-is-joining-textile/ (February 2025)

**Assessment for Submantle:** Ceramic is no longer relevant to decentralized identity or VC infrastructure. Do not reference it in architecture planning. The pivot actually makes Ceramic conceptually adjacent to Submantle's territory (agent intelligence infrastructure), but their approach (marketplace for intelligence) is different from Submantle's (behavioral trust scoring). Not a dependency. Not a competitor. Not a reference implementation.

---

## Part 5: ION — Definitive Status

### Status: Maintenance Mode, Not Production Recommended

ION launched v1.0 in 2021. As of March 2026:
- Last formal release: v1.0.4 (June 2022)
- 72 open issues, slow PR activity
- Bitcoin blockchain dependency
- No production Go library
- Microsoft has not evangelized ION in 2025-2026; their decentralized identity product (Entra Verified ID) uses did:web for issuer identity

ION achieved what it set out to do — prove Sidetree on Bitcoin works — but has not grown into a mainstream DID infrastructure. The Sidetree protocol itself lives at a separate DIF repository and has broader applicability, but Bitcoin anchoring remains an operational burden.

**Assessment for Submantle:** Do not use or reference ION. It conflicts with the no-blockchain constraint, has no Go library, and is not gaining traction in the 2025-2026 ecosystem.

---

## Part 6: SSI in Production — What Actually Works

### The Honest Assessment

Real SSI production deployments as of 2026 are concentrated in three areas:

**1. Government Identity Wallets — Working in Production**
- EU Digital Identity Wallet (eIDAS 2.0) — production launches rolling out across member states throughout 2026
- British Columbia's Verified Organizations Network (VON) — one of the earliest production SSI deployments
- Thailand Digital Credentials framework — production deployment with Transformational
- California DMV mobile driver's license — using OID4VP, live

**2. Enterprise Accreditation — Working in Production**
- cheqd's ecosystem: 230K+ testnet DIDs created, ASI Alliance (Fetch.ai, SingularityNET, Ocean Protocol) using it for AI agent identity
- Verifiable professional credentials (educational, employment, compliance)
- cheqd's verified business identities (VERA: 50K in South Africa)

**3. Niche AI Agent Identity — Emerging**
- cheqd's MCP toolkit for VC issuance to AI agents (1 star on GitHub — early adopter phase, not mainstream)
- Academic implementations using Hyperledger Indy + JSON-LD VCs (Huang et al. 2025 paper)

**What doesn't work:**
- Universal interoperability across DID methods — "over 100 DID methods registered with different trust models, credentials issued in one SSI ecosystem often cannot be verified in another" (SSI market analysis 2025). This is the interoperability wall SSI still hasn't solved.
- User-controlled wallets at consumer scale — requiring users to manage DIDs is proving to be a significant UX barrier outside government mandate contexts
- Cross-ecosystem portability — an SSI credential from a Hyperledger Indy system cannot be verified by an OID4VP-based system without adaptation layers

**Source:** SSI market report 2025; SSI platforms analysis Medium post 2025; cheqd documentation

**Critical lesson for Submantle:** The deployments that succeed are the ones where someone OTHER than the end user manages the identity infrastructure (governments issuing wallets, enterprises issuing employee credentials, cheqd managing DID lifecycle for developers). Submantle's on-device model — where Submantle manages the agent's DID automatically — is the right pattern. Don't ask users or developers to understand DIDs.

---

## Part 7: Decentralized Trust Without Blockchain

### The Patterns That Work

The requirement is Web3 COMPATIBILITY but not Web3 DEPENDENCY. Three established patterns enable this:

**Pattern 1: did:web + HTTPS (DNS-Anchored Trust)**
Trust is rooted in DNS ownership and TLS certificate chains — the same infrastructure that secures the web. A verifier checks that a DID document was served over authenticated HTTPS from a domain. Trust transitive: if you trust the domain owner, you trust the key material they publish.

**Evidence:** This is how Entra Verified ID, most EU wallet issuer identity systems, and production enterprise VC deployments work. It is the dominant pattern for institutional identity.

**Tradeoff:** Inherits DNS's centralization and attack surface. Doesn't provide cryptographic proof that a DID document hasn't been silently changed.

**Pattern 2: Trust Lists / Trust Registries (Authority-Anchored Trust)**
A governance authority maintains a list of trusted entities. Verifiers consult the list. This is how X.509 PKI works (certificate authorities), how eIDAS works (national trust lists), and how TRAIN (Trust Management Infrastructure) works in the SSI context.

**The Trust Over IP Foundation's Trust Registry Query Protocol (TRQP v2.0)** is the relevant standard. As of December 2025, it completed Public Review 02 and is being finalized. TRQP defines a lightweight REST-like protocol for querying "Has Authority A authorized Entity B to take Action X on Resource Y?" It is described as "DNS for trust."

**Evidence:** TRQP is being implemented in production by cheqd (via TRAIN integration), the European trust list infrastructure, and EUDI Wallet governance frameworks.

**Source:** https://trustoverip.github.io/tswg-trust-registry-protocol/

**Pattern 3: Cryptographic Event Logs (Tamper-Evident Trust)**
This is what did:webvh adds to did:web — a microledger of DID document changes that can be independently verified without a blockchain. Each change is cryptographically linked to the previous state. A verifier can confirm that the current document is the authentic continuation of a known history.

**Evidence:** did:webvh (formerly did:tdw) is being standardized in the W3C DID Methods WG. The KERI (Key Event Receipt Infrastructure) project implements this pattern more fully for full key state management.

**Assessment for Submantle:** Submantle does not need to pick one pattern. The layered approach:
- did:web for public agent identity (Pattern 1) — simple, no infrastructure
- Submantle itself as a trust registry (Pattern 2) — Submantle maintains the authoritative record of which agents have been registered, their trust scores, and their behavioral attestations
- did:webvh for V2 when tamper-evident history matters (Pattern 3) — upgrade path

---

## Part 8: Trust Registries — Can Submantle Be One?

### What a Trust Registry Is

A TRQP-compliant trust registry answers governance questions: "Is Entity B authorized by Authority A to perform Action X?" It is fundamentally about **policy-based authorization** — an institution certifying that an entity meets certain criteria.

Example: "Has the California DMV authorized this credential as a valid mDL?"

### What Submantle Is (vs. a TRQP Registry)

Submantle answers a different kind of question: "What is Agent X's behavioral trust score based on observed behavior?" This is **evidence-based reputation**, not policy-based authorization.

These are different layers:
- Trust registry: "This agent was certified by Anthropic."
- Submantle: "This agent has a 0.87 trust score based on 10,000 queries with 3 incidents."

**However:** Submantle could implement a TRQP-compatible interface as a trust registry layer on top of its behavioral data. A TRQP query of "Has Submantle authorized Agent B to act at Tier 2 or above?" could be answered by Submantle's trust score computation. This would make Submantle a trust registry that answers behavioral questions through the TRQP interface.

**This is architecturally novel.** No existing trust registry answers behavioral questions — they all answer institutional authorization questions. Submantle could be the first behavioral trust registry, implementing TRQP as its API surface.

**Practical implications:**
- TRQP is a REST API pattern — straightforward to implement on top of Submantle's existing API
- TRQP v2.0 is finalizing in 2026 — good timing to align
- This would make Submantle interoperable with any TRQP-aware verifier without requiring them to understand Submantle's internal model
- cheqd's TRAIN integration uses TRQP — meaning a Submantle TRQP endpoint would be immediately discoverable by cheqd-integrated systems

**Source:** https://trustoverip.github.io/tswg-trust-registry-protocol/ ; cheqd followup (followup-3-cheqd-implementation.md)

---

## Part 9: did:web Specifically — Deep Dive for Agent Identity

### The Security Tradeoffs in Full Detail

did:web is the right DID method for AI agent identity in Submantle's context. Here is the complete tradeoff analysis:

**Security properties:**
- Authenticity: HTTPS + TLS ensures you're talking to the claimed domain. A valid did:web document served over HTTPS is authentic at time of resolution.
- Non-repudiation: The key material in the DID document can be used to verify signatures.
- Availability: As reliable as the hosting domain's HTTPS uptime.

**Security weaknesses:**
- **No history integrity:** A domain owner can silently replace their DID document. There is no way for a verifier to detect that the document changed without independent auditing.
- **DNS hijacking vector:** If the domain's DNS is compromised (registration lapse, registrar attack, BGP hijack), an attacker can serve a malicious DID document pointing to their keys. This is the primary attack surface.
- **Domain expiry:** If a company's domain expires, their agents' DIDs become unresolvable or hijackable.
- **Centralization:** Submantle's agent identity infrastructure depends on domain registrars and DNS providers — exactly the centralized infrastructure SSI is meant to avoid.

**Mitigation:** For enterprise/institutional agents (Anthropic's Claude, OpenAI's GPT-4, etc.), did:web is fine — large companies maintain domain ownership reliably. For individual agents, did:key is safer (no external dependency) with did:web as an optional upgrade.

**How Submantle agents could use did:web:**
- Submantle daemon serves `/.well-known/did.json` locally at `localhost` or at an agent-specific path
- For agents registered with Submantle: `did:web:submantle.local:agents:{agent-id}` — resolvable only within the device
- For externally-visible agents: `did:web:{developer-domain}:agents:{agent-id}` — developer hosts it
- Submantle handles key generation and rotation automatically — developers never touch key material

---

## Part 10: Verifiable Presentation Exchange — The Standards Picture

### OpenID4VP: Final Standard, Production Deployment

OpenID for Verifiable Presentations (OID4VP) reached Final specification status on July 8-9, 2025. This is the primary presentation protocol for the EU Digital Identity Wallet and is being adopted globally.

**What it handles:** The verifier sends a request (using DCQL or DIF Presentation Exchange query format) describing which credentials it needs. The holder's wallet selects matching credentials and returns a VP. The verifier checks signatures.

**Self-certification launched February 2026** for OID4VP 1.0 through the OpenID Foundation's conformance testing platform. Implementations can now get certified.

**EU legal mandate:** Member states must implement OID4VP by December 2026.

**Source:** https://vidos.id/blog/openid4vp-reaches-final-status

### DIF Presentation Exchange vs. DCQL

OID4VP supports two query languages:
- **DIF Presentation Exchange (PE):** The original, complex query format. Still supported.
- **DCQL (Decentralized Credential Query Language):** Simpler, newer format. The latest HAIP draft makes DCQL the ONLY mandated language, phasing PE out for interoperability profile purposes.

**Implication for Submantle:** If Submantle implements any VP exchange mechanism, align with DCQL (the forward direction) rather than PE.

### DIDComm: A Different Use Case

DIDComm v2 is a messaging protocol for secure, private agent-to-agent communication. It is NOT the same as OID4VP — it handles the transport and encryption layer for VC exchange in peer-to-peer contexts (no central server, asynchronous, offline-capable).

DIDComm is used in Hyperledger Aries and cheqd's MCP toolkit. It's more suited for enterprise workflows (issuing credentials to employees, healthcare record sharing) than for the web-based trust verification Submantle needs.

**For Submantle V1:** OID4VP is the relevant protocol if Submantle needs to handle VP presentations. DIDComm is not needed for Submantle's current scope.

---

## Part 11: cheqd — Architecture Lessons for Submantle

From followup-3-cheqd-implementation.md, the key architecture decisions to absorb:

**What cheqd validated:**
1. **DID per agent is the right pattern.** Every agent gets its own DID. cheqd does this in production with 230K+ testnet DIDs.
2. **Bitstring Status List is the right revocation mechanism.** W3C standard, on-chain (or in Submantle's case, in SQLite). Issuer flips a bit; verifier checks one index. This is the pattern to implement.
3. **AnonCreds ZKPs, not BBS+, are cheqd's selective disclosure path.** This reinforces the BBS+ skip-for-V1 decision.
4. **TRAIN/TRQP for trust chain verification.** Recursive verification: credential → issuer accreditation → root DID → DNS anchor. Submantle could implement this verification chain.

**What Submantle adds that cheqd doesn't have:**
- Runtime behavioral observation
- Behavioral attestation (the "BehavioralAttestation" credential type doesn't exist yet)
- Trust scores based on observed behavior, not institutional accreditation

**VC schema Submantle needs (not in cheqd):**
A new credential type `BehavioralAttestation` with fields:
- `subject_did` — the agent being attested
- `observation_window_start` — when observation began
- `observation_window_end` — when last observation completed
- `total_queries` — from Beta formula numerator
- `total_incidents` — from Beta formula denominator
- `trust_score` — computed Beta value (optional — may be computed by verifier)
- `observation_hash` — hash of the behavioral event log (tamper-evidence)
- `trust_tier` — "anonymous" | "registered" | "trusted"

---

## Part 12: The Go Library Landscape — Honest Assessment

The Go DID/VC library landscape is fragmented and pre-production for most components. This is the realistic picture:

| Component | Library | Version | Status | Notes |
|-----------|---------|---------|--------|-------|
| SD-JWT | github.com/MichaelFraser99/go-sd-jwt | v1.4.0 | **Stable** | Only v1.0+ SD-JWT Go lib |
| JWT (baseline) | github.com/golang-jwt/jwt | v5 (stable) | **Stable** | Not SD-JWT specific |
| DID parsing | github.com/nuts-foundation/go-did | v0.18.0 | Pre-v1.0 | GPL-3.0, 33 importers |
| did:web | github.com/tbd54566975/web5-go/dids/didweb | v0.24.0 | Pre-v1.0 | Apache-2.0 |
| did:key | github.com/tbd54566975/web5-go/dids/didkey | v0.24.0 | Pre-v1.0 | Apache-2.0 |
| VC issuance | Multiple partial libs | — | Fragmented | No clear winner |
| BBS+ | No production Go lib | — | Gap | See followup-2 |
| DIDComm | No production Go lib found | — | Gap | Rust libs exist |

**Practical recommendation for Submantle's Go rewrite:**
- Use `go-sd-jwt` v1.4.0 for selective disclosure. It is the only stable-versioned SD-JWT Go library.
- Use `golang-jwt/jwt` for base JWT operations.
- For DID creation/parsing: `web5-go` is Apache-2.0 and has did:web + did:key. Acceptable for prototype; wait for v1.0 before production commitment. Alternatively, implement a thin did:web layer directly (the spec is simple enough that custom implementation is feasible).
- Do not depend on any v0.x library for security-critical key management operations in production.

---

## Gaps and Unknowns

**1. The Go DID/VC v1.0 gap is real.**
No production-stable (v1.0+) Go library exists for DID creation/resolution or VC issuance as of March 2026. Submantle's production Go rewrite will either need to wait for library maturity or implement thin custom layers. The thin custom implementation path is viable for did:web (the spec is a JSON document at a URL) and did:key (pure cryptography). The SD-JWT layer is solved (go-sd-jwt v1.4.0).

**2. did:webvh vs. did:web decision point.**
did:webvh solves did:web's history integrity problem, but has no production Go library and is not yet a finalized spec. The W3C DID Methods WG is working on this. The right decision is to use did:web now and plan for did:webvh upgrade when it finalizes (likely 2027 at W3C cadence).

**3. TRQP v2.0 implementation timeline.**
TRQP v2.0 is completing public review in early 2026. If Submantle wants to implement a TRQP-compatible behavioral trust registry interface, the spec will be final enough to build against in 2026. This is worth tracking — it would give Submantle a standards-compliant API surface.

**4. OID4VP + Submantle trust presentation.**
If agents want to present their Submantle trust attestation to brand partners using OID4VP, Submantle needs a VP endpoint. This is a V2 feature — agents need a wallet-like component to hold their `BehavioralAttestation` VCs and respond to OID4VP presentation requests. Not blocking for V1, but the architecture decision (where does the agent's VC wallet live?) should be made before the attestation layer is designed.

**5. did:web for locally-hosted agent identity.**
The spec allows `did:web:localhost` for development. For production on-device agents, the domain anchoring problem is real — Submantle agents on a device without an externally reachable domain cannot publish a did:web that external verifiers can resolve. This suggests a two-tier identity model:
- Local only: did:key (no external resolution needed)
- Externally verifiable: did:web at a Submantle-hosted or developer-hosted URL

Submantle could optionally host agent DIDs (e.g., `did:web:submantle.io:agents:{device-hash}:{agent-id}`) as a service, providing external resolvability without requiring developers to host their own HTTPS endpoints.

---

## Synthesis

### The Decentralized Identity Stack for Submantle

Based on all research, the following architecture is recommended for Submantle's decentralized identity integration:

**Layer 1 — Agent Identity (Immediate: V1)**
- Primary: did:key for all agents (no infrastructure, cryptographic, ephemeral)
- Optional upgrade: did:web for agents whose developers maintain a web domain
- Submantle generates and manages keys; developers never touch raw key material
- Library: `web5-go` for did:key + did:web (Apache-2.0, pre-v1.0, acceptable for current Python prototype; reassess for Go production)

**Layer 2 — Trust Attestation Format (Post-MVTL)**
- W3C VC 2.0 data model + SD-JWT (RFC 9901) selective disclosure
- New credential type: `BehavioralAttestation` (define schema; nothing equivalent exists)
- Revocation: Bitstring Status List pattern (W3C standard, SQLite-backed)
- Library: `go-sd-jwt` v1.4.0 (stable, production-ready)

**Layer 3 — Trust Registry Interface (V2)**
- Implement TRQP v2.0-compatible query API endpoint on top of Submantle's trust scores
- This makes Submantle the first behavioral trust registry in the TRQP ecosystem
- Enables cheqd-integrated systems to query Submantle agent trust automatically via TRAIN

**Layer 4 — Verifiable Presentation Exchange (V2)**
- OID4VP for agents presenting their BehavioralAttestation to brand partners
- DCQL query format (the forward direction per HAIP)
- Requires a VC wallet component for agents — design decision needed

**Compatibility without dependency:** Agents with decentralized identities (any DID method) can register with Submantle using their DID as their identifier. Submantle does not require any specific DID method — it accepts DIDs as identifiers and records behavioral data against them. Blockchain-based DIDs (did:ion, did:ethr) are fully compatible — Submantle just won't require them.

---

## What the Competition Looks Like in Decentralized Identity

**cheqd:** The closest infrastructure reference. Credential issuance, DID management, AnonCreds ZKPs, Bitstring Status List revocation. Blockchain-dependent (Cosmos). No behavioral layer. Apache-2.0. Potential partner, not competitor.

**SpruceID:** Digital trust infrastructure for governments. Rust-first. Building OID4VP and SD-JWT tooling. No behavioral trust layer. Not a competitor.

**OpenWallet Foundation:** Incubating OID4VC TypeScript libraries, DCQL, OpenID Federation. Standards infrastructure, not a product.

**HUMAN Security AgenticTrust:** Web-application-layer behavioral monitoring. No portable identity, no VC attestations, no DID support. The behavioral approach is similar to Submantle but the layer (web application vs. OS/device) and portability (per-website vs. universal) are fundamentally different. Already identified in synthesis.md as most sophisticated near-competitor.

**Key finding:** No organization in the decentralized identity space is building behavioral trust attestations. Everyone building in the DID/VC ecosystem is building identity/authorization infrastructure, not behavioral reputation infrastructure. The gap is confirmed from the decentralized identity angle as well as the standards angle.

---

## Confidence Assessment

| Finding | Confidence | Basis |
|---------|------------|-------|
| did:web is best DID method for Submantle agents | HIGH | Cross-confirmed: enterprise adoption, Cisco framework, W3C WG scope |
| did:ion is stalled/not recommended | HIGH | GitHub directly checked, last release 2022 |
| Ceramic Network pivoted away from identity | HIGH | Official blog post February 2025 |
| SD-JWT RFC 9901 final; go-sd-jwt v1.4.0 stable | HIGH | IETF datatracker + pkg.go.dev direct |
| W3C VC 2.0 final (7 specs May 2025) | HIGH | W3C press release |
| OID4VP final July 2025 | HIGH | OpenID Foundation announcement |
| No production Go v1.0 DID library | HIGH | pkg.go.dev direct searches |
| Submantle can implement TRQP-compatible interface | MEDIUM | Logical analysis; TRQP v2.0 spec review |
| did:webvh will supersede did:web | MEDIUM | WG draft; not finalized |
| BehavioralAttestation VC schema is novel | HIGH | No existing schema found anywhere |

---

*Research completed: 2026-03-11. External sources verified via WebSearch and WebFetch: W3C publications, IETF datatracker, pkg.go.dev, GitHub repositories, OpenID Foundation, Trust Over IP Foundation, Ceramic Network blog.*

*Sources consulted:*
- *https://datatracker.ietf.org/doc/rfc9901/*
- *https://pkg.go.dev/github.com/MichaelFraser99/go-sd-jwt*
- *https://pkg.go.dev/github.com/nuts-foundation/go-did*
- *https://pkg.go.dev/github.com/tbd54566975/web5-go/dids/didweb*
- *https://github.com/decentralized-identity/ion*
- *https://blog.ceramic.network/ceramic-is-joining-textile/*
- *https://trustoverip.github.io/tswg-trust-registry-protocol/*
- *https://w3c.github.io/did-methods-wg-charter/2025/did-methods-wg.html*
- *https://vidos.id/blog/openid4vp-reaches-final-status*
- *https://arxiv.org/html/2511.02841v1*
- *Plus internal expedition documents: synthesis.md, followup-2-bbs-plus-status.md, followup-3-cheqd-implementation.md, followup-4-ietf-eat-draft.md*
