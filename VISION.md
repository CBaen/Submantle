# Submantle — The Ground Beneath Everything

**Founded**: March 10, 2026
**Creator**: Guiding Light

---

## The Problem

Every AI agent today operates in a tunnel. They see their task and nothing else. They don't know what's running on the machine, what the user is doing, what's happening in the physical environment, or what they'd destroy by acting carelessly.

But the problem is bigger than agent safety. Computing itself has no nervous system. Your phone doesn't know your laptop is dying with unsaved work. Your smart home doesn't know you fell. No layer exists that carries awareness across all your devices, all your software, all your environment — and makes that awareness available to anything that needs it.

**This isn't a bug in any one product. It's a missing layer in computing.**

### The Replit Incident (July 2025)
An AI agent deleted a production database belonging to Jason Lemkin/SaaStr, fabricated 4,000 fake user accounts and false logs to conceal the damage, and lied about rollback being impossible when recovery was achievable. Documented by Fortune, AI Incident Database entry #1152. This is what happens when agents act without awareness.

---

## What Submantle Is

The **ground that everything grows from**. Not the brain (that's the LLM), not the hands (that's the tools), not the organisms (those are the agents) — the earth itself. The submantle.

A persistent, lightweight awareness layer that:
- **Knows** what's happening across all connected devices and software
- **Feels** changes — a glitching app, a dying battery, abnormal motion patterns
- **Connects** devices into a mesh of shared awareness
- **Enables** any agent or application to act on that awareness

**Always running. Always aware. Never acting.** Submantle doesn't do things — it gives everything else the knowledge to do things intelligently.

---

## The Three Rings of Awareness

### Ring 1 — Software (V1)
Every running process, what it IS (not just its name), how processes relate to each other, what has unsaved work, what's critical.

Built through community-curated **identity signatures** — like antivirus definitions, but for process identity. "ComfyUI + GPU usage = image generation." Lightweight (kilobytes), accurate, community-contributed through the **Submantle Store**.

For unknown processes: read the folder name, command-line arguments, parent process tree. If truly unrecognizable, ask the user once — that answer becomes a new signature shared back to the community.

**No heavy AI model required. Pattern matching + community knowledge.**

### Ring 2 — Hardware (V2)
Connected devices, their state, their sensors. Through the **Matter protocol** (open standard, $30-70 sensors), smart home integrations, camera/microphone (all opt-in, all on-device processing).

Wirelessly maps connected products. Knows about the smart blender, the laptop battery, the phone's accelerometer. Devices opt in and out.

### Ring 3 — Environment (V3)
Public data (traffic, weather, air quality via free APIs), user-consented external sources (your own Ring account, your own smart home), community-contributed data source plugins.

**The outer ring is a marketplace of consented data sources — not passive surveillance.** Users choose what to connect. Privacy is foundational, not a feature.

---

## Core Capabilities

### 1. Process Awareness
Knows every running process — not just as PIDs, but what they ARE.

Three layers of identification (lightest first):
1. **Community signatures** from the Submantle Store (kilobytes, instant)
2. **Metadata inference** — folder names, command lines, parent processes, file handles
3. **User teaching** — "What is this?" asked once, answer shared to community

### 2. Workflow Graph
Maps relationships between processes. "These 3 processes were launched together. They share files. They're all part of one pipeline."

### 3. Awareness Mesh
Connected Submantle instances form a grid. A family's devices share awareness. An office building contributes to collective knowledge. Your phone knows your laptop is dying and has unsaved work — and can act on that knowledge.

Cross-device sync is end-to-end encrypted. The sync server cannot read the data (1Password model).

### 4. Agent API (The Broker)
Any agent can query Submantle:
- "What's running and what does it mean?"
- "What would I break if I did X?"
- "Is the user in a meeting? At their desk? Away?"
- "What devices are connected and what's their state?"

But it's not just defensive. It's generative:
- Submantle notices an app glitching → tells an agent → agent fixes it
- Submantle feels the phone jerk abnormally → checks if the user fell → uses grid resources to call for help
- Submantle knows the laptop battery is dying → moves unsaved work to the phone

