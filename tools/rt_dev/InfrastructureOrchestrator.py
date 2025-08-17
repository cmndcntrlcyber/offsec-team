import os
import json
import yaml
import subprocess
import time
from typing import Dict, List, Optional, Tuple, Union, Any
from pydantic import BaseModel, Field

class InfrastructureOrchestrator:
    """
    A tool for managing infrastructure automation workflows.
    Provides capabilities for generating, deploying, and validating infrastructure code.
    """
    
    def __init__(self):
        self.terraform_templates = {
            "aws": {
                "vpc": self._get_aws_vpc_template(),
                "ec2": self._get_aws_ec2_template(),
                "rds": self._get_aws_rds_template(),
                "s3": self._get_aws_s3_template()
            },
            "azure": {
                "resource_group": self._get_azure_resource_group_template(),
                "virtual_network": self._get_azure_vnet_template(),
                "vm": self._get_azure_vm_template(),
                "storage": self._get_azure_storage_template()
            },
            "gcp": {
                "network": self._get_gcp_network_template(),
                "compute": self._get_gcp_compute_template(),
                "storage": self._get_gcp_storage_template(),
                "cloud_sql": self._get_gcp_cloudsql_template()
            }
        }
        
        self.docker_compose_templates = {
            "basic": self._get_basic_compose_template(),
            "web": self._get_web_compose_template(),
            "data": self._get_data_compose_template(),
            "security": self._get_security_compose_template()
        }
        
        self.deployment_history = {}
    
    def generate_terraform_configuration(self, infrastructure_spec: Dict[str, Any] = Field(..., description="Infrastructure specification")) -> str:
        """
        Create Terraform configurations from specifications.
        
        Args:
            infrastructure_spec: Dictionary containing infrastructure specifications
                Required keys:
                - provider: Cloud provider (aws, azure, gcp)
                - resources: List of resources to create
                - variables: Dictionary of variables
                - outputs: List of outputs to generate
            
        Returns:
            Generated Terraform configuration as a string
        """
        # Validate required fields
        required_keys = ["provider", "resources"]
        for key in required_keys:
            if key not in infrastructure_spec:
                return f"Error: Missing required key '{key}' in infrastructure specification"
        
        provider = infrastructure_spec["provider"].lower()
        if provider not in ["aws", "azure", "gcp"]:
            return f"Error: Unsupported provider '{provider}'. Supported providers: aws, azure, gcp"
        
        # Build Terraform configuration
        tf_config = []
        
        # Add provider block
        provider_block = self._generate_provider_block(provider, infrastructure_spec.get("provider_config", {}))
        tf_config.append(provider_block)
        
        # Add terraform block
        tf_block = """terraform {
  required_version = ">= 1.0.0"
  required_providers {"""
        
        if provider == "aws":
            tf_block += """
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }"""
        elif provider == "azure":
            tf_block += """
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }"""
        elif provider == "gcp":
            tf_block += """
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }"""
        
        tf_block += """
  }
}"""
        tf_config.append(tf_block)
        
        # Add variable blocks
        if "variables" in infrastructure_spec:
            for var_name, var_spec in infrastructure_spec["variables"].items():
                var_block = self._generate_variable_block(var_name, var_spec)
                tf_config.append(var_block)
        
        # Add resource blocks
        for resource in infrastructure_spec["resources"]:
            if "type" not in resource or "name" not in resource:
                continue
                
            resource_block = self._generate_resource_block(
                provider, 
                resource["type"], 
                resource["name"], 
                resource.get("config", {})
            )
            tf_config.append(resource_block)
        
        # Add output blocks
        if "outputs" in infrastructure_spec:
            for output in infrastructure_spec["outputs"]:
                if "name" not in output or "value" not in output:
                    continue
                    
                output_block = self._generate_output_block(
                    output["name"], 
                    output["value"], 
                    output.get("description", "")
                )
                tf_config.append(output_block)
        
        return "\n\n".join(tf_config)
    
    def deploy_docker_compose_stack(self, compose_config: Dict[str, Any] = Field(..., description="Docker Compose configuration"), 
                                   environment: str = Field("development", description="Deployment environment")) -> Dict[str, Any]:
        """
        Build and deploy Docker Compose stacks.
        
        Args:
            compose_config: Docker Compose configuration
            environment: Deployment environment (development, staging, production)
            
        Returns:
            Dictionary containing deployment status and information
        """
        # Validate compose configuration
        if "version" not in compose_config:
            compose_config["version"] = "3.8"  # Default to version 3.8
        
        if "services" not in compose_config or not compose_config["services"]:
            return {
                "success": False,
                "error": "No services defined in Docker Compose configuration"
            }
        
        # Add environment-specific configurations
        self._add_environment_config(compose_config, environment)
        
        # Generate docker-compose.yml file
        timestamp = int(time.time())
        deployment_id = f"deployment_{timestamp}"
        self.deployment_history[deployment_id] = {
            "timestamp": timestamp,
            "environment": environment,
            "status": "pending",
            "compose_file": f"docker-compose-{deployment_id}.yml"
        }
        
        compose_file = self.deployment_history[deployment_id]["compose_file"]
        
        try:
            # Convert to YAML and write to file
            with open(compose_file, "w") as f:
                yaml.dump(compose_config, f, default_flow_style=False)
            
            # In a real implementation, we would execute docker-compose up here
            # For this implementation, we'll simulate the deployment
            deployment_result = self._simulate_docker_compose_deployment(deployment_id, compose_file)
            
            self.deployment_history[deployment_id]["status"] = "deployed" if deployment_result["success"] else "failed"
            self.deployment_history[deployment_id]["result"] = deployment_result
            
            return {
                "success": deployment_result["success"],
                "deployment_id": deployment_id,
                "environment": environment,
                "details": deployment_result,
                "compose_file": compose_file
            }
            
        except Exception as e:
            self.deployment_history[deployment_id]["status"] = "failed"
            self.deployment_history[deployment_id]["error"] = str(e)
            
            return {
                "success": False,
                "deployment_id": deployment_id,
                "environment": environment,
                "error": str(e)
            }
    
    def validate_infrastructure_deployment(self, deployment_id: str = Field(..., description="ID of the deployment to validate")) -> Dict[str, Any]:
        """
        Verify successful infrastructure deployment.
        
        Args:
            deployment_id: ID of the deployment to validate
            
        Returns:
            Dictionary containing validation results
        """
        if deployment_id not in self.deployment_history:
            return {
                "success": False,
                "error": f"Deployment ID '{deployment_id}' not found"
            }
        
        deployment = self.deployment_history[deployment_id]
        
        # For a real implementation, we would check the actual status of the services
        # For this implementation, we'll simulate the validation
        validation_result = self._simulate_deployment_validation(deployment)
        
        # Update deployment history with validation results
        self.deployment_history[deployment_id]["validation"] = validation_result
        
        return {
            "success": validation_result["success"],
            "deployment_id": deployment_id,
            "environment": deployment.get("environment", "unknown"),
            "status": deployment.get("status", "unknown"),
            "details": validation_result,
            "timestamp": time.time()
        }
    
    def _generate_provider_block(self, provider: str, provider_config: Dict[str, Any]) -> str:
        """Generate provider configuration block"""
        if provider == "aws":
            region = provider_config.get("region", "us-west-2")
            return f"""provider "aws" {{
  region = "{region}"
}}"""
        elif provider == "azure":
            return """provider "azurerm" {
  features {}
}"""
        elif provider == "gcp":
            project = provider_config.get("project", "my-project")
            region = provider_config.get("region", "us-central1")
            return f"""provider "google" {{
  project = "{project}"
  region  = "{region}"
}}"""
        else:
            return f"# Unsupported provider: {provider}"
    
    def _generate_variable_block(self, name: str, spec: Dict[str, Any]) -> str:
        """Generate Terraform variable block"""
        var_block = f'variable "{name}" {{\n'
        
        if "type" in spec:
            var_block += f'  type        = {spec["type"]}\n'
        
        if "description" in spec:
            var_block += f'  description = "{spec["description"]}"\n'
        
        if "default" in spec:
            if isinstance(spec["default"], str):
                var_block += f'  default     = "{spec["default"]}"\n'
            else:
                var_block += f'  default     = {spec["default"]}\n'
        
        var_block += '}'
        return var_block
    
    def _generate_resource_block(self, provider: str, resource_type: str, resource_name: str, config: Dict[str, Any]) -> str:
        """Generate Terraform resource block"""
        # If the provider has templates for this resource type, use them
        if provider in self.terraform_templates and resource_type in self.terraform_templates[provider]:
            template = self.terraform_templates[provider][resource_type]
            
            # Replace variables in template
            for key, value in config.items():
                placeholder = f"{{{{var.{key}}}}}"
                if isinstance(value, str):
                    replacement = f'"{value}"'
                else:
                    replacement = str(value)
                template = template.replace(placeholder, replacement)
            
            return template.replace("{{resource_name}}", resource_name)
        
        # Otherwise, generate a basic resource block
        resource_block = f'resource "{resource_type}" "{resource_name}" {{\n'
        
        for key, value in config.items():
            if isinstance(value, str):
                resource_block += f'  {key} = "{value}"\n'
            elif isinstance(value, dict):
                resource_block += f'  {key} {{\n'
                for k, v in value.items():
                    if isinstance(v, str):
                        resource_block += f'    {k} = "{v}"\n'
                    else:
                        resource_block += f'    {k} = {v}\n'
                resource_block += '  }\n'
            else:
                resource_block += f'  {key} = {value}\n'
        
        resource_block += '}'
        return resource_block
    
    def _generate_output_block(self, name: str, value: str, description: str = "") -> str:
        """Generate Terraform output block"""
        output_block = f'output "{name}" {{\n'
        output_block += f'  value       = {value}\n'
        
        if description:
            output_block += f'  description = "{description}"\n'
        
        output_block += '}'
        return output_block
    
    def _add_environment_config(self, compose_config: Dict[str, Any], environment: str) -> None:
        """Add environment-specific configurations to Docker Compose config"""
        # Set environment variables for all services
        for service_name, service in compose_config.get("services", {}).items():
            if "environment" not in service:
                service["environment"] = {}
            
            if isinstance(service["environment"], list):
                # Convert list to dict for easier manipulation
                env_dict = {}
                for item in service["environment"]:
                    if "=" in item:
                        key, value = item.split("=", 1)
                        env_dict[key] = value
                service["environment"] = env_dict
            
            # Add environment-specific variables
            service["environment"]["DEPLOYMENT_ENV"] = environment
            
            # Environment-specific adjustments
            if environment == "production":
                # Add production-specific configurations
                if "deploy" not in service:
                    service["deploy"] = {}
                
                # Set replicas based on service type
                if service_name.startswith("web") or service_name.startswith("api"):
                    service["deploy"]["replicas"] = 3
                else:
                    service["deploy"]["replicas"] = 1
                
                # Add restart policy
                service["deploy"]["restart_policy"] = {
                    "condition": "any",
                    "delay": "5s",
                    "max_attempts": 3
                }
                
                # Remove development-only volumes
                if "volumes" in service:
                    service["volumes"] = [v for v in service["volumes"] if not v.startswith("./dev")]
            
            elif environment == "staging":
                # Add staging-specific configurations
                if "deploy" not in service:
                    service["deploy"] = {}
                
                service["deploy"]["replicas"] = 1
                service["deploy"]["restart_policy"] = {
                    "condition": "on-failure",
                    "max_attempts": 3
                }
            
            # Development environment (default)
            else:
                # Add development-specific configurations
                service["environment"]["DEBUG"] = "true"
                
                # Add development volumes if not present
                if "volumes" not in service:
                    service["volumes"] = []
                
                # Only add if it's not already in the list
                dev_volume = "./dev:/app/dev"
                if dev_volume not in service["volumes"]:
                    service["volumes"].append(dev_volume)
    
    def _simulate_docker_compose_deployment(self, deployment_id: str, compose_file: str) -> Dict[str, Any]:
        """Simulate Docker Compose deployment (for demonstration purposes)"""
        # In a real implementation, this would execute docker-compose commands
        # For this implementation, we'll simulate the deployment
        
        # Load the compose file to get service information
        try:
            with open(compose_file, "r") as f:
                compose_config = yaml.safe_load(f)
            
            services = compose_config.get("services", {})
            service_count = len(services)
            
            # Simulate deployment result
            return {
                "success": True,
                "message": f"Successfully deployed {service_count} services",
                "services": list(services.keys()),
                "containers": [f"{name}-{deployment_id}" for name in services.keys()],
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _simulate_deployment_validation(self, deployment: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate deployment validation (for demonstration purposes)"""
        # In a real implementation, this would check the actual status of services
        # For this implementation, we'll simulate the validation
        
        if deployment.get("status") != "deployed":
            return {
                "success": False,
                "message": f"Deployment status is '{deployment.get('status')}', not 'deployed'",
                "checks": [
                    {"name": "deployment_status", "success": False, "message": "Deployment not completed"}
                ]
            }
        
        result = deployment.get("result", {})
        services = result.get("services", [])
        
        checks = []
        all_success = True
        
        # Validate each service
        for service in services:
            # Simulate service check (90% success rate)
            service_success = True if time.time() % 10 != 0 else False
            
            checks.append({
                "name": f"service_{service}",
                "success": service_success,
                "message": "Service running correctly" if service_success else "Service has issues"
            })
            
            if not service_success:
                all_success = False
        
        # Add network check
        network_success = True
        checks.append({
            "name": "network",
            "success": network_success,
            "message": "Network configured correctly"
        })
        
        # Add volume check
        volume_success = True
        checks.append({
            "name": "volumes",
            "success": volume_success,
            "message": "Volumes mounted correctly"
        })
        
        return {
            "success": all_success,
            "message": "All checks passed" if all_success else "Some checks failed",
            "checks": checks,
            "timestamp": time.time()
        }
    
    # Template methods
    def _get_aws_vpc_template(self) -> str:
        return """resource "aws_vpc" "{{resource_name}}" {
  cidr_block           = "{{var.cidr_block}}"
  enable_dns_support   = {{var.enable_dns_support}}
  enable_dns_hostnames = {{var.enable_dns_hostnames}}
  
  tags = {
    Name = "{{var.name}}"
    Environment = "{{var.environment}}"
  }
}"""
    
    def _get_aws_ec2_template(self) -> str:
        return """resource "aws_instance" "{{resource_name}}" {
  ami           = "{{var.ami}}"
  instance_type = "{{var.instance_type}}"
  subnet_id     = "{{var.subnet_id}}"
  
  tags = {
    Name = "{{var.name}}"
    Environment = "{{var.environment}}"
  }
}"""
    
    def _get_aws_rds_template(self) -> str:
        return """resource "aws_db_instance" "{{resource_name}}" {
  allocated_storage    = {{var.allocated_storage}}
  storage_type         = "{{var.storage_type}}"
  engine               = "{{var.engine}}"
  engine_version       = "{{var.engine_version}}"
  instance_class       = "{{var.instance_class}}"
  name                 = "{{var.name}}"
  username             = "{{var.username}}"
  password             = "{{var.password}}"
  parameter_group_name = "{{var.parameter_group_name}}"
  
  tags = {
    Environment = "{{var.environment}}"
  }
}"""
    
    def _get_aws_s3_template(self) -> str:
        return """resource "aws_s3_bucket" "{{resource_name}}" {
  bucket = "{{var.bucket}}"
  acl    = "{{var.acl}}"
  
  versioning {
    enabled = {{var.versioning_enabled}}
  }
  
  tags = {
    Name        = "{{var.name}}"
    Environment = "{{var.environment}}"
  }
}"""
    
    def _get_azure_resource_group_template(self) -> str:
        return """resource "azurerm_resource_group" "{{resource_name}}" {
  name     = "{{var.name}}"
  location = "{{var.location}}"
  
  tags = {
    environment = "{{var.environment}}"
  }
}"""
    
    def _get_azure_vnet_template(self) -> str:
        return """resource "azurerm_virtual_network" "{{resource_name}}" {
  name                = "{{var.name}}"
  address_space       = ["{{var.address_space}}"]
  location            = "{{var.location}}"
  resource_group_name = "{{var.resource_group_name}}"
  
  tags = {
    environment = "{{var.environment}}"
  }
}"""
    
    def _get_azure_vm_template(self) -> str:
        return """resource "azurerm_virtual_machine" "{{resource_name}}" {
  name                  = "{{var.name}}"
  location              = "{{var.location}}"
  resource_group_name   = "{{var.resource_group_name}}"
  network_interface_ids = ["{{var.network_interface_id}}"]
  vm_size               = "{{var.vm_size}}"
  
  storage_image_reference {
    publisher = "{{var.publisher}}"
    offer     = "{{var.offer}}"
    sku       = "{{var.sku}}"
    version   = "{{var.version}}"
  }
  
  storage_os_disk {
    name              = "{{var.os_disk_name}}"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "{{var.managed_disk_type}}"
  }
  
  os_profile {
    computer_name  = "{{var.computer_name}}"
    admin_username = "{{var.admin_username}}"
    admin_password = "{{var.admin_password}}"
  }
  
  tags = {
    environment = "{{var.environment}}"
  }
}"""
    
    def _get_azure_storage_template(self) -> str:
        return """resource "azurerm_storage_account" "{{resource_name}}" {
  name                     = "{{var.name}}"
  resource_group_name      = "{{var.resource_group_name}}"
  location                 = "{{var.location}}"
  account_tier             = "{{var.account_tier}}"
  account_replication_type = "{{var.account_replication_type}}"
  
  tags = {
    environment = "{{var.environment}}"
  }
}"""
    
    def _get_gcp_network_template(self) -> str:
        return """resource "google_compute_network" "{{resource_name}}" {
  name                    = "{{var.name}}"
  auto_create_subnetworks = "{{var.auto_create_subnetworks}}"
}"""
    
    def _get_gcp_compute_template(self) -> str:
        return """resource "google_compute_instance" "{{resource_name}}" {
  name         = "{{var.name}}"
  machine_type = "{{var.machine_type}}"
  zone         = "{{var.zone}}"
  
  boot_disk {
    initialize_params {
      image = "{{var.image}}"
    }
  }
  
  network_interface {
    network = "{{var.network}}"
    access_config {
      // Ephemeral IP
    }
  }
  
  metadata = {
    environment = "{{var.environment}}"
  }
}"""
    
    def _get_gcp_storage_template(self) -> str:
        return """resource "google_storage_bucket" "{{resource_name}}" {
  name     = "{{var.name}}"
  location = "{{var.location}}"
  
  versioning {
    enabled = {{var.versioning_enabled}}
  }
  
  labels = {
    environment = "{{var.environment}}"
  }
}"""
    
    def _get_gcp_cloudsql_template(self) -> str:
        return """resource "google_sql_database_instance" "{{resource_name}}" {
  name             = "{{var.name}}"
  database_version = "{{var.database_version}}"
  region           = "{{var.region}}"
  
  settings {
    tier = "{{var.tier}}"
    
    backup_configuration {
      enabled = {{var.backup_enabled}}
      start_time = "{{var.backup_start_time}}"
    }
    
    ip_configuration {
      ipv4_enabled = {{var.ipv4_enabled}}
      authorized_networks {
        name  = "{{var.authorized_network_name}}"
        value = "{{var.authorized_network_value}}"
      }
    }
  }
}"""
    
    def _get_basic_compose_template(self) -> str:
        return """version: '3.8'

services:
  app:
    image: {{var.app_image}}
    ports:
      - "{{var.app_port}}:{{var.app_internal_port}}"
    environment:
      - ENVIRONMENT={{var.environment}}
    restart: always
"""
    
    def _get_web_compose_template(self) -> str:
        return """version: '3.8'

services:
  web:
    image: {{var.web_image}}
    ports:
      - "{{var.web_port}}:{{var.web_internal_port}}"
    environment:
      - ENVIRONMENT={{var.environment}}
    depends_on:
      - api
    restart: always
    
  api:
    image: {{var.api_image}}
    ports:
      - "{{var.api_port}}:{{var.api_internal_port}}"
    environment:
      - ENVIRONMENT={{var.environment}}
      - DB_HOST=db
    depends_on:
      - db
    restart: always
    
  db:
    image: {{var.db_image}}
    volumes:
      - db_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER={{var.db_user}}
      - POSTGRES_PASSWORD={{var.db_password}}
      - POSTGRES_DB={{var.db_name}}
    restart: always

volumes:
  db_data:
"""
    
    def _get_data_compose_template(self) -> str:
        return """version: '3.8'

services:
  postgres:
    image: postgres:{{var.postgres_version}}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER={{var.postgres_user}}
      - POSTGRES_PASSWORD={{var.postgres_password}}
      - POSTGRES_DB={{var.postgres_db}}
    ports:
      - "{{var.postgres_port}}:5432"
    restart: always
    
  redis:
    image: redis:{{var.redis_version}}
    volumes:
      - redis_data:/data
    ports:
      - "{{var.redis_port}}:6379"
    restart: always
    
  elasticsearch:
    image: elasticsearch:{{var.elasticsearch_version}}
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "{{var.elasticsearch_port}}:9200"
    restart: always

volumes:
  postgres_data:
  redis_data:
  elasticsearch_data:
"""
    
    def _get_security_compose_template(self) -> str:
        return """version: '3.8'

services:
  rtpi_proxy:
    image: nginx:{{var.nginx_version}}
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./nginx/ssl:/etc/nginx/ssl
    restart: always
    
  rtpi_healer:
    image: {{var.healer_image}}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - MONITORING_INTERVAL={{var.monitoring_interval}}
    restart: always
    
  burpsuite:
    image: {{var.burpsuite_image}}
    ports:
      - "{{var.burpsuite_port}}:8080"
    volumes:
      - burpsuite_data:/home/burpsuite
    restart: always
    
  kali:
    image: {{var.kali_image}}
    ports:
      - "{{var.kali_port}}:6901"
    volumes:
      - kali_data:/home/kali
    environment:
      - VNC_PASSWORD={{var.vnc_password}}
    restart: always

volumes:
  burpsuite_data:
  kali_data:
"""
