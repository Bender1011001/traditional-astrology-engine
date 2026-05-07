"""
FREE READING GENERATOR
======================
Template-based, instant, zero-LLM reading for the B2C funnel.
Extracts key consumer-friendly data from Auditor chart output and renders
a clean HTML reading in < 3 seconds. No API credits consumed.

Architecture:
  Auditor.generate_full_nativity() → chart_data dict → this module → HTML string

This module is the "hook" that converts a visitor into a paying customer.
The free reading shows enough to be valuable, then CTAs toward $25/$69 tiers.
"""

import json
import logging
from typing import Any, Dict, Optional

from src.engine.forensic_engine import Auditor

logger = logging.getLogger(__name__)


# =============================================================================
# CONSUMER-FRIENDLY SIGN INTERPRETATIONS
# These are accurate traditional descriptions, written for a general audience.
# =============================================================================

SUN_IN_SIGN = {
    "Aries": {
        "title": "The Pioneer",
        "text": "Your Sun in Aries marks you as a person of action and initiative. In the traditional system, Aries is the domicile of Mars — the planet of courage, assertion, and decisive movement. You are driven to lead, to begin new ventures, and to meet challenges head-on. The ancients associated this placement with military commanders and entrepreneurs: people who forge ahead where others hesitate.",
    },
    "Taurus": {
        "title": "The Builder",
        "text": "Your Sun in Taurus places you under the governance of Venus in her earthly domicile. This is the sign of acquisition, stability, and material mastery. The classical tradition marks Taurus natives as patient accumulators — builders of lasting wealth and enduring structures. You value what is real, tangible, and proven.",
    },
    "Gemini": {
        "title": "The Messenger",
        "text": "Your Sun in Gemini falls under Mercury's rule — the planet of intellect, communication, and exchange. Traditional astrology associates Gemini with scribes, merchants, and intermediaries: those who move between worlds, translating ideas and connecting people. You are naturally curious, adaptable, and skilled with words.",
    },
    "Cancer": {
        "title": "The Guardian",
        "text": "Your Sun in Cancer places you in the domicile of the Moon — the planet of nurture, memory, and instinct. The classical tradition marks Cancer as the sign of ancestry, home, and deep emotional bonds. You are protective of those you love, sensitive to your environment, and possess a powerful intuitive faculty.",
    },
    "Leo": {
        "title": "The Sovereign",
        "text": "Your Sun in Leo is in its own domicile — the most powerful placement for the luminary of Spirit and will. Traditional astrology associates Leo with kings, nobles, and figures of authority. You are naturally drawn to leadership, creative expression, and being recognized for your contributions. The Sun here shines at full power.",
    },
    "Virgo": {
        "title": "The Analyst",
        "text": "Your Sun in Virgo falls under Mercury's second domicile — the earth sign of precision, craft, and discernment. The classical tradition associates Virgo with skilled artisans, physicians, and scholars: those who refine, correct, and perfect. You possess a penetrating analytical mind and a drive toward practical mastery.",
    },
    "Libra": {
        "title": "The Diplomat",
        "text": "Your Sun in Libra is in the sign of its Fall — but do not mistake this for weakness. Venus rules here, and the traditional emphasis is on negotiation, alliance, and aesthetic judgment. The ancients associated Libra with judges, diplomats, and architects of social order. Your strength lies in balance, fairness, and strategic collaboration.",
    },
    "Scorpio": {
        "title": "The Investigator",
        "text": "Your Sun in Scorpio places you under Mars's nocturnal domicile — the sign of depth, intensity, and unyielding resolve. Traditional astrology associates Scorpio with those who operate beneath the surface: investigators, strategists, and guardians of secrets. You have an extraordinary capacity for focus and psychological insight.",
    },
    "Sagittarius": {
        "title": "The Explorer",
        "text": "Your Sun in Sagittarius falls under Jupiter's fiery domicile — the sign of religion, philosophy, and far-reaching journeys. The classical tradition marks Sagittarius natives as seekers of truth, teachers, and adventurers. You are driven by meaning, vision, and the desire to understand the larger pattern of existence.",
    },
    "Capricorn": {
        "title": "The Architect",
        "text": "Your Sun in Capricorn places you under Saturn's earthly domicile — the sign of structure, ambition, and long-term planning. Traditional astrology associates Capricorn with statesmen, administrators, and empire builders: those who play the long game. You are disciplined, patient, and capable of sustained effort toward distant goals.",
    },
    "Aquarius": {
        "title": "The Reformer",
        "text": "Your Sun in Aquarius is in its Detriment — the sign opposite Leo. Under Saturn's airy domicile, the traditional emphasis is on systems, communities, and unconventional thinking. The ancients associated Aquarius with philosophers, engineers, and those who challenge the established order. Your vision extends beyond the individual to the collective.",
    },
    "Pisces": {
        "title": "The Mystic",
        "text": "Your Sun in Pisces places you under Jupiter's watery domicile — the sign of dreams, compassion, and transcendence. The classical tradition marks Pisces as the final sign, associated with spiritual seekers, healers, and artists who channel something beyond the material. You possess deep empathy and an instinct for the unseen.",
    },
}

