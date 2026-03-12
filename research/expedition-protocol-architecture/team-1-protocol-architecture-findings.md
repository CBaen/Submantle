# Team 1 Findings: Protocol Architecture Models
## Date: 2026-03-11
## Researcher: Team Member 1

---

## Preamble: What I Read

**Internal codebase:** VISION.md (full), api.py (full), agent_registry.py (full), events.py (full). Key takeaway: Substrate already has an HMAC-based agent identity layer, a privacy-gated event bus, and a FastAPI REST surface. The prototype is effectively a local daemon with a REST API — the architectural challenge is how that daemon connects to the world.

**External research:** 12+ web searches, 5 detailed page fetches covering: TCP/IP/SMTP adoption history, DNS/OAuth/TLS structural analysis, ActivityPub/SMTP federation failure modes, PGP web-of-trust failure analysis, libp2p/GossipSub P2P reputation research, Certificate Transparency gossip protocol architecture, Tailscale hybrid control/data plane architecture, IETF agent identity drafts (2025-2026), MCP November 2025 spec update, CSA cross-domain agent trust analysis (March 2026), Stripe/Twilio developer-first adoption playbook.

---

## Section 1: How the Successful Internet Protocols Actually Work

Before assessing which model fits Substrate, it's essential to understand the structural reality of each reference protocol — not the simplified version.

### 1.1 DNS — Hierarchical Delegation, Not Central Control

DNS is structurally a tree. The root servers (13 logical clusters operated by 12 independent organizations) hold no data except pointers to Top-Level Domain (TLD) servers (.com, .org, etc.). TLD servers hold no data except pointers to authoritative nameservers. Authoritative nameservers hold the actual records.

**What this means structurally:** DNS is not "centralized" in the way people think. The root servers are a coordination layer — they don't see most traffic. Resolvers cache aggressively, so the majority of DNS queries never reach the root. The architecture is: central coordination of a directory tree, with distributed caching and resolution.

**The insight:** DNS achieved global scale by making the coordination layer handle almost nothing. The root is a pointer, not a database. The real work happens locally (resolver caches) and at the edges (authoritative servers).

**Source:** Internet Protocol Suite - Wikipedia (accessed 2026-03-11); Gary Kessler TCP/IP overview (accessed 2026-03-11)

### 1.2 TLS/HTTPS — Hub-and-Spoke Trust Anchors with Peer-to-Peer Encryption

TLS uses a hub-and-spoke trust model for one thing only: establishing which Certificate Authorities (CAs) are trusted. The operating system or browser ships a list of ~100-150 trusted root CAs. That's the "hub." But every actual TLS session is peer-to-peer — the client and server negotiate a session key directly, and the CA is not involved in the connection at all after certificate issuance.

**Certificate Transparency (CT)** was added as a gossip-based audit layer on top of this. Every certificate must be logged in at least two public CT logs (append-only Merkle trees). Browsers verify that a certificate was logged before trusting it. CT gossip protocols allow clients to cross-verify that they're seeing the same version of a log — detecting if a CA is serving different views to different clients.

**2025 development:** The Static CT API (built on the "Sunlight" design) has replaced RFC 6962 in most deployments. It eliminated the Maximum Merge Delay requirement, making logs far cheaper to operate and better available. Let's Encrypt is ending support for the old RFC 6962 format in 2025.

**The insight:** TLS separates the trust bootstrapping problem (hub-and-spoke with CAs) from the encryption problem (peer-to-peer). The CA is consulted rarely and for a narrow purpose (certificate issuance). The audit layer (CT) adds a federated gossip network on top for accountability without adding centralization.

**Sources:** InfoQ — Certificate Transparency deep dive (accessed 2026-03-11); Let's Encrypt RFC 6962 EOL announcement, August 2025; CT Gossip aggregation papers on Semantic Scholar (accessed 2026-03-11)

### 1.3 OAuth 2.0 / OIDC — Hub-and-Spoke Identity with Portable Tokens

