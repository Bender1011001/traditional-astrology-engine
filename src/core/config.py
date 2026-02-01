from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    JWT_SECRET: str
    DATABASE_URL: str = "sqlite:///./users.db"
    REDIS_URL: str = "redis://localhost:6379"
    SENDER_EMAIL: str
    SENDGRID_API_KEY: Optional[str] = None
    SITE_BASE_URL: str = "https://traditional-astrology.com"
    CORS_ORIGINS: str = "http://localhost:3000,https://traditional-astrology.com"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
