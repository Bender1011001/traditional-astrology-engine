import os
import stripe
import sys

# Load env vars
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(root_dir, '.env')

if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k] = v

api_key = os.getenv('STRIPE_SECRET_KEY')

if not api_key:
    print("No API Key found.")
    sys.exit(1)

stripe.api_key = api_key

try:
    print("Listing recent prices...")
    prices = stripe.Price.list(limit=5)
    for p in prices.data:
        prod = stripe.Product.retrieve(p.product)
        print(f"Product: {prod.name}")
        print(f"  Price ID: {p.id}")
        print(f"  Amount: {p.unit_amount/100} {p.currency}")
        print("-" * 30)
except Exception as e:
    print(e)
