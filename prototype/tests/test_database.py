"""
Tests for prototype/database.py — SubmantleDB

Runs entirely in memory (:memory:) — no files created, no cleanup needed.
Each test gets a fresh database via the db fixture.

Run: cd prototype && python -m pytest tests/test_database.py -v
"""

import time

import pytest

# Add prototype/ to path so imports work whether running from project root or prototype/
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SubmantleDB


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def db():
    """Fresh in-memory database for each test. No disk I/O, no cleanup."""
    return SubmantleDB(":memory:")


# ── Initialization ─────────────────────────────────────────────────────────────

class TestInitialization:
    def test_creates_schema(self, db):
        """All four tables must exist after init."""
        with db._conn() as conn:
            tables = {
                row[0] for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
        assert "scan_snapshots" in tables
        assert "agent_registry" in tables
        assert "events" in tables
        assert "settings" in tables

    def test_wal_mode(self, db):
        """WAL journal mode must be active. In-memory DBs use 'memory' mode —
        that's expected and fine for testing; WAL only applies to file-backed DBs."""
        with db._conn() as conn:
            result = conn.execute("PRAGMA journal_mode").fetchone()[0]
        # In-memory: 'memory', file-backed: 'wal'
        assert result in ("wal", "memory")

    def test_idempotent_init(self):
        """Calling __init__ twice on same path must not fail or duplicate schema."""
        db = SubmantleDB(":memory:")
        # Re-initialize the same instance (simulating server restart with same file)
        db._initialize()  # Should not raise or create duplicate tables


# ── scan_snapshots ─────────────────────────────────────────────────────────────

class TestScanSnapshots:
    def test_save_and_retrieve_latest(self, db):
        """Save a snapshot and get it back via get_latest_scan."""
        data = {"processes": [{"pid": 1, "name": "init"}], "total": 1}
        row_id = db.save_scan_snapshot(data, process_count=1, identified_count=0)

        assert isinstance(row_id, int)
        assert row_id > 0

        latest = db.get_latest_scan()
        assert latest is not None
        assert latest["process_count"] == 1
        assert latest["identified_count"] == 0
        assert latest["data"] == data
        assert latest["analytics_metadata"] is None

    def test_latest_scan_returns_none_when_empty(self, db):
        assert db.get_latest_scan() is None

    def test_get_latest_returns_most_recent(self, db):
        """With multiple snapshots, get_latest_scan returns the newest."""
        db.save_scan_snapshot({"batch": 1}, process_count=10, identified_count=3)
        time.sleep(0.01)  # ensure distinct timestamps
        db.save_scan_snapshot({"batch": 2}, process_count=20, identified_count=5)

        latest = db.get_latest_scan()
        assert latest["data"]["batch"] == 2
        assert latest["process_count"] == 20

    def test_analytics_metadata_stored_and_retrieved(self, db):
        """analytics_metadata JSON round-trips correctly."""
        meta = {"device_count": 1, "aggregated": True}
        db.save_scan_snapshot(
            {"x": 1}, process_count=5, identified_count=2,
            analytics_metadata=meta
        )
        latest = db.get_latest_scan()
        assert latest["analytics_metadata"] == meta

    def test_analytics_metadata_nullable(self, db):
        """analytics_metadata defaults to None when not provided."""
        db.save_scan_snapshot({"x": 1}, process_count=1, identified_count=0)
        latest = db.get_latest_scan()
        assert latest["analytics_metadata"] is None

    def test_get_scan_history_order(self, db):
        """History is returned newest-first."""
        for i in range(5):
            db.save_scan_snapshot({"i": i}, process_count=i, identified_count=0)
            time.sleep(0.005)

        history = db.get_scan_history(limit=5)
        counts = [h["process_count"] for h in history]
        assert counts == sorted(counts, reverse=True)

    def test_get_scan_history_respects_limit(self, db):
        for i in range(10):
            db.save_scan_snapshot({"i": i}, process_count=i, identified_count=0)

        history = db.get_scan_history(limit=3)
        assert len(history) == 3

    def test_prune_scan_history(self, db):
        """Prune keeps the N most recent rows and deletes the rest."""
        for i in range(10):
            db.save_scan_snapshot({"i": i}, process_count=i, identified_count=0)

        deleted = db.prune_scan_history(keep_count=5)
        assert deleted == 5

        remaining = db.get_scan_history(limit=100)
        assert len(remaining) == 5

    def test_prune_no_op_when_within_limit(self, db):
        """Prune with keep_count > existing rows deletes nothing."""
        db.save_scan_snapshot({"x": 1}, process_count=1, identified_count=0)
        deleted = db.prune_scan_history(keep_count=100)
        assert deleted == 0


# ── agent_registry ─────────────────────────────────────────────────────────────

class TestAgentRegistry:
    def _sample_agent(self, db, suffix=""):
        return db.register_agent(
            agent_name=f"TestAgent{suffix}",
            version="1.0.0",
            author="Test Author",
            capabilities=["read_processes", "query_status"],
            token_hash=f"deadbeef{suffix}",
        )

    def test_register_and_retrieve_by_token_hash(self, db):
        agent_id = self._sample_agent(db)
        agent = db.get_agent_by_token_hash("deadbeef")

        assert agent is not None
        assert agent["id"] == agent_id
        assert agent["agent_name"] == "TestAgent"
        assert agent["version"] == "1.0.0"
        assert agent["author"] == "Test Author"
        assert agent["capabilities"] == ["read_processes", "query_status"]
        assert agent["token_hash"] == "deadbeef"
        assert agent["total_queries"] == 0
        assert agent["incidents"] == 0
        assert agent["trust_metadata"] is None

    def test_get_agent_by_id(self, db):
        agent_id = self._sample_agent(db)
        agent = db.get_agent_by_id(agent_id)
        assert agent is not None
        assert agent["id"] == agent_id

    def test_get_agent_not_found(self, db):
        assert db.get_agent_by_token_hash("nonexistent") is None
        assert db.get_agent_by_id(9999) is None

    def test_list_agents_empty(self, db):
        assert db.list_agents() == []

    def test_list_agents(self, db):
        self._sample_agent(db, "A")
        self._sample_agent(db, "B")
        agents = db.list_agents()
        assert len(agents) == 2
        names = {a["agent_name"] for a in agents}
        assert names == {"TestAgentA", "TestAgentB"}

    def test_capabilities_round_trip(self, db):
        """Capabilities list serializes/deserializes correctly."""
        db.register_agent("X", "1.0", "Y", ["cap1", "cap2", "cap3"], "hash1")
        agent = db.get_agent_by_token_hash("hash1")
        assert agent["capabilities"] == ["cap1", "cap2", "cap3"]

    def test_token_hash_unique_constraint(self, db):
        """Registering two agents with the same token_hash must fail."""
        db.register_agent("AgentA", "1.0", "X", [], "samehash")
        with pytest.raises(Exception):  # sqlite3.IntegrityError
            db.register_agent("AgentB", "1.0", "Y", [], "samehash")

    def test_update_last_seen(self, db):
        agent_id = self._sample_agent(db)
        before = db.get_agent_by_id(agent_id)["last_seen"]
        time.sleep(0.01)
        db.update_agent_last_seen(agent_id)
        after = db.get_agent_by_id(agent_id)["last_seen"]
        assert after > before

    def test_increment_queries(self, db):
        agent_id = self._sample_agent(db)
        db.increment_agent_queries(agent_id)
        db.increment_agent_queries(agent_id)
        agent = db.get_agent_by_id(agent_id)
        assert agent["total_queries"] == 2

    def test_increment_incidents(self, db):
        agent_id = self._sample_agent(db)
        db.increment_agent_incidents(agent_id)
        agent = db.get_agent_by_id(agent_id)
        assert agent["incidents"] == 1

    def test_deregister_agent(self, db):
        agent_id = self._sample_agent(db)
        result = db.deregister_agent(agent_id)
        assert result is True
        assert db.get_agent_by_id(agent_id) is None

    def test_deregister_nonexistent_returns_false(self, db):
        assert db.deregister_agent(9999) is False

    def test_trust_metadata_round_trip(self, db):
        db.register_agent("X", "1.0", "Y", [], "hash2",
                          trust_metadata={"score": 0.9, "flags": []})
        agent = db.get_agent_by_token_hash("hash2")
        assert agent["trust_metadata"] == {"score": 0.9, "flags": []}

    def test_update_trust_metadata(self, db):
        agent_id = self._sample_agent(db)
        db.update_trust_metadata(agent_id, {"score": 0.75})
        agent = db.get_agent_by_id(agent_id)
        assert agent["trust_metadata"] == {"score": 0.75}


# ── events ─────────────────────────────────────────────────────────────────────

class TestEvents:
    def test_log_and_retrieve(self, db):
        db.log_event("SCAN_COMPLETE", {"process_count": 42})
        events = db.get_recent_events(limit=1)
        assert len(events) == 1
        assert events[0]["event_type"] == "SCAN_COMPLETE"
        assert events[0]["data"]["process_count"] == 42
        assert events[0]["privacy_mode_active"] is False

    def test_privacy_mode_flag_stored(self, db):
        db.log_event("PRIVACY_TOGGLED", {"active": True}, privacy_mode_active=True)
        events = db.get_recent_events(event_type="PRIVACY_TOGGLED")
        assert events[0]["privacy_mode_active"] is True

    def test_get_recent_events_newest_first(self, db):
        for i in range(5):
            db.log_event("SCAN_COMPLETE", {"i": i})

        events = db.get_recent_events(limit=5)
        # Events are ordered newest-first; the last inserted has highest id
        ids = [e["id"] for e in events]
        assert ids == sorted(ids, reverse=True)

    def test_filter_by_event_type(self, db):
        db.log_event("SCAN_COMPLETE", {})
        db.log_event("PROCESS_STARTED", {"pid": 1})
        db.log_event("SCAN_COMPLETE", {})

        scans = db.get_recent_events(event_type="SCAN_COMPLETE")
        assert len(scans) == 2
        assert all(e["event_type"] == "SCAN_COMPLETE" for e in scans)

    def test_get_recent_events_respects_limit(self, db):
        for _ in range(10):
            db.log_event("SCAN_COMPLETE", {})
        events = db.get_recent_events(limit=3)
        assert len(events) == 3

    def test_prune_events(self, db):
        for i in range(10):
            db.log_event("SCAN_COMPLETE", {"i": i})

        deleted = db.prune_events(keep_count=5)
        assert deleted == 5
        remaining = db.get_recent_events(limit=100)
        assert len(remaining) == 5

    def test_data_json_round_trip(self, db):
        """Complex nested data survives the JSON round-trip."""
        payload = {
            "process_count": 100,
            "categories": {"browser": 3, "editor": 1},
            "critical": ["postgres", "docker"],
        }
        db.log_event("SCAN_COMPLETE", payload)
        event = db.get_recent_events(limit=1)[0]
        assert event["data"] == payload


# ── settings ───────────────────────────────────────────────────────────────────

class TestSettings:
    def test_get_nonexistent_returns_default(self, db):
        assert db.get_setting("nonexistent") is None
        assert db.get_setting("nonexistent", "fallback") == "fallback"

    def test_set_and_get(self, db):
        db.set_setting("privacy_mode", "false")
        assert db.get_setting("privacy_mode") == "false"

    def test_set_overwrites(self, db):
        db.set_setting("key", "v1")
        db.set_setting("key", "v2")
        assert db.get_setting("key") == "v2"

    def test_values_stored_as_strings(self, db):
        """Non-string values are coerced to string."""
        db.set_setting("count", 42)
        assert db.get_setting("count") == "42"

    def test_delete_setting(self, db):
        db.set_setting("to_delete", "yes")
        result = db.delete_setting("to_delete")
        assert result is True
        assert db.get_setting("to_delete") is None

    def test_delete_nonexistent_returns_false(self, db):
        assert db.delete_setting("ghost") is False

    def test_all_settings(self, db):
        db.set_setting("a", "1")
        db.set_setting("b", "2")
        settings = db.all_settings()
        assert settings == {"a": "1", "b": "2"}

    def test_set_updates_timestamp(self, db):
        db.set_setting("ts_test", "v1")
        with db._conn() as conn:
            t1 = conn.execute(
                "SELECT updated_at FROM settings WHERE key = 'ts_test'"
            ).fetchone()[0]

        time.sleep(0.01)
        db.set_setting("ts_test", "v2")
        with db._conn() as conn:
            t2 = conn.execute(
                "SELECT updated_at FROM settings WHERE key = 'ts_test'"
            ).fetchone()[0]

        assert t2 > t1
