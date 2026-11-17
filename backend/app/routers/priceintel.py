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


def _feature(name: str):
    from app.priceintel.features import feature_enabled
    if not feature_enabled(name):
        raise HTTPException(status_code=503, detail=f"feature {name} disabled")


@router.get("/api/features/used-phone-kit")
def used_phone_kit():
    _feature("used_phone_kit")
    from app.priceintel.features import USED_PHONE_KIT
    return USED_PHONE_KIT


@router.post("/api/features/compatibility")
def compatibility(body: dict):
    _feature("compatibility")
    from app.priceintel.features import check_compatibility
    return check_compatibility(body.get("device", {}), body.get("country", "PK"))


@router.post("/api/features/budget-plan")
def budget_plan(body: dict):
    _feature("budget_planner")
    from app.services.search import search as run_search
    country, currency = body.get("country", "PK"), body.get("currency", "PKR")
    plan, total, unmet = [], 0.0, []
    for item in body.get("items", []):
        r = run_search(item.get("query", ""), {}, country, currency)
        best = None
        for p in r["products"]:
            for o in p["offers"]:
                if o.get("landed") and not o.get("quarantined"):
                    if best is None or o["landed"]["total"] < best["landed"]["total"]:
                        best = o
        cap = float(item.get("max_price", 0))
        if best and best["landed"]["total"] <= cap:
            plan.append({"query": item["query"], "title": best["offer"]["title"],
                         "landed_total": best["landed"]["total"], "currency": currency,
                         "go_url": best["go_url"], "within_budget": True})
            total += best["landed"]["total"]
        else:
            unmet.append({"query": item["query"], "cap": cap,
                          "cheapest_found": best["landed"]["total"] if best else None})
    return {"plan": plan, "total": round(total, 2), "currency": currency, "unmet": unmet}


@router.post("/api/features/outcomes")
def outcome_add(body: dict):
    _feature("outcomes")
    from app.priceintel.features import OUTCOME_STORE
    try:
        return OUTCOME_STORE.add(body.get("seller", ""), body.get("outcome", ""),
                                 body.get("note", ""), body.get("user_ref", ""))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/features/outcomes/{seller}")
def outcome_summary(seller: str):
    _feature("outcomes")
    from app.priceintel.features import OUTCOME_STORE
    return OUTCOME_STORE.summary(seller)


@router.get("/api/features/evidence-pack")
def evidence_pack(query: str, country: str = "PK", currency: str = "PKR"):
    _feature("evidence_pack")
    import datetime
    from app.services.search import search as run_search
    r = run_search(query, {}, country, currency)
    offers = []
    for p in r["products"]:
        for o in p["offers"]:
            offers.append({"product": p["title"], "connector": o["offer"]["connector"],
                           "price": o["offer"]["price"], "landed_total": o["landed"]["total"] if o["landed"] else None,
                           "trust_score": o["trust_score"], "certainty": o["certainty"]["labels"],
                           "url": o["offer"]["url"], "go_url": o["go_url"]})
    return {"generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "query": query, "ship_to": country, "currency": currency,
            "purpose": "Price-match evidence: dated snapshot of comparable offers with landed totals and trust scores.",
            "offers": offers, "affiliate_disclosure": r.get("affiliate_disclosure")}


@router.get("/api/features/alternatives")
def alternatives(query: str, country: str = "PK", currency: str = "PKR"):
    _feature("alternatives")
    from app.services.search import search as run_search
    r = run_search(query, {}, country, currency)
    if not r["products"]:
        return {"alternatives": []}
    main = r["products"][0]
    main_best = main["offers"][0]["landed"]["total"] if main["offers"] and main["offers"][0].get("landed") else None
    out = []
    for p in r["products"][1:]:
        if not p["offers"] or not p["offers"][0].get("landed"):
            continue
        o = p["offers"][0]
        delta = None
        if main_best:
            delta = round((o["landed"]["total"] - main_best) / main_best * 100, 1)
        out.append({"title": p["title"], "landed_total": o["landed"]["total"],
                    "trust_score": o["trust_score"], "vs_main_pct": delta,
                    "why": ("cheaper than the main match" if (delta or 0) < 0 else "a different model in the same search — compare specs before switching")})
    return {"main": main["title"], "alternatives": out}


@router.get("/api/features/deal-passport")
def deal_passport(query: str, country: str = "PK", currency: str = "PKR"):
    _feature("deal_passport")
    from app.priceintel.features import PASSPORT
    from app.services.search import search as run_search
    r = run_search(query, {}, country, currency)
    if not r["products"]:
        return {"product": None, "timeline": []}
    p = r["products"][0]
    PASSPORT.record(p["title"], "search_check", {"country": country, "offers": len(p["offers"]),
                                                 "band_hidden": (p.get("fair_price_band") or {}).get("hidden")})
    best = p["offers"][0] if p["offers"] else {}
    return {"product": p["title"], "fair_price_band": p.get("fair_price_band"),
            "best_trust_score": best.get("trust_score"), "best_pci": (best.get("pci") or {}).get("index"),
            "warnings": (best.get("trust") or {}).get("warnings", []),
            "timeline": PASSPORT.for_product(p["title"])}


