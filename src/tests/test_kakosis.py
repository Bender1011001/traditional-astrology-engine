"""Tests for kakosis.py — 7 Conditions of Maltreatment (Hellenistic)."""
from src.engine.kakosis import KakosisEngine, MaltreatmentCondition
from src.engine.models import Chart, Planet, PlanetName, Sect, Sign


def _make_chart(planet_positions, asc=0.0, sun_alt=10.0):
    planets = [Planet(name=n, longitude=lon, speed=spd) for n, lon, spd in planet_positions]
    return Chart(sun_altitude=sun_alt, planets=planets, ascendant=asc, mc=270.0)


# ─── get_zodiac_index ────────────────────────────────────────────────────────

def test_zodiac_index_aries():
    assert KakosisEngine.get_zodiac_index(Sign.ARIES) == 0


def test_zodiac_index_pisces():
    assert KakosisEngine.get_zodiac_index(Sign.PISCES) == 11


def test_zodiac_index_string():
    assert KakosisEngine.get_zodiac_index("Leo") == 4


def test_zodiac_index_invalid():
    assert KakosisEngine.get_zodiac_index("NotASign") == -1


# ─── is_malefic_for_sect ─────────────────────────────────────────────────────

def test_malefic_mars_day():
    """Mars is the worse malefic in a Day chart."""
    assert KakosisEngine.is_malefic_for_sect(PlanetName.MARS, Sect.DAY) is True


def test_malefic_saturn_night():
    """Saturn is the worse malefic in a Night chart."""
    assert KakosisEngine.is_malefic_for_sect(PlanetName.SATURN, Sect.NIGHT) is True


def test_non_malefic():
    """Jupiter is not a malefic."""
    assert KakosisEngine.is_malefic_for_sect(PlanetName.JUPITER, Sect.DAY) is False


# ─── check_maltreatments ────────────────────────────────────────────────────

def test_check_maltreatments_returns_list():
    chart = _make_chart([
        (PlanetName.SUN, 100.0, 1.0),
        (PlanetName.MOON, 200.0, 13.0),
        (PlanetName.MARS, 300.0, 0.5),
        (PlanetName.SATURN, 50.0, 0.03),
        (PlanetName.JUPITER, 170.0, 0.08),
        (PlanetName.VENUS, 230.0, 1.0),
    ])
    moon = chart.planets[1]
    result = KakosisEngine.check_maltreatments(moon, chart)
    assert isinstance(result, list)
    for cond in result:
        assert isinstance(cond, MaltreatmentCondition)


# ─── _check_overcoming ──────────────────────────────────────────────────────

def test_overcoming_dexter_square():
    """Malefic in 10th sign from planet = Overcoming."""
    # Moon at 0° Cancer (idx=3), 10th sign from Cancer = Aries (idx=0+9=12%12=12→0? No: 3+9=12%12=0=Aries)
    # Actually (3+9)%12 = 0 = Aries. So malefic at Aries.
    chart = _make_chart([
        (PlanetName.SUN, 100.0, 1.0),
        (PlanetName.MOON, 100.0, 13.0),  # Cancer (idx 3)
        (PlanetName.MARS, 5.0, 0.5),     # Aries (idx 0) — 10th sign from Cancer
        (PlanetName.SATURN, 300.0, 0.03),
        (PlanetName.JUPITER, 60.0, 0.08),
        (PlanetName.VENUS, 230.0, 1.0),
    ])
    moon = chart.planets[1]
    result = KakosisEngine._check_overcoming(moon, chart, Sect.DAY)
    mars_overcome = [c for c in result if c.malefic == PlanetName.MARS]
    assert len(mars_overcome) == 1
    assert "Overcome" in mars_overcome[0].description


# ─── _check_opposition ──────────────────────────────────────────────────────

def test_opposition_malefic():
    """Malefic in 7th sign from planet = Opposition."""
    # Moon at 0° Aries (idx=0), 7th sign = Libra (idx=6). Saturn at 185° Libra.
    chart = _make_chart([
        (PlanetName.SUN, 100.0, 1.0),
        (PlanetName.MOON, 5.0, 13.0),     # Aries
        (PlanetName.SATURN, 185.0, 0.03),  # Libra — opposing Aries
        (PlanetName.MARS, 300.0, 0.5),
        (PlanetName.JUPITER, 60.0, 0.08),
        (PlanetName.VENUS, 230.0, 1.0),
    ])
    moon = chart.planets[1]
    result = KakosisEngine._check_opposition(moon, chart, Sect.NIGHT)
    assert len(result) >= 1
    assert result[0].type == "Opposition"


# ─── _check_striking_ray ────────────────────────────────────────────────────

