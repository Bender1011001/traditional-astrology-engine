from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import swisseph as swe

import validate_rochberg_astronomy as astronomy_validator


def _event_map(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(event["event_id"]): event for event in spec["events"]}


def _jd(date: dict[str, Any], ut_hour: float = 0.0) -> float:
    return swe.julday(
        int(date["year"]),
        int(date["month"]),
        int(date["day"]),
        float(ut_hour),
        swe.JUL_CAL,
    )


def _ut_hour(jd_ut: float) -> float:
    return (jd_ut + 0.5 - math.floor(jd_ut + 0.5)) * 24.0


def _calendar_timestamp(jd_ut: float) -> dict[str, Any]:
    year, month, day, hour = swe.revjul(jd_ut, swe.JUL_CAL)
    return {
        "year": int(year),
        "month": int(month),
        "day": int(day),
        "ut_hour": round(hour, 6),
        "jd_ut": round(jd_ut, 9),
    }


def _circular_difference(value: float, reference: float) -> float:
    return (value - reference + 180.0) % 360.0 - 180.0


def _position(jd_ut: float, body: int) -> tuple[float, float]:
    position, flags = swe.calc_ut(jd_ut, body, swe.FLG_SWIEPH | swe.FLG_SPEED)
    if not flags & swe.FLG_SWIEPH:
        raise RuntimeError(
            "Swiss Ephemeris silently fell back while reconstructing Text 1; "
            f"return flags were {flags}"
        )
    return float(position[0]), float(position[3])


def _rise_set(
    day_jd: float,
    body: int,
    mode: int,
    geopos: tuple[float, float, float],
) -> float:
    event_mode = mode | swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION
    result, times = swe.rise_trans(
        day_jd,
        body,
        event_mode,
        geopos,
        0.0,
        15.0,
        swe.FLG_SWIEPH,
    )
    if result != 0:
        raise RuntimeError(
            f"No rise/set event found for body {body} from JD {day_jd}: {result}"
        )
    return float(times[0])


def _true_altitude(
    jd_ut: float,
    body: int,
    geopos: tuple[float, float, float],
) -> float:
    swe.set_topo(*geopos)
    equatorial, flags = swe.calc_ut(
        jd_ut,
        body,
        swe.FLG_SWIEPH | swe.FLG_EQUATORIAL | swe.FLG_TOPOCTR,
    )
    if not flags & swe.FLG_SWIEPH:
        raise RuntimeError(
            "Swiss Ephemeris silently fell back during altitude calculation; "
            f"return flags were {flags}"
        )
    _, true_altitude, _ = swe.azalt(
        jd_ut,
        swe.EQU2HOR,
        geopos,
        0.0,
        15.0,
        equatorial[:3],
    )
    return float(true_altitude)


def _speed_root(body: int, lower: float, upper: float) -> float:
    lower_speed = _position(lower, body)[1]
    upper_speed = _position(upper, body)[1]
    if lower_speed == 0.0:
        return lower
    if upper_speed == 0.0:
        return upper
    if lower_speed * upper_speed > 0.0:
        raise RuntimeError(
            f"Station root is not bracketed: {lower_speed} to {upper_speed}"
        )
    for _ in range(80):
        midpoint = (lower + upper) / 2.0
        midpoint_speed = _position(midpoint, body)[1]
        if lower_speed * midpoint_speed <= 0.0:
            upper = midpoint
        else:
            lower = midpoint
            lower_speed = midpoint_speed
    return (lower + upper) / 2.0


def _longitude_row(
    event_id: str,
    body_name: str,
    calculated: float,
    published: float,
    published_layer: str = "modern_tropical",
) -> dict[str, Any]:
    residual = _circular_difference(calculated, published)
    return {
        "event_id": event_id,
        "body": body_name,
        "published_layer": published_layer,
        "published_degrees": published,
        "calculated_degrees": round(calculated, 9),
        "residual_degrees": round(residual, 9),
    }


def _time_row(
    event_id: str,
    phenomenon: str,
    calculated_jd: float,
    published_hour: float,
) -> dict[str, Any]:
    calculated_hour = _ut_hour(calculated_jd)
    return {
        "event_id": event_id,
        "phenomenon": phenomenon,
        "published_ut_hour": published_hour,
        "calculated_ut_hour": round(calculated_hour, 9),
        "residual_hours": round(calculated_hour - published_hour, 9),
    }


