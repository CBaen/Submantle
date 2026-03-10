"""
Substrate Database Layer — SQLite persistence.
The ground beneath everything needs memory.

All state that survives a restart lives here:
  - scan_snapshots: timestamped process scan results
  - agent_registry: registered agents and their trust metadata
  - events: immutable event log
  - settings: key-value configuration store

Design principles:
  - No ORM. Raw sqlite3 — lightweight, zero dependencies.
  - WAL mode for concurrent reads (multiple readers, one writer).
  - JSON columns for structured data that doesn't need filtering.
  - Thread-safe via sqlite3's check_same_thread=False + connection-per-operation pattern.
  - analytics_metadata column on scan_snapshots is intentionally nullable —
    reserved for future federated analytics. Cannot be retrofitted later without
    a schema migration, so it lives here from day one.
"""

import json
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any


# Default database path — sits next to this file.
# Tests should pass ':memory:' to the constructor instead.
DEFAULT_DB_PATH = Path(__file__).parent / "substrate.db"


class SubstrateDB:
    """
    Lightweight SQLite interface for Substrate.

    Usage:
        db = SubstrateDB()                  # uses prototype/substrate.db
        db = SubstrateDB(':memory:')        # in-memory, for tests
        db = SubstrateDB('/path/to/db')     # explicit path

    Thread safety:
        Each call acquires its own connection from the pool. SQLite's WAL mode
        allows concurrent reads. Writes serialize naturally through SQLite's
        locking. Do not share Connection objects across threads.
    """

    def __init__(self, path: str | Path | None = None) -> None:
        if path is None:
            self._path = str(DEFAULT_DB_PATH)
        elif path == ":memory:":
            self._path = ":memory:"
        else:
            self._path = str(path)

        self._initialize()

    # ── Connection management ──────────────────────────────────────────────────

    @contextmanager
    def _conn(self):
        """
        Yield a short-lived connection. Commits on exit, rolls back on error.
        Using check_same_thread=False is safe here — we never share a connection
        across threads, we create a new one per logical operation.
        """
        conn = sqlite3.connect(self._path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # dict-like rows
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _initialize(self) -> None:
        """Create schema and configure WAL mode. Idempotent."""
        with self._conn() as conn:
            # WAL mode: readers never block writers, writers never block readers.
            # Critical for the 5-second scan cycle running alongside API requests.
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.executescript(_SCHEMA)

    # ── scan_snapshots ─────────────────────────────────────────────────────────

    def save_scan_snapshot(
        self,
        data: dict,
        process_count: int,
        identified_count: int,
        analytics_metadata: dict | None = None,
    ) -> int:
        """
        Persist a process scan result.

        Args:
            data: Full scan payload — the dict returned by substrate.scan_processes()
                  combined with the awareness_report(). Caller decides what to include.
            process_count: Total processes seen in this scan.
            identified_count: Processes matched to a signature.
            analytics_metadata: Reserved for future federated analytics aggregation.
                                 Pass None — this column exists architecturally, not yet
                                 functionally. A future analytics module will populate it
                                 with pre-aggregated, privacy-safe statistics.

        Returns:
            Row ID of the new snapshot.
        """
        with self._conn() as conn:
            cursor = conn.execute(
                """
                INSERT INTO scan_snapshots
                    (timestamp, data, process_count, identified_count, analytics_metadata)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    time.time(),
                    json.dumps(data),
                    process_count,
                    identified_count,
                    json.dumps(analytics_metadata) if analytics_metadata is not None else None,
                ),
            )
            return cursor.lastrowid

    def get_latest_scan(self) -> dict | None:
        """
        Return the most recent scan snapshot, or None if no scans exist.

        Returns a dict with keys:
            id, timestamp, data (parsed), process_count, identified_count,
            analytics_metadata (parsed, may be None)
        """
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM scan_snapshots ORDER BY timestamp DESC LIMIT 1"
            ).fetchone()
            if row is None:
                return None
            return _row_to_scan_snapshot(row)

    def get_scan_history(self, limit: int = 100) -> list[dict]:
        """
        Return up to `limit` recent snapshots, newest first.
        Useful for trend analysis and awareness stream.
        """
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM scan_snapshots ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [_row_to_scan_snapshot(r) for r in rows]

    def prune_scan_history(self, keep_count: int = 1000) -> int:
        """
        Delete old snapshots, keeping the `keep_count` most recent.
        Returns the number of rows deleted.
        Protects the database from unbounded growth.
        """
        with self._conn() as conn:
            result = conn.execute(
                """
                DELETE FROM scan_snapshots
                WHERE id NOT IN (
                    SELECT id FROM scan_snapshots
                    ORDER BY timestamp DESC
                    LIMIT ?
                )
                """,
                (keep_count,),
            )
            return result.rowcount

    # ── agent_registry ─────────────────────────────────────────────────────────

    def register_agent(
        self,
        agent_name: str,
        version: str,
        author: str,
        capabilities: list[str],
        token_hash: str,
        trust_metadata: dict | None = None,
    ) -> int:
        """
        Insert a new agent registration.

        Args:
            agent_name: Human-readable name (e.g., "SubstrateWatcher").
            version: Semver string.
            author: Publisher/author name.
            capabilities: List of capability strings the agent declares.
            token_hash: HMAC-SHA256 hex digest — NOT the raw token. Store only the hash.
            trust_metadata: Optional structured trust data (schema TBD by agent_registry.py).

        Returns:
            Row ID of the new agent registration.
        """
        now = time.time()
        with self._conn() as conn:
            cursor = conn.execute(
                """
                INSERT INTO agent_registry
                    (agent_name, version, author, capabilities,
                     token_hash, registration_time, last_seen,
                     total_queries, incidents, trust_metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, ?)
                """,
                (
                    agent_name,
                    version,
                    author,
                    json.dumps(capabilities),
                    token_hash,
                    now,
                    now,
                    json.dumps(trust_metadata) if trust_metadata is not None else None,
                ),
            )
            return cursor.lastrowid

    def get_agent_by_token_hash(self, token_hash: str) -> dict | None:
        """Look up an agent by token hash. Returns None if not found."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM agent_registry WHERE token_hash = ?",
                (token_hash,),
            ).fetchone()
            return _row_to_agent(row) if row else None

    def get_agent_by_id(self, agent_id: int) -> dict | None:
        """Look up an agent by primary key. Returns None if not found."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM agent_registry WHERE id = ?",
                (agent_id,),
            ).fetchone()
            return _row_to_agent(row) if row else None

    def list_agents(self) -> list[dict]:
        """Return all registered agents, ordered by registration time."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM agent_registry ORDER BY registration_time ASC"
            ).fetchall()
            return [_row_to_agent(r) for r in rows]

    def update_agent_last_seen(self, agent_id: int) -> None:
        """Touch last_seen timestamp. Called on every verified query."""
        with self._conn() as conn:
            conn.execute(
                "UPDATE agent_registry SET last_seen = ? WHERE id = ?",
                (time.time(), agent_id),
            )

    def increment_agent_queries(self, agent_id: int) -> None:
        """Increment total_queries counter for trust scoring."""
        with self._conn() as conn:
            conn.execute(
                "UPDATE agent_registry SET total_queries = total_queries + 1, last_seen = ? WHERE id = ?",
                (time.time(), agent_id),
            )

    def increment_agent_incidents(self, agent_id: int) -> None:
        """Increment incident counter. Future trust scoring algorithm uses this."""
        with self._conn() as conn:
            conn.execute(
                "UPDATE agent_registry SET incidents = incidents + 1 WHERE id = ?",
                (agent_id,),
            )

    def deregister_agent(self, agent_id: int) -> bool:
        """
        Remove an agent registration.
        Returns True if a row was deleted, False if agent_id was not found.
        """
        with self._conn() as conn:
            result = conn.execute(
                "DELETE FROM agent_registry WHERE id = ?",
                (agent_id,),
            )
            return result.rowcount > 0

    def update_trust_metadata(self, agent_id: int, trust_metadata: dict) -> None:
        """Replace trust_metadata JSON for an agent."""
        with self._conn() as conn:
            conn.execute(
                "UPDATE agent_registry SET trust_metadata = ? WHERE id = ?",
                (json.dumps(trust_metadata), agent_id),
            )

    # ── events ─────────────────────────────────────────────────────────────────

    def log_event(
        self,
        event_type: str,
        data: dict,
        privacy_mode_active: bool = False,
    ) -> int:
        """
        Append an event to the immutable event log.

        Args:
            event_type: One of the EventType enum values (string).
            data: Arbitrary event payload. Privacy-sensitive data should be
                  stripped before calling this when privacy_mode_active=True.
            privacy_mode_active: Snapshot of privacy state at emission time.
                                  Useful for auditing what was logged under which mode.

        Returns:
            Row ID of the new event.
        """
        with self._conn() as conn:
            cursor = conn.execute(
                """
                INSERT INTO events (timestamp, event_type, data, privacy_mode_active)
                VALUES (?, ?, ?, ?)
                """,
                (
                    time.time(),
                    event_type,
                    json.dumps(data),
                    1 if privacy_mode_active else 0,
                ),
            )
            return cursor.lastrowid

    def get_recent_events(
        self,
        limit: int = 100,
        event_type: str | None = None,
    ) -> list[dict]:
        """
        Return recent events, newest first.

        Args:
            limit: Max rows to return.
            event_type: If set, filter to only this event type.
        """
        with self._conn() as conn:
            if event_type:
                rows = conn.execute(
                    """
                    SELECT * FROM events
                    WHERE event_type = ?
                    ORDER BY timestamp DESC LIMIT ?
                    """,
                    (event_type, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM events ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            return [_row_to_event(r) for r in rows]

    def prune_events(self, keep_count: int = 10000) -> int:
        """
        Delete old events, keeping the most recent `keep_count`.
        Returns rows deleted.
        """
        with self._conn() as conn:
            result = conn.execute(
                """
                DELETE FROM events
                WHERE id NOT IN (
                    SELECT id FROM events
                    ORDER BY timestamp DESC
                    LIMIT ?
                )
                """,
                (keep_count,),
            )
            return result.rowcount

    # ── settings ───────────────────────────────────────────────────────────────

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a setting value. Returns `default` if key doesn't exist.
        Values are stored as strings; caller is responsible for type conversion.
        """
        with self._conn() as conn:
            row = conn.execute(
                "SELECT value FROM settings WHERE key = ?",
                (key,),
            ).fetchone()
            if row is None:
                return default
            return row["value"]

    def set_setting(self, key: str, value: Any) -> None:
        """
        Upsert a setting. Value is coerced to string.
        Used by: privacy.py (mode state), agent_registry.py (server secret).
        """
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at
                """,
                (key, str(value), time.time()),
            )

    def delete_setting(self, key: str) -> bool:
        """Remove a setting. Returns True if it existed."""
        with self._conn() as conn:
            result = conn.execute(
                "DELETE FROM settings WHERE key = ?",
                (key,),
            )
            return result.rowcount > 0

    def all_settings(self) -> dict[str, str]:
        """Return all settings as a plain dict. Useful for diagnostics."""
        with self._conn() as conn:
            rows = conn.execute("SELECT key, value FROM settings").fetchall()
            return {r["key"]: r["value"] for r in rows}


# ── Schema ─────────────────────────────────────────────────────────────────────

_SCHEMA = """
CREATE TABLE IF NOT EXISTS scan_snapshots (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp           REAL    NOT NULL,       -- Unix epoch, float
    data                TEXT    NOT NULL,       -- JSON: full scan payload
    process_count       INTEGER NOT NULL,       -- total processes in this scan
    identified_count    INTEGER NOT NULL,       -- matched to a signature
    analytics_metadata  TEXT    DEFAULT NULL    -- JSON: reserved for federated analytics
                                               --   (pre-aggregated, privacy-safe stats)
                                               --   Nullable by design. Will be populated
                                               --   by a future analytics module.
                                               --   NEVER remove this column without a
                                               --   migration plan — retrofitting requires
                                               --   a schema migration on every device.
);

CREATE INDEX IF NOT EXISTS idx_scan_snapshots_timestamp
    ON scan_snapshots(timestamp DESC);


CREATE TABLE IF NOT EXISTS agent_registry (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name          TEXT    NOT NULL,
    version             TEXT    NOT NULL,
    author              TEXT    NOT NULL,
    capabilities        TEXT    NOT NULL DEFAULT '[]',  -- JSON array of strings
    token_hash          TEXT    NOT NULL UNIQUE,        -- HMAC-SHA256 hex, NOT the raw token
    registration_time   REAL    NOT NULL,
    last_seen           REAL    NOT NULL,
    total_queries       INTEGER NOT NULL DEFAULT 0,
    incidents           INTEGER NOT NULL DEFAULT 0,
    trust_metadata      TEXT    DEFAULT NULL            -- JSON: future trust scoring data
);

CREATE INDEX IF NOT EXISTS idx_agent_registry_token_hash
    ON agent_registry(token_hash);


CREATE TABLE IF NOT EXISTS events (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp           REAL    NOT NULL,
    event_type          TEXT    NOT NULL,
    data                TEXT    NOT NULL DEFAULT '{}',  -- JSON event payload
    privacy_mode_active INTEGER NOT NULL DEFAULT 0      -- BOOLEAN: 0=false, 1=true
);

CREATE INDEX IF NOT EXISTS idx_events_timestamp
    ON events(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_events_type
    ON events(event_type, timestamp DESC);


CREATE TABLE IF NOT EXISTS settings (
    key         TEXT    PRIMARY KEY,
    value       TEXT    NOT NULL,
    updated_at  REAL    NOT NULL
);
"""


# ── Row serializers ────────────────────────────────────────────────────────────

def _row_to_scan_snapshot(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "timestamp": row["timestamp"],
        "data": json.loads(row["data"]),
        "process_count": row["process_count"],
        "identified_count": row["identified_count"],
        "analytics_metadata": json.loads(row["analytics_metadata"])
            if row["analytics_metadata"] is not None else None,
    }


def _row_to_agent(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "agent_name": row["agent_name"],
        "version": row["version"],
        "author": row["author"],
        "capabilities": json.loads(row["capabilities"]),
        "token_hash": row["token_hash"],
        "registration_time": row["registration_time"],
        "last_seen": row["last_seen"],
        "total_queries": row["total_queries"],
        "incidents": row["incidents"],
        "trust_metadata": json.loads(row["trust_metadata"])
            if row["trust_metadata"] is not None else None,
    }


def _row_to_event(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "timestamp": row["timestamp"],
        "event_type": row["event_type"],
        "data": json.loads(row["data"]),
        "privacy_mode_active": bool(row["privacy_mode_active"]),
    }
