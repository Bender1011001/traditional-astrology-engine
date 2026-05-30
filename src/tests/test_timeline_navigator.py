from datetime import datetime

import pytest

from src.engine.models import Chart, Planet, PlanetName
from src.engine.timeline_navigator import (
    generate_timeline,
    rebuild_chart_from_raw,
    resolve_birth_datetime,
)


def _chart() -> Chart:
    return Chart(
        planets=[
            Planet(name=PlanetName.SUN, longitude=140.5, speed=0.95),
            Planet(name=PlanetName.MOON, longitude=82.2, speed=12.5),
            Planet(name=PlanetName.MERCURY, longitude=162.0, speed=1.2),
            Planet(name=PlanetName.VENUS, longitude=118.5, speed=1.1),
            Planet(name=PlanetName.MARS, longitude=99.0, speed=0.6),
            Planet(name=PlanetName.JUPITER, longitude=285.3, speed=0.12),
            Planet(name=PlanetName.SATURN, longitude=5.7, speed=0.05),
        ],
        ascendant=154.0,
        mc=70.0,
        sun_altitude=10.0,
        geo_lat=38.25,
        geo_lon=-122.04,
        jd=2450310.0958,
        houses={i: ((154.0 + (i - 1) * 30.0) % 360.0) for i in range(1, 13)},
    )


def test_generate_timeline_returns_real_frames_and_scores():
    payload = generate_timeline(
        chart=_chart(),
        birth_dt=datetime(1996, 8, 13, 14, 18),
        birth_jd=2450310.0958,
        start=datetime(2026, 5, 17, 0, 0),
        end=datetime(2026, 5, 19, 0, 0),
        step_hours=24,
        intent="launch",
    )

    assert payload["range"]["frame_count"] == 3
    assert payload["natal"]["sect"] == "Day"
    assert len(payload["natal"]["planets"]) == 7
    assert len(payload["frames"]) == 3
    assert payload["frames"][0]["display"] == "2026-05-17 00:00 UTC"

    first = payload["frames"][0]
    assert len(first["transits"]) == 7
    assert {planet["name"] for planet in first["transits"]} == {
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
    }
    assert 0 <= first["score"] <= 100
    assert first["tone"] in {"supportive", "constructive", "mixed", "caution", "heavy"}
    assert first["reasons"]
    assert first["moon"]["sign"]


def test_generate_timeline_rejects_oversized_ranges():
    with pytest.raises(ValueError, match="exceed"):
        generate_timeline(
            chart=_chart(),
            birth_dt=datetime(1996, 8, 13, 14, 18),
            birth_jd=2450310.0958,
            start=datetime(2026, 1, 1),
            end=datetime(2026, 3, 1),
            step_hours=1,
            intent="general",
        )


def test_rebuild_chart_from_raw_preserves_natal_anchor():
    raw = {
        "planets": {
            "Sun": {
                "longitude": 140.5,
                "latitude": 0.0,
                "speed": 0.95,
                "altitude": 10.0,
            },
            "Moon": {"longitude": 82.2, "latitude": 1.0, "speed": 12.5},
        },
        "angles": {"Ascendant": 154.0, "MC": 70.0},
        "houses": {"1": 154.0, "2": 184.0},
        "meta": {
            "sun_altitude": 10.0,
            "lat": 38.25,
            "lon": -122.04,
            "julian_day": 2450310.0958,
            "utc_time": "1996-08-13T14:18:00+00:00",
        },
    }

    chart = rebuild_chart_from_raw(raw)
    birth_dt = resolve_birth_datetime(raw)

    assert chart.ascendant == 154.0
    assert chart.sun_altitude == 10.0
    assert chart.houses == {1: 154.0, 2: 184.0}
    assert [planet.name for planet in chart.planets] == [PlanetName.SUN, PlanetName.MOON]
    assert birth_dt == datetime(1996, 8, 13, 14, 18)
