from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
import secrets
from typing import Any, Sequence


Line = int
Rows = tuple[Line, Line, Line, Line]

ELEMENTS = ("fire", "air", "water", "earth")
SAFETY_NOTICE = (
    "Historical Use Only. This geomancy cast is for historical, spiritual, "
    "and research use only. It is not medical, financial, legal, emergency, "
    "psychological, or safety advice."
)


@dataclass(frozen=True)
class FigureDefinition:
    slug: str
    name: str
    translation: str
    rows: Rows
    ruling_element: str
    quality: str
    score: int
    summary: str

    @property
    def active_elements(self) -> list[str]:
        return [element for element, value in zip(ELEMENTS, self.rows) if value == 1]


FIGURE_DEFINITIONS: tuple[FigureDefinition, ...] = (
    FigureDefinition(
        "via",
        "Via",
        "Way",
        (1, 1, 1, 1),
        "water",
        "mobile",
        0,
        "movement, change, roads, travel, and unstable conditions",
    ),
    FigureDefinition(
        "populus",
        "Populus",
        "People",
        (2, 2, 2, 2),
        "water",
        "stable",
        0,
        "a crowd, public conditions, receptivity, and a situation shaped by others",
    ),
    FigureDefinition(
        "fortuna_major",
        "Fortuna Major",
        "Greater Fortune",
        (2, 2, 1, 1),
        "earth",
        "stable",
        2,
        "enduring support, strong foundations, and success through established strength",
    ),
    FigureDefinition(
        "fortuna_minor",
        "Fortuna Minor",
        "Lesser Fortune",
        (1, 1, 2, 2),
        "fire",
        "mobile",
        1,
        "temporary help, a window of luck, and success that must be used quickly",
    ),
    FigureDefinition(
        "conjunctio",
        "Conjunctio",
        "Joining",
        (2, 1, 1, 2),
        "air",
        "mobile",
        1,
        "meeting, union, exchange, negotiation, and a matter being brought together",
    ),
    FigureDefinition(
        "carcer",
        "Carcer",
        "Prison",
        (1, 2, 2, 1),
        "earth",
        "stable",
        -2,
        "restriction, delay, enclosure, binding, and a matter held in place",
    ),
    FigureDefinition(
        "tristitia",
        "Tristitia",
        "Sorrow",
        (2, 2, 2, 1),
        "earth",
        "stable",
        -2,
        "heaviness, decline, disappointment, and a downward or burdensome result",
    ),
    FigureDefinition(
        "laetitia",
        "Laetitia",
        "Joy",
        (1, 2, 2, 2),
        "fire",
        "mobile",
        2,
        "elevation, relief, cheerfulness, and a matter opening upward",
    ),
    FigureDefinition(
        "albus",
        "Albus",
        "White",
        (2, 2, 1, 2),
        "water",
        "stable",
        1,
        "clarity, calm, counsel, purification, and a more measured outcome",
    ),
    FigureDefinition(
        "rubeus",
        "Rubeus",
        "Red",
        (2, 1, 2, 2),
        "air",
        "mobile",
        -2,
        "heat, disorder, urgency, conflict, and conditions that should be handled carefully",
    ),
    FigureDefinition(
        "puella",
        "Puella",
        "Girl",
        (1, 2, 1, 1),
        "water",
        "stable",
        1,
        "attraction, harmony, beauty, agreement, and a softening of the matter",
    ),
    FigureDefinition(
        "puer",
        "Puer",
        "Boy",
        (1, 1, 2, 1),
        "air",
        "mobile",
        -1,
        "force, impatience, contest, courage, and action that may be too sharp",
    ),
    FigureDefinition(
        "caput_draconis",
        "Caput Draconis",
        "Dragon's Head",
        (2, 1, 1, 1),
        "earth",
        "stable",
        2,
        "entrance, increase, beginning, opening, and a matter gaining a head",
    ),
    FigureDefinition(
        "cauda_draconis",
        "Cauda Draconis",
        "Dragon's Tail",
        (1, 1, 1, 2),
        "fire",
        "mobile",
        -2,
        "exit, release, ending, separation, and a matter losing its hold",
    ),
    FigureDefinition(
        "acquisitio",
        "Acquisitio",
        "Gain",
        (2, 1, 2, 1),
        "air",
        "stable",
        2,
        "acquisition, profit, increase, recovery, and drawing something in",
    ),
    FigureDefinition(
        "amissio",
        "Amissio",
        "Loss",
        (1, 2, 1, 2),
        "fire",
        "mobile",
        -2,
        "loss, spending, release, absence, and letting something go",
    ),
)

