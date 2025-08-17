"""
Shared utilities and components for cybersecurity AI workflow integration.

This module provides common functionality used across all AI agent tools:
- API clients for platform integration
- Common data models and schemas  
- Security utilities and authentication
"""

__version__ = "1.0.0"
__author__ = "Cybersecurity AI Workflow Integration Team"

# Import key components for easy access
from .data_models.base_models import *
from .security.auth import SecurityManager

__all__ = [
    "SecurityManager",
]
