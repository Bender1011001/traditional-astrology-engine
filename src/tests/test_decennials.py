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

    # Sub-periods total exactly 129 calendar months.
    assert len(res[0]["sub_periods"]) == 7
    assert res[0]["sub_periods"][0]["sub_lord"] == "Sun"

    # Sun's least years become 19 calendar months.
    start = datetime.fromisoformat(res[0]["sub_periods"][0]["start_date"])
    end = datetime.fromisoformat(res[0]["sub_periods"][0]["end_date"])
    assert start == datetime(2000, 1, 1, tzinfo=timezone.utc)
    assert end == datetime(2001, 8, 1, tzinfo=timezone.utc)
    assert res[0]["end_date"] == datetime(
        2010, 10, 1, tzinfo=timezone.utc
    ).isoformat()
    assert res[0]["sub_periods"][-1]["end_date"] == res[0]["end_date"]


def test_decennial_cycle_repeats_from_apheta_after_seven_major_periods():
    planets = [
        Planet(name=name, longitude=float(index * 30), speed=1.0)
        for index, name in enumerate(
            (
                PlanetName.SUN,
                PlanetName.MOON,
                PlanetName.MARS,
                PlanetName.JUPITER,
                PlanetName.VENUS,
                PlanetName.SATURN,
                PlanetName.MERCURY,
            )
        )
    ]
    chart = Chart(sun_altitude=10.0, planets=planets, ascendant=0.0)
    result = DecennialEngine.generate_decennials(
        chart, datetime(2000, 1, 1), lifespan_years=90
    )
    assert result[0]["major_lord"] == "Sun"
    assert result[7]["major_lord"] == "Sun"


def _regression_chart():
    planets = [
        Planet(name=name, longitude=float(index * 30), speed=1.0)
        for index, name in enumerate(
            (
                PlanetName.SUN,
                PlanetName.MOON,
                PlanetName.MARS,
                PlanetName.JUPITER,
                PlanetName.VENUS,
                PlanetName.SATURN,
                PlanetName.MERCURY,
            )
        )
    ]
    return Chart(sun_altitude=10.0, planets=planets, ascendant=0.0)


def test_decennials_leap_day_birth_keeps_129_month_invariant():
    """Regression: a Feb 29 birth must not break the 129-month invariant.

    Chaining month additions from a clamped Feb 28/30 date used to drift the
    anchor day and raise ValueError, which aborted the entire nativity.
    """
    from datetime import datetime, timezone

    chart = _regression_chart()
    start = datetime(1988, 2, 29, 23, 45, tzinfo=timezone.utc)
    periods = DecennialEngine.generate_decennials(chart, start)
    assert periods, "leap-day birth must produce decennial periods"
    for major in periods:
        assert major["duration_months"] == 129
        assert major["sub_periods"][0]["start_date"] == major["start_date"]
        assert major["sub_periods"][-1]["end_date"] == major["end_date"]


def test_decennials_day31_birth_keeps_129_month_invariant():
    from datetime import datetime, timezone

    chart = _regression_chart()
    start = datetime(1990, 1, 31, 12, 0, tzinfo=timezone.utc)
    periods = DecennialEngine.generate_decennials(chart, start)
    for major in periods:
        assert major["sub_periods"][-1]["end_date"] == major["end_date"]
