"""Tests for the multi-tradition panel.

These lock the properties that make the panel defendable: every section carries
disclosures, refusals are actually enforced, the known-good Fairfield values are
reproduced, and a broken section cannot take down the panel.
"""

from __future__ import annotations

import json
from datetime import date

import pytest

from src.engine.multitradition import BirthInput, build_panel, render
from src.engine.multitradition.tibetan import year_character
from src.engine.multitradition.types import DisclosureKind

FAIRFIELD = BirthInput(
    name="Andrew",
    civil_date=date(1996, 8, 13),
    civil_time="07:18",
    utc_offset_hours=-7.0,
    latitude=38.2494,
    longitude=-122.0397,
    place_label="Fairfield, California, United States",
)
SYDNEY = BirthInput(
    name="Fixture: Sydney",
    civil_date=date(1978, 11, 3),
    civil_time="22:40",
    utc_offset_hours=11.0,
    latitude=-33.8688,
    longitude=151.2093,
    place_label="Sydney, New South Wales, Australia",
)
PARIS_1931 = BirthInput(
    name="Fixture: Paris 1931",
    civil_date=date(1931, 2, 3),
    civil_time="04:05",
    utc_offset_hours=0.0,
    latitude=48.8566,
    longitude=2.3522,
    place_label="Paris, France",
)
QUITO_LATE_ZI = BirthInput(
    name="Fixture: Quito late-Zi",
    civil_date=date(2004, 6, 21),
    civil_time="23:20",
    utc_offset_hours=-5.0,
    latitude=-0.1807,
    longitude=-78.4678,
    place_label="Quito, Ecuador",
)

ALL_FIXTURES = [FAIRFIELD, SYDNEY, PARIS_1931, QUITO_LATE_ZI]


@pytest.fixture(scope="module")
def fairfield_panel() -> dict:
    return build_panel(FAIRFIELD)


def _section(panel: dict, tradition_id: str) -> dict:
    return next(s for s in panel["sections"] if s["tradition_id"] == tradition_id)


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_every_fixture_builds_every_section(birth: BirthInput) -> None:
    panel = build_panel(birth)
    failures = {s["tradition_id"]: s["error"] for s in panel["sections"] if s.get("error")}
    assert not failures, f"sections failed: {failures}"
    # Sections are added by separate tradition packs; the count only grows.
    # Presence of each expected tradition is asserted individually below.
    assert len(panel["sections"]) >= 8


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_every_section_discloses_something(birth: BirthInput) -> None:
    """A section with no disclosures is a section hiding its conventions."""
    panel = build_panel(birth)
    for section in panel["sections"]:
        assert section["disclosures"], f"{section['tradition_id']} discloses nothing"


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_panel_is_not_customer_eligible(birth: BirthInput) -> None:
    panel = build_panel(birth)
    assert panel["customer_eligible"] is False
    assert panel["historical_use_only"] is True


def test_western_matches_known_values(fairfield_panel: dict) -> None:
    facts = _section(fairfield_panel, "western_traditional")["facts"]
    assert facts["ascendant"]["sign"] == "Virgo"
    assert facts["ascendant"]["degree_in_sign"] == pytest.approx(1.5017, abs=0.01)
    assert facts["sect"] == "day"
    sun = next(p for p in facts["placements"] if p["body"] == "Sun")
    assert sun["sign"] == "Leo"
    assert sun["whole_sign_house"] == 12


def test_vedic_matches_known_values(fairfield_panel: dict) -> None:
    facts = _section(fairfield_panel, "indian_jyotisha")["facts"]
    assert facts["ayanamsa_degrees"] == pytest.approx(23.8098, abs=0.001)
    assert facts["lagna"]["rasi"] == "Leo"
    assert facts["lagna"]["nakshatra"] == "Magha"
    assert facts["janma_nakshatra"]["name"] == "Ashlesha"
    assert facts["janma_nakshatra"]["lord"] == "Mercury"
    # Vimshottari starts in the balance of the janma-nakshatra lord's period.
    assert facts["vimshottari_mahadashas"][0]["lord"] == "Mercury"
    assert facts["vimshottari_mahadashas"][0]["partial_at_birth"] is True
    jupiter = next(g for g in facts["grahas"] if g["graha"] == "Jupiter")
    assert jupiter["rasi"] == "Sagittarius"
    assert jupiter["dignity"] == "own sign"


def test_navamsha_structural_properties() -> None:
    """D9 must satisfy four properties the classical rule guarantees."""
    from collections import Counter

    from src.engine.multitradition.vedic import (
        NAVAMSHA_ARC,
        SIGNS,
        navamsha_sign,
    )

    # 1. The 108 divisions map onto the 12 signs exactly nine times each.
    counts = Counter(
        navamsha_sign((i + 0.5) * NAVAMSHA_ARC)[0] for i in range(108)
    )
    assert set(counts) == set(SIGNS)
    assert set(counts.values()) == {9}

    # 2. Movable signs begin their navamsha from themselves.
    for sign in ("Aries", "Cancer", "Libra", "Capricorn"):
        assert navamsha_sign(SIGNS.index(sign) * 30 + 0.01)[0] == sign

    # 3. Fixed signs begin from the ninth sign; dual signs from the fifth.
    assert navamsha_sign(30.01)[0] == "Capricorn"  # Taurus -> 9th
    assert navamsha_sign(60.01)[0] == "Libra"  # Gemini -> 5th

    # 4. The cycle closes: the final navamsha of Pisces is Pisces.
    assert navamsha_sign(359.99)[0] == "Pisces"


def test_navamsha_present_for_every_graha(fairfield_panel: dict) -> None:
    facts = _section(fairfield_panel, "indian_jyotisha")["facts"]
    assert "navamsha" in facts["lagna"]
    for graha in facts["grahas"]:
        assert graha["navamsha"] in _sign_names()
        assert 1 <= graha["navamsha_division"] <= 9
        assert isinstance(graha["vargottama"], bool)


def _sign_names() -> list[str]:
    from src.engine.multitradition.vedic import SIGNS

    return SIGNS


def test_bazi_matches_known_pillars(fairfield_panel: dict) -> None:
    facts = _section(fairfield_panel, "chinese_bazi")["facts"]
    assert facts["pillar_year_used"] == 1996
    pillars = facts["pillars"]
    assert pillars["year"]["stem"] == "bing" and pillars["year"]["branch"] == "zi"
    assert pillars["month"]["stem"] == "bing" and pillars["month"]["branch"] == "shen"
    assert pillars["day"]["stem"] == "ren" and pillars["day"]["branch"] == "wu_branch"
    assert facts["day_master"]["element"] == "Water"
    assert facts["day_master"]["polarity"] == "yang"
    assert facts["element_tally"]["Earth"] == 0


def test_bazi_day_anchor_cross_checks() -> None:
    """The day-count anchor must reproduce a second, independent known day."""
    from src.engine.multitradition.bazi import (
        DAY_ANCHOR_INDEX,
        DAY_ANCHOR_JDN,
        _pair,
    )

    # 2000-01-01 is JDN 2451545 and a Wu-Wu day (sexagenary index 54).
    index = (DAY_ANCHOR_INDEX + (2451545 - DAY_ANCHOR_JDN)) % 60
    assert index == 54
    assert _pair(index) == ("wu_stem", "wu_branch")


def test_bazi_emits_all_three_hour_time_bases(fairfield_panel: dict) -> None:
    candidates = _section(fairfield_panel, "chinese_bazi")["facts"][
        "hour_pillar_candidates"
    ]
    assert set(candidates) == {"true_solar_time", "clock_time", "local_mean_time"}
    # Fairfield sits far west of its zone meridian, so the fork is real here.
    assert candidates["true_solar_time"]["branch"] != candidates["clock_time"]["branch"]


def test_bazi_hour_fork_is_disclosed_when_it_changes_the_pillar(
    fairfield_panel: dict,
) -> None:
    section = _section(fairfield_panel, "chinese_bazi")
    forks = [d for d in section["disclosures"] if d["kind"] == DisclosureKind.FORK.value]
    assert any("Hour pillar" in d["subject"] for d in forks)


def test_maya_emits_both_correlations(fairfield_panel: dict) -> None:
    facts = _section(fairfield_panel, "maya")["facts"]
    profiles = facts["correlation_profiles"]
    assert set(profiles) == {"gmt_584283", "gmt_584285"}
    assert profiles["gmt_584283"]["long_count"] == "12.19.3.7.6"
    assert profiles["gmt_584283"]["tzolkin"] == "10 Kimi"
    # The two correlations differ by exactly two days.
    assert (
        profiles["gmt_584283"]["total_day"] - profiles["gmt_584285"]["total_day"] == 2
    )


def test_nahua_refuses_a_correlation(fairfield_panel: dict) -> None:
    section = _section(fairfield_panel, "nahua_central_mexican")
    assert section["facts"]["correlation_status"] == "unresolved_no_approved_epoch"
    refusals = [
        d for d in section["disclosures"] if d["kind"] == DisclosureKind.REFUSAL.value
    ]
    assert any("correlation" in d["subject"].lower() for d in refusals)
    # The fixture position must never be presented as a real day sign.
    assert "fixture" in section["facts"]["fixture_anchor_note"].lower()


def test_nahua_reading_quotes_corpus_without_personalizing(
    fairfield_panel: dict,
) -> None:
    """The reading must quote the corpus AND keep the day-sign refusal."""
    section = _section(fairfield_panel, "nahua_central_mexican")
    assert section.get("reading"), "Nahua reading section missing"
    joined = " ".join(section["reading"])
    # Quotes the corpus...
    assert "Cipactli" in joined
    assert "forfeiture" in joined.lower() or "destroy" in joined.lower()
    # ...without assigning it to the reader.
    assert "not assigned to your birth" in joined
    # The correlation refusal must survive alongside the reading.
    assert section["facts"]["correlation_status"] == "unresolved_no_approved_epoch"


