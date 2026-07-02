from datetime import datetime, timedelta
from typing import Dict, List, Optional

import swisseph as swe

from .models import Chart, Planet, PlanetName, Sect, Sign
from .reference_data import DOMICILES

# Zodiacal Releasing Planetary Years (Valens)
ZR_YEARS = {
    Sign.ARIES: 15,
    Sign.TAURUS: 8,
    Sign.GEMINI: 20,
    Sign.CANCER: 25,
    Sign.LEO: 19,
    Sign.VIRGO: 20,
    Sign.LIBRA: 8,
    Sign.SCORPIO: 15,
    Sign.SAGITTARIUS: 12,
    Sign.CAPRICORN: 27,
    Sign.AQUARIUS: 30,
    Sign.PISCES: 12,
}


def calculate_profection_sign(ascendant_sign: Sign, age: int) -> Sign:
    signs = list(Sign)
    start_index = signs.index(ascendant_sign)
    target_index = (start_index + age) % 12
    return signs[target_index]


def get_lord_of_year(profection_sign: Sign) -> PlanetName:
    return DOMICILES[profection_sign]


def calculate_monthly_profection(
    annual_sign: Sign,
    month: int,
    method: str = "Continuous",
    natal_start_sign: Optional[Sign] = None,
    age: Optional[int] = None,
    total_months: Optional[int] = None,
) -> Sign:
    """
    Implements Monthly Profection.
    - Continuous: 1 sign per month from the annual profection sign.
    - Saltatory: 12 signs per year cycle, but jump-calculated from natal start sign (e.g. Ascendant).

    month: 1-indexed (1 to 12)
    """
    signs = list(Sign)
    if method == "Continuous":
        start_index = signs.index(annual_sign)
        target_index = (start_index + (month - 1)) % 12
        return signs[target_index]
    elif method == "Saltatory":
        if natal_start_sign is None or age is None:
            raise ValueError("Natal start sign and age required for Saltatory method")
        # Total months since birth; if not provided, fall back to whole-year months
        if total_months is None:
            total_months = (age * 12) + (month - 1)
        start_index = signs.index(natal_start_sign)
        target_index = (start_index + total_months) % 12
        return signs[target_index]
    else:
        raise ValueError(f"Unknown profection method: {method}")


def calculate_daily_profection(monthly_sign: Sign, day: float, method: str = "Standard") -> Sign:
    """
    Implements Daily Profection.
    Standard: 2 days and 8 hours (2.333 days) per sign from the monthly profection sign.
    Valens: Exactly 1 sign per day rate.

    day: 1-indexed (1 to 30)
    """
    signs = list(Sign)
    
    if method == "Valens":
        rate = 1.0
    else:
        # 2 days and 8 hours = 2 + 8/24 = 2.3333... days
        # which is exactly 7/3 days.
        rate = 7 / 3

    start_index = signs.index(monthly_sign)
    # We subtract 1 from day to make it 0-indexed for calculation
    steps = int((day - 1) / rate)
    target_index = (start_index + steps) % 12
    return signs[target_index]


def calculate_epitasis_days(monthly_sign: Sign, transiting_loy_sign: Sign, method: str = "Standard") -> list[int]:
    """
    Identify specific days within a month where the Daily Profection matches
    the zodiacal sign of the transiting Lord of the Year.

    This is the 'Secret Key' of Book IV where symbolic time (Profection)
    matches real time (Transit).
    """
    epitasis_days = []
    # Check for a standard 30-day month
    for day in range(1, 31):
        daily_sign = calculate_daily_profection(monthly_sign, float(day), method=method)
        if daily_sign == transiting_loy_sign:
            epitasis_days.append(day)
    return epitasis_days


def get_opposite_sign(sign: Sign) -> Sign:
    signs = list(Sign)
    idx = signs.index(sign)
    return signs[(idx + 6) % 12]


