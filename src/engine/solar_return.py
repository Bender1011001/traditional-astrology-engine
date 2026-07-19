import logging
from datetime import datetime
from typing import Dict

from .models import Chart, Planet, PlanetName, Sect, Sign

logger = logging.getLogger(__name__)
from .dignities import DignityCalculator
from .reference_data import DOMICILES


class SolarReturnEngine:
    """
    Source-scoped annual revolution analysis.

    The customer layer follows Ibn Ezra's Book of Revolution: cast the exact
    return of the Sun, compare return planets with the nativity, inspect the
    return Ascendant and its ruler, and compare the sect-light triplicity ruler
    in both figures.  Tajika Muntha, arbitrary point weights, and a supposed
    "Morin handover" are intentionally not mixed into this method.
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

        # The report's pre-modern core uses whole-sign topical places.  The
        # exact Ascendant and Midheaven remain astronomical angles.
        sr_cusps, sr_ascmc = swe.houses(
            sr_jd, natal_chart.geo_lat, natal_chart.geo_lon, b"W"
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
            house_system="W",
        )

        res = SolarReturnEngine.analyze_solar_return(sr_chart, natal_chart, age)
        res["year"] = birth_dt.year + age
        y, m, d, hour = swe.revjul(sr_jd)
        hh = int(hour)
        minute_float = (hour - hh) * 60.0
        mm = int(minute_float)
        ss = int(round((minute_float - mm) * 60.0))
        if ss == 60:
            ss = 0
            mm += 1
        if mm == 60:
            mm = 0
            hh += 1
        res["return_datetime_utc"] = (
            f"{int(y):04d}-{int(m):02d}-{int(d):02d}T{hh:02d}:{mm:02d}:{ss:02d}Z"
        )
        return res

    @staticmethod
    def analyze_solar_return(sr_chart: Chart, natal_chart: Chart, age: int) -> Dict:
        """
        Compare the exact annual revolution with the natal figure.
        """
        septener = {
            PlanetName.SUN,
            PlanetName.MOON,
            PlanetName.MERCURY,
            PlanetName.VENUS,
            PlanetName.MARS,
            PlanetName.JUPITER,
            PlanetName.SATURN,
        }
        is_day = natal_chart.sun_altitude > 0.0
        natal_sect = Sect.DAY if is_day else Sect.NIGHT

        def whole_sign_house(longitude: float, ascendant: float) -> int:
            return (int(longitude / 30) - int(ascendant / 30)) % 12 + 1

        # Ibn Ezra calls the ruler of the return Ascendant a witness.  It is not
        # silently replaced by the ruler of a separately imported Muntha.
        sr_asc_sign = list(Sign)[int(sr_chart.ascendant / 30) % 12]
        return_ruler_name = DOMICILES[sr_asc_sign]
        return_ruler = next(
            (p for p in sr_chart.planets if p.name == return_ruler_name), None
        )
        return_ruler_payload: Dict[str, object] = {
            "name": return_ruler_name.value,
            "return_ascendant_sign": sr_asc_sign.value,
        }
        if return_ruler:
            dignity = DignityCalculator.calculate_planet_dignity(
                return_ruler.name, return_ruler.longitude, natal_sect
            )
            return_ruler_payload.update(
                {
                    "return_sign": return_ruler.sign.value,
                    "return_house": whole_sign_house(
                        return_ruler.longitude, sr_chart.ascendant
                    ),
                    "essential_score": dignity.get("total_score"),
                    "essential_details": dignity.get("details", []),
                    "retrograde": return_ruler.is_retrograde,
                }
            )

        # Compare each visible planet's return place with its natal place.
        determinations = []
        for p in sr_chart.planets:
            if p.name not in septener:
                continue
            sr_h = whole_sign_house(p.longitude, sr_chart.ascendant)
            natal_h = whole_sign_house(p.longitude, natal_chart.ascendant)
            dignity = DignityCalculator.calculate_planet_dignity(
                p.name, p.longitude, natal_sect
            )

            determinations.append(
                {
                    "planet": p.name.value,
                    "return_sign": p.sign.value,
                    "sr_house": sr_h,
                    "natal_house_overlay": natal_h,
                    "essential_score": dignity.get("total_score"),
                    "essential_details": dignity.get("details", []),
                    "retrograde": p.is_retrograde,
                    "judgment": f"{p.name.value} in return whole-sign house {sr_h} overlays natal whole-sign house {natal_h}.",
                }
            )

        # Ibn Ezra explicitly tells the reader to compare the sect-light
        # triplicity ruler's condition in the nativity and revolution.
        sect_light = next(
            (
                p
                for p in natal_chart.planets
                if p.name == (PlanetName.SUN if is_day else PlanetName.MOON)
            ),
            None,
        )
        triplicity_comparison: Dict[str, object] = {}
        if sect_light:
            element = DignityCalculator.ZODIAC_ELEMENTS.get(sect_light.sign)
            rulers = DignityCalculator.TRIPLICITY_RULERS.get(element) if element else None
            if rulers:
                ruler_name = rulers[0] if is_day else rulers[1]
                natal_ruler = next(
                    (p for p in natal_chart.planets if p.name == ruler_name), None
                )
                sr_ruler = next(
                    (p for p in sr_chart.planets if p.name == ruler_name), None
                )
                if natal_ruler and sr_ruler:
                    natal_dignity = DignityCalculator.calculate_planet_dignity(
                        ruler_name, natal_ruler.longitude, natal_sect
                    )
                    return_dignity = DignityCalculator.calculate_planet_dignity(
                        ruler_name, sr_ruler.longitude, natal_sect
                    )
                    triplicity_comparison = {
                        "ruler": ruler_name.value,
                        "natal_house": whole_sign_house(
                            natal_ruler.longitude, natal_chart.ascendant
                        ),
                        "return_house": whole_sign_house(
                            sr_ruler.longitude, sr_chart.ascendant
                        ),
                        "natal_essential_score": natal_dignity.get("total_score"),
                        "return_essential_score": return_dignity.get("total_score"),
                        "natal_retrograde": natal_ruler.is_retrograde,
                        "return_retrograde": sr_ruler.is_retrograde,
                    }

        return {
            "method": "Ibn Ezra annual revolution core",
            "return_jd_ut": sr_chart.jd,
            "return_ascendant": {
                "longitude": sr_chart.ascendant,
                "sign": sr_asc_sign.value,
            },
            "return_ascendant_ruler": return_ruler_payload,
            "sect_light_triplicity_comparison": triplicity_comparison,
            "determinations": determinations,
            "location_basis": "Natal coordinates used as the return-location proxy because no residence-at-return coordinates were supplied.",
            "source_rule_id": "ibn_ezra_annual_revolution_core",
        }
