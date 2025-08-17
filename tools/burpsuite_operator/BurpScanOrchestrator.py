"""
BurpSuite Scan Orchestrator for cybersecurity AI workflow integration.

This tool manages and automates BurpSuite scans with advanced configuration,
scheduling, and coordination capabilities.
"""

import time
import uuid
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ..shared.data_models.security_models import ScanResult, SeverityLevel
from .BurpSuiteAPIClient import BurpSuiteAPIClient


class BurpScanOrchestrator:
    """
    Advanced BurpSuite scan orchestrator for automated security testing.
    Provides scan configuration, scheduling, and management capabilities.
    """
    
    def __init__(self):
        """Initialize the BurpSuite scan orchestrator."""
        self.api_client = BurpSuiteAPIClient()
        self.active_scans = {}
        self.scan_history = []
        self.logger = logging.getLogger("BurpScanOrchestrator")
    
    def create_scan_configuration(self, target_url: str = Field(..., description="Target URL to scan"),
                                scan_type: str = Field(..., description="Type of scan (crawl_and_audit, audit_only, crawl_only)")) -> Dict[str, Any]:
        """
        Create a comprehensive scan configuration.
        
        Args:
            target_url: Target URL for scanning
            scan_type: Type of scan to perform
            
        Returns:
            Scan configuration details
        """
        try:
            scan_id = str(uuid.uuid4())
            
            # Define scan type configurations
            scan_configs = {
                "crawl_and_audit": {
                    "crawl_strategy": "thorough",
                    "audit_checks": "all",
                    "max_crawl_depth": 10,
                    "max_audit_items": 1000
                },
                "audit_only": {
                    "crawl_strategy": "none", 
                    "audit_checks": "all",
                    "max_audit_items": 500
                },
                "crawl_only": {
                    "crawl_strategy": "thorough",
                    "audit_checks": "none",
                    "max_crawl_depth": 15
                }
            }
            
            if scan_type not in scan_configs:
                return {
                    "success": False,
                    "error": f"Invalid scan type: {scan_type}. Valid types: {list(scan_configs.keys())}"
                }
            
            base_config = scan_configs[scan_type]
            
            configuration = {
                "scan_id": scan_id,
                "target_url": target_url,
                "scan_type": scan_type,
                "created_at": datetime.utcnow().isoformat(),
                "status": "configured",
                "burp_config": {
                    "urls": [target_url],
                    "scope": {
                        "include": [{"rule": target_url + "/*"}],
                        "exclude": []
                    },
                    **base_config,
                    "resource_pool": {
                        "maximum_concurrent_requests": 10,
                        "delay_between_requests": 100
                    },
                    "application_login": {
                        "login_required": False
                    }
                }
            }
            
            self.active_scans[scan_id] = configuration
            
            return {
                "success": True,
                "scan_id": scan_id,
                "configuration": configuration
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create scan configuration: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def launch_automated_scan(self, scan_config_id: str = Field(..., description="Scan configuration ID")) -> Dict[str, Any]:
        """
        Launch an automated BurpSuite scan.
        
        Args:
            scan_config_id: ID of the scan configuration to use
            
        Returns:
            Scan launch result and tracking information
        """
        try:
            if scan_config_id not in self.active_scans:
                return {"success": False, "error": f"Scan configuration {scan_config_id} not found"}
            
            config = self.active_scans[scan_config_id]
            
            # Start the scan via BurpSuite API
            scan_response = self.api_client.execute_burp_function(
                "start_scan",
                parameters=config["burp_config"]
            )
            
            if not scan_response["success"]:
                return {
                    "success": False,
                    "error": f"Failed to start scan: {scan_response.get('error', 'Unknown error')}"
                }
            
            # Update configuration with scan details
            burp_scan_id = scan_response["result"].get("scan_id")
            config.update({
                "status": "running",
                "burp_scan_id": burp_scan_id,
                "started_at": datetime.utcnow().isoformat(),
                "progress": 0
            })
            
            self.logger.info(f"Launched automated scan: {scan_config_id}")
            
            return {
                "success": True,
                "scan_id": scan_config_id,
                "burp_scan_id": burp_scan_id,
                "status": "running",
                "target_url": config["target_url"]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to launch scan: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def track_scan_status(self, scan_id: str = Field(..., description="Scan ID to track")) -> Dict[str, Any]:
        """
        Track the status and progress of a running scan.
        
        Args:
            scan_id: ID of the scan to track
            
        Returns:
            Current scan status and progress information
        """
        try:
            if scan_id not in self.active_scans:
                return {"success": False, "error": f"Scan {scan_id} not found"}
            
            config = self.active_scans[scan_id]
            burp_scan_id = config.get("burp_scan_id")
            
            if not burp_scan_id:
                return {
                    "success": True,
                    "scan_id": scan_id,
                    "status": config["status"],
                    "progress": 0
                }
            
            # Get status from BurpSuite
            status_response = self.api_client.execute_burp_function(
                "get_scan_status",
                parameters={"scan_id": burp_scan_id}
            )
            
            if status_response["success"]:
                burp_status = status_response["result"]
                
                # Update local configuration
                config["progress"] = burp_status.get("scan_metrics", {}).get("crawl_and_audit_progress", 0)
                config["status"] = "completed" if burp_status.get("scan_status") == "finished" else "running"
                
                if config["status"] == "completed" and "completed_at" not in config:
                    config["completed_at"] = datetime.utcnow().isoformat()
                    self.scan_history.append(config.copy())
                
                return {
                    "success": True,
                    "scan_id": scan_id,
                    "status": config["status"],
                    "progress": config["progress"],
                    "burp_status": burp_status,
                    "target_url": config["target_url"],
                    "started_at": config.get("started_at"),
                    "completed_at": config.get("completed_at")
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get status from BurpSuite: {status_response.get('error')}"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to track scan status: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def schedule_scan(self, scan_config_id: str, schedule_time: str, recurring: bool = False) -> Dict[str, Any]:
        """
        Schedule a scan to run at a specific time.
        
        Args:
            scan_config_id: Scan configuration ID
            schedule_time: ISO format datetime string for scheduling
            recurring: Whether the scan should recur
            
        Returns:
            Scheduling result
        """
        try:
            if scan_config_id not in self.active_scans:
                return {"success": False, "error": f"Scan configuration {scan_config_id} not found"}
            
            schedule_datetime = datetime.fromisoformat(schedule_time.replace('Z', '+00:00'))
            
            config = self.active_scans[scan_config_id]
            config.update({
                "scheduled_for": schedule_time,
                "recurring": recurring,
                "status": "scheduled"
            })
            
            # In a real implementation, you would integrate with a job scheduler
            # For now, we'll just mark it as scheduled
            
            return {
                "success": True,
                "scan_id": scan_config_id,
                "scheduled_for": schedule_time,
                "recurring": recurring,
                "message": f"Scan scheduled for {schedule_time}"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to schedule scan: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def stop_scan(self, scan_id: str) -> Dict[str, Any]:
        """
        Stop a running scan.
        
        Args:
            scan_id: ID of the scan to stop
            
        Returns:
            Stop operation result
        """
        try:
            if scan_id not in self.active_scans:
                return {"success": False, "error": f"Scan {scan_id} not found"}
            
            config = self.active_scans[scan_id]
            burp_scan_id = config.get("burp_scan_id")
            
            if burp_scan_id:
                # Stop scan via BurpSuite API (if supported)
                stop_response = self.api_client.execute_burp_function(
                    "stop_scan", 
                    parameters={"scan_id": burp_scan_id}
                )
                
                if stop_response["success"]:
                    config["status"] = "stopped"
                    config["stopped_at"] = datetime.utcnow().isoformat()
                    
                    return {
                        "success": True,
                        "scan_id": scan_id,
                        "status": "stopped",
                        "message": "Scan stopped successfully"
                    }
                else:
                    return {"success": False, "error": "Failed to stop scan in BurpSuite"}
            else:
                config["status"] = "stopped"
                return {
                    "success": True,
                    "scan_id": scan_id,
                    "status": "stopped",
                    "message": "Scan configuration stopped"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to stop scan: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_scan_queue_status(self) -> Dict[str, Any]:
        """
        Get the status of all scans in the queue.
        
        Returns:
            Overview of all scan statuses
        """
        try:
            scan_summary = {
                "total_scans": len(self.active_scans),
                "running": 0,
                "completed": 0,
                "scheduled": 0,
                "configured": 0,
                "stopped": 0
            }
            
            scans_detail = []
            
            for scan_id, config in self.active_scans.items():
                status = config["status"]
                scan_summary[status] = scan_summary.get(status, 0) + 1
                
                scans_detail.append({
                    "scan_id": scan_id,
                    "target_url": config["target_url"],
                    "status": status,
                    "progress": config.get("progress", 0),
                    "created_at": config["created_at"],
                    "started_at": config.get("started_at"),
                    "completed_at": config.get("completed_at")
                })
            
            return {
                "success": True,
                "summary": scan_summary,
                "scans": scans_detail,
                "history_count": len(self.scan_history)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get queue status: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def cleanup_completed_scans(self, older_than_days: int = 7) -> Dict[str, Any]:
        """
        Clean up completed scans older than specified days.
        
        Args:
            older_than_days: Remove scans completed more than this many days ago
            
        Returns:
            Cleanup operation result
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
            cleaned_count = 0
            
            # Clean up from active scans
            scan_ids_to_remove = []
            for scan_id, config in self.active_scans.items():
                if config["status"] == "completed" and "completed_at" in config:
                    completed_date = datetime.fromisoformat(config["completed_at"])
                    if completed_date < cutoff_date:
                        scan_ids_to_remove.append(scan_id)
            
            for scan_id in scan_ids_to_remove:
                del self.active_scans[scan_id]
                cleaned_count += 1
            
            # Clean up from history
            original_history_count = len(self.scan_history)
            self.scan_history = [
                scan for scan in self.scan_history
                if datetime.fromisoformat(scan["completed_at"]) >= cutoff_date
            ]
            cleaned_count += original_history_count - len(self.scan_history)
            
            return {
                "success": True,
                "cleaned_scans": cleaned_count,
                "cutoff_date": cutoff_date.isoformat(),
                "remaining_active": len(self.active_scans),
                "remaining_history": len(self.scan_history)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup scans: {str(e)}")
            return {"success": False, "error": str(e)}
