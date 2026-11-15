import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from app.connectors.structured import offers_from_jsonld
from app.connectors.generic import assert_public_url
from app.connectors.registry import REGISTRY
HTML=pathlib.Path(__file__).parent.joinpath("fixtures/product_page.html").read_text()
def test_jsonld_parse():
    offers=offers_from_jsonld("test", HTML, "https://shop.example/p1")
    assert len(offers)==1 and offers[0].price==349.0 and offers[0].gtin=="0027242919999" and offers[0].rating==4.8
def test_ssrf_blocks_localhost():
    import socket
    orig=socket.getaddrinfo
    socket.getaddrinfo=lambda h, *a, **k: [(None,None,None,None,("127.0.0.1",0))]
    try:
        try: assert_public_url("http://localhost/x"); assert False
        except ValueError: pass
    finally: socket.getaddrinfo=orig
def test_registry_has_global_and_regional():
    for n in ["amazon","ebay","etsy","google_shopping","aliexpress","generic","daraz","flipkart","noon","shopee","mercadolibre","allegro","walmart","temu"]: assert n in REGISTRY, n
    assert len(REGISTRY)>=28
def test_drift_detector():
    from app.connectors.base import BaseConnector
    assert BaseConnector().drift_check([]) is True
