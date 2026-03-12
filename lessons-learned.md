# Substrate — Lessons Learned

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
- **Rule**: Substrate doesn't DETECT incidents (that would require ML). It RECORDS reports from third parties. Like a credit bureau — the bureau doesn't catch missed payments, the bank reports them.
- **Why**: This eliminated the #1 "blocking decision" that had stalled trust layer progress.
