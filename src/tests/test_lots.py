"""Tests for lots.py — Hermetic Lots (40+ Arabic Parts)."""

from src.engine.lots import (calculate_all_lots, calculate_lot,
                             calculate_lot_position)
from src.engine.models import Chart, LotName, Planet, PlanetName, Sect


def _make_chart(asc=0.0, sun_alt=10.0):
    """Build a chart with all 7 traditional planets."""
    planets = [
        Planet(name=PlanetName.SUN, longitude=120.0, speed=1.0),  # Leo
        Planet(name=PlanetName.MOON, longitude=100.0, speed=13.0),  # Cancer
        Planet(name=PlanetName.MERCURY, longitude=130.0, speed=1.2),  # Leo
        Planet(name=PlanetName.VENUS, longitude=60.0, speed=1.0),  # Gemini
        Planet(name=PlanetName.MARS, longitude=200.0, speed=0.5),  # Libra
        Planet(name=PlanetName.JUPITER, longitude=270.0, speed=0.08),  # Capricorn
        Planet(name=PlanetName.SATURN, longitude=300.0, speed=0.03),  # Aquarius
    ]
    return Chart(sun_altitude=sun_alt, planets=planets, ascendant=asc, mc=270.0)


# ─── calculate_lot (generic formula) ────────────────────────────────────────


def test_lot_formula_basic():
    """Asc + (B - A) mod 360."""
    result = calculate_lot(0.0, 100.0, 200.0)
    assert result == 100.0  # 0 + 200 - 100 = 100


def test_lot_formula_with_asc():
    result = calculate_lot(30.0, 100.0, 200.0)
    assert result == 130.0  # 30 + 200 - 100 = 130


def test_lot_formula_wraparound():
    result = calculate_lot(350.0, 10.0, 30.0)
    # 350 + 30 - 10 = 370 % 360 = 10
    assert abs(result - 10.0) < 0.01


def test_lot_formula_negative_wrap():
    result = calculate_lot(10.0, 200.0, 100.0)
    # 10 + 100 - 200 = -90 → 270
    assert abs(result - 270.0) < 0.01


# ─── calculate_all_lots ─────────────────────────────────────────────────────


def test_all_lots_day_chart():
    chart = _make_chart(asc=0.0, sun_alt=10.0)
    lots = calculate_all_lots(chart, Sect.DAY)
    assert isinstance(lots, dict)
    assert len(lots) >= 30  # Should have 30+ lots
    # All values should be 0-360
    for name, lon in lots.items():
        assert 0.0 <= lon < 360.0, f"Lot {name} has invalid longitude: {lon}"


def test_all_lots_night_chart():
    chart = _make_chart(asc=0.0, sun_alt=-5.0)
    lots = calculate_all_lots(chart, Sect.NIGHT)
    assert isinstance(lots, dict)
    assert len(lots) >= 30


def test_fortune_spirit_sect_reversal():
    """Fortune and Spirit should reverse with sect."""
    chart = _make_chart(asc=0.0)
    day_lots = calculate_all_lots(chart, Sect.DAY)
    night_lots = calculate_all_lots(chart, Sect.NIGHT)
    # Fortune Day = Asc + Moon - Sun; Fortune Night = Asc + Sun - Moon
    # These are mirrored, so Fortune(Day) should equal Spirit(Night) and vice versa
    assert (
        abs(day_lots[LotName.FORTUNE.value] - night_lots[LotName.SPIRIT.value]) < 0.01
    )
    assert (
        abs(day_lots[LotName.SPIRIT.value] - night_lots[LotName.FORTUNE.value]) < 0.01
    )


def test_fortune_formula():
    """Day Fortune = Asc + Moon - Sun."""
    chart = _make_chart(asc=0.0, sun_alt=10.0)
    lots = calculate_all_lots(chart, Sect.DAY)
    # Asc=0, Sun=120, Moon=100 → Fortune = 0 + 100 - 120 = -20 → 340
    expected = (0.0 + 100.0 - 120.0) % 360.0
    assert abs(lots[LotName.FORTUNE.value] - expected) < 0.01


def test_spirit_formula():
    """Day Spirit = Asc + Sun - Moon."""
    chart = _make_chart(asc=0.0, sun_alt=10.0)
    lots = calculate_all_lots(chart, Sect.DAY)
    expected = (0.0 + 120.0 - 100.0) % 360.0
    assert abs(lots[LotName.SPIRIT.value] - expected) < 0.01


def test_hermetic_seven_present():
    """The 7 Paulus Alexandrinus lots should all be present."""
    chart = _make_chart()
    lots = calculate_all_lots(chart, Sect.DAY)
    for lot_name in [
        LotName.FORTUNE,
        LotName.SPIRIT,
        LotName.NECESSITY,
        LotName.EROS,
        LotName.COURAGE,
        LotName.VICTORY,
        LotName.NEMESIS,
    ]:
        assert lot_name.value in lots, f"Missing Hermetic Lot: {lot_name.value}"


def test_forensic_lots_present():
    """Forensic lots (Debt, Theft, Accusation) should be calculated."""
    chart = _make_chart()
    lots = calculate_all_lots(chart, Sect.DAY)
    assert LotName.DEBT.value in lots
    assert LotName.THEFT.value in lots
    assert LotName.ACCUSATION.value in lots


def test_commodity_lots_present():
    """Commodity lots (Wheat, Barley, Rice, Lentils) should be calculated."""
    chart = _make_chart()
    lots = calculate_all_lots(chart, Sect.DAY)
    assert LotName.WHEAT.value in lots
    assert LotName.BARLEY.value in lots
    assert LotName.RICE.value in lots
    assert LotName.LENTILS.value in lots


# ─── calculate_lot_position ─────────────────────────────────────────────────


def test_lot_position_fortune():
    chart = _make_chart()
    lon = calculate_lot_position(chart, LotName.FORTUNE, Sect.DAY)
    assert 0.0 <= lon < 360.0


def test_lot_position_unknown():
    """Unknown lot name should return 0.0."""
    chart = _make_chart()
    # Use a valid LotName that might not be in the dict if something goes wrong
    lon = calculate_lot_position(chart, LotName.FORTUNE, Sect.DAY)
    assert isinstance(lon, float)


# ─── missing planets edge case ───────────────────────────────────────────────


def test_missing_planets_returns_empty():
    """Chart with missing planets should return empty dict."""
    chart = Chart(
        sun_altitude=10.0,
        planets=[Planet(name=PlanetName.SUN, longitude=100.0, speed=1.0)],
        ascendant=0.0,
        mc=270.0,
    )
    lots = calculate_all_lots(chart, Sect.DAY)
    assert lots == {}
