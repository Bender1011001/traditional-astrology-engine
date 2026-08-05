"""What kind of document a report actually is, decided by its own contents.

An external review put it exactly: "the current collection gives a false
impression of uniform completeness. One report is an extensive Jyotiṣa
calculation, another is a source-critical Jaimini notebook, another is an
unresolved calendar experiment, and another has zero sourced delineations. They
should not all be presented under the same 'full reading' product category."

That is right, and the fix is not to write better titles by hand - hand-written
labels go stale the moment an engine improves, which this project has already
done twice in one week. The label is computed from what the report contains.

The classification is deliberately harsh at the boundaries. A document with no
sourced delineation is not a reading in any sense a practitioner would accept,
however much arithmetic it contains, and a document whose central anchor is
unsettled is a reconstruction of a method rather than a judgment about a person.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

READING = "reading"
DOSSIER = "calculation dossier"
RECONSTRUCTION = "provisional reconstruction"
AUDIT = "source audit"

LABEL = {
    READING: "Reading",
    DOSSIER: "Calculation dossier",
    RECONSTRUCTION: "Provisional reconstruction",
    AUDIT: "Source audit",
}

EXPLANATION = {
    READING: (
        "This document delineates. It quotes sourced judgments about this "
        "chart, in this tradition's own order, and names what it withholds."
    ),
    DOSSIER: (
        "This document CALCULATES more than it delineates. The figures are "
        "computed and checked; the interpretive layer above them is thin, so "
        "read it as a worked chart rather than as a judgment."
    ),
    RECONSTRUCTION: (
        "This document reconstructs a METHOD more than it reads a chart. Its "
        "central anchor is unsettled — see the refusals — so its structure is "
        "shown for inspection rather than applied to the native."
    ),
    AUDIT: (
        "This document contains NO sourced delineation for this chart. It "
        "reports what the tradition computes and what this engine can and "
        "cannot yet establish. It is not a reading and is not offered as one."
    ),
}

#: A report needs at least this many quoted delineations before the word
#: "reading" is defensible. Below it, the arithmetic is doing all the work.
DELINEATION_FLOOR = 12

#: Phrases that mean the report's own anchor did not settle. A chart whose
#: birth mansion or main-star board is undetermined has no stable subject.
ANCHOR_FAILURE = (
    "not emitted",
    "has a settled palace",
    "not settled",
    "could not be computed",
    "not placed",
)


@dataclass
class Readiness:
    kind: str
    delineations: int
    refusals: int
    anchor_unsettled: bool

    @property
    def label(self) -> str:
        return LABEL[self.kind]

    @property
    def explanation(self) -> str:
        return EXPLANATION[self.kind]


def _anchor_unsettled(report: Any) -> bool:
    for section in report.sections:
        for refusal in section.refusals:
            low = refusal.lower()
            if any(p in low for p in ANCHOR_FAILURE):
                return True
    return False


def classify(report: Any) -> Readiness:
    """What this report is, from what it contains rather than what it hoped."""
    delineations = report.delineation_count
    refusals = sum(len(s.refusals) for s in report.sections)
    unsettled = _anchor_unsettled(report)

    if delineations == 0:
        kind = AUDIT
    elif unsettled:
        kind = RECONSTRUCTION
    elif delineations < DELINEATION_FLOOR:
        kind = DOSSIER
    else:
        kind = READING

    return Readiness(
        kind=kind,
        delineations=delineations,
        refusals=refusals,
        anchor_unsettled=unsettled,
    )
