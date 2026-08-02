"""Vietnamese lunisolar calendar section.

The validated pack carries five rules for the modern Vietnamese calendar: a
month begins on the local civil day containing the astronomical New Moon; the
winter solstice falls in month 11; twelve months between month-11 anchors is a
normal year; thirteen makes the first following month without a principal solar
term intercalary; and every one of those civil dates is assigned on Vietnam's
local day, not Beijing's.

That last rule is the whole point of the pack, and it is not pedantry. In the
worked 1985 case the two calendars diverge by an entire month - Tet on 21
January against a Chinese New Year on 20 February - because a New Moon and a
solstice each land within an hour of local midnight. This section reproduces all
five of the pack's published vectors before reporting anything about the birth.

What the pack refuses to supply is the astronomy: it names no ephemeris, no
timescale and no tolerance, and warns that the 105-degree reference longitude is
not a substitute for statutory timezone history. Those are product choices here,
disclosed as such, which is why this section is graded configured rather than
validated.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

import swisseph as swe

from .timebase import TimeBases
from .types import BirthInput, DisclosureKind, EvidenceGrade, TraditionSection

RESEARCH_ROOT = (
    Path(__file__).resolve().parents[3] / "docs" / "research" / "multitradition"
)
VN_MANIFEST = RESEARCH_ROOT / "vietnamese" / "calendar_rule_manifest.json"
VN_VECTORS = RESEARCH_ROOT / "vietnamese" / "calendar_validation_vectors.json"

# Vietnam's civil day on the pack's documented 105E reference longitude.
VN_OFFSET_HOURS = 7.0
# Beijing's civil day, used only for the divergence contrast the pack's own
# vectors require. No Chinese calendar result is emitted under a Vietnamese label.
BEIJING_OFFSET_HOURS = 8.0

MEAN_SYNODIC_MONTH = 29.530588861
LUNATION_EPOCH_JD = 2451550.09766  # k = 0 New Moon, 2000-01-06
MEAN_ELONGATION_RATE = 12.190749  # degrees/day, Moon minus Sun
MEAN_SOLAR_RATE = 0.9856473  # degrees/day
# A configured tolerance: events this close to Vietnamese local midnight can be
# pushed across the day boundary by ephemeris or civil-time uncertainty.
BOUNDARY_TOLERANCE_MINUTES = 5.0


@lru_cache(maxsize=2)
def _pack(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sun_longitude(jd: float) -> float:
    return swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)[0][0]


def _moon_longitude(jd: float) -> float:
    return swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH)[0][0]


@lru_cache(maxsize=512)
def _new_moon(k: int) -> float:
    """UT Julian day of the k-th New Moon, refined from the mean lunation."""
    jd = LUNATION_EPOCH_JD + MEAN_SYNODIC_MONTH * k
    for _ in range(12):
        delta = ((_moon_longitude(jd) - _sun_longitude(jd) + 180.0) % 360.0) - 180.0
        step = delta / MEAN_ELONGATION_RATE
        jd -= step
        if abs(step) < 1e-7:
            break
    return jd


def _solar_term(target_degrees: float, seed_jd: float) -> float:
    """UT Julian day at which apparent solar longitude reaches target_degrees."""
    jd = seed_jd
    for _ in range(12):
        delta = ((_sun_longitude(jd) - target_degrees + 180.0) % 360.0) - 180.0
        step = delta / MEAN_SOLAR_RATE
        jd -= step
        if abs(step) < 1e-7:
            break
    return jd


@lru_cache(maxsize=64)
def _winter_solstice(year: int) -> float:
    return _solar_term(270.0, swe.julday(year, 12, 21, 12.0))


def _lunation_index(jd: float) -> int:
    return round((jd - LUNATION_EPOCH_JD) / MEAN_SYNODIC_MONTH)


def _utc(jd: float) -> datetime:
    year, month, day, hour = swe.revjul(jd)
    return datetime(year, month, day) + timedelta(hours=hour)


def _civil_date(jd: float, offset_hours: float) -> date:
    return (_utc(jd) + timedelta(hours=offset_hours)).date()


def _midnight_jd(civil_day: date, offset_hours: float) -> float:
    return (
        swe.julday(civil_day.year, civil_day.month, civil_day.day, 0.0)
        - offset_hours / 24.0
    )


def _minutes_from_local_midnight(jd: float, offset_hours: float) -> float:
    local = _utc(jd) + timedelta(hours=offset_hours)
    since = local.hour * 60 + local.minute + local.second / 60
    return min(since, 24 * 60 - since)


@dataclass(frozen=True)
class LunarYear:
    """One month-11 anchor to the next, on a named civil-day basis."""

    anchor_year: int
    offset_hours: float
    solstice_jd: float
    next_solstice_jd: float
    month_starts: tuple[date, ...]  # month_count + 1 entries; last is the next anchor
    month_start_jds: tuple[float, ...]
    numbers: tuple[int, ...]
    intercalary: tuple[bool, ...]
    principal_terms: tuple[tuple[float, float], ...]  # (target degrees, jd)
    intercalary_index: int | None

    @property
    def month_count(self) -> int:
        return len(self.numbers)

    @property
    def is_leap(self) -> bool:
        return self.intercalary_index is not None


@lru_cache(maxsize=32)
def _month11_anchor(year: int, offset_hours: float) -> tuple[date, float, float]:
    """Start of the lunar month containing this year's winter solstice."""
    solstice_jd = _winter_solstice(year)
    solstice_date = _civil_date(solstice_jd, offset_hours)
    k = _lunation_index(solstice_jd)
    for probe in (k + 1, k, k - 1, k - 2):
        new_moon_jd = _new_moon(probe)
        if _civil_date(new_moon_jd, offset_hours) <= solstice_date:
            return _civil_date(new_moon_jd, offset_hours), new_moon_jd, solstice_jd
    raise ValueError(f"no New Moon found at or before the {year} winter solstice")


