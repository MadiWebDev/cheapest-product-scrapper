# Task card — Phase 14: hardening + docs + final report

- **Goal:** measured coverage, security pass, chaos basics, load
  smoke, complete docs, FINAL_REPORT, final zip.
- **Acceptance:** critical-module coverage 94% (target 80%) ✓;
  security headers + legacy admin auth (L-069) implemented and
  tested ✓; chaos tests (adapter failure / stale FX / Redis down) ✓;
  load smoke real numbers ✓; 12 docs + FINAL_REPORT ✓; verify/eval/
  e2e/audit-truth/fairness all green at close ✓; suite 101 passed ✓.
- **Review findings (pass 2):** the coverage run modified
  backend/.coverage — it is excluded from the commit and from every
  push manifest, as always.
- **Red-team findings (pass 3):** load-smoke numbers are in-process
  and labelled as such; the 5 s max is first-request warmup and is
  disclosed in PERFORMANCE.md rather than averaged away silently.
- **Status:** VERIFIED — TRUTH_LEDGER L-082…L-086; L-087 BLOCKED (Docker).
