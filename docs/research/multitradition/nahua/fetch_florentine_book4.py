"""Fetch Florentine Codex Book 4 folio records from the Getty backend API.

The Digital Florentine Codex frontend (florentinecodex.getty.edu) is a Next.js
application; its page HTML carries no readable text for a plain fetch. The
application's backend, however, serves complete folio records as JSON:

    https://dfc-be.ch.digtest.co.uk/codex/codex_folio/book/4/folio/{folio}/

Each record carries the stable folio UUID (the same IDs the validated
tonalpohualli pack cites), IIIF image URLs, and four text records per folio:
Nahuatl transcription, Nahuatl-to-English translation, Spanish transcription,
and Spanish-to-English translation, each with its own UUID, markdown, and
citation block.

This fetcher saves raw JSON witnesses under florentine_book4/ and maintains an
access manifest with SHA-256 hashes, so downstream encoding always points at a
pinned local witness rather than a live URL.

Usage:
    python fetch_florentine_book4.py 1r 1v 2r        # specific folios
    python fetch_florentine_book4.py --pilot          # the pilot witness set
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

BACKEND = "https://dfc-be.ch.digtest.co.uk/codex/codex_folio/book/4/folio/{folio}/"
OUT_DIR = Path(__file__).resolve().parent / "florentine_book4"
MANIFEST = OUT_DIR / "access_manifest.json"
USER_AGENT = "traditional-astrology-corpus-builder (research; contact repo owner)"
# Chapter 1 (Ce Cipactli) with lead-in, plus the opening of chapter 2.
PILOT_FOLIOS = ["1r", "1v", "2r", "2v", "3r", "3v", "4r", "4v", "5r", "5v"]
REQUEST_GAP_SECONDS = 1.5


def fetch_folio(folio: str) -> bytes:
    url = BACKEND.format(folio=folio)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status} for {url}")
        return response.read()


def summarize(record: dict) -> dict:
    texts = record.get("texts") or {}
    entries = []
    for column in ("nahuatl_col", "spanish_col"):
        for item in texts.get(column) or []:
            entries.append({
                "text_record_id": item.get("id"),
                "column": item.get("column"),
                "type": item.get("type"),
                "subtitle": item.get("subtitle"),
                "markdown_chars": len(item.get("markdown") or ""),
            })
    return {
        "folio_id": record.get("id"),
        "canvas_id": record.get("canvas_id"),
        "book_number": record.get("book_number"),
        "folio": (record.get("url") or {}).get("folio"),
        "text_records": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folios", nargs="*", help="Folio labels such as 1r 1v 2r")
    parser.add_argument("--pilot", action="store_true", help="Fetch the pilot set")
    args = parser.parse_args()

    folios = list(args.folios)
    if args.pilot:
        folios = PILOT_FOLIOS
    if not folios:
        parser.error("Provide folio labels or --pilot")

    OUT_DIR.mkdir(exist_ok=True)
    manifest: dict = (
        json.loads(MANIFEST.read_text(encoding="utf-8"))
        if MANIFEST.exists()
        else {
            "source": "Digital Florentine Codex backend API",
            "backend_url_pattern": BACKEND,
            "frontend": "https://florentinecodex.getty.edu/book/4/folio/{folio}",
            "rights_basis": (
                "16th-century Nahuatl and Spanish are public domain. The Getty "
                "digital edition's modern apparatus and translations carry their "
                "own citations, preserved verbatim inside each witness record. "
                "Downstream encoding quotes the public-domain transcription "
                "columns and renders translations independently; the stored "
                "witnesses serve as provenance, not as republication."
            ),
            "witnesses": {},
        }
    )

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    for index, folio in enumerate(folios):
        if index:
            time.sleep(REQUEST_GAP_SECONDS)
        raw = fetch_folio(folio)
        record = json.loads(raw)
        out_path = OUT_DIR / f"folio_{folio}.json"
        out_path.write_bytes(raw)
        digest = hashlib.sha256(raw).hexdigest()
        manifest["witnesses"][folio] = {
            "file": out_path.name,
            "sha256": digest,
            "bytes": len(raw),
            "retrieved": date.today().isoformat(),
            "summary": summarize(record),
        }
        print(f"{folio}: {len(raw)} bytes sha256={digest[:16]}... "
              f"({len(manifest['witnesses'][folio]['summary']['text_records'])} text records)")

    manifest["updated"] = date.today().isoformat()
    MANIFEST.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"manifest: {MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
