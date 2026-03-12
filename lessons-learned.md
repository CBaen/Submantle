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

### Rebrand Early, Rebrand Completely
- **Pattern**: "Substrate" conflicted with Parity Technologies' blockchain framework. Caught before public launch but after 91 files existed.
- **Rule**: Resolve naming conflicts before writing significant code. When rebranding, dispatch parallel agents by file zone (docs, code, research) and verify with grep afterward. Rename files AND folders, not just content.
- **Why**: The longer you wait, the more files to change. 91 files took 4 parallel agents. 500 files would take a full session.
