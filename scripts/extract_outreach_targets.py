import csv
import os
import re
from datetime import date


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SOURCE_PATH = os.path.join(ROOT, "docs", "research", "Gig Economy Astrologer Contact Research.txt")
OUT_DIR = os.path.join(ROOT, "docs", "outreach")
OUT_CSV = os.path.join(OUT_DIR, "outreach_targets.csv")


SEGMENT_BY_NAME = {
    # Institutional educators / teachers
    "Adam Elenbaas (Nightlight Astrology)": "teacher",
    "Debra Silverman": "teacher",
    "Helena Woods": "teacher",
    "Jules Ferrari (Golden Nature)": "teacher",
    "Vasilios Takos": "teacher",
    "Annie Botticelli": "teacher",
    # Content-first creators
    "Alice Bell": "content_creator",
    "Rowan Hogg": "content_creator",
    "Zina Star": "content_creator",
    "Aliza Kelly": "content_creator",
    "Leah Whitehorse": "content_creator",
    "Crypto Damus": "content_creator",
    "The Moon Lodge": "content_creator",
    # Marketplace sellers
    "MagicBrands (Etsy)": "pdf_seller",
    "SoulPurposeAstro (Etsy)": "pdf_seller",
    "Simply Elegant Style": "pdf_seller",
    "Layla Neris (Etsy)": "pdf_seller",
    "Aditi (AditiTheBrand)": "pdf_seller",
    "R Christoph (Fiverr)": "pdf_seller",
}


def guess_platform(primary: str, secondary: str) -> str:
    blob = f"{primary} {secondary}".lower()
    if "etsy" in blob:
        return "etsy"
    if "substack" in blob:
        return "substack"
    if "patreon" in blob:
        return "patreon"
    if "instagram" in blob or "ig:" in blob or "@" in secondary:
        return "instagram"
    if "contact form" in blob or "http" in blob or "www." in blob:
        return "website"
    if "gmail.com" in blob:
        return "email"
    return "other"


def normalize_line(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\ufeff", "")).strip()


def extract_records(text: str):
    lines = [normalize_line(l) for l in text.splitlines()]
    # Find the "Master Data Registry" table start.
    start_idx = None
    for i, l in enumerate(lines):
        if l == "Name/Entity":
            start_idx = i
            break
    if start_idx is None:
        raise RuntimeError("Could not find table header 'Name/Entity'")

    # Skip header lines until we hit first real name row.
    # The table has 4 lines per record: name, primary, secondary, notes.
    rows = []
    i = start_idx + 1
    # Drop empty and header-ish lines until the first entity name.
    while i < len(lines) and (
        (not lines[i])
        or ("primary email" in lines[i].lower())
        or ("secondary contact" in lines[i].lower())
        or ("notes / methodology" in lines[i].lower())
    ):
        i += 1

    while i < len(lines):
        l = lines[i]
        if not l:
            i += 1
            continue
        if l.startswith("________________") or l.startswith("7. "):
            break

        # Expect 4-line record. If the file formatting shifts, try to recover by skipping blanks.
        name = l
        parts = []
        j = i + 1
        while j < len(lines) and len(parts) < 3:
            if lines[j]:
                if lines[j].startswith("________________") or lines[j].startswith("7. "):
                    break
                parts.append(lines[j])
            j += 1

        if len(parts) < 3:
            # Give up; the remainder isn't parseable as expected.
            break

        primary, secondary, notes = parts[0], parts[1], parts[2]
        seg = SEGMENT_BY_NAME.get(name, "unknown")
        platform = guess_platform(primary, secondary)

        rows.append(
            {
                "name": name,
                "segment": seg,
                "platform_primary": platform,
                "primary_contact": primary,
                "secondary_contact": secondary,
                "notes": notes,
                "source": os.path.basename(SOURCE_PATH),
                "last_verified": date.today().isoformat(),
            }
        )
        i = j

    return rows


def main():
    if not os.path.exists(SOURCE_PATH):
        raise SystemExit(f"Missing source file: {SOURCE_PATH}")

    with open(SOURCE_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    records = extract_records(text)
    os.makedirs(OUT_DIR, exist_ok=True)

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "name",
                "segment",
                "platform_primary",
                "primary_contact",
                "secondary_contact",
                "notes",
                "source",
                "last_verified",
            ],
        )
        writer.writeheader()
        for r in records:
            writer.writerow(r)

    print(f"Wrote {len(records)} targets -> {OUT_CSV}")


if __name__ == "__main__":
    main()
