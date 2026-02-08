from fastapi import APIRouter, HTTPException
from src.api.v1.schemas import SynastryRequest
from src.engine.calculator.main import calculate_chart_data
from src.api.v1.utils import result_to_model
from src.services.engine_bridge import SynastryEngineAsync

router = APIRouter()

@router.post("/synastry")
async def calculate_synastry(request: SynastryRequest):
    """
    Analyzes the 'Structural Fit' between two people using Traditional Synastry rules.
    """
    # Calculate both charts
    # Note: calculate_chart_data is sync. We should use wrapper if high load.
    # Synastry involves 2 charts + comparison.
    # For now, direct call or wrapper?
    # Let's use direct call for chart calc (as before) but wrap the analysis.
    
    res_a = calculate_chart_data(
        request.person_a.date,
        request.person_a.time,
        request.person_a.city,
        request.person_a.state,
        request.person_a.house_system,
        bool(request.person_a.compare_house_systems),
        request.person_a.zodiac_system,
        request.person_a.ayanamsa
    )
    res_b = calculate_chart_data(
        request.person_b.date,
        request.person_b.time,
        request.person_b.city,
        request.person_b.state,
        request.person_b.house_system,
        bool(request.person_b.compare_house_systems),
        request.person_b.zodiac_system,
        request.person_b.ayanamsa
    )
    
    if "error" in res_a:
        raise HTTPException(status_code=400, detail=f"Person A Error: {res_a['error']}")
    if "error" in res_b:
        raise HTTPException(status_code=400, detail=f"Person B Error: {res_b['error']}")
        
    chart_a = result_to_model(res_a)
    chart_b = result_to_model(res_b)
    
    engine = SynastryEngineAsync()
    analysis = await engine.analyze_structural_fit(chart_a, chart_b)
    
    return {
        "person_a": res_a,
        "person_b": res_b,
        "synastry": analysis
    }
