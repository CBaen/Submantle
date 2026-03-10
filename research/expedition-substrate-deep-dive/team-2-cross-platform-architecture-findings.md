# Team 2 Findings: Cross-Platform Architecture
## Date: 2026-03-10
## Researcher: Team Member 2

---

## Scope

This covers seven angles: language choice for the daemon, OS-specific process APIs, knowledge graph storage, IPC/API layer, plugin architecture, cross-device sync, and mobile platform constraints.

---

## 1. Language Evaluation: Rust vs Go vs C++

### Battle-Tested Approaches

**Go — the dominant choice for cross-platform system daemons**
- **What:** Go produces a single statically-linked binary that runs on all target platforms with minimal FFI complexity, a garbage collector tuned for low-latency, and a rich ecosystem for system-level work.
- **Evidence:** Tailscale's daemon (`tailscaled`) is written in Go and runs on Windows, macOS, Linux, FreeBSD, and OpenBSD. Docker's daemon is Go. Kubernetes is Go. HashiCorp's entire tool suite (Terraform, Vault, Nomad) is Go. This is the most proven language for "cross-platform daemon that must ship as a binary."
- **Source:** https://github.com/tailscale/tailscale (accessed 2026-03-10); https://blog.jetbrains.com/rust/2025/06/12/rust-vs-go/ (accessed 2026-03-10)
- **Fits our case because:** Substrate is a daemon, not a hot path. Development velocity matters enormously at POC stage. Cross-platform service management is well-solved in Go. The goroutine model makes concurrent event handling from multiple OS sources natural.
- **Tradeoffs:** Go's GC adds ~10% memory overhead and occasional pauses. Binary size is larger than Rust before optimization (typically 10-20MB vs 2-5MB). Memory consumption for equivalent Go services runs 100-320 MB vs Rust's 50-80 MB. Not ideal if memory is the hard constraint.

### Novel Approaches

**Rust — rising challenger with superior memory efficiency**
- **What:** Rust produces binaries with no GC overhead, predictable memory layout, and compile-time safety for concurrent code. As of 2025, Rust is a permanent part of the Linux kernel. Android 16 ships Rust-built memory allocator components.
- **Why interesting:** For a daemon that must run 24/7 at minimal CPU/memory cost, Rust's 50-80 MB vs Go's 100-320 MB matters. On mobile (Android), where the OS will kill background processes based on memory pressure, this gap is meaningful.
- **Evidence:** Cloudflare uses Rust for system-critical components. Discord migrated to Rust/Actix-web and cut latency by 50%. Rust Actix-web runs ~1.5x faster than Go Fiber with 20% lower memory usage (TechEmpower Round 23 benchmarks). The `service-manager` crate provides unified Windows SCM / macOS launchd / Linux systemd service registration.
- **Source:** https://byteiota.com/rust-vs-go-2026-backend-performance-benchmarks/ (accessed 2026-03-10); https://crates.io/crates/uni_service_manager (accessed 2026-03-10)
- **Fits our case because:** If Substrate ever needs to run on Android or resource-constrained devices, Rust's memory discipline becomes critical. Also, a process-monitoring daemon is exactly the kind of system-adjacent code where Rust's memory safety prevents a class of bugs that would be embarrassing for a product selling "awareness."
- **Risks:** Rust has a steep learning curve. Development velocity is significantly slower. For a solo or small team at POC stage, this is a real cost. Cross-platform service registration is less battle-tested than Go equivalents (though `uni_service_manager` and `service-manager` crates exist).

**C++ — not recommended**
- C++ is used in the macOS `sysmond` daemon and various OS internals, but it offers no meaningful advantage over Rust for new cross-platform code and adds manual memory management without the safety guarantees. The main argument for C++ (ecosystem maturity) is less compelling in 2026 than it was five years ago.

### Synthesis: Language Decision

**Recommendation: Go for POC and V1. Evaluate Rust migration for performance-sensitive components at V2.**

The entire community of comparable tools (Tailscale, Docker, Kubernetes, HashiCorp suite) chose Go for exactly this use case. The cross-platform service management story in Go is mature. Development velocity at early stage is not a nice-to-have — it determines whether the project gets built at all. Rust can be adopted incrementally (via FFI from Go, or for specific OS-API bindings) once the architecture is proven.

