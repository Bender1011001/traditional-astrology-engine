from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .models import PlanetName
import swisseph as swe

class PlanetaryHourEngine:
    """
    Implements the Traditional Planetary Hours Algorithm (Sunrise Convention).
    Calculates Temporal Hours and Planetary Rulers for Day and Hour.
    """

    CHALDEAN_ORDER = [
        PlanetName.SATURN,
        PlanetName.JUPITER,
        PlanetName.MARS,
        PlanetName.SUN,
        PlanetName.VENUS,
        PlanetName.MERCURY,
        PlanetName.MOON
    ]

    DAY_RULERS = {
        0: PlanetName.MOON,      # Monday
        1: PlanetName.MARS,      # Tuesday
        2: PlanetName.MERCURY,   # Wednesday
        3: PlanetName.JUPITER,   # Thursday
        4: PlanetName.VENUS,     # Friday
        5: PlanetName.SATURN,    # Saturday
        6: PlanetName.SUN        # Sunday
    }

    @staticmethod
    def _calculate_sun_times(lat: float, lon: float, date: datetime) -> Dict:
        """
        Calculates distinct sunrise/sunset for the given date.
        Uses swisseph to get precise rise/set times.
        Returns JD and datetime for current day's sunrise/sunset and next sunrise.
        """
        # We need sunrise/sunset for the chart date, and next sunrise for night hours.
        # Ensure geopos is set
        swe.set_topo(lon, lat, 0)
        
        # JD for midnight (start of day) and noon
        jd_midnight = swe.julday(date.year, date.month, date.day, 0.0)
        jd_noon = swe.julday(date.year, date.month, date.day, 12.0)
        
        # Calculate Rise/Set
        # flags: BIT_DISC_CENTER (0) or BIT_NO_REFRACTION etc.
        # Standard: Center of disc + refraction? 
        # Actually traditionally: Upper limb appearance.
        # swe.rise_trans is complex. Using ChartCalculator helper if available? 
        # Let's use swe.rise_trans directly.
        # Planet Sun = 0
        
        # Ephemeris flags are separate from rise/set calculation flags.
        ephe_flags = swe.FLG_SWIEPH
        # NOTE: For planetary hours, standard topocentric rise is best.
        
        geopos = (lon, lat, 0)
        
        # Calculate Rise/Set flags
        calc_rise = swe.CALC_RISE | swe.BIT_DISC_CENTER | swe.BIT_FIXED_DISC_SIZE
        calc_set = swe.CALC_SET | swe.BIT_DISC_CENTER | swe.BIT_FIXED_DISC_SIZE
        
        # Using 7 arguments: jd, planet, rsmi (calc flags), geopos, atpress, attemp, ephe_flags
        # Note: flags variable holds the ephemeris flags (FLG_SWIEPH)
        
        # Sunrise: search from midnight to find TODAY's sunrise (not tomorrow's)
        res_rise = swe.rise_trans(jd_midnight, swe.SUN, calc_rise, geopos, 0, 0, ephe_flags)
        # Sunset: search from noon (sunset always after noon)
        res_set = swe.rise_trans(jd_noon, swe.SUN, calc_set, geopos, 0, 0, ephe_flags)
        
        # Next Sunrise: search from today's noon
        res_next_rise = swe.rise_trans(jd_noon, swe.SUN, calc_rise, geopos, 0, 0, ephe_flags)

        # Convert simple JDs
        if len(res_rise) > 0: rise_jd = res_rise[1][0]
        else: rise_jd = 0 # Polar?
        
        if len(res_set) > 0: set_jd = res_set[1][0]
        else: set_jd = 0
        
        if len(res_next_rise) > 0: next_rise_jd = res_next_rise[1][0]
        else: next_rise_jd = 0

        return {
            "rise_jd": rise_jd,
            "set_jd": set_jd,
            "next_rise_jd": next_rise_jd
        }

    @staticmethod
    def calculate_hours(chart_dt: datetime, lat: float, lon: float) -> Dict:
        """
        Calculates the planetary hour data for a specific datetime.
        """
        # Get Sun times for the date
        # Note: Chart dt might be before sunrise (meaning previous planetary day)
        # We need to check if dt < sunrise.
        
        times = PlanetaryHourEngine._calculate_sun_times(lat, lon, chart_dt)
        if times["rise_jd"] == 0:
            return {"error": "Polar condition unhandled"} # Simplified for now

        # Convert chart dt to JD for comparison
        chart_jd = swe.julday(chart_dt.year, chart_dt.month, chart_dt.day, 
                              chart_dt.hour + chart_dt.minute/60.0 + chart_dt.second/3600.0)

        # Logic: If chart_jd < rise_jd, we are in the night of the previous day.
        # We must re-calculate periods for Yesterday Sunrise -> Yesterday Sunset -> Today Sunrise.
        
        if chart_jd < times["rise_jd"]:
            # Recalculate for yesterday
            prev_day = chart_dt - timedelta(days=1)
            times = PlanetaryHourEngine._calculate_sun_times(lat, lon, prev_day)
            # Logic check:
            # Rise = Yesterday Rise
            # Set = Yesterday Set
            # Next Rise = Today Rise (which is > chart_jd, so chart_jd is in Night phase)
            current_phase = "NIGHT"
        elif chart_jd >= times["set_jd"]:
            # Chart is after Sunset -> Night phase of Today
            current_phase = "NIGHT"
        else:
            # Chart is Day phase
            current_phase = "DAY"
            
        rise = times["rise_jd"]
        setting = times["set_jd"]
        next_rise = times["next_rise_jd"]

        # Calculate Lengths
        day_len = setting - rise
        night_len = next_rise - setting
        
        day_hour_len = day_len / 12
        night_hour_len = night_len / 12
        
        # Day Ruler
        # Determine civil weekday at the time of the *Planetary Day start* (Rise)
        # If we went back a day, use that weekday
        # We can implement a clean logical check:
        # JD to Date conversion
        rise_y, rise_m, rise_d, rise_h = swe.revjul(rise)
        # Python weekday: Mon=0
        # date(rise_y, rise_m, rise_d).weekday()
        # Just use math from JD? 
        # (J + 1.5) % 7 -> gives 0 for Monday?
        # Standard: JD 0 = Mon Jan 1 4713 BC?
        # (floor(jd + 0.5)) % 7 gives: 0=Mon, 1=Tue, ..., 6=Sun.
        
        wd_idx = int(rise + 0.5) % 7
        day_ruler = PlanetaryHourEngine.DAY_RULERS[wd_idx]
        
        # Hour Calculation
        hour_number = 1
        
        if current_phase == "DAY":
            elapsed = chart_jd - rise
            hour_idx = int(elapsed / day_hour_len) # 0-11
            hour_number = hour_idx + 1
            
            # Start planet is Day Ruler
            # Sequence: Chaldean Order.
            # Index of Day Ruler
            start_idx = PlanetaryHourEngine.CHALDEAN_ORDER.index(day_ruler)
            current_planet_idx = (start_idx + hour_idx) % 7
            hour_ruler = PlanetaryHourEngine.CHALDEAN_ORDER[current_planet_idx]
            
            # Remaining time
            # next hour start
            next_hour_jd = rise + ((hour_idx + 1) * day_hour_len)
            mins_remaining = (next_hour_jd - chart_jd) * 24 * 60
            
        else: # NIGHT
            elapsed = chart_jd - setting
            hour_idx = int(elapsed / night_hour_len) # 0-11
            hour_number = hour_idx + 1 + 12 # 13-24 traditionally, or 1st night hour
            
            # Start planet for Night?
            # 1st Night Hour is always 12 hours after 1st Day Hour? No.
            # Day has 12 hours. Last Day hour (12th) is...
            # The sequence continues. 
            # Day Hour 1 = Day Ruler.
            # Day Hour 12 = (Day Ruler idx + 11) % 7
            # Night Hour 1 = (Day Ruler idx + 12) % 7
            
            start_idx = PlanetaryHourEngine.CHALDEAN_ORDER.index(day_ruler)
            # Offset = 12 day hours + hour_idx night hours
            current_planet_idx = (start_idx + 12 + hour_idx) % 7
            hour_ruler = PlanetaryHourEngine.CHALDEAN_ORDER[current_planet_idx]
            
            next_hour_jd = setting + ((hour_idx + 1) * night_hour_len)
            mins_remaining = (next_hour_jd - chart_jd) * 24 * 60
            
        return {
            "day_ruler": day_ruler.value,
            "hour_ruler": hour_ruler.value,
            "hour_number_civil": hour_number, # 1-24
            "hour_number_phase": (hour_number - 1) % 12 + 1, # 1-12
            "phase": current_phase, # DAY or NIGHT
            "minutes_remaining": mins_remaining,
            "next_hour_ruler": PlanetaryHourEngine.CHALDEAN_ORDER[(current_planet_idx + 1) % 7].value
        }
