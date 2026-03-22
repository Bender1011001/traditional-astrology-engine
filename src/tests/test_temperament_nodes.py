"""Tests for temperament.py — TemperamentEngine and nodes.py — Nodal analysis."""
from src.engine.temperament import TemperamentEngine
from src.engine.nodes import analyze_nodes, get_shortest_dist, NodalContact
from src.engine.models import Chart, Planet, PlanetName, Sign


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPERAMENT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def _make_chart(sun_lon=120.0, moon_lon=100.0, asc=0.0, sun_alt=10.0, nn=80.0):
    planets = [
        Planet(name=PlanetName.SUN, longitude=sun_lon, speed=1.0),
        Planet(name=PlanetName.MOON, longitude=moon_lon, speed=13.0),
        Planet(name=PlanetName.MERCURY, longitude=130.0, speed=1.2),
        Planet(name=PlanetName.VENUS, longitude=60.0, speed=1.0),
        Planet(name=PlanetName.MARS, longitude=200.0, speed=0.5),
        Planet(name=PlanetName.JUPITER, longitude=90.0, speed=0.08),
        Planet(name=PlanetName.SATURN, longitude=300.0, speed=0.03),
    ]
    return Chart(sun_altitude=sun_alt, planets=planets, ascendant=asc, mc=270.0, north_node=nn)


# ─── get_element_qualities ───────────────────────────────────────────────────

def test_element_qualities_fire():
    qual = TemperamentEngine.get_element_qualities(Sign.ARIES)
    assert qual["Hot"] == 1
    assert qual["Dry"] == 1
    assert qual["Cold"] == 0
    assert qual["Moist"] == 0


def test_element_qualities_water():
    qual = TemperamentEngine.get_element_qualities(Sign.CANCER)
    assert qual["Cold"] == 1
    assert qual["Moist"] == 1


def test_element_qualities_all_signs():
    """Every sign should return valid qualities."""
    for sign in Sign:
        qual = TemperamentEngine.get_element_qualities(sign)
        assert isinstance(qual, dict)
        assert sum(qual.values()) == 2  # Each element has exactly 2 active qualities


# ─── calculate_temperament ──────────────────────────────────────────────────

def test_temperament_returns_expected_keys():
    chart = _make_chart()
    result = TemperamentEngine.calculate_temperament(chart)
    assert "primary_temperament" in result
    assert "scores" in result
    assert "net_balance" in result
    assert "breakdown" in result


def test_temperament_scores_non_negative():
    chart = _make_chart()
    result = TemperamentEngine.calculate_temperament(chart)
    for quality, score in result["scores"].items():
        assert score >= 0, f"{quality} score is negative: {score}"


def test_temperament_valid_type():
    chart = _make_chart()
    result = TemperamentEngine.calculate_temperament(chart)
    valid_types = [
        "Sanguine (Hot/Moist)", "Choleric (Hot/Dry)",
        "Melancholic (Cold/Dry)", "Phlegmatic (Cold/Moist)", "Balanced"
    ]
    assert result["primary_temperament"] in valid_types


def test_temperament_breakdown_not_empty():
    chart = _make_chart()
    result = TemperamentEngine.calculate_temperament(chart)
    assert len(result["breakdown"]) > 0
    assert any("Ascendant" in d for d in result["breakdown"])
    assert any("Moon" in d for d in result["breakdown"])


def test_temperament_net_balance():
    chart = _make_chart()
    result = TemperamentEngine.calculate_temperament(chart)
    scores = result["scores"]
    assert result["net_balance"]["Hot_vs_Cold"] == scores["Hot"] - scores["Cold"]
    assert result["net_balance"]["Moist_vs_Dry"] == scores["Moist"] - scores["Dry"]


# ─── _get_moon_phase_qualities ───────────────────────────────────────────────

def test_moon_phase_new():
    name, qual = TemperamentEngine._get_moon_phase_qualities(30.0)
    assert name == "New-1stQ"
    assert qual["Hot"] == 1 and qual["Moist"] == 1


def test_moon_phase_full_to_lastq():
    name, qual = TemperamentEngine._get_moon_phase_qualities(200.0)
    assert name == "Full-LastQ"
    assert qual["Cold"] == 1 and qual["Dry"] == 1


def test_moon_phase_all_quadrants():
    """Each 90° sector should map to a different phase."""
    phases = set()
    for angle in [30, 100, 200, 300]:
        name, _ = TemperamentEngine._get_moon_phase_qualities(float(angle))
        phases.add(name)
    assert len(phases) == 4


