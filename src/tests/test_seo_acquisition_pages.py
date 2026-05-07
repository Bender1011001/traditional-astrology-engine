from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STATIC = ROOT / "src" / "static"

ACQUISITION_PAGES = [
    "free-natal-chart-pdf.html",
    "astrology-reading-for-clients.html",
    "sect-astrology-calculator.html",
]


def test_acquisition_pages_are_indexable_gtag_only_and_direct_to_funnel():
    for page in ACQUISITION_PAGES:
        html = (STATIC / page).read_text(encoding="utf-8")

        assert '<meta name="robots" content="index,follow"/>' in html
        assert f'https://traditional-astrology.com/{page}' in html
        assert "G-RCNDWN4XVN" in html
        assert "GTM-TJNM5XVD" not in html
        assert "googletagmanager.com/gtm.js" not in html
        assert "googletagmanager.com/ns.html" not in html
        assert 'href="/#get-reading"' in html
        assert "Not medical, legal, or financial advice" in html


def test_acquisition_pages_are_in_sitemap():
    sitemap = (STATIC / "sitemap.xml").read_text(encoding="utf-8")

    for page in ACQUISITION_PAGES:
        assert f"https://traditional-astrology.com/{page}" in sitemap
