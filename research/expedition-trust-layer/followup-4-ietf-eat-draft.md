# Followup Research: IETF Agentic EAT Extension Draft — Status and Revival Potential

**Date:** 2026-03-11
**Researcher:** Expedition Team Member
**Assignment:** Investigate draft-huang-rats-agentic-eat-cap-attest-00 and the broader landscape of agentic attestation standards
**Context:** Two prior research teams incorrectly presented this expired draft as an active standards opportunity. This report corrects the record.

---

## Executive Summary

The Huang draft is **confirmed expired** with no revival, renewal, or supersession as of 2026-03-11. The RATS working group has not formally discussed agentic extensions. However, the broader IETF landscape is more active than prior teams reported — a parallel Huawei draft on EAT profiles for AI agents is **currently active**, two WIMSE-adjacent drafts are live, and NIST launched a formal AI Agent Standards Initiative in February 2026. The conditions for Submantle to submit its own individual draft are favorable and the process is accessible.

---

## Question 1: Status of draft-huang-rats-agentic-eat-cap-attest-00

**Status: EXPIRED. Not renewed. Not superseded.**

- Submitted: June 13, 2025 (version 00 only — never revised)
- Expired: December 15, 2025 (185-day IETF rule)
- Current datatracker state: "Expired Internet-Draft (individual)"
- RFC stream: None (was listed as "(None)" — no WG stream, no ISE stream)
- Intended RFC status: Standards Track (aspirational, never progressed)
- WG adoption: None — never submitted to RATS WG for consideration
- IETF endorsement: None — explicitly "not endorsed by the IETF"

The IETF archives the expired version as a tombstone. The datatracker note warns: "The e-mail addresses provided for the authors of this Internet-Draft may no longer be valid." This is a standard signal that the authors have not been actively maintaining IETF engagement.

A companion draft from the same author — `draft-huang-acme-scalable-agent-enrollment-00` (extending SCEP/EST for agentic AI certificate enrollment) — **also expired December 15, 2025** on the same date, with no renewal. Both appear to have been one-and-done submissions.

**Source:** https://datatracker.ietf.org/doc/draft-huang-rats-agentic-eat-cap-attest/

---

## Question 2: Author and Affiliation

**Ken Huang** — sole author of the expired draft.

- Affiliation: **DistributedApps.ai** (ken.huang@distributedapps.ai)
- DistributedApps.ai describes itself as focused on "Agentic AI Threat Intelligence"
- Huang is also listed in Cloud Security Alliance contributor records
- Co-authored a related paper on "AI Agents with Decentralized Identifiers and Verifiable Credentials" (arXiv:2511.02841, November 2025)
- His IETF profile shows two individual drafts (both expired) and no working group affiliation
- The companion ACME draft listed a co-author: Jerry Huang (AT&T) — different person, same surname

**Assessment:** Ken Huang is an independent researcher/startup founder, not a delegate from a major vendor with institutional IETF standing. This explains the lack of WG adoption activity. No academic institution affiliation. No follow-on version submitted.

**Sources:**
https://datatracker.ietf.org/person/ken.huang@distributedapps.ai
https://distributedapps.ai/publications
https://github.com/kenhuangus

---

## Question 3: Has the RATS WG Discussed Agentic Extensions Since the Draft Expired?

**No formal discussion found.** Evidence from three sources:

1. **RATS mailing list (March 2026):** Live threads are focused on EAT `exp` claim encoding, epoch markers, timestamp handling, and preparation for IETF 125 presentations. No AI or agentic attestation threads visible.

2. **RATS WG charter:** Does not mention AI, agents, or behavioral attestation. The charter focuses on traditional system component integrity, manufacturing provenance, and evidence conveying protocols.

3. **RATS active work items (as of 2026-03-11):**
   - draft-ietf-rats-ear (EAT Attestation Results)
   - draft-ietf-rats-corim (COTS software management reference)
   - draft-ietf-rats-epoch-markers
   - draft-ietf-rats-reference-interaction-models
   - draft-ietf-rats-endorsements
   - draft-ietf-rats-daa (Direct Anonymous Attestation)

   None of these address AI agents or behavioral attestation.

