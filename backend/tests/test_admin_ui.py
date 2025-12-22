"""
Unit tests for admin_ui routes with mocked CloudAPIClient.
Phase 2.B Commit 3 - Verify error handling and dependency injection.
"""
import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient

from app.main import app
from app.services.cloud_api_client import CloudAPIClient, APIResult, ErrorType
from app.admin_ui.router import handle_api_error, get_cloud_client


client = TestClient(app)


# =====================================================
# TEST: handle_api_error() utility function
# =====================================================

def test_handle_api_error_unauthorized():
    """Test UNAUTHORIZED error converts to auth error message"""
    result = handle_api_error(ErrorType.UNAUTHORIZED, "Invalid token")
    
    assert "message" in result
    assert result["message"]["type"] == "error"
    assert "autenticación" in result["message"]["text"].lower()
    assert "⚠️" in result["message"]["text"]


def test_handle_api_error_timeout():
    """Test TIMEOUT error converts to network unavailable message"""
    result = handle_api_error(ErrorType.TIMEOUT, "Connection timeout")
    
    assert "message" in result
    assert result["message"]["type"] == "error"
    assert "no disponible" in result["message"]["text"].lower()
    assert "🔌" in result["message"]["text"]


def test_handle_api_error_network():
    """Test NETWORK error converts to network unavailable message"""
    result = handle_api_error(ErrorType.NETWORK, "Connection refused")
    
    assert "message" in result
    assert result["message"]["type"] == "error"
    assert "no disponible" in result["message"]["text"].lower()


def test_handle_api_error_server():
    """Test SERVER_ERROR converts to server error message"""
    result = handle_api_error(ErrorType.SERVER_ERROR, "Internal server error")
    
    assert "message" in result
    assert result["message"]["type"] == "error"
    assert "servidor" in result["message"]["text"].lower()
    assert "❌" in result["message"]["text"]


def test_handle_api_error_unknown():
    """Test unknown errors include detail message"""
    result = handle_api_error(ErrorType.UNKNOWN, "Something went wrong")
    
    assert "message" in result
    assert result["message"]["type"] == "error"
    assert "Something went wrong" in result["message"]["text"]


# =====================================================
# TEST: Admin UI routes with HTTP Basic Auth
# =====================================================

def test_list_clients_without_auth():
    """Test /admin-ui/clients returns 401 without auth"""
    response = client.get("/admin-ui/clients")
    
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers


def test_list_fields_without_auth():
    """Test /admin-ui/fields returns 401 without auth"""
    response = client.get("/admin-ui/fields")
    
    assert response.status_code == 401


def test_list_whatsapp_users_without_auth():
    """Test /admin-ui/whatsapp-users returns 401 without auth"""
    response = client.get("/admin-ui/whatsapp-users")
    
    assert response.status_code == 401


# =====================================================
# TEST: Successful API responses (mocked CloudAPIClient)
# =====================================================

def test_list_clients_success():
    """Test /admin-ui/clients with successful Cloud API response"""
    # Mock CloudAPIClient using dependency_overrides
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_clients.return_value = APIResult(
        ok=True,
        data=[
            {"code": "CLI001", "name": "Cliente Test", "fields_count": 5}
        ],
        error_type=None,
        detail=None
    )
    
    # Override dependency
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get(
            "/admin-ui/clients",
            auth=("admin", "admin123")
        )
        
        assert response.status_code == 200
        assert "Cliente Test" in response.text
        assert "CLI001" in response.text
        # Should NOT show error banner
        assert "🔌 Cloud API no disponible" not in response.text
    finally:
        # Clean up override
        app.dependency_overrides.clear()


