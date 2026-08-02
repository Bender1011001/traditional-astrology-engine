from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any
from urllib.request import urlopen

import swisseph as swe


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fetch_missing_ephemeris_files(
    spec: dict[str, Any], ephe_dir: Path
) -> None:
    ephe_dir.mkdir(parents=True, exist_ok=True)
    for file_spec in spec["ephemeris_files"]:
        destination = ephe_dir / file_spec["name"]
        if destination.exists():
            continue
        partial = destination.with_suffix(destination.suffix + ".part")
        if partial.exists():
            partial.unlink()
        try:
            with urlopen(file_spec["official_url"], timeout=60) as response:
                with partial.open("wb") as stream:
                    while chunk := response.read(1024 * 1024):
                        stream.write(chunk)
            if partial.stat().st_size != file_spec["bytes"]:
                raise RuntimeError(
                    f"Downloaded ephemeris byte-count mismatch: {partial}"
                )
            actual_hash = _sha256(partial)
            if actual_hash != file_spec["sha256"]:
                raise RuntimeError(
                    f"Downloaded ephemeris SHA-256 mismatch for "
                    f"{file_spec['name']}: {actual_hash}"
                )
            partial.replace(destination)
        finally:
            if partial.exists():
                partial.unlink()


def _circular_difference_degrees(value: float, reference: float) -> float:
    return (value - reference + 180.0) % 360.0 - 180.0


def _verify_runtime(spec: dict[str, Any], ephe_dir: Path) -> None:
    profile = spec["calculation_profile"]
    actual_package = str(getattr(swe, "__version__", ""))
    actual_library = str(swe.version)
    if actual_package != profile["pyswisseph_package_version"]:
        raise RuntimeError(
            f"pyswisseph version mismatch: expected "
            f"{profile['pyswisseph_package_version']}, got {actual_package}"
        )
    if actual_library != profile["swisseph_library_version"]:
        raise RuntimeError(
            f"Swiss Ephemeris library mismatch: expected "
            f"{profile['swisseph_library_version']}, got {actual_library}"
        )
    for file_spec in spec["ephemeris_files"]:
        path = ephe_dir / file_spec["name"]
        if not path.is_file():
            raise FileNotFoundError(f"Required ephemeris file is missing: {path}")
        if path.stat().st_size != file_spec["bytes"]:
            raise RuntimeError(f"Ephemeris byte-count mismatch: {path}")
        actual_hash = _sha256(path)
        if actual_hash != file_spec["sha256"]:
            raise RuntimeError(
                f"Ephemeris SHA-256 mismatch for {path.name}: {actual_hash}"
            )


def _lock_tidal_acceleration(profile: dict[str, Any]) -> None:
    expected_name = profile["tidal_acceleration_constant"]
    if expected_name != "TIDAL_DE431":
        raise RuntimeError(f"Unsupported tidal acceleration constant: {expected_name}")
    expected_value = float(profile["tidal_acceleration_arcsec_per_century_squared"])
    library_value = float(swe.TIDAL_DE431)
    if not math.isclose(expected_value, library_value, abs_tol=1e-12):
        raise RuntimeError(
            f"Tidal acceleration mismatch: spec={expected_value}, "
            f"library={library_value}"
        )
    swe.set_tid_acc(library_value)
    if not math.isclose(float(swe.get_tid_acc()), expected_value, abs_tol=1e-12):
        raise RuntimeError("Swiss Ephemeris did not retain the requested tidal constant")


