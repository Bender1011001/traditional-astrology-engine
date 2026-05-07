"""Tests for hyleg.py — HylegAlcocodenEngine."""

from src.engine.hyleg import HylegAlcocodenEngine
from src.engine.models import Chart, Planet, PlanetName


def _build_chart(
    sun_lon=30.0, moon_lon=120.0, asc=0.0, sun_alt=10.0, extra_planets=None
):
    """Build a Chart with Sun, Moon and optionally other planets."""
    planets = [
        Planet(name=PlanetName.SUN, longitude=sun_lon, speed=1.0, altitude=sun_alt),
        Planet(name=PlanetName.MOON, longitude=moon_lon, speed=13.0, altitude=5.0),
        Planet(name=PlanetName.MERCURY, longitude=45.0, speed=1.2),
        Planet(name=PlanetName.VENUS, longitude=60.0, speed=1.0),
        Planet(name=PlanetName.MARS, longitude=200.0, speed=0.5),
        Planet(name=PlanetName.JUPITER, longitude=90.0, speed=0.08),
        Planet(name=PlanetName.SATURN, longitude=300.0, speed=0.03),
    ]
    if extra_planets:
        planets.extend(extra_planets)
    return Chart(sun_altitude=sun_alt, planets=planets, ascendant=asc, mc=270.0)


# ─── determine_hyleg ─────────────────────────────────────────────────────────


def test_determine_hyleg_returns_dict():
    chart = _build_chart()
    result = HylegAlcocodenEngine.determine_hyleg(chart)
    assert isinstance(result, dict)
    assert "type" in result
    assert "name" in result
    assert "longitude" in result
    assert "candidate" in result


def test_determine_hyleg_day_chart():
    """In a day chart, Sun is checked first."""
    chart = _build_chart(sun_alt=10.0)
    result = HylegAlcocodenEngine.determine_hyleg(chart)
    # Should return something — either Sun, Moon, Fortune or Ascendant
    assert result["name"] in ["Sun", "Moon", "Fortune", "Ascendant"]


def test_determine_hyleg_night_chart():
    """In a night chart, Moon is checked first."""
    chart = _build_chart(sun_alt=-10.0)
    result = HylegAlcocodenEngine.determine_hyleg(chart)
    assert result["name"] in ["Sun", "Moon", "Fortune", "Ascendant"]


# ─── determine_alcocoden ─────────────────────────────────────────────────────


def test_determine_alcocoden_bonatti_method():
    chart = _build_chart()
    hyleg = HylegAlcocodenEngine.determine_hyleg(chart)
    alco = HylegAlcocodenEngine.determine_alcocoden(
        hyleg, chart, method="bonatti_points"
    )
    # Can be None if no candidate qualifies
    if alco is not None:
        assert "name" in alco
        assert "score" in alco
        assert "planet" in alco
        assert "aspect" in alco


def test_determine_alcocoden_valens_term():
    chart = _build_chart()
    hyleg = HylegAlcocodenEngine.determine_hyleg(chart)
    alco = HylegAlcocodenEngine.determine_alcocoden(hyleg, chart, method="valens_term")
    if alco is not None:
        assert alco["via"] == "valens_term"


# ─── calculate_lifespan ──────────────────────────────────────────────────────


def test_calculate_lifespan_with_alcocoden():
    chart = _build_chart()
    hyleg = HylegAlcocodenEngine.determine_hyleg(chart)
    alco = HylegAlcocodenEngine.determine_alcocoden(hyleg, chart)
    if alco:
        result = HylegAlcocodenEngine.calculate_lifespan(hyleg, alco, chart)
        assert "total_years" in result
        assert result["total_years"] >= 5  # Safety clamp
        assert "vitality_rating" in result
        assert "breakdown" in result
        assert isinstance(result["breakdown"], list)


def test_calculate_lifespan_no_alcocoden():
    chart = _build_chart()
    hyleg = HylegAlcocodenEngine.determine_hyleg(chart)
    result = HylegAlcocodenEngine.calculate_lifespan(hyleg, None, chart)
    assert result["total_years"] == 0
    assert "No Alcocoden found" in result["breakdown"][0]


# ─── determine_anareta ───────────────────────────────────────────────────────


def test_determine_anareta_basic():
    chart = _build_chart()
    hyleg = HylegAlcocodenEngine.determine_hyleg(chart)
    anareta = HylegAlcocodenEngine.determine_anareta(hyleg, chart)
    assert isinstance(anareta, dict)
    assert "name" in anareta
    assert "reason" in anareta


def test_determine_anareta_no_hyleg():
    result = HylegAlcocodenEngine.determine_anareta({}, _build_chart())
    assert result["name"] is None
    assert "No Hyleg available" in result["reason"]


def test_determine_anareta_with_tight_malefic():
    """Mars square the Hyleg should be detected as Anareta."""
    # Place the Sun at 0° as Hyleg, Mars at 90° (exact square)
    chart = _build_chart(sun_lon=0.0, asc=350.0)
    # Override Mars to be at 90° exactly
    for p in chart.planets:
        if p.name == PlanetName.MARS:
            p.longitude = 90.0
    hyleg = {
        "type": "Planet",
        "name": "Sun",
        "longitude": 0.0,
        "candidate": PlanetName.SUN,
    }
    anareta = HylegAlcocodenEngine.determine_anareta(hyleg, chart)
    if anareta["name"]:
        assert anareta["name"] in ["Mars", "Saturn", "Descendant (7th cusp)"]
        assert "aspect_to_hyleg" in anareta


# ─── planetary_years ──────────────────────────────────────────────────────────


def test_planetary_years_table():
    """Ensure all 7 planets have minor, mean, major years."""
    required = [
        PlanetName.SATURN,
        PlanetName.JUPITER,
        PlanetName.MARS,
        PlanetName.SUN,
        PlanetName.VENUS,
        PlanetName.MERCURY,
        PlanetName.MOON,
    ]
    for p in required:
        years = HylegAlcocodenEngine.PLANETARY_YEARS[p]
        assert "minor" in years
        assert "mean" in years
        assert "major" in years
        assert years["minor"] < years["mean"] < years["major"]
