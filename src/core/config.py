from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    JWT_SECRET: str
    ADMIN_SECRET_KEY: str = ""  # Admin endpoint authentication
    DATABASE_URL: str = "sqlite:///./users.db"
    REDIS_URL: Optional[str] = None
    SENDER_EMAIL: str
    SENDGRID_API_KEY: Optional[str] = None
    SITE_BASE_URL: str = "https://traditional-astrology.com"
    CORS_ORIGINS: str = (
        "http://localhost:3000,"
        "https://traditional-astrology.com,"
        "https://www.traditional-astrology.com,"
        "https://astrology-engine-central-7387.azurewebsites.net"
    )
    OWNER_EMAILS: str = ""
    OWNER_BOOTSTRAP_KEY: str = ""

    # Pricing (B2B SaaS). Leave blank to disable checkout for that tier until configured.
    STRIPE_PRICE_PRACTITIONER_MONTHLY: str = ""
    STRIPE_PRICE_PRACTITIONER_ANNUAL: str = ""
    STRIPE_PRICE_STUDIO_MONTHLY: str = ""
    STRIPE_PRICE_STUDIO_ANNUAL: str = ""

    # Legacy Stripe env var names (single-tier pricing). Used as fallback for Practitioner seeding.
    STRIPE_SUBSCRIPTION_PRICE_ID: str = ""
    STRIPE_ANNUAL_PRICE_ID: str = ""

    TRIAL_DAYS_DEFAULT: int = 14
    # Revenue control:
    # - "pilot": disable paid checkout globally while building product fit.
    # - "live": enable paid checkout.
    SALES_MODE: str = "pilot"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
