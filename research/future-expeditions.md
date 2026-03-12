# Future Expedition Ideas

Captured ideas that deserve deep research — AFTER V1 ships and proves the core value.

---

## Expedition: Agent Reviews & Ratings Ecosystem

### Origin
Guiding Light, 2026-03-10, during post-expedition discussion.

### The Idea
Google Reviews for the agent economy. Instead of humans rating restaurants, AI agents rate services based on actual measured experience. Visible to both agents and humans.

### Why It's Novel
- No one is doing this as of March 2026
- Agent reviews are based on measured data, not opinions: uptime, response time, error rates, breaking changes, documentation quality
- An agent that used an API 10,000 times knows more about it than a human who used it once
- Humans benefit too — before picking a service, see what agents actually experienced
- Less privacy-sensitive than usage intelligence — it's about service quality, not user behavior

### Research Questions
1. What review/rating systems exist for APIs and developer tools? (ProgrammableWeb, G2, StackShare — but these are human reviews)
2. How would agent reviews be structured? What metrics matter to an agent vs. a human?
3. What's the trust model? How do you prevent fake agent reviews? (Submantle verification — the agent actually ran through Submantle when it used the service)
4. How does this connect to the Submantle Store? (Reviewed services get listed, high-rated ones get featured)
5. Is there a revenue model? (Featured listings, verified review badges, enterprise analytics on agent experience data)
6. How do existing review platforms (Google, Yelp, G2) handle fraud? What translates to agent reviews?
7. What does "ease of use" mean from an agent's perspective? Can Submantle define a standard agent experience score?

### Connection to Submantle Core
- Submantle sees what agents do (the awareness layer)
- Submantle sees when services fail or succeed (the observation layer)
- Aggregating this into reviews is a natural extension of the knowledge graph
- Reviews become a form of Submantle Insights — but about services, not users
- "Submantle Reviewed" could become a trust badge like "Submantle Safe" but for service quality

### Prerequisite
V1 must exist first. You need Submantle running on real devices, with real agents querying it, generating real experience data. The reviews grow FROM the awareness layer — they can't be designed in a vacuum.

### Guiding Light's Words
"Think about company reviews! The reviews would be more from AI and can be seen by AI but also humans. It could be the new Google Reviews but focused on the agent infrastructure and ease of use and experience."

---

## Expedition: Privacy Mode Product Design

### Origin
Guiding Light, 2026-03-10, during post-expedition discussion.

### The Idea
Privacy mode isn't a compromise — it's a trust feature. The product should still work well WITH privacy mode on. "Of course the product will be better if it didn't have it on privacy mode, but we can do so much with it still."

### Research Questions
1. How do comparable products handle privacy/pause modes? (Apple Screen Time, Focus modes, Firefox tracking protection)
2. What features should STILL work in privacy mode? (Live process view without memory? Device mesh connection? Basic alerts?)
3. What's the UX of privacy mode? Always visible toggle? Scheduled privacy hours? Per-app exclusions?
4. How do you communicate "privacy mode is on" without making the user feel guilty?
5. What's the graceful degradation path? (Full awareness → privacy mode → fully off)

### Guiding Light's Words
"We just need to remember that privacy and not hide it. Of course the product will be better if it didn't have it on privacy mode, but we can do so much with it still."

---

## Expedition: Submantle as Payment Processor for Agents

### Origin
Guiding Light, 2026-03-10, during post-expedition discussion.

### The Idea
Submantle isn't just a product that uses Stripe for billing. Submantle IS the payment layer for agent transactions. Designed specifically for ease of agent transaction. Code designed to make agent usage "not only easier, but more attractive to use just from a design perspective."

### Research Questions
1. What makes an agent "prefer" one payment rail over another? (API simplicity, speed, reliability, documentation quality)
2. Can API design aesthetics influence agent developer adoption? (Clean vs messy APIs, developer experience as competitive moat)
3. How do credit economies work at scale? (Gaming: V-Bucks, Robux. SaaS: Clay credits, OpenAI credits)
4. What's the regulatory landscape for credit-based payment systems? (Are credits regulated as stored value?)
5. What does "attractive to use from a design perspective" mean for an API? (DX research, developer satisfaction metrics)

### Guiding Light's Words
"Submantle will also be a payment processor, it will be focused on agent payments and code will be designed to make their usage not only easier, but more attractive to use just from a design perspective — if that means anything for AI preference in payment processor other than sheer financials."
