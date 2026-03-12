# Team 4 Findings: Protocol-Scale Infrastructure
## Date: 2026-03-10
## Researcher: Team Member 4

---

### Battle-Tested Approaches

---

#### 1. The Tailscale Architecture Model: Minimal Coordination Plane + P2P Data Plane

- **What:** A centralized coordination server that exchanges only encryption keys and policies (kilobytes per node), combined with a fully peer-to-peer data plane that carries all actual traffic end-to-end encrypted. The coordination server is a "shared drop box for public keys" — not a data relay.
- **Evidence:** Tailscale reached 10,000 paying business customers and 500,000+ weekly active users by January 2025, with a total user base in the millions. Their infrastructure team is **three engineers**. The DERP relay fleet (the fallback relay layer for traffic that cannot traverse NAT directly) runs on DigitalOcean, Vultr, and NetActuate. The coordination service handled over one million simultaneously connected nodes before sharding was required. Revenue is $45.2M on a 250-person company total.
- **Source:** https://tailscale.com/blog/how-tailscale-works (accessed 2026-03-10); https://tailscale.com/blog/infra-team-stays-small (accessed 2026-03-10); https://tailscale.com/blog/5000-customers (accessed 2026-03-10); https://getlatka.com/companies/tailscale.com (accessed 2026-03-10)
- **Fits our case because:** Submantle's coordination needs are even lighter than Tailscale's. Submantle doesn't route data — it distributes signature updates, broadcasts device discovery announcements, and answers agent queries. The control plane carries almost nothing. The coordination server is the right architecture: it manages membership and distributes updates; all actual awareness data stays on-device. This means Submantle can run a coordination server for millions of nodes on commodity infrastructure with a very small team.
- **Tradeoffs:** The coordination server is a single point of failure for control-plane functions (adding devices, pushing signature updates, managing access). Tailscale found sharding necessary at one million simultaneously connected nodes — a scale Submantle won't reach quickly, but the sharding requirement is a known engineering cost at that tier. Also: keeping the coordination server closed-source (as Tailscale does) is necessary to sustain the business, but creates community tension. Headscale — an independent reimplementation — emerged to address self-hosting demand.

---

#### 2. WireGuard's Design Philosophy: Radical Simplicity as a Scale Strategy

- **What:** WireGuard achieves global deployment on hundreds of millions of devices with a codebase under 4,000 lines (excluding crypto primitives). The entire design philosophy is: fewer lines = smaller attack surface = easier audit = faster inclusion in every OS.
- **Evidence:** WireGuard was merged into the Linux kernel (5.6, released March 2020). It is now the default VPN protocol in Android 13+, included in macOS 14+ kernel, and ships in every major Linux distribution. This was achieved by one person (Jason Donenfeld) writing code so simple it could be audited by any competent security engineer in a day. OpenVPN by comparison is 70,000 lines.
- **Source:** https://www.wireguard.com/papers/wireguard.pdf (accessed 2026-03-10); https://en.wikipedia.org/wiki/WireGuard (accessed 2026-03-10); https://www.wireguard.com/ (accessed 2026-03-10)
- **Fits our case because:** Submantle's daemon must be trusted by users to run persistently on their machines with elevated OS privileges. Trust is earned through auditability and simplicity. The WireGuard lesson applies directly: keep the daemon core small enough that a motivated security researcher can audit it in a weekend. "We're this small and do this little" is a stronger privacy claim than any policy document.
- **Tradeoffs:** WireGuard achieved kernel inclusion — a path Submantle cannot take for its daemon. WireGuard also does exactly one thing (VPN tunneling), while Submantle must do many things (process monitoring, device discovery, agent brokering, sync). The simplicity principle applies but cannot be applied as purely.

---

#### 3. Let's Encrypt's Automation-First Architecture

