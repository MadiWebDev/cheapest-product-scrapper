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

c = TestClient(app)


def test_security_headers_present():
    r = c.get("/api/health")
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-frame-options"] == "DENY"
    assert "default-src 'none'" in r.headers["content-security-policy"]


def test_legacy_admin_guard(monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "phase14-key")
    assert c.get("/api/admin/connectors").status_code == 403
    assert c.get("/api/admin/connectors", headers={"x-admin-key": "phase14-key"}).status_code == 200
    monkeypatch.delenv("ADMIN_API_KEY")
    assert c.get("/api/admin/connectors").status_code == 200  # local-dev open, documented


def test_chaos_adapter_failure_degrades():
    class Boom:
        name = "boom"
        def search(self, q, f=None, country="US"):
            raise RuntimeError("adapter exploded")
        def drift_check(self, offers):
            return True
    ss.REGISTRY["boom"] = Boom()
    try:
        r = ss.search("iphone", {}, "US", "USD", connectors=["boom", "demo"])
        assert r["total_offers"] >= 1  # demo still served
        health = {h["connector"]: h for h in r["connector_health"]}
        assert health["boom"]["error"] and health["boom"]["offers"] == 0
    finally:
        del ss.REGISTRY["boom"]


def test_chaos_stale_fx_still_searches(monkeypatch):
    import app.services.fx as fxmod
    def down(url, timeout=8):
        raise OSError("fx down")
    monkeypatch.setattr(fxmod.urllib.request, "urlopen", down)
    fxmod._cache.update(rates=None, ts=0, stale=True)
    r = ss.search("iphone", {}, "PK", "PKR", connectors=["demo"])
    assert r["fx_stale"] is True and r["total_offers"] >= 1


def test_chaos_redis_down_search_unaffected(monkeypatch):
    # The finder path has no hard Redis dependency (Celery workers use
    # Redis out-of-band); a dead REDIS_URL must not break search.
    monkeypatch.setenv("REDIS_URL", "redis://127.0.0.1:6390/0")
    r = ss.search("iphone", {}, "US", "USD", connectors=["demo"])
    assert r["total_offers"] >= 1
