from datetime import datetime
from fastapi import APIRouter, HTTPException
from src.api.v1.schemas import HoraryRequest
from src.engine.chart_calculator import calculate_chart_data, get_local_datetime_now
from src.engine.horary import build_horary_oracle
from src.api.v1.utils import result_to_model

router = APIRouter()

@router.post("/horary")
async def horary_oracle(request: HoraryRequest):
    """
    Casts a Horary chart and provides an 'Oracle' interpretation for a specific question.
    """
    question = (request.question or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is required for horary.")

    date_str = request.date
    time_str = request.time
    if not date_str or not time_str:
        try:
            local_dt = get_local_datetime_now(request.city, request.state)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Location error: {str(e)}")
        date_str = local_dt.strftime("%Y-%m-%d")
        time_str = local_dt.strftime("%H:%M")

    res = calculate_chart_data(date_str, time_str, request.city, request.state)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])

    chart_model = result_to_model(res)
    oracle = build_horary_oracle(question, chart_model)

    return {
        "meta": res.get("meta", {}),
        "oracle": oracle
    }
