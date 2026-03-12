# Validation Report: Protocol Architecture — CLUSTER C
## Date: 2026-03-11
## Validator Focus: Architecture model validity (C1–C4)

---

### Evidence Challenges

**C2 — Tailscale split-plane analogy is oversimplified and partially misleading.**

Team 1 characterizes the Tailscale control plane as "thin" and implies it is essentially just a signing key plus policy distribution. This understates what Tailscale's coordination server actually does. Per Tailscale's own documentation, the control plane: (1) manages and distributes security policies ("your company's security policy is stored on the Tailscale coordination server, all in one place, and automatically distributed to each node"), (2) integrates with OAuth2/OIDC/SAML identity providers for authentication and access control decisions, (3) operates DERP relay servers for networks that block UDP, and (4) provides audit logging for compliance. The control plane is essential for ongoing orchestration and governance — not merely for bootstrapping key exchange.

Team 1's report describes the coordination server in several places as essentially "a signing key." This is reductive. Tailscale itself runs a multi-server, always-on infrastructure service with identity provider integrations. When Team 1 maps this to Submantle and states "a thin Submantle coordination server" needs only to handle "agent registration, credential issuance, and trust score attestation," they are glossing over the full operational surface that their own reference architecture actually requires.

The analogy is directionally useful — the conceptual split between on-device computation and off-device coordination is sound — but it should not be used to justify a "minimal infrastructure" claim, and describing the control plane as merely a "signing key" will mislead anyone who reads it.

**C3 — CT gossip protocol is not standardized, not in production, and is a poor reference for trust score propagation.**

This is the weakest claim in Cluster C. The Certificate Transparency gossip protocol was never standardized. RFC 6962 explicitly deferred gossip to "a separate document" and called for "a variety of gossip mechanisms to emerge." The IETF trans working group draft (draft-ietf-trans-gossip-05) was filed as "Expired (IESG: Dead)" — last updated January 2018, formally archived by February 2020. No RFC was ever published from this work.

CT v2 (RFC 9162), which superseded RFC 6962, also explicitly excludes gossip: it acknowledges that a misbehaving log could serve different views to different clients, then states that solutions to this problem are "outside the scope of this document." CT gossip was not standardized in v1 or v2.

Furthermore, the broader CT ecosystem has moved away from gossip entirely. Sigstore's Rekor (the closest production transparency log for signing events) is migrating to tile-based logs (Trillian-Tessera) in its v2 redesign — not gossip-based cross-log consistency.

Team 1 cites CT gossip as a "battle-tested" pattern for "distributed verification without centralization." It is not. It is an abandoned IETF draft for a narrow certificate audit problem that was never deployed at scale. Applying it to trust score propagation is a doubly-stretched analogy: once because the gossip spec never shipped, and again because trust score distribution is a meaningfully different problem from certificate log cross-consistency.

**C4 — "Signing key + HTTPS endpoint + daemon" materially understates the minimum viable infrastructure.**

The report's own Section 6 (Gaps and Unknowns) acknowledges: "The thin coordination server [...] holds the signing key for all Submantle trust attestations. If that key is compromised, all issued credentials are suspect. Key management for an attestation service is non-trivial — HSMs, key rotation, split custody." This self-contradiction is significant: the report names a minimum that it simultaneously identifies as under-analyzed and potentially catastrophic if wrong.

OWASP key management standards require for a production signing service: a FIPS 140-2/140-3 compliant cryptographic module, an HSM for key storage (hardware cryptographic modules are explicitly preferred over software), access controls with accountability tracking, and a compromise-recovery plan including re-key procedures. The Sigstore project — a production signing and transparency infrastructure solving a comparable problem — requires three distinct components (Cosign, Fulcio, Rekor) plus a 24/7 on-call rotation and a 99.5% SLO on core endpoints.

For Submantle specifically, the infrastructure not named in C4 includes: the revocation endpoint (Bitstring Status List, CDN-delivered), a database for tracking issued credential indices and revocation status, rate limiting and anti-gaming logic for attestation requests, monitoring and alerting for the signing service, and the agent registration database. None of these are the signing key or the HTTPS endpoint — they are the surrounding operational infrastructure without which the signing key and endpoint are not "viable."

