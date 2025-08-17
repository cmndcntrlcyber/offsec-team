"""
MCP-Nexus API client for cybersecurity AI workflow integration.

This module provides a specialized API client for connecting to and managing
MCP-Nexus server operations, device registration, and real-time communications.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from .base_client import BaseAPIClient, APIError

from ..data_models.platform_models import MCPServerProcess, EdgeDevice
from ..data_models.base_models import HealthStatus


class MCPNexusClient(BaseAPIClient):
    """
    Specialized API client for MCP-Nexus platform integration.
    Provides methods for server management, device registration, and real-time communication.
    """
    
    def __init__(self, base_url: str, **kwargs):
        """
        Initialize MCP-Nexus client.
        
        Args:
            base_url: MCP-Nexus server base URL
            **kwargs: Additional arguments passed to BaseAPIClient
        """
        super().__init__(base_url, **kwargs)
        self.logger = logging.getLogger("MCPNexusClient")
    
    # Server Process Management
    
    def create_server_process(self, 
                            command: str,
                            working_directory: Optional[str] = None,
                            environment_vars: Optional[Dict[str, str]] = None,
                            auto_restart: bool = True,
                            health_check_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new MCP server process.
        
        Args:
            command: Command to start the server
            working_directory: Working directory for the process
            environment_vars: Environment variables
            auto_restart: Whether to enable auto-restart
            health_check_url: Health check endpoint URL
            
        Returns:
            Server process information
        """
        try:
            data = {
                "command": command,
                "working_directory": working_directory,
                "environment_vars": environment_vars or {},
                "auto_restart": auto_restart,
                "health_check_url": health_check_url
            }
            
            response = self.post("/api/servers", json_data=data)
            self.logger.info(f"Created server process: {command}")
            return response["data"]
            
        except APIError as e:
            self.logger.error(f"Failed to create server process: {str(e)}")
            raise
    
    def list_server_processes(self) -> List[Dict[str, Any]]:
        """
        List all MCP server processes.
        
        Returns:
            List of server process information
        """
        try:
            response = self.get("/api/servers")
            return response["data"]["servers"]
            
        except APIError as e:
            self.logger.error(f"Failed to list server processes: {str(e)}")
            raise
    
    def get_server_process(self, server_id: str) -> Dict[str, Any]:
        """
        Get information about a specific server process.
        
        Args:
            server_id: Server process ID
            
        Returns:
            Server process information
        """
        try:
            response = self.get(f"/api/servers/{server_id}")
            return response["data"]
            
        except APIError as e:
            self.logger.error(f"Failed to get server process {server_id}: {str(e)}")
            raise
    
    def start_server_process(self, server_id: str) -> Dict[str, Any]:
        """
        Start a server process.
        
        Args:
            server_id: Server process ID
            
        Returns:
            Operation result
        """
        try:
            response = self.post(f"/api/servers/{server_id}/start")
            self.logger.info(f"Started server process: {server_id}")
            return response["data"]
            
        except APIError as e:
            self.logger.error(f"Failed to start server process {server_id}: {str(e)}")
            raise
    
    def stop_server_process(self, server_id: str) -> Dict[str, Any]:
        """
        Stop a server process.
        
        Args:
            server_id: Server process ID
            
        Returns:
            Operation result
        """
        try:
            response = self.post(f"/api/servers/{server_id}/stop")
            self.logger.info(f"Stopped server process: {server_id}")
            return response["data"]
            
        except APIError as e:
            self.logger.error(f"Failed to stop server process {server_id}: {str(e)}")
            raise
    
    def restart_server_process(self, server_id: str) -> Dict[str, Any]:
        """
        Restart a server process.
        
        Args:
            server_id: Server process ID
            
        Returns:
            Operation result
        """
        try:
            response = self.post(f"/api/servers/{server_id}/restart")
            self.logger.info(f"Restarted server process: {server_id}")
            return response["data"]
            
        except APIError as e:
            self.logger.error(f"Failed to restart server process {server_id}: {str(e)}")
            raise
    
    def delete_server_process(self, server_id: str) -> Dict[str, Any]:
        """
        Delete a server process.
        
        Args:
            server_id: Server process ID
            
        Returns:
            Operation result
        """
        try:
            response = self.delete(f"/api/servers/{server_id}")
            self.logger.info(f"Deleted server process: {server_id}")
            return response["data"]
            
        except APIError as e:
            self.logger.error(f"Failed to delete server process {server_id}: {str(e)}")
            raise
    
    # Edge Device Management
    
    def register_edge_device(self,
                           device_type: str,
                           capabilities: List[str],
                           certificate_pem: Optional[str] = None) -> Dict[str, Any]:
        """
        Register a new edge device.
        
        Args:
            device_type: Type of edge device
            capabilities: List of device capabilities
            certificate_pem: Client certificate in PEM format
            
        Returns:
            Device registration information
        """
        try:
            data = {
                "device_type": device_type,
                "capabilities": capabilities,
                "certificate_pem": certificate_pem
            }
            
            response = self.post("/api/devices", json_data=data)
            self.logger.info(f"Registered edge device: {device_type}")
            return response["data"]
            
        except APIError as e:
            self.logger.error(f"Failed to register edge device: {str(e)}")
            raise
    
    def list_edge_devices(self) -> List[Dict[str, Any]]:
        """
        List all registered edge devices.
        
        Returns:
            List of edge device information
        """
        try:
            response = self.get("/api/devices")
            return response["data"]["devices"]
            
        except APIError as e:
            self.logger.error(f"Failed to list edge devices: {str(e)}")
            raise
    
    def get_edge_device(self, device_id: str) -> Dict[str, Any]:
        """
        Get information about a specific edge device.
        
        Args:
            device_id: Device ID
            
        Returns:
            Edge device information
        """
        try:
            response = self.get(f"/api/devices/{device_id}")
            return response["data"]
            
        except APIError as e:
            self.logger.error(f"Failed to get edge device {device_id}: {str(e)}")
            raise
    
    def update_device_status(self, device_id: str, health_status: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update device health status.
        
        Args:
            device_id: Device ID
            health_status: Health status information
            
        Returns:
            Update result
        """
        try:
            response = self.put(f"/api/devices/{device_id}/status", json_data=health_status)
            return response["data"]
            
        except APIError as e:
            self.logger.error(f"Failed to update device status for {device_id}: {str(e)}")
            raise
    
    def block_edge_device(self, device_id: str, reason: str) -> Dict[str, Any]:
        """
        Block an edge device.
        
        Args:
            device_id: Device ID
            reason: Reason for blocking
            
        Returns:
            Operation result
        """
        try:
            data = {"reason": reason}
            response = self.post(f"/api/devices/{device_id}/block", json_data=data)
            self.logger.warning(f"Blocked edge device {device_id}: {reason}")
            return response["data"]
            
        except APIError as e:
            self.logger.error(f"Failed to block edge device {device_id}: {str(e)}")
            raise
    
    def unblock_edge_device(self, device_id: str) -> Dict[str, Any]:
        """
        Unblock an edge device.
        
        Args:
            device_id: Device ID
            
        Returns:
            Operation result
        """
        try:
            response = self.post(f"/api/devices/{device_id}/unblock")
            self.logger.info(f"Unblocked edge device: {device_id}")
            return response["data"]
            
        except APIError as e:
            self.logger.error(f"Failed to unblock edge device {device_id}: {str(e)}")
            raise
    
    # Real-time Communication
    
    def create_websocket_connection_for_device(self, device_id: str, on_message=None, on_error=None, on_close=None):
        """
        Create WebSocket connection for real-time device communication.
        
        Args:
            device_id: Device ID
            on_message: Message callback function
            on_error: Error callback function
            on_close: Close callback function
            
        Returns:
            WebSocket connection
        """
        endpoint = f"/ws/devices/{device_id}"
        return self.create_websocket_connection(endpoint, on_message, on_error, on_close)
    
    def send_device_message(self, device_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to an edge device via REST API.
        
        Args:
            device_id: Device ID
            message: Message data
            
        Returns:
            Send result
        """
        try:
            response = self.post(f"/api/devices/{device_id}/message", json_data=message)
            return response["data"]
            
        except APIError as e:
            self.logger.error(f"Failed to send message to device {device_id}: {str(e)}")
            raise
    
    # Server Health and Monitoring
    
    def get_server_health(self) -> Dict[str, Any]:
        """
        Get MCP-Nexus server health status.
        
        Returns:
            Health status information
        """
        try:
            response = self.get("/api/health")
            return response["data"]
            
        except APIError as e:
            self.logger.error(f"Failed to get server health: {str(e)}")
            raise
    
    def get_server_metrics(self) -> Dict[str, Any]:
        """
        Get server performance metrics.
        
        Returns:
            Performance metrics
        """
        try:
            response = self.get("/api/metrics")
            return response["data"]
            
        except APIError as e:
            self.logger.error(f"Failed to get server metrics: {str(e)}")
            raise
    
    def get_server_logs(self, lines: int = 100, level: str = "info") -> List[Dict[str, Any]]:
        """
        Get recent server logs.
        
        Args:
            lines: Number of log lines to retrieve
            level: Log level filter
            
        Returns:
            List of log entries
        """
        try:
            params = {"lines": lines, "level": level}
            response = self.get("/api/logs", params=params)
            return response["data"]["logs"]
            
        except APIError as e:
            self.logger.error(f"Failed to get server logs: {str(e)}")
            raise
    
    # Configuration Management
    
    def get_server_config(self) -> Dict[str, Any]:
        """
        Get server configuration.
        
        Returns:
            Server configuration
        """
        try:
            response = self.get("/api/config")
            return response["data"]
            
        except APIError as e:
            self.logger.error(f"Failed to get server config: {str(e)}")
            raise
    
    def update_server_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update server configuration.
        
        Args:
            config: Configuration updates
            
        Returns:
            Update result
        """
        try:
            response = self.put("/api/config", json_data=config)
            self.logger.info("Updated server configuration")
            return response["data"]
            
        except APIError as e:
            self.logger.error(f"Failed to update server config: {str(e)}")
            raise
    
    # Task and Workflow Management
    
    def create_workflow(self, workflow_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new workflow.
        
        Args:
            workflow_spec: Workflow specification
            
        Returns:
            Workflow information
        """
        try:
            response = self.post("/api/workflows", json_data=workflow_spec)
            self.logger.info(f"Created workflow: {workflow_spec.get('name', 'unnamed')}")
            return response["data"]
            
        except APIError as e:
            self.logger.error(f"Failed to create workflow: {str(e)}")
            raise
    
    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get workflow information.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Workflow information
        """
        try:
            response = self.get(f"/api/workflows/{workflow_id}")
            return response["data"]
            
        except APIError as e:
            self.logger.error(f"Failed to get workflow {workflow_id}: {str(e)}")
            raise
    
    def start_workflow(self, workflow_id: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Start a workflow execution.
        
        Args:
            workflow_id: Workflow ID
            parameters: Workflow parameters
            
        Returns:
            Execution information
        """
        try:
            data = {"parameters": parameters or {}}
            response = self.post(f"/api/workflows/{workflow_id}/start", json_data=data)
            self.logger.info(f"Started workflow: {workflow_id}")
            return response["data"]
            
        except APIError as e:
            self.logger.error(f"Failed to start workflow {workflow_id}: {str(e)}")
            raise
    
    def get_workflow_status(self, workflow_id: str, execution_id: str) -> Dict[str, Any]:
        """
        Get workflow execution status.
        
        Args:
            workflow_id: Workflow ID
            execution_id: Execution ID
            
        Returns:
            Execution status
        """
        try:
            response = self.get(f"/api/workflows/{workflow_id}/executions/{execution_id}")
            return response["data"]
            
        except APIError as e:
            self.logger.error(f"Failed to get workflow status: {str(e)}")
            raise
    
    def stop_workflow(self, workflow_id: str, execution_id: str) -> Dict[str, Any]:
        """
        Stop a workflow execution.
        
        Args:
            workflow_id: Workflow ID
            execution_id: Execution ID
            
        Returns:
            Stop result
        """
        try:
            response = self.post(f"/api/workflows/{workflow_id}/executions/{execution_id}/stop")
            self.logger.info(f"Stopped workflow execution: {execution_id}")
            return response["data"]
            
        except APIError as e:
            self.logger.error(f"Failed to stop workflow execution: {str(e)}")
            raise
