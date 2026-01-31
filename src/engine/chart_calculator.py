import swisseph as swe
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError, GeocoderTimedOut, GeocoderUnavailable
from timezonefinder import TimezoneFinder
import pytz
from datetime import datetime, timedelta
import os
import time

# Classical Imports
from src.engine.classical_mechanics import ClassicalMechanicsEngine
from src.engine.models import Sign, PlanetName, Chart, Planet
from src.engine.reference_data import DOMICILES
from src.engine.advanced_mechanics import (
    HermeticLotEngine, MonomoiriaEngine, AlmutenEngine, DoryphoryEngine
)

# Initialize Geocoder
_ua_base = os.getenv("NOMINATIM_USER_AGENT", "astrology_app/1.0")
_ua_contact = os.getenv("NOMINATIM_CONTACT", "").strip()
_user_agent = f"{_ua_base} ({_ua_contact})" if _ua_contact else _ua_base
_timeout = int(os.getenv("NOMINATIM_TIMEOUT", "10"))
_max_attempts = max(1, int(os.getenv("NOMINATIM_MAX_ATTEMPTS", "3")))
_backoff_seconds = float(os.getenv("NOMINATIM_BACKOFF_SECONDS", "1.0"))

geolocator = Nominatim(user_agent=_user_agent, timeout=_timeout)
tf = TimezoneFinder()

def get_coordinates(city: str, state: str = "") -> tuple[float, float]:
    """
    Get latitude and longitude for a given city and state.
    """
    query = f"{city}, {state}" if state else city
    last_error = None
    for attempt in range(1, _max_attempts + 1):
        try:
            location = geolocator.geocode(query, exactly_one=True)
            if location:
                return location.latitude, location.longitude
            raise ValueError(f"Could not find location: {query}")
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            last_error = e
            if attempt < _max_attempts:
                time.sleep(_backoff_seconds * attempt)
                continue
            raise ValueError(
                f"Geocoding timed out after {_timeout}s. "
                f"Try again or increase NOMINATIM_TIMEOUT."
            ) from e
        except GeocoderServiceError as e:
            raise ValueError(f"Geocoding service error: {e}") from e
    raise ValueError(f"Geocoding failed: {last_error}")

def get_julian_day(dt_utc: datetime) -> float:
    """
    Calculate Julian Day from UTC datetime.
    """
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, 
                      dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0)

def get_timezone(lat: float, lon: float) -> str:
    """
    Resolve timezone for a given coordinate pair.
    """
    tz_str = tf.timezone_at(lng=lon, lat=lat)
    if not tz_str:
        raise ValueError("Could not determine timezone")
    return tz_str

def get_local_datetime_now(city: str, state: str = "") -> datetime:
    """
    Returns a timezone-aware datetime for the current moment at a given location.
    """
    lat, lon = get_coordinates(city, state)
    tz_str = get_timezone(lat, lon)
    local_tz = pytz.timezone(tz_str)
    return datetime.now(local_tz)

ZODIAC_SYSTEM_LABELS = {
    "tropical": "Tropical",
    "sidereal": "Sidereal"
}

AYANAMSA_OPTIONS = {
    "fagan_bradley": (swe.SIDM_FAGAN_BRADLEY, "Fagan-Bradley"),
    "lahiri": (swe.SIDM_LAHIRI, "Lahiri"),
    "krishnamurti": (swe.SIDM_KRISHNAMURTI, "Krishnamurti"),
    "raman": (swe.SIDM_RAMAN, "Raman"),
    "hipparchos": (swe.SIDM_HIPPARCHOS, "Hipparchos"),
    "true_citra": (swe.SIDM_TRUE_CITRA, "True Citra"),
    "true_revati": (swe.SIDM_TRUE_REVATI, "True Revati"),
    "suryasiddhanta": (swe.SIDM_SURYASIDDHANTA, "Surya Siddhanta")
}

