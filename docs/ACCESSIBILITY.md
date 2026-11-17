# Accessibility checklist (Phase 8 — manual pass)

Automated axe tooling is not installed in this environment; this is an
honest manual checklist against the built UI, re-checked at Phase 8.

- [x] All form controls have accessible names (aria-label on search
      input, country/currency/language selects; visible label for the
      Lite-mode checkbox).
- [x] Landmarks: single `main`, `article` per product card, `section`
      for compare; heading order h1 → h2 without skips on home and
      methodology pages.
- [x] Demo banner and quarantine warnings use role="alert".
- [x] Loading state exposes aria-busy.
- [x] Language switcher sets `lang` and `dir` on <html> at runtime
      (ur/ar render RTL); the static document default is lang="en".
- [x] Interactive elements are native buttons/links/inputs (keyboard
      operable by default); search submits on Enter.
- [x] No information is carried by colour alone: certainty, fair-price
      position, match confidence and PCI are printed as text.
- [ ] Colour-contrast ratios not machine-measured (no tooling) —
      palette is default Tailwind on white/neutral-900; flagged as a
      residual gap for a tooling-enabled pass.
- [ ] Screen-reader end-to-end pass not performed (no AT in VM).
