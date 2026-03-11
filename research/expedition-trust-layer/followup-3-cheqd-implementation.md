# Followup Research: What cheqd Actually Built
**Date:** 2026-03-11
**Researcher:** Expedition Sub-Agent
**Trigger:** Team 5 cited cheqd as having MCP servers for VC issuance to AI agents. No team investigated the details.
**Sources:** GitHub repo, raw source files, official docs, blog posts, third-party reporting.

---

## Executive Summary

cheqd has built a real, working, open-source MCP server for issuing verifiable credentials to AI agents. It is not vaporware. It is also not a behavioral trust system — it is purely a **credential issuance and accreditation infrastructure**. cheqd's work is directly relevant to Substrate's attestation design and presents both a reference implementation and a partial integration opportunity, but it does not overlap with Substrate's behavioral layer (runtime observation, process awareness, event-driven signatures). These are additive, not competitive.

---

## 1. What cheqd Has Actually Built

### The MCP Toolkit (`cheqd/mcp-toolkit`)
- **Repository:** https://github.com/cheqd/mcp-toolkit
- **License:** Apache-2.0
- **Created:** March 13, 2025
- **Last release:** February 20, 2026 (v1.4.1-develop.2)
- **Commits:** 152
- **Stars:** 1 (extremely low adoption signal)
- **Language:** TypeScript (98.6%)

The toolkit is a **modular monorepo** with three packages:

| Package | Purpose |
|---------|---------|
| `packages/credo` | Core identity tools built on OpenWallet Foundation's Credo-ts library |
| `packages/server` | Local MCP server (stdio transport) |
| `packages/remote-server` | Hosted remote MCP server at remote-mcp.cheqd.io/mcp |

### Deployment Options
1. **Remote (hosted):** Connect to `https://remote-mcp.cheqd.io/mcp` via npx — zero setup, shared infrastructure
2. **Local NPX:** Run locally with environment variables (CREDO_PORT, CREDO_NAME, CREDO_ENDPOINT, CREDO_CHEQD_TESTNET_MNEMONIC, TRAIN_ENDPOINT)
3. **Docker Compose:** Containerized local deployment

---

## 2. MCP Tool Inventory (Complete)

These are the actual MCP tools the server exposes, derived from source code:

### DID Management Tools
| Tool | Description |
|------|-------------|
| `create-did` | Creates and publishes a new DID document to testnet or mainnet |
| `resolve-did` | Resolves a DID document and metadata from cheqd network |
| `update-did` | Updates an existing DID document |
| `deactivate-did` | Permanently marks a DID as inactive |
| `list-did` | Lists all DIDs in the agent's wallet |
| `create-did-linked-resource` | Publishes a resource linked to an existing DID |
| `resolve-did-linked-resource` | Resolves a specific DID-linked resource by DID URL |

### Credential Tools
| Tool | Description |
|------|-------------|
| `create-credential-offer-connectionless` | Creates a connectionless offer (generates QR code) |
| `create-credential-offer-didcomm` | Creates a credential offer over an established DIDComm connection |
| `list-credentials` | Retrieves all credential records from agent wallet |
| `list-credential-exchange-records` | Lists all credential exchange transactions |
| `get-credential-record` | Fetches a specific credential by ID |
| `accept-credential-offer` | Accepts a pending credential offer |
| `import-credential` | Imports a JWT credential string into the wallet |

### AnonCreds (Schema/Definition) Tools
| Tool | Description |
|------|-------------|
| `list-schemas` | Lists all schemas from agent wallet |
| `get-schema` | Resolves a schema by DID URL |
| `create-schema` | Publishes a new credential schema to cheqd |
| `list-credential-definitions` | Lists all credential definitions |
| `get-credential-definition` | Resolves a credential definition |
| `create-credential-definition` | Publishes a credential definition for a schema |

### Proof Tools
| Tool | Description |
|------|-------------|
| `create-proof-request-connectionless` | Creates a connectionless proof request with QR code |
| `create-proof-request-didcomm` | Creates a proof request over DIDComm connection |
| `list-proofs` | Retrieves all proof records |
| `get-proof-record` | Fetches a specific proof record |
| `accept-proof-request` | Accepts a proof request and generates a ZKP from wallet credentials |