C4 is not wrong about the logical minimum components. The problem is the word "minimum viable," which implies operational readiness that the three named components alone do not provide.

---

### Verified Claims

**C1 — RATS RFC 9334 exists and the Passport Model maps accurately to Submantle's architecture.**

RFC 9334 was published by the IETF in January 2023 as an informational document. The three roles (Attester, Verifier, Relying Party) exist exactly as described. The Passport Model is defined as: the Attester obtains an Attestation Result from the Verifier, then presents it directly to Relying Parties who apply their own appraisal policy. The agent carries the credential and presents it anywhere — this maps precisely to Submantle's W3C VC model where an on-device daemon generates evidence, Submantle's attestation server signs and issues a VC, and brands validate it locally without calling back to Submantle.

RFC 9334 also explicitly addresses freshness (via synchronized timestamps, nonces, and epoch markers), which confirms that the re-attestation concern Team 1 flags in Section 6 is architecturally grounded and has standard vocabulary. This claim holds up in full.

One nuance worth noting: RFC 9334 is classified as "Informational," not a protocol standard. It defines vocabulary and conceptual models, not a wire protocol. Submantle can correctly cite it as the architectural framework, but should not imply it specifies an implementable protocol that other systems will already speak.

**C2 (partial) — The conceptual split between on-device computation and off-device coordination is the correct model.**

Despite the oversimplification noted above, the core architectural insight is valid: separating trust computation (on-device) from attestation issuance (server-side) is the right structural approach for Submantle's privacy-by-architecture constraint, and Tailscale demonstrates this pattern works at production scale. The claim that actual data flows never touch the coordination server is accurate — Tailscale's coordination server handles only key distribution and policy, not actual traffic. Applying this to Submantle (behavioral data never leaves the device; only the signed attestation result crosses to the server) is a sound analogy. The problem is exclusively with the characterization of the control plane as operationally "thin" or reducible to "a signing key."

**C4 (partial) — The three logical components are correctly identified.**

A signing key, an HTTPS endpoint, and an on-device daemon are the three correct logical primitives. The claim is accurate as a description of Submantle's architectural structure. The challenge is only with framing these three primitives as "minimum viable" when operational readiness requires substantially more.

---

### Missing Angles

**Sigstore as the correct production reference — not CT gossip.**

Team 1 proposes CT gossip as a novel approach for Submantle's attestation audit layer. The better reference is Sigstore, which Team 1 does not mention. Sigstore's Rekor is a deployed, maintained, immutable transparency log for software signing events with a public API, SLO targets, and Linux Foundation governance. Rekor solves the same "who watches the watchman" problem for a signing authority that Team 1 wants CT gossip to solve for Submantle. If Submantle ever builds a transparency log for attestation issuance, Rekor's architecture (or Trillian-Tessera, its v2 backend) is the reference to study. CT gossip is an abandoned draft; Rekor is a running system.

**ACME / Let's Encrypt as a reference for attestation service design.**

Team 1 mentions Let's Encrypt in the context of HTTPS adoption statistics but does not analyze ACME (RFC 8555) as an architectural reference for Submantle's attestation service. ACME defines a protocol for automated certificate issuance from a CA, including account registration, domain validation challenges, and certificate lifecycle management. The ACME model is structurally closer to Submantle's agent registration and attestation issuance flow than TLS itself is. Let's Encrypt's operational experience with rate limits, abuse prevention, CT integration, and key rotation is directly applicable to Submantle's attestation service design.

**The RATS Background-Check Model deserves acknowledgment for the brand API use case.**

