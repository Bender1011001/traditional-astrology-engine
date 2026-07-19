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
        ("This indicates chronic headaches and low blood pressure.", "medical_or_surgical"),
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


def test_contract_rejects_excessive_length():
    violations = validate_customer_reading(
        _valid_body("additional symbolic testimony " * 16_000)
    )
    assert "too_long" in {violation.code for violation in violations}


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
        enforce_customer_reading(_valid_body("Surgery is safe when the Moon leaves Leo."))
    assert exc_info.value.violations
    assert "medical_or_surgical" in str(exc_info.value)


def test_plain_english_treat_as_is_not_a_medical_claim():
    """'Treat it as a failed variant' is doctrine language, not a treatment claim.

    Regression: the medical filter previously matched the bare word 'treat',
    which blocked publication for any chart whose longevity fork includes the
    engine's own falsification caveat.
    """
    from src.services.reading_contract import validate_customer_reading

    passage = (
        "The computed years fall below the native's current age, so the branch "
        "is empirically falsified as a literal figure. Treat it as a failed or "
        "misapplied variant requiring rectification."
    )
    codes = {v.code for v in validate_customer_reading(passage, require_v2_structure=False)}
    assert "medical_or_surgical" not in codes

    codes_bad = {
        v.code
        for v in validate_customer_reading(
            "This configuration suggests a treatment plan for the native.",
            require_v2_structure=False,
        )
    }
    assert "medical_or_surgical" in codes_bad
