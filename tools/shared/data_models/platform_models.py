"""
Platform-specific data models for cybersecurity AI workflow integration.

This module contains data structures specific to MCP-Nexus, rtpi-pen, and attack-node platforms.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator

from .base_models import ConnectionConfig, IdentifiedModel, HealthStatus


class MCPNexusConnection(ConnectionConfig):
    """Connection configuration for MCP-Nexus platform."""
    
    client_certificate: Optional[str] = Field(default=None, description="Client certificate for mTLS authentication")
    client_key: Optional[str] = Field(default=None, description="Client private key for mTLS authentication")
    websocket_endpoint: Optional[str] = Field(default=None, description="WebSocket endpoint for real-time communication")
    mcp_server_config: Dict[str, Any] = Field(default_factory=dict, description="MCP server configuration")
    edge_device_id: Optional[str] = Field(default=None, description="Edge device identifier")
    auto_restart_limit: int = Field(default=5, description="Auto-restart attempt limit")
    
    @validator('websocket_endpoint')
    def validate_websocket_endpoint(cls, v):
        if v and not (v.startswith('ws://') or v.startswith('wss://')):
            raise ValueError('WebSocket endpoint must start with ws:// or wss://')
        return v


class RTPIPenConnection(ConnectionConfig):
    """Connection configuration for rtpi-pen platform."""
    
    kasm_workspace_url: Optional[str] = Field(default=None, description="Kasm workspace URL")
    empire_api_endpoint: Optional[str] = Field(default=None, description="PowerShell Empire API endpoint")
    empire_api_token: Optional[str] = Field(default=None, description="PowerShell Empire API token")
    portainer_endpoint: Optional[str] = Field(default=None, description="Portainer management endpoint")
    postgres_config: Dict[str, Any] = Field(default_factory=dict, description="PostgreSQL configuration")
    redis_config: Dict[str, Any] = Field(default_factory=dict, description="Redis configuration")
    nginx_config: Dict[str, Any] = Field(default_factory=dict, description="Nginx configuration")
    self_healing_enabled: bool = Field(default=True, description="Enable self-healing capabilities")
    
    @validator('empire_api_endpoint')
    def validate_empire_endpoint(cls, v):
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('Empire API endpoint must be a valid HTTP/HTTPS URL')
        return v


class AttackNodeConnection(ConnectionConfig):
    """Connection configuration for attack-node platform."""
    
    kali_environment_url: Optional[str] = Field(default=None, description="Kali Linux environment URL")
    burp_suite_api_key: Optional[str] = Field(default=None, description="Burp Suite Professional API key")
    burp_suite_endpoint: Optional[str] = Field(default=None, description="Burp Suite API endpoint")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic Claude API key")
    docker_config: Dict[str, Any] = Field(default_factory=dict, description="Docker environment configuration")
    operation_tracking: bool = Field(default=True, description="Enable operation tracking")
    
    @validator('burp_suite_endpoint')
    def validate_burp_endpoint(cls, v):
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('Burp Suite endpoint must be a valid HTTP/HTTPS URL')
        return v


class MCPServerProcess(IdentifiedModel):
    """MCP server process information."""
    
    command: str = Field(..., description="Command used to start the server")
    environment_vars: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    working_directory: Optional[str] = Field(default=None, description="Working directory")
    process_id: Optional[int] = Field(default=None, description="Process ID")
    status: str = Field(default="stopped", description="Process status")
    restart_count: int = Field(default=0, description="Number of restarts")
    last_restart: Optional[datetime] = Field(default=None, description="Last restart time")
    auto_restart: bool = Field(default=True, description="Enable auto-restart")
    health_check_url: Optional[str] = Field(default=None, description="Health check endpoint")
    
    def restart_process(self):
        """Mark process as restarted."""
        self.restart_count += 1
        self.last_restart = datetime.utcnow()
        self.status = "restarting"


class EdgeDevice(IdentifiedModel):
    """Edge device registration for MCP-Nexus."""
    
    device_type: str = Field(..., description="Type of edge device")
    capabilities: List[str] = Field(default_factory=list, description="Device capabilities")
    certificate_fingerprint: Optional[str] = Field(default=None, description="Certificate fingerprint")
    is_blocked: bool = Field(default=False, description="Whether device is blocked")
    last_seen: Optional[datetime] = Field(default=None, description="Last communication time")
    health_status: Optional[HealthStatus] = Field(default=None, description="Device health status")
    resource_usage: Dict[str, Union[int, float]] = Field(default_factory=dict, description="Resource usage metrics")
    
    def block_device(self, reason: str):
        """Block the device."""
        self.is_blocked = True
        self.metadata["block_reason"] = reason
        self.metadata["blocked_at"] = datetime.utcnow().isoformat()
    
    def unblock_device(self):
        """Unblock the device."""
        self.is_blocked = False
        self.metadata.pop("block_reason", None)
        self.metadata["unblocked_at"] = datetime.utcnow().isoformat()


class KasmWorkspace(IdentifiedModel):
    """Kasm workspace information."""
    
    workspace_type: str = Field(..., description="Type of workspace")
    image: str = Field(..., description="Docker image used")
    url: str = Field(..., description="Workspace access URL")
    status: str = Field(default="stopped", description="Workspace status")
    user_id: Optional[str] = Field(default=None, description="Associated user ID")
    session_id: Optional[str] = Field(default=None, description="Current session ID")
    resource_limits: Dict[str, Any] = Field(default_factory=dict, description="Resource limits")
    environment_variables: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    
    def start_workspace(self):
        """Start the workspace."""
        self.status = "starting"
        self.update_timestamp()
    
    def stop_workspace(self):
        """Stop the workspace."""
        self.status = "stopping"
        self.session_id = None
        self.update_timestamp()


class EmpireAgent(IdentifiedModel):
    """PowerShell Empire agent information."""
    
    agent_id: str = Field(..., description="Empire agent ID")
    hostname: str = Field(..., description="Target hostname")
    username: str = Field(..., description="Username on target")
    operating_system: str = Field(..., description="Target operating system")
    process_name: str = Field(..., description="Process name")
    process_id: int = Field(..., description="Process ID")
    language: str = Field(default="powershell", description="Agent language")
    delay: int = Field(default=60, description="Check-in delay in seconds")
    jitter: float = Field(default=0.0, description="Jitter percentage")
    external_ip: Optional[str] = Field(default=None, description="External IP address")
    internal_ip: Optional[str] = Field(default=None, description="Internal IP address")
    last_seen: Optional[datetime] = Field(default=None, description="Last check-in time")
    is_elevated: bool = Field(default=False, description="Whether agent has elevated privileges")
    
    def update_last_seen(self):
        """Update last seen timestamp."""
        self.last_seen = datetime.utcnow()


class DockerContainer(IdentifiedModel):
    """Docker container information."""
    
    container_id: str = Field(..., description="Docker container ID")
    image: str = Field(..., description="Container image")
    command: Optional[str] = Field(default=None, description="Container command")
    status: str = Field(..., description="Container status")
    ports: Dict[str, str] = Field(default_factory=dict, description="Port mappings")
    volumes: Dict[str, str] = Field(default_factory=dict, description="Volume mappings")
    environment: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    network_mode: Optional[str] = Field(default=None, description="Network mode")
    restart_policy: str = Field(default="unless-stopped", description="Restart policy")
    health_check: Optional[Dict[str, Any]] = Field(default=None, description="Health check configuration")
    
    def is_running(self) -> bool:
        """Check if container is running."""
        return self.status.lower() == "running"
    
    def is_healthy(self) -> bool:
        """Check if container is healthy."""
        if not self.health_check:
            return self.is_running()
        return self.status.lower() == "running" and self.health_check.get("status") == "healthy"


class SelfHealingRule(IdentifiedModel):
    """Self-healing rule configuration."""
    
    service_name: str = Field(..., description="Service name to monitor")
    trigger_conditions: List[Dict[str, Any]] = Field(..., description="Conditions that trigger healing")
    healing_actions: List[Dict[str, Any]] = Field(..., description="Actions to take when triggered")
    cooldown_period: int = Field(default=300, description="Cooldown period in seconds")
    max_attempts: int = Field(default=3, description="Maximum healing attempts")
    success_criteria: List[Dict[str, Any]] = Field(default_factory=list, description="Criteria to determine success")
    notification_settings: Dict[str, Any] = Field(default_factory=dict, description="Notification configuration")
    is_enabled: bool = Field(default=True, description="Whether rule is enabled")
    
    def trigger_healing(self) -> Dict[str, Any]:
        """Trigger healing action."""
        return {
            "rule_id": self.id,
            "service": self.service_name,
            "triggered_at": datetime.utcnow().isoformat(),
            "actions": self.healing_actions
        }


class RedTeamOperation(IdentifiedModel):
    """Red team operation information."""
    
    operation_name: str = Field(..., description="Operation name")
    targets: List[str] = Field(..., description="Target systems or domains")
    objectives: List[str] = Field(..., description="Operation objectives")
    methodology: str = Field(..., description="Testing methodology")
    start_date: datetime = Field(..., description="Operation start date")
    end_date: Optional[datetime] = Field(default=None, description="Operation end date")
    team_members: List[str] = Field(default_factory=list, description="Team member IDs")
    tools_used: List[str] = Field(default_factory=list, description="Tools and techniques used")
    findings: List[str] = Field(default_factory=list, description="Security findings")
    status: str = Field(default="planning", description="Operation status")
    risk_level: str = Field(default="medium", description="Risk level assessment")
    
    def add_finding(self, finding_id: str):
        """Add a security finding to the operation."""
        if finding_id not in self.findings:
            self.findings.append(finding_id)
            self.update_timestamp()
    
    def complete_operation(self):
        """Mark operation as completed."""
        self.status = "completed"
        self.end_date = datetime.utcnow()
        self.update_timestamp()


class AIIntegrationConfig(BaseModel):
    """AI service integration configuration."""
    
    provider: str = Field(..., description="AI provider (openai, anthropic, etc.)")
    api_key: str = Field(..., description="API key for the service")
    model: str = Field(..., description="Model to use")
    api_endpoint: Optional[str] = Field(default=None, description="Custom API endpoint")
    max_tokens: int = Field(default=4000, description="Maximum tokens per request")
    temperature: float = Field(default=0.7, description="Generation temperature")
    timeout: int = Field(default=60, description="Request timeout in seconds")
    rate_limit: Dict[str, int] = Field(default_factory=dict, description="Rate limiting configuration")
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError('Temperature must be between 0.0 and 2.0')
        return v
    
    @validator('provider')
    def validate_provider(cls, v):
        allowed_providers = ['openai', 'anthropic', 'azure', 'custom']
        if v not in allowed_providers:
            raise ValueError(f'Provider must be one of: {", ".join(allowed_providers)}')
        return v


class PlatformConfig(IdentifiedModel):
    """Overall platform configuration."""
    
    platform_name: str = Field(..., description="Platform name")
    platform_type: str = Field(..., description="Platform type")
    environment: str = Field(default="production", description="Environment (dev, staging, production)")
    mcp_nexus: Optional[MCPNexusConnection] = Field(default=None, description="MCP-Nexus connection config")
    rtpi_pen: Optional[RTPIPenConnection] = Field(default=None, description="rtpi-pen connection config")
    attack_node: Optional[AttackNodeConnection] = Field(default=None, description="attack-node connection config")
    ai_integrations: List[AIIntegrationConfig] = Field(default_factory=list, description="AI service configurations")
    security_settings: Dict[str, Any] = Field(default_factory=dict, description="Security configuration")
    logging_config: Dict[str, Any] = Field(default_factory=dict, description="Logging configuration")
    monitoring_config: Dict[str, Any] = Field(default_factory=dict, description="Monitoring configuration")
    backup_config: Dict[str, Any] = Field(default_factory=dict, description="Backup configuration")
    is_active: bool = Field(default=True, description="Whether platform is active")
    
    @validator('environment')
    def validate_environment(cls, v):
        allowed_environments = ['dev', 'staging', 'production', 'test']
        if v not in allowed_environments:
            raise ValueError(f'Environment must be one of: {", ".join(allowed_environments)}')
        return v
    
    @validator('platform_type')
    def validate_platform_type(cls, v):
        allowed_types = ['mcp_nexus', 'rtpi_pen', 'attack_node', 'hybrid']
        if v not in allowed_types:
            raise ValueError(f'Platform type must be one of: {", ".join(allowed_types)}')
        return v
    
    def add_ai_integration(self, config: AIIntegrationConfig):
        """Add AI service integration."""
        self.ai_integrations.append(config)
        self.update_timestamp()
    
    def activate_platform(self):
        """Activate the platform."""
        self.is_active = True
        self.metadata["activated_at"] = datetime.utcnow().isoformat()
        self.update_timestamp()
    
    def deactivate_platform(self, reason: str):
        """Deactivate the platform."""
        self.is_active = False
        self.metadata["deactivation_reason"] = reason
        self.metadata["deactivated_at"] = datetime.utcnow().isoformat()
        self.update_timestamp()