---

## 2. OS-Specific Process APIs

### Windows

**Battle-Tested: Win32 Process API + ETW**
- **What:** `OpenProcess`, `EnumProcesses`, `CreateToolhelp32Snapshot` provide the basic process list. ETW (Event Tracing for Windows) provides real-time event streams for process start/stop, thread creation, and image loading.
- **Evidence:** ETW is the mechanism used by Windows Defender, Sysmon, Splunk's Windows agent, and every professional EDR product. WMI (`Win32_Process` class) provides a higher-level query interface over the same data, used in production monitoring at scale.
- **Source:** https://learn.microsoft.com/en-us/windows/win32/etw/event-tracing-portal (accessed 2026-03-10); https://benjitrapp.github.io/defenses/2024-02-11-etw/ (accessed 2026-03-10)
- **Fits our case because:** ETW delivers process lifecycle events without polling. It's the same mechanism every serious Windows monitoring tool uses. WMI provides higher-level enrichment (parent PID, command line, user, etc.).
- **Tradeoffs:** ETW consumers need elevated privileges. WMI queries are slower than direct Win32 calls. ETW's API surface is complex — third-party libraries (like `ferrisetw` in Rust or various Go wrappers) simplify it significantly.

### macOS

**Battle-Tested: libproc + BSD sysctl**
- **What:** `proc_listpids` enumerates PIDs. `proc_pidinfo` with `PROC_PIDPATHINFO` gets the executable path. `sysctl(KERN_PROC)` gets full process list with metadata. The `sysmond` daemon (accessible via `libsysmon.dylib` XPC) is what Activity Monitor uses internally.
- **Evidence:** These are the standard, undeprecated interfaces. `libproc-rs` is an actively maintained Rust crate wrapping them. `proc_info` calls require no special privileges for listing own or any-user processes (basic metadata is accessible to any user, per BSD tradition).
- **Source:** https://github.com/andrewdavidmackenzie/libproc-rs (accessed 2026-03-10); https://developer.apple.com/forums/thread/655349 (accessed 2026-03-10)
- **Fits our case because:** These APIs are stable, available without root, and sufficient for the "know what processes are running and what they are" use case.
- **Tradeoffs:** Apple's `Endpoint Security Framework` provides richer real-time events (process launch/exit, file access) but requires a System Extension and explicit user approval in macOS 12+. For a privacy-respecting daemon that "never acts," the simpler libproc approach avoids those friction points.

### Linux

**Battle-Tested: procfs + Netlink Process Connector**
- **What:** `/proc/[pid]/` contains everything — status, cmdline, exe symlink, fd directory, maps. The Netlink Process Connector (`CN_IDX_PROC`) delivers events for fork, exec, exit, UID/GID changes over a socket.
- **Evidence:** osquery (Facebook/Meta) uses the Linux Audit System (auditing `execve` syscalls) for process monitoring at enterprise scale. Forkstat, available in most distribution repositories, uses Netlink and is considered production-stable for similar work. Slack's engineering team documented syscall auditing at scale using the same kernel interfaces.
- **Source:** https://github.com/konstantin89/linux-netlink-process-monitoring (accessed 2026-03-10); https://slack.engineering/syscall-auditing-at-scale/ (accessed 2026-03-10); https://docs.kernel.org/filesystems/proc.html (accessed 2026-03-10)
- **Fits our case because:** procfs polling is the simplest approach (no privileges needed for basic data). Netlink gives event-driven updates. Both are standard kernel interfaces, not deprecated.
- **Tradeoffs:** Netlink Process Connector may miss events under heavy load (known limitation; documented by forkstat maintainers). Requires root or `CAP_NET_ADMIN` for Netlink. procfs polling has O(process_count) cost per cycle. For high-fidelity monitoring, augmenting with eBPF (in kernel 4.18+) is the emerging best practice but adds complexity.

### Android

