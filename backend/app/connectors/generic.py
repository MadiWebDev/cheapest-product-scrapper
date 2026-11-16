from __future__ import annotations
import ipaddress, socket, urllib.parse
from app.connectors.base import BaseConnector
from app.connectors.structured import offers_from_jsonld, extract_opengraph
from app.domain.models import RawOffer
from app.domain.normalize import clean_price
def assert_public_url(url: str) -> None:
    """SSRF guard: https/http only, host must resolve to a public IP."""
    u=urllib.parse.urlparse(url)
    if u.scheme not in ("http","https") or not u.hostname: raise ValueError("invalid url")
    if u.username or u.password: raise ValueError("credentials in URL blocked")
    infos=socket.getaddrinfo(u.hostname, None)
    for info in infos:
        ip=ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast: raise ValueError("private/reserved IP blocked")
class GenericConnector(BaseConnector):
    name="generic"; compliance_note="User-supplied URL only; JSON-LD/OpenGraph extraction; SSRF-guarded; robots respected by caller's fetch policy."
    def search(self, query, filters=None, country="US"):
        if query.startswith("http"): return self.get_product(query)
        return []
    def get_product(self, url_or_id):
        assert_public_url(url_or_id); html_text=self.fetch(url_or_id)
        offers=offers_from_jsonld(self.name, html_text, url_or_id)
        if offers: return offers
        og=extract_opengraph(html_text)
        if og.get("title"):
            return [RawOffer(connector=self.name, title=og["title"], url=url_or_id, price=clean_price(og.get("price")), image=og.get("image"))]
        return []
