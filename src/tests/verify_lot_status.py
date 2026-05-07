from src.engine.advanced_mechanics import HermeticLotEngine
from src.engine.models import Chart, Planet, PlanetName


def test_lot_maltreatment():
    print("=== Testing Lot Maltreatment Logic ===")

    # 1. Setup a Day Chart
    # Asc = 0 Aries
    # Sun = 10 Aries (Day)
    # Moon = 10 Cancer
    # Fortune = Asc + Moon - Sun = 0 + 90 - 10 = 80 (20 Gemini). Wait.
    # Fortune (Day) = Asc + Moon - Sun.
    # Let's simple numbers.
    # Asc = 0.
    # Sun = 0. (Aries 0)
    # Moon = 90. (Cancer 0)
    # Fortune = 0 + 90 - 0 = 90 (Cancer 0).

    # 2. Setup Planets
    sun = Planet(PlanetName.SUN, 0.0, altitude=10.0)  # Day chart
    moon = Planet(PlanetName.MOON, 90.0)
    # Malefic: Saturn at 92.0 (Cancer 2) -> Conjunction with Fortune (90.0)
    saturn = Planet(PlanetName.SATURN, 92.0)

    # Add other planets to avoid errors if engine expects them (though it iterates chart.planets)
    mars = Planet(PlanetName.MARS, 180.0)
    mercury = Planet(PlanetName.MERCURY, 30.0)
    venus = Planet(PlanetName.VENUS, 60.0)
    jupiter = Planet(PlanetName.JUPITER, 120.0)

    planets = [sun, moon, mercury, venus, mars, jupiter, saturn]

    # Houses (dummy)
    houses = {i: (i - 1) * 30.0 for i in range(1, 13)}

    chart = Chart(sun_altitude=10.0, planets=planets, ascendant=0.0, houses=houses)

    # 3. Calculate Lots
    print("Calculating Lots...")
    lots = HermeticLotEngine.calculate_all_lots(chart)

    fortune = lots.get("Fortune")
    if not fortune:
        print("FAIL: Fortune not calculated.")
        return

    print(f"Fortune Position: {fortune['longitude']} (Sign: {fortune['sign']})")
    print(f"Status: {fortune['status']}")
    print(f"Details: {fortune['maltreatment_details']}")

    # 4. Assertions
    # Fortune is at 90.0. Saturn is at 92.0.
    # Should be Maltreated (Adherence or similar).

    if "Maltreated" in fortune["status"]:
        print("PASS: Maltreatment detected.")
    else:
        print("FAIL: Fortune should be maltreated but is Clear.")

    # Test Ruler Maltreatment
    # Ruler of Cancer is Moon.
    # Moon is at 90.0. Saturn is at 92.0. Moon is also maltreated!
    if "Ruler Maltreated" in fortune["status"]:
        print("PASS: Ruler Maltreatment detected.")
    else:
        print("FAIL: Ruler (Moon) should be maltreated.")


if __name__ == "__main__":
    test_lot_maltreatment()
