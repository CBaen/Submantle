# Substrate Queue

**Purpose:** Active tasks only. Git commit history preserves completed tasks.

## Active

- [ ] **Dashboard depth** (added: 2026-03-10)
      What: Clickable device rows, nested process categories, expandable counts, full dependency chains in query results.
      Context: Guiding Light's direct request — "none of these fields have nested data. That's necessary."

- [ ] **Trust layer wiring — auth middleware** (added: 2026-03-11)
      What: Token-based auth on /api/query, wired to agent registry.
      Context: Expedition synthesis "MVTL step 1". Blocking gap identified by 3 independent research passes.

- [ ] **Trust layer wiring — incident taxonomy** (added: 2026-03-11)
      What: Define what specific agent behaviors constitute an incident. Product decision from Guiding Light.
      Context: Expedition synthesis "MVTL step 2". Every team flagged this as the #1 blocking design decision.

- [ ] **Trust layer wiring — record_query()** (added: 2026-03-11)
      What: Wire record_query() to API endpoints so every agent interaction becomes trust data.
      Context: Expedition synthesis "MVTL step 3". Without this, Beta formula returns undefined forever.

- [ ] **Trust layer wiring — agent name uniqueness** (added: 2026-03-11)
      What: Enforce unique agent names in registry. Prevents trivial identity confusion.
      Context: Expedition synthesis "MVTL step 4". Reviewer finding from V1 build.

- [ ] **Trust layer wiring — compute_trust()** (added: 2026-03-11)
      What: Implement pure Beta formula (total_queries / (total_queries + incidents)), initialize at (1,1) = 0.5, expose in API.
      Context: Expedition synthesis "MVTL steps 5-6". Formula validated by 3 teams + 3 validators.

- [ ] **MCP server** (added: 2026-03-10)
      What: Ambient awareness stream + deep query tools via Model Context Protocol.
      Context: Fresh-eyes audit recommended MCP as the value proof — let agents be the first users.

- [ ] **Commit research files** (added: 2026-03-11)
      What: 17 expedition files + 6 follow-ups + updated project docs. All uncommitted.
      Context: Trust layer expedition complete, documents updated, need to persist to git.

- [ ] **EU AI Act compliance docs** (added: 2026-03-11)
      What: Three lightweight documents — self-assessment ("not an AI system"), privacy policy, data flow docs.
      Context: Follow-up research confirmed Substrate likely outside scope. Documents needed before August 2026.

- [ ] **Lock CORS to localhost** (added: 2026-03-10)
      What: Replace wildcard CORS with localhost-only before any WiFi deployment.
      Context: Reviewer finding from V1 build.

- [ ] **License decision** (added: 2026-03-10)
      What: Choose open-source license (Apache 2.0 / BSL / AGPL).
      Context: Required before any public release or community contribution.
