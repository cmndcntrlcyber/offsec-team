"""
Authentication and authorization utilities for cybersecurity AI workflow integration.

This module provides secure authentication mechanisms for platform integrations,
including API key management, JWT tokens, and role-based access control.
"""

import os
import time
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
import jwt
import bcrypt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64


class SecurityException(Exception):
    """Base exception for security-related errors."""
    pass


class AuthenticationError(SecurityException):
    """Exception raised for authentication failures."""
    pass


class AuthorizationError(SecurityException):
    """Exception raised for authorization failures."""
    pass


class TokenExpiredError(AuthenticationError):
    """Exception raised when a token has expired."""
    pass


class InvalidTokenError(AuthenticationError):
    """Exception raised when a token is invalid."""
    pass


class UserCredentials(BaseModel):
    """User credentials model."""
    
    username: str = Field(..., description="Username")
    password_hash: str = Field(..., description="Hashed password")
    salt: str = Field(..., description="Password salt")
    roles: List[str] = Field(default_factory=list, description="User roles")
    permissions: List[str] = Field(default_factory=list, description="User permissions")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    last_login: Optional[datetime] = Field(default=None, description="Last login timestamp")
    is_active: bool = Field(default=True, description="Whether user is active")
    failed_attempts: int = Field(default=0, description="Failed login attempts")
    locked_until: Optional[datetime] = Field(default=None, description="Account lock expiration")


class APIKey(BaseModel):
    """API key model."""
    
    key_id: str = Field(..., description="Unique key identifier")
    key_hash: str = Field(..., description="Hashed API key")
    name: str = Field(..., description="Human-readable key name")
    owner: str = Field(..., description="Key owner identifier")
    permissions: List[str] = Field(default_factory=list, description="Key permissions")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    expires_at: Optional[datetime] = Field(default=None, description="Expiration timestamp")
    last_used: Optional[datetime] = Field(default=None, description="Last usage timestamp")
    usage_count: int = Field(default=0, description="Number of times used")
    is_active: bool = Field(default=True, description="Whether key is active")
    allowed_ips: List[str] = Field(default_factory=list, description="Allowed IP addresses")


class TokenPayload(BaseModel):
    """JWT token payload model."""
    
    user_id: str = Field(..., description="User identifier")
    username: str = Field(..., description="Username")
    roles: List[str] = Field(default_factory=list, description="User roles")
    permissions: List[str] = Field(default_factory=list, description="User permissions")
    issued_at: int = Field(default_factory=lambda: int(time.time()), description="Issued at timestamp")
    expires_at: int = Field(..., description="Expiration timestamp")
    issuer: str = Field(default="cybersec-ai-workflow", description="Token issuer")
    audience: str = Field(default="platform-apis", description="Token audience")


