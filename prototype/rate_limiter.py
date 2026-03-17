"""
Submantle Rate Limiter — hourly sliding window per caller.

In-memory dict as primary store (fast), SQLite as backup (survives restarts).
Anonymous callers are identified by hashed IP. Keyed callers by key hash.

Window alignment: requests are bucketed into clock-aligned hours.
  window_start = floor(now / 3600) * 3600
This is simpler than rolling windows and trivially stored in SQLite.
"""

import hashlib
import math
import time
from dataclasses import dataclass

from database import SubmantleDB


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""
    allowed: bool
    limit: int
    remaining: int
    reset_at: float  # Unix epoch when the current window expires


class RateLimiter:
    """
    Hourly rate limiter with in-memory cache and SQLite persistence.

    Usage:
        limiter = RateLimiter(db=db)
        result = limiter.check_and_increment("some_identifier", limit=100)
        if not result.allowed:
            # Return 429
    """

    def __init__(self, db: SubmantleDB) -> None:
        self._db = db
        self._cache: dict[str, dict] = {}
        # key: identifier (key_hash or hashed IP)
        # value: {"window_start": float, "count": int}

    def check_and_increment(self, identifier: str, limit: int) -> RateLimitResult:
        """
        Check if the caller is within their rate limit and increment the counter.

        Args:
            identifier: key_hash for keyed callers, hashed IP for anonymous
            limit: maximum requests per hour for this caller

        Returns:
            RateLimitResult with allowed status and standard rate limit metadata
        """
        now = time.time()
        window_start = _align_to_hour(now)
        reset_at = window_start + 3600

        # Check in-memory cache
        cached = self._cache.get(identifier)
        if cached and cached["window_start"] == window_start:
            count = cached["count"]
        else:
            # Cache miss or window rolled over — reload from SQLite
            count = self._db.get_usage_window(identifier, window_start)
            self._cache[identifier] = {"window_start": window_start, "count": count}

        # Check limit
        if count >= limit:
            return RateLimitResult(
                allowed=False,
                limit=limit,
                remaining=0,
                reset_at=reset_at,
            )

        # Increment
        new_count = count + 1
        self._cache[identifier] = {"window_start": window_start, "count": new_count}
        self._db.increment_usage(identifier, window_start)

        # Evict stale cache entries (from prior windows)
        self._evict_stale(window_start)

        return RateLimitResult(
            allowed=True,
            limit=limit,
            remaining=max(0, limit - new_count),
            reset_at=reset_at,
        )

    def _evict_stale(self, current_window: float) -> None:
        """Remove cache entries from prior windows to prevent memory growth."""
        stale = [k for k, v in self._cache.items() if v["window_start"] < current_window]
        for k in stale:
            del self._cache[k]


def _align_to_hour(timestamp: float) -> float:
    """Align a Unix timestamp to the start of its hour."""
    return math.floor(timestamp / 3600) * 3600


def hash_ip(ip: str) -> str:
    """Hash an IP address for anonymous rate limiting. Privacy: never store raw IPs."""
    return hashlib.sha256(ip.encode()).hexdigest()
