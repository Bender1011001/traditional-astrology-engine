"""
Degree-quality engine (deterministic lookup over the classical per-degree tables).

Implements the five classical "qualities of the degrees" exactly as William Lilly
prints them in the *Two necessary Tables of the Signes* (Christian Astrology,
1647, pp.116-118):

  1. masculine / feminine degrees
  2. light / dark / smoky / void degrees
  3. deep or pitted degrees
  4. lame or deficient (azimene) degrees
  5. degrees of increasing fortune

SOURCE & CONVENTIONS
- Data transcribed from Lilly's printed table, p.116 (worldastrology.net facsimile),
  cross-validated against secondary lists (which use 0-based degrees exactly one
  lower, confirming Lilly's numbering).
- **One-based degrees.** Lilly's "degree 1" = the arc 0°00'-0°59', "degree 2" =
  1°00'-1°59', ... "degree 30" = 29°00'-29°59'. We store integers 1..30.
- **Boundary encoding** for the two graded columns (masc/fem and light/dark/smoky/
  void): each entry is [end_degree, label] meaning "the block ending at this
  one-based degree (inclusive, starting just after the previous boundary) has this
  label." The last boundary of every sign is 30. The flag columns (pitted, azimene,
  increasing_fortune) are plain lists of one-based degrees.
- **`tradition` is a stored authority, not a validator.** Lilly (1647) is the
  default. al-Bīrūnī differs on specific degrees and is a SEPARATE authority (left
  empty here until sourced); never auto-merge traditions.

Interpretive uses are Lilly's own (CA pp.117-118): sexing an unknown querent or
unborn child (masc/fem); complexion & mental clarity (light/dark/smoky/void); an
affair "at a stand" needing help (pitted); bodily defect / blemish / chronic
infirmity / lameness (azimene); augmentation of wealth (increasing fortune).
"""

from typing import Any, Dict, List, Optional, Union

from .models import Sign

_SIGNS = [s.value for s in Sign]

