"""
Admin Web UI Router
Simple web interface to manage clients and fields.
Phase 2.B: Connected to Cloud API via HTTP (no direct DB access).
Phase 3.A: Full CRUD operations via CloudAPIClient.
"""
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pathlib import Path
import secrets
from typing import Optional

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
    elif error_type == ErrorType.NOT_FOUND:
        message = "❓ Recurso no encontrado."
    elif error_type == ErrorType.VALIDATION:
        message = f"⚠️ Error de validación: {detail}"
    elif error_type == ErrorType.CONFLICT:
        message = f"⚠️ Conflicto: {detail}"
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


# =====================================================
# CLIENTS CRUD - Phase 3.A
# =====================================================

@router.post("/clients", response_class=HTMLResponse)
async def create_client(
    request: Request,
    username: str = Depends(verify_admin_ui),
    cloud_client: CloudAPIClient = Depends(get_cloud_client),
    code: str = Form(...),
    name: str = Form(...),
    contact_email: Optional[str] = Form(None),
    whatsapp_number: Optional[str] = Form(None)
):
    """Create new client via Cloud API"""
    data = {
        "code": code,
        "name": name,
        "contact_email": contact_email if contact_email else None,
        "whatsapp_number": whatsapp_number if whatsapp_number else None
    }
    
    result = cloud_client.create_client(data)
    
    if result.ok:
        return RedirectResponse(
            url="/admin-ui/clients?success=Cliente creado exitosamente",
            status_code=303
        )
    
    # On error, return to list page with error banner
    context = {
        "request": request,
        "clients": [],
        "open_create_panel": True,
        "form_data": data
    }
    context.update(handle_api_error(result.error_type, result.detail))
    
    # Also fetch current clients list
    list_result = cloud_client.get_clients()
    if list_result.ok:
        context["clients"] = list_result.data or []
    
    return templates.TemplateResponse("clients.html", context)


@router.get("/clients/{client_code}/edit", response_class=HTMLResponse)
async def edit_client_form(
    request: Request,
    client_code: str,
    username: str = Depends(verify_admin_ui),
    cloud_client: CloudAPIClient = Depends(get_cloud_client)
):
    """Load client for editing"""
    result = cloud_client.get_client_detail(client_code)
    
    if not result.ok:
        if result.error_type == ErrorType.NOT_FOUND:
            return RedirectResponse(
                url="/admin-ui/clients?error=Cliente no encontrado",
                status_code=303
            )
        context = {"request": request, "client": None}
        context.update(handle_api_error(result.error_type, result.detail))
        return templates.TemplateResponse("edit_client.html", context)
    
    client_data = result.data
    context = {
        "request": request,
        "client": client_data,
        "terminology": client_data.get("terminology", {}) if isinstance(client_data, dict) else {}
    }
    return templates.TemplateResponse("edit_client.html", context)


@router.post("/clients/{client_code}/edit", response_class=HTMLResponse)
async def update_client(
    request: Request,
    client_code: str,
    username: str = Depends(verify_admin_ui),
    cloud_client: CloudAPIClient = Depends(get_cloud_client),
    name: str = Form(...),
    contact_email: Optional[str] = Form(None),
    whatsapp_number: Optional[str] = Form(None)
):
    """Update client via Cloud API"""
    data = {
        "name": name,
        "contact_email": contact_email if contact_email else None,
        "whatsapp_number": whatsapp_number if whatsapp_number else None
    }
    
    result = cloud_client.update_client(client_code, data)
    
    if result.ok:
        return RedirectResponse(
            url="/admin-ui/clients?success=Cliente actualizado exitosamente",
            status_code=303
        )
    
    # On error, stay on edit page with error banner
    # Need to fetch full client data to get terminology for template
    client_result = cloud_client.get_client_detail(client_code)
    client_data = client_result.data if client_result.ok else {}
    terminology = client_data.get("terminology", {}) if isinstance(client_data, dict) else {}
    
    context = {
        "request": request,
        "client": {**data, "code": client_code},
        "terminology": terminology
    }
    context.update(handle_api_error(result.error_type, result.detail))
    return templates.TemplateResponse("edit_client.html", context)


@router.post("/clients/{client_code}/delete")
async def delete_client(
    client_code: str,
    username: str = Depends(verify_admin_ui),
    cloud_client: CloudAPIClient = Depends(get_cloud_client)
):
    """Delete client via Cloud API"""
    result = cloud_client.delete_client(client_code)
    
    if result.ok:
        return RedirectResponse(
            url="/admin-ui/clients?success=Cliente eliminado exitosamente",
            status_code=303
        )
    
    # On error, redirect with error message
    error_msg = "No se pudo eliminar el cliente"
    if result.error_type == ErrorType.NOT_FOUND:
        error_msg = "Cliente no encontrado"
    elif result.error_type == ErrorType.CONFLICT:
        error_msg = "No se puede eliminar: el cliente tiene campos asociados"
    
    return RedirectResponse(
        url=f"/admin-ui/clients?error={error_msg}",
        status_code=303
    )


# =====================================================
# FIELDS CRUD - Phase 3.A
# =====================================================