Team 1 recommends the Passport Model exclusively, but RFC 9334 defines the Background-Check Model for a reason: when a Relying Party needs fresh, non-cached attestation (e.g., a high-stakes financial transaction), the Passport Model's credential staleness problem is significant. Submantle's brand API — where a brand queries Submantle in real-time for a trust score before permitting an agent to transact — is arguably a Background-Check Model interaction, not a Passport Model interaction. The report presents both RATS models and correctly selects Passport for the agent-carries-credential flow, but does not acknowledge that the brand query API may require Background-Check semantics. Both models may coexist in Submantle's final architecture, and this distinction should be explicit.

**Notary v2 (CNCF) as a minimum-viable signing reference.**

The report does not address Notary v2, which is a CNCF production signing infrastructure for container images with explicit design guidance for minimum viable deployment. Notary v2's reference implementation (notation-go) demonstrates what a signing service requires at operational minimum, with explicit key management tiers (local file system, cloud KMS, HSM). This is directly useful for scoping Submantle's V1 signing service before the operational requirements are under-estimated by a "signing key + endpoint" framing.

---

### Overall Assessment

Cluster C's most important claim — C1, that RATS RFC 9334 Passport Model precisely names Submantle's architecture — is verified and accurate. RFC 9334 provides stable, IETF-standard vocabulary for what Submantle is building, which is a genuine contribution: "Attester, Verifier, Relying Party" is more credible in standards-body and enterprise contexts than custom framing. The Tailscale split-plane analogy (C2) is directionally correct as a conceptual model but is presented with more operational precision than it deserves — the control plane is meaningfully more complex than the report implies, and describing it as a "signing key" in multiple places will mislead anyone who uses these findings to plan actual infrastructure. The CT gossip reference (C3) does not hold: the CT gossip protocol was abandoned by IETF, never deployed, and CT v2 explicitly excludes it; Sigstore/Rekor is the production equivalent Team 1 should have cited. The minimum viable infrastructure claim (C4) correctly names the three logical components but the framing as "minimum viable" is unjustified given the key management, revocation, and operational infrastructure the report itself acknowledges is required but not analyzed. The most actionable correction for the orchestrator: replace the CT gossip reference with Sigstore/Rekor, qualify the Tailscale analogy explicitly as a conceptual model rather than an operational blueprint, and treat C4 as a three-component architectural description rather than an infrastructure sizing claim.

---

*Validation complete: 2026-03-11*
*Validator: Architecture Model Validity — Cluster C only*

---

## PRIOR CONTENT — Validation Report: Validator 3 (Original)
## Original Focus: Product-first vs. protocol-first path; founder usability as a compass; standards body realism for AAIF

---

## Order of Analysis

Per the Divergence-First Protocol: challenges and gaps before confirmations. Everything that doesn't hold up comes first.

---

## 1. Evidence Challenges

### 1.1 The MCP Go SDK "jointly maintained by Anthropic and Google" claim requires scrutiny

Team 2 states the Go SDK (v1.4.0) is "co-maintained by Anthropic and Google" and uses this as a confidence anchor throughout. This specific claim is not independently verifiable from the sources provided, and the framing deserves skepticism. The Go SDK being hosted at `github.com/modelcontextprotocol/go-sdk` with contributions from both companies' engineers is plausible, but "jointly maintained" implies ongoing shared ownership obligations — a governance commitment rather than a code contribution. The distinction matters: if one company reduces its contribution, the "co-maintained" framing collapses and the SDK's stability claim weakens. The cited source is the GitHub repo itself; no governance agreement or co-maintenance SLA is cited. Confidence in the Go SDK's production-readiness should be moderate, not high.

### 1.2 The 97M monthly SDK downloads figure is unverified in the findings

This number appears in the Research Brief (carried in from prior research), in Team 2, and in Team 4. No team in this expedition re-verified this specific figure with a fresh source fetch. Team 4 cites a 2026-03-11 article about MCP's one-year review. Team 2 cites modelcontextprotocol.io/docs/sdk. Neither provides the specific 97M figure with a verifiable timestamp. This is a high-profile number used to justify MCP as "the dominant integration surface" — it should have been independently confirmed.

### 1.3 Team 3's Stripe "Five Levels of Agentic Commerce" provenance is thin

