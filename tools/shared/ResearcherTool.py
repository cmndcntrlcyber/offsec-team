"""
Shared Research Tool for OFFSEC-TEAM Agents

This tool provides a unified interface for all agents to access the research-agent MCP server
capabilities. It handles authentication, error management, and provides consistent interfaces
across all agents in the offsec-team ecosystem.

Available Research Capabilities:
- web_search: AI-powered web search and analysis
- web_scrape: Extract structured data from websites  
- code_generate: Generate code from natural language descriptions
- code_analyze: Analyze code for security, performance, and quality
- content_analyze: Analyze content for insights and intelligence
- content_summarize: Create concise summaries of content
- extract_information: Extract specific information from content
- generate_report: Generate comprehensive reports from data
- browser_automate: Perform browser automation tasks
"""

import os
import json
import time
import logging
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field

# Import the MCP client for research agent communication
try:
    from ..api_clients.mcp_nexus_client import MCPNexusClient
except ImportError:
    # Fallback for direct usage
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from api_clients.base_client import BaseAPIClient


class ResearchRequest(BaseModel):
    """Model for research requests"""
    tool_name: str = Field(..., description="Name of the research tool to use")
    query: str = Field(..., description="Query or input for the research tool")
    options: Dict[str, Any] = Field(default_factory=dict, description="Additional options")
    context: Optional[str] = Field(None, description="Additional context for the research")
    agent_id: Optional[str] = Field(None, description="ID of the requesting agent")


class ResearchResponse(BaseModel):
    """Model for research responses"""
    success: bool
    tool_name: str
    query: str
    result: Any
    metadata: Dict[str, Any]
    timestamp: str
    agent_id: Optional[str] = None
    error: Optional[str] = None


