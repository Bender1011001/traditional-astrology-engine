import copy
import re

import pytest

from src.services.reading_composer import (
    compose_customer_reading,
    compose_deterministic_draft,
)
from src.services.reading_contract import ReadingContractError
from src.services.reading_evidence import CUSTOMER_TOPICS, build_reading_evidence
from src.services.judgment_planner import build_judgment_plan


@pytest.fixture()
def chart_data():
    return {
        "meta": {
            "chart": {
                "name": "Native",
                "date": "1996-08-13",
                "time": "07:18",
                "city": "Fairfield",
                "state": "CA",
                "house_system": {"label": "Whole Sign"},
                "zodiac_system": {"label": "Tropical"},
            }
        },
        "analysis": {
            "sect": {"type": "DAY", "sun_altitude_deg": 9.87},
            "planets_forensic": [
                {
                    "name": name,
                    "longitude_fmt": {"string": f"{sign} 10°00′"},
                    "sign": sign,
                    "house": house,
                    "retrograde": False,
                    "solar_status": "FREE" if name != "Sun" else "SUN",
                    "dignities": {
                        "score_breakdown": {
                            dignity: points,
                        }
                    },
                }
                for name, sign, house, dignity, points in (
                    ("Sun", "Leo", 12, "domicile", 5),
                    ("Moon", "Leo", 12, "face", 1),
                    ("Mercury", "Virgo", 1, "exaltation", 4),
                    ("Venus", "Cancer", 11, "triplicity", 3),
                    ("Mars", "Cancer", 11, "fall", -4),
                    ("Jupiter", "Capricorn", 5, "fall", -4),
                    ("Saturn", "Aries", 8, "fall", -4),
                )
            ],
            "dignity": {
                "almuten": {"winner": "Mercury", "score": 27, "breakdown": {}}
            },
            "aspects": [
                {
                    "planet_a": "Mercury",
                    "planet_b": "Mars",
                    "type": "Sextile",
                    "orb": 4.66,
                    "is_applying": False,
                }
            ],
            "aspects_shadow": [
                {"planet_a": "Uranus", "planet_b": "Pluto", "type": "Sextile"}
            ],
            "teams": {
                "receptions": [
                    {
                        "a_in_b": {
                            "host": "Jupiter",
                            "guest": "Mars",
                            "dignities": ["Exaltation"],
                            "is_operative": True,
                        },
                        "b_in_a": {
                            "host": "Mars",
                            "guest": "Jupiter",
                            "dignities": ["Exaltation"],
                            "is_operative": True,
                        },
                    }
                ]
            },
            "enhanced_profections": {
                "age": 29,
                "annual_sign": "Aquarius",
                "lord_of_year": "Saturn",
            },
            "triplicity_periods": {
                "sect": "Day",
                "sect_light": "Sun",
                "sect_light_sign": "Leo",
                "element": "Fire",
                "rulers": {
                    "first": "Sun",
                    "second": "Jupiter",
                    "participant": "Saturn",
                },
                "temporal_roles": {
                    "first": "beginning of life/fortune testimony",
                    "second": "later outcome of life/fortune testimony",
                    "participant": "supporting testimony; no fixed final life third",
                },
                "method": "Dorothean sect-light triplicity judgment (first, second, and participating rulers; no fixed age thirds)",
            },
            "fate": {
                "firdaria": {
                    "Major Period": "Mercury",
                    "Sub Period": "Venus",
                    "Source Rule ID": "al_biruni_firdaria_seven_planet_core",
                },
                "zodiacal_releasing": {
                    "Spirit": {"current": {"Level 1": "Scorpio"}},
                    "Fortune": {"current": {"Level 1": "Virgo"}},
                },
            },
            "temperament": {
                "primary_temperament": "Melancholic (Cold/Dry)",
                "net_balance": {"Hot_vs_Cold": -4, "Moist_vs_Dry": -2},
            },
            "topical": {
                "twelve_topoi": [
                    {
                        "house": 10,
                        "sign": "Gemini",
                        "ruler": "Mercury",
                        "ruler_condition": {
                            "sign": "Virgo",
                            "house": 1,
                            "condition_band": "well-supported",
                            "reasons": ["essential dignity strong (+9)", "angular (house 1)"],
                        },
                        "ruler_in_aversion_to_its_house": False,
                        "occupants": [],
                    }
                ]
            },
            "doctrinal_disagreements": {"chart_specific": []},
            "medical": {"unsafe": "surgery timing"},
            "vitality": {"unsafe": "length of life"},
            "remediation": {"unsafe": "prescription"},
        },
    }


