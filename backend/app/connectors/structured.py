from __future__ import annotations
import json, re, html as htmlmod
from app.domain.models import RawOffer
from app.domain.normalize import clean_price, normalize_availability
def extract_jsonld(html_text: str) -> list[dict]:
    out=[]
    for m in re.finditer(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html_text, re.S|re.I):
        try:
            data=json.loads(htmlmod.unescape(m.group(1).strip()))
            out.extend(data if isinstance(data,list) else [data])
        except Exception: pass
    return out
def extract_next_data(html_text: str) -> dict|None:
    m=re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html_text, re.S)
    if m:
        try: return json.loads(m.group(1))
        except Exception: return None
    return None
def offers_from_jsonld(connector: str, html_text: str, page_url: str) -> list[RawOffer]:
    offers=[]
    def walk(node):
        if isinstance(node, dict):
            if str(node.get("@type","")).lower()=="product":
                off=node.get("offers") or {}
                if isinstance(off, list): off=off[0] if off else {}
                price=clean_price(off.get("price") or off.get("lowPrice"))
                agg=node.get("aggregateRating") or {}
                offers.append(RawOffer(connector=connector, title=node.get("name") or "Untitled", url=page_url,
                    price=price, currency=off.get("priceCurrency","USD"), image=(node.get("image") if isinstance(node.get("image"),str) else (node.get("image") or [None])[0] if node.get("image") else None),
                    gtin=node.get("gtin13") or node.get("gtin") or node.get("gtin12"), mpn=node.get("mpn"),
                    brand=(node.get("brand") or {}).get("name") if isinstance(node.get("brand"),dict) else node.get("brand"),
                    rating=float(agg["ratingValue"]) if agg.get("ratingValue") else None, review_count=int(agg.get("reviewCount",0)) if agg.get("reviewCount") else 0,
                    availability=normalize_availability(off.get("availability","")).value))
            for v in node.values(): walk(v)
        elif isinstance(node, list):
            for v in node: walk(v)
    for doc in extract_jsonld(html_text): walk(doc)
    return offers
def extract_opengraph(html_text: str) -> dict:
    og={}
    for m in re.finditer(r'<meta property="og:([^"]+)" content="([^"]*)"', html_text):
        og[m.group(1)]=htmlmod.unescape(m.group(2))
    pm=re.search(r'<meta property="product:price:amount" content="([^"]*)"', html_text)
    if pm: og["price"]=pm.group(1)
    return og