def _calculate_case(
    case: dict[str, Any],
    body_ids: dict[str, int],
    profile: dict[str, Any],
) -> dict[str, Any]:
    moment = case["julian_datetime"]
    jd_ut = swe.julday(
        moment["year"],
        moment["month"],
        moment["day"],
        moment["ut_hour"],
        swe.JUL_CAL,
    )
    correction = case["rochberg_longitude_correction_degrees"]
    rows: list[dict[str, Any]] = []
    for body, published in case["published_adjusted_longitudes"].items():
        body_id = body_ids[body]
        primary, primary_flags = swe.calc_ut(
            jd_ut, body_id, swe.FLG_SWIEPH | swe.FLG_SPEED
        )
        secondary, secondary_flags = swe.calc_ut(
            jd_ut, body_id, swe.FLG_MOSEPH | swe.FLG_SPEED
        )
        if not primary_flags & swe.FLG_SWIEPH:
            raise RuntimeError(
                f"Swiss Ephemeris silently fell back for {case['case_id']}:{body}; "
                f"return flags were {primary_flags}"
            )
        if not secondary_flags & swe.FLG_MOSEPH:
            raise RuntimeError(
                f"Moshier calculation was not used for {case['case_id']}:{body}; "
                f"return flags were {secondary_flags}"
            )
        adjusted = (primary[0] + correction) % 360.0
        residual = _circular_difference_degrees(adjusted, float(published))
        backend_difference = _circular_difference_degrees(primary[0], secondary[0])
        tolerance = (
            profile["moon_tolerance_degrees"]
            if body == "moon"
            else profile["planet_tolerance_degrees"]
        )
        rows.append(
            {
                "key": f"{case['case_id']}:{body}",
                "body": body,
                "published_adjusted_longitude_degrees": float(published),
                "primary_tropical_longitude_degrees": round(primary[0], 9),
                "primary_adjusted_longitude_degrees": round(adjusted, 9),
                "residual_degrees": round(residual, 9),
                "secondary_tropical_longitude_degrees": round(secondary[0], 9),
                "primary_secondary_difference_degrees": round(
                    backend_difference, 9
                ),
                "tolerance_degrees": tolerance,
                "within_tolerance": abs(residual) <= tolerance,
            }
        )
    return {
        "case_id": case["case_id"],
        "record_id": case["record_id"],
        "jd_ut": round(jd_ut, 9),
        "delta_t_seconds": round(swe.deltat(jd_ut) * 86400.0, 3),
        "rows": rows,
    }


def _summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [row for result in results for row in result["rows"]]
    planet_rows = [row for row in rows if row["body"] != "moon"]
    moon_rows = [row for row in rows if row["body"] == "moon"]
    failed = [row["key"] for row in rows if not row["within_tolerance"]]
    return {
        "position_checks": len(rows),
        "planet_checks": len(planet_rows),
        "moon_checks": len(moon_rows),
        "within_body_tolerance": sum(row["within_tolerance"] for row in rows),
        "planet_checks_within_tolerance": sum(
            row["within_tolerance"] for row in planet_rows
        ),
        "moon_checks_within_tolerance": sum(
            row["within_tolerance"] for row in moon_rows
        ),
        "out_of_tolerance_keys": failed,
        "maximum_planet_residual_degrees": round(
            max(abs(row["residual_degrees"]) for row in planet_rows), 4
        ),
        "maximum_primary_secondary_difference_degrees": round(
            max(
                abs(row["primary_secondary_difference_degrees"])
                for row in rows
            ),
            4,
        ),
    }


def _moon_residual_at_jd(
    jd_ut: float, correction: float, published: float
) -> float:
    primary, primary_flags = swe.calc_ut(
        jd_ut, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SPEED
    )
    if not primary_flags & swe.FLG_SWIEPH:
        raise RuntimeError(
            f"Swiss Ephemeris silently fell back during Moon time diagnostic: "
            f"return flags were {primary_flags}"
        )
    adjusted = (primary[0] + correction) % 360.0
    return _circular_difference_degrees(adjusted, published)


def _nearest_moon_time_shift_hours(case: dict[str, Any]) -> float:
    moment = case["julian_datetime"]
    center = swe.julday(
        moment["year"],
        moment["month"],
        moment["day"],
        moment["ut_hour"],
        swe.JUL_CAL,
    )
    correction = float(case["rochberg_longitude_correction_degrees"])
    published = float(case["published_adjusted_longitudes"]["moon"])
    start = center - 1.5
    end = center + 1.5
    steps = 720
    prior_jd = start
    prior_value = _moon_residual_at_jd(prior_jd, correction, published)
    roots: list[float] = []
    for index in range(1, steps + 1):
        current_jd = start + (end - start) * index / steps
        current_value = _moon_residual_at_jd(
            current_jd, correction, published
        )
        if prior_value == 0.0:
            roots.append(prior_jd)
        elif current_value == 0.0:
            roots.append(current_jd)
        elif prior_value * current_value < 0.0:
            lower = prior_jd
            upper = current_jd
            lower_value = prior_value
            for _ in range(60):
                midpoint = (lower + upper) / 2.0
                midpoint_value = _moon_residual_at_jd(
                    midpoint, correction, published
                )
                if lower_value * midpoint_value <= 0.0:
                    upper = midpoint
                else:
                    lower = midpoint
                    lower_value = midpoint_value
            roots.append((lower + upper) / 2.0)
        prior_jd = current_jd
        prior_value = current_value
    if not roots:
        raise RuntimeError(f"No local Moon root found for {case['case_id']}")
    nearest = min(roots, key=lambda value: abs(value - center))
    return round((nearest - center) * 24.0, 4)


