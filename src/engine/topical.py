"""
Topical delineation engine (deterministic).

Implements the per-topic significator stack that traditional natal delineation
requires but that the engine previously left to the narrative (LLM) layer to
improvise:

  1. The Twelve Topoi (Whole Sign houses): for each house -> sign, domicile lord,
     the lord's *condition* (read from the forensic payload), occupants, and a
     terse deterministic condition tag with its raw reasons.
  2. Natural / universal significators per topic (Hellenistic), so each life
     topic is judged by House + House-ruler + Natural significator (+ Lot),
     never by house alone.
  3. Derived ("turned") houses for the relational topics (4th = parents,
     5th = children, 7th = spouse, 10th = praxis/mother): e.g. the spouse's
     wealth = 2nd-from-7th = radical 8th.
  4. Places relative to the Lot of Fortune (esp. the 11th-from-Fortune, the
     "Place of Acquisition").

Sources:
  - Valens, Anthology II (significations of the twelve places).
  - Paulus Alexandrinus, Introduction 24 (the twelve topoi).
  - Ptolemy, Tetrabiblos III.4-6 (natural significators of parents, marriage,
    children); IV.4 (action / the lord of praxis: the orientality of Mercury,
    Venus, Mars).
  - Dorotheus, Carmen Astrologicum II (marriage significators by sex: Venus for
    men, Mars for women).

NOTE ON ALTITUDE: this layer emits FACTS + a terse condition tag only. The
prose synthesis remains the job of the narrative layer; this module exists so
the narrative cannot *fabricate* the ruler-condition chain — it must cite it.
"""

from typing import Any, Dict, List, Optional

from .models import PlanetName, Sect, Sign
from .reference_data import DETRIMENTS, DOMICILES, EXALTATIONS, FALLS

_SIGNS = list(Sign)

# Whole-sign topical significations. Phrasing intentionally tracks the premium
# prompt's RULE 3 house table so the deterministic layer and the doctrine layer
# never disagree.
HOUSE_TOPICS = {
    1: "Life, body, vitality, spirit, appearance",
    2: "Movable property, money, livelihood, allies",
    3: "Siblings, neighbors, short journeys, rumors and letters",
    4: "Father, land, ancestry, foundations, end of the matter",
    5: "Children, pleasure, sex, gifts, ambassadors",
    6: "Sickness, injury, servants, small animals, toil, bad fortune",
    7: "Marriage and spouse, open enemies, lawsuits, contracts",
    8: "Death, inheritance, others' money, fear, idleness",
    9: "God, religion, long journeys, dreams, divination, foreign lands",
    10: "Action (praxis), rank, reputation, career, mother",
    11: "Friends, hopes, benefactors, Good Spirit, alliances",
    12: "Hidden enemies, prison, sorrow, loss, large animals, Bad Spirit",
}

# Whole-sign aspectual configuration by sign-distance. Two signs are configured
# (in aspect) at conjunction(0), sextile(2), square(3), trine(4), opposition(6)
# and their mirrors. The remaining distances {1, 5, 7, 11} are AVERSION
# (semisextile 30deg / inconjunct 150deg): a planet cannot see the place.
_IN_ASPECT = {0, 2, 3, 4, 6, 8, 9, 10}
_AVERSION = {1, 5, 7, 11}


def _lon_of_lot(lot_entry: Any) -> Optional[float]:
    """Tolerantly extract an absolute longitude from a hermetic-lots entry."""
    if lot_entry is None:
        return None
    if isinstance(lot_entry, (int, float)):
        return float(lot_entry)
    if isinstance(lot_entry, dict):
        if lot_entry.get("longitude") is not None:
            try:
                return float(lot_entry["longitude"])
            except (TypeError, ValueError):
                pass
        fmt = lot_entry.get("longitude_fmt") or {}
        if isinstance(fmt, dict) and fmt.get("lon_abs") is not None:
            try:
                return float(fmt["lon_abs"])
            except (TypeError, ValueError):
                pass
    return None


def _sign_idx(lon: float) -> int:
    return int(lon / 30.0) % 12


def _house_of_sign_idx(sign_idx: int, asc_sign_idx: int) -> int:
    return ((sign_idx - asc_sign_idx) % 12) + 1


def _sign_of_house(house: int, asc_sign_idx: int) -> Sign:
    return _SIGNS[(asc_sign_idx + (house - 1)) % 12]