AYANAMSA_ALIASES = {
    "faganbradley": "fagan_bradley",
    "fagan": "fagan_bradley",
    "lahiri": "lahiri",
    "krishnamurti": "krishnamurti",
    "kp": "krishnamurti",
    "raman": "raman",
    "hipparchos": "hipparchos",
    "hipparchus": "hipparchos",
    "truecitra": "true_citra",
    "truerevati": "true_revati",
    "suryasiddhanta": "suryasiddhanta"
}

def _normalize_zodiac_system(value: str | None) -> tuple[str, str]:
    if not value:
        return "tropical", ZODIAC_SYSTEM_LABELS["tropical"]
    raw = value.strip().lower()
    if raw in ("sidereal", "s", "sid"):
        return "sidereal", ZODIAC_SYSTEM_LABELS["sidereal"]
    return "tropical", ZODIAC_SYSTEM_LABELS["tropical"]

def _normalize_ayanamsa(value: str | None) -> tuple[int, str, str]:
    if not value:
        mode, label = AYANAMSA_OPTIONS["lahiri"]
        return mode, label, "lahiri"
    key = value.strip().lower().replace(" ", "").replace("-", "").replace("_", "")
    norm = AYANAMSA_ALIASES.get(key, "lahiri")
    mode, label = AYANAMSA_OPTIONS.get(norm, AYANAMSA_OPTIONS["lahiri"])
    return mode, label, norm

def _angle_delta(a: float, b: float) -> float:
    d = abs(a - b) % 360.0
    return 360.0 - d if d > 180.0 else d

def _house_from_cusps(longitude: float, houses: dict[int, float]) -> int:
    cusps = [houses[i] for i in range(1, 13)]
    lon = longitude % 360.0
    for i in range(12):
        c1 = cusps[i] % 360.0
        c2 = cusps[(i + 1) % 12] % 360.0
        if c1 <= c2:
            if c1 <= lon < c2:
                return i + 1
        else:
            if lon >= c1 or lon < c2:
                return i + 1
    return 1

def _build_distribution(counts: list[int], labels: list[str]) -> list[dict]:
    total = sum(counts)
    if total <= 0:
        return []
    items = []
    for idx, label in enumerate(labels):
        count = counts[idx]
        if count <= 0:
            continue
        items.append({
            "label": label,
            "count": count,
            "percent": round((count / total) * 100.0, 1)
        })
    return items

def _compute_snapshot(
    utc_dt: datetime,
    jd: float,
    lat: float,
    lon: float,
    house_code: str,
    zodiac_code: str,
    ayanamsa_mode: int | None
) -> dict:
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    if zodiac_code == "sidereal":
        flags |= swe.FLG_SIDEREAL
        if ayanamsa_mode is not None:
            swe.set_sid_mode(ayanamsa_mode)
    sun = swe.calc_ut(jd, swe.SUN, flags)[0][0]
    moon = swe.calc_ut(jd, swe.MOON, flags)[0][0]
    cusps, ascmc = swe.houses(jd, lat, lon, house_code.encode())
    ayanamsa_deg = None
    if zodiac_code == "sidereal":
        try:
            ayanamsa_deg = swe.get_ayanamsa_ut(jd)
        except Exception:
            ayanamsa_deg = None
        if ayanamsa_deg is not None:
            cusps = [((c - ayanamsa_deg) % 360) for c in cusps]
            ascmc = [((a - ayanamsa_deg) % 360) for a in ascmc]
    return {
        "utc_time": utc_dt.isoformat(),
        "jd": jd,
        "ayanamsa_deg": ayanamsa_deg,
        "asc": ascmc[0],
        "mc": ascmc[1],
        "sun": sun,
        "moon": moon,
        "houses": {i + 1: c for i, c in enumerate(cusps)}
    }

