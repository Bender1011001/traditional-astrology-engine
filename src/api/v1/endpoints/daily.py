"""
Daily Navigator API Endpoint — /api/v1/charts/daily-briefing

Given birth data, returns a synthesized daily prediction briefing that layers
profections, firdaria, zodiacal releasing, transits, epitasis, and recommendations.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

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
    """Reconstruct a Chart model from raw calculator output."""
    planets = []
    for pdata in raw.get("planets", []):
        try:
            name = PlanetName(pdata["name"])
        except (ValueError, KeyError):
            continue
        sign = None
        try:
            sign = Sign(pdata.get("sign", ""))
        except (ValueError, KeyError):
            pass
        planets.append(Planet(
            name=name,
            longitude=pdata.get("longitude", 0.0),
            latitude=pdata.get("latitude", 0.0),
            speed=pdata.get("speed", 0.0),
            sign=sign,
        ))

    asc = raw.get("angles", {}).get("Ascendant", 0.0)
    mc = raw.get("angles", {}).get("MC", 0.0)

    sun = next((p for p in planets if p.name == PlanetName.SUN), None)
    sun_alt = 1.0 if sun else 0.0
    if "meta" in raw:
        sun_alt_val = raw["meta"].get("sun_altitude")
        if sun_alt_val is not None:
            sun_alt = sun_alt_val

    houses = raw.get("houses", [])
    house_cusps = []
    if isinstance(houses, list):
        for h in houses:
            if isinstance(h, dict):
                house_cusps.append(h.get("cusp", 0.0))
            else:
                house_cusps.append(float(h))

    geo_lat = raw.get("meta", {}).get("lat", 0.0)
    geo_lon = raw.get("meta", {}).get("lon", 0.0)

    return Chart(
        planets=planets,
        ascendant=asc,
        mc=mc,
        house_cusps=house_cusps,
        sun_altitude=sun_alt,
        geo_lat=geo_lat,
        geo_lon=geo_lon,
        jd=raw.get("meta", {}).get("julian_day", 0.0),
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
        logger.error("Chart calculation failed for daily briefing: %s", e)
        raise HTTPException(status_code=500, detail=f"Chart calculation error: {str(e)}")

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
        raise HTTPException(status_code=500, detail=f"Prediction engine error: {str(e)}")

    return {
        "status": "success",
        "subject": data.name or "Native",
        "disclaimer": "Historical Use Only — not medical, financial, or legal advice.",
        "briefing": briefing,
    }
