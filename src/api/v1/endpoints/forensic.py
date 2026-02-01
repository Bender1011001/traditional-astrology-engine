from fastapi import APIRouter
from src.engine.models import Chart
from src.services.engine_bridge import perform_forensic_audit_async
from src.api.v1.schemas import ChartRequest
from src.api.v1.utils import result_to_model 
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

@router.post("/audit")
async def run_audit(data: ChartRequest): # Reusing ChartRequest for simplicity
    # 1. Calculate Chart
    result = await calculate_chart_async(
        data.date,
        data.time,
        data.city,
        data.state,
        data.house_system,
        bool(data.compare_house_systems),
        data.zodiac_system,
        data.ayanamsa
    )
    
    if "error" in result:
        return {"error": result["error"]}

    # 2. Convert to Model
    chart_model = result_to_model(result)
    
    # 3. Helpers for audit (age, etc) - simplfied for B2B API (maybe they provide age?)
    age = data.age or 0
    # Provide defaults to avoid crashing if logic needs them
    
    # 4. Audit
    audit_report = await perform_forensic_audit_async(chart_model, result["meta"]["julian_day"], age=age)
    
    return audit_report