def test_list_fields_success():
    """Test /admin-ui/fields with successful Cloud API response"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_fields.return_value = APIResult(
        ok=True,
        data={
            "fields": [
                {
                    "field_code": "FLD001",  # Template expects field_code
                    "name": "Campo Norte",
                    "client_name": "Cliente Test",
                    "size_ha": 10.5
                }
            ],
            "clients": []
        },
        error_type=None,
        detail=None
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get(
            "/admin-ui/fields",
            auth=("admin", "admin123")
        )
        
        assert response.status_code == 200
        assert "Campo Norte" in response.text
        assert "FLD001" in response.text
    finally:
        app.dependency_overrides.clear()


def test_list_whatsapp_users_success():
    """Test /admin-ui/whatsapp-users with successful Cloud API response"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_whatsapp_users.return_value = APIResult(
        ok=True,
        data={
            "users": [
                {
                    "phone_number_id": "123456",
                    "display_name": "Test User",
                    "is_active": True
                }
            ],
            "fields": []
        },
        error_type=None,
        detail=None
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get(
            "/admin-ui/whatsapp-users",
            auth=("admin", "admin123")
        )
        
        assert response.status_code == 200
        assert "Test User" in response.text
        assert "123456" in response.text
    finally:
        app.dependency_overrides.clear()


# =====================================================
# TEST: Error scenarios (mocked CloudAPIClient)
# =====================================================

def test_list_clients_network_error():
    """Test /admin-ui/clients shows error banner on NETWORK error"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_clients.return_value = APIResult(
        ok=False,
        data=None,
        error_type=ErrorType.NETWORK,
        detail="Connection refused"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get(
            "/admin-ui/clients",
            auth=("admin", "admin123")
        )
        
        assert response.status_code == 200
        # Should show error banner
        assert "🔌 Cloud API no disponible" in response.text
        assert "bg-red-50" in response.text  # Error banner styling
    finally:
        app.dependency_overrides.clear()


def test_list_fields_timeout_error():
    """Test /admin-ui/fields shows error banner on TIMEOUT error"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_fields.return_value = APIResult(
        ok=False,
        data=None,
        error_type=ErrorType.TIMEOUT,
        detail="Request timeout"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get(
            "/admin-ui/fields",
            auth=("admin", "admin123")
        )
        
        assert response.status_code == 200
        assert "🔌 Cloud API no disponible" in response.text
    finally:
        app.dependency_overrides.clear()


def test_list_whatsapp_users_unauthorized_error():
    """Test /admin-ui/whatsapp-users shows auth error banner on UNAUTHORIZED"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_whatsapp_users.return_value = APIResult(
        ok=False,
        data=None,
        error_type=ErrorType.UNAUTHORIZED,
        detail="Invalid admin token"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get(
            "/admin-ui/whatsapp-users",
            auth=("admin", "admin123")
        )
        
        assert response.status_code == 200
        assert "⚠️ Error de autenticación" in response.text
    finally:
        app.dependency_overrides.clear()


def test_list_clients_server_error():
    """Test /admin-ui/clients shows server error banner on SERVER_ERROR"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_clients.return_value = APIResult(
        ok=False,
        data=None,
        error_type=ErrorType.SERVER_ERROR,
        detail="Internal server error"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get(
            "/admin-ui/clients",
            auth=("admin", "admin123")
        )
        
        assert response.status_code == 200
        assert "❌ Error en el servidor" in response.text
    finally:
        app.dependency_overrides.clear()


# =====================================================
# TEST: Empty data handling
# =====================================================

def test_list_clients_empty_data():
    """Test /admin-ui/clients handles empty data array gracefully"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_clients.return_value = APIResult(
        ok=True,
        data=[],  # Empty list
        error_type=None,
        detail=None
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get(
            "/admin-ui/clients",
            auth=("admin", "admin123")
        )
        
        assert response.status_code == 200
        # Should show empty state message
        assert "No hay clientes registrados" in response.text
    finally:
        app.dependency_overrides.clear()


def test_list_fields_none_data():
    """Test /admin-ui/fields handles None data gracefully"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_fields.return_value = APIResult(
        ok=True,
        data=None,  # None triggers default empty dict behavior
        error_type=None,
        detail=None
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get(
            "/admin-ui/fields",
            auth=("admin", "admin123")
        )
        
        assert response.status_code == 200
        # Should default to empty dict → empty lists → empty state
        assert "No hay campos registrados" in response.text
    finally:
        app.dependency_overrides.clear()


# =====================================================
# TEST: Clients CRUD operations - Phase 3.A
# =====================================================