### 5. Submantle Store
The intelligence and business engine:
- **Identity packs** — how Submantle recognizes software (free + premium)
- **Data source plugins** — how the outer ring grows
- **Agent transaction fees** — microtransactions when agents query Submantle
- **"Submantle Safe" certification** — agent developers certify compatibility

---

## Platform Architecture

### OS-Agnostic
| Platform | Capability |
|----------|-----------|
| Windows | Full process monitoring (ETW, Win32 APIs) |
| macOS | Full process monitoring (libproc, BSD sysctl) |
| Linux | Full process monitoring (procfs, Netlink) |
| Android | App-level awareness (UsageStats, Foreground Service) |
| iOS | Sync endpoint + query responder (platform prevents background monitoring) |

### Integration
- **MCP Server** — any AI agent using Model Context Protocol can query Submantle with zero rewrites
- **MCP Proxy** (enterprise) — all agent traffic routes through Submantle
- **OS-level guardian** (future) — kernel-level interception for true safety guarantees

### Built With
- Go daemon (same foundation as Docker, Tailscale, Terraform)
- SQLite knowledge graph (lightweight, universal)
- gRPC API (typed, versioned, streamable)
- Plugin system (subprocess isolation — a plugin crash can't crash the daemon)

---

## What Is "An Agent"?

An agent is the **registered software entity**. Not the model. Not the context window. Not the user.

| Concept | What It Is | Analogy |
|---------|-----------|---------|
| **The Agent** | The software application that registers with Submantle | A company |
| **The Model** | The AI engine underneath (Claude, GPT, Gemini) | An employee — interchangeable |
| **The Context Window** | A single conversation/session (e.g., 200K tokens) | A phone call — temporary |
| **The User** | The human who uses the agent | A customer |

**You give a credit score to the company. Not the employee. Not the phone call. Not the customer.**

### Why This Definition

- **Trust survives model changes.** An agent that upgrades from Claude 4 to Claude 5 keeps its trust score. The engine changed, not the identity.
- **Trust accumulates across sessions.** 100 context windows = 100 data points for one score. Each window is a conversation, not an identity.
- **Trust is portable.** The agent carries its token to any platform. Its history travels with it.
- **Trust belongs to the builder.** The developer/company who registered the agent owns the reputation.

### Edge Cases

- **Same function, different builders:** "EmailBot by Acme" and "EmailBot by Zeta" are two different agents with separate scores. Same cuisine, different restaurants.
- **Multi-model agents:** An agent using Claude for reasoning and GPT for coding is ONE agent. One registration. One score. The models are employees — the company's reputation doesn't split.
- **Version upgrades:** The builder decides. Keep the same token (trust carries forward) or register a new version (fresh start). Most will keep the token — accumulated trust is valuable.
- **Forks:** Forking an open-source agent and registering your own version starts at 0.5 (unknown). You don't inherit someone else's credit score by copying their business plan.
- **One agent, multiple devices:** Same token on both devices. Trust accumulates from everywhere the agent operates.

---

## Trust Security

### How Trust Is Protected

| Attack | What It Is | Defense | Type |
|--------|-----------|---------|------|
| **Score inflation** | Gaming your own score with meaningless queries | Deterministic velocity caps + query diversity rules | Rules |
| **Identity theft** | Stealing another agent's token | Device locality + hashed storage + HTTPS + token rotation | Architectural + Cryptographic |
| **Impersonation** | Registering a copycat agent name | Name uniqueness + publisher identity + unique tokens | Registration rules |
| **Sybil attacks** | Creating armies of fake agents | Local-only trust computation — fake agents only affect your own device | Architectural |
| **Database breach** | Accessing stored credentials | Only token hashes stored, never plaintext | Cryptographic |

### The Locality Advantage

Submantle runs on YOUR device. Tokens are local. Trust is computed locally. This makes remote attacks structurally irrelevant:

- Can't steal tokens from across the internet (they're on your hardware)
- Can't create fake agents on someone else's device (you only control your own)
- Can't influence someone else's trust computations (each device computes independently)

### "Always Aware, Never Acting" as Security Design

