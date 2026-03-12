from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from .models import PlanetName, Chart, Planet

# Minor Years (Least Years) of the Planets
MINOR_YEARS = {
    PlanetName.SATURN: 30,
    PlanetName.JUPITER: 12,
    PlanetName.MARS: 15,
    PlanetName.SUN: 19,
    PlanetName.VENUS: 8,
    PlanetName.MERCURY: 20,
    PlanetName.MOON: 25
}

# Operative Houses (Chrematistikos Topoi) in priority order
OPERATIVE_HOUSES = [1, 10, 11, 7, 5, 9, 4]

class DecennialEngine:
    @staticmethod
    def get_zodiacal_sequence(chart: Chart) -> List[Planet]:
        """
        Returns the seven traditional planets in zodiacal order, 
        starting from the Ascendant degree.
        """
        traditional = [
            PlanetName.SATURN, PlanetName.JUPITER, PlanetName.MARS,
            PlanetName.SUN, PlanetName.VENUS, PlanetName.MERCURY, PlanetName.MOON
        ]
        
        # Filter for traditional planets
        planets = [p for p in chart.planets if p.name in traditional]
        
        # Sort by longitude relative to Ascendant
        # normalized_offset = (p.lon - asc) % 360
        sorted_planets = sorted(
            planets, 
            key=lambda p: (p.longitude - chart.ascendant) % 360.0
        )
        
        return sorted_planets

    @staticmethod
    def select_apheta(chart: Chart) -> Planet:
        """
        Selects the Apheta (Releaser) for Decennials.
        1. Sect Light in Operative Place
        2. Contrary Light in Operative Place
        3. Post-Ascendant Planet
        """
        # Determine Sect
        # Note: chart.sun_altitude is used to determine day/night
        is_day = chart.sun_altitude > -0.833 # Standard horizon
        
        sun = next((p for p in chart.planets if p.name == PlanetName.SUN), None)
        moon = next((p for p in chart.planets if p.name == PlanetName.MOON), None)
        
        # Helper to find house of a planet
        def get_house(planet_lon: float) -> int:
            if not chart.houses: return 1 # Fallback
            # Find which house contains the longitude
            # For Whole Sign, it's just index from Ascendant sign
            asc_sign_idx = int(chart.ascendant / 30)
            p_sign_idx = int(planet_lon / 30)
            house = (p_sign_idx - asc_sign_idx) % 12 + 1
            return house

        # 1. Sect Light
        sect_light = sun if is_day else moon
        if sect_light:
            house = get_house(sect_light.longitude)
            if house in OPERATIVE_HOUSES:
                return sect_light
                
        # 2. Contrary Light
        contrary_light = moon if is_day else sun
        if contrary_light:
            house = get_house(contrary_light.longitude)
            if house in OPERATIVE_HOUSES:
                return contrary_light
                
        # 3. Post-Ascendant
        sequence = DecennialEngine.get_zodiacal_sequence(chart)
        return sequence[0]

    @staticmethod
    def generate_decennials(chart: Chart, start_date: datetime, lifespan_years: int = 100) -> List[Dict]:
        """
        Generates the Decennial tree (General and Sub-periods).
        Uses a 360-day year (Prophetic Year) logic internally for durations.
        """
        apheta = DecennialEngine.select_apheta(chart)
        full_sequence = DecennialEngine.get_zodiacal_sequence(chart)
        
        # Standard Period = 129 months = 3870 days
        PERIOD_DAYS = 3870
        
        results = []
        current_date = start_date
        
        # Align sequence to Apheta
        start_idx = full_sequence.index(apheta)
        current_sequence = full_sequence[start_idx:] + full_sequence[:start_idx]
        
        # Cycle 1
        for i in range(7):
            major_lord = current_sequence[i]
            major_period = {
                "major_lord": major_lord.name.value,
                "start_date": current_date.isoformat(),
                "end_date": (current_date + timedelta(days=PERIOD_DAYS)).isoformat(),
                "sub_periods": []
            }
            
            # Sub-periods start with Major Lord
            sub_sequence = current_sequence[i:] + current_sequence[:i]
            sub_date = current_date
            
            for j in range(7):
                sub_lord = sub_sequence[j]
                duration_days = MINOR_YEARS[sub_lord.name] * 30  # minor_years × 30-day months = sub-period in days
                
                major_period["sub_periods"].append({
                    "sub_lord": sub_lord.name.value,
                    "start_date": sub_date.isoformat(),
                    "end_date": (sub_date + timedelta(days=duration_days)).isoformat()
                })
                sub_date += timedelta(days=duration_days)
                
            results.append(major_period)
            current_date += timedelta(days=PERIOD_DAYS)
            
            if len(results) * 10.75 >= lifespan_years:
                break
                
        # Reset Logic for Old Age (Jump to Fourth)
        if len(results) < (lifespan_years / 10.75):
            # Valens Rule: Finish 7 planets, then jump to the 4th from Apheta
            new_start_idx = (start_idx + 3) % 7
            new_sequence = full_sequence[new_start_idx:] + full_sequence[:new_start_idx]
            
            # Repeat Cycle 2
            for i in range(7):
                major_lord = new_sequence[i]
                major_period = {
                    "major_lord": major_lord.name.value,
                    "start_date": current_date.isoformat(),
                    "end_date": (current_date + timedelta(days=PERIOD_DAYS)).isoformat(),
                    "sub_periods": []
                }
                
                sub_sequence = new_sequence[i:] + new_sequence[:i]
                sub_date = current_date
                
                for j in range(7):
                    sub_lord = sub_sequence[j]
                    duration_days = MINOR_YEARS[sub_lord.name] * 30
                    major_period["sub_periods"].append({
                        "sub_lord": sub_lord.name.value,
                        "start_date": sub_date.isoformat(),
                        "end_date": (sub_date + timedelta(days=duration_days)).isoformat()
                    })
                    sub_date += timedelta(days=duration_days)
                    
                results.append(major_period)
                current_date += timedelta(days=PERIOD_DAYS)
                if len(results) * 10.75 >= lifespan_years:
                    break
                    
        return results
