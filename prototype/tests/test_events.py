"""
Tests for prototype/events.py — EventBus

Tests cover:
  - Subscribe/unsubscribe mechanics
  - Event emission and dispatch to subscribers
  - Privacy mode suppression
  - SQLite persistence integration (with real in-memory DB)
  - Error isolation (subscriber failures don't propagate)
  - Wildcard subscriptions
  - Event object structure

Run: cd prototype && python -m pytest tests/test_events.py -v
"""

import time

import pytest

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from events import EventBus, EventType, Event, _PROCESS_EVENTS
from database import SubmantleDB


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def bus():
    """EventBus with no DB (pure in-memory dispatch)."""
    return EventBus()


@pytest.fixture
def db():
    return SubmantleDB(":memory:")


@pytest.fixture
def bus_with_db(db):
    """EventBus wired to an in-memory SQLite database."""
    return EventBus(db=db), db


# ── EventType enum ─────────────────────────────────────────────────────────────

class TestEventType:
    def test_all_required_types_exist(self):
        """All types specified in the build brief must be present."""
        required = {
            "PROCESS_STARTED", "PROCESS_DIED", "SCAN_COMPLETE",
            "PRIVACY_TOGGLED", "AGENT_REGISTERED", "AGENT_DEREGISTERED",
            "RESOURCE_WARNING",
        }
        actual = {e.value for e in EventType}
        assert required == actual

    def test_str_enum_values(self):
        """EventType values work as plain strings (for JSON/SQLite)."""
        assert str(EventType.SCAN_COMPLETE) == "SCAN_COMPLETE"
        assert EventType.SCAN_COMPLETE == "SCAN_COMPLETE"

    def test_process_events_set(self):
        """_PROCESS_EVENTS must contain exactly the three process-related types."""
        assert EventType.PROCESS_STARTED in _PROCESS_EVENTS
        assert EventType.PROCESS_DIED in _PROCESS_EVENTS
        assert EventType.SCAN_COMPLETE in _PROCESS_EVENTS
        # Non-process events must NOT be in the suppression set
        assert EventType.PRIVACY_TOGGLED not in _PROCESS_EVENTS
        assert EventType.AGENT_REGISTERED not in _PROCESS_EVENTS
        assert EventType.RESOURCE_WARNING not in _PROCESS_EVENTS


# ── Event dataclass ────────────────────────────────────────────────────────────

class TestEventDataclass:
    def test_event_creation(self):
        e = Event(
            event_type=EventType.SCAN_COMPLETE,
            data={"process_count": 10},
            source="submantle",
        )
        assert e.event_type == EventType.SCAN_COMPLETE
        assert e.data["process_count"] == 10
        assert e.source == "submantle"
        assert isinstance(e.timestamp, float)
        assert e.timestamp > 0

    def test_to_dict(self):
        e = Event(EventType.PRIVACY_TOGGLED, {"active": True}, "privacy")
        d = e.to_dict()
        assert d["event_type"] == EventType.PRIVACY_TOGGLED
        assert d["data"] == {"active": True}
        assert d["source"] == "privacy"
        assert "timestamp" in d


# ── Subscribe / Unsubscribe ────────────────────────────────────────────────────

