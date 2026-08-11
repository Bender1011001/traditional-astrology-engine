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

# "guaranteed" and "certain outcome" were matched as bare words, which meant the
# contract flagged its OWN disclaimers - "it describes the manner and severity of
# a difficulty, not a guaranteed event" tripped the fatalism check. That pushes
# authors toward vaguer hedging, which is the opposite of what this rule is for.
# The check now requires an ASSERTIVE construction, so a promise still fails and
# a denial of a promise does not. Variable-width lookbehind is unavailable in
# `re`, so enumerating negations is not an option; requiring the assertive form
# is both simpler and harder to defeat by accident.
_FATALISTIC = re.compile(
    r"\b(?:the universe (?:will )?(?:demand|require)s?|mandatory (?:reset|reckoning)|"
    r"(?:is|are|was|were)\s+guaranteed|guarantees?\s+(?:that|you|a\b|an\b|the\b)|"
    r"guaranteed\s+(?:outcome|success|result|to\b)|"
    r"(?:is|are|it is)\s+(?:a\s+)?certain outcome|"
    r"ultimate worldly success|architect of your own survival|"
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

# A `_MEDICAL_OR_SURGICAL` filter used to sit here. It blocked surgery,
# diagnosis, treatment, prognosis, "touched with iron", and a list of specific
# complaints. It is removed, because it censored the SOURCES.
#
# Valens IV.4 (p. 160) assigns "climacterics, weaknesses, bleedings, falls or
# sufferings" to the release from Fortune. Ptolemy III.5 gives deaths and
# injuries "through cuttings and cauterisations". The Aquarius/Saturn bound at
# I.3 reads "dropsies and spasms". That is the doctrine; reporting what a source
# says about a chart is not a medical claim about the reader, and a regex
# deciding which parts of a 2nd-century text a customer may see is exactly the
# practitioner's judgment this project does not exercise.
#
# What still holds the line is `_PROTECTED_DIRECTIVE` below: the report may
# report what Valens says, and may not tell anyone in OUR voice to seek care,
# change medication, or act on their health. Relaying is not advising.

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


# A phrase inside a denial is not the claim the contract is guarding against.
# "success is guaranteed" must fail; "nothing here is guaranteed" and "not a
# guaranteed event" are the disclaimers we WANT authors to write, and flagging
# them pushes the prose toward vaguer hedging - the opposite of the intent.
# Python's `re` has no variable-width lookbehind, so this is checked as a window
# of preceding text rather than inside each pattern.
_NEGATION_NEARBY = re.compile(
    r"\b(?:not|never|no|none|nothing|nor|without|cannot|can't|doesn't|does not|"
    r"isn't|is not|won't|will not|rather than|instead of)\b[^.;:]{0,40}$",
    re.IGNORECASE,
)


def _pattern_violation(
    text: str, pattern: re.Pattern[str], code: str, message: str
) -> ReadingViolation | None:
    for match in pattern.finditer(text):
        # Look back to the start of the sentence, capped, for a negator.
        window_start = max(0, match.start() - 80)
        preceding = text[window_start : match.start()]
        preceding = re.split(r"[.;:]\s", preceding)[-1]
        if _NEGATION_NEARBY.search(preceding):
            continue
        return ReadingViolation(code, message, _excerpt(text, match))
    return None


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
    # There is deliberately NO upper word limit. One existed (20,000, added in
    # 8c000ca with the v7 pipeline) to stop the composer aggregating every
    # technique instead of synthesising. It did not do that. It fail-closed the
    # ENTIRE report - a customer who tripped it received nothing at all - and it
    # counted the citation appendix that `_append_evidence_notes` bolts on after
    # composition, so reports were being rejected for the size of their own
    # footnotes. Length is not a safety property. Aggregation is an editorial
    # problem and belongs in the composer, not in a publication gate. The real
    # guards - fatalism, medical, doctrine overreach, outer planets, repetition,
    # and the minimum - all remain below.

    checks = (
        (_INTERNAL_OUTPUT, "internal_output", "Raw engine paths or enums leaked into customer prose."),
        (_FATALISTIC, "fatalistic_claim", "The report makes a deterministic or guaranteed claim."),
        (_DOCTRINE_OVERREACH, "doctrine_overreach", "The report turns mitigation or hierarchy into a doctrinal override."),
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
