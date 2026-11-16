from fastapi import APIRouter, HTTPException, Depends, Query, Path, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date, timedelta
import io
from app.auth.crypto import verify_password, hash_password, create_access_token, generate_face_embedding, compare_face_embeddings
from app.auth.dependencies import get_current_user, require_role
from app.database import db_users, db_clients, db_employees, db_attendance, db_leaves, db_activity, db_face_embeddings, save_to_json



router = APIRouter(prefix="/api", tags=["HR & Face AI Management"])

# ==========================================
# PYDANTIC SCHEMAS
# ==========================================
class HRLoginReq(BaseModel):
    username: str
    password: str

class HRRegisterReq(BaseModel):
    username: str
    email: EmailStr
    password: str
    company_name: Optional[str] = None

class EmployeeCreateReq(BaseModel):
    employee_code: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    department: str
    position: str

class CheckInReq(BaseModel):
    employee_id: int
    timestamp: datetime

class ChangePasswordReq(BaseModel):
    current_password: str
    new_password: str

class LeaveCreateReq(BaseModel):
    employee_id: int
    start_date: date
    end_date: date
    reason: str

class LeaveStatusReq(BaseModel):
    status: str

# ==========================================
# 7. HR AUTHENTICATION
# ==========================================
@router.post("/hr/auth/login")
def hr_login(payload: HRLoginReq):
    user = next((u for u in db_users if u["username"] == payload.username), None)
    
    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid HR credentials")
        
    access_token = create_access_token(data={
        "user_id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "client_id": user["client_id"] # Safe multi-tenancy context bound inside the JWT!
    })
    
    return {
        "success": True,
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": _public_user(user)
    }

@router.post("/hr/auth/register")
def hr_register(payload: HRRegisterReq):
    """Creates a new client company workspace with an HR owner account."""
    username = payload.username.strip()
    if len(username) < 3:
        raise HTTPException(status_code=422, detail="Username must be at least 3 characters")
    if len(payload.password) < 6:
        raise HTTPException(status_code=422, detail="Password must be at least 6 characters")

    if any(u["username"].lower() == username.lower() for u in db_users):
        raise HTTPException(status_code=409, detail="Username already taken")
    if any(u["email"].lower() == payload.email.lower() for u in db_users):
        raise HTTPException(status_code=409, detail="Email is already registered")

    # Create a company workspace for the new account
    new_client_id = max((c["id"] for c in db_clients), default=0) + 1
    company_name = payload.company_name.strip() or f"{username}'s Company"
    db_clients.append({
        "id": new_client_id,
        "company_name": company_name,
        "company_code": f"C{new_client_id:03d}",
        "status": "active",
        "created_at": datetime.now().isoformat()
    })

    new_user_id = max((u["id"] for u in db_users), default=0) + 1
    user = {
        "id": new_user_id,
        "client_id": new_client_id,
        "username": username,
        "email": payload.email,
        "hashed_password": hash_password(payload.password),
        "role": "HR",
        "status": "active"
    }
    db_users.append(user)
    save_to_json()

    access_token = create_access_token(data={
        "user_id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "client_id": user["client_id"]
    })

    return {
        "success": True,
        "message": "Account created successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "user": _public_user(user)
    }

class ProfileUpdateReq(BaseModel):
    email: EmailStr

# ----------------------------- Avatar uploads ------------------------------
import os as _os
import shutil as _shutil
import uuid as _uuid
from fastapi import UploadFile, File

AVATAR_DIR = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(__file__))), "uploads", "avatars")
_os.makedirs(AVATAR_DIR, exist_ok=True)
ALLOWED_AVATAR_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_AVATAR_BYTES = 2 * 1024 * 1024  # 2 MB

