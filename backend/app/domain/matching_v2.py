"""Matching v2 (directive §9): confidence 0–100 + reason list, with HARD
separation rules that no amount of title similarity may override:

storage, RAM, colour, generation, condition, accessory-vs-device,
bundle-vs-single, SIM variant, carrier lock.

v1 `group_offers` remains available; v2 wraps the same similarity
signals with explicit hard blocks and explainable confidence, and maps
groups onto the Product / ProductVariant / Offer shape.
"""
from __future__ import annotations

import re

from .matching import brand_model_key, exact_key, seq_ratio, token_set_ratio
from .models import RawOffer
from .normalize import is_accessory, normalize_title

COLORS = {"black", "white", "blue", "red", "green", "silver", "gold", "grey", "gray",
          "purple", "pink", "yellow", "titanium", "midnight", "starlight", "phantom"}


def _storage(o: RawOffer) -> str | None:
    v = o.attributes.get("storage") or o.attributes.get("capacity")
    if v:
        return str(v).lower().replace(" ", "")
    m = re.search(r"\b(\d+)\s*(gb|tb)\b", normalize_title(o.title))
    return f"{m.group(1)}{m.group(2)}" if m else None


def _ram(o: RawOffer) -> str | None:
    v = o.attributes.get("ram")
    if v:
        return str(v).lower().replace(" ", "")
    m = re.search(r"\b(\d+)\s*gb\s*ram\b", normalize_title(o.title))
    return f"{m.group(1)}gb" if m else None


def _color(o: RawOffer) -> str | None:
    v = o.attributes.get("color") or o.attributes.get("colour")
    if v:
        return str(v).lower().strip()
    toks = set(normalize_title(o.title).split())
    found = toks & COLORS
    return sorted(found)[0] if len(found) == 1 else None


def _model_tokens(title: str) -> dict[str, str]:
    """Model-number tokens by alphabetic skeleton: 's24' -> {'s': '24'},
    'iphone 15' -> {'': '15'}, '1000xm5' -> {'xm': '10005'} style split.
    Storage/RAM tokens (…gb/…tb) are excluded — they are separate axes."""
    out: dict[str, str] = {}
    for tok in normalize_title(title).split():
        if tok.endswith(("gb", "tb")) or not any(c.isdigit() for c in tok):
            continue
        m = re.fullmatch(r"([a-z]*)(\d+)([a-z]*)", tok)
        if m:
            out[m.group(1) + "|" + m.group(3)] = m.group(2)
    return out


def _generation_conflict(a: RawOffer, b: RawOffer) -> str | None:
    ta, tb = _model_tokens(a.title), _model_tokens(b.title)
    for skel in ta.keys() & tb.keys():
        if ta[skel] != tb[skel]:
            return f"generation/model number differs ({skel}{ta[skel]} vs {skel}{tb[skel]})"
    return None


def _generation(o: RawOffer) -> str | None:
    v = o.attributes.get("generation") or o.attributes.get("model")
    if v:
        return str(v).lower().replace(" ", "")
    bk = brand_model_key(o)
    return bk.split(":")[-1] if bk else None


def _sim(o: RawOffer) -> str | None:
    v = o.attributes.get("sim")
    if v:
        return str(v).lower().replace(" ", "")
    t = normalize_title(o.title)
    if "dual sim" in t or "dual-sim" in t:
        return "dual"
    if "single sim" in t:
        return "single"
    return None


def _carrier(o: RawOffer) -> str | None:
    v = o.attributes.get("carrier")
    if v:
        return str(v).lower().replace(" ", "")
    t = normalize_title(o.title)
    if "carrier locked" in t or "network locked" in t:
        return "locked"
    if "unlocked" in t:
        return "unlocked"
    return None


def _bundle(o: RawOffer) -> bool:
    return any(w in normalize_title(o.title) for w in ("bundle", "pack of", "combo"))


def hard_block(a: RawOffer, b: RawOffer) -> str | None:
    """Return the separation rule that forbids merging a and b, or None."""
    if a.condition != b.condition:
        return f"condition differs ({a.condition} vs {b.condition})"
    if is_accessory(a.title) != is_accessory(b.title):
        return "accessory vs main product"
    if _bundle(a) != _bundle(b):
        return "bundle vs single item"
    for name, fn in (("storage", _storage), ("RAM", _ram), ("colour", _color),
                     ("generation/model", _generation), ("SIM variant", _sim),
                     ("carrier lock", _carrier)):
        va, vb = fn(a), fn(b)
        if va and vb and va != vb:
            return f"{name} differs ({va} vs {vb})"
    return _generation_conflict(a, b)


