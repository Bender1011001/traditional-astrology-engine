from datetime import datetime

from fastapi import APIRouter, HTTPException

from src.api.v1.schemas import KairosRequest  # type: ignore
from src.engine.electional import ElectionalEngine

router = APIRouter()


@router.post("/kairos")
async def find_kairos(request: KairosRequest):
    """
    Finds the 'Golden Window' (Electional Astrology) for a specific activity within a time range.
    """
    engine = ElectionalEngine()

    if request.start_date:
        try:
            start_dt = datetime.strptime(request.start_date, "%Y-%m-%d")
        except (ValueError, TypeError):
            start_dt = datetime.now()
    else:
        start_dt = datetime.now()

    # This Scan is expensive. Ideally async.
    # engine.find_kairos is CPU bound.
    # Wrapper?
    from fastapi.concurrency import run_in_threadpool

    res = await run_in_threadpool(
        engine.find_kairos,
        start_dt=start_dt,
        city=request.city,
        state=request.state,
        hours_to_scan=request.hours,
        activity=request.activity,
    )

    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])

    return res
