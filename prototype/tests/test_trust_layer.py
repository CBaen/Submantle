"""
Tests for trust layer functionality in prototype/agent_registry.py and
prototype/database.py.

Covers:
  - compute_trust() — Beta Reputation formula, lookup by name and id
  - record_incident() — counter increment, trust effect, DB storage, event emission
  - Agent name uniqueness — duplicate rejection, deregister-then-reregister
  - Database incident_reports table — save, retrieve, ordering, filtering
  - EventBus privacy behaviour for INCIDENT_REPORTED

All tests use real classes with ':memory:' SQLite — no mocks.

Run:
    cd prototype && python -m pytest tests/test_trust_layer.py -v
    # or without pytest:
    cd prototype && python tests/test_trust_layer.py
"""

import sqlite3
import unittest

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SubmantleDB
from agent_registry import AgentRegistry
from events import EventBus, EventType


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_registry(with_bus=False):
    """Return (registry, db) — optionally also (registry, db, bus)."""
    db = SubmantleDB(":memory:")
    if with_bus:
        bus = EventBus()
        registry = AgentRegistry(db=db, event_bus=bus)
        return registry, db, bus
    return AgentRegistry(db=db), db


def _register(registry, name="test-agent", version="1.0.0", author="Tester"):
    """Register an agent and return its token."""
    return registry.register(name, version, author, [])


# ── TestComputeTrust ───────────────────────────────────────────────────────────

class TestComputeTrust(unittest.TestCase):
    """compute_trust() — Beta Reputation formula and lookups."""

    def test_compute_trust_new_agent_scores_half(self):
        """Brand new agent with zero queries and zero incidents scores 0.5."""
        registry, db = _make_registry()
        _register(registry, "fresh-agent")
        result = registry.compute_trust(agent_name="fresh-agent")
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result["trust_score"], 0.5, places=4)

    def test_compute_trust_after_queries_increases(self):
        """Recording queries raises the trust score above 0.5."""
        registry, db = _make_registry()
        token = _register(registry, "query-agent")
        for _ in range(5):
            registry.record_query(token)
        result = registry.compute_trust(agent_name="query-agent")
        self.assertIsNotNone(result)
        self.assertGreater(result["trust_score"], 0.5)

    def test_compute_trust_after_incidents_decreases(self):
        """An incident report lowers the trust score below 0.5."""
        registry, db = _make_registry()
        _register(registry, "bad-agent")
        registry.record_incident(
            agent_name="bad-agent",
            reporter="acme-brand",
            incident_type="policy_violation",
        )
        result = registry.compute_trust(agent_name="bad-agent")
        self.assertIsNotNone(result)
        self.assertLess(result["trust_score"], 0.5)

    def test_compute_trust_formula_correctness(self):
        """10 queries + 2 incidents: score = (10+1)/(10+2+2) = 11/14 ≈ 0.7857."""
        registry, db = _make_registry()
        token = _register(registry, "formula-agent")
        for _ in range(10):
            registry.record_query(token)
        for _ in range(2):
            registry.record_incident(
                agent_name="formula-agent",
                reporter="acme-brand",
                incident_type="policy_violation",
            )
        result = registry.compute_trust(agent_name="formula-agent")
        expected = round(11 / 14, 4)
        self.assertAlmostEqual(result["trust_score"], expected, places=4)

    def test_compute_trust_by_name(self):
        """Look up by agent_name returns the correct agent's score."""
        registry, db = _make_registry()
        _register(registry, "named-agent")
        result = registry.compute_trust(agent_name="named-agent")
        self.assertIsNotNone(result)
        self.assertEqual(result["agent_name"], "named-agent")

    def test_compute_trust_by_id(self):
        """Look up by agent_id returns the correct agent's score."""
        registry, db = _make_registry()
        _register(registry, "id-agent")
        record = db.get_agent_by_name("id-agent")
        agent_id = record["id"]
        result = registry.compute_trust(agent_id=agent_id)
        self.assertIsNotNone(result)
        self.assertEqual(result["agent_name"], "id-agent")

    def test_compute_trust_unknown_agent_returns_none(self):
        """Querying a non-existent agent name returns None."""
        registry, db = _make_registry()
        result = registry.compute_trust(agent_name="ghost-agent")
        self.assertIsNone(result)

    def test_compute_trust_returns_metadata(self):
        """Result dict contains all required metadata fields."""
        registry, db = _make_registry()
        _register(registry, "meta-agent", version="2.0.0", author="Meta Corp")
        result = registry.compute_trust(agent_name="meta-agent")
        self.assertIsNotNone(result)
        required_keys = {
            "agent_name", "trust_score", "total_queries", "incidents",
            "registration_time", "last_seen", "version", "author",
            "score_version", "has_history", "reporter_diversity", "is_active",
        }
        self.assertEqual(required_keys, set(result.keys()))
        self.assertEqual(result["agent_name"], "meta-agent")
        self.assertEqual(result["version"], "2.0.0")
        self.assertEqual(result["author"], "Meta Corp")
        self.assertEqual(result["total_queries"], 0)
        self.assertEqual(result["incidents"], 0)

    def test_compute_trust_no_db_returns_none(self):
        """Registry without a DB cannot compute trust — returns None."""
        registry = AgentRegistry()  # no db
        result = registry.compute_trust(agent_name="any-agent")
        self.assertIsNone(result)


