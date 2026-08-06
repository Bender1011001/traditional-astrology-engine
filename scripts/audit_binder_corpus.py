#!/usr/bin/env python3
"""Generate JSON and Markdown audits of the local Binder1 corpus."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.services.binder_corpus import audit_binder_corpus, render_binder_audit_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        default="artifacts/binder-corpus-audit",
        help="Directory for binder_corpus_audit.json and .md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    audit = audit_binder_corpus()
    json_path = output_dir / "binder_corpus_audit.json"
    markdown_path = output_dir / "binder_corpus_audit.md"
    json_path.write_text(
        json.dumps(audit.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(render_binder_audit_markdown(audit), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
