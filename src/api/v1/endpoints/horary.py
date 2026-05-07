
from fastapi import APIRouter, Depends, HTTPException, Request

from src.api.v1.middleware.horary_rate_limiter import enforce_horary_rate_limit
from src.api.v1.schemas import HoraryRequest  # type: ignore
from src.api.v1.utils import result_to_model
from src.engine.calculator.main import calculate_chart_data
from src.engine.horary import build_horary_oracle

router = APIRouter()


@router.post("/horary", dependencies=[Depends(enforce_horary_rate_limit)])
async def horary_oracle(payload: HoraryRequest, request: Request):
    """
    Casts a Horary chart and provides an 'Oracle' interpretation for a specific question.
    """
    question = (payload.question or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is required for horary.")

    date_str = payload.date
    time_str = payload.time
    lat = getattr(payload, "latitude", None)
    lon = getattr(payload, "longitude", None)

    if not date_str or not time_str or lat is None or lon is None:
        from datetime import datetime

        import pytz  # type: ignore

        from src.engine.calculator.geo import get_coordinates, get_timezone

        try:
            if lat is None or lon is None:
                lat, lon = get_coordinates(payload.city, payload.state)
            if not date_str or not time_str:
                tz_str = get_timezone(lat, lon)
                local_dt = datetime.now(pytz.timezone(tz_str))
                date_str = date_str or local_dt.strftime("%Y-%m-%d")
                time_str = time_str or local_dt.strftime("%H:%M")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Location error: {str(e)}")

    # Enforce Regiomontanus (R) for standard classical Horary math, overridden if payload specified
    res = calculate_chart_data(
        date_str,
        time_str,
        payload.city,
        payload.state,
        latitude=lat,
        longitude=lon,
        house_system="R",
    )
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])

    chart_model = result_to_model(res)
    oracle = build_horary_oracle(question, chart_model)

    return {"meta": res.get("meta", {}), "oracle": oracle}
