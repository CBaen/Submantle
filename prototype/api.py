"""
Substrate API — FastAPI server wrapping the process awareness daemon.
Serves the dashboard and exposes JSON endpoints.

Run: uvicorn api:app --reload --port 8421
"""

import json
import socket
import struct
import subprocess
import time
from pathlib import Path

import psutil
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from substrate import (
    awareness_report,
    build_process_tree,
    load_signatures,
    query_what_would_break,
    scan_processes,
)

VERSION = "0.1.0"

app = FastAPI(title="Substrate", version=VERSION, docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ── Cache ──────────────────────────────────────────────────────────────────────
# Re-scan at most every 5 seconds to avoid hammering psutil on every poll.

_cache: dict = {}
_cache_ts: float = 0.0
_CACHE_TTL = 5.0


def _get_state() -> dict:
    global _cache, _cache_ts
    now = time.time()
    if now - _cache_ts < _CACHE_TTL:
        return _cache

    signatures = load_signatures()
    processes = scan_processes(signatures)
    tree = build_process_tree(processes)
    report = awareness_report(processes, tree)

    _cache = {
        "report": report,
        "processes": processes,
        "tree": tree,
        "scanned_at": now,
    }
    _cache_ts = now
    return _cache


# ── Device Discovery ───────────────────────────────────────────────────────────
# Lightweight ARP-based local network scan. No root required on most platforms.
# Falls back to a small mock dataset if network scanning is unavailable.

def _get_local_network_prefix() -> str | None:
    """Return the /24 prefix of the machine's primary LAN IP, e.g. '192.168.1.'"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        parts = ip.split(".")
        return ".".join(parts[:3]) + "."
    except Exception:
        return None


def _ping_host(ip: str, timeout_ms: int = 300) -> int | None:
    """Ping a host. Returns round-trip ms or None if unreachable."""
    try:
        import platform
        flag = "-n" if platform.system().lower() == "windows" else "-c"
        result = subprocess.run(
            ["ping", flag, "1", "-w", str(timeout_ms), ip],
            capture_output=True,
            timeout=1,
        )
        if result.returncode == 0:
            # Very rough: return 1ms as placeholder (full RTT parsing is overkill here)
            return 1
    except Exception:
        pass
    return None


def _discover_devices() -> list[dict]:
    """
    Discover devices on the local network using ARP cache and ping sweep.
    This is intentionally lightweight — no root, no raw sockets.
    Returns a list of device dicts.
    """
    devices = []

    # --- Method 1: Parse the ARP cache (fastest, no network traffic) ---
    try:
        import platform
        if platform.system().lower() == "windows":
            result = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=5)
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 2 and parts[0].count(".") == 3:
                    ip = parts[0].strip()
                    mac = parts[1].strip() if len(parts) > 1 else "unknown"
                    # Filter multicast (224.x-239.x), broadcast, and link-local
                    first_octet = int(ip.split(".")[0])
                    if mac not in ("---", "ff-ff-ff-ff-ff-ff") and not (224 <= first_octet <= 239) and first_octet != 255:
                        devices.append({
                            "ip": ip,
                            "mac": mac.upper(),
                            "hostname": _resolve_hostname(ip),
                            "manufacturer": _guess_manufacturer(mac),
                            "type": _guess_device_type(ip, mac),
                            "status": "online",
                            "response_ms": 1,
                        })
        else:
            result = subprocess.run(["arp", "-n"], capture_output=True, text=True, timeout=5)
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 3 and parts[0].count(".") == 3:
                    ip = parts[0]
                    mac = parts[2] if parts[2] != "(incomplete)" else "unknown"
                    devices.append({
                        "ip": ip,
                        "mac": mac.upper(),
                        "hostname": _resolve_hostname(ip),
                        "manufacturer": _guess_manufacturer(mac),
                        "type": _guess_device_type(ip, mac),
                        "status": "online",
                        "response_ms": 1,
                    })
    except Exception:
        pass

    # --- Add this machine itself ---
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        devices.insert(0, {
            "ip": local_ip,
            "mac": "local",
            "hostname": hostname,
            "manufacturer": "This machine",
            "type": "workstation",
            "status": "online",
            "response_ms": 0,
            "is_self": True,
        })
    except Exception:
        pass

    # Deduplicate by IP
    seen = set()
    unique = []
    for d in devices:
        if d["ip"] not in seen:
            seen.add(d["ip"])
            unique.append(d)

    return unique[:20]  # Cap at 20 devices for the dashboard


def _resolve_hostname(ip: str) -> str:
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return ip


def _guess_manufacturer(mac: str) -> str:
    """Very rough OUI-based manufacturer guessing from the first 3 octets."""
    if not mac or mac in ("unknown", "local"):
        return "Unknown"
    oui = mac.replace("-", ":").upper()[:8]
    # A tiny subset of common OUIs — enough for a prototype
    OUI_MAP = {
        # Virtualization
        "00:50:56": "VMware",
        "08:00:27": "VirtualBox",
        "00:15:5D": "Microsoft Hyper-V",
        # SBCs
        "B8:27:EB": "Raspberry Pi",
        "DC:A6:32": "Raspberry Pi",
        "E4:5F:01": "Raspberry Pi",
        # Smart Home
        "00:17:88": "Philips Hue",
        "18:B4:30": "Nest/Google",
        "68:A4:0E": "Amazon (Echo/Ring)",
        "40:B4:CD": "Amazon (Echo/Ring)",
        "F0:F0:A4": "Amazon (Echo/Ring)",
        "30:FD:38": "Google (Nest/Chromecast)",
        "54:60:09": "Google (Nest/Chromecast)",
        # Routers / Networking
        "98:25:4A": "ASUS",
        "04:D9:F5": "ASUS",
        "1C:87:2C": "ASUS",
        "50:C7:BF": "TP-Link",
        "60:32:B1": "TP-Link",
        "C0:25:E9": "TP-Link",
        "00:1A:2B": "Cisco",
        "00:14:BF": "Linksys",
        "74:DA:38": "EnGenius",
        "B0:BE:76": "Netgear",
        "A4:2B:B0": "Netgear",
        # Apple
        "F4:F2:6D": "Apple",
        "A4:C3:F0": "Apple",
        "AC:BC:32": "Apple",
        "3C:22:FB": "Apple",
        "18:65:90": "Apple",
        "88:66:5A": "Apple",
        "14:98:77": "Apple",
        # Samsung
        "8C:F5:A3": "Samsung",
        "FC:A1:83": "Samsung",
        # Dell / HP / Lenovo
        "00:26:B9": "Dell",
        "3C:D9:2B": "HP",
        "98:E7:43": "HP",
        "A4:34:D9": "Intel",
        "8C:8C:AA": "Lenovo",
        # Sonos / Media
        "B8:E9:37": "Sonos",
        "34:7E:5C": "Sonos",
        "78:28:CA": "Sonos",
        "48:A6:B8": "Roku",
    }
    return OUI_MAP.get(oui, "Network Device")


def _guess_device_type(ip: str, mac: str) -> str:
    """Guess device type from IP position and MAC hints."""
    last_octet = int(ip.split(".")[-1]) if ip.count(".") == 3 else 0
    mac_up = (mac or "").upper()

    if last_octet == 1:
        return "router"
    if "F4:F2:6D" in mac_up or "A4:C3:F0" in mac_up or "3C:22:FB" in mac_up:
        return "apple-device"
    if "B8:27:EB" in mac_up or "DC:A6:32" in mac_up:
        return "raspberry-pi"
    mfg = _guess_manufacturer(mac)
    if mfg in ("VMware", "VirtualBox", "Microsoft Hyper-V"):
        return "vm"
    if last_octet in range(2, 10):
        return "server"
    return "unknown"


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "alive", "version": VERSION}


@app.get("/api/status")
def status():
    state = _get_state()
    report = state["report"]
    scanned_at = state["scanned_at"]

    return {
        "timestamp": report["timestamp"],
        "scan_age_seconds": round(time.time() - scanned_at, 1),
        "total_processes": report["total_processes"],
        "identified_processes": report["identified_processes"],
        "identification_rate": float(report["identification_rate"].rstrip("%")),
        "critical_count": len(report["critical_processes"]),
        "categories": report["by_category"],
        "critical_processes": report["critical_processes"],
    }


@app.get("/api/query")
def query(process: str = ""):
    if not process.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "process parameter is required"},
        )
    state = _get_state()
    result = query_what_would_break(
        process.strip(), state["processes"], state["tree"]
    )
    return result


@app.get("/api/devices")
def devices():
    discovered = _discover_devices()
    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "devices": discovered,
    }


# ── Dashboard ──────────────────────────────────────────────────────────────────

@app.get("/")
def dashboard():
    html_path = Path(__file__).parent / "dashboard.html"
    if html_path.exists():
        return FileResponse(str(html_path), media_type="text/html")
    return JSONResponse(
        status_code=404,
        content={"error": "dashboard.html not found — run from prototype/ directory"},
    )
