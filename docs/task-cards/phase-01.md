# Task card — Phase 1: walking skeleton (PK, smartphones, compliance gate, /go)

- **Goal:** One thin real slice: search → match → landed cost with
  certainty labels → trust score with top-3 reasons → ranked results →
  tracked /go redirect, with sources gated by compliance records.
- **Acceptance criteria:**
  - COMPLIANCE_REVIEW records exist for Daraz + 2 PK sources, built only
    from fetched public pages. ✓ (Daraz blocked by its own terms §2E;
    PriceOye/Telemart pending — terms not reviewed)
  - Gate disables unapproved sources in live mode, demo unaffected. ✓
  - /go resolves only server-registered offers, re-validates the host
    against the allowlist at click time, records clicks, applies an
    affiliate tag only when env-configured; disclosure in search payload. ✓
  - Journey test covers the full slice. ✓ (API level; Playwright B3-006)
- **Tests added:** test_compliance.py (6), test_go.py (5), test_journey.py (3).
  Suite: 31 passed.
- **Files touched:** app/priceintel/{__init__,compliance,go}.py,
  app/data/compliance/*.json, app/routers/priceintel.py, app/main.py,
  app/domain/{landed,scoring}.py, app/services/search.py, tests/*.
- **Review findings (pass 2):** search() previously trusted connector
  output URLs end-to-end; /go now re-validates at click time, not just
  at registration. Affiliate param defaults to "tag" but is per-connector
  overridable via env (programs differ; rules live with the compliance
  record when approved).
- **Red-team findings (pass 3):** (1) Lookalike hosts — `evil-amazon.com`,
  `amazon.com.evil.com`, `amazon.com@evil.com` — all rejected by the
  suffix rule + urlparse hostname (tests). (2) Expired approved record
  disables the gate (test). (3) telemart.pk robots.txt contained an
  embedded prompt-injection block aimed at agents — ignored entirely;
  only the robots rules were recorded.
- **Status:** VERIFIED — TRUTH_LEDGER L-017…L-022.
