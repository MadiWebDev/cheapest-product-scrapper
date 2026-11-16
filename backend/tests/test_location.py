import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from app.priceintel.location import (country_config, format_money, location_block,
                                     resolve_country, _group_south_asian)
from app.priceintel import compliance


def test_manual_choice_always_wins():
    r = resolve_country(explicit="AE", remembered="US", ip_country="GB", accept_language="de-DE")
    assert r == {"country": "AE", "source": "manual", "manual": True}


def test_remembered_beats_ip_and_language():
    r = resolve_country(remembered="US", ip_country="GB", accept_language="de-DE")
    assert r["country"] == "US" and r["source"] == "remembered"


def test_ip_beats_language_and_language_beats_default():
    assert resolve_country(ip_country="GB", accept_language="de-DE")["country"] == "GB"
    assert resolve_country(accept_language="de-DE,de;q=0.9")["country"] == "DE"
    assert resolve_country()["country"] == "PK"  # Pakistan-first default
    assert resolve_country(explicit="XX")["country"] == "PK"  # unknown code ignored, never crashes


def test_pk_config_has_pta_cod_and_cities():
    cfg = country_config("PK")
    assert "PTA" in cfg["phone_note"]
    assert cfg["payment_norms"]["cod_common"] is True
    assert "Karachi" in cfg["cities"] and "Lahore" in cfg["cities"]
    block = location_block("PK", "smartphones")
    assert block["cod_available"] is True and "phone_note" in block


def test_lakh_crore_formatting():
    assert format_money(85_500, "PKR") == "PKR 85,500"
    assert format_money(125_000, "PKR").startswith("PKR 1.25 lakh")
    assert format_money(23_000_000, "PKR").startswith("PKR 2.3 crore")
    assert format_money(150_000, "INR").startswith("INR 1.5 lakh")
    assert format_money(1250.0, "USD") == "USD 1,250"
    assert _group_south_asian(12345678) == "1,23,45,678"


def test_compliance_update_roundtrip(tmp_path, monkeypatch):
    rec = dict(compliance.get_record("priceoye"))
    (tmp_path / "priceoye.json").write_text(json.dumps(rec))
    monkeypatch.setattr(compliance, "DATA", tmp_path)
    try:
        compliance.update_record("priceoye", status="approved", reviewer="qa",
                                 expiry_date="2999-01-01")
    except ValueError:
        raise AssertionError("approval with reviewer+expiry must succeed")
    assert compliance.is_live_enabled("priceoye") is True
    # restore real record state for other tests
    monkeypatch.setitem(compliance.RECORDS, "priceoye", rec)


def test_approval_requires_reviewer_and_expiry(tmp_path, monkeypatch):
    rec = dict(compliance.get_record("telemart"))
    (tmp_path / "telemart.json").write_text(json.dumps(rec))
    monkeypatch.setattr(compliance, "DATA", tmp_path)
    for kwargs in ({"reviewer": "", "expiry_date": "2999-01-01"}, {"reviewer": "qa", "expiry_date": None}):
        try:
            compliance.update_record("telemart", status="approved", **kwargs)
            raise AssertionError("approval without reviewer/expiry must fail")
        except ValueError:
            pass
