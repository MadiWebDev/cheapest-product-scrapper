"""Sponsored offers (directive §17/§29A): a SEPARATE, labeled list.
Sponsored entries are never inserted into organic results or ranking —
the search response carries them under their own top-level key with a
'Sponsored' label, and a test asserts the separation.
"""
from __future__ import annotations

from app.domain.normalize import normalize_title

_SPONSORED: list[dict] = []


def register_sponsored(entry: dict) -> dict:
    rec = {"title": entry["title"], "url": entry["url"], "price": entry.get("price"),
           "currency": entry.get("currency", "USD"), "connector": entry.get("connector", "sponsored"),
           "label": "Sponsored", "campaign": entry.get("campaign", "")}
    _SPONSORED.append(rec)
    return rec


def sponsored_for(query: str) -> list[dict]:
    q = set(normalize_title(query).split())
    if not q:
        return []
    out = []
    for rec in _SPONSORED:
        toks = set(normalize_title(rec["title"]).split())
        if q & toks:
            out.append(dict(rec))
    return out


def all_sponsored() -> list[dict]:
    return [dict(r) for r in _SPONSORED]


def clear() -> None:
    _SPONSORED.clear()
