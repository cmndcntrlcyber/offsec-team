"""
Base API client for cybersecurity AI workflow integration.

This module provides a foundational HTTP client with authentication,
retry logic, and error handling for platform API communications.
"""

import json
import time
import logging
from typing import Any, Dict, List, Optional, Union, Tuple
from urllib.parse import urljoin, urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import ssl
import websocket
from datetime import datetime, timedelta

from ..security.auth import SecurityManager, AuthenticationError
from ..data_models.base_models import BaseResponse, ErrorResponse, SuccessResponse


class APIError(Exception):
    """Base exception for API-related errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class ConnectionError(APIError):
    """Exception raised for connection-related errors."""
    pass


class TimeoutError(APIError):
    """Exception raised for timeout-related errors."""
    pass


class AuthenticationError(APIError):
    """Exception raised for authentication-related errors."""
    pass


class BaseAPIClient:
    """
    Base API client providing common HTTP operations with authentication,
    retry logic, and error handling for platform integrations.
    """
    
    def __init__(self,
                 base_url: str,
                 api_key: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 timeout: int = 30,
                 max_retries: int = 3,
                 verify_ssl: bool = True,
                 client_cert: Optional[Tuple[str, str]] = None,
                 headers: Optional[Dict[str, str]] = None):
        """
        Initialize the base API client.
        
        Args:
            base_url: Base URL for API endpoints
            api_key: API key for authentication
            username: Username for basic authentication
            password: Password for basic authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            verify_ssl: Whether to verify SSL certificates
            client_cert: Client certificate (cert_file, key_file) tuple
            headers: Additional headers to include in requests
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.username = username
        self.password = password
        self.timeout = timeout
        self.max_retries = max_retries
        self.verify_ssl = verify_ssl
        self.client_cert = client_cert
        self.custom_headers = headers or {}
        
        # Setup session with retry strategy
        self.session = self._create_session()
        
        # JWT token storage
        self.jwt_token = None
        self.token_expires_at = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        
        # Connection health tracking
        self.last_successful_request = None
        self.consecutive_failures = 0
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy and authentication."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'User-Agent': 'CybersecAIWorkflow-Client/1.0',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Add custom headers
        if self.custom_headers:
            session.headers.update(self.custom_headers)
        
        # Configure authentication
        if self.api_key:
            session.headers['Authorization'] = f'Bearer {self.api_key}'
        elif self.username and self.password:
            session.auth = (self.username, self.password)
        
        # SSL configuration
        if not self.verify_ssl:
            session.verify = False
            # Disable SSL warnings
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        if self.client_cert:
            session.cert = self.client_cert
        
        return session
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        if endpoint.startswith(('http://', 'https://')):
            return endpoint
        return urljoin(self.base_url + '/', endpoint.lstrip('/'))
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle HTTP response and convert to standard format."""
        try:
            # Update connection health tracking
            if response.status_code < 400:
                self.last_successful_request = datetime.utcnow()
                self.consecutive_failures = 0
            else:
                self.consecutive_failures += 1
            
            # Try to parse JSON response
            try:
                data = response.json()
            except ValueError:
                data = {"message": response.text or "No response body"}
            
            # Handle different status codes
            if 200 <= response.status_code < 300:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": data,
                    "headers": dict(response.headers)
                }
            elif response.status_code == 401:
                raise AuthenticationError(
                    "Authentication failed", 
                    status_code=response.status_code,
                    response_data=data
                )
            elif response.status_code == 403:
                raise APIError(
                    "Access forbidden", 
                    status_code=response.status_code,
                    response_data=data
                )
            elif response.status_code == 404:
                raise APIError(
                    "Resource not found", 
                    status_code=response.status_code,
                    response_data=data
                )
            elif response.status_code == 429:
                raise APIError(
                    "Rate limit exceeded", 
                    status_code=response.status_code,
                    response_data=data
                )
            elif response.status_code >= 500:
                raise APIError(
                    f"Server error: {data.get('message', 'Unknown error')}", 
                    status_code=response.status_code,
                    response_data=data
                )
            else:
                raise APIError(
                    f"HTTP {response.status_code}: {data.get('message', 'Unknown error')}", 
                    status_code=response.status_code,
                    response_data=data
                )
                
        except requests.exceptions.RequestException as e:
            self.consecutive_failures += 1
            self.logger.error(f"Request failed: {str(e)}")
            raise ConnectionError(f"Request failed: {str(e)}")
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Perform GET request.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers
            
        Returns:
            Response data dictionary
            
        Raises:
            APIError: If request fails
        """
        url = self._build_url(endpoint)
        request_headers = dict(self.session.headers)
        if headers:
            request_headers.update(headers)
        
        try:
            self.logger.debug(f"GET {url}")
            response = self.session.get(
                url, 
                params=params, 
                headers=request_headers,
                timeout=self.timeout
            )
            return self._handle_response(response)
            
        except requests.exceptions.Timeout:
            self.consecutive_failures += 1
            raise TimeoutError(f"Request timeout after {self.timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            self.consecutive_failures += 1
            raise ConnectionError(f"Connection failed: {str(e)}")
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
             json_data: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Perform POST request.
        
        Args:
            endpoint: API endpoint
            data: Form data
            json_data: JSON data
            headers: Additional headers
            
        Returns:
            Response data dictionary
            
        Raises:
            APIError: If request fails
        """
        url = self._build_url(endpoint)
        request_headers = dict(self.session.headers)
        if headers:
            request_headers.update(headers)
        
        try:
            self.logger.debug(f"POST {url}")
            response = self.session.post(
                url,
                data=data,
                json=json_data,
                headers=request_headers,
                timeout=self.timeout
            )
            return self._handle_response(response)
            
        except requests.exceptions.Timeout:
            self.consecutive_failures += 1
            raise TimeoutError(f"Request timeout after {self.timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            self.consecutive_failures += 1
            raise ConnectionError(f"Connection failed: {str(e)}")
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
            json_data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Perform PUT request.
        
        Args:
            endpoint: API endpoint
            data: Form data
            json_data: JSON data
            headers: Additional headers
            
        Returns:
            Response data dictionary
            
        Raises:
            APIError: If request fails
        """
        url = self._build_url(endpoint)
        request_headers = dict(self.session.headers)
        if headers:
            request_headers.update(headers)
        
        try:
            self.logger.debug(f"PUT {url}")
            response = self.session.put(
                url,
                data=data,
                json=json_data,
                headers=request_headers,
                timeout=self.timeout
            )
            return self._handle_response(response)
            
        except requests.exceptions.Timeout:
            self.consecutive_failures += 1
            raise TimeoutError(f"Request timeout after {self.timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            self.consecutive_failures += 1
            raise ConnectionError(f"Connection failed: {str(e)}")
    
    def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Perform DELETE request.
        
        Args:
            endpoint: API endpoint
            headers: Additional headers
            
        Returns:
            Response data dictionary
            
        Raises:
            APIError: If request fails
        """
        url = self._build_url(endpoint)
        request_headers = dict(self.session.headers)
        if headers:
            request_headers.update(headers)
        
        try:
            self.logger.debug(f"DELETE {url}")
            response = self.session.delete(
                url,
                headers=request_headers,
                timeout=self.timeout
            )
            return self._handle_response(response)
            
        except requests.exceptions.Timeout:
            self.consecutive_failures += 1
            raise TimeoutError(f"Request timeout after {self.timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            self.consecutive_failures += 1
            raise ConnectionError(f"Connection failed: {str(e)}")
    
    def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
              json_data: Optional[Dict[str, Any]] = None,
              headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Perform PATCH request.
        
        Args:
            endpoint: API endpoint
            data: Form data
            json_data: JSON data
            headers: Additional headers
            
        Returns:
            Response data dictionary
            
        Raises:
            APIError: If request fails
        """
        url = self._build_url(endpoint)
        request_headers = dict(self.session.headers)
        if headers:
            request_headers.update(headers)
        
        try:
            self.logger.debug(f"PATCH {url}")
            response = self.session.patch(
                url,
                data=data,
                json=json_data,
                headers=request_headers,
                timeout=self.timeout
            )
            return self._handle_response(response)
            
        except requests.exceptions.Timeout:
            self.consecutive_failures += 1
            raise TimeoutError(f"Request timeout after {self.timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            self.consecutive_failures += 1
            raise ConnectionError(f"Connection failed: {str(e)}")
    
    def authenticate_jwt(self, login_endpoint: str = "/auth/login") -> bool:
        """
        Authenticate using username/password and obtain JWT token.
        
        Args:
            login_endpoint: Login endpoint URL
            
        Returns:
            True if authentication successful
            
        Raises:
            AuthenticationError: If authentication fails
        """
        if not (self.username and self.password):
            raise AuthenticationError("Username and password required for JWT authentication")
        
        try:
            response = self.post(login_endpoint, json_data={
                "username": self.username,
                "password": self.password
            })
            
            if response["success"]:
                token_data = response["data"]
                self.jwt_token = token_data.get("access_token") or token_data.get("token")
                
                # Calculate expiration
                expires_in = token_data.get("expires_in", 3600)  # Default 1 hour
                self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                
                # Update session headers
                self.session.headers['Authorization'] = f'Bearer {self.jwt_token}'
                
                self.logger.info("JWT authentication successful")
                return True
            else:
                raise AuthenticationError("JWT authentication failed")
                
        except APIError:
            raise
        except Exception as e:
            raise AuthenticationError(f"JWT authentication error: {str(e)}")
    
    def refresh_jwt_token(self, refresh_endpoint: str = "/auth/refresh") -> bool:
        """
        Refresh JWT token if it's about to expire.
        
        Args:
            refresh_endpoint: Token refresh endpoint
            
        Returns:
            True if token was refreshed
        """
        if not self.jwt_token or not self.token_expires_at:
            return False
        
        # Check if token expires within 5 minutes
        if datetime.utcnow() + timedelta(minutes=5) < self.token_expires_at:
            return False  # Token still valid
        
        try:
            response = self.post(refresh_endpoint, headers={
                'Authorization': f'Bearer {self.jwt_token}'
            })
            
            if response["success"]:
                token_data = response["data"]
                self.jwt_token = token_data.get("access_token") or token_data.get("token")
                
                # Calculate expiration
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                
                # Update session headers
                self.session.headers['Authorization'] = f'Bearer {self.jwt_token}'
                
                self.logger.info("JWT token refreshed")
                return True
            
        except Exception as e:
            self.logger.warning(f"Token refresh failed: {str(e)}")
        
        return False
    
    def health_check(self, endpoint: str = "/health") -> Dict[str, Any]:
        """
        Perform health check on the API.
        
        Args:
            endpoint: Health check endpoint
            
        Returns:
            Health check response
        """
        try:
            response = self.get(endpoint)
            return {
                "healthy": response["success"],
                "status_code": response["status_code"],
                "response_time": response.get("response_time"),
                "data": response.get("data", {})
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "consecutive_failures": self.consecutive_failures
            }
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get current connection status and health metrics.
        
        Returns:
            Connection status information
        """
        return {
            "base_url": self.base_url,
            "last_successful_request": self.last_successful_request.isoformat() if self.last_successful_request else None,
            "consecutive_failures": self.consecutive_failures,
            "jwt_token_active": bool(self.jwt_token),
            "jwt_token_expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None,
            "ssl_verification": self.verify_ssl,
            "timeout": self.timeout
        }
    
    def create_websocket_connection(self, endpoint: str, 
                                  on_message=None, on_error=None, on_close=None,
                                  headers: Optional[Dict[str, str]] = None) -> websocket.WebSocketApp:
        """
        Create a WebSocket connection.
        
        Args:
            endpoint: WebSocket endpoint
            on_message: Message callback function
            on_error: Error callback function  
            on_close: Close callback function
            headers: Additional headers
            
        Returns:
            WebSocket app instance
        """
        # Convert HTTP URL to WebSocket URL
        ws_url = self._build_url(endpoint)
        ws_url = ws_url.replace('http://', 'ws://').replace('https://', 'wss://')
        
        # Prepare headers
        ws_headers = {}
        if headers:
            ws_headers.update(headers)
        
        # Add authentication header if available
        if self.jwt_token:
            ws_headers['Authorization'] = f'Bearer {self.jwt_token}'
        elif self.api_key:
            ws_headers['Authorization'] = f'Bearer {self.api_key}'
        
        def on_ws_error(ws, error):
            self.logger.error(f"WebSocket error: {error}")
            if on_error:
                on_error(ws, error)
        
        def on_ws_close(ws, close_status_code, close_msg):
            self.logger.info(f"WebSocket closed: {close_status_code} - {close_msg}")
            if on_close:
                on_close(ws, close_status_code, close_msg)
        
        # Create WebSocket app
        ws = websocket.WebSocketApp(
            ws_url,
            header=ws_headers,
            on_message=on_message,
            on_error=on_ws_error,
            on_close=on_ws_close
        )
        
        return ws
    
    def close(self):
        """Close the HTTP session."""
        if self.session:
            self.session.close()
            self.logger.info("API client session closed")
