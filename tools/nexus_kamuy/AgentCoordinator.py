"""
Agent Coordinator for cybersecurity AI workflow integration.

This tool manages multi-agent coordination, capability discovery,
task delegation, load balancing, and agent health monitoring.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ..shared.data_models.workflow_models import AgentRole, Task, TaskQueue
from ..shared.api_clients.mcp_nexus_client import MCPNexusClient
from ..shared.api_clients.rtpi_pen_client import RTPIPenClient
from ..shared.api_clients.attack_node_client import AttackNodeClient


class AgentCoordinator:
    """
    Multi-agent coordination system for cybersecurity AI workflows.
    Provides agent discovery, capability matching, load balancing, and health monitoring.
    """
    
    def __init__(self):
        """Initialize the Agent Coordinator."""
        self.mcp_client = MCPNexusClient("http://localhost:3000")
        self.rtpi_client = RTPIPenClient("http://localhost:8080")
        self.attack_client = AttackNodeClient("http://localhost:5000")
        self.logger = logging.getLogger("AgentCoordinator")
        
        self.registered_agents = {}
        self.agent_capabilities = {}
        self.agent_queues = {}
        self.coordination_sessions = {}
        
        # Initialize agent registry
        self._initialize_agent_registry()
    
    def discover_agent_capabilities(self, agent_roles: List[str] = Field(..., description="List of agent roles to discover capabilities for")) -> Dict[str, Any]:
        """
        Discover and catalog capabilities of specified agents.
        
        Args:
            agent_roles: List of agent roles to discover capabilities for
            
        Returns:
            Agent capability discovery results
        """
        try:
            discovery_result = {
                "discovery_id": f"discovery-{int(datetime.utcnow().timestamp())}",
                "discovery_date": datetime.utcnow().isoformat(),
                "agents_discovered": len(agent_roles),
                "capabilities": {},
                "availability_status": {},
                "performance_metrics": {}
            }
            
            for agent_role in agent_roles:
                if agent_role not in [role.value for role in AgentRole]:
                    self.logger.warning(f"Unknown agent role: {agent_role}")
                    continue
                
                # Discover capabilities for this agent
                capabilities = self._discover_agent_capabilities(agent_role)
                availability = self._check_agent_availability(agent_role)
                performance = self._get_agent_performance_metrics(agent_role)
                
                discovery_result["capabilities"][agent_role] = capabilities
                discovery_result["availability_status"][agent_role] = availability
                discovery_result["performance_metrics"][agent_role] = performance
                
                # Update local registry
                self.agent_capabilities[agent_role] = capabilities
                self.registered_agents[agent_role] = {
                    "capabilities": capabilities,
                    "availability": availability,
                    "performance": performance,
                    "last_updated": datetime.utcnow().isoformat()
                }
            
            self.logger.info(f"Agent capability discovery completed: {discovery_result['discovery_id']}")
            
            return {
                "success": True,
                "discovery_result": discovery_result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to discover agent capabilities: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def delegate_task_to_agent(self, task: Dict[str, Any] = Field(..., description="Task to delegate"),
                             preferred_agent: Optional[str] = Field(None, description="Preferred agent role"),
                             selection_criteria: Dict[str, Any] = Field(default_factory=dict, description="Agent selection criteria")) -> Dict[str, Any]:
        """
        Delegate a task to the most suitable agent based on capabilities and load.
        
        Args:
            task: Task to be delegated
            preferred_agent: Preferred agent role (optional)
            selection_criteria: Criteria for agent selection
            
        Returns:
            Task delegation results
        """
        try:
            delegation_result = {
                "delegation_id": f"delegate-{int(datetime.utcnow().timestamp())}",
                "task_id": task.get("id", "unknown"),
                "delegation_time": datetime.utcnow().isoformat(),
                "selected_agent": None,
                "selection_reasoning": [],
                "delegation_success": False
            }
            
            # Determine suitable agents for the task
            suitable_agents = self._find_suitable_agents(task, selection_criteria)
            
            if not suitable_agents:
                return {
                    "success": False,
                    "error": "No suitable agents found for task",
                    "delegation_result": delegation_result
                }
            
            # Select best agent
            if preferred_agent and preferred_agent in suitable_agents:
                selected_agent = preferred_agent
                delegation_result["selection_reasoning"].append(f"Used preferred agent: {preferred_agent}")
            else:
                selected_agent = self._select_optimal_agent(suitable_agents, task, selection_criteria)
                delegation_result["selection_reasoning"].append(f"Selected optimal agent based on criteria")
            
            delegation_result["selected_agent"] = selected_agent
            
            # Delegate task to selected agent
            delegation_success = self._delegate_to_agent(selected_agent, task)
            delegation_result["delegation_success"] = delegation_success
            
            if delegation_success:
                delegation_result["queue_position"] = self._get_agent_queue_position(selected_agent, task["id"])
                
                self.logger.info(f"Task {task.get('id')} delegated to {selected_agent}")
                
                return {
                    "success": True,
                    "delegation_result": delegation_result
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to delegate task to {selected_agent}",
                    "delegation_result": delegation_result
                }
            
        except Exception as e:
            self.logger.error(f"Failed to delegate task: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def balance_agent_workload(self, rebalance_strategy: str = Field(default="even_distribution", description="Workload balancing strategy")) -> Dict[str, Any]:
        """
        Balance workload across available agents.
        
        Args:
            rebalance_strategy: Strategy for load balancing
            
        Returns:
            Load balancing results
        """
        try:
            balancing_result = {
                "balancing_id": f"balance-{int(datetime.utcnow().timestamp())}",
                "strategy": rebalance_strategy,
                "balancing_time": datetime.utcnow().isoformat(),
                "agent_loads": {},
                "redistributed_tasks": [],
                "balancing_success": True
            }
            
            # Get current load for each agent
            for agent_role in self.agent_queues:
                queue = self.agent_queues[agent_role]
                load_info = {
                    "pending_tasks": len(queue.pending_tasks),
                    "running_tasks": len(queue.running_tasks),
                    "queue_capacity": queue.max_concurrent_tasks,
                    "utilization_percentage": (len(queue.running_tasks) / queue.max_concurrent_tasks) * 100
                }
                balancing_result["agent_loads"][agent_role] = load_info
            
            # Apply rebalancing strategy
            if rebalance_strategy == "even_distribution":
                redistribution = self._apply_even_distribution_strategy()
                balancing_result["redistributed_tasks"] = redistribution
            
            elif rebalance_strategy == "capability_based":
                redistribution = self._apply_capability_based_strategy()
                balancing_result["redistributed_tasks"] = redistribution
            
            elif rebalance_strategy == "priority_based":
                redistribution = self._apply_priority_based_strategy()
                balancing_result["redistributed_tasks"] = redistribution
            
            else:
                balancing_result["balancing_success"] = False
                balancing_result["error"] = f"Unknown rebalancing strategy: {rebalance_strategy}"
            
            return {
                "success": balancing_result["balancing_success"],
                "balancing_result": balancing_result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to balance agent workload: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def monitor_agent_health(self, agent_roles: List[str] = Field(..., description="Agent roles to monitor")) -> Dict[str, Any]:
        """
        Monitor health and performance of specified agents.
        
        Args:
            agent_roles: List of agent roles to monitor
            
        Returns:
            Agent health monitoring results
        """
        try:
            health_monitoring = {
                "monitoring_id": f"health-{int(datetime.utcnow().timestamp())}",
                "monitoring_time": datetime.utcnow().isoformat(),
                "agents_monitored": len(agent_roles),
                "health_status": {},
                "performance_alerts": [],
                "overall_system_health": "healthy"
            }
            
            unhealthy_agents = 0
            
            for agent_role in agent_roles:
                health_status = self._check_agent_health(agent_role)
                health_monitoring["health_status"][agent_role] = health_status
                
                # Check for health issues
                if health_status["status"] != "healthy":
                    unhealthy_agents += 1
                    
                    health_monitoring["performance_alerts"].append({
                        "agent": agent_role,
                        "alert_type": "health_degraded",
                        "severity": health_status.get("severity", "medium"),
                        "details": health_status.get("issues", [])
                    })
                
                # Check for performance issues
                performance_metrics = health_status.get("performance_metrics", {})
                if performance_metrics.get("response_time", 0) > 5000:  # > 5 seconds
                    health_monitoring["performance_alerts"].append({
                        "agent": agent_role,
                        "alert_type": "slow_response",
                        "severity": "medium",
                        "details": f"Response time: {performance_metrics['response_time']}ms"
                    })
                
                if performance_metrics.get("error_rate", 0) > 0.05:  # > 5% error rate
                    health_monitoring["performance_alerts"].append({
                        "agent": agent_role,
                        "alert_type": "high_error_rate",
                        "severity": "high",
                        "details": f"Error rate: {performance_metrics['error_rate']*100:.1f}%"
                    })
            
            # Determine overall system health
            if unhealthy_agents == 0:
                health_monitoring["overall_system_health"] = "healthy"
            elif unhealthy_agents < len(agent_roles) / 2:
                health_monitoring["overall_system_health"] = "degraded"
            else:
                health_monitoring["overall_system_health"] = "critical"
            
            return {
                "success": True,
                "health_monitoring": health_monitoring
            }
            
        except Exception as e:
            self.logger.error(f"Failed to monitor agent health: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def coordinate_multi_agent_task(self, task_definition: Dict[str, Any] = Field(..., description="Multi-agent task definition")) -> Dict[str, Any]:
        """
        Coordinate execution of tasks requiring multiple agents.
        
        Args:
            task_definition: Definition of multi-agent task
            
        Returns:
            Multi-agent coordination results
        """
        try:
            coordination_id = f"coord-{int(datetime.utcnow().timestamp())}"
            
            coordination_result = {
                "coordination_id": coordination_id,
                "task_name": task_definition.get("name", "unnamed_task"),
                "started_at": datetime.utcnow().isoformat(),
                "participating_agents": [],
                "subtasks": [],
                "coordination_status": "active",
                "overall_progress": 0.0,
                "agent_assignments": {}
            }
            
            # Break down task into subtasks
            subtasks = self._decompose_multi_agent_task(task_definition)
            coordination_result["subtasks"] = subtasks
            
            # Assign subtasks to appropriate agents
            for subtask in subtasks:
                assignment_result = self.delegate_task_to_agent(subtask)
                
                if assignment_result["success"]:
                    assigned_agent = assignment_result["delegation_result"]["selected_agent"]
                    coordination_result["agent_assignments"][subtask["id"]] = assigned_agent
                    
                    if assigned_agent not in coordination_result["participating_agents"]:
                        coordination_result["participating_agents"].append(assigned_agent)
                else:
                    coordination_result["coordination_status"] = "failed"
                    return {
                        "success": False,
                        "error": f"Failed to assign subtask {subtask['id']}",
                        "coordination_result": coordination_result
                    }
            
            # Store coordination session
            self.coordination_sessions[coordination_id] = coordination_result
            
            self.logger.info(f"Multi-agent task coordination initiated: {coordination_id}")
            
            return {
                "success": True,
                "coordination_result": coordination_result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to coordinate multi-agent task: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _initialize_agent_registry(self):
        """Initialize the agent registry with known agents."""
        # Initialize queues for each agent type
        for agent_role in AgentRole:
            self.agent_queues[agent_role.value] = TaskQueue(
                queue_id=f"queue-{agent_role.value}",
                queue_name=f"{agent_role.value.title()} Task Queue",
                agent_role=agent_role,
                max_concurrent_tasks=3  # Default capacity
            )
        
        # Define base capabilities for each agent
        self.agent_capabilities = {
            AgentRole.RT_DEV.value: {
                "primary_functions": ["code_generation", "infrastructure_orchestration", "ci_pipeline_management"],
                "supported_languages": ["python", "rust", "go", "terraform", "docker"],
                "integration_platforms": ["mcp_nexus", "rtpi_pen"],
                "specializations": ["devops", "automation", "infrastructure_as_code"]
            },
            AgentRole.BUG_HUNTER.value: {
                "primary_functions": ["vulnerability_scanning", "web_testing", "security_analysis", "report_generation"],
                "supported_tools": ["nmap", "nikto", "sqlmap", "custom_scanners"],
                "integration_platforms": ["attack_node", "rtpi_pen"],
                "specializations": ["web_security", "network_security", "penetration_testing"]
            },
            AgentRole.BURPSUITE_OPERATOR.value: {
                "primary_functions": ["web_scanning", "api_testing", "vulnerability_assessment"],
                "supported_tools": ["burpsuite_professional", "burpsuite_enterprise"],
                "integration_platforms": ["attack_node"],
                "specializations": ["web_application_security", "api_security", "manual_testing"]
            },
            AgentRole.DAEDELU5.value: {
                "primary_functions": ["infrastructure_management", "compliance_auditing", "policy_enforcement", "self_healing"],
                "supported_tools": ["terraform", "ansible", "docker", "kubernetes"],
                "integration_platforms": ["rtpi_pen", "mcp_nexus"],
                "specializations": ["infrastructure_as_code", "compliance", "automation", "security_hardening"]
            },
            AgentRole.NEXUS_KAMUY.value: {
                "primary_functions": ["workflow_orchestration", "agent_coordination", "task_scheduling", "collaboration"],
                "supported_tools": ["workflow_engine", "task_scheduler", "communication_bus"],
                "integration_platforms": ["mcp_nexus", "rtpi_pen", "attack_node"],
                "specializations": ["orchestration", "coordination", "management", "reporting"]
            }
        }
    
    def _discover_agent_capabilities(self, agent_role: str) -> Dict[str, Any]:
        """Discover capabilities of a specific agent."""
        base_capabilities = self.agent_capabilities.get(agent_role, {})
        
        # Enhanced capability discovery
        enhanced_capabilities = base_capabilities.copy()
        
        # Add dynamic capabilities based on agent status
        enhanced_capabilities["dynamic_info"] = {
            "last_seen": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "api_endpoints": self._get_agent_api_endpoints(agent_role),
            "resource_requirements": self._get_agent_resource_requirements(agent_role)
        }
        
        return enhanced_capabilities
    
    def _check_agent_availability(self, agent_role: str) -> Dict[str, Any]:
        """Check availability status of an agent."""
        # Simulate availability checking
        availability = {
            "status": "available",
            "current_load": 0.3,  # 30% utilization
            "max_capacity": 5,
            "queue_length": 2,
            "estimated_availability": datetime.utcnow().isoformat(),
            "maintenance_scheduled": False
        }
        
        # Simulate different availability states
        if agent_role == AgentRole.BURPSUITE_OPERATOR.value:
            availability["current_load"] = 0.8  # Higher load for BurpSuite
            availability["queue_length"] = 5
        
        return availability
    
    def _get_agent_performance_metrics(self, agent_role: str) -> Dict[str, Any]:
        """Get performance metrics for an agent."""
        # Simulate performance metrics
        metrics = {
            "average_response_time": 1500,  # milliseconds
            "success_rate": 0.95,
            "error_rate": 0.05,
            "throughput": 15,  # tasks per hour
            "uptime_percentage": 99.5,
            "last_performance_check": datetime.utcnow().isoformat()
        }
        
        # Simulate different performance characteristics
        if agent_role == AgentRole.RT_DEV.value:
            metrics["average_response_time"] = 2000  # Code generation takes longer
            metrics["throughput"] = 8
        elif agent_role == AgentRole.BUG_HUNTER.value:
            metrics["average_response_time"] = 5000  # Scanning takes longer
            metrics["throughput"] = 5
        
        return metrics
    
    def _find_suitable_agents(self, task: Dict[str, Any], criteria: Dict[str, Any]) -> List[str]:
        """Find agents suitable for a given task."""
        suitable_agents = []
        task_type = task.get("task_type", "")
        required_capabilities = criteria.get("required_capabilities", [])
        
        for agent_role, capabilities in self.agent_capabilities.items():
            agent_functions = capabilities.get("primary_functions", [])
            agent_specializations = capabilities.get("specializations", [])
            
            # Check if agent can handle the task type
            task_match = False
            
            # Basic task type matching
            if task_type in agent_functions:
                task_match = True
            
            # Specialization matching
            for spec in agent_specializations:
                if spec in task_type or task_type in spec:
                    task_match = True
                    break
            
            # Required capability matching
            if required_capabilities:
                capability_match = any(cap in agent_functions for cap in required_capabilities)
                task_match = task_match and capability_match
            
            if task_match:
                # Check availability
                availability = self._check_agent_availability(agent_role)
                if availability["status"] == "available" and availability["current_load"] < 0.9:
                    suitable_agents.append(agent_role)
        
        return suitable_agents
    
    def _select_optimal_agent(self, suitable_agents: List[str], task: Dict[str, Any], 
                            criteria: Dict[str, Any]) -> str:
        """Select the optimal agent from suitable candidates."""
        if len(suitable_agents) == 1:
            return suitable_agents[0]
        
        # Scoring system for agent selection
        agent_scores = {}
        
        for agent in suitable_agents:
            score = 0.0
            
            # Factor 1: Current load (lower is better)
            availability = self._check_agent_availability(agent)
            load_score = (1.0 - availability["current_load"]) * 30
            score += load_score
            
            # Factor 2: Performance metrics
            performance = self._get_agent_performance_metrics(agent)
            success_rate_score = performance["success_rate"] * 40
            response_time_score = max(0, (5000 - performance["average_response_time"]) / 5000) * 20
            score += success_rate_score + response_time_score
            
            # Factor 3: Specialization match
            capabilities = self.agent_capabilities.get(agent, {})
            specializations = capabilities.get("specializations", [])
            task_type = task.get("task_type", "")
            
            for spec in specializations:
                if spec in task_type:
                    score += 10  # Bonus for specialization match
            
            agent_scores[agent] = score
        
        # Return agent with highest score
        return max(agent_scores, key=agent_scores.get)
    
    def _delegate_to_agent(self, agent_role: str, task: Dict[str, Any]) -> bool:
        """Delegate task to specific agent."""
        try:
            # Add task to agent's queue
            if agent_role in self.agent_queues:
                queue = self.agent_queues[agent_role]
                queue.add_task(task["id"])
                
                self.logger.info(f"Task {task['id']} added to {agent_role} queue")
                return True
            else:
                self.logger.error(f"No queue found for agent {agent_role}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to delegate to agent {agent_role}: {str(e)}")
            return False
    
    def _get_agent_queue_position(self, agent_role: str, task_id: str) -> int:
        """Get position of task in agent's queue."""
        if agent_role in self.agent_queues:
            queue = self.agent_queues[agent_role]
            try:
                return queue.pending_tasks.index(task_id) + 1
            except ValueError:
                return 0  # Task not in pending queue
        return 0
    
    def _decompose_multi_agent_task(self, task_definition: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Decompose a complex task into subtasks for different agents."""
        task_type = task_definition.get("type", "")
        
        if task_type == "comprehensive_security_assessment":
            return [
                {
                    "id": f"subtask-recon-{int(datetime.utcnow().timestamp())}",
                    "name": "Target Reconnaissance",
                    "task_type": "reconnaissance",
                    "priority": "high",
                    "agent_preference": AgentRole.BUG_HUNTER.value
                },
                {
                    "id": f"subtask-scan-{int(datetime.utcnow().timestamp())}",
                    "name": "Vulnerability Scanning",
                    "task_type": "vulnerability_scanning",
                    "priority": "high",
                    "agent_preference": AgentRole.BURPSUITE_OPERATOR.value
                },
                {
                    "id": f"subtask-compliance-{int(datetime.utcnow().timestamp())}",
                    "name": "Compliance Review",
                    "task_type": "compliance_audit",
                    "priority": "medium",
                    "agent_preference": AgentRole.DAEDELU5.value
                },
                {
                    "id": f"subtask-report-{int(datetime.utcnow().timestamp())}",
                    "name": "Report Generation",
                    "task_type": "reporting",
                    "priority": "low",
                    "agent_preference": AgentRole.NEXUS_KAMUY.value
                }
            ]
        
        # Default decomposition for unknown task types
        return [
            {
                "id": f"subtask-generic-{int(datetime.utcnow().timestamp())}",
                "name": "Generic Task Execution",
                "task_type": task_type,
                "priority": "medium",
                "agent_preference": None
            }
        ]
    
    def _apply_even_distribution_strategy(self) -> List[Dict[str, Any]]:
        """Apply even distribution load balancing strategy."""
        redistributed = []
        
        # Calculate average load
        total_pending = sum(len(queue.pending_tasks) for queue in self.agent_queues.values())
        agent_count = len(self.agent_queues)
        target_load = total_pending // agent_count if agent_count > 0 else 0
        
        # Redistribute tasks from overloaded agents
        for agent_role, queue in self.agent_queues.items():
            if len(queue.pending_tasks) > target_load + 1:
                excess_tasks = len(queue.pending_tasks) - target_load
                
                # Find agents with lower load
                for target_agent, target_queue in self.agent_queues.items():
                    if len(target_queue.pending_tasks) < target_load and excess_tasks > 0:
                        # Move task (simulated)
                        redistributed.append({
                            "task_id": f"task-{excess_tasks}",
                            "from_agent": agent_role,
                            "to_agent": target_agent,
                            "reason": "load_balancing"
                        })
                        excess_tasks -= 1
        
        return redistributed
    
    def _apply_capability_based_strategy(self) -> List[Dict[str, Any]]:
        """Apply capability-based load balancing strategy."""
        # This would analyze task requirements and reassign based on agent capabilities
        return []  # Simplified for demonstration
    
    def _apply_priority_based_strategy(self) -> List[Dict[str, Any]]:
        """Apply priority-based load balancing strategy."""
        # This would prioritize high-priority tasks and assign to best available agents
        return []  # Simplified for demonstration
    
    def _check_agent_health(self, agent_role: str) -> Dict[str, Any]:
        """Check health status of a specific agent."""
        # Simulate health checking
        health_status = {
            "agent_role": agent_role,
            "status": "healthy",
            "last_health_check": datetime.utcnow().isoformat(),
            "issues": [],
            "performance_metrics": self._get_agent_performance_metrics(agent_role),
            "resource_usage": {
                "cpu_percentage": 25.0,
                "memory_percentage": 45.0,
                "disk_usage": 60.0
            }
        }
        
        # Simulate some health issues for demonstration
        if agent_role == AgentRole.BURPSUITE_OPERATOR.value:
            health_status["resource_usage"]["memory_percentage"] = 85.0
            if health_status["resource_usage"]["memory_percentage"] > 80:
                health_status["status"] = "degraded"
                health_status["severity"] = "medium"
                health_status["issues"].append("High memory usage detected")
        
        return health_status
    
    def _get_agent_api_endpoints(self, agent_role: str) -> List[str]:
        """Get API endpoints for an agent."""
        endpoint_map = {
            AgentRole.RT_DEV.value: ["/api/v1/generate", "/api/v1/deploy", "/api/v1/orchestrate"],
            AgentRole.BUG_HUNTER.value: ["/api/v1/scan", "/api/v1/analyze", "/api/v1/report"],
            AgentRole.BURPSUITE_OPERATOR.value: ["/api/v1/scan", "/api/v1/assess", "/api/v1/process"],
            AgentRole.DAEDELU5.value: ["/api/v1/audit", "/api/v1/enforce", "/api/v1/heal"],
            AgentRole.NEXUS_KAMUY.value: ["/api/v1/orchestrate", "/api/v1/coordinate", "/api/v1/schedule"]
        }
        
        return endpoint_map.get(agent_role, [])
    
    def _get_agent_resource_requirements(self, agent_role: str) -> Dict[str, Any]:
        """Get resource requirements for an agent."""
        requirements_map = {
            AgentRole.RT_DEV.value: {
                "cpu_cores": 2,
                "memory_gb": 4,
                "disk_gb": 20,
                "network_bandwidth": "100mbps"
            },
            AgentRole.BUG_HUNTER.value: {
                "cpu_cores": 4,
                "memory_gb": 8,
                "disk_gb": 50,
                "network_bandwidth": "1gbps"
            },
            AgentRole.BURPSUITE_OPERATOR.value: {
                "cpu_cores": 8,
                "memory_gb": 16,
                "disk_gb": 100,
                "network_bandwidth": "1gbps"
            },
            AgentRole.DAEDELU5.value: {
                "cpu_cores": 4,
                "memory_gb": 8,
                "disk_gb": 100,
                "network_bandwidth": "500mbps"
            },
            AgentRole.NEXUS_KAMUY.value: {
                "cpu_cores": 2,
                "memory_gb": 4,
                "disk_gb": 20,
                "network_bandwidth": "500mbps"
            }
        }
        
        return requirements_map.get(agent_role, {})
