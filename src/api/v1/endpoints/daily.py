"""
Daily & Weekly Navigator API Endpoints

  /api/v1/charts/daily-briefing  — single-day synthesized prediction
  /api/v1/charts/weekly-briefing — 7-day look-ahead with week-overview highlights

Given birth data, these endpoints layer profections, firdaria, zodiacal releasing,
transits, epitasis, moon condition, and recommendations.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.services.engine_bridge import calculate_chart_async
from src.engine.daily_navigator import DailyNavigator
from src.engine.models import Chart, Planet, PlanetName, Sign

logger = logging.getLogger(__name__)

router = APIRouter()


class DailyBriefingRequest(BaseModel):
    date: str          # Birth date YYYY-MM-DD
    time: str          # Birth time HH:MM
    city: str
    state: Optional[str] = ""
    name: Optional[str] = "Native"
    target_date: Optional[str] = None  # Date to predict for (default: today)
    house_system: Optional[str] = "W"
    zodiac_system: Optional[str] = "tropical"
    node_type: str = "mean"


def _rebuild_chart_model(raw: dict) -> Chart:
    """Reconstruct a Chart model from raw calculator output.

    Handles both formats:
      - dict: {"Sun": {"longitude": ..., "sign": ...}, ...}  (from calculate_chart_data)
      - list: [{"name": "Sun", "longitude": ..., "sign": ...}, ...]  (from ForensicEngine)
    """
    planets = []
    raw_planets = raw.get("planets", [])

    # Normalize to list of (name_str, data_dict) tuples
    if isinstance(raw_planets, dict):
        planet_items = [(name, data) for name, data in raw_planets.items() if isinstance(data, dict)]
    elif isinstance(raw_planets, list):
        planet_items = [(p.get("name", ""), p) for p in raw_planets if isinstance(p, dict)]
    else:
        planet_items = []

    for name_str, pdata in planet_items:
        try:
            name = PlanetName(name_str)
        except (ValueError, KeyError):
            continue
        # Note: Planet.sign is a computed @property from longitude, not a constructor arg
        planets.append(Planet(
            name=name,
            longitude=pdata.get("longitude", 0.0),
            latitude=pdata.get("latitude", 0.0),
            speed=pdata.get("speed", 0.0),
        ))

    asc = raw.get("angles", {}).get("Ascendant", 0.0)
    mc = raw.get("angles", {}).get("MC", 0.0)

    sun = next((p for p in planets if p.name == PlanetName.SUN), None)
    sun_alt = 1.0 if sun else 0.0
    if "meta" in raw:
        sun_alt_val = raw["meta"].get("sun_altitude")
        if sun_alt_val is not None:
            sun_alt = sun_alt_val

    # Build houses dict {1: cusp, 2: cusp, ...}
    raw_houses = raw.get("houses", {})
    houses_dict: Optional[Dict[int, float]] = None
    if isinstance(raw_houses, dict):
        houses_dict = {int(k): float(v) for k, v in raw_houses.items() if isinstance(v, (int, float))}
    elif isinstance(raw_houses, list):
        houses_dict = {}
        for idx, h in enumerate(raw_houses, start=1):
            if isinstance(h, dict):
                houses_dict[idx] = h.get("cusp", 0.0)
            else:
                houses_dict[idx] = float(h)

    geo_lat = raw.get("meta", {}).get("lat", 0.0)
    geo_lon = raw.get("meta", {}).get("lon", 0.0)

    return Chart(
        sun_altitude=sun_alt,
        planets=planets,
        ascendant=asc,
        mc=mc,
        geo_lat=geo_lat,
        geo_lon=geo_lon,
        jd=raw.get("meta", {}).get("julian_day", 0.0),
        houses=houses_dict,
    )


@router.post("/daily-briefing")
async def daily_briefing(data: DailyBriefingRequest):
    """
    Generate a daily prediction briefing based on birth data and a target date.

    Layers all traditional timing techniques:
    - Annual/Monthly/Daily Profections
    - Firdaria (Major + Sub Period)
    - Zodiacal Releasing (Lot of Spirit)
    - Venus, Mars, Jupiter & Saturn transits to natal septener
    - Moon condition (phase, sign, void of course)
    - Epitasis detection
    - Planetary day alignment
    - Actionable recommendations (propitiation, color, gem, charity)

    Historical Use Only — not medical, financial, or legal advice.
    """
    # 1. Calculate the natal chart
    try:
        raw_chart = await calculate_chart_async(
            date_str=data.date,
            time_str=data.time,
            city=data.city,
            state=data.state or "",
            house_system=data.house_system or "W",
            zodiac_system=data.zodiac_system or "tropical",
            node_type=data.node_type,
        )
    except Exception as e:
        logger.error("Chart calculation failed for daily briefing: %s", repr(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Chart calculation error. Please verify your input.")

    if "error" in raw_chart:
        raise HTTPException(status_code=400, detail=raw_chart["error"])

    # 2. Rebuild Chart model
    chart = _rebuild_chart_model(raw_chart)

    # 3. Parse birth datetime from raw_chart meta
    birth_dt = None
    utc_time_str = raw_chart.get("meta", {}).get("utc_time")
    if utc_time_str:
        try:
            birth_dt = datetime.fromisoformat(utc_time_str.replace("Z", "+00:00"))
            if birth_dt.tzinfo:
                birth_dt = birth_dt.replace(tzinfo=None)
        except (ValueError, TypeError):
            pass

    if birth_dt is None:
        raise HTTPException(status_code=400, detail="Could not resolve UTC birth time.")

    birth_jd = raw_chart.get("meta", {}).get("julian_day", 0.0)

    # 4. Resolve target date
    if data.target_date:
        try:
            target_dt = datetime.strptime(data.target_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="target_date must be YYYY-MM-DD format.")
    else:
        target_dt = datetime.now(timezone.utc).replace(tzinfo=None)

    # 5. Generate the briefing
    try:
        briefing = DailyNavigator.generate_briefing(
            chart=chart,
            birth_dt=birth_dt,
            birth_jd=birth_jd,
            target_date=target_dt,
        )
    except Exception as e:
        logger.exception("DailyNavigator failed: %s", e)
        raise HTTPException(status_code=500, detail="Prediction engine error. Please try again.")

    return {
        "status": "success",
        "subject": data.name or "Native",
        "disclaimer": "Historical Use Only — not medical, financial, or legal advice.",
        "briefing": briefing,
    }


# ─────────────────────────────────────────────────────────────────────────────
# WEEKLY BRIEFING — 7-day look-ahead
# ─────────────────────────────────────────────────────────────────────────────

class WeeklyBriefingRequest(BaseModel):
    date: str          # Birth date YYYY-MM-DD
    time: str          # Birth time HH:MM
    city: str
    state: Optional[str] = ""
    name: Optional[str] = "Native"
    start_date: Optional[str] = None  # First day of the week (default: today)
    days: int = 7                     # Number of days (1-14, default 7)
    house_system: Optional[str] = "W"
    zodiac_system: Optional[str] = "tropical"
    node_type: str = "mean"


def _synthesize_week_overview(days_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze 7 daily briefings and produce a week-level summary.

    Highlights:
      - Days with active epitasis (peak windows)
      - Days with Moon void of course (caution windows)
      - Highest-urgency days
      - Transit cluster summary (most active transit days)
      - Best and worst days at a glance
    """
    epitasis_days: List[str] = []
    voc_days: List[str] = []
    high_urgency_days: List[str] = []
    transit_counts: List[Dict[str, Any]] = []
    challenging_transit_days: List[str] = []

    for day in days_data:
        briefing = day.get("briefing", {})
        display = briefing.get("display_date", briefing.get("date", "?"))
        date_str = briefing.get("date", "?")

        # Epitasis
        if briefing.get("epitasis", {}).get("active"):
            epitasis_days.append(display)

        # Moon VoC
        if briefing.get("moon", {}).get("void_of_course"):
            voc_days.append(display)

        # Urgency
        urgency = briefing.get("recommendations", {}).get("urgency", "low")
        if urgency == "high":
            high_urgency_days.append(display)

        # Transit volume & quality
        transits = briefing.get("transits", [])
        n_challenging = sum(1 for t in transits if t.get("quality") == "challenging")
        n_supportive = sum(1 for t in transits if t.get("quality") == "supportive")
        transit_counts.append({
            "date": date_str,
            "display": display,
            "total": len(transits),
            "supportive": n_supportive,
            "challenging": n_challenging,
        })
        if n_challenging >= 2:
            challenging_transit_days.append(display)

    # Determine best and most cautious days
    best_day = None
    worst_day = None
    best_score = -999
    worst_score = 999

    for tc in transit_counts:
        score = tc["supportive"] - tc["challenging"]
        if score > best_score:
            best_score = score
            best_day = tc["display"]
        if score < worst_score:
            worst_score = score
            worst_day = tc["display"]

    # Build summary paragraph
    parts = []
    if epitasis_days:
        parts.append(
            f"⚡ **Epitasis active** on {', '.join(epitasis_days)} — "
            "events related to your Lord of the Year peak on these days."
        )
    if voc_days:
        parts.append(
            f"🌙 **Moon Void of Course** on {', '.join(voc_days)} — "
            "avoid starting new ventures on these days."
        )
    if challenging_transit_days:
        parts.append(
            f"⚠️ **Heavy transit days**: {', '.join(challenging_transit_days)} — "
            "multiple challenging aspects active. Proceed with patience."
        )
    if best_day:
        parts.append(f"✅ **Best day this week**: {best_day} (most supportive transits).")
    if worst_day and worst_day != best_day:
        parts.append(f"🛑 **Most cautious day**: {worst_day} (most challenging aspects).")

    if not parts:
        parts.append("A relatively steady week with no major peaks or caution windows.")

    return {
        "summary": "\n\n".join(parts),
        "epitasis_days": epitasis_days,
        "void_of_course_days": voc_days,
        "high_urgency_days": high_urgency_days,
        "challenging_transit_days": challenging_transit_days,
        "best_day": best_day,
        "most_cautious_day": worst_day,
        "transit_heatmap": transit_counts,
    }


