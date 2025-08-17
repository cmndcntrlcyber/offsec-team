"""
BurpSuite Result Processor for cybersecurity AI workflow integration.

This tool processes and analyzes BurpSuite scan results with advanced
filtering, correlation, and data transformation capabilities.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ..shared.data_models.security_models import ScanResult, Vulnerability, SeverityLevel
from .BurpSuiteAPIClient import BurpSuiteAPIClient


class BurpResultProcessor:
    """
    Advanced BurpSuite scan result processor for security analysis.
    Provides result extraction, filtering, correlation, and transformation.
    """
    
    def __init__(self):
        """Initialize the BurpSuite result processor."""
        self.api_client = BurpSuiteAPIClient()
        self.logger = logging.getLogger("BurpResultProcessor")
    
    def extract_scan_findings(self, scan_id: str = Field(..., description="BurpSuite scan ID")) -> Dict[str, Any]:
        """
        Extract and organize scan findings from BurpSuite.
        
        Args:
            scan_id: BurpSuite scan identifier
            
        Returns:
            Organized scan findings and metadata
        """
        try:
            # Get scan results from BurpSuite
            results_response = self.api_client.execute_burp_function(
                "get_scan_results",
                parameters={"scan_id": scan_id}
            )
            
            if not results_response["success"]:
                return {
                    "success": False,
                    "error": f"Failed to retrieve scan results: {results_response.get('error')}"
                }
            
            raw_results = results_response["result"]
            
            # Process and organize findings
            findings = {
                "scan_id": scan_id,
                "extracted_at": datetime.utcnow().isoformat(),
                "total_issues": 0,
                "severity_breakdown": {
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                    "info": 0
                },
                "issue_types": {},
                "findings": [],
                "scan_metrics": raw_results.get("scan_metrics", {}),
                "target_info": raw_results.get("target", {})
            }
            
            # Process individual issues
            for issue in raw_results.get("issues", []):
                processed_finding = self._process_individual_issue(issue)
                findings["findings"].append(processed_finding)
                
                # Update counters
                findings["total_issues"] += 1
                severity = processed_finding["severity"].lower()
                findings["severity_breakdown"][severity] += 1
                
                issue_type = processed_finding["issue_type"]
                findings["issue_types"][issue_type] = findings["issue_types"].get(issue_type, 0) + 1
            
            return {
                "success": True,
                "scan_id": scan_id,
                "findings": findings
            }
            
        except Exception as e:
            self.logger.error(f"Failed to extract scan findings: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def classify_vulnerability_findings(self, findings: List[Dict[str, Any]] = Field(..., description="List of vulnerability findings")) -> Dict[str, Any]:
        """
        Classify and categorize vulnerability findings.
        
        Args:
            findings: List of raw vulnerability findings
            
        Returns:
            Classified and categorized findings
        """
        try:
            classification = {
                "total_findings": len(findings),
                "categories": {
                    "injection": [],
                    "authentication": [],
                    "authorization": [],
                    "cryptographic": [],
                    "configuration": [],
                    "information_disclosure": [],
                    "business_logic": [],
                    "other": []
                },
                "owasp_top10_mapping": {},
                "cwe_mapping": {},
                "severity_distribution": {
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                    "info": 0
                }
            }
            
            # Define classification rules
            injection_keywords = ["sql", "xss", "command", "ldap", "xpath", "nosql", "script"]
            auth_keywords = ["authentication", "login", "session", "password", "credential"]
            authz_keywords = ["authorization", "access", "privilege", "permission"]
            crypto_keywords = ["ssl", "tls", "certificate", "encryption", "hash", "crypto"]
            config_keywords = ["configuration", "header", "cors", "csp", "hsts"]
            info_keywords = ["disclosure", "exposure", "leak", "directory", "file"]
            
            for finding in findings:
                issue_name = finding.get("issue_name", "").lower()
                issue_detail = finding.get("issue_detail", "").lower()
                combined_text = f"{issue_name} {issue_detail}"
                
                # Classify by category
                category = "other"
                if any(keyword in combined_text for keyword in injection_keywords):
                    category = "injection"
                elif any(keyword in combined_text for keyword in auth_keywords):
                    category = "authentication"
                elif any(keyword in combined_text for keyword in authz_keywords):
                    category = "authorization"
                elif any(keyword in combined_text for keyword in crypto_keywords):
                    category = "cryptographic"
                elif any(keyword in combined_text for keyword in config_keywords):
                    category = "configuration"
                elif any(keyword in combined_text for keyword in info_keywords):
                    category = "information_disclosure"
                
                finding["category"] = category
                classification["categories"][category].append(finding)
                
                # Map to OWASP Top 10
                owasp_mapping = self._map_to_owasp_top10(issue_name)
                if owasp_mapping:
                    finding["owasp_category"] = owasp_mapping
                    if owasp_mapping not in classification["owasp_top10_mapping"]:
                        classification["owasp_top10_mapping"][owasp_mapping] = 0
                    classification["owasp_top10_mapping"][owasp_mapping] += 1
                
                # Map CWE if available
                cwe_id = finding.get("cwe_id")
                if cwe_id:
                    if cwe_id not in classification["cwe_mapping"]:
                        classification["cwe_mapping"][cwe_id] = 0
                    classification["cwe_mapping"][cwe_id] += 1
                
                # Count severity
                severity = finding.get("severity", "info").lower()
                classification["severity_distribution"][severity] += 1
            
            return {
                "success": True,
                "classification": classification
            }
            
        except Exception as e:
            self.logger.error(f"Failed to classify findings: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def correlate_related_vulnerabilities(self, findings: List[Dict[str, Any]] = Field(..., description="List of vulnerability findings")) -> Dict[str, Any]:
        """
        Correlate and group related vulnerabilities.
        
        Args:
            findings: List of vulnerability findings
            
        Returns:
            Correlated vulnerability groups
        """
        try:
            correlations = {
                "groups": [],
                "correlation_rules_applied": 0,
                "total_findings": len(findings),
                "grouped_findings": 0,
                "standalone_findings": 0
            }
            
            processed_findings = set()
            
            # Correlation rules
            correlation_rules = [
                {
                    "name": "Same URL vulnerabilities",
                    "key": lambda f: f.get("url", "").split("?")[0]  # URL without parameters
                },
                {
                    "name": "Same vulnerability type",
                    "key": lambda f: f.get("issue_type", "")
                },
                {
                    "name": "Same parameter vulnerabilities",
                    "key": lambda f: f"{f.get('url', '').split('?')[0]}_{f.get('parameter', '')}"
                }
            ]
            
            for rule in correlation_rules:
                rule_groups = {}
                
                for i, finding in enumerate(findings):
                    if i in processed_findings:
                        continue
                    
                    correlation_key = rule["key"](finding)
                    if not correlation_key:
                        continue
                    
                    if correlation_key not in rule_groups:
                        rule_groups[correlation_key] = []
                    
                    rule_groups[correlation_key].append((i, finding))
                
                # Process groups with multiple findings
                for correlation_key, group_findings in rule_groups.items():
                    if len(group_findings) > 1:
                        group = {
                            "correlation_rule": rule["name"],
                            "correlation_key": correlation_key,
                            "finding_count": len(group_findings),
                            "findings": [f[1] for f in group_findings],
                            "severity_range": self._get_severity_range([f[1] for f in group_findings]),
                            "affected_urls": list(set(f[1].get("url", "") for f in group_findings)),
                            "issue_types": list(set(f[1].get("issue_type", "") for f in group_findings))
                        }
                        
                        correlations["groups"].append(group)
                        correlations["correlation_rules_applied"] += 1
                        
                        # Mark findings as processed
                        for finding_idx, _ in group_findings:
                            processed_findings.add(finding_idx)
            
            correlations["grouped_findings"] = len(processed_findings)
            correlations["standalone_findings"] = len(findings) - len(processed_findings)
            
            return {
                "success": True,
                "correlations": correlations
            }
            
        except Exception as e:
            self.logger.error(f"Failed to correlate vulnerabilities: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def filter_findings(self, findings: List[Dict[str, Any]], filter_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter findings based on specified criteria.
        
        Args:
            findings: List of vulnerability findings
            filter_criteria: Filtering criteria
            
        Returns:
            Filtered findings
        """
        try:
            filtered = []
            filter_stats = {
                "original_count": len(findings),
                "filtered_count": 0,
                "filters_applied": []
            }
            
            for finding in findings:
                include = True
                
                # Severity filter
                if "severity" in filter_criteria:
                    allowed_severities = filter_criteria["severity"]
                    if isinstance(allowed_severities, str):
                        allowed_severities = [allowed_severities]
                    
                    if finding.get("severity", "").lower() not in [s.lower() for s in allowed_severities]:
                        include = False
                
                # Issue type filter
                if "issue_types" in filter_criteria and include:
                    allowed_types = filter_criteria["issue_types"]
                    if isinstance(allowed_types, str):
                        allowed_types = [allowed_types]
                    
                    if finding.get("issue_type", "") not in allowed_types:
                        include = False
                
                # URL pattern filter
                if "url_pattern" in filter_criteria and include:
                    pattern = filter_criteria["url_pattern"]
                    url = finding.get("url", "")
                    if pattern not in url:
                        include = False
                
                # Confidence filter
                if "min_confidence" in filter_criteria and include:
                    min_confidence = filter_criteria["min_confidence"]
                    confidence = finding.get("confidence", "low")
                    confidence_levels = {"low": 1, "medium": 2, "high": 3}
                    
                    if confidence_levels.get(confidence, 1) < confidence_levels.get(min_confidence, 1):
                        include = False
                
                if include:
                    filtered.append(finding)
            
            filter_stats["filtered_count"] = len(filtered)
            filter_stats["filters_applied"] = list(filter_criteria.keys())
            
            return {
                "success": True,
                "filtered_findings": filtered,
                "filter_stats": filter_stats
            }
            
        except Exception as e:
            self.logger.error(f"Failed to filter findings: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def export_results_to_format(self, findings: Dict[str, Any], export_format: str) -> Dict[str, Any]:
        """
        Export scan results to various formats.
        
        Args:
            findings: Processed scan findings
            export_format: Format to export (json, csv, xml, html)
            
        Returns:
            Export operation result
        """
        try:
            export_data = None
            
            if export_format.lower() == "json":
                export_data = json.dumps(findings, indent=2, default=str)
            
            elif export_format.lower() == "csv":
                export_data = self._convert_to_csv(findings)
            
            elif export_format.lower() == "html":
                export_data = self._convert_to_html(findings)
            
            elif export_format.lower() == "xml":
                export_data = self._convert_to_xml(findings)
            
            else:
                return {
                    "success": False,
                    "error": f"Unsupported export format: {export_format}"
                }
            
            return {
                "success": True,
                "format": export_format,
                "data": export_data,
                "size": len(export_data) if export_data else 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to export results: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _process_individual_issue(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Process individual BurpSuite issue into standardized format."""
        return {
            "issue_id": issue.get("id", ""),
            "issue_type": issue.get("issue_type", {}).get("name", ""),
            "issue_name": issue.get("name", ""),
            "severity": issue.get("severity", "info").title(),
            "confidence": issue.get("confidence", "tentative").lower(),
            "url": issue.get("origin", ""),
            "parameter": issue.get("evidence", {}).get("request_response", {}).get("request", {}).get("parameter", ""),
            "issue_detail": issue.get("issue_detail", ""),
            "issue_background": issue.get("issue_background", ""),
            "remediation_detail": issue.get("remediation_detail", ""),
            "cwe_id": issue.get("type_index"),
            "evidence": issue.get("evidence", {}),
            "references": issue.get("references", [])
        }
    
    def _map_to_owasp_top10(self, issue_name: str) -> Optional[str]:
        """Map vulnerability to OWASP Top 10 category."""
        owasp_mappings = {
            "injection": "A03:2021 – Injection",
            "xss": "A03:2021 – Injection", 
            "authentication": "A07:2021 – Identification and Authentication Failures",
            "authorization": "A01:2021 – Broken Access Control",
            "sensitive data": "A02:2021 – Cryptographic Failures",
            "xxe": "A05:2021 – Security Misconfiguration",
            "deserialization": "A08:2021 – Software and Data Integrity Failures",
            "logging": "A09:2021 – Security Logging and Monitoring Failures",
            "csrf": "A01:2021 – Broken Access Control"
        }
        
        issue_lower = issue_name.lower()
        for keyword, owasp_cat in owasp_mappings.items():
            if keyword in issue_lower:
                return owasp_cat
        return None
    
    def _get_severity_range(self, findings: List[Dict[str, Any]]) -> Dict[str, str]:
        """Get severity range for a group of findings."""
        severities = [f.get("severity", "info").lower() for f in findings]
        severity_levels = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
        
        max_severity = max(severities, key=lambda s: severity_levels.get(s, 0))
        min_severity = min(severities, key=lambda s: severity_levels.get(s, 0))
        
        return {"highest": max_severity, "lowest": min_severity}
    
    def _convert_to_csv(self, findings: Dict[str, Any]) -> str:
        """Convert findings to CSV format."""
        csv_lines = ["Issue Type,Severity,URL,Description,Confidence"]
        
        for finding in findings.get("findings", []):
            line = f'"{finding.get("issue_type", "")}","{finding.get("severity", "")}","{finding.get("url", "")}","{finding.get("issue_detail", "")[:100]}...","{finding.get("confidence", "")}"'
            csv_lines.append(line)
        
        return "\n".join(csv_lines)
    
    def _convert_to_html(self, findings: Dict[str, Any]) -> str:
        """Convert findings to HTML format."""
        html = f"""
        <html>
        <head><title>BurpSuite Scan Results</title></head>
        <body>
        <h1>Scan Results Summary</h1>
        <p>Total Issues: {findings.get('total_issues', 0)}</p>
        <h2>Findings</h2>
        <table border="1">
        <tr><th>Issue Type</th><th>Severity</th><th>URL</th><th>Description</th></tr>
        """
        
        for finding in findings.get("findings", []):
            html += f"""
            <tr>
                <td>{finding.get("issue_type", "")}</td>
                <td>{finding.get("severity", "")}</td>
                <td>{finding.get("url", "")}</td>
                <td>{finding.get("issue_detail", "")[:200]}...</td>
            </tr>
            """
        
        html += "</table></body></html>"
        return html
    
    def _convert_to_xml(self, findings: Dict[str, Any]) -> str:
        """Convert findings to XML format."""
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<scan_results>\n'
        xml += f'  <total_issues>{findings.get("total_issues", 0)}</total_issues>\n'
        xml += '  <findings>\n'
        
        for finding in findings.get("findings", []):
            xml += '    <finding>\n'
            xml += f'      <issue_type>{finding.get("issue_type", "")}</issue_type>\n'
            xml += f'      <severity>{finding.get("severity", "")}</severity>\n'
            xml += f'      <url>{finding.get("url", "")}</url>\n'
            xml += f'      <description>{finding.get("issue_detail", "")}</description>\n'
            xml += '    </finding>\n'
        
        xml += '  </findings>\n</scan_results>'
        return xml
