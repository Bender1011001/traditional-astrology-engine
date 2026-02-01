from datetime import datetime
from typing import Dict, List, Optional
from .models import Chart, Planet, PlanetName, Sign, Sect
from .prediction import calculate_profection_sign, get_lord_of_year
from .dignities import DignityCalculator

class SolarReturnEngine:
    """
    Implements Morin's Hierarchical Determination for Solar Returns.
    Axiom: The SR cannot produce what the Nativity does not promise.
    """

    @staticmethod
    def analyze_solar_return(sr_chart: Chart, natal_chart: Chart, age: int) -> Dict:
        """
        Synthesizes the Solar Return by overlaying it on the Natal Chart.
        """
        # 1. Overlay Logic: SR Ascendant in Natal House
        sr_asc_lon = sr_chart.ascendant
        # Which natal house does the SR Asc fall in?
        natal_house_of_sr_asc = DignityCalculator.get_house_number(sr_asc_lon, natal_chart.ascendant, natal_chart.houses)
        
        # 2. Lord of the Year (LoY)
        # Calculate profection sign from natal ascendant
        natal_asc_idx = int(natal_chart.ascendant / 30) % 12
        natal_asc_sign = list(Sign)[natal_asc_idx]
        
        prof_sign = calculate_profection_sign(natal_asc_sign, age)
        loy_name = get_lord_of_year(prof_sign)
        
        # 3. LoY Status in SR
        loy_planet = next((p for p in sr_chart.planets if p.name == loy_name), None)
        loy_weight = 0
        loy_details = []
        
        if loy_planet:
            # Weighting Algorithm
            sr_house = DignityCalculator.get_house_number(loy_planet.longitude, sr_chart.ascendant, sr_chart.houses)
            
            # Angular in SR (+10)
            if sr_house in [1, 4, 7, 10]:
                loy_weight += 10
                loy_details.append("Angular in SR (+10)")
            # Cadent (-10)
            elif sr_house in [3, 6, 9, 12]:
                loy_weight -= 10
                loy_details.append("Cadent in SR (-10)")
            
            # Combust check (Lilly 15 deg)
            sun = next((p for p in sr_chart.planets if p.name == PlanetName.SUN), None)
            if sun:
                diff = abs(loy_planet.longitude - sun.longitude) % 360
                if diff > 180: diff = 360 - diff
                if diff < 15:
                    loy_weight -= 10
                    loy_details.append("Combust in SR (-10)")
            
            # Aspecting SR Ascendant (+5)
            # (Simple degree based check for now)
            asc_diff = abs(loy_planet.longitude - sr_chart.ascendant) % 360
            if asc_diff > 180: asc_diff = 360 - asc_diff
            if asc_diff < 8 or abs(asc_diff - 120) < 8 or abs(asc_diff - 60) < 8:
                loy_weight += 5
                loy_details.append("Aspecting SR Ascendant (+5)")

        # 4. Planetary Determinations
        determinations = []
        for p in sr_chart.planets:
            if p.name in [PlanetName.SUN, PlanetName.MOON, PlanetName.NORTH_NODE, PlanetName.SOUTH_NODE]:
                continue
            
            # Find SR House
            sr_h = DignityCalculator.get_house_number(p.longitude, sr_chart.ascendant, sr_chart.houses)
            
            # Find Natal House Rulership (Whole Sign)
            # For each sign the planet rules, find which natal house it maps to
            ruled_natal_houses = []
            
            signs_ruled = DignityCalculator.DOMICILES.get(p.name, [])
            for sign in signs_ruled:
                # Which natal house is this sign?
                # Start of sign lon
                sign_start = (list(Sign).index(sign)) * 30
                h_num = DignityCalculator.get_house_number(sign_start + 1.0, natal_chart.ascendant, natal_chart.houses)
                ruled_natal_houses.append(h_num)
            
            determinations.append({
                "planet": p.name.value,
                "sr_house": sr_h,
                "natal_houses_ruled": ruled_natal_houses,
                "judgment": f"{p.name.value} acts in SR House {sr_h} concerning matters of Natal Houses {', '.join(map(str, ruled_natal_houses))}."
            })

        return {
            "sr_asc_in_natal_house": natal_house_of_sr_asc,
            "lord_of_year": {
                "name": loy_name.value,
                "weight": loy_weight,
                "details": loy_details
            },
            "determinations": determinations,
            "morin_axiom": "The Solar Return cannot produce what the Nativity does not promise."
        }