def calculate_zr_lifetime_map(
    start_sign: Sign, birth_date: datetime, years: int = 100, max_level: int = 4
) -> list:
    """
    Calculates the full Zodiacal Releasing lifetime map (L1 through L4).
    Returns a nested structure of L1 chapters, L2 paragraphs, L3 sentences, L4 words.

    Level durations (Valens):
    - L1: planetary years of the sign (in 360-day years)
    - L2: same units, nested within L1
    - L3: L2 years → treated as months; duration = ZR_YEARS[sign] * (30/360) = ZR_YEARS[sign]/12 months
    - L4: L3 months → treated as days; duration = ZR_YEARS[sign] * (30/360) further

    Each level starts from the sign of its parent level.
    """
    signs = list(Sign)

    def _build_level(
        parent_sign_idx: int,
        parent_start_date: datetime,
        parent_duration_days: float,
        level: int,
    ) -> list:
        """Recursively build sub-periods for a given level."""
        entries = []
        elapsed_days = 0
        current_idx = parent_sign_idx
        opposite_sign = signs[(parent_sign_idx + 6) % 12]
        sequence_count = 0

        while elapsed_days < parent_duration_days:
            # Loosing of the Bond at 13th sign (if parent is long enough)
            is_lb = sequence_count == 12
            if is_lb:
                current_idx = signs.index(opposite_sign)

            current_sign = signs[current_idx]

            # Duration at this level: planetary years / scale factor
            raw_duration = ZR_YEARS[current_sign]
            if level == 1:
                duration_days = int(raw_duration * 360)  # Years → days (360-day year)
            elif level == 2:
                duration_days = int(raw_duration * 30)  # Months → days
            elif level == 3:
                duration_days = int(raw_duration * 2.5)  # ~2.5 days per unit (30/12)
            elif level == 4:
                duration_days = int(raw_duration * (2.5 / 12.0))  # ~5 hours per unit (2.5/12)
            else:
                break

            # Don't exceed parent boundaries
            remaining = parent_duration_days - elapsed_days
            if duration_days > remaining:
                duration_days = float(remaining)  # type: ignore

            start = parent_start_date + timedelta(days=elapsed_days)
            end = start + timedelta(days=duration_days)

            is_foreshadowing = (
                current_sign == opposite_sign and not is_lb and sequence_count < 12
            )

            entry = {
                "level": level,
                "sign": current_sign.value,
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": end.strftime("%Y-%m-%d"),
                "status": (
                    "Loosing of the Bond"
                    if is_lb
                    else ("Foreshadowing" if is_foreshadowing else "Normal")
                ),
                "is_pivot": is_lb or is_foreshadowing,
            }

            # Recursively add sub-periods (only if requested and not at max level)
            if level < max_level and level <= 2:
                # Only nest L3 inside L2, and L4 inside L3 (for the current target date queries)
                # Full L3/L4 for all L2 would be massive — only do for level <= 2
                sub = _build_level(current_idx, start, duration_days, level + 1)
                entry["sub_periods"] = sub  # type: ignore

            entries.append(entry)

            elapsed_days += duration_days
            current_idx = (current_idx + 1) % 12
            sequence_count += 1

            if elapsed_days >= parent_duration_days:
                break

        return entries

    # Build L1 chapters
    chapters = []
    total_days_elapsed = 0
    max_days = years * 360
    current_l1_idx = signs.index(start_sign)

    while total_days_elapsed < max_days:
        l1_sign = signs[current_l1_idx]
        l1_duration_days = ZR_YEARS[l1_sign] * 360

        l1_start = birth_date + timedelta(days=total_days_elapsed)
        l1_end = l1_start + timedelta(days=l1_duration_days)

        chapter = {
            "level": 1,
            "sign": l1_sign.value,
            "start_date": l1_start.strftime("%Y-%m-%d"),
            "end_date": l1_end.strftime("%Y-%m-%d"),
            "duration_years": ZR_YEARS[l1_sign],
            "paragraphs": _build_level(current_l1_idx, l1_start, l1_duration_days, 2),
        }

        chapters.append(chapter)
        total_days_elapsed += l1_duration_days
        current_l1_idx = (current_l1_idx + 1) % 12

    return chapters


