#!/usr/bin/env python3
"""Local load smoke (directive §39): in-process TestClient, DEMO_MODE
catalog, N searches; reports p50/p95/mean latency and error count.
This measures THIS machine's in-process performance only — it is not
a production capacity claim.
"""
import os
import statistics
import sys
import time
from pathlib import Path

os.environ["DEMO_MODE"] = "true"
for _v in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "NO_PROXY", "no_proxy"):
    os.environ.pop(_v, None)  # sandbox proxy values crash httpx 0.27 parsing (see backend/tests/conftest.py)
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))


def main() -> int:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    import importlib
    import app.connectors.registry as reg
    importlib.reload(reg)
    import app.services.search as ss
    ss.REGISTRY = reg.REGISTRY
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    lat, errors = [], 0
    for i in range(n):
        t = time.perf_counter()
        r = client.post("/api/search", json={"query": "iphone 15", "country": "PK", "currency": "PKR"})
        lat.append((time.perf_counter() - t) * 1000)
        errors += 0 if r.status_code == 200 else 1
    lat.sort()
    p50 = statistics.median(lat)
    p95 = lat[min(n - 1, int(n * 0.95))]
    print(f"load-smoke: {n} searches | errors {errors} | mean {statistics.mean(lat):.1f} ms | "
          f"p50 {p50:.1f} ms | p95 {p95:.1f} ms | max {lat[-1]:.1f} ms")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
