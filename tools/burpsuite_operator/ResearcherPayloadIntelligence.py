"""
Burp Suite Operator Agent - Researcher Payload Intelligence Tool

This tool leverages the research-agent MCP server to research and generate advanced
payloads for web application security testing. It provides specialized capabilities
for payload research, WAF bypass techniques, and injection vector analysis.
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


class PayloadRequest(BaseModel):
    """Model for payload research requests"""
    vulnerability_type: str = Field(..., description="Type of vulnerability for payload generation")
    target_technology: Optional[str] = Field(None, description="Target technology stack")
    bypass_targets: List[str] = Field(default_factory=list, description="Security controls to bypass (WAF, filters, etc.)")
    payload_complexity: str = Field("standard", description="Complexity level of payloads")
    custom_requirements: Dict[str, Any] = Field(default_factory=dict, description="Custom payload requirements")


class ResearcherPayloadIntelligence:
    """
    Payload Intelligence tool for Burp Suite Operator agent using research capabilities.
    Specializes in advanced payload research, generation, and bypass technique analysis.
    """
    
    def __init__(self):
        self.researcher = ResearcherTool()
        self.agent_id = "burpsuite_operator"
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("BurpOperator.PayloadIntelligence")
        
        # Payload categories and techniques
        self.payload_categories = {
            "injection": ["sql_injection", "nosql_injection", "ldap_injection", "xpath_injection", "command_injection"],
            "xss": ["reflected_xss", "stored_xss", "dom_xss", "blind_xss"],
            "file_attacks": ["lfi", "rfi", "file_upload", "path_traversal"],
            "deserialization": ["java_deserialization", "php_deserialization", "python_pickle", "dotnet_deserialization"],
            "template_injection": ["ssti", "csti", "template_engines"]
        }
        
        # WAF and filter bypass techniques
        self.bypass_techniques = {
            "encoding": ["url_encoding", "html_encoding", "unicode_encoding", "base64_encoding"],
            "obfuscation": ["case_variation", "comment_insertion", "whitespace_manipulation", "concatenation"],
            "evasion": ["time_delays", "blind_techniques", "out_of_band", "polyglot_payloads"],
            "protocol": ["http_parameter_pollution", "http_smuggling", "chunked_encoding"]
        }
        
        # Common WAF signatures and bypass methods
        self.waf_signatures = {
            "cloudflare": ["cf_bypass_techniques", "cloudflare_evasion"],
            "aws_waf": ["aws_waf_bypass", "aws_specific_evasion"],
            "akamai": ["akamai_bypass", "akamai_evasion"],
            "imperva": ["imperva_bypass", "incapsula_evasion"],
            "f5": ["f5_asm_bypass", "bigip_evasion"]
        }
    
    def research_custom_payloads(self, 
                                vulnerability_type: str = Field(..., description="Type of vulnerability to generate payloads for"),
                                target_context: Dict[str, Any] = Field(default_factory=dict, description="Context about target application"),
                                payload_requirements: Dict[str, Any] = Field(default_factory=dict, description="Specific payload requirements")) -> Dict[str, Any]:
        """
        Research and generate custom payloads for specific vulnerability types and contexts.
        
        Args:
            vulnerability_type: Type of vulnerability (SQL injection, XSS, etc.)
            target_context: Information about the target application
            payload_requirements: Specific requirements for payload generation
            
        Returns:
            Dictionary containing researched and generated custom payloads
        """
        try:
            self.logger.info(f"Researching custom payloads for: {vulnerability_type}")
            
            payload_research = {
                "vulnerability_type": vulnerability_type,
                "target_context": target_context,
                "payload_requirements": payload_requirements,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "custom_payloads": {}
            }
            
            # Research latest payload techniques
            latest_query = f"{vulnerability_type} latest payload techniques 2024 advanced exploitation"
            latest_result = self.researcher.perform_research(
                tool_name="web_search",
                query=latest_query,
                options={
                    "search_type": "latest_techniques_focused",
                    "max_results": 10,
                    "include_snippets": True
                },
                agent_id=self.agent_id
            )
            payload_research["custom_payloads"]["latest_techniques"] = latest_result
            
            # Research context-specific payloads
            if target_context:
                context_technologies = target_context.get("technologies", [])
                if context_technologies:
                    context_query = f"{vulnerability_type} payloads {' '.join(context_technologies)} specific exploitation"
                    context_result = self.researcher.perform_research(
                        tool_name="web_search",
                        query=context_query,
                        options={
                            "search_type": "context_specific_focused",
                            "max_results": 8,
                            "include_snippets": True
                        },
                        agent_id=self.agent_id
                    )
                    payload_research["custom_payloads"]["context_specific"] = context_result
            
            # Generate custom payloads using code generation
            generation_query = f"Generate advanced {vulnerability_type} payloads with variations and encoding"
            generation_result = self.researcher.perform_research(
                tool_name="code_generate",
                query=generation_query,
                options={
                    "language": "python",
                    "framework": "security_testing",
                    "style": "payload_generation"
                },
                agent_id=self.agent_id
            )
            payload_research["custom_payloads"]["generated_payloads"] = generation_result
            
            # Research payload chaining techniques
            chaining_query = f"{vulnerability_type} payload chaining multi-stage exploitation techniques"
            chaining_result = self.researcher.perform_research(
                tool_name="content_analyze",
                query=chaining_query,
                options={
                    "analysis_type": "payload_chaining_analysis",
                    "focus_areas": ["chaining_techniques", "multi_stage_payloads", "exploitation_chains"],
                    "output_format": "structured"
                },
                agent_id=self.agent_id
            )
            payload_research["custom_payloads"]["chaining_techniques"] = chaining_result
            
            # Analyze payload effectiveness
            effectiveness_analysis = self._analyze_payload_effectiveness(payload_research)
            payload_research["effectiveness_analysis"] = effectiveness_analysis
            
            # Generate payload variations
            payload_variations = self._generate_payload_variations(payload_research)
            payload_research["payload_variations"] = payload_variations
            
            return {
                "success": True,
                "payload_research": payload_research,
                "summary": f"Generated comprehensive custom payloads for {vulnerability_type}"
            }
            
        except Exception as e:
            self.logger.error(f"Error researching custom payloads: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "vulnerability_type": vulnerability_type
            }
    
    def analyze_waf_bypass_techniques(self, 
                                    waf_type: str = Field(..., description="Type of WAF to research bypass techniques for"),
                                    target_payload_type: str = Field(..., description="Type of payload to bypass WAF for"),
                                    bypass_complexity: str = Field("standard", description="Complexity level of bypass techniques")) -> Dict[str, Any]:
        """
        Research and analyze WAF bypass techniques for specific WAF types and payload categories.
        
        Args:
            waf_type: Type of WAF (CloudFlare, AWS WAF, Akamai, etc.)
            target_payload_type: Type of payload to bypass WAF for
            bypass_complexity: Complexity level of bypass techniques
            
        Returns:
            Dictionary containing WAF bypass techniques and analysis
        """
        try:
            self.logger.info(f"Analyzing WAF bypass techniques for: {waf_type}")
            
            bypass_analysis = {
                "waf_type": waf_type,
                "target_payload_type": target_payload_type,
                "bypass_complexity": bypass_complexity,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "bypass_techniques": {}
            }
            
            # Research general WAF bypass techniques
            general_query = f"{waf_type} WAF bypass techniques {target_payload_type} evasion methods"
            general_result = self.researcher.perform_research(
                tool_name="web_search",
                query=general_query,
                options={
                    "search_type": "waf_bypass_focused",
                    "max_results": 10,
                    "include_snippets": True
                },
                agent_id=self.agent_id
            )
            bypass_analysis["bypass_techniques"]["general_techniques"] = general_result
            
            # Research encoding-based bypass techniques
            encoding_query = f"{waf_type} bypass encoding techniques {target_payload_type} obfuscation"
            encoding_result = self.researcher.perform_research(
                tool_name="web_search",
                query=encoding_query,
                options={
                    "search_type": "encoding_bypass_focused",
                    "max_results": 8,
                    "include_snippets": True
                },
                agent_id=self.agent_id
            )
            bypass_analysis["bypass_techniques"]["encoding_techniques"] = encoding_result
            
            # Research advanced evasion techniques
            evasion_query = f"advanced {waf_type} evasion techniques {target_payload_type} sophisticated bypass"
            evasion_result = self.researcher.perform_research(
                tool_name="content_analyze",
                query=evasion_query,
                options={
                    "analysis_type": "evasion_analysis",
                    "focus_areas": ["advanced_evasion", "sophisticated_bypass", "novel_techniques"],
                    "output_format": "structured"
                },
                agent_id=self.agent_id
            )
            bypass_analysis["bypass_techniques"]["advanced_evasion"] = evasion_result
            
            # Research protocol-level bypass techniques
            protocol_query = f"{waf_type} protocol level bypass HTTP smuggling parameter pollution"
            protocol_result = self.researcher.perform_research(
                tool_name="web_search",
                query=protocol_query,
                options={
                    "search_type": "protocol_bypass_focused",
                    "max_results": 6,
                    "include_snippets": True
                },
                agent_id=self.agent_id
            )
            bypass_analysis["bypass_techniques"]["protocol_techniques"] = protocol_result
            
            # Generate bypass payload examples
            if bypass_complexity in ["advanced", "expert"]:
                payload_generation_result = self.researcher.perform_research(
                    tool_name="code_generate",
                    query=f"Generate {waf_type} bypass payloads for {target_payload_type}",
                    options={
                        "language": "python",
                        "framework": "security_testing",
                        "style": "waf_bypass_generation"
                    },
                    agent_id=self.agent_id
                )
                bypass_analysis["bypass_techniques"]["generated_bypasses"] = payload_generation_result
            
            # Analyze bypass effectiveness
            effectiveness_assessment = self._assess_bypass_effectiveness(bypass_analysis)
            bypass_analysis["effectiveness_assessment"] = effectiveness_assessment
            
            # Generate bypass recommendations
            bypass_recommendations = self._generate_bypass_recommendations(bypass_analysis)
            bypass_analysis["recommendations"] = bypass_recommendations
            
            return {
                "success": True,
                "bypass_analysis": bypass_analysis,
                "summary": f"Analyzed comprehensive WAF bypass techniques for {waf_type}"
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing WAF bypass techniques: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "waf_type": waf_type
            }
    
    def study_injection_vectors(self, 
                              injection_type: str = Field(..., description="Type of injection to study"),
                              application_context: Dict[str, Any] = Field(default_factory=dict, description="Application context information"),
                              vector_complexity: str = Field("comprehensive", description="Complexity level of vector analysis")) -> Dict[str, Any]:
        """
        Study and analyze injection vectors for specific injection types and application contexts.
        
        Args:
            injection_type: Type of injection (SQL, NoSQL, Command, etc.)
            application_context: Context about the target application
            vector_complexity: Complexity level of vector analysis
            
        Returns:
            Dictionary containing injection vector analysis and techniques
        """
        try:
            self.logger.info(f"Studying injection vectors for: {injection_type}")
            
            vector_analysis = {
                "injection_type": injection_type,
                "application_context": application_context,
                "vector_complexity": vector_complexity,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "injection_vectors": {}
            }
            
            # Research basic injection vectors
            basic_query = f"{injection_type} injection vectors techniques entry points web application"
            basic_result = self.researcher.perform_research(
                tool_name="web_search",
                query=basic_query,
                options={
                    "search_type": "injection_vector_focused",
                    "max_results": 10,
                    "include_snippets": True
                },
                agent_id=self.agent_id
            )
            vector_analysis["injection_vectors"]["basic_vectors"] = basic_result
            
            # Research advanced injection techniques
            advanced_query = f"advanced {injection_type} injection techniques blind time-based boolean"
            advanced_result = self.researcher.perform_research(
                tool_name="web_search",
                query=advanced_query,
                options={
                    "search_type": "advanced_injection_focused",
                    "max_results": 8,
                    "include_snippets": True
                },
                agent_id=self.agent_id
            )
            vector_analysis["injection_vectors"]["advanced_techniques"] = advanced_result
            
            # Research context-specific vectors
            if application_context:
                technologies = application_context.get("technologies", [])
                if technologies:
                    context_query = f"{injection_type} injection {' '.join(technologies)} specific vectors"
                    context_result = self.researcher.perform_research(
                        tool_name="content_analyze",
                        query=context_query,
                        options={
                            "analysis_type": "context_injection_analysis",
                            "focus_areas": ["technology_specific_vectors", "framework_vulnerabilities", "platform_techniques"],
                            "output_format": "structured"
                        },
                        agent_id=self.agent_id
                    )
                    vector_analysis["injection_vectors"]["context_specific"] = context_result
            
            # Research out-of-band techniques
            oob_query = f"{injection_type} out of band injection techniques DNS HTTP SMTP"
            oob_result = self.researcher.perform_research(
                tool_name="web_search",
                query=oob_query,
                options={
                    "search_type": "oob_injection_focused",
                    "max_results": 6,
                    "include_snippets": True
                },
                agent_id=self.agent_id
            )
            vector_analysis["injection_vectors"]["out_of_band"] = oob_result
            
            # Research polyglot and universal payloads
            polyglot_query = f"{injection_type} polyglot payloads universal injection techniques"
            polyglot_result = self.researcher.perform_research(
                tool_name="web_search",
                query=polyglot_query,
                options={
                    "search_type": "polyglot_focused",
                    "max_results": 5,
                    "include_snippets": True
                },
                agent_id=self.agent_id
            )
            vector_analysis["injection_vectors"]["polyglot_techniques"] = polyglot_result
            
            # Generate vector-specific payloads
            if vector_complexity == "comprehensive":
                payload_generation_result = self.researcher.perform_research(
                    tool_name="code_generate",
                    query=f"Generate comprehensive {injection_type} injection payloads with multiple vectors",
                    options={
                        "language": "python",
                        "framework": "security_testing",
                        "style": "injection_payload_generation"
                    },
                    agent_id=self.agent_id
                )
                vector_analysis["injection_vectors"]["generated_payloads"] = payload_generation_result
            
            # Analyze vector effectiveness
            vector_effectiveness = self._analyze_vector_effectiveness(vector_analysis)
            vector_analysis["effectiveness_analysis"] = vector_effectiveness
            
            # Generate testing methodology
            testing_methodology = self._generate_injection_testing_methodology(vector_analysis)
            vector_analysis["testing_methodology"] = testing_methodology
            
            return {
                "success": True,
                "vector_analysis": vector_analysis,
                "summary": f"Completed comprehensive injection vector analysis for {injection_type}"
            }
            
        except Exception as e:
            self.logger.error(f"Error studying injection vectors: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "injection_type": injection_type
            }
    
    def generate_payload_report(self, 
                              payload_data: Dict[str, Any] = Field(..., description="Payload research data to include in report"),
                              report_type: str = Field("comprehensive", description="Type of report to generate"),
                              target_audience: str = Field("security_team", description="Target audience for the report")) -> Dict[str, Any]:
        """
        Generate comprehensive payload analysis and research reports.
        
        Args:
            payload_data: Data about payload research to include
            report_type: Type of report to generate
            target_audience: Intended audience for the report
            
        Returns:
            Dictionary containing the generated payload report
        """
        try:
            self.logger.info(f"Generating {report_type} payload report")
            
            # Prepare report data
            report_data = {
                "payload_data": payload_data,
                "report_type": report_type,
                "target_audience": target_audience,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Generate report using research agent
            report_query = f"Generate {report_type} payload analysis report for {target_audience}"
            report_result = self.researcher.perform_research(
                tool_name="generate_report",
                query=report_query,
                options={
                    "report_type": f"payload_{report_type}",
                    "data": payload_data,
                    "template": "security_testing",
                    "format": "markdown",
                    "audience": target_audience
                },
                agent_id=self.agent_id
            )
            
            # Enhance report with payload-specific analysis
            if report_result.get("success"):
                enhanced_report = self._enhance_payload_report(report_result, payload_data, report_type, target_audience)
                report_data["report"] = enhanced_report
            else:
                report_data["report"] = report_result
            
            # Generate report summary
            report_summary = self._generate_payload_report_summary(report_data)
            report_data["summary"] = report_summary
            
            return {
                "success": True,
                "payload_report": report_data,
                "recommendations": self._generate_payload_report_recommendations(report_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating payload report: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "report_type": report_type
            }
    
    def _analyze_payload_effectiveness(self, payload_research: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze effectiveness of researched payloads"""
        analysis = {
            "payload_categories": len(payload_research.get("custom_payloads", {})),
            "technique_diversity": "high" if len(payload_research.get("custom_payloads", {})) > 3 else "medium",
            "context_relevance": "high" if "context_specific" in payload_research.get("custom_payloads", {}) else "medium",
            "generation_success": "generated_payloads" in payload_research.get("custom_payloads", {}),
            "overall_effectiveness": "high"
        }
        
        return analysis
    
    def _generate_payload_variations(self, payload_research: Dict[str, Any]) -> List[str]:
        """Generate payload variations based on research"""
        variations = []
        
        vulnerability_type = payload_research.get("vulnerability_type", "")
        
        variations.append(f"Basic {vulnerability_type} payloads with standard syntax")
        variations.append(f"Encoded {vulnerability_type} payloads with various encoding schemes")
        variations.append(f"Obfuscated {vulnerability_type} payloads with comment insertion")
        variations.append(f"Time-based {vulnerability_type} payloads for blind exploitation")
        variations.append(f"Boolean-based {vulnerability_type} payloads for inference attacks")
        
        if "chaining_techniques" in payload_research.get("custom_payloads", {}):
            variations.append(f"Chained {vulnerability_type} payloads for multi-stage exploitation")
        
        return variations
    
    def _assess_bypass_effectiveness(self, bypass_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess effectiveness of WAF bypass techniques"""
        assessment = {
            "technique_count": len(bypass_analysis.get("bypass_techniques", {})),
            "complexity_level": bypass_analysis.get("bypass_complexity", "standard"),
            "coverage_areas": list(bypass_analysis.get("bypass_techniques", {}).keys()),
            "success_probability": "high" if len(bypass_analysis.get("bypass_techniques", {})) > 3 else "medium"
        }
        
        return assessment
    
    def _generate_bypass_recommendations(self, bypass_analysis: Dict[str, Any]) -> List[str]:
        """Generate WAF bypass recommendations"""
        recommendations = []
        
        waf_type = bypass_analysis.get("waf_type", "")
        target_payload_type = bypass_analysis.get("target_payload_type", "")
        
        recommendations.append(f"Test {waf_type} bypass techniques systematically starting with basic methods")
        recommendations.append(f"Apply encoding techniques specific to {target_payload_type} payloads")
        recommendations.append("Use protocol-level bypass techniques for advanced evasion")
        recommendations.append("Combine multiple bypass techniques for increased success rate")
        recommendations.append("Document successful bypass methods for future testing")
        
        return recommendations
    
    def _analyze_vector_effectiveness(self, vector_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze effectiveness of injection vectors"""
        analysis = {
            "vector_categories": len(vector_analysis.get("injection_vectors", {})),
            "technique_breadth": "comprehensive" if len(vector_analysis.get("injection_vectors", {})) > 4 else "standard",
            "advanced_techniques_included": "advanced_techniques" in vector_analysis.get("injection_vectors", {}),
            "context_adaptation": "context_specific" in vector_analysis.get("injection_vectors", {}),
            "overall_coverage": "excellent"
        }
        
        return analysis
    
    def _generate_injection_testing_methodology(self, vector_analysis: Dict[str, Any]) -> List[str]:
        """Generate injection testing methodology"""
        methodology = []
        
        injection_type = vector_analysis.get("injection_type", "")
        
        methodology.append(f"1. Identify potential {injection_type} injection points")
        methodology.append("2. Test basic injection vectors with simple payloads")
        methodology.append("3. Escalate to advanced techniques if basic methods fail")
        methodology.append("4. Apply context-specific vectors based on technology stack")
        methodology.append("5. Test out-of-band techniques for blind scenarios")
        methodology.append("6. Use polyglot payloads for universal coverage")
        methodology.append("7. Document successful vectors and payloads")
        
        return methodology
    
    def _enhance_payload_report(self, report_result: Dict[str, Any], payload_data: Dict[str, Any], 
                              report_type: str, target_audience: str) -> Dict[str, Any]:
        """Enhance payload report with additional analysis"""
        enhanced_report = report_result.copy()
        
        # Add technical details for security teams
        if target_audience in ["security_team", "technical", "penetration_testers"]:
            enhanced_report["technical_analysis"] = {
                "payload_categories": "Comprehensive coverage of payload types and variations",
                "bypass_techniques": "Advanced WAF bypass and evasion methods included",
                "injection_vectors": "Multiple injection vectors and attack techniques analyzed",
                "implementation_guidance": "Step-by-step implementation and testing procedures"
            }
        
        # Add executive summary for management
        elif target_audience in ["management", "executive", "ciso"]:
            enhanced_report["executive_summary"] = {
                "security_impact": "Payload research enhances security testing effectiveness",
                "risk_mitigation": "Advanced payload techniques improve vulnerability detection",
                "resource_requirements": "Specialized knowledge and tools required for implementation",
                "business_value": "Enhanced security posture through comprehensive testing"
            }
        
        return enhanced_report
    
    def _generate_payload_report_summary(self, report_data: Dict[str, Any]) -> str:
        """Generate summary of payload report"""
        report_type = report_data.get("report_type", "comprehensive")
        target_audience = report_data.get("target_audience", "security_team")
        
        summary = f"Generated {report_type} payload analysis report for {target_audience}. "
        summary += "Report includes advanced payload techniques, bypass methods, and implementation guidance."
        
        return summary
    
    def _generate_payload_report_recommendations(self, report_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations for payload report usage"""
        recommendations = [
            "Review payload techniques with security testing team",
            "Implement advanced payloads in security testing procedures",
            "Establish payload libraries for consistent testing",
            "Train team members on advanced payload techniques",
            "Update testing methodologies based on research findings",
            "Document successful payloads for knowledge sharing",
            "Regular updates to payload research and techniques",
            "Integration with automated security testing tools"
        ]
        
        return recommendations
