# STATE — PRICEINTEL v3 resume file (directive §1.4)

**Current phase:** 3 — Adapter hardening (complete); Phase 4 next.
**Last completed task:** Phase 3 — 30 adapter manifests generated,
contract tests (amazon/ebay/daraz vs fixture), drift → AdapterHealth →
admin/adapters API, SSRF credentials rejection. Suite: 46 passed.
Pushes confirmed: phase-0 3ef8628d, phase-1 6538b242, phase-2 1f71a35e.
**Next three tasks:**
1. Phase 4: matching v2 — confidence 0-100 + reasons, hard
   separation rules as tests.
2. Phase 4: labeled-pairs eval dataset (>=200) + false-merge metric in
   eval.sh; relevance golden set (>=50 PK queries) + precision@5.
3. Phase 4 commit + push.

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
