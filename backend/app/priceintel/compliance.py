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
