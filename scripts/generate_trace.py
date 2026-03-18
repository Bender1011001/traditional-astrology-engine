"""
Generate Computation Trace
==========================
Runs the full engine and captures every calculation step into a beautiful
standalone HTML document that practitioners can read and verify.

Usage:
    python scripts/generate_trace.py --date 1996-08-13 --time 07:18 --city Fairfield --state CA --name "Native"

Output:
    chart_outputs/<name>_trace.html   (self-contained, open in any browser)
    chart_outputs/<name>_trace.json   (machine-readable trace data)
"""

import sys
import os
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.engine.trace import (
    ComputationTrace,
    CAT_ASTRONOMY, CAT_SECT, CAT_DIGNITY, CAT_ACCIDENTAL,
    CAT_ASPECTS, CAT_LOTS, CAT_RECEPTION, CAT_KAKOSIS,
    CAT_VITALITY, CAT_ALMUTEN, CAT_TEMPERAMENT, CAT_PROFECTIONS,
    CAT_ZR, CAT_FIRDARIA, CAT_DECENNIALS, CAT_DIRECTIONS,
    CAT_STARS, CAT_MANSIONS, CAT_MUNDANE, CAT_MEDICAL,
)
from src.engine.models import Planet, Chart, Sect, PlanetName, Sign
from src.engine.calculator.main import calculate_chart_data
from src.engine.dignities import DignityCalculator
from src.engine.aspects import AspectEngine
from src.engine.lots import calculate_all_lots, LotName
from src.engine.reception import ReceptionEngine, ReceptionMode
from src.engine.kakosis import KakosisEngine
from src.engine.hyleg import HylegAlcocodenEngine
from src.engine.temperament import TemperamentEngine
from src.engine.advanced_mechanics import AlmutenEngine, HermeticLotEngine, DoryphoryEngine, DodecatemoriaEngine
from src.engine.prediction import (
    calculate_profection_sign, get_lord_of_year, AdvancedPredictionEngine
)
from src.engine.decennials import DecennialEngine
from src.engine.phasis import PhasisEngine
from src.engine.primary_directions import PrimaryDirectionsEngine
from src.engine.stars import check_fixed_stars
from src.engine.mansions import LunarMansionEngine
from src.engine.geniture import LordOfGenitureEngine
from src.engine.calculations import (
    calculate_solar_status, is_besieged, is_in_via_combusta,
    format_longitude, calculate_prenatal_syzygy_details
)
from src.engine.reference_data import (
    DOMICILES, EXALTATIONS, DOROTHEAN_TRIPLICITY, EGYPTIAN_TERMS,
    FACES_ORDER, SIGN_ELEMENTS, MOIETIES
)
from src.engine.forensic_engine import Auditor
import swisseph as swe


def _fmt(lon: float) -> str:
    """Format longitude to sign-degree-minute string."""
    f = format_longitude(lon)
    return f["string"] if isinstance(f, dict) else str(f)


def _sign_of(lon: float) -> Sign:
    return list(Sign)[int(lon / 30) % 12]


def _deg_in_sign(lon: float) -> float:
    return lon % 30.0


def _rebuild_chart(raw: dict) -> Chart:
    """Rebuild a Chart model from raw calculator output."""
    return Auditor._rebuild_chart_model(raw)


def trace_astronomy(trace: ComputationTrace, raw: dict, chart: Chart):
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


def trace_sect(trace: ComputationTrace, chart: Chart):
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


def trace_dignities(trace: ComputationTrace, chart: Chart):
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
        
        # Get dignity breakdown
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


def trace_aspects(trace: ComputationTrace, chart: Chart):
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


def trace_lots(trace: ComputationTrace, chart: Chart):
    """Trace lot calculations."""
    sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
    is_day = sect == Sect.DAY
    all_lots = calculate_all_lots(chart, sect)
    
    sun = next(p for p in chart.planets if p.name == PlanetName.SUN)
    moon = next(p for p in chart.planets if p.name == PlanetName.MOON)
    
    # Lot of Fortune (most important)
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
        rule=f"Day chart: Asc + Moon − Sun. Night chart: Asc + Sun − Moon. The Lot of Fortune represents the body, health, luck, and material circumstances. It reverses by sect.",
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
        rule=f"Day chart: Asc + Sun − Moon. Night chart: Asc + Moon − Sun. The Lot of Spirit represents the mind, intellect, career, reputation, and will. It is the counterpart of Fortune.",
        source="Paulus Alexandrinus, Introduction; Valens, Anthology IV",
        calculation=f"{formula_s} = {calc_s} (mod 360) = {spir:.2f}°",
        result=f"{_fmt(spir)}",
    )
    
    # Remaining lots (summary)
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


