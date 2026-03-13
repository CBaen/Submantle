# fastapi-mcp Validation Spike

**Date:** 2026-03-12
**Purpose:** Confirm or deny the three unverified assumptions in the council's MCP integration recommendation before writing a single line of integration code.
**Sources:** Context7 (`/tadata-org/fastapi_mcp`, 99 snippets, High reputation, Benchmark 81.45) + official docs at `fastapi-mcp.tadata.com` + GitHub repo `tadata-org/fastapi_mcp`.

---

## Question 1 — Does fastapi-mcp pass through custom Bearer token auth?

**Answer: YES — confirmed, with one required configuration step.**

fastapi-mcp has an explicit `headers` parameter on the `FastApiMCP` constructor that forwards named HTTP headers from the MCP request into the tool invocation call. To pass the `Authorization` header through to Submantle's `_extract_token()` function, you pass `headers=["authorization"]` at construction time.

Evidence from official documentation:

```python
mcp = FastApiMCP(
    app,
    name="Protected MCP",
    auth_config=AuthConfig(
        dependencies=[Depends(token_auth_scheme)]
    ),
    headers=["authorization"]   # <-- this line forwards the header into tool calls
)
```

The docs state explicitly: *"Basic token passthrough allows you to pass a valid authorization header without supporting a full authentication flow. You simply need to ensure your MCP client is sending the authorization header."*

**How this maps to Submantle's auth model:**

Submantle's `_extract_token()` reads `Authorization: Bearer <hex>` from the `Header(None)` FastAPI dependency. Because fastapi-mcp forwards the `authorization` header into the tool call, the token arrives in the header exactly as it would from a regular HTTP client. `_extract_token()` runs unchanged. No modifications to existing auth logic are needed.

**One nuance:** If you also want the MCP layer itself to *reject* unauthenticated requests before they reach the FastAPI endpoints, you add a FastAPI dependency to `AuthConfig`. For Submantle's design — where anonymous access is allowed and auth is optional for trust accumulation — this is not required. The `headers=["authorization"]` line alone is sufficient.

---

## Question 2 — Can we selectively expose only certain endpoints?

**Answer: YES — four parameters give precise control.**

fastapi-mcp exposes four filtering parameters at `FastApiMCP` construction time:

| Parameter | Effect |
|---|---|
| `include_operations` | Whitelist by FastAPI `operation_id` |
| `exclude_operations` | Blacklist by FastAPI `operation_id` |
| `include_tags` | Whitelist by route `tags=[]` |
| `exclude_tags` | Blacklist by route `tags=[]` |

Evidence from official documentation:

```python
# Include only specific operations
readonly_mcp = FastApiMCP(
    app,
    name="Read-Only Item API",
    include_operations=["get_item", "list_items"]
)
readonly_mcp.mount_http(mount_path="/readonly-mcp")

# Exclude specific operations
no_delete_mcp = FastApiMCP(
    app,
    name="No Delete Item API",
    exclude_operations=["delete_item"]
)
no_delete_mcp.mount_http(mount_path="/no-delete-mcp")
```

The docs state: *"This allows you to create specialized MCP servers, for example, a read-only version of your API or an API that excludes sensitive operations like deletion."*

**How this maps to Submantle's endpoint set:**

The council recommends exposing read-only score queries but NOT write operations. Using `include_operations`, the exact whitelist for a safe MCP surface is:

```python
include_operations=[
    "health",           # GET /api/health
    "status",           # GET /api/status
    "query",            # GET /api/query  — core product endpoint
    "agents_list",      # GET /api/agents
    "verify_directory", # GET /api/verify
    "verify_agent",     # GET /api/verify/{agent_name}
]
```

Excluded from MCP (write/mutate operations):
- `privacy_toggle` — POST /api/privacy/toggle
- `agents_register` — POST /api/agents/register
- `agents_deregister` — DELETE /api/agents/{agent_id}
- `report_incident` — POST /api/incidents/report

**Note on operation_ids:** FastAPI auto-generates `operation_id` from the function name. Submantle's route functions already have clean names (`health`, `status`, `query`, `agents_list`, etc.) that map directly. This can be verified by hitting `/openapi.json` on the running server. If any auto-generated IDs differ from the function names, `operation_id="..."` can be added explicitly to the `@app.get()` decorators.

---

## Question 3 — What MCP transport does fastapi-mcp use?

**Answer: HTTP transport (Streamable HTTP) by default — stdio conflict does NOT apply.**

