"""
Submantle Agent Registry — Identity and lifecycle management for registered agents.

Agents are external programs (AI assistants, automation scripts, monitoring
tools) that want to query Submantle. Registration gives them a verifiable token.
Submantle uses that token to know who is asking, track query patterns, and
(in future) build trust scores.

Design decisions:
- HMAC-SHA256 tokens using stdlib only (hmac + hashlib). No third-party crypto.
- Server secret is generated once on first run and stored in the settings table.
- Token = HMAC(secret, agent_name + ":" + iso_timestamp) encoded as hex.
  The separator ":" prevents concatenation ambiguity (e.g. "foo" + "bar:time"
  vs "foobar" + ":time").
- Token verification: Substrate re-derives the expected HMAC from stored data
  and uses hmac.compare_digest for timing-safe comparison.
- Trust scoring schema is captured but algorithm is deferred (future work).
- Agent registry works in BOTH privacy states — identity is not sensitive,
  activity is. Agents can still be looked up when Substrate is in PRIVATE mode.
- Capabilities stored as JSON array in the DB.

The token is the agent's bearer credential. Substrate does not store the raw
token — only the SHA-256 hash of it. This means a compromised DB leaks nothing
usable. Agents must keep their own token.

Interface note for Builder A (database.py):
  register_agent() must accept a registration_time parameter so the registry
  controls the canonical timestamp used in token derivation. Without this,
  HMAC re-derivation at verify time would use a DB-generated timestamp that
  differs from the one used to build the token.

  Expected signature:
      register_agent(agent_name, version, author, capabilities, token_hash,
                     registration_time: str) -> int
"""

import hashlib
import hmac
import json
import logging
import os
import secrets
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# Settings key for the server HMAC secret
_SECRET_SETTING_KEY = "agent_registry_secret"


