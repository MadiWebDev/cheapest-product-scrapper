import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from app.domain.models import RawOffer
from app.domain.landed import landed_price, can_ship
from app.domain.scoring import quality_score, bayesian_rating, value_score
from app.domain.matching import group_offers, token_set_ratio
from app.domain.normalize import normalize_availability, clean_price
FX={"USD":1.0,"EUR":0.92,"GBP":0.79,"PKR":278.0}
def offer(**kw):
    d=dict(connector="test", title="Apple iPhone 15 128GB", url="https://x/1", price=100.0, currency="USD", rating=4.5, review_count=200, seller_rating=98.0, seller_age_years=4, returns_days=30, buyer_protection=True)
    d.update(kw); return RawOffer(**d)
def test_landed_includes_tax_over_de_minimis():
    b=landed_price(offer(price=900, shipping_price=10), "GB","GBP",FX,category="electronics")
    assert b and b.total>b.item and b.tax>0 and b.provenance["tax"]=="estimated"
def test_landed_under_de_minimis_no_duty():
    b=landed_price(offer(price=50), "US","USD",FX); assert b and b.duty==0
def test_can_ship():
    assert can_ship(offer(ships_to=["US"]), "US") and not can_ship(offer(ships_to=["US"]), "GB")
def test_bayesian_pulls_low_count_to_prior():
    assert bayesian_rating(5.0, 2) < 4.2
def test_quality_range_and_official_bonus():
    q1,_=quality_score(offer()); q2,_=quality_score(offer(official_store=True))
    assert 0<=q1<=100 and q2>q1
def test_counterfeit_penalty():
    q,_=quality_score(offer(price=10), market_median=100); q2,_=quality_score(offer(price=95), market_median=100); assert q<q2
def test_value_weights():
    assert 0<=value_score(80,100,100,3)<=100
def test_grouping_exact_gtin_and_accessory_separation():
    a=offer(gtin="123"); b=offer(connector="ebay", gtin="123", title="Apple iPhone 15 128GB Black")
    c=offer(title="iPhone 15 Case Cover", gtin=None)
    gs=group_offers([a,b,c]); assert len(gs)==2 and max(len(g["offers"]) for g in gs)==2
def test_availability_and_price_clean():
    assert normalize_availability("Only 2 left in stock").value=="low_stock"
    assert clean_price("$1,299.99")==1299.99 and clean_price("n/a") is None
def test_token_ratio():
    assert token_set_ratio("iphone 15 case","iphone 15 case")>0.9