# --- Lilly 1647, Christian Astrology p.116 (one-based degrees) ---------------
# masculine_feminine: boundary list [end_degree, "M"|"F"]
_MF = {
    "Aries": [[8, "M"], [9, "F"], [15, "M"], [22, "F"], [30, "M"]],
    "Taurus": [[5, "F"], [11, "M"], [17, "F"], [21, "M"], [24, "F"], [30, "M"]],
    "Gemini": [[5, "F"], [16, "M"], [22, "F"], [26, "M"], [30, "F"]],
    "Cancer": [[2, "M"], [8, "F"], [10, "M"], [12, "F"], [23, "M"], [27, "F"], [30, "M"]],
    "Leo": [[5, "M"], [8, "F"], [15, "M"], [23, "F"], [30, "M"]],
    "Virgo": [[8, "F"], [12, "M"], [20, "F"], [30, "M"]],
    "Libra": [[5, "M"], [15, "F"], [20, "M"], [27, "F"], [30, "M"]],
    "Scorpio": [[4, "M"], [14, "F"], [17, "M"], [25, "F"], [30, "M"]],
    "Sagittarius": [[2, "M"], [5, "F"], [12, "M"], [24, "F"], [30, "M"]],
    "Capricorn": [[11, "M"], [19, "F"], [30, "M"]],
    "Aquarius": [[5, "M"], [15, "F"], [21, "M"], [25, "F"], [27, "M"], [30, "F"]],
    "Pisces": [[10, "M"], [20, "F"], [23, "M"], [28, "F"], [30, "M"]],
}
# light_dark_smoky_void: boundary list [end_degree, "light"|"dark"|"smoky"|"void"]
_LDSV = {
    "Aries": [[3, "dark"], [8, "light"], [16, "dark"], [20, "light"], [24, "void"], [29, "light"], [30, "void"]],
    "Taurus": [[3, "dark"], [7, "light"], [12, "void"], [15, "light"], [20, "void"], [28, "light"], [30, "dark"]],
    "Gemini": [[4, "light"], [7, "dark"], [12, "light"], [16, "void"], [22, "light"], [27, "dark"], [30, "void"]],
    "Cancer": [[12, "light"], [14, "dark"], [18, "void"], [20, "smoky"], [28, "light"], [30, "void"]],
    "Leo": [[10, "dark"], [20, "smoky"], [25, "void"], [30, "light"]],
    "Virgo": [[5, "dark"], [8, "light"], [10, "void"], [16, "light"], [22, "smoky"], [27, "void"], [30, "dark"]],
    "Libra": [[5, "light"], [10, "dark"], [18, "light"], [21, "dark"], [27, "light"], [30, "void"]],
    "Scorpio": [[3, "dark"], [8, "light"], [14, "void"], [22, "light"], [24, "smoky"], [29, "void"], [30, "dark"]],
    "Sagittarius": [[9, "light"], [12, "dark"], [19, "light"], [23, "smoky"], [30, "light"]],
    "Capricorn": [[7, "dark"], [10, "light"], [15, "smoky"], [19, "light"], [22, "dark"], [25, "void"], [30, "dark"]],
    "Aquarius": [[4, "smoky"], [9, "light"], [13, "dark"], [23, "light"], [25, "void"], [30, "dark"]],
    "Pisces": [[6, "dark"], [12, "light"], [18, "dark"], [22, "light"], [25, "void"], [28, "light"], [30, "dark"]],
}
_PITTED = {
    "Aries": [6, 11, 16, 23, 29],
    "Taurus": [5, 12, 24, 25],
    "Gemini": [2, 12, 17, 26, 30],
    "Cancer": [12, 17, 23, 26, 30],
    "Leo": [6, 13, 15, 22, 23, 28],
    "Virgo": [8, 13, 16, 21, 22],
    "Libra": [1, 7, 20, 30],
    "Scorpio": [9, 10, 22, 23, 27],
    "Sagittarius": [7, 12, 15, 24, 27, 30],
    "Capricorn": [7, 17, 22, 24, 29],
    "Aquarius": [1, 12, 17, 22, 24, 29],
    "Pisces": [4, 9, 24, 27, 28],
}
_AZIMENE = {
    "Aries": [],
    "Taurus": [6, 7, 8, 9, 10],
    "Gemini": [],
    "Cancer": [9, 10, 11, 12, 13, 14, 15],
    "Leo": [18, 27, 28],
    "Virgo": [],
    "Libra": [],
    "Scorpio": [19, 28],
    "Sagittarius": [1, 7, 8, 18, 19],
    "Capricorn": [26, 27, 28, 29],
    "Aquarius": [18, 19],
    "Pisces": [],
}
_INCREASING = {
    "Aries": [19],
    "Taurus": [3, 15, 27],
    "Gemini": [11],
    "Cancer": [1, 2, 3, 4, 15],
    "Leo": [2, 5, 7, 19],
    "Virgo": [3, 14, 20],
    "Libra": [3, 15, 21],
    "Scorpio": [7, 18, 20],
    "Sagittarius": [12, 20],
    "Capricorn": [12, 13, 14, 20],
    "Aquarius": [7, 16, 17, 20],
    "Pisces": [13, 20],
}

DEGREE_QUALITIES: Dict[str, Dict[str, Any]] = {
    "lilly_1647": {
        "source": "William Lilly, Christian Astrology (1647), p.116 'Two necessary Tables of the Signes'",
        "degree_convention": "one-based: degree 1 = 0°00'-0°59' ... degree 30 = 29°00'-29°59'",
        "masculine_feminine": _MF,
        "light_dark_smoky_void": _LDSV,
        "pitted": _PITTED,
        "azimene": _AZIMENE,
        "increasing_fortune": _INCREASING,
    },
    # Alternate authority — populate from al-Bīrūnī (Wright) when sourced.
    "al_biruni": {
        "source": "al-Bīrūnī, The Book of Instruction (Wright tr.) — alternate authority (not yet transcribed)",
        "degree_convention": "one-based",
        "masculine_feminine": {s: [] for s in _SIGNS},
        "light_dark_smoky_void": {s: [] for s in _SIGNS},
        "pitted": {s: [] for s in _SIGNS},
        "azimene": {s: [] for s in _SIGNS},
        "increasing_fortune": {s: [] for s in _SIGNS},
    },
}

