"""Trust v2 (directive §11): a decomposable trust score that STORES its
inputs and formula version with every result, plus explicit
suspicious-offer warning categories. Indicators only — a warning is a
risk signal, never an accusation of fraud.
"""
from __future__ import annotations

from app.domain.models import RawOffer
from app.domain.scoring import quality_score, top_reasons

VERSION = "trust-v2.1"


def suspicious_categories(offer: RawOffer, median: float | None, expl: dict) -> list[dict]:
    cats: list[dict] = []
    if median and offer.price and offer.price < 0.5 * median:
        cats.append({"id": "price_far_below_median",
                     "text": "Price is less than half the market median — counterfeit/grey-market risk indicator (not proof)"})
    if expl.get("fake_review_penalty", 0) > 0:
        cats.append({"id": "review_pattern_risk",
                     "text": "Review-pattern risk signals (rating high relative to review volume/age)"})
    if offer.seller_age_years and offer.seller_age_years < 1 and offer.price and median and offer.price > median:
        cats.append({"id": "new_seller_high_value",
                     "text": "Seller account is under a year old and the item is priced above the median"})
    if offer.rating and offer.rating >= 4.5 and offer.review_count < 10:
        cats.append({"id": "thin_review_base",
                     "text": "Very high rating on a very small number of reviews"})
    if not offer.buyer_protection:
        cats.append({"id": "no_buyer_protection",
                     "text": "No buyer protection reported for this offer"})
    if offer.returns_days == 0:
        cats.append({"id": "no_returns",
                     "text": "No returns window reported for this offer"})
    return cats


def trust_v2(offer: RawOffer, median: float | None) -> dict:
    """Full trust record: score + version + stored inputs + components
    + top reasons + warning categories. Reproducible from inputs."""
    score, expl = quality_score(offer, median)
    inputs = {
        "seller_rating": offer.seller_rating,
        "seller_feedback_count": offer.seller_feedback_count,
        "seller_age_years": offer.seller_age_years,
        "official_store": offer.official_store,
        "rating": offer.rating,
        "review_count": offer.review_count,
        "price": offer.price,
        "market_median": median,
        "price_vs_median": round(offer.price / median, 4) if (offer.price and median) else None,
        "condition": offer.condition,
        "warranty": offer.warranty,
        "returns_days": offer.returns_days,
        "buyer_protection": offer.buyer_protection,
    }
    return {
        "score": score,
        "version": VERSION,
        "inputs": inputs,
        "components": expl,
        "reasons": top_reasons(expl, offer),
        "warnings": suspicious_categories(offer, median, expl),
    }