- **What:** Let's Encrypt automated every aspect of certificate issuance, validation, and renewal using the ACME protocol (RFC 8555). The result: 3 permanent engineers running infrastructure that issues 340,000 certificates per hour, protects 762 million websites, and is scaling toward 1 billion active certificates.
- **Evidence:** As of January 2025, Let's Encrypt's rate limiting system was rebuilt on Redis + GCRA, handling 30+ million unique rate limit entries. The new system produced an 80% reduction in MariaDB operations and a 99% drop in authorization table reads. The team that built this: 3 permanent engineers. Operating cost is donation-funded; initial sponsors included Mozilla, EFF, Cisco, and Akamai. First certificate issued September 14, 2015; 1 million certificates by March 2016 (6 months); 1 billion total by 2020; 10 million per day by September 2025.
- **Source:** https://letsencrypt.org/2025/12/09/10-years (accessed 2026-03-10); https://letsencrypt.org/2025/01/30/scaling-rate-limits (accessed 2026-03-10); https://www.bleepingcomputer.com/news/security/let-s-encrypt-issued-over-3-billion-certificates-securing-309m-sites-for-free/ (accessed 2026-03-10)
- **Fits our case because:** Let's Encrypt proves that a small team can run critical protocol infrastructure at internet scale if and only if the system is built for automation from day one. Every operation that touches a human is a bottleneck. Signature update distribution, device registration, and agent transaction settlement in Submantle must be designed the same way: zero human intervention per operation. The ACME model (standardized protocol, client-side automation, no human in the loop) is the right template for Submantle's update and registration flows.
- **Tradeoffs:** Let's Encrypt is a nonprofit funded by industry donations — no revenue pressure, no VC timeline. Submantle has commercial ambitions. Let's Encrypt's model of "build for the internet good" enabled partnerships with Mozilla, Chrome, and Apache that accelerated adoption. Submantle won't get those tailwinds automatically.

---

#### 4. Signal's Small-Team Large-Scale Privacy Infrastructure

- **What:** Signal runs E2E encrypted messaging for approximately 70 million monthly active users with approximately 50 full-time employees. Total infrastructure cost: ~$14 million/year. Total operating cost (including staff): ~$33 million/year projected to $50 million by 2025.
- **Evidence:** Signal's $14M/year infrastructure spans AWS, Google Compute Engine, and Microsoft Azure. The team of ~50 includes three separate client platform teams (Android, iOS, Desktop), server/infrastructure engineering, product, design, localization, and support. Signal introduced post-quantum encryption (SPQR/Triple Ratchet) in October 2025, peer-reviewed at Eurocrypt 2025. Signal's "Sealed Sender" protocol uses zero-knowledge proofs so even Signal cannot see who is messaging whom. In September 2025, Signal added E2E encrypted backups using zero-knowledge proofs.
- **Source:** https://signal.org/blog/signal-is-expensive/ (accessed 2026-03-10); https://cyberinsider.com/signal-estimates-operational-costs-to-reach-50-million-by-2025/ (accessed 2026-03-10); https://en.wikipedia.org/wiki/Signal_(software) (accessed 2026-03-10)
- **Fits our case because:** Signal demonstrates that privacy-first infrastructure at tens of millions of users is achievable with a lean team (~50 people) if the architecture does the privacy work at the protocol level rather than at the policy level. The "server sees nothing" model (E2E encryption, zero-knowledge proofs, sealed sender) is architecturally compatible with Submantle's cross-device sync requirements. Submantle's sync server should be designed so it literally cannot read user data — not as a policy but as a cryptographic guarantee.
- **Tradeoffs:** Signal is a nonprofit with $25.8M in 2024 revenue (donations). It burns money to run, which is why Meredith Whittaker regularly publicizes the costs. A commercial Submantle cannot use Signal's funding model. Signal also benefits from the protocol (Signal Protocol) being widely trusted and audited by the global security community — trust Submantle will need to earn.

---

#### 5. Tailscale's Open Source Strategy: Open Client, Closed Coordination