def test_evidence_packet_excludes_protected_layers_and_outer_planets(chart_data):
    evidence = build_reading_evidence(chart_data)
    combined = " ".join(item.fact + " " + item.provenance for item in evidence)
    assert "medical" not in combined.lower()
    assert "vitality" not in combined.lower()
    assert "remediation" not in combined.lower()
    assert "uranus" not in combined.lower()
    assert "pluto" not in combined.lower()
    sect = next(item for item in evidence if item.category == "foundation")
    almutens = [item for item in evidence if item.category == "chart_ruler"]
    career = next(item for item in evidence if item.category == "topical")
    timing = [item for item in evidence if item.category == "timing"]
    assert sect.source_rule_id == "sect_malefic_moderation"
    # Was "text_verified", which is the DEFAULT applied when a registry rule
    # carries no verification field at all - it reads like a verification but
    # means "unrecorded". Tetrabiblos I.7 has since been read in the Boll-Boer
    # Greek, so this rule now carries a real, stronger status.
    assert sect.verification_status == "greek_text_read_directly"
    assert almutens == []
    assert "action, rank, reputation, and career" in career.fact
    assert "essential dignity strong (+9)" in career.fact
    assert career.source_rule_id == "whole_sign_topical_chain"
    assert career.verification_status == "translation_inspected_partial"
    annual = next(item for item in timing if item.source_rule_id == "annual_profection_sign_rotation")
    releasing = next(item for item in timing if item.source_rule_id == "valens_zodiacal_releasing")
    firdaria = next(
        item
        for item in timing
        if item.source_rule_id == "al_biruni_firdaria_seven_planet_core"
    )
    # Both upgraded this session: annual profection read from Paulus (Boer
    # pp. 82-95) and releasing read from Valens IV.4-7 (Kroll pp. 160-189).
    assert annual.verification_status == "greek_text_read_directly"
    assert releasing.verification_status == "greek_text_read_directly"
    assert firdaria.verification_status == "translation_and_facing_text_inspected"
    aspect = next(item for item in evidence if item.category == "aspect")
    # Was "translation_inspected_partial" while ptolemaic_aspects cited Ashmand
    # 1822 - which is Ashmand's English of PROCLUS' PARAPHRASE, i.e. Ptolemy at
    # two removes. Tetrabiblos I.14 has since been read in the Boll-Boer Greek
    # directly, so the provenance genuinely improved and the assertion tracks it.
    assert aspect.verification_status == "greek_text_read_directly"
    joy = next(item for item in evidence if item.category == "planetary_joy")
    assert joy.details == {"name": "Mercury", "house": 1}
    assert joy.source_rule_id == "paulus_planetary_joys"
    # Upgraded this session - the joys were read in Boer's Greek (pp. 53-95).
    assert joy.verification_status == "greek_text_read_directly"


def test_customer_topic_catalog_covers_all_twelve_places():
    assert set(CUSTOMER_TOPICS) == set(range(1, 13))


def test_longevity_branches_publish_exact_years_and_failed_rival(chart_data):
    chart_data["analysis"]["vitality"] = {
        "hyleg": {"type": "Angle", "name": "Ascendant", "longitude": 151.5},
        "alcocoden_methods": {
            "valens_term": {
                "name": "Mercury",
                "details": {"aspect": "Conjunction (Whole Sign)", "aspect_mode": "whole_sign"},
            },
            "bonatti_points": {
                "name": "Venus",
                "details": {"aspect": "Sextile", "aspect_mode": "degree_orb"},
            },
        },
        "years_capacity": {
            "valens_term": {
                "hyleg": "Ascendant",
                "alcocoden": "Mercury",
                "base_years_type": "Major",
                "base_years": 76,
                "total_years": 76,
                "breakdown": ["Base: Major Years of Mercury (76) due to House 1 and dignity 9"],
            },
            "bonatti_points": {
                "hyleg": "Ascendant",
                "alcocoden": "Venus",
                "base_years_type": "Mean",
                "base_years": 45,
                "total_years": 17.7,
                "invalid_under_sanity": True,
                "breakdown": [
                    "Base: Mean Years of Venus (45) due to House 11 and dignity 5",
                    "Subtracted 18.4 (Mars Conjunction)",
                    "Added 7.9 (Jupiter Opposition)",
                    "Subtracted 16.8 (Saturn Square)",
                ],
            },
        },
        "anareta": {"name": None, "reason": "No qualifying static Anareta."},
        "anaretic_windows": {
            "candidates": [
                {
                    "promittor": "Saturn",
                    "aspect": "Opposition",
                    "years": 43.68,
                    "date_offset": "43y 8m",
                }
            ]
        },
    }

    report, packet = compose_customer_reading(chart_data, llm_request=None)
    longevity = [item for item in packet["evidence"] if item["category"] == "longevity"]

    assert len(longevity) == 2
    assert longevity[0]["source_rule_id"] == "lilly_hyleg_alcocoden_and_years"
    assert "Branch One — Mercury Gives 76 Years" in report
    assert "a lifetime of 76 years" in report
    assert "Venus Produces a Failed Result" in report
    assert "resulting figure is 17.70 years" in report
    assert "Saturn in opposition to the Hyleg at age 43.68" in report