def _public_user(user):
    """User dict safe to return to the client, including the avatar filename."""
    return {
        "id": user["id"],
        "client_id": user["client_id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "status": user["status"],
        "avatar": user.get("avatar")
    }

@router.post("/hr/auth/profile/avatar")
async def upload_avatar(file: UploadFile = File(...), current_user: dict = Depends(require_role(["HR", "MANAGER", "EXECUTIVE"]))):
    user = next((u for u in db_users if u["id"] == current_user["user_id"]), None)
    if not user:
        raise HTTPException(status_code=404, detail="User account profile missing")
    if file.content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(status_code=415, detail="Only JPEG, PNG, WebP or GIF images are allowed")
    contents = await file.read()
    if len(contents) > MAX_AVATAR_BYTES:
        raise HTTPException(status_code=413, detail="Image must be smaller than 2 MB")

    ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}[file.content_type]
    filename = f"user{user['id']}_{_uuid.uuid4().hex[:8]}{ext}"
    with open(_os.path.join(AVATAR_DIR, filename), "wb") as fh:
        fh.write(contents)

    # Remove the previous avatar file so uploads don't pile up
    old = user.get("avatar")
    if old:
        old_path = _os.path.join(AVATAR_DIR, _os.path.basename(old))
        if _os.path.exists(old_path):
            _os.remove(old_path)

    user["avatar"] = filename
    save_to_json()
    return {"success": True, "message": "Avatar updated", "user": _public_user(user)}

@router.delete("/hr/auth/profile/avatar")
def remove_avatar(current_user: dict = Depends(require_role(["HR", "MANAGER", "EXECUTIVE"]))):
    user = next((u for u in db_users if u["id"] == current_user["user_id"]), None)
    if not user:
        raise HTTPException(status_code=404, detail="User account profile missing")
    old = user.get("avatar")
    if old:
        old_path = _os.path.join(AVATAR_DIR, _os.path.basename(old))
        if _os.path.exists(old_path):
            _os.remove(old_path)
        user.pop("avatar", None)
        save_to_json()
    return {"success": True, "message": "Avatar removed", "user": _public_user(user)}

@router.get("/hr/auth/profile")
def get_profile(current_user: dict = Depends(require_role(["HR", "MANAGER", "EXECUTIVE"]))):
    """Extended profile: account info + company details + tenant statistics."""
    user = next((u for u in db_users if u["id"] == current_user["user_id"]), None)
    if not user:
        raise HTTPException(status_code=404, detail="User account profile missing")
    tenant_id = user["client_id"]
    client = next((c for c in db_clients if c["id"] == tenant_id), None)
    employees = [e for e in db_employees if e["client_id"] == tenant_id]
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "status": user["status"],
        "avatar": user.get("avatar"),
        "client_id": tenant_id,
        "company": {
            "name": client["company_name"],
            "code": client["company_code"],
            "created_at": client.get("created_at")
        } if client else None,
        "stats": {
            "employees": len(employees),
            "departments": len({e["department"] for e in employees}),
            "attendance_records": sum(1 for a in db_attendance if a["client_id"] == tenant_id),
            "pending_leaves": sum(1 for l in db_leaves if l["client_id"] == tenant_id and l["status"] == "pending")
        }
    }

@router.put("/hr/auth/profile")
def update_profile(payload: ProfileUpdateReq, current_user: dict = Depends(require_role(["HR", "MANAGER", "EXECUTIVE"]))):
    """Update the account email (uniqueness checked across all users)."""
    user = next((u for u in db_users if u["id"] == current_user["user_id"]), None)
    if not user:
        raise HTTPException(status_code=404, detail="User account profile missing")
    new_email = payload.email.strip().lower()
    if any(u["email"].lower() == new_email and u["id"] != user["id"] for u in db_users):
        raise HTTPException(status_code=409, detail="Email already in use")
    user["email"] = payload.email.strip()
    save_to_json()
    return {
        "success": True,
        "message": "Profile updated",
        "user": _public_user(user)
    }

