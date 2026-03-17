"""
Submantle API — FastAPI server wrapping the process awareness daemon.
Serves the dashboard and exposes JSON endpoints.

Run: uvicorn api:app --reload --port 8421

Module initialization order (critical — do not reorder):
  1. SubmantleDB      — SQLite layer must exist before anything else
  2. EventBus(db=db)  — persists events; needs DB
  3. PrivacyManager   — loads persisted state from DB, syncs bus on toggle
  4. AgentRegistry    — loads HMAC secret from DB, emits events on bus
"""

import hashlib
import socket
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import psutil
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from submantle import (
    awareness_report,
    build_process_tree,
    load_signatures,
    query_what_would_break,
    scan_processes,
    scan_with_events,
)
from database import SubmantleDB
from events import EventBus, EventType
from privacy import PrivacyManager
from agent_registry import AgentRegistry
from business_registry import BusinessRegistry, TIER_LIMITS
from rate_limiter import RateLimiter, RateLimitResult, hash_ip
from fastapi_mcp import FastApiMCP

VERSION = "0.1.0"

# ── Module initialization ───────────────────────────────────────────────────
# Order matters: DB first, then bus (needs DB), then privacy and registry (need both).

_db = SubmantleDB()
_bus = EventBus(db=_db)
_privacy = PrivacyManager(db=_db, event_bus=_bus)
_registry = AgentRegistry(db=_db, event_bus=_bus)
_business_registry = BusinessRegistry(db=_db, event_bus=_bus)
_rate_limiter = RateLimiter(db=_db)

# ── FastAPI setup ────────────────────────────────────────────────────────────

