"""
Daedelu5 Agent Router

FastAPI router for Daedelu5 agent tools, including Infrastructure-as-Code management,
compliance auditing, security policy enforcement, and self-healing integration.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Import Daedelu5 tools
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from tools.daedelu5.InfrastructureAsCodeManager import InfrastructureAsCodeManager
from tools.daedelu5.ComplianceAuditor import ComplianceAuditor
from tools.daedelu5.SecurityPolicyEnforcer import SecurityPolicyEnforcer
from tools.daedelu5.SelfHealingIntegrator import SelfHealingIntegrator

logger = logging.getLogger("Daedelu5Router")

# Create router
router = APIRouter()

# Initialize Daedelu5 tool instances
iac_manager = InfrastructureAsCodeManager()
compliance_auditor = ComplianceAuditor()
policy_enforcer = SecurityPolicyEnforcer()
healing_integrator = SelfHealingIntegrator()

# Pydantic models for Daedelu5 specific requests
class IaCRequest(BaseModel):
    """Request model for Infrastructure-as-Code operations"""
    infrastructure_type: str = Field(..., description="Type of infrastructure (terraform, cloudformation, etc.)")
    action: str = Field(..., description="Action to perform (deploy, validate, destroy)")
    configuration: Dict[str, Any] = Field(..., description="Infrastructure configuration")

class ComplianceRequest(BaseModel):
    """Request model for compliance auditing"""
    framework: str = Field(..., description="Compliance framework (nist, iso27001, pci-dss)")
    target_system: str = Field(..., description="Target system to audit")
    audit_scope: List[str] = Field(..., description="Areas to audit")

class PolicyRequest(BaseModel):
    """Request model for security policy enforcement"""
    policy_type: str = Field(..., description="Type of policy to enforce")
    target_resources: List[str] = Field(..., description="Resources to apply policy to")
    policy_config: Dict[str, Any] = Field(..., description="Policy configuration")

class HealingRequest(BaseModel):
    """Request model for self-healing operations"""
    incident_type: str = Field(..., description="Type of incident to heal")
    affected_resources: List[str] = Field(..., description="Affected resources")
    healing_strategy: str = Field(..., description="Healing strategy to apply")

@router.post("/iac/manage")
async def manage_infrastructure_code(request: IaCRequest):
    """Manage Infrastructure-as-Code deployments"""
    try:
        result = iac_manager.manage_terraform_lifecycle(
            action=request.action,
            configuration=request.configuration,
            infrastructure_type=request.infrastructure_type
        )
        
        return {
            "success": result.get("success", False),
            "iac_result": result,
            "infrastructure_type": request.infrastructure_type,
            "action": request.action,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"IaC management failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"IaC management failed: {str(e)}")

@router.post("/compliance/audit")
async def audit_compliance(request: ComplianceRequest):
    """Perform compliance auditing against security frameworks"""
    try:
        result = compliance_auditor.audit_framework_compliance(
            framework=request.framework,
            target_system=request.target_system,
            audit_scope=request.audit_scope
        )
        
        return {
            "success": result.get("success", False),
            "compliance_result": result,
            "framework": request.framework,
            "target_system": request.target_system,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Compliance audit failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Compliance audit failed: {str(e)}")

@router.post("/policy/enforce")
async def enforce_security_policy(request: PolicyRequest):
    """Enforce security policies across infrastructure"""
    try:
        result = policy_enforcer.enforce_security_policies(
            policy_type=request.policy_type,
            target_resources=request.target_resources,
            policy_configuration=request.policy_config
        )
        
        return {
            "success": result.get("success", False),
            "enforcement_result": result,
            "policy_type": request.policy_type,
            "resources_affected": len(request.target_resources),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Policy enforcement failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Policy enforcement failed: {str(e)}")

@router.post("/healing/integrate")
async def integrate_self_healing(request: HealingRequest):
    """Integrate self-healing capabilities for incident response"""
    try:
        result = healing_integrator.integrate_healing_mechanisms(
            incident_type=request.incident_type,
            affected_resources=request.affected_resources,
            healing_strategy=request.healing_strategy
        )
        
        return {
            "success": result.get("success", False),
            "healing_result": result,
            "incident_type": request.incident_type,
            "healing_strategy": request.healing_strategy,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Self-healing integration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Self-healing integration failed: {str(e)}")

@router.get("/status")
async def get_daedelu5_status():
    """Get Daedelu5 agent status and capabilities"""
    return {
        "agent": "Daedelu5",
        "status": "active",
        "capabilities": {
            "infrastructure_as_code": {
                "terraform_management": True,
                "cloudformation_support": True,
                "deployment_validation": True
            },
            "compliance_auditing": {
                "nist_framework": True,
                "iso27001_framework": True,
                "pci_dss_framework": True
            },
            "policy_enforcement": {
                "security_policies": True,
                "access_controls": True,
                "resource_tagging": True
            },
            "self_healing": {
                "incident_response": True,
                "automated_remediation": True,
                "resource_recovery": True
            }
        },
        "tools_loaded": [
            "InfrastructureAsCodeManager",
            "ComplianceAuditor",
            "SecurityPolicyEnforcer",
            "SelfHealingIntegrator"
        ],
        "timestamp": datetime.utcnow()
    }

@router.get("/tools")
async def list_daedelu5_tools():
    """List all available Daedelu5 tools and endpoints"""
    return {
        "agent": "Daedelu5",
        "tools": {
            "infrastructure_as_code": {
                "manage_infrastructure_code": "POST /iac/manage"
            },
            "compliance": {
                "audit_compliance": "POST /compliance/audit"
            },
            "policy_enforcement": {
                "enforce_security_policy": "POST /policy/enforce"
            },
            "self_healing": {
                "integrate_self_healing": "POST /healing/integrate"
            },
            "status": {
                "get_daedelu5_status": "GET /status",
                "list_daedelu5_tools": "GET /tools"
            }
        },
        "total_endpoints": 6,
        "timestamp": datetime.utcnow()
    }
