"""
Submantle Business Registry — API key management for businesses.

Businesses are the customers. They register to get an API key, present it
when checking agent trust scores, and pay for higher rate limits.

Business keys are separate from agent tokens:
  - Agent tokens: HMAC-SHA256, used to accumulate trust history
  - Business keys: sk_live_ prefix, used to check trust scores

Design mirrors agent_registry.py but is simpler — no HMAC derivation,
just SHA-256 hash storage of a random key.
"""

import hashlib
import secrets
import time

from database import SubmantleDB
from events import EventBus, EventType

# Tier defaults — requests per hour
TIER_LIMITS = {
    "anonymous": 10,
    "free": 100,
    "paid": 1000,
}

KEY_PREFIX = "sk_live_"


class BusinessRegistry:
    """
    Manages business API keys for trust score lookups.

    Usage:
        registry = BusinessRegistry(db=db, event_bus=bus)
        raw_key = registry.register("Acme Corp", "api@acme.com")
        # raw_key is returned ONCE — business must save it
        biz = registry.verify(raw_key)
    """

    def __init__(self, db: SubmantleDB, event_bus: EventBus | None = None) -> None:
        self._db = db
        self._bus = event_bus

    def register(self, business_name: str, email: str) -> str:
        """
        Register a new business. Returns the raw API key exactly once.

        The raw key is never stored — only its SHA-256 hash is persisted.
        The business must save the key; it cannot be recovered.
        """
        if not business_name or not business_name.strip():
            raise ValueError("business_name is required")
        if not email or not email.strip():
            raise ValueError("email is required")

        raw_key = KEY_PREFIX + secrets.token_hex(32)
        key_hash = _hash_key(raw_key)
        rate_limit = TIER_LIMITS["free"]

        self._db.register_business_key(
            key_hash=key_hash,
            business_name=business_name.strip(),
            email=email.strip(),
            tier="free",
            rate_limit=rate_limit,
        )

        if self._bus:
            self._bus.emit(
                EventType.AGENT_REGISTERED,  # Reuse existing event type for now
                {"business_name": business_name, "tier": "free"},
            )

        return raw_key

    def verify(self, raw_key: str) -> dict | None:
        """
        Verify a raw API key. Returns the business record or None.

        Simpler than agent token verification — no HMAC re-derivation.
        Just hash the presented key and look it up.
        """
        if not raw_key or not raw_key.startswith(KEY_PREFIX):
            return None

        key_hash = _hash_key(raw_key)
        return self._db.get_business_by_key_hash(key_hash)

    def upgrade_to_paid(self, business_id: int, stripe_customer_id: str) -> bool:
        """
        Upgrade a business from free to paid tier.
        Called by the Stripe webhook after successful payment.
        """
        return self._db.update_business_tier(
            business_id=business_id,
            tier="paid",
            rate_limit=TIER_LIMITS["paid"],
            stripe_customer_id=stripe_customer_id,
        )


def _hash_key(raw_key: str) -> str:
    """SHA-256 hash of a raw API key. Deterministic, one-way."""
    return hashlib.sha256(raw_key.encode()).hexdigest()
