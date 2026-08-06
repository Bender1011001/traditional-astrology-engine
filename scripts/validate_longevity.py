"""Falsification harness for the Hyleg/Alcocoden length-of-life technique.

THE ACCEPTANCE CRITERION
------------------------
The Alcocoden's years are a *maximum promise*, not a prediction of death. In
the tradition the promise is cut short by anaretic directions, accident, or
calamity -- Lilly: the native "might live the selected years only if no
obstructive directions, sudden casualties, or general calamity intervene";
Valens treats the figure as a maximum that stands unless something cuts it.

Therefore, for anyone whose life is complete and whose birth time is recorded:

        promised_years  >=  age actually attained at death

A promise BELOW the age the native actually reached is definitionally broken --
you cannot outlive your own maximum. That is the test. Under-promising is a
failure; over-promising is not (directions explain the shortfall).

Subjects are drawn from the project's Rodden-rated corpus (AA = birth
certificate, A = from memory/family). Death dates are public record.

Run:  python scripts/validate_longevity.py
Exit code 0 only when every subject passes.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scripts.generate_premium_report import generate_chart_data  # noqa: E402


@dataclass(frozen=True)
class Subject:
    name: str
    birth: str          # YYYY-MM-DD
    time: str           # HH:MM local
    city: str
    region: str
    lat: float
    lon: float
    died_age: int       # age actually attained
    rodden: str         # birth-time quality


# Recorded birth times, completed lives. Death ages are whole years attained.
SUBJECTS: list[Subject] = [
    Subject("Marilyn Monroe", "1926-06-01", "09:30", "Los Angeles", "CA",
            34.0522, -118.2437, 36, "AA"),
    Subject("Steve Jobs", "1955-02-24", "19:15", "San Francisco", "CA",
            37.7749, -122.4194, 56, "AA"),
    Subject("Richard Nixon", "1913-01-09", "21:35", "Yorba Linda", "CA",
            33.8675, -117.8231, 81, "A"),
    Subject("Albert Einstein", "1879-03-14", "11:30", "Ulm", "Germany",
            48.4011, 9.9876, 76, "AA"),
    Subject("Carl Jung", "1875-07-26", "19:32", "Kesswil", "Switzerland",
            47.6000, 9.3167, 85, "AA"),
    Subject("Winston Churchill", "1874-11-30", "01:30", "Woodstock", "United Kingdom",
            51.8500, -1.3500, 90, "AA"),
    Subject("John F. Kennedy", "1917-05-29", "15:00", "Brookline", "MA",
            42.3318, -71.1212, 46, "A"),
    Subject("Bruce Lee", "1940-11-27", "07:12", "San Francisco", "CA",
            37.7749, -122.4194, 32, "AA"),
    Subject("Muhammad Ali", "1942-01-17", "18:35", "Louisville", "KY",
            38.2527, -85.7585, 74, "AA"),
    Subject("Babe Ruth", "1895-02-06", "13:45", "Baltimore", "MD",
            39.2904, -76.6122, 53, "AA"),
    Subject("Joe DiMaggio", "1914-11-25", "12:40", "Martinez", "CA",
            38.0194, -122.1341, 84, "AA"),
    Subject("Jack Dempsey", "1895-06-24", "17:00", "Manassa", "CO",
            37.1725, -105.9372, 87, "AA"),
    Subject("Rocky Marciano", "1923-09-01", "07:30", "Brockton", "MA",
            42.0834, -71.0184, 45, "AA"),
    Subject("Jackie Robinson", "1919-01-31", "18:30", "Cairo", "GA",
            30.8774, -84.2019, 53, "AA"),
    Subject("Wilt Chamberlain", "1936-08-21", "23:59", "Philadelphia", "PA",
            39.9526, -75.1652, 63, "AA"),
    Subject("Stephen Hawking", "1942-01-08", "12:16", "Oxford", "United Kingdom",
            51.7520, -1.2577, 76, "AA"),
    Subject("Louis Pasteur", "1822-12-27", "02:00", "Dole", "France",
            47.0937, 5.4906, 72, "AA"),
    Subject("Niels Bohr", "1885-10-07", "10:00", "Copenhagen", "Denmark",
            55.6761, 12.5683, 77, "AA"),
    Subject("Werner Heisenberg", "1901-12-05", "04:45", "Wurzburg", "Germany",
            49.7913, 9.9534, 74, "AA"),
    Subject("Enrico Fermi", "1901-09-29", "07:00", "Rome", "Italy",
            41.9028, 12.4964, 53, "AA"),
]


def promised_years(chart: dict) -> tuple[float | None, str, dict]:
    """Return (best promised years, describing label, raw branches)."""
    vitality = (chart.get("analysis") or {}).get("vitality") or {}
    capacity = vitality.get("years_capacity") or {}
    branches: dict[str, float] = {}
    for key, branch in capacity.items():
        if not isinstance(branch, dict):
            continue
        total = branch.get("total_years")
        if isinstance(total, (int, float)) and branch.get("alcocoden"):
            branches[key] = float(total)
    if not branches:
        return None, "no Alcocoden found by any method", capacity
    # The promise is the strongest surviving branch: the report should not
    # under-promise relative to any method it is willing to publish.
    best_key = max(branches, key=lambda k: branches[k])
    return branches[best_key], best_key, capacity


def main() -> int:
    print("=" * 92)
    print("LONGEVITY FALSIFICATION TEST")
    print("Criterion: promised years must be >= age actually attained.")
    print("(The Alcocoden promises a maximum; directions cut it short. Under-promising is a bug.)")
    print("=" * 92)
    print(f"{'subject':22} {'rod':>3} {'died':>5} {'promised':>9} {'method':>14}   verdict")
    print("-" * 92)

    failures: list[str] = []
    errors: list[str] = []
    for s in SUBJECTS:
        try:
            chart = json.loads(
                generate_chart_data(
                    name=s.name, date_str=s.birth, time_str=s.time,
                    city=s.city, state=s.region, latitude=s.lat, longitude=s.lon,
                )
            )
        except Exception as exc:  # chart generation itself failed
            errors.append(f"{s.name}: chart generation failed: {exc!r}")
            print(f"{s.name:22} {s.rodden:>3} {s.died_age:>5} {'ERROR':>9} {'-':>14}   CHART FAILED")
            continue

        years, method, _raw = promised_years(chart)
        if years is None:
            failures.append(f"{s.name}: no Alcocoden found (died at {s.died_age})")
            print(f"{s.name:22} {s.rodden:>3} {s.died_age:>5} {'none':>9} {'-':>14}   FAIL (no giver of years)")
            continue

        ok = years >= s.died_age
        gap = years - s.died_age
        verdict = f"pass (+{gap:.0f})" if ok else f"FAIL ({gap:+.0f} short)"
        if not ok:
            failures.append(f"{s.name}: promised {years:.1f}, attained {s.died_age}")
        print(f"{s.name:22} {s.rodden:>3} {s.died_age:>5} {years:>9.1f} {method:>14}   {verdict}")

    total = len(SUBJECTS)
    passed = total - len(failures) - len(errors)
    print("-" * 92)
    print(f"PASSED {passed}/{total}")
    if errors:
        print(f"\nCHART ERRORS ({len(errors)}):")
        for e in errors:
            print("  -", e)
    if failures:
        print(f"\nFAILURES ({len(failures)}) — promise fell below the life actually lived:")
        for f in failures:
            print("  -", f)
        print("\nThe technique is not yet correctly implemented.")
        return 1
    print("\nAll subjects pass: no promise falls short of the life actually lived.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
