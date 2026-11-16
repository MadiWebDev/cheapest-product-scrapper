import sys, pathlib, os
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from app.priceintel.go import (ALLOWED_DOMAINS, OfferStore, apply_affiliate,
                               destination_allowed, offer_id_for)


def test_allowlist_accepts_real_subdomains():
    assert destination_allowed("amazon", "https://www.amazon.com/dp/B0X")
    assert destination_allowed("amazon", "https://smile.amazon.co.uk/dp/B0X")
    assert destination_allowed("daraz", "https://www.daraz.pk/products/i123.html")


def test_allowlist_rejects_lookalikes():
    assert not destination_allowed("amazon", "https://evil-amazon.com/dp/B0X")
    assert not destination_allowed("amazon", "https://amazon.com.evil.com/dp/B0X")
    assert not destination_allowed("amazon", "https://www.amazon.com@evil.com/x")
    assert not destination_allowed("daraz", "https://daraz.pk.evil.io/x")
    assert not destination_allowed("unknown_connector", "https://example.com/x")
    assert not destination_allowed("amazon", "ftp://www.amazon.com/x")


def test_offer_id_is_stable():
    assert offer_id_for("demo", "https://demo.example/1") == offer_id_for("demo", "https://demo.example/1")
    assert offer_id_for("demo", "https://demo.example/1") != offer_id_for("demo", "https://demo.example/2")


def test_affiliate_tag_only_when_configured(monkeypatch):
    monkeypatch.delenv("AFFILIATE_TAG_AMAZON", raising=False)
    monkeypatch.delenv("AFFILIATE_TAG_DEFAULT", raising=False)
    url, applied = apply_affiliate("https://www.amazon.com/dp/B0X", "amazon")
    assert applied is False and url == "https://www.amazon.com/dp/B0X"
    monkeypatch.setenv("AFFILIATE_TAG_AMAZON", "priceintel-20")
    url, applied = apply_affiliate("https://www.amazon.com/dp/B0X", "amazon")
    assert applied is True and "tag=priceintel-20" in url


def test_store_register_and_click_summary():
    s = OfferStore()

    class O:
        connector = "demo"; url = "https://demo.example/9"; title = "T"
        price = 10.0; currency = "USD"; demo = True

    oid = offer_id_for("demo", O.url)
    s.register(oid, O(), "T")
    assert s.get(oid)["connector"] == "demo"
    s.record_click(oid, s.get(oid), False)
    assert s.click_summary() == {"total_clicks": 1, "by_connector": {"demo": 1}}
    assert "demo" in ALLOWED_DOMAINS
