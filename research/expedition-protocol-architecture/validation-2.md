# Validation Report — Validator 2
## Date: 2026-03-11
## Expedition: Protocol Architecture
## Special Focus: Team 1 Tailscale feasibility / Team 3 economy completeness / Team 5 Go library assessment

---

## Preamble: What I Verified

Read all five team findings in full. Conducted external verification on the following claims via WebFetch:

- `pkg.go.dev/github.com/MichaelFraser99/go-sd-jwt` — current version, RFC compliance, competitor landscape
- `pkg.go.dev/search?q=sd-jwt&m=package` — full Go SD-JWT ecosystem scan
- `github.com/MichaelFraser99/go-sd-jwt/releases/tag/v1.4.0` — release notes for RFC alignment
- `datatracker.ietf.org/doc/rfc9901/` — RFC 9901 status and relationship to draft
- `tailscale.com/blog/how-tailscale-works` — Tailscale architecture
- `eips.ethereum.org/EIPS/eip-8004` — ERC-8004 actual status
- `dev.to/zarq-ai/state-of-ai-assets-q1-2026` — ZARQ census (returned 404)
- `clawtrust.io` — ClawTrust status
- `trustoverip.github.io/tswg-trust-registry-protocol/` — TRQP v2.0 status

---

## Section 1: Evidence Challenges

### Challenge 1 — Team 5 (and Team 1 echo): go-sd-jwt v1.4.0 may not implement RFC 9901

**Claim:** Team 5 states that go-sd-jwt v1.4.0 "reached major version v1 — considered stable" and implements the SD-JWT specification. Team 5 also adds: "The note that go-sd-jwt's docs reference the draft URL is worth watching — verify in the library source that the RFC 9901 serialization format is implemented correctly before production use." Team 1 section 8.3 confirms SD-JWT as RFC 9901 but does not independently verify the library.

**What I found:** External verification confirms the documentation issue Team 5 flagged is substantive. The go-sd-jwt v1.4.0 release notes (August 30, 2025) contain no mention of RFC 9901. The README explicitly links to `datatracker.ietf.org/doc/draft-ietf-oauth-selective-disclosure-jwt/` — the draft path, not the RFC 9901 path. This matters because RFC 9901 was published November 2025, three months after v1.4.0. The library was written against a draft and has not published a release explicitly claiming RFC 9901 conformance.

**Severity:** Moderate. RFC 9901 evolved from that draft, so the serialization format is likely compatible (the RFC process rarely makes breaking format changes this late). But Team 5's recommendation to "verify in the library source" before production use is correct and should be stronger: this is an unverified compatibility assumption, not a confirmed fact. Both teams presented it as confirmed. It is not. The validation recommendation stands: do not ship Submantle's attestation layer against go-sd-jwt v1.4.0 without running the RFC 9901 test vectors against it first.

**Verdict:** Team 5 correctly flagged the risk but underweighted it. Teams should not have described this library as implementing RFC 9901 without verification.

---

### Challenge 2 — Team 3: ERC-8004 is NOT live on mainnet and the 24K registration claim is unverifiable

**Claim:** Team 3 states "ERC-8004: Ethereum standard (live mainnet January 29, 2026). Three registries: Identity Registry, Reputation Registry, Validation Registry. Reputation Registry records feedback tied to payment proofs. 24K+ agents registered in first two weeks."

**What I found:** Direct verification of `eips.ethereum.org/EIPS/eip-8004` shows:

1. ERC-8004 is in **Draft** status as of verification date. It is a Standards Track ERC proposal created August 13, 2025. It is not a finalized standard.
2. The EIP page contains no information about mainnet deployment, no deployment addresses, and no registration counts.
3. The "24K+ agents registered in first two weeks" claim is not traceable to the EIP page or any source cited by Team 3 (the source cited is the EIP itself).

**Severity:** High for this specific claim. The 24K registration figure and the "live mainnet January 29, 2026" framing appear to conflate the ERC proposal with a specific smart contract deployment that may or may not exist. Ethereum has many ERC-compliant contracts that may implement EIP-8004-like patterns without being the canonical EIP-8004 deployment. The claim may be derived from a specific project's contract rather than an official standard deployment. Team 3 presents this as settled fact with no hedge.

**Impact on findings:** The broader point Team 3 makes — that on-chain agent reputation exists and validates market demand — remains plausible even if the specific numbers are wrong. But citing a Draft EIP as a "live mainnet standard" is a material misrepresentation.

**Verdict:** Team 3 should have clearly labeled ERC-8004 as a draft proposal and been explicit that any deployment figures come from a specific project, not an officially adopted standard.

