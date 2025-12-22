"""
Tests for WhatsApp Users CRUD operations in Admin UI
Phase 3.C
"""
from unittest.mock import Mock
from fastapi.testclient import TestClient
from app.main import app
from app.services.cloud_api_client import CloudAPIClient, APIResult, ErrorType
from app.admin_ui.router import get_cloud_client

client = TestClient(app)


# =====================================================
# WhatsApp Users CRUD Tests
# =====================================================

def test_create_whatsapp_user_success():
    """Test POST /admin-ui/whatsapp-users creates user"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.create_whatsapp_user.return_value = APIResult(
        ok=True,
        data={"id": "uuid-123", "phone_number": "+56912345678"},
        status=201
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.post(
            "/admin-ui/whatsapp-users",
            data={
                "phone_number": "+56912345678",
                "display_name": "Test User",
                "field_ids": "1,2,3"
            },
            auth=("admin", "admin123"),
            follow_redirects=False
        )
        
        assert response.status_code == 303
        assert "/admin-ui/whatsapp-users" in response.headers["location"]
        assert "success=" in response.headers["location"]
        
        # Verify API call
        mock_client.create_whatsapp_user.assert_called_once()
        call_data = mock_client.create_whatsapp_user.call_args[0][0]
        assert call_data["phone_number"] == "+56912345678"
        assert call_data["display_name"] == "Test User"
        assert call_data["field_ids"] == [1, 2, 3]
    finally:
        app.dependency_overrides.clear()


def test_create_whatsapp_user_without_auth():
    """Test POST /admin-ui/whatsapp-users requires auth"""
    response = client.post(
        "/admin-ui/whatsapp-users",
        data={"phone_number": "+56912345678"}
    )
    assert response.status_code == 401


def test_create_whatsapp_user_conflict():
    """Test POST /admin-ui/whatsapp-users with duplicate phone"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.create_whatsapp_user.return_value = APIResult(
        ok=False,
        error_type=ErrorType.CONFLICT,
        status=409,
        detail="User with this phone number already exists"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.post(
            "/admin-ui/whatsapp-users",
            data={
                "phone_number": "+56912345678",
                "field_ids": ""
            },
            auth=("admin", "admin123"),
            follow_redirects=False
        )
        
        assert response.status_code == 303
        assert "error=" in response.headers["location"]
    finally:
        app.dependency_overrides.clear()


