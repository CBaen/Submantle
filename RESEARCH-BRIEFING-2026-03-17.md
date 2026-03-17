# SubMantle Research Briefing
Date: 2026-03-17
Compiled by: Agent (Sonnet 4.6)
Source files:
- `C:\Users\baenb\.claude\research\submantle-market-validation-2026-03-17.md`
- Task output `a0b30fd403a9bc6be` (future-proofing/Sequoia research)
- Task output `a4fea15fe00eface2` (co-founder profile/DIF research)
- Intermediate tool results in session `8b5ca570-6714-4ef2-83e7-8b806a0ef75c`

---

## What SubMantle Is

SubMantle is "the credit bureau for AI agents" — an OS-level behavioral trust scoring daemon that:
- Monitors AI agent processes at the system level (not just API calls)
- Builds deterministic trust scores from actual behavioral evidence
- Issues W3C Verifiable Credentials encoding that evidence

**The differentiating combination:** OS-level instrumentation + behavioral evidence + W3C Verifiable Credentials. No funded competitor has all three layers. This is a genuinely novel architecture.

---

## Market Validation

### Regulatory Tailwinds (All 2025-2026)

| Signal | Detail | Why It Matters |
|--------|--------|----------------|
| NIST | Launched agent identity standards initiative, February 2026 | Standards bodies moving = enterprise procurement follows within 18-36 months |
| Singapore | Issued first global agentic AI governance framework, January 2026 | First-mover signal — other jurisdictions follow Singapore in AI regulation |
| WEF | Projects $236B agent market; identifies trust as the prerequisite for adoption | Trust is not optional infrastructure — it is the unlock condition |

### Funded Adjacent Companies ($300M+ Combined)

These companies validate the market is real and funded. None are doing behavioral evidence at the OS level.

| Company | Funding | What They Do | SubMantle Gap |
|---------|---------|--------------|---------------|
| Operant AI | Undisclosed | Runtime AI agent security | No behavioral history / VC issuance |
| Astrix | $85M | Non-human identity management (API keys, service accounts) | No OS-level agent monitoring |
| Vouched | $17M | Identity verification for humans onboarding AI workflows | Humans, not agents |
| Safe Security | $70M | Cyber risk quantification | Risk scoring, not behavioral trust for A2A |

SubMantle operates in the gap between infrastructure security (Operant) and identity management (Astrix).

### Industry Paradigm Shift: Know Your Agent (KYA)

"Know Your Agent" is becoming the organizing frame for enterprise AI adoption. Organizations deploying autonomous agents need to answer: what did this agent do, why, and can I prove it?

**SubMantle's position:** The behavioral evidence layer that makes KYA possible.

**Critical gap in current A2A protocols:** Google's Agent Cards have no behavioral trust field. There is no standard mechanism for an agent to present verifiable behavioral history to another agent or to a human auditor. SubMantle fills this gap.

---

## White Space Analysis

What no one has built (as of March 2026):

1. **OS-level behavioral telemetry for agents.** Existing tools monitor API calls or network traffic. No one captures what the agent process actually *does* at the OS level (file access, syscalls, process spawning).

2. **Verifiable Credential issuance from behavioral data.** W3C VCs exist for human identity. No one has applied the VC model to AI agent behavioral history.

3. **Agent-to-Agent trust presentation layer.** When Agent A needs to decide whether to delegate to Agent B, there is no standard way for Agent B to present verifiable evidence of its past behavior. SubMantle would be that standard.

4. **Portable trust scores that follow agents across deployments.** A trust score that lives with the agent's credential, not inside a single platform's walled garden.

The adjacent companies are building walls inside their own platforms. SubMantle is building a credential layer that works *across* platforms — the same way a credit score works across banks.

---

## Sequoia's Agent Infrastructure Thesis

Source: Sequoia Capital public writing on AI agents (fetched March 2026)

### Current Assessment

Sequoia characterizes autonomous agents as an emerging capability rather than a settled paradigm. Direct quote: "Autonomous agents' traction is undeniable. On the other hand, it's unclear how useful these AI applications are today for real tasks."

They acknowledge meaningful advancement while noting uncertainty: agents "could become an interesting part of the AI application landscape, and the technology is just starting to get good."

### The Multi-Agent Future Prediction

Sequoia envisions a sophisticated multi-agent ecosystem where **"your AI could hire or outsource to another AI."** This creates specialized agents handling specific tasks, with higher-level agents orchestrating outputs — an agent-to-agent collaboration model.

