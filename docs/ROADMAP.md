# Roadmap — Cheapest Product Finder

Phases are sequential and each ends with: **build + lint + tests green →
conventional commit → push**. Never leave the repo broken at a phase
boundary. Phase 0 is done. Estimates are order-of-magnitude only; the
acceptance criteria are the contract, not the dates.

> Source of truth for the target design: `docs/ARCHITECTURE.md`.
> Decisions: `docs/DECISIONS.md`.

## Phase 0 — Audit & architecture ✅ DONE (2026-11-15)

- [x] Clone repo, inspect every file (stack, structure, scraping logic, UI)
- [x] Reproduce baseline: `py_compile` OK; `pip install` fails
      (`upstash-redis==0.3.0` gone from PyPI); app import fails on three
      independent defects (VECTOR import, missing `email-validator`,
      SlowAPI handlers without `Request`); app boots + serves
      `/api/health` only after four scratch-copy fixes (evidence in
      `docs/ARCHITECTURE.md` §1.7)
- [x] `docs/ARCHITECTURE.md`, `docs/ROADMAP.md` (this file),
      `docs/DECISIONS.md`
- [x] Repo hygiene: root `.gitignore`, `backend/.env` untracked
      (placeholder values only — see DECISIONS D-007)
- Acceptance: docs merged, baseline recorded honestly, repo still builds
  exactly as before (no production code changed in Phase 0).

## Phase 1 — Core domain model, DB, connector interface, queue, caching, config — DESIGN supplied by user 2026-11-16; code NOT present in repo 228bf32 (verified: no connectors/tests/002/metrics in tree) — built for real in this build, see PROGRESS.md

- [x] Fixed B-01…B-05: `VECTOR` import from `pgvector.sqlalchemy`,
      `email-validator` added, `httpx==0.27.2` pinned, `Request` added
      to rate-limited handlers, `upstash-redis` dropped (dead pin),
      `CREATE EXTENSION vector` in migration 001.
- [x] Security fixes B-09…B-12: server-assigned plans (client-sent
      `plan` ignored), refresh tokens, `TrustedHost` allow-list from
      settings, atomic plan-limit increment, money → `NUMERIC(19,4)`,
      `TIMESTAMPTZ`, `datetime.now(timezone.utc)`.
- [x] New target model (§3.1): `products`, `offers`, `sellers`,
      `price_history`, `fx_rates`, `tax_rules`, `alerts`, `watchlists`,
      `api_keys`, `connector_health`; extended `users`/`searches`;
      Alembic `002_target_model` (upgrade + downgrade round-tripped
      in tests).
- [x] Connector interface + registry + 5 mock connectors (Amazon,
      eBay, Etsy, Google Shopping, AliExpress) + circuit breaker;
      demo mode runs with zero keys.
- [x] Celery hardening: lazy OpenAI/Cloudinary clients, beat schedule
      for the monthly reset (fixes B-08), `run_connector_search`
      fan-out task, `broker_connection_retry_on_startup`; Redis cache
      helpers (graceful degradation when Redis is down); structlog;
      `/health` + `/ready` + `/metrics`; full `.env.example`.
- [x] Verification (all green, 2026-11-15): fresh venv
      `pip install -r requirements.txt` succeeds; `import app.main`
      succeeds with no keys; `alembic upgrade head` on a bare
      Postgres 16 + pgvector; seed (49 suppliers, Decimal prices);
      live API boot — register/login/refresh/`/me`, `/ready`
      (database+redis true), `/metrics`, `/docs`; live Celery worker
      ran `run_connector_search` → 15 offers, 5/5 connectors ok;
      `ruff check` clean; **55 tests pass, 86% coverage** on the new
      core modules (`app.connectors`, `app.services`, `app.workers`,
      `app.auth`, `app.config`).
- [x] Extra latent defects found by testing and fixed in this phase
      (see DECISIONS D-013…D-019): passlib+bcrypt≥4.1 broken hashing,
      SQLAlchemy enum sent member names (`FREE`) rejected by the DB
      enum, kombu 5.7 refusing redis-py 5.0.1, `Search` image fields
      blocking text searches, `SavedSupplier` N+1, missing 401 for
      absent bearer token.
