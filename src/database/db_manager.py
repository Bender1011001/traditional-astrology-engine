import json
import os
from typing import Dict, Any
import shutil
import subprocess
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from src.database.core import SessionLocal
from src.database.models import AstrologicalDelineation
from functools import lru_cache

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def load_json_data(filename: str) -> Dict[str, Any]:
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

class DelineationLibrary:
    """
    Primary lookup goes to DB.  When nothing is found the library falls back to
    the legacy JSON files in data/legacy/ so that delineation text is always
    available — even before the DB has been seeded.
    """

    # Map DB category names → legacy JSON filenames
    _LEGACY_FILES = {
        "planets_in_signs":          "planets_in_signs.json",
        "planets_in_signs_ingested": "planets_in_signs_ingested.json",
        "planets_in_houses":         "planets_in_houses.json",
        "house_topoi":               "house_topoi.json",
        "detailed_delineations":     "detailed_delineations.json",
        "aspect_delineations":       "aspect_delineations.json",
        "profections":               "profections.json",
        "lots_arabic_parts":         "lots_arabic_parts.json",
        "lunar_mansions":            "lunar_mansions.json",
        "fixed_stars":               "fixed_stars.json",
    }

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._json_cache: Dict[str, Dict] = {}   # category → loaded json dict

    def _load_legacy(self, category: str) -> Dict:
        """Lazy-load a legacy JSON file and cache it."""
        if category in self._json_cache:
            return self._json_cache[category]
        filename = self._LEGACY_FILES.get(category)
        if not filename:
            self._json_cache[category] = {}
            return {}
        legacy_dir = os.path.join(DATA_DIR, 'legacy')
        path = os.path.join(legacy_dir, filename)
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._json_cache[category] = data
                return data
            except Exception as e:
                logger.debug("Legacy JSON load failed for %s: %s", category, repr(e), exc_info=True)
                self._json_cache[category] = {}
                return {}
        self._json_cache[category] = {}
        return {}

    def _query_db(self, category: str, key: str) -> Any:
        cache_key = f"{category}:{key}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        db = SessionLocal()
        try:
            res = db.query(AstrologicalDelineation).filter(
                AstrologicalDelineation.category == category,
                AstrologicalDelineation.key == key
            ).first()
            if res:
                self._cache[cache_key] = res.content
                return res.content
        except Exception as e:
            logger.debug("DB query failed for %s:%s: %s", category, key, repr(e), exc_info=True)
        finally:
            db.close()

        # Fallback: legacy JSON
        legacy = self._load_legacy(category)
        val = legacy.get(key)
        if val is not None:
            self._cache[cache_key] = val
            return val
        return None
        
    def get_planet_delineation(self, key: str) -> str:
        res = self._query_db('planets_in_signs', key)
        if not res:
            # Try ingested fallback
            res = self._query_db('planets_in_signs_ingested', key)
        return res if res else "Delineation not found in Codex."

    def get_detailed_profile(self, planet: str) -> Dict:
        res = self._query_db('detailed_delineations', planet.upper())
        return res if res else {}

    def get_house_planet_delineation(self, key: str) -> str:
        res = self._query_db('planets_in_houses', key)
        return res if res else "Delineation not found for House placement."

    def get_house_definition(self, house_num: int) -> str:
        key = f"HOUSE_{house_num}"
        res = self._query_db('house_topoi', key)
        return res if res else "Unknown House"

    def get_arbitrary_delineation(self, category: str, key: str) -> Any:
        """Generic lookup for any category."""
        return self._query_db(category, key)

class DatabaseBackupManager:
    @staticmethod
    def run_backup(target_dir: str = "backups") -> str:
        """
        Creates a backup of the current database.
        Supports SQLite (file copy) and Postgres (pg_dump).
        """
        try:
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            db_url = os.getenv("DATABASE_URL", "sqlite:///./users.db")
            
            # Handle SQLite
            if "sqlite" in db_url:
                # remove prefix logic
                if db_url.startswith("sqlite:///"):
                    db_path = db_url.replace("sqlite:///", "")
                elif db_url.startswith("sqlite://"):
                     db_path = db_url.replace("sqlite://", "")
                else:
                     db_path = "users.db" # Default
                
                # If relative path, assume relative to cwd (root)
                if not os.path.isabs(db_path):
                     db_path = os.path.join(os.getcwd(), db_path)

                if os.path.exists(db_path):
                    backup_name = f"users_backup_{timestamp}.db"
                    dest_path = os.path.join(target_dir, backup_name)
                    shutil.copy2(db_path, dest_path)
                    return f"SQLite Backup successful: {dest_path}"
                else:
                    return f"SQLite DB file not found at {db_path}"

            # Handle Postgres
            elif "postgres" in db_url:
                # pg_dump must be in PATH
                backup_name = f"pg_backup_{timestamp}.sql"
                dest_path = os.path.join(target_dir, backup_name)
                
                # Mask password in log but use it for command
                # Ideally use PGPASSFILE or env vars.
                # Here we assume pg_dump can use the URL directly
                cmd = ["pg_dump", db_url, "-f", dest_path]
                
                subprocess.run(cmd, check=True, capture_output=True)
                return f"Postgres Backup successful: {dest_path}"
            
            return "Unknown database type."
            
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode() if e.stderr else str(e)
            logging.error("Backup failed: %s", err)
            return f"Backup failed: {err}"
        except Exception as e:
            logging.error("Backup failed: %s", repr(e), exc_info=True)
            return f"Backup failed: {e}"

def init_db():
    from src.database.core import engine, Base
    # Ensure models are imported so they are registered with Base
    import src.database.models
    Base.metadata.create_all(bind=engine)
