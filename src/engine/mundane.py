
import swisseph as swe
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .models import Sign, PlanetName, Planet
from .stars import STARS, get_shortest_dist, get_star_longitude

# Chorography mapping from Binder1_part_001.txt
CHOROGRAPHY = {
    "Fire": ["Britain", "Gaul", "Germany"],
    "Water": ["Africa", "Western Libya"],
    "Air": ["Northeast Asia"],
    "Earth": ["Ethiopia", "Southern Asia"]
}

SIGN_TO_TRI_NAME = {
    Sign.ARIES: "Fire", Sign.LEO: "Fire", Sign.SAGITTARIUS: "Fire",
    Sign.TAURUS: "Earth", Sign.VIRGO: "Earth", Sign.CAPRICORN: "Earth",
    Sign.GEMINI: "Air", Sign.LIBRA: "Air", Sign.AQUARIUS: "Air",
    Sign.CANCER: "Water", Sign.SCORPIO: "Water", Sign.PISCES: "Water"
}

class MundaneEngine:
    """
    Implements the Mundane Hierarchy and Eclipse Sophistication rules.
    Rank 1: Eclipses
    Rank 2: Great Conjunctions (Jupiter-Saturn)
    Rank 3: Comets
    Rank 4: Seasonal Ingresses (Aries Ingress)
    """

    def __init__(self, jd: float, lat: float = 0.0, lon: float = 0.0):
        self.jd = jd
        self.lat = lat
        self.lon = lon
        self.comets = [] 

    def add_comet(self, name: str, color: str, tail_direction: str):
        """
        Classification of comets by color and tail direction.
        Ref: Binder1_part_023.txt - Mundane Hierarchy.
        """
        classification = "Unknown"
        if color.lower() in ["red", "orange", "bright"]:
            classification = "Martial (War, Fire, Sudden Events)"
        elif color.lower() in ["dark", "leaden", "grey"]:
            classification = "Saturnian (Pestilence, Cold, Structural Decay)"
        elif color.lower() in ["yellow", "white"]:
            classification = "Jupiterian/Venusian (Religious/Social turnover)"
            
        self.comets.append({
            "name": name,
            "color": color,
            "tail_direction": tail_direction,
            "classification": classification,
            "forensic_effect": f"Disruption in the direction of the {tail_direction} region."
        })

    def get_hierarchy_report(self) -> List[Dict[str, Any]]:
        report = []
        
        # 1. Eclipses (Rank 1)
        eclipses = self.get_recent_eclipses()
        for eclipse in eclipses:
            soph = self.calculate_eclipse_sophistication(eclipse)
            report.append({
                "rank": 1,
                "event": eclipse["type"],
                "data": soph,
                "overrides": ["Rank 2", "Rank 3", "Rank 4", "Natal"]
            })

        # 2. Great Conjunctions (Rank 2)
        gc = self.get_latest_great_conjunction()
        if gc:
            report.append({
                "rank": 2,
                "event": "Great Conjunction (Jupiter-Saturn)",
                "data": gc,
                "overrides": ["Rank 3", "Rank 4", "Natal"]
            })

        # 3. Comets (Rank 3)
        if self.comets:
            for comet in self.comets:
                report.append({
                    "rank": 3,
                    "event": f"Comet {comet.get('name', '')}",
                    "data": comet,
                    "overrides": ["Rank 4", "Natal"]
                })

        # 4. Seasonal Ingresses (Rank 4)
        # Calculate Aries Ingress for the year of birth
        year, month, day, hour = swe.revjul(self.jd)
        ingress = self.get_aries_ingress(int(year))
        report.append({
            "rank": 4,
            "event": "Aries Ingress",
            "data": ingress,
            "overrides": ["Natal"]
        })

        return report

    def get_recent_eclipses(self) -> List[Dict]:
        results = []
        # Solar Eclipse (Previous)
        try:
            # swe.sol_eclipse_when_glob returns [retflag, tret, attr, ...)
            # tret[0] = max eclipse, tret[1] = first contact, tret[4] = last contact
            res_sol = swe.sol_eclipse_when_glob(self.jd, swe.FLG_SWIEPH, 0, 1)
            tjd_sol = res_sol[1][0] # max eclipse
            
            # Duration calculation
            # Use absolute difference to be safe, though end should be > start
            start_t = res_sol[1][1]
            end_t = res_sol[1][4]
            duration_days = abs(end_t - start_t)
            duration_hours = duration_days * 24.0

            res_pos = swe.calc_ut(tjd_sol, swe.SUN, swe.FLG_SWIEPH)
            lon = res_pos[0][0]
            
            results.append({
                "type": "Solar Eclipse",
                "jd": tjd_sol,
                "longitude": lon,
                "duration_hours": duration_hours,
                "sign": list(Sign)[int(lon / 30) % 12],
                "degree": lon % 30
            })
        except Exception:
            pass

        # Lunar Eclipse (Previous)
        try:
            res_lun = swe.lun_eclipse_when(self.jd, swe.FLG_SWIEPH, 0, 1)
            tjd_lun = res_lun[1][0] # max eclipse
            
            # Duration calculation - for lunar we use the umbral duration (partial + total)
            # tret[1] = start of partial eclipse, tret[2] = end of partial eclipse
            start_t = res_lun[1][1]
            end_t = res_lun[1][2]
            if start_t <= 0 or end_t <= 0:
                # Fallback to penumbral
                start_t = res_lun[1][5]
                end_t = res_lun[1][6]
            
            if start_t > 0 and end_t > 0:
                duration_days = abs(end_t - start_t)
            else:
                # Fallback if no contacts found
                duration_days = 0.04 # approx 1 hour
            duration_hours = duration_days * 24.0

            res_pos = swe.calc_ut(tjd_lun, swe.MOON, swe.FLG_SWIEPH)
            lon = res_pos[0][0]
            
            results.append({
                "type": "Lunar Eclipse",
                "jd": tjd_lun,
                "longitude": lon,
                "duration_hours": duration_hours,
                "sign": list(Sign)[int(lon / 30) % 12],
                "degree": lon % 30
            })
        except Exception:
            pass

        return results

    def calculate_eclipse_sophistication(self, eclipse: Dict) -> Dict:
        # 1. Duration Rule
        # Solar: 1 hour = 1 year influence
        # Lunar: 1 hour = 1 month influence
        if eclipse["type"] == "Solar Eclipse":
            influence_years = eclipse["duration_hours"]
            influence_months = influence_years * 12
        else:
            influence_months = eclipse["duration_hours"]
            influence_years = influence_months / 12.0

        # 2. Timing Rule (Quadrants of Intensification)
        # Calculate local chart for eclipse time
        houses, ascmc = swe.houses(eclipse["jd"], self.lat, self.lon, b'P')
        asc = ascmc[0]
        mc = ascmc[1]
        dsc = (asc + 180) % 360
        ic = (mc + 180) % 360
        
        eclipse_lon = eclipse["longitude"]
        
        # Determine Quadrant
        quadrant = "Unknown"
        # East (Rise to MC): 12, 11, 10
        # South (MC to Set): 9, 8, 7
        # West (Set to IC): 6, 5, 4
        # North (IC to Rise): 3, 2, 1
        
        # Simple house-based check using Swiss Eph houses
        # Find which house the eclipse longitude falls in
        # houses array is [cusp1, cusp2, ... cusp12]
        house_found = 0
        for i in range(12):
            c1 = houses[i]
            c2 = houses[(i+1)%12]
            # Handle wrapping
            if c1 < c2:
                if c1 <= eclipse_lon < c2:
                    house_found = i + 1
                    break
            else:
                if eclipse_lon >= c1 or eclipse_lon < c2:
                    house_found = i + 1
                    break
        
        if house_found in [12, 1, 2]:
            quadrant = "Ascendant (Months 1-4)"
            intensification = "Early onset - immediate impact."
        elif house_found in [11, 10, 9]:
            quadrant = "Midheaven (Months 5-8)"
            intensification = "Mid-period onset - peak visibility."
        elif house_found in [8, 7, 6]:
            quadrant = "Descendant (Months 9-12)"
            intensification = "Late onset - impact via others/contracts."
        else:
            quadrant = "IC (Hidden/Root)"
            intensification = "Internal or foundational impact."

        # 3. Chorography
        sign = eclipse["sign"]
        tri_name = SIGN_TO_TRI_NAME.get(sign, "Unknown")
        regions = CHOROGRAPHY.get(tri_name, [])

        return {
            "duration_hours": eclipse["duration_hours"],
            "influence_period": f"{influence_years:.2f} years ({influence_months:.2f} months)",
            "quadrant": quadrant,
            "intensification": intensification,
            "chorography_triplicity": tri_name,
            "affected_regions": regions
        }

    def get_latest_great_conjunction(self) -> Optional[Dict]:
        """
        Find the nearest preceding Great Conjunction (Jupiter-Saturn).
        """
        curr_jd = self.jd
        # Step back in 30-day increments
        max_iter = 300 # Approx 25 years
        prev_diff = None
        
        for _ in range(max_iter):
            res_j = swe.calc_ut(curr_jd, swe.JUPITER, swe.FLG_SWIEPH)
            res_s = swe.calc_ut(curr_jd, swe.SATURN, swe.FLG_SWIEPH)
            lon_j = res_j[0][0]
            lon_s = res_s[0][0]
            
            diff = (lon_j - lon_s + 180) % 360 - 180 # Normalized -180 to 180
            
            if prev_diff is not None and (prev_diff * diff < 0):
                # Found crossing! Refine with binary search or simple iteration
                # For production, we'd use a solver, but let's approximate
                # The crossing happened between curr_jd and curr_jd + 30
                return {
                    "jd": curr_jd,
                    "longitude": lon_j,
                    "sign": list(Sign)[int(lon_j / 30) % 12].value,
                    "description": "Great Conjunction of Jupiter and Saturn (20-year cycle)"
                }
            
            prev_diff = diff
            curr_jd -= 30.0
            
        return None

    def get_aries_ingress(self, year: int) -> Dict:
        """
        Calculate the Aries Ingress for the given year.
        Sun enters 0° Aries.
        """
        # Start at approx March 20 of that year
        # swe.julday(year, month, day, hour)
        t_approx = swe.julday(year, 3, 20, 0)
        
        # Use swe.solcross to find exact crossing of 0 longitude
        # if not available in this binding, we iterate
        curr_jd = t_approx
        for _ in range(20): # Search around March
            res_sun = swe.calc_ut(curr_jd, swe.SUN, swe.FLG_SWIEPH)
            lon = res_sun[0][0]
            # We want lon to be 0.
            # Handle wrapping around 360/0
            if lon > 300: lon -= 360
            
            if abs(lon) < 0.01:
                break
            # Sun moves approx 1 degree per day
            curr_jd -= lon 
            
        final_sun = swe.calc_ut(curr_jd, swe.SUN, swe.FLG_SWIEPH)
        lon = final_sun[0][0]
        
        return {
            "jd": curr_jd,
            "longitude": lon,
            "sign": "Aries",
            "degree": 0.0,
            "description": f"Aries Ingress {year}"
        }

