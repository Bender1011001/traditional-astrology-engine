import os, sys
ROOT = r"E:\code.projects\astrology"
os.chdir(ROOT)
sys.path.insert(0, ROOT)
os.environ.setdefault("STRIPE_SECRET_KEY","sk_test_dummy")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET","whsec_dummy")
os.environ.setdefault("JWT_SECRET","devsecret")
os.environ.setdefault("SENDER_EMAIL","dev@test.local")
os.environ.setdefault("SALES_MODE","pilot")
os.environ.setdefault("DATABASE_URL","sqlite:///./users.db")
os.environ.setdefault("OPENROUTER_API_KEY","dummy")
import uvicorn
from src.app import app
uvicorn.run(app, host="127.0.0.1", port=8011)
