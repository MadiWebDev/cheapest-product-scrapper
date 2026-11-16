import sys, pathlib, datetime
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from app.priceintel import compliance


def test_daraz_record_exists_and_is_blocked_by_terms():
    rec = compliance.get_record("daraz")
    assert rec is not None
    assert rec["status"] == "blocked"  # terms §2E prohibit listing/price collection
    assert compliance.is_live_enabled("daraz") is False


def test_pending_records_keep_gate_closed():
    for sid in ("priceoye", "telemart"):
        rec = compliance.get_record(sid)
        assert rec is not None and rec["status"] == "pending"
        assert compliance.is_live_enabled(sid) is False


def test_unknown_source_is_disabled():
    assert compliance.is_live_enabled("no-such-source") is False


def test_expired_approved_record_disables(monkeypatch):
    rec = {"source_id": "x", "status": "approved", "expiry_date": "2020-01-01"}
    monkeypatch.setitem(compliance.RECORDS, "x", rec)
    assert compliance.is_live_enabled("x", today=datetime.date(2026, 1, 1)) is False


def test_unexpired_approved_record_enables(monkeypatch):
    rec = {"source_id": "y", "status": "approved", "expiry_date": "2999-01-01"}
    monkeypatch.setitem(compliance.RECORDS, "y", rec)
    assert compliance.is_live_enabled("y", today=datetime.date(2026, 1, 1)) is True


def test_gate_report_covers_all_records():
    report = compliance.gate_report()
    assert {r["source_id"] for r in report} == {"daraz", "priceoye", "telemart"}
    assert all(r["live_enabled"] is False for r in report)
