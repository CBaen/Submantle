"""
Tests for prototype/agent_registry.py

All tests are self-contained. DB and EventBus dependencies are mocked inline —
no dependency on Builder A's actual database.py or events.py.

Run:
    cd prototype && python -m pytest tests/test_agent_registry.py -v
    # or without pytest:
    cd prototype && python tests/test_agent_registry.py
"""

import hashlib
import hmac
import json
import secrets
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, call, patch

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_registry import AgentRegistry, _now_iso, _token_hash, _SECRET_SETTING_KEY


# ── Mock DB helpers ────────────────────────────────────────────────────────────

class MockDB:
    """
    In-memory mock of SubstrateDB that faithfully implements the agent registry
    interface. Cleaner than MagicMock for stateful behaviour.
    """

    def __init__(self, existing_secret: str | None = None):
        self._settings: dict[str, str] = {}
        self._agents: dict[int, dict] = {}  # agent_id -> record
        self._next_id = 1

        if existing_secret is not None:
            self._settings[_SECRET_SETTING_KEY] = existing_secret

    # Settings
    def get_setting(self, key: str) -> str | None:
        return self._settings.get(key)

    def set_setting(self, key: str, value: str) -> None:
        self._settings[key] = value

    # Agent operations
    def register_agent(
        self, agent_name, version, author, capabilities, token_hash,
        registration_time: str | None = None
    ) -> int:
        agent_id = self._next_id
        self._next_id += 1
        self._agents[agent_id] = {
            "id": agent_id,
            "agent_name": agent_name,
            "version": version,
            "author": author,
            "capabilities": capabilities,
            "token_hash": token_hash,
            # Use the registry-supplied timestamp so HMAC re-derivation at
            # verify time uses the same value that was used to build the token.
            "registration_time": registration_time if registration_time is not None else _now_iso(),
            "last_seen": None,
            "total_queries": 0,
            "incidents": 0,
            "trust_metadata": None,
        }
        return agent_id

    def get_agent_by_token_hash(self, token_hash: str) -> dict | None:
        for record in self._agents.values():
            if record["token_hash"] == token_hash:
                return dict(record)
        return None

    def list_agents(self) -> list[dict]:
        return [dict(r) for r in self._agents.values()]

    def delete_agent(self, agent_id: int) -> bool:
        if agent_id in self._agents:
            del self._agents[agent_id]
            return True
        return False

    def update_agent_last_seen(self, agent_id: int) -> None:
        if agent_id in self._agents:
            self._agents[agent_id]["last_seen"] = _now_iso()

    def increment_agent_queries(self, agent_id: int) -> None:
        if agent_id in self._agents:
            self._agents[agent_id]["total_queries"] += 1


def _make_event_bus() -> MagicMock:
    return MagicMock()


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestAgentRegistryInit(unittest.TestCase):
    """Initialisation and secret management."""

    def test_creates_secret_when_no_db(self):
        registry = AgentRegistry()
        # Secret should be a 32-byte value
        self.assertEqual(len(registry._secret), 32)

    def test_creates_and_persists_new_secret(self):
        db = MockDB()
        registry = AgentRegistry(db=db)
        stored = db.get_setting(_SECRET_SETTING_KEY)
        self.assertIsNotNone(stored)
        # Stored as hex: 32 bytes = 64 hex chars
        self.assertEqual(len(stored), 64)

    def test_loads_existing_secret(self):
        existing_secret = secrets.token_bytes(32)
        db = MockDB(existing_secret=existing_secret.hex())
        registry = AgentRegistry(db=db)
        self.assertEqual(registry._secret, existing_secret)

    def test_secret_consistent_across_instances_with_same_db(self):
        """Two registries sharing a DB should use the same secret."""
        db = MockDB()
        r1 = AgentRegistry(db=db)
        r2 = AgentRegistry(db=db)
        self.assertEqual(r1._secret, r2._secret)

    def test_init_survives_db_get_failure(self):
        db = MagicMock()
        db.get_setting.side_effect = Exception("DB unavailable")
        db.set_setting.side_effect = Exception("DB unavailable")
        registry = AgentRegistry(db=db)
        # Should have generated an ephemeral secret
        self.assertIsNotNone(registry._secret)
        self.assertEqual(len(registry._secret), 32)


