# Task card — Phase 8: web app completion

- **Goal:** cards carry the v3 evidence (certainty, fair position,
  match confidence, freshness, PCI, trust reason), evidence drawer +
  methodology page, i18n + RTL, Lite mode, accessibility pass.
- **Acceptance:** build green, First Load JS shared 87.3 kB vs 90 kB
  baseline ✓; check-i18n passes 18/18 keys ur+ar ✓; methodology route
  static ✓; accessibility manual checklist in docs/ACCESSIBILITY.md ✓.
- **Tests/evidence:** npm run build output; node scripts/check-i18n.mjs.
  Backend suite unaffected (69 passed).
- **Review findings (pass 2):** a TS error (optional-before-required
  parameter in the freshness helper) was caught by the build and fixed —
  the build is the frontend's verify gate.
- **Red-team findings (pass 3):** product detail is delivered as the
  card evidence drawer because the v1 architecture has no product
  route or product-by-id API; the ledger says so instead of claiming a
  product page exists. Contrast/screen-reader gaps are recorded as
  IMPLEMENTED-UNVERIFIED, not waved through.
- **Status:** VERIFIED — L-049…L-052, L-054; L-053 IMPLEMENTED-UNVERIFIED.