---

### Challenge 3 — Team 3: ZARQ census source returned 404

**Claim:** Team 3 cites `dev.to/zarq-ai/state-of-ai-assets-q1-2026` as the source for "143K agents, 17K MCP servers, all trust scored" in Q1 2026.

**What I found:** This URL returned HTTP 404 during verification. The source does not exist at the cited address as of 2026-03-11.

**Severity:** Moderate. The ZARQ/Nerq rebranding Team 3 mentioned suggests the organization exists, and the census data may be real but the specific URL is broken or wrong. However, a finding that relies on an unverifiable source cannot be cited as evidence. The claim about ZARQ conducting a census with specific numbers is unsupported.

**Verdict:** This specific claim is unsourced as cited. The surrounding characterization of ZARQ as a technical-metrics-only scorer (not behavioral) may be accurate, but the census numbers should be treated as unverified.

---

### Challenge 4 — Team 2: Go SDK version number citation is inconsistent with MCP SDK versioning

**Claim:** Team 2 states "Go SDK: v1.4.0 (Feb 2026), 4.1k stars, 373 forks, 995 dependent projects." They also state this version is "co-maintained by Anthropic and Google."

**What I found:** Team 5 cites go-sd-jwt as also being v1.4.0. This version number coincidence across two different libraries (MCP Go SDK and SD-JWT Go library) is suspicious and worth noting. However, I was unable to directly verify the MCP Go SDK version in the time available. Team 2's claim about "co-maintained by Anthropic and Google" is plausible given MCP's governance structure but the specific "Google" attribution is notable — Google DeepMind adopted MCP but "jointly maintained" is a stronger claim than adoption.

**Severity:** Low. The core finding (MCP Go SDK exists, is production-grade, is the right target for Submantle) is well-evidenced. The specific version number and co-maintenance claim deserve spot verification before being cited in external materials.

---

### Challenge 5 — Team 1: The attestation server's threat model is understated