class TestSubscriptions:
    def test_subscribe_and_callback_called(self, bus):
        received = []
        bus.subscribe(EventType.SCAN_COMPLETE, lambda e: received.append(e))
        bus.emit(EventType.SCAN_COMPLETE, {"count": 5}, source="test")
        assert len(received) == 1
        assert received[0].data["count"] == 5

    def test_subscribe_multiple_callbacks(self, bus):
        calls = []
        bus.subscribe(EventType.SCAN_COMPLETE, lambda e: calls.append("a"))
        bus.subscribe(EventType.SCAN_COMPLETE, lambda e: calls.append("b"))
        bus.emit(EventType.SCAN_COMPLETE, {}, source="test")
        assert sorted(calls) == ["a", "b"]

    def test_no_duplicate_subscriptions(self, bus):
        """Same callback registered twice should only be called once."""
        count = []
        cb = lambda e: count.append(1)
        bus.subscribe(EventType.SCAN_COMPLETE, cb)
        bus.subscribe(EventType.SCAN_COMPLETE, cb)  # duplicate
        bus.emit(EventType.SCAN_COMPLETE, {}, source="test")
        assert len(count) == 1

    def test_unsubscribe_stops_delivery(self, bus):
        received = []
        cb = lambda e: received.append(e)
        bus.subscribe(EventType.SCAN_COMPLETE, cb)
        bus.unsubscribe(EventType.SCAN_COMPLETE, cb)
        bus.emit(EventType.SCAN_COMPLETE, {}, source="test")
        assert received == []

    def test_unsubscribe_returns_true_when_found(self, bus):
        cb = lambda e: None
        bus.subscribe(EventType.SCAN_COMPLETE, cb)
        assert bus.unsubscribe(EventType.SCAN_COMPLETE, cb) is True

    def test_unsubscribe_returns_false_when_not_found(self, bus):
        cb = lambda e: None
        assert bus.unsubscribe(EventType.SCAN_COMPLETE, cb) is False

    def test_subscriber_count(self, bus):
        bus.subscribe(EventType.SCAN_COMPLETE, lambda e: None)
        bus.subscribe(EventType.SCAN_COMPLETE, lambda e: None)
        bus.subscribe(EventType.PRIVACY_TOGGLED, lambda e: None)
        assert bus.subscriber_count(EventType.SCAN_COMPLETE) == 2
        assert bus.subscriber_count(EventType.PRIVACY_TOGGLED) == 1

    def test_subscriber_count_total(self, bus):
        bus.subscribe(EventType.SCAN_COMPLETE, lambda e: None)
        bus.subscribe(EventType.PRIVACY_TOGGLED, lambda e: None)
        assert bus.subscriber_count() == 2


# ── Wildcard subscriptions ─────────────────────────────────────────────────────

class TestWildcardSubscriptions:
    def test_wildcard_receives_all_events(self, bus):
        received = []
        bus.subscribe("*", lambda e: received.append(e.event_type))

        bus.emit(EventType.SCAN_COMPLETE, {}, "test")
        bus.emit(EventType.PRIVACY_TOGGLED, {}, "test")
        bus.emit(EventType.AGENT_REGISTERED, {}, "test")

        assert EventType.SCAN_COMPLETE in received
        assert EventType.PRIVACY_TOGGLED in received
        assert EventType.AGENT_REGISTERED in received

    def test_wildcard_respects_privacy_suppression(self, bus):
        """Wildcard should not receive events already suppressed by privacy mode."""
        received = []
        bus.subscribe("*", lambda e: received.append(e.event_type))
        bus.set_privacy_mode(True)

        bus.emit(EventType.PROCESS_STARTED, {"pid": 1}, "test")
        bus.emit(EventType.SCAN_COMPLETE, {}, "test")

        assert EventType.PROCESS_STARTED not in received
        assert EventType.SCAN_COMPLETE not in received

    def test_wildcard_does_not_duplicate_events(self, bus):
        """An event should not be delivered twice to the same wildcard callback."""
        count = []
        bus.subscribe("*", lambda e: count.append(1))
        bus.emit(EventType.SCAN_COMPLETE, {}, "test")
        assert len(count) == 1


# ── Event emission ─────────────────────────────────────────────────────────────

class TestEmission:
    def test_emit_returns_event(self, bus):
        event = bus.emit(EventType.SCAN_COMPLETE, {"x": 1}, source="test")
        assert isinstance(event, Event)
        assert event.event_type == EventType.SCAN_COMPLETE
        assert event.data == {"x": 1}
        assert event.source == "test"

    def test_emit_data_is_shallow_copied(self, bus):
        """Mutating the original dict after emit must not change the event's data."""
        data = {"mutable": "value"}
        received = []
        bus.subscribe(EventType.SCAN_COMPLETE, lambda e: received.append(e))
        bus.emit(EventType.SCAN_COMPLETE, data, source="test")
        data["mutable"] = "changed"
        assert received[0].data["mutable"] == "value"

    def test_emit_with_string_event_type(self, bus):
        """emit() must accept string event types as well as EventType enum values."""
        received = []
        bus.subscribe(EventType.SCAN_COMPLETE, lambda e: received.append(e))
        bus.emit("SCAN_COMPLETE", {}, source="test")
        assert len(received) == 1

    def test_emit_without_subscribers_does_not_raise(self, bus):
        event = bus.emit(EventType.RESOURCE_WARNING, {"cpu": 95}, source="test")
        assert event is not None

    def test_event_has_timestamp(self, bus):
        before = time.time()
        event = bus.emit(EventType.SCAN_COMPLETE, {}, source="test")
        after = time.time()
        assert before <= event.timestamp <= after

    def test_correct_event_type_on_emitted_event(self, bus):
        received = []
        bus.subscribe(EventType.RESOURCE_WARNING, lambda e: received.append(e))
        bus.emit(EventType.RESOURCE_WARNING, {"cpu": 90}, source="monitor")
        assert received[0].event_type == EventType.RESOURCE_WARNING
        assert received[0].source == "monitor"


