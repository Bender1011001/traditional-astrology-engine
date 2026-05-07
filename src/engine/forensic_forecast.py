from datetime import datetime, timedelta
from typing import Dict, List

import swisseph as swe

from .models import Chart, Sign
from .prediction import (calculate_daily_profection,
                         calculate_monthly_profection,
                         calculate_profection_sign, get_lord_of_year)


def get_profection_timings(birth_date: datetime, target_date: datetime):
    """
    Calculates symbolic profection timing parameters based on 30-day month logic.
    """
    # Age (completed years)
    age = (
        target_date.year
        - birth_date.year
        - ((target_date.month, target_date.day) < (birth_date.month, birth_date.day))
    )

    # Last birthday
    last_birthday = datetime(target_date.year, birth_date.month, birth_date.day)
    if last_birthday > target_date:
        last_birthday = datetime(target_date.year - 1, birth_date.month, birth_date.day)

    days_since_birthday = (target_date - last_birthday).days

    # Valens/Traditional: 1 month = 30 days.
    # Month in profection year (1-12)
    profection_month = (days_since_birthday // 30) + 1
    if profection_month > 12:
        profection_month = 12

    # Day in profection month (1-30)
    profection_day = (days_since_birthday % 30) + 1

    return age, profection_month, float(profection_day)


def calculate_5_day_forecast(
    natal_chart: Chart, birth_jd: float, start_date: datetime
) -> List[Dict]:
    forecast = []

    # 1. Birth Info
    birth_y, birth_m, birth_d, birth_h = swe.revjul(birth_jd)
    # Convert to datetime for logic
    # Note: birth_h is fractional hour
    hour = int(birth_h)
    minute = int((birth_h - hour) * 60)
    second = int(((birth_h - hour) * 60 - minute) * 60)
    try:
        birth_dt = datetime(
            int(birth_y), int(birth_m), int(birth_d), hour, minute, second
        )
    except ValueError:
        # Fallback if weird date
        birth_dt = datetime(int(birth_y), int(birth_m), int(birth_d))

    # 2. Natal Constants
    asc_sign_idx = int(natal_chart.ascendant / 30) % 12
    asc_sign = list(Sign)[asc_sign_idx]

    # Flags for Swiss Ephemeris
    flags = swe.FLG_SWIEPH

    for i in range(5):
        target_date = start_date + timedelta(days=i)
        age, prof_m, prof_d = get_profection_timings(birth_dt, target_date)

        # A. Profections
        ann_sign = calculate_profection_sign(asc_sign, age)
        loy_name = get_lord_of_year(ann_sign)

        mon_sign = calculate_monthly_profection(ann_sign, prof_m)
        day_sign = calculate_daily_profection(mon_sign, prof_d)
        day_lord_name = get_lord_of_year(day_sign)

        # B. Transits for this day (at Noon for general day feel)
        target_jd = swe.julday(
            target_date.year, target_date.month, target_date.day, 12.0
        )

        # Transiting LoY
        loy_pid = getattr(swe, loy_name.value.upper(), swe.SUN)
        loy_trans_res = swe.calc_ut(target_jd, loy_pid, flags)[0]
        loy_trans_lon = loy_trans_res[0]
        loy_trans_sign = list(Sign)[int(loy_trans_lon / 30) % 12]

        # C. Epitasis Check
        # Is the Daily Profection Sign the sign where the Lord of the Year is currently transiting?
        is_epitasis = day_sign == loy_trans_sign

        # D. Mood & Dignity
        # Mood based on Day Lord's status in NATAL chart
        natal_day_lord = next(
            (p for p in natal_chart.planets if p.name == day_lord_name), None
        )
        mood = "Neutral"
        if natal_day_lord:
            # Use a simplified dignity or just the existing logic
            # For speed, we check natal sign
            sect = "DAY" if natal_chart.sun_altitude > 0 else "NIGHT"
            # Actually we can just use the name
            # Score it
            score = 0
            if natal_day_lord.sign == ann_sign:
                score += 2  # Year favoritism
            # Simplified mood logic
            if score > 0:
                mood = "Empowered"
            else:
                mood = "Standard"

        # F. Synthesis
        day_data = {
            "date": target_date.strftime("%Y-%m-%d"),
            "display_date": target_date.strftime("%A, %b %d"),
            "chronocrator": day_lord_name.value,
            "profection_sign": day_sign.value,
            "epitasis": is_epitasis,
            "mood": mood,
            "summary": f"The '{day_lord_name.value}' domain is active. "
            + (
                f"TRANSIT ALERT: High Stakes (Epitasis) enabled."
                if is_epitasis
                else "Flow is consistent with the annual cycle."
            ),
        }
        forecast.append(day_data)

    return forecast
