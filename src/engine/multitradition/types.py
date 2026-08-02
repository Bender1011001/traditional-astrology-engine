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


@dataclass(frozen=True)
class Disclosure:
    """One statement about how this section was produced, or what it will not say."""

    kind: DisclosureKind
    subject: str
    detail: str
    alternatives: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "kind": self.kind.value,
            "subject": self.subject,
            "detail": self.detail,
        }
        if self.alternatives:
            payload["alternatives"] = list(self.alternatives)
        return payload


@dataclass(frozen=True)
class BirthInput:
    """A resolved birth moment. Timezone offset is explicit; nothing is guessed."""

    name: str
    civil_date: date
    civil_time: str  # "HH:MM" wall clock at the place of birth
    utc_offset_hours: float
    latitude: float
    longitude: float
    place_label: str

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
    ) -> None:
        self.disclosures.append(Disclosure(kind, subject, detail, alternatives))

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
