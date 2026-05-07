from datetime import datetime, timezone

import swisseph as swe
from fastapi import APIRouter, HTTPException

from src.api.v1.schemas import WorldRequest  # type: ignore
from src.engine.mundane import build_world_dashboard

router = APIRouter()


@router.post("/world")
async def world_dashboard(request: WorldRequest):
    """
    Renders the 'Universal Overdrive' dashboard for global astrological events.
    """
    dt = None
    if request.date or request.time:
        date_str = request.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        time_str = request.time or "12:00"
        try:
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Date parsing error: {str(e)}")
    else:
        dt = datetime.now(timezone.utc)

    jd = swe.julday(
        dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0 + dt.second / 3600.0
    )
    dashboard = build_world_dashboard(jd)
    dashboard["timestamp"] = dt.isoformat() + "Z"
    return dashboard
