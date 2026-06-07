import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "database" / "village_api.db"

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

print("DATABASE TEST STARTED")
print("----------------------")

# 1. Check all table counts
tables = [
    "countries",
    "states",
    "districts",
    "subdistricts",
    "villages",
    "users",
    "api_keys",
    "api_logs"
]

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"{table}: {count}")

print("\nSample states:")
cursor.execute("""
SELECT state_code, state_name
FROM states
LIMIT 10
""")
for row in cursor.fetchall():
    print(row)

print("\nSearch village example:")
cursor.execute("""
SELECT 
    v.village_name,
    s.subdistrict_name,
    d.district_name,
    st.state_name,
    'India' AS country_name
FROM villages v
JOIN subdistricts s 
    ON v.state_code = s.state_code
    AND v.district_code = s.district_code
    AND v.subdistrict_code = s.subdistrict_code
JOIN districts d
    ON v.state_code = d.state_code
    AND v.district_code = d.district_code
JOIN states st
    ON v.state_code = st.state_code
WHERE v.village_name LIKE ?
LIMIT 10
""", ("%Manibeli%",))

results = cursor.fetchall()

if results:
    for row in results:
        print(row)
else:
    print("No village found for Manibeli")

conn.close()

print("\nDATABASE TEST COMPLETED")