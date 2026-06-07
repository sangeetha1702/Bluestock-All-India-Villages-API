from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from pathlib import Path
import time

app = Flask(__name__)
CORS(app)

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "database" / "village_api.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def check_api_key():
    # First check API key from header
    api_key = request.headers.get("X-API-Key")

    # Browser testing purpose: allow API key from URL also
    if not api_key:
        api_key = request.args.get("api_key")

    if not api_key:
        return False

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT api_key_id, user_id, status
        FROM api_keys
        WHERE api_key = ?
    """, (api_key,))

    key_data = cursor.fetchone()
    conn.close()

    if key_data and key_data["status"] == "ACTIVE":
        return True

    return False

def api_key_required():
    if not check_api_key():
        return jsonify({
            "success": False,
            "message": "Invalid or missing API key"
        }), 401
    return None


@app.route("/")
def home():
    return jsonify({
        "success": True,
        "message": "All India Villages API is running"
    })


@app.route("/api/v1/states", methods=["GET"])
def get_states():
    auth_error = api_key_required()
    if auth_error:
        return auth_error

    start_time = time.time()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT state_code, state_name
        FROM states
        ORDER BY state_name
    """)

    rows = cursor.fetchall()
    conn.close()

    data = [dict(row) for row in rows]

    response_time = round((time.time() - start_time) * 1000)

    return jsonify({
        "success": True,
        "count": len(data),
        "responseTimeMs": response_time,
        "data": data
    })


@app.route("/api/v1/states/<state_code>/districts", methods=["GET"])
def get_districts_by_state(state_code):
    auth_error = api_key_required()
    if auth_error:
        return auth_error

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT district_code, district_name, state_code
        FROM districts
        WHERE state_code = ?
        ORDER BY district_name
    """, (state_code,))

    rows = cursor.fetchall()
    conn.close()

    data = [dict(row) for row in rows]

    return jsonify({
        "success": True,
        "count": len(data),
        "data": data
    })


@app.route("/api/v1/districts/<district_code>/subdistricts", methods=["GET"])
def get_subdistricts_by_district(district_code):
    auth_error = api_key_required()
    if auth_error:
        return auth_error

    state_code = request.args.get("state_code")

    conn = get_db_connection()
    cursor = conn.cursor()

    if state_code:
        cursor.execute("""
            SELECT subdistrict_code, subdistrict_name, district_code, state_code
            FROM subdistricts
            WHERE district_code = ? AND state_code = ?
            ORDER BY subdistrict_name
        """, (district_code, state_code))
    else:
        cursor.execute("""
            SELECT subdistrict_code, subdistrict_name, district_code, state_code
            FROM subdistricts
            WHERE district_code = ?
            ORDER BY subdistrict_name
        """, (district_code,))

    rows = cursor.fetchall()
    conn.close()

    data = [dict(row) for row in rows]

    return jsonify({
        "success": True,
        "count": len(data),
        "data": data
    })


@app.route("/api/v1/subdistricts/<subdistrict_code>/villages", methods=["GET"])
def get_villages_by_subdistrict(subdistrict_code):
    auth_error = api_key_required()
    if auth_error:
        return auth_error

    state_code = request.args.get("state_code")
    district_code = request.args.get("district_code")
    limit = request.args.get("limit", 100)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT village_code, village_name, subdistrict_code, district_code, state_code
        FROM villages
        WHERE subdistrict_code = ?
        AND (? IS NULL OR state_code = ?)
        AND (? IS NULL OR district_code = ?)
        ORDER BY village_name
        LIMIT ?
    """, (
        subdistrict_code,
        state_code, state_code,
        district_code, district_code,
        int(limit)
    ))

    rows = cursor.fetchall()
    conn.close()

    data = [dict(row) for row in rows]

    return jsonify({
        "success": True,
        "count": len(data),
        "data": data
    })


@app.route("/api/v1/search", methods=["GET"])
def search_villages():
    auth_error = api_key_required()
    if auth_error:
        return auth_error

    query = request.args.get("q", "")
    limit = request.args.get("limit", 10)

    if len(query) < 2:
        return jsonify({
            "success": False,
            "message": "Search query must be at least 2 characters"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            v.village_code,
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
        LIMIT ?
    """, (f"%{query}%", int(limit)))

    rows = cursor.fetchall()
    conn.close()

    data = []

    for row in rows:
        full_address = f"{row['village_name']}, {row['subdistrict_name']}, {row['district_name']}, {row['state_name']}, India"

        data.append({
            "value": row["village_code"],
            "label": row["village_name"],
            "fullAddress": full_address,
            "hierarchy": {
                "village": row["village_name"],
                "subDistrict": row["subdistrict_name"],
                "district": row["district_name"],
                "state": row["state_name"],
                "country": "India"
            }
        })

    return jsonify({
        "success": True,
        "count": len(data),
        "data": data
    })


@app.route("/api/v1/autocomplete", methods=["GET"])
def autocomplete():
    auth_error = api_key_required()
    if auth_error:
        return auth_error

    query = request.args.get("q", "")
    limit = request.args.get("limit", 10)

    if len(query) < 2:
        return jsonify({
            "success": False,
            "message": "Autocomplete query must be at least 2 characters"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            v.village_code,
            v.village_name,
            s.subdistrict_name,
            d.district_name,
            st.state_name
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
        LIMIT ?
    """, (f"{query}%", int(limit)))

    rows = cursor.fetchall()
    conn.close()

    data = []

    for row in rows:
        data.append({
            "value": row["village_code"],
            "label": f"{row['village_name']} ({row['subdistrict_name']}, {row['district_name']}, {row['state_name']})",
            "fullAddress": f"{row['village_name']}, {row['subdistrict_name']}, {row['district_name']}, {row['state_name']}, India"
        })

    return jsonify({
        "success": True,
        "count": len(data),
        "data": data
    })

@app.route("/api/v1/admin/stats", methods=["GET"])
def admin_stats():
    auth_error = api_key_required()
    if auth_error:
        return auth_error

    conn = get_db_connection()
    cursor = conn.cursor()

    tables = {
        "countries": "countries",
        "states": "states",
        "districts": "districts",
        "subdistricts": "subdistricts",
        "villages": "villages",
        "users": "users",
        "api_keys": "api_keys",
        "api_logs": "api_logs"
    }

    stats = {}

    for key, table in tables.items():
        cursor.execute(f"SELECT COUNT(*) AS total FROM {table}")
        stats[key] = cursor.fetchone()["total"]

    conn.close()

    return jsonify({
        "success": True,
        "data": {
            "totalCountries": stats["countries"],
            "totalStates": stats["states"],
            "totalDistricts": stats["districts"],
            "totalSubdistricts": stats["subdistricts"],
            "totalVillages": stats["villages"],
            "totalUsers": stats["users"],
            "totalApiKeys": stats["api_keys"],
            "totalApiLogs": stats["api_logs"]
        }
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)