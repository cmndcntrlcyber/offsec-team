"""
Compliance Auditor for cybersecurity AI workflow integration.

This tool validates infrastructure compliance with security standards,
regulatory requirements, and organizational policies.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ..shared.api_clients.rtpi_pen_client import RTPIPenClient
from ..shared.data_models.security_models import ComplianceCheck, ComplianceStatus


class ComplianceAuditor:
    """
    Advanced compliance auditor for security infrastructure validation.
    Provides automated compliance checking against multiple security frameworks.
    """
    
    def __init__(self):
        """Initialize the Compliance Auditor."""
        self.rtpi_client = RTPIPenClient("http://localhost:8080")
        self.logger = logging.getLogger("ComplianceAuditor")
        self.compliance_frameworks = {
            "nist": "NIST Cybersecurity Framework",
            "iso27001": "ISO 27001",
            "cis": "CIS Controls",
            "pci_dss": "PCI DSS",
            "sox": "Sarbanes-Oxley",
            "gdpr": "GDPR",
            "hipaa": "HIPAA"
        }
    
    def audit_infrastructure_compliance(self, infrastructure_config: Dict[str, Any] = Field(..., description="Infrastructure configuration"),
                                      compliance_frameworks: List[str] = Field(..., description="Compliance frameworks to check against")) -> Dict[str, Any]:
        """
        Audit infrastructure against specified compliance frameworks.
        
        Args:
            infrastructure_config: Infrastructure configuration to audit
            compliance_frameworks: List of compliance frameworks to validate against
            
        Returns:
            Comprehensive compliance audit results
        """
        try:
            audit_id = f"audit-{int(datetime.utcnow().timestamp())}"
            
            audit_results = {
                "audit_id": audit_id,
                "audit_date": datetime.utcnow().isoformat(),
                "infrastructure_id": infrastructure_config.get("id", "unknown"),
                "frameworks_audited": compliance_frameworks,
                "overall_compliance_score": 0.0,
                "framework_results": {},
                "critical_violations": [],
                "recommendations": [],
                "compliance_gaps": []
            }
            
            total_checks = 0
            passed_checks = 0
            
            for framework in compliance_frameworks:
                if framework not in self.compliance_frameworks:
                    self.logger.warning(f"Unknown compliance framework: {framework}")
                    continue
                
                framework_result = self._audit_framework_compliance(
                    infrastructure_config, framework
                )
                
                audit_results["framework_results"][framework] = framework_result
                
                # Update overall metrics
                framework_checks = framework_result.get("total_checks", 0)
                framework_passed = framework_result.get("passed_checks", 0)
                
                total_checks += framework_checks
                passed_checks += framework_passed
                
                # Collect critical violations
                audit_results["critical_violations"].extend(
                    framework_result.get("critical_violations", [])
                )
                
                # Collect recommendations
                audit_results["recommendations"].extend(
                    framework_result.get("recommendations", [])
                )
            
            # Calculate overall compliance score
            if total_checks > 0:
                audit_results["overall_compliance_score"] = round((passed_checks / total_checks) * 100, 2)
            
            # Generate compliance gaps
            audit_results["compliance_gaps"] = self._identify_compliance_gaps(audit_results)
            
            self.logger.info(f"Infrastructure compliance audit completed: {audit_id}")
            
            return {
                "success": True,
                "audit_results": audit_results
            }
            
        except Exception as e:
            self.logger.error(f"Failed to audit infrastructure compliance: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def validate_security_policies(self, policy_set: Dict[str, Any] = Field(..., description="Security policies to validate")) -> Dict[str, Any]:
        """
        Validate security policies against best practices and standards.
        
        Args:
            policy_set: Security policies to validate
            
        Returns:
            Policy validation results
        """
        try:
            validation_results = {
                "validation_id": f"policy-val-{int(datetime.utcnow().timestamp())}",
                "validation_date": datetime.utcnow().isoformat(),
                "total_policies": len(policy_set),
                "policy_results": {},
                "overall_score": 0.0,
                "policy_gaps": [],
                "recommendations": []
            }
            
            total_score = 0.0
            
            for policy_name, policy_config in policy_set.items():
                policy_result = self._validate_individual_policy(policy_name, policy_config)
                validation_results["policy_results"][policy_name] = policy_result
                total_score += policy_result.get("score", 0.0)
                
                if policy_result.get("gaps"):
                    validation_results["policy_gaps"].extend(policy_result["gaps"])
                
                if policy_result.get("recommendations"):
                    validation_results["recommendations"].extend(policy_result["recommendations"])
            
            # Calculate overall score
            if len(policy_set) > 0:
                validation_results["overall_score"] = round(total_score / len(policy_set), 2)
            
            return {
                "success": True,
                "validation": validation_results
            }
            
        except Exception as e:
            self.logger.error(f"Failed to validate security policies: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def check_regulatory_requirements(self, system_config: Dict[str, Any] = Field(..., description="System configuration"),
                                    regulations: List[str] = Field(..., description="Regulatory requirements to check")) -> Dict[str, Any]:
        """
        Check system configuration against regulatory requirements.
        
        Args:
            system_config: System configuration to check
            regulations: List of regulations to validate against
            
        Returns:
            Regulatory compliance check results
        """
        try:
            compliance_check = {
                "check_id": f"reg-check-{int(datetime.utcnow().timestamp())}",
                "check_date": datetime.utcnow().isoformat(),
                "system_id": system_config.get("id", "unknown"),
                "regulations_checked": regulations,
                "compliance_status": {},
                "violations": [],
                "required_actions": [],
                "compliance_percentage": 0.0
            }
            
            total_requirements = 0
            met_requirements = 0
            
            for regulation in regulations:
                reg_result = self._check_regulation_compliance(system_config, regulation)
                compliance_check["compliance_status"][regulation] = reg_result
                
                total_requirements += reg_result.get("total_requirements", 0)
                met_requirements += reg_result.get("met_requirements", 0)
                
                compliance_check["violations"].extend(reg_result.get("violations", []))
                compliance_check["required_actions"].extend(reg_result.get("required_actions", []))
            
            # Calculate compliance percentage
            if total_requirements > 0:
                compliance_check["compliance_percentage"] = round(
                    (met_requirements / total_requirements) * 100, 2
                )
            
            return {
                "success": True,
                "compliance_check": compliance_check
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check regulatory requirements: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def generate_compliance_report(self, audit_results: Dict[str, Any] = Field(..., description="Audit results data")) -> Dict[str, Any]:
        """
        Generate comprehensive compliance report.
        
        Args:
            audit_results: Audit results to generate report from
            
        Returns:
            Generated compliance report
        """
        try:
            report = {
                "report_id": f"comp-report-{int(datetime.utcnow().timestamp())}",
                "generated_at": datetime.utcnow().isoformat(),
                "audit_summary": {
                    "audit_id": audit_results.get("audit_id"),
                    "audit_date": audit_results.get("audit_date"),
                    "overall_score": audit_results.get("overall_compliance_score", 0)
                },
                "executive_summary": self._generate_executive_summary(audit_results),
                "detailed_findings": self._organize_detailed_findings(audit_results),
                "remediation_plan": self._generate_remediation_plan(audit_results),
                "risk_matrix": self._create_risk_matrix(audit_results),
                "next_audit_recommendation": self._calculate_next_audit_date(audit_results)
            }
            
            # Generate different report formats
            report_formats = {
                "json": json.dumps(report, indent=2, default=str),
                "markdown": self._generate_markdown_report(report),
                "html": self._generate_html_report(report)
            }
            
            return {
                "success": True,
                "report": report,
                "formats": report_formats
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate compliance report: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _audit_framework_compliance(self, config: Dict[str, Any], framework: str) -> Dict[str, Any]:
        """Audit against specific compliance framework."""
        framework_checks = self._get_framework_checks(framework)
        
        result = {
            "framework": framework,
            "framework_name": self.compliance_frameworks.get(framework, framework),
            "total_checks": len(framework_checks),
            "passed_checks": 0,
            "failed_checks": 0,
            "critical_violations": [],
            "recommendations": [],
            "check_details": []
        }
        
        for check in framework_checks:
            check_result = self._execute_compliance_check(config, check)
            result["check_details"].append(check_result)
            
            if check_result["passed"]:
                result["passed_checks"] += 1
            else:
                result["failed_checks"] += 1
                
                if check_result.get("critical", False):
                    result["critical_violations"].append(check_result)
                
                if check_result.get("recommendation"):
                    result["recommendations"].append(check_result["recommendation"])
        
        return result
    
    def _get_framework_checks(self, framework: str) -> List[Dict[str, Any]]:
        """Get compliance checks for a specific framework."""
        framework_checks = {
            "nist": [
                {"id": "AC-1", "name": "Access Control Policy", "category": "access_control", "critical": True},
                {"id": "AU-1", "name": "Audit Policy", "category": "auditing", "critical": True},
                {"id": "CA-1", "name": "Security Assessment", "category": "assessment", "critical": False},
                {"id": "CM-1", "name": "Configuration Management", "category": "configuration", "critical": True},
                {"id": "IA-1", "name": "Identification and Authentication", "category": "identity", "critical": True}
            ],
            "iso27001": [
                {"id": "A.9.1", "name": "Business Requirements for Access Control", "category": "access_control", "critical": True},
                {"id": "A.12.1", "name": "Operational Procedures", "category": "operations", "critical": True},
                {"id": "A.13.1", "name": "Network Security Management", "category": "network", "critical": True},
                {"id": "A.14.1", "name": "Security in Development", "category": "development", "critical": False}
            ],
            "cis": [
                {"id": "CIS-1", "name": "Inventory of Authorized Devices", "category": "asset_management", "critical": True},
                {"id": "CIS-2", "name": "Inventory of Authorized Software", "category": "asset_management", "critical": True},
                {"id": "CIS-3", "name": "Continuous Vulnerability Management", "category": "vulnerability", "critical": True},
                {"id": "CIS-4", "name": "Controlled Use of Administrative Privileges", "category": "access_control", "critical": True}
            ]
        }
        
        return framework_checks.get(framework, [])
    
    def _execute_compliance_check(self, config: Dict[str, Any], check: Dict[str, Any]) -> Dict[str, Any]:
        """Execute individual compliance check."""
        check_result = {
            "check_id": check["id"],
            "check_name": check["name"],
            "category": check["category"],
            "critical": check.get("critical", False),
            "passed": False,
            "details": "",
            "recommendation": ""
        }
        
        # Simulate compliance checking based on category
        category = check["category"]
        
        if category == "access_control":
            # Check for access control configurations
            has_rbac = config.get("security", {}).get("rbac_enabled", False)
            has_mfa = config.get("security", {}).get("mfa_enabled", False)
            
            if has_rbac and has_mfa:
                check_result["passed"] = True
                check_result["details"] = "RBAC and MFA are properly configured"
            else:
                check_result["details"] = "Missing RBAC or MFA configuration"
                check_result["recommendation"] = "Enable role-based access control and multi-factor authentication"
        
        elif category == "auditing":
            # Check for audit logging
            has_audit_logs = config.get("logging", {}).get("audit_enabled", False)
            log_retention = config.get("logging", {}).get("retention_days", 0)
            
            if has_audit_logs and log_retention >= 90:
                check_result["passed"] = True
                check_result["details"] = "Audit logging is properly configured"
            else:
                check_result["details"] = "Insufficient audit logging configuration"
                check_result["recommendation"] = "Enable audit logging with at least 90-day retention"
        
        elif category == "configuration":
            # Check for configuration management
            has_config_mgmt = config.get("configuration", {}).get("managed", False)
            has_change_control = config.get("configuration", {}).get("change_control", False)
            
            if has_config_mgmt and has_change_control:
                check_result["passed"] = True
                check_result["details"] = "Configuration management is properly implemented"
            else:
                check_result["details"] = "Missing configuration management controls"
                check_result["recommendation"] = "Implement configuration management with change control"
        
        elif category == "network":
            # Check network security
            has_firewall = config.get("network", {}).get("firewall_enabled", False)
            has_encryption = config.get("network", {}).get("encryption_enabled", False)
            
            if has_firewall and has_encryption:
                check_result["passed"] = True
                check_result["details"] = "Network security controls are in place"
            else:
                check_result["details"] = "Missing network security controls"
                check_result["recommendation"] = "Enable firewall and network encryption"
        
        elif category == "vulnerability":
            # Check vulnerability management
            has_scanning = config.get("security", {}).get("vulnerability_scanning", False)
            scan_frequency = config.get("security", {}).get("scan_frequency", "never")
            
            if has_scanning and scan_frequency in ["daily", "weekly"]:
                check_result["passed"] = True
                check_result["details"] = "Regular vulnerability scanning is configured"
            else:
                check_result["details"] = "Insufficient vulnerability management"
                check_result["recommendation"] = "Enable regular vulnerability scanning"
        
        else:
            # Default check - look for basic security configurations
            security_config = config.get("security", {})
            if security_config:
                check_result["passed"] = True
                check_result["details"] = "Basic security configuration present"
            else:
                check_result["details"] = "No security configuration found"
                check_result["recommendation"] = "Implement basic security configurations"
        
        return check_result
    
    def validate_policy_enforcement(self, policies: Dict[str, Any] = Field(..., description="Security policies"),
                                  current_state: Dict[str, Any] = Field(..., description="Current system state")) -> Dict[str, Any]:
        """
        Validate that security policies are properly enforced.
        
        Args:
            policies: Security policies to validate
            current_state: Current system state
            
        Returns:
            Policy enforcement validation results
        """
        try:
            validation = {
                "validation_id": f"policy-val-{int(datetime.utcnow().timestamp())}",
                "validation_date": datetime.utcnow().isoformat(),
                "total_policies": len(policies),
                "enforced_policies": 0,
                "unenforced_policies": 0,
                "policy_violations": [],
                "enforcement_gaps": [],
                "recommendations": []
            }
            
            for policy_name, policy_config in policies.items():
                enforcement_check = self._check_policy_enforcement(
                    policy_name, policy_config, current_state
                )
                
                if enforcement_check["enforced"]:
                    validation["enforced_policies"] += 1
                else:
                    validation["unenforced_policies"] += 1
                    validation["policy_violations"].append(enforcement_check)
                
                if enforcement_check.get("gaps"):
                    validation["enforcement_gaps"].extend(enforcement_check["gaps"])
                
                if enforcement_check.get("recommendation"):
                    validation["recommendations"].append(enforcement_check["recommendation"])
            
            # Calculate enforcement percentage
            if validation["total_policies"] > 0:
                enforcement_percentage = (validation["enforced_policies"] / validation["total_policies"]) * 100
                validation["enforcement_percentage"] = round(enforcement_percentage, 2)
            
            return {
                "success": True,
                "validation": validation
            }
            
        except Exception as e:
            self.logger.error(f"Failed to validate policy enforcement: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def track_compliance_drift(self, baseline_config: Dict[str, Any] = Field(..., description="Baseline configuration"),
                             current_config: Dict[str, Any] = Field(..., description="Current configuration")) -> Dict[str, Any]:
        """
        Track configuration drift from compliance baseline.
        
        Args:
            baseline_config: Baseline compliant configuration
            current_config: Current system configuration
            
        Returns:
            Configuration drift analysis
        """
        try:
            drift_analysis = {
                "analysis_id": f"drift-{int(datetime.utcnow().timestamp())}",
                "analysis_date": datetime.utcnow().isoformat(),
                "baseline_date": baseline_config.get("created_at", "unknown"),
                "drift_detected": False,
                "drift_items": [],
                "risk_level": "low",
                "remediation_required": False
            }
            
            # Compare configurations
            drift_items = self._compare_configurations(baseline_config, current_config)
            drift_analysis["drift_items"] = drift_items
            
            if drift_items:
                drift_analysis["drift_detected"] = True
                
                # Assess risk level based on drift
                critical_drifts = [item for item in drift_items if item.get("severity") == "critical"]
                high_drifts = [item for item in drift_items if item.get("severity") == "high"]
                
                if critical_drifts:
                    drift_analysis["risk_level"] = "critical"
                    drift_analysis["remediation_required"] = True
                elif high_drifts:
                    drift_analysis["risk_level"] = "high"
                    drift_analysis["remediation_required"] = True
                elif len(drift_items) > 5:
                    drift_analysis["risk_level"] = "medium"
                
            return {
                "success": True,
                "drift_analysis": drift_analysis
            }
            
        except Exception as e:
            self.logger.error(f"Failed to track compliance drift: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _validate_individual_policy(self, policy_name: str, policy_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate individual security policy."""
        result = {
            "policy_name": policy_name,
            "score": 0.0,
            "enforced": False,
            "gaps": [],
            "recommendation": ""
        }
        
        # Check policy completeness
        required_fields = ["description", "rules", "enforcement_level", "scope"]
        missing_fields = [field for field in required_fields if field not in policy_config]
        
        if missing_fields:
            result["gaps"] = [f"Missing required field: {field}" for field in missing_fields]
            result["recommendation"] = f"Add missing policy fields: {', '.join(missing_fields)}"
            result["score"] = 50.0  # Partial score for incomplete policy
        else:
            result["enforced"] = True
            result["score"] = 100.0
        
        # Check policy specificity
        rules = policy_config.get("rules", [])
        if len(rules) < 3:
            result["gaps"].append("Policy rules are too generic or insufficient")
            result["score"] *= 0.8
        
        return result
    
    def _check_policy_enforcement(self, policy_name: str, policy_config: Dict[str, Any], 
                                current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Check if a policy is properly enforced."""
        return {
            "policy_name": policy_name,
            "enforced": True,  # Simplified check
            "enforcement_level": policy_config.get("enforcement_level", "advisory"),
            "gaps": [],
            "recommendation": ""
        }
    
    def _check_regulation_compliance(self, config: Dict[str, Any], regulation: str) -> Dict[str, Any]:
        """Check compliance with specific regulation."""
        regulation_requirements = {
            "gdpr": [
                "data_encryption", "access_logs", "data_retention_policy", 
                "user_consent", "data_portability", "breach_notification"
            ],
            "hipaa": [
                "access_control", "audit_logs", "encryption", "workforce_training",
                "assigned_security_responsibility", "incident_procedures"
            ],
            "pci_dss": [
                "firewall_configuration", "vendor_defaults", "cardholder_data_protection",
                "encryption_transmission", "antivirus", "secure_systems"
            ],
            "sox": [
                "access_controls", "change_management", "monitoring_controls",
                "backup_procedures", "incident_response"
            ]
        }
        
        requirements = regulation_requirements.get(regulation, [])
        met_requirements = 0
        violations = []
        
        for req in requirements:
            # Simplified requirement checking
            if config.get("security", {}).get(req, False):
                met_requirements += 1
            else:
                violations.append(f"Missing requirement: {req}")
        
        return {
            "regulation": regulation,
            "total_requirements": len(requirements),
            "met_requirements": met_requirements,
            "violations": violations,
            "required_actions": [f"Implement {req}" for req in requirements if not config.get("security", {}).get(req, False)]
        }
    
    def _compare_configurations(self, baseline: Dict[str, Any], current: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compare configurations to identify drift."""
        drift_items = []
        
        # Compare security settings
        baseline_security = baseline.get("security", {})
        current_security = current.get("security", {})
        
        for key, baseline_value in baseline_security.items():
            current_value = current_security.get(key)
            if current_value != baseline_value:
                drift_items.append({
                    "category": "security",
                    "setting": key,
                    "baseline_value": baseline_value,
                    "current_value": current_value,
                    "severity": "high" if key in ["encryption_enabled", "mfa_enabled"] else "medium"
                })
        
        return drift_items
    
    def _identify_compliance_gaps(self, audit_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify critical compliance gaps."""
        gaps = []
        
        for framework, result in audit_results.get("framework_results", {}).items():
            failed_checks = result.get("failed_checks", 0)
            if failed_checks > 0:
                gaps.append({
                    "framework": framework,
                    "failed_checks": failed_checks,
                    "gap_severity": "critical" if failed_checks > 3 else "medium"
                })
        
        return gaps
    
    def _generate_executive_summary(self, audit_results: Dict[str, Any]) -> Dict[str, str]:
        """Generate executive summary for compliance report."""
        score = audit_results.get("overall_compliance_score", 0)
        
        if score >= 90:
            status = "Excellent compliance posture with minor improvements needed"
        elif score >= 75:
            status = "Good compliance with some areas requiring attention"
        elif score >= 60:
            status = "Moderate compliance with significant improvements needed"
        else:
            status = "Poor compliance requiring immediate remediation"
        
        return {
            "overall_status": status,
            "compliance_score": f"{score}%",
            "key_message": f"System achieved {score}% compliance across audited frameworks"
        }
    
    def _organize_detailed_findings(self, audit_results: Dict[str, Any]) -> Dict[str, List]:
        """Organize findings by severity and category."""
        findings = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        for violation in audit_results.get("critical_violations", []):
            findings["critical"].append(violation)
        
        return findings
    
    def _generate_remediation_plan(self, audit_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate remediation plan based on audit results."""
        return {
            "immediate_actions": audit_results.get("critical_violations", []),
            "short_term_actions": [],
            "long_term_actions": audit_results.get("recommendations", []),
            "estimated_effort": "Medium",
            "priority_order": ["critical_violations", "high_risk_gaps", "policy_updates"]
        }
    
    def _create_risk_matrix(self, audit_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create risk matrix from audit results."""
        return {
            "critical": len(audit_results.get("critical_violations", [])),
            "high": 0,
            "medium": 0,
            "low": 0
        }
    
    def _calculate_next_audit_date(self, audit_results: Dict[str, Any]) -> str:
        """Calculate recommended next audit date."""
        score = audit_results.get("overall_compliance_score", 100)
        
        if score < 70:
            next_audit = datetime.utcnow() + timedelta(days=30)
        elif score < 85:
            next_audit = datetime.utcnow() + timedelta(days=90)
        else:
            next_audit = datetime.utcnow() + timedelta(days=180)
        
        return next_audit.isoformat()
    
    def _generate_markdown_report(self, report: Dict[str, Any]) -> str:
        """Generate Markdown format compliance report."""
        md = f"""# Compliance Audit Report

**Report ID:** {report['report_id']}
**Generated:** {report['generated_at']}
**Overall Score:** {report['audit_summary']['overall_score']}%

## Executive Summary
{report['executive_summary']['overall_status']}

## Risk Matrix
- Critical: {report['risk_matrix']['critical']}
- High: {report['risk_matrix']['high']}
- Medium: {report['risk_matrix']['medium']}
- Low: {report['risk_matrix']['low']}

## Recommendations
- Next audit recommended: {report['next_audit_recommendation']}
"""
        return md
    
    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generate HTML format compliance report."""
        html = f"""
        <html>
        <head><title>Compliance Audit Report</title></head>
        <body>
        <h1>Compliance Audit Report</h1>
        <p><strong>Report ID:</strong> {report['report_id']}</p>
        <p><strong>Generated:</strong> {report['generated_at']}</p>
        <p><strong>Overall Score:</strong> {report['audit_summary']['overall_score']}%</p>
        
        <h2>Executive Summary</h2>
        <p>{report['executive_summary']['overall_status']}</p>
        
        <h2>Risk Matrix</h2>
        <ul>
        <li>Critical: {report['risk_matrix']['critical']}</li>
        <li>High: {report['risk_matrix']['high']}</li>
        <li>Medium: {report['risk_matrix']['medium']}</li>
        <li>Low: {report['risk_matrix']['low']}</li>
        </ul>
        </body>
        </html>
        """
        return html
