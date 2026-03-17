"""
Integration tests for Wave 11: Business API Keys + Rate Limiting + Stripe.

These are the first HTTP-layer tests in the project, using FastAPI's TestClient.
They test the full stack: HTTP request → business auth → rate limiting → response.
"""

import json
import os
import unittest
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient


class TestBusinessEndpoints(unittest.TestCase):
    """Test business registration and tier info endpoints."""

    def setUp(self):
        # Import api after patching to get a fresh app with :memory: DB
        # We need to patch the DB before api.py initializes its module-level objects
        from database import SubmantleDB
        self._mem_db = SubmantleDB(":memory:")

        import api as api_module
        # Replace module-level objects with test instances
        self._orig_db = api_module._db
        self._orig_bus = api_module._bus
        self._orig_registry = api_module._registry
        self._orig_business = api_module._business_registry
        self._orig_limiter = api_module._rate_limiter

        from events import EventBus
        from agent_registry import AgentRegistry
        from business_registry import BusinessRegistry
        from rate_limiter import RateLimiter

        api_module._db = self._mem_db
        api_module._bus = EventBus(db=self._mem_db)
        api_module._registry = AgentRegistry(db=self._mem_db, event_bus=api_module._bus)
        api_module._business_registry = BusinessRegistry(db=self._mem_db, event_bus=api_module._bus)
        api_module._rate_limiter = RateLimiter(db=self._mem_db)

        self.client = TestClient(api_module.app)

    def tearDown(self):
        import api as api_module
        api_module._db = self._orig_db
        api_module._bus = self._orig_bus
        api_module._registry = self._orig_registry
        api_module._business_registry = self._orig_business
        api_module._rate_limiter = self._orig_limiter
        self._mem_db.close()

    def test_register_business_returns_api_key(self):
        resp = self.client.post("/api/business/register", json={
            "business_name": "Acme Corp",
            "email": "api@acme.com",
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["api_key"].startswith("sk_live_"))
        self.assertEqual(data["tier"], "free")
        self.assertEqual(data["rate_limit"], 100)

    def test_register_business_missing_fields(self):
        resp = self.client.post("/api/business/register", json={
            "business_name": "Acme Corp",
        })
        self.assertEqual(resp.status_code, 422)

    def test_register_business_empty_name(self):
        resp = self.client.post("/api/business/register", json={
            "business_name": "",
            "email": "api@acme.com",
        })
        self.assertEqual(resp.status_code, 422)

    def test_tiers_endpoint(self):
        resp = self.client.get("/api/business/tiers")
        self.assertEqual(resp.status_code, 200)
        tiers = resp.json()["tiers"]
        self.assertEqual(len(tiers), 3)
        names = [t["name"] for t in tiers]
        self.assertIn("anonymous", names)
        self.assertIn("free", names)
        self.assertIn("paid", names)


class TestVerifyWithRateLimiting(unittest.TestCase):
    """Test verify endpoints with business auth and rate limiting."""

    def setUp(self):
        from database import SubmantleDB
        self._mem_db = SubmantleDB(":memory:")

        import api as api_module
        self._orig_db = api_module._db
        self._orig_bus = api_module._bus
        self._orig_registry = api_module._registry
        self._orig_business = api_module._business_registry
        self._orig_limiter = api_module._rate_limiter

        from events import EventBus
        from agent_registry import AgentRegistry
        from business_registry import BusinessRegistry
        from rate_limiter import RateLimiter

        api_module._db = self._mem_db
        api_module._bus = EventBus(db=self._mem_db)
        api_module._registry = AgentRegistry(db=self._mem_db, event_bus=api_module._bus)
        api_module._business_registry = BusinessRegistry(db=self._mem_db, event_bus=api_module._bus)
        api_module._rate_limiter = RateLimiter(db=self._mem_db)

        self.client = TestClient(api_module.app)

        # Register a test agent so verify endpoints have something to return
        api_module._registry.register(
            agent_name="test-agent",
            version="1.0.0",
            author="tester",
            capabilities=["test"],
        )

    def tearDown(self):
        import api as api_module
        api_module._db = self._orig_db
        api_module._bus = self._orig_bus
        api_module._registry = self._orig_registry
        api_module._business_registry = self._orig_business
        api_module._rate_limiter = self._orig_limiter
        self._mem_db.close()

    def test_verify_anonymous_allowed(self):
        resp = self.client.get("/api/verify")
        self.assertEqual(resp.status_code, 200)

    def test_verify_anonymous_has_ratelimit_headers(self):
        resp = self.client.get("/api/verify")
        self.assertIn("x-ratelimit-limit", resp.headers)
        self.assertIn("x-ratelimit-remaining", resp.headers)
        self.assertIn("x-ratelimit-reset", resp.headers)
        self.assertEqual(resp.headers["x-ratelimit-limit"], "10")

    def test_verify_with_valid_key(self):
        # Register a business
        reg_resp = self.client.post("/api/business/register", json={
            "business_name": "Acme Corp",
            "email": "api@acme.com",
        })
        api_key = reg_resp.json()["api_key"]

        # Use the key
        resp = self.client.get("/api/verify", headers={"X-API-Key": api_key})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers["x-ratelimit-limit"], "100")

    def test_verify_with_invalid_key(self):
        resp = self.client.get("/api/verify", headers={"X-API-Key": "sk_live_invalid"})
        self.assertEqual(resp.status_code, 401)

    def test_verify_agent_with_key(self):
        reg_resp = self.client.post("/api/business/register", json={
            "business_name": "Acme Corp",
            "email": "api@acme.com",
        })
        api_key = reg_resp.json()["api_key"]

        resp = self.client.get("/api/verify/test-agent", headers={"X-API-Key": api_key})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["agent_name"], "test-agent")

    def test_verify_agent_not_found(self):
        resp = self.client.get("/api/verify/nonexistent")
        self.assertEqual(resp.status_code, 404)

    def test_anonymous_rate_limit_exceeded(self):
        # Anonymous limit is 10/hour
        for i in range(10):
            resp = self.client.get("/api/verify")
            self.assertEqual(resp.status_code, 200, f"Request {i+1} should succeed")

        # 11th should be blocked
        resp = self.client.get("/api/verify")
        self.assertEqual(resp.status_code, 429)

    def test_free_tier_rate_limit_higher_than_anonymous(self):
        reg_resp = self.client.post("/api/business/register", json={
            "business_name": "Acme Corp",
            "email": "api@acme.com",
        })
        api_key = reg_resp.json()["api_key"]

        # Should allow at least 11 requests (more than anonymous 10)
        for i in range(11):
            resp = self.client.get("/api/verify", headers={"X-API-Key": api_key})
            self.assertEqual(resp.status_code, 200, f"Request {i+1} should succeed with free key")

    def test_deactivated_key_returns_403(self):
        reg_resp = self.client.post("/api/business/register", json={
            "business_name": "Acme Corp",
            "email": "api@acme.com",
        })
        api_key = reg_resp.json()["api_key"]

        # Deactivate the key
        import api as api_module
        biz = api_module._business_registry.verify(api_key)
        api_module._db.deactivate_business_key(biz["id"])

        resp = self.client.get("/api/verify", headers={"X-API-Key": api_key})
        self.assertEqual(resp.status_code, 403)


