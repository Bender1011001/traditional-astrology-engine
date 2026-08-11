import pytest

from src.services.reading_contract import (
    ReadingContractError,
    enforce_customer_reading,
    validate_customer_reading,
)


HEADINGS = """# Your Nativity at a Glance
# The Leading Testimonies
# Life Topics
# The Present Chapter
# Where the Sources Differ
# Method and Limits
"""


def _valid_body(extra: str = "") -> str:
    prose = " ".join(
        [
            "Traditional doctrine treats this testimony as symbolic and conditional.",
            "Its expression depends on the planet's dignity, place, sect, and relationships.",
            "No single factor cancels the rest of the nativity.",
        ]
        * 45
    )
    return f"{HEADINGS}\n{prose}\n{extra}"


@pytest.mark.parametrize(
    ("claim", "code"),
    [
        ("Use analysis.planets_forensic[1].solar_status for the Moon.", "internal_output"),
        ("The universe will demand that you withdraw from public life.", "fatalistic_claim"),
        ("Fixed stars override standard planetary dignity.", "doctrine_overreach"),
        ("Primary Directions are the permission layer for every event.", "doctrine_overreach"),
        ("You must clear your debts and audit all legal commitments.", "protected_directive"),
        ("Uranus conjunct Altair is a central promise of eminence.", "outer_planet_core"),
    ],
)
def test_contract_rejects_unpublishable_claims(claim: str, code: str):
    violations = validate_customer_reading(_valid_body(claim))
    assert code in {violation.code for violation in violations}


def test_contract_requires_customer_editorial_structure():
    violations = validate_customer_reading("ordinary symbolic prose " * 700)
    assert "missing_structure" in {violation.code for violation in violations}


def test_contract_does_not_cap_length():
    """A long report is not an unsafe one.

    The old 20,000-word ceiling fail-closed the WHOLE report, so a customer who
    tripped it received nothing, and it counted the citation appendix appended
    after composition - rejecting reports for the size of their own footnotes.
    Length is an editorial concern, not a publication-safety one.
    """
    violations = validate_customer_reading(
        _valid_body("additional symbolic testimony " * 16_000)
    )
    assert not any(v.code == "too_long" for v in violations)
    assert not violations, [v.code for v in violations]


def test_contract_rejects_verbatim_repeated_paragraphs():
    paragraph = " ".join(f"distinct{i}" for i in range(40))
    violations = validate_customer_reading(_valid_body(f"\n\n{paragraph}\n\n{paragraph}"))
    assert "repeated_paragraph" in {violation.code for violation in violations}


def test_contract_accepts_safe_structured_report():
    assert validate_customer_reading(_valid_body()) == ()


def test_contract_accepts_historical_longevity_judgment():
    claim = (
        "The Mercury Alcocoden branch gives a lifetime of 76 years, while the rival Venus branch fails. "
        "A Saturn anaretic window appears at age 43.68 under the configured direction model."
    )
    assert validate_customer_reading(_valid_body(claim)) == ()


def test_enforcer_raises_with_auditable_codes():
    with pytest.raises(ReadingContractError) as exc_info:
        enforce_customer_reading(
            _valid_body("You must arrange medical care before the Moon leaves Leo.")
        )
    assert exc_info.value.violations
    assert "protected_directive" in str(exc_info.value)


def test_the_report_may_relay_what_the_sources_say_about_the_body():
    """Reporting a source's bodily doctrine is not a medical claim about the reader.

    Valens IV.4 assigns "climacterics, weaknesses, bleedings, falls or sufferings"
    to the release from Fortune; Ptolemy III.5 gives injuries "through cuttings
    and cauterisations"; the Aquarius/Saturn bound reads "dropsies and spasms".
    A filter that blocked this censored the sources, which is the practitioner's
    judgment this project does not exercise.
    """
    passage = (
        "Valens assigns bodily matters - climacterics, weaknesses, bleedings, falls "
        "or sufferings - to the release from the Lot of Fortune (IV.4, p. 160). "
        "Ptolemy III.5 gives injuries through cuttings and cauterisations, and the "
        "Aquarius bound of Saturn reads dropsies and spasms. This describes the "
        "doctrine, not a diagnosis or a prognosis for any person."
    )
    codes = {v.code for v in validate_customer_reading(passage, require_v2_structure=False)}
    assert "medical_or_surgical" not in codes
    assert "protected_directive" not in codes


def test_the_report_still_may_not_direct_the_reader_about_their_health():
    """Relaying is not advising. Our own voice telling someone to act still fails."""
    codes = {
        v.code
        for v in validate_customer_reading(
            "You should seek medical care and change your medication this year.",
            require_v2_structure=False,
        )
    }
    assert "protected_directive" in codes
