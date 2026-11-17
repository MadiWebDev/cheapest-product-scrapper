from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.connectors.registry import REGISTRY
from app.domain.landed import VAT, DUTY
router=APIRouter(prefix="/api/admin", tags=["admin"])
_state={n:{"enabled":True,"successes":0,"failures":0,"blocks":0} for n in REGISTRY}
@router.get("/connectors")
def health():
    from app.priceintel.health import HEALTH
    from app.priceintel.manifests import MANIFESTS
    from app.priceintel.compliance import is_live_enabled
    return {"connectors":[{"name":n, **_state[n], "health":REGISTRY[n].health_check(),
                            "runtime":HEALTH.for_connector(n),
                            "compliance_status":(MANIFESTS.get(n) or {}).get("compliance_status","unreviewed"),
                            "live_enabled":is_live_enabled(n)} for n in REGISTRY]}
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

# --- v3: compliance review administration (directive §6/§35) ---
from app.priceintel.compliance import RECORDS as COMPLIANCE_RECORDS, gate_report as _gate_report, update_record as _update_record
@router.get("/admin/compliance")
def admin_compliance(): return {"gate": _gate_report(), "records": COMPLIANCE_RECORDS}
@router.post("/admin/compliance/{source_id}")
def admin_compliance_update(source_id: str, body: dict):
    try:
        rec=_update_record(source_id, status=body.get("status",""), reviewer=body.get("reviewer",""), expiry_date=body.get("expiry_date"), reason=body.get("reason",""))
    except KeyError: raise HTTPException(404, "unknown source")
    except ValueError as e: raise HTTPException(400, str(e))
    return {"updated": source_id, "status": rec["status"], "live_enabled": rec["status"]=="approved"}

# --- v3 Phase 9: monetization admin ---
from app.priceintel.affiliate import CONVERSIONS as _CONV, revenue_report as _rev
from app.priceintel.sponsored import register_sponsored as _reg_sponsored
@router.get("/admin/revenue")
def admin_revenue(): return _rev()
@router.post("/admin/conversions")
def admin_conversion(body: dict):
    added=_CONV.add(body.get("external_id",""), body.get("connector",""), float(body.get("amount",0)), body.get("currency","USD"))
    return {"added": added, "duplicate": not added}
@router.post("/admin/sponsored")
def admin_sponsored(body: dict): return _reg_sponsored(body)
