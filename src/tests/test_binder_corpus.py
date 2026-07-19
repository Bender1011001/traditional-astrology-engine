from pathlib import Path

from src.services.binder_corpus import audit_binder_corpus, render_binder_audit_markdown


def test_binder_audit_classifies_mixed_sources(tmp_path: Path):
    root = tmp_path / "Binder1.txt"
    canonical = tmp_path / "canonical.txt"
    root.write_text("Ptolemy\nhttps://archive.org/details/example\n", encoding="utf-8")
    canonical.write_text(
        root.read_text(encoding="utf-8")
        + "Works cited\nhttps://reddit.com/r/example\nhttps://brill.com/book\nValens\n",
        encoding="utf-8",
    )
    audit = audit_binder_corpus(root, canonical)
    assert audit.root_is_exact_prefix is True
    assert audit.appended_bytes > 0
    assert audit.url_count == 3
    assert audit.domain_tiers["primary_edition_repository"] == 1
    assert audit.domain_tiers["academic_secondary"] == 1
    assert audit.domain_tiers["discovery_only_low_trust"] == 1
    assert audit.authority_mentions["Ptolemy"] == 1
    assert audit.authority_mentions["Valens"] == 1


def test_binder_markdown_states_publication_boundary(tmp_path: Path):
    root = tmp_path / "Binder1.txt"
    canonical = tmp_path / "canonical.txt"
    root.write_text("base", encoding="utf-8")
    canonical.write_text("base\nhttps://scribd.com/example", encoding="utf-8")
    rendered = render_binder_audit_markdown(audit_binder_corpus(root, canonical))
    assert "discovery and source-routing corpus" in rendered
    assert "scribd.com" in rendered
    assert "discovery_only_low_trust" in rendered

