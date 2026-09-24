from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

@app.get("/api/health", tags=["System Maintenance"])
def health_check():
    return {"status": "ok"}
