"""
Agent Tool Bridge API

FastAPI backend that bridges Open WebUI tool calls to the existing cybersecurity agent ecosystem.
Provides standardized REST endpoints for Open WebUI integration at https://chat.attck.nexus/
"""

import os
import sys
import logging
import requests
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Request, Security, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.websockets import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
import uvicorn
import json
from typing import AsyncGenerator

# Tool imports will be handled via API calls to tools service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AgentToolBridge")

# Configuration
TOOLS_ENDPOINT_URL = os.getenv('TOOLS_ENDPOINT_URL', 'https://tools.attck.nexus')

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - initialize and cleanup resources"""
    logger.info("OpenWebUI Bridge service starting...")
    yield
    logger.info("OpenWebUI Bridge service shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Agent Tool Bridge API",
    description="Bridge API for Open WebUI integration with cybersecurity agent tools",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for Open WebUI at https://chat.attck.nexus/ and researcher integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://chat.attck.nexus",
        "https://researcher.c3s.nexus",
        "https://tools.attck.nexus",
        "http://192.168.1.81",
        "http://192.168.1.81:3000",
        "http://192.168.1.81:8080",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*", "X-Chat-Thread-ID", "X-User-ID", "X-Session-ID", "X-Origin-Endpoint"],
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

class ResearcherRequest(BaseModel):
    """Request model for researcher routing"""
    request_type: str = Field(..., description="Type of researcher request")
    agent: str = Field(..., description="Target agent")
    tool_name: str = Field(..., description="Tool to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    context: Dict[str, Any] = Field(..., description="Thread context information")
    routing_chain: List[str] = Field(default_factory=list, description="Routing chain for request")

class ResearcherResponse(BaseModel):
    """Response model for researcher routing"""
    success: bool
    result: Any = None
    error: Optional[str] = None
    context: Dict[str, Any]
    return_to: str
    execution_time_ms: Optional[int] = None
    insights: Optional[str] = None
    recommendations: Optional[str] = None

class ContextualToolRequest(BaseModel):
    """Enhanced tool request with context"""
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    agent: str = Field(..., description="Target agent")
    request_id: Optional[str] = Field(None, description="Optional request ID for tracking")
    context: Optional[Dict[str, Any]] = Field(None, description="Thread context")
    route_via_researcher: bool = Field(False, description="Whether to route via researcher")

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

async def execute_agent_tool(agent_name: str, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool on the specified agent via tools service API"""
    start_time = datetime.utcnow()
    
    try:
        # Forward to tools service
        tools_service_url = os.getenv('TOOLS_SERVICE_URL', 'http://tools-service:8001')
        
        headers = {
            "Authorization": f"Bearer {os.getenv('TOOLS_SERVICE_TOKEN', '')}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "tool_name": tool_name,
            "parameters": parameters,
            "agent": agent_name
        }
        
        response = await asyncio.to_thread(
            requests.post,
            f"{tools_service_url}/execute",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "result": result,
                "execution_time_ms": int(execution_time)
            }
        else:
            return {
                "success": False,
                "error": f"Tools service error: {response.status_code}",
                "execution_time_ms": int(execution_time)
            }
            
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
        agents_loaded=5,  # 5 agent types available
        open_webui_endpoint=TOOLS_ENDPOINT_URL
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        agents_loaded=5,  # 5 agent types available
        open_webui_endpoint=TOOLS_ENDPOINT_URL
    )

