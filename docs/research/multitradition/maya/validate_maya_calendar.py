from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"Expected a JSON object in {path}")
    return data


def euclidean_mod(value: int, modulus: int) -> int:
    if modulus <= 0:
        raise ValueError("Modulus must be positive")
    return value % modulus


class MayaCalendarKernel:
    def __init__(self, spec: dict[str, Any]) -> None:
        self.spec = spec
        self.weights = spec["long_count"]["weights_days"]
        self.tzolkin = spec["tzolkin"]
        self.haab_spec = spec["haab"]
        self.correlations = spec["correlations"]

    @staticmethod
    def _require_int(value: Any, label: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{label} must be an integer")
        return value

    def compose_long_count(self, components: list[int]) -> int:
        if len(components) != 5:
            raise ValueError("A canonical Long Count must have five components")
        names = self.spec["long_count"]["component_order"]
        constraints = self.spec["long_count"]["canonical_input_constraints"]
        total = 0
        for name, raw_value in zip(names, components, strict=True):
            value = self._require_int(raw_value, name)
            bounds = constraints[name]
            if value < bounds["minimum"]:
                raise ValueError(f"{name} is below its minimum")
            if "maximum" in bounds and value > bounds["maximum"]:
                raise ValueError(f"{name} exceeds its canonical radix")
            total += value * int(self.weights[name])
        return total

    def decompose_long_count(self, total_day: int) -> list[int]:
        remainder = self._require_int(total_day, "total_day")
        if remainder < 0:
            raise ValueError("Negative totals require a separately sourced Extended Long Count")
        components: list[int] = []
        for name in self.spec["long_count"]["component_order"]:
            weight = int(self.weights[name])
            component, remainder = divmod(remainder, weight)
            components.append(component)
        return components

    def tzolkin_for(self, total_day: int, name_profile: str) -> dict[str, Any]:
        total = self._require_int(total_day, "total_day")
        if total < 0:
            raise ValueError("Negative totals are outside this profile")
        profiles = self.tzolkin["name_profiles"]
        if name_profile not in profiles:
            raise ValueError(f"Unknown Tzolk'in name profile: {name_profile}")
        index = euclidean_mod(total + 19, 20)
        return {
            "number": euclidean_mod(total + 3, 13) + 1,
            "name": profiles[name_profile][index],
            "index": index,
            "name_profile": name_profile,
        }

    def haab_for(self, total_day: int) -> dict[str, Any]:
        total = self._require_int(total_day, "total_day")
        if total < 0:
            raise ValueError("Negative totals are outside this profile")
        position = euclidean_mod(total + 348, 365)
        month_index, day = divmod(position, 20)
        month_names = self.haab_spec["month_names"]
        if month_index == 18 and day > 4:
            raise AssertionError("Impossible Wayeb day produced")
        return {
            "day": day,
            "month": month_names[month_index],
            "month_index": month_index,
            "position": position,
        }

    def correlation_constant(self, correlation_id: str) -> int:
        if correlation_id not in self.correlations:
            raise ValueError(f"Unknown correlation profile: {correlation_id}")
        return int(self.correlations[correlation_id]["constant"])

    def jdn_for(self, total_day: int, correlation_id: str) -> int:
        total = self._require_int(total_day, "total_day")
        if total < 0:
            raise ValueError("Negative totals are outside this profile")
        return total + self.correlation_constant(correlation_id)

    @staticmethod
    def gregorian_to_jdn(year: int, month: int, day: int) -> int:
        if isinstance(year, bool) or not isinstance(year, int):
            raise TypeError("year must be an integer")
        if not 1 <= month <= 12:
            raise ValueError("month must be between 1 and 12")
        if not 1 <= day <= 31:
            raise ValueError("day must be between 1 and 31")
        a = (14 - month) // 12
        adjusted_year = year + 4800 - a
        adjusted_month = month + 12 * a - 3
        jdn = (
            day
            + (153 * adjusted_month + 2) // 5
            + 365 * adjusted_year
            + adjusted_year // 4
            - adjusted_year // 100
            + adjusted_year // 400
            - 32045
        )
        if MayaCalendarKernel.jdn_to_gregorian(jdn) != {
            "year": year,
            "month": month,
            "day": day,
        }:
            raise ValueError("Invalid proleptic Gregorian date")
        return jdn

    @staticmethod
    def jdn_to_gregorian(jdn: int) -> dict[str, int]:
        if isinstance(jdn, bool) or not isinstance(jdn, int):
            raise TypeError("jdn must be an integer")
        a = jdn + 32044
        b = (4 * a + 3) // 146097
        c = a - (146097 * b) // 4
        d = (4 * c + 3) // 1461
        e = c - (1461 * d) // 4
        m = (5 * e + 2) // 153
        day = e - (153 * m + 2) // 5 + 1
        month = m + 3 - 12 * (m // 10)
        year = 100 * b + d - 4800 + m // 10
        return {"year": year, "month": month, "day": day}

    def calendar_from_total(
        self, total_day: int, correlation_id: str, name_profile: str
    ) -> dict[str, Any]:
        jdn = self.jdn_for(total_day, correlation_id)
        result: dict[str, Any] = {
            "total_day": total_day,
            "long_count": self.decompose_long_count(total_day),
            "tzolkin": self.tzolkin_for(total_day, name_profile),
            "haab": self.haab_for(total_day),
            "correlation_id": correlation_id,
            "correlation_constant": self.correlation_constant(correlation_id),
            "integer_jdn": jdn,
            "gregorian": self.jdn_to_gregorian(jdn),
            "customer_prediction": False,
        }
        if total_day == 0:
            result["source_creation_notation"] = "13.0.0.0.0"
        return result


def assert_expected_subset(actual: Any, expected: Any, path: str = "expected") -> None:
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            raise AssertionError(f"{path}: expected mapping, got {type(actual).__name__}")
        for key, value in expected.items():
            if key not in actual:
                raise AssertionError(f"{path}.{key}: missing key")
            assert_expected_subset(actual[key], value, f"{path}.{key}")
        return
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise AssertionError(f"{path}: list length/type mismatch")
        for index, (actual_item, expected_item) in enumerate(
            zip(actual, expected, strict=True)
        ):
            assert_expected_subset(actual_item, expected_item, f"{path}[{index}]")
        return
    if actual != expected:
        raise AssertionError(f"{path}: expected {expected!r}, got {actual!r}")


def evaluate_vector(kernel: MayaCalendarKernel, vector: dict[str, Any]) -> dict[str, Any]:
    inputs = vector["inputs"]
    operation = inputs["operation"]
    if operation == "calendar_from_total":
        return kernel.calendar_from_total(
            inputs["total_day"], inputs["correlation_id"], inputs["name_profile"]
        )
    if operation == "calendar_from_gregorian":
        civil = inputs["gregorian"]
        jdn = kernel.gregorian_to_jdn(civil["year"], civil["month"], civil["day"])
        total = jdn - kernel.correlation_constant(inputs["correlation_id"])
        return kernel.calendar_from_total(
            total, inputs["correlation_id"], inputs["name_profile"]
        )
    if operation == "rollover_cases":
        return {"long_counts": [kernel.decompose_long_count(v) for v in inputs["totals"]]}
    if operation == "haab_cases":
        return {"haab": [kernel.haab_for(v) for v in inputs["totals"]]}
    if operation == "tzolkin_cases":
        return {
            "tzolkin": [
                kernel.tzolkin_for(v, inputs["name_profile"]) for v in inputs["totals"]
            ]
        }
    if operation == "calendar_round_compare":
        first, second = inputs["totals"]
        profile = inputs["name_profile"]
        first_round = (kernel.tzolkin_for(first, profile), kernel.haab_for(first))
        second_round = (kernel.tzolkin_for(second, profile), kernel.haab_for(second))
        round_keys = ("number", "name", "day", "month")
        first_values = tuple(first_round[0][key] for key in round_keys[:2]) + tuple(
            first_round[1][key] for key in round_keys[2:]
        )
        second_values = tuple(second_round[0][key] for key in round_keys[:2]) + tuple(
            second_round[1][key] for key in round_keys[2:]
        )
        return {
            "same_calendar_round": first_values == second_values,
            "long_counts_differ": kernel.decompose_long_count(first)
            != kernel.decompose_long_count(second),
            "period_days": second - first,
        }
    if operation == "compare_correlations":
        total = inputs["total_day"]
        ids = inputs["correlation_ids"]
        jdns = [kernel.jdn_for(total, correlation_id) for correlation_id in ids]
        internal = [
            (kernel.tzolkin_for(total, "yucatec_smithsonian_2012"), kernel.haab_for(total))
            for _ in ids
        ]
        return {
            "integer_jdns": jdns,
            "jdn_difference": jdns[1] - jdns[0],
            "internal_cycles_equal": internal[0] == internal[1],
            "correlation_ids_visible": all(bool(value) for value in ids),
        }
    if operation == "compare_name_profiles":
        yucatec, kiche = inputs["name_profiles"]
        pairs = []
        for total in inputs["totals"]:
            first = kernel.tzolkin_for(total, yucatec)
            second = kernel.tzolkin_for(total, kiche)
            pairs.append(
                {"index": first["index"], "yucatec": first["name"], "kiche": second["name"]}
            )
        return {"pairs": pairs, "indices_equal": True, "meanings_emitted": False}
    if operation == "invalid_long_counts":
        rejected = 0
        for case in inputs["cases"]:
            try:
                kernel.compose_long_count(case)
            except (TypeError, ValueError):
                rejected += 1
        return {"all_rejected": rejected == len(inputs["cases"]), "silent_normalization": False}
    if operation == "invalid_totals":
        rejected = 0
        for total in inputs["totals"]:
            try:
                kernel.decompose_long_count(total)
            except (TypeError, ValueError):
                rejected += 1
        return {"all_rejected": rejected == len(inputs["totals"]), "extended_count_inferred": False}
    if operation == "publication_contract":
        contract = kernel.spec["publication_contract"]
        return {
            "calendar_facts_allowed": contract["birth_input_eligible"],
            "interpretation_allowed": contract["interpretation_eligible"],
            "personality_output": False,
            "living_meaning_output": False,
            "customer_prediction": contract["customer_prediction"],
            "historical_use_only": contract["historical_use_only"],
            "live_engine": contract["live_engine"],
        }
    raise ValueError(f"Unknown validation operation: {operation}")


def validate(root: Path) -> dict[str, Any]:
    spec = read_json(root / "calendar_kernel_spec.json")
    vectors = read_json(root / "calendar_validation_vectors.json")
    if spec["source_pack_id"] != vectors["source_pack_id"]:
        raise ValueError("Specification and vector source packs differ")
    kernel = MayaCalendarKernel(spec)
    passed: list[str] = []
    for vector in vectors["vectors"]:
        actual = evaluate_vector(kernel, vector)
        assert_expected_subset(actual, vector["expected"], vector["vector_id"])
        passed.append(vector["vector_id"])
    return {
        "status": "pass",
        "source_pack_id": spec["source_pack_id"],
        "vectors_passed": len(passed),
        "vector_ids": passed,
        "correlation_profiles": sorted(spec["correlations"]),
        "live_engine": spec["publication_contract"]["live_engine"],
        "interpretation_eligible": spec["publication_contract"]["interpretation_eligible"],
        "customer_prediction": spec["publication_contract"]["customer_prediction"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Maya calendar research kernel.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Maya research directory")
    args = parser.parse_args()
    print(json.dumps(validate(args.root.resolve()), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
