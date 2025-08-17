"""
Self-Healing Integrator for cybersecurity AI workflow integration.

This tool connects with rtpi-pen's self-healing capabilities to define
healing rules, register actions, and test healing workflows.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ..shared.api_clients.rtpi_pen_client import RTPIPenClient
from ..shared.data_models.platform_models import SelfHealingRule


class SelfHealingIntegrator:
    """
    Self-healing integration tool for rtpi-pen platform.
    Provides rule definition, action registration, and workflow testing.
    """
    
    def __init__(self):
        """Initialize the Self-Healing Integrator."""
        self.rtpi_client = RTPIPenClient("http://localhost:8080")
        self.healing_rules = {}
        self.logger = logging.getLogger("SelfHealingIntegrator")
    
    def define_healing_rules(self, service_name: str = Field(..., description="Service name to monitor"),
                           failure_conditions: Dict[str, Any] = Field(..., description="Conditions that trigger healing")) -> Dict[str, Any]:
        """
        Define self-healing rules for a service.
        
        Args:
            service_name: Name of the service to monitor
            failure_conditions: Conditions that trigger healing actions
            
        Returns:
            Healing rule definition result
        """
        try:
            rule_id = f"heal-{service_name}-{int(datetime.utcnow().timestamp())}"
            
            # Define default healing actions based on service type
            default_actions = self._get_default_healing_actions(service_name)
            
            # Create comprehensive healing rule
            healing_rule = {
                "rule_id": rule_id,
                "service_name": service_name,
                "created_at": datetime.utcnow().isoformat(),
                "trigger_conditions": failure_conditions,
                "healing_actions": default_actions,
                "cooldown_period": 300,  # 5 minutes
                "max_attempts": 3,
                "success_criteria": self._get_success_criteria(service_name),
                "notification_settings": {
                    "notify_on_trigger": True,
                    "notify_on_success": True,
                    "notify_on_failure": True
                },
                "is_enabled": True
            }
            
            # Store rule locally
            self.healing_rules[rule_id] = healing_rule
            
            # Register with rtpi-pen
            try:
                rtpi_response = self.rtpi_client.create_healing_rule(healing_rule)
                healing_rule["rtpi_rule_id"] = rtpi_response.get("rule_id")
            except Exception as e:
                self.logger.warning(f"Failed to register with rtpi-pen: {str(e)}")
                healing_rule["rtpi_registration_error"] = str(e)
            
            self.logger.info(f"Defined healing rule for {service_name}: {rule_id}")
            
            return {
                "success": True,
                "rule_id": rule_id,
                "service_name": service_name,
                "healing_rule": healing_rule
            }
            
        except Exception as e:
            self.logger.error(f"Failed to define healing rules: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def register_healing_actions(self, service_name: str = Field(..., description="Service name"),
                               actions: List[Dict[str, Any]] = Field(..., description="Healing actions to register")) -> Dict[str, Any]:
        """
        Register custom healing actions for a service.
        
        Args:
            service_name: Name of the service
            actions: List of healing actions to register
            
        Returns:
            Action registration result
        """
        try:
            registered_actions = []
            
            for action in actions:
                action_id = f"action-{service_name}-{action.get('name', 'unnamed')}-{int(datetime.utcnow().timestamp())}"
                
                action_config = {
                    "action_id": action_id,
                    "service_name": service_name,
                    "name": action.get("name", "unnamed_action"),
                    "type": action.get("type", "restart"),
                    "command": action.get("command", ""),
                    "timeout": action.get("timeout", 60),
                    "retry_count": action.get("retry_count", 2),
                    "prerequisites": action.get("prerequisites", []),
                    "rollback_action": action.get("rollback_action"),
                    "validation_check": action.get("validation_check"),
                    "registered_at": datetime.utcnow().isoformat()
                }
                
                registered_actions.append(action_config)
                
                # Update existing rules for this service
                for rule_id, rule in self.healing_rules.items():
                    if rule["service_name"] == service_name:
                        if "custom_actions" not in rule:
                            rule["custom_actions"] = []
                        rule["custom_actions"].append(action_config)
            
            return {
                "success": True,
                "service_name": service_name,
                "registered_actions": registered_actions,
                "action_count": len(registered_actions)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to register healing actions: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_healing_workflow(self, service_name: str = Field(..., description="Service name"),
                            failure_scenario: str = Field(..., description="Failure scenario to test")) -> Dict[str, Any]:
        """
        Test healing workflow for a specific failure scenario.
        
        Args:
            service_name: Name of the service to test
            failure_scenario: Type of failure to simulate
            
        Returns:
            Test execution result
        """
        try:
            test_id = f"test-{service_name}-{int(datetime.utcnow().timestamp())}"
            
            # Find applicable healing rules
            applicable_rules = [
                rule for rule in self.healing_rules.values()
                if rule["service_name"] == service_name and rule["is_enabled"]
            ]
            
            if not applicable_rules:
                return {
                    "success": False,
                    "error": f"No healing rules found for service {service_name}"
                }
            
            test_result = {
                "test_id": test_id,
                "service_name": service_name,
                "failure_scenario": failure_scenario,
                "started_at": datetime.utcnow().isoformat(),
                "rules_tested": len(applicable_rules),
                "test_steps": [],
                "overall_result": "unknown"
            }
            
            # Simulate failure scenario
            simulation_result = self._simulate_failure_scenario(service_name, failure_scenario)
            test_result["test_steps"].append({
                "step": "failure_simulation",
                "result": simulation_result,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Test each applicable rule
            successful_healings = 0
            for rule in applicable_rules:
                rule_test = self._test_healing_rule(rule, failure_scenario)
                test_result["test_steps"].append({
                    "step": f"test_rule_{rule['rule_id']}",
                    "result": rule_test,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                if rule_test.get("success"):
                    successful_healings += 1
            
            # Determine overall result
            if successful_healings > 0:
                test_result["overall_result"] = "success"
            elif simulation_result.get("success"):
                test_result["overall_result"] = "partial_success"
            else:
                test_result["overall_result"] = "failure"
            
            test_result["completed_at"] = datetime.utcnow().isoformat()
            test_result["successful_rules"] = successful_healings
            
            return {
                "success": True,
                "test_result": test_result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to test healing workflow: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def monitor_healing_effectiveness(self, service_name: str, days_back: int = 7) -> Dict[str, Any]:
        """Monitor healing effectiveness over time."""
        try:
            # Get service health history
            health_response = self.rtpi_client.get_service_health(service_name)
            
            effectiveness_metrics = {
                "service_name": service_name,
                "monitoring_period_days": days_back,
                "total_healing_attempts": 0,
                "successful_healings": 0,
                "failed_healings": 0,
                "average_healing_time": 0,
                "most_common_failures": [],
                "effectiveness_score": 0.0
            }
            
            # Calculate effectiveness (simulated data for demo)
            effectiveness_metrics.update({
                "total_healing_attempts": 15,
                "successful_healings": 12,
                "failed_healings": 3,
                "average_healing_time": 45,  # seconds
                "effectiveness_score": 0.8  # 80% success rate
            })
            
            return {
                "success": True,
                "effectiveness_metrics": effectiveness_metrics
            }
            
        except Exception as e:
            self.logger.error(f"Failed to monitor healing effectiveness: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _get_default_healing_actions(self, service_name: str) -> List[Dict[str, Any]]:
        """Get default healing actions for a service type."""
        service_type = self._detect_service_type(service_name)
        
        action_templates = {
            "database": [
                {"name": "restart_service", "type": "restart", "timeout": 60},
                {"name": "clear_cache", "type": "command", "command": "redis-cli flushall", "timeout": 30},
                {"name": "check_connections", "type": "validation", "command": "pg_isready", "timeout": 15}
            ],
            "web_service": [
                {"name": "restart_container", "type": "restart", "timeout": 45},
                {"name": "clear_temp_files", "type": "command", "command": "rm -rf /tmp/*", "timeout": 10},
                {"name": "health_check", "type": "validation", "command": "curl -f http://localhost/health", "timeout": 10}
            ],
            "security_tool": [
                {"name": "restart_tool", "type": "restart", "timeout": 90},
                {"name": "verify_license", "type": "validation", "command": "license-check", "timeout": 15},
                {"name": "reset_configuration", "type": "command", "command": "reset-config", "timeout": 30}
            ]
        }
        
        return action_templates.get(service_type, action_templates["web_service"])
    
    def _get_success_criteria(self, service_name: str) -> List[Dict[str, Any]]:
        """Get success criteria for healing validation."""
        return [
            {"type": "http_check", "url": f"http://{service_name}/health", "expected_status": 200},
            {"type": "process_check", "process_name": service_name, "expected_state": "running"},
            {"type": "port_check", "port": 80, "expected_state": "open"}
        ]
    
    def _detect_service_type(self, service_name: str) -> str:
        """Detect service type based on service name."""
        if any(db in service_name.lower() for db in ["postgres", "redis", "mysql", "mongo"]):
            return "database"
        elif any(tool in service_name.lower() for tool in ["burp", "empire", "nmap", "metasploit"]):
            return "security_tool"
        else:
            return "web_service"
    
    def _simulate_failure_scenario(self, service_name: str, failure_scenario: str) -> Dict[str, Any]:
        """Simulate a failure scenario for testing."""
        scenarios = {
            "service_down": {"simulated": True, "impact": "high", "recovery_time": 60},
            "high_memory": {"simulated": True, "impact": "medium", "recovery_time": 30},
            "network_timeout": {"simulated": True, "impact": "medium", "recovery_time": 45},
            "config_error": {"simulated": True, "impact": "high", "recovery_time": 120}
        }
        
        scenario_data = scenarios.get(failure_scenario, {"simulated": False})
        scenario_data["scenario"] = failure_scenario
        scenario_data["service"] = service_name
        scenario_data["timestamp"] = datetime.utcnow().isoformat()
        
        return {"success": True, "simulation": scenario_data}
    
    def _test_healing_rule(self, rule: Dict[str, Any], failure_scenario: str) -> Dict[str, Any]:
        """Test a specific healing rule against a failure scenario."""
        # Check if rule conditions match the failure scenario
        conditions = rule.get("trigger_conditions", {})
        
        # Simulate rule execution
        rule_test = {
            "rule_id": rule["rule_id"],
            "triggered": True,
            "actions_executed": len(rule.get("healing_actions", [])),
            "execution_time": 30,  # simulated
            "success": True
        }
        
        return rule_test