def test_nahua_augury_pack_witnesses_resolve() -> None:
    """Every statement's witness file and text-record UUID must exist."""
    import json
    from pathlib import Path

    root = Path("docs/research/multitradition/nahua")
    pack = json.loads((root / "book4_augury_pack.json").read_text(encoding="utf-8"))
    assert pack["statements"], "augury pack is empty"
    for statement in pack["statements"]:
        witness_path = root / statement["witness"]["file"]
        assert witness_path.is_file(), f"missing witness {witness_path}"
        record = json.loads(witness_path.read_text(encoding="utf-8"))
        ids = {
            item["id"]
            for column in ("nahuatl_col", "spanish_col")
            for item in record["texts"][column]
        }
        assert statement["witness"]["text_record_id"] in ids, statement["statement_id"]
        # The quoted Nahuatl must actually appear in the witness markdown
        # (normalized for the diacritic stripping used in the pack).
        source_text = " ".join(
            item.get("markdown") or ""
            for column in ("nahuatl_col", "spanish_col")
            for item in record["texts"][column]
        )
        probe = statement["nahuatl"][:40]
        normalized_source = (
            source_text.replace("ç", "c").replace("â", "a").replace("ã", "a")
            .replace("õ", "o").replace("ô", "o")
        )
        assert probe[:25] in normalized_source or probe[:25] in source_text, (
            f"quotation not found in witness for {statement['statement_id']}"
        )


def test_tibetan_year_character_anchors() -> None:
    assert year_character(1027) == {
        "element": "Fire",
        "animal": "Rabbit",
        "polarity": "female",
        "sexagenary_index": 3,
    }
    assert year_character(1984)["element"] == "Wood"
    assert year_character(1984)["animal"] == "Mouse"
    assert year_character(1996)["element"] == "Fire"
    assert year_character(1996)["animal"] == "Mouse"


def test_tibetan_refuses_mewa_and_parkha(fairfield_panel: dict) -> None:
    section = _section(fairfield_panel, "tibetan")
    assert "mewa" not in section["facts"]
    assert "parkha_male_line" not in section["facts"]
    refusals = [
        d for d in section["disclosures"] if d["kind"] == DisclosureKind.REFUSAL.value
    ]
    assert any("Mewa" in d["subject"] for d in refusals)


def test_islamicate_gates_firdaria_durations(fairfield_panel: dict) -> None:
    section = _section(fairfield_panel, "islamicate_persian")
    gated = section["facts"]["distinctive_layers_gated"]
    assert any("firdaria period" in item for item in gated)


# --- Islamicate: al-Biruni reference conditions -----------------------------

CLASSICAL_SEVEN = {"Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"}


def _al_biruni_vectors() -> dict:
    import json
    from pathlib import Path

    path = Path(
        "docs/research/multitradition/islamicate/"
        "al_biruni_reference_condition_validation_vectors.json"
    )
    vectors = json.loads(path.read_text(encoding="utf-8"))["vectors"]
    return {vector["vector_id"]: vector for vector in vectors}


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_islamicate_computes_halb_and_hayyiz_for_seven_planets(
    birth: BirthInput,
) -> None:
    facts = _section(build_panel(birth), "islamicate_persian")["facts"]
    conditions = facts["planetary_conditions"]
    assert {c["body"] for c in conditions} == CLASSICAL_SEVEN
    for condition in conditions:
        # Every planet carries both flags explicitly. `None` is a computed
        # refusal (Mercury's unresolved context), not a missing key.
        assert "halb" in condition and "hayyiz" in condition
        assert condition["halb"] in (True, False, None)
        assert condition["hayyiz"] in (True, False, None)
        assert condition["sign_gender"] in ("male", "female")
        assert isinstance(condition["above_horizon"], bool)
        if condition["body"] != "Mercury":
            assert condition["halb"] is not None, condition["body"]
            assert condition["hayyiz"] is not None, condition["body"]


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_islamicate_hayyiz_implies_halb_one_way(birth: BirthInput) -> None:
    """al-Biruni section 496: every hayyiz is a halb; the converse is not."""
    facts = _section(build_panel(birth), "islamicate_persian")["facts"]
    for condition in facts["planetary_conditions"]:
        if condition["hayyiz"] is True:
            assert condition["halb"] is True, condition["body"]
    assert facts["condition_summary"]["one_way_implication_holds"] is True
    summary = facts["condition_summary"]
    assert set(summary["in_hayyiz"]) <= set(summary["in_halb"])


def test_islamicate_halb_hayyiz_reproduce_the_pack_vectors() -> None:
    """The pack ships truth tables. Reproduce them from the engine helpers."""
    from src.engine.multitradition.western import (
        islamicate_halb,
        islamicate_hayyiz,
    )

    vectors = _al_biruni_vectors()

    for case in vectors["islamicate.al_biruni.halb_truth_table"]["expected"]["cases"]:
        assert (
            islamicate_halb(
                case["planet_sect"], case["nativity_sect"], case["above_horizon"]
            )
            is case["halb"]
        ), case

    male_signs = {"aries", "gemini", "leo", "libra", "sagittarius", "aquarius"}
    genders = {"sun": "male", "venus": "female", "mars": "male"}
    hayyiz_cases = vectors["islamicate.al_biruni.hayyiz_implication_examples"][
        "expected"
    ]
    for case in hayyiz_cases["cases"]:
        planet_sect = "diurnal" if case["planet"] == "sun" else "nocturnal"
        halb = islamicate_halb(
            planet_sect, case["nativity_sect"], case["above_horizon"]
        )
        sign_gender = "male" if case["sign"] in male_signs else "female"
        hayyiz = islamicate_hayyiz(halb, genders[case["planet"]], sign_gender)
        assert halb is case["halb"], case
        assert hayyiz is case["hayyiz"], case
    assert hayyiz_cases["every_hayyiz_is_halb"] is True
    assert hayyiz_cases["halb_without_hayyiz_exists"] is True

    # Mars: male but nocturnal, so it needs the nocturnal horizon condition
    # AND a male sign. The general predicate must reproduce the pack's
    # Mars-specific worked cases without a special case.
    for case in vectors["islamicate.al_biruni.mars_hayyiz_examples"]["expected"][
        "cases"
    ]:
        halb = islamicate_halb(
            "nocturnal", case["nativity_sect"], case["above_horizon"]
        )
        sign_gender = "male" if case["sign"] in male_signs else "female"
        assert halb is case["halb"], case
        assert islamicate_hayyiz(halb, "male", sign_gender) is case["hayyiz"], case


def test_islamicate_mercury_is_conditional_not_defaulted() -> None:
    """al-Qabisi's male/diurnal Mercury must not leak into al-Biruni's."""
    from src.engine.multitradition.western import islamicate_mercury_resolution

    vectors = _al_biruni_vectors()
    cases = vectors["islamicate.al_biruni.mercury_resolution_matrix"]["expected"][
        "cases"
    ]
    expected = {case["case"]: case for case in cases}

    alone_in_aries = islamicate_mercury_resolution("male", [])
    assert alone_in_aries["gender"] == expected["alone_in_aries"]["gender"]
    assert alone_in_aries["sect"] == expected["alone_in_aries"]["sect"]

    with_venus = islamicate_mercury_resolution(
        None, [{"body": "Venus", "gender": "female", "sect": "nocturnal"}]
    )
    assert with_venus["gender"] == expected["associated_with_venus"]["gender"]
    assert with_venus["sect"] == expected["associated_with_venus"]["sect"]

    # Sign and association pointing opposite ways: the inspected passage gives
    # no conflict priority, so the sect must fail closed rather than default.
    conflicted = islamicate_mercury_resolution(
        "male", [{"body": "Venus", "gender": "female", "sect": "nocturnal"}]
    )
    assert conflicted["sect"] is None
    assert conflicted["conflict"] is True


def test_islamicate_mercury_disagreement_is_surfaced(fairfield_panel: dict) -> None:
    section = _section(fairfield_panel, "islamicate_persian")
    resolution = section["facts"]["mercury_resolution"]
    assert "al-Qabisi" in resolution["al_qabisi_difference"]
    assert "male and diurnal" in resolution["al_qabisi_difference"]
    joined = " ".join(section["reading"])
    assert "al-Qabisi" in joined and "al-Biruni" in joined


def test_islamicate_firdaria_order_follows_sect(fairfield_panel: dict) -> None:
    facts = _section(fairfield_panel, "islamicate_persian")["facts"]
    vectors = _al_biruni_vectors()
    assert facts["sect"]["nativity_sect"] == "diurnal"
    assert (
        facts["firdaria"]["major_order"]
        == vectors["islamicate.al_biruni.firdaria.diurnal_order"]["expected"][
            "major_order"
        ]
    )
    nocturnal = _section(build_panel(SYDNEY), "islamicate_persian")["facts"]
    assert nocturnal["sect"]["nativity_sect"] == "nocturnal"
    assert (
        nocturnal["firdaria"]["major_order"]
        == vectors["islamicate.al_biruni.firdaria.nocturnal_order"]["expected"][
            "major_order"
        ]
    )


