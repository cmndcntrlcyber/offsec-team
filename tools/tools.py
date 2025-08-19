"""
Enhanced Tools Class - OpenWebUI Integration

This module provides the Tools class that integrates the Enhanced Researcher Tools
with OpenWebUI, maintaining backward compatibility while providing access to all
enhanced research capabilities.
"""

import os
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

# Import the enhanced researcher tools
try:
    # Try relative import first (for package usage)
    from .enhanced_researcher_tools import EnhancedResearcherTools, EndpointConfig
except ImportError:
    try:
        # Try absolute import (for OpenWebUI)
        from tools.enhanced_researcher_tools import EnhancedResearcherTools, EndpointConfig
    except ImportError:
        try:
            # Try direct import (for standalone usage)
            from enhanced_researcher_tools import EnhancedResearcherTools, EndpointConfig
        except ImportError:
            # If all imports fail, set to None and handle gracefully
            EnhancedResearcherTools = None
            EndpointConfig = None


class Tools:
    """
    Enhanced Tools class for OpenWebUI integration.
    
    This class provides both the original Tools interface and enhanced research capabilities
    through the EnhancedResearcherTools platform. It maintains full backward compatibility
    while offering access to multi-agent research orchestration.
    """
    
    def __init__(self):
        # Initialize enhanced researcher tools
        try:
            # Try to use environment variables for configuration
            config = EndpointConfig(
                tools_api=os.getenv("TOOLS_API_URL", "https://tools.attck.nexus"),
                researcher_api=os.getenv("RESEARCHER_API_URL", "https://researcher.attck.nexus"),
                mcp_research_agent=os.getenv("MCP_RESEARCH_AGENT_URL", "https://research-agent-mcp.attck-community.workers.dev"),
                chat_return=os.getenv("CHAT_RETURN_URL", "https://chat.attck.nexus"),
                timeout=int(os.getenv("RESEARCH_TIMEOUT", "45")),
                max_retries=int(os.getenv("RESEARCH_MAX_RETRIES", "3")),
                parallel_enabled=os.getenv("RESEARCH_PARALLEL_ENABLED", "true").lower() == "true"
            )
            
            self.enhanced_researcher = EnhancedResearcherTools(config=config)
            self.enhanced_available = True
        except Exception as e:
            print(f"Warning: Enhanced researcher tools not available: {str(e)}")
            self.enhanced_researcher = None
            self.enhanced_available = False
        
        # Configuration for basic functionality
        self.researcher_base_url = os.getenv("RESEARCHER_BASE_URL", "https://researcher.attck.nexus")
        self.chat_base_url = os.getenv("CHAT_BASE_URL", "https://chat.attck.nexus")
        self.timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))

        # Headers for API requests
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Open-WebUI-Research-Agent/2.0",
        }

    def _make_request(self, endpoint: str, data: Dict[str, Any], method: str = "POST") -> Dict[str, Any]:
        """Make HTTP request with error handling and retries (fallback method)"""
        url = f"{self.researcher_base_url}{endpoint}"

        for attempt in range(self.max_retries):
            try:
                if method.upper() == "POST":
                    response = requests.post(
                        url, json=data, headers=self.headers, timeout=self.timeout
                    )
                else:
                    response = requests.get(
                        url, headers=self.headers, timeout=self.timeout
                    )

                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    return {
                        "success": False,
                        "error": f"Request failed after {self.max_retries} attempts: {str(e)}",
                        "timestamp": datetime.now().isoformat(),
                    }
                continue

        return {"success": False, "error": "Unknown error occurred"}

    def _format_user_context(self, __user__: dict = {}) -> str:
        """Format user context for research requests"""
        context = ""
        if "name" in __user__:
            context += f"User: {__user__['name']}"
        if "id" in __user__:
            context += f" (ID: {__user__['id']})"
        if "email" in __user__:
            context += f" (Email: {__user__['email']})"

        return context if context else "User: Anonymous"

    # Enhanced Research Methods (Primary Interface)
    
    def enhanced_web_search(self,
                          query: str = Field(..., description="Search query or research topic"),
                          max_results: int = Field(10, description="Maximum number of results"),
                          include_threat_intel: bool = Field(True, description="Include threat intelligence correlation"),
                          analysis_depth: str = Field("comprehensive", description="Analysis depth: basic, standard, comprehensive"),
                          __user__: dict = {}) -> str:
        """Enhanced AI-powered web search with multi-endpoint analysis and threat intelligence"""
        if self.enhanced_available:
            return self.enhanced_researcher.enhanced_web_search(
                query=query,
                max_results=max_results,
                include_threat_intel=include_threat_intel,
                analysis_depth=analysis_depth,
                __user__=__user__
            )
        else:
            # Fallback to basic web search
            return self.web_search(query=query, max_results=max_results, __user__=__user__)

    def multi_agent_vulnerability_assessment(self,
                                            target_url: str = Field(..., description="Target URL for vulnerability assessment"),
                                            assessment_depth: str = Field("comprehensive", description="Assessment depth: basic, standard, comprehensive"),
                                            include_compliance_check: bool = Field(True, description="Include compliance assessment"),
                                            __user__: dict = {}) -> str:
        """Multi-agent vulnerability assessment combining bug hunting, compliance, and threat intelligence"""
        if self.enhanced_available:
            return self.enhanced_researcher.multi_agent_vulnerability_assessment(
                target_url=target_url,
                assessment_depth=assessment_depth,
                include_compliance_check=include_compliance_check,
                __user__=__user__
            )
        else:
            # Fallback to basic vulnerability assessment
            return f"⚠️ **Enhanced vulnerability assessment not available**\n\nFalling back to basic assessment for: {target_url}\n\nPlease check Enhanced Researcher Tools configuration."

    def orchestrated_security_workflow(self,
                                     workflow_type: str = Field(..., description="Workflow type: security_audit, compliance_check, threat_assessment"),
                                     target_scope: str = Field(..., description="Target scope for the workflow"),
                                     coordination_level: str = Field("full", description="Coordination level: basic, standard, full"),
                                     __user__: dict = {}) -> str:
        """Orchestrated security workflow using multi-agent coordination"""
        if self.enhanced_available:
            return self.enhanced_researcher.orchestrated_security_workflow(
                workflow_type=workflow_type,
                target_scope=target_scope,
                coordination_level=coordination_level,
                __user__=__user__
            )
        else:
            return f"⚠️ **Orchestrated workflow not available**\n\nWorkflow type: {workflow_type}\nTarget scope: {target_scope}\n\nPlease check Enhanced Researcher Tools configuration."

    def advanced_threat_intelligence_research(self,
                                            indicators: List[str] = Field(..., description="Threat indicators to research"),
                                            threat_types: List[str] = Field(["malware", "apt", "vulnerability"], description="Types of threats to investigate"),
                                            include_attribution: bool = Field(True, description="Include threat actor attribution"),
                                            correlation_depth: str = Field("deep", description="Correlation depth: shallow, standard, deep"),
                                            __user__: dict = {}) -> str:
        """Advanced threat intelligence research with multi-source correlation"""
        if self.enhanced_available:
            return self.enhanced_researcher.advanced_threat_intelligence_research(
                indicators=indicators,
                threat_types=threat_types,
                include_attribution=include_attribution,
                correlation_depth=correlation_depth,
                __user__=__user__
            )
        else:
            return f"⚠️ **Advanced threat intelligence not available**\n\nIndicators: {', '.join(indicators)}\nThreat types: {', '.join(threat_types)}\n\nPlease check Enhanced Researcher Tools configuration."

    def infrastructure_security_assessment(self,
                                         infrastructure_config: Dict[str, Any] = Field(..., description="Infrastructure configuration to assess"),
                                         compliance_frameworks: List[str] = Field(["SOC2", "ISO27001"], description="Compliance frameworks to check"),
                                         include_iac_analysis: bool = Field(True, description="Include Infrastructure-as-Code analysis"),
                                         __user__: dict = {}) -> str:
        """Comprehensive infrastructure security assessment with compliance checking"""
        if self.enhanced_available:
            return self.enhanced_researcher.infrastructure_security_assessment(
                infrastructure_config=infrastructure_config,
                compliance_frameworks=compliance_frameworks,
                include_iac_analysis=include_iac_analysis,
                __user__=__user__
            )
        else:
            return f"⚠️ **Infrastructure assessment not available**\n\nCompliance frameworks: {', '.join(compliance_frameworks)}\n\nPlease check Enhanced Researcher Tools configuration."

    def automated_penetration_testing_workflow(self,
                                             target_url: str = Field(..., description="Target URL for penetration testing"),
                                             test_scope: List[str] = Field(["web_app", "api", "authentication"], description="Testing scope"),
                                             automation_level: str = Field("high", description="Automation level: low, medium, high"),
                                             __user__: dict = {}) -> str:
        """Automated penetration testing workflow using coordinated agents"""
        if self.enhanced_available:
            return self.enhanced_researcher.automated_penetration_testing_workflow(
                target_url=target_url,
                test_scope=test_scope,
                automation_level=automation_level,
                __user__=__user__
            )
        else:
            return f"⚠️ **Automated penetration testing not available**\n\nTarget: {target_url}\nScope: {', '.join(test_scope)}\n\nPlease check Enhanced Researcher Tools configuration."

    # Original Tools Interface (Backward Compatibility)

    def get_user_name_and_email_and_id(self, __user__: dict = {}) -> str:
        """Get the user name, Email and ID from the user object"""
        if self.enhanced_available:
            return self.enhanced_researcher.get_user_name_and_email_and_id(__user__)
        
        result = ""
        if "name" in __user__:
            result += f"User: {__user__['name']}"
        if "id" in __user__:
            result += f" (ID: {__user__['id']})"
        if "email" in __user__:
            result += f" (Email: {__user__['email']})"

        return result if result else "User: Unknown"

    def get_current_time(self) -> str:
        """Get the current time in a human-readable format"""
        if self.enhanced_available:
            return self.enhanced_researcher.get_current_time()
        
        now = datetime.now()
        current_time = now.strftime("%I:%M:%S %p")
        current_date = now.strftime("%A, %B %d, %Y")
        return f"Current Date and Time = {current_date}, {current_time}"

    def calculator(self, equation: str = Field(..., description="The mathematical equation to calculate")) -> str:
        """Calculate the result of an equation"""
        if self.enhanced_available:
            return self.enhanced_researcher.calculator(equation)
        
        try:
            # Basic safety check - only allow basic math operations
            allowed_chars = set("0123456789+-*/()., ")
            if not all(c in allowed_chars for c in equation):
                return "Invalid equation - only basic math operations allowed"

            result = eval(equation)
            return f"{equation} = {result}"
        except Exception as e:
            return f"Invalid equation: {str(e)}"

    def get_current_weather(self, city: str = Field("New York, NY", description="Get the current weather for a given city")) -> str:
        """Get the current weather for a given city"""
        if self.enhanced_available:
            return self.enhanced_researcher.get_current_weather(city)
        
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return "API key is not set in the environment variable 'OPENWEATHER_API_KEY'."

        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": api_key, "units": "metric"}

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("cod") != 200:
                return f"Error fetching weather data: {data.get('message')}"

            weather_description = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]

            return f"Weather in {city}: {temperature}°C, {weather_description}, Humidity: {humidity}%, Wind: {wind_speed} m/s"
        except requests.RequestException as e:
            return f"Error fetching weather data: {str(e)}"

    def web_search(self,
                   query: str = Field(..., description="Search query or research topic"),
                   max_results: int = Field(10, description="Maximum number of results to analyze"),
                   analyze: bool = Field(True, description="Whether to perform AI analysis on results"),
                   sources: List[str] = Field([], description="Specific domains or sources to focus on"),
                   __user__: dict = {}) -> str:
        """Perform AI-powered web search and analysis"""
        if self.enhanced_available:
            # Use enhanced web search if available
            return self.enhanced_researcher.enhanced_web_search(
                query=query,
                max_results=max_results,
                include_threat_intel=True,
                analysis_depth="comprehensive",
                __user__=__user__
            )
        
        # Fallback to basic implementation
        user_context = self._format_user_context(__user__)
        data = {
            "query": query,
            "max_results": max_results,
            "analyze": analyze,
            "sources": sources,
            "user_context": user_context,
        }

        result = self._make_request("/tools/web_search", data)

        if result.get("success"):
            return f"🔍 **Web Search Results for: {query}**\n\n{json.dumps(result.get('data', {}), indent=2)}"
        else:
            return f"❌ **Search Failed**: {result.get('error', 'Unknown error')}"

    def web_scrape(self,
                   url: str = Field(..., description="URL to scrape"),
                   selectors: Dict[str, str] = Field({}, description="CSS selectors for data extraction"),
                   wait_for: str = Field("", description="Element to wait for before scraping"),
                   headers: Dict[str, str] = Field({}, description="Custom HTTP headers"),
                   __user__: dict = {}) -> str:
        """Extract structured data from websites"""
        user_context = self._format_user_context(__user__)
        data = {
            "url": url,
            "selectors": selectors,
            "wait_for": wait_for,
            "headers": headers,
            "user_context": user_context,
        }

        result = self._make_request("/tools/web_scrape", data)

        if result.get("success"):
            return f"🌐 **Web Scraping Results for: {url}**\n\n{json.dumps(result.get('data', {}), indent=2)}"
        else:
            return f"❌ **Scraping Failed**: {result.get('error', 'Unknown error')}"

    def code_generate(self,
                      description: str = Field(..., description="Detailed description of the code to generate"),
                      language: str = Field("javascript", description="Programming language"),
                      framework: str = Field("", description="Framework or library to use"),
                      __user__: dict = {}) -> str:
        """Generate code from natural language descriptions"""
        user_context = self._format_user_context(__user__)
        data = {
            "description": description,
            "language": language,
            "framework": framework,
            "user_context": user_context,
        }

        result = self._make_request("/tools/code_generate", data)

        if result.get("success"):
            generated_code = result.get("data", {}).get("code", "No code generated")
            return f"💻 **Generated {language.title()} Code**\n\n```{language}\n{generated_code}\n```\n\n**Explanation:**\n{result.get('data', {}).get('explanation', 'No explanation provided')}"
        else:
            return f"❌ **Code Generation Failed**: {result.get('error', 'Unknown error')}"

    def code_analyze(self,
                     code: str = Field(..., description="Code to analyze"),
                     language: str = Field("javascript", description="Programming language"),
                     analysis_type: str = Field("all", description="Type of analysis: security, performance, quality, or all"),
                     __user__: dict = {}) -> str:
        """Analyze code for security, performance, and quality issues"""
        user_context = self._format_user_context(__user__)
        data = {
            "code": code,
            "language": language,
            "analysis_type": analysis_type,
            "user_context": user_context,
        }

        result = self._make_request("/tools/code_analyze", data)

        if result.get("success"):
            analysis = result.get("data", {})
            return f"🔍 **Code Analysis Results ({analysis_type})**\n\n**Issues Found:** {analysis.get('issues_count', 0)}\n\n**Analysis:**\n{analysis.get('analysis', 'No analysis provided')}\n\n**Recommendations:**\n{analysis.get('recommendations', 'No recommendations provided')}"
        else:
            return f"❌ **Code Analysis Failed**: {result.get('error', 'Unknown error')}"

    def content_analyze(self,
                        content: str = Field(..., description="Content to analyze"),
                        analysis_type: str = Field("general", description="Type of analysis: general, security, technical, intelligence, or competitive"),
                        __user__: dict = {}) -> str:
        """Analyze content for insights, key information, and intelligence"""
        user_context = self._format_user_context(__user__)
        data = {
            "content": content,
            "analysis_type": analysis_type,
            "user_context": user_context,
        }

        result = self._make_request("/tools/content_analyze", data)

        if result.get("success"):
            analysis = result.get("data", {})
            return f"📊 **Content Analysis ({analysis_type})**\n\n**Key Insights:**\n{analysis.get('insights', 'No insights provided')}\n\n**Summary:**\n{analysis.get('summary', 'No summary provided')}"
        else:
            return f"❌ **Content Analysis Failed**: {result.get('error', 'Unknown error')}"

    def content_summarize(self,
                          content: str = Field(..., description="Content to summarize"),
                          max_length: int = Field(500, description="Maximum length of summary"),
                          __user__: dict = {}) -> str:
        """Create concise summaries of long content"""
        user_context = self._format_user_context(__user__)
        data = {
            "content": content,
            "max_length": max_length,
            "user_context": user_context,
        }

        result = self._make_request("/tools/content_summarize", data)

        if result.get("success"):
            summary = result.get("data", {}).get("summary", "No summary generated")
            return f"📝 **Content Summary (max {max_length} chars)**\n\n{summary}"
        else:
            return f"❌ **Summarization Failed**: {result.get('error', 'Unknown error')}"

    def extract_information(self,
                            content: str = Field(..., description="Content to extract information from"),
                            extraction_type: str = Field("general", description="Type of information: general, technical, business, security, contact, or dates"),
                            __user__: dict = {}) -> str:
        """Extract specific types of information from content"""
        user_context = self._format_user_context(__user__)
        data = {
            "content": content,
            "extraction_type": extraction_type,
            "user_context": user_context,
        }

        result = self._make_request("/tools/extract_information", data)

        if result.get("success"):
            extracted = result.get("data", {})
            return f"🔍 **Information Extraction ({extraction_type})**\n\n{json.dumps(extracted, indent=2)}"
        else:
            return f"❌ **Information Extraction Failed**: {result.get('error', 'Unknown error')}"

    def generate_report(self,
                        data: List[Dict[str, Any]] = Field(..., description="Array of data objects to include in report"),
                        report_type: str = Field("comprehensive", description="Type of report: comprehensive, executive, technical, security, or intelligence"),
                        __user__: dict = {}) -> str:
        """Generate comprehensive reports from collected data"""
        user_context = self._format_user_context(__user__)
        request_data = {
            "data": data,
            "report_type": report_type,
            "user_context": user_context,
        }

        result = self._make_request("/tools/generate_report", request_data)

        if result.get("success"):
            report = result.get("data", {}).get("report", "No report generated")
            return f"📋 **{report_type.title()} Report**\n\n{report}"
        else:
            return f"❌ **Report Generation Failed**: {result.get('error', 'Unknown error')}"

    def research_workflow(self,
                          query: str = Field(..., description="Research query or topic"),
                          workflow: str = Field("comprehensive", description="Workflow type: comprehensive or executive"),
                          __user__: dict = {}) -> str:
        """Perform a complete research workflow"""
        if self.enhanced_available:
            # Use enhanced orchestrated workflow if available
            return self.enhanced_researcher.orchestrated_security_workflow(
                workflow_type="security_audit",
                target_scope=query,
                coordination_level="full",
                __user__=__user__
            )
        
        # Fallback to basic workflow
        user_context = self._format_user_context(__user__)
        data = {"query": query, "workflow": workflow, "user_context": user_context}

        result = self._make_request("/research", data)

        if result.get("success"):
            workflow_results = result.get("results", [])
            output = f"🔬 **Research Workflow Results for: {query}**\n\n"

            for i, step in enumerate(workflow_results, 1):
                step_name = step.get("step", f"Step {i}").replace("_", " ").title()
                step_result = step.get("result", {})

                if step_result.get("success"):
                    output += f"**{i}. {step_name}** ✅\n"
                    if "data" in step_result:
                        output += f"{json.dumps(step_result['data'], indent=2)}\n\n"
                else:
                    output += f"**{i}. {step_name}** ❌\n"
                    output += f"Error: {step_result.get('error', 'Unknown error')}\n\n"

            return output
        else:
            return f"❌ **Research Workflow Failed**: {result.get('error', 'Unknown error')}"

    def batch_research(self,
                       tools: List[Dict[str, Any]] = Field(..., description="Array of tool configurations to execute"),
                       __user__: dict = {}) -> str:
        """Execute multiple research tools in batch"""
        user_context = self._format_user_context(__user__)

        # Add user context to each tool
        for tool in tools:
            if "arguments" not in tool:
                tool["arguments"] = {}
            tool["arguments"]["user_context"] = user_context

        data = {"tools": tools}
        result = self._make_request("/batch", data)

        if result.get("success"):
            batch_results = result.get("results", [])
            output = f"🔄 **Batch Research Results**\n\n"

            for i, batch_result in enumerate(batch_results, 1):
                tool_name = batch_result.get("tool", f"Tool {i}")
                tool_result = batch_result.get("result", {})

                output += f"**{i}. {tool_name.replace('_', ' ').title()}**\n"

                if tool_result.get("success"):
                    output += "✅ Success\n"
                    if "data" in tool_result:
                        output += f"{json.dumps(tool_result['data'], indent=2)}\n\n"
                else:
                    output += f"❌ Failed: {tool_result.get('error', 'Unknown error')}\n\n"

            return output
        else:
            return f"❌ **Batch Research Failed**: {result.get('error', 'Unknown error')}"

    def researcher_health_check(self, __user__: dict = {}) -> str:
        """Check the health and status of the research infrastructure"""
        if self.enhanced_available:
            return self.enhanced_researcher.get_research_infrastructure_status(__user__)
        
        # Fallback to basic health check
        result = self._make_request("/health", {}, method="GET")

        if result.get("status") == "healthy":
            capabilities = result.get("capabilities", [])
            return f"✅ **Research Agent Status: Healthy**\n\n**Available Tools:** {len(capabilities)}\n{', '.join(capabilities)}\n\n**Version:** {result.get('version', 'Unknown')}\n**Timestamp:** {result.get('timestamp', 'Unknown')}"
        else:
            return f"❌ **Research Agent Status: Unhealthy**\n\nError: {result.get('error', 'Service unavailable')}"
