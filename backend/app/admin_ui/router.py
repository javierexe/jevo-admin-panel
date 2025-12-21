"""
Admin Web UI Router
Simple web interface to manage clients and fields.
Phase 2.B: Connected to Cloud API via HTTP (no direct DB access).
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pathlib import Path
import secrets

from app.core.config import settings
from app.services.cloud_api_client import CloudAPIClient, ErrorType

router = APIRouter(prefix="/admin-ui", tags=["admin-ui"])
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))
security = HTTPBasic()


def verify_admin_ui(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify admin credentials for web UI using HTTP Basic Auth"""
    is_username_correct = secrets.compare_digest(
        credentials.username.encode("utf8"), 
        settings.ADMIN_USERNAME.encode("utf8")
    )
    is_password_correct = secrets.compare_digest(
        credentials.password.encode("utf8"), 
        settings.ADMIN_PASSWORD.encode("utf8")
    )
    
    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def get_cloud_client() -> CloudAPIClient:
    """Dependency to inject CloudAPIClient"""
    return CloudAPIClient(
        base_url=settings.CLOUD_API_URL,
        admin_token=settings.CLOUD_API_ADMIN_TOKEN
    )


def handle_api_error(error_type: ErrorType, detail: str) -> dict:
    """
    Convert API errors into template context with message banner.
    Returns dict with 'message' key matching base.html structure.
    """
    if error_type == ErrorType.UNAUTHORIZED:
        message = "⚠️ Error de autenticación con Cloud API. Verifique el token de administrador."
    elif error_type in (ErrorType.TIMEOUT, ErrorType.NETWORK):
        message = "🔌 Cloud API no disponible. Intente nuevamente más tarde."
    elif error_type == ErrorType.SERVER_ERROR:
        message = "❌ Error en el servidor. Contacte al administrador del sistema."
    else:
        message = f"⚠️ Error inesperado: {detail}"
    
    return {
        "message": {
            "type": "error",
            "text": message
        }
    }


# =====================================================
# ROUTES - Phase 2.B: Connected to Cloud API
# =====================================================

@router.get("/clients", response_class=HTMLResponse)
async def list_clients(
    request: Request, 
    username: str = Depends(verify_admin_ui),
    cloud_client: CloudAPIClient = Depends(get_cloud_client)
):
    """List all clients from Cloud API"""
    result = cloud_client.get_clients()
    
    context = {
        "request": request,
        "open_create_panel": False
    }
    
    if result.ok:
        context["clients"] = result.data or []
    else:
        context["clients"] = []
        context.update(handle_api_error(result.error_type, result.detail))
    
    return templates.TemplateResponse("clients.html", context)


@router.get("/fields", response_class=HTMLResponse)
async def list_fields(
    request: Request, 
    username: str = Depends(verify_admin_ui),
    cloud_client: CloudAPIClient = Depends(get_cloud_client)
):
    """List all fields from Cloud API"""
    result = cloud_client.get_fields()
    
    context = {
        "request": request,
        "open_create_panel": False
    }
    
    if result.ok:
        # Fields endpoint might return both fields and clients
        data = result.data or {}
        context["fields"] = data.get("fields", []) if isinstance(data, dict) else []
        context["clients"] = data.get("clients", []) if isinstance(data, dict) else []
    else:
        context["fields"] = []
        context["clients"] = []
        context.update(handle_api_error(result.error_type, result.detail))
    
    return templates.TemplateResponse("fields.html", context)


@router.get("/whatsapp-users", response_class=HTMLResponse)
async def list_whatsapp_users(
    request: Request, 
    username: str = Depends(verify_admin_ui),
    cloud_client: CloudAPIClient = Depends(get_cloud_client)
):
    """List all WhatsApp users from Cloud API"""
    result = cloud_client.get_whatsapp_users()
    
    context = {
        "request": request,
        "open_create_panel": False
    }
    
    if result.ok:
        # WhatsApp users endpoint might return users and fields
        data = result.data or {}
        context["users"] = data.get("users", []) if isinstance(data, dict) else []
        context["fields"] = data.get("fields", []) if isinstance(data, dict) else []
    else:
        context["users"] = []
        context["fields"] = []
        context.update(handle_api_error(result.error_type, result.detail))
    
    return templates.TemplateResponse("whatsapp_users.html", context)