MOON_IN_SIGN = {
    "Aries": {
        "title": "Instinct of Action",
        "text": "Your Moon in Aries gives you fast emotional reflexes. You process feelings through action — when upset, you move; when inspired, you charge forward. The traditional view: the Moon in Mars's sign produces bold instincts but restless moods.",
    },
    "Taurus": {
        "title": "Instinct of Comfort",
        "text": "Your Moon in Taurus is Exalted — one of the strongest lunar placements. Your emotional nature is steady, reliable, and deeply connected to physical comfort and beauty. The ancients said this Moon gives contentment and a natural talent for attracting material security.",
    },
    "Gemini": {
        "title": "Instinct of Curiosity",
        "text": "Your Moon in Gemini processes emotions through conversation and mental stimulation. You need variety, social engagement, and intellectual sparring to feel alive. The traditional view: Mercury's sign gives the Moon quick wit but sometimes scattered focus.",
    },
    "Cancer": {
        "title": "Instinct of Protection",
        "text": "Your Moon in Cancer is in its own Domicile — the most powerful lunar placement of all. Your emotional life is rich, deep, and closely tied to family and memory. The ancients said this Moon gives powerful intuition and an almost psychic sensitivity to the moods of others.",
    },
    "Leo": {
        "title": "Instinct of Expression",
        "text": "Your Moon in Leo processes emotions through creativity and dramatic expression. You need recognition, warmth, and a stage — even if that stage is your living room. The traditional view: the Sun's domicile gives the Moon warmth and generosity but also a need for admiration.",
    },
    "Virgo": {
        "title": "Instinct of Service",
        "text": "Your Moon in Virgo finds emotional security through order, routine, and being useful. You process feelings practically — by fixing, organizing, or analyzing. The traditional view: Mercury's earth sign gives the Moon precision but can produce anxiety when things feel chaotic.",
    },
    "Libra": {
        "title": "Instinct of Harmony",
        "text": "Your Moon in Libra processes emotions through relationships and aesthetic environments. You need peace, beauty, and balanced partnerships to feel centered. The traditional view: Venus's air sign gives the Moon social grace and a talent for negotiation.",
    },
    "Scorpio": {
        "title": "Instinct of Depth",
        "text": "Your Moon in Scorpio is in its Fall — but this produces intensity, not weakness. Your emotional nature runs deep and you feel things with extraordinary power. The traditional view: Mars's water sign gives the Moon resilience and determination, but emotions can become consuming.",
    },
    "Sagittarius": {
        "title": "Instinct of Freedom",
        "text": "Your Moon in Sagittarius processes emotions through adventure, philosophy, and humor. You need space, freedom, and the sense that life has meaning. The traditional view: Jupiter's fire sign gives the Moon optimism and restlessness in equal measure.",
    },
    "Capricorn": {
        "title": "Instinct of Control",
        "text": "Your Moon in Capricorn is in its Detriment — the sign opposite Cancer. Your emotional nature is controlled, strategic, and goal-oriented. The ancients said this Moon produces self-discipline and endurance, but the price is a tendency to suppress vulnerability.",
    },
    "Aquarius": {
        "title": "Instinct of Independence",
        "text": "Your Moon in Aquarius processes emotions through ideas, communities, and causes. You need mental stimulation and social engagement but also significant personal space. The traditional view: Saturn's air sign gives the Moon a cool, objective quality.",
    },
    "Pisces": {
        "title": "Instinct of Compassion",
        "text": "Your Moon in Pisces processes emotions through empathy, imagination, and creativity. Your boundaries are naturally permeable — you absorb the emotional atmosphere of any room you enter. The traditional view: Jupiter's water sign gives the Moon exceptional sensitivity and artistic talent.",
    },
}

