from __future__ import annotations
import re
from difflib import SequenceMatcher
from .models import RawOffer
from .normalize import normalize_title, is_accessory
def token_set_ratio(a: str, b: str) -> float:
    ta, tb = set(normalize_title(a).split()), set(normalize_title(b).split())
    if not ta or not tb: return 0.0
    inter=len(ta&tb); return round(2*inter/(len(ta)+len(tb)),4) if (len(ta)+len(tb)) else 0.0
def seq_ratio(a,b): return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()
def exact_key(o: RawOffer) -> str|None:
    for v in (o.gtin, o.asin, o.mpn):
        if v: return f"id:{str(v).strip().lower()}"
    return None
def brand_model_key(o: RawOffer) -> str|None:
    brand=(o.brand or "").lower().strip()
    model=(o.model or "").lower().strip()
    if not model:
        m=re.search(r"\b([a-z]{1,4}[- ]?\d{2,}[a-z0-9-]*)\b", normalize_title(o.title))
        if m: model=m.group(1).replace(" ","")
    if brand and model: return f"bm:{brand}:{model}"
    return None
def _variant_sig(o: RawOffer) -> str:
    parts=[]
    for k in ("storage","capacity","size","color","colour","pack_count","count"):
        if k in o.attributes: parts.append(f"{k}={str(o.attributes[k]).lower()}")
    t=normalize_title(o.title)
    m=re.search(r"\b(\d+)\s*(gb|tb)\b", t)
    if m and not parts: parts.append(f"storage={m.group(1)}{m.group(2)}")
    return "|".join(sorted(parts))
def group_offers(offers: list[RawOffer]) -> list[dict]:
    """Group offers into canonical products. Accessories/bundles/variants never merge with the main product."""
    groups: list[dict]=[]
    for o in offers:
        placed=False
        acc=is_accessory(o.title); bundle=any(w in normalize_title(o.title) for w in ("bundle","pack of","combo"))
        for g in groups:
            rep=g["offers"][0]
            if exact_key(o) and exact_key(o)==exact_key(rep): g["offers"].append(o); placed=True; break
            if brand_model_key(o) and brand_model_key(o)==brand_model_key(rep) and _variant_sig(o)==_variant_sig(rep) and acc==is_accessory(rep.title) and bundle==any(w in normalize_title(rep.title) for w in ("bundle","pack of","combo")):
                g["offers"].append(o); placed=True; break
            sim=max(token_set_ratio(o.title, rep.title), seq_ratio(o.title, rep.title))
            if sim>=0.86 and _variant_sig(o)==_variant_sig(rep) and acc==is_accessory(rep.title):
                if (o.brand and rep.brand and o.brand.lower()!=rep.brand.lower()): continue
                g["offers"].append(o); placed=True; break
        if not placed:
            groups.append({"id": exact_key(o) or brand_model_key(o) or normalize_title(o.title)[:60], "title": o.title, "brand": o.brand, "gtin": o.gtin, "asin": o.asin, "mpn": o.mpn, "accessory": acc, "offers":[o]})
    return groups
