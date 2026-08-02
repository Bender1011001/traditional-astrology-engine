"""Cross-tradition convergence: where independent systems agree, and where they don't.

This layer exists because agreement between systems that share no mathematics is
the one claim a single-tradition practitioner cannot make. It is also the easiest
place in the whole product to mislead, so the rules here are strict:

1. **Independence is computed, not assumed.** Western, Islamicate, and medieval
   Jewish share one calculation core; Western and Vedic whole-sign house numbers
   are identical by construction because every point shifts back one sign
   together. Agreements inside a shared-basis group are reported as ONE voice,
   not several.
2. **Disagreements get equal billing.** A convergence page that only lists
   agreements is a horoscope, not an analysis.
3. **No claim is invented here.** This layer only reads facts other sections
   already computed and disclosed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Sections sharing a calculation basis count as one independent voice.
# Western/Islamicate/Jewish: literally the same tropical chart object.
# Western/Vedic: whole-sign house NUMBERS coincide because the ascendant shifts
# back one sign in lockstep with every planet - so house-placement agreement
# between them is an identity, not evidence.
SHARED_BASIS_GROUPS: dict[str, tuple[str, ...]] = {
    "hellenistic_core": (
        "western_traditional",
        "islamicate_persian",
        "medieval_jewish",
    ),
    "sexagenary_core": ("chinese_bazi", "tibetan", "vietnamese", "ziwei_doushu"),
    "mesoamerican_count": ("maya", "nahua_central_mexican"),
}


def _basis_of(tradition_id: str) -> str:
    for basis, members in SHARED_BASIS_GROUPS.items():
        if tradition_id in members:
            return basis
    return tradition_id


@dataclass
class Convergence:
    topic: str
    statement: str
    supporting: list[str] = field(default_factory=list)
    independent_voices: int = 0
    caveat: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "topic": self.topic,
            "statement": self.statement,
            "supporting_traditions": self.supporting,
            "independent_voices": self.independent_voices,
        }
        if self.caveat:
            payload["caveat"] = self.caveat
        return payload


def _section_map(panel: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        s["tradition_id"]: s
        for s in panel["sections"]
        if not s.get("error")
    }


def _voices(tradition_ids: list[str]) -> int:
    return len({_basis_of(t) for t in tradition_ids})


def build(panel: dict[str, Any]) -> dict[str, Any]:
    """Compare what the sections already computed. Invents nothing."""
    sections = _section_map(panel)
    agreements: list[Convergence] = []
    disagreements: list[Convergence] = []

    # --- Timing: which years/periods do independent clocks flag? ---
    timing_sources: list[str] = []
    timing_detail: list[str] = []

    vedic = sections.get("indian_jyotisha")
    if vedic:
        dashas = vedic["facts"].get("vimshottari_mahadashas") or []
        if dashas:
            timing_sources.append("indian_jyotisha")
            current = dashas[0]
            timing_detail.append(
                f"Vedic: Vimshottari {current['lord']} mahadasha "
                f"{current['start']} to {current['end']}"
            )

    bazi = sections.get("chinese_bazi")
    if bazi:
        luck = bazi["facts"].get("luck_pillars") or {}
        forward = (luck.get("sequences") or {}).get("forward") or []
        if forward:
            timing_sources.append("chinese_bazi")
            timing_detail.append(
                f"BaZi: luck pillars begin at age {luck.get('start_age')}, "
                f"first pillar {forward[0].get('label')} "
                f"({forward[0].get('start')})"
            )

    if _voices(timing_sources) >= 2:
        agreements.append(Convergence(
            topic="Timing systems present",
            statement=(
                "Two or more traditions with no shared timing mathematics each "
                "supply a period structure for this birth: " + "; ".join(timing_detail)
            ),
            supporting=timing_sources,
            independent_voices=_voices(timing_sources),
            caveat=(
                "Both systems produce periods, which is not the same as both "
                "flagging the same date. Period boundaries are reported "
                "separately and are NOT aligned or averaged here."
            ),
        ))

    # --- Sect / day-night: Hellenistic sect vs BaZi day-master polarity ---
    western = sections.get("western_traditional")
    if western and bazi:
        sect = western["facts"].get("sect")
        dm = bazi["facts"].get("day_master") or {}
        disagreements.append(Convergence(
            topic="Day/night and polarity",
            statement=(
                f"Hellenistic sect is {sect}; the BaZi day master is "
                f"{dm.get('polarity')} {dm.get('element')}. These are NOT "
                "equivalent concepts and must not be read as agreeing or "
                "disagreeing - sect is a chart-wide condition set by the Sun's "
                "position relative to the horizon, while polarity is an "
                "intrinsic property of one stem."
            ),
            supporting=["western_traditional", "chinese_bazi"],
            independent_voices=2,
            caveat="Listed to prevent a false equivalence, not as a finding.",
        ))

    # --- Structural: which traditions refuse to personalize? ---
    refusing = []
    for tid, section in sections.items():
        for disclosure in section.get("disclosures", []):
            if disclosure["kind"] == "refusal" and any(
                word in disclosure["detail"].lower()
                for word in ("personality", "day sign", "not a personality",
                             "cannot support", "no approved")
            ):
                refusing.append(tid)
                break
    if refusing:
        agreements.append(Convergence(
            topic="Traditions that decline to personalize",
            statement=(
                "These sections report structure but refuse a personal verdict, "
                "each for a source-specific reason stated in its own "
                "disclosures: " + ", ".join(sorted(set(refusing)))
            ),
            supporting=sorted(set(refusing)),
            independent_voices=_voices(sorted(set(refusing))),
            caveat=(
                "Refusals are findings about the surviving corpora, not gaps in "
                "this engine."
            ),
        ))

    # --- Evidence-grade spread ---
    grades: dict[str, list[str]] = {}
    for tid, section in sections.items():
        grades.setdefault(section["evidence_grade"], []).append(tid)

    return {
        "method_note": (
            "Agreement is only meaningful between traditions that share no "
            "mathematics. Sections are grouped by calculation basis and a "
            "shared-basis group counts as ONE independent voice. Western, "
            "Islamicate, and medieval Jewish share one tropical chart; Western "
            "and Vedic whole-sign house numbers coincide by construction and "
            "are therefore never counted as independent agreement on placement."
        ),
        "shared_basis_groups": {
            basis: [m for m in members if m in sections]
            for basis, members in SHARED_BASIS_GROUPS.items()
            if any(m in sections for m in members)
        },
        "independent_voice_count": _voices(list(sections)),
        "agreements": [a.to_dict() for a in agreements],
        "distinctions": [d.to_dict() for d in disagreements],
        "evidence_grade_spread": grades,
    }
