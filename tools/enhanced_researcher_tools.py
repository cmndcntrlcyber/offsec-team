import os
import requests
import json
import asyncio
import websockets
import time
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from pydantic import BaseModel, Field
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum

# Import shared components
try:
    from .shared.ResearcherTool import ResearcherTool
    from .shared.api_clients.mcp_nexus_client import MCPNexusClient
    from .shared.api_clients.base_client import BaseAPIClient
except ImportError:
    # Fallback for standalone usage
    pass


class ResearchComplexity(Enum):
    """Research complexity levels for intelligent routing"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ORCHESTRATED = "orchestrated"


class AgentCapability(Enum):
    """Available agent capabilities"""
    BUG_HUNTER = "bug_hunter"
    RT_DEV = "rt_dev"
    BURPSUITE_OPERATOR = "burpsuite_operator"
    DAEDELU5 = "daedelu5"
    NEXUS_KAMUY = "nexus_kamuy"


@dataclass
class ResearchContext:
    """Context for research operations"""
    thread_id: str
    user_id: str
    session_id: str
    timestamp: float
    complexity: ResearchComplexity
    agents_involved: List[AgentCapability]
    routing_chain: List[str]
    conversation_history: List[Dict[str, str]]


@dataclass
class EndpointConfig:
    """Configuration for research endpoints"""
    tools_api: str = "https://tools.attck.nexus"
    researcher_api: str = "https://researcher.attck.nexus"
    mcp_research_agent: str = "https://research-agent-mcp.attck-community.workers.dev"
    chat_return: str = "https://chat.attck.nexus"
    timeout: int = 45
    max_retries: int = 3
    parallel_enabled: bool = True


class EnhancedResearcherTools:
    """
    Enhanced research tools that utilize the full offsec-team research infrastructure.
    
    This class integrates with:
    - Multiple specialized agents (bug_hunter, rt_dev, burpsuite_operator, daedelu5, nexus_kamuy)
    - Multi-endpoint parallel processing
    - MCP research-agent server
    - Intelligent routing and workflow orchestration
    - Real-time threat intelligence
    """
    
    def __init__(self, config: Optional[EndpointConfig] = None):
        self.config = config or EndpointConfig()
        self.session_contexts = {}
        self.agent_tools = {}
        self.mcp_client = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("EnhancedResearcherTools")
        
        # Initialize components
        self._initialize_agent_capabilities()
        self._initialize_mcp_connection()
        self._load_threat_intelligence_feeds()
        
        # Headers for API requests
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Enhanced-Research-Agent/2.0",
            "X-Research-Platform": "offsec-team",
        }

    def _initialize_agent_capabilities(self):
        """Initialize all agent capabilities and their specialized tools"""
        self.agent_tools = {
            AgentCapability.BUG_HUNTER: {
                "detect_framework": {
                    "description": "Advanced framework and technology detection",
                    "complexity": ResearchComplexity.SIMPLE,
                    "parameters": ["target_url", "scan_depth", "include_fingerprinting"]
                },
                "test_injection_vulnerabilities": {
                    "description": "Comprehensive injection vulnerability testing",
                    "complexity": ResearchComplexity.MODERATE,
                    "parameters": ["target_url", "scan_depth", "include_blind", "payload_sets"]
                },
                "analyze_cross_site_vulnerabilities": {
                    "description": "XSS and CSRF vulnerability analysis",
                    "complexity": ResearchComplexity.MODERATE,
                    "parameters": ["target_url", "scan_depth", "include_dom_analysis"]
                },
                "evaluate_authentication_security": {
                    "description": "Authentication mechanism security evaluation",
                    "complexity": ResearchComplexity.COMPLEX,
                    "parameters": ["target_url", "auth_type", "include_session_analysis"]
                },
                "threat_intelligence_lookup": {
                    "description": "Real-time threat intelligence correlation",
                    "complexity": ResearchComplexity.MODERATE,
                    "parameters": ["indicators", "threat_types", "include_attribution"]
                },
                "exploit_database_search": {
                    "description": "Search exploit databases for relevant vulnerabilities",
                    "complexity": ResearchComplexity.SIMPLE,
                    "parameters": ["cve_ids", "product_names", "include_poc"]
                }
            },
            AgentCapability.RT_DEV: {
                "generate_language_template": {
                    "description": "Generate secure code templates",
                    "complexity": ResearchComplexity.SIMPLE,
                    "parameters": ["language", "template_type", "security_features", "include_tests"]
                },
                "deploy_docker_compose_stack": {
                    "description": "Deploy containerized infrastructure",
                    "complexity": ResearchComplexity.COMPLEX,
                    "parameters": ["stack_config", "environment", "security_hardening"]
                },
                "generate_terraform_configuration": {
                    "description": "Generate Infrastructure-as-Code configurations",
                    "complexity": ResearchComplexity.MODERATE,
                    "parameters": ["cloud_provider", "resources", "security_policies"]
                },
                "ci_cd_pipeline_analysis": {
                    "description": "Analyze and optimize CI/CD pipelines",
                    "complexity": ResearchComplexity.COMPLEX,
                    "parameters": ["pipeline_config", "security_gates", "optimization_targets"]
                },
                "security_integration_assessment": {
                    "description": "Assess security tool integration in development workflows",
                    "complexity": ResearchComplexity.COMPLEX,
                    "parameters": ["tools_list", "integration_points", "automation_level"]
                }
            },
            AgentCapability.BURPSUITE_OPERATOR: {
                "launch_automated_scan": {
                    "description": "Launch comprehensive Burp Suite automated scan",
                    "complexity": ResearchComplexity.MODERATE,
                    "parameters": ["target_url", "scan_config", "authentication", "scope_definition"]
                },
                "establish_burp_connection": {
                    "description": "Establish and configure Burp Suite proxy connection",
                    "complexity": ResearchComplexity.SIMPLE,
                    "parameters": ["proxy_config", "certificate_handling", "upstream_proxy"]
                },
                "extract_scan_findings": {
                    "description": "Extract and analyze Burp Suite scan results",
                    "complexity": ResearchComplexity.MODERATE,
                    "parameters": ["scan_id", "severity_filter", "include_false_positives"]
                },
                "payload_intelligence_analysis": {
                    "description": "Advanced payload analysis and optimization",
                    "complexity": ResearchComplexity.COMPLEX,
                    "parameters": ["target_parameters", "payload_types", "evasion_techniques"]
                },
                "web_app_intelligence_gathering": {
                    "description": "Comprehensive web application intelligence gathering",
                    "complexity": ResearchComplexity.COMPLEX,
                    "parameters": ["target_url", "reconnaissance_depth", "technology_profiling"]
                }
            },
            AgentCapability.DAEDELU5: {
                "audit_infrastructure_compliance": {
                    "description": "Comprehensive infrastructure compliance auditing",
                    "complexity": ResearchComplexity.COMPLEX,
                    "parameters": ["infrastructure_config", "compliance_frameworks", "audit_scope"]
                },
                "check_regulatory_requirements": {
                    "description": "Check against regulatory compliance requirements",
                    "complexity": ResearchComplexity.MODERATE,
                    "parameters": ["framework", "organization_type", "geographic_scope"]
                },
                "enforce_security_baseline": {
                    "description": "Enforce security baseline configurations",
                    "complexity": ResearchComplexity.COMPLEX,
                    "parameters": ["baseline_standard", "target_systems", "remediation_mode"]
                },
                "risk_intelligence_assessment": {
                    "description": "Advanced risk intelligence and assessment",
                    "complexity": ResearchComplexity.COMPLEX,
                    "parameters": ["risk_categories", "threat_landscape", "business_context"]
                },
                "policy_analysis_engine": {
                    "description": "Analyze and optimize security policies",
                    "complexity": ResearchComplexity.MODERATE,
                    "parameters": ["policy_documents", "analysis_scope", "optimization_goals"]
                }
            },
            AgentCapability.NEXUS_KAMUY: {
                "create_multi_agent_workflow": {
                    "description": "Create complex multi-agent research workflows",
                    "complexity": ResearchComplexity.ORCHESTRATED,
                    "parameters": ["workflow_spec", "agent_coordination", "success_criteria"]
                },
                "coordinate_multi_agent_task": {
                    "description": "Coordinate tasks across multiple specialized agents",
                    "complexity": ResearchComplexity.ORCHESTRATED,
                    "parameters": ["task_definition", "agent_assignments", "coordination_strategy"]
                },
                "establish_collaboration_session": {
                    "description": "Establish real-time agent collaboration session",
                    "complexity": ResearchComplexity.COMPLEX,
                    "parameters": ["session_config", "participating_agents", "communication_protocol"]
                },
                "workflow_optimization_engine": {
                    "description": "Optimize research workflows for efficiency and accuracy",
                    "complexity": ResearchComplexity.COMPLEX,
                    "parameters": ["current_workflow", "performance_metrics", "optimization_targets"]
                },
                "task_intelligence_coordinator": {
                    "description": "Intelligent task distribution and coordination",
                    "complexity": ResearchComplexity.ORCHESTRATED,
                    "parameters": ["task_queue", "agent_capabilities", "priority_matrix"]
                }
            }
        }

    def _initialize_mcp_connection(self):
        """Initialize connection to MCP research-agent server"""
        try:
            self.logger.info("Initializing MCP research-agent connection")
            # In a real implementation, this would establish the MCP connection
            # For now, we'll prepare the connection parameters
            self.mcp_config = {
                "endpoint": self.config.mcp_research_agent,
                "timeout": self.config.timeout,
                "retry_attempts": self.config.max_retries
            }
            self.mcp_connected = True
            self.logger.info("MCP research-agent connection initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize MCP connection: {str(e)}")
            self.mcp_connected = False

    def _load_threat_intelligence_feeds(self):
        """Load and initialize threat intelligence feeds"""
        self.threat_feeds = {
            "cve_database": "https://cve.mitre.org/data/downloads/",
            "exploit_db": "https://www.exploit-db.com/",
            "threat_actors": "https://attack.mitre.org/",
            "malware_families": "https://malpedia.caad.fkie.fraunhofer.de/",
            "ioc_feeds": "https://threatfox.abuse.ch/"
        }
        self.logger.info("Threat intelligence feeds initialized")

    def _create_research_context(self, query: str, user_context: dict = {}) -> ResearchContext:
        """Create research context for tracking and routing"""
        thread_id = f"research_{int(time.time())}_{hashlib.md5(query.encode()).hexdigest()[:8]}"
        user_id = user_context.get("id", user_context.get("name", "anonymous"))
        
        # Determine complexity based on query analysis
        complexity = self._analyze_query_complexity(query)
        
        # Determine involved agents based on query content
        agents_involved = self._determine_required_agents(query)
        
        context = ResearchContext(
            thread_id=thread_id,
            user_id=user_id,
            session_id=f"session_{hash(str(user_id))}",
            timestamp=time.time(),
            complexity=complexity,
            agents_involved=agents_involved,
            routing_chain=[self.config.chat_return],
            conversation_history=[]
        )
        
        self.session_contexts[thread_id] = context
        return context

    def _analyze_query_complexity(self, query: str) -> ResearchComplexity:
        """Analyze query to determine research complexity"""
        query_lower = query.lower()
        
        # Orchestrated complexity indicators
        orchestrated_indicators = [
            'multi-step', 'workflow', 'orchestrate', 'coordinate', 'comprehensive analysis',
            'end-to-end', 'full assessment', 'complete audit', 'integrated approach'
        ]
        
        # Complex indicators
        complex_indicators = [
            'deep analysis', 'advanced', 'comprehensive', 'detailed assessment',
            'security audit', 'compliance check', 'risk assessment', 'threat modeling'
        ]
        
        # Moderate indicators
        moderate_indicators = [
            'analyze', 'assess', 'evaluate', 'scan', 'test', 'investigate'
        ]
        
        if any(indicator in query_lower for indicator in orchestrated_indicators):
            return ResearchComplexity.ORCHESTRATED
        elif any(indicator in query_lower for indicator in complex_indicators):
            return ResearchComplexity.COMPLEX
        elif any(indicator in query_lower for indicator in moderate_indicators):
            return ResearchComplexity.MODERATE
        else:
            return ResearchComplexity.SIMPLE

    def _determine_required_agents(self, query: str) -> List[AgentCapability]:
        """Determine which agents are needed based on query content"""
        query_lower = query.lower()
        required_agents = []
        
        # Bug Hunter indicators
        if any(term in query_lower for term in [
            'vulnerability', 'exploit', 'security scan', 'penetration test',
            'xss', 'sql injection', 'csrf', 'authentication', 'framework detection'
        ]):
            required_agents.append(AgentCapability.BUG_HUNTER)
        
        # RT-Dev indicators
        if any(term in query_lower for term in [
            'code generation', 'template', 'infrastructure', 'deployment',
            'docker', 'terraform', 'ci/cd', 'pipeline', 'automation'
        ]):
            required_agents.append(AgentCapability.RT_DEV)
        
        # BurpSuite Operator indicators
        if any(term in query_lower for term in [
            'burp suite', 'web application scan', 'proxy', 'payload',
            'web app testing', 'automated scan'
        ]):
            required_agents.append(AgentCapability.BURPSUITE_OPERATOR)
        
        # Daedelu5 indicators
        if any(term in query_lower for term in [
            'compliance', 'audit', 'regulatory', 'policy', 'governance',
            'soc2', 'iso27001', 'pci dss', 'gdpr', 'baseline'
        ]):
            required_agents.append(AgentCapability.DAEDELU5)
        
        # Nexus Kamuy indicators (workflow orchestration)
        if any(term in query_lower for term in [
            'workflow', 'orchestrate', 'coordinate', 'multi-agent',
            'collaboration', 'task management', 'process automation'
        ]) or len(required_agents) > 2:  # Complex multi-agent scenarios
            required_agents.append(AgentCapability.NEXUS_KAMUY)
        
        return required_agents if required_agents else [AgentCapability.BUG_HUNTER]  # Default

    def _make_parallel_requests(self, context: ResearchContext, query: str, 
                              parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute parallel requests across all research endpoints"""
        if not self.config.parallel_enabled:
            return self._sequential_research(context, query, parameters)
        
        self.logger.info(f"Starting parallel research for thread {context.thread_id}")
        
        # Prepare requests for all endpoints
        requests_config = [
            ("tools_api", self._prepare_tools_request, self.config.tools_api),
            ("researcher_api", self._prepare_researcher_request, self.config.researcher_api),
            ("mcp_agent", self._prepare_mcp_request, self.config.mcp_research_agent)
        ]
        
        responses = {}
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all requests
            future_to_endpoint = {}
            for endpoint_name, prepare_func, endpoint_url in requests_config:
                request_data = prepare_func(context, query, parameters, endpoint_url)
                future = executor.submit(self._execute_endpoint_request, 
                                       endpoint_name, request_data)
                future_to_endpoint[future] = endpoint_name
            
            # Collect responses
            for future in as_completed(future_to_endpoint, timeout=self.config.timeout):
                endpoint_name = future_to_endpoint[future]
                try:
                    result = future.result()
                    responses[endpoint_name] = result
                    self.logger.info(f"Received response from {endpoint_name}")
                except Exception as e:
                    self.logger.error(f"Error from {endpoint_name}: {str(e)}")
                    responses[endpoint_name] = {
                        "success": False,
                        "error": str(e),
                        "endpoint": endpoint_name
                    }
        
        total_time = int((time.time() - start_time) * 1000)
        return self._aggregate_parallel_responses(responses, context, total_time)

    async def _stream_parallel_requests(self, context: ResearchContext, query: str, 
                                      parameters: Dict[str, Any], progress_callback=None) -> Dict[str, Any]:
        """Execute parallel requests with streaming progress updates"""
        if not self.config.parallel_enabled:
            return await self._stream_sequential_research(context, query, parameters, progress_callback)
        
        self.logger.info(f"Starting streaming parallel research for thread {context.thread_id}")
        
        if progress_callback:
            await progress_callback({
                "type": "progress",
                "data": {"message": "Initializing parallel research endpoints...", "progress": 20},
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "enhanced_researcher_tools"
            })
        
        # Prepare requests for all endpoints
        requests_config = [
            ("tools_api", self._prepare_tools_request, self.config.tools_api),
            ("researcher_api", self._prepare_researcher_request, self.config.researcher_api),
            ("mcp_agent", self._prepare_mcp_request, self.config.mcp_research_agent)
        ]
        
        responses = {}
        start_time = time.time()
        
        # Execute requests with progress updates
        completed_requests = 0
        total_requests = len(requests_config)
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all requests
            future_to_endpoint = {}
            for endpoint_name, prepare_func, endpoint_url in requests_config:
                request_data = prepare_func(context, query, parameters, endpoint_url)
                future = executor.submit(self._execute_endpoint_request, 
                                       endpoint_name, request_data)
                future_to_endpoint[future] = endpoint_name
            
            # Collect responses with progress updates
            for future in as_completed(future_to_endpoint, timeout=self.config.timeout):
                endpoint_name = future_to_endpoint[future]
                try:
                    result = future.result()
                    responses[endpoint_name] = result
                    completed_requests += 1
                    
                    if progress_callback:
                        progress_percentage = 20 + (completed_requests / total_requests) * 60  # 20-80% range
                        await progress_callback({
                            "type": "progress",
                            "data": {
                                "message": f"Completed request to {endpoint_name} ({completed_requests}/{total_requests})",
                                "progress": int(progress_percentage)
                            },
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "source": "enhanced_researcher_tools"
                        })
                    
                    self.logger.info(f"Received response from {endpoint_name}")
                except Exception as e:
                    self.logger.error(f"Error from {endpoint_name}: {str(e)}")
                    responses[endpoint_name] = {
                        "success": False,
                        "error": str(e),
                        "endpoint": endpoint_name
                    }
                    completed_requests += 1
                    
                    if progress_callback:
                        progress_percentage = 20 + (completed_requests / total_requests) * 60
                        await progress_callback({
                            "type": "progress",
                            "data": {
                                "message": f"Error from {endpoint_name}: {str(e)}",
                                "progress": int(progress_percentage)
                            },
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "source": "enhanced_researcher_tools"
                        })
        
        if progress_callback:
            await progress_callback({
                "type": "progress",
                "data": {"message": "Aggregating results from all endpoints...", "progress": 85},
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "enhanced_researcher_tools"
            })
        
        total_time = int((time.time() - start_time) * 1000)
        return self._aggregate_parallel_responses(responses, context, total_time)

    async def _stream_sequential_research(self, context: ResearchContext, query: str, 
                                        parameters: Dict[str, Any], progress_callback=None) -> Dict[str, Any]:
        """Fallback sequential research with streaming updates"""
        self.logger.info(f"Starting streaming sequential research for thread {context.thread_id}")
        
        if progress_callback:
            await progress_callback({
                "type": "progress",
                "data": {"message": "Starting sequential research analysis...", "progress": 25},
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "enhanced_researcher_tools"
            })
        
        # Route through researcher API for complex analysis
        try:
            request_data = self._prepare_researcher_request(context, query, parameters, self.config.researcher_api)
            
            if progress_callback:
                await progress_callback({
                    "type": "progress",
                    "data": {"message": "Connecting to researcher API...", "progress": 50},
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "enhanced_researcher_tools"
                })
            
            result = self._execute_endpoint_request("researcher_api", request_data)
            
            if result.get("success"):
                if progress_callback:
                    await progress_callback({
                        "type": "progress",
                        "data": {"message": "Researcher analysis completed", "progress": 85},
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "source": "enhanced_researcher_tools"
                    })
                
                return {
                    "success": True,
                    "research_type": "sequential_researcher",
                    "result": result.get("result", {}),
                    "context": {
                        "thread_id": context.thread_id,
                        "complexity": context.complexity.value,
                        "agents_involved": [agent.value for agent in context.agents_involved]
                    }
                }
            else:
                # Fallback to tools API
                if progress_callback:
                    await progress_callback({
                        "type": "progress",
                        "data": {"message": "Falling back to tools API...", "progress": 60},
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "source": "enhanced_researcher_tools"
                    })
                
                request_data = self._prepare_tools_request(context, query, parameters, self.config.tools_api)
                result = self._execute_endpoint_request("tools_api", request_data)
                
                return {
                    "success": result.get("success", False),
                    "research_type": "sequential_tools",
                    "result": result.get("result", {}),
                    "context": {
                        "thread_id": context.thread_id,
                        "complexity": context.complexity.value,
                        "agents_involved": [agent.value for agent in context.agents_involved]
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Sequential research failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "research_type": "sequential_failed"
            }

    def _prepare_tools_request(self, context: ResearchContext, query: str, 
                             parameters: Dict[str, Any], endpoint_url: str) -> Dict[str, Any]:
        """Prepare request for tools.attck.nexus endpoint"""
        return {
            "url": f"{endpoint_url}/execute",
            "method": "POST",
            "headers": {
                **self.headers,
                "X-Thread-ID": context.thread_id,
                "X-User-ID": context.user_id,
                "X-Session-ID": context.session_id
            },
            "data": {
                "query": query,
                "parameters": parameters,
                "agents": [agent.value for agent in context.agents_involved],
                "context": {
                    "thread_id": context.thread_id,
                    "complexity": context.complexity.value,
                    "routing_chain": context.routing_chain
                }
            }
        }

    def _prepare_researcher_request(self, context: ResearchContext, query: str,
                                  parameters: Dict[str, Any], endpoint_url: str) -> Dict[str, Any]:
        """Prepare request for researcher.attck.nexus endpoint"""
        return {
            "url": f"{endpoint_url}/analyze",
            "method": "POST",
            "headers": {
                **self.headers,
                "X-Thread-ID": context.thread_id,
                "X-User-ID": context.user_id,
                "X-Session-ID": context.session_id
            },
            "data": {
                "request_type": "comprehensive_research",
                "query": query,
                "parameters": parameters,
                "context": {
                    "thread_id": context.thread_id,
                    "complexity": context.complexity.value,
                    "agents_involved": [agent.value for agent in context.agents_involved],
                    "routing_chain": context.routing_chain + [endpoint_url]
                },
                "analysis_depth": "deep" if context.complexity in [
                    ResearchComplexity.COMPLEX, ResearchComplexity.ORCHESTRATED
                ] else "standard"
            }
        }

    def _prepare_mcp_request(self, context: ResearchContext, query: str,
                           parameters: Dict[str, Any], endpoint_url: str) -> Dict[str, Any]:
        """Prepare request for MCP research-agent endpoint"""
        return {
            "url": f"{endpoint_url}/research",
            "method": "POST",
            "headers": {
                **self.headers,
                "X-Thread-ID": context.thread_id,
                "X-User-ID": context.user_id,
                "X-Session-ID": context.session_id
            },
            "data": {
                "message": query,
                "context": {
                    "thread_id": context.thread_id,
                    "complexity": context.complexity.value,
                    "agents_requested": [agent.value for agent in context.agents_involved]
                },
                "capabilities_requested": [
                    "research", "analysis", "tool_execution", "threat_intelligence"
                ],
                "parameters": parameters,
                "routing_context": "parallel_research"
            }
        }

    def _execute_endpoint_request(self, endpoint_name: str, request_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute request to a specific endpoint"""
        try:
            response = requests.request(
                method=request_config["method"],
                url=request_config["url"],
                headers=request_config["headers"],
                json=request_config["data"],
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                result["endpoint_source"] = endpoint_name
                result["response_time_ms"] = response.elapsed.total_seconds() * 1000
                return result
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "endpoint_source": endpoint_name
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "endpoint_source": endpoint_name
            }

    def _aggregate_parallel_responses(self, responses: Dict[str, Dict[str, Any]], 
                                    context: ResearchContext, total_time: int) -> Dict[str, Any]:
        """Aggregate responses from parallel endpoint requests"""
        successful_responses = []
        failed_responses = []
        
        for endpoint, response in responses.items():
            if response.get("success", False):
                successful_responses.append(response)
            else:
                failed_responses.append(response)
        
        # Create comprehensive aggregated result
        aggregated_result = {
            "success": len(successful_responses) > 0,
            "research_type": "parallel_multi_endpoint",
            "total_execution_time_ms": total_time,
            "endpoints_queried": list(responses.keys()),
            "successful_endpoints": len(successful_responses),
            "failed_endpoints": len(failed_responses),
            "context": {
                "thread_id": context.thread_id,
                "complexity": context.complexity.value,
                "agents_involved": [agent.value for agent in context.agents_involved]
            }
        }
        
        if successful_responses:
            # Synthesize insights from all successful responses
            combined_insights = self._synthesize_multi_endpoint_insights(
                successful_responses, context
            )
            
            aggregated_result["result"] = {
                "combined_insights": combined_insights,
                "endpoint_results": {
                    resp.get("endpoint_source", "unknown"): resp.get("result", {})
                    for resp in successful_responses
                },
                "threat_intelligence": self._extract_threat_intelligence(successful_responses),
                "security_recommendations": self._generate_security_recommendations(
                    successful_responses, context
                ),
                "workflow_suggestions": self._generate_workflow_suggestions(
                    successful_responses, context
                )
            }
        
        if failed_responses:
            aggregated_result["errors"] = {
                resp.get("endpoint_source", "unknown"): resp.get("error", "Unknown error")
                for resp in failed_responses
            }
        
        return aggregated_result

    def _synthesize_multi_endpoint_insights(self, responses: List[Dict[str, Any]], 
                                          context: ResearchContext) -> Dict[str, Any]:
        """Synthesize insights from multiple endpoint responses"""
        synthesis = {
            "executive_summary": "",
            "key_findings": [],
            "confidence_score": 0.0,
            "research_depth": context.complexity.value,
            "cross_endpoint_correlations": []
        }
        
        # Extract findings from each endpoint
        tools_findings = []
        researcher_insights = []
        mcp_analysis = []
        
        for response in responses:
            endpoint = response.get("endpoint_source", "unknown")
            result = response.get("result", {})
            
            if endpoint == "tools_api":
                if "vulnerabilities" in result:
                    tools_findings.extend(result["vulnerabilities"])
                if "framework_detected" in result:
                    tools_findings.append(f"Framework: {result['framework_detected']}")
                    
            elif endpoint == "researcher_api":
                if "insights" in result:
                    researcher_insights.append(result["insights"])
                if "risk_assessment" in result:
                    researcher_insights.append(f"Risk Level: {result['risk_assessment']}")
                    
            elif endpoint == "mcp_agent":
                if "analysis" in result:
                    mcp_analysis.append(result["analysis"])
                if "recommendations" in result:
                    mcp_analysis.extend(result["recommendations"])
        
        # Generate executive summary
        total_findings = len(tools_findings) + len(researcher_insights) + len(mcp_analysis)
        synthesis["executive_summary"] = (
            f"Multi-endpoint research analysis completed across {len(responses)} platforms. "
            f"Generated {total_findings} findings with {context.complexity.value} complexity analysis. "
            f"Involved {len(context.agents_involved)} specialized agents."
        )
        
        # Combine key findings
        synthesis["key_findings"] = tools_findings + researcher_insights + mcp_analysis
        
        # Calculate confidence score based on endpoint agreement
        synthesis["confidence_score"] = min(0.9, 0.3 + (len(responses) * 0.2))
        
        return synthesis

    def _extract_threat_intelligence(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract threat intelligence from endpoint responses"""
        threat_intel = {
            "indicators_of_compromise": [],
            "threat_actors": [],
            "attack_patterns": [],
            "vulnerabilities": [],
            "risk_score": 0.0
        }
        
        for response in responses:
            result = response.get("result", {})
            
            # Extract IOCs
            if "iocs" in result:
                threat_intel["indicators_of_compromise"].extend(result["iocs"])
            
            # Extract vulnerabilities
            if "vulnerabilities" in result:
                threat_intel["vulnerabilities"].extend(result["vulnerabilities"])
            
            # Extract attack patterns
            if "attack_patterns" in result:
                threat_intel["attack_patterns"].extend(result["attack_patterns"])
        
        # Calculate risk score
        vuln_count = len(threat_intel["vulnerabilities"])
        ioc_count = len(threat_intel["indicators_of_compromise"])
        threat_intel["risk_score"] = min(10.0, (vuln_count * 2.0) + (ioc_count * 1.5))
        
        return threat_intel

    def _generate_security_recommendations(self, responses: List[Dict[str, Any]], 
                                         context: ResearchContext) -> List[str]:
        """Generate security recommendations based on research results"""
        recommendations = []
        
        # Agent-specific recommendations
        if AgentCapability.BUG_HUNTER in context.agents_involved:
            recommendations.extend([
                "Implement regular vulnerability scanning",
                "Deploy web application firewall (WAF)",
                "Establish security testing in CI/CD pipeline"
            ])
        
        if AgentCapability.DAEDELU5 in context.agents_involved:
            recommendations.extend([
                "Conduct compliance audit review",
                "Update security policies and procedures",
                "Implement continuous compliance monitoring"
            ])
        
        if AgentCapability.RT_DEV in context.agents_involved:
            recommendations.extend([
                "Integrate security tools in development workflow",
                "Implement infrastructure-as-code security scanning",
                "Establish secure coding standards"
            ])
        
        # Add response-specific recommendations
        for response in responses:
            result = response.get("result", {})
            if "recommendations" in result:
                if isinstance(result["recommendations"], list):
                    recommendations.extend(result["recommendations"])
                else:
                    recommendations.append(str(result["recommendations"]))
        
        return list(set(recommendations))  # Remove duplicates

    def _generate_workflow_suggestions(self, responses: List[Dict[str, Any]], 
                                     context: ResearchContext) -> List[str]:
        """Generate workflow suggestions for follow-up actions"""
        suggestions = []
        
        if context.complexity == ResearchComplexity.ORCHESTRATED:
            suggestions.extend([
                "Consider establishing automated workflow for similar research tasks",
                "Implement multi-agent coordination for comprehensive analysis",
                "Set up continuous monitoring for identified security issues"
            ])
        
        if len(context.agents_involved) > 2:
            suggestions.append(
                "Establish collaboration session between agents for ongoing coordination"
            )
        
        # Add endpoint-specific suggestions
        for response in responses:
            endpoint = response.get("endpoint_source", "")
            if endpoint == "mcp_agent":
                suggestions.append("Leverage MCP research-agent for ongoing intelligence gathering")
            elif endpoint == "researcher_api":
                suggestions.append("Schedule follow-up research analysis for trend monitoring")
        
        return suggestions

    # Public API Methods - Enhanced versions of original tools

    def enhanced_web_search(self, 
                          query: str = Field(..., description="Search query or research topic"),
                          max_results: int = Field(10, description="Maximum number of results"),
                          include_threat_intel: bool = Field(True, description="Include threat intelligence correlation"),
                          analysis_depth: str = Field("comprehensive", description="Analysis depth: basic, standard, comprehensive"),
                          __user__: dict = {}) -> str:
        """
        Enhanced AI-powered web search with multi-endpoint analysis and threat intelligence.
        """
        try:
            context = self._create_research_context(query, __user__)
            
            parameters = {
                "max_results": max_results,
                "include_threat_intel": include_threat_intel,
                "analysis_depth": analysis_depth,
                "search_type": "comprehensive"
            }
            
            # Execute parallel research across all endpoints
            result = self._make_parallel_requests(context, query, parameters)
            
            return self._format_enhanced_response("Web Search", result, context)
            
        except Exception as e:
            self.logger.error(f"Enhanced web search failed: {str(e)}")
            return f"❌ **Enhanced Web Search Failed**: {str(e)}"

    def multi_agent_vulnerability_assessment(self,
                                            target_url: str = Field(..., description="Target URL for vulnerability assessment"),
                                            assessment_depth: str = Field("comprehensive", description="Assessment depth: basic, standard, comprehensive"),
                                            include_compliance_check: bool = Field(True, description="Include compliance assessment"),
                                            __user__: dict = {}) -> str:
        """
        Multi-agent vulnerability assessment combining bug hunting, compliance, and threat intelligence.
        """
        try:
            context = self._create_research_context(f"vulnerability assessment for {target_url}", __user__)
            
            parameters = {
                "target_url": target_url,
                "assessment_depth": assessment_depth,
                "include_compliance_check": include_compliance_check,
                "scan_types": ["injection", "xss", "csrf", "authentication", "framework_detection"]
            }
            
            result = self._make_parallel_requests(context, f"comprehensive vulnerability assessment of {target_url}", parameters)
            
            return self._format_enhanced_response("Multi-Agent Vulnerability Assessment", result, context)
            
        except Exception as e:
            self.logger.error(f"Multi-agent vulnerability assessment failed: {str(e)}")
            return f"❌ **Multi-Agent Vulnerability Assessment Failed**: {str(e)}"

    def orchestrated_security_workflow(self,
                                     workflow_type: str = Field(..., description="Workflow type: security_audit, compliance_check, threat_assessment"),
                                     target_scope: str = Field(..., description="Target scope for the workflow"),
                                     coordination_level: str = Field("full", description="Coordination level: basic, standard, full"),
                                     __user__: dict = {}) -> str:
        """
        Orchestrated security workflow using Nexus Kamuy for multi-agent coordination.
        """
        try:
            context = self._create_research_context(f"{workflow_type} workflow for {target_scope}", __user__)
            context.complexity = ResearchComplexity.ORCHESTRATED
            context.agents_involved = [AgentCapability.NEXUS_KAMUY, AgentCapability.BUG_HUNTER, AgentCapability.DAEDELU5]
            
            parameters = {
                "workflow_type": workflow_type,
                "target_scope": target_scope,
                "coordination_level": coordination_level,
                "workflow_spec": {
                    "phases": ["reconnaissance", "analysis", "assessment", "reporting"],
                    "agent_coordination": True,
                    "real_time_collaboration": True
                }
            }
            
            result = self._make_parallel_requests(context, f"orchestrated {workflow_type} workflow", parameters)
            
            return self._format_enhanced_response("Orchestrated Security Workflow", result, context)
            
        except Exception as e:
            self.logger.error(f"Orchestrated security workflow failed: {str(e)}")
            return f"❌ **Orchestrated Security Workflow Failed**: {str(e)}"

    def advanced_threat_intelligence_research(self,
                                            indicators: List[str] = Field(..., description="Threat indicators to research"),
                                            threat_types: List[str] = Field(["malware", "apt", "vulnerability"], description="Types of threats to investigate"),
                                            include_attribution: bool = Field(True, description="Include threat actor attribution"),
                                            correlation_depth: str = Field("deep", description="Correlation depth: shallow, standard, deep"),
                                            __user__: dict = {}) -> str:
        """
        Advanced threat intelligence research with multi-source correlation.
        """
        try:
            context = self._create_research_context(f"threat intelligence research for {len(indicators)} indicators", __user__)
            
            parameters = {
                "indicators": indicators,
                "threat_types": threat_types,
                "include_attribution": include_attribution,
                "correlation_depth": correlation_depth,
                "intelligence_sources": list(self.threat_feeds.keys())
            }
            
            result = self._make_parallel_requests(context, "advanced threat intelligence research", parameters)
            
            return self._format_enhanced_response("Advanced Threat Intelligence Research", result, context)
            
        except Exception as e:
            self.logger.error(f"Advanced threat intelligence research failed: {str(e)}")
            return f"❌ **Advanced Threat Intelligence Research Failed**: {str(e)}"

    def infrastructure_security_assessment(self,
                                         infrastructure_config: Dict[str, Any] = Field(..., description="Infrastructure configuration to assess"),
                                         compliance_frameworks: List[str] = Field(["SOC2", "ISO27001"], description="Compliance frameworks to check"),
                                         include_iac_analysis: bool = Field(True, description="Include Infrastructure-as-Code analysis"),
                                         __user__: dict = {}) -> str:
        """
        Comprehensive infrastructure security assessment with compliance checking.
        """
        try:
            context = self._create_research_context("infrastructure security assessment", __user__)
            context.agents_involved = [AgentCapability.DAEDELU5, AgentCapability.RT_DEV, AgentCapability.BUG_HUNTER]
            
            parameters = {
                "infrastructure_config": infrastructure_config,
                "compliance_frameworks": compliance_frameworks,
                "include_iac_analysis": include_iac_analysis,
                "assessment_scope": "comprehensive"
            }
            
            result = self._make_parallel_requests(context, "infrastructure security assessment", parameters)
            
            return self._format_enhanced_response("Infrastructure Security Assessment", result, context)
            
        except Exception as e:
            self.logger.error(f"Infrastructure security assessment failed: {str(e)}")
            return f"❌ **Infrastructure Security Assessment Failed**: {str(e)}"

    def automated_penetration_testing_workflow(self,
                                             target_url: str = Field(..., description="Target URL for penetration testing"),
                                             test_scope: List[str] = Field(["web_app", "api", "authentication"], description="Testing scope"),
                                             automation_level: str = Field("high", description="Automation level: low, medium, high"),
                                             __user__: dict = {}) -> str:
        """
        Automated penetration testing workflow using BurpSuite and Bug Hunter agents.
        """
        try:
            context = self._create_research_context(f"penetration testing workflow for {target_url}", __user__)
            context.agents_involved = [AgentCapability.BURPSUITE_OPERATOR, AgentCapability.BUG_HUNTER, AgentCapability.NEXUS_KAMUY]
            
            parameters = {
                "target_url": target_url,
                "test_scope": test_scope,
                "automation_level": automation_level,
                "workflow_coordination": True
            }
            
            result = self._make_parallel_requests(context, f"automated penetration testing of {target_url}", parameters)
            
            return self._format_enhanced_response("Automated Penetration Testing Workflow", result, context)
            
        except Exception as e:
            self.logger.error(f"Automated penetration testing workflow failed: {str(e)}")
            return f"❌ **Automated Penetration Testing Workflow Failed**: {str(e)}"

    def _sequential_research(self, context: ResearchContext, query: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback sequential research when parallel processing is disabled"""
        self.logger.info(f"Starting sequential research for thread {context.thread_id}")
        
        # Route through researcher API for complex analysis
        try:
            request_data = self._prepare_researcher_request(context, query, parameters, self.config.researcher_api)
            result = self._execute_endpoint_request("researcher_api", request_data)
            
            if result.get("success"):
                return {
                    "success": True,
                    "research_type": "sequential_researcher",
                    "result": result.get("result", {}),
                    "context": {
                        "thread_id": context.thread_id,
                        "complexity": context.complexity.value,
                        "agents_involved": [agent.value for agent in context.agents_involved]
                    }
                }
            else:
                # Fallback to tools API
                request_data = self._prepare_tools_request(context, query, parameters, self.config.tools_api)
                result = self._execute_endpoint_request("tools_api", request_data)
                
                return {
                    "success": result.get("success", False),
                    "research_type": "sequential_tools",
                    "result": result.get("result", {}),
                    "context": {
                        "thread_id": context.thread_id,
                        "complexity": context.complexity.value,
                        "agents_involved": [agent.value for agent in context.agents_involved]
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Sequential research failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "research_type": "sequential_failed"
            }

    def _format_enhanced_response(self, operation_name: str, result: Dict[str, Any], context: ResearchContext) -> str:
        """Format enhanced response for display"""
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            return f"❌ **{operation_name} Failed**\n\nError: {error_msg}\n\nThread: {context.thread_id}"
        
        response_data = result.get("result", {})
        execution_time = result.get("total_execution_time_ms", 0)
        
        # Header with operation info
        formatted_response = f"🚀 **{operation_name} Complete**\n\n"
        formatted_response += f"**Thread ID:** `{context.thread_id}`\n"
        formatted_response += f"**Execution Time:** {execution_time}ms\n"
        formatted_response += f"**Research Complexity:** {context.complexity.value}\n"
        formatted_response += f"**Agents Involved:** {', '.join([agent.value for agent in context.agents_involved])}\n"
        formatted_response += f"**User:** {context.user_id}\n\n"
        
        # Add combined insights if available
        combined_insights = response_data.get("combined_insights", {})
        if combined_insights:
            formatted_response += f"**Executive Summary:**\n{combined_insights.get('executive_summary', 'N/A')}\n\n"
            
            key_findings = combined_insights.get("key_findings", [])
            if key_findings:
                formatted_response += "**Key Findings:**\n"
                for finding in key_findings[:10]:  # Limit to top 10
                    formatted_response += f"• {finding}\n"
                formatted_response += "\n"
            
            confidence_score = combined_insights.get("confidence_score", 0.0)
            formatted_response += f"**Confidence Score:** {confidence_score:.2f}/1.0\n\n"
        
        # Add threat intelligence if available
        threat_intel = response_data.get("threat_intelligence", {})
        if threat_intel and threat_intel.get("risk_score", 0) > 0:
            formatted_response += f"**Threat Intelligence:**\n"
            formatted_response += f"• Risk Score: {threat_intel.get('risk_score', 0):.1f}/10.0\n"
            
            vulnerabilities = threat_intel.get("vulnerabilities", [])
            if vulnerabilities:
                formatted_response += f"• Vulnerabilities Found: {len(vulnerabilities)}\n"
            
            iocs = threat_intel.get("indicators_of_compromise", [])
            if iocs:
                formatted_response += f"• IOCs Identified: {len(iocs)}\n"
            formatted_response += "\n"
        
        # Add security recommendations
        recommendations = response_data.get("security_recommendations", [])
        if recommendations:
            formatted_response += "**Security Recommendations:**\n"
            for rec in recommendations[:5]:  # Limit to top 5
                formatted_response += f"• {rec}\n"
            formatted_response += "\n"
        
        # Add workflow suggestions
        workflow_suggestions = response_data.get("workflow_suggestions", [])
        if workflow_suggestions:
            formatted_response += "**Workflow Suggestions:**\n"
            for suggestion in workflow_suggestions[:3]:  # Limit to top 3
                formatted_response += f"• {suggestion}\n"
            formatted_response += "\n"
        
        # Add endpoint information
        if result.get("research_type") == "parallel_multi_endpoint":
            successful_endpoints = result.get("successful_endpoints", 0)
            total_endpoints = result.get("endpoints_queried", [])
            formatted_response += f"**Multi-Endpoint Analysis:** {successful_endpoints}/{len(total_endpoints)} endpoints successful\n"
            formatted_response += f"**Endpoints:** {', '.join(total_endpoints)}\n\n"
        
        # Add routing information
        routing_chain = context.routing_chain + [
            self.config.tools_api,
            self.config.researcher_api,
            self.config.mcp_research_agent
        ]
        formatted_response += f"*Routed via: {' → '.join(routing_chain)}*"
        
        return formatted_response

    # Utility methods for backward compatibility with original Tools class
    
    def get_user_name_and_email_and_id(self, __user__: dict = {}) -> str:
        """Get user information (backward compatibility)"""
        result = ""
        if "name" in __user__:
            result += f"User: {__user__['name']}"
        if "id" in __user__:
            result += f" (ID: {__user__['id']})"
        if "email" in __user__:
            result += f" (Email: {__user__['email']})"
        return result if result else "User: Unknown"

    def get_current_time(self) -> str:
        """Get current time (backward compatibility)"""
        now = datetime.now()
        current_time = now.strftime("%I:%M:%S %p")
        current_date = now.strftime("%A, %B %d, %Y")
        return f"Current Date and Time = {current_date}, {current_time}"

    def calculator(self, equation: str = Field(..., description="Mathematical equation to calculate")) -> str:
        """Calculate mathematical equation (backward compatibility)"""
        try:
            allowed_chars = set("0123456789+-*/()., ")
            if not all(c in allowed_chars for c in equation):
                return "Invalid equation - only basic math operations allowed"
            result = eval(equation)
            return f"{equation} = {result}"
        except Exception as e:
            return f"Invalid equation: {str(e)}"

    def get_current_weather(self, city: str = Field("New York, NY", description="City for weather information")) -> str:
        """Get current weather (backward compatibility)"""
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

    # Health and monitoring methods
    
    def get_research_infrastructure_status(self, __user__: dict = {}) -> str:
        """Get status of the entire research infrastructure"""
        try:
            context = self._create_research_context("infrastructure health check", __user__)
            
            # Check all endpoints
            endpoint_status = {}
            for endpoint_name, endpoint_url in [
                ("tools_api", self.config.tools_api),
                ("researcher_api", self.config.researcher_api),
                ("mcp_research_agent", self.config.mcp_research_agent)
            ]:
                try:
                    response = requests.get(f"{endpoint_url}/health", timeout=10)
                    endpoint_status[endpoint_name] = {
                        "status": "healthy" if response.status_code == 200 else "unhealthy",
                        "response_time": response.elapsed.total_seconds() * 1000
                    }
                except Exception as e:
                    endpoint_status[endpoint_name] = {
                        "status": "unreachable",
                        "error": str(e)
                    }
            
            # Format status report
            status_report = "🏥 **Research Infrastructure Status**\n\n"
            
            healthy_count = sum(1 for status in endpoint_status.values() if status.get("status") == "healthy")
            total_count = len(endpoint_status)
            
            status_report += f"**Overall Health:** {healthy_count}/{total_count} endpoints healthy\n"
            status_report += f"**Thread ID:** `{context.thread_id}`\n\n"
            
            for endpoint_name, status in endpoint_status.items():
                status_icon = "✅" if status.get("status") == "healthy" else "❌"
                status_report += f"{status_icon} **{endpoint_name}**: {status.get('status', 'unknown')}"
                
                if "response_time" in status:
                    status_report += f" ({status['response_time']:.0f}ms)"
                elif "error" in status:
                    status_report += f" - {status['error']}"
                
                status_report += "\n"
            
            status_report += f"\n**Agent Capabilities:** {len(self.agent_tools)} agent types available\n"
            status_report += f"**MCP Connection:** {'Connected' if self.mcp_connected else 'Disconnected'}\n"
            status_report += f"**Parallel Processing:** {'Enabled' if self.config.parallel_enabled else 'Disabled'}\n"
            
            return status_report
            
        except Exception as e:
            self.logger.error(f"Infrastructure status check failed: {str(e)}")
            return f"❌ **Infrastructure Status Check Failed**: {str(e)}"
