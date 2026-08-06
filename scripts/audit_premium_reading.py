"""Audit a generated premium reading for depth, safety, and PDF integrity."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.services.reading_contract import validate_customer_reading


SEPTENER = ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn")
REQUIRED_H1 = (
    "Your Nativity at a Glance",
    "The Leading Testimonies",
    "Life Topics",
    "The Present Chapter",
    "Where the Sources Differ",
    "Method and Limits",
)


def audit_reading(
    markdown_path: Path,
    pdf_path: Path,
    *,
    minimum_words: int = 6_000,
    minimum_pages: int = 15,
    minimum_evidence_items: int = 45,
) -> dict[str, object]:
    markdown = markdown_path.read_text(encoding="utf-8")
    words = re.findall(r"\b[\w'’-]+\b", markdown)
    evidence_ids = sorted(set(re.findall(r"\[(E\d+)\]", markdown)))
    violations = [
        {"code": item.code, "message": item.message, "excerpt": item.excerpt}
        for item in validate_customer_reading(
            markdown,
            minimum_words=minimum_words,
            maximum_words=20_000,
        )
    ]

    missing_h1 = [
        heading for heading in REQUIRED_H1
        if markdown.count(f"# {heading}") != 1
    ]
    missing_planets = [
        planet for planet in SEPTENER if f"### {planet}" not in markdown
    ]
    missing_houses = [
        house for house in range(1, 13)
        if not re.search(rf"^## House {house}:", markdown, re.MULTILINE)
    ]

    reader = PdfReader(str(pdf_path))
    page_words = [len((page.extract_text() or "").split()) for page in reader.pages]
    sparse_interior_pages = [
        index + 1
        for index, count in enumerate(page_words)
        if 0 < index < len(page_words) - 1 and count < 80
    ]

    failures: list[str] = []
    if violations:
        failures.append("publication_contract")
    if missing_h1:
        failures.append("top_level_structure")
    if missing_planets:
        failures.append("septener_coverage")
    if missing_houses:
        failures.append("twelve_place_coverage")
    if len(evidence_ids) < minimum_evidence_items:
        failures.append("evidence_depth")
    if len(reader.pages) < minimum_pages:
        failures.append("pdf_depth")
    if sparse_interior_pages:
        failures.append("sparse_interior_pages")

    return {
        "status": "pass" if not failures else "fail",
        "markdown": str(markdown_path.resolve()),
        "pdf": str(pdf_path.resolve()),
        "markdown_words": len(words),
        "pdf_pages": len(reader.pages),
        "pdf_page_words": page_words,
        "unique_evidence_items": len(evidence_ids),
        "missing_top_level_headings": missing_h1,
        "missing_planets": missing_planets,
        "missing_houses": missing_houses,
        "sparse_interior_pages": sparse_interior_pages,
        "publication_violations": violations,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("markdown", type=Path)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--minimum-words", type=int, default=6_000)
    parser.add_argument("--minimum-pages", type=int, default=15)
    parser.add_argument("--minimum-evidence-items", type=int, default=45)
    args = parser.parse_args()

    result = audit_reading(
        args.markdown,
        args.pdf,
        minimum_words=args.minimum_words,
        minimum_pages=args.minimum_pages,
        minimum_evidence_items=args.minimum_evidence_items,
    )
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
