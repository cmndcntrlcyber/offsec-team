"""
title: Offsec Team Tools Auto-Router
author: attck.nexus
author_url: https://attck.nexus
funding_url: https://github.com/attck-nexus
version: 1.0
"""

import re
import json
import requests
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging
import time

class Filter:
    class Valves(BaseModel):
        priority: int = Field(
            default=10, description="Priority level for the filter operations."
        )
        api_base_url: str = Field(
            default="https://tools.attck.nexus", description="Base URL for the tools API"
        )
        researcher_api_url: str = Field(
            default="https://researcher.c3s.nexus", description="Base URL for the researcher API"
        )
        mcp_research_agent_url: str = Field(
            default="https://research-agent-mcp.attck-community.workers.dev", description="Base URL for the MCP research agent"
        )
        chat_return_url: str = Field(
            default="https://chat.attck.nexus", description="Return URL for chat responses"
        )
        enable_simultaneous_requests: bool = Field(
            default=True, description="Enable simultaneous requests to all three endpoints"
        )
        parallel_request_timeout: int = Field(
            default=30, description="Timeout for parallel requests in seconds"
        )
        bearer_token: str = Field(
            default="sk-755ea70d07874c7d9e0b46d3966eb145", description="Bearer token for API authentication"
        )
        max_turns: int = Field(
            default=50, description="Maximum conversation turns before reset"
        )
        enable_auto_routing: bool = Field(
            default=True, description="Enable automatic tool routing based on context"
        )
        enable_researcher_routing: bool = Field(
            default=True, description="Enable routing through researcher.c3s.nexus for complex analysis"
        )
        debug_mode: bool = Field(
            default=False, description="Enable debug logging"
        )

    class UserValves(BaseModel):
        max_turns: int = Field(
            default=25, description="Maximum conversation turns for user"
        )
        enable_tools: bool = Field(
            default=True, description="Allow user to access offsec tools"
        )

    def __init__(self):
        self.valves = self.Valves()
        self.available_tools = {}
        
        # Add toggle switch for easy enable/disable in Open WebUI
        self.toggle = True
        
        # Add cybersecurity-themed icon (shield with tools)
        self.icon = """data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGZpbGw9Im5vbmUiIHZpZXdCb3g9IjAgMCAyNCAyNCIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZT0iY3VycmVudENvbG9yIj4KICA8cGF0aCBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGQ9Im0xNi44NjIgNy40MzNjMC0yLjU4My0yLjA2MS00Ljc1OC00LjgxNC01LjUzN2EzLjU3MyAzLjU3MyAwIDAgMC0yLjA5NiAwQzcuMTk5IDIuNjc1IDUuMTM4IDQuODUgNS4xMzggNy40MzNjMCAxLjc1NS42MTkgMy4zMTcgMS41ODQgNC4zMTNhMTQuODA5IDE0LjgwOSAwIDAgMCA0LjI3OCA3LjUxNCAxNC45MjYgMTQuOTI2IDAgMCAwIDQuMjc4LTcuNTE0Yy45NjUtLjk5NiAxLjU4NC0yLjU1OCAxLjU4NC00LjMxM3oiLz4KICA8cGF0aCBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGQ9Im05IDEyaDYiLz4KICA8cGF0aCBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGQ9Im0xMiA5djYiLz4KPC9zdmc+"""
        self.intent_patterns = {
            'bug_hunter': [
                r'(?i)\b(vulnerability|vuln|xss|sql injection|security scan|penetration test|pentest|exploit|cve|security audit|web security|injection attack|csrf|security assessment)\b',
                r'(?i)\b(scan.*website|test.*security|find.*vulnerabilities|security.*analysis|threat.*assessment)\b',
                r'(?i)\b(detect.*framework|identify.*technology|analyze.*framework|framework.*detection|technology.*stack|fingerprint)\b',
                r'(?i)\b(detect.*for|identify.*for|analyze.*for|scan.*for|test.*for).*https?://',
                r'(?i)\b(scan).*\b(vulnerabilities|security|pentest)\b',
                r'(?i)\b(scan).*https?://.*\b(vulnerabilities|for vulnerabilities)\b'
            ],
            'rt_dev': [
                r'(?i)\b(code generation|generate.*code|create.*template|fastapi|flask|docker|terraform|infrastructure|deployment|ci/cd|devops|kubernetes|automation)\b',
                r'(?i)\b(build.*application|create.*service|deploy.*infrastructure|generate.*template|code.*template)\b'
            ],
            'burpsuite_operator': [
                r'(?i)\b(burp suite|burpsuite|burp scan|proxy|intercept|spider|intruder|repeater|scanner|web application scan)\b',
                r'(?i)\b(burp.*scan|launch.*scan|automated.*scan|payload.*testing|web.*testing)\b'
            ],
            'daedelu5': [
                r'(?i)\b(compliance|audit|policy|governance|soc2|iso27001|pci dss|gdpr|security policy|infrastructure as code|iac)\b',
                r'(?i)\b(compliance.*check|audit.*infrastructure|policy.*enforcement|regulatory.*requirements)\b'
            ],
            'nexus_kamuy': [
                r'(?i)\b(workflow|orchestration|automation|task.*scheduling|multi.*agent|coordination|collaboration|pipeline)\b',
                r'(?i)\b(orchestrate.*workflow|coordinate.*agents|manage.*tasks|schedule.*execution|automate.*process)\b'
            ]
        }
        self.tool_mappings = {}
        self.thread_contexts = {}  # Store active thread contexts
        self.logger = logging.getLogger(__name__)

    def _log(self, message: str, level: str = "info"):
        """Log message if debug mode is enabled"""
        if self.valves.debug_mode:
            if level == "error":
                self.logger.error(f"OffsecRouter: {message}")
            elif level == "warning":
                self.logger.warning(f"OffsecRouter: {message}")
            else:
                self.logger.info(f"OffsecRouter: {message}")

    def _extract_thread_context(self, body: dict, __user__: Optional[dict] = None) -> Dict[str, Any]:
        """Extract thread context from request body and user information"""
        thread_id = str(uuid.uuid4())
        user_id = "anonymous"
        
        # Try to extract user information
        if __user__:
            if isinstance(__user__, dict):
                user_id = __user__.get("id", __user__.get("name", "anonymous"))
            elif hasattr(__user__, "id"):
                user_id = __user__.id
            elif hasattr(__user__, "name"):
                user_id = __user__.name
        
        # Extract conversation history
        messages = body.get("messages", [])
        conversation_history = []
        for msg in messages[-5:]:  # Keep last 5 messages for context
            conversation_history.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")[:500]  # Truncate for size
            })
        
        context = {
            "thread_id": thread_id,
            "user_id": user_id,
            "timestamp": int(time.time()),
            "origin_endpoint": self.valves.chat_return_url,
            "conversation_history": conversation_history,
            "session_id": f"session_{hash(str(user_id))}"
        }
        
        # Store context for later retrieval
        self.thread_contexts[thread_id] = context
        self._log(f"Created thread context: {thread_id} for user: {user_id}")
        
        return context

    def _should_route_to_researcher(self, agent: str, tool: str, message: str) -> bool:
        """Determine if request should be routed through researcher.c3s.nexus"""
        if not self.valves.enable_researcher_routing:
            return False
        
        # Route complex analysis tasks to researcher
        researcher_indicators = [
            'complex', 'analysis', 'research', 'investigate', 'deep dive',
            'comprehensive', 'detailed', 'thorough', 'multi-step', 'workflow',
            'orchestrate', 'coordinate', 'collaborate', 'strategy', 'planning'
        ]
        
        message_lower = message.lower()
        has_researcher_indicator = any(indicator in message_lower for indicator in researcher_indicators)
        
        # Always route nexus_kamuy (workflow orchestration) through researcher
        if agent == 'nexus_kamuy':
            return True
        
        # Route complex security analysis through researcher
        if agent in ['bug_hunter', 'daedelu5'] and has_researcher_indicator:
            return True
        
        return has_researcher_indicator

    def _make_parallel_requests(self, context: Dict[str, Any], agent: str, tool: str, parameters: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """Make simultaneous requests to all three endpoints and aggregate responses"""
        if not self.valves.enable_simultaneous_requests:
            # Fallback to sequential routing if parallel is disabled
            return self._route_to_researcher(context, agent, tool, parameters)
        
        self._log(f"Starting parallel requests for {agent}.{tool} across all endpoints")
        
        # Prepare common headers
        headers = {
            "Authorization": "Bearer " + self.valves.bearer_token,
            "Content-Type": "application/json",
            "X-Chat-Thread-ID": context["thread_id"],
            "X-User-ID": context["user_id"],
            "X-Session-ID": context["session_id"],
            "X-Origin-Endpoint": context["origin_endpoint"]
        }
        
        # Prepare payloads for each endpoint
        tools_payload = {
            "tool_name": tool,
            "agent": agent,
            "parameters": parameters,
            "request_id": f"parallel_{context['thread_id']}_tools"
        }
        
        researcher_payload = {
            "request_type": "tool_execution",
            "agent": agent,
            "tool_name": tool,
            "parameters": parameters,
            "context": context,
            "routing_chain": [
                self.valves.chat_return_url,
                self.valves.api_base_url,
                self.valves.researcher_api_url
            ]
        }
        
        mcp_payload = {
            "message": user_message,
            "context": context,
            "agent_request": {
                "agent": agent,
                "tool": tool,
                "parameters": parameters
            },
            "capabilities_requested": ["research", "analysis", "tool_execution"],
            "routing_context": "parallel_request"
        }
        
        # Execute requests in parallel using ThreadPoolExecutor
        responses = {}
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all requests simultaneously
            future_to_endpoint = {
                executor.submit(self._request_tools_endpoint, tools_payload, headers): "tools",
                executor.submit(self._request_researcher_endpoint, researcher_payload, headers): "researcher", 
                executor.submit(self._request_mcp_endpoint, mcp_payload, headers): "mcp"
            }
            
            # Collect responses as they complete
            for future in as_completed(future_to_endpoint, timeout=self.valves.parallel_request_timeout):
                endpoint_name = future_to_endpoint[future]
                try:
                    result = future.result()
                    responses[endpoint_name] = result
                    self._log(f"Received response from {endpoint_name} endpoint")
                except Exception as e:
                    self._log(f"Error from {endpoint_name} endpoint: {str(e)}", "warning")
                    responses[endpoint_name] = {
                        "success": False,
                        "error": str(e),
                        "endpoint": endpoint_name
                    }
        
        total_time = int((time.time() - start_time) * 1000)
        self._log(f"Parallel requests completed in {total_time}ms")
        
        # Aggregate responses
        return self._aggregate_parallel_responses(responses, context, agent, tool, total_time)
    
    def _request_tools_endpoint(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Make request to tools.attck.nexus endpoint"""
        try:
            response = requests.post(
                f"{self.valves.api_base_url}/execute",
                headers=headers,
                json=payload,
                timeout=self.valves.parallel_request_timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                result["endpoint_source"] = "tools.attck.nexus"
                return result
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "endpoint_source": "tools.attck.nexus"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "endpoint_source": "tools.attck.nexus"
            }
    
    def _request_researcher_endpoint(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Make request to researcher.c3s.nexus endpoint"""
        try:
            response = requests.post(
                f"{self.valves.researcher_api_url}/analyze",
                headers=headers,
                json=payload,
                timeout=self.valves.parallel_request_timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                result["endpoint_source"] = "researcher.c3s.nexus"
                return result
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "endpoint_source": "researcher.c3s.nexus"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "endpoint_source": "researcher.c3s.nexus"
            }
    
    def _request_mcp_endpoint(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Make request to research-agent-mcp.attck-community.workers.dev endpoint"""
        try:
            response = requests.post(
                f"{self.valves.mcp_research_agent_url}/research",
                headers=headers,
                json=payload,
                timeout=self.valves.parallel_request_timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                result["endpoint_source"] = "research-agent-mcp.attck-community.workers.dev"
                return result
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "endpoint_source": "research-agent-mcp.attck-community.workers.dev"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "endpoint_source": "research-agent-mcp.attck-community.workers.dev"
            }
    
    def _aggregate_parallel_responses(self, responses: Dict[str, Dict[str, Any]], context: Dict[str, Any], agent: str, tool: str, total_time: int) -> Dict[str, Any]:
        """Aggregate responses from all parallel endpoints"""
        successful_responses = []
        failed_responses = []
        
        for endpoint, response in responses.items():
            if response.get("success", False):
                successful_responses.append(response)
            else:
                failed_responses.append(response)
        
        # Create aggregated response
        aggregated_result = {
            "success": len(successful_responses) > 0,
            "parallel_execution": True,
            "total_execution_time_ms": total_time,
            "endpoints_queried": list(responses.keys()),
            "successful_endpoints": len(successful_responses),
            "failed_endpoints": len(failed_responses),
            "context": context,
            "agent": agent,
            "tool": tool
        }
        
        if successful_responses:
            # Combine successful results
            combined_results = {}
            insights = []
            recommendations = []
            tool_results = []
            
            for response in successful_responses:
                endpoint_source = response.get("endpoint_source", "unknown")
                result = response.get("result", {})
                
                # Collect insights from researcher and MCP
                if "insights" in result:
                    insights.append(f"**{endpoint_source}**: {result['insights']}")
                
                # Collect recommendations
                if "recommendations" in result:
                    recommendations.append(f"**{endpoint_source}**: {result['recommendations']}")
                
                # Collect tool execution results
                if endpoint_source == "tools.attck.nexus":
                    tool_results.append({
                        "source": endpoint_source,
                        "execution_time": response.get("execution_time_ms", 0),
                        "result": result
                    })
                
                # Store individual endpoint results
                combined_results[endpoint_source] = result
            
            aggregated_result["result"] = {
                "combined_results": combined_results,
                "insights": "\n\n".join(insights) if insights else None,
                "recommendations": "\n\n".join(recommendations) if recommendations else None,
                "tool_results": tool_results,
                "synthesis": self._synthesize_responses(successful_responses, agent, tool)
            }
        
        if failed_responses:
            aggregated_result["errors"] = {
                endpoint["endpoint_source"]: endpoint.get("error", "Unknown error")
                for endpoint in failed_responses
            }
        
        return aggregated_result
    
    def _synthesize_responses(self, responses: List[Dict[str, Any]], agent: str, tool: str) -> str:
        """Synthesize insights from multiple endpoint responses"""
        synthesis = f"**Multi-Endpoint Analysis Summary for {agent}.{tool}**\n\n"
        
        # Count successful endpoints
        endpoint_sources = [r.get("endpoint_source", "unknown") for r in responses]
        synthesis += f"Successfully queried {len(responses)} endpoints: {', '.join(endpoint_sources)}\n\n"
        
        # Extract key findings
        key_findings = []
        for response in responses:
            result = response.get("result", {})
            source = response.get("endpoint_source", "unknown")
            
            if source == "tools.attck.nexus":
                if result.get("vulnerabilities_found"):
                    key_findings.append(f"Tools endpoint found {result['vulnerabilities_found']} vulnerabilities")
                elif result.get("template_created"):
                    key_findings.append(f"Tools endpoint successfully created {result.get('language', 'code')} template")
                elif result.get("framework"):
                    key_findings.append(f"Tools endpoint identified framework: {result['framework']}")
            
            elif source == "researcher.c3s.nexus":
                if result.get("analysis_completed"):
                    key_findings.append("Researcher provided comprehensive analysis")
                if result.get("risk_level"):
                    key_findings.append(f"Researcher assessed risk level: {result['risk_level']}")
            
            elif source == "research-agent-mcp.attck-community.workers.dev":
                if result.get("research_completed"):
                    key_findings.append("MCP research agent provided contextual insights")
                if result.get("confidence_score"):
                    key_findings.append(f"MCP confidence score: {result['confidence_score']}")
        
        if key_findings:
            synthesis += "**Key Findings:**\n" + "\n".join(f"• {finding}" for finding in key_findings)
        else:
            synthesis += "**Key Findings:** Analysis completed across multiple endpoints with detailed results available in individual responses."
        
        return synthesis

    def _route_to_researcher(self, context: Dict[str, Any], agent: str, tool: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Route request through researcher.c3s.nexus (legacy method for fallback)"""
        try:
            headers = {
                "Authorization": "Bearer " + self.valves.bearer_token,
                "Content-Type": "application/json",
                "X-Chat-Thread-ID": context["thread_id"],
                "X-User-ID": context["user_id"],
                "X-Session-ID": context["session_id"],
                "X-Origin-Endpoint": context["origin_endpoint"]
            }
            
            payload = {
                "request_type": "tool_execution",
                "agent": agent,
                "tool_name": tool,
                "parameters": parameters,
                "context": context,
                "routing_chain": [
                    self.valves.chat_return_url,
                    self.valves.api_base_url,
                    self.valves.researcher_api_url
                ]
            }
            
            self._log(f"Routing to researcher: {agent}.{tool} for thread {context['thread_id']}")
            
            response = requests.post(
                self.valves.researcher_api_url + "/analyze",
                headers=headers,
                json=payload,
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                # Ensure the response includes routing back to chat
                result["context"] = context
                result["return_to"] = self.valves.chat_return_url
                return result
            else:
                self._log(f"Researcher API error: {response.status_code} - {response.text}", "warning")
                # Fallback to direct tool execution
                return self._execute_tool(agent, tool, parameters)
                
        except Exception as e:
            self._log(f"Researcher routing error: {str(e)}", "warning")
            # Fallback to direct tool execution
            return self._execute_tool(agent, tool, parameters)

    def _handle_parallel_response(self, response: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Handle response from parallel requests and format for chat return"""
        if not response.get('success'):
            error_msg = response.get('error', 'Parallel request execution failed')
            errors = response.get('errors', {})
            
            formatted_response = f"❌ **Multi-Endpoint Request Failed**\n\n"
            formatted_response += f"**Thread ID:** `{context['thread_id']}`\n"
            formatted_response += f"**Error:** {error_msg}\n\n"
            
            if errors:
                formatted_response += "**Endpoint Errors:**\n"
                for endpoint, error in errors.items():
                    formatted_response += f"- **{endpoint}**: {error}\n"
            
            return formatted_response
        
        result = response.get('result', {})
        total_time = response.get('total_execution_time_ms', 0)
        successful_endpoints = response.get('successful_endpoints', 0)
        failed_endpoints = response.get('failed_endpoints', 0)
        
        # Main header with parallel execution indicator
        formatted_response = f"🚀 **Multi-Endpoint Analysis Complete**\n\n"
        formatted_response += f"**Thread ID:** `{context['thread_id']}`\n"
        formatted_response += f"**Total Execution Time:** {total_time}ms\n"
        formatted_response += f"**Successful Endpoints:** {successful_endpoints}/3\n"
        formatted_response += f"**User:** {context['user_id']}\n\n"
        
        # Add synthesis summary
        if result.get('synthesis'):
            formatted_response += f"**Executive Summary:**\n{result['synthesis']}\n\n"
        
        # Add insights if available
        if result.get('insights'):
            formatted_response += f"**Combined Insights:**\n{result['insights']}\n\n"
        
        # Add recommendations if available  
        if result.get('recommendations'):
            formatted_response += f"**Recommendations:**\n{result['recommendations']}\n\n"
        
        # Add detailed results from each endpoint
        combined_results = result.get('combined_results', {})
        if combined_results:
            formatted_response += "**Individual Endpoint Results:**\n\n"
            
            for endpoint, endpoint_result in combined_results.items():
                formatted_response += f"**{endpoint}:**\n"
                if isinstance(endpoint_result, dict):
                    for key, value in endpoint_result.items():
                        if key not in ['insights', 'recommendations']:  # Skip already displayed items
                            if isinstance(value, (list, dict)) and len(str(value)) > 100:
                                formatted_response += f"- **{key.title()}:** *[Complex data - see raw results]*\n"
                            else:
                                formatted_response += f"- **{key.title()}:** {value}\n"
                else:
                    formatted_response += f"- **Result:** {endpoint_result}\n"
                formatted_response += "\n"
        
        # Add tool execution results
        tool_results = result.get('tool_results', [])
        if tool_results:
            formatted_response += "**Tool Execution Details:**\n"
            for tool_result in tool_results:
                source = tool_result.get('source', 'unknown')
                exec_time = tool_result.get('execution_time', 0)
                formatted_response += f"- **{source}:** {exec_time}ms execution time\n"
            formatted_response += "\n"
        
        # Add error information if any endpoints failed
        if failed_endpoints > 0:
            errors = response.get('errors', {})
            if errors:
                formatted_response += f"**Failed Endpoints ({failed_endpoints}):**\n"
                for endpoint, error in errors.items():
                    formatted_response += f"- **{endpoint}:** {error}\n"
                formatted_response += "\n"
        
        formatted_response += f"*Routed simultaneously via: chat.attck.nexus → [tools.attck.nexus + researcher.c3s.nexus + research-agent-mcp.attck-community.workers.dev] → chat.attck.nexus*"
        
        return formatted_response

    def _handle_researcher_response(self, response: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Handle response from researcher and format for chat return (legacy method for fallback)"""
        if not response.get('success'):
            error_msg = response.get('error', 'Researcher analysis failed')
            return f"❌ **Researcher Analysis Failed**\n\nError: {error_msg}\n\n*Thread: {context['thread_id']}*"
        
        result = response.get('result', {})
        analysis_time = response.get('execution_time_ms', 0)
        
        formatted_response = f"🧠 **Researcher Analysis Complete**\n\n"
        formatted_response += f"**Thread ID:** `{context['thread_id']}`\n"
        formatted_response += f"**Analysis Time:** {analysis_time}ms\n"
        formatted_response += f"**User:** {context['user_id']}\n\n"
        
        # Include researcher insights if available
        if isinstance(result, dict):
            if result.get('insights'):
                formatted_response += f"**Insights:**\n{result['insights']}\n\n"
            
            if result.get('recommendations'):
                formatted_response += f"**Recommendations:**\n{result['recommendations']}\n\n"
            
            if result.get('tool_results'):
                formatted_response += f"**Tool Results:**\n{json.dumps(result['tool_results'], indent=2)}\n\n"
        
        formatted_response += f"*Routed via: chat.attck.nexus → tools.attck.nexus → researcher.c3s.nexus → chat.attck.nexus*"
        
        return formatted_response

    def _cleanup_old_contexts(self):
        """Clean up old thread contexts to prevent memory issues"""
        current_time = int(time.time())
        expired_contexts = []
        
        for thread_id, context in self.thread_contexts.items():
            # Remove contexts older than 1 hour
            if current_time - context.get("timestamp", 0) > 3600:
                expired_contexts.append(thread_id)
        
        for thread_id in expired_contexts:
            del self.thread_contexts[thread_id]
        
        if expired_contexts:
            self._log(f"Cleaned up {len(expired_contexts)} expired thread contexts")

    def _load_available_tools(self):
        """Load available tools from the API with retry logic"""
        import time
        
        for attempt in range(3):
            success = self._attempt_api_load(attempt + 1)
            if success:
                return True
            
            if attempt < 2:
                time.sleep(1 * (2 ** attempt))
        
        self._log("All API connection attempts failed, using fallback configuration", "warning")
        self._setup_fallback_tools()
        return False
    
    def _attempt_api_load(self, attempt_num):
        """Single attempt to load tools from API"""
        try:
            headers = {
                "Authorization": "Bearer " + self.valves.bearer_token,
                "Content-Type": "application/json"
            }
            
            self._log("Attempting to load tools (attempt " + str(attempt_num) + "/3)")
            
            response = requests.get(self.valves.api_base_url + "/agents", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.available_tools = data.get('agents', {})
                self._build_tool_mappings()
                self._log("Successfully loaded " + str(len(self.available_tools)) + " agent categories with tools")
                return True
            else:
                self._log("API returned " + str(response.status_code) + ": " + response.text, "warning")
                return False
                
        except Exception as e:
            self._log("Connection error (attempt " + str(attempt_num) + "): " + str(e), "warning")
            return False

    def _setup_fallback_tools(self):
        """Set up fallback tools when API is unavailable"""
        self.available_tools = {
            'bug_hunter': {
                'loaded': 1,
                'available_tools': [
                    'bug_hunter.detect_framework',
                    'bug_hunter.test_injection_vulnerabilities',
                    'bug_hunter.analyze_cross_site_vulnerabilities',
                    'bug_hunter.evaluate_authentication_security'
                ]
            },
            'rt_dev': {
                'loaded': 1,
                'available_tools': [
                    'rt_dev.generate_language_template',
                    'rt_dev.deploy_docker_compose_stack',
                    'rt_dev.generate_terraform_configuration'
                ]
            },
            'burpsuite_operator': {
                'loaded': 1,
                'available_tools': [
                    'burpsuite_operator.launch_automated_scan',
                    'burpsuite_operator.establish_burp_connection',
                    'burpsuite_operator.extract_scan_findings'
                ]
            },
            'daedelu5': {
                'loaded': 1,
                'available_tools': [
                    'daedelu5.audit_infrastructure_compliance',
                    'daedelu5.check_regulatory_requirements',
                    'daedelu5.enforce_security_baseline'
                ]
            },
            'nexus_kamuy': {
                'loaded': 1,
                'available_tools': [
                    'nexus_kamuy.create_multi_agent_workflow',
                    'nexus_kamuy.coordinate_multi_agent_task',
                    'nexus_kamuy.establish_collaboration_session'
                ]
            }
        }
        self._build_tool_mappings()
        self._log("Fallback tools configuration loaded")

    def _build_tool_mappings(self):
        """Build mappings from common tasks to specific tools"""
        self.tool_mappings = {
            # Bug Hunter tools
            'vulnerability_scan': ('bug_hunter', 'test_injection_vulnerabilities'),
            'security_audit': ('bug_hunter', 'analyze_cross_site_vulnerabilities'),
            'web_security_test': ('bug_hunter', 'analyze_security_settings'),
            'framework_analysis': ('bug_hunter', 'detect_framework'),
            
            # RT-Dev tools  
            'code_generation': ('rt_dev', 'generate_language_template'),
            'infrastructure_deployment': ('rt_dev', 'deploy_docker_compose_stack'),
            'terraform_config': ('rt_dev', 'generate_terraform_configuration'),
            'platform_deploy': ('rt_dev', 'deploy_to_rtpi_pen'),
            
            # BurpSuite tools
            'burp_scan': ('burpsuite_operator', 'launch_automated_scan'),
            'burp_proxy': ('burpsuite_operator', 'establish_burp_connection'),
            'scan_results': ('burpsuite_operator', 'extract_scan_findings'),
            
            # Daedelu5 tools
            'compliance_audit': ('daedelu5', 'audit_infrastructure_compliance'),
            'policy_check': ('daedelu5', 'check_regulatory_requirements'),
            'security_baseline': ('daedelu5', 'enforce_security_baseline'),
            
            # Nexus-Kamuy tools
            'workflow_orchestration': ('nexus_kamuy', 'create_multi_agent_workflow'),
            'task_coordination': ('nexus_kamuy', 'coordinate_multi_agent_task'),
            'agent_collaboration': ('nexus_kamuy', 'establish_collaboration_session')
        }

    def _detect_intent(self, message: str) -> Optional[str]:
        """Detect user intent from message content"""
        message_lower = message.lower()
        
        # Check for explicit agent mentions
        if 'bug hunter' in message_lower or 'vulnerability' in message_lower:
            return 'bug_hunter'
        elif 'rt-dev' in message_lower or 'code gen' in message_lower:
            return 'rt_dev'
        elif 'burp' in message_lower:
            return 'burpsuite_operator'
        elif 'compliance' in message_lower or 'audit' in message_lower:
            return 'daedelu5'
        elif 'workflow' in message_lower or 'orchestrat' in message_lower:
            return 'nexus_kamuy'
        
        # Pattern matching for intent detection
        for agent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message):
                    return agent
        
        return None

    def _extract_parameters(self, message: str, agent: str, tool: str) -> Dict[str, Any]:
        """Extract parameters from natural language message"""
        params = {}
        
        # URL extraction
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, message)
        if urls:
            params['target_url'] = urls[0]
            params['url'] = urls[0]  # Alternative parameter name
        
        # Common parameter extraction based on context
        if agent == 'bug_hunter':
            if 'deep' in message.lower():
                params['scan_depth'] = 'deep'
            elif 'shallow' in message.lower():
                params['scan_depth'] = 'shallow'
            else:
                params['scan_depth'] = 'medium'
                
            params['include_blind'] = 'blind' in message.lower()
            
        elif agent == 'rt_dev':
            # Extract programming language
            languages = ['python', 'javascript', 'go', 'rust', 'java', 'typescript']
            for lang in languages:
                if lang in message.lower():
                    params['language'] = lang
                    break
            else:
                params['language'] = 'python'  # default
                
            # Extract framework
            if 'fastapi' in message.lower():
                params['template_type'] = 'fastapi'
            elif 'flask' in message.lower():
                params['template_type'] = 'flask'
            elif 'express' in message.lower():
                params['template_type'] = 'express'
            else:
                params['template_type'] = 'fastapi'  # default
                
            params['include_tests'] = 'test' in message.lower()
            
        elif agent == 'daedelu5':
            # Extract compliance framework
            if 'soc2' in message.lower() or 'soc 2' in message.lower():
                params['framework'] = 'SOC2'
            elif 'iso27001' in message.lower() or 'iso 27001' in message.lower():
                params['framework'] = 'ISO27001'
            elif 'pci' in message.lower():
                params['framework'] = 'PCI_DSS'
            else:
                params['framework'] = 'SOC2'  # default
        
        return params

    def _select_best_tool(self, agent: str, message: str) -> str:
        """Select the best tool for the given agent and message context"""
        message_lower = message.lower()
        
        # Agent-specific tool selection logic
        if agent == 'bug_hunter':
            if 'xss' in message_lower or 'cross site' in message_lower:
                return 'analyze_cross_site_vulnerabilities'
            elif 'injection' in message_lower or 'sql' in message_lower:
                return 'test_injection_vulnerabilities'
            elif 'auth' in message_lower or 'login' in message_lower:
                return 'evaluate_authentication_security'
            elif 'framework' in message_lower or 'detect' in message_lower:
                return 'detect_framework'
            else:
                return 'test_injection_vulnerabilities'  # default comprehensive scan
                
        elif agent == 'rt_dev':
            if 'template' in message_lower or 'generate' in message_lower:
                return 'generate_language_template'
            elif 'docker' in message_lower or 'deploy' in message_lower:
                return 'deploy_docker_compose_stack'
            elif 'terraform' in message_lower or 'infrastructure' in message_lower:
                return 'generate_terraform_configuration'
            else:
                return 'generate_language_template'
                
        elif agent == 'burpsuite_operator':
            if 'scan' in message_lower:
                return 'launch_automated_scan'
            elif 'connect' in message_lower or 'proxy' in message_lower:
                return 'establish_burp_connection'
            elif 'results' in message_lower or 'findings' in message_lower:
                return 'extract_scan_findings'
            else:
                return 'launch_automated_scan'
                
        elif agent == 'daedelu5':
            if 'audit' in message_lower:
                return 'audit_infrastructure_compliance'
            elif 'policy' in message_lower:
                return 'check_regulatory_requirements'
            elif 'baseline' in message_lower or 'harden' in message_lower:
                return 'enforce_security_baseline'
            else:
                return 'audit_infrastructure_compliance'
                
        elif agent == 'nexus_kamuy':
            if 'workflow' in message_lower:
                return 'create_multi_agent_workflow'
            elif 'coordinate' in message_lower:
                return 'coordinate_multi_agent_task'
            elif 'collaborate' in message_lower:
                return 'establish_collaboration_session'
            else:
                return 'create_multi_agent_workflow'
        
        # Fallback to first available tool for the agent
        agent_info = self.available_tools.get(agent, {})
        tools = agent_info.get('available_tools', [])
        return tools[0].split('.')[-1] if tools else 'unknown_tool'

    def _execute_tool(self, agent: str, tool: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool via the API with fallback handling"""
        import time
        
        for attempt in range(2):
            result = self._try_execute_tool(agent, tool, parameters, attempt + 1)
            if result is not None:
                return result
            
            if attempt < 1:
                time.sleep(1 * (2 ** attempt))
        
        self._log("API unavailable, returning simulated response for " + agent + "." + tool, "warning")
        return self._generate_mock_response(agent, tool, parameters)
    
    def _try_execute_tool(self, agent: str, tool: str, parameters: Dict[str, Any], attempt_num: int):
        """Single attempt to execute tool via API"""
        try:
            headers = {
                "Authorization": "Bearer " + self.valves.bearer_token,
                "Content-Type": "application/json"
            }
            
            request_id = "openwebui_" + str(hash(str(parameters)))
            payload = {
                "tool_name": tool,
                "agent": agent,
                "parameters": parameters,
                "request_id": request_id
            }
            
            self._log("Executing " + agent + "." + tool + " (attempt " + str(attempt_num) + ")")
            
            response = requests.post(
                self.valves.api_base_url + "/execute", 
                headers=headers, 
                json=payload, 
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self._log("API error: " + str(response.status_code) + " - " + response.text, "warning")
                return None
                
        except Exception as e:
            self._log("API error (attempt " + str(attempt_num) + "): " + str(e), "warning")
            return None

    def _generate_mock_response(self, agent: str, tool: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a mock response when the real API is unavailable"""
        import time
        
        mock_responses = {
            'bug_hunter': {
                'detect_framework': {
                    'success': True,
                    'result': {
                        'framework': 'Unknown (API Offline)',
                        'confidence': 0.0,
                        'technologies': ['Simulated Response'],
                        'note': 'This is a simulated response - API is currently unavailable'
                    },
                    'execution_time_ms': 100
                },
                'test_injection_vulnerabilities': {
                    'success': True,
                    'result': {
                        'vulnerabilities_found': 0,
                        'scan_status': 'Simulated (API Offline)',
                        'note': 'This is a simulated response - API is currently unavailable'
                    },
                    'execution_time_ms': 150
                }
            },
            'rt_dev': {
                'generate_language_template': {
                    'success': True,
                    'result': {
                        'template_created': True,
                        'language': parameters.get('language', 'python'),
                        'framework': parameters.get('template_type', 'fastapi'),
                        'note': 'This is a simulated response - API is currently unavailable'
                    },
                    'execution_time_ms': 200
                }
            }
        }
        
        # Get agent-specific mock response
        agent_responses = mock_responses.get(agent, {})
        tool_response = agent_responses.get(tool, {
            'success': True,
            'result': {
                'status': 'Simulated Success',
                'agent': agent,
                'tool': tool,
                'parameters': parameters,
                'note': 'This is a simulated response - API is currently unavailable'
            },
            'execution_time_ms': 100
        })
        
        return tool_response

    def _format_tool_response(self, response: Dict[str, Any], agent: str, tool: str) -> str:
        """Format tool response for natural conversation"""
        if not response.get('success'):
            error_msg = response.get('error', 'Unknown error')
            return f"❌ **Tool Execution Failed**\n\nAgent: {agent}\nTool: {tool}\nError: {error_msg}"
        
        result = response.get('result', {})
        execution_time = response.get('execution_time_ms', 0)
        
        formatted_response = f"✅ **{agent.title().replace('_', '-')} Tool Executed Successfully**\n\n"
        formatted_response += f"**Tool:** `{tool}`\n"
        formatted_response += f"**Execution Time:** {execution_time}ms\n\n"
        
        # Format result based on type
        if isinstance(result, dict):
            formatted_response += "**Results:**\n"
            for key, value in result.items():
                if isinstance(value, (list, dict)):
                    formatted_response += f"- **{key.title()}:** {json.dumps(value, indent=2)}\n"
                else:
                    formatted_response += f"- **{key.title()}:** {value}\n"
        elif isinstance(result, list):
            formatted_response += "**Results:**\n"
            for i, item in enumerate(result, 1):
                formatted_response += f"{i}. {item}\n"
        else:
            formatted_response += f"**Result:** {result}\n"
        
        return formatted_response

    def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        """Process incoming requests and route to appropriate tools with contextual threading"""
        self._log("Processing inlet request with contextual routing")
        
        if not self.valves.enable_auto_routing:
            return body
        
        # Check user permissions - handle both dict and Pydantic model formats
        if __user__:
            try:
                # Try Pydantic model access first (Open WebUI format)
                if hasattr(__user__, "valves") and hasattr(__user__.valves, "enable_tools"):
                    if not __user__.valves.enable_tools:
                        return body
                # Fallback to dictionary access for compatibility
                elif isinstance(__user__, dict) and not __user__.get("valves", {}).get("enable_tools", True):
                    return body
            except (AttributeError, TypeError):
                # If we can't access user settings, allow by default
                pass
        
        # Clean up old contexts periodically
        self._cleanup_old_contexts()
        
        # Load tools if not already loaded
        if not self.available_tools:
            self._log("Loading available tools...")
            self._load_available_tools()
        
        messages = body.get("messages", [])
        if not messages:
            return body
        
        # Get the latest user message
        user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        if not user_message:
            return body
        
        # Check if this looks like a tool request
        tool_indicators = [
            'scan', 'test', 'generate', 'create', 'deploy', 'audit', 'check',
            'analyze', 'vulnerability', 'security', 'compliance', 'workflow', 'detect'
        ]
        
        has_tool_indicator = any(indicator in user_message.lower() for indicator in tool_indicators)
        
        if not has_tool_indicator:
            self._log(f"No tool indicators found in message: '{user_message}'")
            return body
        
        # Detect intent and select appropriate tool
        agent = self._detect_intent(user_message)
        if not agent:
            self._log("No intent detected, passing through")
            return body
        
        tool = self._select_best_tool(agent, user_message)
        parameters = self._extract_parameters(user_message, agent, tool)
        
        self._log(f"Detected intent: {agent}, tool: {tool}, params: {parameters}")
        
        # Extract thread context for routing
        thread_context = self._extract_thread_context(body, __user__)
        
        # Check if simultaneous requests are enabled
        if self.valves.enable_simultaneous_requests:
            self._log(f"Starting parallel requests for {agent}.{tool} across all endpoints")
            tool_response = self._make_parallel_requests(thread_context, agent, tool, parameters, user_message)
            formatted_response = self._handle_parallel_response(tool_response, thread_context)
        else:
            # Fallback to sequential routing when parallel requests are disabled
            if self._should_route_to_researcher(agent, tool, user_message):
                self._log(f"Sequential routing through researcher for complex analysis: {agent}.{tool}")
                tool_response = self._route_to_researcher(thread_context, agent, tool, parameters)
                formatted_response = self._handle_researcher_response(tool_response, thread_context)
            else:
                self._log(f"Sequential direct tool execution: {agent}.{tool}")
                tool_response = self._execute_tool(agent, tool, parameters)
                formatted_response = self._format_tool_response(tool_response, agent, tool)
                # Add routing info for direct execution
                formatted_response += f"\n\n*Routed via: chat.attck.nexus → tools.attck.nexus → chat.attck.nexus*"
        
        # Add tool response to the conversation
        messages.append({
            "role": "assistant",
            "content": formatted_response
        })
        
        body["messages"] = messages
        return body

    def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        """Process outgoing responses"""
        self._log("Processing outlet response")
        return body