class SecurityManager:
    """
    Security manager for authentication and authorization operations.
    Provides unified security services for all platform integrations.
    """
    
    def __init__(self, 
                 jwt_secret_key: Optional[str] = None,
                 jwt_algorithm: str = "HS256",
                 token_expiration_minutes: int = 60,
                 max_failed_attempts: int = 5,
                 lockout_duration_minutes: int = 30):
        """
        Initialize the security manager.
        
        Args:
            jwt_secret_key: Secret key for JWT signing (will be generated if not provided)
            jwt_algorithm: JWT signing algorithm
            token_expiration_minutes: JWT token expiration time in minutes
            max_failed_attempts: Maximum failed login attempts before lockout
            lockout_duration_minutes: Account lockout duration in minutes
        """
        self.jwt_secret_key = jwt_secret_key or self._generate_secret_key()
        self.jwt_algorithm = jwt_algorithm
        self.token_expiration_minutes = token_expiration_minutes
        self.max_failed_attempts = max_failed_attempts
        self.lockout_duration_minutes = lockout_duration_minutes
        
        # In-memory storage for demo purposes
        # In production, these would be stored in a secure database
        self.users: Dict[str, UserCredentials] = {}
        self.api_keys: Dict[str, APIKey] = {}
        self.revoked_tokens: set = set()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("SecurityManager")
    
    def _generate_secret_key(self, length: int = 64) -> str:
        """Generate a cryptographically secure secret key."""
        return secrets.token_urlsafe(length)
    
    def _hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """
        Hash a password using bcrypt with salt.
        
        Args:
            password: Plain text password
            salt: Optional salt (will be generated if not provided)
            
        Returns:
            Tuple of (password_hash, salt)
        """
        if salt is None:
            salt = bcrypt.gensalt().decode('utf-8')
        else:
            salt = salt.encode('utf-8')
            
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        return password_hash, salt.decode('utf-8') if isinstance(salt, bytes) else salt
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password
            password_hash: Stored password hash
            
        Returns:
            True if password is correct, False otherwise
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            self.logger.error(f"Password verification error: {str(e)}")
            return False
    
    def _hash_api_key(self, api_key: str) -> str:
        """
        Hash an API key for secure storage.
        
        Args:
            api_key: Plain text API key
            
        Returns:
            Hashed API key
        """
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def create_user(self, username: str, password: str, roles: List[str] = None, 
                   permissions: List[str] = None) -> str:
        """
        Create a new user account.
        
        Args:
            username: Username
            password: Plain text password
            roles: List of user roles
            permissions: List of user permissions
            
        Returns:
            User ID
            
        Raises:
            ValueError: If username already exists
        """
        if username in self.users:
            raise ValueError(f"Username '{username}' already exists")
        
        password_hash, salt = self._hash_password(password)
        
        user = UserCredentials(
            username=username,
            password_hash=password_hash,
            salt=salt,
            roles=roles or [],
            permissions=permissions or []
        )
        
        self.users[username] = user
        self.logger.info(f"Created user: {username}")
        
        return username
    
    def authenticate_user(self, username: str, password: str, client_ip: Optional[str] = None) -> TokenPayload:
        """
        Authenticate a user with username and password.
        
        Args:
            username: Username
            password: Plain text password
            client_ip: Client IP address for logging
            
        Returns:
            Token payload for successful authentication
            
        Raises:
            AuthenticationError: If authentication fails
        """
        if username not in self.users:
            self.logger.warning(f"Authentication attempt for non-existent user: {username} from {client_ip}")
            raise AuthenticationError("Invalid credentials")
        
        user = self.users[username]
        
        # Check if account is locked
        if user.locked_until and datetime.utcnow() < user.locked_until:
            self.logger.warning(f"Authentication attempt for locked account: {username} from {client_ip}")
            raise AuthenticationError("Account is temporarily locked")
        
        # Check if account is active
        if not user.is_active:
            self.logger.warning(f"Authentication attempt for inactive account: {username} from {client_ip}")
            raise AuthenticationError("Account is not active")
        
        # Verify password
        if not self._verify_password(password, user.password_hash):
            user.failed_attempts += 1
            
            # Lock account if too many failed attempts
            if user.failed_attempts >= self.max_failed_attempts:
                user.locked_until = datetime.utcnow() + timedelta(minutes=self.lockout_duration_minutes)
                self.logger.warning(f"Account locked due to failed attempts: {username} from {client_ip}")
            
            self.logger.warning(f"Failed authentication for user: {username} from {client_ip}")
            raise AuthenticationError("Invalid credentials")
        
        # Reset failed attempts and update last login
        user.failed_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        
        # Create token payload
        expires_at = int(time.time()) + (self.token_expiration_minutes * 60)
        token_payload = TokenPayload(
            user_id=username,
            username=username,
            roles=user.roles,
            permissions=user.permissions,
            expires_at=expires_at
        )
        
        self.logger.info(f"Successful authentication for user: {username} from {client_ip}")
        return token_payload
    
    def generate_jwt_token(self, payload: TokenPayload) -> str:
        """
        Generate a JWT token from a token payload.
        
        Args:
            payload: Token payload
            
        Returns:
            JWT token string
        """
        return jwt.encode(payload.dict(), self.jwt_secret_key, algorithm=self.jwt_algorithm)
    
    def verify_jwt_token(self, token: str) -> TokenPayload:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Token payload
            
        Raises:
            InvalidTokenError: If token is invalid
            TokenExpiredError: If token has expired
        """
        if token in self.revoked_tokens:
            raise InvalidTokenError("Token has been revoked")
        
        try:
            decoded = jwt.decode(token, self.jwt_secret_key, algorithms=[self.jwt_algorithm])
            payload = TokenPayload(**decoded)
            
            # Check expiration
            if payload.expires_at < int(time.time()):
                raise TokenExpiredError("Token has expired")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(f"Invalid token: {str(e)}")
    
    def revoke_token(self, token: str):
        """
        Revoke a JWT token.
        
        Args:
            token: JWT token to revoke
        """
        self.revoked_tokens.add(token)
        self.logger.info("Token revoked")
    
    def create_api_key(self, name: str, owner: str, permissions: List[str] = None,
                      expires_days: Optional[int] = None, allowed_ips: List[str] = None) -> str:
        """
        Create a new API key.
        
        Args:
            name: Human-readable key name
            owner: Key owner identifier
            permissions: List of permissions for the key
            expires_days: Number of days until expiration (None for no expiration)
            allowed_ips: List of allowed IP addresses (None for no restriction)
            
        Returns:
            Plain text API key (should be stored securely by caller)
        """
        # Generate a secure API key
        api_key = secrets.token_urlsafe(32)
        key_id = secrets.token_urlsafe(16)
        key_hash = self._hash_api_key(api_key)
        
        # Calculate expiration
        expires_at = None
        if expires_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        # Create API key record
        api_key_record = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            owner=owner,
            permissions=permissions or [],
            expires_at=expires_at,
            allowed_ips=allowed_ips or []
        )
        
        self.api_keys[key_id] = api_key_record
        self.logger.info(f"Created API key: {name} for owner: {owner}")
        
        return api_key
    
    def verify_api_key(self, api_key: str, client_ip: Optional[str] = None) -> APIKey:
        """
        Verify an API key.
        
        Args:
            api_key: Plain text API key
            client_ip: Client IP address
            
        Returns:
            API key record
            
        Raises:
            AuthenticationError: If API key is invalid or expired
        """
        key_hash = self._hash_api_key(api_key)
        
        # Find matching API key
        for key_id, key_record in self.api_keys.items():
            if key_record.key_hash == key_hash:
                # Check if key is active
                if not key_record.is_active:
                    raise AuthenticationError("API key is not active")
                
                # Check expiration
                if key_record.expires_at and datetime.utcnow() > key_record.expires_at:
                    raise AuthenticationError("API key has expired")
                
                # Check IP restrictions
                if key_record.allowed_ips and client_ip:
                    if client_ip not in key_record.allowed_ips:
                        self.logger.warning(f"API key access denied from IP: {client_ip}")
                        raise AuthenticationError("API key not allowed from this IP address")
                
                # Update usage statistics
                key_record.last_used = datetime.utcnow()
                key_record.usage_count += 1
                
                self.logger.info(f"API key verified: {key_record.name}")
                return key_record
        
        self.logger.warning(f"Invalid API key attempt from {client_ip}")
        raise AuthenticationError("Invalid API key")
    
    def check_permission(self, user_or_key: Union[TokenPayload, APIKey], 
                        required_permission: str) -> bool:
        """
        Check if a user or API key has a specific permission.
        
        Args:
            user_or_key: User token payload or API key record
            required_permission: Required permission string
            
        Returns:
            True if permission is granted, False otherwise
        """
        permissions = user_or_key.permissions
        
        # Check exact permission match
        if required_permission in permissions:
            return True
        
        # Check wildcard permissions
        for permission in permissions:
            if permission.endswith('*'):
                if required_permission.startswith(permission[:-1]):
                    return True
        
        return False
    
    def require_permission(self, user_or_key: Union[TokenPayload, APIKey], 
                          required_permission: str):
        """
        Require a specific permission, raising an exception if not granted.
        
        Args:
            user_or_key: User token payload or API key record
            required_permission: Required permission string
            
        Raises:
            AuthorizationError: If permission is not granted
        """
        if not self.check_permission(user_or_key, required_permission):
            entity_name = getattr(user_or_key, 'username', getattr(user_or_key, 'name', 'unknown'))
            self.logger.warning(f"Permission denied for {entity_name}: {required_permission}")
            raise AuthorizationError(f"Permission denied: {required_permission}")
    
    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user information (excluding sensitive data).
        
        Args:
            username: Username
            
        Returns:
            User information dictionary or None if user not found
        """
        if username not in self.users:
            return None
        
        user = self.users[username]
        return {
            "username": user.username,
            "roles": user.roles,
            "permissions": user.permissions,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "is_active": user.is_active,
            "failed_attempts": user.failed_attempts
        }
    
    def list_api_keys(self, owner: str) -> List[Dict[str, Any]]:
        """
        List API keys for a specific owner (excluding sensitive data).
        
        Args:
            owner: Key owner identifier
            
        Returns:
            List of API key information dictionaries
        """
        keys = []
        for key_record in self.api_keys.values():
            if key_record.owner == owner:
                keys.append({
                    "key_id": key_record.key_id,
                    "name": key_record.name,
                    "permissions": key_record.permissions,
                    "created_at": key_record.created_at.isoformat(),
                    "expires_at": key_record.expires_at.isoformat() if key_record.expires_at else None,
                    "last_used": key_record.last_used.isoformat() if key_record.last_used else None,
                    "usage_count": key_record.usage_count,
                    "is_active": key_record.is_active
                })
        return keys
    
    def revoke_api_key(self, key_id: str, owner: str) -> bool:
        """
        Revoke an API key.
        
        Args:
            key_id: API key ID
            owner: Key owner (for authorization)
            
        Returns:
            True if key was revoked, False if not found
        """
        if key_id in self.api_keys:
            key_record = self.api_keys[key_id]
            if key_record.owner == owner:
                key_record.is_active = False
                self.logger.info(f"API key revoked: {key_record.name}")
                return True
        return False
