"""Phase 13 expansion features (directive §16.2), each behind a flag:
FEATURE_<NAME>=false disables the endpoint (503). Defaults: on for the
self-contained rule/content features; smart_digest defaults off (it is
a job, enabled by the operator).
"""
from __future__ import annotations

import os
import time

DEFAULTS = {"used_phone_kit": True, "compatibility": True, "budget_planner": True,
            "outcomes": True, "evidence_pack": True, "alternatives": True,
            "deal_passport": True, "smart_digest": False}


def feature_enabled(name: str) -> bool:
    v = os.getenv(f"FEATURE_{name.upper()}")
    if v is not None:
        return v.lower() == "true"
    return DEFAULTS.get(name, False)


# --- 1. used-phone safety kit -------------------------------------------------

USED_PHONE_KIT = {
    "title": "Used-phone safety kit",
    "sections": [
        {"id": "identity", "title": "Identity & lock checks", "items": [
            "Dial *#06# and match the IMEI on screen with the box/receipt and the SIM tray.",
            "Pakistan: verify PTA approval on the DIRBS portal/app before paying; a non-PTA phone loses SIM service.",
            "Check iCloud / Google FRP lock: sign in with YOUR account during the meeting; a locked phone is worthless.",
            "Confirm the seller can factory-reset the phone in front of you."]},
        {"id": "hardware", "title": "Hardware checks", "items": [
            "Battery health: iPhone Settings > Battery; Android dialer codes vary — ask for a screenshot before meeting.",
            "Screen: show pure white/black images to spot burn-in, dead pixels and replaced panels.",
            "Ports & buttons: plug in a charger, test volume/power buttons, cameras, speaker and microphone on a call.",
            "Water damage: check the SIM-tray moisture indicator; avoid phones with fogged camera lenses."]},
        {"id": "deal", "title": "Deal safety", "items": [
            "Meet in a public place; never pay in advance to a personal wallet.",
            "Compare the asking price with the fair-price band; far-below-band is a risk indicator.",
            "Get a written receipt with the IMEI, price, date and seller contact."]},
    ],
}


# --- 2. compatibility checker ---------------------------------------------------

def check_compatibility(device: dict, country: str) -> dict:
    from app.priceintel.location import country_config
    cfg = country_config(country) or {}
    checks: list[dict] = []
    plug = (device.get("plug") or "").upper()
    dest_plug = (cfg.get("plug") or "")
    if plug:
        ok = plug in dest_plug.replace(" ", "").split("/") or plug in dest_plug
        checks.append({"id": "plug", "status": "ok" if ok else "adapter_needed",
                       "text": f"Device plug {plug} vs {country} sockets ({dest_plug})"})
    if device.get("dual_voltage") is False:
        checks.append({"id": "voltage", "status": "converter_needed",
                       "text": f"Device is not dual-voltage; {country} supply is {cfg.get('voltage')} — a converter is required"})
    elif device.get("dual_voltage") is True:
        checks.append({"id": "voltage", "status": "ok", "text": "Dual-voltage device works on any mains supply"})
    if device.get("carrier_locked"):
        checks.append({"id": "carrier", "status": "blocked",
                       "text": "Carrier-locked device will not work on other networks until unlocked by the carrier"})
    if cfg.get("phone_note") and device.get("kind") == "phone":
        checks.append({"id": "registration", "status": "check_required", "text": cfg["phone_note"]})
    verdict = "blocked" if any(c["status"] == "blocked" for c in checks) else \
        "action_needed" if any(c["status"] in ("adapter_needed", "converter_needed", "check_required") for c in checks) else "ok"
    return {"country": country, "verdict": verdict, "checks": checks}


# --- 4. purchase-outcome feedback ------------------------------------------------

OUTCOMES = ("as_described", "fake_or_counterfeit", "damaged", "late_delivery", "never_arrived", "wrong_item")


class OutcomeStore:
    def __init__(self) -> None:
        self.records: list[dict] = []

    def add(self, seller: str, outcome: str, note: str = "", user_ref: str = "") -> dict:
        if outcome not in OUTCOMES:
            raise ValueError(f"outcome must be one of {OUTCOMES}")
        rec = {"seller": seller, "outcome": outcome, "note": note,
               "user_ref": user_ref, "ts": time.time()}
        self.records.append(rec)
        return rec

    def summary(self, seller: str) -> dict:
        rows = [r for r in self.records if r["seller"] == seller]
        counts: dict[str, int] = {}
        for r in rows:
            counts[r["outcome"]] = counts.get(r["outcome"], 0) + 1
        bad = sum(counts.get(k, 0) for k in ("fake_or_counterfeit", "never_arrived", "wrong_item"))
        return {"seller": seller, "total_reports": len(rows), "by_outcome": counts,
                "trust_calibration_flag": bad >= 3,
                "calibration_note": ("3+ serious outcome reports — trust inputs for this seller "
                                     "should be reviewed (calibration signal, not a verdict)") if bad >= 3 else ""}


OUTCOME_STORE = OutcomeStore()


# --- 7. deal passport -------------------------------------------------------------

class PassportLog:
    """Evidence timeline assembled from checks actually performed."""

    def __init__(self) -> None:
        self.events: list[dict] = []

    def record(self, product_title: str, kind: str, detail: dict) -> None:
        self.events.append({"ts": time.time(), "product": product_title, "kind": kind, "detail": detail})

    def for_product(self, product_title: str) -> list[dict]:
        return [dict(e) for e in self.events if e["product"] == product_title]


PASSPORT = PassportLog()
