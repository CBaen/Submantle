# Validation Report 4: Identity & Cryptography
## Date: 2026-03-11
## Validator Focus: Go library landscape and DID ecosystem

---

### Evidence Challenges

**D1 — CHALLENGED (partially false): go-sd-jwt v1.4.0 is NOT the only stable Go SD-JWT library.**

Team 5 claims MichaelFraser99/go-sd-jwt is "the primary Go SD-JWT library" and the only v1.0+ option. This is incorrect. A direct pkg.go.dev search found:

- `github.com/trustbloc/vc-go/sdjwt` — v1.3.6, Apache-2.0, published January 29, 2026. This is a **complete SD-JWT implementation** covering all three roles (issuer, holder, verifier) with full lifecycle support. It is production-stable, has 50 importers, and is actively maintained (4 months newer than go-sd-jwt's last release). This is a material omission.

The omission matters because trustbloc/vc-go also covers W3C VC 2.0 data model and DIF Presentation Exchange. If Submantle uses trustbloc/vc-go, it gets SD-JWT AND VC issuance in one v1.0+ dependency, eliminating the gap Team 5 identified for VC issuance. Team 5's Go library landscape table (Part 12) listed trustbloc under the SD-JWT verifier only and did not surface that the parent module is a full v1.0+ VC stack.

**A secondary concern on go-sd-jwt itself:** The library's README references the IETF draft URL (`draft-ietf-oauth-selective-disclosure-jwt/`), not RFC 9901 specifically. Team 5 noted this caveat but assessed it as minor. This deserves stronger flagging: before production use, the library's serialization format must be verified against RFC 9901's finalized encoding. The draft and RFC may differ in normative details. This is not a blocker but is a genuine implementation risk Team 5 underweighted.

**Correction on RFC 9901 status:** Team 5 calls it an "Internet Standard" (the highest IETF designation). IETF datatracker confirms RFC 9901 is a **Proposed Standard**, not a full Internet Standard. This is still a strong standard designation with IESG approval and community review, but the characterization is technically incorrect. It does not affect Submantle's decision to use SD-JWT.

---

**D2 — CHALLENGED (requires significant qualification): The "no production Go v1.0 DID library" claim is misleading.**

Team 5 states flatly: "No production-stable (v1.0+) Go library exists for DID creation/resolution." This requires two challenges:

1. `github.com/pascaldekloe/did` — v1.1.0, CC0 license (public domain), last updated July 2023. This library implements W3C DID parsing, DID URL parsing, and DID Document parsing fully, with a `didweb` sub-package for did:web HTTP resolution. It is explicitly v1.0+ and has no external dependencies. Team 5 missed it entirely.

   **Important caveat:** pascaldekloe/did is a parsing library, not a creation/resolution library. It does not generate DID documents or handle key material. But "no production Go DID library" is a broader claim than the evidence supports.

2. `github.com/trustbloc/vc-go` — v1.3.6, as noted above, includes DIF Well Known DID Configuration support. This is not a full DID resolver but it is DID-adjacent tooling at v1.0+.

3. `github.com/decentralized-identity/web5-go` — Team 5 cited this as `tbd54566975/web5-go`. The canonical module path is `decentralized-identity/web5-go` (v0.25.0 as of December 2024). It is pre-v1.0, but Team 5's source citation is slightly wrong on the org name.

**Verdict:** The specific claim that no v1.0+ library handles DID *creation and resolution* is defensible. But stating "no production Go v1.0 DID library exists" is overbroad — pascaldekloe/did is a counterexample for parsing. The correct framing is: no v1.0+ Go library handles the full DID lifecycle (creation + key management + resolution). Parsing is solved.

---

**D3 — CONFIRMED WITH A DATE CORRECTION:** Team 5 states the last ION release was "v1.0.4 in June 2022." The releases page shows it as June 2021 (v1.0.4, June 9, 2021), not 2022. The team-5 findings document says "June 2022" in one place and cites it as "3.5 years old" from a March 2026 vantage — which would put the date at ~September 2022, not June. None of these calculations are internally consistent.

Checking the GitHub commit history: the most recent commit was August 25, 2023 (a documentation typo fix). The claims-to-validate.md says "June 2022" for the last release. The team-5 findings say "v1.0.4 in June 2022."

The ION releases page itself shows v1.0.4 on June 9, **2021**. The "3.5 years old as of March 2026" arithmetic is also wrong for that date (it would be ~4.75 years). The date discrepancy does not change the conclusion — ION is unambiguously stalled regardless of whether the last release was 2021 or 2022 — but the cited date is wrong.

**The stalled-project conclusion stands. The cited date does not.**

---

**D4 — CONFIRMED WITH NUANCE:** Ceramic did merge with Textile in February 2025 and did pivot away from decentralized identity as its primary use case. The blog post confirms this. However, the characterization "pivoted away from decentralized identity" is slightly too absolute. The post states Ceramic continues operating with no disruption and positions itself as "a foundational component of an open intelligence network where AI agents buy and sell intelligence." This is a pivot toward AI agent infrastructure, not a shutdown or abandonment of all prior work. ComposeDB deprecation is mentioned in Team 5's findings but not directly confirmed by the blog post excerpt.

**For Submantle's purposes:** Ceramic is correctly assessed as irrelevant to decentralized identity or VC infrastructure going forward.

---

**D5 — CONFIRMED BUT STATUS NEEDS PRECISION:** TRQP v2.0 is real and active. The spec document confirms it completed Public Review 02 in December 2025 and is being dispositioned in the Trust Over IP Trust Registry Task Force. Team 5 describes this as "finalizing in 2026" — which is accurate as a description of where it is headed, but it has not yet finalized. It is post-public-review, in disposition. A final spec could land in 2026 but is not guaranteed.

The claim that "Submantle could be the first behavioral trust registry" implementing TRQP is a logical argument, not a verified fact. No search contradicts it — no behavioral trust registry implementing TRQP was found — but this is an inference, not an independently confirmed finding.

---

**D6 — CONFIRMED:** No `BehavioralAttestation` credential type exists in the W3C VC 2.0 specification, the W3C CCG credential types registry (404 at the listed URL — registry may have moved), or any discovered VC ecosystem documentation. The credential type is genuinely novel as far as external searches can determine. The gap is real.

---

### Verified Claims

- **ION is stalled:** Confirmed. No release since 2021, no activity since August 2023. Microsoft has pivoted to Entra Verified ID with did:web.
- **Ceramic pivoted away from identity:** Confirmed. February 2025 Textile merger, pivot to AI agent intelligence infrastructure.
- **BehavioralAttestation does not exist:** Confirmed. No matching schema found in W3C VC 2.0, CCG, or any searchable VC ecosystem documentation.
- **TRQP v2.0 is active in 2026:** Confirmed. Post-Public-Review-02 as of December 2025, disposition ongoing.
- **go-sd-jwt v1.4.0 is stable:** Confirmed. v1.4.0 published August 30, 2025. MIT license. However, it is not the only stable SD-JWT Go library (see D1 challenge).
- **W3C VC 2.0 is a final standard:** Confirmed. Multiple finalized specs as of May 2025.
- **did:ion has no production Go library:** Confirmed. No Go library found for ION.
- **No v1.0+ Go library handles full DID lifecycle (creation + key management + resolution):** Confirmed. pascaldekloe/did handles parsing at v1.0+; nothing handles the full stack.

---

### Missing Angles

**1. trustbloc/vc-go is the elephant in the room.**
The most significant gap in Team 5's research is not flagging `github.com/trustbloc/vc-go` as the closest thing to a production-ready Go VC stack. At v1.3.6 (January 2026), Apache-2.0, it covers VC data model, SD-JWT (full issuer/holder/verifier), BBS+ signatures, DIF Presentation Exchange, and StatusList2021 revocation. It has 50+ importers and is maintained by TrustBloc (a Hyperledger Labs project). This library substantially narrows the "Go library gap" Team 5 identified. Submantle should evaluate it seriously before the Go rewrite.

**2. The "draft vs. RFC" question for trustbloc/vc-go SD-JWT needs its own check.**
trustbloc/vc-go's sdjwt package may also reference older drafts rather than RFC 9901. Both go-sd-jwt and trustbloc carry the same implementation risk. Team 5 flagged it for go-sd-jwt only.

**3. pascaldekloe/did for DID parsing.**
A zero-dependency, CC0-licensed, v1.1.0 Go DID parsing library was not surfaced. For Submantle's purposes — where the primary need is parsing agent DIDs to record behavioral data against them — this library may be sufficient for V1 without taking a dependency on heavier frameworks.

**4. axone-protocol/axone-sdk/credential.**
A v1.2.0 (April 2025) BSD-3-Clause Go VC library from the Axone Protocol was found. It is smaller and less established than trustbloc/vc-go but is another v1.0+ option not mentioned in Team 5's findings.

**5. The did:dht method was not assessed.**
The decentralized-identity/web5-go package lists `did:dht` as an active (though under-development) method. did:dht anchors DID documents in the Mainline DHT network — no blockchain, no DNS dependency, globally resolvable. It is the method TBD is actively building toward and could be relevant for Submantle's "externally verifiable on-device agent" problem (see Team 5's Gap #5). Not mentioned in Team 5's DID method assessment.

---

### Overall Assessment

Team 5's core conclusions are directionally sound: ION is stalled, Ceramic has pivoted, BehavioralAttestation is a novel credential type, and the Go DID/VC ecosystem is fragmented and pre-v1.0 for most tooling. However, the research has three material gaps that matter for Submantle's architecture decisions. First, the trustbloc/vc-go library (v1.3.6, January 2026, Apache-2.0) is a full Go SD-JWT and VC stack at v1.0+ that Team 5 missed — it partially contradicts the "no stable Go VC tooling" narrative and should be evaluated before the Go rewrite begins. Second, the D1 claim that go-sd-jwt is "the ONLY stable Go SD-JWT library" is demonstrably false; trustbloc/vc-go/sdjwt is a second production-stable option with full issuer/holder/verifier coverage. Third, the ION last-release date cited (June 2022) appears to be incorrect — the actual last formal release was June 2021 — a minor factual error that should be corrected in any external documentation. The TRQP v2.0 claim is directionally accurate but overstates finalization readiness; it has completed public review but is not yet final. None of these challenges undermine Submantle's architectural direction, but the Go library landscape is meaningfully less barren than Team 5 portrayed.