@lru_cache(maxsize=32)
def _lunar_year(anchor_year: int, offset_hours: float) -> LunarYear:
    start_date, start_jd, solstice_jd = _month11_anchor(anchor_year, offset_hours)
    end_date, end_jd, next_solstice_jd = _month11_anchor(anchor_year + 1, offset_hours)

    starts: list[date] = []
    start_jds: list[float] = []
    k0 = _lunation_index(start_jd)
    step = 0
    while True:
        new_moon_jd = _new_moon(k0 + step)
        civil = _civil_date(new_moon_jd, offset_hours)
        if civil >= end_date:
            break
        starts.append(civil)
        start_jds.append(new_moon_jd)
        step += 1
    starts.append(end_date)
    start_jds.append(end_jd)

    # Fourteen principal terms from the anchor solstice cover any 12 or 13 month
    # span. Instants are kept, not just containment flags, because the pack
    # requires the absent term and its neighbours to appear in the trace.
    terms: list[tuple[float, float]] = []
    for index in range(14):
        target = (270.0 + 30.0 * index) % 360.0
        terms.append(
            (target, _solar_term(target, solstice_jd + 30.4368 * index))
        )

    intercalary_index: int | None = None
    if len(starts) - 1 == 13:
        for index in range(1, len(starts) - 1):
            window = (starts[index], starts[index + 1])
            if not _terms_in_window(terms, window, offset_hours):
                intercalary_index = index
                break

    numbers: list[int] = []
    intercalary: list[bool] = []
    for index in range(len(starts) - 1):
        if index == 0:
            numbers.append(11)
            intercalary.append(False)
        elif index == intercalary_index:
            numbers.append(numbers[-1])
            intercalary.append(True)
        else:
            numbers.append(numbers[-1] % 12 + 1)
            intercalary.append(False)

    return LunarYear(
        anchor_year=anchor_year,
        offset_hours=offset_hours,
        solstice_jd=solstice_jd,
        next_solstice_jd=next_solstice_jd,
        month_starts=tuple(starts),
        month_start_jds=tuple(start_jds),
        numbers=tuple(numbers),
        intercalary=tuple(intercalary),
        principal_terms=tuple(terms),
        intercalary_index=intercalary_index,
    )


def _terms_in_window(
    terms: tuple[tuple[float, float], ...] | list[tuple[float, float]],
    window: tuple[date, date],
    offset_hours: float,
) -> list[tuple[float, float]]:
    begin, end = window
    return [
        term
        for term in terms
        if begin <= _civil_date(term[1], offset_hours) < end
    ]