@router.post("/hr/auth/change-password")
def hr_change_password(payload: ChangePasswordReq, current_user: dict = Depends(get_current_user)):
    user = next((u for u in db_users if u["id"] == current_user["user_id"]), None)
    if not user:
        raise HTTPException(status_code=404, detail="User account profile missing")
    if not verify_password(payload.current_password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if len(payload.new_password) < 6:
        raise HTTPException(status_code=422, detail="New password must be at least 6 characters")
    user["hashed_password"] = hash_password(payload.new_password)
    save_to_json()
    return {"success": True, "message": "Password updated successfully"}

@router.post("/hr/auth/logout")
def hr_logout(current_user: dict = Depends(get_current_user)):
    return {"success": True, "message": "Logout successful"}

@router.get("/hr/auth/me")
def hr_me(current_user: dict = Depends(require_role(["HR", "MANAGER", "EXECUTIVE"]))):
    user = next((u for u in db_users if u["id"] == current_user["user_id"]), None)
    if not user:
        raise HTTPException(status_code=404, detail="User account profile missing")
    return _public_user(user)

# ==========================================
# 8. EMPLOYEES (Scoped by client_id)
# ==========================================
def _log_activity(current_user: dict, action: str, detail: str):
    """Append an entry to the tenant-scoped audit trail (kept to the last 200 per tenant)."""
    db_activity.append({
        "id": max((a["id"] for a in db_activity), default=9000) + 1,
        "client_id": current_user["client_id"],
        "username": current_user.get("username", "system"),
        "action": action,
        "detail": detail,
        "created_at": datetime.now().isoformat()
    })
    tenant = current_user["client_id"]
    tenant_logs = [a for a in db_activity if a["client_id"] == tenant]
    if len(tenant_logs) > 200:
        cutoff = tenant_logs[0]["id"]
        db_activity[:] = [a for a in db_activity if a["id"] > cutoff]

@router.get("/hr/activity")
def get_activity(current_user: dict = Depends(require_role(["HR", "MANAGER", "EXECUTIVE"]))):
    tenant_id = current_user["client_id"]
    scoped = [a for a in db_activity if a["client_id"] == tenant_id]
    scoped.sort(key=lambda a: a["created_at"], reverse=True)
    return {"activity": scoped[:50], "total": len(scoped)}

@router.get("/hr/employees")
def get_employees(current_user: dict = Depends(require_role(["HR", "MANAGER", "EXECUTIVE"]))):
    tenant_id = current_user["client_id"]
    scoped_employees = [e for e in db_employees if e["client_id"] == tenant_id]
    return {"employees": scoped_employees, "total": len(scoped_employees)}

@router.post("/hr/employees")
def create_employee(payload: EmployeeCreateReq, current_user: dict = Depends(require_role(["HR", "MANAGER"]))):
    tenant_id = current_user["client_id"]
    new_id = max((e["id"] for e in db_employees), default=100) + 1
    new_emp = {
        "id": new_id,
        "client_id": tenant_id, # Bound to current tenant automatically
        "employee_code": payload.employee_code,
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "email": payload.email,
        "phone": payload.phone,
        "department": payload.department,
        "position": payload.position,
        "status": "active",
        "face_registered": False,
        "created_at": datetime.now().isoformat()
    }
    db_employees.append(new_emp)
    _log_activity(current_user, "employee_created", f"{payload.first_name} {payload.last_name} ({payload.employee_code})")
    save_to_json()
    return {"success": True, "employee": new_emp}

@router.get("/hr/employees/{employee_id}")
def get_employee(employee_id: int, current_user: dict = Depends(require_role(["HR", "MANAGER", "EXECUTIVE"]))):
    tenant_id = current_user["client_id"]
    emp = next((e for e in db_employees if e["id"] == employee_id and e["client_id"] == tenant_id), None)
    if not emp: 
        raise HTTPException(status_code=404, detail="Employee profile not found in your company")
    return emp

@router.put("/hr/employees/{employee_id}")
def update_employee(employee_id: int, payload: EmployeeCreateReq, current_user: dict = Depends(require_role(["HR", "MANAGER"]))):
    tenant_id = current_user["client_id"]
    emp = next((e for e in db_employees if e["id"] == employee_id and e["client_id"] == tenant_id), None)
    if not emp: 
        raise HTTPException(status_code=404, detail="Employee profile not found in your company")
    
    emp |= payload.model_dump()
    _log_activity(current_user, "employee_updated", f"{payload.first_name} {payload.last_name} ({payload.employee_code})")
    save_to_json()
    return {"success": True, "employee": emp}

@router.delete("/hr/employees/{employee_id}")
def delete_employee(employee_id: int, current_user: dict = Depends(require_role(["HR"]))):
    global db_employees
    tenant_id = current_user["client_id"]
    emp = next((e for e in db_employees if e["id"] == employee_id and e["client_id"] == tenant_id), None)
    if not emp: 
        raise HTTPException(status_code=404, detail="Employee profile not found in your company")
        
    db_employees.remove(emp)
    _log_activity(current_user, "employee_deleted", f"{emp['first_name']} {emp['last_name']} ({emp['employee_code']})")
    save_to_json()
    return {"success": True, "message": "Employee profile deleted permanently"}

# ==========================================
# TENANT DATA HELPERS (used by attendance, dashboard, alerts and reports)
# ==========================================
def _fmt_time(iso_str):
    """Format an ISO datetime string as HH:MM (or None)."""
    if not iso_str:
        return None
    try:
        return datetime.fromisoformat(iso_str).strftime("%H:%M")
    except (ValueError, TypeError):
        return iso_str

def _emp_name(employee_id):
    emp = next((e for e in db_employees if e["id"] == employee_id), None)
    return f"{emp['first_name']} {emp['last_name']}" if emp else "Unknown"

def _tenant_employees(tenant_id):
    return [e for e in db_employees if e["client_id"] == tenant_id]

def _tenant_attendance(tenant_id, start_date=None, end_date=None, employee_id=None):
    rows = [a for a in db_attendance if a["client_id"] == tenant_id]
    if start_date:
        rows = [a for a in rows if a["date"] >= start_date.isoformat()]
    if end_date:
        rows = [a for a in rows if a["date"] <= end_date.isoformat()]
    if employee_id:
        rows = [a for a in rows if a["employee_id"] == employee_id]
    rows.sort(key=lambda a: (a["date"], a["id"]))
    return rows

def _work_hours_totals(tenant_id):
    """Aggregate worked/overtime/undertime hours per employee for a tenant."""
    totals = {}
    for a in _tenant_attendance(tenant_id):
        t = totals.setdefault(a["employee_id"], {"worked": 0.0, "ot": 0.0, "ut": 0.0})
        t["worked"] += a.get("worked_hours") or 0
        t["ot"] += a.get("overtime_hours") or 0
        t["ut"] += a.get("undertime_hours") or 0
    return totals

def _reference_date(tenant_id):
    """Today when records exist, otherwise the most recent recorded date (demo-friendly)."""
    today = date.today().isoformat()
    dates = {a["date"] for a in db_attendance if a["client_id"] == tenant_id}
    return today if today in dates else max(dates, default=today)

def _dashboard_counts(tenant_id, ref_date):
    """Presence/status counts for the given reference day."""
    employees = _tenant_employees(tenant_id)
    rows = [a for a in _tenant_attendance(tenant_id) if a["date"] == ref_date]
    late = sum(1 for a in rows if a.get("status") == "late")
    return {
        "total_employees": len(employees),
        "present": len(rows),
        "absent": max(0, len(employees) - len(rows)),
        "late": late,
        "on_time": len(rows) - late,
        "overtime": sum(1 for a in rows if (a.get("overtime_hours") or 0) > 0),
        "undertime": sum(1 for a in rows if (a.get("undertime_hours") or 0) > 0),
    }

# ==========================================
# 9. ATTENDANCE (Scoped by client_id)
# ==========================================
@router.post("/hr/attendance/check-in")
def check_in(payload: CheckInReq, current_user: dict = Depends(get_current_user)):
    tenant_id = current_user["client_id"]
    
    new_record = {
        "id": max((a["id"] for a in db_attendance), default=1000) + 1,
        "employee_id": payload.employee_id,
        "client_id": tenant_id,
        "date": payload.timestamp.date().isoformat(),
        "check_in": payload.timestamp.isoformat(),
        "check_out": None,
        "status": "on_time",
        "worked_hours": 0,
        "overtime_hours": 0,
        "undertime_hours": 0
    }
    db_attendance.append(new_record)
    _log_activity(current_user, "check_in", f"{payload.employee_id} at {payload.timestamp.strftime('%H:%M')}")
    return {"success": True, "attendance": new_record}

@router.post("/hr/attendance/check-out")
def check_out(payload: CheckInReq, current_user: dict = Depends(get_current_user)):
    tenant_id = current_user["client_id"]
    record = next((a for a in db_attendance if a["employee_id"] == payload.employee_id and a["check_out"] is None and a["client_id"] == tenant_id), None)

    if not record:
        # No open check-in: create a same-day record anchored at the check-out time
        # so the worked-hours math below stays honest.
        record = {
            "id": max((a["id"] for a in db_attendance), default=1000) + 1,
            "employee_id": payload.employee_id,
            "client_id": tenant_id,
            "date": payload.timestamp.date().isoformat(),
            "check_in": payload.timestamp.isoformat(),
            "status": "on_time",
            "worked_hours": 0,
            "overtime_hours": 0,
            "undertime_hours": 0
        }
        db_attendance.append(record)

    check_in_dt = datetime.fromisoformat(record["check_in"])
    gross = (payload.timestamp - check_in_dt).total_seconds() / 3600.0
    worked = round(max(0.0, gross - 0.5), 1)  # 30 min break, same rule as the demo seed

    record["check_out"] = payload.timestamp.isoformat()
    record["worked_hours"] = worked
    record["overtime_hours"] = round(max(0.0, worked - 9.0), 1)
    record["undertime_hours"] = 0.0 if worked >= 8 else round(max(0.0, 8.0 - worked), 1)
    _log_activity(current_user, "check_out", f"{payload.employee_id} at {payload.timestamp.strftime('%H:%M')}")
    return {"success": True, "attendance": record}

@router.get("/hr/attendance")
def get_attendance(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    employee_id: Optional[int] = Query(None),
    current_user: dict = Depends(require_role(["HR", "MANAGER", "EXECUTIVE"]))
):
    tenant_id = current_user["client_id"]
    scoped_attendance = _tenant_attendance(tenant_id, start_date, end_date, employee_id)

    formatted = []
    for att in scoped_attendance:
        formatted.append({
            "id": att["id"],
            "employee_id": att["employee_id"],
            "employee_name": _emp_name(att["employee_id"]),
            "date": att["date"],
            "check_in": _fmt_time(att.get("check_in")),
            "check_out": _fmt_time(att.get("check_out")),
            "status": att["status"],
            "worked_hours": att["worked_hours"],
            "overtime_hours": att["overtime_hours"],
            "undertime_hours": att["undertime_hours"]
        })
    return {"attendance": formatted, "total": len(formatted)}

# ==========================================
# 10. WORK HOURS & 11. DASHBOARD REVENUE
# ==========================================
@router.get("/hr/work-hours")
def get_work_hours(current_user: dict = Depends(require_role(["HR", "MANAGER", "EXECUTIVE"]))):
    tenant_id = current_user["client_id"]
    totals = _work_hours_totals(tenant_id)
    work_hours = [
        {
            "employee_id": emp_id,
            "employee_name": _emp_name(emp_id),
            "total_worked_hours": round(t["worked"], 1),
            "total_overtime_hours": round(t["ot"], 1),
            "total_undertime_hours": round(t["ut"], 1)
        }
        for emp_id, t in totals.items()
    ]
    work_hours.sort(key=lambda w: w["total_worked_hours"], reverse=True)
    return {"work_hours": work_hours}

@router.get("/hr/dashboard/summary")
def get_dashboard_summary(current_user: dict = Depends(require_role(["HR", "MANAGER", "EXECUTIVE"]))):
    tenant_id = current_user["client_id"]
    return _dashboard_counts(tenant_id, _reference_date(tenant_id))

@router.get("/hr/dashboard/today")
def get_dashboard_today(current_user: dict = Depends(require_role(["HR", "MANAGER", "EXECUTIVE"]))):
    tenant_id = current_user["client_id"]
    ref = _reference_date(tenant_id)
    counts = _dashboard_counts(tenant_id, ref)
    return {
        "date": ref,
        "total_employees": counts["total_employees"],
        "checked_in": counts["present"],
        "not_checked_in": counts["absent"],
        "late": counts["late"],
        "on_time": counts["on_time"]
    }

@router.get("/hr/dashboard/analytics")
def get_dashboard_analytics(current_user: dict = Depends(require_role(["HR", "MANAGER", "EXECUTIVE"]))):
    tenant_id = current_user["client_id"]
    total_employees = len(_tenant_employees(tenant_id))
    dates = sorted({a["date"] for a in _tenant_attendance(tenant_id)})[-7:]
    attendance_trend = []
    for day in dates:
        rows = [a for a in _tenant_attendance(tenant_id) if a["date"] == day]
        present = len(rows)
        late = sum(1 for a in rows if a.get("status") == "late")
        attendance_trend.append({
            "date": day,
            "present": present,
            "late": late,
            "absent": max(0, total_employees - present)
        })
    return {"attendance_trend": attendance_trend}

# ==========================================
# 12. ALERTS (computed from real attendance data)
# ==========================================
def _tenant_alerts(tenant_id, alert_type):
    """Build alert objects from the tenant's last-30-days attendance records."""
    cutoff = (datetime.now() - timedelta(days=30)).date().isoformat()
    rows = [a for a in _tenant_attendance(tenant_id) if a["date"] >= cutoff]

    if alert_type == "overtime":
        rows = [a for a in rows if (a.get("overtime_hours") or 0) > 0]
        message = lambda a: f"{_emp_name(a['employee_id'])} worked {a['overtime_hours']}h overtime"
    elif alert_type == "late":
        rows = [a for a in rows if a.get("status") == "late"]
        message = lambda a: f"{_emp_name(a['employee_id'])} arrived late on {a['date']}"
    else:  # under_time
        rows = [a for a in rows if (a.get("undertime_hours") or 0) > 0]
        message = lambda a: f"{_emp_name(a['employee_id'])} was {a['undertime_hours']}h short on {a['date']}"

    alerts = [
        {
            "id": a["id"],
            # Globally unique alert key: one attendance row can raise several alert types.
            "key": f"{alert_type}:{a['id']}",
            "employee_id": a["employee_id"],
            "employee_name": _emp_name(a["employee_id"]),
            "type": alert_type,
            "message": message(a),
            "date": a["date"],
            "value": a.get("overtime_hours") if alert_type == "overtime"
                     else a.get("undertime_hours") if alert_type == "under_time"
                     else 0,
            "status": "active"
        }
        for a in rows
    ]
    alerts.sort(key=lambda x: x["date"], reverse=True)
    return alerts

class MarkAlertsReadReq(BaseModel):
    keys: list[str] = []
    all: bool = False

def _user_row(current_user: dict):
    return next((u for u in db_users if u["id"] == current_user["user_id"]), None)

def _read_alert_keys(user) -> set:
    return set((user or {}).get("read_alerts") or [])

def _decorate_alerts(alerts, user):
    """Attach the per-user `read` flag and return (alerts, unread_count)."""
    read_keys = _read_alert_keys(user)
    for alert in alerts:
        alert["read"] = alert["key"] in read_keys
    return alerts, sum(1 for a in alerts if not a["read"])

def _store_read_keys(user, keys):
    # Keep the list bounded: only remember keys that still exist as alerts.
    user["read_alerts"] = sorted(set(keys))
    save_to_json()

@router.get("/hr/alerts")
def get_alerts(current_user: dict = Depends(require_role(["HR", "MANAGER"]))):
    tenant_id = current_user["client_id"]
    alerts = (_tenant_alerts(tenant_id, "overtime")
              + _tenant_alerts(tenant_id, "late")
              + _tenant_alerts(tenant_id, "under_time"))
    alerts.sort(key=lambda x: x["date"], reverse=True)

    user = _user_row(current_user)
    alerts, unread = _decorate_alerts(alerts, user)
    return {"alerts": alerts, "total": len(alerts), "unread": unread}

@router.post("/hr/alerts/read")
def mark_alerts_read(payload: MarkAlertsReadReq, current_user: dict = Depends(require_role(["HR", "MANAGER"]))):
    """Mark alerts as read for the signed-in user (persisted per account)."""
    tenant_id = current_user["client_id"]
    user = _user_row(current_user)
    if not user:
        raise HTTPException(status_code=404, detail="User account profile missing")

    live = (_tenant_alerts(tenant_id, "overtime")
            + _tenant_alerts(tenant_id, "late")
            + _tenant_alerts(tenant_id, "under_time"))
    live_keys = {a["key"] for a in live}

    if payload.all:
        keys = live_keys
    else:
        keys = {k for k in payload.keys if k in live_keys}
    _store_read_keys(user, _read_alert_keys(user) | keys)

    alerts, unread = _decorate_alerts(live, user)
    return {"success": True, "total": len(alerts), "unread": unread, "read": len(alerts) - unread}

@router.get("/hr/alerts/overtime")
def get_overtime_alerts(current_user: dict = Depends(require_role(["HR", "MANAGER"]))):
    alerts, unread = _decorate_alerts(
        _tenant_alerts(current_user["client_id"], "overtime"), _user_row(current_user)
    )
    return {"alerts": alerts, "total": len(alerts), "unread": unread}

@router.get("/hr/alerts/under-time")
def get_undertime_alerts(current_user: dict = Depends(require_role(["HR", "MANAGER"]))):
    alerts, unread = _decorate_alerts(
        _tenant_alerts(current_user["client_id"], "under_time"), _user_row(current_user)
    )
    return {"alerts": alerts, "total": len(alerts), "unread": unread}

@router.get("/hr/alerts/late")
def get_late_alerts(current_user: dict = Depends(require_role(["HR", "MANAGER"]))):
    alerts, unread = _decorate_alerts(
        _tenant_alerts(current_user["client_id"], "late"), _user_row(current_user)
    )
    return {"alerts": alerts, "total": len(alerts), "unread": unread}


# ==========================================
# 13. FACE AI (Active Processing Engine)
# ==========================================
@router.post("/face/register")
async def face_register(
    employee_id: int = Query(...), 
    image: UploadFile = File(...), 
    current_user: dict = Depends(get_current_user)
):
    """
    Purpose: Extracts and registers an employee's face embedding vector.
    """
    tenant_id = current_user["client_id"]
    
    # Verify the employee belongs to this tenant company before letting them register a face
    emp = next((e for e in db_employees if e["id"] == employee_id and e["client_id"] == tenant_id), None)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee profile not found in your company")
        
    # Read the raw binary photo frame uploaded by Orgil N's app
    image_bytes = await image.read()
    
    # Pass it to our new AI engine to get the mathematical array
    embedding = generate_face_embedding(image_bytes)
    if not embedding:
        raise HTTPException(status_code=400, detail="No clear face detected in the image. Please try again.")
        
    # Store the 128 numbers securely inside our database module linked to their profile
    db_face_embeddings[str(employee_id)] = embedding
    emp["face_registered"] = True  # Toggle status flag update
    _log_activity(current_user, "face_enrolled", f"{emp['first_name']} {emp['last_name']} ({emp['employee_code']})")
    save_to_json()

    return {
        "success": True, 
        "employee_id": employee_id, 
        "face_registered": True, 
        "message": "Face embedding vector extracted and registered successfully"
    }

@router.post("/face/verify")
async def face_verify(
    image: UploadFile = File(...), 
    current_user: dict = Depends(get_current_user)
):
    """
    Purpose: Identifies an employee from a live camera capture frame.
    """
    tenant_id = current_user["client_id"]
    image_bytes = await image.read()
    
    # Convert live webcam image to a temporary 128-dimension vector
    live_embedding = generate_face_embedding(image_bytes)
    if not live_embedding:
        raise HTTPException(status_code=400, detail="No clear face detected in the camera frame.")
        
    # Search through all registered face vectors belonging to this company's employees
    for emp_id_str, stored_embedding in db_face_embeddings.items():
        emp_id = int(emp_id_str)
        # Double check tenant safety configuration boundaries
        emp = next((e for e in db_employees if e["id"] == emp_id and e["client_id"] == tenant_id), None)
        if not emp:
            continue
            
        # Mathematically check if the live face coordinates match the stored database entry
        matched, confidence = compare_face_embeddings(stored_embedding, live_embedding)
        if matched:
            return {
                "success": True,
                "matched": True,
                "employee_id": emp["id"],
                "employee_name": f"{emp['first_name']} {emp['last_name']}",
                "confidence": confidence
            }
            
    # If the loop finishes without finding a mathematical match close enough
    return {
        "success": True,
        "matched": False,
        "employee_id": None,
        "employee_name": None,
        "confidence": 0.0
    }


# ==========================================
# 14. LEAVE REQUESTS
# ==========================================
def _leave_out(leave):
    emp = next((e for e in db_employees if e["id"] == leave["employee_id"]), None)
    return {
        **leave,
        "employee_name": f"{emp['first_name']} {emp['last_name']}" if emp else "Unknown",
        "employee_code": emp["employee_code"] if emp else None,
        "department": emp["department"] if emp else None
    }

@router.get("/hr/leaves")
def get_leaves(current_user: dict = Depends(require_role(["HR", "MANAGER", "EXECUTIVE"]))):
    tenant_id = current_user["client_id"]
    scoped = [l for l in db_leaves if l["client_id"] == tenant_id]
    scoped.sort(key=lambda l: l.get("created_at") or "", reverse=True)
    return {"leaves": [_leave_out(l) for l in scoped], "total": len(scoped)}

@router.post("/hr/leaves")
def create_leave(payload: LeaveCreateReq, current_user: dict = Depends(require_role(["HR", "MANAGER", "EXECUTIVE"]))):
    tenant_id = current_user["client_id"]
    emp = next((e for e in db_employees if e["id"] == payload.employee_id and e["client_id"] == tenant_id), None)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee profile not found in your company")
    if payload.end_date < payload.start_date:
        raise HTTPException(status_code=422, detail="End date cannot be before start date")

    leave = {
        "id": max((l["id"] for l in db_leaves), default=5000) + 1,
        "client_id": tenant_id,
        "employee_id": payload.employee_id,
        "start_date": payload.start_date.isoformat(),
        "end_date": payload.end_date.isoformat(),
        "reason": payload.reason.strip(),
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    db_leaves.append(leave)
    _log_activity(current_user, "leave_requested", f"{_leave_out(leave)['employee_name']} · {payload.start_date} → {payload.end_date}")
    save_to_json()
    return {"success": True, "leave": _leave_out(leave)}

@router.post("/hr/leaves/{leave_id}/status")
def set_leave_status(leave_id: int, payload: LeaveStatusReq, current_user: dict = Depends(require_role(["HR", "MANAGER"]))):
    tenant_id = current_user["client_id"]
    leave = next((l for l in db_leaves if l["id"] == leave_id and l["client_id"] == tenant_id), None)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    status = payload.status.lower()
    if status not in ("approved", "rejected", "pending"):
        raise HTTPException(status_code=422, detail="Status must be approved, rejected or pending")
    leave["status"] = status
    _log_activity(current_user, f"leave_{status}", f"{_leave_out(leave)['employee_name']} · {leave['start_date']} → {leave['end_date']}")
    save_to_json()
    return {"success": True, "leave": _leave_out(leave)}


# ==========================================
# 15. REPORTS (built from real tenant data)
# ==========================================
@router.get("/hr/reports/attendance")
def report_attendance(current_user: dict = Depends(require_role(["HR", "MANAGER"]))):
    tenant_id = current_user["client_id"]
    data = [
        {
            "id": a["id"],
            "employee_id": a["employee_id"],
            "employee_name": _emp_name(a["employee_id"]),
            "date": a["date"],
            "check_in": _fmt_time(a.get("check_in")),
            "check_out": _fmt_time(a.get("check_out")),
            "status": a["status"]
        }
        for a in _tenant_attendance(tenant_id)
    ]
    return {"report_type": "attendance", "data": data}

@router.get("/hr/reports/work-hours")
def report_work_hours(current_user: dict = Depends(require_role(["HR", "MANAGER"]))):
    tenant_id = current_user["client_id"]
    totals = _work_hours_totals(tenant_id)
    data = [
        {
            "employee_id": emp_id,
            "employee_name": _emp_name(emp_id),
            "total_worked_hours": round(t["worked"], 1),
            "total_overtime_hours": round(t["ot"], 1),
            "total_undertime_hours": round(t["ut"], 1)
        }
        for emp_id, t in sorted(totals.items(), key=lambda kv: -kv[1]["worked"])
    ]
    return {"report_type": "work-hours", "data": data}

@router.get("/hr/reports/export")
def report_export(
    report_type: str = Query(...), 
    format: str = Query(...), 
    current_user: dict = Depends(require_role(["HR", "MANAGER"]))
):
    tenant_id = current_user["client_id"]
    output = io.StringIO()
    if report_type == "work-hours":
        output.write("employee_id,employee_name,total_worked_hours,total_overtime_hours,total_undertime_hours\n")
        result = report_work_hours(current_user)
        for row in result["data"]:
            output.write(f"{row['employee_id']},{row['employee_name']},{row['total_worked_hours']},{row['total_overtime_hours']},{row['total_undertime_hours']}\n")
    else:
        output.write("id,employee_id,employee_name,date,check_in,check_out,status\n")
        result = report_attendance(current_user)
        for row in result["data"]:
            output.write(f"{row['id']},{row['employee_id']},{row['employee_name']},{row['date']},{row['check_in'] or ''},{row['check_out'] or ''},{row['status']}\n")
    
    media_type = "text/csv" if format == "csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    response = StreamingResponse(io.BytesIO(output.getvalue().encode()), media_type=media_type)
    response.headers["Content-Disposition"] = f"attachment; filename=report_{report_type}.{format}"
    return response
