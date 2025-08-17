"""
BurpSuite Operator Agent Router

FastAPI router for BurpSuite Operator agent tools, including Burp Suite Professional integration,
scan orchestration, result processing, and vulnerability assessment.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Import BurpSuite Operator tools
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from tools.burpsuite_operator.BurpSuiteAPIClient import BurpSuiteAPIClient
from tools.burpsuite_operator.BurpScanOrchestrator import BurpScanOrchestrator
from tools.burpsuite_operator.BurpResultProcessor import BurpResultProcessor
from tools.burpsuite_operator.BurpVulnerabilityAssessor import BurpVulnerabilityAssessor

logger = logging.getLogger("BurpSuiteRouter")

# Create router
router = APIRouter()

# Initialize BurpSuite Operator tool instances
burp_client = BurpSuiteAPIClient()
scan_orchestrator = BurpScanOrchestrator()
result_processor = BurpResultProcessor()
vuln_assessor = BurpVulnerabilityAssessor()

# Pydantic models for BurpSuite Operator specific requests
class BurpScanRequest(BaseModel):
    """Request model for Burp Suite scanning"""
    target_url: str = Field(..., description="Target URL to scan")
    scan_config: Dict[str, Any] = Field(default_factory=dict, description="Scan configuration")

class BurpResultsRequest(BaseModel):
    """Request model for processing Burp results"""
    scan_id: str = Field(..., description="Scan ID to process results for")
    include_false_positives: bool = Field(default=False, description="Whether to include false positives")

class VulnerabilityAssessmentRequest(BaseModel):
    """Request model for vulnerability assessment"""
    scan_results: Dict[str, Any] = Field(..., description="Scan results to assess")
    severity_threshold: str = Field(default="medium", description="Minimum severity to include")

@router.post("/scan/start")
async def start_burp_scan(request: BurpScanRequest):
    """Start a Burp Suite Professional scan"""
    try:
        result = scan_orchestrator.orchestrate_comprehensive_scan(
            target_url=request.target_url,
            scan_configuration=request.scan_config
        )
        
        return {
            "success": result.get("success", False),
            "scan_result": result,
            "target_url": request.target_url,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Burp scan failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Burp scan failed: {str(e)}")

@router.post("/results/process")
async def process_burp_results(request: BurpResultsRequest):
    """Process and analyze Burp Suite scan results"""
    try:
        result = result_processor.process_scan_results(
            scan_id=request.scan_id,
            include_false_positives=request.include_false_positives
        )
        
        return {
            "success": result.get("success", False),
            "processed_results": result,
            "scan_id": request.scan_id,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Burp result processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Burp result processing failed: {str(e)}")

@router.post("/vulnerability/assess")
async def assess_vulnerabilities(request: VulnerabilityAssessmentRequest):
    """Assess and categorize discovered vulnerabilities"""
    try:
        result = vuln_assessor.assess_vulnerability_criticality(
            scan_results=request.scan_results,
            severity_threshold=request.severity_threshold
        )
        
        return {
            "success": result.get("success", False),
            "assessment_result": result,
            "severity_threshold": request.severity_threshold,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Vulnerability assessment failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Vulnerability assessment failed: {str(e)}")

@router.get("/status")
async def get_burpsuite_status():
    """Get BurpSuite Operator agent status and capabilities"""
    return {
        "agent": "BurpSuite Operator",
        "status": "active",
        "capabilities": {
            "scanning": {
                "comprehensive_scans": True,
                "targeted_scans": True,
                "custom_configurations": True
            },
            "result_processing": {
                "automated_processing": True,
                "false_positive_filtering": True,
                "report_generation": True
            },
            "vulnerability_assessment": {
                "criticality_analysis": True,
                "risk_scoring": True,
                "remediation_guidance": True
            }
        },
        "tools_loaded": [
            "BurpSuiteAPIClient",
            "BurpScanOrchestrator",
            "BurpResultProcessor",
            "BurpVulnerabilityAssessor"
        ],
        "timestamp": datetime.utcnow()
    }

@router.get("/tools")
async def list_burpsuite_tools():
    """List all available BurpSuite Operator tools and endpoints"""
    return {
        "agent": "BurpSuite Operator",
        "tools": {
            "scanning": {
                "start_burp_scan": "POST /scan/start"
            },
            "result_processing": {
                "process_burp_results": "POST /results/process"
            },
            "vulnerability_assessment": {
                "assess_vulnerabilities": "POST /vulnerability/assess"
            },
            "status": {
                "get_burpsuite_status": "GET /status",
                "list_burpsuite_tools": "GET /tools"
            }
        },
        "total_endpoints": 5,
        "timestamp": datetime.utcnow()
    }