def match_confidence(a: RawOffer, b: RawOffer) -> dict:
    """Explainable pairwise confidence: {score 0-100, reasons, hard_block}."""
    if a is b:
        return {"score": 100, "reasons": ["same offer"], "hard_block": None}
    ov = get_override(a.title, b.title)
    if ov == "match":
        return {"score": 100, "reasons": ["human review override: confirmed match"], "hard_block": None}
    if ov == "no_match":
        return {"score": 0, "reasons": ["human review override: confirmed non-match"],
                "hard_block": "human review override"}
    block = hard_block(a, b)
    ea, eb = exact_key(a), exact_key(b)
    if ea and eb and ea == eb:
        if block:
            return {"score": 0, "reasons": [f"shared identifier but hard rule: {block}"],
                    "hard_block": block}
        return {"score": 100, "reasons": ["shared GTIN/ASIN/MPN identifier"], "hard_block": None}
    if block:
        return {"score": 0, "reasons": [f"hard separation: {block}"], "hard_block": block}
    reasons: list[str] = []
    score = 0.0
    tsr = token_set_ratio(a.title, b.title)
    score += tsr * 55
    reasons.append(f"title token overlap {tsr:.2f}")
    sr = seq_ratio(a.title, b.title)
    score += sr * 20
    if a.brand and b.brand:
        if a.brand.lower() == b.brand.lower():
            score += 10
            reasons.append(f"same brand ({a.brand})")
        else:
            score -= 25
            reasons.append(f"different brands ({a.brand} vs {b.brand})")
    ba, bb = brand_model_key(a), brand_model_key(b)
    if ba and bb and ba == bb:
        score += 15
        reasons.append("same brand+model key")
    ta = set(normalize_title(a.title).split())
    tb = set(normalize_title(b.title).split())
    if ta and tb and (ta <= tb or tb <= ta):
        score += 8
        reasons.append("one title's tokens fully contain the other's")
    sa, sb = _storage(a), _storage(b)
    if sa and sb and sa == sb:
        score += 5
        reasons.append(f"same storage ({sa})")
    ca, cb = _color(a), _color(b)
    if ca and cb and ca == cb:
        score += 5
        reasons.append(f"same colour ({ca})")
    return {"score": int(max(0, min(100, round(score)))), "reasons": reasons, "hard_block": None}


# Operating point measured on eval/matching_pairs.json (244 pairs,
# 2026-11-17): threshold 60 -> false-merge 0.00%, false-split 1.67%.
# The directive's false-merge gate is <1%; 60 keeps margin on both sides.
MERGE_THRESHOLD = 60


# --- human review overrides (Phase 11 match-review queue) --------------------
# A reviewed decision beats the algorithm for that exact title pair.
_OVERRIDES: dict[frozenset, str] = {}


def _pair_key(title_a: str, title_b: str) -> frozenset:
    return frozenset((normalize_title(title_a), normalize_title(title_b)))


def set_override(title_a: str, title_b: str, decision: str) -> None:
    if decision not in ("match", "no_match"):
        raise ValueError("decision must be match | no_match")
    _OVERRIDES[_pair_key(title_a, title_b)] = decision


def get_override(title_a: str, title_b: str) -> str | None:
    return _OVERRIDES.get(_pair_key(title_a, title_b))


def group_offers_v2(offers: list[RawOffer]) -> list[dict]:
    """Group offers; every non-representative offer carries its match
    confidence + reasons vs the group representative. Groups expose the
    Product/ProductVariant/Offer mapping (variant = hard-rule signature)."""
    groups: list[dict] = []
    for o in offers:
        placed = False
        for g in groups:
            rep = g["offers"][0]
            m = match_confidence(o, rep)
            if m["hard_block"] is None and m["score"] >= MERGE_THRESHOLD:
                g["offers"].append(o)
                g["offer_matches"].append(m)
                placed = True
                break
        if not placed:
            groups.append({
                "id": exact_key(o) or brand_model_key(o) or normalize_title(o.title)[:60],
                "title": o.title, "brand": o.brand, "gtin": o.gtin, "asin": o.asin,
                "mpn": o.mpn, "accessory": is_accessory(o.title),
                "variant": {"storage": _storage(o), "ram": _ram(o), "color": _color(o),
                            "generation": _generation(o), "condition": o.condition,
                            "sim": _sim(o), "carrier": _carrier(o), "bundle": _bundle(o)},
                "offers": [o],
                "offer_matches": [{"score": 100, "reasons": ["group representative"],
                                   "hard_block": None}],
            })
    return groups
