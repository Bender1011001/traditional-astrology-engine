import sqlite3

con = sqlite3.connect(r'E:\code.projects\astrology\astrology.db')
cur = con.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cur.fetchall()]
print('=== astrology.db tables ===')
for t in tables:
    cur.execute(f'SELECT COUNT(*) FROM "{t}"')
    count = cur.fetchone()[0]
    print(f'  {t}: {count} rows')
    if count > 0:
        cur.execute(f'PRAGMA table_info("{t}")')
        cols = [c[1] for c in cur.fetchall()]
        print(f'    cols: {cols}')
        if count <= 15:
            cur.execute(f'SELECT * FROM "{t}" LIMIT 5')
            for row in cur.fetchall():
                truncated = tuple(str(v)[:100] if isinstance(v, str) and len(str(v)) > 100 else v for v in row)
                print(f'    {truncated}')
con.close()
