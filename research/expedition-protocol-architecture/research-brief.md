# Research Brief: Substrate Protocol Architecture
## Date: 2026-03-11
## Project: Substrate

### Problem Statement
We've been building a local awareness prototype, but the real product is a protocol — "its own layer of the internet" for agent behavioral trust. We need to understand what that means technically, how agents actually plug into it, who the relevant players are, and how a protocol achieves global adoption. The founder cannot maintain direction if the architecture isn't clear in plain terms.

### Expected Outcome
A clear architectural blueprint that answers: What IS Substrate technically? How do agents connect? How does it grow with AI? Who else is building adjacent infrastructure? How did other protocols go from idea to global adoption? — all explained so a non-technical founder can use it as a compass to keep the project on course.

### Current State
- Working prototype: Python process scanner, agent registry (HMAC-SHA256), privacy mode, event bus, SQLite, 160 tests
- Trust layer designed but not wired: Beta Reputation formula, W3C VC 2.0 + SD-JWT attestation format, agent identity model
- 3 expeditions + 6 follow-ups completed — validated that the behavioral trust gap is real and unoccupied
- MCP identified as likely integration surface (97M+ monthly SDK downloads)
- Production language will be Go (validated, not yet implemented)

### Project Direction
Substrate is evolving from a local device awareness tool into a protocol-level trust infrastructure for AI agents. Think DNS for trust — any agent can query it, any device can run a node, any platform can verify scores. The prototype proves the concept locally; the protocol makes it global.

Key settled decisions:
- Beta Reputation formula: trust = total_queries / (total_queries + incidents), initialize at (1,1) = 0.5
- W3C VC 2.0 + SD-JWT (RFC 9901) for portable trust attestations
- Agent = registered software entity (not model, not context window, not user)
- Enforcement is NEVER done by Substrate — third parties enforce their own thresholds
- EU AI Act compliance via deterministic-only scoring (no ML)

### Constraints (Non-Negotiable)
1. **Always aware, never acting** — Substrate exposes scores, never enforces. Applies to entire system.
2. **Deterministic scoring only** — Pure math (Beta Reputation), no ML. Keeps us outside EU AI Act.
3. **Privacy by architecture** — On-device processing, E2E encrypted sync, no telemetry.
4. **Lightweight first** — Invisible resource usage. No heavy models.
5. **Agent-first design** — Built for agents as primary users. Humans interact through connectors.

### Destructive Boundaries
- Do NOT recommend ML-based scoring or anomaly detection
- Do NOT recommend centralized data collection architectures that violate privacy-by-architecture
- Do NOT recommend Substrate making enforcement decisions (blocking, gating, throttling)
- Do NOT recommend blockchain-required architectures (Web3 compatible does not mean Web3 dependent)
- The Beta Reputation formula, SD-JWT attestation format, and "always aware never acting" principle are SETTLED
- Do NOT recommend abandoning the existing prototype — it's a valid reference implementation foundation

### Research Angles

**Team 1 — Protocol Architecture Models:** How do internet protocols actually work (TCP/IP, DNS, HTTPS, OAuth, SMTP)? Which network topology fits a behavioral trust layer — peer-to-peer, federated, hub-and-spoke, hybrid? What are the tradeoffs given our constraints (on-device processing, privacy, deterministic scoring)?

**Team 2 — Agent Integration Surface:** How do AI agents actually connect to things today? MCP, OpenAI function calling, LangChain, CrewAI, AutoGen, agent frameworks. What protocols do agents speak? What would make it trivial for any agent to plug into a trust network? What's the SDK/connector model?

**Team 3 — Agent Economy Infrastructure:** Who's building the roads agents will travel? Google UCP, Mastercard Verifiable Intent, Stripe, A16z, OASIS, W3C. What commerce and transaction infrastructure is being built for agents? Where does behavioral trust fit in the agent transaction chain?

**Team 4 — Protocol Adoption Playbook:** How did successful protocols achieve global adoption? HTTPS (Let's Encrypt), OAuth, SMTP, DNS. What's the pattern? What role did reference implementations, corporate sponsors, and developer communities play? What's realistic for a solo founder with a protocol?

**Team 5 — Decentralized Identity & Trust Infrastructure:** What decentralized identity infrastructure is production-ready? DIDs, W3C VC ecosystem, SSI, Ceramic, ION. How do decentralized systems handle trust without centralization? What's hype vs. real? What's compatible with on-device-first architecture?

### Failed Approaches
None explicitly — but the current prototype is a local-only Python app. The gap we're researching is how to go from "works on one machine" to "works for every agent on earth."

### Team Size: 5
Five independent angles that each determine a different facet of the architecture. No overlap — each team's findings feed a different part of the blueprint.
