"""Tests for phasis.py — Planetary Phases, Solar Proximity, Arcus Visionis."""

from src.engine.models import (Planet, PlanetaryPhase, PlanetName,
                               SolarProximity)
from src.engine.phasis import AV_THRESHOLDS, NAME_TO_SWE, PhasisEngine

# ─── is_oriental ─────────────────────────────────────────────────────────────


def test_is_oriental_behind_sun():
    """Planet behind Sun zodiacally (Sun at 100, planet at 80) = Oriental."""
    assert PhasisEngine.is_oriental(80.0, 100.0) is True


def test_is_oriental_ahead_sun():
    """Planet ahead of Sun (Sun at 100, planet at 200) = Occidental."""
    assert PhasisEngine.is_oriental(200.0, 100.0) is False


def test_is_oriental_wraparound():
    """Planet at 350, Sun at 10 — planet behind Sun = Oriental."""
    assert PhasisEngine.is_oriental(350.0, 10.0) is True


# ─── get_solar_proximity ────────────────────────────────────────────────────


def test_solar_proximity_cazimi():
    """Within 17' (0.283°) of Sun = Cazimi."""
    result = PhasisEngine.get_solar_proximity(100.0, 100.1)
    assert result == SolarProximity.CAZIMI


def test_solar_proximity_combust():
    """Within 8° of Sun = Combust."""
    result = PhasisEngine.get_solar_proximity(95.0, 100.0)
    assert result == SolarProximity.COMBUST


def test_solar_proximity_under_beams():
    """Within 15° but outside 8° = Under Beams."""
    result = PhasisEngine.get_solar_proximity(88.0, 100.0)
    assert result == SolarProximity.UNDER_BEAMS


def test_solar_proximity_free():
    """Beyond 15° = Free."""
    result = PhasisEngine.get_solar_proximity(70.0, 100.0)
    assert result == SolarProximity.FREE


def test_solar_proximity_wraparound():
    """Proximity wraps around the zodiac."""
    result = PhasisEngine.get_solar_proximity(355.0, 5.0)  # 10° apart
    assert result == SolarProximity.UNDER_BEAMS


# ─── get_synodic_phase ──────────────────────────────────────────────────────


def test_synodic_phase_sun():
    """Sun always returns FREE."""
    sun = Planet(name=PlanetName.SUN, longitude=100.0, speed=1.0)
    result = PhasisEngine.get_synodic_phase(sun, 100.0)
    assert result == PlanetaryPhase.FREE


def test_synodic_phase_cazimi():
    """Planet conjunct Sun within cazimi returns CAZIMI."""
    merc = Planet(name=PlanetName.MERCURY, longitude=100.1, speed=1.2)
    result = PhasisEngine.get_synodic_phase(merc, 100.0)
    assert result == PlanetaryPhase.CAZIMI


def test_synodic_phase_station_retrograde():
    """Nearly stationary planet with negative speed = Station Retrograde."""
    sat = Planet(name=PlanetName.SATURN, longitude=200.0, speed=-0.02)
    result = PhasisEngine.get_synodic_phase(sat, 100.0)
    assert result == PlanetaryPhase.STATION_RETROGRADE


def test_synodic_phase_station_direct():
    sat = Planet(name=PlanetName.SATURN, longitude=200.0, speed=0.02)
    result = PhasisEngine.get_synodic_phase(sat, 100.0)
    assert result == PlanetaryPhase.STATION_DIRECT


def test_synodic_phase_superior_opposition():
    """Superior planet ~180° from Sun = Opposition."""
    mars = Planet(name=PlanetName.MARS, longitude=280.0, speed=0.5)
    result = PhasisEngine.get_synodic_phase(mars, 100.0)
    assert result == PlanetaryPhase.OPPOSITION


def test_synodic_phase_returns_planetary_phase():
    """Any planet should return a PlanetaryPhase enum."""
    jup = Planet(name=PlanetName.JUPITER, longitude=200.0, speed=0.1)
    result = PhasisEngine.get_synodic_phase(jup, 100.0)
    assert isinstance(result, PlanetaryPhase)


# ─── AV_THRESHOLDS ──────────────────────────────────────────────────────────


def test_av_thresholds_completeness():
    """All traditional planets should have AV thresholds."""
    for pn in [
        PlanetName.SATURN,
        PlanetName.JUPITER,
        PlanetName.MARS,
        PlanetName.MERCURY,
    ]:
        assert pn in AV_THRESHOLDS


def test_av_threshold_venus_asymmetric():
    """Venus has separate morning/evening thresholds."""
    assert "VENUS_EVENING" in AV_THRESHOLDS
    assert "VENUS_MORNING" in AV_THRESHOLDS
    assert AV_THRESHOLDS["VENUS_MORNING"] > AV_THRESHOLDS["VENUS_EVENING"]


# ─── NAME_TO_SWE ────────────────────────────────────────────────────────────


def test_name_to_swe_mapping():
    """All 7 classical bodies should map to swisseph constants."""
    for pn in [
        PlanetName.SUN,
        PlanetName.MOON,
        PlanetName.MERCURY,
        PlanetName.VENUS,
        PlanetName.MARS,
        PlanetName.JUPITER,
        PlanetName.SATURN,
    ]:
        assert pn in NAME_TO_SWE


# ─── calculate_visibility_details ────────────────────────────────────────────


def test_visibility_sun_always_visible():
    result = PhasisEngine.calculate_visibility_details(
        jd=2460000.0,
        lat=40.0,
        lon=-74.0,
        planet_name=PlanetName.SUN,
        planet_lon=100.0,
        planet_lat=0.0,
        sun_lon=100.0,
    )
    assert result["is_visible"] is True
    assert result["method"] == "sun_default"


def test_visibility_non_traditional():
    """Nodes/non-traditional bodies default to visible."""
    result = PhasisEngine.calculate_visibility_details(
        jd=2460000.0,
        lat=40.0,
        lon=-74.0,
        planet_name=PlanetName.MOON,
        planet_lon=200.0,
        planet_lat=5.0,
        sun_lon=100.0,
    )
    assert result["is_visible"] is True
    assert result["method"] == "non_traditional_default"


def test_visibility_details_keys():
    """Result should have all documented keys."""
    result = PhasisEngine.calculate_visibility_details(
        jd=2460000.0,
        lat=40.0,
        lon=-74.0,
        planet_name=PlanetName.SATURN,
        planet_lon=200.0,
        planet_lat=0.0,
        sun_lon=100.0,
    )
    for key in [
        "is_visible",
        "method",
        "oriental",
        "event",
        "threshold_solar_depression_deg",
        "sun_altitude_at_event_deg",
        "event_jd_ut",
        "note",
    ]:
        assert key in result, f"Missing key: {key}"


# ─── check_chariot ──────────────────────────────────────────────────────────


def test_chariot_sun_in_leo():
    """Sun at 120° (Leo, its domicile) should be in its chariot."""
    result = PhasisEngine.check_chariot(PlanetName.SUN, 120.0, {}, {})
    assert result is True


def test_chariot_not_in_dignity():
    """Saturn at 120° (Leo) is NOT in its chariot."""
    result = PhasisEngine.check_chariot(PlanetName.SATURN, 120.0, {}, {})
    assert result is False
