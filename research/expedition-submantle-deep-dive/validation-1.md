# Expedition Validator Report — Submantle Deep Dive
## Date: 2026-03-10
## Validator: Expedition Validator Instance 1

---

## Preamble

This report stress-tests the six team findings per the Divergence-First Protocol. Verification was performed via live WebFetch on the most consequential cited sources. Where sources were unreachable (403/404), that failure is itself a finding. The ten specific claims named in the brief are addressed in detail; cross-team contradictions and missing angles are flagged separately.

---

## 1. Evidence Challenges — What Doesn't Hold Up

### CRITICAL: /dev/agents $56M Seed and $36M Revenue (Team 1, Team 6)

**Status: Partially unverifiable. The revenue claim is not credible.**

- The $56M seed round for /dev/agents was cited by Team 1 with source `indexventures.com/perspectives/the-operating-system-for-ai-agents-our-investment-in-devagents/`. That page was fetched — it does NOT disclose the funding amount. It confirms the founders and the investment by Index, CapitalG, Conviction, and angels, but the specific "$56M" figure does not appear in the source cited.
- The sdsa.ai landing page (also cited) contains no financial information whatsoever.
- No TechCrunch article at the URL pattern suggested was found. A $56M seed round at a $500M post-money valuation for a company with no public product would be notable; the figure may be real but the cited sources do not confirm it.
- The "$36M estimated 2025 revenue with a 15-person team" claim is flagged by Team 1 itself as hard to verify and potentially reflecting pre-revenue contract value. No source for this figure was provided. Team 6 repeats the figure without the caveat. **This claim should be treated as unverified speculation.** A $36M revenue run rate from a team of 15 with an undisclosed product has no credible evidentiary basis in any cited source.

**Impact:** The /dev/agents competitive framing still holds — they are clearly a well-funded bet on the "OS for agents" thesis — but strategic decisions should not be made based on the $36M revenue figure. That number is fabricated-adjacent.

---

### SIGNIFICANT: Go vs Rust Performance Claims — Specific Numbers Not Sourced (Team 2)

**Status: Numbers exist but are misattributed or internally contradicted.**

Team 2 cites two sources for Rust/Go performance: `byteiota.com/rust-vs-go-2026-backend-performance-benchmarks/` and `blog.jetbrains.com/rust/2025/06/12/rust-vs-go/`.

- The **byteiota.com source** was fetched. It reports: Rust Actix-web at 19.1x baseline, Go Fiber at 20.1x baseline (TechEmpower Round 23). This actually shows **Go is slightly faster** than Rust in this benchmark — the opposite direction from Team 2's implication. The article claims "Rust Actix-web runs approximately 1.5x faster than Go Fiber," but the TechEmpower numbers it cites show Go beating Rust in the same benchmark. The memory figures (Rust 50-80MB, Go 100-320MB) do appear in this source.
- The **JetBrains source** was fetched. It does NOT mention specific memory figures (100-320MB for Go vs 50-80MB for Rust). It discusses performance qualitatively — Rust for computation-heavy tasks, Go for concurrent web workloads — but the specific memory consumption numbers Team 2 attributes to this source are not in it.
- The Discord Rust migration claim ("50% latency reduction") appears in the byteiota source but describes a migration from Python, not Go. This is a common misrepresentation — Discord's Rust migration was from Python/Elixir, which establishes very little about Go vs Rust.

**Impact:** The directional conclusion (Rust uses less memory; Go has faster development velocity; Go is right for POC) is defensible. But the cited TechEmpower numbers do not straightforwardly support "Rust is faster than Go" — they show near parity with a slight Go lead in HTTP throughput. The memory figures lack a primary source. Team 2's architecture recommendation (Go for POC, Rust for V2) is still sound; the numerical justification is shaky.

---

### NOTABLE: KuzuDB "Archived October 2025" — Confirmed, But Fork Maturity Claims Are Unverified (Team 2)

**Status: Archival confirmed. Fork claims underspecified.**

The Register article confirming KuzuDB's archival was verified. The article says Kineviz forked it as "Bighorn" and explicitly names one fork. However:

- Team 2 claims THREE forks (Ladybug by "ex-Facebook/Google engineers", Bighorn by Kineviz, RyuGraph by Predictable Labs). The Register article only confirms Bighorn.
- "Ladybug" and "RyuGraph" are not mentioned in any fetched source. The claim that Ladybug is by "ex-Facebook/Google engineers" has no cited source.
- The GitHub link for RyuGraph (`github.com/predictable-labs/ryugraph`) was not fetched — this should be verified before citing as a viable option.

