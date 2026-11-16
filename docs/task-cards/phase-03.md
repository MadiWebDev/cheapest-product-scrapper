# Task card — Phase 3: adapter framework hardening

- **Goal:** manifests for all adapters, contract tests vs fixtures,
  drift output wired to health + admin, SSRF extension.
- **Acceptance:** 30 manifests generated from the registry (cannot drift
  silently — regenerate, don't hand-edit) ✓; contract tests for amazon /
  ebay / daraz against a labelled synthetic fixture ✓; run_connector
  records every run into AdapterHealth, surfaced in /api/admin/connectors
  and /api/adapters ✓; SSRF guard rejects credentials-in-URL ✓.
- **Tests added:** test_adapters.py (8). Suite: 46 passed.
- **Review findings (pass 2):** manifest compliance_status is derived
  from the compliance records at generation time — a record change
  requires regeneration; the adapters API reads the manifest, not the
  record, so staleness would be visible as a mismatch (contract test
  asserts daraz=blocked).
- **Red-team findings (pass 3):** credentials-in-URL (`user:pass@host`)
  was accepted by the SSRF guard — now rejected with a test. DNS-based
  checks already cover private/loopback/link-local/reserved targets.
- **Status:** VERIFIED — TRUTH_LEDGER L-028…L-030.
