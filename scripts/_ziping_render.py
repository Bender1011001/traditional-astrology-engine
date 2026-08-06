"""Render page images from the BaZi source PDFs for visual transcription.

Usage:
  python scripts/_ziping_render.py <pdf-path> <first-page> <last-page> <outdir> [zoom]

Pages are 1-based and inclusive. Zoom defaults to 4.0 (Sanming Tonghui pages are
physically small, ~295x392 pt, so a high zoom is required for legibility).
"""
from __future__ import annotations

import os
import sys

import fitz


def main() -> int:
    pdf, first, last, outdir = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    zoom = float(sys.argv[5]) if len(sys.argv) > 5 else 4.0
    os.makedirs(outdir, exist_ok=True)
    doc = fitz.open(pdf)
    mat = fitz.Matrix(zoom, zoom)
    base = os.path.splitext(os.path.basename(pdf))[0]
    for n in range(first, min(last, doc.page_count) + 1):
        page = doc[n - 1]
        pix = page.get_pixmap(matrix=mat)
        path = os.path.join(outdir, f"{base}_p{n:04d}.png")
        pix.save(path)
        print(path, pix.width, pix.height)
    doc.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
