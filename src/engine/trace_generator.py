"""
Trace Generator — Reusable Module
===================================
Generates a complete computation trace for any chart.
Used by both the CLI script and the web API.

Returns a JSON-serializable dict with all computation steps.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any

from .trace import (
    ComputationTrace,
    CAT_ASTRONOMY, CAT_SECT, CAT_DIGNITY, CAT_ACCIDENTAL,
    CAT_ASPECTS, CAT_LOTS, CAT_RECEPTION, CAT_KAKOSIS,
    CAT_VITALITY, CAT_ALMUTEN, CAT_TEMPERAMENT, CAT_PROFECTIONS,
    CAT_ZR, CAT_FIRDARIA, CAT_DECENNIALS, CAT_DIRECTIONS,
    CAT_STARS, CAT_MANSIONS, CAT_MUNDANE, CAT_MEDICAL,
)
from .models import Planet, Chart, Sect, PlanetName, Sign
from .calculator.main import calculate_chart_data
from .dignities import DignityCalculator
from .aspects import AspectEngine
from .lots import calculate_all_lots, LotName
from .reception import ReceptionEngine, ReceptionMode
from .kakosis import KakosisEngine
from .hyleg import HylegAlcocodenEngine
from .temperament import TemperamentEngine
from .advanced_mechanics import AlmutenEngine, DoryphoryEngine, DodecatemoriaEngine
from .prediction import (
    calculate_profection_sign, get_lord_of_year, AdvancedPredictionEngine,
    calculate_firdaria, FIRDARIA_DAY, FIRDARIA_NIGHT,
)
from .decennials import DecennialEngine
from .phasis import PhasisEngine
from .primary_directions import PrimaryDirectionsEngine
from .stars import check_fixed_stars
from .mansions import LunarMansionEngine
from .classical_mechanics import ClassicalMechanicsEngine, calculate_antiscia_points
from .geniture import LordOfGenitureEngine
from .calculations import (
    calculate_solar_status, is_besieged, is_in_via_combusta,
    format_longitude, calculate_prenatal_syzygy_details
)
from .reference_data import (
    DOMICILES, EXALTATIONS, DOROTHEAN_TRIPLICITY, EGYPTIAN_TERMS,
    FACES_ORDER, SIGN_ELEMENTS, MOIETIES
)
from .forensic_engine import Auditor
import swisseph as swe

logger = logging.getLogger(__name__)


def _fmt(lon: float) -> str:
    """Format longitude to sign-degree-minute string."""
    f = format_longitude(lon)
    return f["string"] if isinstance(f, dict) else str(f)


def _sign_of(lon: float) -> Sign:
    return list(Sign)[int(lon / 30) % 12]


def _deg_in_sign(lon: float) -> float:
    return lon % 30.0


def generate_trace(
    date_str: str,
    time_str: str,
    city: str,
    state: str = "",
    name: str = "Native",
) -> Dict[str, Any]:
    """
    Generate a complete computation trace for given birth data.
    
    Returns a JSON-serializable dict with:
        - subject_name, birth_data, total_steps, categories
        - steps: list of step dicts
    
    This runs all the same trace functions as the CLI script but 
    returns the data for API consumption instead of writing files.
    """
    birth_label = f"{date_str} {time_str}, {city}, {state}" if state else f"{date_str} {time_str}, {city}"
    trace = ComputationTrace(subject_name=name, birth_data=birth_label)

    try:
        # 1. Calculate chart
        raw = calculate_chart_data(
            date_str=date_str, time_str=time_str,
            city=city, state=state, house_system="W"
        )

        if "error" in raw:
            return {"error": raw["error"], "steps": [], "total_steps": 0, "categories": []}

        chart = Auditor._rebuild_chart_model(raw)
        
        # Determine age
        utc_time = raw["meta"].get("utc_time", date_str)
        try:
            birth_dt = datetime.fromisoformat(utc_time)
        except (ValueError, TypeError):
            birth_dt = datetime.strptime(date_str, "%Y-%m-%d")
        
        if birth_dt.tzinfo:
            birth_dt = birth_dt.replace(tzinfo=None)
        now = datetime.now()
        age = now.year - birth_dt.year - ((now.month, now.day) < (birth_dt.month, birth_dt.day))

        # 2. Trace all categories
        _trace_astronomy(trace, raw, chart)
        _trace_planetary_hours(trace, chart, raw)
        _trace_sect(trace, chart)
        _trace_dignities(trace, chart)
        _trace_aspects(trace, chart)
        _trace_antiscia(trace, chart)
        _trace_lots(trace, chart)
        _trace_reception(trace, chart)
        _trace_kakosis(trace, chart)
        _trace_vitality(trace, chart)
        _trace_temperament(trace, chart)
        _trace_almuten(trace, chart)
        _trace_profections(trace, chart, age)
        _trace_fixed_stars(trace, chart)
        _trace_firdaria(trace, chart, birth_dt, now)
        _trace_decennials(trace, chart, birth_dt, now)
        _trace_lunar_mansions(trace, chart)
        _trace_primary_directions(trace, chart, raw)
        _trace_doryphory(trace, chart)
        _trace_dodecatemoria(trace, chart)

        return trace.to_dict()

    except Exception as e:
        logger.error(f"Trace generation failed: {e}", exc_info=True)
        return {
            "error": str(e),
            "steps": trace.to_dict().get("steps", []),
            "total_steps": len(trace.steps),
            "categories": trace.categories,
            "subject_name": name,
            "birth_data": birth_label,
        }


# ─── Trace Functions ──────────────────────────────────────────────────────────
# These are extracted from scripts/generate_trace.py for reuse.

def _trace_astronomy(trace: ComputationTrace, raw: dict, chart: Chart):
    """Trace the astronomical foundations."""
    meta = raw.get("meta", {})

    trace.add(
        category=CAT_ASTRONOMY,
        technique="Geocoordinates & Timezone",
        inputs={"city": meta.get("city"), "state": meta.get("state")},
        rule="Convert place name to latitude/longitude and determine local timezone.",
        source="Geopy + TimezoneFinder",
        calculation=f"City lookup → Lat: {meta.get('lat')}, Lon: {meta.get('lon')}, TZ: {meta.get('timezone')}",
        result=f"{meta.get('lat')}°N, {meta.get('lon')}°E, {meta.get('timezone')}",
    )

    trace.add(
        category=CAT_ASTRONOMY,
        technique="Julian Day Number",
        inputs={"date": meta.get("date"), "time": meta.get("time"), "tz": meta.get("timezone")},
        rule="Convert local date/time to Universal Time, then to Julian Day for ephemeris lookup.",
        source="Swiss Ephemeris (pyswisseph)",
        calculation=f"Local {meta.get('date')} {meta.get('time')} {meta.get('timezone')} → UTC → JD = {meta.get('julian_day')}",
        result=meta.get("julian_day"),
    )

    # Each planet position
    planets_data = raw.get("planets", {})
    for pname, pdata in planets_data.items():
        if pname in ("Uranus", "Neptune", "Pluto"):
            continue
        lon = pdata.get("longitude", 0)
        speed = pdata.get("speed", 0)
        retro = "℞ Retrograde" if pdata.get("retrograde") else "Direct"

        trace.add(
            category=CAT_ASTRONOMY,
            technique=f"{pname} Position",
            inputs={"planet": pname, "JD": meta.get("julian_day")},
            rule="Query Swiss Ephemeris for ecliptic longitude, latitude, and daily speed of the planet at the given Julian Day.",
            source="Swiss Ephemeris (Moshier)",
            calculation=f"swe.calc_ut(JD, {pname}) → longitude = {lon:.6f}°",
            result=f"{_fmt(lon)} ({retro}, speed: {speed:.4f}°/day)",
            subsection="Planetary Positions",
        )

    # Ascendant & MC
    angles = raw.get("angles", {})
    asc = angles.get("Ascendant", 0)
    mc = angles.get("MC", 0)

    trace.add(
        category=CAT_ASTRONOMY,
        technique="Ascendant (Rising Degree)",
        inputs={"JD": meta.get("julian_day"), "lat": meta.get("lat"), "lon": meta.get("lon")},
        rule="Calculate the ecliptic degree crossing the eastern horizon at the moment of birth for the given geographic coordinates.",
        source="Swiss Ephemeris swe.houses()",
        calculation=f"swe.houses(JD, lat={meta.get('lat')}, lon={meta.get('lon')}) → Ascendant = {asc:.6f}°",
        result=f"Ascendant: {_fmt(asc)}",
        subsection="Angles",
    )

    trace.add(
        category=CAT_ASTRONOMY,
        technique="Midheaven (MC)",
        inputs={"JD": meta.get("julian_day"), "lat": meta.get("lat")},
        rule="Calculate the ecliptic degree at the upper meridian (culmination point).",
        source="Swiss Ephemeris swe.houses()",
        calculation=f"MC = {mc:.6f}°",
        result=f"MC: {_fmt(mc)}",
        subsection="Angles",
    )

    # Prenatal Syzygy
    try:
        syz = calculate_prenatal_syzygy_details(meta.get("julian_day", 0))
        trace.add(
            category=CAT_ASTRONOMY,
            technique="Prenatal Syzygy (SAN)",
            inputs={"birth_JD": meta.get("julian_day")},
            rule="Find the New Moon or Full Moon immediately preceding birth. This is the Prenatal Syzygy, used for Hyleg determination and sect refinement.",
            source="Ptolemy, Tetrabiblos III.2",
            calculation=f"Search backward from JD for last Sun-Moon conjunction (New) or opposition (Full). Found: {syz.get('type')} at {_fmt(syz.get('longitude', 0))}",
            result=f"{syz.get('type')} at {_fmt(syz.get('longitude', 0))}",
        )
    except Exception:
        pass


def _trace_planetary_hours(trace: ComputationTrace, chart: Chart, raw: dict):
    """Trace planetary hour calculation."""
    meta = raw.get("meta", {})
    lat = meta.get("geo_lat", 0)
    lon = meta.get("geo_lon", 0)
    utc_str = meta.get("utc_time", "")

    try:
        birth_dt = datetime.fromisoformat(utc_str.replace("Z", "+00:00")) if utc_str else None
        if birth_dt and birth_dt.tzinfo:
            birth_dt = birth_dt.replace(tzinfo=None)

        if not birth_dt:
            return

        asc_sign = _sign_of(chart.ascendant)
        asc_lord = DOMICILES.get(asc_sign)
        asc_lord_str = asc_lord.value if asc_lord else None

        hour_info = ClassicalMechanicsEngine.get_planetary_hours(
            birth_dt, lat, lon, asc_sign, asc_lord_str
        )

        if hour_info:
            trace.add(
                category=CAT_ASTRONOMY,
                technique="Planetary Hour at Birth",
                inputs={"datetime_utc": str(birth_dt), "latitude": lat, "longitude": lon},
                rule="Calculate sunrise/sunset using Swiss Ephemeris. Divide the daytime into 12 unequal 'temporal hours', and similarly the nighttime. Each hour is ruled by a planet in Chaldean descending order starting from the Day Lord.",
                source="Lilly, Christian Astrology pp.31-32; Abu Ma'shar",
                calculation=f"Day: {hour_info.day_of_week}, Day Lord: {hour_info.day_lord}. {'Daytime' if hour_info.is_daytime else 'Nighttime'} birth, Hour #{hour_info.hour_number} → Hour Lord: {hour_info.hour_lord}. ASC Lord: {asc_lord_str or '?'}.",
                result=f"Hour Lord: {hour_info.hour_lord} ({hour_info.radicality})",
                subsection="Planetary Hours",
            )
    except Exception:
        pass


def _trace_sect(trace: ComputationTrace, chart: Chart):
    """Trace sect determination."""
    sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
    trace.add(
        category=CAT_SECT,
        technique="Day/Night Sect",
        inputs={"sun_altitude": f"{chart.sun_altitude:.2f}°"},
        rule="If the Sun is above the horizon (altitude > 0°), the chart is a DAY chart. If below, it is a NIGHT chart. This is the single most important distinction in traditional astrology — it determines which planets are 'in sect' and which are 'contrary to sect.'",
        source="Ptolemy, Tetrabiblos III.3; Dorotheus, Carmen Astrologicum I.1",
        calculation=f"Sun altitude = {chart.sun_altitude:.2f}°. {'Above' if chart.sun_altitude > 0 else 'Below'} the horizon → {'DAY' if sect == Sect.DAY else 'NIGHT'} chart.",
        result=f"{'DAY' if sect == Sect.DAY else 'NIGHT'} Chart",
        notes=f"In a {'DAY' if sect == Sect.DAY else 'NIGHT'} chart: {'Sun, Jupiter, Saturn' if sect == Sect.DAY else 'Moon, Venus, Mars'} are the sect planets (more constructive). {'Mars' if sect == Sect.DAY else 'Saturn'} is the out-of-sect malefic (most destructive planet in this chart).",
    )


def _trace_dignities(trace: ComputationTrace, chart: Chart):
    """Trace essential dignity calculations for each planet."""
    sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
    signs = list(Sign)

    for planet in chart.planets:
        if planet.name in (PlanetName.URANUS, PlanetName.NEPTUNE, PlanetName.PLUTO,
                          PlanetName.NORTH_NODE, PlanetName.SOUTH_NODE):
            continue

        sign = _sign_of(planet.longitude)
        deg = _deg_in_sign(planet.longitude)
        element = SIGN_ELEMENTS.get(sign, "Unknown")

        dig = DignityCalculator.calculate_planet_dignity(planet.name, planet.longitude, sect)
        rulers = DignityCalculator.get_essential_rulers(planet.longitude, sect)
        score_bd = dig.get("score_breakdown", {})

        # Domicile
        dom_ruler = DOMICILES.get(sign)
        dom_score = score_bd.get("domicile", 0)
        is_dom = dom_ruler == planet.name
        trace.add(
            category=CAT_DIGNITY,
            technique="Domicile",
            inputs={"planet": planet.name.value, "sign": sign.value, "degree": f"{deg:.2f}°"},
            rule=f"The domicile ruler of {sign.value} is {dom_ruler.value if dom_ruler else 'Unknown'}. If {planet.name.value} IS the domicile ruler of its own sign, it receives +5 dignity. If it is in the OPPOSITE sign of the one it rules, it is in Detriment (-5).",
            source="Ptolemy, Tetrabiblos I.17",
            calculation=f"{planet.name.value} at {_fmt(planet.longitude)} → Sign: {sign.value} → Ruler of {sign.value}: {dom_ruler.value if dom_ruler else '?'}. {'MATCH → +5 (Domicile)' if is_dom else f'No match → {dom_score} points'}",
            result=f"{'Domicile (+5)' if is_dom else f'{dom_score}'}",
            subsection=planet.name.value,
        )

        # Exaltation
        exalt_ruler = EXALTATIONS.get(sign)
        exalt_score = score_bd.get("exaltation", 0)
        is_exalt = exalt_ruler == planet.name
        trace.add(
            category=CAT_DIGNITY,
            technique="Exaltation",
            inputs={"planet": planet.name.value, "sign": sign.value},
            rule=f"The exaltation ruler of {sign.value} is {exalt_ruler.value if exalt_ruler else 'None'}. If {planet.name.value} is exalted here, it receives +4 dignity. If in the opposite sign of its exaltation, it is in Fall (-4).",
            source="Ptolemy, Tetrabiblos I.19",
            calculation=f"Exaltation ruler of {sign.value}: {exalt_ruler.value if exalt_ruler else 'None'}. {'MATCH → +4 (Exaltation)' if is_exalt else f'{exalt_score} points'}",
            result=f"{'Exaltation (+4)' if is_exalt else f'{exalt_score}'}",
            subsection=planet.name.value,
        )

        # Triplicity
        trip_ruler = rulers.get("triplicity")
        trip_score = score_bd.get("triplicity", 0)
        sect_label = "Day" if sect == Sect.DAY else "Night"
        trip_rulers_raw = DOROTHEAN_TRIPLICITY.get(element, ("?", "?", "?"))
        trace.add(
            category=CAT_DIGNITY,
            technique="Triplicity (Dorothean)",
            inputs={"planet": planet.name.value, "element": element, "sect": sect_label},
            rule=f"{element} triplicity rulers (Dorothean): Day={trip_rulers_raw[0].value if hasattr(trip_rulers_raw[0], 'value') else trip_rulers_raw[0]}, Night={trip_rulers_raw[1].value if hasattr(trip_rulers_raw[1], 'value') else trip_rulers_raw[1]}, Participant={trip_rulers_raw[2].value if hasattr(trip_rulers_raw[2], 'value') else trip_rulers_raw[2]}. If {planet.name.value} is the active triplicity ruler for this sect, it receives +3.",
            source="Dorotheus, Carmen Astrologicum I.1",
            calculation=f"Element: {element}, Sect: {sect_label} → Active ruler: {trip_ruler.value if trip_ruler else '?'}. {planet.name.value} {'= MATCH → +3' if trip_score > 0 else '≠ ruler → 0'}",
            result=f"{trip_score}",
            subsection=planet.name.value,
        )

        # Term / Bounds
        term_ruler = rulers.get("term")
        term_score = score_bd.get("term", 0)
        terms_list = EGYPTIAN_TERMS.get(sign, [])
        terms_str = ", ".join([f"{t[0].value if hasattr(t[0], 'value') else t[0]}(<{t[1]}°)" for t in terms_list])
        trace.add(
            category=CAT_DIGNITY,
            technique="Term / Bounds (Egyptian)",
            inputs={"planet": planet.name.value, "sign": sign.value, "degree": f"{deg:.2f}°"},
            rule=f"Egyptian Terms of {sign.value}: [{terms_str}]. The planet ruling the degree-range that contains {deg:.1f}° is the Term ruler. If {planet.name.value} is the Term ruler, +2.",
            source="Valens, Anthology; Egyptian tradition",
            calculation=f"Degree {deg:.2f}° in {sign.value} → Term ruler: {term_ruler.value if term_ruler else '?'}. {planet.name.value} {'= MATCH → +2' if term_score > 0 else '≠ ruler → 0'}",
            result=f"{term_score}",
            subsection=planet.name.value,
        )

        # Face / Decan
        face_score = score_bd.get("face", 0)
        face_idx = min(int(deg / 10), 2)
        sign_idx = signs.index(sign)
        global_face_idx = (sign_idx * 3 + face_idx) % len(FACES_ORDER)
        face_ruler = FACES_ORDER[global_face_idx]
        trace.add(
            category=CAT_DIGNITY,
            technique="Face / Decan (Chaldean)",
            inputs={"planet": planet.name.value, "sign": sign.value, "degree": f"{deg:.2f}°", "decan": face_idx + 1},
            rule=f"Chaldean decan order cycles through Saturn→Jupiter→Mars→Sun→Venus→Mercury→Moon. Decan {face_idx+1} of {sign.value} (degrees {face_idx*10}–{(face_idx+1)*10}°) is ruled by {face_ruler.value if hasattr(face_ruler, 'value') else face_ruler}. If {planet.name.value} is the Face ruler, +1.",
            source="Chaldean order; Firmicus Maternus",
            calculation=f"Sign #{sign_idx+1} × 3 decans + decan {face_idx+1} → global index {global_face_idx} → ruler: {face_ruler.value if hasattr(face_ruler, 'value') else face_ruler}. {face_score} points.",
            result=f"{face_score}",
            subsection=planet.name.value,
        )

        # Total Score
        total = dig.get("total_score", 0)
        trace.add(
            category=CAT_DIGNITY,
            technique="Total Essential Dignity Score",
            inputs={"planet": planet.name.value},
            rule="Sum: Domicile(+5) + Exaltation(+4) + Triplicity(+3) + Term(+2) + Face(+1) + Detriment(-5) + Fall(-4). If zero positive dignities, Peregrine (-5).",
            source="Lilly, Christian Astrology p.104",
            calculation=f"Dom({dom_score}) + Exalt({exalt_score}) + Trip({trip_score}) + Term({term_score}) + Face({face_score}) + Detr({score_bd.get('detriment', 0)}) + Fall({score_bd.get('fall', 0)}) + Peregr({score_bd.get('peregrine', 0)}) = {total}",
            result=f"Score: {total}",
            subsection=planet.name.value,
            notes="Positive = well-dignified (can act effectively). Negative = debilitated (frustrated, weakened). Zero with no dignity = Peregrine (wanderer, without resources).",
        )


def _trace_aspects(trace: ComputationTrace, chart: Chart):
    """Trace aspect calculations."""
    aspects = AspectEngine.calculate_aspects(chart)
    core_planets = {PlanetName.SUN, PlanetName.MOON, PlanetName.MERCURY,
                   PlanetName.VENUS, PlanetName.MARS, PlanetName.JUPITER, PlanetName.SATURN}

    for asp in aspects:
        if asp.planet_a not in core_planets or asp.planet_b not in core_planets:
            continue

        p_a = next((p for p in chart.planets if p.name == asp.planet_a), None)
        p_b = next((p for p in chart.planets if p.name == asp.planet_b), None)
        if not p_a or not p_b:
            continue

        moiety_a = MOIETIES.get(asp.planet_a, 3.0)
        moiety_b = MOIETIES.get(asp.planet_b, 3.0)
        max_orb = moiety_a + moiety_b

        apply_str = "Applying (strengthening)" if asp.is_applying else "Separating (past peak)"

        exact_angles = {"Conjunction": 0, "Sextile": 60, "Square": 90, "Trine": 120, "Opposition": 180}
        exact_deg = exact_angles.get(asp.type.value, 0)

        trace.add(
            category=CAT_ASPECTS,
            technique=f"{asp.planet_a.value} {asp.type.value} {asp.planet_b.value}",
            inputs={
                "planet_a": f"{asp.planet_a.value} at {_fmt(p_a.longitude)}",
                "planet_b": f"{asp.planet_b.value} at {_fmt(p_b.longitude)}",
                "speed_a": f"{p_a.speed:.4f}°/day",
                "speed_b": f"{p_b.speed:.4f}°/day",
            },
            rule=f"Ptolemaic aspects: Conjunction (0°), Sextile (60°), Square (90°), Trine (120°), Opposition (180°). Maximum orb = sum of moieties: {moiety_a} + {moiety_b} = {max_orb}°.",
            source="Ptolemy, Tetrabiblos I.13; Lilly, CA p.107",
            calculation=f"Angular separation: |{p_a.longitude:.2f} - {p_b.longitude:.2f}| → {asp.type.value} (exact at {exact_deg}°). Actual orb = {asp.orb:.2f}°. Within max orb {max_orb}°? Yes. {apply_str}.",
            result=f"{asp.type.value} with {asp.orb:.2f}° orb, {apply_str}",
        )


def _trace_antiscia(trace: ComputationTrace, chart: Chart):
    """Trace Antiscia (shadow points)."""
    shadow_aspects = ClassicalMechanicsEngine.check_shadow_aspects(chart.planets)

    if not shadow_aspects:
        trace.add(
            category=CAT_ASPECTS,
            technique="Antiscia Survey",
            inputs={"method": "Solstice Reflection"},
            rule="Antiscia: Reflect each planet's longitude across the Cancer/Capricorn axis. If another planet falls on the shadow point within moiety-orb, a hidden connection exists.",
            source="Ptolemy, Tetrabiblos; Lilly, Christian Astrology, pp.91-92",
            calculation="Checked all 21 planet pairs. No antiscia or contra-antiscia aspects found within orb.",
            result="No shadow aspects",
            subsection="Antiscia (Shadow Points)",
        )
        return

    for sa in shadow_aspects:
        quality = sa.get("quality", "?")
        trace.add(
            category=CAT_ASPECTS,
            technique=f"{sa.get('type', 'Antiscia')}: {sa.get('planet_1', '?')} / {sa.get('planet_2', '?')}",
            inputs={
                "planet_1": sa.get("planet_1", "?"),
                "planet_2": sa.get("planet_2", "?"),
                "orb": f"{sa.get('orb', '?')} deg",
                "partile": "Yes" if sa.get("partile") else "No",
            },
            rule=f"The {sa.get('type', 'Antiscia')} of {sa.get('planet_1', '?')} falls on {sa.get('planet_2', '?')}.",
            source="Ptolemy, Tetrabiblos; Lilly, Christian Astrology, pp.91-92",
            calculation=f"Orb: {sa.get('orb', '?')} deg. Partile (within 1 deg): {'Yes' if sa.get('partile') else 'No'}.",
            result=f"{quality}: {sa.get('planet_1', '?')} / {sa.get('planet_2', '?')} ({sa.get('type', '?')})",
            subsection="Antiscia (Shadow Points)",
        )


def _trace_lots(trace: ComputationTrace, chart: Chart):
    """Trace lot calculations."""
    sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
    is_day = sect == Sect.DAY
    all_lots = calculate_all_lots(chart, sect)

    sun = next(p for p in chart.planets if p.name == PlanetName.SUN)
    moon = next(p for p in chart.planets if p.name == PlanetName.MOON)

    # Lot of Fortune
    fort = all_lots.get(LotName.FORTUNE.value, 0)
    if is_day:
        formula = "Asc + Moon - Sun"
        calc = f"{chart.ascendant:.2f} + {moon.longitude:.2f} - {sun.longitude:.2f} = {(chart.ascendant + moon.longitude - sun.longitude) % 360:.2f}"
    else:
        formula = "Asc + Sun - Moon"
        calc = f"{chart.ascendant:.2f} + {sun.longitude:.2f} - {moon.longitude:.2f} = {(chart.ascendant + sun.longitude - moon.longitude) % 360:.2f}"

    trace.add(
        category=CAT_LOTS,
        technique="Lot of Fortune (Tyche)",
        inputs={"Asc": _fmt(chart.ascendant), "Sun": _fmt(sun.longitude), "Moon": _fmt(moon.longitude), "sect": "Day" if is_day else "Night"},
        rule=f"Day chart: Asc + Moon − Sun. Night chart: Asc + Sun − Moon. The Lot of Fortune represents the body, health, luck, and material circumstances.",
        source="Paulus Alexandrinus, Introduction; Valens, Anthology II",
        calculation=f"{formula} = {calc} (mod 360) = {fort:.2f}°",
        result=f"{_fmt(fort)}",
    )

    # Lot of Spirit
    spir = all_lots.get(LotName.SPIRIT.value, 0)
    if is_day:
        formula_s = "Asc + Sun - Moon"
        calc_s = f"{chart.ascendant:.2f} + {sun.longitude:.2f} - {moon.longitude:.2f} = {(chart.ascendant + sun.longitude - moon.longitude) % 360:.2f}"
    else:
        formula_s = "Asc + Moon - Sun"
        calc_s = f"{chart.ascendant:.2f} + {moon.longitude:.2f} - {sun.longitude:.2f} = {(chart.ascendant + moon.longitude - sun.longitude) % 360:.2f}"

    trace.add(
        category=CAT_LOTS,
        technique="Lot of Spirit (Daimon)",
        inputs={"Asc": _fmt(chart.ascendant), "Sun": _fmt(sun.longitude), "Moon": _fmt(moon.longitude)},
        rule=f"Day chart: Asc + Sun − Moon. Night chart: Asc + Moon − Sun. The Lot of Spirit represents the mind, intellect, career, and will.",
        source="Paulus Alexandrinus, Introduction; Valens, Anthology IV",
        calculation=f"{formula_s} = {calc_s} (mod 360) = {spir:.2f}°",
        result=f"{_fmt(spir)}",
    )

    # Remaining lots
    lot_names_map = {
        LotName.EROS.value: ("Eros (Love)", "Venus/Spirit", "Desire, love, attraction"),
        LotName.NECESSITY.value: ("Necessity (Ananke)", "Mercury/Fortune", "Constraints, obligations, enemies"),
        LotName.COURAGE.value: ("Courage (Tolma)", "Mars/Fortune", "Boldness, daring, conflict"),
        LotName.VICTORY.value: ("Victory (Nike)", "Jupiter/Spirit", "Success, triumph, faith"),
        LotName.NEMESIS.value: ("Nemesis", "Saturn/Fortune", "Saturn dealings, karmic debts"),
    }

    for lot_key, (lot_label, formula_desc, meaning) in lot_names_map.items():
        lon = all_lots.get(lot_key, 0)
        trace.add(
            category=CAT_LOTS,
            technique=lot_label,
            inputs={"formula_type": formula_desc, "sect": "Day" if is_day else "Night"},
            rule=f"Hermetic Lot: {lot_label}. {meaning}. Formula varies by sect (sect-reversed).",
            source="Paulus Alexandrinus, Introduction",
            calculation=f"Result = {lon:.2f}°",
            result=f"{_fmt(lon)}",
        )


def _trace_reception(trace: ComputationTrace, chart: Chart):
    """Trace reception and mutual reception."""
    mutuals = ReceptionEngine.calculate_mutual_receptions(chart, ReceptionMode.STANDARD_LILLY)

    if mutuals:
        for mr in mutuals:
            pa = mr.planet_a.value if hasattr(mr.planet_a, 'value') else str(mr.planet_a)
            pb = mr.planet_b.value if hasattr(mr.planet_b, 'value') else str(mr.planet_b)

            trace.add(
                category=CAT_RECEPTION,
                technique=f"Mutual Reception: {pa} <-> {pb}",
                inputs={"planet_a": pa, "planet_b": pb, "type": mr.type, "strength": mr.strength_score},
                rule=f"Mutual Reception: {pa} is in {pb}'s dignity AND {pb} is in {pa}'s dignity. Type: {mr.type}.",
                source="Bonatti, Liber Astronomiae; Lilly, Christian Astrology",
                calculation=f"{pa} reception of {pb}: {', '.join(mr.reception_a_in_b.dignities)} (score {mr.reception_a_in_b.score}). {pb} reception of {pa}: {', '.join(mr.reception_b_in_a.dignities)} (score {mr.reception_b_in_a.score}). Combined: {mr.strength_score}.",
                result=f"{mr.type} Mutual Reception (strength: {mr.strength_score})",
            )
    else:
        trace.add(
            category=CAT_RECEPTION,
            technique="Mutual Reception Survey",
            inputs={"mode": "Standard (Lilly)"},
            rule="Check all 21 planet-pairs for mutual reception. None found.",
            source="Bonatti, Liber Astronomiae; Lilly, Christian Astrology",
            calculation="All 21 pairs checked — no mutual reception detected.",
            result="No mutual receptions",
        )


def _trace_kakosis(trace: ComputationTrace, chart: Chart):
    """Trace maltreatment conditions."""
    core_planets = [p for p in chart.planets if p.name in (
        PlanetName.SUN, PlanetName.MOON, PlanetName.MERCURY,
        PlanetName.VENUS, PlanetName.MARS, PlanetName.JUPITER, PlanetName.SATURN
    )]

    for planet in core_planets:
        conditions = KakosisEngine.check_maltreatments(planet, chart)
        if conditions:
            for cond in conditions:
                trace.add(
                    category=CAT_KAKOSIS,
                    technique=f"{cond.type}",
                    inputs={"victim": planet.name.value, "malefic": cond.malefic.value},
                    rule=f"Kakosis condition: {cond.type}. {planet.name.value} is maltreated by {cond.malefic.value}.",
                    source="Valens, Anthology IV.7; Hephaistio, Apotelesmatics",
                    calculation=cond.description,
                    result=f"Severity: {cond.severity}/10",
                    subsection=planet.name.value,
                )
        else:
            trace.add(
                category=CAT_KAKOSIS,
                technique="No Maltreatment",
                inputs={"planet": planet.name.value},
                rule="Check all 7 conditions of maltreatment. If none apply, the planet is free from kakosis.",
                source="Valens, Anthology IV.7",
                calculation=f"All 7 checks passed for {planet.name.value} — no maltreatment detected.",
                result="✅ Clear",
                subsection=planet.name.value,
            )


def _trace_vitality(trace: ComputationTrace, chart: Chart):
    """Trace Hyleg, Alcocoden, and Anareta."""
    sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT

    hyleg = HylegAlcocodenEngine.determine_hyleg(chart)
    trace.add(
        category=CAT_VITALITY,
        technique="Hyleg (Giver of Life)",
        inputs={"sect": "Day" if sect == Sect.DAY else "Night"},
        rule=f"{'Day chart' if sect == Sect.DAY else 'Night chart'}: Check {'Sun → Moon → Lot of Fortune → Ascendant' if sect == Sect.DAY else 'Moon → Sun → Lot of Fortune → Ascendant'} in priority order. The first luminary in a hylegical house that qualifies becomes the Hyleg.",
        source="Bonatti, Liber Astronomiae VIII; Lilly, CA pp.537-541",
        calculation=f"Checking candidates in order... Winner: {hyleg.get('name', 'None')} at {_fmt(hyleg.get('longitude', 0))}.",
        result=f"Hyleg: {hyleg.get('name', 'Not found')}",
    )

    if hyleg.get("name"):
        alcocoden = HylegAlcocodenEngine.determine_alcocoden(hyleg, chart)
        if alcocoden:
            alco_name = alcocoden.get("name", "Unknown")
            if hasattr(alco_name, "value"):
                alco_name = alco_name.value
            trace.add(
                category=CAT_VITALITY,
                technique="Alcocoden (Giver of Years)",
                inputs={"hyleg": hyleg.get("name"), "hyleg_longitude": _fmt(hyleg.get("longitude", 0))},
                rule="Find the essential ruler of the Hyleg degree with the highest Bonatti-score that aspects the Hyleg. That planet is the Alcocoden — it grants its Minor, Mean, or Major years as the baseline vitality.",
                source="Bonatti, Liber Astronomiae VIII",
                calculation=f"Hyleg at {_fmt(hyleg.get('longitude', 0))} → essential rulers scored → winner: {alco_name} (score: {alcocoden.get('score', 0)}) via {alcocoden.get('aspect', 'Unknown')}",
                result=f"Alcocoden: {alco_name}",
            )

            lifespan = HylegAlcocodenEngine.calculate_lifespan(hyleg, alcocoden, chart)
            trace.add(
                category=CAT_VITALITY,
                technique="Vitality Calculation",
                inputs={"alcocoden": alco_name},
                rule="Start with the Alcocoden's base years. Add years from benefic aspects, subtract from malefic aspects.",
                source="Bonatti, Liber Astronomiae VIII; Lilly, CA pp.537-541",
                calculation=" → ".join(lifespan.get("breakdown", [])),
                result=f"Total: {lifespan.get('total_years', 0):.1f} years — Rating: {lifespan.get('vitality_rating', 'Unknown')}",
                notes="Historical Use Only. This section is not medical advice, diagnosis, or treatment.",
            )

        anareta = HylegAlcocodenEngine.determine_anareta(hyleg, chart)
        trace.add(
            category=CAT_VITALITY,
            technique="Anareta (Destroyer of Life)",
            inputs={"hyleg": hyleg.get("name")},
            rule="The Anareta is the planet making the tightest hard aspect to the Hyleg degree.",
            source="Bonatti, Liber Astronomiae VIII; Lilly, CA pp.537-541",
            calculation=anareta.get("reason", "No suitable candidate found."),
            result=f"Anareta: {anareta.get('name', 'None')}",
            notes="Historical Use Only. This section is not medical advice, diagnosis, or treatment.",
        )


def _trace_temperament(trace: ComputationTrace, chart: Chart):
    """Trace temperament calculation."""
    temp = TemperamentEngine.calculate_temperament(chart)
    scores = temp.get("scores", {})
    net = temp.get("net_balance", {})
    breakdown_text = "\n".join(temp.get("breakdown", []))

    trace.add(
        category=CAT_TEMPERAMENT,
        technique="Lilly's Humoral Temperament",
        inputs={"method": "Christian Astrology pp.57-83"},
        rule="Sum Hot/Cold/Moist/Dry points from: Ascendant sign element, Ascendant ruler's sign, Moon sign, Moon phase, Season, Planets aspecting Moon, Inherent planetary natures. Net balance determines temperament.",
        source="Lilly, Christian Astrology, pp.57-83 (1647)",
        calculation=f"Hot={scores.get('Hot',0)}, Cold={scores.get('Cold',0)}, Moist={scores.get('Moist',0)}, Dry={scores.get('Dry',0)}. Net: Hot-Cold={net.get('Hot_vs_Cold', 0)}, Moist-Dry={net.get('Moist_vs_Dry', 0)}",
        result=f"{temp.get('primary_temperament', 'Unknown')}",
        notes=breakdown_text,
    )


def _trace_almuten(trace: ComputationTrace, chart: Chart):
    """Trace Almuten Figuris."""
    almuten_result = AlmutenEngine.calculate_almuten(chart)
    gen_result = LordOfGenitureEngine.calculate(chart)

    almuten_winner = getattr(almuten_result, 'winner', None)
    if almuten_winner is None and isinstance(almuten_result, dict):
        almuten_winner = almuten_result.get('winner', 'Unknown')
    if hasattr(almuten_winner, 'value'):
        almuten_winner = almuten_winner.value

    gen_winner = getattr(gen_result, 'winner', None)
    if gen_winner is None and isinstance(gen_result, dict):
        gen_winner = gen_result.get('winner', 'Unknown')
    if hasattr(gen_winner, 'value'):
        gen_winner = gen_winner.value

    trace.add(
        category=CAT_ALMUTEN,
        technique="Almuten Figuris (Ibn Ezra)",
        inputs={"method": "Ibn Ezra 5-point scoring at 5 hylegical places"},
        rule="Score each planet's essential dignities at the 5 hylegical degrees (Sun, Moon, Asc, PoF, SAN). The planet with the highest cumulative score is the Almuten Figuris — the 'Soul Guardian' of the nativity.",
        source="Ibn Ezra, The Beginning of Wisdom; Bonatti",
        calculation=f"Winner: {almuten_winner} (top scorer across 5 places)",
        result=f"Almuten Figuris: {almuten_winner}",
    )

    trace.add(
        category=CAT_ALMUTEN,
        technique="Lord of Geniture (Lilly)",
        inputs={"method": "Net fortitudes & debilities (Ptolemaic terms/triplicity)"},
        rule="Score each planet on essential dignity + accidental dignity. The highest net score is the Lord of the Geniture.",
        source="Lilly, Christian Astrology (1647)",
        calculation=f"Winner: {gen_winner}",
        result=f"Lord of Geniture: {gen_winner}",
    )


def _trace_profections(trace: ComputationTrace, chart: Chart, age: int):
    """Trace annual profections."""
    signs = list(Sign)
    asc_sign_idx = int(chart.ascendant / 30) % 12
    annual_idx = (asc_sign_idx + age) % 12
    annual_sign = signs[annual_idx]
    loy = get_lord_of_year(annual_sign)

    trace.add(
        category=CAT_PROFECTIONS,
        technique="Annual Profection",
        inputs={"age": age, "ascendant_sign": signs[asc_sign_idx].value},
        rule=f"Starting from the Ascendant sign ({signs[asc_sign_idx].value}), advance one sign per year of life. At age {age}, the profection has advanced {age} signs from the Ascendant.",
        source="Valens, Anthology IV; Abu Ma'shar; Bonatti",
        calculation=f"Asc sign index: {asc_sign_idx} ({signs[asc_sign_idx].value}) + age {age} = index {annual_idx} (mod 12) = {annual_sign.value}",
        result=f"Annual Sign: {annual_sign.value}. Lord of the Year: {loy.value}",
        notes=f"The Lord of the Year ({loy.value}) is activated — transits to/from this planet and planets in its natal sign are the primary timing triggers.",
    )


def _trace_fixed_stars(trace: ComputationTrace, chart: Chart):
    """Trace fixed star contacts."""
    contacts = check_fixed_stars(chart)

    if not contacts:
        trace.add(
            category=CAT_STARS,
            technique="Fixed Star Survey",
            inputs={"stars_checked": "21 Royal + Behenian stars"},
            rule="Check all 21 cataloged fixed stars for ecliptic conjunction and paran contacts.",
            source="Ptolemy, Tetrabiblos I.9; Robson, Fixed Stars & Constellations",
            calculation="No contacts found within orb for any star-planet pair.",
            result="No fixed star contacts",
        )
        return

    from .stars import STARS as STAR_CATALOG

    for contact in contacts:
        star_data = next((s for s in STAR_CATALOG if s.name == contact.star_name), None)

        if contact.contact_type == "CONJUNCTION":
            trace.add(
                category=CAT_STARS,
                technique=f"{contact.star_name} conjunct {contact.planet_name}",
                inputs={
                    "star": contact.star_name,
                    "planet": contact.planet_name,
                    "nature": star_data.nature if star_data else "Unknown",
                    "magnitude": star_data.magnitude if star_data else "?",
                },
                rule=f"A fixed star conjunct a planet within orb infuses the planet with the star's nature.",
                source="Ptolemy, Tetrabiblos I.9; Anonymous of 379",
                calculation=contact.message,
                result=f"Glory: {star_data.glory if star_data else '?'}. Nemesis: {star_data.nemesis if star_data else '?'}",
                subsection="Ecliptic Conjunctions",
            )
        elif contact.contact_type == "PARAN":
            trace.add(
                category=CAT_STARS,
                technique=f"Paran: {contact.star_name} / {contact.planet_name}",
                inputs={
                    "star": contact.star_name,
                    "planet": contact.planet_name,
                    "angle": contact.angle or "?",
                },
                rule="A Paran occurs when a star and planet are simultaneously on angular points (ASC, MC, DSC, IC).",
                source="Ptolemy, Phaseis; Brady, Fixed Stars",
                calculation=contact.message,
                result=f"Paran at {contact.angle}: {contact.star_name} + {contact.planet_name}",
                subsection="Parans (Co-Rising/Setting)",
            )
        elif contact.contact_type in ("ANGULAR_PRESENCE", "AXIS_ALERT"):
            trace.add(
                category=CAT_STARS,
                technique=f"{contact.star_name} on {contact.planet_name}",
                inputs={"star": contact.star_name, "angle": contact.planet_name},
                rule="A fixed star directly on an angle indicates eminence or notoriety.",
                source="Ptolemy, Tetrabiblos I.9; Robson",
                calculation=contact.message,
                result=f"Star on angle: {contact.star_name} on {contact.planet_name}",
                subsection="Angular Stars",
            )


def _trace_firdaria(trace: ComputationTrace, chart: Chart, birth_date, target_date):
    """Trace Firdaria periods."""
    sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
    fird = calculate_firdaria(sect, birth_date, target_date)

    if "error" in fird:
        trace.add(
            category=CAT_FIRDARIA,
            technique="Firdaria",
            inputs={"sect": "Day" if sect == Sect.DAY else "Night"},
            rule="Firdaria divides life into planetary periods in sect-determined order.",
            source="Abu Ma'shar, On the Revolutions of the Years",
            calculation=f"Error: {fird['error']}",
            result="Could not calculate",
        )
        return

    sequence = FIRDARIA_DAY if sect == Sect.DAY else FIRDARIA_NIGHT
    order_str = " -> ".join([f"{p.value}({d}yr)" for p, d in sequence])

    trace.add(
        category=CAT_FIRDARIA,
        technique="Firdaria Period",
        inputs={"sect": "Day" if sect == Sect.DAY else "Night", "current_age": fird.get("Current Age", "?")},
        rule=f"{'Day' if sect == Sect.DAY else 'Night'} chart Firdaria sequence: {order_str}. Each major period is subdivided into 7 sub-periods.",
        source="Abu Ma'shar, On the Revolutions of the Years of Nativities",
        calculation=f"Age {fird.get('Current Age', '?')} falls in: Major = {fird.get('Major Period', '?')} ({fird.get('Major Start', '?')} to {fird.get('Major End', '?')}), Sub = {fird.get('Sub Period', '?')} ({fird.get('Sub Start', '?')} to {fird.get('Sub End', '?')}).",
        result=f"Major: {fird.get('Major Period', '?')} / Sub: {fird.get('Sub Period', '?')}",
        notes=f"Cross-reference with profections and transits for integrated timing.",
    )


def _trace_decennials(trace: ComputationTrace, chart: Chart, birth_date, target_date):
    """Trace Decennials (Valens chronocrator system)."""
    try:
        apheta = DecennialEngine.select_apheta(chart)
        apheta_name = apheta.name.value if hasattr(apheta.name, 'value') else str(apheta.name)

        is_day = chart.sun_altitude > 0
        sect_light = "Sun" if is_day else "Moon"

        trace.add(
            category=CAT_DECENNIALS,
            technique="Apheta Selection (Decennial Releaser)",
            inputs={"sect": "Day" if is_day else "Night", "sect_light": sect_light},
            rule=f"{'Day' if is_day else 'Night'} chart: Check Sect Light, Contrary Light, then Post-Ascendant planet. The first qualifying candidate is the Apheta.",
            source="Valens, Anthology IV.10-11",
            calculation=f"Sect Light = {sect_light}. Selected: {apheta_name} at {_fmt(apheta.longitude)}.",
            result=f"Apheta: {apheta_name}",
        )

        zod_seq = DecennialEngine.get_zodiacal_sequence(chart)
        seq_str = ", ".join([f"{p.name.value}({_fmt(p.longitude)})" for p in zod_seq])

        trace.add(
            category=CAT_DECENNIALS,
            technique="Zodiacal Sequence",
            inputs={"starting_from": "Ascendant"},
            rule="Order all 7 traditional planets by zodiacal longitude starting from the Ascendant degree.",
            source="Valens, Anthology IV.10",
            calculation=f"Ascendant at {_fmt(chart.ascendant)}. Ordering planets: {seq_str}.",
            result=f"Sequence: {' -> '.join([p.name.value for p in zod_seq])}",
        )

        try:
            periods = DecennialEngine.calculate_decennials(chart, birth_date, target_date)
            if periods and isinstance(periods, list) and len(periods) > 0:
                current = periods[-1]
                if isinstance(current, dict):
                    trace.add(
                        category=CAT_DECENNIALS,
                        technique="Current Decennial Period",
                        inputs={"target_date": str(target_date)},
                        rule="Each planet's major period lasts its Minor Years. Sub-periods cycle through the remaining planets in zodiacal order.",
                        source="Valens, Anthology IV.10-11",
                        calculation=f"Current period: {current}",
                        result=f"Major: {current.get('major', '?')} / Sub: {current.get('sub', '?')}",
                    )
        except Exception:
            pass

    except Exception as e:
        logger.warning(f"Decennial trace failed: {e}")


def _trace_lunar_mansions(trace: ComputationTrace, chart: Chart):
    """Trace the Moon's natal Lunar Mansion."""
    try:
        moon = next((p for p in chart.planets if p.name == PlanetName.MOON), None)
        if not moon:
            return

        mansion = LunarMansionEngine.get_lunar_mansion(moon.longitude)
        mansion_id = mansion.get("mansion_id", "?")
        mansion_name = mansion.get("name", "Unknown")
        good = ", ".join(mansion.get("intents_good", []))
        bad = ", ".join(mansion.get("intents_bad", []))
        sources = ", ".join(mansion.get("source_refs", []))

        trace.add(
            category=CAT_MANSIONS,
            technique="Natal Moon Lunar Mansion",
            inputs={"moon_longitude": round(moon.longitude, 4), "moon_position": _fmt(moon.longitude)},
            rule="Divide the ecliptic into 28 equal segments of 12°51'26\". The Moon's position determines the natal mansion and its electional properties.",
            source=sources or "Picatrix Bk I, Ch 4",
            calculation=f"Moon at {_fmt(moon.longitude)} → {moon.longitude:.4f}° ÷ 12.857° = Mansion #{mansion_id} ({mansion_name}).",
            result=f"Mansion #{mansion_id}: {mansion_name}",
            notes=f"Good for: {good}. Avoid: {bad}." if good or bad else None,
        )
    except Exception as e:
        logger.warning(f"Lunar mansion trace failed: {e}")


