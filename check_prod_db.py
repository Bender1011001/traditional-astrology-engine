import psycopg2
import psycopg2.extras

# Connect via public IP (need to allow this IP in Cloud SQL authorized networks, or use proxy)
# Using the prod credentials from Cloud Run
conn_str = "postgresql://postgres:AstrF0rg3_Pr0d_2026!@34.57.76.114/astrology"

try:
    conn = psycopg2.connect(conn_str, connect_timeout=10)
    cur = conn.cursor()

    # Get all tables
    cur.execute("""
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename
    """)
    tables = [r[0] for r in cur.fetchall()]
    print("=== PRODUCTION Cloud SQL Tables ===")
    for t in tables:
        cur.execute(f'SELECT COUNT(*) FROM "{t}"')
        count = cur.fetchone()[0]
        print(f"  {t}: {count} rows")

    # Drill into the interesting ones
    interesting = ['chart_events', 'reading_feedback_events', 'guest_requests',
                   'async_report_tasks', 'users', 'user_subscriptions']

    for t in interesting:
        if t not in tables:
            print(f"\n[{t}] - TABLE DOES NOT EXIST")
            continue
        cur.execute(f'SELECT COUNT(*) FROM "{t}"')
        count = cur.fetchone()[0]
        print(f"\n=== {t} ({count} rows) ===")
        if count > 0:
            cur.execute(f'SELECT * FROM "{t}" ORDER BY 1 DESC LIMIT 10')
            rows = cur.fetchall()
            cols = [desc[0] for desc in cur.description]
            print(f"  Columns: {cols}")
            for row in rows:
                truncated = tuple(str(v)[:120] if isinstance(v, str) and len(str(v)) > 120 else v for v in row)
                print(f"  {truncated}")

    conn.close()

except Exception as e:
    print(f"Connection error: {e}")
    print("\nTrying to check if psycopg2 is installed...")
    import subprocess
    import sys
    subprocess.run([sys.executable, "-m", "pip", "show", "psycopg2-binary"], capture_output=False)