def trace_kakosis(trace: ComputationTrace, chart: Chart):
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
                rule="Check all 7 conditions of maltreatment (Overcoming, Opposition, Besiegement, Enclosure, Striking Ray, Adherence). If none apply, the planet is free from kakosis.",
                source="Valens, Anthology IV.7",
                calculation=f"All 7 checks passed for {planet.name.value} — no maltreatment detected.",
                result="✅ Clear",
                subsection=planet.name.value,
            )


def trace_vitality(trace: ComputationTrace, chart: Chart):
    """Trace Hyleg, Alcocoden, and Anareta."""
    sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
    
    hyleg = HylegAlcocodenEngine.determine_hyleg(chart)
    trace.add(
        category=CAT_VITALITY,
        technique="Hyleg (Giver of Life)",
        inputs={"sect": "Day" if sect == Sect.DAY else "Night"},
        rule=f"{'Day chart' if sect == Sect.DAY else 'Night chart'}: Check {'Sun → Moon → Lot of Fortune → Ascendant' if sect == Sect.DAY else 'Moon → Sun → Lot of Fortune → Ascendant'} (in priority order). The first luminary in a hylegical house (1, 7, 9, 10, 11) that is aspected by one of its rulers qualifies as the Hyleg.",
        source="Bonatti, Liber Astronomiae VIII; Lilly, CA pp.537-541",
        calculation=f"Checking candidates in order... Winner: {hyleg.get('name', 'None')} ({hyleg.get('type', '')}) at {_fmt(hyleg.get('longitude', 0))}.",
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
            
            # Lifespan
            lifespan = HylegAlcocodenEngine.calculate_lifespan(hyleg, alcocoden, chart)
            trace.add(
                category=CAT_VITALITY,
                technique="Vitality Calculation",
                inputs={"alcocoden": alco_name},
                rule="Start with the Alcocoden's base years (Minor/Mean/Major based on house placement and dignity). Then add years from benefic aspects to the Alcocoden, subtract years from malefic aspects.",
                source="Bonatti, Liber Astronomiae VIII; Lilly, CA pp.537-541",
                calculation=" → ".join(lifespan.get("breakdown", [])),
                result=f"Total: {lifespan.get('total_years', 0):.1f} years — Rating: {lifespan.get('vitality_rating', 'Unknown')}",
                notes="Historical Use Only. This section is not medical advice, diagnosis, or treatment.",
            )
        
        anareta = HylegAlcocodenEngine.determine_anareta(hyleg, chart)
        trace.add(
            category=CAT_VITALITY,
            technique="Anareta (Destroyer of Life)",
            inputs={"hyleg": hyleg.get("name"), "hyleg_longitude": _fmt(hyleg.get("longitude", 0))},
            rule="The Anareta is the planet (usually Mars or Saturn) making the tightest hard aspect (conjunction, square, opposition) to the Hyleg degree. The out-of-sect malefic is prioritized.",
            source="Bonatti, Liber Astronomiae VIII; Lilly, CA pp.537-541",
            calculation=anareta.get("reason", "No suitable candidate found."),
            result=f"Anareta: {anareta.get('name', 'None')}",
            notes="Historical Use Only. This section is not medical advice, diagnosis, or treatment.",
        )


def trace_temperament(trace: ComputationTrace, chart: Chart):
    """Trace temperament calculation."""
    temp = TemperamentEngine.calculate_temperament(chart)
    scores = temp.get("scores", {})
    net = temp.get("net_balance", {})
    
    breakdown_text = "\n".join(temp.get("breakdown", []))
    
    trace.add(
        category=CAT_TEMPERAMENT,
        technique="Lilly's Humoral Temperament",
        inputs={"method": "Christian Astrology pp.57-83"},
        rule="Sum Hot/Cold/Moist/Dry points from: (1) Ascendant sign element, (2) Ascendant ruler's sign, (3) Moon sign, (4) Moon phase, (5) Season, (6) Planets aspecting Moon, (7) Inherent planetary natures. Net balance determines temperament: Hot+Moist=Sanguine, Hot+Dry=Choleric, Cold+Dry=Melancholic, Cold+Moist=Phlegmatic.",
        source="Lilly, Christian Astrology, pp.57-83 (1647)",
        calculation=f"Hot={scores.get('Hot',0)}, Cold={scores.get('Cold',0)}, Moist={scores.get('Moist',0)}, Dry={scores.get('Dry',0)}. Net: Hot-Cold={net.get('Hot_vs_Cold', 0)}, Moist-Dry={net.get('Moist_vs_Dry', 0)}",
        result=f"{temp.get('primary_temperament', 'Unknown')}",
        notes=breakdown_text,
    )


def trace_profections(trace: ComputationTrace, chart: Chart, age: int):
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
        notes=f"The Lord of the Year ({loy.value}) is activated — transits to/from this planet, and planets in its natal sign, are the primary timing triggers for the year.",
    )