### Connection Tools
| Tool | Description |
|------|-------------|
| `create-connection-invitation-didcomm` | Creates a DIDComm invitation with QR code |
| `accept-connection-invitation-didcomm` | Accepts an invitation URL to establish DIDComm connection |
| `list-connections-didcomm` | Lists all established connections |
| `get-connection-record-didcomm` | Fetches a specific connection record |

### Trust Registry Tool
| Tool | Description |
|------|-------------|
| `verify-trust-registry` | Verifies a DID or credential against the trust registry via TRAIN |

**Total: 23 MCP tools across 5 categories.**

---

## 3. VC Schema: What Fields/Claims Are Supported

cheqd has defined a specific schema for AI agent credentials. The credential type is:

```
type: ["VerifiableCredential", "VerifiableAttestation", "AIAgentAuthorization"]
format: VC-JWT (default)
```

### Credential Fields for AI Agents

**Identity fields:**
- `aiAgentName` — agent name
- `aiAgentVersion` — version string
- `issuerDid` — DID of the issuing organization
- `subjectDid` — DID of the AI agent itself

**Model metadata:**
- `model` — model type (e.g., Claude, GPT-4)
- `modelVersion` — specific version
- `contextWindow` — token context limit
- `temperature`, `topK`, `topP`, `maxTokens` — inference parameters

**Training & safety:**
- `fineTuned` — boolean flag
- `fineTuningDetails` — description of fine-tuning
- `safetyRating` — safety assessment value
- `certifications` — compliance certifications array

**Performance:**
- `evaluationMetrics` — includes BLEU-4, ROUGE-L, F1 scores

**Governance:**
- `certificationAuthority` — who certified this agent
- `validUntil` — credential expiry timestamp
- `credentialSchema` — reference to JSONSchemaValidator2020
- `termsOfUse` — attestation policy details

### Agent Bill of Materials
cheqd also supports an "Agent Bill of Materials" credential type that records who built the agent, what model/corpus was used, when it was deployed, and by whom — functioning as a verifiable provenance record for AI agents.

---

## 4. Agent Identity (DIDs)

cheqd uses **did:cheqd** as the primary DID method, anchored on a Cosmos SDK blockchain. Key properties:

- Each AI agent gets its own DID (unique per-agent identity)
- DIDs are created programmatically via `create-did` MCP tool
- DID documents are stored on-ledger with verification methods
- DIDs can be updated (capability changes) or deactivated (agent retirement)
- Full DID resolution via cheqd's Universal Resolver driver

The DID serves as the cryptographic anchor for all credentials. An agent's wallet holds its DID's private keys and all associated credentials.

---

## 5. Behavioral Trust: None

This is the critical finding for Substrate.

cheqd's system is **purely credential issuance and accreditation-based**. Trust is derived from:
1. Who signed the credential (institutional authority)
2. Whether the issuer is in a trusted trust chain
3. Whether the credential has been revoked

There is **no behavioral trust component**:
- No runtime behavioral monitoring
- No observation of what an agent actually does
- No reputation scoring based on actions
- No anomaly detection
- No behavioral signatures or patterns

cheqd answers: *"This agent was authorized by this organization."*
cheqd does **not** answer: *"This agent behaves consistently with its authorization."*

The `verify-trust-registry` tool returns a boolean (`VerificationStatus: true/false`) plus a timestamped summary. It is a point-in-time credential validity check, not ongoing behavioral assessment.

---

## 6. Revocation Mechanism

cheqd implements **two revocation mechanisms**, both on-chain:

### Bitstring Status List (W3C Standard)
- Each issued credential is assigned an `index` position in a bitstring
- The bitstring is a compressed binary array: `0` = valid, `1` = revoked
- The status list is stored on-ledger as a **DID-Linked Resource** (versioned)
- **Revocation:** Issuer calls `POST /credential/revoke` with `listType: "BitstringStatusList"` and `publish: true` — this flips the bit at the credential's index and publishes the updated bitstring on-ledger
- **Verification:** Verifier calls `POST /credential-status/check` with the DID, list name, and index — returns `{"revoked": true/false}`
- **Supports suspension** (temporary revocation) in addition to permanent revocation