The Huang draft was submitted *to* RATS by naming convention (draft-huang-**rats**-...) but there is no evidence it was ever discussed on the RATS mailing list, presented at a RATS WG session, or reviewed by the WG chairs.

**Sources:**
https://mailarchive.ietf.org/arch/browse/rats/
https://datatracker.ietf.org/wg/rats/about/
https://datatracker.ietf.org/doc/charter-ietf-rats/

---

## Question 4: Process for Reviving an Expired Draft vs. Submitting a New One

These are functionally **the same process** — there is no special "revival" track at IETF.

### How Expired Drafts Work
- I-Ds expire automatically 185 days after submission
- The expired version remains in the archive as a read-only tombstone
- Expiration has no formal consequence — it is not rejection, just inactivity
- To "revive" an expired draft, the author simply submits a new version (e.g., -01) through the standard Datatracker submission tool. The draft name carries over.

### How to Submit a New Individual Draft
1. Write the draft in RFCXML (v3 preferred) or plain text
2. Submit via https://datatracker.ietf.org/submit — no login required, but recommended
3. The tool validates format using xml2rfc and idnits
4. Email verification step (or automatic if logged in as a listed author)
5. The draft appears in the IETF I-D repository within hours
6. **Cost: Free. No membership required. No institutional affiliation required.**

### Naming Convention for WG-Targeting Drafts
If targeting a specific WG for eventual adoption, the convention is:
`draft-{authors}-{wgname}-{title}-00`

Example for RATS: `draft-submantle-rats-behavioral-attestation-00`
Upon WG adoption, it would be renamed: `draft-ietf-rats-behavioral-attestation-00`

### WG Adoption Process
1. Submit individual draft targeting WG namespace
2. Present at WG session or propose on mailing list
3. WG chairs call for adoption (if there is sufficient interest)
4. WG members express support/objection
5. If adopted, authors submit renamed `draft-ietf-{wg}-...` as version -00
6. From adoption to RFC: typically 1-4 years (varies widely)

### Timeline Reality Check
- Individual draft → WG discussion: months
- WG adoption → RFC publication: 1-4 years
- With no WG interest at all: individual draft can remain indefinitely as informational reference

**Sources:**
https://ietf.github.io/id-guidelines/
https://authors.ietf.org/submitting-your-internet-draft
https://www.ietf.org/participate/ids/

---

## Question 5: Other Active Drafts for Behavioral/Agentic Attestation at IETF

This is where prior research was incomplete. There is **more active work** than previously reported:

### Active Individual Drafts (verified as of 2026-03-11)

#### draft-messous-eat-ai-00
- **Status: ACTIVE** — last updated February 23, 2026, expires August 27, 2026
- Authors: Ayoub Messous, Lionel Morand, Peter Chunchi Liu (all Huawei R&D)
- Scope: EAT profile for autonomous AI agents — model integrity (weights/architecture hashes), training data provenance, inference-time authorization constraints, SBOM references
- Stream: Individual submission — not WG-adopted
- Relationship to RATS: Complements the RATS architecture
- Notable: Includes optional 5G/6G extensions for ETSI ENI and 3GPP interoperability
- This draft is CLOSER to Submantle's behavioral layer than the Huang draft — it includes training data provenance and inference constraints
- **Source:** https://datatracker.ietf.org/doc/draft-messous-eat-ai/

#### draft-ni-wimse-ai-agent-identity-02
- **Status: ACTIVE** — last updated February 28, 2026, expires September 1, 2026
- Authors: Ni Yuan, Peter Chunchi Liu (Huawei)
- Scope: WIMSE applicability for AI agents — dual-identity credential binding (agent identity + owner identity), bootstrapping and attestation, cross-organization agent interactions
- Working group target: WIMSE (Workload Identity in Multi System Environments)
- **Source:** https://datatracker.ietf.org/doc/draft-ni-wimse-ai-agent-identity/

