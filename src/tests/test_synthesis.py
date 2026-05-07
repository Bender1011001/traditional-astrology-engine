"""Tests for synthesis.py — ReportSynthesizer."""

from src.engine.synthesis import ReportSynthesizer


def _build_minimal_report():
    """Build a minimal valid report dict for synthesis."""
    return {
        "soul_guardian": {
            "almuten": "Jupiter",
            "job_description": "Expansion and wisdom",
        },
        "vitality": {
            "hyleg": {"name": "Sun", "type": "Planet"},
            "alcocoden": {"name": "Jupiter", "aspect": "Trine"},
            "years_capacity": {
                "default": {
                    "base_years": 79,
                    "base_years_type": "Major",
                    "alcocoden": "Jupiter",
                    "vitality_rating": "Strong",
                }
            },
            "anareta": {"name": "Mars", "reason": "Square to Hyleg"},
            "vitality_rating": "Strong",
        },
        "summary": {
            "sect": "Day",
            "temperament": {
                "primary_temperament": "Sanguine",
                "scores": {"Hot": 4, "Cold": 2, "Moist": 3, "Dry": 1},
                "net_balance": {"Hot_vs_Cold": 2, "Moist_vs_Dry": 2},
            },
            "constructive_team": ["Jupiter", "Sun"],
            "destructive_team": ["Mars"],
            "mutual_receptions": [],
            "universal_events": [],
            "universal_causation_audit": [],
        },
        "planets": [
            {
                "name": "Sun",
                "sign": "Leo",
                "longitude": 126.5,
                "dignities": {
                    "total_score": 9,
                    "score_breakdown": {
                        "domicile": 5,
                        "exaltation": 0,
                        "triplicity": 3,
                        "term": 0,
                        "face": 1,
                        "monomoiria": 0,
                        "detriment": 0,
                        "fall": 0,
                    },
                },
                "solar_status": "SUN",
                "maltreatments": [],
                "retrograde": False,
                "speed": 1.0,
                "impacts": [],
                "delineation": "The Sun in Leo shines with sovereign authority.",
            },
            {
                "name": "Moon",
                "sign": "Cancer",
                "longitude": 100.0,
                "dignities": {
                    "total_score": 5,
                    "score_breakdown": {
                        "domicile": 5,
                        "exaltation": 0,
                        "triplicity": 0,
                        "term": 0,
                        "face": 0,
                        "monomoiria": 0,
                        "detriment": 0,
                        "fall": 0,
                    },
                },
                "solar_status": "FREE",
                "maltreatments": [],
                "retrograde": False,
                "speed": 13.0,
                "impacts": [],
                "delineation": "The Moon in Cancer is in domicile.",
            },
        ],
        "houses": {str(i): (i - 1) * 30.0 for i in range(1, 13)},
        "aspects": [
            {
                "planet_a": "Sun",
                "planet_b": "Moon",
                "type": "Sextile",
                "orb": 3.5,
                "is_applying": True,
                "text": "Harmonious luminaries.",
            },
        ],
        "fixed_stars": [
            {
                "star_name": "Regulus",
                "planet_name": "Sun",
                "message": "Royal star conjunct Sun.",
                "mythology": "Heart of the Lion",
            },
        ],
        "forensic_lots": {
            "Lot of Fortune": {
                "status": "Clear",
                "sign": "Virgo",
                "ruler": "Mercury",
                "data": {"longitude": 155.0, "house": 6, "sign": "Virgo"},
            },
        },
        "profections": {"lord_of_year": "Jupiter", "annual_sign": "Sagittarius"},
        "firdaria": {
            "Major Period": "Jupiter",
            "Sub Period": "Venus",
            "Sub Start": "2024-01-01",
            "Sub End": "2025-06-01",
        },
    }


# ─── synthesize (full pipeline) ─────────────────────────────────────────────


def test_synthesize_returns_string():
    report = _build_minimal_report()
    result = ReportSynthesizer.synthesize(report)
    assert isinstance(result, str)
    assert len(result) > 100


def test_synthesize_contains_all_sections():
    report = _build_minimal_report()
    result = ReportSynthesizer.synthesize(report)
    assert "EXECUTIVE SUMMARY" in result
    assert "SECT" in result
    assert "SOVEREIGN POWER" in result
    assert "PLANETARY PROTOCOLS" in result
    assert "HOUSE CUSPS" in result
    assert "ASPECT ANALYSIS" in result
    assert "FATE TIMELINE" in result
    assert "FIXED STAR" in result
    assert "FORENSIC AUDIT" in result
    assert "UNIVERSAL OVERRIDES" in result


# ─── _generate_executive_summary ─────────────────────────────────────────────


def test_executive_summary_almuten():
    report = _build_minimal_report()
    result = ReportSynthesizer._generate_executive_summary(report)
    assert "Jupiter" in result
    assert "Almuten" in result


def test_executive_summary_vitality():
    report = _build_minimal_report()
    result = ReportSynthesizer._generate_executive_summary(report)
    assert "Hyleg" in result
    assert "Sun" in result
    assert "Vitality Rating" in result
    assert "Historical Use Only" in result


def test_executive_summary_anareta():
    report = _build_minimal_report()
    result = ReportSynthesizer._generate_executive_summary(report)
    assert "Anareta" in result or "Mars" in result


# ─── _generate_constitution ──────────────────────────────────────────────────


