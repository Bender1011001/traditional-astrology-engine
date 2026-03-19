from datetime import datetime
from typing import Dict, List, Optional, Any
import swisseph as swe
import logging

from .models import Planet, Chart, Sect, PlanetName, Sign
from src.engine.calculator.main import calculate_chart_data
from .advanced_mechanics import AlmutenEngine, HermeticLotEngine, DoryphoryEngine, MonomoiriaEngine, DodecatemoriaEngine
from .electional import ElectionalEngine
from .solar_return import SolarReturnEngine
from .planetary_hours import PlanetaryHourEngine
from .kakosis import KakosisEngine
from .medical import MedicalAstrology
from .synthesis import ReportSynthesizer
from .reference_data import PLANET_ESSENCES, TERM_METHODS, RULE_SOURCE_MAP
from .lots import calculate_all_lots, LotName
from .horary import calculate_antiscia, analyze_horary_physics
from .prediction import (
    calculate_profection_sign, 
    calculate_monthly_profection, 
    calculate_daily_profection,
    get_lord_of_year,
    AdvancedPredictionEngine,
    calculate_solar_return_jd,
    calculate_epitasis_days
)
from .decennials import DecennialEngine
from .phasis import PhasisEngine
from src.database.db_manager import DelineationLibrary
from .primary_directions import PrimaryDirectionsEngine
from .mundane import MundaneEngine, check_eclipse_impact, get_recent_eclipses
from .reception import ReceptionEngine, ReceptionMode
from .stars import check_fixed_stars
from .decumbiture import DecumbitureEngine
from .aspects import AspectEngine
from .dignities import DignityCalculator
from .hyleg import HylegAlcocodenEngine
from .temperament import TemperamentEngine
from .mansions import LunarMansionEngine
from .geniture import LordOfGenitureEngine
from .calculations import calculate_solar_status, is_besieged, is_in_via_combusta, format_longitude
import re

RULE_SOURCE_MAP_EXT = {
    "Bonatti Consideration 5": ["Bonatti, Liber Astronomiae, Consideration 5 (Void of Course)"],
    "Bonatti Consideration 30": ["Bonatti, Liber Astronomiae, Consideration 30 (Planet at 29°)"],
    "Bonatti Consideration 141": ["Bonatti, Liber Astronomiae, Consideration 141 (Significator in Ascendant)"],
    "Via Combusta": ["Traditional doctrine (Lilly, Christian Astrology, p. 115)"],
    "Combustion": ["Traditional doctrine (Ptolemy, Tetrabiblos I.24; Lilly, CA, p. 113)"],
    "Besiegement": ["Traditional doctrine (Lilly, Christian Astrology, p. 114)"],
    "Antiscia": ["Firmicus Maternus, Mathesis II.30", "Lilly, CA, p. 90"],
    "Melothesia": ["Manilius, Astronomica IV", "Culpeper, English Physician"],
    "Sect/Hayz/Halb": ["Ptolemy, Tetrabiblos III.3", "Dorotheus, Carmen Astrologicum I.1"],
    "Universal Overdrive": ["Ptolemy, Tetrabiblos II.1"],
    "Universal Causation": ["Ptolemy, Tetrabiblos II.8"],
    "Mundane Rank 4 > Natal Particulars": ["Traditional mundane hierarchy (Ptolemy, Tetrabiblos II.3)"],
    "Aries Ingress": ["Traditional mundane ingress doctrine (Bonatti, Liber Astronomiae, VIII)"]
}

def _extract_sources(text: Optional[str]) -> List[str]:
    if not text:
        return []
    matches = re.findall(r"\(([^)]+)\)", text)
    return [m.strip() for m in matches if m.strip()]

def _resolve_sources(cause: Optional[str], rule_text: Optional[str]) -> List[str]:
    sources = []
    sources.extend(_extract_sources(rule_text))
    if not sources and rule_text in RULE_SOURCE_MAP_EXT:
        sources.extend(RULE_SOURCE_MAP_EXT[rule_text])
    if cause:
        for key, refs in RULE_SOURCE_MAP_EXT.items():
            if key in cause:
                sources.extend(refs)
                break
    deduped = []
    for src in sources:
        if src not in deduped:
            deduped.append(src)
    return deduped

def _estimate_confidence(sources: List[str], conflicts: List[str], base: int = 70) -> int:
    score = base
    score += len(sources) * 5
    score -= len(conflicts) * 10
    return min(max(score, 0), 100)

def _slugify(text: str) -> str:
    return re.sub(r'[\W_]+', '-', text.lower()).strip('-')

logger = logging.getLogger(__name__)

# Initialize Library
LIB = DelineationLibrary()

