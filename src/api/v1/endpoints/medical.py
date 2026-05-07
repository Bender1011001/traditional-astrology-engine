from fastapi import APIRouter

from src.engine.medical import MedicalAstrology
from src.engine.models import Chart

router = APIRouter()

MEDICAL_DISCLAIMER = (
    "FOR HISTORICAL AND EDUCATIONAL RESEARCH PURPOSES ONLY. NOT MEDICAL ADVICE. "
    "DO NOT USE FOR HEALTH DECISIONS OR SURGERY SCHEDULING."
)


@router.get("/surgery_check")
async def surgery_check(body_part: str, jd: float):
    """
    Performs a traditional 'Surgery Rule' check for a specific body part and date.
    NOTE: For historical research only. NOT medical advice.
    """
    # This is a simplified check for current transits
    # In a real app, you'd pass the natal chart too
    # For now, we use a dummy natal chart or just focus on transits
    dummy_chart = Chart(sun_altitude=1, planets=[], ascendant=0, mc=0)
    res = MedicalAstrology.can_perform_surgery(body_part, jd, dummy_chart)
    res["medical_disclaimer"] = MEDICAL_DISCLAIMER
    return res
