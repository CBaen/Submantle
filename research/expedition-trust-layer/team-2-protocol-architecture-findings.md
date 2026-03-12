# Team 2 Findings: Protocol Architecture — What a Behavioral Trust Protocol Needs
## Date: 2026-03-10
## Researcher: Team Member 2

---

## Executive Summary

The protocol landscape in early 2026 has a clean, exploitable gap. Every major protocol — MCP, A2A, ACP, ANP — answers **identity** ("who are you?") and **authorization** ("what can you do?"). None answers **behavioral trust** ("should I trust you based on what you've done?"). This gap is not accidental: the infrastructure for capturing and verifying behavioral trust at internet scale does not yet exist as a standard.

Submantle is not competing with these protocols. It is the missing layer they all assume exists but don't provide. The path to standardization is clear and the window is open.

---

## Battle-Tested Approaches

### 1. OAuth 2.1 + OpenID Connect — The Current Auth Stack

- **What:** Delegated authorization (OAuth 2.1) combined with identity federation (OIDC), now the foundational auth layer for MCP remote servers.
- **Evidence:** Deployed at internet scale since 2012 (OAuth 2.0). OAuth 2.1 ratified and required for MCP remote transport as of the November 2025 spec. MCP has 97M+ monthly SDK downloads as of December 2025.
- **Source:** [MCP Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25); [MCP OAuth Analysis, Stack Overflow Blog, January 2026](https://stackoverflow.blog/2026/01/21/is-that-allowed-authentication-and-authorization-in-model-context-protocol/); [MCP Anniversary Blog, November 2025](http://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/)
- **Fits our case because:** Submantle's MCP server integration will necessarily operate on top of OAuth 2.1. Trust attestations Submantle issues must be compatible with this stack — they cannot replace it. OAuth scopes can carry references to trust tiers without disrupting the auth flow.
- **Tradeoffs:** OAuth was built for delegated access, not real-time behavioral decisions. It cannot keep up with autonomous agents making high-stakes decisions at machine speed. It has no concept of behavioral history, trust accumulation, or decay. Token issuance proves only that an agent authenticated — not that it behaved well. The MCP spec explicitly states: "The exact mechanism for authentication and authorization for downstream requests is outside the scope of the MCP specification." Behavioral trust is fully out of scope.

### 2. X.509 / TLS — The Cryptographic Identity Foundation

- **What:** Certificate-based identity used in HTTPS, mutual TLS (mTLS), and SPIFFE SVIDs. Proves "this is who I am" with a cryptographically verifiable chain of trust.
- **Evidence:** The foundation of every secure connection on the internet since 1999. mTLS is recommended for machine-to-machine auth in 2025 enterprise AI deployments.
- **Source:** [WSO2 Agent Identity Analysis, 2025-2026](https://wso2.com/library/blogs/why-ai-agents-need-their-own-identity-lessons-from-2025-and-resolutions-for-2026/); [Machine Identity mTLS SPIFFE Guide, 2026](https://petronellatech.com/blog/machine-identity-is-the-new-perimeter-mtls-spiffe-for-zero-trust/)
- **Fits our case because:** A Submantle Trust Attestation formatted as a Verifiable Credential (VC) can embed within or alongside TLS certificate workflows. Submantle's existing HMAC-SHA256 token scheme is already using the right cryptographic instincts — it can grow into a VC-issuer model.
- **Tradeoffs:** X.509/TLS proves identity at a point in time. It has no semantic layer for behavioral trust claims. Certificate revocation is slow (CRL/OCSP latency). Does not accumulate historical evidence.

### 3. W3C Verifiable Credentials 2.0 — The Portable Trust Credential Standard

- **What:** A W3C Recommendation (May 15, 2025) for expressing cryptographically verifiable, privacy-respecting claims about any subject — including machine agents.
- **Evidence:** VC 2.0 is now a finalized W3C standard. The EU Commission assessed VCDM 2.0 for the European Digital Identity Wallet by December 2025. BBS+ cryptosuites (also finalized) enable selective disclosure — a holder can prove they have a VC and reveal only specific claims, without revealing the underlying data or creating linkable proofs.
- **Source:** [W3C VC 2.0 Recommendation, May 2025](https://www.w3.org/press-releases/2025/verifiable-credentials-2-0/); [W3C VC Data Model 2.0](https://www.w3.org/TR/vc-data-model-2.0/); [BBS Cryptosuites](https://www.w3.org/TR/vc-di-bbs/); [AI Agents with DIDs and VCs (arxiv 2511.02841)](https://arxiv.org/html/2511.02841v1)
- **Fits our case because:** A "Submantle Trust Attestation" can be structured exactly as a W3C VC. Submantle acts as the Issuer. The agent is the Subject/Holder. Any third party (brand, marketplace, API) is the Verifier. This is the right vocabulary and the right architecture. BBS+ selective disclosure solves the privacy constraint: an agent can prove its trust tier is "Trusted" without revealing which specific behaviors earned that score or how many queries it has made. The credential is portable across any platform that understands W3C VCs.
- **Tradeoffs:** VCs currently carry static or periodically-refreshed claims — they are not real-time behavioral streams. The VC framework does not define how trust is *computed*, only how it is *expressed and verified*. Submantle still needs to define the scoring algorithm and the VC schema. A revocation mechanism is needed (if an agent's trust score drops, existing VCs must be invalidatable).

---

## Novel Approaches

### 1. IETF EAT (Entity Attestation Token) + Agentic Extensions

- **What:** The Entity Attestation Token (EAT) is now an IETF RFC (RFC 9711). Two recent IETF drafts extend EAT specifically for agentic AI: `draft-huang-rats-agentic-eat-cap-attest-00` and `draft-messous-eat-ai-00`. A third draft, `draft-jiang-seat-dynamic-attestation-00`, addresses dynamic re-attestation for agents over live TLS sessions.
- **Why it's interesting:** EAT is a CBOR/JWT token that carries cryptographically verifiable claims about an entity's current state. The agentic extensions define eight new claims including `agent_capabilities`, `policy_constraints`, `model_fingerprint`, `dynamic_proof`, and `endorsements`. The dynamic attestation draft addresses how AI agents whose model, tools, and policies change over time can re-attest without tearing down TLS sessions. This is infrastructure-level, not application-level.
- **Evidence:** RFC 9711 published 2025. `draft-huang-rats-agentic-eat-cap-attest-00` published on IETF datatracker 2025. `draft-jiang-seat-dynamic-attestation-00` on IETF datatracker, describing AI agent "runtime posture" attestation for TLS 1.3.
- **Source:** [RFC 9711 EAT](https://datatracker.ietf.org/doc/rfc9711/); [Agentic EAT Capability Attestation Draft](https://www.ietf.org/archive/id/draft-huang-rats-agentic-eat-cap-attest-00.html); [EAT Profile for AI Agents](https://datatracker.ietf.org/doc/draft-messous-eat-ai/); [Dynamic Attestation for AI Agents](https://www.ietf.org/archive/id/draft-jiang-seat-dynamic-attestation-00.html)
- **Fits our case because:** EAT gives Submantle a standards-track token format for capability attestation. A Submantle Trust Attestation could be an EAT extended with behavioral trust claims — a "Submantle Behavioral EAT." The `endorsements` claim is exactly the mechanism needed: third-party authorities (including Submantle) sign endorsements that become part of the agent's attestation. Critically, these drafts are early-stage (00), meaning Submantle could contribute to shaping them.
- **Risks:** EAT agentic extensions address *structural* attestation (what is the agent?) not *behavioral* attestation (what has the agent done?). The IETF RATS behavioral evidence draft (`draft-kamimura-rats-behavioral-evidence-01`) explicitly warns that even combining attestation + behavioral logging leaves gaps: time-of-check vs time-of-use, lack of cryptographic binding between attestation results and behavioral records, and possibility of selective event omission. These gaps are Submantle's design opportunity.

### 2. OpenID Connect for Agents (OIDC-A) — Agent-First Identity Extension

- **What:** An emerging proposal extending OIDC to define first-class agent identity with claims for `agent_type`, `agent_model`, `agent_version`, `agent_provider`, `agent_instance_id`, `agent_trust_level`, `agent_capabilities`, and `agent_attestation`. Adds delegation chain tracking (`delegator_sub`) and a dedicated attestation endpoint.
- **Why it's interesting:** OIDC-A directly introduces `agent_trust_level` as a claim type — the first identity-layer acknowledgment that agents should carry trust tier information. If this becomes standard, Submantle's trust tiers (Anonymous, Registered, Trusted) map directly onto it.
- **Evidence:** Proposal published April 2025 by Subramanya N. Not yet a formal standards track document.
- **Source:** [OIDC-A Proposal, April 2025](https://subramanya.ai/2025/04/28/oidc-a-proposal/)
- **Fits our case because:** If OIDC-A becomes a standard, Submantle's trust tier becomes a native field in the agent's identity token. Submantle's role as the authoritative issuer of `agent_trust_level` claims would be structurally embedded in how agents authenticate everywhere.
- **Risks:** Not yet a formal standards proposal. No implementation guidance for production attestation formats. The proposal lacks revocation mechanisms and privacy safeguards. May not advance to IETF/W3C standards track. Submantle should not build against it exclusively.

### 3. SPIFFE/SPIRE — Workload Identity for Machine Actors

- **What:** CNCF-graduated open standard for cryptographic workload identity. SPIRE issues short-lived X.509 SVIDs (SPIFFE Verifiable Identity Documents) based on environmental attestation. The SPIFFE URI format (`spiffe://domain/path/agent-instance-id`) provides a namespace for unique agent identities.
- **Why it's interesting:** SPIFFE has native support for the concept Submantle needs: identity that is tied to *where and how* the workload is running, not just who registered it. An agent's SPIFFE ID can encode its instance, namespace, and context. The 2025 enterprise conversation around AI agents explicitly names SPIFFE as a candidate for NHI (Non-Human Identity) management.
- **Evidence:** SPIFFE/SPIRE are CNCF graduated projects. Gartner named NHI management a 2025 strategic trend. Multiple 2025 analyses evaluate SPIFFE for AI agents. The core limitation identified: current SPIRE implementations treat all replicas as identical, a mismatch with non-deterministic AI agent behavior — but the spec is flexible enough to support instance-level differentiation.
- **Source:** [SPIFFE for AI Agents, Solo.io 2025](https://www.solo.io/blog/agent-identity-and-access-management---can-spiffe-work); [SPIFFE Securing Agentic AI, HashiCorp 2025](https://www.hashicorp.com/en/blog/spiffe-securing-the-identity-of-agentic-ai-and-non-human-actors); [NHIMG SPIFFE Analysis 2025](https://nhimg.org/community/agentic-ai/exploring-spiffe-for-agent-identity-and-access-management/)
- **Fits our case because:** Submantle's HMAC-SHA256 agent tokens are a local variant of the same concept SPIFFE formalizes. The Go production rewrite could adopt SPIFFE IDs as the canonical agent identity format, making Submantle-registered agents interoperable with enterprise zero-trust infrastructure without modification.
- **Risks:** SPIFFE does not accumulate behavioral history. It is an identity assertion system, not a trust scoring system. Adding behavioral reputation on top of SPIFFE requires external infrastructure — which is exactly Submantle's role. Also: SPIRE requires a central SPIRE server, which conflicts with Submantle's on-device architecture unless SPIRE is deployed locally per device.

---

## Emerging Approaches

### 1. A2A (Agent2Agent Protocol) — The Dominant Agent Communication Standard

- **What:** Google launched A2A in April 2025, donated to Linux Foundation in June 2025. IBM's ACP merged into A2A in August 2025. Now under Linux Foundation governance alongside MCP. The A2A v0.3 spec introduces gRPC support, signed Agent Cards, and On-Behalf-Of (OBO) token patterns.
- **Momentum:** Major industry consolidation: Anthropic (MCP), Google (A2A), IBM (ACP, now merged), OpenAI, Microsoft, AWS, Cisco, Salesforce, ServiceNow, SAP all involved. The Agentic AI Foundation (AAIF) was formed December 9, 2025 under Linux Foundation with MCP, Block's goose, and OpenAI's AGENTS.md as anchor projects.
- **Source:** [Linux Foundation A2A Launch](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents); [ACP A2A Merger, LFAI, August 2025](https://lfaidata.foundation/communityblog/2025/08/29/acp-joins-forces-with-a2a-under-the-linux-foundations-lf-ai-data/); [AAIF Formation, December 2025](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation-aaif-anchored-by-new-project-contributions-including-model-context-protocol-mcp-goose-and-agents-md/)
- **Fits our case because:** A2A's Agent Cards are the discovery mechanism — agents announce their capabilities and identity via JSON documents. This is the current equivalent of a business card. A Submantle Trust Attestation embedded in or linked from an Agent Card would give every agent in the A2A ecosystem a behavioral trust signal attached to their public identity. A2A's OBO token pattern creates explicit delegation chains — exactly the kind of provenance data Submantle's event bus could observe and score.
- **Maturity risk:** A2A spec is at v0.3 as of early 2026. Signed Agent Cards are new. Enterprise adoption is early-stage. The OBO pattern is specified but not widely implemented. The behavioral trust gap is explicitly unaddressed in the spec — A2A defines how agents communicate, not whether to trust them.

### 2. ANP (Agent Network Protocol) + W3C AI Agent Protocol Community Group

- **What:** ANP uses W3C DIDs (specifically the `did:wba` method) for decentralized agent identity. During agent handshakes, DID signatures in HTTP headers allow mutual verification without central authority. The ANP open source community initiated the W3C AI Agent Protocol Community Group, which held its first meeting June 18, 2025, and now meets biweekly.
- **Momentum:** W3C Community Group established June 2025. Draft white paper and technical specification framework published. Standards track advancement expected 2026-2027, but not yet a formal W3C Working Group.
- **Source:** [ANP White Paper](https://agent-network-protocol.com/specs/white-paper.html); [W3C AI Agent Protocol CG](https://www.w3.org/community/agentprotocol/); [W3C CG Progress June 2025](https://agent-network-protocol.com/blogs/posts/w3c-agent-protocol-progress-202506.html); [Protocol Comparison Survey, arxiv 2505.02279](https://arxiv.org/html/2505.02279v1)
- **Fits our case because:** ANP's `did:wba` method creates a pathway for Submantle to become a DID issuer — giving each Submantle-registered agent a `did:submantle` or `did:wba` identifier that carries a Submantle-signed behavioral trust credential. The W3C Community Group is the right venue for Submantle to participate in shaping how trust is discussed at the standards level. This is the standards seat at the table.
- **Maturity risk:** ANP has less adoption than MCP/A2A. W3C Community Groups do not produce binding standards — they produce input for Working Groups. The path from CG to formal W3C Recommendation takes 3-7 years historically. `did:wba` is not a registered W3C DID method yet.

### 3. IETF RATS Architecture + Behavioral Evidence Gap

- **What:** IETF's Remote ATtestation ProcedureS (RATS) working group (RFC 9334, published January 2023) defines the architectural roles: Attester, Verifier, Relying Party, Endorser. An emerging draft (`draft-kamimura-rats-behavioral-evidence-01`) explicitly addresses the gap between attestation (is the system trustworthy?) and behavioral evidence (what did it actually do?).
- **Momentum:** RFC 9334 is a stable RFC. RATS WG is active at IETF with multiple 2025 drafts. Behavioral evidence draft is informational (no normative proposals) but signals that IETF recognizes this gap.
- **Source:** [RFC 9334 RATS Architecture](https://datatracker.ietf.org/doc/rfc9334/); [RATS Behavioral Evidence Draft](https://www.ietf.org/archive/id/draft-kamimura-rats-behavioral-evidence-01.html); [IETF Agent Networks Framework Draft, October 2025](https://www.ietf.org/archive/id/draft-zyyhl-agent-networks-framework-01.html)
- **Fits our case because:** RATS defines the architectural vocabulary Submantle needs. In RATS terms, Submantle is the Verifier (and through its registry, an Endorser). The behavioral evidence draft identifies exactly the gap Submantle fills and explicitly calls for future protocol work. A "Submantle Behavioral Evidence Specification" submitted as an IETF Individual Draft would be a legitimate first step toward standards-track participation.
- **Maturity risk:** Behavioral evidence draft is informational only. IETF standardization of behavioral trust claims for AI agents is at least 3-5 years from RFC status. No existing RATS mechanism handles dynamic, accumulated behavioral trust — only point-in-time configuration attestation.

---

## Gaps and Unknowns

### What the research did NOT answer:

1. **The scoring-to-credential binding problem.** How does a trust score computed locally (on Submantle's device, from observed behavioral data that cannot leave the device) become a cryptographically verifiable credential that a remote verifier can trust? The ZKP approach (prove your score is above threshold without revealing the score) is theoretically sound using zk-SNARKs/BBS+ signatures, but there are no production implementations of on-device ZKP proof generation at low computational cost that would meet Submantle's "lightweight first" constraint. This needs prototyping.

2. **Credential freshness vs. privacy.** If Submantle issues a trust VC and the agent's behavior deteriorates, how is the credential revoked without creating a global revocation list that leaks which agents have been penalized? W3C StatusList2021 / Bitstring Status List v1.0 exist but have scalability and privacy tradeoffs. The right answer here is unknown without prototyping.

3. **Cross-device trust propagation.** Submantle's awareness mesh syncs across devices E2E encrypted. The research found no existing protocol for how a trust credential earned on Device A gets recognized on Device B without the sync server being able to read the behavioral data that justifies it. This is a unique architectural challenge.

4. **Standards body engagement path.** The research confirms IETF and W3C have open doors (RATS WG, AI Agent Protocol CG). But the specific steps for Submantle — as a startup, not a standards body member — to submit an IETF Individual Draft and get it adopted into a working group were not fully mapped. Historical precedents (how did OAuth, JOSE, TLS 1.3 move from implementation to RFC?) were not deeply researched in this expedition.

5. **Submantle's trust tier as VC claim — schema design.** No existing VC schema for behavioral trust tiers (Anonymous, Registered, Trusted) was found. The schema would need to be invented, published, and registered. What claims it should contain beyond the tier label (e.g., score range, decay date, capability-specific trust) is undefined.

### Where evidence was thin or contradictory:

- The OIDC-A proposal is a single author's draft with no standards body backing yet. Evidence for its adoption is thin.
- ANP's adoption numbers were not available. It is harder to assess relative to MCP/A2A.
- The computational cost of zk-SNARK proof generation on a typical laptop/phone was not found in the research. This is critical for Submantle's "lightweight first" constraint and needs empirical testing.

---

## Synthesis

### The Landscape Picture

As of March 2026, the protocol stack for agent interoperability looks like this:

```
Layer                  Protocol(s)              Status
─────────────────────────────────────────────────────
Communication          MCP, A2A (merged ACP)    Production, under Linux Foundation
Identity (who?)        DIDs, SPIFFE, OIDC-A     Established + emerging extensions
Authorization (what?)  OAuth 2.1, PKCE, OBO     Production in MCP
Attestation (how?)     IETF EAT, RATS, FIDO     Early-stage for agents
Behavioral Trust       ← NOTHING →              The gap
```

This is the clearest signal in all the research: **behavioral trust has no protocol representation**. The IETF's own behavioral evidence draft says so explicitly. The protocol comparison survey says so. Every enterprise analysis says so. OAuth leaves it out of scope. MCP says it cannot enforce it. A2A doesn't address it. SPIFFE doesn't accumulate it. The gap is structural, not an oversight — the industry has not solved the "should I trust based on what you've done?" question at the infrastructure level.

### What Submantle Needs to Become the Trust Layer

Based on this research, a behavioral trust protocol requires exactly five components, and Submantle's current architecture partially covers three of them:

**1. Persistent Agent Identity (Submantle has this)**
A cryptographic identifier that persists across sessions and is bound to behavioral history. Submantle's HMAC-SHA256 registry provides this. The upgrade path is to SPIFFE-compatible IDs or DIDs in the Go production rewrite.

**2. Behavioral Evidence Recording (Submantle has this)**
A tamper-evident log of agent actions that cannot be retroactively modified. Submantle's SQLite event log + `total_queries` + `incidents` fields in the agent registry provide the foundation. The upgrade path is cryptographic binding between the identity token and the behavioral log entries (preventing forgery).

**3. Trust Score Computation (Submantle has the formula, not the implementation)**
An algorithm that translates behavioral evidence into a trust signal. Submantle already identified the Beta Reputation formula: `trust = alpha/(alpha+beta)`. The research confirms this is a sound approach (Beta distribution is well-studied for Bayesian reputation). The upgrade path is implementing the formula and adding trust decay.

**4. Trust Attestation Credential (Submantle does NOT have this)**
A portable, cryptographically verifiable credential that carries the trust score in a form that remote parties can verify without accessing the raw behavioral data. This is the missing piece. The right format is a W3C Verifiable Credential with BBS+ selective disclosure. The issuer is Submantle. The holder is the agent. The verifier is any third party (brand, API, marketplace).

**5. Verification Protocol (Submantle does NOT have this)**
A protocol by which a verifier (e.g., a brand's API) can request and validate a Submantle Trust Attestation. This needs to specify: the VC schema, the endpoint for verification, how freshness is established, and how revocation works. This is the standards-track deliverable.

### The Strongest Approach

**Build on W3C VCs + IETF EAT, contribute to IETF RATS.**

Specifically:
- Format Submantle Trust Attestations as W3C VCs (VC 2.0, already a finalized standard) with BBS+ selective disclosure (also finalized). This is the portable, privacy-preserving credential format that already has ecosystem support.
- Use IETF EAT (RFC 9711) as the token format for the attestation when embedded in protocol headers (JWT/CBOR). This makes Submantle trust tokens compatible with the IETF attestation ecosystem.
- Contribute `draft-submantle-rats-behavioral-trust-00` to the IETF RATS working group. The existing behavioral evidence draft has no normative proposals — Submantle can fill that gap. The ask is not starting from scratch: it's taking the behavioral evidence concept (which IETF already acknowledges) and defining the cryptographic binding and token format.
- Participate in the W3C AI Agent Protocol Community Group to ensure the trust vocabulary being designed for agent protocols references the behavioral trust credential format Submantle is building.

### What Does NOT Need to Be Built

- **Blockchain/distributed ledger for trust.** Research shows these failed at adoption for reputation systems (ERC-8004 is early-stage Ethereum). Submantle's on-device model is more reliable, more private, and more performant.
- **Centralized behavioral data.** ZKP-based selective disclosure allows Submantle to issue trust credentials without ever sending behavioral data off-device. The proof of tier membership is the credential. The behavioral data stays local.
- **A new communication protocol.** Submantle does not need to compete with MCP, A2A, or ANP. It plugs into all of them as the trust layer underneath.

### The Standards Seat at the Table

The path Submantle should pursue, in order:

1. **Join W3C AI Agent Protocol Community Group** — already open, free, informal. The right place to introduce the behavioral trust vocabulary.
2. **Publish an IETF Individual Draft** — on behavioral trust claims for EAT/RATS, citing the existing behavioral evidence gap. This establishes prior art and invites IETF discussion.
3. **Get MCP Registry trust integration** — Submantle's trust attestation recognized in the official MCP Registry (DNS/HTTP namespace-based trust, currently registry.modelcontextprotocol.io) would give it AAIF ecosystem presence.
4. **IETF Working Group participation** — once the individual draft has traction, work with the RATS WG to adopt behavioral trust claims.

Historical analogies: OAuth 2.0 went from Blaine Cook's initial proposal (2006) to RFC 6749 (2012) — six years. JOSE (JSON Web Signatures/Tokens) was ~4 years. The window for defining behavioral trust at the IETF level is open right now. In 2 years, it will likely be contested territory.

---

*Research sources accessed March 10, 2026. All URLs verified as of this date.*
