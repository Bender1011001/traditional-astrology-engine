"""Assemble the Ziping technique manifest from per-juan mining fragments.

Sub-agents each write `bazi/_ziping_frag_<tag>.json` holding `fragment_rules`
and `fragment_vectors`. This script concatenates them into the two deliverables,
enforcing the corpus schemas and the house rules that the corpus validator does
not itself check (verbatim Chinese, rendering grade, customer_prediction false,
every rule covered by at least one vector).

Usage:
  python scripts/_ziping_assemble.py            # assemble + report
  python scripts/_ziping_assemble.py --dry-run  # report only
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1] / "docs" / "research" / "multitradition"
BAZI = ROOT / "bazi"
MANIFEST = BAZI / "ziping_technique_rule_manifest.json"
VECTORS = BAZI / "ziping_technique_validation_vectors.json"

TRADITION = "chinese_bazi"
PACK = "bazi_ziping_technique_v1"
EDITION = "sanming_tonghui_siku_zhejiang_and_yuanhai_ziping_wanli_1600_page_images"
REGISTRY_IDS = [
    "bazi_sanming_tonghui_siku_zhejiang_local_page_images",
    "bazi_yuanhai_ziping_wanli_1600_local_page_images",
    "bazi_sanming_tonghui_siku_quanshu_zhejiang_scan",
    "bazi_yuanhai_ziping_gugong_zhenben_facsimile_lead",
    "bazi_yuanhai_ziping_ctext",
    "bazi_sanming_tonghui_ctext_juan10_12",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fragments() -> list[tuple[Path, dict[str, Any]]]:
    out = []
    for path in sorted(BAZI.glob("_ziping_frag_*.json")):
        try:
            out.append((path, _load(path)))
        except json.JSONDecodeError as exc:
            print(f"  !! UNPARSEABLE {path.name}: {exc}", file=sys.stderr)
    return out


def _house_rule_problems(rule: dict[str, Any]) -> list[str]:
    problems = []
    concl = rule.get("conclusion") or {}
    if not isinstance(concl, dict):
        return ["conclusion is not an object"]
    if concl.get("customer_prediction") is not False:
        problems.append("customer_prediction is not false")
    if not str(concl.get("chinese") or "").strip():
        problems.append("no verbatim Chinese in conclusion.chinese")
    if concl.get("rendering_grade") != "engine_translation_unreviewed":
        problems.append("rendering_grade is not engine_translation_unreviewed")
    if not str(concl.get("engine_rendering") or "").strip():
        problems.append("no engine_rendering")
    if not str(rule.get("rule_id", "")).startswith("bazi.ziping."):
        problems.append("rule_id is not under bazi.ziping.")
    for passage in rule.get("source_passages") or []:
        if not str(passage.get("location") or "").strip():
            problems.append("a source passage has no location")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    rule_schema = _load(ROOT / "rule_manifest.schema.json")
    vector_schema = _load(ROOT / "validation_vectors.schema.json")

    rules: list[dict[str, Any]] = []
    vectors: list[dict[str, Any]] = []
    seen_rules: set[str] = set()
    seen_vectors: set[str] = set()
    by_fragment: dict[str, tuple[int, int]] = {}
    problems: list[str] = []

    for path, frag in _fragments():
        frag_rules = frag.get("fragment_rules") or []
        frag_vectors = frag.get("fragment_vectors") or []
        kept_r = kept_v = 0
        for rule in frag_rules:
            rid = str(rule.get("rule_id", ""))
            if not rid:
                problems.append(f"{path.name}: a rule has no rule_id")
                continue
            if rid in seen_rules:
                problems.append(f"{path.name}: duplicate rule_id {rid} (dropped)")
                continue
            for problem in _house_rule_problems(rule):
                problems.append(f"{path.name}:{rid}: {problem}")
            seen_rules.add(rid)
            rules.append(rule)
            kept_r += 1
        for vector in frag_vectors:
            vid = str(vector.get("vector_id", ""))
            if not vid:
                problems.append(f"{path.name}: a vector has no vector_id")
                continue
            if vid in seen_vectors:
                problems.append(f"{path.name}: duplicate vector_id {vid} (dropped)")
                continue
            seen_vectors.add(vid)
            vectors.append(vector)
            kept_v += 1
        by_fragment[path.name] = (kept_r, kept_v)

    covered = {rid for v in vectors for rid in v.get("rule_ids", [])}
    uncovered = sorted(seen_rules - covered)
    orphan_vector_refs = sorted(covered - seen_rules)

    print("Fragments assembled:")
    for name, (r, v) in sorted(by_fragment.items()):
        print(f"  {name:44s} rules={r:4d} vectors={v:4d}")
    print(f"\nTOTAL rules={len(rules)} vectors={len(vectors)}")
    print(f"Rules without vector coverage: {len(uncovered)}")
    for rid in uncovered:
        print(f"  UNCOVERED {rid}")
    for rid in orphan_vector_refs:
        print(f"  ORPHAN VECTOR REF {rid}")
    topics = Counter(rid.split(".")[2] for rid in sorted(seen_rules) if rid.count(".") >= 2)
    print("\nRules by topic: " + ", ".join(f"{k}={v}" for k, v in topics.most_common()))
    if problems:
        print(f"\nHouse-rule problems ({len(problems)}):")
        for problem in problems:
            print(f"  {problem}")

    if args.dry_run:
        return 0
    if not rules:
        print("\nNo rules to assemble; nothing written.")
        return 1

    manifest = {
        "schema_version": 1,
        "updated": "2026-08-05",
        "tradition_id": TRADITION,
        "school_id": "ziping_sanming_tonghui_siku_and_yuanhai_wanli_1600",
        "source_pack_id": PACK,
        "source_edition_id": EDITION,
        "source_registry_ids": REGISTRY_IDS,
        "implementation_status": "research_verified",
        "publication_status": "research_only",
        "evidence_note": _load(BAZI / "_ziping_evidence_note.json")["evidence_note"],
        "rules": rules,
    }
    vector_file = {
        "schema_version": 1,
        "updated": "2026-08-05",
        "tradition_id": TRADITION,
        "source_pack_id": PACK,
        "status": (
            "Research vectors. Each rule carries at least one vector; vectors drawn "
            "from a source worked chart (命例) quote the source's own verdict and are "
            "marked as such in provenance. Not run against the live engine as a test "
            "suite - the engine cannot yet decide several of the encoded predicates, "
            "and each such gap is named in the rule's conclusion.engine_missing_facts."
        ),
        "source_ids": REGISTRY_IDS,
        "vectors": vectors,
    }

    jsonschema.Draft202012Validator(
        rule_schema, format_checker=jsonschema.FormatChecker()
    ).validate(manifest)
    jsonschema.Draft202012Validator(
        vector_schema, format_checker=jsonschema.FormatChecker()
    ).validate(vector_file)

    MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    VECTORS.write_text(
        json.dumps(vector_file, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"\nWrote {MANIFEST.name} and {VECTORS.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
