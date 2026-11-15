from __future__ import annotations
import json, pathlib
from .models import RawOffer, LandedBreakdown
DATA=pathlib.Path(__file__).parent.parent/"data"
def _load(name):
    return json.loads((DATA/name).read_text())
VAT=_load("vat_gst.json"); DUTY=_load("duty.json")
# fallback static FX (USD base) used only when live providers fail AND no cache; flagged stale by caller
FALLBACK_FX={"USD":1.0,"EUR":0.92,"GBP":0.79,"PKR":278.0,"INR":83.0,"AED":3.67,"SAR":3.75,"JPY":155.0,"AUD":1.52,"CAD":1.36,"TRY":32.5,"PLN":3.95,"ZAR":18.2,"BRL":5.1,"MXN":17.0,"SGD":1.34,"CNY":7.2}
def convert(amount: float, from_ccy: str, to_ccy: str, fx: dict[str,float]) -> float:
    if from_ccy==to_ccy: return amount
    usd=amount/fx[from_ccy]; return usd*fx[to_ccy]
def landed_price(offer: RawOffer, ship_to: str, user_ccy: str, fx: dict[str,float]|None=None, category: str="default", fx_margin_rate: float=0.015) -> LandedBreakdown|None:
    if offer.price is None: return None
    fx=fx or FALLBACK_FX
    if offer.currency not in fx or user_ccy not in fx: return None
    item_usd=convert(offer.price, offer.currency, "USD", fx)
    ship_usd=convert(offer.shipping_price or 0.0, offer.currency, "USD", fx)
    de_min=DUTY["de_minimis_usd"].get(ship_to, 0)
    duty_rate=DUTY["duty_by_category"].get(category, DUTY["duty_by_category"]["default"])
    duty=0.0 if item_usd<=de_min else (item_usd+ship_usd)*duty_rate
    vat_rate=VAT["rates"].get(ship_to, 0.0)
    tax=(item_usd+ship_usd+duty)*vat_rate
    handling=DUTY["handling_usd"] if item_usd>de_min else 0.0
    subtotal=item_usd+ship_usd+duty+tax+handling
    total_user=convert(subtotal, "USD", user_ccy, fx)
    fx_margin=total_user*fx_margin_rate; total_user+=fx_margin
    prov={"item":"exact","shipping":"exact" if offer.shipping_price is not None else "estimated","duty":"estimated","tax":"estimated","handling":"estimated","fx":"estimated"}
    c=lambda usd: round(convert(usd,"USD",user_ccy,fx),2)
    return LandedBreakdown(item=c(item_usd), shipping=c(ship_usd), duty=c(duty), tax=c(tax), handling=c(handling), fx_margin=round(fx_margin,2), total=round(total_user,2), currency=user_ccy, provenance=prov)
def can_ship(offer: RawOffer, ship_to: str) -> bool:
    return (not offer.ships_to) or ship_to in offer.ships_to
