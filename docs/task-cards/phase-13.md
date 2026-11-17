# Task card — Phase 13: §16.2 expansion features

- **Goal:** the remaining §16.2 features, flag-gated, in directive
  priority order, with honest scopes.
- **Built (all tested):** used-phone safety kit (guidance content),
  compatibility checker (plug/voltage/carrier/PTA-registration rules),
  budget planner, purchase-outcome feedback + calibration signal,
  price-match evidence pack, alternatives engine, Deal Passport,
  smart digest job (flag default off).
- **Not built / scoped honestly:** radio-band-level phone
  compatibility (needs a device band database we cannot legitimately
  obtain — the checker covers plug/voltage/carrier/registration and
  says so); outcome reports raise a calibration flag for review rather
  than silently rewriting trust scores.
- **Tests added:** test_features.py (7). Suite: 96 passed.
- **Review findings (pass 2):** every endpoint checks its flag first
  and returns 503 when disabled — a flag that only hides UI would not
  be a real gate.
- **Red-team findings (pass 3):** the evidence pack carries the
  affiliate disclosure and per-offer certainty labels, so a screenshot
  of it can't be mistaken for a guaranteed price.
- **Status:** VERIFIED — TRUTH_LEDGER L-073…L-081.