def trace_almuten(trace: ComputationTrace, chart: Chart):
    """Trace Almuten Figuris."""
    almuten_result = AlmutenEngine.calculate_almuten(chart)
    gen_result = LordOfGenitureEngine.calculate(chart)
    
    # Handle both dataclass and dict returns
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
        rule="Score each planet's essential dignities at the 5 hylegical degrees (Sun, Moon, Asc, PoF, SAN). The planet with the highest cumulative score is the Almuten Figuris — the 'Soul Guardian' or true ruler of the nativity.",
        source="Ibn Ezra, The Beginning of Wisdom; Bonatti",
        calculation=f"Winner: {almuten_winner} (top scorer across 5 places)",
        result=f"Almuten Figuris: {almuten_winner}",
    )
    
    trace.add(
        category=CAT_ALMUTEN,
        technique="Lord of Geniture (Lilly)",
        inputs={"method": "Net fortitudes & debilities (Ptolemaic terms/triplicity)"},
        rule="Score each planet on essential dignity (Ptolemaic) + accidental dignity (house, motion, speed, solar phase, orientality, aspects). The planet with the highest net score is the Lord of the Geniture.",
        source="Lilly, Christian Astrology (1647)",
        calculation=f"Winner: {gen_winner}",
        result=f"Lord of Geniture: {gen_winner}",
    )


def trace_fixed_stars(trace: ComputationTrace, chart: Chart):
    """Trace fixed star contacts."""
    contacts = check_fixed_stars(chart)
    
    if not contacts:
        trace.add(
            category=CAT_STARS,
            technique="Fixed Star Survey",
            inputs={"stars_checked": "21 Royal + Behenian stars"},
            rule="Check all 21 cataloged fixed stars for ecliptic conjunction and paran (co-culmination) contacts with all 7 traditional planets and the Ascendant/MC angles.",
            source="Ptolemy, Tetrabiblos I.9; Robson, Fixed Stars & Constellations",
            calculation="No contacts found within orb for any star-planet pair.",
            result="No fixed star contacts",
        )
        return
    
    for contact in contacts:
        # Find the star data for enrichment
        from src.engine.stars import STARS as STAR_CATALOG
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
                rule=f"A fixed star conjunct a planet within orb ({star_data.orb if star_data else 1.0} deg) infuses the planet with the star's nature. First-magnitude stars are strongest.",
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
                rule="A Paran (paranatellonta) occurs when a star and planet are simultaneously on angular points (ASC, MC, DSC, IC). Parans are superior to ecliptic conjunctions for eminence.",
                source="Ptolemy, Phaseis; Brady, Fixed Stars",
                calculation=contact.message,
                result=f"Paran at {contact.angle}: {contact.star_name} + {contact.planet_name}",
                subsection="Parans (Co-Rising/Setting)",
            )
        elif contact.contact_type == "ANGULAR_PRESENCE":
            trace.add(
                category=CAT_STARS,
                technique=f"{contact.star_name} on {contact.planet_name}",
                inputs={"star": contact.star_name, "angle": contact.planet_name},
                rule="A fixed star directly on the Ascendant or Midheaven is an indicator of eminence or notoriety, depending on the star's nature.",
                source="Ptolemy, Tetrabiblos I.9; Robson",
                calculation=contact.message,
                result=f"Star on angle: {contact.star_name} on {contact.planet_name}",
                subsection="Angular Stars",
            )
        elif contact.contact_type == "AXIS_ALERT":
            trace.add(
                category=CAT_STARS,
                technique=f"Antares-Aldebaran Axis: {contact.planet_name}",
                inputs={"planet": contact.planet_name},
                rule="The Antares-Aldebaran axis (Royal Stars at 180 deg opposition) is a critical polarity. Moon or Mars on this axis signifies intense life themes around integrity vs. obsession.",
                source="Ptolemy; Robson, Fixed Stars & Constellations",
                calculation=contact.message,
                result="Critical axis activated",
                subsection="Axis Alerts",
                notes="Historical Use Only. Traditional violent-death significations are noted for scholarly context, not predictive use.",
            )