**What's actually accessible without root:**
- **`ActivityManager.getRunningAppProcesses()`** — returns a list of running app processes with importance level (foreground vs background). As of Android 5+ (API 21+), this returns only your own processes and a subset of visible ones. Full enumeration was restricted for privacy in Android 7+.
- **`UsageStatsManager`** — returns app usage statistics by time window. Requires `PACKAGE_USAGE_STATS` permission (granted by user in Settings). This is the realistic path for "what apps has the user been using."
- **`ActivityManager.RunningAppProcessInfo`** — provides importance level: `IMPORTANCE_FOREGROUND`, `IMPORTANCE_VISIBLE`, `IMPORTANCE_SERVICE`, `IMPORTANCE_CACHED`. Sufficient to know "what is active right now."
- **Evidence:** Android 15 added `ProfilingManager` and `ApplicationStartInfo` for process diagnostics. Android 16 continues tightening background restrictions.
- **Source:** https://developer.android.com/reference/android/app/ActivityManager (accessed 2026-03-10); https://softices.com/blogs/android-foreground-services-types-permissions-use-cases-limitations (accessed 2026-03-10)
- **Tradeoffs:** You cannot enumerate all processes on Android as a third-party app. The platform intentionally limits this. The realistic scope for Substrate on Android is "what apps are in use" (via UsageStats) rather than "what processes are running."

### iOS

**What's actually accessible:**
- Essentially nothing for process enumeration. iOS provides no public API for listing other processes. There is no equivalent of `proc_listpids` for third-party apps on iOS.
- What IS accessible: `BGAppRefreshTask` (periodic, system-scheduled, ~30 seconds), `BGProcessingTask` (longer, up to several minutes, requires charging + Wi-Fi typically), and the new iOS 26 `BGContinuedProcessingTask` (user-initiated only, continues a task started in foreground).
- iOS 26 `BGContinuedProcessingTask` explicitly requires "a button tap or gesture, never automatic." It is not a mechanism for background monitoring.
- **Evidence:** https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtask (accessed 2026-03-10); https://dev.to/arshtechpro/wwdc-2025-ios-26-background-apis-explained-bgcontinuedprocessingtask-changes-everything-9b5 (accessed 2026-03-10)
- **Honest assessment:** Substrate cannot be a process-monitoring daemon on iOS. The platform's sandboxing and background execution model makes this architecturally impossible without OS vendor cooperation — which the project constraints explicitly exclude. The iOS surface for Substrate is limited to: receiving sync data from other platforms, providing a query interface for AI agents running on iOS, and surfacing context that was built on other devices.

---

## 3. Knowledge Graph Storage

### Battle-Tested Approaches

**SQLite as the primary store with graph queries in application code**
- **What:** SQLite stores nodes and edges as tables. Graph traversal is implemented as recursive CTEs or application-side BFS/DFS. This is the approach used by almost every mobile and embedded application that needs relationship data without a dedicated graph engine.
- **Evidence:** SQLite is used in every iOS app, most Android apps, Firefox, Chrome, and countless embedded systems. It is the most deployed database in the world. Its WAL mode supports concurrent reads with a single writer efficiently. Total binary size for SQLite itself: ~1MB.
- **Source:** https://duckdb.org/docs/stable/guides/sql_features/graph_queries (accessed 2026-03-10)
- **Fits our case because:** Process graphs are not deeply nested (typical depth: 3-5 levels, parent-child-grandchild process trees). Workflow relationships are sparse. SQLite handles this comfortably with recursive CTEs. The entire state can be in-memory (SQLite supports `:memory:`) for hot reads, persisted to disk for durability.
- **Tradeoffs:** You write the graph traversal logic yourself. No Cypher, no SPARQL. For complex multi-hop queries ("find all processes transitively connected to this file"), recursive CTEs become verbose. This is an implementation cost, not an architectural blocker.

**DuckDB with DuckPGQ extension**
- **What:** DuckDB is an in-process analytical database. The DuckPGQ extension implements SQL/PGQ (the graph query syntax from SQL:2023), enabling Cypher-like graph queries over DuckDB tables.
- **Evidence:** DuckPGQ is a community extension, actively maintained. DuckDB itself is production-proven (Motherduck, many analytics teams). The extension supports graph algorithms and path queries.
- **Source:** https://duckdb.org/community_extensions/extensions/duckpgq (accessed 2026-03-10); https://thedataquarry.com/blog/embedded-db-1/ (accessed 2026-03-10)
- **Fits our case because:** If Substrate needs to answer analytical queries ("show me workflow patterns over the last 30 days"), DuckDB's columnar storage is faster than row-oriented SQLite. DuckPGQ adds graph query syntax without a separate graph database.
- **Tradeoffs:** DuckPGQ is still a community extension, not a core feature — maturity risk. DuckDB's binary size is larger (~35MB). It is optimized for read-heavy analytics, not write-heavy event ingestion.

