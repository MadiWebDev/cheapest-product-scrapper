"""Developer API keys (directive §16): hashed at rest, per-key monthly
quotas, usage accounting. A raw key is returned once at creation."""
from __future__ import annotations

import hashlib
import secrets
import time


def _h(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


class DevKeys:
    def __init__(self) -> None:
        self.keys: dict[str, dict] = {}  # hash -> record

    def create(self, owner: str, tenant: str, monthly_quota: int = 1000) -> str:
        key = "pk_" + secrets.token_urlsafe(24)
        self.keys[_h(key)] = {"owner": owner, "tenant": tenant,
                              "monthly_quota": monthly_quota, "used": 0,
                              "created_at": time.time(), "active": True}
        return key

    def authenticate(self, key: str | None) -> dict | None:
        if not key:
            return None
        rec = self.keys.get(_h(key))
        return rec if rec and rec["active"] else None

    def consume(self, key: str) -> tuple[bool, str]:
        rec = self.authenticate(key)
        if not rec:
            return False, "invalid key"
        if rec["used"] >= rec["monthly_quota"]:
            return False, "monthly quota exceeded"
        rec["used"] += 1
        return True, "ok"

    def usage(self, key: str) -> dict | None:
        rec = self.authenticate(key)
        if not rec:
            return None
        return {"owner": rec["owner"], "tenant": rec["tenant"],
                "used": rec["used"], "monthly_quota": rec["monthly_quota"],
                "remaining": rec["monthly_quota"] - rec["used"]}


DEVKEYS = DevKeys()
