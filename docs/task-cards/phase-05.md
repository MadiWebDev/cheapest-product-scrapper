# Task card — Phase 5: landed v2 + price truth

- **Goal:** golden-case-verified landed cost, hourly FX with tested
  failover, fair-price band, PCI, glitch quarantine.
- **Acceptance:** 12 golden cases recomputed independently from the rule
  tables ✓; FX failover chain unit-tested, TTL daily→hourly per §10 ✓;
  band hidden below 5 samples ✓; PCI components exposed ✓; quarantine
  boundary-tested and wired (flagged, last, no Best price) ✓.
- **Tests added:** test_price_truth.py (5). Suite: 56 passed.
- **Review findings (pass 2):** the golden test's None-case check had a
  bug (`exp.get("result")` is None for every case) — caught by running
  it; fixed to an explicit key check. Expectations were verified against
  the actual VAT table before asserting (GB 0.20, DE 0.19, PK 0.17).
- **Red-team findings (pass 3):** quarantine uses the group median of
  landed totals in the target currency (never raw mixed-currency
  prices); a quarantined offer stays visible with its reason — hiding
  it silently would be less honest than flagging it.
- **Status:** VERIFIED — TRUTH_LEDGER L-034…L-039.
