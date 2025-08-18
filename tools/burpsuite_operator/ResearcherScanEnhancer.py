"""
Burp Suite Operator Agent - Researcher Scan Enhancer Tool

This tool leverages the research-agent MCP server to enhance Burp Suite scans
with intelligence-driven configuration, payload optimization, and coverage analysis.
It provides specialized capabilities for web application security testing enhancement.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

# Import the shared researcher tool
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from shared.ResearcherTool import ResearcherTool


class ScanEnhancementRequest(BaseModel):
    """Model for scan enhancement requests"""
    target_url: str = Field(..., description="Target URL for scan enhancement")
    detected_technologies: List[str] = Field(default_factory=list, description="Detected technologies and frameworks")
    scan_type: str = Field("comprehensive", description="Type of scan to enhance")
    current_findings: List[Dict[str, Any]] = Field(default_factory=list, description="Current scan findings")
    enhancement_focus: List[str] = Field(default_factory=lambda: ["coverage", "payloads", "configuration"], description="Areas to focus enhancement on")


class ResearcherScanEnhancer:
    """
    Scan Enhancement tool for Burp Suite Operator agent using research capabilities.
    Specializes in enhancing web application security scans with intelligence-driven improvements.
    """
    
    def __init__(self):
        self.researcher = ResearcherTool()
        self.agent_id = "burpsuite_operator"
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("BurpOperator.ScanEnhancer")
        
        # Scan enhancement categories
        self.enhancement_categories = {
            "technology_specific": ["framework_vulnerabilities", "version_specific_issues", "configuration_weaknesses"],
            "payload_optimization": ["injection_vectors", "bypass_techniques", "encoding_variations"],
            "coverage_improvement": ["endpoint_discovery", "parameter_analysis", "authentication_testing"],
            "advanced_techniques": ["business_logic", "race_conditions", "timing_attacks"]
        }
        
        # Common web technologies and their specific testing approaches
        self.technology_mappings = {
            "php": ["php_specific_vulnerabilities", "include_attacks", "deserialization"],
            "java": ["java_deserialization", "spring_vulnerabilities", "struts_issues"],
            "nodejs": ["prototype_pollution", "npm_vulnerabilities", "express_issues"],
            "python": ["pickle_deserialization", "django_issues", "flask_vulnerabilities"],
            "dotnet": ["viewstate_attacks", "deserialization", "asp_net_issues"]
        }
    
    def enhance_scan_configuration(self, 
                                 target_url: str = Field(..., description="Target URL to enhance scanning for"),
                                 detected_technologies: List[str] = Field(default_factory=list, description="List of detected technologies"),
                                 scan_scope: str = Field("comprehensive", description="Scope of scan enhancement"),
                                 current_config: Dict[str, Any] = Field(default_factory=dict, description="Current Burp configuration")) -> Dict[str, Any]:
        """
        Enhance Burp Suite scan configuration based on target intelligence.
        
        Args:
            target_url: Target URL for scan enhancement
            detected_technologies: Technologies detected on the target
            scan_scope: Scope of the scan enhancement
            current_config: Current Burp Suite configuration
            
        Returns:
            Dictionary containing enhanced scan configuration recommendations
        """
        try:
            self.logger.info(f"Enhancing scan configuration for: {target_url}")
            
            enhancement_data = {
                "target_url": target_url,
                "detected_technologies": detected_technologies,
                "scan_scope": scan_scope,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "enhancements": {}
            }
            
            # Research technology-specific vulnerabilities
            if detected_technologies:
                tech_research = self._research_technology_vulnerabilities(detected_technologies)
                enhancement_data["enhancements"]["technology_specific"] = tech_research
            
            # Research optimal scan configurations
            config_query = f"Burp Suite scan configuration best practices {' '.join(detected_technologies)} web application security"
            config_result = self.researcher.perform_research(
                tool_name="web_search",
                query=config_query,
                options={
                    "search_type": "configuration_focused",
                    "max_results": 8,
                    "include_snippets": True
                },
                agent_id=self.agent_id
            )
            enhancement_data["enhancements"]["configuration_research"] = config_result
            
            # Research advanced testing techniques
            advanced_query = f"advanced web application security testing techniques {target_url} penetration testing"
            advanced_result = self.researcher.perform_research(
                tool_name="content_analyze",
                query=advanced_query,
                options={
                    "analysis_type": "advanced_testing_analysis",
                    "focus_areas": ["testing_methodologies", "advanced_techniques", "coverage_optimization"],
                    "output_format": "structured"
                },
                agent_id=self.agent_id
            )
            enhancement_data["enhancements"]["advanced_techniques"] = advanced_result
            
            # Generate configuration recommendations
            config_recommendations = self._generate_config_recommendations(enhancement_data)
            enhancement_data["configuration_recommendations"] = config_recommendations
            
            # Generate scan optimization suggestions
            optimization_suggestions = self._generate_optimization_suggestions(enhancement_data)
            enhancement_data["optimization_suggestions"] = optimization_suggestions
            
            return {
                "success": True,
                "scan_enhancement": enhancement_data,
                "summary": f"Generated enhanced scan configuration for {target_url} with {len(detected_technologies)} detected technologies"
            }
            
        except Exception as e:
            self.logger.error(f"Error enhancing scan configuration: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "target_url": target_url
            }
    
    def research_payload_variations(self, 
                                  vulnerability_type: str = Field(..., description="Type of vulnerability to research payloads for"),
                                  target_context: Dict[str, Any] = Field(default_factory=dict, description="Context about the target application"),
                                  bypass_requirements: List[str] = Field(default_factory=list, description="Specific bypass requirements (WAF, filters, etc.)")) -> Dict[str, Any]:
        """
        Research advanced payload variations for specific vulnerability types.
        
        Args:
            vulnerability_type: Type of vulnerability (SQL injection, XSS, etc.)
            target_context: Context information about the target
            bypass_requirements: Specific bypass requirements
            
        Returns:
            Dictionary containing researched payload variations and techniques
        """
        try:
            self.logger.info(f"Researching payload variations for: {vulnerability_type}")
            
            payload_research = {
                "vulnerability_type": vulnerability_type,
                "target_context": target_context,
                "bypass_requirements": bypass_requirements,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload_variations": {}
            }
            
            # Research basic payload variations
            basic_query = f"{vulnerability_type} payload variations techniques web application security testing"
            basic_result = self.researcher.perform_research(
                tool_name="web_search",
                query=basic_query,
                options={
                    "search_type": "payload_focused",
                    "max_results": 10,
                    "include_snippets": True
                },
                agent_id=self.agent_id
            )
            payload_research["payload_variations"]["basic_payloads"] = basic_result
            
            # Research bypass techniques if required
            if bypass_requirements:
                bypass_query = f"{vulnerability_type} bypass techniques {' '.join(bypass_requirements)} evasion methods"
                bypass_result = self.researcher.perform_research(
                    tool_name="web_search",
                    query=bypass_query,
                    options={
                        "search_type": "bypass_focused",
                        "max_results": 8,
                        "include_snippets": True
                    },
                    agent_id=self.agent_id
                )
                payload_research["payload_variations"]["bypass_techniques"] = bypass_result
            
            # Research encoding and obfuscation techniques
            encoding_query = f"{vulnerability_type} encoding obfuscation techniques payload transformation"
            encoding_result = self.researcher.perform_research(
                tool_name="content_analyze",
                query=encoding_query,
                options={
                    "analysis_type": "encoding_analysis",
                    "focus_areas": ["encoding_methods", "obfuscation_techniques", "transformation_methods"],
                    "output_format": "structured"
                },
                agent_id=self.agent_id
            )
            payload_research["payload_variations"]["encoding_techniques"] = encoding_result
            
            # Generate custom payloads using code generation
            if target_context:
                custom_payload_result = self.researcher.perform_research(
                    tool_name="code_generate",
                    query=f"Generate custom {vulnerability_type} payloads for {target_context}",
                    options={
                        "language": "python",
                        "framework": "security_testing",
                        "style": "payload_generation"
                    },
                    agent_id=self.agent_id
                )
                payload_research["payload_variations"]["custom_payloads"] = custom_payload_result
            
            # Analyze payload effectiveness
            effectiveness_analysis = self._analyze_payload_effectiveness(payload_research)
            payload_research["effectiveness_analysis"] = effectiveness_analysis
            
            # Generate payload recommendations
            payload_recommendations = self._generate_payload_recommendations(payload_research)
            payload_research["recommendations"] = payload_recommendations
            
            return {
                "success": True,
                "payload_research": payload_research,
                "summary": f"Researched comprehensive payload variations for {vulnerability_type}"
            }
            
        except Exception as e:
            self.logger.error(f"Error researching payload variations: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "vulnerability_type": vulnerability_type
            }
    
    def analyze_scan_coverage(self, 
                            scan_results: Dict[str, Any] = Field(..., description="Current scan results to analyze"),
                            target_info: Dict[str, Any] = Field(default_factory=dict, description="Information about the target application"),
                            coverage_goals: List[str] = Field(default_factory=lambda: ["endpoints", "parameters", "authentication", "business_logic"], description="Coverage goals to analyze")) -> Dict[str, Any]:
        """
        Analyze current scan coverage and identify gaps for improvement.
        
        Args:
            scan_results: Current Burp Suite scan results
            target_info: Information about the target application
            coverage_goals: Specific coverage goals to analyze
            
        Returns:
            Dictionary containing coverage analysis and improvement recommendations
        """
        try:
            self.logger.info("Analyzing scan coverage and identifying gaps")
            
            coverage_analysis = {
                "scan_results_summary": self._summarize_scan_results(scan_results),
                "target_info": target_info,
                "coverage_goals": coverage_goals,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "coverage_assessment": {}
            }
            
            # Research comprehensive testing methodologies
            methodology_query = "web application security testing methodology comprehensive coverage OWASP testing guide"
            methodology_result = self.researcher.perform_research(
                tool_name="web_search",
                query=methodology_query,
                options={
                    "search_type": "methodology_focused",
                    "max_results": 8,
                    "include_snippets": True
                },
                agent_id=self.agent_id
            )
            coverage_analysis["coverage_assessment"]["methodology_research"] = methodology_result
            
            # Analyze current coverage against best practices
            coverage_query = f"Analyze web application security testing coverage gaps missing test cases"
            coverage_result = self.researcher.perform_research(
                tool_name="content_analyze",
                query=coverage_query,
                options={
                    "analysis_type": "coverage_analysis",
                    "focus_areas": ["testing_gaps", "missing_vectors", "coverage_improvement"],
                    "output_format": "structured"
                },
                agent_id=self.agent_id
            )
            coverage_analysis["coverage_assessment"]["gap_analysis"] = coverage_result
            
            # Research specific coverage areas
            for goal in coverage_goals:
                goal_query = f"web application security testing {goal} coverage best practices comprehensive testing"
                goal_result = self.researcher.perform_research(
                    tool_name="web_search",
                    query=goal_query,
                    options={
                        "search_type": f"{goal}_coverage_focused",
                        "max_results": 5,
                        "include_snippets": True
                    },
                    agent_id=self.agent_id
                )
                coverage_analysis["coverage_assessment"][f"{goal}_coverage"] = goal_result
            
            # Generate coverage improvement recommendations
            improvement_recommendations = self._generate_coverage_improvements(coverage_analysis)
            coverage_analysis["improvement_recommendations"] = improvement_recommendations
            
            # Generate coverage metrics
            coverage_metrics = self._calculate_coverage_metrics(coverage_analysis)
            coverage_analysis["coverage_metrics"] = coverage_metrics
            
            return {
                "success": True,
                "coverage_analysis": coverage_analysis,
                "summary": "Completed comprehensive scan coverage analysis with improvement recommendations"
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing scan coverage: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def correlate_findings_with_intelligence(self, 
                                           scan_findings: List[Dict[str, Any]] = Field(..., description="Scan findings to correlate"),
                                           threat_context: Dict[str, Any] = Field(default_factory=dict, description="Threat intelligence context"),
                                           correlation_depth: str = Field("standard", description="Depth of correlation analysis")) -> Dict[str, Any]:
        """
        Correlate scan findings with threat intelligence and vulnerability databases.
        
        Args:
            scan_findings: List of scan findings to correlate
            threat_context: Additional threat intelligence context
            correlation_depth: Depth of correlation analysis
            
        Returns:
            Dictionary containing correlated findings and intelligence
        """
        try:
            self.logger.info(f"Correlating {len(scan_findings)} scan findings with threat intelligence")
            
            correlation_analysis = {
                "scan_findings_count": len(scan_findings),
                "threat_context": threat_context,
                "correlation_depth": correlation_depth,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "correlations": {}
            }
            
            # Extract vulnerability types from findings
            vulnerability_types = self._extract_vulnerability_types(scan_findings)
            
            # Research threat intelligence for identified vulnerabilities
            for vuln_type in vulnerability_types:
                intel_query = f"{vuln_type} threat intelligence recent attacks exploitation trends"
                intel_result = self.researcher.perform_research(
                    tool_name="web_search",
                    query=intel_query,
                    options={
                        "search_type": "threat_intelligence_focused",
                        "max_results": 6,
                        "include_snippets": True
                    },
                    agent_id=self.agent_id
                )
                correlation_analysis["correlations"][f"{vuln_type}_intelligence"] = intel_result
            
            # Research exploitation patterns
            exploitation_query = f"web application vulnerability exploitation patterns attack techniques"
            exploitation_result = self.researcher.perform_research(
                tool_name="content_analyze",
                query=exploitation_query,
                options={
                    "analysis_type": "exploitation_analysis",
                    "focus_areas": ["attack_patterns", "exploitation_techniques", "threat_actors"],
                    "output_format": "structured"
                },
                agent_id=self.agent_id
            )
            correlation_analysis["correlations"]["exploitation_patterns"] = exploitation_result
            
            # Extract indicators of compromise if available
            ioc_extraction_result = self.researcher.perform_research(
                tool_name="extract_information",
                query=f"Extract indicators of compromise from vulnerability findings: {str(scan_findings)[:1000]}",
                options={
                    "extraction_targets": ["ip_addresses", "domains", "file_hashes", "attack_signatures"],
                    "format": "structured",
                    "confidence_threshold": 0.7
                },
                agent_id=self.agent_id
            )
            correlation_analysis["correlations"]["ioc_extraction"] = ioc_extraction_result
            
            # Generate correlation insights
            correlation_insights = self._generate_correlation_insights(correlation_analysis)
            correlation_analysis["insights"] = correlation_insights
            
            # Generate prioritized recommendations
            prioritized_recommendations = self._generate_prioritized_recommendations(correlation_analysis)
            correlation_analysis["prioritized_recommendations"] = prioritized_recommendations
            
            return {
                "success": True,
                "correlation_analysis": correlation_analysis,
                "summary": f"Correlated {len(scan_findings)} findings with threat intelligence and vulnerability databases"
            }
            
        except Exception as e:
            self.logger.error(f"Error correlating findings with intelligence: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _research_technology_vulnerabilities(self, technologies: List[str]) -> Dict[str, Any]:
        """Research vulnerabilities specific to detected technologies"""
        tech_research = {}
        
        for tech in technologies:
            tech_query = f"{tech} security vulnerabilities recent CVE web application"
            tech_result = self.researcher.perform_research(
                tool_name="web_search",
                query=tech_query,
                options={
                    "search_type": "technology_vulnerability_focused",
                    "max_results": 5,
                    "include_snippets": True
                },
                agent_id=self.agent_id
            )
            tech_research[tech] = tech_result
        
        return tech_research
    
    def _generate_config_recommendations(self, enhancement_data: Dict[str, Any]) -> List[str]:
        """Generate Burp Suite configuration recommendations"""
        recommendations = []
        
        detected_technologies = enhancement_data.get("detected_technologies", [])
        
        # General recommendations
        recommendations.append("Enable comprehensive active scanning for all identified technologies")
        recommendations.append("Configure custom insertion points for parameter testing")
        recommendations.append("Enable advanced SQL injection detection techniques")
        
        # Technology-specific recommendations
        for tech in detected_technologies:
            if tech.lower() in ["php", "mysql"]:
                recommendations.append("Enable PHP-specific payload variations and MySQL injection techniques")
            elif tech.lower() in ["java", "spring"]:
                recommendations.append("Enable Java deserialization testing and Spring-specific vulnerabilities")
            elif tech.lower() in ["nodejs", "express"]:
                recommendations.append("Enable Node.js-specific testing including prototype pollution")
        
        recommendations.append("Configure session handling rules for authenticated testing")
        recommendations.append("Enable business logic testing extensions")
        
        return recommendations
    
    def _generate_optimization_suggestions(self, enhancement_data: Dict[str, Any]) -> List[str]:
        """Generate scan optimization suggestions"""
        suggestions = []
        
        suggestions.append("Optimize scan speed by focusing on high-impact vulnerability types")
        suggestions.append("Configure intelligent attack insertion points based on application structure")
        suggestions.append("Enable advanced crawling techniques for comprehensive coverage")
        suggestions.append("Implement custom payload lists based on target technology stack")
        suggestions.append("Configure scan scheduling to minimize impact on target application")
        
        return suggestions
    
    def _analyze_payload_effectiveness(self, payload_research: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze effectiveness of researched payloads"""
        analysis = {
            "payload_categories": len(payload_research.get("payload_variations", {})),
            "bypass_techniques_available": "bypass_techniques" in payload_research.get("payload_variations", {}),
            "custom_payloads_generated": "custom_payloads" in payload_research.get("payload_variations", {}),
            "effectiveness_rating": "high" if len(payload_research.get("payload_variations", {})) > 2 else "medium"
        }
        
        return analysis
    
    def _generate_payload_recommendations(self, payload_research: Dict[str, Any]) -> List[str]:
        """Generate payload usage recommendations"""
        recommendations = []
        
        vulnerability_type = payload_research.get("vulnerability_type", "")
        
        recommendations.append(f"Test all researched {vulnerability_type} payload variations systematically")
        recommendations.append("Start with basic payloads before progressing to advanced techniques")
        
        if "bypass_techniques" in payload_research.get("payload_variations", {}):
            recommendations.append("Apply bypass techniques if initial payloads are filtered")
        
        if "encoding_techniques" in payload_research.get("payload_variations", {}):
            recommendations.append("Use encoding and obfuscation techniques for evasion")
        
        recommendations.append("Document successful payloads for future testing scenarios")
        
        return recommendations
    
    def _summarize_scan_results(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize scan results for analysis"""
        summary = {
            "total_findings": len(scan_results.get("findings", [])),
            "severity_distribution": {},
            "vulnerability_types": [],
            "coverage_areas": []
        }
        
        # Analyze findings if available
        findings = scan_results.get("findings", [])
        for finding in findings:
            severity = finding.get("severity", "unknown").lower()
            summary["severity_distribution"][severity] = summary["severity_distribution"].get(severity, 0) + 1
            
            vuln_type = finding.get("type", "unknown")
            if vuln_type not in summary["vulnerability_types"]:
                summary["vulnerability_types"].append(vuln_type)
        
        return summary
    
    def _generate_coverage_improvements(self, coverage_analysis: Dict[str, Any]) -> List[str]:
        """Generate coverage improvement recommendations"""
        improvements = []
        
        coverage_goals = coverage_analysis.get("coverage_goals", [])
        
        for goal in coverage_goals:
            if goal == "endpoints":
                improvements.append("Enhance endpoint discovery through advanced crawling and directory enumeration")
            elif goal == "parameters":
                improvements.append("Implement comprehensive parameter analysis including hidden and custom parameters")
            elif goal == "authentication":
                improvements.append("Expand authentication testing to include session management and privilege escalation")
            elif goal == "business_logic":
                improvements.append("Develop business logic test cases specific to application functionality")
        
        improvements.append("Implement automated regression testing for identified vulnerabilities")
        improvements.append("Enhance coverage reporting and metrics tracking")
        
        return improvements
    
    def _calculate_coverage_metrics(self, coverage_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate coverage metrics"""
        metrics = {
            "coverage_goals_addressed": len(coverage_analysis.get("coverage_goals", [])),
            "methodology_alignment": "high",  # Simplified assessment
            "improvement_opportunities": len(coverage_analysis.get("improvement_recommendations", [])),
            "overall_coverage_score": 75  # Simplified scoring
        }
        
        return metrics
    
    def _extract_vulnerability_types(self, scan_findings: List[Dict[str, Any]]) -> List[str]:
        """Extract unique vulnerability types from scan findings"""
        vuln_types = set()
        
        for finding in scan_findings:
            vuln_type = finding.get("type", finding.get("vulnerability_type", "unknown"))
            if vuln_type != "unknown":
                vuln_types.add(vuln_type)
        
        return list(vuln_types)
    
    def _generate_correlation_insights(self, correlation_analysis: Dict[str, Any]) -> List[str]:
        """Generate insights from correlation analysis"""
        insights = []
        
        findings_count = correlation_analysis.get("scan_findings_count", 0)
        correlations = correlation_analysis.get("correlations", {})
        
        insights.append(f"Analyzed {findings_count} scan findings against current threat intelligence")
        
        if correlations:
            insights.append(f"Found correlations across {len(correlations)} intelligence sources")
            insights.append("Identified potential attack patterns matching current threat landscape")
        
        insights.append("Correlation analysis provides context for vulnerability prioritization")
        insights.append("Intelligence integration enhances understanding of real-world exploitation risk")
        
        return insights
    
    def _generate_prioritized_recommendations(self, correlation_analysis: Dict[str, Any]) -> List[str]:
        """Generate prioritized recommendations based on correlation analysis"""
        recommendations = []
        
        recommendations.append("Prioritize vulnerabilities with active exploitation in threat intelligence")
        recommendations.append("Focus on vulnerabilities matching current attack patterns")
        recommendations.append("Implement additional monitoring for high-risk vulnerability types")
        recommendations.append("Develop specific test cases for identified threat scenarios")
        recommendations.append("Update security controls based on correlation findings")
        
        return recommendations