def get_recent_eclipses(jd: float) -> List[Dict]:
    """Maintain backward compatibility."""
    engine = MundaneEngine(jd)
    return engine.get_recent_eclipses()

def check_eclipse_impact(chart_lon: float, eclipse_lon: float, orb: float = 3.0) -> Optional[str]:
    """
    Check if an eclipse hit a sensitive point.
    """
    diff = abs(chart_lon - eclipse_lon)
    if diff > 180: diff = 360 - diff
    
    if diff <= orb:
        return f"DIRECT HIT (Orb {diff:.2f}°)"
    return None

def check_universal_causation_dec2025(jd: float) -> List[Dict]:
    """
    Specific audit for December 2025 based on Binder1_part_007.
    Checks for the influence of the October 2024 Solar Eclipse.
    """
    results = []
    # Oct 2, 2024 Solar Eclipse was at approx 190.0 (Libra 10°)
    # Duration was roughly 5 hours (example from prompt)
    # If we follow the rule: 1 hour = 1 year
    if 2460585.5 <= jd <= 2462412.5: # 5 year span
        results.append({
            "cause": "October 2024 Solar Eclipse (Libra 10°)",
            "status": "ACTIVE (Year 1 of 5)",
            "rule": "Universal Overdrive: Suspension of Natal Promises",
            "longitude": 190.0,
            "description": "Ptolemaic duration rule: 1 hour obscuration = 1 year influence."
        })
    return results

