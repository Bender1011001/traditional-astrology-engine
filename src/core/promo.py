from __future__ import annotations

from datetime import datetime, timezone, date

from src.core.config import settings


def free_individual_readings_promo_active(now: datetime | None = None) -> bool:
    """
    Returns True when the temporary "free individual readings" promo is active.

    Design intent:
    - Keep existing free-tier rate limiting/quota behavior.
    - Only provide a signal (meta.promo_unlocked) so the UI can suppress paywall gating.
    """
    if not bool(getattr(settings, "PROMO_FREE_INDIVIDUAL_READINGS", False)):
        return False

    until = (getattr(settings, "PROMO_FREE_INDIVIDUAL_READINGS_UNTIL", "") or "").strip()
    if not until:
        return True

    try:
        until_d = date.fromisoformat(until)
    except ValueError:
        # Misconfigured date should fail closed.
        return False

    now_d = (now or datetime.now(timezone.utc)).date()
    return now_d <= until_d

