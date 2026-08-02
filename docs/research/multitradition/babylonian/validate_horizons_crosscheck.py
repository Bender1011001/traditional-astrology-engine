from __future__ import annotations

import argparse
import json
import math
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import swisseph as swe

import validate_rochberg_astronomy as rochberg


def _julian_calendar_jd(year: int, month: int, day: int, hour: float) -> float:
    adjusted_year = year
    adjusted_month = month
    if adjusted_month <= 2:
        adjusted_year -= 1
        adjusted_month += 12
    return (
        math.floor(365.25 * (adjusted_year + 4716))
        + math.floor(30.6001 * (adjusted_month + 1))
        + day
        + hour / 24.0
        - 1524.5
    )


def _request_horizons(
    crosscheck: dict[str, Any],
    body: str,
    jd_values: list[float],
    time_type: str,
) -> tuple[dict[float, dict[str, float]], dict[str, str]]:
    if time_type not in {"UT", "TT"}:
        raise ValueError(f"Unsupported Horizons time type: {time_type}")
    target = crosscheck["target_ids"][body]["command"]
    tlist = " ".join(f"'{value:.12f}'" for value in sorted(jd_values))
    quantities = "30,31" if time_type == "UT" else "31"
    profile = crosscheck["query_profile"]
    parameters = {
        "format": "json",
        "COMMAND": f"'{target}'",
        "OBJ_DATA": "'NO'",
        "MAKE_EPHEM": "'YES'",
        "EPHEM_TYPE": f"'{profile['ephemeris_type']}'",
        "CENTER": f"'{profile['center']}'",
        "TLIST": tlist,
        "TLIST_TYPE": f"'{profile['time_list_type']}'",
        "TIME_TYPE": f"'{time_type}'",
        "TIME_DIGITS": "'FRACSEC'",
        "QUANTITIES": f"'{quantities}'",
        "REF_SYSTEM": f"'{profile['reference_system']}'",
        "CAL_FORMAT": f"'{profile['calendar_format']}'",
        "CAL_TYPE": f"'{profile['calendar_type']}'",
        "ANG_FORMAT": f"'{profile['angle_format']}'",
        "CSV_FORMAT": "'YES'",
        "APPARENT": f"'{profile['apparent_mode']}'",
        "EXTRA_PREC": "'YES'" if profile["extra_precision"] else "'NO'",
    }
    url = crosscheck["api"]["endpoint"] + "?" + urllib.parse.urlencode(parameters)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "AstrologyEngineResearch/1.0 JPL-Horizons-validation"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.load(response)
    if payload.get("error"):
        raise RuntimeError(f"Horizons error for {body}/{time_type}: {payload['error']}")
    signature = payload.get("signature") or {}
    expected_source = crosscheck["api"]["expected_signature_source"]
    if signature.get("source") != expected_source:
        raise RuntimeError(
            f"Unexpected Horizons signature source: {signature.get('source')!r}"
        )
    result = payload.get("result", "")
    if "$$SOE" not in result or "$$EOE" not in result:
        raise RuntimeError(f"Horizons response has no ephemeris block: {body}/{time_type}")
    block = result.split("$$SOE", 1)[1].split("$$EOE", 1)[0]
    parsed: dict[float, dict[str, float]] = {}
    for line in block.splitlines():
        if not line.strip():
            continue
        columns = [column.strip() for column in line.split(",")]
        jd = float(columns[0])
        if time_type == "UT":
            parsed[jd] = {
                "delta_t_seconds": float(columns[3]),
                "longitude_degrees": float(columns[4]),
            }
        else:
            parsed[jd] = {"longitude_degrees": float(columns[3])}
    if len(parsed) != len(set(jd_values)):
        raise RuntimeError(
            f"Horizons row-count mismatch for {body}/{time_type}: "
            f"expected {len(set(jd_values))}, got {len(parsed)}"
        )
    return parsed, {str(key): str(value) for key, value in signature.items()}


def _nearest_row(
    rows: dict[float, dict[str, float]], jd: float
) -> dict[str, float]:
    matched_jd = min(rows, key=lambda candidate: abs(candidate - jd))
    if abs(matched_jd - jd) > 1e-8:
        raise RuntimeError(
            f"Horizons JD mismatch: requested {jd:.12f}, got {matched_jd:.12f}"
        )
    return rows[matched_jd]


