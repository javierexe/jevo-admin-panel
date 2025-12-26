from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api import auth, incidents
from app.admin_ui import router as admin_ui_router
from pathlib import Path
import os

# Create FastAPI application
app = FastAPI(
    title="JEVO Incidents API",
    description="Backend API for centralized incident reporting system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for local uploads
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Mount Admin UI static files
admin_ui_static = Path(__file__).parent / "admin_ui" / "static"
if admin_ui_static.exists():
    app.mount("/admin-ui/static", StaticFiles(directory=str(admin_ui_static)), name="admin-ui-static")

# Include routers
app.include_router(auth.router)
app.include_router(incidents.router)
app.include_router(admin_ui_router.router)


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "JEVO Incidents API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/__build")
async def build_info():
    """Build information for debugging"""
    import os
    return {
        "service": "jevo-admin-panel",
        "commit": os.getenv("RAILWAY_GIT_COMMIT_SHA", "unknown"),
        "branch": os.getenv("RAILWAY_GIT_BRANCH", "unknown"),
        "env": os.getenv("RAILWAY_ENVIRONMENT_NAME", "unknown")
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