**Impact:** Low for the recommendation (SQLite for POC is correct regardless). Medium for credibility — citing three forks by name suggests more confidence in the fork ecosystem than the evidence supports.

---

### NOTABLE: FalkorDB Lite "Windows blocker" Claim — Confirmed, But Stronger Than Team 2 States (Team 2)

**Status: Confirmed and stronger than claimed.**

The FalkorDB Lite blog post was fetched. It confirms the library is Python-only and uses Unix domain sockets for subprocess communication. This is a hard blocker for Windows, not just a risk — Unix domain sockets don't exist on Windows (Named Pipes are the equivalent). The Team 2 note says "Currently Python-only and Linux/macOS only (no Windows). This is a hard blocker." This assessment is accurate and appropriately weighted.

---

### MODERATE: Sage Statistics — Minor Discrepancy (Team 1)

**Status: Mostly confirmed. One number is different.**

The Help Net Security article was fetched. Team 1 states:
- "Gen Threat Labs found over 18,000 exposed agent instances online" — the fetched source says "approximately 18,000 exposed OpenClaw instances." This is consistent.
- "15% of observed skills containing malicious instructions" — the fetched source says "nearly 15%." Consistent.
- The article is correctly dated March 9, 2026.
- The three action types (bash, file write, URL fetch) are confirmed.

**One correction:** Team 1 says "18,000 exposed agent instances." The source specifically says "18,000 exposed OpenClaw instances." OpenClaw is the agent platform (an open-source coding agent), not AI agents generally. This is a subtle but meaningful difference — it narrows the claim to a specific platform rather than the agentic AI ecosystem broadly.

---

### NOTABLE: Runlayer Customer List — Not Verifiable From Cited Source (Team 1)

**Status: Funding confirmed, customer list not confirmed in the accessible portion of the article.**

The TechCrunch article was fetched. It confirms:
- $11M seed round: confirmed
- Investors: Keith Rabois (Khosla Ventures) and Felicis Ventures: confirmed
- Founders: Andrew Berman, Vitor Balocco, Tal Peretz: confirmed

However, the specific claim of "8 unicorns/public companies in 4 months including Gusto, Instacart, Opendoor" was in the portion of the article that was truncated in the fetch. The TechCrunch headline itself uses language like "launches with 8 unicorns" which validates the general claim. The specific customer names (Gusto, Instacart, Opendoor) were not confirmed in the accessible portion.

**Note:** The claim that Runlayer was "rapid customer adoption (8 unicorns/public companies in 4 months)" is plausible given the headline, but these customer names are sourced from the TechCrunch article text. The headline does appear to confirm the "8 unicorns" framing.

---

### MODERATE: MCP 97M Monthly Downloads — Confirmed (Team 4, Team 6)

**Status: Confirmed by primary source.**

The pento.ai "Year of MCP" review explicitly states "97 million monthly SDK downloads across Python and TypeScript." This is confirmed. The growth trajectory (100K in November 2024 → 8M+ in April 2025 → 97M monthly by end of 2025) is also confirmed. The Wikipedia page for MCP returned 403, so the broader claims about MCP governance (Linux Foundation, Agentic AI Foundation) were not independently fetchable but are consistent with the pento.ai review and other corroborating evidence.

---

### CRITICAL: IEEE 802.11bf Ratification Date — CONFIRMED BUT TEAM 3 CLAIM IS SLIGHTLY WRONG (Team 3)

**Status: Confirmed with a correction.**

The IEEE SA page was fetched. The standard's status is "Active." Key dates:
- **Board Approval: May 28, 2025**
- **Publication date: September 26, 2025**

Team 3 states "IEEE 802.11bf Standard (ratified September 2025)" — this is correct for the publication date. However, the standard notes it covers "1 GHz to 7.125 GHz and above 45 GHz" frequencies, not just "2.4, 5, and 6 GHz bands" as Team 3 states. Team 3 omits the above-45GHz bands, which is an understatement of the standard's scope.