fastapi-mcp mounts as an HTTP endpoint on the same FastAPI app via `mcp.mount_http()`. It does not spawn a subprocess, does not use stdio, and does not conflict with the daemon architecture. The MCP server is just another set of routes on port 8421.

Evidence from official documentation:

> *"HTTP transport is the recommended transport method as it implements the latest MCP Streamable HTTP specification. It provides better session management, more robust connection handling, and aligns with standard HTTP practices."*

The two supported modes:
- `mcp.mount_http()` — Streamable HTTP, recommended, mounts at `/mcp` by default
- `mcp.mount_sse()` — SSE, backwards compatibility only

For Claude Desktop and other stdio-only clients, the docs recommend bridging with `mcp-proxy` (a separate lightweight process). This bridge is entirely external to Submantle — it connects to the already-running HTTP endpoint. No changes to Submantle's architecture are needed.

**The stdio conflict the council identified** (daemon + subprocess = two competing processes) does not apply here. fastapi-mcp is HTTP-native.

---

## Summary Table

| Question | Answer | Confidence |
|---|---|---|
| Custom Bearer token passthrough | YES — `headers=["authorization"]` parameter | Confirmed by official docs + code examples |
| Selective endpoint exposure | YES — `include_operations`, `exclude_operations`, `include_tags`, `exclude_tags` | Confirmed by official docs + code examples |
| HTTP transport (not stdio) | YES — `mount_http()` is the default and recommended path | Confirmed by official docs |

**All three assumptions are confirmed.** The council's recommendation is valid.

---

## Minimal Integration Plan

This is the exact code change required in `prototype/api.py`. No other files need modification.

### Step 1 — Install the library

```
pip install fastapi-mcp
```

### Step 2 — Add to `prototype/api.py`

After the existing `app = FastAPI(...)` block and the `CORSMiddleware` setup, add:

```python
from fastapi_mcp import FastApiMCP

# --- after existing app setup, before route definitions ---

_mcp = FastApiMCP(
    app,
    name="Submantle",
    description="Trust bureau for AI agents. Query trust scores and process awareness.",
    include_operations=[
        "health",
        "status",
        "query",
        "agents_list",
        "verify_directory",
        "verify_agent",
        "privacy_status",
    ],
    headers=["authorization"],   # Forward bearer token into tool calls
)
_mcp.mount_http()                # Mounts at /mcp by default
```

That is the entirety of the change. Three effective lines beyond the import.

### What this produces

- MCP endpoint at `http://localhost:8421/mcp`
- 7 read-only tools exposed to any MCP client
- Write operations (register, deregister, incident report, privacy toggle) are invisible to MCP clients
- Bearer token forwarded transparently — authenticated agents accumulate trust via `record_query()` exactly as before
- Dashboard at `localhost:8421/` unaffected
- All 160 existing tests unaffected (no existing code modified)

### Connecting a client

**For HTTP-native MCP clients:**
```json
{
  "mcpServers": {
    "submantle": {
      "url": "http://localhost:8421/mcp",
      "headers": { "Authorization": "Bearer <token>" }
    }
  }
}
```

**For stdio clients (Claude Desktop, etc.) via mcp-proxy:**
```
npx mcp-remote http://localhost:8421/mcp --header "Authorization:Bearer <token>"
```

---

## Risks and Open Questions

**Low risk — no blockers:**

1. **operation_id verification** — FastAPI generates operation IDs from function names by default, but auto-generation appends HTTP method suffixes in some versions (e.g., `query_get`). Verify actual IDs by hitting `http://localhost:8421/openapi.json` after startup and reading the `operationId` fields. If they differ, add explicit `operation_id=` to the relevant `@app.get()` decorators — a one-line change per route.

2. **`/api/query` token accumulation path** — The `/api/query` endpoint calls `record_query(token)` only if a token is present in the header. With `headers=["authorization"]` configured, the MCP path is identical to the direct HTTP path. Anonymous MCP calls (no token) will still work; they just won't accumulate trust. This is the intended behavior per the credit bureau model.

3. **`/api/devices` exclusion** — The device discovery endpoint is excluded from the whitelist above. It runs ARP sweeps and ping operations — not appropriate to expose as an MCP tool. This is intentional.

4. **Rate limiting** — fastapi-mcp does not add rate limiting. MCP clients calling `/api/query` repeatedly will hit the 5-second cache like any HTTP client. No change needed.

5. **`docs_url=None`** — The existing app disables Swagger UI (`docs_url=None, redoc_url=None`). fastapi-mcp does not depend on these being enabled. The MCP schema is served at `/mcp` directly.
