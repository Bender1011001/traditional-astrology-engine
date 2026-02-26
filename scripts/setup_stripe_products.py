"""
AstroForge — Stripe Product Setup
==================================
Creates the Stripe Products and Prices for all AstroForge subscription tiers,
then writes the generated price IDs directly into the local database.

Run this ONCE when setting up a new environment, or after a pricing change:
    python scripts/setup_stripe_products.py

After it runs:
  - Stripe will have AstroForge-branded products at the correct price points
  - The local DB subscription_plans table will be updated with the new price IDs
  - Paid checkout is immediately live

Requirements:
  - STRIPE_SECRET_KEY must be set in .env
  - Run migrate_plans_to_astroforge.py first (to ensure the plans exist in the DB)

Note: Stripe Price objects are immutable (you cannot change the amount of an
existing price). Running this script again will create NEW prices and update
the DB to point to them. Old prices are left inactive in Stripe but do no harm.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(root_dir, ".env")
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

import stripe
from src.database.core import engine, Base, SessionLocal
from src.database.models import SubscriptionPlan

api_key = os.getenv("STRIPE_SECRET_KEY", "")


# ---------------------------------------------------------------------------
# Plan definitions: what we want to create in Stripe
# ---------------------------------------------------------------------------
PLANS = [
    {
        "tier": "scholar",
        "product_name": "AstroForge Scholar",
        "description": "Unlimited natal chart readings, PDF export, saved charts. Perfect for individual practitioners.",
        "monthly_cents": 999,       # $9.99
        "annual_cents": 9900,       # $99.00 (save ~17%)
    },
    {
        "tier": "practitioner",
        "product_name": "AstroForge Practitioner",
        "description": "Everything in Scholar plus: bulk CSV→ZIP PDF export, client labels, API access (100 calls/day), white-label PDFs.",
        "monthly_cents": 2900,      # $29.00
        "annual_cents": 29000,      # $290.00 (save ~17%)
    },
    {
        "tier": "studio",
        "product_name": "AstroForge Studio",
        "description": "High-volume plan: 1,000 API calls/day, SLA, dedicated support. For studios and high-volume Etsy sellers.",
        "monthly_cents": 9700,      # $97.00
        "annual_cents": 97000,      # $970.00 (save ~17%)
    },
]

ONE_TIME_PLANS = [
    {
        "env_key": "STRIPE_PRICE_SINGLE_READING_ONETIME",
        "product_name": "AstroForge Single Reading",
        "description": "One-time unlock for a single natal chart PDF reading.",
        "amount_cents": 2000,       # $20.00
    },
]


def setup_products():
    if not api_key:
        print("[ERROR] STRIPE_SECRET_KEY not found. Add it to .env and retry.")
        return

    if api_key.startswith("sk_test_"):
        print("[INFO]  Running in TEST mode (sk_test_ key detected).")
    elif api_key.startswith("sk_live_"):
        print("[WARN]  Running in LIVE mode (sk_live_ key detected). Real charges will be created.")
        confirm = input("Type 'live' to proceed: ")
        if confirm.strip().lower() != "live":
            print("Aborted.")
            return
    else:
        print(f"[ERROR] Unrecognized key prefix. Please check STRIPE_SECRET_KEY.")
        return

    stripe.api_key = api_key
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    results = {}

    try:
        # -------------------------------------------------------
        # Subscription plans
        # -------------------------------------------------------
        for plan_def in PLANS:
            tier = plan_def["tier"]
            print(f"\nCreating {plan_def['product_name']}...")

            product = stripe.Product.create(
                name=plan_def["product_name"],
                description=plan_def["description"],
            )

            price_mo = stripe.Price.create(
                unit_amount=plan_def["monthly_cents"],
                currency="usd",
                recurring={"interval": "month"},
                product=product.id,
            )
            price_yr = stripe.Price.create(
                unit_amount=plan_def["annual_cents"],
                currency="usd",
                recurring={"interval": "year"},
                product=product.id,
            )

            print(f"   [OK] Monthly: {price_mo.id}")
            print(f"   [OK] Annual:  {price_yr.id}")
            results[tier] = {"monthly": price_mo.id, "annual": price_yr.id}

            # Update DB
            db_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == tier).first()
            if db_plan:
                db_plan.stripe_price_id_monthly = price_mo.id
                db_plan.stripe_price_id_annual = price_yr.id
                print(f"   [OK] DB updated for tier '{tier}'")
            else:
                print(f"   [WARN]  No DB record for tier '{tier}' — run migrate_plans_to_astroforge.py first")

        # -------------------------------------------------------
        # One-time products
        # -------------------------------------------------------
        for ot in ONE_TIME_PLANS:
            print(f"\nCreating one-time product: {ot['product_name']}...")
            product = stripe.Product.create(
                name=ot["product_name"],
                description=ot["description"],
            )
            price = stripe.Price.create(
                unit_amount=ot["amount_cents"],
                currency="usd",
                product=product.id,
            )
            print(f"   [OK] Price ID: {price.id}")
            print(f"   [INFO]  Add to .env:  {ot['env_key']}={price.id}")

        db.commit()

        # -------------------------------------------------------
        # Summary
        # -------------------------------------------------------
        print("\n" + "=" * 60)
        print("SETUP COMPLETE — STRIPE PRICE IDs")
        print("=" * 60)
        for tier, ids in results.items():
            print(f"  {tier:<16} monthly={ids['monthly']}")
            print(f"  {tier:<16} annual ={ids['annual']}")
        print("=" * 60)
        print("DB has been updated. Paid checkout is now live.")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    setup_products()
