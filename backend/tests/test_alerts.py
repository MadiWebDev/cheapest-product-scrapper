import sys, pathlib
from datetime import datetime, timezone
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from app.priceintel.alerts_v2 import AlertService
from app.services.alerts import notify


def test_create_and_unsubscribe_token_flow():
    s = AlertService()
    a = s.create_alert("u1", "iphone 15", 300000, "email", "u@example.com")
    assert a["unsubscribe_token"]
    assert s.unsubscribe("wrong-token") is False
    assert s.unsubscribe(a["unsubscribe_token"]) is True
    ok, reason = s.should_notify(s.alerts[a["id"]], 250000)
    assert ok is False and reason == "inactive"


def test_quiet_hours_window():
    s = AlertService()
    a = s.create_alert("u1", "x", 10, quiet_start=23, quiet_end=7)
    rec = s.alerts[a["id"]]
    # 20:00 UTC = 01:00 Asia/Karachi (UTC+5) -> inside 23-07 window
    assert s.in_quiet_hours(rec, datetime(2026, 1, 1, 20, 0, tzinfo=timezone.utc)) is True
    # 10:00 UTC = 15:00 PKT -> outside
    assert s.in_quiet_hours(rec, datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)) is False
    b = s.create_alert("u1", "y", 10)
    assert s.in_quiet_hours(s.alerts[b["id"]], datetime(2026, 1, 1, 20, 0, tzinfo=timezone.utc)) is False


def test_dedupe_rules():
    s = AlertService()
    a = s.create_alert("u1", "iphone 15", 300000)
    rec = s.alerts[a["id"]]
    assert s.should_notify(rec, 350000)[0] is False  # above target
    assert s.should_notify(rec, 290000)[0] is True
    rec["last_notified_price"] = 290000
    rec["last_notified_at"] = 1_000_000
    assert s.should_notify(rec, 289000, now_ts=1_000_100)[0] is False  # <1% move within 24h
    assert s.should_notify(rec, 280000, now_ts=1_000_100)[0] is True   # >1% drop re-notifies
    assert s.should_notify(rec, 289000, now_ts=1_000_100 + 90000)[0] is True  # after 24h


def test_evaluate_delivery_honesty_without_smtp(monkeypatch):
    monkeypatch.delenv("SMTP_HOST", raising=False)
    s = AlertService()
    s.create_alert("u1", "iphone 15", 300000, "email", "u@example.com")
    out = s.evaluate("iphone 15", 250000)
    assert out[0]["sent"] is False
    assert out[0]["channel_result"]["reason"] == "SMTP not configured"
    # not marked as notified, so a later configured run can still send
    rec = list(s.alerts.values())[0]
    assert rec["last_notified_price"] is None


def test_watchlist_isolation_and_dedupe():
    s = AlertService()
    assert s.watch_add("u1", "prod-1")["added"] is True
    assert s.watch_add("u1", "prod-1")["added"] is False
    s.watch_add("u2", "prod-2")
    assert [i["product_ref"] for i in s.watch_list("u1")] == ["prod-1"]
    assert s.watch_remove("u1", "prod-1")["removed"] is True
    assert s.watch_list("u1") == [] and len(s.watch_list("u2")) == 1


def test_whatsapp_official_channel_blocked_without_credentials(monkeypatch):
    monkeypatch.delenv("WHATSAPP_CLOUD_TOKEN", raising=False)
    r = notify("whatsapp_official", "923001234567", "hi")
    assert r["sent"] is False and "not configured" in r["reason"]


def test_telegram_webhook_gating_and_commands(monkeypatch):
    monkeypatch.delenv("TELEGRAM_WEBHOOK_SECRET", raising=False)
    from fastapi.testclient import TestClient
    from app.main import app
    c = TestClient(app)
    assert c.post("/api/telegram/webhook", json={}).status_code == 503
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "s3cret")
    assert c.post("/api/telegram/webhook", json={}).status_code == 401
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    r = c.post("/api/telegram/webhook",
               json={"message": {"text": "/start", "chat": {"id": 42}}},
               headers={"x-telegram-bot-api-secret-token": "s3cret"})
    assert r.status_code == 200 and r.json()["ok"] is True
    # delivery honestly reports not_configured without a bot token
    assert r.json()["delivery"]["sent"] is False