class Auditor:
    """
    The Auditor (Hub): The sole orchestrator for deep astrological auditing.
    Replaces the legacy 'Sovereign Engine' terminology.
    Output: Bifurcated JSON (technical_data, human_translation).
    """

    @staticmethod
    def generate_full_nativity(
        date_str: str,
        time_str: str,
        city: str,
        state: str = "",
        name: str = "Native",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        house_system: str = "W",
        zodiac_system: str = "tropical",
        ayanamsa: Optional[str] = None,
        node_type: str = "mean",
        analysis_date: Optional[datetime] = None,
        decumbiture_jd: Optional[float] = None,
        decumbiture_utc_iso: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Single Entry Point for Comprehensive Forensic Audit.
        """
        try:
            # 1. Astronomy: Call chart_calculator
            raw_chart_data = calculate_chart_data(
                date_str=date_str,
                time_str=time_str,
                city=city,
                state=state,
                latitude=latitude,
                longitude=longitude,
                house_system=house_system,
                zodiac_system=zodiac_system,
                ayanamsa=ayanamsa,
                node_type=node_type,
            )

            if "error" in raw_chart_data:
                return {"error": raw_chart_data["error"]}

            # Reconstruct Chart Model
            chart = Auditor._rebuild_chart_model(raw_chart_data)
            jd = raw_chart_data["meta"]["julian_day"]
            
            # Resolve Dates
            ans_date = analysis_date or datetime.now()
            birth_dt = None
            if "utc_time" in raw_chart_data["meta"]:
                birth_dt = datetime.fromisoformat(raw_chart_data["meta"]["utc_time"])
                if birth_dt.tzinfo: birth_dt = birth_dt.replace(tzinfo=None)
            
            # Age Calculation
            age = 0
            if birth_dt:
                age = ans_date.year - birth_dt.year - ((ans_date.month, ans_date.day) < (birth_dt.month, birth_dt.day))

            # 2. Analysis: Aggregate Specialized Engine Results via Centralized Auditor
            # Optional: allow decumbiture critical days when an illness-onset JD is provided.
            if decumbiture_jd is None and decumbiture_utc_iso:
                try:
                    ddt = datetime.fromisoformat(decumbiture_utc_iso.replace("Z", "+00:00"))
                    # Convert to naive UTC for swe.julday if tz-aware
                    if ddt.tzinfo is not None:
                        ddt = ddt.astimezone(tz=None).replace(tzinfo=None)
                    decumbiture_jd = swe.julday(ddt.year, ddt.month, ddt.day, ddt.hour + (ddt.minute / 60.0) + (ddt.second / 3600.0))
                except Exception as e:
                    logger.warning(f"Invalid decumbiture_utc_iso; ignoring. Error: {e}")
                    decumbiture_jd = None

            audit_results = Auditor.perform_audit(
                chart=chart,
                jd=jd,
                birth_dt=birth_dt,
                ans_date=ans_date,
                age=age,
                decumbiture_jd=decumbiture_jd,
            )
            analysis = audit_results["analysis"]
            planets_forensic = audit_results["planets_forensic"]

            # Ensure planetary forensic payload is available under analysis for prompt/Data Map stability.
            # (Some callers only pass `technical_data.analysis` into an LLM, so keep this co-located.)
            if isinstance(analysis, dict):
                analysis["planets_forensic"] = planets_forensic

            # 3. State Assembly: Assemble technical_data
            technical_data = {
                "meta": {
                    "subject_name": name,
                    "generated_at": datetime.now().isoformat(),
                    "analysis_date": ans_date.replace(microsecond=0).isoformat(),
                    "julian_day": jd,
                    "age": age,
                    # Birth/location inputs (auditable). Preserve calculator meta verbatim so downstream
                    # consumers can cite the actual birth date/time/location, timezone, and geocode source.
                    "chart": raw_chart_data.get("meta", {}),
                    # Back-compat convenience fields
                    "birth_date": raw_chart_data.get("meta", {}).get("date"),
                    "birth_time": raw_chart_data.get("meta", {}).get("time"),
                    "city": raw_chart_data.get("meta", {}).get("city"),
                    "state": raw_chart_data.get("meta", {}).get("state"),
                    "lat": raw_chart_data.get("meta", {}).get("lat"),
                    "lon": raw_chart_data.get("meta", {}).get("lon"),
                    "timezone": raw_chart_data.get("meta", {}).get("timezone"),
                    "utc_time": raw_chart_data.get("meta", {}).get("utc_time"),
                },
                "astronomy": {
                    "planets": raw_chart_data["planets"],
                    "houses": raw_chart_data["houses"],
                    "angles": {
                        "Ascendant": raw_chart_data["angles"].get("Ascendant"),
                        "MC": raw_chart_data["angles"].get("MC"),
                    }
                },
                "analysis": analysis,
                # Back-compat for older consumers. Prefer `technical_data.analysis.planets_forensic`.
                "planets_forensic": planets_forensic,
                "rule_ledger": audit_results.get("rule_ledger", [])
            }

            # 4. Translation: Pass to ReportSynthesizer
            legacy_report = Auditor._map_to_legacy_report(technical_data, chart)
            human_translation = {
                "report_markdown": ReportSynthesizer.synthesize(legacy_report),
                "executive_summary": ReportSynthesizer._generate_executive_summary(legacy_report)
            }

            return {
                "technical_data": technical_data,
                "human_translation": human_translation
            }

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"Auditor Failure: {e}\n{error_trace}")
            return {"error": f"Auditor Failure: {str(e)}"}

    @staticmethod
    def perform_audit(
        chart: Chart, 
        jd: float, 
        birth_dt: Optional[datetime] = None, 
        ans_date: Optional[datetime] = None,
        age: Optional[int] = None,
        decumbiture_jd: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Exhaustive Architectural Audit of a Nativity.
        Consolidates logic from perform_forensic_audit (logic.py).
        """
        ans_date = ans_date or datetime.now()
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
        
        # 1. Base Analysis
        analysis = {}
        # Explicit sect payload so downstream prompts don't try to infer via houses/signs.
        analysis["sect"] = {
            "type": "DAY" if sect == Sect.DAY else "NIGHT",
            "sun_altitude_deg": chart.sun_altitude,
            "note": "Sect is determined by Sun altitude (above/below horizon), not by house labels."
        }
        analysis[ "dignity" ] = Auditor._calculate_dignity_suite(chart)
        analysis[ "fate" ] = Auditor._calculate_fate_suite(chart, birth_dt, ans_date)
        analysis[ "teams" ] = Auditor._calculate_teams_and_reception(chart)
        # For "Interfector" timing we need an approximate age in years.
        age_years = None
        if birth_dt and ans_date:
            try:
                age_years = max(0.0, (ans_date - birth_dt).days / 365.25)
            except Exception:
                age_years = None
        if age_years is None and age is not None:
            age_years = float(age)

        analysis["vitality"] = Auditor._calculate_vitality_suite(chart, age_years=age_years)
        analysis["triplicity_periods"] = Auditor._calculate_triplicity_periods(chart)
        analysis[ "temperament" ] = TemperamentEngine.calculate_temperament(chart)
        # Store aspects in a JSON-serializable format for auditability.
        # Split into "core" (septener-only) vs "shadow" (involving outer planets) to preserve metric purity.
        _aspects_raw = AspectEngine.calculate_aspects(chart)
        analysis["aspects_raw"] = _aspects_raw
        core_names = {
            PlanetName.SUN,
            PlanetName.MOON,
            PlanetName.MERCURY,
            PlanetName.VENUS,
            PlanetName.MARS,
            PlanetName.JUPITER,
            PlanetName.SATURN,
        }
        shadow_names = {PlanetName.URANUS, PlanetName.NEPTUNE, PlanetName.PLUTO}

        def _asp_to_dict(asp) -> Dict[str, Any]:
            return {
                "planet_a": asp.planet_a.value,
                "planet_b": asp.planet_b.value,
                "type": asp.type.value,
                "orb": float(asp.orb),
                "is_applying": bool(asp.is_applying),
                "text": asp.text,
            }

        try:
            core = []
            shadow = []
            for asp in _aspects_raw:
                a = asp.planet_a
                b = asp.planet_b
                if a in shadow_names or b in shadow_names:
                    shadow.append(_asp_to_dict(asp))
                elif a in core_names and b in core_names:
                    core.append(_asp_to_dict(asp))
                else:
                    # Ignore nodes/unsupported bodies for the report layer.
                    continue
            analysis["aspects"] = core
            analysis["aspects_shadow"] = shadow
        except Exception:
            analysis["aspects"] = []
            analysis["aspects_shadow"] = []
        analysis["medical"] = Auditor._calculate_medical_suite(chart, decumbiture_jd=decumbiture_jd)
        
        # 2. Advanced Suites
        analysis[ "advanced_mechanics" ] = {
            "almuten": analysis[ "dignity" ][ "almuten" ],
            "doryphory": Auditor._calculate_doryphory_details(chart),
            "mundane_context": MundaneEngine(jd, chart.geo_lat, chart.geo_lon).get_hierarchy_report(),
            "eclipse_charts": MundaneEngine(jd, chart.geo_lat, chart.geo_lon).eclipse_charts_for_native(chart.geo_lat, chart.geo_lon)
        }

        # 2b. Prenatal Syzygy + Natal Phase (auditable mechanics)
        try:
            import swisseph as swe
            from .calculations import calculate_prenatal_syzygy_details
            sun = next(p for p in chart.planets if p.name == PlanetName.SUN)
            moon = next(p for p in chart.planets if p.name == PlanetName.MOON)
            syz = calculate_prenatal_syzygy_details(chart.jd or 0.0)
            syz_lon = float(syz["longitude"])
            syz_type = str(syz["type"])
            moon_sun_phase = float((moon.longitude - sun.longitude) % 360.0)  # 0..360 from Sun to Moon
            # Minimal elongation (0..180): min(phase, 360-phase)
            natal_elong = moon_sun_phase if moon_sun_phase <= 180.0 else (360.0 - moon_sun_phase)
            is_waxing = moon_sun_phase < 180.0

            def _jd_to_utc_iso(jd_ut: float) -> str:
                y, m, d, h = swe.revjul(float(jd_ut))
                hh = int(h)
                mm_f = (h - hh) * 60.0
                mm = int(mm_f)
                ss = int(round((mm_f - mm) * 60.0))
                if ss == 60:
                    ss = 0
                    mm += 1
                if mm == 60:
                    mm = 0
                    hh = (hh + 1) % 24
                return f"{int(y):04d}-{int(m):02d}-{int(d):02d}T{hh:02d}:{mm:02d}:{ss:02d}Z"

            analysis["syzygy"] = {
                "prenatal_syzygy": {
                    "type": syz_type,
                    "jd_ut": syz.get("jd_ut"),
                    "datetime_utc": _jd_to_utc_iso(syz.get("jd_ut")) if syz.get("jd_ut") is not None else None,
                    "sun_longitude": syz.get("sun_longitude"),
                    "moon_longitude": syz.get("moon_longitude"),
                    "longitude": syz_lon,
                    "longitude_fmt": format_longitude(syz_lon),
                    "next_syzygy": {
                        "type": syz.get("next_syzygy", {}).get("type"),
                        "jd_ut": syz.get("next_syzygy", {}).get("jd_ut"),
                        "datetime_utc": _jd_to_utc_iso(syz.get("next_syzygy", {}).get("jd_ut"))
                        if syz.get("next_syzygy", {}).get("jd_ut") is not None
                        else None,
                        "sun_longitude": syz.get("next_syzygy", {}).get("sun_longitude"),
                        "moon_longitude": syz.get("next_syzygy", {}).get("moon_longitude"),
                        "longitude": syz.get("next_syzygy", {}).get("longitude"),
                        "longitude_fmt": format_longitude(syz.get("next_syzygy", {}).get("longitude", 0.0))
                        if syz.get("next_syzygy", {}).get("longitude") is not None
                        else None,
                    },
                    "note": syz.get("note"),
                },
                "natal_phase": {
                    # Minimal elongation (0..180). This is what most users mean by "elongation".
                    "moon_sun_elongation_deg": round(natal_elong, 6),
                    "moon_sun_elongation_min_deg": round(natal_elong, 6),
                    "moon_sun_phase_deg": round(moon_sun_phase, 6),
                    "is_waxing": bool(is_waxing),
                    "is_waning": bool(not is_waxing),
                    "note_elongation": "moon_sun_elongation_* is the minimal separation in degrees (0..180). Do not derive alternate values (e.g., 180-elongation).",
                    "note_phase": "moon_sun_phase_deg is measured from Sun to Moon (0..360). Waxing if <180; waning if >180.",
                    "note": "Elongation at birth is a separate quantity from the prenatal syzygy type.",
                },
            }
        except Exception:
            analysis["syzygy"] = {"note": "Syzygy/phase not available."}

        # 3. Supplemental Layers
        moon = next((p for p in chart.planets if p.name == PlanetName.MOON), None)
        analysis[ "supplemental" ] = {
            "lunar_mansion": LunarMansionEngine.get_lunar_mansion(moon.longitude) if moon else None,
            "stars": Auditor._calculate_star_impacts(chart),
            "nodes": Auditor._calculate_nodal_impacts(chart),
            "elements": Auditor._calculate_elemental_balance(chart),
            "hemispheres": Auditor._calculate_hemispheres(chart),
            "heliacal_events": PhasisEngine.calculate_heliacal_events(chart.jd, chart.geo_lat, chart.geo_lon) if hasattr(chart, "jd") else []
        }

        # Angle metadata (Whole Sign note): MC is an angle and may fall outside the 10th whole-sign house.
        try:
            asc_lon = float(chart.ascendant)
            mc_lon = float(chart.mc)
            asc_sign = list(Sign)[int(asc_lon / 30) % 12].value
            mc_sign = list(Sign)[int(mc_lon / 30) % 12].value
            mc_house_wsh = DignityCalculator.get_house_number(mc_lon, asc_lon, getattr(chart, "houses", None))
            analysis["angles"] = {
                "Ascendant": {"longitude": asc_lon, "longitude_fmt": format_longitude(asc_lon), "sign": asc_sign, "house_wsh": 1},
                "Midheaven": {"longitude": mc_lon, "longitude_fmt": format_longitude(mc_lon), "sign": mc_sign, "house_wsh": mc_house_wsh},
                "note": "Whole Sign Houses are used for house topics; MC is reported as an angle with its whole-sign house position."
            }
        except Exception:
            analysis["angles"] = {"note": "Angle metadata unavailable."}

        # 4. Temporal Layers
        if birth_dt and age is not None:
             analysis[ "solar_return" ] = Auditor._calculate_solar_return_summary(chart, birth_dt, age)
        
        # 5. Planetary Detail
        planets_forensic = Auditor._analyze_all_planets(chart, jd)

        # 6. Forensic Lots (Parents/Debt/Theft)
        forensic_lots = Auditor._calculate_forensic_lots(chart)
        analysis["forensic_lots"] = forensic_lots
        
        # 7. Enhanced Mechanics (Profections, Horary Physics)
        # Note: logic.py used manual profection calculation. We should use it for parity.
        # AdvancedPredictionEngine gives basic stuff, but logic.py had epitasis.
        profections = Auditor._calculate_enhanced_profections(chart, birth_dt, ans_date, age)
        analysis["enhanced_profections"] = profections
        
        horary_phys = Auditor._calculate_horary_physics(chart, age)
        analysis["horary_physics"] = horary_phys

        # 8. Universal Ledger (Source of Truth)
        rule_ledger = Auditor._generate_rule_ledger(
            chart=chart,
            planets_data=planets_forensic,
            active_directions=analysis["fate"].get("active_directions", []),
            stars=analysis["supplemental"].get("stars", []),
            hermetic_lots=analysis["fate"].get("hermetic_lots", {}),
            forensic_lots=forensic_lots,
            jd=jd
        )

        return {
            "analysis": analysis,
            "planets_forensic": planets_forensic,
            "rule_ledger": rule_ledger
        }

    @staticmethod
    def _calculate_doryphory_details(chart: Chart) -> List[Dict]:
        dory = DoryphoryEngine.check_doryphory(chart)
        sun = next((p for p in chart.planets if p.name == PlanetName.SUN), None)
        moon = next((p for p in chart.planets if p.name == PlanetName.MOON), None)
        out: List[Dict] = []

        def _same_sign(a: float, b: float) -> bool:
            return int(a / 30.0) % 12 == int(b / 30.0) % 12

        for d in dory:
            p = next((pp for pp in chart.planets if pp.name == d.planet), None)
            if not p:
                continue

            lum = sun if d.related_luminary == "Sun" else moon
            lum_lon = float(lum.longitude) if lum else None
            p_lon = float(p.longitude)

            # Basic delta for auditability (not used for house judgment).
            delta = None
            if lum_lon is not None:
                if d.related_luminary == "Sun":
                    delta = float((lum_lon - p_lon) % 360.0)  # positive if planet precedes Sun
                else:
                    delta = float((p_lon - lum_lon) % 360.0)  # positive if planet follows Moon

            out.append(
                {
                    "luminary": d.related_luminary,
                    "guard": d.planet.value,
                    "type": d.type,
                    "score": d.score,
                    "guard_longitude": p_lon,
                    "guard_longitude_fmt": format_longitude(p_lon),
                    "luminary_longitude": lum_lon,
                    "luminary_longitude_fmt": format_longitude(lum_lon) if lum_lon is not None else None,
                    "delta_deg": round(delta, 6) if delta is not None else None,
                    "same_sign": _same_sign(p_lon, lum_lon) if lum_lon is not None else None,
                    "note": "Doryphory instances are computed by DoryphoryEngine (Type 3 bodily rules + same-sign nuance).",
                }
            )

        return out

    @staticmethod
    def _calculate_star_impacts(chart: Chart) -> List[Any]:
        from .stars import check_fixed_stars
        contacts = check_fixed_stars(chart)
        # Ensure JSON-serializable payload (avoid dataclass repr strings in reports).
        try:
            from dataclasses import is_dataclass, asdict
            out = []
            for c in contacts:
                if is_dataclass(c):
                    out.append(asdict(c))
                elif isinstance(c, dict):
                    out.append(c)
                else:
                    out.append({"value": str(c)})
            return out
        except Exception:
            return [{"value": str(c)} for c in contacts]

    @staticmethod
    def _calculate_nodal_impacts(chart: Chart) -> List[Any]:
        from .nodes import analyze_nodes
        return analyze_nodes(chart)

    @staticmethod
    def _calculate_elemental_balance(chart: Chart) -> Dict[str, int]:
        elements = {"FIRE": 0, "EARTH": 0, "AIR": 0, "WATER": 0}
        for p in chart.planets:
            if p.name in [PlanetName.URANUS, PlanetName.NEPTUNE, PlanetName.PLUTO]: continue
            sign_idx = int(p.longitude / 30) % 12
            sign = list(Sign)[sign_idx]
            el = DignityCalculator.ZODIAC_ELEMENTS.get(sign)
            if el: elements[el] += 1
        return elements

    @staticmethod
    def _calculate_hemispheres(chart: Chart) -> Dict:
        hemi = {"East": 0, "West": 0, "North": 0, "South": 0}
        for p in chart.planets:
            if p.name in [PlanetName.URANUS, PlanetName.NEPTUNE, PlanetName.PLUTO]: continue
            
            # House-based hemisphere logic (Simple Whole Sign/Equal-ish proxy)
            # 10,11,12,1,2,3 -> East
            # 4,5,6,7,8,9 -> West
            # 7,8,9,10,11,12 -> South (Above Horizon)
            # 1,2,3,4,5,6 -> North (Below Horizon)
            h = DignityCalculator.get_house_number(p.longitude, chart.ascendant, chart.houses)
            if h in [10, 11, 12, 1, 2, 3]: hemi["East"] += 1
            else: hemi["West"] += 1
            
            if h in [7, 8, 9, 10, 11, 12]: hemi["South"] += 1
            else: hemi["North"] += 1
            
        return {
            "counts": hemi,
            "focus": {
                "orientation": "Self-Determination (East)" if hemi["East"] > hemi["West"] else "Other-Oriented (West)",
                "visibility": "Public/Objective (South)" if hemi["South"] > hemi["North"] else "Private/Subjective (North)"
            }
        }

    @staticmethod
    def _calculate_solar_return_summary(chart: Chart, birth_dt: datetime, age: int) -> Dict:
        try:
            current_yr = birth_dt.year + age
            sun = next(p for p in chart.planets if p.name == PlanetName.SUN)
            sr_jd = calculate_solar_return_jd(sun.longitude, chart.jd, current_yr)
            
            # Simple wrapper to match expected logic
            return SolarReturnEngine.analyze_solar_return_from_jd(chart, sr_jd, age, birth_dt)
        except Exception as e:
            logger.error(f"Solar Return calculation failed: {e}")
            return {"error": "Solar Return calculation failed"}

    @staticmethod
    def _calculate_forensic_lots(chart: Chart) -> Dict:
        """
        Calculates specific forensic lots (Debt, Theft, Accusation, Parents) and verifies affliction.
        """
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
        all_lots = calculate_all_lots(chart, sect)
        
        mars_p = next((p for p in chart.planets if p.name == PlanetName.MARS), None)
        saturn_p = next((p for p in chart.planets if p.name == PlanetName.SATURN), None)
        
        def _enrich(lon):
            if lon is None: return None
            sign_idx = int(lon / 30) % 12
            sign = list(Sign)[sign_idx]
            house = DignityCalculator.get_house_number(lon, chart.ascendant, chart.houses)
            return {"longitude": lon, "sign": sign.value, "house": house}

        def _is_afflicted_by(lot_lon, malefic_lon, orb=3.0):
            if lot_lon is None or malefic_lon is None: return False
            dist = abs(lot_lon - malefic_lon) % 360
            if dist > 180: dist = 360 - dist
            return dist <= orb

        report = {}
        
        # 1. Debt
        debt_lon = all_lots.get(LotName.DEBT.value)
        report["Debt/Bankruptcy"] = {
            "data": _enrich(debt_lon),
            "status": "AFFLICTED" if mars_p and _is_afflicted_by(debt_lon, mars_p.longitude) else "Clear",
            "verification": "Mars contact signifies aggressive debt or sudden bankruptcy."
        }
        
        # 2. Theft
        theft_lon = all_lots.get(LotName.THEFT.value)
        report["Theft"] = {
            "data": _enrich(theft_lon),
            "status": "AFFLICTED" if mars_p and _is_afflicted_by(theft_lon, mars_p.longitude) else "Clear",
            "verification": "Mars contact signifies loss through theft or violence."
        }
        
        # 3. Accusation
        acc_lon = all_lots.get(LotName.ACCUSATION.value)
        report["Accusation"] = {
            "data": _enrich(acc_lon),
            "status": "AFFLICTED" if saturn_p and _is_afflicted_by(acc_lon, saturn_p.longitude) else "Clear",
            "verification": "Saturn contact signifies legal entrapment or false witness."
        }
        
        # 4. Parents
        for parent, name in [(LotName.FATHER, "Father"), (LotName.MOTHER, "Mother")]:
            p_lon = all_lots.get(parent.value)
            if p_lon is not None:
                ruler_name = DignityCalculator.get_essential_rulers(p_lon, sect)["domicile"]
                ruler = next((p for p in chart.planets if p.name == ruler_name), None)
                status = "Neutral"
                verif = f"Ruler {ruler_name.value} condition is average."
                if ruler:
                    score = DignityCalculator.calculate_planet_dignity(ruler.name, ruler.longitude, sect)["total_score"]
                    if score >= 3:
                        status = "STRONG"
                        verif = f"Ruler {ruler_name.value} is well-dignified (Score: {score})."
                    elif score <= -3:
                        status = "WEAK"
                        verif = f"Ruler {ruler_name.value} is debilitated (Score: {score})."
                report[name] = {"data": _enrich(p_lon), "status": status, "verification": verif}
                
        return report

    @staticmethod
    def _calculate_horary_physics(chart: Chart, age: int) -> Dict:
        if age is None: return {}
        asc_sign_idx = int(chart.ascendant / 30) % 12
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
        
        # Ascendant Ruler (L1)
        # Note: Logic.py used 'domicile' from essential rulers
        essentials = DignityCalculator.get_essential_rulers(chart.ascendant, sect)
        asc_lord_name = essentials["domicile"]
        
        # Lord of Year
        annual_sign = calculate_profection_sign(list(Sign)[asc_sign_idx], age)
        loy_lord_name = get_lord_of_year(annual_sign)
        
        return {
            "significators": f"{asc_lord_name.value} (L1) and {loy_lord_name.value} (LoY)",
            "interactions": analyze_horary_physics(asc_lord_name, loy_lord_name, chart)
        }

    @staticmethod
    def _calculate_enhanced_profections(chart: Chart, birth_dt: Optional[datetime], ans_date: datetime, age: int) -> Dict:
        if age is None: return {}
        asc_sign_idx = int(chart.ascendant / 30) % 12
        signs = list(Sign)
        
        # Annual
        annual_index = (asc_sign_idx + age) % 12
        annual_sign = signs[annual_index]
        loy_name = get_lord_of_year(annual_sign)
        
        # Monthly & Daily Defaults
        month = 1
        day = 1
        
        if birth_dt and ans_date:
            try:
                # Logic: Calculate profection month (1-12) and day (1-30)
                m_diff = (ans_date.year - birth_dt.year) * 12 + (ans_date.month - birth_dt.month)
                if ans_date.day < birth_dt.day:
                    m_diff -= 1
                month = (m_diff % 12) + 1
                
                day_diff = (ans_date.day - birth_dt.day)
                if day_diff < 0: day_diff += 30
                day = day_diff + 1
            except:
                pass

        # Monthly (Continuous)
        monthly_cont_index = (annual_index + (month - 1)) % 12
        monthly_sign_cont = signs[monthly_cont_index]
        
        # Monthly (Saltatory)
        total_months = (age * 12) + (month - 1)
        monthly_salt_index = (asc_sign_idx + total_months) % 12
        monthly_sign_salt = signs[monthly_salt_index]
        
        # Daily
        daily_rate = 7 / 3
        daily_steps = int((day - 1) / daily_rate)
        daily_index = (monthly_cont_index + daily_steps) % 12
        daily_sign = signs[daily_index]
        
        # LOY Natal Position — which house does the Lord of Year occupy?
        loy_planet = next((p for p in chart.planets if p.name == loy_name), None)
        loy_natal_house = None
        loy_natal_sign = None
        loy_retrograde = False
        loy_dignities_summary = ""
        if loy_planet:
            loy_natal_house = DignityCalculator.get_house_number(
                loy_planet.longitude, chart.ascendant, getattr(chart, "houses", None)
            )
            loy_natal_sign = signs[int(loy_planet.longitude / 30) % 12].value
            loy_retrograde = getattr(loy_planet, "speed", 1.0) < 0
            
            # Essential dignity check
            sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
            rulers = DignityCalculator.get_essential_rulers(loy_planet.longitude, sect)
            if rulers.get("domicile") == loy_name:
                loy_dignities_summary = "Domicile"
            elif rulers.get("exaltation") == loy_name:
                loy_dignities_summary = "Exaltation"
            elif rulers.get("triplicity") == loy_name:
                loy_dignities_summary = "Triplicity"
            elif rulers.get("term") == loy_name:
                loy_dignities_summary = "Term"
            elif rulers.get("face") == loy_name:
                loy_dignities_summary = "Face"
            else:
                loy_dignities_summary = "Peregrine"
        
        # Epitasis
        epitasis_days = []
        if loy_planet:
            epitasis_days = calculate_epitasis_days(monthly_sign_cont, loy_planet.sign)
            
        return {
            "annual_sign": annual_sign.value,
            "lord_of_year": loy_name.value,
            "lord_of_year_natal": {
                "house": loy_natal_house,
                "sign": loy_natal_sign,
                "retrograde": loy_retrograde,
                "dignity": loy_dignities_summary,
            },
            "monthly_sign": {
                "continuous": monthly_sign_cont.value,
                "saltatory": monthly_sign_salt.value
            },
            "daily_sign": daily_sign.value,
            "epitasis_days": epitasis_days,
            "age": age, "month": month, "day": day
        }

    @staticmethod
    def _generate_rule_ledger(
        chart: Chart, 
        planets_data: List[Dict], 
        active_directions: List[Dict], 
        stars: List[Any], 
        hermetic_lots: Dict, 
        forensic_lots: Dict, 
        jd: float
    ) -> List[Dict]:
        """
        Generates the Source of Truth Rule Ledger.
        """
        ledger = []
        rule_counts = {}

        def _uid(base):
            c = rule_counts.get(base, 0) + 1
            rule_counts[base] = c
            return f"{base}-{c}" if c > 1 else base

        # 1. Planets
        for p_data in planets_data:
            p_label = p_data.get("name", "Planet")
            base_trace = [f"Planet: {p_label}", f"Sign: {p_data.get('sign')}"]
            
            # Dignity
            dig = p_data.get("dignities", {})
            if dig:
                score = dig.get("total_score", 0)
                ledger.append({
                    "id": _uid(f"{p_label.lower()}-dignity"),
                    "category": "Essential Dignity",
                    "condition": f"{p_label} in {p_data.get('sign')}",
                    "judgment": f"Score: {score}. " + ", ".join([f"{k}: {v}" for k,v in dig.get("breakdown", {}).items()]),
                    "sources": ["Ptolemy, Tetrabiblos", "Dorotheus"],
                    "confidence": 90,
                    "conflicts": [],
                    "trace": base_trace
                })
            
            # Impacts
            for imp in p_data.get("impacts", []):
                cause = imp.get("cause")
                effect = imp.get("effect")
                sources = _resolve_sources(cause, "")
                ledger.append({
                    "id": _uid(f"{p_label.lower()}-{_slugify(cause)}"),
                    "category": "Condition",
                    "condition": f"{p_label}: {cause}",
                    "judgment": effect,
                    "sources": sources,
                    "confidence": _estimate_confidence(sources, [], base=75),
                    "conflicts": [],
                    "trace": base_trace + [f"Cause: {cause}"]
                })

            # Delineation
            if "delineation" in p_data:
                 sources = _extract_sources(p_data["delineation"])
                 ledger.append({
                    "id": _uid(f"{p_label.lower()}-delineation"),
                    "category": "Planet Delineation",
                    "condition": f"{p_label} in {p_data.get('sign')}",
                    "judgment": str(p_data["delineation"])[:150] + "...",
                    "sources": sources,
                    "confidence": 70,
                    "conflicts": [],
                    "trace": base_trace
                 })
                 
            # Classical - Monomoiria/Dodecatemoria if available in future
            if "classical" in p_data:
                mono = p_data["classical"].get("monomoiria")
                if mono:
                    ledger.append({
                        "id": _uid(f"{p_label.lower()}-monomoiria"),
                        "category": "Monomoiria",
                        "condition": f"{p_label} Degree Ruler",
                        "judgment": f"Zoidion: {mono.get('zoidion_ruler')}",
                        "sources": ["Paul of Alexandria"],
                        "confidence": 85,
                        "conflicts": [],
                        "trace": base_trace
                    })
                dodec = p_data["classical"].get("dodecatemoria")
                if dodec and isinstance(dodec, dict):
                    val = dodec.get("valens") or {}
                    if val:
                        ledger.append({
                            "id": _uid(f"{p_label.lower()}-dodecatemoria"),
                            "category": "Dodecatemoria",
                            "condition": f"{p_label} Twelfth-Part (Valens)",
                            "judgment": f"{val.get('sign')} (House {val.get('house')})",
                            "sources": ["Valens", "Paul of Alexandria"],
                            "confidence": 80,
                            "conflicts": [],
                            "trace": base_trace
                        })

        # 2. Directions
        for d in active_directions:
            ledger.append({
                "id": _uid(f"direction-{_slugify(str(d.get('promittor', '')))}-{_slugify(str(d.get('aspect', '')))}"),
                "category": "Primary Direction",
                "condition": f"Directed {d.get('significator')} to {d.get('promittor')}",
                "judgment": f"Arc {d.get('arc')}: {d.get('aspect')}",
                "sources": ["Ptolemy", "Placidus"],
                "confidence": 85,
                "conflicts": [],
                "trace": [f"Year: {d.get('years')}"]
            })

        # 3. Stars
        for s in stars:
            s_name = s.star_name if hasattr(s, "star_name") else s.get("star_name")
            p_name = s.planet_name if hasattr(s, "planet_name") else s.get("planet_name")
            msg = s.message if hasattr(s, "message") else s.get("message")
            ledger.append({
                "id": _uid(f"star-{_slugify(str(s_name))}"),
                "category": "Fixed Star",
                "condition": f"{s_name} + {p_name}",
                "judgment": msg,
                "sources": ["Anonymous of 379", "Brady"],
                "confidence": 90,
                "conflicts": [],
                "trace": []
            })
            
        # 4. Forensic Lots
        for k, v in forensic_lots.items():
            if v.get("status") != "Clear":
                 ledger.append({
                    "id": _uid(f"lot-{_slugify(k)}"),
                    "category": "Forensic Lot",
                    "condition": f"Lot of {k}",
                    "judgment": v.get("verification"),
                    "sources": ["Bonatti", "Valens"],
                    "confidence": 85,
                    "conflicts": [],
                    "trace": [f"Status: {v.get('status')}"]
                 })

        # 5. Eclipses
        if jd > 0:
            eclipses = get_recent_eclipses(jd)
            for lot_name, lot_data in hermetic_lots.items():
                lon = lot_data
                if isinstance(lot_data, dict): lon = lot_data.get("longitude")
                
                if isinstance(lon, (int, float)):
                    for ec in eclipses:
                        if check_eclipse_impact(lon, ec["longitude"]):
                             ledger.append({
                                "id": _uid(f"eclipse-{_slugify(lot_name)}"),
                                "category": "Universal Override",
                                "condition": f"Eclipse impacting Lot of {lot_name}",
                                "judgment": "Suspended Promise: Area under universal pressure.",
                                "sources": ["Ptolemy II"],
                                "confidence": 92,
                                "conflicts": [],
                                "trace": [f"Eclipse JD: {ec['jd']}"]
                             })

        return ledger
        
    @staticmethod
    def _rebuild_chart_model(raw_data: Dict) -> Chart:
        planets = []
        for name, p_data in raw_data["planets"].items():
            planets.append(Planet(
                name=PlanetName(name),
                longitude=p_data["longitude"],
                latitude=p_data.get("latitude", 0.0),
                speed=p_data.get("speed", 0.0)
            ))
        
        # Extract Sun Altitude (Required for Sect)
        sun_data = raw_data["planets"].get("Sun", {})
        sun_altitude = sun_data.get("altitude", 0.0)

        # Extract Angles
        angles = raw_data.get("angles", {})
        ascendant = angles.get("Ascendant", 0.0)
        mc = angles.get("MC", 0.0)

        return Chart(
            sun_altitude=sun_altitude,
            planets=planets,
            ascendant=ascendant,
            mc=mc,
            geo_lat=raw_data["meta"]["lat"],
            geo_lon=raw_data["meta"]["lon"],
            jd=raw_data["meta"]["julian_day"],
            houses=raw_data["houses"]
        )

    @staticmethod
    def _calculate_dignity_suite(chart: Chart) -> Dict:
        almuten_data = AlmutenEngine.calculate_almuten(chart)
        geniture = LordOfGenitureEngine.calculate(chart)
        scores = {}
        winner = "Unknown"
        winner_score = 0
        
        if almuten_data:
            winner = almuten_data.winner.value
            for k, v in almuten_data.scores.items():
                scores[k] = v.total_score
            winner_score = scores.get(winner, 0)

        return {
            "almuten": {
                "winner": winner,
                "score": winner_score,
                "breakdown": scores
            },
            "lord_of_geniture": geniture,
            "doryphory": [d.planet.value for d in DoryphoryEngine.check_doryphory(chart)]
        }

    @staticmethod
    def _calculate_fate_suite(chart: Chart, birth_dt: Optional[datetime], ans_date: datetime) -> Dict:
        # Hermetic Lots
        lots = HermeticLotEngine.calculate_all_lots(chart)
        
        # Predictive Engines
        bdt = birth_dt or datetime.now()
        
        # Calculate Age Calculation for Directions
        age_years = (ans_date - bdt).days / 365.25
        if age_years < 0: age_years = 0

        # 1. Primary Directions
        directions = PrimaryDirectionsEngine.calculate_directions_to_angles(chart, chart.geo_lat)
        planet_directions = PrimaryDirectionsEngine.calculate_directions_to_planets(chart, chart.geo_lat)
        distributor = PrimaryDirectionsEngine.calculate_current_distributor(chart, age_years, chart.geo_lat)
        
        # Serialize and Filter Active (for Ledger)
        p_dirs_json = []
        active_dirs = []
        for d in directions:
            d_json = {
                "significator": d.significator,
                "promittor": d.promittor,
                "aspect": d.aspect,
                "arc": d.arc,
                "years": d.years,
                "date_offset": d.date_offset,
                "method": d.method,
                "key": "Ptolemy (1 degree = 1 year)",
                "notes": "Zodiacal primary direction using oblique ascension (OA) of zodiacal aspect points (lat=0 for aspect point).",
            }
            p_dirs_json.append(d_json)
            # Active if within 1 year of current age
            if abs(d.years - age_years) <= 1.0:
                 active_dirs.append(d_json)

        # 2. Advanced Prediction (Transits, Firdaria, Profections)
        predictor = AdvancedPredictionEngine(
            chart, bdt, chart.jd, chart.geo_lat, chart.geo_lon
        )
        prediction_report = predictor.get_prediction_report(ans_date)

        return {
            "hermetic_lots": lots,
            "primary_directions": p_dirs_json,
            "planet_to_planet_directions": [{"significator": d.significator, "promittor": d.promittor, "aspect": d.aspect, "arc": d.arc, "years": d.years, "date_offset": d.date_offset} for d in planet_directions],
            "primary_direction_distributor": distributor,
            "circumambulations": PrimaryDirectionsEngine.calculate_circumambulations(chart, chart.geo_lat),
            "active_directions": active_dirs,
            "profections": prediction_report.get("profections", {}),
            "firdaria": prediction_report.get("firdaria", {}),
            "solar_return": prediction_report.get("solar_return_info", {}),
            "muntha": prediction_report.get("muntha", {}),
            "transits": prediction_report.get("transits", []),
            "decennials": DecennialEngine.generate_decennials(chart, bdt) if bdt else []
        }

    @staticmethod
    def _calculate_medical_suite(chart: Chart, decumbiture_jd: Optional[float] = None) -> Dict:
        asc_sign = list(Sign)[int(chart.ascendant / 30) % 12]
        governed_part = MedicalAstrology.get_body_part_for_sign(asc_sign)
        critical_days = None
        critical_note = "Not calculable from natal data alone. Provide decumbiture (illness onset) date/time to compute."
        if decumbiture_jd:
            try:
                critical_days = DecumbitureEngine.calculate_critical_days(decumbiture_jd)
                critical_note = "Calculated from decumbiture (illness onset) Moon motion."
            except Exception as e:
                critical_days = None
                critical_note = f"Critical days calculation failed: {e}"
        return {
            "constitution": governed_part,
            "distemper": DecumbitureEngine.analyze_distemper(asc_sign),
            "critical_days": critical_days,
            "critical_days_note": critical_note,
            "surgery_risk": MedicalAstrology.can_perform_surgery(
                governed_part,
                chart.jd,
                chart
            )
        }

    @staticmethod
    def _calculate_vitality_suite(chart: Chart, age_years: Optional[float] = None) -> Dict[str, Any]:
        """
        Vitality Trinity: Hyleg (giver of life), Alcocoden (giver of years), Anareta (killing planet).
        Output is strictly technical for auditability.
        """
        hyleg = HylegAlcocodenEngine.determine_hyleg(chart)

        alc_valens = HylegAlcocodenEngine.determine_alcocoden(hyleg, chart, method="valens_term") if hyleg else None
        alc_bonatti = HylegAlcocodenEngine.determine_alcocoden(hyleg, chart, method="bonatti_points") if hyleg else None

        # Keep both computations: different traditions can yield different alchochoden choices.
        lifespan_valens = (
            HylegAlcocodenEngine.calculate_lifespan(hyleg, alc_valens, chart)
            if hyleg and alc_valens
            else {"total_years": 0, "breakdown": ["No Alcocoden found (Valens term method)."]}
        )
        lifespan_bonatti = (
            HylegAlcocodenEngine.calculate_lifespan(hyleg, alc_bonatti, chart)
            if hyleg and alc_bonatti
            else {"total_years": 0, "breakdown": ["No Alcocoden found (Bonatti/Lilly points method)."]}
        )

        # Sanity guard: if a computed "years" figure is less than the native's current age,
        # it cannot be presented as a literal longevity value. Mark it invalid and scrub the number.
        def _sanitize_years(label: str, payload: Dict[str, Any]) -> Dict[str, Any]:
            try:
                if age_years is None:
                    return payload
                total = payload.get("total_years")
                if total is None:
                    return payload
                total_f = float(total)
                if total_f + 1e-9 < float(age_years):
                    out = dict(payload)
                    out["invalid_under_sanity"] = True
                    out["total_years"] = None
                    bd = list(out.get("breakdown") or [])
                    # Redact numeric detail to prevent downstream consumers from presenting a bogus
                    # "death age" that is already falsified by current age.
                    try:
                        import re
                        bd = [re.sub(r"[-+]?\\d+(?:\\.\\d+)?", "[REDACTED]", str(x)) for x in bd]
                    except Exception:
                        bd = [str(x) for x in bd]
                    bd.append(
                        "SANITY: this method produced a years figure that is less than the native's current age. "
                        "The numeric output has been scrubbed; do NOT read as length-of-life. "
                        "Treat as a failed/misapplied variant or an early-life vulnerability indicator requiring rectification "
                        "and primary-direction validation."
                    )
                    out["breakdown"] = bd
                    return out
            except Exception:
                return payload
            return payload

        lifespan_valens = _sanitize_years("valens_term", lifespan_valens)
        lifespan_bonatti = _sanitize_years("bonatti_points", lifespan_bonatti)

        # Choose a default for downstream consumers (Bonatti tends to be more permissive/robust).
        alc = alc_bonatti or alc_valens
        lifespan = lifespan_bonatti if alc_bonatti else lifespan_valens
        anareta = HylegAlcocodenEngine.determine_anareta(hyleg, chart) if hyleg else {"name": None, "reason": "No Hyleg available."}

        # Primary Directions "hits" to the Hyleg degree (technical).
        #
        # NOTE: Older report layers called this the "Interfector" and used "executioner" language.
        # That wording is interpretive and causes confusion when benefics/Almuten are involved.
        # We output a neutral payload and separately derive a conservative "anaretic windows" list.
        directed_hits_to_hyleg = {"active_hard_hit": None, "candidates": [], "note": "Not calculated (missing hyleg or age)."}
        anaretic_windows = {
            "candidates": [],
            "criteria": {
                "promittors": ["Mars", "Saturn"],
                "aspects": ["Conjunction", "Square", "Opposition"],
            },
            "note": (
                "Anaretic windows are a conservative technical flag: malefic hard primary-direction hits "
                "to the Hyleg degree. This is NOT a death prediction. Treat as a period requiring stricter "
                "risk management and remediation (historical symbolism)."
            ),
        }
        try:
            if hyleg and "longitude" in hyleg:
                dirs = PrimaryDirectionsEngine.calculate_directions_to_point(
                    chart=chart,
                    geo_lat=chart.geo_lat,
                    target_lon=hyleg["longitude"],
                    target_label=f"Hyleg ({hyleg.get('name')})"
                )
                dirs_json = [
                    {
                        "significator": d.significator,
                        "promittor": d.promittor,
                        "aspect": d.aspect,
                        "arc": d.arc,
                        "years": d.years,
                        "date_offset": d.date_offset,
                        "method": d.method,
                    }
                    for d in dirs
                ]

                # Nearest hard hit to the native's current age (if age is known).
                active_hard = None
                if age_years is not None and dirs_json:
                    hard = [
                        d for d in dirs_json
                        if (d.get("aspect") or "") in ["Conjunction", "Square", "Opposition"]
                    ]
                    if hard:
                        active_hard = min(hard, key=lambda x: abs((x.get("years") or 0) - age_years))

                directed_hits_to_hyleg = {
                    "active_hard_hit": active_hard,
                    "candidates": dirs_json[:25],
                    "note": (
                        "Primary-direction promittors striking the Hyleg degree (zodiacal/OA method). "
                        "This payload is technical; do not personify as an 'executioner'."
                    ),
                }

                # Conservative anaretic windows: malefic hard hits only.
                anaretic_windows["candidates"] = [
                    d for d in dirs_json
                    if (d.get("promittor") in ["Mars", "Saturn"])
                    and (d.get("aspect") in ["Conjunction", "Square", "Opposition"])
                ]
        except Exception as e:
            directed_hits_to_hyleg = {"active_hard_hit": None, "candidates": [], "note": f"Primary-direction hit calculation failed: {e}"}
            anaretic_windows["note"] = f"{anaretic_windows.get('note')} (Derivation failed: {e})"

        alc_name = None
        if alc and isinstance(alc, dict):
            pn = alc.get("name")
            alc_name = pn.value if hasattr(pn, "value") else (str(pn) if pn else None)

        return {
            "hyleg": hyleg,
            "alcocoden": {"name": alc_name},
            "alcocoden_methods": {
                "valens_term": {
                    "name": (alc_valens.get("name").value if hasattr(alc_valens.get("name"), "value") else str(alc_valens.get("name")))
                    if isinstance(alc_valens, dict) and alc_valens.get("name") is not None
                    else None,
                    "details": alc_valens,
                },
                "bonatti_points": {
                    "name": (alc_bonatti.get("name").value if hasattr(alc_bonatti.get("name"), "value") else str(alc_bonatti.get("name")))
                    if isinstance(alc_bonatti, dict) and alc_bonatti.get("name") is not None
                    else None,
                    "details": alc_bonatti,
                },
                "note": "Multiple longevity traditions exist. This engine reports both Valens-term and Bonatti/Lilly-points candidates.",
            },
            "years_capacity": {
                "default": lifespan,
                "valens_term": lifespan_valens,
                "bonatti_points": lifespan_bonatti,
                "note": "Traditional years computations; not a literal life expectancy. Cross-validate with Primary Directions and documented accidents.",
            },
            "years_capacity_sanity": {
                "age_years": age_years,
                "valens_term_lt_age": (
                    (lifespan_valens.get("total_years") is not None and float(lifespan_valens.get("total_years")) < float(age_years))
                    if age_years is not None
                    else None
                ),
                "bonatti_points_lt_age": (
                    (lifespan_bonatti.get("total_years") is not None and float(lifespan_bonatti.get("total_years")) < float(age_years))
                    if age_years is not None
                    else None
                ),
                "note": "If a computed years figure is less than the native's current age, it cannot be read as a literal 'length of life'. Treat it as a failed/misapplied variant or as an early-life vulnerability indicator requiring rectification and primary-direction validation.",
            },
            "anareta": anareta,
            "directed_hits_to_hyleg": directed_hits_to_hyleg,
            "anaretic_windows": anaretic_windows,
            # Back-compat for existing prompts/consumers. Deprecated: prefer `directed_hits_to_hyleg`.
            "interfector": {
                "active": directed_hits_to_hyleg.get("active_hard_hit"),
                "candidates": directed_hits_to_hyleg.get("candidates"),
                "note": "DEPRECATED: use `directed_hits_to_hyleg`. Older layers used 'Interfector'/'Executioner' wording; avoid that framing.",
            },
            "note": "Historical vitality/longevity technique. Not medical advice."
        }

    @staticmethod
    def _calculate_triplicity_periods(chart: Chart) -> Dict[str, Any]:
        """
        Dorothean Triplicity Periods: life divided into three chapters ruled by the triplicity rulers
        of the sect light's element (early/middle/late).
        """
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
        sun = next((p for p in chart.planets if p.name == PlanetName.SUN), None)
        moon = next((p for p in chart.planets if p.name == PlanetName.MOON), None)
        sect_light = sun if sect == Sect.DAY else moon
        if not sect_light:
            return {"error": "Sect light not found."}

        sign_idx = int(sect_light.longitude / 30) % 12
        sign = list(Sign)[sign_idx]
        element = DignityCalculator.ZODIAC_ELEMENTS.get(sign)
        rulers = DignityCalculator.TRIPLICITY_RULERS.get(element) if element else None
        if not rulers:
            return {"error": "Triplicity rulers not available."}

        # Dorothean tuple is (day, night, participant). Order differs by sect.
        day_r, night_r, part_r = rulers[0], rulers[1], rulers[2]
        if sect == Sect.DAY:
            order = [day_r, night_r, part_r]
        else:
            order = [night_r, day_r, part_r]

        return {
            "sect": sect.value,
            "sect_light": sect_light.name.value,
            "sect_light_sign": sign.value,
            "element": element,
            "chapters": {
                "early_life_ruler": order[0].value,
                "middle_life_ruler": order[1].value,
                "late_life_ruler": order[2].value,
            },
            "all_rulers": [r.value for r in order],
            "method": "Dorothean Triplicity Periods (3 rulers: day/night/participant; ordered by sect)"
        }

    @staticmethod
    def _calculate_teams_and_reception(chart: Chart) -> Dict:
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
        receptions = ReceptionEngine.calculate_mutual_receptions(chart, ReceptionMode.STANDARD_LILLY)
        
        constructive = []
        destructive = []
        for p in chart.planets:
            if p.name in [PlanetName.URANUS, PlanetName.NEPTUNE, PlanetName.PLUTO]: continue
            
            if sect == Sect.DAY:
                if p.name in [PlanetName.SUN, PlanetName.JUPITER, PlanetName.SATURN]: constructive.append(p.name.value)
                elif p.name in [PlanetName.MARS]: destructive.append(p.name.value)
            else:
                if p.name in [PlanetName.MOON, PlanetName.VENUS, PlanetName.MARS]: constructive.append(p.name.value)
                elif p.name in [PlanetName.SATURN]: destructive.append(p.name.value)

        def _planet_sign(pn: PlanetName) -> str:
            p = next((x for x in chart.planets if x.name == pn), None)
            return p.sign.value if p else "Unknown"

        def _rec_payload(r) -> Dict[str, object]:
            # r is a Reception dataclass
            return {
                "guest": r.guest.value,
                "host": r.host.value,
                "dignities": list(r.dignities),
                "score": r.score,
                "is_valid": r.is_valid,
                "is_operative": r.is_operative,
                "mode": r.mode,
                "mitigation": r.mitigation,
            }

        return {
            "constructive_team": constructive,
            "destructive_team": destructive,
            "receptions": [{
                "planet_a": r.planet_a.value,
                "planet_b": r.planet_b.value,
                "type": r.type,
                "score": r.strength_score,
                # Make reception claims formally correct and auditable:
                # A is "guest" in B's place; B receives A by dignities in that sign.
                "a_in_b": _rec_payload(r.reception_a_in_b),
                "b_in_a": _rec_payload(r.reception_b_in_a),
                "planet_a_sign": _planet_sign(r.planet_a),
                "planet_b_sign": _planet_sign(r.planet_b),
            } for r in receptions]
        }

    @staticmethod
    def _analyze_all_planets(chart: Chart, jd: float) -> List[Dict]:
        results = []
        speculum = {} 
        for p in chart.planets:
            if p.name in [PlanetName.URANUS, PlanetName.NEPTUNE, PlanetName.PLUTO]:
                continue
            
            p_data = Auditor._analyze_single_planet(p, chart, jd, speculum)
            results.append(p_data)
        return results

    @staticmethod
    def _analyze_single_planet(planet: Planet, chart: Chart, jd: float, speculum: Dict) -> Dict:
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
        sun = next(p for p in chart.planets if p.name == PlanetName.SUN)
        moon = next((p for p in chart.planets if p.name == PlanetName.MOON), None)
        house_num = DignityCalculator.get_house_number(planet.longitude, chart.ascendant, getattr(chart, "houses", None))
        essentials = DignityCalculator.get_essential_rulers(planet.longitude, sect)

        # Monomoiria and Dodecatemoria are "secret chart" layers used for remediation and hidden condition checks.
        asc_sign = list(Sign)[int(chart.ascendant / 30) % 12]
        sun_sign = list(Sign)[int(sun.longitude / 30) % 12]
        moon_sign = list(Sign)[int(moon.longitude / 30) % 12] if moon else asc_sign
        is_day = sect == Sect.DAY

        zoidion_mono = MonomoiriaEngine.get_zoidion_monomoiria(planet.longitude)
        trigonal_mono = MonomoiriaEngine.get_trigonal_monomoiria(planet.longitude, is_day, sun_sign, moon_sign)

        dodec_val_lon = DodecatemoriaEngine.calculate_dodecatemoria_valens(planet.longitude)
        dodec_paul_lon = DodecatemoriaEngine.calculate_dodecatemoria_paul(planet.longitude)

        def _dodec_payload(lon: float, method: str) -> Dict[str, object]:
            s = list(Sign)[int(lon / 30) % 12]
            h = DignityCalculator.get_house_number(lon, chart.ascendant, getattr(chart, "houses", None))
            # Use Egyptian terms for consistency with the broader engine unless explicitly requested otherwise.
            term_ruler = DignityCalculator.get_essential_rulers(lon, sect).get("term")
            return {
                "method": method,
                "longitude": lon,
                "longitude_fmt": format_longitude(lon),
                "sign": s.value,
                "house": h,
                "term_ruler": term_ruler.value if hasattr(term_ruler, "value") else str(term_ruler),
            }

        result = {
            "name": planet.name.value,
            "longitude": planet.longitude,
            "longitude_fmt": format_longitude(planet.longitude),
            "sign": planet.sign.value,
            "house": house_num,
            # Oriental/occidental is needed for phasis/doryphory and to prevent LLM contradictions.
            # We compute it here rather than relying on Chart.Planet fields.
            "is_oriental": PhasisEngine.is_oriental(planet.longitude, sun.longitude) if planet.name not in [PlanetName.SUN, PlanetName.MOON] else None,
            "speed": planet.speed,
            "retrograde": bool(planet.speed is not None and planet.speed < 0),
            "dispositor": essentials.get("domicile").value if essentials.get("domicile") else None,
            "dignities": DignityCalculator.calculate_planet_dignity(planet.name, planet.longitude, sect),
            "accidental": DignityCalculator.calculate_accidental_dignity(planet, chart),
            "solar_status": calculate_solar_status(planet, sun),
            "solar_elongation_deg": round((((planet.longitude - sun.longitude) + 540.0) % 360.0) - 180.0, 6),
            "phasis": {
                "phase": PhasisEngine.get_synodic_phase(planet, sun.longitude).value,
                "visibility": None,
                "is_visible": None,
            },
            "voice": {
                # "Voice" is the report-layer framing: visible planets can testify.
                "has_voice": None,
                "note": "Derived from phasis visibility; visibility implies capacity to testify (traditional phasis doctrine)."
            },
            "maltreatments": [
                {"condition": m.type, "malefic": m.malefic.value, "description": m.description, "severity": m.severity}
                for m in KakosisEngine.check_maltreatments(planet, chart)
            ],
            "classical": {
                "monomoiria": {
                    "zoidion_ruler": zoidion_mono.value,
                    "trigonal_ruler": trigonal_mono.value,
                },
                "dodecatemoria": {
                    "valens": _dodec_payload(dodec_val_lon, "Valens (x12)"),
                    "paul": _dodec_payload(dodec_paul_lon, "Paul (x13)"),
                },
            },
            "impacts": []
        }

        # Phasis visibility details (auditable)
        try:
            vis = PhasisEngine.calculate_visibility_details(
                jd,
                chart.geo_lat,
                chart.geo_lon,
                planet.name,
                planet.longitude,
                planet.latitude,
                sun.longitude,
            )
            result["phasis"]["visibility"] = vis
            result["phasis"]["is_visible"] = bool(vis.get("is_visible"))
        except Exception:
            result["phasis"]["visibility"] = {"note": "Visibility calculation failed."}
            result["phasis"]["is_visible"] = None

        # Populate voice flag after phasis computed
        try:
            result["voice"]["has_voice"] = bool(result.get("phasis", {}).get("is_visible"))
        except Exception:
            result["voice"]["has_voice"] = None

        # Moon special-case: treat near-Sun condition as lunar phase/visibility, not "planetary combustion" rhetoric.
        if planet.name == PlanetName.MOON:
            try:
                elong = abs(((planet.longitude - sun.longitude) + 540.0) % 360.0 - 180.0)
                # "Visible" threshold is contextual; for audit, be conservative.
                # If within ~12 degrees of Sun, treat as not visibly testifying.
                if elong < 12.0:
                    result["phasis"]["is_visible"] = False
                    if isinstance(result["phasis"].get("visibility"), dict):
                        result["phasis"]["visibility"]["is_visible"] = False
                        result["phasis"]["visibility"]["method"] = "lunar_dark_override"
                        result["phasis"]["visibility"]["note"] = "Moon within 12° of Sun: forced dark/obscured for testimony."
                    result["voice"]["has_voice"] = False
                    result["voice"]["note"] = "Moon within 12° of Sun: treated as dark/obscured for testimony (phase/visibility doctrine)."
            except Exception:
                pass

        # Besiegement
        if is_besieged(planet, chart):
            result["impacts"].append({"cause": "Besiegement", "effect": "BLOCKED: Trapped between Malefics."})

        # Via Combusta
        if is_in_via_combusta(planet.longitude):
            result["impacts"].append({"cause": "Via Combusta", "effect": "DEBILITATED: The Burning Way."})

        # Antiscia
        ant, cant = calculate_antiscia(planet.longitude)
        for other in chart.planets:
            if other.name == planet.name: continue
            if abs(other.longitude - ant) < 1.0:
                result["impacts"].append({"cause": "Antiscia", "effect": f"Shadow contact with {other.name.value}"})

        # Delineation
        sect_str = "DAY" if sect == Sect.DAY else "NIGHT"
        key = f"{planet.name.value.upper()}_{planet.sign.value.upper()}_{sect_str}"
        result["delineation"] = LIB.get_planet_delineation(key)

        return result

    @staticmethod
    def _map_to_legacy_report(tech_data: Dict, chart: Chart) -> Dict:
        analysis = tech_data["analysis"]
        teams = analysis["teams"]
        moon = next(p for p in chart.planets if p.name == PlanetName.MOON)
        
        # Helper for Profections — prefer enhanced_profections (has LOY natal info)
        profections = analysis.get("enhanced_profections", {})
        if not profections:
            # Fallback to muntha-based construction
            muntha = analysis["fate"].get("muntha", {})
            if muntha:
                sign_name = muntha.get("sign")
                from .reference_data import DOMICILES, Sign
                try:
                    s = next(s for s in Sign if s.value == sign_name)
                    ruler = DOMICILES[s]
                    profections = {
                        "lord_of_year": ruler.value if hasattr(ruler, "value") else str(ruler),
                        "annual_sign": sign_name
                    }
                except Exception:
                    profections = {"lord_of_year": "Unknown", "annual_sign": sign_name}

        # Format Aspects for Legacy Report
        formatted_aspects = []
        # Prefer raw dataclass aspects if present, otherwise accept dict payloads.
        aspects_iter = analysis.get("aspects_raw") or analysis.get("aspects") or []
        for asp in aspects_iter:
            if isinstance(asp, dict):
                formatted_aspects.append({
                    "planet_a": asp.get("planet_a"),
                    "planet_b": asp.get("planet_b"),
                    "type": asp.get("type"),
                    "orb": asp.get("orb"),
                    "is_applying": asp.get("is_applying"),
                    "text": asp.get("text", ""),
                })
            else:
                formatted_aspects.append({
                    "planet_a": asp.planet_a.value,
                    "planet_b": asp.planet_b.value,
                    "type": asp.type.value,
                    "orb": asp.orb,
                    "is_applying": asp.is_applying,
                    "text": asp.text
                })

        legacy = {
            "summary": {
                "sect": Sect.DAY.value if chart.sun_altitude > 0 else Sect.NIGHT.value,
                "temperament": analysis.get("temperament", {}),
                "lunar_mansion": LunarMansionEngine.get_lunar_mansion(moon.longitude),
                "mutual_receptions": teams["receptions"],
                "constructive_team": teams["constructive_team"],
                "destructive_team": teams["destructive_team"],
                "maltreatments": {p["name"]: p["maltreatments"] for p in tech_data["planets_forensic"] if p["maltreatments"]},
                "universal_events": get_recent_eclipses(chart.jd),
                "dominant_elements": []
            },
            "soul_guardian": {
                "almuten": analysis["dignity"]["almuten"]["winner"],
                "job_description": f"Sovereign {analysis['dignity']['almuten']['winner']}"
            },
            "vitality": analysis.get("vitality", {"vitality_rating": "Indeterminate"}),
            "primary_directions": analysis["fate"]["primary_directions"],
            "primary_direction_distributor": analysis["fate"].get("primary_direction_distributor", {}),
            "profections": profections,
            "firdaria": analysis["fate"].get("firdaria", {}),
            "decennials": analysis["fate"].get("decennials", []),
            "solar_return": analysis["fate"].get("solar_return", {}),
            "forensic_lots": analysis["fate"]["hermetic_lots"],
            "planets": tech_data["planets_forensic"],
            "houses": tech_data["astronomy"]["houses"],
            "aspects": formatted_aspects,
            "fixed_stars": [{"star_name": s.star_name if hasattr(s, 'star_name') else s.get('star_name', ''), "planet_name": s.planet_name if hasattr(s, 'planet_name') else s.get('planet_name', ''), "message": s.message if hasattr(s, 'message') else s.get('message', ''), "mythology": s.mythology if hasattr(s, 'mythology') else s.get('mythology', '')} for s in analysis.get('supplemental', {}).get('stars', [])],
            "triplicity_periods": analysis.get("triplicity_periods", {})
        }
        return legacy
