#!/usr/bin/env python3
"""Ranking fairness audit (directive §12): on a fixed benchmark
(DEMO_MODE catalog), verify that display order is explained by
landed cost + trust + delivery only, and that no connector is
systematically positioned better than its value scores justify.

Exit 1 on any violation. Run: DEMO_MODE handled internally.
"""
import os
import sys
from pathlib import Path

os.environ["DEMO_MODE"] = "true"
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))


def main() -> int:
    import importlib
    import app.connectors.registry as reg
    importlib.reload(reg)
    import app.services.search as ss
    ss.REGISTRY = reg.REGISTRY

    violations = []
    per_connector: dict[str, list[tuple[float, float]]] = {}
    for query in ("iphone 15", "samsung galaxy", "headphones"):
        r = ss.search(query, {}, "PK", "PKR", connectors=["demo"])
        for p in r["products"]:
            offers = p["offers"]
            scores = [o["value_score"] for o in offers]
            if scores != sorted(scores, reverse=True):
                # quarantined-last is the one allowed deviation; check within partitions
                part = [o for o in offers if not o.get("quarantined")]
                ps = [o["value_score"] for o in part]
                if ps != sorted(ps, reverse=True):
                    violations.append(f"order not value-sorted in {p['title']}")
            n = len(offers)
            for i, o in enumerate(offers):
                pos_pct = 1.0 - (i / max(n - 1, 1)) if n > 1 else 1.0
                val_pct = 1.0
                if n > 1:
                    rank = sorted(scores, reverse=True).index(o["value_score"])
                    val_pct = 1.0 - (rank / max(n - 1, 1))
                per_connector.setdefault(o["offer"]["connector"], []).append((pos_pct, val_pct))
    for conn, pairs in per_connector.items():
        mean_pos = sum(a for a, _ in pairs) / len(pairs)
        mean_val = sum(b for _, b in pairs) / len(pairs)
        boost = mean_pos - mean_val
        print(f"fairness: {conn}: offers={len(pairs)} mean_position_pct={mean_pos:.3f} "
              f"mean_value_pct={mean_val:.3f} boost={boost:+.3f}")
        if boost > 0.15:
            violations.append(f"{conn} positioned {boost:.2f} better than its value scores justify")
    if violations:
        for v in violations:
            print("fairness VIOLATION:", v)
        return 1
    print("fairness: OK — order is explained by value score (landed + trust + delivery)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