def _trace_primary_directions(trace: ComputationTrace, chart: Chart, raw: dict):
    """Trace Primary Directions to Angles (top 5 nearest)."""
    try:
        geo_lat = raw.get("meta", {}).get("lat")
        if geo_lat is None:
            return

        directions = PrimaryDirectionsEngine.calculate_directions_to_angles(chart, geo_lat)

        # Trace the method
        trace.add(
            category=CAT_DIRECTIONS,
            technique="Primary Directions Engine",
            inputs={"geographic_latitude": round(geo_lat, 4), "method": "Placidus/Zodiacal"},
            rule="Direct each traditional planet's zodiacal aspects to the Ascendant and Midheaven. Arc = OA(promittor aspect point) - OA(significator). 1° arc ≈ 1 year (Ptolemy Key).",
            source="Ptolemy, Tetrabiblos III.10; Placidus de Titis",
            calculation=f"Computed {len(directions)} directions to Asc/MC within 100° arc.",
            result=f"{len(directions)} valid directions found",
        )

        # Show top 5 nearest
        for d in directions[:5]:
            arc_str = f"{d.arc:.2f}°"
            trace.add(
                category=CAT_DIRECTIONS,
                technique=f"Direction: {d.promittor} {d.aspect} → {d.significator}",
                inputs={"promittor": d.promittor, "significator": d.significator, "aspect": d.aspect},
                rule=f"Zodiacal direction of {d.promittor}'s {d.aspect} ray to the {d.significator}.",
                source="Placidus de Titis, Primum Mobile",
                calculation=f"Arc = {arc_str}, converted via Ptolemy Key: {d.years:.1f} years ({d.date_offset}).",
                result=f"{d.date_offset} from birth",
                notes=f"Method: {d.method}",
            )
    except Exception as e:
        logger.warning(f"Primary directions trace failed: {e}")


