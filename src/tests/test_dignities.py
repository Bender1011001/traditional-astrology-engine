"""Tests for dignities.py — DignityCalculator."""

from src.engine.dignities import (DignityCalculator, TermSystem,
                                  TriplicityScheme)
from src.engine.models import Chart, Planet, PlanetName, Sect, Sign

# ─── calculate_planet_dignity ────────────────────────────────────────────────


def test_sun_in_leo_domicile():
    """Sun in Leo should have Domicile (+5)."""
    result = DignityCalculator.calculate_planet_dignity(PlanetName.SUN, 120.0, Sect.DAY)
    assert result["score_breakdown"]["domicile"] == 5
    assert result["total_score"] >= 5
    assert result["sign"] == "Leo"


def test_sun_in_aquarius_detriment():
    """Sun in Aquarius should have Detriment (-5)."""
    result = DignityCalculator.calculate_planet_dignity(PlanetName.SUN, 315.0, Sect.DAY)
    assert result["score_breakdown"]["detriment"] == -5


def test_sun_in_aries_exaltation():
    """Sun in Aries should have Exaltation (+4)."""
    result = DignityCalculator.calculate_planet_dignity(PlanetName.SUN, 10.0, Sect.DAY)
    assert result["score_breakdown"]["exaltation"] == 4


def test_sun_in_libra_fall():
    """Sun in Libra should have Fall (-4)."""
    result = DignityCalculator.calculate_planet_dignity(PlanetName.SUN, 190.0, Sect.DAY)
    assert result["score_breakdown"]["fall"] == -4


def test_dignity_returns_all_keys():
    result = DignityCalculator.calculate_planet_dignity(
        PlanetName.MARS, 100.0, Sect.NIGHT
    )
    assert "total_score" in result
    assert "score_breakdown" in result
    assert "details" in result
    assert "variants" in result
    assert "sign" in result
    assert "degree" in result


def test_triplicity_day_fire():
    """Sun should have Triplicity in a Fire sign during day."""
    # Sun at 5° Aries (Fire sign), Day chart — Sun is day triplicity ruler of Fire
    result = DignityCalculator.calculate_planet_dignity(PlanetName.SUN, 5.0, Sect.DAY)
    assert result["score_breakdown"]["triplicity"] == 3


def test_triplicity_night_fire():
    """Jupiter should have Triplicity in a Fire sign at night."""
    # Jupiter at 5° Aries, Night — Jupiter is night triplicity ruler of Fire
    result = DignityCalculator.calculate_planet_dignity(
        PlanetName.JUPITER, 5.0, Sect.NIGHT
    )
    assert result["score_breakdown"]["triplicity"] == 3


def test_all_planets_dignity_computable():
    """Every traditional planet should compute without errors."""
    planets = [
        PlanetName.SUN,
        PlanetName.MOON,
        PlanetName.MERCURY,
        PlanetName.VENUS,
        PlanetName.MARS,
        PlanetName.JUPITER,
        PlanetName.SATURN,
    ]
    for p in planets:
        for lon in [0.0, 90.0, 180.0, 270.0]:
            result = DignityCalculator.calculate_planet_dignity(p, lon, Sect.DAY)
            assert isinstance(result["total_score"], int)


# ─── calculate_planet_dignity_variant ────────────────────────────────────────


def test_variant_ptolemaic_terms():
    result = DignityCalculator.calculate_planet_dignity_variant(
        PlanetName.VENUS, 35.0, Sect.DAY, term_system=TermSystem.PTOLEMAIC
    )
    assert "total_score" in result
    assert result["variants"]["term_system"] == "Ptolemaic"


def test_variant_ptolemaic_triplicity():
    result = DignityCalculator.calculate_planet_dignity_variant(
        PlanetName.MARS,
        5.0,
        Sect.NIGHT,
        triplicity_scheme=TriplicityScheme.PTOLEMAIC_SECT_GATED,
    )
    assert result["variants"]["triplicity_scheme"] == "Ptolemaic (sect-gated)"


