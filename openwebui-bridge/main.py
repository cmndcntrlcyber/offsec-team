"""
Agent Tool Bridge API

FastAPI backend that bridges Open WebUI tool calls to the existing cybersecurity agent ecosystem.
Provides standardized REST endpoints for Open WebUI integration at https://chat.attck.nexus/
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Add the parent directory to sys.path to import our tools
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tools.rt_dev.CodeForgeGenerator import CodeForgeGenerator
from tools.rt_dev.InfrastructureOrchestrator import InfrastructureOrchestrator
from tools.rt_dev.PlatformConnector import PlatformConnector
from tools.rt_dev.CIPipelineManager import CIPipelineManager

from tools.bug_hunter.WebVulnerabilityTester import WebVulnerabilityTester
from tools.bug_hunter.FrameworkSecurityAnalyzer import FrameworkSecurityAnalyzer
from tools.bug_hunter.VulnerabilityReportGenerator import VulnerabilityReportGenerator

from tools.burpsuite_operator.BurpSuiteAPIClient import BurpSuiteAPIClient
from tools.burpsuite_operator.BurpScanOrchestrator import BurpScanOrchestrator
from tools.burpsuite_operator.BurpResultProcessor import BurpResultProcessor
from tools.burpsuite_operator.BurpVulnerabilityAssessor import BurpVulnerabilityAssessor

from tools.daedelu5.InfrastructureAsCodeManager import InfrastructureAsCodeManager
from tools.daedelu5.ComplianceAuditor import ComplianceAuditor
from tools.daedelu5.SecurityPolicyEnforcer import SecurityPolicyEnforcer
from tools.daedelu5.SelfHealingIntegrator import SelfHealingIntegrator

from tools.nexus_kamuy.WorkflowOrchestrator import WorkflowOrchestrator
from tools.nexus_kamuy.AgentCoordinator import AgentCoordinator
from tools.nexus_kamuy.TaskScheduler import TaskScheduler
from tools.nexus_kamuy.CollaborationManager import CollaborationManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AgentToolBridge")

# Global agent instances
agent_instances = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - initialize and cleanup resources"""
    # Initialize agent instances
    logger.info("Initializing agent instances...")
    
    try:
        agent_instances.update({
            # RT-Dev Tools
            "code_forge_generator": CodeForgeGenerator(),
            "infrastructure_orchestrator": InfrastructureOrchestrator(),
            "platform_connector": PlatformConnector(),
            "ci_pipeline_manager": CIPipelineManager(),
            
            # Bug Hunter Tools
            "web_vulnerability_tester": WebVulnerabilityTester(),
            "framework_security_analyzer": FrameworkSecurityAnalyzer(),
            "vulnerability_report_generator": VulnerabilityReportGenerator(),
            
            # BurpSuite Operator Tools
            "burp_suite_client": BurpSuiteAPIClient(),
            "burp_scan_orchestrator": BurpScanOrchestrator(),
            "burp_result_processor": BurpResultProcessor(),
            "burp_vulnerability_assessor": BurpVulnerabilityAssessor(),
            
            # Daedelu5 Tools
            "infrastructure_iac_manager": InfrastructureAsCodeManager(),
            "compliance_auditor": ComplianceAuditor(),
            "security_policy_enforcer": SecurityPolicyEnforcer(),
            "self_healing_integrator": SelfHealingIntegrator(),
            
            # Nexus-Kamuy Tools
            "workflow_orchestrator": WorkflowOrchestrator(),
            "agent_coordinator": AgentCoordinator(),
            "task_scheduler": TaskScheduler(),
            "collaboration_manager": CollaborationManager()
        })
        
        logger.info(f"Successfully initialized {len(agent_instances)} agent instances")
        
    except Exception as e:
        logger.error(f"Failed to initialize agent instances: {str(e)}")
        raise
    
    yield
    
    # Cleanup
    logger.info("Cleaning up agent instances...")
    agent_instances.clear()