def _trace_doryphory(trace: ComputationTrace, chart: Chart):
    """Trace Doryphory (bodyguard planets flanking the luminaries)."""
    try:
        instances = DoryphoryEngine.check_doryphory(chart)

        sun_guards = [i for i in instances if i.related_luminary == "Sun"]
        moon_guards = [i for i in instances if i.related_luminary == "Moon"]

        trace.add(
            category=CAT_ACCIDENTAL,
            technique="Doryphory (Spear-Bearers / Bodyguards)",
            inputs={"total_guards": len(instances), "solar": len(sun_guards), "lunar": len(moon_guards)},
            rule="Solar doryphory: planets rising before the Sun (oriental, within 30°, not combust <8°). Lunar doryphory: planets setting after the Moon (occidental, within 30°). Co-presence in the same sign also qualifies.",
            source="Porphyry, Introduction to the Tetrabiblos; Firmicus Maternus, Mathesis",
            calculation=f"Found {len(sun_guards)} solar bodyguard(s), {len(moon_guards)} lunar bodyguard(s).",
            result=f"{len(instances)} total bodyguards",
            notes="Doryphory dramatically elevates natal eminence. More guards = higher social standing potential." if instances else "No bodyguards found — native lacks doryphory support.",
        )

        for inst in instances:
            trace.add(
                category=CAT_ACCIDENTAL,
                technique=f"Bodyguard: {inst.planet.value}",
                inputs={"planet": inst.planet.value, "luminary": inst.related_luminary, "type": inst.type},
                rule=f"{inst.type} doryphory relative to the {inst.related_luminary}.",
                source="Porphyry; Firmicus Maternus",
                calculation=f"{inst.planet.value} acts as {inst.type} bodyguard to the {inst.related_luminary}.",
                result=f"Score: {inst.score}/10",
            )
    except Exception as e:
        logger.warning(f"Doryphory trace failed: {e}")


