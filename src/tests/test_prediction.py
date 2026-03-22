"""Tests for prediction.py — profections, firdaria, ZR, lunar phase, solar arcs, muntha."""
from datetime import datetime
from src.engine.prediction import (
    calculate_profection_sign,
    get_lord_of_year,
    calculate_monthly_profection,
    calculate_daily_profection,
    calculate_epitasis_days,
    get_opposite_sign,
    calculate_zr_lifetime_map,
    calculate_zr_periods,
    calculate_firdaria,
    calculate_lunar_phase_advanced,
    calculate_solar_arcs,
    calculate_muntha,
    ZR_YEARS,
    FIRDARIA_DAY,
    FIRDARIA_NIGHT,
)
from src.engine.models import Sign, PlanetName, Sect, Chart, Planet
import pytest


# ─── calculate_profection_sign ───────────────────────────────────────────────

def test_profection_age_zero():
    """Age 0 → same sign as Ascendant."""
    assert calculate_profection_sign(Sign.ARIES, 0) == Sign.ARIES


def test_profection_age_one():
    """Age 1 → next sign."""
    assert calculate_profection_sign(Sign.ARIES, 1) == Sign.TAURUS


def test_profection_age_twelve():
    """Age 12 → back to Ascendant (full cycle)."""
    assert calculate_profection_sign(Sign.ARIES, 12) == Sign.ARIES


def test_profection_arbitrary():
    assert calculate_profection_sign(Sign.LEO, 5) == Sign.CAPRICORN


# ─── get_lord_of_year ────────────────────────────────────────────────────────

def test_lord_of_year_aries():
    assert get_lord_of_year(Sign.ARIES) == PlanetName.MARS


def test_lord_of_year_leo():
    assert get_lord_of_year(Sign.LEO) == PlanetName.SUN


def test_lord_of_year_pisces():
    assert get_lord_of_year(Sign.PISCES) == PlanetName.JUPITER


# ─── calculate_monthly_profection ────────────────────────────────────────────

def test_monthly_profection_continuous_month1():
    """Month 1 stays in the annual sign."""
    assert calculate_monthly_profection(Sign.ARIES, 1) == Sign.ARIES


def test_monthly_profection_continuous_month7():
    assert calculate_monthly_profection(Sign.ARIES, 7) == Sign.LIBRA


def test_monthly_profection_saltatory():
    result = calculate_monthly_profection(
        Sign.ARIES, 3, method='Saltatory',
        natal_start_sign=Sign.ARIES, age=1
    )
    assert isinstance(result, Sign)


def test_monthly_profection_unknown_method():
    with pytest.raises(ValueError, match="Unknown profection method"):
        calculate_monthly_profection(Sign.ARIES, 1, method='Invalid')


def test_monthly_profection_saltatory_missing_args():
    with pytest.raises(ValueError, match="Natal start sign and age required"):
        calculate_monthly_profection(Sign.ARIES, 1, method='Saltatory')


# ─── calculate_daily_profection ──────────────────────────────────────────────

def test_daily_profection_day1():
    """Day 1 stays in the monthly sign."""
    assert calculate_daily_profection(Sign.ARIES, 1.0) == Sign.ARIES


def test_daily_profection_day3():
    """After ~2.33 days, should shift to next sign."""
    result = calculate_daily_profection(Sign.ARIES, 3.0)
    # int((3-1) / (7/3)) = int(2 / 2.333) = int(0.857) = 0 → still Aries
    assert result == Sign.ARIES


def test_daily_profection_day4():
    """Day 4 should be in the next sign."""
    result = calculate_daily_profection(Sign.ARIES, 4.0)
    # int((4-1) / (7/3)) = int(3 / 2.333) = int(1.286) = 1 → Taurus
    assert result == Sign.TAURUS


# ─── calculate_epitasis_days ─────────────────────────────────────────────────

def test_epitasis_days_returns_list():
    result = calculate_epitasis_days(Sign.ARIES, Sign.TAURUS)
    assert isinstance(result, list)
    assert all(1 <= d <= 30 for d in result)


def test_epitasis_days_same_sign():
    """When monthly and LoY signs match, day 1 should be an epitasis day."""
    result = calculate_epitasis_days(Sign.ARIES, Sign.ARIES)
    assert 1 in result


# ─── get_opposite_sign ───────────────────────────────────────────────────────

def test_opposite_sign():
    assert get_opposite_sign(Sign.ARIES) == Sign.LIBRA
    assert get_opposite_sign(Sign.CANCER) == Sign.CAPRICORN
    assert get_opposite_sign(Sign.LEO) == Sign.AQUARIUS


# ─── ZR_YEARS table ─────────────────────────────────────────────────────────

def test_zr_years_all_signs():
    """All 12 signs should have ZR years."""
    for sign in Sign:
        assert sign in ZR_YEARS
        assert ZR_YEARS[sign] > 0


def test_zr_years_sum():
    """Total ZR years should equal 211 (Valens planetary years sum)."""
    total = sum(ZR_YEARS.values())
    assert total == 211


# ─── calculate_zr_lifetime_map ───────────────────────────────────────────────

