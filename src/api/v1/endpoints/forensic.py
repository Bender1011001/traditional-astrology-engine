from fastapi import APIRouter, Depends, HTTPException, Request

from src.api.v1.middleware.auth import verify_api_key
from src.api.v1.middleware.rate_limiting import enforce_rate_limit
from src.api.v1.schemas import ChartRequest  # type: ignore

router = APIRouter()

from src.services.engine_bridge import generate_full_nativity_async


@router.post("/audit")
async def run_audit(
    data: ChartRequest, request: Request, auth_context: dict = Depends(verify_api_key)
):
    # 1. Enforce Authentication
    if not auth_context:
        raise HTTPException(
            status_code=401, detail="X-API-Key required for forensic audit"
        )

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
        ayanamsa=data.ayanamsa,
        node_type=data.node_type,
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # Return just the detailed forensic analysis part for this endpoint
    # (or the whole thing if requested, but 'audit' implies the deep dive)
    if "technical_data" in result and "planets_forensic" in result["technical_data"]:
        return {
            "forensic_report": result["technical_data"]["planets_forensic"],
            "analysis": result["technical_data"]["analysis"],
        }

    return result