def test_create_client_success():
    """Test POST /admin-ui/clients creates client successfully"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.create_client.return_value = APIResult(ok=True, data={"code": "CLI001"}, status=201)
    mock_client.get_clients.return_value = APIResult(ok=True, data=[], status=200)  # For error path
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.post(
            "/admin-ui/clients",
            auth=("admin", "admin123"),
            data={
                "code": "CLI001",
                "name": "Test Client",
                "contact_email": "test@example.com",
                "whatsapp_number": "56912345678"
            },
            follow_redirects=False  # Don't follow redirect
        )
        
        assert response.status_code == 303  # Redirect
        assert "/admin-ui/clients" in response.headers["location"]
        assert "success=" in response.headers["location"]
        mock_client.create_client.assert_called_once()
    finally:
        app.dependency_overrides.clear()


def test_create_client_validation_error():
    """Test POST /admin-ui/clients with validation error"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.create_client.return_value = APIResult(
        ok=False,
        error_type=ErrorType.VALIDATION,
        status=422,
        detail="Invalid email format"
    )
    mock_client.get_clients.return_value = APIResult(ok=True, data=[], status=200)
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.post(
            "/admin-ui/clients",
            auth=("admin", "admin123"),
            data={"code": "CLI001", "name": "Test", "contact_email": "invalid"}
        )
        
        assert response.status_code == 200
        assert "Error de validación" in response.text
    finally:
        app.dependency_overrides.clear()


def test_create_client_conflict_error():
    """Test POST /admin-ui/clients with duplicate code"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.create_client.return_value = APIResult(
        ok=False,
        error_type=ErrorType.CONFLICT,
        status=409,
        detail="Client already exists"
    )
    mock_client.get_clients.return_value = APIResult(ok=True, data=[], status=200)
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.post(
            "/admin-ui/clients",
            auth=("admin", "admin123"),
            data={"code": "CLI001", "name": "Test"}
        )
        
        assert response.status_code == 200
        assert "Conflicto" in response.text
    finally:
        app.dependency_overrides.clear()


def test_edit_client_form_success():
    """Test GET /admin-ui/clients/{code}/edit loads client"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_client_detail.return_value = APIResult(
        ok=True,
        data={
            "code": "CLI001",
            "name": "Test Client",
            "contact_email": "test@example.com",
            "terminology": {
                "unit_terms": "Unidad",
                "group_terms": "Grupo",
                "program_terms": "Programa"
            }
        },
        status=200
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get(
            "/admin-ui/clients/CLI001/edit",
            auth=("admin", "admin123")
        )
        
        assert response.status_code == 200
        assert "Test Client" in response.text
        assert "CLI001" in response.text
    finally:
        app.dependency_overrides.clear()


def test_edit_client_form_not_found():
    """Test GET /admin-ui/clients/{code}/edit with non-existent client"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_client_detail.return_value = APIResult(
        ok=False,
        error_type=ErrorType.NOT_FOUND,
        status=404,
        detail="Not found"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get(
            "/admin-ui/clients/NOTFOUND/edit",
            auth=("admin", "admin123"),
            follow_redirects=False
        )
        
        assert response.status_code == 303  # Redirect
        assert "/admin-ui/clients" in response.headers["location"]
        assert "error=" in response.headers["location"]
    finally:
        app.dependency_overrides.clear()


def test_update_client_success():
    """Test POST /admin-ui/clients/{code}/edit updates client"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.update_client.return_value = APIResult(ok=True, data={}, status=200)
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.post(
            "/admin-ui/clients/CLI001/edit",
            auth=("admin", "admin123"),
            data={
                "name": "Updated Name",
                "contact_email": "new@example.com"
            },
            follow_redirects=False
        )
        
        assert response.status_code == 303
        assert "/admin-ui/clients" in response.headers["location"]
        assert "success=" in response.headers["location"]
        mock_client.update_client.assert_called_once()
    finally:
        app.dependency_overrides.clear()


