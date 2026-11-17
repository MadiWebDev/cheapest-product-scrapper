import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from app.domain.models import RawOffer
from app.domain.landed import landed_price, VAT, DUTY
from app.priceintel.price_truth import (fair_price_band, band_position, is_glitch,
                                        price_confidence_index)

GOLDEN = json.loads((pathlib.Path(__file__).parent.parent.parent / "eval" / "landed_golden.json").read_text())


def _expected(case):
    """Independent recomputation from the rule tables (not via landed_price)."""
    o, fx = case["offer"], case["fx"]
    item = o["price"] / fx[o["currency"]]
    ship = (o["shipping_price"] or 0.0) / fx[o["currency"]]
    de_min = DUTY["de_minimis_usd"].get(case["country"], 0)
    duty_rate = DUTY["duty_by_category"].get(case["category"], DUTY["duty_by_category"]["default"])
    duty = 0.0 if item <= de_min else (item + ship) * duty_rate
    tax_rate = VAT["rates"].get(case["country"], 0.0)
    tax = (item + ship + duty) * tax_rate
    handling = DUTY["handling_usd"] if item > de_min else 0.0
    subtotal = item + ship + duty + tax + handling
    total = subtotal * fx[case["currency"]]
    return total * 1.015, duty, tax_rate, handling


def test_landed_golden_cases():
    assert len(GOLDEN["cases"]) >= 10
    for case in GOLDEN["cases"]:
        o = RawOffer(connector="golden", title=case["name"], url="https://g.example/x",
                     price=case["offer"]["price"], currency=case["offer"]["currency"],
                     shipping_price=case["offer"]["shipping_price"])
        got = landed_price(o, case["country"], case["currency"], case["fx"], case["category"])
        exp = case["expect"]
        if "result" in exp and exp["result"] is None:
            assert got is None, case["name"]
            continue
        total, duty, tax_rate, handling = _expected(case)
        assert got is not None and abs(got.total - total) / total < 0.005, case["name"]
        assert (got.duty > 0) == exp["duty_applies"], case["name"]
        assert (got.handling > 0) == exp["handling_applies"], case["name"]
        if exp.get("tax_rate") is not None:
            assert abs(tax_rate - exp["tax_rate"]) < 1e-9, case["name"]


def test_fair_band_hidden_when_sample_small():
    b = fair_price_band([10.0, 11.0, 12.0])
    assert b["hidden"] is True and b["sample_size"] == 3
    b2 = fair_price_band([10, 11, 12, 13, 14, 15])
    assert b2["hidden"] is False and b2["median"] == 12.5 and b2["sample_size"] == 6
    assert band_position(5, b2) == "below_band"
    assert band_position(12, b2) == "in_band"
    assert band_position(99, b2) == "above_band"
    assert band_position(12, b) is None


def test_glitch_quarantine_threshold():
    assert is_glitch(39.0, 100.0) is True   # 61% below median
    assert is_glitch(40.0, 100.0) is False  # exactly 60% below -> not quarantined
    assert is_glitch(90.0, 100.0) is False
    assert is_glitch(10.0, 0.0) is False


def test_pci_components_and_bounds():
    good = price_confidence_index(band_sample=9, shipping_certainty="CONFIRMED",
                                  fx_stale=False, rating=4.5, review_count=200, quarantined=False)
    assert good["index"] == 95 and good["components"]["band_sample"] == 15
    bad = price_confidence_index(band_sample=1, shipping_certainty="UNKNOWN",
                                 fx_stale=True, rating=None, review_count=0, quarantined=True)
    assert bad["index"] == 25 and bad["components"]["glitch_quarantine"] == -15
    assert 0 <= bad["index"] <= 100


def test_fx_failover_chain(monkeypatch):
    import io
    import app.services.fx as fxmod

    class Resp:
        def __init__(self, payload): self.payload = payload
        def read(self): return json.dumps(self.payload).encode()
        def __enter__(self): return self
        def __exit__(self, *a): return False

    calls = []
    def fake_urlopen(url, timeout=8):
        calls.append(url)
        if "frankfurter" in url:
            raise OSError("primary down")
        return Resp({"rates": {"EUR": 0.9, "PKR": 280.0}})

    monkeypatch.setattr(fxmod.urllib.request, "urlopen", fake_urlopen)
    fxmod._cache.update(rates=None, ts=0, stale=True)
    rates, stale = fxmod.get_fx()
    assert stale is False and rates["PKR"] == 280.0 and len(calls) == 2

    def all_down(url, timeout=8):
        raise OSError("all down")
    monkeypatch.setattr(fxmod.urllib.request, "urlopen", all_down)
    fxmod._cache.update(rates=None, ts=0, stale=True)
    rates2, stale2 = fxmod.get_fx()
    assert stale2 is True and rates2["PKR"] == 278.0  # static fallback, flagged stale, never invented
