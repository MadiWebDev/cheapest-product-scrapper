# STATE — PRICEINTEL v3 resume file (directive §1.4)

**Current phase:** 0 — Audit, foundation, Agent Operating System.
**Last completed task:** Phase 0 baselines measured; boot defects B-01/B-05
fixed; requirements repaired; verify/eval/e2e/audit-truth scripts created.
**Next three tasks:**
1. Phase 1: compliance registry + gate (Daraz + 2 PK sources reviewed
   from public pages), certainty-labelled landed cost in the skeleton
   path, trust top-3 reasons, `GET /go/:offerId` tracked redirect.
2. Phase 1: API journey test (TestClient) search → match → landed →
   trust → rank → /go; three-pass notes on the phase task card.
3. Phase 1 commit + push (push-files), verify remote head.

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
