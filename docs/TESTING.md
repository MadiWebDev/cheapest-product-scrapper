# Testing

- Backend: `~/workspace/cpf-venv/bin/python -m pytest` in `backend/`
  — **101 tests, all passing (2026-11-17)**. Suites map to phases:
  domain/connectors/search (v1), compliance/go/journey (P1), location
  (P2), adapters (P3), matching_v2 (P4), price_truth (P5),
  trust_ranking (P6), ai_mcp (P7), monetization (P9), alerts (P10),
  admin_devapi (P11), features (P13), hardening/chaos (P14).
- Gates: `./verify.sh` (pytest + audit:truth), `./eval.sh` (matching /
  relevance / scam / landed gates), `./e2e.sh` (boot + smoke),
  `tools/fairness_audit.py`, `tools/load_smoke.py`.
- Frontend: `npm run build` is the gate (type-check + static export);
  `node scripts/check-i18n.mjs` for locale completeness.
- Coverage (critical modules, measured 2026-11-17): **94%** total —
  landed 97%, matching_v2 92%, scoring 100%, price_truth 100%,
  trust 96%, compliance 93%, go 96%, v1 matching 79%.
- Not available in this VM: Playwright/browser E2E (B3-006), Docker
  boot (B3-001). API journeys use FastAPI TestClient and are labelled
  as such everywhere.
