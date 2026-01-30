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
        # 1. Create Monthly Product
        print("\nCreating Monthly Subscription...")
        monthly = stripe.Product.create(
            name="Codex Caelestis - Pro Access (Monthly)",
            description="Unlimited chart readings, full forensic reports, and 5-year forecasts.",
        )
        
        monthly_price = stripe.Price.create(
            unit_amount=499, # $4.99
            currency="usd",
            recurring={"interval": "month"},
            product=monthly.id,
        )
        print(f"✅ Success! Monthly Price ID: {monthly_price.id}")

        # 2. Create Annual Product
        print("\nCreating Annual Subscription...")
        annual = stripe.Product.create(
            name="Codex Caelestis - Pro Access (Annual)",
            description="Unlimited access for 1 year. Save ~17%.",
        )
        
        annual_price = stripe.Price.create(
            unit_amount=4900, # $49.00
            currency="usd",
            recurring={"interval": "year"},
            product=annual.id,
        )
        print(f"✅ Success! Annual Price ID: {annual_price.id}")
        
        print("\n" + "="*50)
        print("COPY THESE LINES INTO YOUR .env FILE:")
        print("="*50)
        print(f"STRIPE_SUBSCRIPTION_PRICE_ID={monthly_price.id}")
        print(f"STRIPE_ANNUAL_PRICE_ID={annual_price.id}")
        print("="*50)

    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    setup_products()
