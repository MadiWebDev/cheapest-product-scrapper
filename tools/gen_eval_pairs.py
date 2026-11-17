#!/usr/bin/env python3
"""Generate the labeled matching-pairs + PK relevance eval datasets.

Deterministic and template-based: pairs are constructed from product
variants along known axes, so labels are correct by construction.
These are SYNTHETIC eval fixtures (labelled as such in the files) —
they measure the matcher, they are not marketplace data.
Outputs: eval/matching_pairs.json, eval/relevance_pk.json,
eval/catalog_fixture.json.
"""
import itertools
import json
import pathlib

OUT = pathlib.Path(__file__).parent.parent / "eval"
OUT.mkdir(exist_ok=True)

# (brand, model, base title) — PK-relevant catalogue
MODELS = [
    ("Apple", "iPhone 15", "Apple iPhone 15"),
    ("Apple", "iPhone 14", "Apple iPhone 14"),
    ("Samsung", "Galaxy S24", "Samsung Galaxy S24"),
    ("Samsung", "Galaxy S23", "Samsung Galaxy S23"),
    ("Samsung", "Galaxy A54", "Samsung Galaxy A54"),
    ("Google", "Pixel 8", "Google Pixel 8"),
    ("Xiaomi", "Redmi Note 13", "Xiaomi Redmi Note 13"),
    ("Infinix", "Hot 40", "Infinix Hot 40"),
    ("Tecno", "Spark 20", "Tecno Spark 20"),
    ("OnePlus", "12R", "OnePlus 12R"),
]

PHRASINGS = [
    "{base} {storage} {color}",
    "{brand} {model} ({storage}) - {color} - Dual SIM - PTA Approved",
    "{model} {storage}GB {color} Unlocked",  # storage number only; fixed below
]


def phrasings(base, brand, model, storage, color):
    num = storage.replace("GB", "")
    return [
        f"{base} {storage} {color}",
        f"{brand} {model} ({storage}) - {color} - Dual SIM - PTA Approved",
        f"{model} {num}GB {color} Unlocked Smartphone",
        f"{base} - {storage} - {color} - Official Warranty",
    ]


def offer(title, brand, storage=None, color=None, condition="new", extra_attrs=None):
    attrs = {}
    if storage:
        attrs["storage"] = storage
    if color:
        attrs["color"] = color
    if extra_attrs:
        attrs.update(extra_attrs)
    return {"title": title, "brand": brand, "attributes": attrs, "condition": condition}


pairs = []

# --- positives: same variant, different seller phrasings ---
for brand, model, base in MODELS:
    for storage, color in (("128GB", "Black"), ("256GB", "Blue")):
        titles = phrasings(base, brand, model, storage, color)
        for t1, t2 in itertools.combinations(titles, 2):
            pairs.append({"a": offer(t1, brand, storage, color),
                          "b": offer(t2, brand, storage, color),
                          "label": "match", "kind": "positive:phrasing"})

# --- hard negatives: one axis differs ---
for brand, model, base in MODELS:
    a = offer(f"{base} 128GB Black", brand, "128GB", "Black")
    negs = [
        ("storage", offer(f"{base} 256GB Black", brand, "256GB", "Black")),
        ("colour", offer(f"{base} 128GB Blue", brand, "128GB", "Blue")),
        ("accessory", offer(f"{base} Case - Leather Cover", brand, "128GB", "Black")),
        ("condition", offer(f"{base} 128GB Black - Used", brand, "128GB", "Black", condition="used")),
        ("bundle", offer(f"{base} 128GB Black Bundle with Charger and Case", brand, "128GB", "Black")),
        ("sim", offer(f"{base} 128GB Black Single SIM", brand, "128GB", "Black", extra_attrs={"sim": "single"})),
        ("carrier", offer(f"{base} 128GB Black Carrier Locked", brand, "128GB", "Black", extra_attrs={"carrier": "locked"})),
        ("ram", offer(f"{base} 128GB Black 12GB RAM", brand, "128GB", "Black", extra_attrs={"ram": "12GB"})),
    ]
    a_ram = offer(f"{base} 128GB Black 8GB RAM", brand, "128GB", "Black", extra_attrs={"ram": "8GB"})
    a_sim = offer(f"{base} 128GB Black Dual SIM", brand, "128GB", "Black", extra_attrs={"sim": "dual"})
    a_car = offer(f"{base} 128GB Black Unlocked", brand, "128GB", "Black", extra_attrs={"carrier": "unlocked"})
    for kind, b in negs:
        left = a_sim if kind == "sim" else a_car if kind == "carrier" else a_ram if kind == "ram" else a
        pairs.append({"a": left, "b": b, "label": "no_match", "kind": f"hard_negative:{kind}"})

