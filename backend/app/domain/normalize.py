from __future__ import annotations
import re
from .models import Availability
def normalize_availability(text: str|None, qty: int|None=None) -> Availability:
    if qty is not None:
        if qty==0: return Availability.OUT_OF_STOCK
        if qty<=3: return Availability.LOW_STOCK
        return Availability.IN_STOCK
    t=(text or "").lower()
    if any(k in t for k in ("out of stock","sold out","unavailable","oos")): return Availability.OUT_OF_STOCK
    if "preorder" in t or "pre-order" in t: return Availability.PREORDER
    if "backorder" in t or "back order" in t: return Availability.BACKORDER
    if any(k in t for k in ("only","low stock","left in stock","hurry")): return Availability.LOW_STOCK
    if any(k in t for k in ("in stock","available","in-stock")): return Availability.IN_STOCK
    return Availability.UNKNOWN
def clean_price(v) -> float|None:
    if v is None: return None
    if isinstance(v,(int,float)): return float(v) if v>0 else None
    m=re.search(r"[\d][\d,]*\.?\d*", str(v).replace("\xa0"," "))
    if not m: return None
    try:
        x=float(m.group(0).replace(",","")); return x if x>0 else None
    except ValueError: return None
def normalize_title(t: str) -> str:
    return re.sub(r"\s+"," ", re.sub(r"[^a-z0-9 ]"," ", (t or "").lower())).strip()
ACCESSORY_WORDS={"case","cover","charger","cable","adapter","protector","stand","mount","strap","skin","bumper","holder"}
def is_accessory(title: str) -> bool:
    toks=set(normalize_title(title).split()); return bool(toks & ACCESSORY_WORDS)