def test_update_client_validation_error():
    """Test POST /admin-ui/clients/{code}/edit with validation error"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.update_client.return_value = APIResult(
        ok=False,
        error_type=ErrorType.VALIDATION,
        status=422,
        detail="Invalid data"
    )
    # Template needs terminology even when showing error
    mock_client.get_client_detail.return_value = APIResult(
        ok=True,
        data={
            "code": "CLI001",
            "name": "Test",
            "terminology": {"unit_terms": "Unidad", "group_terms": "Grupo", "program_terms": "Programa"}
        },
        status=200
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.post(
            "/admin-ui/clients/CLI001/edit",
            auth=("admin", "admin123"),
            data={"name": ""}
        )
        
        assert response.status_code == 200
        assert "Error de validación" in response.text
    finally:
        app.dependency_overrides.clear()


def test_delete_client_success():
    """Test POST /admin-ui/clients/{code}/delete removes client"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.delete_client.return_value = APIResult(ok=True, status=204)
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.post(
            "/admin-ui/clients/CLI001/delete",
            auth=("admin", "admin123"),
            follow_redirects=False
        )
        
        assert response.status_code == 303
        assert "/admin-ui/clients" in response.headers["location"]
        assert "success=" in response.headers["location"]
        mock_client.delete_client.assert_called_once_with("CLI001")
    finally:
        app.dependency_overrides.clear()


def test_delete_client_not_found():
    """Test POST /admin-ui/clients/{code}/delete with non-existent client"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.delete_client.return_value = APIResult(
        ok=False,
        error_type=ErrorType.NOT_FOUND,
        status=404,
        detail="Not found"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.post(
            "/admin-ui/clients/NOTFOUND/delete",
            auth=("admin", "admin123"),
            follow_redirects=False
        )
        
        assert response.status_code == 303
        assert "error=" in response.headers["location"]
        # URL encoding might convert spaces to %20 or +
        location_lower = response.headers["location"].lower()
        assert "encontrado" in location_lower or "not%20found" in location_lower
    finally:
        app.dependency_overrides.clear()


def test_delete_client_conflict():
    """Test POST /admin-ui/clients/{code}/delete with fields dependency"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.delete_client.return_value = APIResult(
        ok=False,
        error_type=ErrorType.CONFLICT,
        status=409,
        detail="Client has fields"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.post(
            "/admin-ui/clients/CLI001/delete",
            auth=("admin", "admin123"),
            follow_redirects=False
        )
        
        assert response.status_code == 303
        assert "error=" in response.headers["location"]
        assert "campos" in response.headers["location"].lower()
    finally:
        app.dependency_overrides.clear()


# =====================================================
# TEST: Fields CRUD operations - Phase 3.A
# =====================================================

