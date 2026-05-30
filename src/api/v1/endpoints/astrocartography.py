import logging

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool

from src.api.v1.schemas import AstrocartographyRequest
from src.engine.astrocartography import generate_astrocartography_map

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/astrocartography/map")
async def calculate_astrocartography_map(request: AstrocartographyRequest):
    """
    Generate chart-tied astrocartography lines and ranking metadata.

    The response is deterministic map data: no LLM calls and no relocation advice.
    """
    try:
        target_locations = (
            [item.model_dump() for item in request.target_locations]
            if request.target_locations
            else None
        )
        return await run_in_threadpool(
            generate_astrocartography_map,
            date_str=request.date,
            time_str=request.time,
            city=request.city,
            state=request.state or "",
            name=request.name or "Native",
            latitude=request.latitude,
            longitude=request.longitude,
            house_system=request.house_system or "W",
            zodiac_system=request.zodiac_system or "tropical",
            ayanamsa=request.ayanamsa,
            node_type=request.node_type,
            time_unknown=bool(request.time_unknown),
            intent=request.intent,
            planets=request.planets,
            target_locations=target_locations,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error("Astrocartography map generation failed: %s", repr(exc), exc_info=True)
        raise HTTPException(status_code=500, detail="Astrocartography calculation failed.")
