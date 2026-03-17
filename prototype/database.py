"""
Submantle Database Layer — SQLite persistence.
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
  - File-backed DB: per-operation connections (WAL handles concurrent access).
  - In-memory DB: single persistent connection (SQLite :memory: is per-connection).
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
DEFAULT_DB_PATH = Path(__file__).parent / "submantle.db"


class SubmantleDB:
    """
    Lightweight SQLite interface for Submantle.

    Usage:
        db = SubmantleDB()                  # uses prototype/submantle.db
        db = SubmantleDB(':memory:')        # in-memory, for tests
        db = SubmantleDB('/path/to/db')     # explicit path

    Thread safety:
        File-backed: Each call acquires a short-lived connection. WAL mode allows
        concurrent reads. Writes serialize through SQLite's locking. Do not share
        Connection objects across threads.

        In-memory (':memory:'): A single persistent connection is held for the
        lifetime of the SubmantleDB instance. SQLite :memory: databases are
        per-connection — a new connection sees an empty database. The persistent
        connection is protected with check_same_thread=False and is safe for
        single-threaded test use. For multi-threaded production use, always use
        a file-backed database.
    """

    def __init__(self, path: str | Path | None = None) -> None:
        if path is None:
            self._path = str(DEFAULT_DB_PATH)
            self._memory_conn: sqlite3.Connection | None = None
        elif path == ":memory:":
            self._path = ":memory:"
            # Pre-open and hold the persistent connection for in-memory use.
            # This must happen before _initialize() so the schema is created
            # on the same connection that subsequent operations will use.
            self._memory_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._memory_conn.row_factory = sqlite3.Row
        else:
            self._path = str(path)
            self._memory_conn = None

        self._initialize()

    def close(self) -> None:
        """Release the persistent in-memory connection, if held. No-op for file DBs."""
        if self._memory_conn is not None:
            self._memory_conn.close()
            self._memory_conn = None

    # ── Connection management ──────────────────────────────────────────────────

    @contextmanager
    def _conn(self):
        """
        Yield a connection. Commits on exit, rolls back on error.

        In-memory: yields the persistent connection. Does NOT close it on exit.
        File-backed: opens a new connection, commits/rolls back, closes on exit.
        """
        if self._memory_conn is not None:
            # In-memory: reuse the persistent connection.
            try:
                yield self._memory_conn
                self._memory_conn.commit()
            except Exception:
                self._memory_conn.rollback()
                raise
        else:
            # File-backed: short-lived connection per operation.
            conn = sqlite3.connect(self._path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
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
            # Note: PRAGMA journal_mode=WAL is a no-op on :memory: (returns 'memory'),
            # which is acceptable — in-memory DBs don't need WAL.
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.executescript(_SCHEMA)
            # Schema migration: add deregistered_at if missing (existing DBs won't have it)
            try:
                conn.execute("ALTER TABLE agent_registry ADD COLUMN deregistered_at REAL DEFAULT NULL")
            except Exception:
                pass  # Column already exists
            # Wave 3 migration: add incident review columns
            for col, spec in [
                ("status", "TEXT NOT NULL DEFAULT 'accepted'"),
                ("severity", "TEXT NOT NULL DEFAULT 'standard'"),
                ("reviewed_at", "REAL DEFAULT NULL"),
                ("duplicate_of", "INTEGER DEFAULT NULL"),
            ]:
                try:
                    conn.execute(f"ALTER TABLE incident_reports ADD COLUMN {col} {spec}")
                except Exception:
                    pass  # Column already exists

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
            data: Full scan payload — the dict returned by submantle.scan_processes()
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
        registration_time: str | None = None,
        trust_metadata: dict | None = None,
    ) -> int:
        """
        Insert a new agent registration.

        Args:
            agent_name: Human-readable name (e.g., "SubmantleWatcher").
            version: Semver string.
            author: Publisher/author name.
            capabilities: List of capability strings the agent declares.
            token_hash: HMAC-SHA256 hex digest — NOT the raw token. Store only the hash.
            registration_time: ISO 8601 timestamp string owned by agent_registry.py.
                               Must round-trip exactly — the HMAC token is derived from it.
                               If None, uses current UTC time as ISO string.
            trust_metadata: Optional structured trust data (schema TBD by agent_registry.py).

        Returns:
            Row ID of the new agent registration.
        """
        now = time.time()
        if registration_time is None:
            from datetime import datetime, timezone
            registration_time = datetime.now(timezone.utc).isoformat()
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
                    registration_time,
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

    def list_agents(self, active_only: bool = True) -> list[dict]:
        """Return registered agents, ordered by registration time."""
        with self._conn() as conn:
            if active_only:
                rows = conn.execute(
                    "SELECT * FROM agent_registry WHERE deregistered_at IS NULL ORDER BY registration_time ASC"
                ).fetchall()
            else:
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
        """Soft-delete: mark agent as deregistered. Record is permanent."""
        with self._conn() as conn:
            result = conn.execute(
                "UPDATE agent_registry SET deregistered_at = ? WHERE id = ? AND deregistered_at IS NULL",
                (time.time(), agent_id),
            )
            return result.rowcount > 0

    def get_agent_by_name(self, agent_name: str, include_deregistered: bool = True) -> dict | None:
        """Look up an agent by name. By default finds both active and deregistered agents."""
        with self._conn() as conn:
            if include_deregistered:
                row = conn.execute(
                    "SELECT * FROM agent_registry WHERE agent_name = ?",
                    (agent_name,),
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT * FROM agent_registry WHERE agent_name = ? AND deregistered_at IS NULL",
                    (agent_name,),
                ).fetchone()
            return _row_to_agent(row) if row else None

    def update_trust_metadata(self, agent_id: int, trust_metadata: dict) -> None:
        """Replace trust_metadata JSON for an agent."""
        with self._conn() as conn:
            conn.execute(
                "UPDATE agent_registry SET trust_metadata = ? WHERE id = ?",
                (json.dumps(trust_metadata), agent_id),
            )

    # ── incident_reports ────────────────────────────────────────────────────────

    def save_incident_report(
        self,
        agent_id: int,
        agent_name: str,
        reporter: str,
        incident_type: str,
        description: str = "",
        status: str = "accepted",
        severity: str = "standard",
        duplicate_of: int | None = None,
    ) -> int:
        """
        Record an incident report against an agent.

        Credit bureau model: Submantle stores third-party reports.
        It does not detect incidents itself.

        Returns:
            Row ID of the new incident report.
        """
        with self._conn() as conn:
            cursor = conn.execute(
                """
                INSERT INTO incident_reports
                    (agent_id, agent_name, reporter, incident_type, description, timestamp,
                     status, severity, duplicate_of)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (agent_id, agent_name, reporter, incident_type, description, time.time(),
                 status, severity, duplicate_of),
            )
            return cursor.lastrowid

    def get_incident_reports(
        self,
        agent_id: int | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """
        Return incident reports, newest first.
        If agent_id is provided, filter to that agent only.
        """
        with self._conn() as conn:
            if agent_id is not None:
                rows = conn.execute(
                    """
                    SELECT * FROM incident_reports
                    WHERE agent_id = ?
                    ORDER BY timestamp DESC LIMIT ?
                    """,
                    (agent_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM incident_reports ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            return [_row_to_incident_report(r) for r in rows]

    def get_reporter_diversity(self, agent_id: int) -> int:
        """
        Count distinct reporters who have filed incidents against an agent.

        Used by compute_trust() to enrich the trust score response.
        Returns 0 if the agent has no incident reports.
        """
        with self._conn() as conn:
            row = conn.execute(
                "SELECT COUNT(DISTINCT reporter) FROM incident_reports WHERE agent_id = ?",
                (agent_id,),
            ).fetchone()
            return row[0] if row else 0

    def find_duplicate_incident(
        self, agent_id: int, reporter: str, incident_type: str, window_seconds: float = 86400.0
    ) -> dict | None:
        """Find a recent incident with same agent + reporter + type within the time window. Returns the incident or None."""
        cutoff = time.time() - window_seconds
        with self._conn() as conn:
            row = conn.execute(
                """
                SELECT * FROM incident_reports
                WHERE agent_id = ? AND reporter = ? AND incident_type = ?
                  AND timestamp > ? AND status != 'duplicate'
                ORDER BY timestamp DESC LIMIT 1
                """,
                (agent_id, reporter, incident_type, cutoff),
            ).fetchone()
            return _row_to_incident_report(row) if row else None

    def update_incident_status(self, incident_id: int, status: str) -> bool:
        """Update an incident's status and set reviewed_at timestamp. Returns True if found."""
        with self._conn() as conn:
            result = conn.execute(
                "UPDATE incident_reports SET status = ?, reviewed_at = ? WHERE id = ?",
                (status, time.time(), incident_id),
            )
            return result.rowcount > 0

    def get_accepted_incident_count(self, agent_id: int) -> int:
        """Count accepted incidents for an agent. Used for formula compatibility."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM incident_reports WHERE agent_id = ? AND status = 'accepted'",
                (agent_id,),
            ).fetchone()
            return row[0] if row else 0

    def get_incident_by_id(self, incident_id: int) -> dict | None:
        """Look up a specific incident report by ID."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM incident_reports WHERE id = ?",
                (incident_id,),
            ).fetchone()
            return _row_to_incident_report(row) if row else None

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

    # ── business_api_keys ──────────────────────────────────────────────────────

    def register_business_key(
        self,
        key_hash: str,
        business_name: str,
        email: str,
        tier: str = "free",
        rate_limit: int = 100,
    ) -> int:
        """
        Register a new business API key.

        Args:
            key_hash: SHA-256 hex of the raw API key. Never store the raw key.
            business_name: Human-readable business name.
            email: Contact email — also used for Stripe webhook matching.
            tier: 'free' or 'paid'. Determines rate limit.
            rate_limit: Requests per hour for this key.

        Returns:
            Row ID of the new business key record.
        """
        with self._conn() as conn:
            cursor = conn.execute(
                """
                INSERT INTO business_api_keys
                    (key_hash, business_name, email, tier, rate_limit, created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
                """,
                (key_hash, business_name, email, tier, rate_limit, time.time()),
            )
            return cursor.lastrowid

    def get_business_by_key_hash(self, key_hash: str) -> dict | None:
        """Look up a business by API key hash. Returns None if not found."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM business_api_keys WHERE key_hash = ?",
                (key_hash,),
            ).fetchone()
            return _row_to_business_key(row) if row else None

    def get_business_by_email(self, email: str) -> dict | None:
        """Look up a business by email. Used by Stripe webhook to match payments."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM business_api_keys WHERE email = ? AND is_active = 1 ORDER BY created_at DESC LIMIT 1",
                (email,),
            ).fetchone()
            return _row_to_business_key(row) if row else None

    def get_business_by_id(self, business_id: int) -> dict | None:
        """Look up a business by primary key."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM business_api_keys WHERE id = ?",
                (business_id,),
            ).fetchone()
            return _row_to_business_key(row) if row else None

    def update_business_tier(
        self,
        business_id: int,
        tier: str,
        rate_limit: int | None = None,
        stripe_customer_id: str | None = None,
    ) -> bool:
        """
        Update a business key's tier and optionally its rate limit and Stripe ID.
        Returns True if the record was found and updated.
        """
        updates = ["tier = ?"]
        params: list = [tier]
        if rate_limit is not None:
            updates.append("rate_limit = ?")
            params.append(rate_limit)
        if stripe_customer_id is not None:
            updates.append("stripe_customer_id = ?")
            params.append(stripe_customer_id)
        params.append(business_id)
        with self._conn() as conn:
            result = conn.execute(
                f"UPDATE business_api_keys SET {', '.join(updates)} WHERE id = ?",
                params,
            )
            return result.rowcount > 0

    def deactivate_business_key(self, business_id: int) -> bool:
        """Deactivate a business API key. Returns True if found."""
        with self._conn() as conn:
            result = conn.execute(
                "UPDATE business_api_keys SET is_active = 0 WHERE id = ? AND is_active = 1",
                (business_id,),
            )
            return result.rowcount > 0

    # ── business_api_usage ─────────────────────────────────────────────────────

    def get_usage_window(self, key_hash: str, window_start: float) -> int:
        """Return request count for a given key in a given hour window. Returns 0 if no record."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT request_count FROM business_api_usage WHERE key_hash = ? AND window_start = ?",
                (key_hash, window_start),
            ).fetchone()
            return row["request_count"] if row else 0

    def increment_usage(self, key_hash: str, window_start: float) -> int:
        """
        Increment usage count for a key in the given hour window. Upserts.
        Returns the new count.
        """
        now = time.time()
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO business_api_usage (key_hash, window_start, request_count, updated_at)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(key_hash, window_start) DO UPDATE SET
                    request_count = request_count + 1,
                    updated_at = ?
                """,
                (key_hash, window_start, now, now),
            )
            row = conn.execute(
                "SELECT request_count FROM business_api_usage WHERE key_hash = ? AND window_start = ?",
                (key_hash, window_start),
            ).fetchone()
            return row["request_count"] if row else 1

    def prune_usage(self, max_age_hours: int = 48) -> int:
        """Delete usage records older than max_age_hours. Prevents unbounded growth."""
        cutoff = time.time() - (max_age_hours * 3600)
        with self._conn() as conn:
            result = conn.execute(
                "DELETE FROM business_api_usage WHERE window_start < ?",
                (cutoff,),
            )
            return result.rowcount


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
    registration_time   TEXT    NOT NULL,               -- ISO 8601 string (owned by agent_registry.py
                                                        --   for HMAC token derivation — must round-trip
                                                        --   exactly as stored)
    last_seen           REAL    NOT NULL,
    total_queries       INTEGER NOT NULL DEFAULT 0,
    incidents           INTEGER NOT NULL DEFAULT 0,
    trust_metadata      TEXT    DEFAULT NULL,           -- JSON: future trust scoring data
    deregistered_at     REAL    DEFAULT NULL            -- Unix epoch when deregistered. NULL = active.
);

CREATE INDEX IF NOT EXISTS idx_agent_registry_token_hash
    ON agent_registry(token_hash);

CREATE UNIQUE INDEX IF NOT EXISTS idx_agent_registry_name
    ON agent_registry(agent_name);


CREATE TABLE IF NOT EXISTS incident_reports (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id        INTEGER NOT NULL,
    agent_name      TEXT    NOT NULL,
    reporter        TEXT    NOT NULL,
    incident_type   TEXT    NOT NULL,
    description     TEXT    NOT NULL DEFAULT '',
    timestamp       REAL    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'accepted',   -- pending, accepted, rejected, duplicate
    severity        TEXT    NOT NULL DEFAULT 'standard',   -- critical, standard
    reviewed_at     REAL    DEFAULT NULL,                  -- when status changed from pending
    duplicate_of    INTEGER DEFAULT NULL,                  -- FK to incident_reports(id) for dedup chain
    FOREIGN KEY (agent_id) REFERENCES agent_registry(id)
);

CREATE INDEX IF NOT EXISTS idx_incident_reports_agent
    ON incident_reports(agent_id, timestamp DESC);


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


CREATE TABLE IF NOT EXISTS business_api_keys (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    key_hash            TEXT    NOT NULL UNIQUE,        -- SHA-256 hex, NOT the raw key
    business_name       TEXT    NOT NULL,
    email               TEXT    NOT NULL,
    tier                TEXT    NOT NULL DEFAULT 'free', -- 'free' or 'paid'
    rate_limit          INTEGER NOT NULL DEFAULT 100,    -- requests per hour
    stripe_customer_id  TEXT    DEFAULT NULL,
    created_at          REAL    NOT NULL,
    is_active           INTEGER NOT NULL DEFAULT 1       -- BOOLEAN: 0=false, 1=true
);

CREATE INDEX IF NOT EXISTS idx_business_api_keys_hash
    ON business_api_keys(key_hash);

CREATE INDEX IF NOT EXISTS idx_business_api_keys_email
    ON business_api_keys(email);


CREATE TABLE IF NOT EXISTS business_api_usage (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    key_hash            TEXT    NOT NULL,
    window_start        REAL    NOT NULL,               -- Unix epoch, aligned to hour
    request_count       INTEGER NOT NULL DEFAULT 0,
    updated_at          REAL    NOT NULL,
    UNIQUE(key_hash, window_start)
);

CREATE INDEX IF NOT EXISTS idx_business_api_usage_lookup
    ON business_api_usage(key_hash, window_start);
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
    result = {
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
    # deregistered_at may not exist in older schemas before migration
    try:
        result["deregistered_at"] = row["deregistered_at"]
    except (IndexError, KeyError):
        result["deregistered_at"] = None
    return result


def _row_to_incident_report(row: sqlite3.Row) -> dict:
    result = {
        "id": row["id"],
        "agent_id": row["agent_id"],
        "agent_name": row["agent_name"],
        "reporter": row["reporter"],
        "incident_type": row["incident_type"],
        "description": row["description"],
        "timestamp": row["timestamp"],
    }
    # Wave 3 fields — may not exist in older schemas
    for field, default in [("status", "accepted"), ("severity", "standard"), ("reviewed_at", None), ("duplicate_of", None)]:
        try:
            result[field] = row[field]
        except (IndexError, KeyError):
            result[field] = default
    return result


def _row_to_business_key(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "key_hash": row["key_hash"],
        "business_name": row["business_name"],
        "email": row["email"],
        "tier": row["tier"],
        "rate_limit": row["rate_limit"],
        "stripe_customer_id": row["stripe_customer_id"],
        "created_at": row["created_at"],
        "is_active": bool(row["is_active"]),
    }


def _row_to_event(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "timestamp": row["timestamp"],
        "event_type": row["event_type"],
        "data": json.loads(row["data"]),
        "privacy_mode_active": bool(row["privacy_mode_active"]),
    }