### AnonCreds Revocation Registry
- Uses cryptographic accumulator-based revocation (Hyperledger AnonCreds spec)
- Status lists stored as DID-Linked Resource versions (revocation registry definitions + entries)
- Holders can generate **zero-knowledge proof of non-revocation** — they prove their credential is not revoked without revealing which credential they hold
- Verifiers can verify this proof without learning the credential holder's identity
- Designed as migration path for organizations moving off deprecated Sovrin/Indy networks

### Critical Note for Substrate
The revocation mechanism is **issuer-initiated only**. A credential can only be revoked by the entity that issued it (or an authorized delegatee). There is no mechanism for automated revocation based on behavioral violations. This is an architectural gap cheqd has not addressed.

---

## 7. Open Source and License

- **License:** Apache-2.0 — permissive, commercially friendly, patent grant included
- All packages in the mcp-toolkit monorepo are Apache-2.0
- The underlying Credo-ts library (OpenWallet Foundation) is also Apache-2.0
- **Fully open source** — no proprietary lock-in in the core tools

---

## 8. Integration vs. Build from Scratch

### What cheqd Has Already Solved
- DID creation and management on-chain
- VC issuance (W3C JWT format)
- AnonCreds ZKP-based credentials
- Bitstring Status List revocation
- Trust chain validation via TRAIN
- MCP tool wrappers for all of the above
- Hosted remote server (zero ops)

### What cheqd Has Not Solved (Substrate's Territory)
- **Behavioral observation** — what is an agent actually doing at runtime?
- **Process-level awareness** — what software is running, consuming resources?
- **Event-driven trust signals** — detecting anomalies, pattern changes, deviations
- **Behavioral attestation** — signing observed behavior into a verifiable claim
- **Cross-device awareness** — knowing what's happening across a device mesh
- **Lightweight local execution** — cheqd requires Node.js 20+, a full wallet agent, and blockchain connectivity

### Integration Feasibility
Substrate could **extend** cheqd's work in a specific, targeted way:

**Scenario:** Substrate observes agent behavior for N hours/actions. If behavior is consistent with the agent's declared credential, Substrate generates a **behavioral attestation VC** and submits it via the cheqd MCP toolkit's `create-credential-offer-connectionless` tool. This would be the world's first behavioral trust layer feeding into a credential trust layer.

This is additive, not duplicative. cheqd handles the credential infrastructure; Substrate handles the behavioral evidence. Neither can do what the other does.

---

## 9. Business Model

cheqd operates a **dual revenue model**:

### CHEQ Token (On-Chain Fees)
- Every DID write and resource creation on the cheqd ledger requires CHEQ tokens
- Credential Payments: verifiers pay credential issuers in CHEQ when decrypting on-ledger resources
- The more credentials issued/verified, the more CHEQ consumed and burned
- July 2025: Launched a Cosmos-powered fee oracle to peg CHEQ transaction costs to USD equivalents, eliminating price volatility for enterprises

### cheqd Studio (SaaS)
- REST API platform for credential issuance without blockchain expertise
- Targeted at enterprises and credential platform partners (Paradym, Truvera, Hovi Studio)
- Partners build commercial credential products on top of cheqd's infrastructure

### Partner Ecosystem Revenue
- Partners pay for API access to cheqd Studio
- cheqd earns through network transaction volume (on-chain) and enterprise SaaS

---

## 10. Adoption and Traction

### GitHub Metrics
| Repository | Stars | Forks |
|-----------|-------|-------|
| cheqd-node | 69 | 51 |
| mcp-toolkit | 1 | unknown |
| did-resolver | 11 | unknown |
| studio | 11 | unknown |

**The MCP toolkit has 1 star.** This is a signal that it is new infrastructure being pushed by the company, not organically adopted yet.

### Verified Partnerships (2025)
- **ASI Alliance** (Fetch.ai, SingularityNET, Ocean Protocol, CUDOS): 20+ projects using AI agent identity system, including TrueAGI, Rejuve.AI, SophiaVerse
- **VERA**: 50K verified business identities in South Africa
- **JuliaOS**: Native credential issuance and auditor attestations
- **PlatformD**: Privacy-preserving DeFi compliance VCs
- **Sovereign AI Alliance**: Co-founded with Datahive, Nuklai, Datagram

### Scale Metrics (H1 2025)
- 230K+ testnet DIDs created
- 7 strategic partnerships

### Market Recognition
- Ranked 34th in UK's top startups for scalable identity solutions (August 2025)

---

## 11. BBS+ Selective Disclosure