def test_longevity_prose_is_derived_from_each_customers_branches(chart_data):
    alternate = copy.deepcopy(chart_data)
    alternate["analysis"]["vitality"] = {
        "hyleg": {"type": "Planet", "name": "Sun", "longitude": 42.25},
        "alcocoden_methods": {
            "valens_term": {
                "name": "Jupiter",
                "details": {"aspect": "Trine", "aspect_mode": "degree_orb"},
            },
            "bonatti_points": {
                "name": "Saturn",
                "details": {"aspect": "Sextile", "aspect_mode": "degree_orb"},
            },
        },
        "years_capacity": {
            "valens_term": {
                "hyleg": "Sun",
                "alcocoden": "Jupiter",
                "base_years_type": "Major",
                "base_years": 79,
                "total_years": 63.5,
                "breakdown": ["Base: Major Years of Jupiter (79)", "Subtracted 15.5"],
            },
            "bonatti_points": {
                "hyleg": "Sun",
                "alcocoden": "Saturn",
                "base_years_type": "Mean",
                "base_years": 43.5,
                "total_years": 12.25,
                "invalid_under_sanity": True,
                "breakdown": ["Base: Mean Years of Saturn (43.5)", "Subtracted 31.25"],
            },
        },
        "anareta": {"name": "Mars", "reason": "Mars casts the configured square."},
        "anaretic_windows": {
            "candidates": [
                {
                    "promittor": "Mars",
                    "aspect": "Square",
                    "years": 51.2,
                    "date_offset": "51y 2m",
                }
            ]
        },
    }

    report, _packet = compose_customer_reading(alternate, llm_request=None)

    assert "Branch One — Jupiter Gives 63.5 Years" in report
    assert "a lifetime of 63.5 years" in report
    assert "Branch Two — Saturn Produces a Failed Result" in report
    assert "Mars in square to the Hyleg at age 51.20" in report
    assert "Mercury Gives 76 Years" not in report
    assert "Venus Produces a Failed Result" not in report


def test_judgment_planner_ranks_the_actual_helm_not_mercury_by_default():
    packet = {
        "subject": "Alternate Native",
        "evidence": [
            {
                "id": "E1",
                "category": "foundation",
                "fact": "The chart is NIGHT.",
                "details": {},
            },
            {
                "id": "E2",
                "category": "topical",
                "details": {"house": 1, "ruler": "Mars"},
            },
            {
                "id": "E3",
                "category": "topical",
                "details": {"house": 10, "ruler": "Saturn"},
            },
            {
                "id": "E4",
                "category": "planetary_condition",
                "details": {
                    "name": "Mars",
                    "house": 1,
                    "dignities": "domicile",
                    "retrograde": False,
                    "maltreatments": [],
                },
            },
            {
                "id": "E5",
                "category": "planetary_condition",
                "details": {
                    "name": "Mercury",
                    "house": 6,
                    "dignities": "no recorded essential dignity",
                    "retrograde": False,
                    "maltreatments": [],
                },
            },
            {
                "id": "E6",
                "category": "planetary_condition",
                "details": {
                    "name": "Saturn",
                    "house": 10,
                    "dignities": "triplicity",
                    "retrograde": False,
                    "maltreatments": [],
                },
            },
        ],
    }

    plan = build_judgment_plan(packet)

    assert plan.sect == "Night"
    assert plan.helm_ruler == "Mars"
    assert plan.public_ruler == "Saturn"
    assert plan.strongest_planet is not None
    assert plan.strongest_planet.name == "Mars"
    assert plan.ranked_planets[-1].name == "Mercury"


