# Codebase Analyst Findings: Product-Market Fit Council
## Date: 2026-03-12
## Role: Codebase Analyst
## Council: Who Pays for Agent Trust — and What Exactly Are They Buying?

---

## Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Demo Readiness | 3/10 | Trust bureau story is present but fragile without seeded data |
| Integration Simplicity | 6/10 | REST API is clean; story is buried by missing auth on incident reporting |
| Functional Completeness (trust layer) | 5/10 | Formula runs on real data; no auth middleware, no velocity caps, no soft delete |
| Functional Completeness (awareness layer) | 7/10 | Process scan, device discovery, query endpoint all working |
| Actionability for Customer | 4/10 | Businesses can query trust scores; the scores are empty and ungameable-but-also-meaningless |
| Architecture Integrity | 7/10 | Modules cleanly separated; data model is sound; known technical debt explicitly logged |

---

## Question 1: What Can a Customer Actually USE Today?

### Endpoint-by-endpoint assessment

**`GET /api/health`** — Works. Returns version string. Not customer-facing value, but useful for ops.

**`GET /api/status`** — Works. Returns a live process count, identification rate, category breakdown, and list of critical processes. If a brand called this right now, they would get a real answer about what's running on the device running Submantle. This is genuine value for the awareness use case. The limitation: it describes *this machine*, not any agent's behavior. No connection yet between what's running and what an agent's trust score means.

**`GET /api/query?process=X`** — Works. Returns "what would break if process X stopped." This is the most evocative endpoint — it answers the Replit incident question directly. If someone is evaluating an agent that wants to kill a process, this tells them the blast radius. Anonymous access works. Authenticated access records a query toward trust score. The problem: nobody knows this endpoint exists, and there's no documentation of what to pass in `process`.

**`GET /api/devices`** — Works. Returns ARP-discovered LAN devices with manufacturer guesses and hostname resolution. Lightweight, no root required. Value is real for the awareness/mesh story. Not connected to trust layer.

**`POST /api/privacy/toggle` and `GET /api/privacy/status`** — Work. Real off switch, persisted across restarts. This is a genuine trust signal for the device owner.

**`POST /api/agents/register`** — Works. Sends name, version, author, capabilities, gets back a bearer token. HMAC-SHA256, token hash stored (not plaintext). Registration time ISO-8601 round-trips correctly for HMAC verification. This is production-quality cryptography for a prototype. An agent developer could call this today and get a real credential.

**`GET /api/agents`** — Works. Lists all registered agents with metadata. Token hashes excluded from response. No authentication required to list — this is intentional (the directory is public).

**`DELETE /api/agents/{id}`** — Works. Requires Bearer token, verifies ownership. Hard DELETE — this is the known soft-delete debt flagged in the scoring council. History is permanently lost on deregister.

**`GET /api/verify`** — Works. Returns all registered agents with computed trust scores. This is the trust bureau's public face. If a brand called this right now, they would get a list of agents with Beta Reputation scores. The problem: every new agent starts at 0.5, and scores only move if agents have been making authenticated queries. With zero seeded data, every agent in a fresh registry shows `trust_score: 0.5`, `total_queries: 0`, `incidents: 0`. The endpoint works; the data is empty.

**`GET /api/verify/{agent_name}`** — Works. This is the core product call: "how trustworthy is this agent?" Returns trust score, query count, incident count, registration time, last seen, version, author. No authentication required — deliberately public. This endpoint is the thing a brand would integrate. Today it returns real math on real data; the data just doesn't exist yet.

**`POST /api/incidents/report`** — Works mechanically. No authentication on reporter. Any caller can send any `reporter` string and any `agent_name` and the incident is recorded against that agent's score. The scoring council identified this as CRITICAL. From a product standpoint, this means the trust score is currently manipulable by anyone who knows an agent name. This is not a demo-blocker (you control the demo environment) but it is a real-world deployment blocker.

**`record_query()` wiring** — This IS wired in `api.py` at line 402-403: `token = _extract_token(authorization); if token: _registry.record_query(token)`. The HANDOFF note from 2026-03-10 said "record_query() not wired" — that note is stale. It is wired. Query counts accumulate on authenticated calls to `/api/query`.

