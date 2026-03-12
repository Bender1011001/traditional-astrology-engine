from __future__ import annotations

"""
01_parse_gauquelin.py - Gauquelin CURA data parser.

Data source: http://cura.free.fr/gauq/17archg.html
Parses the 17 CURA-format files (A1-A6, B1-B6, C1-C3, D1-D2, E1).

CURA Fixed-Width Format:
  Cols  1-4   record number
  Cols  5-24  last name
  Cols 25-44  first name
  Col  45     gender (M/F)
  Cols 46-53  DD MM YYYY
  Cols 54-57  HH MM
  Cols 58-72  city name
  Cols 73-74  country code
  Cols 75-80  latitude (e.g. 4852N)
  Cols 81-86  longitude (e.g. 00220E)

Blind Pipeline Contract
-----------------------
Produces two separated output files:
  subjects_blind.json      - id, date, time, city, country, gender ONLY
                             No name. No occupation data.
                             --> pass to 02_batch_calculate.py
  subjects_occupation.json - id, occupation_group, occupation_detail ONLY
                             MUST NOT be passed to 02_batch_calculate.py.
                             --> merged in 04_analyze.py only.

Usage:
    python 01_parse_gauquelin.py --data-dir ./cura_data --out-dir ./output
    python 01_parse_gauquelin.py --files A1.txt A2.txt --out-dir ./output
    python 01_parse_gauquelin.py --validate-split --out-dir ./output
"""

import argparse
import json
import logging
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


CURA_SERIES_DETAIL: Dict[str, str] = {
    "A1": "Sports Champions (French)",
    "A2": "Sports Champions (European - Athletics)",
    "A3": "Sports Champions (European - Ball Sports)",
    "A4": "Sports Champions (European - Combat and Racing)",
    "A5": "Sports Champions (European - Team Sports)",
    "A6": "Sports Champions (European - Water Sports)",
    "B1": "Physicians and Scientists",
    "B2": "Military Officers",
    "B3": "Painters and Artists",
    "B4": "Actors and Performers",
    "B5": "Musicians",
    "B6": "Writers and Poets",
    "C1": "Sports Champions (Replication Set 1)",
    "C2": "Sports Champions (Replication Set 2)",
    "C3": "Scientists (Replication Set)",
    "D1": "Military Officers (Extended)",
    "D2": "Journalists and Politicians",
    "E1": "Executives and Clergy",
}

CURA_SERIES_GROUP: Dict[str, str] = {
    "A1": "Athletes", "A2": "Athletes", "A3": "Athletes",
    "A4": "Athletes", "A5": "Athletes", "A6": "Athletes",
    "B1": "Scientists",
    "B2": "Military",
    "B3": "Artists",  "B4": "Artists",  "B5": "Artists",
    "B6": "Writers",
    "C1": "Athletes", "C2": "Athletes",
    "C3": "Scientists",
    "D1": "Military",
    "D2": "Politicians",
    "E1": "Executives",
}


@dataclass
class RawRecord:
    """Full intermediate representation of one parsed Gauquelin subject."""
    record_num: int
    series: str
    last_name: str
    first_name: str
    gender: str
    day: int
    month: int
    year: int
    hour: int
    minute: int
    city: str
    country: str
    lat_raw: str
    lon_raw: str
    occupation_detail: str
    occupation_group: str

    @property
    def uid(self) -> str:
        """Unique subject identifier: series + zero-padded record number."""
        return f"{self.series}-{self.record_num:04d}"

    @property
    def date_str(self) -> str:
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"

    @property
    def time_str(self) -> str:
        return f"{self.hour:02d}:{self.minute:02d}"