RISING_SIGN = {
    "Aries": {
        "title": "The Warrior's Gate",
        "text": "With Aries rising, Mars is the lord of your chart. Your first impression is one of directness, energy, and confidence. The body tends toward an athletic build with a distinctive forehead or facial features. Traditionally, Aries rising marks a life defined by initiative and physical courage.",
    },
    "Taurus": {
        "title": "The Earth Gate",
        "text": "With Taurus rising, Venus governs your chart. Your first impression is one of calm stability, with an appreciation for beauty and comfort. The body tends toward a solid build with a strong neck and pleasant face. Traditionally, Taurus rising marks a life oriented toward material accomplishment.",
    },
    "Gemini": {
        "title": "The Messenger's Gate",
        "text": "With Gemini rising, Mercury rules your chart. Your first impression is one of curiosity, wit, and adaptable energy. The body tends toward a slender, youthful appearance. Traditionally, Gemini rising marks a life of intellectual versatility and social connectivity.",
    },
    "Cancer": {
        "title": "The Moon's Gate",
        "text": "With Cancer rising, the Moon governs your chart. Your first impression is one of warmth and emotional receptivity. The body tends toward a round face and soft features. Traditionally, Cancer rising marks a life deeply shaped by family, heritage, and domestic life.",
    },
    "Leo": {
        "title": "The Sun's Gate",
        "text": "With Leo rising, the Sun is lord of your chart. Your first impression is one of warmth, authority, and natural magnetism. The body tends toward a proud bearing with notable hair. Traditionally, Leo rising marks a life drawn toward leadership and creative expression.",
    },
    "Virgo": {
        "title": "The Scholar's Gate",
        "text": "With Virgo rising, Mercury (in earth) governs your chart. Your first impression is one of intelligence, precision, and quiet competence. The body tends toward a slender, well-groomed appearance. Traditionally, Virgo rising marks a life oriented toward mastery of craft and intellectual service.",
    },
    "Libra": {
        "title": "The Diplomat's Gate",
        "text": "With Libra rising, Venus (in air) governs your chart. Your first impression is one of grace, charm, and aesthetic sensibility. The body tends toward balanced, symmetrical features. Traditionally, Libra rising marks a life shaped by partnerships, negotiations, and the pursuit of justice.",
    },
    "Scorpio": {
        "title": "The Sentinel's Gate",
        "text": "With Scorpio rising, Mars (by night) governs your chart. Your first impression is intense, penetrating, and quietly powerful. The body tends toward a compact, magnetic build with striking eyes. Traditionally, Scorpio rising marks a life of deep transformation and strategic mastery.",
    },
    "Sagittarius": {
        "title": "The Pilgrim's Gate",
        "text": "With Sagittarius rising, Jupiter governs your chart. Your first impression is one of enthusiasm, optimism, and expansive warmth. The body tends toward height with an open, expressive face. Traditionally, Sagittarius rising marks a life of adventure, learning, and philosophical seeking.",
    },
    "Capricorn": {
        "title": "The Chancellor's Gate",
        "text": "With Capricorn rising, Saturn governs your chart. Your first impression is one of seriousness, competence, and quiet authority. The body tends toward a lean build that ages well. Traditionally, Capricorn rising marks a life of ambitious long-range planning and increasing power over time.",
    },
    "Aquarius": {
        "title": "The Innovator's Gate",
        "text": "With Aquarius rising, Saturn (in air) governs your chart. Your first impression is one of originality, intellectual independence, and cool detachment. The body tends toward a distinctive, unconventional appearance. Traditionally, Aquarius rising marks a life oriented toward systemic thinking and community reform.",
    },
    "Pisces": {
        "title": "The Dreamer's Gate",
        "text": "With Pisces rising, Jupiter (by water) governs your chart. Your first impression is one of gentleness, imaginative depth, and spiritual sensitivity. The body tends toward soft features and an ethereal quality. Traditionally, Pisces rising marks a life guided by intuition, compassion, and creative vision.",
    },
}