**Summary of what a brand gets today:** They can call `/api/verify/{agent_name}` and get a mathematically correct trust score with full metadata. The score is 0.5 for every agent with no interaction history. That is the entire product surface for the brand-side customer right now.

**Summary of what an agent developer gets today:** They can register, receive a cryptographic token, make authenticated queries that accumulate toward their trust score, and see their score via the public verification endpoint. This loop is complete and functional.

---

## Question 2: Customer Type Assessment (VISION.md 5 types)

### Customer 1: Agent Developers — 5/10

**What the code supports:** Registration works. Token issuance works. Authenticated query accumulation works. Public score retrieval works. The technical loop is complete: register → query → accumulate → verify.

**What's missing:**
- No API volume pricing or tiering (billing doesn't exist)
- No W3C VC attestation issuance (the portable credential that makes the trust "travel")
- No "Submantle Verified" badge or verification mechanism
- Trust score of 0.5 (unknown) for new agents gives agent developers zero incentive to register until brands demand it
- The value proposition — "higher trust = better rates everywhere" — requires brands to be using Submantle first. The chicken-and-egg problem is structural, not a code gap.

**The real friction:** An agent developer right now asks "why should I register?" The answer is "so brands can check your score." But there are no brands. The loop requires both sides to exist simultaneously. The code is ready for the loop; the loop has no participants.

### Customer 2: Brands/Platforms — 4/10

**What the code supports:** `/api/verify/{agent_name}` returns a real trust score. `/api/verify` lists the full directory. The data model is sound. The API is unauthenticated (free access, no billing) which removes friction for evaluation.

**What's missing:**
- Scores are 0.5 for all new agents (no seeded data, no history)
- Unauthenticated incident reporting means brands cannot trust the scores they see (anyone can sabotage)
- No billing or API key management for brand-side customers
- No threshold query ("show me agents above 0.8") — brands must retrieve all agents and filter client-side
- No `has_history` flag to distinguish new agents from scored-at-0.5 agents
- No SLA, no rate limiting, no uptime guarantee
- CORS is wildcard (`allow_origins=["*"]`) — a brand's security team will flag this

**The honest state:** A brand can query trust scores today. Those scores are mathematically correct but commercially meaningless — no history, no reporter authentication, no agent ecosystem. A brand integration lead looking at this would say "call us when the data exists."

### Customer 3: Device Owners — 7/10

**What the code supports:** This is the most complete customer story in the current codebase. Process awareness works. Device discovery works. Privacy mode works and persists. The dashboard exists. The "what would break" query works. Scan snapshots persist to SQLite so restarts serve last-known state.

**What's missing:**
- Multi-device mesh (sync across devices) — not built
- Clickable device rows in dashboard (noted as NEXT in CLAUDE.md)
- Mobile-responsive dashboard
- No registration passphrase (anyone on localhost can toggle privacy)
- No billing for Pro tier
- 15 identity signatures in `signatures.json` — enough for a demo, thin for real-world recognition

**The honest state:** For a single-device user who runs the daemon locally and uses the dashboard, this is a real product. It does what it says. The demo is compelling for this customer type because data exists immediately (their own processes). This is the most demo-ready use case today.

### Customer 4: Enterprises — 1/10

**What the code supports:** The data model supports multi-agent registrations. The event log is append-only (audit trail). Privacy mode exists. That's it.

**What's missing:** Everything a CISO would require. No SSO. No role-based access. No managed trust policies. No compliance certification. No audit export. No SLA. No support tier. No organization/tenant concept in the data model. The `agent_registry` table has no `org_id` or `tenant` field — every agent is a flat global namespace. An enterprise cannot even define "their" agents vs. others.

**The honest state:** Enterprise is a future-state customer that requires a production rewrite, auth infrastructure, multi-tenancy, and likely a compliance certification. Nothing in the current prototype addresses enterprise requirements.

### Customer 5: Data Buyers — 1/10

**What the code supports:** `scan_snapshots` table has an `analytics_metadata` column reserved for federated analytics. It's always NULL — the column exists architecturally but has no data. The `events` table accumulates behavioral data. That's the extent of it.

**What's missing:** Anonymization pipeline. Aggregation logic. Privacy-safe export. Critical mass of devices (data is only interesting at scale — 1 device produces no market intelligence). The `analytics_metadata` column exists as a forward-looking placeholder; nothing populates it.

**The honest state:** Data buyers require a network effect that cannot exist until the product has meaningful adoption. This customer type is Year 3+. Including it in V1 planning is aspirational, not actionable.

---

## Question 3: The Simplest Possible Integration

### For an Agent Developer (registering and building trust)

```
# Step 1: Register (one call)
POST /api/agents/register
{"agent_name": "my-agent", "version": "1.0.0", "author": "Acme Corp", "capabilities": []}
→ returns {"token": "abc123..."}

# Step 2: Authenticate queries (add one header)
GET /api/query?process=python
Authorization: Bearer abc123...

# Step 3: Check your score (anyone can call this)
GET /api/verify/my-agent
→ returns {"trust_score": 0.73, "total_queries": 47, "incidents": 2, ...}
```

That is 3 API calls and 1 bearer token. The integration is genuinely simple.

**Compared to Stripe:** Stripe's genius is that you get money flowing in 7 lines. The value is immediate — you run the code and a payment happens. Submantle's equivalent would be: you run the code and your trust score starts building. But the value of a trust score requires other parties to check it. Stripe works unilaterally (money moves). Submantle requires bilateral adoption (someone must also care about the score).

This is the fundamental difference. Stripe reduced a bilateral problem (merchant + card network + bank) to a unilateral integration (just add the SDK). Submantle hasn't yet reduced its bilateral problem — agent developer + brand must both participate for the loop to mean anything.

**What the "seven lines of code" moment would look like for Submantle:** An agent developer adds 3 lines to their agent, and as a direct result, they gain access to a brand's premium API tier. The 3 lines of integration has an immediate, observable reward. That reward requires at least one brand to have integrated first. The code is ready for this loop. The loop has no participants.

### For a Brand (checking trust scores)

```
# No registration required today
GET https://submantle.instance/api/verify/agent-name
→ returns trust score + metadata
```

One line. No auth. This is actually Stripe-simple on the brand side. The problem is not the integration — it's that the score is 0.5 for every new agent.

---

## Question 4: Closest Customer to Demoable — and What's Needed

**Closest to demoable: Brands/Platforms** — but only if agent data is seeded first.

Here's why brands win despite the low score: the brand integration is genuinely one API call, no auth required, and the response is human-readable JSON with clear semantics. A brand engineer looking at `/api/verify/some-agent` understands immediately what they're looking at. The conceptual sale — "check this score before giving an agent access" — is clear from the response payload alone.

**What the minimum code is to get from current state to "you could show this to a real buyer":**

1. **Seed 3-5 agents with real interaction histories.** Write a script that registers test agents, makes authenticated queries over several days, and submits one legitimate incident against one agent. This is zero new code — it's using existing endpoints. Result: the `/api/verify` directory shows differentiated scores (0.3, 0.5, 0.7, 0.9) instead of uniform 0.5.

2. **Add `has_history` flag to the verify response.** One-line addition to `compute_trust()` return dict: `"has_history": (q + i) > 0`. Brands can see "genuinely unknown" vs. "scored."

3. **Add reporter authentication to `/api/incidents/report`.** The current endpoint is a public write endpoint with no auth. For a demo, this can be locked to a hardcoded reporter token (the brand demoing the product). This is not production reporter authentication — it's demo safety. Two lines of code.

4. **CORS lockdown to localhost.** Change `allow_origins=["*"]` to `allow_origins=["http://localhost:8421"]` for demo safety.

None of these are architectural changes. They are: a seeding script, one dict key, two lines of auth check, one config change. The demo becomes: "Here are five agents. This one has been making consistent queries for a week with no incidents — trust score 0.91. This one has two incident reports — trust score 0.34. This one registered yesterday — trust score 0.5, has_history: false. Here's how your brand would query this."

That is a real demo. It is honest about what the data is. It shows the loop working.

**The demo requires data, not code.** That distinction matters.

---

## Question 5: What Does the Current Architecture Prevent?

### 1. Multi-tenant / Enterprise use: Prevented architecturally

The `agent_registry` table has no organization concept. Every agent is in a global flat namespace. An enterprise that wants to say "show me trust scores for agents in our org" cannot do this without a schema migration and auth layer rebuild. This is not a small fix — it requires a `organizations` table, foreign keys into `agent_registry`, and an entirely different auth model. The current auth model (bearer tokens per agent, no org concept) cannot be extended to enterprise governance without fundamental redesign. The prototype is explicitly not built for this, and the Go production rewrite should plan for it from the schema up.

### 2. Reporter accountability at scale: Prevented by trust model gap

The incident reporting endpoint works, but reporter authentication creates a second trust problem: who are the reporters and can they be trusted? The scoring model council identified this. The architecture as built treats reporters as anonymous strings. Building reporter reputation (reporter accuracy score) requires a parallel Beta Reputation system for reporters — same formula, different inputs, different table. This is buildable but not a small addition. It's a second product layer inside the first product.

### 3. Portable W3C VC attestations: Not prevented, but not present

The trust score exists. The metadata exists. What doesn't exist is the cryptographic packaging that makes a trust score "travel" — a W3C Verifiable Credential signed by Submantle's DID, provable to any relying party without calling Submantle at all. This is a future feature (Go rewrite), not missing from the prototype by accident. The architecture can support it. The data it would attest to exists. But until it's built, trust scores require calling Submantle. This is not portable — it's centralized verification. The vision of an agent "carrying its trust everywhere" does not exist yet.

### 4. Score decay / temporal trust: Not prevented, but not designed

The current formula has no time dimension. An agent that made 10,000 queries in 2024 and has been dormant since retains a score based on those queries. This is correct per the design decision ("scores change only through interaction, never through time") but it creates the structural failure mode the scoring council's Devil's Advocate identified: a compromised high-trust agent retains its score until incident reports catch up. The architecture can add decay — the formula is a pure function — but the decision to add it has not been made.

### 5. Real-time score streaming / webhooks: Not built, not prevented

Brands integrating trust scores today must poll `/api/verify/{agent_name}`. There is no event-driven push notification ("this agent's score just dropped below 0.6"). The `events` table exists and the event bus fires on incident reports (`INCIDENT_REPORTED` event type). A webhook delivery layer could be built on top of the event bus without changing the trust layer. This is a gap but not a structural blocker — the primitives are there.

---

## The Thing That Is Missing From a PMF Perspective

The codebase implements a trust bureau correctly. The gap is not in the code.

The gap is **demonstration of the flywheel**. The trust bureau model requires two sides: agents that want high scores, and brands that check scores. Neither side has incentive to participate until the other exists. The code is ready for the loop. There are no participants.

This means the product cannot sell itself through documentation or demos built from empty data. The minimum viable thing is not code — it is a seeded ecosystem with at least one brand and one agent completing the loop with real stakes. Until that exists, `/api/verify` returns a row of 0.5s and the pitch requires a leap of imagination rather than evidence.

The scoring model council's tension report correctly identifies this as the highest-confidence strategic finding that the council treated as lowest-priority because it was "outside scope." From a product-market fit perspective, this is the entire question. The code is not the bottleneck. The loop is.

---

## Summary Ratings by Customer Type

| Customer Type | Current Code Supports | Missing for V1 Value | PMF Readiness |
|--------------|----------------------|---------------------|---------------|
| Agent Developers | Registration, token auth, query accumulation, score retrieval | Brands to check scores; W3C VC portability | 5/10 (loop works, no participants) |
| Brands/Platforms | Trust score API, one-call integration, public directory | Seeded data; reporter auth; `has_history` flag | 4/10 (API ready, data empty) |
| Device Owners | Process scan, device discovery, privacy mode, dashboard | Multi-device mesh; richer signatures | 7/10 (most complete today) |
| Enterprises | Event log, audit trail | Everything else (multi-tenancy, SSO, compliance) | 1/10 (wrong architecture for enterprise) |
| Data Buyers | Reserved analytics column | Anonymization, aggregation, network scale | 1/10 (requires adoption at scale) |

---

*Filed by: Codebase Analyst, Research Council on Product-Market Fit*
*Date: 2026-03-12*