Team 3 cites `johndschultz.com/thoughts/five-levels-of-agentic-commerce/` and `businessengineer.ai/p/the-five-levels-of-agentic-commerce` as sources for the Five Levels framework — these are third-party blog aggregators, not Stripe's primary source. The Stripe primary URL cited (`stripe.com/blog/three-agentic-commerce-trends-nrf-2026`) is about NRF trends, and may contain different framing than the Five Levels model that Team 3 presents in detail. This is a significant rhetorical centerpiece — the "trust cliff" framing that anchors Submantle's insertion point narrative. The difference between "Stripe said this" and "a blogger summarized Stripe using these five levels" is material for a founder pitching to Stripe or referencing Stripe publicly.

### 1.4 ERC-8004 adoption numbers may be speculative

Team 3 states "24K+ agents registered in first two weeks" for ERC-8004 (live January 29, 2026). The source cited is `eips.ethereum.org/EIPS/eip-8004`. EIP pages do not typically contain adoption metrics — they contain the specification. This number almost certainly came from a press release, blog post, or third-party tracker, not the EIP document itself. The number may be accurate, but the cited source cannot contain it. The evidence provenance is misattributed.

### 1.5 HUMAN Security AgenticTrust "per-site only" claim is asserted, not proven by source inspection

Both Team 3 and Team 5 characterize HUMAN AgenticTrust as "per-site only, not portable." The cited sources are `humansecurity.com/applications/agentic-ai/` and `humansecurity.com/newsroom/first-adaptive-trust-layer`. HUMAN is a well-funded company ($190M+ raised) that may have cross-site aggregation products not described on the marketing pages. The "per-site" limitation is structurally plausible and likely correct, but it's based on reading marketing copy, not architecture documentation or direct confirmation from HUMAN. This is a major competitive claim that Submantle's narrative depends on — if HUMAN has cross-site behavioral history for agents that the teams missed, the competitive gap analysis is wrong.

### 1.6 Team 1's Tailscale node count is imprecise

Team 1 states Tailscale has "millions of nodes in production (2025)" with no specific number and cites Tailscale's technical blog. This is a rough order-of-magnitude estimate, not a sourced figure. It's used to validate that the split control/data plane architecture works at scale. The architectural argument is sound regardless of whether Tailscale has 2M or 20M nodes, but the imprecision is worth noting.

---

## 2. Contradictions Between Teams

### 2.1 Team 3 and Team 4 give contradictory signals about AAIF and behavioral trust standards

Team 3 states: "The AAIF's scope as of March 2026 is protocol stewardship (MCP, goose, AGENTS.md), not trust infrastructure. No working groups found addressing behavioral trust." This is a factual finding based on direct research.

Team 4 recommends: "Submantle as the behavioral trust layer for the MCP ecosystem is a narrow, specific, achievable beachhead... The Agentic AI Foundation (Linux Foundation, co-founded by Anthropic/OpenAI/Block) governs MCP... contributing a behavioral trust specification to AAIF would place Submantle inside the canonical agent infrastructure stack."

These two positions are not reconciled. If AAIF's scope is confirmed to exclude behavioral trust, Team 4's Phase 2 recommendation of AAIF as the beachhead governance path requires an active effort to expand AAIF's scope — which is a very different proposition than joining an existing trust working group. Team 4's synthesis treats the AAIF path as accessible and natural; Team 3's evidence suggests it is neither obvious nor confirmed. Neither team synthesizes this tension for the founder.

### 2.2 Team 2 and Team 4 contradict on the build-order priority of MCP

Team 2 recommends: "Phase 1 (Immediate): Wrap existing FastAPI REST routes as MCP Tools via Python MCP SDK. Enables MCP clients to reach Submantle within one session — no Go migration required."

Team 4 recommends: "Phase 1 (current → first public release): Write a protocol specification, but ship the reference implementation at the same time."

These are not mutually exclusive, but Team 2's Phase 1 is a three-day engineering task. Team 4's Phase 1 includes writing a spec and is framed as the multi-week public launch sequence. If a founder reads both, they get two different "what to do next" answers. Neither acknowledges the other team's phasing.

