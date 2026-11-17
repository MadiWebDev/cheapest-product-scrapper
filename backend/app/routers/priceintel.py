"""PriceIntel v3 routes: /go tracked redirect + compliance gate API."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.priceintel.compliance import gate_report, get_record
from app.priceintel.go import STORE, apply_affiliate, destination_allowed
from app.priceintel.location import COUNTRIES, country_config, format_money, resolve_country

router = APIRouter(tags=["priceintel"])


@router.get("/go/{offer_id}")
def go(offer_id: str, request: Request):
    entry = STORE.get(offer_id)
    if not entry:
        raise HTTPException(status_code=404, detail="unknown offer_id (offers are registered by search)")
    if not destination_allowed(entry["connector"], entry["url"]):
        raise HTTPException(status_code=400, detail="destination failed allowlist re-validation at click time")
    final, affiliate_applied = apply_affiliate(entry["url"], entry["connector"])
    STORE.record_click(offer_id, entry, affiliate_applied, request.headers.get("user-agent"))
    return RedirectResponse(final, status_code=302)


@router.get("/api/compliance")
def compliance_list():
    return {"sources": gate_report(),
            "rule": "A source runs in live mode only with an approved, unexpired COMPLIANCE_REVIEW record (directive §6)."}


@router.get("/api/compliance/{source_id}")
def compliance_one(source_id: str):
    rec = get_record(source_id)
    if not rec:
        raise HTTPException(status_code=404, detail="no compliance record for this source")
    return rec


@router.get("/api/clicks/summary")
def clicks_summary():
    return STORE.click_summary()


@router.get("/api/countries")
def countries():
    return {"version": "2026-11-17",
            "countries": {code: {"name": c["name"], "currency": c["currency"],
                                 "cod_available": bool(c.get("payment_norms", {}).get("cod_common"))}
                          for code, c in sorted(COUNTRIES.items())}}


@router.get("/api/countries/{code}")
def country_one(code: str):
    cfg = country_config(code)
    if not cfg:
        raise HTTPException(status_code=404, detail="unknown country code")
    return {"code": code.upper(), **cfg}


@router.get("/api/location/resolve")
def location_resolve(request: Request, country: str | None = None, remembered: str | None = None):
    return resolve_country(explicit=country, remembered=remembered,
                           accept_language=request.headers.get("accept-language"))


@router.get("/api/format/money")
def money(amount: float, currency: str = "PKR"):
    return {"amount": amount, "currency": currency.upper(), "formatted": format_money(amount, currency)}


@router.get("/api/adapters")
def adapters():
    from app.priceintel.health import HEALTH
    from app.priceintel.manifests import MANIFESTS
    from app.priceintel.compliance import is_live_enabled
    return {"adapters": [{"id": m["id"], "access_method": m["access_method"],
                          "compliance_status": m["compliance_status"],
                          "live_enabled": is_live_enabled(m["id"]),
                          "health": HEALTH.for_connector(m["id"])}
                         for m in MANIFESTS.values()]}


@router.get("/api/billing/plans")
def billing_plans():
    from app.priceintel.billing import PLANS
    return {"provider": "paddle", "plans": PLANS,
            "note": "Prices are this product's own list prices; checkout activates when Paddle keys are configured."}


@router.post("/api/billing/checkout")
def billing_checkout(body: dict):
    from app.priceintel.billing import PROVIDER
    return PROVIDER.create_checkout(body.get("plan", ""), body.get("user_ref", ""))


@router.post("/api/billing/webhook/paddle")
async def paddle_webhook(request: Request):
    from app.priceintel.billing import PROVIDER
    raw = await request.body()
    sig = request.headers.get("paddle-signature", "")
    if not PROVIDER.verify_webhook(raw, sig):
        raise HTTPException(status_code=401, detail="invalid webhook signature")
    import json as _json
    return PROVIDER.handle_event(_json.loads(raw))


@router.get("/api/sponsored")
def sponsored_list():
    from app.priceintel.sponsored import all_sponsored
    return {"sponsored": all_sponsored()}


@router.post("/api/assistant")
def assistant(body: dict):
    from app.priceintel.ai import answer
    return answer(body.get("query", ""), body.get("country", "PK"), body.get("currency", "PKR"))


@router.post("/api/scam-check")
def scam_check(body: dict):
    from app.priceintel.scam import analyze_ad
    return analyze_ad(body.get("text", ""), body.get("market_median"))


@router.get("/api/adapters/{adapter_id}")
def adapter_one(adapter_id: str):
    from app.priceintel.health import HEALTH
    from app.priceintel.manifests import manifest_for
    m = manifest_for(adapter_id)
    if not m:
        raise HTTPException(status_code=404, detail="unknown adapter")
    return {**m, "health": HEALTH.for_connector(adapter_id)}
