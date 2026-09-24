from fastapi import FastAPI, HTTPException, Path, Query, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, date
import io

# Initialize FastAPI with the required /api base prefix routing rule
app = FastAPI(title="WorkSight API", version="1.0.0", docs_url="/api/docs", openapi_url="/api/openapi.json")

# ==========================================
# MOCK DATABASE STATE (For runtime testing)
# ==========================================
db_clients = [
    {"id": 1, "company_name": "ABC Technology", "company_code": "ABC001", "status": "active", "created_at": "2026-09-01T10:00:00"},
    {"id": 2, "company_name": "XYZ Company", "company_code": "XYZ001", "status": "active", "created_at": "2026-09-05T10:00:00"}
]
db_users = [
    {"id": 10, "client_id": 1, "username": "alice", "email": "alice@abc.com", "role": "HR", "status": "active"}
]
db_employees = [
    {
        "id": 101, "client_id": 1, "employee_code": "EMP001", "first_name": "John", "last_name": "Smith",
        "email": "john@abc.com", "phone": "123456789", "department": "IT", "position": "Software Engineer",
        "status": "active", "face_registered": True, "created_at": "2026-09-01T09:00:00"
    }
]
db_attendance = [
    {
        "id": 1001, "employee_id": 101, "date": "2026-09-17", "check_in": "2026-09-17T08:52:00", 
        "check_out": "2026-09-17T18:10:00", "status": "on_time", "worked_hours": 9.3, "overtime_hours": 1.3, "undertime_hours": 0
    }
]

# ==========================================
# PYDANTIC SCHEMAS (Request/Response Models)
# ==========================================
class AdminLoginReq(BaseModel):
    username: str
    password: str

class ClientCreateReq(BaseModel):
    company_name: str
    company_code: str

class ClientUpdateReq(BaseModel):
    company_name: str
    company_code: str
    status: str