### 2.3 Team 1 and Team 5 treat did:web differently for on-device agents

Team 1 recommends did:web as the agent identity mechanism without detailing the DNS dependency risk for on-device agents.

Team 5 explicitly surfaces the problem: "For production on-device agents, the domain anchoring problem is real — Submantle agents on a device without an externally reachable domain cannot publish a did:web that external verifiers can resolve." Team 5 proposes a two-tier model (did:key for local, did:web for external) and notes that Submantle could optionally host agent DIDs.

Team 1's synthesis omits this problem entirely. A founder reading only Team 1 would conclude did:web is unambiguously recommended. A founder reading both would discover the limitation only by going to Team 5. The contradiction is not irreconcilable — Team 5 resolves it — but it's a gap in Team 1's completeness.

---

## 3. Alignment Drift — The Central Finding of This Validation

**The Research Brief's expected outcome:** "A clear architectural blueprint that answers: What IS Submantle technically? How do agents connect? How does it grow with AI? Who else is building adjacent infrastructure? How did other protocols go from idea to global adoption? — all explained so a non-technical founder can use it as a compass to keep the project on course."

**The actual deliverable across five teams:** Technically rigorous, deeply sourced research findings written for a technical audience, with synthesis sections that make architectural recommendations — but whose plain-language translation remains incomplete.

This is the most serious gap in the expedition.

### 3.1 The compass problem: the findings are a map, not a compass

The Brief explicitly says "a non-technical founder can use it as a compass." A compass gives you a direction when you're lost. A map shows you the terrain. These findings are an excellent map. They are not a compass.

Specific examples:

- Team 1 provides an excellent split-plane architectural model but never says in plain terms: "Submantle is like a notary office. Your device computes the trust score. The notary office stamps and signs it. Brands check the stamp. The notary office never sees your behavior." The RATS RFC vocabulary (Attester, Verifier, Relying Party) is introduced in section 8.1 but not simplified for a founder who cannot code.

- Team 4 provides a 500-line document with eight protocol case studies, eight failure case studies, eight adoption patterns, five gaps, and a four-phase path. The "Synthesis" section is titled "The Realistic Path for Submantle" but requires reading 400 lines of prior content to be meaningful. The founder asked: "How did other protocols go from idea to global adoption?" Team 4 answers the question comprehensively for a reader with weeks to absorb it. Not as a compass.

- Team 5's "Synthesis" section provides a four-layer architecture table. Useful to a Go engineer planning implementation. Not directly usable by a founder as a daily directional check.

The closest thing to a compass in the findings is Team 1's analogy in Section 7: "Submantle is a Tailscale-for-trust." That single sentence is more usable by a non-technical founder than the next 50 paragraphs. The expedition generated the raw material for a compass but did not assemble one.

### 3.2 Protocol-first drift: the findings lean heavily toward protocol destiny

The Research Brief asks about Submantle's path from prototype to protocol. Every team answered as if the protocol destination is already decided. This may be correct — but the Brief's phrasing is a question, not a premise.

Team 4 is the most explicit about this drift: it says Submantle should plan for "3–5 years to critical mass" and recommends ISRG (nonprofit governance) as the structural model. These are protocol-phase planning assumptions. But the founder's immediate question may have been simpler: "What do I need to decide and do next to keep moving in the right direction?"

The findings answer the question "What does Submantle need to become a global protocol?" rather than "What is the next decision the founder needs to make and why?" These are related but not the same.

Teams 2 and 4's build-order recommendations come closest to answering the simpler version. Team 2's Phase 1 (wrap existing FastAPI in MCP) and Team 4's Phase 1/2/3 path are actionable. But they arrive after 300+ lines of context a non-technical founder has to work through.

### 3.3 The incident taxonomy gap is unaddressed as a blocker

The Research Brief acknowledges the incident taxonomy is the "#1 blocking design decision." Every team treats this as already-resolved background information and moves past it. None of the five teams addresses it — not its product definition, not how its absence affects each team's recommendations, not what a minimum viable incident taxonomy would look like.

