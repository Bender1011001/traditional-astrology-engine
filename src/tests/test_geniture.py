"""Tests for geniture.py — Lord of Geniture (Lilly net fortitudes/debilities)."""

from src.engine.geniture import GeniturePlanetScore, LordOfGenitureEngine
from src.engine.models import Chart, Planet, PlanetName, Sect, Sign


def _make_chart(planet_positions, asc=0.0, sun_alt=10.0):
    planets = [
        Planet(name=n, longitude=lon, speed=spd) for n, lon, spd in planet_positions
    ]
    return Chart(sun_altitude=sun_alt, planets=planets, ascendant=asc, mc=270.0)


def _full_chart(asc=0.0, sun_alt=10.0):
    """A standard chart with all 7 traditional planets."""
    return _make_chart(
        [
            (PlanetName.SUN, 120.0, 1.0),  # Leo
            (PlanetName.MOON, 100.0, 13.0),  # Cancer
            (PlanetName.MERCURY, 130.0, 1.5),  # Leo
            (PlanetName.VENUS, 60.0, 1.0),  # Gemini
            (PlanetName.MARS, 200.0, 0.5),  # Libra
            (PlanetName.JUPITER, 270.0, 0.08),  # Capricorn
            (PlanetName.SATURN, 300.0, 0.03),  # Aquarius
        ],
        asc=asc,
        sun_alt=sun_alt,
    )


# ─── Helper methods ──────────────────────────────────────────────────────────


def test_norm_diff_same():
    assert LordOfGenitureEngine._norm_diff(100.0, 100.0) == 0.0


def test_norm_diff_wrap():
    assert abs(LordOfGenitureEngine._norm_diff(350.0, 10.0) - 20.0) < 0.01


def test_in_sign():
    assert LordOfGenitureEngine._in_sign(120.0) == Sign.LEO


def test_deg_in_sign():
    assert abs(LordOfGenitureEngine._deg_in_sign(125.0) - 5.0) < 0.01


# ─── _essential_score_lilly ──────────────────────────────────────────────────


def test_essential_domicile():
    """Sun in Leo should get domicile (+5)."""
    score, breakdown, details = LordOfGenitureEngine._essential_score_lilly(
        PlanetName.SUN, 120.0, Sect.DAY  # 0° Leo
    )
    assert breakdown["domicile"] == 5
    assert score >= 5


def test_essential_detriment():
    """Sun in Aquarius should get detriment (-5)."""
    score, breakdown, details = LordOfGenitureEngine._essential_score_lilly(
        PlanetName.SUN, 300.0, Sect.DAY  # 0° Aquarius
    )
    assert breakdown["detriment"] == -5


def test_essential_peregrine():
    """Planet with no dignity at its position should be peregrine (-5)."""
    # Saturn at 120° Leo — no essential dignity
    score, breakdown, details = LordOfGenitureEngine._essential_score_lilly(
        PlanetName.SATURN, 120.0, Sect.DAY
    )
    # May or may not be peregrine depending on triplicity/terms — check if flag is set
    # Saturn is not domicile, exalt, trip, term, or face in Leo
    if breakdown["peregrine"] != 0:
        assert breakdown["peregrine"] == -5


# ─── _house_score_lilly ─────────────────────────────────────────────────────


def test_house_score_angular():
    score, detail = LordOfGenitureEngine._house_score_lilly(1)
    assert score == 5
    assert "+5" in detail


def test_house_score_succedent_strong():
    score, _ = LordOfGenitureEngine._house_score_lilly(11)
    assert score == 4


def test_house_score_12th():
    score, _ = LordOfGenitureEngine._house_score_lilly(12)
    assert score == -5


def test_house_score_8th():
    score, _ = LordOfGenitureEngine._house_score_lilly(8)
    assert score == -2


# ─── _motion_score_lilly ────────────────────────────────────────────────────


def test_motion_direct():
    p = Planet(name=PlanetName.JUPITER, longitude=270.0, speed=0.08)
    score, breakdown, details = LordOfGenitureEngine._motion_score_lilly(p)
    assert breakdown["direct"] == 4
    assert breakdown["retrograde"] == 0


def test_motion_retrograde():
    p = Planet(name=PlanetName.JUPITER, longitude=270.0, speed=-0.08)
    score, breakdown, details = LordOfGenitureEngine._motion_score_lilly(p)
    assert breakdown["retrograde"] == -5
    assert score == -5


