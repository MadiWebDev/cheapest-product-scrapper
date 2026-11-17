"""Admin console v2 (directive §16/§35): RBAC, match-review queue with
audit trail, seller scorecards with right-of-reply, audit log, and
seller-intelligence basics with per-tenant isolation.

Keys are stored as SHA-256 hashes only; a raw key is shown once at
creation. Every sensitive action appends to the audit log.
"""
from __future__ import annotations

import hashlib
import os
import secrets
import time

ROLES = ("viewer", "moderator", "admin")
ROLE_RANK = {r: i for i, r in enumerate(ROLES)}


def _h(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


class AdminAuth:
    def __init__(self) -> None:
        self.users: dict[str, dict] = {}  # key_hash -> {name, role}

    def bootstrap(self) -> None:
        key = os.getenv("ADMIN_API_KEY")
        if key and _h(key) not in self.users:
            self.users[_h(key)] = {"name": "bootstrap-admin", "role": "admin"}

    def create_user(self, name: str, role: str) -> str:
        if role not in ROLES:
            raise ValueError(f"role must be one of {ROLES}")
        key = "adm_" + secrets.token_urlsafe(24)
        self.users[_h(key)] = {"name": name, "role": role}
        return key

    def authenticate(self, key: str | None) -> dict | None:
        self.bootstrap()
        if not key:
            return None
        return self.users.get(_h(key))

    def require(self, key: str | None, min_role: str) -> dict:
        user = self.authenticate(key)
        if not user:
            raise PermissionError("invalid or missing admin key")
        if ROLE_RANK[user["role"]] < ROLE_RANK[min_role]:
            raise PermissionError(f"requires role >= {min_role}")
        return user


AUTH = AdminAuth()


class AuditLog:
    def __init__(self) -> None:
        self.entries: list[dict] = []

    def add(self, actor: str, action: str, target: str, detail: dict | None = None) -> dict:
        e = {"ts": time.time(), "actor": actor, "action": action, "target": target,
             "detail": detail or {}}
        self.entries.append(e)
        return e

    def list(self, limit: int = 100) -> list[dict]:
        return [dict(e) for e in self.entries[-limit:]]


AUDIT = AuditLog()


# --- match review queue -----------------------------------------------------

class MatchReviewQueue:
    def __init__(self) -> None:
        self.items: dict[str, dict] = {}

    def enqueue(self, title_a: str, title_b: str, confidence: int, reasons: list[str]) -> dict:
        rid = hashlib.sha1(f"{title_a}|{title_b}".encode()).hexdigest()[:12]
        if rid in self.items:
            return self.items[rid]
        rec = {"id": rid, "title_a": title_a, "title_b": title_b,
               "confidence": confidence, "reasons": reasons,
               "status": "pending", "enqueued_at": time.time()}
        self.items[rid] = rec
        return rec

    def decide(self, rid: str, decision: str, actor: str) -> dict:
        if decision not in ("approve_match", "split", "merge"):
            raise ValueError("decision must be approve_match | split | merge")
        rec = self.items[rid]
        rec["status"] = "decided"
        rec["decision"] = decision
        rec["decided_by"] = actor
        rec["decided_at"] = time.time()
        from app.domain.matching_v2 import set_override
        set_override(rec["title_a"], rec["title_b"],
                     "match" if decision in ("approve_match", "merge") else "no_match")
        AUDIT.add(actor, f"match_review.{decision}", rid,
                  {"title_a": rec["title_a"], "title_b": rec["title_b"]})
        return rec

    def pending(self) -> list[dict]:
        return [dict(r) for r in self.items.values() if r["status"] == "pending"]


REVIEW = MatchReviewQueue()


# --- seller scorecards + intelligence (per-tenant) ---------------------------

class SellerIntel:
    """Observations are keyed by tenant: one tenant's seller data is
    never visible to another."""

    def __init__(self) -> None:
        self.obs: dict[str, list[dict]] = {}  # tenant -> observations
        self.replies: dict[str, list[dict]] = {}  # seller -> replies

    def record(self, tenant: str, offer) -> None:
        if not offer.seller_name:
            return
        self.obs.setdefault(tenant, []).append({
            "seller": offer.seller_name, "title": offer.title, "price": offer.price,
            "connector": offer.connector, "seller_rating": offer.seller_rating,
            "official_store": offer.official_store, "ts": time.time()})

    def scorecard(self, tenant: str, seller: str) -> dict | None:
        rows = [o for o in self.obs.get(tenant, []) if o["seller"] == seller]
        if not rows:
            return None
        ratings = [o["seller_rating"] for o in rows if o["seller_rating"]]
        return {"seller": seller, "offers_seen": len(rows),
                "avg_seller_rating": round(sum(ratings) / len(ratings), 2) if ratings else None,
                "connectors": sorted({o["connector"] for o in rows}),
                "official_store_seen": any(o["official_store"] for o in rows),
                "replies": [dict(r) for r in self.replies.get(seller, [])]}

    def reply(self, seller: str, text: str, actor: str) -> dict:
        rec = {"seller": seller, "text": text, "by": actor, "ts": time.time()}
        self.replies.setdefault(seller, []).append(rec)
        AUDIT.add(actor, "seller.reply", seller, {"text": text[:200]})
        return rec

    def undercut_alerts(self, tenant: str, seller: str) -> list[dict]:
        from app.domain.normalize import normalize_title
        mine: dict[str, float] = {}
        others: dict[str, list[tuple[str, float]]] = {}
        for o in self.obs.get(tenant, []):
            key = normalize_title(o["title"])[:60]
            if o["price"] is None:
                continue
            if o["seller"] == seller:
                mine[key] = min(mine.get(key, o["price"]), o["price"])
            else:
                others.setdefault(key, []).append((o["seller"], o["price"]))
        alerts = []
        for key, my_price in mine.items():
            for other_seller, price in others.get(key, []):
                if price < my_price * 0.98:
                    alerts.append({"title_key": key, "my_price": my_price,
                                   "competitor": other_seller, "competitor_price": price,
                                   "gap_pct": round((my_price - price) / my_price * 100, 1)})
        return alerts


SELLERS = SellerIntel()
