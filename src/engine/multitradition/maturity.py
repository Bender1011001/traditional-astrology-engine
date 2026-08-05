"""Per-module maturity, on separate axes instead of one label.

The external review's finding 2: a single status label conceals a
multidimensional reality. A module can be computationally live but historically
weak, historically strong but interpretively incomplete, or mathematically
validated but irrelevant to natal astrology. These axes answer the questions
the one label conflated:

  category                  what KIND of thing this module currently is
  source_readiness          how good the controlling texts are
  computational_readiness   how much of the tradition's own method computes
  validation_coverage       how much is checked against worked examples/vectors
  interpretation_readiness  whether a sourced judgment layer exists
  publication_readiness     what a customer may be shown

Every value is an honest assessment as of the date stamped below, maintained by
hand and asserted by tests - if a module grows or shrinks, this table must move
with it, and the panel footer is generated FROM it, so the headline can no
longer say "15 traditions" while five of them are calendars.
"""

from __future__ import annotations

from typing import Any

ASSESSED = "2026-08-05"

# Category vocabulary - the honest coverage summary is grouped by these.
NATAL_REPORT = "natal_report"
PARTIAL_JUDGMENT = "partial_judgment_engine"
CONSTRUCTION = "construction_experiment"
CALENDAR = "calendar_module"
STATE_OMEN = "state_omen_corpus"
SOLAR_RETURN = "solar_return_module"

CATEGORY_LABEL = {
    NATAL_REPORT: "developed natal report",
    PARTIAL_JUDGMENT: "partial judgment engine",
    CONSTRUCTION: "chart-construction experiment",
    CALENDAR: "calendar / cycle module",
    STATE_OMEN: "state-omen corpus demonstration",
    SOLAR_RETURN: "solar-return module",
}

