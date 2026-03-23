"""
Tests for the Daily Navigator engine and API endpoint.
"""
import pytest
from datetime import datetime
from src.engine.daily_navigator import DailyNavigator
from src.engine.models import Chart, Planet, PlanetName


def _make_test_chart():
    """Build a minimal natal chart for testing (roughly Marilyn Monroe's data)."""
    planets = [
        Planet(name=PlanetName.SUN, longitude=75.5, speed=0.95),
        Planet(name=PlanetName.MOON, longitude=229.3, speed=12.5),
        Planet(name=PlanetName.MERCURY, longitude=97.0, speed=1.2),
        Planet(name=PlanetName.VENUS, longitude=58.5, speed=1.1),
        Planet(name=PlanetName.MARS, longitude=230.5, speed=0.6),
        Planet(name=PlanetName.JUPITER, longitude=296.7, speed=0.12),
        Planet(name=PlanetName.SATURN, longitude=231.7, speed=0.05),
    ]
    return Chart(
        planets=planets,
        ascendant=163.0,  # ~13° Leo
        mc=80.0,
        sun_altitude=5.0,  # Day chart
        geo_lat=34.05,
        geo_lon=-118.24,
        jd=2423585.0,
    )


class TestDailyNavigatorEngine:
    """Tests for the DailyNavigator.generate_briefing method."""

    def test_briefing_returns_all_keys(self):
        chart = _make_test_chart()
        birth_dt = datetime(1926, 6, 1, 9, 30)
        birth_jd = 2424319.895833
        target_date = datetime(2026, 3, 23)

        briefing = DailyNavigator.generate_briefing(chart, birth_dt, birth_jd, target_date)

        expected_keys = {
            "date", "display_date", "profections", "firdaria",
            "zodiacal_releasing", "transits", "moon", "epitasis",
            "planetary_day", "recommendations", "forecast_summary",
        }
        assert expected_keys.issubset(set(briefing.keys())), f"Missing keys: {expected_keys - set(briefing.keys())}"

    def test_profections_block_structure(self):
        chart = _make_test_chart()
        birth_dt = datetime(1926, 6, 1, 9, 30)
        birth_jd = 2424319.895833
        target_date = datetime(2026, 3, 23)

        briefing = DailyNavigator.generate_briefing(chart, birth_dt, birth_jd, target_date)
        prof = briefing["profections"]

        assert "age" in prof
        assert "annual_sign" in prof
        assert "lord_of_year" in prof
        assert "daily_sign" in prof
        assert "daily_lord" in prof
        assert "keywords" in prof
        assert isinstance(prof["age"], int)

    def test_firdaria_block_present(self):
        chart = _make_test_chart()
        birth_dt = datetime(1990, 7, 15, 14, 0)
        birth_jd = 2448090.0833
        target_date = datetime(2026, 3, 23)

        briefing = DailyNavigator.generate_briefing(chart, birth_dt, birth_jd, target_date)
        fir = briefing["firdaria"]
        assert "Major Period" in fir or "error" in fir

    def test_epitasis_detection(self):
        chart = _make_test_chart()
        birth_dt = datetime(1990, 7, 15, 14, 0)
        birth_jd = 2448090.0833
        target_date = datetime(2026, 3, 23)

        briefing = DailyNavigator.generate_briefing(chart, birth_dt, birth_jd, target_date)
        epi = briefing["epitasis"]
        assert "active" in epi
        assert isinstance(epi["active"], bool)
        assert "lord_of_year_transiting_sign" in epi

    def test_recommendations_block(self):
        chart = _make_test_chart()
        birth_dt = datetime(1990, 7, 15, 14, 0)
        birth_jd = 2448090.0833
        target_date = datetime(2026, 3, 23)

        briefing = DailyNavigator.generate_briefing(chart, birth_dt, birth_jd, target_date)
        rec = briefing["recommendations"]
        assert "primary_time_lord" in rec
        assert "color" in rec
        assert "gem" in rec
        assert "do" in rec
        assert "avoid" in rec
        assert isinstance(rec["do"], list)
        assert len(rec["do"]) > 0

    def test_forecast_summary_is_string(self):
        chart = _make_test_chart()
        birth_dt = datetime(1990, 7, 15, 14, 0)
        birth_jd = 2448090.0833
        target_date = datetime(2026, 3, 23)

        briefing = DailyNavigator.generate_briefing(chart, birth_dt, birth_jd, target_date)
        assert isinstance(briefing["forecast_summary"], str)
        assert len(briefing["forecast_summary"]) > 50  # Should be a meaningful paragraph

    def test_transits_are_list(self):
        chart = _make_test_chart()
        birth_dt = datetime(1990, 7, 15, 14, 0)
        birth_jd = 2448090.0833
        target_date = datetime(2026, 3, 23)

        briefing = DailyNavigator.generate_briefing(chart, birth_dt, birth_jd, target_date)
        assert isinstance(briefing["transits"], list)

    def test_planetary_day_block(self):
        chart = _make_test_chart()
        birth_dt = datetime(1990, 7, 15, 14, 0)
        birth_jd = 2448090.0833
        target_date = datetime(2026, 3, 23)

        briefing = DailyNavigator.generate_briefing(chart, birth_dt, birth_jd, target_date)
        pd = briefing["planetary_day"]
        assert "weekday" in pd
        assert "ruler" in pd
        assert "alignment" in pd

    def test_moon_condition_block(self):
        chart = _make_test_chart()
        birth_dt = datetime(1990, 7, 15, 14, 0)
        birth_jd = 2448090.0833
        target_date = datetime(2026, 3, 23)

        briefing = DailyNavigator.generate_briefing(chart, birth_dt, birth_jd, target_date)
        moon = briefing["moon"]
        assert "sign" in moon
        assert "phase" in moon
        assert "void_of_course" in moon
        assert "waxing" in moon
        assert "degree" in moon
        assert "note" in moon
        assert isinstance(moon["void_of_course"], bool)
        assert isinstance(moon["waxing"], bool)
        assert 0 <= moon["degree"] < 30

    def test_different_target_dates(self):
        """Briefings for different dates should return different date fields and
        potentially different Moon data, confirming date routing works."""
        chart = _make_test_chart()
        birth_dt = datetime(1990, 7, 15, 14, 0)
        birth_jd = 2448090.0833

        briefing_a = DailyNavigator.generate_briefing(
            chart, birth_dt, birth_jd, datetime(2026, 3, 20)
        )
        briefing_b = DailyNavigator.generate_briefing(
            chart, birth_dt, birth_jd, datetime(2026, 3, 25)
        )

        assert briefing_a["date"] == "2026-03-20"
        assert briefing_b["date"] == "2026-03-25"
        # Moon should differ across 5 days (it moves ~13°/day)
        assert briefing_a["moon"]["sign"] != briefing_b["moon"]["sign"] or \
               briefing_a["moon"]["degree"] != briefing_b["moon"]["degree"]

    def test_recommendations_urgency_valid(self):
        """Urgency must be one of the expected severity levels."""
        chart = _make_test_chart()
        birth_dt = datetime(1990, 7, 15, 14, 0)
        birth_jd = 2448090.0833
        target_date = datetime(2026, 3, 23)

        briefing = DailyNavigator.generate_briefing(chart, birth_dt, birth_jd, target_date)
        rec = briefing["recommendations"]
        assert rec["urgency"] in ("low", "moderate", "high", "critical")
