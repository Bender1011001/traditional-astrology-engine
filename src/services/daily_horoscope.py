"""Daily solar/rising-sign horoscopes from real transit positions.

The public daily horoscope is intentionally lighter than the personal Daily
Navigator, but it still uses Swiss Ephemeris positions for the date instead of
static copy. Interpretations are symbolic and historical-use only.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

import swisseph as swe


SIGN_NAMES = [
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

SIGN_RULERS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

PLANET_IDS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
}

PLANETARY_DAY_RULERS = [
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
    "Sun",
]

HOUSE_TOPICS = {
    1: "body, attention, and self-direction",
    2: "money, tools, and personal resources",
    3: "messages, siblings, study, and short trips",
    4: "home, family roots, and private foundations",
    5: "pleasure, children, craft, and creative output",
    6: "workload, maintenance, and practical obligations",
    7: "partners, clients, and visible agreements",
    8: "shared resources, debts, and other people's obligations",
    9: "learning, faith, travel, and counsel",
    10: "reputation, office, and public responsibility",
    11: "friends, patrons, audience, and long-range hopes",
    12: "rest, withdrawal, hidden strain, and unfinished business",
}

HOUSE_ACTIONS = {
    1: "keep the day simple and make one visible choice on your own behalf",
    2: "review what you own, owe, and need before committing resources",
    3: "answer the message, write the note, or handle the local errand",
    4: "stabilize the home base before taking on outside demands",
    5: "protect time for craft, delight, or a generous personal gesture",
    6: "finish one practical task and do not overfill the schedule",
    7: "make agreements explicit and listen before responding",
    8: "check terms, shared costs, and obligations before accepting them",
    9: "seek the clearer teaching, source, or wider frame",
    10: "put the public task in order and keep your word visibly",
    11: "use allies, audience, and professional friends wisely",
    12: "work quietly, rest deliberately, and avoid unnecessary exposure",
}

ASPECTS_BY_SIGN = {
    0: ("conjunction", "directly emphasizes"),
    2: ("sextile", "cooperates with"),
    3: ("square", "presses on"),
    4: ("trine", "supports"),
    6: ("opposition", "confronts"),
    8: ("trine", "supports"),
    9: ("square", "presses on"),
    10: ("sextile", "cooperates with"),
}


@dataclass(frozen=True)
class TransitPosition:
    name: str
    longitude: float
    speed: float

    @property
    def sign_index(self) -> int:
        return int(self.longitude // 30) % 12

    @property
    def sign(self) -> str:
        return SIGN_NAMES[self.sign_index]

    @property
    def degree(self) -> float:
        return self.longitude % 30

    @property
    def retrograde(self) -> bool:
        return self.speed < 0


def _configure_ephemeris_path() -> None:
    repo_ephe = Path(__file__).resolve().parents[1] / "ephe"
    configured = os.environ.get("SE_EPHE_PATH", "")
    parts = [str(repo_ephe)]
    parts.extend(part for part in configured.split(os.pathsep) if part)
    ephe_path = os.pathsep.join(dict.fromkeys(parts))
    os.environ["SE_EPHE_PATH"] = ephe_path
    swe.set_ephe_path(ephe_path)


def _calculate_position(jd: float, name: str, planet_id: int) -> TransitPosition:
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    try:
        coords = swe.calc_ut(jd, planet_id, flags)[0]
    except swe.Error:
        coords = swe.calc_ut(jd, planet_id, swe.FLG_MOSEPH | swe.FLG_SPEED)[0]
    return TransitPosition(
        name=name, longitude=float(coords[0]) % 360, speed=float(coords[3])
    )


def _sign_index(sign: str) -> int:
    return SIGN_NAMES.index(sign)


def _house_from(rising_sign_index: int, planet_sign_index: int) -> int:
    return ((planet_sign_index - rising_sign_index) % 12) + 1


def _sign_aspect(from_index: int, to_index: int) -> Optional[tuple[str, str]]:
    return ASPECTS_BY_SIGN.get((from_index - to_index) % 12)


def _lunar_phase(sun_lon: float, moon_lon: float) -> Dict[str, Any]:
    elongation = (moon_lon - sun_lon) % 360
    if elongation < 45:
        phase = "New Moon phase"
    elif elongation < 90:
        phase = "waxing crescent"
    elif elongation < 135:
        phase = "first quarter"
    elif elongation < 180:
        phase = "waxing gibbous"
    elif elongation < 225:
        phase = "Full Moon phase"
    elif elongation < 270:
        phase = "waning gibbous"
    elif elongation < 315:
        phase = "last quarter"
    else:
        phase = "waning crescent"
    return {
        "phase": phase,
        "elongation": round(elongation, 3),
        "waxing": elongation < 180,
    }


def _tone(score: int) -> str:
    if score >= 2:
        return "supportive"
    if score <= -2:
        return "cautious"
    return "mixed"


def _support_clause(
    sign_index: int, positions: Dict[str, TransitPosition]
) -> tuple[int, str]:
    clauses: List[str] = []
    score = 0
    for benefic in ("Venus", "Jupiter"):
        house = _house_from(sign_index, positions[benefic].sign_index)
        aspect = _sign_aspect(positions[benefic].sign_index, sign_index)
        if house in {1, 4, 7, 10} or (aspect and aspect[0] in {"sextile", "trine"}):
            score += 1
            clauses.append(f"{benefic} offers help from the {house}th house")
    if clauses:
        return score, "; ".join(clauses) + "."
    return (
        score,
        "The benefics are quieter today, so progress comes through ordinary diligence.",
    )


def _pressure_clause(
    sign_index: int, positions: Dict[str, TransitPosition]
) -> tuple[int, str]:
    clauses: List[str] = []
    score = 0
    for malefic in ("Mars", "Saturn"):
        house = _house_from(sign_index, positions[malefic].sign_index)
        aspect = _sign_aspect(positions[malefic].sign_index, sign_index)
        if house in {1, 4, 7, 10} or (aspect and aspect[0] in {"square", "opposition"}):
            score -= 1
            clauses.append(f"{malefic} asks for care around the {house}th-house topic")
    if clauses:
        return score, "; ".join(clauses) + "."
    return (
        score,
        "Mars and Saturn are not bearing down directly, which gives the day more room.",
    )


def generate_daily_horoscopes(target_date: date) -> Dict[str, Any]:
    """Return public daily horoscopes for all twelve signs."""
    _configure_ephemeris_path()
    jd = swe.julday(target_date.year, target_date.month, target_date.day, 12.0)
    positions = {
        name: _calculate_position(jd, name, planet_id)
        for name, planet_id in PLANET_IDS.items()
    }

    sun = positions["Sun"]
    moon = positions["Moon"]
    phase = _lunar_phase(sun.longitude, moon.longitude)
    day_ruler = PLANETARY_DAY_RULERS[target_date.weekday()]
    day_ruler_position = positions[day_ruler]

    horoscopes = []
    for sign_index, sign in enumerate(SIGN_NAMES):
        ruler_name = SIGN_RULERS[sign]
        ruler_position = positions[ruler_name]
        moon_house = _house_from(sign_index, moon.sign_index)
        ruler_house = _house_from(sign_index, ruler_position.sign_index)
        day_ruler_house = _house_from(sign_index, day_ruler_position.sign_index)

        score = 0
        moon_aspect = _sign_aspect(moon.sign_index, sign_index)
        if moon_aspect:
            if moon_aspect[0] in {"trine", "sextile", "conjunction"}:
                score += 1
            elif moon_aspect[0] in {"square", "opposition"}:
                score -= 1

        if ruler_position.retrograde:
            score -= 1

        support_score, support = _support_clause(sign_index, positions)
        pressure_score, pressure = _pressure_clause(sign_index, positions)
        score += support_score + pressure_score

        moon_relation = (
            f"The Moon in {moon.sign} {moon_aspect[1]} {sign}"
            if moon_aspect
            else f"The Moon in {moon.sign} does not make a whole-sign Ptolemaic aspect to {sign}"
        )
        retro_note = (
            f"{ruler_name} is retrograde, so revise before pushing ahead."
            if ruler_position.retrograde
            else f"{ruler_name} is direct, so its house topic can move more plainly."
        )

        summary = (
            f"{moon_relation}, drawing attention to {HOUSE_TOPICS[moon_house]}. "
            f"Your traditional ruler {ruler_name} is in {ruler_position.sign}, "
            f"placing emphasis on {HOUSE_TOPICS[ruler_house]}. {retro_note} "
            f"{support} {pressure}"
        )

        horoscopes.append(
            {
                "sign": sign,
                "ruler": ruler_name,
                "tone": _tone(score),
                "score": score,
                "moon_house": moon_house,
                "ruler_house": ruler_house,
                "planetary_day_house": day_ruler_house,
                "headline": f"{HOUSE_TOPICS[moon_house].capitalize()} come into focus.",
                "summary": summary,
                "action": HOUSE_ACTIONS[moon_house],
            }
        )

    return {
        "date": target_date.isoformat(),
        "disclaimer": "Historical Use Only - not medical, financial, or legal advice.",
        "method": (
            "Tropical zodiac, seven traditional planets, Swiss Ephemeris positions "
            "at 12:00 UTC, whole-sign topics from each sign as the first house."
        ),
        "sky": {
            "sun": {"sign": sun.sign, "degree": round(sun.degree, 3)},
            "moon": {"sign": moon.sign, "degree": round(moon.degree, 3)},
            "lunar_phase": phase,
            "planetary_day": {"ruler": day_ruler, "house_note": "computed per sign"},
            "positions": {
                name: {
                    "sign": pos.sign,
                    "degree": round(pos.degree, 3),
                    "retrograde": pos.retrograde,
                }
                for name, pos in positions.items()
            },
        },
        "horoscopes": horoscopes,
    }
