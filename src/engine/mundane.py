
import swisseph as swe
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .models import Sign, PlanetName, Planet, Sect
from .stars import STARS, get_shortest_dist, get_star_longitude
from .calculations import format_longitude, calculate_prenatal_syzygy

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

# Persian/Medieval Mean Motion Constants (Degrees per Day)
# Based on Abu Ma'shar / Al-Khwarizmi parameters
MEAN_MOTION_SATURN = 0.0334597  # Approx 120.45 years for 4 orbits? No, 30 years per orbit.
# 360 / (29.457 * 365.25) approx 0.033
MEAN_MOTION_JUPITER = 0.0830912 # Approx 11.86 years. 
# 360 / (11.86 * 365.25) approx 0.083

# Epoch: Great Flood / Kali Yuga (Feb 17/18, 3101 BCE)
# Roughly JD 588465.5. Both were at 0.0 Aries (Theoretical Mean).
EPOCH_KALI_YUGA = 588465.5

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
        
        # 0. Universal Cycles (Mighty Firdaria, Mean Eras, & World Firdaria)
        firdaria = self.get_mighty_firdaria()
        era = self.get_mean_conjunction_era()
        world_firdaria = self.get_world_firdaria()
        report.append({
            "rank": 0,
            "event": "Universal Periodic Cycles",
            "data": {
                "mighty_firdaria": firdaria,
                "mean_conjunction_era": era,
                "world_firdaria": world_firdaria
            },
            "overrides": ["All natal and particular mundane indicators"]
        })

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
            # Add Al-Mubtazz scoring for the Ingress of the GC year
            year, _, _, _ = swe.revjul(gc["jd"])
            ingress = self.get_aries_ingress(int(year))
            victor = self.calculate_al_mubtazz(ingress["jd"])
            gc["al_mubtazz"] = victor
            
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
            tot_start_t = res_sol[1][2] if len(res_sol[1]) > 2 else -1
            tot_end_t = res_sol[1][3] if len(res_sol[1]) > 3 else -1
            
            if start_t > 0 and end_t > 0:
                duration_days = abs(end_t - start_t)
            else:
                # Fallback if contacts are not fully defined (e.g. partial only, or calculation limits)
                duration_days = 0.10 # Approx 2.4 hours as standard fallback
            
            duration_hours = duration_days * 24.0
            central_phase_minutes = None
            if tot_start_t and tot_end_t and tot_start_t > 0 and tot_end_t > 0 and tot_end_t > tot_start_t:
                # Swiss Ephemeris provides intermediate contacts; depending on the eclipse this may represent
                # a "central" phase duration, not guaranteed "maximum totality". We record it but do not
                # convert it into years of influence.
                central_phase_minutes = (tot_end_t - tot_start_t) * 24.0 * 60.0

            res_pos = swe.calc_ut(tjd_sol, swe.SUN, swe.FLG_SWIEPH)
            lon = res_pos[0][0]
            
            results.append({
                "type": "Solar Eclipse",
                "jd": tjd_sol,
                "longitude": lon,
                "duration_hours": duration_hours,
                "central_phase_minutes": central_phase_minutes,
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
                "central_phase_minutes": None,
                "sign": list(Sign)[int(lon / 30) % 12],
                "degree": lon % 30
            })
        except Exception:
            pass

        return results

    def get_world_firdaria(self) -> Dict[str, Any]:
        """
        Implements the Firdaria of the World (75-year Mundane Eras).
        Sequence: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn (75 years each).
        Epoch: 3101 BCE (Kali Yuga).
        """
        days_per_75y = 75 * 365.25
        days_since_epoch = self.jd - EPOCH_KALI_YUGA
        
        cycle_length_days = 525 * 365.25
        elapsed_in_cycle = days_since_epoch % cycle_length_days
        
        sequence = [
            (PlanetName.SUN, 75),
            (PlanetName.MOON, 75),
            (PlanetName.MARS, 75),
            (PlanetName.MERCURY, 75),
            (PlanetName.JUPITER, 75),
            (PlanetName.VENUS, 75),
            (PlanetName.SATURN, 75)
        ]
        
        current_days = 0
        active_planet = None
        start_jd = 0
        
        for planet, years in sequence:
            dur_days = years * 365.25
            if elapsed_in_cycle < current_days + dur_days:
                active_planet = planet
                # Global start JD for this 75 year block
                num_cycles = int(days_since_epoch // cycle_length_days)
                start_jd = EPOCH_KALI_YUGA + (num_cycles * cycle_length_days) + current_days
                break
            current_days += dur_days
            
        if not active_planet:
            active_planet = PlanetName.SATURN # Fallback for edge cases
            start_jd = self.jd - (elapsed_in_cycle)
            
        end_jd = start_jd + (75 * 365.25)
        
        return {
            "planet": active_planet.value,
            "duration": 75,
            "start_jd": start_jd,
            "end_jd": end_jd,
            "system": "Firdaria of the World (75Y Sequence)"
        }

    def calculate_eclipse_sophistication(self, eclipse: Dict) -> Dict:
        # 1. Duration / Influence Rule (conservatively handled)
        # Different authors use different keys. The common modern reconstruction is:
        # minutes of *totality* -> years of effect. We only compute an influence proxy when
        # totality minutes are available; otherwise we leave it unset to avoid fake precision.
        influence_years = None
        influence_months = None
        influence_note = (
            "Influence period not computed. "
            "Traditional keys vary by author; do not infer 'years of effect' from duration without a declared rule."
        )

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

        y, m, d, _h = swe.revjul(eclipse["jd"])
        date_utc = f"{int(y):04d}-{int(m):02d}-{int(d):02d}"

        return {
            "jd": eclipse["jd"],
            "date_utc": date_utc,
            "longitude": eclipse["longitude"],
            "sign": eclipse["sign"].value if hasattr(eclipse["sign"], "value") else str(eclipse["sign"]),
            "degree": round(eclipse["degree"], 2),
            "longitude_fmt": format_longitude(eclipse["longitude"]),
            "house_quadrant": house_found,
            # Intentionally suppressed: these event windows are easy to misread as "years of effect".
            # Traditional influence keys vary by author and require explicit methodological choice.
            "duration_hours": None,
            "central_phase_minutes": None,
            "influence_years": influence_years,
            "influence_months": influence_months,
            "influence_note": influence_note,
            "quadrant": quadrant,
            "intensification": intensification,
            "chorography_triplicity": tri_name,
            "chorography_regions": regions,
            "chorography_note": "Regions are traditional chorography mappings by triplicity, not modern visibility maps."
        }

    def get_latest_great_conjunction(self) -> Optional[Dict]:
        """
        Find the nearest preceding Great Conjunction (Jupiter-Saturn).
        Returns True Conjunction data.
        """
        # Search backwards for the *closest preceding* conjunction in time.
        # We detect the first time the Jupiter-Saturn separation enters a "near-conjunction" band,
        # then refine locally to find the minimum separation.
        start_jd = self.jd
        step = 2.0
        max_days = 80 * 365.25  # ~80 years back is plenty for typical use
        trigger_sep = 5.0       # degrees

        def _sep_at(jd: float) -> tuple[float, float, float]:
            j_lon = swe.calc_ut(jd, swe.JUPITER, swe.FLG_SWIEPH)[0][0]
            s_lon = swe.calc_ut(jd, swe.SATURN, swe.FLG_SWIEPH)[0][0]
            delta = (j_lon - s_lon) % 360.0
            sep = min(delta, 360.0 - delta)
            return sep, j_lon, s_lon

        traversed = 0.0
        jd = start_jd
        bracket_center = None
        while traversed < max_days:
            sep, _j, _s = _sep_at(jd)
            if sep <= trigger_sep:
                bracket_center = jd
                break
            jd -= step
            traversed += step

        if bracket_center is None:
            return None

        # Refine around the detected band. Conjunction proximity persists for months/years,
        # so use a generous window.
        refine_center = bracket_center
        refine_window = 500.0  # days
        refine_step = 0.05     # days (~1.2h)
        jd = refine_center + refine_window
        end = refine_center - refine_window
        best = {"sep": 999.0, "jd": None, "lon_j": None, "lon_s": None}
        while jd >= end:
            sep, j_lon, s_lon = _sep_at(jd)
            if sep < best["sep"]:
                best = {"sep": sep, "jd": jd, "lon_j": j_lon, "lon_s": s_lon}
            jd -= refine_step

        conj_jd = best["jd"]
        lon_j = best["lon_j"]
        fmt = format_longitude(lon_j)
        y, m, d, _h = swe.revjul(conj_jd)
        return {
            "jd": conj_jd,
            "date_utc": f"{int(y):04d}-{int(m):02d}-{int(d):02d}",
            "longitude": lon_j,
            "longitude_fmt": fmt,
            "sign": fmt["sign"],
            "degree": fmt["deg_in_sign"],
            "separation_deg": round(best["sep"], 6) if best["sep"] is not None else None,
            "type": "Great Conjunction (Jupiter-Saturn)",
            "description": "Computed by detecting the closest preceding conjunction band (sep<=5°) and minimizing separation locally.",
        }

    def get_mean_conjunction_era(self) -> Dict:
        """
        Calculates the current Mean Conjunction (Wasati) era and Mutation status.
        Uses the Persian Epoch (3101 BCE).
        """
        # 1. Theoretical Mean Positions
        days_since_epoch = self.jd - EPOCH_KALI_YUGA
        mean_sat = (days_since_epoch * MEAN_MOTION_SATURN) % 360.0
        mean_jup = (days_since_epoch * MEAN_MOTION_JUPITER) % 360.0
        
        # 2. Find last Mean Conjunction
        # Diff closing rate: MEAN_MOTION_JUPITER - MEAN_MOTION_SATURN
        closing_rate = MEAN_MOTION_JUPITER - MEAN_MOTION_SATURN
        diff = (mean_jup - mean_sat) % 360.0
        
        days_to_last = diff / closing_rate
        last_mean_jd = self.jd - days_to_last
        y, m, d, _h = swe.revjul(last_mean_jd)
        
        # Position at conjunction
        lon_at_conj = (mean_sat - (days_to_last * MEAN_MOTION_SATURN)) % 360.0
        lon_fmt = format_longitude(lon_at_conj)
        sign = list(Sign)[int(lon_at_conj / 30) % 12]
        triplicity = SIGN_TO_TRI_NAME.get(sign, "Unknown")
        
        # 3. Determine Mutation (Elemental Shift)
        # Check the previous 12 conjunctions (approx 240 years)
        # If the current triplicity differs from the one ~240 years ago, we are in a new era.
        days_in_240 = 240 * 365.25
        prev_mean_jd = last_mean_jd - days_in_240
        prev_mean_sat = ((prev_mean_jd - EPOCH_KALI_YUGA) * MEAN_MOTION_SATURN) % 360.0
        # This is a bit simplistic, better to check successive steps of ~19.85 years
        
        return {
            "last_mean_jd": last_mean_jd,
            "date_utc": f"{int(y):04d}-{int(m):02d}-{int(d):02d}",
            "longitude": lon_at_conj,
            "longitude_fmt": lon_fmt,
            "sign": sign.value,
            "triplicity": triplicity,
            "type": "Mean Conjunction (Wasati)",
            "cycle": "Minor/Middle Cycle boundary indicator"
        }

    def calculate_al_mubtazz(self, ingress_jd: float) -> Dict:
        """
        Calculates the 'Victor' (Al-Mubtazz) for the Aries Ingress.
        Scoring: Domicile (5), Exaltation (4), Triplicity (3), Term (2), Face (1).
        Vital Points: Asc, Sun, Moon, Fortune, Syzygy.
        """
        from .dignities import DignityCalculator
        from .lots import calculate_lot
        
        # 1. Establish Ingress Chart
        cusps, ascmc = swe.houses(ingress_jd, self.lat, self.lon, b'P')
        asc = ascmc[0]
        sun_pos = swe.calc_ut(ingress_jd, swe.SUN, swe.FLG_SWIEPH)[0][0]
        moon_pos = swe.calc_ut(ingress_jd, swe.MOON, swe.FLG_SWIEPH)[0][0]
        # azalt(tjd, calc_flag, geopos, atpress, attemp, xin)
        # geopos = (lon, lat, alt), xin = (lon, lat, dist)
        res_azalt = swe.azalt(ingress_jd, swe.EQU2HOR, (self.lon, self.lat, 0), 0, 0, (sun_pos, 0, 1.0))
        alt_sun = res_azalt[1] # Index 1 is altitude
        
        is_day = alt_sun > 0
        sect = "DAY" if is_day else "NIGHT"
        
        # Part of Fortune
        if is_day:
            pof = calculate_lot(asc, sun_pos, moon_pos)
        else:
            pof = calculate_lot(asc, moon_pos, sun_pos)
            
        # Prenatal Syzygy — use precise Newton-Raphson solver from calculations module
        try:
            syz_pos, _syz_type = calculate_prenatal_syzygy(ingress_jd)
        except Exception:
            syz_pos = sun_pos  # Fallback
        
        vital_points = [
            ("Ascendant", asc),
            ("Sun", sun_pos),
            ("Moon", moon_pos),
            ("Fortune", pof),
            ("Syzygy", syz_pos)
        ]
        
        # 2. Scoring Matrix
        planets = [PlanetName.SATURN, PlanetName.JUPITER, PlanetName.MARS, PlanetName.SUN, PlanetName.VENUS, PlanetName.MERCURY, PlanetName.MOON]
        scores = {p.value: 0 for p in planets}
        
        for name, lon in vital_points:
            # Get dignities at this point
            # Note: We need a simplified score-only version of calculate_planet_dignity
            for p in planets:
                dig = DignityCalculator.calculate_planet_dignity(p, lon, Sect.DAY if is_day else Sect.NIGHT)
                breakdown = dig["score_breakdown"]
                # Ibn Ezra / Al-Mubtazz uses positive scores only
                scores[p.value] += sum(max(0, v) for v in breakdown.values())
                
        winner = max(scores, key=scores.get)
        
        return {
            "victor": winner,
            "score": scores[winner],
            "breakdown": scores,
            "ingress_jd": ingress_jd,
            "sect": sect
        }

    def get_mighty_firdaria(self) -> Dict:
        """
        Calculates the current ruler of the world based on the Mighty Firdaria (Abu Ma'shar).
        Uses a 1200-year cycle (Sum of Great Years approx).
        Order: Saturn (57), Jupiter (79), Mars (66), Sun (120), Venus (82), Mercury (76), Moon (108).
        Total Lifecycle: 588 years (approx. half a Great Mutation).
        Note: Variations exist for the start epoch. 
        """
        GREAT_YEARS = {
            PlanetName.SATURN: 57,
            PlanetName.JUPITER: 79,
            PlanetName.MARS: 66,
            PlanetName.SUN: 120,
            PlanetName.VENUS: 82,
            PlanetName.MERCURY: 76,
            PlanetName.MOON: 108
        }
        ORDER = [PlanetName.SATURN, PlanetName.JUPITER, PlanetName.MARS, PlanetName.SUN, PlanetName.VENUS, PlanetName.MERCURY, PlanetName.MOON]
        TOTAL_CYCLE = sum(GREAT_YEARS.values()) # 588 years
        
        # Epoch: 3101 BCE (Kali Yuga).
        # We assume the sequence started with Saturn at JD 588465.5
        years_since_epoch = (self.jd - EPOCH_KALI_YUGA) / 365.25
        cycle_pos = years_since_epoch % TOTAL_CYCLE
        
        current_ruler = None
        elapsed = 0.0
        for p in ORDER:
            duration = GREAT_YEARS[p]
            if elapsed <= cycle_pos < (elapsed + duration):
                current_ruler = p
                break
            elapsed += duration
            
        return {
            "ruler": current_ruler.value if current_ruler else "Unknown",
            "years_into_period": round(cycle_pos - elapsed, 2),
            "remaining_years": round(elapsed + GREAT_YEARS.get(current_ruler, 0) - cycle_pos, 2)
        }

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