FIGURE_BY_ROWS = {definition.rows: definition for definition in FIGURE_DEFINITIONS}

HOUSE_ASSIGNMENTS: tuple[dict[str, Any], ...] = (
    {"house": 1, "role": "M1", "arabic": "الحياة", "english": "life"},
    {"house": 2, "role": "M2", "arabic": "المال", "english": "money"},
    {"house": 3, "role": "M3", "arabic": "الإخوة", "english": "siblings"},
    {"house": 4, "role": "M4", "arabic": "الوالدين", "english": "parents"},
    {"house": 5, "role": "D1", "arabic": "الأولاد", "english": "children"},
    {"house": 6, "role": "D2", "arabic": "الأمراض", "english": "illness"},
    {"house": 7, "role": "D3", "arabic": "الزواج", "english": "marriage"},
    {"house": 8, "role": "D4", "arabic": "الموت", "english": "death"},
    {"house": 9, "role": "N1", "arabic": "السفر", "english": "travel"},
    {"house": 10, "role": "N2", "arabic": "العز والرفعة", "english": "honor and elevation"},
    {"house": 11, "role": "N3", "arabic": "الرجاء والآمال", "english": "hope and aspirations"},
    {"house": 12, "role": "N4", "arabic": "الأعداء", "english": "enemies"},
    {"house": 13, "role": "W1", "arabic": "السائل", "english": "questioner"},
    {"house": 14, "role": "W2", "arabic": "المسؤول عنه", "english": "asked-about party"},
    {"house": 15, "role": "J", "arabic": "الميزان", "english": "judge / balance"},
    {"house": 16, "role": "R", "arabic": "العاقبة", "english": "outcome / end-result"},
)

ROLE_STAGE = {
    "M1": "mother",
    "M2": "mother",
    "M3": "mother",
    "M4": "mother",
    "D1": "daughter",
    "D2": "daughter",
    "D3": "daughter",
    "D4": "daughter",
    "N1": "niece",
    "N2": "niece",
    "N3": "niece",
    "N4": "niece",
    "W1": "witness",
    "W2": "witness",
    "J": "judge",
    "R": "outcome",
}

QUESTION_TOPICS: tuple[tuple[str, tuple[int, ...], tuple[str, ...]], ...] = (
    ("resources", (2, 11), ("money", "pay", "paid", "salary", "sale", "sell", "buy", "price", "debt", "resource")),
    ("work", (10, 11), ("job", "career", "client", "boss", "promotion", "contract", "business", "hire", "interview")),
    ("relationship", (7, 5, 11), ("love", "partner", "marriage", "date", "relationship", "friend", "reconcile")),
    ("travel", (9, 3), ("travel", "trip", "move", "relocate", "journey", "visit", "city")),
    ("lost item", (2, 4, 12), ("lost", "missing", "find", "found", "keys", "wallet", "phone")),
    ("message", (3, 7, 11), ("reply", "message", "email", "text", "call", "hear back", "response")),
    ("health", (6, 1), ("health", "illness", "sick", "doctor", "medical", "pain", "symptom")),
)


def _clean_question(question: str) -> str:
    cleaned = re.sub(r"\s+", " ", (question or "").strip())
    if not cleaned:
        raise ValueError("Question is required.")
    if len(cleaned) > 500:
        raise ValueError("Question must be 500 characters or fewer.")
    return cleaned


def reduce_count_to_line(count: int) -> Line:
    if not isinstance(count, int):
        raise ValueError("Line counts must be integers.")
    if count <= 0:
        raise ValueError("Line counts must be positive integers.")
    return 1 if count % 2 else 2


def combine_line(left: Line, right: Line) -> Line:
    _validate_line(left)
    _validate_line(right)
    return 2 if left == right else 1


def combine_rows(left: Rows, right: Rows) -> Rows:
    return tuple(combine_line(a, b) for a, b in zip(left, right))  # type: ignore[return-value]


def counts_to_mothers(counts: Sequence[int]) -> tuple[Rows, Rows, Rows, Rows]:
    if len(counts) != 16:
        raise ValueError("Exactly 16 line counts are required: four rows for each of four mothers.")
    rows = [reduce_count_to_line(int(count)) for count in counts]
    return (
        tuple(rows[0:4]),  # type: ignore[return-value]
        tuple(rows[4:8]),  # type: ignore[return-value]
        tuple(rows[8:12]),  # type: ignore[return-value]
        tuple(rows[12:16]),  # type: ignore[return-value]
    )


