# Task card — Phase 2: location intelligence + country config

- **Goal:** §5 location priority with manual-wins, country configuration
  data, lakh/crore formatting, PK depth (PTA, COD, cities).
- **Acceptance:** resolution priority unit-tested incl. unknown-code
  fallback ✓; PK config carries PTA note, COD, 12 cities ✓; format_money
  backend + lib/format.ts frontend parity ✓ (build green, 87.3 kB First
  Load JS shared); admin compliance review endpoint added to the existing
  admin router (extended, not rebuilt) ✓.
- **Tests added:** test_location.py (7). Suite: 38 passed.
- **Review findings (pass 2):** approval write-path must never open the
  gate accidentally — approval without reviewer or expiry raises (test).
  Frontend country memory uses the same "manual wins" rule: the stored
  value is itself a past manual choice, restored on load.
- **Red-team findings (pass 3):** resolve_country ignores unknown codes
  instead of trusting them (test); IP country is a parameter only — no
  spoofable header is read directly by the resolver.
- **Status:** VERIFIED — TRUTH_LEDGER L-023…L-027.
