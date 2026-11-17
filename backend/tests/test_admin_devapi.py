import sys, pathlib, os
os.environ["DEMO_MODE"] = "true"
os.environ["ADMIN_API_KEY"] = "bootstrap-test-key"
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
import importlib
import app.connectors.registry as reg
importlib.reload(reg)
import app.services.search as ss
ss.REGISTRY = reg.REGISTRY

from fastapi.testclient import TestClient
from app.main import app
from app.domain.models import RawOffer
from app.domain.matching_v2 import match_confidence
from app.priceintel.admin_v2 import SELLERS

c = TestClient(app)
ADMIN = {"x-admin-key": "bootstrap-test-key"}


def test_rbac_roles_enforced():
    assert c.get("/api/admin/v2/audit-log").status_code == 403
    assert c.get("/api/admin/v2/audit-log", headers={"x-admin-key": "wrong"}).status_code == 403
    r = c.post("/api/admin/v2/users", json={"name": "mod1", "role": "moderator"}, headers=ADMIN)
    assert r.status_code == 200
    mod_key = r.json()["key"]
    # moderator cannot create users (admin-only)
    assert c.post("/api/admin/v2/users", json={"name": "x", "role": "viewer"},
                  headers={"x-admin-key": mod_key}).status_code == 403
    # moderator can read the audit log (viewer+)
    assert c.get("/api/admin/v2/audit-log", headers={"x-admin-key": mod_key}).status_code == 200


def test_keys_stored_hashed_only():
    from app.priceintel.admin_v2 import AUTH
    r = c.post("/api/admin/v2/users", json={"name": "v1", "role": "viewer"}, headers=ADMIN)
    raw = r.json()["key"]
    assert raw not in AUTH.users  # only the hash is a key in the store
    assert all(len(k) == 64 for k in AUTH.users)


def test_match_review_decision_changes_matcher_and_audits():
    r = c.post("/api/admin/v2/match-review/scan", json={"query": "iphone", "connectors": ["demo"]}, headers=ADMIN)
    assert r.status_code == 200
    # direct enqueue path for a deterministic pair
    from app.priceintel.admin_v2 import REVIEW
    item = REVIEW.enqueue("Apple iPhone 15 128GB Black", "iPhone 15 (128GB) Black - PTA Approved", 62, ["title token overlap 0.62"])
    d = c.post(f"/api/admin/v2/match-review/{item['id']}/decision",
               json={"decision": "split"}, headers=ADMIN)
    assert d.status_code == 200 and d.json()["decision"] == "split"
    a = RawOffer(connector="t", title="Apple iPhone 15 128GB Black", url="https://t.example/1", price=1.0)
    b = RawOffer(connector="t", title="iPhone 15 (128GB) Black - PTA Approved", url="https://t.example/2", price=1.0)
    m = match_confidence(a, b)
    assert m["hard_block"] == "human review override"
    log = c.get("/api/admin/v2/audit-log", headers=ADMIN).json()["entries"]
    assert any(e["action"] == "match_review.split" for e in log)


def test_seller_scorecard_reply_and_tenant_isolation():
    SELLERS.record("tenant-a", RawOffer(connector="demo", title="Phone X", url="https://t.example/1",
                                        price=100.0, seller_name="SellerOne", seller_rating=4.5))
    SELLERS.record("tenant-a", RawOffer(connector="demo", title="Phone X", url="https://t.example/2",
                                        price=90.0, seller_name="SellerTwo", seller_rating=4.0))
    card = c.get("/api/admin/v2/sellers/SellerOne/scorecard", params={"tenant": "tenant-a"}, headers=ADMIN)
    assert card.status_code == 200 and card.json()["offers_seen"] == 1
    # tenant isolation: tenant-b sees nothing
    assert c.get("/api/admin/v2/sellers/SellerOne/scorecard", params={"tenant": "tenant-b"},
                 headers=ADMIN).status_code == 404
    # undercut: SellerTwo is cheaper on the same title
    u = c.get("/api/admin/v2/sellers/SellerOne/undercuts", params={"tenant": "tenant-a"}, headers=ADMIN)
    assert len(u.json()["alerts"]) == 1 and u.json()["alerts"][0]["competitor"] == "SellerTwo"
    # right of reply
    rep = c.post("/api/admin/v2/sellers/SellerOne/reply", json={"text": "We price-match on request."}, headers=ADMIN)
    assert rep.status_code == 200
    card2 = c.get("/api/admin/v2/sellers/SellerOne/scorecard", params={"tenant": "tenant-a"}, headers=ADMIN)
    assert card2.json()["replies"][0]["text"] == "We price-match on request."


def test_devapi_quota_and_usage():
    r = c.post("/api/admin/v2/devkeys", json={"owner": "dev1", "tenant": "public", "monthly_quota": 2}, headers=ADMIN)
    key = r.json()["key"]
    h = {"x-api-key": key}
    assert c.get("/api/v1/search", params={"q": "iphone"}, headers=h).status_code == 200
    assert c.get("/api/v1/search", params={"q": "iphone"}, headers=h).status_code == 200
    assert c.get("/api/v1/search", params={"q": "iphone"}, headers=h).status_code == 429
    u = c.get("/api/v1/usage", headers=h)
    assert u.json()["used"] == 2 and u.json()["remaining"] == 0
    assert c.get("/api/v1/search", params={"q": "x"}, headers={"x-api-key": "pk_nope"}).status_code == 401