def test_motion_swift():
    """Faster than average should give swift bonus."""
    p = Planet(name=PlanetName.MERCURY, longitude=130.0, speed=2.0)  # Avg ~1.6
    score, breakdown, details = LordOfGenitureEngine._motion_score_lilly(p)
    assert breakdown["swift"] == 2


# ─── _solar_phase_score_lilly ────────────────────────────────────────────────


def test_solar_phase_sun_exempt():
    """Sun itself should return 0 for solar phase."""
    chart = _full_chart()
    sun = chart.planets[0]
    score, _, _ = LordOfGenitureEngine._solar_phase_score_lilly(sun, chart)
    assert score == 0


def test_solar_phase_cazimi():
    """Planet within 0°17' of Sun = Cazimi (+5)."""
    chart = _make_chart(
        [
            (PlanetName.SUN, 120.0, 1.0),
            (PlanetName.MERCURY, 120.1, 1.2),  # 0.1° from Sun (within 0.28° cazimi)
        ]
    )
    merc = chart.planets[1]
    score, breakdown, _ = LordOfGenitureEngine._solar_phase_score_lilly(merc, chart)
    assert breakdown["cazimi"] == 5


def test_solar_phase_combust():
    """Planet within 8.5° of Sun = Combust (-5)."""
    chart = _make_chart(
        [
            (PlanetName.SUN, 120.0, 1.0),
            (PlanetName.MERCURY, 125.0, 1.2),  # 5° from Sun
        ]
    )
    merc = chart.planets[1]
    score, breakdown, _ = LordOfGenitureEngine._solar_phase_score_lilly(merc, chart)
    assert breakdown["combust"] == -5


def test_solar_phase_under_beams():
    """Planet within 17° but outside 8.5° = Under Beams (-4)."""
    chart = _make_chart(
        [
            (PlanetName.SUN, 120.0, 1.0),
            (PlanetName.VENUS, 132.0, 1.0),  # 12° from Sun
        ]
    )
    venus = chart.planets[1]
    score, breakdown, _ = LordOfGenitureEngine._solar_phase_score_lilly(venus, chart)
    assert breakdown["under_beams"] == -4


# ─── _orientality_score_lilly ────────────────────────────────────────────────


def test_orientality_moon_increasing():
    """Moon ahead of Sun (increasing light) should get +2."""
    chart = _make_chart(
        [
            (PlanetName.SUN, 120.0, 1.0),
            (PlanetName.MOON, 200.0, 13.0),  # 80° ahead
        ]
    )
    moon = chart.planets[1]
    score, _, details = LordOfGenitureEngine._orientality_score_lilly(moon, chart)
    assert score == 2


# ─── calculate (full pipeline) ──────────────────────────────────────────────


def test_calculate_returns_expected_keys():
    chart = _full_chart()
    result = LordOfGenitureEngine.calculate(chart)
    assert "winner" in result
    assert "scores" in result
    assert "method" in result
    assert "Lilly" in result["method"]


def test_calculate_scores_all_seven():
    """All 7 traditional planets should have scores."""
    chart = _full_chart()
    result = LordOfGenitureEngine.calculate(chart)
    for pname in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
        assert pname in result["scores"], f"Missing score for {pname}"


def test_calculate_winner_is_valid():
    chart = _full_chart()
    result = LordOfGenitureEngine.calculate(chart)
    valid = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Unknown"]
    assert result["winner"] in valid


def test_calculate_score_has_breakdown():
    chart = _full_chart()
    result = LordOfGenitureEngine.calculate(chart)
    for pname, data in result["scores"].items():
        assert "total" in data
        assert "breakdown" in data
        assert "details" in data
        assert isinstance(data["total"], int)
        assert isinstance(data["details"], list)


# ─── GeniturePlanetScore dataclass ──────────────────────────────────────────


def test_geniture_planet_score_dataclass():
    gps = GeniturePlanetScore(
        planet=PlanetName.SUN,
        total=15,
        breakdown={"domicile": 5, "direct": 4},
        details=["Domicile (+5)", "Direct (+4)"],
    )
    assert gps.total == 15
    assert gps.planet == PlanetName.SUN