### Novel Approaches

**FalkorDB Lite (embedded property graph, subprocess model)**
- **What:** FalkorDB Lite runs the FalkorDB graph engine as a forked subprocess, communicating via Unix socket. No Docker, no server, no configuration. File-based persistence.
- **Evidence:** Available as a Python library. Uses sparse matrices (GraphBLAS) for adjacency representation, which is memory-efficient for sparse graphs. Announced as an alternative after KuzuDB's archival in October 2025.
- **Source:** https://www.falkordb.com/blog/falkordblite-embedded-python-graph-database/ (accessed 2026-03-10)
- **Fits our case because:** Provides full Cypher query support. The subprocess isolation model means a crash in the graph engine doesn't crash the daemon.
- **Risks:** Currently Python-only and Linux/macOS only (no Windows). This is a hard blocker for Substrate's Windows requirement. Not suitable as the primary store without a cross-platform implementation.

**KuzuDB forks (Ladybug, Bighorn, RyuGraph)**
- **What:** After KuzuDB was archived in October 2025, three community forks emerged: Ladybug (by ex-Facebook/Google engineers), Bighorn (by Kineviz), and RyuGraph (by Predictable Labs). KuzuDB was the leading embedded property graph database with Cypher support and C/Rust/Python bindings.
- **Evidence:** KuzuDB's archival was covered by The Register. Community response was immediate with multiple forks launching within weeks.
- **Source:** https://www.theregister.com/2025/10/14/kuzudb_abandoned/ (accessed 2026-03-10); https://github.com/predictable-labs/ryugraph (accessed 2026-03-10)
- **Fits our case because:** The original KuzuDB had C++ bindings usable from Rust/Go. If a fork stabilizes, it would provide a true embedded property graph.
- **Maturity risk:** All three forks are months old as of March 2026. None has a track record in production. Betting on a fork for a core storage layer is a risky dependency choice at this stage.

### Synthesis: Storage Decision

**Recommendation: SQLite (in-memory + WAL persistence) for the POC and V1.**

The process relationship graph for a single machine is small — hundreds to low thousands of nodes. SQLite with recursive CTEs is sufficient, battle-tested, and available everywhere. If/when query complexity grows or analytical workloads emerge, a migration path to DuckDB + DuckPGQ exists. Pure graph database options (KuzuDB forks, FalkorDB) are either too immature or platform-restricted to rely on.

---

## 4. IPC/API Layer

### Battle-Tested Approaches

**gRPC over Unix domain sockets (Linux/macOS) + Named Pipes (Windows)**
- **What:** gRPC transports over local sockets instead of TCP. On Linux/macOS, Unix domain sockets (`unix:///path/to/socket`). On Windows, Named Pipes. This is exactly how Docker's daemon (`dockerd`) exposes its API — via `unix:///var/run/docker.sock` on Linux/macOS and `npipe:////./pipe/docker_engine` on Windows.
- **Evidence:** Docker daemon uses this architecture. gRPC over Unix socket adds ~100µs latency overhead for local IPC (measured), which is negligible for a context broker. Benchmarks show Unix domain sockets and Named Pipes outperform TCP/IP for local communication by avoiding networking overhead. Microsoft's ASP.NET Core documentation explicitly covers gRPC over Named Pipes for Windows IPC.
- **Source:** https://learn.microsoft.com/en-us/aspnet/core/grpc/interprocess-uds (accessed 2026-03-10); https://learn.microsoft.com/en-us/aspnet/core/grpc/interprocess-namedpipes (accessed 2026-03-10); https://www.mpi-hd.mpg.de/personalhomes/fwerner/research/2021/09/grpc-for-ipc/ (accessed 2026-03-10)
- **Fits our case because:** Strongly-typed, versioned interfaces via Protobuf — critical when agents from different vendors query Substrate. Language-agnostic (any language with gRPC bindings can be an agent). Streaming support for real-time event subscriptions. Docker's use of this exact pattern for daemon-to-client communication is the closest real-world precedent.
- **Tradeoffs:** More setup than a simple REST API. Proto definitions add overhead. Requires gRPC library in every client. Raw gRPC over UDS is ~10x slower than blocking I/O over the same socket, but still fast enough (sub-millisecond) for this use case.

