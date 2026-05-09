import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

from src.core.config import settings

DEFAULT_DATABASE_URL = "sqlite:///./users.db"


def _resolve_database_url(configured_url: str, is_cloud_run: bool) -> str:
    if configured_url and configured_url != DEFAULT_DATABASE_URL:
        return configured_url
    if is_cloud_run:
        raise RuntimeError(
            "DATABASE_URL must be set for Cloud Run. Refusing to fall back to SQLite."
        )
    return DEFAULT_DATABASE_URL


# Priority: DATABASE_URL env var (Production), else local SQLite only outside Cloud Run.
DATABASE_URL = _resolve_database_url(
    settings.DATABASE_URL,
    bool(os.getenv("K_SERVICE")),
)

# Normalize legacy 'postgres://' URLs to SQLAlchemy-compatible 'postgresql://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Detect Cloud Run Cloud SQL Auth Proxy (uses Unix sockets at /cloudsql/...)
_is_cloudsql_proxy = "/cloudsql/" in DATABASE_URL

# Add sslmode=require if it's a remote postgres DB connecting directly (not via proxy)
if (
    "postgres" in DATABASE_URL
    and "localhost" not in DATABASE_URL
    and "127.0.0.1" not in DATABASE_URL
    and not _is_cloudsql_proxy
):
    if "sslmode=" not in DATABASE_URL:
        # Use ? or & depending on if there are already params
        separator = "&" if "?" in DATABASE_URL else "?"
        DATABASE_URL += f"{separator}sslmode=require"

# Log connection attempt (masked)
safe_url = DATABASE_URL
if "@" in safe_url:
    part1 = safe_url.split("@")[1]
    logger.info(
        "Connecting to DB at %s via %s",
        part1.split("?")[0],
        "CloudSQL Proxy" if _is_cloudsql_proxy else f"SSL={('sslmode' in safe_url)}",
    )
else:
    logger.info("Connecting to Local/Sqlite DB")

# Engine configuration optimized for Serverless/Cloud Run dynamic scaling
# Hardcapping connection footprints so horizontal container scaling doesn't exhaust DB slots.
engine_kwargs = {
    "pool_size": 2,
    "max_overflow": 4,
    "pool_timeout": 30,
    "pool_recycle": 1800,
}

if "sqlite" in DATABASE_URL:
    engine_kwargs = {"connect_args": {"check_same_thread": False}}  # type: ignore
elif _is_cloudsql_proxy:
    # Cloud SQL Auth Proxy handles encryption — no SSL flags needed on the connection.
    engine_kwargs["connect_args"] = {  # type: ignore
        "connect_timeout": 5,
    }
else:
    # Direct remote Postgres — require SSL at the driver level.
    engine_kwargs["connect_args"] = {  # type: ignore
        "sslmode": "require",
        "connect_timeout": 5,
    }

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