def _now_iso() -> str:
    """UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def _token_hash(token: str) -> str:
    """SHA-256 hex digest of a token. Used for storage — never store the raw token."""
    return hashlib.sha256(token.encode()).hexdigest()


class AgentRegistry:
    """
    Manages the lifecycle of registered agents.

    Instantiate once at startup and share across components.
    Thread-safety: individual DB operations use sqlite3's built-in serialisation
    when using the same connection, and all state that lives in Python (the
    HMAC secret) is written once on init and then read-only.
    """

    def __init__(self, db=None, event_bus=None):
        """
        Args:
            db: SubstrateDB instance. If None, registry is not persisted
                (safe for testing).
            event_bus: EventBus instance. If None, events are not emitted.
        """
        self._db = db
        self._event_bus = event_bus
        self._secret = self._load_or_create_secret()

        logger.info("AgentRegistry initialized.")

    # ── Secret management ──────────────────────────────────────────────────────

    def _load_or_create_secret(self) -> bytes:
        """
        Load the HMAC secret from settings, or generate a new one.

        The secret is a 32-byte random value encoded as hex in the settings table.
        Generating on first run means Substrate doesn't require any config.
        """
        if self._db is not None:
            try:
                stored = self._db.get_setting(_SECRET_SETTING_KEY)
                if stored:
                    return bytes.fromhex(stored)
            except Exception as exc:
                logger.warning(
                    "Could not load agent registry secret from DB: %s. "
                    "Generating ephemeral secret — tokens won't survive restart.",
                    exc,
                )

        # Generate a new 32-byte secret
        new_secret = secrets.token_bytes(32)

        if self._db is not None:
            try:
                self._db.set_setting(_SECRET_SETTING_KEY, new_secret.hex())
                logger.info("Generated and stored new agent registry secret.")
            except Exception as exc:
                logger.error(
                    "Could not persist agent registry secret: %s. "
                    "Using ephemeral secret.",
                    exc,
                )

        return new_secret

    # ── Token construction ─────────────────────────────────────────────────────

    def _make_token(self, agent_name: str, timestamp: str) -> str:
        """
        Derive a fresh HMAC-SHA256 token.

        Token message: "agent_name:timestamp"
        The colon separator prevents name/timestamp ambiguity during verification.
        """
        message = f"{agent_name}:{timestamp}".encode()
        return hmac.new(self._secret, message, hashlib.sha256).hexdigest()

    def _verify_token_against_record(self, token: str, record: dict) -> bool:
        """
        Re-derive the expected token from stored data and compare.

        Uses hmac.compare_digest to prevent timing attacks.
        """
        expected = self._make_token(
            record["agent_name"], record["registration_time"]
        )
        return hmac.compare_digest(expected, token)

    # ── Public API ─────────────────────────────────────────────────────────────

    def register(
        self,
        agent_name: str,
        version: str,
        author: str,
        capabilities: list[str],
    ) -> str:
        """
        Register a new agent and return a bearer token.

        The token is the agent's only credential. Substrate does not store it —
        only its SHA-256 hash. The agent must preserve the token.

        Args:
            agent_name:   Unique identifier for the agent (e.g. "my-assistant").
            version:      Semantic version string (e.g. "1.0.0").
            author:       Author or publisher name.
            capabilities: List of capability strings the agent declares
                          (e.g. ["process_query", "device_list"]).

        Returns:
            The HMAC-SHA256 token (hex string) the agent will use for all
            subsequent calls.

        Raises:
            ValueError: If required fields are missing or empty.
        """
        # Validate inputs
        if not agent_name or not agent_name.strip():
            raise ValueError("agent_name is required")
        if not version or not version.strip():
            raise ValueError("version is required")
        if not author or not author.strip():
            raise ValueError("author is required")
        if not isinstance(capabilities, list):
            raise ValueError("capabilities must be a list")

        agent_name = agent_name.strip()
        version = version.strip()
        author = author.strip()

        # The registry owns the registration_time because the HMAC token is
        # derived from it. The DB stores what it's given — it does not generate
        # its own timestamp for this field. (See module docstring for rationale.)
        timestamp = _now_iso()
        token = self._make_token(agent_name, timestamp)
        t_hash = _token_hash(token)

        if self._db is not None:
            try:
                self._db.register_agent(
                    agent_name=agent_name,
                    version=version,
                    author=author,
                    capabilities=capabilities,
                    token_hash=t_hash,
                    registration_time=timestamp,
                )
            except Exception as exc:
                logger.error("Failed to persist agent registration: %s", exc)
                raise RuntimeError(
                    f"Registration failed — could not write to DB: {exc}"
                ) from exc

        logger.info(
            "Agent registered: name=%s version=%s author=%s capabilities=%s",
            agent_name,
            version,
            author,
            capabilities,
        )

        self._emit("AGENT_REGISTERED", {
            "agent_name": agent_name,
            "version": version,
            "author": author,
        })

        return token

    def verify(self, token: str) -> Optional[dict]:
        """
        Verify a token and return agent info, or None if invalid.

        Looks up the stored record by token hash, then re-derives the expected
        HMAC and compares with timing-safe comparison.

        Returns:
            dict with agent info if valid, or None.
        """
        if not token:
            return None

        t_hash = _token_hash(token)

        if self._db is not None:
            try:
                record = self._db.get_agent_by_token_hash(t_hash)
            except Exception as exc:
                logger.error("DB error during token verification: %s", exc)
                return None

            if record is None:
                return None

            if not self._verify_token_against_record(token, record):
                logger.warning(
                    "Token hash matched but HMAC verification failed for agent '%s'. "
                    "Possible token forge or DB tampering.",
                    record.get("agent_name"),
                )
                return None

            return record

        # No DB — ephemeral mode: we cannot verify (we have no stored records)
        return None

    def list_agents(self) -> list[dict]:
        """
        Return all registered agents.

        Token hashes are NOT included in the output — only safe metadata.
        """
        if self._db is None:
            return []

        try:
            records = self._db.list_agents()
        except Exception as exc:
            logger.error("Failed to list agents: %s", exc)
            return []

        # Strip token_hash before returning — callers don't need it
        return [
            {k: v for k, v in r.items() if k != "token_hash"}
            for r in records
        ]

    def deregister(self, token: str) -> bool:
        """
        Remove a registered agent. Token must be valid.

        Returns True if the agent was found and removed, False otherwise.
        """
        if not token:
            return False

        # Verify before deregistering — prevents unauthenticated deletions
        agent_info = self.verify(token)
        if agent_info is None:
            logger.warning("Deregister attempted with invalid token.")
            return False

        agent_id = agent_info.get("id")
        agent_name = agent_info.get("agent_name")

        if self._db is not None:
            try:
                removed = self._db.deregister_agent(agent_id)
            except Exception as exc:
                logger.error(
                    "Failed to remove agent '%s' from DB: %s", agent_name, exc
                )
                return False

            if removed:
                logger.info("Agent deregistered: name=%s id=%s", agent_name, agent_id)
                self._emit("AGENT_DEREGISTERED", {"agent_name": agent_name, "agent_id": agent_id})

            return removed

        return False

    def record_query(self, token: str) -> bool:
        """
        Record that an agent made a query. Updates last_seen and total_queries.

        Returns True if the agent was found and updated, False if token is invalid.
        This is called by the API layer on every authenticated agent request.
        """
        agent_info = self.verify(token)
        if agent_info is None:
            return False

        agent_id = agent_info.get("id")

        if self._db is not None:
            try:
                self._db.update_agent_last_seen(agent_id)
                self._db.increment_agent_queries(agent_id)
            except Exception as exc:
                logger.warning(
                    "Failed to update query stats for agent id=%s: %s", agent_id, exc
                )

        return True

    # ── Internals ──────────────────────────────────────────────────────────────

    def _emit(self, event_type: str, data: dict) -> None:
        """Emit an event if an event bus is configured. Silent on failure."""
        if self._event_bus is None:
            return
        try:
            self._event_bus.emit(event_type, data, source="AgentRegistry")
        except Exception as exc:
            logger.warning("Failed to emit %s event: %s", event_type, exc)

    def __repr__(self) -> str:
        return "AgentRegistry()"
