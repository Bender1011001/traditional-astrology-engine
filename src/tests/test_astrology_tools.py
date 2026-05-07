from unittest.mock import MagicMock, patch

from src.astrology_tools import AstrologyTools


def test_astrology_tools_calculate_chart():
    tools = AstrologyTools()
    with patch("src.astrology_tools.calculate_chart_data") as mock_calc:
        mock_calc.return_value = {"success": True}
        result = tools.calculate_chart(1996, 8, 13, 7, 18, "Fairfield", "CA")
        mock_calc.assert_called_once_with("1996-08-13", "07:18", "Fairfield", "CA")
        assert result == {"success": True}


def test_astrology_tools_forensic_audit():
    tools = AstrologyTools()
    with patch("src.astrology_tools.Auditor.generate_full_nativity") as mock_audit:
        mock_audit.return_value = {"audited": True}
        result = tools.forensic_audit(1996, 8, 13, 7, 18, "Fairfield", "CA")
        mock_audit.assert_called_once_with(
            date_str="1996-08-13", time_str="07:18", city="Fairfield", state="CA"
        )
        assert result == {"audited": True}


def test_astrology_tools_find_electional_window():
    tools = AstrologyTools()
    tools.electional = MagicMock()
    tools.electional.find_kairos.return_value = {"window": "found"}

    result = tools.find_electional_window(
        "Fairfield", "CA", "mercantile", 48, "2026-03-22T00:00:00"
    )

    tools.electional.find_kairos.assert_called_once()
    assert result == {"window": "found"}


def test_astrology_tools_get_mundane_context():
    tools = AstrologyTools()
    with patch("src.astrology_tools.MundaneEngine") as mock_engine_class:
        mock_engine = MagicMock()
        mock_engine.get_recent_eclipses.return_value = []
        mock_engine.get_latest_great_conjunction.return_value = {}
        mock_engine.get_world_firdaria.return_value = {}
        mock_engine.get_mighty_firdaria.return_value = {}
        mock_engine_class.return_value = mock_engine

        result = tools.get_mundane_context(2026, 2, 4)

        assert "eclipses" in result
        assert "great_conjunction" in result
        assert "world_firdaria" in result
        assert "mighty_firdaria" in result


def test_astrology_tools_format_electional_report():
    tools = AstrologyTools()
    windows_data = {
        "query": {
            "location": "Fairfield, CA",
            "activity": "general",
            "scan_range": "48 hours",
        },
        "best_windows": [
            {
                "start": "2026-03-22T10:00:00",
                "end": "2026-03-22T12:00:00",
                "peak_time": "2026-03-22T11:00:00",
                "peak_score": 50,
                "mood": "Favorable",
                "duration_hours": 2,
                "details": ["Mercury is dignified"],
            }
        ],
    }

    report = tools.format_electional_report(windows_data)
    assert "⏰ ELECTIONAL TIMING REPORT" in report
    assert "Fairfield, CA" in report
    assert "Favorable" in report
    assert "Mercury is dignified" in report

    # Test with natal context
    report_with_natal = tools.format_electional_report(
        windows_data,
        natal_context={
            "almuten": "Sun",
            "time_lord": "Moon",
            "recommendations": ["Do something"],
        },
    )
    assert "NATAL SYNCHRONIZATION" in report_with_natal
    assert "Sun" in report_with_natal
    assert "Moon" in report_with_natal
    assert "Do something" in report_with_natal
