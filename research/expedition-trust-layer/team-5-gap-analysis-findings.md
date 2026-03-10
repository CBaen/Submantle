# Team 5 Findings: Gap Analysis — What Substrate Has vs. What a Trust Layer Needs
## Date: 2026-03-10
## Researcher: Team Member 5

---

## Methodology

This analysis reads all existing Substrate prototype code (7 files), the VISION.md, the HANDOFF.md, the mae-principles expedition synthesis, and the other teams' findings where available. External research covers W3C VC 2.0, IETF EAT/RFC 9711, the agentic EAT extensions draft, MCP November 2025 spec, SPIFFE/SPIRE, OpenID Federation 1.0, cheqd's agent trust work, and current academic reputation algorithm literature. Every claim is sourced.

---

## Part 1: What Substrate Already Has (Component-by-Component Assessment)

The following table maps each existing component to its trust layer utility:

| Component | File(s) | Trust Layer Utility | Assessment |
|---|---|---|---|
| SQLite schema with `total_queries` + `incidents` | `database.py` | Alpha + Beta inputs for Beta Reputation formula | **Serves vision as-is** — schema is correct. Not yet wired. |
| HMAC-SHA256 agent token system | `agent_registry.py` | Cryptographic agent identity at registration time | **Serves vision, needs extension** — local identity, not portable |
| `trust_metadata` JSON column | `database.py` | Reserved slot for computed trust scores | **Serves vision as-is** — deliberately reserved |
| `analytics_metadata` column on scan_snapshots | `database.py` | Reserved for federated analytics aggregation | **Serves vision as-is** — architecture-forward design |
| EventBus with wildcard subscription | `events.py` | Ambient stream foundation for real-time trust events | **Serves vision as-is** — ready for MCP ambient stream |
| Privacy mode (AWARE/PRIVATE) | `privacy.py` | Trust layer privacy requirement — on-device only | **Serves vision as-is** — strongest privacy guarantee in the field |
| Process scanner + signatures.json | `substrate.py` | Behavioral context for trust scoring (what is the agent doing?) | **Needs extension** — scans processes, not agent behavior |
| `register()` / `verify()` / `deregister()` | `agent_registry.py` | Agent lifecycle management | **Serves vision, needs extension** — no uniqueness constraint yet |
| `record_query()` | `agent_registry.py` | Method exists, never called | **Gap — critical wiring missing** |
| `increment_agent_incidents()` | `database.py` | Method exists, never called | **Gap — critical wiring missing** |
| `capabilities` JSON array | `database.py` | Context axis for capability-scoped trust | **Serves vision as-is** — ready for per-capability Beta |
| `scan_with_events()` + EventBus | `substrate.py`, `events.py` | Process lifecycle events | **Partially serves** — process awareness, not agent behavioral events |
| CORS wildcard + open registration | `api.py` | Security perimeter | **Gap** — blocks production readiness |
| No auth middleware on `/api/query` | `api.py` | Trust data will never accumulate without this | **Gap — critical** (confirmed by mae-principles validators) |
| No agent name uniqueness constraint | `database.py` schema | Sybil resistance requires unique identity anchors | **Gap** — confirmed HANDOFF open decision |
| No trust score computation function | (anywhere) | Phase 1 Advisory requires a compute step | **Gap — manageable** — formula is identified, just not written |
| No trust attestation credential format | (anywhere) | Portable trust credential agents can carry | **Gap — architectural** — requires design decision |
| No cross-device identity | (anywhere) | Trust portability across Substrate nodes | **Gap — V2+** — E2E sync not yet built |

### Summary assessment
Substrate has built exactly the right foundation. The schema is correct. The crypto primitives are correct. The privacy architecture is correct. The event bus is correct. What's missing is the layer that *operates* on that foundation: the wiring that makes trust data accumulate, the function that computes a score from it, and the format that makes that score portable.

---

## Part 2: What's Missing (Gap Inventory)

### Gap 1: Auth Middleware on Query Endpoints
**Criticality: BLOCKS the vision. Must be first.**

`/api/query` and `/api/status` accept unauthenticated calls. `record_query()` is never called in `api.py`. This means `total_queries` stays at zero for every agent, permanently. The Beta Reputation formula `trust = alpha / (alpha + beta)` requires alpha > 0 to be meaningful. Without auth middleware, Substrate will never accumulate the behavioral data the trust layer is built on.

- **What it requires:** A FastAPI dependency that extracts the Bearer token from incoming requests, calls `_registry.verify(token)`, and calls `_registry.record_query(token)` on success. Unauthenticated calls get routed as Anonymous (no trust data). The open-access design is preserved — agents that don't register still get answers, they just don't accumulate trust.
- **Blocks:** Everything. No trust layer without behavioral data.
- **Source:** Mae-principles synthesis (confirmed by all 3 validators, section "The authentication gap is the real blocker"). HANDOFF.md reviewer finding: "record_query() not wired in api.py."
- **Go rewrite necessary?** No. Trivially implementable in Python FastAPI as a dependency.

### Gap 2: Incident Definition and Wiring
**Criticality: HIGH. Blocks Beta formula completeness.**

`increment_agent_incidents()` exists in `database.py` and is never called from anywhere. The Beta formula's beta input is `incidents`. Without defining what constitutes an incident and wiring detection to that counter, the denominator of the trust score is always inflated to default zero, making every agent appear maximally trusted.

