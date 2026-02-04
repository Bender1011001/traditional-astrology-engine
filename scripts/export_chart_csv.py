import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from src.engine.forensic_engine import Auditor
from src.engine.models import Sign


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export core chart calculations to CSV.")
    parser.add_argument("--date", required=True, help="Birth date (YYYY-MM-DD)")
    parser.add_argument("--time", required=True, help="Birth time (HH:MM)")
    parser.add_argument("--city", required=True, help="Birth city")
    parser.add_argument("--state", default="", help="Birth state/province")
    parser.add_argument("--name", default="Native", help="Name of the person")
    parser.add_argument("--house_system", default="W", help="House system (W, P, R, etc.)")
    parser.add_argument("--zodiac_system", default="tropical", help="Zodiac system (tropical/sidereal)")
    parser.add_argument("--ayanamsa", default=None, help="Ayanamsa for sidereal calculations")
    parser.add_argument("--output_dir", default="chart_outputs", help="Directory for CSV output")
    parser.add_argument("--output_file", default="", help="Optional CSV filename override")
    return parser.parse_args()


def sign_from_longitude(lon: float) -> str:
    idx = int(lon / 30) % 12
    return list(Sign)[idx].value


def house_from_cusps(longitude: float, houses: dict[int, float]) -> int:
    if not houses:
        return 0
    cusps = [houses[i] for i in range(1, 13)]
    lon = longitude % 360.0
    for index in range(12):
        start = cusps[index] % 360.0
        end = cusps[(index + 1) % 12] % 360.0
        if start <= end:
            if start <= lon < end:
                return index + 1
        else:
            if lon >= start or lon < end:
                return index + 1
    return 1


def get_attr(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def add_row(rows: list[dict[str, Any]], category: str, item: str, field: str, value: Any,
            unit: str = "", notes: str = "") -> None:
    rows.append({
        "category": category,
        "item": item,
        "field": field,
        "value": value,
        "unit": unit,
        "notes": notes
    })


def main() -> None:
    args = parse_args()

    result = Auditor.generate_full_nativity(
        date_str=args.date,
        time_str=args.time,
        city=args.city,
        state=args.state,
        name=args.name,
        house_system=args.house_system,
        zodiac_system=args.zodiac_system,
        ayanamsa=args.ayanamsa
    )

    if "error" in result:
        raise SystemExit(result["error"])

    tech = result["technical_data"]
    analysis = tech.get("analysis", {})
    rows: list[dict[str, Any]] = []

    meta = tech.get("meta", {})
    coords = meta.get("coords", {})
    add_row(rows, "meta", "input", "name", args.name)
    add_row(rows, "meta", "input", "date", args.date)
    add_row(rows, "meta", "input", "time", args.time)
    add_row(rows, "meta", "input", "city", args.city)
    add_row(rows, "meta", "input", "state", args.state or "")
    add_row(rows, "meta", "input", "house_system", args.house_system)
    add_row(rows, "meta", "input", "zodiac_system", args.zodiac_system)
    add_row(rows, "meta", "input", "ayanamsa", args.ayanamsa or "")
    add_row(rows, "meta", "calc", "timestamp", meta.get("timestamp", ""))
    add_row(rows, "meta", "calc", "julian_day", meta.get("julian_day", ""), "JD")
    add_row(rows, "meta", "calc", "latitude", coords.get("lat", ""), "deg")
    add_row(rows, "meta", "calc", "longitude", coords.get("lon", ""), "deg")
    add_row(rows, "meta", "calc", "age", meta.get("age", ""))

    angles = tech.get("astronomy", {}).get("angles", {})
    add_row(rows, "angles", "Asc", "longitude", angles.get("Asc", ""), "deg")
    add_row(rows, "angles", "MC", "longitude", angles.get("MC", ""), "deg")

    houses = tech.get("astronomy", {}).get("houses", {})
    for idx in range(1, 13):
        cusp = houses.get(idx)
        if cusp is None:
            continue
        add_row(rows, "houses", f"House {idx}", "cusp_longitude", cusp, "deg")

    planets = tech.get("astronomy", {}).get("planets", {})
    for name, data in planets.items():
        lon = data.get("longitude", 0.0)
        add_row(rows, "planets", name, "longitude", lon, "deg")
        add_row(rows, "planets", name, "latitude", data.get("latitude", 0.0), "deg")
        add_row(rows, "planets", name, "speed", data.get("speed", 0.0), "deg/day")
        add_row(rows, "planets", name, "altitude", data.get("altitude", 0.0), "deg")
        add_row(rows, "planets", name, "sign", sign_from_longitude(lon))
        add_row(rows, "planets", name, "degree_in_sign", round(lon % 30, 4), "deg")
        add_row(rows, "planets", name, "house", house_from_cusps(lon, houses))
        add_row(rows, "planets", name, "is_retrograde", data.get("is_retrograde", False))

    aspects = analysis.get("aspects", [])
    for asp in aspects:
        p1 = get_attr(asp, "planet_a")
        p2 = get_attr(asp, "planet_b")
        aspect_type = get_attr(asp, "type")
        orb = get_attr(asp, "orb")
        applying = get_attr(asp, "is_applying")
        text = get_attr(asp, "text", "")
        p1 = getattr(p1, "value", p1)
        p2 = getattr(p2, "value", p2)
        aspect_type = getattr(aspect_type, "value", aspect_type)
        label = f"{p1}-{aspect_type}-{p2}"
        add_row(rows, "aspects", label, "orb", orb, "deg")
        add_row(rows, "aspects", label, "applying", applying)
        if text:
            add_row(rows, "aspects", label, "notes", text)

    hermetic_lots = analysis.get("fate", {}).get("hermetic_lots", {})
    for lot_name, lot_data in hermetic_lots.items():
        add_row(rows, "lots", lot_name, "longitude", lot_data.get("longitude", ""), "deg")
        add_row(rows, "lots", lot_name, "sign", lot_data.get("sign", ""))
        add_row(rows, "lots", lot_name, "house", lot_data.get("house", ""))
        add_row(rows, "lots", lot_name, "ruler", lot_data.get("ruler", ""))
        add_row(rows, "lots", lot_name, "status", lot_data.get("status", ""))

    forensic_lots = analysis.get("forensic_lots", {})
    for lot_name, lot_data in forensic_lots.items():
        add_row(rows, "forensic_lots", lot_name, "longitude", lot_data.get("longitude", ""), "deg")
        add_row(rows, "forensic_lots", lot_name, "sign", lot_data.get("sign", ""))
        add_row(rows, "forensic_lots", lot_name, "house", lot_data.get("house", ""))
        add_row(rows, "forensic_lots", lot_name, "ruler", lot_data.get("ruler", ""))
        add_row(rows, "forensic_lots", lot_name, "status", lot_data.get("status", ""))

    for p in tech.get("planets_forensic", []):
        name = p.get("name", "")
        dignities = p.get("dignities", {})
        add_row(rows, "dignities", name, "total_score", dignities.get("total_score", 0))
        add_row(rows, "dignities", name, "sign", dignities.get("sign", ""))
        add_row(rows, "dignities", name, "degree", dignities.get("degree", 0.0), "deg")
        breakdown = dignities.get("score_breakdown", {})
        for key, value in breakdown.items():
            add_row(rows, "dignities", name, f"score_{key}", value)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = args.name.replace(" ", "_").lower() or "chart"
    filename = args.output_file or f"{safe_name}_export_{timestamp}.csv"
    output_path = output_dir / filename

    with open(output_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["category", "item", "field", "value", "unit", "notes"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"CSV export ready: {output_path}")


if __name__ == "__main__":
    main()
