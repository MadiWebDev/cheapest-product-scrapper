from __future__ import annotations
import json, os, time, urllib.request
from app.domain.landed import FALLBACK_FX
_cache={"rates":None,"ts":0,"stale":True}
def get_fx() -> tuple[dict, bool]:
    """Daily-cached FX: frankfurter (primary) -> open.er-api (fallback) -> last cache/fallback table flagged stale. Never invents rates."""
    now=time.time()
    if _cache["rates"] and now-_cache["ts"]<86400: return _cache["rates"], _cache["stale"]
    for url in [os.getenv("FX_PRIMARY_URL","https://api.frankfurter.app/latest?from=USD"), os.getenv("FX_FALLBACK_URL","https://open.er-api.com/v6/latest/USD")]:
        try:
            with urllib.request.urlopen(url, timeout=8) as r: data=json.loads(r.read())
            rates=data.get("rates") or data.get("conversion_rates")
            if rates: rates.setdefault("USD",1.0); _cache.update(rates=rates, ts=now, stale=False); return rates, False
        except Exception: continue
    if _cache["rates"]: return _cache["rates"], True
    return FALLBACK_FX, True
