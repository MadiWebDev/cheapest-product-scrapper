"""Scam-ad checker (directive §16.2.1): paste an ad, get risk
INDICATORS + a safe-buying checklist. Indicators only — this tool never
declares an ad a scam; it surfaces signals a buyer should verify.
"""
from __future__ import annotations

import re

_PRICE_RE = re.compile(r"(?:rs\.?|pkr|price[:\s]*)\s*([\d,]{3,})", re.I)

INDICATORS = [
    ("advance_payment", "high", ("advance payment", "advance bhejo", "pehle payment", "pay first", "100% advance"),
     "Asks for advance payment before delivery — high-risk pattern in classified ads"),
    ("off_platform_payment", "high", ("jazzcash", "easypaisa", "bank transfer only", "crypto", "gift card"),
     "Pushes payment to a direct wallet/transfer with no buyer protection"),
    ("urgency_pressure", "medium", ("only today", "hurry", "last piece", "limited time", "jaldi karo", "offer ending"),
     "Urgency pressure — a common manipulation tactic"),
    ("no_cod", "medium", ("no cod", "cod not available", "cash on delivery nahi"),
     "Refuses cash on delivery where COD is the local norm"),
    ("external_contact_only", "low", ("whatsapp only", "dm only", "call only", "no comments"),
     "Pushes all contact to a single private channel"),
    ("vague_specs", "low", ("box pack", "fresh piece", "guaranteed original"),
     "Marketing phrases in place of verifiable specs (model/storage/PTA status)"),
]

CHECKLIST = [
    "Meet in a public place or use a platform with buyer protection; avoid advance payment to personal wallets.",
    "For phones: check the IMEI on the PTA DIRBS portal and confirm PTA-approved status before paying.",
    "Verify model, storage, RAM and condition in person against the ad's claims.",
    "Prefer cash on delivery; inspect the item before the courier leaves.",
    "Compare the asking price with the fair-price band — far-below-band prices are a risk indicator.",
    "Keep the ad, chat and receipts until the purchase is complete.",
]


def analyze_ad(text: str, market_median: float | None = None) -> dict:
    low = (text or "").lower()
    found = []
    for iid, severity, needles, why in INDICATORS:
        if any(n in low for n in needles):
            found.append({"id": iid, "severity": severity, "text": why})
    m = _PRICE_RE.search(text or "")
    if m and market_median:
        price = float(m.group(1).replace(",", ""))
        if price < 0.5 * market_median:
            found.append({"id": "price_far_below_market", "severity": "high",
                          "text": f"Asking price {price:,.0f} is less than half the market median {market_median:,.0f} — verify the item exists and matches the description"})
    highs = sum(1 for f in found if f["severity"] == "high")
    level = "high" if highs >= 2 else "medium" if highs == 1 or len(found) >= 3 else "low" if found else "none_found"
    return {"indicators": found, "risk_level": level,
            "note": "Indicators only — these are signals to verify, not proof that an ad is fraudulent.",
            "checklist": CHECKLIST}