def get_transiting_planets(jd: float) -> List[Planet]:
    """
    Returns a lightweight set of transiting planets for global dashboards.
    """
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    planet_ids = {
        PlanetName.SUN: swe.SUN,
        PlanetName.MOON: swe.MOON,
        PlanetName.MERCURY: swe.MERCURY,
        PlanetName.VENUS: swe.VENUS,
        PlanetName.MARS: swe.MARS,
        PlanetName.JUPITER: swe.JUPITER,
        PlanetName.SATURN: swe.SATURN
    }

    planets = []
    for name, pid in planet_ids.items():
        res = swe.calc_ut(jd, pid, flags)[0]
        planets.append(Planet(name=name, longitude=res[0], latitude=res[1], speed=res[3]))
    return planets

def get_active_fixed_stars(jd: float) -> List[Dict]:
    """
    Identify fixed stars activated by transiting planets.
    """
    active = []
    planets = get_transiting_planets(jd)
    for planet in planets:
        for star in STARS:
            star_lon = get_star_longitude(star, jd)
            dist = get_shortest_dist(planet.longitude, star_lon)
            if dist <= star.orb:
                active.append({
                    "star": star.name,
                    "planet": planet.name.value,
                    "orb": round(dist, 2),
                    "nature": star.nature,
                    "glory": star.glory,
                    "nemesis": star.nemesis
                })
    return active

