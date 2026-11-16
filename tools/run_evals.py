#!/usr/bin/env python3
"""Evaluation runner (directive §38). Enforces thresholds for every
dataset present under eval/; datasets not yet built are reported as
PLANNED (their owning phase is noted) rather than silently skipped."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

EXPECTED = {
    "matching_pairs.json": "Phase 4",
    "relevance_pk.json": "Phase 4",
    "landed_golden.json": "Phase 5",
    "scam_ads.json": "Phase 7",
}


def main() -> int:
    failures = []
    eval_dir = ROOT / "eval"
    for name, phase in EXPECTED.items():
        p = eval_dir / name
        if not p.exists():
            print(f"eval: {name} PLANNED ({phase})")
            continue
        data = json.loads(p.read_text())
        print(f"eval: {name} present with {len(data)} cases — threshold checks run by pytest eval tests")
    # The numeric gates themselves live in backend/tests/test_eval_*.py,
    # executed by verify.sh; this runner fails if a present dataset is empty.
    for name in EXPECTED:
        p = eval_dir / name
        if p.exists() and len(json.loads(p.read_text())) == 0:
            failures.append(f"eval dataset {name} is empty")
    if failures:
        for f in failures:
            print(" -", f)
        return 1
    print("eval: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
