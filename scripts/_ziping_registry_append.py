"""Append the two locally-opened BaZi page-image sources to the source registry.

Append-only: existing entries are never modified. Re-running is a no-op for ids
that already exist.
"""
from __future__ import annotations

import json
from pathlib import Path

REGISTRY = (
    Path(__file__).resolve().parents[1]
    / "docs" / "research" / "multitradition" / "source_registry.json"
)

NEW = [
    {
        "id": "bazi_sanming_tonghui_siku_zhejiang_local_page_images",
        "tradition": "chinese_bazi",
        "branch": "ming_interpretation",
        "title": "三命通會, complete 12-juan page-image set (Siku Quanshu recension, Zhejiang University Library 600 DPI scan), held locally",
        "author": "Wan Minying (萬民英); digitized by Zhejiang University Library; Qing-court 欽定四庫全書 recension",
        "repository": "local acquisition mirror of archive.org item 06056477.cn and siblings",
        "url": "https://archive.org/details/06056477.cn",
        "source_type": "photographic_facsimile_scan_of_a_named_dated_print_edition",
        "evidence_grade_target": "A",
        "status": "page_inspected",
        "page_count": 2746,
        "acquired_pdf_sha256": {
            "sanming_tonghui_juan01.pdf": "16f9fc8204ac0d7189320c105c5febc6662ec5f8a5ea34b7d1647a6694d440dd",
            "sanming_tonghui_juan02.pdf": "306e38d9fc0e683c36848f1d9b962b97acfd4de54c222549993e1a0706c961a3",
            "sanming_tonghui_juan03.pdf": "08cef96849244b7920bb4c39e99b9858ace9f452a349c0836612e6f453679bcf",
            "sanming_tonghui_juan04.pdf": "46d6156b27b3e709b3a74c829e0535f328239ad52b9876b8c7be2056b50be00a",
            "sanming_tonghui_juan05.pdf": "c72955c71543be849194d2054fee99718d756ac448e9c78cc477879c40e521fa",
            "sanming_tonghui_juan06.pdf": "c24c502e9e98fe3ac371e1164035e5803c40bd871d4095fb42367c688a404108",
            "sanming_tonghui_juan07.pdf": "20e7a9f4c1dfa6aafced80a4cdd08befec64e4d8df6efb5d8f96c49fd0cfb2f2",
            "sanming_tonghui_juan08.pdf": "fc287c5a69e735c5d4592cb5feca99061f878680fb5f4337903e837f82d891bc",
            "sanming_tonghui_juan09.pdf": "e5b28e6411e3dd45a40151d0df4595c415e1a4c56c2eb3578bde4baca98b211a",
            "sanming_tonghui_juan10.pdf": "ea88ae03cc8685fc7058ff7cd9f7b9eff2de6531d62e20b84b8b2e8cbfee62f7",
            "sanming_tonghui_juan11.pdf": "91ecc5e0d41c7597c305ea1f91e7af4f7c005ae2d8aa621fb693647927922247",
            "sanming_tonghui_juan12.pdf": "1ee06e81fa0ece8704ce7816a85dc608ede74c87cc9c4af4b1e1dc9f2c90e4c1",
        },
        "verified_scope": (
            "All twelve juan are held locally as per-juan PDFs at "
            "tmp/acquire/pdfs/sanming_tonghui_siku_zhejiang/sanming_tonghui_juan01..12.pdf, "
            "2,746 pages in total, SHA-256 recorded in bazi/source_audit.md. The embedded "
            "OCR text layer was checked and found unusable (garbled single characters, no "
            "coherent runs), so every rule sourced to this item was read from a RENDERED "
            "PAGE IMAGE at zoom 4.5-5.0 via scripts/_ziping_render.py. Juan 1 folio 2 "
            "carries the 欽定四庫全書 header and the Siku 提要, and juan 1 folio 1 names "
            "明 萬民英 撰 - the recension identity is therefore confirmed from the page "
            "itself, not from catalogue metadata. This is the first pass in which page "
            "images of this item were personally opened; the prior registry entry "
            "bazi_sanming_tonghui_siku_quanshu_zhejiang_scan records the metadata-only "
            "inspection it supersedes for evidence purposes without replacing."
        ),
        "rights_note": (
            "Underlying Ming/Qing print is public domain. The Zhejiang University Library "
            "digitization's own reuse terms were not displayed on the item page and remain "
            "unconfirmed; quotation here is limited to short passages with citation, which "
            "is the same footing as the rest of this corpus."
        ),
        "next_action": (
            "Collate the juan-12 case charts and the juan-6 named charts against a second, "
            "independent facsimile (the ANU Xu Dishan holding) to move from B to A grade, "
            "and commission independent Classical Chinese review of the encoded renderings."
        ),
    },
    {
        "id": "bazi_yuanhai_ziping_wanli_1600_local_page_images",
        "tradition": "chinese_bazi",
        "branch": "song_ziping_lineage",
        "title": "新刊合併官板音義評注淵海子平 (Yuanhai Ziping), dated Ming Wanli 28 (1600) print, page-image scan held locally",
        "author": (
            "attributed to the Xu Ziping lineage; compiled by Yang Cong (楊淙), "
            "supplemented by Li Qin (李欽), arranged by Tang Jinchi (唐錦池), Wanli 28 (1600)"
        ),
        "repository": "local acquisition mirror; Liu Longtian (劉龍田) blockprint witness",
        "url": "https://archive.org/details/yuanhai_ziping_ming_wanli_1600_liulongtian",
        "source_type": "photographic_facsimile_scan_of_a_named_dated_print_edition",
        "evidence_grade_target": "A",
        "status": "page_inspected",
        "page_count": 157,
        "acquired_pdf_bytes": 92240495,
        "acquired_pdf_sha256": (
            "7de1868a9c375e79e3b268900a0c055d0ba92b168bb0cfae7c929c4cbf355256"
        ),
        "acquired_source_archive_sha256": (
            "a56aa863dcbec19292f954be7ca91c071b1d9a387e00d422005f24197cb0bf1b"
        ),
        "verified_scope": (
            "Held locally as a 157-page PDF (each PDF page is a double-page spread, so "
            "roughly 314 half-leaves) at tmp/acquire/pdfs/yuanhai_ziping_ming_wanli_1600.pdf "
            "plus the matching JP2 archive, SHA-256 recorded in bazi/source_audit.md. The "
            "PDF carries NO text layer at all; every rule sourced to this item was read "
            "from a rendered page image at zoom 3.0. Chapter headings including 論起大運法 "
            "and 論起小運法 were read directly from the page. This is the DATED print the "
            "prior registry lead bazi_yuanhai_ziping_gugong_zhenben_facsimile_lead described "
            "but could not open; it supersedes the anonymous Wikisource and ctext "
            "transcriptions (bazi_yuanhai_ziping_wikisource, bazi_yuanhai_ziping_ctext) as "
            "the citable witness, and those two are retained for collation only."
        ),
        "rights_note": (
            "The 1600 blockprint is public domain. The specific digitization carries a "
            "visible institutional watermark on the leaves; reuse terms for the scan itself "
            "were not confirmed, so quotation is limited to short cited passages."
        ),
        "next_action": (
            "Complete the character-by-character collation of the verse layer (萬金賦, "
            "四言獨步, 五言獨步, 五行生克賦, 珞琭子消息賦) against the ctext transcription "
            "already encoded in yuanhai_ziping_delineation_manifest.json, and upgrade those "
            "22 rules' source_passages from the anonymous transcription to this print."
        ),
    },
]


def main() -> int:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    existing = {source["id"] for source in data["sources"]}
    added = []
    for entry in NEW:
        if entry["id"] in existing:
            continue
        data["sources"].append(entry)
        added.append(entry["id"])
    data["updated"] = "2026-08-05"
    REGISTRY.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("appended:", added or "(nothing new)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