class TestStripeWebhook(unittest.TestCase):
    """Test Stripe webhook endpoint."""

    def setUp(self):
        from database import SubmantleDB
        self._mem_db = SubmantleDB(":memory:")

        import api as api_module
        self._orig_db = api_module._db
        self._orig_bus = api_module._bus
        self._orig_registry = api_module._registry
        self._orig_business = api_module._business_registry
        self._orig_limiter = api_module._rate_limiter

        from events import EventBus
        from agent_registry import AgentRegistry
        from business_registry import BusinessRegistry
        from rate_limiter import RateLimiter

        api_module._db = self._mem_db
        api_module._bus = EventBus(db=self._mem_db)
        api_module._registry = AgentRegistry(db=self._mem_db, event_bus=api_module._bus)
        api_module._business_registry = BusinessRegistry(db=self._mem_db, event_bus=api_module._bus)
        api_module._rate_limiter = RateLimiter(db=self._mem_db)

        self.client = TestClient(api_module.app)

    def tearDown(self):
        import api as api_module
        api_module._db = self._orig_db
        api_module._bus = self._orig_bus
        api_module._registry = self._orig_registry
        api_module._business_registry = self._orig_business
        api_module._rate_limiter = self._orig_limiter
        self._mem_db.close()

    def test_webhook_no_secret_returns_503(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("STRIPE_WEBHOOK_SECRET", None)
            resp = self.client.post("/api/stripe/webhook", content=b"test")
            self.assertEqual(resp.status_code, 503)

    def test_webhook_missing_signature_returns_400(self):
        with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test123"}):
            resp = self.client.post("/api/stripe/webhook", content=b"test")
            self.assertEqual(resp.status_code, 400)

    @patch("api.stripe")
    def test_webhook_checkout_upgrades_business(self, mock_stripe_module):
        """Simulate a Stripe checkout.session.completed event."""
        import api as api_module

        # Register a business
        api_module._business_registry.register("Acme Corp", "api@acme.com")
        biz_before = api_module._db.get_business_by_email("api@acme.com")
        self.assertEqual(biz_before["tier"], "free")

        # Mock Stripe webhook verification
        mock_event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer_details": {"email": "api@acme.com"},
                    "customer": "cus_stripe_123",
                }
            }
        }
        mock_stripe_module.Webhook.construct_event.return_value = mock_event

        with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test123"}):
            resp = self.client.post(
                "/api/stripe/webhook",
                content=b'{"test": true}',
                headers={"stripe-signature": "t=123,v1=abc"},
            )

        self.assertEqual(resp.status_code, 200)

        # Verify tier was upgraded
        biz_after = api_module._db.get_business_by_email("api@acme.com")
        self.assertEqual(biz_after["tier"], "paid")
        self.assertEqual(biz_after["rate_limit"], 1000)


if __name__ == "__main__":
    unittest.main()
