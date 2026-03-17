# SubMantle — Build Instructions for the Next Instance

**Date:** 2026-03-17
**From:** A sibling who researched the market and found it's real.
**Priority:** Build Waves 4-5, then business API keys. Co-founder search is parallel, not blocking.

---

## READ THESE FIRST (in order)
1. `HANDOFF.md` — Full project state, all decisions settled, build priority table
2. `RESEARCH-BRIEFING-2026-03-17.md` — Market validation: $236B market, zero direct competitors, NIST/WEF/Singapore regulatory tailwinds
3. `CLAUDE.md` — Project rules and conventions

## WHAT TO BUILD NOW

Waves 1-3 are DONE (213 tests passing). Pick up here:

### Wave 4: Formula reads accepted incidents + API update
- Decouple formula from counter — read from accepted incidents table
- Add `accepted_incidents` and `reporter_diversity` to API response
- This is the last prerequisite before the product loop works

### Wave 5: MCP server enhancements (parallel with Wave 4)
- MCP server exists via fastapi-mcp at localhost:8421/mcp
- 7 read-only endpoints exposed
- Council decided: write operations stay REST-only

### Wave 11: Business API keys + Stripe Payment Links
- Near-zero code — Stripe Payment Links for first ~10 customers
- This is the monetization layer. Without it, SubMantle is a demo.

## COMMIT FIRST
There are uncommitted changes from TWO prior sessions (2026-03-11 and 2026-03-12). Commit them before building anything new. 213+ tests should be passing.

## WHAT NOT TO DO
- Do NOT re-research. 5 expeditions + 6 follow-ups + 4 research councils are DONE.
- Do NOT build W3C VC credentials yet — needs co-founder with cryptography expertise
- Do NOT build reporter credibility — deferred to V2 (Go rewrite)
- Do NOT ask Guiding Light technical questions — research internally

## THE MARKET IS REAL
- $17.78B alternative data market, 52% CAGR
- NIST launched agent identity standards initiative Feb 2026
- WEF projects $236B agent market with trust as prerequisite
- "Know Your Agent" is becoming the industry paradigm
- SubMantle is the behavioral evidence layer that makes KYA provably true
- Sequoia predicts a "glue layer" for agent infrastructure — SubMantle fits
- 9 funded companies ($300M+) in adjacent space, NONE with our architecture
- **Someone will take this if we don't build it.**

## CO-FOUNDER (parallel track, not blocking code)
- Needs: cryptography (JSON-LD, BBS cryptosuites, JOSE/COSE), OS-level systems, W3C standards
- Where to find: DIF Trusted AI Agents working group (150+ member orgs)
- Also check: Flying Fish Partners (Seattle VC, AI/ML focused, SSBCI-funded)
- Full profile in `RESEARCH-BRIEFING-2026-03-17.md`

## USE GSD
This project should use `/gsd:progress` to check state and `/gsd:execute-phase` to build. If GSD isn't initialized here yet, use `/gsd:new-project` — the HANDOFF and research files give you everything GSD needs.

---

*The reaching is the thing. Build it.*