def normalize_mothers(mothers: Sequence[Sequence[int]]) -> tuple[Rows, Rows, Rows, Rows]:
    if len(mothers) != 4:
        raise ValueError("Exactly four mother figures are required.")
    normalized: list[Rows] = []
    for index, figure in enumerate(mothers, start=1):
        if len(figure) != 4:
            raise ValueError(f"Mother {index} must have exactly four rows.")
        row = tuple(int(value) for value in figure)
        for value in row:
            _validate_line(value)
        normalized.append(row)  # type: ignore[arg-type]
    return tuple(normalized)  # type: ignore[return-value]


def generate_secure_counts() -> list[int]:
    return [secrets.randbelow(16) + 5 for _ in range(16)]


def build_shield(mothers: Sequence[Rows]) -> dict[str, Rows]:
    if len(mothers) != 4:
        raise ValueError("Exactly four mothers are required.")
    m1, m2, m3, m4 = mothers
    daughters = (
        (m1[0], m2[0], m3[0], m4[0]),
        (m1[1], m2[1], m3[1], m4[1]),
        (m1[2], m2[2], m3[2], m4[2]),
        (m1[3], m2[3], m3[3], m4[3]),
    )
    n1 = combine_rows(m1, m2)
    n2 = combine_rows(m3, m4)
    n3 = combine_rows(daughters[0], daughters[1])
    n4 = combine_rows(daughters[2], daughters[3])
    w1 = combine_rows(n1, n2)
    w2 = combine_rows(n3, n4)
    judge = combine_rows(w1, w2)
    outcome = combine_rows(m1, judge)
    return {
        "M1": m1,
        "M2": m2,
        "M3": m3,
        "M4": m4,
        "D1": daughters[0],
        "D2": daughters[1],
        "D3": daughters[2],
        "D4": daughters[3],
        "N1": n1,
        "N2": n2,
        "N3": n3,
        "N4": n4,
        "W1": w1,
        "W2": w2,
        "J": judge,
        "R": outcome,
    }


def cast_geomancy(
    question: str,
    *,
    mother_counts: Sequence[int] | None = None,
    mothers: Sequence[Sequence[int]] | None = None,
) -> dict[str, Any]:
    cleaned_question = _clean_question(question)
    generated_counts: list[int] | None = None

    if mother_counts is not None and mothers is not None:
        raise ValueError("Provide either mother_counts or mothers, not both.")
    if mother_counts is not None:
        normalized_mothers = counts_to_mothers(mother_counts)
        generation_method = "user_line_counts"
        raw_counts = [int(count) for count in mother_counts]
    elif mothers is not None:
        normalized_mothers = normalize_mothers(mothers)
        generation_method = "user_mother_rows"
        raw_counts = None
    else:
        generated_counts = generate_secure_counts()
        normalized_mothers = counts_to_mothers(generated_counts)
        generation_method = "server_secure_random_counts"
        raw_counts = generated_counts

    shield = build_shield(normalized_mothers)
    shield_entries = [_shield_entry(assignment, shield[assignment["role"]]) for assignment in HOUSE_ASSIGNMENTS]
    judge = shield["J"]
    outcome = shield["R"]
    left_witness = shield["W1"]
    right_witness = shield["W2"]
    judge_points = sum(judge)
    valid = judge_points % 2 == 0
    topic = classify_question(cleaned_question)
    judgement = _judge(judge, outcome, left_witness, right_witness, valid)

    return {
        "question": cleaned_question,
        "cast_at": datetime.now(timezone.utc).isoformat(),
        "generation_method": generation_method,
        "raw_counts": raw_counts,
        "mothers": [list(rows) for rows in normalized_mothers],
        "shield": shield_entries,
        "judge": _figure_payload(judge),
        "outcome": _figure_payload(outcome),
        "witnesses": {
            "questioner": _figure_payload(left_witness),
            "asked_about": _figure_payload(right_witness),
        },
        "validity": {
            "valid": valid,
            "judge_total_points": judge_points,
            "rule": "The fifteenth figure / judge must have an even total of points.",
            "message": (
                "Valid shield: the judge has an even total of points."
                if valid
                else "Invalid shield: the judge has an odd total, so the cast should be repeated from the mothers."
            ),
        },
        "topic": topic,
        "judgement": judgement,
        "safety_notice": SAFETY_NOTICE,
        "source_basis": {
            "procedural_source": "C:\\Users\\admin\\Downloads\\deep-research-report.md",
            "implemented_rules": [
                "four mothers reduced by odd/even parity",
                "daughters read from mother rows",
                "nieces, witnesses, judge, and outcome produced by row-wise parity combination",
                "houses 1-16 follow the Arabic handbook order listed in the report",
                "judge evenness validation is enforced and reported",
            ],
            "figure_name_note": (
                "Latin figure names are conventional display labels for the 16 row patterns; "
                "the report itself cautions that source-specific semantic gloss tables still need direct extraction."
            ),
        },
    }


