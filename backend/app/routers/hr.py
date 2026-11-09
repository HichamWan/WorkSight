from fastapi import APIRouter, HTTPException, Depends, Query, Path, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date
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
        "user": {
            "id": user["id"],
            "client_id": user["client_id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "status": user["status"]
        }
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
        "user": {
            "id": user["id"],
            "client_id": user["client_id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "status": user["status"]
        }
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
    return {
        "id": user["id"],
        "client_id": user["client_id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "status": user["status"]
    }

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
    new_id = len(db_employees) + 101
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
# 9. ATTENDANCE (Scoped by client_id)
# ==========================================
@router.post("/hr/attendance/check-in")
def check_in(payload: CheckInReq, current_user: dict = Depends(get_current_user)):
    tenant_id = current_user["client_id"]
    
    new_record = {
        "id": len(db_attendance) + 1001,
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
        record = {
            "id": 1001,
            "employee_id": payload.employee_id,
            "client_id": tenant_id,
            "date": payload.timestamp.date().isoformat(),
            "check_in": "2026-09-17T08:52:00"
        }
        db_attendance.append(record)
    
    record["check_out"] = payload.timestamp.isoformat()
    record["worked_hours"] = 9.3
    record["overtime_hours"] = 1.3
    record["undertime_hours"] = 0
    return {"success": True, "attendance": record}

@router.get("/hr/attendance")
def get_attendance(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    employee_id: Optional[int] = Query(None),
    current_user: dict = Depends(require_role(["HR", "MANAGER", "EXECUTIVE"]))
):
    tenant_id = current_user["client_id"]
    scoped_attendance = [a for a in db_attendance if a["client_id"] == tenant_id]
    
    formatted = []
    for att in scoped_attendance:
        emp = next((e for e in db_employees if e["id"] == att["employee_id"]), {"first_name": "John", "last_name": "Smith"})
        formatted.append({
            "id": att["id"],
            "employee_id": att["employee_id"],
            "employee_name": f"{emp['first_name']} {emp['last_name']}",
            "date": att["date"],
            "check_in": "08:52",
            "check_out": "18:10",
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
    return {
        "work_hours": [
            {"employee_id": 101, "employee_name": "John Smith", "total_worked_hours": 168.5, "total_overtime_hours": 8.5, "total_undertime_hours": 2.0}
        ]
    }

@router.get("/hr/dashboard/summary")
def get_dashboard_summary(current_user: dict = Depends(require_role(["HR", "MANAGER", "EXECUTIVE"]))):
    return {"total_employees": 50, "present": 42, "absent": 8, "late": 5, "on_time": 37, "overtime": 6, "undertime": 3}

@router.get("/hr/dashboard/today")
def get_dashboard_today(current_user: dict = Depends(require_role(["HR", "MANAGER", "EXECUTIVE"]))):
    return {"date": "2026-09-17", "total_employees": 50, "checked_in": 42, "not_checked_in": 8, "late": 5, "on_time": 37}

@router.get("/hr/dashboard/analytics")
def get_dashboard_analytics(current_user: dict = Depends(require_role(["HR", "MANAGER", "EXECUTIVE"]))):
    return {
        "attendance_trend": [
            {"date": "2026-09-15", "present": 45, "late": 3, "absent": 5},
            {"date": "2026-09-16", "present": 44, "late": 4, "absent": 6},
            {"date": "2026-09-17", "present": 42, "late": 5, "absent": 8}
        ]
    }

# ==========================================
# 12. ALERTS
# ==========================================
@router.get("/hr/alerts")
def get_alerts(current_user: dict = Depends(require_role(["HR", "MANAGER"]))):
    return {
        "alerts": [
            {
                "id": 1, 
                "employee_id": 101, 
                "employee_name": "John Smith", 
                "type": "overtime", 
                "message": "Employee worked overtime", 
                "date": "2026-09-17", 
                "value": 2.5, 
                "status": "active"
            }
        ],
        "total": 1
    }

@router.get("/hr/alerts/overtime")
def get_overtime_alerts(current_user: dict = Depends(require_role(["HR", "MANAGER"]))):
    return [
        {
            "id": 1,
            "employee_id": 101,
            "employee_name": "John Smith",
            "type": "overtime",
            "message": "Employee worked overtime",
            "date": "2026-09-17",
            "value": 2.5,
            "status": "active"
        }
    ]

@router.get("/hr/alerts/under-time")
def get_undertime_alerts(current_user: dict = Depends(require_role(["HR", "MANAGER"]))):
    return {"alerts": [], "total": 0}

@router.get("/hr/alerts/late")
def get_late_alerts(current_user: dict = Depends(require_role(["HR", "MANAGER"]))):
    return {"alerts": [], "total": 0}


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
# 15. REPORTS
# ==========================================
@router.get("/hr/reports/attendance")
def report_attendance(current_user: dict = Depends(require_role(["HR", "MANAGER"]))):
    return {
        "report_type": "attendance",
        "data": [
            {
                "id": 1001,
                "employee_id": 101,
                "employee_name": "John Smith",
                "date": "2026-09-17",
                "check_in": "08:52",
                "check_out": "18:10",
                "status": "on_time"
            }
        ]
    }

@router.get("/hr/reports/work-hours")
def report_work_hours(current_user: dict = Depends(require_role(["HR", "MANAGER"]))):
    return {
        "report_type": "work-hours",
        "data": [
            {
                "employee_id": 101,
                "employee_name": "John Smith",
                "total_worked_hours": 168.5
            }
        ]
    }

@router.get("/hr/reports/export")
def report_export(
    report_type: str = Query(...), 
    format: str = Query(...), 
    current_user: dict = Depends(require_role(["HR", "MANAGER"]))
):
    output = io.StringIO()
    output.write("id,employee_id,date,status\n1001,101,2026-09-17,on_time\n")
    
    media_type = "text/csv" if format == "csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    response = StreamingResponse(io.BytesIO(output.getvalue().encode()), media_type=media_type)
    response.headers["Content-Disposition"] = f"attachment; filename=report_{report_type}.{format}"
    return response
