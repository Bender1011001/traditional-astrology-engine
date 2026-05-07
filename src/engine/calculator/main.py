import logging
from datetime import datetime

import pytz  # type: ignore
import swisseph as swe

logger = logging.getLogger(__name__)

from ..advanced_mechanics import (AlmutenEngine, DodecatemoriaEngine,
                                  DoryphoryEngine, HermeticLotEngine,
                                  MonomoiriaEngine)
from ..aspects import AspectEngine
# Classical Imports (Pointing to existing engine modules)
from ..classical_mechanics import ClassicalMechanicsEngine
from ..house_systems import AlcabitiusEngine
from ..kakosis import KakosisEngine
from ..models import (Chart, Planet, PlanetName, Sign)
from ..phasis import PhasisEngine
from ..reception import ReceptionEngine, ReceptionMode
from ..reference_data import DOMICILES
from .astronomy import compare_house_systems_calc
from .config import (COMPARE_SYSTEMS, normalize_ayanamsa, normalize_house_system,
                     normalize_zodiac_system)
from .geo import (get_coordinates, get_coordinates_with_meta,
                  get_timezone)
from .time_utils import _localize_with_historical_tz, get_julian_day


class ChartCalculator:
    """
    Core calculator class that encapsulates Swiss Ephemeris logic
    and returns a localized Chart object.
    """

    def calculate_chart(
        self,
        dt: datetime,
        city: str,
        state: str = "",
        latitude: float | None = None,
        longitude: float | None = None,
        house_system: str | None = None,
        zodiac_system: str | None = None,
        ayanamsa: str | None = None,
        node_type: str = "mean",  # "mean" or "true"
    ) -> Chart:
        # 1. Geocoding (or explicit override)
        if latitude is not None and longitude is not None:
            lat, lon = float(latitude), float(longitude)
        else:
            lat, lon = get_coordinates(city, state)

        # 2. Timezone
        tz_str = get_timezone(lat, lon)
        local_tz = pytz.timezone(tz_str)

        # 3. Time Localization
        # Note: input dt might be naive or aware. We assume it represents "Wall Clock" time at location
        # unless it's already UTC? Legacy implementation assumed wall clock.
        local_dt, utc_dt, tz_meta = _localize_with_historical_tz(local_tz, dt)

        # 4. Julian Day
        jd = get_julian_day(utc_dt)

        # 5. Configuration
        house_code, _ = normalize_house_system(house_system)
        zodiac_code, _ = normalize_zodiac_system(zodiac_system)

        ayanamsa_deg = None
        if zodiac_code == "sidereal":
            ayanamsa_mode, _, _ = normalize_ayanamsa(ayanamsa)
            swe.set_sid_mode(ayanamsa_mode)
            try:
                ayanamsa_deg = swe.get_ayanamsa_ut(jd)
            except Exception as e:
                logger.warning("Ayanamsa calc failed: %s", repr(e), exc_info=True)
                ayanamsa_deg = None

        # 6. Planet Calculations
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        if zodiac_code == "sidereal":
            flags |= swe.FLG_SIDEREAL

        # Topocentric calculations setup
        topo_flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_TOPOCTR
        swe.set_topo(lon, lat, 0)  # lat, lon, height

        # Pre-calc Sun for phasis
        sun_raw = swe.calc_ut(jd, swe.SUN, flags)
        sun_coords = sun_raw[0] if isinstance(sun_raw[0], (list, tuple)) else sun_raw
        sun_lon = sun_coords[0]

        planets_data = {
            "Sun": swe.SUN,
            "Moon": swe.MOON,
            "Mercury": swe.MERCURY,
            "Venus": swe.VENUS,
            "Mars": swe.MARS,
            "Jupiter": swe.JUPITER,
            "Saturn": swe.SATURN,
            "Uranus": swe.URANUS,
            "Neptune": swe.NEPTUNE,
            "Pluto": swe.PLUTO,
            "North_Node": swe.TRUE_NODE if node_type == "true" else swe.MEAN_NODE,
        }

        chart_planets = []
        sun_altitude = 0.0

        for name, pid in planets_data.items():
            # Core SWISSEPH calc
            res_full = swe.calc_ut(jd, pid, flags)
            coords = res_full[0] if isinstance(res_full[0], (list, tuple)) else res_full

            # Topocentric for Altitude
            topo_full = swe.calc_ut(jd, pid, topo_flags)
            topo_coords = (
                topo_full[0] if isinstance(topo_full[0], (list, tuple)) else topo_full
            )
            xin = (topo_coords[0], topo_coords[1], topo_coords[2])
            geopos_tuple = (lon, lat, 0)
            azresult = swe.azalt(jd, swe.ECL2HOR, geopos_tuple, 0, 0, xin)
            altitude = azresult[1]
            long_val = coords[0]
            lat_val = coords[1]
            speed_val = coords[3]

            # Enum Mapping
            try:
                enum_name = PlanetName[name.upper()]
            except KeyError:
                if name == "North_Node":
                    enum_name = PlanetName.NORTH_NODE
                else:
                    continue

            # Phasis & Visibility (Mini-calc for Chart Object)
            # Full phasis engine is heavy, but we need basic flags for the Chart object?
            # Existing main.py did full phasis calc.
            # We'll do basic phasis needed for Chart object properties

            is_ori = False
            is_vis = True
            phase_enum = None
            prox_enum = None

            if enum_name in [
                PlanetName.MERCURY,
                PlanetName.VENUS,
                PlanetName.MARS,
                PlanetName.JUPITER,
                PlanetName.SATURN,
            ]:
                is_ori = PhasisEngine.is_oriental(long_val, sun_lon)
                prox_enum = PhasisEngine.get_solar_proximity(long_val, sun_lon)
                is_vis = PhasisEngine.calculate_visibility(
                    jd, lat, lon, enum_name, long_val, lat_val, sun_lon
                )

            p_obj = Planet(
                name=enum_name,
                longitude=long_val,
                latitude=lat_val,
                speed=speed_val,
                altitude=altitude,
                is_oriental=is_ori,
                is_visible=is_vis,
                solar_proximity=prox_enum,
            )

            if enum_name in [
                PlanetName.MERCURY,
                PlanetName.VENUS,
                PlanetName.MARS,
                PlanetName.JUPITER,
                PlanetName.SATURN,
            ]:
                p_obj.phase = PhasisEngine.get_synodic_phase(p_obj, sun_lon)

            chart_planets.append(p_obj)

            if name == "Sun":
                sun_altitude = altitude

        # South Node
        if "North_Node" in planets_data:
            # Find NN object
            nn_obj = next(
                (p for p in chart_planets if p.name == PlanetName.NORTH_NODE), None
            )
            if nn_obj:
                sn_lon = (nn_obj.longitude + 180) % 360
                sn_obj = Planet(
                    name=PlanetName.SOUTH_NODE,
                    longitude=sn_lon,
                    latitude=-nn_obj.latitude,
                    speed=nn_obj.speed,
                    altitude=0,  # Approx
                )
                chart_planets.append(sn_obj)

        # 7. Houses
        if house_code == "B":
            # Alcabitius logic
            cusps_dict = AlcabitiusEngine.calculate_houses(jd, lat, lon)
            _, ascmc = swe.houses(jd, lat, lon, b"W")
            cusps = [cusps_dict[i] for i in range(1, 13)]
        else:
            cusps, ascmc = swe.houses(jd, lat, lon, house_code.encode())

        if zodiac_code == "sidereal" and ayanamsa_deg is not None:
            cusps = [((c - ayanamsa_deg) % 360) for c in cusps]
            ascmc = [((a - ayanamsa_deg) % 360) for a in ascmc]

        # Construct Chart Object
        chart = Chart(
            sun_altitude=sun_altitude,
            planets=chart_planets,
            ascendant=ascmc[0],
            mc=ascmc[1],
            geo_lat=lat,
            geo_lon=lon,
            jd=jd,
            houses={i + 1: c for i, c in enumerate(cusps)},
        )

        return chart


