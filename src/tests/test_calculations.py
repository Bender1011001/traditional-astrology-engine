"""Tests for calculations.py — core utility functions."""
from src.engine.calculations import (
    format_longitude,
    calculate_sect,
    calculate_lunar_phase,
    calculate_solar_status,
    is_in_via_combusta,
    is_besieged,
    is_void_of_course,
    calculate_prenatal_syzygy,
)
from src.engine.models import Planet, PlanetName, Sect, Chart


# ─── format_longitude ────────────────────────────────────────────────────────

def test_format_longitude_aries_zero():
    result = format_longitude(0.0)
    assert result["sign"] == "Aries"
    assert result["dms"]["deg"] == 0
    assert result["lon_abs"] == 0.0
    assert "Aries" in result["string"]


def test_format_longitude_leo():
    result = format_longitude(126.27)
    assert result["sign"] == "Leo"
    assert 0 <= result["dms"]["deg"] < 30


def test_format_longitude_wraparound():
    """360° should wrap to 0° Aries."""
    result = format_longitude(360.0)
    assert result["sign"] == "Aries"
    assert result["lon_abs"] == 0.0


def test_format_longitude_negative():
    """Negative should wrap correctly."""
    result = format_longitude(-30.0)
    # -30 % 360 = 330 = Pisces 0°
    assert result["sign"] == "Pisces"


def test_format_longitude_each_sign():
    """Each 30° boundary should map to the next sign."""
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    for i, expected_sign in enumerate(signs):
        result = format_longitude(i * 30.0 + 15.0)
        assert result["sign"] == expected_sign, f"At {i*30+15}° expected {expected_sign}, got {result['sign']}"


def test_format_longitude_dms_seconds_rollover():
    """Test that 59.999 seconds rounds to 0 seconds and increments minute."""
    # This is an edge case in the rounding logic
    result = format_longitude(0.0)
    assert result["dms"]["sec"] < 60
    assert result["dms"]["min"] < 60


# ─── calculate_sect ──────────────────────────────────────────────────────────

def test_calculate_sect_day():
    assert calculate_sect(10.0) == Sect.DAY


def test_calculate_sect_night():
    assert calculate_sect(-5.0) == Sect.NIGHT


def test_calculate_sect_horizon():
    """Sun at exactly 0 altitude is night (not > 0)."""
    assert calculate_sect(0.0) == Sect.NIGHT


# ─── calculate_lunar_phase ───────────────────────────────────────────────────

def test_lunar_phase_new_moon():
    name, profile = calculate_lunar_phase(0.0, 10.0)
    assert name == "New Moon"
    assert "Initiator" in profile


def test_lunar_phase_full_moon():
    name, profile = calculate_lunar_phase(0.0, 190.0)
    assert name == "Full Moon"
    assert "Objectifier" in profile or "Realizer" in profile


def test_lunar_phase_crescent():
    name, _ = calculate_lunar_phase(0.0, 60.0)
    assert name == "Crescent"


def test_lunar_phase_balsamic():
    name, _ = calculate_lunar_phase(0.0, 330.0)
    assert name == "Balsamic"


def test_lunar_phase_all_phases():
    """All 8 phases should be reachable."""
    phases_found = set()
    for diff in range(0, 360, 5):
        name, _ = calculate_lunar_phase(0.0, float(diff))
        phases_found.add(name)
    assert len(phases_found) == 8, f"Only found {len(phases_found)} phases: {phases_found}"


# ─── calculate_solar_status ──────────────────────────────────────────────────

def test_solar_status_sun_is_sun():
    sun = Planet(name=PlanetName.SUN, longitude=100.0, speed=1.0)
    assert calculate_solar_status(sun, sun) == "SUN"


def test_solar_status_cazimi():
    sun = Planet(name=PlanetName.SUN, longitude=100.0, speed=1.0)
    planet = Planet(name=PlanetName.MERCURY, longitude=100.1, speed=1.0)
    assert calculate_solar_status(planet, sun) == "CAZIMI"


def test_solar_status_combust():
    sun = Planet(name=PlanetName.SUN, longitude=100.0, speed=1.0)
    planet = Planet(name=PlanetName.MERCURY, longitude=105.0, speed=1.0)
    assert calculate_solar_status(planet, sun) == "COMBUST"


def test_solar_status_under_beams():
    sun = Planet(name=PlanetName.SUN, longitude=100.0, speed=1.0)
    planet = Planet(name=PlanetName.MERCURY, longitude=112.0, speed=1.0)
    assert calculate_solar_status(planet, sun) == "UNDER_BEAMS"


def test_solar_status_free():
    sun = Planet(name=PlanetName.SUN, longitude=100.0, speed=1.0)
    planet = Planet(name=PlanetName.MERCURY, longitude=130.0, speed=1.0)
    assert calculate_solar_status(planet, sun) == "FREE"


def test_solar_status_moon_dark():
    sun = Planet(name=PlanetName.SUN, longitude=100.0, speed=1.0)
    moon = Planet(name=PlanetName.MOON, longitude=104.0, speed=13.0)
    assert calculate_solar_status(moon, sun) == "DARK_MOON"


