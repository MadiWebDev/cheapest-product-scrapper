from __future__ import annotations
import os
from app.connectors.marketplaces import AmazonConnector, EbayConnector, EtsyConnector, GoogleShoppingConnector, AliExpressConnector, REGIONAL
from app.connectors.generic import GenericConnector
from app.connectors.demo import DemoConnector
def build_registry() -> dict:
    reg={"amazon":AmazonConnector(),"ebay":EbayConnector(),"etsy":EtsyConnector(),"google_shopping":GoogleShoppingConnector(),"aliexpress":AliExpressConnector(),"generic":GenericConnector()}
    for name, cls in REGIONAL.items(): reg[name]=cls()
    if os.getenv("DEMO_MODE","false").lower()=="true": reg["demo"]=DemoConnector()
    return reg
REGISTRY=build_registry()
