import logging

from fastapi import APIRouter, HTTPException

from src.api.v1.schemas import GeomancyRequest
from src.engine.geomancy import cast_geomancy

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/geomancy/cast")
async def cast_geomantic_shield(payload: GeomancyRequest):
    """
    Cast a classical geomantic shield from line counts, mother rows, or
    server-side secure random counts.
    """
    try:
        return cast_geomancy(
            payload.question,
            mother_counts=payload.mother_counts,
            mothers=payload.mothers,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Geomancy cast failed: %s", repr(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Could not cast geomancy shield.")
