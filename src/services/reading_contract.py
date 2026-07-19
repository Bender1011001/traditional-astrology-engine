"""Fail-closed quality contract for customer-facing natal readings.

The calculation engine may expose historical techniques that are unsuitable for
an automated customer report.  This module validates the prose that leaves the
system.  It deliberately does not try to "fix" unsafe or unsupported claims:
when the report crosses a boundary, generation fails and can be retried or
reviewed by a human.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable


@dataclass(frozen=True)
class ReadingViolation:
    code: str
    message: str
    excerpt: str


class ReadingContractError(RuntimeError):
    """Raised when a customer report violates the publication contract."""

    def __init__(self, violations: Iterable[ReadingViolation]):
        self.violations = tuple(violations)
        detail = "; ".join(
            f"{item.code}: {item.message} [{item.excerpt}]"
            for item in self.violations
        )
        super().__init__(f"Customer reading failed publication validation: {detail}")


_INTERNAL_OUTPUT = re.compile(
    r"(?:analysis\.|astronomy\.|planets_forensic|lon_abs|"
    r"\b(?:DARK_MOON|MOON_UNDER_BEAMS|CONSTRUCTIVE_MALEFIC|DESTRUCTIVE_MALEFIC)\b)"
)

_FATALISTIC = re.compile(
    r"\b(?:the universe (?:will )?(?:demand|require)s?|mandatory (?:reset|reckoning)|"
    r"guaranteed|certain outcome|ultimate worldly success|architect of your own survival|"
    r"this will happen|fate has determined|the chart decrees)\b",
    re.IGNORECASE,
)

_DOCTRINE_OVERREACH = re.compile(
    r"(?:fixed stars?.{0,50}overrid(?:e|es|ing).{0,50}(?:dignit|planet|house)|"
    r"reception.{0,50}(?:overrid(?:e|es)|guarantee|ensures?|resolves?)|"
    r"primary directions?.{0,40}permission layer|"
    r"mundane (?:background|context|hierarchy).{0,50}overrid(?:e|es).{0,30}natal|"
    r"\b(?:Saturn|Mars)\b.{0,30}\b(?:ally|helpful malefic|constructive malefic)\b)",
    re.IGNORECASE | re.DOTALL,
)

_MEDICAL_OR_SURGICAL = re.compile(
    r"\b(?:surgery|surgical|operate on|operation on|safe for (?:surgery|intervention)|"
    r"touch(?:ed)? with iron|diagnos(?:is|e)|treatment|prognosis|"
    r"low blood pressure|acid imbalance|chronic headaches?|gastric irritation|"
    r"intestinal dryness|joint health|physical preservation|vulnerable systems?)\b",
    re.IGNORECASE,
)

_PROTECTED_DIRECTIVE = re.compile(
    r"\b(?:must|should|need to|required to|do not|never|avoid|focus entirely on|"
    r"step down|clear|organize|audit|scrutinize)\b[^.;]{0,90}\b(?:debts?|liabilit(?:y|ies)|"
    r"estate|contracts?|legal commitments?|investments?|speculation|livelihood|"
    r"physical health|medical care|surgery|medication|therapy)\b",
    re.IGNORECASE | re.DOTALL,
)

_OUTER_PLANET_CORE = re.compile(r"\b(?:Uranus|Neptune|Pluto)\b", re.IGNORECASE)

_REQUIRED_HEADINGS = (
    "# Your Nativity at a Glance",
    "# The Leading Testimonies",
    "# Life Topics",
    "# The Present Chapter",
    "# Where the Sources Differ",
    "# Method and Limits",
)


def _excerpt(text: str, match: re.Match[str], radius: int = 85) -> str:
    start = max(0, match.start() - radius)
    end = min(len(text), match.end() + radius)
    return re.sub(r"\s+", " ", text[start:end]).strip()[:260]


def _pattern_violation(
    text: str, pattern: re.Pattern[str], code: str, message: str
) -> ReadingViolation | None:
    match = pattern.search(text)
    if not match:
        return None
    return ReadingViolation(code, message, _excerpt(text, match))


def _repeated_paragraph(text: str) -> ReadingViolation | None:
    seen: dict[str, str] = {}
    for raw in re.split(r"\n\s*\n", text):
        paragraph = re.sub(r"[`*_>#|\[\]()-]", " ", raw)
        paragraph = re.sub(r"\s+", " ", paragraph).strip().lower()
        if len(paragraph.split()) < 35:
            continue
        normalized = re.sub(r"\b\d+(?:\.\d+)?\b", "#", paragraph)
        if normalized in seen:
            return ReadingViolation(
                "repeated_paragraph",
                "A substantial paragraph is repeated verbatim.",
                raw.strip()[:260],
            )
        seen[normalized] = raw
    return None


def validate_customer_reading(
    markdown: str,
    *,
    require_v2_structure: bool = True,
    minimum_words: int = 1_200,
    maximum_words: int = 20_000,
) -> tuple[ReadingViolation, ...]:
    """Return every publication violation found in ``markdown``.

    The validator operates on the customer body, not an internal computation
    trace.  A caller may disable the v2 heading requirement while migrating old
    stored reports, but safety and doctrine checks always run.
    """
    violations: list[ReadingViolation] = []
    if not markdown.strip():
        return (ReadingViolation("empty_report", "The report is empty.", ""),)

    word_count = len(re.findall(r"\b[\w'’-]+\b", markdown))
    if word_count < minimum_words:
        violations.append(
            ReadingViolation(
                "too_short",
                f"Report has {word_count} words; minimum is {minimum_words}.",
                markdown[:180].strip(),
            )
        )
    if word_count > maximum_words:
        violations.append(
            ReadingViolation(
                "too_long",
                f"Report has {word_count} words; maximum is {maximum_words}.",
                "The report must be edited for synthesis rather than aggregation.",
            )
        )

    checks = (
        (_INTERNAL_OUTPUT, "internal_output", "Raw engine paths or enums leaked into customer prose."),
        (_FATALISTIC, "fatalistic_claim", "The report makes a deterministic or guaranteed claim."),
        (_DOCTRINE_OVERREACH, "doctrine_overreach", "The report turns mitigation or hierarchy into a doctrinal override."),
        (_MEDICAL_OR_SURGICAL, "medical_or_surgical", "The report contains a diagnosis-like or surgical claim."),
        (_PROTECTED_DIRECTIVE, "protected_directive", "The report gives medical, financial, or legal direction."),
        (_OUTER_PLANET_CORE, "outer_planet_core", "Outer planets are outside the declared traditional septener scope."),
    )
    for pattern, code, message in checks:
        violation = _pattern_violation(markdown, pattern, code, message)
        if violation:
            violations.append(violation)

    if require_v2_structure:
        missing = [heading for heading in _REQUIRED_HEADINGS if heading not in markdown]
        if missing:
            violations.append(
                ReadingViolation(
                    "missing_structure",
                    "The report is missing required editorial sections.",
                    ", ".join(missing),
                )
            )

    repeated = _repeated_paragraph(markdown)
    if repeated:
        violations.append(repeated)
    return tuple(violations)


def enforce_customer_reading(markdown: str, **kwargs: object) -> str:
    """Return ``markdown`` unchanged or raise ``ReadingContractError``."""
    violations = validate_customer_reading(markdown, **kwargs)
    if violations:
        raise ReadingContractError(violations)
    return markdown
