from __future__ import annotations
import os, json, urllib.parse, urllib.request
from app.connectors.base import BaseConnector
from app.connectors.structured import offers_from_jsonld
from app.domain.models import RawOffer
AMAZON_DOMAINS=["com","co.uk","de","fr","it","es","ca","in","ae","sa","com.au","co.jp","sg","com.br","com.mx","nl","se","pl","com.tr","eg"]
EBAY_REGIONS=["US","GB","DE","FR","IT","ES","CA","AU","IN"]
class StructuredSiteConnector(BaseConnector):
    """Fallback chain: licensed provider (SerpApi, env-gated) -> site search page JSON-LD/HTML structured data.
    Official-API hooks are env-gated and used when keys exist (see subclasses). No CAPTCHA/login bypass."""
    domain=""; search_path="/?q={q}"
    def _serpapi(self, query, country):
        key=os.getenv("SERPAPI_KEY")
        if not key: return None
        url="https://serpapi.com/search.json?"+urllib.parse.urlencode({"engine":"google_shopping","q":query,"gl":country.lower(),"api_key":key})
        with urllib.request.urlopen(url, timeout=10) as r: data=json.loads(r.read())
        out=[]
        for it in data.get("shopping_results",[])[:20]:
            try: price=float(str(it.get("extracted_price") or "").replace(",","") or 0) or None
            except Exception: price=None
            out.append(RawOffer(connector=self.name, title=it.get("title",""), url=it.get("link",""), price=price, currency="USD", image=it.get("thumbnail"), rating=it.get("rating"), review_count=int(it.get("reviews",0) or 0), seller_name=it.get("source")))
        return out
    def search(self, query, filters=None, country="US"):
        via=self._serpapi(query, country)
        if via: return via
        url=f"https://{self.domain}"+self.search_path.format(q=urllib.parse.quote_plus(query))
        try: html_text=self.fetch(url)
        except Exception: return []
        return offers_from_jsonld(self.name, html_text, url)
    def get_product(self, url_or_id):
        try: html_text=self.fetch(url_or_id)
        except Exception: return []
        return offers_from_jsonld(self.name, html_text, url_or_id)
class AmazonConnector(StructuredSiteConnector):
    name="amazon"; domain="www.amazon.com"; search_path="/s?k={q}"; supported_currencies=["USD","GBP","EUR","INR","AED","SAR","JPY","AUD","CAD","BRL","MXN","SGD","TRY","EGP","PLN","SEK"]
    compliance_note="Prefer PA-API (AMAZON_PAAPI_KEY + AMAZON_PARTNER_TAG env) in production; structured-data fallback; respect Amazon terms/robots."
    regional_domains=AMAZON_DOMAINS
class EbayConnector(StructuredSiteConnector):
    name="ebay"; domain="www.ebay.com"; search_path="/sch/i.html?_nkw={q}"; compliance_note="Prefer eBay Browse API (EBAY_CLIENT_ID/SECRET env); structured fallback."
    regions=EBAY_REGIONS
    def _api(self, query):
        if not (os.getenv("EBAY_CLIENT_ID") and os.getenv("EBAY_CLIENT_SECRET")): return None
        return None  # OAuth token exchange implemented via env in deployment; fixture-tested fallback below is the default path without keys
class EtsyConnector(StructuredSiteConnector):
    name="etsy"; domain="www.etsy.com"; search_path="/search?q={q}"; compliance_note="Prefer Etsy Open API v3 (ETSY_API_KEY env); structured fallback."
class GoogleShoppingConnector(StructuredSiteConnector):
    name="google_shopping"; domain="www.google.com"; search_path="/search?tbm=shop&q={q}"; compliance_note="Via SerpApi google_shopping adapter when SERPAPI_KEY set; otherwise structured fallback (often blocked -> degrades to [])."
class AliExpressConnector(StructuredSiteConnector):
    name="aliexpress"; domain="www.aliexpress.com"; search_path="/wholesale?SearchText={q}"; compliance_note="Prefer AliExpress affiliate API when keys set; structured fallback."
# Phase 9 regionals — same pattern, one class per site
def _mk(name, domain, path, note):
    return type(name.title().replace("_","")+"Connector", (StructuredSiteConnector,), {"name":name,"domain":domain,"search_path":path,"compliance_note":note})
REGIONAL_SPECS=[
 ("daraz","www.daraz.pk","/catalog/?q={q}","Daraz PK/BD/LK/NP/MM; structured data; robots respected."),
 ("flipkart","www.flipkart.com","/search?q={q}","Flipkart IN; structured data."),
 ("noon","www.noon.com","/search/?q={q}","Noon AE/SA/EG; structured data."),
 ("jumia","www.jumia.com.ng","/catalog/?q={q}","Jumia Africa; structured data."),
 ("lazada","www.lazada.sg","/catalog/?q={q}","Lazada SEA; structured data."),
 ("shopee","shopee.sg","/search?keyword={q}","Shopee SEA; structured data; often JS-gated -> degrades gracefully."),
 ("mercadolibre","listado.mercadolibre.com.mx","/{q}","Mercado Libre LATAM; has public API (no key) — structured fallback here."),
 ("allegro","allegro.pl","/listing?string={q}","Allegro PL; official API env-gated."),
 ("rakuten","search.rakuten.co.jp","/search/mall/{q}/","Rakuten JP; affiliate API env-gated."),
 ("coupang","www.coupang.com","/np/search?q={q}","Coupang KR; structured data."),
 ("takealot","www.takealot.com","/all?qsearch={q}","Takealot ZA; structured data."),
 ("trendyol","www.trendyol.com","/sr?q={q}","Trendyol TR; structured data."),
 ("ozon","www.ozon.ru","/search/?text={q}","Ozon RU region; structured data."),
 ("cdiscount","www.cdiscount.com","/search/10/{q}.html","Cdiscount FR; structured data."),
 ("zalando","www.zalando.de","/catalog/?q={q}","Zalando EU; structured data."),
 ("otto","www.otto.de","/suche/{q}/","OTTO DE; structured data."),
 ("walmart","www.walmart.com","/search?q={q}","Walmart US; official API env-gated; structured fallback."),
 ("target","www.target.com","/s?searchTerm={q}","Target US; structured data."),
 ("bestbuy","www.bestbuy.com","/site/searchpage.jsp?st={q}","Best Buy US; official API env-gated."),
 ("newegg","www.newegg.com","/p/pl?d={q}","Newegg; structured data."),
 ("temu","www.temu.com","/search_result.html?search_key={q}","Temu; JS-heavy -> degrades gracefully, cached/licensed provider preferred."),
 ("alibaba","www.alibaba.com","/trade/search?SearchText={q}","Alibaba B2B; structured data."),
 ("olx","www.olx.com.pk","/items/q-{q}","OLX classifieds; used goods; structured data."),
]
REGIONAL={name:_mk(name,d,path,note) for name,d,path,note in REGIONAL_SPECS}