- **What:** Tailscale open-sources all clients for open-source operating systems (Linux, Android), the DERP relay server, and the WireGuard implementation. The coordination server stays closed. This provides auditability where it matters (client code that touches private keys) without open-sourcing the business-critical coordination infrastructure.
- **Evidence:** The Headscale project — a community-built open-source reimplementation of the Tailscale coordination server — emerged independently. Tailscale's response: hired the principal Headscale maintainer while keeping Headscale independent and compatible. The strategy acknowledges demand for self-hosting without undermining the managed service business. As of 2025, Tailscale continues this model.
- **Source:** https://tailscale.com/blog/opensource (accessed 2026-03-10); https://github.com/juanfont/headscale (accessed 2026-03-10)
- **Fits our case because:** Submantle needs the same split: open-source the daemon (what runs on user machines and touches their data) for auditability and trust; keep the coordination server and store infrastructure closed for business reasons. The existence of a community coordination server (equivalent to Headscale) is probably net-positive — it serves self-hosters without threatening the managed service business, and the maintained compatibility becomes a community trust signal.
- **Tradeoffs:** Keeping the coordination server closed means enterprise customers cannot self-audit the full stack. Some privacy-conscious users will self-host specifically to avoid the managed service. This is acceptable if the daemon is fully auditable.

---

#### 6. Auto-Update Distribution: Cross-Platform at Scale

- **What:** GoReleaser automates building and distributing Go binaries to Homebrew (macOS/Linux), Winget (Windows), Scoop (Windows), AUR (Arch Linux), GitHub Releases, and Nix simultaneously from a single CI pipeline.
- **Evidence:** GoReleaser is actively maintained in 2024-2026, adding Winget zip support and improved Scoop handling in 2024. Tailscale's distribution infrastructure uses platform-native mechanisms: APT/YUM/DNF repositories on Linux, App Store on macOS/iOS, Google Play on Android, MSI on Windows. Their installer script detects 25+ Linux distributions and selects the appropriate package type. The CI/CD pipeline tests across all supported distributions daily.
- **Source:** https://goreleaser.com/ (accessed 2026-03-10); https://deepwiki.com/tailscale/tailscale/8.3-installation-and-distribution (accessed 2026-03-10); https://omaha-consulting.com/best-update-framework-for-windows (accessed 2026-03-10)
- **Fits our case because:** Submantle needs to reach Windows (primary), macOS, and Linux from day one. GoReleaser handles this with a few CI configuration lines. The "one CI run → packages for every platform" model is achievable by a solo developer. The hard parts are platform-specific: Windows MSI signing, macOS notarization, and submitting to Linux repositories. These are one-time setup costs, not ongoing maintenance.
- **Tradeoffs:** App Store (macOS) and Google Play (Android) add review delay and platform policy risk. Linux package managers have varying acceptance timelines. MSI signing requires a code-signing certificate (currently ~$200-500/year). MacOS notarization requires an Apple Developer account ($99/year). These are costs, not blockers.

---

### Novel Approaches

---

#### 7. The "Piggybacking" Model: Infrastructure That Runs on Your Infrastructure