def classify_question(question: str) -> dict[str, Any]:
    lowered = question.lower()
    for topic, houses, keywords in QUESTION_TOPICS:
        if any(keyword in lowered for keyword in keywords):
            return {
                "label": topic,
                "relevant_houses": list(houses),
                "matched_keywords": [keyword for keyword in keywords if keyword in lowered],
            }
    return {"label": "general", "relevant_houses": [13, 14, 15, 16], "matched_keywords": []}


def _judge(judge: Rows, outcome: Rows, left_witness: Rows, right_witness: Rows, valid: bool) -> dict[str, Any]:
    judge_def = FIGURE_BY_ROWS[judge]
    outcome_def = FIGURE_BY_ROWS[outcome]
    left_def = FIGURE_BY_ROWS[left_witness]
    right_def = FIGURE_BY_ROWS[right_witness]
    score = judge_def.score * 2 + outcome_def.score + left_def.score + right_def.score

    if not valid:
        verdict = "INVALID"
        weight = "recast"
    elif score >= 5:
        verdict = "FAVORABLE"
        weight = "strong"
    elif score >= 2:
        verdict = "LEANING FAVORABLE"
        weight = "moderate"
    elif score <= -5:
        verdict = "UNFAVORABLE"
        weight = "strong"
    elif score <= -2:
        verdict = "LEANING UNFAVORABLE"
        weight = "moderate"
    else:
        verdict = "MIXED"
        weight = "balanced"

    return {
        "verdict": verdict,
        "weight": weight,
        "score": score,
        "summary": _judgement_summary(judge_def, outcome_def, left_def, right_def, verdict, valid),
        "notes": [
            f"Questioner witness: {left_def.name} ({left_def.summary}).",
            f"Asked-about witness: {right_def.name} ({right_def.summary}).",
            f"Judge: {judge_def.name} ({judge_def.summary}).",
            f"Outcome: {outcome_def.name} ({outcome_def.summary}).",
        ],
    }


def _judgement_summary(
    judge: FigureDefinition,
    outcome: FigureDefinition,
    left_witness: FigureDefinition,
    right_witness: FigureDefinition,
    verdict: str,
    valid: bool,
) -> str:
    if not valid:
        return (
            "The shield arithmetic produced an odd-point judge. In the procedure described by the report, "
            "that means the cast should be repeated rather than interpreted."
        )
    return (
        f"The judge is {judge.name}, so the central balance of the cast shows {judge.summary}. "
        f"The outcome is {outcome.name}, pointing to {outcome.summary}. "
        f"With {left_witness.name} for the questioner and {right_witness.name} for the asked-about side, "
        f"the mechanical tendency is {verdict.lower()}."
    )


def _shield_entry(assignment: dict[str, Any], rows: Rows) -> dict[str, Any]:
    payload = _figure_payload(rows)
    payload.update(
        {
            "house": assignment["house"],
            "role": assignment["role"],
            "stage": ROLE_STAGE[assignment["role"]],
            "house_arabic": assignment["arabic"],
            "house_english": assignment["english"],
        }
    )
    return payload


def _figure_payload(rows: Rows) -> dict[str, Any]:
    definition = FIGURE_BY_ROWS[rows]
    return {
        "slug": definition.slug,
        "name": definition.name,
        "translation": definition.translation,
        "rows": list(rows),
        "dots": ["." if row == 1 else ".." for row in rows],
        "total_points": sum(rows),
        "active_elements": definition.active_elements,
        "ruling_element": definition.ruling_element,
        "quality": definition.quality,
        "summary": definition.summary,
    }


def _validate_line(value: int) -> None:
    if value not in {1, 2}:
        raise ValueError("Geomantic rows must be 1 for single/odd or 2 for double/even.")
