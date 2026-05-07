"""Tests for mundane.py helper functions and MundaneEngine core methods."""



from src.engine.models import Sign
from src.engine.mundane import (CHOROGRAPHY, SIGN_TO_TRI_NAME, MundaneEngine,
                                check_eclipse_impact)

# ─── check_eclipse_impact ────────────────────────────────────────────────────


def test_check_eclipse_impact_direct_hit():
    result = check_eclipse_impact(100.0, 101.5, orb=3.0)
    assert result is not None
    assert "DIRECT HIT" in result
    assert "1.50" in result


def test_check_eclipse_impact_exact():
    result = check_eclipse_impact(200.0, 200.0, orb=3.0)
    assert result is not None
    assert "0.00" in result


def test_check_eclipse_impact_miss():
    result = check_eclipse_impact(100.0, 110.0, orb=3.0)
    assert result is None


def test_check_eclipse_impact_wraparound():
    """Test that wrapping 0/360 boundary works."""
    result = check_eclipse_impact(358.0, 1.0, orb=5.0)
    assert result is not None
    assert "DIRECT HIT" in result


# ─── CHOROGRAPHY / SIGN mappings ─────────────────────────────────────────────


def test_chorography_all_elements():
    assert "Fire" in CHOROGRAPHY
    assert "Water" in CHOROGRAPHY
    assert "Air" in CHOROGRAPHY
    assert "Earth" in CHOROGRAPHY


def test_sign_to_triplicity_coverage():
    """Every sign should map to one of the four elements."""
    for sign in Sign:
        tri = SIGN_TO_TRI_NAME.get(sign)
        assert tri in {
            "Fire",
            "Water",
            "Air",
            "Earth",
        }, f"{sign} has no triplicity mapping"


# ─── MundaneEngine basic methods ─────────────────────────────────────────────


def test_mundane_engine_add_comet():
    engine = MundaneEngine(jd=2460000.0)
    engine.add_comet("Test Comet", "red", "East")
    assert len(engine.comets) == 1
    assert engine.comets[0]["name"] == "Test Comet"
    assert engine.comets[0]["classification"] == "Martial (War, Fire, Sudden Events)"
    assert "East" in engine.comets[0]["regional_effect"]


def test_mundane_engine_add_comet_saturnian():
    engine = MundaneEngine(jd=2460000.0)
    engine.add_comet("Dark Comet", "dark", "West")
    assert (
        engine.comets[0]["classification"]
        == "Saturnian (Pestilence, Cold, Structural Decay)"
    )


def test_mundane_engine_add_comet_jupiterian():
    engine = MundaneEngine(jd=2460000.0)
    engine.add_comet("Bright Comet", "yellow", "North")
    assert (
        engine.comets[0]["classification"]
        == "Jupiterian/Venusian (Religious/Social turnover)"
    )


def test_mundane_engine_add_comet_unknown():
    engine = MundaneEngine(jd=2460000.0)
    engine.add_comet("Weird Comet", "purple", "South")
    assert engine.comets[0]["classification"] == "Unknown"


def test_mundane_engine_world_firdaria():
    """World Firdaria should return a valid planet and positive duration."""
    engine = MundaneEngine(jd=2460000.0)
    result = engine.get_world_firdaria()
    assert "planet" in result
    assert result["duration"] == 75
    assert "start_jd" in result
    assert "end_jd" in result
    assert result["end_jd"] > result["start_jd"]


def test_mundane_engine_mighty_firdaria():
    """Mighty Firdaria should return a known planet ruler."""
    engine = MundaneEngine(jd=2460000.0)
    result = engine.get_mighty_firdaria()
    assert "ruler" in result
    valid_rulers = {"Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"}
    assert result["ruler"] in valid_rulers
    assert "years_into_period" in result
    assert "remaining_years" in result


def test_mundane_engine_aries_ingress():
    """Aries Ingress should find the Sun near 0° Aries."""
    engine = MundaneEngine(jd=2460000.0)
    result = engine.get_aries_ingress(2025)
    assert result["sign"] == "Aries"
    assert result["degree"] == 0.0
    assert "jd" in result
    # The Sun longitude should be very close to 0 (or 360)
    lon = result["longitude"]
    assert lon < 1.0 or lon > 359.0
