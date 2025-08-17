"""
Task Scheduler for cybersecurity AI workflow integration.

This tool provides advanced task queue management, scheduling,
prioritization, resource allocation, and dependency resolution.
"""

import heapq
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from ..shared.data_models.workflow_models import Task, TaskQueue, TaskPriority, AgentRole
from ..shared.api_clients.mcp_nexus_client import MCPNexusClient


class TaskScheduler:
    """
    Advanced task scheduling system for cybersecurity AI workflows.
    Provides intelligent scheduling, priority management, and resource optimization.
    """
    
    def __init__(self):
        """Initialize the Task Scheduler."""
        self.mcp_client = MCPNexusClient("http://localhost:3000")
        self.logger = logging.getLogger("TaskScheduler")
        
        self.task_registry = {}
        self.agent_queues = {}
        self.scheduled_tasks = []  # Priority queue using heapq
        self.recurring_schedules = {}
        self.resource_allocations = {}
        self.scheduling_history = []
        
        # Initialize scheduling parameters
        self._initialize_scheduling_system()
    
    def schedule_task_execution(self, task: Dict[str, Any] = Field(..., description="Task to schedule"),
                              schedule_time: Optional[str] = Field(None, description="ISO format datetime for scheduling"),
                              priority_override: Optional[str] = Field(None, description="Priority override"),
                              resource_requirements: Dict[str, Any] = Field(default_factory=dict, description="Resource requirements")) -> Dict[str, Any]:
        """
        Schedule a task for execution with advanced prioritization.
        
        Args:
            task: Task to be scheduled
            schedule_time: When to execute the task (ISO format)
            priority_override: Override task priority
            resource_requirements: Resource requirements for the task
            
        Returns:
            Task scheduling results
        """
        try:
            schedule_id = f"schedule-{int(datetime.utcnow().timestamp())}"
            
            # Create task object if needed
            if isinstance(task, dict):
                task_obj = Task(**task)
            else:
                task_obj = task
            
            # Apply priority override if specified
            if priority_override:
                try:
                    task_obj.priority = TaskPriority(priority_override)
                except ValueError:
                    self.logger.warning(f"Invalid priority override: {priority_override}")
            
            # Determine execution time
            if schedule_time:
                execution_time = datetime.fromisoformat(schedule_time.replace('Z', '+00:00'))
            else:
                execution_time = datetime.utcnow()
            
            # Calculate priority score for heap
            priority_score = self._calculate_priority_score(task_obj, execution_time, resource_requirements)
            
            # Create scheduling entry
            schedule_entry = {
                "schedule_id": schedule_id,
                "task_id": task_obj.id,
                "task": task_obj,
                "execution_time": execution_time,
                "priority_score": priority_score,
                "resource_requirements": resource_requirements,
                "scheduled_at": datetime.utcnow(),
                "status": "scheduled"
            }
            
            # Add to priority queue (negative score for min-heap behavior with max priority)
            heapq.heappush(self.scheduled_tasks, (-priority_score, execution_time, schedule_entry))
            
            # Store in registry
            self.task_registry[task_obj.id] = schedule_entry
            
            # Allocate resources if specified
            if resource_requirements:
                allocation_result = self._allocate_task_resources(task_obj.id, resource_requirements)
                schedule_entry["resource_allocation"] = allocation_result
            
            self.logger.info(f"Task {task_obj.id} scheduled for execution at {execution_time}")
            
            return {
                "success": True,
                "schedule_id": schedule_id,
                "task_id": task_obj.id,
                "execution_time": execution_time.isoformat(),
                "priority_score": priority_score,
                "queue_position": self._get_queue_position(task_obj.id)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to schedule task: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def manage_task_priorities(self, priority_updates: List[Dict[str, Any]] = Field(..., description="List of priority updates")) -> Dict[str, Any]:
        """
        Manage and update task priorities dynamically.
        
        Args:
            priority_updates: List of task priority updates
            
        Returns:
            Priority management results
        """
        try:
            priority_result = {
                "update_id": f"priority-{int(datetime.utcnow().timestamp())}",
                "updated_at": datetime.utcnow().isoformat(),
                "successful_updates": 0,
                "failed_updates": 0,
                "update_details": [],
                "queue_reordered": False
            }
            
            for update in priority_updates:
                task_id = update.get("task_id")
                new_priority = update.get("new_priority")
                reason = update.get("reason", "manual_update")
                
                if task_id not in self.task_registry:
                    priority_result["failed_updates"] += 1
                    priority_result["update_details"].append({
                        "task_id": task_id,
                        "success": False,
                        "error": "Task not found"
                    })
                    continue
                
                try:
                    # Update task priority
                    schedule_entry = self.task_registry[task_id]
                    old_priority = schedule_entry["task"].priority.value
                    
                    schedule_entry["task"].priority = TaskPriority(new_priority)
                    
                    # Recalculate priority score
                    new_priority_score = self._calculate_priority_score(
                        schedule_entry["task"],
                        schedule_entry["execution_time"],
                        schedule_entry["resource_requirements"]
                    )
                    schedule_entry["priority_score"] = new_priority_score
                    
                    # Mark for queue reordering
                    priority_result["queue_reordered"] = True
                    
                    priority_result["successful_updates"] += 1
                    priority_result["update_details"].append({
                        "task_id": task_id,
                        "success": True,
                        "old_priority": old_priority,
                        "new_priority": new_priority,
                        "reason": reason,
                        "new_priority_score": new_priority_score
                    })
                    
                except ValueError as e:
                    priority_result["failed_updates"] += 1
                    priority_result["update_details"].append({
                        "task_id": task_id,
                        "success": False,
                        "error": str(e)
                    })
            
            # Reorder queue if priorities changed
            if priority_result["queue_reordered"]:
                self._reorder_task_queue()
            
            return {
                "success": True,
                "priority_result": priority_result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to manage task priorities: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def allocate_computational_resources(self, resource_pool: Dict[str, Any] = Field(..., description="Available resource pool"),
                                       allocation_strategy: str = Field(default="fair_share", description="Resource allocation strategy")) -> Dict[str, Any]:
        """
        Allocate computational resources to scheduled tasks.
        
        Args:
            resource_pool: Available computational resources
            allocation_strategy: Strategy for resource allocation
            
        Returns:
            Resource allocation results
        """
        try:
            allocation_result = {
                "allocation_id": f"alloc-{int(datetime.utcnow().timestamp())}",
                "allocation_time": datetime.utcnow().isoformat(),
                "strategy": allocation_strategy,
                "total_resources": resource_pool,
                "task_allocations": {},
                "resource_utilization": {},
                "allocation_success": True
            }
            
            # Get pending tasks that need resources
            pending_tasks = [entry for entry in self.task_registry.values() 
                           if entry["status"] == "scheduled" and entry.get("resource_requirements")]
            
            if allocation_strategy == "fair_share":
                allocations = self._apply_fair_share_allocation(pending_tasks, resource_pool)
            elif allocation_strategy == "priority_based":
                allocations = self._apply_priority_based_allocation(pending_tasks, resource_pool)
            elif allocation_strategy == "deadline_aware":
                allocations = self._apply_deadline_aware_allocation(pending_tasks, resource_pool)
            else:
                return {
                    "success": False,
                    "error": f"Unknown allocation strategy: {allocation_strategy}"
                }
            
            allocation_result["task_allocations"] = allocations
            
            # Calculate resource utilization
            allocation_result["resource_utilization"] = self._calculate_resource_utilization(
                allocations, resource_pool
            )
            
            # Store allocations
            for task_id, allocation in allocations.items():
                if task_id in self.task_registry:
                    self.task_registry[task_id]["allocated_resources"] = allocation
            
            return {
                "success": True,
                "allocation_result": allocation_result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to allocate resources: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def resolve_task_dependencies(self, task_id: str = Field(..., description="Task ID to resolve dependencies for")) -> Dict[str, Any]:
        """
        Resolve task dependencies and determine execution readiness.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Dependency resolution results
        """
        try:
            if task_id not in self.task_registry:
                return {"success": False, "error": f"Task {task_id} not found"}
            
            schedule_entry = self.task_registry[task_id]
            task = schedule_entry["task"]
            
            resolution_result = {
                "task_id": task_id,
                "resolution_time": datetime.utcnow().isoformat(),
                "dependencies_resolved": True,
                "blocking_dependencies": [],
                "dependency_chain": [],
                "execution_ready": False,
                "estimated_ready_time": None
            }
            
            # Check direct dependencies
            for dep_task_id in task.dependencies:
                dep_status = self._check_dependency_status(dep_task_id)
                resolution_result["dependency_chain"].append(dep_status)
                
                if not dep_status["satisfied"]:
                    resolution_result["dependencies_resolved"] = False
                    resolution_result["blocking_dependencies"].append(dep_status)
            
            # Check resource dependencies
            resource_deps = schedule_entry.get("resource_requirements", {})
            if resource_deps:
                resource_availability = self._check_resource_availability(resource_deps)
                if not resource_availability["available"]:
                    resolution_result["dependencies_resolved"] = False
                    resolution_result["blocking_dependencies"].append({
                        "type": "resource",
                        "details": resource_availability
                    })
            
            # Determine execution readiness
            if resolution_result["dependencies_resolved"]:
                execution_time = schedule_entry["execution_time"]
                if execution_time <= datetime.utcnow():
                    resolution_result["execution_ready"] = True
                else:
                    resolution_result["estimated_ready_time"] = execution_time.isoformat()
            else:
                # Estimate when dependencies will be resolved
                resolution_result["estimated_ready_time"] = self._estimate_dependency_resolution_time(
                    resolution_result["blocking_dependencies"]
                )
            
            return {
                "success": True,
                "resolution_result": resolution_result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to resolve task dependencies: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def optimize_task_execution_order(self, optimization_criteria: Dict[str, Any] = Field(..., description="Optimization criteria")) -> Dict[str, Any]:
        """
        Optimize task execution order based on specified criteria.
        
        Args:
            optimization_criteria: Criteria for optimization
            
        Returns:
            Optimization results
        """
        try:
            optimization_result = {
                "optimization_id": f"optimize-{int(datetime.utcnow().timestamp())}",
                "optimization_time": datetime.utcnow().isoformat(),
                "criteria": optimization_criteria,
                "original_order": [],
                "optimized_order": [],
                "optimization_metrics": {},
                "improvement_percentage": 0.0
            }
            
            # Get current task order
            current_tasks = [entry for entry in self.task_registry.values() 
                           if entry["status"] == "scheduled"]
            
            optimization_result["original_order"] = [task["task_id"] for task in current_tasks]
            
            # Apply optimization algorithm
            optimization_type = optimization_criteria.get("type", "deadline_first")
            
            if optimization_type == "deadline_first":
                optimized_tasks = self._optimize_by_deadline(current_tasks)
            elif optimization_type == "priority_first":
                optimized_tasks = self._optimize_by_priority(current_tasks)
            elif optimization_type == "dependency_aware":
                optimized_tasks = self._optimize_by_dependencies(current_tasks)
            elif optimization_type == "resource_efficient":
                optimized_tasks = self._optimize_by_resources(current_tasks)
            else:
                return {
                    "success": False,
                    "error": f"Unknown optimization type: {optimization_type}"
                }
            
            optimization_result["optimized_order"] = [task["task_id"] for task in optimized_tasks]
            
            # Calculate optimization metrics
            optimization_result["optimization_metrics"] = self._calculate_optimization_metrics(
                current_tasks, optimized_tasks
            )
            
            # Apply optimized order
            self._apply_optimized_order(optimized_tasks)
            
            return {
                "success": True,
                "optimization_result": optimization_result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to optimize task execution order: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def create_recurring_schedule(self, task_template: Dict[str, Any] = Field(..., description="Task template for recurring execution"),
                                schedule_pattern: str = Field(..., description="Schedule pattern (cron-like)"),
                                schedule_config: Dict[str, Any] = Field(..., description="Schedule configuration")) -> Dict[str, Any]:
        """
        Create recurring schedule for repeated task execution.
        
        Args:
            task_template: Template for tasks to be created
            schedule_pattern: Pattern for recurring execution
            schedule_config: Additional schedule configuration
            
        Returns:
            Recurring schedule creation results
        """
        try:
            schedule_id = f"recurring-{int(datetime.utcnow().timestamp())}"
            
            # Parse schedule pattern
            schedule_info = self._parse_schedule_pattern(schedule_pattern)
            
            if not schedule_info["valid"]:
                return {
                    "success": False,
                    "error": f"Invalid schedule pattern: {schedule_pattern}"
                }
            
            recurring_schedule = {
                "schedule_id": schedule_id,
                "task_template": task_template,
                "schedule_pattern": schedule_pattern,
                "schedule_info": schedule_info,
                "config": schedule_config,
                "created_at": datetime.utcnow().isoformat(),
                "is_active": True,
                "next_execution": schedule_info["next_run"],
                "execution_count": 0,
                "max_executions": schedule_config.get("max_executions"),
                "end_date": schedule_config.get("end_date")
            }
            
            # Store recurring schedule
            self.recurring_schedules[schedule_id] = recurring_schedule
            
            # Schedule first execution
            first_task_result = self._schedule_recurring_task_instance(recurring_schedule)
            
            self.logger.info(f"Recurring schedule created: {schedule_id}")
            
            return {
                "success": True,
                "schedule_id": schedule_id,
                "recurring_schedule": recurring_schedule,
                "first_task_scheduled": first_task_result["success"],
                "next_execution": schedule_info["next_run"].isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create recurring schedule: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_scheduling_analytics(self, time_period_days: int = Field(default=7, description="Time period for analytics in days")) -> Dict[str, Any]:
        """
        Get comprehensive scheduling analytics and performance metrics.
        
        Args:
            time_period_days: Number of days to analyze
            
        Returns:
            Scheduling analytics results
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=time_period_days)
            
            analytics = {
                "analytics_id": f"analytics-{int(datetime.utcnow().timestamp())}",
                "analysis_period": {
                    "start_date": cutoff_date.isoformat(),
                    "end_date": datetime.utcnow().isoformat(),
                    "days": time_period_days
                },
                "task_metrics": {},
                "queue_performance": {},
                "resource_efficiency": {},
                "scheduling_patterns": {}
            }
            
            # Analyze tasks in period
            period_tasks = [entry for entry in self.scheduling_history 
                          if datetime.fromisoformat(entry["scheduled_at"]) >= cutoff_date]
            
            analytics["task_metrics"] = {
                "total_scheduled": len(period_tasks),
                "completed_successfully": len([t for t in period_tasks if t.get("status") == "completed"]),
                "failed_tasks": len([t for t in period_tasks if t.get("status") == "failed"]),
                "cancelled_tasks": len([t for t in period_tasks if t.get("status") == "cancelled"]),
                "average_execution_time": self._calculate_average_execution_time(period_tasks),
                "priority_distribution": self._analyze_priority_distribution(period_tasks)
            }
            
            # Queue performance analysis
            analytics["queue_performance"] = self._analyze_queue_performance()
            
            # Resource efficiency analysis
            analytics["resource_efficiency"] = self._analyze_resource_efficiency(period_tasks)
            
            # Scheduling pattern analysis
            analytics["scheduling_patterns"] = self._analyze_scheduling_patterns(period_tasks)
            
            return {
                "success": True,
                "analytics": analytics
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get scheduling analytics: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _initialize_scheduling_system(self):
        """Initialize the scheduling system with default parameters."""
        # Priority weights for scoring
        self.priority_weights = {
            TaskPriority.URGENT: 100,
            TaskPriority.HIGH: 75,
            TaskPriority.MEDIUM: 50,
            TaskPriority.LOW: 25
        }
        
        # Resource types and their weights
        self.resource_types = {
            "cpu": {"weight": 1.0, "unit": "cores"},
            "memory": {"weight": 1.0, "unit": "gb"},
            "disk": {"weight": 0.5, "unit": "gb"},
            "network": {"weight": 0.3, "unit": "mbps"}
        }
        
        # Initialize agent queues
        for agent_role in AgentRole:
            self.agent_queues[agent_role.value] = TaskQueue(
                queue_id=f"queue-{agent_role.value}",
                queue_name=f"{agent_role.value.title()} Scheduler Queue",
                agent_role=agent_role,
                max_concurrent_tasks=5
            )
    
    def _calculate_priority_score(self, task: Task, execution_time: datetime, 
                                resource_requirements: Dict[str, Any]) -> float:
        """Calculate priority score for task scheduling."""
        base_score = self.priority_weights.get(task.priority, 25)
        
        # Time factor (sooner = higher priority)
        time_delta = (execution_time - datetime.utcnow()).total_seconds()
        time_factor = max(0.1, 1.0 - (time_delta / 86400))  # Scale by day
        
        # Resource factor (lower resource needs = slight priority boost)
        resource_factor = 1.0
        if resource_requirements:
            total_resource_weight = sum(
                req_value * self.resource_types.get(req_type, {}).get("weight", 1.0)
                for req_type, req_value in resource_requirements.items()
                if isinstance(req_value, (int, float))
            )
            resource_factor = max(0.5, 1.0 - (total_resource_weight / 100))
        
        # Calculate final score
        priority_score = base_score * time_factor * resource_factor
        
        return round(priority_score, 2)
    
    def _parse_schedule_pattern(self, pattern: str) -> Dict[str, Any]:
        """Parse schedule pattern and calculate next execution time."""
        # Simplified cron-like pattern parsing
        pattern_info = {
            "pattern": pattern,
            "valid": False,
            "type": "unknown",
            "next_run": None,
            "interval": None
        }
        
        try:
            if pattern.startswith("@"):
                # Special patterns
                special_patterns = {
                    "@hourly": {"type": "interval", "minutes": 60},
                    "@daily": {"type": "interval", "minutes": 1440},
                    "@weekly": {"type": "interval", "minutes": 10080},
                    "@monthly": {"type": "interval", "minutes": 43200}
                }
                
                if pattern in special_patterns:
                    pattern_config = special_patterns[pattern]
                    pattern_info.update({
                        "valid": True,
                        "type": pattern_config["type"],
                        "interval": pattern_config["minutes"],
                        "next_run": datetime.utcnow() + timedelta(minutes=pattern_config["minutes"])
                    })
            
            elif pattern.startswith("every "):
                # Interval patterns like "every 30 minutes"
                parts = pattern.split()
                if len(parts) >= 3:
                    try:
                        interval_value = int(parts[1])
                        interval_unit = parts[2].lower()
                        
                        unit_multipliers = {
                            "minute": 1, "minutes": 1,
                            "hour": 60, "hours": 60,
                            "day": 1440, "days": 1440
                        }
                        
                        if interval_unit in unit_multipliers:
                            interval_minutes = interval_value * unit_multipliers[interval_unit]
                            pattern_info.update({
                                "valid": True,
                                "type": "interval",
                                "interval": interval_minutes,
                                "next_run": datetime.utcnow() + timedelta(minutes=interval_minutes)
                            })
                    except ValueError:
                        pass
            
            # If no valid pattern found, default to hourly
            if not pattern_info["valid"]:
                pattern_info.update({
                    "valid": True,
                    "type": "default",
                    "interval": 60,
                    "next_run": datetime.utcnow() + timedelta(hours=1)
                })
        
        except Exception as e:
            self.logger.error(f"Failed to parse schedule pattern: {str(e)}")
        
        return pattern_info
    
    def _schedule_recurring_task_instance(self, recurring_schedule: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule an instance of a recurring task."""
        try:
            # Create task from template
            template = recurring_schedule["task_template"]
            instance_id = f"{template.get('id', 'recurring')}-{int(datetime.utcnow().timestamp())}"
            
            task_instance = template.copy()
            task_instance["id"] = instance_id
            task_instance["created_from_schedule"] = recurring_schedule["schedule_id"]
            
            # Schedule the task instance
            schedule_result = self.schedule_task_execution(
                task=task_instance,
                schedule_time=recurring_schedule["next_execution"].isoformat()
            )
            
            if schedule_result["success"]:
                # Update recurring schedule
                recurring_schedule["execution_count"] += 1
                
                # Calculate next execution time
                interval_minutes = recurring_schedule["schedule_info"]["interval"]
                recurring_schedule["next_execution"] = datetime.utcnow() + timedelta(minutes=interval_minutes)
            
            return schedule_result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_queue_position(self, task_id: str) -> int:
        """Get position of task in scheduling queue."""
        # Count tasks with higher or equal priority that are scheduled earlier
        if task_id not in self.task_registry:
            return -1
        
        target_entry = self.task_registry[task_id]
        target_score = target_entry["priority_score"]
        target_time = target_entry["execution_time"]
        
        position = 1
        for _, _, entry in self.scheduled_tasks:
            if (entry["priority_score"] > target_score or 
                (entry["priority_score"] == target_score and entry["execution_time"] < target_time)):
                position += 1
        
        return position
    
    def _reorder_task_queue(self):
        """Reorder task queue after priority changes."""
        # Rebuild priority queue
        current_tasks = []
        while self.scheduled_tasks:
            _, _, entry = heapq.heappop(self.scheduled_tasks)
            current_tasks.append(entry)
        
        # Re-add with updated priorities
        for entry in current_tasks:
            priority_score = entry["priority_score"]
            execution_time = entry["execution_time"]
            heapq.heappush(self.scheduled_tasks, (-priority_score, execution_time, entry))
    
    def _allocate_task_resources(self, task_id: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Allocate resources for a specific task."""
        allocation = {
            "task_id": task_id,
            "allocated_at": datetime.utcnow().isoformat(),
            "resources": requirements,
            "allocation_status": "allocated"
        }
        
        self.resource_allocations[task_id] = allocation
        return allocation
    
    def _apply_fair_share_allocation(self, tasks: List[Dict[str, Any]], 
                                   resource_pool: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Apply fair share resource allocation."""
        allocations = {}
        
        if not tasks:
            return allocations
        
        # Divide resources equally among tasks
        task_count = len(tasks)
        
        for task_entry in tasks:
            task_id = task_entry["task_id"]
            requirements = task_entry.get("resource_requirements", {})
            
            # Allocate proportional share
            allocation = {}
            for resource_type, total_amount in resource_pool.items():
                if resource_type in requirements:
                    requested = requirements[resource_type]
                    fair_share = total_amount / task_count
                    allocation[resource_type] = min(requested, fair_share)
            
            allocations[task_id] = allocation
        
        return allocations
    
    def _apply_priority_based_allocation(self, tasks: List[Dict[str, Any]], 
                                       resource_pool: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Apply priority-based resource allocation."""
        allocations = {}
        
        # Sort tasks by priority
        sorted_tasks = sorted(tasks, key=lambda t: t["priority_score"], reverse=True)
        
        remaining_resources = resource_pool.copy()
        
        for task_entry in sorted_tasks:
            task_id = task_entry["task_id"]
            requirements = task_entry.get("resource_requirements", {})
            
            allocation = {}
            for resource_type, requested in requirements.items():
                if resource_type in remaining_resources:
                    available = remaining_resources[resource_type]
                    allocated = min(requested, available)
                    allocation[resource_type] = allocated
                    remaining_resources[resource_type] -= allocated
            
            allocations[task_id] = allocation
        
        return allocations
    
    def _apply_deadline_aware_allocation(self, tasks: List[Dict[str, Any]], 
                                       resource_pool: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Apply deadline-aware resource allocation."""
        # Sort by execution time (earliest first)
        sorted_tasks = sorted(tasks, key=lambda t: t["execution_time"])
        
        return self._apply_priority_based_allocation(sorted_tasks, resource_pool)
    
    def _calculate_resource_utilization(self, allocations: Dict[str, Dict[str, Any]], 
                                      resource_pool: Dict[str, Any]) -> Dict[str, float]:
        """Calculate resource utilization percentages."""
        utilization = {}
        
        for resource_type, total_amount in resource_pool.items():
            allocated_amount = sum(
                allocation.get(resource_type, 0) for allocation in allocations.values()
            )
            utilization[resource_type] = (allocated_amount / total_amount) * 100 if total_amount > 0 else 0
        
        return utilization
    
    def _check_dependency_status(self, dep_task_id: str) -> Dict[str, Any]:
        """Check the status of a task dependency."""
        if dep_task_id in self.task_registry:
            dep_entry = self.task_registry[dep_task_id]
            dep_task = dep_entry["task"]
            
            return {
                "dependency_id": dep_task_id,
                "satisfied": dep_task.status.value in ["completed"],
                "current_status": dep_task.status.value,
                "type": "task_dependency"
            }
        else:
            return {
                "dependency_id": dep_task_id,
                "satisfied": False,
                "current_status": "not_found",
                "type": "task_dependency"
            }
    
    def _check_resource_availability(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Check if required resources are available."""
        # Simplified resource availability check
        return {
            "available": True,
            "requirements": requirements,
            "availability_details": "Resources are available"
        }
    
    def _estimate_dependency_resolution_time(self, blocking_deps: List[Dict[str, Any]]) -> str:
        """Estimate when blocking dependencies will be resolved."""
        max_resolution_time = datetime.utcnow()
        
        for dep in blocking_deps:
            if dep.get("type") == "task_dependency":
                # Estimate based on typical task execution time
                estimated_time = datetime.utcnow() + timedelta(minutes=30)
            elif dep.get("type") == "resource":
                # Estimate based on resource provisioning time
                estimated_time = datetime.utcnow() + timedelta(minutes=10)
            else:
                estimated_time = datetime.utcnow() + timedelta(minutes=15)
            
            if estimated_time > max_resolution_time:
                max_resolution_time = estimated_time
        
        return max_resolution_time.isoformat()
    
    def _optimize_by_deadline(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize task order by deadline."""
        return sorted(tasks, key=lambda t: t["execution_time"])
    
    def _optimize_by_priority(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize task order by priority."""
        return sorted(tasks, key=lambda t: t["priority_score"], reverse=True)
    
    def _optimize_by_dependencies(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize task order considering dependencies."""
        # Topological sort for dependency resolution
        ordered_tasks = []
        remaining_tasks = tasks.copy()
        
        while remaining_tasks:
            # Find tasks with no unresolved dependencies
            ready_tasks = []
            for task_entry in remaining_tasks:
                task = task_entry["task"]
                dependencies_satisfied = all(
                    dep_id in [completed["task_id"] for completed in ordered_tasks]
                    for dep_id in task.dependencies
                )
                if dependencies_satisfied:
                    ready_tasks.append(task_entry)
            
            if not ready_tasks:
                # Circular dependency or missing dependency - add remaining tasks
                ordered_tasks.extend(remaining_tasks)
                break
            
            # Sort ready tasks by priority and add to ordered list
            ready_tasks.sort(key=lambda t: t["priority_score"], reverse=True)
            ordered_tasks.extend(ready_tasks)
            
            # Remove from remaining
            for task in ready_tasks:
                remaining_tasks.remove(task)
        
        return ordered_tasks
    
    def _optimize_by_resources(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize task order for resource efficiency."""
        # Sort by resource requirements (lower first for better packing)
        return sorted(tasks, key=lambda t: sum(t.get("resource_requirements", {}).values()))
    
    def _calculate_optimization_metrics(self, original: List[Dict[str, Any]], 
                                      optimized: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate optimization improvement metrics."""
        return {
            "tasks_reordered": len([t for i, t in enumerate(optimized) 
                                  if i < len(original) and t["task_id"] != original[i]["task_id"]]),
            "estimated_time_savings": 15,  # minutes (simulated)
            "resource_efficiency_improvement": 10.5,  # percentage (simulated)
            "dependency_violations_resolved": 2  # count (simulated)
        }
    
    def _apply_optimized_order(self, optimized_tasks: List[Dict[str, Any]]):
        """Apply optimized task order to the scheduling queue."""
        # Rebuild the priority queue with optimized order
        self.scheduled_tasks.clear()
        
        for i, task_entry in enumerate(optimized_tasks):
            # Adjust execution times to reflect optimized order
            base_time = datetime.utcnow() + timedelta(minutes=i * 5)  # 5-minute intervals
            task_entry["execution_time"] = base_time
            
            # Update registry
            self.task_registry[task_entry["task_id"]] = task_entry
            
            # Add back to priority queue
            heapq.heappush(
                self.scheduled_tasks, 
                (-task_entry["priority_score"], base_time, task_entry)
            )
    
    def _calculate_average_execution_time(self, tasks: List[Dict[str, Any]]) -> float:
        """Calculate average execution time for tasks."""
        execution_times = []
        for task in tasks:
            if "actual_duration" in task and task["actual_duration"]:
                execution_times.append(task["actual_duration"])
        
        return sum(execution_times) / len(execution_times) if execution_times else 0.0
    
    def _analyze_priority_distribution(self, tasks: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze distribution of task priorities."""
        distribution = {"urgent": 0, "high": 0, "medium": 0, "low": 0}
        
        for task in tasks:
            priority = task.get("task", {}).get("priority", "medium")
            if isinstance(priority, TaskPriority):
                priority = priority.value
            distribution[priority] = distribution.get(priority, 0) + 1
        
        return distribution
    
    def _analyze_queue_performance(self) -> Dict[str, Any]:
        """Analyze queue performance metrics."""
        performance = {}
        
        for agent_role, queue in self.agent_queues.items():
            status = queue.get_queue_status()
            performance[agent_role] = {
                **status,
                "efficiency_score": 85.0,  # Simulated
                "average_wait_time": 12.5   # minutes (simulated)
            }
        
        return performance
    
    def _analyze_resource_efficiency(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze resource allocation efficiency."""
        return {
            "average_utilization": 78.5,  # percentage (simulated)
            "resource_waste": 12.3,       # percentage (simulated)
            "optimization_opportunities": 3  # count (simulated)
        }
    
    def _analyze_scheduling_patterns(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze scheduling patterns and trends."""
        return {
            "peak_hours": ["09:00", "14:00", "16:00"],
            "busiest_day": "Wednesday",
            "recurring_task_percentage": 35.2,
            "average_queue_depth": 4.8
        }