def calculate_chart_data(
    date_str: str,
    time_str: str,
    city: str,
    state: str = "",
    latitude: float | None = None,
    longitude: float | None = None,
    house_system: str | None = None,
    compare_house_systems: bool = False,
    zodiac_system: str | None = None,
    ayanamsa: str | None = None,
    time_range_start: str | None = None,
    time_range_end: str | None = None,
    time_range_samples: int | None = None,
    include_sensitivity: bool = True,
    node_type: str = "mean",
):
    """
    Calculate chart data for the given input.
    date_str: "YYYY-MM-DD"
    time_str: "HH:MM"
    """
    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError as e:
        return {"error": f"Date parsing error: {str(e)}"}

    calc = ChartCalculator()

    # Ensure we have explicit coordinates before calculating, so we only geocode once and can report the source.
    geocode_meta = None
    if latitude is None or longitude is None:
        try:
            lat_val, lon_val, geocode_meta = get_coordinates_with_meta(city, state)
            latitude, longitude = lat_val, lon_val
        except Exception as e:
            logger.error("Geocoding error", exc_info=True)
            return {"error": str(e)}
    else:
        geocode_meta = {
            "source": "override",
            "note": "Latitude/longitude provided directly to calculator.",
        }

    try:
        chart = calc.calculate_chart(
            dt,
            city,
            state,
            latitude=latitude,
            longitude=longitude,
            house_system=house_system,
            zodiac_system=zodiac_system,
            ayanamsa=ayanamsa,
            node_type=node_type,
        )
    except Exception as e:
        logger.error("Chart calculation error", exc_info=True)
        return {"error": str(e)}

    # Reconstruct Metadata for serialization
    # Ideally we'd get this from the calculator too, but we can re-derive simple stuff or assume standard
    # To get exact timezone info that Calculator used, we might need to expose it.
    # For now, we'll re-do geocode/tz purely for the "meta" dict or refactor Calculator to return a tuple.
    # Refactoring Calculator to return tuple (Chart, Meta) is cleaner but ChartCalculator.calculate_chart traditionally returns just Chart.
    # We will just re-fetch tz info for the meta report to be safe.

    tz_str = "unknown"
    tz_meta = {}  # type: ignore
    utc_dt = dt
    house_code, house_label = normalize_house_system(house_system)
    zodiac_code, zodiac_label = normalize_zodiac_system(zodiac_system)

    # Re-derive timezone metadata from the chart coordinates (works even if geocoding was bypassed).
    try:
        tz_str = get_timezone(chart.geo_lat, chart.geo_lon)  # type: ignore
        local_tz = pytz.timezone(tz_str)
        _, utc_dt, tz_meta = _localize_with_historical_tz(local_tz, dt)
    except Exception as e:
        logger.debug("Timezone re-derivation failed", exc_info=True)
        # Keep best-effort defaults; chart.jd is still authoritative for calculations.
        tz_str = tz_str or "unknown"
        tz_meta = tz_meta or {}

    results = {
        "meta": {
            "date": date_str,
            "time": time_str,
            "city": city,
            "state": state,
            "lat": chart.geo_lat,
            "lon": chart.geo_lon,
            "geocode": geocode_meta,
            "timezone": tz_str,
            "tz_abbrev": tz_meta.get("tz_abbrev"),
            "utc_offset_hours": tz_meta.get("utc_offset_hours"),
            "dst_offset_hours": tz_meta.get("dst_offset_hours"),
            "utc_time": utc_dt.isoformat(),
            "julian_day": chart.jd,
            "house_system": {
                "code": house_code,
                "label": house_label,
                "requested": house_system,
            },
            "zodiac_system": {"code": zodiac_code, "label": zodiac_label},
            "node_type": node_type,
        },
        "planets": {},
        "houses": chart.houses,
        "angles": {"Ascendant": chart.ascendant, "MC": chart.mc},
    }

    # Serialize Planets from Chart Object
    for p in chart.planets:
        p_name_str = p.name.value
        # Special casing for formatting to match original output if needed
        # Original keys were title case e.g. "Sun", "North_Node"
        key_name = p_name_str.title()
        if p.name == PlanetName.NORTH_NODE:
            key_name = "North_Node"
        if p.name == PlanetName.SOUTH_NODE:
            key_name = "South_Node"

        results["planets"][key_name] = {  # type: ignore
            "longitude": p.longitude,
            "latitude": p.latitude,
            "speed": p.speed,
            "altitude": p.altitude,
            "is_retrograde": p.is_retrograde,
            "classical": {},
        }

    # --- Advanced Mechanics Integration (Lots, Almuten, etc) ---
    # ... (Reuse logic logic) ...

    # 1. Classical Calculations per Planet (Antiscia, Dodecatemoria)
    for p in chart.planets:
        key_name = p.name.value.title()
        if p.name == PlanetName.NORTH_NODE:
            key_name = "North_Node"
        if p.name == PlanetName.SOUTH_NODE:
            key_name = "South_Node"

        if key_name not in results["planets"]:  # type: ignore
            continue

        antiscia = ClassicalMechanicsEngine.get_antiscia(p.longitude)
        dodecatemorion = ClassicalMechanicsEngine.get_dodecatemorion(p.longitude)

        if "classical" not in results["planets"][key_name]:  # type: ignore
            results["planets"][key_name]["classical"] = {}  # type: ignore

        results["planets"][key_name]["classical"]["antiscia"] = {  # type: ignore
            "longitude": antiscia.antiscia_lon,
            "sign": antiscia.antiscia_sign.value,
        }
        results["planets"][key_name]["classical"]["contra_antiscia"] = {  # type: ignore
            "longitude": antiscia.contra_antiscia_lon,
            "sign": antiscia.contra_antiscia_sign.value,
        }
        results["planets"][key_name]["classical"]["dodecatemorion"] = {  # type: ignore
            "longitude": dodecatemorion.longitude,
            "sign": dodecatemorion.sign.value,
            "term_ruler": dodecatemorion.term_ruler,
        }

        # Phasis serialization
        # Our Chart object already has these, but we need to serialize them
        if p.name not in [
            PlanetName.URANUS,
            PlanetName.NEPTUNE,
            PlanetName.PLUTO,
            PlanetName.NORTH_NODE,
            PlanetName.SOUTH_NODE,
        ]:
            results["planets"][key_name]["classical"]["phasis"] = {  # type: ignore
                "phase": p.phase.value if p.phase else None,
                "solar_proximity": (
                    p.solar_proximity.value if p.solar_proximity else None
                ),
                "is_oriental": p.is_oriental,
                "is_visible": p.is_visible,
            }

    # 2. Hermetic Lots
    lots_data = HermeticLotEngine.calculate_all_lots(chart)
    if "classical" not in results:
        results["classical"] = {}
    results["classical"]["hermetic_lots"] = lots_data  # type: ignore

    # 3. Planetary Hours & Almuten
    try:
        asc_sign = list(Sign)[int(chart.ascendant / 30)]
        asc_lord_enum = DOMICILES.get(asc_sign)
        asc_lord_str = asc_lord_enum.value if asc_lord_enum else None

        p_hours = ClassicalMechanicsEngine.get_planetary_hours(
            utc_dt, chart.geo_lat, chart.geo_lon, asc_sign, asc_lord_str  # type: ignore
        )

        day_lord_enum = None
        hour_lord_enum = None

        if p_hours:
            results["classical"]["planetary_hours"] = {  # type: ignore
                "day_of_week": p_hours.day_of_week,
                "day_lord": p_hours.day_lord,
                "hour_lord": p_hours.hour_lord,
                "hour_number": p_hours.hour_number,
                "is_daytime": p_hours.is_daytime,
            }
            if p_hours.day_lord:
                day_lord_enum = PlanetName(p_hours.day_lord)
            if p_hours.hour_lord:
                hour_lord_enum = PlanetName(p_hours.hour_lord)

        almuten_data = AlmutenEngine.calculate_almuten(
            chart, day_lord_enum, hour_lord_enum
        )
        results["classical"]["almuten_figuris"] = {  # type: ignore
            "winner": almuten_data.winner.value,
            "scores": {
                k: {
                    "total": v.total_score,
                    "essential": v.essential_score,
                    "house": v.house_score,
                    "day_hour": v.day_hour_score,
                }
                for k, v in almuten_data.scores.items()
            },
            "hylegs": almuten_data.hylegs,
        }
    except Exception as e:
        results["classical_error"] = str(e)  # type: ignore

    # 4. Doryphory
    doryphory_list = DoryphoryEngine.check_doryphory(chart)
    for d in doryphory_list:
        p_key = d.planet.value.title()
        if p_key in results["planets"]:  # type: ignore
            if "doryphory" not in results["planets"][p_key]["classical"]:  # type: ignore
                results["planets"][p_key]["classical"]["doryphory"] = []  # type: ignore
            results["planets"][p_key]["classical"]["doryphory"].append(  # type: ignore
                {"type": d.type, "luminary": d.related_luminary, "score": d.score}
            )

    # 5. Monomoiria
    # ... (Need is_day, sun_sign, moon_sign etc)
    is_day = chart.sun_altitude >= 0
    sun_p = next((p for p in chart.planets if p.name == PlanetName.SUN), None)
    moon_p = next((p for p in chart.planets if p.name == PlanetName.MOON), None)

    if sun_p and moon_p:
        sun_sign = list(Sign)[int(sun_p.longitude / 30)]
        moon_sign = list(Sign)[int(moon_p.longitude / 30)]
        for p in chart.planets:
            if p.name == PlanetName.SOUTH_NODE:
                continue
            key_name = p.name.value.title()
            if p.name == PlanetName.NORTH_NODE:
                key_name = "North_Node"

            z_ruler = MonomoiriaEngine.get_zoidion_monomoiria(p.longitude)
            t_ruler = MonomoiriaEngine.get_trigonal_monomoiria(
                p.longitude, is_day, sun_sign, moon_sign
            )

            if key_name in results["planets"]:  # type: ignore
                results["planets"][key_name]["classical"]["monomoiria"] = {  # type: ignore
                    "zoidion_ruler": z_ruler.value,
                    "trigonal_ruler": t_ruler.value,
                }

    # 6. Dodecatemoria Detailed
    dodeca_valens = DodecatemoriaEngine.get_dodecatemoria_data(chart, is_valens=True)
    dodeca_paul = DodecatemoriaEngine.get_dodecatemoria_data(chart, is_valens=False)
    for p in chart.planets:
        key_name = p.name.value.title()
        if p.name == PlanetName.NORTH_NODE:
            key_name = "North_Node"
        if p.name in dodeca_valens:
            if key_name in results["planets"]:  # type: ignore
                results["planets"][key_name]["classical"]["dodecatemoria"] = {  # type: ignore
                    "valens": dodeca_valens[p.name],  # type: ignore
                    "paul": dodeca_paul[p.name],  # type: ignore
                }

    # 7. Kakosis
    for p in chart.planets:
        maltreatments = KakosisEngine.check_maltreatments(p, chart)
        if maltreatments:
            key_name = p.name.value.title()
            if p.name == PlanetName.NORTH_NODE:
                key_name = "North_Node"
            if key_name in results["planets"]:  # type: ignore
                results["planets"][key_name]["classical"]["kakosis"] = [  # type: ignore
                    {
                        "condition": c.type,
                        "malefic": c.malefic.value if c.malefic else "None",
                        "details": c.description,
                    }
                    for c in maltreatments
                ]

    # 8. Receptions
    strict = ReceptionEngine.calculate_mutual_receptions(
        chart, ReceptionMode.STRICT_BONATTI
    )
    std = ReceptionEngine.calculate_mutual_receptions(
        chart, ReceptionMode.STANDARD_LILLY
    )
    results["classical"]["receptions"] = {  # type: ignore
        "strict_bonatti": [
            {
                "planets": [m.planet_a.value, m.planet_b.value],
                "type": m.type,
                "score": m.strength_score,
            }
            for m in strict
        ],
        "standard_lilly": [
            {
                "planets": [m.planet_a.value, m.planet_b.value],
                "type": m.type,
                "score": m.strength_score,
            }
            for m in std
        ],
    }

    # 9. Aspects
    all_aspects = AspectEngine.calculate_aspects(chart)
    results["aspects"] = [  # type: ignore
        {
            "p1": a.planet_a.value,
            "p2": a.planet_b.value,
            "type": a.type.value,
            "orb": round(a.orb, 2),
            "is_applying": a.is_applying,
            "text": a.text,
        }
        for a in all_aspects
    ]

    # Compare systems if requested
    if compare_house_systems:
        # Re-calc house comparison
        systems = []
        for c in COMPARE_SYSTEMS:
            if c not in systems:
                systems.append(c)
        if house_code not in systems:
            systems.insert(0, house_code)

        ayanamsa_deg = None
        if zodiac_code == "sidereal":
            ayanamsa_mode, _, _ = normalize_ayanamsa(ayanamsa)
            swe.set_sid_mode(ayanamsa_mode)
            try:
                ayanamsa_deg = swe.get_ayanamsa_ut(chart.jd)
            except Exception:
                pass

        hb, errs = compare_house_systems_calc(
            chart.jd, chart.geo_lat, chart.geo_lon, systems, ayanamsa_deg  # type: ignore
        )
        results["houses_by_system"] = hb

    try:
        return results
    finally:
        swe.close()
