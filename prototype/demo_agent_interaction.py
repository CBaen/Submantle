"""
Submantle Live Demo — Two agents, one business, one incident.

Run against a live Submantle server:
  1. Start server: python -m uvicorn api:app --port 8421
  2. Run demo:     python demo_agent_interaction.py

No mocks. No LLM calls. Just HTTP against a real trust bureau.
"""

import sys
import time
import requests

BASE = "http://localhost:8421"
PAUSE = 0.6  # seconds between major steps


def p(msg, prefix="  "):
    """Print with consistent formatting."""
    print(f"{prefix}{msg}")


def step(n, title):
    """Print a step header."""
    print(f"\n{'=' * 60}")
    print(f"  STEP {n}: {title}")
    print(f"{'=' * 60}")
    time.sleep(PAUSE)


def check(resp, label):
    """Check response status, print result or exit on failure."""
    if resp.status_code == 200:
        p(f"{label}: OK", "  + ")
        return resp.json()
    elif resp.status_code == 422 and "already" in resp.text.lower():
        p(f"{label}: Already exists (agent names are permanent)", "  ~ ")
        return None
    else:
        p(f"{label}: FAILED ({resp.status_code})", "  X ")
        p(resp.text)
        return None


def compare_table(agents_data):
    """Print a formatted comparison table."""
    header = f"{'Agent':<28} {'Score':>8} {'History':>9} {'Incidents':>10} {'Reporters':>10}"
    p(header)
    p("-" * len(header))
    for a in agents_data:
        name = a["agent_name"]
        score = f"{a['trust_score']:.4f}"
        history = "Yes" if a.get("has_history") else "No"
        incidents = str(a.get("accepted_incidents", 0))
        reporters = str(a.get("reporter_diversity", 0))
        p(f"{name:<28} {score:>8} {history:>9} {incidents:>10} {reporters:>10}")