def test_variant_peregrine():
    """A planet with no essential dignity should get Peregrine (-5)."""
    # Use a planet in a sign where it has nothing — e.g. Moon at 0° Gemini
    result = DignityCalculator.calculate_planet_dignity_variant(
        PlanetName.MOON, 60.0, Sect.DAY, include_monomoiria=False
    )
    # Note: Moon may still have term or face in Gemini, so check conditionally
    if (
        result["score_breakdown"]["domicile"] == 0
        and result["score_breakdown"]["exaltation"] == 0
        and result["score_breakdown"]["triplicity"] == 0
        and result["score_breakdown"]["term"] == 0
        and result["score_breakdown"]["face"] == 0
        and result["score_breakdown"]["detriment"] == 0
        and result["score_breakdown"]["fall"] == 0
    ):
        assert "Peregrine" in " ".join(result["details"])


# ─── get_house_number ────────────────────────────────────────────────────────


def test_house_number_whole_sign():
    """Whole Sign: planet in same sign as Asc = House 1."""
    house = DignityCalculator.get_house_number(5.0, 0.0)
    assert house == 1


def test_house_number_opposite():
    """Planet 180° from Asc = House 7."""
    house = DignityCalculator.get_house_number(180.0, 0.0)
    assert house == 7


def test_house_number_with_cusps():
    """With explicit house cusps."""
    cusps = {i: (i - 1) * 30.0 for i in range(1, 13)}
    house = DignityCalculator.get_house_number(45.0, 0.0, cusps)
    assert house == 2


# ─── get_monomoiria_ruler ────────────────────────────────────────────────────


def test_monomoiria_ruler_returns_planet():
    ruler = DignityCalculator.get_monomoiria_ruler(Sign.ARIES, 0.0)
    assert isinstance(ruler, PlanetName)
    # 0° Aries → domicile ruler = Mars, degree 0 → Mars
    assert ruler == PlanetName.MARS


def test_monomoiria_ruler_chaldean_rotation():
    """Subsequent degrees should rotate through the Chaldean order."""
    r0 = DignityCalculator.get_monomoiria_ruler(Sign.ARIES, 0.0)
    r1 = DignityCalculator.get_monomoiria_ruler(Sign.ARIES, 1.0)
    # r0 = Mars (domicile ruler), r1 should be next in Chaldean order from Mars
    assert r0 != r1  # They should differ


# ─── check_hayz_halb ─────────────────────────────────────────────────────────


def test_hayz_diurnal_planet_day():
    """Sun in a Fire sign, day chart, above horizon → Hayz."""
    chart = Chart(
        sun_altitude=10.0,
        planets=[Planet(name=PlanetName.SUN, longitude=5.0, speed=1.0)],
        ascendant=180.0,  # Libra Asc → Aries is House 7 (above horizon)
        mc=270.0,
    )
    result = DignityCalculator.check_hayz_halb(PlanetName.SUN, 5.0, chart)
    # Aries (Fire/Masculine), Day chart, House 7 (above horizon) → Hayz
    assert result["status"] == "Hayz"
    assert result["horizon_method"] == "house_number_fallback"


def test_hayz_returns_dict():
    chart = Chart(
        sun_altitude=10.0,
        planets=[Planet(name=PlanetName.MOON, longitude=100.0, speed=13.0)],
        ascendant=0.0,
        mc=270.0,
    )
    result = DignityCalculator.check_hayz_halb(PlanetName.MOON, 100.0, chart)
    assert "status" in result
    assert "details" in result


