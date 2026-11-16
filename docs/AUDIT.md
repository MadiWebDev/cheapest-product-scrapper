# AUDIT — PRICEINTEL v3 baseline (Phase 0, 2026-11-17)

Scope: full re-audit of the v1 build (commit `a9b870a` local / `ccb27576`
remote) before any v3 feature work, per directive §3 and §43. All numbers
below were measured in this session; the commands are quoted so they can
be re-run.

## Measured baselines (2026-11-17)

| Measurement | Command | Result |
|---|---|---|
| Backend tests | `cd backend && ~/workspace/cpf-venv/bin/python -m pytest -q` | **17 passed in 1.34s** |
| Full-app boot + search smoke | `DEMO_MODE=true` TestClient `POST /api/search {query:"iphone 15", country:"PK", currency:"PKR"}` | **200 in 0.26s**, 2 products / 2 offers, `demo: true` |
| Connector registry | `GET /api/connectors` | **200, 30 connectors** |
| Health endpoints | `GET /ready`, `/metrics`, `/api/health` | **200 / 200 / 200** |
| Frontend build | `cd web-application && npm run build` | **exit 0 in 24.8s**, First Load JS **90 kB** (route `/`) |
| Docker | `docker compose version` | **`docker: command not found`** — Compose boot BLOCKED in this VM (B3-001) |
| Git | local HEAD / remote head | `a9b870a` / `ccb27576` (trees verified identical in v1 except intended absences) |

## What the v1 repo actually is

- **Backend** (`backend/`, Python/FastAPI): a legacy "SourceLens" supplier
  app (auth, image upload, supplier search — kept per D-011/D-022) plus the
  additive Cheapest Product Finder modules: `app/domain/` (models, landed,
  scoring, matching, normalize), `app/connectors/` (base, registry, 5 global
  + generic + demo + regional marketplaces), `app/services/` (search, fx,
  alerts, translate), `app/routers/` (finder, admin), `app/models/catalog.py`
  (migration 002 tables), `app/data/` (vat_gst.json, duty.json — labelled
  "estimate", versioned 2026-11-16).
- **Frontend** (`web-application/`, Next.js 14.2.35): single-page search app
  (`app/page.tsx`, `components/SearchApp.tsx`), Tailwind, PWA manifest,
  demo banner. No i18n framework, no product/compare pages yet.
- **Data**: VAT/GST table covers 27 countries; duty table has de-minimis
  for 14 countries and 9 category rates. Both are estimates and labelled
  as such — v3 keeps the labels and adds rule ids/versions (§10).

## Defects found by re-running the app (not just its unit tests)

The v1 unit suite never imports `app.main`, so boot defects survived.
All fixed in Phase 0 (D-028):

1. **B-01 (real)**: `app/models/supplier.py` imported `VECTOR` from
   `sqlalchemy.dialects.postgresql` → ImportError on boot. Fixed to
   `pgvector.sqlalchemy.Vector`.
2. **B-05 (real)**: `app/main.py` rate-limited handlers lacked the
   `request: Request` parameter slowapi requires → boot exception. Fixed.
3. **Missing dependency**: `email-validator` used by schemas but absent
   from requirements.txt. Added (2.1.0).
4. **Dead pin**: `upstash-redis==0.3.0` does not exist on PyPI (the v1
   user-doc roadmap claimed it was "dropped" — it was not). Removed.
5. **Version conflict**: `openai==1.10.0` breaks with `httpx>=0.28`;
   pinned `httpx==0.27.2`.
6. **Environment quirk (not app code)**: the sandbox's `NO_PROXY` IPv6
   entry crashes httpx 0.27 proxy parsing when any client is constructed
   at import time. Test bootstrap strips proxy vars
   (`backend/tests/conftest.py`); scripts unset them too.

## Reusable / sound

Domain engines (landed, scoring, matching, normalize) — pure functions,
unit-tested; connector registry + drift detector; FX service with
failover + stale flag; SSE search; admin router skeleton; catalog models
with NUMERIC(19,4) money (D-008/D-021).

## Gaps vs directive v3 (feed the phase plan)

No compliance gate (connectors carry only a free-text note); no /go
tracked redirect; landed cost has exact/estimated provenance but not the
§10 certainty vocabulary or rule ids; no fair-price band / PCI / glitch
quarantine; trust = v1 quality score (no stored inputs/version, no
outcome loop); no AI provider abstraction; no affiliate service or
billing; alerts lack quiet hours/dedupe/unsubscribe; no eval datasets;
no TRUTH_LEDGER/STATE/BLOCKERS docs (created this phase); CI file exists
locally but cannot be pushed (App lacks Workflows permission — B3-002).

## Characterization note

The 17 v1 tests are the characterization suite for the domain engines;
v3 phases add tests before refactoring any of those modules (§3
strangler rule). No v1 module is deleted in v3.
