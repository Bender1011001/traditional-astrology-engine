from fastapi import APIRouter

from src.core.config import settings
from src.core.promo import free_individual_readings_promo_active

router = APIRouter()


@router.get("/meta")
def get_public_meta():
    """
    Public runtime flags for the frontend (no auth).
    Keep stable and small; safe to cache.
    """
    return {
        "promo": {
            "free_individual_readings": bool(free_individual_readings_promo_active()),
            "free_individual_readings_until": (
                settings.PROMO_FREE_INDIVIDUAL_READINGS_UNTIL or ""
            ).strip()
            or None,
        }
    }
