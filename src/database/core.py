import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

# Priority: DATABASE_URL env var (Production), else local SQLite
DATABASE_URL = settings.DATABASE_URL or "sqlite:///./users.db"

# Fix for Render/Heroku 'postgres://' vs 'postgresql://' schema
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Add sslmode=require if it's a remote postgres DB and not already specified
if "postgres" in DATABASE_URL and "localhost" not in DATABASE_URL and "127.0.0.1" not in DATABASE_URL:
    if "sslmode=" not in DATABASE_URL:
        # Use ? or & depending on if there are already params
        separator = "&" if "?" in DATABASE_URL else "?"
        DATABASE_URL += f"{separator}sslmode=require"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {
        "sslmode": "require",  # Redundant but safe for some drivers
        "connect_timeout": 10   # Don't hang forever
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
