"""
Workflow-specific data models for cybersecurity AI workflow integration.

This module contains data structures for tasks, workflows, and collaboration between AI agents.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator

from .base_models import IdentifiedModel, TaskStatus, ProgressTracker


class TaskPriority(str, Enum):
    """Task priority levels."""
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AgentRole(str, Enum):
    """AI agent roles in the workflow."""
    RT_DEV = "rt_dev"
    BUG_HUNTER = "bug_hunter"
    DAEDELU5 = "daedelu5"
    BURPSUITE_OPERATOR = "burpsuite_operator"
    NEXUS_KAMUY = "nexus_kamuy"


class WorkflowType(str, Enum):
    """Types of workflows."""
    SECURITY_ASSESSMENT = "security_assessment"
    PENETRATION_TEST = "penetration_test"
    VULNERABILITY_SCAN = "vulnerability_scan"
    INFRASTRUCTURE_DEPLOYMENT = "infrastructure_deployment"
    CODE_ANALYSIS = "code_analysis"
    COMPLIANCE_CHECK = "compliance_check"
    INCIDENT_RESPONSE = "incident_response"


class Task(IdentifiedModel):
    """Task model for workflow execution."""
    
    title: str = Field(..., description="Task title")
    task_type: str = Field(..., description="Type of task")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current task status")
    assigned_agent: Optional[AgentRole] = Field(default=None, description="Agent assigned to the task")
    requester: str = Field(..., description="Who requested the task")
    requirements: Dict[str, Any] = Field(default_factory=dict, description="Task requirements and parameters")
    dependencies: List[str] = Field(default_factory=list, description="List of task IDs this depends on")
    blocking_tasks: List[str] = Field(default_factory=list, description="List of task IDs that depend on this")
    expected_duration: Optional[int] = Field(default=None, description="Expected duration in minutes")
    actual_duration: Optional[int] = Field(default=None, description="Actual duration in minutes")
    start_time: Optional[datetime] = Field(default=None, description="Task start time")
    end_time: Optional[datetime] = Field(default=None, description="Task completion time")
    progress: Optional[ProgressTracker] = Field(default=None, description="Task progress tracking")
    results: Dict[str, Any] = Field(default_factory=dict, description="Task execution results")
    error_details: Optional[Dict[str, Any]] = Field(default=None, description="Error details if task failed")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    
    @validator('priority')
    def validate_priority(cls, v):
        if v not in TaskPriority:
            raise ValueError(f'Priority must be one of: {", ".join([p.value for p in TaskPriority])}')
        return v
    
    def start_task(self, agent: AgentRole, total_steps: Optional[int] = None):
        """Start executing the task."""
        self.assigned_agent = agent
        self.status = TaskStatus.RUNNING
        self.start_time = datetime.utcnow()
        
        if total_steps:
            self.progress = ProgressTracker(total_steps=total_steps)
        
        self.update_timestamp()
    
    def complete_task(self, results: Dict[str, Any]):
        """Complete the task successfully."""
        self.status = TaskStatus.COMPLETED
        self.end_time = datetime.utcnow()
        self.results = results
        
        if self.start_time:
            duration_delta = self.end_time - self.start_time
            self.actual_duration = int(duration_delta.total_seconds() / 60)
        
        if self.progress:
            self.progress.complete()
        
        self.update_timestamp()
    
    def fail_task(self, error_details: Dict[str, Any], retry: bool = True):
        """Mark task as failed."""
        self.error_details = error_details
        
        if retry and self.retry_count < self.max_retries:
            self.retry_count += 1
            self.status = TaskStatus.PENDING
            self.metadata[f"retry_{self.retry_count}_at"] = datetime.utcnow().isoformat()
        else:
            self.status = TaskStatus.FAILED
            self.end_time = datetime.utcnow()
            
            if self.start_time:
                duration_delta = self.end_time - self.start_time
                self.actual_duration = int(duration_delta.total_seconds() / 60)
        
        self.update_timestamp()
    
    def cancel_task(self, reason: str):
        """Cancel the task."""
        self.status = TaskStatus.CANCELLED
        self.end_time = datetime.utcnow()
        self.metadata["cancellation_reason"] = reason
        self.metadata["cancelled_at"] = datetime.utcnow().isoformat()
        
        if self.start_time:
            duration_delta = self.end_time - self.start_time
            self.actual_duration = int(duration_delta.total_seconds() / 60)
        
        self.update_timestamp()


class WorkflowStep(BaseModel):
    """Individual step in a workflow."""
    
    step_id: str = Field(..., description="Unique step identifier")
    step_name: str = Field(..., description="Step name")
    agent_role: AgentRole = Field(..., description="Agent responsible for this step")
    step_type: str = Field(..., description="Type of step")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Step parameters")
    dependencies: List[str] = Field(default_factory=list, description="Step dependencies")
    timeout_minutes: int = Field(default=60, description="Step timeout in minutes")
    retry_on_failure: bool = Field(default=True, description="Whether to retry on failure")
    critical: bool = Field(default=False, description="Whether step is critical for workflow success")
    validation_rules: List[Dict[str, Any]] = Field(default_factory=list, description="Output validation rules")
    
    def create_task(self, workflow_id: str, requester: str) -> Task:
        """Create a task from this workflow step."""
        return Task(
            id=f"{workflow_id}_{self.step_id}",
            title=f"Workflow Step: {self.step_name}",
            task_type=self.step_type,
            priority=TaskPriority.HIGH if self.critical else TaskPriority.MEDIUM,
            assigned_agent=self.agent_role,
            requester=requester,
            requirements=self.parameters,
            expected_duration=self.timeout_minutes,
            max_retries=3 if self.retry_on_failure else 0
        )


class CollaborationWorkflow(IdentifiedModel):
    """Multi-agent collaboration workflow."""
    
    workflow_name: str = Field(..., description="Workflow name")
    workflow_type: WorkflowType = Field(..., description="Type of workflow")
    requester: str = Field(..., description="Who requested the workflow")
    target: str = Field(..., description="Workflow target (system, application, etc.)")
    objectives: List[str] = Field(..., description="Workflow objectives")
    steps: List[WorkflowStep] = Field(..., description="Workflow steps")
    current_step_index: int = Field(default=0, description="Index of current step")
    status: str = Field(default="pending", description="Workflow status")
    start_time: Optional[datetime] = Field(default=None, description="Workflow start time")
    end_time: Optional[datetime] = Field(default=None, description="Workflow completion time")
    estimated_duration: Optional[int] = Field(default=None, description="Estimated duration in minutes")
    actual_duration: Optional[int] = Field(default=None, description="Actual duration in minutes")
    progress: Optional[ProgressTracker] = Field(default=None, description="Overall workflow progress")
    participating_agents: List[AgentRole] = Field(default_factory=list, description="Agents participating in workflow")
    step_results: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Results from each step")
    failure_handling: str = Field(default="continue", description="How to handle step failures")
    notification_settings: Dict[str, Any] = Field(default_factory=dict, description="Notification configuration")
    
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['pending', 'running', 'completed', 'failed', 'cancelled', 'paused']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v
    
    @validator('failure_handling')
    def validate_failure_handling(cls, v):
        allowed_values = ['stop', 'continue', 'retry', 'skip']
        if v not in allowed_values:
            raise ValueError(f'Failure handling must be one of: {", ".join(allowed_values)}')
        return v
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.participating_agents:
            self.participating_agents = list(set(step.agent_role for step in self.steps))
        if not self.estimated_duration:
            self.estimated_duration = sum(step.timeout_minutes for step in self.steps)
        if not self.progress:
            self.progress = ProgressTracker(total_steps=len(self.steps))
    
    def start_workflow(self):
        """Start the workflow execution."""
        self.status = "running"
        self.start_time = datetime.utcnow()
        self.current_step_index = 0
        self.update_timestamp()
    
    def advance_step(self, step_results: Dict[str, Any]):
        """Advance to the next step."""
        if self.current_step_index < len(self.steps):
            current_step = self.steps[self.current_step_index]
            self.step_results[current_step.step_id] = step_results
            
            self.current_step_index += 1
            if self.progress:
                self.progress.advance_step(
                    step_name=self.steps[self.current_step_index - 1].step_name
                )
            
            self.update_timestamp()
    
    def get_current_step(self) -> Optional[WorkflowStep]:
        """Get the current workflow step."""
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None
    
    def complete_workflow(self):
        """Complete the workflow."""
        self.status = "completed"
        self.end_time = datetime.utcnow()
        
        if self.start_time:
            duration_delta = self.end_time - self.start_time
            self.actual_duration = int(duration_delta.total_seconds() / 60)
        
        if self.progress:
            self.progress.complete()
        
        self.update_timestamp()
    
    def fail_workflow(self, error_details: Dict[str, Any]):
        """Mark workflow as failed."""
        self.status = "failed"
        self.end_time = datetime.utcnow()
        self.metadata["error_details"] = error_details
        self.metadata["failed_at_step"] = self.current_step_index
        
        if self.start_time:
            duration_delta = self.end_time - self.start_time
            self.actual_duration = int(duration_delta.total_seconds() / 60)
        
        self.update_timestamp()
    
    def pause_workflow(self):
        """Pause the workflow execution."""
        self.status = "paused"
        self.metadata["paused_at"] = datetime.utcnow().isoformat()
        self.update_timestamp()
    
    def resume_workflow(self):
        """Resume the workflow execution."""
        self.status = "running"
        self.metadata["resumed_at"] = datetime.utcnow().isoformat()
        self.update_timestamp()


class ExecutionContext(BaseModel):
    """Execution context for tasks and workflows."""
    
    context_id: str = Field(..., description="Unique context identifier")
    platform_connections: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Platform connection details")
    environment: str = Field(default="development", description="Execution environment")
    security_context: Dict[str, Any] = Field(default_factory=dict, description="Security context information")
    resource_limits: Dict[str, Union[int, float]] = Field(default_factory=dict, description="Resource limits")
    working_directory: Optional[str] = Field(default=None, description="Working directory for execution")
    environment_variables: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    configuration_overrides: Dict[str, Any] = Field(default_factory=dict, description="Configuration overrides")
    logging_config: Dict[str, Any] = Field(default_factory=dict, description="Logging configuration")
    monitoring_enabled: bool = Field(default=True, description="Whether to enable monitoring")
    debug_mode: bool = Field(default=False, description="Whether debug mode is enabled")
    
    @validator('environment')
    def validate_environment(cls, v):
        allowed_environments = ['development', 'testing', 'staging', 'production']
        if v not in allowed_environments:
            raise ValueError(f'Environment must be one of: {", ".join(allowed_environments)}')
        return v
    
    def add_platform_connection(self, platform_name: str, connection_config: Dict[str, Any]):
        """Add a platform connection to the context."""
        self.platform_connections[platform_name] = connection_config
    
    def get_platform_connection(self, platform_name: str) -> Optional[Dict[str, Any]]:
        """Get platform connection configuration."""
        return self.platform_connections.get(platform_name)
    
    def set_resource_limit(self, resource: str, limit: Union[int, float]):
        """Set a resource limit."""
        self.resource_limits[resource] = limit
    
    def get_resource_limit(self, resource: str) -> Optional[Union[int, float]]:
        """Get a resource limit."""
        return self.resource_limits.get(resource)


class TaskQueue(BaseModel):
    """Task queue for managing task execution."""
    
    queue_id: str = Field(..., description="Queue identifier")
    queue_name: str = Field(..., description="Queue name")
    agent_role: AgentRole = Field(..., description="Agent role this queue serves")
    max_concurrent_tasks: int = Field(default=5, description="Maximum concurrent tasks")
    priority_based: bool = Field(default=True, description="Whether to use priority-based scheduling")
    pending_tasks: List[str] = Field(default_factory=list, description="List of pending task IDs")
    running_tasks: List[str] = Field(default_factory=list, description="List of running task IDs")
    completed_tasks: List[str] = Field(default_factory=list, description="List of completed task IDs")
    failed_tasks: List[str] = Field(default_factory=list, description="List of failed task IDs")
    queue_metrics: Dict[str, Union[int, float]] = Field(default_factory=dict, description="Queue performance metrics")
    
    def add_task(self, task_id: str):
        """Add a task to the queue."""
        if task_id not in self.pending_tasks:
            self.pending_tasks.append(task_id)
    
    def start_task(self, task_id: str) -> bool:
        """Move task from pending to running."""
        if task_id in self.pending_tasks and len(self.running_tasks) < self.max_concurrent_tasks:
            self.pending_tasks.remove(task_id)
            self.running_tasks.append(task_id)
            return True
        return False
    
    def complete_task(self, task_id: str):
        """Move task from running to completed."""
        if task_id in self.running_tasks:
            self.running_tasks.remove(task_id)
            self.completed_tasks.append(task_id)
    
    def fail_task(self, task_id: str):
        """Move task from running to failed."""
        if task_id in self.running_tasks:
            self.running_tasks.remove(task_id)
            self.failed_tasks.append(task_id)
    
    def get_queue_status(self) -> Dict[str, int]:
        """Get current queue status."""
        return {
            "pending": len(self.pending_tasks),
            "running": len(self.running_tasks),
            "completed": len(self.completed_tasks),
            "failed": len(self.failed_tasks),
            "capacity_used": len(self.running_tasks),
            "capacity_available": self.max_concurrent_tasks - len(self.running_tasks)
        }


class CollaborationSession(IdentifiedModel):
    """Session for multi-agent collaboration."""
    
    session_name: str = Field(..., description="Session name")
    participants: List[AgentRole] = Field(..., description="Participating agents")
    session_type: str = Field(..., description="Type of collaboration session")
    objective: str = Field(..., description="Session objective")
    status: str = Field(default="active", description="Session status")
    created_by: str = Field(..., description="Who created the session")
    start_time: datetime = Field(default_factory=datetime.utcnow, description="Session start time")
    end_time: Optional[datetime] = Field(default=None, description="Session end time")
    shared_context: Dict[str, Any] = Field(default_factory=dict, description="Shared context between agents")
    communication_log: List[Dict[str, Any]] = Field(default_factory=list, description="Communication log")
    shared_resources: List[str] = Field(default_factory=list, description="Shared resource IDs")
    coordination_rules: Dict[str, Any] = Field(default_factory=dict, description="Coordination rules")
    
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['active', 'paused', 'completed', 'cancelled']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v
    
    def add_message(self, sender: AgentRole, message: str, message_type: str = "info"):
        """Add a message to the communication log."""
        message_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "sender": sender.value,
            "message": message,
            "type": message_type
        }
        self.communication_log.append(message_entry)
        self.update_timestamp()
    
    def share_resource(self, resource_id: str, shared_by: AgentRole):
        """Share a resource with all participants."""
        if resource_id not in self.shared_resources:
            self.shared_resources.append(resource_id)
            self.add_message(shared_by, f"Shared resource: {resource_id}", "resource_share")
    
    def update_shared_context(self, key: str, value: Any, updated_by: AgentRole):
        """Update shared context."""
        self.shared_context[key] = {
            "value": value,
            "updated_by": updated_by.value,
            "updated_at": datetime.utcnow().isoformat()
        }
        self.update_timestamp()
    
    def end_session(self, ended_by: str):
        """End the collaboration session."""
        self.status = "completed"
        self.end_time = datetime.utcnow()
        self.metadata["ended_by"] = ended_by
        self.add_message(AgentRole.NEXUS_KAMUY, f"Session ended by {ended_by}", "session_end")
        self.update_timestamp()
