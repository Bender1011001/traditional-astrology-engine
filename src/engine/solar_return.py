import logging
from datetime import datetime
from typing import Dict

from .models import Chart, Planet, PlanetName, Sign

logger = logging.getLogger(__name__)
from .dignities import DignityCalculator
from .reference_data import DOMICILES


class SolarReturnEngine:
    """
    Implements Morin's Hierarchical Determination for Solar Returns.
    Axiom: The SR cannot produce what the Nativity does not promise.
    """

    @staticmethod
    def calculate(
        birth_dt: datetime,
        birth_city: str,
        birth_state: str,
        return_year: int,
        return_city: str,
        return_state: str,
    ) -> Dict:
        """
        Main entry point for generating a solar return chart report.
        """
        import swisseph as swe

        from .calculator.main import ChartCalculator

        calc = ChartCalculator()

        natal_chart = calc.calculate_chart(birth_dt, birth_city, birth_state)

        natal_sun = next(
            (p for p in natal_chart.planets if p.name == PlanetName.SUN), None
        )
        if not natal_sun:
            raise ValueError("Natal chart has no Sun.")

        sun_lon = natal_sun.longitude

        t_approx = swe.julday(
            return_year,
            birth_dt.month,
            birth_dt.day,
            birth_dt.hour + birth_dt.minute / 60.0,
        )

        curr_jd = t_approx
        for _ in range(30):
            res_sun = swe.calc_ut(curr_jd, swe.SUN, swe.FLG_SWIEPH)
            lon = res_sun[0][0]

            diff = lon - sun_lon
            if diff > 180:
                diff -= 360
            if diff < -180:
                diff += 360

            if abs(diff) < 0.0001:
                break

            curr_jd -= diff / 0.9856

        sr_jd = curr_jd
        age = return_year - birth_dt.year

        return SolarReturnEngine.analyze_solar_return_from_jd(
            natal_chart, sr_jd, age, birth_dt
        )

    @staticmethod
    def analyze_solar_return_from_jd(
        natal_chart: Chart, sr_jd: float, age: int, birth_dt: datetime
    ) -> Dict:
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
            if pid is None:
                continue

            try:
                res = swe.calc_ut(sr_jd, pid, flag_sr)[0]
                sr_planets.append(
                    Planet(
                        name=pname_enum, longitude=res[0], latitude=res[1], speed=res[3]
                    )
                )
            except Exception as e:
                logger.warning(
                    "SR planet calc failed for %s: %s",
                    pname_enum,
                    repr(e),
                    exc_info=True,
                )
                continue

        # SR Houses
        # Note: We use b'P' for Placidus, but Whole Sign 'W' is often preferred.
        # Using Placidus for the angles and house cusps as a default.
        sr_cusps, sr_ascmc = swe.houses(
            sr_jd, natal_chart.geo_lat, natal_chart.geo_lon, b"P"
        )

        sr_chart = Chart(
            sun_altitude=0,  # Not strictly needed for SR analysis logic as written
            planets=sr_planets,
            ascendant=sr_ascmc[0],
            mc=sr_ascmc[1],
            houses={i + 1: c for i, c in enumerate(sr_cusps)},
            geo_lat=natal_chart.geo_lat,
            geo_lon=natal_chart.geo_lon,
            jd=sr_jd,
        )

        res = SolarReturnEngine.analyze_solar_return(sr_chart, natal_chart, age)
        res["year"] = birth_dt.year + age
        return res

    @staticmethod
    def analyze_solar_return(sr_chart: Chart, natal_chart: Chart, age: int) -> Dict:
        """
        Synthesizes the Solar Return by overlaying it on the Natal Chart.
        Uses Medieval 'Lord of the Year' (Ruler of the Revolution) logic.
        """
        # 1. Muntha (Profected Ascendant)
        # 1 sign per year from natal asc sign
        natal_asc_sign_idx = int(natal_chart.ascendant / 30) % 12
        muntha_sign_idx = (natal_asc_sign_idx + age) % 12
        muntha_sign = list(Sign)[muntha_sign_idx]
        muntha_lon = (muntha_sign_idx * 30.0) + (natal_chart.ascendant % 30)

        # Muntha position in SR Houses
        muntha_sr_house = DignityCalculator.get_house_number(
            muntha_lon, sr_chart.ascendant, sr_chart.houses
        )
        muntha_natal_house = DignityCalculator.get_house_number(
            muntha_lon, natal_chart.ascendant, natal_chart.houses
        )

        # 2. Lord of the Year (LoY) Candidates
        # A. Ruler of Muntha
        loy_muntha = DOMICILES[muntha_sign]

        # B. Ruler of SR Ascendant
        sr_asc_sign = list(Sign)[int(sr_chart.ascendant / 30) % 12]
        loy_sr_asc = DOMICILES[sr_asc_sign]

        # C. Lord of the Profection (usually same as Muntha ruler)
        # We select the Muntha Ruler as the primary 'Lord of the Year' per traditional standard
        loy_name = loy_muntha

        # 3. LoY Assessment (Condition & Handover)
        loy_sr_planet = next((p for p in sr_chart.planets if p.name == loy_name), None)
        loy_natal_planet = next(
            (p for p in natal_chart.planets if p.name == loy_name), None
        )

        loy_weight = 0
        loy_details = []

        if loy_sr_planet:
            # Rulership of SR Ascendant (+5 bonus if same)
            if loy_name == loy_sr_asc:
                loy_weight += 5
                loy_details.append("Ruler of SR Ascendant (+5)")

            # SR House Position
            sr_h = DignityCalculator.get_house_number(
                loy_sr_planet.longitude, sr_chart.ascendant, sr_chart.houses
            )
            if sr_h in [1, 4, 7, 10]:
                loy_weight += 10
                loy_details.append(f"Angular in SR (House {sr_h}) (+10)")
            elif sr_h in [3, 6, 9, 12]:
                loy_weight -= 10
                loy_details.append(f"Cadent in SR (House {sr_h}) (-10)")

            # Essential Dignity in SR
            # (Simplified check)
            sr_sign = list(Sign)[int(loy_sr_planet.longitude / 30) % 12]
            if sr_sign == muntha_sign:
                loy_weight += 5
                loy_details.append(f"In Muntha Sign in SR (+5)")

        # 4. Morin's Handover (Activation)
        # Does the SR planet aspect its Natal position or the Natal Ascendant?
        handover_active = False
        if loy_sr_planet and loy_natal_planet:
            diff = abs(loy_sr_planet.longitude - loy_natal_planet.longitude) % 360
            dist = diff if diff <= 180 else 360 - diff
            if dist < 8.0:  # Conjunction activation
                handover_active = True
                loy_details.append("Natal Handover Active (SR Lord on Natal Position)")

        # 5. Planetary Determinations (Traditional Overlay)
        determinations = []
        for p in sr_chart.planets:
            if p.name in [
                PlanetName.SUN,
                PlanetName.MOON,
                PlanetName.NORTH_NODE,
                PlanetName.SOUTH_NODE,
            ]:
                continue

            sr_h = DignityCalculator.get_house_number(
                p.longitude, sr_chart.ascendant, sr_chart.houses
            )
            natal_h = DignityCalculator.get_house_number(
                p.longitude, natal_chart.ascendant, natal_chart.houses
            )

            determinations.append(
                {
                    "planet": p.name.value,
                    "sr_house": sr_h,
                    "natal_house_overlay": natal_h,
                    "judgment": f"{p.name.value} in SR House {sr_h} overlays Natal House {natal_h}.",
                }
            )

        return {
            "muntha": {
                "sign": muntha_sign.value,
                "sr_house": muntha_sr_house,
                "natal_house": muntha_natal_house,
            },
            "lord_of_year": {
                "name": loy_name.value,
                "weight": loy_weight,
                "details": loy_details,
                "handover_active": handover_active,
            },
            "determinations": determinations,
            "morin_axiom": "The Solar Return cannot produce what the Nativity does not promise.",
        }
