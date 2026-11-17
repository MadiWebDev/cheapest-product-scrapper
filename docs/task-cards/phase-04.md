# Task card — Phase 4: matching v2 + eval datasets

- **Goal:** explainable match confidence with hard separation rules;
  labeled-pairs eval with a false-merge gate; PK relevance golden set.
- **Acceptance:** match_confidence returns score + reasons + hard_block
  ✓; all 9 separation axes unit-tested ✓; 244 labeled pairs generated
  deterministically (labels correct by construction) ✓; eval.sh gates:
  false-merge < 1% (measured 0.0000), hit-rate@5 >= 0.90 (measured
  1.000) ✓; search exposes match_confidence/match_reasons + variant ✓.
- **Tests added:** test_matching_v2.py (5, incl. eval-gate test). Suite: 51 passed.
- **Review findings (pass 2):** first measurement caught a real defect —
  iPhone 15 vs 14 merged at 83 because brand_model_key cannot extract
  bare-number models. Fixed with an alphabetic-skeleton model-token
  comparison (s24/s23, 15/14, 1000xm5/xm4). Threshold then chosen from
  data: 60 gives FM 0.00% / FS 1.67%.
- **Red-team findings (pass 3):** precision@5 is a misleading metric
  with one relevant item per query (cap 0.2) — the runner reports it
  for transparency but gates on hit-rate@5. Storage tokens are excluded
  from generation skeletons so 128GB/256GB stay a storage-axis block,
  not a generation block.
- **Status:** VERIFIED — TRUTH_LEDGER L-031…L-033.
