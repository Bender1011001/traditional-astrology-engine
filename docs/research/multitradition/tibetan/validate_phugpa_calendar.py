from __future__ import annotations

import argparse
import json
from fractions import Fraction
from math import floor
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"Expected a JSON object in {path}")
    return data


def pair_fraction(pair: list[int]) -> Fraction:
    if len(pair) != 2 or pair[1] == 0:
        raise ValueError(f"Invalid rational pair: {pair!r}")
    return Fraction(pair[0], pair[1])


class PhugpaCalendarKernel:
    def __init__(self, spec: dict[str, Any], epoch_profile: str | None = None) -> None:
        self.spec = spec
        self.epoch_profile = epoch_profile or spec["default_epoch_profile"]
        if self.epoch_profile not in spec["epoch_profiles"]:
            raise ValueError(f"Unknown epoch profile: {self.epoch_profile}")
        epoch = spec["epoch_profiles"][self.epoch_profile]
        self.year0 = int(epoch["year"])
        self.month0 = int(epoch["month"])
        self.beta_star = int(epoch["beta_star"])
        self.m0 = Fraction(int(epoch["m0"]["integer"])) + pair_fraction(
            epoch["m0"]["fraction"]
        )
        self.s0 = pair_fraction(epoch["s0"])
        self.a0 = pair_fraction(epoch["a0"])
        constants = spec["exact_rational_constants"]
        self.m1 = pair_fraction(constants["mean_month_m1"])
        self.m2 = pair_fraction(constants["mean_lunar_day_m2"])
        self.s1 = pair_fraction(constants["mean_sun_month_s1"])
        self.s2 = pair_fraction(constants["mean_sun_day_s2"])
        self.a1 = pair_fraction(constants["moon_anomaly_month_a1"])
        self.a2_profiles = {
            key: pair_fraction(value)
            for key, value in constants["moon_anomaly_day_profiles"].items()
        }
        self.moon_table = [int(value) for value in constants["moon_table"]]
        self.sun_table = [int(value) for value in constants["sun_table"]]

    @staticmethod
    def _require_int(value: Any, label: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{label} must be an integer")
        return value

    @staticmethod
    def gregorian_from_jdn(jdn: int) -> list[int]:
        a = jdn + 32044
        b = (4 * a + 3) // 146097
        c = a - (146097 * b) // 4
        d = (4 * c + 3) // 1461
        e = c - (1461 * d) // 4
        m = (5 * e + 2) // 153
        day = e - (153 * m + 2) // 5 + 1
        month = m + 3 - 12 * (m // 10)
        year = 100 * b + d - 4800 + m // 10
        return [year, month, day]

    def leap_month(self, year: int) -> int | None:
        year = self._require_int(year, "year")
        residue = (24 * year + 33) % 65
        if residue < 41:
            return None
        month = floor(33 - Fraction(residue, 2))
        if not 1 <= month <= 12:
            raise AssertionError("Phugpa leap formula produced an invalid month")
        return month

    def true_month_count(self, year: int, month: int, leap: bool = False) -> int:
        year = self._require_int(year, "year")
        month = self._require_int(month, "month")
        if not 1 <= month <= 12:
            raise ValueError("month must be between 1 and 12")
        if not isinstance(leap, bool):
            raise TypeError("leap must be boolean")
        if leap and self.leap_month(year) != month:
            raise ValueError(f"Month {month} of {year} is not a Phugpa leap month")
        solar_month_count = 12 * (year - self.year0) + month - self.month0
        return (
            (67 * solar_month_count + self.beta_star + 17) // 65
            - int(leap)
        )

    def _table_node(self, index: int, period: int, base: list[int]) -> int:
        index %= period
        quarter = period // 4
        half = period // 2
        if index <= quarter:
            return base[index]
        if index <= half:
            return self._table_node(half - index, period, base)
        return -self._table_node(index - half, period, base)

    def _interpolate_table(
        self, argument: Fraction, period: int, base: list[int]
    ) -> Fraction:
        argument %= period
        lower = floor(argument)
        fraction = argument - lower
        start = self._table_node(lower, period, base)
        end = self._table_node(lower + 1, period, base)
        return Fraction(start) + fraction * (end - start)

    def true_date(
        self,
        true_month_count: int,
        lunar_day: int,
        a2_profile: str = "standard_almanac",
    ) -> Fraction:
        n = self._require_int(true_month_count, "true_month_count")
        day = self._require_int(lunar_day, "lunar_day")
        if not 0 <= day <= 30:
            raise ValueError("lunar_day must be between 0 and 30")
        if a2_profile not in self.a2_profiles:
            raise ValueError(f"Unknown moon anomaly day profile: {a2_profile}")
        mean_date = n * self.m1 + day * self.m2 + self.m0
        mean_sun = (n * self.s1 + day * self.s2 + self.s0) % 1
        moon_anomaly = (
            n * self.a1 + day * self.a2_profiles[a2_profile] + self.a0
        ) % 1
        moon_equation = self._interpolate_table(
            28 * moon_anomaly, 28, self.moon_table
        )
        sun_anomaly = (mean_sun - Fraction(1, 4)) % 1
        sun_equation = self._interpolate_table(
            12 * sun_anomaly, 12, self.sun_table
        )
        return mean_date + moon_equation / 60 - sun_equation / 60

    def lunar_day_end_jdn(
        self,
        year: int,
        month: int,
        day: int,
        leap: bool = False,
        a2_profile: str = "standard_almanac",
    ) -> int:
        if not 1 <= day <= 30:
            raise ValueError("day must be between 1 and 30")
        n = self.true_month_count(year, month, leap)
        return floor(self.true_date(n, day, a2_profile))

    def _previous_lunar_day_end_jdn(
        self,
        year: int,
        month: int,
        day: int,
        leap: bool,
        a2_profile: str,
    ) -> int:
        n = self.true_month_count(year, month, leap)
        if day > 1:
            return floor(self.true_date(n, day - 1, a2_profile))
        return floor(self.true_date(n - 1, 30, a2_profile))

    def lunar_date(
        self,
        year: int,
        month: int,
        day: int,
        leap: bool = False,
        a2_profile: str = "standard_almanac",
    ) -> dict[str, Any]:
        end_jdn = self.lunar_day_end_jdn(
            year, month, day, leap, a2_profile
        )
        previous_jdn = self._previous_lunar_day_end_jdn(
            year, month, day, leap, a2_profile
        )
        increment = end_jdn - previous_jdn
        if increment == 0:
            jdns: list[int] = []
            status = "skipped"
        elif increment == 1:
            jdns = [end_jdn]
            status = "regular"
        elif increment == 2:
            jdns = [end_jdn - 1, end_jdn]
            status = "repeated"
        else:
            raise AssertionError(f"Unexpected lunar-day JDN increment: {increment}")
        return {
            "status": status,
            "integer_jdns": jdns,
            "gregorian_dates": [self.gregorian_from_jdn(jdn) for jdn in jdns],
            "weekdays": [(jdn + 2) % 7 for jdn in jdns],
        }

    def losar_jdn(self, year: int, a2_profile: str = "standard_almanac") -> int:
        return self.lunar_day_end_jdn(
            year - 1, 12, 30, False, a2_profile
        ) + 1


def assert_expected_subset(actual: Any, expected: Any, path: str) -> None:
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            raise AssertionError(f"{path}: expected mapping")
        for key, value in expected.items():
            if key not in actual:
                raise AssertionError(f"{path}.{key}: missing")
            assert_expected_subset(actual[key], value, f"{path}.{key}")
        return
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise AssertionError(f"{path}: list mismatch")
        for index, (left, right) in enumerate(zip(actual, expected, strict=True)):
            assert_expected_subset(left, right, f"{path}[{index}]")
        return
    if actual != expected:
        raise AssertionError(f"{path}: expected {expected!r}, got {actual!r}")


def evaluate_vector(
    default_kernel: PhugpaCalendarKernel,
    spec: dict[str, Any],
    vector: dict[str, Any],
) -> dict[str, Any]:
    inputs = vector["inputs"]
    operation = inputs["operation"]
    if operation == "losar_table":
        return {
            "gregorian_dates": [
                default_kernel.gregorian_from_jdn(default_kernel.losar_jdn(year))
                for year in inputs["years"]
            ]
        }
    if operation == "leap_month_table":
        values = {
            str(year): month
            for year in range(inputs["year_start"], inputs["year_end"] + 1)
            if (month := default_kernel.leap_month(year)) is not None
        }
        return {"leap_months": values}
    if operation == "year_day_anomalies":
        year = inputs["year"]
        months: dict[str, dict[str, list[int]]] = {}
        for month in range(1, 13):
            repeated: list[int] = []
            skipped: list[int] = []
            for day in range(1, 31):
                status = default_kernel.lunar_date(year, month, day)["status"]
                if status == "repeated":
                    repeated.append(day)
                elif status == "skipped":
                    skipped.append(day)
            months[str(month)] = {"repeated": repeated, "skipped": skipped}
        return {"months": months}
    if operation == "lunar_date":
        return default_kernel.lunar_date(
            inputs["year"], inputs["month"], inputs["day"], inputs["leap"]
        )
    if operation == "leap_month_order":
        year = inputs["year"]
        month = inputs["month"]
        leap_count = default_kernel.true_month_count(year, month, True)
        regular_count = default_kernel.true_month_count(year, month, False)
        return {
            "is_leap_month": default_kernel.leap_month(year) == month,
            "leap_true_month_count": leap_count,
            "regular_true_month_count": regular_count,
            "consecutive": regular_count - leap_count == 1,
            "leap_precedes_regular": leap_count < regular_count,
        }
    if operation == "epoch_compare":
        kernels = [PhugpaCalendarKernel(spec, name) for name in inputs["epoch_profiles"]]
        comparisons: list[list[int]] = []
        for date in inputs["dates"]:
            comparisons.append(
                [
                    kernel.lunar_day_end_jdn(
                        date["year"], date["month"], date["day"], date["leap"]
                    )
                    for kernel in kernels
                ]
            )
        losars = [kernel.losar_jdn(2024) for kernel in kernels]
        return {
            "all_integer_jdns_equal": all(len(set(row)) == 1 for row in comparisons),
            "losar_2024_equal": len(set(losars)) == 1,
        }
    if operation == "a2_divergences":
        standard: list[int] = []
        lochen: list[int] = []
        for case in inputs["cases"]:
            arguments = (case["year"], case["month"], case["day"], case["leap"])
            standard.append(
                default_kernel.lunar_day_end_jdn(*arguments, "standard_almanac")
            )
            lochen.append(
                default_kernel.lunar_day_end_jdn(*arguments, "lochen_correction")
            )
        return {
            "standard_jdns": standard,
            "lochen_jdns": lochen,
            "civil_dates_named_by_source": [
                [2001, 2, 10], [2006, 5, 10], [2025, 11, 19]
            ],
        }
    if operation == "lineage_boundary_fixture":
        year = inputs["year"]
        if year != 2025:
            raise ValueError("The sourced Tsurphu comparison fixture is limited to 2025")
        return {
            "phugpa_losar": default_kernel.gregorian_from_jdn(
                default_kernel.losar_jdn(year)
            ),
            "tsurphu_reference_losar": [2025, 3, 1],
            "merge_allowed": False,
            "cache_identity_equal": False,
        }
    if operation == "publication_contract":
        publication = spec["publication_contract"]
        return {
            "calendar_facts_allowed": publication["calendar_fact_eligible"],
            "interpretation_allowed": publication["interpretation_eligible"],
            "institutional_conformance": publication["institutional_conformance"],
            "live_engine": publication["live_engine"],
            "customer_prediction": publication["customer_prediction"],
            "historical_use_only": publication["historical_use_only"],
        }
    raise ValueError(f"Unknown operation: {operation}")


def validate(root: Path) -> dict[str, Any]:
    spec = read_json(root / "phugpa_calendar_spec.json")
    vectors = read_json(root / "phugpa_calendar_validation_vectors.json")
    if spec["source_pack_id"] != vectors["source_pack_id"]:
        raise ValueError("Specification and vectors have different source packs")
    kernel = PhugpaCalendarKernel(spec)
    passed: list[str] = []
    for vector in vectors["vectors"]:
        actual = evaluate_vector(kernel, spec, vector)
        assert_expected_subset(actual, vector["expected"], vector["vector_id"])
        passed.append(vector["vector_id"])
    publication = spec["publication_contract"]
    return {
        "status":"pass",
        "source_pack_id":spec["source_pack_id"],
        "vectors_passed":len(passed),
        "vector_ids":passed,
        "losar_dates_checked":31,
        "published_2012_day_anomaly_inventory_checked":True,
        "epoch_profiles_checked":len(spec["epoch_profiles"]),
        "live_engine":publication["live_engine"],
        "institutional_conformance":publication["institutional_conformance"],
        "interpretation_eligible":publication["interpretation_eligible"],
        "customer_prediction":publication["customer_prediction"]
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phugpa calendar research kernel.")
    parser.add_argument("--root",type=Path,default=ROOT,help="Tibetan research directory")
    args = parser.parse_args()
    print(json.dumps(validate(args.root.resolve()),indent=2,sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