def trace_reception(trace: ComputationTrace, chart: Chart):
    """Trace reception and mutual reception."""
    from src.engine.reception import ReceptionEngine, ReceptionMode
    
    mutuals = ReceptionEngine.calculate_mutual_receptions(chart, ReceptionMode.STANDARD_LILLY)
    
    if mutuals:
        for mr in mutuals:
            pa = mr.planet_a.value if hasattr(mr.planet_a, 'value') else str(mr.planet_a)
            pb = mr.planet_b.value if hasattr(mr.planet_b, 'value') else str(mr.planet_b)
            
            trace.add(
                category=CAT_RECEPTION,
                technique=f"Mutual Reception: {pa} <-> {pb}",
                inputs={
                    "planet_a": pa,
                    "planet_b": pb,
                    "type": mr.type,
                    "strength": mr.strength_score,
                },
                rule=f"Mutual Reception: {pa} is in {pb}'s dignity AND {pb} is in {pa}'s dignity. They support each other. Type: {mr.type}. A Pure Domicile mutual reception is the strongest (planets effectively swap signs).",
                source="Bonatti, Liber Astronomiae; Lilly, Christian Astrology",
                calculation=f"{pa} reception of {pb}: {', '.join(mr.reception_a_in_b.dignities)} (score {mr.reception_a_in_b.score}). {pb} reception of {pa}: {', '.join(mr.reception_b_in_a.dignities)} (score {mr.reception_b_in_a.score}). Combined: {mr.strength_score}.",
                result=f"{mr.type} Mutual Reception (strength: {mr.strength_score})",
                notes=f"Operative: A→B {'Yes' if mr.reception_a_in_b.is_operative else 'No'}, B→A {'Yes' if mr.reception_b_in_a.is_operative else 'No'}.",
            )
    else:
        trace.add(
            category=CAT_RECEPTION,
            technique="Mutual Reception Survey",
            inputs={"mode": "Standard (Lilly)"},
            rule="Check all 21 planet-pairs for mutual reception (two planets each having dignity in the other's sign). None found.",
            source="Bonatti, Liber Astronomiae; Lilly, Christian Astrology",
            calculation="All 21 pairs checked — no mutual reception detected.",
            result="No mutual receptions",
        )


def trace_firdaria(trace: ComputationTrace, chart: Chart, birth_date, target_date):
    """Trace Firdaria periods."""
    from src.engine.prediction import calculate_firdaria, FIRDARIA_DAY, FIRDARIA_NIGHT
    
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
        inputs={
            "sect": "Day" if sect == Sect.DAY else "Night",
            "current_age": fird.get("Current Age", "?"),
        },
        rule=f"{'Day' if sect == Sect.DAY else 'Night'} chart Firdaria sequence: {order_str}. Each major period is subdivided into 7 sub-periods (one per planet). The major lord sets the theme; the sub-lord modifies it.",
        source="Abu Ma'shar, On the Revolutions of the Years of Nativities",
        calculation=f"Age {fird.get('Current Age', '?')} falls in: Major = {fird.get('Major Period', '?')} ({fird.get('Major Start', '?')} to {fird.get('Major End', '?')}), Sub = {fird.get('Sub Period', '?')} ({fird.get('Sub Start', '?')} to {fird.get('Sub End', '?')}).",
        result=f"Major: {fird.get('Major Period', '?')} / Sub: {fird.get('Sub Period', '?')}",
        notes=f"The current Firdaria lord ({fird.get('Major Period', '?')}) should be cross-referenced with profections and transits for integrated timing.",
    )