def test_striking_ray_tight_square():
    """Malefic within 3° of exact square = Striking with a Ray."""
    # Moon at 0°, Mars at 91° → square orb = 1°
    chart = _make_chart([
        (PlanetName.SUN, 100.0, 1.0),
        (PlanetName.MOON, 0.0, 13.0),
        (PlanetName.MARS, 91.0, 0.5),  # 1° from exact square
        (PlanetName.SATURN, 200.0, 0.03),
        (PlanetName.JUPITER, 60.0, 0.08),
        (PlanetName.VENUS, 230.0, 1.0),
    ])
    moon = chart.planets[1]
    result = KakosisEngine._check_striking_ray(moon, chart, Sect.DAY)
    mars_strikes = [c for c in result if c.malefic == PlanetName.MARS]
    assert len(mars_strikes) == 1
    assert "Struck" in mars_strikes[0].description


# ─── _check_adherence ────────────────────────────────────────────────────────

def test_adherence_applying_conjunction():
    """Planet applying to tight conjunction with malefic = Adherence."""
    # Moon at 88° (applying to Saturn at 90°, within 3°, Moon faster)
    chart = _make_chart([
        (PlanetName.SUN, 100.0, 1.0),
        (PlanetName.MOON, 88.0, 13.0),
        (PlanetName.SATURN, 90.0, 0.03),
        (PlanetName.MARS, 200.0, 0.5),
        (PlanetName.JUPITER, 60.0, 0.08),
        (PlanetName.VENUS, 230.0, 1.0),
    ])
    moon = chart.planets[1]
    result = KakosisEngine._check_adherence(moon, chart, Sect.DAY)
    adherence = [c for c in result if c.malefic == PlanetName.SATURN]
    assert len(adherence) == 1
    assert "Adhering" in adherence[0].description


# ─── _check_besiegement ─────────────────────────────────────────────────────

def test_besiegement_between_malefics():
    """Planet between Mars and Saturn within tight span = Besiegement."""
    # Moon at 95°, Mars at 90°, Saturn at 100°. Span = 5+5=10 < 15
    chart = _make_chart([
        (PlanetName.SUN, 200.0, 1.0),
        (PlanetName.MOON, 95.0, 13.0),
        (PlanetName.MARS, 90.0, 0.5),
        (PlanetName.SATURN, 100.0, 0.03),
        (PlanetName.JUPITER, 60.0, 0.08),
        (PlanetName.VENUS, 230.0, 1.0),
    ])
    moon = chart.planets[1]
    result = KakosisEngine._check_besiegement(moon, chart, Sect.DAY)
    assert len(result) == 1
    assert "Besieged" in result[0].description


# ─── _apply_intervention ────────────────────────────────────────────────────

def test_intervention_reduces_severity():
    """Benefic aspecting the victim should reduce severity."""
    chart = _make_chart([
        (PlanetName.SUN, 200.0, 1.0),
        (PlanetName.MOON, 95.0, 13.0),
        (PlanetName.MARS, 90.0, 0.5),
        (PlanetName.SATURN, 100.0, 0.03),
        (PlanetName.JUPITER, 95.0, 0.08),  # Jupiter conjunct Moon — intervention!
        (PlanetName.VENUS, 230.0, 1.0),
    ])
    moon = chart.planets[1]
    conditions = [MaltreatmentCondition("Besiegement", PlanetName.SATURN, "Besieged.", 10)]
    result = KakosisEngine._apply_intervention(moon, chart, conditions)
    assert result[0].severity < 10
    assert "Mitigated" in result[0].description


def test_intervention_no_benefic():
    """No benefic = no mitigation."""
    chart = _make_chart([
        (PlanetName.SUN, 200.0, 1.0),
        (PlanetName.MOON, 95.0, 13.0),
        (PlanetName.MARS, 90.0, 0.5),
        (PlanetName.SATURN, 100.0, 0.03),
    ])
    moon = chart.planets[1]
    conditions = [MaltreatmentCondition("Besiegement", PlanetName.SATURN, "Besieged.", 10)]
    result = KakosisEngine._apply_intervention(moon, chart, conditions)
    assert result[0].severity == 10


def test_intervention_empty_conditions():
    chart = _make_chart([(PlanetName.SUN, 100.0, 1.0)])
    result = KakosisEngine._apply_intervention(chart.planets[0], chart, [])
    assert result == []


# ─── MaltreatmentCondition dataclass ─────────────────────────────────────────

def test_maltreatment_condition_dataclass():
    cond = MaltreatmentCondition("Overcoming", PlanetName.MARS, "Test", 8)
    assert cond.type == "Overcoming"
    assert cond.malefic == PlanetName.MARS
    assert cond.severity == 8
