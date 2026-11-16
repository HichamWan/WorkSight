from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.routers import admin, hr

app = FastAPI(
    title="WorkSight API", 
    version="1.1.0", 
    docs_url="/api/docs", 
    openapi_url="/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🚀 FIX: We attach the routers directly without stacking prefixes incorrectly
app.include_router(admin.router)
app.include_router(hr.router)

# Serve uploaded avatars (files live in backend/uploads/avatars)
_BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_AVATAR_DIR = os.path.join(_BACKEND_ROOT, "uploads", "avatars")
os.makedirs(_AVATAR_DIR, exist_ok=True)
app.mount("/api/avatars", StaticFiles(directory=_AVATAR_DIR), name="avatars")

@app.get("/api/health", tags=["System Maintenance"])
def health_check():
    return {"status": "ok", "version": "1.1.0"}
