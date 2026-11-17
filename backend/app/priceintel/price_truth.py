"""Price Truth (directive §10): fair-price band, Price Confidence Index,
glitch-price quarantine. All formulas are deterministic and expose their
components — no black-box scores.
"""
from __future__ import annotations

import statistics

MIN_BAND_SAMPLE = 5
GLITCH_DROP = 0.60  # >60% below the group median -> quarantine


def fair_price_band(prices: list[float], window: str = "current search results") -> dict:
    """Median/IQR band. Hidden when the sample is too small to be honest."""
    clean = sorted(p for p in prices if p and p > 0)
    n = len(clean)
    if n < MIN_BAND_SAMPLE:
        return {"hidden": True, "sample_size": n, "window": window,
                "reason": f"fair-price band needs at least {MIN_BAND_SAMPLE} offers (have {n})"}
    q1, med, q3 = statistics.quantiles(clean, n=4, method="inclusive")[0], statistics.median(clean), statistics.quantiles(clean, n=4, method="inclusive")[2]
    return {"hidden": False, "sample_size": n, "window": window,
            "median": round(med, 2), "q1": round(q1, 2), "q3": round(q3, 2),
            "iqr": round(q3 - q1, 2), "low": round(q1, 2), "high": round(q3, 2)}


def band_position(price: float, band: dict) -> str | None:
    if band.get("hidden"):
        return None
    if price < band["low"]:
        return "below_band"
    if price > band["high"]:
        return "above_band"
    return "in_band"


def is_glitch(price: float, median: float) -> bool:
    """A price more than 60% below the group median is quarantined
    pending re-verification — it is shown, flagged, and never wins
    'best price'."""
    return bool(median and median > 0 and price < median * (1 - GLITCH_DROP))


def price_confidence_index(*, band_sample: int, shipping_certainty: str,
                           fx_stale: bool, rating: float | None,
                           review_count: int, quarantined: bool) -> dict:
    components: dict[str, int] = {}
    score = 50
    band_pts = 15 if band_sample >= 8 else 8 if band_sample >= MIN_BAND_SAMPLE else 0
    components["band_sample"] = band_pts
    score += band_pts
    ship_pts = 10 if shipping_certainty == "CONFIRMED" else 0
    components["shipping_known"] = ship_pts
    score += ship_pts
    fx_pts = -10 if fx_stale else 10
    components["fx_freshness"] = fx_pts
    score += fx_pts
    rev_pts = 10 if (rating and review_count >= 50) else 5 if (rating and review_count >= 1) else 0
    components["review_evidence"] = rev_pts
    score += rev_pts
    if quarantined:
        components["glitch_quarantine"] = -15
        score -= 15
    return {"index": max(0, min(100, score)), "components": components}
