from typing import Dict, Optional
from .models import Chart, Sect, PlanetName, LotName

def calculate_lot(asc: float, a_lon: float, b_lon: float) -> float:
    """
    Generic Lot Formula: Asc + (B - A)
    Vector from A to B projected from Asc.
    """
    return (asc + b_lon - a_lon) % 360.0

def calculate_lot_position(chart: Chart, lot_name: LotName, sect: Sect) -> float:
    """
    Calculates the position of a specific lot.
    """
    all_lots = calculate_all_lots(chart, sect)
    return all_lots.get(lot_name.value, 0.0)

def calculate_all_lots(chart: Chart, sect: Sect) -> Dict[str, float]:
    """
    Calculates standard Arabic Parts and Forensic Lots.
    Returns a dictionary mapping LotName values (strings) to longitudes.
    """
    # Get planetary positions
    sun = next((p for p in chart.planets if p.name == PlanetName.SUN), None)
    moon = next((p for p in chart.planets if p.name == PlanetName.MOON), None)
    mercury = next((p for p in chart.planets if p.name == PlanetName.MERCURY), None)
    venus = next((p for p in chart.planets if p.name == PlanetName.VENUS), None)
    mars = next((p for p in chart.planets if p.name == PlanetName.MARS), None)
    jupiter = next((p for p in chart.planets if p.name == PlanetName.JUPITER), None)
    saturn = next((p for p in chart.planets if p.name == PlanetName.SATURN), None)
    
    if not (sun and moon and mercury and venus and mars and jupiter and saturn):
        return {} # Cannot calculate without Septener
        
    asc = chart.ascendant
    is_day = (sect == Sect.DAY)
    
    lots = {}
    
    # 1. The Seven Hermetic Lots (Paulus Alexandrinus Protocol)
    
    # Fortune (Tyche): Moon vs Sun
    lots[LotName.FORTUNE.value] = calculate_lot(asc, sun.longitude, moon.longitude) if is_day else calculate_lot(asc, moon.longitude, sun.longitude)
        
    # Spirit (Daimon): Sun vs Moon
    lots[LotName.SPIRIT.value] = calculate_lot(asc, moon.longitude, sun.longitude) if is_day else calculate_lot(asc, sun.longitude, moon.longitude)
        
    fort_lon = lots[LotName.FORTUNE.value]
    spir_lon = lots[LotName.SPIRIT.value]
    
    # Necessity (Ananke): Mercury vs Fortune
    lots[LotName.NECESSITY.value] = calculate_lot(asc, fort_lon, mercury.longitude) if is_day else calculate_lot(asc, mercury.longitude, fort_lon)
        
    # Eros: Venus vs Spirit
    lots[LotName.EROS.value] = calculate_lot(asc, spir_lon, venus.longitude) if is_day else calculate_lot(asc, venus.longitude, spir_lon)
        
    # Courage (Tolma): Mars vs Fortune
    lots[LotName.COURAGE.value] = calculate_lot(asc, fort_lon, mars.longitude) if is_day else calculate_lot(asc, mars.longitude, fort_lon)
        
    # Victory (Nike): Jupiter vs Spirit
    lots[LotName.VICTORY.value] = calculate_lot(asc, spir_lon, jupiter.longitude) if is_day else calculate_lot(asc, jupiter.longitude, spir_lon)
        
    # Nemesis: Saturn vs Fortune
    lots[LotName.NEMESIS.value] = calculate_lot(asc, fort_lon, saturn.longitude) if is_day else calculate_lot(asc, saturn.longitude, fort_lon)
        
    # 2. Spiritual Foundation Lots (Paulus)
    
    # Basis: Shortest arc between Fortune and Spirit
    arc = (spir_lon - fort_lon + 360) % 360
    if arc > 180:
        # Backward arc is shorter
        lots[LotName.BASIS.value] = calculate_lot(asc, fort_lon, spir_lon)
        lots[LotName.FOUNDATION.value] = lots[LotName.BASIS.value]
    else:
        lots[LotName.BASIS.value] = calculate_lot(asc, spir_lon, fort_lon)
        lots[LotName.FOUNDATION.value] = lots[LotName.BASIS.value]

    # Exaltation: Distance from exaltation degree (19 Ari / 3 Tau)
    if is_day:
        lots[LotName.EXALTATION.value] = calculate_lot(asc, sun.longitude, 19.0) # From Sun to 19 Aries
    else:
        lots[LotName.EXALTATION.value] = calculate_lot(asc, moon.longitude, 33.0) # From Moon to 3 Taurus (30+3)

    # 3. Social & Commodity Lots (Al-Biruni / Persian)
    
    # Male Children / Wheat
    lots[LotName.CHILDREN.value] = calculate_lot(asc, sun.longitude, jupiter.longitude) if is_day else calculate_lot(asc, jupiter.longitude, sun.longitude)
    lots[LotName.WHEAT.value] = lots[LotName.CHILDREN.value]

    # Female Children
    lots[LotName.MARRIAGE_WOMEN.value] = calculate_lot(asc, moon.longitude, venus.longitude) if is_day else calculate_lot(asc, venus.longitude, moon.longitude)
    
    # Barley
    lots[LotName.BARLEY.value] = calculate_lot(asc, saturn.longitude, moon.longitude) if is_day else calculate_lot(asc, moon.longitude, saturn.longitude)
    
    # Rice
    lots[LotName.RICE.value] = calculate_lot(asc, jupiter.longitude, saturn.longitude) if is_day else calculate_lot(asc, saturn.longitude, jupiter.longitude)
    
    # Lentils / Iron
    lots[LotName.LENTILS.value] = calculate_lot(asc, saturn.longitude, mars.longitude) if is_day else calculate_lot(asc, mars.longitude, saturn.longitude)

    # 4. Forensic / Specialized Lots (Legacy & Arabic)
    
    # Debt
    lots[LotName.DEBT.value] = calculate_lot(asc, mercury.longitude, saturn.longitude) if is_day else calculate_lot(asc, saturn.longitude, mercury.longitude)
        
    # Theft
    lots[LotName.THEFT.value] = calculate_lot(asc, mercury.longitude, mars.longitude) if is_day else calculate_lot(asc, mars.longitude, mercury.longitude)
        
    # Accusation (Legal Trouble)
    lots[LotName.ACCUSATION.value] = calculate_lot(asc, saturn.longitude, mars.longitude) if is_day else calculate_lot(asc, mars.longitude, saturn.longitude)
        
    # Marriage (Men)
    lots[LotName.MARRIAGE_MEN.value] = calculate_lot(asc, saturn.longitude, venus.longitude)
    
    # Siblings
    lots[LotName.SIBLINGS.value] = calculate_lot(asc, saturn.longitude, jupiter.longitude) if is_day else calculate_lot(asc, jupiter.longitude, saturn.longitude)
        
    # Friends
    lots[LotName.FRIENDS.value] = calculate_lot(asc, mercury.longitude, moon.longitude)
    
    # Enemies
    lots[LotName.ENEMIES.value] = calculate_lot(asc, saturn.longitude, mars.longitude)
    
    # Sickness
    lots[LotName.SICKNESS.value] = calculate_lot(asc, saturn.longitude, mars.longitude)
    
    # Assets (Substance)
    if chart.houses and 2 in chart.houses:
        lots[LotName.ASSETS.value] = (asc + chart.houses[2] - sun.longitude) % 360 
    else:
        lots[LotName.ASSETS.value] = calculate_lot(asc, saturn.longitude, jupiter.longitude)
        
    # Death
    if chart.houses and 8 in chart.houses:
        lots[LotName.DEATH.value] = calculate_lot(asc, moon.longitude, chart.houses[8])
    else:
        lots[LotName.DEATH.value] = calculate_lot(asc, moon.longitude, saturn.longitude)
        
    # Journeys
    if chart.houses and 9 in chart.houses:
        lots[LotName.JOURNEYS.value] = calculate_lot(asc, sun.longitude, chart.houses[9])
    else:
        lots[LotName.JOURNEYS.value] = calculate_lot(asc, sun.longitude, mars.longitude)
        
    # Success/Kingdom
    lots[LotName.SUCCESS.value] = calculate_lot(asc, sun.longitude, jupiter.longitude)
    
    # Misfortune
    lots[LotName.MISFORTUNE.value] = calculate_lot(asc, sun.longitude, saturn.longitude)
    
    # Life
    lots[LotName.LIFE.value] = calculate_lot(asc, saturn.longitude, jupiter.longitude)
    
    # Wisdom
    lots[LotName.WISDOM.value] = calculate_lot(asc, saturn.longitude, sun.longitude)
    
    # Art
    lots[LotName.ART.value] = calculate_lot(asc, sun.longitude, venus.longitude)
    
    # Battles
    lots[LotName.BATTLES.value] = calculate_lot(asc, saturn.longitude, mars.longitude)
    
    # Commerce
    lots[LotName.COMMERCE.value] = calculate_lot(asc, sun.longitude, mercury.longitude)
    
    # Boldness
    lots[LotName.BOLDNESS.value] = calculate_lot(asc, moon.longitude, mars.longitude)
    
    # Father
    lots[LotName.FATHER.value] = calculate_lot(asc, sun.longitude, saturn.longitude) if is_day else calculate_lot(asc, saturn.longitude, sun.longitude)
        
    # Mother
    lots[LotName.MOTHER.value] = calculate_lot(asc, venus.longitude, moon.longitude) if is_day else calculate_lot(asc, moon.longitude, venus.longitude)

    # Poverty (Al-Biruni: Reverse of Necessity)
    lots[LotName.POVERTY.value] = calculate_lot(asc, mercury.longitude, fort_lon) if is_day else calculate_lot(asc, fort_lon, mercury.longitude)

    return lots
