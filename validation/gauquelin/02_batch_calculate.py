"""
02_batch_calculate.py - Batch astrological calculation pipeline (blind).

Processes every record in subjects_blind.json through the Codex Caelestis
engine (Auditor.generate_full_nativity) WITHOUT ever loading occupation data.

Output:
  results_raw.json   - Astrological fields keyed by anonymous id only.
  failures_log.json  - Records that failed, with error reasons.

Fields extracted per subject:
  temperament.primary, temperament.scores {Hot, Cold, Moist, Dry}
  almuten.winner, almuten.breakdown (7-planet dict)
  lord_of_geniture.winner, lord_of_geniture.scores
  sect.type
  per planet (Sun Moon Mercury Venus Mars Jupiter Saturn):
    house, essential_dignity_total, accidental_total, solar_status, is_retrograde
  elements {FIRE, EARTH, AIR, WATER}
  hemispheres {East, West, North, South}
  maltreatment_count, maltreatment_severity_sum

Usage:
    python 02_batch_calculate.py
        --blind-file ./output/subjects_blind.json
        --out-dir    ./output
        --engine-dir /path/to/astrology/src
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

try:
    from tqdm import tqdm
    _HAS_TQDM = True
except ImportError:
    _HAS_TQDM = False


def _progress(iterable, total: int, desc: str = "Processing"):
    """Wrap iterable with a progress display (tqdm or simple print fallback)."""
    if _HAS_TQDM:
        return tqdm(iterable, total=total, desc=desc, unit="subject")
    class _SimpleProg:
        def __init__(self, it):
            self._it = iter(it)
            self._n = 0
        def __iter__(self):
            return self
        def __next__(self):
            val = next(self._it)
            self._n += 1
            if self._n % 100 == 0:
                logger.info("%s: %d / %d", desc, self._n, total)
            return val
    return _SimpleProg(iterable)

# ---------------------------------------------------------------------------
# Engine loader
# ---------------------------------------------------------------------------

def load_engine(engine_dir: str) -> Any:
    """
    Import the Codex Caelestis Auditor from engine_dir.

    Sets dummy environment variables required by the engine before import.
    This keeps the batch runner self-contained and avoids needing a real
    .env file for the geocoding / database credentials.
    """
    # Set dummy env vars that engine modules may read at import time
    dummy_env = {
        "DATABASE_URL":    "sqlite:///dummy_gauquelin.db",
        "SECRET_KEY":      "gauquelin_blind_pipeline_key",
        "GEOCODING_API":   "none",
        "OPENAI_API_KEY":  "sk-dummy",
        "RAPIDAPI_KEY":    "dummy",
        "AZURE_STORAGE":   "DefaultEndpointsProtocol=https;dummy",
    }
    for k, v in dummy_env.items():
        os.environ.setdefault(k, v)

    # Add engine_dir to path so src.engine imports resolve
    engine_path = str(Path(engine_dir).resolve())
    if engine_path not in sys.path:
        sys.path.insert(0, engine_path)

    # Import the Auditor class
    try:
        from src.engine.forensic_engine import Auditor
        logger.info("Loaded Auditor from %s", engine_path)
        return Auditor
    except ImportError as exc:
        logger.error("Cannot import Auditor: %s", exc)
        logger.error("Ensure --engine-dir points to the root of the astrology project.")
        raise


# ---------------------------------------------------------------------------
# Field extractors
# ---------------------------------------------------------------------------

CLASSICAL_PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]


def _safe_get(obj: Any, *keys, default=None) -> Any:
    """Safely traverse nested dict/object using a sequence of keys."""
    for key in keys:
        if obj is None:
            return default
        if isinstance(obj, dict):
            obj = obj.get(key)
        else:
            obj = getattr(obj, key, None)
    return obj if obj is not None else default


def extract_temperament(tech: Dict) -> Dict:
    """Extract temperament fields from technical_data."""
    temp = _safe_get(tech, "analysis", "temperament", default={})
    return {
        "primary": _safe_get(temp, "primary_temperament", default="Unknown"),
        "scores":  _safe_get(temp, "scores", default={"Hot": 0, "Cold": 0, "Moist": 0, "Dry": 0}),
    }


def extract_almuten(tech: Dict) -> Dict:
    """Extract Almuten Figuris result from technical_data."""
    alm = _safe_get(tech, "analysis", "dignity", "almuten", default={})
    return {
        "winner":    _safe_get(alm, "winner",    default="Unknown"),
        "breakdown": _safe_get(alm, "breakdown", default={}),
    }


def extract_lord_of_geniture(tech: Dict) -> Dict:
    """Extract Lord of the Geniture result."""
    log = _safe_get(tech, "analysis", "dignity", "lord_of_geniture", default={})
    winner = _safe_get(log, "winner", default="Unknown")
    raw_scores = _safe_get(log, "scores", default={})
    scores_out = {}
    for planet, score_data in raw_scores.items():
        if isinstance(score_data, dict):
            scores_out[planet] = score_data.get("total", 0)
        else:
            scores_out[planet] = int(score_data) if score_data is not None else 0
    return {
        "winner": winner,
        "scores": scores_out,
    }


def extract_sect(tech: Dict) -> Dict:
    """Extract sect type."""
    sect_data = _safe_get(tech, "analysis", "sect", default={})
    if isinstance(sect_data, dict):
        sect_type = sect_data.get("type", "Unknown")
    elif isinstance(sect_data, str):
        sect_type = sect_data
    else:
        sect_type = str(sect_data)
    return {"type": sect_type}

def extract_planet_data(tech: Dict) -> Dict:
    """
    Extract per-planet fields for the 7 classical planets.

    For each planet: house, essential_dignity_total, accidental_total,
    solar_status, is_retrograde.
    """
    planet_out: Dict[str, Dict] = {}

    # Primary source: analysis.planets_forensic (a list of dicts)
    forensic_list = _safe_get(tech, "analysis", "planets_forensic", default=[])
    if not forensic_list:
        forensic_list = _safe_get(tech, "planets_forensic", default=[])

    # Build lookup by planet name
    pf_by_name: Dict[str, Dict] = {}
    for pf in forensic_list:
        if isinstance(pf, dict):
            name = pf.get("name", "")
            if name:
                pf_by_name[name] = pf

    for planet_name in CLASSICAL_PLANETS:
        pf = pf_by_name.get(planet_name, {})

        # Essential dignity total
        dig = pf.get("dignities", {})
        if isinstance(dig, dict):
            ess_total = dig.get("total_score", dig.get("score", 0))
        else:
            ess_total = 0

        # Accidental dignity total
        acc = pf.get("accidental", {})
        if isinstance(acc, dict):
            acc_total = acc.get("score", acc.get("total", 0))
        else:
            acc_total = 0

        planet_out[planet_name] = {
            "house":                 pf.get("house", 0),
            "essential_dignity_total": int(ess_total) if ess_total is not None else 0,
            "accidental_total":      int(acc_total) if acc_total is not None else 0,
            "solar_status":          pf.get("solar_status", "Free"),
            "is_retrograde":         bool(pf.get("retrograde", False)),
        }

    return planet_out


def extract_elements(tech: Dict) -> Dict:
    """Extract elemental balance counts {FIRE, EARTH, AIR, WATER}."""
    el = _safe_get(tech, "analysis", "supplemental", "elements", default={})
    if not el:
        el = _safe_get(tech, "analysis", "elements", default={})
    return {
        "FIRE":  int(el.get("FIRE", 0)  if el else 0),
        "EARTH": int(el.get("EARTH", 0) if el else 0),
        "AIR":   int(el.get("AIR", 0)   if el else 0),
        "WATER": int(el.get("WATER", 0) if el else 0),
    }


def extract_hemispheres(tech: Dict) -> Dict:
    """Extract hemisphere counts {East, West, North, South}."""
    hemi_block = _safe_get(tech, "analysis", "supplemental", "hemispheres", default={})
    if not hemi_block:
        hemi_block = _safe_get(tech, "analysis", "hemispheres", default={})
    if isinstance(hemi_block, dict) and "counts" in hemi_block:
        counts = hemi_block["counts"]
    else:
        counts = hemi_block or {}
    return {
        "East":  int(counts.get("East", 0)),
        "West":  int(counts.get("West", 0)),
        "North": int(counts.get("North", 0)),
        "South": int(counts.get("South", 0)),
    }


def extract_maltreatments(tech: Dict) -> Dict:
    """
    Count total kakosis conditions and sum their severity across all 7 planets.
    """
    forensic_list = _safe_get(tech, "analysis", "planets_forensic", default=[])
    if not forensic_list:
        forensic_list = _safe_get(tech, "planets_forensic", default=[])

    total_count = 0
    total_severity = 0

    for pf in forensic_list:
        if not isinstance(pf, dict):
            continue
        name = pf.get("name", "")
        if name not in CLASSICAL_PLANETS:
            continue
        malts = pf.get("maltreatments", [])
        if isinstance(malts, list):
            total_count += len(malts)
            for m in malts:
                if isinstance(m, dict):
                    total_severity += int(m.get("severity", 0))

    return {
        "maltreatment_count":        total_count,
        "maltreatment_severity_sum": total_severity,
    }

def process_subject(subject: Dict, Auditor: Any) -> Dict:
    """
    Run one subject through the Codex Caelestis engine and extract fields.

    Parameters
    ----------
    subject : dict
        A record from subjects_blind.json with keys: id, date, time, city, country.
    Auditor : class
        The loaded Auditor class from src.engine.forensic_engine.

    Returns
    -------
    dict
        Extracted astrological fields keyed by anonymous id.
        Contains no name or occupation fields.
    """
    sid = subject["id"]
    date = subject["date"]   # YYYY-MM-DD
    time = subject["time"]   # HH:MM
    city = subject.get("city", "Paris")
    country = subject.get("country", "FR")

    # Build city string for engine (country is appended if not already present)
    city_arg = city
    if country and country.upper() not in city.upper():
        city_arg = f"{city}, {country}"

    # Call the engine
    result = Auditor.generate_full_nativity(
        date_str=date,
        time_str=time,
        city=city_arg,
        name="Subject",  # Generic name - never stored in output
        house_system="W",
        zodiac_system="tropical",
    )

    if "error" in result:
        raise RuntimeError(result["error"])

    tech = result.get("technical_data", {})

    # Extract all fields
    row: Dict = {"id": sid}
    row["temperament"]       = extract_temperament(tech)
    row["almuten"]           = extract_almuten(tech)
    row["lord_of_geniture"]  = extract_lord_of_geniture(tech)
    row["sect"]              = extract_sect(tech)
    row["planets"]           = extract_planet_data(tech)
    row["elements"]          = extract_elements(tech)
    row["hemispheres"]       = extract_hemispheres(tech)
    row.update(extract_maltreatments(tech))

    return row


def run_batch(
    blind_path: Path,
    out_dir: Path,
    engine_dir: str,
    limit: Optional[int] = None,
    resume: bool = False,
    sleep_seconds: float = 0.1,
) -> None:
    """
    Main batch processing loop.

    Parameters
    ----------
    blind_path    : Path to subjects_blind.json
    out_dir       : Directory to write results_raw.json and failures_log.json
    engine_dir    : Path to the root of the astrology project (contains src/)
    limit         : If set, process only this many subjects (for testing)
    resume        : If True, skip subjects already in results_raw.json
    sleep_seconds : Delay between calculations (avoids memory overload)
    """
    # Load blind subjects (no occupation data)
    logger.info("Loading blind subjects from %s", blind_path)
    with open(blind_path, encoding="utf-8") as fh:
        subjects: List[Dict] = json.load(fh)

    if limit:
        subjects = subjects[:limit]
    logger.info("Subjects to process: %d", len(subjects))

    # Load engine
    Auditor = load_engine(engine_dir)

    out_dir.mkdir(parents=True, exist_ok=True)
    results_path  = out_dir / "results_raw.json"
    failures_path = out_dir / "failures_log.json"

    # Resume: load existing results to skip already-calculated ids
    existing_ids: set = set()
    results: List[Dict] = []
    if resume and results_path.exists():
        with open(results_path, encoding="utf-8") as fh:
            results = json.load(fh)
        existing_ids = {r["id"] for r in results}
        logger.info("Resuming: %d already calculated.", len(existing_ids))

    failures: List[Dict] = []
    if failures_path.exists():
        with open(failures_path, encoding="utf-8") as fh:
            failures = json.load(fh)

    to_process = [s for s in subjects if s["id"] not in existing_ids]
    logger.info("Subjects remaining: %d", len(to_process))

    processed = 0
    failed = 0

    for subject in _progress(to_process, total=len(to_process)):
        sid = subject["id"]
        try:
            row = process_subject(subject, Auditor)
            results.append(row)
            processed += 1
        except Exception as exc:
            failed += 1
            failures.append({
                "id":    sid,
                "date":  subject.get("date", ""),
                "time":  subject.get("time", ""),
                "city":  subject.get("city", ""),
                "error": str(exc),
            })
            logger.debug("Failed %s: %s", sid, exc)

        # Rate limit to avoid memory buildup
        time.sleep(sleep_seconds)

        # Checkpoint: save every 500 records
        if processed % 500 == 0 and processed > 0:
            _checkpoint_save(results, results_path)
            _checkpoint_save(failures, failures_path)

    # Final save
    _checkpoint_save(results, results_path)
    _checkpoint_save(failures, failures_path)

    logger.info("Batch complete: %d processed, %d failed.", processed, failed)
    logger.info("Results saved to %s", results_path)
    logger.info("Failures saved to %s", failures_path)


def _checkpoint_save(data: List, path: Path) -> None:
    """Write data to path atomically (write to temp, then rename)."""
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False, default=str)
    tmp.replace(path)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Batch calculate Codex Caelestis nativities (blind pipeline).",
    )
    ap.add_argument(
        "--blind-file", type=Path, required=True,
        help="Path to subjects_blind.json from step 01.",
    )
    ap.add_argument(
        "--out-dir", type=Path, default=Path("."),
        help="Output directory for results_raw.json and failures_log.json.",
    )
    ap.add_argument(
        "--engine-dir", type=str, default=".",
        help="Root directory of the astrology project (must contain src/).",
    )
    ap.add_argument(
        "--limit", type=int, default=None,
        help="Process only the first N subjects (for testing).",
    )
    ap.add_argument(
        "--resume", action="store_true",
        help="Skip subjects already in results_raw.json.",
    )
    ap.add_argument(
        "--sleep", type=float, default=0.1,
        help="Seconds to sleep between calculations (default 0.1).",
    )
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.blind_file.exists():
        logger.error("subjects_blind.json not found at %s", args.blind_file)
        return 1

    run_batch(
        blind_path=args.blind_file,
        out_dir=args.out_dir,
        engine_dir=args.engine_dir,
        limit=args.limit,
        resume=args.resume,
        sleep_seconds=args.sleep,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())