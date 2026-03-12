# Team 4 Findings: Resilience, Health Monitoring & The Submantle Metaphor
## Date: 2026-03-10
## Researcher: Team Member 4

---

### Battle-Tested Approaches

#### 1. The Three-Phase Healing Loop (Isolate → Assess → Restore)

Mae's AutoHealer implements a biological wound-response cycle directly derived from salamander limb regeneration and immune wound healing. The three phases are not just names — each phase has a distinct job:

- **Isolate**: Sever the wound from the rest of the network to prevent cascade failure. Mae does this by calling `substrate.isolate_region()`, which removes edges between the failing node set and the rest of the topology while preserving the internal edges. The removed edges are returned as a dict so they can be precisely restored later. The biological analog is blood clotting — not killing the tissue, just sealing it off.
- **Assess**: Root-cause analysis, not symptom chasing. Without this phase, a healer fixes symptoms and re-triggers the same failure. Mae plugs in a CausalEngine here; when none is available, it falls back gracefully to treating the failure type as the root cause.
- **Restore**: Reconnect, redistribute load, inject resources. Only after root cause is known.

**Evidence of production-testing**: The 50-round endurance run (25,000 steps, 18 agents) brought starvation events from 5,088/round to 182 total after fixes. The pipeline has been stress-tested under real load.

**What this means for Submantle**: Submantle does not yet have a health repair loop. It has health state (AWARE/PRIVATE) but no self-repair. If a scan cycle hangs, if SQLite locks, if the API stops responding — nothing catches it. The three-phase pattern translates directly: (1) detect the hang, (2) identify cause (locked DB? crashed thread?), (3) restart the component. The pattern does not require complexity; even a lightweight watchdog loop applying these three phases in order is more than Submantle currently has.

---

#### 2. The Self-Healing Loop Prevention Pattern (Healer Skips Self)

One of the most precise lessons from the endurance hardening was the auto-healer self-healing loop. When Mae's own healer health dropped to 0.4 during an active healing operation, the next scan found it below the 0.5 threshold and tried to heal it — which consumed more health, creating a feedback spiral.

**The exact fix** (from mae-core `auto_healer.py`, line 236):
```python
if system_id == "auto_healer":
    continue
```

This one line is architecturally significant. Any monitoring system that monitors itself must explicitly exclude itself from the remediation loop. The healer observes its own health through a separate self-monitor triad (`_self_monitor()`) that runs on a different cadence from the main scan, with different indicators (scan staleness, queue overflow, detection blindness) and different recovery actions (reset scan counter, prune history, widen detection threshold). The self-monitor is a peer, not a subordinate.

**What this means for Submantle**: If Submantle adds a health monitor, it must not attempt to restart itself from within itself. The monitor and the monitored must be different execution contexts. This is a concrete safety pattern, not theory.

---

#### 3. Per-System Cooldown Windows

Mae's endurance run revealed that without cooldowns, the auto-healer re-healed the same system on every scan interval after a failed repair — flooding the system with healing events even when the cause was not addressable. The fix was a `_healing_cooldowns` dict keyed by system_id, with a 50-step window before the same system can be healed again.

This is identical in structure to the circuit breaker pattern from distributed systems — a component that has failed recently gets a grace window before the circuit re-opens. The difference is that Mae's is per-system rather than per-endpoint, which is the right granularity for a daemon monitoring a set of named subsystems.

**Evidence**: From the endurance run results — triad violations went from 6 per audit to 0, dysbiosis to 0, membrane rejections to 0. Cooldowns were one of three fixes in that commit round.

---

#### 4. Replenishment Rate Must Exceed Decay Rate (or Be Designed Intentionally Below It)

This is the most concretely measurable lesson from Mae's endurance hardening.

**The failure mode** (from mae-core HANDOFF.md, Commit 3): `NutrientFlowEngine` had `decay_rate=0.01/step` and zero replenishment. After ~350 steps, all nodes drained below `starvation_threshold=0.15`. The auto-healer was flooded with starvation events every step. The fix added `replenishment_rate=0.008` — slightly below decay (0.01), creating intentional mild scarcity (residual ~3.6 starvation events/round by design).

**The formula**: If `replenishment_rate < decay_rate`, the system trends toward depletion. The question is: how long until it starves, and is that acceptable? Mae made it explicit by choosing 0.008 < 0.01 intentionally, accepting ~3.6 starvation events/round as background noise rather than crisis.