# ── Privacy mode ───────────────────────────────────────────────────────────────

class TestPrivacyMode:
    def test_privacy_mode_defaults_off(self, bus):
        assert bus.privacy_mode is False

    def test_set_privacy_mode(self, bus):
        bus.set_privacy_mode(True)
        assert bus.privacy_mode is True
        bus.set_privacy_mode(False)
        assert bus.privacy_mode is False

    def test_process_started_suppressed_in_private(self, bus):
        received = []
        bus.subscribe(EventType.PROCESS_STARTED, lambda e: received.append(e))
        bus.set_privacy_mode(True)
        result = bus.emit(EventType.PROCESS_STARTED, {"pid": 123}, source="test")
        assert result is None
        assert received == []

    def test_process_died_suppressed_in_private(self, bus):
        received = []
        bus.subscribe(EventType.PROCESS_DIED, lambda e: received.append(e))
        bus.set_privacy_mode(True)
        result = bus.emit(EventType.PROCESS_DIED, {"pid": 456}, source="test")
        assert result is None
        assert received == []

    def test_scan_complete_suppressed_in_private(self, bus):
        received = []
        bus.subscribe(EventType.SCAN_COMPLETE, lambda e: received.append(e))
        bus.set_privacy_mode(True)
        result = bus.emit(EventType.SCAN_COMPLETE, {"process_count": 10}, source="test")
        assert result is None
        assert received == []

    def test_privacy_toggled_passes_through_in_private(self, bus):
        """PRIVACY_TOGGLED must always fire, even in private mode."""
        received = []
        bus.subscribe(EventType.PRIVACY_TOGGLED, lambda e: received.append(e))
        bus.set_privacy_mode(True)
        result = bus.emit(EventType.PRIVACY_TOGGLED, {"active": True}, source="privacy")
        assert result is not None
        assert len(received) == 1

    def test_agent_registered_passes_through_in_private(self, bus):
        """Agent events pass through in PRIVATE mode — identity is not sensitive."""
        received = []
        bus.subscribe(EventType.AGENT_REGISTERED, lambda e: received.append(e))
        bus.set_privacy_mode(True)
        result = bus.emit(EventType.AGENT_REGISTERED, {"name": "TestAgent"}, source="registry")
        assert result is not None
        assert len(received) == 1

    def test_agent_deregistered_passes_through_in_private(self, bus):
        received = []
        bus.subscribe(EventType.AGENT_DEREGISTERED, lambda e: received.append(e))
        bus.set_privacy_mode(True)
        result = bus.emit(EventType.AGENT_DEREGISTERED, {"name": "TestAgent"}, source="registry")
        assert result is not None
        assert len(received) == 1

    def test_resource_warning_passes_through_in_private(self, bus):
        received = []
        bus.subscribe(EventType.RESOURCE_WARNING, lambda e: received.append(e))
        bus.set_privacy_mode(True)
        result = bus.emit(EventType.RESOURCE_WARNING, {"cpu": 99}, source="monitor")
        assert result is not None
        assert len(received) == 1

    def test_process_events_work_after_disabling_private(self, bus):
        """Events suppressed in PRIVATE must flow again after switching back to AWARE."""
        received = []
        bus.subscribe(EventType.SCAN_COMPLETE, lambda e: received.append(e))
        bus.set_privacy_mode(True)
        bus.emit(EventType.SCAN_COMPLETE, {}, source="test")  # suppressed
        bus.set_privacy_mode(False)
        bus.emit(EventType.SCAN_COMPLETE, {}, source="test")  # should pass
        assert len(received) == 1