def test_constitution_sect_and_temperament():
    report = _build_minimal_report()
    result = ReportSynthesizer._generate_constitution(report)
    assert "Day" in result
    assert "Sanguine" in result
    assert "Historical Use Only" in result


def test_constitution_humoral_scores():
    report = _build_minimal_report()
    result = ReportSynthesizer._generate_constitution(report)
    assert "Hot" in result
    assert "Cold" in result


def test_constitution_string_temperament():
    """Handle case where temperament is a plain string."""
    report = _build_minimal_report()
    report["summary"]["temperament"] = "Choleric"
    result = ReportSynthesizer._generate_constitution(report)
    assert "Choleric" in result


# ─── _generate_dignity_breakdown ─────────────────────────────────────────────


def test_dignity_breakdown_teams():
    report = _build_minimal_report()
    result = ReportSynthesizer._generate_dignity_breakdown(report)
    assert "Jupiter" in result
    assert "Mars" in result


# ─── _generate_planetary_protocols ───────────────────────────────────────────


def test_planetary_protocols_sun():
    report = _build_minimal_report()
    result = ReportSynthesizer._generate_planetary_protocols(report)
    assert "Sun in Leo" in result
    assert "Essential Dignity" in result


def test_planetary_protocols_delineation():
    report = _build_minimal_report()
    result = ReportSynthesizer._generate_planetary_protocols(report)
    assert "sovereign authority" in result


def test_planetary_protocols_node_delineation():
    """Nodes should get fallback delineation from internal dict."""
    report = _build_minimal_report()
    report["planets"].append(
        {
            "name": "North_Node",
            "sign": "Aries",
            "longitude": 10.0,
            "dignities": {"total_score": 0, "score_breakdown": {}},
            "solar_status": "FREE",
            "maltreatments": [],
            "retrograde": False,
            "speed": 0.0,
            "impacts": [],
            "delineation": "",
        }
    )
    result = ReportSynthesizer._generate_planetary_protocols(report)
    assert "North_Node" in result
    assert "AMPLIFICATION" in result  # From the node_delineations dict for Aries


def test_planetary_protocols_retrograde():
    report = _build_minimal_report()
    report["planets"][1]["retrograde"] = True
    report["planets"][1]["speed"] = -0.5
    result = ReportSynthesizer._generate_planetary_protocols(report)
    assert "Retrograde" in result or "℞" in result


def test_planetary_protocols_combust():
    report = _build_minimal_report()
    report["planets"][1]["solar_status"] = "COMBUST"
    result = ReportSynthesizer._generate_planetary_protocols(report)
    assert "COMBUST" in result


def test_planetary_protocols_maltreatment():
    report = _build_minimal_report()
    report["planets"][1]["maltreatments"] = [
        {"description": "Besieged by Mars and Saturn"}
    ]
    result = ReportSynthesizer._generate_planetary_protocols(report)
    assert "MALTREATMENT" in result
    assert "Besieged" in result


# ─── _generate_house_systems ────────────────────────────────────────────────


def test_house_systems_12_rows():
    report = _build_minimal_report()
    result = ReportSynthesizer._generate_house_systems(report)
    # Should have 12 house rows
    assert result.count("|") >= 24  # At least 12 rows × 2 pipes


# ─── _generate_aspect_analysis ──────────────────────────────────────────────


def test_aspect_analysis_sextile():
    report = _build_minimal_report()
    result = ReportSynthesizer._generate_aspect_analysis(report)
    assert "Sun" in result
    assert "Sextile" in result
    assert "Harmonious" in result


def test_aspect_analysis_no_aspects():
    report = _build_minimal_report()
    report["aspects"] = []
    result = ReportSynthesizer._generate_aspect_analysis(report)
    assert "No major classical aspects" in result


def test_aspect_analysis_applying():
    report = _build_minimal_report()
    result = ReportSynthesizer._generate_aspect_analysis(report)
    assert "increasing in intensity" in result


# ─── _generate_fixed_stars ──────────────────────────────────────────────────


def test_fixed_stars_present():
    report = _build_minimal_report()
    result = ReportSynthesizer._generate_fixed_stars(report)
    assert "Regulus" in result
    assert "Heart of the Lion" in result


def test_fixed_stars_empty():
    report = _build_minimal_report()
    report["fixed_stars"] = []
    result = ReportSynthesizer._generate_fixed_stars(report)
    assert result == ""


# ─── _generate_fate_timeline ────────────────────────────────────────────────


def test_fate_timeline_profections():
    report = _build_minimal_report()
    result = ReportSynthesizer._generate_fate_timeline(report)
    assert "Lord of the Year" in result
    assert "Jupiter" in result


def test_fate_timeline_firdaria():
    report = _build_minimal_report()
    result = ReportSynthesizer._generate_fate_timeline(report)
    assert "Firdaria" in result
    assert "Venus" in result


# ─── _generate_forensic_audit ───────────────────────────────────────────────


def test_forensic_audit_lot():
    report = _build_minimal_report()
    result = ReportSynthesizer._generate_forensic_audit(report)
    assert "Lot of Fortune" in result
    assert "Clear" in result
    assert "Mercury" in result


# ─── _generate_universal_overrides ──────────────────────────────────────────


def test_universal_overrides_empty():
    report = _build_minimal_report()
    result = ReportSynthesizer._generate_universal_overrides(report)
    assert "No major universal overrides" in result
