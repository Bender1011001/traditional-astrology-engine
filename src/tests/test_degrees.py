"""Tests for the degree-quality engine, asserting the real Lilly (1647) values.

Lilly works the Aries column explicitly on CA p.117-118, which lets us validate
the boundary encoding against his own prose:
  masc/fem: 1-8 M, 9 F, 10-15 M, 16-22 F, 23-30 M
  light/dark: 1-3 dark, 4-8 light, 9-16 dark, 17-20 light, 21-24 void, 25-29 light, 30 void
"""
from src.engine.degrees import DegreeQualityEngine as DQ


def _deg(sign_idx, one_based_degree):
    """Ecliptic longitude at the middle of a given one-based degree of a sign."""
    return sign_idx * 30 + (one_based_degree - 1) + 0.5


def test_one_based_conversion_and_sign():
    assert DQ.lookup(0.0)["degree_one_based"] == 1
    assert DQ.lookup(0.99)["degree_one_based"] == 1
    assert DQ.lookup(1.0)["degree_one_based"] == 2
    assert DQ.lookup(29.99)["degree_one_based"] == 30
    r = DQ.lookup(30.0)
    assert r["sign"] == "Taurus" and r["degree_one_based"] == 1


def test_aries_masc_fem_matches_lilly_prose():
    # 1-8 M, 9 F, 10-15 M, 16-22 F, 23-30 M
    assert DQ.lookup(_deg(0, 1))["masculine_feminine"] == "M"
    assert DQ.lookup(_deg(0, 8))["masculine_feminine"] == "M"
    assert DQ.lookup(_deg(0, 9))["masculine_feminine"] == "F"
    assert DQ.lookup(_deg(0, 15))["masculine_feminine"] == "M"
    assert DQ.lookup(_deg(0, 16))["masculine_feminine"] == "F"
    assert DQ.lookup(_deg(0, 22))["masculine_feminine"] == "F"
    assert DQ.lookup(_deg(0, 23))["masculine_feminine"] == "M"


def test_aries_light_dark_matches_lilly_prose():
    assert DQ.lookup(_deg(0, 1))["light_dark_smoky_void"] == "dark"
    assert DQ.lookup(_deg(0, 4))["light_dark_smoky_void"] == "light"
    assert DQ.lookup(_deg(0, 16))["light_dark_smoky_void"] == "dark"
    assert DQ.lookup(_deg(0, 20))["light_dark_smoky_void"] == "light"
    assert DQ.lookup(_deg(0, 24))["light_dark_smoky_void"] == "void"
    assert DQ.lookup(_deg(0, 29))["light_dark_smoky_void"] == "light"
    assert DQ.lookup(_deg(0, 30))["light_dark_smoky_void"] == "void"


def test_flag_columns():
    assert DQ.lookup(_deg(0, 6))["pitted"] is True        # Aries pitted incl. 6
    assert DQ.lookup(_deg(0, 7))["pitted"] is False
    assert DQ.lookup(_deg(0, 19))["increasing_fortune"] is True   # Aries 19
    # Azimene: Taurus 6-10 present; Aries & Pisces have none.
    assert DQ.lookup(_deg(1, 6))["azimene"] is True
    assert DQ.lookup(_deg(1, 10))["azimene"] is True
    assert DQ.lookup(_deg(1, 11))["azimene"] is False
    assert DQ.lookup(_deg(0, 6))["azimene"] is False
    assert DQ.lookup(_deg(11, 15))["azimene"] is False   # Pisces: no azimene


def test_data_present():
    assert DQ.has_data("lilly_1647") is True
    assert DQ.has_data("al_biruni") is False
    card = DQ.lookup(_deg(1, 6))   # Taurus deg 6: azimene
    assert card["data_available"] is True
    assert any("azimene" in n.lower() for n in card["interpretations"])
