"""Western, Islamicate, and medieval Jewish sections over the live engine core.

These three share one calculation core - tropical positions, whole-sign or
quadrant houses, sect, dignity - and diverge in which techniques they layer on
top. The Islamicate section computes al-Biruni's reference conditions (sect,
halb, hayyiz, firdaria ordering) from the validated pack on disk; the Jewish
section remains a profile naming its methods and its source pack.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from .types import BirthInput, DisclosureKind, EvidenceGrade, TraditionSection

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
CLASSICAL = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

ISLAMICATE_ROOT = (
    Path(__file__).resolve().parents[3]
    / "docs"
    / "research"
    / "multitradition"
    / "islamicate"
)
AL_BIRUNI_SPEC = ISLAMICATE_ROOT / "al_biruni_reference_condition_spec.json"
AL_BIRUNI_RULES = ISLAMICATE_ROOT / "al_biruni_reference_condition_rule_manifest.json"
ISLAMICATE_CONCORDANCE = (
    ISLAMICATE_ROOT / "al_biruni_abu_mashar_al_qabisi_candidate_concordance.json"
)

# The concordance stores machine ids; a reading must name authors and works the
# way a specialist does, so the labels are spelled out here rather than derived.
AUTHOR_LABEL = {
    "al_biruni": "al-Biruni",
    "abu_mashar_al_balkhi": "Abu Ma'shar al-Balkhi",
    "al_qabisi": "al-Qabisi",
}
WORK_LABEL = {
    "kitab_al_tafhim": "Kitab al-Tafhim",
    "kitab_al_mudkhal_al_kabir": "Kitab al-Mudkhal al-Kabir (Great Introduction)",
    "mukhtasar_al_mudkhal": "Mukhtasar al-Mudkhal (Abbreviation)",
    "kitab_al_mudkhal_ila_sinaat_ahkam_al_nujum": (
        "Kitab al-Mudkhal ila Sina'at Ahkam al-Nujum (Introduction)"
    ),
}


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


@lru_cache(maxsize=4)
def _islamicate_pack(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def islamicate_above_horizon(longitude: float, ascendant: float) -> bool:
    """True when a zodiacal degree has already risen.

    Measured on the ecliptic against the Ascendant-Descendant axis: a degree is
    above the earth when it lies in the 180-degree arc *behind* the Ascendant in
    zodiacal order. Celestial latitude is ignored, which is the traditional
    treatment - the alternative (true altitude) is named in the disclosure.
    """
    return 0.0 < (ascendant - longitude) % 360.0 < 180.0


def islamicate_halb(
    planet_sect: str | None, nativity_sect: str, above_horizon: bool
) -> bool | None:
    """al-Biruni, Kitab al-Tafhim section 496.

    A diurnal planet is in halb above the horizon by day or below it by night;
    a nocturnal planet above by night or below by day. `None` means the planet's
    sect is not resolvable from this pack, and the pack fails closed rather than
    defaulting.
    """
    if planet_sect is None:
        return None
    return (planet_sect == nativity_sect) == bool(above_horizon)


def islamicate_hayyiz(
    halb: bool | None, planet_gender: str | None, sign_gender: str | None
) -> bool | None:
    """al-Biruni section 496: halb plus agreement of planet and sign gender.

    The implication is one-way by construction here: hayyiz can only be true
    where halb is already true, and halb alone never implies hayyiz.
    """
    if halb is None or planet_gender is None or sign_gender is None:
        return None
    return bool(halb) and planet_gender == sign_gender


def islamicate_mercury_resolution(
    sign_gender: str | None, associates: list[dict[str, Any]]
) -> dict[str, Any]:
    """Resolve Mercury's conditional gender and sect, or refuse to.

    al-Biruni makes Mercury's gender conditional on association (male when
    alone) and its sect conditional on the sign or an associated planet, and the
    inspected passage supplies no priority rule when those bases disagree. This
    therefore resolves only the unambiguous cases and reports the conflict
    otherwise.
    """
    sign_sect = None
    if sign_gender is not None:
        sign_sect = "diurnal" if sign_gender == "male" else "nocturnal"

    if not associates:
        return {
            "basis": "alone_in_sign",
            "associates": [],
            "gender": "male",
            "gender_basis": "al-Biruni: Mercury is male when alone",
            "sect": sign_sect,
            "sect_basis": (
                "al-Biruni: conditional on the sign; the sign's gender carries "
                "its day/night classification"
            ),
            "conflict": False,
        }

    names = [a["body"] for a in associates]
    genders = {a["gender"] for a in associates}
    sects = {a["sect"] for a in associates}
    gender = next(iter(genders)) if len(genders) == 1 else None
    sect = next(iter(sects)) if len(sects) == 1 else None
    conflict = gender is None or sect is None
    sect_basis = "al-Biruni: conditional on the associated planet"
    if sect is not None and sign_sect is not None and sect != sign_sect:
        # Sign and association point opposite ways and section 385-386 gives no
        # priority between them. Fail closed rather than pick one silently.
        conflict = True
        sect = None
        sect_basis = (
            "unresolved: the sign gives "
            + sign_sect
            + " and the associated planet gives the opposite; the inspected "
            "passage states no conflict priority"
        )
    return {
        "basis": "associated_in_sign",
        "associates": names,
        "gender": gender,
        "gender_basis": (
            "al-Biruni: conditional on association"
            if gender
            else "unresolved: associated planets disagree in gender"
        ),
        "sect": sect,
        "sect_basis": sect_basis,
        "conflict": conflict,
    }


def islamicate_firdaria_subperiods(
    major_ruler: str, descending_cycle: list[str]
) -> list[dict[str, Any]]:
    """Equal sevenths of a major period, al-Biruni section 395.

    The first seventh belongs to the major chronocrator alone; each later
    seventh joins it with the next planet below in the descending cycle. No
    duration is attached - section 395 supplies none.
    """
    start = descending_cycle.index(major_ruler)
    subperiods: list[dict[str, Any]] = []
    for index in range(1, 8):
        rulers = [major_ruler]
        if index > 1:
            rulers.append(descending_cycle[(start + index - 1) % len(descending_cycle)])
        subperiods.append({
            "index": index,
            "fraction_start": f"{index - 1}/7",
            "fraction_end": f"{index}/7",
            "rulers": rulers,
        })
    return subperiods


def _islamicate_lineage(candidate: dict[str, Any]) -> str:
    translator = candidate.get("translator")
    if translator:
        return f"{candidate['language']} - {translator}"
    return str(candidate["language"])


def _islamicate_variant_table(concordance: dict[str, Any]) -> list[dict[str, Any]]:
    """Firdaria year values by lineage, with both totals preserved."""
    concept = next(
        c
        for c in concordance["comparison_concepts"]
        if c["concept_id"] == "firdaria_year_values"
    )
    rows: list[dict[str, Any]] = []
    for candidate in concept["candidates"]:
        listed = candidate["listed_values"]
        computed = sum(listed.values())
        stated = candidate.get("stated_total")
        rows.append({
            "author": AUTHOR_LABEL.get(candidate["author_id"], candidate["author_id"]),
            "work": WORK_LABEL.get(candidate["work_id"], candidate["work_id"]),
            "lineage": _islamicate_lineage(candidate),
            "passage": candidate["passage"],
            "mars_years": listed.get("mars"),
            "moon_years": listed.get("moon"),
            "recomputed_total": computed,
            "stated_total": stated,
            # None, not True, where the witness states no total at all: an
            # absent total is not an agreeing one.
            "totals_agree": None if stated is None else stated == computed,
            "listed_values": listed,
            "status": candidate["status"],
        })
    return rows


def build_islamicate(birth: BirthInput, western: TraditionSection) -> TraditionSection:
    """Compute al-Biruni's reference conditions over the shared Western core.

    Everything doctrinal here is loaded from the validated al-Biruni pack on
    disk and attributed to al-Biruni by section. Abu Ma'shar and al-Qabisi
    appear only as *variants* from the hash-pinned Wurzburg TEI witnesses -
    never as substitutes for al-Biruni, and never merged with him.
    """
    spec = _islamicate_pack(AL_BIRUNI_SPEC)
    manifest = _islamicate_pack(AL_BIRUNI_RULES)
    concordance = _islamicate_pack(ISLAMICATE_CONCORDANCE)
    classifications = spec["classifications"]
    firdaria_spec = spec["firdaria"]
    condition_logic = spec["condition_logic"]

    placements = western.facts.get("placements")
    if not placements:
        raise ValueError("Islamicate section needs Western placements to compute on")

    section = TraditionSection(
        tradition_id="islamicate_persian",
        display_name="Islamicate / Persian",
        evidence_grade=EvidenceGrade.VALIDATED_PACK,
        basis=(
            "Shares the Western calculation core. Distinctive layer computed "
            "here: al-Biruni's sect, halb, hayyiz and firdaria structure from "
            "the validated Kitab al-Tafhim reference-condition pack, with the "
            "Abu Ma'shar / al-Qabisi variant concordance shown alongside."
        ),
    )

    # --- sect -------------------------------------------------------------
    nativity_sect = "diurnal" if western.facts.get("sect") == "day" else "nocturnal"
    asc = western.facts["ascendant"]
    asc_longitude = SIGNS.index(asc["sign"]) * 30 + asc["degree_in_sign"]

    male_signs = set(classifications["male_signs"])
    male_planets = set(classifications["male_planets"])
    female_planets = set(classifications["female_planets"])
    diurnal_planets = set(classifications["diurnal_planets"])
    nocturnal_planets = set(classifications["nocturnal_planets"])

    # --- classification and horizon position per planet -------------------
    resolved: dict[str, dict[str, Any]] = {}
    for placement in placements:
        key = placement["body"].lower()
        sign = placement["sign"]
        longitude = SIGNS.index(sign) * 30 + placement["degree_in_sign"]
        gender = None
        if key in male_planets:
            gender = "male"
        elif key in female_planets:
            gender = "female"
        sect_of_planet = None
        if key in diurnal_planets:
            sect_of_planet = "diurnal"
        elif key in nocturnal_planets:
            sect_of_planet = "nocturnal"
        resolved[key] = {
            "body": placement["body"],
            "sign": sign,
            "sign_gender": "male" if sign.lower() in male_signs else "female",
            "longitude": round(longitude, 4),
            "above_horizon": islamicate_above_horizon(longitude, asc_longitude),
            "planet_gender": gender,
            "planet_sect": sect_of_planet,
        }

    # --- Mercury's conditional classification -----------------------------
    mercury = resolved.get("mercury")
    mercury_resolution: dict[str, Any] = {}
    if mercury is not None:
        associates = [
            {"body": entry["body"], "gender": entry["planet_gender"],
             "sect": entry["planet_sect"]}
            for key, entry in resolved.items()
            if key != "mercury" and entry["sign"] == mercury["sign"]
        ]
        mercury_resolution = islamicate_mercury_resolution(
            mercury["sign_gender"], associates
        )
        mercury["planet_gender"] = mercury_resolution["gender"]
        mercury["planet_sect"] = mercury_resolution["sect"]
        mercury_resolution["sign"] = mercury["sign"]
        mercury_resolution["al_qabisi_difference"] = (
            "The inspected al-Qabisi chapter II, Arabic and John of Seville's "
            "Latin, describes Mercury as male and diurnal outright. al-Biruni "
            "is the controlling author here, so al-Qabisi's classification is "
            "recorded as a cross-author difference and not substituted."
        )

    # --- halb and hayyiz --------------------------------------------------
    conditions: list[dict[str, Any]] = []
    for name in CLASSICAL:
        entry = resolved.get(name.lower())
        if entry is None:
            continue
        halb = islamicate_halb(
            entry["planet_sect"], nativity_sect, entry["above_horizon"]
        )
        hayyiz = islamicate_hayyiz(
            halb, entry["planet_gender"], entry["sign_gender"]
        )
        conditions.append({
            "body": entry["body"],
            "sign": entry["sign"],
            "sign_gender": entry["sign_gender"],
            "above_horizon": entry["above_horizon"],
            "planet_sect": entry["planet_sect"],
            "planet_gender": entry["planet_gender"],
            "halb": halb,
            "hayyiz": hayyiz,
            "resolution": (
                "resolved" if halb is not None else "unresolved_conditional"
            ),
        })

    in_halb = [c["body"] for c in conditions if c["halb"] is True]
    in_hayyiz = [c["body"] for c in conditions if c["hayyiz"] is True]
    halb_only = [c["body"] for c in conditions if c["halb"] and not c["hayyiz"]]
    implication_holds = all(
        c["halb"] is True for c in conditions if c["hayyiz"] is True
    )

    mars = next((c for c in conditions if c["body"] == "Mars"), None)
    mars_case: dict[str, Any] = {}
    if mars is not None:
        mars_case = {
            "rule_id": "islamicate.al_biruni.condition.mars_hayyiz",
            "pack_note": condition_logic["mars_note"],
            "planet_gender": "male",
            "planet_sect": "nocturnal",
            "required_horizon": "above the horizon by night, or below it by day",
            "required_sign_gender": "male",
            "sign": mars["sign"],
            "sign_gender": mars["sign_gender"],
            "horizon_requirement_met": mars["halb"] is True,
            "sign_requirement_met": mars["sign_gender"] == "male",
            "halb": mars["halb"],
            "hayyiz": mars["hayyiz"],
        }

    # --- firdaria: order and structure only -------------------------------
    order_key = (
        "diurnal_major_order" if nativity_sect == "diurnal" else "nocturnal_major_order"
    )
    major_order = list(firdaria_spec[order_key])
    descending = list(firdaria_spec["descending_cycle"])
    firdaria = {
        "nativity_sect": nativity_sect,
        "rule_id": f"islamicate.al_biruni.firdaria.major_order.{nativity_sect}",
        "source_section": "395, Firdaria of planets (printed p. 239)",
        "major_order": major_order,
        "descending_cycle": descending,
        "subperiods_per_major_period": firdaria_spec["subperiods_per_major_period"],
        "subperiod_rule": firdaria_spec["subperiod_rule"],
        "first_major_period": {
            "major_ruler": major_order[0],
            "subperiods": islamicate_firdaria_subperiods(major_order[0], descending),
        },
        "subperiod_series": [
            {
                "sequence": index + 1,
                "major_ruler": ruler,
                "sevenths": [
                    "+".join(part["rulers"])
                    for part in islamicate_firdaria_subperiods(ruler, descending)
                ],
            }
            for index, ruler in enumerate(major_order)
        ],
        "durations_emitted": False,
        "node_periods_emitted": False,
        "duration_refusal_rule_id": "islamicate.al_biruni.firdaria.duration.unresolved",
        "duration_refusal": (
            "al-Biruni, Kitab al-Tafhim section 395 states neither node periods "
            "nor a table of major-period durations. This section therefore "
            "emits the ordering and the equal-seventh structure and refuses "
            "every age, year count, and calendar date derived from them."
        ),
    }

    # --- variant concordance ---------------------------------------------
    variant_rows = _islamicate_variant_table(concordance)
    candidate_count = sum(
        len(concept["candidates"]) for concept in concordance["comparison_concepts"]
    )
    variant_concordance = {
        "corpus": concordance["discovery_method"]["corpus"],
        "retrieved": concordance["discovery_method"]["retrieved"],
        "witness_lineages": [
            "Arabic (al-Biruni, Abu Ma'shar, al-Qabisi)",
            "Latin - Hermann of Carinthia",
            "Latin - John of Seville",
            "Latin - Adelard of Bath",
        ],
        "candidate_passages": candidate_count,
        "preserved_variants": len(concordance["variant_observations"]),
        "firdaria_year_values_by_lineage": variant_rows,
        "observations": [
            {
                "observation_id": item["observation_id"],
                "type": item["type"],
                "evidence": item["evidence"],
                "resolution": item["resolution"],
                "engine_action": item["engine_action"],
            }
            for item in concordance["variant_observations"]
        ],
        "hard_invariants": concordance["hard_invariants"],
    }

    _islamicate_disclose(section, spec, manifest, concordance)

    section.facts = {
        "shared_calculation_core": "western_traditional",
        "source_pack": {
            "pack_id": spec["source_pack_id"],
            "author": AUTHOR_LABEL["al_biruni"],
            "work": WORK_LABEL["kitab_al_tafhim"],
            "edition_id": spec["edition_id"],
            "rules_loaded": len(manifest["rules"]),
            "implementation_status": manifest["implementation_status"],
            "publication_status": manifest["publication_status"],
        },
        "sect": {
            "nativity_sect": nativity_sect,
            "western_sect_label": western.facts.get("sect"),
            "sun_altitude_degrees": western.facts.get("sun_altitude_degrees"),
            "ascendant_longitude": round(asc_longitude, 4),
            "horizon_test": "zodiacal arc against the Ascendant-Descendant axis",
            "sun_arc_test_agrees_with_altitude": (
                resolved["sun"]["above_horizon"]
                if "sun" in resolved
                else None
            ) == (nativity_sect == "diurnal"),
        },
        "classifications": {
            "male_signs": classifications["male_signs"],
            "female_signs": classifications["female_signs"],
            "male_planets": classifications["male_planets"],
            "female_planets": classifications["female_planets"],
            "diurnal_planets": classifications["diurnal_planets"],
            "nocturnal_planets": classifications["nocturnal_planets"],
            "mercury_gender": classifications["mercury_gender"],
            "mercury_sect": classifications["mercury_sect"],
        },
        "planetary_conditions": conditions,
        "condition_summary": {
            "halb_definition": condition_logic["halb"],
            "hayyiz_definition": condition_logic["hayyiz"],
            "implication": condition_logic["implication"],
            "in_halb": in_halb,
            "in_hayyiz": in_hayyiz,
            "halb_without_hayyiz": halb_only,
            "one_way_implication_holds": implication_holds,
            "joy_boundary": condition_logic["joy_boundary"],
        },
        "mercury_resolution": mercury_resolution,
        "mars_case": mars_case,
        "firdaria": firdaria,
        "variant_concordance": variant_concordance,
        "distinctive_layers_computed": [
            "sect and its planetary consequences",
            "halb and hayyiz for the seven classical planets",
            "planetary and sign gender/sect classification",
            "Mercury's conditional classification",
            "firdaria ordering, diurnal and nocturnal",
            "equal-seventh subperiod structure",
        ],
        "distinctive_layers_gated": [
            "firdaria period durations and dates",
            "Abu Ma'shar Great Introduction doctrine",
            "al-Qabisi Introduction doctrine",
            "lunar mansions",
            "tasyir / directions",
        ],
    }

    section.reading = _islamicate_reading(
        nativity_sect=nativity_sect,
        conditions=conditions,
        in_halb=in_halb,
        in_hayyiz=in_hayyiz,
        halb_only=halb_only,
        mars_case=mars_case,
        mercury_resolution=mercury_resolution,
        firdaria=firdaria,
        variant_rows=variant_rows,
    )
    return section


def _islamicate_disclose(
    section: TraditionSection,
    spec: dict[str, Any],
    manifest: dict[str, Any],
    concordance: dict[str, Any],
) -> None:
    section.disclose(
        DisclosureKind.SOURCE,
        "Pack provenance",
        "Sect and gender classifications, halb/hayyiz and their one-way "
        "implication, the firdaria ordering and the equal-seventh subperiod "
        "structure are computed from the validated al-Biruni reference-condition "
        f"pack ({len(manifest['rules'])} rules, edition "
        f"{spec['edition_id']}), built from facing-page Arabic/English evidence "
        "in the Halle institutional scan. Every claim below is al-Biruni's "
        "unless another author is named.",
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Horizon test",
        "Above/below the horizon is taken from the planet's zodiacal degree "
        "against the Ascendant-Descendant axis, ignoring celestial latitude - "
        "the traditional treatment. The Sun's result is cross-checked against "
        "the ephemeris altitude that set the sect.",
        ("true altitude from the ephemeris", "quadrant house cusps"),
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Mercury association test",
        "al-Biruni conditions Mercury on association without defining it in the "
        "inspected passage. Co-presence in the same sign is used here; where the "
        "sign and an associated planet point opposite ways, the pack states no "
        "priority and this section leaves Mercury unresolved.",
        ("bodily conjunction within orb", "any aspect", "sign ruler only"),
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Firdaria periods and ages",
        "The al-Biruni pack refuses node periods and age/date firdaria "
        "arithmetic because section 395 supplies neither node periods nor a "
        "major-duration table. The ordering and the equal sevenths below are "
        "therefore a sequence without a clock: no years, no ages, no dates.",
    
        category="extraction_incomplete",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Judgment from halb or hayyiz",
        "Section 498 lists halb or hayyiz among several conditions of a "
        "planet's joy. This section does not infer a complete judgment from "
        "them, cancel a debility, or change a planet's benefic or malefic "
        "nature - the pack forbids all three.",
    
        category="extraction_incomplete",
    )
    section.disclose(
        DisclosureKind.SOURCE,
        "Variant concordance",
        "Seven Wurzburg TEI witnesses are hash-pinned in this repository, "
        f"covering separate Arabic, Hermann of Carinthia, John of Seville and "
        f"Adelard of Bath lineages; "
        f"{sum(len(c['candidates']) for c in concordance['comparison_concepts'])} "
        f"candidate passages and "
        f"{len(concordance['variant_observations'])} preserved variants are "
        "catalogued. The Arabic originals are ninth- to eleventh-century and "
        "public domain, so the disagreements are shown rather than deferred.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Abu Ma'shar and al-Qabisi doctrine",
        "The variants below are published as evidence, not promoted to rules: "
        "no Latin lineage overrides the Arabic or another Latin lineage, the "
        "Great Introduction and the Abbreviation stay different works, and "
        "al-Biruni is never backfilled from either author. Rule promotion "
        "waits on the critical apparatus and Arabic specialist review.",
    
        category="school_fork_unresolved",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Prediction",
        "The pack marks itself interpretation-ineligible and historical-use "
        "only. The reading below reports classification, structure and "
        "attribution; it derives no life prediction, no timing, and no advice.",
    
        category="policy_suppressed",
    )


def _islamicate_join(names: list[str]) -> str:
    if not names:
        return "none"
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


def _islamicate_verb(names: list[str], singular: str, plural: str) -> str:
    return singular if len(names) == 1 else plural


def _islamicate_reading(
    *,
    nativity_sect: str,
    conditions: list[dict[str, Any]],
    in_halb: list[str],
    in_hayyiz: list[str],
    halb_only: list[str],
    mars_case: dict[str, Any],
    mercury_resolution: dict[str, Any],
    firdaria: dict[str, Any],
    variant_rows: list[dict[str, Any]],
) -> list[str]:
    """Judge in al-Biruni's order: sect, condition, structure, then variants."""
    sun = next((c for c in conditions if c["body"] == "Sun"), None)
    sun_position = "above" if sun and sun["above_horizon"] else "below"
    reading = [
        "Sect first, because every condition rule in this section is "
        f"conditioned on it. The Sun stands {sun_position} the horizon at "
        f"birth, so this is a {nativity_sect} nativity. al-Biruni (Kitab "
        "al-Tafhim, sections 386 and 396-401, Wright 1934 facing edition) puts "
        "Saturn, Jupiter and the Sun in the diurnal sect and Mars, Venus and "
        "the Moon in the nocturnal sect, and leaves Mercury conditional.",
        "Planetary condition, al-Biruni section 496: a planet is in halb when "
        "a diurnal planet stands above the horizon by day or below it by "
        "night, or a nocturnal planet above by night or below by day. It is in "
        "hayyiz when it is in halb and additionally occupies a sign of its own "
        "gender. The implication runs one way only - every hayyiz is a halb, "
        "and a halb is not thereby a hayyiz.",
        f"In this chart {_islamicate_join(in_halb)} "
        f"{_islamicate_verb(in_halb, 'holds', 'hold')} halb, and "
        f"{_islamicate_join(in_hayyiz)} "
        f"{_islamicate_verb(in_hayyiz, 'holds', 'hold')} hayyiz. "
        + (
            f"{_islamicate_join(halb_only)} "
            f"{_islamicate_verb(halb_only, 'holds', 'hold')} halb without "
            "hayyiz, which is al-Biruni's one-way implication showing up in "
            "the chart itself."
            if halb_only
            else "No planet here holds halb without hayyiz."
        ),
    ]

    if mars_case:
        horizon_verdict = (
            "meets" if mars_case["horizon_requirement_met"] else "fails"
        )
        sign_verdict = "meets" if mars_case["sign_requirement_met"] else "fails"
        reading.append(
            "Mars is the case al-Biruni singles out in section 496: male in "
            "gender but nocturnal in sect, so it needs the nocturnal horizon "
            "condition - above by night or below by day - and a male sign. "
            f"Here Mars is in {mars_case['sign']}, a "
            f"{mars_case['sign_gender']} sign, and it {horizon_verdict} the "
            f"horizon condition and {sign_verdict} the sign condition: halb "
            f"{mars_case['halb']}, hayyiz {mars_case['hayyiz']}."
        )

    if mercury_resolution:
        gender = mercury_resolution.get("gender")
        sect = mercury_resolution.get("sect")
        basis = (
            "alone in its sign"
            if mercury_resolution.get("basis") == "alone_in_sign"
            else "sharing its sign with "
            + _islamicate_join(mercury_resolution.get("associates", []))
        )
        if gender and sect:
            verdict = f"reads it as {gender} and {sect}"
        elif gender:
            verdict = (
                f"reads its gender as {gender} but leaves its sect unresolved, "
                "so no halb or hayyiz is computed for it"
            )
        elif sect:
            verdict = (
                f"reads its sect as {sect} but leaves its gender unresolved, "
                "so no hayyiz is computed for it"
            )
        else:
            verdict = (
                "leaves both its gender and its sect unresolved, so no halb or "
                "hayyiz is computed for it"
            )
        reading.append(
            "Mercury is conditional in al-Biruni, not fixed: sections 385-386 "
            "make its gender depend on association and its sect on the sign or "
            f"an associated planet, and give no priority when those bases "
            f"disagree. It is {basis} here, so this section {verdict}, rather "
            "than defaulting. al-Qabisi, by contrast, describes Mercury as "
            "male and diurnal outright in the inspected chapter II, in both "
            "the Arabic and John of Seville's Latin. al-Biruni is the "
            "controlling author for this section, so al-Qabisi's "
            "classification is recorded as a cross-author difference and is "
            "not substituted."
        )

    reading.append(
        "Section 498 lists halb and hayyiz among several conditions of a "
        "planet's joy. al-Biruni does not there cancel a debility or change a "
        "planet's benefic or malefic nature, and neither does this section: "
        "the flags above are one condition, not a verdict."
    )

    first = firdaria["first_major_period"]
    sevenths = [
        "+".join(ruler.capitalize() for ruler in part["rulers"])
        for part in first["subperiods"]
    ]
    reading.append(
        "Firdaria, as structure only. al-Biruni, section 395, calls the "
        f"firdaria a Persian idea and gives the {nativity_sect} order as "
        + ", ".join(major.capitalize() for major in firdaria["major_order"])
        + ". Each major period divides into seven equal parts: the first "
        "belongs to the major chronocrator alone and each later seventh joins "
        "it with the next planet below in the descending cycle Saturn, "
        "Jupiter, Mars, Sun, Venus, Mercury, Moon - so the opening "
        f"{first['major_ruler'].capitalize()} period runs "
        + ", ".join(sevenths)
        + "."
    )
    reading.append(
        "No firdaria ages or dates follow from that. The inspected section 395 "
        "supplies neither node periods nor a table of major-period durations, "
        "so what al-Biruni gives here is an ordering without a clock. Duration "
        "tables do exist in Abu Ma'shar and al-Qabisi - and they disagree with "
        "each other and with themselves, which is what the rest of this "
        "section records."
    )

    by_key = {(row["author"], row["lineage"], row["work"]): row for row in variant_rows}
    arabic_mars = next(
        (
            row["mars_years"]
            for row in variant_rows
            if row["lineage"] == "Arabic" and "Great Introduction" in row["work"]
        ),
        None,
    )
    hermann_mars = next(
        (
            row["mars_years"]
            for row in variant_rows
            if "Hermann of Carinthia" in row["lineage"]
        ),
        None,
    )
    reading.append(
        "Variant, Mars firdaria years - Abu Ma'shar al-Balkhi, Great "
        f"Introduction. The Arabic witness (VII.8, p. 800) gives Mars "
        f"{arabic_mars} years; Hermann of Carinthia's Latin (chapter 8, p. "
        f"143) gives {hermann_mars}. Neither lineage overrides the other, so "
        "both are recorded and neither is selected "
        "[firdaria_great_introduction_mars_variant]."
    )

    john = next(
        (
            row
            for row in variant_rows
            if "John of Seville" in row["lineage"]
            and "Great Introduction" in row["work"]
        ),
        None,
    )
    if john:
        reading.append(
            "Variant, internal arithmetic - John of Seville's Latin of the same "
            f"Great Introduction (differentia VIII, p. 310) lists values that "
            f"sum to {john['recomputed_total']}, including a bracketed Moon of "
            f"{john['moon_years']}, while stating a total of "
            f"{john['stated_total']}, and it orders Jupiter and Mars ahead of "
            "the Moon and Saturn. The conflict is preserved as evidence and "
            "never silently corrected "
            "[firdaria_great_introduction_john_internal_total]."
        )

    adelard = next(
        (row for row in variant_rows if "Adelard of Bath" in row["lineage"]), None
    )
    abbreviation_arabic = by_key.get(
        (
            AUTHOR_LABEL["abu_mashar_al_balkhi"],
            "Arabic",
            WORK_LABEL["mukhtasar_al_mudkhal"],
        )
    )
    if adelard and abbreviation_arabic:
        reading.append(
            "Variant, internal arithmetic - Adelard of Bath's Latin of Abu "
            "Ma'shar's Abbreviation, a separate work from the Great "
            f"Introduction (chapter 7, p. 136), lists values summing to "
            f"{adelard['recomputed_total']} but states "
            f"{adelard['stated_total']}; the Arabic of the same work (chapter "
            f"7, p. 80) lists {abbreviation_arabic['recomputed_total']} and "
            f"states {abbreviation_arabic['stated_total']}. Both the recorded "
            "and the recomputed totals are kept "
            "[firdaria_abbreviation_latin_total]."
        )

    reading.append(
        "Variant, terminology - al-Qabisi's Arabic (chapter I, p. 60) carries "
        "distinct halb and hayyiz tokens inside one definition, while John of "
        "Seville's Latin of that chapter (chapter 1, p. 266) collapses the two "
        "stages into alhaiz and aiz; Adelard of Bath, translating the "
        "Abbreviation (chapter 3, p. 110), drops the transliteration entirely "
        "and writes competentia. This section does not normalise those terms "
        "onto one another [halb_hayyiz_qabisi_latin_terminology, "
        "hayyiz_abbreviation_competentia]."
    )
    reading.append(
        "Variant, lexical - a halb-form token in the Great Introduction Arabic "
        "(p. 786) and the Abbreviation Arabic (p. 52) is glossed through "
        "dignities and joys rather than the horizon, unlike al-Qabisi p. 60 "
        "and the al-Biruni baseline. Surface forms are not equated across "
        "passages [halb_lexeme_semantic_anomaly]."
    )
    reading.append(
        "Finally, a scope difference rather than a contradiction: al-Biruni's "
        "section 395 simply omits the duration and node tables that al-Qabisi "
        "(chapters II and IV) and Abu Ma'shar (the year-value passages) do "
        "carry. al-Biruni is not backfilled from them "
        "[firdaria_scope_not_contradiction]."
    )
    return reading


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
    
        category="source_unread",
    )

    # Spec item 7. Ibn Ezra writes in Hebrew and coins Hebrew equivalents for
    # Arabic technical vocabulary; the parallel critical edition prints both, and
    # collapsing to English alone hides the layer a historian of medieval Hebrew
    # science would check first.
    section.disclose(
        DisclosureKind.SOURCE,
        "Hebrew terminology",
        "Technical terms are given in Hebrew with transliteration alongside the "
        "English, as the parallel Hebrew-English critical edition prints them. "
        "Several are Ibn Ezra's own Hebrew calques for Arabic terms.",
    )
    section.facts = {
        "shared_calculation_core": "western_traditional",
        "hebrew_terminology": [
            {
                "hebrew": "תקופת השנה",
                "transliteration": "tequfat ha-shanah",
                "english": "annual revolution (solar return)",
                "note": "The figure cast for the Sun's return to its natal degree.",
            },
            {
                "hebrew": "מזל צומח",
                "transliteration": "mazzal tzomeach",
                "english": "ascendant (literally: rising sign)",
            },
            {
                "hebrew": "בעל הבית",
                "transliteration": "ba'al ha-bayit",
                "english": "lord of the house (domicile ruler)",
                "note": "Hebrew calque for the Arabic rabb al-bayt.",
            },
            {
                "hebrew": "משרת",
                "transliteration": "mesharet",
                "english": "planet (literally: servant)",
            },
            {
                "hebrew": "גבול",
                "transliteration": "gevul",
                "english": "bound / term",
            },
            {
                "hebrew": "מולד",
                "transliteration": "molad",
                "english": "conjunction, birth of the lunation",
                "note": "Also the technical term of the Hebrew calendar itself.",
            },
        ],
        "distinctive_layers_available": [
            "Ibn Ezra annual revolution comparison (validated)",
            "sect-light triplicity ruler phases (validated)",
            "Hebrew technical vocabulary alongside translation",
        ],
        "distinctive_layers_gated": ["Book of Nativities natal doctrine"],
    }
    return section