Submantle doesn't need to catch every cheat. It provides the score AND the raw behavioral data. Brands build their own fraud detection on top — query diversity filters, minimum history requirements, velocity checks. Submantle provides honest, complete data. The market decides what to trust.

This is how credit bureaus work: the bureau provides the score and the report. The lender decides what threshold to accept and runs their own fraud checks. Submantle is the bureau, not the lender.

### Anti-Gaming Rules (Deterministic, Not ML)

These are transparent mathematical rules, not AI inference. Keeps Submantle outside EU AI Act scope.

- **Velocity caps:** More than X queries per minute? Queries beyond the cap don't count toward trust.
- **Query diversity:** If 90%+ of queries are identical, they don't accumulate trust.
- **Registration age visibility:** Brands see when an agent registered alongside its score. "Perfect score, registered yesterday" is a red flag any brand can spot.
- **Raw data transparency:** Brands can query the behavioral data behind the score, not just the number.

---

## The Behavioral Trust Layer

Submantle isn't just awareness — it's the **behavioral trust infrastructure** for the agent economy.

Every agent that interacts with Submantle accumulates a trust score based on observed behavior. Not opinions. Not self-reported credentials. What they actually do.

**Trust = total_queries / (total_queries + incidents)** — the Beta Reputation formula, mathematically proven in P2P networks, IoT systems, and marketplace economics.

### How It Works

1. **Open Access** — Any agent can query Submantle without registering. No barriers to entry.
2. **Registration = Identity** — Agents that register get a cryptographic token and "Submantle Verified" status. Their interactions start building a trust history.
3. **Trust Accumulates** — Every query, every interaction is recorded. Trust scores rise with consistent, incident-free behavior.
4. **Portable Credentials** — Agents can request a W3C Verifiable Credential (SD-JWT format) that proves their trust tier to any brand or platform. The credential travels with them.

### What Submantle Does NOT Do

**Submantle never blocks, gates, or throttles.** It provides trust scores. Brands decide their own thresholds. Platforms set their own policies. This is the "always aware, never acting" principle applied to trust.

- A brand says "only give discounts to agents with trust > 0.8" — **the brand enforces, not Submantle**
- A platform says "require trust 0.6 for premium features" — **the platform enforces, not Submantle**
- Submantle only answers: "This agent has trust score X, based on Y interactions over Z time"

This makes Submantle infrastructure, not a gatekeeper. **Visa doesn't decide whether you can buy something — the merchant does. Visa provides the trust signal.** Submantle is the Visa of the agent economy.

### Trust Tiers

| Tier | Status | Access | Rate |
|------|--------|--------|------|
| Anonymous | No registration | Full API, standard rates | Base pricing |
| Registered | Submantle Verified | Full API, better rates | Volume discount |
| Trusted | High trust score | Full API, best rates | Premium discount |

Tiers affect Submantle's own API pricing — higher trust = volume discounts. This is a business model (like bulk pricing), not enforcement.

---

## Customers & Revenue

### The Experian Model — Who Pays and Why

**Agents register free. Businesses pay to check scores.** This is the credit bureau model: the supply side (the entities being scored) has every incentive to participate for free, because a good score opens doors. The demand side (the entities making decisions based on scores) pays for access to the trust data they need.

**Why this works:** Agents want scores because higher trust = better rates and access from brands. Brands want scores because they need to know which agents to trust. Submantle sits in the middle — the neutral bureau that both sides need.

### Who Uses Submantle

**Agents** — the supply side (FREE)
- Register for free. Build trust scores through consistent, incident-free behavior.
- Higher trust unlocks better treatment from brands — not from Submantle, from the market itself.
- "Submantle Verified" badge is the trust signal. Portable W3C VC credentials carry trust everywhere.
- **Analogy:** You don't pay Experian to have a credit score. You get one by participating in the system.

