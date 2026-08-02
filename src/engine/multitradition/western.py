"""Western, Islamicate, and medieval Jewish sections over the live engine core.

These three share one calculation core - tropical positions, whole-sign or
quadrant houses, sect, dignity - and diverge in which techniques they layer on
top. Rather than recompute, the Islamicate and Jewish sections are profiles that
name their distinctive methods and their source packs.
"""

from __future__ import annotations

from typing import Any

from .types import BirthInput, DisclosureKind, EvidenceGrade, TraditionSection

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
CLASSICAL = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]


def _sign_of(longitude: float) -> tuple[str, float]:
    index = int((longitude % 360) // 30)
    return SIGNS[index], (longitude % 360) - index * 30


def build_western(birth: BirthInput, chart: Any) -> TraditionSection:
    section = TraditionSection(
        tradition_id="western_traditional",
        display_name="Western traditional (Hellenistic/medieval)",
        evidence_grade=EvidenceGrade.LIVE_ENGINE,
        basis=(
            "Tropical Swiss Ephemeris positions from the shipping engine, the same "
            "core that produces the live premium report."
        ),
    )
    section.disclose(
        DisclosureKind.SOURCE,
        "Engine provenance",
        "Positions produced by the live calculator. The shipping premium report "
        "carries the full judgment layer with per-claim evidence notes; this panel "
        "section reports the calculation basis only.",
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Houses",
        "Whole-sign houses are used for topical judgment, with the quadrant "
        "Midheaven reported separately, following the live report's convention.",
        ("Placidus", "Regiomontanus", "Alcabitius", "Porphyry"),
    )

    planet_map = {p.name.value: p for p in chart.planets}
    asc_sign, asc_degree = _sign_of(chart.ascendant)
    asc_index = SIGNS.index(asc_sign)
    mc_sign, mc_degree = _sign_of(chart.mc)

    placements = []
    for name in CLASSICAL:
        planet = planet_map.get(name)
        if planet is None:
            continue
        sign, degree = _sign_of(planet.longitude)
        placements.append({
            "body": name,
            "sign": sign,
            "degree_in_sign": round(degree, 4),
            "whole_sign_house": (SIGNS.index(sign) - asc_index) % 12 + 1,
            "retrograde": getattr(planet, "speed", 0.0) < 0,
        })

    sun_altitude = getattr(chart, "sun_altitude", 0.0)
    section.facts = {
        "ascendant": {"sign": asc_sign, "degree_in_sign": round(asc_degree, 4)},
        "midheaven": {"sign": mc_sign, "degree_in_sign": round(mc_degree, 4)},
        "sect": "day" if sun_altitude > 0 else "night",
        "sun_altitude_degrees": round(sun_altitude, 4),
        "placements": placements,
    }
    return section


def build_islamicate(birth: BirthInput, western: TraditionSection) -> TraditionSection:
    section = TraditionSection(
        tradition_id="islamicate_persian",
        display_name="Islamicate / Persian",
        evidence_grade=EvidenceGrade.VALIDATED_PACK,
        basis=(
            "Shares the Western calculation core. Distinctive layer: al-Biruni's "
            "reference conditions from the validated al-Biruni pack."
        ),
    )
    section.disclose(
        DisclosureKind.SOURCE,
        "Pack provenance",
        "Firdaria ordering, equal-seventh subperiod structure, sect and gender "
        "classifications, halb/hayyiz and their one-way implication come from the "
        "validated al-Biruni reference-condition pack, built from facing-page "
        "Arabic/English evidence.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Firdaria periods and ages",
        "The al-Biruni pack refuses node periods and age/date firdaria arithmetic "
        "because section 395 supplies neither node periods nor a major-duration "
        "table. Those values are therefore not emitted from this pack.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Abu Ma'shar and al-Qabisi doctrine",
        "Seven TEI witnesses are hash-pinned and 30 passage candidates are "
        "catalogued, including a Mars firdaria disagreement (Arabic 7 years vs "
        "Hermann 8) and an apparent al-Qabisi/al-Biruni Mercury difference. None "
        "is promoted to a rule pending controlling-edition collation.",
    )

    section.facts = {
        "sect": western.facts.get("sect"),
        "shared_calculation_core": "western_traditional",
        "distinctive_layers_available": [
            "al-Biruni reference conditions (validated)",
            "halb / hayyiz classification (validated)",
            "firdaria ordering, diurnal and nocturnal (validated)",
        ],
        "distinctive_layers_gated": [
            "firdaria period durations and dates",
            "Abu Ma'shar Great Introduction doctrine",
            "al-Qabisi Introduction doctrine",
            "lunar mansions",
        ],
    }
    return section


def build_medieval_jewish(
    birth: BirthInput, western: TraditionSection
) -> TraditionSection:
    section = TraditionSection(
        tradition_id="medieval_jewish",
        display_name="Medieval Jewish (Ibn Ezra)",
        evidence_grade=EvidenceGrade.VALIDATED_PACK,
        basis=(
            "Shares the Western calculation core. Distinctive layer: Ibn Ezra's "
            "Book of Revolutions method from the validated pack."
        ),
    )
    section.disclose(
        DisclosureKind.SOURCE,
        "Pack provenance",
        "Ibn Ezra revolutions rules come from a validated pack built on the "
        "parallel Hebrew-English critical edition, and already drive the "
        "solar-return layer of the live premium report.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Nativities treatise",
        "The Book of Nativities module remains source-limited: its rule and "
        "precedence extraction is not complete, so no natal doctrine specific to "
        "it is asserted here.",
    )

    section.facts = {
        "shared_calculation_core": "western_traditional",
        "distinctive_layers_available": [
            "Ibn Ezra annual revolution comparison (validated)",
            "sect-light triplicity ruler phases (validated)",
        ],
        "distinctive_layers_gated": ["Book of Nativities natal doctrine"],
    }
    return section
