from __future__ import annotations
from fastapi import APIRouter
from app.connectors.registry import REGISTRY
from app.domain.landed import VAT, DUTY
router=APIRouter(prefix="/api/admin", tags=["admin"])
_state={n:{"enabled":True,"successes":0,"failures":0,"blocks":0} for n in REGISTRY}
@router.get("/connectors")
def health(): return {"connectors":[{"name":n, **_state[n], "health":REGISTRY[n].health_check()} for n in REGISTRY]}
@router.post("/connectors/{name}/toggle")
def toggle(name: str, enabled: bool=True):
    if name in _state: _state[name]["enabled"]=enabled
    return {"name":name,"enabled":enabled}
@router.get("/tax-tables")
def tax_tables(): return {"vat_gst":VAT,"duty":DUTY,"label":"estimate"}
@router.get("/metrics")
def metrics():
    lines=["# HELP cpf_connectors_total Connectors registered","# TYPE cpf_connectors_total gauge", f"cpf_connectors_total {len(REGISTRY)}"]
    return "\n".join(lines)
