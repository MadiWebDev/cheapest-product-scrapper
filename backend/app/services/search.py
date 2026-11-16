from __future__ import annotations
import concurrent.futures, datetime, os, time
from app.connectors.registry import REGISTRY
from app.domain.matching import group_offers
from app.domain.landed import landed_price, can_ship, certainty_for
from app.domain.scoring import quality_score, value_score, median_price, top_reasons
from app.domain.normalize import normalize_availability
from app.services.fx import get_fx
from app.priceintel.compliance import is_live_enabled
from app.priceintel.go import STORE as GO_STORE, offer_id_for
SORTS={"best_value","lowest_landed","lowest_item","best_quality","fastest","biggest_discount"}
def run_connector(name, query, filters, country):
    conn=REGISTRY[name]; t=time.time()
    try: offers=conn.search(query, filters, country); return name, offers, round((time.time()-t)*1000), conn.drift_check(offers), None
    except Exception as e: return name, [], round((time.time()-t)*1000), False, str(e)[:200]
def apply_filters(offers, f: dict):
    out=[]
    for o in offers:
        if f.get("condition") and o.condition not in f["condition"]: continue
        if f.get("min_price") is not None and (o.price is None or o.price<f["min_price"]): continue
        if f.get("max_price") is not None and (o.price is None or o.price>f["max_price"]): continue
        if f.get("min_rating") is not None and (o.rating is None or o.rating<f["min_rating"]): continue
        if f.get("min_reviews") and o.review_count<f["min_reviews"]: continue
        if f.get("min_seller_rating") is not None and (o.seller_rating is None or o.seller_rating<f["min_seller_rating"]): continue
        if f.get("in_stock_only") and normalize_availability(o.availability, o.stock_qty).value in ("out_of_stock",): continue
        if f.get("free_shipping_only") and (o.shipping_price or 0)>0: continue
        if f.get("max_delivery_days") and o.delivery_days and o.delivery_days>f["max_delivery_days"]: continue
        if f.get("official_only") and not o.official_store: continue
        if f.get("brand") and (o.brand or "").lower() not in [b.lower() for b in f["brand"]]: continue
        out.append(o)
    return out
def search(query: str, filters: dict|None=None, country: str="US", currency: str="USD", connectors: list[str]|None=None, weights: dict|None=None, category: str="default") -> dict:
    filters=filters or {}; names=connectors or [n for n in REGISTRY if n!="generic"]
    # Compliance gate (directive §6): in live mode (DEMO_MODE off) a source
    # without an approved, unexpired compliance record is disabled.
    demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
    if not demo_mode:
        gated, kept = [], []
        for n in names:
            if n == "generic" or is_live_enabled(n): kept.append(n)
            else: gated.append(n)
        names = kept
    else:
        gated = []
    fx, fx_stale=get_fx(); all_offers=[]; health=[]
    for n in gated: health.append({"connector": n, "offers": 0, "latency_ms": 0, "drift_suspected": False, "error": "disabled: no approved compliance record (live mode)", "compliance_blocked": True})
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for name, offers, ms, drift, err in ex.map(lambda n: run_connector(n, query, filters, country), names):
            all_offers.extend(offers); health.append({"connector":name,"offers":len(offers),"latency_ms":ms,"drift_suspected":drift,"error":err})
    all_offers=apply_filters(all_offers, filters)
    median=median_price(all_offers); groups=group_offers(all_offers); products=[]; unavailable=[]
    for g in groups:
        scored=[]
        for o in g["offers"]:
            if not can_ship(o, country): unavailable.append(o.to_dict()); continue
            landed=landed_price(o, country, currency, fx, category)
            q, expl=quality_score(o, median)
            oid=offer_id_for(o.connector, o.url); GO_STORE.register(oid, o, g["title"])
            scored.append({"offer":o.to_dict(),"landed":landed.to_dict() if landed else None,"quality_score":q,"quality_explanation":expl,"availability":normalize_availability(o.availability,o.stock_qty).value,"value_score":0.0,
                           "offer_id":oid,"go_url":f"/go/{oid}","trust_score":q,"trust_reasons":top_reasons(expl, o),
                           "certainty":certainty_for(o, landed),"checked_at":datetime.datetime.now(datetime.timezone.utc).isoformat()})
        if not scored: continue
        best=min([s["landed"]["total"] for s in scored if s["landed"]] or [0])
        for s in scored:
            s["value_score"]=value_score(s["quality_score"], s["landed"]["total"] if s["landed"] else None, best or None, s["offer"].get("delivery_days"), weights)
        scored.sort(key=lambda s: s["value_score"], reverse=True)
        if scored:
            scored[0]["badges"]=["Best value"]
            by_price=min(scored, key=lambda s: s["landed"]["total"] if s["landed"] else 1e18); by_price.setdefault("badges",[]).append("Best price")
            by_q=max(scored, key=lambda s: s["quality_score"]); by_q.setdefault("badges",[]).append("Best quality")
        products.append({"id":g["id"],"title":g["title"],"brand":g["brand"],"gtin":g["gtin"],"accessory":g["accessory"],"offers":scored})
    sort=(filters.get("sort") or "best_value")
    keyf={"lowest_landed":lambda p: min([o["landed"]["total"] for o in p["offers"] if o["landed"]] or [1e18]),"best_quality":lambda p: -max(o["quality_score"] for o in p["offers"]),"lowest_item":lambda p: min([o["offer"]["price"] or 1e18 for o in p["offers"]])}
    if sort in keyf: products.sort(key=keyf[sort])
    return {"query":query,"country":country,"currency":currency,"fx_stale":fx_stale,"demo":("demo" in REGISTRY),"products":products,"unavailable":unavailable,"connector_health":health,"total_offers":sum(len(p["offers"]) for p in products),
            "affiliate_disclosure":"Outbound /go links may earn the platform a commission when an affiliate tag is configured; commissions never affect ranking."}
def fake_discount(was: float|None, now: float|None, median_90d: float|None) -> dict:
    if not was or not now or not median_90d: return {"fake":False,"reason":"insufficient history"}
    claimed=(was-now)/was; real=(median_90d-now)/median_90d
    return {"fake": claimed-real>0.15, "claimed_discount_pct":round(claimed*100,1), "real_discount_vs_90d_median_pct":round(real*100,1)}
def good_time_to_buy(history_prices: list[float], current: float) -> dict:
    if len(history_prices)<5: return {"verdict":"unknown","reason":"not enough history"}
    lo, hi, avg=min(history_prices), max(history_prices), sum(history_prices)/len(history_prices)
    verdict="good" if current<=lo*1.05 else ("fair" if current<=avg else "wait")
    return {"verdict":verdict,"lowest":lo,"highest":hi,"average":round(avg,2),"current":current}