def _localize_with_historical_tz(local_tz: pytz.tzinfo.BaseTzInfo, naive_dt: datetime) -> tuple[datetime, datetime, dict]:
    meta = {
        "tz_abbrev": None,
        "utc_offset_hours": None,
        "dst_offset_hours": None,
        "tz_warning": None,
        "tz_resolution": None
    }
    try:
        localized = local_tz.localize(naive_dt, is_dst=None)
        meta["tz_resolution"] = "exact"
    except pytz.AmbiguousTimeError:
        localized = local_tz.localize(naive_dt, is_dst=False)
        meta["tz_resolution"] = "ambiguous_standard_time"
        meta["tz_warning"] = "Ambiguous local time due to DST; defaulted to standard time."
    except pytz.NonExistentTimeError:
        localized = local_tz.localize(naive_dt, is_dst=True)
        meta["tz_resolution"] = "nonexistent_shifted_to_dst"
        meta["tz_warning"] = "Non-existent local time during DST transition; defaulted to post-transition (DST)."

    utc_dt = localized.astimezone(pytz.utc)
    offset = localized.utcoffset() or timedelta(0)
    dst = localized.dst() or timedelta(0)
    meta["tz_abbrev"] = localized.tzname()
    meta["utc_offset_hours"] = round(offset.total_seconds() / 3600.0, 4)
    meta["dst_offset_hours"] = round(dst.total_seconds() / 3600.0, 4)
    if meta["tz_abbrev"] == "LMT":
        meta["tz_warning"] = (meta["tz_warning"] + " " if meta["tz_warning"] else "") + "Local Mean Time (LMT) in effect; standard time may not have been adopted."
    return localized, utc_dt, meta

HOUSE_SYSTEM_LABELS = {
    "P": "Placidus",
    "W": "Whole Sign",
    "R": "Regiomontanus",
    "B": "Alcabitius",
    "C": "Campanus",
    "O": "Porphyry",
    "E": "Equal",
    "K": "Koch",
    "T": "Topocentric"
}

HOUSE_SYSTEM_ALIASES = {
    "placidus": "P",
    "pl": "P",
    "wholesign": "W",
    "whole": "W",
    "ws": "W",
    "regiomontanus": "R",
    "regio": "R",
    "alcabitius": "B",
    "alcabitius": "B",
    "campanus": "C",
    "porphyry": "O",
    "equal": "E",
    "koch": "K",
    "topocentric": "T",
    "topo": "T"
}

COMPARE_SYSTEMS = ["W", "P", "R", "B", "O", "C"]

def _normalize_house_system(value: str | None) -> tuple[str, str]:
    if not value:
        return "P", HOUSE_SYSTEM_LABELS["P"]
    raw = value.strip()
    if not raw:
        return "P", HOUSE_SYSTEM_LABELS["P"]
    if len(raw) == 1 and raw.upper() in HOUSE_SYSTEM_LABELS:
        code = raw.upper()
        return code, HOUSE_SYSTEM_LABELS[code]
    key = raw.lower().replace(" ", "").replace("-", "").replace("_", "")
    code = HOUSE_SYSTEM_ALIASES.get(key, "P")
    return code, HOUSE_SYSTEM_LABELS.get(code, "Placidus")