@router.post("/fields", response_class=HTMLResponse)
async def create_field(
    request: Request,
    username: str = Depends(verify_admin_ui),
    cloud_client: CloudAPIClient = Depends(get_cloud_client),
    client_code: str = Form(...),
    field_code: str = Form(...),
    name: str = Form(...),
    location: Optional[str] = Form(None),
    size_ha: Optional[float] = Form(None),
    timezone: str = Form("America/Santiago")
):
    """Create new field via Cloud API"""
    data = {
        "client_code": client_code,
        "field_code": field_code,
        "name": name,
        "location": location if location else None,
        "size_ha": size_ha,
        "timezone": timezone
    }
    
    result = cloud_client.create_field(data)
    
    if result.ok:
        return RedirectResponse(
            url="/admin-ui/fields?success=Campo creado exitosamente",
            status_code=303
        )
    
    # On error, return to list page with error banner
    context = {
        "request": request,
        "fields": [],
        "clients": [],
        "open_create_panel": True,
        "form_data": data
    }
    context.update(handle_api_error(result.error_type, result.detail))
    
    # Fetch current lists
    list_result = cloud_client.get_fields()
    if list_result.ok:
        data_response = list_result.data or {}
        context["fields"] = data_response.get("fields", []) if isinstance(data_response, dict) else []
        context["clients"] = data_response.get("clients", []) if isinstance(data_response, dict) else []
    
    return templates.TemplateResponse("fields.html", context)


@router.get("/fields/{client_code}/{field_code}/edit", response_class=HTMLResponse)
async def edit_field_form(
    request: Request,
    client_code: str,
    field_code: str,
    username: str = Depends(verify_admin_ui),
    cloud_client: CloudAPIClient = Depends(get_cloud_client)
):
    """Load field for editing"""
    result = cloud_client.get_field_detail(client_code, field_code)
    
    if not result.ok:
        if result.error_type == ErrorType.NOT_FOUND:
            return RedirectResponse(
                url="/admin-ui/fields?error=Campo no encontrado",
                status_code=303
            )
        context = {"request": request, "field": None}
        context.update(handle_api_error(result.error_type, result.detail))
        return templates.TemplateResponse("edit_field.html", context)
    
    field_data = result.data
    context = {
        "request": request,
        "field": field_data,
        "icc_credentials": field_data.get("icc_credentials", {}) if isinstance(field_data, dict) else {},
        "nomenclature": field_data.get("nomenclature", {}) if isinstance(field_data, dict) else {}
    }
    return templates.TemplateResponse("edit_field.html", context)


@router.post("/fields/{client_code}/{field_code}/edit", response_class=HTMLResponse)
async def update_field(
    request: Request,
    client_code: str,
    field_code: str,
    username: str = Depends(verify_admin_ui),
    cloud_client: CloudAPIClient = Depends(get_cloud_client),
    name: str = Form(...),
    location: Optional[str] = Form(None),
    size_ha: Optional[float] = Form(None),
    timezone: str = Form("America/Santiago"),
    icc_username: Optional[str] = Form(None),
    icc_password: Optional[str] = Form(None)
):
    """Update field via Cloud API"""
    data = {
        "name": name,
        "location": location if location else None,
        "size_ha": size_ha,
        "timezone": timezone
    }
    
    # Only include ICC credentials if provided
    if icc_username:
        data["icc_username"] = icc_username
    if icc_password:
        data["icc_password"] = icc_password
    
    result = cloud_client.update_field(client_code, field_code, data)
    
    if result.ok:
        return RedirectResponse(
            url="/admin-ui/fields?success=Campo actualizado exitosamente",
            status_code=303
        )
    
    # On error, stay on edit page with error banner
    # Need to fetch full field data to get icc_credentials and nomenclature for template
    field_result = cloud_client.get_field_detail(client_code, field_code)
    field_data = field_result.data if field_result.ok else {}
    icc_credentials = field_data.get("icc_credentials", {}) if isinstance(field_data, dict) else {}
    nomenclature = field_data.get("nomenclature", {}) if isinstance(field_data, dict) else {}
    
    context = {
        "request": request,
        "field": {**data, "client_code": client_code, "field_code": field_code},
        "icc_credentials": icc_credentials,
        "nomenclature": nomenclature
    }
    context.update(handle_api_error(result.error_type, result.detail))
    return templates.TemplateResponse("edit_field.html", context)


@router.post("/fields/{client_code}/{field_code}/delete")
async def delete_field(
    client_code: str,
    field_code: str,
    username: str = Depends(verify_admin_ui),
    cloud_client: CloudAPIClient = Depends(get_cloud_client)
):
    """Delete field via Cloud API"""
    result = cloud_client.delete_field(client_code, field_code)
    
    if result.ok:
        return RedirectResponse(
            url="/admin-ui/fields?success=Campo eliminado exitosamente",
            status_code=303
        )
    
    # On error, redirect with error message
    error_msg = "No se pudo eliminar el campo"
    if result.error_type == ErrorType.NOT_FOUND:
        error_msg = "Campo no encontrado"
    elif result.error_type == ErrorType.CONFLICT:
        error_msg = "No se puede eliminar: el campo tiene datos asociados"
    
    return RedirectResponse(
        url=f"/admin-ui/fields?error={error_msg}",
        status_code=303
    )


@router.get("/fields/{client_code}/{field_code}/config")
async def download_field_config(
    client_code: str,
    field_code: str,
    username: str = Depends(verify_admin_ui),
    cloud_client: CloudAPIClient = Depends(get_cloud_client)
):
    """Download field agent config as .env file via Cloud API proxy"""
    result = cloud_client.get_field_agent_config(client_code, field_code)
    
    if not result.ok:
        # Redirect to fields list with error
        error_msg = "No se pudo descargar la configuración"
        if result.error_type == ErrorType.NOT_FOUND:
            error_msg = "Configuración no encontrada"
        return RedirectResponse(
            url=f"/admin-ui/fields?error={error_msg}",
            status_code=303
        )
    
    # Return plain text with Content-Disposition header
    filename = f"{client_code}_{field_code}.env"
    return PlainTextResponse(
        content=result.data,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
