import pytest
from src.engine.models import Chart, Planet, PlanetName, Sect, LotName
from src.engine.lots import calculate_all_lots

def test_lots_expanded_poverty_necessity():
    # Setup standard chart with distinct planets
    sun = Planet(name=PlanetName.SUN, longitude=30.0)      # 0° Taurus
    moon = Planet(name=PlanetName.MOON, longitude=120.0)   # 0° Leo
    mercury = Planet(name=PlanetName.MERCURY, longitude=90.0) # 0° Cancer
    venus = Planet(name=PlanetName.VENUS, longitude=60.0)
    mars = Planet(name=PlanetName.MARS, longitude=150.0)
    jupiter = Planet(name=PlanetName.JUPITER, longitude=180.0)
    saturn = Planet(name=PlanetName.SATURN, longitude=210.0)
    
    chart = Chart(sun_altitude=10.0, planets=[sun, moon, mercury, venus, mars, jupiter, saturn], ascendant=0.0)
    
    # 1. Day Chart
    lots_day = calculate_all_lots(chart, Sect.DAY)
    assert lots_day
    
    # Fortune (Tyche): Asc + Moon - Sun = 0 + 120 - 30 = 90
    assert lots_day[LotName.FORTUNE.value] == 90.0
    
    # Spirit (Daimon): Asc + Sun - Moon = 0 + 30 - 120 = 270
    assert lots_day[LotName.SPIRIT.value] == 270.0
    
    # Necessity (Ananke): Asc + Fortune - Mercury = 0 + 90 - 90 = 0
    assert lots_day[LotName.NECESSITY.value] == 0.0
    
    # Poverty: Asc + Fortune - Spirit = 0 + 90 - 270 = 180 (different from Necessity!)
    assert lots_day[LotName.POVERTY.value] == 180.0
    assert lots_day[LotName.POVERTY.value] != lots_day[LotName.NECESSITY.value]

    # 2. Night Chart
    lots_night = calculate_all_lots(chart, Sect.NIGHT)
    assert lots_night
    
    # Fortune (Tyche): Asc + Sun - Moon = 0 + 30 - 120 = 270
    assert lots_night[LotName.FORTUNE.value] == 270.0
    
    # Spirit (Daimon): Asc + Moon - Sun = 0 + 120 - 30 = 90
    assert lots_night[LotName.SPIRIT.value] == 90.0
    
    # Necessity (Ananke): Asc + Mercury - Fortune = 0 + 90 - 270 = 180
    assert lots_night[LotName.NECESSITY.value] == 180.0
    
    # Poverty: Asc + Spirit - Fortune = 0 + 90 - 270 = 180
    # In this specific configuration they happen to be equal, but let's change mercury longitude to see difference
    
    mercury.longitude = 95.0
    lots_night_diff = calculate_all_lots(chart, Sect.NIGHT)
    # Necessity = Asc + Mercury - Fortune = 0 + 95 - 270 = 185
    assert lots_night_diff[LotName.NECESSITY.value] == 185.0
    # Poverty = Asc + Spirit - Fortune = 0 + 90 - 270 = 180 (remains same since Mercury isn't in formula)
    assert lots_night_diff[LotName.POVERTY.value] == 180.0
    assert lots_night_diff[LotName.POVERTY.value] != lots_night_diff[LotName.NECESSITY.value]
