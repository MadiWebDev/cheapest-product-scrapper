"""Tracked outbound redirect — GET /go/:offerId (directive §1.7, §29A).

Safety rules:
- The destination comes only from a server-side offer record created
  during search; never from a user-supplied URL (no open redirects).
- The destination host is re-validated at click time against the
  per-marketplace allowlist below.
- An affiliate tag is appended only when one is configured via env
  (AFFILIATE_TAG_<CONNECTOR> or AFFILIATE_TAG_DEFAULT); otherwise the
  plain destination is used. Clicks are recorded with the affiliate
  flag so revenue analytics can separate tagged/untagged traffic.
"""
from __future__ import annotations

import hashlib
import os
import time
import urllib.parse

# host == domain or host is a subdomain of it
ALLOWED_DOMAINS: dict[str, list[str]] = {
    "amazon": ["amazon.com", "amazon.co.uk", "amazon.de", "amazon.fr", "amazon.it",
               "amazon.es", "amazon.ca", "amazon.in", "amazon.ae", "amazon.sa",
               "amazon.com.au", "amazon.co.jp", "amazon.sg", "amazon.com.br",
               "amazon.com.mx", "amazon.nl", "amazon.se", "amazon.pl",
               "amazon.com.tr", "amazon.eg"],
    "ebay": ["ebay.com", "ebay.co.uk", "ebay.de", "ebay.fr", "ebay.it", "ebay.es",
             "ebay.ca", "ebay.com.au", "ebay.in"],
    "etsy": ["etsy.com"],
    "google_shopping": ["google.com"],
    "aliexpress": ["aliexpress.com"],
    "demo": ["demo.example"],
    "daraz": ["daraz.pk", "daraz.com.bd", "daraz.lk", "daraz.com.np", "daraz.com.mm"],
    "flipkart": ["flipkart.com"],
    "noon": ["noon.com"],
    "jumia": ["jumia.com.ng", "jumia.com.eg", "jumia.co.ke", "jumia.com.gh"],
    "lazada": ["lazada.sg", "lazada.com.my", "lazada.co.id", "lazada.vn",
               "lazada.co.th", "lazada.com.ph"],
    "shopee": ["shopee.sg", "shopee.com.my", "shopee.co.id", "shopee.vn",
               "shopee.co.th", "shopee.ph", "shopee.com.br", "shopee.com.mx"],
    "mercadolibre": ["mercadolibre.com.mx", "mercadolibre.com.ar", "mercadolibre.com.br",
                     "mercadolibre.com.co", "mercadolibre.cl"],
    "allegro": ["allegro.pl"],
    "rakuten": ["rakuten.co.jp"],
    "coupang": ["coupang.com"],
    "takealot": ["takealot.com"],
    "trendyol": ["trendyol.com"],
    "ozon": ["ozon.ru"],
    "cdiscount": ["cdiscount.com"],
    "zalando": ["zalando.de", "zalando.co.uk", "zalando.fr", "zalando.it", "zalando.es"],
    "otto": ["otto.de"],
    "walmart": ["walmart.com"],
    "target": ["target.com"],
    "bestbuy": ["bestbuy.com"],
    "newegg": ["newegg.com"],
    "temu": ["temu.com"],
    "alibaba": ["alibaba.com"],
    "olx": ["olx.com.pk"],
    "generic": [],  # user-supplied URL feature: any http/https host (SSRF-checked at extraction time)
}


def offer_id_for(connector: str, url: str) -> str:
    return hashlib.sha256(f"{connector}|{url}".encode()).hexdigest()[:16]


def destination_allowed(connector: str, url: str) -> bool:
    u = urllib.parse.urlparse(url)
    if u.scheme not in ("http", "https") or not u.hostname:
        return False
    host = u.hostname.lower()
    if connector == "generic":
        return True
    domains = ALLOWED_DOMAINS.get(connector)
    if domains is None:
        return False
    return any(host == d or host.endswith("." + d) for d in domains)


def apply_affiliate(url: str, connector: str) -> tuple[str, bool]:
    tag = os.getenv(f"AFFILIATE_TAG_{connector.upper()}") or os.getenv("AFFILIATE_TAG_DEFAULT")
    if not tag:
        return url, False
    param = os.getenv(f"AFFILIATE_PARAM_{connector.upper()}", "tag")
    u = urllib.parse.urlparse(url)
    q = urllib.parse.parse_qsl(u.query)
    if param in dict(q):
        return url, True
    q.append((param, tag))
    return urllib.parse.urlunparse(u._replace(query=urllib.parse.urlencode(q))), True


BOT_TOKENS = ("bot", "crawler", "spider", "preview", "headless", "curl", "wget",
              "python-requests", "monitor", "pingdom")


def is_bot_ua(user_agent: str | None) -> bool:
    ua = (user_agent or "").lower()
    return any(tok in ua for tok in BOT_TOKENS)


class OfferStore:
    """In-process offer + click store for the walking skeleton.

    Deliberately simple (single-process). The DB-backed store is a
    later-phase concern; the interface (register/get/record_click)
    is what the router and analytics depend on.
    """

    def __init__(self) -> None:
        self.offers: dict[str, dict] = {}
        self.clicks: list[dict] = []

    def register(self, offer_id: str, offer, product_title: str = "") -> None:
        self.offers[offer_id] = {
            "offer_id": offer_id,
            "connector": offer.connector,
            "url": offer.url,
            "title": offer.title,
            "product_title": product_title,
            "price": offer.price,
            "currency": offer.currency,
            "demo": bool(getattr(offer, "demo", False)),
            "registered_at": time.time(),
        }

    def get(self, offer_id: str) -> dict | None:
        return self.offers.get(offer_id)

    def record_click(self, offer_id: str, entry: dict, affiliate_applied: bool,
                     user_agent: str | None = None) -> dict:
        click = {
            "offer_id": offer_id,
            "connector": entry["connector"],
            "ts": time.time(),
            "affiliate_applied": affiliate_applied,
            "demo": entry.get("demo", False),
            "bot": is_bot_ua(user_agent),
        }
        self.clicks.append(click)
        return click

    def click_summary(self) -> dict:
        by: dict[str, int] = {}
        for c in self.clicks:
            by[c["connector"]] = by.get(c["connector"], 0) + 1
        return {"total_clicks": len(self.clicks), "by_connector": by}


STORE = OfferStore()
