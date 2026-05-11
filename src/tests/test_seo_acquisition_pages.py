from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from src.app import app


ROOT = Path(__file__).resolve().parents[2]
STATIC = ROOT / "src" / "static"

ACQUISITION_PAGES = [
    "free-natal-chart-pdf.html",
    "astrology-reading-for-clients.html",
    "sect-astrology-calculator.html",
]

DEPRECATED_BUSINESS_PAGES = [
    "etsy-astrology-seller.html",
    "sell-astrology-readings-etsy.html",
    "astrology-client-birth-data.html",
    "traditional-astrology-vs-astrolabe.html",
    "astroforge-vs-astrolabe.html",
    "how-to-price-astrology-readings.html",
]


def test_site_uses_one_google_analytics_tag_path():
    files = [
        *STATIC.glob("*.html"),
        *STATIC.glob("blog/*.html"),
        *STATIC.glob("pt/*.html"),
        *STATIC.glob("sr/*.html"),
        ROOT / "src" / "templates" / "email" / "reset_password.html",
    ]

    for path in files:
        html = path.read_text(encoding="utf-8")
        assert "GTM-TJNM5XVD" not in html, str(path)
        assert "googletagmanager.com/gtm.js" not in html, str(path)
        assert "googletagmanager.com/ns.html" not in html, str(path)
        assert "G-RCNDWN4XVN" not in html, str(path)
        assert html.count("googletagmanager.com/gtag/js?id=") <= 1, str(path)
        if "googletagmanager.com/gtag/js?id=" in html:
            assert "googletagmanager.com/gtag/js?id=G-5T7HPNKL7V" in html, str(path)


def test_paid_flows_emit_single_deduped_ga4_purchase_event():
    config_js = (STATIC / "js" / "config.js").read_text(encoding="utf-8")
    reading_js = (STATIC / "js" / "reading-app.js").read_text(encoding="utf-8")
    horary_js = (STATIC / "js" / "horary-app.js").read_text(encoding="utf-8")
    sw_js = (STATIC / "sw.js").read_text(encoding="utf-8")
    homepage = (STATIC / "index.html").read_text(encoding="utf-8")
    natal = (STATIC / "natal-charts.html").read_text(encoding="utf-8")
    horary = (STATIC / "horary.html").read_text(encoding="utf-8")
    report_py = (ROOT / "scripts" / "daily_funnel_report.py").read_text(
        encoding="utf-8"
    )

    assert 'window.gtag("event", "purchase", payload)' in config_js
    assert "ta_purchase_tracked_${transactionId}" in config_js
    assert "trackPurchase(data.purchase" in reading_js
    assert "trackPurchase(data.purchase" in horary_js
    assert "/api/v1/horary/subscription/checkout" in horary_js
    assert "/api/v1/horary/subscriber-answer" in horary_js
    assert "/api/v1/horary/checkout" not in horary_js
    assert "/api/v1/horary/paid-answer" not in horary_js
    assert "astro-v22-geomancy-horary-subscription" in sw_js
    assert "/js/chart-graphics.js" in sw_js
    assert "/js/geomancy-app.js" in sw_js
    assert "js/reading-app.js?v=rev20260509bestwheel1" in homepage
    assert "/js/reading-app.js?v=rev20260509bestwheel1" in natal
    assert "js/horary-app.js?v=20260511horarysub1" in horary
    assert "$5/month" in horary
    assert "$1" not in horary
    assert 'GA4_MEASUREMENT_ID = "G-5T7HPNKL7V"' in report_py
    assert 'GA4_MEASUREMENT_ID = "G-RCNDWN4XVN"' not in report_py


def test_geomancy_page_is_indexable_and_uses_real_api():
    html = (STATIC / "geomancy.html").read_text(encoding="utf-8")
    js = (STATIC / "js" / "geomancy-app.js").read_text(encoding="utf-8")
    sitemap = (STATIC / "sitemap.xml").read_text(encoding="utf-8")

    assert '<meta name="robots" content="index,follow" />' in html
    assert "https://traditional-astrology.com/geomancy.html" in html
    assert "G-5T7HPNKL7V" in html
    assert "GTM-TJNM5XVD" not in html
    assert "/api/v1/geomancy/cast" in js
    assert "mother_counts" in js
    assert "Historical Use Only" in html
    assert "What Is Geomancy?" in html
    assert "The Strict Rules" in html
    assert "Judge Validity" in html
    assert "$5/month" in html
    assert "https://traditional-astrology.com/geomancy.html" in sitemap


def test_chart_wheel_renders_traditional_astrology_structure():
    chart_js = (STATIC / "js" / "chart-graphics.js").read_text(encoding="utf-8")

    assert "Traditional astrology natal chart" in chart_js
    assert "SIGN_GLYPHS" in chart_js
    assert "ROMAN_HOUSES" in chart_js
    assert "zodiac-glyph" in chart_js
    assert "degree-tick" in chart_js
    assert "house-number" in chart_js
    assert "angle-label" in chart_js
    assert "aspect-line" in chart_js
    assert "planet-label" in chart_js
    assert "TERRA" not in chart_js


def test_acquisition_pages_are_indexable_gtag_only_and_direct_to_funnel():
    for page in ACQUISITION_PAGES:
        html = (STATIC / page).read_text(encoding="utf-8")

        assert '<meta name="robots" content="index,follow"/>' in html
        assert f"https://traditional-astrology.com/{page}" in html
        assert "G-5T7HPNKL7V" in html
        assert "G-RCNDWN4XVN" not in html
        assert "GTM-TJNM5XVD" not in html
        assert "googletagmanager.com/gtm.js" not in html
        assert "googletagmanager.com/ns.html" not in html
        assert 'href="/#get-reading"' in html
        assert "Not medical, legal, or financial advice" in html


def test_acquisition_pages_are_in_sitemap():
    sitemap = (STATIC / "sitemap.xml").read_text(encoding="utf-8")

    for page in ACQUISITION_PAGES:
        assert f"https://traditional-astrology.com/{page}" in sitemap


def test_sitemap_keeps_live_pages_and_excludes_retired_business_pages():
    sitemap = (STATIC / "sitemap.xml").read_text(encoding="utf-8")

    assert "https://traditional-astrology.com/blog.html" in sitemap
    for page in DEPRECATED_BUSINESS_PAGES:
        assert f"https://traditional-astrology.com/{page}" not in sitemap


def test_robots_disallows_retired_business_pages_without_blocking_blog():
    robots = (STATIC / "robots.txt").read_text(encoding="utf-8")

    assert "Disallow: /blog.html" not in robots
    for page in DEPRECATED_BUSINESS_PAGES:
        assert f"Disallow: /{page}" in robots


@pytest.mark.asyncio
@pytest.mark.parametrize("page", DEPRECATED_BUSINESS_PAGES)
async def test_retired_business_pages_redirect_to_customer_funnel(page):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False
    ) as ac:
        response = await ac.get(f"/{page}")

    assert response.status_code == 301
    assert response.headers["location"] == "/#get-reading"
