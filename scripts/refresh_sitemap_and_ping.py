"""Keep sitemap lastmod honest, then tell the crawlers.

Two jobs, deliberately in this order:

1. Rewrite every <lastmod> in src/static/sitemap.xml from the file's real last
   commit date, taken from git. Not "today" for everything - stamping an
   unchanged page as fresh is lying to a crawler, and crawlers that catch you
   doing it trust the whole sitemap less. Pages that genuinely have not changed
   keep their genuinely old date.

2. Submit the changed URLs to IndexNow, which fans out to Bing, Yandex, Seznam
   and Naver from one call. This does NOT reach Google (Google declined
   IndexNow and retired its own ping endpoint in 2023); Google discovers
   changes by recrawl, which is exactly why step 1 matters more than step 2.

Usage:
    python scripts/refresh_sitemap_and_ping.py            # rewrite + show diff, no network
    python scripts/refresh_sitemap_and_ping.py --submit   # rewrite + submit to IndexNow
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATIC = REPO / "src" / "static"
SITEMAP = STATIC / "sitemap.xml"
HOST = "traditional-astrology.com"
KEY_FILE = STATIC / "indexnow-key.txt"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/IndexNow"


def git_last_modified(path: Path) -> str | None:
    """Real last-commit date for a file, YYYY-MM-DD, or None if untracked."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(path.relative_to(REPO))],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        return out or None
    except subprocess.CalledProcessError:
        return None


def url_to_file(loc: str) -> Path | None:
    """Map a sitemap <loc> back to the static file that serves it."""
    path = loc.split(HOST, 1)[-1].lstrip("/") if HOST in loc else loc.lstrip("/")
    path = path.split("?", 1)[0].split("#", 1)[0]
    if not path or path.endswith("/"):
        path += "index.html"
    candidate = STATIC / path
    return candidate if candidate.is_file() else None


def refresh() -> tuple[str, list[str]]:
    original = SITEMAP.read_text(encoding="utf-8")
    changed: list[str] = []

    # Operate per <url> block so a <loc> is only ever paired with its own <lastmod>.
    def fix_block(match: re.Match[str]) -> str:
        block = match.group(0)
        loc_match = re.search(r"<loc>\s*([^<\s]+)\s*</loc>", block)
        if not loc_match:
            return block
        loc = loc_match.group(1)
        target = url_to_file(loc)
        if target is None:
            return block
        real_date = git_last_modified(target)
        if not real_date:
            return block

        def sub_lastmod(lm: re.Match[str]) -> str:
            if lm.group(1) != real_date:
                changed.append(loc)
            return f"<lastmod>{real_date}</lastmod>"

        new_block, n = re.subn(
            r"<lastmod>([^<]*)</lastmod>", sub_lastmod, block, count=1
        )
        if n == 0:
            # No lastmod present; add one after </loc> rather than leaving it blank.
            new_block = block.replace(
                loc_match.group(0),
                f"{loc_match.group(0)}\n    <lastmod>{real_date}</lastmod>",
                1,
            )
            changed.append(loc)
        return new_block

    updated = re.sub(r"<url>.*?</url>", fix_block, original, flags=re.S)
    return updated, changed


def submit(urls: list[str]) -> None:
    if not urls:
        print("nothing changed; no IndexNow submission needed")
        return
    if not KEY_FILE.is_file():
        sys.exit(f"missing IndexNow key file: {KEY_FILE}")
    key = KEY_FILE.read_text(encoding="utf-8").strip()

    payload = {
        "host": HOST,
        "key": key,
        "keyLocation": f"https://{HOST}/{key}.txt",
        "urlList": urls,
    }
    request = urllib.request.Request(
        INDEXNOW_ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            # 200 accepted, 202 accepted-pending-key-validation. Both are fine.
            print(f"IndexNow: HTTP {response.status} for {len(urls)} url(s)")
    except urllib.error.HTTPError as exc:
        print(f"IndexNow rejected the submission: HTTP {exc.code} {exc.reason}")
        print(exc.read().decode("utf-8", "replace")[:400])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--submit", action="store_true", help="POST changed URLs to IndexNow"
    )
    args = parser.parse_args()

    updated, changed = refresh()
    if updated != SITEMAP.read_text(encoding="utf-8"):
        SITEMAP.write_text(updated, encoding="utf-8")

    print(f"lastmod corrected for {len(changed)} url(s)")
    for loc in changed:
        print(f"  {loc}")

    if args.submit:
        submit(changed)
    elif changed:
        print("\n(dry run - re-run with --submit to notify IndexNow)")


if __name__ == "__main__":
    main()
