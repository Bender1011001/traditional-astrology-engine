
import pytest

from src.engine.advanced_mechanics import HermeticLotEngine
from src.engine.forensic_engine import Auditor
from src.engine.lots import calculate_all_lots
from src.engine.models import Chart, LotName, Planet, PlanetName, Sect


def test_lot_expansion():
    """
    Verify that the Lot library now calculates 35+ items including commodities.
    """
    # Create a dummy chart
    planets = [
        Planet(name=PlanetName.SUN, longitude=0.0),  # 0 Aries
        Planet(name=PlanetName.MOON, longitude=90.0),  # 0 Cancer
        Planet(name=PlanetName.MERCURY, longitude=10.0),
        Planet(name=PlanetName.VENUS, longitude=20.0),
        Planet(name=PlanetName.MARS, longitude=30.0),
        Planet(name=PlanetName.JUPITER, longitude=60.0),
        Planet(name=PlanetName.SATURN, longitude=120.0),
    ]
    chart = Chart(
        sun_altitude=10.0,  # Day
        planets=planets,
        ascendant=0.0,
        houses={i: (i - 1) * 30 for i in range(1, 13)},
    )

    lots = calculate_all_lots(chart, Sect.DAY)

    # Check count
    assert len(lots) >= 35, f"Expected at least 35 lots, got {len(lots)}"

    # Check specific critical lots
    assert LotName.FORTUNE.value in lots
    assert LotName.DEBT.value in lots
    assert LotName.BASIS.value in lots
    assert LotName.WHEAT.value in lots
    assert LotName.BARLEY.value in lots

    # Check math for Fortune (Day: Asc + Moon - Sun)
    # 0 + 90 - 0 = 90
    assert lots[LotName.FORTUNE.value] == 90.0

    # Check math for Basis (Paulus)
    # Fort=90, Spir=270. Arc Spir to Fort = 180.
    # Basis formula in lots.py: if arc > 180, Asc + Fort - Spir. Else Asc + Spir - Fort.
    # or actually the doc says: "If Spirit is shortest, Asc + Fortune - Spirit."
    # Let's check my implementation:
    # spir_lon=270, fort_lon=90. arc = (270-90) = 180.
    # My code: arc is 180. arc > 180 is False. so Basis = calculate_lot(asc, spir_lon, fort_lon)
    # Basis = 0 + 90 - 270 = -180 = 180.
    assert lots[LotName.BASIS.value] == 180.0


def test_hermetic_engine_enrichment():
    """
    Verify that HermeticLotEngine enriches the lots with metadata for all LotNames.
    """
    planets = [
        Planet(name=PlanetName.SUN, longitude=0.0),
        Planet(name=PlanetName.MOON, longitude=10.0),
        Planet(name=PlanetName.MERCURY, longitude=20.0),
        Planet(name=PlanetName.VENUS, longitude=30.0),
        Planet(name=PlanetName.MARS, longitude=40.0),
        Planet(name=PlanetName.JUPITER, longitude=50.0),
        Planet(name=PlanetName.SATURN, longitude=60.0),
    ]
    chart = Chart(
        sun_altitude=10.0,
        planets=planets,
        ascendant=0.0,
        houses={i: (i - 1) * 30 for i in range(1, 13)},
    )

    enriched_lots = HermeticLotEngine.calculate_all_lots(chart)

    # Check count
    assert (
        len(enriched_lots) >= 35
    ), f"Expected 35+ enriched lots, got {len(enriched_lots)}"


def test_audit_integration():
    """
    Verify that the Auditor surfaces the expanded lots in its technical report.
    """
    planets = [
        Planet(name=PlanetName.SUN, longitude=0.0),
        Planet(name=PlanetName.MOON, longitude=10.0),
        Planet(name=PlanetName.MERCURY, longitude=20.0),
        Planet(name=PlanetName.VENUS, longitude=30.0),
        Planet(name=PlanetName.MARS, longitude=40.0),
        Planet(name=PlanetName.JUPITER, longitude=50.0),
        Planet(name=PlanetName.SATURN, longitude=60.0),
    ]
    chart = Chart(
        sun_altitude=10.0,
        planets=planets,
        ascendant=0.0,
        houses={i: (i - 1) * 30 for i in range(1, 13)},
        geo_lat=40.7,
        geo_lon=-74.0,
        jd=2451545.0,
    )

    results = Auditor.perform_audit(chart, jd=chart.jd, age=30)

    fate = results["analysis"]["fate"]
    hermetic_lots = fate["hermetic_lots"]

    assert "Wheat" in hermetic_lots
    assert "Barley" in hermetic_lots
    assert "Basis" in hermetic_lots


if __name__ == "__main__":
    pytest.main([__file__])
