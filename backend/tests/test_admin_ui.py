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
