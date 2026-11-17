# Task card — Phase 6: trust v2 + ranking fairness

- **Goal:** decomposable trust with stored inputs, warning categories,
  per-result ranking explanation, fairness audit, and a proof that
  ranking cannot see monetization data.
- **Acceptance:** trust record (score/version/inputs/components/
  reasons/warnings) per offer ✓; 6 warning categories, indicator
  language ✓; ranking block per offer ✓; fairness audit script exits 0
  on the fixed benchmark ✓; architectural + behavioral isolation tests ✓.
- **Tests added:** test_trust_ranking.py (5). Suite: 61 passed.
- **Review findings (pass 2):** a static import scan alone would be a
  weak proof (search.py legitimately imports the /go offer store), so
  the scan targets data-access identifiers and is paired with the
  behavioral test — affiliate env on/off produces byte-identical
  scores and ordering.
- **Red-team findings (pass 3):** the fairness audit's one allowed
  deviation is the quarantine partition (quarantined offers rank last
  by design); the audit checks value-sortedness within partitions
  rather than pretending the deviation doesn't exist.
- **Status:** VERIFIED — TRUTH_LEDGER L-040…L-043.
