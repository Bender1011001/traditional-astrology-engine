"""Quick read-only count of key tables in production Cloud SQL."""
import os, sys
sys.path.insert(0, ".")

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text

db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("ERROR: DATABASE_URL not in environment")
    sys.exit(1)

engine = create_engine(db_url, connect_args={"connect_timeout": 15})

queries = {
    "chart_events (free charts generated, tracked since 2026-05-02)": (
        "SELECT COUNT(*) as total, "
        "MIN(created_at) as first_at, "
        "MAX(created_at) as last_at "
        "FROM chart_events"
    ),
    "reading_feedback_events (good/bad votes)": (
        "SELECT COUNT(*) as total, "
        "SUM(CASE WHEN vote='good' THEN 1 ELSE 0 END) as good, "
        "SUM(CASE WHEN vote='bad'  THEN 1 ELSE 0 END) as bad  "
        "FROM reading_feedback_events"
    ),
    "guest_requests (legacy rate-limit rows)": (
        "SELECT COUNT(*) as total FROM guest_requests"
    ),
    "async_report_tasks (paid report jobs by status)": (
        "SELECT COALESCE(status,'unknown') as status, COUNT(*) as cnt "
        "FROM async_report_tasks GROUP BY status ORDER BY cnt DESC"
    ),
    "horary_rate_limits (horary questions asked)": (
        "SELECT COUNT(*) as total FROM horary_rate_limits"
    ),
    "leads (email captures)": (
        "SELECT COUNT(*) as total FROM leads"
    ),
}

with engine.connect() as conn:
    for label, sql in queries.items():
        try:
            result = conn.execute(text(sql))
            rows = result.fetchall()
            cols = result.keys() if hasattr(result, "keys") else []
            print(f"\n=== {label} ===")
            for row in rows:
                print("  ", dict(zip(cols, row)))
        except Exception as e:
            print(f"\n=== {label} ===")
            print(f"  ERROR: {e}")