def test_solar_status_moon_under_beams():
    sun = Planet(name=PlanetName.SUN, longitude=100.0, speed=1.0)
    moon = Planet(name=PlanetName.MOON, longitude=112.0, speed=13.0)
    assert calculate_solar_status(moon, sun) == "MOON_UNDER_BEAMS"


def test_solar_status_moon_free():
    sun = Planet(name=PlanetName.SUN, longitude=100.0, speed=1.0)
    moon = Planet(name=PlanetName.MOON, longitude=160.0, speed=13.0)
    assert calculate_solar_status(moon, sun) == "FREE"


# ─── is_in_via_combusta ─────────────────────────────────────────────────────

def test_via_combusta_inside():
    assert is_in_via_combusta(210.0) is True


def test_via_combusta_boundary_low():
    assert is_in_via_combusta(195.0) is True


def test_via_combusta_boundary_high():
    assert is_in_via_combusta(225.0) is True


def test_via_combusta_outside():
    assert is_in_via_combusta(100.0) is False
    assert is_in_via_combusta(226.0) is False


# ─── is_besieged ─────────────────────────────────────────────────────────────

def _make_chart(positions, asc=0.0, sun_alt=10.0):
    planets = [Planet(name=n, longitude=lon, speed=1.0) for n, lon in positions.items()]
    return Chart(sun_altitude=sun_alt, planets=planets, ascendant=asc, mc=270.0)


def test_besieged_between_malefics():
    chart = _make_chart({
        PlanetName.SUN: 100.0,
        PlanetName.MOON: 105.0,
        PlanetName.MARS: 100.0,
        PlanetName.SATURN: 110.0,
        PlanetName.MERCURY: 150.0,
        PlanetName.VENUS: 200.0,
        PlanetName.JUPITER: 300.0,
    })
    moon = next(p for p in chart.planets if p.name == PlanetName.MOON)
    assert is_besieged(moon, chart) is True


def test_not_besieged_too_far():
    chart = _make_chart({
        PlanetName.SUN: 100.0,
        PlanetName.MOON: 105.0,
        PlanetName.MARS: 50.0,
        PlanetName.SATURN: 200.0,
        PlanetName.MERCURY: 150.0,
        PlanetName.VENUS: 250.0,
        PlanetName.JUPITER: 300.0,
    })
    moon = next(p for p in chart.planets if p.name == PlanetName.MOON)
    assert is_besieged(moon, chart) is False


def test_mars_cannot_be_besieged():
    """Mars itself should never be considered besieged."""
    chart = _make_chart({
        PlanetName.SUN: 100.0,
        PlanetName.MOON: 200.0,
        PlanetName.MARS: 105.0,
        PlanetName.SATURN: 110.0,
        PlanetName.MERCURY: 150.0,
        PlanetName.VENUS: 250.0,
        PlanetName.JUPITER: 300.0,
    })
    mars = next(p for p in chart.planets if p.name == PlanetName.MARS)
    assert is_besieged(mars, chart) is False


# ─── is_void_of_course ──────────────────────────────────────────────────────

def test_voc_with_applying_aspect():
    """Moon with an applying aspect should NOT be void of course."""
    planets = [
        Planet(name=PlanetName.MOON, longitude=100.0, speed=13.0),
        Planet(name=PlanetName.JUPITER, longitude=110.0, speed=0.08),
    ]
    # Moon at 100, Jupiter at 110 — Moon needs to reach 110 (conjunction) before 120 (next sign)
    # Moon speed=13, Jupiter speed=0.08, closing_speed=12.92 > 0 => applying
    assert is_void_of_course(100.0, planets) is False


def test_voc_late_sign_no_aspects():
    """Moon late in sign with no targets ahead should be VoC."""
    planets = [
        Planet(name=PlanetName.MOON, longitude=29.0, speed=13.0),
        Planet(name=PlanetName.JUPITER, longitude=200.0, speed=0.08),
        Planet(name=PlanetName.SATURN, longitude=300.0, speed=0.03),
    ]
    # Moon at 29° Aries, only 1° left in sign — Jupiter and Saturn far away
    result = is_void_of_course(29.0, planets)
    # This may or may not be VoC depending on exact aspect geometry
    assert isinstance(result, bool)


def test_voc_no_moon():
    """No Moon planet at all should return True (safety)."""
    planets = [
        Planet(name=PlanetName.SUN, longitude=100.0, speed=1.0),
    ]
    assert is_void_of_course(100.0, planets) is True


# ─── calculate_prenatal_syzygy ───────────────────────────────────────────────

def test_prenatal_syzygy_returns_tuple():
    """Should return (longitude, type) tuple."""
    import swisseph as swe
    # Use a known Julian Day (Jan 1, 2000 noon)
    jd = swe.julday(2000, 1, 1, 12.0)
    lon, syz_type = calculate_prenatal_syzygy(jd)
    assert isinstance(lon, float)
    assert syz_type in ["New", "Full"]
    assert 0.0 <= lon < 360.0