def test_islamicate_subperiod_structure_matches_pack_vector() -> None:
    from src.engine.multitradition.western import islamicate_firdaria_subperiods

    descending = ["saturn", "jupiter", "mars", "sun", "venus", "mercury", "moon"]
    expected = _al_biruni_vectors()[
        "islamicate.al_biruni.firdaria.sun_subperiod_structure"
    ]["expected"]["subperiods"]
    assert islamicate_firdaria_subperiods("sun", descending) == expected
    # Structure only: no seventh carries a duration of any kind.
    for major in descending:
        parts = islamicate_firdaria_subperiods(major, descending)
        assert len(parts) == 7
        assert parts[0]["rulers"] == [major]
        assert all(set(p) == {"index", "fraction_start", "fraction_end", "rulers"}
                   for p in parts)


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_islamicate_emits_no_firdaria_durations(birth: BirthInput) -> None:
    """Section 395 gives no node periods and no duration table. Emit none."""
    firdaria = _section(build_panel(birth), "islamicate_persian")["facts"]["firdaria"]
    assert firdaria["durations_emitted"] is False
    assert firdaria["node_periods_emitted"] is False

    offenders: list[str] = []

    def walk(node, path: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                walk(value, f"{path}.{key}")
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, f"{path}[{index}]")
        elif isinstance(node, (int, float)) and not isinstance(node, bool):
            leaf = path.rsplit(".", 1)[-1].lower()
            if any(token in leaf for token in ("year", "age", "date", "duration")):
                offenders.append(f"{path}={node}")

    walk(firdaria, "firdaria")
    assert not offenders, f"firdaria emitted duration-like values: {offenders}"
    # The lunar nodes are not chronocrators in this pack.
    assert "north_node" not in str(firdaria["major_order"])
    assert len(firdaria["major_order"]) == 7


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_islamicate_refusal_disclosures_survive(birth: BirthInput) -> None:
    section = _section(build_panel(birth), "islamicate_persian")
    refusals = [
        d for d in section["disclosures"] if d["kind"] == DisclosureKind.REFUSAL.value
    ]
    subjects = " ".join(d["subject"] for d in refusals)
    details = " ".join(d["detail"] for d in refusals)
    assert "Firdaria periods and ages" in subjects
    assert "section 395" in details
    assert "major-duration table" in details
    # The joy boundary and the prediction boundary must both stay refused.
    assert any("halb or hayyiz" in d["subject"] for d in refusals)
    assert any("Prediction" == d["subject"] for d in refusals)
    joined_reading = " ".join(section["reading"])
    assert "no firdaria ages or dates" in joined_reading.lower()


def test_islamicate_variants_are_surfaced_with_lineage(fairfield_panel: dict) -> None:
    """The 8 preserved variants are the publishable scholarship. Show them."""
    section = _section(fairfield_panel, "islamicate_persian")
    concordance = section["facts"]["variant_concordance"]
    assert concordance["candidate_passages"] == 30
    assert concordance["preserved_variants"] == 8
    assert len(concordance["observations"]) == 8

    rows = concordance["firdaria_year_values_by_lineage"]
    lineages = {row["lineage"] for row in rows}
    assert "Arabic" in lineages
    assert "Latin - Hermann of Carinthia" in lineages
    assert "Latin - John of Seville" in lineages
    assert "Latin - Adelard of Bath" in lineages

    def row_for(lineage_fragment: str, work_fragment: str) -> dict:
        return next(
            r
            for r in rows
            if lineage_fragment in r["lineage"] and work_fragment in r["work"]
        )

    # Mars: Arabic 7 against Hermann's 8.
    assert row_for("Arabic", "Great Introduction")["mars_years"] == 7
    assert row_for("Hermann of Carinthia", "Great Introduction")["mars_years"] == 8
    # John of Seville: listed values total 74 against a stated 75.
    john = row_for("John of Seville", "Great Introduction")
    assert john["recomputed_total"] == 74
    assert john["stated_total"] == 75
    assert john["totals_agree"] is False
    # Adelard of Bath: 75 against a stated 77, where the Arabic agrees with itself.
    adelard = row_for("Adelard of Bath", "Abbreviation")
    assert adelard["recomputed_total"] == 75
    assert adelard["stated_total"] == 77
    assert adelard["totals_agree"] is False
    assert row_for("Arabic", "Abbreviation")["totals_agree"] is True

    # Terminology variants: collapse and competentia.
    observation_ids = {o["observation_id"] for o in concordance["observations"]}
    assert "halb_hayyiz_qabisi_latin_terminology" in observation_ids
    assert "hayyiz_abbreviation_competentia" in observation_ids


def test_islamicate_reading_attributes_every_variant_by_lineage(
    fairfield_panel: dict,
) -> None:
    section = _section(fairfield_panel, "islamicate_persian")
    reading = section["reading"]
    assert reading, "Islamicate reading missing"
    joined = " ".join(reading)

    # Sect is stated first - it conditions everything after it.
    assert "Sect first" in reading[0]
    assert "al-Biruni" in reading[0]
    # Condition before structure, structure before variants.
    halb_index = next(i for i, line in enumerate(reading) if "halb" in line)
    firdaria_index = next(i for i, line in enumerate(reading) if "Firdaria" in line)
    variant_index = next(i for i, line in enumerate(reading) if "Variant," in line)
    assert halb_index < firdaria_index < variant_index

    # Every lineage is named, and no variant is attributed to "Islamic astrology".
    for lineage in (
        "Hermann of Carinthia",
        "John of Seville",
        "Adelard of Bath",
        "Arabic",
    ):
        assert lineage in joined, lineage
    assert "competentia" in joined
    assert "alhaiz" in joined
    assert "Islamic astrology" not in joined

    # Named authors, never a generic tradition label.
    for author in ("al-Biruni", "Abu Ma'shar", "al-Qabisi"):
        assert author in joined, author

    # The arithmetic disagreements are stated numerically, not hand-waved.
    assert "74" in joined and "75" in joined and "77" in joined


def test_render_produces_markdown_with_labels(fairfield_panel: dict) -> None:
    text = render(fairfield_panel)
    assert text.startswith("# Multi-tradition panel")
    assert "Refused" in text
    assert "Configured" in text
    for section in fairfield_panel["sections"]:
        assert section["display_name"] in text


