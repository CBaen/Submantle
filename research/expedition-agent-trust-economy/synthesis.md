# Expedition Synthesis: Agent Trust Economy — What to Build, Where Trust Has Monetary Value
## Date: April 12, 2026
## Expedition: 3 researchers + convergence analyst + devil's advocate + GL proxy

---

## All Options Discovered

| # | Option | Convergence | Confidence | Source | Notes |
|---|--------|-------------|------------|--------|-------|
| 1 | Portable behavioral trust gap is real and unsolved | CONVERGED | High | Web + Docs agree, GT confirms no competitor in codebase | Core validation |
| 2 | Financial services is highest-value market | CONVERGED | High | Web + Docs: SEC, FCA, Basel III, NIST critical infrastructure | Agents already deployed for fraud, underwriting, compliance |
| 3 | Healthcare is highest-value market | CONVERGED | High | Web + Docs: HIPAA 2025 mandates operation-level agent audit logs | Hardest regulatory mandate found |
| 4 | EU AI Act creates hard demand (Aug 2, 2026) | CONVERGED | High | Web + Docs: 7% revenue penalty, registry mandates | But: no regulation mandates portable trust SCORES specifically |
| 5 | Identity standards cover WHO, not HOW WELL | CONVERGED | High | Web + Docs: MCP, A2A, OIDC-A all identity-only | Submantle's exact positioning gap |
| 6 | Context-dependence undermines score portability | CONVERGED | High | Web + Docs flag independently | Core intellectual challenge — not solved by anyone |
| 7 | Submantle codebase has critical gaps for seeding | SINGLE-SOURCE | High | Ground Truth: no Sybil prevention, no SDK, unauthenticated incidents | Must fix before any public distribution |
| 8 | Microsoft launched competing trust scoring (Apr 2) | NEW | High | Web Scout: Agent Governance Toolkit, 0-1000 scale, open source | 10 days ago. Enterprise distribution advantage. |
| 9 | AIUC has $15M + Anthropic co-founder angel | NEW | High | Web Scout: trust-unlocks-liability model, ElevenLabs live | Closest existing model to Submantle's vision |
| 10 | ACF Standards selling behavioral certification NOW | NEW | Medium | Docs & Standards: 30 tests, public registry | Direct competitor missed by prior research |
| 11 | MolTrust building portable W3C VC trust | NEW | Medium | Web Scout: Switzerland, Bitcoin Lightning, MCP server | Early but directly overlapping |
| 12 | IETF draft proposes 5-dimension agent payment trust | NEW | Medium | Web + Docs: draft-sharif-agent-payment-trust-00 | Protocol-level competition if ratified |
| 13 | Procurement: 60-70% autonomous by 2028 | SINGLE-SOURCE | Medium | Web Scout only | Large upside, supplier friction is real |
| 14 | Legal: 52% of teams using contract AI | SINGLE-SOURCE | Medium | Web Scout only | "Under attorney supervision" = trust gate |
| 15 | No regulation mandates portable trust scores | DIVERGENT | High | Docs says no; Web implies yes via compliance framing | Key nuance: mandates are for audit LOGS, not SCORES |

---

## The Hard Truths (Devil's Advocate + GL Proxy, Addressed)

### 1. The seeding strategy has no revenue math
The chain from "build free agents" → "agents register" → "businesses pay for verification" was never computed. How many agents before the first business pays? The credit bureau analogy is wrong — Experian scaled by mandate, not virality.
**Status:** OPEN. Revenue arithmetic is the next required analysis step.

### 2. The competitive window is shorter than assumed
"12-18 months" was GL's assumption, not a research finding. Microsoft launched 10 days ago. AIUC has 9 months head start + $15M. ACF Standards is already selling.
**Honest assessment:** Window may be 6-9 months, not 12-18.

### 3. The portability problem is fundamental
If an agent's behavior in Deployment A doesn't predict Deployment B, the SubScore carries no valid information across contexts. This isn't a future challenge — it's a present validity question.
**Status:** OPEN. No one has solved this, including competitors. First-mover who addresses it credibly wins.

### 4. Regulatory demand is real but Submantle can't capture it yet
EU AI Act deadline is August 2026. Businesses facing that deadline will buy from AIUC (auditors + insurance), Microsoft (existing enterprise agreements), or build in-house. Not from a SQLite prototype.
**Honest assessment:** Regulatory demand validates the market, not Submantle's current position in it.

### 5. Neutrality = no distribution partner
Every trust bureau in history distributed through an entity with existing relationships. Submantle's neutrality means no one has a commercial incentive to push it.
**Status:** OPEN. The hardest strategic question. No answer in any research.

### 6. Codebase needs prerequisite work
Not "two critical fixes" — it's: Sybil prevention + authenticated incidents + production deployment + stable URL + SDK/client library + namespace protection. Weeks of work, not days.

---

## What GL Should Do — Recommended Path

### Step 0: Revenue Arithmetic (BEFORE more building)
Compute: What's GL's monthly income floor? At what price would businesses pay for trust verification? (Comparable: AIUC charges for certification + insurance. ACF Standards charges for behavioral testing.) How many paying customers to cover that floor? How many registered agents before the first business cares?

### Step 1: Fix the Prerequisites (2-3 weeks)
- Rate-limit registration endpoint (Sybil prevention)
- Authenticate incident reporters (must have valid agent token)
- Deploy to a real public URL (Railway config exists)
- Update agent.json with production URL
- Build a minimal Python SDK (`pip install submantle`) for one-call registration

### Step 2: Don't Build Free Agents — Partner with Existing Ones
The devil's advocate is right: building free agents is a build cost GL can't afford. Instead:
- The Agent Skills standard (agentskills.io) means 840K+ agents already exist on SkillsMP
- The Anthropic plugin marketplace has thousands of agents
- Claude Code's --agent flag + 30+ community agent repos = agents that already exist
- **Strategy shift:** Don't build agents. Build a registration SDK so EXISTING agents can register with one line of code. Make the SDK a plugin/skill that agent builders install.

### Step 3: Target AIUC's Model, Not Experian's
AIUC proves the revenue model: trust certification that unlocks liability coverage. Businesses pay because the certification reduces their insurance cost. Submantle's SubScore could be the continuous behavioral input that feeds AIUC's certification decision. Partnership, not competition.

### Step 4: First Customer = Agent Platform, Not End Business
Don't sell to financial services companies (they'll buy Microsoft). Sell to agent PLATFORMS — the companies building and deploying agents who need their agents to carry trust credentials. They have the incentive (differentiation) and the distribution (every agent they deploy auto-registers).

---

## Open Questions
1. Revenue arithmetic: income floor → pricing → customer count → agent count threshold
2. Portability validity: does behavioral trust transfer across deployment contexts?
3. Distribution partner: who has commercial incentive to bundle Submantle?
4. AIUC relationship: partner or competitor?
5. Microsoft positioning: how does Submantle differentiate above the free open-source baseline?

---

## GL Proxy Notes (Transparency)
- The $236B WEF figure is the AI agent economy broadly, not trust infrastructure TAM
- "12-18 month window" was GL's assumption — evidence suggests 6-9 months
- No regulation mandates portable trust scores specifically — only audit logs and process documentation
- HIPAA mandate claim needs source URL verification before external use
