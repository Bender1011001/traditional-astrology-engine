from pathlib import Path
import re

from src.services.html_report_renderer import build_report_context


ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "src" / "templates" / "reports"
HTML_PATH = REPORT_DIR / "astrology_report_template.html"
CSS_PATH = REPORT_DIR / "astrology_report_template.css"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_astrology_report_template_has_ordered_modules_without_fixed_page_contract():
    html = _read(HTML_PATH)
    modules = re.findall(
        r'<section class="[^"]*\breport-section\b[^"]*" data-section-index="(\d+)" data-section="([^"]+)"',
        html,
    )

    assert len(modules) >= 20
    assert [int(module[0]) for module in modules] == list(range(1, len(modules) + 1))
    assert len({module[1] for module in modules}) == len(modules)
    assert "data-page=" not in html


def test_astrology_report_template_keeps_pdf_print_rules():
    css = _read(CSS_PATH)

    assert "@page" in css
    assert "size: Letter" in css
    assert "break-after: page" in css
    assert "page-break-after: always" in css
    assert ".cover-page,\n.final-page" in css
    assert "counter-reset: report-section" in css
    assert "counter-increment: report-section" in css
    assert "print-color-adjust: exact" in css
    assert "--foil-gradient" in css


def test_astrology_report_template_has_required_safety_and_conversion_slots():
    html = _read(HTML_PATH)

    assert "Historical Use Only" in html
    assert "medical, legal, psychological, emergency, investment, or financial advice" in html
    assert "report.next_steps.actions" in html
    assert "report.conversion.primary_recommendation" in html
    assert "report.summary.sect" in html


def test_astrology_report_template_has_engine_data_bindings_for_major_sections():
    html = _read(HTML_PATH)
    required_bindings = [
        "report.chart.wheel_svg",
        "report.technical_readout.rows",
        "report.planets",
        "report.houses",
        "report.dignities",
        "report.aspects",
        "report.receptions",
        "report.lots",
        "report.timing.profection",
        "report.timing.firdaria.periods",
        "report.timing.spirit_peak",
        "report.timing.primary_directions",
        "report.synthesis.themes",
    ]

    for binding in required_bindings:
        assert binding in html


def test_astrology_report_template_contains_no_unfinished_markers():
    combined = _read(HTML_PATH) + "\n" + _read(CSS_PATH)
    forbidden = [
        "TODO",
        "FIXME",
        "Lorem ipsum",
        "logic goes here",
        "pass",
    ]

    for marker in forbidden:
        assert marker not in combined


def test_report_renderer_maps_engine_data_into_template_context():
    chart_data = {
        "meta": {
            "subject_name": "Test Native",
            "birth_date": "1996-08-13",
            "birth_time": "07:18",
            "city": "Fairfield",
            "state": "CA",
            "lat": 38.2493581,
            "lon": -122.039966,
            "timezone": "America/Los_Angeles",
            "utc_time": "1996-08-13T14:18:00+00:00",
            "chart": {"house_system": "Whole Sign", "zodiac_system": "Tropical"},
        },
        "astronomy": {
            "planets": {
                "Sun": {"longitude": 141.1},
                "Mercury": {"longitude": 167.2},
                "North_Node": {"longitude": 339.1},
                "Uranus": {"longitude": 304.2},
            },
            "houses": {str(index): (150 + (index - 1) * 30) % 360 for index in range(1, 13)},
            "angles": {"Ascendant": 151.5, "MC": 57.0},
        },
        "analysis": {
            "sect": {"type": "DAY", "sun_altitude_deg": 9.87},
            "angles": {
                "Ascendant": {"longitude": 151.5, "longitude_fmt": {"string": "Virgo 01°30'00\""}},
                "Midheaven": {"longitude": 57.0, "longitude_fmt": {"string": "Taurus 27°00'00\""}},
                "note": "Whole Sign topics with MC separately.",
            },
            "dignity": {"almuten": {"winner": "Mercury", "score": 27, "breakdown": {"Mercury": 27}}},
            "teams": {"constructive_team": ["Sun"], "destructive_team": ["Mars"], "receptions": []},
            "temperament": {"primary_temperament": "Melancholic", "scores": {"Cold": 8, "Dry": 7}},
            "planets_forensic": [
                {
                    "name": "Mercury",
                    "longitude": 167.2,
                    "longitude_fmt": {"string": "Virgo 17°10'58\""},
                    "sign": "Virgo",
                    "house": 1,
                    "retrograde": False,
                    "dignities": {"total_score": 9},
                    "accidental": {"total_score": 11, "details": ["In the 1th House (+5)"]},
                    "details": ["Domicile (+5)", "Exaltation (+4)"],
                    "solar_status": "FREE",
                },
                {
                    "name": "North_Node",
                    "longitude": 339.1,
                    "sign": "Pisces",
                    "house": 7,
                    "retrograde": True,
                    "dignities": {"total_score": 0},
                    "accidental": {"total_score": 0},
                    "details": [],
                },
            ],
            "aspects": [],
            "fate": {
                "firdaria": {
                    "Major Period": "Mercury",
                    "Sub Period": "Venus",
                    "Current Age": 29.73,
                },
                "hermetic_lots": {
                    "Spirit": {
                        "longitude": 159.35,
                        "sign": "Virgo",
                        "longitude_fmt": {"string": "Virgo 09°21'00\""},
                        "house": 1,
                        "ruler": "Mercury",
                        "status": "Clear",
                    }
                },
                "primary_directions": [],
            },
            "enhanced_profections": {"age": 29, "annual_sign": "Aquarius", "lord_of_year": "Saturn"},
            "solar_return": {},
            "supplemental": {"stars": []},
        },
    }

    context = build_report_context(
        chart_data,
        "# Part 1\n\n### NATAL CHART AUDIT\nThis is a real customer-facing report body.",
    )
    report = context["report"]

    assert report["client"]["display_name"] == "Test Native"
    assert report["summary"]["sect"] == "Day"
    assert report["summary"]["almuten"] == "Mercury"
    assert "Virgo" in report["summary"]["ascendant"]
    assert report["chart"]["wheel_svg"].startswith('<svg class="chart-wheel"')
    assert "NN" not in report["chart"]["wheel_svg"]
    assert "Uranus" not in report["chart"]["wheel_svg"]
    assert {row["name"] for row in report["planets"]} == {"Mercury"}
    assert report["technical_readout"]["badges"][0] == "7 visible planets"
    assert report["timing"]["spirit_peak"]["peak_sign"] == "Gemini"