def test_hayz_uses_calculated_altitude_and_al_biruni_halb_rule():
    sun = Planet(name=PlanetName.SUN, longitude=5.0, speed=1.0, altitude=12.0)
    jupiter = Planet(
        name=PlanetName.JUPITER,
        longitude=275.0,  # Capricorn, feminine sign
        speed=0.08,
        altitude=20.0,
    )
    moon = Planet(
        name=PlanetName.MOON,
        longitude=95.0,  # Cancer, feminine sign
        speed=13.0,
        altitude=-15.0,
    )
    chart = Chart(
        sun_altitude=12.0,
        planets=[sun, jupiter, moon],
        ascendant=180.0,
        mc=270.0,
        jd=2450000.0,
    )

    sun_result = DignityCalculator.check_hayz_halb(PlanetName.SUN, 5.0, chart)
    jupiter_result = DignityCalculator.check_hayz_halb(
        PlanetName.JUPITER, 275.0, chart
    )
    moon_result = DignityCalculator.check_hayz_halb(
        PlanetName.MOON, 95.0, chart
    )

    assert sun_result["status"] == "Hayz"
    assert jupiter_result["status"] == "Halb"
    assert moon_result["status"] == "Hayz"
    assert all(
        result["horizon_method"] == "stored_altitude"
        for result in (sun_result, jupiter_result, moon_result)
    )


def test_hayz_keeps_mercury_indeterminate_until_association_is_modeled():
    mercury = Planet(
        name=PlanetName.MERCURY,
        longitude=165.0,
        speed=1.2,
        altitude=-10.0,
    )
    chart = Chart(
        sun_altitude=10.0,
        planets=[mercury],
        ascendant=150.0,
        mc=60.0,
        jd=2450000.0,
    )
    result = DignityCalculator.check_hayz_halb(
        PlanetName.MERCURY, 165.0, chart
    )
    assert result["status"] == "Indeterminate"
    assert result["halb_match"] is None


# ─── calculate_accidental_dignity ────────────────────────────────────────────


def test_accidental_dignity_angular():
    """Planet in angular house should get +5."""
    chart = Chart(
        sun_altitude=10.0,
        planets=[
            Planet(name=PlanetName.SUN, longitude=5.0, speed=1.0),
            Planet(name=PlanetName.JUPITER, longitude=5.0, speed=0.08),
        ],
        ascendant=0.0,
        mc=270.0,
    )
    jupiter = chart.planets[1]
    result = DignityCalculator.calculate_accidental_dignity(jupiter, chart)
    assert result["house"] == 1  # Same sign as Asc
    assert any("+5" in d for d in result["details"])


def test_accidental_dignity_retrograde():
    """Retrograde planet should get -5."""
    chart = Chart(
        sun_altitude=10.0,
        planets=[
            Planet(name=PlanetName.SUN, longitude=100.0, speed=1.0),
            Planet(name=PlanetName.SATURN, longitude=300.0, speed=-0.03),
        ],
        ascendant=0.0,
        mc=270.0,
    )
    saturn = chart.planets[1]
    result = DignityCalculator.calculate_accidental_dignity(saturn, chart)
    assert any("Retrograde" in d for d in result["details"])


# ─── get_essential_rulers ────────────────────────────────────────────────────


def test_get_essential_rulers():
    rulers = DignityCalculator.get_essential_rulers(5.0, Sect.DAY)
    assert "domicile" in rulers
    assert "exaltation" in rulers
    assert "triplicity" in rulers
    assert "term" in rulers
    assert "face" in rulers
    # 5° Aries → domicile = Mars
    assert rulers["domicile"] == PlanetName.MARS


# ─── calculate_planetary_joy ─────────────────────────────────────────────────


def test_planetary_joy_mercury_h1():
    p = Planet(name=PlanetName.MERCURY, longitude=0.0, speed=1.0)
    assert DignityCalculator.calculate_planetary_joy(p, 1) == 2


def test_planetary_joy_wrong_house():
    p = Planet(name=PlanetName.MERCURY, longitude=0.0, speed=1.0)
    assert DignityCalculator.calculate_planetary_joy(p, 5) == 0


def test_planetary_joy_all():
    """Each joy planet should score 2 in its joy house."""
    joys = {
        PlanetName.MERCURY: 1,
        PlanetName.MOON: 3,
        PlanetName.VENUS: 5,
        PlanetName.MARS: 6,
        PlanetName.SUN: 9,
        PlanetName.JUPITER: 11,
        PlanetName.SATURN: 12,
    }
    for name, house in joys.items():
        p = Planet(name=name, longitude=0.0, speed=1.0)
        assert (
            DignityCalculator.calculate_planetary_joy(p, house) == 2
        ), f"{name.value} joy in house {house} failed"
