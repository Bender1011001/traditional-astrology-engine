import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger(__name__)

from src.core.config import settings

# Priority: DATABASE_URL env var (Production), else local SQLite
DATABASE_URL = settings.DATABASE_URL or "sqlite:///./users.db"

# Normalize legacy 'postgres://' URLs to SQLAlchemy-compatible 'postgresql://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Add sslmode=require if it's a remote postgres DB and not already specified
if "postgres" in DATABASE_URL and "localhost" not in DATABASE_URL and "127.0.0.1" not in DATABASE_URL:
    if "sslmode=" not in DATABASE_URL:
        # Use ? or & depending on if there are already params
        separator = "&" if "?" in DATABASE_URL else "?"
        DATABASE_URL += f"{separator}sslmode=require"

# Log connection attempt (masked)
safe_url = DATABASE_URL
if "@" in safe_url:
    part1 = safe_url.split("@")[1]
    logger.info("Connecting to DB at %s with SSL=%s", part1.split('?')[0], 'sslmode' in safe_url)
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
    engine_kwargs = {"connect_args": {"check_same_thread": False}}
else:
    # Explicitly set SSL for Postgres
    engine_kwargs["connect_args"] = {
        "sslmode": "require",
        "connect_timeout": 5  # Reduced timeout for faster failure debugging
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
