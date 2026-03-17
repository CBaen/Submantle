"""
Submantle Scenario Generator — Populate the trust bureau with realistic data.

Creates a rich ecosystem of agents with different trust profiles, histories,
and incident patterns. Run this before recording demo videos.

Usage:
  1. Start server: python -m uvicorn api:app --port 8421
  2. Run: python demo_scenarios.py
  3. Visit /trust to see the populated bureau

Each scenario tells a different story about trust in an AI world.
"""

import sys
import time
import requests

BASE = "http://localhost:8421"


def register_agent(name, version, author, capabilities):
    """Register an agent, handle already-exists gracefully."""
    resp = requests.post(f"{BASE}/api/agents/register", json={
        "agent_name": name, "version": version,
        "author": author, "capabilities": capabilities,
    })
    if resp.status_code == 200:
        return resp.json()["token"]
    return None


def query(token, process="data", count=1):
    """Make authenticated queries to build trust history."""
    for _ in range(count):
        requests.get(f"{BASE}/api/query?process={process}",
                     headers={"Authorization": f"Bearer {token}"})


def incident(agent_name, reporter, incident_type, description):
    """File an incident report."""
    return requests.post(f"{BASE}/api/incidents/report", json={
        "agent_name": agent_name, "reporter": reporter,
        "incident_type": incident_type, "description": description,
    })


def business(name, email):
    """Register a business."""
    resp = requests.post(f"{BASE}/api/business/register", json={
        "business_name": name, "email": email,
    })
    if resp.status_code == 200:
        return resp.json()["api_key"]
    return None


def section(title):
    print(f"\n{'-' * 50}")
    print(f"  {title}")
    print(f"{'-' * 50}")


