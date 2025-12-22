"""
Integration-style tests for Cloud API failure scenarios
Tests timeout, 500 errors, 401 errors for each entity type
"""
from unittest.mock import Mock
from fastapi.testclient import TestClient
from app.main import app
from app.services.cloud_api_client import CloudAPIClient, APIResult, ErrorType
from app.admin_ui.router import get_cloud_client

client = TestClient(app)


# =====================================================
# Clients - Failure Scenarios
# =====================================================

def test_list_clients_with_timeout():
    """Test GET /admin-ui/clients handles timeout gracefully"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_clients.return_value = APIResult(
        ok=False,
        error_type=ErrorType.TIMEOUT,
        status=None,
        detail="Request timeout"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get("/admin-ui/clients", auth=("admin", "admin123"))
        
        assert response.status_code == 200
        assert "Cloud API no disponible" in response.text
        assert "clients" in response.text  # Should still render page
    finally:
        app.dependency_overrides.clear()


def test_list_clients_with_500():
    """Test GET /admin-ui/clients handles server error gracefully"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_clients.return_value = APIResult(
        ok=False,
        error_type=ErrorType.SERVER_ERROR,
        status=500,
        detail="Internal server error"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get("/admin-ui/clients", auth=("admin", "admin123"))
        
        assert response.status_code == 200
        assert "Error en el servidor" in response.text
    finally:
        app.dependency_overrides.clear()


def test_list_clients_with_401():
    """Test GET /admin-ui/clients handles unauthorized gracefully"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_clients.return_value = APIResult(
        ok=False,
        error_type=ErrorType.UNAUTHORIZED,
        status=401,
        detail="Invalid token"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get("/admin-ui/clients", auth=("admin", "admin123"))
        
        assert response.status_code == 200
        assert "autenticación" in response.text.lower()
    finally:
        app.dependency_overrides.clear()


def test_edit_client_form_with_network_error():
    """Test GET /admin-ui/clients/{code}/edit handles network error"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_client_detail.return_value = APIResult(
        ok=False,
        error_type=ErrorType.NETWORK,
        status=None,
        detail="Network unreachable"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get("/admin-ui/clients/CLI001/edit", auth=("admin", "admin123"))
        
        assert response.status_code == 200
        assert "no disponible" in response.text.lower()
    finally:
        app.dependency_overrides.clear()


# =====================================================
# Fields - Failure Scenarios
# =====================================================

def test_list_fields_with_timeout():
    """Test GET /admin-ui/fields handles timeout gracefully"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_fields.return_value = APIResult(
        ok=False,
        error_type=ErrorType.TIMEOUT,
        status=None,
        detail="Request timeout"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get("/admin-ui/fields", auth=("admin", "admin123"))
        
        assert response.status_code == 200
        assert "Cloud API no disponible" in response.text
    finally:
        app.dependency_overrides.clear()


def test_list_fields_with_500():
    """Test GET /admin-ui/fields handles server error gracefully"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_fields.return_value = APIResult(
        ok=False,
        error_type=ErrorType.SERVER_ERROR,
        status=500,
        detail="Internal server error"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get("/admin-ui/fields", auth=("admin", "admin123"))
        
        assert response.status_code == 200
        assert "Error en el servidor" in response.text
    finally:
        app.dependency_overrides.clear()


def test_edit_field_form_with_401():
    """Test GET /admin-ui/fields/{client}/{field}/edit handles unauthorized"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_field_detail.return_value = APIResult(
        ok=False,
        error_type=ErrorType.UNAUTHORIZED,
        status=401,
        detail="Invalid token"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get(
            "/admin-ui/fields/CLI001/FLD001/edit",
            auth=("admin", "admin123")
        )
        
        assert response.status_code == 200
        assert "autenticación" in response.text.lower()
    finally:
        app.dependency_overrides.clear()


# =====================================================
# WhatsApp Users - Failure Scenarios
# =====================================================

def test_list_whatsapp_users_with_timeout():
    """Test GET /admin-ui/whatsapp-users handles timeout gracefully"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_whatsapp_users.return_value = APIResult(
        ok=False,
        error_type=ErrorType.TIMEOUT,
        status=None,
        detail="Request timeout"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get("/admin-ui/whatsapp-users", auth=("admin", "admin123"))
        
        assert response.status_code == 200
        assert "Cloud API no disponible" in response.text
    finally:
        app.dependency_overrides.clear()


def test_list_whatsapp_users_with_500():
    """Test GET /admin-ui/whatsapp-users handles server error gracefully"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_whatsapp_users.return_value = APIResult(
        ok=False,
        error_type=ErrorType.SERVER_ERROR,
        status=500,
        detail="Internal server error"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get("/admin-ui/whatsapp-users", auth=("admin", "admin123"))
        
        assert response.status_code == 200
        assert "Error en el servidor" in response.text
    finally:
        app.dependency_overrides.clear()


def test_edit_whatsapp_user_with_network_error():
    """Test GET /admin-ui/whatsapp-users/{id}/edit handles network error"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_whatsapp_user.return_value = APIResult(
        ok=False,
        error_type=ErrorType.NETWORK,
        status=None,
        detail="Network unreachable"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get(
            "/admin-ui/whatsapp-users/uuid-123/edit",
            auth=("admin", "admin123")
        )
        
        assert response.status_code == 200
        assert "no disponible" in response.text.lower()
    finally:
        app.dependency_overrides.clear()


def test_edit_whatsapp_user_with_401():
    """Test GET /admin-ui/whatsapp-users/{id}/edit handles unauthorized"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_whatsapp_user.return_value = APIResult(
        ok=False,
        error_type=ErrorType.UNAUTHORIZED,
        status=401,
        detail="Invalid token"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get(
            "/admin-ui/whatsapp-users/uuid-123/edit",
            auth=("admin", "admin123")
        )
        
        assert response.status_code == 200
        assert "autenticación" in response.text.lower()
    finally:
        app.dependency_overrides.clear()
