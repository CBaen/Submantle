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
        # Use different reporters so neither is a duplicate
        registry.record_incident(
            agent_name="formula-agent",
            reporter="acme-brand",
            incident_type="policy_violation",
        )
        registry.record_incident(
            agent_name="formula-agent",
            reporter="other-brand",
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

    def test_deregister_then_reregister_same_name_rejected(self):
        """After deregistering, the same name CANNOT be registered again — permanent record."""
        registry, db = _make_registry()
        token = _register(registry, "recycled-bot")
        deregistered = registry.deregister(token)
        self.assertTrue(deregistered)
        # Name is permanently reserved — re-registration must raise
        with self.assertRaises(ValueError) as ctx:
            _register(registry, "recycled-bot")
        self.assertIn("permanent", str(ctx.exception).lower())


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
        """compute_trust result contains all expected keys including Wave 1 and Wave 2 fields."""
        registry, db = _make_registry()
        _register(registry, "wave1-agent", version="3.0.0", author="Wave Corp")
        result = registry.compute_trust(agent_name="wave1-agent")
        self.assertIsNotNone(result)
        required_keys = {
            "agent_name", "trust_score", "total_queries", "incidents",
            "registration_time", "last_seen", "version", "author",
            "score_version", "has_history", "reporter_diversity", "is_active",
        }
        self.assertEqual(required_keys, set(result.keys()))
        self.assertEqual(result["score_version"], "v1.0")
        self.assertIsInstance(result["has_history"], bool)
        self.assertIsInstance(result["reporter_diversity"], int)


# ── TestWave2SoftDelete ────────────────────────────────────────────────────────

class TestWave2SoftDelete(unittest.TestCase):
    """Wave 2: Soft-delete deregistration — permanent records, credit bureau model."""

    def test_deregister_is_soft_delete(self):
        """After deregistering, agent still exists in DB with deregistered_at set."""
        registry, db = _make_registry()
        token = _register(registry, "soft-deleted-agent")
        registry.deregister(token)
        record = db.get_agent_by_name("soft-deleted-agent")
        self.assertIsNotNone(record)
        self.assertIsNotNone(record["deregistered_at"])
        self.assertIsInstance(record["deregistered_at"], float)

    def test_deregistered_agent_excluded_from_active_list(self):
        """list_agents(active_only=True) excludes deregistered; active_only=False includes."""
        registry, db = _make_registry()
        token = _register(registry, "gone-agent")
        _register(registry, "still-here-agent")
        registry.deregister(token)

        active = registry.list_agents(active_only=True)
        active_names = {a["agent_name"] for a in active}
        self.assertNotIn("gone-agent", active_names)
        self.assertIn("still-here-agent", active_names)

        all_agents = registry.list_agents(active_only=False)
        all_names = {a["agent_name"] for a in all_agents}
        self.assertIn("gone-agent", all_names)
        self.assertIn("still-here-agent", all_names)

    def test_deregistered_agent_trust_still_queryable(self):
        """compute_trust() still returns score for deregistered agent with is_active=False."""
        registry, db = _make_registry()
        token = _register(registry, "scored-gone-agent")
        registry.deregister(token)
        result = registry.compute_trust(agent_name="scored-gone-agent")
        self.assertIsNotNone(result)
        self.assertFalse(result["is_active"])
        self.assertIn("trust_score", result)

    def test_deregistered_agent_token_invalidated(self):
        """verify() returns None for a deregistered agent's token."""
        registry, db = _make_registry()
        token = _register(registry, "invalid-token-agent")
        registry.deregister(token)
        result = registry.verify(token)
        self.assertIsNone(result)

    def test_deregistered_agent_queries_rejected(self):
        """record_query() returns False for a deregistered agent's token."""
        registry, db = _make_registry()
        token = _register(registry, "no-query-agent")
        registry.deregister(token)
        result = registry.record_query(token)
        self.assertFalse(result)

    def test_is_active_true_for_active_agent(self):
        """compute_trust() returns is_active=True for an agent that is still active."""
        registry, db = _make_registry()
        _register(registry, "active-agent")
        result = registry.compute_trust(agent_name="active-agent")
        self.assertIsNotNone(result)
        self.assertTrue(result["is_active"])

    def test_verify_directory_includes_deregistered(self):
        """list_agents(active_only=False) includes deregistered agents in the public record."""
        registry, db = _make_registry()
        token = _register(registry, "public-record-agent")
        registry.deregister(token)
        all_agents = registry.list_agents(active_only=False)
        all_names = {a["agent_name"] for a in all_agents}
        self.assertIn("public-record-agent", all_names)


# ── TestWave3IncidentPipeline ──────────────────────────────────────────────────

class TestWave3IncidentPipeline(unittest.TestCase):
    """Wave 3: Pending state, severity classification, and deduplication."""

    def test_self_ping_auto_rejected(self):
        """Reporter == agent_name → incident auto-rejected, counter NOT incremented."""
        registry, db = _make_registry()
        _register(registry, "self-ping-agent")
        result = registry.record_incident(
            agent_name="self-ping-agent",
            reporter="self-ping-agent",
            incident_type="policy_violation",
        )
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reason"], "self-ping")
        record = db.get_agent_by_name("self-ping-agent")
        self.assertEqual(record["incidents"], 0)

    def test_self_ping_case_insensitive(self):
        """Self-ping detection is case-insensitive."""
        registry, db = _make_registry()
        _register(registry, "CasedAgent")
        result = registry.record_incident(
            agent_name="CasedAgent",
            reporter="casedagent",
            incident_type="policy_violation",
        )
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "rejected")

    def test_duplicate_detection(self):
        """Same reporter + agent + type within 24h → duplicate."""
        registry, db = _make_registry()
        _register(registry, "dup-agent")
        result1 = registry.record_incident(
            agent_name="dup-agent",
            reporter="brand-x",
            incident_type="policy_violation",
        )
        self.assertIsInstance(result1, dict)
        self.assertEqual(result1["status"], "accepted")
        result2 = registry.record_incident(
            agent_name="dup-agent",
            reporter="brand-x",
            incident_type="policy_violation",
        )
        self.assertIsInstance(result2, dict)
        self.assertEqual(result2["status"], "duplicate")
        self.assertIn("duplicate_of", result2)

    def test_duplicate_does_not_increment_counter(self):
        """Duplicate incidents don't affect the incident counter."""
        registry, db = _make_registry()
        _register(registry, "dup-count-agent")
        registry.record_incident("dup-count-agent", "brand-x", "type-a")
        registry.record_incident("dup-count-agent", "brand-x", "type-a")  # duplicate
        record = db.get_agent_by_name("dup-count-agent")
        self.assertEqual(record["incidents"], 1)

    def test_different_type_not_duplicate(self):
        """Same reporter + agent but different type → NOT duplicate."""
        registry, db = _make_registry()
        _register(registry, "diff-type-agent")
        result1 = registry.record_incident("diff-type-agent", "brand-x", "type-a")
        result2 = registry.record_incident("diff-type-agent", "brand-x", "type-b")
        self.assertEqual(result1["status"], "accepted")
        self.assertEqual(result2["status"], "accepted")
        record = db.get_agent_by_name("diff-type-agent")
        self.assertEqual(record["incidents"], 2)

    def test_different_reporter_not_duplicate(self):
        """Same agent + type but different reporter → NOT duplicate."""
        registry, db = _make_registry()
        _register(registry, "diff-reporter-agent")
        result1 = registry.record_incident("diff-reporter-agent", "brand-x", "type-a")
        result2 = registry.record_incident("diff-reporter-agent", "brand-y", "type-a")
        self.assertEqual(result1["status"], "accepted")
        self.assertEqual(result2["status"], "accepted")

    def test_accepted_incident_increments_counter(self):
        """Standard accepted incidents still increment the counter."""
        registry, db = _make_registry()
        _register(registry, "accept-agent")
        registry.record_incident("accept-agent", "brand-x", "type-a")
        record = db.get_agent_by_name("accept-agent")
        self.assertEqual(record["incidents"], 1)

    def test_incident_status_in_report(self):
        """Saved incident report includes status field."""
        registry, db = _make_registry()
        _register(registry, "status-agent")
        registry.record_incident("status-agent", "brand-x", "type-a")
        reports = db.get_incident_reports()
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0]["status"], "accepted")

    def test_severity_defaults_to_standard(self):
        """Severity defaults to 'standard' when not specified."""
        registry, db = _make_registry()
        _register(registry, "sev-agent")
        registry.record_incident("sev-agent", "brand-x", "type-a")
        reports = db.get_incident_reports()
        self.assertEqual(reports[0]["severity"], "standard")

    def test_severity_critical_passed_through(self):
        """Severity 'critical' is stored correctly."""
        registry, db = _make_registry()
        _register(registry, "crit-agent")
        registry.record_incident("crit-agent", "brand-x", "type-a", severity="critical")
        reports = db.get_incident_reports()
        self.assertEqual(reports[0]["severity"], "critical")

    def test_rejected_incident_stored_for_audit(self):
        """Rejected self-ping incidents are still stored in the database."""
        registry, db = _make_registry()
        _register(registry, "audit-agent")
        registry.record_incident("audit-agent", "audit-agent", "type-a")
        reports = db.get_incident_reports()
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0]["status"], "rejected")

    def test_review_incident_accept(self):
        """review_incident() can accept a pending incident and increment counter."""
        registry, db = _make_registry()
        _register(registry, "review-agent")
        agent = db.get_agent_by_name("review-agent")
        incident_id = db.save_incident_report(
            agent_id=agent["id"],
            agent_name="review-agent",
            reporter="brand-x",
            incident_type="type-a",
            status="pending",
        )
        result = registry.review_incident(incident_id, "accepted")
        self.assertTrue(result)
        record = db.get_agent_by_name("review-agent")
        self.assertEqual(record["incidents"], 1)
        reports = db.get_incident_reports(agent_id=agent["id"])
        accepted = [r for r in reports if r["id"] == incident_id]
        self.assertEqual(accepted[0]["status"], "accepted")
        self.assertIsNotNone(accepted[0]["reviewed_at"])

    def test_review_incident_reject(self):
        """review_incident() can reject a pending incident without incrementing counter."""
        registry, db = _make_registry()
        _register(registry, "reject-review-agent")
        agent = db.get_agent_by_name("reject-review-agent")
        incident_id = db.save_incident_report(
            agent_id=agent["id"],
            agent_name="reject-review-agent",
            reporter="brand-x",
            incident_type="type-a",
            status="pending",
        )
        result = registry.review_incident(incident_id, "rejected")
        self.assertTrue(result)
        record = db.get_agent_by_name("reject-review-agent")
        self.assertEqual(record["incidents"], 0)


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
