# Follow-Up Research: BBS+ Cryptosuite Status
## Date: 2026-03-11
## Researcher: Expedition Follow-Up Agent
## Assignment: Verify W3C BBS+ finalization status for Submantle Trust Attestations

---

## Research Summary

This report resolves the open question flagged in validation-2.md and synthesis.md: whether BBS+ cryptosuites are among the finalized W3C specifications or remain as Candidate Recommendations. All findings are externally verified via live web sources. The answer has direct implications for whether Submantle can use BBS+ for selective disclosure in V1 or must choose an alternative.

---

## Question 1: What is the current W3C status of BBS+ cryptosuites?

**Answer: Candidate Recommendation Draft (CRD) — NOT a W3C Recommendation.**

The specification "Data Integrity BBS Cryptosuites v1.0" is published as a W3C Candidate Recommendation Draft as of **April 3, 2025**. It has not been elevated to a W3C Recommendation. The document explicitly states: "Publication as a Candidate Recommendation does not imply endorsement by W3C and its Members."

Source: https://www.w3.org/TR/vc-di-bbs/

---

## Question 2: Which two W3C VC specifications were NOT finalized in May 2025?

**Answer: Confirmed. The two specifications that remained as Candidate Recommendations are:**

1. **Data Integrity BBS Cryptosuites v1.0** — BBS+ signature suite enabling zero-knowledge proof disclosures. Still Candidate Recommendation Draft as of April 3, 2025.
2. **Verifiable Credentials JSON Schema Specification** — Provides credential schema mechanisms for semantic interoperability. Still Candidate Recommendation Draft as of February 4, 2025.

The seven specifications that DID reach W3C Recommendation on May 15, 2025 were:
- Verifiable Credentials Data Model v2.0 (core spec)
- Verifiable Credentials Data Model v1.1
- Verifiable Credential Data Integrity 1.0
- Data Integrity ECDSA Cryptosuites v1.0
- Data Integrity EdDSA Cryptosuites v1.0
- Securing Verifiable Credentials using JOSE and COSE
- Bitstring Status List v1.0

Source: https://www.w3.org/groups/wg/vc/publications/

---

## Question 3: Is BBS+ one of the two that remained as Candidate Recommendations?

**Answer: Yes. BBS+ is one of the two specifications that did not make it into the May 2025 finalization.**

This is definitively confirmed. The W3C VC Working Group publications page clearly separates the two Candidate Recommendation Drafts (BBS Cryptosuites and JSON Schema) from the seven W3C Recommendations published May 15, 2025.

**This means:** Any Submantle architecture relying on BBS+ selective disclosure is building on a specification that has not achieved final W3C Recommendation status.

---

## Question 4: If BBS+ is not yet finalized, what is the timeline to finalization?

**Answer: No official timeline. Estimated 2026-2027 based on precedent and current trajectory.**

### What is known:
- BBS Cryptosuites entered Candidate Recommendation on **April 4, 2024**
- As of March 2026, it has been in Candidate Recommendation for approximately **11 months** since the April 2025 CRD update
- The W3C VC Working Group charter runs until **March 31, 2028**, providing the institutional container
- No open GitHub issues reference a target Recommendation date
- The only active milestone ("BbsSignature2021") shows 50% completion with no due date

### The blocking dependency:
The W3C BBS Cryptosuites spec contains a critical "at-risk" provision: optional BBS features "will be removed before finalization if their respective specifications at the IETF do not reach RFC status on the same timeline." This links W3C BBS advancement to:

**IETF draft-irtf-cfrg-bbs-signatures** — The underlying BBS Signatures specification being developed in the IRTF Crypto Forum Research Group. As of January 8, 2026, it is at **draft version 10** and targets Informational RFC status through the IRTF stream (not the IETF Standards Track). No telechat date or responsible AD is assigned. Timeline to publication is indeterminate.