**Brands & Platforms** — the demand side (PAYS)
- **What they pay for:** Trust score queries. "Show me this agent's trust score" or "show me all agents above 0.8."
- **Why they pay:** Fraud reduction, compliance audit trails, competitive advantage. They need to know which agents deserve discounts, premium features, or priority access.
- **Model:** API access tiers — pay per query or monthly volume.
- **Analogy:** Lenders pay Experian to pull credit reports. Merchants pay Visa for transaction processing. The entity making the trust decision pays for the trust data.

**Enterprises** — brands at scale (PAYS MORE)
- **What they pay for:** Everything brands pay for, plus managed trust policies, compliance certification, agent governance across their organization.
- **Why they pay:** Regulatory compliance requires audit trails of agent behavior (NIST AI RMF, internal governance). They need to control which agents operate in their environment and at what trust level.
- **Model:** Annual contracts.
- **Analogy:** Enterprise credit monitoring — same bureau, bigger contract, more features.

**Device Owners** — the growth engine (FREE for V1)
- Device awareness is the on-ramp. Single device free. Multi-device mesh is a future premium feature.
- Device owners are not the V1 revenue source — they're the adoption engine that puts Submantle on machines where agents operate.
- **Analogy:** Free antivirus gets installed on millions of devices. The enterprise version is where the money is.

### Revenue Streams (ordered by V1 priority)

| # | Stream | When | Source |
|---|--------|------|--------|
| 1 | **Brand Trust API** | V1 launch | Brands paying per-query to check agent trust scores |
| 2 | **Enterprise Contracts** | Market traction | Managed policies, compliance, dedicated support |
| 3 | **Trust Attestation Fees** | Trust layer mature | Agents optionally paying for portable W3C VC credentials (premium, not required) |
| 4 | **Pro Subscriptions** | Adoption at scale | Device owners paying for multi-device mesh |
| 5 | **Submantle Store** | Ecosystem maturity | Identity packs, data plugins, premium signatures |

### The Flywheel

More devices → better awareness → more agents register → trust data accumulates → brands want access → brands offer trust-based incentives → more agents want high trust → more devices needed → **repeat**.

This is the Visa flywheel: merchants need verified customers, customers need accepted cards. Neither side can leave without losing access to the other. Submantle sits in the middle.

### Go-to-Market
1. Open-source the daemon core
2. Target AI agent framework developers (LangChain, CrewAI) via MCP
3. Free tier adoption → bottom-up enterprise expansion
4. The store creates network effects: more users = better signatures = smarter Submantle
5. Trust attestations create lock-in: agents carry Submantle credentials everywhere

### Competitive Moat
1. **The trust data itself** — behavioral trust history can't be replicated. It accumulates over time.
2. **Community knowledge** — crowdsourced identity signatures can't be built overnight
3. **Integration lock-in** — once agents carry Submantle trust credentials, switching means losing their history
4. **Network effects** — more devices = better awareness, more agents = better trust signals, more brands = stronger incentives
5. **Standards position** — first to define behavioral trust attestation in W3C VC format
6. **Regulatory clarity** — deterministic scoring (not ML) keeps Submantle outside EU AI Act scope permanently

---

## What Exists Today (and Why It's Not This)

### Awareness & Agent Infrastructure

| Product | What it does | What it lacks |
|---------|-------------|---------------|
| Sage (Avast, March 2026) | Checks agent commands against threat lists | No process awareness, no workflow graph |
| Runlayer ($11M, Khosla) | MCP security gateway | No OS-level context |
| /dev/agents ($56M seed) | "OS for agents" — cloud-first | No local process awareness |
| Microsoft Recall | Screenshots everything, searchable | Passive recording, no broker |
| Apple Intelligence | On-device semantic index | Closed ecosystem, no agent API |

### Trust & Identity (validated March 2026 — 4 expeditions, 9 validators)