**REST over HTTP/local socket**
- **What:** HTTP server on localhost with a REST API. Used by VS Code's extension system (JSON-RPC over the Language Server Protocol), many IDE extensions, and Claude Desktop's MCP connections.
- **Evidence:** VS Code extensions communicate via JSON-RPC 2.0, which runs over stdio or local sockets. Language servers are standalone processes communicating with the host over this protocol.
- **Source:** https://code.visualstudio.com/api/language-extensions/language-server-extension-guide (accessed 2026-03-10)
- **Fits our case because:** Simpler for third-party developers to integrate with. curl-debuggable. Every language has an HTTP client. Good for the "agent query" pattern where the interaction is request/response.
- **Tradeoffs:** No streaming primitives (WebSockets required for events). No built-in schema enforcement. Less suitable for the event subscription use case (agents wanting live process change notifications).

### Synthesis: IPC Decision

**Recommendation: gRPC over Unix socket (Linux/macOS) and Named Pipe (Windows), with a REST/HTTP fallback for simple queries.**

This mirrors Docker's architecture exactly. Protobuf definitions create the contract between Substrate and agents — important when Substrate becomes the broker for multiple competing agent vendors. The streaming capability handles event subscriptions natively. The REST fallback lowers the bar for integrating simple agents.

---

## 5. Plugin Architecture

### Battle-Tested Approaches

**HashiCorp go-plugin: subprocess + gRPC protocol**
- **What:** Plugins are separate executables launched as subprocesses. The host and plugin communicate via gRPC over a local socket. The protocol is negotiated on startup. Plugins crash without crashing the host.
- **Evidence:** Used by Terraform, Vault, Nomad, Waypoint for 4+ years in production. Terraform Plugin Protocol v6 is the current version, using Protocol Buffers + gRPC as the canonical transport. This system supports plugins written in any language with gRPC bindings.
- **Source:** https://github.com/hashicorp/go-plugin (accessed 2026-03-10); https://developer.hashicorp.com/terraform/plugin/terraform-plugin-protocol (accessed 2026-03-10)
- **Fits our case because:** Data source plugins for Substrate (e.g., "read calendar to infer intent," "read IDE state to understand what's being worked on") are exactly the kind of optional, potentially third-party, potentially crash-prone extensions that benefit from process isolation. A plugin crash should not bring down the core daemon.
- **Tradeoffs:** Each plugin is a separate process, which has startup time and memory overhead. Subprocess communication adds latency versus in-process plugins. Go-specific convention for the host (though plugins can be any language).

**Grafana Backend Plugins: standalone Go binary + gRPC**
- **What:** Grafana plugins are standalone Go binaries that Grafana launches and communicates with via gRPC. They add new data sources, visualization panels, or entire sub-applications.
- **Evidence:** Grafana's plugin ecosystem has hundreds of production plugins. The frontend (TypeScript/React) and backend (Go) plugin systems run in parallel with well-defined interfaces.
- **Source:** https://deepwiki.com/grafana/grafana/11-plugin-system (accessed 2026-03-10)
- **Fits our case because:** Same pattern as go-plugin, with more design surface area (Grafana handles frontend plugins too). Useful reference for how to structure the plugin interface contract.
- **Tradeoffs:** Grafana's plugin system is Grafana-specific; go-plugin is the more portable abstraction.

**VS Code Extension Model: Extension Host process + JSON-RPC**
- **What:** VS Code runs all extensions in a separate Extension Host process (Node.js). Extensions communicate with VS Code via a stable API surface (JSON-RPC over IPC). Extensions cannot crash the editor itself.
- **Evidence:** This model has supported thousands of extensions in production since VS Code's launch. Language servers are further isolated as subprocesses of extensions.
- **Source:** https://code.visualstudio.com/api/language-extensions/language-server-extension-guide (accessed 2026-03-10)
- **Fits our case because:** The isolation model (editor survives extension crashes) is exactly what Substrate needs. The "stable API surface" concept maps to Substrate's plugin interface.
- **Tradeoffs:** VS Code's model is TypeScript/Node.js specific. The general architectural pattern applies, but the implementation would need to be language-agnostic for Substrate.