MATURITY: dict[str, dict[str, Any]] = {
    "western_traditional": {
        "category": NATAL_REPORT,
        "source_readiness": "high - the live premium engine's own audited basis",
        "computational_readiness": "full",
        "validation_coverage": "full engine test suite",
        "interpretation_readiness": "full (the shipping premium report)",
        "publication_readiness": "customer-live",
    },
    "hellenistic": {
        "category": NATAL_REPORT,
        "source_readiness": "mixed - Firmicus/Ptolemy packs strong; Valens read from page images after the OCR proved to hold 0 Greek codepoints, Books I-II and part of IV mined, III and V-IX not",
        "computational_readiness": "high - sect, dignities, lots, whole-sign topics, Valens' own Lot of Foreign Travel",
        "validation_coverage": "reference tables cross-checked against pack vectors",
        "interpretation_readiness": "developed - report engine; Valens' marriage and travel chapters judged tri-valued, undecided conditions named rather than counted against the chart",
        "publication_readiness": "research only",
    },
    "latin_european": {
        "category": PARTIAL_JUDGMENT,
        "source_readiness": "moderate - Lilly's tables encoded; no Lilly rule manifest in the corpus yet",
        "computational_readiness": "high - scoring, cusps, accidental dignities",
        "validation_coverage": "GERMES cross-check on the scoring layer",
        "interpretation_readiness": "partial",
        "publication_readiness": "research only",
    },
    "islamicate_persian": {
        "category": PARTIAL_JUDGMENT,
        "source_readiness": "high - validated al-Biruni pack",
        "computational_readiness": "moderate - reference conditions over the shared core",
        "validation_coverage": "pack validator passes",
        "interpretation_readiness": "partial - conditions computed, no judgment layer",
        "publication_readiness": "research only",
    },
    "islamicate_al_qabisi": {
        "category": NATAL_REPORT,
        "source_readiness": "high - 71 rules from the Arabic TEI across chapters I-V, translation unreviewed",
        "computational_readiness": "high - profection, dignity scoring, firdaria, lots, hyleg chain (syzygy uncomputed)",
        "validation_coverage": "al-Qabisi's own worked examples reproduce; 6 of 6 agree",
        "interpretation_readiness": "developed - report engine in his own chapter order; kadkhudah years still refused",
        "publication_readiness": "research only",
    },
    "medieval_jewish": {
        "category": SOLAR_RETURN,
        "source_readiness": "moderate - annual-revolution pack validated; the natal treatise unextracted",
        "computational_readiness": "moderate - revolution structure only",
        "validation_coverage": "pack validator passes",
        "interpretation_readiness": "minimal",
        "publication_readiness": "research only",
    },
    "indian_jyotisha": {
        "category": NATAL_REPORT,
        "source_readiness": "high - four witnesses (BPHS, Saravali, Brhajjataka, Phaladipika), translations unreviewed",
        "computational_readiness": "high - grahas, bhavas, drishti, yogas, Vimshottari, nine vargas (D1-D4, D7, D9, D10, D12, D30, D60), full Sadbala and Ashtakavarga",
        "validation_coverage": "1,540 corpus vectors; the 1899 recension's own worked Sadbala figures reproduce exactly (uccha 38|04, dig 49|01, paksha 47|05, natonnata 48|44, ayana 27|15, pindotpatti 91) and all eight ashtakavarga tables sum to 337",
        "interpretation_readiness": "developed - 38 sourced delineations, synthesis layer v1, and BPHS uttara 2.44 executed: competing yogas are ranked by Sadbala instead of being listed side by side",
        "publication_readiness": "research only",
    },
    "jaimini": {
        "category": NATAL_REPORT,
        "source_readiness": "high - 116 rules from the Upadesa Sutras with the Sutrarthaprakasika, translations unreviewed",
        "computational_readiness": "high - rasi drsti, argala with both disputed forks, chara karakas, arudha padas, karaka-kundali, the three special lagnas and the Varnada",
        "validation_coverage": "the rasi drsti table reproduces Abhyankar's Ranade chart three times and his Lokur chart twice, five hits none of which is a Parasari aspect; the Patel chart discriminates the Rahu convention and the engine matches his stated Atmakaraka",
        "interpretation_readiness": "developed - report engine reading from the karaka-kundali, with the karaka scheme and the chara dasa lengths both refused because the pack refuses them",
        "publication_readiness": "research only",
    },
    "chinese_bazi": {
        "category": NATAL_REPORT,
        "source_readiness": "moderate - Yuanhai Ziping/Sanming Tonghui transcriptions traceable to the Siku recension, uncollated",
        "computational_readiness": "high - pillars, Ten Gods, relations, luck pillars, Ziping predicates",
        "validation_coverage": "one worked chart hand-verified; sexagenary kernel validated",
        "interpretation_readiness": "structural - strength/pattern/useful-god adjudication source-gated",
        "publication_readiness": "research only",
    },
    "tibetan": {
        "category": CALENDAR,
        "source_readiness": "low for the elemental layer - White Beryl located and public domain, but the photostat defeats transcription",
        "computational_readiness": "minimal - year character only, via the shared sexagenary cycle",
        "validation_coverage": "year character verified at four anchors",
        "interpretation_readiness": "none",
        "publication_readiness": "research only",
    },
    "maya": {
        "category": CALENDAR,
        "source_readiness": "high - validated kernel, both GMT correlations",
        "computational_readiness": "full for the calendar",
        "validation_coverage": "pack validator passes",
        "interpretation_readiness": "none - no natal judgment layer is attested in the encoded corpus",
        "publication_readiness": "research only",
    },
    "nahua_central_mexican": {
        "category": CALENDAR,
        "source_readiness": "high - Florentine Codex Book 4 hash-pinned, 72 statements",
        "computational_readiness": "blocked - no approved civil-date correlation",
        "validation_coverage": "cycle arithmetic validated on a fixture",
        "interpretation_readiness": "research finding - the source itself says the operative day sign could be chosen, not inherited",
        "publication_readiness": "research only; day-sign assignment refused",
    },
    "mesopotamian_babylonian": {
        "category": STATE_OMEN,
        "source_readiness": "high - Rochberg corpus encoded",
        "computational_readiness": "demonstration - tropical positions against a sidereal-era corpus, disclosed",
        "validation_coverage": "corpus validator passes; 41 of 72 protases unevaluable",
        "interpretation_readiness": "none by design - no natal genre survives",
        "publication_readiness": "research only",
    },
    "pharaonic_egyptian": {
        "category": CALENDAR,
        "source_readiness": "moderate",
        "computational_readiness": "blocked - no approved chronology profile places the birth",
        "validation_coverage": "cycle round-trip validated",
        "interpretation_readiness": "none",
        "publication_readiness": "research only",
    },
    "ziwei_doushu": {
        "category": PARTIAL_JUDGMENT,
        "source_readiness": "low - grade-D transcription, base facsimile unidentified",
        "computational_readiness": "high - palaces, month/hour stars, the five-phase bureau, and all fourteen main stars with their brightness",
        "validation_coverage": "all 10 pack vectors reproduce; calendar-regime invariance tested; the recovered Zi Wei closed form reproduces every cell of all five printed grids and all ten day-one and day-two anchors stated in words",
        "interpretation_readiness": "partial - juan 2's life-palace entry is quoted for whatever holds the life palace, where the pack rendered it; most cells are transcribed and unrendered",
        "publication_readiness": "research only",
    },
    "vietnamese": {
        "category": CALENDAR,
        "source_readiness": "moderate - modern profile, validated worked tables",
        "computational_readiness": "full for the calendar",
        "validation_coverage": "all published vectors reproduce",
        "interpretation_readiness": "none - natal interpretation explicitly refused",
        "publication_readiness": "research only",
    },
}


def maturity_of(tradition_id: str) -> dict[str, Any] | None:
    entry = MATURITY.get(tradition_id)
    if entry is None:
        return None
    return {"assessed": ASSESSED, **entry}


def coverage_summary(tradition_ids: list[str]) -> str:
    """The honest headline, generated from the table rather than asserted."""
    from collections import Counter

    counts = Counter(
        MATURITY[tid]["category"] for tid in tradition_ids if tid in MATURITY
    )
    parts = [
        f"{n} {CATEGORY_LABEL[cat]}{'s' if n != 1 else ''}"
        for cat, n in sorted(counts.items(), key=lambda kv: -kv[1])
    ]
    return " · ".join(parts)