def lunar_date(civil_day: date, offset_hours: float = VN_OFFSET_HOURS) -> dict[str, Any]:
    """Lunar month number, intercalary flag and day for one local civil date."""
    year = _lunar_year(civil_day.year, offset_hours)
    if civil_day < year.month_starts[0]:
        year = _lunar_year(civil_day.year - 1, offset_hours)
    index = max(
        i for i in range(year.month_count) if year.month_starts[i] <= civil_day
    )
    start = year.month_starts[index]
    end = year.month_starts[index + 1] - timedelta(days=1)
    return {
        "lunar_year": year,
        "month_index": index,
        "month_number": year.numbers[index],
        "is_intercalary": year.intercalary[index],
        "day": (civil_day - start).days + 1,
        "month_start_civil_date": start,
        "month_end_civil_date": end,
        "month_length_days": (year.month_starts[index + 1] - start).days,
    }


def _tet(year: LunarYear) -> date | None:
    for index in range(year.month_count):
        if year.numbers[index] == 1 and not year.intercalary[index]:
            return year.month_starts[index]
    return None


def build(birth: BirthInput, bases: TimeBases) -> TraditionSection:
    manifest = _pack(VN_MANIFEST)
    section = TraditionSection(
        tradition_id="vietnamese",
        display_name="Vietnamese lunisolar calendar",
        evidence_grade=EvidenceGrade.CONFIGURED,
        basis=(
            "Month starts, the month-11 solstice anchor, month numbering and the "
            "no-principal-term intercalation rule from the validated modern "
            "Vietnamese calendar pack, computed on Vietnam's civil day with a "
            "product-supplied ephemeris the pack declines to name."
        ),
    )
    section.disclose(
        DisclosureKind.SOURCE,
        "Rule provenance and grade",
        "The five calculation rules come from "
        f"{manifest['source_pack_id']}. The pack's own evidence grade is D: the "
        "inspected technical page is explicit and carries worked 1984-1985 "
        "tables, but its authorship and statutory authority are not established "
        "and independent recomputation, almanac comparison and Vietnamese review "
        "remain pending. All five of its published vectors are reproduced below.",
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Ephemeris and timescale",
        "New Moon instants are found where apparent geocentric Moon-Sun elongation "
        "reaches zero, and principal terms where apparent solar longitude reaches a "
        "multiple of 30 degrees, both from the Swiss Ephemeris in UT with civil "
        "dates on the proleptic Gregorian calendar. The pack names no ephemeris, "
        "timescale or numerical tolerance, so this is the product's choice.",
        ("JPL DE440 directly", "VSOP87/ELP mean-element tables",
         "Published Vietnamese almanac tables"),
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Civil-day basis",
        "Every event is dated on UTC+7, from the 105-degrees-east reference "
        "longitude documented on the inspected page, applied uniformly across all "
        "years. The pack warns in terms that a reference longitude is not a "
        "substitute for statutory timezone history, and that the valid period and "
        "precise role of 105E require Vietnamese authority - so for any year "
        "outside the modern statutory profile this is an assumption, not a "
        "sourced fact.",
        ("Vietnamese statutory zone history, including UTC+8 periods",
         "Beijing UTC+8 basis (rejected by the pack)"),
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Applying a Vietnamese calendar to a birth outside Vietnam",
        "The Vietnamese calendar is a civil calendar defined on Vietnam's own day, "
        "so the birth instant is converted to Vietnam's civil date rather than the "
        "birth place's. Where the two differ, both are shown. This is a projection "
        "of a place-specific calendar onto a foreign birth, and is reported as "
        "such.",
        ("Refuse the section for non-Vietnamese births",
         "Date the events on the birth place's civil day (this would no longer be "
         "the Vietnamese calendar)"),
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Boundary tolerance",
        f"Events falling within {BOUNDARY_TOLERANCE_MINUTES:g} minutes of "
        "Vietnamese local midnight are flagged, because ephemeris or civil-time "
        "uncertainty can push them across the day boundary and move a month label. "
        "The pack requires alternates rather than a silent choice in that case; "
        "the threshold itself is a product setting.",
        ("A tighter threshold tied to a stated ephemeris error budget",
         "No tolerance check at all"),
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Historical royal calendars",
        "Refused. This is the modern calculation profile. The pack states it "
        "cannot be applied proleptically to a historical royal calendar without a "
        "regime-specific source, and the Vietnamese audit requires a "
        "calendar_regime_id and a dated almanac concordance for any historical "
        "conversion, because Vietnamese dynastic calendars could and did differ "
        "from contemporary Chinese ones. For a birth predating the modern profile "
        "the date below is the modern rule run backward, not the calendar that was "
        "in force.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Any Vietnamese natal reading",
        "Refused. This is a calendar fact and nothing more. The surviving corpus "
        "cannot support a Vietnamese natal system: Tu Vi and Tu Binh each require "
        "their own named editions, construction tables and worked charts, none of "
        "which exist here, and the audit forbids relabeling a Chinese BaZi or Zi "
        "Wei result as Vietnamese. No sexagenary year name, no star chart and no "
        "personality claim is emitted here.",
    )

    vn_civil_date = (bases.utc + timedelta(hours=VN_OFFSET_HOURS)).date()
    resolved = lunar_date(vn_civil_date)
    year: LunarYear = resolved["lunar_year"]
    index = resolved["month_index"]

    month_start_jd = year.month_start_jds[index]
    tet = _tet(year)
    boundary = _boundary_trace(year, index)

    if boundary["closest_margin_minutes"] < BOUNDARY_TOLERANCE_MINUTES:
        section.disclose(
            DisclosureKind.FORK,
            "Day-boundary sensitivity",
            f"{boundary['closest_event']} falls "
            f"{boundary['closest_margin_minutes']:.1f} minutes from Vietnamese "
            "local midnight. A different ephemeris or civil-time rule could place "
            "it on the adjacent day and shift this month's label, so the result "
            "below is one of two candidates rather than a settled date.",
            ("The adjacent civil day for that event",),
        )

    section.facts = {
        "calendar_profile": {
            "school_id": manifest["school_id"],
            "reference_longitude": "105E",
            "civil_offset_hours": VN_OFFSET_HOURS,
            "ephemeris": "Swiss Ephemeris (swisseph), apparent geocentric, UT",
            "civil_calendar": "proleptic Gregorian",
            "implementation_status_in_pack": manifest["implementation_status"],
        },
        "civil_dates": {
            "birth_place_civil_date": birth.civil_date.isoformat(),
            "vietnamese_civil_date": vn_civil_date.isoformat(),
            "differs_from_birth_place_day": vn_civil_date != birth.civil_date,
            "utc": bases.utc.isoformat(),
        },
        "lunar_date": {
            "month_number": resolved["month_number"],
            "is_intercalary": resolved["is_intercalary"],
            "day": resolved["day"],
            "label": (
                ("intercalary month " if resolved["is_intercalary"] else "month ")
                + str(resolved["month_number"])
                + ", day "
                + str(resolved["day"])
            ),
            "month_start_civil_date": resolved["month_start_civil_date"].isoformat(),
            "month_end_civil_date": resolved["month_end_civil_date"].isoformat(),
            "month_length_days": resolved["month_length_days"],
        },
        "month_start_new_moon": {
            "utc": _utc(month_start_jd).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "hanoi_civil_date": _civil_date(month_start_jd, VN_OFFSET_HOURS).isoformat(),
            "beijing_civil_date": _civil_date(
                month_start_jd, BEIJING_OFFSET_HOURS
            ).isoformat(),
            "local_day_differs_from_beijing": (
                _civil_date(month_start_jd, VN_OFFSET_HOURS)
                != _civil_date(month_start_jd, BEIJING_OFFSET_HOURS)
            ),
        },
        "lunar_year_structure": {
            "month11_anchor_start": year.month_starts[0].isoformat(),
            "next_month11_anchor_start": year.month_starts[-1].isoformat(),
            "month_count": year.month_count,
            "is_leap_year": year.is_leap,
            "anchor_solstice_utc": _utc(year.solstice_jd).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "anchor_solstice_hanoi_date": _civil_date(
                year.solstice_jd, VN_OFFSET_HOURS
            ).isoformat(),
            "anchor_solstice_beijing_date": _civil_date(
                year.solstice_jd, BEIJING_OFFSET_HOURS
            ).isoformat(),
            "tet_in_this_anchor_span": tet.isoformat() if tet else None,
            "birth_precedes_that_tet": bool(tet and vn_civil_date < tet),
        },
        "intercalation_evidence": _intercalation_evidence(year),
        "boundary_trace": boundary,
        "worked_example_selfcheck": _worked_example_selfcheck(),
    }
    section.reading = [
        "What this section is: a date, computed under a named set of modern rules, "
        "on Vietnam's civil day rather than anyone else's.",
        "The Vietnamese civil day is doing real work here, not decoration. In the "
        "pack's own 1984-85 worked case a New Moon lands at 23:47 Hanoi time and a "
        "winter solstice at 23:22 - both a few minutes short of midnight - and "
        "those minutes are why Tet 1985 fell on 21 January in Vietnam while "
        "Chinese New Year fell on 20 February. The engine reproduces both dates "
        "above from the rules alone.",
        "What this section is not: a reading. A Vietnamese natal system would need "
        "its own named edition and construction tables, which the corpus does not "
        "have, and a Chinese chart wearing a Vietnamese label would be worse than "
        "nothing.",
    ]
    return section


