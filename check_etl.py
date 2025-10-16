import sqlite3
import os

db = 'database.db'
print('DB exists:', os.path.exists(db))

try:
    import pandas as pd
    print('pandas', pd.__version__)
except Exception as e:
    print('pandas import error:', e)

conn = sqlite3.connect(db)
cur = conn.cursor()

for t in ('Vendor', 'Location', 'Trip'):
    try:
        n = cur.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
        print(f'{t}: {n:,}')
    except Exception as e:
        print(f'{t}: error -', e)

conn.close()
