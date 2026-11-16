"""Compliance gate (directive §6, Appendix C, D-032).

A source may run in LIVE mode only when a COMPLIANCE_REVIEW record
exists, has status "approved", and is unexpired. Records are versioned
JSON under app/data/compliance/. Anything else — missing, pending,
blocked, expired — means the adapter is DISABLED for live mode.
Fixture/demo mode is unaffected and always labelled.
"""
from __future__ import annotations

import datetime
import json
import pathlib

DATA = pathlib.Path(__file__).parent.parent / "data" / "compliance"


def load_records() -> dict[str, dict]:
    out: dict[str, dict] = {}
    if DATA.exists():
        for p in sorted(DATA.glob("*.json")):
            rec = json.loads(p.read_text())
            out[rec["source_id"]] = rec
    return out


RECORDS = load_records()


def get_record(source_id: str) -> dict | None:
    return RECORDS.get(source_id)


def is_live_enabled(source_id: str, today: datetime.date | None = None) -> bool:
    rec = RECORDS.get(source_id)
    if not rec or rec.get("status") != "approved":
        return False
    exp = rec.get("expiry_date")
    if exp:
        today = today or datetime.date.today()
        if datetime.date.fromisoformat(exp) < today:
            return False
    return True


STATUSES = ("pending", "approved", "blocked", "rejected", "expired")


def update_record(source_id: str, *, status: str, reviewer: str,
                  expiry_date: str | None = None, reason: str = "") -> dict:
    """Admin review write-path: updates the versioned record on disk.
    Approving requires a reviewer and an expiry date — the gate must
    never open by accident."""
    if status not in STATUSES:
        raise ValueError(f"status must be one of {STATUSES}")
    if source_id not in RECORDS:
        raise KeyError(source_id)
    if status == "approved" and (not reviewer or not expiry_date):
        raise ValueError("approval requires a reviewer and an expiry_date")
    rec = dict(RECORDS[source_id])
    rec.update({"status": status, "reviewer": reviewer,
                "sign_off_date": datetime.date.today().isoformat() if status == "approved" else rec.get("sign_off_date"),
                "expiry_date": expiry_date or rec.get("expiry_date")})
    if reason:
        rec["status_reason"] = reason
    (DATA / f"{source_id}.json").write_text(json.dumps(rec, indent=2))
    RECORDS[source_id] = rec
    return rec


def gate_report(today: datetime.date | None = None) -> list[dict]:
    return [
        {
            "source_id": sid,
            "status": rec.get("status"),
            "live_enabled": is_live_enabled(sid, today),
            "expiry_date": rec.get("expiry_date"),
            "status_reason": rec.get("status_reason"),
        }
        for sid, rec in sorted(RECORDS.items())
    ]
