"""
RT-Dev Agent Router

FastAPI router for RT-Dev agent tools, including code generation, infrastructure orchestration,
platform connectivity, CI/CD management, and Windows debugging via mcp-windbg integration.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

# Import RT-Dev tools
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from tools.rt_dev.CodeForgeGenerator import CodeForgeGenerator
from tools.rt_dev.InfrastructureOrchestrator import InfrastructureOrchestrator
from tools.rt_dev.PlatformConnector import PlatformConnector
from tools.rt_dev.CIPipelineManager import CIPipelineManager

# Import mcp-windbg integration
from ..integrations.mcp_windbg_client import get_windbg_client

logger = logging.getLogger("RTDevRouter")

# Create router
router = APIRouter()

# Initialize RT-Dev tool instances
code_forge = CodeForgeGenerator()
infra_orchestrator = InfrastructureOrchestrator()
platform_connector = PlatformConnector()
ci_pipeline = CIPipelineManager()

# Pydantic models for RT-Dev specific requests
class CodeGenerationRequest(BaseModel):
    """Request model for code generation"""
    language: str = Field(..., description="Programming language (python, rust, go, docker, terraform)")
    project_type: str = Field(..., description="Type of project (basic, api, cli, etc.)")
    variables: Dict[str, str] = Field(default_factory=dict, description="Template variables to replace")

class CodeInjectionRequest(BaseModel):
    """Request model for code injection"""
    template: str = Field(..., description="Template code with markers")
    custom_blocks: Dict[str, str] = Field(..., description="Custom code blocks to inject")

class CodeValidationRequest(BaseModel):
    """Request model for code validation"""
    code: str = Field(..., description="Code to validate")
    language: str = Field(..., description="Programming language of the code")

class InfrastructureRequest(BaseModel):
    """Request model for infrastructure operations"""
    infrastructure_type: str = Field(..., description="Type of infrastructure (containers, services, networks)")
    action: str = Field(..., description="Action to perform (deploy, scale, monitor, backup)")
    target_environment: str = Field(..., description="Target environment")
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Infrastructure configuration")

class PlatformConnectionRequest(BaseModel):
    """Request model for platform connections"""
    platform_type: str = Field(..., description="Type of platform (cloud, container, database)")
    connection_params: Dict[str, Any] = Field(..., description="Connection parameters")
    action: str = Field(..., description="Action to perform (connect, test, configure)")

class CIPipelineRequest(BaseModel):
    """Request model for CI/CD pipeline operations"""
    pipeline_type: str = Field(..., description="Type of pipeline (build, test, deploy)")
    source_repository: str = Field(..., description="Source code repository")
    target_environment: str = Field(..., description="Target deployment environment")
    pipeline_config: Dict[str, Any] = Field(default_factory=dict, description="Pipeline configuration")

class CrashDumpAnalysisRequest(BaseModel):
    """Request model for crash dump analysis"""
    dump_path: str = Field(..., description="Path to the crash dump file")
    session_id: Optional[str] = Field(None, description="Optional session identifier")

class RemoteDebugRequest(BaseModel):
    """Request model for remote debugging"""
    connection_string: str = Field(..., description="Remote connection string (e.g., tcp:Port=5005,Server=192.168.1.100)")
    session_id: Optional[str] = Field(None, description="Optional session identifier")

class WinDBGCommandRequest(BaseModel):
    """Request model for WinDBG commands"""
    session_id: str = Field(..., description="Active session identifier")
    command: str = Field(..., description="WinDBG command to execute")

class DumpDirectoryRequest(BaseModel):
    """Request model for listing crash dumps"""
    directory: str = Field(..., description="Directory to search for dump files")

# Code Generation Endpoints
@router.post("/code/generate")
async def generate_code(request: CodeGenerationRequest):
    """Generate boilerplate code in various programming languages"""
    try:
        result = code_forge.generate_language_template(
            language=request.language,
            project_type=request.project_type,
            variables=request.variables
        )
        
        return {
            "success": True,
            "generated_code": result,
            "language": request.language,
            "project_type": request.project_type,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Code generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Code generation failed: {str(e)}")

@router.post("/code/inject")
async def inject_code_blocks(request: CodeInjectionRequest):
    """Inject custom code blocks into templates"""
    try:
        result = code_forge.inject_custom_code_blocks(
            template=request.template,
            custom_blocks=request.custom_blocks
        )
        
        return {
            "success": True,
            "modified_template": result,
            "blocks_injected": len(request.custom_blocks),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Code injection failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Code injection failed: {str(e)}")

@router.post("/code/validate")
async def validate_code_syntax(request: CodeValidationRequest):
    """Validate syntax of generated code"""
    try:
        is_valid, error_message = code_forge.validate_code_syntax(
            code=request.code,
            language=request.language
        )
        
        return {
            "success": True,
            "is_valid": is_valid,
            "error_message": error_message if not is_valid else None,
            "language": request.language,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Code validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Code validation failed: {str(e)}")

# Infrastructure Management Endpoints
@router.post("/infrastructure/manage")
async def manage_infrastructure(request: InfrastructureRequest):
    """Manage infrastructure deployment and operations"""
    try:
        result = infra_orchestrator.orchestrate_infrastructure_deployment(
            infrastructure_type=request.infrastructure_type,
            deployment_config=request.configuration,
            target_environment=request.target_environment
        )
        
        return {
            "success": result.get("success", False),
            "result": result,
            "infrastructure_type": request.infrastructure_type,
            "action": request.action,
            "target_environment": request.target_environment,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Infrastructure management failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Infrastructure management failed: {str(e)}")

@router.post("/infrastructure/coordinate")
async def coordinate_deployment(request: InfrastructureRequest):
    """Coordinate multi-service deployment"""
    try:
        result = infra_orchestrator.coordinate_service_deployment(
            services=request.configuration.get("services", []),
            deployment_strategy=request.configuration.get("strategy", "rolling"),
            environment=request.target_environment
        )
        
        return {
            "success": result.get("success", False),
            "result": result,
            "services_deployed": len(request.configuration.get("services", [])),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Deployment coordination failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deployment coordination failed: {str(e)}")

# Platform Connectivity Endpoints
@router.post("/platform/connect")
async def connect_platform(request: PlatformConnectionRequest):
    """Connect to external platforms and services"""
    try:
        result = platform_connector.establish_platform_connection(
            platform_type=request.platform_type,
            connection_config=request.connection_params
        )
        
        return {
            "success": result.get("success", False),
            "connection_result": result,
            "platform_type": request.platform_type,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Platform connection failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Platform connection failed: {str(e)}")

@router.post("/platform/sync")
async def sync_platform_data(request: PlatformConnectionRequest):
    """Synchronize data across multiple platforms"""
    try:
        result = platform_connector.synchronize_cross_platform_data(
            platforms=request.connection_params.get("platforms", []),
            sync_config=request.connection_params.get("sync_config", {})
        )
        
        return {
            "success": result.get("success", False),
            "sync_result": result,
            "platforms_synced": len(request.connection_params.get("platforms", [])),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Platform sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Platform sync failed: {str(e)}")

# CI/CD Pipeline Endpoints
@router.post("/ci/create-pipeline")
async def create_ci_pipeline(request: CIPipelineRequest):
    """Create and configure CI/CD pipeline"""
    try:
        result = ci_pipeline.create_pipeline_configuration(
            pipeline_name=f"{request.pipeline_type}_pipeline",
            source_repo=request.source_repository,
            target_env=request.target_environment,
            pipeline_steps=request.pipeline_config.get("steps", [])
        )
        
        return {
            "success": result.get("success", False),
            "pipeline_result": result,
            "pipeline_type": request.pipeline_type,
            "source_repository": request.source_repository,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"CI pipeline creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CI pipeline creation failed: {str(e)}")

@router.post("/ci/execute-pipeline")
async def execute_ci_pipeline(request: CIPipelineRequest):
    """Execute CI/CD pipeline"""
    try:
        result = ci_pipeline.execute_pipeline(
            pipeline_id=request.pipeline_config.get("pipeline_id"),
            environment=request.target_environment,
            parameters=request.pipeline_config.get("parameters", {})
        )
        
        return {
            "success": result.get("success", False),
            "execution_result": result,
            "pipeline_type": request.pipeline_type,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"CI pipeline execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CI pipeline execution failed: {str(e)}")

# Windows Debugging Endpoints (via mcp-windbg)
@router.post("/debug/crash-dump/open")
async def open_crash_dump(request: CrashDumpAnalysisRequest):
    """Open and analyze a Windows crash dump file"""
    try:
        windbg_client = get_windbg_client()
        result = await windbg_client.open_crash_dump(
            dump_path=request.dump_path,
            session_id=request.session_id
        )
        
        return {
            "success": result.get("success", False),
            "analysis_result": result,
            "dump_path": request.dump_path,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Crash dump analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Crash dump analysis failed: {str(e)}")

@router.post("/debug/remote/connect")
async def connect_remote_debug(request: RemoteDebugRequest):
    """Connect to a remote debugging session"""
    try:
        windbg_client = get_windbg_client()
        result = await windbg_client.open_remote_session(
            connection_string=request.connection_string,
            session_id=request.session_id
        )
        
        return {
            "success": result.get("success", False),
            "connection_result": result,
            "connection_string": request.connection_string,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Remote debug connection failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Remote debug connection failed: {str(e)}")

@router.post("/debug/command/execute")
async def execute_windbg_command(request: WinDBGCommandRequest):
    """Execute a WinDBG command in an active session"""
    try:
        windbg_client = get_windbg_client()
        result = await windbg_client.execute_command(
            session_id=request.session_id,
            command=request.command
        )
        
        return {
            "success": result.get("success", False),
            "command_result": result,
            "session_id": request.session_id,
            "command": request.command,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"WinDBG command execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"WinDBG command execution failed: {str(e)}")

@router.delete("/debug/session/{session_id}")
async def close_debug_session(session_id: str):
    """Close an active debugging session"""
    try:
        windbg_client = get_windbg_client()
        result = windbg_client.close_session(session_id)
        
        return {
            "success": result.get("success", False),
            "close_result": result,
            "session_id": session_id,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Debug session closure failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Debug session closure failed: {str(e)}")

@router.post("/debug/dumps/list")
async def list_crash_dumps(request: DumpDirectoryRequest):
    """List Windows crash dump files in a directory"""
    try:
        windbg_client = get_windbg_client()
        result = windbg_client.list_crash_dumps(request.directory)
        
        return {
            "success": result.get("success", False),
            "dumps_list": result,
            "directory": request.directory,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Crash dump listing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Crash dump listing failed: {str(e)}")

@router.get("/debug/sessions")
async def get_debug_sessions():
    """Get information about active debugging sessions"""
    try:
        windbg_client = get_windbg_client()
        result = windbg_client.get_active_sessions()
        
        return {
            "success": True,
            "sessions_info": result,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Debug sessions query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Debug sessions query failed: {str(e)}")

# Status and Information Endpoints
@router.get("/status")
async def get_rt_dev_status():
    """Get RT-Dev agent status and capabilities"""
    try:
        windbg_client = get_windbg_client()
        debug_info = windbg_client.get_active_sessions()
        
        return {
            "agent": "RT-Dev",
            "status": "active",
            "capabilities": {
                "code_generation": {
                    "languages": ["python", "rust", "go", "docker", "terraform"],
                    "project_types": ["basic", "api", "cli", "web", "microservice"]
                },
                "infrastructure": {
                    "deployment": True,
                    "orchestration": True,
                    "monitoring": True
                },
                "platform_connectivity": {
                    "cloud_platforms": True,
                    "container_platforms": True,
                    "database_connections": True
                },
                "ci_cd": {
                    "pipeline_creation": True,
                    "pipeline_execution": True,
                    "deployment_automation": True
                },
                "debugging": {
                    "crash_dump_analysis": debug_info.get("cdb_available", False),
                    "remote_debugging": debug_info.get("cdb_available", False),
                    "active_sessions": debug_info.get("session_count", 0)
                }
            },
            "tools_loaded": [
                "CodeForgeGenerator",
                "InfrastructureOrchestrator", 
                "PlatformConnector",
                "CIPipelineManager",
                "MCPWinDBGClient"
            ],
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Status query failed: {str(e)}")
        return {
            "agent": "RT-Dev",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow()
        }

@router.get("/tools")
async def list_rt_dev_tools():
    """List all available RT-Dev tools and endpoints"""
    return {
        "agent": "RT-Dev",
        "tools": {
            "code_generation": {
                "generate_code": "POST /code/generate",
                "inject_code_blocks": "POST /code/inject", 
                "validate_code_syntax": "POST /code/validate"
            },
            "infrastructure": {
                "manage_infrastructure": "POST /infrastructure/manage",
                "coordinate_deployment": "POST /infrastructure/coordinate"
            },
            "platform_connectivity": {
                "connect_platform": "POST /platform/connect",
                "sync_platform_data": "POST /platform/sync"
            },
            "ci_cd": {
                "create_ci_pipeline": "POST /ci/create-pipeline",
                "execute_ci_pipeline": "POST /ci/execute-pipeline"
            },
            "debugging": {
                "open_crash_dump": "POST /debug/crash-dump/open",
                "connect_remote_debug": "POST /debug/remote/connect",
                "execute_windbg_command": "POST /debug/command/execute",
                "close_debug_session": "DELETE /debug/session/{session_id}",
                "list_crash_dumps": "POST /debug/dumps/list",
                "get_debug_sessions": "GET /debug/sessions"
            },
            "status": {
                "get_rt_dev_status": "GET /status",
                "list_rt_dev_tools": "GET /tools"
            }
        },
        "total_endpoints": 16,
        "timestamp": datetime.utcnow()
    }