def test_broken_section_does_not_kill_panel(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.engine.multitradition import panel as panel_module

    def explode(*_args, **_kwargs):
        raise RuntimeError("simulated failure")

    monkeypatch.setattr(panel_module.mesoamerican, "build_maya", explode)
    result = panel_module.build_panel(FAIRFIELD)
    maya = _section(result, "maya")
    assert maya["error"] and "simulated failure" in maya["error"]
    # Every other section still built.
    others = [s for s in result["sections"] if s["tradition_id"] != "maya"]
    assert all(not s.get("error") for s in others)


# --------------------------------------------------------------------------- #
# Jyotisha reading layer: drishti, antardasha, combustion, naisargika, yogas,
# and the judgment hierarchy the defensibility spec fixes.
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def vedic_sections() -> dict:
    """Every fixture's Jyotisha section, built once for the whole module."""
    return {
        birth.name: _section(build_panel(birth), "indian_jyotisha")
        for birth in ALL_FIXTURES
    }


def _step_numbers(reading: list[str]) -> list[int]:
    """Leading step label of every reading line, per the spec's hierarchy."""
    numbers = []
    for line in reading:
        head = line.split(".", 1)[0]
        assert head.isdigit(), f"reading line carries no step label: {line[:70]}"
        numbers.append(int(head))
    return numbers


def test_drishti_computed_for_every_graha(fairfield_panel: dict) -> None:
    """Universal 7th aspect for all; special aspects only for Mars/Jupiter/Saturn."""
    from src.engine.multitradition.vedic import (
        GRAHA_ORDER,
        SPECIAL_DRISHTI,
        drishti_houses,
    )

    facts = _section(fairfield_panel, "indian_jyotisha")["facts"]
    rows = {row["graha"]: row for row in facts["drishti"]}
    assert set(rows) == set(GRAHA_ORDER), "a graha is missing from the drishti table"

    for graha in facts["grahas"]:
        name = graha["graha"]
        row = rows[name]
        aspects = drishti_houses(name, graha["house"])
        assert 7 in aspects, f"{name} lacks the universal 7th aspect"
        assert len(aspects) == 1 + len(SPECIAL_DRISHTI.get(name, ()))
        assert row["from_house"] == graha["house"]
        assert row["aspects_houses"] == sorted(set(aspects.values()))
        assert graha["drishti_houses"] == row["aspects_houses"]

    # The classical rule, checked from the lagna so the arithmetic is legible.
    assert set(drishti_houses("Sun", 1).values()) == {7}
    assert set(drishti_houses("Mars", 1).values()) == {4, 7, 8}
    assert set(drishti_houses("Jupiter", 1).values()) == {5, 7, 9}
    assert set(drishti_houses("Saturn", 1).values()) == {3, 7, 10}
    # Wrap-around: Saturn in the 12th aspects the 2nd, 6th and 9th.
    assert drishti_houses("Saturn", 12) == {3: 2, 7: 6, 10: 9}
    # Rahu and Ketu take the 7th only under the disclosed scheme.
    assert set(drishti_houses("Rahu", 5).values()) == {11}


def test_antardasha_subdivides_the_running_mahadasha(vedic_sections: dict) -> None:
    """Nine bhuktis, sequence from the mahadasha lord, summing to its length."""
    from src.engine.multitradition.vedic import DASHA_SEQUENCE, DASHA_YEARS

    order = [name for name, _ in DASHA_SEQUENCE]
    for label, section in vedic_sections.items():
        block = section["facts"]["vimshottari_antardashas"]
        assert block, f"{label}: no antardasha block"
        periods = block["periods"]
        lord = block["mahadasha_lord"]
        full = block["mahadasha_full_years"]

        assert len(periods) == 9, f"{label}: expected nine bhuktis"
        # Sub-lords run the standard sequence starting from the mahadasha lord.
        start = order.index(lord)
        assert [p["antardasha_lord"] for p in periods] == [
            order[(start + step) % 9] for step in range(9)
        ], label
        assert periods[0]["antardasha_lord"] == lord, label

        # Proportional subdivision, exactly as the spec states it.
        for period in periods:
            expected = full * DASHA_YEARS[period["antardasha_lord"]] / 120
            assert period["years"] == pytest.approx(expected, abs=1e-6), label
            assert period["mahadasha_lord"] == lord

        # The sub-periods reconstitute the mahadasha, within rounding.
        assert sum(p["years"] for p in periods) == pytest.approx(full, abs=1e-4)
        assert block["sum_of_antardasha_years"] == pytest.approx(full, abs=1e-4)
        assert "/ 120" in block["subdivision_rule"]

        # The running mahadasha is the one being subdivided, and the running
        # bhukti sits inside it.
        current = section["facts"]["vimshottari_current"]
        assert current["status"] == "running", label
        assert current["mahadasha"]["lord"] == lord, label
        running = current["antardasha"]
        assert running is not None, label
        assert running["mahadasha_lord"] == lord, label
        stamp = current["as_of"]
        assert running["start"] <= stamp < running["end"], label
        assert current["mahadasha"]["start"] <= stamp < current["mahadasha"]["end"]


def test_antardasha_of_a_birth_partial_mahadasha_still_sums_to_full(
    fairfield_panel: dict,
) -> None:
    """A mahadasha already running at birth is subdivided from its notional start."""
    from src.engine.multitradition.vedic import (
        DASHA_YEARS,
        _antardashas,
        _mahadasha_spans,
    )

    facts = _section(fairfield_panel, "indian_jyotisha")["facts"]
    lord = facts["janma_nakshatra"]["lord"]
    spans = _mahadasha_spans(FAIRFIELD, lord, 0.6)
    first = spans[0]
    assert first["partial_at_birth"] is True
    assert first["notional_start"] < first["start"], "balance must predate birth"

    block = _antardashas(first)
    assert block["mahadasha_full_years"] == DASHA_YEARS[lord]
    assert sum(p["years"] for p in block["periods"]) == pytest.approx(
        DASHA_YEARS[lord], abs=1e-4
    )
    # Bhuktis that closed before the birth moment are flagged, not hidden.
    assert any(p["before_birth"] for p in block["periods"])


def test_combustion_flags_are_booleans(vedic_sections: dict) -> None:
    from src.engine.multitradition.vedic import (
        COMBUSTION_ORBS,
        COMBUSTION_ORBS_RETROGRADE,
    )

    for label, section in vedic_sections.items():
        for graha in section["facts"]["grahas"]:
            assert isinstance(graha["combust"], bool), f"{label}/{graha['graha']}"
            assert isinstance(graha["solar_separation_degrees"], float)
            orb = graha["combustion_orb_degrees"]
            assert orb is None or isinstance(orb, float)
            if orb is None:
                # No orb, no claim: the Sun itself and the nodes.
                assert graha["combust"] is False
                assert graha["graha"] in {"Sun", "Rahu", "Ketu"}
            else:
                expected = (
                    COMBUSTION_ORBS_RETROGRADE.get(graha["graha"], orb)
                    if graha["retrograde"]
                    else COMBUSTION_ORBS[graha["graha"]]
                )
                assert orb == expected
                assert graha["combust"] is (
                    graha["solar_separation_degrees"] <= orb
                )


def test_fairfield_moon_is_combust_under_the_configured_orb(
    fairfield_panel: dict,
) -> None:
    facts = _section(fairfield_panel, "indian_jyotisha")["facts"]
    by_name = {g["graha"]: g for g in facts["grahas"]}
    moon = by_name["Moon"]
    assert moon["combust"] is True
    assert moon["combustion_orb_degrees"] == 12.0
    assert moon["solar_separation_degrees"] == pytest.approx(7.85, abs=0.05)
    # Own sign and combust at once - the condition the reading must not smooth over.
    assert moon["dignity"] == "own sign"
    assert by_name["Sun"]["combust"] is False
    assert by_name["Mercury"]["combust"] is False


def test_combustion_orbs_disclosed_as_configured(fairfield_panel: dict) -> None:
    section = _section(fairfield_panel, "indian_jyotisha")
    configured = [
        d
        for d in section["disclosures"]
        if d["kind"] == DisclosureKind.CONFIGURED_METHOD.value
        and "ombustion" in d["subject"]
    ]
    assert configured, "combustion orbs are a product choice and must be disclosed"
    detail = configured[0]["detail"]
    for expected in (
        "Moon 12", "Mars 17", "Mercury 14", "Jupiter 11", "Venus 10", "Saturn 15",
    ):
        assert expected in detail, expected
    assert "retrograde" in detail
    assert configured[0]["alternatives"]
    # And the table itself is emitted as a fact, not only as prose.
    orbs = section["facts"]["combustion_orbs_configured"]
    assert orbs["direct"]["Mars"] == 17.0
    assert orbs["retrograde_overrides"] == {"Mercury": 12.0, "Venus": 8.0}


def test_naisargika_table_is_complete_and_asymmetric() -> None:
    from src.engine.multitradition.vedic import (
        GRAHAS,
        NAISARGIKA,
        naisargika_relation,
    )

    for graha in GRAHAS:
        row = NAISARGIKA[graha]
        listed = [*row["friends"], *row["neutral"], *row["enemies"]]
        assert sorted(listed) == sorted(set(GRAHAS) - {graha}), graha
        assert len(listed) == len(set(listed)), f"{graha} listed twice"

    # The classical table is deliberately not symmetric.
    assert naisargika_relation("Mars", "Moon") == "friend"
    assert naisargika_relation("Moon", "Mars") == "neutral"
    assert naisargika_relation("Saturn", "Sun") == "enemy"
    assert naisargika_relation("Moon", "Moon") == "own sign lord"
    # The nodes carry no agreed naisargika row.
    assert naisargika_relation("Rahu", "Sun") == "not assessed for nodes"


def test_naisargika_dispositor_relation_on_every_graha(
    vedic_sections: dict,
) -> None:
    from src.engine.multitradition.vedic import (
        SIGN_LORD,
        naisargika_relation,
    )

    for label, section in vedic_sections.items():
        for graha in section["facts"]["grahas"]:
            assert graha["dispositor"] == SIGN_LORD[graha["rasi"]], label
            assert graha["dispositor_relation"] == naisargika_relation(
                graha["graha"], graha["dispositor"]
            ), f"{label}/{graha['graha']}"


def test_yogas_report_constituent_facts(fairfield_panel: dict) -> None:
    """A yoga is only defendable if the facts that made it true are shown."""
    from src.engine.multitradition.vedic import drishti_houses

    facts = _section(fairfield_panel, "indian_jyotisha")["facts"]
    yogas = facts["yogas"]
    assert yogas, "Leo lagna with Mars owning 4 and 9 must yield at least one yoga"

    houses = {g["graha"]: g["house"] for g in facts["grahas"]}
    for yoga in yogas:
        assert yoga["rule"], yoga
        assert len(yoga["constituent_facts"]) >= 2, yoga["yoga"]
        joined = " ".join(yoga["constituent_facts"])
        for graha in yoga["grahas"]:
            assert graha in joined, f"{yoga['yoga']} never names {graha}"
        # Every record cites at least one house number - the structural claim.
        assert any(char.isdigit() for char in joined)
        # Any claimed relation must actually hold in the chart.
        if len(yoga["grahas"]) == 2:
            first, second = yoga["grahas"]
            if yoga["relation"] == "conjunct":
                assert houses[first] == houses[second], yoga["summary"]
            else:
                assert houses[second] in drishti_houses(
                    first, houses[first]
                ).values()
                assert houses[first] in drishti_houses(
                    second, houses[second]
                ).values()

    # Leo lagna: Mars owns the 4th (Scorpio, a kendra) and the 9th (Aries,
    # a trikona), which is the textbook yogakaraka identification.
    yogakaraka = [y for y in yogas if y["yoga"] == "Yogakaraka"]
    assert [y["grahas"] for y in yogakaraka] == [["Mars"]]
    constituents = " ".join(yogakaraka[0]["constituent_facts"])
    assert "kendra" in constituents and "trikona" in constituents
    assert "house 4" in constituents and "house 9" in constituents

    # The lagna lord is a kendra AND trikona lord trivially; it must not be
    # promoted to yogakaraka on that basis alone.
    assert facts["lagna"]["lord"] == "Sun"
    assert all("Sun" not in y["grahas"] for y in yogakaraka)

    assert any(y["yoga"] == "Raja Yoga" for y in yogas)
    assert any(y["yoga"] == "Dhana Yoga" for y in yogas)
    # Mercury owns the 2nd and the 11th - two dhana houses in one hand.
    single_lord_dhana = [
        y for y in yogas if y["yoga"] == "Dhana Yoga" and len(y["grahas"]) == 1
    ]
    assert [y["grahas"] for y in single_lord_dhana] == [["Mercury"]]


def test_yoga_records_are_well_formed_for_every_fixture(
    vedic_sections: dict,
) -> None:
    for label, section in vedic_sections.items():
        for yoga in section["facts"]["yogas"]:
            assert yoga["yoga"] in {"Yogakaraka", "Raja Yoga", "Dhana Yoga"}, label
            assert yoga["grahas"] and yoga["summary"] and yoga["rule"]
            assert yoga["constituent_facts"], f"{label}: {yoga['yoga']} bare name"


def test_navamsha_cross_check_surfaces_d1_d9_divergence(
    fairfield_panel: dict,
) -> None:
    """Saturn is neutral in D1 Pisces but exalted in D9 Libra - that must show."""
    section = _section(fairfield_panel, "indian_jyotisha")
    rows = {r["graha"]: r for r in section["facts"]["navamsha_cross_check"]}
    saturn = rows["Saturn"]
    assert saturn["rasi_d1"] == "Pisces"
    assert saturn["dignity_d1"] == "neutral placement"
    assert saturn["rasi_d9"] == "Libra"
    assert saturn["dignity_d9"] == "exalted"
    assert saturn["diverges"] is True
    assert "raises" in saturn["verdict"]

    # Jupiter runs the other way: own sign in D1, plain in D9.
    jupiter = rows["Jupiter"]
    assert jupiter["dignity_d1"] == "own sign"
    assert jupiter["diverges"] is True
    assert "undercuts" in jupiter["verdict"]

    # And the divergence must reach the prose, not just the fact block.
    step_six = " ".join(
        line for line in section["reading"] if line.startswith("6.")
    )
    assert "Saturn" in step_six and "Libra" in step_six and "exalted" in step_six


def test_reading_follows_the_judgment_hierarchy(vedic_sections: dict) -> None:
    """Lagna first, yogas seventh, dasha last - the spec's order, enforced."""
    for label, section in vedic_sections.items():
        reading = section.get("reading")
        assert reading, f"{label}: Jyotisha reading missing"
        numbers = _step_numbers(reading)
        assert numbers == sorted(numbers), f"{label}: steps run out of order"
        assert set(numbers) == set(range(1, 9)), f"{label}: missing a step"
        assert numbers[0] == 1 and numbers[-1] == 8, label

        # 1. lagna, 2. Moon before any solar claim, 7. yogas only after.
        assert numbers.index(1) < numbers.index(7), label
        assert "Lagna" in reading[0], label
        moon_line = reading[numbers.index(2)]
        assert "janma" in moon_line.lower(), label
        assert "outranks the Sun" in moon_line, label

        # Nothing may name a yoga before step 7.
        first_yoga = next(
            (i for i, line in enumerate(reading) if "oga" in line), None
        )
        assert first_yoga is not None, label
        assert numbers[first_yoga] == 7, f"{label}: a yoga was named too early"

        # 8. dasha is read against the natal structure, not free-floating.
        dasha = " ".join(line for line in reading if line.startswith("8."))
        assert "mahadasha" in dasha.lower() and "antardasha" in dasha.lower()
        assert "natal structure" in dasha, label


def test_vedic_refusals_cover_the_spec_list(vedic_sections: dict) -> None:
    """Ayurdaya, muhurta/remedies, varna, compatibility, Shadbala/Ashtakavarga."""
    required = ("ayurdaya", "muhurta", "varna", "marriage", "shadbala")
    for label, section in vedic_sections.items():
        refusals = [
            d
            for d in section["disclosures"]
            if d["kind"] == DisclosureKind.REFUSAL.value
        ]
        assert refusals, label
        blob = " ".join(f"{d['subject']} {d['detail']}" for d in refusals).lower()
        for token in required:
            assert token in blob, f"{label}: no refusal covers {token}"
        assert "ashtakavarga" in blob, label
        # The refusals must be actual refusals, not hedged claims.
        assert "no lifespan" in blob or "no longevity" in blob, label


def test_vedic_reading_never_asserts_a_refused_claim(vedic_sections: dict) -> None:
    """The prose must not smuggle back what the refusals removed."""
    banned = ("shadbala", "ashtakavarga", "varna", "guna milan", "gemstone")
    for label, section in vedic_sections.items():
        prose = " ".join(section["reading"]).lower()
        for token in banned:
            if token in ("shadbala", "ashtakavarga"):
                # Named only to say they are not used.
                for line in section["reading"]:
                    if token in line.lower():
                        assert "not evaluated" in line.lower(), f"{label}: {token}"
                continue
            assert token not in prose, f"{label}: reading asserts {token}"


# --------------------------------------------------------------------------
# Egyptian civil calendar, Zi Wei Dou Shu, Vietnamese lunisolar calendar
# --------------------------------------------------------------------------

NEW_TRADITION_IDS = ("pharaonic_egyptian", "ziwei_doushu", "vietnamese")


@pytest.fixture(scope="module")
def quito_panel() -> dict:
    return build_panel(QUITO_LATE_ZI)


def _disclosure_blob(section: dict, kind: DisclosureKind | None = None) -> str:
    return " ".join(
        f"{d['subject']} {d['detail']}"
        for d in section["disclosures"]
        if kind is None or d["kind"] == kind.value
    ).lower()


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_new_sections_build_for_every_fixture(birth: BirthInput) -> None:
    """All three new packs must render for every fixture, with disclosures."""
    panel = build_panel(birth)
    present = {s["tradition_id"] for s in panel["sections"]}
    for tradition_id in NEW_TRADITION_IDS:
        assert tradition_id in present, f"{tradition_id} missing from panel"
        section = _section(panel, tradition_id)
        assert not section.get("error"), f"{tradition_id}: {section.get('error')}"
        assert section["disclosures"], f"{tradition_id} discloses nothing"
        assert section["facts"], f"{tradition_id} emitted no facts"


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_new_sections_each_carry_a_refusal(birth: BirthInput) -> None:
    """Each of these packs has something it cannot say; it must say so."""
    panel = build_panel(birth)
    for tradition_id in NEW_TRADITION_IDS:
        section = _section(panel, tradition_id)
        refusals = [
            d
            for d in section["disclosures"]
            if d["kind"] == DisclosureKind.REFUSAL.value
        ]
        assert refusals, f"{tradition_id} refuses nothing"


# --- Egyptian -------------------------------------------------------------


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_egyptian_refuses_to_place_the_birth(birth: BirthInput) -> None:
    """default_profile is null in the pack, so the birth is never converted."""
    section = _section(build_panel(birth), "pharaonic_egyptian")
    placement = section["facts"]["birth_placement"]
    assert placement["placed"] is False
    assert placement["chronology_profile_used"] is None
    assert placement["reason"] == "no_approved_chronology_profile"
    # The withheld input is reported, never a converted date.
    assert "season_id" not in placement
    assert "year_position" not in placement
    assert section["facts"]["chronology_contract"]["default_profile"] is None
    refusals = _disclosure_blob(section, DisclosureKind.REFUSAL)
    assert "chronology" in refusals
    assert "default_profile" in refusals or "null" in refusals


def test_egyptian_structure_matches_the_validated_pack(fairfield_panel: dict) -> None:
    facts = _section(fairfield_panel, "pharaonic_egyptian")["facts"]
    model = facts["calendar_model"]
    assert model["year_length_days"] == 365
    assert model["ordinary_months"] == 12
    assert model["ordinary_month_length_days"] == 30
    assert model["ordinary_days"] == 360
    assert model["additional_days"] == 5
    assert model["intercalation"] is False
    assert model["seasons"] == [
        "Akhet (4 months)",
        "Peret (4 months)",
        "Shemu (4 months)",
    ]
    structure = facts["cycle_internal_structure"]
    assert structure["position_date_round_trip_over_365_positions"] is True
    # Landmarks from the pack's own vectors.
    assert structure["landmark_positions"]["I Akhet 1"] == 0
    assert structure["landmark_positions"]["II Akhet 1"] == 30
    assert structure["landmark_positions"]["I Peret 1"] == 120
    assert structure["landmark_positions"]["I Shemu 1"] == 240
    assert structure["landmark_positions"]["heriu-renpet day 5"] == 364


def test_egyptian_conversion_fails_closed() -> None:
    """The pack's negative chronology vectors must be reproduced exactly."""
    from src.engine.multitradition.egyptian import date_to_position, place_civil_date

    assert place_civil_date(0, None)["error"] == "missing_profile"
    complete = {
        "profile_id": "x",
        "tradition_id": "pharaonic_egyptian",
        "model_id": "alexandrian_coptic_leap",
        "anchor_civil_date": "2000-01-01",
        "calendar_policy": "test",
        "anchor_egyptian_date": {"season_id": "akhet", "month_in_season": 1, "day": 1},
        "historical_regime": "test",
        "authority": "test",
        "uncertainty_days": 0,
        "locality": "test",
        "day_start": "test",
    }
    assert place_civil_date(0, complete)["error"] == "wrong_calendar_model"
    # An incomplete profile is not silently completed.
    partial = dict(complete, model_id="pharaonic_civil_365")
    del partial["uncertainty_days"]
    assert place_civil_date(0, partial)["error"] == "missing_profile"
    # Ordinary months have exactly thirty days; the year has exactly five extras.
    assert date_to_position("akhet", 1, 31)["error"] == "invalid_ordinary_day"
    assert (
        date_to_position("heriu_renpet", None, 6)["error"] == "invalid_additional_day"
    )


def test_egyptian_emits_no_forbidden_output_fields(fairfield_panel: dict) -> None:
    """The pack names the fields a calendar position may never turn into."""
    import json

    section = _section(fairfield_panel, "pharaonic_egyptian")
    blob = json.dumps(section["facts"]).lower()
    for forbidden in ("prognosis", "personality", "good_bad", "compatibility"):
        assert f'"{forbidden}"' not in blob, f"forbidden field {forbidden} emitted"


def test_egyptian_surfaces_the_sallier_iv_access_refusal(
    fairfield_panel: dict,
) -> None:
    """Source-access-only, and the epagomenal section is lost, not proven absent."""
    section = _section(fairfield_panel, "pharaonic_egyptian")
    witness = section["facts"]["sallier_iv_witness"]
    assert witness["rule_extraction_ready"] is False
    assert witness["complete_translation_present"] is False
    assert witness["historical_absence_proven"] is False
    assert any("Epagomenal" in item for item in witness["lost_ranges"])
    refusals = _disclosure_blob(section, DisclosureKind.REFUSAL)
    assert "sallier" in refusals
    assert "lost" in refusals
    assert (
        section["facts"]["hemerology_boundary"][
            "missing_witness_text_creates_negative_rule"
        ]
        is False
    )


# --- Zi Wei Dou Shu -------------------------------------------------------


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_ziwei_only_builds_a_chart_when_every_calendar_regime_agrees(
    birth: BirthInput,
) -> None:
    """The regime check is a gate, not decoration: disagreement must refuse."""
    section = _section(build_panel(birth), "ziwei_doushu")
    check = section["facts"]["calendar_regime_check"]
    construction = section["facts"]["chart_construction"]

    months = {regime["chart_month"] for regime in check["regimes"]}
    assert check["chart_month_invariant"] is (len(months) == 1)

    if check["chart_month_invariant"]:
        assert construction["status"] == "constructed_palaces_only"
        assert construction["chart_month"] == check["chart_month"]
    else:
        assert construction["status"] == "blocked_calendar_regimes_disagree"
        assert "life_palace" not in construction
        assert "four_transformations" not in section["facts"]

    # Whatever the outcome, these stay refused for reasons the regime cannot fix.
    refusals = _disclosure_blob(section, DisclosureKind.REFUSAL)
    assert "five tigers" in refusals
    assert "bureau" in refusals
    assert "decade" in refusals


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_ziwei_never_places_a_main_star_or_a_meaning(birth: BirthInput) -> None:
    """Palaces are a board. The pack has no table that puts a piece on it."""
    section = _section(build_panel(birth), "ziwei_doushu")
    construction = section["facts"]["chart_construction"]
    if construction["status"] != "constructed_palaces_only":
        return
    absent = " ".join(construction["still_absent"]).lower()
    for missing in ("bureau", "main star", "five tigers", "meaning"):
        assert missing in absent
    # No main star may be PLACED on any palace - the fourteen main stars must
    # appear nowhere in the palace/board facts. (Four Transformations is a
    # separate, explicitly disclosed table lookup keyed on year stem alone,
    # not a placement, and the pack's own worked-example reproduction in
    # vector_selfcheck legitimately names stars too - neither is checked here.)
    board_blob = json.dumps(construction).lower()
    for star in ("ziwei", "tianfu", "pojun", "tanlang", "qisha"):
        assert f'"{star}"' not in board_blob
    assert not section.get("reading")


def test_ziwei_life_and_body_palace_structure() -> None:
    """Life and body are mirror counts from the month palace; check the algebra."""
    from src.engine.multitradition.ziwei import (
        BRANCHES,
        body_palace_branch,
        life_palace_branch,
        month_palace_branch,
    )

    for month in range(1, 13):
        anchor = BRANCHES.index(month_palace_branch(month))
        lives = {life_palace_branch(month, hour) for hour in BRANCHES}
        bodies = {body_palace_branch(month, hour) for hour in BRANCHES}
        # Each sweeps all twelve branches exactly once across the twelve hours.
        assert lives == set(BRANCHES)
        assert bodies == set(BRANCHES)
        for hour in BRANCHES:
            life = BRANCHES.index(life_palace_branch(month, hour))
            body = BRANCHES.index(body_palace_branch(month, hour))
            # Equidistant from the month palace in opposite directions.
            assert (anchor - life) % 12 == (body - anchor) % 12
        # Zi hour puts both on the month palace - the pack's own month-1 example.
        assert life_palace_branch(month, "zi") == month_palace_branch(month)
        assert body_palace_branch(month, "zi") == month_palace_branch(month)


def test_ziwei_four_transformations_table_is_complete_and_distinct() -> None:
    """Ten stems, four distinct stars each, no stem missing."""
    from src.engine.multitradition.ziwei import four_transformations

    stems = ("jia", "yi", "bing", "ding", "wu", "ji", "geng", "xin", "ren", "gui")
    for stem in stems:
        row = four_transformations(stem)
        assert set(row) == {"lu", "quan", "ke", "ji"}
        assert len(set(row.values())) == 4, f"{stem} repeats a star"


def test_ziwei_chart_month_survives_every_meridian_for_the_fairfield_birth(
    fairfield_panel: dict,
) -> None:
    """The claim that makes the configured calendar defendable, asserted directly.

    Three regimes, one chart month - and a lunar DAY that does move, which is
    the stated reason the bureau stays refused. If that ever stops being true
    the refusal loses its evidence and this test should fail loudly.
    """
    check = _section(fairfield_panel, "ziwei_doushu")["facts"][
        "calendar_regime_check"
    ]
    assert {r["regime_id"] for r in check["regimes"]} == {
        "purple_mountain_120e",
        "beijing_local_mean_time",
        "indochina_105e",
    }
    assert {r["chart_month"] for r in check["regimes"]} == {6}
    assert check["chart_month_invariant"] is True
    assert check["lunar_day_invariant"] is False


def test_ziwei_reproduces_its_pack_vectors(fairfield_panel: dict) -> None:
    check = _section(fairfield_panel, "ziwei_doushu")["facts"]["vector_selfcheck"]
    assert check["ziwei.quanshu.wenchang_wenqu.zi"]["wenchang"] == "xu"
    assert check["ziwei.quanshu.wenchang_wenqu.zi"]["wenqu"] == "chen"
    assert check["ziwei.quanshu.wenchang_wenqu.chou"]["wenchang"] == "you"
    assert check["ziwei.quanshu.wenchang_wenqu.chou"]["wenqu"] == "si"
    for key, value in check.items():
        if isinstance(value, dict) and "matches_source_example" in value:
            assert value["matches_source_example"] is True, key
    assert check["five_tigers_table"] == "not_implemented_by_pack_instruction"


def test_ziwei_emits_every_double_hour_basis_and_no_meaning(
    fairfield_panel: dict,
) -> None:
    section = _section(fairfield_panel, "ziwei_doushu")
    placements = section["facts"]["hour_keyed_placements"]
    assert set(placements) == {"true_solar_time", "clock_time", "local_mean_time"}
    for row in placements.values():
        assert row["wenchang_branch"] and row["wenqu_branch"]
    # Grade D construction candidates may not become prose.
    assert not section.get("reading")
    assert section["evidence_grade"] == "transcription_grade"


def test_ziwei_wenchang_wenqu_are_bijective_over_the_twelve_hours() -> None:
    """Each anchor sweeps all twelve branches exactly once - one per double-hour."""
    from src.engine.multitradition.ziwei import (
        BRANCHES,
        wenchang_branch,
        wenqu_branch,
    )

    assert {wenchang_branch(b) for b in BRANCHES} == set(BRANCHES)
    assert {wenqu_branch(b) for b in BRANCHES} == set(BRANCHES)
    # The two stars coincide only where the counts meet: Mao and You.
    coincide = {b for b in BRANCHES if wenchang_branch(b) == wenqu_branch(b)}
    assert coincide == {"mao", "you"}


# --- Vietnamese lunisolar calendar ----------------------------------------


def test_vietnamese_reproduces_every_published_vector(fairfield_panel: dict) -> None:
    """The 1984-85 worked tables are the pack's only proof; reproduce them all."""
    check = _section(fairfield_panel, "vietnamese")["facts"][
        "worked_example_selfcheck"
    ]
    assert check["all_published_vectors_reproduced"] is True
    assert check["month11_1984"]["computed"]["start_civil_date"] == "1984-11-23"
    assert check["month11_1984"]["computed"]["end_civil_date"] == "1984-12-21"
    divergence = check["new_year_divergence_1985"]["computed"]
    assert divergence["vietnamese_new_year"] == "1985-01-21"
    assert divergence["chinese_new_year"] == "1985-02-20"
    leap = check["intercalary_month_1985"]["computed"]
    assert leap["is_leap_year"] is True
    assert leap["intercalary_month_start"] == "1985-03-21"
    assert leap["intercalary_month_end"] == "1985-04-19"
    for key, value in check.items():
        if isinstance(value, dict) and "matches" in value:
            assert value["matches"] is True, key


def test_vietnamese_uses_vietnams_civil_day_not_the_birth_places(
    quito_panel: dict,
) -> None:
    """A 23:20 Quito birth is already the next day in Vietnam - and must say so."""
    facts = _section(quito_panel, "vietnamese")["facts"]
    dates = facts["civil_dates"]
    assert dates["birth_place_civil_date"] == "2004-06-21"
    assert dates["vietnamese_civil_date"] == "2004-06-22"
    assert dates["differs_from_birth_place_day"] is True
    assert facts["calendar_profile"]["civil_offset_hours"] == 7.0
    assert facts["calendar_profile"]["reference_longitude"] == "105E"


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_vietnamese_lunar_date_is_well_formed(birth: BirthInput) -> None:
    facts = _section(build_panel(birth), "vietnamese")["facts"]
    lunar = facts["lunar_date"]
    assert 1 <= lunar["month_number"] <= 12
    assert 1 <= lunar["day"] <= 30
    assert lunar["month_length_days"] in (29, 30)
    assert isinstance(lunar["is_intercalary"], bool)
    structure = facts["lunar_year_structure"]
    assert structure["month_count"] in (12, 13)
    assert structure["is_leap_year"] is (structure["month_count"] == 13)


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_vietnamese_refuses_natal_claims_and_historical_regimes(
    birth: BirthInput,
) -> None:
    section = _section(build_panel(birth), "vietnamese")
    refusals = _disclosure_blob(section, DisclosureKind.REFUSAL)
    assert "royal" in refusals or "historical" in refusals
    assert "tu vi" in refusals or "natal" in refusals
    # A calendar date, never a chart: no pillars, stars or sexagenary year name.
    for banned in ("pillars", "stars", "sexagenary_year", "day_master", "palaces"):
        assert banned not in section["facts"]


def test_vietnamese_ephemeris_and_civil_day_are_disclosed_as_configured(
    fairfield_panel: dict,
) -> None:
    """The pack names no ephemeris and no statutory zone history; we must."""
    section = _section(fairfield_panel, "vietnamese")
    configured = _disclosure_blob(section, DisclosureKind.CONFIGURED_METHOD)
    assert "ephemeris" in configured
    assert "105" in configured
    alternatives = [
        alternative
        for d in section["disclosures"]
        for alternative in d.get("alternatives", [])
    ]
    assert alternatives, "configured choices must name their alternatives"
    assert section["evidence_grade"] == "configured_method"


# --------------------------------------------------------------------------
# M5: Mesopotamian (Babylonian) omen-mode section
#
# The corpus contains no personality genre, so the section's defining property
# is a refusal. These tests lock that refusal, the conservatism of the omen
# matcher, and the disclosure of the matching orb.
# --------------------------------------------------------------------------

BABYLONIAN_ID = "mesopotamian_babylonian"
EDITION_ORDER = ["Moon", "Sun", "Jupiter", "Venus", "Mercury", "Saturn", "Mars"]


def _babylonian(panel: dict) -> dict:
    return _section(panel, BABYLONIAN_ID)


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_babylonian_section_builds_for_every_fixture(birth: BirthInput) -> None:
    panel = build_panel(birth)
    assert BABYLONIAN_ID in {s["tradition_id"] for s in panel["sections"]}
    section = _babylonian(panel)
    assert not section.get("error"), section.get("error")
    assert section["facts"], "no calculation emitted"
    assert section["disclosures"], "a section hiding its conventions"
    assert section.get("reading"), "no reading emitted"
    # The calendar projection and the matching orb are product choices.
    assert section["evidence_grade"] == "configured_method"


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_babylonian_refuses_the_personality_genre(birth: BirthInput) -> None:
    """The defining refusal: the surviving corpus has no personality genre."""
    section = _babylonian(build_panel(birth))
    refusals = [
        d for d in section["disclosures"] if d["kind"] == DisclosureKind.REFUSAL.value
    ]
    genre = [d for d in refusals if "genre" in d["subject"].lower()]
    assert genre, "no refusal names the genre boundary"
    detail = genre[0]["detail"].lower()
    assert "no personality genre" in detail
    assert "cannot be turned into one" in detail
    # The other refusals the spec's refusal list requires.
    subjects = " ".join(d["subject"].lower() for d in refusals)
    for required in ("prediction", "natal synthesis", "witness blending",
                     "commentary layer"):
        assert required in subjects, f"missing refusal: {required}"


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_babylonian_reading_makes_no_personality_claim(birth: BirthInput) -> None:
    """No character claim, and no second-person address to a native at all."""
    import re

    section = _babylonian(build_panel(birth))
    reading = section["reading"]
    blob = " ".join(reading)

    # Second-person address is the tell of a personality reading.
    assert not re.search(r"\b(you|your|yours|yourself)\b", blob, re.IGNORECASE), (
        "the Babylonian section must never address a native"
    )
    assert not re.search(
        r"\b(your|the native's|his|her|their)\s+"
        r"(character|personality|temperament|disposition|traits?)\b",
        blob,
        re.IGNORECASE,
    ), "a personality claim leaked into the Babylonian reading"
    # The genre boundary is stated in the reading itself, not only in metadata.
    lowered = blob.lower()
    assert "kings" in lowered and "lands" in lowered
    assert "no protasis that takes a birth as input" in lowered
    assert "personality reading" in lowered


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_babylonian_never_asserts_a_customer_prediction(birth: BirthInput) -> None:
    """Every surfaced clause stays a historical artifact, for every fixture."""
    facts = _babylonian(build_panel(birth))["facts"]
    matching = facts["omen_matching"]
    surfaced = matching["matched"] + matching["calendar_selector_overlap"]
    for record in surfaced:
        assert record["customer_prediction"] is False, record["rule_id"]
        assert record["birth_input_eligible"] is False, record["rule_id"]
        assert record["attribution"], record["rule_id"]
        assert "not about a person" in record["genre_label"]
    judgments = facts["horoscope_judgment_clauses"]
    assert judgments["encoded_clause_count"] == 21
    assert judgments["executable_from_birth_input"] == 0
    assert judgments["with_resolved_trigger"] == 0
    for clause in judgments["clauses"]:
        assert clause["customer_prediction"] is False, clause["rule_id"]
        assert clause["attribution"], clause["rule_id"]


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_babylonian_matching_orb_is_disclosed_and_accounted(
    birth: BirthInput,
) -> None:
    """No silent default: the orb is stated and every rule lands in a bucket."""
    section = _babylonian(build_panel(birth))
    configured = [
        d
        for d in section["disclosures"]
        if d["kind"] == DisclosureKind.CONFIGURED_METHOD.value
    ]
    orb = [d for d in configured if "orb" in d["subject"].lower()]
    assert orb, "the matching orb must be disclosed"
    assert orb[0]["alternatives"], "the orb must name the widenings it refused"
    # The calendar projection and the tropical/sidereal gap are disclosed too.
    blob = _disclosure_blob(section, DisclosureKind.CONFIGURED_METHOD)
    assert "calendar" in blob and "projection" in blob
    assert "sidereal" in blob and "tropical" in blob

    matching = section["facts"]["omen_matching"]
    assert matching["configured_orb"]
    assert matching["rules_evaluated"] == 72
    accounted = (
        matching["matched_count"]
        + matching["non_executable_by_pack"]
        + matching["unevaluable_count"]
        + matching["not_matched_count"]
    )
    assert accounted == matching["rules_evaluated"], "a rule vanished silently"
    # Calendar overlap is reported, and reported as *not* a match.
    assert "Not matches" in matching["calendar_selector_overlap_note"]


def test_babylonian_fairfield_matches_no_omen(fairfield_panel: dict) -> None:
    """1996-08-13 carries no eclipse, so the corpus has nothing to say."""
    facts = _babylonian(fairfield_panel)["facts"]
    projection = facts["babylonian_date_projection"]
    assert projection["status"] == "modern_projection_not_a_historical_date"
    assert projection["month"] == "abu" and projection["day"] == 27
    assert facts["eclipse_condition"]["lunar_eclipse_in_progress"] is False
    matching = facts["omen_matching"]
    assert matching["matched_count"] == 0
    assert matching["calendar_selector_overlap"] == []
    assert "no umbral lunar eclipse" in matching["no_match_reason"]


def test_babylonian_paris_projects_a_day_fourteen_full_moon() -> None:
    """The projection must land the full moon on the middle of the month."""
    facts = _babylonian(build_panel(PARIS_1931))["facts"]
    projection = facts["babylonian_date_projection"]
    assert projection["month"] == "shabatu"
    assert projection["day"] == 14
    assert facts["lunar_condition"]["phase"] == "opposition, full moon"
    # Day 14 with no eclipse: the protases naming it are surfaced, not matched.
    matching = facts["omen_matching"]
    assert matching["matched_count"] == 0
    assert matching["calendar_selector_overlap"], "day-14 protases not surfaced"


def test_babylonian_matcher_quotes_and_attributes_every_match() -> None:
    """Drive the matcher with a sky that does satisfy encoded protases."""
    from src.engine.multitradition.babylonian import evaluate_rules

    eclipse_sky = {
        "phenomenon": "lunar_eclipse",
        "babylonian_month": "simanu",  # SAA 8 writes this month `sivan`
        "babylonian_day": 15,
        "watch": "evening",
        "sets_while_eclipsed": False,
    }
    result = evaluate_rules(eclipse_sky)
    assert result["matched_count"] >= 5, "the matching path never fires"
    for record in result["matched"]:
        assert record["apodosis_clauses"], record["rule_id"]
        assert "[" in record["attribution"], "no edition id in the citation"
        assert record["concerns"], record["rule_id"]
        assert "kings, lands" in record["genre_label"]
        assert record["customer_prediction"] is False
        assert record["birth_input_eligible"] is False
    # Rules the packs mark non-executable are never matched.
    matched_ids = {record["rule_id"] for record in result["matched"]}
    assert "babylonian.eae20.im.xiii.schematic_days_destruction" not in matched_ids
    assert "babylonian.saa8.535.rev12.evening_watch_term" not in matched_ids
    # A recensional variant is carried beside its primary, never merged into it.
    revolt = next(
        record for record in result["matched"]
        if record["rule_id"].endswith("sivan15_revolt_variant")
    )
    assert revolt["recensional_variant"]
    assert revolt["recensional_variant"] not in revolt["apodosis_clauses"]


def test_babylonian_reports_positions_in_the_editions_own_order(
    fairfield_panel: dict,
) -> None:
    """Rochberg's table order, sign and degree only - the corpus has no more."""
    facts = _babylonian(fairfield_panel)["facts"]
    positions = facts["positions_in_edition_order"]
    assert [item["body"] for item in positions] == EDITION_ORDER
    for item in positions:
        assert item["zodiac"] == "tropical"
        assert 0.0 <= item["degree_in_sign"] < 30.0
        assert set(item) == {"body", "sign", "degree_in_sign", "zodiac"}
    for absent in ("houses", "aspects", "rulerships", "sect"):
        assert absent in facts["not_recorded_by_this_corpus"]
        assert absent not in facts


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_panel_still_builds_every_section_with_babylonian_wired(
    birth: BirthInput,
) -> None:
    panel = build_panel(birth)
    failures = {
        s["tradition_id"]: s["error"] for s in panel["sections"] if s.get("error")
    }
    assert not failures, f"sections failed: {failures}"
    ids = [s["tradition_id"] for s in panel["sections"]]
    assert len(ids) == len(set(ids)), "a tradition id is wired twice"
    assert BABYLONIAN_ID in ids
    for previously_shipped in (
        "western_traditional", "indian_jyotisha", "chinese_bazi", "tibetan",
        "maya", "nahua_central_mexican",
    ):
        assert previously_shipped in ids


# --------------------------------------------------------------------------- #
# BaZi branch relations (spec item 7)
# --------------------------------------------------------------------------- #


def test_branch_relation_tables_are_structurally_complete() -> None:
    """Each of the four pair tables must cover all twelve branches exactly once."""
    from collections import Counter

    from src.engine.multitradition.bazi import (
        LIU_CHONG,
        LIU_HAI,
        LIU_HE,
        LIU_PO,
        _branches,
    )

    branches = set(_branches())
    for table in (LIU_HE, LIU_CHONG, LIU_HAI, LIU_PO):
        assert len(table) == 6
        flat = [b for pair in table for b in pair]
        assert set(flat) == branches
        assert max(Counter(flat).values()) == 1


def test_clashes_are_exactly_six_positions_apart() -> None:
    from src.engine.multitradition.bazi import LIU_CHONG, _branches

    index = {b: i for i, b in enumerate(_branches())}
    for first, second in LIU_CHONG:
        assert abs(index[first] - index[second]) == 6


def test_frames_partition_the_twelve_branches() -> None:
    from collections import Counter

    from src.engine.multitradition.bazi import SAN_HE, SAN_HUI, _branches

    branches = set(_branches())
    for frames in (SAN_HE, SAN_HUI):
        assert len(frames) == 4
        flat = [b for frame, _ in frames for b in frame]
        assert set(flat) == branches
        assert max(Counter(flat).values()) == 1


def test_fairfield_branch_relations(fairfield_panel: dict) -> None:
    """Reproduces the relations verified by hand, plus two it found."""
    relations = _section(fairfield_panel, "chinese_bazi")["facts"][
        "branch_relations"
    ]
    clashes = relations["six_clashes"]
    assert len(clashes) == 1
    assert set(clashes[0]["pillars"]) == {"year", "day"}

    frames = relations["three_harmony_frames"]
    assert any(
        f["type"] == "half" and f["reinforces"] == "Water" for f in frames
    )

    assert len(relations["six_destructions"]) == 1
    punishments = relations["punishments"]
    assert any("discourteous" in p["type"] and p["complete"] for p in punishments)


def test_branch_relations_are_reported_not_ranked(fairfield_panel: dict) -> None:
    relations = _section(fairfield_panel, "chinese_bazi")["facts"][
        "branch_relations"
    ]
    assert "school-specific" in relations["precedence_note"]


def test_branch_relations_appear_in_the_reading(fairfield_panel: dict) -> None:
    reading = " ".join(_section(fairfield_panel, "chinese_bazi")["reading"])
    assert "Branch relations present" in reading


# --------------------------------------------------------------------------- #
# Hellenistic / Latin-European split
# --------------------------------------------------------------------------- #


def test_chaldean_faces_follow_the_canonical_series() -> None:
    """The face series starts at Mars for Aries 0-10, not at Saturn."""
    from src.engine.multitradition.hellenistic import _face_ruler

    expected = [
        (0, "Mars"), (10, "Sun"), (20, "Venus"),
        (30, "Mercury"), (40, "Moon"), (50, "Saturn"), (60, "Jupiter"),
    ]
    for longitude, ruler in expected:
        assert _face_ruler(longitude) == ruler
    # Full circuit: 36 decans, each of the seven appearing in Chaldean order.
    series = [_face_ruler(d * 10) for d in range(36)]
    assert series[0] == "Mars"
    assert len(set(series)) == 7


def test_egyptian_bounds_partition_each_sign() -> None:
    from src.engine.multitradition.hellenistic import SIGNS, _bounds_for

    for sign in SIGNS:
        bounds = _bounds_for(sign)
        assert bounds, f"no bounds for {sign}"
        assert bounds[0][1] == 0.0
        assert bounds[-1][2] == 30.0
        for earlier, later in zip(bounds, bounds[1:]):
            assert earlier[2] == later[1], f"gap or overlap in {sign}"


def test_hellenistic_and_latin_are_separate_sections(fairfield_panel: dict) -> None:
    hellenistic = _section(fairfield_panel, "hellenistic")
    latin = _section(fairfield_panel, "latin_european")
    assert not hellenistic.get("error")
    assert not latin.get("error")
    # The Hellenistic section must NOT carry a numerical dignity score.
    assert "lilly_essential_dignity" not in hellenistic["facts"]
    # The Latin section must carry it.
    assert latin["facts"]["lilly_essential_dignity"]


def test_hellenistic_refuses_the_latin_scoring_table(fairfield_panel: dict) -> None:
    refusals = [
        d
        for d in _section(fairfield_panel, "hellenistic")["disclosures"]
        if d["kind"] == DisclosureKind.REFUSAL.value
    ]
    assert any("numerical dignity score" in d["subject"].lower() for d in refusals)


def test_hermetic_lots_reverse_by_sect(fairfield_panel: dict) -> None:
    """Fortune and Spirit must be reflections of each other about the ascendant."""
    facts = _section(fairfield_panel, "hellenistic")["facts"]
    lots = facts["hermetic_lots"]
    assert lots["sect_reversal_applied"] is True
    assert lots["fortune"]["sign"] == "Leo"
    assert lots["spirit"]["sign"] == "Virgo"


def test_latin_dignity_matches_third_party_where_method_agrees(
    fairfield_panel: dict,
) -> None:
    """Four of seven reproduce GERMES 2.39 exactly; divergence is documented."""
    facts = _section(fairfield_panel, "latin_european")["facts"]
    scores = {p["body"]: p["essential_score"] for p in facts["lilly_essential_dignity"]}
    assert scores["Sun"] == 8
    assert scores["Moon"] == -5
    assert scores["Mercury"] == 9
    assert scores["Venus"] == 4
    assert "third_party_comparison" in facts


def test_peregrine_fork_emits_both_readings(fairfield_panel: dict) -> None:
    facts = _section(fairfield_panel, "latin_european")["facts"]
    saturn = next(
        p for p in facts["lilly_essential_dignity"] if p["body"] == "Saturn"
    )
    assert saturn["essential_score"] == -4
    # The stacking reading reproduces the third-party value.
    assert saturn["essential_score_peregrine_stacking"] == -9


# --- Islamicate: al-Qabisi's own procedures --------------------------------


def test_al_qabisi_reproduces_his_own_worked_examples(fairfield_panel: dict) -> None:
    """The anchors. If profection or the 5/4/3/2/1 scoring drifts, these fail.

    Al-Qabisi's Ch. IV profection example and his Ch. I para 77 almuten example
    both state their own answers, so these are real reproductions of a
    10th-century author's arithmetic, not self-consistency checks.
    """
    check = _section(fairfield_panel, "islamicate_al_qabisi")["facts"][
        "worked_example_selfcheck"
    ]
    assert check["all_profection_points_match"] is True
    for point, row in check["annual_profection"].items():
        assert row["matches"] is True, point
    assert check["mustawli_fully_matches"] is True
    assert check["mustawli_dignity_scoring"]["computed_scores"]["Mars"] == 6
    assert check["mustawli_dignity_scoring"]["computed_scores"]["Sun"] == 7
    assert check["mustawli_dignity_scoring"]["computed_winner"] == "Sun"
    assert check["firdaria_total_matches_stated_75"] is True


def test_al_qabisi_aversion_signs_behold_nothing() -> None:
    """Ch. I states the 2nd, 6th, 8th and 12th behold nothing. Enforce it."""
    from src.engine.multitradition.islamicate import (
        AVERSE_SIGN_DISTANCES,
        SIGNS,
        sign_aspect,
    )

    for distance in range(12):
        a = 5.0
        b = distance * 30 + 5.0
        aspect = sign_aspect(a, b)
        if distance in AVERSE_SIGN_DISTANCES:
            assert aspect is None, f"{distance} signs apart should behold nothing"
        else:
            assert aspect is not None, f"{distance} signs apart should behold"
    assert len(SIGNS) == 12


def test_al_qabisi_tasyir_rate_is_the_mean_solar_motion() -> None:
    """His 59'08\"/day should land within an arcsecond of 360/365.2422."""
    from src.engine.multitradition.islamicate import (
        MEAN_TROPICAL_YEAR_DAYS,
        revolution_rate_degrees_per_day,
    )

    stated = revolution_rate_degrees_per_day()
    modern = 360.0 / MEAN_TROPICAL_YEAR_DAYS
    assert abs(stated - modern) * 3600.0 < 1.0


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_al_qabisi_refuses_a_lifespan_and_settles_a_hyleg(
    birth: BirthInput,
) -> None:
    """Hyleg/kadkhudah structure is emitted; the lifespan it exists for is not."""
    section = _section(build_panel(birth), "islamicate_al_qabisi")
    facts = section["facts"]
    settled = facts["hyleg_settled"]
    assert settled["hyleg"] in {
        "Sun", "Moon", "Ascendant", "Lot of Fortune", "Prenatal syzygy",
    }
    # Every ledger entry with a position must have had the aspect gate applied.
    for entry in facts["hyleg_candidate_ledger"]:
        if entry.get("longitude") is not None:
            assert "passes_aspect_gate" in entry
    refusals = _disclosure_blob(section, DisclosureKind.REFUSAL)
    assert "lifespan" in refusals
    blob = json.dumps(facts).lower()
    for forbidden in ("years_of_life", "death_year", "will_die"):
        assert forbidden not in blob
    assert not section.get("reading")


# --- refusal taxonomy and maturity axes (external review P1) ---------------


def test_every_refusal_carries_a_specific_category(fairfield_panel: dict) -> None:
    """One [REFUSES] label concealed nine different situations. No more:
    every refusal must name which kind it is, from the closed vocabulary."""
    from src.engine.multitradition.types import REFUSAL_CATEGORIES

    unclassified = []
    for section in fairfield_panel["sections"]:
        for d in section.get("disclosures", []):
            if d["kind"] != "refusal":
                continue
            category = d.get("category")
            if category not in REFUSAL_CATEGORIES:
                unclassified.append((section["tradition_id"], d["subject"]))
    assert not unclassified, unclassified


def test_every_section_carries_a_maturity_assessment(fairfield_panel: dict) -> None:
    """Multi-axis maturity replaces the single label (review finding 2)."""
    axes = (
        "category", "source_readiness", "computational_readiness",
        "validation_coverage", "interpretation_readiness",
        "publication_readiness",
    )
    for section in fairfield_panel["sections"]:
        maturity = section.get("maturity")
        assert maturity, f"no maturity assessment: {section['tradition_id']}"
        for axis in axes:
            assert maturity.get(axis), (section["tradition_id"], axis)


def test_coverage_summary_is_generated_not_asserted(fairfield_panel: dict) -> None:
    """The headline is derived from the maturity table, so it cannot claim
    fifteen comparable traditions while five of them are calendars."""
    summary = fairfield_panel.get("coverage_summary", "")
    assert "calendar" in summary
    assert "natal report" in summary
    assert "15 traditions" not in summary