class TopicalEngine:
    # ---- Natural significators (Hellenistic). Each topic is judged by the
    # listed natural significator(s) AND the topical house AND any topical lot.
    # Sect-dependent significators are resolved against the chart's sect.
    @staticmethod
    def _natural_significators(sect: Sect) -> List[Dict[str, Any]]:
        is_day = sect == Sect.DAY
        return [
            {
                "topic": "Father",
                "house": 4,
                "significators": (
                    ["Sun", "Saturn"] if is_day else ["Saturn", "Sun"]
                ),
                "rule": "Ptolemy III.4: the Sun signifies the father by day, Saturn by night (the other is co-significator).",
            },
            {
                "topic": "Mother",
                "house": 10,
                "significators": (
                    ["Venus", "Moon"] if is_day else ["Moon", "Venus"]
                ),
                "rule": "Ptolemy III.4: the Moon and Venus signify the mother (Venus by day, Moon by night as primary). 10th is the Valens place of the mother; 4th is also used for parents.",
            },
            {
                "topic": "Siblings",
                "house": 3,
                "significators": ["Mars"],
                "rule": "3rd place of siblings; Mars taken as natural significator of brothers in the medieval tradition (fork: some use the bound-lord of the 3rd).",
            },
            {
                "topic": "Marriage (native male)",
                "house": 7,
                "significators": ["Venus"],
                "rule": "Dorotheus II: Venus signifies the wife for a male native; the 7th place and its lord co-signify.",
            },
            {
                "topic": "Marriage (native female)",
                "house": 7,
                "significators": ["Mars", "Jupiter"],
                "rule": "Dorotheus II: Mars (and Jupiter) signifies the husband for a female native; the 7th place and its lord co-signify.",
            },
            {
                "topic": "Children",
                "house": 5,
                "significators": ["Jupiter"],
                "rule": "Jupiter is the natural significator of children; the 5th place and its lord co-signify.",
            },
            {
                "topic": "Wealth / Livelihood",
                "house": 2,
                "significators": ["Jupiter"],
                "rule": "Jupiter is the natural significator of wealth; judged with the Lot of Fortune, the 2nd place and its lord, and the 11th-from-Fortune (Place of Acquisition).",
            },
            {
                "topic": "Action / Career (Praxis)",
                "house": 10,
                "significators": ["Mercury", "Venus", "Mars"],
                "rule": "Ptolemy IV.4 / Valens: the lord of action is found among Mercury, Venus, Mars — preferring the one making a morning (oriental) phasis or culminating; judged with the 10th, its lord, and the Lot of Spirit.",
            },
            {
                "topic": "Friends / Patrons",
                "house": 11,
                "significators": ["Jupiter"],
                "rule": "11th is the place of the Good Spirit (friends, hopes, benefactors); Jupiter co-signifies benefaction.",
            },
            {
                "topic": "Enemies / Illness",
                "house": 6,
                "significators": [],
                "rule": "6th (illness, injury, subordinates) and 12th (hidden enemies); judged primarily by the malefic contrary to the sect.",
            },
            {
                "topic": "Death",
                "house": 8,
                "significators": ["Saturn"],
                "rule": "8th place of death; cross-referenced with the Anareta from the vitality audit. Saturn taken as the general significator of endings.",
            },
            {
                "topic": "Religion / Travel",
                "house": 9,
                "significators": ["Jupiter"],
                "rule": "9th place of God, divination, and long journeys; Jupiter co-signifies religion.",
            },
        ]

    @staticmethod
    def _condition(pf_entry: Optional[Dict[str, Any]], asc_sign_idx: int) -> Dict[str, Any]:
        """Read a planet's condition from its forensic payload + compute its
        whole-sign house authoritatively from longitude (strict WSH)."""
        if not pf_entry:
            return {"available": False}

        lon = float(pf_entry.get("longitude") or 0.0)
        sidx = _sign_idx(lon)
        sign = _SIGNS[sidx].value
        house = _house_of_sign_idx(sidx, asc_sign_idx)
        dignities = pf_entry.get("dignities") or {}
        dig = dignities.get("total_score")
        try:
            dig = int(dig) if dig is not None else None
        except (TypeError, ValueError):
            dig = None
        # Peregrine is read from the breakdown, NOT inferred from a total of 0:
        # a planet can net 0 by holding minor dignities that its fall cancels,
        # which is NOT peregrine. Peregrine = none of the five essential
        # dignities AND not in detriment/fall.
        bd = dignities.get("score_breakdown") or {}
        _positives = sum(
            bd.get(_k, 0) or 0
            for _k in ("domicile", "exaltation", "triplicity", "term", "face")
        )
        _in_fall_det = (bd.get("fall", 0) or 0) < 0 or (bd.get("detriment", 0) or 0) < 0
        is_peregrine = (_positives == 0) and not _in_fall_det
        retro = bool(pf_entry.get("retrograde"))
        solar = (pf_entry.get("solar_status") or "FREE").upper()
        malt = pf_entry.get("maltreatments") or []
        malt_n = len(malt) if isinstance(malt, list) else 0

        angular = house in (1, 4, 7, 10)
        succedent = house in (2, 5, 8, 11)
        cadent = house in (3, 6, 9, 12)

        # Deterministic, fully-transparent condition index. This is a heuristic
        # ranking aid, NOT a textual claim — every contributing reason is listed.
        reasons: List[str] = []
        score = 0
        if is_peregrine:
            score -= 2
            reasons.append("peregrine (no essential dignity, not in fall/detriment)")
        elif dig is not None:
            if dig <= -4:
                score -= 2
                reasons.append(f"essentially debilitated ({dig:+d})")
            elif dig < 0:
                score -= 1
                reasons.append(f"essentially weak ({dig:+d})")
            elif dig >= 4:
                score += 2
                reasons.append(f"essential dignity strong ({dig:+d})")
            elif dig >= 1:
                score += 1
                reasons.append(f"minor essential dignity ({dig:+d})")
            else:
                reasons.append(
                    "essential dignity net-neutral (minor dignities offset by fall/detriment)"
                )
        if angular:
            score += 1
            reasons.append(f"angular (house {house})")
        elif cadent:
            score -= 1
            reasons.append(f"cadent (house {house})")
        else:
            reasons.append(f"succedent (house {house})")
        if solar == "CAZIMI":
            score += 1
            reasons.append("cazimi (heart of the Sun)")
        elif solar in ("COMBUST", "UNDER_BEAMS", "MOON_UNDER_BEAMS", "DARK_MOON"):
            score -= 2
            reasons.append(f"afflicted by the Sun ({solar.title().replace('_', ' ')})")
        if retro:
            score -= 1
            reasons.append("retrograde")
        if malt_n:
            score -= 2
            reasons.append(f"maltreatment/kakosis ({malt_n})")

        if score >= 3:
            band = "well-supported"
        elif score >= 1:
            band = "supported"
        elif score == 0:
            band = "mixed"
        elif score >= -2:
            band = "impaired"
        else:
            band = "severely impaired"

        return {
            "available": True,
            "sign": sign,
            "house": house,
            "essential_dignity_score": dig,
            "retrograde": retro,
            "solar_status": solar,
            "maltreatment_count": malt_n,
            "placement": "angular" if angular else ("cadent" if cadent else "succedent"),
            "condition_index": score,
            "condition_band": band,
            "reasons": reasons,
            "_note": "condition_band is a deterministic heuristic over essential dignity, angularity, solar condition, retrogradation, and maltreatment. It is a ranking aid; cite the listed reasons, not the number, as authority.",
        }

    @staticmethod
    def build(
        ascendant_lon: float,
        sect: Sect,
        planets_forensic: List[Dict[str, Any]],
        hermetic_lots: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Construct the deterministic topical layer. Never raises; on partial
        failure it degrades to whatever it could compute."""
        out: Dict[str, Any] = {
            "_doc": "Deterministic topical stack: Twelve Topoi (with ruler-condition chains), natural significators, derived (turned) houses, and places-from-Fortune. The narrative layer MUST cite these rather than re-deriving the ruler chain.",
        }
        try:
            asc_sign_idx = _sign_idx(float(ascendant_lon))
            pf_by_name = {
                str(p.get("name")): p for p in (planets_forensic or []) if p.get("name")
            }

            # ---------------- 1. The Twelve Topoi ----------------
            topoi = []
            for house in range(1, 13):
                hsign = _sign_of_house(house, asc_sign_idx)
                ruler = DOMICILES[hsign]
                exalt = EXALTATIONS.get(hsign)
                ruler_cond = TopicalEngine._condition(
                    pf_by_name.get(ruler.value), asc_sign_idx
                )

                # Ruler-in-aversion-to-its-own-place (cannot regard the topic).
                in_aversion = None
                if ruler_cond.get("available"):
                    rsidx = _sign_idx(float(pf_by_name[ruler.value].get("longitude") or 0.0))
                    step = (rsidx - _SIGNS.index(hsign)) % 12
                    in_aversion = step in _AVERSION

                occupants = []
                for name, pf in pf_by_name.items():
                    if name in ("North_Node", "South_Node"):
                        continue
                    if _sign_idx(float(pf.get("longitude") or 0.0)) == _SIGNS.index(hsign):
                        occupants.append(name)

                topoi.append(
                    {
                        "house": house,
                        "topic": HOUSE_TOPICS[house],
                        "sign": hsign.value,
                        "ruler": ruler.value,
                        "exaltation_ruler": exalt.value if exalt else None,
                        "ruler_condition": ruler_cond,
                        "ruler_in_aversion_to_its_house": in_aversion,
                        "aversion_note": (
                            "The lord of this place is in aversion to it (30/150 deg, whole-sign) and cannot regard its own topic — a structural disconnect."
                            if in_aversion
                            else None
                        ),
                        "occupants": occupants,
                    }
                )
            out["twelve_topoi"] = topoi

            # ---------------- 2. Natural significators ----------------
            sigs = []
            for spec in TopicalEngine._natural_significators(sect):
                resolved = []
                for sname in spec["significators"]:
                    resolved.append(
                        {
                            "planet": sname,
                            "condition": TopicalEngine._condition(
                                pf_by_name.get(sname), asc_sign_idx
                            ),
                        }
                    )
                hsign = _sign_of_house(spec["house"], asc_sign_idx)
                sigs.append(
                    {
                        "topic": spec["topic"],
                        "house": spec["house"],
                        "house_sign": hsign.value,
                        "house_ruler": DOMICILES[hsign].value,
                        "natural_significators": resolved,
                        "rule": spec["rule"],
                    }
                )
            out["natural_significators"] = sigs

            # ---------------- 3. Derived / turned houses ----------------
            # For each relational base, expose the turned topical points most used
            # in delineation, mapped back to the radical whole-sign house.
            base_labels = {
                1: "Native",
                4: "Father / Parents",
                5: "Children",
                7: "Spouse / Partner",
                9: "Mentors / Foreign",
                10: "Mother / Vocation",
            }
            turned_points = {
                1: "self/body",
                2: "wealth",
                4: "home/end",
                7: "their partner",
                10: "career/standing",
            }
            derived = []
            for base, blabel in base_labels.items():
                ring = []
                for k, klabel in turned_points.items():
                    radical_house = ((base - 1) + (k - 1)) % 12 + 1
                    rsign = _sign_of_house(radical_house, asc_sign_idx)
                    ring.append(
                        {
                            "turned_house": k,
                            "meaning": f"{blabel}'s {klabel}",
                            "radical_house": radical_house,
                            "radical_sign": rsign.value,
                            "radical_ruler": DOMICILES[rsign].value,
                        }
                    )
                derived.append({"base_house": base, "base_topic": blabel, "turned": ring})
            out["derived_houses"] = derived

            # ---------------- 4. Places from the Lot of Fortune ----------------
            fortune_lon = _lon_of_lot((hermetic_lots or {}).get("Fortune"))
            if fortune_lon is not None:
                f_sidx = _sign_idx(fortune_lon)
                fortune_places = []
                # 1st (Fortune itself / body & fortune), 2nd (substance from Fortune),
                # 6th (injury from Fortune), 11th (Place of Acquisition / Good Spirit
                # of Fortune — the traditional wealth significator).
                place_labels = {
                    1: "Body & Fortune (the Lot itself)",
                    2: "Substance derived from Fortune",
                    6: "Injury / servitude from Fortune",
                    11: "Place of Acquisition (Good Spirit of Fortune) — wealth",
                }
                for k, klabel in place_labels.items():
                    sidx = (f_sidx + (k - 1)) % 12
                    psign = _SIGNS[sidx]
                    fortune_places.append(
                        {
                            "place_from_fortune": k,
                            "meaning": klabel,
                            "sign": psign.value,
                            "ruler": DOMICILES[psign].value,
                            "radical_house": _house_of_sign_idx(sidx, asc_sign_idx),
                        }
                    )
                out["places_from_fortune"] = {
                    "fortune_sign": _SIGNS[f_sidx].value,
                    "places": fortune_places,
                    "rule": "Hellenistic derived-from-Fortune technique: the 11th-from-Fortune is the Place of Acquisition, a primary testimony for wealth alongside the 2nd house and Jupiter.",
                }
        except Exception as exc:  # never break the audit
            out["error"] = f"topical computation degraded: {exc!r}"
        return out