class TestTokenHelpers(unittest.TestCase):
    """Token construction and hashing utilities."""

    def test_token_hash_is_sha256(self):
        token = "test-token"
        expected = hashlib.sha256(token.encode()).hexdigest()
        self.assertEqual(_token_hash(token), expected)

    def test_token_hash_is_hex_64_chars(self):
        self.assertEqual(len(_token_hash("anything")), 64)

    def test_make_token_produces_hex_64_chars(self):
        registry = AgentRegistry()
        token = registry._make_token("my-agent", "2026-01-01T00:00:00+00:00")
        self.assertEqual(len(token), 64)

    def test_same_inputs_produce_same_token(self):
        registry = AgentRegistry()
        ts = "2026-01-01T00:00:00+00:00"
        t1 = registry._make_token("agent-a", ts)
        t2 = registry._make_token("agent-a", ts)
        self.assertEqual(t1, t2)

    def test_different_names_produce_different_tokens(self):
        registry = AgentRegistry()
        ts = "2026-01-01T00:00:00+00:00"
        t1 = registry._make_token("agent-a", ts)
        t2 = registry._make_token("agent-b", ts)
        self.assertNotEqual(t1, t2)

    def test_name_timestamp_separator_prevents_collision(self):
        """
        Without the ":" separator, "foo" + "bar:ts" == "foobar" + ":ts".
        With it: "foo:bar:ts" != "foobar::ts".
        """
        registry = AgentRegistry()
        t1 = registry._make_token("foo", "bar:ts")
        t2 = registry._make_token("foobar", ":ts")
        self.assertNotEqual(t1, t2)

    def test_different_secrets_produce_different_tokens(self):
        r1 = AgentRegistry(db=MockDB())
        r2 = AgentRegistry(db=MockDB())
        ts = "2026-01-01T00:00:00+00:00"
        # With overwhelming probability, two fresh secrets differ
        t1 = r1._make_token("agent-a", ts)
        t2 = r2._make_token("agent-a", ts)
        self.assertNotEqual(t1, t2)


class TestRegister(unittest.TestCase):
    """register() method."""

    def _registry(self):
        return AgentRegistry(db=MockDB())

    def test_register_returns_hex_token(self):
        registry = self._registry()
        token = registry.register("my-agent", "1.0.0", "Alice", ["query"])
        self.assertIsInstance(token, str)
        self.assertEqual(len(token), 64)

    def test_register_persists_to_db(self):
        db = MockDB()
        registry = AgentRegistry(db=db)
        registry.register("my-agent", "1.0.0", "Alice", ["query"])
        agents = db.list_agents()
        self.assertEqual(len(agents), 1)
        self.assertEqual(agents[0]["agent_name"], "my-agent")

    def test_register_stores_token_hash_not_raw_token(self):
        db = MockDB()
        registry = AgentRegistry(db=db)
        token = registry.register("my-agent", "1.0.0", "Alice", ["query"])
        agents = db.list_agents()
        stored_hash = agents[0]["token_hash"]
        # Token hash should NOT equal the token
        self.assertNotEqual(stored_hash, token)
        # But it should equal sha256(token)
        self.assertEqual(stored_hash, _token_hash(token))

    def test_register_strips_whitespace_from_name(self):
        db = MockDB()
        registry = AgentRegistry(db=db)
        registry.register("  spaced-name  ", "1.0.0", "Alice", [])
        agents = db.list_agents()
        self.assertEqual(agents[0]["agent_name"], "spaced-name")

    def test_register_empty_capabilities_ok(self):
        registry = self._registry()
        token = registry.register("my-agent", "1.0.0", "Alice", [])
        self.assertIsNotNone(token)

    def test_register_raises_on_empty_name(self):
        registry = self._registry()
        with self.assertRaises(ValueError):
            registry.register("", "1.0.0", "Alice", [])

    def test_register_raises_on_whitespace_name(self):
        registry = self._registry()
        with self.assertRaises(ValueError):
            registry.register("   ", "1.0.0", "Alice", [])

    def test_register_raises_on_empty_version(self):
        registry = self._registry()
        with self.assertRaises(ValueError):
            registry.register("my-agent", "", "Alice", [])

    def test_register_raises_on_empty_author(self):
        registry = self._registry()
        with self.assertRaises(ValueError):
            registry.register("my-agent", "1.0.0", "", [])

    def test_register_raises_on_non_list_capabilities(self):
        registry = self._registry()
        with self.assertRaises(ValueError):
            registry.register("my-agent", "1.0.0", "Alice", "query")

    def test_register_emits_agent_registered_event(self):
        bus = _make_event_bus()
        registry = AgentRegistry(db=MockDB(), event_bus=bus)
        registry.register("my-agent", "1.0.0", "Alice", ["query"])
        bus.emit.assert_called_once()
        args = bus.emit.call_args[0]
        self.assertEqual(args[0], "AGENT_REGISTERED")
        self.assertEqual(args[1]["agent_name"], "my-agent")

    def test_register_raises_on_db_failure(self):
        db = MagicMock()
        db.get_setting.return_value = None
        db.set_setting.return_value = None
        db.register_agent.side_effect = Exception("disk full")
        registry = AgentRegistry(db=db)
        with self.assertRaises(RuntimeError):
            registry.register("my-agent", "1.0.0", "Alice", [])


