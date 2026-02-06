import os
import stripe
import sys

# Load env vars
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# We can just check os.environ directly if loaded or load it manually
# For robustness, let's look for .env in root
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(root_dir, '.env')

if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k] = v

api_key = os.getenv('STRIPE_SECRET_KEY')

def setup_products():
    if not api_key:
        print("Error: STRIPE_SECRET_KEY not found in environment or .env file.")
        print("Please add your 'sk_test_...' key to the .env file first.")
        return

    stripe.api_key = api_key
    print(f"Using Stripe Key: {api_key[:8]}...")

    try:
        # --- D2C PLANS ---

        # 1. Starter ($29/mo)
        print("\nCreating Starter Plan ($29/mo)...")
        starter = stripe.Product.create(name="Codex Caelestis - Starter", description="50 charts/mo, forensic audit, PDF export.")
        starter_mo = stripe.Price.create(unit_amount=2900, currency="usd", recurring={"interval": "month"}, product=starter.id)
        starter_yr = stripe.Price.create(unit_amount=29000, currency="usd", recurring={"interval": "year"}, product=starter.id)
        print(f"✅ Starter IDs: {starter_mo.id} (Mo) / {starter_yr.id} (Yr)")

        # 2. Practitioner ($149/mo)
        print("\nCreating Practitioner Plan ($149/mo)...")
        practitioner = stripe.Product.create(name="Codex Caelestis - Practitioner", description="Unlimited charts, commercial license, bulk upload.")
        practitioner_mo = stripe.Price.create(unit_amount=14900, currency="usd", recurring={"interval": "month"}, product=practitioner.id)
        practitioner_yr = stripe.Price.create(unit_amount=149000, currency="usd", recurring={"interval": "year"}, product=practitioner.id)
        print(f"✅ Practitioner IDs: {practitioner_mo.id} (Mo) / {practitioner_yr.id} (Yr)")

        # --- B2B API PLANS ---

        # 3. Master ($299/mo)
        print("\nCreating Master API Plan ($299/mo)...")
        master = stripe.Product.create(name="Codex Caelestis - Master API", description="3,000 calls/mo, white-label.")
        master_mo = stripe.Price.create(unit_amount=29900, currency="usd", recurring={"interval": "month"}, product=master.id)
        master_yr = stripe.Price.create(unit_amount=299000, currency="usd", recurring={"interval": "year"}, product=master.id)
        print(f"✅ Master IDs: {master_mo.id} (Mo) / {master_yr.id} (Yr)")

        # 4. Agency ($799/mo)
        print("\nCreating Agency API Plan ($799/mo)...")
        agency = stripe.Product.create(name="Codex Caelestis - Agency API", description="30,000 calls/mo, SLA, dedicated support.")
        agency_mo = stripe.Price.create(unit_amount=79900, currency="usd", recurring={"interval": "month"}, product=agency.id)
        agency_yr = stripe.Price.create(unit_amount=799000, currency="usd", recurring={"interval": "year"}, product=agency.id)
        print(f"✅ Agency IDs: {agency_mo.id} (Mo) / {agency_yr.id} (Yr)")

        print("\n" + "="*50)
        print("UPDATE seed_fresh_db.py AND .env WITH THESE IDs:")
        print("="*50)
        print(f"STARTER_IDs:      {starter_mo.id} / {starter_yr.id}")
        print(f"PRACTITIONER_IDs: {practitioner_mo.id} / {practitioner_yr.id}")
        print(f"MASTER_IDs:       {master_mo.id} / {master_yr.id}")
        print(f"AGENCY_IDs:       {agency_mo.id} / {agency_yr.id}")
        print("="*50)

    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    setup_products()
