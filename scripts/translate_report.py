"""Translate a generated reading into another language, preserving structure.

The report is deterministic markdown with evidence citations like [E44]. Those
citations, the markdown headings, and every number/date must survive translation
untouched — they are the audit trail that makes the report defensible.

Chunking is by top-level section so each request stays well inside context and a
failed chunk can be retried without redoing the whole document.

Usage:
    python scripts/translate_report.py <input.md> <output.md> --lang Russian
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine.chat_oracle import _openrouter_request  # noqa: E402

SYSTEM_PROMPT = """You are a professional translator specialising in historical \
and technical texts. You are translating a traditional (pre-1700) astrology \
reading from English into {lang}.

ABSOLUTE REQUIREMENTS — a violation makes the output unusable:

1. Preserve EVERY evidence citation exactly as written: [E1], [E44], [E102] etc.
   Never translate, renumber, reorder, merge, or drop them. They must remain in
   the same positions relative to the sentences they follow.
2. Preserve ALL markdown structure exactly: heading levels (##, ###), bold (**),
   italics, bullet markers, blockquotes, tables, and blank lines.
3. Preserve ALL numbers, degrees, dates, date ranges and ages EXACTLY as written
   (e.g. "Aquarius 11°27'13\"", "2059-2060", "age 72", "129 months", "39.5").
   Do not localise number formats. Do not convert date formats.
4. Proper names of planets, signs, lots and houses: use the standard {lang}
   astrological terms. Be consistent throughout — the same English term must map
   to the same {lang} term every time it appears.
5. Names of historical authorities stay recognisable in {lang} convention
   (Ptolemy, Valens, Dorotheus, Paulus, Lilly, al-Biruni, Firmicus, Ibn Ezra,
   Bonatti, Picatrix).
6. Keep the register formal, precise and sober. This is a technical document,
   not marketing copy. Do NOT add, remove, soften, embellish or explain
   anything. Translate what is there — including harsh or difficult statements.
   Any softening of severe testimony corrupts the document.
7. Output ONLY the translated markdown. No preamble, no commentary, no code
   fences around the whole document."""


def split_sections(markdown: str) -> list[str]:
    """Split on top-level (##) headings, keeping each heading with its body."""
    parts = re.split(r"\n(?=## )", markdown)
    chunks: list[str] = []
    buf = ""
    for part in parts:
        # Group small sections together to reduce request count, but never let a
        # chunk get large enough to risk truncation.
        if len(buf) + len(part) < 6000:
            buf = f"{buf}\n{part}" if buf else part
        else:
            if buf:
                chunks.append(buf)
            buf = part
    if buf:
        chunks.append(buf)
    return chunks


def verify_chunk(source: str, translated: str) -> list[str]:
    """Return a list of integrity problems found in a translated chunk."""
    problems: list[str] = []

    src_cites = re.findall(r"\[E\d+\]", source)
    out_cites = re.findall(r"\[E\d+\]", translated)
    if src_cites != out_cites:
        missing = set(src_cites) - set(out_cites)
        added = set(out_cites) - set(src_cites)
        if missing:
            problems.append(f"dropped citations: {sorted(missing)[:8]}")
        if added:
            problems.append(f"invented citations: {sorted(added)[:8]}")
        if not missing and not added:
            problems.append("citations reordered")

    src_heads = len(re.findall(r"^#{2,3} ", source, re.M))
    out_heads = len(re.findall(r"^#{2,3} ", translated, re.M))
    if src_heads != out_heads:
        problems.append(f"heading count {src_heads} -> {out_heads}")

    # Four-digit years must survive exactly.
    src_years = sorted(re.findall(r"\b(1[89]\d\d|20\d\d)\b", source))
    out_years = sorted(re.findall(r"\b(1[89]\d\d|20\d\d)\b", translated))
    if src_years != out_years:
        problems.append(f"year tokens changed ({len(src_years)} -> {len(out_years)})")

    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("output")
    ap.add_argument("--lang", default="Russian")
    ap.add_argument("--model", default=None)
    args = ap.parse_args()

    markdown = open(args.source, encoding="utf-8").read()
    chunks = split_sections(markdown)
    print(f"source: {len(markdown):,} chars in {len(chunks)} chunks -> {args.lang}")

    system = SYSTEM_PROMPT.format(lang=args.lang)
    out_parts: list[str] = []
    flagged: list[str] = []

    for i, chunk in enumerate(chunks, 1):
        translated = None
        for attempt in (1, 2):
            resp = _openrouter_request(
                [
                    {"role": "system", "content": system},
                    {"role": "user", "content": chunk},
                ],
                temperature=0.1,
                max_tokens=8000,
                model=args.model,
            )
            if isinstance(resp, str) and resp.startswith("Error:"):
                print(f"  chunk {i}/{len(chunks)}: API error: {resp[:90]}")
                time.sleep(3)
                continue
            problems = verify_chunk(chunk, resp)
            if not problems:
                translated = resp
                break
            print(f"  chunk {i}/{len(chunks)}: attempt {attempt} integrity: {problems}")
            translated = resp  # keep best effort
        if translated is None:
            print(f"  chunk {i}/{len(chunks)}: FAILED, keeping English")
            flagged.append(f"chunk {i}: untranslated")
            out_parts.append(chunk)
            continue
        problems = verify_chunk(chunk, translated)
        if problems:
            flagged.append(f"chunk {i}: {problems}")
        out_parts.append(translated)
        print(f"  chunk {i}/{len(chunks)}: ok ({len(translated):,} chars)")

    result = "\n\n".join(out_parts)
    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(result)

    print(f"\nwrote {args.output} ({len(result):,} chars)")
    src_c = len(re.findall(r"\[E\d+\]", markdown))
    out_c = len(re.findall(r"\[E\d+\]", result))
    print(f"citations: {src_c} source -> {out_c} translated")
    if flagged:
        print(f"\nINTEGRITY FLAGS ({len(flagged)}) — review before sending:")
        for f in flagged:
            print("  -", f)
        return 1
    print("integrity checks passed on every chunk")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
