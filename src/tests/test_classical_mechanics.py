"""Tests for classical_mechanics.py — Antiscia, Dodecatemoria, and Planetary Hours."""

from datetime import datetime, timezone
from unittest.mock import patch

from src.engine.classical_mechanics import (ClassicalMechanicsEngine,
                                            calculate_antiscia_points,
                                            calculate_dodecatemorion,
                                            calculate_planetary_hours,
                                            check_antiscia_aspect,
                                            get_egyptian_term_ruler,
                                            get_sign_from_lon, normalize_deg)
from src.engine.models import Planet, PlanetName, Sign

# ─── 1. ANTISCIA & CONTRA-ANTISCIA ──────────────────────────────────────────


def test_normalize_deg():
    assert normalize_deg(370.0) == 10.0
    assert abs(normalize_deg(-10.0) - 350.0) < 0.01


def test_get_sign_from_lon():
    assert get_sign_from_lon(10.0) == Sign.ARIES
    assert get_sign_from_lon(100.0) == Sign.CANCER
    assert get_sign_from_lon(359.0) == Sign.PISCES


def test_antiscia_points_aries():
    """10° Aries (10.0) -> Antiscia is 20° Virgo (170.0), Contra is 20° Pisces (350.0)."""
    pt = calculate_antiscia_points(10.0)
    assert pt.original_lon == 10.0
    assert pt.antiscia_lon == 170.0
    assert pt.antiscia_sign == Sign.VIRGO
    assert pt.contra_antiscia_lon == 350.0
    assert pt.contra_antiscia_sign == Sign.PISCES


def test_antiscia_points_cancer():
    """10° Cancer (100.0) -> Antiscia is 20° Gemini (80.0), Contra is 20° Sagittarius (260.0)."""
    pt = calculate_antiscia_points(100.0)
    assert pt.antiscia_lon == 80.0
    assert pt.antiscia_sign == Sign.GEMINI
    assert pt.contra_antiscia_lon == 260.0
    assert pt.contra_antiscia_sign == Sign.SAGITTARIUS


def test_check_antiscia_aspect_exact():
    """Planet 2 exactly on Planet 1's antiscia."""
    # Sun at 10.0 (Antiscia 170.0)
    # Moon at 170.0
    aspect = check_antiscia_aspect(10.0, PlanetName.SUN, 170.0, PlanetName.MOON)
    assert aspect is not None
    assert aspect["type"] == "Antiscia"
    assert aspect["exact"] is True
    assert aspect["orb"] == 0.0


def test_check_antiscia_aspect_within_orb():
    """Planet 2 within orb of Planet 1's contra-antiscia."""
    # Sun at 10.0 (Contra is 350.0)
    # Jupiter at 352.0 (2 degree orb)
    # Moieties: Sun=15/2=7.5? Wait, standard is Sun=15, Jup=9 -> moiety mean = (15+9)/2?
    # Code uses MOIETIES.get() which stores actual moiety (e.g., Sun=7.5, Jup=4.5).
    # Then mean is (7.5 + 4.5)/2 = 6.0 orb limit. 2.0 is well within orb.
    aspect = check_antiscia_aspect(10.0, PlanetName.SUN, 352.0, PlanetName.JUPITER)
    assert aspect is not None
    assert aspect["type"] == "Contra-Antiscia"
    assert aspect["exact"] is False
    assert aspect["orb"] == 2.0


def test_check_antiscia_aspect_outside_orb():
    """Planet 2 outside orb."""
    # Orb limit ~6.0. Put planet at 360-10 = 350. Distance 10 degrees -> no aspect.
    aspect = check_antiscia_aspect(10.0, PlanetName.SUN, 340.0, PlanetName.JUPITER)
    assert aspect is None


def test_engine_check_shadow_aspects():
    """Tests the full chart checker."""
    planets = [
        Planet(name=PlanetName.SUN, longitude=10.0, speed=1.0),
        Planet(
            name=PlanetName.MOON, longitude=170.0, speed=13.0
        ),  # Conjunct Sun's Antiscia
    ]
    results = ClassicalMechanicsEngine.check_shadow_aspects(planets)
    assert len(results) == 1
    assert results[0]["planet_1"] == "Sun"
    assert results[0]["planet_2"] == "Moon"
    assert results[0]["type"] == "Antiscia"
    assert results[0]["partile"] is True


def test_engine_get_antiscia():
    """Tests engine wrapper for get_antiscia."""
    pt = ClassicalMechanicsEngine.get_antiscia(10.0)
    assert pt.antiscia_lon == 170.0


# ─── 2. DODECATEMORIA ───────────────────────────────────────────────────────


def test_egyptian_term_ruler():
    """3° Aries falls into Jupiter's Egyptian Term."""
    ruler = get_egyptian_term_ruler(3.0)
    assert ruler == "Jupiter"


