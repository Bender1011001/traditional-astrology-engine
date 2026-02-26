"""
AstroForge Plan Migration
=========================
Safe, non-destructive migration that brings the subscription_plans table in line
with what the billing/subscription code actually expects.

Run this ONCE against any existing database (dev or prod):
    python scripts/migrate_plans_to_astroforge.py

What it does:
  - Adds "scholar" plan    ($9.99/mo) — was missing, caused trial failures
  - Adds "studio" plan     ($97/mo)   — was missing
  - Updates "practitioner" to $29/mo  — was $149 (old pricing)
  - Leaves all existing users and subscriptions untouched
  - Does NOT drop any tables or wipe data

After running this, trials work immediately.
For paid checkout to work you still need real Stripe price IDs —
run setup_stripe_products.py to create them, then come back and
update the price IDs below (or re-run setup_stripe_products.py
which will update the DB directly).
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.database.core import engine, Base, SessionLocal
from src.database.models import SubscriptionPlan


# ---------------------------------------------------------------------------
# Target plan definitions.  Stripe price IDs marked "NEEDS_SETUP" will allow
# trials to work but will raise a clear error if someone attempts paid checkout.
# Run setup_stripe_products.py to populate real IDs.
# ---------------------------------------------------------------------------
PLAN_TARGETS = [
    {
        "tier": "free",
        "chart_quota": 10,
        "api_quota": 0,
        "price_monthly": 0.00,
        "price_annual": 0.00,
        "stripe_price_id_monthly": None,
        "stripe_price_id_annual": None,
        "features": {
            "pdf_export": False,
            "bulk_upload": False,
            "api_access": False,
            "saved_charts": True,
            "readings": True,
        },
    },
    {
        "tier": "scholar",
        "chart_quota": None,       # unlimited
        "api_quota": 0,
        "price_monthly": 9.99,
        "price_annual": 99.00,
        "stripe_price_id_monthly": None,   # → run setup_stripe_products.py
        "stripe_price_id_annual": None,
        "features": {
            "pdf_export": True,
            "bulk_upload": False,
            "api_access": False,
            "saved_charts": True,
            "readings": True,
        },
    },
    {
        "tier": "practitioner",
        "chart_quota": None,       # unlimited
        "api_quota": 3000,         # 100/day
        "price_monthly": 29.00,    # updated from old $149
        "price_annual": 290.00,
        "stripe_price_id_monthly": None,   # → run setup_stripe_products.py
        "stripe_price_id_annual": None,
        "features": {
            "pdf_export": True,
            "bulk_upload": True,
            "api_access": True,
            "white_label": True,
            "saved_charts": True,
            "readings": True,
        },
    },
    {
        "tier": "studio",
        "chart_quota": None,
        "api_quota": 30000,        # 1000/day
        "price_monthly": 97.00,
        "price_annual": 970.00,
        "stripe_price_id_monthly": None,
        "stripe_price_id_annual": None,
        "features": {
            "pdf_export": True,
            "bulk_upload": True,
            "api_access": True,
            "white_label": True,
            "sla": True,
            "saved_charts": True,
            "readings": True,
        },
    },
]


def migrate():
    Base.metadata.create_all(bind=engine)   # no-op if tables exist
    db = SessionLocal()
    added = []
    updated = []

    try:
        for plan_def in PLAN_TARGETS:
            tier = plan_def["tier"]
            existing = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == tier).first()

            if not existing:
                # Create new plan
                plan = SubscriptionPlan(
                    tier=tier,
                    chart_quota=plan_def["chart_quota"],
                    api_quota=plan_def["api_quota"],
                    price_monthly=plan_def["price_monthly"],
                    price_annual=plan_def["price_annual"],
                    stripe_price_id_monthly=plan_def["stripe_price_id_monthly"],
                    stripe_price_id_annual=plan_def["stripe_price_id_annual"],
                    features=plan_def["features"],
                )
                db.add(plan)
                added.append(tier)
            else:
                # Update prices and features; preserve Stripe IDs if already set
                existing.chart_quota = plan_def["chart_quota"]
                existing.api_quota = plan_def["api_quota"]
                existing.price_monthly = plan_def["price_monthly"]
                existing.price_annual = plan_def["price_annual"]
                existing.features = plan_def["features"]
                # Only overwrite Stripe IDs if the target has a real value
                if plan_def["stripe_price_id_monthly"]:
                    existing.stripe_price_id_monthly = plan_def["stripe_price_id_monthly"]
                if plan_def["stripe_price_id_annual"]:
                    existing.stripe_price_id_annual = plan_def["stripe_price_id_annual"]
                updated.append(tier)

        db.commit()

        print("\n[OK] Migration complete.")
        if added:
            print(f"   Added plans:   {', '.join(added)}")
        if updated:
            print(f"   Updated plans: {', '.join(updated)}")

        # Summary of Stripe readiness
        print("\n[INFO] Plan status after migration:")
        all_plans = db.query(SubscriptionPlan).all()
        for p in sorted(all_plans, key=lambda x: x.price_monthly or 0):
            mo_id = p.stripe_price_id_monthly or "NEEDS_SETUP"
            print(f"   {p.tier:<16} ${p.price_monthly or 0:<8.2f}/mo   stripe_mo={mo_id[:40]}")

        needs_setup = [
            p.tier for p in all_plans
            if p.tier not in ("free",) and not p.stripe_price_id_monthly
        ]
        if needs_setup:
            print(f"\n[WARN] Run setup_stripe_products.py to create Stripe prices for: {', '.join(needs_setup)}")
            print("   Trials work now. Paid checkout will work after Stripe setup.")
        else:
            print("\n[OK] All plans have Stripe price IDs. Checkout is ready.")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Migration failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