# ── TestRecordIncident ─────────────────────────────────────────────────────────

class TestRecordIncident(unittest.TestCase):
    """record_incident() — counter, trust effect, persistence, events."""

    def test_record_incident_increments_counter(self):
        """Reporting an incident increments the agent's incident counter to 1."""
        registry, db = _make_registry()
        _register(registry, "counter-agent")
        registry.record_incident(
            agent_name="counter-agent",
            reporter="brand-x",
            incident_type="unauthorized_access",
        )
        record = db.get_agent_by_name("counter-agent")
        self.assertEqual(record["incidents"], 1)

    def test_record_incident_lowers_trust_score(self):
        """After 5 queries, an incident lowers the score compared to pre-incident."""
        registry, db = _make_registry()
        token = _register(registry, "trust-drop-agent")
        for _ in range(5):
            registry.record_query(token)
        before = registry.compute_trust(agent_name="trust-drop-agent")["trust_score"]
        registry.record_incident(
            agent_name="trust-drop-agent",
            reporter="brand-x",
            incident_type="data_exfiltration",
        )
        after = registry.compute_trust(agent_name="trust-drop-agent")["trust_score"]
        self.assertLess(after, before)

    def test_record_incident_saves_report(self):
        """The incident report is stored in the incident_reports table."""
        registry, db = _make_registry()
        _register(registry, "report-agent")
        registry.record_incident(
            agent_name="report-agent",
            reporter="brand-y",
            incident_type="policy_violation",
            description="Agent accessed restricted endpoint.",
        )
        reports = db.get_incident_reports()
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0]["agent_name"], "report-agent")
        self.assertEqual(reports[0]["reporter"], "brand-y")
        self.assertEqual(reports[0]["incident_type"], "policy_violation")
        self.assertEqual(reports[0]["description"], "Agent accessed restricted endpoint.")

    def test_record_incident_unknown_agent_returns_false(self):
        """Reporting an incident for a non-existent agent returns False."""
        registry, db = _make_registry()
        result = registry.record_incident(
            agent_name="ghost-agent",
            reporter="brand-x",
            incident_type="policy_violation",
        )
        self.assertFalse(result)

    def test_record_incident_emits_event(self):
        """A successful incident report fires INCIDENT_REPORTED on the event bus."""
        registry, db, bus = _make_registry(with_bus=True)
        _register(registry, "event-agent")
        received = []
        bus.subscribe(EventType.INCIDENT_REPORTED, lambda e: received.append(e))
        registry.record_incident(
            agent_name="event-agent",
            reporter="brand-z",
            incident_type="unauthorized_access",
        )
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].event_type, EventType.INCIDENT_REPORTED)
        self.assertEqual(received[0].data["agent_name"], "event-agent")

    def test_record_incident_empty_agent_name_returns_false(self):
        """Empty agent_name is rejected without touching the DB."""
        registry, db = _make_registry()
        result = registry.record_incident(
            agent_name="",
            reporter="brand-x",
            incident_type="policy_violation",
        )
        self.assertFalse(result)

    def test_record_incident_empty_reporter_returns_false(self):
        """Empty reporter is rejected — the credit bureau model requires attribution."""
        registry, db = _make_registry()
        _register(registry, "reject-agent")
        result = registry.record_incident(
            agent_name="reject-agent",
            reporter="",
            incident_type="policy_violation",
        )
        self.assertFalse(result)

    def test_record_incident_empty_type_returns_false(self):
        """Empty incident_type is rejected."""
        registry, db = _make_registry()
        _register(registry, "reject-type-agent")
        result = registry.record_incident(
            agent_name="reject-type-agent",
            reporter="brand-x",
            incident_type="",
        )
        self.assertFalse(result)


# ── TestAgentNameUniqueness ────────────────────────────────────────────────────