def test_dodecatemorion_valens():
    """10° Aries (10.0) Valens: 0 + 12*10 = 120 (0° Leo)."""
    dodec = calculate_dodecatemorion(10.0, method="Valens")
    assert dodec.method == "Valens"
    assert dodec.longitude == 120.0
    assert dodec.sign == Sign.LEO


def test_dodecatemorion_valens_wrap():
    """20° Taurus (50.0) Valens: 30 + 12*20 = 270 (0° Capricorn)."""
    dodec = calculate_dodecatemorion(50.0, method="Valens")
    assert dodec.longitude == 270.0
    assert dodec.sign == Sign.CAPRICORN


def test_dodecatemorion_paul():
    """10° Aries (10.0) Paul: 0 + 13*10 = 130 (10° Leo)."""
    dodec = calculate_dodecatemorion(10.0, method="Paul")
    assert dodec.method == "Paul"
    assert dodec.longitude == 130.0
    assert dodec.sign == Sign.LEO


def test_engine_get_dodecatemorion():
    dodec = ClassicalMechanicsEngine.get_dodecatemorion(10.0, method="Paul")
    assert dodec.longitude == 130.0


# ─── 3. PLANETARY HOURS ─────────────────────────────────────────────────────


@patch("src.engine.planetary_hours.PlanetaryHourEngine.calculate_hours")
def test_planetary_hours_radical(mock_calc):
    """Test radicality logic when ascendant lord matches hour lord."""
    # Saturday, daytime, Jupiter hour
    mock_calc.return_value = {
        "day_ruler": PlanetName.SATURN,
        "hour_ruler": PlanetName.JUPITER,
        "phase": "DAY",
        "hour_number_civil": 3,
    }

    dt = datetime(2023, 1, 1, 12, 0, tzinfo=timezone.utc)
    # Jupiter hour, ASC lord is Jupiter (Pisces)
    info = calculate_planetary_hours(
        dt, 0.0, 0.0, asc_sign=Sign.PISCES, asc_lord="Jupiter"
    )

    assert info is not None
    assert info.day_lord == "Saturn"
    assert info.hour_lord == "Jupiter"
    assert info.is_daytime is True
    assert info.radicality == "Radical (Identity)"


@patch("src.engine.planetary_hours.PlanetaryHourEngine.calculate_hours")
def test_planetary_hours_not_radical(mock_calc):
    """Test non-radical when ascendant lord does not match hour lord."""
    mock_calc.return_value = {
        "day_ruler": PlanetName.SATURN,
        "hour_ruler": PlanetName.VENUS,
    }

    dt = datetime(2023, 1, 1, 12, 0, tzinfo=timezone.utc)

    # We intentionally use an incomplete dict for mock, the function might crash
    # Oh wait, the function accesses report["phase"] and report["hour_number_civil"]
    mock_calc.return_value = {
        "day_ruler": PlanetName.SATURN,
        "hour_ruler": PlanetName.VENUS,
        "phase": "NIGHT",
        "hour_number_civil": 18,
    }

    info = calculate_planetary_hours(dt, 0.0, 0.0, asc_sign=Sign.ARIES, asc_lord="Mars")
    assert info.radicality == "Caution (No Identity)"


@patch("src.engine.planetary_hours.PlanetaryHourEngine.calculate_hours")
def test_planetary_hours_night_lord(mock_calc):
    """Night lord should be 13 hours from day lord in Chaldean order.
    Saturn is day lord. Order: Sat, Jup, Mar, Sun, Ven, Mer, Moo.
    12 shifts from Saturn -> Mod 7: 12 % 7 = 5 shifts.
    Sat(0) + 5 = Mer(5). Night lord should be Mercury.
    """
    mock_calc.return_value = {
        "day_ruler": PlanetName.SATURN,
        "hour_ruler": PlanetName.VENUS,
        "phase": "NIGHT",
        "hour_number_civil": 18,
    }

    info = calculate_planetary_hours(datetime.now(), 0.0, 0.0)
    assert info.night_lord == "Mercury"


@patch("src.engine.planetary_hours.PlanetaryHourEngine.calculate_hours")
def test_planetary_hours_error(mock_calc):
    mock_calc.return_value = {"error": "Too close to pole"}
    info = calculate_planetary_hours(datetime.now(), 89.0, 0.0)
    assert info is None


def test_engine_get_planetary_hours():
    with patch(
        "src.engine.planetary_hours.PlanetaryHourEngine.calculate_hours"
    ) as mock_calc:
        mock_calc.return_value = {
            "day_ruler": PlanetName.SUN,
            "hour_ruler": PlanetName.SUN,
            "phase": "DAY",
            "hour_number_civil": 1,
        }
        info = ClassicalMechanicsEngine.get_planetary_hours(datetime.now(), 0.0, 0.0)
        assert info.day_lord == "Sun"
