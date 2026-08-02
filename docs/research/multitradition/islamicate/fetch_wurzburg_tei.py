"""Fetch the Wurzburg Arabic/Latin TEI witnesses and pin them locally.

The access matrix already records every URL, byte count and SHA-256 from an
earlier verification pass, but discarded the files themselves. That made the
texts look "gated" when they are in fact CC BY-SA 4.0 and one HTTP GET away.

This fetcher re-downloads each artifact and verifies it against the recorded
hash, so the local copy is provably the same bytes that were audited.

    python fetch_wurzburg_tei.py --list
    python fetch_wurzburg_tei.py al_qabisi_introduction_arabic_tei
    python fetch_wurzburg_tei.py --all
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
MATRIX = HERE / "abu_mashar_al_qabisi_access_matrix.json"
OUT_DIR = HERE / "wurzburg_tei"
USER_AGENT = "traditional-astrology-corpus-builder (research)"
GAP_SECONDS = 1.5


def artifacts() -> list[dict]:
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    found = []
    for witness_set in matrix["witness_sets"]:
        for artifact in witness_set.get("artifacts", []):
            found.append({
                "witness_set_id": witness_set["witness_set_id"],
                "author_id": witness_set["author_id"],
                "work_id": witness_set["work_id"],
                **artifact,
            })
    return found


def fetch(artifact: dict) -> tuple[bytes, bool]:
    request = urllib.request.Request(
        artifact["url"], headers={"User-Agent": USER_AGENT}
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        body = response.read()
    digest = hashlib.sha256(body).hexdigest()
    return body, digest == artifact["sha256"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact_ids", nargs="*")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    available = artifacts()
    if args.list:
        for artifact in available:
            print(
                f"{artifact['artifact_id']:48} {artifact['language']:8} "
                f"{artifact['bytes']:>9,} B  {artifact['work_id']}"
            )
        return 0

    wanted = (
        available
        if args.all
        else [a for a in available if a["artifact_id"] in set(args.artifact_ids)]
    )
    if not wanted:
        parser.error("No matching artifacts; use --list to see ids")

    OUT_DIR.mkdir(exist_ok=True)
    failures = 0
    for index, artifact in enumerate(wanted):
        if index:
            time.sleep(GAP_SECONDS)
        body, matched = fetch(artifact)
        path = OUT_DIR / f"{artifact['artifact_id']}.xml"
        path.write_bytes(body)
        status = "hash OK" if matched else "HASH MISMATCH"
        if not matched:
            failures += 1
        print(f"{artifact['artifact_id']:48} {len(body):>9,} B  {status}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
