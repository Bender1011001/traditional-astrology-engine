
import logging
import sys
import json
import os
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

# Ensure log directory exists
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

class JSONFormatter(logging.Formatter):
    """
    Format logs as JSON for easy parsing.
    """
    def format(self, record):
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # Add extra fields if available
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_obj.update(record.extra_data)
            
        return json.dumps(log_obj, default=str)

def configure_logging(app_name="astrology_engine"):
    """
    Configure logging to both stdout and a rotating file.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Clear and close existing handlers
    for handler in logger.handlers:
        handler.close()
    logger.handlers = []
    
    # 1. Console Handler (Standard Text)
    # Ensure Windows console doesn't choke on emojis
    if sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except AttributeError:
            pass
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Check if running in Google Cloud Run
    if os.environ.get("K_SERVICE"):
        # Use structured JSON logging for Cloud Logging ingestion
        console_handler.setFormatter(JSONFormatter())
    else:
        # User readable text for local development
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(module)s] - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 2. File Handler (JSON Lines)
    file_path = os.path.join(LOG_DIR, f"{app_name}.jsonl")
    file_handler = RotatingFileHandler(
        file_path, 
        maxBytes=10*1024*1024, # 10 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    logging.info("Logging initialized. Logs writing to %s", file_path)

# Activity Logger for User Actions
class ActivityLogger:
    @staticmethod
    def log_activity(action: str, user_id: str = "guest", ip: str = "unknown", details: dict = None):
        """
        Log high-level user activity (e.g., "generated_chart", "clicked_buy").
        """
        extra = {
            "action": action,
            "user_id": user_id,
            "ip": ip,
            "details": details or {}
        }
        logging.info("ACTIVITY: %s by %s", action, user_id, extra={"extra_data": extra})