class TestVerify(unittest.TestCase):
    """verify() method."""

    def test_verify_valid_token_returns_agent_info(self):
        db = MockDB()
        registry = AgentRegistry(db=db)
        token = registry.register("my-agent", "1.0.0", "Alice", ["query"])
        result = registry.verify(token)
        self.assertIsNotNone(result)
        self.assertEqual(result["agent_name"], "my-agent")

    def test_verify_invalid_token_returns_none(self):
        db = MockDB()
        registry = AgentRegistry(db=db)
        registry.register("my-agent", "1.0.0", "Alice", ["query"])
        result = registry.verify("deadbeef" * 8)  # 64 char fake token
        self.assertIsNone(result)

    def test_verify_empty_token_returns_none(self):
        registry = AgentRegistry(db=MockDB())
        self.assertIsNone(registry.verify(""))
        self.assertIsNone(registry.verify(None))

    def test_verify_returns_none_without_db(self):
        registry = AgentRegistry()
        self.assertIsNone(registry.verify("any-token"))

    def test_verify_after_deregister_returns_none(self):
        db = MockDB()
        registry = AgentRegistry(db=db)
        token = registry.register("my-agent", "1.0.0", "Alice", [])
        registry.deregister(token)
        self.assertIsNone(registry.verify(token))

    def test_verify_detects_forged_token_with_matching_hash_prefix(self):
        """
        Constructed attack: token hash stored correctly but token itself is different.
        Practically impossible with HMAC but the logic path should reject it.
        This tests the _verify_token_against_record branch.
        """
        db = MockDB()
        registry = AgentRegistry(db=db)
        token = registry.register("my-agent", "1.0.0", "Alice", [])

        # Manually tamper: store a record with a matching token_hash but
        # different registration_time so re-derivation will fail.
        agents = db.list_agents()
        agent_id = agents[0]["id"]
        # Change the registration_time in the record to break re-derivation
        db._agents[agent_id]["registration_time"] = "tampered-timestamp"

        result = registry.verify(token)
        self.assertIsNone(result)

    def test_verify_db_error_returns_none(self):
        db = MagicMock()
        db.get_setting.return_value = None
        db.set_setting.return_value = None
        db.get_agent_by_token_hash.side_effect = Exception("DB gone")
        registry = AgentRegistry(db=db)
        result = registry.verify("some-token")
        self.assertIsNone(result)


class TestListAgents(unittest.TestCase):
    """list_agents() method."""

    def test_empty_registry_returns_empty_list(self):
        registry = AgentRegistry(db=MockDB())
        self.assertEqual(registry.list_agents(), [])

    def test_returns_all_registered_agents(self):
        db = MockDB()
        registry = AgentRegistry(db=db)
        registry.register("agent-a", "1.0.0", "Alice", [])
        registry.register("agent-b", "2.0.0", "Bob", ["query"])
        agents = registry.list_agents()
        self.assertEqual(len(agents), 2)
        names = {a["agent_name"] for a in agents}
        self.assertIn("agent-a", names)
        self.assertIn("agent-b", names)

    def test_token_hash_not_in_list_output(self):
        """list_agents() must not expose token hashes."""
        db = MockDB()
        registry = AgentRegistry(db=db)
        registry.register("my-agent", "1.0.0", "Alice", [])
        agents = registry.list_agents()
        self.assertNotIn("token_hash", agents[0])

    def test_returns_empty_without_db(self):
        registry = AgentRegistry()
        self.assertEqual(registry.list_agents(), [])

    def test_db_error_returns_empty(self):
        db = MagicMock()
        db.get_setting.return_value = None
        db.set_setting.return_value = None
        db.list_agents.side_effect = Exception("DB gone")
        registry = AgentRegistry(db=db)
        result = registry.list_agents()
        self.assertEqual(result, [])


