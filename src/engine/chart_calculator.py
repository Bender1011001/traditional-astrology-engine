import swisseph as swe
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz
from datetime import datetime
import os

# Initialize Geocoder
geolocator = Nominatim(user_agent="astrology_app")
tf = TimezoneFinder()

def get_coordinates(city: str, state: str = "") -> tuple[float, float]:
    """
    Get latitude and longitude for a given city and state.
    """
    query = f"{city}, {state}" if state else city
    location = geolocator.geocode(query)
    if location:
        return location.latitude, location.longitude
    raise ValueError(f"Could not find location: {query}")

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

def calculate_chart_data(date_str: str, time_str: str, city: str, state: str = ""):
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
        local_dt = local_tz.localize(local_dt)
        utc_dt = local_dt.astimezone(pytz.utc)
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
    
    results = {
        "meta": {
            "date": date_str,
            "time": time_str,
            "city": city,
            "state": state,
            "lat": lat,
            "lon": lon,
            "timezone": tz_str,
            "utc_time": utc_dt.isoformat(),
            "julian_day": jd
        },
        "planets": {},
        "houses": {}
    }

    # Flags: SEFLG_SWIEPH (use Ephemeris), SEFLG_SPEED (calc speed)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    topo_flags = flags | swe.FLG_TOPOCTR
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

            results["planets"][name] = {
                "longitude": coords[0],
                "latitude": coords[1],
                "distance": coords[2],
                "speed": coords[3],
                "altitude": altitude,
                "is_retrograde": coords[3] < 0
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
        results["planets"]["South_Node"] = {
            "longitude": (nn_lon + 180) % 360,
            "latitude": -results["planets"]["North_Node"]["latitude"],
            "speed": results["planets"]["North_Node"]["speed"],
            "is_retrograde": True # Nodes are usually Rx
        }


    # 6. Houses (Placidus is default 'P', Whole Sign is 'W')
    # swe.houses(jd, lat, lon, b'P') 
    # returns (cusps, ascmc)
    # ascmc: 0=Asc, 1=MC, 2=ARM, 3=Vertex, ...
    
    try:
        cusps, ascmc = swe.houses(jd, lat, lon, b'P')
        results["houses"] = {i+1: c for i, c in enumerate(cusps)}
        results["angles"] = {
            "Ascendant": ascmc[0],
            "MC": ascmc[1]
        }
    except Exception as e:
        results["error_houses"] = str(e)

    return results

if __name__ == "__main__":
    # Test
    print(calculate_chart_data("2023-10-27", "12:00", "New York", "NY"))
