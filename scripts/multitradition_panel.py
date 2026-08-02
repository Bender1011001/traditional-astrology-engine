"""CLI runner for the multi-tradition panel.

    python scripts/multitradition_panel.py --date 1996-08-13 --time 07:18 \
        --utc-offset -7 --lat 38.2494 --lon -122.0397 --place "Fairfield, CA" \
        --name Andrew --format markdown

    python scripts/multitradition_panel.py --fixture fairfield --format json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.engine.multitradition import BirthInput, build_panel, render  # noqa: E402

FIXTURES: dict[str, dict] = {
    "fairfield": {
        "name": "Andrew",
        "civil_date": date(1996, 8, 13),
        "civil_time": "07:18",
        "utc_offset_hours": -7.0,
        "latitude": 38.2494,
        "longitude": -122.0397,
        "place_label": "Fairfield, California, United States",
    },
    # Southern hemisphere, eastern longitude, DST-free zone.
    "sydney": {
        "name": "Fixture: Sydney",
        "civil_date": date(1978, 11, 3),
        "civil_time": "22:40",
        "utc_offset_hours": 11.0,
        "latitude": -33.8688,
        "longitude": 151.2093,
        "place_label": "Sydney, New South Wales, Australia",
    },
    # Pre-1950, western Europe, near a Li Chun boundary in early February.
    "paris1931": {
        "name": "Fixture: Paris 1931",
        "civil_date": date(1931, 2, 3),
        "civil_time": "04:05",
        "utc_offset_hours": 0.0,
        "latitude": 48.8566,
        "longitude": 2.3522,
        "place_label": "Paris, France",
    },
    # Late-Zi boundary case: 23:20 local, which tests the day-rollover fork.
    "quito_latezi": {
        "name": "Fixture: Quito late-Zi",
        "civil_date": date(2004, 6, 21),
        "civil_time": "23:20",
        "utc_offset_hours": -5.0,
        "latitude": -0.1807,
        "longitude": -78.4678,
        "place_label": "Quito, Ecuador",
    },
}


def _build_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render a multi-tradition panel.")
    parser.add_argument("--fixture", choices=sorted(FIXTURES), help="Use a test birth.")
    parser.add_argument("--name", default="Native")
    parser.add_argument("--date", dest="civil_date", help="YYYY-MM-DD")
    parser.add_argument("--time", dest="civil_time", help="HH:MM wall clock at birth")
    parser.add_argument("--utc-offset", type=float, dest="utc_offset")
    parser.add_argument("--lat", type=float)
    parser.add_argument("--lon", type=float)
    parser.add_argument("--place", default="")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--out", type=Path, help="Write to this path instead of stdout.")
    return parser


def main() -> int:
    args = _build_args().parse_args()

    if args.fixture:
        birth = BirthInput(**FIXTURES[args.fixture])
    else:
        missing = [
            flag
            for flag, value in (
                ("--date", args.civil_date),
                ("--time", args.civil_time),
                ("--utc-offset", args.utc_offset),
                ("--lat", args.lat),
                ("--lon", args.lon),
            )
            if value is None
        ]
        if missing:
            print(f"Missing required arguments: {', '.join(missing)}", file=sys.stderr)
            return 2
        birth = BirthInput(
            name=args.name,
            civil_date=date.fromisoformat(args.civil_date),
            civil_time=args.civil_time,
            utc_offset_hours=args.utc_offset,
            latitude=args.lat,
            longitude=args.lon,
            place_label=args.place,
        )

    panel = build_panel(birth)
    text = (
        json.dumps(panel, indent=2, ensure_ascii=False)
        if args.format == "json"
        else render(panel)
    )

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        print(text)

    failed = [s["tradition_id"] for s in panel["sections"] if s.get("error")]
    if failed:
        print(f"\nSections with errors: {', '.join(failed)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    raise SystemExit(main())