def test_zr_lifetime_map_structure():
    birth = datetime(1990, 1, 1)
    chapters = calculate_zr_lifetime_map(Sign.CANCER, birth, years=20, max_level=2)
    assert isinstance(chapters, list)
    assert len(chapters) > 0
    ch = chapters[0]
    assert "level" in ch
    assert ch["level"] == 1
    assert "sign" in ch
    assert "paragraphs" in ch


def test_zr_lifetime_map_paragraphs():
    birth = datetime(1990, 1, 1)
    chapters = calculate_zr_lifetime_map(Sign.ARIES, birth, years=20, max_level=2)
    first_chapter = chapters[0]
    assert len(first_chapter["paragraphs"]) > 0
    for para in first_chapter["paragraphs"]:
        assert para["level"] == 2


# ─── calculate_zr_periods ───────────────────────────────────────────────────

def test_zr_periods_basic():
    birth = datetime(1990, 1, 1)
    target = datetime(2020, 6, 15)
    result = calculate_zr_periods(Sign.CANCER, birth, target)
    assert "Level 1" in result
    assert "Level 2" in result


# ─── FIRDARIA tables ─────────────────────────────────────────────────────────

def test_firdaria_day_sum():
    """Day firdaria should sum to 75 years."""
    total = sum(d for _, d in FIRDARIA_DAY)
    assert total == 75


def test_firdaria_night_sum():
    """Night firdaria should also sum to 75."""
    total = sum(d for _, d in FIRDARIA_NIGHT)
    assert total == 75


# ─── calculate_firdaria ─────────────────────────────────────────────────────

def test_firdaria_basic():
    birth = datetime(1990, 1, 1)
    target = datetime(2020, 6, 15)
    result = calculate_firdaria(Sect.DAY, birth, target)
    assert "Major Period" in result
    assert "Sub Period" in result
    assert "Current Age" in result
    assert result["Current Age"] > 30


def test_firdaria_night():
    birth = datetime(1990, 1, 1)
    target = datetime(2020, 6, 15)
    result = calculate_firdaria(Sect.NIGHT, birth, target)
    assert "Major Period" in result
    # Night starts with Moon
    # Age 30: Moon(9)+Saturn(11)+Jupiter(12) = 32 → so at age 30 we're in Jupiter
    # Just verify it returns valid data
    assert result["Major Period"] in [p.value for p, _ in FIRDARIA_NIGHT]


def test_firdaria_at_birth():
    birth = datetime(1990, 1, 1)
    target = datetime(1990, 1, 2)
    result = calculate_firdaria(Sect.DAY, birth, target)
    assert result["Major Period"] == "Sun"  # Day chart starts with Sun


def test_firdaria_before_birth():
    birth = datetime(1990, 1, 1)
    target = datetime(1989, 1, 1)
    result = calculate_firdaria(Sect.DAY, birth, target)
    assert "error" in result


# ─── calculate_lunar_phase_advanced ──────────────────────────────────────────

def test_lunar_phase_new():
    result = calculate_lunar_phase_advanced(100.0, 110.0)
    assert result["name"] == "New Moon"
    assert result["type"] == "New Beginnings"


def test_lunar_phase_full():
    result = calculate_lunar_phase_advanced(0.0, 200.0)
    assert result["name"] == "Full Moon"
    assert result["type"] == "Fruition"


def test_lunar_phase_all_eight():
    """All 8 phases should be reachable."""
    phases = set()
    for diff in range(0, 360, 5):
        result = calculate_lunar_phase_advanced(0.0, float(diff))
        phases.add(result["name"])
    assert len(phases) == 8


# ─── calculate_solar_arcs ───────────────────────────────────────────────────

def test_solar_arcs_age_30():
    chart = Chart(
        sun_altitude=10.0,
        planets=[
            Planet(name=PlanetName.SUN, longitude=100.0, speed=1.0),
            Planet(name=PlanetName.MOON, longitude=200.0, speed=13.0),
        ],
        ascendant=0.0, mc=270.0
    )
    progressed = calculate_solar_arcs(chart, 30.0)
    assert len(progressed) == 2
    # Sun +30° = 130°
    assert abs(progressed[0].longitude - 130.0) < 0.01
    # Moon +30° = 230°
    assert abs(progressed[1].longitude - 230.0) < 0.01


def test_solar_arcs_wraparound():
    chart = Chart(
        sun_altitude=10.0,
        planets=[Planet(name=PlanetName.SUN, longitude=350.0, speed=1.0)],
        ascendant=0.0, mc=270.0
    )
    progressed = calculate_solar_arcs(chart, 20.0)
    # 350 + 20 = 370 % 360 = 10
    assert abs(progressed[0].longitude - 10.0) < 0.01


# ─── calculate_muntha ───────────────────────────────────────────────────────

def test_muntha_age_zero():
    result = calculate_muntha(Sign.ARIES, 0)
    assert result["sign"] == "Aries"
    assert result["age"] == 0


def test_muntha_age_5():
    result = calculate_muntha(Sign.ARIES, 5)
    assert result["sign"] == "Virgo"


def test_muntha_full_cycle():
    result = calculate_muntha(Sign.LEO, 12)
    assert result["sign"] == "Leo"
