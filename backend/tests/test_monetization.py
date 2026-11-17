import sys, pathlib, os, json, time, hmac, hashlib
os.environ["DEMO_MODE"] = "true"
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
import importlib
import app.connectors.registry as reg
importlib.reload(reg)
import app.services.search as ss
ss.REGISTRY = reg.REGISTRY

from app.priceintel.affiliate import ConversionLedger, is_bot_ua, resolve_tag
from app.priceintel.billing import PaddleBillingProvider
from app.priceintel import sponsored


def test_tag_resolution_prefers_country(monkeypatch):
    monkeypatch.setenv("AFFILIATE_TAG_AMAZON", "global-20")
    monkeypatch.setenv("AFFILIATE_TAG_AMAZON_PK", "pk-20")
    monkeypatch.delenv("AFFILIATE_TAG_DEFAULT", raising=False)
    assert resolve_tag("amazon", "PK") == "pk-20"
    assert resolve_tag("amazon", "US") == "global-20"
    monkeypatch.delenv("AFFILIATE_TAG_AMAZON")
    monkeypatch.delenv("AFFILIATE_TAG_AMAZON_PK")
    assert resolve_tag("amazon", "PK") is None


def test_bot_filtering():
    assert is_bot_ua("Mozilla/5.0 (compatible; Googlebot/2.1)")
    assert is_bot_ua("curl/8.0")
    assert not is_bot_ua("Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120")


def test_conversion_ledger_dedupes_and_separates():
    led = ConversionLedger()
    assert led.add("ext-1", "amazon", 12.5) is True
    assert led.add("ext-1", "amazon", 12.5) is False  # duplicate ignored
    assert led.totals() == {"amazon": 12.5}


def _sign(secret: str, body: bytes, ts: int) -> str:
    h = hmac.new(secret.encode(), str(ts).encode() + b":" + body, hashlib.sha256).hexdigest()
    return f"ts={ts};h1={h}"


def test_paddle_webhook_signature_verification():
    p = PaddleBillingProvider(webhook_secret="whsec_test")
    body = json.dumps({"event_id": "evt_1", "event_type": "subscription.created",
                       "data": {"customer_id": "cus_1", "status": "active", "items": [{"price_id": "pri_pro"}]}}).encode()
    good = _sign("whsec_test", body, int(time.time()))
    assert p.verify_webhook(body, good) is True
    assert p.verify_webhook(body, _sign("wrong-secret", body, int(time.time()))) is False
    assert p.verify_webhook(body + b" ", good) is False  # tampered body
    assert p.verify_webhook(body, _sign("whsec_test", body, int(time.time()) - 10000)) is False  # stale ts
    assert p.verify_webhook(body, "") is False


def test_paddle_event_idempotency_and_subscription_state():
    p = PaddleBillingProvider(webhook_secret="x")
    ev = {"event_id": "evt_9", "event_type": "subscription.created",
          "data": {"customer_id": "cus_9", "status": "active", "items": [{"price_id": "pri_pro"}]}}
    assert p.handle_event(ev)["processed"] is True
    assert p.handle_event(ev)["duplicate"] is True
    assert p.subscriptions["cus_9"]["status"] == "active"
    ev2 = {"event_id": "evt_10", "event_type": "subscription.canceled",
           "data": {"customer_id": "cus_9", "status": "canceled", "items": [{"price_id": "pri_pro"}]}}
    p.handle_event(ev2)
    assert p.subscriptions["cus_9"]["status"] == "canceled"


def test_checkout_not_configured_is_honest(monkeypatch):
    monkeypatch.delenv("PADDLE_API_KEY", raising=False)
    p = PaddleBillingProvider(api_key="")
    out = p.create_checkout("pro", "user-1")
    assert out["mode"] == "not_configured" and "error" in out
    assert p.create_checkout("nope", "user-1")["error"].startswith("unknown plan")


def test_sponsored_never_mixed_into_organic():
    sponsored.clear()
    sponsored.register_sponsored({"title": "iPhone 15 Pro Max Sponsored Deal", "url": "https://ads.example/x",
                                  "price": 1.0, "currency": "PKR", "campaign": "launch"})
    r = ss.search("iphone 15", {}, "PK", "PKR", connectors=["demo"])
    organic_urls = [o["offer"]["url"] for p in r["products"] for o in p["offers"]]
    assert "https://ads.example/x" not in organic_urls
    assert len(r["sponsored"]) == 1 and r["sponsored"][0]["label"] == "Sponsored"
    sponsored.clear()


def test_revenue_report_keeps_estimated_and_confirmed_separate(monkeypatch):
    from app.priceintel.affiliate import revenue_report
    rep = revenue_report()
    assert "estimated" in rep and "confirmed" in rep
    assert "total_revenue" not in rep  # never summed into one number
