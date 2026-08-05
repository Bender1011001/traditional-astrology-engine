"""Per-tradition report engines.

The multi-tradition *panel* answers "what does each system compute for this
birth, and what does it refuse to say?" - one screen, fifteen short sections.
That is a comparison instrument, and it is not a reading.

This package is the other thing: one full engine per tradition, each producing a
complete report in that tradition's own idiom and its own judgment order, at the
depth the Western premium report already has. A Jyotisha report is not a
Hellenistic report with Sanskrit words swapped in - it opens from the lagna and
its lord, judges by bhava and dignity, and closes on the daśā that is actually
running.

Each module exposes:

    build_report(birth, ...) -> TraditionReport

and every delineation sentence in the output traces to a rule in the research
corpus, quoted with its citation and evidence grade, or it does not appear.
"""

from __future__ import annotations

from .report import ReportSection, TraditionReport, render_markdown

#: The traditions that have a full report engine, mapped to their module. Kept
#: as names rather than imports so that adding a tradition does not make every
#: importer of this package pay for every engine's manifests.
REPORT_ENGINES = {
    "hellenistic": "hellenistic_report",
    "indian_jyotisha": "vedic_report",
    "bazi": "bazi_report",
    "islamicate_al_qabisi": "islamicate_report",
    "jaimini": "jaimini_report",
}


def build_tradition_report(tradition_id: str, birth, **kwargs):
    """Build the full report for one tradition.

    Raises KeyError for a tradition that has rules but no engine yet, which is
    a real and reportable state: the corpus carries several such tracks, and
    silently returning an empty report would hide them.
    """
    from importlib import import_module

    module = import_module(f".{REPORT_ENGINES[tradition_id]}", __package__)
    return module.build_report(birth, **kwargs)


__all__ = [
    "REPORT_ENGINES",
    "ReportSection",
    "TraditionReport",
    "build_tradition_report",
    "render_markdown",
]
