from fastapi import APIRouter, Depends, Request, HTTPException
from src.engine.models import Chart
from src.services.engine_bridge import perform_forensic_audit_async
from src.api.v1.schemas import ChartRequest
from src.api.v1.utils import result_to_model 
from src.api.v1.middleware.auth import verify_api_key
from src.api.v1.middleware.rate_limiting import enforce_rate_limit
# Wait, perform_forensic_audit logic usually takes Chart object.
# But `ChartRequest` is raw input. We need `calculate_chart_data` first to get positions?
# The plan says: "Directly expose the audit logic ... wrapped in threadpool."
# But audit needs a calculated chart.
# If the user passes raw data, we must calculate first.
# Unless B2B client passes calculated positions?
# "perform_forensic_audit" in `src/engine/logic.py` takes `chart: Chart`.
# So we need to calculate it.

from src.services.engine_bridge import calculate_chart_async

router = APIRouter()

from src.services.engine_bridge import generate_full_nativity_async

@router.post("/audit")
async def run_audit(
    data: ChartRequest,
    request: Request,
    auth_context: dict = Depends(verify_api_key)
): 
    # 1. Enforce Authentication
    if not auth_context:
        raise HTTPException(status_code=401, detail="X-API-Key required for forensic audit")

    # 2. Enforce Rate Limit
    await enforce_rate_limit(request, auth_context)

    # 3. Directly call the Hub Engine
    result = await generate_full_nativity_async(
        date_str=data.date,
        time_str=data.time,
        city=data.city,
        state=data.state,
        name=data.name or "Native",
        house_system=data.house_system,
        zodiac_system=data.zodiac_system,
        ayanamsa=data.ayanamsa
    )
    
    if "error" in result:
        return {"error": result["error"]}

    # Return just the detailed forensic analysis part for this endpoint
    # (or the whole thing if requested, but 'audit' implies the deep dive)
    if "technical_data" in result and "planets_forensic" in result["technical_data"]:
        return {
            "forensic_report": result["technical_data"]["planets_forensic"],
            "analysis": result["technical_data"]["analysis"]
        }
    
    return result