def _calculate(spec: dict[str, Any]) -> dict[str, Any]:
    events = _event_map(spec)
    location = spec["calculation_profile"]["location"]
    geopos = (
        float(location["longitude_east_degrees"]),
        float(location["latitude_north_degrees"]),
        float(location["altitude_meters"]),
    )
    correction = float(
        spec["calculation_profile"][
            "rochberg_ancient_minus_modern_longitude_correction_degrees"
        ]
    )
    longitude_rows: list[dict[str, Any]] = []
    time_rows: list[dict[str, Any]] = []
    diagnostics: dict[str, Any] = {}

    mercury_first = events["text1.mercury_first_visibility_morning"]
    day = _jd(mercury_first["editor_julian_date"])
    sunrise = _rise_set(day, swe.SUN, swe.CALC_RISE, geopos)
    mercury_rise = _rise_set(day, swe.MERCURY, swe.CALC_RISE, geopos)
    sun_longitude = _position(sunrise, swe.SUN)[0]
    mercury_longitude = _position(sunrise, swe.MERCURY)[0]
    published = mercury_first["published_computation"]
    longitude_rows.extend(
        [
            _longitude_row(
                mercury_first["event_id"],
                "sun",
                sun_longitude,
                float(published["printed_summary_sun_longitude_degrees"])
                - correction,
                "printed_summary_minus_stated_correction",
            ),
            _longitude_row(
                mercury_first["event_id"],
                "mercury",
                mercury_longitude,
                float(published["later_stated_uncorrected_mercury_longitude_degrees"]),
                "explicitly_stated_uncorrected",
            ),
        ]
    )
    time_rows.extend(
        [
            _time_row(
                mercury_first["event_id"],
                "sunrise",
                sunrise,
                float(published["sunrise_ut_hour"]),
            ),
            _time_row(
                mercury_first["event_id"],
                "mercury_rise",
                mercury_rise,
                float(published["mercury_rise_ut_hour"]),
            ),
        ]
    )
    diagnostics["mercury_first_visibility"] = {
        "printed_mercury_summary_minus_correction_degrees": round(
            float(published["printed_summary_mercury_longitude_degrees"])
            - correction,
            9,
        ),
        "later_stated_uncorrected_mercury_degrees": float(
            published["later_stated_uncorrected_mercury_longitude_degrees"]
        ),
        "internal_layer_difference_degrees": round(
            float(published["printed_summary_mercury_longitude_degrees"])
            - correction
            - float(published["later_stated_uncorrected_mercury_longitude_degrees"]),
            9,
        ),
        "rise_before_sunrise_hours": round((sunrise - mercury_rise) * 24.0, 9),
        "mercury_true_altitude_at_sunrise_degrees": round(
            _true_altitude(sunrise, swe.MERCURY, geopos), 9
        ),
        "published_altitude_degrees": float(
            published["mercury_altitude_at_sunrise_degrees"]
        ),
        "visibility_verdict": None,
    }

    solstice_start = swe.julday(-410, 12, 20, 0.0, swe.JUL_CAL)
    solstice = float(swe.solcross_ut(270.0, solstice_start, swe.FLG_SWIEPH))
    diagnostics["winter_solstice"] = {
        "calculated_tropical_crossing": _calendar_timestamp(solstice),
        "comparison_to_tebetu_day_9": None,
        "reason": "The source treats X.9 as a fixed-scheme date; no independently reconstructed Julian date for X.9 is selected.",
    }

    lunar_days: list[dict[str, Any]] = []
    for day_number in range(13, 17):
        lunar_day = swe.julday(-409, 1, day_number, 0.0, swe.JUL_CAL)
        lunar_sunrise = _rise_set(lunar_day, swe.SUN, swe.CALC_RISE, geopos)
        moon_rise = _rise_set(
            lunar_day - 0.5, swe.MOON, swe.CALC_RISE, geopos
        )
        while moon_rise > lunar_sunrise:
            moon_rise = _rise_set(
                lunar_day - 1.5, swe.MOON, swe.CALC_RISE, geopos
            )
        sun = _position(lunar_sunrise, swe.SUN)[0]
        moon = _position(lunar_sunrise, swe.MOON)[0]
        lunar_days.append(
            {
                "julian_date": {"year": -409, "month": 1, "day": day_number},
                "moon_rise_before_sunrise_hours": round(
                    (lunar_sunrise - moon_rise) * 24.0, 9
                ),
                "absolute_geocentric_elongation_at_sunrise_degrees": round(
                    abs(_circular_difference(moon, sun)), 9
                ),
                "visibility_verdict": None,
            }
        )
    diagnostics["restored_last_lunar_visibility"] = {
        "candidate_diagnostics": lunar_days,
        "selected_julian_date": None,
        "reason": "The phenomenon is restored and the Babylonian calendar mapping is unresolved.",
    }

    morning_events = (
        (
            "text1.mercury_last_visibility_morning",
            swe.MERCURY,
            "mercury",
        ),
        ("text1.venus_last_visibility_morning", swe.VENUS, "venus"),
    )
    for event_id, body, body_name in morning_events:
        event = events[event_id]
        published = event["published_computation"]
        day = _jd(event["editor_julian_date"])
        sunrise = _rise_set(day, swe.SUN, swe.CALC_RISE, geopos)
        body_rise = _rise_set(day, body, swe.CALC_RISE, geopos)
        longitude_rows.extend(
            [
                _longitude_row(
                    event_id,
                    "sun",
                    _position(sunrise, swe.SUN)[0],
                    float(published["sun_longitude_modern_degrees"]),
                ),
                _longitude_row(
                    event_id,
                    body_name,
                    _position(sunrise, body)[0],
                    float(published[f"{body_name}_longitude_modern_degrees"]),
                ),
            ]
        )
        time_rows.extend(
            [
                _time_row(
                    event_id,
                    "sunrise",
                    sunrise,
                    float(published["sunrise_ut_hour"]),
                ),
                _time_row(
                    event_id,
                    f"{body_name}_rise",
                    body_rise,
                    float(published[f"{body_name}_rise_ut_hour"]),
                ),
            ]
        )
        diagnostics[event_id] = {
            "rise_before_sunrise_hours": round((sunrise - body_rise) * 24.0, 9),
            "visibility_verdict": None,
        }

    jupiter_station_event = events["text1.jupiter_second_station"]
    interval = jupiter_station_event["editor_julian_date_interval"]
    interval_start = _jd(interval["start"])
    interval_end = _jd(interval["end"]) + 1.0
    jupiter_station = _speed_root(swe.JUPITER, interval_start, interval_end)
    jupiter_station_longitude = _position(jupiter_station, swe.JUPITER)[0]
    jupiter_station_published = jupiter_station_event["published_computation"]
    longitude_rows.append(
        _longitude_row(
            jupiter_station_event["event_id"],
            "jupiter",
            jupiter_station_longitude,
            float(jupiter_station_published["jupiter_longitude_modern_degrees"]),
        )
    )
    direct_date = _jd(
        jupiter_station_published["returned_to_direct_motion_by_julian_day"]
    )
    direct_speed = _position(direct_date, swe.JUPITER)[1]
    diagnostics["jupiter_second_station"] = {
        "calculated_station": _calendar_timestamp(jupiter_station),
        "inside_published_date_interval": interval_start
        <= jupiter_station
        <= interval_end,
        "date_interval_boundary_error_days": 0.0
        if interval_start <= jupiter_station <= interval_end
        else min(
            abs(jupiter_station - interval_start),
            abs(jupiter_station - interval_end),
        ),
        "longitude_speed_on_october_17_degrees_per_day": round(direct_speed, 12),
        "direct_by_october_17": direct_speed > 0.0,
    }

    jupiter_last = events["text1.jupiter_last_visibility_evening"]
    published = jupiter_last["published_computation"]
    day = _jd(jupiter_last["editor_julian_date"])
    calculation_jd = day + float(published["calculation_ut_hour"]) / 24.0
    sunset = _rise_set(day, swe.SUN, swe.CALC_SET, geopos)
    jupiter_set = _rise_set(day, swe.JUPITER, swe.CALC_SET, geopos)
    longitude_rows.extend(
        [
            _longitude_row(
                jupiter_last["event_id"],
                "sun",
                _position(calculation_jd, swe.SUN)[0],
                float(published["sun_longitude_modern_degrees"]),
            ),
            _longitude_row(
                jupiter_last["event_id"],
                "jupiter",
                _position(calculation_jd, swe.JUPITER)[0],
                float(published["jupiter_longitude_modern_degrees"]),
            ),
        ]
    )
    time_rows.extend(
        [
            _time_row(
                jupiter_last["event_id"],
                "sunset",
                sunset,
                float(published["sunset_ut_hour"]),
            ),
            _time_row(
                jupiter_last["event_id"],
                "jupiter_set",
                jupiter_set,
                float(published["jupiter_set_ut_hour"]),
            ),
        ]
    )
    diagnostics["jupiter_last_visibility"] = {
        "set_after_sunset_hours": round((jupiter_set - sunset) * 24.0, 9),
        "visibility_verdict": None,
    }

    saturn_events = (
        ("text1.saturn_first_visibility_observed", 2.0),
        ("text1.saturn_first_visibility_ideal_alternate", None),
    )
    for event_id, calculation_hour in saturn_events:
        event = events[event_id]
        published = event["published_computation"]
        day = _jd(event["editor_julian_date"])
        sunrise = _rise_set(day, swe.SUN, swe.CALC_RISE, geopos)
        saturn_rise = _rise_set(day, swe.SATURN, swe.CALC_RISE, geopos)
        calculation_jd = (
            day + calculation_hour / 24.0
            if calculation_hour is not None
            else sunrise
        )
        longitude_rows.extend(
            [
                _longitude_row(
                    event_id,
                    "sun",
                    _position(calculation_jd, swe.SUN)[0],
                    float(published["sun_longitude_modern_degrees"]),
                ),
                _longitude_row(
                    event_id,
                    "saturn",
                    _position(calculation_jd, swe.SATURN)[0],
                    float(published["saturn_longitude_modern_degrees"]),
                ),
            ]
        )
        time_rows.extend(
            [
                _time_row(
                    event_id,
                    "sunrise",
                    sunrise,
                    float(published["sunrise_ut_hour"]),
                ),
                _time_row(
                    event_id,
                    "saturn_rise",
                    saturn_rise,
                    float(published["saturn_rise_ut_hour"]),
                ),
            ]
        )
        event_diagnostic: dict[str, Any] = {
            "rise_before_sunrise_hours": round(
                (sunrise - saturn_rise) * 24.0, 9
            ),
            "visibility_verdict": None,
        }
        if calculation_hour is not None:
            event_diagnostic.update(
                {
                    "sun_true_altitude_degrees": round(
                        _true_altitude(calculation_jd, swe.SUN, geopos), 9
                    ),
                    "saturn_true_altitude_degrees": round(
                        _true_altitude(calculation_jd, swe.SATURN, geopos), 9
                    ),
                    "published_sun_altitude_degrees": float(
                        published["sun_altitude_degrees"]
                    ),
                    "published_saturn_altitude_degrees": float(
                        published["saturn_altitude_degrees"]
                    ),
                }
            )
        diagnostics[event_id] = event_diagnostic

    saturn_station = _speed_root(
        swe.SATURN,
        swe.julday(-410, 10, 25, 0.0, swe.JUL_CAL),
        swe.julday(-410, 11, 10, 0.0, swe.JUL_CAL),
    )
    derived_ix7 = swe.julday(-410, 12, 5, 0.0, swe.JUL_CAL) - 8.0
    station_conflict_days = abs(derived_ix7 - saturn_station)
    diagnostics["saturn_first_station_calendar_conflict"] = {
        "calculated_station": _calendar_timestamp(saturn_station),
        "strict_same_month_ix7_derived_from_ix15": _calendar_timestamp(derived_ix7),
        "absolute_conflict_days": round(station_conflict_days, 9),
        "calendar_date_selected_for_engine": None,
    }

    saturn_acronychal = events["text1.saturn_acronychal_rising"]
    published = saturn_acronychal["published_computation"]
    day = _jd(saturn_acronychal["editor_julian_date"])
    sunset = _rise_set(day, swe.SUN, swe.CALC_SET, geopos)
    saturn_rise = _rise_set(day, swe.SATURN, swe.CALC_RISE, geopos)
    sun_longitude = _position(sunset, swe.SUN)[0]
    saturn_longitude = _position(sunset, swe.SATURN)[0]
    elongation = abs(_circular_difference(saturn_longitude, sun_longitude))
    longitude_rows.extend(
        [
            _longitude_row(
                saturn_acronychal["event_id"],
                "sun",
                sun_longitude,
                float(published["sun_longitude_modern_degrees"]),
            ),
            _longitude_row(
                saturn_acronychal["event_id"],
                "saturn",
                saturn_longitude,
                float(published["saturn_longitude_modern_degrees"]),
            ),
        ]
    )
    diagnostics["saturn_acronychal_rising"] = {
        "sunset_ut_hour": round(_ut_hour(sunset), 9),
        "saturn_rise_ut_hour": round(_ut_hour(saturn_rise), 9),
        "saturn_rise_after_sunset_hours": round((saturn_rise - sunset) * 24.0, 9),
        "calculated_elongation_degrees": round(elongation, 9),
        "published_elongation_degrees": float(published["elongation_degrees"]),
        "elongation_residual_degrees": round(
            elongation - float(published["elongation_degrees"]), 9
        ),
        "exact_180_degree_opposition": False,
    }

    gates = spec["exploratory_gates"]
    maximum_longitude_residual = max(
        abs(row["residual_degrees"]) for row in longitude_rows
    )
    maximum_time_residual = max(abs(row["residual_hours"]) for row in time_rows)
    elongation_residual = abs(
        diagnostics["saturn_acronychal_rising"]["elongation_residual_degrees"]
    )
    station_boundary_error = diagnostics["jupiter_second_station"][
        "date_interval_boundary_error_days"
    ]
    checks = {
        "published_modern_longitudes_within_exploratory_gate": maximum_longitude_residual
        <= float(gates["maximum_published_modern_longitude_residual_degrees"]),
        "rise_set_times_within_exploratory_gate": maximum_time_residual
        <= float(gates["maximum_rise_or_set_time_residual_hours"]),
        "published_elongation_within_exploratory_gate": elongation_residual
        <= float(gates["maximum_published_elongation_residual_degrees"]),
        "jupiter_station_within_published_interval": station_boundary_error
        <= float(gates["maximum_station_interval_boundary_error_days"]),
        "jupiter_direct_by_published_date": diagnostics["jupiter_second_station"][
            "direct_by_october_17"
        ],
        "saturn_same_month_conflict_reproduced": station_conflict_days
        >= float(gates["saturn_station_same_month_conflict_minimum_days"]),
        "no_visibility_verdicts_generated": True,
        "no_birth_chart_positions_inferred": True,
    }
    if not all(checks.values()):
        failed = sorted(key for key, value in checks.items() if not value)
        raise AssertionError(f"Text 1 event reconstruction failed: {failed}")

    return {
        "status": "pass_with_documented_calendar_and_editorial_conflicts",
        "summary": {
            "event_records": len(events),
            "published_longitude_checks": len(longitude_rows),
            "published_rise_set_checks": len(time_rows),
            "maximum_published_longitude_residual_degrees": round(
                maximum_longitude_residual, 6
            ),
            "maximum_published_rise_set_residual_hours": round(
                maximum_time_residual, 6
            ),
            "saturn_acronychal_elongation_residual_degrees": round(
                elongation_residual, 6
            ),
            "jupiter_station": _calendar_timestamp(jupiter_station),
            "saturn_station": _calendar_timestamp(saturn_station),
            "saturn_same_month_conflict_days": round(station_conflict_days, 6),
            "tropical_winter_solstice": _calendar_timestamp(solstice),
            "visibility_verdicts": 0,
            "birth_chart_position_inferences": 0,
        },
        "checks": checks,
        "longitude_comparisons": longitude_rows,
        "rise_set_comparisons": time_rows,
        "diagnostics": diagnostics,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Reconstruct Rochberg 1998 Text 1 as an event chronology without "
            "turning visibility or calendar uncertainty into natal-chart facts."
        )
    )
    parser.add_argument(
        "--spec",
        type=Path,
        default=Path(__file__).with_name("rochberg_text1_event_spec.json"),
    )
    parser.add_argument(
        "--astronomy-spec",
        type=Path,
        default=Path(__file__).with_name(
            "rochberg_texts1_10_astronomy_spec.json"
        ),
    )
    parser.add_argument("--ephe-dir", type=Path, required=True)
    parser.add_argument(
        "--fetch-missing",
        action="store_true",
        help="Fetch missing version-locked ephemeris files and verify their hashes.",
    )
    parser.add_argument(
        "--full-results",
        action="store_true",
        help="Emit all comparisons and diagnostics instead of the summary only.",
    )
    args = parser.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    astronomy_spec = json.loads(args.astronomy_spec.read_text(encoding="utf-8"))
    if args.fetch_missing:
        astronomy_validator._fetch_missing_ephemeris_files(  # noqa: SLF001
            astronomy_spec, args.ephe_dir
        )
    astronomy_validator._verify_runtime(  # noqa: SLF001
        astronomy_spec, args.ephe_dir
    )
    swe.set_ephe_path(str(args.ephe_dir.resolve()))
    astronomy_validator._lock_tidal_acceleration(  # noqa: SLF001
        astronomy_spec["calculation_profile"]
    )
    results = _calculate(spec)
    output: dict[str, Any] = {
        "status": results["status"],
        "spec": str(args.spec),
        "astronomy_spec": str(args.astronomy_spec),
        "ephemeris_directory": str(args.ephe_dir),
        "summary": results["summary"],
        "checks": results["checks"],
    }
    if args.full_results:
        output.update(
            {
                "longitude_comparisons": results["longitude_comparisons"],
                "rise_set_comparisons": results["rise_set_comparisons"],
                "diagnostics": results["diagnostics"],
            }
        )
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
