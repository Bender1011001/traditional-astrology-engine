import swisseph as swe
from src.engine.house_systems import AlcabitiusEngine
from .config import HOUSE_SYSTEM_LABELS

def get_planets_ut(jd: float, flags: int, topo_flags: int, geopos: tuple[float, float, float]) -> dict:
    """
    Calculate planetary positions using Swiss Ephemeris.
    """
    swe.set_topo(geopos[0], geopos[1], geopos[2]) # Set topo coords
    
    planets_map = {
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
        "North_Node": swe.MEAN_NODE 
    }
    
    results = {}
    
    for name, pid in planets_map.items():
        try:
            # Geocentric / Heliocentric / Topocentric based on flags
            res_full = swe.calc_ut(jd, pid, flags)
            coords = res_full[0] if isinstance(res_full[0], (list, tuple)) else res_full
            
             # Topocentric Altitude/Azimuth
            topo_full = swe.calc_ut(jd, pid, topo_flags)
            topo_coords = topo_full[0] if isinstance(topo_full[0], (list, tuple)) else topo_full
            xin = (topo_coords[0], topo_coords[1], topo_coords[2])
            
            # Alt/Az logic
            azresult = swe.azalt(jd, swe.ECL2HOR, geopos, 0, 0, xin)
            altitude = azresult[1]
            
            results[name] = {
                "longitude": coords[0],
                "latitude": coords[1],
                "distance": coords[2],
                "speed": coords[3],
                "altitude": altitude
            }
        except swe.Error as e:
             # Fallback logic could go here
             # For now just re-raise or return error dict
             # Emulating old behavior:
             res_full = swe.calc_ut(jd, pid, 0) # Fallback to default flags
             coords = res_full[0] if isinstance(res_full[0], (list, tuple)) else res_full
             results[name] = {
                 "longitude": coords[0],
                 "latitude": coords[1],
                 "distance": coords[2],
                 "speed": coords[3],
                 "note": "Moshier fallback"
             }
             
    return results

def get_houses(jd: float, lat: float, lon: float, house_code: str, ayanamsa_deg: float | None = None) -> tuple[dict, list]:
    """
    Calculate House Cusps and Angles (Asc, MC).
    """
    if house_code == 'B':
        cusps_dict = AlcabitiusEngine.calculate_houses(jd, lat, lon)
        _, ascmc = swe.houses(jd, lat, lon, b'W') # Use W to get AS/MC
        cusps = [cusps_dict[i] for i in range(1, 13)]
    else:
        cusps, ascmc = swe.houses(jd, lat, lon, house_code.encode())
    
    if ayanamsa_deg is not None:
         cusps = [((c - ayanamsa_deg) % 360) for c in cusps]
         ascmc = [((a - ayanamsa_deg) % 360) for a in ascmc]
         
    return {i + 1: c for i, c in enumerate(cusps)}, ascmc

def compare_house_systems_calc(jd: float, lat: float, lon: float, systems: list[str], ayanamsa_deg: float | None = None) -> dict:
    houses_by_system = {}
    errors = {}
    
    for code in systems:
        try:
            cusps, _ = swe.houses(jd, lat, lon, code.encode())
            if ayanamsa_deg is not None:
                cusps = [((c - ayanamsa_deg) % 360) for c in cusps]
            
            label = HOUSE_SYSTEM_LABELS.get(code, code)
            houses_by_system[label] = {i+1: c for i, c in enumerate(cusps)}
        except Exception as e:
            label = HOUSE_SYSTEM_LABELS.get(code, code)
            errors[label] = str(e)
            
    return houses_by_system, errors
