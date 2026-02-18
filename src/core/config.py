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
    STRIPE_PRICE_SCHOLAR_MONTHLY: str = ""
    STRIPE_PRICE_SCHOLAR_ANNUAL: str = ""
    STRIPE_PRICE_PRACTITIONER_MONTHLY: str = ""
    STRIPE_PRICE_PRACTITIONER_ANNUAL: str = ""
    STRIPE_PRICE_STUDIO_MONTHLY: str = ""
    STRIPE_PRICE_STUDIO_ANNUAL: str = ""

    # Legacy Stripe env var names (single-tier pricing). Used as fallback for Practitioner seeding.
    STRIPE_SUBSCRIPTION_PRICE_ID: str = ""
    STRIPE_ANNUAL_PRICE_ID: str = ""

    # One-time report pricing (B2C / audit purchase).
    # If unset, the API may attempt a best-effort lookup by Product name in Stripe.
    STRIPE_PRICE_CALIBRATION_ONETIME: str = ""
    STRIPE_PRICE_FULL_ONETIME: str = ""
    STRIPE_PRICE_SINGLE_READING_ONETIME: str = ""

    # Public reading monetization:
    # - First N free readings per IP per rolling window.
    # - Additional readings require one-time purchase.
    FREE_SINGLE_READINGS_PER_IP: int = 3
    FREE_SINGLE_READINGS_WINDOW_SECONDS: int = 86400
    SINGLE_READING_PRICE_USD: int = 20

    TRIAL_DAYS_DEFAULT: int = 14
    # Revenue control:
    # - "pilot": disable paid checkout globally while building product fit.
    # - "live": enable paid checkout.
    SALES_MODE: str = "live"

    # Promo control: temporarily unlock "individual" (non-premium) readings for free-tier users.
    # - If enabled, the backend marks responses with meta.promo_unlocked=true.
    # - Frontend can use this to disable paywall UI while keeping free-tier rate limits.
    PROMO_FREE_INDIVIDUAL_READINGS: bool = False
    # UTC date in YYYY-MM-DD. If set, promo is active only until end-of-day UTC on this date.
    PROMO_FREE_INDIVIDUAL_READINGS_UNTIL: str = ""

    # RapidAPI marketplace integration.
    # - RAPIDAPI_PROXY_SECRET: The secret RapidAPI sends in X-RapidAPI-Proxy-Secret on every
    #   proxied request. Set this in the RapidAPI Provider Dashboard > Security.
    # - RAPIDAPI_MASTER_KEY: A single sk_live_* API key created in your dashboard specifically
    #   for RapidAPI traffic. All RapidAPI subscribers are billed via RapidAPI; this key is
    #   used server-side only to authenticate the forwarded request.
    # Leave both blank until the RapidAPI listing is active.
    RAPIDAPI_PROXY_SECRET: str = ""
    RAPIDAPI_MASTER_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