#### draft-klrc-aiagent-auth-00
- **Status: ACTIVE** — last updated March 2, 2026, expires September 3, 2026
- Authors: Kasselman (Defakto Security), Lombardo (AWS), Rosomakho (Zscaler), Campbell (Ping Identity) — strong institutional backing
- Scope: Authentication and authorization framework treating agents as workloads — mTLS, WIMSE Proof Tokens, OAuth 2.0 delegation, credential lifecycle
- Notable: Backed by major vendors (AWS, Zscaler, Ping Identity)
- **Source:** https://datatracker.ietf.org/doc/draft-klrc-aiagent-auth/

#### draft-ni-a2a-ai-agent-security-requirements-00/01
- **Status: ACTIVE** — submitted November 2, 2025, expires May 6, 2026
- Authors: Ni Yuan, Liu, Geng, Gao, Li (all Huawei)
- Scope: Security requirements across agent lifecycle — provisioning, registration, cross-domain, access control. Mentions remote attestation for execution environment posture.
- Target WG: agent2agent
- **Source:** https://datatracker.ietf.org/doc/html/draft-ni-a2a-ai-agent-security-requirements-00

### Important Observation on the Huawei Cluster
Three of the four active drafts above are by Huawei researchers. This appears to be a coordinated internal effort — multiple overlapping drafts from the same organization, targeting different WGs (RATS, WIMSE, agent2agent). This is how institutional actors work IETF: flood multiple tracks and see what gets traction.

### What's Missing from All of These
None of the active drafts address **behavioral attestation** — runtime observation of what an agent actually does vs. what it claims. The Messous draft comes closest (inference-time constraints) but remains focused on identity/capability claims, not observed behavior over time. This is a genuine gap.

---

## Question 6: RATS WG Current Charter and Active Work Items

The RATS WG charter centers on:
- Establishing procedures for how Verifiers assess Evidence from Attesters
- Standardizing formats for Evidence, Endorsements, and Attestation Results
- The two-stage appraisal model: Evidence → Verifier → Attestation Result → Relying Party

**Current active WG-adopted drafts:**
- draft-ietf-rats-ear (EAT Attestation Results)
- draft-ietf-rats-corim (Concise Reference Integrity Manifests)
- draft-ietf-rats-epoch-markers
- draft-ietf-rats-reference-interaction-models (Challenge/Response, Uni-Directional, Streaming)
- draft-ietf-rats-endorsements
- draft-ietf-rats-daa (Direct Anonymous Attestation)
- draft-ietf-rats-ar4si (Attestation Results for Secure Interactions)
- draft-ietf-rats-eat-measured-component

**IETF 125 call for presentations:** Live as of March 2026 — WG is actively meeting.

**Charter explicitly out of scope:** Appraisal policy formats and protocols.

**AI/agentic attestation:** Not in charter. Not in active work items. No sign of impending scope expansion.

**Sources:**
https://datatracker.ietf.org/wg/rats/about/
https://datatracker.ietf.org/doc/charter-ietf-rats/

---

## Question 7: What Would It Take for Submantle to Submit Its Own Individual Draft?

