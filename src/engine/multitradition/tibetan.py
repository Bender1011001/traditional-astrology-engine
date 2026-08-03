"""Tibetan year-character section: element, animal, polarity, rabjung position.

The validated Phugpa pack covers month/day calendar calculation, not the
year-character cycle. The year character is derived here from the same
sexagenary cycle the validated BaZi kernel encodes - Tibetan and Chinese share
that cycle exactly, differing only in naming - which makes it checkable against
two independent anchors rather than resting on a private constant.

Mewa and parkha are deliberately NOT computed, and the reason is worth stating
precisely because an earlier version of this module stated it wrongly. It is not
that no source fixes them: the White Beryl does, it is public domain, it has been
retrieved, and its elemental-astrology chapter has been located page-exactly. The
blocker is that the available witness is a photostat reprint whose script is
legible but not yet transcribable at the confidence this repo requires, and a
plausible-looking number would be indistinguishable from a wrong one.
"""

from __future__ import annotations

from .types import BirthInput, DisclosureKind, EvidenceGrade, TraditionSection

# Tibetan animal names for the twelve branches, in branch order from Mouse.
ANIMALS = [
    "Mouse", "Ox", "Tiger", "Rabbit", "Dragon", "Snake",
    "Horse", "Sheep", "Monkey", "Bird", "Dog", "Pig",
]
# Element per stem pair: stems 0-1 Wood, 2-3 Fire, 4-5 Earth, 6-7 Iron, 8-9 Water.
ELEMENTS = ["Wood", "Fire", "Earth", "Iron", "Water"]

SEXAGENARY_ANCHOR_YEAR = 1984  # Jia-Zi year, index 0
FIRST_RABJUNG_YEAR = 1027  # Female Fire Rabbit, start of rabjung 1


def year_character(year: int) -> dict[str, str | int]:
    """Element/animal/polarity for a sexagenary year.

    Verified at two independent anchors:
      1027 -> Female Fire Rabbit (canonical first rabjung year)
      1984 -> Male Wood Mouse (Jia-Zi)
    """
    index = (year - SEXAGENARY_ANCHOR_YEAR) % 60
    stem_index = index % 10
    return {
        "element": ELEMENTS[stem_index // 2],
        "animal": ANIMALS[index % 12],
        "polarity": "male" if stem_index % 2 == 0 else "female",
        "sexagenary_index": index,
    }


def build(birth: BirthInput, bazi_year: int | None = None) -> TraditionSection:
    section = TraditionSection(
        tradition_id="tibetan",
        display_name="Tibetan year character",
        evidence_grade=EvidenceGrade.CONFIGURED,
        basis=(
            "Year character derived from the sexagenary cycle encoded in the "
            "validated BaZi kernel, with Tibetan naming; rabjung position counted "
            "from 1027 CE."
        ),
    )
    section.disclose(
        DisclosureKind.SOURCE,
        "Cycle basis",
        "Tibetan and Chinese share one sexagenary cycle. The element/animal series "
        "here is verified at two independent anchors: 1027 CE = Female Fire Rabbit "
        "(first rabjung) and 1984 CE = Male Wood Mouse (Jia-Zi).",
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Year boundary",
        "The Tibetan year begins at Losar, whose date requires the full Phugpa "
        "month calculation. The BaZi Li Chun pillar year is used as a proxy; Losar "
        "typically falls weeks later, so a birth between the two boundaries may be "
        "assigned the previous year's character.",
        ("Phugpa Losar calculation", "Civil year"),
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Mewa and parkha",
        "Not computed - but the reason has changed, and the earlier one was wrong. "
        "This section used to say their anchors were fixed by no source in the "
        "registry. That was a false blocker. The controlling primary source is "
        "identified and retrieved: Sangye Gyatso's White Beryl (bai DUr dkar po, "
        "1685), whose elemental-astrology chapter has been located page-exactly in "
        "the 1972 Lhasa-block reprint, hash-pinned, and recorded as Public Domain "
        "by the holding archive. The real blocker is legibility, not rights and not "
        "access: OCR of that photostat print is unusable, and direct visual reading "
        "reached confirmed-legible Tibetan script without reaching sentence-level "
        "transcription confidence. Parkha is additionally sex-dependent by "
        "convention, and sex is not part of the birth input contract. Popular "
        "websites do state mewa and parkha arithmetic; they cite nothing, and "
        "taking a number from one would be indistinguishable from taking a wrong "
        "one.",
    
        category="translation_pending",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Obstacle years, la, and compatibility",
        "Kag (obstacle-year) arithmetic, life-force calculations, and compatibility "
        "judgments depend on conventions the research pack has not fixed and are "
        "not asserted.",
    
        category="extraction_incomplete",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Calendar date",
        "The Phugpa pack can compute the Tibetan month and lunar day, but its own "
        "publication contract requires almanac conformance testing before dates are "
        "presented. This section therefore reports the year character only.",
    
        category="extraction_incomplete",
    )

    year = bazi_year if bazi_year is not None else birth.civil_date.year
    character = year_character(year)
    offset = year - FIRST_RABJUNG_YEAR

    section.facts = {
        "pillar_year_used": year,
        "year_character": (
            f"{character['polarity'].capitalize()} {character['element']} "
            f"{character['animal']}"
        ),
        "element": character["element"],
        "animal": character["animal"],
        "polarity": character["polarity"],
        "sexagenary_index": character["sexagenary_index"],
        "rabjung": {
            "cycle_number": offset // 60 + 1,
            "year_in_cycle": offset % 60 + 1,
        },
    }
    return section