def test_create_field_success():
    """Test POST /admin-ui/fields creates field successfully"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.create_field.return_value = APIResult(ok=True, data={}, status=201)
    mock_client.get_fields.return_value = APIResult(ok=True, data={"fields": [], "clients": []}, status=200)  # For error path
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.post(
            "/admin-ui/fields",
            auth=("admin", "admin123"),
            data={
                "client_code": "CLI001",
                "field_code": "FLD001",
                "name": "Test Field",
                "size_ha": 10.5,
                "timezone": "America/Santiago"
            },
            follow_redirects=False
        )
        
        assert response.status_code == 303
        assert "/admin-ui/fields" in response.headers["location"]
        assert "success=" in response.headers["location"]
        mock_client.create_field.assert_called_once()
    finally:
        app.dependency_overrides.clear()


def test_create_field_validation_error():
    """Test POST /admin-ui/fields with validation error"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.create_field.return_value = APIResult(
        ok=False,
        error_type=ErrorType.VALIDATION,
        status=422,
        detail="Invalid field code"
    )
    mock_client.get_fields.return_value = APIResult(
        ok=True,
        data={"fields": [], "clients": []},
        status=200
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.post(
            "/admin-ui/fields",
            auth=("admin", "admin123"),
            data={"client_code": "CLI001", "field_code": "invalid!", "name": "Test"}
        )
        
        assert response.status_code == 200
        assert "Error de validación" in response.text
    finally:
        app.dependency_overrides.clear()


def test_edit_field_form_success():
    """Test GET /admin-ui/fields/{client}/{field}/edit loads field"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_field_detail.return_value = APIResult(
        ok=True,
        data={
            "client": {
                "code": "CLI001",
                "name": "Test Client"
            },
            "code": "FLD001",
            "name": "Test Field",
            "size_ha": 10.5,
            "location": "Test Location",
            "location_lat": -33.4569,
            "location_lng": -70.6483,
            "timezone": "America/Santiago",
            "active": True,
            "icc_credentials": {
                "host": "192.168.1.100",
                "port": 5432,
                "dbname": "iccpro",
                "user": "iccuser"
            },
            "nomenclature": {
                "aliases": "test alias 1, test alias 2",
                "units_text": "E11:11,once",
                "groups_text": "450:cuatrocientos cincuenta"
            }
        },
        status=200
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get(
            "/admin-ui/fields/CLI001/FLD001/edit",
            auth=("admin", "admin123")
        )
        
        assert response.status_code == 200
        assert "Test Field" in response.text
        assert "FLD001" in response.text
    finally:
        app.dependency_overrides.clear()


def test_edit_field_form_not_found():
    """Test GET /admin-ui/fields/{client}/{field}/edit with non-existent field"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_field_detail.return_value = APIResult(
        ok=False,
        error_type=ErrorType.NOT_FOUND,
        status=404,
        detail="Not found"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get(
            "/admin-ui/fields/CLI001/NOTFOUND/edit",
            auth=("admin", "admin123"),
            follow_redirects=False
        )
        
        assert response.status_code == 303
        assert "/admin-ui/fields" in response.headers["location"]
        assert "error=" in response.headers["location"]
    finally:
        app.dependency_overrides.clear()


def test_update_field_success():
    """Test POST /admin-ui/fields/{client}/{field}/edit updates field"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.update_field.return_value = APIResult(ok=True, data={}, status=200)
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.post(
            "/admin-ui/fields/CLI001/FLD001/edit",
            auth=("admin", "admin123"),
            data={
                "name": "Updated Field",
                "size_ha": 15.0,
                "timezone": "America/Santiago"
            },
            follow_redirects=False
        )
        
        assert response.status_code == 303
        assert "/admin-ui/fields" in response.headers["location"]
        assert "success=" in response.headers["location"]
        mock_client.update_field.assert_called_once()
    finally:
        app.dependency_overrides.clear()


def test_delete_field_success():
    """Test POST /admin-ui/fields/{client}/{field}/delete removes field"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.delete_field.return_value = APIResult(ok=True, status=204)
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.post(
            "/admin-ui/fields/CLI001/FLD001/delete",
            auth=("admin", "admin123"),
            follow_redirects=False
        )
        
        assert response.status_code == 303
        assert "/admin-ui/fields" in response.headers["location"]
        assert "success=" in response.headers["location"]
        mock_client.delete_field.assert_called_once_with("CLI001", "FLD001")
    finally:
        app.dependency_overrides.clear()


def test_download_field_config_success():
    """Test GET /admin-ui/fields/{client}/{field}/config downloads .env file"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_field_agent_config.return_value = APIResult(
        ok=True,
        data="FIELD_CODE=FLD001\nCLIENT_CODE=CLI001\n",
        status=200
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get(
            "/admin-ui/fields/CLI001/FLD001/config",
            auth=("admin", "admin123")
        )
        
        assert response.status_code == 200
        assert "FIELD_CODE=FLD001" in response.text
        assert "Content-Disposition" in response.headers
        assert "CLI001_FLD001.env" in response.headers["Content-Disposition"]
    finally:
        app.dependency_overrides.clear()


def test_download_field_config_not_found():
    """Test GET /admin-ui/fields/{client}/{field}/config with non-existent config"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_field_agent_config.return_value = APIResult(
        ok=False,
        error_type=ErrorType.NOT_FOUND,
        status=404,
        detail="Config not found"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get(
            "/admin-ui/fields/CLI001/FLD001/config",
            auth=("admin", "admin123"),
            follow_redirects=False
        )
        
        assert response.status_code == 303
        assert "/admin-ui/fields" in response.headers["location"]
        assert "error=" in response.headers["location"]
    finally:
        app.dependency_overrides.clear()
