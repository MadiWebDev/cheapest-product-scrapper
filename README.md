# Cheapest Product Finder

Global price-comparison engine: search marketplaces worldwide, ranked by **landed price** (item + shipping + VAT/GST + duty + handling + FX margin), **quality score (0–100, explained)** and **value score** for your ship-to country.

## Quick start
```bash
cp backend/.env.example backend/.env   # fill in real values; never commit .env
docker compose up -d db redis
cd backend && pip install -r requirements.txt && alembic upgrade head && uvicorn app.main:app --port 8000
cd ../web-application && npm install && npm run dev   # http://localhost:3000
```
Zero-key demo: set `DEMO_MODE=true` in backend env — demo offers are flagged `demo:true` and banner-labelled in the UI. Off by default.

## Architecture
FastAPI + SQLAlchemy/PostgreSQL (pgvector) + Celery/Redis backend (kept from the original repo, D-001/D-002), Next.js frontend in `web-application/`. See `docs/ARCHITECTURE.md`, decisions in `docs/DECISIONS.md` (D-001…D-024), status in `PROGRESS.md`.

## Connectors
30 registered: Amazon (20 regional domains configured), eBay (9 regions), Etsy, Google Shopping, AliExpress + 23 regional/global sites (Daraz, Flipkart, Noon, Jumia, Lazada, Shopee, Mercado Libre, Allegro, Rakuten, Coupang, Takealot, Trendyol, Ozon, Cdiscount, Zalando, OTTO, Walmart, Target, Best Buy, Newegg, Temu, Alibaba, OLX) + a generic SSRF-guarded URL extractor (JSON-LD → OpenGraph → heuristics).
**Add a connector:** copy `backend/app/connectors/marketplaces.py` pattern (subclass `StructuredSiteConnector` or `BaseConnector`), add one entry in `backend/app/connectors/registry.py`, add a fixture + test under `backend/tests/`, write its compliance note. Fallback chain: official API (env keys) → licensed provider (SerpApi env) → structured data → HTML. No CAPTCHA solving, no login bypass, ever (D-009).

## API
`POST /api/search`, `GET /api/search/stream` (SSE), `GET /api/autocomplete`, `GET /api/extract?url=`, `GET /api/export?fmt=csv|json`, `GET /api/connectors`, `GET /api/admin/connectors`, `GET /api/admin/tax-tables`, `/health`, `/ready`, `/metrics`. Tax/duty tables in `data/` are versioned **estimates** (labelled as such in every response).

## Tests
`cd backend && python -m pytest tests/ -q` — 17 tests; core-logic coverage 88% (domain + matching + landed + scoring + search service, measured 2026-11-16).
