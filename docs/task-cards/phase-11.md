# Task card — Phase 11: admin completion + developer API + seller intel

- **Goal:** RBAC-protected console, match-review queue that actually
  changes matcher behavior, seller scorecards with right-of-reply,
  audit logs, quota'd developer API, tenant-isolated seller intel.
- **Acceptance:** RBAC matrix tested ✓; review decisions write
  matcher overrides + audit entries ✓; scorecard/reply/undercut
  tested with tenant isolation ✓; dev keys hashed, quota 429 tested ✓.
- **Tests added:** test_admin_devapi.py (5). Suite: 89 passed.
- **Review findings (pass 2):** the review queue is useless if decisions
  don't change behavior — decisions write through to matching_v2
  overrides consulted before algorithmic scoring.
- **Red-team findings (pass 3):** (1) raw admin/dev keys exist only in
  the creation response; stores hold SHA-256 hashes (test asserts the
  raw key is absent). (2) Legacy /api/admin/* endpoints remain
  unauthenticated — recorded as L-069 PLANNED for the Phase 14
  security pass rather than silently leaving the gap undocumented.
- **Status:** VERIFIED — L-065…L-068; L-069 PLANNED (Phase 14).