### Synthesis: Plugin Decision

**Recommendation: go-plugin (or its pattern: subprocess + gRPC) for data source plugins.**

The Terraform/HashiCorp ecosystem has proven this is the right answer for "extensible system tool that supports third-party plugins in any language." The subprocess isolation model is essential for a security-sensitive daemon. Define a protobuf interface for "data source plugins" — plugins that provide streams of context (calendar events, browser state, IDE focus) — and go-plugin handles the lifecycle and communication.

---

## 6. Cross-Device Sync

### Battle-Tested Approaches

**End-to-end encrypted sync with server relay (1Password model)**
- **What:** All data is encrypted client-side before transmission. The server stores only ciphertext. A Secret Key (separate from the master password) is combined with the password for decryption, ensuring the server can never decrypt data even with a compromised password database.
- **Evidence:** 1Password's security model uses AES-GCM-256 with PBKDF2-HMAC-SHA256 key derivation. All encryption/decryption is local. The server is a relay and storage layer, not a trust boundary. 1Password passed all external security audits for 2025 (AppSec, Cure53, Trail of Bits).
- **Source:** https://support.1password.com/1password-security/ (accessed 2026-03-10); https://support.1password.com/authentication-encryption/ (accessed 2026-03-10)
- **Fits our case because:** Substrate handles sensitive data (what processes are running, what the user is doing, behavioral patterns). The 1Password model — where the vendor literally cannot read user data — is the right privacy posture for a product claiming "consent foundational." This also makes regulatory compliance simpler.
- **Tradeoffs:** If a user loses their password AND their secret key, their cross-device sync data is unrecoverable. Server-side search/indexing is impossible on encrypted data.

**CRDT-based local-first sync (Automerge model)**
- **What:** CRDTs (Conflict-Free Replicated Data Types) allow concurrent edits on multiple devices to merge automatically without a central arbiter. Automerge 3 (Rust core, multi-language bindings) achieves ~10x lower memory usage than v1. Automerge-repo handles the sync protocol between peers.
- **Evidence:** Yjs and Automerge are both production-ready as of 2025. Obsidian's community-built LocalSync uses Yjs (CRDT) for multi-device vault sync. Linear, Figma, and Notion use CRDT-adjacent approaches for collaborative editing.
- **Source:** https://automerge.org/ (accessed 2026-03-10); https://github.com/elcomtik/obsidian-local-sync (accessed 2026-03-10); https://velt.dev/blog/best-crdt-libraries-real-time-data-sync (accessed 2026-03-10)
- **Fits our case because:** Substrate's state (process graph, workflow history, intent model) is updated on multiple devices simultaneously. CRDTs eliminate merge conflicts without a conflict resolution server. Automerge's Rust core means it can be used from a Rust or Go daemon.
- **Tradeoffs:** CRDTs add metadata overhead to every object (tombstones for deletions accumulate). Automerge's JSON data model may not map cleanly to a typed process graph. One production team (Cinapse, via PowerSync) documented moving away from CRDTs because the overhead and complexity exceeded the benefit for their use case — worth reading before committing.

### Synthesis: Sync Decision

**Recommendation: E2E encrypted server relay (1Password model) for transport, with CRDT semantics for the data structures that need conflict resolution.**

These are not mutually exclusive. The 1Password model is about the encryption/trust model. CRDTs are about conflict resolution. Substrate should: encrypt all data client-side before sync, use a relay server (or peer-to-peer relay) that cannot read the data, and use CRDT structures for the subset of state that can be edited on multiple devices simultaneously (e.g., user-defined labels, intent markers). The process graph itself is device-local (each device knows its own processes) and can be synced as append-only event logs, which are simpler than full CRDT documents.

---

## 7. Mobile Considerations

### iOS — Hard Architectural Constraint

**What actually runs in the background on iOS:**
- `BGAppRefreshTask`: System-scheduled, ~30 seconds max, at the OS's discretion. Used for content refresh when the app is not active.
- `BGProcessingTask`: Longer background task, minutes, requires charging + network connectivity typically. Used for ML model updates, database maintenance.
- `BGContinuedProcessingTask` (new in iOS 26): Continues a task started by an explicit user action (button tap). Cannot run autonomously. Has visible system progress UI. The OS can kill it.
- None of these support persistent background monitoring.

