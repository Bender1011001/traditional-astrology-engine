"""Production revenue funnel report from Cloud Run logs and Stripe.

This script intentionally avoids GA4 headline metrics. It reconciles the
operational funnel from server logs plus Stripe so bot/test traffic and private
page noise do not look like customer demand.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


DEFAULT_PROJECT = "astrology-engine-prod"
DEFAULT_REGION = "us-central1"
DEFAULT_SERVICE = "astrology-engine"
DEFAULT_TIMEZONE = "America/Los_Angeles"
DEFAULT_LIMIT = 5000

GA4_MEASUREMENT_ID = "G-RCNDWN4XVN"

BOT_OR_TEST_RE = re.compile(
    r"bot|crawler|spider|headless|chatgpt|claude|googleother|"
    r"google-inspectiontool|powershell|curl|python|go-http-client|builtwith|"
    r"stripebot|bytespider|yandex|ahrefs|petalbot|meta-externalagent|"
    r"oai-searchbot|amazonbot|bingbot|facebookexternalhit|lighthouse",
    re.IGNORECASE,
)

ASSET_EXTENSIONS = {
    ".css",
    ".js",
    ".png",
    ".jpg",
    ".jpeg",
    ".ico",
    ".svg",
    ".webp",
    ".woff",
    ".woff2",
    ".map",
    ".json",
    ".xml",
    ".txt",
}

PRIVATE_OR_LEGACY_PATHS = {
    "/dashboard",
    "/dashboard/",
    "/dashboard.html",
    "/login.html",
    "/register.html",
    "/signup.html",
    "/profile.html",
    "/forgot-password.html",
    "/reset-password.html",
    "/owner.html",
}


@dataclass(frozen=True)
class Window:
    start_local: datetime
    end_local: datetime
    start_utc: datetime
    end_utc: datetime


@dataclass(frozen=True)
class RequestEvent:
    timestamp: str
    action: str
    method: str
    path: str
    status_code: int | None
    user_agent: str
    ip: str


@dataclass(frozen=True)
class StripeSummary:
    available: bool
    checkout_sessions: int = 0
    paid_sessions: int = 0
    unpaid_sessions: int = 0
    expired_sessions: int = 0
    succeeded_payment_intents: int = 0
    gross_paid_cents: int = 0
    error: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report the production chart-to-payment funnel from Cloud Run logs and Stripe."
    )
    parser.add_argument("--project", default=DEFAULT_PROJECT)
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--service", default=DEFAULT_SERVICE)
    parser.add_argument("--timezone", default=DEFAULT_TIMEZONE)
    parser.add_argument(
        "--date",
        help="Local report start date in YYYY-MM-DD. Defaults to today in --timezone.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="Number of local days to include from --date.",
    )
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument(
        "--skip-stripe",
        action="store_true",
        help="Only report Cloud Run funnel logs; do not call Stripe.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON instead of the text report.",
    )
    return parser.parse_args()


def load_env_file(path: Path) -> None:
    """Load KEY=value or KEY: value files without printing secrets."""
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*[:=]\s*(.*)$", line)
        if not match:
            continue

        key, value = match.groups()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


def load_project_env() -> None:
    root = Path(__file__).resolve().parents[1]
    load_env_file(root / ".env")
    load_env_file(root / "env.yaml")


def build_window(date_arg: str | None, days: int, tz_name: str) -> Window:
    if days < 1:
        raise ValueError("--days must be >= 1")

    tz = ZoneInfo(tz_name)
    start_date = date.fromisoformat(date_arg) if date_arg else datetime.now(tz).date()
    start_local = datetime.combine(start_date, time.min, tzinfo=tz)
    end_local = start_local + timedelta(days=days)
    return Window(
        start_local=start_local,
        end_local=end_local,
        start_utc=start_local.astimezone(timezone.utc),
        end_utc=end_local.astimezone(timezone.utc),
    )


def cloud_logging_timestamp(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def run_gcloud_logging_read(
    *,
    project: str,
    region: str,
    service: str,
    window: Window,
    action: str,
    limit: int,
) -> list[dict[str, Any]]:
    gcloud = shutil.which("gcloud") or shutil.which("gcloud.cmd") or shutil.which("gcloud.ps1")
    if not gcloud:
        raise RuntimeError("gcloud CLI was not found on PATH")

    query = (
        'resource.type="cloud_run_revision" '
        f'AND resource.labels.service_name="{service}" '
        f'AND resource.labels.location="{region}" '
        f'AND timestamp>="{cloud_logging_timestamp(window.start_utc)}" '
        f'AND timestamp<"{cloud_logging_timestamp(window.end_utc)}" '
        f'AND jsonPayload.action="{action}"'
    )
    command = [
        gcloud,
        "logging",
        "read",
        query,
        "--project",
        project,
        "--limit",
        str(limit),
        "--format=json",
    ]
    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "gcloud logging read failed")
    return json.loads(result.stdout or "[]")


def parse_log_entries(entries: list[dict[str, Any]]) -> list[RequestEvent]:
    events: list[RequestEvent] = []
    for entry in entries:
        payload = entry.get("jsonPayload") or {}
        details = payload.get("details") or {}
        status_raw = details.get("status_code")
        try:
            status_code = int(status_raw) if status_raw is not None else None
        except (TypeError, ValueError):
            status_code = None

        events.append(
            RequestEvent(
                timestamp=str(entry.get("timestamp") or payload.get("timestamp") or ""),
                action=str(payload.get("action") or ""),
                method=str(details.get("method") or "").upper(),
                path=normalize_path(str(details.get("path") or "")),
                status_code=status_code,
                user_agent=str(details.get("user_agent") or ""),
                ip=str(payload.get("ip") or ""),
            )
        )
    return events


def normalize_path(path: str) -> str:
    if not path:
        return "/"
    return path.split("?", 1)[0] or "/"


def is_bot_or_test(user_agent: str) -> bool:
    return bool(BOT_OR_TEST_RE.search(user_agent or ""))


def is_asset_or_infra_path(path: str) -> bool:
    suffix = Path(path).suffix.lower()
    if suffix in ASSET_EXTENSIONS:
        return True
    return path in {"/robots.txt", "/sitemap.xml", "/manifest.json", "/favicon.ico"}


def is_public_html_view(event: RequestEvent) -> bool:
    if event.method != "GET":
        return False
    if event.path.startswith("/api/"):
        return False
    if event.path in PRIVATE_OR_LEGACY_PATHS:
        return False
    if is_asset_or_infra_path(event.path):
        return False
    return event.path == "/" or event.path.endswith(".html")


def count_completed(
    events: list[RequestEvent], *, method: str, path: str, status_min: int, status_max: int
) -> int:
    return sum(
        1
        for event in events
        if event.method == method
        and event.path == path
        and event.status_code is not None
        and status_min <= event.status_code <= status_max
    )


def summarize_logs(
    received_events: list[RequestEvent], completed_events: list[RequestEvent]
) -> dict[str, Any]:
    browser_received = [
        event for event in received_events if not is_bot_or_test(event.user_agent)
    ]
    bot_or_test_received = [
        event for event in received_events if is_bot_or_test(event.user_agent)
    ]
    browser_page_views = [
        event for event in browser_received if is_public_html_view(event)
    ]
    unique_browser_ips = {
        event.ip
        for event in browser_page_views
        if event.ip and event.ip not in {"unknown", "169.254.169.126"}
    }

    public_page_counter = Counter(event.path for event in browser_page_views)
    bot_counter = Counter(classify_bot_or_test(event.user_agent) for event in bot_or_test_received)

    return {
        "received_requests": len(received_events),
        "browser_like_requests": len(browser_received),
        "bot_or_test_requests": len(bot_or_test_received),
        "browser_like_page_views": len(browser_page_views),
        "unique_browser_like_ips": len(unique_browser_ips),
        "top_public_pages": public_page_counter.most_common(10),
        "bot_or_test_breakdown": bot_counter.most_common(),
        "free_chart_successes": count_completed(
            completed_events,
            method="POST",
            path="/api/v1/premium/guest/request",
            status_min=200,
            status_max=299,
        ),
        "free_chart_failures": count_completed(
            completed_events,
            method="POST",
            path="/api/v1/premium/guest/request",
            status_min=400,
            status_max=599,
        ),
        "checkout_sessions_created": count_completed(
            completed_events,
            method="POST",
            path="/api/v1/guest/checkout",
            status_min=200,
            status_max=299,
        ),
        "checkout_failures": count_completed(
            completed_events,
            method="POST",
            path="/api/v1/guest/checkout",
            status_min=400,
            status_max=599,
        ),
        "paid_generation_started": count_completed(
            completed_events,
            method="POST",
            path="/api/v1/guest/generate-paid",
            status_min=200,
            status_max=299,
        ),
        "paid_generation_failures": count_completed(
            completed_events,
            method="POST",
            path="/api/v1/guest/generate-paid",
            status_min=400,
            status_max=599,
        ),
    }


def classify_bot_or_test(user_agent: str) -> str:
    ua = user_agent.lower()
    if "bingbot" in ua:
        return "Bing bot"
    if "google" in ua:
        return "Google bot/tool"
    if "yandex" in ua:
        return "Yandex bot"
    if "ahrefs" in ua:
        return "Ahrefs bot"
    if "bytespider" in ua:
        return "Bytespider"
    if "claude" in ua:
        return "Claude bot"
    if "chatgpt" in ua or "oai-searchbot" in ua:
        return "OpenAI bot"
    if "powershell" in ua or "headless" in ua or "curl" in ua or "python" in ua:
        return "Test/scanner"
    if "bot" in ua or "crawler" in ua or "spider" in ua:
        return "Other bot"
    return "Other test/noise"


def fetch_stripe_summary(window: Window) -> StripeSummary:
    api_key = os.getenv("STRIPE_SECRET_KEY", "").strip()
    if not api_key:
        return StripeSummary(available=False, error="STRIPE_SECRET_KEY is not set")

    try:
        import stripe

        stripe.api_key = api_key
        created = {
            "gte": int(window.start_utc.timestamp()),
            "lt": int(window.end_utc.timestamp()),
        }

        sessions = list(
            stripe.checkout.Session.list(limit=100, created=created).auto_paging_iter()
        )
        payment_intents = list(
            stripe.PaymentIntent.list(limit=100, created=created).auto_paging_iter()
        )
    except Exception as exc:  # Stripe/gcloud failures should be visible and explicit.
        return StripeSummary(available=False, error=repr(exc))

    paid_sessions = [
        session for session in sessions if getattr(session, "payment_status", "") == "paid"
    ]
    unpaid_sessions = [
        session for session in sessions if getattr(session, "payment_status", "") != "paid"
    ]
    expired_sessions = [
        session for session in sessions if getattr(session, "status", "") == "expired"
    ]
    succeeded_payment_intents = [
        intent for intent in payment_intents if getattr(intent, "status", "") == "succeeded"
    ]
    gross_paid_cents = sum(int(getattr(session, "amount_total", 0) or 0) for session in paid_sessions)

    return StripeSummary(
        available=True,
        checkout_sessions=len(sessions),
        paid_sessions=len(paid_sessions),
        unpaid_sessions=len(unpaid_sessions),
        expired_sessions=len(expired_sessions),
        succeeded_payment_intents=len(succeeded_payment_intents),
        gross_paid_cents=gross_paid_cents,
    )


def format_money(cents: int) -> str:
    return f"${cents / 100:.2f}"


def build_report_payload(
    *,
    args: argparse.Namespace,
    window: Window,
    log_summary: dict[str, Any],
    stripe_summary: StripeSummary,
) -> dict[str, Any]:
    return {
        "window": {
            "start_local": window.start_local.isoformat(),
            "end_local": window.end_local.isoformat(),
            "start_utc": window.start_utc.isoformat(),
            "end_utc": window.end_utc.isoformat(),
            "timezone": args.timezone,
        },
        "sources": {
            "cloud_run_project": args.project,
            "cloud_run_region": args.region,
            "cloud_run_service": args.service,
            "ga4_measurement_id": GA4_MEASUREMENT_ID,
            "stripe": stripe_summary.available,
        },
        "logs": log_summary,
        "stripe": stripe_summary.__dict__,
    }


def print_text_report(payload: dict[str, Any]) -> None:
    window = payload["window"]
    logs = payload["logs"]
    stripe_data = payload["stripe"]

    print("Traditional Astrology Daily Funnel Report")
    print("=" * 43)
    print(f"Window: {window['start_local']} -> {window['end_local']} ({window['timezone']})")
    print(f"Source: Cloud Run request logs + Stripe live API")
    print(f"GA4 stream kept in code: {payload['sources']['ga4_measurement_id']}")
    print()

    print("Traffic")
    print(f"- Browser-like page views: {logs['browser_like_page_views']}")
    print(f"- Unique browser-like IPs: {logs['unique_browser_like_ips']}")
    print(f"- Browser-like requests: {logs['browser_like_requests']}")
    print(f"- Bot/test requests: {logs['bot_or_test_requests']}")
    if logs["bot_or_test_breakdown"]:
        print("- Bot/test breakdown:")
        for label, count in logs["bot_or_test_breakdown"]:
            print(f"  - {label}: {count}")
    print()

    print("Top Public Pages")
    if logs["top_public_pages"]:
        for path, count in logs["top_public_pages"]:
            print(f"- {path}: {count}")
    else:
        print("- None")
    print()

    print("Server Funnel")
    print(f"- Free chart successes: {logs['free_chart_successes']}")
    print(f"- Free chart failures: {logs['free_chart_failures']}")
    print(f"- Checkout sessions created by API: {logs['checkout_sessions_created']}")
    print(f"- Checkout API failures: {logs['checkout_failures']}")
    print(f"- Paid generation started: {logs['paid_generation_started']}")
    print(f"- Paid generation failures: {logs['paid_generation_failures']}")
    print()

    print("Stripe")
    if stripe_data["available"]:
        print(f"- Checkout sessions: {stripe_data['checkout_sessions']}")
        print(f"- Paid sessions: {stripe_data['paid_sessions']}")
        print(f"- Unpaid/open sessions: {stripe_data['unpaid_sessions']}")
        print(f"- Expired sessions: {stripe_data['expired_sessions']}")
        print(f"- Succeeded PaymentIntents: {stripe_data['succeeded_payment_intents']}")
        print(f"- Gross paid: {format_money(stripe_data['gross_paid_cents'])}")
    else:
        print(f"- Unavailable: {stripe_data['error']}")
    print()

    print("Read")
    if logs["free_chart_successes"] == 0:
        print("- No free-chart demand reached the backend in this window.")
    elif logs["checkout_sessions_created"] == 0:
        print("- Free charts happened, but no one clicked through to checkout.")
    elif stripe_data["available"] and stripe_data["paid_sessions"] == 0:
        print("- Checkout sessions were created, but no payment completed.")
    else:
        print("- Paid funnel activity exists; inspect fulfillment and delivery.")


def main() -> int:
    args = parse_args()
    load_project_env()

    try:
        window = build_window(args.date, args.days, args.timezone)
        received = parse_log_entries(
            run_gcloud_logging_read(
                project=args.project,
                region=args.region,
                service=args.service,
                window=window,
                action="request_received",
                limit=args.limit,
            )
        )
        completed = parse_log_entries(
            run_gcloud_logging_read(
                project=args.project,
                region=args.region,
                service=args.service,
                window=window,
                action="request_completed",
                limit=args.limit,
            )
        )
        log_summary = summarize_logs(received, completed)
        stripe_summary = (
            StripeSummary(available=False, error="Skipped by --skip-stripe")
            if args.skip_stripe
            else fetch_stripe_summary(window)
        )
        payload = build_report_payload(
            args=args,
            window=window,
            log_summary=log_summary,
            stripe_summary=stripe_summary,
        )
    except Exception as exc:
        print(f"daily_funnel_report failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_text_report(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
