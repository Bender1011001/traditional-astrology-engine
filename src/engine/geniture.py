from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .models import Chart, Planet, PlanetName, Sect, Sign
from .dignities import DignityCalculator
from .reference_data import DOMICILES, EXALTATIONS, PTOLEMAIC_TERMS, PTOLEMAIC_TRIPLICITY, SIGN_ELEMENTS, MOIETIES
import logging

logger = logging.getLogger(__name__)


@dataclass
class GeniturePlanetScore:
    planet: PlanetName
    total: int
    breakdown: Dict[str, int]
    details: List[str]


class LordOfGenitureEngine:
    """
    William Lilly style net fortitudes/debilities ("Lord of the Geniture").

    This is intentionally separate from the Almuten Figuris (Ibn Ezra) logic.
    It uses:
    - Ptolemaic Triplicity and Ptolemaic Terms (Lilly mode)
    - A distinct accidental dignity table (house placement + motion + solar phase, etc.)
    """

    CAZIMI_DEG = 17 / 60.0  # 0°17'
    COMBUST_DEG = 8.5       # 8°30'
    UNDER_BEAMS_DEG = 17.0  # 17°

    @staticmethod
    def _norm_diff(a: float, b: float) -> float:
        d = abs((a - b) % 360.0)
        return d if d <= 180.0 else 360.0 - d

    @staticmethod
    def _in_sign(lon: float) -> Sign:
        return list(Sign)[int(lon / 30) % 12]

    @staticmethod
    def _deg_in_sign(lon: float) -> float:
        return lon % 30.0

    @classmethod
    def _ptolemaic_term_ruler(cls, lon: float) -> Optional[PlanetName]:
        sign = cls._in_sign(lon)
        deg = cls._deg_in_sign(lon)
        bounds = PTOLEMAIC_TERMS.get(sign, [])
        for ruler, limit in bounds:
            if deg < limit:
                return ruler
        return None

    @classmethod
    def _face_ruler(cls, lon: float) -> Optional[PlanetName]:
        # Use DignityCalculator's face table (it is chaldean faces; Lilly uses decans too).
        sign = cls._in_sign(lon)
        deg = cls._deg_in_sign(lon)
        face_idx = int(deg // 10)
        try:
            face_val = DignityCalculator.FACES[sign][face_idx]
        except Exception as e:
            logger.warning("Face lookup failed for %s at %.1f°: %s", sign, deg, repr(e), exc_info=True)
            return None
        if isinstance(face_val, str):
            key = face_val.upper()
            return PlanetName[key] if key in PlanetName.__members__ else None
        return face_val

    @classmethod
    def _ptolemaic_triplicity_ruler(cls, lon: float, sect: Sect) -> Optional[PlanetName]:
        sign = cls._in_sign(lon)
        element = SIGN_ELEMENTS.get(sign)
        if not element:
            return None
        rulers = PTOLEMAIC_TRIPLICITY.get(element)
        if not rulers:
            return None
        return rulers[0] if sect == Sect.DAY else rulers[1]

    @classmethod
    def _essential_score_lilly(cls, planet: PlanetName, lon: float, sect: Sect) -> Tuple[int, Dict[str, int], List[str]]:
        score = 0
        breakdown: Dict[str, int] = {
            "domicile": 0,
            "exaltation": 0,
            "triplicity": 0,
            "term": 0,
            "face": 0,
            "detriment": 0,
            "fall": 0,
            "peregrine": 0,
        }
        details: List[str] = []

        sign = cls._in_sign(lon)

        # Domicile / Detriment
        dom = DOMICILES.get(sign)
        if dom == planet:
            score += 5
            breakdown["domicile"] = 5
            details.append("Domicile (+5)")
        else:
            # detriment is opposite domicile
            sign_idx = int(lon / 30) % 12
            opp_sign = list(Sign)[(sign_idx + 6) % 12]
            opp_dom = DOMICILES.get(opp_sign)
            if opp_dom == planet:
                score -= 5
                breakdown["detriment"] = -5
                details.append("Detriment (-5)")

        # Exaltation / Fall
        exalt = EXALTATIONS.get(sign)
        if exalt == planet:
            score += 4
            breakdown["exaltation"] = 4
            details.append("Exaltation (+4)")
        else:
            # fall is opposite exaltation degree-sign; for sign-based scoring, use opposite sign of planet's exaltation sign
            # This matches the common Lilly table used in your prompt.
            ex_sign = None
            for s, p in EXALTATIONS.items():
                if p == planet:
                    ex_sign = s
                    break
            if ex_sign:
                ex_idx = list(Sign).index(ex_sign)
                fall_sign = list(Sign)[(ex_idx + 6) % 12]
                if sign == fall_sign:
                    score -= 4
                    breakdown["fall"] = -4
                    details.append("Fall (-4)")

        # Triplicity (Ptolemaic)
        tri = cls._ptolemaic_triplicity_ruler(lon, sect)
        if tri == planet:
            score += 3
            breakdown["triplicity"] = 3
            details.append(f"Triplicity ({sect.value}, Ptolemaic) (+3)")

        # Term (Ptolemaic)
        term = cls._ptolemaic_term_ruler(lon)
        if term == planet:
            score += 2
            breakdown["term"] = 2
            details.append("Term (Ptolemaic) (+2)")

        # Face
        face = cls._face_ruler(lon)
        if face == planet:
            score += 1
            breakdown["face"] = 1
            details.append("Face (+1)")

        # Peregrine: no essential dignity at all (and not in detriment/fall scoring above)
        has_any_pos = any(breakdown[k] > 0 for k in ["domicile", "exaltation", "triplicity", "term", "face"])
        if not has_any_pos and breakdown["detriment"] == 0 and breakdown["fall"] == 0:
            score -= 5
            breakdown["peregrine"] = -5
            details.append("Peregrine (-5)")

        return score, breakdown, details

    @classmethod
    def _house_score_lilly(cls, house_num: int) -> Tuple[int, str]:
        # From docs/research/Almuten Figuris Calculation Specification.txt (Lilly table)
        if house_num in (1, 10):
            return 5, "House (1/10) (+5)"
        if house_num in (7, 4, 11):
            return 4, "House (7/4/11) (+4)"
        if house_num in (2, 5):
            return 3, "House (2/5) (+3)"
        if house_num == 9:
            return 2, "House (9) (+2)"
        if house_num == 3:
            return 1, "House (3) (+1)"
        if house_num == 12:
            return -5, "House (12) (-5)"
        if house_num in (8, 6):
            return -2, "House (8/6) (-2)"
        return 0, "House (0)"

    @classmethod
    def _motion_score_lilly(cls, planet: Planet) -> Tuple[int, Dict[str, int], List[str]]:
        score = 0
        breakdown = {"direct": 0, "retrograde": 0, "swift": 0, "slow": 0}
        details: List[str] = []

        if planet.speed is not None and planet.speed < 0:
            score -= 5
            breakdown["retrograde"] = -5
            details.append("Retrograde (-5)")
            return score, breakdown, details

        # Direct +4 (per spec)
        score += 4
        breakdown["direct"] = 4
        details.append("Direct (+4)")

        avg = DignityCalculator.AVERAGE_SPEEDS.get(planet.name)
        if avg and planet.speed is not None:
            if planet.speed > avg:
                score += 2
                breakdown["swift"] = 2
                details.append("Swift (+2)")
            elif 0 < planet.speed < avg:
                score -= 2
                breakdown["slow"] = -2
                details.append("Slow (-2)")

        return score, breakdown, details

    @classmethod
    def _solar_phase_score_lilly(cls, planet: Planet, chart: Chart) -> Tuple[int, Dict[str, int], List[str]]:
        if planet.name == PlanetName.SUN:
            return 0, {"cazimi": 0, "combust": 0, "under_beams": 0}, []

        sun = next((p for p in chart.planets if p.name == PlanetName.SUN), None)
        if not sun:
            return 0, {"cazimi": 0, "combust": 0, "under_beams": 0}, []

        dist = cls._norm_diff(planet.longitude, sun.longitude)
        breakdown = {"cazimi": 0, "combust": 0, "under_beams": 0}
        details: List[str] = []

        if dist <= cls.CAZIMI_DEG:
            breakdown["cazimi"] = 5
            details.append("Cazimi (+5)")
            return 5, breakdown, details
        if dist <= cls.COMBUST_DEG:
            breakdown["combust"] = -5
            details.append("Combust (-5)")
            return -5, breakdown, details
        if dist <= cls.UNDER_BEAMS_DEG:
            breakdown["under_beams"] = -4
            details.append("Under Beams (-4)")
            return -4, breakdown, details

        return 0, breakdown, details

    @classmethod
    def _orientality_score_lilly(cls, planet: Planet, chart: Chart) -> Tuple[int, Dict[str, int], List[str]]:
        if planet.name == PlanetName.SUN:
            return 0, {"orientality": 0}, []

        sun = next((p for p in chart.planets if p.name == PlanetName.SUN), None)
        if not sun:
            return 0, {"orientality": 0}, []

        # Oriental: rises before Sun (zodiacal proxy)
        is_oriental = ((sun.longitude - planet.longitude) % 360.0) < 180.0
        score = 0
        details: List[str] = []
        breakdown = {"orientality": 0}

        if planet.name in (PlanetName.SATURN, PlanetName.JUPITER, PlanetName.MARS):
            if is_oriental:
                score += 2
                breakdown["orientality"] = 2
                details.append("Oriental (+2)")
            else:
                score -= 2
                breakdown["orientality"] = -2
                details.append("Occidental (-2)")
        elif planet.name in (PlanetName.VENUS, PlanetName.MERCURY):
            if not is_oriental:
                score += 2
                breakdown["orientality"] = 2
                details.append("Occidental (+2)")
            else:
                score -= 2
                breakdown["orientality"] = -2
                details.append("Oriental (-2)")
        elif planet.name == PlanetName.MOON:
            # Moon: increasing light (+2) / decreasing (-2)
            diff = (planet.longitude - sun.longitude) % 360.0
            if 0 < diff < 180:
                score += 2
                breakdown["orientality"] = 2
                details.append("Increasing in Light (+2)")
            else:
                score -= 2
                breakdown["orientality"] = -2
                details.append("Decreasing in Light (-2)")

        return score, breakdown, details

    @classmethod
    def _aspect_score_lilly(cls, planet: Planet, chart: Chart) -> Tuple[int, Dict[str, int], List[str]]:
        """
        Score aspects to benefics/malefics using Lilly-style moieties as a practical orb.
        This is a simplified subset of Lilly's table (enough to distinguish dominant actors).
        """
        score = 0
        breakdown = {"benefic_aspects": 0, "malefic_aspects": 0}
        details: List[str] = []

        if planet.name in (PlanetName.NORTH_NODE, PlanetName.SOUTH_NODE):
            return 0, breakdown, details

        benefics = [PlanetName.JUPITER, PlanetName.VENUS]
        malefics = [PlanetName.MARS, PlanetName.SATURN]

        def _orb_ok(other: Planet, exact_angle: float) -> bool:
            d = cls._norm_diff(planet.longitude, other.longitude)
            moiety = MOIETIES.get(planet.name, 3.0) + MOIETIES.get(other.name, 3.0)
            return abs(d - exact_angle) <= moiety

        # Benefics
        for other_name in benefics:
            other = next((p for p in chart.planets if p.name == other_name), None)
            if not other:
                continue
            if _orb_ok(other, 0.0):
                score += 5
                breakdown["benefic_aspects"] += 5
                details.append(f"Conjunct {other_name.value} (+5)")
            elif _orb_ok(other, 60.0):
                score += 3
                breakdown["benefic_aspects"] += 3
                details.append(f"Sextile {other_name.value} (+3)")
            elif _orb_ok(other, 120.0):
                score += 4
                breakdown["benefic_aspects"] += 4
                details.append(f"Trine {other_name.value} (+4)")

        # Malefics
        for other_name in malefics:
            other = next((p for p in chart.planets if p.name == other_name), None)
            if not other:
                continue
            if _orb_ok(other, 0.0):
                score -= 5
                breakdown["malefic_aspects"] -= 5
                details.append(f"Conjunct {other_name.value} (-5)")
            elif _orb_ok(other, 90.0):
                score -= 3
                breakdown["malefic_aspects"] -= 3
                details.append(f"Square {other_name.value} (-3)")
            elif _orb_ok(other, 180.0):
                score -= 4
                breakdown["malefic_aspects"] -= 4
                details.append(f"Opposition {other_name.value} (-4)")

        return score, breakdown, details

    @classmethod
    def calculate(cls, chart: Chart) -> Dict[str, object]:
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT

        candidates = [
            PlanetName.SUN,
            PlanetName.MOON,
            PlanetName.MERCURY,
            PlanetName.VENUS,
            PlanetName.MARS,
            PlanetName.JUPITER,
            PlanetName.SATURN,
        ]

        scores: Dict[str, GeniturePlanetScore] = {}

        for pn in candidates:
            p = next((pl for pl in chart.planets if pl.name == pn), None)
            if not p:
                continue

            total = 0
            breakdown: Dict[str, int] = {}
            details: List[str] = []

            # Essential
            ess_s, ess_b, ess_d = cls._essential_score_lilly(pn, p.longitude, sect)
            total += ess_s
            breakdown.update({f"essential_{k}": v for k, v in ess_b.items() if v})
            details.extend(ess_d)

            # House
            house_num = DignityCalculator.get_house_number(p.longitude, chart.ascendant, getattr(chart, "houses", None))
            hs, hs_detail = cls._house_score_lilly(house_num)
            total += hs
            breakdown["acc_house"] = hs
            details.append(hs_detail)

            # Motion / speed
            ms, ms_b, ms_d = cls._motion_score_lilly(p)
            total += ms
            breakdown.update({f"acc_{k}": v for k, v in ms_b.items() if v})
            details.extend(ms_d)

            # Solar phase
            ss, ss_b, ss_d = cls._solar_phase_score_lilly(p, chart)
            total += ss
            breakdown.update({f"acc_{k}": v for k, v in ss_b.items() if v})
            details.extend(ss_d)

            # Orientality / moon light
            os, os_b, os_d = cls._orientality_score_lilly(p, chart)
            total += os
            breakdown.update({f"acc_{k}": v for k, v in os_b.items() if v})
            details.extend(os_d)

            # Aspects (benefic/malefic)
            asp_s, asp_b, asp_d = cls._aspect_score_lilly(p, chart)
            total += asp_s
            breakdown.update({f"acc_{k}": v for k, v in asp_b.items() if v})
            details.extend(asp_d)

            scores[pn.value] = GeniturePlanetScore(
                planet=pn,
                total=int(total),
                breakdown=breakdown,
                details=details,
            )

        winner = None
        if scores:
            winner = max(scores.values(), key=lambda s: s.total).planet.value

        # Serialize for JSON
        return {
            "winner": winner or "Unknown",
            "scores": {
                k: {
                    "total": v.total,
                    "breakdown": v.breakdown,
                    "details": v.details,
                }
                for k, v in scores.items()
            },
            "method": "Lilly (net fortitudes/debilities; Ptolemaic terms/triplicity)"
        }
