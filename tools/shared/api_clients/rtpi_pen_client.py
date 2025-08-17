"""
rtpi-pen API client for cybersecurity AI workflow integration.

This module provides a specialized API client for connecting to rtpi-pen
security infrastructure, including Empire C2, Kasm workspaces, and self-healing services.
"""

import logging
from typing import Any, Dict, List, Optional
from .base_client import BaseAPIClient, APIError


class RTPIPenClient(BaseAPIClient):
    """
    Specialized API client for rtpi-pen platform integration.
    Provides methods for security tool orchestration and self-healing operations.
    """
    
    def __init__(self, base_url: str, **kwargs):
        """
        Initialize rtpi-pen client.
        
        Args:
            base_url: rtpi-pen server base URL
            **kwargs: Additional arguments passed to BaseAPIClient
        """
        super().__init__(base_url, **kwargs)
        self.logger = logging.getLogger("RTPIPenClient")
    
    # Empire C2 Management
    
    def list_empire_agents(self) -> List[Dict[str, Any]]:
        """List all Empire agents."""
        try:
            response = self.get("/api/empire/agents")
            return response["data"]["agents"]
        except APIError as e:
            self.logger.error(f"Failed to list Empire agents: {str(e)}")
            raise
    
    def get_empire_agent(self, agent_name: str) -> Dict[str, Any]:
        """Get specific Empire agent information."""
        try:
            response = self.get(f"/api/empire/agents/{agent_name}")
            return response["data"]
        except APIError as e:
            self.logger.error(f"Failed to get Empire agent {agent_name}: {str(e)}")
            raise
    
    def execute_empire_task(self, agent_name: str, command: str, module: Optional[str] = None) -> Dict[str, Any]:
        """Execute task on Empire agent."""
        try:
            data = {"command": command, "module": module}
            response = self.post(f"/api/empire/agents/{agent_name}/task", json_data=data)
            self.logger.info(f"Executed task on agent {agent_name}: {command}")
            return response["data"]
        except APIError as e:
            self.logger.error(f"Failed to execute task on agent {agent_name}: {str(e)}")
            raise
    
    # Kasm Workspace Management
    
    def create_kasm_workspace(self, workspace_type: str, image: str) -> Dict[str, Any]:
        """Create new Kasm workspace."""
        try:
            data = {"workspace_type": workspace_type, "image": image}
            response = self.post("/api/kasm/workspaces", json_data=data)
            self.logger.info(f"Created Kasm workspace: {workspace_type}")
            return response["data"]
        except APIError as e:
            self.logger.error(f"Failed to create Kasm workspace: {str(e)}")
            raise
    
    def list_kasm_workspaces(self) -> List[Dict[str, Any]]:
        """List all Kasm workspaces."""
        try:
            response = self.get("/api/kasm/workspaces")
            return response["data"]["workspaces"]
        except APIError as e:
            self.logger.error(f"Failed to list Kasm workspaces: {str(e)}")
            raise
    
    # Self-Healing Management
    
    def create_healing_rule(self, rule_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create self-healing rule."""
        try:
            response = self.post("/api/healing/rules", json_data=rule_spec)
            self.logger.info(f"Created healing rule: {rule_spec.get('service_name')}")
            return response["data"]
        except APIError as e:
            self.logger.error(f"Failed to create healing rule: {str(e)}")
            raise
    
    def trigger_healing_action(self, service_name: str, action: str) -> Dict[str, Any]:
        """Trigger healing action for service."""
        try:
            data = {"action": action}
            response = self.post(f"/api/healing/services/{service_name}/heal", json_data=data)
            self.logger.info(f"Triggered healing for {service_name}: {action}")
            return response["data"]
        except APIError as e:
            self.logger.error(f"Failed to trigger healing for {service_name}: {str(e)}")
            raise
    
    def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get service health status."""
        try:
            response = self.get(f"/api/healing/services/{service_name}/health")
            return response["data"]
        except APIError as e:
            self.logger.error(f"Failed to get health for {service_name}: {str(e)}")
            raise