This matters because:

- Team 1's attestation freshness interval ("how often should Submantle re-issue trust VCs?") depends on how fast scores change — which depends on incident taxonomy. Team 1 explicitly flags this as "blocked."
- Team 3's behavioral trust layer (Layer 3 in their stack) has no examples of what counts as an incident in an agent transaction.
- Team 4's adoption path describes how to get brands to query Submantle trust scores — but brands making enforcement decisions need to know what incidents are.

The incident taxonomy is the founder's product decision that unlocks all five teams' recommendations. None of them say this clearly. A founder using these findings as a compass would not know that one product decision they need to make is the keystone.

---

## 4. Missing Angles

### 4.1 The multi-device trust score federation problem is raised but not resolved

Team 1 flags it in Section 6: "If an agent operates on device A and then on device B, and scores are computed locally, how do scores merge or federate across devices?" This is architecturally fundamental — if trust scores are on-device and an agent operates across devices, either (a) scores don't federate and an agent loses trust history when switching devices, or (b) some synchronization happens and the "on-device" privacy claim is complicated.

No team resolves this. Team 5 does not address it. Team 3's insertion point analysis assumes scores are portable — but says nothing about how portability works when the score is computed on the device where the agent registered.

This is a gap in the blueprint, not just a gap in the research.

### 4.2 The attestation server key management threat model is mentioned but not explored

Team 1 (Section 6, item 4) raises the concern: "The thin coordination server [...] holds the signing key for all Submantle trust attestations. If that key is compromised, all issued credentials are suspect." This is a catastrophic risk — not a nuance. Key management for a signing authority requires hardware security modules, key rotation, split custody, or equivalent controls.

None of the five teams addresses this in depth. Team 5 briefly mentions "Submantle generates and manages keys; developers never touch raw key material" — but from the agent side, not the attestation server side. A solo founder building this alone would not know that the attestation server's key security is a critical path item that requires specialized expertise they may not have.

### 4.3 No team tested whether "always aware, never acting" and protocol commercialization are compatible

The Research Brief constraint says Submantle never enforces. All five teams respect this constraint. But none of them examines whether the business model depends on outcomes that require Submantle to be perceived as an enforcer.

Specifically: Team 4's Pattern 4 asks "who is Submantle's Chrome?" — meaning, who makes the absence of Submantle feel like a liability? The answer the research implies is: a marketplace or platform that requires Submantle trust scores. But that third party enforcing Submantle scores creates an economic dynamic where Submantle's commercial success depends on enforcement happening — even though Submantle never enforces. This is the Visa model, and it works for Visa. But no team examines whether agents or developers would resist Submantle if its scores are used punitively by platforms — and whether that resistance would undermine adoption.

### 4.4 No team examines the Guiding Light credential gap

Team 4 acknowledges in its Gap 2: "All of the protocol founders studied had institutional affiliations [...] OR were recognized technical contributors in their domain before creating the protocol [...] Submantle's founder is a solo non-technical creator using AI-assisted development. The credibility path is different." This is a courageous observation. But Team 4 then says "it comes from the working reference implementation, from the precision of the behavioral trust design, and from recruiting a technical co-author for the attestation format specification" — without examining whether any of these are realistic steps for this specific founder.

The "technical co-author" recommendation is particularly significant. If Submantle needs a technical co-author to achieve credibility with institutions like IETF or AAIF, that is a meaningful hiring/recruiting task that requires the founder to evaluate the recommendation as a personal next action — not just as a category of thing that would help. No team addresses how a non-technical founder recruits a technical co-author for a trust protocol specification.

---

## 5. Agreements — High-Confidence Convergence

These findings converged across multiple teams independently. This is the high-confidence zone.

### 5.1 MCP is the right integration surface — confirmed from all angles

