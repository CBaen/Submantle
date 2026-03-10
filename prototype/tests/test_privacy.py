"""
Tests for prototype/privacy.py

All tests are self-contained. DB and EventBus dependencies are mocked inline —
no dependency on Builder A's actual database.py or events.py.

Run:
    cd prototype && python -m pytest tests/test_privacy.py -v
    # or without pytest:
    cd prototype && python tests/test_privacy.py
"""

import threading
import unittest
from unittest.mock import MagicMock, call

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from privacy import PrivacyManager, PrivacyState, _SETTING_KEY


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_db(initial_state: str | None = None) -> MagicMock:
    """Create a mock DB with get_setting/set_setting behaviour."""
    db = MagicMock()
    _store = {}
    if initial_state is not None:
        _store[_SETTING_KEY] = initial_state

    def get_setting(key):
        return _store.get(key)

    def set_setting(key, value):
        _store[key] = value

    db.get_setting.side_effect = get_setting
    db.set_setting.side_effect = set_setting
    return db


def _make_event_bus() -> MagicMock:
    return MagicMock()


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestPrivacyManagerInit(unittest.TestCase):
    """Initialisation and default state."""

    def test_defaults_to_aware_without_db(self):
        pm = PrivacyManager()
        self.assertEqual(pm.state, PrivacyState.AWARE)

    def test_defaults_to_aware_when_setting_absent(self):
        db = _make_db(initial_state=None)
        pm = PrivacyManager(db=db)
        self.assertEqual(pm.state, PrivacyState.AWARE)

    def test_loads_aware_state_from_db(self):
        db = _make_db(initial_state="AWARE")
        pm = PrivacyManager(db=db)
        self.assertEqual(pm.state, PrivacyState.AWARE)

    def test_loads_private_state_from_db(self):
        db = _make_db(initial_state="PRIVATE")
        pm = PrivacyManager(db=db)
        self.assertEqual(pm.state, PrivacyState.PRIVATE)

    def test_defaults_to_aware_when_db_raises(self):
        db = MagicMock()
        db.get_setting.side_effect = Exception("DB connection failed")
        pm = PrivacyManager(db=db)
        self.assertEqual(pm.state, PrivacyState.AWARE)


class TestPrivacyManagerStatePredicates(unittest.TestCase):
    """is_private(), is_aware(), check_privacy()."""

    def test_is_aware_in_aware_mode(self):
        pm = PrivacyManager()
        self.assertTrue(pm.is_aware())
        self.assertFalse(pm.is_private())

    def test_check_privacy_returns_false_when_aware(self):
        """check_privacy() returns False → caller should PROCEED."""
        pm = PrivacyManager()
        self.assertFalse(pm.check_privacy())

    def test_check_privacy_returns_true_when_private(self):
        """check_privacy() returns True → caller should SKIP."""
        db = _make_db(initial_state="PRIVATE")
        pm = PrivacyManager(db=db)
        self.assertTrue(pm.check_privacy())

    def test_is_private_after_set_private(self):
        pm = PrivacyManager()
        pm.set_private()
        self.assertTrue(pm.is_private())
        self.assertFalse(pm.is_aware())


class TestPrivacyManagerTransitions(unittest.TestCase):
    """State transitions and return values."""

    def test_set_private_returns_correct_dict(self):
        pm = PrivacyManager()
        result = pm.set_private()
        self.assertEqual(result["previous_state"], "AWARE")
        self.assertEqual(result["new_state"], "PRIVATE")
        self.assertTrue(result["changed"])

    def test_set_aware_returns_correct_dict(self):
        db = _make_db(initial_state="PRIVATE")
        pm = PrivacyManager(db=db)
        result = pm.set_aware()
        self.assertEqual(result["previous_state"], "PRIVATE")
        self.assertEqual(result["new_state"], "AWARE")
        self.assertTrue(result["changed"])

    def test_set_private_idempotent(self):
        """Calling set_private when already PRIVATE should be safe and return changed=False."""
        db = _make_db(initial_state="PRIVATE")
        pm = PrivacyManager(db=db)
        result = pm.set_private()
        self.assertFalse(result["changed"])
        self.assertEqual(result["previous_state"], "PRIVATE")
        self.assertEqual(result["new_state"], "PRIVATE")

    def test_toggle_aware_to_private(self):
        pm = PrivacyManager()
        result = pm.toggle()
        self.assertEqual(result["new_state"], "PRIVATE")
        self.assertTrue(result["changed"])

    def test_toggle_private_to_aware(self):
        db = _make_db(initial_state="PRIVATE")
        pm = PrivacyManager(db=db)
        result = pm.toggle()
        self.assertEqual(result["new_state"], "AWARE")
        self.assertTrue(result["changed"])

    def test_double_toggle_returns_to_original_state(self):
        pm = PrivacyManager()
        pm.toggle()
        pm.toggle()
        self.assertTrue(pm.is_aware())