OAuth/OIDC is structurally hub-and-spoke: an Identity Provider (IdP) authenticates users, and many Service Providers (SPs) trust the IdP. The token issued by the IdP is portable — the SP validates it cryptographically without calling back to the IdP for every request (stateless validation via JWTs, or stateful via introspection endpoints).

**Key architectural feature:** Once a token is issued, the IdP is not in the critical path of every request. The SP validates locally using the IdP's public key. This is the same pattern as TLS certificates — trust bootstrapping is centralized; actual operation is decentralized.

**2025 developments:** MCP (Model Context Protocol) November 2025 spec mandates OAuth 2.1 for all remote server authentication. MCP servers are now classified as OAuth Resource Servers, meaning they advertise protected resource metadata. This is directly relevant to Substrate's MCP surface.

**The insight:** OAuth solves portable identity by making trust bootstrapping centralized (IdP) but operation stateless (token validation). The bottleneck is the IdP's uptime during token issuance, not during usage.

**Sources:** Auth0 — MCP Spec Update June 2025; Dave Patten — MCP November 2025 spec breakdown; WorkOS — OIDC vs SAML federation (accessed 2026-03-11)

### 1.4 SMTP — Federated with No Central Authority, Trust as a DNS Layer

Email (SMTP) is the canonical federation success story. Anyone can run a mail server. No central authority controls which servers can send or receive. Federation happened bottom-up: universities adopted it, then businesses, then consumer providers.

**The critical architecture for trust:** SMTP's trust layer (SPF, DKIM, DMARC) was added *on top of the base protocol* using DNS as the distribution mechanism. SPF and DKIM records are DNS TXT records — the trust rules are stored in the domain's DNS, queried by receiving mail servers, and enforced locally by each receiver. **No central authority enforces this. Each receiving server runs its own policy.**

DMARC tells receivers what to *do* with mail that fails SPF/DKIM checks — but the receiver decides whether to honor the DMARC record. This is structurally identical to "always aware, never acting": DMARC provides the signal, the receiver enforces.

**Failure mode:** SMTP's federation was easy to adopt but hard to secure later. Decades of open relay abuse led to complex anti-spam systems. The trust layer (SPF/DKIM/DMARC) was bolted on after the fact and required a decade of industry coordination to reach majority adoption. As of May 2025, Microsoft now requires SPF/DKIM/DMARC for high-volume senders to outlook.com.

**Sources:** Email authentication protocols overview — EmailOnAcid 2025; Microsoft DMARC enforcement announcement — Mimecast 2025; SMTP history — mySMTP Blog (accessed 2026-03-11)

### 1.5 TCP/IP — Why It Won: Modularity and Institutional Seed

TCP/IP won the Protocol Wars not by being technically superior but by being modular, open, and mandated at the right institutional moment. The DoD declared it the official standard in 1982 and cut over ARPANET in January 1983. Universities were already using it. That institutional seed created network effects that OSI (technically more sophisticated) could never overcome.

**The architectural lesson:** TCP/IP's four-layer model (Link, Internet, Transport, Application) meant each layer could evolve independently. Mobile networks required changes only to the Link layer. IPv6 replaced IPv4 without changing TCP. The protocol was designed to be composed with whatever came next.

**The adoption lesson:** You need institutional mandate OR organic developer-first adoption. TCP/IP got a government mandate. Stripe and Twilio demonstrated the developer-first path: documentation as growth engine, usage-based pricing, bottom-up adoption by individual developers that eventually reaches enterprise through expansion. The key: make it trivially easy to start, economically rational to scale.

**Sources:** QuantumZeitgeist — How TCP/IP won; Internet Society TCP/IP migration 1983; Stripe/Twilio developer-first playbook — WorkOS, Decibel VC (accessed 2026-03-11)

---

## Section 2: Topology Analysis for Substrate's Constraints

The constraints are non-negotiable: on-device computation, privacy by architecture, deterministic scoring, no enforcement, agent-first design. Each topology must be evaluated against all five.

