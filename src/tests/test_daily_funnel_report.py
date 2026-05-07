from datetime import date

from scripts.daily_funnel_report import (
    RequestEvent,
    build_window,
    is_bot_or_test,
    summarize_logs,
)


def test_bot_detection_catches_known_crawlers_and_test_clients():
    assert is_bot_or_test("Mozilla/5.0 AppleWebKit compatible; bingbot/2.0")
    assert is_bot_or_test("Mozilla/5.0 HeadlessChrome/146.0.0.0")
    assert is_bot_or_test("Mozilla/5.0 PowerShell/7.6.1")
    assert not is_bot_or_test("Mozilla/5.0 Chrome/147.0.0.0 Safari/537.36")


def test_build_window_uses_local_midnight_and_utc_conversion():
    window = build_window("2026-05-01", 1, "America/Los_Angeles")

    assert window.start_local.date() == date(2026, 5, 1)
    assert window.start_local.hour == 0
    assert window.end_local.date() == date(2026, 5, 2)
    assert window.start_utc.hour == 7


def test_summarize_logs_counts_real_funnel_and_excludes_private_pages():
    received = [
        RequestEvent(
            timestamp="2026-05-01T12:00:00Z",
            action="request_received",
            method="GET",
            path="/",
            status_code=None,
            user_agent="Mozilla/5.0 Chrome/147.0.0.0 Safari/537.36",
            ip="203.0.113.10",
        ),
        RequestEvent(
            timestamp="2026-05-01T12:01:00Z",
            action="request_received",
            method="GET",
            path="/dashboard.html",
            status_code=None,
            user_agent="Mozilla/5.0 Chrome/147.0.0.0 Safari/537.36",
            ip="203.0.113.10",
        ),
        RequestEvent(
            timestamp="2026-05-01T12:02:00Z",
            action="request_received",
            method="GET",
            path="/sitemap.xml",
            status_code=None,
            user_agent="Mozilla/5.0 compatible; YandexBot/3.0",
            ip="198.51.100.4",
        ),
    ]
    completed = [
        RequestEvent(
            timestamp="2026-05-01T12:03:00Z",
            action="request_completed",
            method="POST",
            path="/api/v1/premium/guest/request",
            status_code=200,
            user_agent="",
            ip="203.0.113.10",
        ),
        RequestEvent(
            timestamp="2026-05-01T12:04:00Z",
            action="request_completed",
            method="POST",
            path="/api/v1/guest/checkout",
            status_code=500,
            user_agent="",
            ip="203.0.113.10",
        ),
    ]

    summary = summarize_logs(received, completed)

    assert summary["browser_like_page_views"] == 1
    assert summary["unique_browser_like_ips"] == 1
    assert summary["bot_or_test_requests"] == 1
    assert summary["top_public_pages"] == [("/", 1)]
    assert summary["free_chart_successes"] == 1
    assert summary["checkout_failures"] == 1