- **What:** Instead of building dedicated relay infrastructure, design Submantle's coordination layer to run as a lightweight sidecar on existing infrastructure users already run (GitHub Releases for signature updates, Cloudflare Workers for coordination API, S3-compatible storage for encrypted sync).
- **Why it's interesting:** Submantle's coordination server carries almost nothing per node — device registration events, signature update manifests, and encrypted sync blobs. This is a radically different load profile from Tailscale (which must relay encrypted packets for nodes behind strict NATs) or Signal (which relays all messages). Submantle's entire coordination payload for 1 million nodes might be manageable with a single Cloudflare Worker and an R2 bucket.
- **Evidence:** Flagsmith runs billions of feature flag evaluations per month for ~$1,200/month at its current scale on AWS ECS + RDS + CloudFront. That is application-level complexity. Submantle's coordination server is simpler: key-value lookups for device registration, blob storage for encrypted sync, and CDN-cached signature manifests. Cloudflare Workers cost $0.10 per million invocations (free tier: 100,000/day). R2 (S3-compatible) has no egress fees.
- **Source:** https://www.flagsmith.com/blog/infrastructure-costs (accessed 2026-03-10); https://workers.cloudflare.com/ (accessed 2026-03-10)
- **Fits our case because:** A solo founder cannot afford Signal's $14M/year infrastructure. But Submantle's coordination needs are not Signal's. If the daemon does all processing locally and the coordination server only distributes updates and relays encrypted blobs, the cloud cost to serve 100,000 users could be under $500/month. This makes bootstrapping to 100,000 users financially viable without VC.
- **Risks:** Cloudflare Workers has a 10ms CPU time limit per request on the free tier (50ms on paid). Complex coordination logic that exceeds this must be redesigned. Vendor lock-in to Cloudflare. Cloudflare outages become Submantle outages (though local daemons continue working without coordination — they just can't receive updates).

---

#### 8. Headscale/Self-Hosting as a Community Trust Strategy

- **What:** Release a reference implementation of the Submantle coordination server under an open license, specifically designed for self-hosting, alongside the closed managed service.
- **Why it's interesting:** Headscale has 30,000+ GitHub stars (top 200 Go projects globally) despite being a community project that Tailscale did not build. It demonstrates that self-hosting demand for privacy-sensitive infrastructure is real and enthusiastic. Rather than fighting this demand, embracing it builds community trust and free adoption evangelism.
- **Evidence:** Tailscale hired the principal Headscale maintainer while keeping the project independent. The Headscale HN thread in March 2026 attracted 250+ comments. The self-hosting community on r/selfhosted (1M+ members) is a reliable early adopter pool for privacy infrastructure tools.
- **Source:** https://github.com/juanfont/headscale (accessed 2026-03-10); https://news.ycombinator.com/item?id=43563396 (accessed 2026-03-10)
- **Fits our case because:** Submantle's privacy claims ("we cannot read your data") are stronger if a self-hosted coordination server exists. Users who self-host are the loudest evangelists. The first 1,000 users of a privacy-first daemon tool will very likely come from the self-hosting community.
- **Risks:** A well-built self-hosted coordination server reduces switching costs, making it easier for users to leave the managed service. The key is ensuring the managed service provides enough value beyond coordination (e.g., the Submantle Store, certified identity packs, agent transaction settlement) that self-hosters who want the full product still pay.

---

### Emerging Approaches

---

#### 9. Local-First with Thin Coordination: The CRDT + Relay Hybrid

- **What:** Build the sync layer on CRDTs (Conflict-Free Replicated Data Types) with a minimal relay server that stores only encrypted blobs, enabling devices to sync directly (peer-to-peer when possible, relay when needed) without the server understanding any data.
- **Momentum:** Local-first software is compared to "React in 2013" — gaining engineering community interest rapidly. Automerge 3 (Rust core, multi-language bindings) and Yjs are production-ready. The first Programming Local-first Software academic workshop (PLF 2024, collocated with ISSTA/ECOOP) ran in 2024, signaling academic legitimacy. Projects like Linear, Figma, and Notion use CRDT-adjacent approaches.
- **Source:** https://dev.to/bertrand_atemkeng/why-local-first-and-offline-first-software-is-the-future-7mf (accessed 2026-03-10); https://conf.researchr.org/home/issta-ecoop-2024/plf-2024 (accessed 2026-03-10)
- **Fits our case because:** Submantle's state that needs cross-device sync (device registry, workflow history, user labels) maps well to append-only event logs and CRDT merge semantics. If sync is CRDT-based and the relay server stores only ciphertext, the relay infrastructure is minimal (essentially an S3 bucket with WebSocket notification). This keeps operating costs near zero until very large scale.
- **Maturity risk:** CRDT overhead (tombstones, metadata) grows over time and can become a performance/storage problem for long-lived datastores. The local-first ecosystem does not yet have a dominant, production-proven stack across all Submantle's target platforms (Go, Android, eventually iOS). Automerge has Go bindings but they lag the Rust/TypeScript implementations in maturity.

---

#### 10. Cloudflare Workers + Durable Objects as Coordination Infrastructure

- **What:** Use Cloudflare Workers (serverless edge compute) with Durable Objects (stateful, consistent, globally distributed objects) as the coordination server backend. Each Submantle node's state lives in a Durable Object; signature update manifests are served from Cloudflare's CDN globally.
- **Momentum:** Cloudflare Workers now runs in 330+ cities across 122+ countries, reaching within 50ms of 95% of the world's internet population. Durable Objects provide strongly consistent per-object state without managing a database. Workers AI is available at the edge. Cloudflare R2 has no egress fees. Workers free tier: 100,000 requests/day.
- **Source:** https://www.gocodea.com/post/what-are-cloudflare-workers-edge-computing-for-ultra-fast-web-apps (accessed 2026-03-10); https://developers.cloudflare.com/durable-objects/ (accessed 2026-03-10)
- **Fits our case because:** Submantle's coordination server does relatively few, simple operations: register a node (write), fetch signature updates (read from CDN), push encrypted sync blob (write), receive notification that a device came online (event). Durable Objects are exactly the right primitive: one object per user, strongly consistent, globally distributed. Zero infrastructure to manage.
- **Maturity risk:** Durable Objects are production-ready but still evolving. The 10ms CPU limit per Worker invocation constrains complex logic. Vendor lock-in to Cloudflare is real — migrating off would require rewriting the coordination server. Cloudflare's free tier limits (100k requests/day) work at small scale but beyond that the costs scale with usage.

---

### Gaps and Unknowns

1. **What does Submantle's coordination server actually need to do at scale?** The research establishes that the coordination plane should carry minimal traffic (keys, updates, encrypted blobs). But the specific data model for Submantle — device registry entries, signature manifest distribution, agent transaction settlement, encrypted sync blobs — has not been fully designed. The cost and architecture implications depend heavily on these specifics.

2. **Signature manifest distribution at scale.** Let's Encrypt distributes certificate revocation lists (CRLs) at scale using CDN-cached static files. Submantle's signature pack distribution should work similarly. But signature packs are community-contributed and may update frequently. The CDN invalidation strategy and update frequency need design work.

3. **Agent transaction settlement infrastructure.** Transaction settlement at microfee scale (millions of queries per day at sub-cent fees) requires specialized infrastructure: payment processor integration, fraud detection, settlement batching. This is not covered by the protocol scale research — it's a separate domain (addressed by Team 2's findings).

