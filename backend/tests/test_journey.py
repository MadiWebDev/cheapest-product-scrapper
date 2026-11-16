"""Walking-skeleton journey (directive §1.7) at API level via TestClient:
search -> match -> landed cost (certainty labels) -> trust score + reasons
-> ranked results -> tracked /go redirect with click recording.

Playwright is unavailable in this VM (BLOCKERS B3-006); this is the
honest API-level equivalent and is labelled as such in the ledger.
"""
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

client = TestClient(app)


def test_walking_skeleton_journey():
    r = client.post("/api/search", json={"query": "iphone 15", "country": "PK", "currency": "PKR"})
    assert r.status_code == 200
    d = r.json()
    assert d["demo"] is True and d["total_offers"] >= 1
    assert "affiliate_disclosure" in d
    offer = d["products"][0]["offers"][0]
    # landed cost with §10 certainty labels
    assert offer["landed"] is not None and offer["landed"]["total"] > 0
    labels = offer["certainty"]["labels"]
    assert labels["item"] == "CONFIRMED" and labels["tax"] == "PLATFORM_ESTIMATE"
    assert offer["certainty"]["rules"]["tax"].startswith("vat_gst.json@")
    # trust score with top-3 reasons
    assert 0 <= offer["trust_score"] <= 100
    assert 1 <= len(offer["trust_reasons"]) <= 3
    assert offer["checked_at"]
    # tracked redirect
    go = client.get(offer["go_url"], follow_redirects=False)
    assert go.status_code == 302
    assert go.headers["location"].startswith("https://demo.example/")
    s = client.get("/api/clicks/summary")
    assert s.json()["total_clicks"] >= 1


def test_go_unknown_offer_404():
    assert client.get("/go/deadbeefdeadbeef", follow_redirects=False).status_code == 404


def test_compliance_api_lists_records():
    r = client.get("/api/compliance")
    assert r.status_code == 200
    by_id = {s["source_id"]: s for s in r.json()["sources"]}
    assert by_id["daraz"]["status"] == "blocked" and by_id["daraz"]["live_enabled"] is False