class TestAgentNameUniqueness(unittest.TestCase):
    """Agent name uniqueness — one score per entity, credit bureau model."""

    def test_duplicate_name_raises_value_error(self):
        """Registering the same agent name twice raises ValueError."""
        registry, db = _make_registry()
        _register(registry, "bot-1")
        with self.assertRaises(ValueError):
            _register(registry, "bot-1")

    def test_different_names_succeed(self):
        """Two distinct agent names both register successfully."""
        registry, db = _make_registry()
        token_a = _register(registry, "bot-1")
        token_b = _register(registry, "bot-2")
        self.assertIsNotNone(token_a)
        self.assertIsNotNone(token_b)
        self.assertNotEqual(token_a, token_b)
        agents = registry.list_agents()
        names = {a["agent_name"] for a in agents}
        self.assertIn("bot-1", names)
        self.assertIn("bot-2", names)

    def test_deregister_then_reregister_same_name(self):
        """After deregistering, the same name can be registered again."""
        registry, db = _make_registry()
        token = _register(registry, "recycled-bot")
        deregistered = registry.deregister(token)
        self.assertTrue(deregistered)
        # Name should now be free — re-registration must not raise
        new_token = _register(registry, "recycled-bot")
        self.assertIsNotNone(new_token)
        self.assertNotEqual(new_token, token)


# ── TestDatabaseIncidentReports ───────────────────────────────────────────────

class TestDatabaseIncidentReports(unittest.TestCase):
    """database.py incident_reports table — save, retrieve, filter."""

    def _db(self):
        return SubmantleDB(":memory:")

    def _register_agent(self, db, name="db-agent"):
        return db.register_agent(
            agent_name=name,
            version="1.0.0",
            author="DB Tester",
            capabilities=[],
            token_hash=f"hash-{name}",
        )

    def test_save_and_retrieve_incident_report(self):
        """Save a report and verify all fields round-trip correctly."""
        db = self._db()
        agent_id = self._register_agent(db, "agent-alpha")
        db.save_incident_report(
            agent_id=agent_id,
            agent_name="agent-alpha",
            reporter="brand-one",
            incident_type="data_exfiltration",
            description="Sent data to external server.",
        )
        reports = db.get_incident_reports()
        self.assertEqual(len(reports), 1)
        r = reports[0]
        self.assertEqual(r["agent_id"], agent_id)
        self.assertEqual(r["agent_name"], "agent-alpha")
        self.assertEqual(r["reporter"], "brand-one")
        self.assertEqual(r["incident_type"], "data_exfiltration")
        self.assertEqual(r["description"], "Sent data to external server.")
        self.assertIn("id", r)
        self.assertIn("timestamp", r)
        self.assertIsInstance(r["timestamp"], float)

    def test_incident_reports_ordered_newest_first(self):
        """get_incident_reports returns reports newest-first by timestamp."""
        import time
        db = self._db()
        agent_id = self._register_agent(db, "order-agent")
        for i in range(3):
            db.save_incident_report(
                agent_id=agent_id,
                agent_name="order-agent",
                reporter="brand-x",
                incident_type=f"type-{i}",
            )
            time.sleep(0.005)
        reports = db.get_incident_reports(agent_id=agent_id)
        ids = [r["id"] for r in reports]
        self.assertEqual(ids, sorted(ids, reverse=True))

    def test_incident_reports_filter_by_agent_id(self):
        """Filtering by agent_id returns only that agent's reports."""
        db = self._db()
        id_a = self._register_agent(db, "filter-agent-a")
        id_b = self._register_agent(db, "filter-agent-b")
        db.save_incident_report(id_a, "filter-agent-a", "brand-x", "type-1")
        db.save_incident_report(id_a, "filter-agent-a", "brand-x", "type-2")
        db.save_incident_report(id_b, "filter-agent-b", "brand-y", "type-3")

        reports_a = db.get_incident_reports(agent_id=id_a)
        self.assertEqual(len(reports_a), 2)
        self.assertTrue(all(r["agent_id"] == id_a for r in reports_a))

        reports_b = db.get_incident_reports(agent_id=id_b)
        self.assertEqual(len(reports_b), 1)
        self.assertEqual(reports_b[0]["agent_id"], id_b)

    def test_get_agent_by_name(self):
        """Registering via db.register_agent then looking up by name works."""
        db = self._db()
        agent_id = self._register_agent(db, "named-db-agent")
        record = db.get_agent_by_name("named-db-agent")
        self.assertIsNotNone(record)
        self.assertEqual(record["id"], agent_id)
        self.assertEqual(record["agent_name"], "named-db-agent")

    def test_get_agent_by_name_not_found(self):
        """Looking up a name that was never registered returns None."""
        db = self._db()
        result = db.get_agent_by_name("nonexistent-agent")
        self.assertIsNone(result)

    def test_agent_name_unique_index(self):
        """Registering the same agent_name twice raises sqlite3.IntegrityError."""
        db = self._db()
        self._register_agent(db, "unique-agent")
        with self.assertRaises(sqlite3.IntegrityError):
            db.register_agent(
                agent_name="unique-agent",
                version="2.0.0",
                author="Duplicate",
                capabilities=[],
                token_hash="different-hash",
            )