**What this means for Submantle**: Submantle scans every 5 seconds. Every scan costs CPU and memory. The "resource budget" is implicit — Submantle does not track its own resource consumption or set a policy about what proportion of a device's CPU it is allowed to consume. Mae's lesson: make the decay/replenishment balance explicit and intentional. For Submantle: the "decay" is the CPU/memory cost per scan, the "replenishment" is the idle capacity the device has. When the device is under load, the balance should shift — scans should back off. When the device is idle, they can be more aggressive. This is currently not implemented.

---

#### 5. Watchdog Heartbeat Pattern (Industry-Standard, Mae-Validated)

External research confirms the watchdog heartbeat pattern as the production standard for daemon health monitoring. Systemd's implementation (`WatchdogSec`, `sd_notify("WATCHDOG=1")`) sets an interval; if the daemon does not send a heartbeat within that window, systemd kills and restarts it. This catches "zombie" scenarios: the process is alive but stuck — not processing requests, stuck in a lock, or in an infinite loop.

**Mae's equivalent**: AutoHealer's `_self_monitor()` runs every 5 steps (separate cadence from the 10-step main scan), checking three indicators:
1. Scan staleness (steps since last scan ran)
2. Queue overflow (history growing unboundedly)
3. Detection blindness (system active but no failures detected)

Each indicator has a concrete recovery action. This is a software-level watchdog, analogous to systemd's hardware watchdog but internal.

