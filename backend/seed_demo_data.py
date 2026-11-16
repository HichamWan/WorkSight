"""
WorkSight demo data seeder
==========================

Populates backend/database.json with realistic demo data so the platform
looks complete during development and demonstrations:

  * 16 demo client companies (20 total including the pre-existing 4)
  * 100 demo employees spread across the demo companies
  * One HR account (+ MANAGER for some companies) per demo company
  * ~30 days of attendance history (weekdays) + today's check-ins
  * Leave requests with mixed statuses
  * Audit-trail activity entries

Design rules:
  * REPEATABLE / IDEMPOTENT  - every generated record carries the
    "demo.worksight.io" marker (company_code prefix "DEMO", email domain,
    employee emails). Re-running the script first removes ONLY previously
    seeded demo records, so no duplicates can accumulate.
  * NEVER touches real data  - the built-in admin, existing client
    companies, user accounts (alice / noura_test / noura), employees
    John Smith & Alex Tester, their attendance/leaves/activity and face
    embeddings are left untouched.
  * Passwords are hashed with the app's own bcrypt helper
    (app.auth.crypto.hash_password) - same auth system as the API.

Usage (stop the backend server first - it keeps state in memory and would
overwrite the file on its next save):
    cd backend
    python seed_demo_data.py
Then start the server again:  uvicorn app.main:app --reload --port 8000
"""

import json
import os
import random
import sys
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app.auth.crypto import hash_password  # noqa: E402  (project's own hashing)

JSON_DB_PATH = os.path.join(BASE_DIR, "database.json")

# ---------------------------------------------------------------- markers --
DEMO_EMAIL_DOMAIN = "demo.worksight.io"     # all demo users/employees use it
DEMO_CODE_PREFIX = "DEMO"                   # demo company_code: "DEMO001"...
DEMO_USERNAME_PREFIX = "hr_"                # demo login usernames: "hr_novacloud"

DEMO_PASSWORD = "password123"               # login password for every demo account

# deterministic output across runs
random.seed(20261115)

# ------------------------------------------------------------- static data --
DEMO_COMPANIES = [
    "NovaCloud Systems", "Vertex Analytics", "BlueOrbit Tech", "HelixSoft Labs",
    "QuantumLeap AI", "SilverLine Logistics", "IronPeak Security", "GreenField Energy",
    "Meridian Health Group", "Summit Financial", "Catalyst Media", "Aurora Robotics",
    "DataForge Solutions", "Skyline Ventures", "Northwind Retail", "TerraBuild Construction",
]

DEPARTMENTS_POSITIONS = {
    "Engineering": ["Software Engineer", "Senior Software Engineer", "Backend Developer",
                    "Frontend Developer", "Full Stack Developer", "QA Engineer",
                    "DevOps Engineer", "Java Developer", "Python Developer"],
    "IT": ["IT Support Specialist", "System Administrator", "Network Engineer"],
    "Data & AI": ["Data Analyst", "Data Scientist", "AI Engineer", "Machine Learning Engineer"],
    "Security": ["Cybersecurity Engineer", "Security Analyst"],
    "HR": ["HR Specialist", "Recruiter", "People Operations Coordinator"],
    "Finance": ["Accountant", "Financial Analyst"],
    "Marketing": ["Marketing Specialist", "Content Strategist"],
    "Sales": ["Sales Representative", "Account Manager"],
    "Operations": ["Operations Coordinator", "Project Manager"],
    "Design": ["UI/UX Designer", "Graphic Designer"],
    "Customer Support": ["Support Specialist", "Customer Success Manager"],
}

FIRST_NAMES = [
    "Amelia", "Liam", "Sofia", "Noah", "Maya", "Ethan", "Zara", "Lucas", "Aisha", "Omar",
    "Elena", "James", "Priya", "Daniel", "Fatima", "Leo", "Nora", "Hugo", "Yara", "Adam",
    "Clara", "Oscar", "Leila", "Marcus", "Iris", "Tariq", "Hannah", "Victor", "Salma", "Felix",
    "Julia", "Karim", "Emma", "Andre", "Dina", "Peter", "Rania", "Simon", "Talia", "Yusuf",
    "Marta", "Rami", "Ingrid", "Samir", "Chloe", "Diego", "Amal", "Erik", "Lina", "Jonas",
]

