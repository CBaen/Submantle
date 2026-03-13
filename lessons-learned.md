# Submantle — Lessons Learned

### Never Ask Guiding Light Technical Questions
- **Pattern**: Identified "incident taxonomy" as blocking and asked GL to define it
- **Rule**: Research and propose technical answers. Only surface product/vision/business decisions to GL.
- **Why**: GL is a creator/designer, not an engineer. The incident taxonomy turned out to have a simple technical answer (credit bureau model — record reports, don't detect).

### Scale Validation Agents to Data Size
- **Pattern**: Dispatched 3 validators to read 5 large research files each (~250KB total). All 3 ran out of context.
- **Rule**: When research files are large, dispatch more agents with smaller scopes (1 file each + targeted web verification).
- **Why**: A single agent reading 250KB+ has no room left to verify claims and write a report.

### Incident Taxonomy Is a Credit Bureau Model
- **Pattern**: All 5 research teams treated incident taxonomy as a complex product design problem.
- **Rule**: Submantle doesn't DETECT incidents (that would require ML). It RECORDS reports from third parties. Like a credit bureau — the bureau doesn't catch missed payments, the bank reports them.
- **Why**: This eliminated the #1 "blocking decision" that had stalled trust layer progress.

### Proactively Update Lessons Learned
- **Pattern**: GL had to remind me to update this file after a session with multiple learnings.
- **Rule**: After every significant session, review what happened and add lessons BEFORE GL has to ask. The Self-Improvement Loop in CLAUDE.md says "after ANY correction" — don't wait to be corrected twice.
- **Why**: Future agents inherit these lessons. Every unrecorded mistake gets repeated. GL shouldn't have to police documentation — that's our job.

### Set Expectations on Long-Running Agents
- **Pattern**: Mnemom research agent ran for 30+ minutes. GL had to ask "is this agent stuck?"
- **Rule**: When dispatching agents that may take a long time (deep web research on obscure companies), tell GL upfront: "This one may take a while — the company has limited public info." Check progress proactively.
- **Why**: GL has ADHD. Silence during long operations feels like something broke. A 5-second status update prevents frustration.

### CLAUDE.md Must Carry Full Context — GL Is the Bottleneck
- **Pattern**: GL said "I am the bottleneck" and "I won't be able to maintain understanding if this gets built in a direction I can't follow."
- **Rule**: CLAUDE.md must contain enough context that ANY new agent instance can build correctly without GL re-explaining. Include: what the product is, why it matters, competitive landscape, design principles, build priorities, what NOT to do. GL should never have to re-teach the same context twice.
- **Why**: Solo founder + AI dev team means every session starts fresh. If CLAUDE.md doesn't carry the context, GL has to — and that doesn't scale.

### Document Parity Includes Formulas
- **Pattern**: CLAUDE.md, VISION.md, and submantle-index.md all showed the wrong Beta formula variant (`total_queries / (total_queries + incidents)` — division by zero at init). Codebase used the correct Laplace-smoothed version. Validator 3 caught it; no research team did.
- **Rule**: When a formula or key technical detail appears in multiple documents, verify they all match the actual codebase implementation. Use Grep to find all occurrences and fix them in one pass.
- **Why**: A solo founder implementing from CLAUDE.md rather than reading the code would get a broken formula. Document parity isn't just about tracking numbers — it's about technical accuracy.

### Validators With Different Lenses Catch More Than Identical Ones
- **Pattern**: Prior session dispatched 3 validators with identical instructions and they all ran out of context on the same files. This session gave each validator a different focus (general quality, anti-gaming, solo founder feasibility) and all 3 returned with unique, high-value findings.
- **Rule**: When dispatching multiple validators, assign each a distinct analytical lens. They'll naturally cross-reference team findings through their own perspective rather than duplicating effort.
- **Why**: Identical instructions produce correlated findings. Different lenses produce complementary coverage. The anti-gaming validator caught the patient attacker vector; the feasibility validator caught the math errors; the general validator caught the settled-decision violations.

### Update Lessons Learned Without Being Asked (Again)
- **Pattern**: GL had to remind me to update this file — the exact same correction from a prior session already documented in "Proactively Update Lessons Learned" above.
- **Rule**: Check this file at session end. If you learned something, write it. The rule already exists. Follow it.
- **Why**: Repeating a documented mistake is worse than making it the first time. It means the lessons-learned system failed at its one job.

### New Instances Must Be Helpful and Focused — GL Is the Bottleneck
- **Pattern**: Research accumulates across sessions. New instances arrive, read stale research, and re-litigate settled decisions or get confused by outdated findings.
- **Rule**: HANDOFF.md is the single source of truth for current state. Research files are historical records — they inform, they don't override. New instances should read HANDOFF.md, check the build priority table, and start building. Don't re-research what's settled. Don't ask GL to re-explain context. GL is one person with ADHD — every re-explanation costs focus they can't afford.
- **Why**: GL said "I am the bottleneck." Every minute GL spends re-teaching context is a minute not spent on design decisions only GL can make. The documentation must carry the full context so new instances can be productive immediately.

### Verify Auto-Generated Operation IDs Before Using Them
- **Pattern**: fastapi-mcp whitelist used function names (`health`, `query`) but FastAPI auto-generates operation IDs with the full path appended (`health_api_health_get`, `query_api_query_get`). The whitelist silently matched nothing.
- **Rule**: When referencing FastAPI operation IDs, always check `/openapi.json` for the actual generated values. Don't assume they match function names.
- **Why**: Silent failures in whitelists are the worst kind — no error, just zero endpoints exposed. A 30-second check prevents a debugging rabbit hole.

### Research Councils Produce Actionable Intel When the Question is Right
- **Pattern**: GL asked "what would a research council think about multi-protocol access?" The council produced a concrete recommendation (fastapi-mcp, read-only scope, rate limiting first) that was implemented in the same session.
- **Rule**: Research councils work best when the question is a real decision point with multiple valid approaches. "Should we do X?" produces better output than "tell me about X."
- **Why**: The council format forces structured disagreement. The Devil's Advocate caught the billing timing risk and prompt injection surface that neither the Codebase Analyst nor External Researcher identified.

### Rebrand Early, Rebrand Completely
- **Pattern**: "Substrate" conflicted with Parity Technologies' blockchain framework. Caught before public launch but after 91 files existed.
- **Rule**: Resolve naming conflicts before writing significant code. When rebranding, dispatch parallel agents by file zone (docs, code, research) and verify with grep afterward. Rename files AND folders, not just content.
- **Why**: The longer you wait, the more files to change. 91 files took 4 parallel agents. 500 files would take a full session.
