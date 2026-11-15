from __future__ import annotations
import csv, io, json
from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
from app.services.search import search as run_search, fake_discount, good_time_to_buy
from app.connectors.registry import REGISTRY
from app.connectors.generic import GenericConnector
router=APIRouter(prefix="/api", tags=["finder"])
class SearchBody(BaseModel):
    query: str; country: str="US"; currency: str="USD"; filters: dict={}; connectors: list[str]|None=None; weights: dict|None=None; category: str="default"
@router.post("/search")
def search_post(body: SearchBody): return run_search(body.query, body.filters, body.country, body.currency, body.connectors, body.weights, body.category)
@router.get("/search")
def search_get(q: str, country: str="US", currency: str="USD", sort: str="best_value"): return run_search(q, {"sort":sort}, country, currency)
@router.get("/search/stream")
def search_stream(q: str, country: str="US", currency: str="USD"):
    def gen():
        import concurrent.futures
        from app.services.search import run_connector
        names=[n for n in REGISTRY if n!="generic"]
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            futs={ex.submit(run_connector, n, q, {}, country): n for n in names}
            for f in concurrent.futures.as_completed(futs):
                name, offers, ms, drift, err=f.result()
                yield f"event: offer_batch\ndata: {json.dumps({'connector':name,'offers':[o.to_dict() for o in offers],'latency_ms':ms,'drift_suspected':drift,'error':err})}\n\n"
        yield f"event: done\ndata: {json.dumps({'query':q})}\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")
@router.get("/autocomplete")
def autocomplete(q: str):
    base=["iphone 15","iphone 15 case","samsung galaxy s24","sony wh-1000xm5 headphones","macbook air m3","dyson v15","nike air force 1","ps5 controller","air fryer","mechanical keyboard"]
    return {"suggestions":[b for b in base if q.lower() in b][:8]}
@router.get("/extract")
def extract(url: str):
    offers=GenericConnector().get_product(url); return {"offers":[o.to_dict() for o in offers]}
@router.get("/connectors")
def connectors(): return {"connectors":[{"name":n,"countries":c.supported_countries,"currencies":c.supported_currencies,"compliance":c.compliance_note} for n,c in REGISTRY.items()]}
@router.get("/export")
def export(fmt: str="csv", q: str="iphone", country: str="US", currency: str="USD"):
    res=run_search(q, {}, country, currency); rows=[]
    for p in res["products"]:
        for o in p["offers"]: rows.append({"product":p["title"],"connector":o["offer"]["connector"],"price":o["offer"]["price"],"landed_total":o["landed"]["total"] if o["landed"] else None,"quality":o["quality_score"],"url":o["offer"]["url"]})
    if fmt=="json": return rows
    buf=io.StringIO(); w=csv.DictWriter(buf, fieldnames=["product","connector","price","landed_total","quality","url"]); w.writeheader(); w.writerows(rows)
    return Response(buf.getvalue(), media_type="text/csv")
@router.post("/match-feedback")
def match_feedback(body: dict): return {"stored":True,"feedback":body}
@router.get("/insights/fake-discount")
def fd(was: float, now: float, median90: float): return fake_discount(was, now, median90)
@router.get("/trending/{country}")
def trending(country: str): return {"country":country,"note":"Computed from price_history in DB deployments; demo/offline returns empty list honestly","deals":[]}
