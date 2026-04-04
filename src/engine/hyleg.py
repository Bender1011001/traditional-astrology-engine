from typing import Dict, List, Optional, Tuple
import logging
from .models import Chart, Planet, PlanetName, Sect, Sign
from .dignities import DignityCalculator

logger = logging.getLogger(__name__)

class HylegAlcocodenEngine:
    """
    Implements the Medieval Hyleg and Alcocoden technique (Bonatti/Lilly).
    Used for Vitality and Longevity forecasting.
    """
    
    # Hylegical Houses (Whole Sign): 1, 10, 11, 7, 9
    # Bonatti adds 11th as succedent but strong.
    # Standard Hylegical Places: 1, 10, 11, 7, 9. (Some sources say 1, 10, 7, 9, 11).
    # We will use 1, 10, 11, 7, 9.
    HYLEGICAL_HOUSES = [1, 10, 11, 7, 9]

    # Planetary Years (Bonatti/Lilly)
    PLANETARY_YEARS = {
        PlanetName.SATURN: {"minor": 30, "mean": 43.5, "major": 57},
        PlanetName.JUPITER: {"minor": 12, "mean": 45.5, "major": 79},
        PlanetName.MARS: {"minor": 15, "mean": 40.5, "major": 66},
        PlanetName.SUN: {"minor": 19, "mean": 69.5, "major": 120},
        PlanetName.VENUS: {"minor": 8, "mean": 45, "major": 82},
        PlanetName.MERCURY: {"minor": 20, "mean": 48, "major": 76},
        PlanetName.MOON: {"minor": 25, "mean": 66.5, "major": 108}
    }

    @staticmethod
    def _is_in_hylegical_house(planet: Planet, chart: Chart) -> bool:
        # Use Whole Sign house as a fallback; require above-horizon if altitude is available.
        house = DignityCalculator.get_house_number(planet.longitude, chart.ascendant, getattr(chart, "houses", None))
        if house not in HylegAlcocodenEngine.HYLEGICAL_HOUSES:
            return False
            
        # House 1 (Ascendant) is naturally below the horizon, do not disqualify it under altitude rules.
        if house == 1:
            return True
            
        if planet.altitude is not None:
            return planet.altitude > 0
            
        return True

    @staticmethod
    def _has_aspect_from_ruler(planet_pos: float, chart: Chart, sect: Sect) -> bool:
        """
        Bonatti Rule: The potential Hyleg must be aspected by one of its rulers.
        """
        rulers = DignityCalculator.get_essential_rulers(planet_pos, sect)
        # Flatten rulers to a set, filtering Nones
        active_rulers = {r for r in rulers.values() if r is not None}
        
        # Check if any of these rulers aspect the position
        # Aspects: 0, 60, 90, 120, 180 within orb.
        # Classic orb is generous, say 10 deg for vitality checks.
        
        for ruler_name in active_rulers:
            ruler_planet = next((p for p in chart.planets if p.name == ruler_name), None)
            if not ruler_planet: continue
            
            diff = abs(ruler_planet.longitude - planet_pos) % 360
            if diff > 180: diff = 360 - diff
            
            # Check major aspects with orb 10
            is_aspect = False
            for aspect in [0, 60, 90, 120, 180]:
                if abs(diff - aspect) <= 12: # Generous moity orb
                    is_aspect = True
                    break
            
            if is_aspect:
                return True
                
        return False

    @staticmethod
    def determine_hyleg(chart: Chart) -> Dict:
        """
        Determines the Hyleg (Giver of Life).
        Priority:
        Day: Sun -> Moon -> Asc.
        Night: Moon -> Sun -> Asc.
        Fallback: Part of Fortune, Syzygy (Simplified to Asc for now if others fail).
        """
        from .lots import calculate_lot_position, LotName
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
        
        candidates = []
        if sect == Sect.DAY:
            candidates = [PlanetName.SUN, PlanetName.MOON]
        else:
            candidates = [PlanetName.MOON, PlanetName.SUN]
            
        # 1. Check Luminaries
        for name in candidates:
            planet = next((p for p in chart.planets if p.name == name), None)
            if not planet: continue
            
            if HylegAlcocodenEngine._is_in_hylegical_house(planet, chart):
                if HylegAlcocodenEngine._has_aspect_from_ruler(planet.longitude, chart, sect):
                    return {"type": "Planet", "name": name.value, "longitude": planet.longitude, "candidate": name}

        # 2. Check Lot of Fortune
        try:
            lot_fortune = calculate_lot_position(chart, LotName.FORTUNE, sect)
            lot_house = DignityCalculator.get_house_number(lot_fortune, chart.ascendant, getattr(chart, "houses", None))
            if lot_house in HylegAlcocodenEngine.HYLEGICAL_HOUSES:
                if HylegAlcocodenEngine._has_aspect_from_ruler(lot_fortune, chart, sect):
                    return {"type": "Lot", "name": "Fortune", "longitude": lot_fortune, "candidate": "Fortune"}
        except Exception as e:
            logger.warning("Lot of Fortune Hyleg check failed: %s", repr(e), exc_info=True)
        
        # 3. Check Ascendant (Prevention of Asc Hyleg provided rulers aspect it)
        # Ascendant is usually valid if luminaries fail.
        # But technically needs aspect from ruler too.
        if HylegAlcocodenEngine._has_aspect_from_ruler(chart.ascendant, chart, sect):
             return {"type": "Angle", "name": "Ascendant", "longitude": chart.ascendant, "candidate": "Ascendant"}

        # 4. Fallback to Syzygy (not implemented), default to Ascendant if valid, else failure
        return {"type": "Fallback", "name": "Ascendant", "longitude": chart.ascendant, "candidate": "Ascendant"}

    @staticmethod
    def determine_alcocoden(hyleg_data: Dict, chart: Chart, method: str = "bonatti_points") -> Dict:
        """
        Determines the Alcocoden (Giver of Years).

        Supported methods:
        - "valens_term": strict bound/term ruler of the Hyleg degree (degree-based), must aspect the Hyleg.
        - "bonatti_points": essential rulers scored (dom/exalt/trip/term/face), highest score that aspects the Hyleg.

        Notes on aspect requirement:
        - We first attempt a degree-based Ptolemaic aspect check with a generous orb.
        - If no candidate qualifies (common when the Hyleg is an angle/degree), we fall back to
          whole-sign aspect logic (0/60/90/120/180 by sign), which is consistent with
          whole-sign framing used elsewhere in this project.
        """
        h_lon = hyleg_data["longitude"]
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
        
        rulers = DignityCalculator.get_essential_rulers(h_lon, sect) or {}

        # Bonatti-style points per dignity
        weights = {"domicile": 5, "exaltation": 4, "triplicity": 3, "term": 2, "face": 1}

        # Accumulate points for each potential ruler (or strict term only)
        points: Dict[PlanetName, int] = {}
        if method == "valens_term":
            pn = rulers.get("term")
            if pn is not None:
                points[pn] = weights["term"]
        else:
            for dignity_key, w in weights.items():
                pn = rulers.get(dignity_key)
                if pn is None:
                    continue
                points[pn] = points.get(pn, 0) + w

        # Resolve to candidates with planet objects
        candidates = []
        for pn, score in points.items():
            p_obj = next((p for p in chart.planets if p.name == pn), None)
            if not p_obj:
                continue
            candidates.append({"name": pn, "score": score, "planet": p_obj, "via": method})

        if not candidates:
            return None

        def _degree_aspects(p_lon: float, target_lon: float, orb: float = 12.0) -> Optional[str]:
            d = abs(p_lon - target_lon) % 360.0
            if d > 180.0:
                d = 360.0 - d
            for a in [0, 60, 90, 120, 180]:
                if abs(d - a) <= orb:
                    return {0: "Conjunction", 60: "Sextile", 90: "Square", 120: "Trine", 180: "Opposition"}[a]
            return None

        def _sign_aspects(p_lon: float, target_lon: float) -> Optional[str]:
            ps = int(p_lon / 30.0) % 12
            ts = int(target_lon / 30.0) % 12
            diff = (ps - ts) % 12
            mapping = {0: "Conjunction (Whole Sign)", 2: "Sextile (Whole Sign)", 3: "Square (Whole Sign)", 4: "Trine (Whole Sign)", 6: "Opposition (Whole Sign)", 8: "Trine (Whole Sign)", 9: "Square (Whole Sign)", 10: "Sextile (Whole Sign)"}
            return mapping.get(diff)

        # 1) Degree-orb aspect pass
        orb_hits = []
        for c in candidates:
            asp = _degree_aspects(c["planet"].longitude, h_lon)
            if asp:
                c2 = dict(c)
                c2["aspect"] = asp
                c2["aspect_mode"] = "degree_orb"
                orb_hits.append(c2)

        if orb_hits:
            best = max(orb_hits, key=lambda x: (x["score"],))
            return best

        # 2) Whole-sign fallback pass (explicitly marked)
        sign_hits = []
        for c in candidates:
            asp = _sign_aspects(c["planet"].longitude, h_lon)
            if asp:
                c2 = dict(c)
                c2["aspect"] = asp
                c2["aspect_mode"] = "whole_sign"
                sign_hits.append(c2)

        if not sign_hits:
            return None

        best = max(sign_hits, key=lambda x: (x["score"],))
        best["note"] = "No degree-orb aspect qualified; selected by whole-sign aspect fallback."
        return best

    @staticmethod
    def calculate_lifespan(hyleg: Dict, alcocoden: Dict, chart: Chart) -> Dict:
        if not alcocoden:
            return {"total_years": 0, "breakdown": ["No Alcocoden found."]}
        
        p_name = alcocoden["name"]
        p_obj = alcocoden["planet"]
        
        # 1. Determine Years Scale (Major, Mean, Minor)
        house = DignityCalculator.get_house_number(p_obj.longitude, chart.ascendant, getattr(chart, "houses", None))
        dignity = DignityCalculator.calculate_planet_dignity(p_name, p_obj.longitude, Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT)
        dignity_score = dignity.get("total_score", 0)
        
        years_type = "Minor"
        base_years = HylegAlcocodenEngine.PLANETARY_YEARS[p_name]["minor"]
        
        if house in [1, 4, 7, 10] and dignity_score >= 4:
            years_type = "Major"
            base_years = HylegAlcocodenEngine.PLANETARY_YEARS[p_name]["major"]
        elif house in [2, 5, 8, 11] and dignity_score >= 0:
            years_type = "Mean"
            base_years = HylegAlcocodenEngine.PLANETARY_YEARS[p_name]["mean"]
        
        logs = [f"Base: {years_type} Years of {p_name.value} ({base_years}) due to House {house} and dignity {dignity_score}"]
        total = base_years
        
        # 2. Additions/Subtractions from Aspects (Bonatti/Lilly-inspired heuristic)
        #
        # Many medieval presentations add/subtract in a mixed "years + months" manner:
        # - Benefics can add their Minor Years + (Mean Years / 12) as years (months converted to years)
        # - Malefics can subtract similarly, but typically only on hard aspects.
        #
        # This is still an approximation; we keep it auditable and conservative.
        
        for p in chart.planets:
            if p.name == p_name: continue
            
            # Check aspect
            diff = abs(p.longitude - p_obj.longitude) % 360
            if diff > 180: diff = 360 - diff
            
            is_aspect = False
            aspect_type = ""
            if abs(diff - 0) <= 8: aspect_type = "Conjunction"
            elif abs(diff - 60) <= 8: aspect_type = "Sextile"
            elif abs(diff - 90) <= 8: aspect_type = "Square"
            elif abs(diff - 120) <= 8: aspect_type = "Trine"
            elif abs(diff - 180) <= 8: aspect_type = "Opposition"
            
            if aspect_type:
                mod = 0
                if p.name not in HylegAlcocodenEngine.PLANETARY_YEARS:
                    continue
                    
                minor_y = float(HylegAlcocodenEngine.PLANETARY_YEARS[p.name]["minor"])
                mean_y = float(HylegAlcocodenEngine.PLANETARY_YEARS[p.name]["mean"])
                delta_full = minor_y + (mean_y / 12.0)
                
                if p.name in [PlanetName.JUPITER, PlanetName.VENUS]:
                    # Benefics add: full help on soft aspects, partial on hard aspects.
                    if aspect_type in ["Conjunction", "Trine", "Sextile"]:
                        mod = delta_full
                    elif aspect_type in ["Square", "Opposition"]:
                        mod = delta_full / 2.0
                         
                elif p.name in [PlanetName.SATURN, PlanetName.MARS]:
                    # Malefics subtract: only on hard aspects.
                    if aspect_type in ["Conjunction", "Square", "Opposition"]:
                        # Treat squares as weaker than conjunction/opposition in this numeric heuristic.
                        mod = -(delta_full / 2.0) if aspect_type == "Square" else -delta_full
                    elif aspect_type in ["Trine", "Sextile"]:
                        mod = 0
                
                if mod != 0:
                    total += mod
                    action = "Added" if mod > 0 else "Subtracted"
                    logs.append(f"{action} {abs(mod):.1f} ({p.name.value} {aspect_type})")

        # Safety clamp to prevent negative or zero years in output (unless intended by tradition, but generally 0 is not useful)
        if total < 5:
             logs.append("Vitality score adjusted to minimum threshold.")
             total = max(total, 5.0)

        # Classification
        rating = "Moderate"
        if total >= 70: rating = "Superior"
        elif total >= 50: rating = "Strong"
        elif total >= 25: rating = "Moderate"
        else: rating = "Cautionary (Requires strengthening)"

        return {
            "hyleg": hyleg["name"],
            "alcocoden": p_name.value,
            "base_years_type": years_type,
            "base_years": base_years,
            "total_years": total,
            "vitality_rating": rating,
            "breakdown": logs
        }

    @staticmethod
    def determine_anareta(hyleg_data: Dict, chart: Chart) -> Dict:
        """
        Determines the Anareta (Killing Planet / Destroyer of Life).

        Enhanced per Bonatti (Liber Astronomiae Tr. 8) and Lilly (CA pp. 537-541):
        1. Mars and Saturn are primary Anareta candidates via hard aspect
           (Conjunction, Square, Opposition) to the Hyleg degree.
        2. The OUT-OF-SECT malefic is prioritized — it is the chart's most
           destructive planet and thus the more likely Anareta.
        3. The ruler of the 8th house cusp (House of Death) is also a candidate
           if it makes a hard aspect to the Hyleg.
        4. The descending degree (7th cusp / occidental horizon) is a classical
           Anareta point, as it opposes the Ascendant (life).

        Returns the strongest candidate with the tightest orb, with sect-based
        tiebreaking.
        """
        if not hyleg_data or "longitude" not in hyleg_data:
            return {"name": None, "reason": "No Hyleg available."}

        h_lon = hyleg_data["longitude"]
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT

        # Determine out-of-sect malefic (the worse one for this chart)
        if sect == Sect.DAY:
            oos_malefic = PlanetName.MARS   # Mars is worse by day
            is_malefic = PlanetName.SATURN   # Saturn is in-sect by day
        else:
            oos_malefic = PlanetName.SATURN  # Saturn is worse by night
            is_malefic = PlanetName.MARS     # Mars is in-sect by night

        # Build candidate list: malefics + 8th house ruler
        candidates = [PlanetName.MARS, PlanetName.SATURN]

        # Add 8th house ruler if different from malefics
        houses = getattr(chart, "houses", None) or {}
        h8_cusp = houses.get(8, houses.get("8", None))
        if h8_cusp is not None:
            from .reference_data import DOMICILES
            h8_sign = list(Sign)[int(h8_cusp / 30) % 12]
            h8_ruler = DOMICILES.get(h8_sign)
            if h8_ruler and h8_ruler not in candidates:
                candidates.append(h8_ruler)

        best = None
        best_orb = 999.0
        best_aspect = None
        best_is_oos = False   # out-of-sect flag for tiebreaking
        best_source = ""

        # Hard aspect orbs — slightly generous for vitality (life/death matters)
        HARD_ASPECTS = [
            (0,   "Conjunction", 6.0),
            (90,  "Square",      5.0),
            (180, "Opposition",  5.0),
        ]

        for pn in candidates:
            p = next((pl for pl in chart.planets if pl.name == pn), None)
            if not p:
                continue
            diff = abs(p.longitude - h_lon) % 360
            if diff > 180:
                diff = 360 - diff

            is_oos = (pn == oos_malefic)

            for asp, label, orb_allow in HARD_ASPECTS:
                orb = abs(diff - asp)
                if orb <= orb_allow:
                    # Prefer tighter orb; at equal orb, prefer out-of-sect malefic
                    beats_current = False
                    if orb < best_orb:
                        beats_current = True
                    elif abs(orb - best_orb) < 0.5 and is_oos and not best_is_oos:
                        beats_current = True  # sect tiebreaker

                    if beats_current:
                        best = p
                        best_orb = orb
                        best_aspect = label
                        best_is_oos = is_oos
                        best_source = "malefic" if pn in [PlanetName.MARS, PlanetName.SATURN] else "8th_ruler"

        # Also check the descending degree (7th cusp) as a classical Anareta point
        desc_lon = (chart.ascendant + 180.0) % 360.0
        desc_diff = abs(h_lon - desc_lon) % 360
        if desc_diff > 180:
            desc_diff = 360 - desc_diff
        # Conjunction of Hyleg to 7th cusp within 3° is traditionally lethal
        if desc_diff <= 3.0 and desc_diff < best_orb:
            return {
                "name": "Descendant (7th cusp)",
                "longitude": desc_lon,
                "aspect_to_hyleg": "Conjunction to Occidental Horizon",
                "orb": round(desc_diff, 2),
                "reason": "The Hyleg conjoins the Descendant — the occidental horizon is a classical Anareta point (the setting place)."
            }

        if not best:
            return {
                "name": None,
                "reason": "No tight hard aspect from malefics or 8th-house ruler to the Hyleg degree found."
            }

        sect_note = " (Out-of-sect malefic — primary troublemaker)" if best_is_oos else " (In-sect malefic)"
        source_note = ""
        if best_source == "8th_ruler":
            source_note = " [Ruler of the 8th House of Death]"

        return {
            "name": best.name.value,
            "longitude": best.longitude,
            "aspect_to_hyleg": best_aspect,
            "orb": round(best_orb, 2),
            "is_out_of_sect": best_is_oos,
            "reason": f"{best.name.value} makes a tight {best_aspect} ({best_orb:.1f}°) to the Hyleg degree.{sect_note}{source_note}"
        }