class TestDeregister(unittest.TestCase):
    """deregister() method."""

    def test_deregister_valid_token_returns_true(self):
        db = MockDB()
        registry = AgentRegistry(db=db)
        token = registry.register("my-agent", "1.0.0", "Alice", [])
        result = registry.deregister(token)
        self.assertTrue(result)

    def test_deregister_removes_from_db(self):
        db = MockDB()
        registry = AgentRegistry(db=db)
        token = registry.register("my-agent", "1.0.0", "Alice", [])
        registry.deregister(token)
        self.assertEqual(db.list_agents(), [])

    def test_deregister_invalid_token_returns_false(self):
        db = MockDB()
        registry = AgentRegistry(db=db)
        result = registry.deregister("not-a-real-token")
        self.assertFalse(result)

    def test_deregister_empty_token_returns_false(self):
        registry = AgentRegistry(db=MockDB())
        self.assertFalse(registry.deregister(""))

    def test_deregister_emits_event(self):
        bus = _make_event_bus()
        db = MockDB()
        registry = AgentRegistry(db=db, event_bus=bus)
        token = registry.register("my-agent", "1.0.0", "Alice", [])
        bus.reset_mock()
        registry.deregister(token)
        bus.emit.assert_called_once()
        args = bus.emit.call_args[0]
        self.assertEqual(args[0], "AGENT_DEREGISTERED")
        self.assertEqual(args[1]["agent_name"], "my-agent")

    def test_double_deregister_second_returns_false(self):
        db = MockDB()
        registry = AgentRegistry(db=db)
        token = registry.register("my-agent", "1.0.0", "Alice", [])
        registry.deregister(token)
        result = registry.deregister(token)
        self.assertFalse(result)


class TestRecordQuery(unittest.TestCase):
    """record_query() method."""

    def test_record_query_returns_true_for_valid_token(self):
        db = MockDB()
        registry = AgentRegistry(db=db)
        token = registry.register("my-agent", "1.0.0", "Alice", [])
        result = registry.record_query(token)
        self.assertTrue(result)

    def test_record_query_increments_total_queries(self):
        db = MockDB()
        registry = AgentRegistry(db=db)
        token = registry.register("my-agent", "1.0.0", "Alice", [])
        registry.record_query(token)
        registry.record_query(token)
        registry.record_query(token)
        agents = db.list_agents()
        self.assertEqual(agents[0]["total_queries"], 3)

    def test_record_query_updates_last_seen(self):
        db = MockDB()
        registry = AgentRegistry(db=db)
        token = registry.register("my-agent", "1.0.0", "Alice", [])
        # Initially last_seen is None
        agents_before = db.list_agents()
        self.assertIsNone(agents_before[0]["last_seen"])
        registry.record_query(token)
        agents_after = db.list_agents()
        self.assertIsNotNone(agents_after[0]["last_seen"])

    def test_record_query_returns_false_for_invalid_token(self):
        registry = AgentRegistry(db=MockDB())
        result = registry.record_query("invalid-token")
        self.assertFalse(result)

    def test_record_query_db_error_does_not_raise(self):
        """DB write failure on stats update must not crash the caller."""
        db = MagicMock()
        existing_secret = secrets.token_bytes(32)
        db.get_setting.return_value = existing_secret.hex()
        db.set_setting.return_value = None

        # Need verify to work — provide a real record lookup
        mock_db = MockDB(existing_secret=existing_secret.hex())
        registry = AgentRegistry(db=mock_db)
        token = registry.register("my-agent", "1.0.0", "Alice", [])

        # Now simulate DB failure on stats operations
        original_update = mock_db.update_agent_last_seen
        mock_db.update_agent_last_seen = MagicMock(side_effect=Exception("DB error"))
        mock_db.increment_agent_queries = MagicMock(side_effect=Exception("DB error"))

        result = registry.record_query(token)  # should not raise
        self.assertTrue(result)


class TestAgentRegistryPrivacyModeCompatibility(unittest.TestCase):
    """
    Agent registry must work regardless of privacy mode.
    These tests verify the registry's own operations are not
    gated on privacy — that's the caller's (api.py) responsibility.
    """

    def test_register_works_without_privacy_manager(self):
        registry = AgentRegistry(db=MockDB())
        token = registry.register("my-agent", "1.0.0", "Alice", [])
        self.assertIsNotNone(token)

    def test_verify_works_independently(self):
        db = MockDB()
        registry = AgentRegistry(db=db)
        token = registry.register("my-agent", "1.0.0", "Alice", [])
        result = registry.verify(token)
        self.assertIsNotNone(result)

    def test_list_agents_works_independently(self):
        db = MockDB()
        registry = AgentRegistry(db=db)
        registry.register("my-agent", "1.0.0", "Alice", [])
        agents = registry.list_agents()
        self.assertEqual(len(agents), 1)


class TestAgentRegistryRepr(unittest.TestCase):
    def test_repr(self):
        registry = AgentRegistry()
        self.assertIn("AgentRegistry", repr(registry))


# ── Entry point for running without pytest ────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
