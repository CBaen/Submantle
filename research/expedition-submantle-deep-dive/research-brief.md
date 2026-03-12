# Research Brief: Submantle Deep Dive
## Date: 2026-03-10
## Project: Submantle

### Problem Statement
Every AI agent today operates in a tunnel. They see their task and nothing else — no awareness of what's running on the machine, what the user is doing, what other agents are active, or what they'd destroy by acting. Beyond software, they have zero awareness of the physical environment. An agent killed hours of image generation work because it blindly terminated all Node processes. This isn't a bug in one agent — it's a missing layer in computing.

### Expected Outcome
A complete understanding of the Submantle opportunity: what exists today that's close, what technology makes it buildable, how agents would integrate with it, what the legal landscape looks like for ambient sensing, who would pay for it, and how to price it. Walk away ready to make architectural and business decisions.

### Current State
A VISION.md document describing the concept. No code, no git repo, no prior attempts. The vision describes:
- An OS-level context layer (daemon/service) that sits between the OS and AI agents
- Five capabilities: process awareness, workflow graph, user intent model, agent API (broker), cross-device sync
- Three rings of awareness: inner (software/processes), middle (hardware/sensors), outer (environment — WiFi signals, public cameras, traffic data, neighboring devices)
- The "substrate" extends beyond the user's own hardware to any reachable data source
- OS-agnostic by design — must work across Windows, macOS, Linux, Android, iOS

### Project Direction
Exploring whether this is a viable product and company. Need to understand feasibility, market, legal landscape, and architecture before committing to build. The creator (Guiding Light) is a designer/creator, not an engineer — the product must be explainable in non-technical terms.

### Constraints
- Must be OS-agnostic (not tied to any single platform)
- Privacy/consent must be foundational, not bolted on
- Must work as middleware (not require OS vendor adoption to launch)
- Must be buildable incrementally (inner ring first, expanding outward)
- Proof of concept should be buildable with available tools (Claude Code, Python, Rust, etc.)

### Destructive Boundaries
- Do not assume Apple/Google/Microsoft cooperation — Submantle must work independently
- Do not propose approaches that require root/kernel-level access on mobile (App Store rejection)
- Do not recommend surveillance-first approaches — consent architecture is non-negotiable

### Research Angles

**Team 1: Competitive Landscape & Prior Art**
Investigate everything that exists today closest to Submantle — process monitors, ambient computing platforms, AI safety layers, agent coordination tools, contextual awareness systems. Map the gaps. Include both commercial products and research projects.

**Team 2: Cross-Platform Architecture**
How to build an OS-agnostic daemon that monitors processes, builds a knowledge graph, and exposes an API. Evaluate languages (Rust, Go, C++), IPC mechanisms, OS-specific APIs (WMI, procfs, BSD APIs, ActivityManager). How do cross-platform tools like 1Password, Docker, or Tailscale solve this problem?

**Team 3: Ambient Sensing & Spatial Awareness**
WiFi sensing technology (presence detection through RF signals), on-device computer vision, audio classification, sensor fusion. What's commercially available vs research-only? What public data APIs exist (traffic cameras, Ring Neighbors, environmental sensors, municipal open data)? What hardware APIs are accessible on each platform?

**Team 4: AI Agent Coordination & Integration**
How would AI agents talk to a broker? Investigate MCP (Model Context Protocol), OpenAI's tool use, agent sandboxing approaches, inter-agent communication standards. What protocols exist for agents to declare intent before acting? How do current agent frameworks handle environmental context?

**Team 5: Privacy, Consent & Legal Frameworks**
Legal implications of accessing external data sources (Ring cameras, traffic feeds, WiFi signals). GDPR, CCPA, surveillance laws across jurisdictions. What consent architectures exist in tech (OAuth-style permission grants, data trusts, federated approaches)? How do products like Life360 or Find My handle this legally?

**Team 6: Market, Customers & Business Model**
Who are the customers — AI agent developers, enterprises, power users, OS platforms? What's the go-to-market? Analyze comparable middleware/platform pricing (Datadog, 1Password, Tailscale, Auth0). What tiered offerings make sense? What's the TAM as AI agents proliferate? Who pays first?

### Team Size: 6
Six independent research angles with no overlap. The scope is broad (technical architecture + ambient sensing + legal + market) and each angle requires deep, independent investigation.

### Failed Approaches
None — this is a greenfield investigation. No prior attempts exist.