def test_dorothean_triplicity_uses_first_second_and_participant_without_fixed_thirds(chart_data):
    evidence = build_reading_evidence(chart_data)
    item = next(value for value in evidence if value.category == "life_chapters")
    assert item.source_rule_id == "dorotheus_sect_light_triplicity_fortune"
    assert item.details["first"] == "Sun"
    assert item.details["second"] == "Jupiter"
    assert item.details["participant"] == "Saturn"
    assert "final third" in item.interpretive_limit
    report, _ = compose_deterministic_draft(chart_data)
    assert "Sect-Light Fortune and the Course of Life" in report
    assert "does not promise an easy beginning" in report
    assert "improvement does not remain secure" in report
    assert "does not govern a fixed late-life third" in report
    assert "The middle chapter is governed" not in report
    later = next(
        value
        for value in evidence
        if value.source_rule_id == "ibn_ezra_triplicity_life_thirds"
    )
    assert later.details == {
        "method": "ibn_ezra_relative_life_thirds",
        "sect": "Day",
        "first": "Sun",
        "middle": "Jupiter",
        "last": "Saturn",
    }
    assert "Ibn Ezra explicitly divides" in report
    assert "Their exact boundaries are not invented here" in report


def test_comprehensive_mode_fails_closed_on_missing_layers(chart_data):
    with pytest.raises(ReadingContractError, match="missing_evidence_coverage"):
        compose_customer_reading(
            chart_data,
            llm_request=None,
            require_comprehensive=True,
        )


def test_deterministic_report_is_complete_and_cited(chart_data):
    report, packet = compose_customer_reading(chart_data, llm_request=None)
    assert len(report.split()) >= 900
    assert report.count("# Your Nativity at a Glance") == 1
    assert report.count("# Method and Limits") == 1
    assert "[E1]" in report
    assert packet["evidence"]
    assert "Saturn is the more moderated malefic" in report
    assert "does not make Saturn benefic" in report
    assert "Paulus: The Planets in Their Places" in report
    assert "favorable nocturnal branch does not belong to your chart" in report
    assert "advancement is not simply handed over by family or authority" in report
    assert "The Direct Judgment" in report
    assert "The Blunt Conclusion" in report
    assert "The Life as a Whole" in report
    # The ranked forecast covers one full 12-year profection cycle, so its
    # heading is derived from the chart's own years rather than hard-coded.
    forecast_heading = re.search(r"## Ranked Forecast: (\d{4})-(\d{4})", report)
    assert forecast_heading, "ranked forecast section is missing"
    first_year, last_year = int(forecast_heading.group(1)), int(forecast_heading.group(2))
    assert last_year - first_year == 12, (
        f"ranked forecast should span one 12-year profection cycle, got {first_year}-{last_year}"
    )
    # Long-range calendars must extend past the detailed cycle.
    assert "The Full Profection Calendar" in report
    assert "it does not remain abstract" not in report
    assert "Because its ruler is lodged in house" not in report
    assert "The ruler sees its own place" not in report


def test_paulus_place_rules_preserve_harsh_conditions_and_exceptions(chart_data):
    chart_data["analysis"]["aspects"].extend(
        [
            {
                "planet_a": "Moon",
                "planet_b": "Saturn",
                "type": "Trine",
                "orb": 5.0,
                "is_applying": False,
            },
            {
                "planet_a": "Venus",
                "planet_b": "Mars",
                "type": "Conjunction",
                "orb": 2.0,
                "is_applying": True,
            },
            {
                "planet_a": "Venus",
                "planet_b": "Saturn",
                "type": "Square",
                "orb": 3.0,
                "is_applying": False,
            },
        ]
    )

    report, packet = compose_customer_reading(chart_data, llm_request=None)
    place_items = [
        item for item in packet["evidence"] if item["category"] == "planet_in_place_source"
    ]

    assert len(place_items) == 7
    assert all(
        item["source_rule_id"] == "paulus_planets_in_places_chart_rules"
        for item in place_items
    )
    assert "The favorable nocturnal branch does not belong to your chart" in report
    assert "that exception is active" in report
    assert "Paulus's harsher conditional branch is active" in report
    assert "does not remove the malefic regard" in report