4. **The "Tailscale sharding problem" for Submantle.** Tailscale's coordination server handled 1 million simultaneously connected nodes before sharding was needed. Submantle's coordination load per node is lighter (no relay traffic), so the sharding threshold is probably higher. But what exactly triggers Submantle's coordination server sharding need? Unanswered.

5. **Backward compatibility versioning strategy.** Tailscale treats "backward compatible forever" as a core principle. The MCP protocol uses date-based versioning. WireGuard does not version (the protocol is frozen by design). Submantle needs a versioning strategy for: the daemon protocol, the signature format, the agent query API, and the sync protocol. These four versioning problems have different constraints. No clear answer emerged from research.

6. **The cost cliff at 1 million users.** The research validates very low costs at 1,000-100,000 users with light coordination architecture. At 1 million+ simultaneously connected nodes, Tailscale needed to shard their coordination server. What does that cost inflection look like for Submantle? Not determined.

7. **Package manager acceptance timelines.** Homebrew tap (self-managed, immediate), Winget (Microsoft review, days to weeks), Scoop (community PR, days), APT/YUM (typically self-hosted repo, immediate), Snap/Flatpak (review process, weeks). App Store: weeks to months. These timelines affect launch strategy but weren't precisely mapped.

---

### Synthesis

#### The Core Finding: Protocol Scale Is Not the Hard Problem

The research across Tailscale, WireGuard, Let's Encrypt, and Signal converges on a counterintuitive conclusion: **running protocol infrastructure at hundreds of millions of endpoints is not the hard engineering problem.** The hard problem is getting to the first 100,000 users. The infrastructure cost and complexity to serve 1 to 100,000 users is well within solo-founder reach.

The evidence:
- Tailscale's entire infrastructure team is **3 engineers** serving millions of active users
- Let's Encrypt's core engineering team is **3 permanent engineers** serving 762 million websites
- Signal runs global encrypted messaging for 70 million users with **50 total employees**
- WireGuard was built by **one person** and is now deployed on hundreds of millions of devices

This is only possible because of architectural decisions made early:
1. **Minimal coordination, maximum local.** The coordination server carries almost nothing — keys and policies, not data. All the work happens on-device.
2. **Automation-first.** Every operation that can be automated is automated. No human touches a per-node operation.
3. **The right protocol eliminates most of the load.** WireGuard's cryptokey routing means the coordination server only needs to distribute public keys — the nodes do all the hard networking work themselves.

