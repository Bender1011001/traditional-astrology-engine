from fastapi import APIRouter, HTTPException

from src.api.v1.schemas import SynastryRequest  # type: ignore
from src.api.v1.utils import result_to_model
from src.engine.calculator.main import calculate_chart_data
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
        request.person_a.state or "",
        latitude=request.person_a.latitude,
        longitude=request.person_a.longitude,
        house_system=request.person_a.house_system,
        compare_house_systems=bool(request.person_a.compare_house_systems),
        zodiac_system=request.person_a.zodiac_system,
        ayanamsa=request.person_a.ayanamsa,
        node_type=request.person_a.node_type,
    )
    res_b = calculate_chart_data(
        request.person_b.date,
        request.person_b.time,
        request.person_b.city,
        request.person_b.state or "",
        latitude=request.person_b.latitude,
        longitude=request.person_b.longitude,
        house_system=request.person_b.house_system,
        compare_house_systems=bool(request.person_b.compare_house_systems),
        zodiac_system=request.person_b.zodiac_system,
        ayanamsa=request.person_b.ayanamsa,
        node_type=request.person_b.node_type,
    )

    if "error" in res_a:
        raise HTTPException(status_code=400, detail=f"Person A Error: {res_a['error']}")
    if "error" in res_b:
        raise HTTPException(status_code=400, detail=f"Person B Error: {res_b['error']}")

    chart_a = result_to_model(res_a)
    chart_b = result_to_model(res_b)

    engine = SynastryEngineAsync()
    analysis = await engine.analyze_structural_fit(chart_a, chart_b)

    return {"person_a": res_a, "person_b": res_b, "synastry": analysis}