def build_world_dashboard(jd: float) -> Dict[str, Any]:
    """
    Builds a global astrology snapshot for a given Julian Day.
    """
    engine = MundaneEngine(jd)
    eclipses = engine.get_recent_eclipses()
    enriched_eclipses = []
    for eclipse in eclipses:
        sign = eclipse["sign"]
        tri_name = SIGN_TO_TRI_NAME.get(sign, "Unknown")
        enriched_eclipses.append({
            "type": eclipse["type"],
            "jd": eclipse["jd"],
            "longitude": eclipse["longitude"],
            "sign": sign.value,
            "degree": round(eclipse["degree"], 2),
            "duration_hours": round(eclipse["duration_hours"], 2),
            "triplicity": tri_name,
            "affected_regions": CHOROGRAPHY.get(tri_name, []),
            "stress_note": "Eclipse pressures this sign's collective narratives."
        })

    transiting = []
    for p in get_transiting_planets(jd):
        transiting.append({
            "planet": p.name.value,
            "longitude": round(p.longitude, 2),
            "sign": p.sign.value,
            "speed": round(p.speed, 4)
        })

    return {
        "fixed_star_alerts": get_active_fixed_stars(jd),
        "eclipses": enriched_eclipses,
        "universal_overdrive": check_universal_causation_dec2025(jd),
        "transiting_planets": transiting,
        "note": "Universal events can suspend personal promises when they contact natal planets or angles."
    }
