import logging
import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

import swisseph as swe

from .dignities import DignityCalculator
from .models import Chart, Planet, PlanetName, Sect, Sign

logger = logging.getLogger(__name__)


@dataclass
class DirectionResult:
    significator: str
    promittor: str
    aspect: str
    arc: float
    years: float
    date_offset: str  # "X years Y months"
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
    mundane_pos: float  # Equivalent to a 1-12 house coordinate (Proportional distance)


class PrimaryDirectionsEngine:
    """
    Implements a mixed primary-direction toolkit.

    The angle and point routines below are a configured zodiacal
    oblique-ascension method with latitude-free aspect points.  They are not a
    complete Placidus semi-arc implementation and must not be labeled as one.
    The speculum helpers support separate mundane work.
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
            logger.warning("Obliquity calc failed: %s", repr(e), exc_info=True)
            return 23.4392911  # J2000 fallback

    @classmethod
    def ecliptic_to_equatorial(
        cls, lon: float, lat: float, epsilon: float = None  # type: ignore
    ) -> Tuple[float, float]:
        """
        Converts Ecliptic (Lon, Lat) to Equatorial (RA, Dec).
        If epsilon is None, uses the J2000 class constant.
        """
        lon_r = cls._to_rad(lon)
        lat_r = cls._to_rad(lat)
        eps = epsilon if epsilon is not None else cls.EPSILON
        eps_r = cls._to_rad(eps)

        # sin(delta) = sin(eps)*sin(lon)*cos(lat) + cos(eps)*sin(lat)
        sin_dec = math.sin(eps_r) * math.sin(lon_r) * math.cos(lat_r) + math.cos(
            eps_r
        ) * math.sin(lat_r)
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
            return 0.0  # Circumpolar fallback (simplified)
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
        if sa == 0:
            return 0.0
        ratio = abs(md) / sa
        tan_pole = ratio * math.tan(cls._to_rad(geo_lat))
        return cls._to_deg(math.atan(tan_pole))

    @classmethod
    def _get_pole_and_hemisphere(
        cls, ra: float, dec: float, ramc: float, geo_lat: float
    ) -> Tuple[float, bool]:
        md = cls.calculate_md(ra, ramc)
        dsa, nsa = cls.calculate_semi_arcs(dec, geo_lat)
        sa = dsa if abs(md) < dsa else nsa
        pole = cls.calculate_pole(md, sa, geo_lat)
        return pole, md >= 0

    @classmethod
    def calculate_mundane_position(
        cls, ra: float, dec: float, ramc: float, geo_lat: float
    ) -> float:
        """
        Calculates the 1-12 'proportional house position'.
        Standardized: MC=10.0, Asc=1.0, IC=4.0, Dsc=7.0.
        Uses Semi-Arc proportionality.
        """
        md = cls.calculate_md(ra, ramc)
        dsa, nsa = cls.calculate_semi_arcs(dec, geo_lat)

        # Determine Quadrant
        is_above = abs(md) < dsa
        is_east = md < 0  # Simplified: RA_Planet < RA_MC?
        # (Actually md is ra-ramc. If ra < ramc, md < 0 -> East of Meridian)

        if is_above:
            # 7-10 (West) or 10-1 (East)
            ratio = abs(md) / dsa  # 0 at MC, 1.0 at Horiz
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
            ratio = abs(md_ic) / nsa  # 0 at IC, 1.0 at Horiz
            if is_east:
                # 4 to 1
                return 4.0 - (ratio * 3.0)
            else:
                # 4 to 7
                return 4.0 + (ratio * 3.0)

    @classmethod
    def get_full_speculum(
        cls, planet: Planet, ramc: float, geo_lat: float
    ) -> MundaneSpeculum:
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
            ra=ra,
            dec=dec,
            ad=ad,
            dsa=dsa,
            nsa=nsa,
            md=md,
            pole=pole,
            mundane_pos=m_pos,
        )

    @classmethod
    def calculate_current_distributor(
        cls, chart: Chart, age_years: float, geo_lat: float, key: str = "Naibod"
    ) -> Dict:
        """
        Calculates the current 'Distributor' (Term Ruler of Directed Ascendant).
        Algorithm:
        1. Calculate Arc = Age (Ptolemy/Naibod Key).
        2. Direct the Ascendant by this Arc (OA_Dir = OA_Radical + Arc).
        3. Convert OA_Dir back to Zodiacal Longitude.
        4. Find the Term Ruler of that Longitude.
        """
        arc = cls.get_arc_from_years(age_years, key)

        # 1. Get Natal OA of Ascendant
        # We can simulate this by calculating the RAMC that would put the Ascendant at the horizon + Arc?
        # NO. Directing the Ascendant:
        # OA_Asc_Dir = OA_Asc_Natal + Arc.
        # Then find the Ecliptic point that has this OA.
        # This point is the Ascendant of a chart with RAMC' = RAMC_Natal + Arc.

        # Get Natal RAMC (RA of MC)
        mc_lon = chart.mc
        # Compute obliquity from chart's Julian Day for accuracy
        epsilon = (
            cls._get_obliquity(chart.jd)
            if hasattr(chart, "jd") and chart.jd
            else cls.EPSILON
        )
        # swe.house_pos calculates house cusps. We need the reverse or just use houses() with modified Time?
        # Simpler: Get RAMC from MC Longitude.
        mc_ra, _ = cls.ecliptic_to_equatorial(mc_lon, 0.0, epsilon)

        # Directed RAMC
        ramc_directed = (mc_ra + arc) % 360.0

        # Calculate new Ascendant for this RAMC
        # swe.houses_armc(armc, lat, eps, hsys) - armc is in deg
        try:
            # armc is RAMC.
            cusps, ascmc = swe.houses_armc(ramc_directed, geo_lat, epsilon, b"P")
            asc_directed_lon = ascmc[0]

            # Get Term Ruler
            sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
            dignities = DignityCalculator.get_essential_rulers(asc_directed_lon, sect)
            term_ruler = dignities["term"]

            # Ptolemy IV.10: a ray reaching the prorogator governs until the
            # next ray arrives.  Select the most recent directed ray, not an
            # arbitrary planet found within a present-time three-degree orb.
            asc_rays = [
                direction
                for direction in cls.calculate_directions_to_angles(
                    chart, geo_lat, key
                )
                if direction.significator == "Ascendant"
                and direction.years <= age_years
            ]
            if asc_rays:
                last_ray = max(asc_rays, key=lambda direction: direction.years)
                partner = last_ray.promittor
                partner_reason = (
                    f"Last directed ray: {last_ray.promittor} {last_ray.aspect} "
                    f"at age {last_ray.years:.2f}"
                )
            else:
                partner = dignities["domicile"]
                partner_reason = "Configured natal fallback before first directed ray"

            return {
                "type": "Distributor (Term Ruler)",
                "planet": (
                    term_ruler.value
                    if hasattr(term_ruler, "value")
                    else str(term_ruler)
                ),
                "partner": partner.value if hasattr(partner, "value") else str(partner),
                "partner_reason": partner_reason,
                "directed_ascendant_deg": asc_directed_lon,
                "arc": arc,
                "description": f"The Directed Ascendant is at {asc_directed_lon:.2f}°, in the Terms of {term_ruler.value if hasattr(term_ruler, 'value') else term_ruler}. Partner: {partner.value if hasattr(partner, 'value') else partner} ({partner_reason}).",
            }
        except Exception as e:
            return {"error": str(e)}

    @classmethod
    def calculate_circumambulations(
        cls, chart: Chart, geo_lat: float, max_years: int = 80, key: str = "Ptolemy"
    ) -> List[Dict]:
        """
        Circumambulations through the Bounds (Ptolemy Tetrabiblos IV.10).
        Kept on Ptolemy's own 1deg=1yr key: this is Ptolemy's technique, not
        Lilly's - Lilly's stated preference for Naibod applies to his own
        primary-directions chapters (Christian Astrology pp.708-715), not to
        a different author's different technique reusing this module.

        The master predictive technique of Ptolemaic astrology:
        - Directs the Ascendant forward (Ptolemy/Naibod Key).
        - At each year, records which Egyptian Term/Bound the directed Ascendant falls in.
        - The term ruler is the 'Distributor' — the planet governing that period of life.
        - When the Asc crosses from one bound to the next, there is a life transition.

        Returns a year-by-year table of bound rulers, signs, and partner planets.
        """
        from .calculations import format_longitude
        from .reference_data import EGYPTIAN_TERMS

        epsilon = (
            cls._get_obliquity(chart.jd)
            if hasattr(chart, "jd") and chart.jd
            else cls.EPSILON
        )
        mc_ra, _ = cls.ecliptic_to_equatorial(chart.mc, 0.0, epsilon)
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT

        table = []
        prev_ruler = None
        asc_rays = sorted(
            (
                direction
                for direction in cls.calculate_directions_to_angles(
                    chart, geo_lat, key
                )
                if direction.significator == "Ascendant"
            ),
            key=lambda direction: direction.years,
        )

        def _directed_asc_at_age(age_years: float) -> float:
            arc_at_age = cls.get_arc_from_years(age_years, key)
            ramc_at_age = (mc_ra + arc_at_age) % 360.0
            _cusps_at_age, ascmc_at_age = swe.houses_armc(
                ramc_at_age, geo_lat, epsilon, b"P"
            )
            return float(ascmc_at_age[0])

        def _bound_ruler_at_age(age_years: float) -> PlanetName:
            longitude = _directed_asc_at_age(age_years)
            sign_at_age = list(Sign)[int(longitude / 30.0) % 12]
            degree_at_age = longitude % 30.0
            for ruler_at_age, end_degree in EGYPTIAN_TERMS[sign_at_age]:
                if degree_at_age < end_degree:
                    return ruler_at_age
            return EGYPTIAN_TERMS[sign_at_age][-1][0]

        for year in range(max_years + 1):
            arc = cls.get_arc_from_years(float(year), key)
            ramc_dir = (mc_ra + arc) % 360.0

            try:
                _cusps, ascmc = swe.houses_armc(ramc_dir, geo_lat, epsilon, b"P")
                asc_dir_lon = ascmc[0]
            except Exception as e:
                logger.warning(
                    "Directed house calc failed for year %d: %s",
                    year,
                    repr(e),
                    exc_info=True,
                )
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
            prior_ruler = prev_ruler
            is_transition = prior_ruler is not None and bound_ruler != prior_ruler
            exact_transition_age = None
            if is_transition and year > 0:
                low = float(year - 1)
                high = float(year)
                # The directed Ascendant moves smoothly in this configured
                # model. Bisect the first instant at which the new bound ruler
                # replaces the prior ruler instead of reporting only the next
                # whole-year sample.
                for _ in range(48):
                    middle = (low + high) / 2.0
                    if _bound_ruler_at_age(middle) == prior_ruler:
                        low = middle
                    else:
                        high = middle
                exact_transition_age = high
            prev_ruler = bound_ruler

            # Partner: the most recent ray to reach the Ascendant prorogation.
            dignities = DignityCalculator.get_essential_rulers(asc_dir_lon, sect)
            partner = dignities.get("domicile")
            partner_reason = "Configured natal fallback before first directed ray"
            prior_rays = [ray for ray in asc_rays if ray.years <= year]
            if prior_rays:
                last_ray = prior_rays[-1]
                partner = last_ray.promittor
                partner_reason = (
                    f"Last directed ray: {last_ray.promittor} {last_ray.aspect} "
                    f"at age {last_ray.years:.2f}"
                )

            fmt = format_longitude(asc_dir_lon)
            entry = {
                "age": year,
                "directed_asc_lon": round(asc_dir_lon, 4),
                "directed_asc_fmt": fmt["string"],
                "sign": sign.value,
                "bound_ruler": (
                    bound_ruler.value
                    if hasattr(bound_ruler, "value")
                    else str(bound_ruler)
                ),
                "bound_range": f"{bound_start}°–{bound_end}°",
                "partner": partner.value if hasattr(partner, "value") else str(partner),  # type: ignore
                "partner_reason": partner_reason,
                "is_transition": is_transition,
                "exact_transition_age": (
                    round(exact_transition_age, 6)
                    if exact_transition_age is not None
                    else None
                ),
            }
            table.append(entry)

        return table

    @classmethod
    def calculate_directions_to_angles(
        cls, chart: Chart, geo_lat: float, key: str = "Naibod"
    ) -> List[DirectionResult]:
        """
        Calculates directions of all planets to Conjunction/Opposition/Square/Trine/Sextile of Asc/MC.
        """
        results = []

        # 1. Chart Properties
        epsilon = (
            cls._get_obliquity(chart.jd)
            if hasattr(chart, "jd") and chart.jd
            else cls.EPSILON
        )
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
            ("Opposition", 180, True),
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
                        ((p.longitude - asp_angle) % 360, f"{asp_name} (Sinister)"),
                    ]

                for lon_pt, name_pt in aspect_lons:
                    # Calculate OA of this aspect point (Lat 0 assumed for aspects usually)
                    ra_pt, dec_pt = cls.ecliptic_to_equatorial(lon_pt, 0.0, epsilon)
                    ad_pt = cls.calculate_ad(dec_pt, geo_lat)
                    oa_pt = (ra_pt - ad_pt) % 360.0

                    arc = oa_pt - oa_asc
                    # Normalize
                    if arc < 0:
                        arc += 360

                    if 0 < arc < 100:
                        results.append(
                            DirectionResult(
                                significator="Ascendant",
                                promittor=p.name.value,
                                aspect=name_pt,
                                arc=arc,
                                years=cls.get_years_from_arc(arc, key),
                                date_offset=cls.format_years(cls.get_years_from_arc(arc, key)),
                                method="Configured zodiacal OA",
                            )
                        )

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
                        ((p.longitude - asp_angle) % 360, f"{asp_name} (Sinister)"),
                    ]

                for lon_pt, name_pt in aspect_lons:
                    ra_pt, _ = cls.ecliptic_to_equatorial(lon_pt, 0.0, epsilon)
                    arc = (ra_pt - mc_ra) % 360.0

                    if 0 < arc < 100:
                        results.append(
                            DirectionResult(
                                significator="Midheaven",
                                promittor=p.name.value,
                                aspect=name_pt,
                                arc=arc,
                                years=cls.get_years_from_arc(arc, key),
                                date_offset=cls.format_years(cls.get_years_from_arc(arc, key)),
                                method="Configured zodiacal OA",
                            )
                        )

        return sorted(results, key=lambda x: x.years)

    @classmethod
    def calculate_directions_to_point(
        cls,
        chart: Chart,
        geo_lat: float,
        target_lon: float,
        target_label: str = "Point",
        key: str = "Naibod",
    ) -> List[DirectionResult]:
        """
        Calculate zodiacal primary directions of promittors to a generic ecliptic point.

        This is used for vitality auditing where the "Interfector" is the promittor (directed ray)
        that strikes the Hyleg (significator).

        Implementation note:
        - Treats the significator as an ecliptic point (lat=0) for auditability and stability.
        - This is a configured zodiacal direction: arc measured via OA with
          latitude-free ecliptic aspect points.
        """
        results: List[DirectionResult] = []

        # Compute obliquity from chart's Julian Day for accuracy
        epsilon = (
            cls._get_obliquity(chart.jd)
            if hasattr(chart, "jd") and chart.jd
            else cls.EPSILON
        )
        ramc, _ = cls.ecliptic_to_equatorial(chart.mc, 0.0, epsilon)

        # OA of significator point (lat 0) using its actual Pole
        ra_sig, dec_sig = cls.ecliptic_to_equatorial(
            cls._normalize_deg(target_lon), 0.0, epsilon
        )
        pole_sig, is_east = cls._get_pole_and_hemisphere(ra_sig, dec_sig, ramc, geo_lat)
        ad_sig = cls.calculate_ad(dec_sig, pole_sig)
        oa_sig = (ra_sig - ad_sig) % 360.0 if is_east else (ra_sig + ad_sig) % 360.0

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
                    ad_pt = cls.calculate_ad(dec_pt, pole_sig)
                    oa_pt = (
                        (ra_pt - ad_pt) % 360.0 if is_east else (ra_pt + ad_pt) % 360.0
                    )

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
                                years=cls.get_years_from_arc(arc, key),
                                date_offset=cls.format_years(cls.get_years_from_arc(arc, key)),
                                method="Configured zodiacal OA",
                            )
                        )

        return sorted(results, key=lambda x: x.years)

    @classmethod
    def calculate_directions_to_planets(
        cls, chart: Chart, geo_lat: float, key: str = "Naibod"
    ) -> List[DirectionResult]:
        """
        Directs each traditional planet to every other planet's natal position.

        This completes the primary directions suite:
        - calculate_directions_to_angles: planets to Asc/MC
        - calculate_directions_to_point: planets to arbitrary point (Hyleg)
        - calculate_directions_to_planets: planets to each other

        Returns all planet-to-planet directions within 80 years.
        """
        results: List[DirectionResult] = []
        traditional = [
            p
            for p in chart.planets
            if p.name
            not in [
                PlanetName.NORTH_NODE,
                PlanetName.SOUTH_NODE,
                PlanetName.URANUS,
                PlanetName.NEPTUNE,
                PlanetName.PLUTO,
            ]
        ]

        epsilon = (
            cls._get_obliquity(chart.jd)
            if hasattr(chart, "jd") and chart.jd
            else cls.EPSILON
        )
        ramc, _ = cls.ecliptic_to_equatorial(chart.mc, 0.0, epsilon)

        aspects_to_check = [
            ("Conjunction", 0),
            ("Square", 90),
            ("Opposition", 180),
        ]

        for sig in traditional:
            # OA of the significator (the planet being aspected) under its own Pole
            ra_sig, dec_sig = cls.ecliptic_to_equatorial(sig.longitude, 0.0, epsilon)
            pole_sig, is_east = cls._get_pole_and_hemisphere(
                ra_sig, dec_sig, ramc, geo_lat
            )
            ad_sig = cls.calculate_ad(dec_sig, pole_sig)
            oa_sig = (ra_sig - ad_sig) % 360.0 if is_east else (ra_sig + ad_sig) % 360.0

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
                            (
                                (prom.longitude + asp_angle) % 360,
                                f"{asp_name} (Dexter)",
                            ),
                            (
                                (prom.longitude - asp_angle) % 360,
                                f"{asp_name} (Sinister)",
                            ),
                        ]

                    for lon_pt, name_pt in aspect_lons:
                        ra_pt, dec_pt = cls.ecliptic_to_equatorial(lon_pt, 0.0, epsilon)
                        ad_pt = cls.calculate_ad(dec_pt, pole_sig)
                        oa_pt = (
                            (ra_pt - ad_pt) % 360.0
                            if is_east
                            else (ra_pt + ad_pt) % 360.0
                        )

                        arc = oa_pt - oa_sig
                        if arc < 0:
                            arc += 360.0

                        if 0 < arc < 80:
                            results.append(
                                DirectionResult(
                                    significator=sig.name.value,
                                    promittor=prom.name.value,
                                    aspect=name_pt,
                                    arc=arc,
                                    years=cls.get_years_from_arc(arc, key),
                                    date_offset=cls.format_years(cls.get_years_from_arc(arc, key)),
                                    method="Configured zodiacal OA",
                                )
                            )

        return sorted(results, key=lambda x: x.years)

    @staticmethod
    def ptolemy_key(arc: float) -> float:
        """1 degree = 1 year"""
        return arc

    @staticmethod
    def naibod_key(arc: float) -> float:
        """0.9856 degrees = 1 year"""
        return arc / 0.9856

    @classmethod
    def get_years_from_arc(cls, arc: float, key: str = "Naibod") -> float:
        if key == "Naibod":
            return cls.naibod_key(arc)
        return cls.ptolemy_key(arc)

    @classmethod
    def get_arc_from_years(cls, years: float, key: str = "Naibod") -> float:
        if key == "Naibod":
            return years * 0.9856
        return years

    @staticmethod
    def format_years(years: float) -> str:
        y = int(years)
        m = int((years - y) * 12)
        return f"{y}y {m}m"
