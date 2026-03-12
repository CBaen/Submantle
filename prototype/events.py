"""
Submantle Event Bus — Internal pub/sub system.
Everything that changes in Submantle announces itself here.

The event bus does two jobs:
  1. Routes events synchronously to in-process subscribers.
  2. Persists events to the SQLite events table for history/audit.

Privacy mode is enforced at the bus level: when PRIVATE, process-related
events are silently dropped before reaching any subscriber or being logged.
Only PRIVACY_TOGGLED passes through in PRIVATE mode.

Asyncio note:
  The bus is synchronous today. The interface is designed so that swapping
  to asyncio requires only one change: make emit() async and await each
  callback. Subscribers should be written as if they could be awaited.
  Do not put blocking I/O inside subscriber callbacks.
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


class EventType(str, Enum):
    """
    All event types the bus understands.

    Using str+Enum means values compare equal to plain strings (e.g., for SQLite
    queries and JSON). str() behavior changed in Python 3.11+ — __str__ is
    overridden to always return the value string, not "EventType.X".
    """

    # Process lifecycle — suppressed in PRIVATE mode
    PROCESS_STARTED = "PROCESS_STARTED"
    PROCESS_DIED = "PROCESS_DIED"

    # Scan lifecycle — SCAN_COMPLETE is suppressed in PRIVATE mode
    # (because it carries process data)
    SCAN_COMPLETE = "SCAN_COMPLETE"

    # Privacy — always passes through regardless of mode
    PRIVACY_TOGGLED = "PRIVACY_TOGGLED"

    # Agent lifecycle — passes through in PRIVATE mode
    # (identity is not sensitive — activity is)
    AGENT_REGISTERED = "AGENT_REGISTERED"
    AGENT_DEREGISTERED = "AGENT_DEREGISTERED"

    # System health — passes through in PRIVATE mode
    RESOURCE_WARNING = "RESOURCE_WARNING"

    def __str__(self) -> str:
        # Python 3.11+ changed str(StrEnum) to return "ClassName.MEMBER".
        # Override to always return the value string so JSON/SQLite/logging
        # sees "SCAN_COMPLETE" not "EventType.SCAN_COMPLETE".
        return self.value


# Events that carry process data — suppressed when privacy mode is active.
_PROCESS_EVENTS: frozenset[EventType] = frozenset({
    EventType.PROCESS_STARTED,
    EventType.PROCESS_DIED,
    EventType.SCAN_COMPLETE,
})


@dataclass
class Event:
    """
    An event instance. Immutable after creation.

    Fields:
        event_type: The EventType value.
        data: Arbitrary payload dict. Callers own the content.
        source: String identifying the emitting component ("substrate", "api", etc.)
        timestamp: Unix epoch float. Set automatically at emit time.
    """

    event_type: EventType
    data: dict
    source: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        """Serializable representation for logging and API responses."""
        return {
            "event_type": self.event_type,
            "data": self.data,
            "source": self.source,
            "timestamp": self.timestamp,
        }


# Type alias for subscriber callbacks.
# Signature: callback(event: Event) -> None
# Future asyncio upgrade: callback(event: Event) -> Awaitable[None]
EventCallback = Callable[[Event], None]


class EventBus:
    """
    Internal pub/sub event bus.

    Usage:
        bus = EventBus(db=SubmantleDB())    # with persistence
        bus = EventBus()                    # no persistence (tests, early init)

        def on_scan(event):
            print(f"Scan complete: {event.data['process_count']} processes")

        bus.subscribe(EventType.SCAN_COMPLETE, on_scan)
        bus.emit(EventType.SCAN_COMPLETE, {"process_count": 42}, source="submantle")
        bus.unsubscribe(EventType.SCAN_COMPLETE, on_scan)

    Privacy mode:
        bus.set_privacy_mode(True)   # suppress process events
        bus.set_privacy_mode(False)  # restore normal operation

    Wildcard subscription:
        bus.subscribe("*", my_logger)  # receives every event that passes filtering
    """

    # Sentinel for wildcard subscriptions
    _WILDCARD = "*"

    def __init__(self, db=None) -> None:
        """
        Args:
            db: Optional SubmantleDB instance. If provided, events are persisted
                to the events table. If None, events are only dispatched in-memory.
                Pass None for tests or when the DB layer isn't ready yet.
        """
        self._db = db
        self._privacy_mode: bool = False

        # Mapping: event_type (str or "*") -> list of callbacks
        # Using defaultdict avoids "if key not in dict" checks throughout.
        self._subscribers: dict[str, list[EventCallback]] = defaultdict(list)

    # ── Privacy mode ───────────────────────────────────────────────────────────

    def set_privacy_mode(self, active: bool) -> None:
        """
        Enable or disable privacy mode.

        When active=True: process-related events (PROCESS_STARTED, PROCESS_DIED,
        SCAN_COMPLETE) are dropped before reaching any subscriber or the DB log.
        PRIVACY_TOGGLED is always allowed through.

        This method is called by privacy.py when the user toggles privacy mode.
        The privacy state in the bus is a mirror of the authoritative state in
        PrivacyManager — do not rely on this for security decisions; use
        PrivacyManager.check_privacy() instead.
        """
        self._privacy_mode = active

    @property
    def privacy_mode(self) -> bool:
        """Current privacy mode state."""
        return self._privacy_mode

    # ── Subscriptions ──────────────────────────────────────────────────────────

    def subscribe(self, event_type: EventType | str, callback: EventCallback) -> None:
        """
        Register a callback for an event type.

        Args:
            event_type: An EventType value, or "*" to receive all events.
            callback: Callable that accepts a single Event argument.
                      Must not block for extended periods — the bus is synchronous.
                      Keep callbacks fast; offload heavy work to threads/queues.

        Subscribing the same callback twice for the same event_type is safe —
        it will be called only once per emission (duplicate is suppressed).
        """
        key = str(event_type)
        if callback not in self._subscribers[key]:
            self._subscribers[key].append(callback)

    def unsubscribe(self, event_type: EventType | str, callback: EventCallback) -> bool:
        """
        Remove a previously registered callback.

        Args:
            event_type: The event type the callback was registered under.
            callback: The exact callback object (identity comparison, not equality).

        Returns:
            True if the callback was found and removed. False if it wasn't registered.
        """
        key = str(event_type)
        subscribers = self._subscribers.get(key, [])
        if callback in subscribers:
            subscribers.remove(callback)
            return True
        return False

    def subscriber_count(self, event_type: EventType | str | None = None) -> int:
        """
        Count registered subscribers.

        Args:
            event_type: If provided, count only subscribers for that type.
                        If None, count all subscribers across all types.
        """
        if event_type is not None:
            return len(self._subscribers.get(str(event_type), []))
        return sum(len(callbacks) for callbacks in self._subscribers.values())

    # ── Emission ───────────────────────────────────────────────────────────────

    def emit(
        self,
        event_type: EventType | str,
        data: dict,
        source: str = "substrate",
    ) -> Event | None:
        """
        Emit an event. Dispatches to subscribers and logs to SQLite.

        Args:
            event_type: The event type to emit.
            data: Payload dict. Will be shallow-copied to protect against
                  mutation after emission. Do not include process PIDs or
                  personal data when privacy mode is active — callers must
                  scrub sensitive data before calling emit() in PRIVATE mode.
            source: The component emitting this event. Used for tracing.
                    Suggested values: "submantle", "api", "privacy", "agent_registry".

        Returns:
            The Event that was dispatched, or None if the event was suppressed
            by privacy mode.

        Privacy enforcement:
            Process events are silently dropped when privacy_mode=True.
            PRIVACY_TOGGLED always passes through regardless of mode.
        """
        event_type_val = EventType(event_type) if isinstance(event_type, str) else event_type

        # Privacy gate: suppress process events in PRIVATE mode.
        # PRIVACY_TOGGLED is explicitly excluded — it must always fire so that
        # subscribers (UI, logging) know the state changed.
        if self._privacy_mode and event_type_val in _PROCESS_EVENTS:
            return None

        event = Event(
            event_type=event_type_val,
            data=dict(data),  # shallow copy
            source=source,
            timestamp=time.time(),
        )

        # Persist to SQLite before dispatching to subscribers.
        # If DB write fails, we still dispatch — event log is best-effort.
        # Failures are swallowed here because a logging failure should never
        # crash the system. The DB layer logs its own errors.
        if self._db is not None:
            try:
                self._db.log_event(
                    event_type=event.event_type,
                    data=event.data,
                    privacy_mode_active=self._privacy_mode,
                )
            except Exception:
                # Silently continue — event dispatch proceeds regardless of
                # persistence failure. This keeps Submantle running even if
                # the database is temporarily locked or corrupted.
                pass

        # Dispatch to type-specific subscribers
        self._dispatch(str(event_type_val), event)

        # Dispatch to wildcard subscribers
        if str(event_type_val) != self._WILDCARD:
            self._dispatch(self._WILDCARD, event)

        return event

    def _dispatch(self, key: str, event: Event) -> None:
        """
        Call all subscribers for `key`. Errors in subscribers are caught and
        silenced so one bad callback can't prevent others from receiving events.

        In a future asyncio upgrade, this becomes:
            async def _dispatch(self, key, event):
                for cb in list(self._subscribers.get(key, [])):
                    await cb(event)
        """
        for callback in list(self._subscribers.get(key, [])):
            # Iterate over a copy — subscribers may unsubscribe during dispatch.
            try:
                callback(event)
            except Exception:
                # A subscriber failure must not propagate to the emitter or
                # prevent subsequent subscribers from receiving the event.
                # Future: route these to a structured error log.
                pass