INTERPRETATIONS = {
    "masculine_feminine": "Sex/quality of the degree (Lilly CA p.117): used to judge the sex of an unknown querent or unborn child, and a masculine/feminine cast to the matter.",
    "light": "Light degree (Lilly CA p.117): a fairer complexion and a clearer, more capable understanding.",
    "dark": "Dark degree (Lilly CA p.117): a more obscure, dark complexion; any deformity is greater.",
    "smoky": "Smoky degree (Lilly CA p.118): a mixed complexion and condition — neither fair nor foul, neither very judicious nor an 'asse'.",
    "void": "Void/empty degree (Lilly CA p.117): the understanding is small and judgment less than supposed; emptiness in the matter.",
    "pitted": "Deep or pitted degree (Lilly CA p.118): the native/matter is 'at a stand' — stuck and in need of help to be drawn out, like a man fallen into a ditch.",
    "azimene": "Lame or deficient (azimene) degree (Lilly CA p.118): bodily defect, blemish, lameness, blindness, or an inseparable chronic infirmity in the significator's topic.",
    "increasing_fortune": "Degree of increasing fortune (Lilly CA p.118): if the 2nd cusp/its lord, Jupiter, or the Part of Fortune fall here, an argument of much wealth.",
}


def _norm_sign(sign: Union[str, Sign]) -> str:
    return sign.value if isinstance(sign, Sign) else str(sign).title()


def _one_based_degree(longitude: float) -> int:
    """0°00'..0°59' -> 1 ; 29°00'..29°59' -> 30."""
    return int(float(longitude) % 30.0) + 1


def _label_by_boundary(degree_1b: int, boundaries: List[List[Any]]) -> Optional[str]:
    """Return the label of the block containing `degree_1b`. Boundaries are
    [end_degree, label] ascending; the block is the first whose end >= degree."""
    for end_deg, label in boundaries or []:
        if degree_1b <= int(end_deg):
            return str(label)
    return None


class DegreeQualityEngine:
    @staticmethod
    def has_data(tradition: str = "lilly_1647") -> bool:
        t = DEGREE_QUALITIES.get(tradition, {})
        for cat in ("masculine_feminine", "light_dark_smoky_void", "pitted", "azimene", "increasing_fortune"):
            if any(v for v in (t.get(cat) or {}).values()):
                return True
        return False

    @staticmethod
    def lookup(longitude: float, tradition: str = "lilly_1647") -> Dict[str, Any]:
        """Degree-quality card for an ecliptic longitude. Always returns sign +
        one-based degree; quality fields are None/False if the tradition is empty."""
        t = DEGREE_QUALITIES.get(tradition, {})
        sign_idx = int(float(longitude) / 30.0) % 12
        sign = _SIGNS[sign_idx]
        deg = _one_based_degree(longitude)

        mf = _label_by_boundary(deg, (t.get("masculine_feminine") or {}).get(sign, []))
        ldsv = _label_by_boundary(deg, (t.get("light_dark_smoky_void") or {}).get(sign, []))
        pitted = deg in ((t.get("pitted") or {}).get(sign, []) or [])
        azimene = deg in ((t.get("azimene") or {}).get(sign, []) or [])
        incr = deg in ((t.get("increasing_fortune") or {}).get(sign, []) or [])

        notes: List[str] = []
        if mf:
            notes.append(INTERPRETATIONS["masculine_feminine"])
        if ldsv and ldsv in INTERPRETATIONS:
            notes.append(INTERPRETATIONS[ldsv])
        if pitted:
            notes.append(INTERPRETATIONS["pitted"])
        if azimene:
            notes.append(INTERPRETATIONS["azimene"])
        if incr:
            notes.append(INTERPRETATIONS["increasing_fortune"])

        return {
            "sign": sign,
            "degree_one_based": deg,
            "tradition": tradition,
            "source": t.get("source"),
            "masculine_feminine": mf,  # "M" | "F" | None
            "light_dark_smoky_void": ldsv,  # "light"|"dark"|"smoky"|"void"|None
            "pitted": pitted,
            "azimene": azimene,
            "increasing_fortune": incr,
            "interpretations": notes,
            "data_available": DegreeQualityEngine.has_data(tradition),
        }
