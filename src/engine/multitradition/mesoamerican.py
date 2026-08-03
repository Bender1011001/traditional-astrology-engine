"""Maya and Nahua sections.

Maya arithmetic comes from the validated `maya_calendar_kernel` pack, which
registers two correlation profiles and refuses to default silently - so both are
emitted side by side. The Nahua pack registers no civil-date correlation at all,
which is a finding rather than a gap: the section reports the cycle position only
under an explicitly non-historical fixture, and says so.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from .timebase import TimeBases
from .types import BirthInput, DisclosureKind, EvidenceGrade, TraditionSection

RESEARCH_ROOT = (
    Path(__file__).resolve().parents[3] / "docs" / "research" / "multitradition"
)
MAYA_SPEC = RESEARCH_ROOT / "maya" / "calendar_kernel_spec.json"
NAHUA_SPEC = RESEARCH_ROOT / "nahua" / "tonalpohualli_cycle_spec.json"
NAHUA_AUGURY_PACK = RESEARCH_ROOT / "nahua" / "book4_augury_pack.json"

# Lords of the Night are not encoded in the validated Maya pack; the nine-fold
# series is computed here under a disclosed configured formula.
LORDS_OF_NIGHT = [f"G{n}" for n in range(1, 10)]


@lru_cache(maxsize=2)
def _spec(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _emod(value: int, modulus: int) -> int:
    return value % modulus


def build_maya(birth: BirthInput, bases: TimeBases) -> TraditionSection:
    spec = _spec(MAYA_SPEC)
    section = TraditionSection(
        tradition_id="maya",
        display_name="Maya calendar",
        evidence_grade=EvidenceGrade.VALIDATED_PACK,
        basis=(
            "Long Count, Tzolk'in, and Haab arithmetic from the validated Maya "
            "calendar kernel, emitted under both registered correlations."
        ),
    )
    section.disclose(
        DisclosureKind.SOURCE,
        "Kernel provenance",
        "Cycle weights, radices, and position formulae come from the validated "
        "maya_calendar_kernel pack; day-name and month-name profiles are the "
        "Smithsonian 2012 Yucatec spellings the pack registers.",
    )
    section.disclose(
        DisclosureKind.FORK,
        "Correlation constant",
        "The pack registers GMT 584283 as a bounded research default and GMT "
        "584285 as an alternate sensitivity profile. Both are computed below; "
        "they shift every Maya date by two days.",
        ("GMT 584285",),
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Lords of the Night",
        "The nine-fold G-series is not encoded in the validated pack. It is "
        "computed here as G = (total_day mod 9) + 1 with G9 at total_day 8, the "
        "standard modern convention, and labeled configured rather than validated.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Day meanings",
        "Tzolk'in day-sign meanings are not asserted. The pack carries calendar "
        "arithmetic only; codical almanacs and living K'iche' daykeeping practice "
        "are separate source-limited modules.",
    
        category="policy_suppressed",
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Day boundary",
        "The integer JDN of the civil date is used. The pack's own semantics "
        "compare integer date identities and do not infer a birth-time instant, "
        "so the birth clock time does not affect this section.",
    )

    tzolkin_names = spec["tzolkin"]["name_profiles"]["yucatec_smithsonian_2012"]
    haab_months = spec["haab"]["month_names"]
    weights = spec["long_count"]["weights_days"]

    profiles: dict[str, Any] = {}
    for correlation_id, correlation in spec["correlations"].items():
        constant = correlation["constant"]
        total_day = bases.julian_day_number - constant

        remaining = total_day
        long_count: dict[str, int] = {}
        for unit in spec["long_count"]["component_order"]:
            long_count[unit] = remaining // weights[unit]
            remaining -= long_count[unit] * weights[unit]

        tzolkin_number = _emod(total_day + 3, 13) + 1
        tzolkin_name = tzolkin_names[_emod(total_day + 19, 20)]
        haab_position = _emod(total_day + 348, 365)
        haab_month = haab_months[haab_position // 20]
        haab_day = haab_position % 20
        lord = LORDS_OF_NIGHT[_emod(total_day + 1, 9)]

        profiles[correlation_id] = {
            "correlation_constant": constant,
            "status": correlation["status"],
            "integer_jdn": bases.julian_day_number,
            "total_day": total_day,
            "long_count": ".".join(
                str(long_count[u]) for u in spec["long_count"]["component_order"]
            ),
            "tzolkin": f"{tzolkin_number} {tzolkin_name}",
            "haab": f"{haab_day} {haab_month}",
            "lord_of_night": lord,
            "civil_calendar": spec["civil_date_contract"]["calendar"],
        }

    section.facts = {
        "correlation_profiles": profiles,
        "calendar_round_days": spec["calendar_round"]["length_days"],
    }
    return section


def build_nahua(birth: BirthInput, bases: TimeBases) -> TraditionSection:
    spec = _spec(NAHUA_SPEC)
    section = TraditionSection(
        tradition_id="nahua_central_mexican",
        display_name="Nahua tonalpohualli",
        evidence_grade=EvidenceGrade.VALIDATED_PACK,
        basis=(
            "13-by-20 cycle arithmetic from the validated tonalpohualli kernel. "
            "No historical civil-date correlation is available."
        ),
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Civil-date correlation",
        "The validated pack registers NO approved correlation between the "
        "tonalpohualli and the civil calendar, and explicitly forbids reusing a "
        "Maya correlation merely because both traditions run 260-day counts. "
        "The cycle position below is therefore computed under a labeled "
        "non-historical fixture and must not be read as this person's day sign.",
    
        category="school_fork_unresolved",
    )
    section.disclose(
        DisclosureKind.SOURCE,
        "Kernel provenance",
        "Day-sign order and the 260-position recurrence come from the validated "
        "nahua_tonalpohualli_cycle_v1 pack, anchored to Florentine Codex Book 4 "
        "folio 1r and the INAH-hosted trecena table.",
    )

    signs = [entry["id"] for entry in spec["cycle"]["day_signs"]]
    labels = {entry["id"]: entry["source_label"] for entry in spec["cycle"]["day_signs"]}

    # Fixture anchor only: index 0 of the canonical cycle at an arbitrary JDN.
    # This exists to demonstrate the arithmetic path, not to date a birth.
    fixture_anchor_jdn = 2451545  # 2000-01-01, explicitly not a historical correlation
    offset = bases.julian_day_number - fixture_anchor_jdn
    coefficient = _emod(offset, 13) + 1
    sign_id = signs[_emod(offset, 20)]

    section.facts = {
        "correlation_status": "unresolved_no_approved_epoch",
        "fixture_anchor_jdn": fixture_anchor_jdn,
        "fixture_anchor_note": (
            "Non-historical test fixture. Any day-sign claim derived from it is "
            "arithmetic demonstration only."
        ),
        "fixture_cycle_position": {
            "coefficient": coefficient,
            "day_sign_id": sign_id,
            "day_sign_label": labels[sign_id],
            "canonical_cycle_index": _emod(offset, 260),
        },
        "cycle_dimensions": {
            "coefficients": 13,
            "day_signs": 20,
            "joint_period_days": spec["cycle"]["joint_period_days"],
        },
    }

    _attach_nahua_reading(section)
    return section


def _attach_nahua_reading(section: TraditionSection) -> None:
    """Quote the Book 4 corpus from hash-pinned witnesses.

    This is corpus demonstration, not personalization: because no correlation is
    approved, the reading presents what the source says about its own count -
    the conditional-fortune doctrine - and explicitly does not connect any of it
    to the reader's birth date.
    """
    if not NAHUA_AUGURY_PACK.is_file():
        return
    pack = json.loads(NAHUA_AUGURY_PACK.read_text(encoding="utf-8"))
    statements = {s["statement_id"]: s for s in pack["statements"]}

    section.disclose(
        DisclosureKind.SOURCE,
        "Reading corpus",
        "Quotations below come from Florentine Codex Book 4 via hash-pinned "
        "witness files fetched from the Getty backend, quoted in the "
        "public-domain Nahuatl with an independent English rendering graded "
        f"{pack['translation_grade']}. Folio and text-record identifiers "
        "accompany every quotation.",
    )

    heading = statements.get("nahua.book4.ch1.heading_conditional_fortune")
    forfeiture = statements.get("nahua.book4.trecena1.forfeiture")
    mitigations = [
        s for s in pack["statements"] if s["topic"] == "ritual_mitigation"
    ]

    reading: list[str] = [
        "What the corpus itself teaches, quoted as demonstration - not assigned "
        "to your birth:",
    ]
    if heading:
        reading.append(
            f"Folio {heading['witness']['folio']}, chapter heading: "
            f"“{heading['engine_rendering']}”"
        )
    if forfeiture:
        reading.append(
            f"Folio {forfeiture['witness']['folio']}, the forfeiture clause: "
            f"“{forfeiture['engine_rendering']}”"
        )
        reading.append(
            "The doctrine: a day sign grants a potential that conduct completes "
            "or destroys. It is the structural opposite of a personality trait."
        )

    if mitigations:
        reading.append(
            "**And the corpus undercuts the premise of birth-date day signs "
            "outright.** In recorded practice the operative sign was chosen, "
            "not inherited from the date:"
        )
        for statement in mitigations:
            reading.append(
                f"- Folio {statement['witness']['folio']}: "
                f"“{statement['engine_rendering'][:260].rstrip()}…”"
            )
        reading.append(
            "The day-counters deliberately deferred the bathing and naming off "
            "an unfavourable birth day onto a better one - *ic qujpatia in "
            "jtonal*, \"by this they cured his day sign\" - and on folio 55v "
            "whether the birth day was used at all depended on whether the "
            "family could afford the feast. So this section's refusal to hand "
            "you a day sign is not only a correlation gap: the source itself "
            "records that the sign a person carried was frequently not the sign "
            "of their birth."
        )

    section.reading = reading
    section.facts["augury_pack"] = {
        "pack_id": pack["pack_id"],
        "statements": len(pack["statements"]),
        "trecenas_covered": len(
            {s.get("trecena") for s in pack["statements"] if s.get("trecena")}
        ),
        "day_signs_covered": len(
            {s.get("day_sign_id") for s in pack["statements"] if s.get("day_sign_id")}
        ),
        "witness_variants_preserved": sum(
            1 for s in pack["statements"] if s.get("witness_variant")
        ),
        "ritual_mitigation_passages": len(mitigations),
        "scope": pack["scope_note"],
    }
