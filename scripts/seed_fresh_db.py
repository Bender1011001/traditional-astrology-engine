"""
AstroForge — Fresh DB Seed
===========================
Drops all tables and re-creates them from scratch, then seeds the
subscription_plans table with the correct AstroForge tiers.

Run this ONLY on a fresh install or when you explicitly want to wipe everything:
    python scripts/seed_fresh_db.py

For an existing database (e.g. production with real users), use the
non-destructive migration instead:
    python scripts/migrate_plans_to_astroforge.py

After seeding, run setup_stripe_products.py to populate real Stripe price IDs.
Trials work immediately after seeding. Paid checkout requires Stripe setup.
"""

import sys
import os
import uuid

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.database.core import engine, Base, SessionLocal
from src.database.models import SubscriptionPlan, User, UserSubscription


def seed_plans():
    db = SessionLocal()
    try:
        existing = db.query(SubscriptionPlan).count()
        if existing > 0:
            print("Plans already exist. Skipping seed.")
            print("To force re-seed, wipe the DB first (this script prompts for that).")
            return

        print("Seeding AstroForge subscription plans...")

        plans = [
            # ----------------------------------------------------------------
            # Free tier — 10 readings, no PDF export
            # ----------------------------------------------------------------
            SubscriptionPlan(
                tier="free",
                chart_quota=10,
                api_quota=0,
                price_monthly=0.00,
                price_annual=0.00,
                stripe_price_id_monthly=None,
                stripe_price_id_annual=None,
                features={
                    "pdf_export": False,
                    "bulk_upload": False,
                    "api_access": False,
                    "saved_charts": True,
                    "readings": True,
                },
            ),
            # ----------------------------------------------------------------
            # Scholar — $9.99/mo | Unlimited readings, PDF export, saved charts
            # ----------------------------------------------------------------
            SubscriptionPlan(
                tier="scholar",
                chart_quota=None,   # unlimited
                api_quota=0,
                price_monthly=9.99,
                price_annual=99.00,
                stripe_price_id_monthly=None,   # → run setup_stripe_products.py
                stripe_price_id_annual=None,
                features={
                    "pdf_export": True,
                    "bulk_upload": False,
                    "api_access": False,
                    "saved_charts": True,
                    "readings": True,
                },
            ),
            # ----------------------------------------------------------------
            # Practitioner — $29/mo | Bulk CSV→ZIP, API, white-label
            # ----------------------------------------------------------------
            SubscriptionPlan(
                tier="practitioner",
                chart_quota=None,   # unlimited
                api_quota=3000,     # ~100 API calls/day
                price_monthly=29.00,
                price_annual=290.00,
                stripe_price_id_monthly=None,   # → run setup_stripe_products.py
                stripe_price_id_annual=None,
                features={
                    "pdf_export": True,
                    "bulk_upload": True,
                    "api_access": True,
                    "white_label": True,
                    "saved_charts": True,
                    "readings": True,
                },
            ),
            # ----------------------------------------------------------------
            # Studio — $97/mo | High-volume API, SLA, dedicated support
            # ----------------------------------------------------------------
            SubscriptionPlan(
                tier="studio",
                chart_quota=None,
                api_quota=30000,    # ~1000 API calls/day
                price_monthly=97.00,
                price_annual=970.00,
                stripe_price_id_monthly=None,   # → run setup_stripe_products.py
                stripe_price_id_annual=None,
                features={
                    "pdf_export": True,
                    "bulk_upload": True,
                    "api_access": True,
                    "white_label": True,
                    "sla": True,
                    "saved_charts": True,
                    "readings": True,
                },
            ),
        ]

        db.add_all(plans)
        db.commit()
        print(f"✅ Seeded {len(plans)} plans: {', '.join(p.tier for p in plans)}")
        print("ℹ️  Run setup_stripe_products.py to activate paid checkout.")

    except Exception as e:
        print(f"❌ Error seeding plans: {e}")
        db.rollback()
    finally:
        db.close()


def reset_db():
    print("Resetting database (drop all → recreate)...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Tables recreated.")


if __name__ == "__main__":
    confirm = input(
        "This will WIPE users.db and re-seed from scratch.\n"
        "For existing databases, use migrate_plans_to_astroforge.py instead.\n"
        "Type 'yes' to wipe and reseed: "
    )
    if confirm.strip().lower() == "yes":
        reset_db()
        seed_plans()
    else:
        print("Cancelled.")