# ── SQLite persistence integration ────────────────────────────────────────────

class TestPersistenceIntegration:
    def test_events_logged_to_db(self, bus_with_db):
        bus, db = bus_with_db
        bus.emit(EventType.SCAN_COMPLETE, {"process_count": 5}, source="submantle")
        events = db.get_recent_events(limit=10)
        assert len(events) == 1
        assert events[0]["event_type"] == "SCAN_COMPLETE"
        assert events[0]["data"]["process_count"] == 5

    def test_suppressed_events_not_logged(self, bus_with_db):
        """Privacy-suppressed events must not reach the database."""
        bus, db = bus_with_db
        bus.set_privacy_mode(True)
        bus.emit(EventType.PROCESS_STARTED, {"pid": 1}, source="submantle")
        events = db.get_recent_events(limit=10)
        assert len(events) == 0

    def test_privacy_toggled_is_logged_in_private(self, bus_with_db):
        bus, db = bus_with_db
        bus.set_privacy_mode(True)
        bus.emit(EventType.PRIVACY_TOGGLED, {"active": True}, source="privacy")
        events = db.get_recent_events(limit=10)
        assert len(events) == 1
        assert events[0]["event_type"] == "PRIVACY_TOGGLED"
        assert events[0]["privacy_mode_active"] is True

    def test_privacy_mode_flag_reflected_in_log(self, bus_with_db):
        bus, db = bus_with_db
        bus.set_privacy_mode(False)
        bus.emit(EventType.SCAN_COMPLETE, {}, source="submantle")

        events = db.get_recent_events(limit=1)
        assert events[0]["privacy_mode_active"] is False

    def test_db_failure_does_not_crash_dispatch(self):
        """If the DB layer raises, event dispatch to subscribers must still work."""

        class BrokenDB:
            def log_event(self, **kwargs):
                raise RuntimeError("DB exploded")

        received = []
        bus = EventBus(db=BrokenDB())
        bus.subscribe(EventType.SCAN_COMPLETE, lambda e: received.append(e))
        # Must not raise
        event = bus.emit(EventType.SCAN_COMPLETE, {}, source="test")
        assert event is not None
        assert len(received) == 1

    def test_bus_works_without_db(self):
        """EventBus with db=None must work fine — dispatch only, no persistence."""
        received = []
        bus = EventBus(db=None)
        bus.subscribe(EventType.SCAN_COMPLETE, lambda e: received.append(e))
        event = bus.emit(EventType.SCAN_COMPLETE, {}, source="test")
        assert event is not None
        assert len(received) == 1


# ── Error isolation ────────────────────────────────────────────────────────────

class TestErrorIsolation:
    def test_subscriber_exception_does_not_propagate(self, bus):
        """A crashing subscriber must not affect the emitter or other subscribers."""
        good_calls = []

        def bad_callback(e):
            raise ValueError("I am broken")

        def good_callback(e):
            good_calls.append(e)

        bus.subscribe(EventType.SCAN_COMPLETE, bad_callback)
        bus.subscribe(EventType.SCAN_COMPLETE, good_callback)

        # Must not raise
        event = bus.emit(EventType.SCAN_COMPLETE, {}, source="test")
        assert event is not None
        assert len(good_calls) == 1

    def test_unsubscribe_during_dispatch(self, bus):
        """A subscriber that unsubscribes itself during dispatch must not crash."""
        received = []

        def self_unsubscribing(e):
            bus.unsubscribe(EventType.SCAN_COMPLETE, self_unsubscribing)
            received.append(e)

        bus.subscribe(EventType.SCAN_COMPLETE, self_unsubscribing)
        bus.emit(EventType.SCAN_COMPLETE, {}, source="test")
        assert len(received) == 1

        # Second emit: callback is gone, should not be called again
        bus.emit(EventType.SCAN_COMPLETE, {}, source="test")
        assert len(received) == 1
