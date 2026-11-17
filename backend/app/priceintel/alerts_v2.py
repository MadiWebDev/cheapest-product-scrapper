"""Alerts + watchlists v3 (directive §15): quiet hours, dedupe,
one-click unsubscribe tokens, honest channel gating.

Delivery goes through the v1 notify() service, which sends for real
when SMTP/Telegram env is configured and otherwise returns an explicit
not_configured — a notification is never recorded as sent unless the
channel confirms it.
"""
from __future__ import annotations

import hashlib
import secrets
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.services.alerts import notify


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class AlertService:
    def __init__(self) -> None:
        self.alerts: dict[str, dict] = {}
        self.watchlists: dict[str, list[dict]] = {}

    # --- alerts ------------------------------------------------------
    def create_alert(self, user_ref: str, query: str, target_price: float,
                     channel: str = "email", destination: str = "",
                     quiet_start: int | None = None, quiet_end: int | None = None,
                     tz: str = "Asia/Karachi") -> dict:
        aid = secrets.token_hex(8)
        token = secrets.token_urlsafe(24)
        rec = {"id": aid, "user_ref": user_ref, "query": query,
               "target_price": target_price, "channel": channel,
               "destination": destination, "quiet_start": quiet_start,
               "quiet_end": quiet_end, "tz": tz, "active": True,
               "created_at": time.time(), "last_notified_price": None,
               "last_notified_at": None, "_token_hash": _hash_token(token)}
        self.alerts[aid] = rec
        return {**{k: v for k, v in rec.items() if not k.startswith("_")},
                "unsubscribe_token": token}

    def unsubscribe(self, token: str) -> bool:
        h = _hash_token(token or "")
        for rec in self.alerts.values():
            if secrets.compare_digest(rec["_token_hash"], h):
                rec["active"] = False
                return True
        return False

    def in_quiet_hours(self, rec: dict, now_utc: datetime | None = None) -> bool:
        if rec.get("quiet_start") is None or rec.get("quiet_end") is None:
            return False
        now = (now_utc or datetime.now(timezone.utc)).astimezone(ZoneInfo(rec.get("tz", "Asia/Karachi")))
        s, e, h = rec["quiet_start"], rec["quiet_end"], now.hour
        return s <= h < e if s <= e else (h >= s or h < e)

    def should_notify(self, rec: dict, price: float, now_ts: float | None = None) -> tuple[bool, str]:
        now_ts = now_ts if now_ts is not None else time.time()
        if not rec["active"]:
            return False, "inactive"
        if price > rec["target_price"]:
            return False, "above target"
        last = rec.get("last_notified_price")
        if last is not None:
            if abs(price - last) / last < 0.01 and now_ts - (rec.get("last_notified_at") or 0) < 86400:
                return False, "dedupe: price moved <1% within 24h"
        return True, "target reached"

    def evaluate(self, query: str, best_price: float, now_utc: datetime | None = None) -> list[dict]:
        """Evaluate all alerts for a query against an observed best price."""
        out = []
        for rec in self.alerts.values():
            if rec["query"].lower() != query.lower():
                continue
            ok, reason = self.should_notify(rec, best_price)
            if not ok:
                out.append({"alert_id": rec["id"], "sent": False, "suppressed": reason})
                continue
            if self.in_quiet_hours(rec, now_utc):
                out.append({"alert_id": rec["id"], "sent": False, "suppressed": "quiet hours"})
                continue
            msg = (f"Price alert: '{rec['query']}' is now {best_price} "
                   f"(target {rec['target_price']}). Unsubscribe: /api/alerts/unsubscribe?token=<your token>")
            res = notify(rec["channel"], rec["destination"], msg)
            if res.get("sent"):
                rec["last_notified_price"] = best_price
                rec["last_notified_at"] = time.time()
            out.append({"alert_id": rec["id"], "sent": bool(res.get("sent")),
                        "channel_result": res})
        return out

    # --- watchlists ----------------------------------------------------
    def watch_add(self, user_ref: str, product_ref: str, note: str = "") -> dict:
        items = self.watchlists.setdefault(user_ref, [])
        if any(i["product_ref"] == product_ref for i in items):
            return {"added": False, "reason": "already on watchlist"}
        items.append({"product_ref": product_ref, "note": note, "added_at": time.time()})
        return {"added": True}

    def watch_remove(self, user_ref: str, product_ref: str) -> dict:
        items = self.watchlists.get(user_ref, [])
        self.watchlists[user_ref] = [i for i in items if i["product_ref"] != product_ref]
        return {"removed": len(items) != len(self.watchlists[user_ref])}

    def watch_list(self, user_ref: str) -> list[dict]:
        return [dict(i) for i in self.watchlists.get(user_ref, [])]


SERVICE = AlertService()