def test_firmicus_antiscia_major_configurations_are_published(chart_data):
    chart_data["analysis"]["antiscia_configurations"] = [
        {
            "planet_1": "Sun",
            "planet_2": "Jupiter",
            "antiscion_of": "Sun",
            "antiscion_longitude": 38.9,
            "aspect": "Trine",
            "aspect_angle": 120.0,
            "orb": 0.395,
            "orb_limit": 1.0,
            "source_rule_id": "firmicus_antiscia_major_configurations",
        },
        {
            "planet_1": "Mercury",
            "planet_2": "Mars",
            "antiscion_of": "Mercury",
            "antiscion_longitude": 12.82,
            "aspect": "Square",
            "aspect_angle": 90.0,
            "orb": 0.298,
            "orb_limit": 1.0,
            "source_rule_id": "firmicus_antiscia_major_configurations",
        },
    ]

    report, packet = compose_customer_reading(chart_data, llm_request=None)
    antiscia = [
        item for item in packet["evidence"] if item["category"] == "antiscia_configuration"
    ]

    assert len(antiscia) == 1
    assert antiscia[0]["verification_status"] == "translation_and_table_inspected"
    assert "Firmicus judges major aspects through reflected degrees" in report
    assert "The Sun-Jupiter trine connects authority" in report
    assert "The Mercury-Mars square corrects their bodily sextile" in report


def test_ptolemaic_doryphory_uses_sign_rule_and_rejects_royal_overclaim(chart_data):
    chart_data["analysis"]["advanced_mechanics"] = {
        "doryphory": [
            {
                "luminary": "Moon",
                "guard": "Mercury",
                "type": "Bodily/Occidental",
                "phase": "occidental",
                "placement_relation": "next_following_sign",
                "guard_house_wsh": 1,
                "guard_angular_wsh": True,
                "delta_deg": 33.936,
                "source_rule_id": "ptolemy_doryphory_rank",
            }
        ]
    }

    report, packet = compose_customer_reading(chart_data, llm_request=None)
    doryphory = [item for item in packet["evidence"] if item["category"] == "doryphory"]

    assert len(doryphory) == 1
    assert doryphory[0]["verification_status"] == "translation_inspected"
    assert "prior fixed 30-degree shortcut was wrong" in report
    assert "Mercury is the Moon's spear-bearer" in report
    assert "royal or sovereign branch is not present" in report
    assert "leading role in ordinary" in report


def test_doryphory_prose_uses_the_actual_guard_and_luminary(chart_data):
    alternate = copy.deepcopy(chart_data)
    alternate["analysis"]["advanced_mechanics"] = {
        "doryphory": [
            {
                "luminary": "Sun",
                "guard": "Venus",
                "type": "Bodily/Oriental",
                "phase": "oriental",
                "placement_relation": "same_sign",
                "guard_house_wsh": 10,
                "guard_angular_wsh": True,
                "delta_deg": 5.25,
                "source_rule_id": "ptolemy_doryphory_rank",
            }
        ]
    }
    venus = next(
        planet
        for planet in alternate["analysis"]["planets_forensic"]
        if planet["name"] == "Venus"
    )
    venus["house"] = 10

    report, _packet = compose_customer_reading(alternate, llm_request=None)

    assert "Venus is the Sun's spear-bearer" in report
    assert "The guard is angular, so the attendance has public force" in report
    assert "strong Mercury serves the twelfth-place Moon" not in report


def test_picatrix_mansion_is_not_converted_into_natal_personality(chart_data):
    chart_data["analysis"]["supplemental"] = {
        "lunar_mansion": {
            "mansion_id": 11,
            "name": "Al-Zubrah",
            "inspected_source_name_variant": "Azobra",
            "calculation_method": "configured_equal_tropical_28_from_aries",
            "source_rule_id": "picatrix_lunar_mansions_electional_scope",
            "usage_scope": "electional_talismanic_only",
            "natal_delineation_supported": False,
            "assignment_robust_to_inspected_boundary_variants": True,
        }
    }

    report, packet = compose_customer_reading(chart_data, llm_request=None)
    mansion = [
        item for item in packet["evidence"] if item["category"] == "lunar_mansion_scope"
    ]

    assert len(mansion) == 1
    assert mansion[0]["verification_status"] == "translation_inspected_partial_boundaries"
    assert "What the Source Does and Does Not Say" in report
    assert "no honest natal prediction is extracted" in report
    assert "invented mansion personality keywords" in report


