"""Panel orchestrator: one birth input, every tradition we can source rules for.

A failing section never takes down the panel - it is recorded with its error and
the remaining traditions still render. That property matters because the panel is
meant to show honestly what each tradition can and cannot say.
"""

from __future__ import annotations

from typing import Any

from . import (
    babylonian,
    bazi,
    egyptian,
    hellenistic,
    mesoamerican,
    tibetan,
    timebase,
    vedic,
    vietnamese,
    western,
    ziwei,
)
from .types import BirthInput, TraditionSection

PANEL_VERSION = "0.1.0"


def _chart(birth: BirthInput, sidereal: bool):
    from ..calculator.main import ChartCalculator

    return ChartCalculator().calculate_chart(
        dt=birth.civil_datetime,
        city=birth.place_label,
        state="",
        latitude=birth.latitude,
        longitude=birth.longitude,
        house_system="W",
        zodiac_system="sidereal" if sidereal else "tropical",
        ayanamsa="lahiri" if sidereal else None,
        node_type="mean",
    )


def _guard(builder, tradition_id: str, display_name: str) -> TraditionSection:
    try:
        return builder()
    except Exception as exc:  # noqa: BLE001 - a broken section must not kill the panel
        from .types import EvidenceGrade

        section = TraditionSection(
            tradition_id=tradition_id,
            display_name=display_name,
            evidence_grade=EvidenceGrade.CONFIGURED,
            basis="Section failed to build.",
        )
        section.error = f"{type(exc).__name__}: {exc}"
        return section


def build_panel(birth: BirthInput) -> dict[str, Any]:
    bases = timebase.compute(birth.utc_datetime, birth.longitude)

    tropical_chart = _chart(birth, sidereal=False)
    sidereal_chart = _chart(birth, sidereal=True)

    # Hellenistic and Latin-European read the same sky by different procedure.
    # `western_section` remains the shared calculation basis that the Islamicate
    # and Jewish profiles hang off, since all four share the tropical core.
    western_section = _guard(
        lambda: western.build_western(birth, tropical_chart),
        "western_traditional",
        "Western traditional (shared core)",
    )
    hellenistic_section = _guard(
        lambda: hellenistic.build_hellenistic(birth, tropical_chart),
        "hellenistic",
        "Hellenistic (Greco-Roman)",
    )
    latin_section = _guard(
        lambda: hellenistic.build_latin_european(birth, tropical_chart),
        "latin_european",
        "Latin-European (medieval / Renaissance)",
    )
    bazi_section = _guard(
        lambda: bazi.build(birth, bases), "chinese_bazi", "Chinese BaZi (Four Pillars)"
    )
    pillar_year = None
    if not bazi_section.error:
        pillar_year = bazi_section.facts.get("pillar_year_used")

    sections = [
        western_section,
        hellenistic_section,
        latin_section,
        _guard(
            lambda: western.build_islamicate(birth, western_section),
            "islamicate_persian",
            "Islamicate / Persian",
        ),
        _guard(
            lambda: western.build_medieval_jewish(birth, western_section),
            "medieval_jewish",
            "Medieval Jewish (Ibn Ezra)",
        ),
        _guard(
            lambda: vedic.build(birth, sidereal_chart),
            "indian_jyotisha",
            "Vedic (Jyotisha)",
        ),
        bazi_section,
        _guard(
            lambda: tibetan.build(birth, pillar_year), "tibetan", "Tibetan year cycle"
        ),
        _guard(
            lambda: mesoamerican.build_maya(birth, bases), "maya", "Maya calendar"
        ),
        _guard(
            lambda: mesoamerican.build_nahua(birth, bases),
            "nahua_central_mexican",
            "Nahua tonalpohualli",
        ),
        _guard(
            lambda: babylonian.build(birth, bases, tropical_chart),
            "mesopotamian_babylonian",
            "Mesopotamian (Babylonian omen corpus)",
        ),
        _guard(
            lambda: egyptian.build(birth, bases),
            "pharaonic_egyptian",
            "Pharaonic Egyptian civil calendar",
        ),
        _guard(
            lambda: ziwei.build(birth, bases),
            "ziwei_doushu",
            "Zi Wei Dou Shu (Purple Star)",
        ),
        _guard(
            lambda: vietnamese.build(birth, bases),
            "vietnamese",
            "Vietnamese lunisolar calendar",
        ),
    ]

    panel: dict[str, Any] = {
        "panel_version": PANEL_VERSION,
        "historical_use_only": True,
        "customer_eligible": False,
        "birth": birth.to_dict(),
        "time_bases": {
            "utc": bases.utc.isoformat(),
            "julian_day_ut": round(bases.julian_day_ut, 6),
            "julian_day_number": bases.julian_day_number,
            "local_mean_time": bases.local_mean_time.strftime("%H:%M:%S"),
            "true_solar_time": bases.true_solar_time.strftime("%H:%M:%S"),
            "equation_of_time_minutes": round(bases.equation_of_time_minutes, 3),
        },
        "sections": [section.to_dict() for section in sections],
    }
    # Convergence reads only what the sections already computed, so it runs last
    # and is guarded: a failure here must never cost the reader their sections.
    try:
        from . import convergence

        panel["convergence"] = convergence.build(panel)
    except Exception as exc:  # noqa: BLE001
        panel["convergence_error"] = f"{type(exc).__name__}: {exc}"
    return panel
