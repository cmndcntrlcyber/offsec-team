"""
BurpSuite API Client for cybersecurity AI workflow integration.

This tool provides direct integration with BurpSuite Professional API
for scan management and vulnerability assessment operations.
"""

import os
import time
import json
import logging
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from ..shared.api_clients.base_client import BaseAPIClient, APIError
from ..shared.data_models.security_models import ScanResult, Vulnerability


class BurpSuiteAPIClient:
    """
    BurpSuite Professional API client for security scanning operations.
    Provides methods for scan management, extension control, and result retrieval.
    """
    
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 1337,
                 api_key: Optional[str] = None):
        """
        Initialize BurpSuite API client.
        
        Args:
            host: BurpSuite API host
            port: BurpSuite API port  
            api_key: API key for authentication
        """
        base_url = f"http://{host}:{port}"
        self.client = BaseAPIClient(base_url, api_key=api_key)
        self.logger = logging.getLogger("BurpSuiteAPIClient")
    
    def establish_burp_connection(self, host: str = Field(..., description="BurpSuite host"), 
                                port: int = Field(..., description="BurpSuite port"),
                                api_key: str = Field(..., description="API key")) -> Dict[str, Any]:
        """
        Establish connection to BurpSuite API.
        
        Args:
            host: BurpSuite host address
            port: BurpSuite API port
            api_key: Authentication API key
            
        Returns:
            Connection status and capabilities
        """
        try:
            # Update client configuration
            self.client.base_url = f"http://{host}:{port}"
            self.client.api_key = api_key
            self.client.session.headers['Authorization'] = f'Bearer {api_key}'
            
            # Test connection
            health_check = self.client.health_check("/")
            
            # Get BurpSuite version and capabilities
            try:
                version_response = self.client.get("/burp/versions")
                capabilities_response = self.client.get("/burp/configuration")
                
                return {
                    "success": True,
                    "connected": health_check["healthy"],
                    "burp_version": version_response.get("data", {}),
                    "capabilities": capabilities_response.get("data", {}),
                    "api_endpoint": self.client.base_url
                }
            except:
                return {
                    "success": health_check["healthy"],
                    "connected": health_check["healthy"],
                    "api_endpoint": self.client.base_url
                }
                
        except Exception as e:
            self.logger.error(f"Failed to connect to BurpSuite: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def manage_burp_extensions(self, action: str = Field(..., description="Action (list, load, unload)"),
                             extension_id: str = Field(default="", description="Extension ID")) -> Dict[str, Any]:
        """
        Manage BurpSuite extensions.
        
        Args:
            action: Action to perform (list, load, unload)
            extension_id: Extension identifier
            
        Returns:
            Extension management result
        """
        try:
            if action == "list":
                response = self.client.get("/burp/extensions")
                return {
                    "success": True,
                    "extensions": response.get("data", [])
                }
            
            elif action == "load":
                if not extension_id:
                    return {"success": False, "error": "Extension ID required for load action"}
                
                response = self.client.post(f"/burp/extensions/{extension_id}/load")
                return {
                    "success": response["success"],
                    "extension_id": extension_id,
                    "status": "loaded"
                }
            
            elif action == "unload":
                if not extension_id:
                    return {"success": False, "error": "Extension ID required for unload action"}
                
                response = self.client.post(f"/burp/extensions/{extension_id}/unload")
                return {
                    "success": response["success"],
                    "extension_id": extension_id,
                    "status": "unloaded"
                }
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            self.logger.error(f"Extension management failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def execute_burp_function(self, function_name: str = Field(..., description="Function name"),
                            parameters: Dict[str, Any] = Field(default_factory=dict, description="Function parameters")) -> Dict[str, Any]:
        """
        Execute BurpSuite function remotely.
        
        Args:
            function_name: Name of BurpSuite function to execute
            parameters: Function parameters
            
        Returns:
            Function execution result
        """
        try:
            # Map common function names to API endpoints
            function_map = {
                "start_scan": "/burp/scanner/scans",
                "get_scan_status": "/burp/scanner/scans/{scan_id}",
                "get_scan_results": "/burp/scanner/scans/{scan_id}/report",
                "add_scope_item": "/burp/target/scope",
                "get_sitemap": "/burp/target/sitemap",
                "send_to_intruder": "/burp/intruder/attack",
                "send_to_repeater": "/burp/repeater/send"
            }
            
            if function_name not in function_map:
                return {"success": False, "error": f"Unknown function: {function_name}"}
            
            endpoint = function_map[function_name]
            
            # Handle parameterized endpoints
            if "{scan_id}" in endpoint and "scan_id" in parameters:
                endpoint = endpoint.format(scan_id=parameters["scan_id"])
                parameters.pop("scan_id")
            
            # Execute function based on type
            if function_name in ["start_scan", "add_scope_item", "send_to_intruder", "send_to_repeater"]:
                response = self.client.post(endpoint, json_data=parameters)
            else:
                response = self.client.get(endpoint, params=parameters)
            
            return {
                "success": response["success"],
                "function": function_name,
                "result": response.get("data", {})
            }
            
        except Exception as e:
            self.logger.error(f"Function execution failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_burp_configuration(self) -> Dict[str, Any]:
        """
        Get BurpSuite configuration settings.
        
        Returns:
            Current BurpSuite configuration
        """
        try:
            response = self.client.get("/burp/configuration")
            return {
                "success": True,
                "configuration": response.get("data", {})
            }
        except Exception as e:
            self.logger.error(f"Failed to get configuration: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def update_burp_configuration(self, config_updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update BurpSuite configuration settings.
        
        Args:
            config_updates: Configuration updates to apply
            
        Returns:
            Configuration update result
        """
        try:
            response = self.client.put("/burp/configuration", json_data=config_updates)
            return {
                "success": response["success"],
                "updated_settings": list(config_updates.keys())
            }
        except Exception as e:
            self.logger.error(f"Failed to update configuration: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_burp_project_info(self) -> Dict[str, Any]:
        """
        Get current BurpSuite project information.
        
        Returns:
            Project information and statistics
        """
        try:
            project_response = self.client.get("/burp/project")
            stats_response = self.client.get("/burp/project/statistics")
            
            return {
                "success": True,
                "project": project_response.get("data", {}),
                "statistics": stats_response.get("data", {})
            }
        except Exception as e:
            self.logger.error(f"Failed to get project info: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def export_burp_project(self, file_path: str) -> Dict[str, Any]:
        """
        Export BurpSuite project to file.
        
        Args:
            file_path: Path to export project file
            
        Returns:
            Export operation result
        """
        try:
            response = self.client.post("/burp/project/export", json_data={"path": file_path})
            return {
                "success": response["success"],
                "export_path": file_path
            }
        except Exception as e:
            self.logger.error(f"Failed to export project: {str(e)}")
            return {"success": False, "error": str(e)}
