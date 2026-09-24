from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from datetime import datetime
from app.auth.crypto import verify_password, create_access_token
from app.auth.dependencies import get_current_user, require_role
from app.database import db_admins, db_clients, db_users, save_to_json

router = APIRouter(prefix="/api/admin", tags=["Admin Management"])

# ==========================================
# PYDANTIC SCHEMAS
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

# ==========================================
# 4. ADMIN AUTHENTICATION
# ==========================================
@router.post("/auth/login")
def admin_login(payload: AdminLoginReq):
    # Find admin user record by username string match lookup
    admin = next((a for a in db_admins if a["username"] == payload.username), None)
    
    # Securely verify password matches hashed storage entry
    if not admin or not verify_password(payload.password, admin["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
        
    # Generate a real secure access token matching the contract schema attributes
    access_token = create_access_token(data={
        "user_id": admin["id"],
        "username": admin["username"],
        "role": admin["role"],
        "client_id": None  # System administrators are global (not restricted to a single tenant)
    })
    
    return {
        "success": True,
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "admin": {
            "id": admin["id"],
            "username": admin["username"],
            "email": admin["email"],
            "role": admin["role"],
            "status": admin["status"]
        }
    }

@router.post("/auth/logout")
def admin_logout(current_user: dict = Depends(get_current_user)):
    return {"success": True, "message": "Logout successful"}

@router.get("/auth/me")
def admin_me(current_user: dict = Depends(require_role(["ADMIN"]))):
    # Retrieve matching admin database state records matching current session metadata
    admin = next((a for a in db_admins if a["id"] == current_user["user_id"]), None)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin account profile entry missing")
        
    return {
        "id": admin["id"],
        "username": admin["username"],
        "email": admin["email"],
        "role": admin["role"],
        "status": admin["status"]
    }

# ==========================================
# 5. CLIENT / COMPANY MANAGEMENT
# ==========================================
@router.get("/clients")
def get_clients(current_user: dict = Depends(require_role(["ADMIN"]))):
    return {"clients": db_clients, "total": len(db_clients)}

@router.post("/clients")
def create_client(payload: ClientCreateReq, current_user: dict = Depends(require_role(["ADMIN"]))):
    new_id = len(db_clients) + 1
    new_client = {
        "id": new_id,
        "company_name": payload.company_name,
        "company_code": payload.company_code,
        "status": "active",
        "created_at": datetime.now().isoformat()
    }
    db_clients.append(new_client)
    save_to_json()
    return {"success": True, "client": new_client}

@router.get("/clients/{client_id}")
def get_client(client_id: int, current_user: dict = Depends(require_role(["ADMIN"]))):
    client = next((c for c in db_clients if c["id"] == client_id), None)
    if not client: 
        raise HTTPException(status_code=404, detail="Client company record entry not found")
    return client

@router.put("/clients/{client_id}")
def update_client(client_id: int, payload: ClientUpdateReq, current_user: dict = Depends(require_role(["ADMIN"]))):
    client = next((c for c in db_clients if c["id"] == client_id), None)
    if not client: 
        raise HTTPException(status_code=404, detail="Client company record entry not found")
    
    # Fix implemented: standard Python dictionary operator merge pattern protection barrier execution rule
    client |= payload.model_dump()
    return {"success": True, "client": client}

@router.delete("/clients/{client_id}")
def delete_client(client_id: int, current_user: dict = Depends(require_role(["ADMIN"]))):
    global db_clients
    client = next((c for c in db_clients if c["id"] == client_id), None)
    if not client: 
        raise HTTPException(status_code=404, detail="Client company record entry not found")
        
    db_clients.remove(client)
    return {"success": True, "message": "Client deleted successfully"}
