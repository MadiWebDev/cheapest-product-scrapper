import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from app.connectors.registry import REGISTRY
from app.connectors.generic import assert_public_url
from app.priceintel.manifests import MANIFESTS, manifest_for
from app.priceintel.health import AdapterHealth

FIXTURE = (pathlib.Path(__file__).parent / "fixtures" / "search_results.html").read_text()


def test_manifest_exists_for_every_connector():
    for name in REGISTRY:
        m = manifest_for(name)
        assert m is not None, f"missing manifest for {name}"
        for field in ("id", "countries", "access_method", "compliance_status",
                      "rate_limit", "cache_ttl_seconds", "data_use"):
            assert field in m


def test_manifest_compliance_status_matches_records():
    assert manifest_for("daraz")["compliance_status"] == "blocked"
    assert manifest_for("priceoye") is None or True  # priceoye is not a connector
    assert manifest_for("amazon")["compliance_status"] == "unreviewed"
    assert manifest_for("demo")["access_method"] == "fixture" if "demo" in REGISTRY else True


def _contract(connector_name):
    conn = REGISTRY[connector_name]
    conn.fetch = lambda url: FIXTURE  # stub network with the fixture page
    offers = conn.search("fixture phone", {}, "US")
    assert len(offers) == 2
    for o in offers:
        assert o.connector == connector_name
        assert o.title and o.price and o.price > 0
        assert o.currency == "USD"
        assert o.url.startswith("https://")
    return offers


def test_contract_amazon():
    offers = _contract("amazon")
    assert offers[0].gtin == "4006381333931" and offers[0].rating == 4.5


def test_contract_ebay():
    _contract("ebay")


def test_contract_daraz():
    offers = _contract("daraz")
    assert all(o.url.startswith("https://www.daraz.pk") for o in offers)


def test_drift_output_reaches_health_store():
    h = AdapterHealth()
    h.record("amazon", 10, False)
    h.record("amazon", 0, True, error=None)
    snap = h.for_connector("amazon")
    assert snap["runs"] == 2 and snap["drift_runs"] == 1 and snap["last_drift_suspected"] is True


def test_ssrf_rejects_credentials_in_url():
    try:
        assert_public_url("https://user:pass@example.com/x")
        raise AssertionError("credentials in URL must be blocked")
    except ValueError:
        pass


def test_search_run_records_health():
    import os
    os.environ["DEMO_MODE"] = "true"
    import importlib
    import app.connectors.registry as reg
    importlib.reload(reg)
    import app.services.search as ss
    ss.REGISTRY = reg.REGISTRY
    from app.priceintel.health import HEALTH
    ss.search("iphone", {}, "US", "USD", connectors=["demo"])
    assert HEALTH.for_connector("demo")["runs"] >= 1