@router.post("/api/features/digest/run")
def digest_run(body: dict):
    _feature("smart_digest")
    from app.priceintel.alerts_v2 import SERVICE
    from app.services.alerts import notify
    from app.services.search import search as run_search
    user_ref = body.get("user_ref", "")
    items = SERVICE.watch_list(user_ref)
    lines = []
    for it in items:
        r = run_search(it["product_ref"], {}, body.get("country", "PK"), body.get("currency", "PKR"))
        if r["products"] and r["products"][0]["offers"]:
            o = r["products"][0]["offers"][0]
            if o.get("landed"):
                lines.append(f"{it['product_ref']}: best landed {o['landed']['currency']} {o['landed']['total']} via {o['offer']['connector']}")
    digest = {"user_ref": user_ref, "items": lines, "generated": True}
    dest = body.get("destination", "")
    delivery = notify(body.get("channel", "email"), dest, "\n".join(lines) or "No watched items.") if dest else {"sent": False, "reason": "no destination"}
    return {"digest": digest, "delivery": delivery}


@router.post("/api/alerts")
def create_alert(body: dict):
    from app.priceintel.alerts_v2 import SERVICE
    return SERVICE.create_alert(body.get("user_ref", ""), body.get("query", ""),
                                float(body.get("target_price", 0)), body.get("channel", "email"),
                                body.get("destination", ""), body.get("quiet_start"),
                                body.get("quiet_end"), body.get("tz", "Asia/Karachi"))


@router.get("/api/alerts/unsubscribe")
def alert_unsubscribe(token: str):
    from app.priceintel.alerts_v2 import SERVICE
    ok = SERVICE.unsubscribe(token)
    if not ok:
        raise HTTPException(status_code=404, detail="unknown unsubscribe token")
    return {"unsubscribed": True}


@router.post("/api/alerts/evaluate")
def alert_evaluate(body: dict):
    from app.priceintel.alerts_v2 import SERVICE
    return {"results": SERVICE.evaluate(body.get("query", ""), float(body.get("best_price", 0)))}


@router.post("/api/watchlist")
def watch_add(body: dict):
    from app.priceintel.alerts_v2 import SERVICE
    return SERVICE.watch_add(body.get("user_ref", ""), body.get("product_ref", ""), body.get("note", ""))


@router.get("/api/watchlist")
def watch_list(user_ref: str):
    from app.priceintel.alerts_v2 import SERVICE
    return {"items": SERVICE.watch_list(user_ref)}


@router.post("/api/telegram/webhook")
async def telegram_webhook(request: Request):
    """Telegram bot webhook (directive §15). Active only when
    TELEGRAM_WEBHOOK_SECRET is configured; verifies Telegram's secret
    header. Live delivery needs TELEGRAM_BOT_TOKEN (B3-005)."""
    import os as _os
    from app.priceintel.alerts_v2 import SERVICE
    from app.services.alerts import notify as _notify
    secret = _os.getenv("TELEGRAM_WEBHOOK_SECRET")
    if not secret:
        raise HTTPException(status_code=503, detail="telegram webhook disabled (TELEGRAM_WEBHOOK_SECRET not set)")
    if request.headers.get("x-telegram-bot-api-secret-token") != secret:
        raise HTTPException(status_code=401, detail="bad telegram secret")
    update = await request.json()
    msg = (update.get("message") or {})
    text = (msg.get("text") or "").strip()
    chat_id = str((msg.get("chat") or {}).get("id", ""))
    if not chat_id:
        return {"ok": True, "ignored": "no chat"}
    if text.startswith("/start"):
        reply = "PriceIntel alerts bot. Use the web app to create alerts; send /alerts to list yours, /stop to pause them."
    elif text.startswith("/alerts"):
        mine = [a for a in SERVICE.alerts.values() if a["destination"] == chat_id]
        reply = "\n".join(f"- {a['query']} <= {a['target_price']} ({'active' if a['active'] else 'paused'})" for a in mine) or "No alerts for this chat yet."
    elif text.startswith("/stop"):
        n = 0
        for a in SERVICE.alerts.values():
            if a["destination"] == chat_id and a["active"]:
                a["active"] = False
                n += 1
        reply = f"Paused {n} alert(s)."
    else:
        reply = "Commands: /start, /alerts, /stop"
    res = _notify("telegram", chat_id, reply)
    return {"ok": True, "delivery": res}


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