@router.post("/weekly-briefing")
async def weekly_briefing(data: WeeklyBriefingRequest):
    """
    Generate a multi-day prediction briefing (default: 7 days).

    Returns individual daily briefings plus a week-overview summary that
    highlights epitasis windows, void-of-course days, transit clusters,
    and the best/worst days at a glance.

    Historical Use Only — not medical, financial, or legal advice.
    """
    # Clamp days to a sane range
    num_days = max(1, min(data.days, 14))

    # 1. Calculate the natal chart (once)
    try:
        raw_chart = await calculate_chart_async(
            date_str=data.date,
            time_str=data.time,
            city=data.city,
            state=data.state or "",
            house_system=data.house_system or "W",
            zodiac_system=data.zodiac_system or "tropical",
            node_type=data.node_type,
        )
    except Exception as e:
        logger.error("Chart calculation failed for weekly briefing: %s", repr(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Chart calculation error. Please verify your input.")

    if "error" in raw_chart:
        raise HTTPException(status_code=400, detail=raw_chart["error"])

    # 2. Rebuild Chart model
    chart = _rebuild_chart_model(raw_chart)

    # 3. Parse birth datetime
    birth_dt = None
    utc_time_str = raw_chart.get("meta", {}).get("utc_time")
    if utc_time_str:
        try:
            birth_dt = datetime.fromisoformat(utc_time_str.replace("Z", "+00:00"))
            if birth_dt.tzinfo:
                birth_dt = birth_dt.replace(tzinfo=None)
        except (ValueError, TypeError):
            pass

    if birth_dt is None:
        raise HTTPException(status_code=400, detail="Could not resolve UTC birth time.")

    birth_jd = raw_chart.get("meta", {}).get("julian_day", 0.0)

    # 4. Resolve start date
    if data.start_date:
        try:
            start_dt = datetime.strptime(data.start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="start_date must be YYYY-MM-DD format.")
    else:
        start_dt = datetime.now(timezone.utc).replace(tzinfo=None, hour=0, minute=0, second=0, microsecond=0)

    # 5. Generate briefings for each day
    days_output: List[Dict[str, Any]] = []
    for offset in range(num_days):
        target_dt = start_dt + timedelta(days=offset)
        try:
            briefing = DailyNavigator.generate_briefing(
                chart=chart,
                birth_dt=birth_dt,
                birth_jd=birth_jd,
                target_date=target_dt,
            )
            days_output.append({
                "day_index": offset,
                "briefing": briefing,
            })
        except Exception as e:
            logger.warning("DailyNavigator failed for day %d (%s): %s", offset, target_dt, e)
            days_output.append({
                "day_index": offset,
                "briefing": {"date": target_dt.strftime("%Y-%m-%d"), "error": str(e)},
            })

    # 6. Synthesize week overview
    week_overview = _synthesize_week_overview(days_output)

    return {
        "status": "success",
        "subject": data.name or "Native",
        "start_date": start_dt.strftime("%Y-%m-%d"),
        "num_days": num_days,
        "disclaimer": "Historical Use Only — not medical, financial, or legal advice.",
        "week_overview": week_overview,
        "days": days_output,
    }