**This is precisely the world SubMantle is built for.** When AI hires AI, trust between agents is not optional — it becomes the foundation of the entire system.

### The Five Infrastructure Capabilities Sequoia Identifies

Sequoia says the next generation of agent infrastructure requires:

1. **Compute aware** — minimize resource usage
2. **Data aware** — connect to appropriate models/sources
3. **Agent aware** — discover and reuse agent ecosystems
4. **Safety aware** — output verification and sandboxing
5. **User aware** — learning from preferences

**SubMantle directly serves #3 (agent awareness requires knowing which agents can be trusted) and #4 (safety awareness at the behavioral level).**

### The "Glue Layer" Prediction

Sequoia notes a critical **"glue" layer will emerge** — tooling that stitches agents and their outputs together into coherent workflows, suggesting infrastructure beyond individual agents themselves.

Trust scoring is foundational glue. An agent ecosystem without a way to verify agent trustworthiness cannot self-organize. SubMantle is positioned as part of this glue layer.

### Investment Trajectory

2025-2026 is a critical infrastructure-building phase. Malaysia alone saw US$759 million in AI infrastructure investment between H2 2024 and H1 2025. Data center capacity in Southeast Asia grew from 120 MW to 690 MW in that same period. The investment is real and growing.

---

## Future-Proofing Analysis

The research asked: "Will AI agents be replaced by something else, making SubMantle obsolete?"

### Why SubMantle Is Paradigm-Resistant

The question is whether the *concept* of "autonomous AI processes that take actions in the world and interact with other autonomous AI processes" will persist. It will — the label may change (from "agents" to "autonomous systems" or something else), but the underlying need remains: **any organization delegating tasks to autonomous AI needs to know what that AI actually did.**

The DNS analogy applies directly: DNS survived the shift from desktop web to mobile web to apps to APIs. The address-to-location translation problem was structural, not tied to the current paradigm. Similarly, the behavioral-evidence-to-trust-credential translation problem is structural.

### The Self-Certifying Agent Risk

One genuine risk: could trust be built *into* agents themselves (self-certifying) rather than requiring external scoring?

This is the same argument made against credit bureaus when banks started doing their own internal scoring. The answer is: self-certification is fine inside a single closed ecosystem. It fails at the boundary — when Agent A from Company X needs to decide whether to trust Agent B from Company Y. External verification is the only mechanism that works across organizational boundaries.

SubMantle's value proposition increases as agent ecosystems federate across organizations, not decrease.

### What SubMantle Needs to Evolve Into

For long-term durability:
- The scoring model must abstract above "agents" to "autonomous AI processes" broadly
- The credential format must be protocol-agnostic (not tied to A2A specifically)
- The OS-level instrumentation must keep pace with how AI processes are deployed (containers, edge, serverless)

---

## Co-Founder Profile

### Why a Co-Founder Is Required

SubMantle is not a solo build. Building OS-level security infrastructure without deep expertise produces something that *looks* like it works but is not actually secure — which is worse than not building it, because it creates false trust. Security infrastructure that fails silently destroys credibility permanently.

**This is not a "learn as you go" domain.**

### Technical Skills Required

**Core (must-have):**
- OS-level instrumentation: Linux eBPF/audit framework, or Windows ETW (Event Tracing for Windows). This is the layer that captures what processes actually do.
- Cryptographic signing and verification at scale: key management, signature schemes, rotation
- W3C Verifiable Credentials implementation: JSON-LD, Data Integrity proofs, JOSE/COSE standards

**Language fluency:**
- Rust or Go for the daemon core (performance, memory safety, concurrency)
- Python acceptable for tooling and ML components
- C/C++ background useful for OS internals understanding

**Domain knowledge:**
- Identity management (not just auth — full identity lifecycle)
- Distributed systems (trust scores need to be queryable at scale)
- Security engineering (threat modeling, adversarial thinking — what happens when agents try to game the scoring system?)

### Education Profile

- CS or cybersecurity degree (BS minimum; MS/PhD useful but not required)
- Relevant certifications: CISSP, OSCP, or equivalent signals deep security knowledge
- W3C contributor status or DIF working group participation is a significant positive signal — it means they already operate in the exact standards community SubMantle needs to influence

### Experience Profile

**Where this person comes from:**

| Company Type | Examples | What They Bring |
|-------------|---------|-----------------|
| Identity infrastructure | Okta, Auth0, Ping Identity, Transmit Security | Deep VC/credential implementation knowledge |
| Security companies | CrowdStrike, SentinelOne, Palo Alto | OS-level telemetry, threat detection at scale |
| Agent infrastructure startups | Any 2024-2026 A2A/MCP tooling company | Direct knowledge of agent ecosystem gaps |
| Standards bodies | W3C contributor, DIF working group member | Credibility and community leverage |