### Comparison to ECDSA precedent:
The Data Integrity ECDSA Cryptosuites followed this path:
- First Candidate Recommendation: November 21, 2023
- Final Recommendation: May 15, 2025
- **Duration: approximately 17-18 months in Candidate Recommendation**

BBS Cryptosuites entered Candidate Recommendation in April 2024. Applying the 17-18 month ECDSA precedent would suggest a target of **late 2025 to early 2026** — a window that has already passed without advancement. The IETF dependency appears to be the reason BBS is taking longer than ECDSA.

**Realistic estimate:** If the IRTF BBS Signatures draft publishes as an Informational RFC in mid-2026, W3C BBS Cryptosuites could reach Recommendation by **late 2026 to early 2027**. This is speculative — no official timeline exists.

---

## Question 5: Are there production implementations of BBS+ selective disclosure available today?

**Answer: Yes — several exist, but with important caveats about maturity and Go support.**

### Implementation landscape (as of March 2026):

The W3C BBS Cryptosuites test suite interoperability report (dated March 8, 2026) documents **six independent implementations**:
1. Digital Bazaar, Inc. (JavaScript — strong conformance)
2. Grotto Networking (strong conformance)
3. Netis
4. Procivis One Core
5. SpruceID (Rust via SSI library)
6. Trential

This substantially exceeds the two-implementation threshold required to exit Candidate Recommendation, suggesting the specification is technically mature even though the formal process has not concluded.

### Library assessment by language:

**JavaScript (most mature):**
- `@digitalbazaar/bbs-2023-cryptosuite` — implements BBS-2023 Data Integrity cryptosuite. Available on NPM. No formal releases tagged on GitHub, security documentation marked "TBD." Not recommended for production security-critical use.
- This is the most actively developed implementation but lacks a production release.

**Rust (strong):**
- SpruceID SSI library (Apache 2.0, Trail of Bits security audit March 2022, 645 commits). Confirmed as one of six registered W3C implementations.
- `mattrglobal/pairing_crypto` — implements BBS Signatures draft-03. **Explicitly notes no independent audit.** Not production-ready.

