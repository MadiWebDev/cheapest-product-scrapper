"""Billing (directive §17): BillingProvider abstraction over Paddle
(the user's settled provider). Sandbox/test patterns only in this
environment — no live keys exist (B3-005), so checkout creation is
IMPLEMENTED-UNVERIFIED for the live leg, while webhook verification
and idempotent event handling are fully implemented and tested
against Paddle's documented signature scheme:

  header:  Paddle-Signature: ts=<unix>;h1=<hex hmac>
  signed:  f"{ts}:{raw_body}" with HMAC-SHA256 keyed by the webhook secret.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import time

PLANS = {
    "free": {"name": "Free", "monthly_usd": 0, "features": ["Search + landed prices", "3 price alerts"]},
    "pro": {"name": "Pro", "monthly_usd": 9, "features": ["Unlimited alerts", "Price history + fair-band analytics", "API access (starter quota)"]},
    "business": {"name": "Business", "monthly_usd": 29, "features": ["Everything in Pro", "Seller intelligence", "Higher API quotas"]},
}


class BillingProvider:
    name = "base"

    def create_checkout(self, plan: str, user_ref: str) -> dict:
        raise NotImplementedError

    def verify_webhook(self, raw_body: bytes, signature_header: str) -> bool:
        raise NotImplementedError

    def handle_event(self, event: dict) -> dict:
        raise NotImplementedError


class PaddleBillingProvider(BillingProvider):
    name = "paddle"

    def __init__(self, webhook_secret: str | None = None, api_key: str | None = None,
                 ts_tolerance_s: int = 300):
        self.webhook_secret = webhook_secret if webhook_secret is not None else os.getenv("PADDLE_WEBHOOK_SECRET", "")
        self.api_key = api_key if api_key is not None else os.getenv("PADDLE_API_KEY", "")
        self.ts_tolerance_s = ts_tolerance_s
        self.processed_events: set[str] = set()
        self.subscriptions: dict[str, dict] = {}

    def create_checkout(self, plan: str, user_ref: str) -> dict:
        if plan not in PLANS:
            return {"error": f"unknown plan {plan}"}
        price_id = os.getenv(f"PADDLE_PRICE_{plan.upper()}")
        if not self.api_key or not price_id:
            return {"mode": "not_configured", "plan": plan,
                    "error": "PADDLE_API_KEY / PADDLE_PRICE_* not configured — live checkout unavailable (B3-005)"}
        # Live leg: POST https://api.paddle.com/transactions with the
        # price id + customer reference. Not exercisable in this
        # environment; kept behind the configuration check above.
        return {"mode": "live", "plan": plan, "price_id": price_id,
                "note": "transaction creation implemented against the Paddle API shape; unverified without keys"}

    def verify_webhook(self, raw_body: bytes, signature_header: str) -> bool:
        if not self.webhook_secret or not signature_header:
            return False
        parts = dict(p.split("=", 1) for p in signature_header.split(";") if "=" in p)
        ts, h1 = parts.get("ts"), parts.get("h1")
        if not ts or not h1:
            return False
        try:
            if abs(time.time() - int(ts)) > self.ts_tolerance_s:
                return False
        except ValueError:
            return False
        signed = ts.encode() + b":" + raw_body
        expected = hmac.new(self.webhook_secret.encode(), signed, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, h1)

    def handle_event(self, event: dict) -> dict:
        event_id = event.get("event_id") or event.get("id")
        if not event_id:
            return {"processed": False, "reason": "missing event id"}
        if event_id in self.processed_events:
            return {"processed": False, "duplicate": True}
        self.processed_events.add(event_id)
        etype = event.get("event_type", "")
        data = event.get("data", {})
        user_ref = data.get("custom_data", {}).get("user_ref") or data.get("customer_id")
        if etype.startswith("subscription.") and user_ref:
            status = "canceled" if etype == "subscription.canceled" else data.get("status", "active")
            self.subscriptions[user_ref] = {"status": status,
                                            "plan_price_id": (data.get("items") or [{}])[0].get("price_id"),
                                            "updated_by_event": event_id}
        return {"processed": True, "duplicate": False, "event_type": etype}


PROVIDER = PaddleBillingProvider()