**No BBS+ support in the current MCP toolkit.** The package.json dependencies confirm:
- `@credo-ts/anoncreds` — AnonCreds selective disclosure via ZKPs
- `@hyperledger/anoncreds-nodejs` and `anoncreds-shared` — cryptographic primitives

There is **no BBS+ library** (e.g., `@mattrglobal/bbs-signatures`) in the dependency tree.

cheqd supports **two forms of selective disclosure**:
1. **AnonCreds ZKPs** — Holder proves specific attributes without revealing others, using cryptographic accumulator. Supported in mcp-toolkit.
2. **SD-JWT** — Mentioned in cheqd's documentation as supported format, but **not included in the mcp-toolkit** (no SD-JWT library in package.json).

BBS+ is not on cheqd's public roadmap for 2025-2026. Their selective disclosure strategy appears committed to AnonCreds for ZKP-based privacy.

---

## 12. Competitor or Partner?

**Assessment: Potential partner, not a competitor.**

| Dimension | cheqd | Substrate |
|-----------|-------|---------|
| Core capability | Credential issuance + trust chain validation | Behavioral observation + runtime awareness |
| Trust model | Institutional accreditation | Behavioral attestation |
| Data source | Organizational decisions | Live device/agent runtime |
| Revocation trigger | Issuer decision | (Future) Behavioral violation |
| Privacy approach | ZKP/AnonCreds | On-device processing |
| Infrastructure | Cosmos blockchain | SQLite + local daemon |
| Deployment | Node.js + wallet agent | Lightweight local daemon |
| Target customer | Enterprises, credential platforms | All devices, all agents |

The only overlap is the **end goal** (trusted agents), not the **mechanism**. cheqd answers "who authorized this agent"; Substrate answers "what is this agent doing."

A partnership makes conceptual sense: Substrate observes behavior and generates behavioral evidence; cheqd issues and manages the credentials that encode that evidence. This is not a product partnership to pursue now — but it is worth noting the architectural compatibility.

---

## Key Findings for Substrate's Attestation Design

1. **Revocation mechanism is solved** — Bitstring Status List on-chain is the standard. Substrate does not need to invent this. If Substrate issues attestation VCs, it should use the same W3C Bitstring Status List pattern, either via cheqd's infrastructure or its own implementation.

2. **VC schema is flexible but not behavioral** — cheqd's `AIAgentAuthorization` schema encodes model metadata and safety ratings, not runtime behavior. Substrate would need a new credential type (e.g., `BehavioralAttestation`) with fields for: observed_pattern_hash, observation_window, deviation_score, last_observed_timestamp.

3. **DID per agent is the right pattern** — Every agent should have its own DID. cheqd validates this. Substrate's agent identity module (already built) aligns with this.

4. **TRAIN is a reference for trust chain verification** — The recursive trust chain validation (credential → issuer accreditation → root DID → DNS anchor) is a mature pattern. Substrate's attestation verification could adopt the same recursive model.

5. **Apache-2.0 means Substrate can use cheqd's code directly** — If Substrate ever issues W3C-format VCs, the cheqd MCP toolkit can be dropped in as a credential management layer. No legal or licensing barrier.

6. **BBS+ is not the path** — Neither cheqd nor the broader MCP ecosystem has moved to BBS+. AnonCreds ZKPs are the privacy-preserving path for selective disclosure in this ecosystem.

---

## Sources
- https://github.com/cheqd/mcp-toolkit (source code and releases)
- https://docs.cheqd.io/product/getting-started/ai-agents (AI agent documentation)
- https://docs.cheqd.io/product/getting-started/ai-agents/trust-registry/setup/issue-credential (VC schema)
- https://docs.cheqd.io/product/getting-started/ai-agents/validate (TRAIN validation flow)
- https://docs.cheqd.io/product/studio/credentials/revoke-credential (revocation)
- https://docs.cheqd.io/product/studio/status-lists/bitstring-status-list/check (verification)
- https://cheqd.io/blog/pioneering-trust-in-the-age-of-ai-introducing-cheqds-mcp-enabled-agentic-trust-solution/
- https://cryptobriefing.com/cryptographic-verification-ai-impersonation/ (ASI Alliance partnership)
- https://cheqd.io/blog/2025-in-review-cheqds-year-of-building-trust-identity-and-verifiable-ai/
