# Submantle Queue

**Purpose:** Active tasks only. Git commit history preserves completed tasks.

## URGENT — Business Foundation (before more code)

- [x] **Legal entity exists** (completed: 2026-03-11)
      What: Built by Cameron LLC — Wyoming, EIN 41-4309920, Mercury banking. Business purpose broad enough for Submantle.
      Context: Located at C:\Users\baenb\projects\builtbycameron\business documents\

- [x] **Product name decided — Submantle** (completed: 2026-03-11)
      What: submantle.com purchased. Complete rebrand from "Substrate" to "Submantle" across all 91 files.
      Context: "Substrate" conflicted with Parity Technologies' blockchain framework. "Submantle" = the layer beneath everything. Clean trademark space.

- [ ] **License decision — BSL recommended** (added: 2026-03-11)
      What: Choose Business Source License (BSL). Code visible, readable, forkable — but companies above a threshold can't use commercially without paying. Converts to open source after 3-4 years.
      Context: Used by MariaDB, CockroachDB, Sentry, HashiCorp. Prevents Google/Microsoft from taking the code while allowing community adoption. Required before any public release.

- [ ] **Define 90-day success metric** (added: 2026-03-11)
      What: Pick ONE measurable goal. Examples: "10 real agents querying via MCP" or "1,000 dashboard users" or "1 brand partnership letter of intent."
      Context: Without a target, every feature feels equally important. The metric determines build priority order.

- [ ] **Define first customer persona** (added: 2026-03-11)
      What: Pick ONE specific person/role who pays first. Not "device owners" — a specific pain point, a specific willingness to pay.
      Context: "Everyone" is not a customer. Need this to build the right thing and market to the right people.

- [ ] **Anthropic conversation** (added: 2026-03-11)
      What: Reach out to Anthropic — not as a pitch, as an offering. "We built the behavioral trust layer for MCP. No one else has. Here it is."
      Context: Anthropic is a founding member of the Agentic AI Foundation. They built MCP. They need a trust layer. Natural partnership. Best done with LLC + demo in hand.

## HIGH — Traction (things that create users)

- [x] **Commit all research files** (completed: 2026-03-11)
      What: 17 expedition files + 6 follow-ups + protocol architecture expedition (5 teams + 9 validators). All committed and pushed.
      Context: 4 expeditions complete. 40 commits on origin/main.

- [x] **MCP server** (completed: 2026-03-12)
      What: Read-only MCP at /mcp via fastapi-mcp. 7 endpoints exposed (health, status, query, agents_list, verify_directory, verify_agent, privacy_status). Write ops REST-only. Bearer token auth passthrough.
      Context: Research council recommended fastapi-mcp over custom build. 3-line integration, HTTP transport (not stdio). 220 tests passing.

- [ ] **Demo / landing page** (added: 2026-03-11)
      What: Something to show when someone asks "what is Submantle?" — a 30-second story with a visual. Localhost dashboard is not a pitch.
      Context: No demo video, no landing page, no pitch deck exists. If Anthropic/investor/journalist asks "show me," need something ready.

- [ ] **Dashboard depth** (added: 2026-03-10)
      What: Clickable device rows, nested process categories, expandable counts, full dependency chains in query results.
      Context: Guiding Light's direct request — "none of these fields have nested data. That's necessary." Also makes the demo compelling.

## MEDIUM — Trust Layer Wiring (MVTL — 5 sessions)

- [ ] **Trust layer wiring — auth middleware** (added: 2026-03-11)
      What: Token-based auth on /api/query, wired to agent registry.
      Context: Expedition synthesis "MVTL step 1". Blocking gap identified by 3 independent research passes.

- [ ] **Trust layer wiring — incident reporting format** (updated: 2026-03-11)
      What: Design the reporting format for third-party incident reports. Credit bureau model — Submantle records, doesn't detect.
      Context: RESOLVED by protocol architecture expedition. Not a product decision. Third parties report incidents; Submantle stores and scores.

- [ ] **Trust layer wiring — record_query()** (added: 2026-03-11)
      What: Wire record_query() to API endpoints so every agent interaction becomes trust data.
      Context: Expedition synthesis "MVTL step 3". Without this, Beta formula returns undefined forever.

- [ ] **Trust layer wiring — agent name uniqueness** (added: 2026-03-11)
      What: Enforce unique agent names in registry. Prevents trivial identity confusion.
      Context: Expedition synthesis "MVTL step 4". Reviewer finding from V1 build.

- [ ] **Trust layer wiring — compute_trust() + anti-gaming rules** (added: 2026-03-11)
      What: Pure Beta formula (total_queries / (total_queries + incidents)), initialize at (1,1) = 0.5. Add deterministic velocity caps + query diversity rules.
      Context: Expedition synthesis "MVTL steps 5-6". Anti-gaming rules are deterministic (not ML) to stay outside EU AI Act scope.

## LOWER — Hardening & Compliance

- [ ] **Lock CORS to localhost** (added: 2026-03-10)
      What: Replace wildcard CORS with localhost-only before any WiFi deployment.
      Context: Reviewer finding from V1 build.

- [ ] **EU AI Act compliance docs** (added: 2026-03-11)
      What: Three lightweight documents — self-assessment ("not an AI system"), privacy policy, data flow docs.
      Context: Follow-up research confirmed Submantle likely outside scope. Documents needed before August 2026.

- [ ] **Agent identity definition in API docs** (added: 2026-03-11)
      What: Document that an "agent" = registered software entity (not model, not context window, not user). Include edge cases: multi-model, version upgrades, forks.
      Context: Foundational definition from 2026-03-11 session. Must be clear for any external developer.

- [ ] **Document trust security model** (added: 2026-03-11)
      What: Write up the 5 attack vectors and defenses (score inflation, identity theft, impersonation, Sybil, self-gaming) for external consumption.
      Context: Security documentation needed before any external adoption. Locality advantage is a novel differentiator worth highlighting.
