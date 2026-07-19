"""Inspect and classify the local Binder1 research corpus.

Binder1 is a useful research index, but it concatenates original-text links,
academic research, practitioner material, and low-trust web discussion.  This
module makes that mixture explicit so report code cannot treat the whole file as
one undifferentiated authority.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ROOT_BINDER = ROOT / "Binder1.txt"
CANONICAL_BINDER = ROOT / "docs" / "research" / "Binder1.txt"

PRIMARY_REPOSITORIES = {
    "archive.org",
    "penelope.uchicago.edu",
    "quod.lib.umich.edu",
    "books.google.com",
    "upload.wikimedia.org",
    "sacred-texts.com",
    "ptolemaeus.badw.de",
}
ACADEMIC_REPOSITORIES = {
    "brill.com",
    "dlib.nyu.edu",
    "jstor.org",
    "cambridge.org",
    "oxfordacademic.com",
    "springer.com",
    "semanticscholar.org",
    "revistas.uma.es",
    "cultureandcosmos.org",
}
LOW_TRUST_DOMAINS = {
    "reddit.com",
    "en.wikipedia.org",
    "scribd.com",
    "youtube.com",
    "dokumen.pub",
    "vdoc.pub",
}

AUTHORITY_TERMS = (
    "Valens",
    "Dorotheus",
    "Bonatti",
    "Abu Ma",
    "Ibn Ezra",
    "Ptolemy",
    "William Lilly",
    "Paulus",
    "al-Biruni",
    "Picatrix",
    "Agrippa",
)


@dataclass(frozen=True)
class BinderAudit:
    canonical_path: str
    canonical_sha256: str
    canonical_bytes: int
    canonical_lines: int
    root_path: str
    root_sha256: str
    root_bytes: int
    root_is_exact_prefix: bool
    appended_bytes: int
    document_boundary_count: int
    url_count: int
    domain_count: int
    domain_tiers: dict[str, int]
    top_domains: list[dict[str, Any]]
    authority_mentions: dict[str, int]
    publication_policy: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _domain_tier(domain: str) -> str:
    if domain in PRIMARY_REPOSITORIES:
        return "primary_edition_repository"
    if domain in ACADEMIC_REPOSITORIES:
        return "academic_secondary"
    if domain in LOW_TRUST_DOMAINS:
        return "discovery_only_low_trust"
    return "unclassified_secondary"


def _domains(text: str) -> Counter[str]:
    # Domain extraction remains valid even when long URL paths are line-wrapped.
    found = re.findall(r"https?://(?:www\.)?([A-Za-z0-9.-]+)", text, re.IGNORECASE)
    return Counter(item.lower().rstrip(".") for item in found)


def audit_binder_corpus(
    root_path: Path = ROOT_BINDER,
    canonical_path: Path = CANONICAL_BINDER,
) -> BinderAudit:
    root_bytes = root_path.read_bytes()
    canonical_bytes = canonical_path.read_bytes()
    canonical_text = canonical_bytes.decode("utf-8", errors="replace")
    domains = _domains(canonical_text)
    tier_counts: Counter[str] = Counter()
    for domain, count in domains.items():
        tier_counts[_domain_tier(domain)] += count

    boundaries = len(
        re.findall(
            r"(?im)^\s*(?:works cited|references|bibliography)\s*:?[\s\ufeff]*$",
            canonical_text,
        )
    )
    authority_mentions = {
        term: len(re.findall(re.escape(term), canonical_text, re.IGNORECASE))
        for term in AUTHORITY_TERMS
    }
    top_domains = [
        {"domain": domain, "count": count, "tier": _domain_tier(domain)}
        for domain, count in domains.most_common(50)
    ]
    return BinderAudit(
        canonical_path=str(canonical_path),
        canonical_sha256=_sha256(canonical_bytes),
        canonical_bytes=len(canonical_bytes),
        canonical_lines=canonical_text.count("\n") + 1,
        root_path=str(root_path),
        root_sha256=_sha256(root_bytes),
        root_bytes=len(root_bytes),
        root_is_exact_prefix=canonical_bytes.startswith(root_bytes),
        appended_bytes=max(0, len(canonical_bytes) - len(root_bytes)),
        document_boundary_count=boundaries,
        url_count=sum(domains.values()),
        domain_count=len(domains),
        domain_tiers=dict(sorted(tier_counts.items())),
        top_domains=top_domains,
        authority_mentions=authority_mentions,
        publication_policy=(
            "Binder1 is a discovery and source-routing corpus. A Binder assertion "
            "cannot become a customer doctrine claim unless its cited edition is "
            "separately registered and text-verified."
        ),
    )


def render_binder_audit_markdown(audit: BinderAudit) -> str:
    lines = [
        "# Binder1 Corpus Audit",
        "",
        f"- Canonical file: `{audit.canonical_path}`",
        f"- Canonical SHA-256: `{audit.canonical_sha256}`",
        f"- Canonical size: {audit.canonical_bytes:,} bytes / {audit.canonical_lines:,} lines",
        f"- Root file is exact prefix: {audit.root_is_exact_prefix}",
        f"- Additional canonical material: {audit.appended_bytes:,} bytes",
        f"- Detected report/reference boundaries: {audit.document_boundary_count}",
        f"- Detected citation domains: {audit.domain_count} ({audit.url_count:,} URLs)",
        "",
        "## Publication policy",
        "",
        audit.publication_policy,
        "",
        "## Citation tiers",
        "",
    ]
    for tier, count in audit.domain_tiers.items():
        lines.append(f"- {tier}: {count}")
    lines.extend(["", "## Most frequent domains", "", "| Domain | Count | Tier |", "|---|---:|---|"])
    for item in audit.top_domains:
        lines.append(f"| {item['domain']} | {item['count']} | {item['tier']} |")
    lines.extend(["", "## Authority mentions", ""])
    for authority, count in audit.authority_mentions.items():
        lines.append(f"- {authority}: {count}")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The canonical Binder is extensive and should be searched first. It is not, however, a single primary source. It contains synthesized research reports and mixed-quality citations. Primary repositories are candidates for edition verification; academic sources can explain transmission and disagreement; unclassified practitioner sources are corroboration only; low-trust sources are discovery leads and cannot establish doctrine.",
            "",
        ]
    )
    return "\n".join(lines)

