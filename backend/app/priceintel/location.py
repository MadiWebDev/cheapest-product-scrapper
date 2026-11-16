"""Location intelligence (directive §5) + local money formatting (§7).

Resolution priority — manual selection always wins and is never
silently overridden:
  1. explicit manual choice (this request)
  2. remembered preference (stored by the client from an earlier manual choice)
  3. IP-derived country (only when a trusted upstream supplies it)
  4. browser language region
  5. default: PK (Pakistan-first product)
"""
from __future__ import annotations

import json
import pathlib

DATA = pathlib.Path(__file__).parent.parent / "data" / "countries.json"
_doc = json.loads(DATA.read_text())
COUNTRIES: dict[str, dict] = _doc["countries"]
DEFAULT_COUNTRY = "PK"


def country_config(code: str | None) -> dict | None:
    if not code:
        return None
    return COUNTRIES.get(code.upper())


def _lang_region(accept_language: str | None) -> str | None:
    if not accept_language:
        return None
    first = accept_language.split(",")[0].strip()
    if "-" in first:
        region = first.rsplit("-", 1)[1].upper()
        if region in COUNTRIES:
            return region
    return None


def resolve_country(explicit: str | None = None, remembered: str | None = None,
                    ip_country: str | None = None, accept_language: str | None = None) -> dict:
    for value, source in ((explicit, "manual"), (remembered, "remembered"),
                          (ip_country, "ip"), (_lang_region(accept_language), "language")):
        if value and value.upper() in COUNTRIES:
            return {"country": value.upper(), "source": source,
                    "manual": source in ("manual", "remembered")}
    return {"country": DEFAULT_COUNTRY, "source": "default", "manual": False}


def location_block(country: str, category: str = "default") -> dict:
    cfg = country_config(country) or {}
    block = {
        "country": (country or "").upper(),
        "currency_default": cfg.get("currency"),
        "cod_available": bool(cfg.get("payment_norms", {}).get("cod_common")),
        "cities": cfg.get("cities") or [],
        "plug": cfg.get("plug"), "voltage": cfg.get("voltage"),
    }
    if cfg.get("phone_note") and category in ("default", "phones", "smartphones", "mobile"):
        block["phone_note"] = cfg["phone_note"]
    return block


# --- money formatting ---------------------------------------------------------

def _group_south_asian(n: int) -> str:
    """1,25,000 style grouping used in Pakistan/India."""
    s = str(abs(n))
    if len(s) <= 3:
        return ("-" if n < 0 else "") + s
    head, tail = s[:-3], s[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    return ("-" if n < 0 else "") + ",".join(parts) + "," + tail


def _trim(x: float) -> str:
    return f"{x:.2f}".rstrip("0").rstrip(".")


def format_money(amount: float, currency: str) -> str:
    cur = (currency or "").upper()
    cfg_style = None
    for c in COUNTRIES.values():
        if c.get("currency") == cur:
            cfg_style = c.get("number_style")
            break
    n = int(round(amount))
    if cfg_style == "lakh_crore" and abs(n) >= 100_000:
        if abs(n) >= 10_000_000:
            return f"{cur} {_trim(n / 10_000_000)} crore ({cur} {_group_south_asian(n)})"
        return f"{cur} {_trim(n / 100_000)} lakh ({cur} {_group_south_asian(n)})"
    if cfg_style == "lakh_crore":
        return f"{cur} {_group_south_asian(n)}"
    return f"{cur} {n:,}"
