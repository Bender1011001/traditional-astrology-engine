"""Tests for decennials.py — Decennials Time-Lord system."""

from datetime import datetime, timezone
from unittest.mock import patch

from src.engine.decennials import DecennialEngine
from src.engine.models import Chart, Planet, PlanetName


def test_get_zodiacal_sequence():
    """Ensure traditional planets are sorted by longitude relative to Ascendant."""
    ascendant = 300.0  # Aquarius
    # Planets at various positions
    p_sun = Planet(name=PlanetName.SUN, longitude=310.0, speed=1.0)  # +10
    p_moon = Planet(name=PlanetName.MOON, longitude=10.0, speed=13.0)  # +70
    p_mars = Planet(name=PlanetName.MARS, longitude=200.0, speed=1.0)  # +260
    p_saturn = Planet(name=PlanetName.SATURN, longitude=350.0, speed=0.0)  # +50

    chart = Chart(
        sun_altitude=10.0,
        planets=[p_sun, p_moon, p_mars, p_saturn],
        ascendant=ascendant,
        mc=210.0,
    )

    sequence = DecennialEngine.get_zodiacal_sequence(chart)

    names = [p.name for p in sequence]
    # Order should be Sun(+10), Saturn(+50), Moon(+70), Mars(+260)
    assert names == [
        PlanetName.SUN,
        PlanetName.SATURN,
        PlanetName.MOON,
        PlanetName.MARS,
    ]


def test_select_apheta_sect_light():
    """Day chart, Sun in operative house."""
    # Day chart (Sun > 0)
    # Asc at 0 (Aries), Sun at 0 (Aries) -> 1st House (Operative)
    sun = Planet(name=PlanetName.SUN, longitude=0.0, speed=1.0)
    moon = Planet(name=PlanetName.MOON, longitude=180.0, speed=13.0)
    chart = Chart(
        sun_altitude=10.0,
        planets=[sun, moon],
        ascendant=0.0,
        mc=270.0,
        houses=[0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330],
    )

    apheta = DecennialEngine.select_apheta(chart)
    assert apheta.name == PlanetName.SUN


def test_select_apheta_contrary_light():
    """Day chart, Sun in 12th (Cadent/Non-operative), Moon in 1st (Operative)."""
    # Day chart
    # Asc at 0 (Aries).
    # Sun at 350.0 (Pisces) -> 12th House (Non-Operative, OPERATIVE_HOUSES = 1,10,11,7,5,9,4)
    # Moon at 0.0 (Aries) -> 1st House (Operative)
    sun = Planet(name=PlanetName.SUN, longitude=350.0, speed=1.0)
    moon = Planet(name=PlanetName.MOON, longitude=0.0, speed=13.0)
    chart = Chart(
        sun_altitude=10.0,
        planets=[sun, moon],
        ascendant=0.0,
        mc=270.0,
        houses=[0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330],
    )

    apheta = DecennialEngine.select_apheta(chart)
    assert apheta.name == PlanetName.MOON


def test_select_apheta_post_ascendant():
    """Both lights non-operative, falls back to first post-ascendant planet."""
    # Night chart
    # Asc at 0 (Aries)
    # Moon at 350 (Pisces, 12th)
    # Sun at 60 (Gemini, 3rd)
    # Mars at 30 (Taurus, 2nd) -> Wait, 2nd is not operative, but post-ascendant catches it!
    # Because sequence just takes zodiacal sort.
    sun = Planet(name=PlanetName.SUN, longitude=60.0, speed=1.0)
    moon = Planet(name=PlanetName.MOON, longitude=350.0, speed=13.0)
    mars = Planet(name=PlanetName.MARS, longitude=30.0, speed=1.0)

    chart = Chart(
        sun_altitude=-10.0,
        planets=[sun, moon, mars],
        ascendant=0.0,
        mc=270.0,
        houses=[0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330],
    )

    apheta = DecennialEngine.select_apheta(chart)
    assert apheta.name == PlanetName.MARS


@patch("src.engine.decennials.DecennialEngine.get_zodiacal_sequence")
@patch("src.engine.decennials.DecennialEngine.select_apheta")
def test_generate_decennials(mock_select_apheta, mock_zodiacal):
    """Generates proper nested decennials tree up to requested lifespan."""
    # Set up a fake chart and sequence
    sun = Planet(name=PlanetName.SUN, longitude=10.0, speed=1.0)
    moon = Planet(name=PlanetName.MOON, longitude=20.0, speed=13.0)
    mars = Planet(name=PlanetName.MARS, longitude=30.0, speed=1.0)
    jup = Planet(name=PlanetName.JUPITER, longitude=40.0, speed=1.0)
    ven = Planet(name=PlanetName.VENUS, longitude=50.0, speed=1.0)
    sat = Planet(name=PlanetName.SATURN, longitude=60.0, speed=0.0)
    mer = Planet(name=PlanetName.MERCURY, longitude=70.0, speed=1.0)

    chart = Chart(
        sun_altitude=10.0,
        planets=[sun, moon, mars, jup, ven, sat, mer],
        ascendant=0.0,
        mc=270.0,
    )
    mock_zodiacal.return_value = [sun, moon, mars, jup, ven, sat, mer]
    mock_select_apheta.return_value = sun

    start_dt = datetime(2000, 1, 1, 0, 0, tzinfo=timezone.utc)
    res = DecennialEngine.generate_decennials(chart, start_dt, lifespan_years=20)

    # 20 years implies at least 2 major periods of ~10.75 years.
    # (Because 10.75 * 2 = 21.5 >= 20)
    assert len(res) == 2
    assert res[0]["major_lord"] == "Sun"
    assert res[1]["major_lord"] == "Moon"

    # Sub periods total exactly 3870 days.
    assert len(res[0]["sub_periods"]) == 7
    assert res[0]["sub_periods"][0]["sub_lord"] == "Sun"

    # Sun minor years is 19. Sub-period should be 19 * 30 = 570 days.
    # Start date string parser -> check distance
    start = datetime.fromisoformat(res[0]["sub_periods"][0]["start_date"])
    end = datetime.fromisoformat(res[0]["sub_periods"][0]["end_date"])

    delta = end - start
    assert delta.days == 570