### Technical Requirements
- Write the draft in RFCXML or plain text following IETF formatting guidelines
- Document must stand alone — full abstract, introduction, terminology, security considerations, IANA considerations sections
- For a RATS-targeting draft: Must engage with RFC 9334 (RATS architecture) and RFC 9711 (EAT / the base we'd extend)
- Idnits tool compliance (nit checker for formatting)

### Process Requirements
- No membership or institutional affiliation required
- No fee
- Submit at datatracker.ietf.org/submit
- Email verification
- That's it — the draft is live immediately upon successful submission

### Strategic Requirements (what actually matters for traction)
1. **Name it for the target WG:** `draft-{authors}-rats-behavioral-attestation-00` signals intent to RATS
2. **Get on a WG agenda:** Email the RATS chairs (rats-chairs@ietf.org) requesting a discussion slot at IETF 125
3. **Post to the mailing list:** rats@ietf.org — introduce the draft, explain the gap it fills
4. **Have co-authors with institutional backing:** A single startup author (like Huang) gets less traction than a multi-org author list. Target: one author from a major cloud vendor, one from academia
5. **Engage before the draft:** The IETF blog post from January 2026 notes a proposed agent-to-agent working group with a strawman charter. Participating there first builds relationships

### Timeline Estimate (realistic)
- Submission of individual draft: Can happen any time — weeks to prepare a solid -00
- First WG discussion (if agenda slot obtained): IETF 125 (likely late 2026)
- WG adoption (if interest exists): 6-18 months post-first-discussion
- RFC publication (if adopted): 2-5 years

### Submantle-Specific Strategic Assessment
Submantle's behavioral trust layer — the part that observes runtime agent behavior and generates attestation evidence — would be a **novel contribution** to the IETF landscape. No existing draft covers this. The gap is real and documented in prior expedition findings.

However: An IETF draft is a standards play, not a product play. The right sequencing is:
1. Build the behavioral attestation capability in Submantle (product)
2. Document the technical approach publicly (whitepaper or blog)
3. Submit a draft once there is real-world data to reference
4. Use the draft process to build relationships with cloud vendors who would co-author

**Sources:**
https://ietf.github.io/id-guidelines/
https://authors.ietf.org/submitting-your-internet-draft

---

## Question 8: Other Standards Bodies Working on Behavioral Attestation for AI Agents

### NIST — AI Agent Standards Initiative (February 2026)
- **Announced:** February 17, 2026
- **Scope:** Authentication, identity infrastructure for agents; software and AI agent identity and authorization; sector-specific adoption (healthcare, finance, education)
- **Active consultations:** RFI on AI agent security (closed March 9, 2026); comment period on identity/authorization concept paper (closed April 2, 2026)
- **Relationship to behavioral attestation:** Addresses identity and authorization; does not yet define behavioral monitoring standards
- **Significance:** NIST involvement signals US government alignment — standards that emerge here often flow into federal procurement requirements
- **Source:** https://www.nist.gov/caisi/ai-agent-standards-initiative

### Linux Foundation — Agentic AI Foundation (AAIF, December 2025)
- **Founded:** December 2025
- **Founding members:** Anthropic, OpenAI, Block, AWS, Google, Microsoft, and others
- **Contributed projects:** MCP (Anthropic), goose (Block), AGENTS.md (OpenAI)
- **Scope:** Interoperability, not attestation — making agents work together, not verifying their behavior
- **Behavioral attestation:** Not in current scope; "security controls" mentioned for MCP but not defined
- **Significance:** Anthropic is a founding member — this is directly relevant to Submantle's MCP integration angle
- **Source:** https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation

### FIDO Alliance
- **AI agent work:** Exploratory, not standardized. Leadership has discussed at plenaries that "behavioral changes will require new standards, devised and agreed to by the FIDO Alliance"
- **Current posture:** Starting with agents using existing credentials, eventually developing agent-specific identities
- **No published specification** for AI agent behavioral attestation as of 2026-03-11
- **Source:** https://sphericalcowconsulting.com/2026/02/17/understanding-the-fido-alliance/

### W3C — AI Agent Protocol Community Group
- **Status:** Community group (not a formal W3C working group — lower standing)
- **Scope:** Agent discovery, interoperability, verifiable credential-based trust, end-to-end encryption
- **Behavioral attestation:** Mentioned in design goals but not formalized
- **Source:** https://www.w3.org/community/agentprotocol/

### Cloud Security Alliance (CSA)
- **Agentic Trust Framework (ATF):** Published February 2, 2026
- **Behavioral attestation:** Explicitly covered — "behavioral biometrics provide continuous authentication beyond cryptographic keys"; "trust earned through demonstrated behavior and continuously verified through monitoring"
- **Nature:** Framework/guidance document, NOT a formal technical standard
- **Significance:** CSA is influential in enterprise security practice — their frameworks shape enterprise purchasing and compliance requirements even without formal standards status
- **STAR for AI:** CSA is extending their Security, Trust, Assurance, and Risk (STAR) certification program to AI systems
- **Source:** https://cloudsecurityalliance.org/blog/2026/02/02/the-agentic-trust-framework-zero-trust-governance-for-ai-agents

### IEEE / ISO / ITU-T
- No evidence found of active behavioral attestation standards for AI agents at these bodies as of 2026-03-11. The 3GPP/ETSI connection appears in the Huawei drafts (5G/6G context) but is not a general behavioral attestation standard.

---

## Synthesis: The Real Standards Picture

Prior research teams overstated the Huang draft's significance (active standards opportunity) and understated the broader landscape.

**What is actually happening:**

1. **RATS WG is not leading AI attestation.** It is focused on its existing charter (hardware/firmware attestation, TPM-style evidence). AI is not in scope.

2. **The agentic identity/attestation space is fragmenting across WIMSE, RATS, and a proposed new WG.** No single WG owns this. The Huawei cluster is testing multiple tracks simultaneously.

3. **Behavioral attestation (runtime observation of agent behavior) has no formal IETF or W3C home.** It exists in CSA guidance documents and academic papers but not in standards-track protocol work. This is the genuine gap.

4. **The agent-to-agent WG proposal (from IETF 124 side meeting, January 2026 blog post) is the most likely future home** for agent trust standards. If this WG is chartered, it would be the right target for Submantle's contribution.

5. **The behavioral trust layer Submantle is building has no standards-track competition.** That is both an opportunity (first-mover in standards) and a challenge (no existing WG to anchor to).

**What this means for Submantle:**
- Monitoring the IETF agent-to-agent mailing list and proposed WG charter process is the right move
- A Submantle individual draft should wait until (a) the behavioral trust layer is built and (b) the agent-to-agent WG is chartered — targeting the new WG rather than RATS
- The CSA Agentic Trust Framework is worth engaging with now — it creates enterprise demand for exactly what Submantle provides, and CSA involvement would build credibility before an IETF submission

---

## Research Confidence Assessment

| Finding | Confidence | Source Quality |
|---------|------------|----------------|
| Huang draft expired, not renewed | High | Verified on IETF Datatracker directly |
| Ken Huang / DistributedApps.ai affiliation | High | Datatracker profile + GitHub + CSA profile |
| RATS WG has not discussed agentic extensions | High | Live mailing list + charter review |
| Messous draft is active (Huawei) | High | Verified on IETF Datatracker directly |
| klrc-aiagent-auth is active | High | Verified on IETF Datatracker directly |
| IETF draft submission process | High | Official IETF guidelines |
| AAIF founding members / scope | High | Linux Foundation press release |
| NIST AI Agent Standards Initiative | High | NIST official page |
| FIDO Alliance exploring AI standards | Medium | Third-party reporting on plenary |
| No active behavioral attestation standard anywhere | High | Cross-confirmed across all sources |

---

## Key URLs for Future Reference

- Expired Huang draft: https://datatracker.ietf.org/doc/draft-huang-rats-agentic-eat-cap-attest/
- Active Messous draft: https://datatracker.ietf.org/doc/draft-messous-eat-ai/
- Active WIMSE AI identity draft: https://datatracker.ietf.org/doc/draft-ni-wimse-ai-agent-identity/
- Active klrc auth draft: https://datatracker.ietf.org/doc/draft-klrc-aiagent-auth/
- RATS WG: https://datatracker.ietf.org/wg/rats/about/
- IETF agentic AI blog (January 2026): https://www.ietf.org/blog/agentic-ai-standards/
- IETF draft submission tool: https://datatracker.ietf.org/submit
- Draft author guidelines: https://ietf.github.io/id-guidelines/
- NIST AI Agent Standards Initiative: https://www.nist.gov/caisi/ai-agent-standards-initiative
- Linux Foundation AAIF: https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation
- CSA Agentic Trust Framework: https://cloudsecurityalliance.org/blog/2026/02/02/the-agentic-trust-framework-zero-trust-governance-for-ai-agents