def calculate_zr_periods(
    start_sign: Sign, start_date: datetime, target_date: datetime, level: int = 2
) -> dict:
    """
    Calculates Zodiacal Releasing periods for a specific date.
    Returns L1 through L4 (if available).
    """
    full_map = calculate_zr_lifetime_map(start_sign, start_date, years=120, max_level=4)

    target_date_str = target_date.strftime("%Y-%m-%d")

    for l1 in full_map:
        if l1["start_date"] <= target_date_str < l1["end_date"]:
            for l2 in l1["paragraphs"]:
                if l2["start_date"] <= target_date_str < l2["end_date"]:
                    result = {
                        "Level 1": l1["sign"],
                        "Level 2": l2["sign"],
                        "L1_Duration_Years": l1["duration_years"],
                        "Status": l2["status"],
                        "L2_Start": l2["start_date"],
                        "L2_End": l2["end_date"],
                    }

                    # Traverse L3 if available
                    for l3 in l2.get("sub_periods", []):
                        if l3["start_date"] <= target_date_str < l3["end_date"]:
                            result["Level 3"] = l3["sign"]
                            result["L3_Status"] = l3["status"]
                            result["L3_Start"] = l3["start_date"]
                            result["L3_End"] = l3["end_date"]
                            break

                    return result

    return {"Level 1": "Unknown", "Level 2": "End of Period"}


# Firdaria Sequences
FIRDARIA_DAY = [
    (PlanetName.SUN, 10),
    (PlanetName.VENUS, 8),
    (PlanetName.MERCURY, 13),
    (PlanetName.MOON, 9),
    (PlanetName.SATURN, 11),
    (PlanetName.JUPITER, 12),
    (PlanetName.MARS, 7),
    (PlanetName.NORTH_NODE, 3),
    (PlanetName.SOUTH_NODE, 2),
]

FIRDARIA_NIGHT = [
    (PlanetName.MOON, 9),
    (PlanetName.SATURN, 11),
    (PlanetName.JUPITER, 12),
    (PlanetName.MARS, 7),
    (PlanetName.SUN, 10),
    (PlanetName.VENUS, 8),
    (PlanetName.MERCURY, 13),
    (PlanetName.NORTH_NODE, 3),
    (PlanetName.SOUTH_NODE, 2),
]


def calculate_firdaria(sect: Sect, birth_date: datetime, target_date: datetime) -> dict:
    """
    Calculates the Firdaria period and sub-period for a given date.
    Returns a dict with major period, sub-period, and date ranges.
    """
    sequence = FIRDARIA_DAY if sect == Sect.DAY else FIRDARIA_NIGHT

    # Calculate age in years
    age_days = (target_date - birth_date).days
    age_years = age_days / 365.25

    if age_years < 0:
        return {"error": "Target date is before birth date"}

    current_age = 0.0
    major_period = None
    major_start_age = 0.0

    for planet, duration in sequence:
        if age_years < current_age + duration:
            major_period = planet
            major_start_age = current_age
            major_duration = duration
            break
        current_age += duration

    if major_period is None:
        return {"error": "Age exceeds Firdaria cycle (75 years)"}

    # Sub-periods (only for the 7 planets, not for Nodes)
    if major_period in [PlanetName.NORTH_NODE, PlanetName.SOUTH_NODE]:
        sub_period = major_period
        sub_start_age = major_start_age
        sub_end_age = major_start_age + major_duration
    else:
        # Each major period is divided into 7 equal sub-periods
        sub_duration = major_duration / 7.0
        elapsed_in_major = age_years - major_start_age
        sub_idx = int(elapsed_in_major / sub_duration)
        if sub_idx > 6:
            sub_idx = 6

        # Sub-period sequence: starts with major ruler, follows the 7-planet sequence
        planets_only = [
            p
            for p, d in sequence
            if p not in [PlanetName.NORTH_NODE, PlanetName.SOUTH_NODE]
        ]
        start_planet_idx = planets_only.index(major_period)
        sub_period = planets_only[(start_planet_idx + sub_idx) % 7]

        sub_start_age = major_start_age + (sub_idx * sub_duration)
        sub_end_age = sub_start_age + sub_duration

    def age_to_date(age):
        return birth_date + timedelta(days=age * 365.25)

    return {
        "Major Period": major_period.value,
        "Sub Period": sub_period.value,
        "Major Start": age_to_date(major_start_age).strftime("%Y-%m-%d"),
        "Major End": age_to_date(major_start_age + major_duration).strftime("%Y-%m-%d"),
        "Sub Start": age_to_date(sub_start_age).strftime("%Y-%m-%d"),
        "Sub End": age_to_date(sub_end_age).strftime("%Y-%m-%d"),
        "Current Age": round(age_years, 2),
    }