**Source**: [How to Configure systemd Watchdog for Service Health Checks on Ubuntu](https://oneuptime.com/blog/post/2026-03-02-how-to-configure-systemd-watchdog-for-service-health-checks-on-ubuntu/view), [watchdogd: Advanced system monitor for Linux](https://github.com/troglobit/watchdogd)

---

#### 6. EventBus Channel Registration as a Required Initialization Step

Mae's 30,000+ warning flood (eliminated in Commit 1 of endurance hardening) came from 6 missing EventBus channel registrations. Channels for `defense.membrane_status`, `defense.quarantine_event`, and others existed in code but were not registered with the bus — so every attempted publish generated a warning log.

**The pattern**: Every component that publishes to the bus must register its channels at initialization time. This is not optional — it's part of startup correctness. Mae learned this the hard way at 50 rounds × 500 steps.

**What this means for Submantle**: Submantle's EventBus (events.py) currently has 7 event types hardcoded in the `EventType` enum. There is no registration step — events just go into the enum. This works fine at current scale. But as Submantle grows (MCP events, agent health events, device-level events), missing registrations will cause exactly the same warning floods Mae experienced. Consider building a `register_channels()` call pattern before those problems occur.

---

### Novel Approaches

#### 7. The Physarum Optimizer: Edges That Earn Their Keep

Mae's substrate package includes a `PhysarumOptimizer` based on the Physarum polycephalum slime mold's network optimization behavior (Tero et al., Science 2010). The core equation is:

`dD/dt = f(|Q|) - gamma * D`

Where D is edge conductance, Q is flow through the edge, and gamma is natural decay. Edges that carry more flow grow stronger; edges that carry little flow decay below a prune threshold and are removed. The network self-optimizes its topology toward the paths that actually get used.

This is Hebbian learning applied to network structure: "use it or lose it" at the edge level, not just the synapse level.

**Novel translation for Submantle**: Submantle builds a process tree (`build_process_tree()`) representing parent-child process relationships. It also has a `query_what_would_break()` function that follows child relationships. But the relationship graph is static — it does not track which relationships are active (parent-child communication happening) versus dormant (child exists but is forked and idle).

A lightweight Physarum-inspired pattern could track: which process relationships generate events (process started/died events that reference parent PIDs). Frequently-used relationships strengthen; dormant ones decay. Over time, Submantle would develop a weighted relationship model that distinguishes "this process always has children that matter" from "this parent sometimes has children but they're usually noise." This would make `query_what_would_break()` more accurate without requiring LLM inference — it's structural signal from observed behavior.

**Tradeoffs**: Adds state (relationship weights) and computation (weight update per scan). Must be configurable to disable. Not appropriate for the prototype — this is a V2+ concept.

---

#### 8. The Autopoietic Closure Principle for a Computing Awareness Layer

Mae's Law 6 (Autopoietic Closure) states: the system must include itself as an object of its own awareness. The AutoHealer must know its own health. The SomaticMap must include itself as a tracked system.

Submantle is an awareness layer for computing. By this same principle: Submantle must be part of the computing awareness it provides. When an agent queries Submantle about what processes are running and what's important, Submantle itself should appear in that list — with its own health status, resource consumption, uptime, and last scan time.

Currently, Submantle does not include itself in the process scan results. `scan_processes()` returns all processes including the Python process running Submantle, but it has no identity signature for itself, so it returns as an unidentified process.

**The fix**: Add a Submantle identity signature to `signatures.json` for the Submantle daemon process. Give it importance: "critical". Add a health status endpoint that reports not just "is Submantle running" but "when did it last successfully scan, what is its SQLite lag, what is the event bus queue depth." This closes the autopoietic loop — Submantle knows what it is and where it stands.

---

#### 9. Two-Layer Privacy Defense Must Be Kept In Sync

Mae's endurance hardening revealed that privacy state management requires two layers to be synchronized, not one. Mae had `PrivacyManager` (the gate) and `EventBus` (the filter), and they had to be told separately.

Submantle has implemented this correctly — `PrivacyManager._emit_toggle_event()` calls `self._event_bus.set_privacy_mode(new_state == PrivacyState.PRIVATE)` before emitting the `PRIVACY_TOGGLED` event. This is the right order: sync the filter before broadcasting the state change, so no process event leaks through between the state write and the filter update.

**This is already a solved pattern in Submantle** — noting it here as a validation that Submantle got this right independently.

---

### Emerging Approaches

#### 10. Circadian-Aware Resource Scheduling for a Computing Daemon

Mae's `CircadianRhythm` uses three phases (ACTIVE / CONSOLIDATION / REST) driven by simulation steps. Importantly, it notes in its docstring: "Unlike real organisms, Mae's cycle is not tied to wall-clock time."

For Submantle, wall-clock time IS the right signal. Submantle runs on a real device with a real user. The user's sleep/wake pattern creates genuine circadian variation in device usage. Windows already implements this: the user is considered absent after 4 minutes of no keyboard/mouse input; Microsoft Defender shifts from 10-minute verification intervals (user present) to 30-second intervals (user away).

**The principle**: Submantle's scan frequency and depth should be modulated by user presence state. Three natural phases:

| Phase | Trigger | Submantle Behavior |
|-------|---------|-------------------|
| ACTIVE | User present (input in last 4 min) | Minimal scan (5s interval, identity only, no heavy queries) |
| CONSOLIDATION | User idle (10–60 min) | Moderate scan (30s interval, full awareness, signature updates) |
| REST | User away (60+ min) | Background maintenance (5m interval, signature cache refresh, DB prune, event log archive) |

Windows provides idle detection via `GetLastInputInfo()` (Win32) and the Task Scheduler idle condition API. These are production-stable APIs.

**Evidence**: Windows Task Scheduler's idle detection has been production-stable since Windows Vista. The `WICG/idle-detection` proposal is the web standard equivalent. Both are well-documented and widely deployed.

**Source**: [Task idle conditions - Win32 apps | Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/taskschd/task-idle-conditions), [Detecting an Idle Device - Windows drivers](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/detecting-an-idle-device), [WICG/idle-detection proposal](https://github.com/WICG/idle-detection)

**Tradeoffs**: Adds wall-clock dependency. Phase transitions must be gradual (don't snap from 5s to 5m — ramp). Privacy mode is orthogonal — circadian phases modulate scan rate, privacy mode stops scanning entirely. Both must be active simultaneously.

---

#### 11. Topology Health as a System Health Metric

Mae's `get_health_report()` in `MycelialSubmantle` returns a rich topology health snapshot:
- `connectivity_ratio`: fraction of nodes reachable from any starting node (1.0 = fully connected; < 1.0 = fragmented)
- `clustering_coefficient`: how much nodes cluster (high = strong local neighborhoods)
- `avg_degree`: average connections per node
- `isolated_nodes`: count of nodes with zero connections
- `empty_nodes`: count of positions without agents

For Mae, a drop in `connectivity_ratio` means agents are being cut off from communication. For Submantle, an analogous "topology health" concept applies to the process relationship graph. Current metrics in Submantle are flat counts (total_processes, identified_count). There is no measurement of graph health — whether the process relationship tree is as connected as it should be, whether critical hubs (PID 1 equivalent, init processes) retain their expected children.

**Translation**: A "process graph health" metric: does the observed process tree match expected topology? Missing expected children of a critical parent process could indicate that important processes have died without being noticed.

**Status**: This is an emerging idea — no production validation yet. The concept requires defining "expected topology" per device, which requires learning from historical scans. V2+ concept.

---

#### 12. Demand-Proportional Resource Distribution (Murray's Law)

Mae's `CirculatorySystem` distributes compute, memory, and attention resources proportional to demand, with urgency as a priority multiplier. The distribution follows Murray's Law (1926): the cube of a parent vessel's radius equals the sum of cubes of its children's radii — minimizing total energy for transport.

The heart rate increases under high total demand (sympathetic response) and decreases when demand is low (parasympathetic). Supply regenerates each step at 15% of max — autopoietic closure applied to resource management.

**Translation for Submantle**: When multiple agents query Submantle simultaneously, there is no prioritization — queries are handled in arrival order. A demand-proportional approach would prioritize queries from agents with higher trust scores and more critical declared capabilities. This is a natural extension of the existing agent trust schema. An agent with `importance: critical` querying about a critical process gets faster service than an unknown agent querying for diagnostics.

**Status**: Emerging, not yet needed. Relevant when Submantle has 10+ registered agents making concurrent queries.

---

### Gaps and Unknowns

**Gap 1: Submantle has no self-health reporting**
The most significant gap is that Submantle does not report its own health to any internal system. There is no equivalent of Mae's SomaticMap heartbeat for Submantle's own components (scanner thread, SQLite writer, API, event bus). A Submantle instance could be functioning partially (API up, scanner dead) with no way to detect this.

**Gap 2: The decay/replenishment balance for Submantle's own resources is implicit**
Submantle's scan loop in `api.py` runs at a fixed interval regardless of device load. There is no mechanism to back off when the device is under CPU pressure, disk pressure, or memory pressure. Mae's endurance run taught that zero replenishment leads to starvation. The analog here is: running at full scan rate during peak device load causes the device to resent Submantle rather than trust it. "Lightweight first" (Submantle's own principle #1) requires measuring and adapting, not just hoping the fixed interval is small enough.

**Gap 3: Region isolation has no Submantle equivalent**
Mae can call `isolate_region()` to surgically remove a failing component from the network while keeping the rest healthy. Submantle has no equivalent. If the SQLite writer deadlocks, the entire system halts. Isolation would mean: the scanner continues writing to an in-memory buffer, the API continues serving the last known state, and the DB writer is restarted independently. The components are not currently isolated enough for this.

**Gap 4: The EventBus has no backpressure mechanism**
Mae's EventBus and Submantle's EventBus share this gap. If a subscriber is slow, it blocks the dispatcher. If events flood in faster than they can be processed, there is no shedding mechanism. Mae learned about this indirectly through the starvation event flood (before the replenishment fix). Submantle could face the same issue if process churn is high (many processes starting/dying per scan).

**Gap 5: Unknown — how much does Windows idle detection cost?**
The circadian-aware scheduling proposal relies on calling `GetLastInputInfo()` or similar to detect user presence. The cost of this call is unknown from research — it may be negligible, or it may require elevated permissions on some Windows configurations. This needs a 30-minute validation before being built.

**Gap 6: Key mismatch pattern**
Mae's HANDOFF.md documents that `_on_starvation()` read `message.get("node_id")` but the substrate published `{"nodes": [...]}` — a key mismatch that caused the starvation handler to silently do nothing for weeks. This is a category of bug that unit tests often miss because they test the handler or the publisher in isolation, not the message contract between them. Submantle's current event payload contracts are informal (plain dicts). This gap will grow as event types multiply.

---

### Synthesis

#### The Shared Metaphor Is Architecturally Generative

Both Mae's `MycelialSubmantle` and Submantle (the product) are defined by the same metaphor: the soil that everything grows in. The metaphor is not decoration — it drove concrete architectural decisions in Mae that translate directly:

1. **The soil is aware of its own health.** `get_health_report()` is a first-class method on `MycelialSubmantle`. Submantle should have an equivalent — not just "is the daemon running" but a rich health snapshot including scanner timing, DB lag, event bus depth, and self-identification.

2. **The soil manages its own resource flow.** `NutrientFlowEngine` tracks decay and replenishment explicitly. Submantle's resource management is implicit (hope the fixed scan interval is light enough). Making it explicit — measuring CPU per scan, adapting interval to device load — is the same transition Mae made from zero replenishment to intentional mild scarcity.

3. **The soil heals itself.** Mae's AutoHealer is wired directly to substrate events. Submantle has no healing loop. The three-phase pattern (isolate, assess, restore) is simple enough to implement at prototype scale without introducing architectural complexity.

4. **The soil responds to circadian phases.** Mae's substrate flow rates modulate based on phase (REST = half decay, half flow). Submantle's computing environment has real circadian variation driven by user presence. Adapting scan frequency to idle state is the same principle applied to wall-clock time rather than simulation steps.

#### What Endurance Testing Taught

Mae's 50-round, 25,000-step endurance run surfaced six categories of failure that were invisible in unit tests:

1. **Trust floor decay**: External providers decayed below rejection threshold after ~90 steps. Fix: add a floor.
2. **Missing EventBus channels**: 30,000+ warning floods. Fix: register all channels at startup.
3. **Self-healing loop**: Healer triggered its own threshold. Fix: explicitly skip self.
4. **Key mismatch in message contracts**: Starvation handler silently failed. Fix: test the contract, not just the handler.
5. **Zero replenishment**: All nodes starved after ~350 steps. Fix: explicit replenishment rate.
6. **Cooldown absence**: Re-healed same system every scan. Fix: per-system cooldown windows.

For a daemon that runs 24/7, these are exactly the failure modes that matter. Submantle's 160 tests cover unit behavior; they do not cover what happens at 72 hours of continuous operation, what happens when the device wakes from sleep mid-scan, or what happens when process churn spikes during an update storm. Mae's endurance approach — run for thousands of steps, watch the metrics, find what drifts — is directly applicable to Submantle.

#### Priority Stack for Submantle

Ranked by leverage vs. implementation cost, given Submantle's current state and design principles:

1. **Add Submantle's own identity signature** (1 hour): Closes the autopoietic loop. Submantle appears in its own awareness report as a critical process. High leverage, trivial cost.

2. **Explicit resource budget with idle-adaptive scan rate** (1–2 days): Replace fixed 5-second scan with idle-aware scheduling. ACTIVE phase: back off. REST phase: more aggressive maintenance. This directly serves "lightweight first" and turns the device from a passive target to an active collaborator.

3. **Watchdog heartbeat for the scanner thread** (half day): The scanner runs in a background thread. If it hangs, nothing currently detects it. A simple heartbeat timestamp + watchdog check on the next API call is the minimum viable health monitor.

4. **Three-phase healing for component failures** (2–3 days): Start small — handle SQLite lock and scanner thread hang. The pattern is: detect (no heartbeat), assess (is the DB locked? is the thread alive?), restore (restart the thread, flush and reconnect DB). This does not require Mae's complexity — three `if` blocks in a startup loop would achieve 80% of the value.

5. **Formalize event payload contracts** (ongoing): The key mismatch pattern (node_id vs nodes) is a maintenance tax that compounds with system growth. Even informal documentation of expected payload shape per EventType — in the docstring of each `emit()` call — would catch these before they hit a 50-round endurance run equivalent.

Items 4 and 5 from Mae's endurance list (cooldown windows and per-system circuit breakers) are not yet relevant for Submantle since there is nothing to cool down. They become relevant when the healing loop is built.

---

*Research sourced from: mae-core source files (mycelial_substrate.py, nutrient_flow.py, topology.py, auto_healer.py, circadian_rhythm.py, MAES_BIOLOGY.md, HANDOFF.md, substrate/CONNECTIONS.md), Submantle prototype files (substrate.py, events.py, privacy.py, database.py), external sources below.*

**External Sources Referenced:**
- [Self-Healing Systems - GeeksforGeeks](https://www.geeksforgeeks.org/system-design/self-healing-systems-system-design/)
- [Architecture strategies for self-healing and self-preservation - Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/reliability/self-preservation)
- [How to Configure systemd Watchdog for Service Health Checks on Ubuntu](https://oneuptime.com/blog/post/2026-03-02-how-to-configure-systemd-watchdog-for-service-health-checks-on-ubuntu/view)
- [watchdogd: Advanced system monitor for Linux](https://github.com/troglobit/watchdogd)
- [Task idle conditions - Win32 apps | Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/taskschd/task-idle-conditions)
- [Detecting an Idle Device - Windows drivers | Microsoft Learn](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/detecting-an-idle-device)
- [WICG/idle-detection proposal](https://github.com/WICG/idle-detection)
- [Fluid mechanics within mycorrhizal networks - New Phytologist 2025](https://nph.onlinelibrary.wiley.com/doi/10.1111/nph.70509)
- [Complete Guide to Resilience Patterns in Distributed Systems - Technori 2026](https://technori.com/2026/02/24230-the-complete-guide-to-resilience-patterns-in-distributed-systems/gabriel/)
- [How to Prevent Resource Starvation of Kubernetes Services - Appvia](https://www.appvia.io/blog/how-to-prevent-resource-starvation-of-kubernetes-services)
