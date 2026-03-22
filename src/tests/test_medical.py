"""Tests for medical.py — Traditional Iatromathematics and Surgery Rules."""
from unittest.mock import patch, MagicMock
from src.engine.medical import MedicalAstrology
from src.engine.models import Sign, Planet, PlanetName, Chart


def test_get_body_part_for_sign():
    """Sign to melothesia mapping should work correctly."""
    assert "Head" in MedicalAstrology.get_body_part_for_sign(Sign.ARIES)
    assert "Throat" in MedicalAstrology.get_body_part_for_sign(Sign.TAURUS)
    assert "Feet" in MedicalAstrology.get_body_part_for_sign(Sign.PISCES)
    assert "Unknown" == MedicalAstrology.get_body_part_for_sign("Not_A_Sign")


def test_check_moon_mercury_interference_exact_square():
    """Moon exactly square Mercury should warn of confusion/delirium."""
    result = MedicalAstrology.check_moon_mercury_interference(10.0, 100.0)
    assert result is not None
    assert "Diagnostic Confusion" in result["type"]
    assert "square" in result["condition"]


def test_check_moon_mercury_interference_exact_opposition():
    """Moon exactly opposite Mercury should warn of confusion."""
    result = MedicalAstrology.check_moon_mercury_interference(10.0, 185.0)  # Diff is 175 (within orb 8)
    assert result is not None
    assert "Diagnostic Confusion" in result["type"]
    assert "opposition" in result["condition"]


def test_check_moon_mercury_interference_no_aspect():
    """Moon trine Mercury (120 degrees) should not warn."""
    result = MedicalAstrology.check_moon_mercury_interference(10.0, 130.0)
    assert result is None


@patch("swisseph.calc_ut")
@patch("src.engine.mundane.get_recent_eclipses")
@patch("src.engine.medical.MedicalAstrology.calculate_critical_days")
def test_can_perform_surgery_safe(mock_calc_critical, mock_get_eclipses, mock_swe):
    """No rule violations should render surgery as safe."""
    chart = Chart(sun_altitude=10.0, planets=[], ascendant=0.0, mc=270.0)
    
    # Mocking SWISSEPH
    # Returns [lon, lat, dist, speed_lon, speed_lat, speed_dist] wrapped in a tuple
    def fake_swe_calc(jd, body, flags):
        if body == 1:  # swe.MOON
            return ([180.0, 0, 1, 13, 0, 0], 0)  # Moon at 0 Libra
        elif body == 4:  # swe.MARS
            return ([300.0, 0, 1, 1, 0, 0], 0)   # Mars non-aspect
        elif body == 6:  # swe.SATURN
            return ([30.0, 0, 1, 0, 0, 0], 0)    # Saturn non-aspect
        return ([0.0, 0, 1, 0, 0, 0], 0)
    
    mock_swe.side_effect = fake_swe_calc
    mock_get_eclipses.return_value = []
    mock_calc_critical.return_value = []

    res = MedicalAstrology.can_perform_surgery("Knees", 2460000.0, chart)
    
    assert res["safe"] is True
    assert len(res["reasons"]) == 0
    assert res["moon_sign"] == Sign.LIBRA.value
    assert res["target_body_part"] == "Knees"


@patch("swisseph.calc_ut")
@patch("src.engine.mundane.get_recent_eclipses")
def test_can_perform_surgery_unsafe_moon_sign(mock_get_eclipses, mock_swe):
    """Surgery on Knees when Moon is in Capricorn should be unsafe."""
    chart = Chart(sun_altitude=10.0, planets=[], ascendant=0.0, mc=270.0)
    
    def fake_swe_calc_capricorn(jd, body, flags):
        if body == 1:  # swe.MOON
            return ([280.0, 0, 1, 13, 0, 0], 0)  # Moon at 10 Capricorn
        elif body == 4:  # swe.MARS
            return ([90.0, 0, 1, 1, 0, 0], 0)   # Mars far
        elif body == 6:  # swe.SATURN
            return ([0.0, 0, 1, 0, 0, 0], 0)    # Saturn far
        return ([0.0, 0, 1, 0, 0, 0], 0)
    
    mock_swe.side_effect = fake_swe_calc_capricorn
    mock_get_eclipses.return_value = []

    res = MedicalAstrology.can_perform_surgery("Knees", 2460000.0, chart)
    
    assert res["safe"] is False
    assert len(res["reasons"]) == 1
    assert "Capricorn" in res["reasons"][0]


@patch("swisseph.calc_ut")
@patch("src.engine.mundane.get_recent_eclipses")
def test_can_perform_surgery_unsafe_affliction(mock_get_eclipses, mock_swe):
    """Surgery unsafe when Moon is conjunct Mars."""
    chart = Chart(sun_altitude=10.0, planets=[], ascendant=0.0, mc=270.0)
    
    def fake_swe_calc_conjunct(jd, body, flags):
        if body == 1:  # swe.MOON
            return ([50.0, 0, 1, 13, 0, 0], 0)
        elif body == 4:  # swe.MARS
            return ([52.0, 0, 1, 1, 0, 0], 0)   # Conjunct within 8 deg
        elif body == 6:  # swe.SATURN
            return ([0.0, 0, 1, 0, 0, 0], 0)
        return ([0.0, 0, 1, 0, 0, 0], 0)
    
    mock_swe.side_effect = fake_swe_calc_conjunct
    mock_get_eclipses.return_value = []

    res = MedicalAstrology.can_perform_surgery("Knees", 2460000.0, chart)
    
    assert res["safe"] is False
    assert any("Mars" in reason for reason in res["reasons"])


@patch("swisseph.calc_ut")
def test_calculate_remediation_window(mock_swe):
    """Testing remediation window identifies Mars/Saturn conjunctions with luminaries."""
    def fake_swe_mock(jd, body, flags):
        # Let's make Moon conjunct Mars every day.
        if body == 1:  # swe.MOON
            return ([10.0, 0, 1, 13, 0, 0], 0)
        elif body == 4:  # swe.MARS
            return ([12.0, 0, 1, 1, 0, 0], 0)
        return ([100.0, 0, 1, 0, 0, 0], 0)
        
    mock_swe.side_effect = fake_swe_mock
    
    windows = MedicalAstrology.calculate_remediation_window(2460000.0, duration_days=2)
    assert len(windows) == 2
    assert windows[0]["intensity"] >= 10
    assert any("conjunct" in r for r in windows[0]["reasons"])