**Claim:** Team 1 (Section 4, Gap #4) identifies "Minimum viable attestation server footprint" as an unknown: "It holds the signing key for all Submantle trust attestations. If that key is compromised, all issued credentials are suspect. Key management for an attestation service is non-trivial — HSMs, key rotation, split custody."

**Problem:** Team 1 identifies this gap but then proceeds to recommend the Tailscale model without resolving it. The synthesis presents the split-plane architecture as clear and feasible, while the key signing security problem is acknowledged in the gaps section but not weighted in the feasibility assessment. For a solo founder, running an HSM-secured key signing service is not trivial. This is not a minor operational footnote — it is the core security assumption of the entire attestation architecture.

**Severity:** High for feasibility assessment. The architecture is sound in theory. The operational requirements to run it securely are significantly underestimated relative to a solo founder's realistic capabilities.

---

## Section 2: Contradictions

### Contradiction 1 — Teams 1 and 5 on behavioral data attestation integrity

**Team 1** (Section 7, Novel #1, Risk): "What stops a malicious device from lying about its computed trust score? The attestation server can't verify the local computation."

**Team 5** (Synthesis, Layer 2): Presents the attestation architecture without raising this concern at all. The BehavioralAttestation VC schema includes `total_queries`, `total_incidents`, and `trust_score` fields, implying these are trustworthy numbers that the attestation server will sign.

**The contradiction:** Team 1 correctly identifies that the attestation server is signing claims it cannot verify. Team 5 designs a VC schema as though this is a solved problem. Neither team provides a reconciliation.

**Which has stronger evidence:** Team 1's concern is architecturally correct. The attestation server cannot verify that the local daemon computed the trust score honestly. This is not a minor edge case — it is the fundamental integrity assumption of the entire behavioral trust model. If a device can lie about its trust score and get Submantle to sign it, the entire attestation system is gameable from day one.

**Resolution needed:** This is the single most consequential unresolved tension in the five findings combined. It needs to be surfaced explicitly to the orchestrator, not buried in a "Novel Approaches > Risks" paragraph.

---

### Contradiction 2 — Teams 3 and 4 on ERC-8004 / blockchain positioning

**Team 3** presents ERC-8004 as a "Novel Approach" validating market demand for on-chain agent reputation, and does not flag it as a destructive boundary violation.

**Team 4** (Anti-pattern #7) flags "adding ML to the trust formula" as an anti-pattern, but does not separately flag blockchain-dependent architectures even though the research brief's destructive boundaries explicitly state: "Do NOT recommend blockchain-required architectures."

**Resolution:** Neither team recommended ERC-8004 for Submantle's use — Team 3 notes it as market context, not a recommendation. This is not a direct violation. But Team 3's framing of ERC-8004 as a "Novel Approach" with positive positioning ("Confirms market demand for persistent agent reputation. Validates Submantle's 'identity survives model changes' principle") is misleading — it is a blockchain-dependent architecture that Submantle has explicitly ruled out.

---

### Contradiction 3 — Teams 1 and 5 on Go library production readiness

**Team 5** recommends: "Do not depend on any v0.x library for security-critical key management operations in production."

**Team 5** also recommends: "For DID creation/parsing: web5-go is Apache-2.0 and has did:web + did:key. Acceptable for prototype; wait for v1.0 before production commitment. Alternatively, implement a thin did:web layer directly."

**Team 1** (Section 8.3) confirms SD-JWT as RFC 9901 "full Internet Standard" and treats go-sd-jwt as confirmed production-ready.

**The tension:** Team 5 recommends waiting for v1.0 on DID libraries for production, then cites a library (go-sd-jwt) that may not have verified RFC 9901 conformance as the exception. Team 1 treats go-sd-jwt as confirmed production-ready without verification. There is an inconsistency in how the teams applied production-readiness standards across libraries.

---

## Section 3: Alignment Drift

### Drift 1 — Team 1's Tailscale recommendation does not resolve the "solo founder feasibility" question the Brief requires

**The Brief asks:** Which network topology fits a behavioral trust layer given our constraints? What are the tradeoffs?

**Team 1's answer:** The Tailscale split-plane model is correct. Submantle should run a thin attestation server for the control plane and keep computation on-device for the data plane.

**What's missing:** The Brief specifies the project is from a solo founder with a working Python prototype. "Run a thin attestation server" is not examined for solo founder feasibility. Tailscale's coordination server runs on hundreds of machines with a team of engineers. A "thin" version still requires:
- Production HTTPS endpoint with high availability
- Key management for the signing key (HSM or equivalent)
- Zero-downtime deployment capability
- Security incident response capability

Team 1 identifies these concerns in the gaps section but the synthesis does not distinguish between "architecturally correct" and "feasible for a solo founder." The Brief explicitly says findings should be explainable so a non-technical founder can use them as a compass. The feasibility gap is a compass-level problem.

**My verification confirms:** Tailscale's architecture is real and as described. The coordination server operational complexity is accurately described as "simple to deploy" for the client-side. For the server-side (running the coordination server), Tailscale itself operates that as a managed service with a full engineering team. The architectural analogy holds; the operational analogy does not transfer to a solo founder.

---

### Drift 2 — Team 4's adoption playbook identifies a credibility gap it cannot resolve

**The Brief asks:** What's realistic for a solo founder with a protocol?

**Team 4's answer is honest:** "The credibility path is different: it comes from the working reference implementation, from the precision of the behavioral trust design, and from recruiting a technical co-author for the attestation format specification."

**The drift:** Team 4 correctly identifies that all successful solo protocol founders had deep technical credibility (Torvalds, Cohen, Postel) or institutional affiliation (Postel at USC/ISI). The current Submantle founder has neither. Team 4 then recommends recruiting a technical co-author but does not explain how a non-technical solo founder finds and recruits a credible technical co-author for a novel protocol that has no funding. This is the most important question for adoption that the playbook raises and does not answer.

**This is not an evidence failure** — the analysis is honest. It is an alignment drift: the Brief asked for a realistic path; Team 4 identifies a dependency (technical co-author) without a path to meet it.

---

### Drift 3 — Teams 2 and 3 treat the AAIF as a near-term standards pathway without verifying readiness

**Team 3** writes: "Contributing a behavioral trust specification to AAIF would place Submantle inside the canonical agent infrastructure stack." This is presented as a strategic implication with high actionability.

**Team 4** writes: "For Submantle, the logical first co-signer is Anthropic. The Agentic AI Foundation is the institutional home where a behavioral trust standard could live."

**The problem:** Neither team verifies whether AAIF has a mechanism for accepting contributed behavioral trust specifications, or what the current working group charter covers. Team 3 explicitly notes "No working groups found addressing behavioral trust" — which is the most honest part of this finding. The prescription ("contribute a spec") does not follow from the finding ("no working group for this exists").

**This may still be sound strategic advice** — standards bodies can create new working groups — but it is presented as more concrete than the evidence supports.

---

## Section 4: Missing Angles

### Missing Angle 1 — Nobody examined the on-device daemon's resource cost under real load

The Brief specifies "Lightweight first — invisible resource usage." The research brief expected outcome was "a clear architectural blueprint." None of the five teams examined the resource profile of running:
- A persistent on-device daemon in Go
- Continuous process scanning
- SQLite writes on behavioral events
- MCP server (STDIO or HTTP) accepting connections

For Windows (the target device, per project memory), background process resource usage is highly visible to users. No team benchmarked or estimated this. The "lightweight first" constraint is treated as an aspiration, not a verified property of the proposed architecture.

---

### Missing Angle 2 — The incident taxonomy blocking problem received zero architectural treatment

Every team mentions the incident taxonomy as the #1 unresolved design decision. No team proposed how the protocol architecture should be structured so it can accept a future incident taxonomy without being redesigned. This is a significant architectural gap: if the incident taxonomy changes after the protocol is deployed, how do verifiers with cached credentials handle the change? What's the migration path?

Team 1 mentions attestation freshness as an unknown (Gap #1). Team 2 mentions Elicitation as a channel for incident confirmation. But no team designed the protocol layer around the reality that incident taxonomy is undefined — they all designed as if it will be defined before deployment.

---

### Missing Angle 3 — The multi-device trust score federation problem is identified but not resolved

Team 1 (Gap #2) identifies it: "If an agent operates on device A and then on device B, and scores are computed locally, how do scores merge or federate across devices?"

Team 1 (Section 8.6) proposes CRDTs as a potential answer.

No other team addresses this. The CRDT proposal is not explored in terms of what a "trust score CRDT" would look like mathematically — the Beta formula does not naively commute with CRDT merge operations. Adding two Beta(α₁, β₁) distributions from two devices requires deciding whether to sum the parameters (treating them as independent observations of the same agent) or to take the min/max. This mathematical question determines whether multi-device trust accumulation is coherent or gameable. No team examined it.

---

### Missing Angle 4 — Team 3 does not address whether Submantle's Visa analogy holds for the bilateral dependency flywheel

Team 3 makes the Visa analogy strongly: "Submantle is the Visa of agent behavioral trust." The Visa flywheel requires bilateral dependency — merchants accept Visa because consumers carry it, consumers carry Visa because merchants accept it.

Team 3 does not examine how Submantle achieves bilateral lock-in. Specifically: what prevents a brand from building its own per-site behavioral scoring (HUMAN Security model) rather than querying Submantle? The Forrester BATMS category has 19 vendors doing exactly that. Why does the Visa model apply rather than the "everyone builds their own" model that the Forrester category represents?

The answer may exist (portability, O-level data, deterministic formula) but it was not articulated as a response to this specific objection.

---

## Section 5: Agreements (High-Confidence Zone)

Where all five teams independently converge, confidence is high.

### Agreement 1 — The behavioral trust gap is real and unoccupied at the portable layer

Teams 2, 3, 4, and 5 all independently confirmed: no existing player provides portable, cross-platform, OS-level behavioral trust that travels with the agent. The Forrester BATMS category (Team 3), the IETF draft landscape (Teams 1, 3, 4), the DID/VC ecosystem (Team 5), and the MCP integration surface (Team 2) all confirm the same structural absence. This is the strongest finding in the expedition and is well-evidenced.

### Agreement 2 — MCP is the right integration surface for V1

Teams 1, 2, and 4 independently converged on MCP. Team 2 provides the deepest evidence. Team 1 confirms it from the architecture angle. Team 4 confirms it from the adoption angle. This is a high-confidence finding with multiple independent verifications including my own external check of MCP adoption metrics.

### Agreement 3 — W3C VC 2.0 + SD-JWT is the right attestation format

All five teams use or confirm this. Team 5 verifies it against W3C standards track. Team 1 confirms it against RFC 9334 (RATS). Team 2 shows the MCP integration path. Team 3 confirms it aligns with the W3C WebPayments convergence on digital credentials. Team 4 notes it aligns with the neutral governance model. The only caveat (verified by me) is that the specific go-sd-jwt library's RFC 9901 conformance has not been confirmed. The format choice is correct; the library choice requires additional validation.

### Agreement 4 — "Always aware, never acting" has structural precedent (DKIM/DMARC)

Teams 1 and 4 both identify DKIM/DMARC as the architectural proof that "signal without enforcement" works at internet scale. Team 3 confirms this with the Visa analogy. The convergence on this structural argument strengthens the design principle significantly — it is not just a design choice, it is a proven pattern.

### Agreement 5 — Deterministic scoring is the right call both legally and architecturally

Teams 3, 4, and 5 all confirm that ML-based scoring would create EU AI Act exposure. Team 3 adds the strongest evidence: all existing behavioral scoring competitors (DataDome, Mnemom) use ML, creating legal exposure they may not be aware of. Submantle's deterministic formula is a genuine legal and architectural differentiator.

---

## Section 6: Surprises

### Surprise 1 — Team 1's RATS RFC 9334 finding is genuinely useful and underused

Team 1 (Section 8.1) identifies that RFC 9334 (IETF RATS Architecture) provides an exact standard vocabulary for what Submantle is building: Attester (on-device daemon), Verifier (attestation server), Relying Party (brands). This is not just an analogy — it is the IETF's formal architecture for exactly this kind of system. None of the other four teams referenced this. It should be treated as a primary architectural reference, not a supplementary finding. If Submantle submits to IETF, RATS is the working group home.

### Surprise 2 — The go-sd-jwt RFC compliance issue is more significant than Team 5 flagged

I expected to confirm Team 5's finding that go-sd-jwt v1.4.0 is the stable library for SD-JWT. What I found is that v1.4.0 was published in August 2025 and RFC 9901 was published in November 2025. The library predates the RFC by three months. The documentation still links to the draft. There is no release note claiming RFC 9901 conformance. This means both teams presenting go-sd-jwt as "implementing RFC 9901" are making an assumption that has not been verified. This needs a direct code audit or conformance test against RFC 9901 test vectors before Submantle uses it in production.

### Surprise 3 — ERC-8004 is still a draft, undermining Team 3's market validation framing

The "24K+ agents registered in first two weeks" figure from Team 3 appears to have no verifiable source. Direct verification of eips.ethereum.org/EIPS/eip-8004 shows it is a draft ERC with no deployment information. This is the most direct factual error in all five findings. It does not change the strategic picture (the market demand for agent reputation is real and evidenced by many other sources), but the specific claim is unsupported.

### Surprise 4 — The solo founder credibility problem is more acute than any team addressed directly

Team 4 identifies it honestly. But no team addresses the compound problem: Submantle's founder is non-technical AND solo AND has no institutional affiliation AND is building in a space where the incumbent competitors (Trulioo, DataDome, HUMAN Security) have institutional backing and funded development teams. The path from here to institutional co-signer is not addressed. The research brief asked for what is "realistic" for a solo founder, and the honest answer from the playbook research is that the solo founder path requires either a technical co-author who provides credibility, a beachhead community that provides social proof, or a corporate co-signer who provides legitimacy — and Submantle currently has none of these.

---

## Summary: What the Orchestrator Must Know

### Confirmed with High Confidence
1. MCP is the right integration surface for V1. Evidence is strong, multi-team, and externally verified.
2. The behavioral trust gap at the portable OS layer is real. All five teams confirm it independently.
3. W3C VC 2.0 + SD-JWT is the right attestation format. The format choice is confirmed; the library conformance requires one additional verification step.
4. The split-plane architecture (Tailscale model) is architecturally correct for Submantle's constraints.
5. Deterministic scoring has genuine legal and architectural advantages over all ML-based competitors.

### Requires Correction Before Use
1. **ERC-8004:** Present it as a draft EIP proposal, not a live mainnet standard. Remove or attribute the 24K registration figure. The market validation point still holds through other sources.
2. **ZARQ census:** Source URL is broken. Remove the specific agent/MCP server counts or re-source them.
3. **go-sd-jwt RFC 9901 conformance:** Do not state this library implements RFC 9901 without running conformance tests against RFC 9901 test vectors. The library was written before the RFC was published.

### Unresolved Tensions That Need Escalation
1. **The behavioral attestation integrity problem:** What prevents a malicious on-device daemon from lying about its trust score and getting Submantle's server to sign it? Team 1 raises this in Novel Approaches. Team 5 designs around it in the VC schema. No team resolves it. This is an architectural-level integrity question that must be answered before the MVTL is designed.
2. **Solo founder attestation server operations:** The Tailscale model requires running a key-signing service with HSM-level security. This is not addressed in terms of what a solo founder can realistically operate. The architecture is right; the operational plan is missing.
3. **The multi-device trust score federation problem:** The CRDT suggestion from Team 1 is a starting point, not a design. The Beta formula's behavior under CRDT merge is unverified mathematically.

### One Architectural Finding All Teams Missed
Team 1's identification of RFC 9334 (IETF RATS Architecture) as the formal standard for what Submantle is building should be promoted to primary architectural reference status. RATS provides the standard vocabulary (Attester, Verifier, Relying Party), the two topology models (Passport Model vs. Background-Check Model), and the relevant IETF working group for any future standards submission. None of the other four teams referenced it. It should be in the expedition synthesis.

---

*Validation completed: 2026-03-11. External sources verified via WebFetch. All evidence challenges based on direct verification, not assumption.*