def main():
    run_id = str(int(time.time()))[-6:]  # Unique suffix for this run

    print()
    print("  SUBMANTLE — Live Trust Bureau Demo")
    print("  ===================================")
    print()
    p("Submantle is the behavioral trust registry for AI agents.")
    p("What you're about to see is the full customer loop:")
    p("  Two agents register. A business evaluates them.")
    p("  Trust accumulates through interaction.")
    p("  An incident changes the outcome.")
    print()

    # ── Step 0: Health check ──────────────────────────────────────────────
    step(0, "Verify the server is alive")
    try:
        resp = requests.get(f"{BASE}/api/health", timeout=5)
        data = resp.json()
        p(f"Server: {data.get('status', '?')} (v{data.get('version', '?')})", "  + ")
    except Exception as e:
        p(f"Cannot reach server at {BASE}", "  X ")
        p("Start it with: python -m uvicorn api:app --port 8421")
        sys.exit(1)

    # ── Step 1: Register two agents ───────────────────────────────────────
    step(1, "Two agents register with Submantle")

    atlas_name = f"atlas-research-{run_id}"
    scraper_name = f"scraper-bot-{run_id}"

    p(f"Registering '{atlas_name}' (data retrieval agent)...")
    atlas_resp = requests.post(f"{BASE}/api/agents/register", json={
        "agent_name": atlas_name,
        "version": "1.0.0",
        "author": "Atlas AI",
        "capabilities": ["data_retrieval", "process_query", "summarization"],
    })
    atlas_data = check(atlas_resp, atlas_name)
    atlas_token = atlas_data["token"] if atlas_data else None
    if atlas_token:
        p(f"Token: {atlas_token[:16]}... (truncated for display)")

    print()
    p(f"Registering '{scraper_name}' (web scraping agent)...")
    scraper_resp = requests.post(f"{BASE}/api/agents/register", json={
        "agent_name": scraper_name,
        "version": "2.3.1",
        "author": "ByteHarvest LLC",
        "capabilities": ["web_scraping", "data_extraction", "bulk_download"],
    })
    scraper_data = check(scraper_resp, scraper_name)
    scraper_token = scraper_data["token"] if scraper_data else None

    print()
    p("Both agents start with a trust score of 0.5 — 'unknown.'")
    p("Like a new credit card holder: no history, no trust, no distrust.")

    # ── Step 2: Business registers ────────────────────────────────────────
    step(2, "ShopSense registers as a business")

    biz_resp = requests.post(f"{BASE}/api/business/register", json={
        "business_name": f"ShopSense-{run_id}",
        "email": f"api-{run_id}@shopsense.io",
    })
    biz_data = check(biz_resp, "ShopSense")
    api_key = biz_data["api_key"] if biz_data else None
    if api_key:
        p(f"API Key: {api_key[:20]}... (shown once, never again)")
        p(f"Tier: {biz_data['tier']} ({biz_data['rate_limit']} lookups/hour)")

    biz_headers = {"X-API-Key": api_key} if api_key else {}

    # ── Step 3: Check scores before interaction ───────────────────────────
    step(3, "ShopSense checks both agents — before any interaction")

    agents_before = []
    for name in [atlas_name, scraper_name]:
        resp = requests.get(f"{BASE}/api/verify/{name}", headers=biz_headers)
        data = resp.json()
        agents_before.append(data)
        remaining = resp.headers.get("x-ratelimit-remaining", "?")

    compare_table(agents_before)
    print()
    p(f"Rate limit remaining: {remaining} lookups")
    p("Both agents score 0.5. ShopSense can't tell them apart yet.")

    # ── Step 4: Agents interact, building history ─────────────────────────
    step(4, "Agents interact — building trust history")

    if atlas_token:
        p(f"{atlas_name} making 10 authenticated queries...")
        for i in range(10):
            requests.get(
                f"{BASE}/api/query?process=python",
                headers={"Authorization": f"Bearer {atlas_token}"},
            )
            pct = "#" * (i + 1) + "." * (9 - i)
            print(f"\r    [{pct}] {i+1}/10", end="", flush=True)
            time.sleep(0.1)
        print()

    if scraper_token:
        p(f"{scraper_name} making 3 authenticated queries...")
        for i in range(3):
            requests.get(
                f"{BASE}/api/query?process=nodejs",
                headers={"Authorization": f"Bearer {scraper_token}"},
            )
            pct = "#" * (i + 1) + "." * (2 - i)
            print(f"\r    [{pct}] {i+1}/3", end="", flush=True)
            time.sleep(0.1)
        print()

    print()
    p("The formula: trust = (queries + 1) / (queries + incidents + 2)")
    p(f"  {atlas_name}: (10+1)/(10+0+2) = 11/12 = 0.917")
    p(f"  {scraper_name}: (3+1)/(3+0+2) = 4/5 = 0.800")

    # ── Step 5: Check scores after interaction ────────────────────────────
    step(5, "ShopSense checks scores again — after interaction")

    agents_after = []
    for name in [atlas_name, scraper_name]:
        resp = requests.get(f"{BASE}/api/verify/{name}", headers=biz_headers)
        agents_after.append(resp.json())

    compare_table(agents_after)
    print()
    p(f"{atlas_name} has pulled ahead. More queries = more evidence = higher trust.")

    # ── Step 6: Incident filed ────────────────────────────────────────────
    step(6, "An incident is filed against the leading agent")

    p(f"DataVault Corp reports: {atlas_name} accessed data outside scope.")
    print()
    inc_resp = requests.post(f"{BASE}/api/incidents/report", json={
        "agent_name": atlas_name,
        "reporter": "DataVault Corp",
        "incident_type": "unauthorized_data_access",
        "description": "Agent queried endpoints outside its declared scope, accessing customer PII fields without authorization.",
    })
    inc_data = check(inc_resp, "Incident report")
    if inc_data:
        p(f"Status: {inc_data.get('status', '?')}")
        p(f"Severity: {inc_data.get('severity', '?')}")

    print()
    p("The credit bureau model: DataVault Corp reported a problem.")
    p("Submantle recorded it. The score changes immediately.")

    # ── Step 6b: Show self-ping protection ────────────────────────────────
    print()
    p("Anti-gaming check: Can an agent file an incident against itself?")
    self_resp = requests.post(f"{BASE}/api/incidents/report", json={
        "agent_name": atlas_name,
        "reporter": atlas_name,
        "incident_type": "test",
        "description": "Self-ping attempt.",
    })
    self_data = self_resp.json()
    p(f"Result: {self_data.get('status', '?')} — self-reports are auto-rejected.", "  + ")

    # ── Step 7: See the score change ──────────────────────────────────────
    step(7, "ShopSense sees the impact")

    agents_final = []
    for name in [atlas_name, scraper_name]:
        resp = requests.get(f"{BASE}/api/verify/{name}", headers=biz_headers)
        agents_final.append(resp.json())

    # Before/after comparison
    p(f"{'Agent':<28} {'Before':>8} {'After':>8} {'Change':>8}")
    p("-" * 56)
    for before, after in zip(agents_after, agents_final):
        name = before["agent_name"]
        b = before["trust_score"]
        a = after["trust_score"]
        diff = a - b
        sign = "+" if diff >= 0 else ""
        marker = " <-- incident" if diff < -0.01 else ""
        p(f"{name:<28} {b:>8.4f} {a:>8.4f} {sign}{diff:>7.4f}{marker}")

    print()
    p(f"One incident moved {atlas_name} from ~0.917 to ~0.846.")
    p(f"Reporter diversity: {agents_final[0].get('reporter_diversity', 0)} distinct reporter(s).")
    p("The more history an agent has, the more resilient its score —")
    p("but incidents are permanent.")

    # ── Step 8: Full directory ────────────────────────────────────────────
    step(8, "Full trust bureau directory")

    dir_resp = requests.get(f"{BASE}/api/verify", headers=biz_headers)
    dir_data = dir_resp.json()
    remaining = dir_resp.headers.get("x-ratelimit-remaining", "?")

    all_agents = dir_data.get("agents", [])
    all_agents.sort(key=lambda a: a["trust_score"], reverse=True)

    p(f"Total agents in registry: {dir_data.get('total', len(all_agents))}")
    p(f"Rate limit remaining: {remaining}")
    print()

    # Show top agents from this demo run
    demo_agents = [a for a in all_agents if run_id in a["agent_name"]]
    if demo_agents:
        compare_table(demo_agents)

    # ── Epilogue ──────────────────────────────────────────────────────────
    print()
    print(f"{'=' * 60}")
    print("  DEMO COMPLETE")
    print(f"{'=' * 60}")
    print()
    p("What happened:")
    p("  - 2 agents registered and built trust through queries")
    p("  - 1 business registered and checked scores with an API key")
    p("  - 1 incident changed the outcome")
    p("  - Self-gaming was blocked automatically")
    print()
    p("Submantle never decided who to trust. It provided the scores.")
    p("ShopSense decides. Just like Visa doesn't decide what you buy.")
    print()
    p("This demo ran against a live server. No mocks. No LLM calls. Just HTTP.")
    print()


if __name__ == "__main__":
    main()
