import os
import json
from datetime import datetime
from app.auth.crypto import hash_password

# The path where your local text database will live
JSON_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database.json")

# =========================================================================
# GLOBAL IN-MEMORY OBJECT CONTEXTS
# =========================================================================
db_admins = []
db_clients = []
db_users = []
db_employees = []
db_attendance = []
db_face_embeddings = {}  # Format: {"employee_id_string": [float, float, ...]}

def save_to_json():
    """Serializes and writes all current database variables into a local JSON text file."""
    data = {
        "db_admins": db_admins,
        "db_clients": db_clients,
        "db_users": db_users,
        "db_employees": db_employees,
        "db_attendance": db_attendance,
        "db_face_embeddings": db_face_embeddings
    }
    with open(JSON_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_from_json():
    """Loads records from database.json on server startup, or seeds default data if empty."""
    global db_admins, db_clients, db_users, db_employees, db_attendance, db_face_embeddings
    
    if os.path.exists(JSON_DB_PATH):
        try:
            with open(JSON_DB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                db_admins = data.get("db_admins", [])
                db_clients = data.get("db_clients", [])
                db_users = data.get("db_users", [])
                db_employees = data.get("db_employees", [])
                db_attendance = data.get("db_attendance", [])
                db_face_embeddings = data.get("db_face_embeddings", {})
                print(f"[DATABASE INFO] Successfully loaded persisted states from local file schema.")
                return
        except Exception as e:
            print(f"[DATABASE ERROR] Could not read file structure, seeding defaults: {e}")

    # =========================================================================
    # SEED DEFAULT FALLBACK VALUES (If file doesn't exist yet)
    # =========================================================================
    print(f"[DATABASE INFO] Local storage file not found. Seeding initial setup data entries...")
    db_admins.append({
        "id": 1, "username": "admin", "email": "admin@worksight.com",
        "hashed_password": hash_password("password"), "role": "ADMIN", "status": "active"
    })
    db_clients.extend([
        {"id": 1, "company_name": "ABC Technology", "company_code": "ABC001", "status": "active", "created_at": "2026-09-01T10:00:00"},
        {"id": 2, "company_name": "XYZ Company", "company_code": "XYZ001", "status": "active", "created_at": "2026-09-05T10:00:00"}
    ])
    db_users.append({
        "id": 10, "client_id": 1, "username": "alice", "email": "alice@abc.com",
        "hashed_password": hash_password("password"), "role": "HR", "status": "active"
    })
    db_employees.append({
        "id": 101, "client_id": 1, "employee_code": "EMP001", "first_name": "John", "last_name": "Smith",
        "email": "john@abc.com", "phone": "123456789", "department": "IT", "position": "Software Engineer",
        "status": "active", "face_registered": True, "created_at": "2026-09-01T09:00:00"
    })
    db_attendance.append({
        "id": 1001, "employee_id": 101, "client_id": 1, "date": "2026-09-17",
        "check_in": "2026-09-17T08:52:00", "check_out": "2026-09-17T18:10:00", "status": "on_time",
        "worked_hours": 9.3, "overtime_hours": 1.3, "undertime_hours": 0
    })
    
    # Save newly seeded fields straight away
    save_to_json()

# Trigger an initial layout compilation boot load automatically when app imports this file module context
load_from_json()
