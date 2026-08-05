"""Things that must never appear in a report a human reads.

Every rule here corresponds to a defect that actually shipped. An external
review of the 2026-08-05 reports found all of them by reading the files, which
is the one check nobody had automated: the reports built, the sections
rendered, the sentences parsed, and the prose contained a source-code path.

The rules are deliberately about SURFACE, not about astrology. A linter that
tried to judge whether a delineation was apt would be another unreliable
classifier. This one only asks whether a string that belongs in a debugger has
escaped into a document, and that question has a right answer.

Two rules are subtler than the rest and are here because the review caught them:

- ``not_computed`` may not be rendered as ``failed``. The distinction is the
  whole of this project's uncertainty discipline, and collapsing it in prose
  undoes in one line what the engine took care to preserve.
- A report may not name a source that its own tradition does not use. That one
  was template leakage - a Hellenistic report citing Sāravalī - and it is
  indistinguishable, to a reader, from a claim about Hellenistic astrology.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

#: Tokens that only ever come from a debugger, a dict repr, or a code path.
IMPLEMENTATION_TOKENS = (
    (re.compile(r"\bsrc/[a-z_]+/"), "a source-code path"),
    # Only in VALUE position. "None of the fourteen" and "True solar time" are
    # ordinary English; ": False" and "| None |" are a debugger talking.
    (re.compile(r"(?::|=|\|)\s*(None|True|False)\b"), "a Python value in prose"),
    (re.compile(r"`(None|True|False)`"), "a Python value in prose"),
    (re.compile(r"\bresearch_only\b"), "the internal policy token research_only"),
    (re.compile(r"\bcustomer_prediction\b"), "an internal policy key"),
    (re.compile(r"\boutput_policy\b"), "an internal policy key"),
    (re.compile(r"\brendering_grade\b"), "an internal grading key"),
    (re.compile(r"\bengine_rendering\b"), "an internal field name"),
    (re.compile(r"\bempty -"), "a raw status string"),
    (re.compile(r"\b[a-z]+_[a-z]+_[a-z_]+\b(?![)\]])"), "a snake_case identifier"),
)

#: Uncertainty states that must not be flattened into each other in prose.
UNCERTAINTY_COLLAPSE = (
    (
        re.compile(r"place None.*?(failed|not eligible)", re.IGNORECASE),
        "an uncomputed candidate rendered as though it had been tested",
    ),
    (
        re.compile(r"not[_ ]computed.*?\bfailed\b", re.IGNORECASE),
        "not_computed rendered as failed",
    ),
)

#: A number that never got computed, printed as though it were a position.
NULL_QUANTITY = re.compile(
    r"(falls?|rises?|stands?|lies?)\s+at\s+(None|nan|null)", re.IGNORECASE
)

#: A foreign source is only a defect when the report claims to be USING it -
#: al-Qabisi naming Valens as the authority for a lot is scholarship, not
#: leakage, and the two read identically to a regex that only looks for names.
METHOD_LANGUAGE = re.compile(
    r"adjudicat|precedence|gates?\b|synthesis uses|for this tradition",
    re.IGNORECASE,
)

#: Sources that belong to one tradition appearing in another's report. The
#: value is the set of tradition_ids where naming it is legitimate.
SOURCE_OWNERSHIP = {
    "Saravali": {"indian_jyotisha", "jaimini"},
    "Sāravalī": {"indian_jyotisha", "jaimini"},
    "Phaladeepika": {"indian_jyotisha", "jaimini"},
    "Phaladīpikā": {"indian_jyotisha", "jaimini"},
    "BPHS": {"indian_jyotisha", "jaimini"},
    "Firmicus": {"hellenistic"},
    "Valens": {"hellenistic"},
    "al-Qabisi": {"islamicate_al_qabisi"},
    "al-Qabīsī": {"islamicate_al_qabisi"},
}

#: Lines that are allowed to contain otherwise-banned tokens, because quoting
#: the token IS the point - a disclosure that names the convention it used.
ALLOWED_CONTEXT = re.compile(
    r"configured_method|is labelled|is named here|the word|the token", re.IGNORECASE
)


@dataclass
class Finding:
    rule: str
    detail: str
    where: str
    excerpt: str

    def __str__(self) -> str:
        return f"[{self.rule}] {self.detail} in {self.where}: {self.excerpt!r}"


def _lines_of(report: Any) -> list[tuple[str, str]]:
    """Every reader-facing string, paired with the section it came from."""
    out: list[tuple[str, str]] = []
    for section in report.sections:
        for note in section.notes:
            out.append((section.title, note))
        for refusal in section.refusals:
            out.append((section.title, refusal))
        for d in section.delineations:
            out.append((section.title, d.text))
    return out


def lint(report: Any, *, strict_snake_case: bool = True) -> list[Finding]:
    """Every surface defect in a built report.

    ``strict_snake_case`` is separable because a few legitimate technical terms
    are snake_case in every tradition's vocabulary, and a caller mid-cleanup
    may want the louder failures first.
    """
    findings: list[Finding] = []
    tradition = getattr(report, "tradition_id", "")

    for where, text in _lines_of(report):
        if NULL_QUANTITY.search(text):
            findings.append(Finding(
                "null-quantity",
                "an uncomputed number printed as though it were a position",
                where, text[:120],
            ))
        for pattern, detail in UNCERTAINTY_COLLAPSE:
            if pattern.search(text):
                findings.append(
                    Finding("uncertainty-collapse", detail, where, text[:120])
                )
        allowed = ALLOWED_CONTEXT.search(text)
        for pattern, detail in IMPLEMENTATION_TOKENS:
            if detail == "a snake_case identifier" and not strict_snake_case:
                continue
            m = pattern.search(text)
            if not m:
                continue
            if allowed and detail in (
                "a snake_case identifier", "the internal policy token research_only"
            ):
                continue
            findings.append(
                Finding("implementation-leak", detail, where, text[:120])
            )
        for name, owners in SOURCE_OWNERSHIP.items():
            if not (name in text and tradition and tradition not in owners):
                continue
            if METHOD_LANGUAGE.search(text):
                findings.append(Finding(
                    "foreign-source",
                    f"{name} cited as METHOD in a {tradition} report",
                    where, text[:120],
                ))
    return findings


def assert_clean(report: Any, **kw: Any) -> None:
    findings = lint(report, **kw)
    if findings:
        raise AssertionError(
            f"{len(findings)} report-lint failure(s) in "
            f"{getattr(report, 'tradition_id', '?')}:\n  "
            + "\n  ".join(str(f) for f in findings[:12])
        )
