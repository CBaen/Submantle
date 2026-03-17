"""
Tests for Business Registry — API key management for businesses.

Mirrors the approach in test_agent_registry.py: real :memory: SQLite DB,
no mocks for the database layer.
"""

import unittest
from database import SubmantleDB
from business_registry import BusinessRegistry, KEY_PREFIX, TIER_LIMITS, _hash_key


class TestBusinessRegistry(unittest.TestCase):
    """Unit tests for BusinessRegistry key generation and verification."""

    def setUp(self):
        self.db = SubmantleDB(":memory:")
        self.registry = BusinessRegistry(db=self.db)

    def tearDown(self):
        self.db.close()

    def test_register_returns_prefixed_key(self):
        key = self.registry.register("Acme Corp", "api@acme.com")
        self.assertTrue(key.startswith(KEY_PREFIX))

    def test_register_key_has_correct_length(self):
        key = self.registry.register("Acme Corp", "api@acme.com")
        suffix = key.removeprefix(KEY_PREFIX)
        self.assertEqual(len(suffix), 64)  # 32 bytes = 64 hex chars

    def test_register_stores_hash_not_raw_key(self):
        key = self.registry.register("Acme Corp", "api@acme.com")
        key_hash = _hash_key(key)
        record = self.db.get_business_by_key_hash(key_hash)
        self.assertIsNotNone(record)
        self.assertNotEqual(record["key_hash"], key)  # hash, not raw

    def test_verify_valid_key_returns_business(self):
        key = self.registry.register("Acme Corp", "api@acme.com")
        result = self.registry.verify(key)
        self.assertIsNotNone(result)
        self.assertEqual(result["business_name"], "Acme Corp")
        self.assertEqual(result["email"], "api@acme.com")
        self.assertEqual(result["tier"], "free")

    def test_verify_invalid_key_returns_none(self):
        result = self.registry.verify("sk_live_invalidkey123")
        self.assertIsNone(result)

    def test_verify_no_prefix_returns_none(self):
        result = self.registry.verify("not_a_key")
        self.assertIsNone(result)

    def test_verify_empty_returns_none(self):
        result = self.registry.verify("")
        self.assertIsNone(result)

    def test_register_default_tier_is_free(self):
        key = self.registry.register("Acme Corp", "api@acme.com")
        result = self.registry.verify(key)
        self.assertEqual(result["tier"], "free")
        self.assertEqual(result["rate_limit"], TIER_LIMITS["free"])

    def test_upgrade_to_paid(self):
        key = self.registry.register("Acme Corp", "api@acme.com")
        biz = self.registry.verify(key)
        self.registry.upgrade_to_paid(biz["id"], "cus_stripe123")
        updated = self.registry.verify(key)
        self.assertEqual(updated["tier"], "paid")
        self.assertEqual(updated["rate_limit"], TIER_LIMITS["paid"])
        self.assertEqual(updated["stripe_customer_id"], "cus_stripe123")

    def test_deactivate_key(self):
        key = self.registry.register("Acme Corp", "api@acme.com")
        biz = self.registry.verify(key)
        self.db.deactivate_business_key(biz["id"])
        result = self.registry.verify(key)
        # verify() still returns the record (hash lookup works)
        # but is_active will be False — caller checks this
        self.assertIsNotNone(result)
        self.assertFalse(result["is_active"])

    def test_duplicate_email_allowed(self):
        key1 = self.registry.register("Acme Corp", "api@acme.com")
        key2 = self.registry.register("Acme Labs", "api@acme.com")
        self.assertNotEqual(key1, key2)
        biz1 = self.registry.verify(key1)
        biz2 = self.registry.verify(key2)
        self.assertIsNotNone(biz1)
        self.assertIsNotNone(biz2)

    def test_register_empty_name_raises(self):
        with self.assertRaises(ValueError):
            self.registry.register("", "api@acme.com")

    def test_register_empty_email_raises(self):
        with self.assertRaises(ValueError):
            self.registry.register("Acme Corp", "")

    def test_each_key_is_unique(self):
        keys = set()
        for i in range(10):
            key = self.registry.register(f"Business {i}", f"b{i}@test.com")
            keys.add(key)
        self.assertEqual(len(keys), 10)

    def test_get_business_by_email(self):
        self.registry.register("Acme Corp", "api@acme.com")
        result = self.db.get_business_by_email("api@acme.com")
        self.assertIsNotNone(result)
        self.assertEqual(result["business_name"], "Acme Corp")

    def test_get_business_by_email_not_found(self):
        result = self.db.get_business_by_email("nobody@nowhere.com")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
