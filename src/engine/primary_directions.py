import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import swisseph as swe
import logging
from .models import Chart, Planet, PlanetName, Sect, Sign
from .dignities import DignityCalculator

logger = logging.getLogger(__name__)

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

    # Obliquity of Ecliptic (J2000 fallback; prefer _get_obliquity(jd) for accuracy)
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

    @staticmethod
    def _get_obliquity(jd: float) -> float:
        """Compute true obliquity of the ecliptic for a given Julian Day via Swiss Ephemeris."""
        try:
            res = swe.calc_ut(jd, swe.ECL_NUT)
            coords = res[0] if isinstance(res[0], (list, tuple)) else res
            return coords[0]  # true obliquity
        except Exception as e:
            logger.debug("Obliquity calc failed: %s", e)
            return 23.4392911  # J2000 fallback

    @classmethod
    def ecliptic_to_equatorial(cls, lon: float, lat: float, epsilon: float = None) -> Tuple[float, float]:
        """
        Converts Ecliptic (Lon, Lat) to Equatorial (RA, Dec).
        If epsilon is None, uses the J2000 class constant.
        """
        lon_r = cls._to_rad(lon)
        lat_r = cls._to_rad(lat)
        eps = epsilon if epsilon is not None else cls.EPSILON
        eps_r = cls._to_rad(eps)

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
        # Compute obliquity from chart's Julian Day for accuracy
        epsilon = cls._get_obliquity(chart.jd) if hasattr(chart, 'jd') and chart.jd else cls.EPSILON
        # swe.house_pos calculates house cusps. We need the reverse or just use houses() with modified Time?
        # Simpler: Get RAMC from MC Longitude.
        mc_ra, _ = cls.ecliptic_to_equatorial(mc_lon, 0.0, epsilon)
        
        # Directed RAMC
        ramc_directed = (mc_ra + arc) % 360.0
        
        # Calculate new Ascendant for this RAMC
        # swe.houses_armc(armc, lat, eps, hsys) - armc is in deg
        try:
            # armc is RAMC.
            cusps, ascmc = swe.houses_armc(ramc_directed, geo_lat, epsilon, b'P')
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
                if p.name in [PlanetName.URANUS, PlanetName.NEPTUNE, PlanetName.PLUTO]:
                    continue
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
    def calculate_circumambulations(cls, chart: Chart, geo_lat: float, max_years: int = 80) -> List[Dict]:
        """
        Circumambulations through the Bounds (Ptolemy Tetrabiblos III.10).

        The master predictive technique of Ptolemaic astrology:
        - Directs the Ascendant forward 1° per year (Ptolemy Key).
        - At each year, records which Egyptian Term/Bound the directed Ascendant falls in.
        - The term ruler is the 'Distributor' — the planet governing that period of life.
        - When the Asc crosses from one bound to the next, there is a life transition.

        Returns a year-by-year table of bound rulers, signs, and partner planets.
        """
        from .reference_data import EGYPTIAN_TERMS
        from .calculations import format_longitude

        epsilon = cls._get_obliquity(chart.jd) if hasattr(chart, 'jd') and chart.jd else cls.EPSILON
        mc_ra, _ = cls.ecliptic_to_equatorial(chart.mc, 0.0, epsilon)
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT

        table = []
        prev_ruler = None

        for year in range(max_years + 1):
            arc = cls.ptolemy_key(float(year))
            ramc_dir = (mc_ra + arc) % 360.0

            try:
                _cusps, ascmc = swe.houses_armc(ramc_dir, geo_lat, epsilon, b'P')
                asc_dir_lon = ascmc[0]
            except Exception as e:
                logger.debug("Directed house calc failed for year %d: %s", year, e)
                continue

            # Determine which bound the directed Asc falls in
            sign_idx = int(asc_dir_lon / 30) % 12
            sign = list(Sign)[sign_idx]
            deg_in_sign = asc_dir_lon % 30

            terms_for_sign = EGYPTIAN_TERMS[sign]
            bound_ruler = None
            bound_start = 0
            bound_end = 0
            for ruler, end_deg in terms_for_sign:
                if deg_in_sign < end_deg:
                    bound_ruler = ruler
                    bound_end = end_deg
                    break
                bound_start = end_deg

            if not bound_ruler:
                bound_ruler = terms_for_sign[-1][0]
                bound_start = terms_for_sign[-2][1] if len(terms_for_sign) > 1 else 0
                bound_end = 30

            # Detect bound transitions
            is_transition = (prev_ruler is not None and bound_ruler != prev_ruler)
            prev_ruler = bound_ruler

            # Partner: planet aspecting the directed degree or domicile ruler
            dignities = DignityCalculator.get_essential_rulers(asc_dir_lon, sect)
            partner = dignities.get("domicile")
            partner_reason = "Domicile ruler"
            for p in chart.planets:
                if p.name in [PlanetName.URANUS, PlanetName.NEPTUNE, PlanetName.PLUTO,
                              PlanetName.NORTH_NODE, PlanetName.SOUTH_NODE]:
                    continue
                diff = abs(p.longitude - asc_dir_lon) % 360
                if diff > 180:
                    diff = 360 - diff
                for asp_angle in [0, 60, 90, 120, 180]:
                    if abs(diff - asp_angle) < 3.0:
                        partner = p.name
                        partner_reason = f"Aspecting ({p.name.value})"
                        break
                if partner != dignities.get("domicile"):
                    break

            fmt = format_longitude(asc_dir_lon)
            entry = {
                "age": year,
                "directed_asc_lon": round(asc_dir_lon, 4),
                "directed_asc_fmt": fmt["string"],
                "sign": sign.value,
                "bound_ruler": bound_ruler.value if hasattr(bound_ruler, "value") else str(bound_ruler),
                "bound_range": f"{bound_start}°–{bound_end}°",
                "partner": partner.value if hasattr(partner, "value") else str(partner),
                "partner_reason": partner_reason,
                "is_transition": is_transition,
            }
            table.append(entry)

        return table

    @classmethod
    def calculate_directions_to_angles(cls, chart: Chart, geo_lat: float) -> List[DirectionResult]:
        """
        Calculates directions of all planets to Conjunction/Opposition/Square/Trine/Sextile of Asc/MC.
        """
        results = []
        
        # 1. Chart Properties
        epsilon = cls._get_obliquity(chart.jd) if hasattr(chart, 'jd') and chart.jd else cls.EPSILON
        mc_ra, _ = cls.ecliptic_to_equatorial(chart.mc, 0.0, epsilon)
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
            if p.name in [PlanetName.NORTH_NODE, PlanetName.SOUTH_NODE]:
                continue
            if p.name in [PlanetName.URANUS, PlanetName.NEPTUNE, PlanetName.PLUTO]:
                # Non-traditional bodies should not be used as promittors in traditional primary directions.
                continue
            
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
                     ra_pt, dec_pt = cls.ecliptic_to_equatorial(lon_pt, 0.0, epsilon)
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
                     ra_pt, _ = cls.ecliptic_to_equatorial(lon_pt, 0.0, epsilon)
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

    @classmethod
    def calculate_directions_to_point(
        cls,
        chart: Chart,
        geo_lat: float,
        target_lon: float,
        target_label: str = "Point"
    ) -> List[DirectionResult]:
        """
        Calculate zodiacal primary directions of promittors to a generic ecliptic point.

        This is used for vitality auditing where the "Interfector" is the promittor (directed ray)
        that strikes the Hyleg (significator).

        Implementation note:
        - Treats the significator as an ecliptic point (lat=0) for auditability and stability.
        - This is a simplified "Placidus/Zodiacal" style direction: arc measured via OA.
        """
        results: List[DirectionResult] = []

        # Compute obliquity from chart's Julian Day for accuracy
        epsilon = cls._get_obliquity(chart.jd) if hasattr(chart, 'jd') and chart.jd else cls.EPSILON

        # OA of significator point (lat 0)
        ra_sig, dec_sig = cls.ecliptic_to_equatorial(cls._normalize_deg(target_lon), 0.0, epsilon)
        ad_sig = cls.calculate_ad(dec_sig, geo_lat)
        oa_sig = (ra_sig - ad_sig) % 360.0

        aspects_to_check = [
            ("Conjunction", 0),
            ("Sextile", 60),
            ("Square", 90),
            ("Trine", 120),
            ("Opposition", 180),
        ]

        for p in chart.planets:
            if p.name in [PlanetName.NORTH_NODE, PlanetName.SOUTH_NODE]:
                continue
            if p.name in [PlanetName.URANUS, PlanetName.NEPTUNE, PlanetName.PLUTO]:
                continue

            for asp_name, asp_angle in aspects_to_check:
                aspect_lons = []
                if asp_angle == 0:
                    aspect_lons = [(p.longitude, "Conjunction")]
                elif asp_angle == 180:
                    aspect_lons = [((p.longitude + 180) % 360, "Opposition")]
                else:
                    aspect_lons = [
                        ((p.longitude + asp_angle) % 360, f"{asp_name} (Dexter)"),
                        ((p.longitude - asp_angle) % 360, f"{asp_name} (Sinister)"),
                    ]

                for lon_pt, name_pt in aspect_lons:
                    ra_pt, dec_pt = cls.ecliptic_to_equatorial(lon_pt, 0.0, epsilon)
                    ad_pt = cls.calculate_ad(dec_pt, geo_lat)
                    oa_pt = (ra_pt - ad_pt) % 360.0

                    arc = oa_pt - oa_sig
                    if arc < 0:
                        arc += 360.0

                    # Practical range filter for report usefulness (0-100 years)
                    if 0 < arc < 100:
                        results.append(
                            DirectionResult(
                                significator=target_label,
                                promittor=p.name.value,
                                aspect=name_pt,
                                arc=arc,
                                years=cls.ptolemy_key(arc),
                                date_offset=cls.format_years(arc),
                                method="Placidus/Zodiacal",
                            )
                        )

        return sorted(results, key=lambda x: x.years)

    @classmethod
    def calculate_directions_to_planets(cls, chart: Chart, geo_lat: float) -> List[DirectionResult]:
        """
        Directs each traditional planet to every other planet's natal position.
        
        This completes the primary directions suite:
        - calculate_directions_to_angles: planets to Asc/MC
        - calculate_directions_to_point: planets to arbitrary point (Hyleg)
        - calculate_directions_to_planets: planets to each other
        
        Returns all planet-to-planet directions within 80 years.
        """
        results: List[DirectionResult] = []
        traditional = [p for p in chart.planets 
                       if p.name not in [PlanetName.NORTH_NODE, PlanetName.SOUTH_NODE,
                                         PlanetName.URANUS, PlanetName.NEPTUNE, PlanetName.PLUTO]]
        
        epsilon = cls._get_obliquity(chart.jd) if hasattr(chart, 'jd') and chart.jd else cls.EPSILON
        
        aspects_to_check = [
            ("Conjunction", 0),
            ("Square", 90),
            ("Opposition", 180),
        ]
        
        for sig in traditional:
            # OA of the significator (the planet being aspected)
            ra_sig, dec_sig = cls.ecliptic_to_equatorial(sig.longitude, 0.0, epsilon)
            ad_sig = cls.calculate_ad(dec_sig, geo_lat)
            oa_sig = (ra_sig - ad_sig) % 360.0
            
            for prom in traditional:
                if prom.name == sig.name:
                    continue
                
                for asp_name, asp_angle in aspects_to_check:
                    if asp_angle == 0:
                        aspect_lons = [(prom.longitude, "Conjunction")]
                    elif asp_angle == 180:
                        aspect_lons = [((prom.longitude + 180) % 360, "Opposition")]
                    else:
                        aspect_lons = [
                            ((prom.longitude + asp_angle) % 360, f"{asp_name} (Dexter)"),
                            ((prom.longitude - asp_angle) % 360, f"{asp_name} (Sinister)"),
                        ]
                    
                    for lon_pt, name_pt in aspect_lons:
                        ra_pt, dec_pt = cls.ecliptic_to_equatorial(lon_pt, 0.0, epsilon)
                        ad_pt = cls.calculate_ad(dec_pt, geo_lat)
                        oa_pt = (ra_pt - ad_pt) % 360.0
                        
                        arc = oa_pt - oa_sig
                        if arc < 0:
                            arc += 360.0
                        
                        if 0 < arc < 80:
                            results.append(DirectionResult(
                                significator=sig.name.value,
                                promittor=prom.name.value,
                                aspect=name_pt,
                                arc=arc,
                                years=cls.ptolemy_key(arc),
                                date_offset=cls.format_years(arc),
                                method="Placidus/Zodiacal",
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
