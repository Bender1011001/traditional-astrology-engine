from typing import Dict, List, Tuple
import math
import swisseph as swe
from .models import Chart, Sign, PlanetName

def normalize_deg(deg: float) -> float:
    return deg % 360.0

def get_true_obliquity(jd: float) -> float:
    """Returns true obliquity from Swiss Ephemeris."""
    res, _ = swe.calc_ut(jd, -1, swe.FLG_SWIEPH)
    return res[0]

def ra_to_ecl(ra: float, eps: float) -> float:
    """Converts Right Ascension to Ecliptic Longitude (beta=0)."""
    ra_rad = math.radians(ra)
    eps_rad = math.radians(eps)
    
    # tan(lambda) = sin(RA) / (cos(RA) * cos(eps))
    lon_rad = math.atan2(math.sin(ra_rad), math.cos(ra_rad) * math.cos(eps_rad))
    return normalize_deg(math.degrees(lon_rad))

def ecl_to_ra(lon: float, eps: float) -> float:
    """Converts Ecliptic Longitude to Right Ascension (beta=0)."""
    lon_rad = math.radians(lon)
    eps_rad = math.radians(eps)
    
    # tan(RA) = sin(lambda) * cos(eps) / cos(lambda)
    ra_rad = math.atan2(math.sin(lon_rad) * math.cos(eps_rad), math.cos(lon_rad))
    return normalize_deg(math.degrees(ra_rad))

class AlcabitiusEngine:
    @staticmethod
    def calculate_houses(jd: float, lat: float, lon: float) -> Dict[int, float]:
        """
        Rigorous manual implementation of Alcabitius (Standard Method).
        Trisects the semi-arcs of the Ascendant and projects via Hour Circles.
        """
        # 1. Get base angles and ARMC
        # We use Whole Signhouses code 'W' to get clean angles from swe
        _, ascmc = swe.houses(jd, lat, lon, b'W')
        asc_lon = ascmc[0]
        mc_lon = ascmc[1]
        ramc = ascmc[2] # Right Ascension of Midheaven
        
        # 2. Get true obliquity
        eps = get_true_obliquity(jd)
        
        # 3. Calculate RA of Ascendant
        ra_asc = ecl_to_ra(asc_lon, eps)
        
        # 4. Calculate Semi-Arcs
        # DSA: Arc from MC to Ascendant (Eastward)
        dsa = normalize_deg(ra_asc - ramc)
        nsa = 180.0 - dsa # Geometric identity (RA_IC - RA_ASC)
        
        # 5. Trisect and project
        # House 10 is MC
        ra_11 = normalize_deg(ramc + dsa/3.0)
        ra_12 = normalize_deg(ramc + 2.0*dsa/3.0)
        
        # House 1 is ASC
        ra_2 = normalize_deg(ra_asc + nsa/3.0)
        ra_3 = normalize_deg(ra_asc + 2.0*nsa/3.0)
        
        cusps = {
            1: asc_lon,
            2: ra_to_ecl(ra_2, eps),
            3: ra_to_ecl(ra_3, eps),
            4: normalize_deg(mc_lon + 180.0),
            10: mc_lon,
            11: ra_to_ecl(ra_11, eps),
            12: ra_to_ecl(ra_12, eps)
        }
        
        # 6. Fill Opposites
        cusps[5] = normalize_deg(cusps[11] + 180.0)
        cusps[6] = normalize_deg(cusps[12] + 180.0)
        cusps[7] = normalize_deg(cusps[1] + 180.0)
        cusps[8] = normalize_deg(cusps[2] + 180.0)
        cusps[9] = normalize_deg(cusps[3] + 180.0)
        
        # Return sorted by house number
        return {i: cusps[i] for i in range(1, 13)}