def _intercalation_evidence(year: LunarYear) -> dict[str, Any]:
    """Why this year is or is not leap, with the deciding term instants shown."""
    if not year.is_leap:
        return {
            "is_leap_year": False,
            "months_between_month11_anchors": year.month_count,
            "rule": "twelve months between anchors: sequential 11, 12, 1..10",
        }
    index = year.intercalary_index
    assert index is not None
    window = (year.month_starts[index], year.month_starts[index + 1])
    previous = _terms_in_window(
        year.principal_terms, (year.month_starts[index - 1], window[0]), VN_OFFSET_HOURS
    )
    following = _terms_in_window(
        year.principal_terms,
        (window[1], year.month_starts[min(index + 2, year.month_count)]),
        VN_OFFSET_HOURS,
    )
    return {
        "is_leap_year": True,
        "months_between_month11_anchors": year.month_count,
        "rule": (
            "thirteen months between anchors: the first month after the anchor "
            "containing no principal term repeats the preceding month number"
        ),
        "intercalary_month_number": year.numbers[index],
        "intercalary_start_civil_date": window[0].isoformat(),
        "intercalary_end_civil_date": (window[1] - timedelta(days=1)).isoformat(),
        "principal_terms_inside_it": len(
            _terms_in_window(year.principal_terms, window, VN_OFFSET_HOURS)
        ),
        "preceding_principal_term": _term_row(previous[-1]) if previous else None,
        "following_principal_term": _term_row(following[0]) if following else None,
    }