SECT_DESCRIPTIONS = {
    "DAY": {
        "title": "Diurnal Nativity (Day Chart)",
        "text": "You were born during the day — the Sun was above the horizon at the moment of your first breath. In the traditional system, this makes Jupiter your Greater Benefic (your primary source of opportunity and growth) and Saturn your constructive disciplinarian (the taskmaster who builds through structure). Mars, as the out-of-sect malefic, is the source of your greatest friction and challenge.",
    },
    "NIGHT": {
        "title": "Nocturnal Nativity (Night Chart)",
        "text": "You were born at night — the Sun was below the horizon at the moment of your first breath. In the traditional system, this makes Venus your Greater Benefic (your primary source of grace, connection, and good fortune) and Mars your constructive warrior (the drive that pushes you to achieve). Saturn, as the out-of-sect malefic, represents your heaviest burdens and structural obstacles.",
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _get_sign_from_longitude(lon: float) -> str:
    """Convert ecliptic longitude to sign name."""
    signs = [
        "Aries",
        "Taurus",
        "Gemini",
        "Cancer",
        "Leo",
        "Virgo",
        "Libra",
        "Scorpio",
        "Sagittarius",
        "Capricorn",
        "Aquarius",
        "Pisces",
    ]
    return signs[int(lon / 30.0) % 12]


def _get_degree_in_sign(lon: float) -> str:
    """Get the degree and minute within a sign."""
    degree_in_sign = lon % 30.0
    deg = int(degree_in_sign)
    minutes = int((degree_in_sign - deg) * 60)
    return f"{deg}°{minutes:02d}'"


def _format_planet_position(lon: float) -> str:
    """Return a human-friendly position string like 'Leo 15°23'."""
    sign = _get_sign_from_longitude(lon)
    deg_str = _get_degree_in_sign(lon)
    return f"{sign} {deg_str}"


def _get_dignity_label(score: int) -> str:
    """Convert a dignity score to a consumer-friendly label."""
    if score >= 5:
        return "Domicile (At Home)"
    elif score >= 4:
        return "Exalted (Honored)"
    elif score >= 3:
        return "Strong (Supported)"
    elif score >= 1:
        return "Moderate"
    elif score == 0:
        return "Neutral"
    elif score >= -3:
        return "Challenged"
    elif score >= -4:
        return "In Fall (Dishonored)"
    else:
        return "In Detriment (Struggling)"


def _get_dignity_color_class(score: int) -> str:
    """Get a CSS class for color-coding dignity scores."""
    if score >= 3:
        return "dignity-strong"
    elif score >= 1:
        return "dignity-moderate"
    elif score == 0:
        return "dignity-neutral"
    else:
        return "dignity-weak"


def _planet_display_name(name: str) -> str:
    """Convert internal planet names to display names."""
    return name.replace("_", " ").title()


PLANET_GLYPHS = {
    "Sun": "☉",
    "Moon": "☽",
    "Mercury": "☿",
    "Venus": "♀",
    "Mars": "♂",
    "Jupiter": "♃",
    "Saturn": "♄",
}

SIGN_GLYPHS = {
    "Aries": "♈",
    "Taurus": "♉",
    "Gemini": "♊",
    "Cancer": "♋",
    "Leo": "♌",
    "Virgo": "♍",
    "Libra": "♎",
    "Scorpio": "♏",
    "Sagittarius": "♐",
    "Capricorn": "♑",
    "Aquarius": "♒",
    "Pisces": "♓",
}


# =============================================================================
# MAIN GENERATOR
# =============================================================================


def generate_free_reading(
    name: str,
    date_str: str,
    time_str: str,
    city: str,
    state: str = "",
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Generates an instant, template-based free reading.

    Returns:
        {
            "status": "completed" | "failed",
            "reading_html": str,     # The rendered HTML reading
            "chart_data_summary": dict,  # Key data points for analytics
            "error": str | None,
        }
    """
    try:
        # 1. Generate chart data via the Auditor (same engine as premium)
        result = Auditor.generate_full_nativity(
            date_str=date_str,
            time_str=time_str,
            city=city,
            state=state or "",
            name=name or "Guest",
            latitude=latitude,
            longitude=longitude,
            house_system="W",
        )

        if not result or "error" in result:
            error_msg = (
                result.get("error", "Unknown calculation error")
                if result
                else "Engine returned no data"
            )
            logger.error("Free reading chart generation failed: %s", error_msg)
            return {
                "status": "failed",
                "reading_html": "",
                "chart_data_summary": {},
                "error": str(error_msg),
            }

        technical_data = result["technical_data"]
        analysis = technical_data.get("analysis", {})
        meta = technical_data.get("meta", {})
        astronomy = technical_data.get("astronomy", {})
        planets_forensic = analysis.get("planets_forensic", [])

        # 2. Extract key data points
        chart_meta = meta.get("chart", {})
        sun_data = _find_planet(planets_forensic, "Sun")
        moon_data = _find_planet(planets_forensic, "Moon")
        asc_lon = float(astronomy.get("angles", {}).get("Ascendant", 0))

        sun_sign = (
            _get_sign_from_longitude(float(sun_data.get("longitude", 0)))
            if sun_data
            else "Unknown"
        )
        moon_sign = (
            _get_sign_from_longitude(float(moon_data.get("longitude", 0)))
            if moon_data
            else "Unknown"
        )
        rising_sign = _get_sign_from_longitude(asc_lon)

        sect_data = analysis.get("sect", {})
        sect_type = sect_data.get("type", "DAY")

        profections = analysis.get("enhanced_profections", {})
        temperament = analysis.get("temperament", {})

        # Build dignity scorecard for the septener
        dignity_rows = _build_dignity_scorecard(planets_forensic, sect_type)

        # Build chart wheel data for SVG rendering in the browser
        try:
            planets_for_wheel = {
                p["name"]: {
                    "longitude": float(p["longitude"]),
                    "retrograde": p.get("retrograde", False),
                }
                for p in planets_forensic
                if p.get("name") and p.get("longitude") is not None
            }
            raw_houses = astronomy.get("houses", {})
            houses_for_wheel = {
                str(k): float(v) for k, v in raw_houses.items() if v is not None
            }
            chart_wheel_data = {
                "planets": planets_for_wheel,
                "houses": houses_for_wheel,
                "angles": {"Ascendant": asc_lon},
            }
        except Exception as exc:
            logger.warning("Chart wheel data build failed: %s", repr(exc))
            chart_wheel_data = None

        # 3. Render HTML
        reading_html = _render_free_reading_html(
            name=name or "Guest",
            date_str=chart_meta.get("date", date_str),
            time_str=chart_meta.get("time", time_str),
            city=chart_meta.get("city", city),
            state=chart_meta.get("state", state),
            sun_sign=sun_sign,
            sun_lon=float(sun_data.get("longitude", 0)) if sun_data else 0,
            moon_sign=moon_sign,
            moon_lon=float(moon_data.get("longitude", 0)) if moon_data else 0,
            rising_sign=rising_sign,
            rising_lon=asc_lon,
            sect_type=sect_type,
            dignity_rows=dignity_rows,
            profections=profections,
            temperament=temperament,
            age=meta.get("age", 0),
            chart_wheel_data=chart_wheel_data,
        )

        chart_summary = {
            "sun_sign": sun_sign,
            "moon_sign": moon_sign,
            "rising_sign": rising_sign,
            "sect": sect_type,
            "age": meta.get("age"),
        }

        return {
            "status": "completed",
            "reading_html": reading_html,
            "chart_data_summary": chart_summary,
            "error": None,
        }

    except Exception as e:
        logger.error("Free reading generation failed: %s", repr(e), exc_info=True)
        return {
            "status": "failed",
            "reading_html": "",
            "chart_data_summary": {},
            "error": f"Chart calculation error: {str(e)}",
        }


def _find_planet(planets_forensic: list, name: str) -> Optional[dict]:
    """Find a planet by name in the forensic data list."""
    for p in planets_forensic:
        if p.get("name") == name:
            return p
    return None


def _build_dignity_scorecard(planets_forensic: list, sect_type: str) -> list:
    """Build a consumer-friendly dignity scorecard for the septener."""
    septener = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    rows = []

    for pname in septener:
        pdata = _find_planet(planets_forensic, pname)
        if not pdata:
            continue

        lon = float(pdata.get("longitude", 0))
        sign = _get_sign_from_longitude(lon)
        dignities = pdata.get("dignities", {})
        total_score = dignities.get("total_score", 0)

        # Determine sect role
        sect_role = ""
        if pname == "Sun":
            sect_role = "Luminary of Spirit"
        elif pname == "Moon":
            sect_role = "Luminary of Fortune"
        elif pname == "Jupiter":
            sect_role = "Greater Benefic" if sect_type == "DAY" else "Lesser Benefic"
        elif pname == "Venus":
            sect_role = "Greater Benefic" if sect_type == "NIGHT" else "Lesser Benefic"
        elif pname == "Saturn":
            sect_role = (
                "Ally / Constructive" if sect_type == "DAY" else "Adversary / Blocking"
            )
        elif pname == "Mars":
            sect_role = (
                "Adversary / Volatile" if sect_type == "DAY" else "Ally / Driven"
            )
        elif pname == "Mercury":
            sect_role = "Neutral / Adaptable"

        house = pdata.get("house")
        retrograde = pdata.get("retrograde", False)

        rows.append(
            {
                "name": pname,
                "glyph": PLANET_GLYPHS.get(pname, ""),
                "sign": sign,
                "sign_glyph": SIGN_GLYPHS.get(sign, ""),
                "position": _format_planet_position(lon),
                "dignity_score": total_score,
                "dignity_label": _get_dignity_label(total_score),
                "dignity_class": _get_dignity_color_class(total_score),
                "sect_role": sect_role,
                "house": house,
                "retrograde": retrograde,
            }
        )

    return rows


# =============================================================================
# HTML RENDERER
# =============================================================================


def _render_free_reading_html(
    name: str,
    date_str: str,
    time_str: str,
    city: str,
    state: str,
    sun_sign: str,
    sun_lon: float,
    moon_sign: str,
    moon_lon: float,
    rising_sign: str,
    rising_lon: float,
    sect_type: str,
    dignity_rows: list,
    profections: dict,
    temperament: dict,
    age: int,
    chart_wheel_data: Optional[dict] = None,
) -> str:
    """Renders the complete free reading as an HTML fragment."""

    sun_data = SUN_IN_SIGN.get(sun_sign, {"title": sun_sign, "text": ""})
    moon_data = MOON_IN_SIGN.get(moon_sign, {"title": moon_sign, "text": ""})
    rising_data = RISING_SIGN.get(rising_sign, {"title": rising_sign, "text": ""})
    sect_info = SECT_DESCRIPTIONS.get(sect_type, SECT_DESCRIPTIONS["DAY"])

    # Chart wheel HTML (embedded JSON consumed by reading-app.js → renderChartWheel)
    if chart_wheel_data:
        wheel_json = json.dumps(chart_wheel_data, ensure_ascii=False)
        chart_wheel_html = f"""
        <div class="reading-section chart-wheel-section">
            <h2 class="section-title">✦ Your Natal Chart</h2>
            <div id="chartWheelContainer" class="chart-wheel-container"></div>
            <script type="application/json" id="chartWheelData">{wheel_json}</script>
        </div>
        """
    else:
        chart_wheel_html = ""

    # Big Three header
    sun_glyph = SIGN_GLYPHS.get(sun_sign, "")
    moon_glyph = SIGN_GLYPHS.get(moon_sign, "")
    rising_glyph = SIGN_GLYPHS.get(rising_sign, "")

    # Profections (current year)
    prof_sign = profections.get("annual_sign", "")
    lord_of_year = profections.get("lord_of_year", "")
    loy_natal = profections.get("lord_of_year_natal", {})
    loy_dignity = loy_natal.get("dignity", "")
    loy_house = loy_natal.get("house")

    # Temperament
    temp_primary = temperament.get("primary_temperament", "")
    temp_qualities = temperament.get("qualities_summary", "")

    location = f"{city}, {state}" if state else city

    # Build dignity scorecard HTML
    dignity_html = _render_dignity_table(dignity_rows)

    # Build profections section
    profections_html = ""
    if prof_sign and lord_of_year:
        lord_glyph = PLANET_GLYPHS.get(lord_of_year, "")
        prof_sign_glyph = SIGN_GLYPHS.get(prof_sign, "")

        loy_condition = ""
        if loy_dignity in ("Domicile", "Exaltation"):
            loy_condition = f"<strong>{lord_of_year}</strong> is in <span class='dignity-strong'>{loy_dignity}</span> — a strong year where this planet can deliver on its promises."
        elif loy_dignity in ("Triplicity", "Term", "Face"):
            loy_condition = f"<strong>{lord_of_year}</strong> has moderate dignity ({loy_dignity}) — a year of steady progress, though some effort is required."
        elif loy_dignity == "Peregrine":
            loy_condition = f"<strong>{lord_of_year}</strong> is Peregrine (no essential dignity) — this year's ruler lacks inherent resources. Focus on adaptability and building external support."
        else:
            loy_condition = f"<strong>{lord_of_year}</strong> is in {loy_dignity} — a challenging year that demands patience, resilience, and strategic thinking."

        house_note = f" (natally in House {loy_house})" if loy_house else ""

        profections_html = f"""
        <div class="reading-section">
            <h2 class="section-title">✦ Your Year at Age {age}</h2>
            <div class="section-subtitle">Annual Profection: {prof_sign_glyph} {prof_sign}</div>
            <div class="profection-card">
                <div class="profection-header">
                    <span class="profection-glyph">{lord_glyph}</span>
                    <div>
                        <div class="profection-lord">Lord of the Year: {lord_of_year}{house_note}</div>
                        <div class="profection-sign">Profected to {prof_sign}</div>
                    </div>
                </div>
                <p class="profection-text">{loy_condition}</p>
                <p class="profection-note">Annual profections are a classical timing technique dating to Vettius Valens (2nd century CE). Each year of your life activates a different sign and its ruling planet, coloring the themes and opportunities of that period.</p>
            </div>
        </div>
        """

    return f"""
    <div class="free-reading" id="freeReadingContainer">
        <div class="reading-header">
            <div class="reading-header-meta">
                <span>Born {date_str} at {time_str}</span>
                <span class="meta-sep">·</span>
                <span>{location}</span>
            </div>
            <h1 class="reading-title">Your Natal Chart Overview</h1>
            <p class="reading-subtitle">Calculated using the Swiss Ephemeris · Whole Sign Houses · Traditional Methods</p>
        </div>

        <!-- CHART WHEEL -->
        {chart_wheel_html}

        <!-- THE BIG THREE -->
        <div class="big-three-grid">
            <div class="big-three-card">
                <div class="bt-glyph">{sun_glyph}</div>
                <div class="bt-label">Sun</div>
                <div class="bt-sign">{sun_sign}</div>
                <div class="bt-degree">{_format_planet_position(sun_lon)}</div>
                <div class="bt-title">{sun_data['title']}</div>
            </div>
            <div class="big-three-card">
                <div class="bt-glyph">{moon_glyph}</div>
                <div class="bt-label">Moon</div>
                <div class="bt-sign">{moon_sign}</div>
                <div class="bt-degree">{_format_planet_position(moon_lon)}</div>
                <div class="bt-title">{moon_data['title']}</div>
            </div>
            <div class="big-three-card">
                <div class="bt-glyph">{rising_glyph}</div>
                <div class="bt-label">Rising</div>
                <div class="bt-sign">{rising_sign}</div>
                <div class="bt-degree">{_format_planet_position(rising_lon)}</div>
                <div class="bt-title">{rising_data['title']}</div>
            </div>
        </div>

        <!-- SUN INTERPRETATION -->
        <div class="reading-section">
            <h2 class="section-title">☉ Sun in {sun_sign} — {sun_data['title']}</h2>
            <p class="section-body">{sun_data['text']}</p>
        </div>

        <!-- MOON INTERPRETATION -->
        <div class="reading-section">
            <h2 class="section-title">☽ Moon in {moon_sign} — {moon_data['title']}</h2>
            <p class="section-body">{moon_data['text']}</p>
        </div>

        <!-- RISING SIGN -->
        <div class="reading-section">
            <h2 class="section-title">{rising_glyph} {rising_sign} Rising — {rising_data['title']}</h2>
            <p class="section-body">{rising_data['text']}</p>
        </div>

        <!-- SECT -->
        <div class="reading-section">
            <h2 class="section-title">✦ {sect_info['title']}</h2>
            <p class="section-body">{sect_info['text']}</p>
        </div>

        <!-- DIGNITY SCORECARD -->
        <div class="reading-section">
            <h2 class="section-title">⚖ Planetary Strength Scorecard</h2>
            <p class="section-note">How well-positioned is each planet to act on your behalf? This scorecard uses the traditional essential dignity system — the same method practitioners have used for 2,000 years.</p>
            {dignity_html}
        </div>

        <!-- PROFECTIONS (THIS YEAR) -->
        {profections_html}

        <!-- UPSELL CTA -->
        <div class="free-reading-cta">
            <div class="cta-divider"></div>
            <h2 class="cta-title">Want to go deeper?</h2>
            <p class="cta-subtitle">Your full reading adds the 12-house analysis, all eight Hermetic Lots, Fixed Star conjunctions, Firdaria time-lord periods, and a year-by-year forecast — everything computed from the same chart data above, in a downloadable PDF.</p>
            <div class="cta-value-points" style="display:flex; gap:1.5rem; justify-content:center; flex-wrap:wrap; margin:1.25rem 0; font-size:0.85rem; color:rgba(255,255,255,0.7);">
                <span>📄 PDF you keep forever</span>
                <span>⏱️ Ready in under a minute</span>
                <span>🔒 No account needed</span>
            </div>
            <div class="cta-buttons">
                <button class="btn-cta" onclick="startCheckout('full_reading')" id="checkoutFullBtn" data-default-label="✦ Get Full Reading — $25">
                    ✦ Get Full Reading — $25
                </button>
                <span class="btn-or">— or —</span>
                <button class="btn-cta btn-cta-secondary" onclick="startCheckout('premium_audit')" id="checkoutPremiumBtn" data-default-label="Complete Analysis — $69">
                    Complete Analysis — $69
                </button>
            </div>
            <p class="cta-fine-print">Secure payment via Stripe · No account needed · Instant PDF delivery</p>
        </div>

        <!-- DISCLAIMER -->
        <div class="reading-disclaimer">
            <p>This reading uses pre-1700 traditional astrological methods for historical/entertainment purposes only. It is not medical, financial, or legal advice.</p>
        </div>
    </div>
    """


def _render_dignity_table(rows: list) -> str:
    """Render the dignity scorecard as an HTML table."""
    if not rows:
        return "<p>Planetary data unavailable.</p>"

    tbody = ""
    for r in rows:
        retro_badge = ' <span class="retro-badge">℞</span>' if r["retrograde"] else ""
        house_str = f"House {r['house']}" if r["house"] else "—"

        tbody += f"""
        <tr>
            <td class="planet-cell">
                <span class="planet-glyph">{r['glyph']}</span>
                <span class="planet-name">{r['name']}</span>
            </td>
            <td class="sign-cell">
                <span class="sign-glyph">{r['sign_glyph']}</span>
                {r['sign']}{retro_badge}
            </td>
            <td class="house-cell">{house_str}</td>
            <td class="dignity-cell {r['dignity_class']}">
                <span class="dignity-score">{r['dignity_score']:+d}</span>
                <span class="dignity-label">{r['dignity_label']}</span>
            </td>
            <td class="role-cell">{r['sect_role']}</td>
        </tr>
        """

    return f"""
    <div class="dignity-table-wrapper">
        <table class="dignity-table">
            <thead>
                <tr>
                    <th>Planet</th>
                    <th>Sign</th>
                    <th>House</th>
                    <th>Dignity</th>
                    <th>Sect Role</th>
                </tr>
            </thead>
            <tbody>
                {tbody}
            </tbody>
        </table>
    </div>
    """