**What Substrate can actually do on iOS:**
1. **Receive sync data** from other devices when the app is in foreground or during a BGProcessingTask window.
2. **Answer queries** from AI agents running on iOS — the agent sends a query, the app wakes if needed, Substrate replies with cached context.
3. **Surface context built on other platforms** — if the user's Mac built the workflow graph, iOS Substrate can display and query it.
4. **No process monitoring** — iOS sandboxing makes this architecturally impossible without Apple cooperation.

- **Source:** https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtask (accessed 2026-03-10); https://dev.to/arshtechpro/wwdc-2025-ios-26-background-apis-explained-bgcontinuedprocessingtask-changes-everything-9b5 (accessed 2026-03-10)

### Android — Meaningfully Better, Still Constrained

**What's accessible:**
- `ActivityManager.getRunningAppProcesses()`: Own processes + visibility-gated info about others. Returns importance level (foreground/background/cached). Not a full process list.
- `UsageStatsManager`: App usage history by time window. Requires user-granted `PACKAGE_USAGE_STATS` permission. This IS the realistic path for "what has the user been doing."
- `Foreground Service`: A persistent service that shows a notification. Can run indefinitely. This is the mechanism for a background monitoring daemon on Android.
- `WorkManager`: For deferred and periodic tasks. Background apps face CPU restrictions under Android 15's `dataSync`/`mediaProcessing` foreground service timeouts (6 hours per 24-hour window).

**What Substrate can actually do on Android:**
1. A **Foreground Service** with a persistent notification can monitor app usage in near-real-time via `UsageStatsManager`.
2. Build a local usage graph (which apps, when, for how long) as a proxy for the workflow graph.
3. Participate fully in cross-device sync.
4. Cannot enumerate all system processes — only app-level visibility via UsageStats.

- **Source:** https://developer.android.com/develop/background-work/services/fgs/changes (accessed 2026-03-10); https://developer.android.com/develop/background-work/background-tasks/bg-work-restrictions (accessed 2026-03-10)

### Synthesis: Mobile Decision

**The MVP skips iOS process monitoring entirely.** iOS Substrate is a sync endpoint and query responder, not a monitor. Android Substrate is viable as a lightweight monitor using Foreground Service + UsageStatsManager, with the understanding that "process awareness" on Android means "app usage awareness" — less granular but genuinely useful.

---

## Gaps and Unknowns

1. **eBPF on Linux**: For high-fidelity process monitoring on Linux (especially in the container-heavy environment where Substrate might run), eBPF is the emerging best practice. It was not fully evaluated here. It requires kernel 4.18+ and root, but provides process event streams without the load-sensitivity issues of Netlink. Worth a separate research pass.

2. **macOS System Extension vs. libproc tradeoffs**: Endpoint Security Framework on macOS provides richer events (file access, network connections, process launches) than libproc alone, but requires notarization, a System Extension, and user approval. The friction vs. capability tradeoff needs product-level input to resolve.

3. **Windows ETW privilege model**: ETW consumers require administrative privileges or specific user rights. How Substrate requests and maintains these privileges across user contexts (standard user vs. admin) needs design work.

4. **Cross-platform service installer**: The daemon must be registered with Windows SCM, macOS launchd, and Linux systemd. The Go `service` package and Rust `service-manager` crate both handle this, but the exact UX of "install Substrate as a system service" needs user experience design, especially around privilege escalation prompts.

5. **KuzuDB fork trajectory**: The three forks (Ladybug, Bighorn, RyuGraph) are months old. If one stabilizes with cross-platform support (especially Windows), it becomes a viable alternative to SQLite for the graph layer. This is worth monitoring quarterly.

6. **Obsidian Sync's actual implementation**: The exact technical architecture of Obsidian Sync (encrypted, server-relayed, end-to-end) was not fully documented in available sources. It is cited as a model but deserves direct technical analysis before adoption as a pattern.

---

## Synthesis

### The Architecture That Fits

