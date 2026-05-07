

from src.engine.forensic_engine import Auditor


def test_auditor_generate_full_nativity():
    """
    Test that Auditor.generate_full_nativity runs successfully and returns the
    bifurcated structure (technical_data, human_translation) expected by the CLI and API.
    """
    date_str = "1990-05-15"
    time_str = "14:30"
    city = "New York"
    state = "NY"
    name = "Test Native"

    # Assume standard house system (W) and tropical zodiac
    result = Auditor.generate_full_nativity(
        date_str=date_str,
        time_str=time_str,
        city=city,
        state=state,
        name=name,
        house_system="W",
        zodiac_system="tropical",
    )

    # Make sure no fatal errors occurred
    assert (
        "error" not in result
    ), f"generate_full_nativity returned an error: {result.get('error')}"

    # Verify the bifurcated payload
    assert "technical_data" in result
    assert "human_translation" in result

    # Check top-level elements of technical_data
    tech_data = result["technical_data"]
    assert "meta" in tech_data
    assert tech_data["meta"]["subject_name"] == name
    assert tech_data["meta"]["city"] == city
    assert "astronomy" in tech_data
    assert "analysis" in tech_data
    assert "rule_ledger" in tech_data

    # Check that analysis sub-modules ran
    analysis = tech_data["analysis"]
    assert "sect" in analysis
    assert "dignity" in analysis
    assert "aspects" in analysis

    # Verify the human translation output
    human_trans = result["human_translation"]
    assert "report_markdown" in human_trans
    assert "executive_summary" in human_trans
    assert len(human_trans["report_markdown"]) > 0


def test_auditor_invalid_input():
    """
    Test that the Auditor gracefully handles bad inputs and returns an error dictionary.
    """
    result = Auditor.generate_full_nativity(
        date_str="INVALID-DATE", time_str="14:30", city="New York"
    )

    assert "error" in result
    assert "technical_data" not in result