Team 1 (protocol architecture), Team 2 (integration surface), Team 3 (agent economy), and Team 4 (adoption playbook) all independently reach the same conclusion: MCP is the correct primary integration surface. Team 1 arrives at it from protocol structure analysis. Team 2 arrives at it from framework compatibility research. Team 3 arrives at it from market infrastructure mapping. Team 4 arrives at it from protocol adoption pattern analysis.

Four independent angles, same conclusion. This is the strongest finding of the expedition.

### 5.2 The behavioral trust gap is real and unoccupied at the OS/portable layer

Team 3 (comprehensive market survey), Team 4 (competitive landscape), and Team 5 (DID ecosystem survey) all confirm independently: no production player offers portable, cross-platform behavioral trust scored from OS-level observation. The Forrester BATMS category (Team 3: 19 vendors) is per-site. ERC-8004 (Team 3, Team 5) is feedback-based, not runtime observation. HUMAN AgenticTrust (Teams 3, 5) is web-layer only.

Three independent research angles, consistent finding.

### 5.3 W3C VC 2.0 + SD-JWT is the correct attestation format

Teams 1, 2, and 5 all validate this. Team 5 does the deepest technical verification (RFC 9901 Internet Standard, go-sd-jwt v1.4.0 stable library, EU Digital Identity Wallet alignment). Team 1 validates it against the RATS RFC architectural model. Team 2 validates it against MCP's OAuth-compatible bearer token model. This settled decision is confirmed from three angles.

### 5.4 The "always aware, never acting" principle has a proven structural precedent

Team 1 identifies DKIM/DMARC as the direct internet-scale proof that "signal without enforcement" works at infrastructure scale. This is valuable: the principle was previously stated as a design choice; it now has 30 years of infrastructure precedent behind it. Teams 3 and 4 independently validate it via the Visa analogy. The principle is architecturally sound and historically proven.

### 5.5 Blockchain dependency is correctly rejected

Teams 1, 3, and 5 all confirm that blockchain-dependent architectures (did:ion, did:ethr, ERC-8004 as a Submantle pattern) are wrong for Submantle's constraints. Multiple specific reasons converge: no production Go libraries, operational complexity, constraint violation, privacy misalignment. Team 5's assessment of did:ion as "maintenance mode, not production recommended" is directly sourced from GitHub.

---

## 6. Surprises

### 6.1 The RATS RFC (RFC 9334) names exactly what Submantle is — this has not been in prior research

Team 1's Section 8.1 introduces the IETF RATS architecture (Remote ATtestation ProcedureS) and maps Submantle's three components directly to RATS roles: Attester (on-device daemon), Verifier (attestation server), Relying Party (brands/platforms). This is not a metaphor — it is a published Internet Standard (RFC 9334) that formally defines the architecture Submantle is implementing.

This is significant for two reasons: (1) Submantle can now describe itself using IETF-standard vocabulary, which matters for standards body engagement and enterprise credibility; (2) the "Passport Model" vs. "Background-Check Model" distinction in RATS is the technical name for the architectural choice Submantle has already made (agents carry credentials; brands validate locally). The finding validates prior decisions with formal standards vocabulary that prior expeditions did not surface.

### 6.2 Submantle's on-device computation is a Sybil resistance mechanism — this has not been stated this clearly before

Team 4 (citing the November 2025 inter-agent trust academic paper) notes: "Submantle's on-device computation specifically addresses [Sybil attacks] — local trust computation is a novel architectural defense against distributed Sybil attacks." This reframes an architectural privacy decision as a security property. Prior expeditions noted "Sybil resistance by locality" but framed it as a secondary benefit. Team 4 and the cited academic paper frame it as a primary architectural advantage that other trust systems lack. This is a competitive differentiation that is not obvious from reading the codebase or prior expedition documents.

### 6.3 TRQP v2.0 could make Submantle the first behavioral trust registry in a standards-compliant ecosystem

Team 5's Part 8 proposes implementing a TRQP v2.0-compatible interface on top of Submantle's trust scores. This would make Submantle a trust registry that answers behavioral questions — something no existing TRQP-aware system does. TRQP is currently finalizing (Public Review 02, December 2025). Team 5 rates this MEDIUM confidence, which is the appropriate level. But the strategic opportunity — being the first behavioral trust registry in the TRQP ecosystem, immediately discoverable by cheqd-integrated systems — is genuinely novel and has not appeared in prior expeditions.

