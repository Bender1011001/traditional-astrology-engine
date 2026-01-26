from typing import Dict
from .models import Chart, Sect, PlanetName, LotName

def normalize_degree(deg: float) -> float:
    while deg < 0:
        deg += 360
    while deg >= 360:
        deg -= 360
    return deg

def get_planet_pos(chart: Chart, name: PlanetName) -> float:
    planet = next((p for p in chart.planets if p.name == name), None)
    if planet:
        return planet.longitude
    return 0.0

def is_combust(chart: Chart, planet_name: PlanetName) -> bool:
    sun_pos = get_planet_pos(chart, PlanetName.SUN)
    planet_pos = get_planet_pos(chart, planet_name)
    
    diff = abs(planet_pos - sun_pos)
    if diff > 180:
        diff = 360 - diff
    return diff < 15.0

def calculate_lot_position(chart: Chart, lot_name: LotName, sect: Sect) -> float:
    asc = chart.ascendant
    sun = get_planet_pos(chart, PlanetName.SUN)
    moon = get_planet_pos(chart, PlanetName.MOON)
    
    # Base Lots First
    fortune = 0.0
    spirit = 0.0
    
    if sect == Sect.DAY:
        fortune = normalize_degree(asc + moon - sun)
        spirit = normalize_degree(asc + sun - moon)
    else:
        fortune = normalize_degree(asc + sun - moon)
        spirit = normalize_degree(asc + moon - sun)
        
    if lot_name == LotName.FORTUNE:
        return fortune
    if lot_name == LotName.SPIRIT:
        return spirit
        
    # Derived Lots
    if lot_name == LotName.EROS:
        # Day: Asc + Spirit - Fortune
        # Night: Asc + Fortune - Spirit
        if sect == Sect.DAY:
            return normalize_degree(asc + spirit - fortune)
        else:
            return normalize_degree(asc + fortune - spirit)
            
    if lot_name == LotName.NECESSITY:
        # Day: Asc + Fortune - Spirit
        # Night: Asc + Spirit - Fortune
        if sect == Sect.DAY:
            return normalize_degree(asc + fortune - spirit)
        else:
            return normalize_degree(asc + spirit - fortune)
            
    if lot_name == LotName.VICTORY:
        # Day: Asc + Jupiter - Spirit
        # Night: Asc + Spirit - Jupiter
        jupiter = get_planet_pos(chart, PlanetName.JUPITER)
        if sect == Sect.DAY:
            return normalize_degree(asc + jupiter - spirit)
        else:
            return normalize_degree(asc + spirit - jupiter)
            
    if lot_name == LotName.FATHER:
        # Day: Asc + Saturn - Sun
        # Night: Asc + Sun - Saturn
        # If Saturn is corrupted (within 15 deg of Sun), use Jupiter: Asc + Jupiter - Sun
        if is_combust(chart, PlanetName.SATURN):
            jupiter = get_planet_pos(chart, PlanetName.JUPITER)
            return normalize_degree(asc + jupiter - sun)
        
        saturn = get_planet_pos(chart, PlanetName.SATURN)
        if sect == Sect.DAY:
            return normalize_degree(asc + saturn - sun)
        else:
            return normalize_degree(asc + sun - saturn)

    if lot_name == LotName.COURAGE:
        # Day: Asc + Fortune - Mars
        # Night: Asc + Mars - Fortune
        fortune = calculate_lot_position(chart, LotName.FORTUNE, sect)
        mars = get_planet_pos(chart, PlanetName.MARS)
        if sect == Sect.DAY:
            return normalize_degree(asc + fortune - mars)
        else:
            return normalize_degree(asc + mars - fortune)

    if lot_name == LotName.NEMESIS:
        # Day: Asc + Fortune - Saturn
        # Night: Asc + Saturn - Fortune
        fortune = calculate_lot_position(chart, LotName.FORTUNE, sect)
        saturn = get_planet_pos(chart, PlanetName.SATURN)
        if sect == Sect.DAY:
            return normalize_degree(asc + fortune - saturn)
        else:
            return normalize_degree(asc + saturn - fortune)
            
    if lot_name == LotName.MOTHER:
        # Day: Asc + Moon - Venus
        # Night: Asc + Venus - Moon
        venus = get_planet_pos(chart, PlanetName.VENUS)
        if sect == Sect.DAY:
            return normalize_degree(asc + moon - venus)
        else:
            return normalize_degree(asc + venus - moon)
            
    return 0.0

def calculate_all_lots(chart: Chart, sect: Sect) -> Dict[str, float]:
    results = {}
    for lot in LotName:
        results[lot.value] = calculate_lot_position(chart, lot, sect)
    return results
