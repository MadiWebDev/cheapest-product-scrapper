"""AffiliateService (directive §17): the single place that knows about
affiliate tags, click quality and revenue analytics.

Rules:
- Tags come only from configuration (env): AFFILIATE_TAG_<CONNECTOR>,
  AFFILIATE_TAG_<CONNECTOR>_<COUNTRY>, AFFILIATE_TAG_DEFAULT.
- Estimated revenue (clicks x configured EPC) and confirmed revenue
  (imported conversion records) are ALWAYS reported separately and
  never summed — an estimate is not earnings.
- Bot-looking clicks are recorded but excluded from revenue estimates.
"""
from __future__ import annotations

import os

from app.priceintel.go import STORE, is_bot_ua  # noqa: F401  (re-exported)


def resolve_tag(connector: str, country: str | None = None) -> str | None:
    if country:
        v = os.getenv(f"AFFILIATE_TAG_{connector.upper()}_{country.upper()}")
        if v:
            return v
    return os.getenv(f"AFFILIATE_TAG_{connector.upper()}") or os.getenv("AFFILIATE_TAG_DEFAULT")


def configured_epc(connector: str) -> float | None:
    """Expected earnings per click, ONLY when the operator configured it
    from their affiliate dashboard. Never invented."""
    v = os.getenv(f"AFFILIATE_EPC_{connector.upper()}")
    return float(v) if v else None


class ConversionLedger:
    """Confirmed conversions imported from affiliate networks.
    Deduplicated by the network's external id."""

    def __init__(self) -> None:
        self.records: dict[str, dict] = {}

    def add(self, external_id: str, connector: str, amount: float, currency: str = "USD") -> bool:
        if external_id in self.records:
            return False
        self.records[external_id] = {"external_id": external_id, "connector": connector,
                                     "amount": amount, "currency": currency}
        return True

    def totals(self) -> dict[str, float]:
        out: dict[str, float] = {}
        for r in self.records.values():
            out[r["connector"]] = out.get(r["connector"], 0.0) + r["amount"]
        return out


CONVERSIONS = ConversionLedger()


def revenue_report() -> dict:
    clicks = STORE.clicks
    human = [c for c in clicks if not c.get("bot")]
    bots = len(clicks) - len(human)
    est: dict[str, dict] = {}
    for c in human:
        if not c.get("affiliate_applied"):
            continue
        epc = configured_epc(c["connector"])
        slot = est.setdefault(c["connector"], {"clicks": 0, "epc_configured": epc is not None,
                                               "estimated_revenue": None})
        slot["clicks"] += 1
        if epc is not None:
            slot["estimated_revenue"] = round((slot["estimated_revenue"] or 0) + epc, 4)
    return {
        "clicks": {"total": len(clicks), "human": len(human), "bot_filtered": bots},
        "estimated": {"by_connector": est,
                      "note": "Estimate = human tagged clicks x operator-configured EPC. Not earnings."},
        "confirmed": {"by_connector": CONVERSIONS.totals(),
                      "note": "Imported network conversion records only, deduplicated by external id."},
    }