# Create FastAPI app
app = FastAPI(
    title="Agent Tool Bridge API",
    description="Bridge API for Open WebUI integration with cybersecurity agent tools",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for Open WebUI at https://chat.attck.nexus/
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://chat.attck.nexus",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Pydantic models for requests/responses
class ToolRequest(BaseModel):
    """Base model for tool requests"""
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    agent: str = Field(..., description="Target agent (rt_dev, bug_hunter, burpsuite_operator, daedelu5, nexus_kamuy)")
    request_id: Optional[str] = Field(None, description="Optional request ID for tracking")

class ToolResponse(BaseModel):
    """Base model for tool responses"""
    success: bool
    result: Any = None
    error: Optional[str] = None
    agent: str
    tool_name: str
    request_id: Optional[str] = None
    timestamp: datetime
    execution_time_ms: Optional[int] = None

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: datetime
    version: str
    agents_loaded: int
    open_webui_endpoint: str

# Authentication dependency
async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Verify API token (placeholder for now)"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # TODO: Implement proper token validation
    # For now, accept any bearer token
    return credentials.credentials

# Utility functions
def get_agent_instance(agent_name: str):
    """Get agent instance by name"""
    agent_map = {
        "rt_dev": [
            "code_forge_generator", 
            "infrastructure_orchestrator", 
            "platform_connector",
            "ci_pipeline_manager"
        ],
        "bug_hunter": [
            "web_vulnerability_tester", 
            "framework_security_analyzer", 
            "vulnerability_report_generator"
        ],
        "burpsuite_operator": [
            "burp_suite_client", 
            "burp_scan_orchestrator", 
            "burp_result_processor",
            "burp_vulnerability_assessor"
        ],
        "daedelu5": [
            "infrastructure_iac_manager", 
            "compliance_auditor", 
            "security_policy_enforcer",
            "self_healing_integrator"
        ],
        "nexus_kamuy": [
            "workflow_orchestrator", 
            "agent_coordinator", 
            "task_scheduler",
            "collaboration_manager"
        ]
    }
    
    return agent_map.get(agent_name, [])

def execute_agent_tool(agent_name: str, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool on the specified agent"""
    start_time = datetime.utcnow()
    
    try:
        # Get relevant agent instances
        relevant_instances = get_agent_instance(agent_name)
        
        if not relevant_instances:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        # Find the appropriate instance and method
        for instance_name in relevant_instances:
            instance = agent_instances.get(instance_name)
            if not instance:
                continue
            
            # Check if the instance has the requested method
            if hasattr(instance, tool_name):
                method = getattr(instance, tool_name)
                
                # Execute the method with parameters
                if callable(method):
                    result = method(**parameters)
                    
                    execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                    
                    return {
                        "success": True,
                        "result": result,
                        "execution_time_ms": int(execution_time)
                    }
        
        # Tool not found in any instance
        available_tools = []
        for instance_name in relevant_instances:
            instance = agent_instances.get(instance_name)
            if instance:
                # Get public methods (tools)
                methods = [method for method in dir(instance) 
                          if not method.startswith('_') and callable(getattr(instance, method))]
                available_tools.extend(methods)
        
        raise ValueError(f"Tool '{tool_name}' not found in agent '{agent_name}'. Available tools: {available_tools}")
        
    except Exception as e:
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            "success": False,
            "error": str(e),
            "execution_time_ms": int(execution_time)
        }

# Routes
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        agents_loaded=len(agent_instances),
        open_webui_endpoint="https://chat.attck.nexus/"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        agents_loaded=len(agent_instances),
        open_webui_endpoint="https://chat.attck.nexus/"
    )

@app.get("/agents")
async def list_agents():
    """List available agents and their tools"""
    agents_info = {}
    
    for agent_name in ["rt_dev", "bug_hunter", "burpsuite_operator", "daedelu5", "nexus_kamuy"]:
        instance_names = get_agent_instance(agent_name)
        tools = []
        
        for instance_name in instance_names:
            instance = agent_instances.get(instance_name)
            if instance:
                # Get public methods (tools)
                methods = [method for method in dir(instance) 
                          if not method.startswith('_') and callable(getattr(instance, method))]
                tools.extend([f"{instance_name}.{method}" for method in methods])
        
        agents_info[agent_name] = {
            "instances": instance_names,
            "available_tools": tools,
            "loaded": len([name for name in instance_names if name in agent_instances])
        }
    
    return {
        "agents": agents_info,
        "total_agents": len(agents_info),
        "total_instances": len(agent_instances),
        "open_webui_endpoint": "https://chat.attck.nexus/"
    }

@app.post("/execute", response_model=ToolResponse)
async def execute_tool(
    request: ToolRequest,
    token: str = Depends(verify_token)
):
    """Execute a tool on the specified agent"""
    start_time = datetime.utcnow()
    
    try:
        # Execute the tool
        result = execute_agent_tool(request.agent, request.tool_name, request.parameters)
        
        return ToolResponse(
            success=result["success"],
            result=result.get("result"),
            error=result.get("error"),
            agent=request.agent,
            tool_name=request.tool_name,
            request_id=request.request_id,
            timestamp=start_time,
            execution_time_ms=result.get("execution_time_ms")
        )
        
    except Exception as e:
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return ToolResponse(
            success=False,
            error=str(e),
            agent=request.agent,
            tool_name=request.tool_name,
            request_id=request.request_id,
            timestamp=start_time,
            execution_time_ms=int(execution_time)
        )

# Agent-specific routes
try:
    from .routers import rt_dev_router, bug_hunter_router, burpsuite_router, daedelu5_router, nexus_kamuy_router
    
    # Include agent-specific routers
    app.include_router(rt_dev_router.router, prefix="/agents/rt_dev", tags=["RT-Dev"])
    app.include_router(bug_hunter_router.router, prefix="/agents/bug_hunter", tags=["Bug Hunter"])  
    app.include_router(burpsuite_router.router, prefix="/agents/burpsuite_operator", tags=["BurpSuite Operator"])
    app.include_router(daedelu5_router.router, prefix="/agents/daedelu5", tags=["Daedelu5"])
    app.include_router(nexus_kamuy_router.router, prefix="/agents/nexus_kamuy", tags=["Nexus-Kamuy"])
    
    logger.info("Successfully loaded all agent routers")
    
except ImportError as e:
    logger.warning(f"Some agent routers could not be imported: {str(e)}")
    # Continue without the problematic routers
    pass

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