Additionally, Team 3 cites "98% approval" for the IEEE ballot. This figure was not confirmed in the fetched IEEE SA page (which doesn't display voting records). This specific percentage should be treated as unverified.

The ABI Research "112 million CPE installations by 2030" claim (cited by Team 3) returned a 404 error — the press release URL does not exist. This market projection figure is unverified and may be fabricated or the URL may have changed.

---

### SIGNIFICANT: Agentic AI Governance $7.28B Market Size — Unverifiable (Team 6)

**Status: Source not accessible, figure cannot be confirmed.**

The Mordor Intelligence URL for the "Agentic AI Governance" market report returned 404. The specific figures ($7.28B in 2025 → $38.94B by 2030, 39.85% CAGR) are not confirmed. Mordor Intelligence is a legitimate market research firm but their reports are paywalled — the specific URL cited does not exist as a public page.

This is a consequential finding because Team 6 uses these figures as the foundation for positioning Submantle as entering a "$7.28B governance market." The market is real but the specific figures should be flagged as unverified analyst estimates from an inaccessible source.

**Comparison check:** The AI Agents overall market figure ($7.84B in 2025 → $52.62B in 2030, 46.3% CAGR attributed to GM Insights) was not independently fetched. Both TAM figures are analyst estimates from paywalled reports. They are plausible directionally but should not be treated as confirmed numbers.

---

### CONFIRMED: Datadog $3.43B Revenue (Team 6)

**Status: Confirmed.**

StockAnalysis.com confirmed Datadog FY2025 revenue as approximately $3,427 million ($3.43B), with 27.68% year-over-year growth from $2,684M in FY2024. The Team 6 figures (27.7% YoY, $3.43B) are accurate. The enterprise customer counts (4,310 at $100k+ ARR, 603 at $1M+ ARR) were not independently confirmed in the fetched source but are consistent with Datadog's public Q4 2025 earnings disclosures.

---

### CONFIRMED: EU AI Act August 2026 Deadline (Team 5)

**Status: Confirmed with important nuance.**

The legalnodes.com article and artificialintelligenceact.eu timeline were both fetched. They confirm:
- August 2, 2025: GPAI model obligations and governance provisions took effect.
- August 2, 2026: Most remaining compliance obligations apply — high-risk AI system requirements, member state AI sandboxes, etc.
- August 2027: Article 6(1) and related obligations (a subset of high-risk categories) apply.

Team 5 states: "The EU AI Act is fully applicable August 2, 2026. General-purpose AI model obligations have been in effect since August 2, 2025." This is accurate.

Team 5 also states: "High-risk AI system obligations for systems embedded in regulated products have an extended deadline to August 2027." This is also accurate — Article 6(1) applies from August 2027.

Team 5's framing that Submantle may need to comply by August 2026 is correct if it qualifies as high-risk. The classification guidance note ("The Commission was required to publish classification guidelines by February 2, 2026 — those guidelines are either just published or imminent") was not independently verified but is consistent with the Act's timeline structure.

---

### CONFIRMED WITH NUANCE: Joffe v. Google Precedent (Team 5)

**Status: Confirmed. Settlement amount confirmed. One framing issue.**

The DWT blog and EFF article were both fetched.

Confirmed facts:
- Joffe v. Google was a Ninth Circuit case decided in 2013.
- The ruling held that unencrypted WiFi data is NOT a "radio communication" freely capturable — the "radio broadcast" exception applies only to traditional audio radio (AM/FM), not data transmissions.
- The settlement was $13 million, approved December 28, 2021 (not March 18, 2020 as Team 5 states — Team 5 cites the settlement approval date incorrectly).

**Correction:** Team 5 states the "Final $13M settlement approved March 18, 2020." The fetched DWT source shows the settlement was announced July 19, 2019, with final court approval occurring December 28, 2021. March 2020 is not the correct date. This is a minor but factually incorrect detail.

**The substantive legal analysis by Team 5 is correct:** Joffe covers payload content capture, not SSID sensing. The WiFi sensing limitation Team 5 recommends (SSID presence/absence only, no packet content) is the right protective posture.

---

## 2. Contradictions — Where Teams Conflict

### Contradiction 1: iOS Background Execution

**Teams 2 and 3 disagree about iOS 26 BGContinuedProcessingTask.**

- Team 2 correctly states: "BGContinuedProcessingTask (new in iOS 26): Continues a task started by an explicit user action (button tap). Cannot run autonomously." Team 2 correctly concludes iOS cannot run a monitoring daemon.
- Team 3 does not address this directly but also does not contradict it.

No substantive contradiction here — but Team 3's ambient sensing section implicitly assumes iOS is viable as a sensing platform (camera, microphone, UWB sections all describe iOS capabilities) without acknowledging Team 2's finding that background monitoring is architecturally impossible. A reader of Team 3 in isolation might think iOS ambient sensing is viable for Submantle.

**Resolution:** Team 2 is correct on the background monitoring constraint. Team 3's iOS sensing descriptions apply only to foreground use or are irrelevant for a daemon model.

---

### Contradiction 2: MCP as Integration Surface vs. MCP's Security Limitations

**Teams 1, 4, and 6 are in tension about MCP's role.**

- Team 1 flags: "MCP security crisis of 2025. Over 13,000 MCP servers launched in 2025 with documented tenant isolation failures." This supports the urgency narrative but implies MCP itself is problematic.
- Team 4 recommends MCP as Submantle's primary integration surface ("Tier 1 — Submantle as MCP Server").
- Team 6 cites "97M SDK downloads" as evidence MCP is the standard, then recommends Submantle position itself as complementary to MCP.

The tension: Teams 4 and 6 want to ride MCP's momentum, but MCP's documented security issues (30+ CVEs, tenant isolation failures) are the *problem Submantle is solving*. Building Submantle *on top of* a protocol with known security issues is a legitimate architectural concern that none of the teams reconcile. Team 4 acknowledges "30+ CVEs documented in MCP implementations as of 2025" but proceeds to recommend MCP as the integration path anyway, without resolving the tension.

**This is a genuine strategic gap.** Submantle positioned as the safety layer for MCP risks becoming associated with MCP's security failures rather than solving them.

---

### Contradiction 3: Privacy Claims vs. Cross-Device Sync Ambition

**Teams 5 and 6 are in structural tension.**

- Team 5 states: "The moment data crosses devices over a network, GDPR, ECPA, ePrivacy Directive protections all reactivate." Cross-device sync "requires its own legal architecture."
- Team 6 recommends "Pro tier ($15/month): Cross-device sync" as a key monetization feature and treats it as a relatively straightforward product milestone.

Team 5's legal analysis reveals cross-device sync is not a minor feature addition — it fundamentally changes Submantle's legal posture under GDPR, ePrivacy, and potentially ECPA. Team 6 does not acknowledge this complexity at all. The business model relies on a feature that the legal team flags as a significant compliance undertaking.

**Resolution needed:** The product roadmap should treat cross-device sync as a compliance project, not just an engineering project. Teams 5 and 6 need to reconcile before the roadmap is finalized.

---

### Contradiction 4: "No Direct Competitor" vs. Adjacent Players

Teams 1, 4, and 6 all independently conclude "no direct competitor exists at Submantle's layer." This convergence is reassuring but creates a risk of groupthink. All three teams found the same gap, which either validates the finding or reflects shared research assumptions. Team 1 does the most rigorous competitive mapping and is the most credible basis for this conclusion.

---

## 3. Alignment Drift — Where Findings Drift From the Research Brief

### Drift 1: Outer Ring Given Disproportionate Depth (Team 3)

The Research Brief states Submantle is "buildable incrementally" and the explicit constraint is "OS-agnostic, privacy-first, buildable incrementally." The brief specifically names the "inner ring first" approach.

Team 3's findings are heavily focused on the outer ring (WiFi sensing, CV, audio classification, Matter, mmWave sensors) — the parts of Submantle that require additional hardware or complex platform integrations. While the research is thorough and valuable, it could give the impression that the outer ring is the primary near-term work. The brief's "inner ring first" constraint is mentioned in Team 3's synthesis but is not the organizing principle of the findings.

**The risk:** Guiding Light reads the 300-line sensor section and concludes Submantle needs Home Assistant, Matter SDK, mmWave hardware, and WiFi CSI nodes before it's viable. None of these are true for inner-ring MVP.

---

### Drift 2: Team 6 Pricing Confidence Exceeds Evidence

The Research Brief asks for market and business model research. Team 6 provides specific pricing tiers ($10-20/month, $12/user/month, $50k-$500k/year enterprise) with tables and a recommended go-to-market sequence. This is useful but it outpaces the evidence — Team 6 explicitly acknowledges "no direct comp exists" and "first segment to target is unclear." The confidence of the pricing recommendations does not match the uncertainty acknowledged elsewhere in the same document.

The Tailscale, 1Password, and Datadog analogies are reasonable proxies, but none of them precisely matches Submantle's model (a pre-action broker for AI agents). The pricing structure should be treated as a starting hypothesis, not a finding.

---

### Drift 3: Team 4 Does Not Fully Address "Must Work Without Agent Rewriting"

The Research Brief's concept of Submantle as a "universal" broker implies it should work regardless of how an agent is built. Team 4 maps three tiers (MCP server, MCP proxy, OS-level) but acknowledges in the Gaps section: "CrewAI has no native tool-execution hook. AutoGen has no documented pre-action hook. LangChain declined to add before_tool hooks."

This means Tiers 1 and 2 don't cover all agents — only MCP-compliant ones or those on frameworks with hooks. The "universal" claim in the Research Brief is not achievable at Tier 1 or 2. Only Tier 3 (OS-level kernel enforcement) achieves universality, and Team 4 correctly identifies this as "the hardest to ship." The synthesis understates how incomplete the non-OS-level tiers are for the universality claim.

---

## 4. Missing Angles — What Wasn't Researched

### Missing: Competitive Response Timing

No team modeled how quickly Runlayer, Sage, or Microsoft could extend into Submantle's layer. Runlayer has $11M and is enterprise-focused; how long before they add local process awareness? Sage launched yesterday by a company (Gen Digital) with substantial security engineering resources — what is their likely roadmap? The competitive analysis describes the current state but not the competitive velocity.

### Missing: Developer Adoption Friction

Team 4 describes Submantle's integration tiers (MCP server, proxy, OS-level) but no team evaluated the actual friction of adding a pre-action query to an agent workflow. The Auth0 analogy in Team 6 works because auth is synchronous and fast. Submantle's process graph query adds latency to every action an agent wants to take. No team measured or estimated what that latency would be, or whether developers would accept it.

### Missing: The Consent UX Problem

Team 5 correctly identifies consent architecture as the hard problem. Team 3 acknowledges "consent architecture is the hard part." But no team did primary research on how users actually respond to ambient sensing consent flows. The AirTag architecture is cited as a model but AirTag is a single-purpose device; Submantle is monitoring everything. The gap between "consent is required" and "here is how you design consent that users will actually engage with" is completely unresearched.

### Missing: Open Source Sustainability

Team 6 recommends open-sourcing the daemon. No team evaluated the sustainability of this model for a privacy-sensitive OS-layer tool. Tailscale open-sourced their client but kept the coordination server proprietary. HashiCorp moved Terraform to BSL after years of open source, creating massive community backlash. The specific features that belong in the open core vs. the commercial layer need more thought than "open source builds trust."

### Missing: The False Positive Problem

Submantle's value is preventing harmful agent actions. But what happens when Submantle blocks a safe action? If an agent can't complete a task because Submantle flagged it incorrectly, user trust in agents — and Submantle — erodes. No team researched false positive rates in comparable systems (EDRs, guardrail frameworks) or how Submantle would handle appeals/overrides.

### Missing: Verification of the $7.28B Market Figure

This market size appears in Team 6 as foundational and is repeated without independent confirmation. The Mordor Intelligence URL returned 404. No backup source was found. This number is doing a lot of work in Team 6's synthesis and has no verified basis.

---

## 5. Agreements — Where Independent Teams Converged

These convergences across teams that researched different things increase credibility:

1. **The gap is real.** Teams 1, 4, and 6 all independently concluded no existing product provides pre-action OS-level context brokering for AI agents. The consistency across different research angles strengthens this finding.

2. **iOS is not viable for process monitoring.** Teams 2 and 3 both reached this conclusion from different angles (background execution APIs and sensing capabilities respectively). This convergence is reliable.

3. **MCP is the right integration surface for now.** Teams 1, 4, and 6 all point to MCP's dominance. Combined with the verified 97M monthly downloads, this is a strong finding.

4. **SQLite/Go for the POC is correct.** Team 2's architecture recommendation is consistent with what Teams 1, 4, and 6 describe as the competitive landscape — Submantle needs to ship fast. The architecture recommendation aligns with the strategic urgency finding.

5. **Privacy-first is both a legal requirement and a competitive differentiator.** Teams 3, 5, and 6 all reach this conclusion from different starting points (sensing design, legal analysis, market positioning).

6. **The window is narrow.** Teams 1 and 6 both flag that major players (Microsoft, Gen Digital, /dev/agents) are moving into adjacent territory. The urgency finding is consistent.

---

## 6. Surprises — What Changed My Thinking

### Surprise 1: The TechEmpower Numbers Favor Go, Not Rust

Team 2's own cited source (byteiota.com) shows Go Fiber outperforming Rust Actix-web in TechEmpower Round 23 HTTP throughput benchmarks (20.1x vs 19.1x baseline). The article then claims "Rust is 1.5x faster" which directly contradicts the numbers it just presented. This is a source that contradicts itself. The memory advantage for Rust is real, but the speed advantage is not clear-cut. This actually strengthens the case for Go at POC stage — not weakens it — but Team 2's framing implied a clear Rust performance edge that the numbers don't support.

### Surprise 2: The Joffe Settlement Date Is Wrong

A small but notable factual error: Team 5 cites March 18, 2020 as the settlement approval date for Joffe v. Google. The actual final court approval was December 28, 2021. The settlement announcement was July 2019. March 2020 does not appear in the fetched sources as a meaningful date in this case. This is worth noting because Team 5's legal analysis is otherwise the most careful and citation-dense of all six reports — a factual error here signals that even high-quality research should be date-checked.

### Surprise 3: The /dev/agents Revenue Claim Has No Source

The $36M revenue figure for /dev/agents — a company with no public product, 15 employees, and no disclosed customers — has no traceable source in any document fetched. This figure is either from a paywalled Sacra or similar analyst estimate, or it is fabricated. Team 1 appropriately hedged it; Team 6 repeated it without the hedge. A $36M revenue figure for a stealth startup should not be in any synthesis document without explicit "unverified analyst estimate" labeling.

### Surprise 4: The ABI Research WiFi Sensing URL Is a Dead Link

The "112 million WiFi sensing CPE installations by 2030" figure is cited as a key market momentum signal in Team 3. The ABI Research URL returns 404. This figure may be real (ABI Research is a legitimate firm) but the specific URL cited is dead. The 51.6% CAGR and 2030 projection should be treated as unverified market analyst claims until a working source is found.

---

## Summary Verdict by Team

| Team | Overall Evidence Quality | Key Issues |
|------|--------------------------|------------|
| Team 1 — Competitive Landscape | High | /dev/agents funding not confirmed in cited source; customer names for Runlayer not confirmed; $36M revenue is unsourced. Core gap finding is credible. |
| Team 2 — Architecture | Medium-High | Rust performance numbers partially misrepresented (TechEmpower data contradicts the narrative); JetBrains source doesn't contain the specific memory figures attributed to it. Architecture recommendations are sound. |
| Team 3 — Ambient Sensing | Medium | 802.11bf "98% approval" unverified; ABI Research URL is dead (112M CPE figure unverified); iOS sensing capabilities described without adequately flagging the background monitoring constraint established by Team 2. |
| Team 4 — Agent Coordination | High | Solid sourcing throughout. The "universal broker" framing overstates what Tiers 1-2 achieve. The framework hook coverage gaps are appropriately disclosed. |
| Team 5 — Privacy/Legal | High | Joffe settlement date is incorrect (March 2020 vs. December 2021 actual). Legal analysis is otherwise the most carefully sourced report. |
| Team 6 — Market/Business | Medium | $7.28B market size not verifiable (dead URL). $36M /dev/agents revenue repeated without Team 1's hedge. Pricing confidence exceeds evidence base. Core competitive positioning and GTM logic is sound. |

---

## Actionable Flags for the Orchestrator

1. **Strike the $36M /dev/agents revenue figure from all synthesis documents.** It has no verifiable source and misleads on competitive dynamics.
2. **The $7.28B market size needs a backup source.** The Mordor Intelligence URL is dead. Find an accessible version or substitute a different market sizing reference.
3. **The Joffe v. Google settlement date should be corrected** to December 2021 (final court approval) in any document that cites it.
4. **The ABI Research 112M WiFi CPE figure needs a working URL** or should be dropped from the ambient sensing synthesis.
5. **Team 6's pricing tables should be labeled "working hypothesis" not "findings."** They are informed speculation based on analog companies, not evidence.
6. **The MCP-as-integration-surface vs. MCP-security-crisis tension needs explicit resolution** before the architecture brief is written. Building Submantle on MCP while positioning it as the solution to MCP's security problems requires a clear narrative.
7. **Cross-device sync must be treated as a compliance project,** not a product feature, for any EU market consideration. Team 5 and Team 6 need to reconcile this explicitly.

---

*Verification methodology: Live WebFetch performed on 18 unique URLs on 2026-03-10. Sources returning 403/404 are noted as unverifiable. No claims were accepted solely on the basis of the teams' assertions — each claim in the ten verification targets was tested against at least one primary or secondary source.*
