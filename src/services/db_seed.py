"""
Database seeding helpers.

These used to live in `src/scripts/seed_db.py`. We keep them in a service module so
the runtime app can import seeding without relying on a "scripts" folder.
"""

from __future__ import annotations

from src.database.core import engine, Base, SessionLocal
from src.database.models import SubscriptionPlan
from src.core.config import settings


def seed_plans() -> None:
    db = SessionLocal()
    try:
        print("Ensuring Subscription Plans exist (upsert)...")

        # Legacy env var fallback (older single-tier config).
        legacy_pract_monthly = (getattr(settings, "STRIPE_SUBSCRIPTION_PRICE_ID", "") or "").strip() or None
        legacy_pract_annual = (getattr(settings, "STRIPE_ANNUAL_PRICE_ID", "") or "").strip() or None

        desired = [
            {
                "tier": "free",
                "chart_quota": None,
                "api_quota": 0,
                "price_monthly": 0.00,
                "price_annual": 0.00,
                "stripe_price_id_monthly": None,
                "stripe_price_id_annual": None,
                "features": {"api_access": False},
            },
            {
                "tier": "scholar",
                "chart_quota": None,
                "api_quota": 0,
                "price_monthly": 14.00,
                "price_annual": 140.00,
                "stripe_price_id_monthly": (getattr(settings, "STRIPE_PRICE_SCHOLAR_MONTHLY", "") or "").strip() or None,
                "stripe_price_id_annual": (getattr(settings, "STRIPE_PRICE_SCHOLAR_ANNUAL", "") or "").strip() or None,
                "features": {"api_access": False, "pdf_export": True, "saved_charts": True},
            },
            {
                "tier": "practitioner",
                "chart_quota": None,
                "api_quota": 500,
                "price_monthly": 79.00,
                "price_annual": 790.00,
                "stripe_price_id_monthly": settings.STRIPE_PRICE_PRACTITIONER_MONTHLY or legacy_pract_monthly,
                "stripe_price_id_annual": settings.STRIPE_PRICE_PRACTITIONER_ANNUAL or legacy_pract_annual,
                "features": {"api_access": True, "pdf_export": True, "saved_charts": True, "white_label_pdf": True, "bulk_csv_pdf": True},
            },
            {
                "tier": "studio",
                "chart_quota": None,
                "api_quota": None,
                "price_monthly": 99.00,
                "price_annual": 990.00,
                "stripe_price_id_monthly": settings.STRIPE_PRICE_STUDIO_MONTHLY or None,
                "stripe_price_id_annual": settings.STRIPE_PRICE_STUDIO_ANNUAL or None,
                "features": {"api_access": True, "pdf_export": True, "saved_charts": True, "white_label_pdf": True, "seats": 5},
            },
        ]

        for d in desired:
            plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == d["tier"]).first()
            if not plan:
                plan = SubscriptionPlan(tier=d["tier"])
                db.add(plan)

            plan.chart_quota = d["chart_quota"]
            plan.api_quota = d["api_quota"]
            plan.price_monthly = d["price_monthly"]
            plan.price_annual = d["price_annual"]
            plan.stripe_price_id_monthly = d["stripe_price_id_monthly"]
            plan.stripe_price_id_annual = d["stripe_price_id_annual"]
            plan.features = d["features"]

        db.commit()
        print("Plans ensured successfully.")
    except Exception as e:
        print(f"Error seeding plans: {e}")
        db.rollback()
    finally:
        db.close()


def reset_db() -> None:
    print("Resetting Database (Clean Break)...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database tables recreated.")