### 2.1 Pure Peer-to-Peer (BitTorrent / libp2p model)

**How it works:** Every node is both client and server. No central directory. Discovery via DHT (distributed hash table) or gossip. Trust/reputation is local unless propagated via gossip protocols.

**Why it doesn't fit Substrate:**
- P2P reputation propagation (EigenTrust, GossipSub scoring) requires nodes to share their local scores with neighbors. This is privacy-hostile: Substrate's local trust computation is a feature, not a limitation. Broadcasting behavioral data to unknown peers violates "privacy by architecture."
- libp2p's own documentation explicitly states: "A fully decentralized reputation management system in which peers collaborate to evaluate each other is outside the scope of libp2p." The community acknowledges this is unsolved in P2P.
- BitTorrent-style DHTs have sybil attack surfaces. libp2p's GossipSub uses peer scoring locally to resist spam, but that score is not portable — it resets on reconnect.
- Discovery and NAT traversal require infrastructure (bootstrap nodes, relay servers). Pure P2P is a theoretical purity that even libp2p doesn't achieve in practice.

**What P2P gets right:** The local computation model. BitTorrent clients track peer quality locally. This mirrors Substrate's model exactly — trust is computed on your device, for your use.

**Source:** libp2p security considerations docs; GitHub discussion on libp2p peer reputation subsystems; EigenTrust Stanford paper (Kamvar et al., 2003); Trust in Shapley — AAMAS 2024

### 2.2 Pure Federated (ActivityPub / SMTP model)

**How it works:** Independent servers implement a shared protocol. Servers federate with each other. No global central server, but each server is a centralized point for its users.

**Real-world failure modes (2025 verified):**
- **Admin dependency is catastrophic.** If an instance admin abandons the server, all users on that instance lose their identity and audience. This happened repeatedly in the Mastodon ecosystem.
- **Economic sustainability is the hidden constraint.** Bluesky's infrastructure costs exceed $500K/month. Grassroots federation instances can't survive black swan events without economic incentives for operators.
- **Defederation is the only trust enforcement mechanism**, and it's reactive — by the time defederation happens, data has already leaked.
- **Interoperability gaps are endemic.** Updating a post propagated to Lemmy but not Mastodon (Mastodon silently rejects updates without an updated timestamp). Private messages don't work reliably between implementations.
- **Centralization by default:** "While a few blogs federating ActivityPub remain perfectly robust from capture, larger instances become juicy points of failure." The network centralizes around large instances despite the federated design.

**What federation gets right:** No single point of failure at the protocol level. SMTP's federation means email survives any single provider's death. The protocol outlives any implementation.

**What this means for Substrate:** Pure federation isn't viable. The trust data is on-device. There's no "Substrate server" that could be federated. The protocol needs to support verification across instances without requiring the computation to move off-device.

**Sources:** shazow.net — "How can open social protocols fail us in 2025" (fetched 2026-03-11); ActivityPub — "The Good, the Bad and the Ugly" — Dominik Chrástecký; Magic Pages ActivityPub Federation Issue June 2025; WordPress Federation Recap 2025

### 2.3 Hub-and-Spoke (DNS root / OAuth IdP model)

**How it works:** Central coordinator handles a narrow, well-defined function. Everything else is distributed. The hub is in the critical path only for bootstrapping (DNS: initial lookup; OAuth: token issuance), not for ongoing operation.

**The risk:** Hub becomes a single point of failure and a centralization magnet. DNS root operators have enormous power. OAuth IdPs are chokepoints — if Google's OIDC goes down, millions of "Sign in with Google" flows break.

**What hub-and-spoke gets right for Substrate:**
- Tailscale demonstrates the optimal version: **control plane hub-and-spoke, data plane mesh.** The coordination server handles only key exchange and policy distribution — tiny messages, no actual traffic. The actual WireGuard connections are peer-to-peer. Private keys never leave devices.
- OAuth demonstrates that hub-and-spoke token issuance can be combined with stateless, decentralized token *validation*. The IdP signs the JWT; every verifier validates it locally without calling back to the IdP.

