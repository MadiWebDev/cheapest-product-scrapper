#!/usr/bin/env python3
"""API smoke: boots the real FastAPI app (DEMO_MODE) and exercises the
core read paths. Used by e2e.sh until the Phase 1 journey test lands,
then kept as a fast boot check."""
import os
import sys
import time

for _k in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY",
           "http_proxy", "https_proxy", "all_proxy", "no_proxy"):
    os.environ.pop(_k, None)
os.environ.setdefault("DEMO_MODE", "true")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402


def main() -> int:
    c = TestClient(app)
    t = time.time()
    r = c.post("/api/search", json={"query": "iphone 15", "country": "PK", "currency": "PKR"})
    dt = time.time() - t
    assert r.status_code == 200, r.status_code
    d = r.json()
    assert d["demo"] is True and d["total_offers"] >= 1, d.keys()
    print(f"smoke: POST /api/search 200 in {dt:.2f}s products={len(d['products'])} offers={d['total_offers']}")
    r = c.get("/api/connectors")
    assert r.status_code == 200 and len(r.json()["connectors"]) >= 28
    print(f"smoke: GET /api/connectors 200 connectors={len(r.json()['connectors'])}")
    for path in ("/ready", "/metrics", "/api/health"):
        assert c.get(path).status_code == 200, path
    print("smoke: /ready /metrics /api/health 200")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