def trace_decennials(trace: ComputationTrace, chart: Chart, birth_date, target_date):
    """Trace Decennials (Valens chronocrator system)."""
    apheta = DecennialEngine.select_apheta(chart)
    apheta_name = apheta.name.value if hasattr(apheta.name, 'value') else str(apheta.name)
    
    is_day = chart.sun_altitude > 0
    sect_light = "Sun" if is_day else "Moon"
    
    trace.add(
        category=CAT_DECENNIALS,
        technique="Apheta Selection (Decennial Releaser)",
        inputs={"sect": "Day" if is_day else "Night", "sect_light": sect_light},
        rule=f"{'Day' if is_day else 'Night'} chart: Check (1) Sect Light in operative houses (1,10,11,7,5,9,4), (2) Contrary Light in operative place, (3) Post-Ascendant planet. The first qualifying candidate is the Apheta — the starting planet for the Decennial sequence.",
        source="Valens, Anthology IV.10-11",
        calculation=f"Sect Light = {sect_light}. Checking operative houses... Selected: {apheta_name} at {_fmt(apheta.longitude)}.",
        result=f"Apheta: {apheta_name}",
    )
    
    # Get the zodiacal sequence
    zod_seq = DecennialEngine.get_zodiacal_sequence(chart)
    seq_str = ", ".join([f"{p.name.value}({_fmt(p.longitude)})" for p in zod_seq])
    
    trace.add(
        category=CAT_DECENNIALS,
        technique="Zodiacal Sequence",
        inputs={"starting_from": "Ascendant"},
        rule="Order all 7 traditional planets by zodiacal longitude starting from the Ascendant degree. This sequence determines the order of Decennial major periods.",
        source="Valens, Anthology IV.10",
        calculation=f"Ascendant at {_fmt(chart.ascendant)}. Ordering planets: {seq_str}.",
        result=f"Sequence: {' -> '.join([p.name.value for p in zod_seq])}",
    )
    
    # Calculate the actual decennial periods for current date
    try:
        periods = DecennialEngine.calculate_decennials(chart, birth_date, target_date)
        if periods and not isinstance(periods, dict):
            current = periods[-1] if isinstance(periods, list) else periods
            if isinstance(current, dict):
                trace.add(
                    category=CAT_DECENNIALS,
                    technique="Current Decennial Period",
                    inputs={"target_date": str(target_date)},
                    rule="Each planet's major period lasts its Minor Years. Sub-periods cycle through the remaining planets in zodiacal order, each lasting proportional years.",
                    source="Valens, Anthology IV.10-11",
                    calculation=f"Current period: {current}",
                    result=f"Major: {current.get('major', '?')} / Sub: {current.get('sub', '?')}",
                )
    except Exception:
        pass


# ─── HTML Renderer ────────────────────────────────────────────────────────────