def _term_row(term: tuple[float, float]) -> dict[str, Any]:
    target, jd = term
    return {
        "solar_longitude_degrees": target,
        "utc": _utc(jd).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "hanoi_civil_date": _civil_date(jd, VN_OFFSET_HOURS).isoformat(),
    }


def _boundary_trace(year: LunarYear, index: int) -> dict[str, Any]:
    """How close the events that fix this month's label sit to local midnight."""
    events: list[tuple[str, float]] = [
        ("the New Moon opening this lunar month", year.month_start_jds[index]),
        ("the New Moon opening the next lunar month", year.month_start_jds[index + 1]),
        ("the winter solstice anchoring month 11", year.solstice_jd),
        ("the winter solstice closing the span", year.next_solstice_jd),
    ]
    if year.intercalary_index is not None:
        leap_index = year.intercalary_index
        neighbours = _terms_in_window(
            year.principal_terms,
            (
                year.month_starts[leap_index - 1],
                year.month_starts[min(leap_index + 2, year.month_count)],
            ),
            VN_OFFSET_HOURS,
        )
        for target, jd in neighbours:
            events.append(
                (f"the principal term at solar longitude {target:g} degrees", jd)
            )
    margins = [
        (label, _minutes_from_local_midnight(jd, VN_OFFSET_HOURS))
        for label, jd in events
    ]
    label, minutes = min(margins, key=lambda row: row[1])
    return {
        "tolerance_minutes": BOUNDARY_TOLERANCE_MINUTES,
        "closest_event": label,
        "closest_margin_minutes": round(minutes, 2),
        "within_tolerance": minutes < BOUNDARY_TOLERANCE_MINUTES,
        "all_margins_minutes": {row[0]: round(row[1], 2) for row in margins},
    }


