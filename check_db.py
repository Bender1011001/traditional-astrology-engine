import sqlite3

for db_path in [r'E:\code.projects\astrology\astrology.db', r'E:\code.projects\astrology\users.db']:
    print(f'\n=== {db_path} ===')
    try:
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [r[0] for r in cur.fetchall()]
        print(f'Tables: {tables}')
        for t in tables:
            cur.execute(f'SELECT COUNT(*) FROM "{t}"')
            count = cur.fetchone()[0]
            print(f'  {t}: {count} rows')
            if 0 < count <= 20:
                cur.execute(f'PRAGMA table_info("{t}")')
                cols = [c[1] for c in cur.fetchall()]
                print(f'    Columns: {cols}')
                cur.execute(f'SELECT * FROM "{t}" LIMIT 5')
                for row in cur.fetchall():
                    # truncate long fields
                    truncated = tuple(str(v)[:120] if isinstance(v, str) and len(str(v)) > 120 else v for v in row)
                    print(f'    {truncated}')
        con.close()
    except Exception as e:
        print(f'ERROR: {e}')
