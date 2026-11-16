# Task card — Phase 0: v3 audit, baselines, Agent Operating System

- **Goal:** Re-evidence the v1 product, fix what blocks it from booting,
  and install the v3 operating system (docs, ledger, scripts, ADRs).
- **Acceptance criteria:**
  - Baselines measured and recorded in AUDIT.md (tests, smoke, build). ✓
  - App boots end-to-end under TestClient. ✓ (after B-01/B-05 fixes)
  - STATE / TRUTH_LEDGER / BLOCKERS / RISKS / THREAT_MODEL /
    IMPLEMENTATION_STATUS exist and agree. ✓
  - Stack reconciliation recorded as ADRs D-025…D-032. ✓
  - verify.sh / eval.sh / e2e.sh / audit-truth.sh exist and exit 0. ✓
  - Docker gate honestly BLOCKED (B3-001), CI push BLOCKED (B3-002). ✓
- **Tests added:** tests/conftest.py (hermetic proxy stripping);
  audit_truth check 3 acts as the demo-guard test.
- **Files touched:** backend/app/main.py, backend/app/models/supplier.py,
  backend/requirements.txt, backend/tests/conftest.py, tools/*,
  *.sh, docs/* (new + DECISIONS append).
- **Review findings (pass 2):** requirements.txt still carried the dead
  upstash pin the paper docs claimed removed — fixed at the source, not
  just the venv. main.py's finder-router try/except swallows import
  errors silently; left as-is (legacy behaviour, D-022) but noted here.
- **Red-team findings (pass 3):** (1) Sandbox NO_PROXY IPv6 entry crashes
  httpx at import — reproduced, isolated to env, mitigated in conftest +
  scripts. (2) audit_truth's first marker pass false-positived on the
  fraud-detection vocabulary (`fake_discount`, `fake_review_penalty`,
  a `"fake":` result key) — reproduced by running the audit, then
  refined to fabricated-data phrases (mock/fake + data/price/offer/
  result); scan verified clean against the tree. (3) Demo guard tested under
  APP_ENV=production via subprocess — import fails with the guard
  message, as required.
- **Status:** VERIFIED — evidence in TRUTH_LEDGER L-001…L-011.
