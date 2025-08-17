"""
attack-node API client for cybersecurity AI workflow integration.

This module provides a specialized API client for connecting to attack-node
red team operations platform and Burp Suite Professional integration.
"""

import logging
from typing import Any, Dict, List, Optional
from .base_client import BaseAPIClient, APIError


class AttackNodeClient(BaseAPIClient):
    """
    Specialized API client for attack-node platform integration.
    Provides methods for red team operations and Burp Suite management.
    """
    
    def __init__(self, base_url: str, **kwargs):
        """
        Initialize attack-node client.
        
        Args:
            base_url: attack-node server base URL
            **kwargs: Additional arguments passed to BaseAPIClient
        """
        super().__init__(base_url, **kwargs)
        self.logger = logging.getLogger("AttackNodeClient")
    
    # Red Team Operations Management
    
    def create_operation(self, operation_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create new red team operation."""
        try:
            response = self.post("/api/operations", json_data=operation_spec)
            self.logger.info(f"Created operation: {operation_spec.get('name')}")
            return response["data"]
        except APIError as e:
            self.logger.error(f"Failed to create operation: {str(e)}")
            raise
    
    def list_operations(self) -> List[Dict[str, Any]]:
        """List all operations."""
        try:
            response = self.get("/api/operations")
            return response["data"]["operations"]
        except APIError as e:
            self.logger.error(f"Failed to list operations: {str(e)}")
            raise
    
    def get_operation(self, operation_id: str) -> Dict[str, Any]:
        """Get specific operation."""
        try:
            response = self.get(f"/api/operations/{operation_id}")
            return response["data"]
        except APIError as e:
            self.logger.error(f"Failed to get operation {operation_id}: {str(e)}")
            raise
    
    # Burp Suite Integration
    
    def start_burp_scan(self, target_url: str, scan_config: Dict[str, Any]) -> Dict[str, Any]:
        """Start Burp Suite scan."""
        try:
            data = {"target_url": target_url, **scan_config}
            response = self.post("/api/burp/scans", json_data=data)
            self.logger.info(f"Started Burp scan for {target_url}")
            return response["data"]
        except APIError as e:
            self.logger.error(f"Failed to start Burp scan: {str(e)}")
            raise
    
    def get_burp_scan_status(self, scan_id: str) -> Dict[str, Any]:
        """Get Burp scan status."""
        try:
            response = self.get(f"/api/burp/scans/{scan_id}")
            return response["data"]
        except APIError as e:
            self.logger.error(f"Failed to get scan status {scan_id}: {str(e)}")
            raise
    
    def get_burp_scan_results(self, scan_id: str) -> Dict[str, Any]:
        """Get Burp scan results."""
        try:
            response = self.get(f"/api/burp/scans/{scan_id}/results")
            return response["data"]
        except APIError as e:
            self.logger.error(f"Failed to get scan results {scan_id}: {str(e)}")
            raise
    
    # Docker Environment Management
    
    def get_kali_environment(self) -> Dict[str, Any]:
        """Get Kali Linux environment status."""
        try:
            response = self.get("/api/docker/kali")
            return response["data"]
        except APIError as e:
            self.logger.error(f"Failed to get Kali environment: {str(e)}")
            raise
    
    def execute_kali_command(self, command: str) -> Dict[str, Any]:
        """Execute command in Kali environment."""
        try:
            data = {"command": command}
            response = self.post("/api/docker/kali/execute", json_data=data)
            return response["data"]
        except APIError as e:
            self.logger.error(f"Failed to execute command: {str(e)}")
            raise