#### What This Means for Submantle

Submantle's architecture, as designed, follows these principles:
- **Daemon does the work locally.** Process scanning, signature matching, workflow graph — all on-device.
- **Coordination server distributes only updates and relayed blobs.** Signature pack manifests, device registration, encrypted sync. This is genuinely light traffic.
- **Agent queries go directly to the local daemon.** No cloud round-trip for agent queries — the local gRPC socket handles all of this.

This means Submantle's coordination server can be extremely simple and cheap to run. The Cloudflare Workers + R2 model (or a single small VPS with PostgreSQL) could handle 100,000 active nodes. Sharding is a problem for when you have 1 million simultaneously connected nodes — which is a good problem to have.

#### The Realistic Solo Founder Scale Ladder

Based on evidence from Tailscale's early growth and solo SaaS infrastructure research:

| Scale | Infrastructure | Monthly Cost | Team Needed |
|-------|---------------|-------------|-------------|
| 0 → 1,000 users | Single VPS (DigitalOcean $20/mo), GitHub Releases for binary distribution, Homebrew tap | ~$50/month | Solo |
| 1,000 → 10,000 users | Same VPS + managed Postgres, CDN for signature packs, GoReleaser CI | ~$200/month | Solo |
| 10,000 → 100,000 users | Vertical scale VPS + read replicas, CDN, possibly load balancer | ~$500-1,500/month | Solo + 1-2 contractors |
| 100,000 → 1M users | Horizontal scale, coordination server sharding, dedicated infra team | ~$5,000-20,000/month | 3-5 infra engineers |
| 1M+ users | Full distributed coordination, multiple regions | ~$50k+/month | Dedicated infra team |

The "can a solo founder bootstrap" question has a clear answer: **yes, to 10,000 users, comfortably.** Reaching 100,000 requires more infrastructure sophistication but not a team. The inflection point where infrastructure stops being a solo job is somewhere in the 100,000-1,000,000 range.

#### The Adoption Playbook: What Works for Protocol Daemons

From the evidence:

1. **Show HN launch.** Research shows HN exposure averages 121 GitHub stars in 24 hours, with viral asymmetry meaning a minority of launches get 10x that. A well-timed Show HN post with a working demo is the highest-ROI launch action for a developer daemon tool. Tailscale was discovered this way by its early users.

2. **Homebrew as the macOS on-ramp.** Homebrew is the de facto developer package manager for macOS. A Homebrew tap (self-hosted formula, no review required) can be live the day of launch. `brew install substrate` is the correct first-install experience for the target user.

3. **Bottom-up enterprise.** Tailscale's growth model: individual developers adopt it personally → use it for homelab → bring it to work → IT buys it. Submantle should design for the same vector: AI agent developers adopt it for their own development workflow → integrate it into their tools → enterprise buys the Pro/Team tier.

4. **Open-source the daemon core.** Every comparable protocol tool that achieved ubiquity is open-source at the core. WireGuard (GPL), Tailscale client (BSD), Signal Protocol (AGPL). Open-sourcing the daemon creates auditability, community trust, and free distribution channels (GitHub stars as social proof, awesome-lists, r/selfhosted evangelism). The Submantle Store and coordination server can remain closed.

5. **Self-hosting community as the launchpad.** r/selfhosted (1M+ members), r/homelab, the Hacker News audience — these are exactly the people who will install a Go daemon, configure it, and write blog posts about it. They reach the broader developer audience. They are the first 1,000 users.

#### The Strongest Combination of Approaches

For Submantle's specific constraints (solo founder, privacy-first, bootstrappable, Go daemon):

- **Day 1 infrastructure:** Single VPS + GitHub Releases + GoReleaser + Homebrew tap. Cost: $20-50/month.
- **Coordination server:** Cloudflare Workers + R2 for the first 100,000 users. Zero egress fees, global CDN, near-zero operational overhead.
- **Open source model:** Daemon core open (GitHub, BSD or Apache 2.0). Coordination server and Submantle Store closed. Self-hosted coordination server released as a reference implementation (Headscale model).
- **Sync model:** E2E encrypted relay (1Password trust model) with append-only event logs. Simple, proven, no CRDT complexity at V1.
- **Update distribution:** GoReleaser automates everything. Platform-native channels (App Store, Google Play) for mobile. Background auto-update for the daemon (platform-native mechanisms on Windows/macOS/Linux).
- **Backward compatibility:** Freeze the agent query API at v1 and version it like MCP (date-based). Never break it. Add capabilities via extensions, not replacements.

