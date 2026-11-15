from __future__ import annotations
import os, time, urllib.request, urllib.error
from dataclasses import dataclass
from app.domain.models import RawOffer
@dataclass
class RateLimitPolicy: requests_per_minute: int=30; concurrency: int=2; timeout_seconds: float=12.0
class BaseConnector:
    name="base"; supported_countries: list[str]=[]; supported_currencies: list[str]=["USD"]
    rate_limit_policy=RateLimitPolicy(); compliance_note=""; enabled_by_default=True
    def search(self, query, filters=None, country="US"): raise NotImplementedError
    def get_product(self, url_or_id): raise NotImplementedError
    def health_check(self): return {"connector":self.name,"ok":True}
    def fetch(self, url: str) -> str:
        req=urllib.request.Request(url, headers={"User-Agent":"CheapestProductFinder/1.0 (+https://github.com/MadiWebDev/cheapest-product-scrapper)"})
        with urllib.request.urlopen(req, timeout=self.rate_limit_policy.timeout_seconds) as r: return r.read().decode("utf-8","ignore")
    def drift_check(self, offers: list[RawOffer]) -> bool:
        if not offers: return True
        invalid=sum(1 for o in offers if not o.price or o.price<=0)
        return invalid/max(len(offers),1) > 0.5
