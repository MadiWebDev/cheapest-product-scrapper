# TRUTH LEDGER — PRICEINTEL v3 (directive §1.3, Appendix D)

One row per claim. VERIFIED requires evidence from a command/test run in
this program. Statuses: VERIFIED / IMPLEMENTED-UNVERIFIED / STUBBED /
BLOCKED / PLANNED.

| ID | Claim | Module | Status | Evidence | Re-verified | Notes |
|---|---|---|---|---|---|---|
| L-001 | Backend unit suite passes (17 tests: domain, connectors, search service) | backend/tests | VERIFIED | `~/workspace/cpf-venv/bin/python -m pytest -q` → "17 passed in 1.34s" (2026-11-17) | 2026-11-17 | v1 suite kept as characterization tests |
| L-002 | Full FastAPI app boots and serves search end-to-end in DEMO_MODE | backend/app/main.py | VERIFIED | TestClient smoke: POST /api/search 200 in 0.26s, 2 products/2 offers, demo=true; /api/connectors 200 (30); /ready /metrics /api/health 200 (2026-11-17) | 2026-11-17 | Required Phase-0 fixes B-01/B-05 (D-028) before it could boot at all |
| L-003 | Frontend production build passes; First Load JS 90 kB | web-application | VERIFIED | `npm run build` exit 0 in 24.8s, route / First Load 90 kB (2026-11-17) | 2026-11-17 | Next 14.2.35 |
| L-004 | Landed-price engine computes tax/duty/de-minimis with provenance labels | backend/app/domain/landed.py | VERIFIED | tests/test_domain.py::test_landed_includes_tax_over_de_minimis, test_landed_under_de_minimis_no_duty pass in suite (2026-11-17) | 2026-11-17 | §10 certainty vocabulary arrives Phase 5 |
| L-005 | Quality/value scoring with explanation dict | backend/app/domain/scoring.py | VERIFIED | tests/test_domain.py scoring tests pass in suite (2026-11-17) | 2026-11-17 | Trust v2 (stored inputs/version) is Phase 6 |
| L-006 | Matching groups offers and separates accessories/variants | backend/app/domain/matching.py | VERIFIED | tests/test_domain.py matching tests pass in suite (2026-11-17) | 2026-11-17 | Confidence+reasons and eval set are Phase 4 |
| L-007 | SSRF guard blocks private/loopback targets in URL extractor | backend/app/connectors/generic.py | VERIFIED | tests/test_connectors.py::test_ssrf_blocks_localhost passes (2026-11-17) | 2026-11-17 | |
| L-008 | Connector registry exposes 30 connectors incl. regionals | backend/app/connectors | VERIFIED | GET /api/connectors → 30 entries (2026-11-17 smoke) | 2026-11-17 | Live calls BLOCKED (B3-003); fixture-tested only |
| L-009 | FX service fetches live rates with failover and stale flag | backend/app/services/fx.py | IMPLEMENTED-UNVERIFIED | evidence needed: a run with network fetch logged fresh (stale=false) | — | Code + fallback verified by reading; live fetch not re-proven this program |
| L-010 | DEMO_MODE is rejected when APP_ENV=production | backend/app/main.py | VERIFIED | tools/audit_truth.py check 3 subprocess boot attempt fails with the guard message (2026-11-17) | 2026-11-17 | §1.14 / D-027 |
| L-011 | verify/eval/e2e/audit-truth scripts run green | repo root | VERIFIED | `./verify.sh`, `./eval.sh`, `./e2e.sh`, `./audit-truth.sh` all exit 0 (2026-11-17, Phase 0 close) | 2026-11-17 | eval datasets themselves land Phase 4/5/7 |
| L-012 | App starts via Docker Compose | docker-compose.yml | BLOCKED | evidence needed: docker-capable host run | — | B3-001: docker absent in build VM |
| L-013 | CI workflow on GitHub is current | .github/workflows/ci.yml | BLOCKED | evidence needed: successful push of the file | — | B3-002: App lacks Workflows permission (403) |
| L-014 | Live marketplace search returns real offers | backend/app/connectors | BLOCKED | evidence needed: run with owner API keys | — | B3-003 |
| L-015 | Playwright browser E2E journeys | e2e | BLOCKED | evidence needed: Playwright run | — | B3-006; fallback = TestClient journeys (L-002 pattern) |
| L-016 | Price history / alerts / admin endpoints from v1 | backend/app/routers, services/alerts.py | IMPLEMENTED-UNVERIFIED | evidence needed: endpoint-level tests (Phase 10 re-evidence task) | — | v1 claimed; not re-run this program yet |
