# Submantle Queue

**Purpose:** Active tasks only. Git commit history preserves completed tasks.
**When an item is DONE: delete it from this file.** Git tracks completion history. Queues are for current work only. Never accumulate completed items.

## URGENT — Business Foundation (before more code)

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

- [ ] **Demo / landing page** (added: 2026-03-11)
      What: Something to show when someone asks "what is Submantle?" — a 30-second story with a visual. Localhost dashboard is not a pitch.
      Context: No demo video, no landing page, no pitch deck exists. If Anthropic/investor/journalist asks "show me," need something ready.

- [ ] **Dashboard depth** (added: 2026-03-10)
      What: Clickable device rows, nested process categories, expandable counts, full dependency chains in query results.
      Context: Guiding Light's direct request — "none of these fields have nested data. That's necessary." Also makes the demo compelling.

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
