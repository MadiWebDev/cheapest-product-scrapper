"""MCP-style endpoint (directive §13): authenticated, rate-limited
JSON-RPC over HTTP exposing the platform's own tools (search, landed,
fair band, history) to external agents. Auth via MCP_API_KEY env —
when it is not configured the endpoint is disabled (503), never open.
"""
from __future__ import annotations

import os
import time

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(tags=["mcp"])


class RateLimiter:
    def __init__(self, limit: int = 60, window_s: int = 60):
        self.limit, self.window_s = limit, window_s
        self.hits: dict[str, list[float]] = {}

    def allow(self, key: str) -> bool:
        now = time.time()
        q = [t for t in self.hits.get(key, []) if now - t < self.window_s]
        if len(q) >= self.limit:
            self.hits[key] = q
            return False
        q.append(now)
        self.hits[key] = q
        return True


LIMITER = RateLimiter(limit=int(os.getenv("MCP_RATE_LIMIT", "60")))

TOOLS = [
    {"name": "search", "description": "Search offers across sources with landed cost and trust scores",
     "input": {"query": "string", "country": "string", "currency": "string"}},
    {"name": "landed", "description": "Compute the landed cost breakdown for a price",
     "input": {"price": "number", "currency": "string", "country": "string", "target_currency": "string"}},
    {"name": "fair_band", "description": "Fair-price band (median/IQR) for a list of prices",
     "input": {"prices": "number[]"}},
    {"name": "history", "description": "Price history for a product (DB deployments only)",
     "input": {"product": "string"}},
]


def _call_tool(name: str, args: dict):
    if name == "search":
        from app.services.search import search as run_search
        return run_search(args.get("query", ""), {}, args.get("country", "PK"),
                          args.get("currency", "PKR"))
    if name == "landed":
        from app.domain.landed import landed_price
        from app.domain.models import RawOffer
        from app.services.fx import get_fx
        fx, stale = get_fx()
        o = RawOffer(connector="mcp", title="mcp query", url="https://mcp.example/x",
                     price=args.get("price"), currency=args.get("currency", "USD"),
                     shipping_price=args.get("shipping_price"))
        b = landed_price(o, args.get("country", "PK"), args.get("target_currency", "PKR"),
                         fx, args.get("category", "default"))
        return {"landed": b.to_dict() if b else None, "fx_stale": stale}
    if name == "fair_band":
        from app.priceintel.price_truth import fair_price_band
        return fair_price_band([float(p) for p in args.get("prices", [])])
    if name == "history":
        return {"available": False,
                "reason": "Price history is served from the database in DB deployments; this runtime has no history rows for the query."}
    raise HTTPException(status_code=400, detail=f"unknown tool {name}")


@router.post("/mcp")
def mcp(request: Request, body: dict):
    key_env = os.getenv("MCP_API_KEY")
    if not key_env:
        raise HTTPException(status_code=503, detail="MCP disabled: MCP_API_KEY not configured")
    key = request.headers.get("x-api-key", "")
    if key != key_env:
        raise HTTPException(status_code=401, detail="invalid API key")
    if not LIMITER.allow(key):
        raise HTTPException(status_code=429, detail="rate limit exceeded")
    method = body.get("method")
    if method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        params = body.get("params", {})
        result = {"content": _call_tool(params.get("name", ""), params.get("arguments", {}))}
    else:
        raise HTTPException(status_code=400, detail=f"unknown method {method}")
    return {"jsonrpc": "2.0", "id": body.get("id"), "result": result}
