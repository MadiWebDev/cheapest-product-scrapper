# Task card — Phase 12: mobile + extension scaffolds

- **Goal:** Expo app + MV3 extension sharing the API contracts, with
  honest statuses and flag-gated camera features.
- **Acceptance:** mobile/lib/api.ts is a real typed client for search +
  alerts + /go ✓; extension popup implements the full extract →
  compare → best-landed flow ✓; manifests valid ✓; JS syntax-checked
  ✓; barcode/snap flags disabled with explicit errors ✓; web cards
  deep-link via priceintel:// ✓; frontend build green ✓.
- **Tests/evidence:** node --check on all extension JS; JSON manifest
  parse; npm run build. No runtime exists here for either platform —
  both are IMPLEMENTED-UNVERIFIED in the ledger, not VERIFIED.
- **Review findings (pass 2):** extension host_permissions are scoped
  to the API origin only, and permissions to activeTab only — no
  broad host access for a scaffold.
- **Red-team findings (pass 3):** the extension sends the tab URL to
  the user's own backend extractor, which is SSRF-guarded server-side;
  nothing is sent to third parties. The mobile app stores no secrets;
  the API base is public configuration.
- **Status:** IMPLEMENTED-UNVERIFIED — L-070, L-071; L-072 VERIFIED.
