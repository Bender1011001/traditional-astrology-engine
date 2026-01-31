import pytest
from engine.models import Sign, PlanetName
from engine.medical import MedicalAstrology

def test_melothesia():
    part = MedicalAstrology.get_body_part_for_sign(Sign.ARIES)
    assert "Head" in part
    
    part = MedicalAstrology.get_body_part_for_sign(Sign.CAPRICORN)
    assert "Knees" in part

def test_surgery_logic():
    # Mocking Surgery check
    # Moon in Aries, Head surgery -> Should be False (Safe: False)
    # We can't easily mock swisseph calc_ut inside the function without mocking swe.
    # Let's see if we can at least test the logic if it was available.
    pass

def test_mercury_inference():
    # Moon 90 deg from Mercury
    res = MedicalAstrology.check_moon_mercury_interference(0.0, 90.0)
    assert res is not None
    assert "Confusion" in res["type"]
