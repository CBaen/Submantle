# Claims Requiring Validation — Protocol Architecture Expedition
## Date: 2026-03-11

These are the key claims from 5 research teams that need external verification.

---

## CLUSTER A: MCP Dominance & Integration Surface

**Claim A1 (Team 2):** MCP Go SDK is at v1.4.0 with 4.1k GitHub stars, 995 dependent projects, co-maintained by Anthropic and Google.
- Source cited: github.com/modelcontextprotocol/go-sdk

**Claim A2 (Team 2):** MCP TypeScript SDK has 11.8k stars, v1.27.1 (Feb 2026), 158 contributors.
- Source cited: github.com/modelcontextprotocol/typescript-sdk

**Claim A3 (Team 2):** LangChain MCP adapter has 3.4k GitHub stars as of March 2026.
- Source cited: github.com/langchain-ai/langchain-mcp-adapters

**Claim A4 (Team 2):** Every major agent framework (LangChain, CrewAI, AutoGen, Semantic Kernel) either natively connects to MCP servers or has an adapter. A single MCP server implementation reaches the majority of production agents.

**Claim A5 (Team 2):** MCP OAuth 2.1 authorization spec maps directly to Substrate's existing HMAC bearer token model.
- Source cited: modelcontextprotocol.io/specification/2025-11-25/basic/authorization

**Claim A6 (Team 2):** A2A protocol (Google) has 22.4k GitHub stars, v0.3.0, Linux Foundation stewardship.
- Source cited: github.com/google/A2A

---

## CLUSTER B: Behavioral Trust Gap

**Claim B1 (Team 3):** No company offers portable, OS-level, deterministic behavioral trust scoring for agents. All existing BATMS vendors (19 in Forrester category) are per-site, web-layer only.
- Vendors checked: HUMAN Security, DataDome, Akamai, Arkose Labs, CHEQ, ClawTrust, Mnemom, Signet, ZARQ, Oscilar, Kontext

**Claim B2 (Team 3):** Google UCP "does not solve which agents should be trusted."
- Source cited: ucp.dev spec, TechCrunch January 2026

**Claim B3 (Team 3):** Mastercard Verifiable Intent (March 5, 2026) explicitly excludes behavioral trust — authorization only.

**Claim B4 (Team 3):** Stripe articulated "Five Levels of Agentic Commerce" and the trust cliff is at Level 3→4 (from "help me decide" to "decide for me").
- Source cited: stripe.com/blog/three-agentic-commerce-trends-nrf-2026

**Claim B5 (Team 3):** WEF projects AI agents market at $236B by 2034.
- Source cited: weforum.org/stories/2026/01/ai-agents-trust/

**Claim B6 (Team 3):** Multiple IETF drafts note "continuous attestation of behavioral patterns is required" but none specify how.
- Source cited: datatracker.ietf.org/doc/draft-klrc-aiagent-auth/

**Claim B7 (Team 3):** AAIF (Agentic AI Foundation, Linux Foundation) has no working group addressing behavioral trust.
- Source cited: aaif.io

**Claim B8 (Team 3):** ERC-8004 on Ethereum mainnet had 24K+ agents registered in first two weeks (January 2026). Uses feedback-based reputation, NOT runtime behavioral observation.
- Source cited: eips.ethereum.org/EIPS/eip-8004

---

## CLUSTER C: Protocol Architecture

**Claim C1 (Team 1):** RATS RFC 9334 "Passport Model" (agent carries credential, presents anywhere) names Substrate's architecture precisely.
- Source cited: IETF RATS architecture

**Claim C2 (Team 1):** Tailscale's split-plane model (thin control plane + on-device data plane) is the correct reference architecture.

**Claim C3 (Team 1):** Certificate Transparency's gossip protocol achieves distributed verification without centralization — reference for trust score propagation.

**Claim C4 (Team 1):** Minimum viable infrastructure: signing key + HTTPS endpoint + on-device daemon.

---

## CLUSTER D: Identity & Cryptography

**Claim D1 (Team 5):** go-sd-jwt v1.4.0 is the ONLY stable (v1.0+) Go SD-JWT library.
- Source cited: github.com/MichaelFraser99/go-sd-jwt

**Claim D2 (Team 5):** No production Go v1.0 DID library exists as of March 2026. Multiple pre-v1.0 libraries available.

**Claim D3 (Team 5):** did:ion is stalled — last formal release June 2022, Microsoft pivoted to Entra Verified ID.
- Source cited: github.com/decentralized-identity/ion

**Claim D4 (Team 5):** Ceramic Network pivoted away from decentralized identity (February 2025 merger with Textile).
- Source cited: blog.ceramic.network/ceramic-is-joining-textile/

**Claim D5 (Team 5):** TRQP v2.0 (Trust Registry Query Protocol) is finalizing in 2026 — Substrate could implement as first behavioral trust registry.
- Source cited: trustoverip.github.io/tswg-trust-registry-protocol/

**Claim D6 (Team 5):** BehavioralAttestation credential type does not exist anywhere in the VC ecosystem.

---

## CLUSTER E: Adoption & Solo Founder

**Claim E1 (Team 4):** IETF philosophy: "rough consensus and running code" — build first, standardize later.
- Source cited: RFC 8170

**Claim E2 (Team 4):** Solo founders created Git (Torvalds) and BitTorrent (Cohen) as protocols.

**Claim E3 (Team 4):** Let's Encrypt adoption pattern: free automated certs drove HTTPS from ~39% to ~49% in one year (2016).

**Claim E4 (Team 4):** AAIF is the natural venue for behavioral trust spec — members include Anthropic, OpenAI, Google, AWS, Microsoft.

**Claim E5 (Team 4):** RFC 8170 principle: "Transition is easiest when changing only one entity still benefits that entity."

**Claim E6 (Team 4):** Solo founder CAN create protocols but needs technical co-author for spec credibility.

---

## META-QUESTIONS FOR VALIDATORS

1. Has ANY new behavioral trust competitor emerged since March 2026 that we missed?
2. Is MCP actually as dominant as claimed, or are there serious alternatives the teams didn't consider?
3. Is the "product first, protocol later" path actually viable, or does Substrate need to start as a protocol from day one?
4. Can a non-technical founder maintain direction over a protocol project, or will they inevitably lose control?
5. Are there regulatory risks the teams understated?
