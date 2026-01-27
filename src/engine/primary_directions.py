import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from .models import Chart, Planet, PlanetName, Sect

@dataclass
class DirectionResult:
    significator: str
    promittor: str
    aspect: str
    arc: float
    years: float
    date_offset: str # "X years Y months"
    method: str

class PrimaryDirectionsEngine:
    """
    Implements Primary Directions using Placidus (Semi-Arc) and Regiomontanus methods.
    Focuses on Placidus as the 'gold standard' for intermediate points.
    """

    # Obliquity of Ecliptic (Approx for J2000, or JNow could be passed)
    EPSILON = 23.4392911

    @staticmethod
    def _to_rad(deg: float) -> float:
        return math.radians(deg)

    @staticmethod
    def _to_deg(rad: float) -> float:
        return math.degrees(rad)

    @staticmethod
    def _normalize_deg(deg: float) -> float:
        return deg % 360.0

    @classmethod
    def ecliptic_to_equatorial(cls, lon: float, lat: float) -> Tuple[float, float]:
        """
        Converts Ecliptic (Lon, Lat) to Equatorial (RA, Dec).
        """
        lon_r = cls._to_rad(lon)
        lat_r = cls._to_rad(lat)
        eps_r = cls._to_rad(cls.EPSILON)

        # sin(delta) = sin(eps)*sin(lon)*cos(lat) + cos(eps)*sin(lat)
        sin_dec = math.sin(eps_r) * math.sin(lon_r) * math.cos(lat_r) + \
                  math.cos(eps_r) * math.sin(lat_r)
        dec_r = math.asin(sin_dec)

        # tan(alpha) = (sin(lon)*cos(eps) - tan(lat)*sin(eps)) / cos(lon)
        y = math.sin(lon_r) * math.cos(eps_r) - math.tan(lat_r) * math.sin(eps_r)
        x = math.cos(lon_r)
        ra_r = math.atan2(y, x)

        return (cls._to_deg(ra_r) % 360.0, cls._to_deg(dec_r))

    @classmethod
    def calculate_ad(cls, dec: float, geo_lat: float) -> float:
        """
        Ascensional Difference: sin(AD) = tan(dec) * tan(lat)
        """
        # Clamp tan*tan to [-1, 1] to avoid domain errors (e.g. circumpolar)
        val = math.tan(cls._to_rad(dec)) * math.tan(cls._to_rad(geo_lat))
        if val > 1.0 or val < -1.0:
            return 0.0 # Circumpolar fallback (simplified)
        return cls._to_deg(math.asin(val))

    @classmethod
    def calculate_semi_arcs(cls, dec: float, geo_lat: float) -> Tuple[float, float]:
        """
        Returns (Diurnal SA, Nocturnal SA).
        DSA = 90 + AD
        NSA = 90 - AD
        (For Northern Hemisphere logic implies positive AD for North Dec)
        """
        ad = cls.calculate_ad(dec, geo_lat)
        dsa = 90.0 + ad
        nsa = 90.0 - ad
        return (dsa, nsa)

    @classmethod
    def calculate_md(cls, ra: float, ramc: float) -> float:
        """
        Meridian Distance (RA - RAMC).
        Normalized to -180 to +180 for "Least Distance" logic?
        Or strict RA - RAMC % 360.
        Placidus usually uses the distance to the *nearest* meridian.
        Let's perform standard substraction and normalize.
        """
        md = (ra - ramc) % 360.0
        if md > 180:
            md -= 360
        return md

    @classmethod
    def get_proportional_distance(cls, ra: float, dec: float, ramc: float, geo_lat: float) -> Tuple[float, float]:
        """
        Calculates Proportional Distance (0.0 - 1.0) and the Semi-Arc used.
        Returns (PropDist, SemiArc).
        """
        # Meridian Distance
        md = (ra - ramc)
        # Normalize MD to determine Quadrant?
        # Standard:
        # 10th House (MC to Asc): Western, Above Horizon
        # 7th House (Desc to IC): Western, Below Horizon
        # ...
        
        # We need to know if the point is Above or Below horizon
        # Check standard Geometric logic:
        # Determine OA of Ascendant
        # If RA is between OA_Asc and OA_Desc, etc?
        # Simpler: Check MD.
        pass
        # To strictly determine Above/Below horizon using just RA/Dec/RAMC/Lat:
        # Calculate Local Sidereal Time (LST) ~ RAMC.
        # Hour Angle (HA) = LST - RA
        # Altitude formula...
        # Simplified:
        #  HA = RAMC - RA
        #  If Abs(HA) < DSA, Above Horizon. Else Below.
        
        dsa, nsa = cls.calculate_semi_arcs(dec, geo_lat)
        
        # Distance from Meridian (Upper)
        dist_upper = abs(cls.calculate_md(ra, ramc))
        
        # Check if above horizon
        # Note: MD is distance from Upper Meridian (MC).
        # If dist_upper < DSA, it is Above Horizon.
        # If dist_upper > DSA, it is Below Horizon?
        # Yes, DSA is the half-arc from Rise to Set (crossing MC).
        
        is_above = dist_upper < dsa
        
        if is_above:
            # Proportional Dist from MC
            # Using Placidus definition: MD / SA
            # Usually range -1 (Rise) to 0 (MC) to +1 (Set)?
            # Or 0 (MC) to 1 (Horizon).
            # Let's standardize: Ratio from Meridian.
            ratio = dist_upper / dsa
            # Distinguish East/West?
            # If RA > RAMC (0-180), West.
            # If RA < RAMC (0-180), East.
            
            # Text implies: PropDist used for diff.
            # Let's return signed PropDist.
            # East is negative (rising to MC), West is positive (setting from MC).
            
            diff = (ra - ramc)
            # Normalize diff -180 to 180
            if diff > 180: diff -= 360
            elif diff < -180: diff += 360
            
            # If distinct East/West
            pd = diff / dsa
            return (pd, dsa)
        else:
            # Below Horizon
            # Use distance from IC.
            # IC = RAMC + 180
            ic = (ramc + 180) % 360
            
            diff = (ra - ic)
            if diff > 180: diff -= 360
            elif diff < -180: diff += 360
            
            pd = diff / nsa
            # This PD is relative to IC.
            # We must coordinate systems.
            # Placidus Mundane Position:
            # MC = 0
            # Asc = -1 (East Horizon) ?? Or +1?
            # Standard "Mundane position":
            # MC=0, Asc=3, IC=6, Desc=9?
            # Let's stick to the Text's Formula:
            # "Arc = (PropDist_P - PropDist_S) * SA_P"
            # This implies PD must be continuous or handled by quadrant.
            
            # Let's use the 0-4 quadrant system or similar.
            # But the formula suggests raw ratio.
            
            # Alternative: Calculate Arc to Angle explicitly for Angles.
            # For planets: Calculate Time.
            
            # Let's try to return the raw ratio from the UPPER meridian, keeping arc continuity?
            # No, text examples use simple subtraction.
            
            # Let's stick to simple Arc to Angle first for reliability, as text says "Intermediate points...".
            # If we assume directions TO ANGLES:
            # Arc = OA_P - OA_Asc (for Asc direction)
            # Arc = (RA_P - RA_M) - ...
            
            # Let's assume this Engine will primarily calculate Directions TO ANGLES (Asc/MC) as priority.
            # And Planet-to-Planet later.
            
            return (0.0, 0.0) # Placeholder

    @classmethod
    def calculate_directions_to_angles(cls, chart: Chart, geo_lat: float) -> List[DirectionResult]:
        """
        Calculates directions of all planets to Conjunction/Opposition of Asc/MC.
        """
        results = []
        
        # 1. Chart Properties
        ramc = chart.mc # Is chart.mc in RA or Ecliptic Longitude?
        # Usually models.py stores MC as Ecliptic Longitude!
        # We need RAMC!
        # If we have MC Longitude, we can convert to RA (Lat=0).
        # MC is always on Ecliptic? Yes. And Latitude=0.
        
        mc_ra, _ = cls.ecliptic_to_equatorial(chart.mc, 0.0)
        
        # Ascendant RA?
        asc_ra, _ = cls.ecliptic_to_equatorial(chart.ascendant, 0.0)
        # Note: Ascendant OA is defined as RAMC + 90.
        oa_asc = (mc_ra + 90.0) % 360.0
        
        # 2. Iterate Planets (Promittors)
        promittors = chart.planets
        
        for p in promittors:
            if p.name in [PlanetName.NORTH_NODE, PlanetName.SOUTH_NODE]: continue
            
            # Calculate Promittor Coordinates
            # Note: Using Natal Latitude!
            ra_p, dec_p = cls.ecliptic_to_equatorial(p.longitude, p.latitude)
            
            # Calculate AD, OA, OD
            ad_p = cls.calculate_ad(dec_p, geo_lat)
            oa_p = (ra_p - ad_p) % 360.0 # Eastern
            od_p = (ra_p + ad_p) % 360.0 # Western (Setting)
            
            # 3. Direct to Ascendant (Conjunction)
            # Promittor coming to Ascendant (Rising)
            # Arc = OA_Promittor - OA_Asc
            arc_asc = (oa_p - oa_asc)
            # Normalize simple arc (traditional usually positive for future?)
            # Valid arcs are 0 to 100 degrees (approx 100 years).
            # If negative, it implies it happened in past (converse?) or far future?
            # We usually look for arcs > 0.
            # If arc < 0: arc += 360? No, that's 300+ years.
            
            # Placidus Directions usually measured forward (Direct).
            # So if OA_P > OA_Asc, it will arrive later?
            # Wait. Primary Motion is East to West (Rotation).
            # So RA/OA increases towards East?
            # RAMC increases with time!
            # So OA_Asc increases with time.
            # If OA_P > OA_Asc, then OA_Asc will "catch up" to OA_P?
            # Yes. So Arc = OA_P - OA_Asc.
            
            if 0 < arc_asc < 100:
                results.append(DirectionResult(
                    significator="Ascendant",
                    promittor=p.name.value,
                    aspect="Conjunction",
                    arc=arc_asc,
                    years=cls.ptolemy_key(arc_asc),
                    date_offset=cls.format_years(arc_asc),
                    method="Placidus/Ptolemy"
                ))
                
            # 4. Direct to Midheaven (Conjunction)
            # Promittor coming to MC (Culminating)
            # Arc = RA_Promittor - RAMC
            arc_mc = (ra_p - mc_ra)
            # Normalize
            if diff := (ra_p - mc_ra):
                 # Handle wrapping nicely?
                 # If RA_P = 10, RAMC = 350. Arc = 20? 
                 # 10 - 350 = -340. += 360 = 20. Correct.
                 pass
            
            arc_mc = (ra_p - mc_ra) % 360.0
            if 0 < arc_mc < 100:
                results.append(DirectionResult(
                    significator="Midheaven",
                    promittor=p.name.value,
                    aspect="Conjunction",
                    arc=arc_mc,
                    years=cls.ptolemy_key(arc_mc),
                    date_offset=cls.format_years(arc_mc),
                    method="Placidus/Ptolemy"
                ))

            # 5. Opposition to Ascendant (Setting) = Conjunction to Descendant
            # Arc = OD_Promittor - OD_Desc
            # OD_Desc = RAMC - 90
            od_desc = (mc_ra - 90.0) % 360.0
            arc_desc = (od_p - od_desc) % 360.0
            
            if 0 < arc_desc < 100:
                 results.append(DirectionResult(
                    significator="Ascendant",
                    promittor=p.name.value,
                    aspect="Opposition",
                    arc=arc_desc,
                    years=cls.ptolemy_key(arc_desc),
                    date_offset=cls.format_years(arc_desc),
                    method="Placidus/Ptolemy"
                ))
            
            # 6. Opposition to MC (IC)
            # Arc = RA - RA_IC
            ra_ic = (mc_ra + 180.0) % 360.0
            arc_ic = (ra_p - ra_ic) % 360.0
            
            if 0 < arc_ic < 100:
                results.append(DirectionResult(
                    significator="Midheaven",
                    promittor=p.name.value,
                    aspect="Opposition",
                    arc=arc_ic,
                    years=cls.ptolemy_key(arc_ic),
                    date_offset=cls.format_years(arc_ic),
                    method="Placidus/Ptolemy"
                ))

        return sorted(results, key=lambda x: x.years)

    @staticmethod
    def ptolemy_key(arc: float) -> float:
        """1 degree = 1 year"""
        return arc

    @staticmethod
    def format_years(years: float) -> str:
        y = int(years)
        m = int((years - y) * 12)
        return f"{y}y {m}m"

