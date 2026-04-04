import os
import json
import logging
import urllib.request
import urllib.error
from datetime import datetime, timezone
import hashlib

logger = logging.getLogger(__name__)

# User can supply this via environment variable or overwrite this string directly.
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "REPLACE_WITH_YOUR_WEBHOOK_URL")

def archive_chart_output(chart_request_dump: dict, result: dict):
    """
    Saves the full chart calculate output to local disk for record keeping
    so that no chart outputs are ever lost, even for free guests.
    """
    try:
        now = datetime.now(timezone.utc)
        folder_path = os.path.join(
            "data", "archives", "charts", 
            str(now.year), 
            f"{now.month:02d}", 
            f"{now.day:02d}"
        )
        os.makedirs(folder_path, exist_ok=True)
        
        # generate a unique filename
        name = chart_request_dump.get("name", "Guest")
        req_date = chart_request_dump.get("date", "0000-00-00")
        hash_str = hashlib.md5(f"{name}{req_date}{now.timestamp()}".encode()).hexdigest()[:8]
        
        filename = f"{now.strftime('%H%M%S')}_{name.replace(' ', '_')}_{hash_str}.json"
        file_path = os.path.join(folder_path, filename)
        
        payload = {
            "timestamp": now.isoformat(),
            "request": chart_request_dump,
            "result": result
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Chart archived successfully to {file_path}")
    except Exception as e:
        logger.error(f"Failed to archive chart output: {e}", exc_info=True)


def notify_chart_created(chart_request_dump: dict, tier: str = "unknown"):
    """
    Sends a Discord webhook notification indicating a chart was generated.
    """
    if "REPLACE_WITH_YOUR_WEBHOOK_URL" in DISCORD_WEBHOOK_URL or not DISCORD_WEBHOOK_URL:
        # Silently skip if no webhook is configured, logging a single warning so it's not spammy.
        logger.info("Discord webhook URL not configured. Skipping Discord notification.")
        return
        
    try:
        name = chart_request_dump.get("name", "Guest")
        city = chart_request_dump.get("city", "Unknown City")
        house_system = chart_request_dump.get("house_system", "W")
        
        content = (
            f"**🔮 New Chart Generated!**\n"
            f"> **Name:** {name}\n"
            f"> **Location:** {city}\n"
            f"> **House System:** {house_system}\n"
            f"> **Tier:** {tier}"
        )
        
        payload = {"content": content}
        req = urllib.request.Request(
            DISCORD_WEBHOOK_URL, 
            data=json.dumps(payload).encode('utf-8'),
            headers={'User-Agent': 'AstrologyApp', 'Content-Type': 'application/json'}
        )
        
        urllib.request.urlopen(req, timeout=5.0)
    except urllib.error.URLError as e:
        logger.error(f"Failed to send discord notification: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in discord notification: {e}")