- Acceptance: all criteria above met. Note: per-domain Celery
  concurrency/rate limits, retries with exponential backoff and DLQ
  were **not** fully built in Phase 1 (the fan-out task captures
  per-connector failures and the circuit breaker opens; per-domain
  rate limiting moves to Phase 2 with the real connectors).

## Phase 2 — First 5 connectors + generic URL extractor

- Amazon (multi-domain), eBay, Etsy, Google Shopping, AliExpress +
  generic URL extractor (JSON-LD + heuristics, SSRF-protected).
- Fallback chain per connector: official API → licensed provider adapter
  (env-gated) → JSON-LD/`__NEXT_DATA__` → HTML parse → Playwright pool.
- Fixture tests per connector + selector-drift detector + admin
  degraded flag + cached fallback with age label.
- `docs/COMPLIANCE.md` started: per-connector robots.txt/ToS note.
- Acceptance: each connector has fixtures + tests; a search against mock
  + at least one live source returns normalised `RawOffer`s; a forced
  parse failure triggers the drift flag (not a crash); no connector
  touches the DB.

## Phase 3 — Normalisation, product matching, deduplication

- Normalisers (currency, availability/condition enums, URL + text
  sanitisation), identity keys (GTIN/ASIN/MPN), brand+model regex,
  token-set fuzzy match, pgvector embedding similarity, attribute check
  (colour/size/storage/pack count/variant).
- Canonical `Product` + grouped offers; look-alikes (accessories, cases,
  bundles, variants) separated; “report wrong match” → rules table.
- Re-plumb image search onto the same pipeline (Vision → attributes →
  match, instead of the supplier-table lookup).
- Acceptance: fixture suite of known duplicates / near-misses
  (same product different titles, case vs phone, 128 GB vs 256 GB)
  matches correctly; no false merge in the suite; unit coverage ≥80%.

## Phase 4 — Country engine (FX, tax, duty, shipping, landed price)

- FX service (free provider + fallback, daily cache, `fx_rate`/`fx_as_of`
  recorded per price); geo-IP + manual country/currency override.
- Versioned `data/tax_rules/` tables (VAT/GST, de-minimis, duty by
  category, handling fees) + admin editing; landed-price computation
  with per-line `exact`/`estimated` tags; “not available in your country”
  section.
- Acceptance: landed-price unit tests for ≥10 country/category
  combinations incl. below/above de-minimis; FX fallback tested by
  killing the primary provider; UI/API expose the full breakdown.

## Phase 5 — Quality, availability & value scoring

- Quality Score 0–100 (Bayesian rating, volume/recency, fake-review
  heuristics, seller reputation, condition/warranty, counterfeit signal,
  returns/buyer protection) with per-factor explanation payload.
- Value Score with user-adjustable weights (price/quality/speed/
  reliability); fake-discount detector vs 90-day median.
- Availability normalisation (`in_stock/low_stock/preorder/backorder/
  out_of_stock/unknown`) + live re-verification of top results +
  “last verified X minutes ago”.
- Acceptance: scoring unit tests incl. low-review-count correction and
  below-median-price counterfeit flag; explanation payload present for
  every scored offer.

## Phase 6 — Search API, filters, streaming results

- `POST /api/v1/search` (text/GTIN/ASIN/MPN/URL), full filter set,
  sort modes, autocomplete + typo tolerance, multilingual query
  translation + merge, saved searches, shareable URLs, CSV/XLSX/JSON
  export.
- SSE streaming (`offer_batch` / `connector_done` / `connector_failed` /
  `search_complete`); per-connector timeouts so one slow site never
  blocks; query cache.
- Acceptance: Playwright-free API integration test streams results from
  ≥3 mock connectors progressively; filter/sort matrix test passes;
  p95 search latency budget recorded in the phase notes.

## Phase 7 — Frontend (search, results, product page, compare, i18n)

- Remove the orphan `web-application` gitlink; build real Next.js App
  Router + TypeScript + Tailwind + shadcn/ui in `web-application/`.
- Home, results (grid/list, SSE progressive loading, skeletons, empty/
  error states), product page (offers table, history chart, alerts,
  similar), compare (≤4), watchlists, trending; dark mode; WCAG AA;
  i18n EN/UR/AR/HI/ES/FR/DE/ZH + RTL; PWA shell; SEO (SSR, sitemap,
  JSON-LD, per-country URLs).