def calculate_chart_data(
    date_str: str,
    time_str: str,
    city: str,
    state: str = "",
    house_system: str | None = None,
    compare_house_systems: bool = False,
    zodiac_system: str | None = None,
    ayanamsa: str | None = None,
    time_range_start: str | None = None,
    time_range_end: str | None = None,
    time_range_samples: int | None = None,
    include_sensitivity: bool = True
):
    """
    Calculate chart data for the given input.
    date_str: "YYYY-MM-DD"
    time_str: "HH:MM"
    """
    # 1. Geocoding
    try:
        lat, lon = get_coordinates(city, state)
    except Exception as e:
        return {"error": str(e)}

    # 2. Timezone
    tz_str = tf.timezone_at(lng=lon, lat=lat)
    if not tz_str:
        return {"error": "Could not determine timezone"}
    
    local_tz = pytz.timezone(tz_str)
    
    # 3. Parse Date/Time
    try:
        local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        local_dt, utc_dt, tz_meta = _localize_with_historical_tz(local_tz, local_dt)
    except Exception as e:
        return {"error": f"Date parsing error: {str(e)}"}

    # 4. Julian Day
    jd = get_julian_day(utc_dt)

    # 5. Calculate Planets
    # swe.set_ephe_path('/path/to/ephe') # Optional: Set if needed
    
    planets = {
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
        "North_Node": swe.MEAN_NODE # Or TRUE_NODE
    }
    
    house_code, house_label = _normalize_house_system(house_system)
    zodiac_code, zodiac_label = _normalize_zodiac_system(zodiac_system)
    ayanamsa_mode = None
    ayanamsa_label = None
    ayanamsa_key = None
    ayanamsa_deg = None
    if zodiac_code == "sidereal":
        ayanamsa_mode, ayanamsa_label, ayanamsa_key = _normalize_ayanamsa(ayanamsa)
        swe.set_sid_mode(ayanamsa_mode)
        try:
            ayanamsa_deg = swe.get_ayanamsa_ut(jd)
        except Exception:
            ayanamsa_deg = None
    results = {
        "meta": {
            "date": date_str,
            "time": time_str,
            "city": city,
            "state": state,
            "lat": lat,
            "lon": lon,
            "timezone": tz_str,
            "tz_abbrev": tz_meta.get("tz_abbrev"),
            "utc_offset_hours": tz_meta.get("utc_offset_hours"),
            "dst_offset_hours": tz_meta.get("dst_offset_hours"),
            "tz_warning": tz_meta.get("tz_warning"),
            "tz_resolution": tz_meta.get("tz_resolution"),
            "utc_time": utc_dt.isoformat(),
            "julian_day": jd,
            "house_system": {
                "code": house_code,
                "label": house_label,
                "requested": house_system or house_label
            },
            "zodiac_system": {
                "code": zodiac_code,
                "label": zodiac_label,
                "ayanamsa": {
                    "code": ayanamsa_key,
                    "label": ayanamsa_label,
                    "degrees": ayanamsa_deg
                } if zodiac_code == "sidereal" else None
            },
            "compare_house_systems": bool(compare_house_systems)
        },
        "planets": {},
        "houses": {}
    }

    # Flags: SEFLG_SWIEPH (use Ephemeris), SEFLG_SPEED (calc speed)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    if zodiac_code == "sidereal":
        flags |= swe.FLG_SIDEREAL
    topo_flags = (swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_TOPOCTR)
    swe.set_topo(lon, lat, 0)

    for name, pid in planets.items():
        try:
            # res is usually ((lon, lat, dist, spd_lon, spd_lat, spd_dist), rflag) or (lon, lat, ... rflag)
            # Inspecting structure:
            res_full = swe.calc_ut(jd, pid, flags)
            
            # Helper to extract coordinates
            if isinstance(res_full[0], (list, tuple)):
                coords = res_full[0]
            else:
                coords = res_full

            # Calculate Altitude/Azimuth using topocentric position for accuracy.
            topo_full = swe.calc_ut(jd, pid, topo_flags)
            topo_coords = topo_full[0] if isinstance(topo_full[0], (list, tuple)) else topo_full
            xin = (topo_coords[0], topo_coords[1], topo_coords[2])
            geopos = (lon, lat, 0) # lon, lat, height
            azresult = swe.azalt(jd, swe.ECL2HOR, geopos, 0, 0, xin)
            # azresult returns (azimuth, true_altitude, apparent_altitude)
            
            altitude = azresult[1]
            long_val = coords[0]

            # --- Classical Calculations per Planet ---
            antiscia = ClassicalMechanicsEngine.get_antiscia(long_val)
            dodecatemorion = ClassicalMechanicsEngine.get_dodecatemorion(long_val)

            results["planets"][name] = {
                "longitude": coords[0],
                "latitude": coords[1],
                "distance": coords[2],
                "speed": coords[3],
                "altitude": altitude,
                "is_retrograde": coords[3] < 0,
                "classical": {
                    "antiscia": {
                        "longitude": antiscia.antiscia_lon,
                        "sign": antiscia.antiscia_sign.value
                    },
                    "contra_antiscia": {
                         "longitude": antiscia.contra_antiscia_lon,
                         "sign": antiscia.contra_antiscia_sign.value
                    },
                    "dodecatemorion": {
                        "longitude": dodecatemorion.longitude,
                        "sign": dodecatemorion.sign.value,
                        "term_ruler": dodecatemorion.term_ruler
                    }
                }
            }
        except swe.Error as e:
             # Fallback to Moshier if file missing
             res_full = swe.calc_ut(jd, pid, 0)
             if isinstance(res_full[0], (list, tuple)):
                coords = res_full[0]
             else:
                coords = res_full
                
             results["planets"][name] = {
                "longitude": coords[0],
                "latitude": coords[1],
                "distance": coords[2],
                "speed": coords[3],
                "note": "Moshier fallback"
            }
            
    # Calculate South Node (180 degrees from North Node)
    if "North_Node" in results["planets"]:
        nn_lon = results["planets"]["North_Node"]["longitude"]
        
        sn_lon = (nn_lon + 180) % 360
        antiscia_sn = ClassicalMechanicsEngine.get_antiscia(sn_lon)
        
        results["planets"]["South_Node"] = {
            "longitude": sn_lon,
            "latitude": -results["planets"]["North_Node"]["latitude"],
            "speed": results["planets"]["North_Node"]["speed"],
            "is_retrograde": True, # Nodes are usually Rx
             "classical": {
                    "antiscia": {
                        "longitude": antiscia_sn.antiscia_lon,
                        "sign": antiscia_sn.antiscia_sign.value
                    },
                    "contra_antiscia": {
                         "longitude": antiscia_sn.contra_antiscia_lon,
                         "sign": antiscia_sn.contra_antiscia_sign.value
                    }
            }
        }


    # 6. Houses (Placidus is default 'P', Whole Sign is 'W')
    # swe.houses(jd, lat, lon, b'P') 
    # returns (cusps, ascmc)
    # ascmc: 0=Asc, 1=MC, 2=ARM, 3=Vertex, ...
    
    try:
        cusps, ascmc = swe.houses(jd, lat, lon, house_code.encode())
        if zodiac_code == "sidereal" and ayanamsa_deg is not None:
            cusps = [((c - ayanamsa_deg) % 360) for c in cusps]
            ascmc = [((a - ayanamsa_deg) % 360) for a in ascmc]
        results["houses"] = {i+1: c for i, c in enumerate(cusps)}
        results["angles"] = {
            "Ascendant": ascmc[0],
            "MC": ascmc[1]
        }
        
        # --- Planetary Hours / Radicality Calculation ---
        try:
            asc_deg = ascmc[0]
            asc_idx = int(asc_deg / 30) % 12
            asc_sign = list(Sign)[asc_idx]
            
            # DOMICILES is a dict {Sign: PlanetName}
            # Ascendant Lord
            asc_lord_enum = DOMICILES.get(asc_sign)
            asc_lord_str = asc_lord_enum.value if asc_lord_enum else None
            
            # Calculate Hours
            # We need utc_dt (datetime)
            p_hours = ClassicalMechanicsEngine.get_planetary_hours(utc_dt, lat, lon, asc_sign, asc_lord_str)
            
            if p_hours:
                 results["classical"] = {
                     "planetary_hours": {
                         "day_of_week": p_hours.day_of_week,
                         "day_lord": p_hours.day_lord,
                         "hour_lord": p_hours.hour_lord,
                         "hour_number": p_hours.hour_number,
                         "is_daytime": p_hours.is_daytime,
                         "radicality": p_hours.radicality,
                         "night_lord": p_hours.night_lord
                     }
                 }
        except Exception as e_classical:
            results["classical_error"] = str(e_classical)

        # --- Advanced Mechanics Integration ---
        try:
            # 1. Reconstruct Chart Object
            chart_planets = []
            sun_alt = 0.0
            
            for pname, pdata in results["planets"].items():
                if pname == "South_Node": continue # Skip computed SN for now, model handles explicit planets usually? Or add it?
                # Using key matching
                try:
                    enum_name = PlanetName[pname.upper()]
                except KeyError:
                    # Try manual mapping or skip
                    if pname == "North_Node": enum_name = PlanetName.NORTH_NODE
                    else: continue
                
                p_obj = Planet(
                    name=enum_name,
                    longitude=pdata["longitude"],
                    latitude=pdata.get("latitude", 0),
                    speed=pdata.get("speed", 0),
                    altitude=pdata.get("altitude", 0)
                )
                chart_planets.append(p_obj)
                
                if pname == "Sun":
                    sun_alt = pdata.get("altitude", 0)

            # Create Chart
            chart_obj = Chart(
                sun_altitude=sun_alt,
                planets=chart_planets,
                ascendant=ascmc[0],
                mc=ascmc[1],
                geo_lat=lat,
                geo_lon=lon,
                jd=jd,
                houses={i+1: c for i, c in enumerate(cusps)}
            )
            
            # 2. Hermetic Lots
            lots_data = HermeticLotEngine.calculate_all_lots(chart_obj)
            if "classical" not in results: results["classical"] = {}
            results["classical"]["hermetic_lots"] = lots_data
            
            # 3. Almuten Figuris
            day_lord_enum = None
            hour_lord_enum = None
            if "classical" in results and "planetary_hours" in results["classical"]:
                 ph = results["classical"]["planetary_hours"]
                 dl = ph.get("day_lord")
                 hl = ph.get("hour_lord")
                 # Convert to Enum, handling possible string mismatches
                 try:
                     if dl: day_lord_enum = PlanetName(dl)
                     if hl: hour_lord_enum = PlanetName(hl)
                 except ValueError:
                     pass # Maybe "Sun" vs "Sun" mismatch? usually match.

            almuten_data = AlmutenEngine.calculate_almuten(chart_obj, day_lord_enum, hour_lord_enum)
            results["classical"]["almuten_figuris"] = {
                "winner": almuten_data.winner.value,
                "scores": {k: {
                    "total": v.total_score,
                    "essential": v.essential_score,
                    "house": v.house_score,
                    "day_hour": v.day_hour_score,
                    "breakdown": v.breakdown
                } for k, v in almuten_data.scores.items()},
                "hylegs": almuten_data.hylegs
            }
            
            # 4. Doryphory
            doryphory_list = DoryphoryEngine.check_doryphory(chart_obj)
            for d_instance in doryphory_list:
                p_key = d_instance.planet.value.title() # "Jupiter"
                # Map naming if needed e.g., North_Node -> North_Node
                if p_key == "North_node": p_key = "North_Node" # Title case quirk?
                if p_key not in results["planets"]:
                    # Try uppercase? No, results uses keys like "Jupiter"
                    pass
                
                target_keys = [p_key]
                if p_key == "North_Node": target_keys = ["North_Node"]
                
                for k in target_keys:
                    if k in results["planets"]:
                        if "classical" not in results["planets"][k]: results["planets"][k]["classical"] = {}
                        if "doryphory" not in results["planets"][k]["classical"]:
                            results["planets"][k]["classical"]["doryphory"] = []
                        
                        results["planets"][k]["classical"]["doryphory"].append({
                            "type": d_instance.type,
                            "luminary": d_instance.related_luminary,
                            "score": d_instance.score
                        })

            # 5. Monomoiria
            is_day = (sun_alt >= 0)
            sun_p = next((p for p in chart_planets if p.name == PlanetName.SUN), None)
            moon_p = next((p for p in chart_planets if p.name == PlanetName.MOON), None)
            
            if sun_p and moon_p:
                sun_sign_idx = int(sun_p.longitude / 30)
                moon_sign_idx = int(moon_p.longitude / 30)
                sun_sign = list(Sign)[sun_sign_idx]
                moon_sign = list(Sign)[moon_sign_idx]
                
                for pname, pdata in results["planets"].items():
                    lon_val = pdata["longitude"]
                    z_ruler = MonomoiriaEngine.get_zoidion_monomoiria(lon_val)
                    t_ruler = MonomoiriaEngine.get_trigonal_monomoiria(lon_val, is_day, sun_sign, moon_sign)
                    
                    if "classical" not in pdata: pdata["classical"] = {}
                    pdata["classical"]["monomoiria"] = {
                        "zoidion_ruler": z_ruler.value,
                        "trigonal_ruler": t_ruler.value
                    }
                    results["planets"][pname] = pdata

        except Exception as e_adv:
            results["advanced_error"] = str(e_adv)
            import traceback
            results["advanced_error_trace"] = traceback.format_exc()

    except Exception as e:
        results["error_houses"] = str(e)

    if compare_house_systems:
        systems = []
        for code in COMPARE_SYSTEMS:
            if code not in systems:
                systems.append(code)
        if house_code not in systems:
            systems.insert(0, house_code)

        houses_by_system = {}
        errors = {}
        for code in systems:
            try:
                cusps, _ = swe.houses(jd, lat, lon, code.encode())
                if zodiac_code == "sidereal" and ayanamsa_deg is not None:
                    cusps = [((c - ayanamsa_deg) % 360) for c in cusps]
                label = HOUSE_SYSTEM_LABELS.get(code, code)
                houses_by_system[label] = {i+1: c for i, c in enumerate(cusps)}
            except Exception as e:
                label = HOUSE_SYSTEM_LABELS.get(code, code)
                errors[label] = str(e)

        results["houses_by_system"] = houses_by_system
        if errors:
            results["houses_by_system_errors"] = errors

    if include_sensitivity and time_range_start and time_range_end:
        sensitivity = {}
        try:
            start_local = datetime.strptime(f"{date_str} {time_range_start}", "%Y-%m-%d %H:%M")
            end_local = datetime.strptime(f"{date_str} {time_range_end}", "%Y-%m-%d %H:%M")
        except Exception:
            sensitivity["error"] = "Invalid time range format. Use HH:MM."
            results["time_sensitivity"] = sensitivity
            return results

        range_warning = None
        if end_local <= start_local:
            end_local = end_local + timedelta(days=1)
            range_warning = "End time is before start; assumed next day."

        try:
            start_localized, start_utc, _ = _localize_with_historical_tz(local_tz, start_local)
            end_localized, end_utc, _ = _localize_with_historical_tz(local_tz, end_local)
        except Exception as e:
            sensitivity["error"] = f"Time range localization error: {e}"
            results["time_sensitivity"] = sensitivity
            return results

        start_jd = get_julian_day(start_utc)
        end_jd = get_julian_day(end_utc)

        start_snap = _compute_snapshot(start_utc, start_jd, lat, lon, house_code, zodiac_code, ayanamsa_mode)
        end_snap = _compute_snapshot(end_utc, end_jd, lat, lon, house_code, zodiac_code, ayanamsa_mode)

        house_deltas = {}
        for h in range(1, 13):
            if h in start_snap["houses"] and h in end_snap["houses"]:
                house_deltas[h] = round(_angle_delta(start_snap["houses"][h], end_snap["houses"][h]), 4)

        sensitivity = {
            "range": {
                "start": time_range_start,
                "end": time_range_end,
                "minutes": int((end_localized - start_localized).total_seconds() / 60),
                "warning": range_warning
            },
            "start": {
                "utc_time": start_snap["utc_time"],
                "asc": start_snap["asc"],
                "mc": start_snap["mc"],
                "sun": start_snap["sun"],
                "moon": start_snap["moon"],
                "ayanamsa_deg": start_snap["ayanamsa_deg"]
            },
            "end": {
                "utc_time": end_snap["utc_time"],
                "asc": end_snap["asc"],
                "mc": end_snap["mc"],
                "sun": end_snap["sun"],
                "moon": end_snap["moon"],
                "ayanamsa_deg": end_snap["ayanamsa_deg"]
            },
            "deltas": {
                "asc": round(_angle_delta(start_snap["asc"], end_snap["asc"]), 4),
                "mc": round(_angle_delta(start_snap["mc"], end_snap["mc"]), 4),
                "sun": round(_angle_delta(start_snap["sun"], end_snap["sun"]), 4),
                "moon": round(_angle_delta(start_snap["moon"], end_snap["moon"]), 4),
                "houses": house_deltas
            },
            "asc_sign_change": int(start_snap["asc"] / 30) % 12 != int(end_snap["asc"] / 30) % 12,
            "mc_sign_change": int(start_snap["mc"] / 30) % 12 != int(end_snap["mc"] / 30) % 12
        }

        results["time_sensitivity"] = sensitivity

        # Distribution sampling across range
        try:
            sample_count = int(time_range_samples) if time_range_samples else 12
        except Exception:
            sample_count = 12
        sample_count = max(3, min(sample_count, 120))
        total_seconds = (end_utc - start_utc).total_seconds()
        if total_seconds <= 0:
            results["time_range_distribution"] = {
                "error": "Time range duration is zero."
            }
            return results

        step_seconds = total_seconds / (sample_count - 1)
        sign_labels = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        house_labels = [str(i) for i in range(1, 13)]
        asc_counts = [0] * 12
        mc_counts = [0] * 12
        moon_sign_counts = [0] * 12
        sun_house_counts = [0] * 12
        moon_house_counts = [0] * 12

        for i in range(sample_count):
            utc_dt = start_utc + timedelta(seconds=step_seconds * i)
            jd_sample = get_julian_day(utc_dt)
            snap = _compute_snapshot(utc_dt, jd_sample, lat, lon, house_code, zodiac_code, ayanamsa_mode)
            asc_idx = int(snap["asc"] / 30) % 12
            mc_idx = int(snap["mc"] / 30) % 12
            moon_idx = int(snap["moon"] / 30) % 12
            asc_counts[asc_idx] += 1
            mc_counts[mc_idx] += 1
            moon_sign_counts[moon_idx] += 1

            sun_house = _house_from_cusps(snap["sun"], snap["houses"])
            moon_house = _house_from_cusps(snap["moon"], snap["houses"])
            sun_house_counts[sun_house - 1] += 1
            moon_house_counts[moon_house - 1] += 1

        results["time_range_distribution"] = {
            "range": {
                "start": time_range_start,
                "end": time_range_end,
                "minutes": int((end_localized - start_localized).total_seconds() / 60),
                "warning": range_warning
            },
            "samples": sample_count,
            "step_minutes": round(step_seconds / 60.0, 2),
            "asc_sign": _build_distribution(asc_counts, sign_labels),
            "mc_sign": _build_distribution(mc_counts, sign_labels),
            "moon_sign": _build_distribution(moon_sign_counts, sign_labels),
            "sun_house": _build_distribution(sun_house_counts, house_labels),
            "moon_house": _build_distribution(moon_house_counts, house_labels)
        }

    return results

if __name__ == "__main__":
    # Test
    print(calculate_chart_data("2023-10-27", "12:00", "New York", "NY"))