---

## 7. The Compass Problem — Summary Judgment

The Research Brief asked for findings "explained so a non-technical founder can use it as a compass." This is the test the expedition should have been optimizing for. On that test, the collective output is: **excellent raw material, incomplete compass.**

If the synthesizing orchestrator takes one action based on this validation, it should be: translate the five teams' convergent findings into the plain-language compass the Brief requested. The materials are all here. The convergence is real. What is missing is the final distillation into a directional statement a founder can hold in working memory.

The three sentences that should be at the front of any synthesis:

1. "Submantle is a notary service for agent behavior: your device computes the trust score; Submantle's server stamps and signs it into a portable credential; brands check the stamp locally without calling Submantle back." (This is what Team 1's RATS model means in plain English.)

2. "Build the MCP server first, because MCP is the language every major AI system speaks, and making Submantle one MCP call away is the difference between Submantle being theoretical and Submantle being used." (This is what Teams 2 and 4 converge on.)

3. "Before Submantle can be trusted by brands, two product decisions have to be made: what counts as an incident, and who is the first institutional co-signer." (This is what Teams 1, 3, and 4 all flag as blockers but don't state as a two-item list.)

### On AAIF specifically (Special Focus)

Team 4 says AAIF is the natural standards venue. Team 3 says AAIF has no behavioral trust working groups and no evidence of that being on the roadmap. Both are right. The synthesis needed is: AAIF is the right *long-term* venue, but it requires Submantle to first demonstrate adoption in the MCP ecosystem that AAIF governs, then propose a behavioral trust working group from a position of demonstrated usage. This is a 2-3 year path from current state, not a near-term step. Presenting it as "the natural venue" without the timeline and the prerequisite (demonstrated MCP adoption) gives a founder a misleading sense of access.

### On solo founder credibility

Team 4 is honest about the credential gap but does not give the founder actionable next steps for addressing it. The gap between "recruit a technical co-author" (the recommendation) and "how does a non-technical solo founder find and attract a security-credentialed co-author for an unpublished trust protocol specification" (the real question) is left entirely open.

---

## Validation Summary

| Team | Evidence Quality | Alignment with Brief | Compass Value |
|------|-----------------|----------------------|---------------|
| Team 1 | High — 12+ searches, multiple source fetches, RATS RFC is genuinely novel | Good — covers protocol architecture | Medium — technical depth exceeds founder accessibility |
| Team 2 | High — MCP specs directly fetched, version numbers verified, Go SDK confirmed | Excellent — directly answers "how do agents connect?" | High — Phase 1-5 build order is actionable |
| Team 3 | High — comprehensive market survey, multiple primary sources | Excellent — answers "who else is building adjacent infrastructure?" | Medium — stack diagram is excellent; synthesis requires prior context |
| Team 4 | High — eight case studies, multiple source verifications | Good — covers adoption playbook | Medium — comprehensive but dense; compass value is buried |
| Team 5 | High — pkg.go.dev and GitHub directly checked, RFC datatracker confirmed | Good — covers decentralized identity | Medium — excellent for a Go engineer; partial for a non-technical founder |

**Strongest findings:** MCP as integration surface (all teams), behavioral trust gap confirmation (Teams 3, 4, 5), RATS RFC vocabulary (Team 1), TRQP behavioral registry opportunity (Team 5).

**Most important unresolved tensions:** AAIF accessibility (Teams 3 vs. 4), multi-device trust federation (Teams 1, 5), attestation server key management (Team 1), incident taxonomy as the keystone blocker (all teams).

**The gap the orchestrator must close:** A plain-language synthesis that a non-technical founder can hold as a compass — not just a technically excellent map.

---

*Validation complete: 2026-03-11*
*Validator 3 — Independent validation, no prior involvement in this expedition's research teams*
