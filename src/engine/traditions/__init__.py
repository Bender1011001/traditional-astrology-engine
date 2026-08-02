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

__all__ = ["ReportSection", "TraditionReport", "render_markdown"]
