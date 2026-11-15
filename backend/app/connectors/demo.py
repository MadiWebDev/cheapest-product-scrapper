from __future__ import annotations
from app.connectors.base import BaseConnector
from app.domain.models import RawOffer
CATALOG=[
 ("Apple iPhone 15 128GB Black",799.0,"USD","0194253400011"),("Samsung Galaxy S24 256GB",849.0,"USD","8806090011223"),
 ("Sony WH-1000XM5 Wireless Headphones",349.0,"USD","0027242919999"),("Apple MacBook Air M3 13-inch",1099.0,"USD","0194253400028"),
 ("Dyson V15 Detect Vacuum",649.0,"USD","5025155011111"),("Nike Air Force 1 07 White UK9",110.0,"USD","0019520011111")]
class DemoConnector(BaseConnector):
    name="demo"; compliance_note="DEMO ONLY — active only when DEMO_MODE=true; every offer flagged demo=true."
    def search(self, query, filters=None, country="US"):
        q=query.lower(); out=[]
        for title,price,ccy,gtin in CATALOG:
            if any(w in title.lower() for w in q.split()) or q in title.lower():
                out.append(RawOffer(connector="demo", title=title, url=f"https://demo.example/{gtin}", price=price, currency=ccy, gtin=gtin, rating=4.6, review_count=1200, seller_name="Demo Store", seller_rating=98.0, seller_age_years=5, shipping_price=0.0, availability="in_stock", delivery_days=3, returns_days=30, buyer_protection=True, official_store=True, demo=True))
        return out
    def get_product(self, url_or_id): return []
