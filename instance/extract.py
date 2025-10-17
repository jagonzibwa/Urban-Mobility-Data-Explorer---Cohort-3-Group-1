import sqlite3
import json
import os

# Use the database file located in the same directory as this script (instance/site.db)
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance/site.db')
OUTPUT_FILE = 'urban_mobility_data.json'

def fetch_table(conn, table_name):
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]
   

def export_all_to_json():
    conn = sqlite3.connect(DB_PATH)

    # List available tables for diagnostics
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    available = [r[0] for r in cur.fetchall()]
    print(f"Using DB at: {DB_PATH}")
    print(f"Available tables: {available}")

    tables_to_export = {
        "vendors": "Vendor",
        "locations": "Location",
        "trips": "Trip",
    }

    data = {}
    # Build a case-insensitive mapping from desired table name to actual table name in DB
    actual_tables_map = {t.lower(): t for t in available}

    for key, desired in tables_to_export.items():
        actual = None
        # Try exact match first
        if desired in available:
            actual = desired
        else:
            # Case-insensitive match
            actual = actual_tables_map.get(desired.lower())

        if actual:
            try:
                data[key] = fetch_table(conn, actual)
            except sqlite3.OperationalError as e:
                print(f"Could not fetch table '{actual}': {e}")
                data[key] = []
        else:
            print(f"Table matching '{desired}' not found in DB (checked: {available})")
            data[key] = []

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"All tables exported to {OUTPUT_FILE}")
    conn.close()

export_all_to_json()