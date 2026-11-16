#!/usr/bin/env python3
"""Generate adapter manifests (directive §8) from the live registry +
compliance records, so manifests cannot silently drift from the code.
Artifacts: backend/app/data/manifests/<connector>.json (versioned).
Run: ~/workspace/cpf-venv/bin/python tools/gen_manifests.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app.connectors.registry import REGISTRY  # noqa: E402
from app.priceintel.compliance import RECORDS  # noqa: E402

OUT = ROOT / "backend" / "app" / "data" / "manifests"
OUT.mkdir(parents=True, exist_ok=True)

API_PREFERRED = {"amazon", "ebay", "etsy", "aliexpress", "google_shopping"}


def access_method(name: str, conn) -> str:
    rec = RECORDS.get(name)
    if rec:
        return rec.get("access_method", "unreviewed")
    if name == "demo":
        return "fixture"
    if name == "generic":
        return "user_supplied_url"
    if name in API_PREFERRED:
        return "official_api_preferred_structured_fallback"
    return "public_structured_data"


def main() -> None:
    for name, conn in sorted(REGISTRY.items()):
        rec = RECORDS.get(name)
        pol = conn.rate_limit_policy
        manifest = {
            "id": name,
            "countries": list(conn.supported_countries),
            "currencies": list(conn.supported_currencies),
            "access_method": access_method(name, conn),
            "compliance_id": name if rec else None,
            "compliance_status": rec["status"] if rec else "unreviewed",
            "rate_limit": {"requests_per_minute": pol.requests_per_minute,
                           "concurrency": pol.concurrency,
                           "timeout_seconds": pol.timeout_seconds},
            "cache_ttl_seconds": {"search": 900, "product": 3600},
            "data_use": {"may_store_offers": True, "may_display_price": True,
                         "attribution": "Source name shown with every offer; outbound via /go"},
            "compliance_note": conn.compliance_note,
        }
        domain = getattr(conn, "domain", None)
        if domain:
            manifest["search_template"] = f"https://{domain}" + getattr(conn, "search_path", "")
        (OUT / f"{name}.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
        print("manifest:", name, manifest["compliance_status"])
    print(f"{len(REGISTRY)} manifests written to {OUT}")


if __name__ == "__main__":
    main()
