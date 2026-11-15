import sys, pathlib, os
os.environ["DEMO_MODE"]="true"
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
# rebuild registry with demo
import importlib
import app.connectors.registry as reg; importlib.reload(reg)
import app.services.search as ss; ss.REGISTRY=reg.REGISTRY
def test_demo_search_groups_and_scores():
    r=ss.search("iphone", {}, "US", "USD", connectors=["demo"])
    assert r["total_offers"]>=1 and r["products"][0]["offers"][0]["quality_score"]>0
    assert r["products"][0]["offers"][0]["landed"] is not None
def test_filters_exclude():
    r=ss.search("iphone", {"max_price":10}, "US", "USD", connectors=["demo"]); assert r["total_offers"]==0
def test_fake_discount_and_buy_timing():
    from app.services.search import fake_discount, good_time_to_buy
    assert fake_discount(200,150,155)["fake"] is True
    assert good_time_to_buy([100,110,105,120,115], 99)["verdict"]=="good"
