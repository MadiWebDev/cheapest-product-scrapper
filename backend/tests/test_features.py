import sys, pathlib, os
os.environ["DEMO_MODE"] = "true"
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
import importlib
import app.connectors.registry as reg
importlib.reload(reg)
import app.services.search as ss
ss.REGISTRY = reg.REGISTRY

from fastapi.testclient import TestClient
from app.main import app
from app.priceintel.features import OutcomeStore, check_compatibility, feature_enabled

c = TestClient(app)


def test_used_phone_kit_content():
    r = c.get("/api/features/used-phone-kit")
    assert r.status_code == 200
    ids = {s["id"] for s in r.json()["sections"]}
    assert {"identity", "hardware", "deal"} <= ids
    text = str(r.json())
    assert "PTA" in text and "IMEI" in text


def test_compatibility_rules():
    out = check_compatibility({"plug": "A", "dual_voltage": False, "kind": "phone"}, "PK")
    statuses = {x["id"]: x["status"] for x in out["checks"]}
    assert statuses["plug"] == "adapter_needed"
    assert statuses["voltage"] == "converter_needed"
    assert statuses["registration"] == "check_required"
    assert out["verdict"] == "action_needed"
    locked = check_compatibility({"carrier_locked": True, "kind": "phone"}, "PK")
    assert locked["verdict"] == "blocked"
    fine = check_compatibility({"plug": "C", "dual_voltage": True, "kind": "laptop"}, "PK")
    assert fine["verdict"] == "ok"


def test_budget_planner_with_demo(monkeypatch):
    r = c.post("/api/features/budget-plan", json={
        "items": [{"query": "iphone 15", "max_price": 10_000_000},
                  {"query": "iphone 15", "max_price": 1}],
        "country": "PK", "currency": "PKR"})
    d = r.json()
    assert len(d["plan"]) == 1 and d["plan"][0]["within_budget"] is True
    assert len(d["unmet"]) == 1 and d["unmet"][0]["cheapest_found"] is not None
    assert d["total"] == d["plan"][0]["landed_total"]


def test_outcome_feedback_and_calibration_flag():
    s = OutcomeStore()
    for _ in range(3):
        s.add("BadSeller", "never_arrived")
    summ = s.summary("BadSeller")
    assert summ["trust_calibration_flag"] is True and summ["total_reports"] == 3
    s.add("GoodSeller", "as_described")
    assert s.summary("GoodSeller")["trust_calibration_flag"] is False
    try:
        s.add("X", "not_a_real_outcome")
        raise AssertionError("invalid outcome must raise")
    except ValueError:
        pass


def test_evidence_pack_and_alternatives_and_passport():
    r = c.get("/api/features/evidence-pack", params={"query": "iphone", "country": "PK", "currency": "PKR"})
    d = r.json()
    assert d["generated_at"] and len(d["offers"]) >= 1 and "purpose" in d
    a = c.get("/api/features/alternatives", params={"query": "iphone"})
    assert a.status_code == 200 and "alternatives" in a.json()
    p = c.get("/api/features/deal-passport", params={"query": "iphone 15"})
    pd = p.json()
    assert pd["product"] and len(pd["timeline"]) >= 1


def test_feature_flag_disables_endpoint(monkeypatch):
    monkeypatch.setenv("FEATURE_USED_PHONE_KIT", "false")
    assert feature_enabled("used_phone_kit") is False
    assert c.get("/api/features/used-phone-kit").status_code == 503
    monkeypatch.delenv("FEATURE_USED_PHONE_KIT")
    assert c.get("/api/features/used-phone-kit").status_code == 200


def test_smart_digest_defaults_off(monkeypatch):
    monkeypatch.delenv("FEATURE_SMART_DIGEST", raising=False)
    assert feature_enabled("smart_digest") is False
    assert c.post("/api/features/digest/run", json={"user_ref": "u1"}).status_code == 503
    monkeypatch.setenv("FEATURE_SMART_DIGEST", "true")
    r = c.post("/api/features/digest/run", json={"user_ref": "u1"})
    assert r.status_code == 200 and r.json()["digest"]["generated"] is True
