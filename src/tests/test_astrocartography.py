import math
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from src.app import app
from src.engine.astrocartography import (
    generate_astrocartography_map,
)


def _normalize_lon(value: float) -> float:
    return ((value + 180.0) % 360.0) - 180.0


def test_astrocartography_generates_real_angular_lines():
    data = generate_astrocartography_map(
        name="Map Native",
        date_str="1996-08-13",
        time_str="07:18",
        city="Fairfield",
        state="CA",
        latitude=38.2493581,
        longitude=-122.039966,
        intent="business",
        target_locations=[
            {"name": "New York", "latitude": 40.7128, "longitude": -74.0060}
        ],
    )

    assert data["status"] == "ok"
    assert data["intent"]["key"] == "business"
    assert data["chart"]["sect"] in {"DAY", "NIGHT"}
    assert "not relocation" in data["disclaimer"]

    lines = data["lines"]
    assert len(lines) >= 28
    assert {line["angle"] for line in lines} == {"MC", "IC", "ASC", "DSC"}
    assert {line["planet"] for line in lines} >= {
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
    }
    assert data["ranked_lines"][0]["score"] >= data["ranked_lines"][-1]["score"]
    assert data["target_locations"][0]["closest_symbolic_lines"]


def test_mc_ic_and_asc_lines_match_sidereal_geometry():
    data = generate_astrocartography_map(
        name="Geometry Native",
        date_str="1996-08-13",
        time_str="07:18",
        city="Fairfield",
        state="CA",
        latitude=38.2493581,
        longitude=-122.039966,
        planets=["Sun"],
    )

    gst = float(data["map"]["greenwich_sidereal_deg"])
    sun_mc = next(line for line in data["lines"] if line["id"] == "sun_mc")
    sun_ic = next(line for line in data["lines"] if line["id"] == "sun_ic")
    sun_asc = next(line for line in data["lines"] if line["id"] == "sun_asc")

    mc_lon = sun_mc["segments"][0][0]["lon"]
    ic_lon = sun_ic["segments"][0][0]["lon"]
    ra = float(sun_mc["right_ascension_deg"])
    dec = math.radians(float(sun_asc["declination_deg"]))

    assert abs(_normalize_lon((ra - gst) - mc_lon)) < 0.01
    assert abs(_normalize_lon((ra + 180.0 - gst) - ic_lon)) < 0.01

    asc_point = sun_asc["segments"][0][len(sun_asc["segments"][0]) // 2]
    lat = math.radians(float(asc_point["lat"]))
    hour_angle = math.radians(_normalize_lon(gst + float(asc_point["lon"]) - ra))
    horizon_value = (
        math.sin(lat) * math.sin(dec)
        + math.cos(lat) * math.cos(dec) * math.cos(hour_angle)
    )
    assert abs(horizon_value) < 1e-4


@pytest.mark.asyncio
async def test_astrocartography_endpoint_returns_map_payload():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True
    ) as ac:
        response = await ac.post(
            "/api/v1/astrocartography/map",
            json={
                "name": "Endpoint Native",
                "date": "1996-08-13",
                "time": "07:18",
                "city": "Fairfield",
                "state": "CA",
                "latitude": 38.2493581,
                "longitude": -122.039966,
                "time_unknown": True,
                "intent": "career",
                "planets": ["Sun", "Jupiter", "Uranus", "Neptune", "Pluto"],
                "target_locations": [
                    {"name": "London", "latitude": 51.5072, "longitude": -0.1276}
                ],
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["chart"]["time_confidence"] == "low_noon_placeholder"
    assert data["intent"]["key"] == "career"
    assert {line["planet"] for line in data["lines"]} == {"Sun", "Jupiter"}
    assert {line["planet"] for line in data["lines"]}.isdisjoint({"Uranus", "Neptune", "Pluto"})
    assert {line["stroke"] for line in data["lines"]} == {"solid", "dashed", "dotted", "dash-dot"}
    assert data["target_locations"][0]["name"] == "London"


def test_frontend_assets_reference_astrocartography_renderer():
    root = Path(__file__).resolve().parents[1] / "static"
    reading_app = (root / "js" / "reading-app.js").read_text(encoding="utf-8")
    sw = (root / "sw.js").read_text(encoding="utf-8")
    index = (root / "index.html").read_text(encoding="utf-8")

    assert "renderAstrocartographyMap" in reading_app
    assert "/js/astrocartography-map.js" in sw
    assert "rev20260816convert1" in index