def _worked_example_selfcheck() -> dict[str, Any]:
    """Reproduce every published vector in the pack. Pass or fail is reported."""
    vectors = {v["vector_id"]: v for v in _pack(VN_VECTORS)["vectors"]}
    results: dict[str, Any] = {}

    vietnam_1984 = _lunar_year(1984, VN_OFFSET_HOURS)
    beijing_1984 = _lunar_year(1984, BEIJING_OFFSET_HOURS)

    new_moon_jd = _new_moon(_lunation_index(swe.julday(1984, 5, 30, 16.8)))
    expected = vectors["vietnam.calendar.new_moon_local_day_divergence.1984_05_30"][
        "expected"
    ]
    computed = {
        "hanoi_civil_date": _civil_date(new_moon_jd, VN_OFFSET_HOURS).isoformat(),
        "beijing_civil_date": _civil_date(
            new_moon_jd, BEIJING_OFFSET_HOURS
        ).isoformat(),
    }
    results["new_moon_local_day_divergence_1984_05_30"] = {
        "computed_utc": _utc(new_moon_jd).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "computed": computed,
        "expected": expected,
        "matches": computed == expected,
    }

    solstice_jd = _winter_solstice(1984)
    expected = vectors["vietnam.calendar.solstice_local_day_divergence.1984_12_21"][
        "expected"
    ]
    computed = {
        "hanoi_civil_date": _civil_date(solstice_jd, VN_OFFSET_HOURS).isoformat(),
        "beijing_civil_date": _civil_date(solstice_jd, BEIJING_OFFSET_HOURS).isoformat(),
    }
    results["solstice_local_day_divergence_1984_12_21"] = {
        "computed_utc": _utc(solstice_jd).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "computed": computed,
        "expected": expected,
        "matches": computed == expected,
    }

    expected = vectors["vietnam.calendar.month11_1984"]["expected"]
    computed = {
        "month_number": vietnam_1984.numbers[0],
        "start_civil_date": vietnam_1984.month_starts[0].isoformat(),
        "end_civil_date": (
            vietnam_1984.month_starts[1] - timedelta(days=1)
        ).isoformat(),
    }
    results["month11_1984"] = {
        "computed": computed,
        "expected": expected,
        "matches": computed == expected,
    }

    expected = vectors["vietnam.calendar.new_year_divergence.1985"]["expected"]
    vietnam_tet, beijing_tet = _tet(vietnam_1984), _tet(beijing_1984)
    computed = {
        "vietnamese_new_year": vietnam_tet.isoformat() if vietnam_tet else None,
        "chinese_new_year": beijing_tet.isoformat() if beijing_tet else None,
    }
    results["new_year_divergence_1985"] = {
        "computed": computed,
        "expected": expected,
        "matches": computed == expected,
        "note": (
            "The Chinese date is the same five rules evaluated on Beijing's civil "
            "day, which is how the pack's own vector states the contrast. It is "
            "not an authoritative Chinese calendar result."
        ),
    }

    expected = vectors["vietnam.calendar.intercalary_month.1985"]["expected"]
    leap_index = vietnam_1984.intercalary_index
    computed = {
        "is_leap_year": vietnam_1984.is_leap,
        "intercalary_month_start": (
            vietnam_1984.month_starts[leap_index].isoformat()
            if leap_index is not None
            else None
        ),
        "intercalary_month_end": (
            (vietnam_1984.month_starts[leap_index + 1] - timedelta(days=1)).isoformat()
            if leap_index is not None
            else None
        ),
    }
    results["intercalary_month_1985"] = {
        "computed": computed,
        "expected": {
            key: expected[key]
            for key in ("is_leap_year", "intercalary_month_start",
                        "intercalary_month_end")
        },
        "matches": computed == {
            key: expected[key]
            for key in ("is_leap_year", "intercalary_month_start",
                        "intercalary_month_end")
        },
    }

    results["all_published_vectors_reproduced"] = all(
        row["matches"] for row in results.values() if isinstance(row, dict)
    )
    return results