def test_lunar_mansion_scope_does_not_leak_the_fairfield_moon(chart_data):
    alternate = copy.deepcopy(chart_data)
    moon = next(
        planet
        for planet in alternate["analysis"]["planets_forensic"]
        if planet["name"] == "Moon"
    )
    moon["sign"] = "Sagittarius"
    moon["longitude_fmt"] = {"string": "Sagittarius 03°15′"}
    alternate["analysis"]["supplemental"] = {
        "lunar_mansion": {
            "mansion_id": 20,
            "name": "Al-Na'am",
            "inspected_source_name_variant": "Nahaym",
            "calculation_method": "configured_equal_tropical_28_from_aries",
            "source_rule_id": "picatrix_lunar_mansions_electional_scope",
            "usage_scope": "electional_talismanic_only",
            "natal_delineation_supported": False,
            "assignment_robust_to_inspected_boundary_variants": True,
        }
    }

    report, _packet = compose_customer_reading(alternate, llm_request=None)

    assert "Moon at Sagittarius 03°15′ calculates to tropical mansion 20" in report
    assert "Leo 13°14′ remains" not in report


def test_paulus_seven_lots_preserve_formulas_and_severe_meanings(chart_data):
    chart_data["analysis"]["fate"] = {
        **chart_data["analysis"]["fate"],
        "hermetic_lots": {
            name: {
                "longitude_fmt": {"string": f"{sign} 10°00′"},
                "sign": sign,
                "house": house,
                "ruler": ruler,
                "status": status,
            }
            for name, sign, house, ruler, status in (
                ("Fortune", "Leo", 12, "Sun", "Clear"),
                ("Spirit", "Virgo", 1, "Mercury", "Clear"),
                ("Eros", "Gemini", 10, "Mercury", "Clear"),
                ("Necessity", "Leo", 12, "Sun", "Clear"),
                ("Courage", "Libra", 2, "Venus", "Lot Maltreated / Ruler Maltreated"),
                ("Victory", "Capricorn", 5, "Saturn", "Lot Maltreated"),
                ("Nemesis", "Capricorn", 5, "Saturn", "Lot Maltreated"),
            )
        },
    }

    report, packet = compose_customer_reading(chart_data, llm_request=None)
    lots = [item for item in packet["evidence"] if item["category"] == "lot"]

    assert len(lots) == 7
    assert all(item["source_rule_id"] == "paulus_seven_hermetic_lots" for item in lots)
    assert all(item["verification_status"] == "translation_and_facing_pages_inspected" for item in lots)
    assert "constraint, submission, struggle, war, enmity, hatred, condemnation, and restriction" in report
    assert "boldness, treachery, might, and villainy" in report
    assert "impotence, exile, destruction, grief, and the quality of death" in report
    assert "The recorded maltreatment makes reversal, loss, conflict" in report


def test_lot_judgments_follow_each_lots_actual_house_and_ruler(chart_data):
    alternate = copy.deepcopy(chart_data)
    alternate["analysis"]["fate"] = {
        **alternate["analysis"]["fate"],
        "hermetic_lots": {
            "Fortune": {
                "longitude_fmt": {"string": "Scorpio 04°00′"},
                "sign": "Scorpio",
                "house": 3,
                "ruler": "Mars",
                "status": "Clear",
            },
            "Spirit": {
                "longitude_fmt": {"string": "Taurus 12°00′"},
                "sign": "Taurus",
                "house": 9,
                "ruler": "Venus",
                "status": "Clear",
            },
        },
    }

    report, _packet = compose_customer_reading(alternate, llm_request=None)

    assert "Lot of Fortune is at Scorpio 04°00′ in whole-sign house 3, ruled by Mars" in report
    assert "In learning, messages, siblings, and local movement" in report
    assert "circumstance, bodily life, possessions, and public allotment" in report
    assert "Lot of Spirit is at Taurus 12°00′ in whole-sign house 9, ruled by Venus" in report
    assert "In religion, study, divination, and long journeys" in report
    assert "choice, intention, command, and the work deliberately undertaken" in report
    assert "Fortune in the twelfth and ruled by the strong twelfth-place Sun" not in report


def test_editor_can_return_the_bounded_draft(chart_data):
    def echo_draft(**kwargs):
        content = kwargs["messages"][1]["content"]
        return content.split("DETERMINISTIC DRAFT:\n", 1)[1]

    report, _packet = compose_customer_reading(chart_data, llm_request=echo_draft)
    assert "# The Present Chapter" in report


