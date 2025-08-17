"""
Base data models for cybersecurity AI workflow integration.

This module contains fundamental data structures used across all platforms and tools.
"""

import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field, validator


class ResponseStatus(str, Enum):
    """Standard response status enumeration."""
    SUCCESS = "success"
    ERROR = "error" 
    WARNING = "warning"
    PENDING = "pending"


class SeverityLevel(str, Enum):
    """Security finding severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BaseResponse(BaseModel):
    """Base response model for all API operations."""
    
    success: bool = Field(..., description="Whether the operation was successful")
    status: ResponseStatus = Field(..., description="Response status")
    message: str = Field(default="", description="Human-readable status message")
    timestamp: float = Field(default_factory=time.time, description="Unix timestamp")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")
    request_id: Optional[str] = Field(default=None, description="Unique request identifier")
    
    @validator('timestamp', pre=True, always=True)
    def set_timestamp(cls, v):
        return v or time.time()


class SuccessResponse(BaseResponse):
    """Response model for successful operations."""
    
    success: Literal[True] = Field(default=True)
    status: Literal[ResponseStatus.SUCCESS] = Field(default=ResponseStatus.SUCCESS)
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    
    def __init__(self, data: Optional[Dict[str, Any]] = None, message: str = "Operation completed successfully", **kwargs):
        super().__init__(
            data=data,
            message=message,
            **kwargs
        )


class ErrorResponse(BaseResponse):
    """Response model for failed operations."""
    
    success: Literal[False] = Field(default=False)
    status: Literal[ResponseStatus.ERROR] = Field(default=ResponseStatus.ERROR)
    error_code: Optional[str] = Field(default=None, description="Machine-readable error code")
    error_details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error information")
    stack_trace: Optional[str] = Field(default=None, description="Stack trace for debugging")
    
    def __init__(self, message: str = "Operation failed", error_code: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code=error_code,
            **kwargs
        )


class PaginatedResponse(SuccessResponse):
    """Response model for paginated data."""
    
    page: int = Field(default=1, description="Current page number")
    page_size: int = Field(default=50, description="Items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    items: List[Dict[str, Any]] = Field(..., description="Page items")
    
    @validator('total_pages', pre=True, always=True)
    def calculate_total_pages(cls, v, values):
        if 'total_items' in values and 'page_size' in values:
            return max(1, (values['total_items'] + values['page_size'] - 1) // values['page_size'])
        return v
    
    @validator('has_next', pre=True, always=True)
    def calculate_has_next(cls, v, values):
        if 'page' in values and 'total_pages' in values:
            return values['page'] < values['total_pages']
        return v
    
    @validator('has_previous', pre=True, always=True)
    def calculate_has_previous(cls, v, values):
        if 'page' in values:
            return values['page'] > 1
        return v


class TimestampedModel(BaseModel):
    """Base model with timestamp fields."""
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    def update_timestamp(self):
        """Update the updated_at field to current time."""
        self.updated_at = datetime.utcnow()


class IdentifiedModel(TimestampedModel):
    """Base model with ID and timestamps."""
    
    id: str = Field(..., description="Unique identifier")
    name: Optional[str] = Field(default=None, description="Human-readable name")
    description: Optional[str] = Field(default=None, description="Description")
    tags: List[str] = Field(default_factory=list, description="Associated tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ConnectionConfig(BaseModel):
    """Base configuration for platform connections."""
    
    host: str = Field(..., description="Host address")
    port: int = Field(..., description="Port number")
    use_ssl: bool = Field(default=True, description="Use SSL/TLS")
    api_key: Optional[str] = Field(default=None, description="API key for authentication")
    username: Optional[str] = Field(default=None, description="Username for authentication")
    password: Optional[str] = Field(default=None, description="Password for authentication")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    retry_attempts: int = Field(default=3, description="Number of retry attempts")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    
    @validator('port')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v
    
    @validator('timeout')
    def validate_timeout(cls, v):
        if v <= 0:
            raise ValueError('Timeout must be positive')
        return v
    
    @validator('retry_attempts')
    def validate_retry_attempts(cls, v):
        if v < 0:
            raise ValueError('Retry attempts cannot be negative')
        return v


class HealthStatus(BaseModel):
    """Health status information."""
    
    status: str = Field(..., description="Overall health status")
    is_healthy: bool = Field(..., description="Whether the system is healthy")
    components: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Component health status")
    metrics: Dict[str, Union[int, float, str]] = Field(default_factory=dict, description="Health metrics")
    last_check: datetime = Field(default_factory=datetime.utcnow, description="Last health check time")
    uptime: Optional[float] = Field(default=None, description="Uptime in seconds")
    
    def add_component_status(self, component: str, status: str, details: Optional[Dict[str, Any]] = None):
        """Add or update component health status."""
        self.components[component] = {
            "status": status,
            "is_healthy": status.lower() in ["healthy", "ok", "running"],
            "details": details or {},
            "last_check": datetime.utcnow().isoformat()
        }
    
    def update_overall_status(self):
        """Update overall status based on component statuses."""
        if not self.components:
            self.status = "unknown"
            self.is_healthy = False
            return
        
        unhealthy_components = [
            name for name, info in self.components.items()
            if not info.get("is_healthy", False)
        ]
        
        if not unhealthy_components:
            self.status = "healthy"
            self.is_healthy = True
        elif len(unhealthy_components) == len(self.components):
            self.status = "unhealthy"
            self.is_healthy = False
        else:
            self.status = "degraded"
            self.is_healthy = False
        
        self.last_check = datetime.utcnow()


class ProgressTracker(BaseModel):
    """Progress tracking for long-running operations."""
    
    current_step: int = Field(default=0, description="Current step number")
    total_steps: int = Field(..., description="Total number of steps")
    step_name: Optional[str] = Field(default=None, description="Name of current step")
    progress_percentage: float = Field(default=0.0, description="Progress as percentage")
    estimated_completion: Optional[datetime] = Field(default=None, description="Estimated completion time")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Start time")
    completed_steps: List[str] = Field(default_factory=list, description="List of completed steps")
    
    @validator('progress_percentage', pre=True, always=True)
    def calculate_progress(cls, v, values):
        if 'current_step' in values and 'total_steps' in values and values['total_steps'] > 0:
            return min(100.0, (values['current_step'] / values['total_steps']) * 100)
        return v
    
    def advance_step(self, step_name: Optional[str] = None):
        """Advance to the next step."""
        if self.current_step < self.total_steps:
            if self.step_name:
                self.completed_steps.append(self.step_name)
            self.current_step += 1
            self.step_name = step_name
            self.progress_percentage = (self.current_step / self.total_steps) * 100
    
    def complete(self):
        """Mark the operation as completed."""
        if self.step_name and self.step_name not in self.completed_steps:
            self.completed_steps.append(self.step_name)
        self.current_step = self.total_steps
        self.progress_percentage = 100.0
        self.step_name = "Completed"