- **What it requires:** (1) A definition: what is an incident for Substrate? Examples: query returns an error, agent makes a query about a process marked as critical without declaring that capability, agent deregisters and re-registers immediately (churn behavior), agent makes queries at anomalous rate. (2) Wiring: wherever those conditions are detected in `api.py`, call `_registry.increment_agent_incidents()`.
- **Blocks:** Meaningful trust differentiation between well-behaved and badly-behaved agents.
- **Source:** Mae-principles synthesis section 5; HANDOFF.md reviewer findings.
- **Go rewrite necessary?** No.

### Gap 3: Trust Score Computation Function
**Criticality: HIGH. Required for Phase 1 Advisory.**

No `compute_trust()` function exists anywhere in the codebase. The mae-principles synthesis prescribes a pure function over existing schema fields (Team 1's formula, validated by all researchers). The three-signal approach maps cleanly:

- **TEMPORAL signal:** `(now - registration_time) / 86400` — days since registration, capped at some ceiling
- **BEHAVIORAL signal:** `total_queries / max(days_active, 1)` — query frequency per day
- **OPERATIONAL signal:** `total_queries / (total_queries + incidents)` — Beta Reputation formula

Combined: weighted average. Starting weights can be equal (1/3 each). Trust tiers: Anonymous (no token) = 0.0, Registered (new) = baseline, Trusted = score above threshold.

- **What it requires:** One pure Python function, no new dependencies, returning a float 0.0-1.0 and the computed tier.
- **Blocks:** Returning trust scores in API responses (Phase 1 Advisory). Everything downstream.
- **Source:** Mae-principles synthesis, section 5. Research brief, "Beta Reputation System formula identified."
- **Go rewrite necessary?** No. The formula is language-agnostic.

### Gap 4: Trust Attestation Credential Format
**Criticality: ARCHITECTURAL. Must be designed before Go rewrite.**

This is the most consequential missing piece for the trust layer vision. Substrate can compute a trust score internally, but for agents to carry that trust score across services (to brands, marketplaces, other Substrate nodes, MCP servers), it needs a portable format.

**What the standards landscape says as of March 2026:**

W3C Verifiable Credentials 2.0 became a final W3C Recommendation on May 15, 2025. It defines the correct format for portable, cryptographically verifiable claims about any subject including machine agents. An agent's Substrate trust attestation expressed as a W3C VC would have:
- **Issuer:** Substrate node (identified by a DID or a public key — the HMAC secret is already a seed for this)
- **Subject:** The agent (identified by agent_id, which today maps to `agent_name + registration_time`)
- **Claims:** trust_score, trust_tier, registration_time, last_seen, total_queries, incident_rate — at minimum
- **Validity:** Issued with a short expiry (e.g., 24-48 hours) so stale credentials auto-invalidate
- **Selective disclosure:** BBS+ cryptosuites (also finalized W3C standard) let an agent prove "my tier is Trusted" without revealing the underlying behavioral data

This design is confirmed by at least three external sources: cheqd has already released MCP servers that enable agents to read/write DIDs and issue VCs (cheqd.io, 2025); the arXiv paper 2511.02841v1 demonstrates a mutual authentication protocol between agents using DIDs and VCs; Team 2 of this expedition (Protocol Architecture) independently reached the same W3C VC conclusion.

The IETF EAT (RFC 9711, April 2025) with the agentic extensions draft (`draft-huang-rats-agentic-eat-cap-attest-00`) is the alternative/complement. EAT is better suited for *capability* attestation (what can this agent do?) while W3C VCs are better suited for *identity and trust* attestation (who is this agent and how trusted is it?). Both can coexist — an agent could carry an EAT for capability claims and a W3C VC for trust tier claims.

- **What it requires:** Schema design for the VC (which claims, what types, what format). A `issue_trust_attestation()` function in `agent_registry.py` that produces a signed JSON-LD VC. An API endpoint (`GET /api/agents/{id}/attestation`) that returns the attestation. A revocation mechanism (when trust score drops, invalidate outstanding attestations).
- **Blocks:** Trust portability across services. Brands and marketplaces participating. Cross-node federation.
- **Source:** [W3C VC 2.0 Recommendation, May 2025](https://www.w3.org/press-releases/2025/verifiable-credentials-2-0/); [AI Agents with DIDs and VCs, arXiv 2511.02841](https://arxiv.org/html/2511.02841v1); [cheqd Agentic Trust Solutions, 2025](https://cheqd.io/solutions/use-cases/verifiable-ai/agentic-trust-solutions/); [IETF draft-huang-rats-agentic-eat-cap-attest-00](https://www.ietf.org/archive/id/draft-huang-rats-agentic-eat-cap-attest-00.html)
- **Go rewrite necessary?** Schema design in Python prototype is fine. The production Go implementation should adopt the same schema — it's language-agnostic JSON-LD.

### Gap 5: Agent Name Uniqueness Constraint
**Criticality: HIGH. Must be resolved before trust scoring goes live.**

The `agent_registry` table has no UNIQUE constraint on `agent_name`. An agent can register as "claude-assistant" ten times and get ten tokens. Under the current Beta Reputation formula, each registration starts at zero trust. A malicious agent could abuse this to reset its score: accumulate incidents, deregister, re-register under the same name, start fresh. This is the simplest Sybil vector in the current design.

The Agent Name Service (ANS) concept — documented in a 2025 IETF draft `draft-narajala-ans-00` — addresses exactly this problem: federated name uniqueness with PKI-backed verification. ANS mirrors DNS governance: unique names under federated authorities. Substrate doesn't need the full ANS complexity for V1, but it needs the uniqueness guarantee.

The HANDOFF.md explicitly flags this as an open decision: "No uniqueness constraint on agent names — decide before trust scoring."

- **What it requires:** Either: (a) UNIQUE constraint on `agent_name` in the schema (simplest, names are globally unique on a given Substrate instance), or (b) UNIQUE on `(agent_name, author)` (allows same name from different authors), or (c) A registration passphrase/challenge that ties re-registration to the original token (most trust-preserving — you can only re-register if you have the old token, which links old and new trust records).
- **Blocks:** Trust score integrity. Without this, trust decay and Sybil resistance are unsolvable.
- **Source:** [IETF Agent Name Service draft-narajala-ans-00](https://datatracker.ietf.org/doc/html/draft-narajala-ans-00); HANDOFF.md open decision; Mae-principles synthesis on event payload contracts.

### Gap 6: Trust Decay Mechanism
**Criticality: MEDIUM. Completes the "use it or lose it" design principle.**

The research brief specifies trust decay explicitly. Academic literature confirms time-based decay is essential for trust systems that resist manipulation: exponential decay functions prevent long-dormant agents from holding permanently high scores earned in a distant past, and prevent malicious agents from slowly gaming the system through low-volume fraud over extended periods.

The existing schema already supports this: `last_seen` provides the recency signal. The decay mechanism is purely computational — it does not require schema changes.

The TEMPORAL signal in the three-signal trust formula (`(now - last_seen)` contributing to score) is the implementation: an agent that hasn't queried in 30 days automatically has a lower recency component, reducing its combined score. "Use it or lose it" is already built into the formula design; it just needs the implementation.

- **What it requires:** The `compute_trust()` function (Gap 3) incorporating the TEMPORAL signal correctly. A simple exponential or linear decay factor applied to the last_seen delta. No new schema. No new infrastructure.
- **Blocks:** Nothing independently — it's part of Gap 3.
- **Source:** [Trust model based on time decay factor, ScienceDirect 2020](https://www.sciencedirect.com/science/article/abs/pii/S0045790620305619); [Blockchain-Based Reputation Management, IEICE APCC 2025](https://www.ieice.org/publications/proceedings/bin/pdf_link.php?fname=F4-1-1.pdf&iconf=APCC&year=2025&vol=97&number=F4-1-1&lang=E); mae-principles synthesis, TEMPORAL signal definition.

### Gap 7: Trust Verification Protocol (Third-Party Verification)
**Criticality: HIGH for ecosystem adoption. Deferred until attestation format exists.**

For brands and marketplaces to plug in, they need a verification endpoint: given an agent presenting a trust attestation, how does a third party verify it is valid and was issued by a legitimate Substrate node?

The W3C VC framework defines this three-party model: **Issuer** (Substrate) → **Holder** (agent) → **Verifier** (brand/marketplace). The verification is cryptographic: the Verifier checks the signature on the VC against the Issuer's public key, checks the credential hasn't expired or been revoked, and checks the claims match their policy.

For trust tier–based discounts (brands offering better rates to Trusted agents), the verification flow is: agent presents VC to brand API → brand calls Substrate's verification endpoint or independently verifies the cryptographic signature → brand applies discount policy based on trust tier in VC.

This requires Substrate to publish its public key in a discoverable way (a DID document, or a simple HTTPS endpoint). It does not require Substrate to be in the verification path in real-time — verification can be offline/local if the agent carries a valid signed VC.

- **What it requires:** A public key endpoint (`GET /api/trust/public-key` or a DID document at `/.well-known/did.json`). A verification endpoint (`POST /api/trust/verify`) that takes a VC and returns valid/invalid + claims. Documentation of the VC schema so third parties can build verifiers.
- **Blocks:** Brand participation. Marketplace integration. Cross-node trust federation.
- **Source:** [W3C VC Overview - Verification](https://www.w3.org/TR/vc-overview/); [cheqd Trust Registry Build](https://docs.cheqd.io/product/studio/trust-registries); [Indicio: Why Verifiable Credentials Will Power AI in 2026](https://indicio.tech/blog/why-verifiable-credentials-will-power-ai-in-2026/)

### Gap 8: Cross-Instance Trust Federation
**Criticality: LOW for V1. Required for "protocol layer" vision.**

For Substrate to be internet infrastructure — not just a local registry — trust scores must be portable across Substrate nodes. An agent registered on Guiding Light's Windows laptop should carry its trust history when it connects to a different Substrate instance on a different device or organization.

The architectural options as of 2026:

1. **VC portability (recommended):** The agent carries its signed VC from the issuing Substrate node. Any Substrate node anywhere can verify the VC offline using the issuer's public key. No central server required. The agent's local trust history is anchored to the issuing node — the receiving node can choose to extend provisional trust based on the VC, then build its own local behavioral record.

2. **OpenID Federation (emerging standard):** OpenID Federation 1.0 entered its final review period December 2025–February 2026. It defines a trust chain mechanism where trust propagates transitively through a federation hierarchy: leaf entity → intermediate authority → trust anchor. An IETF JWT-based chain of authority. This is how Italy's national eID federated dozens of identity providers. Substrate could join or operate an OpenID Federation to enable cross-node trust without direct bilateral relationships.

3. **E2E encrypted sync (existing Substrate roadmap):** The VISION.md already specifies E2E encrypted sync on the 1Password model. If agent trust records sync across devices with the same owner, trust portability within a user's mesh is solved trivially. Cross-owner federation is the harder case.

- **What it requires:** VC portability is the lowest-friction path and requires only Gap 4 (attestation format) to be solved first. OpenID Federation is a V2+ addition. E2E sync is on the existing roadmap.
- **Blocks:** Nothing in V1. Required for the "hundreds of millions of devices" vision.
- **Source:** [OpenID Federation 1.0 specification](https://openid.net/specs/openid-federation-1_0.html); [OpenID Federation trust chain explained](https://connect2id.com/learn/openid-federation); [arXiv 2511.02841v1 - cross-domain VC verification](https://arxiv.org/html/2511.02841v1)

### Gap 9: Marketplace Infrastructure
**Criticality: MEDIUM. Enables the business model but not the core trust layer.**

The Substrate Store concept (identity packs, certifications, brand storefronts) requires infrastructure that does not yet exist: brand API keys, discount policy storage, a query flow that branches based on trust tier, transaction logging for microfees, and a developer dashboard.

This is not a technical novelty — it's straightforward CRUD. The architectural requirement is that the trust tier be computed and available in the request context before the marketplace routing decision is made. Once Gaps 1-5 are addressed, marketplace infrastructure is buildable incrementally without architectural commitment.

The critical design note (from Team 4's research direction, confirmed by credit card network precedents): the network effect flywheel requires **brands to get real value from trust segmentation** on day one. The minimum viable marketplace is a single brand API that enforces one discount for Trusted agents and standard rates for others. Complexity follows adoption.

- **What it requires:** Trust tier exposed in API response headers or request context. A brand policy table (brand_id, min_trust_tier, discount_rate). A query interceptor that looks up policy and adjusts response. Nothing exotic.
- **Blocks:** Revenue. Not the trust layer itself.

### Gap 10: MCP Server Integration
**Criticality: HIGH for ecosystem adoption. Next major build milestone.**

The MCP specification (November 2025 version) classifies MCP servers as OAuth Resource Servers. It requires OAuth 2.1 authorization. It explicitly does NOT define behavioral trust — that gap is Substrate's opportunity.

MCP now has 97M+ monthly SDK downloads (Team 2 finding). The MCP ambient stream (EventBus wildcard → MCP stream) is already architecturally ready — the EventBus wildcard subscription was built for exactly this. The auth integration requires Substrate's agent tokens to coexist with or extend MCP's OAuth 2.1 requirement.

The November 2025 MCP spec adds: Resource Indicators (RFC 8707, scoping tokens to specific servers), incremental scope negotiation, and signed agent cards. Substrate's trust tier can be embedded as an OAuth scope or included in the signed agent card — both are within the spec's extensibility provisions.

- **What it requires:** An MCP server module that wraps the EventBus wildcard subscription as an SSE stream, exposes Substrate's 3 query tools via MCP tool definitions, and handles MCP OAuth token verification (or provides a bridge to Substrate's HMAC tokens).
- **Blocks:** Agent ecosystem adoption. Without MCP integration, Substrate is a local tool, not infrastructure.
- **Source:** [MCP Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25); [MCP Auth Analysis, Auth0, June 2025](https://auth0.com/blog/mcp-specs-update-all-about-auth/); HANDOFF.md Priority 2.

---

## Part 3: Critical Path Analysis

### The Minimum Viable Trust Layer (MVTL)

These are the 6 things that constitute a functional trust layer — the irreducible minimum before the word "trust" in the product description has any claim to truth:

| Step | Gap Addressed | Effort Estimate | Blocks If Skipped |
|---|---|---|---|
| 1. Auth middleware on query endpoints | Gap 1 | Small (~1 hour) | Everything. Trust data never accumulates. |
| 2. Agent name uniqueness constraint | Gap 5 | Small (~30 min) | Sybil attacks, score reset abuse |
| 3. Define incident types, wire counter | Gap 2 | Small-Medium (~2-3 hours) | Beta denominator stays zero |
| 4. `compute_trust()` pure function | Gap 3 | Small (~1-2 hours) | Trust scores never computed |
| 5. Return trust_score in API responses | — | Trivial (add field to response) | Phase 1 Advisory invisible |
| 6. Trust attestation credential format | Gap 4 | Medium (~1 day design + build) | Trust not portable, brands can't plug in |

Steps 1-5 constitute Phase 1 Advisory from the mae-principles synthesis. They can be built in a single focused session. They require zero new infrastructure, zero new dependencies, zero schema migration (trust_metadata column is already reserved for exactly this).

Step 6 is the architectural commitment. It requires a design decision on the VC format (W3C VC 2.0 is the right choice per two independent research teams and current standards). Once the schema is defined, implementation is straightforward.

### What Requires Architectural Commitment NOW vs. Deferrable

**Commit now (decisions that are expensive to change later):**

1. **Agent name uniqueness strategy.** Whatever uniqueness rule is chosen becomes the identity anchor for trust history. Changing it later means migrating every existing agent record or breaking backward compatibility. Decide before the first external agent registers.

2. **Trust attestation schema.** The VC claim fields determine what trust data is portable. Once brands and marketplaces build against a schema, changing it is a breaking change. Start minimal (trust_tier, issued_at, expiry, agent_id, issuer_id) and add claims over time — but the core fields must be stable from day one of Go production.

3. **Incident taxonomy.** The definition of "incident" determines what the Beta formula measures. If the taxonomy is wrong (too strict → all agents appear untrustworthy; too loose → trust scores carry no signal), the entire scoring system is miscalibrated. A written incident taxonomy, even a short v1 list, is a commitment that shapes all downstream trust decisions.

**Defer confidently (not blocking, not architectural):**

- Trust verification protocol (Gap 7) — requires attestation format first
- Cross-instance federation (Gap 8) — requires attestation format and E2E sync
- Marketplace infrastructure (Gap 9) — requires trust tier in responses first
- EigenTrust / subjective logic / multi-dimensional trust (Team 3 findings) — V2+ after months of data
- OpenID Federation participation — V2+
- Per-capability Beta distributions — V2+

### Where the Go Rewrite Becomes Necessary (vs. Nice-to-Have)

The Go rewrite is **necessary** when Substrate hits any of these conditions:

1. **Concurrent agent connections exceed ~100 simultaneous.** Python's GIL and FastAPI's async model can handle dozens of concurrent connections efficiently, but SQLite's single-writer model becomes a bottleneck before Python does. At ~100+ concurrent agents all triggering `record_query()` writes simultaneously, WAL mode starts showing contention. The 100,000 TPS benchmark (andersmurphy.com, December 2025) requires read-heavy configuration — write-heavy trust recording under concurrent load hits earlier limits.

2. **Trust attestation cryptography requires production hardness.** Python's `hmac` stdlib is correct and safe. But issuing W3C VCs with BBS+ cryptosuites (the privacy-preserving selective disclosure standard) requires a library (`py_ecc` or similar) that has not been production-validated at the scale Substrate targets. Go's crypto ecosystem (specifically `gnark` and `go-jose`) is better suited for this. Additionally: the SPIFFE/SPIRE identity stack is natively Go — if Substrate adopts SPIFFE IDs as the canonical agent identity format for enterprise deployments, Go is the natural home.

3. **Cross-device daemon deployment.** The Python prototype runs under uvicorn, which requires Python installed. Distributing a Go binary that self-contains the daemon, database, and crypto is dramatically simpler for end-user deployment — same pattern as Docker, Tailscale, and Terraform, which the VISION.md explicitly cites.

4. **MCP proxy (enterprise) requires zero-latency interception.** The MCP proxy pattern (all agent traffic routes through Substrate) requires low-latency, high-throughput request interception. Python adds overhead that becomes measurable at enterprise traffic volumes.

The Go rewrite is **not yet necessary** for:
- MVTL (Steps 1-5 above)
- Phase 1 Advisory trust scoring
- First MCP server integration
- First brand partnership (one brand at low volume)
- Dashboard depth
- Up to ~50 registered agents on a single device

**The rewrite trigger point:** When an external agent (outside Guiding Light's own use) registers and starts making regular queries, the pressure to formalize the trust token format begins. When that external agent carries its Substrate VC to a third service, the protocol surface is committed. The Go rewrite should happen *before* the first external adoption, not after — because the trust schema and API surface defined in Python become the schema and API surface the Go implementation must be backward-compatible with.

---

## Battle-Tested Approaches

### A. Beta Reputation System (already validated)
- **What:** `trust = alpha / (alpha + beta)` where alpha = `total_queries` and beta = `incidents`
- **Evidence:** Jøsang (2002), used in MANETs, IoT, P2P, and MIDGE. All three mae-principles validators confirmed. Team 3 confirmed as the right V1 algorithm.
- **Source:** Mae-principles synthesis, section 2; Team 3 findings, section 1. DOI: 10.1007/978-3-540-74810-6_8
- **Fits our case because:** The schema already has the exact fields. O(1) computation. Zero new dependencies. Upgrade path to multi-dimensional scoring is documented (Team 3, algorithm phase table).
- **Tradeoffs:** Single-dimensional until extended. Requires meaningful incident taxonomy to be non-trivial.

### B. W3C Verifiable Credentials 2.0 as Trust Attestation Format
- **What:** Cryptographically signed JSON-LD documents expressing trust claims. Issuer/Subject/Holder/Verifier model. BBS+ selective disclosure. Final W3C standard as of May 2025.
- **Evidence:** W3C Recommendation May 15, 2025. EU Digital Identity Wallet assessment completed. cheqd released MCP server for VC issuance in 2025. arXiv 2511.02841v1 demonstrates agent-to-agent VC verification in production.
- **Source:** [W3C VC 2.0 Recommendation](https://www.w3.org/press-releases/2025/verifiable-credentials-2-0/); [cheqd 2025 in Review](https://cheqd.io/blog/2025-in-review-cheqds-year-of-building-trust-identity-and-verifiable-ai/); [arXiv 2511.02841v1](https://arxiv.org/html/2511.02841v1)
- **Fits our case because:** Substrate is exactly the Issuer in the VC trust triangle. The agent is the Holder who carries the credential. Brands and marketplaces are Verifiers. Selective disclosure (BBS+) satisfies the privacy constraint: an agent can prove its trust tier without revealing which behaviors earned it.
- **Tradeoffs:** VCs are static snapshots, not live streams. Requires a revocation mechanism for when trust scores drop. The BBS+ library in Python is less mature than in Go (important for the rewrite decision).

---

## Novel Approaches

### A. IETF EAT Agentic Extension for Capability Attestation
- **What:** `draft-huang-rats-agentic-eat-cap-attest-00` extends RFC 9711 (EAT, April 2025) with 8 new claims specifically for AI agents: `agent_id`, `agent_capabilities`, `policy_constraints`, `model_fingerprint`, `dynamic_proof`, `submodules`, `endorsements`.
- **Why it's interesting:** The `endorsements` claim is structurally identical to what Substrate issues: a third-party signed attestation embedded in the agent's token. The `policy_constraints` claim is how an agent declares behavioral limits ("I will not access files outside /home/user"). An agent carrying an EAT with Substrate's endorsement embedded is the technical implementation of "Substrate Verified."
- **Evidence:** Draft published on IETF datatracker 2025. RFC 9711 published April 2025 as Internet Standards Track.
- **Source:** [RFC 9711](https://datatracker.ietf.org/doc/rfc9711/); [draft-huang-rats-agentic-eat-cap-attest-00](https://www.ietf.org/archive/id/draft-huang-rats-agentic-eat-cap-attest-00.html)
- **Fits our case because:** Substrate's trust tier can be expressed as an EAT `endorsement`. The draft is early-stage (00) — Substrate could contribute to shaping this standard to include behavioral trust claims, not just capability claims. First-mover opportunity at the standards level.
- **Risks:** Draft is 00 — immature and subject to change. EAT addresses structural/capability attestation, not behavioral history. The IETF RATS behavioral evidence draft explicitly warns about time-of-check vs. time-of-use gaps even with attestation + behavioral logging. Substrate's on-device behavioral record closes this gap, but EAT alone does not.

### B. Agent Name Service (ANS) for Sybil-Resistant Identity
- **What:** IETF draft `draft-narajala-ans-00` (2025) proposes a protocol-agnostic agent registry with PKI-backed unique name verification and challenge-response authentication, mirroring DNS governance under federated authorities.
- **Why it's interesting:** ANS solves Gap 5 (name uniqueness) at the protocol level, not just the database level. An ANS-registered agent has a globally unique, cryptographically verifiable name that cannot be spoofed without the corresponding private key. Substrate could operate as an ANS authority for agents it registers.
- **Evidence:** IETF datatracker 2025. [Sybil-Resistant Service Discovery for Agent Economies, arXiv 2510.27554](https://arxiv.org/html/2510.27554) confirms Sybil resistance requires making spam registration economically costly — either through cryptographic cost (key generation) or social cost (vouching).
- **Source:** [IETF draft-narajala-ans-00](https://datatracker.ietf.org/doc/html/draft-narajala-ans-00); [arXiv 2510.27554](https://arxiv.org/html/2510.27554)
- **Fits our case because:** The registration passphrase approach in HANDOFF.md (fix before WiFi deployment) is the V1 version of this — the passphrase adds social cost to registration. ANS is the V2 version that makes this globally verifiable.
- **Risks:** Draft is early-stage. Full ANS implementation is overkill for V1. The minimum viable version is just a uniqueness constraint in the database.

---

## Emerging Approaches

### A. OpenID Federation 1.0 for Cross-Node Trust Federation
- **What:** JWT-based trust chain specification where trust propagates transitively: leaf entity → intermediate → trust anchor. Final specification public review December 2025–February 2026.
- **Momentum:** Already in production use for Italy's national eID (federated dozens of identity providers, thousands of applications). CNCF published a Keycloak integration guide in May 2025. OpenID Federation 1.1 draft already published, indicating active development.
- **Source:** [OpenID Federation 1.0 Specification](https://openid.net/specs/openid-federation-1_0.html); [CNCF Keycloak Integration, May 2025](https://www.cncf.io/blog/2025/05/05/building-trust-with-openid-federation-trust-chain-on-keycloak-2/)
- **Fits our case because:** Cross-instance Substrate trust federation requires exactly this: a mechanism for one Substrate node to trust an attestation issued by another Substrate node without a direct bilateral relationship. OpenID Federation's trust chain model handles this without central coordination.
- **Maturity risk:** Not yet widely implemented outside EU identity contexts. Substrate needs V2+ features (E2E sync, multi-device mesh) before this is relevant. The VC portability approach (Gap 8, option A) is simpler and sufficient for V1.

### B. MCP OAuth 2.1 Trust Scope Extension
- **What:** The November 2025 MCP specification classifies MCP servers as OAuth Resource Servers and adds incremental scope negotiation. OAuth scopes can carry arbitrary claims — a scope like `substrate:trust:trusted` could communicate trust tier within the existing OAuth flow without modification to the spec.
- **Momentum:** MCP has 97M+ monthly SDK downloads as of December 2025. The AAIF (Agentic AI Foundation) was formed December 2025 under Linux Foundation with MCP, goose, and AGENTS.md as anchor projects.
- **Source:** [MCP Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25); [MCP Anniversary Blog, November 2025](https://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/); [AAIF Formation, December 2025](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation-aaif-anchored-by-new-project-contributions-including-model-context-protocol-mcp-goose-and-agents-md/)
- **Fits our case because:** Adding trust tier as an MCP OAuth scope is the lowest-friction path for agents to carry Substrate trust into any MCP-connected service. No changes to MCP are required — OAuth scope names are not standardized at the spec level.
- **Maturity risk:** OAuth scopes as trust signals have no standard semantics. A brand would need to implement Substrate-specific scope parsing. Not a standards-track approach. Viable as a pragmatic first step while the VC format matures.

---

## Gaps and Unknowns

1. **The incident taxonomy is entirely undefined.** The research has identified the formula and the plumbing but nobody has written down what specific agent behaviors constitute an incident. This requires Guiding Light's input — it's a product decision, not a technical one. "What bad things do we want to detect and penalize?" is the question.

2. **Substrate's own DID.** For Substrate to issue W3C VCs, it needs a verifiable issuer identity. The HMAC secret is a symmetric key — VC issuance requires an asymmetric key pair (the issuer's public key must be discoverable). The HANDOFF.md does not address this. It is a small but real architectural addition.

3. **Trust score calibration.** The Beta formula computes a number between 0 and 1. The trust tier thresholds (what score = Registered, what score = Trusted) are not defined anywhere. These thresholds determine how hard it is to earn trust and will require empirical calibration once real behavioral data exists. Start conservative (high thresholds) and loosen based on data.

4. **Privacy mode + trust recording interaction.** When Substrate is in PRIVATE mode, no process data is collected. But `record_query()` currently calls `verify()` which accesses the agent registry — and the agent registry works in PRIVATE mode (identity is not sensitive). The question: does query trust recording happen in PRIVATE mode? If agents can query in PRIVATE mode, should those queries contribute to their trust scores? The privacy module's design says activity is sensitive but identity is not. A case can be made either way. This needs an explicit decision.

5. **Trust score manipulation through query flooding.** A high-frequency agent that makes thousands of queries with zero incidents will rapidly accumulate a high trust score. This is technically correct behavior per the Beta formula but could be gamed. Rate limiting (which is on the HANDOFF.md open decision list under "no rate limit/passphrase") serves dual purpose: API protection and trust score integrity.

6. **What happens to trust records when an agent deregisters?** Current `deregister_agent()` deletes the DB row. If trust history is deleted on deregistration, re-registration starts from zero, which is correct for anonymous agents but potentially wrong for legitimate agents that need to rotate their credentials. A "soft delete" or credential rotation flow may be needed.

---

## Synthesis

### What does Substrate already have that genuinely serves the trust layer vision?

More than it appears. The schema is correctly designed — the `total_queries`, `incidents`, `trust_metadata`, `analytics_metadata`, `registration_time`, and `last_seen` fields are exactly the right raw materials. The HMAC-SHA256 crypto is the right primitive. The two-layer privacy defense is a genuine differentiator — Microsoft Recall faced massive backlash for centralized behavioral surveillance; Substrate's on-device model is architecturally differentiated in a way that matters to end users and regulators alike. The EventBus wildcard subscription is ready for the MCP ambient stream. The SQLite WAL mode handles the prototype scale comfortably.

### What's the strongest approach for the critical path?

The critical path is sequential and short:

**Phase 1 (auth + wiring, one session):** Auth middleware → incident taxonomy → `record_query()` wired → name uniqueness constraint → `compute_trust()` → trust score in API responses. This is the MVTL. It requires no new dependencies, no new files, no schema migration. It is the difference between a system that *could* compute trust and one that *does*.

**Phase 2 (attestation, one design session + build session):** Define the W3C VC schema for a Substrate Trust Attestation. Generate an asymmetric key pair for the Substrate issuer identity. Implement `issue_trust_attestation()`. Add `/api/agents/{id}/attestation` endpoint. Add a short-lived expiry and a revocation mechanism. This is the difference between trust that is local and trust that is portable.

**Phase 3 (MCP integration, the ecosystem door):** Wrap the EventBus as an MCP SSE stream. Expose the 3 query tools as MCP tools. Handle MCP OAuth token integration. Include trust tier in the MCP response context. This is the difference between a local daemon and internet infrastructure.

### What combination of approaches is recommended?

- **Trust formula:** Beta Reputation System (confirmed by two independent expeditions, all validators, and current academic literature)
- **Trust credential format:** W3C VC 2.0 with BBS+ selective disclosure (confirmed by Team 2, cheqd, arXiv 2511.02841, and now this team independently)
- **Capability attestation:** IETF EAT with agentic extensions as a complementary format — Substrate endorsements embedded as EAT `endorsements` claims
- **Name uniqueness:** V1 = database UNIQUE constraint on `agent_name`. V2 = registration passphrase tying re-registration to old token. V3 = ANS-compatible when the draft matures.
- **Cross-node federation:** V1 = VC portability (agent carries credential, verifier checks signature). V2 = OpenID Federation trust chain.
- **MCP integration:** OAuth scope as pragmatic first step, VC as the durable solution.

### What does the orchestrator need to know that doesn't fit neatly into categories?

**The window is real but not permanent.** As of March 2026, no production trust layer for agents exists. The IETF and W3C are actively writing the standards. The agent frameworks (MCP, A2A) explicitly have no behavioral trust layer. The Cloud Security Alliance published an Agentic Trust Framework in February 2026 that identifies exactly the gap Substrate fills. The DEV.to article published in early 2026 describes the current state as "the early web before HTTPS." This is an accurate description of the moment.

But: cheqd has MCP servers for DID and VC issuance. The IETF has active drafts for agentic EAT. The standards space is moving. The window for Substrate to *define* the standard (not just implement it) requires participation in these standards bodies — contributing to `draft-huang-rats-agentic-eat-cap-attest` would put Substrate's behavioral trust model into the IETF process. This is not required for V1, but it is the play that converts Substrate from "a product that uses standards" to "the project that defines the behavioral trust standard."

**The six unwired lines of code are the company.** `record_query()` is never called. `increment_agent_incidents()` is never called. Auth middleware doesn't exist. These are not technical debt — they are the gap between "we have the infrastructure" and "the infrastructure works." Everything in the trust layer vision — the Beta formula, the trust tiers, the brand discounts, the behavioral VCs — requires these six wires to be connected. The MVTL is less than a day of work. It is the highest-leverage thing that can be built right now.

**SQLite is not the bottleneck.** The instinct to rewrite in Go for scale is correct in direction but premature in timing. SQLite with WAL mode has been benchmarked at 100,000 TPS over a billion rows (andersmurphy.com, December 2025) for read-heavy workloads. Substrate's trust recording is write-heavy under concurrent agent load — but "concurrent agent load" at the prototype stage is Guiding Light's own agents plus a handful of early adopters. The Go rewrite becomes necessary when: (1) concurrent agents exceed ~100, (2) VC issuance requires production crypto libraries, or (3) distribution requires a self-contained binary. None of these apply before MCP integration is built and tested.

**The product insight and the trust layer are the same insight.** "Your devices know what's going on" (the feeling) and "trust is earned through observed behavior" (the mechanism) are both about reliable, unself-reported awareness. The trust layer is not a pivot from the product — it is the product at the protocol layer. Substrate feels the ground. Trust is what the ground has earned. The brand discount is how the ground becomes the infrastructure everything else pays to stand on.

---

*Sources referenced in this document:*
- [W3C VC 2.0 Recommendation, May 2025](https://www.w3.org/press-releases/2025/verifiable-credentials-2-0/)
- [W3C VC Overview](https://www.w3.org/TR/vc-overview/)
- [RFC 9711 EAT, IETF April 2025](https://datatracker.ietf.org/doc/rfc9711/)
- [IETF draft-huang-rats-agentic-eat-cap-attest-00](https://www.ietf.org/archive/id/draft-huang-rats-agentic-eat-cap-attest-00.html)
- [AI Agents with DIDs and VCs, arXiv 2511.02841v1](https://arxiv.org/html/2511.02841v1)
- [cheqd Agentic Trust Solutions 2025](https://cheqd.io/solutions/use-cases/verifiable-ai/agentic-trust-solutions/)
- [cheqd 2025 in Review](https://cheqd.io/blog/2025-in-review-cheqds-year-of-building-trust-identity-and-verifiable-ai/)
- [cheqd Issue VC to AI Agent](https://docs.cheqd.io/product/getting-started/ai-agents/trust-registry/setup/issue-credential)
- [MCP Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25)
- [MCP Auth Update, Auth0 June 2025](https://auth0.com/blog/mcp-specs-update-all-about-auth/)
- [OpenID Federation 1.0 Specification](https://openid.net/specs/openid-federation-1_0.html)
- [OpenID Federation Trust Chain Explained](https://connect2id.com/learn/openid-federation)
- [CNCF OpenID Federation Keycloak, May 2025](https://www.cncf.io/blog/2025/05/05/building-trust-with-openid-federation-trust-chain-on-keycloak-2/)
- [SPIFFE for Attestable Workload Identity, Solo.io 2025](https://www.solo.io/blog/spire-attestable-workload-identity)
- [IETF draft-narajala-ans-00 Agent Name Service](https://datatracker.ietf.org/doc/html/draft-narajala-ans-00)
- [Sybil-Resistant Service Discovery, arXiv 2510.27554](https://arxiv.org/html/2510.27554)
- [Agentic Trust Framework, CSA February 2026](https://cloudsecurityalliance.org/blog/2026/02/02/the-agentic-trust-framework-zero-trust-governance-for-ai-agents)
- [Agent Economy Has No Trust Layer, DEV.to 2026](https://dev.to/darbogach/why-your-ai-agent-needs-a-trust-badge-the-agent-economy-has-no-trust-layer-3f05)
- [SQLite 100K TPS, andersmurphy.com December 2025](https://andersmurphy.com/2025/12/02/100000-tps-over-a-billion-rows-the-unreasonable-effectiveness-of-sqlite.html)
- [Trust Decay in Social Networks, ScienceDirect 2020](https://www.sciencedirect.com/science/article/abs/pii/S0045790620305619)
- [Indicio: Verifiable Credentials for AI in 2026](https://indicio.tech/blog/why-verifiable-credentials-will-power-ai-in-2026/)
- [Arxiv 2511.19930: Reputation Systems for Data Trading, November 2025](https://arxiv.org/abs/2511.19930)
- Mae-principles expedition synthesis (this project, 2026-03-10)
- HANDOFF.md (this project, 2026-03-10)
- VISION.md (this project, 2026-03-10)