def test_editor_cannot_invent_evidence_identifier(chart_data):
    draft, _packet = compose_deterministic_draft(chart_data)

    def invent(**_kwargs):
        return draft + "\n\nAn unsupported claim. [E999]"

    with pytest.raises(ReadingContractError, match="unknown_evidence"):
        compose_customer_reading(chart_data, llm_request=invent)


def test_editor_cannot_direct_the_reader_about_their_health(chart_data):
    """The editor may relay a source's bodily doctrine; it may not give direction.

    This previously asserted on `medical_or_surgical`, a filter that also blocked
    Valens IV.4 and Ptolemy III.5 on the body. Relaying what a source says is
    allowed; telling the reader to act on their health in our voice is not.
    """
    draft, _packet = compose_deterministic_draft(chart_data)

    def unsafe(**_kwargs):
        return draft + "\n\nYou must arrange medical care while the Moon is in Leo. [E1]"

    with pytest.raises(ReadingContractError, match="protected_directive"):
        compose_customer_reading(chart_data, llm_request=unsafe)


def test_degree_quality_delineation_preserves_lillys_significator_scope(chart_data):
    def card(sign, degree, quality, *, pitted=False, azimene=False):
        return {
            "sign": sign,
            "degree_one_based": degree,
            "tradition": "lilly_1647",
            "masculine_feminine": "F",
            "light_dark_smoky_void": quality,
            "pitted": pitted,
            "azimene": azimene,
            "increasing_fortune": False,
            "data_available": True,
        }

    chart_data["analysis"]["angles"] = {
        "Ascendant": {
            "sign": "Virgo",
            "longitude_fmt": {"string": "Virgo 01°30′"},
        },
        "Midheaven": {
            "sign": "Taurus",
            "house_wsh": 9,
            "longitude_fmt": {"string": "Taurus 27°02′"},
        },
    }
    chart_data["analysis"]["degree_qualities"] = {
        "Ascendant": card("Virgo", 2, "dark"),
        "Moon": card("Leo", 14, "smoky"),
        "Mercury": card("Virgo", 18, "smoky"),
        "Sun": card("Leo", 22, "void", pitted=True),
        "Mars": card("Cancer", 13, "dark", azimene=True),
        "Jupiter": card("Capricorn", 9, "light"),
        "Lot of Fortune": card("Leo", 24, "void"),
    }

    report, _packet = compose_customer_reading(chart_data, llm_request=None)

    assert "Ascendant is one of the significators" in report
    assert "Moon is one of the significators" in report
    assert "Sun carries a pitted table flag" in report
    assert "Mars carries an azimene table flag outside Lilly's stated" in report
    assert "applying its bodily language directly to you would exceed the printed rule" in report


def test_no_alcocoden_renders_honest_absence_not_unknown_placeholder():
    """Regression: charts where a longevity method finds no Alcocoden must say so.

    The Jul 28 customer chart rendered '### Branch One — Unknown Gives 0 Years'
    and 'makes Unknown Alcocoden' — a raw fallback surfaced as customer prose.
    """
    from src.services.reading_composer import _longevity_paragraphs

    items = [
        {
            "id": "E44",
            "details": {
                "hyleg": {"name": "Ascendant", "longitude": 220.59},
                "strict_method": {"name": None, "details": {}},
                "points_method": {"name": "points", "details": {"aspect": "Square"}},
            },
        },
        {
            "id": "E45",
            "details": {
                "strict_capacity": {
                    "alcocoden": None,
                    "total_years": 0,
                    "breakdown": ["No Alcocoden found (Valens term method)."],
                    "invalid_under_sanity": True,
                },
                "points_capacity": {
                    "alcocoden": "Sun",
                    "base_years": 19,
                    "base_years_type": "minor",
                    "total_years": 19.0,
                    "breakdown": ["Base: Minor Years of Sun (19)"],
                    "invalid_under_sanity": True,
                },
                "anareta": {"reason": "none found"},
                "anaretic_windows": {"candidates": []},
            },
        },
    ]
    text = " | ".join(_longevity_paragraphs(items))
    assert "Unknown" not in text
    assert "Finds No Giver of Years" in text
    assert "0 Years" not in text
    assert "finds no qualifying Alcocoden" in text
    # The found branch still renders normally
    assert "Sun" in text and "19" in text
