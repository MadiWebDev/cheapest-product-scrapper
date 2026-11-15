# Decisions (ADRs)

Architectural decisions for the Cheapest Product Finder. When something is
ambiguous, the decision made is recorded here and work continues — per the
project brief. Each entry: context → decision → consequences. New decisions
are appended, never rewritten; superseded entries are marked as such.

## D-001 — Keep the Python/FastAPI backend; do not rewrite in Node/TypeScript

- **Date:** 2026-11-15 (Phase 0)
- **Context:** The brief’s default stack is Node.js + TypeScript +
  Fastify/Express, BullMQ, MongoDB-or-Postgres. The repo as found is
  Python 3.11 / FastAPI / SQLAlchemy / Celery / PostgreSQL + pgvector.
- **Decision:** Keep Python/FastAPI and evolve it. The existing auth,
  upload, worker, migration and seeding code is sound in structure; a
  rewrite would discard the only working code for zero product benefit.
  FastAPI + Celery + Postgres/pgvector cover every Phase 1–12 need
  (typed schemas via Pydantic v2, OpenAPI for free, pgvector for matching
  embeddings, Celery for the queue). The frontend is green-field and
  follows the brief (Next.js + TypeScript).
- **Consequences:** Connector interface, queue and scoring are implemented
  in Python. If a future maintainer wants TypeScript end-to-end, that is
  a rewrite project, not a phase — it is explicitly out of scope.

## D-002 — Keep Celery + Redis and PostgreSQL + pgvector (not BullMQ / MongoDB)

- **Date:** 2026-11-15 (Phase 0)
- **Context:** Brief defaults to BullMQ + Redis and Postgres “or MongoDB
  if the repo already uses it”.
- **Decision:** The repo already uses Postgres + pgvector and Celery +
  Redis. Keep both. Celery is the Python equivalent of BullMQ (per-domain
  concurrency, retries, DLQ, beat scheduling). Postgres is the right call
  over MongoDB: landed-price/tax/history data is relational, and pgvector
  already stores the matching embeddings.
- **Consequences:** Phase 1 hardens Celery (circuit breakers, DLQ, beat
  schedule) instead of introducing BullMQ. No MongoDB is introduced.

## D-003 — The `web-application/` gitlink is unrecoverable; rebuild the frontend from scratch

- **Date:** 2026-11-15 (Phase 0)
- **Context:** `web-application/` is a gitlink (`160000`, commit
  `2d6de21f…`) with no `.gitmodules` and GitHub reports
  `submodule_git_url: null`. There is no source to recover from this repo.
- **Decision:** Treat the frontend as green-field. In Phase 7, remove the
  gitlink (`git rm --cached web-application`) and build a real Next.js
  App Router app in `web-application/`. Do not attempt to guess or
  reconstruct the lost code.
- **Consequences:** No frontend exists until Phase 7. Phases 1–6 are
  API-first and verified via API/integration tests, which is the correct
  order anyway.

## D-004 — Monorepo layout: `backend/` (Python) + `web-application/` (Next.js) + `docs/` + `data/`

- **Date:** 2026-11-15 (Phase 0)
- **Context:** The repo already has `backend/` and `web-application/`
  top-level folders; the brief expects a single deployable system.
- **Decision:** Keep the two-folder monorepo. Add repo-root
  `docker-compose.yml` (Phase 11) orchestrating web/api/worker/beat/
  postgres/redis, `docs/` for architecture/roadmap/decisions/compliance,
  and `backend/data/tax_rules/` for versioned tax tables.
- **Consequences:** One repo, one CI pipeline, two deployables. The
  existing `backend/docker-compose.yml` is superseded by the root one
  in Phase 11 (it omits Redis, the frontend, and healthchecks).

## D-005 — Connector order: global five first, regionals in Phase 9

- **Date:** 2026-11-15 (Phase 0)
- **Context:** The brief lists Walmart, Target, Best Buy, Newegg, Temu
  in the “global” group, but they are US-centric; the regional list is
  long (Daraz, Flipkart, Noon, Jumia, …).
- **Decision:** Phase 2 builds Amazon, eBay, Etsy, Google Shopping,
  AliExpress + the generic URL extractor. Walmart/Target/Best Buy/
  Newegg/Temu/Alibaba join the Phase 9 regional batch unless their
  official APIs prove trivial during Phase 2, in which case the Phase 2
  notes will record the early addition. The connector interface is
  proven by five connectors; Phase 9 is then mechanical.
- **Consequences:** US-only stores are not in the first demo. The
  generic URL extractor partially covers them from Phase 2 (a user can
  paste a Walmart/Target URL).

## D-006 — Fix-before-build: Phase 1 starts by repairing the broken base

- **Date:** 2026-11-15 (Phase 0)
- **Context:** The committed tree does not install or import (§1.5/§1.7
  of `ARCHITECTURE.md`): dead `upstash-redis` pin, wrong `VECTOR`
  import, missing `email-validator`, SlowAPI handlers without `Request`.
