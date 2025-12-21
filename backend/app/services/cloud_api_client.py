"""
Cloud API Client
HTTP client for communicating with the Cloud API admin endpoints.
NO direct database access - all data comes from HTTP calls.
"""
import httpx
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class ErrorType(str, Enum):
    """Error types for standardized error handling"""
    UNAUTHORIZED = "unauthorized"
    TIMEOUT = "timeout"
    NETWORK = "network"
    SERVER_ERROR = "server_error"
    NOT_FOUND = "not_found"
    VALIDATION = "validation"
    UNKNOWN = "unknown"


@dataclass
class APIResult:
    """Standardized result object for all API calls"""
    ok: bool
    data: Optional[Any] = None
    error_type: Optional[ErrorType] = None
    status: Optional[int] = None
    detail: Optional[str] = None


class CloudAPIClient:
    """
    HTTP client for Cloud API admin endpoints.
    
    Features:
    - Bearer token authentication
    - 10s timeout
    - Retry logic (max 2 retries with 1s delay for GET requests)
    - Normalized error handling
    """
    
    def __init__(self, base_url: str, admin_token: str, timeout: int = 10, max_retries: int = 2):
        """
        Initialize Cloud API client.
        
        Args:
            base_url: Base URL of Cloud API (e.g., http://localhost:8001)
            admin_token: Bearer token for admin endpoints
            timeout: Request timeout in seconds (default: 10)
            max_retries: Maximum retries for GET requests (default: 2)
        """
        self.base_url = base_url.rstrip('/')
        self.admin_token = admin_token
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        retry: bool = True,
        **kwargs
    ) -> APIResult:
        """
        Make HTTP request with retry logic and error normalization.
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint (e.g., /admin/clients)
            retry: Whether to retry on failure (only for GET)
            **kwargs: Additional arguments for httpx request
        
        Returns:
            APIResult with normalized response or error
        """
        url = f"{self.base_url}{endpoint}"
        attempts = self.max_retries + 1 if (retry and method == "GET") else 1
        
        for attempt in range(attempts):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.request(
                        method=method,
                        url=url,
                        headers=self.headers,
                        **kwargs
                    )
                    
                    # Handle successful responses
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            return APIResult(ok=True, data=data, status=200)
                        except Exception:
                            return APIResult(ok=True, data=None, status=200)
                    
                    # Handle specific error cases
                    if response.status_code == 401:
                        return APIResult(
                            ok=False,
                            error_type=ErrorType.UNAUTHORIZED,
                            status=401,
                            detail="Cloud API authentication failed"
                        )
                    
                    if response.status_code == 404:
                        return APIResult(
                            ok=False,
                            error_type=ErrorType.NOT_FOUND,
                            status=404,
                            detail="Resource not found"
                        )
                    
                    if response.status_code == 422:
                        return APIResult(
                            ok=False,
                            error_type=ErrorType.VALIDATION,
                            status=422,
                            detail="Validation error"
                        )
                    
                    if response.status_code >= 500:
                        return APIResult(
                            ok=False,
                            error_type=ErrorType.SERVER_ERROR,
                            status=response.status_code,
                            detail="Cloud API server error"
                        )
                    
                    # Other client errors
                    return APIResult(
                        ok=False,
                        error_type=ErrorType.UNKNOWN,
                        status=response.status_code,
                        detail=f"Unexpected status: {response.status_code}"
                    )
                    
            except httpx.TimeoutException:
                if attempt < attempts - 1:
                    time.sleep(1)  # Wait 1s before retry
                    continue
                return APIResult(
                    ok=False,
                    error_type=ErrorType.TIMEOUT,
                    status=None,
                    detail="Cloud API request timeout"
                )
            
            except (httpx.NetworkError, httpx.ConnectError) as e:
                if attempt < attempts - 1:
                    time.sleep(1)  # Wait 1s before retry
                    continue
                return APIResult(
                    ok=False,
                    error_type=ErrorType.NETWORK,
                    status=None,
                    detail="Cloud API unavailable"
                )
            
            except Exception as e:
                return APIResult(
                    ok=False,
                    error_type=ErrorType.UNKNOWN,
                    status=None,
                    detail=f"Unexpected error: {str(e)}"
                )
        
        # Should never reach here, but just in case
        return APIResult(
            ok=False,
            error_type=ErrorType.UNKNOWN,
            status=None,
            detail="Request failed after retries"
        )
    
    # =====================================================
    # Admin endpoints for listing resources
    # =====================================================
    
    def get_clients(self) -> APIResult:
        """
        Get all clients from Cloud API.
        
        Returns:
            APIResult with list of clients or error
        """
        return self._make_request("GET", "/admin/clients")
    
    def get_fields(self) -> APIResult:
        """
        Get all fields from Cloud API.
        
        Returns:
            APIResult with list of fields or error
        """
        return self._make_request("GET", "/admin/fields")
    
    def get_whatsapp_users(self) -> APIResult:
        """
        Get all WhatsApp users from Cloud API.
        
        Returns:
            APIResult with list of WhatsApp users or error
        """
        return self._make_request("GET", "/admin/whatsapp-users")


def get_cloud_api_client(base_url: str, admin_token: str) -> CloudAPIClient:
    """
    Dependency function for FastAPI to inject CloudAPIClient.
    
    Args:
        base_url: Cloud API base URL from settings
        admin_token: Admin token from settings
    
    Returns:
        Configured CloudAPIClient instance
    """
    return CloudAPIClient(base_url=base_url, admin_token=admin_token)
