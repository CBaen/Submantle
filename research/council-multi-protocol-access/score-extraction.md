# Score Extraction: Multi-Protocol Access Strategy
## Date: 2026-03-12
## Extracted by: Orchestrator (Phase 4)

---

## Shared Dimensions (cross-agent comparison)

| Shared Dimension | Codebase Analyst | External Researcher | Devil's Advocate | Spread |
|-----------------|-----------------|---------------------|------------------|--------|
| Overall Risk | 9/10 | 8/10 (Approach B) | 2/10 | **7** |
| Reversibility | 10/10 | 10/10 (Approach B) | 5/10 | **5** |
| Evidence Confidence | 10/10 | 9/10 (Approach B) | 7/10 | **3** |

**Note on scoring convention:** Higher score = more favorable (10 = lowest risk / highest reversibility / highest confidence). The Devil's Advocate inverts this in their role-specific dimensions (lower = worse), but shared dimensions use the same scale across all agents.

---

## Role-Specific Dimensions

### Codebase Analyst

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Feasibility | 9/10 | Service layer already protocol-agnostic. AgentRegistry has zero HTTP imports. |
| Blast Radius | 9/10 | MCP/CLI are additive — zero changes to core modules |
| Pattern Consistency | 9/10 | Clear template from api.py's thin adapter pattern |
| Dependency Risk | 9/10 | No upstream dependencies change. SQLite WAL handles concurrency. |

### External Researcher

**Approach B: REST + MCP via fastapi-mcp (primary recommendation)**

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Relevance | 10/10 | Directly addresses agent access with minimal effort |
| Maturity | 8/10 | fastapi-mcp v0.4.0, 11.7k stars. Not v1.0, but battle-tested |
| Community Health | 9/10 | High activity, multiple contributors, strong FastAPI ecosystem |
| Integration Effort | 9/10 | 3 lines of code. Auth passthrough built-in. |

**Other approaches scored:** REST only (safe but insufficient), REST+MCP+CLI (moderate, defer CLI), Exchange Hub (rejected, 3/10 risk), Open+Gated (correct model, 7/10 risk)

### Devil's Advocate

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Failure Probability | 3/10 | High probability of shipping with exploitable gaps or incomplete |
| Failure Severity | 3/10 | Security incident in trust infrastructure is existential |
| Assumption Fragility | 2/10 | Central assumptions (MCP is right, CLI serves need, neutral=multi-protocol) are unverified |
| Hidden Complexity | 2/10 | Visible: "add MCP." Hidden: auth/rate-limiting/testing across all protocols |

---

## Challenge Round Score Revisions (proposed, not adopted)

| Agent | Dimension | Original | Proposed Revision | Proposed By | Reasoning |
|-------|-----------|----------|-------------------|-------------|-----------|
| CA | Overall Risk | 9/10 | 5/10 | Devil's Advocate | "If it means risk to the project, closer to 5" — captures deployment, strategic, maintenance risk |
| ER | Evidence Confidence | 9/10 | 7/10 | Devil's Advocate | fastapi-mcp works ≠ fastapi-mcp tracks SDK v2 on Submantle's timeline |
| DA | Reversibility | 5/10 | 8-10/10 | External Researcher + Codebase Analyst | fastapi-mcp = 3-line mount/unmount. Pre-publication, reversibility is near-10 |
| ER | Reversibility | 10/10 | 8/10 | Devil's Advocate | Implementation reversibility ≠ deployment reversibility. Once external agents integrate, removal is breaking. |

---

## Key Score Tensions

1. **Overall Risk spread of 7 points** — CA sees implementation risk (low), DA sees project risk (high). These measure different things. Synthesis must distinguish implementation risk from ecosystem/strategic risk.

2. **Reversibility spread of 5 points** — Pre-publication vs. post-publication. Both positions are defensible for their timeframe. Resolution: reversibility is ~10 before publication, ~5-8 after.

3. **Evidence Confidence spread of 3 points** — CA and ER have high confidence in their evidence (codebase lines, library docs). DA has lower confidence because the assumptions underlying the recommendation (SDK stability, auth passthrough for HMAC) are unverified. Both positions are valid.
