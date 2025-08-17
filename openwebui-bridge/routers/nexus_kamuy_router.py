"""
Nexus-Kamuy Agent Router

FastAPI router for Nexus-Kamuy agent tools, including workflow orchestration,
agent coordination, task scheduling, and collaboration management.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Import Nexus-Kamuy tools
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from tools.nexus_kamuy.WorkflowOrchestrator import WorkflowOrchestrator
from tools.nexus_kamuy.AgentCoordinator import AgentCoordinator
from tools.nexus_kamuy.TaskScheduler import TaskScheduler
from tools.nexus_kamuy.CollaborationManager import CollaborationManager

logger = logging.getLogger("NexusKamuyRouter")

# Create router
router = APIRouter()

# Initialize Nexus-Kamuy tool instances
workflow_orchestrator = WorkflowOrchestrator()
agent_coordinator = AgentCoordinator()
task_scheduler = TaskScheduler()
collaboration_manager = CollaborationManager()

# Pydantic models for Nexus-Kamuy specific requests
class WorkflowRequest(BaseModel):
    """Request model for workflow operations"""
    workflow_name: str = Field(..., description="Name of the workflow")
    workflow_type: str = Field(..., description="Type of workflow")
    target: str = Field(..., description="Workflow target")
    objectives: List[str] = Field(..., description="Workflow objectives")
    agent_requirements: Dict[str, Any] = Field(..., description="Agent capability requirements")

class WorkflowExecutionRequest(BaseModel):
    """Request model for workflow execution"""
    workflow_id: str = Field(..., description="Workflow ID to execute")

class AgentHandoffRequest(BaseModel):
    """Request model for agent handoffs"""
    workflow_id: str = Field(..., description="Workflow ID")
    current_step: str = Field(..., description="Current step ID")
    next_step: str = Field(..., description="Next step ID")

class WorkflowStateRequest(BaseModel):
    """Request model for workflow state management"""
    workflow_id: str = Field(..., description="Workflow ID")
    action: str = Field(..., description="State management action (pause, resume, cancel, retry)")

class TaskScheduleRequest(BaseModel):
    """Request model for task scheduling"""
    task_name: str = Field(..., description="Name of the task")
    schedule_config: Dict[str, Any] = Field(..., description="Scheduling configuration")
    agent_assignments: List[str] = Field(..., description="Assigned agents")

class CollaborationRequest(BaseModel):
    """Request model for collaboration management"""
    collaboration_type: str = Field(..., description="Type of collaboration")
    participating_agents: List[str] = Field(..., description="Participating agents")
    shared_resources: Dict[str, Any] = Field(..., description="Shared resources")

@router.post("/workflow/create")
async def create_multi_agent_workflow(request: WorkflowRequest):
    """Create a comprehensive multi-agent workflow"""
    try:
        result = workflow_orchestrator.create_multi_agent_workflow(
            workflow_name=request.workflow_name,
            workflow_type=request.workflow_type,
            target=request.target,
            objectives=request.objectives,
            agent_requirements=request.agent_requirements
        )
        
        return {
            "success": result.get("success", False),
            "workflow_result": result,
            "workflow_name": request.workflow_name,
            "workflow_type": request.workflow_type,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Multi-agent workflow creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Multi-agent workflow creation failed: {str(e)}")

@router.post("/workflow/execute")
async def execute_workflow_pipeline(request: WorkflowExecutionRequest):
    """Execute a complete workflow pipeline with all steps"""
    try:
        result = workflow_orchestrator.execute_workflow_pipeline(
            workflow_id=request.workflow_id
        )
        
        return {
            "success": result.get("success", False),
            "execution_result": result,
            "workflow_id": request.workflow_id,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Workflow pipeline execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow pipeline execution failed: {str(e)}")

@router.post("/workflow/handoff")
async def coordinate_agent_handoffs(request: AgentHandoffRequest):
    """Coordinate handoffs between different AI agents"""
    try:
        result = workflow_orchestrator.coordinate_agent_handoffs(
            workflow_id=request.workflow_id,
            current_step=request.current_step,
            next_step=request.next_step
        )
        
        return {
            "success": result.get("success", False),
            "handoff_result": result,
            "workflow_id": request.workflow_id,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Agent handoff coordination failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent handoff coordination failed: {str(e)}")

@router.post("/workflow/manage-state")
async def manage_workflow_state(request: WorkflowStateRequest):
    """Manage workflow execution state"""
    try:
        result = workflow_orchestrator.manage_workflow_state(
            workflow_id=request.workflow_id,
            action=request.action
        )
        
        return {
            "success": result.get("success", False),
            "state_result": result,
            "workflow_id": request.workflow_id,
            "action": request.action,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Workflow state management failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow state management failed: {str(e)}")

@router.get("/workflow/{workflow_id}/progress")
async def track_workflow_progress(workflow_id: str):
    """Track comprehensive workflow progress and metrics"""
    try:
        result = workflow_orchestrator.track_workflow_progress(
            workflow_id=workflow_id
        )
        
        return {
            "success": result.get("success", False),
            "progress_result": result,
            "workflow_id": workflow_id,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Workflow progress tracking failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow progress tracking failed: {str(e)}")

@router.post("/task/schedule")
async def schedule_task(request: TaskScheduleRequest):
    """Schedule tasks for multi-agent execution"""
    try:
        result = task_scheduler.schedule_multi_agent_task(
            task_name=request.task_name,
            schedule_config=request.schedule_config,
            agent_assignments=request.agent_assignments
        )
        
        return {
            "success": result.get("success", False),
            "schedule_result": result,
            "task_name": request.task_name,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Task scheduling failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Task scheduling failed: {str(e)}")

@router.post("/collaboration/establish")
async def establish_collaboration(request: CollaborationRequest):
    """Establish agent collaboration framework"""
    try:
        result = collaboration_manager.establish_agent_collaboration(
            collaboration_type=request.collaboration_type,
            participating_agents=request.participating_agents,
            shared_resources=request.shared_resources
        )
        
        return {
            "success": result.get("success", False),
            "collaboration_result": result,
            "collaboration_type": request.collaboration_type,
            "participating_agents": request.participating_agents,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Collaboration establishment failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Collaboration establishment failed: {str(e)}")

@router.get("/status")
async def get_nexus_kamuy_status():
    """Get Nexus-Kamuy agent status and capabilities"""
    return {
        "agent": "Nexus-Kamuy",
        "status": "active",
        "capabilities": {
            "workflow_orchestration": {
                "multi_agent_workflows": True,
                "pipeline_execution": True,
                "state_management": True
            },
            "agent_coordination": {
                "handoff_management": True,
                "task_delegation": True,
                "collaboration_framework": True
            },
            "task_scheduling": {
                "multi_agent_tasks": True,
                "priority_management": True,
                "resource_allocation": True
            },
            "collaboration": {
                "cross_agent_communication": True,
                "shared_resource_management": True,
                "knowledge_synchronization": True
            }
        },
        "tools_loaded": [
            "WorkflowOrchestrator",
            "AgentCoordinator",
            "TaskScheduler",
            "CollaborationManager"
        ],
        "timestamp": datetime.utcnow()
    }

@router.get("/tools")
async def list_nexus_kamuy_tools():
    """List all available Nexus-Kamuy tools and endpoints"""
    return {
        "agent": "Nexus-Kamuy",
        "tools": {
            "workflow_orchestration": {
                "create_multi_agent_workflow": "POST /workflow/create",
                "execute_workflow_pipeline": "POST /workflow/execute",
                "coordinate_agent_handoffs": "POST /workflow/handoff",
                "manage_workflow_state": "POST /workflow/manage-state",
                "track_workflow_progress": "GET /workflow/{workflow_id}/progress"
            },
            "task_management": {
                "schedule_task": "POST /task/schedule"
            },
            "collaboration": {
                "establish_collaboration": "POST /collaboration/establish"
            },
            "status": {
                "get_nexus_kamuy_status": "GET /status",
                "list_nexus_kamuy_tools": "GET /tools"
            }
        },
        "total_endpoints": 9,
        "timestamp": datetime.utcnow()
    }
