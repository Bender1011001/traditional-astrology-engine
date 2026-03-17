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

NAME_TO_SWE = {
    PlanetName.SUN: swe.SUN,
    PlanetName.MOON: swe.MOON,
    PlanetName.MERCURY: swe.MERCURY,
    PlanetName.VENUS: swe.VENUS,
    PlanetName.MARS: swe.MARS,
    PlanetName.JUPITER: swe.JUPITER,
    PlanetName.SATURN: swe.SATURN,
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
        # The Sun is the reference body; it cannot be cazimi/combust/under beams relative to itself.
        # Treat it as FREE for proximity classification.
        # (Solar status is handled separately in calculations.calculate_solar_status.)
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
        A planet is in its chariot if it is in its own Domicile, Exaltation, or Bounds (Terms).
        Ref: Paulus Alexandrinus, Introduction to Astrology, Ch. 14.
        """
        from .dignities import DignityCalculator
        from .models import Sect
        # Use a neutral sect for essential ruler lookup (chariot doesn't depend on sect)
        rulers = DignityCalculator.get_essential_rulers(planet_lon, Sect.DAY)
        if rulers.get("domicile") == planet_name:
            return True
        if rulers.get("exaltation") == planet_name:
            return True
        if rulers.get("term") == planet_name:
            return True
        return False

    @staticmethod
    def calculate_visibility_details(
        jd: float,
        lat: float,
        lon: float,
        planet_name: PlanetName,
        planet_lon: float,
        planet_lat: float,
        sun_lon: float,
    ) -> Dict[str, object]:
        """
        Arcus Visionis (AV) visibility check with auditable fields.

        Returns a dict with:
        - is_visible (bool)
        - method (str)
        - oriental (bool)
        - event ("rise"|"set")
        - threshold_solar_depression_deg (float)
        - sun_altitude_at_event_deg (float|None) (positive above horizon; negative below)
        - event_jd_ut (float|None)
        - note (str|None)

        If vertical computation fails (e.g., polar day/night), falls back to elongation-based heuristic
        and marks method accordingly.
        """
        # Non-traditional points/bodies: treat as visible if present, but report as heuristic.
        if planet_name == PlanetName.SUN:
            return {
                "is_visible": True,
                "method": "sun_default",
                "oriental": None,
                "event": None,
                "threshold_solar_depression_deg": None,
                "sun_altitude_at_event_deg": None,
                "event_jd_ut": None,
                "note": "Sun visibility is not evaluated by Arcus Visionis in this engine; treated as visible by definition.",
            }
        if planet_name not in AV_THRESHOLDS and planet_name != PlanetName.VENUS:
            return {
                "is_visible": True,
                "method": "non_traditional_default",
                "oriental": None,
                "event": None,
                "threshold_solar_depression_deg": None,
                "sun_altitude_at_event_deg": None,
                "event_jd_ut": None,
                "note": "No AV thresholds defined for this body; treated as visible by default.",
            }

        oriental = PhasisEngine.is_oriental(planet_lon, sun_lon)

        if planet_name == PlanetName.VENUS:
            threshold = float(AV_THRESHOLDS["VENUS_MORNING"] if oriental else AV_THRESHOLDS["VENUS_EVENING"])
        else:
            threshold = float(AV_THRESHOLDS.get(planet_name, 12.0))

        geopos = (float(lon), float(lat), 0.0)
        rsmi = 1 if oriental else 2  # 1=rise, 2=set
        event_label = "rise" if oriental else "set"

        p_id = NAME_TO_SWE.get(planet_name)
        if p_id is None:
            return {
                "is_visible": True,
                "method": "non_traditional_default",
                "oriental": oriental,
                "event": event_label,
                "threshold_solar_depression_deg": threshold,
                "sun_altitude_at_event_deg": None,
                "event_jd_ut": None,
                "note": "No Swiss Ephemeris body mapping; treated as visible by default.",
            }

        try:
            # Find next rise/set near the reference JD.
            # Use jd-0.5 to ensure we catch the relevant event around the date boundary.
            # pyswisseph signature: rise_trans(tjdut, body, rsmi, geopos, atpress=0, attemp=0, flags=FLG_SWIEPH)
            _res, tret = swe.rise_trans(jd - 0.5, p_id, rsmi, geopos, 0.0, 0.0, swe.FLG_SWIEPH)
            t_event = float(tret[0])

            # Sun altitude at the planet's rise/set time.
            sun_pos, _ = swe.calc_ut(t_event, swe.SUN, swe.FLG_SWIEPH)
            res_azalt = swe.azalt(t_event, swe.FLG_SWIEPH, geopos, 0, 0, sun_pos[:3])
            sun_alt = float(res_azalt[1])

            is_vis = sun_alt <= (-threshold)
            return {
                "is_visible": is_vis,
                "method": "arcus_visionis_vertical",
                "oriental": oriental,
                "event": event_label,
                "threshold_solar_depression_deg": threshold,
                "sun_altitude_at_event_deg": round(sun_alt, 6),
                "event_jd_ut": round(t_event, 8),
                "note": None,
            }
        except Exception as e:
            # Fallback: elongation heuristic (less auditable, but deterministic).
            # NOTE: This is not AV; we label it as such.
            elong = abs(planet_lon - sun_lon)
            if elong > 180:
                elong = 360 - elong

            # Conservative heuristic thresholds (degrees of elongation).
            elong_thresholds = {
                PlanetName.MERCURY: 12.0,
                PlanetName.VENUS: 8.0,
                PlanetName.MARS: 10.0,
                PlanetName.JUPITER: 8.0,
                PlanetName.SATURN: 8.0,
            }
            e_thr = float(elong_thresholds.get(planet_name, 12.0))
            return {
                "is_visible": bool(elong >= e_thr),
                "method": "elongation_fallback",
                "oriental": oriental,
                "event": event_label,
                "threshold_solar_depression_deg": threshold,
                "sun_altitude_at_event_deg": None,
                "event_jd_ut": None,
                "note": f"Vertical AV calc failed ({type(e).__name__}); used elongation >= {e_thr:.1f}° heuristic.",
            }

    @staticmethod
    def calculate_visibility(
        jd: float,
        lat: float,
        lon: float,
        planet_name: PlanetName,
        planet_lon: float,
        planet_lat: float,
        sun_lon: float,
    ) -> bool:
        return bool(
            PhasisEngine.calculate_visibility_details(jd, lat, lon, planet_name, planet_lon, planet_lat, sun_lon).get(
                "is_visible"
            )
        )

    @staticmethod
    def get_synodic_phase(planet: Planet, sun_lon: float) -> PlanetaryPhase:
        """
        Identifies the synodic phase of a planet.
        """
        if planet.name == PlanetName.SUN:
            return PlanetaryPhase.FREE

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
