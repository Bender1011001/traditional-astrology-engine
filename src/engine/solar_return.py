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
    def analyze_solar_return_from_jd(natal_chart: Chart, sr_jd: float, age: int, birth_dt: datetime) -> Dict:
        """
        Reconstructs the SR chart from JD and performs analysis.
        """
        import swisseph as swe
        
        # 1. Reconstruct SR Chart
        sr_planets = []
        flag_sr = swe.FLG_SWIEPH | swe.FLG_SPEED
        for pname_enum in PlanetName:
            if pname_enum in [PlanetName.NORTH_NODE, PlanetName.SOUTH_NODE]: 
                continue
            
            # Map PlanetName to Swiss Eph ID
            swe_id_map = {
                PlanetName.SUN: swe.SUN,
                PlanetName.MOON: swe.MOON,
                PlanetName.MERCURY: swe.MERCURY,
                PlanetName.VENUS: swe.VENUS,
                PlanetName.MARS: swe.MARS,
                PlanetName.JUPITER: swe.JUPITER,
                PlanetName.SATURN: swe.SATURN,
                PlanetName.URANUS: swe.URANUS,
                PlanetName.NEPTUNE: swe.NEPTUNE,
                PlanetName.PLUTO: swe.PLUTO,
            }
            pid = swe_id_map.get(pname_enum)
            if pid is None: continue
            
            try:
                res = swe.calc_ut(sr_jd, pid, flag_sr)[0]
                sr_planets.append(Planet(
                    name=pname_enum, 
                    longitude=res[0], 
                    latitude=res[1], 
                    speed=res[3]
                ))
            except:
                continue
        
        # SR Houses
        # Note: We use b'P' for Placidus, but Whole Sign 'W' is often preferred. 
        # Using Placidus for the angles and house cusps as a default.
        sr_cusps, sr_ascmc = swe.houses(sr_jd, natal_chart.geo_lat, natal_chart.geo_lon, b'P')
        
        sr_chart = Chart(
            sun_altitude=0, # Not strictly needed for SR analysis logic as written
            planets=sr_planets,
            ascendant=sr_ascmc[0],
            mc=sr_ascmc[1],
            houses={i+1: c for i, c in enumerate(sr_cusps)},
            geo_lat=natal_chart.geo_lat,
            geo_lon=natal_chart.geo_lon,
            jd=sr_jd
        )
        
        res = SolarReturnEngine.analyze_solar_return(sr_chart, natal_chart, age)
        res["year"] = birth_dt.year + age
        return res

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
