# STATE — PRICEINTEL v3 resume file (directive §1.4)

**Current phase:** 1 — Walking skeleton (complete); Phase 2 next.
**Last completed task:** Phase 1 — compliance gate + records (Daraz
blocked by its terms §2E; PriceOye/Telemart pending), certainty labels +
trust reasons in search output, /go tracked redirect, journey tests.
Suite: 31 passed.
**Next three tasks:**
1. Phase 2: location intelligence (priority order, manual wins),
   country config data incl. PK (PTA note, COD, holidays), PKR
   lakh/crore formatting backend + frontend.
2. Phase 2: registry/admin extension for compliance records.
3. Phase 2 commit + push.

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