# --- hard negatives: generation differs (sibling models) ---
for (b1, m1, base1), (b2, m2, base2) in zip(MODELS, MODELS[1:] + MODELS[:1]):
    if b1 == b2:
        pairs.append({"a": offer(f"{base1} 128GB Black", b1, "128GB", "Black"),
                      "b": offer(f"{base2} 128GB Black", b2, "128GB", "Black"),
                      "label": "no_match", "kind": "hard_negative:generation"})

# --- easy negatives: different brands ---
for (b1, m1, base1), (b2, m2, base2) in itertools.combinations(MODELS, 2):
    if b1 != b2:
        pairs.append({"a": offer(f"{base1} 128GB Black", b1, "128GB", "Black"),
                      "b": offer(f"{base2} 128GB Black", b2, "128GB", "Black"),
                      "label": "no_match", "kind": "negative:brand"})

pairs = pairs[:260]
(OUT / "matching_pairs.json").write_text(json.dumps(
    {"synthetic": True, "generated_by": "tools/gen_eval_pairs.py", "pairs": pairs}, indent=1))
n_match = sum(1 for p in pairs if p["label"] == "match")
print(f"matching_pairs: {len(pairs)} pairs ({n_match} match / {len(pairs) - n_match} no_match)")

# --- relevance golden set (PK) over a fixed catalog fixture ---
catalog = []
for i, (brand, model, base) in enumerate(MODELS):
    catalog.append({"id": f"p{i}", "title": f"{base} 128GB Black", "brand": brand})
    catalog.append({"id": f"p{i}c", "title": f"{base} Case - Shockproof Cover", "brand": brand})
catalog += [
    {"id": "h1", "title": "Sony WH-1000XM5 Wireless Headphones", "brand": "Sony"},
    {"id": "h2", "title": "Sony WH-1000XM4 Wireless Headphones", "brand": "Sony"},
    {"id": "w1", "title": "Apple Watch Series 9 GPS 45mm", "brand": "Apple"},
    {"id": "l1", "title": "Apple MacBook Air M3 13-inch 256GB", "brand": "Apple"},
    {"id": "l2", "title": "Apple MacBook Air M2 13-inch 256GB", "brand": "Apple"},
    {"id": "c1", "title": "Anker 737 Power Bank 24000mAh", "brand": "Anker"},
]
(OUT / "catalog_fixture.json").write_text(json.dumps(
    {"synthetic": True, "items": catalog}, indent=1))

queries = []
for i, (brand, model, base) in enumerate(MODELS):
    queries.append({"query": f"{model.lower()}", "relevant_ids": [f"p{i}"]})
    queries.append({"query": f"{model.lower()} case", "relevant_ids": [f"p{i}c"]})
    queries.append({"query": f"{model.lower()} price in pakistan", "relevant_ids": [f"p{i}"]})
    queries.append({"query": f"{brand.lower()} {model.lower()} pta approved", "relevant_ids": [f"p{i}"]})
queries += [
    {"query": "sony xm5 headphones", "relevant_ids": ["h1"]},
    {"query": "sony wh-1000xm4", "relevant_ids": ["h2"]},
    {"query": "apple watch series 9", "relevant_ids": ["w1"]},
    {"query": "macbook air m3", "relevant_ids": ["l1"]},
    {"query": "macbook air m2", "relevant_ids": ["l2"]},
    {"query": "anker power bank", "relevant_ids": ["c1"]},
    {"query": "iphone 15 ki qeemat", "relevant_ids": ["p0"]},
    {"query": "samsung s24 sasta", "relevant_ids": ["p2"]},
    {"query": "infinix hot 40 rate", "relevant_ids": ["p7"]},
    {"query": "redmi note 13 cover", "relevant_ids": ["p6c"]},
]
(OUT / "relevance_pk.json").write_text(json.dumps(
    {"synthetic": True, "generated_by": "tools/gen_eval_pairs.py", "queries": queries}, indent=1))
print(f"relevance_pk: {len(queries)} queries over {len(catalog)} catalog items")