app = FastAPI(title="Submantle", version=VERSION, docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

# ── MCP server ────────────────────────────────────────────────────────────────
# Read-only MCP surface for AI agents to query trust scores.
# Write operations (register, deregister, incident report) are REST-only.

_mcp = FastApiMCP(
    app,
    name="Submantle",
    description="Trust bureau for AI agents. Query trust scores and process awareness.",
    include_operations=[
        "health_api_health_get",
        "status_api_status_get",
        "query_api_query_get",
        "agents_list_api_agents_get",
        "verify_directory_api_verify_get",
        "verify_agent_api_verify__agent_name__get",
        "privacy_status_api_privacy_status_get",
    ],
    headers=["authorization", "x-api-key"],
)
_mcp.mount_http()

# ── Cache ──────────────────────────────────────────────────────────────────────
# Re-scan at most every 5 seconds to avoid hammering psutil on every poll.
# Previous process list is tracked for event diffing.

_cache: dict = {}
_cache_ts: float = 0.0
_CACHE_TTL = 5.0
_previous_processes: Optional[list] = None


def _get_state() -> dict:
    """
    Return current process state. Respects privacy mode.

    When PRIVATE: returns a lightweight sentinel dict signalling privacy mode.
    When AWARE:   scans (or serves from 5-second cache) and persists to SQLite.
    """
    global _cache, _cache_ts, _previous_processes

    # Privacy gate — return a minimal stub so callers know not to show process data.
    if _privacy.check_privacy():
        return {"privacy_mode": True}

    now = time.time()
    if now - _cache_ts < _CACHE_TTL:
        return _cache

    signatures = load_signatures()

    # Scan and emit lifecycle events, comparing against last known state.
    current_processes = scan_with_events(
        signatures=signatures,
        bus=_bus,
        privacy_manager=_privacy,
        previous_processes=_previous_processes,
    )
    _previous_processes = current_processes

    tree = build_process_tree(current_processes)
    report = awareness_report(current_processes, tree)

    # Persist snapshot to SQLite so restarts can serve the last known state.
    identified_count = report["identified_processes"]
    process_count = report["total_processes"]
    try:
        _db.save_scan_snapshot(
            data={"report": report},
            process_count=process_count,
            identified_count=identified_count,
        )
    except Exception:
        pass  # Non-fatal — the system must not break because a DB write failed.

    _cache = {
        "privacy_mode": False,
        "report": report,
        "processes": current_processes,
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


# ── Request / Response Models ───────────────────────────────────────────────

class AgentRegisterRequest(BaseModel):
    agent_name: str
    version: str
    author: str
    capabilities: list[str] = []


class BusinessRegisterRequest(BaseModel):
    business_name: str
    email: str


class IncidentReportRequest(BaseModel):
    agent_name: str
    reporter: str
    incident_type: str
    description: str = ""


def _extract_token(authorization: str | None) -> str | None:
    """Extract bearer token from Authorization header. Returns None if absent."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return authorization.removeprefix("Bearer ").strip() or None


# ── Business API Key Auth + Rate Limiting ──────────────────────────────────────

@dataclass
class BusinessContext:
    """Resolved identity and rate limit state for a business caller."""
    tier: str            # 'anonymous', 'free', 'paid'
    identifier: str      # key_hash for keyed callers, hashed IP for anonymous
    limit: int           # requests/hour for this tier
    remaining: int       # requests left in current window
    reset_at: float      # Unix epoch when window expires
    business_name: str | None


def get_business_context(
    request: Request,
    x_api_key: str | None = Header(None),
) -> BusinessContext:
    """
    FastAPI dependency: resolve business identity and enforce rate limit.

    Reads X-API-Key header. Anonymous access is allowed with lower limits.
    Raises 401 for invalid keys, 403 for deactivated keys, 429 for rate exceeded.
    """
    if x_api_key:
        biz = _business_registry.verify(x_api_key)
        if biz is None:
            raise HTTPException(status_code=401, detail="Invalid API key")
        if not biz["is_active"]:
            raise HTTPException(status_code=403, detail="API key deactivated")
        identifier = biz["key_hash"]
        tier = biz["tier"]
        limit = biz["rate_limit"]
        business_name = biz["business_name"]
    else:
        # Anonymous caller — rate limit by hashed IP
        client_ip = request.client.host if request.client else "unknown"
        identifier = hash_ip(client_ip)
        tier = "anonymous"
        limit = TIER_LIMITS["anonymous"]
        business_name = None

    # Check rate limit
    rl = _rate_limiter.check_and_increment(identifier, limit)
    if not rl.allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": str(rl.limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(rl.reset_at)),
                "Retry-After": str(int(rl.reset_at - time.time())),
            },
        )

    return BusinessContext(
        tier=tier,
        identifier=identifier,
        limit=rl.limit,
        remaining=rl.remaining,
        reset_at=rl.reset_at,
        business_name=business_name,
    )


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "alive", "version": VERSION}


@app.get("/api/status")
def status():
    state = _get_state()

    # Privacy mode — return minimal health-only response.
    if state.get("privacy_mode"):
        return {
            "privacy_mode": True,
            "status": "Submantle is running in privacy mode. No process data is being collected.",
        }

    report = state["report"]
    scanned_at = state["scanned_at"]

    return {
        "privacy_mode": False,
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
def query(process: str = "", authorization: Optional[str] = Header(None)):
    if not process.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "process parameter is required"},
        )

    # Privacy mode — no queries allowed.
    if _privacy.check_privacy():
        return JSONResponse(
            status_code=403,
            content={
                "error": "Privacy mode is active. Submantle is not watching.",
                "privacy_mode": True,
            },
        )

    # Record interaction if agent is authenticated.
    # Anonymous access still works — trust data just doesn't accumulate.
    token = _extract_token(authorization)
    if token:
        _registry.record_query(token)

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


# ── Privacy endpoints ───────────────────────────────────────────────────────

@app.post("/api/privacy/toggle")
def privacy_toggle():
    """
    Toggle privacy mode on/off.

    Returns the new state. Safe to call multiple times — idempotent
    transitions return changed=False and emit no extra events.
    """
    result = _privacy.toggle()

    # Invalidate the scan cache so the next /api/status call reflects the
    # mode change immediately rather than serving stale process data.
    global _cache, _cache_ts
    _cache = {}
    _cache_ts = 0.0

    return {
        "previous_state": result["previous_state"],
        "new_state": result["new_state"],
        "changed": result["changed"],
        "is_private": _privacy.is_private(),
    }


@app.get("/api/privacy/status")
def privacy_status():
    """Return current privacy mode state."""
    return {
        "state": _privacy.state.value,
        "is_private": _privacy.is_private(),
    }


# ── Agent endpoints ─────────────────────────────────────────────────────────

@app.post("/api/agents/register")
def agents_register(body: AgentRegisterRequest):
    """
    Register a new agent. Returns a bearer token.

    The token is the agent's credential for all subsequent calls.
    Submantle does not store the raw token — the agent must preserve it.
    """
    try:
        token = _registry.register(
            agent_name=body.agent_name,
            version=body.version,
            author=body.author,
            capabilities=body.capabilities,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {
        "token": token,
        "agent_name": body.agent_name,
    }


@app.get("/api/agents")
def agents_list():
    """
    List all registered agents.
    Token hashes are excluded from the response.
    """
    agents = _registry.list_agents()
    return {"agents": agents}


@app.delete("/api/agents/{agent_id}")
def agents_deregister(agent_id: int, authorization: Optional[str] = Header(None)):
    """
    Deregister an agent. Requires Authorization: Bearer <token> header.

    The token must belong to the agent being deregistered — agents can only
    remove themselves. This prevents unauthenticated deletion.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization: Bearer <token> header is required",
        )

    token = authorization.removeprefix("Bearer ").strip()

    # Verify the token belongs to the agent_id being deregistered.
    agent_info = _registry.verify(token)
    if agent_info is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    if agent_info["id"] != agent_id:
        raise HTTPException(
            status_code=403,
            detail="Token does not belong to this agent",
        )

    success = _registry.deregister(token)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")

    return {"deregistered": True, "agent_id": agent_id, "permanent": True}


# ── Trust Bureau — Verification (Door 2: for businesses) ──────────────────────

@app.get("/api/verify")
def verify_directory(
    request: Request,
    ctx: BusinessContext = Depends(get_business_context),
):
    """
    Public directory of all registered agents with trust scores.

    This is the trust bureau's public face. Businesses browse this to see
    which agents exist and what their scores are. Rate-limited by tier.
    """
    agents = _registry.list_agents(active_only=False)
    scored = []
    for agent in agents:
        trust = _registry.compute_trust(agent_id=agent["id"])
        if trust:
            scored.append(trust)
    response = JSONResponse(content={"agents": scored, "total": len(scored)})
    _add_ratelimit_headers(response, ctx)
    return response


@app.get("/api/verify/{agent_name}")
def verify_agent(
    agent_name: str,
    request: Request,
    ctx: BusinessContext = Depends(get_business_context),
):
    """
    Check a specific agent's trust score.

    This is the core product: a business asks "how trustworthy is this agent?"
    and gets back a score with full metadata. Rate-limited by tier.
    """
    result = _registry.compute_trust(agent_name=agent_name)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_name}' not found",
        )
    response = JSONResponse(content=result)
    _add_ratelimit_headers(response, ctx)
    return response