- Acceptance: Playwright E2E for the main search flow passes; Lighthouse
  performance/accessibility budgets recorded; no hard-coded strings in
  UI (all via i18n).

## Phase 8 — Price history, alerts, watchlists, notifications

- Daily `price_history` snapshots; 30/90/365-day charts (low/avg/high,
  “good time to buy?”); price-drop + back-in-stock alerts via email,
  Telegram, WhatsApp-link, web push; target-price watchlists; weekly
  best-deals digest; public trending-deals page per country.
- Acceptance: alert fires on a seeded price drop in staging; digest
  renders; history chart matches stored snapshots.

## Phase 9 — Remaining regional connectors

- Daraz, Flipkart, Noon, Jumia, Lazada, Shopee, Mercado Libre, Allegro,
  Rakuten, Coupang, Takealot, OLX, Zalando, OTTO, Cdiscount, Trendyol,
  Ozon, Walmart, Target, Best Buy, Newegg, Temu, Alibaba (+ others as
  the registry allows). Same interface, fixtures, drift detection and
  compliance note as Phase 2 — this phase is mechanical, not architectural.
- Acceptance: every new connector ships with fixtures + tests + a
  compliance note; connector-health dashboard shows all green/degraded honestly.

## Phase 10 — Admin dashboard, monitoring, public API

- Admin: connector health, success rates, latency, block rates, cost per
  provider, error logs, manual re-run, enable/disable, tax/duty editing.
- Observability: structured logs, Prometheus metrics, Sentry, health
  endpoints (finished from Phase 1 skeleton).
- Public REST API (`/api/v1/`): API keys, rate limits, usage tracking.
- Acceptance: admin can disable a connector and see search degrade
  gracefully; public API key flow works end-to-end with rate limiting.

## Phase 11 — Security hardening, tests, Docker, CI, performance pass

- SSRF audit, input validation sweep, helmet/CORS tightening, secrets
  audit (no secrets in repo/history), dependency audit.
- Test push to ≥80% coverage on core logic (matching, scoring,
  landed price, connectors); Playwright E2E suite green.
- Root `docker-compose.yml` (web, api, worker, beat, postgres, redis)
  with healthchecks; GitHub Actions CI (lint, typecheck, test, build);
  performance pass (query/cache/queue tuning, budgets recorded).
- Acceptance: CI green on a clean checkout; `docker compose up` runs
  the full app in demo mode with zero keys.

## Phase 12 — Docs, final cleanup, delivery

- README with screenshots, setup, env variables, how to add a connector,
  legal/compliance notes; `docs/API_KEYS.md` (accounts/keys to create
  with signup links, what is mocked, what to do next); final cleanup.
- Final delivery: (a) repo pushed to GitHub, (b) zip of the full project,
  (c) short “How to run it” guide, (d) API-keys/mocked/next-steps list.
- Acceptance: a new developer can go from clone to running demo-mode
  app by following the README alone.

---

## Phase log

| Phase | Status | Commit |
| --- | --- | --- |
| 0 — Audit & architecture | ✅ Done 2026-11-15 | see `git log` |
| 1 — Core model / DB / connectors / queue / cache | ✅ Done 2026-11-15 | see `git log` |
| 2 — First 5 connectors + URL extractor | Not started | — |
| 3 — Matching / dedup | Not started | — |
| 4 — Country engine | Not started | — |
| 5 — Quality / availability / value | Not started | — |
| 6 — Search API / streaming | Not started | — |
| 7 — Frontend | Not started | — |
| 8 — History / alerts / watchlists | Not started | — |
| 9 — Regional connectors | Not started | — |
| 10 — Admin / monitoring / public API | Not started | — |
| 11 — Security / tests / Docker / CI / perf | Not started | — |
| 12 — Docs / cleanup / delivery | Not started | — |

## Reconciliation note (agent, 2026-11-16)
User-supplied docs adopted as design baseline. Phase 0 = verified. Phase 1 claims (55 tests / 86% coverage / registry / fan-out / metrics) did not exist in the cloned tree and are implemented in this build's Phase 1 commit; test/coverage numbers reported in PROGRESS.md are only those actually run here.
