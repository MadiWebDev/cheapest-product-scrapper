import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from app.domain.models import RawOffer
from app.domain.matching_v2 import group_offers_v2, hard_block, match_confidence


def O(title, brand=None, attrs=None, condition="new", gtin=None):
    return RawOffer(connector="t", title=title, url="https://t.example/x", price=100.0,
                    brand=brand, attributes=attrs or {}, condition=condition, gtin=gtin)


def test_hard_separation_rules():
    base = O("Apple iPhone 15 128GB Black", "Apple", {"storage": "128GB", "color": "Black"})
    cases = [
        O("Apple iPhone 15 256GB Black", "Apple", {"storage": "256GB", "color": "Black"}),
        O("Apple iPhone 15 128GB Blue", "Apple", {"storage": "128GB", "color": "Blue"}),
        O("Apple iPhone 14 128GB Black", "Apple", {"storage": "128GB", "color": "Black"}),
        O("Apple iPhone 15 128GB Black", "Apple", {"storage": "128GB", "color": "Black"}, condition="used"),
        O("iPhone 15 Case Leather", "Apple", {"storage": "128GB", "color": "Black"}),
        O("Apple iPhone 15 128GB Black Bundle", "Apple", {"storage": "128GB", "color": "Black"}),
        O("Apple iPhone 15 128GB Black", "Apple", {"storage": "128GB", "color": "Black", "ram": "8GB"}),
    ]
    ram_base = O("Apple iPhone 15 128GB Black", "Apple", {"storage": "128GB", "color": "Black", "ram": "6GB"})
    for other in cases[:-1]:
        assert hard_block(base, other) is not None, other.title
    assert hard_block(ram_base, cases[-1]) is not None  # RAM axis


def test_bare_number_generation_conflict():
    a = O("Apple iPhone 15 128GB Black", "Apple")
    b = O("Apple iPhone 14 128GB Black", "Apple")
    assert hard_block(a, b) is not None
    c = O("Sony WH-1000XM5 Headphones", "Sony")
    d = O("Sony WH-1000XM4 Headphones", "Sony")
    assert hard_block(c, d) is not None


def test_confidence_reasons_and_exact_id():
    a = O("Samsung Galaxy S24 256GB Blue", "Samsung", gtin="123")
    b = O("Samsung Galaxy S24 256GB Blue", "Samsung", gtin="123")
    m = match_confidence(a, b)
    assert m["score"] == 100 and any("GTIN" in r for r in m["reasons"])
    c = O("Samsung Galaxy S24 (256GB) - Blue - Dual SIM", "Samsung")
    m2 = match_confidence(a, c)
    assert m2["score"] >= 60 and m2["reasons"]


def test_grouping_keeps_variants_separate_and_exposes_variant():
    offers = [O("Apple iPhone 15 128GB Black", "Apple"), O("Apple iPhone 15 128GB Black - PTA Approved", "Apple"),
              O("Apple iPhone 15 256GB Black", "Apple"), O("iPhone 15 Case", "Apple")]
    groups = group_offers_v2(offers)
    assert len(groups) == 3
    main = [g for g in groups if len(g["offers"]) == 2][0]
    assert main["variant"]["storage"] == "128gb"
    assert main["offer_matches"][1]["score"] >= 60


def test_eval_gates():
    import json, subprocess
    r = subprocess.run([sys.executable, str(pathlib.Path(__file__).parent.parent.parent / "tools" / "run_evals.py")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "false-merge" in r.stdout
    pairs = json.loads((pathlib.Path(__file__).parent.parent.parent / "eval" / "matching_pairs.json").read_text())
    assert len(pairs["pairs"]) >= 200