@app.get("/agents")
async def list_agents():
    """List available agents and their tools"""
    try:
        # Forward to tools service to get actual agent info
        tools_service_url = os.getenv('TOOLS_SERVICE_URL', 'http://tools-service:8001')
        
        response = await asyncio.to_thread(
            requests.get,
            f"{tools_service_url}/agents",
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            # Fallback response
            return {
                "agents": {
                    "rt_dev": {"status": "available", "tools": ["code_generation", "infrastructure_management"]},
                    "bug_hunter": {"status": "available", "tools": ["vulnerability_scanning", "security_analysis"]},
                    "burpsuite_operator": {"status": "available", "tools": ["web_scanning", "api_testing"]},
                    "daedelu5": {"status": "available", "tools": ["iac_management", "compliance_audit"]},
                    "nexus_kamuy": {"status": "available", "tools": ["workflow_orchestration", "task_coordination"]}
                },
                "total_agents": 5,
                "open_webui_endpoint": TOOLS_ENDPOINT_URL
            }
            
    except Exception as e:
        logger.error(f"Failed to get agents list: {str(e)}")
        # Return basic agent info
        return {
            "agents": {
                "rt_dev": {"status": "available", "tools": ["code_generation", "infrastructure_management"]},
                "bug_hunter": {"status": "available", "tools": ["vulnerability_scanning", "security_analysis"]},
                "burpsuite_operator": {"status": "available", "tools": ["web_scanning", "api_testing"]},
                "daedelu5": {"status": "available", "tools": ["iac_management", "compliance_audit"]},
                "nexus_kamuy": {"status": "available", "tools": ["workflow_orchestration", "task_coordination"]}
            },
            "total_agents": 5,
            "open_webui_endpoint": TOOLS_ENDPOINT_URL
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
        result = await execute_agent_tool(request.agent, request.tool_name, request.parameters)
        
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

# Streaming utility functions
async def stream_agent_tool_execution(agent_name: str, tool_name: str, parameters: Dict[str, Any], request_id: Optional[str] = None) -> AsyncGenerator[str, None]:
    """Execute a tool with streaming progress updates"""
    start_time = datetime.utcnow()
    
    try:
        # Send initial progress
        yield f"data: {json.dumps({'type': 'progress', 'timestamp': datetime.utcnow().isoformat(), 'data': {'message': f'Initializing {agent_name}.{tool_name}...', 'progress': 10}, 'source': 'fastapi-backend', 'request_id': request_id})}\n\n"
        
        # Forward to tools service for streaming execution
        tools_service_url = os.getenv('TOOLS_SERVICE_URL', 'http://tools-service:8001')
        
        headers = {
            "Authorization": f"Bearer {os.getenv('TOOLS_SERVICE_TOKEN', '')}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        
        payload = {
            "tool_name": tool_name,
            "parameters": parameters,
            "agent": agent_name,
            "request_id": request_id,
            "stream": True
        }
        
        yield f"data: {json.dumps({'type': 'progress', 'timestamp': datetime.utcnow().isoformat(), 'data': {'message': f'Connecting to tools service...', 'progress': 25}, 'source': 'fastapi-backend', 'request_id': request_id})}\n\n"
        
        # Make streaming request to tools service
        response = await asyncio.to_thread(
            requests.post,
            f"{tools_service_url}/execute/stream",
            headers=headers,
            json=payload,
            timeout=60,
            stream=True
        )
        
        if response.status_code == 200:
            yield f"data: {json.dumps({'type': 'progress', 'timestamp': datetime.utcnow().isoformat(), 'data': {'message': f'Tool execution started...', 'progress': 50}, 'source': 'fastapi-backend', 'request_id': request_id})}\n\n"
            
            # Stream response from tools service
            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith('data: '):
                    # Forward the streaming data
                    yield f"{line}\n\n"
                    
        else:
            # Handle error response
            error_msg = f"Tools service error: {response.status_code}"
            yield f"data: {json.dumps({'type': 'error', 'timestamp': datetime.utcnow().isoformat(), 'data': {'error': error_msg}, 'source': 'fastapi-backend', 'request_id': request_id})}\n\n"
            
    except Exception as e:
        error_msg = f"Streaming execution failed: {str(e)}"
        logger.error(error_msg)
        yield f"data: {json.dumps({'type': 'error', 'timestamp': datetime.utcnow().isoformat(), 'data': {'error': error_msg}, 'source': 'fastapi-backend', 'request_id': request_id})}\n\n"
    
    finally:
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        yield f"data: {json.dumps({'type': 'complete', 'timestamp': datetime.utcnow().isoformat(), 'data': {'message': 'Tool execution completed', 'execution_time_ms': int(execution_time)}, 'source': 'fastapi-backend', 'request_id': request_id})}\n\n"

@app.post("/execute/stream")
async def execute_tool_stream(
    request: ToolRequest,
    token: str = Depends(verify_token)
):
    """Execute a tool with streaming progress updates"""
    return StreamingResponse(
        stream_agent_tool_execution(request.agent, request.tool_name, request.parameters, request.request_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

@app.post("/execute/contextual", response_model=ToolResponse)
async def execute_contextual_tool(
    request: ContextualToolRequest,
    token: str = Depends(verify_token),
    x_chat_thread_id: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None),
    x_session_id: Optional[str] = Header(None),
    x_origin_endpoint: Optional[str] = Header(None)
):
    """Execute a tool with contextual routing support"""
    start_time = datetime.utcnow()
    
    try:
        # Build context from headers if not provided in request
        if not request.context:
            request.context = {
                "thread_id": x_chat_thread_id,
                "user_id": x_user_id,
                "session_id": x_session_id,
                "origin_endpoint": x_origin_endpoint or "https://chat.attck.nexus",
                "timestamp": int(start_time.timestamp())
            }
        
        # Route via researcher if requested
        if request.route_via_researcher:
            logger.info(f"Routing {request.agent}.{request.tool_name} via researcher for thread {request.context.get('thread_id')}")
            result = await route_to_researcher(request, request.context)
        else:
            logger.info(f"Direct execution of {request.agent}.{request.tool_name}")
            result = await execute_agent_tool(request.agent, request.tool_name, request.parameters)
        
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
        logger.error(f"Contextual execution failed: {str(e)}")
        
        return ToolResponse(
            success=False,
            error=str(e),
            agent=request.agent,
            tool_name=request.tool_name,
            request_id=request.request_id,
            timestamp=start_time,
            execution_time_ms=int(execution_time)
        )

@app.post("/execute/contextual/stream")
async def execute_contextual_tool_stream(
    request: ContextualToolRequest,
    token: str = Depends(verify_token),
    x_chat_thread_id: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None),
    x_session_id: Optional[str] = Header(None),
    x_origin_endpoint: Optional[str] = Header(None)
):
    """Execute a contextual tool with streaming progress updates"""
    # Build context from headers if not provided in request
    if not request.context:
        request.context = {
            "thread_id": x_chat_thread_id,
            "user_id": x_user_id,
            "session_id": x_session_id,
            "origin_endpoint": x_origin_endpoint or "https://chat.attck.nexus",
            "timestamp": int(datetime.utcnow().timestamp())
        }
    
    return StreamingResponse(
        stream_agent_tool_execution(request.agent, request.tool_name, request.parameters, request.request_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

@app.get(
    "/openapi.json",
    tags=["Core"],
    summary="OpenAPI Specification", 
    description="Get the OpenAPI 3.0 specification for OpenWebUI tool integration",
    include_in_schema=False
)
async def get_openapi_json():
    """
    Serve OpenAPI specification for OpenWebUI integration
    
    This endpoint provides the complete OpenAPI 3.0 specification that OpenWebUI
    can use to discover and integrate with all available cybersecurity tools.
    """
    import os
    openapi_file = os.path.join(os.path.dirname(__file__), "openapi.json")
    if os.path.exists(openapi_file):
        return FileResponse(
            openapi_file,
            media_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )
    else:
        # Fallback to FastAPI's auto-generated OpenAPI
        return app.openapi()

@app.post("/researcher/callback")
async def researcher_callback(
    request: ResearcherResponse,
    token: str = Depends(verify_token)
):
    """Handle callbacks from researcher.c3s.nexus with analysis results"""
    try:
        logger.info(f"Received researcher callback for thread {request.context.get('thread_id')}")
        
        # Process the researcher response and route back to chat
        return_url = request.return_to
        context = request.context
        
        # Format the response for the chat interface
        formatted_response = {
            "success": request.success,
            "result": {
                "insights": request.insights,
                "recommendations": request.recommendations,
                "tool_results": request.result,
                "context": context,
                "routing_chain": "chat.attck.nexus → tools.attck.nexus → researcher.c3s.nexus → chat.attck.nexus"
            },
            "error": request.error,
            "execution_time_ms": request.execution_time_ms,
            "timestamp": datetime.utcnow()
        }
        
        # Log successful callback processing
        logger.info(f"Processed researcher callback for thread {context.get('thread_id')}, routing back to {return_url}")
        
        return {
            "status": "callback_processed",
            "thread_id": context.get("thread_id"),
            "return_url": return_url,
            "response": formatted_response
        }
        
    except Exception as e:
        logger.error(f"Researcher callback processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Callback processing failed: {str(e)}")

async def route_to_researcher(request: ContextualToolRequest, context: Dict[str, Any]) -> Dict[str, Any]:
    """Route request to researcher.c3s.nexus for complex analysis"""
    try:
        researcher_url = "https://researcher.c3s.nexus/analyze"
        
        headers = {
            "Authorization": f"Bearer {os.getenv('RESEARCHER_API_TOKEN', 'sk-755ea70d07874c7d9e0b46d3966eb145')}",
            "Content-Type": "application/json",
            "X-Chat-Thread-ID": context.get("thread_id", ""),
            "X-User-ID": context.get("user_id", ""),
            "X-Session-ID": context.get("session_id", ""),
            "X-Origin-Endpoint": context.get("origin_endpoint", "https://chat.attck.nexus")
        }
        
        payload = {
            "request_type": "tool_execution",
            "agent": request.agent,
            "tool_name": request.tool_name,
            "parameters": request.parameters,
            "context": context,
            "routing_chain": [
                "https://chat.attck.nexus",
                "https://tools.attck.nexus",
                "https://researcher.c3s.nexus"
            ],
            "callback_url": "https://tools.attck.nexus/researcher/callback"
        }
        
        logger.info(f"Sending request to researcher: {request.agent}.{request.tool_name}")
        
        # Use asyncio for async HTTP request
        response = await asyncio.to_thread(
            requests.post,
            researcher_url,
            headers=headers,
            json=payload,
            timeout=45
        )
        
        if response.status_code == 200:
            result = response.json()
            # Ensure the response includes routing back to chat
            result["context"] = context
            result["return_to"] = context.get("origin_endpoint", "https://chat.attck.nexus")
            return result
        else:
            logger.warning(f"Researcher API error: {response.status_code} - {response.text}")
            # Fallback to direct tool execution
            return await execute_agent_tool(request.agent, request.tool_name, request.parameters)
            
    except Exception as e:
        logger.error(f"Researcher routing error: {str(e)}")
        # Fallback to direct tool execution
        return await execute_agent_tool(request.agent, request.tool_name, request.parameters)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_contexts: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str, context: Dict[str, Any]):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.session_contexts[session_id] = context
        logger.info(f"WebSocket connected: {session_id}")
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.session_contexts:
            del self.session_contexts[session_id]
        logger.info(f"WebSocket disconnected: {session_id}")
    
    async def send_personal_message(self, message: Dict[str, Any], session_id: str):
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_text(json.dumps(message))
    
    async def broadcast_to_session(self, message: Dict[str, Any], session_id: str):
        await self.send_personal_message(message, session_id)

manager = ConnectionManager()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time communication"""
    try:
        # Accept the connection with context
        context = {
            "session_id": session_id,
            "connected_at": datetime.utcnow().isoformat(),
            "user_id": "websocket_user",  # Could be extracted from query params
            "thread_id": f"ws_{session_id}"
        }
        
        await manager.connect(websocket, session_id, context)
        
        # Send welcome message
        await manager.send_personal_message({
            "type": "connection_established",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "capabilities": ["streaming", "real_time_updates", "multi_agent_coordination"]
        }, session_id)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "tool_execution":
                # Handle tool execution via WebSocket
                await handle_websocket_tool_execution(message_data, session_id)
            elif message_data.get("type") == "ping":
                # Handle ping/pong for keepalive
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }, session_id)
            else:
                # Echo other messages
                await manager.send_personal_message({
                    "type": "echo",
                    "original_message": message_data,
                    "timestamp": datetime.utcnow().isoformat()
                }, session_id)
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        logger.info(f"WebSocket client {session_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for {session_id}: {str(e)}")
        manager.disconnect(session_id)

async def handle_websocket_tool_execution(message_data: Dict[str, Any], session_id: str):
    """Handle tool execution via WebSocket with real-time updates"""
    try:
        tool_name = message_data.get("tool_name")
        agent = message_data.get("agent")
        parameters = message_data.get("parameters", {})
        request_id = message_data.get("request_id")
        
        # Send acknowledgment
        await manager.send_personal_message({
            "type": "tool_execution_started",
            "tool_name": tool_name,
            "agent": agent,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }, session_id)
        
        # Execute tool with streaming updates via WebSocket
        async for chunk in stream_agent_tool_execution(agent, tool_name, parameters, request_id):
            if chunk.startswith("data: "):
                chunk_data = json.loads(chunk[6:])
                await manager.send_personal_message({
                    "type": "tool_stream_chunk",
                    "chunk_data": chunk_data,
                    "timestamp": datetime.utcnow().isoformat()
                }, session_id)
        
        # Send completion notification
        await manager.send_personal_message({
            "type": "tool_execution_completed",
            "tool_name": tool_name,
            "agent": agent,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }, session_id)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "tool_execution_error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, session_id)

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
        port=8001,
        reload=True,
        log_level="info"
    )