class TestPrivacyManagerPersistence(unittest.TestCase):
    """Persistence to DB settings table."""

    def test_persists_private_on_set_private(self):
        db = _make_db()
        pm = PrivacyManager(db=db)
        pm.set_private()
        # get_setting should now return PRIVATE
        self.assertEqual(db.get_setting(_SETTING_KEY), "PRIVATE")

    def test_persists_aware_on_set_aware(self):
        db = _make_db(initial_state="PRIVATE")
        pm = PrivacyManager(db=db)
        pm.set_aware()
        self.assertEqual(db.get_setting(_SETTING_KEY), "AWARE")

    def test_no_persist_when_db_none(self):
        """No DB — transitions still work, just without persistence."""
        pm = PrivacyManager(db=None)
        pm.set_private()
        self.assertTrue(pm.is_private())

    def test_persist_failure_does_not_raise(self):
        """If DB write fails, the state change still takes effect in memory."""
        db = MagicMock()
        db.get_setting.return_value = None
        db.set_setting.side_effect = Exception("disk full")
        pm = PrivacyManager(db=db)
        pm.set_private()  # should not raise
        self.assertTrue(pm.is_private())  # state changed in memory


class TestPrivacyManagerEvents(unittest.TestCase):
    """Event bus integration."""

    def test_emits_privacy_toggled_on_set_private(self):
        bus = _make_event_bus()
        pm = PrivacyManager(event_bus=bus)
        pm.set_private()
        bus.emit.assert_called_once()
        args = bus.emit.call_args
        self.assertEqual(args[0][0], "PRIVACY_TOGGLED")
        self.assertEqual(args[0][1]["new_state"], "PRIVATE")

    def test_emits_privacy_toggled_on_set_aware(self):
        db = _make_db(initial_state="PRIVATE")
        bus = _make_event_bus()
        pm = PrivacyManager(db=db, event_bus=bus)
        pm.set_aware()
        bus.emit.assert_called_once()
        args = bus.emit.call_args
        self.assertEqual(args[0][1]["new_state"], "AWARE")

    def test_no_event_when_state_unchanged(self):
        """Idempotent set_private should not emit (nothing changed)."""
        bus = _make_event_bus()
        db = _make_db(initial_state="PRIVATE")
        pm = PrivacyManager(db=db, event_bus=bus)
        pm.set_private()
        bus.emit.assert_not_called()

    def test_event_bus_failure_does_not_raise(self):
        """If event bus fails, the transition still completes."""
        bus = MagicMock()
        bus.emit.side_effect = Exception("bus down")
        pm = PrivacyManager(event_bus=bus)
        pm.set_private()  # should not raise
        self.assertTrue(pm.is_private())

    def test_no_event_without_event_bus(self):
        """No event bus — transitions still work silently."""
        pm = PrivacyManager(event_bus=None)
        pm.set_private()
        self.assertTrue(pm.is_private())


class TestPrivacyManagerThreadSafety(unittest.TestCase):
    """Thread safety under concurrent reads and writes."""

    def test_concurrent_reads_are_safe(self):
        pm = PrivacyManager()
        results = []
        errors = []

        def reader():
            try:
                for _ in range(100):
                    _ = pm.state
                    _ = pm.is_private()
                    _ = pm.check_privacy()
                results.append("ok")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=reader) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)
        self.assertEqual(len(results), 8)

    def test_concurrent_toggles_do_not_corrupt_state(self):
        """
        Many threads toggling simultaneously. We can't predict the final state
        but it must be one of the two valid values and never raise.
        """
        pm = PrivacyManager()
        errors = []

        def toggler():
            try:
                for _ in range(20):
                    pm.toggle()
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=toggler) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)
        # State must be one of the two valid values
        self.assertIn(pm.state, (PrivacyState.AWARE, PrivacyState.PRIVATE))

    def test_read_while_writing_is_safe(self):
        pm = PrivacyManager()
        errors = []

        def writer():
            try:
                for _ in range(50):
                    pm.set_private()
                    pm.set_aware()
            except Exception as e:
                errors.append(e)

        def reader():
            try:
                for _ in range(100):
                    _ = pm.state
                    _ = pm.check_privacy()
            except Exception as e:
                errors.append(e)

        threads = (
            [threading.Thread(target=writer) for _ in range(4)] +
            [threading.Thread(target=reader) for _ in range(4)]
        )
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)


class TestPrivacyManagerRepr(unittest.TestCase):
    def test_repr_includes_state(self):
        pm = PrivacyManager()
        r = repr(pm)
        self.assertIn("AWARE", r)


# ── Entry point for running without pytest ────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
