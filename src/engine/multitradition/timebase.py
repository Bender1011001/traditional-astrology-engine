"""Time bases shared by several traditions.

Chinese, Tibetan, and Mesoamerican sections each need a different answer to
"which day is this?" and the Chinese hour pillar needs a solar-time decision the
research pack deliberately refuses to default. This module computes every
candidate and hands them to the sections labeled, rather than picking silently.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

import swisseph as swe


@dataclass(frozen=True)
class TimeBases:
    utc: datetime
    julian_day_ut: float
    julian_day_number: int
    local_mean_time: datetime
    true_solar_time: datetime
    equation_of_time_minutes: float


def compute(utc_dt: datetime, longitude: float) -> TimeBases:
    """Derive the civil/mean-solar/true-solar candidates for one birth moment."""
    jd_ut = swe.julday(
        utc_dt.year,
        utc_dt.month,
        utc_dt.day,
        utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600,
    )
    # Integer JDN identifying the civil day (noon-anchored), used by the Maya
    # kernel's integer-date semantics and by sexagenary day counting.
    jdn = int(swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, 12.0))

    local_mean = utc_dt + timedelta(hours=longitude / 15.0)
    eot_days = swe.time_equ(jd_ut)
    if isinstance(eot_days, (tuple, list)):
        eot_days = eot_days[1] if len(eot_days) > 1 else eot_days[0]
    true_solar = local_mean + timedelta(days=float(eot_days))

    return TimeBases(
        utc=utc_dt,
        julian_day_ut=jd_ut,
        julian_day_number=jdn,
        local_mean_time=local_mean,
        true_solar_time=true_solar,
        equation_of_time_minutes=float(eot_days) * 24 * 60,
    )
