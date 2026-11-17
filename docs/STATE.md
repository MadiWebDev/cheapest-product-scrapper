# STATE — PRICEINTEL v3 resume file (directive §1.4)

**Current phase:** 11 — Admin + dev API (complete); Phase 12 next. PUSHES PAUSED (B3-007).
**Last completed task:** Phase 11 — RBAC admin console, match-review
queue with matcher overrides + audit log, seller scorecards/reply/
undercuts with tenant isolation, developer API keys + quotas.
Suite: 89 passed. Known gap: legacy /api/admin/* auth (L-069, Phase 14).
Pushes confirmed: p0 3ef8628d, p1 6538b242, p2 1f71a35e, p3 2000846d.
Phase 4 push UNVERIFIED (B3-007) — reconcile via list_commits before
any re-push; phases 4-5 commits are local until then.
**Next three tasks:**
1. Phase 12: mobile/ (Expo) + extension/ (MV3) scaffolds with
   real API client code; barcode/snap entry points behind flags.
2. Phase 12: deep links from web product cards to the app routes.
3. Phase 12 commit (push pending B3-007 reconciliation).

**Open blockers:** B3-001 Docker absent in VM; B3-002 `.github/workflows/*`
push 403; B3-003 no live marketplace keys; B3-004 no LLM key; B3-005 no
Paddle/Telegram/SMTP creds; B3-006 no Playwright. See BLOCKERS.md.

**Run commands:**
- Tests: `cd backend && ~/workspace/cpf-venv/bin/python -m pytest -q`
  (venv has the full requirements set as of Phase 0; unset proxy vars or
  rely on tests/conftest.py which strips them)
- All checks: `./verify.sh` · Evals: `./eval.sh` · Journeys: `./e2e.sh`
  · Truth audit: `./audit-truth.sh`
- App smoke: `DEMO_MODE=true` + TestClient (tools/smoke.py)

**Known failing items:** none in the test suite. `.github/workflows/ci.yml`
cannot be pushed (B3-002). Local git worktree shows `D backend/.coverage`
(pre-existing, gitignored — leave alone; never push `.env`/`.coverage`).

**Decisions pending:** none — stack reconciliation decided in D-025…D-032.

**Active task cards:** docs/task-cards/phase-00.md (this phase);
phase-01 card created when Phase 1 starts.
