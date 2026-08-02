"""Multi-tradition reading panel.

One birth input, one section per tradition whose rules we can actually source,
each carrying its own evidence grade and its own disclosures. Research-only:
nothing here is customer-eligible.
"""

from .panel import PANEL_VERSION, build_panel
from .render import render
from .types import (
    BirthInput,
    Disclosure,
    DisclosureKind,
    EvidenceGrade,
    TraditionSection,
)

__all__ = [
    "PANEL_VERSION",
    "BirthInput",
    "Disclosure",
    "DisclosureKind",
    "EvidenceGrade",
    "TraditionSection",
    "build_panel",
    "render",
]