- **Decision:** Phase 1 fixes B-01…B-05 (and security B-09…B-12) before
  any new feature work, and proves it with a clean-checkout install +
  boot test in CI. No new feature is built on a broken base.
- **Consequences:** Phase 1 looks like “just fixes” for its first half;
  that is intentional and is the fastest path to a trustworthy base.

## D-007 — `.env` is untracked from Phase 0; committed history left as-is

- **Date:** 2026-11-15 (Phase 0)
- **Context:** `backend/.env` was committed in the single existing commit.
  Its values are all placeholders (`your-…`, `redis://your-…`); no live
  secret was found in the file.
- **Decision:** `git rm --cached backend/.env` in Phase 0 and add a root
  `.gitignore` (`.env`, `__pycache__/`, venvs, etc.). History is **not**
  rewritten: with one commit and placeholder-only values, a rewrite
  buys nothing and would destroy the audit baseline. If any real secret
  is ever found to have been committed, rotate it and rewrite history
  at that point.
- **Consequences:** Fresh clones must copy `.env.example` → `.env`
  (already documented in `backend/README.md`).

## D-008 — Money is `NUMERIC(19,4)`, never `Float`

- **Date:** 2026-11-15 (Phase 0)
- **Context:** `Supplier.price_usd_per_unit` is a `Float`.
- **Decision:** All money columns and all price arithmetic use
  `NUMERIC(19,4)` / Python `Decimal`. The Phase 1 migration converts
  the legacy column.
- **Consequences:** Slightly more verbose arithmetic; correct rounding
  in landed-price math, which is the product’s core differentiator.

## D-009 — No CAPTCHA-solving, no login-wall bypassing, ever

- **Date:** 2026-11-15 (Phase 0)
- **Context:** Brief §9 forbids it; it also creates legal and
  reliability risk.
- **Decision:** On a block, degrade gracefully: next source in the
  fallback chain → cached data with an age label → degraded flag in
  admin. This is a hard rule for every connector, including any
  contributed later.
- **Consequences:** Some sites will show cached/degraded data instead of
  live prices. That is the correct trade-off and is shown honestly
  in the UI.

## D-010 — Demo/seed mode is first-class, not a hack

- **Date:** 2026-11-15 (Phase 0)
- **Context:** Brief §10 requires the app to run with zero API keys.
- **Decision:** Mock connectors implement the same `Connector` interface
  as real ones and are selected by config (`CONNECTORS=mock` / env).
  Seed data is clearly labelled demo data. Business logic never
  branches on “is demo” — only the connector registry does.
- **Consequences:** Every phase can be demoed and tested without
  credentials; the Phase 11 `docker compose up` acceptance test runs
  in demo mode.

## D-011 — Keep image search; re-plumb it onto the new product model

- **Date:** 2026-11-15 (Phase 0)
- **Context:** The repo’s only real feature is image → supplier search
  (GPT-4o Vision + embeddings). The brief’s primary input is text, with
  image listed as “later”. Deleting the image flow would destroy the
  repo’s only working feature; keeping it as-is would preserve a dead
  end (it ranks seeded suppliers, not real offers).
- **Decision:** Keep the upload endpoint, Cloudinary handling, rate
  limits and 30-day expiry semantics. In Phase 3/6, re-plumb the worker
  so Vision output feeds the same normalise → match pipeline as text
  search, and store the embedding on the search record (fixing B-07).
  The legacy `saved_suppliers` / supplier-ranking path is retained
  until Phase 3, then retired or kept as a B2B view by explicit
  decision at that time.
- **Consequences:** Image search ships later than text search, but on
  the real offer pipeline when it does.

## D-012 — Plans are server-assigned; registration always creates a `free` user

- **Date:** 2026-11-15 (Phase 0)
- **Context:** `UserRegister.plan` is client-controlled (B-09): anyone
  can self-assign `enterprise`.
- **Decision:** Phase 1 removes `plan` from the registration schema.
  Plan changes happen only via admin/billing flows. This is fixed in
  Phase 1, not deferred.
- **Consequences:** Existing clients sending `plan` on register get it
  ignored (Pydantic's default extra-ignore behaviour; verified by
  test — a `plan: "enterprise"` registration creates a `free` user).

## D-013 — Replace passlib with direct bcrypt

- **Date:** 2026-11-15 (Phase 1)
- **Context:** `passlib 1.7.4` + `bcrypt >= 4.1` is broken: passlib
  reads the removed `bcrypt.__about__`, then raises `ValueError:
  password cannot be longer than 72 bytes` for *every* password.
  Registration and login therefore failed on a fresh install — found
  by the Phase 1 auth tests, not by inspection.
- **Decision:** Drop `passlib` entirely; use `bcrypt` directly
  (`hashpw`/`gensalt`/`checkpw`, pin `bcrypt==5.0.0`). Stored hashes
  are the same `$2b$` format, so existing passwords keep working.
  The explicit >72-byte rejection stays (bcrypt silently truncates
  otherwise).
- **Consequences:** One fewer unmaintained dependency (passlib has
  been unmaintained since 2020).

## D-014 — SQLAlchemy enums store member values, not names

