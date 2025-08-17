"""
Infrastructure as Code Manager for cybersecurity AI workflow integration.

This tool creates and manages infrastructure as code with support for
Terraform, Docker Compose, and Kubernetes deployments.
"""

import os
import json
import yaml
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ..shared.api_clients.rtpi_pen_client import RTPIPenClient
from ..shared.data_models.platform_models import DockerContainer


class InfrastructureAsCodeManager:
    """
    Advanced infrastructure as code management for cybersecurity deployments.
    Provides Terraform, Docker Compose, and Kubernetes configuration generation.
    """
    
    def __init__(self):
        """Initialize the Infrastructure as Code Manager."""
        self.rtpi_client = RTPIPenClient("http://localhost:8080")  # Default rtpi-pen endpoint
        self.logger = logging.getLogger("InfrastructureAsCodeManager")
        self.deployment_history = []
    
    def generate_terraform_modules(self, infrastructure_requirements: Dict[str, Any] = Field(..., description="Infrastructure requirements")) -> Dict[str, Any]:
        """
        Generate modular Terraform configurations for security infrastructure.
        
        Args:
            infrastructure_requirements: Infrastructure specification
            
        Returns:
            Generated Terraform modules and configurations
        """
        try:
            modules = {}
            
            # Generate main configuration
            main_tf = self._generate_terraform_main(infrastructure_requirements)
            modules["main.tf"] = main_tf
            
            # Generate variables
            variables_tf = self._generate_terraform_variables(infrastructure_requirements)
            modules["variables.tf"] = variables_tf
            
            # Generate outputs
            outputs_tf = self._generate_terraform_outputs(infrastructure_requirements)
            modules["outputs.tf"] = outputs_tf
            
            # Generate provider configuration
            providers_tf = self._generate_terraform_providers(infrastructure_requirements)
            modules["providers.tf"] = providers_tf
            
            # Generate security-specific modules
            if infrastructure_requirements.get("security_tools"):
                security_module = self._generate_security_tools_module(infrastructure_requirements["security_tools"])
                modules["modules/security/main.tf"] = security_module
            
            # Generate monitoring module
            if infrastructure_requirements.get("monitoring"):
                monitoring_module = self._generate_monitoring_module(infrastructure_requirements["monitoring"])
                modules["modules/monitoring/main.tf"] = monitoring_module
            
            return {
                "success": True,
                "modules": modules,
                "module_count": len(modules),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate Terraform modules: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def build_docker_compose_environment(self, services: List[Dict[str, Any]] = Field(..., description="List of services"), 
                                       network_config: Dict[str, Any] = Field(..., description="Network configuration")) -> Dict[str, Any]:
        """
        Build Docker Compose environment for security services.
        
        Args:
            services: List of service configurations
            network_config: Network configuration
            
        Returns:
            Generated Docker Compose configuration
        """
        try:
            compose_config = {
                "version": "3.8",
                "services": {},
                "networks": self._generate_docker_networks(network_config),
                "volumes": {},
                "secrets": {}
            }
            
            # Process each service
            for service in services:
                service_name = service.get("name")
                if not service_name:
                    continue
                
                service_config = {
                    "image": service.get("image", f"{service_name}:latest"),
                    "container_name": f"rtpi_{service_name}",
                    "restart": service.get("restart", "unless-stopped"),
                    "networks": service.get("networks", ["default"]),
                    "environment": service.get("environment", {}),
                    "volumes": service.get("volumes", []),
                    "ports": service.get("ports", [])
                }
                
                # Add health checks for security services
                if service.get("health_check"):
                    service_config["healthcheck"] = {
                        "test": service["health_check"].get("test", ["CMD", "curl", "-f", "http://localhost/health"]),
                        "interval": service["health_check"].get("interval", "30s"),
                        "timeout": service["health_check"].get("timeout", "10s"),
                        "retries": service["health_check"].get("retries", 3)
                    }
                
                # Add security-specific configurations
                if service.get("security_opts"):
                    service_config["security_opt"] = service["security_opts"]
                
                if service.get("privileged"):
                    service_config["privileged"] = True
                
                compose_config["services"][service_name] = service_config
                
                # Add volumes if needed
                for volume in service.get("named_volumes", []):
                    compose_config["volumes"][volume] = {}
            
            # Add common security volumes
            compose_config["volumes"].update({
                "rtpi_data": {},
                "rtpi_logs": {},
                "rtpi_config": {}
            })
            
            return {
                "success": True,
                "docker_compose": compose_config,
                "yaml_output": yaml.dump(compose_config, default_flow_style=False),
                "service_count": len(services)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to build Docker Compose environment: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def deploy_infrastructure_stack(self, stack_definition: Dict[str, Any] = Field(..., description="Stack definition")) -> Dict[str, Any]:
        """
        Deploy complete infrastructure stack.
        
        Args:
            stack_definition: Infrastructure stack definition
            
        Returns:
            Deployment result and status
        """
        try:
            stack_name = stack_definition.get("name", f"security-stack-{int(datetime.utcnow().timestamp())}")
            deployment_type = stack_definition.get("type", "docker-compose")
            
            deployment = {
                "stack_name": stack_name,
                "type": deployment_type,
                "started_at": datetime.utcnow().isoformat(),
                "status": "deploying",
                "components": [],
                "deployment_id": f"deploy-{int(datetime.utcnow().timestamp())}"
            }
            
            if deployment_type == "docker-compose":
                result = self._deploy_docker_compose_stack(stack_definition)
                deployment.update(result)
            elif deployment_type == "terraform":
                result = self._deploy_terraform_stack(stack_definition)
                deployment.update(result)
            elif deployment_type == "kubernetes":
                result = self._deploy_kubernetes_stack(stack_definition)
                deployment.update(result)
            else:
                return {"success": False, "error": f"Unsupported deployment type: {deployment_type}"}
            
            deployment["completed_at"] = datetime.utcnow().isoformat()
            deployment["status"] = "deployed" if result.get("success") else "failed"
            
            # Store deployment history
            self.deployment_history.append(deployment)
            
            return {
                "success": result.get("success", False),
                "deployment": deployment
            }
            
        except Exception as e:
            self.logger.error(f"Failed to deploy infrastructure stack: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def validate_infrastructure_template(self, template: Dict[str, Any], template_type: str) -> Dict[str, Any]:
        """Validate infrastructure template for correctness."""
        try:
            validation = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "template_type": template_type
            }
            
            if template_type == "docker-compose":
                validation.update(self._validate_docker_compose(template))
            elif template_type == "terraform":
                validation.update(self._validate_terraform(template))
            elif template_type == "kubernetes":
                validation.update(self._validate_kubernetes(template))
            
            return {"success": True, "validation": validation}
            
        except Exception as e:
            self.logger.error(f"Failed to validate template: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _generate_terraform_main(self, requirements: Dict[str, Any]) -> str:
        """Generate main Terraform configuration."""
        terraform_main = f"""
# Generated Terraform configuration for cybersecurity infrastructure
# Generated at: {datetime.utcnow().isoformat()}

terraform {{
  required_version = ">= 1.0"
  required_providers {{
    docker = {{
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }}
    local = {{
      source  = "hashicorp/local"
      version = "~> 2.0"
    }}
  }}
}}

# Security infrastructure resources
resource "docker_network" "security_network" {{
  name = "rtpi-security"
  driver = "bridge"
  
  ipam_config {{
    subnet = var.network_subnet
    gateway = var.network_gateway
  }}
}}

# Data volumes
resource "docker_volume" "security_data" {{
  name = "rtpi-security-data"
}}

resource "docker_volume" "security_logs" {{
  name = "rtpi-security-logs"
}}
"""
        
        # Add service configurations
        if "services" in requirements:
            for service in requirements["services"]:
                terraform_main += f"""
resource "docker_container" "{service['name']}" {{
  image = var.{service['name']}_image
  name  = "rtpi_{service['name']}"
  
  networks_advanced {{
    name = docker_network.security_network.name
  }}
  
  restart = "unless-stopped"
  
  # Health check
  healthcheck {{
    test = {service.get('health_check', ['CMD', 'curl', '-f', 'http://localhost/health'])}
    interval = "30s"
    timeout = "10s"
    retries = 3
  }}
}}
"""
        
        return terraform_main
    
    def _generate_terraform_variables(self, requirements: Dict[str, Any]) -> str:
        """Generate Terraform variables."""
        variables = """
# Terraform variables for security infrastructure

variable "network_subnet" {
  description = "Subnet for security network"
  type        = string
  default     = "172.20.0.0/16"
}

variable "network_gateway" {
  description = "Gateway for security network"
  type        = string
  default     = "172.20.0.1"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}
"""
        
        # Add service-specific variables
        if "services" in requirements:
            for service in requirements["services"]:
                variables += f"""
variable "{service['name']}_image" {{
  description = "Docker image for {service['name']}"
  type        = string
  default     = "{service.get('image', service['name'] + ':latest')}"
}}
"""
        
        return variables
    
    def _generate_terraform_outputs(self, requirements: Dict[str, Any]) -> str:
        """Generate Terraform outputs."""
        return """
# Terraform outputs

output "network_id" {
  description = "Security network ID"
  value       = docker_network.security_network.id
}

output "network_name" {
  description = "Security network name"
  value       = docker_network.security_network.name
}

output "deployment_timestamp" {
  description = "Deployment timestamp"
  value       = timestamp()
}
"""
    
    def _generate_terraform_providers(self, requirements: Dict[str, Any]) -> str:
        """Generate Terraform provider configuration."""
        return """
# Terraform providers configuration

provider "docker" {
  host = "unix:///var/run/docker.sock"
}

provider "local" {
  # Local provider for file operations
}
"""
    
    def _generate_security_tools_module(self, security_tools: Dict[str, Any]) -> str:
        """Generate security tools Terraform module."""
        module = """
# Security tools module

# BurpSuite Professional container
resource "docker_container" "burpsuite" {
  count = var.enable_burpsuite ? 1 : 0
  image = "portswigger/burp-suite-professional:latest"
  name  = "rtpi_burpsuite"
  
  ports {
    internal = 1337
    external = var.burpsuite_port
  }
  
  environment = [
    "BURP_LICENSE_KEY=${var.burpsuite_license}"
  ]
}

# Empire C2 container
resource "docker_container" "empire" {
  count = var.enable_empire ? 1 : 0
  image = "bcsecurity/empire:latest"
  name  = "rtpi_empire"
  
  ports {
    internal = 1337
    external = var.empire_port
  }
}
"""
        return module
    
    def _generate_monitoring_module(self, monitoring: Dict[str, Any]) -> str:
        """Generate monitoring Terraform module."""
        return """
# Monitoring module

resource "docker_container" "prometheus" {
  image = "prom/prometheus:latest"
  name  = "rtpi_prometheus"
  
  ports {
    internal = 9090
    external = var.prometheus_port
  }
  
  volumes {
    host_path = "/opt/rtpi/prometheus"
    container_path = "/etc/prometheus"
  }
}

resource "docker_container" "grafana" {
  image = "grafana/grafana:latest"
  name  = "rtpi_grafana"
  
  ports {
    internal = 3000
    external = var.grafana_port
  }
  
  environment = [
    "GF_SECURITY_ADMIN_PASSWORD=${var.grafana_admin_password}"
  ]
}
"""
    
    def _generate_docker_networks(self, network_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Docker network configuration."""
        networks = {
            "default": {
                "driver": "bridge"
            }
        }
        
        if "security_network" in network_config:
            networks["security"] = {
                "driver": "bridge",
                "ipam": {
                    "config": [
                        {
                            "subnet": network_config["security_network"].get("subnet", "172.20.0.0/16")
                        }
                    ]
                }
            }
        
        return networks
    
    def _deploy_docker_compose_stack(self, stack_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy Docker Compose stack."""
        try:
            # In a real implementation, this would execute docker-compose commands
            # For now, simulate deployment
            components = []
            
            for service_name in stack_definition.get("services", {}):
                components.append({
                    "name": service_name,
                    "type": "docker_container",
                    "status": "running"
                })
            
            return {
                "success": True,
                "components": components,
                "deployment_method": "docker-compose"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _deploy_terraform_stack(self, stack_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy Terraform stack."""
        try:
            # Simulate Terraform deployment
            return {
                "success": True,
                "components": [],
                "deployment_method": "terraform"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _deploy_kubernetes_stack(self, stack_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy Kubernetes stack."""
        try:
            # Simulate Kubernetes deployment
            return {
                "success": True,
                "components": [],
                "deployment_method": "kubernetes"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _validate_docker_compose(self, template: Dict[str, Any]) -> Dict[str, List]:
        """Validate Docker Compose template."""
        errors = []
        warnings = []
        
        if "version" not in template:
            errors.append("Missing Docker Compose version")
        
        if "services" not in template:
            errors.append("No services defined")
        else:
            for service_name, service_config in template["services"].items():
                if "image" not in service_config:
                    errors.append(f"Service {service_name} missing image")
        
        return {"errors": errors, "warnings": warnings}
    
    def _validate_terraform(self, template: Dict[str, Any]) -> Dict[str, List]:
        """Validate Terraform template."""
        # Basic validation - in real implementation would use terraform validate
        return {"errors": [], "warnings": []}
    
    def _validate_kubernetes(self, template: Dict[str, Any]) -> Dict[str, List]:
        """Validate Kubernetes template."""
        # Basic validation - in real implementation would use kubectl dry-run
        return {"errors": [], "warnings": []}
