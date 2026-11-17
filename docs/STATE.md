# STATE — PRICEINTEL v3 resume file (directive §1.4)

**Current phase:** 4 — Matching v2 (complete); Phase 5 next.
**Last completed task:** Phase 4 — matching v2 (confidence + reasons,
9 hard separation axes), 244-pair eval (false-merge 0.0000, false-split
0.0167), PK relevance set (hit-rate@5 1.000). Suite: 51 passed.
Pushes confirmed: p0 3ef8628d, p1 6538b242, p2 1f71a35e, p3 2000846d.
**Next three tasks:**
1. Phase 5: landed v2 golden cases (>=10 incl. UAE->PK phone) in
   eval + tests; FX failover verification tests.
2. Phase 5: fair-price band + Price Confidence Index + glitch
   quarantine (>60% drop) in a price-truth module wired to search.
3. Phase 5 commit + push.

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
