# Performance (measured 2026-11-17, this VM)

## Load smoke (tools/load_smoke.py, in-process TestClient, DEMO_MODE)
- 50 searches: **0 errors**; p50 **30.2 ms**; p95 **115.4 ms**;
  mean 232.8 ms skewed by a 5,031 ms first-request warmup (imports +
  cold FX cache). These are in-process numbers on a shared 1.5-vCPU
  VM — a floor for relative comparison, not a production capacity claim.

## Frontend
- First Load JS shared: **87.3 kB** (Phase 0 baseline 90 kB);
  /methodology 87.4 kB. Static export, 5 pages.

## Cost per search (estimate, assumptions stated)
- Demo/fixture path marginal cost ≈ compute only (~30 ms CPU) —
  effectively $0 at small scale.
- Live path cost is dominated by outbound fetches and any paid data
  providers (e.g. SerpApi per-query pricing) plus FX provider quotas;
  no production traffic exists yet, so no per-search dollar figure is
  claimed. The landed/search pipeline itself adds no paid calls.
