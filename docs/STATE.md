# STATE — PRICEINTEL v3 resume file (directive §1.4)

**Current phase:** 2 — Location intelligence (complete); Phase 3 next.
**Last completed task:** Phase 2 — location resolution (manual wins),
country config (16 countries, PK PTA/COD/cities), lakh/crore formatting
backend+frontend, admin compliance review endpoint. Suite: 38 passed.
Pushes confirmed: phase-0 3ef8628d, phase-1 6538b242.
**Next three tasks:**
1. Phase 3: manifest.json per adapter + registry surfacing.
2. Phase 3: contract tests vs fixtures for top adapters; drift output
   wired to adapter health + admin.
3. Phase 3 commit + push.

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
