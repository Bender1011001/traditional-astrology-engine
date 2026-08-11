"""Composite scanned book pages into N-up images for reading.

Reading a scan as images costs tokens by AREA, not by how much text is on the
page. Ancient Greek tokenizes at roughly 2 characters per token, so a 4-up
composite (~2,200 tokens for ~8,000 characters) is about 1.8x CHEAPER than
reading the same pages transcribed to text. Compositing is therefore not a
convenience - it is the cheapest way to read these books at all.

The size cap matters. Grow the composite and the token cost grows with it, so
a 2x2 grid rendered large saves nothing. Hold the output to roughly one page's
pixel budget (~1560 on the long side) and the saving is real: ~549 tokens per
page against ~1,655 for a single page read alone.

At that budget the running text of a 1908 Teubner stays fully legible and the
apparatus criticus sits right at the limit. Sweep at 4-up; re-render a single
page at --per-image 1 whenever a variant reading actually bears on a rule.

    python scripts/composite_pages.py SRC.pdf OUT_DIR --start 60 --end 63
    python scripts/composite_pages.py SRC.pdf OUT_DIR --start 60 --count 40
    python scripts/composite_pages.py SRC.pdf OUT_DIR --start 60 --per-image 1
"""
from __future__ import annotations

import argparse
import pathlib

import fitz  # PyMuPDF
from PIL import Image

# Long-side pixel budget for the finished composite. Chosen to match the cost
# of a single-page read; raising it raises the token bill proportionally.
LONG_SIDE = 1560

# Per-page pixel budget is what governs legibility, not the page count. A 2x3
# grid of portrait pages is much taller than a 2x2, so capping the long side
# alone silently shrinks every page. Scale the cap with the row count instead.

# Render DPI per source page BEFORE downscaling. Supersampling well above the
# target and letting LANCZOS reduce it is what keeps the diacritics readable;
# rendering straight to the target size loses them.
RENDER_DPI = 400


def build(src: str, out_dir: str, start: int, end: int, per_image: int) -> list[pathlib.Path]:
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(src)
    end = min(end, doc.page_count - 1)

    cols = 1 if per_image == 1 else 2
    rows = (per_image + cols - 1) // cols
    written: list[pathlib.Path] = []

    for base in range(start, end + 1, per_image):
        group = [i for i in range(base, min(base + per_image, end + 1))]
        tiles = []
        for i in group:
            pm = doc[i].get_pixmap(dpi=RENDER_DPI)
            tiles.append(Image.frombytes("RGB", [pm.width, pm.height], pm.samples))

        w = max(t.width for t in tiles)
        h = max(t.height for t in tiles)
        grid = Image.new("RGB", (w * cols, h * rows), "white")
        for n, tile in enumerate(tiles):
            grid.paste(tile, ((n % cols) * w, (n // cols) * h))

        cap = LONG_SIDE * (rows / 2 if rows > 2 else 1)
        scale = cap / max(grid.size)
        if scale < 1:
            grid = grid.resize(
                (int(grid.width * scale), int(grid.height * scale)), Image.LANCZOS
            )

        name = f"p{group[0]:04d}-{group[-1]:04d}.png" if len(group) > 1 else f"p{group[0]:04d}.png"
        path = out / name
        grid.save(path)
        written.append(path)
        approx = grid.width * grid.height // 750
        print(f"{path.name}  {grid.width}x{grid.height}  ~{approx} tok  (~{approx // len(group)}/page)")

    return written


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("out_dir")
    ap.add_argument("--start", type=int, default=0, help="0-based PDF page index")
    ap.add_argument("--end", type=int, default=None)
    ap.add_argument("--count", type=int, default=None, help="pages from --start; alternative to --end")
    ap.add_argument("--per-image", type=int, default=4, choices=[1, 2, 4, 6, 8])
    args = ap.parse_args()

    if args.end is None:
        args.end = args.start + (args.count or args.per_image) - 1

    build(args.src, args.out_dir, args.start, args.end, args.per_image)


if __name__ == "__main__":
    main()