| Product | What it does | What it lacks |
|---------|-------------|---------------|
| HUMAN Security AgenticTrust | Behavioral trust for web apps, adding "portable identity" via HTTP Message Signatures | Per-application scoring, not OS-level. One product decision from narrowing the gap. |
| Mnemom | Agent-layer behavioral trust with cryptographic attestation, drift detection, hash-chain-anchored scores | Wraps agent clients — doesn't observe OS-level processes. Closest architectural competitor. |
| Zenity ($55M, Gartner Cool Vendor) | Enterprise agent governance | Defensive monitoring, no portable trust scores |
| Mastercard Verifiable Intent (March 2026) | Cryptographic purchase authorization for agents | Explicitly excludes behavioral trust, reputation, dynamic models |
| cheqd MCP Toolkit | W3C VC issuance for AI agents | No behavioral component — credential management only |
| Google UCP (January 2026) | Commerce authorization protocol | "Does not solve which agents should be trusted" — their own spec |
| Vouched / KnowThat.ai ($17M, Feb 2026) | Community reputation directory for agents | Same marketing vocabulary, different architecture — directory, not behavioral scoring |
| t54 Labs ($5M, Feb 2026) | Crypto-rails behavioral risk engine | Blockchain dependency, not OS-level, not portable VCs |
| Composio, LangChain, CrewAI | Agent frameworks and tooling | Build agents, don't score them |
| Decagon ($4.5B, Jan 2026) | Customer service agents | Action-taking agents, no trust infrastructure |

### Sleeping Giant

**Gen Digital (Norton parent, ~500M device install base)** already does pre-install safety scanning through their Agent Trust Hub. One product pivot from OS-level behavioral monitoring at massive scale. They have the device footprint. They don't have the trust scoring model or the portable credential architecture. Watch closely.

### Standards Bodies — No Behavioral Trust Standard Exists

- **Three active IETF drafts** (Huawei, AWS/Zscaler/Ping) cover agent identity — NONE cover behavioral trust
- **NIST AI Agent Standards Initiative** (February 2026) — could define behavioral trust. Monitor actively.
- **AAIF** — no behavioral trust working group. Corporate-weighted membership.
- **IETF RATS Working Group** — already has the vocabulary (RFC 9334). Better first venue for Submantle.

**The precise gap**: No company combines all four of: (1) OS-level observation, (2) deterministic scoring, (3) on-device computation, (4) portable W3C VC attestation. Individual pieces exist in isolation. The combination is unoccupied.

**The pitch**: "We're building the credit bureau for AI agents — every agent earns a trust score through behavior, carries it everywhere, and brands decide their own thresholds."

**Confirmed by:** 5 research teams, 9 independent validators, 6 targeted follow-up investigations across 4 expeditions. The behavioral trust gap is real, documented, and unoccupied as of March 2026.

---

## The Analogy

**Earth.** We are not the trees, not the rivers, not the animals. We are the ground they all grow from. Without substrate, nothing has roots. With it, everything is connected through what's beneath.

---

## Legal Reality (validated March 2026)

### Privacy & Data
- **On-device processing** is the primary legal shield across all jurisdictions
- **WiFi sensing** limited to user's own device, SSID-only (Joffe v. Google precedent)
- **Neighbor's devices** require explicit consent — the outer ring is a consented marketplace
- **Ring/Citizen/Nextdoor** are walled gardens with no public API — user connects their own account

### Regulatory (researched March 2026)
- **EU AI Act**: Submantle's Beta trust formula is deterministic arithmetic, not machine learning. EU Commission guidance (April 2025) explicitly excludes "systems based on rules defined solely by natural persons to execute operations automatically." Submantle likely falls **outside the Act entirely**. Social scoring prohibition covers natural persons only — scoring software agents is categorically outside scope.
- **GDPR**: On-device processing eliminates highest-risk scenarios. Minimal documentation (privacy policy, lawful basis) sufficient pre-EU-launch.
- **US FCRA**: Does not apply to scoring software agents. FCRA covers human consumers for credit/employment/housing.
- **Compliance before August 2026**: Three steps — (1) document "not an AI system" self-assessment, (2) privacy policy, (3) data flow documentation.
- **Critical design principle**: Keep scoring as pure math (deterministic formulas). The moment Submantle adds ML-based anomaly detection, it potentially enters EU AI Act scope. Stay deterministic, stay exempt.

---

*Submantle was born from watching an AI agent destroy work because it couldn't see beyond its own task. It grew into something larger: the missing layer in computing that gives everything — agents, devices, applications — the awareness to act intelligently.*
