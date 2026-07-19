import calendar
import math
from datetime import datetime
from typing import Any, Dict, List

from .models import Chart, Planet, PlanetName

# Minor Years (Least Years) of the Planets
MINOR_YEARS = {
    PlanetName.SATURN: 30,
    PlanetName.JUPITER: 12,
    PlanetName.MARS: 15,
    PlanetName.SUN: 19,
    PlanetName.VENUS: 8,
    PlanetName.MERCURY: 20,
    PlanetName.MOON: 25,
}

# Operative Houses (Chrematistikos Topoi) in priority order
OPERATIVE_HOUSES = [1, 10, 11, 7, 5, 9, 4]


class DecennialEngine:
    @staticmethod
    def _add_calendar_months(value: datetime, months: int) -> datetime:
        """Advance by civil calendar months while preserving time and timezone.

        Valens states decennial allocations in months and calls the complete
        major period 10 years 9 months (129 months).  Treating every month as
        30 uninterrupted modern days drops the intercalary days and moves
        customer-facing dates progressively early.
        """
        month_index = value.year * 12 + (value.month - 1) + months
        year, month_zero = divmod(month_index, 12)
        month = month_zero + 1
        day = min(value.day, calendar.monthrange(year, month)[1])
        return value.replace(year=year, month=month, day=day)

    @staticmethod
    def get_zodiacal_sequence(chart: Chart) -> List[Planet]:
        """
        Returns the seven traditional planets in zodiacal order,
        starting from the Ascendant degree.
        """
        traditional = [
            PlanetName.SATURN,
            PlanetName.JUPITER,
            PlanetName.MARS,
            PlanetName.SUN,
            PlanetName.VENUS,
            PlanetName.MERCURY,
            PlanetName.MOON,
        ]

        # Filter for traditional planets
        planets = [p for p in chart.planets if p.name in traditional]

        # Sort by longitude relative to Ascendant
        # normalized_offset = (p.lon - asc) % 360
        sorted_planets = sorted(
            planets, key=lambda p: (p.longitude - chart.ascendant) % 360.0
        )

        return sorted_planets

    @staticmethod
    def select_apheta(chart: Chart) -> Planet:
        """
        Selects the Apheta (Releaser) for Decennials.
        1. Sect Light in Operative Place
        2. Contrary Light in Operative Place
        3. Post-Ascendant Planet
        """
        # Determine Sect
        # Note: chart.sun_altitude is used to determine day/night
        is_day = chart.sun_altitude > 0.0

        sun = next((p for p in chart.planets if p.name == PlanetName.SUN), None)
        moon = next((p for p in chart.planets if p.name == PlanetName.MOON), None)

        # Helper to find house of a planet
        def get_house(planet_lon: float) -> int:
            if not chart.houses:
                return 1  # Fallback
            # Find which house contains the longitude
            # For Whole Sign, it's just index from Ascendant sign
            asc_sign_idx = int(chart.ascendant / 30)
            p_sign_idx = int(planet_lon / 30)
            house = (p_sign_idx - asc_sign_idx) % 12 + 1
            return house

        # 1. Sect Light
        sect_light = sun if is_day else moon
        if sect_light:
            house = get_house(sect_light.longitude)
            if house in OPERATIVE_HOUSES:
                return sect_light

        # 2. Contrary Light
        contrary_light = moon if is_day else sun
        if contrary_light:
            house = get_house(contrary_light.longitude)
            if house in OPERATIVE_HOUSES:
                return contrary_light

        # 3. Post-Ascendant
        sequence = DecennialEngine.get_zodiacal_sequence(chart)
        return sequence[0]

    @staticmethod
    def generate_decennials(
        chart: Chart, start_date: datetime, lifespan_years: int = 100
    ) -> List[Dict]:
        """
        Generate the 129-month major periods and their planetary month shares.

        Major periods last 10 years 9 months.  Their sub-periods use the
        planets' minor years as calendar months and therefore sum to the same
        129 months.  After all seven planets, the zodiacal sequence repeats
        from the apheta; the separate "jump to the fourth" rule belongs to a
        different quarter-period method and is not used here.
        """
        apheta = DecennialEngine.select_apheta(chart)
        full_sequence = DecennialEngine.get_zodiacal_sequence(chart)

        results = []

        # Align sequence to Apheta
        start_idx = full_sequence.index(apheta)
        current_sequence = full_sequence[start_idx:] + full_sequence[:start_idx]

        period_count = max(1, math.ceil((lifespan_years * 12) / 129))
        for i in range(period_count):
            major_lord = current_sequence[i % len(current_sequence)]
            # Every boundary is computed from the birth anchor with cumulative
            # months. Chaining from a previously clamped date (e.g. a Feb 29 or
            # day-31 birth landing in a shorter month) would permanently lose
            # the anchor day and break the 129-month invariant.
            major_start = DecennialEngine._add_calendar_months(start_date, i * 129)
            major_end = DecennialEngine._add_calendar_months(start_date, (i + 1) * 129)
            major_period: Dict[str, Any] = {
                "major_lord": major_lord.name.value,
                "start_date": major_start.isoformat(),
                "end_date": major_end.isoformat(),
                "duration_months": 129,
                "aphetic_lord": apheta.name.value,
                "source_rule_id": "valens_decennials_129_months",
                "sub_periods": [],
            }

            # Sub-periods start with Major Lord
            offset = i % len(current_sequence)
            sub_sequence = current_sequence[offset:] + current_sequence[:offset]
            cumulative_months = i * 129

            for sub_lord in sub_sequence:
                duration_months = MINOR_YEARS[sub_lord.name]
                sub_start = DecennialEngine._add_calendar_months(
                    start_date, cumulative_months
                )
                cumulative_months += duration_months
                sub_end = DecennialEngine._add_calendar_months(
                    start_date, cumulative_months
                )

                major_period["sub_periods"].append(
                    {
                        "sub_lord": sub_lord.name.value,
                        "start_date": sub_start.isoformat(),
                        "end_date": sub_end.isoformat(),
                        "duration_months": duration_months,
                    }
                )

            if cumulative_months != (i + 1) * 129:
                raise ValueError(
                    "Decennial sub-periods must total the 129-month major period"
                )

            results.append(major_period)

        return results