LAST_NAMES = [
    "Bennett", "Alvarez", "Okafor", "Nguyen", "Kowalski", "Haddad", "Lindqvist", "Moreau",
    "Tanaka", "Silva", "Novak", "Rahman", "Petrov", "Costa", "Delgado", "Fischer",
    "Ibrahim", "Jensen", "Kim", "Lombardi", "Meyer", "Nakamura", "Osei", "Popescu",
    "Quinn", "Rossi", "Santos", "Tran", "Ueda", "Vargas", "Weber", "Xu", "Yilmaz",
    "Zhang", "Andersson", "Bauer", "Cruz", "Dubois", "Eriksen", "Farrell", "Garcia",
    "Hoffman", "Ivanov", "Johansson", "Keller", "Laurent", "Mendes", "Nilsen",
]

LEAVE_REASONS = [
    "Annual vacation", "Family event", "Medical appointment", "Personal matters",
    "Relocation", "Wedding", "Exam preparation", "Childcare",
]

ACTIVITY_ACTIONS = ["employee_created", "employee_updated", "check_in", "check_out",
                    "face_enrolled", "leave_requested", "leave_approved"]


def _slug(name: str) -> str:
    return "".join(ch for ch in name.lower() if ch.isalnum())


def _next_id(rows):
    return max((r["id"] for r in rows), default=0) + 1


