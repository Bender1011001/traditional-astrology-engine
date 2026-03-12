"""
03_lock_hypotheses.py

Write a timestamped, SHA-256-locked hypothesis file before any merge.
This MUST run before 04_analyze.py to satisfy the preregistration protocol.

Output: hypotheses_locked.json
Usage: python 03_lock_hypotheses.py --out-dir ./output
"""

from __future__ import annotations
import argparse, hashlib, json, logging, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S")
logger = logging.getLogger(__name__)


HYPOTHESES: List[Dict[str, Any]] = [
    {
        "id": "H1",
        "label": "Mars Accidental Dignity - Athletes vs Non-Athletes",
        "description": (
            "Athletes show higher Mars accidental dignity than non-athletes. "
            "Variable: planets.Mars.accidental_total."
        ),
        "variable": "planets.Mars.accidental_total",
        "group_a": "Athletes",
        "group_b": "non-Athletes",
        "test": "Mann-Whitney U + Cohen d",
        "direction": "Athletes > non-Athletes",
        "basis": "Gauquelin (1955) Mars Effect.",
    },
    {
        "id": "H2",
        "label": "Mercury Dignity - Scientists vs Non-Scientists",
        "description": (
            "Scientists show higher Mercury essential or accidental dignity. "
            "Variables: planets.Mercury.essential_dignity_total, accidental_total."
        ),
        "variable": "planets.Mercury.essential_dignity_total OR accidental_total",
        "group_a": "Scientists",
        "group_b": "non-Scientists",
        "test": "Mann-Whitney U + Cohen d",
        "direction": "Scientists > non-Scientists",
        "basis": "Gauquelin Saturn/Mercury effect; Mercury = intellect.",
    },
    {
        "id": "H3",
        "label": "Mars Dignity / Maltreatment - Military vs Artists",
        "description": (
            "Military show higher Mars essential dignity or lower maltreatment "
            "severity than Artists. Variables: planets.Mars.essential_dignity_total, "
            "maltreatment_severity_sum."
        ),
        "variable": "planets.Mars.essential_dignity_total, maltreatment_severity_sum",
        "group_a": "Military",
        "group_b": "Artists",
        "test": "Mann-Whitney U + Cohen d",
        "direction": "Military > Artists (ess. dig.); Military < Artists (maltreatment)",
        "basis": "Classical Mars = warfare; Gauquelin B2/D1.",
    },
    {
        "id": "H4",
        "label": "Melancholic Temperament - Scientists+Writers vs Athletes",
        "description": (
            "Melancholic (Cold/Dry) temperament is more prevalent in Scientists "
            "and Writers than in Athletes."
        ),
        "variable": "temperament.primary (Melancholic vs other)",
        "group_a": "Scientists, Writers",
        "group_b": "Athletes",
        "test": "Chi-square + Cramer V",
        "direction": "Scientists/Writers > Athletes (proportion Melancholic)",
        "basis": "Humoral theory; Saturn = Melancholic.",
    },
    {
        "id": "H5",
        "label": "Choleric Temperament - Athletes+Military vs Scientists",
        "description": (
            "Choleric (Hot/Dry) temperament is more prevalent in Athletes and "
            "Military than in Scientists."
        ),
        "variable": "temperament.primary (Choleric vs other)",
        "group_a": "Athletes, Military",
        "group_b": "Scientists",
        "test": "Chi-square + Cramer V",
        "direction": "Athletes/Military > Scientists (proportion Choleric)",
        "basis": "Humoral theory; Mars = choleric.",
    },
]

VARIABLES_TO_TEST: List[str] = [
    "temperament.primary",
    "temperament.scores.Hot",  "temperament.scores.Cold",
    "temperament.scores.Moist", "temperament.scores.Dry",
    "almuten.winner",
    "lord_of_geniture.winner",
    "sect.type",
    "planets.Sun.house",    "planets.Sun.essential_dignity_total",    "planets.Sun.accidental_total",
    "planets.Moon.house",   "planets.Moon.essential_dignity_total",   "planets.Moon.accidental_total",
    "planets.Mercury.house", "planets.Mercury.essential_dignity_total", "planets.Mercury.accidental_total",
    "planets.Venus.house",  "planets.Venus.essential_dignity_total",  "planets.Venus.accidental_total",
    "planets.Mars.house",   "planets.Mars.essential_dignity_total",   "planets.Mars.accidental_total",
    "planets.Jupiter.house", "planets.Jupiter.essential_dignity_total", "planets.Jupiter.accidental_total",
    "planets.Saturn.house", "planets.Saturn.essential_dignity_total", "planets.Saturn.accidental_total",
    "planets.Sun.solar_status",    "planets.Sun.is_retrograde",
    "planets.Moon.solar_status",   "planets.Moon.is_retrograde",
    "planets.Mercury.solar_status", "planets.Mercury.is_retrograde",
    "planets.Venus.solar_status",  "planets.Venus.is_retrograde",
    "planets.Mars.solar_status",   "planets.Mars.is_retrograde",
    "planets.Jupiter.solar_status", "planets.Jupiter.is_retrograde",
    "planets.Saturn.solar_status", "planets.Saturn.is_retrograde",
    "elements.FIRE", "elements.EARTH", "elements.AIR", "elements.WATER",
    "hemispheres.East", "hemispheres.West", "hemispheres.North", "hemispheres.South",
    "maltreatment_count", "maltreatment_severity_sum",
]


def compute_lock_hash(hypotheses, variables, threshold, min_n) -> str:
    payload = {
        "hypotheses": hypotheses,
        "variables_to_test": variables,
        "significance_threshold": threshold,
        "minimum_group_size": min_n,
    }
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def write_locked_file(out_path: Path) -> None:
    """Write hypotheses_locked.json with UTC timestamp and SHA-256 lock hash."""
    threshold = 0.01
    min_n     = 30
    lock_hash = compute_lock_hash(HYPOTHESES, VARIABLES_TO_TEST, threshold, min_n)
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    locked = {
        "run_timestamp":          timestamp,
        "lock_hash":              lock_hash,
        "lock_hash_algorithm":    "SHA-256",
        "lock_note": (
            "Written by 03_lock_hypotheses.py BEFORE any merge of occupation data. "
            "The lock_hash proves hypotheses were preregistered. "
            "Run 04_analyze.py only after this file exists."
        ),
        "significance_threshold": threshold,
        "minimum_group_size":     min_n,
        "hypotheses":             HYPOTHESES,
        "variables_to_test":      VARIABLES_TO_TEST,
    }
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(locked, fh, indent=2, ensure_ascii=False)
    logger.info("Wrote %s", out_path)
    logger.info("Timestamp : %s", timestamp)
    logger.info("Lock hash : %s", lock_hash)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Lock hypotheses before analysis (preregistration).")
    ap.add_argument("--out-dir", type=Path, default=Path("."))
    ap.add_argument("--force", action="store_true",
        help="Overwrite existing hypotheses_locked.json.")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.out_dir / "hypotheses_locked.json"
    if out_path.exists() and not args.force:
        logger.warning("hypotheses_locked.json already exists. Use --force to overwrite.")
        return 0
    write_locked_file(out_path)
    print(f"
Hypotheses locked: {out_path.resolve()}")
    print("Run 04_analyze.py AFTER this file exists.")
    return 0


if __name__ == "__main__":
    sys.exit(main())