import swisseph as swe
import math
from typing import Dict, List, Optional, Tuple
from .models import PlanetName, PlanetaryPhase, SolarProximity, Planet, Sign

# Arcus Visionis (AV) Thresholds - Ptolemaic Standard (Planetary Hypotheses)
# Units: Degrees of solar depression below the horizon
AV_THRESHOLDS = {
    PlanetName.SATURN: 13.0,
    PlanetName.JUPITER: 9.0,
    PlanetName.MARS: 14.5,
    PlanetName.MERCURY: 12.0,
    # Venus is asymmetric
    "VENUS_EVENING": 5.0,
    "VENUS_MORNING": 7.0
}

class PhasisEngine:
    @staticmethod
    def is_oriental(planet_lon: float, sun_lon: float) -> bool:
        """
        Determines if a planet is Oriental (Morning Star).
        A planet is Oriental if it is 'behind' the Sun in zodiacal order (rises before it).
        """
        diff = (sun_lon - planet_lon) % 360.0
        return 0 < diff < 180.0

    @staticmethod
    def get_solar_proximity(planet_lon: float, sun_lon: float) -> SolarProximity:
        """Determines the solar proximity state based on longitude difference."""
        diff = abs(planet_lon - sun_lon)
        if diff > 180:
            diff = 360 - diff
            
        if diff <= (17.0 / 60.0): # 17 minutes for Cazimi
            return SolarProximity.CAZIMI
        elif diff <= 8.0:
            return SolarProximity.COMBUST
        elif diff <= 15.0:
            return SolarProximity.UNDER_BEAMS
        else:
            return SolarProximity.FREE

    @staticmethod
    def check_chariot(planet_name: PlanetName, planet_lon: float, domiciles: Dict, terms: Dict) -> bool:
        """
        A planet is in its chariot if it is in its own Domicile, Exaltation, or Bounds.
        Note: Passing domiciles/terms as dicts for decoupled logic.
        """
        # Logic to be implemented or called from dignities.py
        # For now, placeholder or base logic if dignities is too complex to pass
        return False # To be integrated with dignities.py

    @staticmethod
    def calculate_visibility(jd: float, lat: float, lon: float, planet_name: PlanetName, planet_lon: float, planet_lat: float, sun_lon: float) -> bool:
        """
        Calculates if a planet is visible based on Arcus Visionis.
        This is a 'vertical' calculation: how far below the horizon is the Sun 
        when the planet is exactly on the horizon?
        """
        if planet_name not in AV_THRESHOLDS and planet_name != PlanetName.VENUS:
            return True # Nodes/Outer planets usually considered visible if they exist (hypothetically)

        # 1. Determine Oriental/Occidental
        oriental = PhasisEngine.is_oriental(planet_lon, sun_lon)
        
        # 2. Get Threshold
        if planet_name == PlanetName.VENUS:
            threshold = AV_THRESHOLDS["VENUS_MORNING"] if oriental else AV_THRESHOLDS["VENUS_EVENING"]
        else:
            threshold = AV_THRESHOLDS.get(planet_name, 12.0)
            
        # 3. Calculate Solar Depression at the moment of Planet Rise (Oriental) or Set (Occidental)
        # We need the Sun's altitude when the planet's altitude is 0.
        # We can use swe for this.
        
        geopos = (lon, lat, 0)
        
        # Determine if we check Rise or Set
        event_type = swe.CALC_RISE if oriental else swe.CALC_SET
        
        # Find the moment the planet is at the horizon (refraction included)
        try:
            # swe_rise_trans(tjd_ut, body, starname, ephe_flag, rsmi, geopos, atpress, attemp, t_ret)
            # rsmi: 1=rise, 2=set
            rsmi = 1 if oriental else 2
            # We need the body ID for the planet. 
            # PlanetName mapping to swe IDs is expected to be handled or already known.
            # Assuming standard mapping: Sun=0, Moon=1, etc.
            
            # For simplicity in this engine, let's assume we pass the swe_id or map it.
            # Let's map PlanetName to swe IDs
            NAME_TO_SWE = {
                PlanetName.SUN: swe.SUN,
                PlanetName.MOON: swe.MOON,
                PlanetName.MERCURY: swe.MERCURY,
                PlanetName.VENUS: swe.VENUS,
                PlanetName.MARS: swe.MARS,
                PlanetName.JUPITER: swe.JUPITER,
                PlanetName.SATURN: swe.SATURN
            }
            
            p_id = NAME_TO_SWE.get(planet_name)
            if p_id is None: return True
            
            # Find next rise/set around JD
            # Signature: swe_rise_trans(tjd_ut, body, starname, ephe_flag, rsmi, geopos, atpress, attemp)
            res = swe.rise_trans(jd - 0.5, p_id, None, swe.FLG_SWIEPH, rsmi, geopos, 0, 0)
            t_event = res[1][0]
            
            # Calculate Sun's altitude at t_event
            sun_pos, _ = swe.calc_ut(t_event, swe.SUN, swe.FLG_SWIEPH)
            
            # res = swe.azalt(tjd, swe_flag, geopos, atpress, attemp, xin)
            res_azalt = swe.azalt(t_event, swe.FLG_SWIEPH, geopos, 0, 0, sun_pos[:3])
            sun_alt = res_azalt[1] # altitude
            
            return sun_alt <= -threshold
            
        except Exception:
            # Fallback to longitudinal approximation if rise_trans fails (Polar regions)
            diff = abs(planet_lon - sun_lon)
            if diff > 180: diff = 360 - diff
            return diff > threshold

    @staticmethod
    def get_synodic_phase(planet: Planet, sun_lon: float) -> PlanetaryPhase:
        """
        Identifies the synodic phase of a planet.
        """
        oriental = PhasisEngine.is_oriental(planet.longitude, sun_lon)
        diff = abs(planet.longitude - sun_lon)
        if diff > 180: diff = 360 - diff
        
        # 1. Check Proximity first
        prox = PhasisEngine.get_solar_proximity(planet.longitude, sun_lon)
        if prox == SolarProximity.CAZIMI: return PlanetaryPhase.CAZIMI
        
        # 2. Check Stations
        if abs(planet.speed) < 0.05: # High threshold for stationarity in phasis
            return PlanetaryPhase.STATION_RETROGRADE if planet.speed < 0 else PlanetaryPhase.STATION_DIRECT

        # 3. Superior vs Inferior
        is_superior = planet.name in [PlanetName.MARS, PlanetName.JUPITER, PlanetName.SATURN]
        
        if is_superior:
            if diff > 165: return PlanetaryPhase.OPPOSITION
            if oriental:
                if diff < 20: return PlanetaryPhase.MORNING_FIRST
                return PlanetaryPhase.FREE
            else:
                if diff < 20: return PlanetaryPhase.EVENING_LAST
                return PlanetaryPhase.FREE
        else:
            # Inferior Cycle
            if oriental:
                if planet.speed < 0: return PlanetaryPhase.MORNING_FIRST
                return PlanetaryPhase.MORNING_LAST
            else:
                if planet.speed > 0: return PlanetaryPhase.EVENING_FIRST
                return PlanetaryPhase.EVENING_LAST

        return PlanetaryPhase.FREE
