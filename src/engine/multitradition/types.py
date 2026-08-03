"""Shared types for the multi-tradition panel.

Every tradition section carries its own evidence grade and an explicit list of
disclosures. A disclosure is how the panel stays defendable: any convention the
product chose (rather than inherited from a validated research pack) must appear
as a `configured_method` disclosure naming the alternatives it displaced.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any


class EvidenceGrade(str, Enum):
    """How well-sourced a section's calculation basis is.

    VALIDATED_PACK  - arithmetic comes from a fail-closed research pack whose
                      standalone validator passes in this repository.
    LIVE_ENGINE     - produced by the shipping Western engine.
    CONFIGURED      - the product selected a convention the research pack
                      deliberately refuses to default; every such choice is
                      disclosed with its alternatives.
    TRANSCRIPTION   - rests on an inspected transcription that cannot yet
                      control wording.
    """

    VALIDATED_PACK = "validated_research_pack"
    LIVE_ENGINE = "live_engine"
    CONFIGURED = "configured_method"
    TRANSCRIPTION = "transcription_grade"


class DisclosureKind(str, Enum):
    CONFIGURED_METHOD = "configured_method"
    FORK = "fork"
    REFUSAL = "refusal"
    SOURCE = "source"


# Refusals differ in meaning, and rendering them all with one label conceals
# that. Each refusal names WHY, from this closed vocabulary, so a reader can
# tell an absent genre from an unread source from a policy suppression - they
# imply very different completeness and very different paths to resolution.
REFUSAL_CATEGORIES = frozenset({
    "not_part_of_tradition",     # the tradition has no such genre at all
    "historically_unattested",   # the specific claim has no surviving witness
    "source_unavailable",        # no usable witness has been acquired
    "source_unread",             # acquired but not yet read/transcribed
    "translation_pending",       # read, but rendering not yet reviewable
    "extraction_incomplete",     # rules only partially encoded
    "calculation_unimplemented", # method known, engine work not done
    "missing_user_input",        # needs an input the schema does not carry
    "school_fork_unresolved",    # competing doctrines, none selected
    "policy_suppressed",         # computed/known but withheld by publication policy
})


@dataclass(frozen=True)
class Disclosure:
    """One statement about how this section was produced, or what it will not say."""

    kind: DisclosureKind
    subject: str
    detail: str
    alternatives: tuple[str, ...] = ()
    category: str | None = None  # for refusals: one of REFUSAL_CATEGORIES

    def __post_init__(self) -> None:
        if self.category is not None and self.category not in REFUSAL_CATEGORIES:
            raise ValueError(f"Unknown refusal category: {self.category!r}")

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "kind": self.kind.value,
            "subject": self.subject,
            "detail": self.detail,
        }
        if self.alternatives:
            payload["alternatives"] = list(self.alternatives)
        if self.category:
            payload["category"] = self.category
        return payload


@dataclass(frozen=True)
class BirthInput:
    """A resolved birth moment. Timezone offset is explicit; nothing is guessed.

    The optional fields exist because several traditions REQUIRE them and their
    absence is a different problem from doctrinal ambiguity (review finding 9):
    BaZi luck-pillar direction and Zi Wei decade limits need the native's sex
    under the traditions' own conventions; time-dependent structures need to
    know how certain the recorded time is. None means "not supplied", and an
    engine must say "missing input", never silently pick.
    """

    name: str
    civil_date: date
    civil_time: str  # "HH:MM" wall clock at the place of birth
    utc_offset_hours: float
    latitude: float
    longitude: float
    place_label: str
    # Optional, tradition-specific. sex is the traditional male/female
    # classification several systems key their arithmetic to - engines treat
    # it as that technical input, nothing more.
    sex: str | None = None                  # "male" | "female" | None
    birth_time_certainty: str | None = None  # e.g. "exact", "rounded", "approximate"
    time_source: str | None = None           # e.g. "birth certificate", "memory"

    @property
    def civil_datetime(self) -> datetime:
        hour, minute = (int(part) for part in self.civil_time.split(":"))
        return datetime(
            self.civil_date.year,
            self.civil_date.month,
            self.civil_date.day,
            hour,
            minute,
        )

    @property
    def utc_datetime(self) -> datetime:
        from datetime import timedelta

        return self.civil_datetime - timedelta(hours=self.utc_offset_hours)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "civil_date": self.civil_date.isoformat(),
            "civil_time": self.civil_time,
            "utc_offset_hours": self.utc_offset_hours,
            "utc_datetime": self.utc_datetime.isoformat(),
            "latitude": self.latitude,
            "longitude": self.longitude,
            "place_label": self.place_label,
            **({"sex": self.sex} if self.sex else {}),
            **({"birth_time_certainty": self.birth_time_certainty}
               if self.birth_time_certainty else {}),
            **({"time_source": self.time_source} if self.time_source else {}),
        }


@dataclass
class TraditionSection:
    """One tradition's contribution to the panel."""

    tradition_id: str
    display_name: str
    evidence_grade: EvidenceGrade
    basis: str
    facts: dict[str, Any] = field(default_factory=dict)
    disclosures: list[Disclosure] = field(default_factory=list)
    reading: list[str] = field(default_factory=list)
    error: str | None = None

    def disclose(
        self,
        kind: DisclosureKind,
        subject: str,
        detail: str,
        alternatives: tuple[str, ...] = (),
        category: str | None = None,
    ) -> None:
        self.disclosures.append(
            Disclosure(kind, subject, detail, alternatives, category)
        )

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "tradition_id": self.tradition_id,
            "display_name": self.display_name,
            "evidence_grade": self.evidence_grade.value,
            "basis": self.basis,
            "facts": self.facts,
            "disclosures": [d.to_dict() for d in self.disclosures],
        }
        if self.reading:
            payload["reading"] = self.reading
        if self.error:
            payload["error"] = self.error
        return payload
