# Submantle Index

**Purpose:** Pointers to research and reference material. Permanent. Stays small.

## Research

- **Submantle Deep Dive Expedition** (2026-03-09): First expedition — what Submantle is, competitive landscape, MCP integration strategy, process identity architecture. Details: `research/expedition-submantle-deep-dive/synthesis.md`

- **Submantle Infrastructure Expedition** (2026-03-09): Second expedition — Go vs Rust vs Python, SQLite architecture, daemon design, gRPC vs REST, plugin isolation. Details: `research/expedition-submantle-infrastructure/synthesis.md`

- **Trust Layer Expedition** (2026-03-11): Third expedition — behavioral trust as internet protocol layer. 5 teams (historical precedents, protocol architecture, behavioral trust science, marketplace competitors, gap analysis) + 3 validators + 1 synthesis. Details: `research/expedition-trust-layer/synthesis.md`

- **Trust Layer Follow-ups** (2026-03-11): 6 targeted investigations resolving open questions from the expedition:
  - Mastercard/Google Verifiable Intent — complementary, not competitive: `research/expedition-trust-layer/followup-1-mastercard-google.md`
  - BBS+ status — still Candidate Recommendation, use SD-JWT for V1: `research/expedition-trust-layer/followup-2-bbs-plus-status.md`
  - cheqd MCP implementation — VC issuance toolkit, no behavioral trust: `research/expedition-trust-layer/followup-3-cheqd-implementation.md`
  - IETF EAT draft status — expired, but 3 active drafts exist, gap uncontested: `research/expedition-trust-layer/followup-4-ietf-eat-draft.md`
  - EU AI Act implications — likely outside scope (deterministic arithmetic): `research/expedition-trust-layer/followup-5-eu-ai-act.md`
  - Solo founder feasibility — works for product phase, 5 sessions for MVTL: `research/expedition-trust-layer/followup-6-solo-founder.md`

- **Protocol Architecture Expedition** (2026-03-11): Fourth expedition — what Submantle IS technically, how agents connect, competitive landscape update, adoption playbook. 5 teams + 9 validators. MCP confirmed, RATS RFC 9334 mapped, incident taxonomy resolved (credit bureau model), Go library landscape corrected. Details: `research/expedition-protocol-architecture/synthesis.md`

- **V1 Foundation Build** (2026-03-10): Triadic construction — 3 builders + 3 reviewers. Privacy mode, SQLite, event bus, agent identity. 160 tests. Details: `research/triadic-build-v1-foundation/build-brief.md`

- **Research Council V2: Product-Market Fit** (2026-03-12): Full 5-phase council — 3 agents + challenge round + synthesis + tension report + plan-deepen. Business confidence 4.5/10. Zero customer conversations is #1 risk. Reporter auth is 5 subtasks. Mastercard VI opportunity. Details: `research/council-product-market-fit-v2/synthesis.md`

- **Research Council V2: Scoring Model (Weights & Measures)** (2026-03-12): Full council — 3 agents + challenge round + synthesis + tension report. V1 formula keeps integer counts (no float weights). Severity determines processing path, not formula impact. Reporter credibility deferred to V2. 5-wave implementation sequence. FICO version fork for score versioning. 9 triple-convergence findings. Details: `research/council-scoring-model-v2/synthesis.md`

- **Expedition: Trust Lifecycle Design** (2026-03-12): 5-team expedition + 3 validators. Status labels, sandbox/testing, review tiers, fairness/recovery, interaction metadata. Phase 2 (cross-validation) complete. Synthesis pending. Key blockers: fractional weights, reporter bootstrapping, patient attacker vector. Details: `research/expedition-trust-lifecycle/`

- **Future Expedition Ideas** (2026-03-10): Agent reviews ecosystem, privacy mode UX, Submantle as payment processor. Details: `research/future-expeditions.md`

## Reference

- **Competitive Landscape** (2026-03-11): 20+ companies analyzed. HUMAN Security is closest behavioral competitor (web-layer only). Mastercard Verifiable Intent is complementary. No one builds portable behavioral trust at OS/device layer. Details: `research/expedition-trust-layer/team-4-marketplace-competitors-findings.md`

- **Trust Formula** (2026-03-11, corrected 2026-03-12): Beta Reputation with Laplace smoothing — trust = (total_queries + 1) / (total_queries + incidents + 2). Validated by Josang 2002, IoT/MANET/P2P production systems, 3 independent research passes. Initialize at (0,0) = 0.5. Details: `research/expedition-trust-layer/team-3-behavioral-trust-science-findings.md`

- **Standards Landscape** (2026-03-11): W3C VC 2.0 finalized May 2025. SD-JWT RFC 9901 finalized November 2025. BBS+ still Candidate. IETF RFC 9711 EAT published April 2025. Three active agent identity drafts (Huawei, AWS/Zscaler/Ping). No behavioral attestation standard exists. Details: `research/expedition-trust-layer/team-2-protocol-architecture-findings.md`

- **Product Analogies** (2026-03-11): Progressive Snapshot (behavioral observation → trust score → economic benefit, avg $322/yr savings). Visa model (trust intermediary, bilateral dependency flywheel). Details: `research/expedition-trust-layer/team-4-marketplace-competitors-findings.md`

- **Anthropic Design Brief** (2026-03-09): Dashboard design language reference. Details: `ANTHROPIC_DESIGN_BRIEF.md`

- **Design Spec** (2026-03-09): Dashboard technical specification. Details: `DESIGN_SPEC.md`