class CURAParser:
    """
    Parser for CURA-format Gauquelin data files.

    Strategy: skip non-data lines, slice name block, apply date/time regex,
    then parse lat/lon/country from the location tail. CURA files are Latin-1.
    """
    _KNOWN_COUNTRIES = frozenset({
        "FR", "BE", "DE", "IT", "ES", "GB", "US", "CH", "AT", "NL",
        "PL", "RU", "SE", "NO", "DK", "PT", "HU", "CZ", "RO", "GR",
        "AR", "BR", "AU", "CA", "MX", "JP", "IN", "ZA", "FI", "IE",
        "YU", "CS", "DD", "SU",
    })
    _DATE_TIME_RE = re.compile(
        r"(?P<day>\d{1,2})\s+(?P<month>\d{1,2})\s+(?P<year>\d{4})\s+"
        r"(?P<hour>\d{1,2})\s+(?P<minute>\d{1,2})"
    )
    _LAT_RE = re.compile(r"(\d{2,4})\s*([NS])", re.IGNORECASE)
    _LON_RE = re.compile(r"(\d{3,5})\s*([EW])", re.IGNORECASE)

    def __init__(self, series: str) -> None:
        self.series = series
        self.occupation_detail = CURA_SERIES_DETAIL.get(series, "Unknown")
        self.occupation_group  = CURA_SERIES_GROUP.get(series, "Unknown")

    def parse_file(self, filepath: Path) -> List[RawRecord]:
        """Parse a CURA file; return a list of RawRecord objects."""
        records: List[RawRecord] = []
        error_count = 0
        try:
            with open(filepath, encoding="latin-1", errors="replace") as fh:
                raw_lines = fh.readlines()
        except OSError as exc:
            logger.error("Cannot open %s: %s", filepath, exc)
            return records
        logger.info("  Parsing %s (%d lines)...", filepath.name, len(raw_lines))
        for lineno, line in enumerate(raw_lines, start=1):
            line = line.rstrip("
")
            if not line.strip() or not line[:4].strip().isdigit():
                continue
            rec = self._parse_line(line, lineno)
            if rec is not None:
                records.append(rec)
            else:
                error_count += 1
                if error_count <= 10:
                    logger.debug("  Skipped line %d: %r", lineno, line[:80])
        logger.info("  %s -> %d records, %d skipped.",
            filepath.name, len(records), error_count)
        return records

    def _parse_line(self, line: str, lineno: int) -> Optional[RawRecord]:
        """Parse one data line; return None on failure."""
        try:
            rec_str = line[:4].strip()
            if not rec_str.isdigit():
                return None
            rec_num = int(rec_str)
            name_block = line[4:50] if len(line) >= 50 else line[4:]
            last_name, first_name = self._split_name(name_block)
            gender_char = line[50:51].strip() if len(line) > 50 else "?"
            gender = gender_char.upper() if gender_char.upper() in ("M", "F") else "?"
            search_zone = line[51:] if len(line) > 51 else ""
            dt_match = self._DATE_TIME_RE.search(search_zone)
            if not dt_match:
                return None
            day    = int(dt_match.group("day"))
            month  = int(dt_match.group("month"))
            year   = int(dt_match.group("year"))
            hour   = int(dt_match.group("hour"))
            minute = int(dt_match.group("minute"))
            if not (1 <= day <= 31 and 1 <= month <= 12 and 1800 <= year <= 2000):
                return None
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                return None
            tail_offset = 51 + dt_match.end()
            tail = line[tail_offset:].strip() if len(line) > tail_offset else ""
            city, country, lat_raw, lon_raw = self._parse_location_tail(tail)
            return RawRecord(
                record_num=rec_num, series=self.series,
                last_name=last_name, first_name=first_name, gender=gender,
                day=day, month=month, year=year,
                hour=hour, minute=minute,
                city=city, country=country,
                lat_raw=lat_raw, lon_raw=lon_raw,
                occupation_detail=self.occupation_detail,
                occupation_group=self.occupation_group,
            )
        except Exception as exc:
            logger.debug("  Line %d: %s", lineno, exc)
            return None

    @staticmethod
    def _split_name(name_block: str) -> Tuple[str, str]:
        last_raw  = name_block[:20].strip()
        first_raw = name_block[20:40].strip()
        if not first_raw and "  " in last_raw:
            parts = re.split(r"\s{2,}", last_raw.strip(), maxsplit=1)
            last_raw  = parts[0].strip()
            first_raw = parts[1].strip() if len(parts) > 1 else ""
        return (last_raw or "UNKNOWN"), (first_raw or "UNKNOWN")
    def _parse_location_tail(self, tail: str) -> Tuple[str, str, str, str]:
        """Extract (city, country, lat_raw, lon_raw) from line tail."""
        lat_raw = lon_raw = ""
        remaining = tail
        lon_match = self._LON_RE.search(tail)
        lat_match = self._LAT_RE.search(tail)
        if lon_match:
            lon_raw   = tail[lon_match.start():lon_match.end()]
            remaining = tail[:lon_match.start()].strip()
        if lat_match and lat_match.start() < (lon_match.start() if lon_match else len(tail)):
            lat_raw   = tail[lat_match.start():lat_match.end()]
            remaining = tail[:lat_match.start()].strip()
        tokens  = remaining.split()
        country = ""
        city    = ""
        if tokens:
            if tokens[-1].upper() in self._KNOWN_COUNTRIES:
                country = tokens[-1].upper()
                city    = " ".join(tokens[:-1])
            elif len(tokens) >= 2 and tokens[-2].upper() in self._KNOWN_COUNTRIES:
                country = tokens[-2].upper()
                city    = " ".join(tokens[:-2])
            else:
                city = " ".join(tokens)
        return (city or "UNKNOWN"), (country or "??"), (lat_raw or "?"), (lon_raw or "?")


FORBIDDEN_BLIND_FIELDS = frozenset({
    "name", "last_name", "first_name", "full_name",
    "occupation", "occupation_group", "occupation_detail",
    "series", "category", "profession",
})


def write_blind_file(records: List[RawRecord], out_path: Path) -> None:
    """
    Write subjects_blind.json.
    Contains id, date, time, city, country, gender ONLY.
    Safe to pass to 02_batch_calculate.py.
    """
    output = [
        {
            "id":      r.uid,
            "date":    r.date_str,
            "time":    r.time_str,
            "city":    r.city,
            "country": r.country,
            "gender":  r.gender,
        }
        for r in records
    ]
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2, ensure_ascii=False)
    logger.info("Wrote %d blind records -> %s", len(output), out_path)


