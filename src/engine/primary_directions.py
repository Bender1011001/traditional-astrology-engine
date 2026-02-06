import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import swisseph as swe
from .models import Chart, Planet, PlanetName, Sect
from .dignities import DignityCalculator

@dataclass
class DirectionResult:
    significator: str
    promittor: str
    aspect: str
    arc: float
    years: float
    date_offset: str # "X years Y months"
    method: str

@dataclass
class MundaneSpeculum:
    planet: str
    ra: float
    dec: float
    ad: float
    dsa: float
    nsa: float
    md: float
    pole: float
    mundane_pos: float # Equivalent to a 1-12 house coordinate (Proportional distance)

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
        dsa = 90 + ad
        nsa = 90 - ad
        return (dsa, nsa)

    @classmethod
    def calculate_md(cls, ra: float, ramc: float) -> float:
        """
        Meridian Distance (RA - RAMC).
        """
        md = (ra - ramc) % 360.0
        if md > 180:
            md -= 360
        return md

    @classmethod
    def calculate_pole(cls, md: float, sa: float, geo_lat: float) -> float:
        """
        Calculates the Pole of the planet (Placidus/Kuehr).
        tan(Pole) = (MD / SA) * tan(GeoLat)
        """
        if sa == 0: return 0.0
        ratio = abs(md) / sa
        tan_pole = ratio * math.tan(cls._to_rad(geo_lat))
        return cls._to_deg(math.atan(tan_pole))

    @classmethod
    def calculate_mundane_position(cls, ra: float, dec: float, ramc: float, geo_lat: float) -> float:
        """
        Calculates the 1-12 'proportional house position'.
        Standardized: MC=10.0, Asc=1.0, IC=4.0, Dsc=7.0.
        Uses Semi-Arc proportionality.
        """
        md = cls.calculate_md(ra, ramc)
        dsa, nsa = cls.calculate_semi_arcs(dec, geo_lat)
        
        # Determine Quadrant
        is_above = abs(md) < dsa
        is_east = md < 0 # Simplified: RA_Planet < RA_MC? 
        # (Actually md is ra-ramc. If ra < ramc, md < 0 -> East of Meridian)

        if is_above:
            # 7-10 (West) or 10-1 (East)
            ratio = abs(md) / dsa # 0 at MC, 1.0 at Horiz
            if is_east:
                # 10 to 1 (Houses 10, 11, 12)
                # MC = 10.0, Asc = 13.0 (or 1.0)
                return 10.0 + (ratio * 3.0)
            else:
                # 10 to 7 (Houses 10, 9, 8, 7)
                return 10.0 - (ratio * 3.0)
        else:
            # 1-4 (East) or 4-7 (West)
            # Distance from IC
            raic = (ramc + 180) % 360
            md_ic = cls.calculate_md(ra, raic)
            ratio = abs(md_ic) / nsa # 0 at IC, 1.0 at Horiz
            if is_east:
                # 4 to 1
                return 4.0 - (ratio * 3.0)
            else:
                # 4 to 7
                return 4.0 + (ratio * 3.0)

    @classmethod
    def get_full_speculum(cls, planet: Planet, ramc: float, geo_lat: float) -> MundaneSpeculum:
        ra, dec = cls.ecliptic_to_equatorial(planet.longitude, planet.latitude)
        ad = cls.calculate_ad(dec, geo_lat)
        dsa, nsa = cls.calculate_semi_arcs(dec, geo_lat)
        md = cls.calculate_md(ra, ramc)
        
        is_above = abs(md) < dsa
        sa = dsa if is_above else nsa
        
        pole = cls.calculate_pole(md, sa, geo_lat)
        m_pos = cls.calculate_mundane_position(ra, dec, ramc, geo_lat)
        
        return MundaneSpeculum(
            planet=planet.name.value,
            ra=ra, dec=dec, ad=ad, dsa=dsa, nsa=nsa, md=md, pole=pole, mundane_pos=m_pos
        )

    @classmethod
    def calculate_current_distributor(cls, chart: Chart, age_years: float, geo_lat: float) -> Dict:
        """
        Calculates the current 'Distributor' (Term Ruler of Directed Ascendant).
        Algorithm:
        1. Calculate Arc = Age (Ptolemy Key).
        2. Direct the Ascendant by this Arc (OA_Dir = OA_Radical + Arc).
        3. Convert OA_Dir back to Zodiacal Longitude.
        4. Find the Term Ruler of that Longitude.
        """
        arc = cls.ptolemy_key(age_years)
        
        # 1. Get Natal OA of Ascendant
        # We can simulate this by calculating the RAMC that would put the Ascendant at the horizon + Arc?
        # NO. Directing the Ascendant:
        # OA_Asc_Dir = OA_Asc_Natal + Arc.
        # Then find the Ecliptic point that has this OA.
        # This point is the Ascendant of a chart with RAMC' = RAMC_Natal + Arc.
        
        # Get Natal RAMC (RA of MC)
        mc_lon = chart.mc
        # swe.house_pos calculates house cusps. We need the reverse or just use houses() with modified Time?
        # Simpler: Get RAMC from MC Longitude.
        mc_ra, _ = cls.ecliptic_to_equatorial(mc_lon, 0.0)
        
        # Directed RAMC
        ramc_directed = (mc_ra + arc) % 360.0
        
        # Calculate new Ascendant for this RAMC
        # swe.houses_armc(armc, lat, eps, hsys) - armc is in deg
        try:
            # armc is RAMC.
            cusps, ascmc = swe.houses_armc(ramc_directed, geo_lat, cls.EPSILON, b'P')
            asc_directed_lon = ascmc[0]
            
            # Get Term Ruler
            sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
            dignities = DignityCalculator.get_essential_rulers(asc_directed_lon, sect)
            term_ruler = dignities["term"]
            
            # Find the "Partner" (Participating Planet)
            # The partner is the planet that aspects the directed degree,
            # or the ruler of the sign if no aspect.
            partner = dignities["domicile"]
            partner_reason = "Domicile Ruler"
            
            for p in chart.planets:
                diff = abs(p.longitude - asc_directed_lon)
                if diff > 180: diff = 360 - diff
                # Check major aspects (Conjunction, Sextile, Square, Trine, Opposition)
                if diff < 3 or abs(diff - 60) < 3 or abs(diff - 90) < 3 or abs(diff - 120) < 3 or abs(diff - 180) < 3:
                    partner = p.name
                    partner_reason = f"Aspecting Planet ({p.name.value})"
                    break

            return {
                "type": "Distributor (Term Ruler)",
                "planet": term_ruler.value if hasattr(term_ruler, "value") else str(term_ruler),
                "partner": partner.value if hasattr(partner, "value") else str(partner),
                "partner_reason": partner_reason,
                "directed_ascendant_deg": asc_directed_lon,
                "arc": arc,
                "description": f"The Directed Ascendant is at {asc_directed_lon:.2f}°, in the Terms of {term_ruler.value if hasattr(term_ruler, 'value') else term_ruler}. Partner: {partner.value if hasattr(partner, 'value') else partner} ({partner_reason})."
            }
        except Exception as e:
            return {"error": str(e)}

    @classmethod
    def calculate_directions_to_angles(cls, chart: Chart, geo_lat: float) -> List[DirectionResult]:
        """
        Calculates directions of all planets to Conjunction/Opposition/Square/Trine/Sextile of Asc/MC.
        """
        results = []
        
        # 1. Chart Properties
        mc_ra, _ = cls.ecliptic_to_equatorial(chart.mc, 0.0)
        oa_asc = (mc_ra + 90.0) % 360.0
        
        # 2. Iterate Planets (Promittors)
        promittors = chart.planets
        
        # Define Aspects to Check
        # (Name, Angle, IsHard)
        aspects_to_check = [
            ("Conjunction", 0, True),
            ("Sextile", 60, False),
            ("Square", 90, True),
            ("Trine", 120, False),
            ("Opposition", 180, True)
        ]
        
        for p in promittors:
            if p.name in [PlanetName.NORTH_NODE, PlanetName.SOUTH_NODE]: continue
            
            # CHECK ALL ASPECTS TO ASCENDANT
            for asp_name, asp_angle, _ in aspects_to_check:
                # Directed Asc moves forward (OA increases).
                # Hit occurs when OA_Asc_Dir = OA_Promittor (plus aspect?).
                # For aspect P to Asc:
                # Arc = OA(P + aspect) - OA_Asc ??
                # Or Arc = OA(P) - OA(Asc + aspect) ??
                # Traditionally: Arc = OA(Promittor's Aspect Point) - OA(Significator).
                # But Promittor has latitude. The aspect point is on the Ecliptic (usually).
                # "Planets directed to angles with latitude" involves finding the point on the sphere.
                # Simplified (Mundane): 
                # Conjunction: Arc = OA_P - OA_Asc
                # Sextile: Arc = OA(P_Sextile_Point) - OA_Asc? 
                # Actually, standard practice for primary directions to angles often treats the aspect as an angle in the Mundane Sphere (Semi-Arc).
                # BUT simpler logic (Zodiacal Aspects directed to Angle):
                # 1. Find Longitude of Promittor.
                # 2. Add aspect (e.g. +60, -60). 
                # 3. Find RA/Dec of that zodiacal degree (Lat=0).
                # 4. Find OA of that degree.
                # 5. Arc = OA_Point - OA_Asc.
                
                # Let's do Zodiacal Aspects (Lat=0 for the aspect point)
                aspect_lons = []
                if asp_angle == 0:
                    aspect_lons = [(p.longitude, "Conjunction")]
                elif asp_angle == 180:
                    aspect_lons = [((p.longitude + 180) % 360, "Opposition")]
                else:
                    aspect_lons = [
                        ((p.longitude + asp_angle) % 360, f"{asp_name} (Dexter)"),
                        ((p.longitude - asp_angle) % 360, f"{asp_name} (Sinister)")
                    ]
                
                for lon_pt, name_pt in aspect_lons:
                     # Calculate OA of this aspect point (Lat 0 assumed for aspects usually)
                     ra_pt, dec_pt = cls.ecliptic_to_equatorial(lon_pt, 0.0)
                     ad_pt = cls.calculate_ad(dec_pt, geo_lat)
                     oa_pt = (ra_pt - ad_pt) % 360.0
                     
                     arc = oa_pt - oa_asc
                     # Normalize 
                     if arc < 0: arc += 360
                     
                     if 0 < arc < 100:
                         results.append(DirectionResult(
                            significator="Ascendant",
                            promittor=p.name.value,
                            aspect=name_pt,
                            arc=arc,
                            years=cls.ptolemy_key(arc),
                            date_offset=cls.format_years(arc),
                            method="Placidus/Zodiacal"
                        ))

            # CHECK ALL ASPECTS TO MC
            # Arc = RA(Promittor Aspect Point) - RAMC
            for asp_name, asp_angle, _ in aspects_to_check:
                aspect_lons = []
                if asp_angle == 0:
                    aspect_lons = [(p.longitude, "Conjunction")]
                elif asp_angle == 180:
                    aspect_lons = [((p.longitude + 180) % 360, "Opposition")]
                else:
                    aspect_lons = [
                        ((p.longitude + asp_angle) % 360, f"{asp_name} (Dexter)"),
                        ((p.longitude - asp_angle) % 360, f"{asp_name} (Sinister)")
                    ]
                
                for lon_pt, name_pt in aspect_lons:
                     ra_pt, _ = cls.ecliptic_to_equatorial(lon_pt, 0.0)
                     arc = (ra_pt - mc_ra) % 360.0
                     
                     if 0 < arc < 100:
                         results.append(DirectionResult(
                            significator="Midheaven",
                            promittor=p.name.value,
                            aspect=name_pt,
                            arc=arc,
                            years=cls.ptolemy_key(arc),
                            date_offset=cls.format_years(arc),
                            method="Placidus/Zodiacal"
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
