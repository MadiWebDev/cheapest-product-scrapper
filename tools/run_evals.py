#!/usr/bin/env python3
"""Evaluation runner (directive §38). Computes real metrics for every
dataset present under eval/ and enforces the gates:

- matching_pairs.json: false-merge rate < 1% (directive gate);
  false-split rate reported.
- relevance_pk.json: hit-rate@5 >= 0.90 over the catalog fixture
  (one relevant item per query, so hit-rate@5 is the meaningful
  metric; precision@5 is capped at 0.2 by construction and reported
  for transparency).

Datasets not yet built are reported PLANNED with their owning phase.
"""
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

FALSE_MERGE_GATE = 0.01
HIT_RATE_GATE = 0.90


def _offer(d, i):
    from app.domain.models import RawOffer
    return RawOffer(connector="eval", title=d["title"], url=f"https://eval.example/{i}",
                    price=100.0, brand=d.get("brand"), attributes=d.get("attributes", {}),
                    condition=d.get("condition", "new"))


def eval_matching() -> tuple[bool, str]:
    from app.domain.matching_v2 import MERGE_THRESHOLD, match_confidence
    data = json.loads((ROOT / "eval" / "matching_pairs.json").read_text())
    pairs = data["pairs"]
    fm = fs = nm = ns = 0
    for i, p in enumerate(pairs):
        m = match_confidence(_offer(p["a"], f"a{i}"), _offer(p["b"], f"b{i}"))
        merged = m["hard_block"] is None and m["score"] >= MERGE_THRESHOLD
        if p["label"] == "no_match":
            nm += 1
            fm += 1 if merged else 0
        else:
            ns += 1
            fs += 0 if merged else 1
    fmr = fm / nm if nm else 0.0
    fsr = fs / ns if ns else 0.0
    ok = fmr < FALSE_MERGE_GATE
    return ok, (f"matching: {len(pairs)} pairs | false-merge {fm}/{nm} = {fmr:.4f} "
                f"(gate < {FALSE_MERGE_GATE}) | false-split {fs}/{ns} = {fsr:.4f}")


def eval_relevance() -> tuple[bool, str]:
    from app.domain.matching import token_set_ratio
    cat = json.loads((ROOT / "eval" / "catalog_fixture.json").read_text())["items"]
    qs = json.loads((ROOT / "eval" / "relevance_pk.json").read_text())["queries"]
    hits = p5 = rr = 0.0
    for q in qs:
        ranked = sorted(cat, key=lambda it: token_set_ratio(q["query"], it["title"]),
                        reverse=True)
        top5 = ranked[:5]
        h = sum(1 for it in top5 if it["id"] in q["relevant_ids"])
        hits += 1 if h else 0
        p5 += h / 5
        for rank, it in enumerate(ranked, 1):
            if it["id"] in q["relevant_ids"]:
                rr += 1 / rank
                break
    n = len(qs)
    hr = hits / n
    ok = hr >= HIT_RATE_GATE
    return ok, (f"relevance: {n} PK queries | hit-rate@5 {hr:.3f} (gate >= {HIT_RATE_GATE}) "
                f"| precision@5 {p5 / n:.3f} (capped 0.2 by construction) | MRR {rr / n:.3f}")


def main() -> int:
    failures = []
    for name, phase in EXPECTED.items():
        if not (ROOT / "eval" / name).exists():
            print(f"eval: {name} PLANNED ({phase})")
    if (ROOT / "eval" / "matching_pairs.json").exists():
        ok, msg = eval_matching()
        print("eval:", msg)
        if not ok:
            failures.append(msg)
    if (ROOT / "eval" / "relevance_pk.json").exists():
        ok, msg = eval_relevance()
        print("eval:", msg)
        if not ok:
            failures.append(msg)
    if failures:
        print("eval: FAILED")
        return 1
    print("eval: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
