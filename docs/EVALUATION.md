# Evaluation (measured 2026-11-17, ./eval.sh)

| Dataset | Size | Metric | Result | Gate |
|---|---|---|---|---|
| matching_pairs.json | 244 pairs (120 match / 124 no-match) | false-merge rate | **0.0000** | < 0.01 ✓ |
| | | false-split rate | 0.0167 | reported |
| relevance_pk.json | 50 PK queries / 26-item catalog | hit-rate@5 | **1.000** | ≥ 0.90 ✓ |
| | | MRR | 1.000 | reported |
| | | precision@5 | 0.200 | construction cap (1 relevant item/query) — reported for transparency, not gated |
| landed_golden.json | 12 cases | totals vs independent recomputation from rule tables | all within 0.5% | pytest gate ✓ |
| scam_ads.json | 16 synthetic ads | indicator recall | **1.000** (8/8) | ≥ 0.85 ✓ |
| | | legit false-flag rate | 0.000 (0/8) | ≤ 0.25 ✓ |

Datasets are synthetic by construction (labels correct by template
design) and are labelled as such in the files. They measure the
algorithms, not live marketplace quality — live-data evaluation needs
compliance-approved sources (see COMPLIANCE.md).
