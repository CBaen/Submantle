"""
Substrate Prototype — Process Awareness Daemon
The ground beneath everything.

Monitors running processes, identifies what they ARE (not just their names),
builds a relationship graph, and answers queries about system state.
"""

import json
import os
import time
from collections import defaultdict
from pathlib import Path

import psutil


SIGNATURES_PATH = Path(__file__).parent / "signatures.json"


def load_signatures():
    with open(SIGNATURES_PATH) as f:
        data = json.load(f)
    return data["signatures"]


def match_signature(proc_info, signatures):
    """Match a process against identity signatures. Returns best match or None."""
    exe = (proc_info.get("exe") or "").lower()
    cmdline = " ".join(proc_info.get("cmdline") or []).lower()
    cwd = (proc_info.get("cwd") or "").lower()

    best_match = None
    best_score = 0

    for sig in signatures:
        m = sig["match"]
        score = 0

        if "exe_contains" in m:
            if any(pat in exe for pat in m["exe_contains"]):
                score += 1
            else:
                continue  # exe match is mandatory

        if "cmdline_contains" in m and any(pat in cmdline for pat in m["cmdline_contains"]):
            score += 2  # cmdline is a stronger signal

        if "cwd_contains" in m and any(pat in cwd for pat in m["cwd_contains"]):
            score += 2

        if score > best_score:
            best_score = score
            best_match = sig

    return best_match


def scan_processes(signatures):
    """Scan all running processes and identify them."""
    processes = []

    for proc in psutil.process_iter(["pid", "ppid", "name", "exe", "cmdline",
                                      "cwd", "status", "create_time",
                                      "memory_info", "cpu_percent"]):
        try:
            info = proc.info
            identity = match_signature(info, signatures)

            entry = {
                "pid": info["pid"],
                "ppid": info["ppid"],
                "name": info["name"],
                "exe": info["exe"],
                "cmdline": info.get("cmdline"),
                "cwd": info.get("cwd"),
                "status": info["status"],
                "uptime_seconds": int(time.time() - (info["create_time"] or time.time())),
                "memory_mb": round((info.get("memory_info") or type("", (), {"rss": 0})).rss / 1024 / 1024, 1),
                "identity": {
                    "id": identity["id"],
                    "name": identity["name"],
                    "category": identity["category"],
                    "importance": identity["importance"],
                    "description": identity["description"],
                } if identity else None,
            }
            processes.append(entry)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return processes


def build_process_tree(processes):
    """Build parent-child relationship tree."""
    by_pid = {p["pid"]: p for p in processes}
    children = defaultdict(list)
    for p in processes:
        if p["ppid"] in by_pid:
            children[p["ppid"]].append(p["pid"])
    return children


def query_what_would_break(target_name, processes, tree):
    """Answer: 'What would break if I killed all processes named X?'"""
    targets = [p for p in processes if target_name.lower() in (p["name"] or "").lower()]

    if not targets:
        return {"safe": True, "message": f"No processes matching '{target_name}' found."}

    identified = [t for t in targets if t["identity"]]
    unidentified = [t for t in targets if not t["identity"]]

    critical = [t for t in identified if t["identity"]["importance"] in ("critical", "high")]
    safe = [t for t in identified if t["identity"]["importance"] == "low"]

    # Find child processes that would also die
    affected_children = []
    for t in targets:
        for child_pid in tree.get(t["pid"], []):
            child = next((p for p in processes if p["pid"] == child_pid), None)
            if child:
                affected_children.append(child)

    result = {
        "query": f"What would break if I killed all '{target_name}' processes?",
        "total_matching": len(targets),
        "critical_processes": [{
            "pid": t["pid"],
            "identity": t["identity"]["name"],
            "description": t["identity"]["description"],
            "uptime": f"{t['uptime_seconds'] // 3600}h {(t['uptime_seconds'] % 3600) // 60}m",
            "memory_mb": t["memory_mb"],
        } for t in critical],
        "safe_to_kill": [{
            "pid": t["pid"],
            "identity": t["identity"]["name"] if t["identity"] else t["name"],
        } for t in safe],
        "unidentified": [{
            "pid": t["pid"],
            "name": t["name"],
            "cmdline": " ".join(t["cmdline"] or [])[:100],
        } for t in unidentified],
        "collateral_damage": [{
            "pid": c["pid"],
            "name": c["name"],
            "identity": c["identity"]["name"] if c["identity"] else "Unknown",
        } for c in affected_children],
        "recommendation": "BLOCK" if critical else ("CAUTION" if unidentified else "SAFE"),
    }
    return result


def awareness_report(processes, tree):
    """Generate a full awareness report — what Substrate currently knows."""
    identified = [p for p in processes if p["identity"]]
    categories = defaultdict(list)
    for p in identified:
        categories[p["identity"]["category"]].append(p)

    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_processes": len(processes),
        "identified_processes": len(identified),
        "identification_rate": f"{len(identified) / max(len(processes), 1) * 100:.1f}%",
        "by_category": {
            cat: [{
                "pid": p["pid"],
                "name": p["identity"]["name"],
                "importance": p["identity"]["importance"],
                "uptime": f"{p['uptime_seconds'] // 3600}h {(p['uptime_seconds'] % 3600) // 60}m",
                "memory_mb": p["memory_mb"],
            } for p in procs]
            for cat, procs in sorted(categories.items())
        },
        "critical_processes": [{
            "pid": p["pid"],
            "name": p["identity"]["name"],
            "description": p["identity"]["description"],
        } for p in identified if p["identity"]["importance"] in ("critical", "high")],
    }
    return report


def main():
    print("=" * 60)
    print("  SUBSTRATE PROTOTYPE — Process Awareness Daemon")
    print("  The ground beneath everything.")
    print("=" * 60)
    print()

    signatures = load_signatures()
    print(f"Loaded {len(signatures)} identity signatures.")
    print("Scanning processes...\n")

    processes = scan_processes(signatures)
    tree = build_process_tree(processes)

    # Full awareness report
    report = awareness_report(processes, tree)
    print(f"Total processes: {report['total_processes']}")
    print(f"Identified: {report['identified_processes']} ({report['identification_rate']})")
    print()

    if report["by_category"]:
        print("--- IDENTIFIED SOFTWARE ---")
        for cat, procs in report["by_category"].items():
            print(f"\n  [{cat}]")
            for p in procs:
                print(f"    PID {p['pid']}: {p['name']} ({p['importance']}) — up {p['uptime']}, {p['memory_mb']}MB")

    if report["critical_processes"]:
        print("\n--- CRITICAL PROCESSES (do not kill) ---")
        for p in report["critical_processes"]:
            print(f"  PID {p['pid']}: {p['name']}")
            print(f"    {p['description']}")

    # Demo: What would break if you killed node?
    print("\n" + "=" * 60)
    print("  DEMO QUERY: 'What would break if I killed all node processes?'")
    print("=" * 60)
    result = query_what_would_break("node", processes, tree)
    print(json.dumps(result, indent=2))

    # Save full state
    state_path = Path(__file__).parent / "substrate_state.json"
    with open(state_path, "w") as f:
        json.dump({
            "awareness": report,
            "processes": [{k: v for k, v in p.items() if k != "cmdline"} for p in processes if p["identity"]],
        }, f, indent=2)
    print(f"\nState saved to {state_path}")


if __name__ == "__main__":
    main()
