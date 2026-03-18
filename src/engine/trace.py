"""
Computation Trace Engine
========================
Captures every calculation step in a reading so practitioners can follow
along and verify the work.  Each step records:

    Category → Technique → Inputs → Rule Applied → Calculation → Result

The trace is rendered as a beautiful standalone HTML document.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class TraceStep:
    """A single auditable computation step."""
    step_number: int
    category: str           # e.g. "Essential Dignities", "Lots", "Aspects"
    technique: str          # e.g. "Domicile Lookup", "Lot of Fortune"
    inputs: Dict[str, Any]  # Human-readable inputs
    rule: str               # The rule or formula in plain language
    source: str             # Historical source (e.g. "Ptolemy, Tetrabiblos I.17")
    calculation: str        # Step-by-step arithmetic or logic
    result: Any             # The final result of this step
    notes: str = ""         # Optional practitioner notes
    subsection: str = ""    # Optional grouping within category


class ComputationTrace:
    """Collects computation steps during a reading."""

    def __init__(self, subject_name: str = "Native", birth_data: str = ""):
        self.subject_name = subject_name
        self.birth_data = birth_data
        self.steps: List[TraceStep] = []
        self.started_at = datetime.now()
        self._counter = 0
        self._start_time = time.perf_counter()

    def add(
        self,
        category: str,
        technique: str,
        inputs: Dict[str, Any],
        rule: str,
        source: str,
        calculation: str,
        result: Any,
        notes: str = "",
        subsection: str = "",
    ) -> TraceStep:
        """Add a computation step to the trace."""
        self._counter += 1
        step = TraceStep(
            step_number=self._counter,
            category=category,
            technique=technique,
            inputs=inputs,
            rule=rule,
            source=source,
            calculation=calculation,
            result=result,
            notes=notes,
            subsection=subsection,
        )
        self.steps.append(step)
        return step

    @property
    def elapsed_ms(self) -> float:
        return (time.perf_counter() - self._start_time) * 1000

    @property
    def categories(self) -> List[str]:
        """Return ordered unique categories."""
        seen = []
        for s in self.steps:
            if s.category not in seen:
                seen.append(s.category)
        return seen

    def steps_by_category(self, category: str) -> List[TraceStep]:
        return [s for s in self.steps if s.category == category]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subject_name": self.subject_name,
            "birth_data": self.birth_data,
            "generated_at": self.started_at.isoformat(),
            "total_steps": len(self.steps),
            "elapsed_ms": round(self.elapsed_ms, 1),
            "categories": self.categories,
            "steps": [
                {
                    "step": s.step_number,
                    "category": s.category,
                    "subsection": s.subsection,
                    "technique": s.technique,
                    "inputs": s.inputs,
                    "rule": s.rule,
                    "source": s.source,
                    "calculation": s.calculation,
                    "result": str(s.result) if not isinstance(s.result, (str, int, float, bool, type(None))) else s.result,
                    "notes": s.notes,
                }
                for s in self.steps
            ],
        }


# ─── Category constants for consistency ───────────────────────────────────────
CAT_ASTRONOMY    = "① Astronomical Foundations"
CAT_SECT         = "② Sect Determination"
CAT_DIGNITY      = "③ Essential Dignities"
CAT_ACCIDENTAL   = "④ Accidental Dignities"
CAT_ASPECTS      = "⑤ Aspects & Geometry"
CAT_LOTS         = "⑥ Arabic Parts / Lots"
CAT_RECEPTION    = "⑦ Reception & Mutual Reception"
CAT_KAKOSIS      = "⑧ Conditions of Maltreatment (Kakosis)"
CAT_VITALITY     = "⑨ Vitality & Longevity"
CAT_ALMUTEN      = "⑩ Almuten Figuris & Lord of Geniture"
CAT_TEMPERAMENT  = "⑪ Temperament (Humoral)"
CAT_PROFECTIONS  = "⑫ Annual Profections"
CAT_ZR           = "⑬ Zodiacal Releasing"
CAT_FIRDARIA     = "⑭ Firdaria"
CAT_DECENNIALS   = "⑮ Decennials"
CAT_DIRECTIONS   = "⑯ Primary Directions"
CAT_STARS        = "⑰ Fixed Stars & Parans"
CAT_MANSIONS     = "⑱ Lunar Mansions"
CAT_MUNDANE      = "⑲ Mundane Context"
CAT_MEDICAL      = "⑳ Medical / Decumbiture"