def _moon_time_shift_diagnostics(spec: dict[str, Any]) -> dict[str, float]:
    return {
        case["case_id"]: _nearest_moon_time_shift_hours(case)
        for case in spec["cases"]
        if "moon" in case["published_adjusted_longitudes"]
    }


def _calculate_diagnostics(
    spec: dict[str, Any], body_ids: dict[str, int]
) -> dict[str, float]:
    values: dict[str, float] = {}
    for diagnostic in spec.get("diagnostic_variants", []):
        base = next(
            case
            for case in spec["cases"]
            if case["case_id"] == diagnostic["based_on_case_id"]
        )
        variant = dict(base)
        variant["case_id"] = diagnostic["case_id"]
        variant["julian_datetime"] = diagnostic["julian_datetime"]
        body = str(diagnostic["body"])
        variant["published_adjusted_longitudes"] = {
            body: base["published_adjusted_longitudes"][body]
        }
        result = _calculate_case(variant, body_ids, spec["calculation_profile"])
        values[str(diagnostic["summary_key"])] = round(
            result["rows"][0]["residual_degrees"], 4
        )
    return values


def _assert_expected(actual: dict[str, Any], expected: dict[str, Any]) -> None:
    if set(actual) != set(expected):
        raise AssertionError(
            f"Summary keys differ: expected {sorted(expected)}, got {sorted(actual)}"
        )
    for key, expected_value in expected.items():
        actual_value = actual[key]
        if isinstance(expected_value, float):
            if math.isclose(actual_value, expected_value, abs_tol=0.0001):
                continue
            raise AssertionError(
                f"Summary mismatch for {key}: expected {expected_value}, "
                f"got {actual_value}"
            )
        if actual_value != expected_value:
            raise AssertionError(
                f"Summary mismatch for {key}: expected {expected_value!r}, "
                f"got {actual_value!r}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Recompute a locked set of Rochberg 1998 longitude tables."
    )
    parser.add_argument(
        "--spec",
        type=Path,
        default=Path(__file__).with_name("rochberg_texts1_10_astronomy_spec.json"),
    )
    parser.add_argument("--ephe-dir", type=Path, required=True)
    parser.add_argument(
        "--fetch-missing",
        action="store_true",
        help=(
            "Download missing version-locked ephemeris files from their "
            "official URLs and verify byte counts and SHA-256 hashes."
        ),
    )
    parser.add_argument(
        "--full-results",
        action="store_true",
        help="Include every per-body result row instead of the validated summary only.",
    )
    args = parser.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    if args.fetch_missing:
        _fetch_missing_ephemeris_files(spec, args.ephe_dir)
    _verify_runtime(spec, args.ephe_dir)
    swe.set_ephe_path(str(args.ephe_dir.resolve()))
    _lock_tidal_acceleration(spec["calculation_profile"])
    results = [
        _calculate_case(case, spec["body_ids"], spec["calculation_profile"])
        for case in spec["cases"]
    ]
    summary = _summarize(results)
    summary["moon_nearest_time_shift_hours"] = _moon_time_shift_diagnostics(spec)
    summary.update(_calculate_diagnostics(spec, spec["body_ids"]))
    _assert_expected(summary, spec["expected_summary"])
    output: dict[str, Any] = {
        "status": "pass",
        "spec": str(args.spec),
        "ephemeris_directory": str(args.ephe_dir),
        "summary": summary,
    }
    if args.full_results:
        output["results"] = results
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