def load_db():
    with open(JSON_DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(data):
    with open(JSON_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def remove_previous_demo(data):
    """Delete only records created by a previous run of this script."""
    demo_client_ids = {c["id"] for c in data["db_clients"]
                       if str(c.get("company_code", "")).startswith(DEMO_CODE_PREFIX)}
    demo_user_ids = {u["id"] for u in data["db_users"]
                     if str(u.get("email", "")).endswith("@" + DEMO_EMAIL_DOMAIN)}
    demo_employee_ids = {e["id"] for e in data["db_employees"]
                         if str(e.get("email", "")).endswith("@" + DEMO_EMAIL_DOMAIN)}

    data["db_clients"] = [c for c in data["db_clients"] if c["id"] not in demo_client_ids]
    data["db_users"] = [u for u in data["db_users"] if u["id"] not in demo_user_ids]
    data["db_employees"] = [e for e in data["db_employees"] if e["id"] not in demo_employee_ids]
    data["db_attendance"] = [a for a in data["db_attendance"]
                             if a["client_id"] not in demo_client_ids
                             and a["employee_id"] not in demo_employee_ids]
    data["db_leaves"] = [l for l in data["db_leaves"]
                         if l["client_id"] not in demo_client_ids
                         and l["employee_id"] not in demo_employee_ids]
    data["db_activity"] = [a for a in data["db_activity"]
                           if a["client_id"] not in demo_client_ids]
    return demo_client_ids, demo_user_ids, demo_employee_ids


def build_companies(data, now):
    clients, users = data["db_clients"], data["db_users"]
    pw_hash = hash_password(DEMO_PASSWORD)
    client_id = _next_id(clients)
    user_id = _next_id(users)
    new_clients, new_users = [], []

    for i, company in enumerate(DEMO_COMPANIES, start=1):
        code = f"{DEMO_CODE_PREFIX}{i:03d}"
        slug = _slug(company)
        created = now - timedelta(days=random.randint(120, 420), hours=random.randint(0, 9))
        new_clients.append({
            "id": client_id,
            "company_name": company,
            "company_code": code,
            "status": "active",
            "created_at": created.isoformat(),
        })
        new_users.append({
            "id": user_id,
            "client_id": client_id,
            "username": f"{DEMO_USERNAME_PREFIX}{slug}",
            "email": f"hr.{slug}@{DEMO_EMAIL_DOMAIN}",
            "hashed_password": pw_hash,
            "role": "HR",
            "status": "active",
        })
        # A MANAGER account for roughly half of the demo companies
        if i % 2 == 0:
            new_users.append({
                "id": user_id + 1,
                "client_id": client_id,
                "username": f"mgr_{slug}",
                "email": f"manager.{slug}@{DEMO_EMAIL_DOMAIN}",
                "hashed_password": pw_hash,
                "role": "MANAGER",
                "status": "active",
            })
        client_id += 1
        user_id += 2 if i % 2 == 0 else 1

    clients.extend(new_clients)
    users.extend(new_users)
    return new_clients


def build_employees(data, clients, now):
    employees = data["db_employees"]
    emp_id = _next_id(employees)
    new_employees = []
    used_emails = set()
    total_target = 100

    # Every demo company gets at least 3 employees; the rest is spread randomly (target: 100)
    dept_names = list(DEPARTMENTS_POSITIONS.keys())
    sizes = [3] * len(clients)
    remaining = total_target - sum(sizes)
    while remaining > 0:
        idx = random.randrange(len(sizes))
        add = min(random.randint(1, 4), remaining)
        sizes[idx] += add
        remaining -= add
    for client, size in zip(clients, sizes):
        for _ in range(size):
            while True:
                first = random.choice(FIRST_NAMES)
                last = random.choice(LAST_NAMES)
                email = f"{first.lower()}.{last.lower()}@{DEMO_EMAIL_DOMAIN}"
                if email not in used_emails:
                    used_emails.add(email)
                    break
            dept = random.choice(dept_names)
            position = random.choice(DEPARTMENTS_POSITIONS[dept])
            new_employees.append({
                "id": emp_id,
                "client_id": client["id"],
                "employee_code": f"EMP{emp_id}",
                "first_name": first,
                "last_name": last,
                "email": email,
                "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                "department": dept,
                "position": position,
                "status": "active",
                "face_registered": False,
                "created_at": (now - timedelta(days=random.randint(30, 400))).isoformat(),
            })
            emp_id += 1

    employees.extend(new_employees)
    return new_employees


def _worked_hours(check_in_dt, check_out_dt):
    """Hours worked minus a 30 min break, rounded to 1 decimal."""
    gross = (check_out_dt - check_in_dt).total_seconds() / 3600.0
    return round(max(0.0, gross - 0.5), 1)


def build_attendance(data, employees, now):
    attendance = data["db_attendance"]
    att_id = _next_id(attendance)
    new_rows = []
    today = now.date()

    for emp in employees:
        cid = emp["client_id"]
        # ---- history: last 30 calendar days, weekdays only -----------------
        for offset in range(30, 0, -1):
            day = today - timedelta(days=offset)
            if day.weekday() >= 5:  # weekend
                continue
            if random.random() < 0.07:  # absent day -> no record
                continue
            late = random.random() < 0.16
            in_h, in_m = (9, random.randint(1, 25)) if late else (8, random.randint(25, 59))
            out_h = random.choice([17, 17, 18, 18, 19])
            check_in = datetime(day.year, day.month, day.day, in_h, in_m, random.randint(0, 59))
            check_out = datetime(day.year, day.month, day.day, out_h, random.randint(0, 59))
            worked = _worked_hours(check_in, check_out)
            overtime = round(max(0.0, worked - 9.0), 1)
            undertime = round(max(0.0, 8.0 - worked), 1)
            new_rows.append({
                "id": att_id, "employee_id": emp["id"], "client_id": cid,
                "date": day.isoformat(),
                "check_in": check_in.isoformat(), "check_out": check_out.isoformat(),
                "status": "late" if late else "on_time",
                "worked_hours": worked, "overtime_hours": overtime,
                "undertime_hours": 0.0 if worked >= 8 else undertime,
            })
            att_id += 1

        # ---- today: partial check-ins so the dashboard looks live ----------
        if random.random() < 0.75:
            late = random.random() < 0.12
            in_h, in_m = (9, random.randint(1, 20)) if late else (8, random.randint(30, 59))
            check_in = datetime(today.year, today.month, today.day, in_h, in_m)
            still_working = random.random() < 0.35
            if still_working:
                check_out, worked, ot, ut = None, 0.0, 0.0, 0.0
            else:
                check_out = datetime(today.year, today.month, today.day,
                                     random.choice([17, 18]), random.randint(0, 59))
                worked = _worked_hours(check_in, check_out)
                ot = round(max(0.0, worked - 9.0), 1)
                ut = 0.0 if worked >= 8 else round(max(0.0, 8.0 - worked), 1)
            new_rows.append({
                "id": att_id, "employee_id": emp["id"], "client_id": cid,
                "date": today.isoformat(),
                "check_in": check_in.isoformat(),
                "check_out": check_out.isoformat() if check_out else None,
                "status": "late" if late else "on_time",
                "worked_hours": worked, "overtime_hours": ot, "undertime_hours": ut,
            })
            att_id += 1

    attendance.extend(new_rows)
    return new_rows


def build_leaves(data, employees, now):
    leaves = data["db_leaves"]
    leave_id = _next_id(leaves)
    new_leaves = []
    today = now.date()

    # 1-3 leave requests per demo company so every tenant has demo data
    employees_by_client = {}
    for e in employees:
        employees_by_client.setdefault(e["client_id"], []).append(e)
    selected = []
    for emp_rows in employees_by_client.values():
        selected.extend(random.sample(emp_rows, k=min(len(emp_rows), random.randint(1, 3))))

    for emp in selected:
        start_off = random.randint(-20, 30)
        start = today + timedelta(days=start_off)
        end = start + timedelta(days=random.randint(1, 5))
        status = random.choices(["pending", "approved", "rejected"], weights=[3, 5, 2])[0]
        created = now - timedelta(days=max(0, -start_off + random.randint(1, 10)),
                                  hours=random.randint(0, 8))
        new_leaves.append({
            "id": leave_id, "client_id": emp["client_id"], "employee_id": emp["id"],
            "start_date": start.isoformat(), "end_date": end.isoformat(),
            "reason": random.choice(LEAVE_REASONS), "status": status,
            "created_at": created.isoformat(),
        })
        leave_id += 1

    leaves.extend(new_leaves)
    return new_leaves


def build_activity(data, clients, new_employees, now):
    activity = data["db_activity"]
    act_id = _next_id(activity)
    new_entries = []
    employees_by_client = {}
    for e in new_employees:
        employees_by_client.setdefault(e["client_id"], []).append(e)

    for client in clients:
        cid = client["id"]
        emp_rows = employees_by_client.get(cid, [])
        if not emp_rows:
            continue
        for _ in range(random.randint(4, 9)):
            emp = random.choice(emp_rows)
            action = random.choice(ACTIVITY_ACTIONS)
            name = f"{emp['first_name']} {emp['last_name']}"
            detail = {
                "employee_created": f"{name} ({emp['employee_code']})",
                "employee_updated": f"{name} ({emp['employee_code']})",
                "check_in": f"{emp['id']} at {random.randint(8, 9):02d}:{random.randint(10, 59):02d}",
                "check_out": f"{emp['id']} at {random.randint(17, 19):02d}:{random.randint(0, 59):02d}",
                "face_enrolled": f"{name} ({emp['employee_code']})",
                "leave_requested": f"{name} · 2026-{random.randint(1, 12):02d}-{random.randint(1, 28):02d} → 2026-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "leave_approved": f"{name} · leave approved",
            }[action]
            hr_username = next((u["username"] for u in data["db_users"]
                                if u["client_id"] == cid and u["role"] == "HR"), "system")
            new_entries.append({
                "id": act_id, "client_id": cid, "username": hr_username,
                "action": action, "detail": detail,
                "created_at": (now - timedelta(days=random.randint(0, 25),
                                               hours=random.randint(0, 9),
                                               minutes=random.randint(0, 59))).isoformat(),
            })
            act_id += 1

    activity.extend(new_entries)
    return new_entries


def main():
    if not os.path.exists(JSON_DB_PATH):
        print("[SEED ERROR] database.json not found - start the server once so it is created.")
        sys.exit(1)

    now = datetime.now()
    data = load_db()

    demo_clients, _, _ = remove_previous_demo(data)
    if demo_clients:
        print(f"[SEED INFO] Removed {len(demo_clients)} previously seeded demo companies.")

    new_clients = build_companies(data, now)
    # Seed employees into EVERY company (existing real tenants included) so the
    # account you are logged in with also sees populated pages.
    all_clients = [c for c in data["db_clients"] if c.get("status", "active") == "active"]
    new_employees = build_employees(data, all_clients, now)
    build_attendance(data, new_employees, now)
    build_leaves(data, new_employees, now)
    build_activity(data, all_clients, new_employees, now)
    save_db(data)

    print("[SEED DONE] Demo data written to", os.path.basename(JSON_DB_PATH))
    print(f"  companies : +{len(new_clients)}  (total {len(data['db_clients'])})")
    print(f"  employees : +{len(new_employees)} (total {len(data['db_employees'])})")
    print(f"  users     : {len(data['db_users'])} total, demo password: {DEMO_PASSWORD}")
    print(f"  attendance: {len(data['db_attendance'])} records")
    print(f"  leaves    : {len(data['db_leaves'])} records")
    print(f"  activity  : {len(data['db_activity'])} entries")
    print("\nExample demo login (company 1):")
    u = next(u for u in data["db_users"] if str(u["email"]).endswith("@" + DEMO_EMAIL_DOMAIN))
    print(f"  username: {u['username']}   password: {DEMO_PASSWORD}")


if __name__ == "__main__":
    main()