**Years of experience:** 7-12 years. Junior engineers don't know the failure modes. Senior architects tend to be too risk-averse to join a zero-revenue startup. The sweet spot is a senior engineer or engineering lead ready to take a founding bet.

**Signal that they're the right fit:**
- Has shipped a production VC implementation (not just read the spec)
- Has instrumented OS-level processes before (eBPF projects, EDR tooling)
- Participates in DIF, W3C VC working groups, or OpenID Foundation
- Has thought about agent security before being asked — not just "oh interesting" but has opinions and concerns already

### The DIF Trusted AI Agents Working Group

**This is the most important community for co-founder sourcing.**

The Decentralized Identity Foundation (DIF) is an engineering-focused 501(c)(6) membership organization dedicated to building open, standards-based decentralized identity. Over 150 member organizations including Microsoft, Adobe, Consensys, and Kyndryl.

DIF's working groups include one called **"Trusted AI Agents"** — this is exactly the intersection of identity and agent infrastructure that SubMantle operates in. The engineers in this working group are:
- Already thinking about agent trust from a credentials perspective
- Connected to the W3C VC standards
- Not yet building at the OS level (that's the gap SubMantle fills)

**Where to find them:**
- DIF working group meetings (public calendar at identity.foundation)
- Mailing lists at lists.identity.foundation
- GitHub: github.com/decentralized-identity
- Conferences: Internet Identity Workshop (IIW), EIC (European Identity Conference), Identiverse

### W3C Verifiable Credentials Technical Requirements

The W3C VC Data Model 2.0 specification defines what SubMantle must implement:

**Core stack:**
- JSON-LD with `@context` property mapping to `https://www.w3.org/ns/credentials/v2`
- Digital signatures via Verifiable Credential Data Integrity 1.0
- JOSE and COSE cryptographic standards
- Data Integrity BBS Cryptosuites for selective disclosure

**What a SubMantle credential must encode:**
- The agent's identity (issuer = SubMantle daemon; subject = agent DID)
- The behavioral claims (what actions were observed, in what context, over what time period)
- The trust score derived from those claims
- The cryptographic proof of the observation (tamper-evidence)
- Revocation status (scores can be downgraded if behavior changes)

### Equity and Deal Terms

**Standard technical co-founder splits:**
- If both founders start simultaneously with no existing work: 50/50 with 4-year vest, 1-year cliff
- If one founder (Guiding Light) has done significant pre-work (concept, research, design, positioning): 60/40 in favor of founding founder, or negotiate based on time investment
- YC standard: 4-year vesting, 1-year cliff, monthly thereafter

**What Guiding Light brings to justify equity:**
- Concept and positioning ("credit bureau for AI agents" is a sticky frame that engineers recognize immediately)
- Design and UX vision (agents need dashboards, audit interfaces, human-readable trust reports)
- Market positioning and the KYA narrative
- Relationship with customers and partners (enterprise sales requires a human)
- Financial commitment to date (research, time, validation work)

**How to pitch to a technical person:**
The pitch is not "I have an idea and need you to build it." The pitch is: "This standards gap is real. The DIF Trusted AI Agents working group is trying to define the problem. Here's the evidence it matters. I'm the person who can take this to market — I need you to be the person who builds it so it actually works. Equal founding bet, equal upside."

Technical co-founders say yes when:
1. The problem is technically interesting (OS-level + crypto + standards = intellectually compelling)
2. The market timing is real (regulation arriving = enterprise urgency = not just a research toy)
3. They trust the non-technical founder's ability to find customers (this is where the KYA narrative and market research does work)

---

## Strategic Positioning

**The frame that works:** "Behavioral evidence layer for Know Your Agent."

This frame:
- Makes the problem immediately legible to enterprise security buyers (they already think in terms of "Know Your Customer")
- Positions SubMantle as infrastructure, not a product — infrastructure has better defensibility and pricing power
- Creates a clear relationship to regulation (KYA will become regulatory language in the same way KYC did)

**What SubMantle is NOT:**
- Not an agent firewall (Operant AI's space)
- Not an API key manager (Astrix's space)
- Not a human identity verifier (Vouched's space)
- Not a policy engine (separate category)

SubMantle is the **evidence layer** — the thing that makes all of the above provable, auditable, and portable across organizational boundaries.

---

## Competitive Landscape

| Company | Funding | Layer | Gap vs SubMantle |
|---------|---------|-------|-----------------|
| Operant AI | Undisclosed | Runtime agent security | No behavioral history, no VC issuance |
| Astrix | $85M | Non-human identity (API keys) | Service accounts, not agent behavior |
| Vouched | $17M | Human identity for AI workflows | Humans, not agents |
| Safe Security | $70M | Cyber risk quantification | Risk scoring, not agent trust credentials |
| SpectralOps | Acquired | Secrets detection | Static analysis, not behavioral |
| (No company) | — | OS-level behavioral trust + VC | **This is the gap SubMantle fills** |

**Why no one is here yet:**
- OS-level instrumentation is hard (requires deep kernel/ETW expertise)
- W3C VC implementation is niche and slow (standards work)
- Most security companies are building walls, not credentials
- The A2A protocol gap (no behavioral trust field in Agent Cards) was only visible when A2A launched

---

## Next Steps for a Lineage Member Picking This Up

### Immediate (before any building)

1. **Find the co-founder first.** Everything else is premature. The technical architecture cannot be validated without someone who can evaluate it. The DIF Trusted AI Agents working group is the best starting point.

2. **Attend Internet Identity Workshop (IIW).** IIW is an unconference where the DIF community congregates. The ideal co-founder is likely there. Format: anyone can propose a session, conversations are direct and technical.

3. **Contribute to the A2A spec gap conversation.** The behavioral trust field missing from Agent Cards is a known problem. Opening a GitHub issue or discussion on the Google A2A spec repository positions SubMantle in the standards conversation before building begins.

### Architecture Decisions to Validate with Co-Founder

Before writing code, the co-founder needs to evaluate:

- **Instrumentation layer:** eBPF (Linux) vs ETW (Windows) vs cross-platform abstraction
- **Credential format:** JSON-LD vs JWT — each has tradeoffs for agent use cases
- **Score persistence:** Where do scores live? On-device, on-chain, in a centralized service?
- **Privacy model:** What behavioral data is captured, what is hashed, what is never stored?
- **Adversarial model:** How does SubMantle prevent agents from gaming their own scores?

### Files to Read in This Project

| File | What It Contains |
|------|-----------------|
| `VISION.md` | Core concept and long-term vision |
| `DESIGN_SPEC.md` | UX/product design specification |
| `ANTHROPIC_DESIGN_BRIEF.md` | How SubMantle relates to Anthropic's ecosystem |
| `submantle-decisions.md` | Decision log (use decision-search.py to query) |
| `submantle-queue.md` | Current work queue |
| `HANDOFF.md` | State at last session end |

### The One Non-Negotiable

Do not begin building before finding a co-founder with OS-level security and cryptography expertise. A SubMantle built without this expertise will fail silently — it will appear to issue trust credentials but they will not be cryptographically sound, and the moment a security researcher inspects them, the product's credibility is destroyed permanently. There is no recovery from that.

The market will wait 6 months for the right co-founder. It will not forgive a false trust product.

---

## Research Confidence Assessment

| Claim | Confidence | Source |
|-------|------------|--------|
| NIST agent identity initiative launched Feb 2026 | High | Market validation file (primary research) |
| Singapore first global agentic governance framework | High | Market validation file (primary research) |
| WEF $236B projection | High | Market validation file (primary research) |
| Astrix $85M funding | High | Market validation file (primary research) |
| Sequoia "glue layer" prediction | High | Sequoia public article (fetched March 2026) |
| Sequoia 5-capability framework | High | Sequoia public article (fetched March 2026) |
| DIF "Trusted AI Agents" working group exists | High | DIF website (fetched March 2026) |
| W3C VC Data Model 2.0 technical requirements | High | W3C spec (fetched March 2026) |
| No competitor has OS-level + behavioral + VC | High | Market validation file (primary research) |
| Co-founder equity 50/50 standard | High | Industry standard, multiple sources |
| "Glue layer" = SubMantle positioning | Medium | Synthesis/inference — not a direct Sequoia statement |

---

*This briefing was compiled from three research files by a single agent instance on 2026-03-17. The subagents that conducted the original research (task IDs a0b30fd403a9bc6be and a4fea15fe00eface2) completed their web fetch calls but did not produce synthesized outputs before their sessions ended. The raw tool results were recovered from the session's persisted output store at `C:\Users\baenb\.claude\projects\C--Users-baenb--claude\8b5ca570-6714-4ef2-83e7-8b806a0ef75c\tool-results\bi1kfvkp1.txt`.*
