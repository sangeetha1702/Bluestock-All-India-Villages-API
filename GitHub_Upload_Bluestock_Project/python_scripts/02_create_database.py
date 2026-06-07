import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
import hashlib

# Project root
ROOT = Path(__file__).resolve().parents[1]

CLEANED_PATH = ROOT / "data" / "cleaned"
DATABASE_PATH = ROOT / "database" / "village_api.db"

DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Delete old database to avoid old UNIQUE constraint errors
if DATABASE_PATH.exists():
    DATABASE_PATH.unlink()
    print("Old database deleted. Creating fresh database...")

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

print("Creating full database tables...")

# 1. Countries
cursor.execute("""
CREATE TABLE countries (
    country_id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_code TEXT NOT NULL,
    country_name TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

# 2. States
cursor.execute("""
CREATE TABLE states (
    state_id INTEGER PRIMARY KEY AUTOINCREMENT,
    state_code TEXT NOT NULL,
    state_name TEXT NOT NULL,
    country_code TEXT DEFAULT 'IN',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

# 3. Districts
cursor.execute("""
CREATE TABLE districts (
    district_id INTEGER PRIMARY KEY AUTOINCREMENT,
    state_code TEXT NOT NULL,
    district_code TEXT NOT NULL,
    district_name TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

# 4. Subdistricts
cursor.execute("""
CREATE TABLE subdistricts (
    subdistrict_id INTEGER PRIMARY KEY AUTOINCREMENT,
    state_code TEXT NOT NULL,
    district_code TEXT NOT NULL,
    subdistrict_code TEXT NOT NULL,
    subdistrict_name TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

# 5. Villages
cursor.execute("""
CREATE TABLE villages (
    village_id INTEGER PRIMARY KEY AUTOINCREMENT,
    state_code TEXT NOT NULL,
    district_code TEXT NOT NULL,
    subdistrict_code TEXT NOT NULL,
    village_code TEXT NOT NULL,
    village_name TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

# 6. Users
cursor.execute("""
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    business_name TEXT,
    phone_number TEXT,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'B2B_USER',
    plan_type TEXT DEFAULT 'Free',
    account_status TEXT DEFAULT 'PENDING_APPROVAL',
    daily_request_limit INTEGER DEFAULT 5000,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

# 7. API Keys
cursor.execute("""
CREATE TABLE api_keys (
    api_key_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    key_name TEXT NOT NULL,
    api_key TEXT UNIQUE NOT NULL,
    api_secret_hash TEXT NOT NULL,
    status TEXT DEFAULT 'ACTIVE',
    daily_limit INTEGER DEFAULT 5000,
    last_used_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    expires_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
""")

# 8. API Logs
cursor.execute("""
CREATE TABLE api_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_key_id INTEGER,
    user_id INTEGER,
    endpoint TEXT NOT NULL,
    method TEXT DEFAULT 'GET',
    query_params TEXT,
    status_code INTEGER,
    response_time_ms INTEGER,
    ip_address TEXT,
    user_agent TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (api_key_id) REFERENCES api_keys(api_key_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
""")

print("Tables created successfully.")
print("Loading cleaned CSV data...")

# Read cleaned CSV files
country_df = pd.read_csv(CLEANED_PATH / "country.csv", dtype=str, keep_default_na=False)
states_df = pd.read_csv(CLEANED_PATH / "states.csv", dtype=str, keep_default_na=False)
districts_df = pd.read_csv(CLEANED_PATH / "districts.csv", dtype=str, keep_default_na=False)
subdistricts_df = pd.read_csv(CLEANED_PATH / "subdistricts.csv", dtype=str, keep_default_na=False)
villages_df = pd.read_csv(CLEANED_PATH / "villages.csv", dtype=str, keep_default_na=False)

# Strip spaces
for df in [country_df, states_df, districts_df, subdistricts_df, villages_df]:
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

# Remove duplicates safely
country_df = country_df.drop_duplicates(subset=["country_code"])
states_df = states_df.drop_duplicates(subset=["state_code"])
districts_df = districts_df.drop_duplicates(subset=["state_code", "district_code"])
subdistricts_df = subdistricts_df.drop_duplicates(
    subset=["state_code", "district_code", "subdistrict_code"]
)
villages_df = villages_df.drop_duplicates(
    subset=["state_code", "district_code", "subdistrict_code", "village_code"]
)

# Load data into tables
country_df.to_sql("countries", conn, if_exists="append", index=False)
states_df.to_sql("states", conn, if_exists="append", index=False)
districts_df.to_sql("districts", conn, if_exists="append", index=False)
subdistricts_df.to_sql("subdistricts", conn, if_exists="append", index=False)

# Villages is large, so load in chunks
villages_df.to_sql(
    "villages",
    conn,
    if_exists="append",
    index=False,
    chunksize=5000
)

print("Creating sample admin and B2B user...")

def hash_text(text):
    return hashlib.sha256(text.encode()).hexdigest()

admin_password = hash_text("admin123")
b2b_password = hash_text("user123")
api_secret_hash = hash_text("demo_secret_123")

# Admin user
cursor.execute("""
INSERT INTO users (
    full_name, email, business_name, phone_number,
    password_hash, role, plan_type, account_status,
    daily_request_limit, is_active
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    "Admin User",
    "admin@villageapi.com",
    "Village API Admin",
    "9999999999",
    admin_password,
    "ADMIN",
    "Unlimited",
    "ACTIVE",
    1000000,
    1
))

# Demo B2B user
cursor.execute("""
INSERT INTO users (
    full_name, email, business_name, phone_number,
    password_hash, role, plan_type, account_status,
    daily_request_limit, is_active
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    "Demo B2B User",
    "demo@client.com",
    "Demo Client Company",
    "8888888888",
    b2b_password,
    "B2B_USER",
    "Free",
    "ACTIVE",
    5000,
    1
))

demo_user_id = cursor.lastrowid

# Demo API key
cursor.execute("""
INSERT INTO api_keys (
    user_id, key_name, api_key, api_secret_hash,
    status, daily_limit, created_at
)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", (
    demo_user_id,
    "Demo API Key",
    "ak_demo_123456789",
    api_secret_hash,
    "ACTIVE",
    5000,
    datetime.now().isoformat()
))

demo_api_key_id = cursor.lastrowid

# Demo API log
cursor.execute("""
INSERT INTO api_logs (
    api_key_id, user_id, endpoint, method,
    query_params, status_code, response_time_ms,
    ip_address, user_agent
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    demo_api_key_id,
    demo_user_id,
    "/api/v1/states",
    "GET",
    "{}",
    200,
    45,
    "127.0.0.1",
    "Postman"
))

print("Creating indexes for fast search...")

cursor.execute("CREATE INDEX idx_states_code ON states(state_code)")
cursor.execute("CREATE INDEX idx_states_name ON states(state_name)")

cursor.execute("CREATE INDEX idx_districts_state_code ON districts(state_code)")
cursor.execute("CREATE INDEX idx_districts_code ON districts(district_code)")
cursor.execute("CREATE INDEX idx_districts_name ON districts(district_name)")

cursor.execute("CREATE INDEX idx_subdistricts_state_district ON subdistricts(state_code, district_code)")
cursor.execute("CREATE INDEX idx_subdistricts_code ON subdistricts(subdistrict_code)")
cursor.execute("CREATE INDEX idx_subdistricts_name ON subdistricts(subdistrict_name)")

cursor.execute("CREATE INDEX idx_villages_state_district_subdistrict ON villages(state_code, district_code, subdistrict_code)")
cursor.execute("CREATE INDEX idx_villages_code ON villages(village_code)")
cursor.execute("CREATE INDEX idx_villages_name ON villages(village_name)")

cursor.execute("CREATE INDEX idx_api_keys_key ON api_keys(api_key)")
cursor.execute("CREATE INDEX idx_api_logs_user ON api_logs(user_id)")
cursor.execute("CREATE INDEX idx_api_logs_created_at ON api_logs(created_at)")

conn.commit()

print("\nDatabase created successfully!")
print("--------------------------------")

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

print("\nDatabase saved at:")
print(DATABASE_PATH)

conn.close()