- **Date:** 2026-11-15 (Phase 1)
- **Context:** `SQLEnum(PlanEnum)` sends the member *name* (`FREE`)
  to Postgres, but the `planenum` type only has lowercase values
  (`free`). Every `INSERT INTO users` failed on a real database —
  found by the Phase 1 model tests.
- **Decision:** Use `values_callable=lambda e: [m.value for m in e]`
  on the `plan` and `role` enum columns.
- **Consequences:** Inserts work; the DB enum and the Python enum
  agree on values.

## D-015 — redis-py bumped to 6.1.0 (kombu floor)

- **Date:** 2026-11-15 (Phase 1)
- **Context:** Celery 5.3.6 pulls kombu 5.7, whose Redis transport
  refuses redis-py < 6.1 (`VersionMismatch`) — the worker could never
  connect to Redis with the old `redis==5.0.1` pin. Found by running
  a real worker end to end, not by unit tests.
- **Decision:** Pin `redis==6.1.0` (the minimum kombu accepts).
- **Consequences:** The queue actually works. If a future kombu
  raises its floor again, bump redis-py with it.

## D-016 — SECRET_KEY: dev default with a warning, fail-fast in production

- **Date:** 2026-11-15 (Phase 1)
- **Context:** The old config had an insecure hard-coded default
  (`your-secret-key-change-in-production`) that silently shipped.
- **Decision:** Empty `SECRET_KEY` in development uses a dev-only
  default and logs a warning; in production a missing/short key
  raises at startup (`Settings` validation).
- **Consequences:** Dev and tests stay frictionless; production
  cannot start with a weak key by accident.

## D-017 — Cache degrades to a no-op when Redis is down

- **Date:** 2026-11-15 (Phase 1)
- **Context:** The cache is an optimisation, not a dependency; the
  app should keep serving (uncached) when Redis is unavailable.
- **Decision:** `Cache` logs once and returns misses/`False` instead
  of raising when Redis is unreachable (verified by a test pointing
  at a dead port).
- **Consequences:** `/api/ready` reports the degradation honestly
  instead of the API crashing.

## D-018 — Test fixtures: truncate before each test, fresh session per request

- **Date:** 2026-11-15 (Phase 1)
- **Context:** The first fixture design truncated tables in teardown
  on the test's own session and shared that session with the
  TestClient. API requests leave the session idle-in-transaction,
  and `TRUNCATE` deadlocked on its locks — the suite hung.
- **Decision:** Truncate on a fresh engine connection *before* each
  test; the TestClient's `get_db` override yields a fresh session per
  request (like production); tests commit their setup rows. Alembic
  commands in `test_migrations` roll back the test session first.
- **Consequences:** The suite runs in ~10s with no hangs.

## D-019 — Per-domain Celery rate limits / DLQ deferred to Phase 2

- **Date:** 2026-11-15 (Phase 1)
- **Context:** The Phase 1 acceptance criteria listed per-domain
  concurrency/rate limits, exponential-backoff retries and a DLQ.
  The fan-out task + circuit breaker cover the failure-isolation
  half; per-domain politeness only matters once real connectors
  exist.
- **Decision:** Defer per-domain rate limiting and DLQ to Phase 2
  (real connectors), and record the gap here instead of claiming
  the criteria were fully met.
- **Consequences:** Phase 1 is honest about what it did not build.

---

## Agent decisions (append-only, D-020+; D-001…D-019 above win on any conflict)

## D-020 — Phase 0 agent decisions D1–D9 supersession map
Agent Phase 0 draft decisions are superseded by / folded into: keep-Python → D-001; submodule removal → D-003 (frontend rebuilt in `web-application/` per D-004, NOT a separate `web/` dir — earlier draft wording superseded); .env handling → D-007; demo mode → D-010. New items retained: FX primary frankfurter.app + fallback open.er-api.com with stale-flag (never invented rates); query-translation dictionary hook + TRANSLATE_API_URL env; hand-rolled Tailwind components in shadcn style for the frontend (no extra codegen dependency).

## D-021 — Money columns use NUMERIC(19,4) per D-008
Initial agent draft of catalog models used Float for money; corrected before Phase 1 commit to Numeric(19,4) for all price/total columns. Domain-layer arithmetic uses float only for scoring ratios, never for stored money.

## D-022 — Legacy SourceLens surface
Legacy supplier/image-search code is kept working (D-011) and re-plumbed later; new catalog domain is additive. No legacy route is deleted in Phase 1.

## D-023 — Next.js pinned to patched 14.2.35
Initial 14.2.5 install printed a known-vulnerability warning; bumped to 14.2.35 (latest patched 14.x) in Phase 11. Rebuild verified after bump in CI config; local rebuild recorded in PROGRESS.md.

## D-024 — Phases 3–6 landed in one commit; 8–10 in one commit
Core domain slices (matching, landed, scoring, search) are interdependent single modules; they were built and tested together and committed as 3b1164e (tags phase-3/4/5/6 point at it) and services/admin as one commit (phase-8/9/10 tags). Recorded honestly rather than fabricating separate per-phase diffs.
