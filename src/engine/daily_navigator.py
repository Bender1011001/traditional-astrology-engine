"""
Daily Navigator — Synthesized Predictions & Recommendations

Given a natal chart and a target date, this module layers ALL traditional
timing techniques and produces a single coherent briefing:

  1. Annual/Monthly/Daily Profections
  2. Firdaria (Major + Sub Period)
  3. Zodiacal Releasing (L1/L2/L3 from Lot of Spirit)
  4. Active Transits (Venus, Mars, Jupiter, Saturn to natal septener)
  5. Moon Condition (phase, sign, void of course)
  6. Epitasis Detection (symbolic × real-sky alignment)
  7. Planetary Day Ruler alignment
  8. Recommendations (propitiation, charity, avoidance)

Historical Use Only — not medical, financial, or legal advice.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

import swisseph as swe

from .forensic_forecast import get_profection_timings
from .lots import calculate_all_lots
from .models import Chart, PlanetName, Sect, Sign
from .prediction import (calculate_daily_profection, calculate_firdaria,
                         calculate_monthly_profection,
                         calculate_profection_sign, calculate_zr_periods,
                         get_lord_of_year)

logger = logging.getLogger(__name__)


# ── Static Look-up Tables ────────────────────────────────────────────────────

PLANET_DAYS = {
    PlanetName.SUN: "Sunday",
    PlanetName.MOON: "Monday",
    PlanetName.MARS: "Tuesday",
    PlanetName.MERCURY: "Wednesday",
    PlanetName.JUPITER: "Thursday",
    PlanetName.VENUS: "Friday",
    PlanetName.SATURN: "Saturday",
}

PLANET_CHARITY = {
    PlanetName.SUN: {
        "color": "Gold / Yellow",
        "gem": "Topaz or Amber",
        "act": "Donate to children's charities or act with generosity and visibility.",
    },
    PlanetName.MOON: {
        "color": "White / Silver",
        "gem": "Moonstone or Pearl",
        "act": "Care for the vulnerable, visit the sick, tend to domestic matters.",
    },
    PlanetName.MERCURY: {
        "color": "Mixed / Iridescent",
        "gem": "Emerald or Agate",
        "act": "Write letters, study, learn a new skill, perform acts of cleverness.",
    },
    PlanetName.VENUS: {
        "color": "Green / Rose",
        "gem": "Turquoise or Lapis Lazuli",
        "act": "Attend to beauty, art, and social harmony. Give to women's shelters.",
    },
    PlanetName.MARS: {
        "color": "Red / Crimson",
        "gem": "Carnelian or Garnet",
        "act": "Channel energy into vigorous exertion or physical discipline. Donate to first responders.",
    },
    PlanetName.JUPITER: {
        "color": "Royal Blue / Purple",
        "gem": "Sapphire or Amethyst",
        "act": "Be generous with wisdom and resources. Sponsor education or religious works.",
    },
    PlanetName.SATURN: {
        "color": "Black / Dark Brown",
        "gem": "Onyx or Hematite",
        "act": "Service to the elderly, patience exercises, donate to long-term cause.",
    },
}

SIGN_KEYWORDS = {
    Sign.ARIES: "initiative, courage, new action",
    Sign.TAURUS: "resources, stability, material security",
    Sign.GEMINI: "communication, learning, adaptability",
    Sign.CANCER: "home, family, emotional security",
    Sign.LEO: "authority, creativity, recognition",
    Sign.VIRGO: "service, health routines, analysis",
    Sign.LIBRA: "partnerships, contracts, balance",
    Sign.SCORPIO: "shared resources, investigation, hidden matters",
    Sign.SAGITTARIUS: "travel, philosophy, legal affairs",
    Sign.CAPRICORN: "career, structure, long-term goals",
    Sign.AQUARIUS: "community, innovation, alliances",
    Sign.PISCES: "solitude, spirituality, surrender",
}


# ── Core Navigator ────────────────────────────────────────────────────────────


class DailyNavigator:
    """Synthesizes all timing layers for a given natal chart and target date."""

    @staticmethod
    def generate_briefing(
        chart: Chart,
        birth_dt: datetime,
        birth_jd: float,
        target_date: datetime,
    ) -> Dict[str, Any]:
        """
        Produce a comprehensive daily briefing.

        Parameters
        ----------
        chart : Chart
            Fully reconstructed natal chart from the Auditor pipeline.
        birth_dt : datetime
            Naive-UTC birth datetime.
        birth_jd : float
            Julian Day of birth (UT).
        target_date : datetime
            The date for which to generate the briefing (usually "today").

        Returns
        -------
        dict  with keys: profections, firdaria, zodiacal_releasing, transits,
              epitasis, planetary_day, recommendations, forecast_summary
        """
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
        age_years = (target_date - birth_dt).days / 365.25
        age = int(age_years)

        # ── 1. Profections ────────────────────────────────────────────────
        asc_sign_idx = int(chart.ascendant / 30) % 12
        asc_sign = list(Sign)[asc_sign_idx]

        annual_sign = calculate_profection_sign(asc_sign, age)
        lord_of_year = get_lord_of_year(annual_sign)

        _, prof_month, prof_day = get_profection_timings(birth_dt, target_date)
        monthly_sign = calculate_monthly_profection(annual_sign, prof_month)
        daily_sign = calculate_daily_profection(monthly_sign, prof_day)
        daily_lord = get_lord_of_year(daily_sign)

        # Lord of Year natal condition
        natal_loy = next((p for p in chart.planets if p.name == lord_of_year), None)
        loy_sign_name = (
            natal_loy.sign.value if (natal_loy and natal_loy.sign) else "Unknown"
        )

        profections_block = {
            "age": age,
            "annual_sign": annual_sign.value,
            "lord_of_year": lord_of_year.value,
            "lord_of_year_natal_sign": loy_sign_name,
            "monthly_sign": monthly_sign.value,
            "monthly_lord": get_lord_of_year(monthly_sign).value,
            "daily_sign": daily_sign.value,
            "daily_lord": daily_lord.value,
            "keywords": SIGN_KEYWORDS.get(daily_sign, ""),
        }

        # ── 2. Firdaria ──────────────────────────────────────────────────
        firdaria_block = calculate_firdaria(sect, birth_dt, target_date)

        # ── 3. Zodiacal Releasing (from Lot of Spirit) ───────────────────
        zr_block: Dict[str, Any] = {}
        try:
            lots = calculate_all_lots(chart, sect)
            spirit_lon = lots.get("Spirit")
            if spirit_lon is not None:
                spirit_sign_idx = int(spirit_lon / 30) % 12
                spirit_sign = list(Sign)[spirit_sign_idx]
                zr_block = calculate_zr_periods(spirit_sign, birth_dt, target_date)
            else:
                zr_block = {"note": "Lot of Spirit not calculable."}
        except Exception as e:
            logger.warning("ZR calculation failed: %s", repr(e), exc_info=True)
            zr_block = {"note": "ZR unavailable."}

        # ── 4. Active Transits ────────────────────────────────────────────
        transits_block = DailyNavigator._compute_transits(chart, target_date)

        # ── 5. Moon Condition (phase, sign, void of course) ──────────────
        moon_block = DailyNavigator._compute_moon_condition(target_date)

        # ── 6. Epitasis Detection ────────────────────────────────────────
        target_jd = swe.julday(
            target_date.year, target_date.month, target_date.day, 12.0
        )
        loy_swe_id = DailyNavigator._planet_to_swe(lord_of_year)
        loy_transit_lon = 0.0
        if loy_swe_id is not None:
            res = swe.calc_ut(target_jd, loy_swe_id, swe.FLG_SWIEPH)
            loy_transit_lon = res[0][0]
        loy_transit_sign = list(Sign)[int(loy_transit_lon / 30) % 12]
        is_epitasis = daily_sign == loy_transit_sign

        epitasis_block = {
            "active": is_epitasis,
            "lord_of_year_transiting_sign": loy_transit_sign.value,
            "daily_profection_sign": daily_sign.value,
            "note": (
                "EPITASIS ACTIVE — Symbolic time aligns with real sky. "
                "Events seeded this year by the Lord of the Year are ripening today."
                if is_epitasis
                else "No epitasis. Symbolic and real-sky cycles are out of phase."
            ),
        }

        # ── 7. Planetary Day ─────────────────────────────────────────────
        weekday = target_date.strftime("%A")
        day_ruler_map = {
            "Sunday": PlanetName.SUN,
            "Monday": PlanetName.MOON,
            "Tuesday": PlanetName.MARS,
            "Wednesday": PlanetName.MERCURY,
            "Thursday": PlanetName.JUPITER,
            "Friday": PlanetName.VENUS,
            "Saturday": PlanetName.SATURN,
        }
        day_ruler = day_ruler_map.get(weekday, PlanetName.SUN)

        planetary_day_block = {
            "weekday": weekday,
            "ruler": day_ruler.value,
            "alignment": (
                "Strong alignment — the planetary day ruler matches your Lord of the Year."
                if day_ruler == lord_of_year
                else (
                    "Moderate alignment — the planetary day ruler matches your Daily Lord."
                    if day_ruler == daily_lord
                    else "Standard day — no special ruler alignment."
                )
            ),
        }

        # ── 8. Recommendations ───────────────────────────────────────────
        recommendations = DailyNavigator._build_recommendations(
            lord_of_year=lord_of_year,
            daily_lord=daily_lord,
            daily_sign=daily_sign,
            day_ruler=day_ruler,
            firdaria_major=firdaria_block.get("Major Period", ""),
            is_epitasis=is_epitasis,
            sect=sect,
            moon_voc=moon_block.get("void_of_course", False),
        )

        # ── 9. Forecast Summary (Plain-Language) ─────────────────────────
        forecast_summary = DailyNavigator._synthesize_summary(
            profections_block,
            firdaria_block,
            zr_block,
            transits_block,
            moon_block,
            epitasis_block,
            planetary_day_block,
            recommendations,
            target_date,
        )

        return {
            "date": target_date.strftime("%Y-%m-%d"),
            "display_date": target_date.strftime("%A, %B %d, %Y"),
            "profections": profections_block,
            "firdaria": firdaria_block,
            "zodiacal_releasing": zr_block,
            "transits": transits_block,
            "moon": moon_block,
            "epitasis": epitasis_block,
            "planetary_day": planetary_day_block,
            "recommendations": recommendations,
            "forecast_summary": forecast_summary,
        }

    # ── Private helpers ───────────────────────────────────────────────────

    @staticmethod
    def _planet_to_swe(planet: PlanetName):
        """Map PlanetName to Swiss Ephemeris constant."""
        _map = {
            PlanetName.SUN: swe.SUN,
            PlanetName.MOON: swe.MOON,
            PlanetName.MERCURY: swe.MERCURY,
            PlanetName.VENUS: swe.VENUS,
            PlanetName.MARS: swe.MARS,
            PlanetName.JUPITER: swe.JUPITER,
            PlanetName.SATURN: swe.SATURN,
        }
        return _map.get(planet)

    @staticmethod
    def _compute_transits(chart: Chart, target_date: datetime) -> List[Dict]:
        """Compute transits of traditional benefics/malefics to natal septener.

        Slower planets (Jupiter, Saturn) get a 3° orb.
        Faster planets (Mars, Venus) get a 2° orb.
        """
        t_jd = swe.julday(target_date.year, target_date.month, target_date.day, 12.0)

        # (swe_id, display_name, nature, orb_limit)
        transit_planets = [
            (swe.VENUS, "Venus", "benefic", 2.0),
            (swe.MARS, "Mars", "malefic", 2.0),
            (swe.JUPITER, "Jupiter", "benefic", 3.0),
            (swe.SATURN, "Saturn", "malefic", 3.0),
        ]
        aspects_checked = [
            ("Conjunction", 0),
            ("Sextile", 60),
            ("Square", 90),
            ("Trine", 120),
            ("Opposition", 180),
        ]
        hits = []

        for pid, p_name, nature, orb_limit in transit_planets:
            res = swe.calc_ut(t_jd, pid, swe.FLG_SWIEPH)
            t_lon = res[0][0]

            for natal_p in chart.planets:
                if natal_p.name in (
                    PlanetName.URANUS,
                    PlanetName.NEPTUNE,
                    PlanetName.PLUTO,
                    PlanetName.NORTH_NODE,
                    PlanetName.SOUTH_NODE,
                ):
                    continue

                diff = abs(t_lon - natal_p.longitude) % 360
                dist = diff if diff <= 180 else 360 - diff

                for asp_name, asp_deg in aspects_checked:
                    actual_orb = abs(dist - asp_deg)
                    if actual_orb <= orb_limit:
                        soft = asp_name in ("Conjunction", "Sextile", "Trine")
                        if nature == "benefic":
                            quality = "supportive" if soft else "mixed"
                        else:
                            quality = "tempering" if soft else "challenging"
                        hits.append(
                            {
                                "transiting": p_name,
                                "natal_planet": natal_p.name.value,
                                "aspect": asp_name,
                                "orb": round(actual_orb, 2),
                                "nature": nature,
                                "quality": quality,
                                "brief": f"Transiting {p_name} {asp_name.lower()} natal {natal_p.name.value}",
                            }
                        )
        return hits

    @staticmethod
    def _compute_moon_condition(target_date: datetime) -> Dict[str, Any]:
        """Compute today's Moon sign, phase, and void-of-course status.

        The Moon is the fastest traditional planet and its daily condition is
        one of the most important electional and natal timing indicators.
        """
        t_jd = swe.julday(target_date.year, target_date.month, target_date.day, 12.0)

        # Moon position
        moon_res = swe.calc_ut(t_jd, swe.MOON, swe.FLG_SWIEPH)
        moon_lon = moon_res[0][0]
        moon_speed = moon_res[0][3]
        moon_sign_idx = int(moon_lon / 30) % 12
        moon_sign = list(Sign)[moon_sign_idx]

        # Sun position (for phase calculation)
        sun_res = swe.calc_ut(t_jd, swe.SUN, swe.FLG_SWIEPH)
        sun_lon = sun_res[0][0]

        # Phase angle (elongation)
        elongation = (moon_lon - sun_lon) % 360

        # Phase name (traditional 8-phase system)
        if elongation < 22.5:
            phase_name = "New Moon"
        elif elongation < 67.5:
            phase_name = "Waxing Crescent"
        elif elongation < 112.5:
            phase_name = "First Quarter"
        elif elongation < 157.5:
            phase_name = "Waxing Gibbous"
        elif elongation < 202.5:
            phase_name = "Full Moon"
        elif elongation < 247.5:
            phase_name = "Waning Gibbous"
        elif elongation < 292.5:
            phase_name = "Last Quarter"
        elif elongation < 337.5:
            phase_name = "Balsamic"
        else:
            phase_name = "New Moon"

        # Phase emoji
        phase_emoji_map = {
            "New Moon": "🌑",
            "Waxing Crescent": "🌒",
            "First Quarter": "🌓",
            "Waxing Gibbous": "🌔",
            "Full Moon": "🌕",
            "Waning Gibbous": "🌖",
            "Last Quarter": "🌗",
            "Balsamic": "🌘",
        }
        phase_emoji = phase_emoji_map.get(phase_name, "🌙")

        # Void of Course detection:
        # Moon is VoC if it makes no applying Ptolemaic aspect to any
        # traditional planet before leaving its current sign.
        sign_end_lon = (moon_sign_idx + 1) * 30.0
        degrees_left = (sign_end_lon - moon_lon) % 360

        # Traditional planet positions at this moment
        trad_planets = [
            swe.SUN,
            swe.MERCURY,
            swe.VENUS,
            swe.MARS,
            swe.JUPITER,
            swe.SATURN,
        ]
        aspect_angles = [0, 60, 90, 120, 180]
        orb_voc = 8.0  # Liberal orb for VoC

        has_applying = False
        for pid in trad_planets:
            p_res = swe.calc_ut(t_jd, pid, swe.FLG_SWIEPH)
            p_lon = p_res[0][0]

            for asp_deg in aspect_angles:
                # Where would the Moon need to be for this aspect?
                target_lon_1 = (p_lon + asp_deg) % 360
                target_lon_2 = (p_lon - asp_deg) % 360

                for target_lon in [target_lon_1, target_lon_2]:
                    # Is target_lon ahead of Moon (applying) and within same sign span?
                    arc = (target_lon - moon_lon) % 360
                    if 0 < arc <= degrees_left + orb_voc and arc < 30:
                        has_applying = True
                        break
                if has_applying:
                    break
            if has_applying:
                break

        is_voc = not has_applying

        # Waxing vs waning
        waxing = elongation < 180

        return {
            "sign": moon_sign.value,
            "degree": round(moon_lon % 30, 1),
            "longitude": round(moon_lon, 2),
            "phase": phase_name,
            "phase_emoji": phase_emoji,
            "elongation": round(elongation, 1),
            "waxing": waxing,
            "speed": round(moon_speed, 2),
            "fast": moon_speed > 13.0,  # Average lunar speed ~13.2°/day
            "void_of_course": is_voc,
            "note": (
                f"The Moon is in **{moon_sign.value}** ({phase_emoji} {phase_name}). "
                + (
                    "**Void of Course** — traditional texts frame initiation symbolism as weaker; this is not decision advice. "
                    if is_voc
                    else ""
                )
                + (
                    "Waxing (increasing) — favorable for beginnings and growth."
                    if waxing
                    else "Waning (decreasing) — favorable for endings and release."
                )
            ),
        }

    @staticmethod
    def _build_recommendations(
        lord_of_year: PlanetName,
        daily_lord: PlanetName,
        daily_sign: Sign,
        day_ruler: PlanetName,
        firdaria_major: str,
        is_epitasis: bool,
        sect: Sect,
        moon_voc: bool = False,
    ) -> Dict[str, Any]:
        """Build actionable recommendations based on the dominant time lord."""
        primary_lord = lord_of_year
        charity = PLANET_CHARITY.get(primary_lord, PLANET_CHARITY[PlanetName.SUN])
        propitiation_day = PLANET_DAYS.get(primary_lord, "Any day")

        # Determine if the current day IS the propitiation day
        is_propitiation_day = day_ruler == primary_lord

        # Urgency level
        urgency = "low"
        if is_epitasis:
            urgency = "high"
        elif moon_voc or day_ruler == lord_of_year or day_ruler == daily_lord:
            urgency = "moderate"

        avoid_list = []
        do_list = []

        # Sect-aware malefic warnings
        if sect == Sect.DAY:
            destructive_malefic = PlanetName.MARS
        else:
            destructive_malefic = PlanetName.SATURN

        if daily_lord == destructive_malefic:
            avoid_list.append(
                f"Symbolic caution: the out-of-sect malefic ({destructive_malefic.value}) is today's daily lord."
            )
            do_list.append(
                "Traditional emphasis: patience, discipline, and focused work themes are highlighted."
            )
        else:
            do_list.append(
                f"The daily lord ({daily_lord.value}) favors: {SIGN_KEYWORDS.get(daily_sign, 'general activity')}."
            )

        if is_epitasis:
            do_list.append(
                "Symbolically amplified window: themes related to this year's Lord of the Year are emphasized today."
            )

        # Moon Void of Course warnings
        if moon_voc:
            avoid_list.append(
                "Void-of-Course Moon: historical timing texts describe weaker initiation symbolism; this is not advice about contracts, finances, health, safety, emergencies, or urgent choices."
            )
            do_list.append(
                "Symbolic framing: routine, review, rest, and reflection themes are emphasized more than initiation themes."
            )

        do_list.append(charity["act"])

        return {
            "primary_time_lord": primary_lord.value,
            "propitiation_day": propitiation_day,
            "is_propitiation_day": is_propitiation_day,
            "color": charity["color"],
            "gem": charity["gem"],
            "urgency": urgency,
            "do": do_list,
            "avoid": (
                avoid_list if avoid_list else ["No specific symbolic cautions for today."]
            ),
        }

    @staticmethod
    def _synthesize_summary(
        profections: Dict,
        firdaria: Dict,
        zr: Dict,
        transits: List,
        moon: Dict,
        epitasis: Dict,
        planetary_day: Dict,
        recommendations: Dict,
        target_date: datetime,
    ) -> str:
        """Produce a plain-language forecast paragraph."""
        parts = []
        parts.append(
            f"**{target_date.strftime('%A, %B %d, %Y')}** — "
            f"You are {profections['age']} years old. "
            f"The annual profection activates **{profections['annual_sign']}**, "
            f"making **{profections['lord_of_year']}** your Lord of the Year "
            f"(natal condition: {profections['lord_of_year_natal_sign']})."
        )

        parts.append(
            f"Today's daily lord is **{profections['daily_lord']}** "
            f"through the sign of **{profections['daily_sign']}** "
            f"({profections['keywords']})."
        )

        # Moon condition
        parts.append(
            f"{moon.get('phase_emoji', '🌙')} The Moon is in **{moon['sign']}** "
            f"({moon['phase']}, {moon['degree']}°). "
            + (
                "**Void of Course** — historical texts describe weaker initiation symbolism; not decision advice. "
                if moon.get("void_of_course")
                else ""
            )
            + (
                "Waxing phase favors growth and new beginnings."
                if moon.get("waxing")
                else "Waning phase favors completion and release."
            )
        )

        if not firdaria.get("error"):
            parts.append(
                f"Your Firdaria major period is ruled by **{firdaria.get('Major Period', '?')}** "
                f"with a sub-period of **{firdaria.get('Sub Period', '?')}**."
            )

        if zr.get("Level 1"):
            parts.append(
                f"Zodiacal Releasing (Spirit): L1 = **{zr.get('Level 1', '?')}**, "
                f"L2 = **{zr.get('Level 2', '?')}** "
                f"({zr.get('Status', '')})."
            )

        if transits:
            transit_strs = [t["brief"] + f" (orb {t['orb']}°)" for t in transits[:5]]
            parts.append("Active transits: " + "; ".join(transit_strs) + ".")

        if epitasis.get("active"):
            parts.append(
                "⚡ **EPITASIS ACTIVE** — The symbolic and real-sky cycles converge today. "
                "Events related to this year's Lord of the Year are at peak intensity."
            )

        parts.append(f"**Recommendation:** {recommendations['do'][0]}")

        return "\n\n".join(parts)