**Go (weak — the critical gap for Submantle's future):**
- `hyperledger/aries-bbs-go` — implements older BBS+ standard (not BBS-2023). No releases, 12 commits, pre-production.
- `github.com/aniagut/msc-bbs-anonymous-credentials` — published June 2025, 0 imports. Research/academic, not production.
- **No production-quality Go implementation of BBS-2023 (the current W3C cryptosuite) exists.**

**Python:**
- No dedicated BBS-2023 Python library identified.

### Bottom line on implementations:
BBS+ selective disclosure can be implemented today if using JavaScript or Rust. For Submantle's planned production language (Go), no production-quality BBS-2023 library exists. This is a material constraint for the Go rewrite phase.

---

## Question 6: What is the practical impact for Submantle? Can we build on BBS+ today, or should we use an alternative for V1?

**Answer: Do not use BBS+ for V1. Use SD-JWT selective disclosure instead. BBS+ is the right V2/V3 target when specification and Go library support mature.**

### Why BBS+ is not recommended for V1:

1. **Specification is not final.** Building on a Candidate Recommendation creates adoption risk — the spec can still change before Recommendation. The optional features risk-clause means some capabilities could be removed entirely if the IETF dependency doesn't resolve.

2. **No production Go library.** Submantle's production language is Go. No production-quality Go implementation of BBS-2023 exists as of March 2026. The Python prototype phase could use JavaScript-binding workarounds, but this adds complexity.

3. **Complexity overhead.** BBS+ requires pairing-friendly elliptic curves (BLS12-381), RDF dataset canonicalization, and the BBS+ proof generation protocol. This is substantially more complex than SD-JWT to implement and debug.

4. **Not the practical standard being deployed.** OpenID for Verifiable Credential Issuance (OID4VCI, published as Final September 2025) explicitly supports SD-JWT VC but does not mention BBS+. The EU Digital Identity Wallet and major production deployments are converging on SD-JWT, not BBS+.

### Why BBS+ remains valuable for V2/V3:

1. **Unlinkability.** BBS+ generates cryptographically unlinkable presentations — two proofs derived from the same credential cannot be correlated by verifiers. SD-JWT does NOT provide this property. For Submantle's use case (behavioral trust attestations shown to multiple parties), this matters: a verifier cannot tell if the same credential was shown to 10 other verifiers.

2. **Single credential, multiple selective disclosures.** BBS+ allows holder to generate any subset disclosure from a single signed credential without re-issuance. SD-JWT requires the issuer to pre-commit to which fields are disclosable.

3. **Implementation trajectory is positive.** Six registered implementations, actively maintained spec, W3C Working Group charter through 2028. This will eventually become a final Recommendation.

**Recommendation for Submantle build sequence:**
- **V1 (now):** Use SD-JWT (RFC 9901) for selective disclosure in Trust Attestations
- **V2 (when Go library matures):** Add BBS+ support as an optional cryptosuite
- **V3 (when W3C Recommendation finalized):** Make BBS+ the default for privacy-preserving disclosures

---

## Question 7: What alternatives to BBS+ exist for selective disclosure in VCs?

### Alternative 1: SD-JWT (Recommended for V1)

**Standard:** RFC 9901 — "Selective Disclosure for JSON Web Tokens," published November 2025. Full Internet Standards Track RFC. This is the clear winner for V1.

**How it works:** The issuer marks specific claims as selectively disclosable by replacing their values with hash digests. The holder presents only the claims needed, along with the pre-images (disclosures) for those claims. Verifiers check that disclosed claims match the signed digests.

**Privacy properties:**
- Holder can disclose any subset of pre-marked fields
- Undisclosed fields are hashed — their values are not revealed
- **Does NOT provide unlinkability** — presentations can be correlated (all use the same credential)
- Key binding (optional) prevents holder impersonation

**Production ecosystem:**
- `go-sd-jwt` (Go, v1.4.0, MIT, stable v1 semver) — available now
- W3C VC JOSE/COSE (May 2025 Recommendation) explicitly supports SD-JWT VC format
- OID4VCI (Final, September 2025) explicitly supports SD-JWT VC
- EU Digital Identity Wallet specification uses SD-JWT
- RFC 9901 is the most deployed selective disclosure standard in production as of early 2026

**Tradeoff vs BBS+:** Simpler, better Go support, more deployed, but no unlinkability.

### Alternative 2: AnonCreds

**Standard:** Community Specification v1.0 Draft, AnonCreds Working Group (moved from Hyperledger). Not a W3C or IETF standard.

**How it works:** Uses CL (Camenisch-Lysyanskaya) signatures with zero-knowledge proofs. Predicate proofs allow statements like "age > 18" without revealing the actual age. Originally built for the Hyperledger Indy/Sovrin ecosystem.

**Production ecosystem:** Used in production in several national identity systems (primarily European). Rust library (anoncreds-rs) at v0.2.3. No Go library.

**Tradeoff vs BBS+:** More mature in production for the Indy/ACA-Py ecosystem, but not aligned with W3C VC 2.0 core standards. Tight ecosystem lock-in. **Not recommended for Submantle** — poor standards interoperability with the broader W3C VC ecosystem that Submantle needs to participate in.

### Alternative 3: JSON-LD + ECDSA/EdDSA (No selective disclosure)

**Standard:** W3C Recommendations (May 15, 2025) — fully finalized.

**How it works:** Standard Data Integrity proofs over the full credential. No selective disclosure capability — the entire credential must be presented.

**Relevance for Submantle V1:** If selective disclosure is deferred to V2, this is the simplest path — use finalized ECDSA or EdDSA cryptosuites with W3C VC 2.0, accept that the full trust attestation is always presented, add selective disclosure later. Excellent Go library support exists (multiple mature JWT/VC libraries).

**Tradeoff:** Simplest to implement but sacrifices privacy — a verifier sees the full trust score and all attestation fields. For Submantle's "prove your tier without revealing your data" design, this is insufficient.

### Alternative 4: Zero-Knowledge Proofs (V3+)

As identified in the expedition synthesis, ZKPs (zk-SNARKs, PLONK, etc.) provide the strongest unlinkability and predicate proof capabilities. Deferred to V3 due to computational overhead and library immaturity. Not an alternative for V1 or V2.

---

## Summary Table

| Approach | W3C/IETF Status | Unlinkability | Go Support | V1 Ready |
|----------|----------------|---------------|------------|----------|
| SD-JWT | RFC 9901 (Nov 2025, Final) | No | Yes (go-sd-jwt v1.4.0) | Yes |
| BBS-2023 | W3C CRD (not Recommendation) | Yes | No production library | No |
| AnonCreds | Community Spec (not W3C/IETF) | Yes | No | No |
| ECDSA/EdDSA | W3C Recommendation (May 2025) | N/A (no disclosure) | Yes | If no disclosure needed |
| ZKP | No standard yet | Yes | No | No |

---

## Recommendation for Submantle

**For V1 Trust Attestations: Use SD-JWT (RFC 9901) with W3C VC 2.0.**

The combination of W3C VC Data Model v2.0 (May 2025 Recommendation) with SD-JWT-encoded selective disclosure is:
- Fully standardized (RFC 9901 + W3C Recommendation)
- Production-ready in Go (go-sd-jwt v1.4.0)
- Aligned with the real-world production ecosystem (EU Digital Identity, OID4VCI)
- Buildable today without waiting for any additional specification work

**The privacy tradeoff is acceptable for V1:** SD-JWT does not provide BBS+-style unlinkability, but for Submantle's V1 use case (agents presenting their trust tier to brand partners), the inability to correlate presentations across verifiers is a V2/V3 concern, not a V1 blocker. The behavioral trust scoring system itself is far more privacy-sensitive than the disclosure format at this stage.

**Keep BBS+ on the V2 roadmap.** The specification is technically mature (six implementations, active maintenance, W3C Working Group through 2028). When the IRTF BBS Signatures RFC publishes (likely 2026) and a production Go library emerges, upgrade Submantle's attestation layer to support BBS-2023 as an optional cryptosuite for privacy-sensitive contexts.

**Validate this decision before the Trust Attestation Layer build begins** — specifically, confirm that cheqd's existing MCP VC implementation (flagged in synthesis.md as a potential reference) uses SD-JWT or BBS+, since aligning with their format could save significant implementation time.

---

## Confidence Assessment

| Finding | Confidence | Basis |
|---------|------------|-------|
| BBS+ is one of the two non-finalized specs | HIGH | Direct W3C publications page verification |
| BBS+ is Candidate Recommendation Draft | HIGH | Direct W3C TR page verification |
| Six implementations registered March 2026 | HIGH | W3C test suite interoperability report |
| No production Go BBS-2023 library | HIGH | pkg.go.dev search + direct GitHub repo checks |
| IETF BBS Signatures at draft-10 (not RFC) | HIGH | IETF datatracker direct verification |
| SD-JWT is RFC 9901 (Nov 2025) | HIGH | IETF datatracker + RFC editor confirmation |
| OID4VCI supports SD-JWT, not BBS+ | HIGH | OpenID Foundation final spec verification |
| BBS+ timeline estimate (late 2026–2027) | LOW-MEDIUM | Derived from ECDSA precedent; no official date |

---

*Research completed: 2026-03-11. External sources verified via live web fetch: W3C TR, W3C publications index, W3C test suite implementation report, IETF datatracker, RFC editor, OpenID Foundation, pkg.go.dev, GitHub repositories.*
