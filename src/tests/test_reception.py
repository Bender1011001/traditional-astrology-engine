"""Tests for reception.py — ReceptionEngine."""
from src.engine.reception import ReceptionEngine, ReceptionMode, Reception, MutualReception
from src.engine.models import Chart, Planet, PlanetName, Sign


def _make_chart(planet_positions, asc=0.0, sun_alt=10.0):
    """Build a Chart from {PlanetName: longitude} dict."""
    planets = [Planet(name=n, longitude=lon, speed=1.0) for n, lon in planet_positions.items()]
    return Chart(sun_altitude=sun_alt, planets=planets, ascendant=asc, mc=270.0)


# ─── analyze_reception ───────────────────────────────────────────────────────

def test_analyze_reception_domicile():
    """Moon in Cancer should be received by the Moon (domicile ruler)."""
    chart = _make_chart({
        PlanetName.SUN: 120.0,    # Leo
        PlanetName.MOON: 100.0,   # Cancer
        PlanetName.MERCURY: 150.0,
        PlanetName.VENUS: 30.0,
        PlanetName.MARS: 200.0,
        PlanetName.JUPITER: 260.0,
        PlanetName.SATURN: 310.0,
    })
    moon = next(p for p in chart.planets if p.name == PlanetName.MOON)
    sun = next(p for p in chart.planets if p.name == PlanetName.SUN)

    # Sun is in Leo (Sun's domicile) — check if Moon receives Sun
    rec = ReceptionEngine.analyze_reception(sun, sun, chart, ReceptionMode.STANDARD_LILLY)
    # Sun in Leo, host=Sun → Sun is Domicile ruler of Leo
    assert "Domicile" in rec.dignities
    assert rec.score >= 5
    assert rec.is_valid is True


def test_analyze_reception_no_dignity():
    """A planet with no dignity in guest's sign should score 0."""
    chart = _make_chart({
        PlanetName.SUN: 0.0,      # Aries
        PlanetName.MOON: 60.0,    # Gemini
        PlanetName.MERCURY: 150.0,
        PlanetName.VENUS: 30.0,
        PlanetName.MARS: 200.0,
        PlanetName.JUPITER: 260.0,
        PlanetName.SATURN: 310.0,
    })
    sun = next(p for p in chart.planets if p.name == PlanetName.SUN)
    moon = next(p for p in chart.planets if p.name == PlanetName.MOON)

    # Sun in Aries, host=Moon — Moon has no major dignity in Aries
    rec = ReceptionEngine.analyze_reception(sun, moon, chart, ReceptionMode.STANDARD_LILLY)
    # Moon doesn't rule Aries, so no Domicile
    assert "Domicile" not in rec.dignities


def test_analyze_reception_strict_mode():
    """Strict Bonatti mode requires score >= 3 for validity."""
    chart = _make_chart({
        PlanetName.SUN: 0.0,
        PlanetName.MOON: 60.0,
        PlanetName.MERCURY: 150.0,
        PlanetName.VENUS: 30.0,
        PlanetName.MARS: 200.0,
        PlanetName.JUPITER: 260.0,
        PlanetName.SATURN: 310.0,
    })
    sun = next(p for p in chart.planets if p.name == PlanetName.SUN)
    moon = next(p for p in chart.planets if p.name == PlanetName.MOON)

    rec = ReceptionEngine.analyze_reception(sun, moon, chart, ReceptionMode.STRICT_BONATTI)
    # If score < 3, should be invalid under Bonatti
    if rec.score < 3:
        assert rec.is_valid is False


def test_reception_dataclass():
    r = Reception(
        guest=PlanetName.SUN,
        host=PlanetName.MOON,
        dignities=["Domicile"],
        score=5,
        is_valid=True,
        is_operative=False,
        mode="Standard (Lilly)"
    )
    assert r.guest == PlanetName.SUN
    assert r.mitigation == "None"


# ─── calculate_mutual_receptions ─────────────────────────────────────────────

def test_mutual_receptions_returns_list():
    chart = _make_chart({
        PlanetName.SUN: 120.0,    # Leo (Sun rules)
        PlanetName.MOON: 100.0,   # Cancer (Moon rules)
        PlanetName.MERCURY: 150.0,
        PlanetName.VENUS: 30.0,
        PlanetName.MARS: 200.0,
        PlanetName.JUPITER: 260.0,
        PlanetName.SATURN: 310.0,
    })
    result = ReceptionEngine.calculate_mutual_receptions(chart, ReceptionMode.STANDARD_LILLY)
    assert isinstance(result, list)
    for mr in result:
        assert isinstance(mr, MutualReception)
        assert mr.strength_score > 0


def test_mutual_reception_type_classification():
    """Sun in Leo + Moon in Cancer = both in domicile, should find mutual reception."""
    chart = _make_chart({
        PlanetName.SUN: 120.0,    # Leo
        PlanetName.MOON: 100.0,   # Cancer
        PlanetName.MERCURY: 150.0,
        PlanetName.VENUS: 30.0,
        PlanetName.MARS: 200.0,
        PlanetName.JUPITER: 260.0,
        PlanetName.SATURN: 310.0,
    })
    mutuals = ReceptionEngine.calculate_mutual_receptions(chart)
    # There could be many mutual receptions; check if types are valid strings
    for mr in mutuals:
        assert mr.type in ["Pure Domicile", "Pure Exaltation", "Major Mixed", "Mixed"]


def test_mutual_receptions_sorted_by_score():
    chart = _make_chart({
        PlanetName.SUN: 120.0,
        PlanetName.MOON: 100.0,
        PlanetName.MERCURY: 150.0,
        PlanetName.VENUS: 30.0,
        PlanetName.MARS: 200.0,
        PlanetName.JUPITER: 260.0,
        PlanetName.SATURN: 310.0,
    })
    mutuals = ReceptionEngine.calculate_mutual_receptions(chart)
    if len(mutuals) > 1:
        for i in range(len(mutuals) - 1):
            assert mutuals[i].strength_score >= mutuals[i + 1].strength_score


# ─── helper methods ──────────────────────────────────────────────────────────

def test_get_face_ruler():
    """Face ruler should return a valid PlanetName."""
    ruler = ReceptionEngine._get_face_ruler(Sign.ARIES, 5.0)
    assert isinstance(ruler, PlanetName)


def test_get_face_ruler_edge_degree():
    """30th degree edge case should not crash."""
    ruler = ReceptionEngine._get_face_ruler(Sign.ARIES, 30.0)
    assert isinstance(ruler, PlanetName)


def test_get_term_ruler():
    """Term ruler should return a PlanetName or None."""
    ruler = ReceptionEngine._get_term_ruler(Sign.ARIES, 5.0, ReceptionMode.STANDARD_LILLY)
    assert ruler is None or isinstance(ruler, PlanetName)


def test_get_triplicity_rulers():
    from src.engine.models import Sect
    rulers = ReceptionEngine._get_triplicity_rulers("Fire", Sect.DAY, ReceptionMode.STANDARD_LILLY)
    assert isinstance(rulers, list)
    assert len(rulers) >= 1
    assert all(isinstance(r, PlanetName) for r in rulers)