def render_html(trace: ComputationTrace) -> str:
    """Render the trace as a beautiful standalone HTML document."""
    
    categories_html = []
    for cat in trace.categories:
        steps = trace.steps_by_category(cat)
        
        # Group by subsection within category
        subsections = {}
        for s in steps:
            key = s.subsection or "__main__"
            subsections.setdefault(key, []).append(s)
        
        steps_html_parts = []
        for sub_key, sub_steps in subsections.items():
            if sub_key != "__main__":
                steps_html_parts.append(f'<h4 class="subsection-header">{sub_key}</h4>')
            
            for s in sub_steps:
                inputs_rows = "".join(
                    f'<tr><td class="input-key">{k}</td><td class="input-val">{v}</td></tr>'
                    for k, v in s.inputs.items()
                )
                notes_html = f'<div class="step-notes"><strong>📝 Practitioner Note:</strong> {s.notes}</div>' if s.notes else ""
                
                steps_html_parts.append(f'''
                <div class="step-card">
                    <div class="step-header">
                        <span class="step-number">Step {s.step_number}</span>
                        <span class="step-technique">{s.technique}</span>
                    </div>
                    <div class="step-body">
                        <div class="step-section">
                            <div class="section-label">📥 Inputs</div>
                            <table class="inputs-table">{inputs_rows}</table>
                        </div>
                        <div class="step-section">
                            <div class="section-label">📜 Rule</div>
                            <div class="rule-text">{s.rule}</div>
                            <div class="source-tag">— {s.source}</div>
                        </div>
                        <div class="step-section">
                            <div class="section-label">🔢 Calculation</div>
                            <div class="calc-text">{s.calculation}</div>
                        </div>
                        <div class="step-section result-section">
                            <div class="section-label">✅ Result</div>
                            <div class="result-text">{s.result}</div>
                        </div>
                        {notes_html}
                    </div>
                </div>
                ''')
        
        steps_html = "\n".join(steps_html_parts)
        cat_id = cat.replace(" ", "-").replace("/", "-").lower()
        
        categories_html.append(f'''
        <div class="category-block" id="{cat_id}">
            <h3 class="category-title" onclick="toggleCategory(this)">
                <span class="collapse-icon">▼</span> {cat}
                <span class="step-count">{len(steps)} steps</span>
            </h3>
            <div class="category-body">
                {steps_html}
            </div>
        </div>
        ''')
    
    # Table of contents
    toc_items = "\n".join(
        f'<li><a href="#{cat.replace(" ", "-").replace("/", "-").lower()}">{cat}</a> <span class="toc-count">({len(trace.steps_by_category(cat))} steps)</span></li>'
        for cat in trace.categories
    )
    
    all_categories = "\n".join(categories_html)
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Computation Trace — {trace.subject_name}</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    :root {{
        --bg: #0a0a0f;
        --surface: #12121a;
        --surface-2: #1a1a2e;
        --surface-3: #252540;
        --border: #2a2a45;
        --text: #e8e8f0;
        --text-dim: #8888aa;
        --text-muted: #555570;
        --accent: #7c6aef;
        --accent-glow: #7c6aef40;
        --gold: #d4a853;
        --gold-glow: #d4a85330;
        --green: #4ade80;
        --cyan: #22d3ee;
        --red: #f87171;
        --orange: #fb923c;
    }}
    
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    
    body {{
        font-family: 'Inter', -apple-system, sans-serif;
        background: var(--bg);
        color: var(--text);
        line-height: 1.6;
        min-height: 100vh;
    }}
    
    .hero {{
        background: linear-gradient(135deg, #0f0c29 0%, #1a1040 40%, #24243e 100%);
        border-bottom: 1px solid var(--border);
        padding: 3rem 2rem;
        text-align: center;
    }}
    
    .hero h1 {{
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--gold), #f0d890, var(--gold));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }}
    
    .hero .subtitle {{
        color: var(--text-dim);
        font-size: 1.1rem;
        font-weight: 300;
    }}
    
    .hero .meta-line {{
        margin-top: 1rem;
        display: flex;
        gap: 2rem;
        justify-content: center;
        flex-wrap: wrap;
    }}
    
    .hero .meta-badge {{
        background: var(--surface-2);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-size: 0.85rem;
        color: var(--text-dim);
    }}
    
    .hero .meta-badge strong {{
        color: var(--gold);
    }}
    
    .container {{
        max-width: 1000px;
        margin: 0 auto;
        padding: 2rem;
    }}
    
    /* TOC */
    .toc {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
    }}
    
    .toc h2 {{
        font-size: 1.1rem;
        color: var(--gold);
        margin-bottom: 1rem;
        font-weight: 600;
    }}
    
    .toc ul {{
        list-style: none;
        columns: 2;
        column-gap: 2rem;
    }}
    
    .toc li {{
        padding: 0.3rem 0;
        break-inside: avoid;
    }}
    
    .toc a {{
        color: var(--accent);
        text-decoration: none;
        font-size: 0.9rem;
        transition: color 0.2s;
    }}
    
    .toc a:hover {{
        color: var(--gold);
    }}
    
    .toc-count {{
        color: var(--text-muted);
        font-size: 0.8rem;
    }}
    
    /* Category */
    .category-block {{
        margin-bottom: 1.5rem;
    }}
    
    .category-title {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1rem 1.5rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.8rem;
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--gold);
        transition: all 0.2s;
        user-select: none;
    }}
    
    .category-title:hover {{
        background: var(--surface-2);
        border-color: var(--gold);
        box-shadow: 0 0 20px var(--gold-glow);
    }}
    
    .collapse-icon {{
        transition: transform 0.3s;
        font-size: 0.8rem;
    }}
    
    .category-title.collapsed .collapse-icon {{
        transform: rotate(-90deg);
    }}
    
    .step-count {{
        margin-left: auto;
        font-size: 0.8rem;
        font-weight: 400;
        color: var(--text-muted);
        background: var(--surface-3);
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
    }}
    
    .category-body {{
        padding: 0.5rem 0 0 0;
        transition: max-height 0.4s ease;
        overflow: hidden;
    }}
    
    .category-body.hidden {{
        display: none;
    }}
    
    .subsection-header {{
        color: var(--cyan);
        font-size: 0.95rem;
        font-weight: 600;
        padding: 0.8rem 0 0.3rem 0.5rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 0.5rem;
    }}
    
    /* Step Card */
    .step-card {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        margin-bottom: 0.75rem;
        overflow: hidden;
        transition: border-color 0.2s;
    }}
    
    .step-card:hover {{
        border-color: var(--accent);
    }}
    
    .step-header {{
        background: var(--surface-2);
        padding: 0.6rem 1.2rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        border-bottom: 1px solid var(--border);
    }}
    
    .step-number {{
        background: var(--accent);
        color: white;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        white-space: nowrap;
    }}
    
    .step-technique {{
        font-weight: 600;
        font-size: 0.95rem;
    }}
    
    .step-body {{
        padding: 1rem 1.2rem;
    }}
    
    .step-section {{
        margin-bottom: 0.8rem;
    }}
    
    .section-label {{
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.3rem;
    }}
    
    .inputs-table {{
        width: 100%;
        font-size: 0.85rem;
        border-collapse: collapse;
    }}
    
    .inputs-table tr {{
        border-bottom: 1px solid var(--border);
    }}
    
    .inputs-table tr:last-child {{
        border-bottom: none;
    }}
    
    .input-key {{
        color: var(--text-dim);
        padding: 0.3rem 0.5rem 0.3rem 0;
        width: 120px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
    }}
    
    .input-val {{
        padding: 0.3rem 0;
        color: var(--text);
    }}
    
    .rule-text {{
        font-size: 0.9rem;
        color: var(--text);
        line-height: 1.7;
        padding: 0.5rem 0.8rem;
        background: var(--surface-2);
        border-radius: 6px;
        border-left: 3px solid var(--gold);
    }}
    
    .source-tag {{
        font-size: 0.8rem;
        color: var(--gold);
        font-style: italic;
        margin-top: 0.3rem;
        padding-left: 0.8rem;
    }}
    
    .calc-text {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        color: var(--cyan);
        background: var(--surface-2);
        padding: 0.6rem 0.8rem;
        border-radius: 6px;
        white-space: pre-wrap;
        word-break: break-word;
    }}
    
    .result-section {{
        background: linear-gradient(135deg, var(--surface-2), var(--surface-3));
        border-radius: 8px;
        padding: 0.8rem;
        border: 1px solid var(--border);
    }}
    
    .result-text {{
        font-size: 1rem;
        font-weight: 600;
        color: var(--green);
    }}
    
    .step-notes {{
        margin-top: 0.5rem;
        font-size: 0.82rem;
        color: var(--text-dim);
        background: var(--surface-2);
        padding: 0.5rem 0.8rem;
        border-radius: 6px;
        border-left: 3px solid var(--orange);
        white-space: pre-wrap;
    }}
    
    /* Footer */
    .footer {{
        text-align: center;
        padding: 2rem;
        color: var(--text-muted);
        font-size: 0.8rem;
        border-top: 1px solid var(--border);
        margin-top: 2rem;
    }}
    
    /* Responsive */
    @media (max-width: 768px) {{
        .hero h1 {{ font-size: 1.5rem; }}
        .toc ul {{ columns: 1; }}
        .container {{ padding: 1rem; }}
        .hero {{ padding: 2rem 1rem; }}
    }}

    /* Print */
    @media print {{
        body {{ background: white; color: #111; }}
        .step-card {{ break-inside: avoid; border: 1px solid #ccc; }}
        .hero {{ background: none; border: none; }}
        .hero h1 {{ color: #333; -webkit-text-fill-color: #333; }}
        .category-body.hidden {{ display: block !important; }}
    }}
</style>
</head>
<body>
    <div class="hero">
        <h1>⚙ Computation Trace</h1>
        <div class="subtitle">Every calculation step, verified and sourced</div>
        <div class="meta-line">
            <div class="meta-badge"><strong>{trace.subject_name}</strong></div>
            <div class="meta-badge">{trace.birth_data}</div>
            <div class="meta-badge"><strong>{len(trace.steps)}</strong> computation steps</div>
            <div class="meta-badge">Completed in <strong>{trace.elapsed_ms:.0f}ms</strong></div>
            <div class="meta-badge">Generated <strong>{trace.started_at.strftime("%Y-%m-%d %H:%M")}</strong></div>
        </div>
    </div>
    
    <div class="container">
        <div class="toc">
            <h2>Table of Contents</h2>
            <ul>{toc_items}</ul>
        </div>
        
        {all_categories}
        
        <div class="footer">
            <p>Traditional Astrology Engine — Computation Trace</p>
            <p>All calculations use pre-1700 methods. Sources cited per step.</p>
            <p>Historical Use Only. Not medical, financial, or legal advice.</p>
        </div>
    </div>
    
    <script>
        function toggleCategory(el) {{
            el.classList.toggle('collapsed');
            const body = el.nextElementSibling;
            body.classList.toggle('hidden');
        }}
    </script>
</body>
</html>'''


def main():
    parser = argparse.ArgumentParser(description="Generate a Computation Trace for a nativity.")
    parser.add_argument("--date", default="1996-08-13", help="Birth date (YYYY-MM-DD)")
    parser.add_argument("--time", default="07:18", help="Birth time (HH:MM)")
    parser.add_argument("--city", default="Fairfield", help="Birth city")
    parser.add_argument("--state", default="CA", help="Birth state/country")
    parser.add_argument("--name", default="Native", help="Subject name")
    args = parser.parse_args()
    
    birth_label = f"{args.date} {args.time}, {args.city}, {args.state}"
    trace = ComputationTrace(subject_name=args.name, birth_data=birth_label)
    
    print(f"{'='*70}")
    print(f"GENERATING COMPUTATION TRACE")
    print(f"Subject: {args.name} | Birth: {birth_label}")
    print(f"{'='*70}")
    
    # 1. Calculate chart
    print("\n[1/10] Calculating chart...")
    raw = calculate_chart_data(
        date_str=args.date, time_str=args.time,
        city=args.city, state=args.state, house_system="W"
    )
    
    if "error" in raw:
        print(f"ERROR: {raw['error']}")
        return
    
    chart = _rebuild_chart(raw)
    jd = raw["meta"]["julian_day"]
    
    # Determine age
    birth_dt = datetime.fromisoformat(raw["meta"].get("utc_time", args.date))
    if birth_dt.tzinfo:
        birth_dt = birth_dt.replace(tzinfo=None)
    now = datetime.now()
    age = now.year - birth_dt.year - ((now.month, now.day) < (birth_dt.month, birth_dt.day))
    
    # 2. Trace every category
    print("[2/14] Tracing astronomical foundations...")
    trace_astronomy(trace, raw, chart)
    
    print("[3/14] Tracing sect determination...")
    trace_sect(trace, chart)
    
    print("[4/14] Tracing essential dignities (5-tier per planet)...")
    trace_dignities(trace, chart)
    
    print("[5/14] Tracing aspects...")
    trace_aspects(trace, chart)
    
    print("[6/14] Tracing lots / Arabic parts...")
    trace_lots(trace, chart)
    
    print("[7/14] Tracing kakosis (maltreatment conditions)...")
    trace_kakosis(trace, chart)
    
    print("[8/14] Tracing vitality (Hyleg -> Alcocoden -> Anareta)...")
    trace_vitality(trace, chart)
    
    print("[9/14] Tracing temperament, Almuten, profections...")
    trace_temperament(trace, chart)
    trace_almuten(trace, chart)
    trace_profections(trace, chart, age)
    
    print("[10/14] Tracing fixed stars...")
    trace_fixed_stars(trace, chart)
    
    print("[11/14] Tracing reception / mutual reception...")
    trace_reception(trace, chart)
    
    print("[12/14] Tracing Firdaria...")
    trace_firdaria(trace, chart, birth_dt, now)
    
    print("[13/14] Tracing Decennials...")
    trace_decennials(trace, chart, birth_dt, now)
    
    print("[14/14] Rendering HTML...")
    
    # Output
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'chart_outputs')
    os.makedirs(out_dir, exist_ok=True)
    
    safe_name = args.name.replace(" ", "_").lower()
    
    # HTML
    html = render_html(trace)
    html_path = os.path.join(out_dir, f'{safe_name}_computation_trace.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\n[OK] HTML trace saved: {html_path}")
    
    # JSON
    json_path = os.path.join(out_dir, f'{safe_name}_computation_trace.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(trace.to_dict(), f, indent=2, default=str)
    print(f"[OK] JSON trace saved: {json_path}")
    
    print(f"\n{'='*70}")
    print(f"TRACE COMPLETE: {len(trace.steps)} steps across {len(trace.categories)} categories")
    print(f"Elapsed: {trace.elapsed_ms:.0f}ms")
    print(f"\nOpen {html_path} in any browser to view the trace.")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
