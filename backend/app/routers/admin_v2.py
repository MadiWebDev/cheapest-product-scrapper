"""Admin console v2 + developer API routes (Phase 11).

Admin routes require an admin key (X-Admin-Key) with a role:
viewer < moderator < admin. The bootstrap key comes from ADMIN_API_KEY.
Developer routes require a developer key (X-API-Key) with quota.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.priceintel.admin_v2 import AUDIT, AUTH, REVIEW, SELLERS
from app.priceintel.devapi import DEVKEYS

router = APIRouter(tags=["admin-v2"])


def _require(request: Request, role: str) -> dict:
    try:
        return AUTH.require(request.headers.get("x-admin-key"), role)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/api/admin/v2/users")
def create_user(request: Request, body: dict):
    actor = _require(request, "admin")
    key = AUTH.create_user(body.get("name", ""), body.get("role", "viewer"))
    AUDIT.add(actor["name"], "admin.create_user", body.get("name", ""), {"role": body.get("role")})
    return {"key": key, "note": "shown once; stored hashed"}


@router.get("/api/admin/v2/audit-log")
def audit_log(request: Request):
    _require(request, "viewer")
    return {"entries": AUDIT.list()}


@router.get("/api/admin/v2/match-review")
def match_review_list(request: Request):
    _require(request, "viewer")
    return {"pending": REVIEW.pending()}


@router.post("/api/admin/v2/match-review/scan")
def match_review_scan(request: Request, body: dict):
    _require(request, "moderator")
    from app.services.search import search as run_search
    r = run_search(body.get("query", ""), {}, body.get("country", "PK"),
                   body.get("currency", "PKR"), body.get("connectors"))
    added = []
    for p in r["products"]:
        rep = p["offers"][0] if p["offers"] else None
        for o in p["offers"][1:]:
            if o.get("match_confidence") is not None and o["match_confidence"] < 75:
                added.append(REVIEW.enqueue(rep["offer"]["title"], o["offer"]["title"],
                                            o["match_confidence"], o.get("match_reasons", [])))
    return {"enqueued": len(added), "items": added}


@router.post("/api/admin/v2/match-review/{rid}/decision")
def match_review_decide(request: Request, rid: str, body: dict):
    actor = _require(request, "moderator")
    try:
        rec = REVIEW.decide(rid, body.get("decision", ""), actor["name"])
    except KeyError:
        raise HTTPException(status_code=404, detail="unknown review item")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return rec


@router.get("/api/admin/v2/sellers/{seller}/scorecard")
def scorecard(request: Request, seller: str, tenant: str = "public"):
    _require(request, "viewer")
    card = SELLERS.scorecard(tenant, seller)
    if not card:
        raise HTTPException(status_code=404, detail="no observations for this seller/tenant")
    return card


@router.post("/api/admin/v2/sellers/{seller}/reply")
def seller_reply(request: Request, seller: str, body: dict):
    actor = _require(request, "moderator")
    return SELLERS.reply(seller, body.get("text", ""), actor["name"])


@router.get("/api/admin/v2/sellers/{seller}/undercuts")
def undercuts(request: Request, seller: str, tenant: str = "public"):
    _require(request, "viewer")
    return {"alerts": SELLERS.undercut_alerts(tenant, seller)}


@router.post("/api/admin/v2/devkeys")
def create_devkey(request: Request, body: dict):
    actor = _require(request, "admin")
    key = DEVKEYS.create(body.get("owner", ""), body.get("tenant", "public"),
                         int(body.get("monthly_quota", 1000)))
    AUDIT.add(actor["name"], "devkey.create", body.get("owner", ""), {})
    return {"key": key, "note": "shown once; stored hashed"}


# --- developer API (quota-enforced) ------------------------------------------

def _consume(request: Request) -> dict:
    key = request.headers.get("x-api-key")
    ok, why = DEVKEYS.consume(key or "")
    if not ok:
        raise HTTPException(status_code=401 if why == "invalid key" else 429, detail=why)
    return DEVKEYS.authenticate(key or "") or {}


@router.get("/api/v1/search")
def v1_search(request: Request, q: str, country: str = "PK", currency: str = "PKR"):
    _consume(request)
    from app.services.search import search as run_search
    return run_search(q, {}, country, currency)


@router.get("/api/v1/usage")
def v1_usage(request: Request):
    u = DEVKEYS.usage(request.headers.get("x-api-key") or "")
    if not u:
        raise HTTPException(status_code=401, detail="invalid key")
    return u
