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
    
    # 1. The Seven Hermetic Lots (Paulus Alexandrinus)
    
    # Fortune (Tyche): Moon vs Sun
    # Day: Asc + Moon - Sun | Night: Asc + Sun - Moon
    if is_day:
        lots[LotName.FORTUNE.value] = calculate_lot(asc, sun.longitude, moon.longitude)
    else:
        lots[LotName.FORTUNE.value] = calculate_lot(asc, moon.longitude, sun.longitude)
        
    # Spirit (Daimon): Sun vs Moon (Reverse of Fortune)
    # Day: Asc + Sun - Moon | Night: Asc + Moon - Sun
    if is_day:
        lots[LotName.SPIRIT.value] = calculate_lot(asc, moon.longitude, sun.longitude)
    else:
        lots[LotName.SPIRIT.value] = calculate_lot(asc, sun.longitude, moon.longitude)
        
    # For the remaining Hermetic Lots, they are anchored to Fortune or Spirit.
    # We need the calculated values.
    fort_lon = lots[LotName.FORTUNE.value]
    spir_lon = lots[LotName.SPIRIT.value]
    
    # Necessity (Ananke): Mercury vs Fortune
    # Day: Asc + Mercury - Fortune | Night: Asc + Fortune - Mercury
    if is_day:
        lots[LotName.NECESSITY.value] = calculate_lot(asc, fort_lon, mercury.longitude)
    else:
        lots[LotName.NECESSITY.value] = calculate_lot(asc, mercury.longitude, fort_lon)
        
    # Eros: Venus vs Spirit
    # Day: Asc + Venus - Spirit | Night: Asc + Spirit - Venus
    if is_day:
        lots[LotName.EROS.value] = calculate_lot(asc, spir_lon, venus.longitude)
    else:
        lots[LotName.EROS.value] = calculate_lot(asc, venus.longitude, spir_lon)
        
    # Courage (Tolma): Mars vs Fortune
    # Day: Asc + Mars - Fortune | Night: Asc + Fortune - Mars
    if is_day:
        lots[LotName.COURAGE.value] = calculate_lot(asc, fort_lon, mars.longitude)
    else:
        lots[LotName.COURAGE.value] = calculate_lot(asc, mars.longitude, fort_lon)
        
    # Victory (Nike): Jupiter vs Spirit
    # Day: Asc + Jupiter - Spirit | Night: Asc + Spirit - Jupiter
    if is_day:
        lots[LotName.VICTORY.value] = calculate_lot(asc, spir_lon, jupiter.longitude)
    else:
        lots[LotName.VICTORY.value] = calculate_lot(asc, jupiter.longitude, spir_lon)
        
    # Nemesis: Saturn vs Fortune
    # Day: Asc + Saturn - Fortune | Night: Asc + Fortune - Saturn
    if is_day:
        lots[LotName.NEMESIS.value] = calculate_lot(asc, fort_lon, saturn.longitude)
    else:
        lots[LotName.NEMESIS.value] = calculate_lot(asc, saturn.longitude, fort_lon)
        
    # 2. Forensic Lots (Traditional/Arabic)
    
    # Debt (Vettius Valens / Bonatti)
    # Formula: Asc + Saturn - Mercury (Day), Asc + Mercury - Saturn (Night)
    # Note: Some sources reverse this. We follow the standard malefic/mercury exchange.
    if is_day:
        lots[LotName.DEBT.value] = calculate_lot(asc, mercury.longitude, saturn.longitude)
    else:
        lots[LotName.DEBT.value] = calculate_lot(asc, saturn.longitude, mercury.longitude)
        
    # Theft
    # Formula: Asc + Mars - Mercury (Day), Asc + Mercury - Mars (Night)
    if is_day:
        lots[LotName.THEFT.value] = calculate_lot(asc, mercury.longitude, mars.longitude)
    else:
        lots[LotName.THEFT.value] = calculate_lot(asc, mars.longitude, mercury.longitude)
        
    # Accusation (of Crimes/Police)
    # Formula: Asc + Mars - Saturn (Day), Asc + Saturn - Mars (Night)
    if is_day:
        lots[LotName.ACCUSATION.value] = calculate_lot(asc, saturn.longitude, mars.longitude)
    else:
        lots[LotName.ACCUSATION.value] = calculate_lot(asc, mars.longitude, saturn.longitude)
        
    # Father (Standard)
    # Day: Asc + Saturn - Sun | Night: Asc + Sun - Saturn
    if is_day:
        lots[LotName.FATHER.value] = calculate_lot(asc, sun.longitude, saturn.longitude)
    else:
        lots[LotName.FATHER.value] = calculate_lot(asc, saturn.longitude, sun.longitude)
        
    # Mother (Standard)
    # Day: Asc + Moon - Venus | Night: Asc + Venus - Moon
    if is_day:
        lots[LotName.MOTHER.value] = calculate_lot(asc, venus.longitude, moon.longitude)
    else:
        lots[LotName.MOTHER.value] = calculate_lot(asc, moon.longitude, venus.longitude)
        
    return lots
