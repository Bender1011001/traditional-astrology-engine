"""Retrieve and line-address the Taisho witnesses used by the Sukuyodo pack.

The three acquired texts are CBETA's TEI P5 transcriptions of the Taisho
Tripitaka, volume 21:

    T1299  文殊師利菩薩及諸仙所說吉凶時日善惡宿曜經  (Xiuyao jing / Sukuyokyo)
    T1308  七曜攘災決                                (Qiyao rangzai jue)
    T1311  梵天火羅九曜                              (Bontenkara kuyo)

Running this script re-downloads each file, re-hashes it, and regenerates the
`*_lines.txt` rendering that every rule citation in this pack addresses. Line
keys look like `T21n1299_p0391b06`: Taisho volume 21, text 1299, page 391,
column b, line 06 - the same address CBETA and SAT print.

CBETA's own header states the terms: "Available for non-commercial use when
distributed with this header intact." The header is retained in the stored XML.

    python docs/research/multitradition/sukuyodo/fetch_sukuyo_sources.py
    python docs/research/multitradition/sukuyodo/fetch_sukuyo_sources.py --verify
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path
from xml.etree import ElementTree as ET

TEI = "{http://www.tei-c.org/ns/1.0}"
CB = "{http://www.cbeta.org/ns/1.0}"
BASE = "https://raw.githubusercontent.com/cbeta-org/xml-p5/master/T/T21"
WORKS = ("T21n1299", "T21n1308", "T21n1311")
SOURCES = Path(__file__).resolve().parent / "sources"
MANIFEST = SOURCES / "access_manifest.json"

# Elements whose content is apparatus, navigation, or editorial rather than
# text. `app` is handled separately so that only the lemma reading survives.
DROP = {TEI + "note", CB + "mulu", TEI + "anchor"}


def _flatten(el: ET.Element, out: list[tuple[str, str]]) -> None:
    tag = el.tag
    if tag == TEI + "lb":
        out.append(("LB", el.get("n") or ""))
    elif tag == TEI + "pb":
        pass
    elif tag == TEI + "app":
        lemma = el.find(TEI + "lem")
        if lemma is not None:
            for child in lemma:
                _flatten(child, out)
            if lemma.text:
                out.append(("T", lemma.text))
        if el.tail:
            out.append(("T", el.tail))
        return
    elif tag in DROP:
        if el.tail:
            out.append(("T", el.tail))
        return
    elif tag == CB + "juan":
        out.append(("MARK", f"[juan {el.get('n')} {el.get('fun')}]"))
    elif tag == TEI + "head":
        out.append(("MARK", "[head]"))
    elif tag == CB + "div":
        out.append(("MARK", f"[div {el.get('type')}]"))

    if el.text:
        out.append(("T", el.text))
    for child in el:
        _flatten(child, out)
    if el.tail:
        out.append(("T", el.tail))


def line_address(xml_path: Path, work_id: str) -> str:
    body = ET.parse(xml_path).getroot().find(f".//{TEI}body")
    if body is None:
        raise ValueError(f"No <body> in {xml_path}")
    tokens: list[tuple[str, str]] = []
    _flatten(body, tokens)

    order: list[str] = []
    lines: dict[str, list[str]] = {}
    current: str | None = None
    pending: list[str] = []
    for kind, value in tokens:
        if kind == "LB":
            current = value
            if current not in lines:
                lines[current] = []
                order.append(current)
            lines[current].extend(pending)
            pending = []
            continue
        text = value if kind == "MARK" else re.sub(r"\s+", "", value)
        if not text:
            continue
        (lines[current] if current is not None else pending).append(text)

    return "".join(f"{work_id}_p{ref}\t{''.join(lines[ref])}\n" for ref in order)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Re-hash local files against the manifest without downloading.",
    )
    args = parser.parse_args()
    SOURCES.mkdir(parents=True, exist_ok=True)
    recorded = json.loads(MANIFEST.read_text(encoding="utf-8"))["artifacts"]
    expected = {item["file"]: item["sha256"] for item in recorded}

    observed: dict[str, str] = {}
    for work in WORKS:
        xml_path = SOURCES / f"{work}.xml"
        if not args.verify:
            url = f"{BASE}/{work}.xml"
            with urllib.request.urlopen(url, timeout=120) as response:
                xml_path.write_bytes(response.read())
        text_path = SOURCES / f"{work}_lines.txt"
        if not args.verify:
            text_path.write_text(line_address(xml_path, work), encoding="utf-8")
        for path in (xml_path, text_path):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            observed[path.name] = digest

    drift = sorted(
        name
        for name, digest in observed.items()
        if name in expected and expected[name] != digest
    )
    print(json.dumps({"observed": observed, "hash_drift": drift}, indent=2))
    return 1 if drift else 0


if __name__ == "__main__":
    raise SystemExit(main())
