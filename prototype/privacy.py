"""
Submantle Privacy Mode — The real off switch.

PrivacyManager controls whether Submantle is actively watching.

AWARE (default):
    Normal operation. Processes are scanned, events emitted, state written to
    SQLite scan tables. Everything works.

PRIVATE:
    Submantle stops watching. The guarantees:
    - No new process scans run
    - In-memory process cache is dropped immediately on toggle
    - Nothing written to SQLite scan tables
    - Process events (PROCESS_STARTED, PROCESS_DIED, SCAN_COMPLETE) are suppressed
    - PRIVACY_TOGGLED event still fires (so the dashboard knows)
    - Health checks still respond ("Submantle is running")
    - Agent registry still works (identity is not sensitive — activity is)

Privacy state is persisted to the SQLite settings table so it survives restarts.
If the DB is unavailable on startup, default is AWARE (fail open for operability).

Thread safety: all state reads and writes go through a threading.Lock so callers
from the scanner thread and the API thread see a consistent value.
"""

import logging
import threading
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class PrivacyState(Enum):
    AWARE = "AWARE"
    PRIVATE = "PRIVATE"


# Settings key used in the SubmantleDB settings table
_SETTING_KEY = "privacy_mode"


class PrivacyManager:
    """
    Manages privacy state for Submantle.

    Designed to be instantiated once at startup and shared across components.
    Use check_privacy() before any sensitive operation.
    """

    def __init__(self, db=None, event_bus=None):
        """
        Args:
            db: SubmantleDB instance. If None, state is not persisted across
                restarts (safe for testing and single-shot use).
            event_bus: EventBus instance. If None, PRIVACY_TOGGLED events are
                not emitted (safe for testing).
        """
        self._lock = threading.Lock()
        self._db = db
        self._event_bus = event_bus
        self._state = self._load_persisted_state()

        # Sync event bus privacy filter on startup — if we restart in PRIVATE mode,
        # the bus must start filtering immediately, not wait for the first toggle.
        if self._event_bus is not None and self._state == PrivacyState.PRIVATE:
            self._event_bus.set_privacy_mode(True)

        logger.info("PrivacyManager initialized in %s mode", self._state.value)

    # ── State access ───────────────────────────────────────────────────────────

    @property
    def state(self) -> PrivacyState:
        """Current privacy state. Thread-safe read."""
        with self._lock:
            return self._state

    def is_private(self) -> bool:
        """Returns True when in PRIVATE mode. Thread-safe."""
        with self._lock:
            return self._state == PrivacyState.PRIVATE

    def is_aware(self) -> bool:
        """Returns True when in AWARE mode. Thread-safe."""
        with self._lock:
            return self._state == PrivacyState.AWARE

    def check_privacy(self) -> bool:
        """
        Gate check for sensitive operations.

        Usage:
            if privacy_manager.check_privacy():
                return  # skip — we are in PRIVATE mode

        Returns True when the caller should SKIP the sensitive work (PRIVATE mode).
        Returns False when the caller should PROCEED (AWARE mode).
        """
        return self.is_private()

    # ── State mutation ─────────────────────────────────────────────────────────

    def set_private(self) -> dict:
        """
        Switch to PRIVATE mode.

        Persists state, emits PRIVACY_TOGGLED event.
        Returns a status dict summarising the transition.
        Idempotent — calling when already PRIVATE is safe.
        """
        return self._transition_to(PrivacyState.PRIVATE)

    def set_aware(self) -> dict:
        """
        Switch to AWARE mode.

        Persists state, emits PRIVACY_TOGGLED event.
        Returns a status dict summarising the transition.
        Idempotent — calling when already AWARE is safe.
        """
        return self._transition_to(PrivacyState.AWARE)

    def toggle(self) -> dict:
        """
        Toggle between AWARE and PRIVATE.

        Returns a status dict with new_state and previous_state.
        """
        with self._lock:
            current = self._state

        if current == PrivacyState.AWARE:
            return self._transition_to(PrivacyState.PRIVATE)
        else:
            return self._transition_to(PrivacyState.AWARE)

    # ── Internals ──────────────────────────────────────────────────────────────

    def _transition_to(self, new_state: PrivacyState) -> dict:
        """
        Perform the state transition with lock held for the state write.

        Persist and emit are done outside the lock to avoid holding it during
        I/O — the brief window where state is changed but not yet persisted is
        acceptable because privacy failing closed (refusing to scan if uncertain)
        is the safe direction.
        """
        with self._lock:
            previous = self._state
            self._state = new_state

        changed = previous != new_state

        if changed:
            logger.info(
                "Privacy mode changed: %s -> %s",
                previous.value,
                new_state.value,
            )
            self._persist_state(new_state)
            self._emit_toggle_event(previous, new_state)

        return {
            "previous_state": previous.value,
            "new_state": new_state.value,
            "changed": changed,
        }

    def _load_persisted_state(self) -> PrivacyState:
        """Load state from DB settings. Defaults to AWARE if unset or DB unavailable."""
        if self._db is None:
            return PrivacyState.AWARE

        try:
            raw = self._db.get_setting(_SETTING_KEY)
            if raw is not None:
                return PrivacyState(raw)
        except Exception as exc:
            logger.warning(
                "Could not load privacy state from DB (%s). Defaulting to AWARE.", exc
            )

        return PrivacyState.AWARE

    def _persist_state(self, state: PrivacyState) -> None:
        """Write current state to DB settings. Logs and continues on failure."""
        if self._db is None:
            return

        try:
            self._db.set_setting(_SETTING_KEY, state.value)
        except Exception as exc:
            logger.error(
                "Failed to persist privacy state to DB (%s). "
                "State is correct in memory but won't survive restart.",
                exc,
            )

    def _emit_toggle_event(self, previous: PrivacyState, new_state: PrivacyState) -> None:
        """
        Emit PRIVACY_TOGGLED event. This is one of the few events that fires in
        BOTH modes — the dashboard needs to know when things changed.
        """
        if self._event_bus is None:
            return

        try:
            # Sync the event bus's privacy filter BEFORE emitting the event.
            # Without this, the bus stays in AWARE mode and process events
            # leak through to subscribers (including the future MCP stream).
            self._event_bus.set_privacy_mode(new_state == PrivacyState.PRIVATE)

            self._event_bus.emit(
                "PRIVACY_TOGGLED",
                {
                    "previous_state": previous.value,
                    "new_state": new_state.value,
                },
                source="PrivacyManager",
            )
        except Exception as exc:
            logger.warning("Failed to emit PRIVACY_TOGGLED event: %s", exc)

    # ── Representation ─────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return f"PrivacyManager(state={self._state.value})"
