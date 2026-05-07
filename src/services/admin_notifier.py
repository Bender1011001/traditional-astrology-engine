import hashlib
import json
import logging
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")


def _send_discord_embed(embed: dict) -> None:
    """
    Posts a single Discord embed object to the configured webhook.
    Silently skips if the webhook URL is not set.
    """
    if not DISCORD_WEBHOOK_URL or "REPLACE_WITH" in DISCORD_WEBHOOK_URL:
        logger.debug("Discord webhook not configured — skipping notification.")
        return

    payload = {"embeds": [embed]}
    try:
        req = urllib.request.Request(
            DISCORD_WEBHOOK_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "User-Agent": "TraditionalAstrology/1.0",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            if resp.status not in (200, 204):
                logger.warning(
                    "Discord webhook returned unexpected status: %s", resp.status
                )
    except urllib.error.HTTPError as e:
        logger.error("Discord webhook HTTP error %s: %s", e.code, e.reason)
    except urllib.error.URLError as e:
        logger.error("Discord webhook connection error: %s", e.reason)
    except Exception as e:
        logger.error("Unexpected error sending Discord notification: %s", repr(e))


# ---------------------------------------------------------------------------
# Public notification functions
# ---------------------------------------------------------------------------


def notify_chart_created(chart_request_dump: dict, tier: str = "unknown") -> None:
    """
    Sends a Discord notification when a new astrological chart is generated.
    Called as a FastAPI BackgroundTask — must never raise.
    """
    try:
        name = chart_request_dump.get("name") or "Guest"
        city = chart_request_dump.get("city") or "Unknown"
        state = chart_request_dump.get("state") or ""
        location = f"{city}, {state}" if state else city
        house_system = chart_request_dump.get("house_system") or "W"
        zodiac = chart_request_dump.get("zodiac_system") or "tropical"
        dob = chart_request_dump.get("date") or "N/A"
        tob = chart_request_dump.get("time") or "N/A"

        tier_colors = {
            "paid": 0x6B46C1,  # purple — paying customer
            "free": 0x4A5568,  # grey   — free tier
            "full_nativity": 0x2B6CB0,  # blue — B2B / full endpoint
        }
        color = tier_colors.get(tier, 0x718096)

        tier_labels = {
            "paid": "💜 Paid",
            "free": "🌑 Free",
            "full_nativity": "🔵 Full (B2B)",
        }
        tier_label = tier_labels.get(tier, f"❓ {tier}")

        embed = {
            "title": "🔮 New Chart Generated",
            "color": color,
            "fields": [
                {"name": "Name", "value": name, "inline": True},
                {"name": "Location", "value": location, "inline": True},
                {"name": "Tier", "value": tier_label, "inline": True},
                {"name": "DOB", "value": dob, "inline": True},
                {"name": "TOB", "value": tob, "inline": True},
                {"name": "House System", "value": house_system.upper(), "inline": True},
                {"name": "Zodiac", "value": zodiac.capitalize(), "inline": True},
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "footer": {"text": "Traditional Astrology Engine"},
        }

        _send_discord_embed(embed)

    except Exception as e:
        logger.error("notify_chart_created failed unexpectedly: %s", repr(e))


def notify_user_registered(email: str, name: str = "", plan_tier: str = "free") -> None:
    """
    Sends a Discord notification when a new user account is created.
    Called as a FastAPI BackgroundTask — must never raise.
    """
    try:
        display_name = name or "Anonymous"
        tier_label = plan_tier.capitalize() if plan_tier else "Free"

        embed = {
            "title": "👤 New Account Registered",
            "color": 0x38A169,  # green — growth event
            "fields": [
                {"name": "Email", "value": email, "inline": True},
                {"name": "Name", "value": display_name, "inline": True},
                {"name": "Initial Plan", "value": tier_label, "inline": True},
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "footer": {"text": "Traditional Astrology Engine"},
        }

        _send_discord_embed(embed)

    except Exception as e:
        logger.error("notify_user_registered failed unexpectedly: %s", repr(e))


def archive_chart_output(chart_request_dump: dict, result: dict) -> None:
    """
    Saves the full chart output to local disk for record keeping.
    No chart outputs are ever lost, even for free guests.
    Called as a FastAPI BackgroundTask — must never raise.
    """
    try:
        now = datetime.now(timezone.utc)
        folder_path = os.path.join(
            "data",
            "archives",
            "charts",
            str(now.year),
            f"{now.month:02d}",
            f"{now.day:02d}",
        )
        os.makedirs(folder_path, exist_ok=True)

        name = chart_request_dump.get("name") or "Guest"
        req_date = chart_request_dump.get("date") or "0000-00-00"
        hash_str = hashlib.md5(
            f"{name}{req_date}{now.timestamp()}".encode()
        ).hexdigest()[:8]

        filename = f"{now.strftime('%H%M%S')}_{name.replace(' ', '_')}_{hash_str}.json"
        file_path = os.path.join(folder_path, filename)

        payload = {
            "timestamp": now.isoformat(),
            "request": chart_request_dump,
            "result": result,
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        logger.info("Chart archived to %s", file_path)

    except Exception as e:
        logger.error("archive_chart_output failed: %s", repr(e), exc_info=True)