Based on this research, the architecture that satisfies all constraints — OS-agnostic, privacy-foundational, no vendor cooperation, incrementally buildable — is:

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Language** | Go (POC/V1), Rust option (V2) | Go dominates this exact use case (Tailscale, Docker, HashiCorp). Faster POC. |
| **Windows process events** | ETW + Win32 Process API | Only production-proven mechanism. Used by every EDR product. |
| **macOS process events** | libproc + BSD sysctl | Stable, no root required for basics, no Apple cooperation needed. |
| **Linux process events** | procfs + Netlink Connector | Standard kernel interfaces. osquery uses this pattern at scale. |
| **Android** | Foreground Service + UsageStatsManager | Best available without root. "App awareness" not "process awareness." |
| **iOS** | Sync endpoint + query responder only | Platform makes monitoring architecturally impossible without Apple cooperation. |
| **Graph storage** | SQLite (WAL mode, in-memory hot layer) | Sufficient for process graphs, universal, zero dependencies. |
| **IPC/API** | gRPC over Unix socket / Named Pipe | Docker's exact architecture. Typed, versioned, streamable, language-agnostic. |
| **Plugin system** | Subprocess + gRPC (go-plugin pattern) | Process isolation protects daemon. Third-party plugins in any language. |
| **Cross-device sync** | E2E encrypted relay + append-only event log | 1Password trust model, simpler than full CRDT for initial scope. |

### The Inner Ring First

The vision's "inner ring first" principle maps cleanly to architecture:

1. **POC**: Go daemon, Linux procfs polling, SQLite, REST API on localhost. Single machine, no sync.
2. **V1**: Add Windows ETW + macOS libproc, replace REST with gRPC, add service installer (SCM/launchd/systemd).
3. **V2**: Add cross-device sync (E2E encrypted relay), Android foreground service, plugin interface.
4. **V3**: iOS sync endpoint, eBPF on Linux, richer process enrichment, intent model.

### The Decisive Risk

The highest architectural risk is the iOS gap. Substrate's value proposition is "cross-device awareness," but iOS — the platform a significant portion of users run on their phone — cannot run a monitoring daemon. The product must be designed from the start to be useful without iOS monitoring, not to promise it and fail to deliver.

---

*Sources referenced in this document:*
- https://github.com/tailscale/tailscale
- https://blog.jetbrains.com/rust/2025/06/12/rust-vs-go/
- https://byteiota.com/rust-vs-go-2026-backend-performance-benchmarks/
- https://learn.microsoft.com/en-us/windows/win32/etw/event-tracing-portal
- https://benjitrapp.github.io/defenses/2024-02-11-etw/
- https://github.com/andrewdavidmackenzie/libproc-rs
- https://developer.apple.com/forums/thread/655349
- https://github.com/konstantin89/linux-netlink-process-monitoring
- https://slack.engineering/syscall-auditing-at-scale/
- https://docs.kernel.org/filesystems/proc.html
- https://developer.android.com/reference/android/app/ActivityManager
- https://developer.android.com/develop/background-work/services/fgs/changes
- https://developer.android.com/develop/background-work/background-tasks/bg-work-restrictions
- https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtask
- https://dev.to/arshtechpro/wwdc-2025-ios-26-background-apis-explained-bgcontinuedprocessingtask-changes-everything-9b5
- https://duckdb.org/community_extensions/extensions/duckpgq
- https://thedataquarry.com/blog/embedded-db-1/
- https://www.theregister.com/2025/10/14/kuzudb_abandoned/
- https://www.falkordb.com/blog/falkordblite-embedded-python-graph-database/
- https://learn.microsoft.com/en-us/aspnet/core/grpc/interprocess-uds
- https://learn.microsoft.com/en-us/aspnet/core/grpc/interprocess-namedpipes
- https://www.mpi-hd.mpg.de/personalhomes/fwerner/research/2021/09/grpc-for-ipc/
- https://github.com/hashicorp/go-plugin
- https://developer.hashicorp.com/terraform/plugin/terraform-plugin-protocol
- https://deepwiki.com/grafana/grafana/11-plugin-system
- https://code.visualstudio.com/api/language-extensions/language-server-extension-guide
- https://support.1password.com/1password-security/
- https://automerge.org/
- https://github.com/elcomtik/obsidian-local-sync
- https://velt.dev/blog/best-crdt-libraries-real-time-data-sync
- https://crates.io/crates/uni_service_manager