def test_create_whatsapp_user_validation_error():
    """Test POST /admin-ui/whatsapp-users with invalid data"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.create_whatsapp_user.return_value = APIResult(
        ok=False,
        error_type=ErrorType.VALIDATION,
        status=422,
        detail="Invalid phone number format"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.post(
            "/admin-ui/whatsapp-users",
            data={
                "phone_number": "invalid",
                "field_ids": ""
            },
            auth=("admin", "admin123"),
            follow_redirects=False
        )
        
        assert response.status_code == 303
        assert "error=" in response.headers["location"]
    finally:
        app.dependency_overrides.clear()


def test_edit_whatsapp_user_form_success():
    """Test GET /admin-ui/whatsapp-users/{id}/edit loads user"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_whatsapp_user.return_value = APIResult(
        ok=True,
        data={
            "id": "uuid-123",
            "phone_number": "+56912345678",
            "display_name": "Test User",
            "is_active": True,
            "field_ids": [1, 2]
        },
        status=200
    )
    mock_client.get_fields.return_value = APIResult(
        ok=True,
        data=[
            {"id": 1, "code": "FLD001", "name": "Field 1", "client": {"code": "CLI001"}},
            {"id": 2, "code": "FLD002", "name": "Field 2", "client": {"code": "CLI001"}},
            {"id": 3, "code": "FLD003", "name": "Field 3", "client": {"code": "CLI002"}}
        ],
        status=200
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get(
            "/admin-ui/whatsapp-users/uuid-123/edit",
            auth=("admin", "admin123")
        )
        
        assert response.status_code == 200
        assert "+56912345678" in response.text
        assert "Test User" in response.text
    finally:
        app.dependency_overrides.clear()


def test_edit_whatsapp_user_form_not_found():
    """Test GET /admin-ui/whatsapp-users/{id}/edit with non-existent user"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.get_whatsapp_user.return_value = APIResult(
        ok=False,
        error_type=ErrorType.NOT_FOUND,
        status=404,
        detail="User not found"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.get(
            "/admin-ui/whatsapp-users/nonexistent-uuid/edit",
            auth=("admin", "admin123"),
            follow_redirects=False
        )
        
        assert response.status_code == 303
        assert "/admin-ui/whatsapp-users" in response.headers["location"]
        assert "error=" in response.headers["location"]
    finally:
        app.dependency_overrides.clear()


def test_update_whatsapp_user_success():
    """Test POST /admin-ui/whatsapp-users/{id}/edit updates user"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.update_whatsapp_user.return_value = APIResult(
        ok=True,
        data={"id": "uuid-123", "phone_number": "+56912345678"},
        status=200
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.post(
            "/admin-ui/whatsapp-users/uuid-123/edit",
            data={
                "display_name": "Updated Name",
                "is_active": "true",
                "field_ids": "1,2"
            },
            auth=("admin", "admin123"),
            follow_redirects=False
        )
        
        assert response.status_code == 303
        assert "/admin-ui/whatsapp-users" in response.headers["location"]
        assert "success=" in response.headers["location"]
        
        # Verify API call
        mock_client.update_whatsapp_user.assert_called_once_with(
            "uuid-123",
            {
                "display_name": "Updated Name",
                "is_active": True,
                "field_ids": [1, 2]
            }
        )
    finally:
        app.dependency_overrides.clear()


def test_update_whatsapp_user_validation_error():
    """Test POST /admin-ui/whatsapp-users/{id}/edit with validation error"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.update_whatsapp_user.return_value = APIResult(
        ok=False,
        error_type=ErrorType.VALIDATION,
        status=422,
        detail="Invalid field IDs"
    )
    mock_client.get_whatsapp_user.return_value = APIResult(
        ok=True,
        data={
            "id": "uuid-123",
            "phone_number": "+56912345678",
            "display_name": "Test User",
            "is_active": True,
            "field_ids": []
        },
        status=200
    )
    mock_client.get_fields.return_value = APIResult(
        ok=True,
        data=[],
        status=200
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.post(
            "/admin-ui/whatsapp-users/uuid-123/edit",
            data={
                "display_name": "Test",
                "is_active": "true",
                "field_ids": "1,2"
            },
            auth=("admin", "admin123")
        )
        
        assert response.status_code == 200
        assert "error_message" in response.text or "Invalid field IDs" in response.text
    finally:
        app.dependency_overrides.clear()


def test_delete_whatsapp_user_success():
    """Test POST /admin-ui/whatsapp-users/{id}/delete soft deletes user"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.delete_whatsapp_user.return_value = APIResult(
        ok=True,
        status=204
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.post(
            "/admin-ui/whatsapp-users/uuid-123/delete",
            auth=("admin", "admin123"),
            follow_redirects=False
        )
        
        assert response.status_code == 303
        assert "/admin-ui/whatsapp-users" in response.headers["location"]
        assert "success=" in response.headers["location"]
        
        mock_client.delete_whatsapp_user.assert_called_once_with("uuid-123")
    finally:
        app.dependency_overrides.clear()


def test_delete_whatsapp_user_not_found():
    """Test POST /admin-ui/whatsapp-users/{id}/delete with non-existent user"""
    mock_client = Mock(spec=CloudAPIClient)
    mock_client.delete_whatsapp_user.return_value = APIResult(
        ok=False,
        error_type=ErrorType.NOT_FOUND,
        status=404,
        detail="User not found"
    )
    
    app.dependency_overrides[get_cloud_client] = lambda: mock_client
    
    try:
        response = client.post(
            "/admin-ui/whatsapp-users/nonexistent-uuid/delete",
            auth=("admin", "admin123"),
            follow_redirects=False
        )
        
        assert response.status_code == 303
        assert "/admin-ui/whatsapp-users" in response.headers["location"]
        assert "error=" in response.headers["location"]
    finally:
        app.dependency_overrides.clear()
