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
from datetime import datetime
import pytz

from app.core.config import settings
from app.services.cloud_api_client import CloudAPIClient, ErrorType

router = APIRouter(prefix="/admin-ui", tags=["admin-ui"])
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

def convert_utc_to_chile(iso_string: str) -> str:
    """Convert UTC ISO timestamp to Chile time (America/Santiago) in DD/MM/YYYY HH:MM format"""
    if not iso_string:
        return "—"
    try:
        # Parse ISO timestamp
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        # Convert to Chile timezone
        chile_tz = pytz.timezone('America/Santiago')
        dt_chile = dt.astimezone(chile_tz)
        # Format as DD/MM/YYYY HH:MM
        return dt_chile.strftime('%d/%m/%Y %H:%M')
    except:
        return "—"
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
    try:
        result = cloud_client.get_clients()
        print(f"[list_clients] API result: ok={result.ok}, data_type={type(result.data)}, data={result.data}")
        
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
    except Exception as e:
        print(f"[list_clients] ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise


@router.get("/fields", response_class=HTMLResponse)
async def list_fields(
    request: Request, 
    username: str = Depends(verify_admin_ui),
    cloud_client: CloudAPIClient = Depends(get_cloud_client)
):
    """List all fields from Cloud API"""
    try:
        result = cloud_client.get_fields()
        print(f"[list_fields] API result: ok={result.ok}, data_type={type(result.data)}, data={result.data}")
        
        context = {
            "request": request,
            "open_create_panel": False
        }
        
        if result.ok:
            # Fields endpoint returns a list directly
            data = result.data or []
            if isinstance(data, list):
                # Convert UTC timestamps to Chile time
                for field in data:
                    if isinstance(field, dict) and 'last_sync_at' in field:
                        field['last_sync_at_formatted'] = convert_utc_to_chile(field['last_sync_at'])
                context["fields"] = data
            elif isinstance(data, dict):
                fields = data.get("fields", [])
                for field in fields:
                    if isinstance(field, dict) and 'last_sync_at' in field:
                        field['last_sync_at_formatted'] = convert_utc_to_chile(field['last_sync_at'])
                context["fields"] = fields
            else:
                context["fields"] = []
        else:
            context["fields"] = []
            context.update(handle_api_error(result.error_type, result.detail))
            print(f"[list_fields] API Error: {result.error_type} - {result.detail}")
        
        # Fetch clients separately for the create form
        clients_result = cloud_client.get_clients()
        if clients_result.ok:
            clients_data = clients_result.data or []
            if isinstance(clients_data, list):
                context["clients"] = clients_data
            elif isinstance(clients_data, dict):
                context["clients"] = clients_data.get("clients", [])
            else:
                context["clients"] = []
        else:
            context["clients"] = []
            print(f"[list_fields] Clients API Error: {clients_result.error_type} - {clients_result.detail}")
        
        print(f"[list_fields] Rendering: {len(context['fields'])} fields, {len(context['clients'])} clients")
        
        return templates.TemplateResponse("fields.html", context)
    except Exception as e:
        print(f"[list_fields] ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise


@router.get("/whatsapp-users", response_class=HTMLResponse)
async def list_whatsapp_users(
    request: Request, 
    username: str = Depends(verify_admin_ui),
    cloud_client: CloudAPIClient = Depends(get_cloud_client)
):
    """List all WhatsApp users from Cloud API"""
    try:
        # Fetch users and fields in parallel
        result = cloud_client.get_whatsapp_users()
        fields_result = cloud_client.get_fields()
        
        print(f"[list_whatsapp_users] API result: ok={result.ok}, data_type={type(result.data)}, data={result.data}")
        
        # Build field lookup map by ID
        fields_map = {}
        if fields_result.ok and isinstance(fields_result.data, list):
            for field in fields_result.data:
                if isinstance(field, dict) and 'id' in field:
                    fields_map[field['id']] = field
        
        context = {
            "request": request,
            "open_create_panel": False
        }
        
        if result.ok:
            # WhatsApp users endpoint returns a list directly
            data = result.data or []
            users = []
            if isinstance(data, list):
                # Process each user: add created_at format and field info
                for user in data:
                    if isinstance(user, dict):
                        # Format created_at
                        if 'created_at' in user:
                            user['created_at_formatted'] = convert_utc_to_chile(user['created_at'])
                        
                        # Get assigned field codes
                        assigned_field_ids = user.get('assigned_field_ids', [])
                        field_codes = []
                        for field_id in assigned_field_ids:
                            if field_id in fields_map:
                                field_codes.append(fields_map[field_id].get('field_code', '?'))
                        
                        user['fields_count'] = len(field_codes)
                        user['assigned_fields_display'] = ', '.join(field_codes) if field_codes else '—'
                    
                    users.append(user)
                context["users"] = users
                context["fields"] = []
            elif isinstance(data, dict):
                users_list = data.get("users", [])
                for user in users_list:
                    if isinstance(user, dict):
                        if 'created_at' in user:
                            user['created_at_formatted'] = convert_utc_to_chile(user['created_at'])
                        
                        assigned_field_ids = user.get('assigned_field_ids', [])
                        field_codes = []
                        for field_id in assigned_field_ids:
                            if field_id in fields_map:
                                field_codes.append(fields_map[field_id].get('field_code', '?'))
                        
                        user['fields_count'] = len(field_codes)
                        user['assigned_fields_display'] = ', '.join(field_codes) if field_codes else '—'
                
                context["users"] = users_list
                context["fields"] = data.get("fields", [])
            else:
                context["users"] = []
                context["fields"] = []
            print(f"[list_whatsapp_users] Rendering: {len(context['users'])} users, {len(context['fields'])} fields")
        else:
            context["users"] = []
            context["fields"] = []
            context.update(handle_api_error(result.error_type, result.detail))
            print(f"[list_whatsapp_users] API Error: {result.error_type} - {result.detail}")
        
        return templates.TemplateResponse("whatsapp_users.html", context)
    except Exception as e:
        print(f"[list_whatsapp_users] ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise


# =====================================================
# WhatsApp Users CRUD endpoints  
# =====================================================

@router.post("/whatsapp-users", response_class=HTMLResponse)
async def create_whatsapp_user(
    request: Request,
    username: str = Depends(verify_admin_ui),
    cloud_client: CloudAPIClient = Depends(get_cloud_client),
    phone_number: str = Form(...),
    display_name: Optional[str] = Form(None),
    field_ids: Optional[str] = Form(None)
):
    """Create new WhatsApp user via Cloud API"""
    # Parse field_ids (comma-separated string from form)
    field_ids_list = []
    if field_ids:
        try:
            field_ids_list = [int(fid.strip()) for fid in field_ids.split(",") if fid.strip()]
        except ValueError:
            return RedirectResponse(
                url="/admin-ui/whatsapp-users?error=IDs de campos inválidos",
                status_code=303
            )
    
    data = {
        "phone_number": phone_number,
        "display_name": display_name if display_name else None,
        "field_ids": field_ids_list
    }
    
    result = cloud_client.create_whatsapp_user(data)
    
    if result.ok:
        return RedirectResponse(
            url="/admin-ui/whatsapp-users?success=Usuario WhatsApp creado exitosamente",
            status_code=303
        )
    
    # On error, redirect with error message
    if result.error_type == ErrorType.CONFLICT:
        return RedirectResponse(
            url=f"/admin-ui/whatsapp-users?error={result.detail or 'Conflicto: el usuario ya existe'}",
            status_code=303
        )
    elif result.error_type == ErrorType.VALIDATION:
        return RedirectResponse(
            url=f"/admin-ui/whatsapp-users?error={result.detail or 'Error de validación'}",
            status_code=303
        )
    else:
        return RedirectResponse(
            url=f"/admin-ui/whatsapp-users?error={result.detail or 'Error al crear usuario'}",
            status_code=303
        )


@router.get("/whatsapp-users/{user_id}/edit", response_class=HTMLResponse)
async def edit_whatsapp_user_form(
    request: Request,
    user_id: str,
    username: str = Depends(verify_admin_ui),
    cloud_client: CloudAPIClient = Depends(get_cloud_client)
):
    """Load WhatsApp user for editing"""
    # Fetch user and all fields in parallel
    user_result = cloud_client.get_whatsapp_user(user_id)
    fields_result = cloud_client.get_fields()
    
    if not user_result.ok:
        if user_result.error_type == ErrorType.NOT_FOUND:
            return RedirectResponse(
                url="/admin-ui/whatsapp-users?error=Usuario no encontrado",
                status_code=303
            )
        context = {"request": request, "user": None, "available_fields": []}
        context.update(handle_api_error(user_result.error_type, user_result.detail))
        return templates.TemplateResponse("edit_whatsapp_user.html", context)
    
    user_data = user_result.data
    all_fields = fields_result.data if fields_result.ok else []
    
    # Get assigned field IDs - API returns 'assigned_field_ids' not 'field_ids'
    assigned_field_ids = []
    if isinstance(user_data, dict):
        assigned_field_ids = user_data.get("assigned_field_ids", user_data.get("field_ids", []))
    
    print(f"[edit_whatsapp_user] user_data type: {type(user_data)}, assigned_field_ids: {assigned_field_ids}")
    
    # Process fields to add display name and is_assigned flag
    processed_fields = []
    if isinstance(all_fields, list):
        for field in all_fields:
            if isinstance(field, dict):
                field_copy = field.copy()
                # Create display name: "FIELD_CODE - Name (CLIENT_CODE)"
                field_code = field.get("field_code", "?")
                name = field.get("name", "Campo sin nombre")
                client_code = field.get("client_code", "")
                field_copy["display"] = f"{field_code} - {name} ({client_code})" if client_code else f"{field_code} - {name}"
                field_copy["is_assigned"] = field.get("id") in assigned_field_ids
                processed_fields.append(field_copy)
    
    print(f"[edit_whatsapp_user] Processed {len(processed_fields)} fields, {sum(1 for f in processed_fields if f.get('is_assigned'))} assigned")
    
    context = {
        "request": request,
        "user": user_data,
        "available_fields": processed_fields,
        "assigned_field_ids": assigned_field_ids
    }
    return templates.TemplateResponse("edit_whatsapp_user.html", context)


@router.post("/whatsapp-users/{user_id}/edit")
async def update_whatsapp_user(
    request: Request,
    user_id: str,
    username: str = Depends(verify_admin_ui),
    cloud_client: CloudAPIClient = Depends(get_cloud_client),
    display_name: Optional[str] = Form(None),
    is_active: Optional[str] = Form(None)
):
    """Update WhatsApp user via Cloud API"""
    # Parse field_ids from form data (multiple values with same name)
    form_data = await request.form()
    field_ids_list = []
    if 'field_ids' in form_data:
        # Get all values with name 'field_ids' (they are UUID strings, not ints)
        field_ids_values = form_data.getlist('field_ids')
        field_ids_list = [str(fid).strip() for fid in field_ids_values if fid]
    
    data = {
        "display_name": display_name if display_name else None,
        "is_active": is_active == "true",
        "field_ids": field_ids_list
    }
    
    result = cloud_client.update_whatsapp_user(user_id, data)
    
    if result.ok:
        return RedirectResponse(
            url="/admin-ui/whatsapp-users?success=Usuario actualizado exitosamente",
            status_code=303
        )
    
    # On error, fetch user again and stay on edit page
    user_result = cloud_client.get_whatsapp_user(user_id)
    fields_result = cloud_client.get_fields()
    user_data = user_result.data if user_result.ok else {}
    all_fields = fields_result.data if fields_result.ok else []
    
    context = {
        "request": request,
        "user": {**data, "id": user_id, "phone_number": user_data.get("phone_number", "")},
        "available_fields": all_fields,
        "assigned_field_ids": field_ids_list
    }
    context.update(handle_api_error(result.error_type, result.detail))
    return templates.TemplateResponse("edit_whatsapp_user.html", context)


@router.post("/whatsapp-users/{user_id}/delete")
async def delete_whatsapp_user(
    user_id: str,
    username: str = Depends(verify_admin_ui),
    cloud_client: CloudAPIClient = Depends(get_cloud_client)
):
    """Soft delete WhatsApp user via Cloud API"""
    result = cloud_client.delete_whatsapp_user(user_id)
    
    if result.ok:
        return RedirectResponse(
            url="/admin-ui/whatsapp-users?success=Usuario eliminado exitosamente",
            status_code=303
        )
    
    if result.error_type == ErrorType.NOT_FOUND:
        return RedirectResponse(
            url="/admin-ui/whatsapp-users?error=Usuario no encontrado",
            status_code=303
        )
    
    return RedirectResponse(
        url=f"/admin-ui/whatsapp-users?error={result.detail or 'Error al eliminar usuario'}",
        status_code=303
    )


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
        context = {
            "request": request,
            "client": {"code": client_code, "name": ""},
            "terminology": {"unit_terms": "", "group_terms": "", "program_terms": ""}
        }
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
    
    # Fetch current fields list
    list_result = cloud_client.get_fields()
    if list_result.ok:
        data_response = list_result.data or {}
        if isinstance(data_response, list):
            context["fields"] = data_response
        elif isinstance(data_response, dict):
            context["fields"] = data_response.get("fields", [])
        else:
            context["fields"] = []
    
    # Fetch clients separately
    clients_result = cloud_client.get_clients()
    if clients_result.ok:
        clients_data = clients_result.data or []
        if isinstance(clients_data, list):
            context["clients"] = clients_data
        elif isinstance(clients_data, dict):
            context["clients"] = clients_data.get("clients", [])
        else:
            context["clients"] = []
    
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
        context = {
            "request": request,
            "field": {
                "code": field_code,
                "name": "",
                "client": {"code": client_code, "name": ""},
                "active": False,
                "location_lat": None,
                "location_lng": None,
                "timezone": "America/Santiago"
            },
            "icc_credentials": {"host": "", "port": 5432, "dbname": "", "user": ""},
            "nomenclature": {"aliases": "", "units_text": "", "groups_text": ""}
        }
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