def write_occupation_file(records: List[RawRecord], out_path: Path) -> None:
    """
    Write subjects_occupation.json.
    Contains id, occupation_group, occupation_detail ONLY.
    MUST NOT be passed to 02_batch_calculate.py.
    """
    output = [
        {
            "id":                r.uid,
            "occupation_group":  r.occupation_group,
            "occupation_detail": r.occupation_detail,
        }
        for r in records
    ]
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2, ensure_ascii=False)
    logger.info("Wrote %d occupation records -> %s", len(output), out_path)


def validate_blind_split(out_dir: Path) -> bool:
    """
    Verify subjects_blind.json contains no name or occupation fields.
    Returns True if clean, False otherwise.
    """
    blind_path = out_dir / "subjects_blind.json"
    if not blind_path.exists():
        logger.error("subjects_blind.json not found in %s", out_dir)
        return False
    with open(blind_path, encoding="utf-8") as fh:
        recs = json.load(fh)
    violations = [
        (r.get("id", "?"), sorted(set(r.keys()) & FORBIDDEN_BLIND_FIELDS))
        for r in recs
        if set(r.keys()) & FORBIDDEN_BLIND_FIELDS
    ]
    if violations:
        logger.error("BLIND FILE CONTAMINATED: %d violation(s). First: %s",
            len(violations), violations[:3])
        return False
    logger.info("Blind split VALID: %d records, no forbidden fields.", len(recs))
    return True


def discover_cura_files(data_dir: Path) -> List[Tuple[str, Path]]:
    """Auto-discover CURA data files in data_dir by series code."""
    found: List[Tuple[str, Path]] = []
    for series in CURA_SERIES_DETAIL:
        for ext in (".txt", ".dat", ".csv", ""):
            for stem in (series, series.lower()):
                candidate = data_dir / f"{stem}{ext}"
                if candidate.exists():
                    found.append((series, candidate))
                    break
    return found


def infer_series(filepath: Path) -> str:
    stem = filepath.stem.upper()
    return stem if stem in CURA_SERIES_DETAIL else "UNKNOWN"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Parse CURA Gauquelin data into blind/occupation split files.",
    )
    ap.add_argument("--data-dir", type=Path)
    ap.add_argument("--files", nargs="+")
    ap.add_argument("--out-dir", type=Path, default=Path("."))
    ap.add_argument("--validate-split", action="store_true")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    if args.validate_split:
        return 0 if validate_blind_split(args.out_dir) else 1

    pairs: List[Tuple[str, Path]] = []
    if args.files:
        for f in args.files:
            fp = Path(f)
            pairs.append((infer_series(fp), fp))
    elif args.data_dir:
        pairs = discover_cura_files(args.data_dir)
        if not pairs:
            logger.error("No CURA files found in %s.", args.data_dir)
            return 1
        logger.info("Discovered %d CURA file(s).", len(pairs))
    else:
        ap.error("Provide --data-dir or --files.")

    all_records: List[RawRecord] = []
    for series, fp in pairs:
        all_records.extend(CURAParser(series).parse_file(fp))

    if not all_records:
        logger.error("No records parsed. Verify input files and format.")
        return 1

    seen: set = set()
    deduped: List[RawRecord] = []
    for r in all_records:
        if r.uid not in seen:
            seen.add(r.uid)
            deduped.append(r)
    dupes = len(all_records) - len(deduped)
    if dupes:
        logger.warning("Removed %d duplicate IDs.", dupes)

    write_blind_file(deduped, args.out_dir / "subjects_blind.json")
    write_occupation_file(deduped, args.out_dir / "subjects_occupation.json")
    validate_blind_split(args.out_dir)

    counts = Counter(r.occupation_group for r in deduped)
    print("
--- Occupation Group Summary ---")
    for grp, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {grp:<22} {n:>5}")
    print(f"
  Total: {len(deduped)}")
    print(f"  Output: {args.out_dir.resolve()}")
    print("
  subjects_blind.json      -> pass to 02_batch_calculate.py")
    print("  subjects_occupation.json -> KEEP SEPARATE until 04_analyze.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())