def calculate_solar_return_jd(
    natal_sun_lon: float, birth_jd: float, target_year: int
) -> float:
    """
    Finds the exact Julian Day when the Sun returns to natal_sun_lon in the given year.
    Uses Swiss Ephemeris to find the moment the Sun reaches the exact longitude.
    """
    # Calculate approximate JD for the target year's birthday
    # Convert birth JD back to date to get month/day
    y, m, d, h = swe.revjul(birth_jd)

    # Start search 5 days before the birthday in target year
    # We use UTC 12:00 for the start point
    jd_start = swe.julday(target_year, m, d, 12.0) - 5

    # Search for the next solar return (Sun returning to natal longitude)
    # We use a simple Newton-Raphson or binary search?
    # Swiss Ephemeris doesn't have a direct 'return' function for Sun,
    # but we can find the moment Sun lon == target.

    current_jd = jd_start
    for _ in range(10):  # Iterative refinement
        res = swe.calc_ut(current_jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED)
        sun_lon = res[0][0]

        diff = (natal_sun_lon - sun_lon + 180) % 360 - 180
        # Sun moves approx 0.041 degrees per hour, or 0.98 deg/day
        # We can use speed from res if available
        speed = res[0][3] if (len(res[0]) > 3 and res[0][3] != 0) else 0.9856

        delta_jd = diff / speed
        current_jd += delta_jd

        if abs(diff) < 0.00001:  # High precision
            break

    return current_jd


def calculate_lunar_phase_advanced(sun_lon: float, moon_lon: float) -> dict:
    """
    Calculates the 8 Lunar Phases and returns detailed profile.
    """
    diff = (moon_lon - sun_lon) % 360
    phase_idx = int(diff / 45)

    phases = [
        {
            "name": "New Moon",
            "angle_range": (0, 45),
            "profile": "The Primitive/The Initiator. Subjective, impulsive, seeding new impulses.",
            "type": "New Beginnings",
        },
        {
            "name": "Waxing Crescent",
            "angle_range": (45, 90),
            "profile": "The Breakthrough/The Mobilizer. Struggle to manifest new forms against the past.",
            "type": "Growth",
        },
        {
            "name": "First Quarter",
            "angle_range": (90, 135),
            "profile": "The Builder/The Crisis-Actor. 'Crisis in Action' - building new structures.",
            "type": "Action",
        },
        {
            "name": "Waxing Gibbous",
            "angle_range": (135, 180),
            "profile": "The Perfector/The Analyst. Refining and evaluating the work; seeking growth.",
            "type": "Refinement",
        },
        {
            "name": "Full Moon",
            "angle_range": (180, 225),
            "profile": "The Realizer/The Objectifier. Objectivity, Relationship, and Revelation.",
            "type": "Fruition",
        },
        {
            "name": "Disseminating",
            "angle_range": (225, 270),
            "profile": "The Teacher/The Demonstrator. Sharing realized vision and values.",
            "type": "Demonstration",
        },
        {
            "name": "Last Quarter",
            "angle_range": (270, 315),
            "profile": "The Revisor/The Crisis-Thinker. 'Crisis in Consciousness' - re-evaluating beliefs.",
            "type": "Re-evaluation",
        },
        {
            "name": "Balsamic",
            "angle_range": (315, 360),
            "profile": "The Prophet/The Seed-Man. Introverted, Future-Oriented, Distillation and Release.",
            "type": "Release",
        },
    ]

    return phases[phase_idx]


