"""
Admin Web UI Router
Simple web interface to manage clients and fields.
Phase 2.A: Basic routing with templates, no CRUD operations yet.
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pathlib import Path
import os
import secrets

router = APIRouter(prefix="/admin-ui", tags=["admin-ui"])
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))
security = HTTPBasic()

# Admin credentials from environment
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


def verify_admin_ui(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify admin credentials for web UI using HTTP Basic Auth"""
    is_username_correct = secrets.compare_digest(
        credentials.username.encode("utf8"), 
        ADMIN_USERNAME.encode("utf8")
    )
    is_password_correct = secrets.compare_digest(
        credentials.password.encode("utf8"), 
        ADMIN_PASSWORD.encode("utf8")
    )
    
    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# =====================================================
# ROUTES - Phase 2.A: Basic templates only
# =====================================================

@router.get("/clients", response_class=HTMLResponse)
async def list_clients(request: Request, username: str = Depends(verify_admin_ui)):
    """List all clients - placeholder view"""
    return templates.TemplateResponse("clients.html", {
        "request": request,
        "clients": [],  # Empty for now
        "open_create_panel": False
    })


@router.get("/fields", response_class=HTMLResponse)
async def list_fields(request: Request, username: str = Depends(verify_admin_ui)):
    """List all fields - placeholder view"""
    return templates.TemplateResponse("fields.html", {
        "request": request,
        "fields": [],  # Empty for now
        "clients": [],  # Empty for now
        "open_create_panel": False
    })


@router.get("/whatsapp-users", response_class=HTMLResponse)
async def list_whatsapp_users(request: Request, username: str = Depends(verify_admin_ui)):
    """List all WhatsApp users - placeholder view"""
    return templates.TemplateResponse("whatsapp_users.html", {
        "request": request,
        "users": [],  # Empty for now
        "fields": [],  # Empty for now
        "open_create_panel": False
    })