def _trace_dodecatemoria(trace: ComputationTrace, chart: Chart):
    """Trace Dodecatemoria (Twelfth-Parts) for all traditional planets."""
    try:
        data = DodecatemoriaEngine.get_dodecatemoria_data(chart, is_valens=True)
        if not data:
            return

        trace.add(
            category=CAT_DIGNITY,
            technique="Dodecatemoria (Twelfth-Parts)",
            inputs={"method": "Valens (×12)", "planets_computed": len(data)},
            rule="Each degree within a sign maps to 2.5° of a 'micro-zodiac'. Formula: Dodecatemorion = Longitude + (Degree-in-Sign × 12). The resulting sign and its ruler reveal a hidden layer of essential condition.",
            source="Vettius Valens, Anthology; Paulus Alexandrinus, Introductory Matters",
            calculation=f"Computed Dodecatemoria for {len(data)} planets using the Valens (×12) method.",
            result=f"{len(data)} twelfth-part projections",
        )

        # Individual planet dodecatemoria
        traditional_names = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
        for pname in traditional_names:
            if pname not in data:
                continue
            d = data[pname]
            planet_obj = next((p for p in chart.planets if p.name.value == pname), None)
            natal_pos = _fmt(planet_obj.longitude) if planet_obj else "?"
            trace.add(
                category=CAT_DIGNITY,
                technique=f"Dodecatemorion: {pname}",
                inputs={"natal_longitude": natal_pos, "degree_in_sign": round(planet_obj.longitude % 30, 2) if planet_obj else "?"},
                rule=f"Longitude + (Degree-in-Sign × 12) mod 360.",
                source="Vettius Valens, Anthology",
                calculation=f"{natal_pos} → degree-in-sign = {planet_obj.longitude % 30:.2f}° × 12 = {(planet_obj.longitude % 30) * 12:.2f}° arc → projected to {_fmt(d['longitude'])} in {d['sign']}" if planet_obj else "?",
                result=f"{d['sign']} (ruler: {d['ruler']}, term: {d.get('term_ruler', '?')})",
            )
    except Exception as e:
        logger.warning(f"Dodecatemoria trace failed: {e}")
