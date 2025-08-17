"""
Security Policy Enforcer for cybersecurity AI workflow integration.

This tool enforces security policies automatically across infrastructure,
provides hardening capabilities, and manages security baselines.
"""

import logging
import subprocess
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ..shared.api_clients.rtpi_pen_client import RTPIPenClient
from ..shared.data_models.security_models import SecurityPolicy, PolicyViolation


class SecurityPolicyEnforcer:
    """
    Advanced security policy enforcer for automated infrastructure hardening.
    Provides policy enforcement, baseline management, and automated remediation.
    """
    
    def __init__(self):
        """Initialize the Security Policy Enforcer."""
        self.rtpi_client = RTPIPenClient("http://localhost:8080")
        self.logger = logging.getLogger("SecurityPolicyEnforcer")
        self.enforcement_history = []
        self.policy_templates = {
            "basic_hardening": self._get_basic_hardening_policies(),
            "enterprise_security": self._get_enterprise_security_policies(),
            "compliance_baseline": self._get_compliance_baseline_policies()
        }
    
    def enforce_security_baseline(self, target_systems: List[str] = Field(..., description="List of target systems"),
                                baseline_template: str = Field(..., description="Security baseline template to apply")) -> Dict[str, Any]:
        """
        Enforce security baseline across target systems.
        
        Args:
            target_systems: List of system identifiers to apply baseline to
            baseline_template: Template name for security baseline
            
        Returns:
            Enforcement results and status
        """
        try:
            enforcement_id = f"enforce-{int(datetime.utcnow().timestamp())}"
            
            if baseline_template not in self.policy_templates:
                return {
                    "success": False,
                    "error": f"Unknown baseline template: {baseline_template}. Available: {list(self.policy_templates.keys())}"
                }
            
            policies = self.policy_templates[baseline_template]
            
            enforcement_results = {
                "enforcement_id": enforcement_id,
                "baseline_template": baseline_template,
                "target_systems": target_systems,
                "started_at": datetime.utcnow().isoformat(),
                "policies_applied": len(policies),
                "system_results": {},
                "overall_success": True,
                "failed_systems": [],
                "applied_policies": []
            }
            
            for system_id in target_systems:
                system_result = self._apply_baseline_to_system(system_id, policies)
                enforcement_results["system_results"][system_id] = system_result
                
                if not system_result["success"]:
                    enforcement_results["overall_success"] = False
                    enforcement_results["failed_systems"].append(system_id)
                
                # Track applied policies
                enforcement_results["applied_policies"].extend(
                    system_result.get("applied_policies", [])
                )
            
            enforcement_results["completed_at"] = datetime.utcnow().isoformat()
            
            # Store enforcement history
            self.enforcement_history.append(enforcement_results)
            
            self.logger.info(f"Security baseline enforcement completed: {enforcement_id}")
            
            return {
                "success": enforcement_results["overall_success"],
                "enforcement_results": enforcement_results
            }
            
        except Exception as e:
            self.logger.error(f"Failed to enforce security baseline: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def apply_hardening_configurations(self, system_id: str = Field(..., description="System ID to harden"),
                                     hardening_level: str = Field(..., description="Hardening level (basic, intermediate, advanced)")) -> Dict[str, Any]:
        """
        Apply security hardening configurations to a system.
        
        Args:
            system_id: System identifier to apply hardening to
            hardening_level: Level of hardening to apply
            
        Returns:
            Hardening application results
        """
        try:
            hardening_configs = self._get_hardening_configurations(hardening_level)
            
            if not hardening_configs:
                return {
                    "success": False,
                    "error": f"Invalid hardening level: {hardening_level}. Valid levels: basic, intermediate, advanced"
                }
            
            hardening_result = {
                "system_id": system_id,
                "hardening_level": hardening_level,
                "started_at": datetime.utcnow().isoformat(),
                "applied_configurations": [],
                "failed_configurations": [],
                "overall_success": True
            }
            
            for config_name, config_data in hardening_configs.items():
                config_result = self._apply_hardening_config(system_id, config_name, config_data)
                
                if config_result["success"]:
                    hardening_result["applied_configurations"].append({
                        "name": config_name,
                        "result": config_result
                    })
                else:
                    hardening_result["failed_configurations"].append({
                        "name": config_name,
                        "error": config_result.get("error"),
                        "result": config_result
                    })
                    hardening_result["overall_success"] = False
            
            hardening_result["completed_at"] = datetime.utcnow().isoformat()
            
            return {
                "success": hardening_result["overall_success"],
                "hardening_result": hardening_result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to apply hardening configurations: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def manage_access_controls(self, system_id: str = Field(..., description="System ID"),
                             access_policy: Dict[str, Any] = Field(..., description="Access control policy")) -> Dict[str, Any]:
        """
        Manage and enforce access control policies.
        
        Args:
            system_id: System identifier
            access_policy: Access control policy configuration
            
        Returns:
            Access control management results
        """
        try:
            access_management = {
                "system_id": system_id,
                "policy_name": access_policy.get("name", "unnamed_policy"),
                "enforcement_date": datetime.utcnow().isoformat(),
                "access_controls_applied": [],
                "failed_controls": [],
                "users_affected": 0,
                "groups_modified": 0
            }
            
            # Apply user access controls
            if "user_rules" in access_policy:
                user_result = self._apply_user_access_controls(system_id, access_policy["user_rules"])
                access_management["access_controls_applied"].append(user_result)
                access_management["users_affected"] = user_result.get("users_processed", 0)
            
            # Apply group access controls
            if "group_rules" in access_policy:
                group_result = self._apply_group_access_controls(system_id, access_policy["group_rules"])
                access_management["access_controls_applied"].append(group_result)
                access_management["groups_modified"] = group_result.get("groups_processed", 0)
            
            # Apply role-based access controls
            if "rbac_rules" in access_policy:
                rbac_result = self._apply_rbac_controls(system_id, access_policy["rbac_rules"])
                access_management["access_controls_applied"].append(rbac_result)
            
            # Apply privilege escalation controls
            if "privilege_controls" in access_policy:
                privilege_result = self._apply_privilege_controls(system_id, access_policy["privilege_controls"])
                access_management["access_controls_applied"].append(privilege_result)
            
            return {
                "success": True,
                "access_management": access_management
            }
            
        except Exception as e:
            self.logger.error(f"Failed to manage access controls: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def automated_policy_remediation(self, violations: List[Dict[str, Any]] = Field(..., description="Policy violations to remediate")) -> Dict[str, Any]:
        """
        Automatically remediate policy violations where possible.
        
        Args:
            violations: List of policy violations to remediate
            
        Returns:
            Remediation results
        """
        try:
            remediation = {
                "remediation_id": f"remediate-{int(datetime.utcnow().timestamp())}",
                "started_at": datetime.utcnow().isoformat(),
                "total_violations": len(violations),
                "auto_remediated": 0,
                "manual_required": 0,
                "remediation_results": [],
                "failed_remediations": []
            }
            
            for violation in violations:
                remediation_result = self._attempt_auto_remediation(violation)
                
                if remediation_result["success"]:
                    remediation["auto_remediated"] += 1
                    remediation["remediation_results"].append(remediation_result)
                else:
                    if remediation_result.get("requires_manual"):
                        remediation["manual_required"] += 1
                    else:
                        remediation["failed_remediations"].append(remediation_result)
            
            remediation["completed_at"] = datetime.utcnow().isoformat()
            remediation["success_rate"] = round(
                (remediation["auto_remediated"] / len(violations)) * 100, 2
            ) if violations else 100.0
            
            return {
                "success": True,
                "remediation": remediation
            }
            
        except Exception as e:
            self.logger.error(f"Failed automated policy remediation: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def monitor_policy_compliance(self, system_ids: List[str] = Field(..., description="Systems to monitor"),
                                monitoring_interval: int = Field(default=3600, description="Monitoring interval in seconds")) -> Dict[str, Any]:
        """
        Monitor ongoing policy compliance across systems.
        
        Args:
            system_ids: List of systems to monitor
            monitoring_interval: How often to check compliance (seconds)
            
        Returns:
            Monitoring setup and initial status
        """
        try:
            monitoring_session = {
                "session_id": f"monitor-{int(datetime.utcnow().timestamp())}",
                "started_at": datetime.utcnow().isoformat(),
                "systems_monitored": system_ids,
                "monitoring_interval": monitoring_interval,
                "status": "active",
                "compliance_snapshots": [],
                "violations_detected": 0,
                "auto_corrections": 0
            }
            
            # Take initial compliance snapshot
            for system_id in system_ids:
                snapshot = self._take_compliance_snapshot(system_id)
                monitoring_session["compliance_snapshots"].append(snapshot)
                
                # Count any immediate violations
                violations = snapshot.get("violations", [])
                monitoring_session["violations_detected"] += len(violations)
            
            # In a real implementation, this would set up continuous monitoring
            # For now, we'll just return the initial setup
            
            return {
                "success": True,
                "monitoring_session": monitoring_session
            }
            
        except Exception as e:
            self.logger.error(f"Failed to setup policy compliance monitoring: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _get_basic_hardening_policies(self) -> Dict[str, Any]:
        """Get basic security hardening policies."""
        return {
            "disable_unnecessary_services": {
                "type": "service_management",
                "action": "disable",
                "services": ["telnet", "ftp", "rsh", "rlogin"],
                "criticality": "high"
            },
            "enable_firewall": {
                "type": "network_security",
                "action": "enable",
                "configuration": {
                    "default_policy": "deny",
                    "allowed_ports": [22, 80, 443]
                },
                "criticality": "critical"
            },
            "password_policy": {
                "type": "authentication",
                "action": "configure",
                "settings": {
                    "min_length": 12,
                    "complexity": True,
                    "expiration_days": 90,
                    "history_count": 5
                },
                "criticality": "high"
            },
            "audit_logging": {
                "type": "monitoring",
                "action": "enable",
                "configuration": {
                    "log_level": "info",
                    "retention_days": 90,
                    "remote_logging": True
                },
                "criticality": "high"
            }
        }
    
    def _get_enterprise_security_policies(self) -> Dict[str, Any]:
        """Get enterprise-level security policies."""
        basic_policies = self._get_basic_hardening_policies()
        
        enterprise_policies = {
            "advanced_threat_detection": {
                "type": "monitoring",
                "action": "enable",
                "configuration": {
                    "behavioral_analysis": True,
                    "anomaly_detection": True,
                    "threat_intelligence": True
                },
                "criticality": "high"
            },
            "network_segmentation": {
                "type": "network_security",
                "action": "configure",
                "configuration": {
                    "vlans": True,
                    "micro_segmentation": True,
                    "zero_trust": True
                },
                "criticality": "critical"
            },
            "endpoint_protection": {
                "type": "endpoint_security",
                "action": "deploy",
                "configuration": {
                    "antivirus": True,
                    "edr": True,
                    "application_whitelisting": True
                },
                "criticality": "critical"
            }
        }
        
        # Merge basic and enterprise policies
        return {**basic_policies, **enterprise_policies}
    
    def _get_compliance_baseline_policies(self) -> Dict[str, Any]:
        """Get compliance-focused security policies."""
        return {
            "data_encryption": {
                "type": "encryption",
                "action": "enforce",
                "configuration": {
                    "at_rest": True,
                    "in_transit": True,
                    "key_management": "automated",
                    "algorithm": "AES-256"
                },
                "criticality": "critical"
            },
            "access_logging": {
                "type": "audit",
                "action": "enable",
                "configuration": {
                    "user_access": True,
                    "admin_access": True,
                    "failed_attempts": True,
                    "privilege_escalation": True
                },
                "criticality": "critical"
            },
            "backup_policies": {
                "type": "data_protection",
                "action": "configure",
                "configuration": {
                    "frequency": "daily",
                    "retention": "1_year",
                    "encryption": True,
                    "offsite": True
                },
                "criticality": "high"
            },
            "incident_response": {
                "type": "security_operations",
                "action": "setup",
                "configuration": {
                    "automated_detection": True,
                    "escalation_procedures": True,
                    "forensic_capabilities": True
                },
                "criticality": "high"
            }
        }
    
    def _apply_baseline_to_system(self, system_id: str, policies: Dict[str, Any]) -> Dict[str, Any]:
        """Apply security baseline policies to a specific system."""
        system_result = {
            "system_id": system_id,
            "success": True,
            "applied_policies": [],
            "failed_policies": [],
            "warnings": []
        }
        
        for policy_name, policy_config in policies.items():
            policy_result = self._apply_single_policy(system_id, policy_name, policy_config)
            
            if policy_result["success"]:
                system_result["applied_policies"].append(policy_result)
            else:
                system_result["failed_policies"].append(policy_result)
                system_result["success"] = False
            
            # Collect warnings
            if policy_result.get("warnings"):
                system_result["warnings"].extend(policy_result["warnings"])
        
        return system_result
    
    def _apply_single_policy(self, system_id: str, policy_name: str, policy_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a single security policy to a system."""
        result = {
            "policy_name": policy_name,
            "policy_type": policy_config.get("type"),
            "action": policy_config.get("action"),
            "success": False,
            "applied_at": datetime.utcnow().isoformat(),
            "warnings": []
        }
        
        try:
            policy_type = policy_config.get("type")
            action = policy_config.get("action")
            configuration = policy_config.get("configuration", {})
            
            if policy_type == "service_management":
                result.update(self._apply_service_policy(system_id, action, configuration))
            
            elif policy_type == "network_security":
                result.update(self._apply_network_policy(system_id, action, configuration))
            
            elif policy_type == "authentication":
                result.update(self._apply_auth_policy(system_id, action, configuration))
            
            elif policy_type == "monitoring":
                result.update(self._apply_monitoring_policy(system_id, action, configuration))
            
            elif policy_type == "encryption":
                result.update(self._apply_encryption_policy(system_id, action, configuration))
            
            elif policy_type == "endpoint_security":
                result.update(self._apply_endpoint_policy(system_id, action, configuration))
            
            else:
                result["warnings"].append(f"Unknown policy type: {policy_type}")
                result["success"] = True  # Don't fail for unknown types
            
        except Exception as e:
            result["error"] = str(e)
            result["success"] = False
        
        return result
    
    def _apply_service_policy(self, system_id: str, action: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply service management policy."""
        if action == "disable":
            services = config.get("services", [])
            disabled_services = []
            
            for service in services:
                # Simulate service disabling
                try:
                    # In real implementation: subprocess.run(["systemctl", "disable", service])
                    disabled_services.append(service)
                    self.logger.info(f"Disabled service {service} on {system_id}")
                except Exception as e:
                    return {"success": False, "error": f"Failed to disable {service}: {str(e)}"}
            
            return {
                "success": True,
                "disabled_services": disabled_services,
                "details": f"Disabled {len(disabled_services)} unnecessary services"
            }
        
        return {"success": True, "details": f"Service management action '{action}' completed"}
    
    def _apply_network_policy(self, system_id: str, action: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply network security policy."""
        if action == "enable" or action == "configure":
            # Simulate firewall configuration
            rules_applied = []
            
            default_policy = config.get("default_policy", "deny")
            allowed_ports = config.get("allowed_ports", [])
            
            rules_applied.append(f"Set default policy to {default_policy}")
            
            for port in allowed_ports:
                rules_applied.append(f"Allow inbound traffic on port {port}")
            
            return {
                "success": True,
                "rules_applied": rules_applied,
                "details": f"Configured firewall with {len(rules_applied)} rules"
            }
        
        return {"success": True, "details": f"Network policy action '{action}' completed"}
    
    def _apply_auth_policy(self, system_id: str, action: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply authentication policy."""
        if action == "configure":
            settings_applied = []
            
            min_length = config.get("min_length", 8)
            complexity = config.get("complexity", False)
            expiration = config.get("expiration_days", 0)
            
            settings_applied.append(f"Set minimum password length to {min_length}")
            
            if complexity:
                settings_applied.append("Enabled password complexity requirements")
            
            if expiration > 0:
                settings_applied.append(f"Set password expiration to {expiration} days")
            
            return {
                "success": True,
                "settings_applied": settings_applied,
                "details": f"Applied {len(settings_applied)} password policy settings"
            }
        
        return {"success": True, "details": f"Authentication policy action '{action}' completed"}
    
    def _apply_monitoring_policy(self, system_id: str, action: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply monitoring policy."""
        if action == "enable":
            monitoring_enabled = []
            
            log_level = config.get("log_level", "info")
            retention = config.get("retention_days", 30)
            remote_logging = config.get("remote_logging", False)
            
            monitoring_enabled.append(f"Set log level to {log_level}")
            monitoring_enabled.append(f"Set log retention to {retention} days")
            
            if remote_logging:
                monitoring_enabled.append("Enabled remote logging")
            
            return {
                "success": True,
                "monitoring_enabled": monitoring_enabled,
                "details": f"Configured {len(monitoring_enabled)} monitoring settings"
            }
        
        return {"success": True, "details": f"Monitoring policy action '{action}' completed"}
    
    def _apply_encryption_policy(self, system_id: str, action: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply encryption policy."""
        if action == "enforce":
            encryption_applied = []
            
            if config.get("at_rest"):
                encryption_applied.append("Enabled encryption at rest")
            
            if config.get("in_transit"):
                encryption_applied.append("Enabled encryption in transit")
            
            algorithm = config.get("algorithm", "AES-256")
            encryption_applied.append(f"Configured {algorithm} encryption")
            
            return {
                "success": True,
                "encryption_applied": encryption_applied,
                "details": f"Applied {len(encryption_applied)} encryption settings"
            }
        
        return {"success": True, "details": f"Encryption policy action '{action}' completed"}
    
    def _apply_endpoint_policy(self, system_id: str, action: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply endpoint security policy."""
        if action == "deploy":
            protections_deployed = []
            
            if config.get("antivirus"):
                protections_deployed.append("Deployed antivirus protection")
            
            if config.get("edr"):
                protections_deployed.append("Deployed EDR solution")
            
            if config.get("application_whitelisting"):
                protections_deployed.append("Enabled application whitelisting")
            
            return {
                "success": True,
                "protections_deployed": protections_deployed,
                "details": f"Deployed {len(protections_deployed)} endpoint protections"
            }
        
        return {"success": True, "details": f"Endpoint policy action '{action}' completed"}
    
    def _get_hardening_configurations(self, hardening_level: str) -> Optional[Dict[str, Any]]:
        """Get hardening configurations for specified level."""
        hardening_configs = {
            "basic": {
                "disable_unused_services": {
                    "services": ["telnet", "ftp", "tftp"],
                    "criticality": "high"
                },
                "update_default_passwords": {
                    "accounts": ["admin", "root", "service"],
                    "criticality": "critical"
                },
                "enable_automatic_updates": {
                    "security_updates": True,
                    "reboot_required": True,
                    "criticality": "medium"
                }
            },
            "intermediate": {
                "configure_fail2ban": {
                    "services": ["ssh", "apache", "nginx"],
                    "ban_time": 3600,
                    "criticality": "high"
                },
                "ssl_hardening": {
                    "disable_ssl_v2": True,
                    "disable_ssl_v3": True,
                    "cipher_suites": "secure_only",
                    "criticality": "high"
                },
                "file_permissions": {
                    "system_files": "0644",
                    "executables": "0755",
                    "sensitive_configs": "0600",
                    "criticality": "medium"
                }
            },
            "advanced": {
                "kernel_hardening": {
                    "aslr": True,
                    "dep": True,
                    "smep": True,
                    "criticality": "high"
                },
                "network_hardening": {
                    "ip_forwarding": False,
                    "syn_cookies": True,
                    "icmp_redirects": False,
                    "criticality": "high"
                },
                "mandatory_access_control": {
                    "selinux": True,
                    "apparmor": True,
                    "grsecurity": False,
                    "criticality": "medium"
                }
            }
        }
        
        return hardening_configs.get(hardening_level)
    
    def _apply_hardening_config(self, system_id: str, config_name: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply specific hardening configuration."""
        # Simulate hardening configuration application
        return {
            "success": True,
            "config_name": config_name,
            "system_id": system_id,
            "applied_at": datetime.utcnow().isoformat(),
            "details": f"Applied {config_name} hardening configuration"
        }
    
    def _apply_user_access_controls(self, system_id: str, user_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Apply user access control rules."""
        return {
            "control_type": "user_access",
            "users_processed": user_rules.get("user_count", 0),
            "rules_applied": len(user_rules.get("rules", [])),
            "success": True
        }
    
    def _apply_group_access_controls(self, system_id: str, group_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Apply group access control rules."""
        return {
            "control_type": "group_access",
            "groups_processed": group_rules.get("group_count", 0),
            "rules_applied": len(group_rules.get("rules", [])),
            "success": True
        }
    
    def _apply_rbac_controls(self, system_id: str, rbac_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Apply role-based access control rules."""
        return {
            "control_type": "rbac",
            "roles_configured": len(rbac_rules.get("roles", [])),
            "permissions_set": len(rbac_rules.get("permissions", [])),
            "success": True
        }
    
    def _apply_privilege_controls(self, system_id: str, privilege_controls: Dict[str, Any]) -> Dict[str, Any]:
        """Apply privilege escalation controls."""
        return {
            "control_type": "privilege_escalation",
            "sudo_rules": len(privilege_controls.get("sudo_rules", [])),
            "admin_controls": len(privilege_controls.get("admin_controls", [])),
            "success": True
        }
    
    def _attempt_auto_remediation(self, violation: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt automatic remediation of a policy violation."""
        violation_type = violation.get("type", "unknown")
        
        # Define auto-remediable violation types
        auto_remediable = {
            "weak_password": {
                "action": "force_password_reset",
                "requires_manual": False
            },
            "disabled_logging": {
                "action": "enable_logging",
                "requires_manual": False
            },
            "open_port": {
                "action": "close_port",
                "requires_manual": True  # Might break services
            },
            "outdated_software": {
                "action": "update_software",
                "requires_manual": True  # Requires testing
            }
        }
        
        remediation_config = auto_remediable.get(violation_type)
        
        if not remediation_config:
            return {
                "success": False,
                "violation_id": violation.get("id"),
                "requires_manual": True,
                "reason": "No automatic remediation available"
            }
        
        if remediation_config["requires_manual"]:
            return {
                "success": False,
                "violation_id": violation.get("id"),
                "requires_manual": True,
                "reason": "Remediation requires manual intervention"
            }
        
        # Simulate automatic remediation
        return {
            "success": True,
            "violation_id": violation.get("id"),
            "action_taken": remediation_config["action"],
            "remediated_at": datetime.utcnow().isoformat()
        }
    
    def _take_compliance_snapshot(self, system_id: str) -> Dict[str, Any]:
        """Take a compliance snapshot of a system."""
        # Simulate compliance check
        snapshot = {
            "system_id": system_id,
            "snapshot_time": datetime.utcnow().isoformat(),
            "compliance_score": 85.0,  # Simulated score
            "violations": [],
            "compliant_policies": [],
            "policy_count": 10
        }
        
        # Simulate some violations for demonstration
        if system_id.endswith("1"):  # Simulate different compliance states
            snapshot["violations"] = [
                {"type": "weak_password", "severity": "medium"},
                {"type": "disabled_logging", "severity": "high"}
            ]
            snapshot["compliance_score"] = 70.0