def _add_ratelimit_headers(response: JSONResponse, ctx: BusinessContext) -> None:
    """Add standard rate limit headers to a response."""
    response.headers["X-RateLimit-Limit"] = str(ctx.limit)
    response.headers["X-RateLimit-Remaining"] = str(ctx.remaining)
    response.headers["X-RateLimit-Reset"] = str(int(ctx.reset_at))


# ── Trust Bureau — Incident Reporting (credit bureau intake) ──────────────────

@app.post("/api/incidents/report")
def report_incident(body: IncidentReportRequest):
    """
    Report an incident involving a registered agent.

    Credit bureau model: third parties report problems. Submantle records
    them. It does not detect incidents itself. The report increments the
    agent's incident counter, which lowers their trust score.
    """
    if not body.agent_name.strip():
        raise HTTPException(status_code=422, detail="agent_name is required")
    if not body.reporter.strip():
        raise HTTPException(status_code=422, detail="reporter is required")
    if not body.incident_type.strip():
        raise HTTPException(status_code=422, detail="incident_type is required")

    result = _registry.record_incident(
        agent_name=body.agent_name,
        reporter=body.reporter,
        incident_type=body.incident_type,
        description=body.description,
    )
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{body.agent_name}' not found",
        )

    # result is a dict with status details
    if isinstance(result, dict):
        return result

    # Backward compat fallback
    return {"reported": True, "agent_name": body.agent_name}


# ── Business endpoints ─────────────────────────────────────────────────────────

@app.post("/api/business/register")
def business_register(body: BusinessRegisterRequest):
    """
    Register a new business and get an API key.

    The key is returned exactly once. The business must save it —
    Submantle stores only the hash and cannot recover the raw key.
    """
    try:
        raw_key = _business_registry.register(
            business_name=body.business_name,
            email=body.email,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return {
        "api_key": raw_key,
        "business_name": body.business_name,
        "tier": "free",
        "rate_limit": TIER_LIMITS["free"],
        "note": "Save this key — it cannot be recovered.",
    }


@app.get("/api/business/tiers")
def business_tiers():
    """Public tier information. No auth required."""
    return {
        "tiers": [
            {"name": "anonymous", "rate_limit": TIER_LIMITS["anonymous"], "requires_key": False, "price": "free"},
            {"name": "free", "rate_limit": TIER_LIMITS["free"], "requires_key": True, "price": "free"},
            {"name": "paid", "rate_limit": TIER_LIMITS["paid"], "requires_key": True, "price": "contact"},
        ],
    }


# ── Stripe webhook ─────────────────────────────────────────────────────────────

@app.post("/api/stripe/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events. Verifies signature, then processes.

    Currently handles: checkout.session.completed (upgrades business tier).
    Stripe package is lazy-imported so the server runs without it installed.
    """
    import os
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        raise HTTPException(status_code=503, detail="Stripe webhook not configured")

    try:
        import stripe
    except ImportError:
        raise HTTPException(status_code=503, detail="Stripe package not installed")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session.get("customer_details", {}).get("email")
        stripe_customer_id = session.get("customer")

        if customer_email:
            biz = _db.get_business_by_email(customer_email)
            if biz:
                _db.update_business_tier(
                    business_id=biz["id"],
                    tier="paid",
                    rate_limit=TIER_LIMITS["paid"],
                    stripe_customer_id=stripe_customer_id,
                )

    return {"received": True}


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


@app.get("/trust")
def trust_dashboard():
    """Trust bureau dashboard — agent directory, scores, business tiers."""
    html_path = Path(__file__).parent / "trust-dashboard.html"
    if html_path.exists():
        return FileResponse(str(html_path), media_type="text/html")
    return JSONResponse(
        status_code=404,
        content={"error": "trust-dashboard.html not found"},
    )
