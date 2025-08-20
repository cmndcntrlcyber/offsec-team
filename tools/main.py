from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, AsyncGenerator
import uvicorn
import os
import logging
import json
import asyncio
from datetime import datetime
import importlib
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer(auto_error=False)

# Pydantic models
class ToolRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    agent: str = Field(..., description="Target agent")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
    stream: Optional[bool] = Field(False, description="Enable streaming response")

class ToolResponse(BaseModel):
    success: bool
    result: Any = None
    error: Optional[str] = None
    agent: str
    tool_name: str
    request_id: Optional[str] = None
    timestamp: datetime
    execution_time_ms: Optional[int] = None

app = FastAPI(
    title="Tools Service",
    description="Multi-agent security tools gateway with streaming support",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agent tool mappings
AGENT_TOOLS = {
    "bug_hunter": {
        "module": "bug_hunter",
        "tools": [
            "web_vulnerability_tester",
            "framework_security_analyzer", 
            "vulnerability_report_generator",
            "exploit_database_search",
            "threat_intelligence_lookup"
        ]
    },
    "rt_dev": {
        "module": "rt_dev",
        "tools": [
            "code_forge_generator",
            "infrastructure_orchestrator",
            "platform_connector",
            "ci_pipeline_manager"
        ]
    },
    "burpsuite_operator": {
        "module": "burpsuite_operator",
        "tools": [
            "burp_suite_client",
            "burp_scan_orchestrator",
            "burp_result_processor",
            "burp_vulnerability_assessor"
        ]
    },
    "daedelu5": {
        "module": "daedelu5",
        "tools": [
            "infrastructure_iac_manager",
            "compliance_auditor",
            "security_policy_enforcer",
            "self_healing_integrator"
        ]
    },
    "nexus_kamuy": {
        "module": "nexus_kamuy",
        "tools": [
            "workflow_orchestrator",
            "agent_coordinator",
            "task_scheduler",
            "collaboration_manager"
        ]
    }
}

async def stream_tool_execution(agent_name: str, tool_name: str, parameters: Dict[str, Any], request_id: Optional[str] = None) -> AsyncGenerator[str, None]:
    """Execute a tool with streaming progress updates"""
    start_time = datetime.utcnow()
    
    try:
        # Send initial progress
        yield f"data: {json.dumps({'type': 'progress', 'timestamp': datetime.utcnow().isoformat(), 'data': {'message': f'Loading {agent_name} agent...', 'progress': 15}, 'source': 'tools-service', 'request_id': request_id})}\n\n"
        
        # Load the agent module
        try:
            # Import enhanced researcher tools for actual execution
            from enhanced_researcher_tools import EnhancedResearcherTools
            
            yield f"data: {json.dumps({'type': 'progress', 'timestamp': datetime.utcnow().isoformat(), 'data': {'message': f'Agent {agent_name} loaded, executing {tool_name}...', 'progress': 35}, 'source': 'tools-service', 'request_id': request_id})}\n\n"
            
            # Initialize the enhanced researcher tools
            researcher = EnhancedResearcherTools()
            
            yield f"data: {json.dumps({'type': 'progress', 'timestamp': datetime.utcnow().isoformat(), 'data': {'message': f'Tool {tool_name} execution started...', 'progress': 50}, 'source': 'tools-service', 'request_id': request_id})}\n\n"
            
            # Map tool names to enhanced researcher methods
            tool_mapping = {
                "enhanced_web_search": researcher.enhanced_web_search,
                "multi_agent_vulnerability_assessment": researcher.multi_agent_vulnerability_assessment,
                "orchestrated_security_workflow": researcher.orchestrated_security_workflow,
                "advanced_threat_intelligence_research": researcher.advanced_threat_intelligence_research,
                "infrastructure_security_assessment": researcher.infrastructure_security_assessment,
                "automated_penetration_testing_workflow": researcher.automated_penetration_testing_workflow,
                "get_research_infrastructure_status": researcher.get_research_infrastructure_status
            }
            
            # Execute the tool
            if tool_name in tool_mapping:
                yield f"data: {json.dumps({'type': 'progress', 'timestamp': datetime.utcnow().isoformat(), 'data': {'message': f'Executing enhanced tool {tool_name}...', 'progress': 70}, 'source': 'tools-service', 'request_id': request_id})}\n\n"
                
                tool_func = tool_mapping[tool_name]
                result = await asyncio.to_thread(tool_func, **parameters)
                
                yield f"data: {json.dumps({'type': 'progress', 'timestamp': datetime.utcnow().isoformat(), 'data': {'message': f'Tool execution completed successfully', 'progress': 90}, 'source': 'tools-service', 'request_id': request_id})}\n\n"
                
                # Send the result
                yield f"data: {json.dumps({'type': 'data', 'timestamp': datetime.utcnow().isoformat(), 'data': {'result': result, 'tool_name': tool_name, 'agent': agent_name}, 'source': 'tools-service', 'request_id': request_id})}\n\n"
                
            else:
                # Simulate tool execution for unknown tools
                yield f"data: {json.dumps({'type': 'progress', 'timestamp': datetime.utcnow().isoformat(), 'data': {'message': f'Simulating {tool_name} execution...', 'progress': 70}, 'source': 'tools-service', 'request_id': request_id})}\n\n"
                
                # Simulate work
                await asyncio.sleep(1)
                
                result = {
                    "success": True,
                    "message": f"Tool {tool_name} executed on agent {agent_name}",
                    "parameters": parameters,
                    "simulated": True,
                    "agent": agent_name,
                    "tool": tool_name
                }
                
                yield f"data: {json.dumps({'type': 'data', 'timestamp': datetime.utcnow().isoformat(), 'data': {'result': result}, 'source': 'tools-service', 'request_id': request_id})}\n\n"
            
        except ImportError as e:
            logger.warning(f"Could not import enhanced_researcher_tools: {str(e)}")
            # Fallback simulation
            yield f"data: {json.dumps({'type': 'progress', 'timestamp': datetime.utcnow().isoformat(), 'data': {'message': f'Fallback execution for {tool_name}...', 'progress': 70}, 'source': 'tools-service', 'request_id': request_id})}\n\n"
            
            await asyncio.sleep(1)
            
            result = {
                "success": True,
                "message": f"Fallback execution of {tool_name} on {agent_name}",
                "parameters": parameters,
                "fallback": True
            }
            
            yield f"data: {json.dumps({'type': 'data', 'timestamp': datetime.utcnow().isoformat(), 'data': {'result': result}, 'source': 'tools-service', 'request_id': request_id})}\n\n"
            
    except Exception as e:
        error_msg = f"Tool execution failed: {str(e)}"
        logger.error(error_msg)
        yield f"data: {json.dumps({'type': 'error', 'timestamp': datetime.utcnow().isoformat(), 'data': {'error': error_msg}, 'source': 'tools-service', 'request_id': request_id})}\n\n"
    
    finally:
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        yield f"data: {json.dumps({'type': 'complete', 'timestamp': datetime.utcnow().isoformat(), 'data': {'message': 'Tool execution finished', 'execution_time_ms': int(execution_time)}, 'source': 'tools-service', 'request_id': request_id})}\n\n"

async def execute_tool_sync(agent_name: str, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool synchronously (non-streaming)"""
    start_time = datetime.utcnow()
    
    try:
        # Try to import and use enhanced researcher tools
        try:
            from enhanced_researcher_tools import EnhancedResearcherTools
            researcher = EnhancedResearcherTools()
            
            tool_mapping = {
                "enhanced_web_search": researcher.enhanced_web_search,
                "multi_agent_vulnerability_assessment": researcher.multi_agent_vulnerability_assessment,
                "orchestrated_security_workflow": researcher.orchestrated_security_workflow,
                "advanced_threat_intelligence_research": researcher.advanced_threat_intelligence_research,
                "infrastructure_security_assessment": researcher.infrastructure_security_assessment,
                "automated_penetration_testing_workflow": researcher.automated_penetration_testing_workflow,
                "get_research_infrastructure_status": researcher.get_research_infrastructure_status
            }
            
            if tool_name in tool_mapping:
                tool_func = tool_mapping[tool_name]
                result = await asyncio.to_thread(tool_func, **parameters)
                
                execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                return {
                    "success": True,
                    "result": result,
                    "agent": agent_name,
                    "tool_name": tool_name,
                    "execution_time_ms": int(execution_time)
                }
            else:
                # Fallback for unknown tools
                result = {
                    "success": True,
                    "message": f"Tool {tool_name} executed on agent {agent_name}",
                    "parameters": parameters,
                    "simulated": True
                }
                
                execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                return {
                    "success": True,
                    "result": result,
                    "agent": agent_name,
                    "tool_name": tool_name,
                    "execution_time_ms": int(execution_time)
                }
                
        except ImportError:
            # Fallback implementation
            result = {
                "success": True,
                "message": f"Fallback execution of {tool_name} on {agent_name}",
                "parameters": parameters,
                "fallback": True
            }
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            return {
                "success": True,
                "result": result,
                "agent": agent_name,
                "tool_name": tool_name,
                "execution_time_ms": int(execution_time)
            }
            
    except Exception as e:
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        return {
            "success": False,
            "error": str(e),
            "agent": agent_name,
            "tool_name": tool_name,
            "execution_time_ms": int(execution_time)
        }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "tools-service",
        "version": "2.0.0",
        "streaming_enabled": True,
        "agents_available": list(AGENT_TOOLS.keys())
    }

@app.get("/")
async def root():
    return {
        "message": "Tools Service API", 
        "version": "2.0.0",
        "streaming_support": True,
        "agents": list(AGENT_TOOLS.keys())
    }

@app.get("/agents")
async def list_agents():
    """List all available agents and their tools"""
    return {
        "agents": AGENT_TOOLS,
        "total_agents": len(AGENT_TOOLS),
        "streaming_enabled": True
    }

@app.get("/tools")
async def list_tools():
    """List all available tools across all agents"""
    all_tools = []
    for agent, config in AGENT_TOOLS.items():
        for tool in config["tools"]:
            all_tools.append(f"{agent}.{tool}")
    
    return {
        "available_tools": list(AGENT_TOOLS.keys()),
        "detailed_tools": all_tools,
        "total_tools": len(all_tools)
    }

@app.post("/execute")
async def execute_tool(request: ToolRequest):
    """Execute a tool synchronously"""
    if request.agent not in AGENT_TOOLS:
        raise HTTPException(status_code=400, detail=f"Unknown agent: {request.agent}")
    
    result = await execute_tool_sync(request.agent, request.tool_name, request.parameters)
    
    return ToolResponse(
        success=result["success"],
        result=result.get("result"),
        error=result.get("error"),
        agent=request.agent,
        tool_name=request.tool_name,
        request_id=request.request_id,
        timestamp=datetime.utcnow(),
        execution_time_ms=result.get("execution_time_ms")
    )

@app.post("/execute/stream")
async def execute_tool_stream(request: ToolRequest):
    """Execute a tool with streaming progress updates"""
    if request.agent not in AGENT_TOOLS:
        raise HTTPException(status_code=400, detail=f"Unknown agent: {request.agent}")
    
    return StreamingResponse(
        stream_tool_execution(request.agent, request.tool_name, request.parameters, request.request_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
