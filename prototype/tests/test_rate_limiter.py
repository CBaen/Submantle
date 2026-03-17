"""
Tests for Rate Limiter — hourly sliding window per caller.

Uses real :memory: SQLite for the persistence layer.
"""

import time
import unittest
from unittest.mock import patch

from database import SubmantleDB
from rate_limiter import RateLimiter, hash_ip, _align_to_hour


class TestRateLimiter(unittest.TestCase):
    """Unit tests for the hourly rate limiter."""

    def setUp(self):
        self.db = SubmantleDB(":memory:")
        self.limiter = RateLimiter(db=self.db)

    def tearDown(self):
        self.db.close()

    def test_first_request_allowed(self):
        result = self.limiter.check_and_increment("caller_a", limit=10)
        self.assertTrue(result.allowed)
        self.assertEqual(result.remaining, 9)

    def test_requests_up_to_limit_allowed(self):
        for i in range(9):
            result = self.limiter.check_and_increment("caller_a", limit=10)
            self.assertTrue(result.allowed)
        # 10th request — last one allowed
        result = self.limiter.check_and_increment("caller_a", limit=10)
        self.assertTrue(result.allowed)
        self.assertEqual(result.remaining, 0)

    def test_request_over_limit_blocked(self):
        for _ in range(10):
            self.limiter.check_and_increment("caller_a", limit=10)
        # 11th request — blocked
        result = self.limiter.check_and_increment("caller_a", limit=10)
        self.assertFalse(result.allowed)
        self.assertEqual(result.remaining, 0)

    def test_different_callers_independent(self):
        # Exhaust caller_a's limit
        for _ in range(10):
            self.limiter.check_and_increment("caller_a", limit=10)
        blocked = self.limiter.check_and_increment("caller_a", limit=10)
        self.assertFalse(blocked.allowed)

        # caller_b should still be fine
        result = self.limiter.check_and_increment("caller_b", limit=10)
        self.assertTrue(result.allowed)

    def test_window_reset_allows_new_requests(self):
        # Exhaust limit in current window
        for _ in range(10):
            self.limiter.check_and_increment("caller_a", limit=10)
        blocked = self.limiter.check_and_increment("caller_a", limit=10)
        self.assertFalse(blocked.allowed)

        # Advance time to next hour window
        future = time.time() + 3601
        with patch("rate_limiter.time") as mock_time, \
             patch("database.time") as mock_db_time:
            mock_time.time.return_value = future
            mock_db_time.time.return_value = future
            # Create a fresh limiter to avoid stale cache
            fresh_limiter = RateLimiter(db=self.db)
            result = fresh_limiter.check_and_increment("caller_a", limit=10)
            self.assertTrue(result.allowed)

    def test_remaining_decrements(self):
        r1 = self.limiter.check_and_increment("caller_a", limit=5)
        self.assertEqual(r1.remaining, 4)
        r2 = self.limiter.check_and_increment("caller_a", limit=5)
        self.assertEqual(r2.remaining, 3)
        r3 = self.limiter.check_and_increment("caller_a", limit=5)
        self.assertEqual(r3.remaining, 2)

    def test_reset_time_is_future(self):
        result = self.limiter.check_and_increment("caller_a", limit=10)
        self.assertGreater(result.reset_at, time.time())

    def test_limit_field_matches_input(self):
        result = self.limiter.check_and_increment("caller_a", limit=42)
        self.assertEqual(result.limit, 42)

    def test_persistence_across_limiter_instances(self):
        # Use 5 requests
        for _ in range(5):
            self.limiter.check_and_increment("caller_a", limit=10)

        # Create new limiter (simulating restart) — same DB
        new_limiter = RateLimiter(db=self.db)
        result = new_limiter.check_and_increment("caller_a", limit=10)
        self.assertTrue(result.allowed)
        # Should have 4 remaining (5 used + 1 just used = 6 total)
        self.assertEqual(result.remaining, 4)


class TestRateLimiterHelpers(unittest.TestCase):
    """Tests for helper functions."""

    def test_hash_ip_deterministic(self):
        h1 = hash_ip("192.168.1.1")
        h2 = hash_ip("192.168.1.1")
        self.assertEqual(h1, h2)

    def test_hash_ip_different_ips_different_hashes(self):
        h1 = hash_ip("192.168.1.1")
        h2 = hash_ip("192.168.1.2")
        self.assertNotEqual(h1, h2)

    def test_align_to_hour(self):
        # 2026-01-01 00:30:00 UTC = 1767225000
        aligned = _align_to_hour(1767225000)
        # Should be 2026-01-01 00:00:00 UTC = 1767225000 - 1800 = 1767223200
        self.assertEqual(aligned % 3600, 0)
        self.assertLessEqual(aligned, 1767225000)
        self.assertGreater(aligned + 3600, 1767225000)


if __name__ == "__main__":
    unittest.main()