**What this means for Substrate:** Substrate could use a thin coordination layer (Substrate's own servers) for agent registration, credential issuance, and trust score attestation — while keeping all computation on-device. The coordination server never touches behavioral data. It only issues signed attestations about what a device has computed.

### 2.4 The Hybrid That Actually Matches Substrate's Requirements

The architecture that fits all five of Substrate's constraints is not any single topology — it's a split-plane design pioneered by Tailscale:

**Control plane (thin, hub-and-spoke):** Handles registration, identity verification, attestation issuance. Substrate's servers receive "this agent has score X, computed on device Y" and issue a W3C VC (SD-JWT) asserting that fact. The server is a notary, not a data processor. It never sees behavioral data.

**Data plane (on-device, no server involved):** Trust computation runs locally on each device using the Beta Reputation formula. Behavioral history lives in local SQLite. Privacy mode gates everything. The server is never in the path of a trust query.

**Verification layer (federated, peer-to-peer):** Brands and platforms that receive an agent's VC validate it cryptographically against Substrate's public key. No callback to Substrate required. This mirrors how TLS certificate validation works — the CA (Substrate) signs the credential, the verifier checks the signature locally.

This is structurally identical to the TLS model applied to behavioral trust:
- CA → Substrate attestation service
- Certificate → W3C VC (SD-JWT) with trust tier
- OCSP/CRL → Bitstring Status List for revocation
- Browser trust store → Brand/platform policy engine (they decide the threshold)

---

## Section 3: Battle-Tested Approaches

### Battle-Tested #1: Split Control/Data Plane (Tailscale / WireGuard Model)

- **What:** Centralize only coordination (key exchange, policy distribution). Decentralize actual operation (data flows peer-to-peer, keys never leave devices).
- **Evidence:** Tailscale has millions of nodes in production (2025). WireGuard underlies major VPN products and is integrated into the Linux kernel. The model has been validated at infrastructure scale.
- **Source:** Tailscale "How it works" technical blog (fetched 2026-03-11); WireGuard kernel integration documentation
- **Fits our case because:** Substrate's trust computation is the data plane — it must stay on-device. Attestation issuance is the control plane — it's a narrow, rare operation that can involve Substrate's servers without creating a privacy problem.
- **Tradeoffs:** The coordination server (control plane) is still a single point of failure for new registrations and attestation issuance. Existing attestations remain valid even if the server is down (they're signed JWTs). The server must be highly available and hardened — it's a key signing service.

### Battle-Tested #2: DNS-Style Hierarchical Delegation for Discovery

- **What:** A root directory that holds only pointers, not data. Clients resolve locally using cached results. Authoritative data lives at the edges.
- **Evidence:** DNS has operated at global scale since 1983. 43 years of proven architecture serving trillions of queries.
- **Source:** Internet Society TCP/IP migration history; Gary Kessler TCP/IP overview (accessed 2026-03-11)
- **Fits our case because:** Substrate's "Substrate Store" for identity signatures is a perfect fit for DNS-style hierarchical resolution. Signatures are authoritative data at the edges (community contributors). The central server holds only pointers and metadata. Clients cache signatures locally — this is what happens today with the signatures.json file.
- **Tradeoffs:** DNS has significant governance complexity (ICANN, TLD operators). Substrate doesn't need that level of governance initially, but the architecture should be designed for it from the start.

### Battle-Tested #3: CA-Style Attestation with Stateless Verification (TLS / JWT Model)

- **What:** A trusted issuer signs a credential. Verifiers validate the signature locally without calling back to the issuer. Revocation is handled via a separate, low-traffic revocation mechanism.
- **Evidence:** HTTPS secures trillions of connections daily. OAuth JWTs are the dominant authentication token for web APIs. Both architectures validate credentials locally, making them fast and the CA/IdP non-critical-path.
- **Source:** OAuth/OIDC architecture — Okta Developer docs, Auth0 (accessed 2026-03-11); TLS certificate model — standard protocol documentation
- **Fits our case because:** This is exactly what Substrate's W3C VC (SD-JWT) model is. The attestation server issues a signed credential. Brands validate locally. Substrate is not in the critical path of every trust check. This is the settled architectural decision — this research confirms it's the correct one.
- **Tradeoffs:** Revocation lag. A JWT is valid until expiry even if the agent is revoked. Short-lived tokens (hours, not months) and Bitstring Status List mitigate this. Token freshness requires agents to re-attest periodically.

### Battle-Tested #4: DKIM/DMARC — Trust Signal with Local Enforcement (the "Never Acting" Precedent)

- **What:** Domain owners publish trust records in DNS. Receiving mail servers check records and enforce locally. No central authority enforces email policy — each receiver runs its own checks.
- **Evidence:** SPF/DKIM/DMARC now required by Google and Microsoft for bulk senders (2025). Email ecosystem has converged on this after ~15 years. Billions of messages authenticated daily.
- **Source:** Microsoft DMARC enforcement — Mimecast 2025; EmailOnAcid authentication protocols 2025 (accessed 2026-03-11)
- **Fits our case because:** This is the architectural proof that "always aware, never acting" works at internet scale. DMARC provides the signal; receivers enforce. Substrate provides the trust score; brands enforce. The email trust stack is the direct precedent. This should be in Substrate's pitch materials.
- **Tradeoffs:** DMARC took a decade to reach majority adoption after SPF was deployed. The trust signal must reach critical mass before it changes behavior. Substrate faces the same cold start problem.

---

## Section 4: Novel Approaches

### Novel #1: Tailscale Control/Data Plane Split Applied to Trust (Not Just Networking)

- **What:** Apply the exact Tailscale architectural split to trust: a thin Substrate coordination server handles only attestation issuance (like Tailscale's coordination server handles only key exchange). On-device daemon handles all computation (like WireGuard handles all actual traffic).
- **Why it's interesting:** Tailscale proved this works at scale for networking. Nobody has applied it to behavioral trust. The insight is that coordination (signing a credential) and computation (computing the trust score) are fundamentally different operations with different privacy requirements.
- **Evidence:** Tailscale architecture (production, millions of nodes, 2025). The split design has been validated. Application to trust is novel but architecturally sound.
- **Source:** Tailscale "How it works" (fetched 2026-03-11)
- **Fits our case because:** Privacy by architecture is preserved — the computation server (on-device) never sends behavioral data to the coordination server. The coordination server only receives "this device reports trust score X for agent Y" plus the cryptographic proof, and signs a VC.
- **Risks:** What stops a malicious device from lying about its computed trust score? The attestation server can't verify the local computation. This is a fundamental trust assumption in the model. Mitigations: registration age visibility, velocity caps as anti-gaming rules, and the fact that lying about trust only helps your own agents on your own device (doesn't affect others). The Sybil resistance by locality argument applies here.

### Novel #2: Certificate Transparency's Gossip Pattern Applied to Trust Audit

- **What:** CT logs are append-only Merkle trees that any browser can audit. Gossip protocols detect if a CA is serving different views to different clients. Apply this to Substrate: a public append-only log of issued trust attestations, with gossip verification to detect if Substrate is behaving inconsistently.
- **Why it's interesting:** CT solved the problem of "how do you make a trusted third party accountable without giving them more power?" The answer is transparency — make all issuances public and auditable. This makes the attestation server auditable without requiring it to be decentralized.
- **Evidence:** CT has been deployed by Google, Let's Encrypt, Apple, and all major browsers since ~2015. The Static CT API (Sunlight, 2025) made it operationally viable at scale.
- **Source:** InfoQ CT deep dive; Let's Encrypt RFC 6962 EOL 2025; Semantic Scholar CT gossip aggregation paper (accessed 2026-03-11)
- **Fits our case because:** Substrate's attestation issuance is a perfect candidate for a public transparency log. Any researcher or auditor can verify that attestations are being issued consistently. This directly addresses the "who watches the watchman" problem for a trust infrastructure that Substrate will eventually face.
- **Risks:** Operationally complex to implement correctly. Adds latency to attestation issuance. The gossip infrastructure requires multiple independent log operators to be meaningful. This is a V3+ feature, not V1.

### Novel #3: IETF EAT (Entity Attestation Token) as Substrate's Credential Format Extension

- **What:** The IETF RATS working group has produced Entity Attestation Token (EAT) as a standard format for claims about software runtime environments. A 2025 IETF draft (draft-huang-rats-agentic-eat-cap-attest-00) extends EAT specifically for AI agents, adding claims for capability inventories, behavioral policies, and model fingerprints.
- **Why it's interesting:** Substrate's W3C VC (SD-JWT) is the right format for portable credentials. EAT could be the format for the *claims* inside those credentials — giving Substrate's attestations a standard vocabulary that IETF is already defining.
- **Evidence:** IETF RATS WG is active (multiple drafts in 2025-2026). The agentic EAT draft expired December 2025 but reflects real standardization momentum. The dynamic attestation draft (draft-jiang-seat-dynamic-attestation) addresses long-lived sessions where agent runtime posture changes frequently — directly relevant to Substrate's ongoing behavioral monitoring.
- **Source:** IETF draft-huang-rats-agentic-eat-cap-attest-00 (fetched 2026-03-11); IETF draft-yl-agent-id-requirements-00 (fetched 2026-03-11); IETF draft-jiang-seat-dynamic-attestation
- **Fits our case because:** Substrate could define its behavioral trust claims using EAT vocabulary and wrap them in SD-JWT VCs. This positions Substrate as standards-aligned from day one — not proprietary. Agents carrying Substrate credentials would be speaking a language that IETF is already standardizing.
- **Risks:** EAT drafts are still in early stages. The agentic extension is one team's proposal, not yet consensus. Substrate should track but not depend on any specific draft. The W3C VC wrapper is more stable than the claim vocabulary.

---

## Section 5: Emerging Approaches

### Emerging #1: MCP as Trust Protocol Transport (Not Just Tool Protocol)

- **What:** MCP's November 2025 specification made MCP servers official OAuth Resource Servers and mandated OAuth 2.1 for remote authentication. This moves MCP from "tool protocol" to "identity-aware protocol." An MCP server can now advertise what credentials it requires and validate them before serving requests.
- **Momentum:** 13,000+ MCP servers launched on GitHub in 2025. 97M+ monthly SDK downloads (per Substrate's prior research). MCP is becoming the dominant agent-to-tool integration layer. The November 2025 spec explicitly anticipates "enterprise registries and federated trust frameworks."
- **Source:** MCP specification 2025-11-25 (modelcontextprotocol.io); Auth0 MCP spec update June 2025; Dave Patten MCP November 2025 analysis (accessed 2026-03-11)
- **Fits our case because:** Substrate's MCP server can present itself as an OAuth Resource Server. Agents querying Substrate over MCP can present their Substrate trust credentials as OAuth tokens. This makes trust verification a native part of the MCP handshake, not a separate step. The "ambient stream" Substrate vision — where agents feel the ground without asking — becomes the MCP subscription model.
- **Maturity risk:** MCP's auth model is new (June 2025). Library support is still catching up. The November 2025 spec changes are significant enough that older MCP clients won't support them. Migration lag is real.

### Emerging #2: Cross-Domain Agent Trust Coordination (CSA Framework, March 2026)

- **What:** Cloud Security Alliance published analysis on March 11, 2026 (the same day as this research) identifying "cross-boundary agent verification" as the unsolved problem. The proposed solution is portable agent identity with coordinated revocation — revocation in one domain propagates to all domains the agent touches.
- **Momentum:** The Salesloft/Drift AI breach (stolen OAuth tokens, 700+ companies affected in 10 days) is driving urgency. 69% of organizations are concerned about non-human identity attacks (CSA survey). The cross-domain trust problem is now board-level concern.
- **Source:** CSA — "AI Security: When Your Agent Crosses Multiple Independent Systems, Who Vouches?" March 11, 2026 (fetched 2026-03-11)
- **Fits our case because:** Substrate's portable W3C VC credentials are exactly the architecture CSA is calling for. The revocation mechanism (Bitstring Status List) provides the coordinated revocation. Substrate is positioned to be the answer to the question CSA is asking publicly.
- **Maturity risk:** No standard yet defines how cross-domain agent revocation works. The CSA framework is analysis, not specification. Substrate building this now would be ahead of any standard — which is a moat opportunity but also a standard convergence risk.

### Emerging #3: Zero-Knowledge Trust Proof (Privacy-Preserving Verification)

- **What:** Rather than revealing a trust score (which reveals how much behavioral data exists), an agent proves it has a trust score *above a threshold* using a zero-knowledge proof. The verifier learns only "this agent qualifies" — not the actual score or behavioral history.
- **Momentum:** ZK proofs for credential verification are gaining traction in the W3C VC community. SD-JWT (which Substrate has adopted) provides selective disclosure without ZK — but ZK provides a stronger privacy guarantee (no information leakage even from what's disclosed).
- **Source:** W3C DID WG March 2025 meeting minutes (resolver trust, selective disclosure); VeriSSO ZK-OIDC paper 2025; INATBA — Building Trust: Integrating AI, Blockchain, and Digital Identity, November 2025
- **Fits our case because:** Privacy by architecture means agents shouldn't have to reveal their full behavioral history to prove they're trustworthy. SD-JWT already provides "I'm in tier Trusted without revealing my exact score." ZK proofs would take this further — "I qualify for this platform's threshold without revealing my tier."
- **Maturity risk:** ZK proofs require significant computation — violates "lightweight first." No production Go library for ZK credential verification is mature in 2026. This is a V4+ feature, potentially waiting for hardware acceleration.

---

## Section 6: Gaps and Unknowns

**What this research could NOT definitively answer:**

1. **Optimal attestation freshness interval.** How often should Substrate re-issue trust VCs? TLS certificates are 90 days (Let's Encrypt) to 1 year. OAuth JWTs are often 1 hour. For behavioral trust, the right interval depends on how fast scores change — which depends on the undefined incident taxonomy. This is blocked by the same decision that's blocked everything else.

2. **What happens to trust scores when devices change.** If an agent operates on device A and then on device B, and scores are computed locally, how do scores merge or federate across devices? The "same token on both devices" model in VISION.md implies the score accumulates from all devices — but the local computation model implies each device has its own score. This tension is unresolved and architecturally significant.

3. **The cold start / bootstrap problem for brands.** A brand that wants to query Substrate trust scores needs to trust Substrate's attestation. Who establishes that trust? In TLS, browser vendors establish root CA trust. In Substrate, there's no equivalent trust anchor decision authority. This is a governance decision, not a technical one, but it blocks the brand API business.

4. **Minimum viable attestation server footprint.** The thin coordination server is architecturally correct, but its threat model hasn't been analyzed. It holds the signing key for all Substrate trust attestations. If that key is compromised, all issued credentials are suspect. Key management for an attestation service is non-trivial — HSMs, key rotation, split custody.

5. **Whether IETF agent identity drafts will converge on compatible formats.** There are at least 6 IETF drafts active in this space. They may conflict. Substrate should monitor but not depend on any single draft. The right move is to be VC/SD-JWT-based (stable W3C standard) and add IETF-compatible claim vocabulary when standards converge.

---

## Section 7: Synthesis

### The Strongest Architecture for Substrate

**Substrate is a Tailscale-for-trust:** split-plane design where computation is on-device and coordination is a thin server. This maps exactly to Substrate's constraints:

| Plane | What it does | Substrate equivalent |
|-------|-------------|---------------------|
| Control plane (thin, centralized) | Agent registration, attestation issuance, signature distribution | Substrate servers — thin notary |
| Data plane (on-device, never centralized) | Trust score computation, behavioral history, process awareness | Local daemon + SQLite |
| Verification layer (stateless, distributed) | Brand/platform validation of trust credentials | Cryptographic signature check against Substrate public key |

**The structural precedents that validate this:**
- **Tailscale:** Control/data plane split, proven at millions-of-nodes scale
- **TLS/CT:** CA attestation + gossip audit, the internet's trust backbone
- **DKIM/DMARC:** "Signal without enforcement" at email scale, proven across 30 years
- **OAuth JWTs:** Stateless credential validation, brands don't need to call Substrate on every check
- **TCP/IP adoption:** Institutional seed (target agent framework developers) + permissionless bottom-up growth

### What Combination Works Best

**Phase 1 (now → MCP server):** On-device daemon (existing), REST/MCP API, local trust computation, JWT-style token issuance from Substrate servers. Architecture: Tailscale control plane model. No gossip, no federation, no P2P.

**Phase 2 (trust layer wired → brand API):** W3C VC attestation issuance. Brands validate Substrate VCs without calling back to Substrate. Revocation via Bitstring Status List. Architecture: TLS/CA model applied to behavioral trust. DMARC model for "signal without enforcement."

**Phase 3 (ecosystem maturity):** Public transparency log for attestation issuance (CT model). Potentially IETF-compatible claim vocabulary in VCs (EAT model). Developer-first adoption playbook (Stripe/Twilio model) — great documentation, usage-based pricing, free tier.

### What the Orchestrator Needs to Know

1. **Substrate is architecturally a TLS Certificate Authority for behavioral trust.** This is the most precise technical analogy: Substrate's on-device daemon is the client; the attestation server is the CA; brands are the browsers; behavioral trust score is the certificate. Everything maps. The DMARC analogy explains the enforcement model. Use both.

2. **The biggest architectural risk is not topology — it's the cold start / trust anchor problem.** Who decides to trust Substrate's root signing key? In TLS, browser vendors make that decision. Substrate needs an equivalent governance layer. This is a business and ecosystem problem, not a technical one. Without it, the brand API business doesn't work.

3. **PGP is the cautionary tale.** Web of Trust failed because it asked too much of ordinary people, had no forward secrecy, and required human key signing parties that never achieved critical mass. Substrate must not replicate PGP's failure modes: it must be invisible to operate (agents register automatically), the UX must require nothing of device owners, and trust must accumulate passively.

4. **ActivityPub's failure modes are Substrate's design checklist.** Each failure mode maps to a Substrate architectural decision already made or pending:
   - Identity loss on server failure → on-device storage means agents own their history
   - Economic sustainability → Substrate's revenue model (API fees, subscriptions) creates sustainability incentives
   - Defederation as only enforcement → "always aware, never acting" means Substrate never needs defederation
   - Centralization by default → thin coordination server, not a host for user data

5. **The IETF space is moving fast and Substrate is ahead of it.** The six active IETF drafts on agent identity (2025-2026) are defining requirements, not solutions. They all acknowledge the behavioral trust gap. Substrate has a working prototype while IETF has working drafts. First-mover with a working implementation is a meaningful position.

6. **MCP is the right integration surface, and the November 2025 spec upgrade makes it more so.** MCP servers are now OAuth Resource Servers. Substrate can issue OAuth 2.1-compatible tokens as part of its trust attestation. Agents querying Substrate over MCP naturally get trust-checked as part of the protocol handshake. The integration surfaces align.

---

*Research conducted 2026-03-11. All web sources accessed on this date. IETF drafts cited by draft name are active unless noted as expired.*
