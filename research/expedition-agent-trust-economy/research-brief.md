# Research Brief: Agent Trust Economy — What to Build, Where Trust Has Monetary Value
## Date: April 12, 2026
## Project: Submantle

### Problem Statement
GL has a working trust bureau prototype (Submantle) but zero registered agents and zero customers. The strategy is to build FREE agents that seed the network, making the trust infrastructure (Submantle) the revenue driver. But nobody has answered: what specific agents do people actually want for high-trust interactions, where does trust verification have the most monetary value, and how do you distribute agents at scale to millions?

### Expected Outcome
A clear answer to three questions:
1. What specific agent types should GL build first (the free agents that seed Submantle)?
2. What businesses would pay for trust verification of those agents (Submantle's revenue)?
3. How do you distribute free agents at massive scale (the seeding mechanism)?

### Current State
- Working FastAPI prototype with agent registration, SubScore computation, Stripe billing, 264 passing tests
- MCP surface (7 endpoints), A2A agent card, llms.txt
- Zero real agents registered, zero customers, zero production deployment
- 5 expeditions + 4 research councils already completed on product-market fit and architecture
- Queue items: license (BSL), 90-day success metric, first customer persona, Anthropic conversation — all unresolved

### Constraints
- Submantle NEVER acts/enforces (Visa model — it labels, brands decide)
- Deterministic scoring only (Beta Reputation formula, no ML — stays outside EU AI Act)
- Credit bureau model: agents register free, businesses pay for trust verification
- On-device computation, privacy by architecture
- 12-18 month competitive window before well-funded players fill the gap
- GL is solo founder, unemployed, needs revenue path

### Destructive Boundaries
- Do NOT propose changing Submantle's architecture or scoring model
- Do NOT re-litigate settled design decisions (see CLAUDE.md)
- Do NOT propose Submantle becoming an agent itself (it's infrastructure)

### Failed Approaches
- Previous research councils flagged "zero customer conversations" as #1 risk — still unresolved
- No co-founder with cryptography expertise found (W3C VC issuance blocked)
- No production deployment exists

### Specific Questions for Researchers
1. What AI agents are people ALREADY using for financial transactions, legal work, healthcare, procurement, or data access? Names, repos, companies, products.
2. What infrastructure gaps exist for running agents at scale? Where do agents break down in production?
3. Where does trust verification create the most MONETARY value? Which industries pay the most for trust signals?
4. What distribution channels exist for free agents? (Anthropic plugin marketplace, Agent Skills standard, npm, PyPI, app stores?)
5. Who would be Submantle's first paying customer? Not "everyone" — a specific role at a specific company type with a specific pain point.
6. What regulations or compliance requirements MANDATE trust verification for AI agents? (EU AI Act, financial regulations, healthcare HIPAA, etc.)
7. What existing trust/identity infrastructure do agents use today? (OAuth, API keys, certificates, nothing?)
8. How big is this market? What's the TAM for agent trust verification?