def calculate_solar_arcs(natal_chart: Chart, age_years: float) -> list[Planet]:
    """
    Implements 'Degree for a Year' solar arc progression.
    All planets moved forward by (Age * Sun's average daily motion) or
    more commonly exactly 1 degree per year in 'Degree for a Year' method.
    The prompt says "Degree for a Year solar arc progression".
    """
    arc = age_years  # 1 degree per year
    progressed_planets = []

    for p in natal_chart.planets:
        new_lon = (p.longitude + arc) % 360
        progressed_planets.append(Planet(name=p.name, longitude=new_lon))

    return progressed_planets


def calculate_muntha(natal_asc_sign: Sign, age_years: int) -> dict:
    """
    Calculates the Muntha (profected Ascendant for the year).
    Moves 1 sign per year.
    """
    signs = list(Sign)
    start_idx = signs.index(natal_asc_sign)
    target_idx = (start_idx + age_years) % 12
    muntha_sign = signs[target_idx]

    return {"sign": muntha_sign.value, "age": age_years}


class AdvancedPredictionEngine:
    """
    Integrated Prediction Engine for Advanced Techniques.
    """

    def __init__(
        self,
        natal_chart: Chart,
        birth_date: datetime,
        birth_jd: float,
        lat: float,
        lon: float,
    ):
        self.natal_chart = natal_chart
        self.birth_date = birth_date
        self.birth_jd = birth_jd
        self.lat = lat
        self.lon = lon
        self.sect = Sect.DAY if natal_chart.sun_altitude > 0 else Sect.NIGHT
        self.epsilon = 23.4392911

    def get_mercury_stations(self) -> List[Dict]:
        """
        Scans ephemeris from birth to 100 days after to find progressed Mercury stations.
        Rule: 1 day = 1 year.
        """
        stations: List[Dict] = []
        prev_speed = None

        # Flags for search
        for day in range(100):
            jd = self.birth_jd + day
            res = swe.calc_ut(jd, swe.MERCURY, swe.FLG_SWIEPH | swe.FLG_SPEED)
            speed = res[0][3]

            if prev_speed is not None:
                # Check for zero-crossing
                if prev_speed > 0 and speed <= 0:
                    stations.append(
                        {
                            "type": "Station Retrograde",
                            "day_after_birth": day,
                            "age": day,
                            "date": (self.birth_date + timedelta(days=day)).strftime(
                                "%Y-%m-%d"
                            ),
                            "longitude": res[0][0],
                        }
                    )
                elif prev_speed < 0 and speed >= 0:
                    stations.append(
                        {
                            "type": "Station Direct",
                            "day_after_birth": day,
                            "age": day,
                            "date": (self.birth_date + timedelta(days=day)).strftime(
                                "%Y-%m-%d"
                            ),
                            "longitude": res[0][0],
                        }
                    )
            prev_speed = speed
        return stations

    def get_sp_moon_triggers(self, target_date: datetime) -> List[Dict]:
        """
        Calculates Progressed Moon position and checks for hits to Primary Direction promissors.
        """
        age_years = (target_date - self.birth_date).days / 365.25
        progressed_jd = self.birth_jd + age_years

        res = swe.calc_ut(progressed_jd, swe.MOON, swe.FLG_SWIEPH)
        sp_moon_lon = res[0][0]

        triggers = []
        # Check hard aspects to natal planets (Conjunction, Square, Opposition)
        for p in self.natal_chart.planets:
            diff = abs(sp_moon_lon - p.longitude) % 360
            dist = diff if diff <= 180 else 360 - diff

            aspect = None
            if dist < 1.0:
                aspect = "Conjunct"
            elif abs(dist - 90) < 1.0:
                aspect = "Square"
            elif abs(dist - 180) < 1.0:
                aspect = "Opposition"

            if aspect:
                triggers.append(
                    {
                        "type": "Secondary Progressed Moon Trigger",
                        "aspect": aspect,
                        "target": p.name.value,
                        "age": round(age_years, 2),
                        "note": f"SP Moon {aspect} natal {p.name.value} acts as high-intensity trigger for primary directions.",
                    }
                )
        return triggers

    def get_firdaria(self, target_date: datetime):
        return calculate_firdaria(self.sect, self.birth_date, target_date)

    def get_solar_return(self, year: int):
        sun = next(p for p in self.natal_chart.planets if p.name == PlanetName.SUN)
        return_jd = calculate_solar_return_jd(sun.longitude, self.birth_jd, year)

        # In a real scenario, we'd use this JD to calculate a full chart
        # For now, we return the JD and metadata
        y, m, d, h = swe.revjul(return_jd)
        # Handle fractional hours for datetime
        return_date = datetime(y, m, d) + timedelta(hours=h)

        return {
            "return_jd": return_jd,
            "return_date": return_date.isoformat(),
            "natal_sun_longitude": sun.longitude,
        }

    def get_solar_arcs(self, age_years: float):
        return calculate_solar_arcs(self.natal_chart, age_years)

    def get_muntha(self, age_years: int):
        # We need the sign of the natal Ascendant
        # Assuming natal_chart.ascendant is 0-360
        asc_sign_idx = int(self.natal_chart.ascendant / 30) % 12
        asc_sign = list(Sign)[asc_sign_idx]
        return calculate_muntha(asc_sign, age_years)

    def get_lunar_phase(self):
        sun = next(p for p in self.natal_chart.planets if p.name == PlanetName.SUN)
        moon = next(p for p in self.natal_chart.planets if p.name == PlanetName.MOON)
        return calculate_lunar_phase_advanced(sun.longitude, moon.longitude)

    def get_zr_lifetime_map(self, lot_name: str = "Spirit"):
        lots = self.get_lots()
        lot_lon = lots.get(lot_name)
        if lot_lon is None:
            return {"error": f"Lot {lot_name} not found"}

        lot_sign_idx = int(lot_lon / 30) % 12
        lot_sign = list(Sign)[lot_sign_idx]
        return calculate_zr_lifetime_map(lot_sign, self.birth_date)

    def get_lots(self):
        from .lots import calculate_all_lots

        return calculate_all_lots(self.natal_chart, self.sect)

    def get_active_transits(self, target_date: datetime):
        """
        Calculates active transits of outer planets (Jupiter to Pluto) to natal planets
        for the target date.
        """
        # Calculate transiting positions
        t_jd = swe.julday(target_date.year, target_date.month, target_date.day, 12.0)

        outer_planets = [
            (swe.JUPITER, "Jupiter"),
            (swe.SATURN, "Saturn"),
            (swe.URANUS, "Uranus"),
            (swe.NEPTUNE, "Neptune"),
            (swe.PLUTO, "Pluto"),
        ]

        hits = []

        for pid, p_name in outer_planets:
            res = swe.calc_ut(t_jd, pid, swe.FLG_SWIEPH)
            t_lon = res[0][0]

            for natal_p in self.natal_chart.planets:
                # Check major hard aspects (Conjunction, Square, Opposition)
                diff = abs(t_lon - natal_p.longitude) % 360
                dist = diff if diff <= 180 else 360 - diff

                aspect = None
                orb = 3.0  # Wide orb for context

                if dist < orb:
                    aspect = "Conjunct"
                elif abs(dist - 90) < orb:
                    aspect = "Square"
                elif abs(dist - 180) < orb:
                    aspect = "Opposition"

                if aspect:
                    hits.append(
                        {
                            "transit": p_name,
                            "natal_planet": natal_p.name.value,
                            "aspect": aspect,
                            "orb": round(
                                (
                                    dist
                                    if aspect == "Conjunct"
                                    else abs(dist - (90 if aspect == "Square" else 180))
                                ),
                                2,
                            ),
                        }
                    )
        return hits

    def get_prediction_report(self, target_date: datetime):
        age_years = (target_date - self.birth_date).days / 365.25

        return {
            "firdaria": self.get_firdaria(target_date),
            "solar_arcs": [
                {"planet": p.name.value, "longitude": round(p.longitude, 2)}
                for p in self.get_solar_arcs(age_years)
            ],
            "transits": self.get_active_transits(target_date),
            "muntha": self.get_muntha(int(age_years)),
            "lunar_phase": self.get_lunar_phase(),
            "mercury_stations": self.get_mercury_stations(),
            "sp_moon_triggers": self.get_sp_moon_triggers(target_date),
            "solar_return_info": self.get_solar_return(
                target_date.year
                if target_date.month >= self.birth_date.month
                else target_date.year - 1
            ),
        }
