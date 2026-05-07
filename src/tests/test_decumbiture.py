"""Tests for decumbiture.py — Critical Days, Prognosis, and Distempers."""

from unittest.mock import patch

from src.engine.decumbiture import DecumbitureEngine
from src.engine.models import Chart, Planet, PlanetName, Sign


def test_analyze_distemper():
    """Sign-based humoral imbalances."""
    res = DecumbitureEngine.analyze_distemper(Sign.ARIES)
    assert res["element"] == "Fire"
    assert "Choleric" in res["excess_humor"]

    res = DecumbitureEngine.analyze_distemper(Sign.CAPRICORN)
    assert res["element"] == "Earth"
    assert "Melancholic" in res["excess_humor"]

    res = DecumbitureEngine.analyze_distemper(Sign.AQUARIUS)
    assert res["element"] == "Air"
    assert "Sanguine" in res["excess_humor"]

    res = DecumbitureEngine.analyze_distemper(Sign.CANCER)
    assert res["element"] == "Water"
    assert "Phlegmatic" in res["excess_humor"]


@patch("src.engine.hyleg.HylegAlcocodenEngine.determine_hyleg")
def test_analyze_natal_constitution(mock_get_hyleg):
    """Vitality ratings based on Ascendant and Hyleg presence."""
    chart = Chart(
        sun_altitude=10.0, planets=[], ascendant=0.0, mc=270.0
    )  # 0.0 is Aries
    mock_get_hyleg.return_value = {"name": "Sun", "strength": "Strong"}

    res = DecumbitureEngine.analyze_natal_constitution(chart)
    assert res["baseline_distemper"]["element"] == "Fire"
    assert res["vitality_rating"] == "Stable"
    assert res["hyleg_found"] == "Sun"


@patch("src.engine.hyleg.HylegAlcocodenEngine.determine_hyleg")
def test_analyze_natal_constitution_delicate(mock_get_hyleg):
    """If no Hyleg is found, vitality is Delicate."""
    chart = Chart(sun_altitude=10.0, planets=[], ascendant=0.0, mc=270.0)
    mock_get_hyleg.return_value = None

    res = DecumbitureEngine.analyze_natal_constitution(chart)
    assert "Delicate" in res["vitality_rating"]


def test_get_contra_indications():
    """Rules against purging in head/throat signs or Saturn cold operations."""
    moon_aries = Planet(name=PlanetName.MOON, longitude=10.0, speed=13.0)
    chart = Chart(sun_altitude=10.0, planets=[moon_aries], ascendant=0.0, mc=270.0)

    warnings = DecumbitureEngine.get_contra_indications(chart)
    assert any("avoid emetics or purging" in w.lower() for w in warnings)

    saturn = Planet(name=PlanetName.SATURN, longitude=13.0, speed=0.0)
    chart_afflicted = Chart(
        sun_altitude=10.0, planets=[moon_aries, saturn], ascendant=0.0, mc=270.0
    )
    warnings_aff = DecumbitureEngine.get_contra_indications(chart_afflicted)
    assert any("saturn afflicting moon" in w.lower() for w in warnings_aff)


def test_check_prognosis_good():
    """Prognosis should be Good/Neutral if there are no major afflictions."""
    p1 = Planet(name=PlanetName.MARS, longitude=100.0, speed=1.0)
    p2 = Planet(name=PlanetName.MOON, longitude=200.0, speed=13.0)
    chart = Chart(sun_altitude=10.0, planets=[p1, p2], ascendant=0.0, mc=270.0)

    res = DecumbitureEngine.check_prognosis(chart)
    assert res["status"] in ["Neutral", "Good"]
    assert len(res["indicators"]) == 0


def test_check_prognosis_bad():
    """Prognosis should be Critically Guarded if multiple heavy afflictions happen."""
    p1 = Planet(name=PlanetName.MARS, longitude=10.0, speed=1.0)
    sun = Planet(
        name=PlanetName.SUN, longitude=12.0, speed=1.0
    )  # Asc ruler combust (2 deg orb)
    moon = Planet(name=PlanetName.MOON, longitude=100.0, speed=13.0)
    mars = Planet(
        name=PlanetName.MARS, longitude=102.0, speed=1.0
    )  # Moon conjunct Mars
    saturn = Planet(
        name=PlanetName.SATURN, longitude=104.0, speed=0.0
    )  # Moon conjunct Saturn too!

    chart = Chart(
        sun_altitude=10.0,
        planets=[p1, sun, moon, mars, saturn],
        ascendant=0.0,
        mc=270.0,
    )
    res = DecumbitureEngine.check_prognosis(chart)

    assert res["score"] < -4
    assert res["status"] == "Critically Guarded"
    assert any("combust" in n.lower() for n in res["indicators"])


@patch("swisseph.calc_ut")
@patch("swisseph.revjul")
def test_calculate_critical_days(mock_revjul, mock_calc):
    """Testing Newton approximation wrapper for Lunar critical crises."""
    # Start Moon at 0 degrees Aries.
    # When iterating, let's just make the Moon travel exactly as requested.
    # Because `calculate_critical_days` dynamically asks swisseph for Moon,
    # we need a deterministic dynamic mock. By passing back:
    # (jd - start_jd) * 13.176 + 0.0

    start_jd = 2460000.0

    def dynamic_moon(jd, body, flags):
        diff_days = jd - start_jd
        # Simple linear progression over 360 deg
        lon = (diff_days * 13.176) % 360.0
        return ([lon, 0, 1, 13.176, 0, 0], 0)

    mock_calc.side_effect = dynamic_moon
    mock_revjul.return_value = (2023, 1, 1, 12.0)

    days = DecumbitureEngine.calculate_critical_days(start_jd)

    # 6 critical phases anticipated
    assert len(days) == 6
    labels = [d["label"] for d in days]
    assert "Indication (Semi-Square)" in labels
    assert "First Crisis (Square)" in labels
    assert "Full Crisis (Opposition)" in labels

    # Check that Full Crisis lands approx day ~13.6
    opposition = next(d for d in days if d["label"] == "Full Crisis (Opposition)")
    assert 13.0 < opposition["days_from_onset"] < 14.5
