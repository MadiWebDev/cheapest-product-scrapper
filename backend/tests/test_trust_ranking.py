import sys, pathlib, os, re
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from app.domain.models import RawOffer
from app.priceintel.trust import trust_v2, VERSION


def O(**kw):
    base = dict(connector="t", title="Phone", url="https://t.example/x", price=100.0,
                seller_rating=4.0, seller_feedback_count=10, seller_age_years=2.0)
    base.update(kw)
    return RawOffer(**base)


def test_trust_record_stores_inputs_and_version():
    rec = trust_v2(O(), median=100.0)
    assert rec["version"] == VERSION
    assert rec["inputs"]["price_vs_median"] == 1.0
    assert 0 <= rec["score"] <= 100 and "components" in rec and "reasons" in rec


def test_suspicious_categories_fire():
    cheap = trust_v2(O(price=30.0), median=100.0)
    assert any(w["id"] == "price_far_below_median" for w in cheap["warnings"])
    thin = trust_v2(O(rating=4.9, review_count=3), median=100.0)
    assert any(w["id"] == "thin_review_base" for w in thin["warnings"])
    bare = trust_v2(O(buyer_protection=False, returns_days=0), median=100.0)
    ids = {w["id"] for w in bare["warnings"]}
    assert {"no_buyer_protection", "no_returns"} <= ids


def test_ranking_modules_have_no_monetization_inputs():
    """Architectural test (directive §12): the ranking path must not read
    commission/campaign/sponsored data. Static scan of the ranking
    modules for monetization data-access identifiers."""
    root = pathlib.Path(__file__).parent.parent
    files = ["app/services/search.py", "app/domain/scoring.py",
             "app/domain/matching_v2.py", "app/priceintel/price_truth.py",
             "app/priceintel/trust.py"]
    forbidden = ["apply_affiliate", "AFFILIATE_TAG", "commission_rate", "campaign_id",
                 "sponsored_offers", "BillingProvider", "epc"]
    for f in files:
        src = (root / f).read_text()
        for token in forbidden:
            assert token not in src, f"{token} found in ranking module {f}"


def test_affiliate_env_does_not_change_ranking(monkeypatch):
    """Behavioral proof: configuring affiliate tags must not change any
    score or ordering — ranking has no path to that data."""
    os.environ["DEMO_MODE"] = "true"
    import importlib
    import app.connectors.registry as reg
    importlib.reload(reg)
    import app.services.search as ss
    ss.REGISTRY = reg.REGISTRY

    def snapshot():
        r = ss.search("iphone 15", {}, "PK", "PKR", connectors=["demo"])
        return [(p["title"], [(o["offer"]["url"], o["value_score"], o["trust_score"]) for o in p["offers"]])
                for p in r["products"]]

    before = snapshot()
    monkeypatch.setenv("AFFILIATE_TAG_DEMO", "should-not-matter-20")
    monkeypatch.setenv("AFFILIATE_TAG_DEFAULT", "should-not-matter-20")
    after = snapshot()
    assert before == after


def test_fairness_audit_passes():
    import subprocess
    root = pathlib.Path(__file__).parent.parent.parent
    r = subprocess.run([sys.executable, str(root / "tools" / "fairness_audit.py")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "fairness: OK" in r.stdout