#### What the Orchestrator Needs to Know

1. **The coordination server is not the hard part.** Don't over-engineer it. A single engineer can run the coordination infrastructure for the first 100,000 users. The hard part is building the daemon (which the first expedition already validated is achievable).

2. **The real scale risk is adoption, not infrastructure.** Tailscale's coordination server handled 1 million nodes before needing to shard. Submantle will not get to 1 million nodes before it becomes clear whether it has product-market fit. Build for 10,000 nodes and design for 1 million — don't build for 1 million on day one.

3. **The WireGuard lesson is the most important.** Radical simplicity in the daemon core builds trust faster than any feature. "4,000 lines" is a credible privacy claim. Keep the daemon small, auditable, and doing exactly one thing well.

4. **Let's Encrypt's team-to-scale ratio is the benchmark.** 3 engineers, 762 million websites. That ratio is achievable only with automation-first design. Every operation that requires a human is a scaling ceiling. Design Submantle's operations (signature pack review, agent certification, user support) with that constraint in mind.

5. **Signal's $14M/year infrastructure cost is the upper bound, not a floor.** Signal relays billions of messages. Submantle's coordination server relays nothing — it distributes updates and stores encrypted blobs. The infrastructure cost should be 1-2 orders of magnitude less than Signal's, especially in the early years.

6. **The 50-employee company serving 70 million users is a credible target.** Signal at 50 people, $14M infrastructure, 70M users is evidence that a small team can run global-scale privacy infrastructure. The bottleneck is not headcount — it is architectural discipline.

---

*Sources referenced in this document:*
- https://tailscale.com/blog/how-tailscale-works
- https://tailscale.com/blog/infra-team-stays-small
- https://tailscale.com/blog/5000-customers
- https://tailscale.com/blog/hypergrowth-isnt-always-easy
- https://tailscale.com/blog/opensource
- https://getlatka.com/companies/tailscale.com
- https://tailscale.com/blog/welcome-grace-lin-10000-customers
- https://betakit.com/tailscale-hits-10000-paid-business-clients-after-doubling-customer-base-in-past-10-months/
- https://deepwiki.com/tailscale/tailscale/8.3-installation-and-distribution
- https://www.wireguard.com/papers/wireguard.pdf
- https://www.wireguard.com/
- https://en.wikipedia.org/wiki/WireGuard
- https://letsencrypt.org/2025/12/09/10-years
- https://letsencrypt.org/2025/01/30/scaling-rate-limits
- https://www.bleepingcomputer.com/news/security/let-s-encrypt-issued-over-3-billion-certificates-securing-309m-sites-for-free/
- https://blog.apnic.net/2025/02/06/lets-encrypt-scales-rate-limits-to-prepare-for-a-billion-active-certificates/
- https://signal.org/blog/signal-is-expensive/
- https://cyberinsider.com/signal-estimates-operational-costs-to-reach-50-million-by-2025/
- https://en.wikipedia.org/wiki/Signal_(software)
- https://electroiq.com/stats/signal-statistics/
- https://signal.org/blog/sealed-sender/
- https://github.com/juanfont/headscale
- https://news.ycombinator.com/item?id=43563396
- https://goreleaser.com/
- https://deepwiki.com/tailscale/tailscale
- https://omaha-consulting.com/best-update-framework-for-windows
- https://www.flagsmith.com/blog/infrastructure-costs
- https://workers.cloudflare.com/
- https://dev.to/bertrand_atemkeng/why-local-first-and-offline-first-software-is-the-future-7mf
- https://conf.researchr.org/home/issta-ecoop-2024/plf-2024
- https://arxiv.org/html/2511.04453v1
- https://insightpartners.com/ideas/tailscale-leadership-story/