class ClientUserCreateReq(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str # HR, MANAGER, EXECUTIVE

class ClientUserUpdateReq(BaseModel):
    username: str
    email: EmailStr
    role: str
    status: str

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

# ==========================================
# 4. ADMIN AUTHENTICATION
# ==========================================
@app.post("/api/admin/auth/login")
def admin_login(payload: AdminLoginReq):
    if payload.username == "admin" and payload.password == "password":
        return {
            "success": True, "message": "Login successful", "access_token": "mock-admin-token", "token_type": "bearer",
            "admin": {"id": 1, "username": "admin", "email": "admin@worksight.com", "role": "ADMIN", "status": "active"}
        }
    raise HTTPException(status_code=401, detail="Invalid admin credentials")

@app.post("/api/admin/auth/logout")
def admin_logout():
    return {"success": True, "message": "Logout successful"}

@app.get("/api/admin/auth/me")
def admin_me():
    return {"id": 1, "username": "admin", "email": "admin@worksight.com", "role": "ADMIN", "status": "active"}


# ==========================================
# 5. CLIENT / COMPANY MANAGEMENT
# ==========================================
@app.get("/api/admin/clients")
def get_clients():
    return {"clients": db_clients, "total": len(db_clients)}

@app.post("/api/admin/clients")
def create_client(payload: ClientCreateReq):
    new_id = len(db_clients) + 1
    new_client = {
        "id": new_id, "company_name": payload.company_name, "company_code": payload.company_code,
        "status": "active", "created_at": datetime.now().isoformat()
    }
    db_clients.append(new_client)
    return {"success": True, "client": new_client}

@app.get("/api/admin/clients/{client_id}")
def get_client(client_id: int):
    client = next((c for c in db_clients if c["id"] == client_id), None)
    if not client: raise HTTPException(status_code=404, detail="Client not found")
    return client

@app.put("/api/admin/clients/{client_id}")
def update_client(client_id: int, payload: ClientUpdateReq):
    client = next((c for c in db_clients if c["id"] == client_id), None)
    if not client: raise HTTPException(status_code=404, detail="Client not found")
    client |= payload.model_dump()
    return {"success": True, "client": client}

@app.delete("/api/admin/clients/{client_id}")
def delete_client(client_id: int):
    global db_clients
    db_clients = [c for c in db_clients if c["id"] != client_id]
    return {"success": True, "message": "Client deleted successfully"}


# ==========================================
# 6. CLIENT USER / HR ACCOUNT MANAGEMENT
# ==========================================
@app.get("/api/admin/clients/{client_id}/users")
def get_client_users(client_id: int):
    filtered_users = [u for u in db_users if u["client_id"] == client_id]
    return {"users": filtered_users, "total": len(filtered_users)}

@app.post("/api/admin/clients/{client_id}/users")
def create_client_user(client_id: int, payload: ClientUserCreateReq):
    new_id = len(db_users) + 10
    new_user = {
        "id": new_id, "client_id": client_id, "username": payload.username,
        "email": payload.email, "role": payload.role, "status": "active"
    }
    db_users.append(new_user)
    return {"success": True, "user": new_user}

@app.get("/api/admin/users/{user_id}")
def get_user(user_id: int):
    user = next((u for u in db_users if u["id"] == user_id), None)
    if not user: raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/api/admin/users/{user_id}")
def update_user(user_id: int, payload: ClientUserUpdateReq):
    user = next((u for u in db_users if u["id"] == user_id), None)
    if not user: raise HTTPException(status_code=404, detail="User not found")
    user.update(payload.model_dump())
    return {"success": True, "user": user}

@app.delete("/api/admin/users/{user_id}")
def delete_user(user_id: int):
    global db_users
    db_users = [u for u in db_users if u["id"] != user_id]
    return {"success": True, "message": "User deleted successfully"}


# ==========================================
# 7. HR AUTHENTICATION
# ==========================================
@app.post("/api/hr/auth/login")
def hr_login(payload: AdminLoginReq): # Shares basic structure string fields
    if payload.username == "alice" and payload.password == "password":
        return {
            "success": True, "message": "Login successful", "access_token": "mock-user-token", "token_type": "bearer",
            "user": {"id": 10, "client_id": 1, "username": "alice", "email": "alice@abc.com", "role": "HR", "status": "active"}
        }
    raise HTTPException(status_code=401, detail="Invalid HR credentials")

@app.post("/api/hr/auth/logout")
def hr_logout():
    return {"success": True, "message": "Logout successful"}

@app.get("/api/hr/auth/me")
def hr_me():
    return {"id": 10, "client_id": 1, "username": "alice", "email": "alice@abc.com", "role": "HR", "status": "active"}


# ==========================================
# 8. EMPLOYEES
# ==========================================
@app.get("/api/hr/employees")
def get_employees():
    return {"employees": db_employees, "total": len(db_employees)}

@app.post("/api/hr/employees")
def create_employee(payload: EmployeeCreateReq):
    new_id = len(db_employees) + 101
    new_emp = {
        "id": new_id, "client_id": 1, "employee_code": payload.employee_code, "first_name": payload.first_name,
        "last_name": payload.last_name, "email": payload.email, "phone": payload.phone, "department": payload.department,
        "position": payload.position, "status": "active", "face_registered": False, "created_at": datetime.now().isoformat()
    }
    db_employees.append(new_emp)
    return {"success": True, "employee": new_emp}

@app.get("/api/hr/employees/{employee_id}")
def get_employee(employee_id: int):
    emp = next((e for e in db_employees if e["id"] == employee_id), None)
    if not emp: raise HTTPException(status_code=404, detail="Employee profile not found")
    return emp

@app.put("/api/hr/employees/{employee_id}")
def update_employee(employee_id: int, payload: EmployeeCreateReq):
    emp = next((e for e in db_employees if e["id"] == employee_id), None)
    if not emp: raise HTTPException(status_code=404, detail="Employee profile not found")
    emp |= payload.model_dump()
    return {"success": True, "employee": emp}

@app.delete("/api/hr/employees/{employee_id}")
def delete_employee(employee_id: int):
    global db_employees
    db_employees = [e for e in db_employees if e["id"] != employee_id]
    return {"success": True, "message": "Employee profile deleted permanently"}


# ==========================================
# 9. ATTENDANCE
# ==========================================
@app.post("/api/hr/attendance/check-in")
def check_in(payload: CheckInReq):
    """
    Purpose: Record an employee check-in.
    """
    # Create the new record matching the structure specified by the team contract
    new_record = {
        "id": len(db_attendance) + 1001,
        "employee_id": payload.employee_id,
        "date": payload.timestamp.date().isoformat(),  # YYYY-MM-DD
        "check_in": payload.timestamp.isoformat(),     # ISO 8601 Timestamp
        "check_out": None,
        "status": "on_time",
        "worked_hours": 0,
        "overtime_hours": 0,
        "undertime_hours": 0
    }
    db_attendance.append(new_record)
    return {"success": True, "attendance": new_record}

@app.post("/api/hr/attendance/check-out")
def check_out(payload: CheckInReq):
    """
    Purpose: Record an employee check-out.
    """
    # Find an active check-in record for this employee that doesn't have a check-out yet
    record = next((a for a in db_attendance if a["employee_id"] == payload.employee_id and a["check_out"] is None), None)
    
    # Fallback to a mock record if no active check-in exists (helpful for isolated testing)
    if not record:
        record = {
            "id": 1001,
            "employee_id": payload.employee_id,
            "date": payload.timestamp.date().isoformat(),
            "check_in": "2026-09-17T08:52:00"
        }
        db_attendance.append(record)
    
    # Update the record with the computed values from the contract specification
    record["check_out"] = payload.timestamp.isoformat()
    record["status"] = "on_time"
    record["worked_hours"] = 9.3
    record["overtime_hours"] = 1.3
    record["undertime_hours"] = 0
    
    return {"success": True, "attendance": record}

@app.get("/api/hr/attendance")
def get_attendance(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    employee_id: Optional[int] = Query(None),
    department: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """
    Purpose: Get attendance history.
    """
    formatted_attendance = []
    
    for att in db_attendance:
        # Dynamically link the employee name if available in the database state
        emp = next((e for e in db_employees if e["id"] == att["employee_id"]), None)
        emp_name = f"{emp['first_name']} {emp['last_name']}" if emp else "John Smith"
        
        # Format dates/times to match Noura's layout expectations precisely
        formatted_attendance.append({
            "id": att["id"],
            "employee_id": att["employee_id"],
            "employee_name": emp_name,
            "date": att["date"],
            "check_in": "08:52" if att["check_in"] else None,
            "check_out": "18:10" if att.get("check_out") else None,
            "status": att["status"],
            "worked_hours": att.get("worked_hours", 0),
            "overtime_hours": att.get("overtime_hours", 0),
            "undertime_hours": att.get("undertime_hours", 0)
        })
        
    return {"attendance": formatted_attendance, "total": len(formatted_attendance)}

@app.get("/api/hr/attendance/{attendance_id}")
def get_single_attendance(attendance_id: int = Path(...)):
    """
    Purpose: Get one attendance record.
    """
    record = next((a for a in db_attendance if a["id"] == attendance_id), None)
    if not record:
        raise HTTPException(status_code=404, detail="Attendance record missing")
    return record


# ==========================================
# 10. WORK HOURS
# ==========================================
@app.get("/api/hr/work-hours")
def get_work_hours(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    employee_id: Optional[int] = Query(None),
    department: Optional[str] = Query(None)
):
    """
    Purpose: Get work-hour summaries.
    """
    return {
        "work_hours": [
            {
                "employee_id": 101,
                "employee_name": "John Smith",
                "total_worked_hours": 168.5,
                "total_overtime_hours": 8.5,
                "total_undertime_hours": 2.0
            }
        ]
    }

@app.get("/api/hr/work-hours/{employee_id}")
def get_employee_work_hours(employee_id: int = Path(...)):
    """
    Purpose: Get work-hour information for one employee.
    """
    return {
        "employee_id": employee_id,
        "employee_name": "John Smith",
        "total_worked_hours": 168.5,
        "total_overtime_hours": 8.5,
        "total_undertime_hours": 2.0
    }


# ==========================================
# 11. DASHBOARD
# ==========================================
@app.get("/api/hr/dashboard/summary")
def get_dashboard_summary():
    """
    Provides ready-to-display numbers for Noura's Vue dashboard.
    """
    return {
        "total_employees": 50,
        "present": 42,
        "absent": 8,
        "late": 5,
        "on_time": 37,
        "overtime": 6,
        "undertime": 3
    }

@app.get("/api/hr/dashboard/today")
def get_dashboard_today():
    """
    Purpose: Today's attendance overview.
    """
    return {
        "date": "2026-09-17",
        "total_employees": 50,
        "checked_in": 42,
        "not_checked_in": 8,
        "late": 5,
        "on_time": 37
    }

@app.get("/api/hr/dashboard/analytics")
def get_dashboard_analytics():
    """
    Purpose: Data for charts and trend visualization.
    """
    return {
        "attendance_trend": [
            {
                "date": "2026-09-15",
                "present": 45,
                "late": 3,
                "absent": 5
            },
            {
                "date": "2026-09-16",
                "present": 44,
                "late": 4,
                "absent": 6
            },
            {
                "date": "2026-09-17",
                "present": 42,
                "late": 5,
                "absent": 8
            }
        ]
    }


# ==========================================
# 12. ALERTS
# ==========================================
@app.get("/api/hr/alerts")
def get_alerts():
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

@app.get("/api/hr/alerts/overtime")
def get_overtime_alerts():
    """Returns overtime alerts."""
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

@app.get("/api/hr/alerts/under-time")
def get_undertime_alerts():
    """Returns under-time alerts."""
    return {"alerts": [], "total": 0}

@app.get("/api/hr/alerts/late")
def get_late_alerts():
    """Returns late-arrival alerts."""
    return {"alerts": [], "total": 0}


# ==========================================
# 13. FACE AI
# ==========================================
@app.post("/api/face/register")
async def face_register(
    employee_id: int = Query(...), 
    image: UploadFile = File(...)
):
    """
    Purpose: Register an employee's face (Used by Orgil N's PySide6 App).
    """
    # Read image contents to simulate processing
    _ = await image.read()
    return {
        "success": True,
        "employee_id": employee_id,
        "face_registered": True,
        "message": "Face registered successfully"
    }

@app.post("/api/face/verify")
async def face_verify(image: UploadFile = File(...)):
    """
    Purpose: Identify an employee from a captured face.
    """
    _ = await image.read()
    # Mocking recognition rule matching response
    return {
        "success": True,
        "matched": True,
        "employee_id": 101,
        "employee_name": "John Smith",
        "confidence": 0.94
    }


# ==========================================
# 14. REPORTS
# ==========================================
@app.get("/api/hr/reports/attendance")
def report_attendance(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    employee_id: Optional[int] = Query(None),
    department: Optional[str] = Query(None)
):
    """Returns attendance report data."""
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

@app.get("/api/hr/reports/work-hours")
def report_work_hours(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    employee_id: Optional[int] = Query(None),
    department: Optional[str] = Query(None)
):
    """Returns work-hour report data."""
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

@app.get("/api/hr/reports/export")
def report_export(
    report_type: str = Query(...),
    format: str = Query(...), # csv or xlsx
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    employee_id: Optional[int] = Query(None),
    department: Optional[str] = Query(None)
):
    """
    Simulates file binary stream delivery for custom spreadsheets (.csv / .xlsx).
    """
    output = io.StringIO()
    output.write("id,employee_id,date,status,worked_hours\n1001,101,2026-09-17,on_time,9.3\n")
    
    media_type = "text/csv" if format == "csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    response = StreamingResponse(io.BytesIO(output.getvalue().encode()), media_type=media_type)
    response.headers["Content-Disposition"] = f"attachment; filename=report_{report_type}.{format}"
    return response


# ==========================================
# 15. HEALTH
# ==========================================
@app.get("/api/health")
def health_check():
    """
    Purpose: Check whether the API is running (Used by Orgil O for DevOps/QA probes).
    """
    return {"status": "ok"}
