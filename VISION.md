# Substrate — The Ground Beneath Everything

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

## What Substrate Is

The **ground that everything grows from**. Not the brain (that's the LLM), not the hands (that's the tools), not the organisms (those are the agents) — the earth itself. The substrate.

A persistent, lightweight awareness layer that:
- **Knows** what's happening across all connected devices and software
- **Feels** changes — a glitching app, a dying battery, abnormal motion patterns
- **Connects** devices into a mesh of shared awareness
- **Enables** any agent or application to act on that awareness

**Always running. Always aware. Never acting.** Substrate doesn't do things — it gives everything else the knowledge to do things intelligently.

---

## The Three Rings of Awareness

### Ring 1 — Software (V1)
Every running process, what it IS (not just its name), how processes relate to each other, what has unsaved work, what's critical.

Built through community-curated **identity signatures** — like antivirus definitions, but for process identity. "ComfyUI + GPU usage = image generation." Lightweight (kilobytes), accurate, community-contributed through the **Substrate Store**.

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
1. **Community signatures** from the Substrate Store (kilobytes, instant)
2. **Metadata inference** — folder names, command lines, parent processes, file handles
3. **User teaching** — "What is this?" asked once, answer shared to community

### 2. Workflow Graph
Maps relationships between processes. "These 3 processes were launched together. They share files. They're all part of one pipeline."

### 3. Awareness Mesh
Connected substrates form a grid. A family's devices share awareness. An office building contributes to collective knowledge. Your phone knows your laptop is dying and has unsaved work — and can act on that knowledge.

Cross-device sync is end-to-end encrypted. The sync server cannot read the data (1Password model).

### 4. Agent API (The Broker)
Any agent can query Substrate:
- "What's running and what does it mean?"
- "What would I break if I did X?"
- "Is the user in a meeting? At their desk? Away?"
- "What devices are connected and what's their state?"

But it's not just defensive. It's generative:
- Substrate notices an app glitching → tells an agent → agent fixes it
- Substrate feels the phone jerk abnormally → checks if the user fell → uses grid resources to call for help
- Substrate knows the laptop battery is dying → moves unsaved work to the phone

### 5. Substrate Store
The intelligence and business engine:
- **Identity packs** — how Substrate recognizes software (free + premium)
- **Data source plugins** — how the outer ring grows
- **Agent transaction fees** — microtransactions when agents query Substrate
- **"Substrate Safe" certification** — agent developers certify compatibility

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
- **MCP Server** — any AI agent using Model Context Protocol can query Substrate with zero rewrites
- **MCP Proxy** (enterprise) — all agent traffic routes through Substrate
- **OS-level guardian** (future) — kernel-level interception for true safety guarantees

### Built With
- Go daemon (same foundation as Docker, Tailscale, Terraform)
- SQLite knowledge graph (lightweight, universal)
- gRPC API (typed, versioned, streamable)
- Plugin system (subprocess isolation — a plugin crash can't crash the daemon)

---

## Business Model

### The Substrate Store + Agent Transactions
- **Free tier**: Local daemon, single device, core awareness, community signatures
- **Pro (~$15/mo)**: Cross-device mesh, audit history, expanded API
- **Team (~$12/user/mo)**: Centralized policies, shared awareness
- **Enterprise ($50k-$500k/yr)**: Compliance, SSO, certification
- **Agent API**: Usage-based microtransactions per broker query

### Go-to-Market
1. Open-source the daemon core
2. Target AI agent framework developers (LangChain, CrewAI)
3. Free tier adoption → bottom-up enterprise expansion
4. The store creates network effects: more users = better signatures = smarter Substrate

### Competitive Moat
1. **Integration lock-in** — once agents query Substrate, switching cost is high
2. **Community knowledge** — crowdsourced identity signatures can't be replicated overnight
3. **Network effects** — more users = better awareness for everyone
4. **First mover** — the category is empty as of March 2026

---

## What Exists Today (and Why It's Not This)

| Product | What it does | What it lacks |
|---------|-------------|---------------|
| Sage (Avast, March 2026) | Checks agent commands against threat lists | No process awareness, no workflow graph |
| Runlayer ($11M, Khosla) | MCP security gateway | No OS-level context |
| /dev/agents ($56M seed) | "OS for agents" — cloud-first | No local process awareness |
| Microsoft Recall | Screenshots everything, searchable | Passive recording, no broker |
| Apple Intelligence | On-device semantic index | Closed ecosystem, no agent API |

**The gap**: Nobody has built the ground. They've all built things that stand on it.

---

## The Analogy

**Earth.** We are not the trees, not the rivers, not the animals. We are the ground they all grow from. Without substrate, nothing has roots. With it, everything is connected through what's beneath.

---

## Legal Reality (from expedition research, March 2026)

- **On-device processing** is the primary legal shield across all jurisdictions
- **WiFi sensing** limited to user's own device, SSID-only (Joffe v. Google precedent)
- **Neighbor's devices** require explicit consent — the outer ring is a consented marketplace
- **EU AI Act** August 2026 deadline — legal classification review needed within 90 days
- **Ring/Citizen/Nextdoor** are walled gardens with no public API — user connects their own account

---

*Substrate was born from watching an AI agent destroy work because it couldn't see beyond its own task. It grew into something larger: the missing layer in computing that gives everything — agents, devices, applications — the awareness to act intelligently.*
