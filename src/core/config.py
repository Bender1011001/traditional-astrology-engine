from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    JWT_SECRET: str
    ADMIN_SECRET_KEY: str = ""  # Admin endpoint authentication
    DATABASE_URL: str = "sqlite:///./users.db"
    REDIS_URL: str = "redis://localhost:6379"
    SENDER_EMAIL: str
    SENDGRID_API_KEY: Optional[str] = None
    SITE_BASE_URL: str = "https://traditional-astrology.com"
    CORS_ORIGINS: str = "http://localhost:3000,https://traditional-astrology.com"
    OWNER_EMAILS: str = ""
    OWNER_BOOTSTRAP_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