# ── TestIncidentReportedEvent ──────────────────────────────────────────────────

class TestIncidentReportedEvent(unittest.TestCase):
    """INCIDENT_REPORTED event passes through in PRIVATE mode."""

    def test_incident_reported_passes_through_in_private(self):
        """INCIDENT_REPORTED is not a process event — it fires even in PRIVATE mode."""
        db = SubmantleDB(":memory:")
        bus = EventBus()
        bus.set_privacy_mode(True)
        registry = AgentRegistry(db=db, event_bus=bus)

        registry.register("private-mode-agent", "1.0.0", "Tester", [])
        received = []
        bus.subscribe(EventType.INCIDENT_REPORTED, lambda e: received.append(e))

        result = registry.record_incident(
            agent_name="private-mode-agent",
            reporter="brand-private",
            incident_type="policy_violation",
        )

        self.assertTrue(result)
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].event_type, EventType.INCIDENT_REPORTED)


# ── TestWave1TrustMetadata ─────────────────────────────────────────────────────

class TestWave1TrustMetadata(unittest.TestCase):
    """Wave 1 enrichment fields: score_version, has_history, reporter_diversity."""

    def test_score_version_present(self):
        """New agent's compute_trust result includes score_version = 'v1.0'."""
        registry, db = _make_registry()
        _register(registry, "version-agent")
        result = registry.compute_trust(agent_name="version-agent")
        self.assertIsNotNone(result)
        self.assertEqual(result["score_version"], "v1.0")

    def test_has_history_false_for_new_agent(self):
        """Brand new agent with zero queries has has_history = False."""
        registry, db = _make_registry()
        _register(registry, "no-history-agent")
        result = registry.compute_trust(agent_name="no-history-agent")
        self.assertIsNotNone(result)
        self.assertFalse(result["has_history"])

    def test_has_history_true_after_queries(self):
        """After recording at least one query, has_history = True."""
        registry, db = _make_registry()
        token = _register(registry, "history-agent")
        registry.record_query(token)
        result = registry.compute_trust(agent_name="history-agent")
        self.assertIsNotNone(result)
        self.assertTrue(result["has_history"])

    def test_reporter_diversity_zero_for_clean_agent(self):
        """Agent with no incidents has reporter_diversity = 0."""
        registry, db = _make_registry()
        _register(registry, "clean-agent")
        result = registry.compute_trust(agent_name="clean-agent")
        self.assertIsNotNone(result)
        self.assertEqual(result["reporter_diversity"], 0)

    def test_reporter_diversity_counts_distinct_reporters(self):
        """Same reporter filing twice = 1. Two different reporters = 2."""
        registry, db = _make_registry()
        _register(registry, "diversity-agent")

        # Same reporter files twice — should count as 1
        registry.record_incident(
            agent_name="diversity-agent",
            reporter="brand-alpha",
            incident_type="policy_violation",
        )
        registry.record_incident(
            agent_name="diversity-agent",
            reporter="brand-alpha",
            incident_type="data_exfiltration",
        )
        result = registry.compute_trust(agent_name="diversity-agent")
        self.assertEqual(result["reporter_diversity"], 1)

        # Second distinct reporter — should now count as 2
        registry.record_incident(
            agent_name="diversity-agent",
            reporter="brand-beta",
            incident_type="policy_violation",
        )
        result = registry.compute_trust(agent_name="diversity-agent")
        self.assertEqual(result["reporter_diversity"], 2)

    def test_compute_trust_returns_wave1_fields(self):
        """compute_trust result contains all expected keys including Wave 1 fields."""
        registry, db = _make_registry()
        _register(registry, "wave1-agent", version="3.0.0", author="Wave Corp")
        result = registry.compute_trust(agent_name="wave1-agent")
        self.assertIsNotNone(result)
        required_keys = {
            "agent_name", "trust_score", "total_queries", "incidents",
            "registration_time", "last_seen", "version", "author",
            "score_version", "has_history", "reporter_diversity",
        }
        self.assertEqual(required_keys, set(result.keys()))
        self.assertEqual(result["score_version"], "v1.0")
        self.assertIsInstance(result["has_history"], bool)
        self.assertIsInstance(result["reporter_diversity"], int)


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