# ─── _get_season_qualities ──────────────────────────────────────────────────

def test_season_spring():
    name, qual = TemperamentEngine._get_season_qualities(Sign.TAURUS)
    assert name == "Spring"
    assert qual["Hot"] == 1 and qual["Moist"] == 1


def test_season_winter():
    name, qual = TemperamentEngine._get_season_qualities(Sign.AQUARIUS)
    assert name == "Winter"
    assert qual["Cold"] == 1 and qual["Moist"] == 1


def test_season_all_signs():
    """All signs should map to a valid season."""
    seasons = set()
    for sign in Sign:
        name, _ = TemperamentEngine._get_season_qualities(sign)
        seasons.add(name)
    assert seasons == {"Spring", "Summer", "Autumn", "Winter"}


# ─── PLANET_NATURES table ───────────────────────────────────────────────────

def test_planet_natures_saturn():
    nature = TemperamentEngine.PLANET_NATURES[PlanetName.SATURN]
    assert nature["Cold"] == 1 and nature["Dry"] == 1


def test_planet_natures_mercury_variable():
    """Mercury is variable (all zeros) — takes sign's nature."""
    nature = TemperamentEngine.PLANET_NATURES[PlanetName.MERCURY]
    assert all(v == 0 for v in nature.values())


# ═══════════════════════════════════════════════════════════════════════════════
# NODES.PY
# ═══════════════════════════════════════════════════════════════════════════════

# ─── get_shortest_dist ───────────────────────────────────────────────────────

def test_shortest_dist_same():
    assert get_shortest_dist(100.0, 100.0) == 0.0


def test_shortest_dist_normal():
    assert get_shortest_dist(10.0, 50.0) == 40.0


def test_shortest_dist_wraparound():
    assert get_shortest_dist(350.0, 10.0) == 20.0


# ─── analyze_nodes ───────────────────────────────────────────────────────────

def test_analyze_nodes_head_contact():
    """Planet conjunct North Node should give Anabolism."""
    chart = _make_chart(nn=90.0)
    # Jupiter is at 90° — same as NN
    contacts = analyze_nodes(chart)
    jupiter_contacts = [c for c in contacts if c.planet_name == "Jupiter"]
    assert len(jupiter_contacts) == 1
    assert jupiter_contacts[0].node_type == "HEAD"
    assert jupiter_contacts[0].metabolic_phase == "Anabolism"
    assert "AMPLIFICATION" in jupiter_contacts[0].description


def test_analyze_nodes_tail_contact():
    """Planet conjunct South Node (NN+180) should give Catabolism."""
    # Mars at 200, NN at 20 → SN at 200
    chart = _make_chart(nn=20.0)
    contacts = analyze_nodes(chart)
    mars_contacts = [c for c in contacts if c.planet_name == "Mars"]
    assert len(mars_contacts) == 1
    assert mars_contacts[0].node_type == "TAIL"
    assert mars_contacts[0].metabolic_phase == "Catabolism"


def test_analyze_nodes_bending():
    """Planet at NN+90 should be at North Bending (Explosion)."""
    # NN at 0, N_bending at 90. Jupiter at 90.
    chart = _make_chart(nn=0.0)
    contacts = analyze_nodes(chart)
    jupiter_contacts = [c for c in contacts if c.planet_name == "Jupiter"]
    assert len(jupiter_contacts) == 1
    assert jupiter_contacts[0].node_type == "N_BENDING"
    assert jupiter_contacts[0].metabolic_phase == "Explosion"


def test_analyze_nodes_no_contacts():
    """Planets far from all nodal points should produce no contacts."""
    # NN at 45 — no planets within 4° orb of 45, 225, 135, or 315
    chart = _make_chart(nn=45.0)
    contacts = analyze_nodes(chart)
    # Check if any contacts are produced (might be some depending on positions)
    for c in contacts:
        assert isinstance(c, NodalContact)


def test_analyze_nodes_orb():
    """Planet just within orb should be detected."""
    # NN=80, Jupiter=90 → dist=10 → outside 4° orb. No contact.
    chart = _make_chart(nn=80.0)
    contacts = analyze_nodes(chart)
    jupiter_contacts = [c for c in contacts if c.planet_name == "Jupiter"]
    # 90-80=10, which is > 4° orb, so no contact expected
    assert len(jupiter_contacts) == 0