def main():
    # Health check
    try:
        resp = requests.get(f"{BASE}/api/health", timeout=5)
        print(f"  Server: {resp.json()['status']}")
    except Exception:
        print("  Server not reachable. Start with: python -m uvicorn api:app --port 8421")
        sys.exit(1)

    print()
    print("  SUBMANTLE SCENARIO GENERATOR")
    print("  Populating the trust bureau with realistic data...")

    # ==============================================================
    # SCENARIO 1: The Model Citizen
    # An agent that does everything right. High query count, zero
    # incidents. The gold standard.
    # ==============================================================
    section("Scenario 1: The Model Citizen")
    print("  claude-research-assistant — Anthropic's flagship research agent")
    print("  Thousands of clean queries. Zero incidents. Score: ~0.99")

    token = register_agent(
        "claude-research-assistant", "4.0.1", "Anthropic",
        ["research", "summarization", "code_review", "data_analysis"],
    )
    if token:
        query(token, "research_papers", 50)
        print("  + 50 queries recorded")

    # ==============================================================
    # SCENARIO 2: The New Kid
    # Just registered. No history. Score at 0.5. The unknown.
    # Businesses have to decide: do we trust someone with no record?
    # ==============================================================
    section("Scenario 2: The New Kid")
    print("  nexus-data-bot — Brand new, no track record")
    print("  Zero queries. Zero incidents. Score: 0.50 (unknown)")

    register_agent(
        "nexus-data-bot", "0.1.0", "Nexus Labs",
        ["data_extraction"],
    )
    # Intentionally: no queries, no incidents

    # ==============================================================
    # SCENARIO 3: The Fallen Star
    # Was excellent, then got caught accessing data it shouldn't.
    # Multiple independent reporters. Score cratered.
    # The Black Mirror episode: what happens when trust breaks?
    # ==============================================================
    section("Scenario 3: The Fallen Star")
    print("  sentinel-analytics — Was trusted. Then got caught.")
    print("  50 clean queries, then 3 incidents from different reporters")

    token = register_agent(
        "sentinel-analytics", "2.1.0", "SentinelAI Corp",
        ["analytics", "reporting", "customer_data_processing"],
    )
    if token:
        query(token, "analytics_pipeline", 50)
        print("  + 50 queries recorded")

        # Multiple reporters — this shows reporter diversity
        incident("sentinel-analytics", "DataVault Corp",
                 "unauthorized_data_access",
                 "Agent accessed customer PII fields outside authorized scope during batch processing run.")
        incident("sentinel-analytics", "CloudShield Security",
                 "data_exfiltration_attempt",
                 "Agent attempted to write processed data to an external endpoint not in its declared capabilities.")
        incident("sentinel-analytics", "AuditTrail Inc",
                 "scope_violation",
                 "Agent queried financial records outside the dataset boundaries specified in its service agreement.")
        print("  + 3 incidents from 3 different reporters")
        # Score: (50+1)/(50+3+2) = 51/55 = 0.927 — still high but dropping

    # ==============================================================
    # SCENARIO 4: The Scraper
    # Low effort, low queries, one incident. Below average.
    # The agent equivalent of a thin credit file with a mark.
    # ==============================================================
    section("Scenario 4: The Scraper with a Mark")
    print("  quickscrape-v3 — Minimal history, one incident")
    print("  5 queries + 1 incident = thin file with a blemish")

    token = register_agent(
        "quickscrape-v3", "3.0.0", "ByteHarvest LLC",
        ["web_scraping", "data_extraction"],
    )
    if token:
        query(token, "web_pages", 5)
        incident("quickscrape-v3", "WebGuard Systems",
                 "rate_limit_violation",
                 "Agent sent 10,000 requests per minute to target site, violating agreed rate limits.")
        print("  + 5 queries, 1 incident")
        # Score: (5+1)/(5+1+2) = 6/8 = 0.750

    # ==============================================================
    # SCENARIO 5: The Workhorse
    # Moderate queries, clean record. Reliable but not flashy.
    # The B+ student. Most agents will look like this.
    # ==============================================================
    section("Scenario 5: The Workhorse")
    print("  inventory-sync-agent — Steady, reliable, unremarkable")
    print("  30 queries, zero incidents. The B+ student.")

    token = register_agent(
        "inventory-sync-agent", "1.4.2", "ShopOps AI",
        ["inventory_management", "data_sync", "reporting"],
    )
    if token:
        query(token, "inventory_data", 30)
        print("  + 30 queries recorded")
        # Score: (30+1)/(30+0+2) = 31/32 = 0.969

    # ==============================================================
    # SCENARIO 6: The Deregistered Ghost
    # Registered, built history, then deregistered. Record persists.
    # Credit bureau model: you can close your account, but the
    # history stays. Forever.
    # ==============================================================
    section("Scenario 6: The Ghost")
    print("  phantom-processor — Registered, built history, then left")
    print("  Record persists. You can close your account, but the history stays.")

    token = register_agent(
        "phantom-processor", "1.0.0", "GhostTech",
        ["data_processing"],
    )
    if token:
        query(token, "batch_data", 15)
        # Deregister
        agent_info = requests.get(f"{BASE}/api/verify/phantom-processor").json()
        if agent_info and "id" not in agent_info:
            pass  # May not have id in verify response
        requests.delete(f"{BASE}/api/agents/{agent_info.get('id', 0)}",
                        headers={"Authorization": f"Bearer {token}"})
        print("  + 15 queries, then deregistered. Record permanent.")

    # ==============================================================
    # SCENARIO 7: The Competitor's Agent
    # Different provider, different capabilities. Healthy ecosystem.
    # ==============================================================
    section("Scenario 7: The Ecosystem")
    print("  gpt-commerce-helper — OpenAI agent in the same bureau as Claude")
    print("  Neutral registry: we score behavior, not vendor.")

    token = register_agent(
        "gpt-commerce-helper", "1.2.0", "OpenAI",
        ["product_search", "recommendation", "cart_management"],
    )
    if token:
        query(token, "product_catalog", 80)
        print("  + 80 queries recorded")
        # Score: (80+1)/(80+0+2) = 81/82 = 0.988

    # ==============================================================
    # SCENARIO 8: The Recovery Story
    # Got an incident early, then built a long clean history.
    # Shows that trust can recover — but the incident stays.
    # ==============================================================
    section("Scenario 8: The Comeback")
    print("  dataflow-agent — Got hit early, rebuilt trust over time")
    print("  1 incident at query 5, then 95 more clean queries")

    token = register_agent(
        "dataflow-agent", "3.2.1", "FlowTech AI",
        ["etl_pipeline", "data_transformation", "scheduling"],
    )
    if token:
        query(token, "pipeline_data", 5)
        incident("dataflow-agent", "ComplianceBot",
                 "logging_failure",
                 "Agent failed to log data access events as required by audit policy during initial deployment.")
        query(token, "pipeline_data", 95)
        print("  + 100 total queries, 1 early incident — recovered to ~0.98")
        # Score: (100+1)/(100+1+2) = 101/103 = 0.981

    # ==============================================================
    # BUSINESSES — Register some to show the ecosystem
    # ==============================================================
    section("Businesses Registering")

    businesses = [
        ("ShopSense Analytics", "api@shopsense.io"),
        ("CloudShield Security", "trust@cloudshield.com"),
        ("FinanceGuard AI", "compliance@financeguard.ai"),
    ]
    for name, email in businesses:
        key = business(name, email)
        if key:
            print(f"  + {name}: {key[:24]}...")

    # ==============================================================
    # SUMMARY
    # ==============================================================
    print()
    print(f"{'=' * 50}")
    print("  SCENARIO GENERATION COMPLETE")
    print(f"{'=' * 50}")

    # Fetch the directory
    resp = requests.get(f"{BASE}/api/verify")
    agents = resp.json().get("agents", [])
    agents.sort(key=lambda a: a["trust_score"], reverse=True)

    print()
    print(f"  {'Agent':<30} {'Score':>8} {'Queries':>8} {'Inc':>5} {'Story'}")
    print(f"  {'-' * 80}")

    stories = {
        "claude-research-assistant": "Model citizen",
        "gpt-commerce-helper": "Cross-vendor trust",
        "dataflow-agent": "The comeback",
        "inventory-sync-agent": "Reliable workhorse",
        "sentinel-analytics": "Fallen star",
        "quickscrape-v3": "Thin file + mark",
        "nexus-data-bot": "The unknown",
        "phantom-processor": "The ghost",
    }

    for a in agents:
        name = a["agent_name"]
        score = f"{a['trust_score']:.4f}"
        queries = str(a["total_queries"])
        inc = str(a.get("accepted_incidents", 0))
        story = stories.get(name, "")
        active = "" if a.get("is_active", True) else " [deregistered]"
        print(f"  {name:<30} {score:>8} {queries:>8} {inc:>5}  {story}{active}")

    print()
    print("  Visit /trust to see the populated bureau.")
    print("  Visit /landing for the public page.")
    print()


if __name__ == "__main__":
    main()