class ResearcherTool:
    """
    Unified research tool for all OFFSEC-TEAM agents.
    Provides access to the research-agent MCP server capabilities.
    """
    
    def __init__(self):
        self.available_tools = {
            "web_search": {
                "description": "Perform AI-powered web search and analysis",
                "category": "research",
                "parameters": ["query", "search_type", "max_results", "include_snippets"]
            },
            "web_scrape": {
                "description": "Extract structured data from websites",
                "category": "research", 
                "parameters": ["url", "selectors", "format", "follow_links"]
            },
            "code_generate": {
                "description": "Generate code from natural language descriptions",
                "category": "coding",
                "parameters": ["description", "language", "framework", "style"]
            },
            "code_analyze": {
                "description": "Analyze code for security, performance, and quality",
                "category": "coding",
                "parameters": ["code", "language", "analysis_type", "security_focus"]
            },
            "content_analyze": {
                "description": "Analyze content for insights and intelligence",
                "category": "analysis",
                "parameters": ["content", "analysis_type", "focus_areas", "output_format"]
            },
            "content_summarize": {
                "description": "Create concise summaries of content",
                "category": "analysis",
                "parameters": ["content", "summary_length", "focus", "format"]
            },
            "extract_information": {
                "description": "Extract specific information from content",
                "category": "analysis",
                "parameters": ["content", "extraction_targets", "format", "confidence_threshold"]
            },
            "generate_report": {
                "description": "Generate comprehensive reports from data",
                "category": "reporting",
                "parameters": ["data", "report_type", "template", "format"]
            },
            "browser_automate": {
                "description": "Perform browser automation tasks",
                "category": "automation",
                "parameters": ["url", "actions", "wait_conditions", "capture_data"]
            }
        }
        
        self.research_history = {}
        self.mcp_client = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("ResearcherTool")
        
        # Initialize MCP connection
        self._initialize_mcp_connection()
    
    def _initialize_mcp_connection(self):
        """Initialize connection to the research-agent MCP server"""
        try:
            # This would connect to the research-agent MCP server through the local MCP ecosystem
            # For now, we'll simulate the connection
            self.logger.info("Initializing connection to research-agent MCP server")
            # In a real implementation, this would establish the MCP connection
            self.mcp_connected = True
        except Exception as e:
            self.logger.error(f"Failed to initialize MCP connection: {str(e)}")
            self.mcp_connected = False
    
    def perform_research(self, 
                        tool_name: str = Field(..., description="Research tool to use (web_search, web_scrape, code_generate, etc.)"),
                        query: str = Field(..., description="Query or input for the research tool"),
                        options: Dict[str, Any] = Field(default_factory=dict, description="Additional options for the tool"),
                        agent_id: str = Field("unknown", description="ID of the requesting agent")) -> Dict[str, Any]:
        """
        Perform research using the specified tool from the research-agent MCP server.
        
        Args:
            tool_name: Name of the research tool to use
            query: Query or input for the research tool
            options: Additional options for the tool
            agent_id: ID of the requesting agent
            
        Returns:
            Dictionary containing research results and metadata
        """
        # Validate tool name
        if tool_name not in self.available_tools:
            return {
                "success": False,
                "error": f"Unknown research tool '{tool_name}'. Available tools: {', '.join(self.available_tools.keys())}"
            }
        
        # Validate query
        if not query or not query.strip():
            return {
                "success": False,
                "error": "Query cannot be empty"
            }
        
        try:
            self.logger.info(f"Performing research with tool '{tool_name}' for agent '{agent_id}'")
            
            # Generate research ID
            research_id = f"research-{int(time.time())}-{hashlib.md5(f'{tool_name}{query}'.encode()).hexdigest()[:8]}"
            
            # Prepare research request
            research_request = ResearchRequest(
                tool_name=tool_name,
                query=query,
                options=options,
                agent_id=agent_id
            )
            
            # Call the research-agent MCP server
            result = self._call_research_mcp(research_request)
            
            # Process and format the result
            processed_result = self._process_research_result(result, tool_name, query)
            
            # Create response
            response = ResearchResponse(
                success=True,
                tool_name=tool_name,
                query=query,
                result=processed_result,
                metadata={
                    "research_id": research_id,
                    "agent_id": agent_id,
                    "tool_category": self.available_tools[tool_name]["category"],
                    "processing_time": time.time(),
                    "options_used": options
                },
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_id=agent_id
            )
            
            # Store in history
            self.research_history[research_id] = response.dict()
            
            return response.dict()
            
        except Exception as e:
            self.logger.error(f"Error performing research: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name,
                "query": query,
                "agent_id": agent_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _call_research_mcp(self, request: ResearchRequest) -> Any:
        """Call the research-agent MCP server with the given request"""
        if not self.mcp_connected:
            raise Exception("MCP connection not available")
        
        # In a real implementation, this would make the actual MCP call
        # For now, we'll simulate different responses based on the tool
        
        tool_name = request.tool_name
        query = request.query
        options = request.options
        
        # Simulate different tool responses
        if tool_name == "web_search":
            return self._simulate_web_search(query, options)
        elif tool_name == "web_scrape":
            return self._simulate_web_scrape(query, options)
        elif tool_name == "code_generate":
            return self._simulate_code_generate(query, options)
        elif tool_name == "code_analyze":
            return self._simulate_code_analyze(query, options)
        elif tool_name == "content_analyze":
            return self._simulate_content_analyze(query, options)
        elif tool_name == "content_summarize":
            return self._simulate_content_summarize(query, options)
        elif tool_name == "extract_information":
            return self._simulate_extract_information(query, options)
        elif tool_name == "generate_report":
            return self._simulate_generate_report(query, options)
        elif tool_name == "browser_automate":
            return self._simulate_browser_automate(query, options)
        else:
            raise Exception(f"Tool '{tool_name}' not implemented")
    
    def _process_research_result(self, result: Any, tool_name: str, query: str) -> Dict[str, Any]:
        """Process and format research results"""
        processed = {
            "raw_result": result,
            "formatted_result": self._format_result_for_tool(result, tool_name),
            "summary": self._generate_result_summary(result, tool_name, query),
            "confidence": self._assess_result_confidence(result, tool_name),
            "actionable_insights": self._extract_actionable_insights(result, tool_name)
        }
        
        return processed
    
    def _format_result_for_tool(self, result: Any, tool_name: str) -> str:
        """Format result based on the tool type"""
        if tool_name in ["web_search", "content_analyze"]:
            return self._format_analysis_result(result)
        elif tool_name in ["code_generate", "code_analyze"]:
            return self._format_code_result(result)
        elif tool_name in ["content_summarize", "extract_information"]:
            return self._format_text_result(result)
        elif tool_name == "generate_report":
            return self._format_report_result(result)
        else:
            return str(result)
    
    def _generate_result_summary(self, result: Any, tool_name: str, query: str) -> str:
        """Generate a summary of the research result"""
        if isinstance(result, dict) and "summary" in result:
            return result["summary"]
        elif isinstance(result, str):
            # Generate summary for text results
            words = result.split()
            if len(words) > 50:
                return " ".join(words[:50]) + "..."
            return result
        else:
            return f"Research completed using {tool_name} for query: {query[:100]}..."
    
    def _assess_result_confidence(self, result: Any, tool_name: str) -> float:
        """Assess confidence level of the research result"""
        # Simple confidence assessment based on result characteristics
        if isinstance(result, dict):
            if "confidence" in result:
                return float(result["confidence"])
            elif "error" in result:
                return 0.1
            else:
                return 0.8
        elif isinstance(result, str) and len(result) > 100:
            return 0.7
        else:
            return 0.5
    
    def _extract_actionable_insights(self, result: Any, tool_name: str) -> List[str]:
        """Extract actionable insights from research results"""
        insights = []
        
        if tool_name == "web_search":
            insights.append("Review search results for relevant threat intelligence")
            insights.append("Consider additional searches for related topics")
        elif tool_name == "code_analyze":
            insights.append("Address any security vulnerabilities identified")
            insights.append("Consider implementing suggested improvements")
        elif tool_name == "content_analyze":
            insights.append("Review analysis findings for security implications")
            insights.append("Consider deeper investigation of flagged areas")
        
        return insights
    
    def get_research_history(self, 
                           agent_id: str = Field(None, description="Filter by agent ID"),
                           tool_name: str = Field(None, description="Filter by tool name"),
                           limit: int = Field(10, description="Maximum number of results")) -> Dict[str, Any]:
        """
        Get research history with optional filtering.
        
        Args:
            agent_id: Filter results by agent ID
            tool_name: Filter results by tool name
            limit: Maximum number of results to return
            
        Returns:
            Dictionary containing filtered research history
        """
        try:
            filtered_history = {}
            count = 0
            
            for research_id, research_data in self.research_history.items():
                if count >= limit:
                    break
                
                # Apply filters
                if agent_id and research_data.get("agent_id") != agent_id:
                    continue
                
                if tool_name and research_data.get("tool_name") != tool_name:
                    continue
                
                filtered_history[research_id] = research_data
                count += 1
            
            return {
                "success": True,
                "history": filtered_history,
                "total_results": len(filtered_history),
                "filters_applied": {
                    "agent_id": agent_id,
                    "tool_name": tool_name,
                    "limit": limit
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving research history: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_available_tools(self) -> Dict[str, Any]:
        """
        Get list of available research tools and their descriptions.
        
        Returns:
            Dictionary containing available tools and their metadata
        """
        return {
            "success": True,
            "tools": self.available_tools,
            "total_tools": len(self.available_tools),
            "categories": list(set(tool["category"] for tool in self.available_tools.values())),
            "mcp_connected": self.mcp_connected
        }
    
    # Simulation methods (these would be replaced with actual MCP calls)
    def _simulate_web_search(self, query: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate web search results"""
        return {
            "query": query,
            "results": [
                {
                    "title": f"Security Research: {query}",
                    "url": "https://example.com/security-research",
                    "snippet": f"Comprehensive analysis of {query} including threat vectors, mitigation strategies, and current trends in the cybersecurity landscape.",
                    "relevance": 0.95
                },
                {
                    "title": f"Latest Vulnerabilities Related to {query}",
                    "url": "https://cve.mitre.org/search",
                    "snippet": f"Recent CVE entries and vulnerability disclosures related to {query} with CVSS scores and remediation guidance.",
                    "relevance": 0.88
                }
            ],
            "total_results": 2,
            "search_time": 0.5,
            "summary": f"Found relevant security information about {query}"
        }
    
    def _simulate_web_scrape(self, url: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate web scraping results"""
        return {
            "url": url,
            "scraped_data": {
                "title": "Security Advisory",
                "content": f"Security information extracted from {url}",
                "metadata": {
                    "last_updated": datetime.now().isoformat(),
                    "content_type": "security_advisory"
                }
            },
            "extraction_success": True,
            "summary": f"Successfully extracted security data from {url}"
        }
    
    def _simulate_code_generate(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate code generation"""
        language = options.get("language", "python")
        return {
            "description": description,
            "generated_code": f"""# Generated {language} code for: {description}
def security_function():
    '''
    {description}
    '''
    # Implementation would go here
    pass
""",
            "language": language,
            "confidence": 0.85,
            "summary": f"Generated {language} code for {description}"
        }
    
    def _simulate_code_analyze(self, code: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate code analysis"""
        return {
            "code_snippet": code[:200] + "..." if len(code) > 200 else code,
            "analysis": {
                "security_issues": [
                    {
                        "type": "potential_sql_injection",
                        "severity": "high",
                        "line": 15,
                        "description": "Potential SQL injection vulnerability detected"
                    }
                ],
                "performance_issues": [],
                "quality_score": 7.5
            },
            "recommendations": [
                "Use parameterized queries to prevent SQL injection",
                "Add input validation for user data"
            ],
            "summary": "Code analysis completed with security recommendations"
        }
    
    def _simulate_content_analyze(self, content: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate content analysis"""
        return {
            "content_length": len(content),
            "analysis": {
                "sentiment": "neutral",
                "key_topics": ["security", "vulnerability", "threat"],
                "security_relevance": 0.9,
                "threat_indicators": ["malware", "exploit", "vulnerability"]
            },
            "insights": [
                "Content contains high security relevance",
                "Multiple threat indicators identified"
            ],
            "summary": "Content analysis reveals security-focused material"
        }
    
    def _simulate_content_summarize(self, content: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate content summarization"""
        return {
            "original_length": len(content),
            "summary": f"Summary: This content discusses security topics and provides analysis of potential threats and vulnerabilities. Key points include threat assessment, risk mitigation strategies, and security best practices.",
            "summary_length": 150,
            "key_points": [
                "Security threat analysis",
                "Risk mitigation strategies", 
                "Best practices recommendations"
            ],
            "summary": "Content successfully summarized with key security insights"
        }
    
    def _simulate_extract_information(self, content: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate information extraction"""
        return {
            "extracted_data": {
                "cve_ids": ["CVE-2024-1234", "CVE-2024-5678"],
                "ip_addresses": ["192.168.1.1", "10.0.0.1"],
                "domains": ["malicious-site.com", "threat-actor.net"],
                "file_hashes": ["a1b2c3d4e5f6", "f6e5d4c3b2a1"]
            },
            "extraction_confidence": 0.92,
            "total_extracted": 6,
            "summary": "Successfully extracted security-relevant information"
        }
    
    def _simulate_generate_report(self, data: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate report generation"""
        report_type = options.get("report_type", "security_assessment")
        return {
            "report_type": report_type,
            "report_content": f"""
# Security Assessment Report

## Executive Summary
This report provides a comprehensive analysis of the security posture based on the provided data.

## Key Findings
- Multiple security vulnerabilities identified
- Threat landscape analysis completed
- Remediation recommendations provided

## Recommendations
1. Implement security patches immediately
2. Enhance monitoring capabilities
3. Conduct regular security assessments

## Conclusion
The security assessment reveals areas for improvement and provides actionable recommendations.
""",
            "report_length": 500,
            "sections": ["executive_summary", "findings", "recommendations", "conclusion"],
            "summary": f"Generated comprehensive {report_type} report"
        }
    
    def _simulate_browser_automate(self, url: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate browser automation"""
        return {
            "url": url,
            "automation_results": {
                "page_loaded": True,
                "actions_completed": ["navigate", "extract_data", "screenshot"],
                "data_captured": {
                    "page_title": "Security Portal",
                    "form_fields": ["username", "password"],
                    "links_found": 15
                }
            },
            "execution_time": 3.2,
            "summary": f"Browser automation completed for {url}"
        }
    
    def _format_analysis_result(self, result: Any) -> str:
        """Format analysis results for display"""
        if isinstance(result, dict):
            formatted = "Analysis Results:\n"
            for key, value in result.items():
                if key != "raw_result":
                    formatted += f"- {key}: {value}\n"
            return formatted
        return str(result)
    
    def _format_code_result(self, result: Any) -> str:
        """Format code results for display"""
        if isinstance(result, dict) and "generated_code" in result:
            return f"Generated Code:\n```\n{result['generated_code']}\n```"
        elif isinstance(result, dict) and "analysis" in result:
            return f"Code Analysis:\n{json.dumps(result['analysis'], indent=2)}"
        return str(result)
    
    def _format_text_result(self, result: Any) -> str:
        """Format text results for display"""
        if isinstance(result, dict) and "summary" in result:
            return result["summary"]
        return str(result)
    
    def _format_report_result(self, result: Any) -> str:
        """Format report results for display"""
        if isinstance(result, dict) and "report_content" in result:
            return result["report_content"]
        return str(result)
