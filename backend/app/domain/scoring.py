from __future__ import annotations
import math, statistics
from .models import RawOffer
def bayesian_rating(rating: float|None, count: int, prior_mean: float=3.8, prior_weight: int=50) -> float:
    if rating is None: return prior_mean
    return (rating*count + prior_mean*prior_weight)/(count+prior_weight)
def fake_review_penalty(offer: RawOffer) -> float:
    p=0.0
    if offer.rating and offer.rating>=4.8 and offer.review_count<20: p+=8
    if offer.rating and offer.rating==5.0 and offer.review_count>=10: p+=6
    if offer.review_count>0 and offer.seller_feedback_count==0: p+=5
    return min(p,20.0)
def counterfeit_risk(offer: RawOffer, market_median: float|None) -> float:
    risk=0.0
    if market_median and offer.price and offer.price < 0.55*market_median: risk+=25
    if offer.seller_age_years<0.5 and offer.brand: risk+=10
    if not offer.image and offer.brand: risk+=5
    return min(risk,40.0)
def quality_score(offer: RawOffer, market_median: float|None=None) -> tuple[float, dict]:
    br=bayesian_rating(offer.rating, offer.review_count)
    rating_pts=(br/5.0)*35
    volume_pts=min(15.0, math.log10(max(offer.review_count,1))*5) if offer.review_count else 0.0
    seller_pts=0.0
    if offer.seller_rating: seller_pts+=min(12.0, offer.seller_rating/100*12 if offer.seller_rating>5 else offer.seller_rating/5*12)
    if offer.official_store: seller_pts+=8
    elif offer.seller_age_years>=3: seller_pts+=4
    cond_pts={"new":8,"refurbished":5,"open-box":4,"used":2}.get(offer.condition,4)
    warranty_pts=5 if offer.warranty else 0
    returns_pts=5 if offer.returns_days>=30 else (3 if offer.returns_days>0 else 0)
    protection_pts=5 if offer.buyer_protection else 0
    fake=fake_review_penalty(offer); cf=counterfeit_risk(offer, market_median)
    total=max(0.0,min(100.0, rating_pts+volume_pts+seller_pts+cond_pts+warranty_pts+returns_pts+protection_pts-fake-cf))
    expl={"bayesian_rating":round(br,2),"rating_points":round(rating_pts,1),"review_volume_points":round(volume_pts,1),"seller_points":round(seller_pts,1),"condition_points":cond_pts,"warranty_points":warranty_pts,"returns_points":returns_pts,"buyer_protection_points":protection_pts,"fake_review_penalty":fake,"counterfeit_risk_penalty":cf,"market_median":market_median}
    return round(total,1), expl
def value_score(quality: float, landed_total: float|None, best_total: float|None, delivery_days: int|None, weights: dict|None=None) -> float:
    w=weights or {"price":0.4,"quality":0.35,"speed":0.15,"reliability":0.10}
    s=sum(w.values()) or 1; w={k:v/s for k,v in w.items()}
    price_pts=100.0 if (landed_total and best_total and landed_total>0) else 50.0
    if landed_total and best_total and landed_total>best_total: price_pts=max(0.0, 100*(best_total/landed_total))
    speed_pts=50.0 if delivery_days is None else max(0.0, 100-delivery_days*6)
    reliability=quality  # reliability proxied by quality engine seller/protection components
    return round(w["price"]*price_pts + w["quality"]*quality + w["speed"]*speed_pts + w["reliability"]*reliability,1)
def median_price(offers: list[RawOffer]) -> float|None:
    ps=[o.price for o in offers if o.price]; return statistics.median(ps) if ps else None