def _build_swiss_rows(
    rochberg_spec: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in rochberg_spec["cases"]:
        moment = case["julian_datetime"]
        jd_ut = _julian_calendar_jd(
            moment["year"], moment["month"], moment["day"], moment["ut_hour"]
        )
        swiss_jd = swe.julday(
            moment["year"],
            moment["month"],
            moment["day"],
            moment["ut_hour"],
            swe.JUL_CAL,
        )
        if not math.isclose(jd_ut, swiss_jd, abs_tol=1e-10):
            raise RuntimeError(
                f"Independent Julian-date conversion mismatch for {case['case_id']}: "
                f"{jd_ut} versus {swiss_jd}"
            )
        delta_t_days = swe.deltat(jd_ut)
        jd_tt = jd_ut + delta_t_days
        for body in case["published_adjusted_longitudes"]:
            body_id = rochberg_spec["body_ids"][body]
            position_ut, flags_ut = swe.calc_ut(
                jd_ut, body_id, swe.FLG_SWIEPH | swe.FLG_SPEED
            )
            position_tt, flags_tt = swe.calc(
                jd_tt, body_id, swe.FLG_SWIEPH | swe.FLG_SPEED
            )
            if not flags_ut & swe.FLG_SWIEPH or not flags_tt & swe.FLG_SWIEPH:
                raise RuntimeError(
                    f"Swiss Ephemeris fallback for {case['case_id']}:{body}"
                )
            rows.append(
                {
                    "key": f"{case['case_id']}:{body}",
                    "case_id": case["case_id"],
                    "body": body,
                    "jd_ut": jd_ut,
                    "jd_tt": jd_tt,
                    "swiss_delta_t_seconds": delta_t_days * 86400.0,
                    "swiss_ut_longitude_degrees": position_ut[0],
                    "swiss_tt_longitude_degrees": position_tt[0],
                }
            )
    return rows


def _maximum_absolute(rows: list[dict[str, Any]], field: str) -> float:
    return max(abs(float(row[field])) for row in rows)


def _mean_absolute(rows: list[dict[str, Any]], field: str) -> float:
    return sum(abs(float(row[field])) for row in rows) / len(rows)


def _summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    planets = [row for row in rows if row["body"] != "moon"]
    moons = [row for row in rows if row["body"] == "moon"]
    delta_t_by_case: dict[str, float] = {}
    for row in rows:
        delta_t_by_case[row["case_id"]] = row["horizons_delta_t_seconds"] - row[
            "swiss_delta_t_seconds"
        ]
    delta_values = list(delta_t_by_case.values())
    return {
        "position_comparisons": len(rows),
        "ut_same_label": {
            "maximum_absolute_difference_degrees": round(
                _maximum_absolute(rows, "ut_difference_degrees"), 7
            ),
            "maximum_planet_difference_degrees": round(
                _maximum_absolute(planets, "ut_difference_degrees"), 7
            ),
            "maximum_moon_difference_degrees": round(
                _maximum_absolute(moons, "ut_difference_degrees"), 7
            ),
            "mean_absolute_difference_degrees": round(
                _mean_absolute(rows, "ut_difference_degrees"), 7
            ),
        },
        "tt_same_instant": {
            "maximum_absolute_difference_degrees": round(
                _maximum_absolute(rows, "tt_difference_degrees"), 7
            ),
            "maximum_planet_difference_degrees": round(
                _maximum_absolute(planets, "tt_difference_degrees"), 7
            ),
            "maximum_moon_difference_degrees": round(
                _maximum_absolute(moons, "tt_difference_degrees"), 7
            ),
            "mean_absolute_difference_degrees": round(
                _mean_absolute(rows, "tt_difference_degrees"), 7
            ),
        },
        "delta_t": {
            "unique_instants": len(delta_values),
            "minimum_horizons_minus_swiss_seconds": round(min(delta_values), 3),
            "maximum_horizons_minus_swiss_seconds": round(max(delta_values), 3),
            "mean_horizons_minus_swiss_seconds": round(
                sum(delta_values) / len(delta_values), 3
            ),
        },
    }


def _assert_drift_gates(summary: dict[str, Any], crosscheck: dict[str, Any]) -> None:
    gates = crosscheck["live_drift_gates"]
    if summary["position_comparisons"] != gates["position_comparisons"]:
        raise AssertionError("Horizons comparison count changed")
    checks = (
        (
            summary["ut_same_label"]["maximum_absolute_difference_degrees"],
            gates["ut_maximum_absolute_difference_degrees"],
            "UT maximum difference",
        ),
        (
            summary["ut_same_label"]["maximum_planet_difference_degrees"],
            gates["ut_maximum_planet_difference_degrees"],
            "UT maximum planet difference",
        ),
        (
            summary["tt_same_instant"]["maximum_absolute_difference_degrees"],
            gates["tt_maximum_absolute_difference_degrees"],
            "TT maximum difference",
        ),
    )
    for actual, maximum, label in checks:
        if actual > maximum:
            raise AssertionError(f"{label} exceeded drift gate: {actual} > {maximum}")
    delta = summary["delta_t"]
    if delta["minimum_horizons_minus_swiss_seconds"] < gates[
        "delta_t_difference_seconds_minimum"
    ]:
        raise AssertionError("Horizons/Swiss minimum Delta-T difference drifted")
    if delta["maximum_horizons_minus_swiss_seconds"] > gates[
        "delta_t_difference_seconds_maximum"
    ]:
        raise AssertionError("Horizons/Swiss maximum Delta-T difference drifted")


def main() -> int:
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Cross-check Rochberg astronomy against NASA/JPL Horizons."
    )
    parser.add_argument(
        "--spec",
        type=Path,
        default=directory / "jpl_horizons_crosscheck_spec.json",
    )
    parser.add_argument(
        "--rochberg-spec",
        type=Path,
        default=directory / "rochberg_texts1_10_astronomy_spec.json",
    )
    parser.add_argument("--ephe-dir", type=Path, required=True)
    parser.add_argument("--fetch-missing", action="store_true")
    parser.add_argument("--full-results", action="store_true")
    args = parser.parse_args()

    crosscheck = json.loads(args.spec.read_text(encoding="utf-8"))
    rochberg_spec = json.loads(args.rochberg_spec.read_text(encoding="utf-8"))
    if args.fetch_missing:
        rochberg._fetch_missing_ephemeris_files(rochberg_spec, args.ephe_dir)
    rochberg._verify_runtime(rochberg_spec, args.ephe_dir)
    swe.set_ephe_path(str(args.ephe_dir.resolve()))
    rochberg._lock_tidal_acceleration(rochberg_spec["calculation_profile"])
    rows = _build_swiss_rows(rochberg_spec)

    signatures: set[tuple[tuple[str, str], ...]] = set()
    for body in rochberg_spec["body_ids"]:
        body_rows = [row for row in rows if row["body"] == body]
        ut_values, ut_signature = _request_horizons(
            crosscheck, body, [row["jd_ut"] for row in body_rows], "UT"
        )
        tt_values, tt_signature = _request_horizons(
            crosscheck, body, [row["jd_tt"] for row in body_rows], "TT"
        )
        signatures.add(tuple(sorted(ut_signature.items())))
        signatures.add(tuple(sorted(tt_signature.items())))
        for row in body_rows:
            horizons_ut = _nearest_row(ut_values, row["jd_ut"])
            horizons_tt = _nearest_row(tt_values, row["jd_tt"])
            row["horizons_delta_t_seconds"] = horizons_ut["delta_t_seconds"]
            row["horizons_ut_longitude_degrees"] = horizons_ut[
                "longitude_degrees"
            ]
            row["horizons_tt_longitude_degrees"] = horizons_tt[
                "longitude_degrees"
            ]
            row["ut_difference_degrees"] = rochberg._circular_difference_degrees(
                row["horizons_ut_longitude_degrees"],
                row["swiss_ut_longitude_degrees"],
            )
            row["tt_difference_degrees"] = rochberg._circular_difference_degrees(
                row["horizons_tt_longitude_degrees"],
                row["swiss_tt_longitude_degrees"],
            )

    if len(signatures) != 1:
        raise RuntimeError(f"Horizons signatures changed within run: {signatures}")
    signature = dict(next(iter(signatures)))
    summary = _summarize(rows)
    _assert_drift_gates(summary, crosscheck)
    output: dict[str, Any] = {
        "status": "pass",
        "horizons_signature": signature,
        "summary": summary,
        "gate_status": crosscheck["gate_status"],
    }
    if args.full_results:
        output["results"] = rows
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
